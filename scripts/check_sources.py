#!/usr/bin/env python3
"""Validate data/sources.yaml and cross-check it against the seeders.

Checks:
  - required fields present, `status` in the allowed set, keys unique;
  - every `status: seeded` source names a `seeder:` whose script exists;
  - every scripts/seed_*.py is referenced by at least one registry entry
    (orphan seeders → warning);
  - `license` present for every source (and NC/ND/login licences flagged).

Exit non-zero on any error (warnings don't fail). Stdlib + PyYAML.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
REGISTRY = REPO_ROOT / "data" / "sources.yaml"
SCRIPTS = REPO_ROOT / "scripts"

REQUIRED = ("key", "name", "status", "description", "homepage", "download", "license")
STATUSES = {"seeded", "candidate", "deferred", "rejected"}
RESTRICTIVE = ("noncommercial", "non-commercial", "-nc", "noderiv", "-nd", "login", "registration")


def main() -> int:
    if not REGISTRY.exists():
        print(f"ERROR: {REGISTRY.relative_to(REPO_ROOT)} not found", file=sys.stderr)
        return 2
    doc = yaml.safe_load(REGISTRY.read_text(encoding="utf-8")) or {}
    sources = doc.get("sources") or []
    errors: list[str] = []
    warnings: list[str] = []

    seen_keys: set[str] = set()
    referenced_scripts: set[str] = set()
    for s in sources:
        key = s.get("key", "<no key>")
        for f in REQUIRED:
            if not s.get(f):
                errors.append(f"[{key}] missing required field: {f}")
        if s.get("status") not in STATUSES:
            errors.append(f"[{key}] invalid status {s.get('status')!r} (allowed: {sorted(STATUSES)})")
        if key in seen_keys:
            errors.append(f"duplicate key: {key}")
        seen_keys.add(key)

        lic = str(s.get("license", "")).lower()
        if any(t in lic for t in RESTRICTIVE):
            warnings.append(f"[{key}] restrictive licence for a CC0 KB: {s.get('license')}")

        seeder = s.get("seeder")
        if seeder:
            script = seeder.split()[0]  # strip "(psimi)" style args
            referenced_scripts.add(script)
            if not (SCRIPTS / script).exists():
                errors.append(f"[{key}] seeder script not found: scripts/{script}")
        elif s.get("status") == "seeded":
            errors.append(f"[{key}] status=seeded but no seeder: field")

    # Orphan seeders: seed_*.py with no registry reference.
    for script in sorted(SCRIPTS.glob("seed_*.py")):
        if script.name not in referenced_scripts:
            warnings.append(f"seeder scripts/{script.name} is not referenced by any source in the registry")

    seeded = sum(1 for s in sources if s.get("status") == "seeded")
    cand = sum(1 for s in sources if s.get("status") == "candidate")
    print(f"data/sources.yaml: {len(sources)} sources "
          f"({seeded} seeded, {cand} candidate, "
          f"{sum(1 for s in sources if s.get('status')=='deferred')} deferred, "
          f"{sum(1 for s in sources if s.get('status')=='rejected')} rejected)")
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
