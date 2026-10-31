"""Independent package/provenance review, 2026-10-29; PTM #1200/#1201/#1204.

Inputs: current publication manifest, task helpers/README files, frozen GitHub
snapshot/archive and exact historical writer copies. Outputs: a new timestamped
JSON assessment and, if absent, a hash-verified initial packaging-source copy.
Only these new preflight evidence files and temporary synthetic fixtures may be
written. No packaging main, source/archive edit, Git, network, scientific method,
corpus mutation or session/goal action is executed. This is provisional inventory
evidence, not a frozen commit inventory or merge authority.
"""

from __future__ import annotations

import datetime as dt
import gzip
import hashlib
import json
from pathlib import Path
import tempfile
import types


HERE = Path(__file__).resolve().parent
REPORTS = HERE.parent
ROOT = HERE.parents[2]
PACKAGER = ROOT / "scripts/adhoc/structural_discovery_20261028/package_evidence.py"
EXPECTED_OPEN_WORK = "2e7a953c2cc0c7203592b8d4590759d8187e3f0fc387a40e3acbd3667e820ca7"
INITIAL_PACKAGE_HASH = "153b996e0f580686c26d33a3e2837e43f3a6f698bd6eab8f4c1c99ed8cb7f1d1"
EXPECTED_SOURCES = {
    "scripts/seed_structural_discovery.py": "7143fb829f46ea77a48a9976d27d3e31f78ac1c5e3e845968fa52ef84b75dbd3",
    "tests/test_seed_structural_discovery.py": "863f49dbf21ecba26e1059289b19d7631ba13a23cf433db4797a892f62e0fec8",
    "research/structural-discovery-20261028/preflight/historical/seed_structural_discovery.initial.py": "96cc0749a8791d599bafeefe3eea9bf2258f900e25d078416fe8553edf9c6e4a",
    "research/structural-discovery-20261028/preflight/historical/test_seed_structural_discovery.initial.py": "b516c6afbc86b5c704a3b311d257bc0c1e8636f4740f10237de9f8952e8b33eb",
}


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def row(path: Path) -> dict:
    return {"path": str(path.relative_to(ROOT)), "sha256": digest(path),
            "bytes": path.stat().st_size}


def package_namespace(source: bytes, path: Path) -> dict:
    namespace = {"__name__": "independent_package_probe", "__file__": str(path)}
    exec(compile(source, str(path), "exec"), namespace)
    return namespace


def retain_initial_packager(fixed_source: bytes) -> Path:
    fixed = b'''def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
'''
    initial = b'''def sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()
'''
    assert fixed_source.count(fixed) == 1, "Reviewed fixed sha implementation changed"
    raw = fixed_source.replace(fixed, initial)
    assert hashlib.sha256(raw).hexdigest() == INITIAL_PACKAGE_HASH
    destination = HERE / "historical/package_evidence.initial.py"
    if destination.exists():
        assert destination.read_bytes() == raw
    else:
        with destination.open("xb") as stream:
            stream.write(raw)
    return destination


def package_probes(fixed: bytes, initial: Path) -> dict:
    namespace = package_namespace(fixed, PACKAGER)
    old = package_namespace(initial.read_bytes(), initial)
    with tempfile.TemporaryDirectory(prefix="ptm-package-review-") as tmp:
        directory = Path(tmp)
        source = directory / "open-work-prewrite.json"
        payload = b'{"independent_synthetic_fixture":true}\r\n'
        source.write_bytes(payload)
        expected = hashlib.sha256(payload).hexdigest()
        # Simulate hashlib's Python 3.10 API surface without altering the module.
        compatible_hashlib = types.SimpleNamespace(sha256=hashlib.sha256)
        old["hashlib"] = compatible_hashlib
        namespace["hashlib"] = compatible_hashlib
        try:
            old["sha"](source)
        except AttributeError as error:
            old_error = str(error)
            assert "file_digest" in old_error
        else:
            raise AssertionError("Initial Python 3.10 API defect did not reproduce")
        assert namespace["sha"](source) == expected
        namespace["REPORTS"] = directory
        namespace["OPEN_WORK_SHA256"] = expected
        namespace["archive_open_work"](False)
        archive = source.with_suffix(".json.gz")
        assert gzip.decompress(archive.read_bytes()) == payload
        assert archive.read_bytes()[4:8] == b"\x00\x00\x00\x00"
        source.unlink()
        namespace["archive_open_work"](True)
        assert source.read_bytes() == payload
        source.write_bytes(b"different-existing-fixture")
        before = source.read_bytes()
        try:
            namespace["archive_open_work"](True)
        except ValueError as error:
            refused = str(error)
            assert "refusing replacement" in refused
        else:
            raise AssertionError("Differing restoration destination was accepted")
        assert source.read_bytes() == before
        blocked = ["alpha-collision-hits.txt.gz", "so-20260807.obo",
                   "hbplus-official-docs.tar.gz", "hbplus-official-doc-text.json"]
        for name in blocked:
            path = directory / name
            path.write_bytes(b"synthetic")
            assert namespace["disposition"](path)[0] == "local_only"
        oversized = directory / "unadjudicated.bin"
        with oversized.open("wb") as stream:
            stream.truncate(10 * 1024 * 1024 + 1)
        try:
            namespace["disposition"](oversized)
        except ValueError as error:
            assert "exceeds 10 MiB" in str(error)
        else:
            raise AssertionError("Unadjudicated oversized artifact accepted")
    return {"initial_python310_api_failure": old_error,
            "fixed_without_file_digest": "pass", "gzip_and_restore_bytes": "pass",
            "differing_restore_target_preserved": refused,
            "restricted_and_raw_inputs_excluded": "pass", "oversize_refusal": "pass",
            "scope": "Synthetic temporary fixture only; actual archive and manifest were not mutated."}


def main() -> None:
    fixed = PACKAGER.read_bytes()
    initial = retain_initial_packager(fixed)
    checks = package_probes(fixed, initial)
    manifest = REPORTS / "publication-manifest.json"
    manifest_bytes = manifest.read_bytes()
    inventory = json.loads(manifest_bytes)
    indexed = {entry["path"]: entry for entry in inventory["files"]}
    assert len(indexed) == len(inventory["files"])
    stale = []
    for name, entry in indexed.items():
        path = ROOT / name
        if not path.is_file():
            stale.append({"path": name, "state": "missing"})
        elif digest(path) != entry["sha256"] or path.stat().st_size != entry["bytes"]:
            stale.append({"path": name, "state": "changed_since_provisional_manifest",
                          "current": row(path), "manifest_sha256": entry["sha256"]})
    current = set(REPORTS.rglob("*.py"))
    current.update((ROOT / "scripts/adhoc/structural_discovery_20261028").glob("*.py"))
    current.update(ROOT / name for name in list(EXPECTED_SOURCES)[:2])
    helpers = []
    for path in sorted(current):
        compile(path.read_bytes(), str(path), "exec")  # No execution or bytecode.
        entry = row(path)
        entry["manifest_retention"] = indexed.get(entry["path"], {}).get("retention", "awaiting_refresh")
        assert entry["manifest_retention"] in {"commit", "awaiting_refresh"}
        helpers.append(entry)
    pins = []
    for name, expected in EXPECTED_SOURCES.items():
        observed = row(ROOT / name)
        assert observed["sha256"] == expected, name
        pins.append({**observed, "expected_sha256": expected, "matches": True})
    original = REPORTS / "open-work-prewrite.json"
    compressed = REPORTS / "open-work-prewrite.json.gz"
    assert digest(original) == EXPECTED_OPEN_WORK
    expanded_hash = hashlib.sha256()
    expanded_bytes = 0
    with gzip.open(compressed, "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            expanded_hash.update(chunk)
            expanded_bytes += len(chunk)
    assert expanded_hash.hexdigest() == EXPECTED_OPEN_WORK
    assert expanded_bytes == original.stat().st_size
    selected = [entry for entry in inventory["files"] if entry["retention"] == "commit"]
    forbidden = [entry["path"] for entry in selected
                 if "-collision-hits" in Path(entry["path"]).name
                 or Path(entry["path"]).name in {"so-20260807.obo", "open-work-prewrite.json",
                                                  "hbplus-official-docs.tar.gz", "hbplus-official-doc-text.json"}
                 or entry["bytes"] > 10 * 1024 * 1024]
    assert not forbidden
    motif_provenance = REPORTS / "motifs/helper-provenance-20261029.json"
    motif_inventory = json.loads(motif_provenance.read_bytes())
    assert digest(REPORTS / "motifs/README.md") == motif_inventory["readme_sha256"]
    for entry in motif_inventory["helpers"]:
        assert digest(REPORTS / "motifs" / entry["path"]) == entry["sha256"]
    contexts = [PACKAGER, ROOT / "scripts/adhoc/structural_discovery_20261028/observe_open_work.py",
                ROOT / "scripts/source_helpers.yaml", ROOT / "pyproject.toml", REPORTS / "README.md",
                REPORTS / "motifs/README.md", REPORTS / "cavities/README.md", HERE / "README.md",
                motif_provenance, REPORTS / "sources-check-final.log", Path(__file__)]
    report = {
        "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "reviewer": "Codex agent /root/preflight_boundary_review",
        "reference": "Standalone structural discovery; PTM #1200/#1201/#1204",
        "verdict": "pass_with_limitations", "scientific_acceptance": False,
        "scope": "Final helper/provenance deltas and current provisional publication inventory; no commit/merge/cycle authority.",
        "inputs": [row(path) for path in contexts],
        "manifest": {"path": str(manifest.relative_to(ROOT)),
                     "sha256": hashlib.sha256(manifest_bytes).hexdigest(),
                     "created_utc": inventory["created_utc"], "provisional": True,
                     "selected_count": len(selected), "local_only_count": len(indexed) - len(selected),
                     "stale_entries_requiring_parent_refresh": stale},
        "resolved_packager_finding": {"issue": "Python 3.10 declared floor versus hashlib.file_digest added in 3.11",
                                       "initial_source": row(initial),
                                       "reconstruction": "Reverse the one inspected sha() change from current source; require exact initial manifest hash before retaining copy.",
                                       "fixed_source": row(PACKAGER), "checks": checks},
        "source_helper_registry_delta": {"script": "seed_structural_discovery.py", "role": "local_generator",
                                          "assessment": "Matches the bounded project-authored manifest route and existing secondary/foundational taxonomy entries; no upstream bulk-ingestion claim.",
                                          "receipt": "sources-check-final.log reports 27 reviewed notices, 0 warnings; parent reported exit 0."},
        "writer_and_historical_exact_pins": pins,
        "open_work_lossless": {"original": row(original), "archive": row(compressed),
                               "expanded_sha256": expanded_hash.hexdigest(), "expanded_bytes": expanded_bytes,
                               "expected_sha256": EXPECTED_OPEN_WORK, "matches": True},
        "helper_inventory": helpers, "ignored_files_included": True,
        "retention_checks": {"forbidden_selected_paths": forbidden,
                             "all_current_python_helpers_compile": True,
                             "all_manifested_python_helpers_selected": True,
                             "motif_helper_provenance_and_readme_hashes_match": True},
        "reviewed_limits": [
            "Current inventory is not frozen: new evidence and final logs require the parent's manifest refresh; no staging or commit was inspected.",
            "All retained helper files are inventoried; the preliminary scanner draft was edited in place before its published report and lacks a contemporaneous separate source/hash.",
            "Historical raw-log gzip integrity is attested by its retained compression manifest, not independently decompressed in this check; those large files are local-only.",
            "Scientific rights/reproduction limits are source-specific. Full SO release and unresolved HBPLUS archive/extracted manual remain local; metadata alone is selected.",
            "Motif/cavity READMEs explicitly preserve temporary, local, historical and mutable-URL limitations; no scientific detector or scientific source retrieval was rerun.",
            "The GitHub observer is read-only but non-atomic and remote-state-dependent; the frozen archive preserves the observation, not current global coordination.",
            "The parent owns remaining checks/publication. This assessment is not goal/cycle completion, native merge readiness or authority to merge.",
        ],
    }
    assert PACKAGER.read_bytes() == fixed
    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    output = HERE / ("package-provenance-assessment-" + timestamp + ".json")
    with output.open("x") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"output": str(output.relative_to(ROOT)), "sha256": digest(output),
                      "helper_count": len(helpers), "provisional_manifest_stale": len(stale),
                      "verdict": report["verdict"]}))


if __name__ == "__main__":
    main()
