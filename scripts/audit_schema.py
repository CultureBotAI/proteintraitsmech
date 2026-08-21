#!/usr/bin/env python3
r"""Programmatic schema-quality probes (#496).

`just audit-schema` has existed in the justfile, and been listed in CLAUDE.md as a working
command, for the life of this repo. `scripts/audit_schema.py` never existed -- not deleted,
never written. The recipe died with `can't open file` every time anyone ran it, and because
it is in no CI workflow, nothing was ever red about it.

That is the failure this file is about as much as anything it checks: **a recipe that has
never run is indistinguishable from one that passes**, and CLAUDE.md is what an agent reads
to learn what this repo can do.

WHAT IT PROBES, AND WHY THESE
------------------------------
Deliberately the checks the other gates do not make. `validate-strict` asks whether records
match the schema; `audit-graphs` asks whether graphs are structurally sound. Neither asks
whether the SCHEMA ITSELF is coherent:

  1. UNREACHABLE CLASSES -- a class no slot ranges over and nothing inherits from. Dead
     weight that still shows up in generated dataclasses and docs.
  2. UNUSED ENUM VALUES -- a permissible value no record uses. Not automatically wrong (a
     value can be aspirational), so this REPORTS rather than fails; the number is the
     point.
  3. RULES THAT CANNOT FIRE -- a precondition matching no permissible value. This repo's
     five axis/category rules are its central invariant, and a rule whose pattern matches
     nothing enforces nothing while looking exactly like enforcement.
  4. CATEGORIES NO RULE COVERS -- the converse, and the more dangerous direction: a
     `*_CATEGORY` prefix with no rule tying it to an axis is a category that can be filed
     on any axis at all.

Read-only, needs no `data/raw`, and reads records only to count enum usage -- so it runs in
CI. Exit 1 on a defect in (1), (3) or (4); (2) is reported.
"""

from __future__ import annotations

import argparse
import collections
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = ROOT / "src" / "proteintraitsmech" / "schema" / "proteintraitsmech.yaml"
TRAITS = ROOT / "data" / "traits"
# TWO roots, not one. `ProteinProfile` ("A Swiss-Prot protein and the corpus trait classes
# it carries") is written to data/profiles by build_swissprot_profiles -- a second document
# type, not dead weight. The first version of this audit assumed a single root and reported
# it and `ProfileTrait` as unreachable classes, which is an audit reporting a design as a
# defect. Neither carries `tree_root: true`, so the roots are named here.
ROOT_CLASSES = ("ProteinTraitRecord", "ProteinProfile")

# Category prefixes deliberately NOT bound to an axis. README: "`UPPER` / `OTHER` are
# administrative and may appear on any axis." Declared rather than special-cased silently,
# so that the day someone adds a third the audit asks about it.
AXIS_FREE_PREFIXES = {"UPPER", "OTHER"}


def load_schema(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def reachable_classes(schema: dict) -> set[str]:
    """Classes reachable from the root by slot ranges or inheritance.

    Walked rather than assumed: a class can be reached through a slot's `range`, through
    `is_a`, or by being a mixin, and counting only one of those would report the other two
    as dead.
    """
    classes = schema.get("classes") or {}
    seen: set[str] = set()
    stack = list(ROOT_CLASSES)
    while stack:
        name = stack.pop()
        if name in seen or name not in classes:
            continue
        seen.add(name)
        cls = classes[name]
        for attr in (cls.get("attributes") or {}).values():
            rng = attr.get("range")
            if rng in classes:
                stack.append(rng)
        for key in ("is_a", "mixins"):
            val = cls.get(key)
            for parent in ([val] if isinstance(val, str) else (val or [])):
                stack.append(parent)
    # anything that inherits FROM a reachable class is itself reachable
    for _ in range(len(classes)):
        grew = False
        for name, cls in classes.items():
            if name in seen:
                continue
            parents = [cls.get("is_a")] + list(cls.get("mixins") or [])
            if any(p in seen for p in parents if p):
                seen.add(name)
                grew = True
        if not grew:
            break
    return seen


def enum_usage(schema: dict, traits: Path) -> dict[str, collections.Counter]:
    """enum name -> Counter of permissible values seen on disk.

    Counted by a line-anchored scan of the slots whose range is that enum, not by parsing
    429,271 records: the values are single-token scalars and the scan is seconds rather
    than minutes.
    """
    classes = schema.get("classes") or {}
    slot_to_enum: dict[str, str] = {}
    for cls in classes.values():
        for slot, attr in (cls.get("attributes") or {}).items():
            rng = attr.get("range")
            if rng in (schema.get("enums") or {}):
                slot_to_enum[slot] = rng
    counts: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    if not traits.is_dir():
        return counts
    pattern = re.compile(
        r"^\s*(" + "|".join(re.escape(s) for s in slot_to_enum) + r"):\s*[\"']?([A-Za-z0-9_]+)",
        re.M)
    for path in traits.rglob("*.yaml"):
        for slot, value in pattern.findall(path.read_text(encoding="utf-8")):
            counts[slot_to_enum[slot]][value] += 1
    return counts


def rule_coverage(schema: dict) -> tuple[list[str], list[str]]:
    """(rules whose precondition matches no enum value, category prefixes no rule covers).

    The second is the dangerous direction. A `SEQ_*` category with no rule binding it to
    the SEQUENCE axis can be filed on any axis, and every record carrying it validates.
    """
    cls = (schema.get("classes") or {}).get("ProteinTraitRecord") or {}
    categories = list(((schema.get("enums") or {})
                       .get("ProteinTraitCategoryEnum") or {}).get("permissible_values") or {})
    dead: list[str] = []
    covered: set[str] = set()
    for rule in cls.get("rules") or []:
        pre = ((rule.get("preconditions") or {}).get("slot_conditions") or {})
        pattern = (pre.get("trait_category") or {}).get("pattern")
        if not pattern:
            continue
        matching = [c for c in categories if re.search(pattern, c)]
        if not matching:
            dead.append(f"{rule.get('title', '<untitled>')} (pattern {pattern!r})")
        covered.update(matching)
    uncovered_prefixes = sorted({c.split("_")[0] for c in categories
                                 if c not in covered} - AXIS_FREE_PREFIXES)
    return dead, uncovered_prefixes


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--schema", default=str(SCHEMA))
    ap.add_argument("--traits", default=str(TRAITS))
    ap.add_argument("--show", type=int, default=12)
    args = ap.parse_args()

    schema_path = Path(args.schema)
    if not schema_path.is_file():
        print(f"FAIL: {schema_path} not found")
        return 2
    schema = load_schema(schema_path)
    classes = schema.get("classes") or {}
    enums = schema.get("enums") or {}
    if not classes:
        # #418/#432/#469: a probe that read nothing must not report a clean schema.
        print("FAIL: the schema declares no classes; this examined nothing.")
        return 1
    print(f"schema: {len(classes)} classes, {len(enums)} enums")

    failures = 0

    reachable = reachable_classes(schema)
    orphans = sorted(set(classes) - reachable)
    if orphans:
        failures += 1
        print(f"\nFAIL: {len(orphans)} class(es) unreachable from any root "
              f"({', '.join(ROOT_CLASSES)}) -- no slot "
              f"ranges over them and nothing inherits from them:")
        for name in orphans[:args.show]:
            print(f"  {name}")
    else:
        print(f"  every class reachable from a root: yes ({len(reachable)})")

    dead_rules, uncovered = rule_coverage(schema)
    if dead_rules:
        failures += 1
        print(f"\nFAIL: {len(dead_rules)} rule(s) whose precondition matches no category. "
              f"A rule matching nothing enforces nothing while looking like enforcement:")
        for line in dead_rules:
            print(f"  {line}")
    if uncovered:
        failures += 1
        print(f"\nFAIL: {len(uncovered)} category prefix(es) no axis rule covers. A "
              f"category with no rule binding it to an axis can be filed on ANY axis:")
        for prefix in uncovered[:args.show]:
            print(f"  {prefix}_*")
    if not dead_rules and not uncovered:
        print("  every category prefix is bound to an axis by a rule: yes")

    usage = enum_usage(schema, Path(args.traits))
    if usage:
        print("\nunused permissible values (reported, not failed -- a value may be "
              "aspirational):")
        total_unused = 0
        for name, spec in sorted(enums.items()):
            values = set((spec.get("permissible_values") or {}))
            unused = sorted(values - set(usage.get(name, {})))
            if unused:
                total_unused += len(unused)
                shown = ", ".join(unused[:6]) + (" …" if len(unused) > 6 else "")
                print(f"  {name:<28} {len(unused):>3} of {len(values):<3}  {shown}")
        print(f"  total unused: {total_unused}")
    else:
        print("\n(no records read, so enum usage was not measured)")

    if failures:
        return 1
    print("\nOK: schema is internally coherent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
