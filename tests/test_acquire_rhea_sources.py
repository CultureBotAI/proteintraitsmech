"""Tests for the saved-plan-gated controlled Rhea acquisition runner."""

from __future__ import annotations

import importlib
import io
import json
import os
import sys
from pathlib import Path
from typing import Any, Callable

import pytest


REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
runner = importlib.import_module("acquire_rhea_sources")
receipt = importlib.import_module("validate_rhea_acquisition_receipt")
stage = importlib.import_module("stage_rhea_uniprot_grounding")


def _write(path: Path, raw: bytes | str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(raw, str):
        path.write_text(raw, encoding="utf-8")
    else:
        path.write_bytes(raw)


def _bodies() -> dict[str, bytes]:
    return {
        "mapping": (
            stage.MAPPING_HEADER
            + "\n10000\tUN\t10000\tP12345\n"
            + "10001\tLR\t10000\tP12345\n"
            + "20002\tRL\t20000\tQ9Y261\n"
        ).encode(),
        "release_properties": ("rhea.release.number=141\nrhea.release.date=2026-06-10\n").encode(),
        "tsv_readme": (
            "Files named rhea2<db>.tsv contain cross-references to other databases\n"
            "RHEA_ID: reaction\nDIRECTION: direction\nMASTER_ID: master\nID: record\n"
        ).encode(),
        "license": (
            "Creative Commons Attribution 4.0 International\n"
            "All files in the Rhea FTP directory may be copied and redistributed freely\n"
        ).encode(),
        "directions": (
            stage.DIRECTIONS_HEADER
            + "\n10000\t10001\t10002\t10003\n"
            + "20000\t20001\t20002\t20003\n"
        ).encode(),
        "reactions": (
            stage.REACTIONS_HEADER
            + "\nRHEA:10000\tA + B = C\tCHEBI:1;CHEBI:2\tEC:1.1.1.1\n"
            + "RHEA:20000\tD = E\tCHEBI:3;CHEBI:4\t\n"
        ).encode(),
    }


def _case(tmp_path: Path, *, existing: tuple[str, ...] = ()) -> dict[str, Any]:
    repo = tmp_path / "repo"
    raw = repo / "data" / "raw" / "rhea"
    raw.mkdir(parents=True)
    bodies = _bodies()
    paths = runner._target_paths(repo)
    for role in existing:
        _write(paths.source_paths()[role], bodies[role])
    return {"repo": repo, "raw": raw, "paths": paths, "bodies": bodies}


def _save_plan(
    case: dict[str, Any], *, enforce_release_contract: bool = False
) -> tuple[dict[str, Any], Path]:
    plan = runner.derive_execution_plan(
        repo_root=case["repo"],
        timeout_seconds=17,
        enforce_release_contract=enforce_release_contract,
    )
    path = case["repo"] / "saved-rhea-acquisition-plan.json"
    _write(path, runner.render_execution_plan(plan))
    return plan, path


class FakeResponse:
    def __init__(
        self,
        *,
        body: bytes,
        url: str,
        status: int = 200,
        headers: dict[str, str] | None = None,
    ) -> None:
        self._stream = io.BytesIO(body)
        self._url = url
        self.status = status
        self.headers = headers or {
            "Content-Length": str(len(body)),
            "Content-Type": "text/plain",
            "Date": "Wed, 26 Aug 2026 12:00:00 GMT",
        }

    def __enter__(self) -> FakeResponse:
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def geturl(self) -> str:
        return self._url

    def read(self, size: int = -1) -> bytes:
        return self._stream.read(size)


class FakeOpener:
    def __init__(
        self,
        bodies: dict[str, bytes],
        *,
        mutate: Callable[[str, bytes, str], FakeResponse] | None = None,
    ) -> None:
        self.bodies = bodies
        self.mutate = mutate
        self.calls: list[tuple[str, int, str | None]] = []

    def __call__(self, request: Any, *, timeout: int) -> FakeResponse:
        url = request.full_url
        role = next(
            role for role in receipt.SOURCE_ROLES if receipt.PLAN_ARTIFACTS[role]["url"] == url
        )
        self.calls.append((role, timeout, request.get_header("Accept-encoding")))
        body = self.bodies[role]
        if self.mutate is not None:
            return self.mutate(role, body, url)
        return FakeResponse(body=body, url=url)


class FixedClock:
    def __init__(self) -> None:
        self.values = [
            "2026-08-26T12:00:00Z",
            *[f"2026-08-26T12:00:{second:02d}Z" for second in range(1, 7)],
            "2026-08-26T12:00:07Z",
        ]

    def __call__(self) -> str:
        if not self.values:
            raise AssertionError("clock called too many times")
        return self.values.pop(0)


def _execute(
    case: dict[str, Any],
    plan_path: Path,
    opener: FakeOpener,
    *,
    hook: Callable[[str], None] | None = None,
    enforce_release_contract: bool = False,
) -> dict[str, Any]:
    return runner.execute_saved_plan(
        execution_plan_path=plan_path,
        repo_root=case["repo"],
        timeout_seconds=17,
        enforce_release_contract=enforce_release_contract,
        opener=opener,
        clock=FixedClock(),
        test_hook=hook,
    )


def test_default_plan_is_deterministic_no_network_and_no_write(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    case = _case(tmp_path)

    def unexpected_network(*_args: object, **_kwargs: object) -> Any:
        raise AssertionError("dry plan attempted network")

    monkeypatch.setattr(runner.urllib.request, "urlopen", unexpected_network)
    before = sorted(path.relative_to(case["repo"]) for path in case["repo"].rglob("*"))
    first = runner.render_execution_plan(
        runner.derive_execution_plan(
            repo_root=case["repo"], timeout_seconds=17, enforce_release_contract=False
        )
    )
    second = runner.render_execution_plan(
        runner.derive_execution_plan(
            repo_root=case["repo"], timeout_seconds=17, enforce_release_contract=False
        )
    )
    after = sorted(path.relative_to(case["repo"]) for path in case["repo"].rglob("*"))

    assert first == second
    assert before == after
    plan = json.loads(first)
    assert plan["safety_boundary"]["network_action_performed"] is False
    assert plan["safety_boundary"]["write_action_performed"] is False
    assert plan["output_binding"]["receipt"]["state"] == "ABSENT_REQUIRED"
    assert plan["plan_id"].startswith(runner.PLAN_ID_PREFIX)


def test_synthetic_saved_plan_executes_all_responses_before_receipt_last(tmp_path: Path) -> None:
    case = _case(tmp_path)
    plan, plan_path = _save_plan(case)
    opener = FakeOpener(case["bodies"])
    events: list[str] = []

    def hook(event: str) -> None:
        if event.startswith("SOURCE_INSTALLED:"):
            assert len(opener.calls) == 6
        events.append(event)

    result = _execute(case, plan_path, opener, hook=hook)

    assert [role for role, _timeout, _encoding in opener.calls] == list(receipt.SOURCE_ROLES)
    assert all(timeout == 17 and encoding == "identity" for _, timeout, encoding in opener.calls)
    assert events[:6] == [f"RESPONSE_CAPTURED:{role}" for role in receipt.SOURCE_ROLES]
    assert events[6] == "TEMPORARY_RECEIPT_VERIFIED"
    assert events[-1] == "RECEIPT_INSTALLED_LAST"
    assert all(
        events.index(f"SOURCE_INSTALLED:{role}") < events.index("RECEIPT_INSTALLED_LAST")
        for role in receipt.SOURCE_ROLES
    )
    for role, path in case["paths"].source_paths().items():
        assert path.read_bytes() == case["bodies"][role]
    supplied = json.loads(case["paths"].receipt.read_text(encoding="ascii"))
    assert supplied["producer"]["implementation_sha256"] == plan["runner_artifact"]["sha256"]
    assert supplied["network_action_performed"] is True
    assert supplied["grounding_boundary"]["grounding_eligible"] is False
    assert result["status"] == ("COMPLETE_PRODUCER_ATTESTATION_INSTALLED_NOT_GROUNDING_ELIGIBLE")
    assert result["central_grounding_eligible"] is False
    assert result["producer_authenticated"] is False


def test_matching_preexisting_sources_are_not_replaced(tmp_path: Path) -> None:
    case = _case(tmp_path, existing=("directions", "reactions"))
    identities = {
        role: (path.stat().st_dev, path.stat().st_ino)
        for role, path in case["paths"].source_paths().items()
        if path.exists()
    }
    _plan, plan_path = _save_plan(case)

    _execute(case, plan_path, FakeOpener(case["bodies"]))

    for role, identity in identities.items():
        path = case["paths"].source_paths()[role]
        assert (path.stat().st_dev, path.stat().st_ino) == identity
    assert case["paths"].receipt.exists()


def test_mismatching_preexisting_late_role_is_rejected_before_first_write(
    tmp_path: Path,
) -> None:
    case = _case(tmp_path, existing=("directions",))
    _plan, plan_path = _save_plan(case)
    response_bodies = dict(case["bodies"])
    response_bodies["directions"] = (
        stage.DIRECTIONS_HEADER + "\n20000\t20001\t20002\t20003\n" + "10000\t10001\t10002\t10003\n"
    ).encode()

    with pytest.raises(runner.RheaAcquisitionRunError, match="differ from HTTPS response"):
        _execute(case, plan_path, FakeOpener(response_bodies))

    assert case["paths"].directions.read_bytes() == case["bodies"]["directions"]
    assert not any(
        path.exists() for role, path in case["paths"].source_paths().items() if role != "directions"
    )
    assert not case["paths"].receipt.exists()


def test_network_failure_and_invalid_downloads_write_nothing(
    tmp_path: Path,
) -> None:
    case = _case(tmp_path)
    _plan, plan_path = _save_plan(case)

    class FailureOpener(FakeOpener):
        def __call__(self, request: Any, *, timeout: int) -> FakeResponse:
            if len(self.calls) == 2:
                raise OSError("synthetic network failure")
            return super().__call__(request, timeout=timeout)

    with pytest.raises(runner.RheaAcquisitionRunError, match="HTTPS request failed"):
        _execute(case, plan_path, FailureOpener(case["bodies"]))
    assert not any(path.exists() for path in case["paths"].source_paths().values())
    assert not case["paths"].receipt.exists()

    invalid = _case(tmp_path / "invalid")
    _plan, invalid_plan = _save_plan(invalid)
    invalid_bodies = dict(invalid["bodies"])
    invalid_bodies["mapping"] = b"not a Rhea mapping\n"
    with pytest.raises(runner.RheaAcquisitionRunError, match="downloaded Rhea bundle"):
        _execute(invalid, invalid_plan, FakeOpener(invalid_bodies))
    assert not any(path.exists() for path in invalid["paths"].source_paths().values())
    assert not invalid["paths"].receipt.exists()


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (
            lambda role, body, url: FakeResponse(
                body=body, url=url, status=False if role == "mapping" else 200
            ),
            "status is not integer 200",
        ),
        (
            lambda role, body, url: FakeResponse(
                body=body,
                url="https://example.org/redirected" if role == "mapping" else url,
            ),
            "final response URL is not canonical",
        ),
        (
            lambda role, body, url: FakeResponse(
                body=body,
                url=url,
                headers=({"Content-Length": str(len(body))} if role == "mapping" else None),
            ),
            "lacks required HTTP Date",
        ),
        (
            lambda role, body, url: FakeResponse(
                body=body,
                url=url,
                headers=(
                    {
                        "Content-Length": "1",
                        "Date": "Wed, 26 Aug 2026 12:00:00 GMT",
                    }
                    if role == "mapping"
                    else None
                ),
            ),
            "Content-Length",
        ),
        (
            lambda role, body, url: FakeResponse(
                body=body,
                url=url,
                headers=(
                    {
                        "Content-Length": str(len(body)),
                        "Date": "Wed, 26 Aug 2020 12:00:00 GMT",
                    }
                    if role == "mapping"
                    else None
                ),
            ),
            "outside the acquisition interval",
        ),
    ],
)
def test_response_contract_failures_precede_all_writes(
    tmp_path: Path,
    mutate: Callable[[str, bytes, str], FakeResponse],
    message: str,
) -> None:
    case = _case(tmp_path)
    _plan, plan_path = _save_plan(case)
    with pytest.raises(runner.RheaAcquisitionRunError, match=message):
        _execute(case, plan_path, FakeOpener(case["bodies"], mutate=mutate))
    assert not any(path.exists() for path in case["paths"].source_paths().values())
    assert not case["paths"].receipt.exists()


def test_bounded_reader_rejects_oversized_and_nonbyte_streams() -> None:
    response = FakeResponse(body=b"ab", url="https://example.org")
    with pytest.raises(runner.RheaAcquisitionRunError, match="exceeds 1 bytes"):
        runner._read_bounded_response(response, role="mapping", limit=1)

    class TextResponse(FakeResponse):
        def read(self, size: int = -1) -> Any:
            return "not bytes"

    with pytest.raises(runner.RheaAcquisitionRunError, match="returned non-bytes"):
        runner._read_bounded_response(
            TextResponse(body=b"x", url="https://example.org"),
            role="mapping",
            limit=10,
        )


def test_saved_plan_mutation_noncanonical_duplicate_and_crlf_are_rejected(
    tmp_path: Path,
) -> None:
    case = _case(tmp_path / "readdressed")
    plan, plan_path = _save_plan(case)
    plan["safety_boundary"]["trait_writes_authorized"] = True
    plan.pop("plan_id")
    plan["plan_id"] = runner.PLAN_ID_PREFIX + receipt.value_sha256(plan)
    _write(plan_path, runner.render_execution_plan(plan))
    with pytest.raises(runner.RheaAcquisitionRunError, match="does not match current"):
        _execute(case, plan_path, FakeOpener(case["bodies"]))

    pretty = _case(tmp_path / "pretty")
    value, pretty_plan = _save_plan(pretty)
    _write(pretty_plan, json.dumps(value, indent=2) + "\n")
    with pytest.raises(runner.RheaAcquisitionRunError, match="one canonical"):
        _execute(pretty, pretty_plan, FakeOpener(pretty["bodies"]))

    duplicate = _case(tmp_path / "duplicate")
    _value, duplicate_plan = _save_plan(duplicate)
    text = duplicate_plan.read_text(encoding="ascii")
    _write(duplicate_plan, '{"schema_version":1,' + text[1:])
    with pytest.raises(runner.RheaAcquisitionRunError, match="duplicate JSON key"):
        _execute(duplicate, duplicate_plan, FakeOpener(duplicate["bodies"]))

    crlf = _case(tmp_path / "crlf")
    _value, crlf_plan = _save_plan(crlf)
    crlf_plan.write_bytes(crlf_plan.read_bytes().replace(b"\n", b"\r\n"))
    with pytest.raises(runner.RheaAcquisitionRunError, match="canonical LF"):
        _execute(crlf, crlf_plan, FakeOpener(crlf["bodies"]))


def test_parent_source_and_saved_plan_drift_fail_closed(tmp_path: Path) -> None:
    source = _case(tmp_path / "source", existing=("directions",))
    _plan, source_plan = _save_plan(source)
    source["paths"].directions.write_bytes(source["bodies"]["directions"] + b"# drift\n")
    opener = FakeOpener(source["bodies"])
    with pytest.raises(runner.RheaAcquisitionRunError, match="does not match current"):
        _execute(source, source_plan, opener)
    assert opener.calls == []

    plan_case = _case(tmp_path / "plan")
    _plan, plan_path = _save_plan(plan_case)
    opener = FakeOpener(plan_case["bodies"])

    def mutate_plan(event: str) -> None:
        if event == "RESPONSE_CAPTURED:reactions":
            plan_path.write_bytes(plan_path.read_bytes() + b" ")

    with pytest.raises(runner.RheaAcquisitionRunError, match="execution plan.*changed"):
        _execute(plan_case, plan_path, opener, hook=mutate_plan)
    assert not plan_case["paths"].receipt.exists()
    assert not any(path.exists() for path in plan_case["paths"].source_paths().values())

    parent = _case(tmp_path / "parent")
    _plan, parent_plan = _save_plan(parent)
    original = parent["raw"].with_name("rhea-original")
    parent["raw"].rename(original)
    parent["raw"].mkdir()
    with pytest.raises(runner.RheaAcquisitionRunError, match="does not match current|parent"):
        _execute(parent, parent_plan, FakeOpener(parent["bodies"]))


def test_post_download_source_drift_is_rejected_before_any_new_write(tmp_path: Path) -> None:
    case = _case(tmp_path, existing=("directions",))
    _plan, plan_path = _save_plan(case)

    def drift(event: str) -> None:
        if event == "TEMPORARY_RECEIPT_VERIFIED":
            case["paths"].directions.write_bytes(case["bodies"]["directions"] + b"# drift\n")

    with pytest.raises(runner.RheaAcquisitionRunError, match="changed after network capture"):
        _execute(case, plan_path, FakeOpener(case["bodies"]), hook=drift)
    assert not case["paths"].receipt.exists()
    assert not any(
        path.exists() for role, path in case["paths"].source_paths().items() if role != "directions"
    )


def test_race_during_source_install_leaves_receipt_absent(tmp_path: Path) -> None:
    case = _case(tmp_path)
    _plan, plan_path = _save_plan(case)

    def collide(event: str) -> None:
        if event == "SOURCE_INSTALLED:mapping":
            _write(case["paths"].release_properties, b"racing bytes\n")

    with pytest.raises(
        runner.RheaAcquisitionRunError,
        match="cannot create Rhea release_properties without replacement",
    ):
        _execute(case, plan_path, FakeOpener(case["bodies"]), hook=collide)
    assert case["paths"].mapping.exists()
    assert not case["paths"].receipt.exists()


def test_symlink_hardlink_and_existing_receipt_are_rejected(tmp_path: Path) -> None:
    symlink = _case(tmp_path / "symlink")
    symlink["raw"].rmdir()
    real = symlink["repo"] / "real-rhea"
    real.mkdir()
    symlink["raw"].symlink_to(real, target_is_directory=True)
    with pytest.raises(runner.RheaAcquisitionRunError, match="cannot safely bind"):
        runner.derive_execution_plan(repo_root=symlink["repo"])

    hardlink = _case(tmp_path / "hardlink", existing=("directions",))
    os.link(hardlink["paths"].directions, hardlink["raw"] / "directions-alias.tsv")
    with pytest.raises(runner.RheaAcquisitionRunError, match="exactly one hard link"):
        runner.derive_execution_plan(repo_root=hardlink["repo"])

    completed = _case(tmp_path / "completed")
    _write(completed["paths"].receipt, b"not replaceable\n")
    with pytest.raises(runner.RheaAcquisitionRunError, match="refuses replacement"):
        runner.derive_execution_plan(repo_root=completed["repo"])


def test_apply_cli_contract_and_second_generation_are_fail_closed(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    case = _case(tmp_path)
    with pytest.raises(SystemExit):
        runner._parser().parse_args(["--repo-root", str(case["repo"])])
    assert runner.main(["--apply"]) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "requires an exact saved" in captured.err

    _plan, plan_path = _save_plan(case)
    _execute(case, plan_path, FakeOpener(case["bodies"]))
    with pytest.raises(runner.RheaAcquisitionRunError, match="refuses replacement"):
        _execute(case, plan_path, FakeOpener(case["bodies"]))


def test_real_release_141_catalogues_can_build_runner_receipt(tmp_path: Path) -> None:
    if not stage.DEFAULT_DIRECTIONS.exists() or not stage.DEFAULT_REACTIONS.exists():
        pytest.skip("ignored release-141 Rhea catalogues are not installed")
    case = _case(tmp_path)
    bodies = dict(case["bodies"])
    bodies["mapping"] = (stage.MAPPING_HEADER + "\n10000\tUN\t10000\tP12345\n").encode()
    bodies["directions"] = stage.DEFAULT_DIRECTIONS.read_bytes()
    bodies["reactions"] = stage.DEFAULT_REACTIONS.read_bytes()
    case["bodies"] = bodies
    _plan, plan_path = _save_plan(case, enforce_release_contract=True)

    result = _execute(
        case,
        plan_path,
        FakeOpener(bodies),
        enforce_release_contract=True,
    )

    assert result["verification_status"] == ("PASS_RECEIPT_CONTENT_AND_SEMANTIC_BINDINGS_ONLY")
    assert result["central_grounding_eligible"] is False


def test_provider_plan_binding_and_production_absence_are_unchanged() -> None:
    assert runner.PLAN_KIND == "RHEA_PROVIDER_ACQUISITION_EXECUTION_PLAN"
    assert runner.derive_execution_plan()["provider_acquisition_plan_id"] == (
        "rhea-uniprot-source-acquisition-plan:"
        "f1c4ab1847503d811f13d466f6dc1ac47c59edb25b8902da832ee89a5f29cb4f"
    )
    assert runner.derive_execution_plan()["provider_acquisition_plan_row_sha256"] == (
        "019b9ed111c7bb8706fbd5dfb3db11737ee2884393ab5805486355be27484cad"
    )
    assert not receipt.DEFAULT_RECEIPT.exists()
