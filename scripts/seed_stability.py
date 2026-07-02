#!/usr/bin/env python3
"""Seed condition-specific structural-stability traits (STRUCT_STABILITY).

The catalog's STRUCTURE axis had only the three generic PATO stability terms
(`stability`, `increased stability`, `decreased stability`). Protein structural
stability is, however, almost always *stability under a specific stressor* —
thermal, oxidative, saline, acidic/alkaline, osmotic, high-pressure,
desiccation, chemical-denaturant, proteolytic, mechanical — and each of those is
a real, curatable trait with increased / decreased variants (the province of
extremophile biochemistry: thermostable, halostable, piezostable enzymes, etc.).

This generator emits, for every condition in CONDITIONS, three records:

  <cond> stability                → parent PATO:0015026 (stability)
  increased <cond> stability      → parents [<cond> stability, PATO:0015027]
  decreased <cond> stability      → parents [<cond> stability, PATO:0015028]

all as `trait_axis: STRUCTURE`, `trait_category: STRUCT_STABILITY`, curator-
minted `proteintraitsmech:STABILITY_<COND>[ _INCREASED | _DECREASED ]`
identifiers, under `data/traits/structure/stability/conditions/`.

Groundings are intentionally conservative: records parent to the verified PATO
stability terms and carry well-established synonyms, but do NOT assert specific
GO/ChEBI condition CURIEs (those can be added by `just ground-categories` or a
curator so we don't bake in unverified ids). `mapping_status: SEEDED`.

Idempotent (skips existing files); dry-run unless --apply. Stdlib-only.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "data" / "traits" / "structure" / "stability" / "conditions"

DEFINITION_SOURCE = "ProteinTraitsMech curated structural-stability taxonomy"
LICENSE = "CC0-1.0"

PATO_STABILITY = "PATO:0015026"
PATO_INCREASED = "PATO:0015027"
PATO_DECREASED = "PATO:0015028"

# (key, adjective for the file slug, condition phrase for the definition,
#  condition label for the "stable under <…>" trait name, [synonyms]).
# Labels read "stable under <condition label>"; the old "<adj> stability"
# form is preserved as a synonym. Extend this list to add conditions.
CONDITIONS: tuple[tuple[str, str, str, str, tuple[str, ...]], ...] = (
    ("THERMAL", "thermal",
     "elevated or reduced temperature (heat or cold)", "thermal conditions",
     ("thermostability", "heat stability", "thermal resistance", "thermotolerance")),
    ("OXIDATIVE", "oxidative",
     "oxidative conditions or reactive oxygen species", "oxidative conditions",
     ("oxidation stability", "redox stability", "resistance to oxidation")),
    ("SALINE", "saline",
     "high ionic strength / elevated salt concentration", "saline (high-salt) conditions",
     ("halostability", "salt stability", "salt resistance", "haloadaptation")),
    ("ACIDIC", "acid",
     "low pH (acidic conditions)", "acidic conditions",
     ("acid stability", "acidostability", "acid resistance")),
    ("ALKALINE", "alkaline",
     "high pH (alkaline conditions)", "alkaline conditions",
     ("alkaline stability", "base stability", "alkali resistance")),
    ("OSMOTIC", "osmotic",
     "osmotic stress", "osmotic stress",
     ("osmostability", "osmotic resistance")),
    ("PRESSURE", "high-pressure",
     "elevated hydrostatic pressure", "high hydrostatic pressure",
     ("barostability", "piezostability", "pressure stability", "pressure resistance")),
    ("DESICCATION", "desiccation",
     "desiccation / dehydration (water loss)", "desiccating conditions",
     ("xerostability", "dehydration stability", "desiccation resistance", "anhydrobiotic stability")),
    ("CHEMICAL", "chemical-denaturant",
     "chemical denaturants such as urea, guanidinium chloride, or detergents", "chemical-denaturant conditions",
     ("denaturant stability", "chemical resistance", "resistance to chemical denaturation")),
    ("PROTEOLYTIC", "proteolytic",
     "proteolytic degradation by peptidases", "proteolytic conditions",
     ("protease resistance", "proteolytic stability", "resistance to proteolysis")),
    ("MECHANICAL", "mechanical",
     "mechanical force / applied load (mechanical unfolding)", "mechanical stress",
     ("mechanostability", "mechanical stability", "force resistance")),
)


def yaml_escape(text: str) -> str:
    if not text:
        return '""'
    unsafe = set(': #{}[],&*!|>%@`\\"\'')
    if (any(c in unsafe for c in text) or text[0] in "-?"
            or text.lower() in {"null", "true", "false", "yes", "no", "on", "off"}):
        return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return text


def folded(text: str) -> list[str]:
    text = " ".join(text.split())
    return [">-", f"  {text}"]


def record(identifier: str, label: str, definition: str,
           parents: list[str], synonyms: tuple[str, ...]) -> str:
    lines: list[str] = []
    lines.append(f"identifier: {identifier}")
    lines.append(f"label: {yaml_escape(label)}")
    f = folded(definition)
    lines.append(f"definition: {f[0]}")
    lines.extend(f[1:])
    lines.append(f"definition_source: {yaml_escape(DEFINITION_SOURCE)}")
    lines.append("trait_axis: STRUCTURE")
    lines.append("trait_category: STRUCT_STABILITY")
    lines.append("term_kind: CLASS")
    lines.append("mapping_status: SEEDED")
    if parents:
        lines.append("parent_traits:")
        lines.extend(f"  - {p}" for p in parents)
    seen: set[str] = set()
    uniq = [s for s in synonyms if s != label and not (s in seen or seen.add(s))]
    if uniq:
        lines.append("synonyms:")
        for s in uniq:
            lines.append(f"  - synonym_text: {yaml_escape(s)}")
            lines.append("    synonym_type: EXACT_SYNONYM")
    lines.append(f"license: {LICENSE}")
    return "\n".join(lines) + "\n"


def build_records() -> list[tuple[str, str]]:
    """Return [(filename, yaml_text), …] for every condition × direction."""
    out: list[tuple[str, str]] = []
    for key, adj, phrase, clabel, syns in CONDITIONS:
        base_id = f"proteintraitsmech:STABILITY_{key}"
        # "stable under <clabel>"; keep the old "<adj> stability" as a synonym.
        base_syns = (f"{adj} stability",) + syns
        base_def = (f"Structural stability of a protein under {phrase} — the "
                    f"capacity to retain its folded, functional conformation "
                    f"when exposed to this condition.")
        out.append((f"{adj}-stability.yaml",
                    record(base_id, f"stable under {clabel}", base_def,
                           [PATO_STABILITY], base_syns)))

        inc_syns = (f"increased {adj} stability",) + tuple(f"increased {s}" for s in syns[:2])
        out.append((f"increased-{adj}-stability.yaml",
                    record(f"{base_id}_INCREASED",
                           f"increased stability under {clabel}",
                           f"Greater-than-reference structural stability under "
                           f"{phrase} (e.g. an extremophile or engineered "
                           f"variant that resists this stressor better than its "
                           f"mesophilic or wild-type counterpart).",
                           [base_id, PATO_INCREASED], inc_syns)))

        dec_syns = (f"decreased {adj} stability",) + tuple(f"decreased {s}" for s in syns[:2])
        out.append((f"decreased-{adj}-stability.yaml",
                    record(f"{base_id}_DECREASED",
                           f"decreased stability under {clabel}",
                           f"Lower-than-reference structural stability under "
                           f"{phrase} (e.g. a destabilising mutation or a "
                           f"condition-sensitive variant that unfolds or is "
                           f"degraded more readily under this stressor).",
                           [base_id, PATO_DECREASED], dec_syns)))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true", help="write YAMLs (default: dry-run)")
    ap.add_argument("--force", action="store_true", help="overwrite existing files")
    args = ap.parse_args()

    recs = build_records()
    written = skipped = 0
    for fname, text in recs:
        path = OUT_DIR / fname
        if path.exists() and not args.force:
            skipped += 1
            continue
        if args.apply:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
            written += 1

    print(f"{len(CONDITIONS)} conditions × 3 = {len(recs)} STRUCT_STABILITY records.")
    if args.apply:
        print(f"Wrote {written}; skipped {skipped} existing → "
              f"{OUT_DIR.relative_to(REPO_ROOT)}/")
    else:
        print(f"Dry-run — would write {len(recs) - skipped}; "
              f"{skipped} already exist. Re-run with --apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
