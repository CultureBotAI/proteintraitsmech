#!/usr/bin/env python3
"""Seed RiPP leader-peptide traits (SEQUENCE / SEQ_LEADER_PEPTIDE).

Ribosomally synthesized and post-translationally modified peptides (RiPPs) are
made as a precursor whose N-terminal **leader peptide** directs the
post-translational modifications and is then cleaved to release the mature
product. The leader is class-characteristic, so each RiPP class is a
leader-peptide trait. This is a curated controlled vocabulary drawn from the
RiPP consensus nomenclature (Arnison et al. 2013 and updates) as implemented in
antiSMASH / MIBiG / BAGEL4 — a small, stable class set, so hand-curated (like
the stability / evolution taxonomies) rather than fetched.

`mapping_status: SEEDED`; CC0-1.0 (curated). Idempotent; --apply to write.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "data" / "traits" / "sequence" / "leader_peptide"
DEF_SOURCE = "ProteinTraitsMech curated RiPP-class taxonomy (antiSMASH/MIBiG/BAGEL4 nomenclature)"
LICENSE = "CC0-1.0"
_SLUG_RE = re.compile(r"[^A-Za-z0-9]+")

# (class, one-line description, synonyms)
CLASSES = (
    ("lanthipeptide", "lanthionine/methyllanthionine-crosslinked RiPP (lantibiotics); leader guides LanBC/LanM modification then LanP/LanT cleavage.", ("lantibiotic", "class I-IV lanthipeptide")),
    ("lasso peptide", "threaded lariat-knot RiPP; leader recognised by the lasso cyclase/peptidase (B/C proteins).", ("lassopeptide",)),
    ("sactipeptide", "sulfur-to-α-carbon (sactionine) crosslinked RiPP made by a radical-SAM enzyme.", ("sactionine peptide",)),
    ("thiopeptide", "pyridine/azole-containing macrocyclic RiPP (thiazolyl peptide).", ("thiazolyl peptide",)),
    ("linear azol(in)e-containing peptide", "cyclodehydratase-installed azole/azoline RiPP (LAP).", ("LAP", "azoline-containing peptide")),
    ("cyanobactin", "N–C macrocyclic RiPP with heterocycles, from cyanobacteria (PatA/PatG proteases).", ()),
    ("bottromycin", "macrocyclic amidine RiPP with a C-terminal decarboxylated thiazole.", ()),
    ("glycocin", "S-linked glycosylated bacteriocin RiPP.", ("glycopeptide bacteriocin",)),
    ("linaridin", "linear dehydrated RiPP (dehydroamino acids without lanthionine).", ()),
    ("proteusin", "polytheonamide-type RiPP with extensive epimerization/methylation.", ()),
    ("microviridin", "ω-ester/amide crosslinked (graspetide) RiPP protease inhibitor.", ("graspetide", "omega-ester peptide")),
    ("microcin", "small gene-encoded antibacterial RiPP/bacteriocin of Enterobacteria.", ()),
    ("head-to-tail cyclized bacteriocin", "circular bacteriocin with a peptide bond joining N- and C-termini.", ("circular bacteriocin", "class IIc bacteriocin")),
    ("lanthipeptide class I", "LanB dehydratase + LanC cyclase lanthipeptide.", ()),
    ("class II bacteriocin", "unmodified/small-modified heat-stable bacteriocin with a double-glycine leader.", ("double-glycine leader peptide",)),
    ("thioamitide", "thioamide-bearing RiPP (e.g. thioviridamide).", ("thioviridamide-like peptide",)),
    ("ranthipeptide", "radical non-α-thioether-linked RiPP (radical SAM).", ()),
    ("sporulation killing factor", "SkfA-type radical-SAM RiPP.", ("SKF",)),
    ("epipeptide", "D-amino-acid-containing RiPP made by a radical-SAM epimerase.", ()),
    ("spliceotide", "RiPP with a β-amino-acid backbone splice (protease-inhibiting).", ()),
)


def slugify(t): return (_SLUG_RE.sub("-", (t or "").lower()).strip("-")[:70]) or "ripp"


def yaml_escape(text) -> str:
    text = str(text)
    if not text:
        return '""'
    unsafe = set(': #{}[],&*!|>%@`\\"\'')
    if (any(c in unsafe for c in text) or text[:1] in ("-", "?")
            or text.lower() in {"null", "true", "false", "yes", "no", "on", "off"}):
        return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return text


def folded(text):
    text = " ".join((text or "").split())
    return [">-", f"  {text}"] if text else [">-", '  ""']


def build_yaml(cls, desc, syns):
    label = f"{cls} leader peptide"
    definition = (f"Leader peptide of a {cls} precursor — {desc} The N-terminal "
                  f"leader directs post-translational modification and is cleaved "
                  f"to release the mature peptide.")
    lines = [f"identifier: proteintraitsmech:RIPP_LEADER_{slugify(cls).upper().replace('-', '_')}",
             f"label: {yaml_escape(label)}"]
    f = folded(definition)
    lines += [f"definition: {f[0]}", *f[1:]]
    lines += [f"definition_source: {yaml_escape(DEF_SOURCE)}",
              "trait_axis: SEQUENCE", "trait_category: SEQ_LEADER_PEPTIDE",
              "term_kind: CLASS", "mapping_status: SEEDED"]
    if syns:
        lines.append("synonyms:")
        for sname in syns:
            lines.append(f"  - synonym_text: {yaml_escape(sname)}")
            lines.append("    synonym_type: RELATED_SYNONYM")
    lines.append(f"license: {LICENSE}")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    written = skipped = 0
    for cls, desc, syns in CLASSES:
        path = OUT_DIR / f"{slugify(cls)}-leader.yaml"
        if path.exists() and not args.force:
            skipped += 1
            continue
        if args.apply:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(build_yaml(cls, desc, syns), encoding="utf-8")
            written += 1

    print(f"{len(CLASSES)} RiPP leader-peptide classes → SEQ_LEADER_PEPTIDE.")
    if args.apply:
        print(f"Wrote {written}; skipped {skipped} existing → "
              f"{OUT_DIR.relative_to(REPO_ROOT)}/")
    else:
        print(f"Dry-run — would write {len(CLASSES) - skipped}; {skipped} exist.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
