"""Tests for the read-only Rhea provider-acquisition receipt verifier."""

from __future__ import annotations

import importlib
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any, Callable

import pytest


REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
receipt = importlib.import_module("validate_rhea_acquisition_receipt")
stage = importlib.import_module("stage_rhea_uniprot_grounding")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _case(tmp_path: Path) -> dict[str, Any]:
    repo = tmp_path / "repo"
    raw = repo / "data" / "raw" / "rhea"
    source_paths = {
        "mapping": raw / "rhea2uniprot_sprot.tsv",
        "release_properties": raw / "rhea-release.properties",
        "tsv_readme": raw / "rhea-tsv-README.txt",
        "license": raw / "LICENSE.txt",
        "directions": raw / "rhea-directions.tsv",
        "reactions": raw / "rhea-reactions.tsv",
    }
    _write(
        source_paths["mapping"],
        stage.MAPPING_HEADER
        + "\n10000\tUN\t10000\tP12345\n"
        + "10001\tLR\t10000\tP12345\n"
        + "20002\tRL\t20000\tQ9Y261\n",
    )
    _write(
        source_paths["release_properties"],
        "rhea.release.number=141\nrhea.release.date=2026-06-10\n",
    )
    _write(
        source_paths["tsv_readme"],
        "Files named rhea2<db>.tsv contain cross-references to other databases\n"
        "RHEA_ID: reaction\nDIRECTION: direction\nMASTER_ID: master\nID: record\n",
    )
    _write(
        source_paths["license"],
        "Creative Commons Attribution 4.0 International\n"
        "All files in the Rhea FTP directory may be copied and redistributed freely\n",
    )
    _write(
        source_paths["directions"],
        stage.DIRECTIONS_HEADER + "\n10000\t10001\t10002\t10003\n" + "20000\t20001\t20002\t20003\n",
    )
    _write(
        source_paths["reactions"],
        stage.REACTIONS_HEADER
        + "\nRHEA:10000\tA + B = C\tCHEBI:1;CHEBI:2\tEC:1.1.1.1\n"
        + "RHEA:20000\tD = E\tCHEBI:3;CHEBI:4\t\n",
    )
    receipt_path = raw / "rhea-provider-acquisition-receipt.json"
    paths = receipt.ReceiptPaths(
        repo_root=repo,
        receipt=receipt_path,
        **source_paths,
    )
    return {
        "repo": repo,
        "raw": raw,
        "source_paths": source_paths,
        "receipt": receipt_path,
        "paths": paths,
    }


def _attestations(case: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, role in enumerate(receipt.SOURCE_ROLES, 1):
        rows.append(
            {
                "role": role,
                "response_url": receipt.PLAN_ARTIFACTS[role]["url"],
                "response_status": 200,
                "response_received_at_utc": f"2026-08-26T12:00:{index:02d}Z",
                "response_header_projection": {
                    "content-length": str(case["source_paths"][role].stat().st_size),
                    "content-type": "text/plain",
                    "date": "Wed, 26 Aug 2026 12:00:00 GMT",
                    "last-modified": "Wed, 26 Aug 2026 11:00:00 GMT",
                },
            }
        )
    return rows


def _producer() -> dict[str, str]:
    return {
        "implementation": "synthetic-test-producer-not-an-authenticated-fetch",
        "implementation_sha256": "1" * 64,
    }


def _install_receipt(
    case: dict[str, Any], *, enforce_release_contract: bool = False
) -> dict[str, Any]:
    value = receipt.build_receipt_value(
        paths=case["paths"],
        acquisition_started_at_utc="2026-08-26T12:00:00Z",
        acquisition_completed_at_utc="2026-08-26T12:01:00Z",
        response_attestations=_attestations(case),
        producer=_producer(),
        enforce_release_contract=enforce_release_contract,
    )
    _write(case["receipt"], receipt.canonical_json(value) + "\n")
    return value


def _rewrite_receipt(
    case: dict[str, Any], mutate: Callable[[dict[str, Any]], None], *, readdress: bool = True
) -> None:
    value = json.loads(case["receipt"].read_text(encoding="ascii"))
    mutate(value)
    if readdress:
        value.pop("receipt_id", None)
        value["receipt_id"] = receipt.RECEIPT_ID_PREFIX + receipt.value_sha256(value)
    _write(case["receipt"], receipt.canonical_json(value) + "\n")


def test_valid_synthetic_receipt_is_content_bound_but_never_grounding_eligible(
    tmp_path: Path,
) -> None:
    case = _case(tmp_path)
    supplied = _install_receipt(case)
    before = sorted(str(path.relative_to(case["repo"])) for path in case["repo"].rglob("*"))

    result = receipt.verify_receipt(paths=case["paths"], enforce_release_contract=False)

    after = sorted(str(path.relative_to(case["repo"])) for path in case["repo"].rglob("*"))
    assert before == after
    assert result["status"] == "PASS_RECEIPT_CONTENT_AND_SEMANTIC_BINDINGS_ONLY"
    assert result["receipt_id"] == supplied["receipt_id"]
    assert result["artifact_and_semantic_bindings_verified"] is True
    assert result["network_action_performed_by_verifier"] is False
    assert result["producer_authenticated"] is False
    assert result["central_grounding_eligible"] is False
    assert result["central_receipt_binding_status"] == receipt.CENTRAL_BINDING_STATUS
    assert result["writes_performed"] is False
    assert result["source_mapping_physical_row_count"] == 3
    assert result["source_reaction_master_count"] == 2


def test_receipt_build_is_deterministic_and_exactly_content_addressed(tmp_path: Path) -> None:
    case = _case(tmp_path)
    first = _install_receipt(case)
    second = receipt.build_receipt_value(
        paths=case["paths"],
        acquisition_started_at_utc="2026-08-26T12:00:00Z",
        acquisition_completed_at_utc="2026-08-26T12:01:00Z",
        response_attestations=_attestations(case),
        producer=_producer(),
        enforce_release_contract=False,
    )
    assert first == second
    without_id = dict(first)
    observed = without_id.pop("receipt_id")
    assert observed == receipt.RECEIPT_ID_PREFIX + receipt.value_sha256(without_id)
    assert first["response_count"] == 6
    assert first["response_rows_sha256"] == receipt.value_sha256(first["response_rows"])
    assert first["source_semantics_sha256"] == receipt.value_sha256(first["source_semantics"])
    assert first["grounding_boundary"] == {
        "central_receipt_binding_status": receipt.CENTRAL_BINDING_STATUS,
        "grounding_eligible": False,
        "promotion_authorized": False,
        "provider_authenticity_proven": False,
    }


@pytest.mark.parametrize("role", receipt.SOURCE_ROLES)
def test_every_response_body_mutation_is_rejected(tmp_path: Path, role: str) -> None:
    case = _case(tmp_path)
    _install_receipt(case)
    path = case["source_paths"][role]
    path.write_bytes(path.read_bytes() + b"# drift\n")

    with pytest.raises(
        (receipt.RheaAcquisitionReceiptError, stage.RheaStageError),
        match=(
            "Content-Length|mismatch|invalid|disagree|reproduce|contract|row|properties|declaration"
        ),
    ):
        receipt.verify_receipt(paths=case["paths"], enforce_release_contract=False)


@pytest.mark.parametrize(
    "mutate",
    [
        lambda value: value.__setitem__("acquisition_plan_id", "wrong"),
        lambda value: value.__setitem__("network_action_performed", False),
        lambda value: value["grounding_boundary"].__setitem__("grounding_eligible", True),
        lambda value: value.__setitem__("provenance_limit", "too-strong"),
        lambda value: value["response_rows"][0].__setitem__("response_body_sha256", "0" * 64),
        lambda value: value["source_semantics"].__setitem__("mapping_physical_row_count", 999),
        lambda value: value.__setitem__("response_count", 5),
    ],
)
def test_readdressed_derived_or_policy_claim_mutation_is_rejected(
    tmp_path: Path, mutate: Callable[[dict[str, Any]], None]
) -> None:
    case = _case(tmp_path)
    _install_receipt(case)
    _rewrite_receipt(case, mutate)

    with pytest.raises(receipt.RheaAcquisitionReceiptError, match="reproduce"):
        receipt.verify_receipt(paths=case["paths"], enforce_release_contract=False)


def test_wrong_unreaddressed_receipt_id_is_rejected(tmp_path: Path) -> None:
    case = _case(tmp_path)
    _install_receipt(case)
    _rewrite_receipt(case, lambda value: value.__setitem__("receipt_id", "wrong"), readdress=False)

    with pytest.raises(receipt.RheaAcquisitionReceiptError, match="reproduce"):
        receipt.verify_receipt(paths=case["paths"], enforce_release_contract=False)


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (
            lambda value: value["response_rows"][0].__setitem__(
                "response_url", "https://example.org/not-rhea"
            ),
            "URL is not canonical",
        ),
        (
            lambda value: value["response_rows"][0].__setitem__("response_status", 404),
            "status is not integer 200",
        ),
        (
            lambda value: value["response_rows"][0].__setitem__(
                "response_received_at_utc", "2026-08-26T12:02:00Z"
            ),
            "outside ordered acquisition interval",
        ),
        (
            lambda value: value["response_rows"][0]["response_header_projection"].pop("date"),
            "lack HTTP Date",
        ),
        (
            lambda value: value["response_rows"][0]["response_header_projection"].__setitem__(
                "content-length", "1"
            ),
            "Content-Length",
        ),
        (
            lambda value: value["response_rows"][0]["response_header_projection"].__setitem__(
                "X-Test", "invalid uppercase key"
            ),
            "header projection is invalid",
        ),
    ],
)
def test_response_attestation_contract_is_closed(
    tmp_path: Path, mutate: Callable[[dict[str, Any]], None], message: str
) -> None:
    case = _case(tmp_path)
    _install_receipt(case)
    _rewrite_receipt(case, mutate)

    with pytest.raises(receipt.RheaAcquisitionReceiptError, match=message):
        receipt.verify_receipt(paths=case["paths"], enforce_release_contract=False)


def test_invalid_producer_binding_is_rejected_but_authentication_is_not_claimed(
    tmp_path: Path,
) -> None:
    case = _case(tmp_path)
    _install_receipt(case)
    _rewrite_receipt(
        case,
        lambda value: value["producer"].__setitem__("implementation_sha256", "not-a-digest"),
    )
    with pytest.raises(receipt.RheaAcquisitionReceiptError, match="producer.*invalid"):
        receipt.verify_receipt(paths=case["paths"], enforce_release_contract=False)

    case = _case(tmp_path / "opaque")
    supplied = _install_receipt(case)
    result = receipt.verify_receipt(paths=case["paths"], enforce_release_contract=False)
    assert supplied["producer"] == _producer()
    assert result["producer_authenticated"] is False
    assert "NOT_REEXECUTED_OR_AUTHENTICATED" in result["provenance_limit"]


def test_noncanonical_duplicate_and_crlf_receipts_are_rejected(tmp_path: Path) -> None:
    pretty = _case(tmp_path / "pretty")
    value = _install_receipt(pretty)
    pretty["receipt"].write_text(json.dumps(value, indent=2) + "\n", encoding="ascii")
    with pytest.raises(receipt.RheaAcquisitionReceiptError, match="one canonical"):
        receipt.verify_receipt(paths=pretty["paths"], enforce_release_contract=False)

    duplicate = _case(tmp_path / "duplicate")
    _install_receipt(duplicate)
    text = duplicate["receipt"].read_text(encoding="ascii")
    duplicate["receipt"].write_text('{"schema_version":1,' + text[1:], encoding="ascii")
    with pytest.raises(receipt.RheaAcquisitionReceiptError, match="duplicate JSON key"):
        receipt.verify_receipt(paths=duplicate["paths"], enforce_release_contract=False)

    crlf = _case(tmp_path / "crlf")
    _install_receipt(crlf)
    crlf["receipt"].write_bytes(crlf["receipt"].read_bytes().replace(b"\n", b"\r\n"))
    with pytest.raises(receipt.RheaAcquisitionReceiptError, match="canonical LF"):
        receipt.verify_receipt(paths=crlf["paths"], enforce_release_contract=False)


def test_symlink_hardlink_and_wrong_target_paths_are_rejected(tmp_path: Path) -> None:
    symlink = _case(tmp_path / "symlink")
    _install_receipt(symlink)
    mapping = symlink["source_paths"]["mapping"]
    original = mapping.with_suffix(".original")
    mapping.rename(original)
    mapping.symlink_to(original)
    with pytest.raises(receipt.RheaAcquisitionReceiptError, match="cannot safely open"):
        receipt.verify_receipt(paths=symlink["paths"], enforce_release_contract=False)

    hardlink = _case(tmp_path / "hardlink")
    _install_receipt(hardlink)
    os.link(hardlink["source_paths"]["mapping"], hardlink["raw"] / "mapping-alias.tsv")
    with pytest.raises(receipt.RheaAcquisitionReceiptError, match="exactly one hard link"):
        receipt.verify_receipt(paths=hardlink["paths"], enforce_release_contract=False)

    wrong = _case(tmp_path / "wrong")
    _install_receipt(wrong)
    wrong_path = wrong["raw"] / "wrong-mapping.tsv"
    wrong_path.write_bytes(wrong["source_paths"]["mapping"].read_bytes())
    wrong_paths = receipt.ReceiptPaths(
        repo_root=wrong["paths"].repo_root,
        receipt=wrong["paths"].receipt,
        mapping=wrong_path,
        release_properties=wrong["paths"].release_properties,
        tsv_readme=wrong["paths"].tsv_readme,
        license=wrong["paths"].license,
        directions=wrong["paths"].directions,
        reactions=wrong["paths"].reactions,
    )
    with pytest.raises(receipt.RheaAcquisitionReceiptError, match="path mismatch"):
        receipt.verify_receipt(paths=wrong_paths, enforce_release_contract=False)


def test_receipt_hardlink_and_source_receipt_alias_are_rejected(tmp_path: Path) -> None:
    linked = _case(tmp_path / "linked")
    _install_receipt(linked)
    os.link(linked["receipt"], linked["raw"] / "receipt-alias.json")
    with pytest.raises(receipt.RheaAcquisitionReceiptError, match="exactly one hard link"):
        receipt.verify_receipt(paths=linked["paths"], enforce_release_contract=False)

    aliased = _case(tmp_path / "aliased")
    aliased["receipt"].unlink(missing_ok=True)
    os.link(aliased["source_paths"]["mapping"], aliased["receipt"])
    with pytest.raises(receipt.RheaAcquisitionReceiptError, match="exactly one hard link"):
        receipt.verify_receipt(paths=aliased["paths"], enforce_release_contract=False)


def test_source_mutation_during_final_recheck_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    case = _case(tmp_path)
    _install_receipt(case)
    real_recheck = receipt._recheck_capture
    mutated = False

    def mutate_then_recheck(
        capture: receipt.ArtifactCapture, *, label: str, max_bytes: int
    ) -> None:
        nonlocal mutated
        if not mutated and label == "Rhea mapping final recheck":
            mutated = True
            capture.path.write_bytes(capture.raw + b"# concurrent drift\n")
        real_recheck(capture, label=label, max_bytes=max_bytes)

    monkeypatch.setattr(receipt, "_recheck_capture", mutate_then_recheck)
    with pytest.raises(receipt.RheaAcquisitionReceiptError, match="changed during verification"):
        receipt.verify_receipt(paths=case["paths"], enforce_release_contract=False)


def test_synthetic_catalogue_receipt_cannot_pass_release_141_enforcement(tmp_path: Path) -> None:
    case = _case(tmp_path)
    _install_receipt(case)

    with pytest.raises(receipt.RheaAcquisitionReceiptError, match="master count|digest"):
        receipt.verify_receipt(paths=case["paths"], enforce_release_contract=True)


def test_real_release_141_catalogues_replay_with_one_synthetic_mapping(tmp_path: Path) -> None:
    required = (stage.DEFAULT_DIRECTIONS, stage.DEFAULT_REACTIONS)
    if not all(path.exists() for path in required):
        pytest.skip("ignored release-141 Rhea catalogues are not installed")
    case = _case(tmp_path)
    shutil.copyfile(stage.DEFAULT_DIRECTIONS, case["source_paths"]["directions"])
    shutil.copyfile(stage.DEFAULT_REACTIONS, case["source_paths"]["reactions"])
    _write(case["source_paths"]["mapping"], stage.MAPPING_HEADER + "\n10000\tUN\t10000\tP12345\n")
    supplied = _install_receipt(case, enforce_release_contract=True)

    result = receipt.verify_receipt(paths=case["paths"], enforce_release_contract=True)

    assert supplied["source_semantics"]["direction_master_count"] == 18_558
    assert supplied["source_semantics"]["reaction_master_count"] == 18_558
    assert supplied["source_semantics"]["mapping_physical_row_count"] == 1
    assert result["source_reaction_master_count"] == 18_558
    assert result["source_mapping_physical_row_count"] == 1
    assert result["central_grounding_eligible"] is False


def test_cli_has_no_apply_output_or_network_mode_and_default_fails_closed(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit):
        receipt._parser().parse_args(["--apply"])
    with pytest.raises(SystemExit):
        receipt._parser().parse_args(["--out", "verification.json"])
    if receipt.DEFAULT_RECEIPT.exists():
        pytest.skip("a production Rhea acquisition receipt is installed")
    assert receipt.main([]) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "ERROR:" in captured.err


def test_acquisition_plan_binding_is_exact_and_stable() -> None:
    assert receipt.ACQUISITION_PLAN_ID == (
        "rhea-uniprot-source-acquisition-plan:"
        "f1c4ab1847503d811f13d466f6dc1ac47c59edb25b8902da832ee89a5f29cb4f"
    )
    assert receipt.ACQUISITION_PLAN_ROW_SHA256 == (
        "019b9ed111c7bb8706fbd5dfb3db11737ee2884393ab5805486355be27484cad"
    )
    assert tuple(receipt.PLAN_ARTIFACTS) == receipt.SOURCE_ROLES
    assert receipt.DEFAULT_RECEIPT_RELATIVE == (
        "data/raw/rhea/rhea-provider-acquisition-receipt.json"
    )
