#!/usr/bin/env python3
"""Acquire three version-pinned apo predictions into a new research snapshot."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys

import gemmi
import yaml

from fetch_source import fetch
from fetch_slc10_pilot import ROOT, RAW

MODEL_PANEL = ("Q14973", "Q96EP9", "Q0GE19")
MODEL_VERSION = 6


def sources():
    rows = [r for r in yaml.safe_load((ROOT / "download.yaml").read_text())
            if r.get("source") == "slc10_models"]
    expected = {f"AF-{p}-F1-model_v{MODEL_VERSION}.cif" for p in MODEL_PANEL}
    if len(rows) != len(expected) or {Path(r["local_name"]).name for r in rows} != expected:
        raise ValueError("model registry differs from the bounded panel")
    for row in rows:
        name = Path(row["local_name"]).name
        if (row["url"] != f"https://alphafold.ebi.ac.uk/files/{name}" or
                row.get("license") != "CC-BY-4.0" or not row.get("license_url")):
            raise ValueError("unreviewed model source contract")
    return rows


def acquire(snapshot, apply=False):
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,79}", snapshot):
        raise ValueError("snapshot must be a simple lowercase identifier")
    destination = RAW / snapshot
    if (RAW.is_symlink() or destination.exists() or destination.is_symlink() or
            not destination.resolve().is_relative_to((ROOT / "data/raw").resolve())):
        raise ValueError("refusing existing, symlinked, or escaped model snapshot")
    rows = sources()
    if not apply:
        return {"destination": str(destination), "sources": rows, "request_limit": 3,
                "qualification": "NONE_APO_PREDICTIONS_ONLY"}
    destination.mkdir(parents=True, exist_ok=False)
    artifacts = []
    for row in rows:
        name = Path(row["local_name"]).name
        path = destination / name
        receipt = fetch(row["url"], path, min_bytes=100_000, contains=("_atom_site.",),
                        max_time=60, retries=0)
        block = gemmi.cif.read_file(str(path)).sole_block()
        if not block.get_mmcif_category("_ma_model_list."):
            raise ValueError("model lacks ModelCIF model metadata")
        receipt.update({"path": name, "license": row["license"], "license_url": row["license_url"],
                        "model_version": MODEL_VERSION})
        artifacts.append(receipt)
        print(f"ACQUIRED {name}", file=sys.stderr, flush=True)
    manifest = {"schema_version": 1, "kind": "SLC10_PREDICTED_MODEL_SNAPSHOT",
                "snapshot": snapshot, "model_version": MODEL_VERSION,
                "fetched_at": datetime.now(timezone.utc).isoformat(), "artifacts": artifacts,
                "qualification": "NONE_APO_PREDICTIONS_ONLY"}
    # Only this last file makes a snapshot consumable. Readers verify every hash.
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
        print(f"Model acquisition failed: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
