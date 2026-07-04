#!/usr/bin/env python3
"""Seed curated microbial functional-module traits from the SEED subsystems
catalogue, served via BV-BRC (US Government public domain) → FUNCTION /
FUNC_PATHWAY.

A SEED **subsystem** is a curator-defined set of functional roles that act
together in a system — a metabolic pathway, module, or complex — grouped under
a 3-level classification spine (superclass → class → subclass). We seed the
**class-level** catalogue only (never per-genome / per-gene instances):

  - the superclass / class / subclass hierarchy as parent spine nodes
    (proteintraitsmech:SEED_SUPERCLASS_/SEED_CLASS_/SEED_SUBCLASS_), and
  - one FUNC_PATHWAY record per subsystem (~920), parent-chained to its
    subclass (or class / superclass), definition from the curated description,
    and the DISTINCT EC numbers parsed from its role names attached as
    `mapped_xrefs` to the already-seeded EC hierarchy — NOT as new records.

Functional roles are deliberately NOT emitted: EC-bearing roles are redundant
with the ExPASy ENZYME EC hierarchy already seeded by seed_ec.py.

Input (fetch via `just fetch-seed-subsystems`, gitignored):
  data/raw/seed_subsystems/subsystem_ref.json
    JSON array from the BV-BRC Data API `subsystem_ref` endpoint; each record
    carries superclass, class, subclass, subsystem_id, subsystem_name,
    description, role_name[] (functional roles, EC inline in parentheses).

Provenance: SEED/RAST (Overbeek et al., NAR 2005; Aziz et al., BMC Genomics
2008) curated the subsystems; BV-BRC (Olson et al., NAR 2023, PMC9825582)
distributes them as US-Government public-domain data. Citation requested, not
required — see https://www.bv-brc.org/citation.

Idempotent; dry-run unless --apply. Stdlib-only.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW = REPO_ROOT / "data" / "raw" / "seed_subsystems"
SRC = RAW / "subsystem_ref.json"
OUT_DIR = REPO_ROOT / "data" / "traits" / "function" / "pathway" / "seed"
SPINE_DIR = OUT_DIR / "spine"
LICENSE = "US Government public domain (BV-BRC)"
DEFINITION_SOURCE = "BV-BRC"

_SLUG_RE = re.compile(r"[^A-Za-z0-9]+")
_IDPART_RE = re.compile(r"[^A-Za-z0-9._-]+")
# EC number embedded in a role name, e.g. "... (EC 6.3.2.4)" — allow partial
# (1.1.1.-) and preliminary (1.13.11.n1) EC classes.
_EC_RE = re.compile(r"\(EC ([0-9]+\.[0-9-]+\.[0-9-]+\.[0-9n-]+)\)")


def slugify(t: str) -> str:
    return (_SLUG_RE.sub("-", (t or "").lower()).strip("-")[:70]) or "seed"


def idpart(t: str) -> str:
    """CURIE-safe local-part token (keeps [A-Za-z0-9._-], preserves case)."""
    return _IDPART_RE.sub("_", (t or "").strip()).strip("_") or "Unclassified"


def id_filename(node_id: str) -> str:
    """Collision-free filename from a CURIE local part (no truncation)."""
    return _SLUG_RE.sub("-", node_id.split(":", 1)[1].lower()).strip("-")


def yaml_escape(text: str) -> str:
    if not text:
        return '""'
    unsafe = set(': #{}[],&*!|>%@`\\"\'')
    if (any(c in unsafe for c in text) or text[0] in "-?"
            or text.lower() in {"null", "true", "false", "yes", "no", "on", "off"}):
        return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return text


def folded(text: str) -> list[str]:
    return [">-", f"  {' '.join((text or '').split())}"]


def spine_ids(superclass: str, klass: str, subclass: str):
    """Return (super_id, class_id, subclass_id) CURIEs; None where absent."""
    sup = idpart(superclass) if superclass else None
    super_id = f"proteintraitsmech:SEED_SUPERCLASS_{sup}" if sup else None
    sup_key = sup or "Unclassified"
    class_id = (f"proteintraitsmech:SEED_CLASS_{sup_key}__{idpart(klass)}"
                if klass else None)
    subclass_id = (
        f"proteintraitsmech:SEED_SUBCLASS_{sup_key}__{idpart(klass)}__{idpart(subclass)}"
        if subclass else None)
    return super_id, class_id, subclass_id


def build_spine_yaml(node_id, label, level, parent_id):
    definition = (f"{label} — a SEED/BV-BRC subsystem {level}; a curated "
                  f"classification grouping of prokaryotic functional modules "
                  f"(subsystems).")
    lines = ["# Source: SEED subsystems via BV-BRC "
             "(US Government public domain); https://www.bv-brc.org/citation",
             f"identifier: {node_id}", f"label: {yaml_escape(label)}"]
    f = folded(definition)
    lines += [f"definition: {f[0]}", *f[1:]]
    lines += [f"definition_source: {DEFINITION_SOURCE}", "trait_axis: FUNCTION",
              "trait_category: FUNC_PATHWAY", "term_kind: CLASS",
              "mapping_status: SEEDED"]
    if parent_id:
        lines += ["parent_traits:", f"  - {parent_id}"]
    lines.append(f"license: {LICENSE}")
    return "\n".join(lines) + "\n"


def build_subsystem_yaml(rec, node_id, parent_id, ecs):
    name = rec.get("subsystem_name") or rec.get("subsystem_id")
    desc = " ".join((rec.get("description") or "").split())
    if desc:
        definition = desc
    else:
        definition = (f"{name} — a SEED/BV-BRC subsystem: a curator-defined set "
                      f"of functional roles that act together in a system "
                      f"(pathway, module, or complex).")
    lines = ["# Source: SEED subsystem via BV-BRC "
             "(US Government public domain); https://www.bv-brc.org/citation",
             f"# subsystem_id: {rec.get('subsystem_id')}",
             f"identifier: {node_id}", f"label: {yaml_escape(name)}"]
    f = folded(definition)
    lines += [f"definition: {f[0]}", *f[1:]]
    lines += [f"definition_source: {DEFINITION_SOURCE}", "trait_axis: FUNCTION",
              "trait_category: FUNC_PATHWAY", "term_kind: CLASS",
              "mapping_status: SEEDED"]
    if parent_id:
        lines += ["parent_traits:", f"  - {parent_id}"]
    if ecs:
        lines += ["mapped_xrefs:"]
        for ec in ecs:
            lines += [f"  - object: EC:{ec}",
                      "    predicate: biolink:related_to",
                      "    mapping_source: seed_role_ec"]
    lines.append(f"license: {LICENSE}")
    return "\n".join(lines) + "\n"


def parse_ecs(rec) -> list[str]:
    ecs = set()
    for role in (rec.get("role_name") or []):
        for m in _EC_RE.findall(role or ""):
            ecs.add(m)
    return sorted(ecs)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    if not SRC.exists():
        print("missing data/raw/seed_subsystems/subsystem_ref.json; "
              "run `just fetch-seed-subsystems`", file=sys.stderr)
        return 2

    records = json.loads(SRC.read_text(encoding="utf-8"))

    # (path, yaml_text) planned records; spine deduped by identifier.
    spine: dict[str, tuple[str, str]] = {}  # node_id -> (slug, yaml_text)
    n_ec_xrefs = 0
    n_sub_with_ec = 0
    subsystem_plan: list[tuple[str, str]] = []  # (slug, yaml_text)

    for rec in records:
        superclass = (rec.get("superclass") or "").strip()
        klass = (rec.get("class") or "").strip()
        subclass = (rec.get("subclass") or "").strip()
        super_id, class_id, subclass_id = spine_ids(superclass, klass, subclass)

        # Register spine nodes (dedup by identifier).
        if super_id and super_id not in spine:
            spine[super_id] = (id_filename(super_id),
                               build_spine_yaml(super_id, superclass,
                                                "superclass", None))
        if class_id and class_id not in spine:
            spine[class_id] = (id_filename(class_id),
                               build_spine_yaml(class_id, klass, "class",
                                                super_id))
        if subclass_id and subclass_id not in spine:
            spine[subclass_id] = (id_filename(subclass_id),
                                  build_spine_yaml(subclass_id, subclass,
                                                   "subclass", class_id))

        parent_id = subclass_id or class_id or super_id
        sub_id = rec.get("subsystem_id") or ""
        if not sub_id:
            continue
        node_id = f"proteintraitsmech:SEED_SUBSYSTEM_{idpart(sub_id)}"
        ecs = parse_ecs(rec)
        if ecs:
            n_sub_with_ec += 1
            n_ec_xrefs += len(ecs)
        slug = id_filename(node_id)
        subsystem_plan.append(
            (slug, build_subsystem_yaml(rec, node_id, parent_id, ecs)))

    written = skipped = 0
    for node_id, (slug, text) in spine.items():
        path = SPINE_DIR / f"{slug}.yaml"
        if path.exists() and not args.force:
            skipped += 1
            continue
        if args.apply:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
            written += 1

    for slug, text in subsystem_plan:
        path = OUT_DIR / f"{slug}.yaml"
        if path.exists() and not args.force:
            skipped += 1
            continue
        if args.apply:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
            written += 1

    total = len(spine) + len(subsystem_plan)
    print(f"{total} SEED records "
          f"({len(spine)} spine nodes, {len(subsystem_plan)} subsystems).")
    print(f"EC grounding: {n_sub_with_ec} subsystems carry mapped_xrefs; "
          f"{n_ec_xrefs} EC xref rows total.")
    if args.apply:
        print(f"Wrote {written}; skipped {skipped} existing → "
              f"{OUT_DIR.relative_to(REPO_ROOT)}/")
    else:
        print(f"Dry-run — would write {total - skipped}; {skipped} exist.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
