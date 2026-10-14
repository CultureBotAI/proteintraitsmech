#!/usr/bin/env python3
"""Publish the validated research bundle byte-for-byte as a versioned docs export.

No raw downloads or heavy dependencies are required at Pages-build time. The
scientific validation gate is validate_molecular_evidence.py and its corpus test.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]


def exports(raw):
    bundle = json.loads(raw)
    if bundle.get("bundle_id") != "ptm-molecular:slc10" or not re.fullmatch(r"[1-9][0-9]*", bundle.get("version", "")):
        raise ValueError("unexpected bundle identity or version")
    version = bundle["version"]
    name = f"slc10-pilot-v{version}.json"
    receipt = {"bundle_id": bundle["bundle_id"], "version": version, "file": name,
               "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw),
               "status": "PROPOSED_RESEARCH_NOT_GO_ANNOTATIONS"}
    return {name: raw, "slc10-pilot-manifest.json": (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode()}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    output = ROOT / "docs/data"
    try:
        for name, raw in exports((ROOT / "data/molecular/slc10/pilot.json").read_bytes()).items():
            path = output / name
            if path.is_symlink() or output.is_symlink():
                raise ValueError("refusing symlinked molecular export")
            if args.check:
                if not path.is_file() or path.read_bytes() != raw:
                    raise ValueError(f"stale molecular export: {name}")
            else:
                output.mkdir(parents=True, exist_ok=True)
                path.write_bytes(raw)
            print(f"{'CHECKED' if args.check else 'EXPORTED'} {name}: {len(raw)} bytes")
    except (ValueError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
