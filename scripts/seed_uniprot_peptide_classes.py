#!/usr/bin/env python3
"""Seed UniProt peptide/processing feature-type **classes** (pivot model)
→ SEQUENCE axis.

UniProt annotates peptide/processing features per protein (SIGNAL, TRANSIT,
PROPEP, PEPTIDE, INIT_MET). Per the pivot rule those are instance-level, so we
seed ONE class per feature type (the reusable trait) and attach reviewed
proteins carrying that feature as `canonical_examples`, each with the feature
region marked up.

Queries the UniProtKB REST API (reviewed entries) — a handful of requests.
`--apply` to write; needs network on first run. Stdlib-only.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from record_io import write_record  # noqa: E402
from yaml_emit import folded, yaml_escape  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "data" / "traits" / "sequence"
SEARCH = "https://rest.uniprot.org/uniprotkb/search"
LICENSE = "CC-BY 4.0"
CAP = 15

# feature: (ft_query, uniprot_feature_type, category, subdir, label, definition)
FEATURES = [
    ("ft_signal", "Signal", "SEQ_SIGNAL_PEPTIDE", "signal_peptide", "signal peptide",
     "An N-terminal secretory signal peptide (typically 15-30 residues with a "
     "positively charged n-region, a hydrophobic h-region, and a polar c-region "
     "carrying a small neutral residue at -3/-1) that targets nascent polypeptides "
     "to the Sec or Tat translocation machinery and is cleaved by signal peptidase "
     "during or immediately after membrane translocation."),
    ("ft_transit", "Transit peptide", "SEQ_TRANSIT_PEPTIDE", "transit_peptide", "transit peptide",
     "An N-terminal organelle-targeting transit peptide (mitochondrial matrix "
     "presequence, chloroplast stromal/thylakoid transit peptide, hydrogenosomal/"
     "mitosomal presequence, or apicoplast bipartite leader) that directs "
     "post-translational import into a membrane-bounded organelle and is "
     "proteolytically cleaved after translocation."),
    ("ft_propep", "Propeptide", "SEQ_PROPEPTIDE", "propeptide", "propeptide",
     "A transient propeptide / pro-region (N-terminal, C-terminal, or internal) "
     "that suppresses premature enzymatic or hormonal activity, assists folding as "
     "an intramolecular chaperone, or provides an enzyme-docking exosite, and is "
     "proteolytically removed during proprotein maturation or zymogen activation."),
    ("ft_peptide", "Peptide", "SEQ_MATURE_CHAIN", "mature_chain", "released active peptide",
     "A released, biologically active polypeptide chain or mature peptide hormone, "
     "neuropeptide, or antimicrobial peptide excised from a larger precursor "
     "polyprotein by site-specific endopeptidase and exopeptidase processing."),
    ("ft_init_met", "Initiator methionine", "SEQ_INITIATOR_METHIONINE", "initiator_methionine",
     "cleaved initiator methionine",
     "The N-terminal translation-initiating methionine residue (Met1) that is "
     "co-translationally or post-translationally excised by methionine "
     "aminopeptidase (MetAP) when the penultimate residue (P1') has a small "
     "side-chain radius of gyration."),
]


def uniprot_search(ft_query: str):
    q = f"({ft_query}:*) AND (reviewed:true)"
    params = {"query": q, "format": "json", "size": str(CAP),
              "fields": "accession,protein_name,organism_name,length,ft_" + ft_query.split("_", 1)[1]}
    url = f"{SEARCH}?{urllib.parse.urlencode(params)}"
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8")).get("results", [])
        except Exception as exc:  # noqa: BLE001
            if attempt < 3:
                time.sleep(2 ** attempt)
                continue
            print(f"  WARN {ft_query}: {exc}", file=sys.stderr)
            return []


def examples_from(results, ft_type):
    out = []
    for e in results:
        acc = e.get("primaryAccession")
        if not acc:
            continue
        pd = e.get("proteinDescription") or {}
        name = ((pd.get("recommendedName") or {}).get("fullName") or {}).get("value") or acc
        org = (e.get("organism") or {}).get("scientificName") or ""
        feats = []
        for ft in e.get("features") or []:
            if ft.get("type") != ft_type:
                continue
            loc = ft.get("location") or {}
            s = (loc.get("start") or {}).get("value")
            en = (loc.get("end") or {}).get("value")
            if s and en:
                feats.append((int(s), int(en)))
        if feats:
            out.append({"acc": acc, "name": name, "org": org, "feats": feats})
    return out


def build_yaml(ft_type, category, label, definition, examples):
    lines = [f"identifier: proteintraitsmech:UNIPROT_FT_{category}",
             f"label: {yaml_escape(label)}"]
    f = folded(definition)
    lines += [f"definition: {f[0]}", *f[1:]]
    lines += ["definition_source: UniProtKB feature type",
              "trait_axis: SEQUENCE", f"trait_category: {category}",
              "term_kind: CLASS", "mapping_status: SEEDED"]
    if examples:
        lines.append("canonical_examples:")
        for ex in examples:
            lines.append(f"  - protein_id: UniProtKB:{ex['acc']}")
            lines.append(f"    protein_label: {yaml_escape(ex['name'])}")
            if ex.get("org"):
                lines.append(f"    taxon_label: {yaml_escape(ex['org'])}")
            lines.append(f"    note: {yaml_escape('UniProt ' + ft_type + ' feature')}")
            lines.append("    source: CURATOR")
            lines.append("    features:")
            for s, e in ex["feats"]:
                lines.append(f"      - start: {s}")
                lines.append(f"        end: {e}")
                lines.append(f"        feature_type: {ft_type.upper().replace(' ', '_')}")
                lines.append("        trait_axis: SEQUENCE")
                lines.append(f"        trait_category: {category}")
    lines.append(f"license: {LICENSE}")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    written = skipped = 0
    for ft_query, ft_type, category, subdir, label, definition in FEATURES:
        path = OUT_DIR / subdir / f"uniprot-{category.lower()}.yaml"
        if path.exists() and not args.force:
            skipped += 1
            continue
        examples = examples_from(uniprot_search(ft_query), ft_type) if args.apply else []
        text = build_yaml(ft_type, category, label, definition, examples)
        print(f"  {category}: {len(examples)} example proteins")
        if args.apply:
            path.parent.mkdir(parents=True, exist_ok=True)
            write_record(path, text)
            written += 1

    print(f"{len(FEATURES)} UniProt peptide feature-type classes → SEQUENCE.")
    if args.apply:
        print(f"Wrote {written}; skipped {skipped} existing.")
    else:
        print(f"Dry-run — {len(FEATURES) - skipped} to write; {skipped} exist. Use --apply (network).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
