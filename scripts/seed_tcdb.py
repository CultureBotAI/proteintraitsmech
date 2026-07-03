#!/usr/bin/env python3
"""Seed membrane-transport traits from the Transporter Classification
Database (TCDB, CC-BY-SA 3.0) → FUNCTION / FUNC_TRANSPORT.

TCDB classifies transport systems in a 5-level TC number
(Class.Subclass.Family.Subfamily.System, e.g. 1.A.1.1.1). As with CATH /
SCOP we seed the **classification classes**, not the individual transport
systems (which are protein instances): the ~2,225 TC **families** (3-level
ids like 1.A.1), plus synthesized **subclass** (1.A) and **class** (1) nodes
so the hierarchy is navigable.

Inputs (fetch via `just fetch-tcdb`, gitignored):
  data/raw/tcdb/families.tsv    "<TC>\\t<family name>"           (families.py)
  data/raw/tcdb/substrates.tsv  "<TC system>\\t<CHEBI:id;name|…>" (getSubstrates.py)

Family records are grounded with the distinct ChEBI substrate ids of every
transport system under them (aggregated up from the 5-level system rows) —
this both grounds the transport trait and feeds the chemistry/ChEBI work.

Each record: identifier TCDB:<TC>, FUNCTION / FUNC_TRANSPORT, parent chained
class → subclass → family. Idempotent; dry-run unless --apply. Stdlib-only.

NB: TCDB is **CC-BY-SA 3.0** (ShareAlike), stamped per-record — distinct from
the repo's CC0 default.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW = REPO_ROOT / "data" / "raw" / "tcdb"
FAMILIES = RAW / "families.tsv"
SUBSTRATES = RAW / "substrates.tsv"
OUT_DIR = REPO_ROOT / "data" / "traits" / "function" / "transport" / "tcdb"
LICENSE = "CC-BY-SA 3.0"
_SLUG_RE = re.compile(r"[^A-Za-z0-9]+")

# Authoritative TCDB top-level classes (TCDB has no class 7).
CLASS_NAMES = {
    "1": "Channels and Pores",
    "2": "Electrochemical Potential-driven Transporters",
    "3": "Primary Active Transporters",
    "4": "Group Translocators",
    "5": "Transmembrane Electron Carriers",
    "6": "Transport-related Metabolons",
    "8": "Accessory Factors Involved in Transport",
    "9": "Incompletely Characterized Transport Systems",
}


def slugify(t): return (_SLUG_RE.sub("-", t.lower()).strip("-")[:70]) or "tc"


def tc_slug(tc): return tc.replace(".", "-").lower()


def yaml_escape(text: str) -> str:
    if not text:
        return '""'
    unsafe = set(': #{}[],&*!|>%@`\\"\'')
    if (any(c in unsafe for c in text) or text[0] in "-?"
            or text.lower() in {"null", "true", "false", "yes", "no", "on", "off"}):
        return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return text


def folded(text): return [">-", f"  {' '.join((text or '').split())}"]


def load_substrates_by_family() -> dict[str, list[str]]:
    """Map TC family (1.A.1) → sorted distinct CHEBI ids, aggregated from the
    5-level system rows in substrates.tsv."""
    fam: dict[str, set[str]] = {}
    if not SUBSTRATES.exists():
        return {}
    for line in SUBSTRATES.read_text(encoding="utf-8", errors="replace").splitlines():
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        tc, subs = parts[0].strip(), parts[1].strip()
        family = ".".join(tc.split(".")[:3])
        if not family:
            continue
        for chunk in subs.split("|"):
            cid = chunk.split(";")[0].strip()
            if cid.startswith("CHEBI:"):
                fam.setdefault(family, set()).add(cid)
    return {k: sorted(v, key=lambda c: int(c.split(":")[1])) for k, v in fam.items()}


def build_yaml(tc, name, kind, parent, chebi):
    """kind ∈ {class, subclass, family}."""
    if kind == "family":
        definition = (f"{name} — a Transporter Classification family "
                      f"(TC {tc}); proteins in this family mediate membrane "
                      f"transport of their substrate(s).")
    elif kind == "subclass":
        definition = (f"TCDB subclass {tc} — a subclass of transport systems "
                      f"under TC class {tc.split('.')[0]}.")
    else:
        definition = (f"{name} — TCDB transport class {tc}, a top-level "
                      f"category of the Transporter Classification system.")
    lines = [f"identifier: TCDB:{tc}", f"label: {yaml_escape(name)}"]
    f = folded(definition)
    lines += [f"definition: {f[0]}", *f[1:]]
    lines += ["definition_source: TCDB", "trait_axis: FUNCTION",
              "trait_category: FUNC_TRANSPORT", "term_kind: CLASS",
              "mapping_status: SEEDED"]
    if parent:
        lines += ["parent_traits:", f"  - TCDB:{parent}"]
    if chebi:
        lines += ["xrefs:"] + [f"  - {c}" for c in chebi]
    lines.append(f"license: {LICENSE}")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    if not FAMILIES.exists():
        print("missing data/raw/tcdb/families.tsv; run `just fetch-tcdb`",
              file=sys.stderr)
        return 2

    subs_by_family = load_substrates_by_family()

    # Collect the family rows and the set of classes / subclasses they imply.
    families: list[tuple[str, str]] = []
    subclasses: set[str] = set()
    classes: set[str] = set()
    for line in FAMILIES.read_text(encoding="utf-8", errors="replace").splitlines():
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        tc, name = parts[0].strip(), parts[1].strip()
        if not re.match(r"^\d+\.[A-Z]\.\d+$", tc) or not name:
            continue
        families.append((tc, name))
        cls, sub = tc.split(".")[0], ".".join(tc.split(".")[:2])
        classes.add(cls)
        subclasses.add(sub)

    # Emission plan: classes → subclasses → families (parents first is not
    # required for the flat corpus, but keeps the hierarchy coherent).
    records: list[tuple[str, str, str, str, str, list[str]]] = []
    for cls in sorted(classes):
        records.append((cls, CLASS_NAMES.get(cls, f"TC class {cls}"),
                        "class", "", f"tc-class-{cls}", []))
    for sub in sorted(subclasses):
        records.append((sub, f"TC subclass {sub}", "subclass",
                        sub.split(".")[0], f"tc-subclass-{tc_slug(sub)}", []))
    for tc, name in families:
        parent = ".".join(tc.split(".")[:2])
        chebi = subs_by_family.get(tc, [])
        records.append((tc, name, "family", parent,
                        f"{slugify(name)}-{tc_slug(tc)}", chebi))

    written = skipped = 0
    for tc, name, kind, parent, slug, chebi in records:
        path = OUT_DIR / f"{slug}.yaml"
        if path.exists() and not args.force:
            skipped += 1
            continue
        if args.apply:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(build_yaml(tc, name, kind, parent, chebi),
                            encoding="utf-8")
            written += 1

    n_fam = len(families)
    n_grounded = sum(1 for _, _, k, _, _, c in records if k == "family" and c)
    print(f"{len(records)} TCDB records "
          f"({len(classes)} classes, {len(subclasses)} subclasses, "
          f"{n_fam} families; {n_grounded} families ChEBI-grounded).")
    if args.apply:
        print(f"Wrote {written}; skipped {skipped} existing → "
              f"{OUT_DIR.relative_to(REPO_ROOT)}/")
    else:
        print(f"Dry-run — would write {len(records) - skipped}; "
              f"{skipped} exist.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
