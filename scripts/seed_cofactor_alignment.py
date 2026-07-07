#!/usr/bin/env python3
"""Align the FUNC_COFACTOR_REQUIREMENT set with the cofactor vocabularies of the
sibling projects MicroGrowAgents (growth-media cofactors) and PFASCommunityAgents
(degradation cofactors), all grounded on ChEBI.

seed_chebi_cofactor.py populates ~239 cofactors automatically from ChEBI's
`has_role cofactor` subtree. MicroGrowAgents additionally *curates* ~68 cofactors
— metals (incl. lanthanides for methylotrophy), active vitamin forms (B12, CoQ,
folate), nucleotide/energy cofactors, and methanogenesis cofactors (F420, CoM,
CoB, methanophenazine) — many of which ChEBI does not tag with the cofactor role,
so they are absent from our set. PFAS references a few by name (FAD, NAD,
cobalamin, corrinoid). This script:

  1. Reads the MG cofactor reference tables (sibling repo, read-only) and adds a
     FUNC_COFACTOR_REQUIREMENT record for each curated cofactor we are missing —
     ChEBI-grounded, provenance-tagged as aligned with MicroGrowAgents.
  2. Writes data/mappings/cofactor_crosswalk.tsv: the 3-way shared vocabulary
     (chebi_id · our trait id · cofactor name · MG cofactor_id · MG category ·
     PFAS name), covering the union so all three projects can join on ChEBI.

The MG path defaults to the sibling checkout; override with --mg-root. Gracefully
no-ops the MG-derived additions if that checkout is absent (the crosswalk still
lists our + PFAS entries). License stays CC-BY 4.0 (ChEBI) — we independently
ground to the same ChEBI ids; MG is cited as curation provenance, not relicensed.

Idempotent; dry-run unless --apply. Stdlib-only.
"""

from __future__ import annotations

import argparse
import csv
import glob
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from seed_chebi_cofactor import (  # noqa: E402
    load_names, slug, clean, yaml_escape, folded, rid, LICENSE, OUT_DIR)

REPO_ROOT = Path(__file__).resolve().parent.parent
COFACTOR_ROOT = "23357"
DEFAULT_MG = Path(
    "/Users/marcin/Documents/VIMSS/ontology/KG-Hub/KG-Microbe/MicroGrowAgents/"
    "MicroGrowAgents")
CROSSWALK = REPO_ROOT / "data" / "mappings" / "cofactor_crosswalk.tsv"

# PFAS (PFASCommunityAgents) references cofactors by name only — pin the obvious
# ChEBI groundings so the crosswalk carries the PFAS column.
PFAS_NAME_CHEBI = {
    "CHEBI:16238": "FAD", "CHEBI:15846": "NAD", "CHEBI:16335": "cobalamin",
    "CHEBI:33913": "corrinoid",
}


def load_mg_cofactors(mg_root: Path) -> dict[str, dict]:
    """chebi_id → {name, category, cofactor_id} from MG's reference TSVs."""
    meta: dict[str, dict] = {}
    refs = sorted(glob.glob(str(mg_root / "data/references/cofactors_complete*.tsv")))
    refs += sorted(glob.glob(str(mg_root / "data/references/cofactors_metals*.tsv")))
    for tsv in refs:
        try:
            with open(tsv, encoding="utf-8") as fh:
                for r in csv.DictReader(fh, delimiter="\t"):
                    cid = (r.get("chebi_id") or "").strip()
                    if not cid.startswith("CHEBI:"):
                        continue
                    m = meta.setdefault(cid, {})
                    for src, dst in [("chemical_name", "name"), ("category", "category"),
                                     ("cofactor_id", "cofactor_id")]:
                        v = (r.get(src) or "").strip()
                        if v and not m.get(dst):
                            m[dst] = v
        except FileNotFoundError:
            continue
    return meta


def our_chebi_ids() -> dict[str, str]:
    """chebi_id → our existing trait identifier."""
    out = {}
    for p in OUT_DIR.glob("*.yaml"):
        t = p.read_text(encoding="utf-8")
        i = re.search(r"(?m)^identifier:\s*(\S+)", t)
        x = re.search(r"(?m)^\s*-\s*(CHEBI:\d+)", t)
        if i and x:
            out[x.group(1)] = i.group(1)
    return out


def build_aligned(chid, name, defn, mg):
    """A FUNC_COFACTOR_REQUIREMENT record for an MG-curated cofactor we lack."""
    lines = [f"identifier: {rid(chid)}", f"label: {yaml_escape('requires ' + name)}"]
    cat = mg.get("category", "").replace("_", " ")
    d = (f"The functional requirement for {name} (CHEBI:{chid}) as a cofactor"
         + (f" ({cat})" if cat else "") + ".")
    extra = defn.get(chid, "")
    if extra:
        d = f"{d} {extra}"
    f = folded(d)
    lines += [f"definition: {f[0]}", *f[1:]]
    lines += ["definition_source: ChEBI (cofactor curated by MicroGrowAgents)",
              "trait_axis: FUNCTION",
              "trait_category: FUNC_COFACTOR_REQUIREMENT", "term_kind: CLASS",
              "mapping_status: SEEDED",
              "parent_traits:", f"  - {rid(COFACTOR_ROOT)}"]
    syns = [s for s in (mg.get("cofactor_id"), mg.get("category")) if s]
    if syns:
        lines.append("synonyms:")
        for s in dict.fromkeys(syns):
            lines += [f"  - synonym_text: {yaml_escape(s)}",
                      "    synonym_type: RELATED_SYNONYM", "    source: MicroGrowAgents"]
    lines += ["xrefs:", f"  - CHEBI:{chid}"]
    lines.append(f"license: {LICENSE}")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--mg-root", default=str(DEFAULT_MG))
    args = ap.parse_args()

    name, defn = load_names()
    ours = our_chebi_ids()
    mg = load_mg_cofactors(Path(args.mg_root))
    if not mg:
        print(f"warning: no MG cofactor tables under {args.mg_root} — "
              f"crosswalk will cover only our + PFAS entries", file=sys.stderr)

    missing = [c for c in mg if c not in ours]
    written = skipped = 0
    for chid in sorted(missing, key=lambda c: int(c.split(":")[1])):
        nm = mg[chid].get("name") or name.get(chid.split(":")[1]) or chid
        path = OUT_DIR / f"{slug(nm)}-chebi{chid.split(':')[1]}.yaml"
        our_id = rid(chid.split(":")[1])
        ours[chid] = our_id            # so the crosswalk sees it
        if path.exists() and not args.force:
            skipped += 1
        elif args.apply:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                build_aligned(chid.split(":")[1], nm, defn, mg[chid]), encoding="utf-8")
            written += 1

    # 3-way crosswalk over the union of all chebi ids seen anywhere
    all_ids = sorted(set(ours) | set(mg) | set(PFAS_NAME_CHEBI),
                     key=lambda c: int(c.split(":")[1]))
    rows = [["chebi_id", "proteintraitsmech_trait", "cofactor_name",
             "microgrowagents_cofactor_id", "microgrowagents_category",
             "pfas_name"]]
    for c in all_ids:
        loc = c.split(":")[1]
        nm = (mg.get(c, {}).get("name") or name.get(loc) or "")
        rows.append([c, ours.get(c, ""), clean(nm),
                     mg.get(c, {}).get("cofactor_id", ""),
                     mg.get(c, {}).get("category", ""),
                     PFAS_NAME_CHEBI.get(c, "")])
    if args.apply:
        CROSSWALK.parent.mkdir(parents=True, exist_ok=True)
        with CROSSWALK.open("w", encoding="utf-8", newline="") as fh:
            csv.writer(fh, delimiter="\t").writerows(rows)

    shared_all3 = sum(1 for c in all_ids
                      if ours.get(c) and c in mg and c in PFAS_NAME_CHEBI)
    print(f"Cofactor alignment: MG={len(mg)} curated, ours(before)={len(ours)-len(missing)}, "
          f"MG-missing-from-ours={len(missing)} → {'added' if args.apply else 'would add'} "
          f"{written if args.apply else len(missing)-skipped}; skipped {skipped}.")
    print(f"Crosswalk: {len(all_ids)} ChEBI cofactors across the union "
          f"({'wrote ' + str(CROSSWALK.relative_to(REPO_ROOT)) if args.apply else 'dry-run'}); "
          f"PFAS-named={len(PFAS_NAME_CHEBI)}.")
    if not args.apply:
        print("Dry-run — re-run with --apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
