"""Independent preliminary writer probes, 2026-10-29, discovery after PR1202.

Inputs: exact current seeder/test/native-writer bytes and synthetic schema-valid
records. Outputs: seeder-preliminary-probes.json beside this retained helper.
Only temporary fixture trees are changed; no real corpus, Git, network, goals,
sessions, or detection providers are used. The seeder source is compiled without
edits, with __file__ pointing to each disposable fixture root; native validators
and writers are imported from the actual repository. This permits exercising the
real CLI report path without needing the pending scientific manifest.
"""

from __future__ import annotations

import contextlib
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile

import yaml


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / "scripts/seed_structural_discovery.py"
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "scripts"))


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def fixture(root: Path) -> tuple[dict, dict, Path, Path]:
    record = {
        "identifier": "proteintraitsmech:TEST_DISCOVERY_ONE",
        "label": "synthetic review fixture",
        "definition": "Synthetic fixture for writer safety; no scientific assertion.",
        "definition_source": "independent synthetic test fixture",
        "trait_axis": "STRUCTURE", "trait_category": "STRUCT_SECONDARY",
        "term_kind": "CLASS", "mapping_status": "PROPOSED", "license": "CC0-1.0",
        "evidence": [{"reference": "synthetic fixture"}],
        "detection_methods": [{"name": "Fixture", "recipe": "fixture {input}"}],
    }
    relative = "data/traits/structure/secondary/test-discovery-one.yaml"
    manifest = root / "data/curation/structural_trait_discovery.yaml"
    manifest.parent.mkdir(parents=True)
    manifest.write_text(yaml.safe_dump({"version": 1, "records": [{"path": relative, "record": record}]}))
    (root / "data/traits").mkdir()
    namespace = {"__name__": "seeder_independent_fixture", "__file__": str(root / "scripts/seed_structural_discovery.py")}
    exec(compile(SOURCE.read_bytes(), str(SOURCE), "exec"), namespace)
    return namespace, record, manifest, root / relative


def escaped_identifier_collision() -> dict:
    with tempfile.TemporaryDirectory(prefix="ptm-independent-id-") as tmp:
        root = Path(tmp)
        ns, record, _, destination = fixture(root)
        other = root / "data/traits/.ignored/existing.yaml"
        other.parent.mkdir()
        (root / ".gitignore").write_text("data/traits/.ignored/\n")
        encoded = record["identifier"].replace("ONE", "\\u004fNE")
        text = yaml.safe_dump(record).replace(
            "identifier: " + record["identifier"], 'identifier: "' + encoded + '"'
        )
        other.write_text(text)
        assert record["identifier"] not in text
        assert yaml.safe_load(text)["identifier"] == record["identifier"]
        validation = ns["validate_one"](other)
        assert validation == [], validation
        report = ns["seed"](apply=True)
        identities = [yaml.safe_load(p.read_text())["identifier"] for p in (root / "data/traits").rglob("*.yaml")]
        return {"existing_record_strict_errors": validation,
                "decoded_id": record["identifier"], "existing_literal_line": text.split("identifier:", 1)[1].splitlines()[0],
                "scan_hit_files": report["preflight"]["identity_hit_files"],
                "created_duplicate": destination.exists() and identities.count(record["identifier"]) == 2,
                "report": report}


def crlf_replay_hash() -> dict:
    with tempfile.TemporaryDirectory(prefix="ptm-independent-crlf-") as tmp:
        root = Path(tmp)
        ns, _, _, destination = fixture(root)
        ns["seed"](apply=True)
        destination.write_bytes(destination.read_bytes().replace(b"\n", b"\r\n"))
        before = destination.read_bytes()
        report = ns["seed"](apply=True)
        return {"action": report["records"][0]["action"],
                "bytes_preserved": destination.read_bytes() == before,
                "actual_sha256": digest(before), "reported_sha256": report["records"][0]["sha256"],
                "hash_matches_actual": report["records"][0]["sha256"] == digest(before)}


def dryrun_report_overwrite() -> dict:
    with tempfile.TemporaryDirectory(prefix="ptm-independent-report-") as tmp:
        root = Path(tmp)
        ns, _, _, destination = fixture(root)
        ns["seed"](apply=True)
        before = destination.read_bytes()
        argv = sys.argv
        try:
            sys.argv = [str(SOURCE), "--report", str(destination)]
            with contextlib.redirect_stdout(io.StringIO()):
                ns["main"]()
        finally:
            sys.argv = argv
        after = destination.read_bytes()
        report = json.loads(after)
        return {"apply_flag": report["apply"], "record_overwritten": before != after,
                "record_was_valid_before": True, "strict_errors_after": ns["validate_one"](destination),
                "reported_action": report["records"][0]["action"],
                "before_sha256": digest(before), "after_sha256": digest(after)}


def main() -> None:
    inputs = [SOURCE, ROOT / "tests/test_seed_structural_discovery.py", ROOT / "scripts/record_io.py"]
    result = {"review_kind": "independent_temporary_fixture_probes",
              "inputs": {str(path.relative_to(ROOT)): digest(path.read_bytes()) for path in inputs},
              "helper_sha256": digest(Path(__file__).read_bytes()),
              "fixture_scope": "Disposable temporary directories; real maintained source compiled unchanged, native validator/writer used.",
              "escaped_identifier_collision": escaped_identifier_collision(),
              "crlf_replay_hash": crlf_replay_hash(),
              "dryrun_report_overwrite": dryrun_report_overwrite()}
    (HERE / "seeder-preliminary-probes.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"escaped_id_duplicate_created": result["escaped_identifier_collision"]["created_duplicate"],
                      "crlf_report_hash_matches": result["crlf_replay_hash"]["hash_matches_actual"],
                      "dryrun_report_overwrites_record": result["dryrun_report_overwrite"]["record_overwritten"]}))


if __name__ == "__main__":
    main()
