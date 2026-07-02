#!/usr/bin/env python3
"""Validate download.yaml (kghub-downloader manifest + source catalogue) and
cross-check it against the seeders.

download.yaml is a flat YAML list of blocks. Each block needs a `url`; blocks
that describe a source (not just a secondary file) also carry `name`, `source`,
`license`, `status`, and — when seeded — `seeder`.

Checks:
  - every block has a `url`;
  - any `status` is in the allowed set;
  - every distinct `source` marked seeded names a `seeder:` whose script exists;
  - every scripts/seed_*.py is referenced by some block (orphans → warning);
  - restrictive (NC/ND/login) licences are flagged.

Exit non-zero on error; warnings don't fail. Stdlib + PyYAML.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST = REPO_ROOT / "download.yaml"
SCRIPTS = REPO_ROOT / "scripts"

STATUSES = {"seeded", "candidate", "deferred", "rejected"}
RESTRICTIVE = ("noncommercial", "non-commercial", "-nc", "byncnd", "by-nc",
               "noderiv", "-nd", "login", "registration", "flagged")


def main() -> int:
    if not MANIFEST.exists():
        print(f"ERROR: {MANIFEST.name} not found", file=sys.stderr)
        return 2
    blocks = yaml.safe_load(MANIFEST.read_text(encoding="utf-8")) or []
    if not isinstance(blocks, list):
        print("ERROR: download.yaml must be a YAML list", file=sys.stderr)
        return 2

    errors: list[str] = []
    warnings: list[str] = []
    referenced: set[str] = set()
    source_status: dict[str, str] = {}
    source_seeder: dict[str, str] = {}

    for i, b in enumerate(blocks):
        tag = b.get("name") or b.get("source") or f"block[{i}]"
        if not b.get("url"):
            errors.append(f"[{tag}] missing required field: url")
        st = b.get("status")
        if st is not None and st not in STATUSES:
            errors.append(f"[{tag}] invalid status {st!r}")
        src = b.get("source")
        if src and st:
            source_status[src] = st
        if src and b.get("seeder"):
            source_seeder[src] = b["seeder"].split()[0]
        if b.get("seeder"):
            script = b["seeder"].split()[0]
            referenced.add(script)
            if not (SCRIPTS / script).exists():
                errors.append(f"[{tag}] seeder script not found: scripts/{script}")
        lic = str(b.get("license", "")).lower()
        if any(t in lic for t in RESTRICTIVE):
            warnings.append(f"[{tag}] restrictive licence for a CC0 KB: {b.get('license')}")

    for src, st in source_status.items():
        if st == "seeded" and src not in source_seeder:
            errors.append(f"source '{src}' is seeded but no block names its seeder:")

    for script in sorted(SCRIPTS.glob("seed_*.py")):
        if script.name not in referenced:
            warnings.append(f"seeder scripts/{script.name} is not referenced in download.yaml")

    by_status: dict[str, int] = {}
    for st in source_status.values():
        by_status[st] = by_status.get(st, 0) + 1
    print(f"download.yaml: {len(blocks)} blocks, {len(source_status)} sources "
          f"({', '.join(f'{n} {s}' for s, n in sorted(by_status.items()))})")
    for w in warnings:
        print(f"  WARN: {w}")
    for e in errors:
        print(f"  ERROR: {e}")
    if errors:
        print(f"\n{len(errors)} error(s).")
        return 1
    print(f"\nOK ({len(warnings)} warning(s)).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
