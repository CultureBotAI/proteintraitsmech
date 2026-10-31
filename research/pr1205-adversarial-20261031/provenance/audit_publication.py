#!/usr/bin/env python3
"""Read-only PR1205 publication audit, 2026-10-31; explicit adversarial-review task.

Inputs: committed discovery publication manifest, additive checksum list, all
discovery helper files (Path.rglob includes ignored files), native review YAML,
source evidence and historical reconstruction receipts. Outputs: a new JSON
observation under this helper's directory; no network, Git mutations, corpus
writes, historical report rewrites or detector execution. References: PR1205,
issues1200/1201/1204/1206. Source/hash verification is not scientific review.
Requires only Python >=3.10; source-input extraction deliberately handles the
native saver format, records parsed counts, and does not replace its validator.
"""
import argparse
import gzip
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
TASK = ROOT / "research/structural-discovery-20261028"


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1048576), b""):
            h.update(chunk)
    return h.hexdigest()


def row_check(row):
    p = ROOT / row["path"]
    actual = sha(p) if p.is_file() else None
    return {**row, "exists": p.is_file(), "actual_sha256": actual,
            "actual_bytes": p.stat().st_size if p.is_file() else None,
            "matches": actual == row["sha256"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--head", required=True, help="Exact head confirmed by parent/read-only Git")
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()
    out = args.output.resolve()
    if out.parent != HERE:
        raise SystemExit("Output must be directly inside this scoped evidence directory")
    manifest_path = TASK / "publication-manifest.json"
    manifest = json.loads(manifest_path.read_text())
    checks = [row_check(r) for r in manifest["files"]]
    additive_path = TASK / "ci-followup/artifact-sha256.txt"
    additive = [row_check({"path": line.split(None, 1)[1], "sha256": line.split(None, 1)[0]})
                for line in additive_path.read_text().splitlines() if line.strip()]
    declared = {r["path"] for r in checks}
    additive_names = {r["path"] for r in additive}
    actual_files = [str(p.relative_to(ROOT)) for p in TASK.rglob("*") if p.is_file()]
    sources = set(p for p in actual_files if p.endswith(".py"))
    sources.update(str(p.relative_to(ROOT)) for p in (ROOT / "scripts/adhoc/structural_discovery_20261028").rglob("*.py"))
    sources.update(["scripts/seed_structural_discovery.py", "tests/test_seed_structural_discovery.py"])
    readmes = "\n".join(p.read_text() for p in TASK.rglob("README.md"))
    helper_rows = [{"path": p, "sha256": sha(ROOT / p), "manifested": p in declared,
                    "additive_sealed": p in additive_names,
                    "basename_mentioned_in_readmes": Path(p).name in readmes}
                   for p in sorted(sources)]
    original = next(r for r in checks if r["path"].endswith("/open-work-prewrite.json"))
    decompressed = gzip.decompress((TASK / "open-work-prewrite.json.gz").read_bytes())
    gzip_check = {"bytes": len(decompressed), "sha256": hashlib.sha256(decompressed).hexdigest(),
                  "matches_historical_manifest": hashlib.sha256(decompressed).hexdigest() == original["sha256"]}
    native = []
    for slug in ["20261029T070848Z-independent-structural-discovery-writer",
                 "20261029T071028Z-independent-tunnel-bottleneck-canary",
                 "20261029T071846Z-independent-beta-arch",
                 "20261029T072012Z-independent-membrane-fenestration"]:
        p = ROOT / "reviews/structured" / slug / "review.yaml"
        raw = p.read_text()
        block = raw.split("\nsource:\n", 1)[1].split("\nscope:\n", 1)[0]
        inputs = [{"path": m[0], "sha256": m[1], "role": m[2]}
                  for m in re.findall(r"  - path: ([^\n]+)\n    sha256: ([0-9a-f]{64})\n    role: ([^\n]+)", block)]
        native.append({"review": str(p.relative_to(ROOT)), "review_sha256": sha(p),
                       "state": re.search(r"  state: ([^\n]+)", block).group(1),
                       "git_revision": re.search(r"  git_revision: ([^\n]+)", block).group(1),
                       "parsed_inputs": len(inputs), "inputs": [row_check(r) for r in inputs],
                       "note": "Working-tree attestations need not equal the current tree; changed/missing context requires interpretation, not automatic invalidation."})
    result = {"timestamp_utc": datetime.now(timezone.utc).isoformat(), "reference": "PR1205 explicit adversarial provenance/publication audit",
              "head": args.head, "root": str(ROOT), "helper_sha256": sha(Path(__file__)),
              "manifest_sha256": sha(manifest_path), "additive_list_sha256": sha(additive_path),
              "manifest_checks": checks, "additive_checks": additive, "helper_count": len(helper_rows),
              "helpers": helper_rows, "gzip_check": gzip_check,
              "task_files_outside_initial_and_additive_inventory": sorted(set(actual_files) - declared - additive_names),
              "native_review_input_checks": native,
              "limits": ["No historical results overwritten; no native saver or validator invoked by this helper.",
                         "Ignored local-only inputs are expected absent from a clean clone; full historical execution is not claimed.",
                         "Helper count covers published source files, not unretained transient editing states."]}
    with out.open("x") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"output": str(out), "helpers": len(helper_rows),
                      "manifest_commit_failures": [r["path"] for r in checks if r["retention"] == "commit" and not r["matches"]],
                      "additive_failures": [r["path"] for r in additive if not r["matches"]],
                      "gzip_match": gzip_check["matches_historical_manifest"]}, indent=2))


if __name__ == "__main__":
    main()
