#!/usr/bin/env python3
"""Curator promotion pass: turn a whole AMR gene family's auto-DRAFT resistance
graphs into REVIEWED graphs by attaching the family's verbatim literature snippets.

`draft_aro_causal_graphs.py` scaffolds a determinant→mechanism→phenotype graph on
every enriched ARO gene, but leaves the edges snippet-less (SEEDED). Because every
member of one AMR gene family shares the *same* inherited mechanism + drug classes,
one curated set of verbatim snippets promotes the *entire family* at once. This
script:
  • finds every draft record whose `is_a` ancestry includes the target family;
  • regenerates its `resistance-draft` graph as a curated `resistance` graph whose
    edges carry a verbatim `snippet` (chosen by edge role + the mechanism/drug the
    edge points at) and a real PMID `reference`;
  • flips `mapping_status: SEEDED → REVIEWED` and appends a `curation_history` event.

Snippets live in `FAMILY_SNIPPETS` keyed by family ARO id — extend it to promote
more families. `just audit-graphs --strict` should report the family's records as
snippet-complete afterwards. Idempotent (skips records already carrying a
`graph_id: resistance` graph). Dry-run unless --apply. Stdlib-only.
"""

from __future__ import annotations

import argparse
import re
import sys

import yaml
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import draft_aro_causal_graphs as D            # parse_relations, obo_names, _yq, MAX_DRUGS
import enrich_aro_resistance as E              # ancestry, parse_obo
import record_io as RIO                        # replace_block, shared splice rules

ARO_DIR = D.ARO_DIR
TRAITS_ROOT = Path(__file__).resolve().parent.parent / "data" / "traits"

# family ARO id → curated evidence. `reference` is the family's characterisation
# paper; `mech[<mechanism ARO id>]`, `mech_res`, `det_res`, `res_drug` are verbatim
# snippets for each edge role.

# ---------------------------------------------------------------------------------------
# Quinolone action, shared by the four fluoroquinolone target-alteration families (gyrA,
# gyrB, parC, parE). The DRUG's half of the mechanism is identical for all of them — one
# drug class, one target enzyme family — so it is written once. What differs per family,
# and is NOT shared below, is which subunit is altered, which domain the QRDR sits in, and
# which paper reports its substitutions.
#
# All five are pasted from PMID:24576155 (Aldred, Kerns & Osheroff 2014, PMC3985860),
# including its U+2032 primes. Superscript reference markers are dropped, nothing else.
_FQ_CLEAVAGE = "To maintain genomic integrity during this process, the enzymes form covalent bonds between active site tyrosine residues and the newly generated 5′-DNA termini."
_FQ_INTERCALATE = "As a result of their intercalation, quinolones increase the steady-state concentration of cleavage complexes by acting as physical blocks to ligation."
_FQ_CELL_DEATH = "If the strand breaks overwhelm these processes, they can lead to cell death. This is the primary mechanism that quinolones use to kill bacterial cells"
_FQ_AFFINITY = "Furthermore, mutation of either residue significantly decreases the affinity of gyrase or topoisomerase IV for quinolones, and mutation of both residues abolishes the ability of clinically relevant quinolones to stabilize cleavage complexes."
# the sentence that settles which subunit is which — and therefore which of the four
# families can reuse gyrA's domain node and which cannot.
_FQ_SUBUNITS = "The subunits in gyrase are GyrA and GyrB. The homologous subunits in topoisomerase IV are ParC and ParE in Gram-negative species and GrlA and GrlB in Gram-positive species. GyrA (and the equivalent topoisomerase IV subunit) contains the active site tyrosine residue. GyrB (and the equivalent topoisomerase IV subunit) contains the ATPase domain as well as the TOPRIM domain, which binds the divalent metal ions involved in DNA cleavage and ligation."

# InterPro abstracts that the two Pfam KB records' definitions are taken from.
_IPR_A_SUBUNIT = "domain 3 (N-terminal of gyrA) is responsible for the breaking-rejoining function through its capacity to form protein-DNA bridges"
_IPR_B_SUBUNIT = "There are four functional domains in topoisomerase II: domain 1 (N-terminal of gyrB) is an ATPase, domain 2 (C-terminal of gyrB) is responsible for subunit interactions, domain 3 (N-terminal of gyrA) is responsible for the breaking-rejoining function through its capacity to form protein-DNA bridges, and domain 4 (C-terminal of gyrA) is able to non-specifically bind DNA."


def _fq_shared_edges(qrdr_regulates_evidence: list) -> list:
    """The quinolone-action arm, identical for gyrA/gyrB/parC/parE.

    Only the `qrdr → cleavage_complex` edge differs between families, because the
    evidence that a substitution in THAT subunit's QRDR reduces drug action is
    subunit-specific — the A-subunit serine/acidic pair forms the water-metal ion bridge
    and the B-subunit residues do not, so citing the A-subunit affinity result on a gyrB
    record would be citing the wrong experiment.
    """
    return [
        {"subject": "domain", "object": "gyrase_activity",
         "predicate": "enables (type II topoisomerase activity)", "predicate_id": "RO:0002327",
         "evidence": [{"reference": "PMID:24576155", "snippet": _FQ_SUBUNITS,
                       "notes": "Aldred 2014, the subunit/domain architecture of gyrase and topoisomerase IV."}]},
        {"subject": "gyrase_activity", "object": "cleavage_complex",
         "predicate": "causally upstream of (forms the covalent intermediate)", "predicate_id": "RO:0002411",
         "evidence": [{"reference": "PMID:24576155", "snippet": _FQ_CLEAVAGE,
                       "notes": "Aldred 2014. The cleavage complex is the enzyme's own catalytic intermediate, present with or without drug."}]},
        {"subject": "drug0", "object": "cleavage_complex",
         "predicate": "molecularly interacts with (intercalates and blocks ligation)", "predicate_id": "RO:0002436",
         "description": "Quinolone action: the drug binds the cleaved complex and blocks religation, raising the steady-state level of DNA breaks.",
         "evidence": [{"reference": "PMID:24576155", "snippet": _FQ_INTERCALATE,
                       "notes": "Aldred 2014. This is the drug-ACTION arm; resistance is the loss of it."}]},
        {"subject": "qrdr", "object": "cleavage_complex",
         "predicate": "negatively regulates (substitution lowers drug action)", "predicate_id": "RO:0002212",
         "description": "The causal core: a QRDR substitution reduces the drug's ability to trap this enzyme, so fewer drug-stabilised cleavage complexes form at a given drug concentration.",
         "evidence": qrdr_regulates_evidence},
        {"subject": "cleavage_complex", "object": "cell_death",
         "predicate": "causally upstream of (drug-stabilised breaks kill the cell)", "predicate_id": "RO:0002411",
         "description": "Why fewer stabilised complexes means survival: the complexes are what kill the cell.",
         "evidence": [{"reference": "PMID:24576155", "snippet": _FQ_CELL_DEATH, "notes": "Aldred 2014."}]},
    ]


def _fq_shared_nodes(qrdr_label: str, qrdr_description: str) -> list:
    """Everything except the `domain` node.

    `protein_traits["primary_key"]` already emits that one, and emitting it here as well
    produced a **duplicate `node_id: domain`** — which `just validate` accepts without
    complaint (the schema has no uniqueness constraint on `node_id`) and only
    `just audit-graphs` rejects. Caught by promoting one record per family before the
    rest, which is the only reason it is not in 29 records.
    """
    return [
        {"node_id": "qrdr", "label": qrdr_label, "node_type": "MOTIF",
         "description": qrdr_description},
        {"node_id": "gyrase_activity",
         "label": "DNA topoisomerase type II (double strand cut, ATP-hydrolyzing) activity",
         "node_type": "MOLECULAR_FUNCTION", "grounding": "GO:0003918"},
        {"node_id": "cleavage_complex", "label": "enzyme-DNA cleavage complex", "node_type": "STATE",
         "description": "The covalent enzyme-cleaved DNA intermediate that quinolones bind and stabilise. Ungrounded, as with the M-CSA reaction-intermediate STATE nodes."},
        {"node_id": "cell_death", "label": "bacterial cell death", "node_type": "PHENOTYPE",
         "grounding": "GO:0008219"},
    ]


def _van_cluster_genes() -> dict:
    """cluster letter -> the van genes the corpus records for that cluster.

    Built from the corpus's own `van<G> gene in van<C> cluster` records, which is why the
    vanR/vanS precondition below is a query rather than a judgement about biology.
    """
    global _VAN_CLUSTERS
    if _VAN_CLUSTERS is None:
        idx: dict[str, set[str]] = {}
        for pth in ARO_DIR.glob("*.yaml"):
            m = re.search(r'^label:\s*"?(van[A-Z]+) gene in (van[A-Z]) cluster"?\s*$',
                          pth.read_text(encoding="utf-8"), re.M)
            if m:
                idx.setdefault(m.group(2), set()).add(m.group(1))
        _VAN_CLUSTERS = idx
    return _VAN_CLUSTERS


_VAN_CLUSTERS = None


def _requires_vanhax(ident: str, label: str, text: str):
    """vanR/vanS graphs name vanH and vanX downstream — so the cluster must have them.

    The evidence is VanA-type (PMID:1556077, Tn1546/pIP816). The D-Ala-D-Ser clusters
    encode vanT and vanXY instead, and vanI has vanX but no vanH, so promoting those would
    assert an operon composition false for that cluster (#201).

    A record with no cluster in its label is the family-level concept (`vanR`, `vanS`) and
    passes: it is the general term the VanA-type description is written against.
    """
    m = re.search(r"gene in (van[A-Z]+) cluster", label)
    if not m:
        # Codex review: this returned None for ANY unparsed label, so a future label shape
        # (`... in vanC1 cluster`, a case change) would fail OPEN and receive the
        # vanH/vanX graph. A label that mentions a cluster but does not parse is refused.
        if "cluster" in label:
            return ("label names a cluster but does not match the expected "
                    "'<gene> gene in van<X> cluster' shape, so the cluster's gene "
                    "content cannot be checked")
        return None
    genes = _van_cluster_genes().get(m.group(1), set())
    missing = [g for g in ("vanH", "vanX") if g not in genes]
    if missing:
        return (f"cluster {m.group(1)} has no {' or '.join(missing)} "
                f"(records present: {' '.join(sorted(genes)) or 'none'}); this config's "
                f"downstream nodes name both")
    return None

# ---------------------------------------------------------------------------------------
# The VanS-VanR regulatory arm, shared by both halves of the two-component system. Every
# snippet is from PMID:1556077 (Arthur, Molinas & Courvalin 1992), which characterised the
# system and mapped the promoter it activates.
#
# THESE TWO FAMILIES CONFER NO RESISTANCE THEMSELVES. They switch on the genes that do —
# and those genes are already curated records in this corpus, so the downstream nodes are
# ARO:3000006 (vanH, round 21) and ARO:3000011 (vanX, round 20) rather than free-text
# labels. This is the first round whose graphs point at earlier rounds' output.
_VANRS_REG = 'Synthesis of these enzymes was regulated at the transcriptional level by the VanS-VanR two-component regulatory system encoded by the proximal part of the cluster.'
_VANRS_PROMOTER = 'Analysis of transcriptional fusions with a reporter gene and RNA mapping indicated that the VanR-VanS two-component regulatory system activates a promoter used for cotranscription of the vanH, vanA, and vanX resistance genes.'
_VANRS_NECESSARY = 'The distal part of the van cluster encodes VanH, VanA, and a third enzyme, VanX, all of which are necessary for resistance.'
_VANRS_INDUCIBLE = 'Plasmid pIP816 of Enterococcus faecium BM4147 confers inducible resistance to vancomycin and encodes the VanH dehydrogenase and the VanA ligase for synthesis of depsipeptide-containing peptidoglycan precursors which bind the antibiotic with reduced affinity.'


def _vanrs_downstream() -> tuple[list, list]:
    """The half of the graph that is identical for vanR and vanS: transcription of the
    resistance operon, and the two enzyme records that operon encodes."""
    nodes = [
        {"node_id": "transcription",
         "label": "positive regulation of DNA-templated transcription (the vanHAX promoter)",
         "node_type": "BIOLOGICAL_PROCESS", "grounding": "GO:0045893"},
        {"node_id": "vanh_gene", "label": "vanH (D-lactate dehydrogenase of the van cluster)",
         "node_type": "PROTEIN", "grounding": "ARO:3000006",
         "description": "KB record, curated in round 21 — the mechanism this regulator switches on."},
        {"node_id": "vanx_gene", "label": "vanX (D,D-dipeptidase of the van cluster)",
         "node_type": "PROTEIN", "grounding": "ARO:3000011",
         "description": "KB record, curated in round 20."},
    ]
    edges = [
        {"subject": "transcription", "object": "vanh_gene",
         "predicate": "positively regulates (cotranscribed from the induced promoter)",
         "predicate_id": "RO:0002213",
         "evidence": [{"reference": "PMID:1556077", "snippet": _VANRS_PROMOTER,
                       "notes": "Arthur et al. 1992 mapped the promoter by transcriptional fusion and RNA mapping; vanH is one of the three genes cotranscribed from it."}]},
        {"subject": "transcription", "object": "vanx_gene",
         "predicate": "positively regulates (cotranscribed from the induced promoter)",
         "predicate_id": "RO:0002213",
         "evidence": [{"reference": "PMID:1556077", "snippet": _VANRS_PROMOTER,
                       "notes": "Same promoter, same experiment; vanX is the third gene of the cotranscript."}]},
        {"subject": "vanh_gene", "object": "resistance",
         "predicate": "causally upstream of (the mechanism this regulator induces)",
         "predicate_id": "RO:0002411",
         "description": "The regulator confers no resistance itself; the enzymes it induces do.",
         "evidence": [{"reference": "PMID:1556077", "snippet": _VANRS_NECESSARY,
                       "notes": "Arthur et al. 1992. VanH's own mechanism is curated on ARO:3000006 (round 21)."}]},
        {"subject": "vanx_gene", "object": "resistance",
         "predicate": "causally upstream of (the mechanism this regulator induces)",
         "predicate_id": "RO:0002411",
         "description": "The regulator confers no resistance itself; the enzymes it induces do.",
         "evidence": [{"reference": "PMID:1556077", "snippet": _VANRS_NECESSARY,
                       "notes": "Arthur et al. 1992. VanX's own mechanism is curated on ARO:3000011 (round 20)."}]},
    ]
    return nodes, edges



FAMILY_SNIPPETS = {
    # ---------------------------------------------------------------------------------
    # vanR — the response regulator (ARO:3000574). A FOURTH kind of mechanism: regulation.
    # vanR neither destroys the drug, nor alters a target, nor remodels a precursor — it
    # transcribes the genes that do. So its graph ends at ARO:3000006 / ARO:3000011, whose
    # own mechanisms are curated, rather than restating them.
    "ARO:3000574": {
        "curated": "2026-08-06T00:00:00Z",
        # Was a hand-written list of 12 ARO ids; now DERIVED from the corpus (#201). The
        # evidence is VanA-type (PMID:1556077, Tn1546/pIP816) and the downstream nodes are
        # vanH + vanX, so a cluster lacking either is excluded — re-evaluated every run
        # rather than frozen at the moment someone looked.
        "precondition": _requires_vanhax,
        "reference": "PMID:1556077",        # Arthur, Molinas & Courvalin 1992, J Bacteriol
        "mech": {"ARO:3000213": _VANRS_REG},
        "mech_res": _VANRS_REG,
        "det_res": [
            {"reference": "PMID:1556077", "snippet": 'VanR was a transcriptional activator related to response regulators of the OmpR subclass.',
             "notes": "Arthur et al. 1992. VanR is a transcriptional activator, not a resistance enzyme."},
            {"reference": "PMID:1556077", "snippet": _VANRS_NECESSARY,
             "notes": "What it activates is what confers resistance: the resistance step is one edge further down this graph, on ARO:3000006 and ARO:3000011."},
        ],
        "res_drug": _VANRS_INDUCIBLE,
        "note": "Regulation, not resistance: VanR activates the promoter of the vanHAX operon, and resistance is inducible for that reason.",
        "extra_nodes": _vanrs_downstream()[0] + [
            {"node_id": "family", "label": "VanR-ABDEGLN family response regulator transcription factor",
             "node_type": "PROTEIN", "grounding": "NCBIfam:NF033117",
             "description": "KB protein-trait record for the VanR family. A family, not a domain — hence `member of`."},
            {"node_id": "activity", "label": "phosphorelay response regulator activity",
             "node_type": "MOLECULAR_FUNCTION", "grounding": "GO:0000156"},
        ],
        "extra_edges": _vanrs_downstream()[1] + [
            {"subject": "determinant", "object": "family",
             "predicate": "member of (the VanR response-regulator family)", "predicate_id": "RO:0002350",
             "evidence": [
                 {"reference": "PMID:1556077", "snippet": 'VanR was a transcriptional activator related to response regulators of the OmpR subclass.',
                  "notes": "Establishes what VanR is."},
                 {"reference": "NCBIfam:NF033117", "snippet": "VanR-ABDEGLN family response regulator transcription factor",
                  "notes": "NCBIfam's own product name for the profile-HMM family this node grounds to; the join with the paper is stated rather than implied. NOT the KB record's definition, which this repo composes."},
             ]},
            {"subject": "family", "object": "activity",
             "predicate": "enables (response-regulator phosphorelay)", "predicate_id": "RO:0002327",
             "evidence": [{"reference": "PMID:1556077", "snippet": 'VanS stimulated VanR-dependent transcription and was related to membrane-associated histidine protein kinases which control the level of phosphorylation of response regulators.',
                           "notes": "Named here from the kinase's side: VanS controls the phosphorylation level of response regulators, of which VanR is one."}]},
            {"subject": "activity", "object": "transcription",
             "predicate": "causally upstream of (activates the promoter)", "predicate_id": "RO:0002411",
             "evidence": [{"reference": "PMID:1556077", "snippet": _VANRS_PROMOTER,
                           "notes": "Arthur et al. 1992."}]},
        ],
    },
    # ---------------------------------------------------------------------------------
    # vanS — the sensor histidine kinase (ARO:3000071). Same downstream half as vanR; the
    # difference is upstream, where VanS phosphorylates rather than being phosphorylated.
    "ARO:3000071": {
        "curated": "2026-08-06T00:00:00Z",
        # Was a hand-written list of 12 ARO ids; now DERIVED from the corpus (#201). The
        # evidence is VanA-type (PMID:1556077, Tn1546/pIP816) and the downstream nodes are
        # vanH + vanX, so a cluster lacking either is excluded — re-evaluated every run
        # rather than frozen at the moment someone looked.
        "precondition": _requires_vanhax,
        "reference": "PMID:1556077",
        "mech": {"ARO:3000213": _VANRS_REG},
        "mech_res": _VANRS_REG,
        "det_res": [
            {"reference": "PMID:1556077", "snippet": 'VanS stimulated VanR-dependent transcription and was related to membrane-associated histidine protein kinases which control the level of phosphorylation of response regulators.',
             "notes": "Arthur et al. 1992. VanS is a sensor kinase, not a resistance enzyme."},
            {"reference": "PMID:1556077", "snippet": _VANRS_NECESSARY,
             "notes": "What it ultimately switches on is what confers resistance."},
        ],
        "res_drug": _VANRS_INDUCIBLE,
        "note": "Regulation, not resistance: VanS stimulates VanR-dependent transcription of the vanHAX operon.",
        "extra_nodes": _vanrs_downstream()[0] + [
            {"node_id": "family", "label": "vancomycin resistance histidine kinase VanS",
             "node_type": "PROTEIN", "grounding": "NCBIfam:NF033091",
             "description": "KB protein-trait record for the VanS family. A family, not a domain — hence `member of`."},
            {"node_id": "activity", "label": "phosphorelay sensor kinase activity",
             "node_type": "MOLECULAR_FUNCTION", "grounding": "GO:0000155"},
            {"node_id": "vanr_protein", "label": "VanR response regulator", "node_type": "PROTEIN",
             "grounding": "ARO:3000574",
             "description": "KB record for the partner regulator, curated in the same round."},
        ],
        "extra_edges": _vanrs_downstream()[1] + [
            {"subject": "determinant", "object": "family",
             "predicate": "member of (the VanS sensor-kinase family)", "predicate_id": "RO:0002350",
             "evidence": [
                 {"reference": "PMID:1556077", "snippet": 'VanS stimulated VanR-dependent transcription and was related to membrane-associated histidine protein kinases which control the level of phosphorylation of response regulators.',
                  "notes": "Establishes what VanS is."},
                 {"reference": "NCBIfam:NF033091", "snippet": "vancomycin resistance histidine kinase VanS",
                  "notes": "NCBIfam's own product name for the profile-HMM family this node grounds to. NOT the KB record's definition, which this repo composes."},
             ]},
            {"subject": "family", "object": "activity",
             "predicate": "enables (sensor histidine kinase phosphorelay)", "predicate_id": "RO:0002327",
             "evidence": [{"reference": "PMID:1556077", "snippet": 'VanS stimulated VanR-dependent transcription and was related to membrane-associated histidine protein kinases which control the level of phosphorylation of response regulators.',
                           "notes": "Arthur et al. 1992: related to membrane-associated histidine protein kinases that control response-regulator phosphorylation."}]},
            {"subject": "activity", "object": "vanr_protein",
             "predicate": "positively regulates (phosphorylates the partner regulator)",
             "predicate_id": "RO:0002213",
             "description": "The phosphorelay step: VanS controls VanR's phosphorylation level, and VanR is what binds the promoter.",
             "evidence": [{"reference": "PMID:1556077", "snippet": 'VanS stimulated VanR-dependent transcription and was related to membrane-associated histidine protein kinases which control the level of phosphorylation of response regulators.',
                           "notes": "The paper states the stimulation and the kinase relationship; it does not report a direct phosphotransfer assay, so the edge claims regulation rather than a measured transfer."}]},
            {"subject": "vanr_protein", "object": "transcription",
             "predicate": "causally upstream of (activates the promoter)", "predicate_id": "RO:0002411",
             "evidence": [{"reference": "PMID:1556077", "snippet": _VANRS_PROMOTER,
                           "notes": "Arthur et al. 1992."}]},
        ],
    },
    # ---------------------------------------------------------------------------------
    # vanH — the OTHER end of the depsipeptide pathway (ARO:3000006). vanX (round 20)
    # removes the drug's binding target; vanH supplies the D-hydroxy acid that the
    # already-promoted vanA/vanB ligases esterify to build the replacement. One 1991 paper
    # (PMID:1931965) purified the enzyme and measured the affinity loss the whole mechanism
    # exists to produce, so all six mechanism edges come from it.
    #
    # NO `protein_traits` BLOCK, deliberately. Its fixed edge is `domain part of
    # determinant`, and the honest KB trait for VanH is a protein FAMILY
    # (NCBIfam:NF000492), which a determinant is a MEMBER of, not composed of. The
    # membership edge is written explicitly below with the predicate that means it.
    # Pfam:PF00389 was the obvious domain candidate and is NOT used: its abstract never
    # names VanH, so citing it for a membership claim would be the defect filed as #196.
    "ARO:3000006": {
        "curated": "2026-08-05T00:00:00Z",
        "reference": "PMID:1931965",        # Bugg et al. 1991, Biochemistry
        "mech": {"ARO:3000213": 'The vancomycin binding constant of a synthetic modified peptidoglycan analogue N-acetyl-D-alanyl-D-2-hydroxybutyrate (Kd greater than 73 mM) was greater than 1000-fold higher than the binding constant for N-acetyl-D-alanyl-D-alanine (Kd = 54 microM), partly due to the disruption of a hydrogen bond in the vancomycin-target complex, thus providing a molecular rationale for high-level vancomycin resistance.'},
        "mech_res": 'The vancomycin binding constant of a synthetic modified peptidoglycan analogue N-acetyl-D-alanyl-D-2-hydroxybutyrate (Kd greater than 73 mM) was greater than 1000-fold higher than the binding constant for N-acetyl-D-alanyl-D-alanine (Kd = 54 microM), partly due to the disruption of a hydrogen bond in the vancomycin-target complex, thus providing a molecular rationale for high-level vancomycin resistance.',
        "det_res": [
            {"reference": "PMID:1931965", "snippet": 'We report purification of VanH to homogeneity, characterization as a D-specific alpha-keto acid dehydrogenase, and comparison with D-lactate dehydrogenases from Leuconostoc mesenteroides and Lactobacillus leichmanii.',
             "notes": "Bugg et al. 1991 purified VanH and characterised the activity; this is the determinant's molecular function, established by purification rather than by sequence similarity."},
            {"reference": "PMID:1931965", "snippet": 'The vancomycin binding constant of a synthetic modified peptidoglycan analogue N-acetyl-D-alanyl-D-2-hydroxybutyrate (Kd greater than 73 mM) was greater than 1000-fold higher than the binding constant for N-acetyl-D-alanyl-D-alanine (Kd = 54 microM), partly due to the disruption of a hydrogen bond in the vancomycin-target complex, thus providing a molecular rationale for high-level vancomycin resistance.',
             "notes": "The same paper measured what that activity buys: a >1000-fold weaker vancomycin binding constant for the modified precursor."},
        ],
        "res_drug": 'The vancomycin binding constant of a synthetic modified peptidoglycan analogue N-acetyl-D-alanyl-D-2-hydroxybutyrate (Kd greater than 73 mM) was greater than 1000-fold higher than the binding constant for N-acetyl-D-alanyl-D-alanine (Kd = 54 microM), partly due to the disruption of a hydrogen bond in the vancomycin-target complex, thus providing a molecular rationale for high-level vancomycin resistance.',
        "note": "Precursor substitution: VanH makes the D-hydroxy acid that replaces the terminal D-Ala, so the drug's binding site is rebuilt rather than removed.",
        "extra_nodes": [
            {"node_id": "family", "label": "D-lactate dehydrogenase VanH (NCBIfam family)",
             "node_type": "PROTEIN", "grounding": "NCBIfam:NF000492",
             "description": "KB protein-trait record for the VanH family. A family, not a domain — hence `member of` rather than `part of`."},
            {"node_id": "dh_activity", "label": "D-lactate dehydrogenase (NAD+) activity",
             "node_type": "MOLECULAR_FUNCTION", "grounding": "GO:0008720"},
            {"node_id": "d_hydroxy_acid", "label": "D-hydroxy acid product of VanH ((R)-lactate)",
             "node_type": "CHEMICAL", "grounding": "CHEBI:16004",
             "description": "Grounded to (R)-lactate, the physiological product. Bugg et al.'s best in vitro substrate for the downstream VanA ligase was D-2-hydroxybutyrate, which is what their quoted measurements use — the node is grounded to the physiological compound and the snippets say which was assayed."},
            {"node_id": "depsipeptide", "label": "peptidoglycan precursor terminating in D-Ala-D-hydroxy acid",
             "node_type": "STATE",
             "description": "The rebuilt precursor. Ungrounded: ChEBI has no term for the UDP-MurNAc pentadepsipeptide."},
            {"node_id": "van_complex", "label": "vancomycin-target complex", "node_type": "STATE",
             "description": "The drug bound to the precursor terminus. Ungrounded: a complex, not a compound."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "family",
             "predicate": "member of (the VanH D-lactate dehydrogenase family)", "predicate_id": "RO:0002350",
             "description": "Routes this determinant through the KB's own VanH family record.",
             "evidence": [
                 {"reference": "PMID:1931965", "snippet": 'We report purification of VanH to homogeneity, characterization as a D-specific alpha-keto acid dehydrogenase, and comparison with D-lactate dehydrogenases from Leuconostoc mesenteroides and Lactobacillus leichmanii.',
                  "notes": "Establishes what VanH is, by purification."},
                 {"reference": "NCBIfam:NF000492", "snippet": "D-lactate dehydrogenase VanH",
                  "notes": "NCBIfam's own product name for profile-HMM NF000492 — the KB trait record this node grounds to. The join of the two is stated rather than implied: the paper says what VanH does, NCBIfam names the family that does it. NOT the KB record's definition text, which this repo composes."},
             ]},
            {"subject": "family", "object": "dh_activity",
             "predicate": "enables (D-specific alpha-keto acid reduction)", "predicate_id": "RO:0002327",
             "evidence": [{"reference": "PMID:1931965", "snippet": 'We report purification of VanH to homogeneity, characterization as a D-specific alpha-keto acid dehydrogenase, and comparison with D-lactate dehydrogenases from Leuconostoc mesenteroides and Lactobacillus leichmanii.',
                           "notes": "Bugg et al. 1991; compared directly with the D-lactate dehydrogenases of Leuconostoc and Lactobacillus."}]},
            {"subject": "dh_activity", "object": "d_hydroxy_acid",
             "predicate": "has output", "predicate_id": "RO:0002234",
             "evidence": [{"reference": "PMID:1931965", "snippet": 'VanA was found to catalyze ester bond formation between D-alanine and the D-hydroxy acid products of VanH, the best substrate being D-2-hydroxybutyrate (Km = 0.60 mM).',
                           "notes": "Names the D-hydroxy acids as the products of VanH, and the ligase that consumes them."}]},
            {"subject": "d_hydroxy_acid", "object": "depsipeptide",
             "predicate": "causally upstream of (is esterified and incorporated)", "predicate_id": "RO:0002411",
             "description": "The VanH product is esterified to D-alanine by the ligase and the ester is incorporated into the precursor.",
             "evidence": [{"reference": "PMID:1931965", "snippet": 'The VanA product D-alanyl-D-2-hydroxybutyrate could then be incorporated into the UDPMurNAc-pentapeptide peptidoglycan precursor by D-Ala-D-Ala adding enzyme from Escherichia coli or by crude extract from E. faecium BM4147.',
                           "notes": "Incorporation shown with both a purified E. coli adding enzyme and a crude E. faecium extract."}]},
            {"subject": "depsipeptide", "object": "van_complex",
             "predicate": "negatively regulates (>1000-fold weaker binding)", "predicate_id": "RO:0002212",
             "description": "The causal core, and it is quantified: replacing the terminal D-Ala raises the vancomycin Kd from 54 microM to >73 mM.",
             "evidence": [{"reference": "PMID:1931965", "snippet": 'The vancomycin binding constant of a synthetic modified peptidoglycan analogue N-acetyl-D-alanyl-D-2-hydroxybutyrate (Kd greater than 73 mM) was greater than 1000-fold higher than the binding constant for N-acetyl-D-alanyl-D-alanine (Kd = 54 microM), partly due to the disruption of a hydrogen bond in the vancomycin-target complex, thus providing a molecular rationale for high-level vancomycin resistance.',
                           "notes": "The authors' own molecular rationale for high-level resistance, including the disrupted hydrogen bond."}]},
            # NOT `drug0 molecularly interacts with van_complex`: the drug is a CONSTITUENT
            # of that complex, so an interaction edge between them is circular. The complex
            # HAS the drug as a part; the affinity claim lives on the depsipeptide edge
            # above, which is where the causation is.
            {"subject": "van_complex", "object": "drug0",
             "predicate": "has part (the bound glycopeptide)", "predicate_id": "BFO:0000051",
             "description": "Defines the complex: vancomycin bound to the precursor terminus, Kd = 54 microM against D-Ala-D-Ala. This is what the depsipeptide prevents.",
             "evidence": [{"reference": "PMID:1931965", "snippet": 'The vancomycin binding constant of a synthetic modified peptidoglycan analogue N-acetyl-D-alanyl-D-2-hydroxybutyrate (Kd greater than 73 mM) was greater than 1000-fold higher than the binding constant for N-acetyl-D-alanyl-D-alanine (Kd = 54 microM), partly due to the disruption of a hydrogen bond in the vancomycin-target complex, thus providing a molecular rationale for high-level vancomycin resistance.',
                           "notes": "The same sentence carries both arms: the drug's normal affinity and its loss."}]},
        ],
    },
    # ---------------------------------------------------------------------------------
    # vanX — glycopeptide resistance by PRECURSOR DEPLETION (ARO:3000011). A third kind of
    # mechanism again: not drug inactivation (β-lactamases), not target alteration
    # (gyrA/parC), but removal of the drug's BINDING TARGET. VanX is a D,D-dipeptidase that
    # destroys D-Ala-D-Ala, so the pentapeptide glycopeptides bind is not made.
    #
    # The resistance ligases themselves (vanA/B/D/M, D-Ala-D-Lac) were promoted in round
    # 14 and carry no drafts; what is left of the van clusters is the accessory and
    # regulatory machinery, of which this is the crispest.
    "ARO:3000011": {
        "curated": "2026-08-05T00:00:00Z",
        "reference": "PMID:7854121",        # Reynolds et al. 1994, Mol Microbiol
        "mech": {"ARO:3000213": "These results establish that VanX is required for production of a D,D-dipeptidase that hydrolyses D-Ala-D-Ala, thereby preventing pentapeptide synthesis and subsequent binding of glycopeptides to D-Ala-D-Ala-containing peptidoglycan precursors at the cell surface."},
        "mech_res": "These results establish that VanX is required for production of a D,D-dipeptidase that hydrolyses D-Ala-D-Ala, thereby preventing pentapeptide synthesis and subsequent binding of glycopeptides to D-Ala-D-Ala-containing peptidoglycan precursors at the cell surface.",
        # two items (#190): the genetic requirement, then the mechanism it implies. The
        # inactivation experiment is what makes this causal rather than correlative.
        "det_res": [
            {"reference": "PMID:7854121",
             "snippet": "Insertional inactivation of vanX led to increased synthesis of pentapeptide with a resulting change in the ratio of pentadepsipeptide: pentapeptide to less than 1:1.",
             "notes": "Reynolds et al. 1994. Knocking out vanX restores the pentapeptide the drug binds — the requirement demonstrated by loss of function, not by association."},
            {"reference": "PMID:7854121",
             "snippet": "These results establish that VanX is required for production of a D,D-dipeptidase that hydrolyses D-Ala-D-Ala, thereby preventing pentapeptide synthesis and subsequent binding of glycopeptides to D-Ala-D-Ala-containing peptidoglycan precursors at the cell surface.",
             "notes": "The authors' own summary of the causal chain, in one sentence."},
        ],
        "res_drug": "These results establish that VanX is required for production of a D,D-dipeptidase that hydrolyses D-Ala-D-Ala, thereby preventing pentapeptide synthesis and subsequent binding of glycopeptides to D-Ala-D-Ala-containing peptidoglycan precursors at the cell surface.",
        "note": "Precursor depletion: VanX removes D-Ala-D-Ala so the pentapeptide that glycopeptides bind is not synthesised.",
        "protein_traits": {
            "primary_key": "domain",
            # the snippet must establish that THIS domain is THIS determinant's, which an
            # activity result does not. The KB record's own InterPro abstract names VanX
            # outright, so it is the right evidence for the part-of edge; Reynolds' activity
            # result stays on the `domain enables dipeptidase` edge, where it belongs.
            "domain": ("Pfam:PF01427", "D-Ala-D-Ala dipeptidase domain (MEROPS M15D, the VanX subfamily)", "DOMAIN",
                       "This group of metallopeptidases belong to MEROPS peptidase family M15 (clan MD), subfamily M15D (vanX D-Ala-D-Ala dipeptidase). The D-alanyl-D-alanine dipeptidase enzyme from Enterococcus faecalis is also known as the vancomycin resistance protein VanX, and hydrolyses D-ala-D-ala."),
            "part_pred": "part of (the dipeptidase domain of this determinant)",
            "part_note": "KB trait record Pfam:PF01427; snippet is the InterPro:IPR000755 abstract that record's definition is taken from, which names VanX as the subfamily M15D enzyme.",
        },
        "extra_nodes": [
            {"node_id": "dipeptidase", "label": "D,D-dipeptidase activity", "node_type": "MOLECULAR_FUNCTION",
             "grounding": "GO:0016805"},
            {"node_id": "dala_dala", "label": "D-alanyl-D-alanine", "node_type": "CHEMICAL",
             "grounding": "CHEBI:16576"},
            {"node_id": "pentapeptide", "label": "UDP-MurNAc-pentapeptide terminating in D-Ala-D-Ala",
             "node_type": "STATE",
             "description": "The peptidoglycan precursor glycopeptides bind. Ungrounded: ChEBI has the D-Ala-D-Ala dipeptide but not this UDP-MurNAc pentapeptide as a distinct term."},
        ],
        "extra_edges": [
            {"subject": "domain", "object": "dipeptidase",
             "predicate": "enables (D,D-dipeptidase activity)", "predicate_id": "RO:0002327",
             "evidence": [
                 {"reference": "PMID:7854121",
                  "snippet": "Expression of vanX in E. faecalis and Escherichia coli resulted in production of a D,D-dipeptidase that hydrolysed D-Ala-D-Ala.",
                  "notes": "Reynolds et al. 1994, heterologous expression in two hosts."},
             ]},
            {"subject": "dipeptidase", "object": "dala_dala",
             "predicate": "has input (hydrolyses)", "predicate_id": "RO:0002233",
             "description": "The enzyme is specific: the pentadepsipeptide, the pentapeptide and D-Ala-D-Lac are not substrates.",
             "evidence": [
                 {"reference": "PMID:7854121",
                  "snippet": "Pentadepsipeptide, pentapeptide and D-Ala-D-Lac were not substrates for the enzyme.",
                  "notes": "Reynolds et al. 1994. The negative result is what makes the target specific — VanX destroys the free dipeptide, not the assembled precursor."},
             ]},
            {"subject": "dipeptidase", "object": "pentapeptide",
             "predicate": "negatively regulates (depletes the precursor)", "predicate_id": "RO:0002212",
             "description": "The causal core: with D-Ala-D-Ala hydrolysed, the pentapeptide the drug binds is not synthesised.",
             "evidence": [
                 {"reference": "PMID:7854121",
                  "snippet": "These results establish that VanX is required for production of a D,D-dipeptidase that hydrolyses D-Ala-D-Ala, thereby preventing pentapeptide synthesis and subsequent binding of glycopeptides to D-Ala-D-Ala-containing peptidoglycan precursors at the cell surface.",
                  "notes": "Reynolds et al. 1994."},
             ]},
            {"subject": "drug0", "object": "pentapeptide",
             "predicate": "molecularly interacts with (binds the D-Ala-D-Ala terminus)", "predicate_id": "RO:0002436",
             "description": "Drug action: glycopeptides bind the D-Ala-D-Ala terminus of the precursor at the cell surface. Removing that terminus is what confers resistance.",
             "evidence": [
                 {"reference": "PMID:7854121",
                  "snippet": "subsequent binding of glycopeptides to D-Ala-D-Ala-containing peptidoglycan precursors at the cell surface",
                  "notes": "Reynolds et al. 1994; the drug-ACTION arm this determinant removes."},
             ]},
        ],
    },
    # ---------------------------------------------------------------------------------
    # gyrA — fluoroquinolone TARGET ALTERATION (ARO:3003292, "fluoroquinolone resistant
    # gyrA"). The first family here that does NOT inactivate its drug: the determinant is
    # the drug's target, and resistance comes from substitutions in the QRDR that lower
    # the affinity of the gyrase–DNA complex for the quinolone. So it is also the first
    # family to use `extra_nodes`/`extra_edges` — see the note in `promoted_graph`.
    #
    # NEXT_TASKS.md said of these drafts that "no shared family config fits — needs
    # per-gene evidence". For gyrA that is wrong, and measurably so: 24 of the 30 gyrA
    # drafts are is_a descendants of ARO:3003292 and share ONE mechanism. What is genuinely
    # per-organism is the RESIDUE NUMBERING, not the mechanism — hence the frame caveat
    # carried on the QRDR node rather than a residue node per record.
    "ARO:3003292": {
        "curated": "2026-08-05T00:00:00Z",
        "reference": "PMID:24576155",       # Aldred, Kerns & Osheroff 2014, Biochemistry
        "mech": {"ARO:3000212": _FQ_AFFINITY},
        "mech_res": _FQ_AFFINITY,
        "det_res": "the amino acids that most frequently are associated with quinolone resistance are Ser83 (based on E. coli GyrA numbering) and an acidic residue four amino acids downstream",
        "res_drug": _FQ_AFFINITY,
        "note": "Target alteration, not drug inactivation: GyrA is the quinolone's target, and QRDR substitutions reduce drug binding to the gyrase-DNA cleavage complex.",
        "protein_traits": {
            "primary_key": "domain",
            "domain": ("Pfam:PF00521", "DNA gyrase/topoisomerase IV, subunit A domain (carries the QRDR)", "DOMAIN",
                       "This entry represents a domain found in type IIA topoisomerases, such as bacterial DNA topoisomerase IV (C subunit, ParC), bacterial DNA gyrases (A subunit, GyrA), and mammalian DNA toposiomerases II."),
            "part_pred": "part of (the subunit-A domain of this determinant)",
            "part_note": "KB trait record Pfam:PF00521; snippet is the InterPro:IPR002205 abstract that record's definition is taken from, not this repo's prose.",
            # deliberately no `fold` and no `enables_mech`: see the round-18 report.
        },
        # the QRDR label says "substituted in this determinant" because the edge below
        # asserts that this node negatively regulates cleavage-complex formation, and the
        # evidence is about MUTATION of these residues, not the region as such.
        "extra_nodes": _fq_shared_nodes(
            "quinolone resistance-determining region (QRDR) of GyrA, substituted in this determinant",
            "GyrA residues 67-106, Ser83 and the acidic residue four positions downstream being the most frequently substituted. Positions are stated in the E. coli GyrA frame; the equivalent positions differ per organism (e.g. Ala90/Asp94 in M. tuberculosis), so no per-record residue node is asserted. Ungrounded: no ontology term denotes the QRDR.",),
        "extra_edges": [
            {"subject": "qrdr", "object": "domain",
             "predicate": "part of (the QRDR lies in the subunit-A domain)", "predicate_id": "BFO:0000050",
             "description": "The QRDR is the N-terminal GyrA region in which quinolone-resistance substitutions occur.",
             "evidence": [
                 {"reference": "PMID:2168148",
                  "snippet": "quinolone resistance was caused by a point mutation within the region between amino acids 67 and 106, especially in the vicinity of amino acid 83, of the GyrA protein",
                  "notes": "Yoshida et al. 1990, the paper that defined the QRDR; cited by these ARO records themselves."},
                 {"reference": "InterPro:IPR002205", "snippet": _IPR_A_SUBUNIT,
                  "notes": "Places the N-terminal GyrA region inside this domain entry. The containment of residues 67-106 in it is an inference FROM THESE TWO SOURCES TOGETHER, not a single asserted statement."},
             ]},
        ] + _fq_shared_edges([
            {"reference": "PMID:24576155", "snippet": _FQ_AFFINITY,
             "notes": "Aldred 2014. Mutation of the QRDR serine or the acidic residue, which together form the water-metal ion bridge to the drug."},
        ]),
    },
    # ---------------------------------------------------------------------------------
    # parC — fluoroquinolone (ARO:3000619). ParC is topoisomerase IV's HOMOLOGUE OF GyrA,
    # so it reuses gyrA's domain node (Pfam:PF00521) and the same water-metal ion bridge
    # result — which is legitimate only because Aldred states the homology outright and
    # because the affinity sentence names "gyrase OR topoisomerase IV".
    "ARO:3000619": {
        "curated": "2026-08-05T00:00:00Z",
        "reference": "PMID:24576155",
        "mech": {"ARO:3000212": _FQ_AFFINITY},
        "mech_res": _FQ_AFFINITY,
        "det_res": "Mutations were found in parC that encoded Thr57-Ser, Thr66-Ile, and Ser80-Arg substitutions.",
        "res_drug": _FQ_AFFINITY,
        "note": "Target alteration. ParC is the topoisomerase IV subunit homologous to GyrA and carries the equivalent QRDR.",
        # ARO:3003702 is "Pseudomonas aeruginosa gyrA AND parC conferring resistance to
        # fluoroquinolones" — a determinant naming BOTH subunits, sitting under the parC
        # family. Both are A subunits so the domain node would be right, but the QRDR node
        # would be labelled ParC-only and the record is about two QRDRs. It needs a graph
        # with one QRDR node per subunit, which is a different config, not this one.
        "exclude": ("ARO:3003702",),
        "protein_traits": {
            "primary_key": "domain",
            "domain": ("Pfam:PF00521", "DNA gyrase/topoisomerase IV, subunit A domain (carries the QRDR)", "DOMAIN",
                       "This entry represents a domain found in type IIA topoisomerases, such as bacterial DNA topoisomerase IV (C subunit, ParC), bacterial DNA gyrases (A subunit, GyrA), and mammalian DNA toposiomerases II."),
            "part_pred": "part of (the subunit-A domain of this determinant)",
            "part_note": "KB trait record Pfam:PF00521; its InterPro:IPR002205 abstract names ParC explicitly as a member.",
        },
        "extra_nodes": _fq_shared_nodes(
            "quinolone resistance-determining region (QRDR) of ParC, substituted in this determinant",
            "The topoisomerase IV counterpart of the GyrA QRDR: Ser80 and the acidic residue four positions downstream in the E. coli ParC frame (Ser84/Glu88 in A. baumannii topoisomerase IV). Positions differ per organism, so no per-record residue node is asserted. Ungrounded: no ontology term denotes the QRDR.",),
        "extra_edges": [
            {"subject": "qrdr", "object": "domain",
             "predicate": "part of (the QRDR lies in the subunit-A domain)", "predicate_id": "BFO:0000050",
             "description": "ParC is topoisomerase IV's homologue of GyrA, so its QRDR sits in the same subunit-A domain entry.",
             "evidence": [
                 {"reference": "PMID:24576155", "snippet": _FQ_SUBUNITS,
                  "notes": "Aldred 2014 states the GyrA/ParC subunit homology this reuse depends on."},
                 {"reference": "PMID:15388468",
                  "snippet": "Mutations were found in parC that encoded Thr57-Ser, Thr66-Ile, and Ser80-Arg substitutions.",
                  "notes": "Eaves et al. 2004, Salmonella enterica: the parC QRDR substitutions themselves."},
             ]},
        ] + _fq_shared_edges([
            {"reference": "PMID:24576155", "snippet": _FQ_AFFINITY,
             "notes": "Aldred 2014. The sentence names topoisomerase IV alongside gyrase, so it applies to ParC directly rather than by analogy."},
            {"reference": "PMID:24576155",
             "snippet": "In A. baumannii topoisomerase IV, these residues are Ser84 and Glu88, respectively.",
             "notes": "Aldred 2014, identifying the water-metal ion bridge pair in a topoisomerase IV A subunit."},
        ]),
    },
    # ---------------------------------------------------------------------------------
    # gyrB — fluoroquinolone (ARO:3000864). A DIFFERENT SUBUNIT and a different story: the
    # B subunit carries the ATPase and TOPRIM domains, NOT the active-site tyrosine and NOT
    # the water-metal ion bridge serine/acidic pair. So it must not reuse gyrA's domain node
    # or gyrA's affinity evidence — citing the A-subunit experiment on a gyrB record would
    # be citing the wrong experiment. Its QRDR and its evidence are its own.
    "ARO:3000864": {
        "curated": "2026-08-05T00:00:00Z",
        "reference": "PMID:22290942",       # Pantel et al. 2012, AAC
        "mech": {"ARO:3000212": "All these substitutions are clearly implicated in FQ resistance, underlining the presence of a hot spot region housing most of the GyrB substitutions implicated in FQ resistance (residues NTE, 538 to 540)."},
        "mech_res": "All these substitutions are clearly implicated in FQ resistance, underlining the presence of a hot spot region housing most of the GyrB substitutions implicated in FQ resistance (residues NTE, 538 to 540).",
        # the substitutions (1991) and the measurement that they cause resistance (2012).
        # Two separate results, and the second is what makes this a causal edge at all.
        "det_res": [
            {"reference": "PMID:1656869",
             "snippet": "all nine type 1 mutants had a point mutation from aspartic acid to asparagine at amino acid 426 and that all four type 2 mutants had a point mutation from lysine to glutamic acid at amino acid 447",
             "notes": "Yoshida et al. 1991 identified the gyrB QRDR substitutions in quinolone-resistant E. coli mutants."},
            {"reference": "PMID:22290942",
             "snippet": "We measured FQ MICs and also DNA gyrase inhibition by FQs in order to unequivocally clarify the role of these mutations in FQ resistance.",
             "notes": "Pantel et al. 2012 reconstituted gyrase with mutant GyrB subunits and measured inhibition, so the causal step here rests on a measurement rather than on association."},
        ],
        "res_drug": "We measured FQ MICs and also DNA gyrase inhibition by FQs in order to unequivocally clarify the role of these mutations in FQ resistance.",
        "note": "Target alteration in the B subunit, which contributes the TOPRIM domain rather than the active-site tyrosine — a different route from the GyrA/ParC water-metal ion bridge.",
        "protein_traits": {
            "primary_key": "domain",
            "domain": ("Pfam:PF00204", "DNA gyrase B subunit domain (carries the GyrB QRDR)", "DOMAIN",
                       _IPR_B_SUBUNIT),
            "part_pred": "part of (the subunit-B domain of this determinant)",
            "part_note": "KB trait record Pfam:PF00204; snippet is the InterPro:IPR013506 abstract that record's definition is taken from.",
        },
        "extra_nodes": _fq_shared_nodes(
            "quinolone resistance-determining region (QRDR) of GyrB, substituted in this determinant",
            "A separate QRDR from GyrA's: Asp426 and Lys447 in the E. coli GyrB frame, extended to positions 500-540 in M. tuberculosis. These residues are NOT the water-metal ion bridge pair, which lies in the A subunit. Ungrounded: no ontology term denotes the QRDR.",),
        "extra_edges": [
            {"subject": "qrdr", "object": "domain",
             "predicate": "part of (the QRDR lies in the subunit-B domain)", "predicate_id": "BFO:0000050",
             "description": "The GyrB QRDR is a region of the B subunit distinct from the GyrA QRDR.",
             "evidence": [
                 {"reference": "PMID:1656869",
                  "snippet": "all nine type 1 mutants had a point mutation from aspartic acid to asparagine at amino acid 426 and that all four type 2 mutants had a point mutation from lysine to glutamic acid at amino acid 447",
                  "notes": "Yoshida et al. 1991, the paper that defined the gyrB QRDR in E. coli — the B-subunit counterpart of PMID:2168148."},
                 {"reference": "PMID:22290942",
                  "snippet": "These findings help us to refine the definition of GyrB QRDR, which is extended to positions 500 to 540.",
                  "notes": "Pantel et al. 2012 extend the GyrB QRDR in M. tuberculosis; the frame differs from E. coli's."},
             ]},
        ] + _fq_shared_edges([
            {"reference": "PMID:22290942",
             "snippet": "All these substitutions are clearly implicated in FQ resistance, underlining the presence of a hot spot region housing most of the GyrB substitutions implicated in FQ resistance (residues NTE, 538 to 540).",
             "notes": "Pantel et al. 2012 measured DNA gyrase inhibition by FQs with reconstituted mutant GyrB, so this is the B subunit's OWN evidence, not the A subunit's affinity result."},
        ]),
    },
    # ---------------------------------------------------------------------------------
    # parE — fluoroquinolone (ARO:3003313). Topoisomerase IV's homologue of GyrB, so it
    # takes the B-subunit shape, not gyrA's.
    "ARO:3003313": {
        "curated": "2026-08-05T00:00:00Z",
        "reference": "PMID:15388468",       # Eaves et al. 2004, AAC (Salmonella enterica)
        "mech": {"ARO:3000212": "Novel mutations were also found in parE encoding Glu453-Gly, His461-Tyr, Ala498-Thr, Val512-Gly, and Ser518-Cys."},
        "mech_res": "Novel mutations were also found in parE encoding Glu453-Gly, His461-Tyr, Ala498-Thr, Val512-Gly, and Ser518-Cys.",
        # Two sources, because parE's causal claim genuinely has two parts (#190): the
        # substitutions were OBSERVED in clinical isolates, and the MECHANISM was measured
        # on the other B subunit and carried across by a stated homology. Before #190 the
        # second part could only sit in a `notes` string.
        #
        # NOT the paper's "isolates ... were examined for mutations in the QRDR of gyrA,
        # gyrB, parC, and parE" sentence, which is METHODS and asserts nothing causal.
        "det_res": [
            {"reference": "PMID:15388468",
             "snippet": "Novel mutations were also found in parE encoding Glu453-Gly, His461-Tyr, Ala498-Thr, Val512-Gly, and Ser518-Cys.",
             "notes": "Eaves et al. 2004. ASSOCIATION from clinical isolates — the substitutions are observed in resistant Salmonella enterica, not shown to cause resistance in a reconstituted enzyme."},
            {"reference": "PMID:24576155", "snippet": _FQ_SUBUNITS,
             "notes": "The homology that carries GyrB's mechanism to ParE: Aldred 2014 states ParE is topoisomerase IV's B subunit, and the reconstituted-enzyme measurement exists for GyrB (PMID:22290942), not for ParE itself. This is the weaker of the four fluoroquinolone families and is recorded as such."},
        ],
        "res_drug": "Novel mutations were also found in parE encoding Glu453-Gly, His461-Tyr, Ala498-Thr, Val512-Gly, and Ser518-Cys.",
        "note": "Target alteration in topoisomerase IV's B subunit, the homologue of GyrB.",
        "protein_traits": {
            "primary_key": "domain",
            "domain": ("Pfam:PF00204", "DNA gyrase B / topoisomerase IV subunit B domain (carries the ParE QRDR)", "DOMAIN",
                       _IPR_B_SUBUNIT),
            "part_pred": "part of (the subunit-B domain of this determinant)",
            "part_note": "KB trait record Pfam:PF00204, the shared B-subunit domain; Aldred 2014 states the GyrB/ParE homology.",
        },
        "extra_nodes": _fq_shared_nodes(
            "quinolone resistance-determining region (QRDR) of ParE, substituted in this determinant",
            "The topoisomerase IV counterpart of the GyrB QRDR: Glu453, His461, Ala498, Val512 and Ser518 in the Salmonella enterica ParE frame. As in GyrB, these are not the water-metal ion bridge pair. Ungrounded: no ontology term denotes the QRDR.",),
        "extra_edges": [
            {"subject": "qrdr", "object": "domain",
             "predicate": "part of (the QRDR lies in the subunit-B domain)", "predicate_id": "BFO:0000050",
             "evidence": [
                 {"reference": "PMID:15388468",
                  "snippet": "Novel mutations were also found in parE encoding Glu453-Gly, His461-Tyr, Ala498-Thr, Val512-Gly, and Ser518-Cys.",
                  "notes": "Eaves et al. 2004: the parE QRDR substitutions themselves."},
                 {"reference": "PMID:24576155", "snippet": _FQ_SUBUNITS,
                  "notes": "Aldred 2014 states the GyrB/ParE subunit homology that puts ParE in the same B-subunit domain entry."},
             ]},
        ] + _fq_shared_edges([
            {"reference": "PMID:15388468",
             "snippet": "Novel mutations were also found in parE encoding Glu453-Gly, His461-Tyr, Ala498-Thr, Val512-Gly, and Ser518-Cys.",
             "notes": "Eaves et al. 2004. These are association data from clinical isolates, NOT the reconstituted-enzyme inhibition measurement available for GyrB — a weaker basis, recorded as such."},
        ]),
    },
    # KPC β-lactamase (class A serine carbapenemase) — PMID:28388065 (KPC-2 mechanism)
    "ARO:3000059": {
        "reference": "PMID:28388065",
        "mech": {
            "ARO:0001004": "KPC-2 is the most prevalent carbapenemase in the United States and it has been termed the 'versatile β-lactamase' due to its large and shallow active site, allowing it to efficiently hydrolyze virtually all β-lactam antibiotics.",
            "ARO:3000187": "The attack of Ser70 on the substrate β-lactam carbonyl results in a covalent acyl-enzyme complex. Subsequently, the catalytic water, activated by Glu166, cleaves the acyl-enzyme bond, leading to the formation of the hydrolyzed product.",
        },
        "mech_res": "The Klebsiella pneumoniae carbapenemase (KPC) class A β-lactamase poses a serious threat to nearly all β-lactam antibiotics.",
        "det_res": "The Klebsiella pneumoniae carbapenemase (KPC) class A β-lactamase poses a serious threat to nearly all β-lactam antibiotics.",
        "res_drug": "KPC-2 ... allowing it to efficiently hydrolyze virtually all β-lactam antibiotics.",
        "note": "Family-level evidence: KPC is a class A serine carbapenemase; the Ser70 acyl-enzyme mechanism is the same chemistry curated atomically in MCSA:2.",
        # Wire the mechanism through the KB's own protein-trait records (all class A
        # serine β-lactamases share the class-A active-site signature + β-lactamase
        # fold). enables_mech = the mechanism ARO id the active site carries out.
        "protein_traits": {
            "active_site": ("PROSITE:PS00146", "class A beta-lactamase active-site signature (S-x-x-K)", "MOTIF", "Beta-lactamase class-A active site"),
            "fold": ("CATH:3.40.710.10", "DD-peptidase/beta-lactamase superfamily fold", "DOMAIN", "DD-peptidase/beta-lactamase superfamily"),
            "enables_mech": "ARO:3000187",
        },
    },
    # TEM β-lactamase (class A serine) — TEM-1 = UniProtKB:P62593 = MCSA:2
    "ARO:3000014": {
        "reference": "PMID:32576842",
        "mech": {
            "ARO:0001004": "In the first acylation step, the β-lactam antibiotic forms an acyl-enzyme intermediate (ES*) with the catalytic serine residue.",
            "ARO:3000187": "In the first acylation step, the β-lactam antibiotic forms an acyl-enzyme intermediate (ES*) with the catalytic serine residue.",
        },
        "mech_res": "In the first acylation step, the β-lactam antibiotic forms an acyl-enzyme intermediate (ES*) with the catalytic serine residue.",
        "det_res": "In the first acylation step, the β-lactam antibiotic forms an acyl-enzyme intermediate (ES*) with the catalytic serine residue.",
        "res_drug": "In the first acylation step, the β-lactam antibiotic forms an acyl-enzyme intermediate (ES*) with the catalytic serine residue.",
        "note": "TEM is the archetypal class A serine β-lactamase (TEM-1 = UniProtKB:P62593 = the MCSA:2 record); Ser70 acyl-enzyme mechanism.",
        "protein_traits": {
            "active_site": ("PROSITE:PS00146", "class A beta-lactamase active-site signature (S-x-x-K)", "MOTIF", "Beta-lactamase class-A active site"),
            "fold": ("CATH:3.40.710.10", "DD-peptidase/beta-lactamase superfamily fold", "DOMAIN", "DD-peptidase/beta-lactamase superfamily"),
            "enables_mech": "ARO:3000187",
        },
    },
    # SHV β-lactamase (class A serine)
    "ARO:3000015": {
        "reference": "PMID:10539992",
        "mech": {
            "ARO:0001004": "SHV enzymes belong to the molecular class A of serine β-lactamases and share extensive functional and structural similarity with TEM β-lactamases.",
            "ARO:3000187": "SHV enzymes belong to the molecular class A of serine β-lactamases and share extensive functional and structural similarity with TEM β-lactamases.",
        },
        "mech_res": "SHV enzymes belong to the molecular class A of serine β-lactamases and share extensive functional and structural similarity with TEM β-lactamases.",
        "det_res": "SHV enzymes belong to the molecular class A of serine β-lactamases and share extensive functional and structural similarity with TEM β-lactamases.",
        "res_drug": "SHV enzymes belong to the molecular class A of serine β-lactamases and share extensive functional and structural similarity with TEM β-lactamases.",
        "note": "SHV is a class A serine β-lactamase, structurally like TEM; same Ser70 acyl-enzyme mechanism.",
        "protein_traits": {
            "active_site": ("PROSITE:PS00146", "class A beta-lactamase active-site signature (S-x-x-K)", "MOTIF", "Beta-lactamase class-A active site"),
            "fold": ("CATH:3.40.710.10", "DD-peptidase/beta-lactamase superfamily fold", "DOMAIN", "DD-peptidase/beta-lactamase superfamily"),
            "enables_mech": "ARO:3000187",
        },
    },
    # CTX-M β-lactamase (class A serine, ESBL / cefotaximase)
    "ARO:3000016": {
        "reference": "PMID:15105882",
        "mech": {
            "ARO:0001004": "The CTX-M-ases belong to the molecular class A beta-lactamases, and the enzymes are functionally characterized as extended-spectrum beta-lactamases.",
            "ARO:3000187": "The CTX-M-ases belong to the molecular class A beta-lactamases, and the enzymes are functionally characterized as extended-spectrum beta-lactamases.",
        },
        "mech_res": "The CTX-M-ases belong to the molecular class A beta-lactamases, and the enzymes are functionally characterized as extended-spectrum beta-lactamases.",
        "det_res": "The CTX-M-ases belong to the molecular class A beta-lactamases, and the enzymes are functionally characterized as extended-spectrum beta-lactamases.",
        "res_drug": "The CTX-M-ases belong to the molecular class A beta-lactamases, and the enzymes are functionally characterized as extended-spectrum beta-lactamases.",
        "note": "CTX-M is a class A serine ESBL (cefotaximase); same Ser70 acyl-enzyme mechanism.",
        "protein_traits": {
            "active_site": ("PROSITE:PS00146", "class A beta-lactamase active-site signature (S-x-x-K)", "MOTIF", "Beta-lactamase class-A active site"),
            "fold": ("CATH:3.40.710.10", "DD-peptidase/beta-lactamase superfamily fold", "DOMAIN", "DD-peptidase/beta-lactamase superfamily"),
            "enables_mech": "ARO:3000187",
        },
    },
    # OXA β-lactamase (class D serine, carbamylated-lysine mechanism)
    "ARO:3000017": {
        "reference": "PMID:16121396",
        "mech": {
            "ARO:0001004": "However, carboxylated lysines in the active sites of OXA-10 and OXA-1 beta-lactamases and the sensor domain of BlaR signal-transducer protein serve in proton transfer events required for the functions of these proteins.",
            "ARO:3000187": "However, carboxylated lysines in the active sites of OXA-10 and OXA-1 beta-lactamases and the sensor domain of BlaR signal-transducer protein serve in proton transfer events required for the functions of these proteins.",
        },
        "mech_res": "However, carboxylated lysines in the active sites of OXA-10 and OXA-1 beta-lactamases and the sensor domain of BlaR signal-transducer protein serve in proton transfer events required for the functions of these proteins.",
        "det_res": "However, carboxylated lysines in the active sites of OXA-10 and OXA-1 beta-lactamases and the sensor domain of BlaR signal-transducer protein serve in proton transfer events required for the functions of these proteins.",
        "res_drug": "However, carboxylated lysines in the active sites of OXA-10 and OXA-1 beta-lactamases and the sensor domain of BlaR signal-transducer protein serve in proton transfer events required for the functions of these proteins.",
        "note": "OXA is a class D serine β-lactamase; catalysis uses a carbamylated (carboxylated) active-site lysine.",
        "protein_traits": {
            "active_site": ("PROSITE:PRU10103", "class D beta-lactamase active-site (carbamylated Lys)", "MOTIF", "Beta-lactamase class-D active site"),
            "fold": ("CATH:3.40.710.10", "DD-peptidase/beta-lactamase superfamily fold", "DOMAIN", "DD-peptidase/beta-lactamase superfamily"),
            "enables_mech": "ARO:3000187",
        },
    },
    # qnr — quinolone target protection (pentapeptide-repeat protein; no matching CATH fold record)
    "ARO:3000419": {
        "reference": "PMID:21227918",
        "mech": {"ARO:0001003": "Plasmid genes qnrA, qnrB, qnrC, qnrD, qnrS, and qnrVC code for proteins of the pentapeptide repeat family that protects DNA gyrase and topoisomerase IV from quinolone inhibition."},
        "mech_res": "Plasmid genes qnrA, qnrB, qnrC, qnrD, qnrS, and qnrVC code for proteins of the pentapeptide repeat family that protects DNA gyrase and topoisomerase IV from quinolone inhibition.",
        "det_res": "Plasmid genes qnrA, qnrB, qnrC, qnrD, qnrS, and qnrVC code for proteins of the pentapeptide repeat family that protects DNA gyrase and topoisomerase IV from quinolone inhibition.",
        "res_drug": "Plasmid genes qnrA, qnrB, qnrC, qnrD, qnrS, and qnrVC code for proteins of the pentapeptide repeat family that protects DNA gyrase and topoisomerase IV from quinolone inhibition.",
        "note": "qnr is a pentapeptide-repeat protein; target protection of DNA gyrase/topoisomerase IV from fluoroquinolones.",
        "protein_traits": {
            "primary_key": "domain",
            "part_pred": "part of (domain of the protein)",
            "enable_pred": "enables (target protection)",
            "part_note": "KB trait: the pentapeptide-repeat domain that mediates gyrase protection.",
            "fold_note": "KB trait: the pentapeptide-repeat (Qnr/MfpA right-handed β-helix, Rfr) fold.",
            "enable_note": "The pentapeptide-repeat domain protects DNA gyrase/topoisomerase IV from quinolones.",
            "domain": ("Pfam:PF00805", "pentapeptide-repeat domain", "DOMAIN", "Pentapeptide repeats (8 copies)"),
            "fold": ("ECOD:T.207.9.1", "pentapeptide-repeat (right-handed β-helix) fold", "DOMAIN", "Pentapeptide repeats"),
            "enables_mech": "ARO:0001003",
        },
    },
    # MCR — phosphoethanolamine transferase; lipid A charge alteration → colistin resistance
    "ARO:3004268": {
        "reference": "PMID:27958270",
        "mech": {"ARO:3003588": "MCR-1 is a phosphoethanolamine (pEtN) transferase that modifies the pEtN moiety of lipid A, conferring resistance to colistin."},
        "mech_res": "MCR-1 is a phosphoethanolamine (pEtN) transferase that modifies the pEtN moiety of lipid A, conferring resistance to colistin.",
        "det_res": "MCR-1 is a phosphoethanolamine (pEtN) transferase that modifies the pEtN moiety of lipid A, conferring resistance to colistin.",
        "res_drug": "MCR-1 is a phosphoethanolamine (pEtN) transferase that modifies the pEtN moiety of lipid A, conferring resistance to colistin.",
        "note": "MCR is a phosphoethanolamine transferase; it modifies lipid A (cell-surface charge alteration) to reduce colistin binding.",
        "protein_traits": {
            "primary_key": "domain",
            "part_pred": "part of (catalytic domain of the protein)",
            "enable_pred": "enables (lipid A modification)",
            "part_note": "KB trait: the phosphoethanolamine-transferase catalytic domain.",
            "fold_note": "KB trait: the alkaline-phosphatase/sulfatase superfamily fold.",
            "enable_note": "The transferase domain adds phosphoethanolamine to lipid A.",
            "domain": ("InterPro:IPR058130", "phosphoethanolamine transferase C-terminal domain", "DOMAIN", "Phosphoethanolamine transferase, C-terminal domain"),
            "fold": ("CATH:3.40.720.10", "alkaline phosphatase / sulfatase superfamily fold", "DOMAIN", "Alkaline Phosphatase, subunit A"),
            "enables_mech": "ARO:3003588",
        },
    },
    # MFS antibiotic efflux pump (major facilitator superfamily)
    "ARO:0010002": {
        "reference": "PMID:38974671",
        "mech": {"ARO:0010000": "The antimicrobial antiport transport cycle in bacteria is driven by the ion-motive force, an energy mode associated with changes in transporter conformations and gating during efflux across the membrane."},
        "mech_res": "The antimicrobial antiport transport cycle in bacteria is driven by the ion-motive force, an energy mode associated with changes in transporter conformations and gating during efflux across the membrane.",
        "det_res": "The antimicrobial antiport transport cycle in bacteria is driven by the ion-motive force, an energy mode associated with changes in transporter conformations and gating during efflux across the membrane.",
        "res_drug": "The antimicrobial antiport transport cycle in bacteria is driven by the ion-motive force, an energy mode associated with changes in transporter conformations and gating during efflux across the membrane.",
        "note": "MFS antibiotic efflux pump; ion-motive-force-driven drug antiport across the membrane.",
        "protein_traits": {
            "primary_key": "domain",
            "part_pred": "part of (domain of the protein)",
            "enable_pred": "enables (drug efflux)",
            "part_note": "KB trait: the MFS transporter domain.",
            "fold_note": "KB trait: the MFS general substrate transporter fold.",
            "enable_note": "The MFS domain carries out ion-motive-force-driven drug efflux.",
            "domain": ("Pfam:PF07690", "major facilitator superfamily (MFS) transporter domain", "DOMAIN", "Major Facilitator Superfamily"),
            "fold": ("CATH:1.20.1250.20", "MFS general substrate transporter fold", "DOMAIN", "MFS general substrate transporter like domains"),
            "enables_mech": "ARO:0010000",
        },
    },
    # RND antibiotic efflux pump (resistance-nodulation-cell division; AcrB/MexB-type)
    "ARO:0010004": {
        "reference": "PMID:19166984",
        "mech": {"ARO:0010000": "The inner membrane component AcrB, a member of the Resistance Nodulation cell Division (RND) family, is the major site for substrate recognition and energy transduction of the entire tripartite system."},
        "mech_res": "The inner membrane component AcrB, a member of the Resistance Nodulation cell Division (RND) family, is the major site for substrate recognition and energy transduction of the entire tripartite system.",
        "det_res": "The inner membrane component AcrB, a member of the Resistance Nodulation cell Division (RND) family, is the major site for substrate recognition and energy transduction of the entire tripartite system.",
        "res_drug": "The inner membrane component AcrB, a member of the Resistance Nodulation cell Division (RND) family, is the major site for substrate recognition and energy transduction of the entire tripartite system.",
        "note": "RND efflux pump (AcrB/MexB-type); proton-motive-force-driven drug efflux via a tripartite system.",
        "protein_traits": {
            "primary_key": "domain",
            "part_pred": "part of (domain of the protein)",
            "enable_pred": "enables (drug efflux)",
            "part_note": "KB trait: the RND (AcrB/AcrD/AcrF) transporter domain.",
            "fold_note": "KB trait: the AcrB pore-domain fold.",
            "enable_note": "The RND transporter domain carries out proton-motive-force-driven drug efflux.",
            "domain": ("Pfam:PF00873", "RND transporter domain (AcrB/AcrD/AcrF family)", "DOMAIN", "AcrB/AcrD/AcrF family"),
            "fold": ("CATH:3.30.70.1430", "AcrB pore-domain fold", "DOMAIN", "Multidrug efflux transporter AcrB pore domain"),
            "enables_mech": "ARO:0010000",
        },
    },
}

# Class C serine β-lactamases (AmpC cephalosporinases) — same fold as class A/D, a
# distinct class-C active-site signature; one shared config across the 4 families.
_AMPC = ("AmpC β-lactamases are clinically important cephalosporinases encoded on the "
         "chromosomes of many of the Enterobacteriaceae and a few other organisms, where "
         "they mediate resistance to cephalothin, cefazolin, cefoxitin, most penicillins, "
         "and β-lactamase inhibitor-β-lactam combinations.")


def _classc(family: str) -> dict:
    return {
        "reference": "PMID:19136439",
        "mech": {"ARO:0001004": _AMPC, "ARO:3000187": _AMPC},
        "mech_res": _AMPC, "det_res": _AMPC, "res_drug": _AMPC,
        "note": f"{family} is a class C serine β-lactamase (AmpC cephalosporinase); Ser64 acyl-enzyme mechanism.",
        "protein_traits": {
            "active_site": ("PROSITE:PRU10102", "class C beta-lactamase active-site signature (Ser64 S-x-x-K)", "MOTIF", "Beta-lactamase class-C active site"),
            "fold": ("CATH:3.40.710.10", "DD-peptidase/beta-lactamase superfamily fold", "DOMAIN", "DD-peptidase/beta-lactamase superfamily"),
            "enables_mech": "ARO:3000187",
            "part_note": "KB trait: the class-C active-site signature carried by this determinant.",
        },
    }


for _fam, _name in [("ARO:3005459", "ADC"), ("ARO:3000098", "PDC"),
                    ("ARO:3000072", "ACT"), ("ARO:3000069", "CMY")]:
    FAMILY_SNIPPETS[_fam] = _classc(_name)


def _domfam(ref, snip, note, dom, fold, em, enable_pred, part_note, fold_note, enable_note):
    """A domain-primary family config (non-β-lactamase). dom/fold are
    (CURIE, node-label, node-type, snippet) 4-tuples; fold may be None."""
    pt = {"primary_key": "domain", "part_pred": "part of (catalytic domain of the protein)",
          "enable_pred": enable_pred, "part_note": part_note, "enable_note": enable_note,
          "domain": dom, "enables_mech": em}
    if fold:
        pt["fold"] = fold
        pt["fold_note"] = fold_note
    return {"reference": ref, "mech": {em: snip}, "mech_res": snip, "det_res": snip,
            "res_drug": snip, "note": note, "protein_traits": pt}


# Aminoglycoside-modifying enzymes (inactivation) + van/sul/dfr (target remodelling)
FAMILY_SNIPPETS["ARO:3000121"] = _domfam(  # AAC — acetyltransferase
    "PMID:26818562",
    "N-Acetyltransferases transfer an acetyl group from acetyl-CoA to a large array of substrates, from small molecules such as aminoglycoside antibiotics to macromolecules.",
    "AAC — aminoglycoside N-acetyltransferase; inactivates aminoglycosides by acetyl-CoA-dependent acetylation.",
    ("InterPro:IPR000182", "GNAT acetyltransferase domain", "DOMAIN", "GNAT domain"),
    ("CATH:3.40.630", "acyl-CoA N-acyltransferase (GNAT) fold", "DOMAIN", "Aminopeptidase"),
    "ARO:3000106", "enables (antibiotic acetylation)",
    "KB trait: the GNAT acetyltransferase domain.", "KB trait: the GNAT structural fold.",
    "The GNAT domain transfers an acetyl group onto the aminoglycoside, inactivating it.")
FAMILY_SNIPPETS["ARO:3000114"] = _domfam(  # APH — phosphotransferase
    "PMID:9200607",
    "Structure of an enzyme required for aminoglycoside antibiotic resistance reveals homology to eukaryotic protein kinases.",
    "APH — aminoglycoside O-phosphotransferase; inactivates aminoglycosides by ATP-dependent phosphorylation (protein-kinase-like fold).",
    ("Pfam:PF01636", "aminoglycoside phosphotransferase domain", "DOMAIN", "Phosphotransferase enzyme family"),
    ("CATH:3.90.1200", "aminoglycoside phosphotransferase (protein-kinase-like) fold", "DOMAIN", "Aminoglycoside 3'-phosphotransferase; Chain: A, domain 2"),
    "ARO:3000105", "enables (antibiotic phosphorylation)",
    "KB trait: the aminoglycoside-phosphotransferase domain.", "KB trait: the protein-kinase-like fold.",
    "The phosphotransferase domain transfers the ATP γ-phosphate onto the aminoglycoside.")
FAMILY_SNIPPETS["ARO:3000218"] = _domfam(  # ANT — nucleotidyltransferase
    "PMID:25564464",
    "ANT(2″)-Ia confers resistance by magnesium-dependent transfer of a nucleoside monophosphate (AMP) to the 2″-hydroxyl of aminoglycoside substrates containing a 2-deoxystreptamine core.",
    "ANT — aminoglycoside nucleotidyltransferase; inactivates aminoglycosides by adenylylation.",
    ("Pfam:PF01909", "nucleotidyltransferase domain", "DOMAIN", "Nucleotidyltransferase domain"),
    ("CATH:3.30.460", "DNA-polymerase-β-like nucleotidyltransferase fold", "DOMAIN", "Beta Polymerase; domain 2"),
    "ARO:3000107", "enables (antibiotic nucleotidylation)",
    "KB trait: the nucleotidyltransferase domain.", "KB trait: the nucleotidyltransferase fold.",
    "The nucleotidyltransferase domain adenylylates the aminoglycoside.")
FAMILY_SNIPPETS["ARO:3002978"] = _domfam(  # van — D-Ala-D-Lac ligase (target alteration)
    "PMID:10908650",
    "D-alanine-D-lactate ligase is directly responsible for the biosynthesis of alternate cell-wall precursors in bacteria that are resistant to the glycopeptide antibiotic vancomycin.",
    "van (D-Ala-D-Lac ligase) — target alteration: remodels the peptidoglycan D-Ala-D-Ala terminus to D-Ala-D-Lac so vancomycin can no longer bind.",
    ("Pfam:PF07478", "D-Ala-D-Ala/D-Lac ligase domain (C-terminus)", "DOMAIN", "D-ala D-ala ligase C-terminus"),
    ("CATH:3.30.470", "ATP-grasp fold", "DOMAIN", "D-amino Acid Aminotransferase; Chain A, domain 1"),
    "ARO:3000213", "enables (cell-wall precursor remodelling)",
    "KB trait: the D-Ala-D-Lac ligase domain.", "KB trait: the ATP-grasp fold.",
    "The ligase synthesises D-Ala-D-Lac, altering the vancomycin target.")
FAMILY_SNIPPETS["ARO:3004238"] = _domfam(  # sul — sulfonamide-resistant DHPS (target replacement)
    "PMID:37419898",
    "We determine crystal structures of the most common Sul enzyme types (Sul1, Sul2 and Sul3) in multiple ligand-bound states, revealing a substantial reorganization of their pABA-interaction region relative to the corresponding region of DHPS.",
    "sul — sulfonamide-resistant dihydropteroate synthase; a drug-insensitive DHPS that replaces the sulfonamide target enzyme.",
    ("Pfam:PF00809", "pterin-binding (DHPS) domain", "DOMAIN", "Pterin binding enzyme"),
    ("CATH:3.20.20", "TIM-barrel fold", "DOMAIN", "TIM Barrel"),
    "ARO:0001002", "enables (drug-insensitive target enzyme)",
    "KB trait: the pterin-binding DHPS domain.", "KB trait: the TIM-barrel fold.",
    "The sulfonamide-insensitive DHPS replaces the drug-sensitive folate-pathway enzyme.")
FAMILY_SNIPPETS["ARO:3001218"] = _domfam(  # dfr — trimethoprim-resistant DHFR (target replacement)
    "PMID:35562546",
    "Trimethoprim resistance in Enterobacteriaceae occurs almost exclusively through the acquisition of plasmid-associated dfr genes that encode intrinsically insensitive DHFR enzymes.",
    "dfr — trimethoprim-resistant dihydrofolate reductase; a drug-insensitive DHFR that replaces the trimethoprim target enzyme.",
    ("Pfam:PF00186", "dihydrofolate reductase domain", "DOMAIN", "Dihydrofolate reductase"),
    ("CATH:3.40.430", "dihydrofolate reductase fold", "DOMAIN", "Dihydrofolate Reductase, subunit A"),
    "ARO:0001002", "enables (drug-insensitive target enzyme)",
    "KB trait: the dihydrofolate-reductase domain.", "KB trait: the DHFR fold.",
    "The trimethoprim-insensitive DHFR replaces the drug-sensitive enzyme.")


# Broad class/family nodes — clear the long tail (remaining class A/C variants, all
# metallo-β-lactamases IMP/VIM/NDM/GOB/BlaB, and the Erm methyltransferases). Already
# hand-curated / previously-promoted members are skipped by the curation-signature guard.
def _classa(family):
    _s = "In the first acylation step, the β-lactam antibiotic forms an acyl-enzyme intermediate (ES*) with the catalytic serine residue."
    return {"reference": "PMID:32576842", "mech": {"ARO:0001004": _s, "ARO:3000187": _s},
            "mech_res": _s, "det_res": _s, "res_drug": _s,
            "note": f"{family} — class A serine β-lactamase; Ser70 acyl-enzyme mechanism.",
            "protein_traits": {
                "active_site": ("PROSITE:PS00146", "class A beta-lactamase active-site signature (S-x-x-K)", "MOTIF", "Beta-lactamase class-A active site"),
                "fold": ("CATH:3.40.710.10", "DD-peptidase/beta-lactamase superfamily fold", "DOMAIN", "DD-peptidase/beta-lactamase superfamily"),
                "enables_mech": "ARO:3000187",
                "part_note": "KB trait: the class-A active-site signature carried by this determinant."}}


FAMILY_SNIPPETS["ARO:3000078"] = _classa("class A beta-lactamase")
FAMILY_SNIPPETS["ARO:3000076"] = _classc("class C beta-lactamase")
FAMILY_SNIPPETS["ARO:3000004"] = _domfam(  # class B metallo-β-lactamase (broad)
    "PMID:33199283",
    "MBLs are one class of β-lactamases (Ambler class B), requiring divalent zinc ions for their β-lactamase activity.",
    "class B metallo-β-lactamase — Zn(II)-dependent hydrolysis of β-lactams (incl. carbapenems); no covalent acyl-enzyme.",
    ("Pfam:PF00753", "metallo-beta-lactamase superfamily domain", "DOMAIN", "Metallo-beta-lactamase superfamily"),
    ("CATH:3.60.15.30", "metallo-beta-lactamase domain fold", "DOMAIN", "Metallo-beta-lactamase domain"),
    "ARO:3000203", "enables (Zn-dependent beta-lactam hydrolysis)",
    "KB trait: the metallo-beta-lactamase domain.", "KB trait: the MBL structural fold.",
    "The di-zinc metallo-beta-lactamase domain hydrolyses the beta-lactam ring.")
FAMILY_SNIPPETS["ARO:3000560"] = _domfam(  # Erm 23S rRNA methyltransferase (broad)
    "PMID:31601908",
    "ErmE is a methyltransferase (MTase) from Saccharopolyspora erythraea that dimethylates A2058 in 23S rRNA",
    "Erm — 23S rRNA adenine dimethyltransferase; target alteration (methylates A2058) conferring MLSB resistance.",
    ("Pfam:PF00398", "rRNA adenine dimethyltransferase domain (RrnaAD)", "DOMAIN", "Ribosomal RNA adenine dimethylase"),
    None,
    "ARO:3000211", "enables (23S rRNA A2058 methylation)",
    "KB trait: the RrnaAD methyltransferase domain.", None,
    "The methyltransferase domain dimethylates 23S rRNA A2058, altering the drug target.")
FAMILY_SNIPPETS["ARO:3004469"] = _domfam(  # ABC-F ribosomal protection protein
    "PMID:27006457",
    "such proteins are capable of displacing antibiotic from the ribosome in vitro",
    "ABC-F ribosomal protection protein — an ABC-family ATPase that binds the ribosome and displaces the antibiotic (target protection).",
    ("Pfam:PF00005", "ABC transporter ATP-binding domain", "DOMAIN", "ABC transporter"),
    ("CATH:3.40.50.300", "P-loop NTPase fold (ABC ATPase nucleotide-binding domain)", "DOMAIN", "P-loop containing nucleotide triphosphate hydrolases"),
    "ARO:0001003", "enables (ribosomal protection)",
    "KB trait: the ABC transporter ATP-binding domain.", "KB trait: the ABC ATPase fold.",
    "The ABC-F ATPase binds the ribosome and displaces the bound antibiotic.")
FAMILY_SNIPPETS["ARO:3000122"] = _domfam(  # chloramphenicol acetyltransferase (CAT)
    "PMID:1364583",
    "CAT, which catalyses O-acetylation of the antibiotic, using acetyl-CoA as the acyl donor.",
    "Chloramphenicol acetyltransferase (CAT) — inactivates chloramphenicol by acetyl-CoA-dependent O-acetylation.",
    ("Pfam:PF00302", "chloramphenicol acetyltransferase domain", "DOMAIN", "Chloramphenicol acetyltransferase"),
    ("CATH:3.30.559", "chloramphenicol acetyltransferase fold", "DOMAIN", "Chloramphenicol Acetyltransferase"),
    "ARO:3000106", "enables (chloramphenicol acetylation)",
    "KB trait: the CAT domain.", "KB trait: the CAT fold.",
    "The CAT domain O-acetylates chloramphenicol, inactivating it.")
FAMILY_SNIPPETS["ARO:3000133"] = _domfam(  # fosfomycin thiol transferase (FosA)
    "PMID:15741169",
    "The metalloglutathione transferase FosA catalyzes the conjugation of glutathione to carbon-1 of the antibiotic fosfomycin, rendering it ineffective as an antibacterial drug.",
    "Fosfomycin thiol transferase (FosA) — inactivates fosfomycin by opening its epoxide ring via glutathione conjugation.",
    ("Pfam:PF00903", "glyoxalase / VOC-superfamily domain", "DOMAIN", "Glyoxalase/Bleomycin resistance protein/Dioxygenase superfamily"),
    ("CATH:3.10.180", "VOC / glyoxalase superfamily fold", "DOMAIN", "2,3-Dihydroxybiphenyl 1,2-Dioxygenase; domain 1"),
    "ARO:3000125", "enables (fosfomycin epoxide opening)",
    "KB trait: the glyoxalase/VOC domain.", "KB trait: the VOC/glyoxalase fold.",
    "The FosA domain conjugates glutathione to fosfomycin, inactivating it.")
FAMILY_SNIPPETS["ARO:3004274"] = _domfam(  # 23S rRNA methyltransferase (Cfr-type)
    "PMID:20007606",
    "The Cfr methyltransferase confers combined resistance to five classes of antibiotics that bind to the peptidyl tranferase center of bacterial ribosomes by catalyzing methylation of the C-8 position of 23S rRNA nucleotide A2503.",
    "23S rRNA methyltransferase (Cfr-type) — target alteration: methylates 23S rRNA A2503 in the peptidyl-transferase centre.",
    ("Pfam:PF04055", "radical-SAM methyltransferase domain", "DOMAIN", "Radical SAM superfamily"),
    ("CATH:3.20.20", "radical-SAM (partial TIM-barrel) fold", "DOMAIN", "TIM Barrel"),
    "ARO:3000211", "enables (23S rRNA A2503 methylation)",
    "KB trait: the radical-SAM methyltransferase domain.", "KB trait: the radical-SAM fold.",
    "The methyltransferase domain methylates 23S rRNA A2503, altering the drug target.")
FAMILY_SNIPPETS["ARO:0010001"] = _domfam(  # ATP-binding cassette (ABC) efflux pump
    "PMID:29892271",
    "Tripartite efflux pumps built around ATP-binding cassette (ABC) transporters are membrane protein machineries that perform vectorial export of drugs and virulence factors from Gram negative bacteria, using ATP-hydrolysis as energy source.",
    "ABC antibiotic efflux pump — ATP-hydrolysis-driven vectorial export of drugs across the membrane.",
    ("Pfam:PF00005", "ABC transporter ATP-binding domain", "DOMAIN", "ABC transporter"),
    ("CATH:3.40.50.300", "P-loop NTPase fold (ABC ATPase nucleotide-binding domain)", "DOMAIN", "P-loop containing nucleotide triphosphate hydrolases"),
    "ARO:0010000", "enables (ATP-driven drug efflux)",
    "KB trait: the ABC transporter ATP-binding domain.", "KB trait: the ABC ATPase fold.",
    "The ABC transporter exports the drug using ATP hydrolysis.")


def _evidence_items(spec, ref: str, note: str) -> list[dict]:
    if isinstance(spec, str):
        return [{"reference": ref, "snippet": spec, "notes": note}]
    return [{"reference": i["reference"], "snippet": i["snippet"],
             "notes": i.get("notes", note)} for i in spec]


def promoted_graph_dict(ident: str, label: str, mech: list, drug: list, names: dict,
                        cfg: dict, terms: dict | None = None) -> dict:
    """Build the curated graph as data, then let PyYAML lay it out (#194).

    This used to concatenate indented strings by hand, which drifted from the layout the
    five `build_*_causal_graphs.py` scripts produce with

        yaml.safe_dump(..., sort_keys=False, allow_unicode=True, width=100,
                       default_flow_style=False)

    and therefore from the 40,115 graphs already in the corpus. Re-promoting one KPC record
    changed 148 lines / 166 deletions with no change of content — which made re-promotion
    effectively unavailable for the ~28 families written before round 18. Same dumper, same
    settings, same layout: a re-promotion diff now shows content and nothing else.
    """
    ref = cfg["reference"]
    note = cfg.get("note", "")
    nodes = [{"node_id": "determinant", "label": label, "node_type": "PROTEIN",
              "grounding": ident}]
    for i, mid in enumerate(mech):
        nodes.append({"node_id": f"mech{i}", "label": names.get(mid, mid),
                      "node_type": "MOLECULAR_FUNCTION", "grounding": mid})
    for i, did in enumerate(drug[:D.MAX_DRUGS]):
        nodes.append({"node_id": f"drug{i}", "label": names.get(did, did),
                      "node_type": "CHEMICAL", "grounding": did})
    pt = cfg.get("protein_traits")
    if pt:
        pkey = pt.get("primary_key", "active_site")
        for key in ([pkey] + (["fold"] if "fold" in pt else [])):
            cid, lab, ntype, _ = pt[key]
            nodes.append({"node_id": key, "label": lab, "node_type": ntype,
                          "grounding": cid,
                          "description": "KB protein-trait record carrying the mechanism."})
    for n in cfg.get("extra_nodes", []):
        node = {"node_id": n["node_id"], "label": n["label"], "node_type": n["node_type"]}
        if n.get("grounding"):
            node["grounding"] = n["grounding"]
        if n.get("description"):
            node["description"] = n["description"]
        nodes.append(node)
    nodes.append({
        "node_id": "resistance", "label": "antibiotic resistance phenotype",
        "node_type": "PHENOTYPE", "grounding": "GO:0046677",
        "description": ("Resistance phenotype conferred by this determinant. Grounded to the "
                        "nearest available superclass: ARO models determinants and mechanisms "
                        "but has no term for the resistance phenotype itself.")})

    edges = []
    for i, mid in enumerate(mech):
        # Codex review: this used to fall back to `next(iter(cfg["mech"].values()))` for a
        # mechanism the config does not describe, writing ANOTHER mechanism's snippet as
        # evidence and stamping the record REVIEWED. Exactly the "correct form, false
        # content" failure #201 exists for, and invisible to every gate. 0 live cases when
        # this was measured; it now raises, and `promote()` turns that into a skip with a
        # reason rather than a silent substitution.
        if mid not in cfg["mech"]:
            raise UncoveredMechanism(mid)
        snip = cfg["mech"][mid]
        edges.append(_edge("determinant", "participates in (resistance mechanism)",
                           "RO:0000056", f"mech{i}", ref, snip, f"Family mechanism {mid}."))
        edges.append(_edge(f"mech{i}", "causally upstream of", "RO:0002411", "resistance",
                           ref, cfg["mech_res"], f"Mechanism {mid} \u2192 resistance."))
    edges.append(_edge("determinant", "causally upstream of (confers resistance)",
                       "RO:0002411", "resistance", ref, cfg["det_res"],
                       "Determinant \u2192 resistance phenotype."))
    for i, did in enumerate(drug[:D.MAX_DRUGS]):
        # `determinant -> drug`, carrying ARO's own confers_resistance_to_drug_class, is
        # the shape BOTH the auto-draft and the 6,180 records promoted before round 18
        # use. The interim `resistance -> drug` edge was this promoter's alone (#194).
        #
        # Its evidence is CARD's assertion, not the family's literature snippet, because
        # the edge says "CARD asserts this" — regenerated from the obo so it matches what
        # the older records carry rather than overwriting it with a hydrolysis quote.
        assertion = _drug_assertion(ident, did, terms) if terms else None
        d_ref, d_snip, d_note = assertion or (ref, cfg["res_drug"],
                                              f"Resistance to {names.get(did, did)}.")
        edges.append(_edge("determinant", "confers resistance to (drug class)",
                           "ARO:2000001", f"drug{i}", d_ref, d_snip, d_note,
                           description=(f"CARD asserts that this determinant confers resistance "
                                        f"to {names.get(did, did)}.")))
    if pt:
        pkey = pt.get("primary_key", "active_site")
        p_cid, _, _, p_snip = pt[pkey]
        edges.append(_edge(pkey, pt.get("part_pred", "part of (active site of the protein)"),
                           "BFO:0000050", "determinant", p_cid, p_snip,
                           pt.get("part_note", "KB trait: the class-A active-site signature "
                                               "carried by this determinant.")))
        if "fold" in pt:
            fo_cid, _, _, fo_snip = pt["fold"]
            edges.append(_edge("determinant", "member of (adopts fold)", "RO:0002350", "fold",
                               fo_cid, fo_snip,
                               pt.get("fold_note", "KB trait: the DD-peptidase/beta-lactamase "
                                                   "superfamily fold.")))
        em = pt.get("enables_mech")
        if em in mech:
            edges.append(_edge(pkey, pt.get("enable_pred", "enables (catalysis)"), "RO:0002327",
                               f"mech{mech.index(em)}", ref, cfg["mech"][em],
                               pt.get("enable_note", "The active site carries out the serine "
                                                     "beta-lactam hydrolysis mechanism.")))
    # Family-specific mechanism edges. The fixed determinant->mechanism->resistance shape
    # above was written for enzymatic INACTIVATION and cannot express other resistance
    # routes -- target alteration, precursor depletion, efflux -- where the causation runs
    # through parts of the target and complexes that shape has no place for.
    #
    # An edge whose subject or object is not among THIS record's nodes is skipped rather
    # than emitted dangling: mechanism and drug nodes come from each member's own ARO
    # relations, so a family member need not carry the one an edge names.
    defined = {n["node_id"] for n in nodes}
    for e in cfg.get("extra_edges", []):
        if e["subject"] not in defined or e["object"] not in defined:
            continue
        edge = {"subject": e["subject"], "predicate": e["predicate"],
                "predicate_id": e["predicate_id"], "object": e["object"]}
        if e.get("description"):
            edge["description"] = e["description"]
        edge["evidence"] = [{"reference": i["reference"], "snippet": i["snippet"],
                             "notes": i.get("notes", "")} for i in e["evidence"]]
        edges.append(edge)

    graph = {
        "graph_id": "resistance",
        "title": f"{label} \u2192 mechanism \u2192 resistance (curated from ARO relations + literature)",
        "description": (f"Curated resistance-causation graph (promoted from the ARO auto-draft). "
                        f"Determinant \u2192 inherited mechanism \u2192 resistance phenotype \u2192 drug "
                        f"classes; edges carry the family's verbatim literature evidence "
                        f"({ref}). {note}"),
        "nodes": nodes,
        "edges": edges,
    }
    return graph


def promoted_graph(*args, **kwargs) -> list[str]:
    """The graph as YAML lines — `causal_graphs:` with this one graph under it."""
    return _dump({"causal_graphs": [promoted_graph_dict(*args, **kwargs)]})


def _dump(obj) -> list[str]:
    return yaml.safe_dump(obj, sort_keys=False, allow_unicode=True, width=100,
                          default_flow_style=False).splitlines()


# ---------------------------------------------------------------------------------------
# `--verify`: check a family config's claims against the records it would promote (#201).
#
# Ancestry says the records are RELATED. It does not say the config's MECHANISM is true of
# each one, and three rounds shipped or nearly shipped graphs where it was not:
#
#   round 19  gyrB/parE would have reused gyrA's water-metal ion bridge result -- wrong
#             subunit, wrong domain, wrong residues.
#   round 19  ARO:3003702 is "gyrA AND parC"; the parC config gave it a ParC-only QRDR.
#   round 22  the vanR/vanS config's downstream is vanH + vanX; six clusters have neither.
#             12 records shipped asserting an operon composition false for their cluster.
#
# Every gate passed on all three: schema-valid, fully grounded, every edge snippet-cited.
# Correct form, false content -- so the check has to be about CONTENT, per record.
#
# Two checks, because the three failures are two different kinds:
#
#   * RESOLVABLE  -- every KB CURIE a config grounds a node to must exist as a record.
#                    Catches typos and stale identifiers. Cheap and fully general.
#   * PRECONDITION -- a per-family predicate over each candidate record. The vanR case is
#                    a query, not a judgement: "does this record's cluster contain the
#                    genes my downstream nodes name?" is answerable from the corpus.
#                    Configs are Python, so this is a callable, and a failing record is
#                    SKIPPED with its reason printed rather than silently promoted.
# Prefixes that ARE record identifiers in data/traits. `UniProtKB:` is deliberately NOT
# here: UniProt accessions appear in `canonical_examples`, never as a record identifier
# (UniProt-seeded records are minted as `proteintraitsmech:UNIPROTKB_…`), so including it
# would report a false UNRESOLVED for any config that grounded a node to a protein.
KB_PREFIXES = ("ARO:", "Pfam:", "NCBIfam:", "PROSITE:", "CATH:", "InterPro:", "CDD:",
               "MEROPS:", "TED:", "GO:")


def config_curies(cfg: dict) -> set[str]:
    """Every KB CURIE this config grounds a node to, or cites as a reference."""
    out = set()
    pt = cfg.get("protein_traits") or {}
    for key, val in pt.items():
        if isinstance(val, tuple) and val and isinstance(val[0], str):
            out.add(val[0])
    for n in cfg.get("extra_nodes", []):
        if n.get("grounding"):
            out.add(n["grounding"])
    for e in cfg.get("extra_edges", []):
        for ev in e.get("evidence", []):
            out.add(ev["reference"])
    # standard-edge snippets too: since #190 any of them may be a list of evidence items,
    # and one of those can cite a KB record rather than a paper — vanH's membership edge
    # cites NCBIfam:NF000492. Scanning only extra_edges would miss that whole shape.
    for field in ("mech_res", "det_res", "res_drug"):
        out.update(_field_references(cfg.get(field)))
    for val in (cfg.get("mech") or {}).values():
        out.update(_field_references(val))
    return {c for c in out if c.startswith(KB_PREFIXES)}


def _field_references(spec) -> set[str]:
    if isinstance(spec, list):
        return {i["reference"] for i in spec if isinstance(i, dict) and "reference" in i}
    return set()


_IDENTIFIER_INDEX: set[str] | None = None


def record_identifiers(root: Path) -> set[str]:
    """Every record identifier in the corpus, read from each file's first line.

    `identifier:` is line 1 of every trait record, so this reads one line per file rather
    than parsing 429k YAML documents. Even so it costs ~70s, which is why it is cached for
    the process and why `--verify-all` exists: 36 separate `--verify` runs would rebuild
    it 36 times and take half an hour.
    """
    global _IDENTIFIER_INDEX
    if _IDENTIFIER_INDEX is not None:
        return _IDENTIFIER_INDEX
    found = set()
    for pth in root.rglob("*.yaml"):
        with pth.open(encoding="utf-8") as fh:
            first = fh.readline()
        if first.startswith("identifier:"):
            found.add(first.split(":", 1)[1].strip().strip('"'))
    _IDENTIFIER_INDEX = found
    return found


def verify(family: str, cfg: dict, terms: dict, candidates: list) -> int:
    """Report what a config claims that its records do not support.

    Returns the count of PROBLEMS, which is deliberately not the count of everything
    printed. A precondition skip is the guard working as intended -- the vanR/vanS config
    correctly refuses 12 records every run -- so counting those as failures would leave
    `just verify-family-drafts` permanently red and therefore ignored. Only an unresolved
    CURIE is an error: it means a config grounds a node to something that is not a record.
    """
    problems = 0
    curies = config_curies(cfg)
    if curies:
        known = record_identifiers(TRAITS_ROOT)
        for c in sorted(curies):
            if c not in known:
                print(f"  UNRESOLVED  {c} is grounded/cited by {family} but is not a record")
                problems += 1
    # Codex review: a family whose ancestry yields nothing is not "verified", it is
    # unchecked — a renamed family id or a stale OBO link reads as 0 candidates, 0
    # problems, exit 0.
    if not candidates:
        print(f"  NO CANDIDATES  {family} matches no record; the family id or the OBO "
              f"ancestry is stale")
        problems += 1
    # Codex review: `exclude` was never validated. A typo in it silently protects nothing,
    # and verify still exits 0 — which is what the guard exists to prevent.
    known_idents = {c[0] for c in candidates}
    for ex in cfg.get("exclude", ()):
        if ex not in known_idents:
            print(f"  STALE EXCLUDE  {ex} is excluded by {family} but is not one of its "
                  f"candidates")
            problems += 1
    # Codex review: a candidate whose mechanism the config has no snippet for used to be
    # promoted with ANOTHER mechanism's evidence. The promotion path now refuses it, so no
    # new record can acquire one. The 1,044 already-promoted records that did are counted
    # and reported but do NOT fail the run (#203): they are a curation backlog, and a gate
    # that is permanently red is a gate nobody reads -- the same mistake as counting
    # precondition skips as failures.
    #
    # They are also not proven wrong. myrA's substituted snippet describes rRNA
    # methylation, which plausibly does support the broader ARO:0001001 target-alteration
    # class it was attached to. What is true is that nobody curated it for that id.
    uncovered_records = 0
    for ident, label, text in candidates:
        mech, _ = D.parse_relations(text)
        uncovered = [m for m in mech if m not in cfg["mech"]]
        if uncovered:
            uncovered_records += 1
            if uncovered_records <= 3:
                print(f"  uncovered mechanism  {ident} ({label}): {', '.join(uncovered)} "
                      f"has no snippet in this config")
    if uncovered_records > 3:
        print(f"  uncovered mechanism  ... and {uncovered_records - 3:,} more in {family}")
    skips = 0
    pre = cfg.get("precondition")
    if pre:
        for ident, label, text in candidates:
            reason = pre(ident, label, text)
            if reason:
                print(f"  would skip  {ident} ({label}): {reason}")
                skips += 1
    print(f"verify {family}: {len(curies)} KB CURIEs checked, {len(candidates)} candidate "
          f"records, {skips} precondition skip(s), {uncovered_records} uncovered-mechanism "
          f"record(s), {problems} problem(s)")
    return problems



def _drug_assertion(ident: str, did: str, terms: dict):
    """CARD's own `confers_resistance_to_drug_class` line, and the term it sits on.

    A variant record rarely asserts the relation itself — it inherits it from a family or
    class ancestor — so this walks `is_a` from the record upward and returns the first term
    that asserts it. Returns None if nothing in the ancestry does, in which case the caller
    falls back to the family's literature snippet.
    """
    for anc in [ident] + [a for a in E.ancestry(terms, ident) if a != ident]:
        for rel in terms.get(anc, {}).get("rel", []):
            if rel.startswith("confers_resistance_to_drug_class") and did in rel:
                return (anc, f"relationship: {rel}",
                        f"Asserted on {anc} ({terms[anc].get('name', anc)}), an is_a ancestor "
                        f"of this record's {ident}; inherited by this variant. CARD/ARO "
                        f"release in data/raw/aro/aro.obo.")
    return None


# The graph ids this promoter owns: the draft it consumes and the graph it produces.
OWNED_GRAPH_IDS = frozenset({"resistance", "resistance-draft"})


class UncoveredMechanism(Exception):
    """A candidate carries a mechanism the family config has no snippet for."""

    def __init__(self, mechanism_id: str):
        super().__init__(mechanism_id)
        self.mechanism_id = mechanism_id


def _edge(subject: str, predicate: str, predicate_id: str, obj: str, ref: str, snippet,
          note: str, description: str | None = None) -> dict:
    edge = {"subject": subject, "predicate": predicate, "predicate_id": predicate_id,
            "object": obj}
    if description:
        edge["description"] = description
    edge["evidence"] = _evidence_items(snippet, ref, note)
    return edge


# The date each family was promoted. Every `build_*_causal_graphs.py` hardcodes its round's
# date as a module constant, deliberately: a re-run must not churn timestamps. That
# convention breaks for THIS script, which is run again for every new family — one constant
# meant 6,235 records all claimed 2026-07-21, including 53 curated two weeks later (#191).
# So the date is per family, defaulting to the rounds 12–14 date the older ones really have.
LEGACY_PROMOTION = "2026-07-21T00:00:00Z"


def curation_entry(cfg: dict) -> dict:
    return {
        "timestamp": cfg.get("curated", LEGACY_PROMOTION),
        "curator": "edison-causal-graphs",
        "action": ("Promoted auto-draft to curated causal_graphs with family verbatim "
                   "snippets; SEEDED -> REVIEWED"),
        "llm_assisted": True,
    }


def curation_event(cfg: dict) -> list[str]:
    return _dump({"curation_history": [curation_entry(cfg)]})



def _candidates(family: str, terms: dict) -> list:
    """Every draft-or-promoted record whose is_a ancestry includes this family."""
    out = []
    for pth in sorted(ARO_DIR.glob("*.yaml")):
        text = pth.read_text(encoding="utf-8")
        ident_m = re.search(r'^identifier:\s*"?(ARO:[^"\s]+)"?\s*$', text, re.M)
        if not ident_m or family not in E.ancestry(terms, ident_m.group(1)):
            continue
        label_m = re.search(r'^label:\s*"?(.+?)"?\s*$', text, re.M)
        out.append((ident_m.group(1), label_m.group(1) if label_m else "", text))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--family", help="family ARO id (must be in FAMILY_SNIPPETS)")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--drafts-only", action="store_true",
                    help="accepted for compatibility and now the DEFAULT; see --repromote")
    ap.add_argument("--repromote", action="store_true",
                    help="also rewrite this promoter's own existing `resistance` graphs "
                         "(needed after a config change). Off by default: rewriting a "
                         "graph a curator may have improved is destructive, and the safe "
                         "behaviour should not depend on remembering a flag (#204)")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--verify", action="store_true",
                    help="check the config's claims against the records it would promote "
                         "(#201) and exit; writes nothing")
    ap.add_argument("--verify-all", action="store_true",
                    help="run --verify for every family in FAMILY_SNIPPETS, in one process "
                         "so the corpus index is built once; writes nothing")
    args = ap.parse_args()
    if not args.family and not args.verify_all:
        ap.error("--family is required unless --verify-all is given")
    if args.verify_all:
        terms = E.parse_obo(E.OBO)
        total = 0
        for fam in FAMILY_SNIPPETS:
            total += verify(fam, FAMILY_SNIPPETS[fam], terms, _candidates(fam, terms))
        print(f"\n--verify-all: {len(FAMILY_SNIPPETS)} families, {total} problem(s) "
              f"(precondition skips are expected and do not count)")
        return 1 if total else 0
    cfg = FAMILY_SNIPPETS.get(args.family)
    if not cfg:
        print(f"no curated snippets for {args.family}; add it to FAMILY_SNIPPETS")
        return 2
    terms = E.parse_obo(E.OBO)
    names = D.obo_names(D.OBO)

    if args.verify:
        return 1 if verify(args.family, cfg, terms, _candidates(args.family, terms)) else 0

    promoted = repromoted = skip_done = skip_nodraft = skip_excluded = 0
    for pth in sorted(ARO_DIR.glob("*.yaml")):
        text = pth.read_text(encoding="utf-8")
        ident_m = re.search(r'^identifier:\s*"?(ARO:[^"\s]+)"?\s*$', text, re.M)
        if not ident_m:
            continue
        if args.family not in E.ancestry(terms, ident_m.group(1)):
            continue
        if ident_m.group(1) in cfg.get("exclude", ()):
            # a descendant whose mechanism the family config does NOT describe. Named per
            # family rather than filtered by a rule, because the reason differs each time
            # and "why is this one not promoted" should be answerable from the config.
            skip_excluded += 1
            continue
        pre = cfg.get("precondition")
        if pre:
            # the same exclusion, DERIVED rather than listed. A hand-maintained `exclude`
            # tuple is correct only until the corpus changes under it; a predicate is
            # re-evaluated every run (#201).
            label_m = re.search(r'^label:\s*"?(.+?)"?\s*$', text, re.M)
            reason = pre(ident_m.group(1), label_m.group(1) if label_m else "", text)
            if reason:
                if not args.apply:
                    print(f"  precondition skip: {ident_m.group(1)} — {reason}")
                skip_excluded += 1
                continue
        is_draft = "graph_id: resistance-draft" in text
        # This promoter's own output is identified STRUCTURALLY -- by the graph id it
        # writes and the curator it stamps -- not by prose in a curation_history sentence
        # that PyYAML wraps at width=100 (#199). Had a wrap landed inside the old grepped
        # phrase, every promoted record would have looked hand-curated, been skipped, and
        # the run would still have exited 0.
        #
        # BOTH conditions, not just the graph id. Re-promotion REPLACES everything between
        # `causal_graphs:` and `license:`, so what counts as "ours" decides what may be
        # overwritten. `graph_id: resistance` alone would also match a graph a curator
        # happened to name that; the conjunction is narrower. Checked: all 6,266 records
        # carrying that graph id also carry this curator, so the conjunction loses nothing
        # today and refuses to clobber a hand-written graph tomorrow. Both are short
        # single-token lines, so neither can be split by wrapping.
        is_ours = ("graph_id: resistance\n" in text
                   and "curator: edison-causal-graphs" in text)
        if is_draft:
            pass                                                # a draft → promote
        elif is_ours and args.repromote:
            pass                                # re-promote our own output (config change)
        else:
            # already curated, and re-promotion was not asked for. Was the default until
            # #204: a curator who improves a promoted graph and leaves the history entry
            # in place had that work silently rewritten by the next --apply.
            skip_done += 1
            continue
        ident = ident_m.group(1)
        label = re.search(r'^label:\s*"?(.+?)"?\s*$', text, re.M).group(1)
        mech, drug = D.parse_relations(text)
        try:
            graph = promoted_graph_dict(ident, label, mech, drug, names, cfg, terms)
        except UncoveredMechanism as exc:
            # the config has no snippet for this member's mechanism. Skipping is the only
            # honest option: the alternative was writing a different mechanism's evidence.
            print(f"  mechanism skip: {ident} — no snippet for {exc.mechanism_id}")
            skip_excluded += 1
            continue
        # MERGE, never splice-and-replace (#204). The old write took every line between
        # `causal_graphs:` and `license:` and threw it away, which destroys
        #   * any OTHER graph on the record -- a builder's `reaction_chemistry`, a
        #     curator's hand-written one -- because they live in the same section, and
        #   * the whole curation_history, which is why every promoted record has exactly
        #     one event no matter how many times it has been promoted.
        # Neither loss is visible in the diff of a record that only ever had our graph,
        # which is why it survived six rounds.
        doc = yaml.safe_load(text) or {}
        # BOTH ids, because this promoter owns both: `resistance-draft` is what it
        # consumes and `resistance` is what it produces. Filtering only `resistance` left
        # a promoted draft carrying its own superseded draft graph alongside the curated
        # one -- caught in review because the canary had exercised the RE-promote path
        # (where the graph is already `resistance`) and not the primary promote-a-draft
        # path, which is the one that runs 1,133 more times.
        graphs = [g for g in (doc.get("causal_graphs") or [])
                  if g.get("graph_id") not in OWNED_GRAPH_IDS]
        graphs.append(graph)
        history = list(doc.get("curation_history") or [])
        event = curation_entry(cfg)
        if event not in history:
            history.append(event)
        new = RIO.replace_block(text, "causal_graphs", "\n".join(_dump({"causal_graphs": graphs})))
        new = RIO.replace_block(new, "curation_history",
                                "\n".join(_dump({"curation_history": history})))
        new = re.sub(r"^mapping_status: SEEDED$", "mapping_status: REVIEWED", new, flags=re.M)
        if args.apply:
            pth.write_text(new, encoding="utf-8")
        promoted += 1
        repromoted += 0 if is_draft else 1
        if args.limit and promoted >= args.limit:
            break

    fam_name = terms.get(args.family, {}).get("name", args.family)
    # `promoted` counts fresh drafts AND re-promotions of this promoter's own output, and
    # reporting both as "drafts promoted" is how a re-run of an already-curated family
    # reads as if 232 drafts existed. Say which is which.
    fresh = promoted - repromoted
    print(f"family {args.family} ({fam_name}): {promoted:,} records written "
          f"({fresh:,} draft{'' if fresh == 1 else 's'} promoted to REVIEWED, "
          f"{repromoted:,} already-curated re-promoted)")
    print(f"  skipped (already curated): {skip_done:,} | skipped (no draft): {skip_nodraft:,}"
          f" | skipped (excluded by config): {skip_excluded:,}")
    print("APPLIED." if args.apply else "Dry-run — pass --apply to write.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
