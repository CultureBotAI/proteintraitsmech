#!/usr/bin/env python3
"""Inventory retained discovery results and package the bulky public PR snapshot.

Date/reference: 2026-10-29, structural discovery goal, PTM #1200/#1201/#1204.
Inputs: this task's research directory and immutable prewrite GitHub snapshot.
Outputs: lossless open-work-prewrite.json.gz plus publication-manifest.json.
All helpers are publication inputs; bulky raw searches, fetched ontology release,
restricted HBPLUS documentation and private readiness text remain local. Nothing
is removed. --restore-open-work recreates only the missing original JSON from
its retained compressed bytes and validates the original SHA-256.
"""

from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[3]
REPORTS = ROOT / "research/structural-discovery-20261028"
OPEN_WORK_SHA256 = "2e7a953c2cc0c7203592b8d4590759d8187e3f0fc387a40e3acbd3667e820ca7"
MANIFEST = REPORTS / "publication-manifest.json"


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def disposition(path: Path) -> tuple[str, str]:
    if "__pycache__" in path.parts or path.suffix == ".pyc":
        return "local_only", "Regenerable Python bytecode, not an executable source helper"
    if "-collision-hits" in path.name:
        return "local_only", "Historical broad raw-search output; compact refined evidence and reproducer are published"
    if path.name == "open-work-prewrite.json":
        return "local_only", "Identical full bytes retained in published open-work-prewrite.json.gz"
    if path.name == "so-20260807.obo":
        return "local_only", "Fetched full ontology release; URL/version/hash and relevant candidate decisions are published"
    if path.name in {"hbplus-official-docs.tar.gz", "hbplus-official-doc-text.json"}:
        return "local_only", "Upstream documentation with unresolved redistribution terms; retained locally, metadata and deferral published"
    if path.name.startswith(("pr-body", "final-remote", "final-head")):
        return "local_only", "Private mutable PR/readiness metadata, outside the evidence commit"
    if path.stat().st_size > 10 * 1024 * 1024:
        raise ValueError(f"Unadjudicated artifact exceeds 10 MiB: {path}")
    return "commit", "Owned result, source evidence with retained terms, or retained task helper"


def archive_open_work(restore: bool) -> None:
    source = REPORTS / "open-work-prewrite.json"
    archive = source.with_suffix(".json.gz")
    if restore:
        raw = gzip.decompress(archive.read_bytes())
        if hashlib.sha256(raw).hexdigest() != OPEN_WORK_SHA256:
            raise ValueError("Archived open-work bytes do not match the frozen observation")
        if source.exists():
            if sha(source) != OPEN_WORK_SHA256:
                raise ValueError("Existing open-work source differs; refusing replacement")
        else:
            with source.open("xb") as stream:
                stream.write(raw)
        return
    if sha(source) != OPEN_WORK_SHA256:
        raise ValueError("Prewrite open-work snapshot changed")
    if not archive.exists():
        with source.open("rb") as source_stream, archive.open("xb") as output:
            with gzip.GzipFile(filename="", mode="wb", fileobj=output, mtime=0) as compressed:
                shutil.copyfileobj(source_stream, compressed)
    if hashlib.sha256(gzip.decompress(archive.read_bytes())).hexdigest() != OPEN_WORK_SHA256:
        raise ValueError("Compressed snapshot failed byte verification")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--restore-open-work", action="store_true")
    args = parser.parse_args()
    archive_open_work(args.restore_open_work)
    if args.restore_open_work:
        print("Frozen open-work snapshot restored/verified; no existing differing file replaced")
        return
    paths = set(REPORTS.rglob("*"))
    paths.update((ROOT / "scripts/adhoc/structural_discovery_20261028").glob("*.py"))
    paths.update([ROOT / "scripts/seed_structural_discovery.py", ROOT / "tests/test_seed_structural_discovery.py"])
    files = []
    for path in sorted(paths):
        if not path.is_file() or path == MANIFEST:
            continue
        retention, reason = disposition(path)
        if path.suffix == ".py" and retention != "commit":
            raise ValueError(f"Executable helper omitted from publication: {path}")
        files.append({"path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size,
                      "sha256": sha(path), "retention": retention, "reason": reason})
    data = {"created_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            "reference": "Standalone structural discovery; PTM issues1200/1201/1204",
            "ignored_included": True,
            "scope": "All files below this task's research root plus task-owned maintained and adhoc source helpers",
            "self_hash_excluded": True,
            "no_files_removed": True,
            "files": files}
    MANIFEST.write_text(json.dumps(data, indent=2) + "\n")
    print(json.dumps({"manifest": str(MANIFEST.relative_to(ROOT)),
                      "commit_files": sum(row["retention"] == "commit" for row in files),
                      "local_only_files": sum(row["retention"] == "local_only" for row in files),
                      "retained_python_sources": sum(row["path"].endswith(".py") for row in files)}))


if __name__ == "__main__":
    main()
