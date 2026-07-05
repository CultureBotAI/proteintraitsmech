#!/usr/bin/env python3
"""Re-scope coiled-coil records off the SEQUENCE_STRUCTURE axis.

Background: an early commit ("Canonicalize coiled coils to MIXED", cf3c605df4)
parked every Pfam coiled-coil entry — and the generic LSF coiled-coil concept —
on SEQUENCE_STRUCTURE / MIXED_COILED_COIL. That predates the axis-follows-
representation rule ("a domain detected by a sequence model is a sequence
trait"). A Pfam coiled-coil is a profile-HMM signature with no structural
representation of its own, so it belongs on the SEQUENCE axis.

This migration (idempotent, dry-run unless --apply):

  • 314 Pfam MIXED_COILED_COIL records
        trait_axis  SEQUENCE_STRUCTURE → SEQUENCE
        trait_category MIXED_COILED_COIL → SEQ_DOMAIN
        file  data/traits/mixed/coiled_coil/pfam/ → data/traits/sequence/domain/pfam/
        (also strips leftover "( )" citation stubs from Pfam→InterPro abstracts)

  • the generic proteintraitsmech:COILED_COIL umbrella node
        trait_axis  SEQUENCE_STRUCTURE → STRUCTURE
        trait_category MIXED_COILED_COIL → STRUCT_SECONDARY
        file → data/traits/structure/secondary/coiled-coil.yaml
        (this is exactly what seed_localstructuralfeature.py already emits for
        COILED_COIL — the migration realigns the record with its seeder)

RepeatsDB MIXED_STRUCTURAL_REPEAT records are deliberately left on
SEQUENCE_STRUCTURE — they are structure-derived and carry real geometry reps.

After this runs, MIXED_COILED_COIL is empty and the SEQUENCE_STRUCTURE axis holds
only the RepeatsDB structural repeats. seed_pfam.py is updated in lockstep so a
re-seed emits Pfam coiled-coils as SEQ_DOMAIN directly.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TRAITS = REPO_ROOT / "data" / "traits"
PFAM_SRC = TRAITS / "mixed" / "coiled_coil" / "pfam"
PFAM_DST = TRAITS / "sequence" / "domain" / "pfam"
PARENT_SRC = TRAITS / "mixed" / "coiled_coil" / "coiled-coil.yaml"
PARENT_DST = TRAITS / "structure" / "secondary" / "coiled-coil.yaml"

# Empty "[ ]" / "( )" / "( , )" stubs left after citation tags were stripped.
_STUB_RE = re.compile(r"\s*[\[(]\s*(?:,\s*)*[\])]")

PARENT_YAML = """\
identifier: proteintraitsmech:COILED_COIL
label: coiled coil
definition: >-
  Generic coiled-coil region: two or more alpha helices wound together like the
  strands of a rope, combining a heptad-repeat sequence signature with a
  supercoiled helical-bundle topology. Modelled as a super-secondary structural
  element (STRUCT_SECONDARY). Source-derived coiled-coil families detected by a
  sequence signature (e.g. the Pfam entries) are SEQ_DOMAIN on the SEQUENCE axis,
  per the axis-follows-representation convention.
definition_source: https://linkml.io/valuesets/elements/LocalStructuralFeature/
trait_axis: STRUCTURE
trait_category: STRUCT_SECONDARY
term_kind: CLASS
mapping_status: SEEDED
xrefs:
- SO:0001080
- valuesets:LocalStructuralFeature
- SO:0001114
license: CC0-1.0
"""


def migrate_pfam(apply: bool) -> int:
    if not PFAM_SRC.is_dir():
        print(f"  (no {PFAM_SRC.relative_to(REPO_ROOT)} — already migrated?)")
        return 0
    n = cleaned = 0
    for src in sorted(PFAM_SRC.glob("*.yaml")):
        text = src.read_text(encoding="utf-8")
        new = text.replace("trait_axis: SEQUENCE_STRUCTURE", "trait_axis: SEQUENCE")
        new = new.replace("trait_category: MIXED_COILED_COIL", "trait_category: SEQ_DOMAIN")
        # _STUB_RE's leading \s* consumes the space before the stub, so removal
        # leaves no doubled space — must NOT touch YAML indentation.
        stubbed = _STUB_RE.sub("", new)
        if stubbed != new:
            cleaned += 1
            new = stubbed
        dst = PFAM_DST / src.name
        n += 1
        if apply:
            PFAM_DST.mkdir(parents=True, exist_ok=True)
            dst.write_text(new, encoding="utf-8")
            src.unlink()
    print(f"  Pfam coiled-coils → SEQUENCE/SEQ_DOMAIN: {n} records "
          f"({cleaned} had '( )' stubs cleaned)")
    return n


def migrate_parent(apply: bool) -> int:
    if not PARENT_SRC.exists():
        print(f"  (no {PARENT_SRC.relative_to(REPO_ROOT)} — already migrated?)")
        return 0
    print(f"  COILED_COIL umbrella → STRUCTURE/STRUCT_SECONDARY "
          f"({PARENT_DST.relative_to(REPO_ROOT)})")
    if apply:
        PARENT_DST.parent.mkdir(parents=True, exist_ok=True)
        PARENT_DST.write_text(PARENT_YAML, encoding="utf-8")
        PARENT_SRC.unlink()
    return 1


def prune_empty(apply: bool) -> None:
    # Remove the now-empty mixed/coiled_coil tree.
    for d in [PFAM_SRC, PFAM_SRC.parent, PFAM_SRC.parent.parent]:
        if d.is_dir() and not any(d.iterdir()):
            print(f"  rmdir {d.relative_to(REPO_ROOT)}")
            if apply:
                d.rmdir()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry-run)")
    args = ap.parse_args()
    print(f"{'APPLYING' if args.apply else 'DRY-RUN'} coiled-coil re-scope:")
    migrate_pfam(args.apply)
    migrate_parent(args.apply)
    prune_empty(args.apply)
    if not args.apply:
        print("\nRe-run with --apply to write.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
