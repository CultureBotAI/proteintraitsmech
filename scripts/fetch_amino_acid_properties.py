#!/usr/bin/env python3
"""Fetch a bounded amino-acid chemistry snapshot; no trait or annotation writes.

Fixed files use fetch_source. New ignored snapshots only; a partial acquisition
never receives a completion manifest. Downloaded Python is data, never executed.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys

import yaml

from fetch_source import fetch

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/amino_acid_properties"
COMPONENTS = ("ALA", "ARG", "ASN", "ASP", "CYS", "GLU", "GLN", "GLY", "HIS", "ILE",
              "LEU", "LYS", "MET", "PHE", "PRO", "SER", "THR", "TRP", "TYR", "VAL")
BIOPYTHON = "https://raw.githubusercontent.com/biopython/biopython/biopython-185"
CONTRACT = {f"{code}.cif": (f"https://files.rcsb.org/ligands/download/{code}.cif", "CC0-1.0",
                           "https://www.wwpdb.org/about/usage-policies") for code in COMPONENTS}
CONTRACT.update({name: (f"{BIOPYTHON}/Bio/SeqUtils/{name}", "BSD-3-Clause",
                        f"{BIOPYTHON}/LICENSE.rst")
                 for name in ("ProtParamData.py", "IsoelectricPoint.py")})


def sources():
    rows = [r for r in yaml.safe_load((ROOT / "download.yaml").read_text())
            if r.get("source") == "amino_acid_properties"]
    if len(rows) != len(CONTRACT) or {r["local_name"] for r in rows} != {
            f"amino_acid_properties/{name}" for name in CONTRACT}:
        raise ValueError("amino-acid source registry differs from the bounded 22-file contract")
    for row in rows:
        name = Path(row["local_name"]).name
        if tuple(row.get(k) for k in ("url", "license", "license_url")) != CONTRACT[name]:
            raise ValueError(f"unreviewed source contract: {name}")
    return sorted(rows, key=lambda row: row["local_name"])


def acquire(snapshot, apply=False):
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,79}", snapshot):
        raise ValueError("snapshot must be a simple lowercase identifier")
    destination = RAW / snapshot
    if any(path.is_symlink() for path in (destination, RAW, RAW.parent, RAW.parent.parent)):
        raise ValueError("refusing symlinked snapshot storage")
    if destination.exists():
        raise ValueError("refusing existing snapshot destination")
    rows = sources()
    plan = {"snapshot": snapshot, "sources": rows, "destination": str(destination),
            "request_limit": len(rows), "per_file_deadline_seconds": 45,
            "qualification": "NONE_REFERENCE_CHEMISTRY_ONLY"}
    if not apply:
        return plan
    destination.mkdir(parents=True, exist_ok=False)
    artifacts = []
    for row in rows:
        name = Path(row["local_name"]).name
        marker = f"data_{name[:-4]}" if name.endswith(".cif") else (
            "kd =" if name == "ProtParamData.py" else "positive_pKs =")
        receipt = fetch(row["url"], destination / name, max_time=45, retries=1,
                        min_bytes=1000, contains=(marker,))
        receipt.update(path=name, license=row["license"], license_url=row["license_url"])
        artifacts.append(receipt)
        print(f"ACQUIRED {name}", file=sys.stderr, flush=True)
    manifest = {"kind": "AMINO_ACID_PROPERTY_SNAPSHOT", "schema_version": 1,
                "snapshot": snapshot, "fetched_at": datetime.now(timezone.utc).isoformat(),
                "artifacts": artifacts, "qualification": plan["qualification"]}
    (destination / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    try:
        print(json.dumps(acquire(args.snapshot, args.apply), indent=2, sort_keys=True))
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"amino-acid property acquisition failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
