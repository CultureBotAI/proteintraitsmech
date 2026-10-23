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

MECHANISM_BLOCKS = {
    "SEQ_SIGNAL_PEPTIDE": """causal_graphs:
- graph_id: CG_UNIPROT_FT_SEQ_SIGNAL_PEPTIDE
  title: N-terminal signal peptide directs Sec/Tat membrane translocation and signal peptidase cleavage
    for secretion
  description: An N-terminal secretory signal peptide (SO:0000418) directs nascent preproteins to the
    Sec translocon for membrane translocation (GO:0043952), which is causally upstream of signal peptidase
    endopeptidase cleavage (GO:0004175) that releases the mature polypeptide for protein secretion (GO:0009306).
  nodes:
  - node_id: SO:0000418
    label: signal_peptide
    node_type: MOTIF
    grounding: SO:0000418
    description: Cleavable N-terminal tripartite secretory signal peptide (n-, h-, and c-regions)
  - node_id: GO:0043952
    label: protein transport by the Sec complex
    node_type: BIOLOGICAL_PROCESS
    grounding: GO:0043952
    description: Co-translational or post-translational polypeptide translocation across the ER or prokaryotic
      cytoplasmic membrane
  - node_id: GO:0004175
    label: endopeptidase activity
    node_type: MOLECULAR_FUNCTION
    grounding: GO:0004175
    description: Signal peptidase (SPase I / SPase II / SPase IV) endopeptidase activity cleaving the
      c-region (-3, -1) recognition motif
  - node_id: GO:0009306
    label: protein secretion
    node_type: BIOLOGICAL_PROCESS
    grounding: GO:0009306
    description: Export of the cleaved mature protein into the secretory lumen, periplasm, or extracellular
      milieu
  edges:
  - subject: SO:0000418
    predicate: positively regulates
    predicate_id: RO:0002213
    object: GO:0043952
    description: N-terminal signal peptides govern protein targeting and translocation across the Sec
      (or Tat) membrane machinery.
    evidence:
    - reference: PMID:34980915
      snippet: Signal peptides (SPs) are short amino acid sequences that control protein secretion and
        translocation in all living organisms.
      notes: Signal peptides direct protein translocation across membranes (PMID:34980915) (ECO:0000305)
  - subject: GO:0043952
    predicate: causally upstream of
    predicate_id: RO:0002411
    object: GO:0004175
    description: Translocation exposes the signal peptide cleavage site at the trans side of the membrane
      for cleavage by signal peptidase I, II, or IV.
    evidence:
    - reference: PMID:34980915
      snippet: SignalP 6.0 is based on protein language models (LMs) that use information from millions
        of unannotated protein sequences across all domains of life to predict all five SP types and their
        cleavage sites.
      notes: Translocated signal peptides are cleaved at their signal peptidase cleavage sites (PMID:34980915)
        (ECO:0000305)
  - subject: GO:0004175
    predicate: positively regulates
    predicate_id: RO:0002213
    object: GO:0009306
    description: Signal peptidase cleavage excises the membrane-tethered leader peptide to complete protein
      secretion.
    evidence:
    - reference: PMID:34980915
      snippet: Signal peptides (SPs) are short amino acid sequences that control protein secretion and
        translocation in all living organisms.
      notes: Signal peptide cleavage releases the secreted protein (PMID:34980915) (ECO:0000305)
evidence:
- reference: PMID:34980915
  notes: Teufel et al. (2022) characterize the five major classes of secretory signal peptides (Sec/SPase
    I, Sec/SPase II, Sec/SPase IV, Tat/SPase I, and Tat/SPase II) and their translocation and cleavage
    mechanisms.""",
    "SEQ_TRANSIT_PEPTIDE": """causal_graphs:
- graph_id: CG_UNIPROT_FT_SEQ_TRANSIT_PEPTIDE
  title: N-terminal transit peptide directs organellar translocon import and processing-peptidase maturation
  description: An N-terminal organelle transit peptide (SO:0000725) interacts with outer- and inner-membrane
    translocons to drive organellar protein import such as chloroplast stroma import (GO:0045037), followed
    by processing endopeptidase cleavage (GO:0004175) that releases the mature protein in the target organellar
    compartment (GO:0009570).
  nodes:
  - node_id: SO:0000725
    label: transit_peptide
    node_type: MOTIF
    grounding: SO:0000725
    description: Cleavable N-terminal organellar targeting presequence (chloroplast cTP or mitochondrial
      MTS)
  - node_id: GO:0045037
    label: protein import into chloroplast stroma
    node_type: BIOLOGICAL_PROCESS
    grounding: GO:0045037
    description: Post-translational translocation of transit-peptide-bearing precursor proteins across
      the TOC-TIC envelope translocons
  - node_id: GO:0004175
    label: endopeptidase activity
    node_type: MOLECULAR_FUNCTION
    grounding: GO:0004175
    description: Stromal processing peptidase (SPP) or mitochondrial processing peptidase (MPP) activity
      excising the N-terminal transit peptide
  - node_id: GO:0009570
    label: chloroplast stroma
    node_type: CELLULAR_LOCALIZATION
    grounding: GO:0009570
    description: Target organellar lumen where the cleaved mature protein folds and functions
  edges:
  - subject: SO:0000725
    predicate: positively regulates
    predicate_id: RO:0002213
    object: GO:0045037
    description: The N-terminal chloroplast transit peptide is necessary and sufficient to direct precursor
      protein import across the plastid envelope.
    evidence:
    - reference: PMID:37324391
      snippet: Import of most plastid proteins is mediated by a sequence-diverse N-terminal targeting
        signal, the chloroplast transit peptide (cTP).
      notes: N-terminal transit peptide mediates plastid protein import (PMID:37324391) (ECO:0000269)
  - subject: GO:0045037
    predicate: causally upstream of
    predicate_id: RO:0002411
    object: GO:0004175
    description: Translocation of the N-terminal transit peptide into the stroma exposes its cleavage
      site to stromal processing peptidase.
    evidence:
    - reference: PMID:37324391
      snippet: Import of most plastid proteins is mediated by a sequence-diverse N-terminal targeting
        signal, the chloroplast transit peptide (cTP).
      notes: Imported transit peptides are proteolytically cleaved upon reaching the stroma (PMID:37324391)
        (ECO:0000269)
  - subject: GO:0004175
    predicate: has target end location
    predicate_id: RO:0002339
    object: GO:0009570
    description: Processing peptidase cleavage releases the mature imported polypeptide in the chloroplast
      stroma.
    evidence:
    - reference: PMID:37324391
      snippet: Import of most plastid proteins is mediated by a sequence-diverse N-terminal targeting
        signal, the chloroplast transit peptide (cTP).
      notes: Transit-peptide-mediated import delivers mature proteins to the chloroplast stroma (PMID:37324391)
        (ECO:0000269)
evidence:
- reference: PMID:37324391
  notes: Chloroplast transit peptides (cTPs) mediate post-translational import of plastid precursor proteins
    through the TOC-TIC translocons and are cleaved in the stroma by stromal processing peptidase.""",
    "SEQ_PROPEPTIDE": """causal_graphs:
- graph_id: CG_UNIPROT_FT_SEQ_PROPEPTIDE
  title: Intramolecular chaperone folding and proteolytic propeptide removal drive zymogen activation
  description: A transient propeptide (SO:0001062) acts as an intramolecular chaperone that positively
    regulates zymogen protein folding (GO:0006457) while maintaining latency until endopeptidase cleavage
    (GO:0004175) excises the pro-region to trigger zymogen activation (GO:0031638).
  nodes:
  - node_id: SO:0001062
    label: propeptide
    node_type: MOTIF
    grounding: SO:0001062
    description: Cleavable pro-region that assists precursor folding and suppresses premature catalytic
      activity
  - node_id: GO:0006457
    label: protein folding
    node_type: BIOLOGICAL_PROCESS
    grounding: GO:0006457
    description: Intramolecular chaperone-assisted folding of the zymogen or proprotein into its native
      conformation
  - node_id: GO:0004175
    label: endopeptidase activity
    node_type: MOLECULAR_FUNCTION
    grounding: GO:0004175
    description: Autocatalytic or trans-acting processing endopeptidase activity cleaving the propeptide
      boundary
  - node_id: GO:0031638
    label: zymogen activation
    node_type: BIOLOGICAL_PROCESS
    grounding: GO:0031638
    description: Proteolytic removal of the inhibitory propeptide to unmask the active mature enzyme or
      protein
  edges:
  - subject: SO:0001062
    predicate: positively regulates
    predicate_id: RO:0002213
    object: GO:0006457
    description: The propeptide functions as an intramolecular chaperone that assists correct folding
      of the zymogen during biosynthesis.
    evidence:
    - reference: PMID:38421254
      snippet: The preparation of active recombinant MTG requires post-translational proteolytic digestion
        of a propeptide that functions as an intramolecular chaperone to assist the correct folding of
        the MTG zymogen (MTGz) in the biosynthesis.
      notes: Propeptide acts as an intramolecular chaperone for zymogen folding (PMID:38421254) (ECO:0000269)
  - subject: GO:0006457
    predicate: causally upstream of
    predicate_id: RO:0002411
    object: GO:0004175
    description: Proper folding of the propeptide-bearing zymogen positions the propeptide cleavage site
      for post-translational endopeptidase digestion.
    evidence:
    - reference: PMID:38421254
      snippet: The preparation of active recombinant MTG requires post-translational proteolytic digestion
        of a propeptide that functions as an intramolecular chaperone to assist the correct folding of
        the MTG zymogen (MTGz) in the biosynthesis.
      notes: Folded zymogen undergoes proteolytic digestion of the propeptide (PMID:38421254) (ECO:0000269)
  - subject: GO:0004175
    predicate: positively regulates
    predicate_id: RO:0002213
    object: GO:0031638
    description: Proteolytic cleavage and removal of the propeptide converts the inactive zymogen into
      the active mature enzyme.
    evidence:
    - reference: PMID:31557781
      snippet: CatC is first synthetized as an inactive zymogen containing an intramolecular chain propeptide,
        the dimeric form of which is processed into the mature tetrameric form by proteolytic cleavages.
      notes: Proteolytic cleavage of the propeptide activates the zymogen (PMID:31557781) (ECO:0000269)
evidence:
- reference: PMID:38421254
  notes: Propeptides act as intramolecular chaperones that assist correct zymogen folding prior to post-translational
    proteolytic removal.
- reference: PMID:31557781
  notes: Inactive zymogens containing an propeptide are converted into mature active enzymes by proteolytic
    excision of the propeptide.""",
    "SEQ_MATURE_CHAIN": """causal_graphs:
- graph_id: CG_UNIPROT_FT_SEQ_MATURE_CHAIN
  title: Proprotein convertase cleavage excises mature bioactive polypeptide chains from precursors
  description: Proprotein convertase endopeptidase activity (GO:0004175) positively regulates proteolytic
    protein processing (GO:0016485) of precursor polyproteins, releasing a defined mature protein/peptide
    region (SO:0000419) that completes functional protein maturation (GO:0051604).
  nodes:
  - node_id: GO:0004175
    label: endopeptidase activity
    node_type: MOLECULAR_FUNCTION
    grounding: GO:0004175
    description: Subtilisin/kexin-like proprotein convertase or processing endopeptidase cleaving precursor
      proteins at specific recognition sites
  - node_id: GO:0016485
    label: protein processing
    node_type: BIOLOGICAL_PROCESS
    grounding: GO:0016485
    description: Site-specific proteolytic cleavage of precursor polyproteins or prohormones in the secretory
      pathway
  - node_id: SO:0000419
    label: mature_protein_region
    node_type: DOMAIN
    grounding: SO:0000419
    description: Excised, biologically active mature polypeptide chain or peptide hormone
  - node_id: GO:0051604
    label: protein maturation
    node_type: BIOLOGICAL_PROCESS
    grounding: GO:0051604
    description: Generation of the active mature peptide or protein product from an inactive precursor
  edges:
  - subject: GO:0004175
    predicate: positively regulates
    predicate_id: RO:0002213
    object: GO:0016485
    description: Proprotein convertases catalyze site-specific endoproteolytic processing of secretory
      precursor proteins.
    evidence:
    - reference: PMID:18184105
      snippet: The proprotein convertases (PCs) are a family of nine secretory serine proteases related
        to bacterial subtilisin and yeast kexin.
      notes: Proprotein convertases are secretory serine endopeptidases that process precursors (PMID:18184105)
        (ECO:0000305)
  - subject: GO:0016485
    predicate: has output
    predicate_id: RO:0002234
    object: SO:0000419
    description: Proteolytic processing at basic or non-basic cleavage sites releases the mature polypeptide
      chain or bioactive peptide.
    evidence:
    - reference: PMID:18184105
      snippet: Seven of them (PC1/3, PC2, furin, PC4, PC5/6, PACE4, and PC7) cleave secretory precursors
        at specific single or paired basic amino acids, whereas SKI-1/S1P and PCSK9 cleave at nonbasic
        residues or self-cleave, respectively.
      notes: Cleavage at defined recognition sites excises mature chains and peptides (PMID:18184105)
        (ECO:0000305)
  - subject: SO:0000419
    predicate: involved in
    predicate_id: RO:0002331
    object: GO:0051604
    description: Release of the excised mature region completes post-translational maturation of hormones,
      neuropeptides, and secreted proteins.
    evidence:
    - reference: PMID:18184105
      snippet: Seven of them (PC1/3, PC2, furin, PC4, PC5/6, PACE4, and PC7) cleave secretory precursors
        at specific single or paired basic amino acids, whereas SKI-1/S1P and PCSK9 cleave at nonbasic
        residues or self-cleave, respectively.
      notes: Excised mature chains represent the processed products of proprotein maturation (PMID:18184105)
        (ECO:0000305)
evidence:
- reference: PMID:18184105
  notes: Seidah et al. (2008) review the proprotein convertase family of serine endopeptidases that cleave
    precursor proteins at dibasic or monobasic sites to release mature bioactive peptides and hormones.""",
    "SEQ_INITIATOR_METHIONINE": """causal_graphs:
- graph_id: CG_UNIPROT_FT_SEQ_INITIATOR_METHIONINE
  title: Co-translational initiator methionine incorporation and excision by methionine aminopeptidase
  description: Translational initiation (GO:0006413) incorporates an N-terminal L-methionine residue (CHEBI:16811)
    at position 1 of the nascent chain, which is recognized and hydrolyzed by initiator methionyl aminopeptidase
    activity (GO:0004239) during N-terminal protein processing (GO:0016485).
  nodes:
  - node_id: GO:0006413
    label: translational initiation
    node_type: BIOLOGICAL_PROCESS
    grounding: GO:0006413
    description: Ribosomal initiation of polypeptide synthesis at the start codon with an N-terminal initiator
      methionine
  - node_id: CHEBI:16811
    label: L-methionine
    node_type: RESIDUE
    grounding: CHEBI:16811
    description: Cleavable N-terminal initiator methionine residue at position 1 of the nascent polypeptide
  - node_id: GO:0004239
    label: initiator methionyl aminopeptidase activity
    node_type: MOLECULAR_FUNCTION
    grounding: GO:0004239
    description: Ribosome-associated methionine aminopeptidase (MetAP) activity hydrolyzing the Met1-Xaa2
      peptide bond
  - node_id: GO:0016485
    label: protein processing
    node_type: BIOLOGICAL_PROCESS
    grounding: GO:0016485
    description: Co-translational proteolytic removal of the N-terminal initiator methionine to unmask
      the mature N-terminus
  edges:
  - subject: GO:0006413
    predicate: positively regulates
    predicate_id: RO:0002213
    object: CHEBI:16811
    description: Ribosomal translational initiation installs L-methionine at the N-terminus of newly synthesized
      cytosolic proteins.
    evidence:
    - reference: PMID:2682640
      snippet: The side-chain length of the penultimate amino acid strongly influences the cleavage of
        the terminal methionine residue in vivo (the probability of cleavage decreases as the size of
        the side chain increases).
      notes: Nascent polypeptides carry an N-terminal initiator methionine subject to in vivo cleavage
        (PMID:2682640) (ECO:0000269)
  - subject: CHEBI:16811
    predicate: participates in
    predicate_id: RO:0000056
    object: GO:0004239
    description: An N-terminal initiator methionine followed by a small penultimate residue participates in
      MetAP substrate recognition and hydrolysis.
    evidence:
    - reference: PMID:2682640
      snippet: We have studied the cleavage of the NH2-terminal methionine residue from 20 mutants of
        Escherichia coli methionyl-tRNA synthetase differing only at the second amino acid position, both
        in vivo and in vitro with purified methionyl aminopeptidase.
      notes: Methionyl aminopeptidase cleaves the N-terminal methionine residue (PMID:2682640) (ECO:0000269)
  - subject: GO:0004239
    predicate: positively regulates
    predicate_id: RO:0002213
    object: GO:0016485
    description: Methionyl aminopeptidase catalysis excises Met1 during co-translational N-terminal protein
      processing.
    evidence:
    - reference: PMID:2682640
      snippet: The in vitro study strongly suggests that the rules governing the NH2-terminal methionine
        excision in vivo reflect the substrate specificity of the methionyl aminopeptidase alone.
      notes: MetAP substrate specificity governs in vivo N-terminal methionine processing (PMID:2682640)
        (ECO:0000269)
evidence:
- reference: PMID:2682640
  notes: Hirel et al. (1989) demonstrate that N-terminal initiator methionine excision by methionyl aminopeptidase
    is governed by the side-chain length of the penultimate amino acid residue.""",
}


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
    if category in MECHANISM_BLOCKS:
        lines.append(MECHANISM_BLOCKS[category])
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
