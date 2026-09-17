#!/usr/bin/env python3
"""Seed the positive protein signatures from eLife 109154 (dry-run by default)."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

import yaml

from elife_metallophores import (
    RAW, build_record, catalog, source_facts, trait_path, verified_archive, write_jsonl,
)
from record_io import write_record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--raw", type=Path, default=RAW)
    args = parser.parse_args()
    with verified_archive(args.raw / "nrp-metallophore-SI.zip") as archive:
        models, members = source_facts(archive)
        if args.apply:
            for model in models.values():
                if model["hmm_available"]:
                    target = args.raw / model["hmm_path"]
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(archive.read(model["hmm_path"]))
    written = skipped = 0
    for model in catalog()["traits"]:
        path = trait_path(model)
        if path.exists() and not args.force:
            skipped += 1
            continue
        if args.apply:
            path.parent.mkdir(parents=True, exist_ok=True)
            write_record(path, yaml.safe_dump(build_record(model, models), sort_keys=False,
                                             allow_unicode=True, width=95), validate=True)
            written += 1
    if args.apply:
        write_jsonl(args.raw / "seed_members.jsonl", members)
        write_jsonl(args.raw / "models.jsonl", list(models.values()))
    print(json.dumps({"traits": len(catalog()["traits"]), "written": written, "skipped": skipped,
                      "source_memberships": dict(Counter(r["source_kind"] for r in members)),
                      "applied": args.apply}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
