#!/usr/bin/env python3
"""Acquire a bounded SLC10 research snapshot, never trait/grounding records.

Dry-run by default. Raw files and a completion manifest live in a NEW ignored
snapshot directory. A partial acquisition has no manifest and cannot be consumed.
Fixed structure/mapping downloads use the shared fetch_source transport. The
exact-accession UniProt API route retains original bodies and release headers.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
import urllib.request

import yaml

from fetch_source import fetch

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/slc10"
PANEL = ("Q14973", "Q12908", "Q3KNW5", "Q96EP9", "Q0GE19", "P26435", "O08705")
STRUCTURES = ("7ZYI", "9QZQ", "8RQF")


def sources():
    rows = [r for r in yaml.safe_load((ROOT / "download.yaml").read_text())
            if r.get("source") == "slc10_pilot"]
    expected = {f"{p}.json" for p in PANEL} | {f"{p}.cif" for p in STRUCTURES} | {
        f"{p.lower()}.xml.gz" for p in STRUCTURES}
    if len(rows) != len(expected) or {r["local_name"].split("/")[-1] for r in rows} != expected:
        raise ValueError("SLC10 source registry differs from the bounded panel")
    for row in rows:
        name = row["local_name"].split("/")[-1]
        if name.endswith(".json"):
            url = f"https://rest.uniprot.org/uniprotkb/{name}"
        elif name.endswith(".cif"):
            url = f"https://files.rcsb.org/download/{name}"
        else:
            url = f"https://ftp.ebi.ac.uk/pub/databases/msd/sifts/xml/{name}"
        if row["url"] != url or not row.get("license") or not row.get("license_url"):
            raise ValueError(f"unreviewed source contract: {name}")
    return rows


def uniprot_response(accession, expected_release):
    url = f"https://rest.uniprot.org/uniprotkb/{accession}.json"
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=45) as response:
        raw = response.read(1_000_001)
        headers = {k.lower(): v for k, v in response.headers.items()}
        if response.status != 200 or len(raw) > 1_000_000:
            raise ValueError(f"invalid or oversized UniProt response: {accession}")
        if headers.get("x-uniprot-release") != expected_release:
            raise ValueError(f"UniProt release mismatch: {accession}")
        entry = json.loads(raw)
        if entry.get("primaryAccession") != accession:
            raise ValueError(f"UniProt accession mismatch: {accession}")
        if not re.fullmatch(r"[ACDEFGHIKLMNPQRSTVWYUOBZJX]+", entry["sequence"]["value"]):
            raise ValueError(f"invalid protein sequence: {accession}")
        if len(entry["sequence"]["value"]) != entry["sequence"]["length"]:
            raise ValueError(f"sequence length mismatch: {accession}")
        return raw, {
            "requested_url": url, "resolved_url": response.geturl(),
            "sha256": hashlib.sha256(raw).hexdigest(), "size_bytes": len(raw),
            "uniprot_release": headers["x-uniprot-release"],
            "sequence_version": entry["entryAudit"]["sequenceVersion"],
            "headers": {k: v for k, v in headers.items() if k in {
                "x-uniprot-release", "x-uniprot-release-date", "etag", "last-modified",
                "content-type"}},
        }


def acquire(snapshot, expected_release, apply=False):
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,79}", snapshot):
        raise ValueError("snapshot must be a simple lowercase identifier")
    if not re.fullmatch(r"\d{4}_\d{2}", expected_release):
        raise ValueError("expected release must have YYYY_NN form")
    destination = RAW / snapshot
    if RAW.is_symlink() or destination.exists() or destination.is_symlink():
        raise ValueError("refusing existing or symlinked snapshot destination")
    if not destination.resolve().is_relative_to((ROOT / "data/raw").resolve()):
        raise ValueError("snapshot escaped ignored raw storage")
    rows = sources()
    plan = {"snapshot": snapshot, "uniprot_release": expected_release,
            "destination": str(destination), "sources": rows,
            "request_limit": 13, "uniprot_max_bytes_per_response": 1_000_000,
            "fixed_file_total_timeout_seconds": 60,
            "qualification": "NONE_RESEARCH_INPUTS_ONLY"}
    if not apply:
        return plan
    destination.mkdir(parents=True, exist_ok=False)
    artifacts = []
    # One entry is the canary: any release/identity failure stops the panel.
    for row in rows:
        name = row["local_name"].split("/")[-1]
        path = destination / name
        if name.endswith(".json"):
            raw, receipt = uniprot_response(name[:-5], expected_release)
            path.write_bytes(raw)
        else:
            kwargs = ({"min_bytes": 100_000, "contains": (f"data_{name[:-4]}",)}
                      if name.endswith(".cif") else
                      {"min_bytes": 1000, "prefix": bytes.fromhex("1f8b")})
            receipt = fetch(row["url"], path, max_time=60, retries=0, **kwargs)
        receipt.update({"path": name, "license": row["license"],
                        "license_url": row["license_url"]})
        artifacts.append(receipt)
        print(f"ACQUIRED {name}", file=sys.stderr, flush=True)
    manifest = {"schema_version": 1, "kind": "SLC10_RESEARCH_SNAPSHOT",
                "snapshot": snapshot, "uniprot_release": expected_release,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "artifacts": artifacts, "qualification": "NONE_RESEARCH_INPUTS_ONLY"}
    (destination / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", required=True)
    parser.add_argument("--expect-release", required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    try:
        print(json.dumps(acquire(args.snapshot, args.expect_release, args.apply),
                         indent=2, sort_keys=True))
    except (ValueError, OSError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
