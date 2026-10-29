"""Independent #1204 regression re-review, 2026-10-29.

Inputs: fixed maintained seeder/tests and retained preliminary fixture helper.
Output: seeder-fixed-probes.json, preserving all preliminary negative evidence.
All apply calls use disposable synthetic fixture trees. The real scientific
manifest is hashed only; no real corpus creation, detector, Git/network/session
or goal action occurs. This is a writer review, not scientific acceptance.
"""

from __future__ import annotations

import contextlib
import copy
import io
import json
from pathlib import Path
import sys
import tempfile

import yaml

sys.dont_write_bytecode = True
import probe_discovery_seeder as prior  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = prior.ROOT


def refusal(function, fragment: str) -> str:
    try:
        function()
    except ValueError as error:
        assert fragment in str(error), str(error)
        return str(error)
    raise AssertionError("Expected refusal: " + fragment)


def cli(ns: dict, args: list[str]) -> str:
    original = sys.argv
    try:
        sys.argv = [str(prior.SOURCE), *args]
        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            ns["main"]()
        return stdout.getvalue()
    finally:
        sys.argv = original


def escaped_collision(field: str) -> dict:
    with tempfile.TemporaryDirectory(prefix="ptm-fixed-id-") as tmp:
        root = Path(tmp)
        ns, candidate, _, destination = prior.fixture(root)
        existing = copy.deepcopy(candidate)
        identity = candidate["identifier"]
        encoded = identity.replace("ONE", "\\u004fNE")
        if field == "xrefs":
            existing["identifier"] = "proteintraitsmech:OTHER"
            existing["xrefs"] = [identity]
        text = yaml.safe_dump(existing)
        text = text.replace("identifier: " + identity, 'identifier: "' + encoded + '"') if field == "identifier" else text.replace("- " + identity, '- "' + encoded + '"')
        other = root / "data/traits/.ignored/existing.yml"
        other.parent.mkdir()
        (root / ".gitignore").write_text("data/traits/.ignored/\n")
        other.write_text(text)
        assert identity not in text
        assert ns["validate_one"](other) == []
        message = refusal(lambda: ns["seed"](apply=True), "already present in another record")
        assert not destination.exists()
        assert other.read_text() == text
        return {"field": field, "escaped_existing_record_strict_valid": True,
                "refused": True, "no_new_record": True, "existing_preserved": True,
                "message": message}


def crlf_refused() -> dict:
    with tempfile.TemporaryDirectory(prefix="ptm-fixed-crlf-") as tmp:
        ns, _, _, destination = prior.fixture(Path(tmp))
        ns["seed"](apply=True)
        crlf = destination.read_bytes().replace(b"\n", b"\r\n")
        destination.write_bytes(crlf)
        refusal(lambda: ns["seed"](apply=True), "refusing replacement")
        assert destination.read_bytes() == crlf
        return {"refused": True, "exact_modified_bytes_preserved": True}


def report_guards() -> dict:
    results = {}
    with tempfile.TemporaryDirectory(prefix="ptm-fixed-report-") as tmp:
        root = Path(tmp)
        ns, _, manifest, destination = prior.fixture(root)
        refusal(lambda: cli(ns, ["--apply", "--report", str(destination)]), "Report must be a new")
        assert not destination.exists()
        results["invalid_report_refused_before_apply"] = True
        before_manifest = manifest.read_bytes()
        refusal(lambda: cli(ns, ["--report", str(manifest)]), "Report must be a new")
        assert manifest.read_bytes() == before_manifest
        results["manifest_preserved"] = True
        ns["seed"](apply=True)
        before = destination.read_bytes()
        refusal(lambda: cli(ns, ["--report", str(destination)]), "Report must be a new")
        assert destination.read_bytes() == before
        results["dryrun_trait_report_refused_and_preserved"] = True
        allowed = root / "research/structural-discovery-20261028"
        allowed.mkdir(parents=True)
        existing = allowed / "old.json"
        existing.write_text('{"historical":true}\n')
        refusal(lambda: cli(ns, ["--report", str(existing)]), "Report must be a new")
        assert existing.read_text() == '{"historical":true}\n'
        results["historical_report_preserved"] = True
        (allowed / "escape").symlink_to(root / "data/traits", target_is_directory=True)
        refusal(lambda: cli(ns, ["--report", str(allowed / "escape/new.json")]), "Report must be a new")
        results["symlink_parent_escape_refused"] = True
        new_report = allowed / "fresh.json"
        cli(ns, ["--report", str(new_report)])
        saved = json.loads(new_report.read_text())
        assert saved["apply"] is False
        assert saved["records"][0]["action"] == "unchanged"
        assert saved["records"][0]["sha256"] == prior.digest(destination.read_bytes())
        results["allowed_new_json_report_succeeds_with_actual_hash"] = True
    return results


def captured_manifest_binding() -> dict:
    with tempfile.TemporaryDirectory(prefix="ptm-fixed-manifest-") as tmp:
        root = Path(tmp)
        ns, _, manifest, destination = prior.fixture(root)
        captured = manifest.read_bytes()
        original_preflight = ns["preflight"]

        def edit_after_read(prepared, root):
            result = original_preflight(prepared, root)
            manifest.write_bytes(captured + b"\n# deliberately injected later edit\n")
            return result

        ns["preflight"] = edit_after_read
        report = ns["seed"]()
        assert report["manifest_sha256"] == prior.digest(captured)
        assert report["manifest_sha256"] != prior.digest(manifest.read_bytes())
        assert not destination.exists()
        return {"hash_binds_original_consumed_bytes": True,
                "later_fixture_edit_not_falsely_reported_as_input": True,
                "dryrun_no_corpus_output": True,
                "scope": "Injected fixture edit tests provenance binding only, not a parallel-writer guarantee."}


def dryrun_apply_replay() -> dict:
    with tempfile.TemporaryDirectory(prefix="ptm-fixed-positive-") as tmp:
        ns, _, _, destination = prior.fixture(Path(tmp))
        preview = ns["seed"]()
        assert not destination.exists()
        assert preview["records"][0]["action"] == "would_create"
        created = ns["seed"](apply=True)
        before = destination.read_bytes()
        replay = ns["seed"](apply=True)
        assert created["records"][0]["action"] == "created"
        assert replay["records"][0]["action"] == "unchanged"
        assert destination.read_bytes() == before
        assert replay["records"][0]["sha256"] == prior.digest(before)
        return {"preview_nonmutating": True, "apply_validated": True,
                "replay_no_change": True, "reported_hash_matches_exact_bytes": True}


def main() -> None:
    inputs = [prior.SOURCE, ROOT / "tests/test_seed_structural_discovery.py",
              ROOT / "data/curation/structural_trait_discovery.yaml", ROOT / "scripts/record_io.py"]
    hashes = {str(path.relative_to(ROOT)): prior.digest(path.read_bytes()) for path in inputs}
    report = {"review_kind": "independent_fixed_writer_regressions", "issue": 1204,
              "inputs": hashes, "helper_sha256": prior.digest(Path(__file__).read_bytes()),
              "prior_fixture_helper_sha256": prior.digest(Path(prior.__file__).read_bytes()),
              "escaped_identifier": escaped_collision("identifier"),
              "escaped_xref": escaped_collision("xrefs"),
              "crlf": crlf_refused(), "report_paths": report_guards(),
              "manifest_binding": captured_manifest_binding(), "positive_control": dryrun_apply_replay()}
    assert hashes == {str(path.relative_to(ROOT)): prior.digest(path.read_bytes()) for path in inputs}, "Review inputs changed during probes"
    report["result"] = "PASS"
    (HERE / "seeder-fixed-probes.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"result": "PASS", "prior_findings_reproduced_as_refusals": ["SDW-001", "SDW-002", "SDW-003"], "manifest_hash_binding": "PASS"}))


if __name__ == "__main__":
    main()
