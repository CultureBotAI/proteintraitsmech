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
import hashlib
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
         "requires": {"drug0": "ARO:0000001"},      # the snippet is about quinolones
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


def _vanrs_ser_downstream() -> tuple[list, list]:
    """The D-Ala-D-Ser clusters' regulon: the ligase, vanT and vanXY (#208).

    Same two-component evidence as the vanH/vanX variant -- PMID:1556077 characterised the
    system -- but the genes it induces are this cluster's, and all three are now curated
    records (round 23), so the graph points at them instead of restating their chemistry.
    """
    nodes = [
        {"node_id": "transcription",
         "label": "positive regulation of DNA-templated transcription (the van resistance operon)",
         "node_type": "BIOLOGICAL_PROCESS", "grounding": "GO:0045893"},
        {"node_id": "ligase_gene", "label": "D-Ala-D-Ser ligase of the van cluster",
         "node_type": "PROTEIN", "grounding": "ARO:3002979",
         "description": "KB record, curated in round 23."},
        {"node_id": "vant_gene", "label": "vanT (membrane serine racemase of the van cluster)",
         "node_type": "PROTEIN", "grounding": "ARO:3000372",
         "description": "KB record, curated in round 23."},
        {"node_id": "vanxy_gene", "label": "vanXY (D,D-dipeptidase/carboxypeptidase of the van cluster)",
         "node_type": "PROTEIN", "grounding": "ARO:3000496",
         "description": "KB record, curated in round 23."},
    ]
    edges = []
    for node, what in (("ligase_gene", "the D-Ala-D-Ser ligase"),
                       ("vant_gene", "vanT"), ("vanxy_gene", "vanXY")):
        edges.append(
            {"subject": "transcription", "object": node,
             "predicate": "positively regulates (induced with the resistance operon)",
             "predicate_id": "RO:0002213",
             "evidence": [{"reference": "PMID:1556077", "snippet": _VANRS_REG,
                           "notes": f"Arthur et al. 1992 established that the two-component system regulates the resistance enzymes at the transcriptional level; in a D-Ala-D-Ser cluster {what} is one of them."}]})
        edges.append(
            {"subject": node, "object": "resistance",
             "predicate": "causally upstream of (the mechanism this regulator induces)",
             "predicate_id": "RO:0002411",
             "description": "The regulator confers no resistance itself; the enzymes it induces do.",
             "evidence": [{"reference": "PMID:10817725", "snippet": _SER_CLUSTER,
                           "notes": f"Arias et al. 2000: the three genes sufficient for VanC-type resistance, of which {what} is one. Its own mechanism is curated on its record."}]})
    return nodes, edges


_RND_PUMP = "ARO:0010004"      # resistance-nodulation-cell division (RND) antibiotic efflux pump
_PART_OF_INDEX = None


def _aro_part_of() -> dict:
    """ARO id -> the complexes it is `part_of`, read from the obo release.

    Efflux SUBUNITS carry no pump-class ancestry of their own (#223) -- 137 drafts sit flat
    under ARO:3000748. But each is `part_of` a complex, and the COMPLEX is classified: every
    AcrAB-TolC, MexAB-OprM, AdeABC and so on is `is_a` RND. So the class is two hops away and
    fully derivable, which is what makes a precondition possible here instead of the
    hand-maintained name list #223 warned against.
    """
    global _PART_OF_INDEX
    if _PART_OF_INDEX is None:
        idx = {}
        text = D.OBO.read_text(encoding="utf-8")
        for stanza in text.split("\n[Term]"):
            m = re.search(r"^id: (ARO:\d+)", stanza, re.M)
            if not m:
                continue
            parents = re.findall(r"^relationship: part_of (ARO:\d+)", stanza, re.M)
            if parents:
                idx[m.group(1)] = parents
        _PART_OF_INDEX = idx
    return _PART_OF_INDEX


def _requires_pump_class(class_id: str, human: str):
    """Build a precondition selecting efflux subunits of one pump class (#223, round 33).

    Generalised from `_requires_rnd_pump` once the second class needed it: the two-hop
    lookup is identical and only the class id changes, so duplicating it per class would be
    four copies of the same walk -- the standing lesson of #93.
    """
    def _check(ident: str, label: str, text: str):
        terms = E.parse_obo(E.OBO)
        # the record's OWN part_of, and its is_a ancestors' -- a species-specific record
        # such as "Escherichia coli acrA" is `is_a acrA`, and it is the generic `acrA`
        # that carries `part_of AcrAB-TolC`. Checking only the record's own link left 4
        # such variants unclassified and therefore uncurable (round 36).
        parts = list(_aro_part_of().get(ident, []))
        for anc in E.ancestry(terms, ident):
            parts.extend(_aro_part_of().get(anc, []))
        for complex_id in parts:
            if class_id in E.ancestry(terms, complex_id):
                return None
        return (f"this determinant is not part of a complex ARO classifies as {human}, "
                f"and pump classes differ in subunit count and energetics")
    return _check


def _requires_rnd_pump(ident: str, label: str, text: str):
    """The record must be a subunit of a complex ARO classifies as RND."""
    terms = E.parse_obo(E.OBO)
    for complex_id in _aro_part_of().get(ident, []):
        if _RND_PUMP in E.ancestry(terms, complex_id):
            return None
    return ("this determinant is not part of a complex ARO classifies as an RND pump, so "
            "the tripartite proton-antiport evidence does not describe it (MFS, ABC, SMR "
            "and MATE pumps have different subunit counts and energetics)")


# The 27 efflux repressors, verified by READING each record's definition rather than by
# keyword (#231). A keyword match returned 31 and was wrong on four: ArmR is an
# ANTIrepressor (opposite direction), and CpxR, MvaT and P. aeruginosa CpxR merely mention
# repression without being the repressor. The direction lives in prose, not in the ontology
# structure, so this is a checked list rather than a derivation -- and the check is recorded
# here and in the round report so it can be re-run rather than trusted.
# Round 41 added 5 more by reading the 35 that stated no direction in a recognised form:
# emrR ('negative regulator ... Mutations lead to EmrAB overexpression'), MexZ
# ('downregulates the mexXY operon'), MvaT and rsmA (both negative regulators of an efflux
# operon) and adeL ('AdeL mutations are associated with AdeFGH overexpression'). MvaT was
# EXCLUDED in round 37 as 'mentions repression without being the repressor' -- reading the
# whole definition rather than the matched clause shows it is one.
_EFFLUX_REPRESSORS = frozenset(['ARO:3000506', 'ARO:3000516', 'ARO:3000518', 'ARO:3000526', 'ARO:3000559', 'ARO:3000620', 'ARO:3000656', 'ARO:3000676', 'ARO:3000702', 'ARO:3000718', 'ARO:3000746', 'ARO:3000815', 'ARO:3000817', 'ARO:3000818', 'ARO:3000819', 'ARO:3000820', 'ARO:3000821', 'ARO:3000824', 'ARO:3000834', 'ARO:3003028', 'ARO:3003373', 'ARO:3003374', 'ARO:3003378', 'ARO:3003379', 'ARO:3003380', 'ARO:3003479', 'ARO:3003709', 'ARO:3003710', 'ARO:3003807', 'ARO:3003838', 'ARO:3004069', 'ARO:3005069'])


# The 15 efflux ACTIVATORS, verified the same way as the repressors (#231, round 37) and
# deliberately CONSERVATIVE: the pattern also excluded marA, which is a transcriptional
# activator, because its definition does not say so in a form the check recognises. A false
# exclusion leaves a record as a draft; a false inclusion would assert the wrong direction
# on a graph whose whole content is that direction. Erring toward the draft is the cheaper
# mistake, and the excluded ones are listed in the round-38 report so they can be revisited.
# Round 41 added 3 more by reading: adeS ('essential for AdeABC expression'), P. aeruginosa
# CpxR ('directly involved in activation of expression of RND efflux pump MexAB-OprM' --
# also a round-37 false exclusion) and baeS ('phosphorylates BaeR to increase its activity').
# Round 40 added 9 more after a second reading pass. ArmR was excluded for the THIRD time:
# its definition says it raises pump levels, but it does so by inhibiting MexR -- it acts on
# a REPRESSOR, not on the pump, so an activator edge would assert the wrong target. Three
# different patterns have now matched it; only reading has ever rejected it.
_EFFLUX_ACTIVATORS = frozenset(['ARO:3000504', 'ARO:3000508', 'ARO:3000524', 'ARO:3000547', 'ARO:3000549', 'ARO:3000553', 'ARO:3000813', 'ARO:3000814', 'ARO:3000816', 'ARO:3000823', 'ARO:3000825', 'ARO:3000826', 'ARO:3000827', 'ARO:3000828', 'ARO:3000829', 'ARO:3000830', 'ARO:3000831', 'ARO:3000832', 'ARO:3000838', 'ARO:3003841', 'ARO:3003843', 'ARO:3004054', 'ARO:3004055', 'ARO:3004108', 'ARO:3004109', 'ARO:3005063', 'ARO:3005064'])


# Two-component regulators of LIPID A modification, read out of the same 46 that produced
# rounds 37-38. Their mechanism is not efflux at all despite the family term: they induce
# the genes that add positive charge to the envelope, so this is round 32's electrostatic
# repulsion reached by a regulatory route.
# marA is NOT here despite being a genuine activator: it also carries ARO:3000244 (reduced
# permeability to antibiotic), because MarA down-regulates porins as well as raising efflux.
# The UncoveredMechanism guard refused it, correctly -- this config describes efflux
# activation only, and a marA graph that said nothing about permeability would describe
# half of what CARD asserts. It needs a config covering both arms (#238).
# Round 42 added the four PhoP/PhoQ records, named as a known false exclusion in round 39.
# They describe the SAME mechanism without the words the round-39 pattern required -- e.g.
# 'A mutant phoP activates pmrHFIJKLM expression responsible for L-aminoarabinose synthesis
# and polymyxin resistance'. L-aminoarabinose IS the lipid A modification; the pattern
# wanted the phrase 'lipid A' and the definition names the sugar instead.
_LPS_REGULATORS = frozenset(['ARO:3003582', 'ARO:3003583', 'ARO:3003585', 'ARO:3003895', 'ARO:3003896', 'ARO:3007203'])

# #425: SPLIT BY ROLE. One config served all six and quoted basR's definition on every
# one, which asserted "Response regulator" on three HISTIDINE KINASES (basS, and the two
# PhoQ mutants) -- the opposite half of the two-component system -- and, until #423
# repaired the truncation that had hidden it, "senses high extracellular Fe(2+)" as well.
# Fe(2+) is BasSR/PmrAB's signal; PhoQ senses Mg2+ and low pH, so the snippet contradicted
# the record it sat on.
#
# The two roles are not a subtlety here, they are the whole mechanism: one senses, the
# other binds DNA. So each gets the archetype from its OWN half -- basR for the response
# regulators, basS for the sensor kinases -- and basS's record stops citing basR's
# definition for all five of its edges, which was the only place its own subject was named.
_LPS_RESPONSE_REGULATORS = frozenset(['ARO:3003582', 'ARO:3003585', 'ARO:3003895'])
_LPS_SENSOR_KINASES = frozenset(['ARO:3003583', 'ARO:3003896', 'ARO:3007203'])
assert _LPS_RESPONSE_REGULATORS | _LPS_SENSOR_KINASES == _LPS_REGULATORS, \
    "the role split must partition _LPS_REGULATORS -- a record in neither gets no config"
assert not (_LPS_RESPONSE_REGULATORS & _LPS_SENSOR_KINASES), \
    "the role split must be disjoint -- an overlap makes list order load-bearing"


def _requires_lps_regulator(ident: str, label: str, text: str):
    if ident in _LPS_REGULATORS:
        return None
    return ("not on the verified lipid-A-regulator list: this config's mechanism is "
            "induction of envelope charge modification, not efflux")


def _requires_lps_response_regulator(ident: str, label: str, text: str):
    if ident in _LPS_RESPONSE_REGULATORS:
        return None
    return ("not a verified lipid-A RESPONSE REGULATOR: this config quotes basR, and a "
            "sensor kinase is the other half of the two-component system (#425)")


def _requires_lps_sensor_kinase(ident: str, label: str, text: str):
    if ident in _LPS_SENSOR_KINASES:
        return None
    return ("not a verified lipid-A SENSOR KINASE: this config quotes basS, and a response "
            "regulator is the other half of the two-component system (#425)")


def _requires_efflux_activator(ident: str, label: str, text: str):
    if ident in _EFFLUX_ACTIVATORS:
        return None
    return ("not on the verified efflux-activator list: this config's mechanism is "
            "over-activity DRIVING pump expression, the opposite direction from the "
            "repressors curated in round 37")


def _requires_efflux_repressor(ident: str, label: str, text: str):
    if ident in _EFFLUX_REPRESSORS:
        return None
    return ("not on the verified efflux-repressor list: this config's mechanism is loss of "
            "repression, and activators, antirepressors and records that merely mention "
            "repression have the opposite or no such direction")


def _requires_mprf(ident: str, label: str, text: str):
    """This config is MprF's lysinylation, not every way of altering envelope charge.

    ARO:3003580 (gene altering cell wall charge) also holds ArnT and PmrF (L-Ara4N on
    lipid A), the ICR phosphoethanolamine transferases, and PhoP (a regulator). They share
    the PRINCIPLE -- add positive charge, repel cationic peptides -- and not the chemistry,
    so each needs its own evidence. Same call as target protection in round 31.
    """
    if re.search(r"\bmprF\b", label):
        return None
    return ("this determinant is not mprF, and the lysyl-phosphatidylglycerol evidence "
            "does not describe L-Ara4N addition, phosphoethanolamine transfer or the "
            "PhoP regulator")


def _requires_macrolide_glycosyltransferase(ident: str, label: str, text: str):
    """Glycosylation -- the third chemistry, after hydrolysis (r46) and phosphorylation (r47)."""
    if re.search(r"glycosyltransferase|glycosylat", text, re.I):
        return None
    return ("this determinant is not a macrolide glycosyltransferase: adding a sugar is "
            "neither opening the lactone ring nor phosphorylating it")


def _requires_macrolide_kinase(ident: str, label: str, text: str):
    """Phosphorylation, not ring hydrolysis (round 46) or glycosylation."""
    if re.search(r"phosphotransferase|\bmph\b|phosphorylat", text, re.I):
        return None
    return ("this determinant is not a macrolide phosphotransferase: adding a phosphate is "
            "not opening the lactone ring, which the Ere esterases do")


def _requires_macrolide_esterase(ident: str, label: str, text: str):
    """Ring hydrolysis, not the phosphotransferases or glycosyltransferases.

    ARO:3000201 holds three chemistries: Ere esterases hydrolyse the macrolactone ring,
    Mph enzymes phosphorylate the drug, and gimA-family enzymes glycosylate it. All three
    inactivate a macrolide and none of them share a reaction, so each needs its own paper
    -- the same call as target protection (rounds 31, 44, 45).
    """
    if re.search(r"esterase", text, re.I):
        return None
    return ("this determinant is not a macrolide esterase: ring hydrolysis is not "
            "phosphorylation or glycosylation, which the other two chemistries under this "
            "family term perform")


def _requires_rifamycin_protection(ident: str, label: str, text: str):
    """RNAP protection, not TetM's ribosomal protection or FusB's EF-G rescue."""
    if re.search(r"grounding: ARO:3000157\b", text):
        return None
    return ("this determinant's drug is not a rifamycin, and the RNAP-displacement evidence "
            "describes neither ribosomal protection nor EF-G rescue")


def _requires_fusidane(ident: str, label: str, text: str):
    """FusB-type protection of EF-G, not TetM's ribosomal protection (round 31)."""
    if re.search(r"grounding: ARO:3007153\b", text):
        return None
    return ("this determinant's drug is not a fusidane, and the EF-G rescue evidence does "
            "not describe tetracycline or rifamycin target protection")


def _requires_tetracycline(ident: str, label: str, text: str):
    """This config is the RIBOSOME-protection mechanism, so refuse the other two.

    `ARO:3000185` (antibiotic target protection) covers three different mechanisms:
    ribosomal protection of tetracycline (TetM/TetO/OtrA), RNA-polymerase binding against
    rifamycins (RbpA, HelR), and EF-G binding against fusidic acid (FusB/FusC/FusD). One
    config cannot describe all three -- the round-19 and round-22 lesson -- so this one
    takes the records whose drug is tetracycline and the other two wait for their own
    evidence.
    """
    if re.search(r"grounding: ARO:3000050\b", text):
        return None
    return ("this determinant's drug is not tetracycline, so the ribosome-protection "
            "evidence does not describe it (rifamycin and fusidane target protection are "
            "different mechanisms with different partners)")


def _requires_lac_cluster(ident: str, label: str, text: str):
    """VanY's characterisation is VanA-type (Tn1546), so refuse a D-Ala-D-Ser cluster.

    PMID:10094630 measured the enzyme on precursors ending in R-D-Ala-D-Ala or
    R-D-Ala-D-Lac. It says nothing about R-D-Ala-D-Ser, so the one vanY draft in a vanG
    cluster is held back rather than given a graph whose evidence does not cover its
    substrate. The mirror of `_requires_ser_cluster` (#201).
    """
    m = re.search(r"gene in (van[A-Z]+) cluster", label)
    if not m:
        if "cluster" in label:
            return ("label names a cluster but does not match the expected shape, so the "
                    "cluster's gene content cannot be checked")
        return None
    genes = _van_cluster_genes().get(m.group(1), set())
    if "vanH" not in genes:
        return (f"cluster {m.group(1)} has no vanH, so it is the D-Ala-D-Ser route; this "
                f"config's evidence measured R-D-Ala-D-Ala and R-D-Ala-D-Lac substrates only")
    return None


def _requires_ser_cluster(ident: str, label: str, text: str):
    """These configs describe the D-Ala-D-SER route, so refuse a D-Ala-D-Lac cluster.

    The mirror of `_requires_vanhax`, and written BEFORE the fan-out this time rather than
    after shipping 12 wrong records: a cluster carrying vanH is the depsipeptide route
    (rounds 20-21) and its genes are not these. Checked against the corpus's own
    per-cluster gene records.
    """
    m = re.search(r"gene in (van[A-Z]+) cluster", label)
    if not m:
        if "cluster" in label:
            return ("label names a cluster but does not match the expected shape, so the "
                    "cluster's gene content cannot be checked")
        return None
    genes = _van_cluster_genes().get(m.group(1), set())
    if "vanH" in genes:
        return (f"cluster {m.group(1)} carries vanH, so it is the D-Ala-D-Lac route "
                f"(rounds 20-21), not the D-Ala-D-Ser route this config describes")
    return None


# The D-Ala-D-Ser arm, shared by the ligase, vanT and vanXY. Every record here belongs to a
# vanC/E/G/L/N cluster, where resistance comes from a precursor ending in D-Ala-D-SER
# rather than D-Ala-D-Lac. PMID:10817725 states the whole three-gene division of labour in
# one sentence, which is why it appears on all three families.
_SER_CLUSTER = "Three genes are sufficient for resistance: vanC-1 encodes a ligase that synthesizes the dipeptide D-Ala-D-Ser for addition to UDP-MurNAc-tripeptide, vanXY(C) encodes a D,D-dipeptidase-carboxypeptidase that hydrolyzes D-Ala-D-Ala and removes D-Ala from UDP-MurNAc-pentapeptide[D-Ala], and vanT encodes a membrane-bound serine racemase that provides D-Ser for the synthetic pathway."
_SER_PRECURSOR = "Glycopeptide-resistant enterococci of the VanC type synthesize UDP-muramyl-pentapeptide[D-Ser] for cell wall assembly and prevent synthesis of peptidoglycan precursors ending in D-Ala."


def _ser_shared_nodes() -> list:
    return [
        {"node_id": "precursor_ser",
         "label": "UDP-MurNAc-pentapeptide[D-Ser] (precursor ending in D-Ala-D-Ser)",
         "node_type": "STATE",
         "description": "The replacement precursor. Ungrounded: ChEBI has the amino acids but not the UDP-MurNAc pentapeptides."},
        {"node_id": "precursor_dala",
         "label": "UDP-MurNAc-pentapeptide[D-Ala] (the precursor glycopeptides bind)",
         "node_type": "STATE",
         "description": "The normal precursor, whose synthesis this pathway prevents. Ungrounded, as above."},
    ]


def _ser_shared_edges() -> list:
    return [
        {"subject": "precursor_ser", "object": "precursor_dala",
         "predicate": "negatively regulates (replaces the D-Ala-ending precursor)",
         "predicate_id": "RO:0002212",
         "description": "The causal core of the VanC route: the wall is assembled from the D-Ser precursor instead, and the D-Ala-ending one is not made.",
         "evidence": [{"reference": "PMID:10817725", "snippet": _SER_PRECURSOR,
                       "notes": "Arias, Courvalin & Reynolds 2000. Both halves in one sentence: what is synthesised, and what is prevented."}]},
        {"subject": "drug0", "object": "precursor_dala",
         "predicate": "molecularly interacts with (binds the D-Ala-D-Ala terminus)",
         "predicate_id": "RO:0002436",
         "requires": {"drug0": "ARO:3000081"},
         "description": "Drug action: the glycopeptide binds the D-Ala terminus. Replacing it is what confers resistance.",
         "evidence": [{"reference": "PMID:10817725", "snippet": _SER_PRECURSOR,
                       "notes": "The precursor named here is the one the drug binds; the VanC route prevents its synthesis."}]},
    ]

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



def _own_definition(text: str) -> str:
    """Just the record's OWN `definition:` block.

    Scanning the whole YAML is a false-positive machine: an ARO record inherits
    drug-class boilerplate that names other mechanisms entirely. A keyword predicate
    run over the full text excluded 17 legitimate PBP3 mutants with the reason
    "definition describes a repressor" because the phrase "deactivation of repressors"
    appears in inherited drug-class prose. Read the record's own claim, nothing else.
    """
    m = re.search(r"^definition:\s*(.*?)(?=\n\w)", text, re.M | re.S)
    return " ".join(m.group(1).split()) if m else ""


def _requires_replacement_pbp(ident: str, label: str, text: str):
    """This config says "an ACQUIRED low-affinity PBP does the wall synthesis instead".

    Discriminates STRUCTURALLY, on the mechanism the record itself carries, not on
    keywords: ARO:3003040 mixes target replacement (ARO:0001002) with target alteration
    by mutation (ARO:3000212), and only the former is this config's story. A PBP3 point
    mutant is a real resistance determinant -- it just belongs to the round 18-19 shape,
    and must be left as a draft rather than given a replacement graph.

    Then one reading check on the record's OWN definition: ARO:3005046 is MecI, the
    *repressor* of mec transcription, which carries the replacement mechanism id despite
    regulating rather than replacing anything. Same trap as ArmR in the efflux rounds.
    Filed as #251.
    """
    mechs = D.parse_relations(text)[0]
    if "ARO:0001002" not in mechs:
        return ("record carries no target-replacement mechanism (ARO:0001002); it is "
                "target alteration by mutation and needs the round 18-19 shape")
    if "repressor" in _own_definition(text).lower():
        return ("own definition describes a repressor, not a replacement PBP -- its "
                "mechanism is regulation of the mec operon (#251)")
    return None


def _requires_mutant_pbp(ident: str, label: str, text: str):
    """Target ALTERATION of a PBP -- the mutation lowers the drug's affinity for it.

    Two exclusions, both structural-then-reading, in the order round 52 established:

    1. the record must carry ARO:3000212 (mutation), not ARO:0001002 -- an ACQUIRED
       low-affinity PBP is target replacement and has its own config (round 52);
    2. its own definition must actually name a penicillin-binding protein. ARO:3004835
       is *pilQ*, an outer-membrane secretin of the Type IV pilus, filed under the PBP
       family; its resistance route is permeability, not target affinity (#254).

    Reading the record's OWN definition, never the full YAML -- the round 52 bug.
    """
    mechs = D.parse_relations(text)[0]
    if "ARO:3000212" not in mechs:
        return "record carries no mutation mechanism (ARO:3000212)"
    own = _own_definition(text).lower()
    # \bpbp\b, NOT \bpbp\s?\d -- ARO:3003938's definition says "PBP transpeptidases"
    # with no number, and the narrower pattern wrongly skipped it. Caught by reading the
    # skip log, which is the only reason round 52's lesson generalised at all.
    # \bpbp (prefix, NO trailing boundary). Round 53 went from `\bpbp\s?\d` to `\bpbp\b`
    # to catch "PBP transpeptidases" -- and thereby stopped matching "PBP1"/"pbp3", which
    # the first pattern DID catch. A fix that traded one miss for another, invisible
    # because promotion is idempotent and never re-checks what it already wrote. #267's
    # cross-family sweep found the 7 stranded records; nothing else would have.
    if not re.search(r"penicillin-binding protein|\bpbp", own):
        return ("own definition does not name a penicillin-binding protein, so a "
                "PBP-affinity mechanism cannot be asserted for it (#254)")
    return None


def _requires_16s_rrna(ident: str, label: str, text: str):
    """The determinant must actually be 16S rRNA -- checked on its OWN definition (#253).

    Round 53's pilQ found a record filed under a family whose mechanism its definition
    contradicted, so every new config now carries this check rather than trusting the
    family term.
    """
    if "ARO:3000212" not in D.parse_relations(text)[0]:
        return "record carries no mutation mechanism (ARO:3000212)"
    own = _own_definition(text).lower()
    if "16s" not in own and "16s" not in label.lower():
        return "own definition does not name 16S rRNA"
    return None


def _requires_23s_rrna(ident: str, label: str, text: str):
    """Determinant must be 23S rRNA, checked on its OWN definition (#253, #254)."""
    if "ARO:3000212" not in D.parse_relations(text)[0]:
        return "record carries no mutation mechanism (ARO:3000212)"
    if "23s" not in _own_definition(text).lower() and "23s" not in label.lower():
        return "own definition does not name 23S rRNA"
    return None


def _requires_pnca(ident: str, label: str, text: str):
    """Determinant must be pncA, checked on its OWN definition (#253, #254)."""
    if "ARO:3000212" not in D.parse_relations(text)[0]:
        return "record carries no mutation mechanism (ARO:3000212)"
    if "pnca" not in _own_definition(text).lower() and "pnca" not in label.lower():
        return "own definition does not name pncA"
    return None


def _requires_ndh(ident: str, label: str, text: str):
    """Determinant must be ndh, checked on its OWN definition (#253, #254)."""
    if "ARO:3000212" not in D.parse_relations(text)[0]:
        return "record carries no mutation mechanism (ARO:3000212)"
    if "ndh" not in _own_definition(text).lower() and "ndh" not in label.lower():
        return "own definition does not name ndh"
    return None


def _requires_upp_recycler(ident: str, label: str, text: str):
    """Determinant must handle undecaprenyl pyrophosphate, per its OWN definition."""
    if "ARO:3000213" not in D.parse_relations(text)[0]:
        return "record carries no cell-wall-restructuring mechanism (ARO:3000213)"
    if "undecaprenyl pyrophosphate" not in _own_definition(text).lower():
        return "own definition does not name undecaprenyl pyrophosphate"
    return None


def _requires_class_d(ident: str, label: str, text: str):
    """Determinant must be a class D beta-lactamase, per its OWN definition."""
    if "ARO:3000187" not in D.parse_relations(text)[0]:
        return "record carries no serine-beta-lactamase hydrolysis mechanism (ARO:3000187)"
    own = _own_definition(text).lower()
    # Allow a family token between "class D" and "beta-lactamase": RAD-1's definition
    # reads "a class D RAD beta-lactamase", and requiring the two adjacent wrongly
    # excluded it. Fourth instance this session of an over-narrow pattern producing a
    # false skip (after #252, #255, and the role-mismatch audit's \b bug) -- caught, again,
    # by reading the records the guard refused rather than trusting the count.
    # No proximity requirement at all. Round 59 used 24 characters and #264's detector
    # immediately found two records it still missed: LRA-13 ("class D/class C fusion
    # bifunctional beta-lactamase") and ARO:3000017, whose definition says "they belong to
    # molecular class D" a full paragraph away from any "beta-lactamase". Three attempts at
    # a proximity window is enough evidence that the window was the wrong idea.
    if not (re.search(r"class d\b", own) and re.search(r"beta[- ]?lactamase", own)):
        return "own definition does not call it a class D beta-lactamase"
    return None


def _requires_tet_hydroxylase(ident: str, label: str, text: str):
    """This config says the determinant HYDROXYLATES the drug.

    tet(34) (ARO:3002870) carries the hydroxylation mechanism id and its own definition
    describes something else entirely: "causes the activation of Mg2+-dependent purine
    nucleotide synthesis, which protects the protein synthesis pathway". That is target
    protection, not inactivation. Fifth record this session filed under a family whose
    mechanism its own definition contradicts, after MecI (#251), pilQ (#254), ahpC (#260)
    and the class D thin-definition set. Filed as #267.
    """
    if "ARO:3000450" not in D.parse_relations(text)[0]:
        return "record carries no hydroxylation mechanism (ARO:3000450)"
    own = _own_definition(text).lower()
    if re.search(r"purine nucleotide|protects the protein synthesis", own):
        return ("own definition describes protection of protein synthesis, not "
                "hydroxylation of the drug (#267)")
    return None


def _requires_topoisomerase_subunit(ident: str, label: str, text: str):
    """Target alteration of a topoisomerase subunit -- the drug can no longer bind it.

    Rounds 18-19 curated the FLUOROQUINOLONE story on gyrA/parC/gyrB/parE, where the
    drug traps the cleavage complex. These records are mostly AMINOCOUMARIN resistance,
    which acts at the ATPase site instead -- a different drug class on overlapping genes,
    which is why config_for's selector matters here rather than a single family config.
    """
    if "ARO:3000212" not in D.parse_relations(text)[0]:
        return "record carries no mutation mechanism (ARO:3000212)"
    own = _own_definition(text).lower()
    # Check the LABEL as well as the definition. Three gyrB records read only "Point
    # mutation in <organism> resulting in aminocoumarin resistance" -- thin, but their
    # ARO term NAME is "Escherichia coli gyrB conferring resistance to aminocoumarin",
    # which is authoritative and unambiguous. Round 61 checked the definition only and
    # left them as drafts for 34 rounds.
    #
    # This is safe here in a way it would NOT be for pilQ (#254): there the label said
    # "pilQ gene conferring resistance to beta-lactam" while the mechanism was wrong, so
    # the definition was the corrective. Here the label names the gene the family is
    # about, and the parent term supplies the mechanism the members omit.
    if not re.search(r"topoisomerase|gyrase|\bgyr[ab]\b|\bpar[ceyx]\b",
                     own + " " + label.lower()):
        return ("neither the definition nor the label names a topoisomerase or gyrase "
                "subunit")
    return None


def _requires_adp_ribosyltransferase(ident: str, label: str, text: str):
    """ADP-ribosylation specifically -- ARO:3000576 mixes FOUR chemistries.

    Its 17 drafts split across ADP-ribosylation (arr, 8), hydroxylation (4),
    glycosylation (2) and phosphorylation (3). They inactivate the same drug by
    different reactions, so one config across the family would assert the wrong
    chemistry for most of it -- rounds 22 and 58's error. The other three need their own
    configs and their own snippets.
    """
    if "ARO:3000266" not in D.parse_relations(text)[0]:
        return "record carries no ADP-ribosylation mechanism (ARO:3000266)"
    return None


def _requires_mech(mech_id: str, human: str, exclude_marker: str = ""):
    """Precondition factory: this config's chemistry, and only it.

    ARO:3000576 holds four reactions that inactivate the same drug (round 62). Each needs
    its own snippets, and the discriminator is purely structural -- the mechanism id the
    record itself carries -- so one factory serves all of them rather than four
    near-identical hand-written predicates, each an opportunity for the pattern bugs that
    cost this session four fixes (#252, #255, #264, #267).
    """
    def _pred(ident: str, label: str, text: str):
        if mech_id not in D.parse_relations(text)[0]:
            return f"record carries no {human} mechanism ({mech_id})"
        # An id-only check is not enough where a record carries the id and its own
        # definition describes something else. tet(34) carries ARO:3000450 and describes
        # TARGET PROTECTION (#267); round 60 excluded it by reading, and this factory
        # then silently re-accepted it because it only looked at the id. A guard that a
        # later, more general config undoes is worse than no guard, because the earlier
        # round's report still claims the record is excluded.
        if exclude_marker and exclude_marker in _own_definition(text).lower():
            return (f"own definition mentions {exclude_marker!r}, so it does not support "
                    f"{human} despite carrying {mech_id} (#267)")
        return None
    return _pred


def _rifampin_modification_config(mech_id: str, human: str, snippet: str,
                                  activity_label: str, extra_note: str = "") -> dict:
    """One rifampin-inactivation chemistry, from CARD's own mechanism-term definition.

    Every one of these is "enzyme covalently modifies the drug, drug stops working", so
    the graph shape is shared and only the chemistry differs. Writing them as a factory
    keeps the four subsets provably parallel; writing them out by hand would let them
    drift, which is what the round 55 test guarding the two rRNA configs was about.
    """
    return {
        "curated": "2026-08-07T00:00:00Z",
        "precondition": _requires_mech(mech_id, human),
        "reference": mech_id,
        "mech": {"ARO:0001004": "Enzymes that inactivate rifampin antibiotics by chemical modification.", mech_id: snippet},
        "mech_res": snippet,
        "det_res": [
            {"reference": mech_id, "snippet": snippet,
             "notes": f"CARD's own definition of {human}."},
            {"reference": "ARO:3000576", "snippet": "Enzymes that inactivate rifampin antibiotics by chemical modification.",
             "notes": ("And what it achieves. SCOPE: this family sentence covers all four "
                       "chemistries under ARO:3000576; only the " + human + " members are "
                       "curated by this config (round 62).")},
        ],
        "res_drug": snippet,
        "note": ("Inactivation by chemical modification -- " + human + " subset of "
                 "ARO:3000576." + (" " + extra_note if extra_note else "")),
        "extra_nodes": [
            {"node_id": "modification", "label": activity_label,
             "node_type": "MOLECULAR_FUNCTION",
             "description": ("Ungrounded: a rifampin-specific " + human + " activity, not "
                             "looked up rather than guessed (rounds 56-62).")},
            {"node_id": "modified", "label": "chemically modified, inactive rifampin",
             "node_type": "STATE", "description": "The product state. Ungrounded."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "modification",
             "predicate": "enables (modifies the drug)", "predicate_id": "RO:0002327",
             "evidence": [{"reference": mech_id, "snippet": snippet,
                           "notes": "The reaction CARD names for this mechanism id."}]},
            {"subject": "modification", "object": "drug0",
             "predicate": "has input (the drug)", "predicate_id": "RO:0002233",
             "evidence": [{"reference": mech_id, "snippet": snippet,
                           "notes": ("The antibiotic is the substrate, which is what makes "
                                     "this inactivation rather than target alteration.")}]},
            {"subject": "modification", "object": "modified",
             "predicate": "causally upstream of (inactivates the drug)",
             "predicate_id": "RO:0002411",
             "description": "The causal core.",
             "evidence": [{"reference": mech_id, "snippet": snippet,
                           "notes": "CARD names the chemistry and the inactivation together."}]},
        ],
    }


def _lps_regulator_config(precondition, reference: str, gene: str, snippet: str,
                          role: str) -> dict:
    """One HALF of a lipid-A-modification two-component system (#425).

    Was one config quoting basR on all six records. `snippet` is now the archetype for
    THIS role only, and it is a verbatim PREFIX of that gene's CARD definition -- the
    trailing "that senses high extracellular Fe(2+)" is dropped from both. Fe(2+) is
    BasSR/PmrAB's signal specifically; PhoQ senses Mg2+ and low pH, so on the four PhoP/PhoQ
    records the clause asserted the wrong signal outright. Dropping it costs nothing here:
    what this config's graph claims is the induction and the charge change, not the input
    the system reads.

    The prefix must stay a prefix -- `just audit-snippets` checks every literal against
    aro.obo, so a paraphrase fails the gate rather than shipping.
    """
    return {
        "curated": "2026-08-07T00:00:00Z",
        "precondition": precondition,
        "reference": reference,
        "mech": {m: snippet for m in ("ARO:0010000", "ARO:3000212", "ARO:0001002",
                                      "ARO:3003588", "ARO:0010001")},
        "mech_res": snippet,
        "det_res": snippet,
        "res_drug": snippet,
        "note": ("Not efflux despite the family term: these induce lipid A modification, "
                 "reaching round 32's electrostatic repulsion by a regulatory route. This "
                 "config covers " + role + "."),
        "extra_nodes": [
            {"node_id": "lipid_a_mod", "label": "lipid A modification gene expression",
             "node_type": "BIOLOGICAL_PROCESS",
             "description": "The pmrHFIJKLM / arn operon and relatives. Ungrounded: which operon differs per organism."},
            {"node_id": "surface_charge", "label": "reduced net negative charge of the envelope",
             "node_type": "QUALITY",
             "description": "The same property mprF produces by lysinylating phosphatidylglycerol (round 32). Ungrounded: no ontology term for envelope net charge."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "lipid_a_mod",
             "predicate": "positively regulates (induces the modification genes)",
             "predicate_id": "RO:0002213",
             "evidence": [{"reference": reference, "snippet": snippet,
                           "notes": ("CARD's definition of " + gene + ", the archetype for "
                                     + role + ". Each record's own definition names the "
                                     "operon IT induces.")}]},
            {"subject": "lipid_a_mod", "object": "surface_charge",
             "predicate": "causally upstream of (adds positive charge to the envelope)",
             "predicate_id": "RO:0002411",
             # NOT the gene archetype: this edge is about what the induced operon does,
             # which is a property of lipid A modification and not of either half of the
             # regulatory system. ARO:3003588 is the mechanism term every one of these
             # records participates in, and it states the charge consequence directly.
             "evidence": [{"reference": "ARO:3003588", "snippet": "The loss or reduction of the net negative charge within the cell wall of gram negative bacteria is a mechanism of resistance for cationic antimicrobials that depend on the negative charge for binding to the surface.",
                           "notes": "CARD's charge-alteration mechanism term, which is what the induced genes bring about. Lipid A modification is the route; the reduced net negative charge is the result."}]},
            {"subject": "surface_charge", "object": "drug0",
             "predicate": "negatively regulates (repels the cationic peptide)",
             "predicate_id": "RO:0002212",
             "description": "The causal core, shared with mprF (round 32) and reached here by induction rather than by the determinant doing the chemistry itself.",
             "evidence": [{"reference": "PMID:11342591", "snippet": "As this unusual modification leads to a reduced negative charge of the membrane surface, MprF-mediated peptide resistance",
                           "notes": "Peschel et al. 2001 state the charge-to-resistance direction. They studied mprF's lysinylation; the charge logic is the same for lipid A modification, and the notes say the transfer rather than implying the paper covered it."}]},
        ],
    }


def _inactivation_transfer_config(mech_id: str, human: str, snippet: str,
                                  activity_label: str, hedged_donor: bool = True,
                                  exclude_marker: str = "") -> dict:
    """One group-transfer chemistry under ARO:3000557, from CARD's mechanism-term text.

    All three of the big ones -- nucleotidylation, phosphorylation, acylation -- HEDGE
    their donor: "usually AMP", "usually by ATP, sometimes GTP", "often via acetylation by
    acetylCoA". So none of them gets a donor node, for round 63's reason: naming one would
    assert a specificity the source explicitly declines to give. That is a property of
    this whole family's text, not a coincidence of one term.

    Contrast round 64's vat acetyltransferases, whose definition names acetyl-CoA outright
    and therefore DOES carry the donor node.
    """
    return {
        "curated": "2026-08-07T00:00:00Z",
        "precondition": _requires_mech(mech_id, human, exclude_marker),
        "reference": mech_id,
        "mech": {"ARO:0001004": "Enzyme that catalyzes the inactivation of an antibiotic resulting in resistance. Inactivation includes chemical modification, destruction, etc.", mech_id: snippet},
        "mech_res": snippet,
        "det_res": [
            {"reference": mech_id, "snippet": snippet,
             "notes": ("CARD's definition of " + human + "."
                       + (" NOTE the hedge -- the donor is given as 'usually'/'often', so "
                          "it is not modelled as a node." if hedged_donor else
                          " No group donor is involved: this reaction cleaves or adds to "
                          "the drug rather than transferring a group onto it."))},
            {"reference": "ARO:3000557", "snippet": "Enzyme that catalyzes the inactivation of an antibiotic resulting in resistance. Inactivation includes chemical modification, destruction, etc.",
             "notes": ("And the family claim. SCOPE: ARO:3000557 covers several chemistries; "
                       "only the " + human + " members are curated by this config.")},
        ],
        "res_drug": snippet,
        "note": ("Inactivation by " + human + "."
                 + (" The group donor is deliberately NOT a node: CARD hedges it, and every "
                    "group-transfer chemistry under ARO:3000557 hedges it the same way."
                    if hedged_donor else
                    " No donor node, because no group is donated -- the reaction cleaves "
                    "the drug or adds to it directly.")),
        "extra_nodes": [
            {"node_id": "transfer", "label": activity_label,
             "node_type": "MOLECULAR_FUNCTION",
             "description": ("Ungrounded: not looked up rather than guessed (rounds 56-67).")},
            {"node_id": "modified", "label": "chemically modified, inactive antibiotic",
             "node_type": "STATE", "description": "The product state. Ungrounded."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "transfer",
             "predicate": "enables (modifies the drug)", "predicate_id": "RO:0002327",
             "evidence": [{"reference": mech_id, "snippet": snippet,
                           "notes": "The reaction CARD names for this mechanism id."}]},
            {"subject": "transfer", "object": "drug0",
             "predicate": "has input (the drug)", "predicate_id": "RO:0002233",
             "evidence": [{"reference": mech_id, "snippet": snippet,
                           "notes": ("The antibiotic is the acceptor, which is what makes "
                                     "this inactivation rather than target alteration.")}]},
            {"subject": "transfer", "object": "modified",
             "predicate": "causally upstream of (inactivates the drug)",
             "predicate_id": "RO:0002411",
             "description": "The causal core.",
             "evidence": [{"reference": "ARO:3000557", "snippet": "Enzyme that catalyzes the inactivation of an antibiotic resulting in resistance. Inactivation includes chemical modification, destruction, etc.",
                           "notes": "'catalyzes the inactivation of an antibiotic resulting in resistance'."}]},
        ],
    }


def _requires_petn_transferase(ident: str, label: str, text: str):
    """Phosphoethanolamine addition, the OTHER way to neutralise lipid A.

    ARO:3003580's existing config describes mprF / lysyl-phosphatidylglycerol. These records add
    phosphoethanolamine instead -- same charge outcome, different moiety -- and round 69's
    #264 near-miss detector is what surfaced them, flagging eptA and the pmr family as
    refused-for-lacking-"L-Ara4N addition" while every token of it was present.
    """
    if "ARO:3003588" not in D.parse_relations(text)[0]:
        return "record carries no charge-alteration mechanism (ARO:3003588)"
    if "phosphoethanolamine" not in _own_definition(text).lower():
        return "own definition does not name phosphoethanolamine"
    return None


def _requires_alm_glycylation(ident: str, label: str, text: str):
    """Glycylation of lipid A -- a THIRD charge-alteration chemistry on ARO:3003580.

    L-Ara4N addition and phosphoethanolamine addition (round 73) already have configs.
    This is glycyl transfer, in Vibrio cholerae's almEFG system.

    ARO:3007434 (the almEFG OPERON itself) is refused: whether a gene cluster should
    carry a protein-trait causal graph is the open modelling question behind the van
    set, and curating an operon here would pre-empt it. Its definition is still the best
    mechanism source for the PROTEIN records, and is cited by them.
    """
    if "ARO:3003588" not in D.parse_relations(text)[0]:
        return "record carries no charge-alteration mechanism (ARO:3003588)"
    own = _own_definition(text).lower()
    if "operon is responsible" in own:
        return ("record is the operon itself, not a protein; whether a gene cluster "
                "carries a protein-trait causal graph is still an open modelling question")
    if not re.search(r"glycyl|glycine", own):
        return "own definition does not name glycyl transfer"
    return None


def _requires_ara4n(ident: str, label: str, text: str):
    """Ara4N addition to lipid A -- the route rounds 73-74 wrongly said was already done.

    Those rounds described ARO:3003580's pre-existing config as "the L-Ara4N config". It
    is not: it is mprF / lysyl-phosphatidylglycerol. Ara4N had NO config, which is why
    arnA, ArnT, PmrE and PmrF were still drafts after two rounds that claimed to be
    adding routes alongside it. Comments corrected in this commit.
    """
    if "ARO:3003588" not in D.parse_relations(text)[0]:
        return "record carries no charge-alteration mechanism (ARO:3003588)"
    own = _own_definition(text).lower()
    if not re.search(r"ara4n|4-amino-4-deoxy-l-arabinose", own):
        return "own definition does not name Ara4N"
    return None


def _requires_lipid_a_aminoacylation(ident: str, label: str, text: str):
    """Aminoacylation of LPS -- the fifth surface-charge route on ARO:3003580."""
    if "ARO:3003588" not in D.parse_relations(text)[0]:
        return "record carries no charge-alteration mechanism (ARO:3003588)"
    if "aminoacylation" not in _own_definition(text).lower():
        return "own definition does not name aminoacylation"
    return None


def _requires_cpr_regulator(ident: str, label: str, text: str):
    """cprRS INDUCES the Arn operon; it does not alter charge itself.

    Round 22's shape: a regulator's graph should END at the records that do the work,
    not restate their chemistry. Here that is the Ara4N route curated in round 75.
    """
    if "ARO:3003588" not in D.parse_relations(text)[0]:
        return "record carries no charge-alteration mechanism (ARO:3003588)"
    own = _own_definition(text).lower()
    if "induces the arn operon" not in own:
        return "own definition does not say it induces the Arn operon"
    return None


def _requires_lpx(ident: str, label: str, text: str):
    """Lipid A BIOSYNTHESIS mutations -- distinct from the charge-alteration routes.

    ARO:3003580's five routes all MODIFY an intact lipid A to neutralise its charge.
    These records mutate lipid A biosynthesis itself, so the target the peptide binds is
    altered or absent rather than merely less negative. Same molecule, opposite direction
    of intervention.
    """
    if "ARO:3000213" not in D.parse_relations(text)[0]:
        return "record carries no cell-wall-restructuring mechanism (ARO:3000213)"
    own = _own_definition(text).lower()
    if "biosynthesis of lipid a" not in own:
        return "own definition does not describe lipid A biosynthesis"
    return None


def _requires_two_component_efflux(ident: str, label: str, text: str):
    """A two-component protein that MODULATES efflux -- it does not transport anything."""
    if "ARO:0010000" not in D.parse_relations(text)[0]:
        return "record carries no efflux mechanism (ARO:0010000)"
    own = _own_definition(text).lower()
    if not re.search(r"two.component|sensor|response regulator|histidine kinase|"
                     r"transcription regulator", own):
        return "own definition does not describe a two-component or regulatory protein"
    return None


def _requires_mutant_efflux_regulator(ident: str, label: str, text: str):
    """A regulator whose MUTATION raises pump expression (ARO:3000219).

    Distinct from round 78's ARO:3000750 in two ways worth keeping apart:
      - there the protein regulates efflux as its normal job; here a MUTATION in it
        raises pump expression, which is why these records carry ARO:3000212;
      - CARD states a DIRECTION here ("result in increased expression") where round 78
        only had "directly or indirectly change rates", so this config may use the
        positive predicate and that one may not.

    This also unblocks AxyZ (round 79): it carries ARO:3000212 because it belongs to THIS
    family, and this family's sentence is the evidence for that id. Round 79 correctly
    refused to borrow the regulation snippet for it.
    """
    if "ARO:3000212" not in D.parse_relations(text)[0]:
        return "record carries no mutation mechanism (ARO:3000212)"
    return None


def _requires_emb_arabinosyltransferase(ident: str, label: str, text: str):
    """An emb arabinosyltransferase variant -- target alteration of a drug's own enzyme."""
    if "ARO:3000212" not in D.parse_relations(text)[0]:
        return "record carries no mutation mechanism (ARO:3000212)"
    return None


def _requires_pps_polyketide(ident: str, label: str, text: str):
    """A ppsA-E polyketide synthase variant."""
    if "ARO:3000212" not in D.parse_relations(text)[0]:
        return "record carries no mutation mechanism (ARO:3000212)"
    return None


def _requires_folp(ident: str, label: str, text: str):
    """A folP / dihydropteroate synthase variant."""
    if "ARO:3000212" not in D.parse_relations(text)[0]:
        return "record carries no mutation mechanism (ARO:3000212)"
    return None


def _requires_rpoc(ident: str, label: str, text: str):
    """An rpoC variant -- RNA polymerase beta prime subunit."""
    if "ARO:3000212" not in D.parse_relations(text)[0]:
        return "record carries no mutation mechanism (ARO:3000212)"
    return None


def _requires_liafsr(ident: str, label: str, text: str):
    """A liaFSR component -- envelope stress regulation, not an effector."""
    if "ARO:3000212" not in D.parse_relations(text)[0]:
        return "record carries no mutation mechanism (ARO:3000212)"
    return None


def _requires_mura(ident: str, label: str, text: str):
    """A murA variant -- resistance by OVEREXPRESSION, not by altered affinity."""
    if "ARO:3000212" not in D.parse_relations(text)[0]:
        return "record carries no mutation mechanism (ARO:3000212)"
    return None


def _requires_amg_modifying(ident: str, label: str, text: str):
    """An aminoglycoside-modifying enzyme (ARO:3007380)."""
    if "ARO:0001004" not in D.parse_relations(text)[0]:
        return "record carries no antibiotic-inactivation mechanism (ARO:0001004)"
    return None


def _requires_rv0678(ident: str, label: str, text: str):
    """Rv0678 -- a REPRESSOR of an efflux pump. Its mutation derepresses."""
    if "ARO:3000212" not in D.parse_relations(text)[0]:
        return "record carries no mutation mechanism (ARO:3000212)"
    return None


def _requires_named_efflux_subunit(ident: str, label: str, text: str):
    """A record whose own definition names it a SUBUNIT of a specific named complex.

    ARO:3000748 mixes four things (#229): genuine subunits, complexes filed as subunits
    (MexAB, MexCD, MexEF, MexGHI, MexMN, MexPQ, MexVW), a regulator (arlS) and the ini
    operon records whose efflux role is only proposed. Only the first group is curatable
    without the categorisation decision #229 is about.

    The pattern requires "IS the <role> OF <complex>" -- a subunit describes its place in
    something larger. A complex's definition says it "consists of" or "is composed of"
    components, which this deliberately does not match. Checked: widening to a bare
    "component" match pulls in all seven Mex complexes, so the narrow form is right.
    """
    if "ARO:0010000" not in D.parse_relations(text)[0]:
        return "record carries no efflux mechanism (ARO:0010000)"
    own = _own_definition(text).lower()
    # Also "required for X activity", not just "is the <role> OF X". Round 86's pattern
    # demanded the second form and missed MexG -- "a membrane protein REQUIRED FOR
    # MexGHI-OpmD efflux activity" -- which is as clear a subunit claim as MexA's.
    # Seventh too-narrow pattern of mine this session, found by counting rather than
    # by trusting the earlier count.
    if not (re.search(r"\b(is|are) (a |an |the )?"
                      r"(membrane fusion protein|periplasmic|inner membrane|outer membrane|"
                      r"subunit|component)\b", own)
            or re.search(r"required for .{0,40}efflux", own)):
        return ("own definition does not name it a subunit of a specific complex (#229 "
                "-- may be a complex, a regulator, or an operon member)")
    if "operon" in own:
        # Same correction as above: the check matches the word "operon", so the reason
        # must claim no more than that.
        return "own definition mentions an operon rather than a named subunit (#229)"
    return None


def _requires_van_protein(mech_id: str, marker: str, human: str):
    """Factory for the van records that are PROTEINS, not clusters.

    Rounds 20-23 curated the van enzymes; the remainder was written off as operon-level
    and blocked on the gene-cluster modelling question. Measuring the definitions showed
    8 of 35 are not cluster-level at all -- they describe individual proteins with their
    own mechanisms. This selects those by a marker phrase from the record's own text.
    """
    def _pred(ident: str, label: str, text: str):
        if mech_id not in D.parse_relations(text)[0]:
            return f"record carries no {human} mechanism ({mech_id})"
        own = _own_definition(text).lower()
        if re.search(r"cluster|operon|cassette", own):
            # Say what was MATCHED, not what I inferred from it. #256 caught the first
            # version claiming "describes a gene cluster" when the check only looks for
            # the words cluster/operon/cassette -- my own guard, on my own code.
            return ("own definition mentions a cluster, operon or cassette rather than "
                    "describing a single protein -- the gene-cluster modelling question "
                    "is still open")
        if marker not in own:
            return f"own definition does not describe {human}"
        return None
    return _pred


def _requires_vanj_homologue(ident: str, label: str, text: str):
    """A vanJ HOMOLOGUE -- and never vanJ itself.

    ARO:3002914 (vanJ) is a descendant of this family term and its own definition contains
    "vanJ", so a naive marker match gave it a "shares ancestor with vanJ" edge pointing at
    its own record. A homology edge to oneself is not a weaker claim, it is a meaningless
    one, and nothing but reading the written record would have caught it.
    """
    if ident == "ARO:3002914":
        return "record IS vanJ; the homologue config must not point it at itself"
    return _requires_van_protein("ARO:3000213", "homologue", "vanJ homology")(
        ident, label, text)


def _requires_ddl_ligase(ident: str, label: str, text: str):
    """The ddl ligases -- they make the SUSCEPTIBLE precursor, and losing them matters.

    Filed under the glycopeptide cluster families, and my cluster/protein split matched
    it as a cluster because the word appears at the END of its definition ("vancomycin
    resistance clusters"). It is a ligase family. Sixth time this session a pattern of
    mine was too coarse and the record only surfaced on reading.
    """
    if "ARO:3000213" not in D.parse_relations(text)[0]:
        return "record carries no cell-wall-restructuring mechanism (ARO:3000213)"
    if "non-van ligases" not in _own_definition(text).lower():
        return "own definition does not describe the non-van D-Ala-D-Ala ligases"
    return None


def _requires_armr(ident: str, label: str, text: str):
    """ArmR -- an ANTIrepressor, the record that defeated three keyword patterns."""
    if "antirepressor" not in _own_definition(text).lower():
        return "own definition does not describe an antirepressor"
    return None


def _requires_transcription_factor_regulator(ident: str, label: str, text: str):
    """A transcription factor regulating transporter genes -- NOT a two-component pair.

    Most of ARO:3000451's drafts are two-component PAIR records (baeSR, basRS, evgSA,
    kdpDE, liaFSR), which are #215's open question. PDR1 is not a pair; it is a single
    transcription factor, and round 78's shape fits it.
    """
    own = _own_definition(text).lower()
    if "transcription factor" not in own:
        return "own definition does not describe a transcription factor"
    if "two-component" in own or "two component" in own:
        return "own definition describes a two-component system (a pair record, #215)"
    return None


def _requires_tet34_protection(ident: str, label: str, text: str):
    """tet(34) -- target PROTECTION, the mechanism I refused four times and never wrote.

    Rounds 60, 70 and 91 all excluded this record from chemistry configs, correctly: it
    carries ARO:0001004, ARO:3000213 and ARO:3000450 while describing none of them. #267
    filed it as misfiled and there it sat. But CARD does state a mechanism -- purine
    nucleotide synthesis PROTECTS the protein synthesis pathway -- and refusing a record
    from the wrong config is not the same as having nothing to say about it.
    """
    if "protects the protein synthesis" not in _own_definition(text).lower():
        return "own definition does not describe protection of protein synthesis"
    return None


def _requires_generic_target_protection(ident: str, label: str, text: str):
    """The target-protection records the three mode-specific configs do not reach.

    Rounds 31, 44 and 45 curated TetM (ribosome displacement), FusB (EF-G rescue) and
    HelR (RNAP displacement) -- three distinct MODES, each with its own paper. These
    three records state protection without naming a mode, so none of those configs fits
    and none should be stretched to.
    """
    if "ARO:0001003" not in D.parse_relations(text)[0]:
        return "record carries no target-protection mechanism (ARO:0001003)"
    own = _own_definition(text).lower()
    if not re.search(r"protect|prevent antibiotic binding|altered sensitivity", own):
        return "own definition does not describe protection of a target"
    return None


def _drug_specific_inactivation_config(fam_id: str, drug: str, snippet: str) -> dict:
    """A drug-specific "enzymes inactivate X by chemical modification" family term.

    Round 85 built this shape for aminoglycosides. Bacitracin, fosfomycin and macrolides
    have the same one: a family term naming a drug and a reaction type, with the specific
    chemistries curated separately or not at all. No reaction node, for round 85's reason
    -- naming one would import a chemistry the term does not claim.
    """
    return {
        "curated": "2026-08-08T00:00:00Z",
        "precondition": _requires_mech("ARO:0001004", "antibiotic inactivation"),
        "reference": fam_id,
        "mech": {"ARO:0001004": snippet},
        "mech_res": snippet,
        "det_res": [
            {"reference": fam_id, "snippet": snippet,
             "notes": ("The claim at the level the family term makes it: enzymes inactivate "
                       + drug + ", by modification the term does not specify.")},
        ],
        "res_drug": snippet,
        "note": ("Inactivation of " + drug + " by unspecified modification. Deliberately no "
                 "reaction node -- naming one would import a chemistry this term does not "
                 "claim (round 85's rule for the aminoglycoside family term)."),
        "extra_nodes": [
            {"node_id": "modification", "label": "enzymatic modification of " + drug,
             "node_type": "MOLECULAR_FUNCTION",
             "description": "Deliberately unspecific -- see the config note."},
            {"node_id": "inactivated", "label": "modified, inactive " + drug,
             "node_type": "STATE", "description": "The product state. Ungrounded."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "modification",
             "predicate": "enables (modifies the drug)", "predicate_id": "RO:0002327",
             "evidence": [{"reference": fam_id, "snippet": snippet,
                           "notes": "The family term's own claim about what these enzymes do."}]},
            {"subject": "modification", "object": "drug0",
             "predicate": "has input (the drug)", "predicate_id": "RO:0002233",
             "evidence": [{"reference": fam_id, "snippet": snippet,
                           "notes": ("The antibiotic is the substrate -- inactivation, not "
                                     "target alteration.")}]},
            {"subject": "modification", "object": "inactivated",
             "predicate": "causally upstream of (inactivates the drug)",
             "predicate_id": "RO:0002411",
             "evidence": [{"reference": fam_id, "snippet": snippet,
                           "notes": "'inactivate' is the term's own verb."}]},
        ],
    }


def _requires_esx5_subunit(ident: str, label: str, text: str):
    """An ESX-5 secretion-system subunit whose own definition states the mechanism."""
    if "ARO:3000212" not in D.parse_relations(text)[0]:
        return "record carries no mutation mechanism (ARO:3000212)"
    if "esx-5 secretion system complex" not in _own_definition(text).lower():
        return "own definition does not place it in the ESX-5 secretion system complex"
    return None


def _fungal_p450_config(fam_id: str, snippet: str, drug: str, hedged: bool) -> dict:
    """A fungal cytochrome P450 family term -- round 66's EF-Tu shape.

    Round 84 read these and left them, calling them "thinner than EF-Tu". Comparing the
    two side by side, that judgement does not hold:

        EF-Tu  "Sequence variants of ELONGATION FACTOR TU that confer resistance..."
        P450   "Fungal CYTOCHROME P450 ENZYMES which include mutations ... to confer
                resistance to antifungal drug compounds."

    Both name a FUNCTION and claim resistance; neither gives a mechanism. Round 66
    curated the first on exactly that basis, so leaving the second was an inconsistency,
    not a standard.
    """
    note_hedge = (" NOTE the hedge: 'mutations OR OTHER MODIFICATIONS' -- the determinant "
                  "class is not even resolved to mutation." if hedged else
                  " Unlike its parent term, this one says 'mutations' without the "
                  "'or other modifications' hedge.")
    return {
        "curated": "2026-08-08T00:00:00Z",
        "precondition": _requires_mech("ARO:3000212", "mutation"),
        "reference": fam_id,
        "mech": {"ARO:3000212": snippet},
        "mech_res": snippet,
        "det_res": [
            {"reference": fam_id, "snippet": snippet,
             "notes": ("A functional identity and a resistance claim, with no mechanism "
                       "between them -- round 66's EF-Tu shape." + note_hedge)},
        ],
        "res_drug": snippet,
        "note": ("Mechanism deliberately NOT asserted. These are the azole target "
                 "(lanosterol 14-alpha-demethylase) in most fungi and the binding story "
                 "is standard, but CARD's sentence gives a function and a resistance claim "
                 "and nothing between. Round 66's position, and #219's lesson."),
        "extra_nodes": [
            {"node_id": "p450_activity", "label": "cytochrome P450 monooxygenase activity",
             "node_type": "MOLECULAR_FUNCTION",
             "description": "The one functional fact CARD's naming supplies. Ungrounded: not looked up rather than guessed (rounds 56-103)."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "p450_activity",
             "predicate": "enables (cytochrome P450 activity)", "predicate_id": "RO:0002327",
             "description": "What the determinant IS, which is all CARD's naming gives.",
             "evidence": [{"reference": fam_id, "snippet": snippet,
                           "notes": ("'Fungal cytochrome P450 enzymes' -- a functional name. "
                                     "NOT asserted: that the drug binds this enzyme, or how "
                                     "the mutations resist " + drug + ", neither of which "
                                     "CARD states.")}]},
        ],
    }


def _minimal_enzyme_config(fam_id: str, snippet: str, activity: str, extra_note: str = "") -> dict:
    """A record naming an enzyme and a resistance claim, with nothing between.

    Round 66's EF-Tu shape, which rounds 104 and 105 established should be applied
    consistently rather than judged case by case. The graph asserts the functional
    identity CARD's naming supplies and stops.
    """
    return {
        "curated": "2026-08-08T00:00:00Z",
        "precondition": _requires_mech("ARO:3000212", "mutation"),
        "reference": fam_id,
        "mech": {"ARO:3000212": snippet},
        "mech_res": snippet,
        "det_res": [
            {"reference": fam_id, "snippet": snippet,
             "notes": ("A functional identity and a resistance claim, with no mechanism "
                       "between them -- round 66's EF-Tu shape." + (" " + extra_note if extra_note else ""))},
        ],
        "res_drug": snippet,
        "note": ("Mechanism NOT asserted: CARD names what the protein is and that its "
                 "mutations resist, and nothing joins the two." + (" " + extra_note if extra_note else "")),
        "extra_nodes": [
            {"node_id": "activity", "label": activity, "node_type": "MOLECULAR_FUNCTION",
             "description": "The one functional fact CARD's naming supplies. Ungrounded: not looked up rather than guessed (rounds 56-109)."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "activity",
             "predicate": "enables (" + activity + ")", "predicate_id": "RO:0002327",
             "description": "What the determinant IS, which is all CARD gives.",
             "evidence": [{"reference": fam_id, "snippet": snippet,
                           "notes": "The functional name. NOT asserted: any interaction with the drug, which CARD does not describe."}]},
        ],
    }


FAMILY_SNIPPETS = {
    # furA (ARO:3004897) -- a repressor of katG, with the DNA-binding mechanism named,
    # and no resistance claim at all.
    #
    # katG activates isoniazid, so repressing it is the obvious resistance route -- and
    # CARD's sentence never mentions isoniazid, resistance or mutations. It describes a
    # regulator and stops. The most complete regulatory sentence in the corpus attached to
    # the least resistance content.
    "ARO:3004897": {
        "curated": "2026-08-10T00:00:00Z",
        "precondition": _requires_mech("ARO:3000212", "mutation"),
        "reference": "ARO:3004897",
        "mech": {"ARO:3000212": "Transcriptional regulator furA, represses the transcription of the catalase-peroxidase gene katG and its own transcription by binding to the promoter region."},
        "mech_res": "Transcriptional regulator furA, represses the transcription of the catalase-peroxidase gene katG and its own transcription by binding to the promoter region.",
        "det_res": [
            {"reference": "ARO:3004897", "snippet": "Transcriptional regulator furA, represses the transcription of the catalase-peroxidase gene katG and its own transcription by binding to the promoter region.",
             "notes": "Direction ('REPRESSES'), targets (katG AND its own gene), and the molecular basis ('BY BINDING TO THE PROMOTER REGION') -- more regulatory detail than any other record here. And no mention of isoniazid, resistance or mutations."},
        ],
        "res_drug": "Transcriptional regulator furA, represses the transcription of the catalase-peroxidase gene katG and its own transcription by binding to the promoter region.",
        "note": ("A katG repressor with the DNA-binding basis stated and NO resistance "
                 "claim. katG activates isoniazid, so repressing it is the obvious route "
                 "-- CARD's sentence contains neither the drug nor the word resistance, so "
                 "no such edge is written. Round 106's rpoB position, inverted: there the "
                 "drug was known and unstated, here the whole resistance link is."),
        "extra_nodes": [
            {"node_id": "katg_transcription", "label": "transcription of the catalase-peroxidase gene katG",
             "node_type": "BIOLOGICAL_PROCESS",
             "description": "What furA represses. Ungrounded: katG has its own KB records, and pointing at one would pick arbitrarily."},
            {"node_id": "promoter_binding", "label": "binding to the katG promoter region",
             "node_type": "STATE",
             "description": "The molecular basis CARD gives -- rare in this corpus's regulator records."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "promoter_binding",
             "predicate": "molecularly interacts with (binds the promoter region)",
             "predicate_id": "RO:0002436",
             "description": "The mechanism of the repression, which most regulator records here leave out entirely (rounds 78, 79, 110, 115).",
             "evidence": [{"reference": "ARO:3004897", "snippet": "Transcriptional regulator furA, represses the transcription of the catalase-peroxidase gene katG and its own transcription by binding to the promoter region.",
                           "notes": "'by binding to the promoter region'."}]},
            {"subject": "promoter_binding", "object": "katg_transcription",
             "predicate": "negatively regulates (represses katG transcription)",
             "predicate_id": "RO:0002212",
             "description": "The NEGATIVE form, licensed by CARD's own 'represses'. NOT asserted: that repressing katG confers isoniazid resistance -- CARD's sentence mentions neither the drug nor resistance.",
             "evidence": [{"reference": "ARO:3004897", "snippet": "Transcriptional regulator furA, represses the transcription of the catalase-peroxidase gene katG and its own transcription by binding to the promoter region.",
                           "notes": "'represses the transcription of the catalase-peroxidase gene katG and its own transcription'."}]},
        ],
    },
    # mshC (ARO:3004904) -- the mshC record that DOES carry a reaction.
    #
    # Round 94 left a different mshC record (ARO:3004889) reading only "Mutations ...
    # resulting in the inability for antibiotic to function". This one adds the chemistry:
    # "It catalyzes the ATP-dependent condensation of GlcN-Ins and L-cysteine". Two records
    # for one gene, one curatable and one not -- as with mshA/mshB in round 109.
    "ARO:3004904": {
        "curated": "2026-08-10T00:00:00Z",
        "precondition": _requires_mech("ARO:3000212", "mutation"),
        "reference": "ARO:3004904",
        "mech": {"ARO:3000212": "Mutations that occur on the mshC gene resulting in the inability for isoniazid to function. It catalyzes the ATP-dependent condensation of GlcN-Ins and L-cysteine to form L-Cys-GlcN-Ins."},
        "mech_res": "Mutations that occur on the mshC gene resulting in the inability for isoniazid to function. It catalyzes the ATP-dependent condensation of GlcN-Ins and L-cysteine to form L-Cys-GlcN-Ins.",
        "det_res": [
            {"reference": "ARO:3004904", "snippet": "Mutations that occur on the mshC gene resulting in the inability for isoniazid to function. It catalyzes the ATP-dependent condensation of GlcN-Ins and L-cysteine to form L-Cys-GlcN-Ins.",
             "notes": "The reaction with both substrates and the product named -- which the OTHER mshC record (ARO:3004889, left in round 94) does not have. Still 'to FUNCTION', so still no prodrug edge (rounds 95, 110, 112, 118)."},
        ],
        "res_drug": "Mutations that occur on the mshC gene resulting in the inability for isoniazid to function. It catalyzes the ATP-dependent condensation of GlcN-Ins and L-cysteine to form L-Cys-GlcN-Ins.",
        "note": ("The mshC record that carries its reaction. Its sibling ARO:3004889 says "
                 "only 'inability for antibiotic to function' and remains a draft -- two "
                 "records for one gene, one curatable and one not, as with mshA and mshB "
                 "(round 109). The word is still 'function', so no activation edge."),
        "extra_nodes": [
            {"node_id": "condensation", "label": "ATP-dependent GlcN-Ins / L-cysteine ligase activity",
             "node_type": "MOLECULAR_FUNCTION", "description": "Ungrounded: not looked up rather than guessed."},
            {"node_id": "cys_glcn_ins", "label": "L-Cys-GlcN-Ins",
             "node_type": "CHEMICAL", "description": "The product CARD names. Ungrounded."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "condensation",
             "predicate": "enables (ATP-dependent condensation)", "predicate_id": "RO:0002327",
             "evidence": [{"reference": "ARO:3004904", "snippet": "Mutations that occur on the mshC gene resulting in the inability for isoniazid to function. It catalyzes the ATP-dependent condensation of GlcN-Ins and L-cysteine to form L-Cys-GlcN-Ins.",
                           "notes": "'It catalyzes the ATP-dependent condensation of GlcN-Ins and L-cysteine'."}]},
            {"subject": "condensation", "object": "cys_glcn_ins",
             "predicate": "has output (L-Cys-GlcN-Ins)", "predicate_id": "RO:0002234",
             "evidence": [{"reference": "ARO:3004904", "snippet": "Mutations that occur on the mshC gene resulting in the inability for isoniazid to function. It catalyzes the ATP-dependent condensation of GlcN-Ins and L-cysteine to form L-Cys-GlcN-Ins.",
                           "notes": "'to form L-Cys-GlcN-Ins'. NOT asserted: any link to isoniazid, which CARD frames only as 'inability to function'."}]},
        ],
    },
    # ald (ARO:3004943) -- the cycloserine partner of ddlA (round 116).
    #
    # ddlA ligates two D-alanines and cycloserine mimics D-alanine. ald supplies L-alanine
    # to the same wall. CARD gives the pathway role and says mutations "can cause
    # cycloserine to not function" -- the "FUNCTION" word again (rounds 95, 110, 112), so
    # no prodrug or activation edge, even though the two records sit either side of the
    # same step.
    "ARO:3004943": {
        "curated": "2026-08-10T00:00:00Z",
        "precondition": _requires_mech("ARO:3000212", "mutation"),
        "reference": "ARO:3004943",
        "mech": {"ARO:3000212": "ald plays a role in cell wall synthesis as L-alanine is an important constituent of the peptidoglycan layer. Resistance due to mutations in ald can cause cycloserine to not function."},
        "mech_res": "ald plays a role in cell wall synthesis as L-alanine is an important constituent of the peptidoglycan layer. Resistance due to mutations in ald can cause cycloserine to not function.",
        "det_res": [
            {"reference": "ARO:3004943", "snippet": "ald plays a role in cell wall synthesis as L-alanine is an important constituent of the peptidoglycan layer. Resistance due to mutations in ald can cause cycloserine to not function.",
             "notes": "Pathway role, and 'can cause cycloserine to NOT FUNCTION' -- the same verb as mshC, nudC and mshA's counterpart. Round 95's line applies: 'function' does not license an activation or mimicry edge, even though ddlA (round 116) supplies exactly that story for the neighbouring step."},
        ],
        "res_drug": "ald plays a role in cell wall synthesis as L-alanine is an important constituent of the peptidoglycan layer. Resistance due to mutations in ald can cause cycloserine to not function.",
        "note": ("L-alanine supply to the peptidoglycan layer. NOT asserted: any relation "
                 "to cycloserine's D-alanine mimicry, which ddlA's record (round 116) "
                 "states for its own step and this one does not."),
        "extra_nodes": [
            {"node_id": "l_alanine", "label": "L-alanine, a constituent of the peptidoglycan layer",
             "node_type": "CHEMICAL", "description": "Ungrounded: not looked up rather than guessed."},
            {"node_id": "wall_synthesis", "label": "cell wall synthesis",
             "node_type": "BIOLOGICAL_PROCESS", "description": "Ungrounded."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "wall_synthesis",
             "predicate": "participates in (cell wall synthesis)", "predicate_id": "RO:0000056",
             "description": "'Participates in', matching CARD's 'plays a role in'.",
             "evidence": [{"reference": "ARO:3004943", "snippet": "ald plays a role in cell wall synthesis as L-alanine is an important constituent of the peptidoglycan layer. Resistance due to mutations in ald can cause cycloserine to not function.",
                           "notes": "'ald plays a role in cell wall synthesis'."}]},
            {"subject": "l_alanine", "object": "wall_synthesis",
             "predicate": "part of (the peptidoglycan layer)", "predicate_id": "BFO:0000050",
             "evidence": [{"reference": "ARO:3004943", "snippet": "ald plays a role in cell wall synthesis as L-alanine is an important constituent of the peptidoglycan layer. Resistance due to mutations in ald can cause cycloserine to not function.",
                           "notes": "'L-alanine is an important constituent of the peptidoglycan layer'. NOT asserted: the link to cycloserine, whose mimicry ddlA's record describes."}]},
        ],
    },
    # BLMT (ARO:3005036) -- resistance stated three times and never explained.
    "ARO:3005036": {
        "curated": "2026-08-10T00:00:00Z",
        "precondition": _requires_mech("ARO:0001004", "antibiotic inactivation"),
        "reference": "ARO:3005036",
        "mech": {"ARO:0001004": "BLMT is a bleomycin (Bm) resistance protein, encoded by the ble gene on the transposon Tn5. This protein confers a survival advantage to Escherichia coli host cells. BLMT confers resistance to bleomycin."},
        "mech_res": "BLMT is a bleomycin (Bm) resistance protein, encoded by the ble gene on the transposon Tn5. This protein confers a survival advantage to Escherichia coli host cells. BLMT confers resistance to bleomycin.",
        "det_res": [
            {"reference": "ARO:3005036", "snippet": "BLMT is a bleomycin (Bm) resistance protein, encoded by the ble gene on the transposon Tn5. This protein confers a survival advantage to Escherichia coli host cells. BLMT confers resistance to bleomycin.",
             "notes": "Three sentences that each restate the resistance -- 'a bleomycin resistance protein', 'confers a survival advantage', 'confers resistance to bleomycin' -- and none says how. It carries the INACTIVATION mechanism id while describing no reaction."},
        ],
        "res_drug": "BLMT is a bleomycin (Bm) resistance protein, encoded by the ble gene on the transposon Tn5. This protein confers a survival advantage to Escherichia coli host cells. BLMT confers resistance to bleomycin.",
        "note": ("A resistance protein whose mechanism is stated nowhere. It carries "
                 "ARO:0001004 (inactivation) and CARD describes no chemistry -- BLMT in "
                 "fact SEQUESTERS bleomycin (round 72's shape), and that is uncited here, "
                 "so no binding edge is written. The graph carries the genetic context CARD "
                 "does give: the ble gene on transposon Tn5."),
        "extra_nodes": [
            {"node_id": "tn5", "label": "the ble gene on transposon Tn5",
             "node_type": "NUCLEIC_ACID",
             "description": "The genetic context, which is the only thing CARD adds beyond restating the resistance. Ungrounded."},
        ],
        "extra_edges": [
            {"subject": "tn5", "object": "determinant",
             "predicate": "causally upstream of (encodes BLMT)", "predicate_id": "RO:0002411",
             "description": "The only non-restating fact in the definition. NOT asserted: sequestration, which is BLMT's actual mechanism and appears in no sentence here.",
             "evidence": [{"reference": "ARO:3005036", "snippet": "BLMT is a bleomycin (Bm) resistance protein, encoded by the ble gene on the transposon Tn5. This protein confers a survival advantage to Escherichia coli host cells. BLMT confers resistance to bleomycin.",
                           "notes": "'encoded by the ble gene on the transposon Tn5'."}]},
        ],
    },
    # MSH2 (ARO:3009134) -- resistance across three unrelated drug classes at once.
    #
    # Every other record in this corpus resists one drug or one class. MSH2 is a MISMATCH
    # REPAIR gene, and strains altered in it resist polyenes, echinocandins AND azoles --
    # three classes with three different targets. The obvious reading is hypermutation, and
    # CARD does not say it, so it is not written.
    "ARO:3009134": {
        "curated": "2026-08-10T00:00:00Z",
        "precondition": _requires_mech("ARO:3000212", "mutation"),
        "reference": "ARO:3009134",
        "mech": {"ARO:3000212": "MSH2 is a mismatch repair gene in fungi. Strains with alterations in this gene exhibit the resistance to Polyenes (Amphotericin B), Echinocandins (Caspofungin, Micafungin), and Azoles (Fluconazole, Voriconazole)."},
        "mech_res": "MSH2 is a mismatch repair gene in fungi. Strains with alterations in this gene exhibit the resistance to Polyenes (Amphotericin B), Echinocandins (Caspofungin, Micafungin), and Azoles (Fluconazole, Voriconazole).",
        "det_res": [
            {"reference": "ARO:3009134", "snippet": "MSH2 is a mismatch repair gene in fungi. Strains with alterations in this gene exhibit the resistance to Polyenes (Amphotericin B), Echinocandins (Caspofungin, Micafungin), and Azoles (Fluconazole, Voriconazole).",
             "notes": "Three drug classes with three different targets, from one altered gene. CARD names the gene's function (mismatch repair) and lists the classes, and joins them by nothing. NOTE the phrasing: 'STRAINS WITH ALTERATIONS ... EXHIBIT' -- an observation about strains, not a claim about the protein."},
        ],
        "res_drug": "MSH2 is a mismatch repair gene in fungi. Strains with alterations in this gene exhibit the resistance to Polyenes (Amphotericin B), Echinocandins (Caspofungin, Micafungin), and Azoles (Fluconazole, Voriconazole).",
        "note": ("Mismatch repair, and resistance to three unrelated drug classes. The "
                 "obvious reading is that losing repair raises the mutation rate and "
                 "resistance follows by any route -- hypermutation. CARD does not say it, "
                 "so it is not written. The graph carries the gene's function and stops."),
        "extra_nodes": [
            {"node_id": "mismatch_repair", "label": "DNA mismatch repair",
             "node_type": "BIOLOGICAL_PROCESS",
             "description": "The one functional fact CARD gives. Ungrounded: not looked up rather than guessed."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "mismatch_repair",
             "predicate": "participates in (DNA mismatch repair)", "predicate_id": "RO:0000056",
             "description": "What the gene IS. NOT asserted: that losing repair causes hypermutation, or that hypermutation is how three drug classes are resisted at once -- neither is in CARD's two sentences.",
             "evidence": [{"reference": "ARO:3009134", "snippet": "MSH2 is a mismatch repair gene in fungi. Strains with alterations in this gene exhibit the resistance to Polyenes (Amphotericin B), Echinocandins (Caspofungin, Micafungin), and Azoles (Fluconazole, Voriconazole).",
                           "notes": "'MSH2 is a mismatch repair gene in fungi'."}]},
        ],
    },
    # pepQ (ARO:3007690) -- a "putative" function and a "cross-resistance" phenotype.
    "ARO:3007690": {
        "curated": "2026-08-10T00:00:00Z",
        "precondition": _requires_mech("ARO:3000212", "mutation"),
        "reference": "ARO:3007690",
        "mech": {"ARO:3000212": "Rv2535c or pepQ encodes a putative Xaa-Pro aminopeptidase and is a new genetic determinant of low-level bedaquiline and clofazimine cross-resistance in Mycobacterium tuberculosis when mutated."},
        "mech_res": "Rv2535c or pepQ encodes a putative Xaa-Pro aminopeptidase and is a new genetic determinant of low-level bedaquiline and clofazimine cross-resistance in Mycobacterium tuberculosis when mutated.",
        "det_res": [
            {"reference": "ARO:3007690", "snippet": "Rv2535c or pepQ encodes a putative Xaa-Pro aminopeptidase and is a new genetic determinant of low-level bedaquiline and clofazimine cross-resistance in Mycobacterium tuberculosis when mutated.",
             "notes": "Four qualifiers in one sentence: the function is 'PUTATIVE', the determinant is 'NEW', the resistance is 'LOW-LEVEL', and it is 'CROSS-RESISTANCE' to two drugs. All four are kept."},
        ],
        "res_drug": "Rv2535c or pepQ encodes a putative Xaa-Pro aminopeptidase and is a new genetic determinant of low-level bedaquiline and clofazimine cross-resistance in Mycobacterium tuberculosis when mutated.",
        "note": ("A putative aminopeptidase conferring low-level cross-resistance. The "
                 "function itself is hedged -- 'encodes a PUTATIVE Xaa-Pro aminopeptidase' "
                 "-- which is a step further than round 111's drmA, where the protein was "
                 "'uncharacterized' but its identity was not in doubt."),
        "extra_nodes": [
            {"node_id": "aminopeptidase", "label": "putative Xaa-Pro aminopeptidase activity",
             "node_type": "MOLECULAR_FUNCTION",
             "description": "The word 'putative' is CARD's and is kept in the label -- the assignment itself is uncertain, not merely uncharacterised."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "aminopeptidase",
             "predicate": "enables (putative Xaa-Pro aminopeptidase activity)",
             "predicate_id": "RO:0002327",
             "description": "Hedged at the level CARD hedges it. NOT asserted: any route from peptidase activity to bedaquiline or clofazimine, which CARD does not describe.",
             "evidence": [{"reference": "ARO:3007690", "snippet": "Rv2535c or pepQ encodes a putative Xaa-Pro aminopeptidase and is a new genetic determinant of low-level bedaquiline and clofazimine cross-resistance in Mycobacterium tuberculosis when mutated.",
                           "notes": "'encodes a putative Xaa-Pro aminopeptidase'."}]},
        ],
    },
    # ddlA (ARO:3004939) -- SUBSTRATE-ANALOG inhibition, stated structurally.
    #
    # Round 82's folP was competitive inhibition, and CARD said so in those words. Here it
    # says WHY: "Cycloserine has a SIMILAR STRUCTURE to d-alanine". That is the structural
    # basis of a substrate analog, and it is the only record in this corpus that gives one.
    #
    # Note what is NOT said: that mutations in ddlA resist. CARD describes the enzyme and
    # the drug's mimicry and stops -- so the resistance edge the family term implies is
    # not written.
    "ARO:3004939": {
        "curated": "2026-08-10T00:00:00Z",
        "precondition": _requires_mech("ARO:3000212", "mutation"),
        "reference": "ARO:3004939",
        "mech": {"ARO:3000212": "ddlA catalyzes the ATP-driven ligation of two D-alanine molecules to form the D-alanyl-D-alanine dipeptide, key in forming the cell wall. Cycloserine has a similar structure to d-alanine and inhibits the growth of the cell wall."},
        "mech_res": "ddlA catalyzes the ATP-driven ligation of two D-alanine molecules to form the D-alanyl-D-alanine dipeptide, key in forming the cell wall. Cycloserine has a similar structure to d-alanine and inhibits the growth of the cell wall.",
        "det_res": [
            {"reference": "ARO:3004939", "snippet": "ddlA catalyzes the ATP-driven ligation of two D-alanine molecules to form the D-alanyl-D-alanine dipeptide, key in forming the cell wall. Cycloserine has a similar structure to d-alanine and inhibits the growth of the cell wall.",
             "notes": "The reaction with its cosubstrate ('ATP-driven ligation of TWO D-alanine molecules'), and the drug's structural basis: 'Cycloserine has a SIMILAR STRUCTURE to d-alanine'. NOT stated: what mutations in ddlA do -- CARD describes the enzyme and the mimicry and stops."},
        ],
        "res_drug": "ddlA catalyzes the ATP-driven ligation of two D-alanine molecules to form the D-alanyl-D-alanine dipeptide, key in forming the cell wall. Cycloserine has a similar structure to d-alanine and inhibits the growth of the cell wall.",
        "note": ("Substrate-analog inhibition, with the structural basis given -- the only "
                 "record here that says WHY a drug competes. Round 82's folP said the "
                 "inhibition was competitive; this says the drug resembles the substrate. "
                 "NOT asserted: the mutation's effect, which CARD does not describe."),
        "extra_nodes": [
            {"node_id": "ligation", "label": "D-Ala-D-Ala ligase activity (ATP-driven)",
             "node_type": "MOLECULAR_FUNCTION",
             "description": "Ungrounded: not looked up rather than guessed (rounds 56-114)."},
            {"node_id": "dala", "label": "D-alanine, the substrate cycloserine resembles",
             "node_type": "CHEMICAL",
             "description": "Ungrounded: rounds 20-23 recorded the same CHEBI gap for the wall precursors."},
            {"node_id": "wall_growth", "label": "cell wall growth",
             "node_type": "BIOLOGICAL_PROCESS", "description": "What the drug inhibits. Ungrounded."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "ligation",
             "predicate": "enables (D-Ala-D-Ala ligation)", "predicate_id": "RO:0002327",
             "evidence": [{"reference": "ARO:3004939", "snippet": "ddlA catalyzes the ATP-driven ligation of two D-alanine molecules to form the D-alanyl-D-alanine dipeptide, key in forming the cell wall. Cycloserine has a similar structure to d-alanine and inhibits the growth of the cell wall.",
                           "notes": "'ddlA catalyzes the ATP-driven ligation of two D-alanine molecules'."}]},
            {"subject": "ligation", "object": "dala",
             "predicate": "has input (D-alanine)", "predicate_id": "RO:0002233",
             "evidence": [{"reference": "ARO:3004939", "snippet": "ddlA catalyzes the ATP-driven ligation of two D-alanine molecules to form the D-alanyl-D-alanine dipeptide, key in forming the cell wall. Cycloserine has a similar structure to d-alanine and inhibits the growth of the cell wall.",
                           "notes": "Two molecules of it, per the same clause."}]},
            {"subject": "drug0", "object": "dala",
             "predicate": "similar to (cycloserine resembles D-alanine)",
             "predicate_id": "RO:0002158",
             "description": "The structural basis of the inhibition, and the reason this is substrate-analog rather than allosteric. RO:0002158 'shares ancestor with' is the closest verified predicate -- checked in round 89, where RO:0002159 turned out to be the developmental sense.",
             "evidence": [{"reference": "ARO:3004939", "snippet": "ddlA catalyzes the ATP-driven ligation of two D-alanine molecules to form the D-alanyl-D-alanine dipeptide, key in forming the cell wall. Cycloserine has a similar structure to d-alanine and inhibits the growth of the cell wall.",
                           "notes": "'Cycloserine has a similar structure to d-alanine'."}]},
            {"subject": "drug0", "object": "wall_growth",
             "predicate": "negatively regulates (inhibits cell wall growth)",
             "predicate_id": "RO:0002212",
             "evidence": [{"reference": "ARO:3004939", "snippet": "ddlA catalyzes the ATP-driven ligation of two D-alanine molecules to form the D-alanyl-D-alanine dipeptide, key in forming the cell wall. Cycloserine has a similar structure to d-alanine and inhibits the growth of the cell wall.",
                           "notes": "'and inhibits the growth of the cell wall'."}]},
        ],
    },
    # FKS2 (ARO:3007548) -- the echinocandin target, named with its product.
    "ARO:3007548": {
        "curated": "2026-08-10T00:00:00Z",
        "precondition": _requires_mech("ARO:3000212", "mutation"),
        "reference": "ARO:3007548",
        "mech": {"ARO:3000212": "Glucan synthase FKS2 is involved in the production of the fungal cell wall by the synthesis of the core component beta-1,3-glucan in Candida spp. Mutations in FKS2 have been shown to confer resistance to echinocandin antibiotic micafungin."},
        "mech_res": "Glucan synthase FKS2 is involved in the production of the fungal cell wall by the synthesis of the core component beta-1,3-glucan in Candida spp. Mutations in FKS2 have been shown to confer resistance to echinocandin antibiotic micafungin.",
        "det_res": [
            {"reference": "ARO:3007548", "snippet": "Glucan synthase FKS2 is involved in the production of the fungal cell wall by the synthesis of the core component beta-1,3-glucan in Candida spp. Mutations in FKS2 have been shown to confer resistance to echinocandin antibiotic micafungin.",
             "notes": "Enzyme, product and pathway named, resistance attributed ('have been SHOWN to') and scoped to one drug (micafungin). NOT stated: that echinocandins inhibit glucan synthase, which is why they work -- CARD names the enzyme and the drug and does not join them."},
        ],
        "res_drug": "Glucan synthase FKS2 is involved in the production of the fungal cell wall by the synthesis of the core component beta-1,3-glucan in Candida spp. Mutations in FKS2 have been shown to confer resistance to echinocandin antibiotic micafungin.",
        "note": ("Glucan synthase, the echinocandin target. NOT asserted: that echinocandins "
                 "inhibit it. That is textbook and this is the record it belongs to -- the "
                 "same position as rpoB (round 106) for rifampicin."),
        "extra_nodes": [
            {"node_id": "glucan_synthesis", "label": "beta-1,3-glucan synthase activity",
             "node_type": "MOLECULAR_FUNCTION", "description": "Ungrounded."},
            {"node_id": "cell_wall", "label": "fungal cell wall production",
             "node_type": "BIOLOGICAL_PROCESS", "description": "Ungrounded."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "glucan_synthesis",
             "predicate": "enables (beta-1,3-glucan synthesis)", "predicate_id": "RO:0002327",
             "evidence": [{"reference": "ARO:3007548", "snippet": "Glucan synthase FKS2 is involved in the production of the fungal cell wall by the synthesis of the core component beta-1,3-glucan in Candida spp. Mutations in FKS2 have been shown to confer resistance to echinocandin antibiotic micafungin.",
                           "notes": "'the synthesis of the core component beta-1,3-glucan'."}]},
            {"subject": "glucan_synthesis", "object": "cell_wall",
             "predicate": "part of (fungal cell wall production)", "predicate_id": "BFO:0000050",
             "evidence": [{"reference": "ARO:3007548", "snippet": "Glucan synthase FKS2 is involved in the production of the fungal cell wall by the synthesis of the core component beta-1,3-glucan in Candida spp. Mutations in FKS2 have been shown to confer resistance to echinocandin antibiotic micafungin.",
                           "notes": "'involved in the production of the fungal cell wall'. NOT asserted: that micafungin inhibits this, which CARD does not say."}]},
        ],
    },
    # ampR (ARO:3007797) -- regulator, and the outcome is a mechanism ALREADY CURATED.
    #
    # Mutations confer resistance "due to BETA-LACTAMASE OVEREXPRESSION" -- and the
    # beta-lactamases are curated (rounds 12-16, 59). Round 22's rule applies: the graph
    # ends at the overexpression, and the hydrolysis chemistry lives on those records.
    "ARO:3007797": {
        "curated": "2026-08-08T00:00:00Z",
        "precondition": _requires_mech("ARO:3000212", "mutation"),
        "reference": "ARO:3007797",
        "mech": {"ARO:3000212": "ampR is a LysR-type transcriptional regulator for beta-lactamase-encoding gene expression. Mutations in ampR of certain organisms have been shown to confer resistance to antibiotics due to beta-lactamase overexpression."},
        "mech_res": "ampR is a LysR-type transcriptional regulator for beta-lactamase-encoding gene expression. Mutations in ampR of certain organisms have been shown to confer resistance to antibiotics due to beta-lactamase overexpression.",
        "det_res": [
            {"reference": "ARO:3007797", "snippet": "ampR is a LysR-type transcriptional regulator for beta-lactamase-encoding gene expression. Mutations in ampR of certain organisms have been shown to confer resistance to antibiotics due to beta-lactamase overexpression.",
             "notes": "A regulator whose mutation raises its target's expression -- Upc2's shape (round 110) with a different target class. CARD names the outcome: 'due to BETA-LACTAMASE OVEREXPRESSION'. NOTE the scope hedge: 'of CERTAIN ORGANISMS', and the attribution: 'have been SHOWN to'."},
        ],
        "res_drug": "ampR is a LysR-type transcriptional regulator for beta-lactamase-encoding gene expression. Mutations in ampR of certain organisms have been shown to confer resistance to antibiotics due to beta-lactamase overexpression.",
        "note": ("Regulation ending at beta-lactamase overexpression. The hydrolysis "
                 "chemistry is curated on the beta-lactamase records (rounds 12-16, 59), so "
                 "round 22's rule applies and this graph stops rather than restating it."),
        "extra_nodes": [
            {"node_id": "bla_expression", "label": "beta-lactamase expression",
             "node_type": "BIOLOGICAL_PROCESS",
             "description": "Where this graph stops. Ungrounded: CARD names no specific beta-lactamase, and picking one would choose arbitrarily among hundreds of curated records."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "bla_expression",
             "predicate": "regulates (beta-lactamase gene expression)",
             "predicate_id": "RO:0002211",
             "description": "Neutral for the NORMAL role -- CARD says 'transcriptional regulator', not activator or repressor. The MUTATION's effect is overexpression, which is the next edge.",
             "evidence": [{"reference": "ARO:3007797", "snippet": "ampR is a LysR-type transcriptional regulator for beta-lactamase-encoding gene expression. Mutations in ampR of certain organisms have been shown to confer resistance to antibiotics due to beta-lactamase overexpression.",
                           "notes": "'a LysR-type transcriptional regulator for beta-lactamase-encoding gene expression' -- no direction given for the wild-type role."}]},
            {"subject": "determinant", "object": "resistance",
             "predicate": "causally upstream of (via beta-lactamase overexpression)",
             "predicate_id": "RO:0002411",
             "description": "The mutation's outcome, with CARD's own 'due to'.",
             "evidence": [{"reference": "ARO:3007797", "snippet": "ampR is a LysR-type transcriptional regulator for beta-lactamase-encoding gene expression. Mutations in ampR of certain organisms have been shown to confer resistance to antibiotics due to beta-lactamase overexpression.",
                           "notes": "'Mutations in ampR ... confer resistance to antibiotics DUE TO beta-lactamase overexpression'. NOT asserted: how beta-lactamases resist, which their own records carry."}]},
        ],
    },
    # Fungal SREBPs (ARO:3007549) -- target overexpression, and CARD hedges the direction.
    "ARO:3007549": {
        "curated": "2026-08-08T00:00:00Z",
        "precondition": _requires_mech("ARO:3007609", "target overexpression"),
        "reference": "ARO:3007549",
        "mech": {"ARO:3007609": "Fungal sterol regulatory element binding proteins are transcription factors that modulate antibiotic-susceptible genes. Mutations in these proteins confer resistance to antifungal drug compounds through differential gene regulation."},
        "mech_res": "Fungal sterol regulatory element binding proteins are transcription factors that modulate antibiotic-susceptible genes. Mutations in these proteins confer resistance to antifungal drug compounds through differential gene regulation.",
        "det_res": [
            {"reference": "ARO:3007549", "snippet": "Fungal sterol regulatory element binding proteins are transcription factors that modulate antibiotic-susceptible genes. Mutations in these proteins confer resistance to antifungal drug compounds through differential gene regulation.",
             "notes": "Transcription factors whose mutations resist 'through DIFFERENTIAL GENE REGULATION' -- CARD's phrase for a direction it declines to give, unlike Upc2 (round 110) which names 'upregulating ERG11'."},
        ],
        "res_drug": "Fungal sterol regulatory element binding proteins are transcription factors that modulate antibiotic-susceptible genes. Mutations in these proteins confer resistance to antifungal drug compounds through differential gene regulation.",
        "note": ("Transcriptional regulation with the direction explicitly unresolved: "
                 "'differential gene regulation' is CARD declining to say up or down. "
                 "Contrast Upc2 (round 110), same mechanism id, where CARD says "
                 "'by upregulating ERG11 expression' and the edge is positive."),
        "extra_nodes": [
            {"node_id": "susceptible_genes", "label": "antibiotic-susceptible genes",
             "node_type": "NUCLEIC_ACID",
             "description": "CARD's own phrase. Ungrounded, and deliberately vague -- no gene is named."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "susceptible_genes",
             "predicate": "regulates (differential gene regulation)", "predicate_id": "RO:0002211",
             "description": "Neutral RO:0002211, licensed by 'DIFFERENTIAL' -- the one word in this corpus that states a direction is deliberately unspecified rather than merely absent.",
             "evidence": [{"reference": "ARO:3007549", "snippet": "Fungal sterol regulatory element binding proteins are transcription factors that modulate antibiotic-susceptible genes. Mutations in these proteins confer resistance to antifungal drug compounds through differential gene regulation.",
                           "notes": "'modulate antibiotic-susceptible genes' and 'through differential gene regulation'. NOT asserted: which genes, or which way."}]},
        ],
    },
    # thyA (ARO:3004152) -- prodrug-activation loss, and CARD says HOW the mutation works.
    #
    # Round 113's folC named the intermediate; this one names the DEFECT: "disrupting the
    # substrate-binding affinity and catalytic activity". Same drug (p-aminosalicylic acid),
    # same pathway, and between them the two records give more of this mechanism than any
    # other pair in the corpus.
    "ARO:3004152": {
        "curated": "2026-08-08T00:00:00Z",
        "precondition": _requires_mech("ARO:3000212", "mutation"),
        "reference": "ARO:3004152",
        "mech": {"ARO:3000212": "Antibiotic resistant form of thymidylate synthase (synthetase), an enzyme that catalyzes the conversion of dUMP to dTMP in nucleotide biosynthesis. Loss-of-function mutations in thymidylate synthase confer resistance to p-aminosalicylic acid by disrupting the substrate-binding affinity and catalytic activity."},
        "mech_res": "Antibiotic resistant form of thymidylate synthase (synthetase), an enzyme that catalyzes the conversion of dUMP to dTMP in nucleotide biosynthesis. Loss-of-function mutations in thymidylate synthase confer resistance to p-aminosalicylic acid by disrupting the substrate-binding affinity and catalytic activity.",
        "det_res": [
            {"reference": "ARO:3004152", "snippet": "Antibiotic resistant form of thymidylate synthase (synthetase), an enzyme that catalyzes the conversion of dUMP to dTMP in nucleotide biosynthesis. Loss-of-function mutations in thymidylate synthase confer resistance to p-aminosalicylic acid by disrupting the substrate-binding affinity and catalytic activity.",
             "notes": "Reaction, and the mutation's actual defect: 'LOSS-OF-FUNCTION mutations ... by DISRUPTING THE SUBSTRATE-BINDING AFFINITY AND CATALYTIC ACTIVITY'. Round 113's folC named the intermediate for the same drug; this names the defect."},
        ],
        "res_drug": "Antibiotic resistant form of thymidylate synthase (synthetase), an enzyme that catalyzes the conversion of dUMP to dTMP in nucleotide biosynthesis. Loss-of-function mutations in thymidylate synthase confer resistance to p-aminosalicylic acid by disrupting the substrate-binding affinity and catalytic activity.",
        "note": ("Prodrug-activation loss with the defect named. Pairs with folC (round 113) "
                 "on p-aminosalicylic acid: folC gives the intermediate, thyA gives what "
                 "the mutation breaks."),
        "extra_nodes": [
            {"node_id": "ts_activity", "label": "thymidylate synthase activity (dUMP to dTMP)",
             "node_type": "MOLECULAR_FUNCTION", "description": "Ungrounded: not looked up rather than guessed."},
            {"node_id": "defect", "label": "disrupted substrate binding and catalysis",
             "node_type": "STATE",
             "description": "What the loss-of-function mutation causes, in CARD's own words."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "ts_activity",
             "predicate": "enables (dUMP to dTMP conversion)", "predicate_id": "RO:0002327",
             "evidence": [{"reference": "ARO:3004152", "snippet": "Antibiotic resistant form of thymidylate synthase (synthetase), an enzyme that catalyzes the conversion of dUMP to dTMP in nucleotide biosynthesis. Loss-of-function mutations in thymidylate synthase confer resistance to p-aminosalicylic acid by disrupting the substrate-binding affinity and catalytic activity.",
                           "notes": "'catalyzes the conversion of dUMP to dTMP in nucleotide biosynthesis'."}]},
            {"subject": "determinant", "object": "defect",
             "predicate": "has quality (disrupted binding and catalysis)",
             "predicate_id": "RO:0000086",
             "evidence": [{"reference": "ARO:3004152", "snippet": "Antibiotic resistant form of thymidylate synthase (synthetase), an enzyme that catalyzes the conversion of dUMP to dTMP in nucleotide biosynthesis. Loss-of-function mutations in thymidylate synthase confer resistance to p-aminosalicylic acid by disrupting the substrate-binding affinity and catalytic activity.",
                           "notes": "'by disrupting the substrate-binding affinity and catalytic activity'."}]},
            {"subject": "defect", "object": "ts_activity",
             "predicate": "negatively regulates (the enzyme stops working)",
             "predicate_id": "RO:0002212",
             "description": "The causal core: loss of function is the resistance, as in rounds 56 and 113.",
             "evidence": [{"reference": "ARO:3004152", "snippet": "Antibiotic resistant form of thymidylate synthase (synthetase), an enzyme that catalyzes the conversion of dUMP to dTMP in nucleotide biosynthesis. Loss-of-function mutations in thymidylate synthase confer resistance to p-aminosalicylic acid by disrupting the substrate-binding affinity and catalytic activity.",
                           "notes": "'LOSS-OF-FUNCTION mutations ... confer resistance'. NOT asserted: how thymidylate synthase activates PAS, which CARD does not say here (folC's record does, for its own step)."}]},
        ],
    },
    # atpE (ARO:3007477) -- target alteration, with the drug's action named.
    "ARO:3007477": {
        "curated": "2026-08-08T00:00:00Z",
        "precondition": _requires_mech("ARO:3000212", "mutation"),
        "reference": "ARO:3007477",
        "mech": {"ARO:3000212": "ATP synthase enzymes, specifically subunit C, resistant to diarylquinolone antibiotics including Bedaquiline. Mutations in ATP synthase confer antibiotic resistance by disrupting binding and blocking of ATP synthase reactions by Bedaquiline."},
        "mech_res": "ATP synthase enzymes, specifically subunit C, resistant to diarylquinolone antibiotics including Bedaquiline. Mutations in ATP synthase confer antibiotic resistance by disrupting binding and blocking of ATP synthase reactions by Bedaquiline.",
        "det_res": [
            {"reference": "ARO:3007477", "snippet": "ATP synthase enzymes, specifically subunit C, resistant to diarylquinolone antibiotics including Bedaquiline. Mutations in ATP synthase confer antibiotic resistance by disrupting binding and blocking of ATP synthase reactions by Bedaquiline.",
             "notes": "Both halves: what Bedaquiline does ('binding and BLOCKING of ATP synthase reactions') and what the mutation does to it ('DISRUPTING' that). SCOPE: subunit C specifically."},
        ],
        "res_drug": "ATP synthase enzymes, specifically subunit C, resistant to diarylquinolone antibiotics including Bedaquiline. Mutations in ATP synthase confer antibiotic resistance by disrupting binding and blocking of ATP synthase reactions by Bedaquiline.",
        "note": "Target alteration of ATP synthase subunit C; the drug's action is stated, unlike most target-alteration records here.",
        "extra_nodes": [
            {"node_id": "atp_synthesis", "label": "ATP synthase reactions",
             "node_type": "BIOLOGICAL_PROCESS", "description": "Ungrounded: not looked up rather than guessed."},
            {"node_id": "blocking", "label": "Bedaquiline binding and blocking of ATP synthase",
             "node_type": "STATE", "description": "What the mutation disrupts."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "atp_synthesis",
             "predicate": "part of (ATP synthase)", "predicate_id": "BFO:0000050",
             "evidence": [{"reference": "ARO:3007477", "snippet": "ATP synthase enzymes, specifically subunit C, resistant to diarylquinolone antibiotics including Bedaquiline. Mutations in ATP synthase confer antibiotic resistance by disrupting binding and blocking of ATP synthase reactions by Bedaquiline.",
                           "notes": "'ATP synthase enzymes, specifically subunit C'."}]},
            {"subject": "drug0", "object": "blocking",
             "predicate": "causally upstream of (binds and blocks ATP synthase)",
             "predicate_id": "RO:0002411",
             "evidence": [{"reference": "ARO:3007477", "snippet": "ATP synthase enzymes, specifically subunit C, resistant to diarylquinolone antibiotics including Bedaquiline. Mutations in ATP synthase confer antibiotic resistance by disrupting binding and blocking of ATP synthase reactions by Bedaquiline.",
                           "notes": "'binding and blocking of ATP synthase reactions by Bedaquiline'."}]},
            {"subject": "determinant", "object": "blocking",
             "predicate": "negatively regulates (mutations disrupt the drug's binding)",
             "predicate_id": "RO:0002212",
             "evidence": [{"reference": "ARO:3007477", "snippet": "ATP synthase enzymes, specifically subunit C, resistant to diarylquinolone antibiotics including Bedaquiline. Mutations in ATP synthase confer antibiotic resistance by disrupting binding and blocking of ATP synthase reactions by Bedaquiline.",
                           "notes": "'Mutations in ATP synthase confer antibiotic resistance by DISRUPTING binding'."}]},
        ],
    },
    # cya (ARO:3004251) -- reduced import, two regulatory steps removed. uhpA's shape
    # (round 109) at one more remove: cya makes cAMP, cAMP regulates the transporter.
    "ARO:3004251": {
        "curated": "2026-08-08T00:00:00Z",
        "precondition": _requires_mech("ARO:3000212", "mutation"),
        "reference": "ARO:3004251",
        "mech": {"ARO:3000212": "Adenylate cyclases encoded by cya genes, which are involved in the synthesis cyclic AMP which regulates the fosfomycin transporter glpT. Mutations in cya genes can confer resistance to fosfomycin."},
        "mech_res": "Adenylate cyclases encoded by cya genes, which are involved in the synthesis cyclic AMP which regulates the fosfomycin transporter glpT. Mutations in cya genes can confer resistance to fosfomycin.",
        "det_res": [
            {"reference": "ARO:3004251", "snippet": "Adenylate cyclases encoded by cya genes, which are involved in the synthesis cyclic AMP which regulates the fosfomycin transporter glpT. Mutations in cya genes can confer resistance to fosfomycin.",
             "notes": "Two steps from the drug: cya makes cAMP, cAMP regulates the fosfomycin TRANSPORTER glpT. Round 109's uhpA was one step; this is the same reduced-import shape at a further remove. NOTE the hedge: 'CAN confer'."},
        ],
        "res_drug": "Adenylate cyclases encoded by cya genes, which are involved in the synthesis cyclic AMP which regulates the fosfomycin transporter glpT. Mutations in cya genes can confer resistance to fosfomycin.",
        "note": ("Reduced import at two removes -- the determinant makes a second messenger "
                 "that regulates the importer. NOT asserted: the DIRECTION of cAMP's effect "
                 "on glpT, which CARD gives as 'regulates' without saying which way."),
        "extra_nodes": [
            {"node_id": "camp", "label": "cyclic AMP", "node_type": "CHEMICAL",
             "description": "The second messenger. Ungrounded: no CHEBI id verified this round."},
            {"node_id": "glpt", "label": "the fosfomycin transporter glpT",
             "node_type": "PROTEIN", "description": "The importer. Ungrounded."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "camp",
             "predicate": "participates in (cyclic AMP synthesis)", "predicate_id": "RO:0000056",
             "description": "'Participates in', matching CARD's 'are INVOLVED IN the synthesis'.",
             "evidence": [{"reference": "ARO:3004251", "snippet": "Adenylate cyclases encoded by cya genes, which are involved in the synthesis cyclic AMP which regulates the fosfomycin transporter glpT. Mutations in cya genes can confer resistance to fosfomycin.",
                           "notes": "'Adenylate cyclases ... involved in the synthesis cyclic AMP'."}]},
            {"subject": "camp", "object": "glpt",
             "predicate": "regulates (the fosfomycin transporter)", "predicate_id": "RO:0002211",
             "description": "Neutral RO:0002211: CARD says 'regulates' without a direction, as in rounds 78 and 110.",
             "evidence": [{"reference": "ARO:3004251", "snippet": "Adenylate cyclases encoded by cya genes, which are involved in the synthesis cyclic AMP which regulates the fosfomycin transporter glpT. Mutations in cya genes can confer resistance to fosfomycin.",
                           "notes": "'cyclic AMP which regulates the fosfomycin transporter glpT'. NOT asserted: which way, nor that reduced glpT is what confers resistance -- CARD states the resistance separately."}]},
        ],
    },
    # folC / dihydrofolate synthase (ARO:3004155) -- the fullest prodrug-activation-loss
    # statement in this corpus, and it names the INTERMEDIATE.
    #
    # Rounds 56 (pncA), 57 (ndh), 95 (mshA), 108 (FUR1) all curated this mechanism from
    # sentences that stopped earlier. This one runs the whole way: the enzyme is required
    # for bioactivation, the mutation stops production of a NAMED analog, and that prevents
    # activation "thus conferring resistance". Every link is CARD's.
    "ARO:3004155": {
        "curated": "2026-08-08T00:00:00Z",
        "precondition": _requires_mech("ARO:3000212", "mutation"),
        "reference": "ARO:3004155",
        "mech": {"ARO:3000212": "Dihydrofolate synthase (synthetase) enzymes resistant to aminosalicylates (inc. para-aminosalicylic acid) caused by mutation. Dihydrofolate synthase is required for bioactivation of p-aminosalicylic acid, and mutation in dihydrofolate synthase inhibits production of the dihydrofolate analog hydroxyl-dihydrofolate, thus preventing activation and conferring resistance."},
        "mech_res": "Dihydrofolate synthase (synthetase) enzymes resistant to aminosalicylates (inc. para-aminosalicylic acid) caused by mutation. Dihydrofolate synthase is required for bioactivation of p-aminosalicylic acid, and mutation in dihydrofolate synthase inhibits production of the dihydrofolate analog hydroxyl-dihydrofolate, thus preventing activation and conferring resistance.",
        "det_res": [
            {"reference": "ARO:3004155", "snippet": "Dihydrofolate synthase (synthetase) enzymes resistant to aminosalicylates (inc. para-aminosalicylic acid) caused by mutation. Dihydrofolate synthase is required for bioactivation of p-aminosalicylic acid, and mutation in dihydrofolate synthase inhibits production of the dihydrofolate analog hydroxyl-dihydrofolate, thus preventing activation and conferring resistance.",
             "notes": "The complete chain, and the only one in this corpus to name the intermediate: 'required for BIOACTIVATION', mutation 'inhibits production of the dihydrofolate analog HYDROXYL-DIHYDROFOLATE', 'THUS preventing activation and conferring resistance'."},
        ],
        "res_drug": "Dihydrofolate synthase (synthetase) enzymes resistant to aminosalicylates (inc. para-aminosalicylic acid) caused by mutation. Dihydrofolate synthase is required for bioactivation of p-aminosalicylic acid, and mutation in dihydrofolate synthase inhibits production of the dihydrofolate analog hydroxyl-dihydrofolate, thus preventing activation and conferring resistance.",
        "note": ("Prodrug-activation loss, stated end to end. Rounds 56, 57, 95 and 108 "
                 "curated this mechanism from sentences that stopped earlier; this one "
                 "names the analog whose absence is the resistance."),
        "extra_nodes": [
            {"node_id": "dhfs", "label": "dihydrofolate synthase activity",
             "node_type": "MOLECULAR_FUNCTION",
             "description": "Ungrounded: not looked up rather than guessed (rounds 56-111)."},
            {"node_id": "analog", "label": "hydroxyl-dihydrofolate, the activated drug analog",
             "node_type": "CHEMICAL",
             "description": "The intermediate CARD names -- rare here. Ungrounded: no CHEBI id verified this round."},
            {"node_id": "activation", "label": "bioactivation of p-aminosalicylic acid",
             "node_type": "STATE", "description": "What the mutation prevents. Ungrounded."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "dhfs",
             "predicate": "enables (dihydrofolate synthase activity)", "predicate_id": "RO:0002327",
             "evidence": [{"reference": "ARO:3004155", "snippet": "Dihydrofolate synthase (synthetase) enzymes resistant to aminosalicylates (inc. para-aminosalicylic acid) caused by mutation. Dihydrofolate synthase is required for bioactivation of p-aminosalicylic acid, and mutation in dihydrofolate synthase inhibits production of the dihydrofolate analog hydroxyl-dihydrofolate, thus preventing activation and conferring resistance.",
                           "notes": "The enzyme the record is named for."}]},
            {"subject": "dhfs", "object": "analog",
             "predicate": "has output (hydroxyl-dihydrofolate)", "predicate_id": "RO:0002234",
             "description": "The step the mutation breaks, with the product named -- which is what makes this the fullest statement of the mechanism in the corpus.",
             "evidence": [{"reference": "ARO:3004155", "snippet": "Dihydrofolate synthase (synthetase) enzymes resistant to aminosalicylates (inc. para-aminosalicylic acid) caused by mutation. Dihydrofolate synthase is required for bioactivation of p-aminosalicylic acid, and mutation in dihydrofolate synthase inhibits production of the dihydrofolate analog hydroxyl-dihydrofolate, thus preventing activation and conferring resistance.",
                           "notes": "'mutation ... inhibits production of the dihydrofolate analog hydroxyl-dihydrofolate'."}]},
            {"subject": "analog", "object": "activation",
             "predicate": "causally upstream of (the drug is activated)",
             "predicate_id": "RO:0002411",
             "evidence": [{"reference": "ARO:3004155", "snippet": "Dihydrofolate synthase (synthetase) enzymes resistant to aminosalicylates (inc. para-aminosalicylic acid) caused by mutation. Dihydrofolate synthase is required for bioactivation of p-aminosalicylic acid, and mutation in dihydrofolate synthase inhibits production of the dihydrofolate analog hydroxyl-dihydrofolate, thus preventing activation and conferring resistance.",
                           "notes": "'Dihydrofolate synthase is required for bioactivation of p-aminosalicylic acid'."}]},
            {"subject": "determinant", "object": "activation",
             "predicate": "negatively regulates (prevents activation)", "predicate_id": "RO:0002212",
             "description": "The causal core, with CARD's own 'thus'.",
             "evidence": [{"reference": "ARO:3004155", "snippet": "Dihydrofolate synthase (synthetase) enzymes resistant to aminosalicylates (inc. para-aminosalicylic acid) caused by mutation. Dihydrofolate synthase is required for bioactivation of p-aminosalicylic acid, and mutation in dihydrofolate synthase inhibits production of the dihydrofolate analog hydroxyl-dihydrofolate, thus preventing activation and conferring resistance.",
                           "notes": "'thus preventing activation and conferring resistance'."}]},
        ],
    },
    # Upc2 (ARO:3007551) -- target OVEREXPRESSION via a regulator, complete in one sentence.
    #
    # Round 84's murA was overexpression of the target itself; this is a REGULATOR whose
    # mutation raises the target's expression. CARD gives the whole chain and names the
    # gene: "by upregulating ERG11 expression". ERG11 is the azole target.
    "ARO:3007551": {
        "curated": "2026-08-08T00:00:00Z",
        # ARO:3007609 (target overexpression), NOT ARO:3000212. I assumed the mutation id
        # because the label says "with mutations", and the record carries the mechanism id
        # for what the mutations DO. Second time this session I guessed a mechanism id
        # rather than reading it (round 87 was the first), and both times the promoter
        # wrote zero records until I looked.
        "precondition": _requires_mech("ARO:3007609", "target overexpression"),
        "reference": "ARO:3007551",
        "mech": {"ARO:3007609": "Upc2 is a sterol synthesis regulatory element binding protein in Candida spp. Mutations in Upc2 have been shown to confer resistance to azole antibiotics including fluconazole by upregulating ERG11 expression."},
        "mech_res": "Upc2 is a sterol synthesis regulatory element binding protein in Candida spp. Mutations in Upc2 have been shown to confer resistance to azole antibiotics including fluconazole by upregulating ERG11 expression.",
        "det_res": [
            {"reference": "ARO:3007551", "snippet": "Upc2 is a sterol synthesis regulatory element binding protein in Candida spp. Mutations in Upc2 have been shown to confer resistance to azole antibiotics including fluconazole by upregulating ERG11 expression.",
             "notes": "The complete chain with CARD's own 'BY': mutations confer azole resistance BY UPREGULATING ERG11 expression. The mechanism is named, the target gene is named, and the resistance is attributed ('have been SHOWN to')."},
        ],
        "res_drug": "Upc2 is a sterol synthesis regulatory element binding protein in Candida spp. Mutations in Upc2 have been shown to confer resistance to azole antibiotics including fluconazole by upregulating ERG11 expression.",
        "note": ("Target overexpression via a regulator. Round 84's murA overexpressed the "
                 "target itself; here a regulator's mutation raises the target's "
                 "expression. NOT asserted: that ERG11 is the azole target or what it does "
                 "-- CARD names the gene and not its role."),
        "extra_nodes": [
            {"node_id": "erg11_expression", "label": "ERG11 expression",
             "node_type": "BIOLOGICAL_PROCESS",
             "description": "What the mutation raises. Ungrounded, and deliberately unelaborated: CARD names the gene without saying what it does."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "erg11_expression",
             "predicate": "positively regulates (upregulates ERG11 expression)",
             "predicate_id": "RO:0002213",
             "description": "The POSITIVE form, licensed by CARD's own 'by UPREGULATING'.",
             "evidence": [{"reference": "ARO:3007551", "snippet": "Upc2 is a sterol synthesis regulatory element binding protein in Candida spp. Mutations in Upc2 have been shown to confer resistance to azole antibiotics including fluconazole by upregulating ERG11 expression.",
                           "notes": "'by upregulating ERG11 expression'. NOT asserted: that ERG11 encodes the azole target, which CARD does not say here."}]},
        ],
    },
    # FUR1 in Saccharomyces (ARO:3007559) -- round 108's Candida FUR1, same sentence.
    "ARO:3007559": {
        "curated": "2026-08-08T00:00:00Z",
        "precondition": _requires_mech("ARO:3000212", "mutation"),
        "reference": "ARO:3007559",
        "mech": {"ARO:3000212": "FUR1 is a fungal uracil phosphoribosyltransferase in Saccharomyces spp. It encodes the UPRT protein, also known as uracil pyrophosphorylase, which is a key regulating enzyme in pyrimidine salvage. Mutations in FUR1 have been shown to confer resistance to 5-flucytosine."},
        "mech_res": "FUR1 is a fungal uracil phosphoribosyltransferase in Saccharomyces spp. It encodes the UPRT protein, also known as uracil pyrophosphorylase, which is a key regulating enzyme in pyrimidine salvage. Mutations in FUR1 have been shown to confer resistance to 5-flucytosine.",
        "det_res": [
            {"reference": "ARO:3007559", "snippet": "FUR1 is a fungal uracil phosphoribosyltransferase in Saccharomyces spp. It encodes the UPRT protein, also known as uracil pyrophosphorylase, which is a key regulating enzyme in pyrimidine salvage. Mutations in FUR1 have been shown to confer resistance to 5-flucytosine.",
             "notes": "Word for word the Candida FUR1 sentence (round 108) with the genus changed. Curated identically -- the 5-FC activation story is standard and CARD tells it for neither species."},
        ],
        "res_drug": "FUR1 is a fungal uracil phosphoribosyltransferase in Saccharomyces spp. It encodes the UPRT protein, also known as uracil pyrophosphorylase, which is a key regulating enzyme in pyrimidine salvage. Mutations in FUR1 have been shown to confer resistance to 5-flucytosine.",
        "note": ("The Saccharomyces FUR1 record, identical in wording to the Candida one "
                 "(round 108) and curated identically. NOT asserted: that 5-FC is activated "
                 "by pyrimidine salvage."),
        "extra_nodes": [
            {"node_id": "uprt", "label": "uracil phosphoribosyltransferase activity",
             "node_type": "MOLECULAR_FUNCTION", "description": "Ungrounded."},
            {"node_id": "salvage", "label": "pyrimidine salvage",
             "node_type": "BIOLOGICAL_PROCESS", "description": "Ungrounded."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "uprt",
             "predicate": "enables (uracil phosphoribosyltransferase activity)",
             "predicate_id": "RO:0002327",
             "evidence": [{"reference": "ARO:3007559", "snippet": "It encodes the UPRT protein, also known as uracil pyrophosphorylase, which is a key regulating enzyme in pyrimidine salvage.",
                           "notes": "Same sentence as the Candida record."}]},
            {"subject": "uprt", "object": "salvage",
             "predicate": "part of (pyrimidine salvage)", "predicate_id": "BFO:0000050",
             "evidence": [{"reference": "ARO:3007559", "snippet": "It encodes the UPRT protein, also known as uracil pyrophosphorylase, which is a key regulating enzyme in pyrimidine salvage.",
                           "notes": "'a key regulating enzyme in pyrimidine salvage'. NOT asserted: the 5-FC activation step."}]},
        ],
    },
    # nudC (ARO:3004892) -- a named function, and "inability to FUNCTION" not "to ACTIVATE".
    "ARO:3004892": {
        "curated": "2026-08-08T00:00:00Z",
        "precondition": _requires_mech("ARO:3000212", "mutation"),
        "reference": "ARO:3004892",
        "mech": {"ARO:3000212": "nudC is a NADH pyrophosphatase that is involved in nicotinate and nicotinamide metabolism. Mutations that occur on the nudC gene resulting in the inability for ethionamide to function."},
        "mech_res": "nudC is a NADH pyrophosphatase that is involved in nicotinate and nicotinamide metabolism. Mutations that occur on the nudC gene resulting in the inability for ethionamide to function.",
        "det_res": [
            {"reference": "ARO:3004892", "snippet": "nudC is a NADH pyrophosphatase that is involved in nicotinate and nicotinamide metabolism. Mutations that occur on the nudC gene resulting in the inability for ethionamide to function.",
             "notes": "Names an enzyme and a pathway -- unlike the bare nudC family term left in round 84 -- but says 'inability for ethionamide to FUNCTION', not 'to ACTIVATE'. Round 95 drew that line between mshA and mshC and it holds here: no activation claim, so no prodrug edge."},
        ],
        "res_drug": "nudC is a NADH pyrophosphatase that is involved in nicotinate and nicotinamide metabolism. Mutations that occur on the nudC gene resulting in the inability for ethionamide to function.",
        "note": ("Enzyme and pathway only. The word is 'FUNCTION', not 'activate' -- round "
                 "95's mshA/mshC distinction -- so no prodrug-activation edge is written, "
                 "even though ethionamide is a prodrug and ndh (round 57) curates that "
                 "story for a neighbouring enzyme."),
        "extra_nodes": [
            {"node_id": "nadh_pp", "label": "NADH pyrophosphatase activity",
             "node_type": "MOLECULAR_FUNCTION", "description": "Ungrounded."},
            {"node_id": "nad_metabolism", "label": "nicotinate and nicotinamide metabolism",
             "node_type": "BIOLOGICAL_PROCESS", "description": "Ungrounded."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "nadh_pp",
             "predicate": "enables (NADH pyrophosphatase activity)", "predicate_id": "RO:0002327",
             "evidence": [{"reference": "ARO:3004892", "snippet": "nudC is a NADH pyrophosphatase that is involved in nicotinate and nicotinamide metabolism. Mutations that occur on the nudC gene resulting in the inability for ethionamide to function.",
                           "notes": "'nudC is a NADH pyrophosphatase'."}]},
            {"subject": "nadh_pp", "object": "nad_metabolism",
             "predicate": "part of (nicotinate and nicotinamide metabolism)",
             "predicate_id": "BFO:0000050",
             "evidence": [{"reference": "ARO:3004892", "snippet": "nudC is a NADH pyrophosphatase that is involved in nicotinate and nicotinamide metabolism. Mutations that occur on the nudC gene resulting in the inability for ethionamide to function.",
                           "notes": "'involved in nicotinate and nicotinamide metabolism'. NOT asserted: how that relates to ethionamide, which CARD does not say."}]},
        ],
    },
    # uhpA (ARO:3003893) -- a 16th mechanism kind: resistance by losing an IMPORTER's
    # activator. The whole chain is in one sentence, and the causal words are CARD's.
    #
    # Distinct from every efflux config (rounds 67-79, 93): nothing is pumped out. And
    # distinct from round 71's resistance-by-absence: what is lost is not the determinant's
    # own function but its REGULATORY effect on a transporter that lets the drug IN.
    "ARO:3003893": {
        "curated": "2026-08-08T00:00:00Z",
        "precondition": _requires_mech("ARO:3000212", "mutation"),
        "reference": "ARO:3003893",
        "mech": {"ARO:3000212": "uhpA is a positive activator of the fosfomycin importer uhpT, thus mutations to uhpA confer fosfomycin resistance by reducing uhpT expression."},
        "mech_res": "uhpA is a positive activator of the fosfomycin importer uhpT, thus mutations to uhpA confer fosfomycin resistance by reducing uhpT expression.",
        "det_res": [
            {"reference": "ARO:3003893", "snippet": "uhpA is a positive activator of the fosfomycin importer uhpT, thus mutations to uhpA confer fosfomycin resistance by reducing uhpT expression.",
             "notes": "The complete chain with CARD's own causal words: uhpA is a POSITIVE ACTIVATOR of the fosfomycin IMPORTER, THUS mutations confer resistance BY REDUCING uhpT expression. Rare in this corpus -- most definitions give a role and a resistance claim with nothing between."},
        ],
        "res_drug": "uhpA is a positive activator of the fosfomycin importer uhpT, thus mutations to uhpA confer fosfomycin resistance by reducing uhpT expression.",
        "note": ("Resistance by losing an importer's activator -- the drug is not pumped "
                 "out, it is not let in. Distinct from every efflux config and from round "
                 "71's resistance-by-absence: what is lost is a REGULATORY effect on a "
                 "transporter, not the determinant's own catalytic function."),
        "extra_nodes": [
            {"node_id": "uhpt_expression", "label": "expression of the fosfomycin importer uhpT",
             "node_type": "BIOLOGICAL_PROCESS",
             "description": "What uhpA activates and the mutation reduces. Ungrounded."},
            {"node_id": "import", "label": "uptake of fosfomycin into the cell",
             "node_type": "BIOLOGICAL_PROCESS",
             "description": "The step that fails. Ungrounded."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "uhpt_expression",
             "predicate": "positively regulates (activates uhpT expression)",
             "predicate_id": "RO:0002213",
             "description": "The POSITIVE form, licensed by CARD's own 'positive activator' -- and it is the loss of this activation that resists.",
             "evidence": [{"reference": "ARO:3003893", "snippet": "uhpA is a positive activator of the fosfomycin importer uhpT, thus mutations to uhpA confer fosfomycin resistance by reducing uhpT expression.",
                           "notes": "'uhpA is a positive activator of the fosfomycin importer uhpT'."}]},
            {"subject": "uhpt_expression", "object": "import",
             "predicate": "causally upstream of (fosfomycin uptake)", "predicate_id": "RO:0002411",
             "description": "Why less transporter is resistance: uhpT is how the drug enters.",
             "evidence": [{"reference": "ARO:3003893", "snippet": "uhpA is a positive activator of the fosfomycin importer uhpT, thus mutations to uhpA confer fosfomycin resistance by reducing uhpT expression.",
                           "notes": "'the fosfomycin IMPORTER uhpT' -- CARD names the transporter's direction."}]},
            {"subject": "determinant", "object": "import",
             "predicate": "negatively regulates (mutations reduce drug uptake)",
             "predicate_id": "RO:0002212",
             "description": "The causal core, in CARD's own words -- 'thus ... by reducing uhpT expression'.",
             "evidence": [{"reference": "ARO:3003893", "snippet": "uhpA is a positive activator of the fosfomycin importer uhpT, thus mutations to uhpA confer fosfomycin resistance by reducing uhpT expression.",
                           "notes": "'thus mutations to uhpA confer fosfomycin resistance BY REDUCING uhpT expression'."}]},
        ],
    },
    # mshB (ARO:3004903) -- a named reaction and no resistance claim at all.
    "ARO:3004903": {
        "curated": "2026-08-08T00:00:00Z",
        "precondition": _requires_mech("ARO:3000212", "mutation"),
        "reference": "ARO:3004903",
        "mech": {"ARO:3000212": "mshB is a deacetylase that is involved in the second step of mycothiol synthesis. GlcNAc-Ins is deacetylated by MshB to produce GlcN-Ins."},
        "mech_res": "mshB is a deacetylase that is involved in the second step of mycothiol synthesis. GlcNAc-Ins is deacetylated by MshB to produce GlcN-Ins.",
        "det_res": [
            {"reference": "ARO:3004903", "snippet": "mshB is a deacetylase that is involved in the second step of mycothiol synthesis. GlcNAc-Ins is deacetylated by MshB to produce GlcN-Ins.",
             "notes": "A named reaction with named substrate and product -- more chemistry than most records here -- and NO resistance claim whatsoever. CARD does not say mutations do anything."},
        ],
        "res_drug": "mshB is a deacetylase that is involved in the second step of mycothiol synthesis. GlcNAc-Ins is deacetylated by MshB to produce GlcN-Ins.",
        "note": ("Reaction only. CARD gives substrate, product and pathway step, and never "
                 "mentions a drug, a mutation or resistance -- less than round 95's aftA, "
                 "which at least called its product essential. The neighbouring mshA record "
                 "(round 95) says 'inability for antibiotic to ACTIVATE'; this one says "
                 "nothing of the kind."),
        "extra_nodes": [
            {"node_id": "deacetylation", "label": "GlcNAc-Ins deacetylase activity",
             "node_type": "MOLECULAR_FUNCTION",
             "description": "Ungrounded: not looked up rather than guessed."},
            {"node_id": "mycothiol", "label": "mycothiol synthesis",
             "node_type": "BIOLOGICAL_PROCESS",
             "description": "The pathway. Ungrounded."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "deacetylation",
             "predicate": "enables (deacetylation of GlcNAc-Ins)", "predicate_id": "RO:0002327",
             "evidence": [{"reference": "ARO:3004903", "snippet": "mshB is a deacetylase that is involved in the second step of mycothiol synthesis. GlcNAc-Ins is deacetylated by MshB to produce GlcN-Ins.",
                           "notes": "'GlcNAc-Ins is deacetylated by MshB to produce GlcN-Ins' -- substrate and product both named."}]},
            {"subject": "deacetylation", "object": "mycothiol",
             "predicate": "part of (the second step of mycothiol synthesis)",
             "predicate_id": "BFO:0000050",
             "evidence": [{"reference": "ARO:3004903", "snippet": "mshB is a deacetylase that is involved in the second step of mycothiol synthesis. GlcNAc-Ins is deacetylated by MshB to produce GlcN-Ins.",
                           "notes": "'involved in the second step of mycothiol synthesis'. NOT asserted: any link to a drug or to resistance, which this definition never mentions."}]},
        ],
    },
    # FUR1 (ARO:3007557) -- prodrug-activation loss, in a fungal pathway.
    #
    # 5-flucytosine is a prodrug converted by the pyrimidine salvage pathway, and UPRT is
    # the enzyme CARD names as "a key regulating enzyme" in it. Losing it is round 56's
    # pncA shape in a eukaryote. NOT asserted: the conversion step itself, which CARD does
    # not describe -- it names the pathway and the resistance and stops.
    "ARO:3007557": {
        "curated": "2026-08-08T00:00:00Z",
        "precondition": _requires_mech("ARO:3000212", "mutation"),
        "reference": "ARO:3007557",
        "mech": {"ARO:3000212": "FUR1 is a fungal uracil phosphoribosyltransferase in Candida spp. It encodes the UPRT protein, also known as uracil pyrophosphorylase, which is a key regulating enzyme in pyrimidine salvage. Mutations in FUR1 have been shown to confer resistance to 5-flucytosine."},
        "mech_res": "FUR1 is a fungal uracil phosphoribosyltransferase in Candida spp. It encodes the UPRT protein, also known as uracil pyrophosphorylase, which is a key regulating enzyme in pyrimidine salvage. Mutations in FUR1 have been shown to confer resistance to 5-flucytosine.",
        "det_res": [
            {"reference": "ARO:3007557", "snippet": "FUR1 is a fungal uracil phosphoribosyltransferase in Candida spp. It encodes the UPRT protein, also known as uracil pyrophosphorylase, which is a key regulating enzyme in pyrimidine salvage. Mutations in FUR1 have been shown to confer resistance to 5-flucytosine.",
             "notes": "Enzyme, its synonym, its pathway role, and the resistance -- with 'have been SHOWN to confer', an attribution rather than a bare claim. NOT stated: how a pyrimidine-salvage enzyme's loss resists 5-flucytosine."},
        ],
        "res_drug": "FUR1 is a fungal uracil phosphoribosyltransferase in Candida spp. It encodes the UPRT protein, also known as uracil pyrophosphorylase, which is a key regulating enzyme in pyrimidine salvage. Mutations in FUR1 have been shown to confer resistance to 5-flucytosine.",
        "note": ("Pyrimidine-salvage enzyme whose mutation confers 5-flucytosine "
                 "resistance. 5-FC is a prodrug and the activation-loss story is standard, "
                 "and CARD does not tell it -- so the graph carries the enzyme's pathway "
                 "role and the resistance, with nothing between."),
        "extra_nodes": [
            {"node_id": "uprt", "label": "uracil phosphoribosyltransferase activity",
             "node_type": "MOLECULAR_FUNCTION",
             "description": "Ungrounded: not looked up rather than guessed (rounds 56-106)."},
            {"node_id": "salvage", "label": "pyrimidine salvage",
             "node_type": "BIOLOGICAL_PROCESS",
             "description": "The pathway CARD names. Ungrounded."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "uprt",
             "predicate": "enables (uracil phosphoribosyltransferase activity)",
             "predicate_id": "RO:0002327",
             "evidence": [{"reference": "ARO:3007557", "snippet": "FUR1 is a fungal uracil phosphoribosyltransferase in Candida spp. It encodes the UPRT protein, also known as uracil pyrophosphorylase, which is a key regulating enzyme in pyrimidine salvage. Mutations in FUR1 have been shown to confer resistance to 5-flucytosine.",
                           "notes": "'It encodes the UPRT protein, also known as uracil pyrophosphorylase'."}]},
            {"subject": "uprt", "object": "salvage",
             "predicate": "part of (pyrimidine salvage)", "predicate_id": "BFO:0000050",
             "description": "Where the graph stops. CARD calls UPRT 'a key regulating enzyme' in this pathway and never connects the pathway to 5-flucytosine.",
             "evidence": [{"reference": "ARO:3007557", "snippet": "FUR1 is a fungal uracil phosphoribosyltransferase in Candida spp. It encodes the UPRT protein, also known as uracil pyrophosphorylase, which is a key regulating enzyme in pyrimidine salvage. Mutations in FUR1 have been shown to confer resistance to 5-flucytosine.",
                           "notes": "'a key regulating enzyme in pyrimidine salvage'. NOT asserted: that 5-FC is activated by this pathway, which is standard and uncited here."}]},
        ],
    },
    # Hmg1 (ARO:3007670) -- one sentence, an enzyme name and a resistance claim.
    "ARO:3007670": {
        "curated": "2026-08-08T00:00:00Z",
        "precondition": _requires_mech("ARO:3000212", "mutation"),
        "reference": "ARO:3007670",
        "mech": {"ARO:3000212": "Hmg1 is an HMG-CoA reductase-encoding gene with mutations in the gene causing triazole resistance."},
        "mech_res": "Hmg1 is an HMG-CoA reductase-encoding gene with mutations in the gene causing triazole resistance.",
        "det_res": [
            {"reference": "ARO:3007670", "snippet": "Hmg1 is an HMG-CoA reductase-encoding gene with mutations in the gene causing triazole resistance.",
             "notes": "One sentence: an enzyme name and a causal claim ('CAUSING triazole resistance', unhedged). Round 66's EF-Tu shape, with the causal verb stronger than most."},
        ],
        "res_drug": "Hmg1 is an HMG-CoA reductase-encoding gene with mutations in the gene causing triazole resistance.",
        "note": ("An HMG-CoA reductase whose mutations cause triazole resistance. HMG-CoA "
                 "reductase is upstream of ergosterol, which is what azoles target -- and "
                 "CARD says none of that, so no pathway edge is written."),
        "extra_nodes": [
            {"node_id": "hmgcoa", "label": "HMG-CoA reductase activity",
             "node_type": "MOLECULAR_FUNCTION",
             "description": "The one functional fact the sentence gives. Ungrounded."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "hmgcoa",
             "predicate": "enables (HMG-CoA reductase activity)", "predicate_id": "RO:0002327",
             "description": "What the determinant IS. NOT asserted: that this enzyme is upstream of ergosterol or that azoles target that pathway -- both true, neither in CARD's sentence.",
             "evidence": [{"reference": "ARO:3007670", "snippet": "Hmg1 is an HMG-CoA reductase-encoding gene with mutations in the gene causing triazole resistance.",
                           "notes": "'Hmg1 is an HMG-CoA reductase-encoding gene'."}]},
        ],
    },
    # fabI (ARO:3004270) -- target alteration, complete, and the pathway round 51 could not
    # source for fabG1. CARD gives enzyme, drug action, mutation and resistance in three
    # sentences, which fabG1's definitions never did.
    "ARO:3004270": {
        "curated": "2026-08-08T00:00:00Z",
        "precondition": _requires_mech("ARO:3000212", "mutation"),
        "reference": "ARO:3004270",
        "mech": {"ARO:3000212": "fabI is a enoyl-acyl carrier reductase used in lipid metabolism and fatty acid biosynthesis. The bacterial biocide Triclosan blocks the final reduction step in fatty acid elongation, inhibiting biosynthesis. Point mutations in fabI can confer resistance to Triclosan and Isoniazid."},
        "mech_res": "fabI is a enoyl-acyl carrier reductase used in lipid metabolism and fatty acid biosynthesis. The bacterial biocide Triclosan blocks the final reduction step in fatty acid elongation, inhibiting biosynthesis. Point mutations in fabI can confer resistance to Triclosan and Isoniazid.",
        "det_res": [
            {"reference": "ARO:3004270", "snippet": "fabI is a enoyl-acyl carrier reductase used in lipid metabolism and fatty acid biosynthesis. The bacterial biocide Triclosan blocks the final reduction step in fatty acid elongation, inhibiting biosynthesis. Point mutations in fabI can confer resistance to Triclosan and Isoniazid.",
             "notes": "Enzyme, drug action and resistance. NOTE the hedge -- mutations 'CAN confer' -- and that TWO drugs are named, Triclosan and isoniazid, of which only Triclosan's action is described."},
        ],
        "res_drug": "fabI is a enoyl-acyl carrier reductase used in lipid metabolism and fatty acid biosynthesis. The bacterial biocide Triclosan blocks the final reduction step in fatty acid elongation, inhibiting biosynthesis. Point mutations in fabI can confer resistance to Triclosan and Isoniazid.",
        "note": ("Target alteration in FAS-II. Same pathway as round 51's fabG1, where CARD "
                 "gave no drug action and three rounds were spent failing to source one. "
                 "Here it is stated. NOT asserted: isoniazid's action, which CARD names as "
                 "a resisted drug without describing what it does."),
        "extra_nodes": [
            {"node_id": "enoyl_reduction", "label": "enoyl-acyl carrier reductase activity",
             "node_type": "MOLECULAR_FUNCTION",
             "description": "Ungrounded: not looked up rather than guessed (rounds 56-105)."},
            {"node_id": "fa_elongation", "label": "final reduction step of fatty acid elongation",
             "node_type": "BIOLOGICAL_PROCESS",
             "description": "The step CARD says Triclosan blocks. Ungrounded."},
            {"node_id": "inhibition", "label": "Triclosan inhibition of fatty acid biosynthesis",
             "node_type": "STATE", "description": "What the mutation relieves. Ungrounded."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "enoyl_reduction",
             "predicate": "enables (enoyl-ACP reduction)", "predicate_id": "RO:0002327",
             "evidence": [{"reference": "ARO:3004270", "snippet": "fabI is a enoyl-acyl carrier reductase used in lipid metabolism and fatty acid biosynthesis. The bacterial biocide Triclosan blocks the final reduction step in fatty acid elongation, inhibiting biosynthesis. Point mutations in fabI can confer resistance to Triclosan and Isoniazid.",
                           "notes": "'fabI is a enoyl-acyl carrier reductase'."}]},
            {"subject": "enoyl_reduction", "object": "fa_elongation",
             "predicate": "part of (the final reduction step)", "predicate_id": "BFO:0000050",
             "evidence": [{"reference": "ARO:3004270", "snippet": "fabI is a enoyl-acyl carrier reductase used in lipid metabolism and fatty acid biosynthesis. The bacterial biocide Triclosan blocks the final reduction step in fatty acid elongation, inhibiting biosynthesis. Point mutations in fabI can confer resistance to Triclosan and Isoniazid.",
                           "notes": "'the final reduction step in fatty acid elongation'."}]},
            {"subject": "drug0", "object": "inhibition",
             "predicate": "causally upstream of (blocks the reduction step)",
             "predicate_id": "RO:0002411",
             "description": "Stated for TRICLOSAN specifically. Isoniazid is named as resisted without its action described -- and round 51 spent three rounds failing to source that action for fabG1.",
             "evidence": [{"reference": "ARO:3004270", "snippet": "fabI is a enoyl-acyl carrier reductase used in lipid metabolism and fatty acid biosynthesis. The bacterial biocide Triclosan blocks the final reduction step in fatty acid elongation, inhibiting biosynthesis. Point mutations in fabI can confer resistance to Triclosan and Isoniazid.",
                           "notes": "'The bacterial biocide Triclosan blocks the final reduction step in fatty acid elongation, inhibiting biosynthesis'."}]},
            {"subject": "determinant", "object": "inhibition",
             "predicate": "negatively regulates (the mutant is no longer inhibited)",
             "predicate_id": "RO:0002212",
             "evidence": [{"reference": "ARO:3004270", "snippet": "fabI is a enoyl-acyl carrier reductase used in lipid metabolism and fatty acid biosynthesis. The bacterial biocide Triclosan blocks the final reduction step in fatty acid elongation, inhibiting biosynthesis. Point mutations in fabI can confer resistance to Triclosan and Isoniazid.",
                           "notes": "'Point mutations in fabI CAN confer resistance to Triclosan and Isoniazid' -- the hedge is CARD's."}]},
        ],
    },
    # nfsB (ARO:3003755) -- prodrug-activation loss, with a CONDITIONAL phenotype.
    "ARO:3003755": {
        "curated": "2026-08-08T00:00:00Z",
        "precondition": _requires_mech("ARO:3000212", "mutation"),
        "reference": "ARO:3003755",
        "mech": {"ARO:3000212": "The nsfB gene encodes a minor oxygen-insensitive nitroreductase. NfsB reduces a broad range of nitroaromatic compounds including the antibiotics nitrofurazone and nitrofurantoin. NfsB is a flavin mononucleotide (FMN)-containing protein and uses both NADH and NADPH as a source of reducing equivalents. Mutations in nfsB lead to increased resistance to nitrofurazone and furazolidone in an nfsA mutant background."},
        "mech_res": "The nsfB gene encodes a minor oxygen-insensitive nitroreductase. NfsB reduces a broad range of nitroaromatic compounds including the antibiotics nitrofurazone and nitrofurantoin. NfsB is a flavin mononucleotide (FMN)-containing protein and uses both NADH and NADPH as a source of reducing equivalents. Mutations in nfsB lead to increased resistance to nitrofurazone and furazolidone in an nfsA mutant background.",
        "det_res": [
            {"reference": "ARO:3003755", "snippet": "The nsfB gene encodes a minor oxygen-insensitive nitroreductase. NfsB reduces a broad range of nitroaromatic compounds including the antibiotics nitrofurazone and nitrofurantoin. NfsB is a flavin mononucleotide (FMN)-containing protein and uses both NADH and NADPH as a source of reducing equivalents. Mutations in nfsB lead to increased resistance to nitrofurazone and furazolidone in an nfsA mutant background.",
             "notes": "The enzyme reduces the nitroaromatic antibiotics themselves, so losing it is prodrug-activation loss (rounds 56, 57, 95). NOTE the condition: resistance rises 'IN AN nfsA MUTANT BACKGROUND' -- a genetic precondition CARD states and this graph does not drop."},
        ],
        "res_drug": "The nsfB gene encodes a minor oxygen-insensitive nitroreductase. NfsB reduces a broad range of nitroaromatic compounds including the antibiotics nitrofurazone and nitrofurantoin. NfsB is a flavin mononucleotide (FMN)-containing protein and uses both NADH and NADPH as a source of reducing equivalents. Mutations in nfsB lead to increased resistance to nitrofurazone and furazolidone in an nfsA mutant background.",
        "note": ("Prodrug-activation loss, CONDITIONAL on an nfsA mutant background. That "
                 "condition is stated by CARD and kept -- it is the difference between "
                 "'mutations confer resistance' and 'mutations confer resistance when "
                 "another gene is already broken'."),
        "extra_nodes": [
            {"node_id": "nitroreduction", "label": "oxygen-insensitive nitroreductase activity",
             "node_type": "MOLECULAR_FUNCTION",
             "description": "Ungrounded: not looked up rather than guessed."},
            {"node_id": "nfsa_background", "label": "nfsA mutant background",
             "node_type": "EXPERIMENTAL_FACTOR",
             "description": "The condition under which the resistance is observed. Ungrounded."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "nitroreduction",
             "predicate": "enables (nitroreduction)", "predicate_id": "RO:0002327",
             "evidence": [{"reference": "ARO:3003755", "snippet": "The nsfB gene encodes a minor oxygen-insensitive nitroreductase. NfsB reduces a broad range of nitroaromatic compounds including the antibiotics nitrofurazone and nitrofurantoin. NfsB is a flavin mononucleotide (FMN)-containing protein and uses both NADH and NADPH as a source of reducing equivalents. Mutations in nfsB lead to increased resistance to nitrofurazone and furazolidone in an nfsA mutant background.",
                           "notes": "'The nsfB gene encodes a minor oxygen-insensitive nitroreductase'."}]},
            {"subject": "nitroreduction", "object": "drug0",
             "predicate": "has input (the nitroaromatic antibiotic)", "predicate_id": "RO:0002233",
             "description": "The enzyme acts ON the drug -- which is what makes losing it prodrug-activation loss rather than target alteration.",
             "evidence": [{"reference": "ARO:3003755", "snippet": "The nsfB gene encodes a minor oxygen-insensitive nitroreductase. NfsB reduces a broad range of nitroaromatic compounds including the antibiotics nitrofurazone and nitrofurantoin. NfsB is a flavin mononucleotide (FMN)-containing protein and uses both NADH and NADPH as a source of reducing equivalents. Mutations in nfsB lead to increased resistance to nitrofurazone and furazolidone in an nfsA mutant background.",
                           "notes": "'NfsB reduces a broad range of nitroaromatic compounds INCLUDING THE ANTIBIOTICS nitrofurazone and nitrofurantoin'."}]},
            {"subject": "nfsa_background", "object": "determinant",
             "predicate": "causally upstream of (the background in which resistance is seen)",
             "predicate_id": "RO:0002411",
             "description": "A genetic PRECONDITION, not a mechanism step. Kept because dropping it would turn a conditional observation into an unconditional claim.",
             "evidence": [{"reference": "ARO:3003755", "snippet": "The nsfB gene encodes a minor oxygen-insensitive nitroreductase. NfsB reduces a broad range of nitroaromatic compounds including the antibiotics nitrofurazone and nitrofurantoin. NfsB is a flavin mononucleotide (FMN)-containing protein and uses both NADH and NADPH as a source of reducing equivalents. Mutations in nfsB lead to increased resistance to nitrofurazone and furazolidone in an nfsA mutant background.",
                           "notes": "'Mutations in nfsB lead to increased resistance ... IN AN nfsA MUTANT BACKGROUND'."}]},
        ],
    },
    # rpoA (ARO:3004997) -- round 106's rpoB shape, one sentence shorter.
    "ARO:3004997": {
        "curated": "2026-08-08T00:00:00Z",
        "precondition": _requires_mech("ARO:3000212", "mutation"),
        "reference": "ARO:3004997",
        "mech": {"ARO:3000212": "RNA polymerase is a multisubunit enzyme that is necessary for transcription. Mutations in rpoA gene confer antibiotic resistance."},
        "mech_res": "RNA polymerase is a multisubunit enzyme that is necessary for transcription. Mutations in rpoA gene confer antibiotic resistance.",
        "det_res": [
            {"reference": "ARO:3004997", "snippet": "RNA polymerase is a multisubunit enzyme that is necessary for transcription. Mutations in rpoA gene confer antibiotic resistance.",
             "notes": "Even barer than rpoB and rpoC (rounds 106, 83): the polymerase's role and a resistance claim, with not even a statement of what the alpha-subunit contributes."},
        ],
        "res_drug": "RNA polymerase is a multisubunit enzyme that is necessary for transcription. Mutations in rpoA gene confer antibiotic resistance.",
        "note": ("Mechanism NOT asserted, and less is available than for rpoB or rpoC -- "
                 "CARD does not say what the alpha-subunit does, so there is no structural "
                 "edge to write either."),
        "extra_nodes": [
            {"node_id": "transcription", "label": "transcription", "node_type": "BIOLOGICAL_PROCESS",
             "description": "Ungrounded: not looked up rather than guessed."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "transcription",
             "predicate": "participates in (transcription)", "predicate_id": "RO:0000056",
             "description": "'Participates in', not 'part of the active center' as for rpoB and rpoC -- CARD says what those subunits form and does not say it here.",
             "evidence": [{"reference": "ARO:3004997", "snippet": "RNA polymerase is a multisubunit enzyme that is necessary for transcription. Mutations in rpoA gene confer antibiotic resistance.",
                           "notes": "'RNA polymerase is a multisubunit enzyme that is necessary for transcription'. NOT asserted: the alpha-subunit's specific contribution, or any drug interaction."}]},
        ],
    },
    # rpoB (ARO:3003276) -- round 83's rpoC shape, and the symmetry is the point.
    #
    # Round 83 refused to give rpoC rifampicin's mechanism, noting that rifampicin binds
    # rpoB, not rpoC -- so the obvious guess was attached to the wrong subunit. Here is
    # rpoB, where that mechanism WOULD belong, and CARD does not state it either. Its
    # definition is structurally identical to rpoC's: the polymerase's role, the subunit's
    # structural contribution, and a bare "mutations confer resistance" with nothing
    # between.
    #
    # So the refusal was doubly right, and rpoB gets the same graph its neighbour got.
    "ARO:3003276": {
        "curated": "2026-08-08T00:00:00Z",
        "precondition": _requires_mech("ARO:3000212", "mutation"),
        "reference": "ARO:3003276",
        "mech": {"ARO:3000212": "RNA polymerase is a multisubunit enzyme that is necessary for transcription. The beta-subunit of RNA polymerase forms the active center of the enzyme and template/transcript binding sites. Mutations in rpoB gene confers antibiotic resistance."},
        "mech_res": "RNA polymerase is a multisubunit enzyme that is necessary for transcription. The beta-subunit of RNA polymerase forms the active center of the enzyme and template/transcript binding sites. Mutations in rpoB gene confers antibiotic resistance.",
        "det_res": [
            {"reference": "ARO:3003276", "snippet": "RNA polymerase is a multisubunit enzyme that is necessary for transcription. The beta-subunit of RNA polymerase forms the active center of the enzyme and template/transcript binding sites. Mutations in rpoB gene confers antibiotic resistance.",
             "notes": "Role, structural contribution, and a bare resistance claim. Rifampicin DOES bind rpoB -- and CARD does not say so here, so it is not asserted. Round 83 refused this mechanism for rpoC because it belongs to rpoB; it turns out not to be citable for rpoB either."},
        ],
        "res_drug": "RNA polymerase is a multisubunit enzyme that is necessary for transcription. The beta-subunit of RNA polymerase forms the active center of the enzyme and template/transcript binding sites. Mutations in rpoB gene confers antibiotic resistance.",
        "note": ("Mechanism deliberately NOT asserted. The rifampicin-rpoB interaction is "
                 "textbook and this is the record it belongs to -- which makes it the most "
                 "inviting uncited edge in the corpus, and the reason the omission is "
                 "pinned rather than trusted."),
        "extra_nodes": [
            {"node_id": "transcription", "label": "transcription", "node_type": "BIOLOGICAL_PROCESS",
             "description": "Ungrounded: not looked up rather than guessed (rounds 56-104)."},
            {"node_id": "active_center", "label": "RNA polymerase active center and template/transcript binding sites",
             "node_type": "PROTEIN",
             "description": "What the beta-subunit forms. Ungrounded."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "active_center",
             "predicate": "part of (the polymerase active center)", "predicate_id": "BFO:0000050",
             "evidence": [{"reference": "ARO:3003276", "snippet": "RNA polymerase is a multisubunit enzyme that is necessary for transcription. The beta-subunit of RNA polymerase forms the active center of the enzyme and template/transcript binding sites. Mutations in rpoB gene confers antibiotic resistance.",
                           "notes": "'The beta-subunit of RNA polymerase forms the active center of the enzyme and template/transcript binding sites'."}]},
            {"subject": "active_center", "object": "transcription",
             "predicate": "part of (transcription)", "predicate_id": "BFO:0000050",
             "evidence": [{"reference": "ARO:3003276", "snippet": "RNA polymerase is a multisubunit enzyme that is necessary for transcription. The beta-subunit of RNA polymerase forms the active center of the enzyme and template/transcript binding sites. Mutations in rpoB gene confers antibiotic resistance.",
                           "notes": "'RNA polymerase ... is necessary for transcription'. NOT asserted: that rifampicin binds this centre, which CARD does not state even here."}]},
        ],
    },
    # pgsA (ARO:3003420) -- a biosynthetic role and no mechanism. Round 95's aftA shape.
    #
    # Left in round 96 as "a role and no mechanism", which is exactly what round 95 had
    # curated aftA on one round earlier. Second inconsistency of the same kind as round
    # 104's P450, and found the same way -- by re-reading what I had written.
    "ARO:3003420": {
        "curated": "2026-08-08T00:00:00Z",
        "precondition": _requires_mech("ARO:3000212", "mutation"),
        "reference": "ARO:3003420",
        "mech": {"ARO:3000212": "pgsA or phosphatidylglycerophosphate synthetase is an integral membrane protein involved in phospholipid biosynthesis. It is a CDP-diacylglycerol-glycerol-3-phosphate 3-phosphatidyltransferase."},
        "mech_res": "pgsA or phosphatidylglycerophosphate synthetase is an integral membrane protein involved in phospholipid biosynthesis. It is a CDP-diacylglycerol-glycerol-3-phosphate 3-phosphatidyltransferase.",
        "det_res": [
            {"reference": "ARO:3003420", "snippet": "pgsA or phosphatidylglycerophosphate synthetase is an integral membrane protein involved in phospholipid biosynthesis. It is a CDP-diacylglycerol-glycerol-3-phosphate 3-phosphatidyltransferase.",
             "notes": "Enzyme identity and pathway, twice over: the protein class and the exact transferase (EC-style) name. CARD says nothing about mutations, a drug, or resistance -- as with aftA (round 95)."},
        ],
        "res_drug": "pgsA or phosphatidylglycerophosphate synthetase is an integral membrane protein involved in phospholipid biosynthesis. It is a CDP-diacylglycerol-glycerol-3-phosphate 3-phosphatidyltransferase.",
        "note": ("Biosynthetic role only. NOT asserted: any resistance mechanism -- CARD's "
                 "sentences name an enzyme and a pathway and never mention a drug. Round "
                 "95's aftA position, applied consistently this time."),
        "extra_nodes": [
            {"node_id": "pgp_synthase", "label": "CDP-diacylglycerol-glycerol-3-phosphate 3-phosphatidyltransferase activity",
             "node_type": "MOLECULAR_FUNCTION",
             "description": "CARD names the reaction precisely. Ungrounded: not looked up rather than guessed."},
            {"node_id": "phospholipid", "label": "phospholipid biosynthesis",
             "node_type": "BIOLOGICAL_PROCESS",
             "description": "The pathway. Ungrounded: no term verified this round."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "pgp_synthase",
             "predicate": "enables (phosphatidylglycerophosphate synthesis)",
             "predicate_id": "RO:0002327",
             "evidence": [{"reference": "ARO:3003420", "snippet": "pgsA or phosphatidylglycerophosphate synthetase is an integral membrane protein involved in phospholipid biosynthesis. It is a CDP-diacylglycerol-glycerol-3-phosphate 3-phosphatidyltransferase.",
                           "notes": "'It is a CDP-diacylglycerol-glycerol-3-phosphate 3-phosphatidyltransferase' -- CARD names the reaction, not just the pathway."}]},
            {"subject": "pgp_synthase", "object": "phospholipid",
             "predicate": "part of (phospholipid biosynthesis)", "predicate_id": "BFO:0000050",
             "evidence": [{"reference": "ARO:3003420", "snippet": "pgsA or phosphatidylglycerophosphate synthetase is an integral membrane protein involved in phospholipid biosynthesis. It is a CDP-diacylglycerol-glycerol-3-phosphate 3-phosphatidyltransferase.",
                           "notes": "'involved in phospholipid biosynthesis'. NOT asserted: any link to a drug, which CARD's sentences do not contain."}]},
        ],
    },
    # The rRNA PARENT term (ARO:3000328) -- rounds 54-55 curated its children, not it.
    "ARO:3000328": {
        "curated": "2026-08-08T00:00:00Z",
        "precondition": _requires_mech("ARO:3000212", "mutation"),
        "determinant_node_type": "NUCLEIC_ACID",
        "reference": "ARO:3000328",
        "mech": {"ARO:3000212": "Single nucleotide polymorphisms (SNPs) in rRNA can confer antibiotic resistance to drugs that target the bacterial ribosome."},
        "mech_res": "Single nucleotide polymorphisms (SNPs) in rRNA can confer antibiotic resistance to drugs that target the bacterial ribosome.",
        "det_res": [
            {"reference": "ARO:3000328", "snippet": "Single nucleotide polymorphisms (SNPs) in rRNA can confer antibiotic resistance to drugs that target the bacterial ribosome.",
             "notes": "The general claim over both subunits: SNPs in rRNA confer resistance to drugs that TARGET THE RIBOSOME. Rounds 54-55 curated the 16S and 23S children with their own mechanism sentences; this term is the shared statement above them."},
        ],
        "res_drug": "Single nucleotide polymorphisms (SNPs) in rRNA can confer antibiotic resistance to drugs that target the bacterial ribosome.",
        "note": ("The rRNA parent term. NOT asserted: the binding-site partonomy that makes "
                 "rounds 54-55's graphs distinctive -- that comes from the 16S and 23S "
                 "definitions, not from this one, which says only that the drugs target "
                 "the ribosome."),
        "extra_nodes": [
            {"node_id": "ribosome", "label": "the bacterial ribosome",
             "node_type": "CELLULAR_LOCALIZATION",
             "description": "What the drugs target. Ungrounded: CARD says 'the bacterial ribosome' without a subunit, and rounds 54-55 grounded the specific subunits from the specific terms."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "ribosome",
             "predicate": "part of (the bacterial ribosome)", "predicate_id": "BFO:0000050",
             "evidence": [{"reference": "ARO:3000328", "snippet": "Single nucleotide polymorphisms (SNPs) in rRNA can confer antibiotic resistance to drugs that target the bacterial ribosome.",
                           "notes": "rRNA is a ribosomal component; CARD frames the drugs as targeting the ribosome."}]},
            {"subject": "drug0", "object": "ribosome",
             "predicate": "molecularly interacts with (targets the ribosome)",
             "predicate_id": "RO:0002436",
             "description": "The general form of what rounds 54-55 stated per-subunit with a named binding site.",
             "evidence": [{"reference": "ARO:3000328", "snippet": "Single nucleotide polymorphisms (SNPs) in rRNA can confer antibiotic resistance to drugs that target the bacterial ribosome.",
                           "notes": "'drugs that target the bacterial ribosome'. NOT asserted: which site, which this term does not give."}]},
        ],
    },
    # cls / cardiolipin synthetase (ARO:3003272) -- three sentences, and the third does
    # not connect to the first two.
    #
    # CARD gives the reaction, says the product matters for "membrane translocation and
    # permeabilization", and then states that mutations confer daptomycin resistance. It
    # never says HOW altered cardiolipin resists daptomycin -- and daptomycin is a
    # membrane-active lipopeptide, so the connection is inviting and uncited. Round 81's
    # ppsA-E position, with one more sentence of context and the same gap.
    "ARO:3003272": {
        "curated": "2026-08-08T00:00:00Z",
        "precondition": _requires_mech("ARO:3000212", "mutation"),
        "reference": "ARO:3003272",
        "mech": {"ARO:3000212": "Cardiolipin synthetase catalyzes the formation of cardiolipin from two phosphatidylglycerol molecules. Cardiolipin is important in membrane translocation and permeabilization. Current known mutations on the enzyme confer resistance to daptomycin."},
        "mech_res": "Cardiolipin synthetase catalyzes the formation of cardiolipin from two phosphatidylglycerol molecules. Cardiolipin is important in membrane translocation and permeabilization. Current known mutations on the enzyme confer resistance to daptomycin.",
        "det_res": [
            {"reference": "ARO:3003272", "snippet": "Cardiolipin synthetase catalyzes the formation of cardiolipin from two phosphatidylglycerol molecules. Cardiolipin is important in membrane translocation and permeabilization. Current known mutations on the enzyme confer resistance to daptomycin.",
             "notes": "Three sentences: the reaction, why the product matters, and the resistance. The third does not follow from the first two in anything CARD writes -- 'Current known mutations on the enzyme confer resistance to daptomycin' is asserted, not derived."},
        ],
        "res_drug": "Cardiolipin synthetase catalyzes the formation of cardiolipin from two phosphatidylglycerol molecules. Cardiolipin is important in membrane translocation and permeabilization. Current known mutations on the enzyme confer resistance to daptomycin.",
        "note": ("Cardiolipin synthesis. NOT asserted: how altered cardiolipin resists "
                 "daptomycin. Daptomycin is membrane-active and the inference is inviting, "
                 "which is exactly why it is left out -- the same reason round 83 refused "
                 "to give rpoC rifampicin's rpoB mechanism."),
        "extra_nodes": [
            {"node_id": "cl_synthesis", "label": "cardiolipin synthase activity",
             "node_type": "MOLECULAR_FUNCTION",
             "description": "Ungrounded: not looked up rather than guessed (rounds 56-102)."},
            {"node_id": "cardiolipin", "label": "cardiolipin",
             "node_type": "CHEMICAL",
             "description": "The product. Ungrounded: no CHEBI id verified this round."},
            {"node_id": "membrane_role", "label": "membrane translocation and permeabilization",
             "node_type": "BIOLOGICAL_PROCESS",
             "description": "What CARD says cardiolipin matters for -- quoted, not connected to the drug."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "cl_synthesis",
             "predicate": "enables (cardiolipin synthesis)", "predicate_id": "RO:0002327",
             "evidence": [{"reference": "ARO:3003272", "snippet": "Cardiolipin synthetase catalyzes the formation of cardiolipin from two phosphatidylglycerol molecules. Cardiolipin is important in membrane translocation and permeabilization. Current known mutations on the enzyme confer resistance to daptomycin.",
                           "notes": "'Cardiolipin synthetase catalyzes the formation of cardiolipin from two phosphatidylglycerol molecules'."}]},
            {"subject": "cl_synthesis", "object": "cardiolipin",
             "predicate": "has output (cardiolipin)", "predicate_id": "RO:0002234",
             "evidence": [{"reference": "ARO:3003272", "snippet": "Cardiolipin synthetase catalyzes the formation of cardiolipin from two phosphatidylglycerol molecules. Cardiolipin is important in membrane translocation and permeabilization. Current known mutations on the enzyme confer resistance to daptomycin.",
                           "notes": "The product named in the same sentence."}]},
            {"subject": "cardiolipin", "object": "membrane_role",
             "predicate": "participates in (membrane translocation and permeabilization)",
             "predicate_id": "RO:0000056",
             "description": "Where the graph stops. CARD says cardiolipin is IMPORTANT IN these processes and never links them to daptomycin.",
             "evidence": [{"reference": "ARO:3003272", "snippet": "Cardiolipin synthetase catalyzes the formation of cardiolipin from two phosphatidylglycerol molecules. Cardiolipin is important in membrane translocation and permeabilization. Current known mutations on the enzyme confer resistance to daptomycin.",
                           "notes": "'Cardiolipin is important in membrane translocation and permeabilization'. NOT asserted: any connection between that role and daptomycin resistance, which CARD asserts separately and does not derive."}]},
        ],
    },
    # ESX-5 secretion subunits (under ARO:3004916) -- reduced permeability, and one
    # record in which CARD contradicts itself.
    #
    # The family TERM carries no mechanism id at all, which is why nothing could be keyed
    # on it; its MEMBERS do. Both curated records name their role in a named complex
    # (round 86's subunit shape) and state the mechanism: mutations "contribute to a
    # DECREASED UPTAKE of antibiotic in the outer membrane" -- reduced permeability.
    "ARO:3004916": {
        "curated": "2026-08-08T00:00:00Z",
        "precondition": _requires_esx5_subunit,
        "reference": "ARO:3004918",
        "mech": {"ARO:3000212": "eccB5 is a transmembrane protein within the ESX-5 secretion system complex. The complex is critical for mycobacterium viability and virulence in the host cell and mutations contribute to a decreased uptake of antibiotic in the outer membrane."},
        "mech_res": "eccB5 is a transmembrane protein within the ESX-5 secretion system complex. The complex is critical for mycobacterium viability and virulence in the host cell and mutations contribute to a decreased uptake of antibiotic in the outer membrane.",
        "det_res": [
            {"reference": "ARO:3004918", "snippet": "eccB5 is a transmembrane protein within the ESX-5 secretion system complex. The complex is critical for mycobacterium viability and virulence in the host cell and mutations contribute to a decreased uptake of antibiotic in the outer membrane.",
             "notes": "Role in a named complex, and the mechanism: mutations 'contribute to a DECREASED UPTAKE of antibiotic in the outer membrane'. NOTE the hedge -- 'contribute to', not 'confer'."},
            {"reference": "ARO:3004919", "snippet": "eccC5 is a membrane-bound ATPase within the ESX-5 secretion system complex. The complex is critical for mycobacterium viability and virulence in the host cell and mutations contribute to a decreased uptake of antibiotic in the outer membrane, yet the Relational Sequencing Tuberculosis Data platform (ReSeqTB, https://platform.reseqtb.org) finds no evidence of an association between eccC5 mutations and drug resistance.",
             "notes": "The SAME sentence for eccC5 -- followed by CARD contradicting it in the same breath: 'YET the Relational Sequencing Tuberculosis Data platform finds NO EVIDENCE of an association between eccC5 mutations and drug resistance'. Quoted whole rather than truncated at the comma."},
        ],
        "res_drug": "eccB5 is a transmembrane protein within the ESX-5 secretion system complex. The complex is critical for mycobacterium viability and virulence in the host cell and mutations contribute to a decreased uptake of antibiotic in the outer membrane.",
        "note": ("Reduced permeability via an ESX-5 subunit. The eccC5 record CONTRADICTS "
                 "ITSELF -- it states the mechanism and then cites ReSeqTB finding no "
                 "association -- and the snippet is quoted whole so the contradiction "
                 "travels with the claim. This corpus has no way to mark a contested claim "
                 "structurally (#220, #306); prose is the only available carrier."),
        "extra_nodes": [
            {"node_id": "esx5", "label": "ESX-5 secretion system complex",
             "node_type": "PROTEIN",
             "description": "The complex the determinant belongs to. Ungrounded."},
            {"node_id": "uptake", "label": "uptake of antibiotic across the outer membrane",
             "node_type": "BIOLOGICAL_PROCESS",
             "description": "What the mutations reduce. Ungrounded."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "esx5",
             "predicate": "part of (the ESX-5 secretion system complex)",
             "predicate_id": "BFO:0000050",
             "description": "Round 86's subunit shape: a subunit is PART OF the complex, not the complex.",
             "evidence": [{"reference": "ARO:3004918", "snippet": "eccB5 is a transmembrane protein within the ESX-5 secretion system complex. The complex is critical for mycobacterium viability and virulence in the host cell and mutations contribute to a decreased uptake of antibiotic in the outer membrane.",
                           "notes": "'a transmembrane protein WITHIN the ESX-5 secretion system complex'."}]},
            {"subject": "determinant", "object": "uptake",
             "predicate": "negatively regulates (decreased antibiotic uptake)",
             "predicate_id": "RO:0002212",
             "description": "The mechanism, hedged as CARD hedges it ('contribute to') -- and for eccC5 specifically, contradicted by the same definition's closing clause.",
             "evidence": [
                 {"reference": "ARO:3004918", "snippet": "eccB5 is a transmembrane protein within the ESX-5 secretion system complex. The complex is critical for mycobacterium viability and virulence in the host cell and mutations contribute to a decreased uptake of antibiotic in the outer membrane.",
                  "notes": "'mutations contribute to a decreased uptake of antibiotic in the outer membrane'."},
                 {"reference": "ARO:3004919", "snippet": "eccC5 is a membrane-bound ATPase within the ESX-5 secretion system complex. The complex is critical for mycobacterium viability and virulence in the host cell and mutations contribute to a decreased uptake of antibiotic in the outer membrane, yet the Relational Sequencing Tuberculosis Data platform (ReSeqTB, https://platform.reseqtb.org) finds no evidence of an association between eccC5 mutations and drug resistance.",
                  "notes": "The contradicting evidence, on the SAME edge rather than omitted: ReSeqTB 'finds no evidence of an association between eccC5 mutations and drug resistance'. A reader of this edge sees both."}]},
        ],
    },
    # Generic target protection (ARO:3000185) -- the records the three MODE configs miss.
    #
    # Rounds 31, 44 and 45 curated TetM, FusB and HelR, each a distinct protection MODE
    # with its own paper. These three records describe protection WITHOUT naming a mode,
    # so no mode config fits and none should be stretched. The family term itself states
    # the general mechanism completely.
    "ARO:3000185-generic": {
        "curated": "2026-08-08T00:00:00Z",
        "precondition": _requires_generic_target_protection,
        "reference": "ARO:3000185",
        "mech": {"ARO:0001003": "These proteins confer antibiotic resistance by bind the antibiotic target to prevent antibiotic binding."},
        "mech_res": "These proteins confer antibiotic resistance by bind the antibiotic target to prevent antibiotic binding.",
        "det_res": [
            {"reference": "ARO:3000185", "snippet": "These proteins confer antibiotic resistance by bind the antibiotic target to prevent antibiotic binding.",
             "notes": "The general mechanism, complete: the determinant BINDS THE TARGET to PREVENT THE ANTIBIOTIC BINDING. (CARD's 'by bind' is its own wording, quoted verbatim.)"},
            {"reference": "ARO:3000507", "snippet": "Proteins which have been experimentally shown to protect RNA-polymerase from rifampin inhibition.",
             "notes": "The RNAP case, with its evidential status stated: 'have been EXPERIMENTALLY SHOWN to protect'. SCOPE: rifampin and RNA polymerase specifically."},
        ],
        "res_drug": "These proteins confer antibiotic resistance by bind the antibiotic target to prevent antibiotic binding.",
        "note": ("Target protection without a named mode. Rounds 31/44/45 curated the three "
                 "modes that DO have papers -- ribosome displacement, EF-G rescue, RNAP "
                 "displacement. NOT asserted here: which of them applies, since these "
                 "records do not say and stretching a mode config to cover them would "
                 "import a mechanism from an unrelated paper."),
        "extra_nodes": [
            {"node_id": "target", "label": "the antibiotic's target",
             "node_type": "PROTEIN",
             "description": "Deliberately unnamed: CARD's general claim is about ANY target, and one member names RNA polymerase while another does not."},
            {"node_id": "blocked_binding", "label": "antibiotic prevented from binding its target",
             "node_type": "STATE",
             "description": "The causal core, in CARD's own words."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "target",
             "predicate": "molecularly interacts with (binds the antibiotic target)",
             "predicate_id": "RO:0002436",
             "description": "The defining act: protection works by binding the TARGET, not the drug -- which is what separates it from sequestration (round 72), where the determinant binds the drug.",
             "evidence": [{"reference": "ARO:3000185", "snippet": "These proteins confer antibiotic resistance by bind the antibiotic target to prevent antibiotic binding.",
                           "notes": "'bind the antibiotic target'."}]},
            {"subject": "determinant", "object": "blocked_binding",
             "predicate": "causally upstream of (prevents antibiotic binding)",
             "predicate_id": "RO:0002411",
             "evidence": [
                 {"reference": "ARO:3000185", "snippet": "These proteins confer antibiotic resistance by bind the antibiotic target to prevent antibiotic binding.",
                  "notes": "'to prevent antibiotic binding'."},
                 {"reference": "ARO:3000507", "snippet": "Proteins which have been experimentally shown to protect RNA-polymerase from rifampin inhibition.",
                  "notes": "And the one member with an evidential claim attached: 'experimentally shown'."}]},
        ],
    },
    # tet(34) (ARO:3002870) -- target protection, curated at last.
    #
    # Excluded from four chemistry configs across rounds 60, 70 and 91 because its
    # mechanism ids (inactivation, hydroxylation, cell-wall restructuring) describe
    # nothing it does. Every one of those refusals was right, and together they left the
    # record with no graph for 37 rounds -- because "this config does not fit" was never
    # followed by "so which one does?".
    "ARO:3002870": {
        "curated": "2026-08-08T00:00:00Z",
        "precondition": _requires_tet34_protection,
        "reference": "ARO:3002870",
        "mech": {"ARO:0001004": "tet(34) causes the activation of Mg2+-dependent purine nucleotide synthesis, which protects the protein synthesis pathway. It is found in Gram-negative Vibrio.",
                 "ARO:3000213": "tet(34) causes the activation of Mg2+-dependent purine nucleotide synthesis, which protects the protein synthesis pathway. It is found in Gram-negative Vibrio.",
                 "ARO:3000450": "tet(34) causes the activation of Mg2+-dependent purine nucleotide synthesis, which protects the protein synthesis pathway. It is found in Gram-negative Vibrio."},
        "mech_res": "tet(34) causes the activation of Mg2+-dependent purine nucleotide synthesis, which protects the protein synthesis pathway. It is found in Gram-negative Vibrio.",
        "det_res": [
            {"reference": "ARO:3002870", "snippet": "tet(34) causes the activation of Mg2+-dependent purine nucleotide synthesis, which protects the protein synthesis pathway. It is found in Gram-negative Vibrio.",
             "notes": "The mechanism CARD does state, after three it does not: activation of Mg2+-dependent purine nucleotide synthesis PROTECTS the protein synthesis pathway. All three of this record's mechanism ids are covered by this one sentence because none of them is what it describes -- the sentence is the honest evidence for each."},
        ],
        "res_drug": "tet(34) causes the activation of Mg2+-dependent purine nucleotide synthesis, which protects the protein synthesis pathway. It is found in Gram-negative Vibrio.",
        "note": ("Target protection, not inactivation. This record carries three chemistry "
                 "mechanism ids and describes none of them; the same sentence is cited for "
                 "all three because it is the only mechanism CARD gives. NOT asserted: how "
                 "purine nucleotide synthesis protects translation, which CARD omits."),
        "extra_nodes": [
            {"node_id": "purine_synthesis", "label": "Mg2+-dependent purine nucleotide synthesis",
             "node_type": "BIOLOGICAL_PROCESS",
             "description": "Ungrounded: not looked up rather than guessed (rounds 56-96)."},
            {"node_id": "protection", "label": "protection of the protein synthesis pathway",
             "node_type": "STATE",
             "description": "The causal core. Ungrounded, and deliberately unelaborated -- CARD says protection happens, not how."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "purine_synthesis",
             "predicate": "positively regulates (activates purine nucleotide synthesis)",
             "predicate_id": "RO:0002213",
             "description": "The POSITIVE form, licensed by CARD's own 'causes the ACTIVATION of'.",
             "evidence": [{"reference": "ARO:3002870", "snippet": "tet(34) causes the activation of Mg2+-dependent purine nucleotide synthesis, which protects the protein synthesis pathway. It is found in Gram-negative Vibrio.",
                           "notes": "'tet(34) causes the activation of Mg2+-dependent purine nucleotide synthesis'."}]},
            {"subject": "purine_synthesis", "object": "protection",
             "predicate": "causally upstream of (protects protein synthesis)",
             "predicate_id": "RO:0002411",
             "description": "The causal core, and where CARD stops -- it says the pathway is protected, not by what route.",
             "evidence": [{"reference": "ARO:3002870", "snippet": "tet(34) causes the activation of Mg2+-dependent purine nucleotide synthesis, which protects the protein synthesis pathway. It is found in Gram-negative Vibrio.",
                           "notes": "'which protects the protein synthesis pathway'. NOT asserted: the mechanism of that protection, nor any interaction with tetracycline, neither of which CARD gives."}]},
        ],
    },
    # ArmR (ARO:3004056) -- the antirepressor that defeated three keyword patterns.
    #
    # Referenced all session as the reason regulator lists cannot be built by keyword:
    # it is neither a repressor nor an activator, but an ANTIrepressor -- it inhibits a
    # repressor, and the double negative is what makes it an efflux determinant. Its own
    # definition states the whole chain, including the STRUCTURAL basis, which almost no
    # other regulator record in this corpus does.
    "ARO:3004056": {
        "curated": "2026-08-08T00:00:00Z",
        "precondition": _requires_armr,
        "reference": "ARO:3004056",
        "mech": {"ARO:0010000": "ArmR, a 53-amino-acid antirepressor, allosterically inhibits MexR dimer-DNA binding by occupying a hydrophobic binding cavity within the center of the MexR dimer. ArmR up-regulation and MexR-ArmR complex formation have previously been shown to upregulate MexAB-OprM."},
        "mech_res": "ArmR, a 53-amino-acid antirepressor, allosterically inhibits MexR dimer-DNA binding by occupying a hydrophobic binding cavity within the center of the MexR dimer. ArmR up-regulation and MexR-ArmR complex formation have previously been shown to upregulate MexAB-OprM.",
        "det_res": [
            {"reference": "ARO:3004056", "snippet": "ArmR, a 53-amino-acid antirepressor, allosterically inhibits MexR dimer-DNA binding by occupying a hydrophobic binding cavity within the center of the MexR dimer. ArmR up-regulation and MexR-ArmR complex formation have previously been shown to upregulate MexAB-OprM.",
             "notes": "The full chain and its structural basis: ArmR occupies a hydrophobic cavity in the MexR dimer, blocks MexR-DNA binding, and the resulting complex upregulates MexAB-OprM. A double negative -- inhibiting a repressor -- which is why keyword lists of repressors and activators both missed it."},
            {"reference": "ARO:0010000", "snippet": "Antibiotic resistance via the transport of antibiotics out of the cell.",
             "notes": "What the upregulated pump achieves."},
        ],
        "res_drug": "Antibiotic resistance via the transport of antibiotics out of the cell.",
        "note": ("Antirepression. ArmR inhibits MexR, MexR represses MexAB-OprM, so "
                 "inhibiting it raises efflux. The graph carries both negatives rather "
                 "than collapsing them into 'activates the pump'."),
        "extra_nodes": [
            {"node_id": "mexr_dna_binding", "label": "MexR dimer binding to DNA",
             "node_type": "STATE",
             "description": "What ArmR blocks. Ungrounded."},
            {"node_id": "pump_expression", "label": "MexAB-OprM expression",
             "node_type": "BIOLOGICAL_PROCESS",
             "description": "The outcome CARD names. Ungrounded."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "mexr_dna_binding",
             "predicate": "negatively regulates (allosterically blocks MexR-DNA binding)",
             "predicate_id": "RO:0002212",
             "description": "The FIRST negative, with its structural basis stated -- ArmR occupies a cavity in the MexR dimer rather than competing at the DNA site.",
             "evidence": [{"reference": "ARO:3004056", "snippet": "ArmR, a 53-amino-acid antirepressor, allosterically inhibits MexR dimer-DNA binding by occupying a hydrophobic binding cavity within the center of the MexR dimer. ArmR up-regulation and MexR-ArmR complex formation have previously been shown to upregulate MexAB-OprM.",
                           "notes": "'allosterically inhibits MexR dimer-DNA binding by occupying a hydrophobic binding cavity within the center of the MexR dimer'."}]},
            {"subject": "determinant", "object": "pump_expression",
             "predicate": "positively regulates (upregulates MexAB-OprM)",
             "predicate_id": "RO:0002213",
             "description": "The NET effect, stated separately from the mechanism because CARD states it separately -- and because collapsing the two would hide that this is antirepression rather than activation.",
             "evidence": [{"reference": "ARO:3004056", "snippet": "ArmR, a 53-amino-acid antirepressor, allosterically inhibits MexR dimer-DNA binding by occupying a hydrophobic binding cavity within the center of the MexR dimer. ArmR up-regulation and MexR-ArmR complex formation have previously been shown to upregulate MexAB-OprM.",
                           "notes": "'ArmR up-regulation and MexR-ArmR complex formation have previously been shown to upregulate MexAB-OprM'. NOTE the hedge: 'have PREVIOUSLY BEEN SHOWN', which CARD attributes rather than asserts directly."}]},
        ],
    },
    # PDR1 (ARO:3007640) -- a transcription factor, not a two-component pair.
    "ARO:3007640": {
        "curated": "2026-08-08T00:00:00Z",
        "precondition": _requires_transcription_factor_regulator,
        "reference": "ARO:3007640",
        "mech": {"ARO:0010000": "PDR1 is a transcription factor that regulates the expression of several genes encoding ABC transporters, contributing to multidrug resistance."},
        "mech_res": "PDR1 is a transcription factor that regulates the expression of several genes encoding ABC transporters, contributing to multidrug resistance.",
        "det_res": [
            {"reference": "ARO:3007640", "snippet": "PDR1 is a transcription factor that regulates the expression of several genes encoding ABC transporters, contributing to multidrug resistance.",
             "notes": "A single transcription factor regulating ABC transporter genes -- round 78's shape, not a two-component pair (#215). NOTE the hedge: 'CONTRIBUTING TO multidrug resistance'."},
        ],
        "res_drug": "Antibiotic resistance via the transport of antibiotics out of the cell.",
        "note": ("Transcriptional regulation of ABC transporters. CARD does not say whether "
                 "PDR1 activates or represses -- 'regulates' -- so the neutral predicate is "
                 "used, as in round 78 and unlike round 79."),
        "extra_nodes": [
            {"node_id": "transporter_genes", "label": "genes encoding ABC transporters",
             "node_type": "NUCLEIC_ACID",
             "description": "What PDR1 regulates. Ungrounded: CARD names no specific gene."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "transporter_genes",
             "predicate": "regulates (expression of ABC transporter genes)",
             "predicate_id": "RO:0002211",
             "description": "Neutral RO:0002211: CARD says 'regulates' without a direction, the same call as round 78's ARO:3000750 and the opposite of round 79's.",
             "evidence": [{"reference": "ARO:3007640", "snippet": "PDR1 is a transcription factor that regulates the expression of several genes encoding ABC transporters, contributing to multidrug resistance.",
                           "notes": "'regulates the expression of several genes encoding ABC transporters'."}]},
        ],
    },
    # mshA (ARO:3004900) -- prodrug-activation loss, in four words.
    #
    # The neighbouring mshC record reads "inability for antibiotic to FUNCTION" and was
    # left as a draft (round 94) because that says nothing mechanistic. mshA reads
    # "inability for antibiotic to ACTIVATE" -- one word different, and it names a
    # mechanism: the drug is a prodrug and this determinant's loss stops its activation.
    # Rounds 56 (pncA) and 57 (ndh) curated the same kind from richer sentences.
    "ARO:3004900": {
        "curated": "2026-08-07T00:00:00Z",
        "precondition": _requires_mech("ARO:3000212", "mutation"),
        "reference": "ARO:3004900",
        "mech": {"ARO:3000212": "Mutations that occur in the mshA gene resulting in the inability for antibiotic to activate."},
        "mech_res": "Mutations that occur in the mshA gene resulting in the inability for antibiotic to activate.",
        "det_res": [
            {"reference": "ARO:3004900", "snippet": "Mutations that occur in the mshA gene resulting in the inability for antibiotic to activate.",
             "notes": "The whole claim, and the word that carries it: mutations leave the antibiotic unable to ACTIVATE -- not merely to function. That makes it prodrug-activation loss (rounds 56, 57), which is more than the neighbouring mshC record says."},
        ],
        "res_drug": "Mutations that occur in the mshA gene resulting in the inability for antibiotic to activate.",
        "note": ("Prodrug-activation loss. NOT asserted: what mshA does, which drug it "
                 "activates, or how -- CARD gives none of it. The graph carries the "
                 "activation failure and nothing else."),
        "extra_nodes": [
            {"node_id": "activation", "label": "activation of the antibiotic",
             "node_type": "STATE",
             "description": "What the mutation prevents. Ungrounded, and deliberately unspecific: CARD names neither the drug nor the reaction."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "activation",
             "predicate": "negatively regulates (prevents the antibiotic activating)",
             "predicate_id": "RO:0002212",
             "description": "The one mechanistic claim CARD makes here, and the word that distinguishes this family from mshC's 'inability to function'.",
             "evidence": [{"reference": "ARO:3004900", "snippet": "Mutations that occur in the mshA gene resulting in the inability for antibiotic to activate.",
                           "notes": "'resulting in the inability for antibiotic to ACTIVATE'."}]},
        ],
    },
    # aftA (ARO:3003422) -- a biosynthetic role, and no resistance mechanism at all.
    #
    # CARD describes what the enzyme does and calls the product ESSENTIAL, but never says
    # what mutations do or why they confer resistance. Round 81's ppsA-E shape, minus even
    # the resistance sentence. Curated for the role; the gap is stated.
    "ARO:3003422": {
        "curated": "2026-08-07T00:00:00Z",
        "precondition": _requires_mech("ARO:3000212", "mutation"),
        "reference": "ARO:3003422",
        "mech": {"ARO:3000212": "Arabinofuranosyltransferase is involved in the biosynthesis of the arabinogalactan region of the mAGP complex, an essential component of the mycobacterial cell wall."},
        "mech_res": "Arabinofuranosyltransferase is involved in the biosynthesis of the arabinogalactan region of the mAGP complex, an essential component of the mycobacterial cell wall.",
        "det_res": [
            {"reference": "ARO:3003422", "snippet": "Arabinofuranosyltransferase is involved in the biosynthesis of the arabinogalactan region of the mAGP complex, an essential component of the mycobacterial cell wall.",
             "notes": "The enzyme's role and the product's importance ('an ESSENTIAL component of the mycobacterial cell wall'). CARD says nothing about what mutations do, nor which drug is involved."},
        ],
        "res_drug": "Arabinofuranosyltransferase is involved in the biosynthesis of the arabinogalactan region of the mAGP complex, an essential component of the mycobacterial cell wall.",
        "note": ("Biosynthetic role only. NOT asserted: any resistance mechanism -- CARD's "
                 "sentence never mentions a drug, mutations, or resistance, so the graph "
                 "carries what the enzyme does and stops. Thinner than round 81's ppsA-E, "
                 "which at least paired a role with a hedged resistance claim."),
        "extra_nodes": [
            {"node_id": "arabinofuranosyl_transfer", "label": "arabinofuranosyltransferase activity",
             "node_type": "MOLECULAR_FUNCTION",
             "description": "Ungrounded: not looked up rather than guessed (rounds 56-93)."},
            {"node_id": "magp", "label": "arabinogalactan region of the mAGP complex",
             "node_type": "CHEMICAL",
             "description": "The product, which CARD calls essential to the mycobacterial cell wall. Ungrounded."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "arabinofuranosyl_transfer",
             "predicate": "participates in (arabinogalactan biosynthesis)",
             "predicate_id": "RO:0000056",
             "description": "'Participates in', matching CARD's own 'is INVOLVED IN' rather than upgrading it.",
             "evidence": [{"reference": "ARO:3003422", "snippet": "Arabinofuranosyltransferase is involved in the biosynthesis of the arabinogalactan region of the mAGP complex, an essential component of the mycobacterial cell wall.",
                           "notes": "'Arabinofuranosyltransferase is INVOLVED IN the biosynthesis'."}]},
            {"subject": "arabinofuranosyl_transfer", "object": "magp",
             "predicate": "has output (the arabinogalactan region)", "predicate_id": "RO:0002234",
             "evidence": [{"reference": "ARO:3003422", "snippet": "Arabinofuranosyltransferase is involved in the biosynthesis of the arabinogalactan region of the mAGP complex, an essential component of the mycobacterial cell wall.",
                           "notes": "'the arabinogalactan region of the mAGP complex, an essential component'. NOT asserted: any link to a drug, which CARD's sentence does not contain."}]},
        ],
    },
    # Generic target-replacement proteins (ARO:3000381).
    #
    # Round 52 curated the WORKED case -- mecA/PBP2a, a foreign PBP doing the wall
    # synthesis. This is the same mechanism stated abstractly, and CARD supplies the piece
    # round 52 had to infer: WHY the alternate protein escapes the drug. "Structurally
    # different and THUS resistant" is the causal link, and "same functions" is why
    # substituting works at all. Both halves in one sentence.
    "ARO:3000381": {
        "curated": "2026-08-07T00:00:00Z",
        "precondition": _requires_mech("ARO:0001002", "target replacement"),
        "reference": "ARO:3000381",
        "mech": {"ARO:0001002": "Alternate proteins that have the same functions as other antibiotic target proteins, but are structurally different and thus resistant to antibiotics. These can replace the activity of other antibiotic-sensitive proteins in the presence of antibiotics."},
        "mech_res": "Alternate proteins that have the same functions as other antibiotic target proteins, but are structurally different and thus resistant to antibiotics. These can replace the activity of other antibiotic-sensitive proteins in the presence of antibiotics.",
        "det_res": [
            {"reference": "ARO:3000381", "snippet": "Alternate proteins that have the same functions as other antibiotic target proteins, but are structurally different and thus resistant to antibiotics. These can replace the activity of other antibiotic-sensitive proteins in the presence of antibiotics.",
             "notes": "Both halves: 'the SAME FUNCTIONS as other antibiotic target proteins' (why substitution works) and 'STRUCTURALLY DIFFERENT and thus resistant' (why the drug does not stop it). Round 52's mecA config had to leave the second implicit."},
        ],
        "res_drug": "Alternate proteins that have the same functions as other antibiotic target proteins, but are structurally different and thus resistant to antibiotics. These can replace the activity of other antibiotic-sensitive proteins in the presence of antibiotics.",
        "note": ("Target replacement, stated abstractly. The determinant does the SAME JOB "
                 "as the drug's target while being structurally unlike it. NOT asserted: "
                 "which target it replaces -- CARD's sentence is deliberately general and "
                 "the members do not name a specific one."),
        "extra_nodes": [
            {"node_id": "shared_function", "label": "the function shared with the drug's target",
             "node_type": "MOLECULAR_FUNCTION",
             "description": "Deliberately unnamed: CARD's claim is that the function is the SAME, not what it is."},
            {"node_id": "structural_difference", "label": "structural difference from the sensitive target",
             "node_type": "STATE",
             "description": "The causal core -- 'structurally different and THUS resistant'."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "shared_function",
             "predicate": "enables (the same function as the drug's target)",
             "predicate_id": "RO:0002327",
             "description": "Why substitution restores the cell: the replacement does the job the inhibited protein was doing.",
             "evidence": [{"reference": "ARO:3000381", "snippet": "Alternate proteins that have the same functions as other antibiotic target proteins, but are structurally different and thus resistant to antibiotics. These can replace the activity of other antibiotic-sensitive proteins in the presence of antibiotics.",
                           "notes": "'Alternate proteins that have the SAME FUNCTIONS as other antibiotic target proteins'."}]},
            {"subject": "determinant", "object": "structural_difference",
             "predicate": "has quality (structurally unlike the sensitive target)",
             "predicate_id": "RO:0000086",
             "evidence": [{"reference": "ARO:3000381", "snippet": "Alternate proteins that have the same functions as other antibiotic target proteins, but are structurally different and thus resistant to antibiotics. These can replace the activity of other antibiotic-sensitive proteins in the presence of antibiotics.",
                           "notes": "'but are STRUCTURALLY DIFFERENT and thus resistant to antibiotics' -- CARD's own 'thus' is the causal link round 52 had to infer."}]},
            {"subject": "structural_difference", "object": "drug0",
             "predicate": "negatively regulates (the drug does not act on it)",
             "predicate_id": "RO:0002212",
             "description": "The replacement escapes the drug BECAUSE it is built differently -- which is what distinguishes this from target alteration, where the same protein is modified.",
             "evidence": [{"reference": "ARO:3000381", "snippet": "Alternate proteins that have the same functions as other antibiotic target proteins, but are structurally different and thus resistant to antibiotics. These can replace the activity of other antibiotic-sensitive proteins in the presence of antibiotics.",
                           "notes": "'thus resistant to antibiotics'. NOT asserted: any binding measurement, which CARD does not give."}]},
        ],
    },
    # Rv1258c / Tap (ARO:3007183) -- named an efflux pump, and hedged.
    #
    # CARD gives one sentence: mutations in "the Rv1258c (Tap) EFFLUX PUMP" CONTRIBUTING
    # to resistance. The determinant is the pump itself, so unlike rounds 78-79 and 91
    # the graph does not route through a complex or a regulator. But "contributing to" is
    # weaker than "confers", and the pump's ENERGETICS are absent -- so no coupling node,
    # unlike SMR (round 67) and MATE (round 69) whose definitions supply one.
    "ARO:3007183": {
        "curated": "2026-08-07T00:00:00Z",
        "precondition": _requires_mech("ARO:3000212", "mutation"),
        "reference": "ARO:3007183",
        "mech": {"ARO:3000212": "Mutations in the Rv1258c (Tap) efflux pump contributing to antibiotic resistance."},
        "mech_res": "Mutations in the Rv1258c (Tap) efflux pump contributing to antibiotic resistance.",
        "det_res": [
            {"reference": "ARO:3007183", "snippet": "Mutations in the Rv1258c (Tap) efflux pump contributing to antibiotic resistance.",
             "notes": "The whole claim, with its hedge: mutations 'CONTRIBUTING TO' antibiotic resistance -- weaker than the 'confers' most families use."},
            {"reference": "ARO:0010000", "snippet": "Antibiotic resistance via the transport of antibiotics out of the cell.",
             "notes": "What efflux achieves. Cited so the graph can end at the process rather than invent a transport mechanism CARD does not describe."},
        ],
        "res_drug": "Mutations in the Rv1258c (Tap) efflux pump contributing to antibiotic resistance.",
        "note": ("An efflux pump named by its own record. NOT asserted: the coupling ion or "
                 "energy source -- unlike SMR (round 67, protons) and MATE (round 69, a "
                 "cationic gradient), CARD says nothing here about what drives Tap."),
        "extra_nodes": [
            {"node_id": "efflux_process", "label": "antibiotic efflux",
             "node_type": "BIOLOGICAL_PROCESS", "grounding": "ARO:0010000",
             "description": "Where this graph stops, for want of any energetics in the source."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "efflux_process",
             "predicate": "participates in (antibiotic efflux)", "predicate_id": "RO:0000056",
             "description": "'Participates in' rather than 'enables': these records are MUTANTS of the pump, and CARD says they contribute to resistance without saying the mutation increases transport.",
             "evidence": [{"reference": "ARO:3007183", "snippet": "Mutations in the Rv1258c (Tap) efflux pump contributing to antibiotic resistance.",
                           "notes": "'the Rv1258c (Tap) efflux pump'."}]},
            {"subject": "efflux_process", "object": "resistance",
             "predicate": "causally upstream of (confers resistance)",
             "predicate_id": "RO:0002411",
             "evidence": [{"reference": "ARO:0010000", "snippet": "Antibiotic resistance via the transport of antibiotics out of the cell.",
                           "notes": "'via the transport of antibiotics out of the cell'."}]},
        ],
    },
    # ileS (ARO:3000446) -- target alteration, with the drug's action stated and the
    # resistance LEVEL qualified. Two sentences, and the second hedges twice: "CAN confer
    # LOW-LEVEL" resistance. Both hedges are kept.
    "ARO:3000446": {
        "curated": "2026-08-07T00:00:00Z",
        "precondition": _requires_mech("ARO:3000212", "mutation"),
        "reference": "ARO:3000446",
        "mech": {"ARO:3000212": "Mupirocin inhibits protein synthesis by interfering with isoleucyl-tRNA synthetase (ileS). Mutations in ileS can confer low-level mupirocin resistance."},
        "mech_res": "Mupirocin inhibits protein synthesis by interfering with isoleucyl-tRNA synthetase (ileS). Mutations in ileS can confer low-level mupirocin resistance.",
        "det_res": [
            {"reference": "ARO:3000446", "snippet": "Mupirocin inhibits protein synthesis by interfering with isoleucyl-tRNA synthetase (ileS). Mutations in ileS can confer low-level mupirocin resistance.",
             "notes": "Drug action and resistance in two sentences. NOTE both hedges in the second: mutations 'CAN confer LOW-LEVEL' resistance -- neither the certainty nor the magnitude is asserted beyond that."},
        ],
        "res_drug": "Mupirocin inhibits protein synthesis by interfering with isoleucyl-tRNA synthetase (ileS). Mutations in ileS can confer low-level mupirocin resistance.",
        "note": ("Target alteration of the aminoacyl-tRNA synthetase mupirocin inhibits. "
                 "The resistance is qualified as LOW-LEVEL and conditional ('can confer'); "
                 "NOT asserted is HOW the mutations reduce the drug's effect, which CARD "
                 "does not say."),
        "extra_nodes": [
            {"node_id": "aminoacylation", "label": "isoleucyl-tRNA synthetase activity",
             "node_type": "MOLECULAR_FUNCTION",
             "description": "Ungrounded: not looked up rather than guessed (rounds 56-91)."},
            {"node_id": "protein_synthesis", "label": "protein synthesis",
             "node_type": "BIOLOGICAL_PROCESS",
             "description": "What the drug blocks. Ungrounded: no term verified this round."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "aminoacylation",
             "predicate": "enables (isoleucyl-tRNA charging)", "predicate_id": "RO:0002327",
             "evidence": [{"reference": "ARO:3000446", "snippet": "Mupirocin inhibits protein synthesis by interfering with isoleucyl-tRNA synthetase (ileS). Mutations in ileS can confer low-level mupirocin resistance.",
                           "notes": "ileS IS the isoleucyl-tRNA synthetase."}]},
            {"subject": "drug0", "object": "aminoacylation",
             "predicate": "negatively regulates (interferes with the synthetase)",
             "predicate_id": "RO:0002212",
             "evidence": [{"reference": "ARO:3000446", "snippet": "Mupirocin inhibits protein synthesis by interfering with isoleucyl-tRNA synthetase (ileS). Mutations in ileS can confer low-level mupirocin resistance.",
                           "notes": "'Mupirocin inhibits protein synthesis by interfering with isoleucyl-tRNA synthetase'."}]},
            {"subject": "aminoacylation", "object": "protein_synthesis",
             "predicate": "part of (protein synthesis)", "predicate_id": "BFO:0000050",
             "description": "Why inhibiting one synthetase stops translation: charged tRNA is required for it.",
             "evidence": [{"reference": "ARO:3000446", "snippet": "Mupirocin inhibits protein synthesis by interfering with isoleucyl-tRNA synthetase (ileS). Mutations in ileS can confer low-level mupirocin resistance.",
                           "notes": "'Mupirocin inhibits protein synthesis BY interfering with' the synthetase -- CARD makes the synthetase the route to the process."}]},
        ],
    },
    # ddl (ARO:3003970) -- the enzyme that makes the cell VULNERABLE.
    #
    # Every other van record curated in rounds 20-23 and 87-89 describes something that
    # produces resistance. ddl is the opposite: it synthesises D-Ala-D-Ala, "the default
    # cell wall precursor that makes a cell VULNERABLE to glycopeptide antibiotics".
    # Losing it is what matters, which makes this round 71's resistance-by-absence shape
    # arriving from the van set.
    #
    # CARD also states a DEPENDENCE, not just a resistance: nonfunctional ddl "can render
    # bacteria glycopeptide DEPENDENT depending on the presence of vancomycin resistance
    # clusters". That is a conditional phenotype -- doubly hedged ("can", "depending on")
    # -- and it is quoted rather than reduced to resistance.
    "ARO:3003970": {
        "curated": "2026-08-07T00:00:00Z",
        "precondition": _requires_ddl_ligase,
        "reference": "ARO:3003970",
        "mech": {"ARO:3000213": "Non-van ligases that synthesize D-Ala-D-Ala, the default cell wall precursor that makes a cell vulnerable to glycopeptide antibiotics. Mutations in the ddl gene can cause the production of nonfunctional/inactivated D-Ala-D-Ala ligases, which can render bacteria glycopeptide dependent depending on the presence of vancomycin resistance clusters."},
        "mech_res": "Non-van ligases that synthesize D-Ala-D-Ala, the default cell wall precursor that makes a cell vulnerable to glycopeptide antibiotics. Mutations in the ddl gene can cause the production of nonfunctional/inactivated D-Ala-D-Ala ligases, which can render bacteria glycopeptide dependent depending on the presence of vancomycin resistance clusters.",
        "det_res": [
            {"reference": "ARO:3003970", "snippet": "Non-van ligases that synthesize D-Ala-D-Ala, the default cell wall precursor that makes a cell vulnerable to glycopeptide antibiotics. Mutations in the ddl gene can cause the production of nonfunctional/inactivated D-Ala-D-Ala ligases, which can render bacteria glycopeptide dependent depending on the presence of vancomycin resistance clusters.",
             "notes": "The inversion, and the hedge. ddl makes the precursor that renders a cell VULNERABLE; mutations inactivate it; and the resulting phenotype is glycopeptide DEPENDENCE, stated conditionally ('can render … depending on the presence of vancomycin resistance clusters')."},
        ],
        "res_drug": "Non-van ligases that synthesize D-Ala-D-Ala, the default cell wall precursor that makes a cell vulnerable to glycopeptide antibiotics. Mutations in the ddl gene can cause the production of nonfunctional/inactivated D-Ala-D-Ala ligases, which can render bacteria glycopeptide dependent depending on the presence of vancomycin resistance clusters.",
        "note": ("The enzyme whose product makes the cell susceptible. NOT asserted: that "
                 "losing it confers resistance outright -- CARD says nonfunctional ddl can "
                 "render bacteria glycopeptide DEPENDENT, conditional on a van cluster "
                 "being present, which is a different phenotype from resistance."),
        "extra_nodes": [
            {"node_id": "dala_dala_synthesis", "label": "D-Ala-D-Ala ligase activity",
             "node_type": "MOLECULAR_FUNCTION",
             "description": "Ungrounded: not looked up rather than guessed (rounds 56-89)."},
            {"node_id": "susceptible_precursor", "label": "D-Ala-D-Ala, the precursor glycopeptides bind",
             "node_type": "CHEMICAL",
             "description": "The VULNERABILITY, not the resistance. Ungrounded: rounds 20-23 recorded the same CHEBI gap for UDP-MurNAc peptides."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "dala_dala_synthesis",
             "predicate": "enables (D-Ala-D-Ala synthesis)", "predicate_id": "RO:0002327",
             "evidence": [{"reference": "ARO:3003970", "snippet": "Non-van ligases that synthesize D-Ala-D-Ala, the default cell wall precursor that makes a cell vulnerable to glycopeptide antibiotics. Mutations in the ddl gene can cause the production of nonfunctional/inactivated D-Ala-D-Ala ligases, which can render bacteria glycopeptide dependent depending on the presence of vancomycin resistance clusters.",
                           "notes": "'Non-van ligases that synthesize D-Ala-D-Ala'."}]},
            {"subject": "dala_dala_synthesis", "object": "susceptible_precursor",
             "predicate": "has output (the susceptible precursor)", "predicate_id": "RO:0002234",
             "description": "The inversion that makes this family unlike every other van record: the product is what the drug binds, so making it is what makes the cell vulnerable.",
             "evidence": [{"reference": "ARO:3003970", "snippet": "Non-van ligases that synthesize D-Ala-D-Ala, the default cell wall precursor that makes a cell vulnerable to glycopeptide antibiotics. Mutations in the ddl gene can cause the production of nonfunctional/inactivated D-Ala-D-Ala ligases, which can render bacteria glycopeptide dependent depending on the presence of vancomycin resistance clusters.",
                           "notes": "'the default cell wall precursor that makes a cell VULNERABLE to glycopeptide antibiotics'."}]},
            {"subject": "susceptible_precursor", "object": "drug0",
             "predicate": "molecularly interacts with (the drug binds this precursor)",
             "predicate_id": "RO:0002436",
             "evidence": [{"reference": "ARO:3003970", "snippet": "Non-van ligases that synthesize D-Ala-D-Ala, the default cell wall precursor that makes a cell vulnerable to glycopeptide antibiotics. Mutations in the ddl gene can cause the production of nonfunctional/inactivated D-Ala-D-Ala ligases, which can render bacteria glycopeptide dependent depending on the presence of vancomycin resistance clusters.",
                           "notes": "Implied by 'makes a cell vulnerable to glycopeptide antibiotics' plus rounds 20-21's curated D-Ala-D-Ala binding; CARD does not write the binding step here."}]},
        ],
    },
    # vanJ homologues (ARO:3004255) -- the mechanism is on ARO:3002914, and this record
    # names it. Round 22's cross-record citation: point at the curated record rather than
    # copy its chemistry, so this inherits whatever ARO:3002914 says today.
    #
    # This is the ONE case in the van remainder where a bare resistance claim can be
    # honestly extended, because the record's own definition names the protein whose
    # mechanism is curated. The two remaining family terms (ARO:3002976, ARO:3000234) say
    # only that van genes confer resistance, and stay drafts.
    "ARO:3004255": {
        "curated": "2026-08-07T00:00:00Z",
        # Must NOT match vanJ itself. ARO:3002914 is a descendant of this family term and
        # its own definition contains "vanJ", so the first version gave vanJ a
        # "shares ancestor with vanJ" edge pointing at its own record. A homology edge to
        # oneself is not a weaker claim, it is a meaningless one.
        "precondition": _requires_vanj_homologue,
        "reference": "ARO:3004255",
        "mech": {"ARO:3000213": "vanJ and vanJ homologue proteins confer resistance to teicoplanin."},
        "mech_res": "vanJ and vanJ homologue proteins confer resistance to teicoplanin.",
        "det_res": [
            {"reference": "ARO:3004255", "snippet": "vanJ and vanJ homologue proteins confer resistance to teicoplanin.",
             "notes": "The whole claim: vanJ AND its homologues confer teicoplanin resistance. No mechanism of its own."},
            {"reference": "ARO:3002914", "snippet": "vanJ is a novel membrane protein that confers resistance to teicoplanin and its derivatives in Streptomyces coelicolor by recycling undecaprenol pyrophosphate during cell wall biosynthesis.",
             "notes": "The mechanism, cited FROM vanJ's record because this definition names vanJ. NOT asserted: that every homologue recycles undecaprenol pyrophosphate -- CARD groups them by resistance phenotype, not by demonstrated mechanism."},
        ],
        "res_drug": "vanJ and vanJ homologue proteins confer resistance to teicoplanin.",
        "note": ("A homologue group whose mechanism lives on ARO:3002914 (round 88). The "
                 "graph points at that record rather than copying its chemistry, so it "
                 "inherits whatever vanJ's record says today -- round 22's rule."),
        "extra_nodes": [
            {"node_id": "vanj_record", "label": "vanJ (undecaprenol pyrophosphate recycling)",
             "node_type": "PROTEIN", "grounding": "ARO:3002914",
             "description": "A KB record curated in round 88. Pointing at it rather than restating it is the whole point of this config."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "vanj_record",
             # RO:0002158 "shares ancestor with", NOT RO:0002159. The first version used
             # 0002159, which is "SERIALLY homologous to" -- a developmental term for
             # repeated structures within an organism (vertebrae), not sequence homology.
             # The OLS lookup returned no _embedded block and I nearly took that as
             # "unverifiable" rather than checking the search endpoint, which named it.
             "predicate": "shares ancestor with (vanJ homologue)",
             "predicate_id": "RO:0002158",
             "description": "Homology, NOT mechanism. CARD groups these by shared resistance phenotype and does not say every homologue performs vanJ's reaction.",
             "evidence": [{"reference": "ARO:3004255", "snippet": "vanJ and vanJ homologue proteins confer resistance to teicoplanin.",
                           "notes": "'vanJ and vanJ HOMOLOGUE proteins' -- the relationship CARD asserts is homology."}]},
        ],
    },
    # vanU (ARO:3000575) -- REGULATION. Round 22's shape: the graph ends at the resistance
    # genes rather than restating their chemistry, which rounds 20-23 already curated.
    "ARO:3000575": {
        "curated": "2026-08-07T00:00:00Z",
        "precondition": _requires_van_protein("ARO:3000213", "transcriptional activator", "transcriptional activation"),
        "reference": "ARO:3000575",
        "mech": {"ARO:3000213": "VanU is a transcriptional activator of vancomycin resistance genes."},
        "mech_res": "VanU is a transcriptional activator of vancomycin resistance genes.",
        "det_res": [
            {"reference": "ARO:3000575", "snippet": "VanU is a transcriptional activator of vancomycin resistance genes.",
             "notes": "The whole claim, with its direction: an ACTIVATOR of the resistance genes. VanU transports nothing and modifies no precursor."},
        ],
        "res_drug": "VanU is a transcriptional activator of vancomycin resistance genes.",
        "note": ("Transcriptional activation of the van genes. The graph ends at those "
                 "genes; their chemistry is curated on their own records (rounds 20-23)."),
        "extra_nodes": [
            {"node_id": "van_genes", "label": "vancomycin resistance genes",
             "node_type": "NUCLEIC_ACID",
             "description": "Where this graph stops. Ungrounded: 'the van genes' as a set is not one record, and pointing at one would pick a cluster arbitrarily."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "van_genes",
             "predicate": "positively regulates (activates transcription)",
             "predicate_id": "RO:0002213",
             "description": "The POSITIVE form, licensed by CARD's own word 'activator' -- as in round 79, and unlike round 78 where CARD gave no direction.",
             "evidence": [{"reference": "ARO:3000575", "snippet": "VanU is a transcriptional activator of vancomycin resistance genes.",
                           "notes": "'a transcriptional ACTIVATOR of vancomycin resistance genes'."}]},
        ],
    },
    # vanJ (ARO:3002914) -- undecaprenol pyrophosphate recycling, the SAME mechanism as
    # round 58's bacA/bcrC, arrived at from a completely different family. Worth noting:
    # a mechanism can recur across ARO families that share no ancestor.
    "ARO:3002914": {
        "curated": "2026-08-07T00:00:00Z",
        "precondition": _requires_van_protein("ARO:3000213", "recycling undecaprenol", "undecaprenol pyrophosphate recycling"),
        "reference": "ARO:3002914",
        "mech": {"ARO:3000213": "vanJ is a novel membrane protein that confers resistance to teicoplanin and its derivatives in Streptomyces coelicolor by recycling undecaprenol pyrophosphate during cell wall biosynthesis."},
        "mech_res": "vanJ is a novel membrane protein that confers resistance to teicoplanin and its derivatives in Streptomyces coelicolor by recycling undecaprenol pyrophosphate during cell wall biosynthesis.",
        "det_res": [
            {"reference": "ARO:3002914", "snippet": "vanJ is a novel membrane protein that confers resistance to teicoplanin and its derivatives in Streptomyces coelicolor by recycling undecaprenol pyrophosphate during cell wall biosynthesis.",
             "notes": "Mechanism, drug and organism in one sentence: resistance to teicoplanin 'by RECYCLING undecaprenol pyrophosphate during cell wall biosynthesis'. Same step as round 58's bacA/bcrC, in an unrelated family."},
        ],
        "res_drug": "vanJ is a novel membrane protein that confers resistance to teicoplanin and its derivatives in Streptomyces coelicolor by recycling undecaprenol pyrophosphate during cell wall biosynthesis.",
        "note": ("Undecaprenol pyrophosphate recycling -- round 58's bacA/bcrC mechanism "
                 "reached from the van set. As there, NOT asserted: that the drug binds "
                 "or sequesters the carrier, which CARD does not say."),
        "extra_nodes": [
            {"node_id": "upp_recycling", "label": "undecaprenol pyrophosphate recycling",
             "node_type": "MOLECULAR_FUNCTION",
             "description": "Ungrounded, as in round 58."},
            {"node_id": "wall", "label": "cell wall biosynthesis",
             "node_type": "BIOLOGICAL_PROCESS",
             "description": "The process the recycling serves. Ungrounded: no term verified this round."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "upp_recycling",
             "predicate": "enables (recycles the lipid carrier)", "predicate_id": "RO:0002327",
             "evidence": [{"reference": "ARO:3002914", "snippet": "vanJ is a novel membrane protein that confers resistance to teicoplanin and its derivatives in Streptomyces coelicolor by recycling undecaprenol pyrophosphate during cell wall biosynthesis.",
                           "notes": "'by recycling undecaprenol pyrophosphate'."}]},
            {"subject": "upp_recycling", "object": "wall",
             "predicate": "part of (cell wall biosynthesis)", "predicate_id": "BFO:0000050",
             "evidence": [{"reference": "ARO:3002914", "snippet": "vanJ is a novel membrane protein that confers resistance to teicoplanin and its derivatives in Streptomyces coelicolor by recycling undecaprenol pyrophosphate during cell wall biosynthesis.",
                           "notes": "'during cell wall biosynthesis'."}]},
        ],
    },
    # vanK (ARO:3002915) -- cross-bridge addition to the stem pentapeptide.
    "ARO:3002915": {
        "curated": "2026-08-07T00:00:00Z",
        "precondition": _requires_van_protein("ARO:3000213", "cross-bridge", "cross-bridge addition"),
        "reference": "ARO:3002915",
        "mech": {"ARO:3000213": "VanK is a member of the Fem family of enzymes that add the cross-bridge amino acids to the stem pentapeptide of cell wall precursors in Streptomyces coelicolor that confers inducible, high-level vancomycin resistance."},
        "mech_res": "VanK is a member of the Fem family of enzymes that add the cross-bridge amino acids to the stem pentapeptide of cell wall precursors in Streptomyces coelicolor that confers inducible, high-level vancomycin resistance.",
        "det_res": [
            {"reference": "ARO:3002915", "snippet": "VanK is a member of the Fem family of enzymes that add the cross-bridge amino acids to the stem pentapeptide of cell wall precursors in Streptomyces coelicolor that confers inducible, high-level vancomycin resistance.",
             "notes": "Enzyme family, reaction, substrate and phenotype: Fem-family, adds CROSS-BRIDGE amino acids to the stem pentapeptide, conferring 'inducible, high-level' vancomycin resistance."},
        ],
        "res_drug": "VanK is a member of the Fem family of enzymes that add the cross-bridge amino acids to the stem pentapeptide of cell wall precursors in Streptomyces coelicolor that confers inducible, high-level vancomycin resistance.",
        "note": ("Cross-bridge addition. NOT asserted: why a modified cross-bridge confers "
                 "vancomycin resistance -- CARD states the reaction and the phenotype and "
                 "nothing between them."),
        "extra_nodes": [
            {"node_id": "crossbridge_transfer", "label": "cross-bridge amino acid addition (Fem family)",
             "node_type": "MOLECULAR_FUNCTION",
             "description": "Ungrounded: not looked up rather than guessed."},
            {"node_id": "stem_pentapeptide", "label": "stem pentapeptide of cell wall precursors",
             "node_type": "CHEMICAL",
             "description": "The substrate. Ungrounded -- the same CHEBI gap rounds 20-23 recorded for UDP-MurNAc peptides."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "crossbridge_transfer",
             "predicate": "enables (cross-bridge addition)", "predicate_id": "RO:0002327",
             "evidence": [{"reference": "ARO:3002915", "snippet": "VanK is a member of the Fem family of enzymes that add the cross-bridge amino acids to the stem pentapeptide of cell wall precursors in Streptomyces coelicolor that confers inducible, high-level vancomycin resistance.",
                           "notes": "'a member of the Fem family of enzymes that add the cross-bridge amino acids'."}]},
            {"subject": "crossbridge_transfer", "object": "stem_pentapeptide",
             "predicate": "has input (the stem pentapeptide)", "predicate_id": "RO:0002233",
             "evidence": [{"reference": "ARO:3002915", "snippet": "VanK is a member of the Fem family of enzymes that add the cross-bridge amino acids to the stem pentapeptide of cell wall precursors in Streptomyces coelicolor that confers inducible, high-level vancomycin resistance.",
                           "notes": "'to the stem pentapeptide of cell wall precursors'. NOT asserted: how this confers resistance, which CARD does not say."}]},
        ],
    },
    # Van ligases (ARO:3002906) -- precursor substitution, stated in one sentence.
    # Round 21's vanH/vanA shape, arrived at from the ligase's own definition rather than
    # from the pathway papers.
    "ARO:3002906": {
        "curated": "2026-08-07T00:00:00Z",
        "precondition": _requires_van_protein("ARO:3000213", "alternative substrates", "alternative-precursor synthesis"),
        "reference": "ARO:3002906",
        "mech": {"ARO:3000213": "Van ligases synthesize alternative substrates for peptidoglycan synthesis that reduce vancomycin binding affinity."},
        "mech_res": "Van ligases synthesize alternative substrates for peptidoglycan synthesis that reduce vancomycin binding affinity.",
        "det_res": [
            {"reference": "ARO:3002906", "snippet": "Van ligases synthesize alternative substrates for peptidoglycan synthesis that reduce vancomycin binding affinity.",
             "notes": "Reaction and consequence in one sentence: alternative substrates for peptidoglycan synthesis that REDUCE vancomycin binding affinity."},
        ],
        "res_drug": "Van ligases synthesize alternative substrates for peptidoglycan synthesis that reduce vancomycin binding affinity.",
        "note": "Precursor substitution -- the target is rebuilt, not modified in place.",
        "extra_nodes": [
            {"node_id": "alt_precursor", "label": "alternative peptidoglycan precursor",
             "node_type": "CHEMICAL",
             "description": "Ungrounded: the UDP-MurNAc depsipeptides have no CHEBI term (rounds 20-21 noted the same gap)."},
            {"node_id": "low_affinity", "label": "reduced vancomycin binding affinity",
             "node_type": "STATE", "description": "The causal core, in CARD's own words."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "alt_precursor",
             "predicate": "enables (synthesis of the alternative substrate)",
             "predicate_id": "RO:0002327",
             "evidence": [{"reference": "ARO:3002906", "snippet": "Van ligases synthesize alternative substrates for peptidoglycan synthesis that reduce vancomycin binding affinity.",
                           "notes": "'Van ligases synthesize alternative substrates for peptidoglycan synthesis'."}]},
            {"subject": "alt_precursor", "object": "low_affinity",
             "predicate": "causally upstream of (reduces drug binding)",
             "predicate_id": "RO:0002411",
             "evidence": [{"reference": "ARO:3002906", "snippet": "Van ligases synthesize alternative substrates for peptidoglycan synthesis that reduce vancomycin binding affinity.",
                           "notes": "'that reduce vancomycin binding affinity'."}]},
        ],
    },
    # VanZ (ARO:3000116) -- an accessory protein with a stated, specific effect.
    "ARO:3000116": {
        "curated": "2026-08-07T00:00:00Z",
        "precondition": _requires_van_protein("ARO:3000213", "terminal d-ala", "D-Ala exclusion"),
        "reference": "ARO:3000116",
        "mech": {"ARO:3000213": "VanZ is a teicoplanin resistance gene that is an accessory protein. VanZ prevents the incorporation of the terminal D-Ala into peptidoglycan subunits."},
        "mech_res": "VanZ is a teicoplanin resistance gene that is an accessory protein. VanZ prevents the incorporation of the terminal D-Ala into peptidoglycan subunits.",
        "det_res": [
            {"reference": "ARO:3000116", "snippet": "VanZ is a teicoplanin resistance gene that is an accessory protein. VanZ prevents the incorporation of the terminal D-Ala into peptidoglycan subunits.",
             "notes": "An 'accessory protein' with a precise effect: it PREVENTS incorporation of the terminal D-Ala. CARD does not say how, and that step is not drawn."},
        ],
        "res_drug": "VanZ is a teicoplanin resistance gene that is an accessory protein. VanZ prevents the incorporation of the terminal D-Ala into peptidoglycan subunits.",
        "note": ("Exclusion of the terminal D-Ala. HOW VanZ prevents incorporation is not "
                 "stated by CARD and is not asserted; the link from a missing D-Ala to "
                 "teicoplanin resistance is likewise left to the ligase records."),
        "extra_nodes": [
            {"node_id": "terminal_dala", "label": "terminal D-Ala of the peptidoglycan subunit",
             "node_type": "CHEMICAL",
             "description": "What is excluded. Ungrounded: a residue position in a precursor, not a compound."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "terminal_dala",
             "predicate": "negatively regulates (prevents its incorporation)",
             "predicate_id": "RO:0002212",
             "description": "The one mechanistic claim CARD makes. NOT asserted: the mechanism by which it prevents incorporation, nor the link from that to teicoplanin binding.",
             "evidence": [{"reference": "ARO:3000116", "snippet": "VanZ is a teicoplanin resistance gene that is an accessory protein. VanZ prevents the incorporation of the terminal D-Ala into peptidoglycan subunits.",
                           "notes": "'VanZ prevents the incorporation of the terminal D-Ala into peptidoglycan subunits'."}]},
        ],
    },
    # Named efflux subunits (under ARO:3000748) -- the part of #229's family that does NOT
    # need the categorisation decision, because their own definitions say what they are.
    "ARO:3000748-subunit": {
        "curated": "2026-08-07T00:00:00Z",
        "precondition": _requires_named_efflux_subunit,
        "reference": "ARO:3000748",
        "mech": {"ARO:0010000": "Antibiotic resistance via the transport of antibiotics out of the cell."},
        "mech_res": "Antibiotic resistance via the transport of antibiotics out of the cell.",
        "det_res": [
            {"reference": "ARO:3000377", "snippet": "MexA is the membrane fusion protein of the MexAB-OprM multidrug efflux complex.",
             "notes": "A subunit describes its place in something larger -- 'the membrane fusion protein OF the MexAB-OprM complex'. That phrasing is what distinguishes these from the complexes filed alongside them (#229)."},
            {"reference": "ARO:3000378", "snippet": "MexB is the inner membrane multidrug exporter of the efflux complex MexAB-OprM.",
             "notes": "And the transporting subunit: 'the inner membrane multidrug exporter'. SCOPE: MexA and MexB are the only two records in this family whose definitions take this form."},
            {"reference": "ARO:3000806", "snippet": "MexG is a membrane protein required for MexGHI-OpmD efflux activity.",
             "notes": "The other subunit phrasing CARD uses: 'REQUIRED FOR MexGHI-OpmD efflux activity'. Round 86's pattern only matched 'is the <role> OF X' and missed this."},
            {"reference": "ARO:0010000", "snippet": "Antibiotic resistance via the transport of antibiotics out of the cell.",
             "notes": "What the complex they belong to achieves."},
        ],
        "res_drug": "Antibiotic resistance via the transport of antibiotics out of the cell.",
        "note": ("A named subunit of a named efflux complex. The graph routes through the "
                 "COMPLEX because no subunit effluxes anything alone -- and stops at the "
                 "efflux process, since the pump's energetics live on the pump records "
                 "(rounds 67, 69)."),
        "extra_nodes": [
            {"node_id": "complex", "label": "the efflux pump complex this subunit belongs to",
             "node_type": "PROTEIN",
             "description": "Ungrounded: the complex records exist but are themselves #229's open categorisation question, so this does not point at one."},
            {"node_id": "efflux_process", "label": "antibiotic efflux",
             "node_type": "BIOLOGICAL_PROCESS", "grounding": "ARO:0010000",
             "description": "Where this graph stops."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "complex",
             "predicate": "part of (the efflux complex)", "predicate_id": "BFO:0000050",
             "description": "The defining claim: a subunit is PART OF the transporter, not the transporter. Writing determinant --> efflux directly would make each subunit a pump.",
             "evidence": [
                 {"reference": "ARO:3000377", "snippet": "MexA is the membrane fusion protein of the MexAB-OprM multidrug efflux complex.",
                  "notes": "'the membrane fusion protein OF the MexAB-OprM multidrug efflux complex'."},
                 {"reference": "ARO:3000378", "snippet": "MexB is the inner membrane multidrug exporter of the efflux complex MexAB-OprM.",
                  "notes": "'the inner membrane multidrug exporter OF the efflux complex MexAB-OprM'."}]},
            {"subject": "complex", "object": "efflux_process",
             "predicate": "participates in (antibiotic efflux)", "predicate_id": "RO:0000056",
             "evidence": [{"reference": "ARO:3000378", "snippet": "MexB is the inner membrane multidrug exporter of the efflux complex MexAB-OprM.",
                           "notes": "'multidrug exporter' -- the complex is what transports."}]},
            {"subject": "efflux_process", "object": "resistance",
             "predicate": "causally upstream of (confers resistance)",
             "predicate_id": "RO:0002411",
             "evidence": [{"reference": "ARO:0010000", "snippet": "Antibiotic resistance via the transport of antibiotics out of the cell.",
                           "notes": "'via the transport of antibiotics out of the cell'."}]},
        ],
    },
    # Aminoglycoside-modifying enzymes (ARO:3007380) -- generic chemical modification.
    #
    # Round 68 curated the specific chemistries (nucleotidylation, phosphorylation,
    # acylation) under ARO:3000557. This family term names only "chemical modification",
    # so the graph is correspondingly general: no reaction node, because CARD does not say
    # which reaction, and the members here do not either.
    "ARO:3007380": {
        "curated": "2026-08-07T00:00:00Z",
        "precondition": _requires_amg_modifying,
        "reference": "ARO:3007380",
        "mech": {"ARO:0001004": "Resistance-conferring genetic elements encoding proteins involved in the enzymatic inactivation of aminoglycoside antibiotics through chemical modification."},
        "mech_res": "Resistance-conferring genetic elements encoding proteins involved in the enzymatic inactivation of aminoglycoside antibiotics through chemical modification.",
        "det_res": [
            {"reference": "ARO:3007380", "snippet": "Resistance-conferring genetic elements encoding proteins involved in the enzymatic inactivation of aminoglycoside antibiotics through chemical modification.",
             "notes": "The claim at the level CARD makes it: 'enzymatic inactivation … through chemical modification', with no reaction named. Round 68's three chemistries are curated separately under ARO:3000557."},
        ],
        "res_drug": "Resistance-conferring genetic elements encoding proteins involved in the enzymatic inactivation of aminoglycoside antibiotics through chemical modification.",
        "note": ("Inactivation by unspecified chemical modification. Deliberately no "
                 "reaction node: CARD names none here, and guessing one would import "
                 "round 68's chemistries onto records that do not claim them."),
        "extra_nodes": [
            {"node_id": "modification", "label": "enzymatic modification of the aminoglycoside",
             "node_type": "MOLECULAR_FUNCTION",
             "description": "Deliberately unspecific -- see the config note."},
            {"node_id": "inactivated", "label": "chemically modified, inactive aminoglycoside",
             "node_type": "STATE", "description": "The product state. Ungrounded."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "modification",
             "predicate": "enables (modifies the drug)", "predicate_id": "RO:0002327",
             "evidence": [{"reference": "ARO:3007380", "snippet": "Resistance-conferring genetic elements encoding proteins involved in the enzymatic inactivation of aminoglycoside antibiotics through chemical modification.",
                           "notes": "'proteins involved in the enzymatic inactivation … through chemical modification'."}]},
            {"subject": "modification", "object": "drug0",
             "predicate": "has input (the drug)", "predicate_id": "RO:0002233",
             "evidence": [{"reference": "ARO:3007380", "snippet": "Resistance-conferring genetic elements encoding proteins involved in the enzymatic inactivation of aminoglycoside antibiotics through chemical modification.",
                           "notes": "The antibiotic is the substrate -- inactivation, not target alteration."}]},
            {"subject": "modification", "object": "inactivated",
             "predicate": "causally upstream of (inactivates the drug)",
             "predicate_id": "RO:0002411",
             "evidence": [{"reference": "ARO:3007380", "snippet": "Resistance-conferring genetic elements encoding proteins involved in the enzymatic inactivation of aminoglycoside antibiotics through chemical modification.",
                           "notes": "'enzymatic inactivation of aminoglycoside antibiotics'."}]},
        ],
    },
    # Rv0678 (ARO:3007672) -- a REPRESSOR, so its mutation DEREPRESSES.
    #
    # The mirror of round 79's ARO:3000219, where mutations raise expression directly.
    # Here CARD states the repression ("NEGATIVELY regulates the expression of the
    # mmpS5/L5 efflux pump") but NOT that mutations relieve it. That step is the whole
    # reason these records confer resistance and it is not written down, so the graph
    # carries the repression and stops.
    "ARO:3007672": {
        "curated": "2026-08-07T00:00:00Z",
        "precondition": _requires_rv0678,
        "reference": "ARO:3007672",
        "mech": {"ARO:3000212": "Rv0678 encodes a transcription factor which negatively regulates the expression of the mmpS5/L5 efflux pump."},
        "mech_res": "Rv0678 encodes a transcription factor which negatively regulates the expression of the mmpS5/L5 efflux pump.",
        "det_res": [
            {"reference": "ARO:3007672", "snippet": "Rv0678 encodes a transcription factor which negatively regulates the expression of the mmpS5/L5 efflux pump.",
             "notes": "The repression, with its direction. CARD does NOT say that mutations relieve it -- the derepression step is the reason these records confer resistance and is nowhere stated."},
        ],
        "res_drug": "Antibiotic resistance via the transport of antibiotics out of the cell.",
        "note": ("Repression of an efflux pump. The DEREPRESSION step -- mutation relieves "
                 "repression, efflux rises -- is deliberately absent: CARD states the "
                 "repression and never states that mutations lift it."),
        "extra_nodes": [
            {"node_id": "pump_expression", "label": "expression of the mmpS5/L5 efflux pump",
             "node_type": "BIOLOGICAL_PROCESS",
             "description": "What Rv0678 represses. Ungrounded."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "pump_expression",
             "predicate": "negatively regulates (represses pump expression)",
             "predicate_id": "RO:0002212",
             "description": "The NEGATIVE form, licensed by CARD's own 'negatively regulates' -- the mirror of round 79's positive edge, where mutations raise expression directly.",
             "evidence": [{"reference": "ARO:3007672", "snippet": "Rv0678 encodes a transcription factor which negatively regulates the expression of the mmpS5/L5 efflux pump.",
                           "notes": "'a transcription factor which negatively regulates the expression of the mmpS5/L5 efflux pump'. NOT asserted: that mutation relieves this repression."}]},
        ],
    },
    # murA (ARO:3002811) -- target OVEREXPRESSION, distinct from target alteration.
    #
    # Rounds 53, 61, 80 and 82 all curated mutations that change the TARGET so the drug
    # binds it less. This one does not: CARD says "OVEREXPRESSION of murA through
    # mutations confers fosfomycin resistance". The enzyme is unchanged and there is
    # simply more of it than the drug can inhibit -- so no affinity node appears, and a
    # test enforces that.
    "ARO:3002811": {
        "curated": "2026-08-07T00:00:00Z",
        "precondition": _requires_mura,
        "reference": "ARO:3002811",
        "mech": {"ARO:3000212": "murA or UDP-N-acetylglucosamine enolpyruvyl transferase catalyses the initial step in peptidoglycan biosynthesis and is inhibited by fosfomycin. Overexpression of murA through mutations confers fosfomycin resistance."},
        "mech_res": "murA or UDP-N-acetylglucosamine enolpyruvyl transferase catalyses the initial step in peptidoglycan biosynthesis and is inhibited by fosfomycin. Overexpression of murA through mutations confers fosfomycin resistance.",
        "det_res": [
            {"reference": "ARO:3002811", "snippet": "murA or UDP-N-acetylglucosamine enolpyruvyl transferase catalyses the initial step in peptidoglycan biosynthesis and is inhibited by fosfomycin. Overexpression of murA through mutations confers fosfomycin resistance.",
             "notes": "Enzyme, pathway step, drug action and mechanism in two sentences -- and the mechanism is OVEREXPRESSION, not altered binding."},
        ],
        "res_drug": "murA or UDP-N-acetylglucosamine enolpyruvyl transferase catalyses the initial step in peptidoglycan biosynthesis and is inhibited by fosfomycin. Overexpression of murA through mutations confers fosfomycin resistance.",
        "note": ("Target overexpression. The enzyme itself is not changed; there is more "
                 "of it than fosfomycin can inhibit. No affinity node, deliberately."),
        "extra_nodes": [
            {"node_id": "enolpyruvyl_transfer", "label": "UDP-N-acetylglucosamine enolpyruvyl transferase activity",
             "node_type": "MOLECULAR_FUNCTION",
             "description": "Ungrounded: not looked up rather than guessed (rounds 56-83)."},
            {"node_id": "pg_synthesis", "label": "peptidoglycan biosynthesis (initial step)",
             "node_type": "BIOLOGICAL_PROCESS",
             "description": "The pathway the drug blocks. Ungrounded: the general process has a GO term, this specific first step was not verified."},
            {"node_id": "overexpression", "label": "elevated murA levels",
             "node_type": "STATE",
             "description": "The causal core. NOT an affinity change -- see the config note."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "enolpyruvyl_transfer",
             "predicate": "enables (enolpyruvyl transfer)", "predicate_id": "RO:0002327",
             "evidence": [{"reference": "ARO:3002811", "snippet": "murA or UDP-N-acetylglucosamine enolpyruvyl transferase catalyses the initial step in peptidoglycan biosynthesis and is inhibited by fosfomycin. Overexpression of murA through mutations confers fosfomycin resistance.",
                           "notes": "'murA or UDP-N-acetylglucosamine enolpyruvyl transferase'."}]},
            {"subject": "enolpyruvyl_transfer", "object": "pg_synthesis",
             "predicate": "part of (the initial step of peptidoglycan biosynthesis)",
             "predicate_id": "BFO:0000050",
             "evidence": [{"reference": "ARO:3002811", "snippet": "murA or UDP-N-acetylglucosamine enolpyruvyl transferase catalyses the initial step in peptidoglycan biosynthesis and is inhibited by fosfomycin. Overexpression of murA through mutations confers fosfomycin resistance.",
                           "notes": "'catalyses the initial step in peptidoglycan biosynthesis'."}]},
            {"subject": "drug0", "object": "enolpyruvyl_transfer",
             "predicate": "negatively regulates (inhibits the transferase)",
             "predicate_id": "RO:0002212",
             "evidence": [{"reference": "ARO:3002811", "snippet": "murA or UDP-N-acetylglucosamine enolpyruvyl transferase catalyses the initial step in peptidoglycan biosynthesis and is inhibited by fosfomycin. Overexpression of murA through mutations confers fosfomycin resistance.",
                           "notes": "'is inhibited by fosfomycin'."}]},
            {"subject": "determinant", "object": "overexpression",
             "predicate": "has quality (elevated expression)", "predicate_id": "RO:0000086",
             "evidence": [{"reference": "ARO:3002811", "snippet": "murA or UDP-N-acetylglucosamine enolpyruvyl transferase catalyses the initial step in peptidoglycan biosynthesis and is inhibited by fosfomycin. Overexpression of murA through mutations confers fosfomycin resistance.",
                           "notes": "'OVEREXPRESSION of murA through mutations' -- the mutation raises the amount, it does not change the enzyme's affinity."}]},
            {"subject": "overexpression", "object": "pg_synthesis",
             "predicate": "causally upstream of (wall synthesis continues under drug)",
             "predicate_id": "RO:0002411",
             "description": "Why more enzyme is resistance: enough escapes inhibition to keep the pathway running.",
             "evidence": [{"reference": "ARO:3002811", "snippet": "murA or UDP-N-acetylglucosamine enolpyruvyl transferase catalyses the initial step in peptidoglycan biosynthesis and is inhibited by fosfomycin. Overexpression of murA through mutations confers fosfomycin resistance.",
                           "notes": "'confers fosfomycin resistance'. NOTE: that enough escapes inhibition is the reading CARD implies, not a sentence it writes."}]},
        ],
    },
    # rpoC (ARO:3003289) -- role and resistance stated, mechanism ABSENT.
    #
    # Round 81's ppsA-E shape. CARD describes what the beta prime subunit does -- "forms
    # the active center of the enzyme and template/transcript binding sites" -- and says
    # "Mutations in rpoC gene confers antibiotic resistance", with nothing between. It
    # never says a drug binds there, nor what the mutations change. Rifampicin binds rpoB,
    # not rpoC, so the obvious guess would also be the wrong one.
    "ARO:3003289": {
        "curated": "2026-08-07T00:00:00Z",
        "precondition": _requires_rpoc,
        "reference": "ARO:3003289",
        "mech": {"ARO:3000212": "RNA polymerase is a multisubunit enzyme that is necessary for transcription. The beta prime subunit of RNA polymerase forms the active center of the enzyme and template/transcript binding sites. Mutations in rpoC gene confers antibiotic resistance."},
        "mech_res": "RNA polymerase is a multisubunit enzyme that is necessary for transcription. The beta prime subunit of RNA polymerase forms the active center of the enzyme and template/transcript binding sites. Mutations in rpoC gene confers antibiotic resistance.",
        "det_res": [
            {"reference": "ARO:3003289", "snippet": "RNA polymerase is a multisubunit enzyme that is necessary for transcription. The beta prime subunit of RNA polymerase forms the active center of the enzyme and template/transcript binding sites. Mutations in rpoC gene confers antibiotic resistance.",
             "notes": "Role and resistance, with no mechanism between them. CARD does not say what a drug does to rpoC or what the mutations change -- and rifampicin binds rpoB, so the obvious guess is not even the right one."},
        ],
        "res_drug": "RNA polymerase is a multisubunit enzyme that is necessary for transcription. The beta prime subunit of RNA polymerase forms the active center of the enzyme and template/transcript binding sites. Mutations in rpoC gene confers antibiotic resistance.",
        "note": ("Mechanism deliberately NOT asserted. CARD gives the subunit's structural "
                 "role and a bare resistance claim; nothing connects them. Round 66's EF-Tu "
                 "and round 81's ppsA-E position."),
        "extra_nodes": [
            {"node_id": "transcription", "label": "transcription", "node_type": "BIOLOGICAL_PROCESS",
             "description": "Ungrounded: not looked up rather than guessed (rounds 56-82)."},
            {"node_id": "active_center", "label": "RNA polymerase active center and template/transcript binding sites",
             "node_type": "PROTEIN",
             "description": "What the beta prime subunit forms. Ungrounded."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "active_center",
             "predicate": "part of (the polymerase active center)", "predicate_id": "BFO:0000050",
             "evidence": [{"reference": "ARO:3003289", "snippet": "RNA polymerase is a multisubunit enzyme that is necessary for transcription. The beta prime subunit of RNA polymerase forms the active center of the enzyme and template/transcript binding sites. Mutations in rpoC gene confers antibiotic resistance.",
                           "notes": "'The beta prime subunit … forms the active center of the enzyme and template/transcript binding sites'."}]},
            {"subject": "active_center", "object": "transcription",
             "predicate": "part of (transcription)", "predicate_id": "BFO:0000050",
             "evidence": [{"reference": "ARO:3003289", "snippet": "RNA polymerase is a multisubunit enzyme that is necessary for transcription. The beta prime subunit of RNA polymerase forms the active center of the enzyme and template/transcript binding sites. Mutations in rpoC gene confers antibiotic resistance.",
                           "notes": "'RNA polymerase … is necessary for transcription'. NOT asserted: any drug interaction with this centre, which CARD does not describe."}]},
        ],
    },
    # liaFSR (ARO:3003279) -- envelope stress regulation, drug as the INDUCING signal.
    "ARO:3003279": {
        "curated": "2026-08-07T00:00:00Z",
        "precondition": _requires_liafsr,
        "reference": "ARO:3003279",
        "mech": {"ARO:3000212": "The liaFSR system regulates the cell envelope stress response. It is transcriptionally activated by exposure to alkaline shock, detergents, and particularly antibiotics with lipid II inhibition properties."},
        "mech_res": "The liaFSR system regulates the cell envelope stress response. It is transcriptionally activated by exposure to alkaline shock, detergents, and particularly antibiotics with lipid II inhibition properties.",
        "det_res": [
            {"reference": "ARO:3003279", "snippet": "The liaFSR system regulates the cell envelope stress response. It is transcriptionally activated by exposure to alkaline shock, detergents, and particularly antibiotics with lipid II inhibition properties.",
             "notes": "What the system regulates, and what induces it -- 'particularly antibiotics with lipid II inhibition properties'. CARD does NOT say how the stress response then confers resistance."},
        ],
        "res_drug": "The liaFSR system regulates the cell envelope stress response. It is transcriptionally activated by exposure to alkaline shock, detergents, and particularly antibiotics with lipid II inhibition properties.",
        "note": ("Regulation of the envelope stress response. The drug is the INDUCER, as "
                 "with cprRS (round 76). How the response confers resistance is not stated "
                 "and is not drawn."),
        "extra_nodes": [
            {"node_id": "lipid_ii_stress", "label": "envelope stress from lipid II-inhibiting antibiotics",
             "node_type": "STATE", "description": "The inducing signal. Ungrounded."},
            {"node_id": "stress_response", "label": "cell envelope stress response",
             "node_type": "BIOLOGICAL_PROCESS",
             "description": "What the system regulates. Ungrounded: no term verified this round."},
        ],
        "extra_edges": [
            {"subject": "drug0", "object": "lipid_ii_stress",
             "predicate": "causally upstream of (creates envelope stress)",
             "predicate_id": "RO:0002411",
             "description": "The drug is the inducing signal, not the thing resisted at this step -- the same inversion as cprRS in round 76.",
             "evidence": [{"reference": "ARO:3003279", "snippet": "The liaFSR system regulates the cell envelope stress response. It is transcriptionally activated by exposure to alkaline shock, detergents, and particularly antibiotics with lipid II inhibition properties.",
                           "notes": "'transcriptionally activated by exposure to … particularly antibiotics with lipid II inhibition properties'."}]},
            {"subject": "lipid_ii_stress", "object": "determinant",
             "predicate": "causally upstream of (activates the liaFSR system)",
             "predicate_id": "RO:0002411",
             "evidence": [{"reference": "ARO:3003279", "snippet": "The liaFSR system regulates the cell envelope stress response. It is transcriptionally activated by exposure to alkaline shock, detergents, and particularly antibiotics with lipid II inhibition properties.",
                           "notes": "'It is transcriptionally activated by exposure to…'."}]},
            {"subject": "determinant", "object": "stress_response",
             "predicate": "regulates (the cell envelope stress response)",
             "predicate_id": "RO:0002211",
             "description": "Where this graph stops. CARD says the system REGULATES the response and never says how the response confers resistance.",
             "evidence": [{"reference": "ARO:3003279", "snippet": "The liaFSR system regulates the cell envelope stress response. It is transcriptionally activated by exposure to alkaline shock, detergents, and particularly antibiotics with lipid II inhibition properties.",
                           "notes": "'The liaFSR system regulates the cell envelope stress response'. Neutral predicate: CARD gives no direction."}]},
        ],
    },
    # folP dihydropteroate synthase (ARO:3000226) -- the most completely stated target
    # alteration in this corpus. CARD gives enzyme, pathway, drug action, mutation effect
    # and resistance in ONE sentence, and a second record adds that the inhibition is
    # COMPETITIVE and that the mutation lowers drug AFFINITY.
    #
    # Competitive inhibition is why this is not round 80's embB shape repeated: the drug is
    # a substrate analogue, so "lowered affinity for the drug" and "still binds its real
    # substrate" are the same claim seen from two sides. The graph says so explicitly.
    "ARO:3000226": {
        "curated": "2026-08-07T00:00:00Z",
        "precondition": _requires_folp,
        "reference": "ARO:3000226",
        "mech": {"ARO:3000212": "Point mutations in dihydropteroate synthase folP prevent sulfonamide antibiotics from inhibiting its role in folate synthesis, thus conferring sulfonamide resistance."},
        "mech_res": "Point mutations in dihydropteroate synthase folP prevent sulfonamide antibiotics from inhibiting its role in folate synthesis, thus conferring sulfonamide resistance.",
        "det_res": [
            {"reference": "ARO:3000226", "snippet": "Point mutations in dihydropteroate synthase folP prevent sulfonamide antibiotics from inhibiting its role in folate synthesis, thus conferring sulfonamide resistance.",
             "notes": "The whole chain in one sentence: mutations PREVENT sulfonamides from inhibiting folP's role in folate synthesis, THUS conferring resistance."},
            {"reference": "ARO:3003388", "snippet": "Dapsone inhibits bacterial synthesis of dihydrofolic acid by competing with with para-aminobenzoate for the active site of dihydropteroate synthetase. Thus acts as a competitive inhibitor of folP. Point mutation within the folP gene results in lowered affinity of dapsone for folP.",
             "notes": "And the kind of inhibition: COMPETITIVE, with para-aminobenzoate, plus the mutation's measured effect -- 'lowered affinity of dapsone for folP'. SCOPE: dapsone's sentence; the family term speaks of sulfonamides generally."},
        ],
        "res_drug": "Point mutations in dihydropteroate synthase folP prevent sulfonamide antibiotics from inhibiting its role in folate synthesis, thus conferring sulfonamide resistance.",
        "note": "Target alteration by lowered drug affinity at a competitive-inhibitor site.",
        "extra_nodes": [
            {"node_id": "dhps_activity", "label": "dihydropteroate synthase activity",
             "node_type": "MOLECULAR_FUNCTION",
             "description": "Ungrounded: not looked up rather than guessed (rounds 56-81)."},
            {"node_id": "folate_synthesis", "label": "folate synthesis",
             "node_type": "BIOLOGICAL_PROCESS",
             "description": "The pathway the drug blocks. Ungrounded: no term verified this round."},
            {"node_id": "low_affinity", "label": "lowered affinity of the drug for the mutant enzyme",
             "node_type": "STATE",
             "description": "The causal core, and measured for dapsone specifically."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "dhps_activity",
             "predicate": "enables (dihydropteroate synthesis)", "predicate_id": "RO:0002327",
             "evidence": [{"reference": "ARO:3000226", "snippet": "Point mutations in dihydropteroate synthase folP prevent sulfonamide antibiotics from inhibiting its role in folate synthesis, thus conferring sulfonamide resistance.",
                           "notes": "folP IS the dihydropteroate synthase."}]},
            {"subject": "dhps_activity", "object": "folate_synthesis",
             "predicate": "part of (folate synthesis)", "predicate_id": "BFO:0000050",
             "evidence": [{"reference": "ARO:3000226", "snippet": "Point mutations in dihydropteroate synthase folP prevent sulfonamide antibiotics from inhibiting its role in folate synthesis, thus conferring sulfonamide resistance.",
                           "notes": "'its role in folate synthesis'."}]},
            {"subject": "drug0", "object": "dhps_activity",
             "predicate": "negatively regulates (competitive inhibition at the PABA site)",
             "predicate_id": "RO:0002212",
             "description": "COMPETITIVE, not allosteric: the drug is a para-aminobenzoate analogue occupying the substrate's own site. That is why a mutation can lower drug affinity without abolishing catalysis.",
             "evidence": [{"reference": "ARO:3003388", "snippet": "Dapsone inhibits bacterial synthesis of dihydrofolic acid by competing with with para-aminobenzoate for the active site of dihydropteroate synthetase. Thus acts as a competitive inhibitor of folP. Point mutation within the folP gene results in lowered affinity of dapsone for folP.",
                           "notes": "'competing with para-aminobenzoate for the active site … Thus acts as a competitive inhibitor of folP'."}]},
            {"subject": "determinant", "object": "low_affinity",
             "predicate": "has quality (lowered drug affinity)", "predicate_id": "RO:0000086",
             "evidence": [{"reference": "ARO:3003388", "snippet": "Dapsone inhibits bacterial synthesis of dihydrofolic acid by competing with with para-aminobenzoate for the active site of dihydropteroate synthetase. Thus acts as a competitive inhibitor of folP. Point mutation within the folP gene results in lowered affinity of dapsone for folP.",
                           "notes": "'Point mutation within the folP gene results in lowered affinity of dapsone for folP'."}]},
            {"subject": "low_affinity", "object": "dhps_activity",
             "predicate": "causally upstream of (the enzyme keeps working under drug)",
             "predicate_id": "RO:0002411",
             "description": "The point of the whole mechanism: folate synthesis continues.",
             "evidence": [{"reference": "ARO:3000226", "snippet": "Point mutations in dihydropteroate synthase folP prevent sulfonamide antibiotics from inhibiting its role in folate synthesis, thus conferring sulfonamide resistance.",
                           "notes": "'prevent sulfonamide antibiotics from inhibiting its role in folate synthesis'."}]},
        ],
    },
    # ppsA-E polyketide synthases (ARO:3005002) -- resistance claim WITHOUT a mechanism.
    #
    # Round 66's EF-Tu shape. CARD says these enzymes make phthiocerol dimycocerosate and
    # that mutations "CAN RESULT IN" pyrazinamide resistance -- and never says how a lipid
    # biosynthesis defect confers resistance to a prodrug activated by pncA (round 56).
    # The connection is real in the literature and absent here, so it is not drawn.
    #
    # Note the family term describes an OPERON ("Genes ppsA-E constitute an operon") while
    # the records are individual proteins. The operon is cited as the source of the
    # biosynthetic claim, not modelled -- the same position round 74 took with almEFG.
    "ARO:3005002": {
        "curated": "2026-08-07T00:00:00Z",
        "precondition": _requires_pps_polyketide,
        "reference": "ARO:3005002",
        "mech": {"ARO:3000212": "Genes ppsA-E constitute an operon encoding enzymes involved in the biosynthesis of phthiocerol dimycocerosate and other lipids in Mycobacterium tuberculosis. Mutations within this region can result in resistance to pyrazinamide."},
        "mech_res": "Genes ppsA-E constitute an operon encoding enzymes involved in the biosynthesis of phthiocerol dimycocerosate and other lipids in Mycobacterium tuberculosis. Mutations within this region can result in resistance to pyrazinamide.",
        "det_res": [
            {"reference": "ARO:3005002", "snippet": "Genes ppsA-E constitute an operon encoding enzymes involved in the biosynthesis of phthiocerol dimycocerosate and other lipids in Mycobacterium tuberculosis. Mutations within this region can result in resistance to pyrazinamide.",
             "notes": "Both claims and the gap between them: what these enzymes DO (phthiocerol dimycocerosate biosynthesis) and that mutations 'CAN RESULT IN' resistance to pyrazinamide. CARD never links the two, and the hedge is its own."},
        ],
        "res_drug": "Genes ppsA-E constitute an operon encoding enzymes involved in the biosynthesis of phthiocerol dimycocerosate and other lipids in Mycobacterium tuberculosis. Mutations within this region can result in resistance to pyrazinamide.",
        "note": ("Resistance mechanism deliberately NOT asserted. CARD gives the enzymes' "
                 "biosynthetic role and a hedged resistance claim ('can result in') with "
                 "nothing between them. How a phthiocerol dimycocerosate defect confers "
                 "pyrazinamide resistance is real elsewhere and uncited here -- round 66's "
                 "EF-Tu position, and #219's lesson about sourcing mechanisms I know."),
        "extra_nodes": [
            {"node_id": "pdim_synthesis", "label": "phthiocerol dimycocerosate biosynthesis",
             "node_type": "BIOLOGICAL_PROCESS",
             "description": "Ungrounded: not looked up rather than guessed (rounds 56-80)."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "pdim_synthesis",
             "predicate": "participates in (phthiocerol dimycocerosate biosynthesis)",
             "predicate_id": "RO:0000056",
             "description": "'Participates in', matching CARD's 'enzymes INVOLVED IN' and because ppsA-E are five enzymes of one pathway -- no single record performs it.",
             "evidence": [{"reference": "ARO:3005002", "snippet": "Genes ppsA-E constitute an operon encoding enzymes involved in the biosynthesis of phthiocerol dimycocerosate and other lipids in Mycobacterium tuberculosis. Mutations within this region can result in resistance to pyrazinamide.",
                           "notes": "'enzymes involved in the biosynthesis of phthiocerol dimycocerosate'. NOT asserted: any link between this pathway and pyrazinamide, which CARD does not draw."}]},
        ],
    },
    # emb arabinosyltransferases (ARO:3005005) -- target alteration, with the drug's own
    # target named by the record. Rounds 18-19, 53 and 61 curated target alteration where
    # the drug binds a nucleic acid or a wall-building enzyme; here CARD spells out the
    # pathway the enzyme serves AND that ethambutol inhibits it, so the graph has a real
    # process at the end rather than a bare "resistance".
    "ARO:3005005": {
        "curated": "2026-08-07T00:00:00Z",
        "precondition": _requires_emb_arabinosyltransferase,
        "reference": "ARO:3005005",
        "mech": {"ARO:3000212": "Known antibiotic-resistant variants of emb arabinosyltransferases, primarily in Mycobacterium and conferring resistance to ethambutol through point mutation."},
        "mech_res": "Known antibiotic-resistant variants of emb arabinosyltransferases, primarily in Mycobacterium and conferring resistance to ethambutol through point mutation.",
        "det_res": [
            {"reference": "ARO:3005005", "snippet": "Known antibiotic-resistant variants of emb arabinosyltransferases, primarily in Mycobacterium and conferring resistance to ethambutol through point mutation.",
             "notes": "The family claim: resistance to ethambutol through point mutation."},
            {"reference": "ARO:3000235", "snippet": "embB gene encodes for an arabinosyl transferase in the arabinogalactan synthesis pathway. It is inhibited by ethambutol. Mutations within the ERDR region of embB confers resistance to ethambutol.",
             "notes": "And the mechanism it leaves out: what the enzyme does, that ethambutol inhibits it, and where the mutations sit. SCOPE: embB's sentence -- embA and embC are the same enzyme family but their own definitions do not repeat the pathway."},
        ],
        "res_drug": "embB gene encodes for an arabinosyl transferase in the arabinogalactan synthesis pathway. It is inhibited by ethambutol. Mutations within the ERDR region of embB confers resistance to ethambutol.",
        "note": "Target alteration of the drug's own enzyme; the ERDR region is named by embB's definition but not by the family term, so it is not asserted family-wide.",
        "extra_nodes": [
            {"node_id": "arabinosyl_transfer", "label": "arabinosyl transferase activity",
             "node_type": "MOLECULAR_FUNCTION",
             "description": "Ungrounded: not looked up rather than guessed (rounds 56-79)."},
            {"node_id": "arabinogalactan", "label": "arabinogalactan synthesis pathway",
             "node_type": "PATHWAY",
             "description": "The cell-wall pathway the enzyme serves. Ungrounded: no term verified this round."},
            {"node_id": "inhibition", "label": "ethambutol inhibition of the transferase",
             "node_type": "STATE",
             "description": "What the mutation prevents. Ungrounded."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "arabinosyl_transfer",
             "predicate": "enables (arabinosyl transfer)", "predicate_id": "RO:0002327",
             "evidence": [{"reference": "ARO:3000235", "snippet": "embB gene encodes for an arabinosyl transferase in the arabinogalactan synthesis pathway. It is inhibited by ethambutol. Mutations within the ERDR region of embB confers resistance to ethambutol.",
                           "notes": "'encodes for an arabinosyl transferase'."}]},
            {"subject": "arabinosyl_transfer", "object": "arabinogalactan",
             "predicate": "part of (arabinogalactan synthesis)", "predicate_id": "BFO:0000050",
             "evidence": [{"reference": "ARO:3000235", "snippet": "embB gene encodes for an arabinosyl transferase in the arabinogalactan synthesis pathway. It is inhibited by ethambutol. Mutations within the ERDR region of embB confers resistance to ethambutol.",
                           "notes": "'in the arabinogalactan synthesis pathway'."}]},
            {"subject": "drug0", "object": "inhibition",
             "predicate": "causally upstream of (inhibits the transferase)",
             "predicate_id": "RO:0002411",
             "description": "What the drug does to the unmutated enzyme, and therefore what resistance restores.",
             "evidence": [{"reference": "ARO:3000235", "snippet": "embB gene encodes for an arabinosyl transferase in the arabinogalactan synthesis pathway. It is inhibited by ethambutol. Mutations within the ERDR region of embB confers resistance to ethambutol.",
                           "notes": "'It is inhibited by ethambutol' -- stated outright, unlike fabG1 (#219) where the drug's action had to be sourced separately."}]},
            {"subject": "determinant", "object": "inhibition",
             "predicate": "negatively regulates (the mutant is no longer inhibited)",
             "predicate_id": "RO:0002212",
             "description": "The causal core.",
             "evidence": [{"reference": "ARO:3000235", "snippet": "embB gene encodes for an arabinosyl transferase in the arabinogalactan synthesis pathway. It is inhibited by ethambutol. Mutations within the ERDR region of embB confers resistance to ethambutol.",
                           "notes": "'Mutations within the ERDR region of embB confers resistance to ethambutol'."}]},
        ],
    },
    # Mutant efflux regulatory proteins (ARO:3000219) -- regulation, with a DIRECTION.
    "ARO:3000219": {
        "curated": "2026-08-07T00:00:00Z",
        "precondition": _requires_mutant_efflux_regulator,
        "reference": "ARO:3000219",
        "mech": {"ARO:3000212": "Efflux regulatory proteins with mutations that result in increased expression of efflux proteins.",
                 "ARO:0010000": "Efflux regulatory proteins with mutations that result in increased expression of efflux proteins."},
        "mech_res": "Efflux regulatory proteins with mutations that result in increased expression of efflux proteins.",
        "det_res": [
            {"reference": "ARO:3000219", "snippet": "Efflux regulatory proteins with mutations that result in increased expression of efflux proteins.",
             "notes": "The mechanism with its direction: mutations 'result in INCREASED expression of efflux proteins'. Contrast round 78's ARO:3000750, which says only 'directly or indirectly change rates' and therefore got a neutral predicate."},
            {"reference": "ARO:0010000", "snippet": "Antibiotic resistance via the transport of antibiotics out of the cell.",
             "notes": "What the raised efflux achieves. Cited so this graph can END at the process rather than restate any pump's chemistry."},
        ],
        "res_drug": "Antibiotic resistance via the transport of antibiotics out of the cell.",
        "note": ("Regulation, not efflux: these proteins transport nothing. The graph ends "
                 "at the efflux process. Uses the POSITIVE predicate because CARD states "
                 "the direction here, unlike ARO:3000750 (round 78)."),
        "extra_nodes": [
            {"node_id": "pump_expression", "label": "expression of efflux pump proteins",
             "node_type": "BIOLOGICAL_PROCESS",
             "description": "The regulated quantity. Ungrounded: 'expression of a particular pump set' has no term here."},
            {"node_id": "efflux_process", "label": "antibiotic efflux",
             "node_type": "BIOLOGICAL_PROCESS", "grounding": "ARO:0010000",
             "description": "Where this graph stops; pump chemistry lives on the pump records (rounds 67, 69)."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "pump_expression",
             "predicate": "positively regulates (mutation raises pump expression)",
             "predicate_id": "RO:0002213",
             "description": "The POSITIVE form, licensed by CARD stating the direction. Round 78's config deliberately used the neutral RO:0002211 because its family term did not.",
             "evidence": [{"reference": "ARO:3000219", "snippet": "Efflux regulatory proteins with mutations that result in increased expression of efflux proteins.",
                           "notes": "'mutations that RESULT IN INCREASED expression of efflux proteins'."}]},
            {"subject": "pump_expression", "object": "efflux_process",
             "predicate": "causally upstream of (more pump, more efflux)",
             "predicate_id": "RO:0002411",
             "evidence": [{"reference": "ARO:3000219", "snippet": "Efflux regulatory proteins with mutations that result in increased expression of efflux proteins.",
                           "notes": "The point of raising expression of EFFLUX proteins."}]},
            {"subject": "efflux_process", "object": "resistance",
             "predicate": "causally upstream of (confers resistance)",
             "predicate_id": "RO:0002411",
             "evidence": [{"reference": "ARO:0010000", "snippet": "Antibiotic resistance via the transport of antibiotics out of the cell.",
                           "notes": "'via the transport of antibiotics out of the cell'."}]},
        ],
    },
    # ---------------------------------------------------------------------------------
    # Two-component regulators of efflux (ARO:3000750) -- round 22's shape.
    #
    # These proteins transport nothing. Writing them as if they effluxed the drug would
    # be the ArmR/MecI/arlS error a sixth time. The graph ends at the efflux PROCESS, the
    # way round 22's vanR/vanS ended at vanH/vanX and round 76's cprRS ended at the Arn
    # records.
    #
    # CARD hedges the coupling: "DIRECTLY OR INDIRECTLY change rates of antibiotic
    # efflux". So the regulatory edge says "modulates" and its notes keep that hedge --
    # for kdpD, whose own definition is about potassium homeostasis, the connection to
    # efflux really is indirect, and a "positively regulates" edge would overstate it for
    # the whole family.
    "ARO:3000750": {
        "curated": "2026-08-07T00:00:00Z",
        "precondition": _requires_two_component_efflux,
        "reference": "ARO:3000750",
        "mech": {"ARO:0010000": "A protein, either a histidine kinase or a response regulator, that is part of a two-component regulatory system that directly or indirectly change rates of antibiotic efflux."},
        "mech_res": "A protein, either a histidine kinase or a response regulator, that is part of a two-component regulatory system that directly or indirectly change rates of antibiotic efflux.",
        "det_res": [
            {"reference": "ARO:3000750", "snippet": "A protein, either a histidine kinase or a response regulator, that is part of a two-component regulatory system that directly or indirectly change rates of antibiotic efflux.",
             "notes": "The family claim, with its hedge: these proteins 'directly or INDIRECTLY change rates of antibiotic efflux'. They do not efflux anything themselves."},
            {"reference": "ARO:0010000", "snippet": "Antibiotic resistance via the transport of antibiotics out of the cell.",
             "notes": "And what the efflux they modulate achieves -- cited so the graph can END here rather than restate any pump's chemistry."},
        ],
        "res_drug": "Antibiotic resistance via the transport of antibiotics out of the cell.",
        "note": ("Regulation of efflux, not efflux. The graph stops at the efflux process; "
                 "pump chemistry lives on the pump records (rounds 67, 69). The edge says "
                 "'modulates' because CARD says 'directly or indirectly'."),
        "extra_nodes": [
            {"node_id": "signalling", "label": "two-component signal transduction",
             "node_type": "BIOLOGICAL_PROCESS", "grounding": "GO:0000160",
             "description": "Checked non-obsolete against OLS (#157)."},
            {"node_id": "efflux_process", "label": "antibiotic efflux",
             "node_type": "BIOLOGICAL_PROCESS", "grounding": "ARO:0010000",
             "description": "Where this graph stops. The pumps' own mechanisms are curated on their records (SMR round 67, MATE round 69)."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "signalling",
             "predicate": "participates in (two-component signal transduction)",
             "predicate_id": "RO:0000056",
             "description": "'Participates in', not 'enables': each record is ONE half of a pair -- a sensor kinase or a response regulator -- and neither performs the transduction alone.",
             "evidence": [{"reference": "ARO:3000750", "snippet": "A protein, either a histidine kinase or a response regulator, that is part of a two-component regulatory system that directly or indirectly change rates of antibiotic efflux.",
                           "notes": "'either a histidine kinase or a response regulator, that is PART OF a two-component regulatory system'."}]},
            {"subject": "signalling", "object": "efflux_process",
             "predicate": "regulates (changes efflux rates, directly or indirectly)",
             "predicate_id": "RO:0002211",
             "description": "RO:0002211 'regulates', not the positive form: CARD says 'change rates', not 'increase' them, and 'directly or indirectly'. kdpD's own definition is about potassium homeostasis, so for at least one member the link really is indirect.",
             "evidence": [{"reference": "ARO:3000750", "snippet": "A protein, either a histidine kinase or a response regulator, that is part of a two-component regulatory system that directly or indirectly change rates of antibiotic efflux.",
                           "notes": "'directly or indirectly change rates of antibiotic efflux'."}]},
            {"subject": "efflux_process", "object": "resistance",
             "predicate": "causally upstream of (confers resistance)",
             "predicate_id": "RO:0002411",
             "evidence": [{"reference": "ARO:0010000", "snippet": "Antibiotic resistance via the transport of antibiotics out of the cell.",
                           "notes": "'via the transport of antibiotics out of the cell'."}]},
        ],
    },
    # ---------------------------------------------------------------------------------
    # Lpx lipid A biosynthesis mutations (ARO:3000012) -- NOT charge alteration.
    #
    # ARO:3003580's five routes (rounds 73-76) all MODIFY an intact lipid A to neutralise
    # its charge. These mutate its BIOSYNTHESIS, so the surface the peptide binds is
    # altered or absent rather than merely less negative. Same molecule, opposite
    # direction of intervention, and a reason not to reach for the charge snippets.
    #
    # CARD hedges twice in one sentence -- "widely known to be involved" and "may cause
    # resistance" -- so neither the enzyme's role nor the resistance is stated firmly, and
    # the notes say so rather than quoting past the hedge.
    "ARO:3000012": {
        "curated": "2026-08-07T00:00:00Z",
        "precondition": _requires_lpx,
        "reference": "ARO:3003573",
        # BOTH ids. These records carry ARO:3000212 (mutation) as well, and
        # UncoveredMechanism correctly refused them otherwise -- the seventh time this
        # session it has stopped a write. The same sentence genuinely serves both: it
        # names the biosynthetic role AND says "mutations to this gene may cause
        # resistance", so it is one claim covering two ids rather than a borrowed snippet.
        "mech": {"ARO:3000212": "The LpxA gene is widely known to be involved in the biosynthesis of lipid A in Gram-negative bacteria and mutations to this gene may cause resistance to antimicrobial peptides that target the outer membrane.",
                 "ARO:3000213": "The LpxA gene is widely known to be involved in the biosynthesis of lipid A in Gram-negative bacteria and mutations to this gene may cause resistance to antimicrobial peptides that target the outer membrane."},
        "mech_res": "The LpxA gene is widely known to be involved in the biosynthesis of lipid A in Gram-negative bacteria and mutations to this gene may cause resistance to antimicrobial peptides that target the outer membrane.",
        "det_res": [
            {"reference": "ARO:3003573", "snippet": "The LpxA gene is widely known to be involved in the biosynthesis of lipid A in Gram-negative bacteria and mutations to this gene may cause resistance to antimicrobial peptides that target the outer membrane.",
             "notes": "NOTE both hedges: 'widely known to be INVOLVED IN' the biosynthesis, and mutations 'MAY cause' resistance. Neither the role nor the resistance is stated firmly, so neither is upgraded here."},
            {"reference": "ARO:3000012", "snippet": "Proteins involved in restructuring of the cell wall, causing antibiotic resistance.",
             "notes": "The family claim, which IS causal ('causing antibiotic resistance') where the record-level sentence hedges."},
        ],
        "res_drug": "The LpxA gene is widely known to be involved in the biosynthesis of lipid A in Gram-negative bacteria and mutations to this gene may cause resistance to antimicrobial peptides that target the outer membrane.",
        "note": ("Lipid A biosynthesis disruption. NOT the charge-alteration mechanism of "
                 "ARO:3003580's five routes: those modify an intact lipid A, these change "
                 "whether it is made properly at all."),
        "extra_nodes": [
            {"node_id": "lipid_a_synthesis", "label": "lipid A biosynthesis",
             "node_type": "BIOLOGICAL_PROCESS",
             "description": "Ungrounded: not looked up rather than guessed (rounds 56-76)."},
            {"node_id": "altered_membrane", "label": "altered outer membrane targeted by the peptide",
             "node_type": "STATE",
             "description": "The causal core. Deliberately vague: CARD says the drug 'targets the outer membrane' and does not say what the mutation does to it."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "lipid_a_synthesis",
             "predicate": "participates in (lipid A biosynthesis)", "predicate_id": "RO:0000056",
             "description": "'Participates in', matching CARD's own 'involved in' -- LpxA/C/D are successive steps and the record does not claim any one performs the pathway.",
             "evidence": [{"reference": "ARO:3003573", "snippet": "The LpxA gene is widely known to be involved in the biosynthesis of lipid A in Gram-negative bacteria and mutations to this gene may cause resistance to antimicrobial peptides that target the outer membrane.",
                           "notes": "'involved in the biosynthesis of lipid A'."}]},
            {"subject": "lipid_a_synthesis", "object": "altered_membrane",
             "predicate": "causally upstream of (changes the membrane the drug targets)",
             "predicate_id": "RO:0002411",
             "evidence": [{"reference": "ARO:3003573", "snippet": "The LpxA gene is widely known to be involved in the biosynthesis of lipid A in Gram-negative bacteria and mutations to this gene may cause resistance to antimicrobial peptides that target the outer membrane.",
                           "notes": "Implied by the pairing of the biosynthesis role with resistance to peptides 'that target the outer membrane'. NOT a mechanism CARD spells out."}]},
            {"subject": "altered_membrane", "object": "drug0",
             "predicate": "negatively regulates (the peptide's target is changed)",
             "predicate_id": "RO:0002212",
             "evidence": [{"reference": "ARO:3003573", "snippet": "The LpxA gene is widely known to be involved in the biosynthesis of lipid A in Gram-negative bacteria and mutations to this gene may cause resistance to antimicrobial peptides that target the outer membrane.",
                           "notes": "'resistance to antimicrobial peptides that target the outer membrane'."}]},
        ],
    },
    # Aminoacylation of LPS (ARO:3003580) -- a fifth surface-charge route.
    "ARO:3003580-acyl": {
        "curated": "2026-08-07T00:00:00Z",
        "precondition": _requires_lipid_a_aminoacylation,
        "reference": "ARO:3003588",
        "mech": {"ARO:3003588": "The loss or reduction of the net negative charge within the cell wall of gram negative bacteria is a mechanism of resistance for cationic antimicrobials that depend on the negative charge for binding to the surface."},
        "mech_res": "Lipid A acyltransferase genes confer resistance to certain types of peptide antibiotics such as polymyxins through the aminoacylation of lipopolysaccharide, thereby decreasing the negative charge of the outer membrane surface.",
        "det_res": [
            {"reference": "ARO:3004363", "snippet": "Lipid A acyltransferase genes confer resistance to certain types of peptide antibiotics such as polymyxins through the aminoacylation of lipopolysaccharide, thereby decreasing the negative charge of the outer membrane surface.",
             "notes": "Route, consequence and drug class in one sentence, stated causally ('confer resistance ... thereby decreasing the negative charge')."},
            {"reference": "ARO:3003588", "snippet": "The loss or reduction of the net negative charge within the cell wall of gram negative bacteria is a mechanism of resistance for cationic antimicrobials that depend on the negative charge for binding to the surface.",
             "notes": "The shared causal sentence for every route on this family."},
        ],
        "res_drug": "Lipid A acyltransferase genes confer resistance to certain types of peptide antibiotics such as polymyxins through the aminoacylation of lipopolysaccharide, thereby decreasing the negative charge of the outer membrane surface.",
        "note": "Charge alteration by aminoacylation of LPS; the fifth route on this family.",
        "extra_nodes": [
            {"node_id": "aminoacylation", "label": "aminoacylation of lipopolysaccharide",
             "node_type": "MOLECULAR_FUNCTION",
             "description": "Ungrounded: not looked up rather than guessed (rounds 56-75)."},
            {"node_id": "charge", "label": "reduced net negative surface charge",
             "node_type": "STATE", "description": "The causal core, shared across this family's routes."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "aminoacylation",
             "predicate": "enables (aminoacylates LPS)", "predicate_id": "RO:0002327",
             "evidence": [{"reference": "ARO:3004363", "snippet": "Lipid A acyltransferase genes confer resistance to certain types of peptide antibiotics such as polymyxins through the aminoacylation of lipopolysaccharide, thereby decreasing the negative charge of the outer membrane surface.",
                           "notes": "'through the aminoacylation of lipopolysaccharide'."}]},
            {"subject": "aminoacylation", "object": "charge",
             "predicate": "causally upstream of (decreases negative charge)",
             "predicate_id": "RO:0002411",
             "evidence": [{"reference": "ARO:3004363", "snippet": "Lipid A acyltransferase genes confer resistance to certain types of peptide antibiotics such as polymyxins through the aminoacylation of lipopolysaccharide, thereby decreasing the negative charge of the outer membrane surface.",
                           "notes": "'thereby decreasing the negative charge of the outer membrane'."}]},
            {"subject": "charge", "object": "drug0",
             "predicate": "negatively regulates (impedes drug binding)",
             "predicate_id": "RO:0002212",
             "evidence": [{"reference": "ARO:3003588", "snippet": "The loss or reduction of the net negative charge within the cell wall of gram negative bacteria is a mechanism of resistance for cationic antimicrobials that depend on the negative charge for binding to the surface.",
                           "notes": "'cationic antimicrobials that depend on the negative charge for binding'."}]},
        ],
    },
    # cprRS -- REGULATION, ending at the Ara4N records rather than restating them.
    "ARO:3003580-cpr": {
        "curated": "2026-08-07T00:00:00Z",
        "precondition": _requires_cpr_regulator,
        "reference": "ARO:3005065",
        "mech": {"ARO:3003588": "cprRS is a two-component regulatory system. In the presence of cationic peptides, it induces the Arn operon to confer resistance."},
        "mech_res": "cprRS is a two-component regulatory system. In the presence of cationic peptides, it induces the Arn operon to confer resistance.",
        "det_res": [
            {"reference": "ARO:3005065", "snippet": "cprRS is a two-component regulatory system. In the presence of cationic peptides, it induces the Arn operon to confer resistance.",
             "notes": "cprRS confers resistance by INDUCING the Arn operon, not by altering charge itself. Round 22's rule: a regulator's graph ends at the records that do the work."},
        ],
        "res_drug": "cprRS is a two-component regulatory system. In the presence of cationic peptides, it induces the Arn operon to confer resistance.",
        "note": ("Regulation, not charge alteration. The downstream is the Ara4N route "
                 "curated in round 75; this graph points at it rather than restating its "
                 "chemistry, so it inherits whatever those records say today."),
        "extra_nodes": [
            {"node_id": "sensing", "label": "sensing of cationic peptides",
             "node_type": "STATE",
             "description": "The inducing signal. Ungrounded."},
            {"node_id": "arn_operon", "label": "Arn operon (Ara4N synthesis and transfer)",
             "node_type": "NUCLEIC_ACID", "grounding": "ARO:3003578",
             "description": "Grounded to PmrF, a KB record curated in round 75 -- the cross-round citation pattern from round 22."},
        ],
        "extra_edges": [
            {"subject": "sensing", "object": "determinant",
             "predicate": "causally upstream of (activates the two-component system)",
             "predicate_id": "RO:0002411",
             "evidence": [{"reference": "ARO:3005065", "snippet": "cprRS is a two-component regulatory system. In the presence of cationic peptides, it induces the Arn operon to confer resistance.",
                           "notes": "'In the presence of cationic peptides' -- the drug itself is the inducing signal."}]},
            {"subject": "determinant", "object": "arn_operon",
             "predicate": "positively regulates (induces the Arn operon)",
             "predicate_id": "RO:0002213",
             "description": "Where this graph STOPS. The Ara4N chemistry lives on those records (round 75), not restated here.",
             "evidence": [{"reference": "ARO:3005065", "snippet": "cprRS is a two-component regulatory system. In the presence of cationic peptides, it induces the Arn operon to confer resistance.",
                           "notes": "'it induces the Arn operon to confer resistance'."}]},
        ],
    },
    # ---------------------------------------------------------------------------------
    # Ara4N addition to lipid A (under ARO:3003580) -- the fourth charge-alteration route,
    # and the one rounds 73-74 mistakenly believed was already curated.
    "ARO:3003580-ara4n": {
        "curated": "2026-08-07T00:00:00Z",
        "precondition": _requires_ara4n,
        "reference": "ARO:3003588",
        "mech": {"ARO:3003588": "The loss or reduction of the net negative charge within the cell wall of gram negative bacteria is a mechanism of resistance for cationic antimicrobials that depend on the negative charge for binding to the surface."},
        "mech_res": "The loss or reduction of the net negative charge within the cell wall of gram negative bacteria is a mechanism of resistance for cationic antimicrobials that depend on the negative charge for binding to the surface.",
        "det_res": [
            {"reference": "ARO:3003588", "snippet": "The loss or reduction of the net negative charge within the cell wall of gram negative bacteria is a mechanism of resistance for cationic antimicrobials that depend on the negative charge for binding to the surface.",
             "notes": "The shared causal sentence, as for the pEtN and glycylation routes."},
            {"reference": "ARO:3003578", "snippet": "PmrF is required for the synthesis and transfer of 4-amino-4-deoxy-L-arabinose (Ara4N) to Lipid A, which allows gram-negative bacteria to resist the antimicrobial activity of cationic antimicrobial peptides and antibiotics such as polymyxin.",
             "notes": "The route and its consequence in one sentence. SCOPE: PmrF's; these records span synthesis (PmrE/ugd, arnA) and transfer (ArnT), which this sentence covers collectively as 'synthesis and transfer'."},
        ],
        "res_drug": "arnA modifies lipid A with 4-amino-4-deoxy-L-arabinose (Ara4N) which allows gram-negative bacteria to resist the antimicrobial activity of cationic antimicrobial peptides and antibiotics such as polymyxin.",
        "note": "Charge alteration by Ara4N addition to lipid A. Distinct from mprF (lysyl-PG), pEtN and glycylation routes on this family.",
        "extra_nodes": [
            {"node_id": "ara4n_pathway", "label": "Ara4N synthesis and transfer to lipid A",
             "node_type": "MOLECULAR_FUNCTION",
             "description": "One node for a multi-step pathway: CARD's sentence bundles 'synthesis and transfer', and these records are different steps of it."},
            {"node_id": "lipid_a", "label": "lipid A of the outer membrane",
             "node_type": "CHEMICAL",
             "description": "The modified surface. Ungrounded: no CHEBI id verified this round."},
            {"node_id": "charge", "label": "reduced net negative surface charge",
             "node_type": "STATE", "description": "The causal core, shared across this family's routes."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "ara4n_pathway",
             "predicate": "participates in (Ara4N synthesis and transfer)",
             "predicate_id": "RO:0000056",
             "description": "'Participates in' rather than 'enables', for round 74's reason: these records are different steps (PmrE/ugd synthesis, ArnT transfer) and no one of them performs the route.",
             "evidence": [{"reference": "ARO:3003578", "snippet": "PmrF is required for the synthesis and transfer of 4-amino-4-deoxy-L-arabinose (Ara4N) to Lipid A, which allows gram-negative bacteria to resist the antimicrobial activity of cationic antimicrobial peptides and antibiotics such as polymyxin.",
                           "notes": "'required for the synthesis AND transfer' -- CARD treats it as a multi-step route."}]},
            {"subject": "ara4n_pathway", "object": "lipid_a",
             "predicate": "causally upstream of (modifies lipid A)", "predicate_id": "RO:0002411",
             "evidence": [{"reference": "ARO:3002985", "snippet": "arnA modifies lipid A with 4-amino-4-deoxy-L-arabinose (Ara4N) which allows gram-negative bacteria to resist the antimicrobial activity of cationic antimicrobial peptides and antibiotics such as polymyxin.",
                           "notes": "'modifies lipid A with 4-amino-4-deoxy-L-arabinose'."}]},
            {"subject": "lipid_a", "object": "charge",
             "predicate": "causally upstream of (reduces surface negative charge)",
             "predicate_id": "RO:0002411",
             "evidence": [{"reference": "ARO:3003588", "snippet": "The loss or reduction of the net negative charge within the cell wall of gram negative bacteria is a mechanism of resistance for cationic antimicrobials that depend on the negative charge for binding to the surface.",
                           "notes": "'loss or reduction of the net negative charge within the cell wall'."}]},
            {"subject": "charge", "object": "drug0",
             "predicate": "negatively regulates (impedes drug binding)",
             "predicate_id": "RO:0002212",
             "evidence": [{"reference": "ARO:3003578", "snippet": "PmrF is required for the synthesis and transfer of 4-amino-4-deoxy-L-arabinose (Ara4N) to Lipid A, which allows gram-negative bacteria to resist the antimicrobial activity of cationic antimicrobial peptides and antibiotics such as polymyxin.",
                           "notes": "'allows gram-negative bacteria to resist ... cationic antimicrobial peptides'."}]},
        ],
    },
    # ---------------------------------------------------------------------------------
    # alm glycylation (under ARO:3003580) -- the THIRD lipid A charge-alteration route.
    #
    # mprF acylation and phosphoethanolamine addition (round 73) are two of the others. All
    # three neutralise the same negative charge by attaching a different group, and all
    # three share ARO:3003588's causal sentence.
    "ARO:3003580-alm": {
        "curated": "2026-08-07T00:00:00Z",
        "precondition": _requires_alm_glycylation,
        "reference": "ARO:3003588",
        "mech": {"ARO:3003588": "The loss or reduction of the net negative charge within the cell wall of gram negative bacteria is a mechanism of resistance for cationic antimicrobials that depend on the negative charge for binding to the surface."},
        "mech_res": "The loss or reduction of the net negative charge within the cell wall of gram negative bacteria is a mechanism of resistance for cationic antimicrobials that depend on the negative charge for binding to the surface.",
        "det_res": [
            {"reference": "ARO:3003588", "snippet": "The loss or reduction of the net negative charge within the cell wall of gram negative bacteria is a mechanism of resistance for cationic antimicrobials that depend on the negative charge for binding to the surface.",
             "notes": "The shared causal sentence: cationic antimicrobials depend on the negative charge, so neutralising it is the resistance. Same for all three lipid A routes."},
            {"reference": "ARO:3007434", "snippet": "The almEFG operon is responsible for glycylation of lipid A as a mechanism of colistin resistance in Vibrio cholerae.",
             "notes": "The route, named for colistin in Vibrio cholerae. Cited FROM the operon record, which is itself left as a draft -- it is the best mechanism source here and curating it would pre-empt the open gene-cluster modelling question."},
        ],
        "res_drug": "The almEFG operon is responsible for glycylation of lipid A as a mechanism of colistin resistance in Vibrio cholerae.",
        "note": "Charge alteration by glycylation of lipid A; L-Ara4N and phosphoethanolamine routes have their own configs on this family.",
        "extra_nodes": [
            {"node_id": "glycyl_transfer", "label": "glycyl transfer to the carrier protein AlmF",
             "node_type": "MOLECULAR_FUNCTION",
             "description": "Ungrounded: not looked up rather than guessed (rounds 56-73)."},
            {"node_id": "lipid_a", "label": "lipid A of the outer membrane",
             "node_type": "CHEMICAL",
             "description": "The modified surface. Ungrounded: no CHEBI id verified this round."},
            {"node_id": "charge", "label": "reduced net negative surface charge",
             "node_type": "STATE",
             "description": "The causal core, shared with the L-Ara4N and pEtN routes."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "glycyl_transfer",
             "predicate": "participates in (the glycyl relay)", "predicate_id": "RO:0000056",
             "description": "A RELAY, not a single enzyme: almE charges the carrier almF, and almG then glycylates lipid A. The predicate is 'participates in' because these records are different steps of one route and no single one performs it.",
             "evidence": [{"reference": "ARO:3007434", "snippet": "Its mechanism involves transfer of a glycyl molecule to the carrier protein almF by almE followed by glycylation of lipid A by almG.",
                           "notes": "CARD names all three roles and their order."}]},
            {"subject": "glycyl_transfer", "object": "lipid_a",
             "predicate": "causally upstream of (glycylates lipid A)", "predicate_id": "RO:0002411",
             "evidence": [{"reference": "ARO:3007434", "snippet": "Its mechanism involves transfer of a glycyl molecule to the carrier protein almF by almE followed by glycylation of lipid A by almG.",
                           "notes": "'followed by glycylation of lipid A by almG'."}]},
            {"subject": "lipid_a", "object": "charge",
             "predicate": "causally upstream of (reduces surface negative charge)",
             "predicate_id": "RO:0002411",
             "evidence": [{"reference": "ARO:3003588", "snippet": "The loss or reduction of the net negative charge within the cell wall of gram negative bacteria is a mechanism of resistance for cationic antimicrobials that depend on the negative charge for binding to the surface.",
                           "notes": "'loss or reduction of the net negative charge within the cell wall'."}]},
            {"subject": "charge", "object": "drug0",
             "predicate": "negatively regulates (impedes drug binding)",
             "predicate_id": "RO:0002212",
             "evidence": [{"reference": "ARO:3003588", "snippet": "The loss or reduction of the net negative charge within the cell wall of gram negative bacteria is a mechanism of resistance for cationic antimicrobials that depend on the negative charge for binding to the surface.",
                           "notes": "'cationic antimicrobials that depend on the negative charge for binding'."}]},
        ],
    },
    # ---------------------------------------------------------------------------------
    # Phosphoethanolamine transferases (under ARO:3003580) -- charge alteration, pEtN route.
    #
    # The family already carries an mprF config. These records neutralise lipid A with
    # phosphoethanolamine instead. Same outcome, different moiety, and the causal sentence
    # is the same: less negative charge, so the cationic drug binds less.
    #
    # Found by #264's near-miss detector in round 69, which flagged eptA and the pmr family
    # as refused for lacking "L-Ara4N addition" when every token of that phrase was in
    # their definitions. That is the detector doing exactly what it was built for.
    "ARO:3003580-petn": {
        "curated": "2026-08-07T00:00:00Z",
        "precondition": _requires_petn_transferase,
        "reference": "ARO:3003588",
        "mech": {"ARO:3003588": "The loss or reduction of the net negative charge within the cell wall of gram negative bacteria is a mechanism of resistance for cationic antimicrobials that depend on the negative charge for binding to the surface."},
        "mech_res": "The loss or reduction of the net negative charge within the cell wall of gram negative bacteria is a mechanism of resistance for cationic antimicrobials that depend on the negative charge for binding to the surface.",
        "det_res": [
            {"reference": "ARO:3003588", "snippet": "The loss or reduction of the net negative charge within the cell wall of gram negative bacteria is a mechanism of resistance for cationic antimicrobials that depend on the negative charge for binding to the surface.",
             "notes": "The mechanism, stated causally: cationic antimicrobials DEPEND on the negative charge for binding, so reducing it is the resistance."},
            {"reference": "ARO:3004269", "snippet": "This family of phosphoethanolamine transferase catalyze the addition of 4-amino-4-deoxy-L-arabinose (L-Ara4N) and phosphoethanolamine to lipid A, which impedes the binding of colistin to the cell membrane.",
             "notes": "And the consequence, named for colistin: 'impedes the binding of colistin to the cell membrane'."},
            {"reference": "ARO:3004112", "snippet": "This group of enzymes catalyzes the addition of a phosphoethanolamine group to another molecule. The addition of this moiety to lipid A in bacterial species is often associated with polymyxin (otherwise known as colistin) resistance.",
             "notes": "The chemistry. NOTE its hedge -- 'often ASSOCIATED WITH polymyxin resistance' -- weaker than ARO:3003588's causal statement, and quoted for the reaction rather than for the resistance link."},
        ],
        "res_drug": "This family of phosphoethanolamine transferase catalyze the addition of 4-amino-4-deoxy-L-arabinose (L-Ara4N) and phosphoethanolamine to lipid A, which impedes the binding of colistin to the cell membrane.",
        "note": "Charge alteration by phosphoethanolamine addition; the L-Ara4N route has its own config on this family.",
        "extra_nodes": [
            {"node_id": "petn_transfer", "label": "phosphoethanolamine transferase activity",
             "node_type": "MOLECULAR_FUNCTION",
             "description": "Ungrounded: not looked up rather than guessed (rounds 56-72)."},
            {"node_id": "lipid_a", "label": "lipid A of the outer membrane",
             "node_type": "CHEMICAL",
             "description": "The modified target surface. Ungrounded: no CHEBI id verified this round."},
            {"node_id": "charge", "label": "reduced net negative surface charge",
             "node_type": "STATE",
             "description": "The causal core. Ungrounded: a charge state is not an entity."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "petn_transfer",
             "predicate": "enables (adds phosphoethanolamine)", "predicate_id": "RO:0002327",
             "evidence": [{"reference": "ARO:3004112", "snippet": "This group of enzymes catalyzes the addition of a phosphoethanolamine group to another molecule. The addition of this moiety to lipid A in bacterial species is often associated with polymyxin (otherwise known as colistin) resistance.",
                           "notes": "'catalyzes the addition of a phosphoethanolamine group'."}]},
            {"subject": "petn_transfer", "object": "lipid_a",
             "predicate": "has input (lipid A)", "predicate_id": "RO:0002233",
             "evidence": [{"reference": "ARO:3004269", "snippet": "This family of phosphoethanolamine transferase catalyze the addition of 4-amino-4-deoxy-L-arabinose (L-Ara4N) and phosphoethanolamine to lipid A, which impedes the binding of colistin to the cell membrane.",
                           "notes": "'addition of ... phosphoethanolamine to lipid A'."}]},
            {"subject": "lipid_a", "object": "charge",
             "predicate": "causally upstream of (reduces surface negative charge)",
             "predicate_id": "RO:0002411",
             "evidence": [{"reference": "ARO:3003588", "snippet": "The loss or reduction of the net negative charge within the cell wall of gram negative bacteria is a mechanism of resistance for cationic antimicrobials that depend on the negative charge for binding to the surface.",
                           "notes": "'loss or reduction of the net negative charge within the cell wall'."}]},
            {"subject": "charge", "object": "drug0",
             "predicate": "negatively regulates (impedes drug binding)",
             "predicate_id": "RO:0002212",
             "description": "Why less charge is resistance: the drug is cationic and binds BECAUSE of the negative surface.",
             "evidence": [
                 {"reference": "ARO:3003588", "snippet": "The loss or reduction of the net negative charge within the cell wall of gram negative bacteria is a mechanism of resistance for cationic antimicrobials that depend on the negative charge for binding to the surface.",
                  "notes": "'cationic antimicrobials that depend on the negative charge for binding'."},
                 {"reference": "ARO:3004269", "snippet": "This family of phosphoethanolamine transferase catalyze the addition of 4-amino-4-deoxy-L-arabinose (L-Ara4N) and phosphoethanolamine to lipid A, which impedes the binding of colistin to the cell membrane.",
                  "notes": "'impedes the binding of colistin to the cell membrane'."}]},
        ],
    },
    # ---------------------------------------------------------------------------------
    # Resistance by ABSENCE (ARO:3003764) -- a 13th mechanism kind, keyed on the mechanism
    # id rather than a family term because its members sit under unrelated families.
    #
    # Round 56's pncA was resistance by losing an ACTIVITY. This is broader and stranger:
    # resistance by the gene not being there at all. The determinant is a deletion.
    #
    # TWO things are deliberately not asserted:
    #
    # 1. That the deleted gene is a porin. CARD says "USUALLY a porin" -- round 63's donor
    #    hedge in another costume -- and these 9 records include a stress-activated kinase
    #    (Hog1), a UDP-glucuronic acid decarboxylase (UXS1) and a PhoPQ regulator (mgrB).
    # 2. The downstream consequence. It differs per record -- increased exposed chitin,
    #    metabolite accumulation, blocked drug entry -- and no sentence covers all of them.
    #    Each would be a good per-record addition; none is a family claim.
    # Keyed on the ROOT term, not on ARO:3003764. "Resistance by absence" is a MECHANISM
    # id, and its 9 records sit under unrelated families (a stress kinase, a decarboxylase,
    # a PhoPQ regulator, porins) with no common ancestor but the root. The promoter walks
    # is_a ancestry, so a mechanism id cannot be a family key -- the precondition does the
    # selection instead, and it selects exactly, on the mechanism the record carries.
    #
    # This makes the candidate set the whole corpus, which is safe for --apply (drafts
    # only, precondition-filtered) and is exactly the case #280's blast-radius guard was
    # built for on the --repromote path.
    "ARO:3000000": {
        "curated": "2026-08-07T00:00:00Z",
        "precondition": _requires_mech("ARO:3003764", "resistance by absence"),
        "reference": "ARO:3003764",
        "mech": {"ARO:3003764": "Mechanism of antibiotic resistance conferred by deletion of gene (usually a porin)."},
        "mech_res": "Mechanism of antibiotic resistance conferred by deletion of gene (usually a porin).",
        "det_res": [
            {"reference": "ARO:3003764", "snippet": "Mechanism of antibiotic resistance conferred by deletion of gene (usually a porin).",
             "notes": "The mechanism, with its hedge intact: 'usually a porin' -- so porin-ness is NOT asserted for these records, which include a kinase, a decarboxylase and a regulator."},
            {"reference": "ARO:3003768", "snippet": "Deletion of gene or gene product results in resistance. For example, deletion of a porin gene blocks drug from entering the cell.",
             "notes": "The general statement. Its porin example is quoted as an EXAMPLE, which is what CARD calls it, not as this family's route."},
        ],
        "res_drug": "Mechanism of antibiotic resistance conferred by deletion of gene (usually a porin).",
        "note": ("Resistance by absence. Neither the identity of the deleted gene nor the "
                 "downstream consequence is asserted: CARD hedges the first and the second "
                 "differs per record (chitin exposure, metabolite accumulation, blocked "
                 "entry). Both are good per-record additions and neither is a family claim."),
        "extra_nodes": [
            {"node_id": "absence", "label": "absence of the gene product",
             "node_type": "STATE",
             "description": "The determinant state, and the whole mechanism. Ungrounded: an absence is not an entity."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "absence",
             "predicate": "has quality (deleted or inactivated)", "predicate_id": "RO:0000086",
             "description": "The determinant here IS a loss -- what the record names is a gene whose deletion confers resistance, not a gene product that acts.",
             "evidence": [{"reference": "ARO:3003768", "snippet": "Deletion of gene or gene product results in resistance. For example, deletion of a porin gene blocks drug from entering the cell.",
                           "notes": "'Deletion of gene or gene product results in resistance'."}]},
            {"subject": "absence", "object": "resistance",
             "predicate": "causally upstream of (confers resistance)",
             "predicate_id": "RO:0002411",
             "description": "The causal core, and deliberately the ONLY downstream edge -- what the absence leads to differs across these records and no source covers all of them.",
             "evidence": [{"reference": "ARO:3003764", "snippet": "Mechanism of antibiotic resistance conferred by deletion of gene (usually a porin).",
                           "notes": "'antibiotic resistance conferred by deletion of gene'."}]},
        ],
    },
    # ---------------------------------------------------------------------------------
    # MATE efflux transporters (ARO:3000112) -- efflux with energetics, hedged.
    #
    # Round 67 curated SMR, whose text names the coupling ion outright: EmrE couples
    # efflux "with the import of PROTONS". MATE's text does not. It says only "utilize the
    # CATIONIC gradient" -- and MATE transporters really are split between Na+ and H+
    # coupling, so the vagueness is the source being correct, not sloppy.
    #
    # So the gradient node here is generic. Copying round 67's proton node across would
    # have been the easy mistake, and exactly the one round 67's own report warned about
    # for RND/MFS/ABC. Round 68's donor-hedge rule, applied to a coupling ion.
    "ARO:3000112": {
        "curated": "2026-08-07T00:00:00Z",
        "precondition": _requires_mech("ARO:0010000", "antibiotic efflux"),
        "reference": "ARO:3000112",
        "mech": {"ARO:0010000": "Antibiotic resistance via the transport of antibiotics out of the cell."},
        "mech_res": "Multidrug and toxic compound extrusion (MATE) transporters utilize the cationic gradient across the membrane as an energy source.",
        "det_res": [
            {"reference": "ARO:3000112", "snippet": "Multidrug and toxic compound extrusion (MATE) transporters utilize the cationic gradient across the membrane as an energy source.",
             "notes": "The energetics, stated but NOT resolved to an ion: 'cationic gradient'. MATE transporters are genuinely split between Na+ and H+ coupling, so this is the source being accurate."},
            {"reference": "ARO:3000112", "snippet": "Although there is a diverse substrate specificity, almost all MATE transporters recognize fluoroquinolones.",
             "notes": "And the substrate range, hedged in its own way -- 'almost all', so the fluoroquinolone claim is not universal within the family."},
        ],
        "res_drug": "Antibiotic resistance via the transport of antibiotics out of the cell.",
        "note": ("Efflux driven by a cationic gradient. The coupling ion is deliberately "
                 "NOT specified: CARD says 'cationic', and unlike SMR (round 67, protons) "
                 "MATE really does split between Na+ and H+."),
        "extra_nodes": [
            {"node_id": "extrusion", "label": "multidrug efflux transporter activity",
             "node_type": "MOLECULAR_FUNCTION",
             "description": "Ungrounded: not looked up rather than guessed (rounds 56-68)."},
            {"node_id": "cation_gradient", "label": "transmembrane cationic gradient (ion unspecified)",
             "node_type": "STATE",
             "description": "The energy source. Deliberately generic -- see the config note."},
            {"node_id": "extruded", "label": "drug outside the cell",
             "node_type": "STATE", "description": "The outcome. Ungrounded."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "extrusion",
             "predicate": "enables (extrudes the drug)", "predicate_id": "RO:0002327",
             "evidence": [{"reference": "ARO:3000112", "snippet": "Multidrug and toxic compound extrusion (MATE) transporters utilize the cationic gradient across the membrane as an energy source.",
                           "notes": "MATE = multidrug and toxic compound extrusion."}]},
            {"subject": "cation_gradient", "object": "extrusion",
             "predicate": "causally upstream of (drives the transport)",
             "predicate_id": "RO:0002411",
             "description": "What powers the pump, as with SMR (round 67) -- but the ion is left open here because CARD leaves it open.",
             "evidence": [{"reference": "ARO:3000112", "snippet": "Multidrug and toxic compound extrusion (MATE) transporters utilize the cationic gradient across the membrane as an energy source.",
                           "notes": "'utilize the cationic gradient across the membrane as an energy source'."}]},
            {"subject": "extrusion", "object": "drug0",
             "predicate": "has input (the drug)", "predicate_id": "RO:0002233",
             "evidence": [{"reference": "ARO:3000112", "snippet": "Although there is a diverse substrate specificity, almost all MATE transporters recognize fluoroquinolones.",
                           "notes": "'almost all MATE transporters recognize fluoroquinolones' -- the recognition claim, with its own hedge intact."}]},
            {"subject": "extrusion", "object": "extruded",
             "predicate": "causally upstream of (removes the drug from the cell)",
             "predicate_id": "RO:0002411",
             "description": "The causal core.",
             "evidence": [{"reference": "ARO:0010000", "snippet": "Antibiotic resistance via the transport of antibiotics out of the cell.",
                           "notes": "'via the transport of antibiotics out of the cell'."}]},
        ],
    },
    # ---------------------------------------------------------------------------------
    # SMR efflux pumps (ARO:0010003) -- efflux, with the ENERGETICS actually stated.
    #
    # Most efflux records in this corpus say only "pumps the drug out". SMR is the first
    # family whose own text gives the coupling: EmrE "couples the efflux of small
    # polyaromatic cations from the cell WITH THE IMPORT OF PROTONS down an
    # electrochemical gradient". That is a proton antiport, and it is what makes efflux a
    # mechanism rather than a restatement of the phenotype -- the drug does not leave
    # because the pump wants it to, it leaves because protons are coming in.
    #
    # SCOPE: the antiport sentence is EmrE's. Other members here (abeS and the rest) are
    # named as SMR-family transporters without their own energetics, so the coupling edge
    # cites EmrE and its notes say so.
    "ARO:0010003": {
        "curated": "2026-08-07T00:00:00Z",
        "precondition": _requires_mech("ARO:0010000", "antibiotic efflux"),
        "reference": "ARO:0010003",
        "mech": {"ARO:0010000": "Antibiotic resistance via the transport of antibiotics out of the cell."},
        "mech_res": "Antibiotic resistance via the transport of antibiotics out of the cell.",
        "det_res": [
            {"reference": "ARO:0010003", "snippet": "Directed pumping of antibiotic out of a cell to confer resistance. Small multidrug resistance (SMR) proteins are a relatively small family of transporters, restricted to prokaryotic cells.",
             "notes": "The family claim: directed pumping of antibiotic out of the cell, by a distinct small transporter family."},
            {"reference": "ARO:3000264", "snippet": "EmrE is a small multidrug transporter that functions as a homodimer and that couples the efflux of small polyaromatic cations from the cell with the import of protons down an electrochemical gradient.",
             "notes": "And the energetics. SCOPE: this is EmrE's sentence; the other members are named as SMR-family transporters without their own coupling data."},
        ],
        "res_drug": "Antibiotic resistance via the transport of antibiotics out of the cell.",
        "note": "Efflux, with the proton-antiport coupling stated rather than assumed.",
        "extra_nodes": [
            {"node_id": "antiport", "label": "drug/proton antiporter activity",
             "node_type": "MOLECULAR_FUNCTION", "grounding": "GO:0015297",
             "description": "Checked non-obsolete against OLS (#157)."},
            {"node_id": "proton_gradient", "label": "inward proton electrochemical gradient",
             "node_type": "STATE",
             "description": "The energy source. Ungrounded: a gradient is not a compound."},
            {"node_id": "extruded", "label": "drug outside the cell",
             "node_type": "STATE", "description": "The outcome. Ungrounded."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "antiport",
             "predicate": "enables (drug/proton antiport)", "predicate_id": "RO:0002327",
             "evidence": [{"reference": "ARO:3000264", "snippet": "EmrE is a small multidrug transporter that functions as a homodimer and that couples the efflux of small polyaromatic cations from the cell with the import of protons down an electrochemical gradient.",
                           "notes": "'couples the efflux ... with the import of protons' -- an antiport by definition."}]},
            {"subject": "proton_gradient", "object": "antiport",
             "predicate": "causally upstream of (drives the transport)",
             "predicate_id": "RO:0002411",
             "description": "What powers the pump. Efflux is not spontaneous, and this is the one family here that says what pays for it.",
             "evidence": [{"reference": "ARO:3000264", "snippet": "EmrE is a small multidrug transporter that functions as a homodimer and that couples the efflux of small polyaromatic cations from the cell with the import of protons down an electrochemical gradient.",
                           "notes": "'down an electrochemical gradient' -- the protons move downhill, which is what drives the drug uphill."}]},
            {"subject": "antiport", "object": "drug0",
             "predicate": "has input (the drug)", "predicate_id": "RO:0002233",
             "evidence": [{"reference": "ARO:0010003", "snippet": "Directed pumping of antibiotic out of a cell to confer resistance. Small multidrug resistance (SMR) proteins are a relatively small family of transporters, restricted to prokaryotic cells.",
                           "notes": "The antibiotic is the transported substrate."}]},
            {"subject": "antiport", "object": "extruded",
             "predicate": "causally upstream of (removes the drug from the cell)",
             "predicate_id": "RO:0002411",
             "description": "The causal core: resistance because the drug is no longer inside.",
             "evidence": [{"reference": "ARO:0010000", "snippet": "Antibiotic resistance via the transport of antibiotics out of the cell.",
                           "notes": "'via the transport of antibiotics out of the cell'."}]},
        ],
    },
    # ---------------------------------------------------------------------------------
    # Antibiotic resistant EF-Tu (ARO:3003356) -- the mechanism is NOT asserted.
    #
    # CARD says only that "sequence variants of elongation factor Tu confer resistance".
    # It never says HOW. Its generic mutation term (ARO:3000212) hedges across two
    # incompatible routes -- "modified antibiotic targets with lower binding affinities"
    # AND "deactivation of repressors that result in increased expression" -- so it cannot
    # be used to pin this family's route either.
    #
    # The well-known answer is that elfamycins bind EF-Tu and the variants stop them. This
    # config does NOT say that. Round 51 was exactly this failure: three rounds spent
    # sourcing a mechanism I knew and the records never claimed. What IS asserted is what
    # CARD states plus what the determinant's own NAME states -- that it is an elongation
    # factor -- and the drug-binding arm is left for whoever can cite it.
    "ARO:3003356": {
        "curated": "2026-08-07T00:00:00Z",
        "precondition": _requires_mech("ARO:3000212", "mutation"),
        "reference": "ARO:3003356",
        "mech": {"ARO:3000212": "Sequence variants of elongation factor Tu that confer resistance to different classes of antibiotics."},
        "mech_res": "Sequence variants of elongation factor Tu that confer resistance to different classes of antibiotics.",
        "det_res": [
            {"reference": "ARO:3003356", "snippet": "Sequence variants of elongation factor Tu that confer resistance to different classes of antibiotics.",
             "notes": "CARD's whole claim for this family: variants confer resistance. Stated causally -- 'confer', unlike the nim family's 'associated with' (round 65)."},
            {"reference": "ARO:3001312", "snippet": "Sequence variants of elongation factor Tu that confer resistance to elfamycin antibiotics.",
             "notes": "And the drug class for most members. Neither sentence says HOW the variant resists."},
            {"reference": "ARO:3000212", "snippet": "Point mutations in the DNA may lead to an altered gene product that may result in antibiotic resistance.",
             "notes": "CARD's generic mutation mechanism, quoted only as far as it goes. Its examples cover BOTH lower target affinity and repressor deactivation, so it cannot pin this family's route -- which is why no mechanism edge is written below."},
        ],
        "res_drug": "Sequence variants of elongation factor Tu that confer resistance to elfamycin antibiotics.",
        "note": ("Mechanism deliberately NOT asserted. CARD states that EF-Tu variants "
                 "confer resistance and never states how; the elfamycin-binding story is "
                 "well known and uncited here. The graph carries the determinant's "
                 "function and its resistance, and stops."),
        "extra_nodes": [
            {"node_id": "ef_activity", "label": "translation elongation factor activity",
             "node_type": "MOLECULAR_FUNCTION", "grounding": "GO:0003746",
             "description": "Checked non-obsolete against OLS (#157)."},
            {"node_id": "elongation", "label": "translational elongation",
             "node_type": "BIOLOGICAL_PROCESS", "grounding": "GO:0006414",
             "description": "Checked non-obsolete against OLS (#157)."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "ef_activity",
             "predicate": "enables (elongation factor activity)", "predicate_id": "RO:0002327",
             "description": "What the determinant IS, which is the one mechanistic fact CARD's own naming supplies.",
             "evidence": [{"reference": "ARO:3003356", "snippet": "Sequence variants of elongation factor Tu that confer resistance to different classes of antibiotics.",
                           "notes": "'elongation factor Tu' -- a functional name, and the only functional claim CARD makes about these records."}]},
            {"subject": "ef_activity", "object": "elongation",
             "predicate": "part of (translational elongation)", "predicate_id": "BFO:0000050",
             "evidence": [{"reference": "ARO:3003356", "snippet": "Sequence variants of elongation factor Tu that confer resistance to different classes of antibiotics.",
                           "notes": "The process the factor serves. NOT asserted: that the drug inhibits it, or that the variant prevents drug binding -- CARD states neither."}]},
        ],
    },
    # ---------------------------------------------------------------------------------
    # Nitroimidazole reductases (nim, ARO:3007103) -- inactivation by REDUCTION.
    #
    # A distinct chemistry from the transfer reactions (rounds 62-64) and the hydrolyses:
    # nothing is added and no bond is cleaved, the drug's nitro group is reduced to an
    # amine and the molecule simply stops being an antibiotic.
    #
    # TWO honesty problems in this family's own text, both handled rather than smoothed:
    #
    # 1. CARD says these enzymes are "ASSOCIATED WITH resistance", not that they confer
    #    it. The chemistry sentence is causal; the resistance sentence is not. The
    #    determinant->resistance edge therefore carries BOTH, with notes saying which is
    #    which, instead of quoting only the strong one.
    # 2. ARO:3007671 states outright that "NimB expression alone is not sufficient for
    #    nitroimidazole resistance" -- a negative result INSIDE the family. It is quoted
    #    on the edge rather than dropped, the way rounds 20 and 23 used negative results.
    "ARO:3007103": {
        "curated": "2026-08-07T00:00:00Z",
        "precondition": _requires_mech("ARO:0001004", "antibiotic inactivation"),
        "reference": "ARO:3007103",
        "mech": {"ARO:0001004": "Nitroimidazole reductases are a group of enzymes that deactivate nitroimidazole antibiotics by reducing their nitro functional group to an amino group."},
        "mech_res": "Nitroimidazole reductases are a group of enzymes that deactivate nitroimidazole antibiotics by reducing their nitro functional group to an amino group.",
        "det_res": [
            {"reference": "ARO:3007103", "snippet": "Nitroimidazole reductases are a group of enzymes that deactivate nitroimidazole antibiotics by reducing their nitro functional group to an amino group.",
             "notes": "The chemistry, stated causally: reduction of the nitro group to an amine deactivates the drug."},
            {"reference": "ARO:3007103", "snippet": "These enzymes are associated with resistance to nitroimidazole derivatives in Bacteroides fragilis but have also been reported in a variety of anaerobic Gram-negative and Gram-positive genera.",
             "notes": "The resistance claim, stated WEAKLY. CARD says 'associated with', not 'confers' -- recorded as association rather than upgraded to causation."},
            {"reference": "ARO:3007671", "snippet": "NimB expression alone is not sufficient for nitroimidazole resistance.",
             "notes": "And the family's own negative result: for C. difficile nimB, the enzyme is necessary but NOT sufficient -- constitutive transcription from a promoter mutation is also required. Quoted because it bounds the claim the other two snippets make."},
        ],
        "res_drug": "Nitroimidazole reductases are a group of enzymes that deactivate nitroimidazole antibiotics by reducing their nitro functional group to an amino group.",
        "note": ("Inactivation by reduction. The determinant->resistance evidence is "
                 "deliberately mixed-strength: CARD states the chemistry causally and the "
                 "resistance only as an association, and one member says expression alone "
                 "is insufficient."),
        "extra_nodes": [
            {"node_id": "reduction", "label": "nitroimidazole reductase activity",
             "node_type": "MOLECULAR_FUNCTION",
             "description": "Ungrounded: not looked up rather than guessed (rounds 56-64)."},
            {"node_id": "nitro", "label": "nitro functional group of the drug",
             "node_type": "CHEMICAL",
             "description": "The group reduced. Ungrounded: a substructure, not a compound."},
            {"node_id": "amine", "label": "amino group -- the reduced, inactive drug",
             "node_type": "STATE", "description": "The product state. Ungrounded."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "reduction",
             "predicate": "enables (reduces the drug)", "predicate_id": "RO:0002327",
             "evidence": [{"reference": "ARO:3007103", "snippet": "Nitroimidazole reductases are a group of enzymes that deactivate nitroimidazole antibiotics by reducing their nitro functional group to an amino group.",
                           "notes": "'a group of enzymes that deactivate nitroimidazole antibiotics by reducing...'."}]},
            {"subject": "nitro", "object": "drug0",
             "predicate": "part of (the intact drug)", "predicate_id": "BFO:0000050",
             "description": "Why reducing this group destroys the antibiotic: the nitro group is what makes a nitroimidazole one.",
             "evidence": [{"reference": "ARO:3007103", "snippet": "Nitroimidazole reductases are a group of enzymes that deactivate nitroimidazole antibiotics by reducing their nitro functional group to an amino group.",
                           "notes": "'their nitro functional group' -- the drug's own substructure, as with the streptogramin lactone ring in round 64."}]},
            {"subject": "reduction", "object": "nitro",
             "predicate": "has input (the nitro group)", "predicate_id": "RO:0002233",
             "evidence": [{"reference": "ARO:3007103", "snippet": "Nitroimidazole reductases are a group of enzymes that deactivate nitroimidazole antibiotics by reducing their nitro functional group to an amino group.",
                           "notes": "The substrate is a group on the drug, not the whole molecule."}]},
            {"subject": "reduction", "object": "amine",
             "predicate": "has output (the reduced amine)", "predicate_id": "RO:0002234",
             "description": "The causal core: reduction to the amine is the deactivation.",
             "evidence": [{"reference": "ARO:3007103", "snippet": "Nitroimidazole reductases are a group of enzymes that deactivate nitroimidazole antibiotics by reducing their nitro functional group to an amino group.",
                           "notes": "'reducing their nitro functional group to an amino group'."}]},
        ],
    },
    # ---------------------------------------------------------------------------------
    # Streptogramin inactivation (ARO:3000233) -- TWO chemistries on TWO drug subtypes.
    #
    # CARD's parent term says so itself: "There are two known mechanisms of streptogramin
    # inactivation". vat acetylates streptogramin A; vgb linearizes type B. Different
    # reaction AND different substrate, so a single config would be wrong twice over.
    # Same measure-before-writing habit as rounds 58, 62 and 63.
    "ARO:3000233": [
        {
            "curated": "2026-08-07T00:00:00Z",
            "precondition": _requires_mech("ARO:3000106", "acylation"),
            "reference": "ARO:3000453",
            "mech": {"ARO:0001004": "vat (Virginiamycin acetyltransferases) enzymes catalyze the transfer of an acetyl group from acetyl-CoA to the secondary alcohol of streptogramin A compounds, thus inactivating virginiamycin-like antibiotics and conferring resistance to these compounds.", "ARO:3000106": "vat (Virginiamycin acetyltransferases) enzymes catalyze the transfer of an acetyl group from acetyl-CoA to the secondary alcohol of streptogramin A compounds, thus inactivating virginiamycin-like antibiotics and conferring resistance to these compounds."},
            "mech_res": "vat (Virginiamycin acetyltransferases) enzymes catalyze the transfer of an acetyl group from acetyl-CoA to the secondary alcohol of streptogramin A compounds, thus inactivating virginiamycin-like antibiotics and conferring resistance to these compounds.",
            "det_res": [
                {"reference": "ARO:3000453", "snippet": "vat (Virginiamycin acetyltransferases) enzymes catalyze the transfer of an acetyl group from acetyl-CoA to the secondary alcohol of streptogramin A compounds, thus inactivating virginiamycin-like antibiotics and conferring resistance to these compounds.",
                 "notes": "The full chain in one sentence: donor, acceptor, the exact position acylated, and the resistance."},
            ],
            "res_drug": "vat (Virginiamycin acetyltransferases) enzymes catalyze the transfer of an acetyl group from acetyl-CoA to the secondary alcohol of streptogramin A compounds, thus inactivating virginiamycin-like antibiotics and conferring resistance to these compounds.",
            "note": "Acetylation of streptogramin A. The vgb lyases in this family act on type B by a different reaction.",
            "extra_nodes": [
                {"node_id": "acetylation", "label": "streptogramin A acetyltransferase activity",
                 "node_type": "MOLECULAR_FUNCTION",
                 "description": "Ungrounded: not looked up rather than guessed (rounds 56-63)."},
                {"node_id": "acetyl_coa", "label": "acetyl-CoA (the acetyl donor)",
                 "node_type": "CHEMICAL", "grounding": "CHEBI:15351"},
                {"node_id": "modified", "label": "acetylated, inactive streptogramin A",
                 "node_type": "STATE", "description": "The product state. Ungrounded."},
            ],
            "extra_edges": [
                {"subject": "determinant", "object": "acetylation",
                 "predicate": "enables (acetylates the drug)", "predicate_id": "RO:0002327",
                 "evidence": [{"reference": "ARO:3000453", "snippet": "vat (Virginiamycin acetyltransferases) enzymes catalyze the transfer of an acetyl group from acetyl-CoA to the secondary alcohol of streptogramin A compounds, thus inactivating virginiamycin-like antibiotics and conferring resistance to these compounds.",
                               "notes": "'catalyze the transfer of an acetyl group'."}]},
                {"subject": "acetylation", "object": "acetyl_coa",
                 "predicate": "has input (the acetyl donor)", "predicate_id": "RO:0002233",
                 "evidence": [{"reference": "ARO:3000453", "snippet": "vat (Virginiamycin acetyltransferases) enzymes catalyze the transfer of an acetyl group from acetyl-CoA to the secondary alcohol of streptogramin A compounds, thus inactivating virginiamycin-like antibiotics and conferring resistance to these compounds.",
                               "notes": "'from acetyl-CoA' -- named outright, unlike the rifampin phosphotransferases whose donor CARD hedges (round 63)."}]},
                {"subject": "acetylation", "object": "drug0",
                 "predicate": "has input (the drug)", "predicate_id": "RO:0002233",
                 "evidence": [{"reference": "ARO:3000453", "snippet": "vat (Virginiamycin acetyltransferases) enzymes catalyze the transfer of an acetyl group from acetyl-CoA to the secondary alcohol of streptogramin A compounds, thus inactivating virginiamycin-like antibiotics and conferring resistance to these compounds.",
                               "notes": "'to the secondary alcohol of streptogramin A compounds' -- CARD gives the position, which is more than most families state."}]},
                {"subject": "acetylation", "object": "modified",
                 "predicate": "causally upstream of (inactivates the drug)",
                 "predicate_id": "RO:0002411",
                 "evidence": [{"reference": "ARO:3000453", "snippet": "vat (Virginiamycin acetyltransferases) enzymes catalyze the transfer of an acetyl group from acetyl-CoA to the secondary alcohol of streptogramin A compounds, thus inactivating virginiamycin-like antibiotics and conferring resistance to these compounds.",
                               "notes": "'thus inactivating virginiamycin-like antibiotics'."}]},
            ],
        },
        {
            "curated": "2026-08-07T00:00:00Z",
            "precondition": _requires_mech("ARO:3000338", "linearization"),
            "reference": "ARO:3000376",
            "mech": {"ARO:0001004": "vgb (Virginiamycin B) lyase inactivates type B streptogramin antibiotics by linearizing the streptogramin lactone ring at the ester linkage through an elimination mechanism, thus conferring resistance to these compounds.", "ARO:3000338": "vgb (Virginiamycin B) lyase inactivates type B streptogramin antibiotics by linearizing the streptogramin lactone ring at the ester linkage through an elimination mechanism, thus conferring resistance to these compounds."},
            "mech_res": "vgb (Virginiamycin B) lyase inactivates type B streptogramin antibiotics by linearizing the streptogramin lactone ring at the ester linkage through an elimination mechanism, thus conferring resistance to these compounds.",
            "det_res": [
                {"reference": "ARO:3000376", "snippet": "vgb (Virginiamycin B) lyase inactivates type B streptogramin antibiotics by linearizing the streptogramin lactone ring at the ester linkage through an elimination mechanism, thus conferring resistance to these compounds.",
                 "notes": "Reaction, bond, and mechanism type all named: the lactone ring is opened at the ester linkage by elimination."},
                {"reference": "ARO:3000233", "snippet": "There are two known mechanisms of streptogramin inactivation shown clinically to confer resistance",
                 "notes": "CARD's parent term stating that this family holds two distinct mechanisms -- the reason it takes two configs."},
            ],
            "res_drug": "vgb (Virginiamycin B) lyase inactivates type B streptogramin antibiotics by linearizing the streptogramin lactone ring at the ester linkage through an elimination mechanism, thus conferring resistance to these compounds.",
            "note": "Ring-opening of type B streptogramin. Not a transfer reaction: nothing is added to the drug.",
            "extra_nodes": [
                {"node_id": "lyase", "label": "streptogramin B lyase activity",
                 "node_type": "MOLECULAR_FUNCTION",
                 "description": "Ungrounded: not looked up rather than guessed."},
                {"node_id": "lactone", "label": "streptogramin lactone ring (ester linkage)",
                 "node_type": "CHEMICAL",
                 "description": "The bond broken. Ungrounded: a substructure, not a compound."},
                {"node_id": "linearized", "label": "linearized, inactive streptogramin B",
                 "node_type": "STATE", "description": "The product state. Ungrounded."},
            ],
            "extra_edges": [
                {"subject": "determinant", "object": "lyase",
                 "predicate": "enables (linearizes the drug)", "predicate_id": "RO:0002327",
                 "evidence": [{"reference": "ARO:3000376", "snippet": "vgb (Virginiamycin B) lyase inactivates type B streptogramin antibiotics by linearizing the streptogramin lactone ring at the ester linkage through an elimination mechanism, thus conferring resistance to these compounds.",
                               "notes": "'vgb (Virginiamycin B) lyase inactivates type B streptogramin antibiotics'."}]},
                {"subject": "lactone", "object": "drug0",
                 "predicate": "part of (the intact drug)", "predicate_id": "BFO:0000050",
                 "description": "Why breaking this bond destroys the antibiotic: the ring IS the drug's structure.",
                 "evidence": [{"reference": "ARO:3000376", "snippet": "vgb (Virginiamycin B) lyase inactivates type B streptogramin antibiotics by linearizing the streptogramin lactone ring at the ester linkage through an elimination mechanism, thus conferring resistance to these compounds.",
                               "notes": "'the streptogramin lactone ring at the ester linkage'."}]},
                {"subject": "lyase", "object": "lactone",
                 "predicate": "has input (the ester linkage)", "predicate_id": "RO:0002233",
                 "evidence": [{"reference": "ARO:3000376", "snippet": "vgb (Virginiamycin B) lyase inactivates type B streptogramin antibiotics by linearizing the streptogramin lactone ring at the ester linkage through an elimination mechanism, thus conferring resistance to these compounds.",
                               "notes": "'through an elimination mechanism' -- CARD names the reaction type, not just the outcome."}]},
                {"subject": "lyase", "object": "linearized",
                 "predicate": "causally upstream of (inactivates the drug)",
                 "predicate_id": "RO:0002411",
                 "evidence": [{"reference": "ARO:3000376", "snippet": "vgb (Virginiamycin B) lyase inactivates type B streptogramin antibiotics by linearizing the streptogramin lactone ring at the ester linkage through an elimination mechanism, thus conferring resistance to these compounds.",
                               "notes": "'thus conferring resistance to these compounds'."}]},
            ],
        },
    ],
    # ---------------------------------------------------------------------------------
    # Rifampin ADP-ribosyltransferases (arr) -- inactivation by chemical modification.
    #
    # Keyed on ARO:3000576 but covering ONLY its ADP-ribosylating members; the family
    # also holds hydroxylases, glycosyltransferases and phosphotransferases, which do the
    # same job by different chemistry.
    "ARO:3000576": {
        "curated": "2026-08-07T00:00:00Z",
        "precondition": _requires_adp_ribosyltransferase,
        "reference": "ARO:3000266",
        "mech": {
            "ARO:0001004": "Enzymes that inactivate rifampin antibiotics by chemical modification.",
            "ARO:3000266": "The inactivation of antibiotics by the enzymatic addition of ADP-ribose from NAD+.",
        },
        "mech_res": "The inactivation of antibiotics by the enzymatic addition of ADP-ribose from NAD+.",
        "det_res": [
            {"reference": "ARO:3000266", "snippet": "The inactivation of antibiotics by the enzymatic addition of ADP-ribose from NAD+.",
             "notes": "The reaction: ADP-ribose is transferred from NAD+ onto the drug."},
            {"reference": "ARO:3000576", "snippet": "Enzymes that inactivate rifampin antibiotics by chemical modification.",
             "notes": "And what it achieves. SCOPE: this family sentence covers hydroxylation, glycosylation and phosphorylation too -- only the ADP-ribosylating members are curated by this config."},
        ],
        "res_drug": "Enzymes that inactivate rifampin antibiotics by chemical modification.",
        "note": "Inactivation by chemical modification. Only the arr/ADP-ribosylating subset of ARO:3000576.",
        "extra_nodes": [
            {"node_id": "adp_ribosylation", "label": "ADP-ribosyltransferase activity on rifampin",
             "node_type": "MOLECULAR_FUNCTION",
             "description": "Ungrounded: a rifampin-specific ADP-ribosyltransferase, not looked up rather than guessed (rounds 56-60)."},
            {"node_id": "nad", "label": "NAD+ (the ADP-ribose donor)",
             "node_type": "CHEMICAL", "grounding": "CHEBI:15846"},
            {"node_id": "modified", "label": "ADP-ribosylated, inactive rifampin",
             "node_type": "STATE",
             "description": "The product state. Ungrounded."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "adp_ribosylation",
             "predicate": "enables (ADP-ribosylates the drug)", "predicate_id": "RO:0002327",
             "evidence": [{"reference": "ARO:3000266", "snippet": "The inactivation of antibiotics by the enzymatic addition of ADP-ribose from NAD+.",
                           "notes": "'the enzymatic addition of ADP-ribose'."}]},
            {"subject": "adp_ribosylation", "object": "nad",
             "predicate": "has input (the ADP-ribose donor)", "predicate_id": "RO:0002233",
             "evidence": [{"reference": "ARO:3000266", "snippet": "The inactivation of antibiotics by the enzymatic addition of ADP-ribose from NAD+.",
                           "notes": "'from NAD+' -- the cosubstrate, which is what makes this a transferase rather than a hydrolase."}]},
            {"subject": "adp_ribosylation", "object": "drug0",
             "predicate": "has input (the drug)", "predicate_id": "RO:0002233",
             "evidence": [{"reference": "ARO:3000266", "snippet": "The inactivation of antibiotics by the enzymatic addition of ADP-ribose from NAD+.",
                           "notes": "The antibiotic is the acceptor, which is what makes this inactivation rather than target alteration."}]},
            {"subject": "adp_ribosylation", "object": "modified",
             "predicate": "causally upstream of (inactivates the drug)",
             "predicate_id": "RO:0002411",
             "description": "The causal core.",
             "evidence": [{"reference": "ARO:3000266", "snippet": "The inactivation of antibiotics by the enzymatic addition of ADP-ribose from NAD+.",
                           "notes": "'The inactivation of antibiotics by...' -- CARD names the outcome in the same sentence as the chemistry."}]},
        ],
    },
    # ---------------------------------------------------------------------------------
    # Antibiotic resistant DNA topoisomerase subunits (ARO:3000370).
    #
    # CARD's parent term states the mechanism in one sentence, and it is a DIFFERENT
    # sentence from rounds 18-19's: there the fluoroquinolone traps the cleavage complex;
    # here resistance is simply that the drug can no longer BIND the subunit. Most of
    # these records are aminocoumarin resistance, which acts at the ATPase site.
    "ARO:3000370": {
        "curated": "2026-08-07T00:00:00Z",
        "precondition": _requires_topoisomerase_subunit,
        "reference": "ARO:3000370",
        "mech": {"ARO:3000212": "Many drugs target topoisomerases to inhibit DNA synthesis. Resistant DNA topoisomerase subunits prevent antibiotic binding and thus confer resistance."},
        "mech_res": "Many drugs target topoisomerases to inhibit DNA synthesis. Resistant DNA topoisomerase subunits prevent antibiotic binding and thus confer resistance.",
        "det_res": [
            {"reference": "ARO:3000370", "snippet": "Many drugs target topoisomerases to inhibit DNA synthesis. Resistant DNA topoisomerase subunits prevent antibiotic binding and thus confer resistance.",
             "notes": "Both halves in one sentence: drugs target topoisomerases, and a resistant subunit prevents binding."},
            {"reference": "ARO:3000479", "snippet": "Point mutations in DNA gyrase subunit B (gyrB) can result in resistance to aminocoumarins. These mutations usually involve arginine residues in organisms.",
             "notes": "The worked case. SCOPE: gyrB and aminocoumarins specifically -- the family also covers parE and parY, which this sentence does not name."},
        ],
        "res_drug": "Many drugs target topoisomerases to inhibit DNA synthesis. Resistant DNA topoisomerase subunits prevent antibiotic binding and thus confer resistance.",
        "note": "Target alteration by loss of drug binding. Distinct from rounds 18-19, where the fluoroquinolone traps the cleavage complex.",
        "extra_nodes": [
            {"node_id": "binding_loss", "label": "loss of antibiotic binding to the mutated subunit",
             "node_type": "STATE",
             "description": "The causal core, in CARD's own words. Ungrounded."},
            {"node_id": "dna_synth", "label": "DNA biosynthetic process",
             "node_type": "BIOLOGICAL_PROCESS", "grounding": "GO:0071897"},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "binding_loss",
             "predicate": "has quality (prevents antibiotic binding)",
             "predicate_id": "RO:0000086",
             "evidence": [{"reference": "ARO:3000370", "snippet": "Many drugs target topoisomerases to inhibit DNA synthesis. Resistant DNA topoisomerase subunits prevent antibiotic binding and thus confer resistance.",
                           "notes": "'Resistant DNA topoisomerase subunits prevent antibiotic binding'."}]},
            {"subject": "drug0", "object": "dna_synth",
             "predicate": "negatively regulates (inhibits DNA synthesis)",
             "predicate_id": "RO:0002212",
             "description": "What the drug does when it CAN bind, and therefore what resistance restores.",
             "evidence": [{"reference": "ARO:3000370", "snippet": "Many drugs target topoisomerases to inhibit DNA synthesis. Resistant DNA topoisomerase subunits prevent antibiotic binding and thus confer resistance.",
                           "notes": "'Many drugs target topoisomerases to inhibit DNA synthesis'."}]},
            {"subject": "binding_loss", "object": "dna_synth",
             "predicate": "causally upstream of (DNA synthesis continues)",
             "predicate_id": "RO:0002411",
             "description": "Why the loss of binding is the resistance: synthesis is no longer inhibited.",
             "evidence": [{"reference": "ARO:3000370", "snippet": "Many drugs target topoisomerases to inhibit DNA synthesis. Resistant DNA topoisomerase subunits prevent antibiotic binding and thus confer resistance.",
                           "notes": "'and thus confer resistance' -- CARD's own 'thus' is the causal link."}]},
        ],
    },
    # ---------------------------------------------------------------------------------
    # Tetracycline inactivation by hydroxylation (ARO:3000036).
    #
    # CARD's parent term states the mechanism AND why it confers resistance, in two
    # sentences -- round 51's lesson, so no search was needed.
    "ARO:3000036": {
        "curated": "2026-08-07T00:00:00Z",
        "precondition": _requires_tet_hydroxylase,
        "reference": "ARO:3000036",
        "mech": {
            "ARO:0001004": "Enzymes or other gene products which hydroxylate tetracycline and other tetracycline derivatives. Hydroxylation inactivates tetracycline-like antibiotics, thus conferring resistance to these compounds.",
            "ARO:3000450": "Enzymes or other gene products which hydroxylate tetracycline and other tetracycline derivatives. Hydroxylation inactivates tetracycline-like antibiotics, thus conferring resistance to these compounds.",
        },
        "mech_res": "Enzymes or other gene products which hydroxylate tetracycline and other tetracycline derivatives. Hydroxylation inactivates tetracycline-like antibiotics, thus conferring resistance to these compounds.",
        "det_res": [
            {"reference": "ARO:3000036", "snippet": "Enzymes or other gene products which hydroxylate tetracycline and other tetracycline derivatives. Hydroxylation inactivates tetracycline-like antibiotics, thus conferring resistance to these compounds.",
             "notes": "CARD states both halves: what the enzyme does, and that doing it inactivates the drug."},
        ],
        "res_drug": "Enzymes or other gene products which hydroxylate tetracycline and other tetracycline derivatives. Hydroxylation inactivates tetracycline-like antibiotics, thus conferring resistance to these compounds.",
        "note": "Inactivation by chemical modification -- the drug is destroyed, not evaded.",
        "extra_nodes": [
            {"node_id": "hydroxylation", "label": "hydroxylation of tetracycline",
             "node_type": "MOLECULAR_FUNCTION",
             "description": "Ungrounded: a tetracycline-specific monooxygenase activity, not looked up this round rather than guessed (rounds 56-59)."},
            {"node_id": "inactivated", "label": "hydroxylated, inactive tetracycline",
             "node_type": "STATE",
             "description": "The product state. Ungrounded."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "hydroxylation",
             "predicate": "enables (hydroxylates the drug)", "predicate_id": "RO:0002327",
             "evidence": [{"reference": "ARO:3000036", "snippet": "Enzymes or other gene products which hydroxylate tetracycline and other tetracycline derivatives. Hydroxylation inactivates tetracycline-like antibiotics, thus conferring resistance to these compounds.",
                           "notes": "'Enzymes or other gene products which hydroxylate tetracycline'."}]},
            {"subject": "hydroxylation", "object": "drug0",
             "predicate": "has input (the drug)", "predicate_id": "RO:0002233",
             "evidence": [{"reference": "ARO:3000036", "snippet": "Enzymes or other gene products which hydroxylate tetracycline and other tetracycline derivatives. Hydroxylation inactivates tetracycline-like antibiotics, thus conferring resistance to these compounds.",
                           "notes": "The substrate is the antibiotic itself, which is what makes this inactivation rather than target alteration."}]},
            {"subject": "hydroxylation", "object": "inactivated",
             "predicate": "causally upstream of (inactivates the drug)",
             "predicate_id": "RO:0002411",
             "description": "The causal core, in CARD's own words.",
             "evidence": [{"reference": "ARO:3000036", "snippet": "Enzymes or other gene products which hydroxylate tetracycline and other tetracycline derivatives. Hydroxylation inactivates tetracycline-like antibiotics, thus conferring resistance to these compounds.",
                           "notes": "'Hydroxylation inactivates tetracycline-like antibiotics, thus conferring resistance'."}]},
        ],
    },
    # ---------------------------------------------------------------------------------
    # Class D beta-lactamases (ARO:3000075) -- inactivation by serine hydrolysis.
    #
    # Rounds 12-16 curated class A (KPC, TEM) with PROSITE:PS00146, the class-A-specific
    # active-site signature. That motif MUST NOT be reused here: it is class A's, and
    # citing it for class D would be exactly the borrowed-evidence defect in #196.
    #
    # PROSITE:PS00337 is the right record, and unusually its own definition NAMES class D
    # ("class -A, C and D enzymes are serine hydrolases"), so the membership claim rests on
    # the source saying so rather than on my inference.
    #
    # NOT asserted: the carbamylated-lysine general base that distinguishes class D
    # chemistry from class A. It is real, it is what makes OXA enzymes interesting, and no
    # source read this round states it. Round 58's lesson -- the claim I know best is the
    # one most likely to arrive uncited.
    "ARO:3000075": {
        "curated": "2026-08-07T00:00:00Z",
        "precondition": _requires_class_d,
        "reference": "PROSITE:PS00337",
        "mech": {
            "ARO:0001004": "Beta-lactamases classes -A, -C, and -D active site. Beta-lactamases (EC 3.5.2.6) are enzymes which catalyze the hydrolysis of an amide bond in the beta-lactam ring of antibiotics belonging to the penicillin/cephalosporin family. Four kinds of beta-lactamase have been identified. Class-B enzymes are zinc containing proteins whilst class -A, C and D enzymes are serine hydrolases. The three classes of serine beta- lactamases are evolutionary related and belong to a superfamily that also includes DD-peptidases and a variety of other penicillin-binding proteins (PBP's). All these proteins contain a Ser-x-x-Lys motif, where the serine is the active site residue.",
            "ARO:3000187": "Beta-lactamases classes -A, -C, and -D active site. Beta-lactamases (EC 3.5.2.6) are enzymes which catalyze the hydrolysis of an amide bond in the beta-lactam ring of antibiotics belonging to the penicillin/cephalosporin family. Four kinds of beta-lactamase have been identified. Class-B enzymes are zinc containing proteins whilst class -A, C and D enzymes are serine hydrolases. The three classes of serine beta- lactamases are evolutionary related and belong to a superfamily that also includes DD-peptidases and a variety of other penicillin-binding proteins (PBP's). All these proteins contain a Ser-x-x-Lys motif, where the serine is the active site residue.",
        },
        "mech_res": "Beta-lactamases classes -A, -C, and -D active site. Beta-lactamases (EC 3.5.2.6) are enzymes which catalyze the hydrolysis of an amide bond in the beta-lactam ring of antibiotics belonging to the penicillin/cephalosporin family. Four kinds of beta-lactamase have been identified. Class-B enzymes are zinc containing proteins whilst class -A, C and D enzymes are serine hydrolases. The three classes of serine beta- lactamases are evolutionary related and belong to a superfamily that also includes DD-peptidases and a variety of other penicillin-binding proteins (PBP's). All these proteins contain a Ser-x-x-Lys motif, where the serine is the active site residue.",
        "det_res": [
            {"reference": "PROSITE:PS00337", "snippet": "Class-B enzymes are zinc containing proteins whilst class -A, C and D enzymes are serine hydrolases.",
             "notes": "PROSITE names class D as a SERINE hydrolase -- which is why the serine mechanism applies to these records and the class B zinc mechanism does not."},
            {"reference": "PROSITE:PS00337", "snippet": "Beta-lactamases classes -A, -C, and -D active site. Beta-lactamases (EC 3.5.2.6) are enzymes which catalyze the hydrolysis of an amide bond in the beta-lactam ring of antibiotics belonging to the penicillin/cephalosporin family. Four kinds of beta-lactamase have been identified. Class-B enzymes are zinc containing proteins whilst class -A, C and D enzymes are serine hydrolases. The three classes of serine beta- lactamases are evolutionary related and belong to a superfamily that also includes DD-peptidases and a variety of other penicillin-binding proteins (PBP's). All these proteins contain a Ser-x-x-Lys motif, where the serine is the active site residue.",
             "notes": "And the reaction itself."},
        ],
        "res_drug": "Beta-lactamases classes -A, -C, and -D active site. Beta-lactamases (EC 3.5.2.6) are enzymes which catalyze the hydrolysis of an amide bond in the beta-lactam ring of antibiotics belonging to the penicillin/cephalosporin family. Four kinds of beta-lactamase have been identified. Class-B enzymes are zinc containing proteins whilst class -A, C and D enzymes are serine hydrolases. The three classes of serine beta- lactamases are evolutionary related and belong to a superfamily that also includes DD-peptidases and a variety of other penicillin-binding proteins (PBP's). All these proteins contain a Ser-x-x-Lys motif, where the serine is the active site residue.",
        "note": ("Serine hydrolysis. Deliberately NOT the carbamylated-lysine general-base "
                 "chemistry specific to class D -- no source read this round states it."),
        "protein_traits": {
            "active_site": ("PROSITE:PS00337",
                            "beta-lactamase class A/C/D active-site signature (S-x-x-K)",
                            "MOTIF",
                            "All these proteins contain a Ser-x-x-Lys motif, where the serine is the active site residue."),
            "enables_mech": "ARO:3000187",
        },
        "extra_nodes": [
            {"node_id": "amide", "label": "amide bond of the beta-lactam ring",
             "node_type": "CHEMICAL",
             "description": "Ungrounded: the specific bond, not the drug class. Not guessing a CHEBI id (rounds 56-58)."},
        ],
        "extra_edges": [
            {"subject": "mech0", "object": "amide",
             "predicate": "has input (the beta-lactam amide bond)", "predicate_id": "RO:0002233",
             "description": "What the hydrolysis acts on -- the bond whose cleavage destroys the drug.",
             "evidence": [{"reference": "PROSITE:PS00337", "snippet": "Beta-lactamases classes -A, -C, and -D active site. Beta-lactamases (EC 3.5.2.6) are enzymes which catalyze the hydrolysis of an amide bond in the beta-lactam ring of antibiotics belonging to the penicillin/cephalosporin family. Four kinds of beta-lactamase have been identified. Class-B enzymes are zinc containing proteins whilst class -A, C and D enzymes are serine hydrolases. The three classes of serine beta- lactamases are evolutionary related and belong to a superfamily that also includes DD-peptidases and a variety of other penicillin-binding proteins (PBP's). All these proteins contain a Ser-x-x-Lys motif, where the serine is the active site residue.",
                           "notes": "'catalyze the hydrolysis of an amide bond in the beta-lactam ring'."}]},
        ],
    },
    # ---------------------------------------------------------------------------------
    # bacA / bcrC -- undecaprenyl pyrophosphate recycling, bacitracin resistance.
    #
    # Two families, ONE config, because CARD describes one step two ways: BacA "recycles"
    # the carrier, BcrC is a "phosphatase" for it. First time in this thread two family
    # ids share a config dict outright.
    #
    # ARO:3000012 (molecular bypass) as a whole is NOT curatable with one config -- it
    # mixes UPP recycling, lipid A biosynthesis, non-functional ddl ligases and the van
    # clusters. Asserting one mechanism across it would be round 22's error again.
    "ARO:3002986": {
        "curated": "2026-08-07T00:00:00Z",
        "precondition": _requires_upp_recycler,
        "reference": "ARO:3002986",
        "mech": {"ARO:3000213": "The bacA gene product (BacA) recycles undecaprenyl pyrophosphate during cell wall biosynthesis which confers resistance to bacitracin."},
        "mech_res": "The bacA gene product (BacA) recycles undecaprenyl pyrophosphate during cell wall biosynthesis which confers resistance to bacitracin.",
        "det_res": [
            {"reference": "ARO:3002986", "snippet": "The bacA gene product (BacA) recycles undecaprenyl pyrophosphate during cell wall biosynthesis which confers resistance to bacitracin.",
             "notes": "BacA: recycling undecaprenyl pyrophosphate confers bacitracin resistance."},
            {"reference": "ARO:3003250", "snippet": "The bcrC gene product (BcrC) is an undecaprenyl pyrophosphate phosphatase originally isolated from Bacillus subtilis. When overexpressed it can confer resistance to bacitracin.",
             "notes": "BcrC: the same carrier, as a phosphatase, and resistance on OVEREXPRESSION -- more recycling capacity, not a different activity."},
        ],
        "res_drug": "The bacA gene product (BacA) recycles undecaprenyl pyrophosphate during cell wall biosynthesis which confers resistance to bacitracin.",
        "note": ("Undecaprenyl pyrophosphate recycling. NOT asserted: that bacitracin binds "
                 "or sequesters undecaprenyl pyrophosphate. That is the textbook mode of "
                 "action and neither CARD definition states it, so the drug->carrier edge "
                 "is deliberately absent (round 51's lesson). Adding it needs its own "
                 "evidence."),
        "extra_nodes": [
            {"node_id": "upp", "label": "undecaprenyl pyrophosphate (the lipid carrier)",
             "node_type": "CHEMICAL",
             "description": "Ungrounded: no CHEBI id verified this round, and rounds 56-57 established not guessing one."},
            {"node_id": "recycling", "label": "undecaprenyl pyrophosphate recycling / dephosphorylation",
             "node_type": "MOLECULAR_FUNCTION",
             "description": "Ungrounded: BacA's recycling and BcrC's phosphatase activity are the same step described two ways."},
            {"node_id": "wall", "label": "peptidoglycan biosynthetic process",
             "node_type": "BIOLOGICAL_PROCESS", "grounding": "GO:0009252"},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "recycling",
             "predicate": "enables (recycles the lipid carrier)", "predicate_id": "RO:0002327",
             "evidence": [
                 {"reference": "ARO:3002986", "snippet": "The bacA gene product (BacA) recycles undecaprenyl pyrophosphate during cell wall biosynthesis which confers resistance to bacitracin.",
                  "notes": "BacA 'recycles undecaprenyl pyrophosphate'."},
                 {"reference": "ARO:3003250", "snippet": "The bcrC gene product (BcrC) is an undecaprenyl pyrophosphate phosphatase originally isolated from Bacillus subtilis. When overexpressed it can confer resistance to bacitracin.",
                  "notes": "BcrC is 'an undecaprenyl pyrophosphate phosphatase' -- the same step."}]},
            {"subject": "recycling", "object": "upp",
             "predicate": "has input (the lipid carrier)", "predicate_id": "RO:0002233",
             "evidence": [{"reference": "ARO:3002986", "snippet": "The bacA gene product (BacA) recycles undecaprenyl pyrophosphate during cell wall biosynthesis which confers resistance to bacitracin.",
                           "notes": "The substrate CARD names."}]},
            {"subject": "recycling", "object": "wall",
             "predicate": "part of (cell wall biosynthesis)", "predicate_id": "BFO:0000050",
             "evidence": [{"reference": "ARO:3002986", "snippet": "The bacA gene product (BacA) recycles undecaprenyl pyrophosphate during cell wall biosynthesis which confers resistance to bacitracin.",
                           "notes": "'during cell wall biosynthesis'."}]},
        ],
    },
    "ARO:3003250": {
        "curated": "2026-08-07T00:00:00Z",
        "precondition": _requires_upp_recycler,
        "reference": "ARO:3002986",
        "mech": {"ARO:3000213": "The bacA gene product (BacA) recycles undecaprenyl pyrophosphate during cell wall biosynthesis which confers resistance to bacitracin."},
        "mech_res": "The bacA gene product (BacA) recycles undecaprenyl pyrophosphate during cell wall biosynthesis which confers resistance to bacitracin.",
        "det_res": [
            {"reference": "ARO:3002986", "snippet": "The bacA gene product (BacA) recycles undecaprenyl pyrophosphate during cell wall biosynthesis which confers resistance to bacitracin.",
             "notes": "BacA: recycling undecaprenyl pyrophosphate confers bacitracin resistance."},
            {"reference": "ARO:3003250", "snippet": "The bcrC gene product (BcrC) is an undecaprenyl pyrophosphate phosphatase originally isolated from Bacillus subtilis. When overexpressed it can confer resistance to bacitracin.",
             "notes": "BcrC: the same carrier, as a phosphatase, and resistance on OVEREXPRESSION -- more recycling capacity, not a different activity."},
        ],
        "res_drug": "The bacA gene product (BacA) recycles undecaprenyl pyrophosphate during cell wall biosynthesis which confers resistance to bacitracin.",
        "note": ("Undecaprenyl pyrophosphate recycling. NOT asserted: that bacitracin binds "
                 "or sequesters undecaprenyl pyrophosphate. That is the textbook mode of "
                 "action and neither CARD definition states it, so the drug->carrier edge "
                 "is deliberately absent (round 51's lesson). Adding it needs its own "
                 "evidence."),
        "extra_nodes": [
            {"node_id": "upp", "label": "undecaprenyl pyrophosphate (the lipid carrier)",
             "node_type": "CHEMICAL",
             "description": "Ungrounded: no CHEBI id verified this round, and rounds 56-57 established not guessing one."},
            {"node_id": "recycling", "label": "undecaprenyl pyrophosphate recycling / dephosphorylation",
             "node_type": "MOLECULAR_FUNCTION",
             "description": "Ungrounded: BacA's recycling and BcrC's phosphatase activity are the same step described two ways."},
            {"node_id": "wall", "label": "peptidoglycan biosynthetic process",
             "node_type": "BIOLOGICAL_PROCESS", "grounding": "GO:0009252"},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "recycling",
             "predicate": "enables (recycles the lipid carrier)", "predicate_id": "RO:0002327",
             "evidence": [
                 {"reference": "ARO:3002986", "snippet": "The bacA gene product (BacA) recycles undecaprenyl pyrophosphate during cell wall biosynthesis which confers resistance to bacitracin.",
                  "notes": "BacA 'recycles undecaprenyl pyrophosphate'."},
                 {"reference": "ARO:3003250", "snippet": "The bcrC gene product (BcrC) is an undecaprenyl pyrophosphate phosphatase originally isolated from Bacillus subtilis. When overexpressed it can confer resistance to bacitracin.",
                  "notes": "BcrC is 'an undecaprenyl pyrophosphate phosphatase' -- the same step."}]},
            {"subject": "recycling", "object": "upp",
             "predicate": "has input (the lipid carrier)", "predicate_id": "RO:0002233",
             "evidence": [{"reference": "ARO:3002986", "snippet": "The bacA gene product (BacA) recycles undecaprenyl pyrophosphate during cell wall biosynthesis which confers resistance to bacitracin.",
                           "notes": "The substrate CARD names."}]},
            {"subject": "recycling", "object": "wall",
             "predicate": "part of (cell wall biosynthesis)", "predicate_id": "BFO:0000050",
             "evidence": [{"reference": "ARO:3002986", "snippet": "The bacA gene product (BacA) recycles undecaprenyl pyrophosphate during cell wall biosynthesis which confers resistance to bacitracin.",
                           "notes": "'during cell wall biosynthesis'."}]},
        ],
    },
    # ---------------------------------------------------------------------------------
    # ndh (ARO:3003460) -- prodrug-activation loss by an INDIRECT route.
    #
    # Round 56's pncA loses the activating enzyme itself. ndh loses nothing of the sort:
    # it is a NADH oxidase, and its mutation shifts the NADH/NAD+ RATIO, which then blocks
    # isoniazid activation two steps downstream. Same family of mechanism, different
    # causal distance -- which is why it gets its own config rather than reusing pncA's.
    #
    # CARD carries the entire chain, including BOTH arms, in one sentence.
    "ARO:3003460": {
        "curated": "2026-08-07T00:00:00Z",
        "precondition": _requires_ndh,
        "reference": "ARO:3003460",
        "mech": {"ARO:3000212": "ndh is a NADH oxidase. It participates in antibiotic resistance by diminishing NADH oxidation and consequently causes an increase in NADH concentration and depletion of NAD+. This alteration of the NADH/NAD+ ratio prevents the peroxidation reactions required for the activation of INH, as well as the displacement of the NADH-isonicotinic acyl complex from InhA enzyme binding site."},
        "mech_res": "Point mutations in the Mycobacterium tuberculosis ndh gene shown clinically to confer resistance to isoniazid.",
        "det_res": [
            {"reference": "ARO:3003461", "snippet": "Point mutations in the Mycobacterium tuberculosis ndh gene shown clinically to confer resistance to isoniazid.",
             "notes": "The clinical resistance claim."},
            {"reference": "ARO:3003460", "snippet": "ndh is a NADH oxidase. It participates in antibiotic resistance by diminishing NADH oxidation and consequently causes an increase in NADH concentration and depletion of NAD+. This alteration of the NADH/NAD+ ratio prevents the peroxidation reactions required for the activation of INH, as well as the displacement of the NADH-isonicotinic acyl complex from InhA enzyme binding site.",
             "notes": "And the full mechanism, which CARD states in a single sentence: diminished NADH oxidation -> altered NADH/NAD+ ratio -> two separate blocks on isoniazid."},
        ],
        "res_drug": "Point mutations in the Mycobacterium tuberculosis ndh gene shown clinically to confer resistance to isoniazid.",
        "note": "Prodrug-activation loss at a distance: the ratio changes, and INH activation fails downstream.",
        "extra_nodes": [
            {"node_id": "nadh_ox", "label": "NADH oxidase activity of ndh",
             "node_type": "MOLECULAR_FUNCTION",
             "description": "Ungrounded on purpose: CARD says 'NADH oxidase', and the nearest GO terms are NADH dehydrogenase activities. Round 56's rule -- do not guess a CURIE that was not verified."},
            {"node_id": "ratio", "label": "raised NADH / depleted NAD+ ratio",
             "node_type": "STATE",
             "description": "The causal hinge. Both downstream arms hang off this one state."},
            {"node_id": "peroxidation", "label": "peroxidation reactions required for isoniazid activation",
             "node_type": "BIOLOGICAL_PROCESS",
             "description": "Ungrounded: the KatG-mediated activation chemistry has no single term in use here."},
            {"node_id": "displacement", "label": "displacement of the NADH-isonicotinic acyl complex from the InhA binding site",
             "node_type": "STATE",
             "description": "The second, independent arm."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "nadh_ox",
             "predicate": "negatively regulates (diminishes NADH oxidation)",
             "predicate_id": "RO:0002212",
             "evidence": [{"reference": "ARO:3003460", "snippet": "ndh is a NADH oxidase. It participates in antibiotic resistance by diminishing NADH oxidation and consequently causes an increase in NADH concentration and depletion of NAD+. This alteration of the NADH/NAD+ ratio prevents the peroxidation reactions required for the activation of INH, as well as the displacement of the NADH-isonicotinic acyl complex from InhA enzyme binding site.",
                           "notes": "'participates in antibiotic resistance by diminishing NADH oxidation'."}]},
            {"subject": "nadh_ox", "object": "ratio",
             "predicate": "causally upstream of (raises NADH, depletes NAD+)",
             "predicate_id": "RO:0002411",
             "evidence": [{"reference": "ARO:3003460", "snippet": "ndh is a NADH oxidase. It participates in antibiotic resistance by diminishing NADH oxidation and consequently causes an increase in NADH concentration and depletion of NAD+. This alteration of the NADH/NAD+ ratio prevents the peroxidation reactions required for the activation of INH, as well as the displacement of the NADH-isonicotinic acyl complex from InhA enzyme binding site.",
                           "notes": "'consequently causes an increase in NADH concentration and depletion of NAD+'."}]},
            {"subject": "ratio", "object": "peroxidation",
             "predicate": "negatively regulates (prevents the activating chemistry)",
             "predicate_id": "RO:0002212",
             "description": "First arm: isoniazid is never activated.",
             "evidence": [{"reference": "ARO:3003460", "snippet": "ndh is a NADH oxidase. It participates in antibiotic resistance by diminishing NADH oxidation and consequently causes an increase in NADH concentration and depletion of NAD+. This alteration of the NADH/NAD+ ratio prevents the peroxidation reactions required for the activation of INH, as well as the displacement of the NADH-isonicotinic acyl complex from InhA enzyme binding site.",
                           "notes": "'prevents the peroxidation reactions required for the activation of INH'."}]},
            {"subject": "ratio", "object": "displacement",
             "predicate": "negatively regulates (prevents the displacement)",
             "predicate_id": "RO:0002212",
             "description": "Second arm, independent of the first. CARD's 'as well as' is doing real work -- these are two mechanisms, not one restated, and splitting them is why this config has four extra edges rather than three.",
             "evidence": [{"reference": "ARO:3003460", "snippet": "ndh is a NADH oxidase. It participates in antibiotic resistance by diminishing NADH oxidation and consequently causes an increase in NADH concentration and depletion of NAD+. This alteration of the NADH/NAD+ ratio prevents the peroxidation reactions required for the activation of INH, as well as the displacement of the NADH-isonicotinic acyl complex from InhA enzyme binding site.",
                           "notes": "'as well as the displacement of the NADH-isonicotinic acyl complex from InhA enzyme binding site'."}]},
        ],
    },
    # ---------------------------------------------------------------------------------
    # pncA (ARO:3004267) -- PRODRUG-ACTIVATION LOSS. Resistance by LOSING a function.
    #
    # Every other mechanism curated in this thread works by the determinant DOING
    # something: destroying the drug, rebuilding a precursor, pumping, replacing a target.
    # Here resistance is the absence of an activity the susceptible cell has. Pyrazinamide
    # is a prodrug; without pyrazinamidase it is never converted to pyrazinoic acid, so the
    # drug is inert rather than defeated.
    #
    # That inverts the usual edge direction, and it is why the core edge below points from
    # the LOSS to the activity rather than from the determinant to the drug.
    #
    # CARD states the whole chain again (round 51's lesson, fourth round running).
    "ARO:3004267": {
        "curated": "2026-08-07T00:00:00Z",
        "precondition": _requires_pnca,
        "reference": "ARO:3004267",
        "mech": {"ARO:3000212": "Point mutations in pncA prevent the enzyme from activating antibiotics, such as pyrazinamide."},
        "mech_res": "Point mutations in pncA prevent the enzyme from activating antibiotics, such as pyrazinamide.",
        "det_res": [
            {"reference": "ARO:3004267", "snippet": "Point mutations in pncA prevent the enzyme from activating antibiotics, such as pyrazinamide.",
             "notes": "The mechanism in one sentence: the mutation PREVENTS activation."},
            {"reference": "ARO:3003418", "snippet": "pncA is a pyrazinamidase/nicotinamidase. It catalyzes the activation of pyrazinamide to pyrazinoic acid. Mutations arise within the pncA gene that caused the loss of pyrazinamidase activity is the major mechanism of antibiotic resistance.",
             "notes": "And the chemistry it prevents -- pyrazinamide to pyrazinoic acid -- plus CARD calling loss of pyrazinamidase activity 'the major mechanism'."},
        ],
        "res_drug": "Point mutations in pncA prevent the enzyme from activating antibiotics, such as pyrazinamide.",
        "note": "Prodrug-activation loss. Resistance is the ABSENCE of an activity, not the presence of one.",
        "extra_nodes": [
            {"node_id": "pzase", "label": "pyrazinamidase / nicotinamidase activity",
             "node_type": "MOLECULAR_FUNCTION", "grounding": "GO:0008936",
             "description": "Grounded to nicotinamidase activity, the EC 3.5.1.19 function CARD names for pncA; checked non-obsolete against OLS."},
            {"node_id": "loss", "label": "loss of pyrazinamidase activity",
             "node_type": "STATE",
             "description": "The causal core, and the reason this graph runs backwards relative to the other mechanisms here. Ungrounded."},
            {"node_id": "poa", "label": "pyrazinoic acid (the active drug)",
             "node_type": "CHEMICAL",
             "description": "Ungrounded deliberately: the active metabolite is not the drug class node, and guessing a CHEBI id for it would be a grounding this round did not verify."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "loss",
             "predicate": "has quality (loss of pyrazinamidase activity)",
             "predicate_id": "RO:0000086",
             "evidence": [{"reference": "ARO:3003394", "snippet": "Some mutation within pncA are associated with loss of enzyme activity, resulting in pyrazinamide resistance.",
                           "notes": "CARD ties the mutation to loss of enzyme activity explicitly."}]},
            {"subject": "loss", "object": "pzase",
             "predicate": "negatively regulates (abolishes the activating activity)",
             "predicate_id": "RO:0002212",
             "description": "The inverted core: resistance follows from the activity being ABSENT.",
             "evidence": [{"reference": "ARO:3003418", "snippet": "pncA is a pyrazinamidase/nicotinamidase. It catalyzes the activation of pyrazinamide to pyrazinoic acid. Mutations arise within the pncA gene that caused the loss of pyrazinamidase activity is the major mechanism of antibiotic resistance.",
                           "notes": "'loss of pyrazinamidase activity is the major mechanism of antibiotic resistance'."}]},
            {"subject": "pzase", "object": "drug0",
             "predicate": "has input (the prodrug)", "predicate_id": "RO:0002233",
             "evidence": [{"reference": "ARO:3003418", "snippet": "pncA is a pyrazinamidase/nicotinamidase. It catalyzes the activation of pyrazinamide to pyrazinoic acid. Mutations arise within the pncA gene that caused the loss of pyrazinamidase activity is the major mechanism of antibiotic resistance.",
                           "notes": "'It catalyzes the activation of pyrazinamide'. NOTE the drug0 node is the drug CLASS; the substrate is pyrazinamide specifically."}]},
            {"subject": "pzase", "object": "poa",
             "predicate": "has output (the active form)", "predicate_id": "RO:0002234",
             "description": "What resistance prevents from ever being made.",
             "evidence": [{"reference": "ARO:3003418", "snippet": "pncA is a pyrazinamidase/nicotinamidase. It catalyzes the activation of pyrazinamide to pyrazinoic acid. Mutations arise within the pncA gene that caused the loss of pyrazinamidase activity is the major mechanism of antibiotic resistance.",
                           "notes": "'the activation of pyrazinamide to pyrazinoic acid'."}]},
        ],
    },
    # ---------------------------------------------------------------------------------
    # 23S rRNA mutations (ARO:3000336) -- the non-macrolide remainder, after round 50.
    #
    # Round 50 curated the macrolide subset and needed a literature search to do it. The
    # rest needs none: CARD's parent term states the FULL chain -- what the drug does
    # (blocks peptidyl transferase), what the mutation does (reduces binding affinity),
    # and that this confers resistance. Round 51's lesson, third round running.
    "ARO:3000336": {
        "curated": "2026-08-07T00:00:00Z",
        "precondition": _requires_23s_rrna,
        "determinant_node_type": "NUCLEIC_ACID",
        "reference": "ARO:3000336",
        "mech": {"ARO:3000212": "Mutations in the 23S rRNA subunit reduce antibiotic binding affinity at specific sites, conferring resistance."},
        "mech_res": "Mutations in the 23S rRNA subunit reduce antibiotic binding affinity at specific sites, conferring resistance.",
        "det_res": [
            {"reference": "ARO:3000336", "snippet": "Point mutations in bacterial 23S rRNA from the large ribosomal subunit that confer resistance to antibiotics.",
             "notes": "CARD's parent term, stating the resistance claim for the family."},
            {"reference": "ARO:3000336", "snippet": "Mutations in the 23S rRNA subunit reduce antibiotic binding affinity at specific sites, conferring resistance.",
             "notes": "And the mechanism, with its direction: binding affinity is REDUCED, at specific sites."},
        ],
        "res_drug": "Mutations in the 23S rRNA subunit reduce antibiotic binding affinity at specific sites, conferring resistance.",
        "note": "Target alteration of an RNA target; the counterpart to round 54's 16S config.",
        "extra_nodes": [
            {"node_id": "binding_site", "label": "antibiotic-binding site within the 23S rRNA",
             "node_type": "NUCLEIC_ACID",
             "description": "Ungrounded: the per-drug site (domain V, the peptidyl transferase centre) has no single term."},
            {"node_id": "low_affinity", "label": "reduced antibiotic binding affinity at the mutated site",
             "node_type": "STATE",
             "description": "The causal core, in CARD's own words. Ungrounded: an affinity property has no term here."},
            {"node_id": "subunit", "label": "large ribosomal subunit (50S)",
             "node_type": "CELLULAR_LOCALIZATION", "grounding": "GO:0015934"},
            {"node_id": "pt_activity", "label": "peptidyl transferase activity",
             "node_type": "MOLECULAR_FUNCTION", "grounding": "GO:0000048"},
        ],
        "extra_edges": [
            {"subject": "binding_site", "object": "determinant",
             "predicate": "part of (the 23S rRNA)", "predicate_id": "BFO:0000050",
             "description": "Why a mutation in the rRNA IS a mutation in the drug's target -- the same shape as round 54's 16S config.",
             "evidence": [{"reference": "ARO:3000336", "snippet": "Mutations in the 23S rRNA subunit reduce antibiotic binding affinity at specific sites, conferring resistance.",
                           "notes": "'at specific sites' -- the sites are in the rRNA itself."}]},
            {"subject": "determinant", "object": "subunit",
             "predicate": "part of (the 50S subunit)", "predicate_id": "BFO:0000050",
             "evidence": [{"reference": "ARO:3000336", "snippet": "Point mutations in bacterial 23S rRNA from the large ribosomal subunit that confer resistance to antibiotics.",
                           "notes": "CARD places the 23S rRNA in the large ribosomal subunit."}]},
            {"subject": "determinant", "object": "low_affinity",
             "predicate": "has quality (reduced antibiotic binding affinity)",
             "predicate_id": "RO:0000086",
             "evidence": [
                 {"reference": "ARO:3000336", "snippet": "Mutations in the 23S rRNA subunit reduce antibiotic binding affinity at specific sites, conferring resistance.",
                  "notes": "The family-level claim."},
                 {"reference": "ARO:3004187", "snippet": "Point mutations in the 23S rRNA subunit may confer resistance to lincosamide antibiotics by reducing antibiotic binding-site affinity.",
                  "notes": "Restated for lincosamides -- 'by reducing antibiotic binding-site affinity' -- which shows the family claim is not linezolid-only."}]},
            {"subject": "low_affinity", "object": "binding_site",
             "predicate": "negatively regulates (drug occupancy of the site)",
             "predicate_id": "RO:0002212",
             "evidence": [{"reference": "ARO:3000336", "snippet": "Mutations in the 23S rRNA subunit reduce antibiotic binding affinity at specific sites, conferring resistance.",
                           "notes": "Reduced affinity means the drug occupies its site less."}]},
            {"subject": "drug0", "object": "pt_activity",
             "predicate": "negatively regulates (blocks peptide synthesis)",
             "predicate_id": "RO:0002212",
             "description": "What the drug does when it IS bound, and therefore what resistance restores.",
             "evidence": [{"reference": "ARO:3000336", "snippet": "Antibiotics such as linezolid block peptide synthesis through peptidyl transferase activity.",
                           "notes": "Stated for linezolid. SCOPE: this family also spans lincosamides, phenicols, pleuromutilins, streptogramins, aminoglycosides and capreomycin, which act at the same centre but are not named by this sentence."}]},
        ],
    },
    # ---------------------------------------------------------------------------------
    # 16S rRNA mutations (ARO:3003211) -- target alteration where the target is RNA.
    #
    # The counterpart to round 50's 23S macrolide config, and the same modelling choice:
    # determinant_node_type NUCLEIC_ACID, because the determinant is rRNA and calling it a
    # PROTEIN in a protein-traits KB would be false rather than merely awkward (#215).
    #
    # CARD carries the whole chain verbatim -- the general rule on the parent term and the
    # worked tetracycline case on ARO:3003499 -- so round 51's lesson holds again: read the
    # source before searching.
    "ARO:3003211": {
        "curated": "2026-08-07T00:00:00Z",
        "precondition": _requires_16s_rrna,
        "determinant_node_type": "NUCLEIC_ACID",
        "reference": "ARO:3003211",
        "mech": {"ARO:3000212": "The antibiotic-binding sites are located within functionally important structures in the ribosomal RNA. Antibiotic resistance is often conferred by base substitutions or methylations at these sites in the rRNA."},
        "mech_res": "Point mutations in the bacterial 16S ribosomal RNA in the small 30S subunit can confer resistance to antibiotics.",
        "det_res": [
            {"reference": "ARO:3003211", "snippet": "Point mutations in the bacterial 16S ribosomal RNA in the small 30S subunit can confer resistance to antibiotics.",
             "notes": "CARD's parent term, stating the resistance claim for the whole family."},
            {"reference": "ARO:3003211", "snippet": "The antibiotic-binding sites are located within functionally important structures in the ribosomal RNA. Antibiotic resistance is often conferred by base substitutions or methylations at these sites in the rRNA.",
             "notes": "And WHY it works: the drug's binding site is IN the rRNA, so a base substitution there changes the site itself."},
        ],
        "res_drug": "Point mutations in the bacterial 16S ribosomal RNA in the small 30S subunit can confer resistance to antibiotics.",
        "note": "Target alteration of an RNA target. The drug's binding site is the mutated structure.",
        "extra_nodes": [
            {"node_id": "binding_site", "label": "antibiotic-binding site within the 16S rRNA",
             "node_type": "NUCLEIC_ACID",
             "description": "Ungrounded: a per-drug rRNA binding site (helix 34, helix 44, the 3' major/minor domains) has no single term."},
            {"node_id": "subunit", "label": "small ribosomal subunit (30S)",
             "node_type": "CELLULAR_LOCALIZATION", "grounding": "GO:0015935"},
            {"node_id": "translation", "label": "translation",
             "node_type": "BIOLOGICAL_PROCESS", "grounding": "GO:0006412"},
        ],
        "extra_edges": [
            {"subject": "binding_site", "object": "determinant",
             "predicate": "part of (the 16S rRNA)", "predicate_id": "BFO:0000050",
             "description": "Why a mutation in the rRNA IS a mutation in the drug's target.",
             "evidence": [{"reference": "ARO:3003211", "snippet": "The antibiotic-binding sites are located within functionally important structures in the ribosomal RNA. Antibiotic resistance is often conferred by base substitutions or methylations at these sites in the rRNA.",
                           "notes": "'binding sites are located within functionally important structures in the ribosomal RNA'."}]},
            {"subject": "determinant", "object": "subunit",
             "predicate": "part of (the 30S subunit)", "predicate_id": "BFO:0000050",
             "evidence": [{"reference": "ARO:3003211", "snippet": "Point mutations in the bacterial 16S ribosomal RNA in the small 30S subunit can confer resistance to antibiotics.",
                           "notes": "CARD places the 16S rRNA in the small 30S subunit."}]},
            {"subject": "drug0", "object": "binding_site",
             "predicate": "molecularly interacts with (binds the rRNA site)",
             "predicate_id": "RO:0002436",
             "evidence": [{"reference": "ARO:3003499", "snippet": "Tetracycline binds tightly to the helix 34 domain in 16S rRNA, where it interferes sterically with the binding of aminoacyl-tRNA to the ribosome A site to block protein synthesis.",
                           "notes": "The worked case: tetracycline at helix 34. Quoted as the family's exemplar -- the other drugs here (pactamycin, edeine, viomycin) bind their own sites, which this snippet does not cover."}]},
            {"subject": "drug0", "object": "translation",
             "predicate": "negatively regulates (blocks protein synthesis)",
             "predicate_id": "RO:0002212",
             "description": "What the drug does once bound, and therefore what resistance restores.",
             "evidence": [{"reference": "ARO:3003499", "snippet": "Tetracycline binds tightly to the helix 34 domain in 16S rRNA, where it interferes sterically with the binding of aminoacyl-tRNA to the ribosome A site to block protein synthesis.",
                           "notes": "'interferes sterically with the binding of aminoacyl-tRNA to the ribosome A site to block protein synthesis'."}]},
        ],
    },
    # ---------------------------------------------------------------------------------
    # Mutant PBPs (ARO:3003040 / ARO:3003938) -- TARGET ALTERATION, the round 18-19 shape.
    #
    # The counterpart to round 52's target REPLACEMENT config on the same family term.
    # There the cell acquires a foreign low-affinity PBP; here the native PBP is mutated
    # until the drug binds it poorly. Round 52's precondition sends each record to the
    # right one, on the mechanism id the record itself carries.
    #
    # CARD states the mechanism verbatim again (round 51's lesson), so the literature is
    # needed only to show mutations actually produce the low-affinity protein.
    "ARO:3003040-mutation": {
        "curated": "2026-08-07T00:00:00Z",
        "precondition": _requires_mutant_pbp,
        "reference": "ARO:3003938",
        "mech": {"ARO:3000212": "Mutations in PBP transpeptidases that change the affinity for penicillin thereby conferring resistance to penicillin antibiotics."},
        "mech_res": "Mutations in PBP transpeptidases that change the affinity for penicillin thereby conferring resistance to penicillin antibiotics.",
        "det_res": [
            {"reference": "ARO:3003938", "snippet": "Mutations in PBP transpeptidases that change the affinity for penicillin thereby conferring resistance to penicillin antibiotics.",
             "notes": "CARD's parent term states the whole mechanism: mutation -> changed affinity -> resistance."},
            {"reference": "ARO:3004833", "snippet": "Point mutation in Neisseria gonorrhoea PBP1 (ponA) decreases affinity between beta-lactam antibiotic molecule and PBP1, thereby conferring resistance to beta-lactam antibiotics.",
             "notes": "And the DIRECTION, which the parent term leaves as 'change': the affinity DECREASES."},
        ],
        "res_drug": "Mutations in PBP transpeptidases that change the affinity for penicillin thereby conferring resistance to penicillin antibiotics.",
        "note": "Target alteration of a native PBP. Contrast round 52: no foreign protein is involved.",
        "extra_nodes": [
            {"node_id": "tp_activity", "label": "transpeptidase activity of the mutant PBP",
             "node_type": "MOLECULAR_FUNCTION", "grounding": "GO:0008658"},
            {"node_id": "low_affinity", "label": "decreased affinity of the mutant PBP for beta-lactams",
             "node_type": "STATE",
             "description": "The causal core. Ungrounded: an affinity property has no ontology term here."},
            {"node_id": "pg_synth", "label": "peptidoglycan biosynthetic process",
             "node_type": "BIOLOGICAL_PROCESS", "grounding": "GO:0009252"},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "low_affinity",
             "predicate": "has quality (decreased beta-lactam affinity)", "predicate_id": "RO:0000086",
             "description": "The mutation's effect on the target, stated by CARD with its direction.",
             "evidence": [
                 {"reference": "ARO:3004833", "snippet": "Point mutation in Neisseria gonorrhoea PBP1 (ponA) decreases affinity between beta-lactam antibiotic molecule and PBP1, thereby conferring resistance to beta-lactam antibiotics.",
                  "notes": "CARD gives the direction explicitly for the ponA case."},
                 {"reference": "PMID:1938899", "snippet": "Three PBP 2x regions were mutated in from two to all four mutants carrying a low-affinity PBP 2x.",
                  "notes": "Laible & Hakenbeck 1991 -- mutations in defined PBP2x regions actually produce the low-affinity protein. Studied S. pneumoniae PBP2x; the other species' PBPs are covered by CARD's family-level claim, not by this paper."}]},
            {"subject": "low_affinity", "object": "tp_activity",
             "predicate": "causally upstream of (leaves the transpeptidase uninhibited)",
             "predicate_id": "RO:0002411",
             "evidence": [{"reference": "ARO:3003938", "snippet": "Mutations in PBP transpeptidases that change the affinity for penicillin thereby conferring resistance to penicillin antibiotics.",
                           "notes": "Why the changed affinity confers resistance: the enzyme keeps working."}]},
            {"subject": "tp_activity", "object": "pg_synth",
             "predicate": "part of (peptidoglycan biosynthesis)", "predicate_id": "BFO:0000050",
             "evidence": [{"reference": "ARO:3003938", "snippet": "Mutations in PBP transpeptidases that change the affinity for penicillin thereby conferring resistance to penicillin antibiotics.",
                           "notes": "PBP transpeptidases cross-link the wall; this is the process the drug targets."}]},
        ],
    },
    # ---------------------------------------------------------------------------------
    # Beta-lactam resistant PBPs (ARO:3003040) -- TARGET REPLACEMENT, an 11th mechanism kind.
    #
    # Distinct from target ALTERATION (rounds 18-19, 51): nothing about the native target
    # changes. The cell ACQUIRES a foreign PBP whose affinity for the drug is so low that
    # wall synthesis simply continues while the native PBPs stay inhibited.
    #
    # Round 51's lesson applied first: CARD's own definitions state this mechanism verbatim
    # ("A foreign PBP2a acquired by lateral gene transfer that is able to perform
    # peptidoglycan synthesis in the presence of beta-lactams"), so no search was needed to
    # know WHAT to curate -- only to evidence the affinity claim.
    "ARO:3003040": {
        "curated": "2026-08-07T00:00:00Z",
        "precondition": _requires_replacement_pbp,
        "reference": "ARO:3000617",
        "mech": {"ARO:0001002": "A foreign PBP2a acquired by lateral gene transfer that is able to perform peptidoglycan synthesis in the presence of beta-lactams."},
        "mech_res": "A foreign PBP2a acquired by lateral gene transfer that is able to perform peptidoglycan synthesis in the presence of beta-lactams.",
        "det_res": [
            {"reference": "ARO:3000617", "snippet": "A foreign PBP2a acquired by lateral gene transfer that is able to perform peptidoglycan synthesis in the presence of beta-lactams.",
             "notes": "CARD states the mechanism in full: foreign, acquired, and functional under drug."},
            {"reference": "PMID:3499861", "snippet": "All strains produced penicillin-binding protein 2' (PBP 2'), which has been associated with methicillin resistance and which has very low affinity for beta-lactam antibiotics.",
             "notes": "The affinity measurement that makes it work -- 'very low affinity for beta-lactam antibiotics'."},
        ],
        "res_drug": "All strains produced penicillin-binding protein 2' (PBP 2'), which has been associated with methicillin resistance and which has very low affinity for beta-lactam antibiotics.",
        "note": "Target replacement. The native PBPs remain fully inhibited; a bypass enzyme carries the load.",
        "extra_nodes": [
            {"node_id": "pbp2a_activity", "label": "peptidoglycan cross-linking by the acquired PBP",
             "node_type": "MOLECULAR_FUNCTION", "grounding": "GO:0008658",
             "description": "Grounded to penicillin binding -- the activity assayed by the PBP gels these papers report."},
            {"node_id": "low_affinity", "label": "low affinity of the acquired PBP for beta-lactams",
             "node_type": "STATE",
             "description": "The causal core. Ungrounded: an affinity property has no ontology term here."},
            {"node_id": "pg_synth", "label": "peptidoglycan biosynthetic process",
             "node_type": "BIOLOGICAL_PROCESS", "grounding": "GO:0009252"},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "pbp2a_activity",
             "predicate": "enables (wall synthesis under drug)", "predicate_id": "RO:0002327",
             "evidence": [{"reference": "ARO:3000617", "snippet": "A foreign PBP2a acquired by lateral gene transfer that is able to perform peptidoglycan synthesis in the presence of beta-lactams.",
                           "notes": "'able to perform peptidoglycan synthesis in the presence of beta-lactams'."}]},
            {"subject": "low_affinity", "object": "pbp2a_activity",
             "predicate": "causally upstream of (leaves the enzyme uninhibited)",
             "predicate_id": "RO:0002411",
             "description": "Why the acquired enzyme keeps working: the drug binds it poorly.",
             "evidence": [{"reference": "PMID:3499861", "snippet": "All strains produced penicillin-binding protein 2' (PBP 2'), which has been associated with methicillin resistance and which has very low affinity for beta-lactam antibiotics.",
                           "notes": "Ueda et al. 1987, across 137 clinical strains."}]},
            {"subject": "determinant", "object": "low_affinity",
             "predicate": "has quality (very low beta-lactam affinity)", "predicate_id": "RO:0000086",
             "evidence": [{"reference": "PMID:6563036", "snippet": "We detected a high-molecular-weight PBP (PBP-2a; approximate size, 78,000 daltons) that was only present in the resistant bacteria but not in the isogenic susceptible strains.",
                           "notes": "Hartman & Tomasz 1984 -- present in the resistant strains and NOT in the isogenic susceptible ones, which is what makes the association causal rather than incidental."}]},
            {"subject": "pbp2a_activity", "object": "pg_synth",
             "predicate": "part of (peptidoglycan biosynthesis)", "predicate_id": "BFO:0000050",
             "evidence": [{"reference": "ARO:3000617", "snippet": "A foreign PBP2a acquired by lateral gene transfer that is able to perform peptidoglycan synthesis in the presence of beta-lactams.",
                           "notes": "The process the acquired PBP sustains."}]},
        ],
    },
    # ---------------------------------------------------------------------------------
    # fabG1 (ARO:3004887) -- unblocks #219, by dropping a claim CARD never made.
    #
    # #219 was blocked on proving that a fabG1 PROMOTER substitution raises inhA expression.
    # That mechanism is real and well known, and CARD does not assert it: its definitions
    # say "Mutations that occur in the fabg1 gene resulting in the inability for the
    # antibiotic to inhibit mycolic acid biosynthesis" and place fabG1 "in the fatty acid
    # synthesis pathway, acting in the first reduction step for mycolic acid".
    #
    # That is TARGET ALTERATION of a FAS-II enzyme, not promoter-driven overexpression. I
    # spent three attempts trying to evidence a mechanism the source does not claim, when
    # the source's own claim was curatable all along.
    "ARO:3004887": {
        "curated": "2026-08-07T00:00:00Z",
        "reference": "ARO:3004887",
        "mech": {"ARO:3000212": "Mutations that occur in the fabg1 gene resulting in the inability for the antibiotic to inhibit mycolic acid biosynthesis."},
        "mech_res": "Mutations that occur in the fabg1 gene resulting in the inability for the antibiotic to inhibit mycolic acid biosynthesis.",
        "det_res": [
            {"reference": "ARO:3004887", "snippet": "Mutations that occur in the fabg1 gene resulting in the inability for the antibiotic to inhibit mycolic acid biosynthesis.",
             "notes": "CARD's own claim, and the only one it makes: the mutation stops the drug inhibiting mycolic acid synthesis."},
            {"reference": "ARO:3004895", "snippet": "fabG1 is involved in the fatty acid synthesis pathway, acting in the first reduction step for mycolic acid. It is associated with isoniazid resistance.",
             "notes": "And where in the pathway: the first reduction step for mycolic acid. NOTE what is deliberately NOT asserted -- the fabG1-inhA operon promoter mechanism, which is real, well documented elsewhere, and not something CARD states for these records (#219)."},
        ],
        "res_drug": "Mutations that occur in the fabg1 gene resulting in the inability for the antibiotic to inhibit mycolic acid biosynthesis.",
        "note": "Target alteration in FAS-II. Deliberately NOT the promoter-overexpression story, which CARD does not assert for these records.",
        "extra_nodes": [
            {"node_id": "fas_step", "label": "first reduction step of mycolic acid synthesis (FabG1/MabA)",
             "node_type": "MOLECULAR_FUNCTION",
             "description": "Ungrounded: the specific ketoacyl-reductase step has no distinct term in use here."},
            {"node_id": "mycolic", "label": "mycolic acid biosynthetic process",
             "node_type": "BIOLOGICAL_PROCESS", "grounding": "GO:0071768"},
            {"node_id": "inhibition", "label": "drug inhibition of mycolic acid synthesis",
             "node_type": "STATE",
             "description": "What the mutation prevents. Ungrounded."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "fas_step",
             "predicate": "enables (the first reduction step)", "predicate_id": "RO:0002327",
             "evidence": [{"reference": "ARO:3004895", "snippet": "fabG1 is involved in the fatty acid synthesis pathway, acting in the first reduction step for mycolic acid. It is associated with isoniazid resistance.",
                           "notes": "CARD places fabG1 in the fatty acid synthesis pathway."}]},
            {"subject": "fas_step", "object": "mycolic",
             "predicate": "part of (mycolic acid biosynthesis)", "predicate_id": "BFO:0000050",
             "evidence": [{"reference": "PMID:8284673", "snippet": "The InhA protein shows significant sequence conservation with the Escherichia coli enzyme EnvM, and cell-free assays indicate that it may be involved in mycolic acid biosynthesis.",
                           "notes": "Banerjee et al. 1994, borrowed from round 28 for the pathway context -- it studied InhA, the NEXT step, and the notes say so rather than implying it covered FabG1."}]},
            {"subject": "drug0", "object": "inhibition",
             "predicate": "causally upstream of (inhibits mycolic acid synthesis)",
             "predicate_id": "RO:0002411",
             "description": "Drug action: activated isoniazid blocks FAS-II, which is what makes the pathway a target at all (rounds 27-28).",
             "evidence": [{"reference": "PMID:1656850",
                           "snippet": "Isonicotinic acid hydrazide (isoniazid; INH) inhibition of mycolic acid synthesis was studied by using cell extracts from both INH-sensitive and -resistant strains of Mycobacterium aurum.",
                           "notes": "Direct evidence for the drug's action (#250). The first version of this edge cited ARO:3004887, which only IMPLIES the inhibition by describing what the mutation prevents -- weaker than the rule that a snippet must state its claim."}]},
            {"subject": "determinant", "object": "inhibition",
             "predicate": "negatively regulates (the mutated enzyme is no longer inhibited)",
             "predicate_id": "RO:0002212",
             "description": "The causal core, in CARD's own words: the mutation results in the antibiotic being unable to inhibit the pathway.",
             "evidence": [{"reference": "ARO:3004887", "snippet": "Mutations that occur in the fabg1 gene resulting in the inability for the antibiotic to inhibit mycolic acid biosynthesis.",
                           "notes": "This is the whole of what the source asserts. A stronger claim would need the promoter evidence #219 could not find."}]},
        ],
    },
    # ---------------------------------------------------------------------------------
    # 23S rRNA / macrolide (ARO:3004125) -- unblocks #217. That issue said no source
    # CONSTRUCTS a 23S substitution and MEASURES the affinity loss, which is the tier round
    # 29's 16S family had. Douthwaite & Aagaard 1993 does exactly that, and was found by
    # searching for a BINDING-measurement paper rather than a substitution-construction one.
    #
    # Same NUCLEIC_ACID determinant shape as round 29, and the same #215 caveat: the
    # determinant is rRNA, so the graph routes through no protein-trait record.
    "ARO:3004125": {
        "curated": "2026-08-07T00:00:00Z",
        "determinant_node_type": "NUCLEIC_ACID",
        "reference": "PMID:7689111",      # Douthwaite & Aagaard 1993, J Mol Biol
        "mech": {"ARO:3000212": "Erythromycin still protects against chemical modification in the mutant peptidyl transferase loops, but the affinity of the drug interaction is reduced 20-fold in the 2057A mutant, 10(3)-fold in the 2058U mutant and 10(4)-fold in the 2058G mutant."},
        "mech_res": "Erythromycin still protects against chemical modification in the mutant peptidyl transferase loops, but the affinity of the drug interaction is reduced 20-fold in the 2057A mutant, 10(3)-fold in the 2058U mutant and 10(4)-fold in the 2058G mutant.",
        "det_res": [
            {"reference": "PMID:7689111", "snippet": "Erythromycin still protects against chemical modification in the mutant peptidyl transferase loops, but the affinity of the drug interaction is reduced 20-fold in the 2057A mutant, 10(3)-fold in the 2058U mutant and 10(4)-fold in the 2058G mutant.",
             "notes": "Douthwaite & Aagaard 1993. The affinity loss is MEASURED and graded: 20-fold at 2057A, 1000-fold at 2058U, 10000-fold at 2058G. Three substitutions, three magnitudes."},
            {"reference": "PMID:7689111", "snippet": "We used a chemical modification approach to analyse conformational changes that are induced by mutations in the peptidyl transferase loop, and to determine how these changes affect drug interaction.",
             "notes": "And the method: chemical modification, which reads the rRNA conformation directly rather than inferring it from an MIC."},
        ],
        "res_drug": "The antibiotic erythromycin inhibits protein synthesis by binding to the 50 S ribosomal subunit, where the drug interacts with the unpaired bases 2058A and 2059A in the peptidyl transferase loop of 23 S rRNA.",
        "note": "Target alteration in 23S rRNA: substitutions in the peptidyl transferase loop reduce macrolide affinity by up to four orders of magnitude.",
        "extra_nodes": [
            {"node_id": "pt_loop", "label": "peptidyl transferase loop of 23S rRNA, around bases 2057, 2058 and 2059",
             "node_type": "NUCLEIC_ACID",
             "description": "The macrolide binding site. Positions are in the E. coli frame and differ per organism (2143 in H. pylori), so no per-record residue node is asserted -- the same caveat as the QRDR and the 16S decoding site."},
            {"node_id": "conformation", "label": "open conformation of the peptidyl transferase loop",
             "node_type": "STATE",
             "description": "What the substitutions induce, and the reason binding falls. Ungrounded."},
        ],
        "extra_edges": [
            {"subject": "pt_loop", "object": "determinant",
             "predicate": "part of (the loop that binds the drug)", "predicate_id": "BFO:0000050",
             "evidence": [{"reference": "PMID:7689111", "snippet": "The antibiotic erythromycin inhibits protein synthesis by binding to the 50 S ribosomal subunit, where the drug interacts with the unpaired bases 2058A and 2059A in the peptidyl transferase loop of 23 S rRNA.",
                           "notes": "The drug interacts with unpaired 2058A and 2059A in this loop."}]},
            {"subject": "drug0", "object": "pt_loop",
             "predicate": "molecularly interacts with (binds the unpaired bases)",
             "predicate_id": "RO:0002436",
             "evidence": [{"reference": "PMID:7689111", "snippet": "The antibiotic erythromycin inhibits protein synthesis by binding to the 50 S ribosomal subunit, where the drug interacts with the unpaired bases 2058A and 2059A in the peptidyl transferase loop of 23 S rRNA.",
                           "notes": "Drug action: erythromycin inhibits protein synthesis from this site."}]},
            {"subject": "determinant", "object": "conformation",
             "predicate": "causally upstream of (opens the loop)", "predicate_id": "RO:0002411",
             "description": "The substitutions do not remove a contact; they change the loop's shape.",
             "evidence": [{"reference": "PMID:7689111", "snippet": "We used a chemical modification approach to analyse conformational changes that are induced by mutations in the peptidyl transferase loop, and to determine how these changes affect drug interaction.",
                           "notes": "Conformational change read by chemical modification, and the paper's framing of what the mutations do."}]},
            {"subject": "conformation", "object": "pt_loop",
             "predicate": "negatively regulates (the open loop binds the drug up to 10,000-fold worse)",
             "predicate_id": "RO:0002212",
             "description": "The causal core, graded rather than binary -- and the control matters: substitutions at 2032 in the adjacent hairpin alter drug tolerance yet change neither the loop's structure nor erythromycin binding, so the effect is specific to this loop.",
             "evidence": [
                 {"reference": "PMID:7689111", "snippet": "Erythromycin still protects against chemical modification in the mutant peptidyl transferase loops, but the affinity of the drug interaction is reduced 20-fold in the 2057A mutant, 10(3)-fold in the 2058U mutant and 10(4)-fold in the 2058G mutant.",
                  "notes": "20-fold, 1,000-fold and 10,000-fold for 2057A, 2058U and 2058G."},
                 {"reference": "PMID:7689111", "snippet": "Single mutations at position 2032 in the adjacent hairpin loop, which have previously been shown to alter drug tolerances, gave no detectable effects on the structure of the peptidyl transferase loop or on erythromycin binding.",
                  "notes": "The negative control in the same paper: a nearby position that affects tolerance but NOT this loop or this binding. It is what makes the causal claim specific rather than positional."},
             ]},
        ],
    },
    # ---------------------------------------------------------------------------------
    # Target-modifying enzymes (ARO:3000519) -- 16S rRNA methyltransferases, and the
    # counterpart of round 29. Those records are MUTATIONS in the decoding site that lower
    # aminoglycoside affinity; these are ENZYMES that methylate the same site to the same
    # end. Same target, same consequence, and the determinant is a protein here rather than
    # the rRNA itself -- which is why the two could not share a config.
    #
    # Mechanism ids taken from the records rather than guessed: ARO:0001001, ARO:3000211
    # and ARO:3000212. Five rounds this session lost time to guessing them (r31, r32, r42,
    # r43, r46), so this one asked the corpus first.
    "ARO:3000519": {
        "curated": "2026-08-07T00:00:00Z",
        "reference": "PMID:40643688",
        "mech": {"ARO:0001001": "The acquisition of aminoglycoside-resistance methyltransferases that modify 16S rRNA nucleotides in the ribosome decoding center, for example, results in exceptionally high-level aminoglycoside resistance and poses a major threat to their future clinical utility.", "ARO:3000211": "The acquisition of aminoglycoside-resistance methyltransferases that modify 16S rRNA nucleotides in the ribosome decoding center, for example, results in exceptionally high-level aminoglycoside resistance and poses a major threat to their future clinical utility.",
                 "ARO:3000212": "The acquisition of aminoglycoside-resistance methyltransferases that modify 16S rRNA nucleotides in the ribosome decoding center, for example, results in exceptionally high-level aminoglycoside resistance and poses a major threat to their future clinical utility."},
        "mech_res": "The acquisition of aminoglycoside-resistance methyltransferases that modify 16S rRNA nucleotides in the ribosome decoding center, for example, results in exceptionally high-level aminoglycoside resistance and poses a major threat to their future clinical utility.",
        "det_res": [
            {"reference": "PMID:40643688", "snippet": "Among several distinct mechanisms used by bacteria to circumvent antibiotic stress, a predominant form of resistance to ribosome-targeting compounds is the methylation of their ribosomal RNA (rRNA) binding sites.",
             "notes": "The mechanism class: modify the drug's binding site on the rRNA rather than the drug or the protein."},
            {"reference": "PMID:40643688", "snippet": "The acquisition of aminoglycoside-resistance methyltransferases that modify 16S rRNA nucleotides in the ribosome decoding center, for example, results in exceptionally high-level aminoglycoside resistance and poses a major threat to their future clinical utility.",
             "notes": "And its clinical weight -- 'exceptionally high-level' resistance, because a methylated site resists the whole aminoglycoside class at once."},
        ],
        "res_drug": "The acquisition of aminoglycoside-resistance methyltransferases that modify 16S rRNA nucleotides in the ribosome decoding center, for example, results in exceptionally high-level aminoglycoside resistance and poses a major threat to their future clinical utility.",
        "note": "Target modification by methylation: the enzyme counterpart of round 29's decoding-site mutations.",
        "extra_nodes": [
            {"node_id": "methyltransferase", "label": "16S rRNA methyltransferase activity",
             "node_type": "MOLECULAR_FUNCTION",
             "description": "Ungrounded: GO has rRNA methyltransferase terms but the resistance-associated positions differ per enzyme (G1405, A1408)."},
            {"node_id": "decoding_site", "label": "16S rRNA decoding site (aminoglycoside binding site)",
             "node_type": "NUCLEIC_ACID",
             "description": "The SAME site round 29's records mutate. Ungrounded there and here, for the same reason: no ontology term denotes it."},
            {"node_id": "methylated", "label": "methylated decoding site", "node_type": "STATE",
             "description": "Ungrounded: a modified nucleotide state rather than a compound."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "methyltransferase",
             "predicate": "enables (16S rRNA methylation)", "predicate_id": "RO:0002327",
             "evidence": [{"reference": "PMID:40643688", "snippet": "The acquisition of aminoglycoside-resistance methyltransferases that modify 16S rRNA nucleotides in the ribosome decoding center, for example, results in exceptionally high-level aminoglycoside resistance and poses a major threat to their future clinical utility.",
                           "notes": "The acquired enzymes modify 16S rRNA nucleotides in the decoding centre."}]},
            {"subject": "methyltransferase", "object": "methylated",
             "predicate": "causally upstream of (methylates the site)", "predicate_id": "RO:0002411",
             "evidence": [{"reference": "PMID:40643688", "snippet": "Among several distinct mechanisms used by bacteria to circumvent antibiotic stress, a predominant form of resistance to ribosome-targeting compounds is the methylation of their ribosomal RNA (rRNA) binding sites.",
                           "notes": "Methylation of the drug's rRNA binding site is the mechanism class."}]},
            {"subject": "methylated", "object": "decoding_site",
             "predicate": "negatively regulates (the modified site no longer binds the drug)",
             "predicate_id": "RO:0002212",
             "description": "The causal core, and the same endpoint round 29 reaches by substitution instead: the decoding site stops binding aminoglycosides.",
             "evidence": [{"reference": "PMID:40643688", "snippet": "The acquisition of aminoglycoside-resistance methyltransferases that modify 16S rRNA nucleotides in the ribosome decoding center, for example, results in exceptionally high-level aminoglycoside resistance and poses a major threat to their future clinical utility.",
                           "notes": "'exceptionally high-level aminoglycoside resistance' -- one modification covers the class."}]},
            {"subject": "drug0", "object": "decoding_site",
             "predicate": "molecularly interacts with (binds the decoding site)",
             "predicate_id": "RO:0002436",
             "evidence": [{"reference": "PMID:40643688", "snippet": "Among several distinct mechanisms used by bacteria to circumvent antibiotic stress, a predominant form of resistance to ribosome-targeting compounds is the methylation of their ribosomal RNA (rRNA) binding sites.",
                           "notes": "Drug action: the rRNA binding site methylation denies it."}]},
        ],
    },
    # ---------------------------------------------------------------------------------
    # Macrolide ESTERASES (ARO:3000201, the Ere/Est records). Drug inactivation -- rounds
    # 12-16's kind -- but the family term holds three unrelated reactions, so the config is
    # for ring hydrolysis only and a precondition keeps the phosphotransferases and
    # glycosyltransferases out until they have their own papers.
    "ARO:3000201": [
    {
        "curated": "2026-08-07T00:00:00Z",
        "precondition": _requires_macrolide_esterase,
        "reference": "PMID:22303981",      # Morar et al. 2012, Biochemistry
        "mech": {"ARO:0001004": "One mechanism of macrolide resistance is via drug inactivation: enzymatic hydrolysis of the macrolactone ring catalyzed by erythromycin esterases, EreA and EreB.", "ARO:3000212": "One mechanism of macrolide resistance is via drug inactivation: enzymatic hydrolysis of the macrolactone ring catalyzed by erythromycin esterases, EreA and EreB.",
                 # ARO:3000321 "hydrolysis of macrolide macrocycle lactone ring" -- I guessed
                 # ARO:3000004, which is a beta-lactamase class. Fifth time this session the
                 # UncoveredMechanism guard has named the id for me (r31, r32, r42, r43, r46).
                 "ARO:3000321": "One mechanism of macrolide resistance is via drug inactivation: enzymatic hydrolysis of the macrolactone ring catalyzed by erythromycin esterases, EreA and EreB."},
        "mech_res": "One mechanism of macrolide resistance is via drug inactivation: enzymatic hydrolysis of the macrolactone ring catalyzed by erythromycin esterases, EreA and EreB.",
        "det_res": "One mechanism of macrolide resistance is via drug inactivation: enzymatic hydrolysis of the macrolactone ring catalyzed by erythromycin esterases, EreA and EreB.",
        "res_drug": "One mechanism of macrolide resistance is via drug inactivation: enzymatic hydrolysis of the macrolactone ring catalyzed by erythromycin esterases, EreA and EreB.",
        "note": "Drug inactivation by hydrolysing the macrolactone ring -- the macrolide's defining chemical feature.",
        "extra_nodes": [
            {"node_id": "esterase", "label": "erythromycin esterase activity",
             "node_type": "MOLECULAR_FUNCTION",
             "description": "Ungrounded: GO has esterase terms but none specific to the macrolactone ring."},
            {"node_id": "ring", "label": "intact macrolactone ring", "node_type": "STATE",
             "description": "The macrolide's defining feature, and what the enzyme opens. Ungrounded."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "esterase",
             "predicate": "enables (macrolactone ring hydrolysis)", "predicate_id": "RO:0002327",
             "evidence": [{"reference": "PMID:22303981", "snippet": "One mechanism of macrolide resistance is via drug inactivation: enzymatic hydrolysis of the macrolactone ring catalyzed by erythromycin esterases, EreA and EreB.",
                           "notes": "Morar et al. 2012 name the reaction and the enzymes that catalyse it."}]},
            {"subject": "esterase", "object": "ring",
             "predicate": "negatively regulates (hydrolyses the ring)", "predicate_id": "RO:0002212",
             "description": "The causal core: opening the macrolactone destroys the scaffold the drug needs to bind the ribosome.",
             "evidence": [{"reference": "PMID:22303981", "snippet": "One mechanism of macrolide resistance is via drug inactivation: enzymatic hydrolysis of the macrolactone ring catalyzed by erythromycin esterases, EreA and EreB.",
                           "notes": "Hydrolysis of the ring IS the inactivation."}]},
            {"subject": "ring", "object": "drug0",
             "predicate": "part of (the intact drug)", "predicate_id": "BFO:0000050",
             "evidence": [{"reference": "PMID:22303981", "snippet": "One mechanism of macrolide resistance is via drug inactivation: enzymatic hydrolysis of the macrolactone ring catalyzed by erythromycin esterases, EreA and EreB.",
                           "notes": "The macrolactone is what makes a macrolide one; without it there is no drug to bind a target."}]},
        ],
    },
        {
            "curated": "2026-08-07T00:00:00Z",
            "precondition": _requires_macrolide_kinase,
            "reference": "PMID:28416110",      # Fong et al. 2017, Structure
            "mech": {"ARO:0001004": "The macrolides are a class of antibiotic, characterized by a large macrocyclic lactone ring that can be inactivated by macrolide phosphotransferase enzymes.", "ARO:3000212": "The macrolides are a class of antibiotic, characterized by a large macrocyclic lactone ring that can be inactivated by macrolide phosphotransferase enzymes.",
                     "ARO:3000105": "The macrolides are a class of antibiotic, characterized by a large macrocyclic lactone ring that can be inactivated by macrolide phosphotransferase enzymes."},
            "mech_res": "The macrolides are a class of antibiotic, characterized by a large macrocyclic lactone ring that can be inactivated by macrolide phosphotransferase enzymes.",
            "det_res": [
                {"reference": "PMID:28416110", "snippet": "The macrolides are a class of antibiotic, characterized by a large macrocyclic lactone ring that can be inactivated by macrolide phosphotransferase enzymes.",
                 "notes": "Fong et al. 2017. The second of three chemistries under this family term: the ring is PHOSPHORYLATED rather than hydrolysed (round 46)."},
                {"reference": "PMID:28416110", "snippet": "We present structures for MPH(2')-I and MPH(2')-II in the apo state, and in complex with GTP analogs and six different macrolides.",
                 "notes": "Structures of both main classes, with nucleotide and six different macrolides bound -- which is what establishes the reaction rather than inferring it."},
            ],
            "res_drug": "The macrolides are a class of antibiotic, characterized by a large macrocyclic lactone ring that can be inactivated by macrolide phosphotransferase enzymes.",
            "note": "Drug inactivation by phosphorylation, distinct from the esterases' ring hydrolysis under the same family term.",
            "extra_nodes": [
                {"node_id": "kinase", "label": "macrolide phosphotransferase activity",
                 "node_type": "MOLECULAR_FUNCTION",
                 "description": "Ungrounded: GO has kinase terms but none specific to macrolide 2'-OH phosphorylation."},
                {"node_id": "pocket", "label": "expanded hydrophobic antibiotic binding pocket",
                 "node_type": "STATE",
                 "description": "What lets one enzyme handle six chemically different macrolides. Ungrounded."},
                {"node_id": "phospho_drug", "label": "phosphorylated (inactive) macrolide",
                 "node_type": "CHEMICAL",
                 "description": "Ungrounded: the product differs per drug."},
            ],
            "extra_edges": [
                {"subject": "determinant", "object": "kinase",
                 "predicate": "enables (macrolide phosphorylation)", "predicate_id": "RO:0002327",
                 "evidence": [{"reference": "PMID:28416110", "snippet": "The macrolides are a class of antibiotic, characterized by a large macrocyclic lactone ring that can be inactivated by macrolide phosphotransferase enzymes.",
                               "notes": "Fong et al. 2017."}]},
                {"subject": "pocket", "object": "determinant",
                 "predicate": "part of (the substrate-binding site)", "predicate_id": "BFO:0000050",
                 "description": "An expanded, largely hydrophobic pocket -- the structural reason one enzyme inactivates chemically unrelated macrolides.",
                 "evidence": [{"reference": "PMID:28416110", "snippet": "The structures show that the enzymes are related to the aminoglycoside phosphotransferases, but are distinguished from them by the presence of a large interdomain linker that contributes to an expanded antibiotic binding pocket.",
                               "notes": "The interdomain linker distinguishing these from the aminoglycoside phosphotransferases they are related to."}]},
                {"subject": "kinase", "object": "phospho_drug",
                 "predicate": "has output", "predicate_id": "RO:0002234",
                 "evidence": [{"reference": "PMID:28416110", "snippet": "We present structures for MPH(2')-I and MPH(2')-II in the apo state, and in complex with GTP analogs and six different macrolides.",
                               "notes": "Nucleotide and macrolide captured together in the structures."}]},
                {"subject": "phospho_drug", "object": "drug0",
                 "predicate": "negatively regulates (the phosphorylated drug is inactive)",
                 "predicate_id": "RO:0002212",
                 "description": "The causal core: the drug is chemically modified rather than displaced, excluded or pumped out.",
                 "evidence": [{"reference": "PMID:28416110", "snippet": "The macrolides are a class of antibiotic, characterized by a large macrocyclic lactone ring that can be inactivated by macrolide phosphotransferase enzymes.",
                               "notes": "'can be inactivated by macrolide phosphotransferase enzymes'."}]},
            ],
        },
        {
            "curated": "2026-08-07T00:00:00Z",
            "precondition": _requires_macrolide_glycosyltransferase,
            "reference": "PMID:17376874",      # Bolam et al. 2007, PNAS
            "mech": {"ARO:0001004": "The Streptomyces antibioticus glycosyltransferases, OleI and OleD, glycosylate and inactivate oleandomycin and diverse macrolides including erythromycin, respectively.", "ARO:3000212": "The Streptomyces antibioticus glycosyltransferases, OleI and OleD, glycosylate and inactivate oleandomycin and diverse macrolides including erythromycin, respectively.",
                     "ARO:3000208": "The Streptomyces antibioticus glycosyltransferases, OleI and OleD, glycosylate and inactivate oleandomycin and diverse macrolides including erythromycin, respectively."},
            "mech_res": "The Streptomyces antibioticus glycosyltransferases, OleI and OleD, glycosylate and inactivate oleandomycin and diverse macrolides including erythromycin, respectively.",
            "det_res": [
                {"reference": "PMID:17376874", "snippet": "The Streptomyces antibioticus glycosyltransferases, OleI and OleD, glycosylate and inactivate oleandomycin and diverse macrolides including erythromycin, respectively.",
                 "notes": "Bolam et al. 2007. The third chemistry under this family term: a sugar is ADDED, rather than the ring being opened (r46) or phosphorylated (r47)."},
                {"reference": "PMID:17376874", "snippet": "Glycosylation of macrolide antibiotics confers host cell immunity from endogenous and exogenous agents.",
                 "notes": "And its origin, which the other two chemistries do not share: these enzymes are the PRODUCER's self-protection. Resistance in a pathogen is that immunity system turning up elsewhere."},
            ],
            "res_drug": "The Streptomyces antibioticus glycosyltransferases, OleI and OleD, glycosylate and inactivate oleandomycin and diverse macrolides including erythromycin, respectively.",
            "note": "Drug inactivation by glycosylation -- originally a macrolide producer's own immunity mechanism.",
            "extra_nodes": [
                {"node_id": "glycosyl", "label": "macrolide glycosyltransferase activity",
                 "node_type": "MOLECULAR_FUNCTION",
                 "description": "Ungrounded: GO has glycosyltransferase terms but none specific to macrolide inactivation."},
                {"node_id": "glyco_drug", "label": "glycosylated (inactive) macrolide",
                 "node_type": "CHEMICAL", "description": "Ungrounded: the product differs per drug."},
                {"node_id": "ribosome_site", "label": "23S rRNA macrolide binding site",
                 "node_type": "NUCLEIC_ACID",
                 "description": "The target the drug can no longer occupy. Same site round 29's 16S work neighbours, and ungrounded for the same reason."},
            ],
            "extra_edges": [
                {"subject": "determinant", "object": "glycosyl",
                 "predicate": "enables (macrolide glycosylation)", "predicate_id": "RO:0002327",
                 "evidence": [{"reference": "PMID:17376874", "snippet": "The Streptomyces antibioticus glycosyltransferases, OleI and OleD, glycosylate and inactivate oleandomycin and diverse macrolides including erythromycin, respectively.",
                               "notes": "OleI and OleD glycosylate and inactivate."}]},
                {"subject": "glycosyl", "object": "glyco_drug",
                 "predicate": "has output", "predicate_id": "RO:0002234",
                 "evidence": [{"reference": "PMID:17376874", "snippet": "The Streptomyces antibioticus glycosyltransferases, OleI and OleD, glycosylate and inactivate oleandomycin and diverse macrolides including erythromycin, respectively.",
                               "notes": "OleD acts on diverse macrolides including erythromycin, which is why one enzyme covers a class."}]},
                {"subject": "glyco_drug", "object": "ribosome_site",
                 "predicate": "negatively regulates (the glycosylated drug cannot occupy the site)",
                 "predicate_id": "RO:0002212",
                 "description": "The causal core, and the structures explain WHY: erythromycin binds OleD in the same conformation it adopts on the 23S RNA, so the sugar is added exactly where the ribosome would bind.",
                 "evidence": [{"reference": "PMID:17376874", "snippet": "Erythromycin binds to OleD and the 23S RNA of its target ribosome in the same conformation",
                               "notes": "Bolam et al. 2007 -- the enzyme recognises the drug in its target-bound conformation."}]},
                {"subject": "drug0", "object": "ribosome_site",
                 "predicate": "molecularly interacts with (binds the 23S site)", "predicate_id": "RO:0002436",
                 "evidence": [{"reference": "PMID:17376874", "snippet": "Erythromycin binds to OleD and the 23S RNA of its target ribosome in the same conformation",
                               "notes": "Drug action: the site glycosylation denies it."}]},
            ],
        },
    ],
    # ---------------------------------------------------------------------------------
    # Permeability (ARO:3000270) -- a TENTH mechanism kind, and the mirror of efflux: the
    # drug is not pumped out, it never gets in. Most of these records are the CHANNEL, and
    # the resistance is its loss or down-regulation -- which is why 8 of the 42 carry ARO's
    # "resistance by absence" mechanism id alongside "reduced permeability".
    #
    # The determinant is therefore usually a porin whose ABSENCE resists, the same inverted
    # shape as katG (round 27) and the efflux repressors (round 37).
    "ARO:3000270": {
        "curated": "2026-08-07T00:00:00Z",
        "reference": "PMID:14665678",      # Nikaido 2003, Microbiol Mol Biol Rev
        "mech": {"ARO:3000244": "Although outer membrane components often play important roles in the interaction of symbiotic or pathogenic bacteria with their host organisms, the major role of this membrane must usually be to serve as a permeability barrier to prevent the entry of noxious compounds and at the same time to allow the influx of nutrient molecules.", "ARO:3000212": "Although outer membrane components often play important roles in the interaction of symbiotic or pathogenic bacteria with their host organisms, the major role of this membrane must usually be to serve as a permeability barrier to prevent the entry of noxious compounds and at the same time to allow the influx of nutrient molecules.",
                 "ARO:0001002": "Although outer membrane components often play important roles in the interaction of symbiotic or pathogenic bacteria with their host organisms, the major role of this membrane must usually be to serve as a permeability barrier to prevent the entry of noxious compounds and at the same time to allow the influx of nutrient molecules.", "ARO:0010000": "Although outer membrane components often play important roles in the interaction of symbiotic or pathogenic bacteria with their host organisms, the major role of this membrane must usually be to serve as a permeability barrier to prevent the entry of noxious compounds and at the same time to allow the influx of nutrient molecules.",
                 "ARO:3003764": "Although outer membrane components often play important roles in the interaction of symbiotic or pathogenic bacteria with their host organisms, the major role of this membrane must usually be to serve as a permeability barrier to prevent the entry of noxious compounds and at the same time to allow the influx of nutrient molecules.",   # resistance by absence -- the id the guard named
                 "ARO:3004596": "Although outer membrane components often play important roles in the interaction of symbiotic or pathogenic bacteria with their host organisms, the major role of this membrane must usually be to serve as a permeability barrier to prevent the entry of noxious compounds and at the same time to allow the influx of nutrient molecules."},
        "mech_res": "Although outer membrane components often play important roles in the interaction of symbiotic or pathogenic bacteria with their host organisms, the major role of this membrane must usually be to serve as a permeability barrier to prevent the entry of noxious compounds and at the same time to allow the influx of nutrient molecules.",
        "det_res": [
            {"reference": "PMID:14665678", "snippet": "Although outer membrane components often play important roles in the interaction of symbiotic or pathogenic bacteria with their host organisms, the major role of this membrane must usually be to serve as a permeability barrier to prevent the entry of noxious compounds and at the same time to allow the influx of nutrient molecules.",
             "notes": "Nikaido 2003. The outer membrane is a permeability barrier by default; channels are what let a drug across it, so losing a channel raises the barrier."},
            # #425. This was carO's own definition, used as an "archetype" on all 42
            # records this config promotes -- 2 of which are carO. Truncated at "influx of
            # carbapenems" it read as generic and nobody noticed; #423 restored the rest of
            # the sentence, which names Acinetobacter baumannii, the carO gene and three
            # genera, and put that on two fungal permeases, a fungal nucleobase
            # transporter, MarA and a Ser/Thr kinase. The truncation had been doing
            # curation work by accident.
            #
            # Replaced by the definition of the FAMILY TERM this config is for, which is an
            # is_a ancestor of every record it promotes and names no gene and no organism.
            # Nothing is lost: the carO sentence was an illustration, and the general claim
            # it illustrated is Nikaido above.
            {"reference": "ARO:3000270", "snippet": "Enzymes or other proteins either directly or indirectly reducing overall permeability to antibiotics.",
             "notes": "CARD's definition of the family term these records sit under -- the claim at exactly the level this config makes it. Each record's own definition names the channel and the drug class IT admits."},
        ],
        "res_drug": "Although outer membrane components often play important roles in the interaction of symbiotic or pathogenic bacteria with their host organisms, the major role of this membrane must usually be to serve as a permeability barrier to prevent the entry of noxious compounds and at the same time to allow the influx of nutrient molecules.",
        "note": "The mirror of efflux: the drug never gets in, rather than being pumped out.",
        "extra_nodes": [
            {"node_id": "influx", "label": "xenobiotic transport (drug influx across the outer membrane)",
             "node_type": "BIOLOGICAL_PROCESS", "grounding": "GO:0042908",
             "description": "GO:0042908 is the transport process; which channel carries it differs per record and is named in that record's own definition."},
            {"node_id": "barrier", "label": "outer membrane permeability barrier",
             "node_type": "STATE",
             "description": "Ungrounded: a property of the envelope rather than a compound."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "influx",
             "predicate": "enables (admits the drug across the membrane)", "predicate_id": "RO:0002327",
             "description": "The wild-type function. Resistance is its loss or down-regulation, which is why these records are channels rather than resistance enzymes.",
             # #425, the second of the two carO sites, and the one that carried the ONLY
             # evidence on this edge. ARO:3000244 is the mechanism term these records
             # participate in; its definition states the inverse of this edge -- that
             # permeability falls when porin production does -- which is precisely the
             # claim, since the edge exists to be negated by the channel's loss.
             "evidence": [{"reference": "ARO:3000244", "snippet": "Reduction in permeability to antibiotic, generally through reduced production of porins, can provide resistance.",
                           "notes": "CARD's mechanism term, stated as the loss: permeability falls when the channel does, which is this edge read backwards. General to every record here; each names its own channel and drug."}]},
            {"subject": "barrier", "object": "influx",
             "predicate": "negatively regulates (the membrane excludes what has no channel)",
             "predicate_id": "RO:0002212",
             "evidence": [{"reference": "PMID:14665678", "snippet": "Although outer membrane components often play important roles in the interaction of symbiotic or pathogenic bacteria with their host organisms, the major role of this membrane must usually be to serve as a permeability barrier to prevent the entry of noxious compounds and at the same time to allow the influx of nutrient molecules.",
                           "notes": "Nikaido 2003: exclusion is the outer membrane's default, and channels are the exception to it."}]},
            {"subject": "influx", "object": "drug0",
             "predicate": "causally upstream of (the drug reaches its target)", "predicate_id": "RO:0002411",
             "description": "The causal core inverted: with the channel lost or down-regulated, this step does not happen and the drug never reaches its target.",
             "evidence": [{"reference": "PMID:14665678", "snippet": "Although outer membrane components often play important roles in the interaction of symbiotic or pathogenic bacteria with their host organisms, the major role of this membrane must usually be to serve as a permeability barrier to prevent the entry of noxious compounds and at the same time to allow the influx of nutrient molecules.",
                           "notes": "A drug that cannot cross the barrier cannot act, whatever its target."}]},
        ],
    },
    # ---------------------------------------------------------------------------------
    # Efflux repressors (ARO:3000451, the 27 verified ones). The regulation shape of rounds
    # 22 and 24 applied to efflux: the determinant confers resistance by FAILING to repress,
    # so more pump is made. Its downstream is the pump records curated in rounds 33-36.
    "ARO:3000451": [
    {
        "curated": "2026-08-07T00:00:00Z",
        "precondition": _requires_efflux_repressor,
        "reference": "ARO:3000702",        # CARD's own AcrR definition, the archetype
        "mech": {"ARO:0010000": "AcrR is a repressor of the AcrAB-TolC multidrug efflux complex. AcrR mutations result in high level antibiotic resistance.", "ARO:3000212": "AcrR is a repressor of the AcrAB-TolC multidrug efflux complex. AcrR mutations result in high level antibiotic resistance.", "ARO:0001002": "AcrR is a repressor of the AcrAB-TolC multidrug efflux complex. AcrR mutations result in high level antibiotic resistance.",
                 "ARO:3003588": "AcrR is a repressor of the AcrAB-TolC multidrug efflux complex. AcrR mutations result in high level antibiotic resistance.", "ARO:0010001": "AcrR is a repressor of the AcrAB-TolC multidrug efflux complex. AcrR mutations result in high level antibiotic resistance."},
        "mech_res": "AcrR is a repressor of the AcrAB-TolC multidrug efflux complex. AcrR mutations result in high level antibiotic resistance.",
        "det_res": "AcrR is a repressor of the AcrAB-TolC multidrug efflux complex. AcrR mutations result in high level antibiotic resistance.",
        "res_drug": "AcrR is a repressor of the AcrAB-TolC multidrug efflux complex. AcrR mutations result in high level antibiotic resistance.",
        "note": "Loss of repression: the determinant represses an efflux pump, and mutations in it raise pump expression.",
        "extra_nodes": [
            {"node_id": "pump", "label": "the efflux pump this determinant represses",
             "node_type": "PROTEIN",
             "description": "Which pump differs per record and is named in that record's own definition -- AcrAB-TolC for AcrR, AdeIJK for AdeN, CmeABC for CmeR. The pump mechanisms themselves are curated records (rounds 33-36)."},
            {"node_id": "repression", "label": "repression of efflux pump expression",
             "node_type": "BIOLOGICAL_PROCESS",
             "description": "Ungrounded: negative regulation of transcription exists in GO, but which promoter differs per record."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "repression",
             "predicate": "enables (represses the pump operon)", "predicate_id": "RO:0002327",
             "evidence": [{"reference": "ARO:3000702", "snippet": "AcrR is a repressor of the AcrAB-TolC multidrug efflux complex. AcrR mutations result in high level antibiotic resistance.",
                           "notes": "CARD's definition of AcrR, the archetype. Each record's own definition names the pump IT represses; this config asserts only the shared direction."}]},
            {"subject": "repression", "object": "pump",
             "predicate": "negatively regulates (holds pump expression down)", "predicate_id": "RO:0002212",
             "evidence": [{"reference": "ARO:3000702", "snippet": "AcrR is a repressor of the AcrAB-TolC multidrug efflux complex. AcrR mutations result in high level antibiotic resistance.",
                           "notes": "The wild-type function. Resistance is the loss of it."}]},
            {"subject": "determinant", "object": "repression",
             "predicate": "negatively regulates (mutation lifts the repression)",
             "predicate_id": "RO:0002212",
             "description": "The causal core, and it runs backwards as katG's does (round 27): resistance is the ABSENCE of a function. A mutated repressor stops holding the pump down, so more pump is made.",
             "evidence": [{"reference": "ARO:3000702", "snippet": "AcrR is a repressor of the AcrAB-TolC multidrug efflux complex. AcrR mutations result in high level antibiotic resistance.",
                           "notes": "'AcrR mutations result in high level antibiotic resistance' -- CARD states the direction outright."}]},
            {"subject": "pump", "object": "drug0",
             "predicate": "negatively regulates (more pump means more efflux)",
             "predicate_id": "RO:0002212",
             "description": "The pump's own mechanism is curated on its record; this edge only carries the consequence of making more of it.",
             "evidence": [{"reference": "ARO:3000702", "snippet": "AcrR is a repressor of the AcrAB-TolC multidrug efflux complex. AcrR mutations result in high level antibiotic resistance.",
                           "notes": "The resistance follows from pump over-expression, not from any change to the pump itself."}]},
        ],
    },
        {
            "curated": "2026-08-07T00:00:00Z",
            "precondition": _requires_efflux_activator,
            "reference": "ARO:3000553",        # CARD's own AdeR definition
            "mech": {"ARO:0010000": "AdeR is a positive regulator of AdeABC efflux system.", "ARO:3000212": "AdeR is a positive regulator of AdeABC efflux system.",
                     "ARO:0001002": "AdeR is a positive regulator of AdeABC efflux system.", "ARO:3003588": "AdeR is a positive regulator of AdeABC efflux system.",
                     "ARO:0010001": "AdeR is a positive regulator of AdeABC efflux system."},
            "mech_res": "AdeR is a positive regulator of AdeABC efflux system.",
            "det_res": "AdeR is a positive regulator of AdeABC efflux system.",
            "res_drug": "AdeR is a positive regulator of AdeABC efflux system.",
            "note": "The mirror of round 37: a positive regulator whose over-activity drives pump expression, rather than a repressor whose loss lifts it.",
            "extra_nodes": [
                {"node_id": "pump", "label": "the efflux pump this determinant activates",
                 "node_type": "PROTEIN",
                 "description": "Which pump differs per record and is named in that record's own definition -- AdeABC for AdeR, norA for ArlR, acrAB for Rob. The pump mechanisms are curated records (rounds 33-36)."},
                {"node_id": "activation", "label": "activation of efflux pump expression",
                 "node_type": "BIOLOGICAL_PROCESS",
                 "description": "Ungrounded: positive regulation of transcription exists in GO, but which promoter differs per record."},
            ],
            "extra_edges": [
                {"subject": "determinant", "object": "activation",
                 "predicate": "enables (activates the pump operon)", "predicate_id": "RO:0002327",
                 "evidence": [{"reference": "ARO:3000553", "snippet": "AdeR is a positive regulator of AdeABC efflux system.",
                               "notes": "CARD's definition of AdeR, the archetype. Each record's own definition names the pump IT activates; this config asserts only the shared direction."}]},
                {"subject": "activation", "object": "pump",
                 "predicate": "positively regulates (raises pump expression)", "predicate_id": "RO:0002213",
                 "description": "The direction that distinguishes this config from round 37's: here resistance follows from the regulator DOING something, not from its loss.",
                 "evidence": [{"reference": "ARO:3000553", "snippet": "AdeR is a positive regulator of AdeABC efflux system.",
                               "notes": "A positive regulator raises expression of the system it controls."}]},
                {"subject": "pump", "object": "drug0",
                 "predicate": "negatively regulates (more pump means more efflux)",
                 "predicate_id": "RO:0002212",
                 "evidence": [{"reference": "ARO:3000553", "snippet": "AdeR is a positive regulator of AdeABC efflux system.",
                               "notes": "The pump's own mechanism is curated on its record; this edge carries only the consequence of making more of it."}]},
            ],
        },
        _lps_regulator_config(
            _requires_lps_response_regulator, "ARO:3003582", "BasR",
            "Response regulator for Lipid A modification genes; two-component system "
            "involved in polymyxin resistance",
            "the response regulator, which binds the modification operon's promoter"),
        _lps_regulator_config(
            _requires_lps_sensor_kinase, "ARO:3003583", "BasS",
            "Histidine protein kinase sensor Lipid A modification gene; part of a "
            "two-component system involved in polymyxin resistance",
            "the sensor kinase, which phosphorylates the response regulator"),
    ],
    # ---------------------------------------------------------------------------------
    # ABC efflux subunits (ARO:3000748, ABC complexes only). Same family term as round 33's
    # RND pumps and a genuinely different machine: RND runs on the proton gradient and
    # passes substrate through a central cavity; MacB has NO such cavity and runs on ATP.
    # Reusing round 33's evidence here would assert the wrong energetics on 14 records,
    # which is what the class precondition exists to prevent.
    # ---------------------------------------------------------------------------------
    # RND efflux subunits (ARO:3000748, RND complexes only) -- a NINTH mechanism kind:
    # the drug is neither destroyed, altered, displaced, repelled nor left unactivated. It
    # is captured and pumped back out, so it never reaches its target at a useful
    # concentration.
    #
    # #223 said a family config here would span RND, MFS, ABC, SMR and MATE at once,
    # because the 137 subunit drafts sit flat under ARO:3000748 with no pump-class
    # ancestry. That was true of the SUBUNITS and not of their complexes: each subunit is
    # `part_of` a complex, and the complex is `is_a` RND. The precondition does that two-hop
    # lookup, so the selection is derived from the release rather than hand-listed.
    "ARO:3000748": [
        {
            "curated": "2026-08-07T00:00:00Z",
            "precondition": _requires_pump_class("ARO:0010002", "a major facilitator superfamily (MFS) efflux pump"),
            "reference": "PMID:16675700",
            "mech": {"ARO:0010000": "EmrD is a multidrug transporter from the Major Facilitator Superfamily that expels amphipathic compounds across the inner membrane of Escherichia coli.", "ARO:3000212": "EmrD is a multidrug transporter from the Major Facilitator Superfamily that expels amphipathic compounds across the inner membrane of Escherichia coli.", "ARO:0001002": "EmrD is a multidrug transporter from the Major Facilitator Superfamily that expels amphipathic compounds across the inner membrane of Escherichia coli."},
            "mech_res": "EmrD is a multidrug transporter from the Major Facilitator Superfamily that expels amphipathic compounds across the inner membrane of Escherichia coli.",
            "det_res": [
                {"reference": "PMID:16675700", "snippet": "EmrD is a multidrug transporter from the Major Facilitator Superfamily that expels amphipathic compounds across the inner membrane of Escherichia coli.",
                 "notes": "The transporter and what it expels."},
                {"reference": "PMID:16675700", "snippet": "Two long loops extend into the inner leaflet side of the cell membrane. This region can serve to recognize and bind substrate directly from the lipid bilayer.",
                 "notes": "Yin et al. 2006. The distinctive step: substrate is recognised DIRECTLY FROM THE LIPID BILAYER by loops in the inner leaflet, not captured from the periplasm as RND does."},
            ],
            "res_drug": "EmrD is a multidrug transporter from the Major Facilitator Superfamily that expels amphipathic compounds across the inner membrane of Escherichia coli.",
            "note": "Secondary-transporter efflux, distinct from RND's periplasmic capture and ABC's ATP-driven mechanotransmission.",
            "extra_nodes": [
                {"node_id": "transporter", "label": "MFS transporter with an internal cavity and inner-leaflet loops", "node_type": "STATE",
                 "description": "Ungrounded: the specific transporter differs per record and is on that record's own ARO relations."},
                {"node_id": "export", "label": "xenobiotic detoxification by transmembrane export across the plasma membrane",
                 "node_type": "BIOLOGICAL_PROCESS", "grounding": "GO:1990961"},
            ],
            "extra_edges": [
                {"subject": "determinant", "object": "transporter",
                 "predicate": "part of (the transporter)", "predicate_id": "BFO:0000050",
                 "evidence": [{"reference": "PMID:16675700", "snippet": "EmrD is a multidrug transporter from the Major Facilitator Superfamily that expels amphipathic compounds across the inner membrane of Escherichia coli.",
                               "notes": "The determinant is a component of this transporter."}]},
                {"subject": "transporter", "object": "export",
                 "predicate": "causally upstream of (binds substrate from the bilayer and exports it)", "predicate_id": "RO:0002411",
                 "evidence": [{"reference": "PMID:16675700", "snippet": "Two long loops extend into the inner leaflet side of the cell membrane. This region can serve to recognize and bind substrate directly from the lipid bilayer.",
                               "notes": "Yin et al. 2006. The distinctive step: substrate is recognised DIRECTLY FROM THE LIPID BILAYER by loops in the inner leaflet, not captured from the periplasm as RND does."}]},
                {"subject": "export", "object": "drug0",
                 "predicate": "negatively regulates (lowers the intracellular drug concentration)",
                 "predicate_id": "RO:0002212",
                 "evidence": [{"reference": "PMID:16675700", "snippet": "EmrD is a multidrug transporter from the Major Facilitator Superfamily that expels amphipathic compounds across the inner membrane of Escherichia coli.",
                               "notes": "The drug is expelled before it reaches a useful concentration."}]},
            ],
        },
        {
            "curated": "2026-08-07T00:00:00Z",
            "precondition": _requires_pump_class("ARO:0010003", "a small multidrug resistance (SMR) efflux pump"),
            "reference": "PMID:22178925",
            "mech": {"ARO:0010000": "EmrE is one such transporter in Escherichia coli. It exports a broad class of polyaromatic cation substrates, thus conferring resistance to drug compounds matching this chemical description.", "ARO:3000212": "EmrE is one such transporter in Escherichia coli. It exports a broad class of polyaromatic cation substrates, thus conferring resistance to drug compounds matching this chemical description.", "ARO:0001002": "EmrE is one such transporter in Escherichia coli. It exports a broad class of polyaromatic cation substrates, thus conferring resistance to drug compounds matching this chemical description."},
            "mech_res": "EmrE is one such transporter in Escherichia coli. It exports a broad class of polyaromatic cation substrates, thus conferring resistance to drug compounds matching this chemical description.",
            "det_res": [
                {"reference": "PMID:22178925", "snippet": "EmrE is one such transporter in Escherichia coli. It exports a broad class of polyaromatic cation substrates, thus conferring resistance to drug compounds matching this chemical description.",
                 "notes": "The transporter and what it expels."},
                {"reference": "PMID:22178925", "snippet": "Here we show that asymmetric antiparallel EmrE exchanges between inward- and outward-facing states that are identical except that they have opposite orientation in the membrane.",
                 "notes": "Morrison et al. 2011. The minimal transporter: an ANTIPARALLEL HOMODIMER whose two states are the same structure in opposite membrane orientations, so alternating access is achieved by exchange rather than by a large conformational cycle."},
            ],
            "res_drug": "EmrE is one such transporter in Escherichia coli. It exports a broad class of polyaromatic cation substrates, thus conferring resistance to drug compounds matching this chemical description.",
            "note": "Secondary-transporter efflux, distinct from RND's periplasmic capture and ABC's ATP-driven mechanotransmission.",
            "extra_nodes": [
                {"node_id": "transporter", "label": "antiparallel EmrE-type homodimer", "node_type": "STATE",
                 "description": "Ungrounded: a dimer state rather than a compound."},
                {"node_id": "export", "label": "xenobiotic detoxification by transmembrane export across the plasma membrane",
                 "node_type": "BIOLOGICAL_PROCESS", "grounding": "GO:1990961"},
            ],
            "extra_edges": [
                {"subject": "determinant", "object": "transporter",
                 "predicate": "part of (the transporter)", "predicate_id": "BFO:0000050",
                 "evidence": [{"reference": "PMID:22178925", "snippet": "EmrE is one such transporter in Escherichia coli. It exports a broad class of polyaromatic cation substrates, thus conferring resistance to drug compounds matching this chemical description.",
                               "notes": "The determinant is a component of this transporter."}]},
                {"subject": "transporter", "object": "export",
                 "predicate": "causally upstream of (alternates orientation to export the substrate)", "predicate_id": "RO:0002411",
                 "evidence": [{"reference": "PMID:22178925", "snippet": "Here we show that asymmetric antiparallel EmrE exchanges between inward- and outward-facing states that are identical except that they have opposite orientation in the membrane.",
                               "notes": "Morrison et al. 2011. The minimal transporter: an ANTIPARALLEL HOMODIMER whose two states are the same structure in opposite membrane orientations, so alternating access is achieved by exchange rather than by a large conformational cycle."}]},
                {"subject": "export", "object": "drug0",
                 "predicate": "negatively regulates (lowers the intracellular drug concentration)",
                 "predicate_id": "RO:0002212",
                 "evidence": [{"reference": "PMID:22178925", "snippet": "EmrE is one such transporter in Escherichia coli. It exports a broad class of polyaromatic cation substrates, thus conferring resistance to drug compounds matching this chemical description.",
                               "notes": "The drug is expelled before it reaches a useful concentration."}]},
            ],
        },
    {
        "curated": "2026-08-06T00:00:00Z",
        "precondition": _requires_pump_class("ARO:0010004", "a resistance-nodulation-cell division (RND) efflux pump"),
        "reference": "PMID:16915237",      # Murakami et al. 2006, Nature
        "mech": {"ARO:0010000": "The structures indicate that drugs are exported by a three-step functionally rotating mechanism in which substrates undergo ordered binding change.", "ARO:3000212": "The structures indicate that drugs are exported by a three-step functionally rotating mechanism in which substrates undergo ordered binding change.", "ARO:0001002": "The structures indicate that drugs are exported by a three-step functionally rotating mechanism in which substrates undergo ordered binding change."},
        "mech_res": "The structures indicate that drugs are exported by a three-step functionally rotating mechanism in which substrates undergo ordered binding change.",
        "det_res": [
            {"reference": "PMID:16915237", "snippet": "AcrB is a principal multidrug efflux transporter in Escherichia coli that cooperates with an outer-membrane channel, TolC, and a membrane-fusion protein, AcrA.",
             "notes": "Murakami et al. 2006. RND resistance is a property of a THREE-part machine: the transporter, a membrane-fusion protein and an outer-membrane channel. A subunit record is a component of that, which is why the graph says `part of` a complex rather than making the subunit the whole pump."},
            {"reference": "PMID:16915237", "snippet": "The structures indicate that drugs are exported by a three-step functionally rotating mechanism in which substrates undergo ordered binding change.",
             "notes": "And the mechanism, from crystal structures of all three conformational states."},
        ],
        "res_drug": "The structures indicate that drugs are exported by a three-step functionally rotating mechanism in which substrates undergo ordered binding change.",
        "note": "Efflux: the drug is captured and exported, so it never reaches its target at a useful concentration.",
        "extra_nodes": [
            {"node_id": "pump_complex", "label": "tripartite RND efflux complex", "node_type": "STATE",
             "description": "Transporter + membrane-fusion protein + outer-membrane channel. Ungrounded here: the specific complex differs per record and is named in that record's own ARO relations."},
            {"node_id": "binding_pocket", "label": "periplasmic multi-site drug binding pocket",
             "node_type": "STATE",
             "description": "Where the substrate is captured. Ungrounded: no ontology term denotes it."},
            {"node_id": "export", "label": "xenobiotic detoxification by transmembrane export across the plasma membrane",
             "node_type": "BIOLOGICAL_PROCESS", "grounding": "GO:1990961"},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "pump_complex",
             "predicate": "part of (a subunit of the tripartite pump)", "predicate_id": "BFO:0000050",
             "evidence": [{"reference": "PMID:16915237", "snippet": "AcrB is a principal multidrug efflux transporter in Escherichia coli that cooperates with an outer-membrane channel, TolC, and a membrane-fusion protein, AcrA.",
                           "notes": "The three parts named. Which complex this particular subunit belongs to is on the record's own ARO part_of relation."}]},
            {"subject": "drug0", "object": "binding_pocket",
             "predicate": "molecularly interacts with (is captured in the pocket)",
             "predicate_id": "RO:0002436",
             "description": "Multi-site binding in an aromatic pocket is what lets one pump handle chemically unrelated drugs.",
             "evidence": [{"reference": "PMID:16915237", "snippet": "Bound substrate was found in the periplasmic domain of one of the three protomers. The voluminous binding pocket is aromatic and allows multi-site binding.",
                           "notes": "Substrate seen bound in the periplasmic domain of one protomer."}]},
            {"subject": "pump_complex", "object": "export",
             "predicate": "causally upstream of (exports the drug)", "predicate_id": "RO:0002411",
             "evidence": [{"reference": "PMID:16915237", "snippet": "The structures indicate that drugs are exported by a three-step functionally rotating mechanism in which substrates undergo ordered binding change.",
                           "notes": "Three protomers, three functional states, one ordered cycle."}]},
            {"subject": "export", "object": "drug0",
             "predicate": "negatively regulates (lowers the intracellular drug concentration)",
             "predicate_id": "RO:0002212",
             "description": "The causal core: the drug is removed before it reaches its target, so nothing about the target need change.",
             "evidence": [{"reference": "PMID:16915237", "snippet": "The structures indicate that drugs are exported by a three-step functionally rotating mechanism in which substrates undergo ordered binding change.",
                           "notes": "The transport cycle is what the resistance consists of."}]},
        ],
    },
    {
        "curated": "2026-08-07T00:00:00Z",
        "precondition": _requires_pump_class("ARO:0010001", "an ATP-binding cassette (ABC) efflux pump"),
        "reference": "PMID:29109272",      # Crow, Greene, Kaplan & Koronakis 2017, PNAS
        "mech": {"ARO:0010000": "The MacB transmembrane domain lacks a central cavity through which substrates could be passed, but instead conveys conformational changes from one side of the membrane to the other, a process we term mechanotransmission.", "ARO:3000212": "The MacB transmembrane domain lacks a central cavity through which substrates could be passed, but instead conveys conformational changes from one side of the membrane to the other, a process we term mechanotransmission.", "ARO:0001002": "The MacB transmembrane domain lacks a central cavity through which substrates could be passed, but instead conveys conformational changes from one side of the membrane to the other, a process we term mechanotransmission."},
        "mech_res": "The MacB transmembrane domain lacks a central cavity through which substrates could be passed, but instead conveys conformational changes from one side of the membrane to the other, a process we term mechanotransmission.",
        "det_res": [
            {"reference": "PMID:29109272", "snippet": "MacB is an ABC transporter that collaborates with the MacA adaptor protein and TolC exit duct to drive efflux of antibiotics and enterotoxin STII out of the bacterial cell.",
             "notes": "Crow et al. 2017. Tripartite like RND -- transporter, adaptor, exit duct -- but the transporter is ATP-driven."},
            {"reference": "PMID:29109272", "snippet": "The MacB transmembrane domain lacks a central cavity through which substrates could be passed, but instead conveys conformational changes from one side of the membrane to the other, a process we term mechanotransmission.",
             "notes": "And the part that makes it a different machine: no central cavity, so the substrate is not passed THROUGH the transmembrane domain at all."},
        ],
        "res_drug": "MacB is an ABC transporter that collaborates with the MacA adaptor protein and TolC exit duct to drive efflux of antibiotics and enterotoxin STII out of the bacterial cell.",
        "note": "ATP-driven efflux by mechanotransmission, distinct from RND's proton-driven transport through a central cavity.",
        "extra_nodes": [
            {"node_id": "pump_complex", "label": "tripartite ABC efflux complex", "node_type": "STATE",
             "description": "Transporter + adaptor + exit duct. Ungrounded: the specific complex differs per record and is on that record's own ARO relations."},
            {"node_id": "atp_cycle", "label": "ATP-driven nucleotide-binding-domain dimerisation",
             "node_type": "STATE",
             "description": "The energising step. Ungrounded: recorded as the conformational cycle the structures describe."},
            {"node_id": "export", "label": "xenobiotic detoxification by transmembrane export across the plasma membrane",
             "node_type": "BIOLOGICAL_PROCESS", "grounding": "GO:1990961"},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "pump_complex",
             "predicate": "part of (a subunit of the tripartite pump)", "predicate_id": "BFO:0000050",
             "evidence": [{"reference": "PMID:29109272", "snippet": "MacB is an ABC transporter that collaborates with the MacA adaptor protein and TolC exit duct to drive efflux of antibiotics and enterotoxin STII out of the bacterial cell.",
                           "notes": "The three parts named; which complex this subunit belongs to is on its own ARO part_of relation."}]},
            {"subject": "atp_cycle", "object": "pump_complex",
             "predicate": "causally upstream of (drives the transport cycle)", "predicate_id": "RO:0002411",
             "description": "ATP rather than the proton gradient -- the energetic difference from RND.",
             "evidence": [{"reference": "PMID:29109272", "snippet": "Comparison of ATP-bound and nucleotide-free states reveals how reversible dimerization of the nucleotide binding domains drives opening and closing of the MacB periplasmic domains via concerted movements of the second transmembrane segment and major coupling helix.",
                           "notes": "Reversible dimerisation of the nucleotide-binding domains, from ATP-bound and nucleotide-free structures."}]},
            {"subject": "pump_complex", "object": "export",
             "predicate": "causally upstream of (exports the drug by mechanotransmission)",
             "predicate_id": "RO:0002411",
             "description": "The distinctive step: conformational change is conveyed across the membrane instead of substrate being passed through it.",
             "evidence": [{"reference": "PMID:29109272", "snippet": "The MacB transmembrane domain lacks a central cavity through which substrates could be passed, but instead conveys conformational changes from one side of the membrane to the other, a process we term mechanotransmission.",
                           "notes": "Crow et al. 2017 name the mechanism and note the absence of a central cavity."}]},
            {"subject": "export", "object": "drug0",
             "predicate": "negatively regulates (lowers the intracellular drug concentration)",
             "predicate_id": "RO:0002212",
             "evidence": [{"reference": "PMID:29109272", "snippet": "MacB is an ABC transporter that collaborates with the MacA adaptor protein and TolC exit duct to drive efflux of antibiotics and enterotoxin STII out of the bacterial cell.",
                           "notes": "The pump drives antibiotics out of the cell; the resistance is that removal."}]},
        ],
    },
    ],
    # ---------------------------------------------------------------------------------
    # mprF -- ELECTROSTATIC REPULSION (ARO:3003580, mprF records only). An eighth kind of
    # mechanism: the drug is neither destroyed, altered, displaced nor pumped out. It is
    # repelled, because the determinant changes the SURFACE CHARGE of the envelope so a
    # cationic peptide no longer reaches it.
    "ARO:3003580": {
        "curated": "2026-08-06T00:00:00Z",
        "precondition": _requires_mprf,
        "reference": "PMID:11342591",      # Peschel et al. 2001, J Exp Med
        # The ids the records actually carry. My first four were guesses and the
        # UncoveredMechanism guard (#203) refused all 10 records rather than substituting
        # -- 0 written, which is exactly what it is for.
        "mech": {
            "ARO:3003588": "As this unusual modification leads to a reduced negative charge of the membrane surface, MprF-mediated peptide resistance",   # antibiotic resistance by charge alteration
            "ARO:0001001": "As this unusual modification leads to a reduced negative charge of the membrane surface, MprF-mediated peptide resistance",   # antibiotic target alteration
            "ARO:3000212": "We describe a novel staphylococcal gene, mprF, which determines resistance to several host defense peptides such as defensins and protegrins.",
        },
        "mech_res": "As this unusual modification leads to a reduced negative charge of the membrane surface, MprF-mediated peptide resistance",
        "det_res": [
            {"reference": "PMID:11342591", "snippet": "We describe a novel staphylococcal gene, mprF, which determines resistance to several host defense peptides such as defensins and protegrins.",
             "notes": "Peschel et al. 2001 identified the gene by the resistance it confers to defensins and protegrins."},
            {"reference": "PMID:11342591", "snippet": "An mprF mutant strain was killed considerably faster by human neutrophils and exhibited attenuated virulence in mice, indicating a key role for defensin resistance in the pathogenicity of S. aureus.",
             "notes": "And showed the loss-of-function phenotype in the relevant setting: the mutant is killed faster by human neutrophils and is attenuated in mice."},
        ],
        "res_drug": "We describe a novel staphylococcal gene, mprF, which determines resistance to several host defense peptides such as defensins and protegrins.",
        "note": "Electrostatic repulsion: lysinylating phosphatidylglycerol lowers the membrane's net negative charge, so cationic peptides are repelled.",
        "extra_nodes": [
            {"node_id": "lysyl_pg", "label": "lysyl-phosphatidylglycerol", "node_type": "CHEMICAL",
             "description": "The modified lipid. Ungrounded: recorded as a modification of phosphatidylglycerol with L-lysine rather than by a CURIE this corpus can cite."},
            {"node_id": "surface_charge", "label": "reduced net negative charge of the membrane surface",
             "node_type": "QUALITY",
             "description": "The property that does the work. Ungrounded: no ontology term for the envelope's net charge."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "lysyl_pg",
             "predicate": "causally upstream of (lysinylates phosphatidylglycerol)",
             "predicate_id": "RO:0002411",
             "description": "Shown by absence: the mutant no longer makes the modified lipid.",
             "evidence": [{"reference": "PMID:11342591", "snippet": "Analysis of membrane lipids demonstrated that the mprF mutant no longer modifies phosphatidylglycerol with l-lysine.",
                           "notes": "Peschel et al. 2001, membrane lipid analysis of the mutant."}]},
            {"subject": "lysyl_pg", "object": "surface_charge",
             "predicate": "causally upstream of (lowers the net negative charge)",
             "predicate_id": "RO:0002411",
             "evidence": [{"reference": "PMID:11342591", "snippet": "As this unusual modification leads to a reduced negative charge of the membrane surface, MprF-mediated peptide resistance",
                           "notes": "Adding a positively charged lysine to an anionic lipid is what reduces the surface's net negative charge."}]},
            {"subject": "surface_charge", "object": "drug0",
             "predicate": "negatively regulates (repels the cationic peptide)",
             "predicate_id": "RO:0002212",
             "description": "The causal core, and an eighth kind of mechanism: the drug is repelled rather than destroyed, altered, displaced or pumped out.",
             "evidence": [{"reference": "PMID:11342591", "snippet": "As this unusual modification leads to a reduced negative charge of the membrane surface, MprF-mediated peptide resistance",
                           "notes": "The paper states the causal direction explicitly -- the reduced charge is what mediates the peptide resistance."}]},
        ],
    },
    # ---------------------------------------------------------------------------------
    # Ribosomal protection of tetracycline (ARO:3000185, tetracycline records only) -- a
    # SEVENTH mechanism kind. The determinant neither modifies the drug nor the target: it
    # removes the drug FROM the target. Nothing curated so far has that shape.
    "ARO:3000185": [
    {
        "curated": "2026-08-06T00:00:00Z",
        "precondition": _requires_tetracycline,
        "reference": "PMID:23027944",      # Donhofer et al. 2012, PNAS
        "mech": {"ARO:0001003": "Ribosome protection proteins (RPPs) confer tetracycline resistance by binding to the ribosome and chasing the drug from its binding site."},
        "mech_res": "Ribosome protection proteins (RPPs) confer tetracycline resistance by binding to the ribosome and chasing the drug from its binding site.",
        "det_res": [
            {"reference": "PMID:23027944", "snippet": "Ribosome protection proteins (RPPs) confer tetracycline resistance by binding to the ribosome and chasing the drug from its binding site.",
             "notes": "Donhofer et al. 2012. The mechanism in one sentence: bind the ribosome, chase the drug off it."},
            {"reference": "PMID:23027944", "snippet": "Moreover, we observe direct interaction between domain IV of TetM and the tetracycline binding site and identify residues critical for conferring tetracycline resistance.",
             "notes": "And the cryo-EM structure that made it direct rather than inferred, plus the residues that matter."},
        ],
        "res_drug": "Ribosome protection proteins (RPPs) confer tetracycline resistance by binding to the ribosome and chasing the drug from its binding site.",
        "note": "Target protection: the drug is displaced from a target that is not itself altered.",
        "extra_nodes": [
            {"node_id": "ribosome_binding", "label": "ribosome binding",
             "node_type": "MOLECULAR_FUNCTION", "grounding": "GO:0043022"},
            {"node_id": "tet_site", "label": "tetracycline binding site on the ribosome",
             "node_type": "STATE",
             "description": "The site the drug occupies and the RPP clears. Ungrounded: no ontology term denotes it."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "ribosome_binding",
             "predicate": "enables (binds the ribosome)", "predicate_id": "RO:0002327",
             "evidence": [{"reference": "PMID:23027944", "snippet": "Ribosome protection proteins (RPPs) confer tetracycline resistance by binding to the ribosome and chasing the drug from its binding site.",
                           "notes": "Binding the ribosome is the first half of the mechanism."}]},
            {"subject": "drug0", "object": "tet_site",
             "predicate": "molecularly interacts with (occupies its binding site)",
             "predicate_id": "RO:0002436",
             "requires": {"drug0": "ARO:3000050"},
             "evidence": [{"reference": "PMID:23027944", "snippet": "Ribosome protection proteins (RPPs) confer tetracycline resistance by binding to the ribosome and chasing the drug from its binding site.",
                           "notes": "Drug action: the site the RPP exists to clear."}]},
            {"subject": "ribosome_binding", "object": "tet_site",
             "predicate": "negatively regulates (chases the drug from the site)",
             "predicate_id": "RO:0002212",
             "description": "The causal core, and the seventh kind of mechanism in this corpus: the drug is displaced from a target that is not itself altered.",
             "evidence": [
                 {"reference": "PMID:23027944", "snippet": "Moreover, we observe direct interaction between domain IV of TetM and the tetracycline binding site and identify residues critical for conferring tetracycline resistance.",
                  "notes": "Domain IV of TetM contacts the tetracycline binding site directly, seen by cryo-EM at 7.2 A."},
                 {"reference": "PMID:23027944", "snippet": "The current model for the mechanism of action of RPPs proposes that drug release is indirect and achieved via conformational changes within the drug-binding site induced upon binding of the RPP to the ribosome.",
                  "notes": "The prior model had release happening INDIRECTLY via conformational change. The paper's own framing is that its structure supports direct dislodgement instead, so both readings are recorded rather than only the newer one."},
             ]},
        ],
    },
        {
            "curated": "2026-08-07T00:00:00Z",
            "precondition": _requires_fusidane,
            "reference": "PMID:22308410",      # Cox et al. 2012, PNAS
            "mech": {"ARO:0001003": "By binding to EF-G on the ribosome, FusB-type proteins promote the dissociation of stalled ribosome-EF-G-GDP complexes that form in the presence of FA, thereby allowing the ribosomes to resume translation.", "ARO:3000212": "By binding to EF-G on the ribosome, FusB-type proteins promote the dissociation of stalled ribosome-EF-G-GDP complexes that form in the presence of FA, thereby allowing the ribosomes to resume translation."},
            "mech_res": "By binding to EF-G on the ribosome, FusB-type proteins promote the dissociation of stalled ribosome-EF-G-GDP complexes that form in the presence of FA, thereby allowing the ribosomes to resume translation.",
            "det_res": [
                {"reference": "PMID:22308410", "snippet": "These proteins bind to elongation factor G (EF-G), the target of FA, and rescue translation from FA-mediated inhibition by an unknown mechanism.",
                 "notes": "Cox et al. 2012. FusB-type proteins bind EF-G, which is fusidic acid's target."},
                {"reference": "PMID:22308410", "snippet": "By binding to EF-G on the ribosome, FusB-type proteins promote the dissociation of stalled ribosome-EF-G-GDP complexes that form in the presence of FA, thereby allowing the ribosomes to resume translation.",
                 "notes": "And the mechanism, which is NOT TetM's: the drug is not dislodged. The stalled complex the drug creates is dissociated, and translation resumes."},
            ],
            "res_drug": "By binding to EF-G on the ribosome, FusB-type proteins promote the dissociation of stalled ribosome-EF-G-GDP complexes that form in the presence of FA, thereby allowing the ribosomes to resume translation.",
            "note": "Target protection by rescuing a stalled complex rather than by displacing the drug.",
            "extra_nodes": [
                {"node_id": "efg", "label": "elongation factor G (EF-G), the drug's target",
                 "node_type": "PROTEIN",
                 "description": "Ungrounded: the specific EF-G differs per organism and the corpus holds no EF-G trait record."},
                {"node_id": "stalled", "label": "stalled ribosome-EF-G-GDP complex", "node_type": "STATE",
                 "description": "What fusidic acid produces, and what FusB dissociates. Ungrounded."},
                {"node_id": "zinc_finger", "label": "four-cysteine zinc finger domain of FusB-type proteins",
                 "node_type": "DOMAIN",
                 "description": "The high-affinity EF-G interaction module. Ungrounded: a unique fold with no KB trait record."},
            ],
            "extra_edges": [
                {"subject": "zinc_finger", "object": "determinant",
                 "predicate": "part of (the EF-G-binding domain)", "predicate_id": "BFO:0000050",
                 "evidence": [{"reference": "PMID:22308410", "snippet": "Here we show that the FusB family are two-domain metalloproteins, the C-terminal domain of which contains a four-cysteine zinc finger with a unique structural fold.",
                               "notes": "Cox et al. 2012; this C-terminal domain mediates the high-affinity interaction with EF-G."}]},
                {"subject": "drug0", "object": "stalled",
                 "predicate": "causally upstream of (stalls the ribosome)", "predicate_id": "RO:0002411",
                 "requires": {"drug0": "ARO:3007153"},
                 "description": "Drug action: fusidic acid traps EF-G on the ribosome after GTP hydrolysis.",
                 "evidence": [{"reference": "PMID:22308410", "snippet": "By binding to EF-G on the ribosome, FusB-type proteins promote the dissociation of stalled ribosome-EF-G-GDP complexes that form in the presence of FA, thereby allowing the ribosomes to resume translation.",
                               "notes": "The complexes 'form in the presence of FA'."}]},
                {"subject": "determinant", "object": "stalled",
                 "predicate": "negatively regulates (dissociates the stalled complex)",
                 "predicate_id": "RO:0002212",
                 "description": "The causal core, and it differs from TetM (round 31): the drug is not displaced. The complex it creates is taken apart, so translation resumes with the drug still present.",
                 "evidence": [{"reference": "PMID:22308410", "snippet": "By binding to EF-G on the ribosome, FusB-type proteins promote the dissociation of stalled ribosome-EF-G-GDP complexes that form in the presence of FA, thereby allowing the ribosomes to resume translation.",
                               "notes": "Cox et al. 2012."}]},
                {"subject": "determinant", "object": "efg",
                 "predicate": "molecularly interacts with (binds the target)", "predicate_id": "RO:0002436",
                 "evidence": [{"reference": "PMID:22308410", "snippet": "These proteins bind to elongation factor G (EF-G), the target of FA, and rescue translation from FA-mediated inhibition by an unknown mechanism.",
                               "notes": "The protection is by binding the TARGET, not the drug."}]},
            ],
        },
        {
            "curated": "2026-08-07T00:00:00Z",
            "precondition": _requires_rifamycin_protection,
            "reference": "PMID:35907401",      # Surette et al. 2022, Mol Cell
            "mech": {"ARO:0001003": "HelR forms a complex with RNAP and rescues transcription inhibition by displacing rifamycins from RNAP, thereby providing resistance by target protection.", "ARO:3000212": "HelR forms a complex with RNAP and rescues transcription inhibition by displacing rifamycins from RNAP, thereby providing resistance by target protection."},
            "mech_res": "HelR forms a complex with RNAP and rescues transcription inhibition by displacing rifamycins from RNAP, thereby providing resistance by target protection.",
            "det_res": [
                {"reference": "PMID:35907401", "snippet": "HelR forms a complex with RNAP and rescues transcription inhibition by displacing rifamycins from RNAP, thereby providing resistance by target protection.",
                 "notes": "Surette et al. 2022. The paper names the mechanism class outright -- 'resistance by target protection' -- and the mode is DISPLACEMENT, as TetM's is (round 31), not FusB's rescue of a stalled complex (round 44)."},
                {"reference": "PMID:35907401", "snippet": "Rifamycin antibiotics such as rifampin are potent inhibitors of prokaryotic RNA polymerase (RNAP) used to treat tuberculosis and other bacterial infections.",
                 "notes": "And what is being protected: RNAP, the target rounds 26's rpoB records alter instead."},
            ],
            "res_drug": "HelR forms a complex with RNAP and rescues transcription inhibition by displacing rifamycins from RNAP, thereby providing resistance by target protection.",
            "note": "Target protection of RNA polymerase by displacing the drug -- the same mode as TetM, on a different target.",
            "extra_nodes": [
                {"node_id": "rnap", "label": "bacterial RNA polymerase, the drug's target",
                 "node_type": "PROTEIN",
                 "description": "The same target rpoB records alter (round 26). Ungrounded: the corpus holds no RNAP complex trait record."},
                {"node_id": "inhibited", "label": "rifamycin-inhibited RNA polymerase", "node_type": "STATE",
                 "description": "Transcription blocked by bound drug. Ungrounded."},
            ],
            "extra_edges": [
                {"subject": "drug0", "object": "inhibited",
                 "predicate": "causally upstream of (inhibits transcription)", "predicate_id": "RO:0002411",
                 "requires": {"drug0": "ARO:3000157"},
                 "evidence": [{"reference": "PMID:35907401", "snippet": "Rifamycin antibiotics such as rifampin are potent inhibitors of prokaryotic RNA polymerase (RNAP) used to treat tuberculosis and other bacterial infections.",
                               "notes": "Drug action: rifamycins are potent RNAP inhibitors."}]},
                {"subject": "determinant", "object": "rnap",
                 "predicate": "molecularly interacts with (forms a complex with RNAP)",
                 "predicate_id": "RO:0002436",
                 "evidence": [{"reference": "PMID:35907401", "snippet": "HelR forms a complex with RNAP and rescues transcription inhibition by displacing rifamycins from RNAP, thereby providing resistance by target protection.",
                               "notes": "Protection works by binding the TARGET, as FusB does with EF-G."}]},
                {"subject": "determinant", "object": "inhibited",
                 "predicate": "negatively regulates (displaces the drug from RNAP)",
                 "predicate_id": "RO:0002212",
                 "description": "The causal core. TetM's mode -- the drug is removed from the target -- applied to RNA polymerase rather than the ribosome.",
                 "evidence": [{"reference": "PMID:35907401", "snippet": "HelR forms a complex with RNAP and rescues transcription inhibition by displacing rifamycins from RNAP, thereby providing resistance by target protection.",
                               "notes": "Surette et al. 2022."}]},
            ],
        },
    ],
    # ---------------------------------------------------------------------------------
    # ethA / EtaA -- the ethionamide half of round 27's mechanism kind (ARO:3003456).
    # Ethionamide is a prodrug like isoniazid, and EthA is its activator, so a defective
    # EthA leaves it inert. Same shape as katG, and the source paper draws the parallel
    # itself: the activated product is "remarkably similar in structure" to isoniazid's.
    #
    # Deferred from round 27 because its characterisation was not found then; the searches
    # that round ran surfaced recent BOOSTER work (MymA, VirS, alpibectir) instead. Fetching
    # PMID:10944230 directly rather than by title is what found it.
    "ARO:3003456": {
        "curated": "2026-08-06T00:00:00Z",
        "reference": "PMID:10944230",      # DeBarber, Mdluli, Bosman, Bekker & Barry 2000, PNAS
        "mech": {"ARO:3000212": "We have demonstrated that overproduction of Rv3855 (EtaR), a putative regulatory protein from MTb, confers ETA resistance whereas overproduction of an adjacent, clustered monooxygenase (Rv3854c, EtaA) confers ETA hypersensitivity."},
        "mech_res": "We have demonstrated that overproduction of Rv3855 (EtaR), a putative regulatory protein from MTb, confers ETA resistance whereas overproduction of an adjacent, clustered monooxygenase (Rv3854c, EtaA) confers ETA hypersensitivity.",
        "det_res": [
            {"reference": "PMID:10944230", "snippet": "We have demonstrated that overproduction of Rv3855 (EtaR), a putative regulatory protein from MTb, confers ETA resistance whereas overproduction of an adjacent, clustered monooxygenase (Rv3854c, EtaA) confers ETA hypersensitivity.",
             "notes": "DeBarber et al. 2000, demonstrated by its CONVERSE: overproducing EtaA makes cells HYPERsensitive, so less of it means less activation and more resistance. The same paper shows overproducing the regulator EtaR confers resistance, which is the same fact from the other side."},
            {"reference": "PMID:10944230", "snippet": "Synthesis of radiolabeled ETA and an examination of drug metabolites formed by whole cells of Mycobacterium tuberculosis (MTb) have allowed us to demonstrate that ETA is activated by S-oxidation before interacting with its cellular target.",
             "notes": "And what the activation is: S-oxidation, shown with radiolabelled drug and metabolite analysis in whole cells."},
        ],
        "res_drug": "Synthesis of radiolabeled ETA and an examination of drug metabolites formed by whole cells of Mycobacterium tuberculosis (MTb) have allowed us to demonstrate that ETA is activated by S-oxidation before interacting with its cellular target.",
        "note": "Prodrug activation loss, as katG is for isoniazid: a defective EthA leaves ethionamide inert.",
        "extra_nodes": [
            {"node_id": "monooxygenase", "label": "monooxygenase activity (EthA/EtaA)",
             "node_type": "MOLECULAR_FUNCTION", "grounding": "GO:0004497"},
            {"node_id": "eta", "label": "ethionamide (inert prodrug)", "node_type": "CHEMICAL",
             "grounding": "CHEBI:4885"},
            {"node_id": "activated_eta",
             "label": "S-oxidised ethionamide (4-pyridylmethanol product)", "node_type": "STATE",
             "description": "The activated species. Ungrounded: the paper characterises it as a 4-pyridylmethanol product without a CURIE this corpus can cite."},
            {"node_id": "inha_gene", "label": "inhA (the shared target of isoniazid and ethionamide)",
             "node_type": "PROTEIN", "grounding": "ARO:3003417",
             "description": "KB record, curated in round 28 -- the target both prodrugs converge on."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "monooxygenase",
             "predicate": "enables (S-oxidation of the prodrug)", "predicate_id": "RO:0002327",
             "evidence": [{"reference": "PMID:10944230", "snippet": "We have demonstrated that overproduction of Rv3855 (EtaR), a putative regulatory protein from MTb, confers ETA resistance whereas overproduction of an adjacent, clustered monooxygenase (Rv3854c, EtaA) confers ETA hypersensitivity.",
                           "notes": "EtaA (Rv3854c) is identified in this paper as the clustered monooxygenase whose level sets ethionamide sensitivity."}]},
            {"subject": "eta", "object": "activated_eta",
             "predicate": "causally upstream of (is S-oxidised)", "predicate_id": "RO:0002411",
             "evidence": [{"reference": "PMID:10944230", "snippet": "Synthesis of radiolabeled ETA and an examination of drug metabolites formed by whole cells of Mycobacterium tuberculosis (MTb) have allowed us to demonstrate that ETA is activated by S-oxidation before interacting with its cellular target.",
                           "notes": "Activation precedes target engagement -- the drug as given does nothing."}]},
            {"subject": "monooxygenase", "object": "activated_eta",
             "predicate": "causally upstream of (activates the prodrug)", "predicate_id": "RO:0002411",
             "evidence": [
                 {"reference": "PMID:10944230", "snippet": "We have demonstrated that overproduction of Rv3855 (EtaR), a putative regulatory protein from MTb, confers ETA resistance whereas overproduction of an adjacent, clustered monooxygenase (Rv3854c, EtaA) confers ETA hypersensitivity.",
                  "notes": "More EtaA, more sensitivity: the activity is what converts the prodrug."},
                 {"reference": "PMID:10944230", "snippet": "ETA is metabolized by MTb to a 4-pyridylmethanol product remarkably similar in structure to that formed by the activation of isoniazid by the catalase-peroxidase KatG.",
                  "notes": "And the product is 'remarkably similar in structure' to isoniazid's KatG-activated product, which is why the two drugs share a target and a resistance logic (round 27)."},
             ]},
            {"subject": "activated_eta", "object": "inha_gene",
             "predicate": "negatively regulates (inhibits the shared target)", "predicate_id": "RO:0002212",
             "description": "Ethionamide and isoniazid converge on InhA, whose own record carries both resistance routes (round 28).",
             "evidence": [{"reference": "PMID:10944230", "snippet": "Synthesis of radiolabeled ETA and an examination of drug metabolites formed by whole cells of Mycobacterium tuberculosis (MTb) have allowed us to demonstrate that ETA is activated by S-oxidation before interacting with its cellular target.",
                           "notes": "The paper says activation happens 'before interacting with its cellular target'; that the target is InhA is curated on ARO:3003417 from PMID:8284673, which showed inhA mutations confer resistance to BOTH drugs."}]},
            {"subject": "determinant", "object": "monooxygenase",
             "predicate": "negatively regulates (the defective EthA cannot activate the prodrug)",
             "predicate_id": "RO:0002212",
             "description": "The causal core, and it runs backwards as katG's does: resistance is the ABSENCE of an activity.",
             "evidence": [{"reference": "PMID:10944230", "snippet": "We have demonstrated that overproduction of Rv3855 (EtaR), a putative regulatory protein from MTb, confers ETA resistance whereas overproduction of an adjacent, clustered monooxygenase (Rv3854c, EtaA) confers ETA hypersensitivity.",
                           "notes": "Shown by the converse rather than by knockout: overproduction gives hypersensitivity, so loss gives resistance."}]},
        ],
    },
    # ---------------------------------------------------------------------------------
    # 16S rRNA / aminoglycoside (ARO:3003666) -- the first family whose determinant is NOT
    # A PROTEIN. 45 records, and `determinant_node_type` exists for them (#215).
    #
    # It is also structurally unlike every earlier family: there is no `part of` edge to a
    # Pfam domain and no `member of` a family, because the corpus holds no rRNA trait
    # records to point at. That is a real gap and is recorded in #215 rather than papered
    # over by routing through a ribosomal protein no cited paper implicates.
    "ARO:3003666": {
        "curated": "2026-08-06T00:00:00Z",
        "determinant_node_type": "NUCLEIC_ACID",
        "reference": "PMID:10357824",      # Recht, Douthwaite & Puglisi 1999, EMBO J
        "mech": {"ARO:3000212": "Expression in E.coli of plasmid-encoded 16S rRNA containing an A1408 to G substitution confers resistance to a subclass of the aminoglycoside antibiotics that contain a 6' amino group on ring I."},
        "mech_res": "Chemical footprinting experiments indicate that resistance arises from the lower affinity of the drug for the eukaryotic rRNA sequence.",
        "det_res": [
            {"reference": "PMID:10357824", "snippet": "Expression in E.coli of plasmid-encoded 16S rRNA containing an A1408 to G substitution confers resistance to a subclass of the aminoglycoside antibiotics that contain a 6' amino group on ring I.",
             "notes": "Recht et al. 1999 built the substitution into plasmid-encoded 16S rRNA and measured resistance -- construction, not association. Note the scope: a SUBCLASS of aminoglycosides, those with a 6' amino group on ring I."},
            {"reference": "PMID:10357824", "snippet": "Chemical footprinting experiments indicate that resistance arises from the lower affinity of the drug for the eukaryotic rRNA sequence.",
             "notes": "And the mechanism, by chemical footprinting: lower affinity of the drug for the substituted sequence."},
        ],
        "res_drug": "We also describe the crystal structure of the 30S subunit complexed with the antibiotics paromomycin, streptomycin and spectinomycin, which interfere with decoding and translocation.",
        "note": "Target alteration in RNA: a substitution in the 16S decoding site lowers aminoglycoside affinity. The same position is what makes these drugs prokaryote-selective.",
        "extra_nodes": [
            {"node_id": "decoding_site",
             "label": "16S rRNA decoding site (A site), around residues A1408, A1492 and A1493",
             "node_type": "NUCLEIC_ACID",
             "description": "The aminoglycoside binding site. Ungrounded: no ontology term denotes this site, the same gap as the QRDR and RRDR in earlier rounds."},
            {"node_id": "decoding", "label": "translation", "node_type": "BIOLOGICAL_PROCESS",
             "grounding": "GO:0006412",
             "description": "Decoding and translocation are the steps these drugs interfere with."},
        ],
        "extra_edges": [
            {"subject": "decoding_site", "object": "determinant",
             "predicate": "part of (the decoding site of this rRNA)", "predicate_id": "BFO:0000050",
             "evidence": [{"reference": "PMID:11014183", "snippet": "This work reveals the structural basis for the action of these antibiotics, and leads to a model for the role of the universally conserved 16S RNA residues A1492 and A1493 in the decoding process.",
                           "notes": "Carter et al. 2000 place A1492 and A1493 in the decoding process; Recht et al. 1999 place 1408 in the same drug-binding site."}]},
            {"subject": "decoding_site", "object": "decoding",
             "predicate": "causally upstream of (decoding and translocation)", "predicate_id": "RO:0002411",
             "evidence": [{"reference": "PMID:11014183", "snippet": "This work reveals the structural basis for the action of these antibiotics, and leads to a model for the role of the universally conserved 16S RNA residues A1492 and A1493 in the decoding process.",
                           "notes": "The universally conserved residues of this site are what read the codon-anticodon match."}]},
            {"subject": "drug0", "object": "decoding_site",
             "predicate": "molecularly interacts with (binds the decoding site)",
             "predicate_id": "RO:0002436",
             "description": "Drug action, from the 30S crystal structures with paromomycin, streptomycin and spectinomycin.",
             "evidence": [{"reference": "PMID:11014183", "snippet": "We also describe the crystal structure of the 30S subunit complexed with the antibiotics paromomycin, streptomycin and spectinomycin, which interfere with decoding and translocation.",
                           "notes": "Carter et al. 2000. The drugs interfere with decoding and translocation, which is why they are bactericidal."}]},
            {"subject": "determinant", "object": "drug0",
             "predicate": "negatively regulates (substitution lowers drug affinity)",
             "predicate_id": "RO:0002212",
             "description": "The causal core, measured rather than inferred: chemical footprinting shows the drug binds the substituted sequence less well.",
             "evidence": [{"reference": "PMID:10357824", "snippet": "Chemical footprinting experiments indicate that resistance arises from the lower affinity of the drug for the eukaryotic rRNA sequence.",
                           "notes": "Recht et al. 1999."}]},
            {"subject": "decoding_site", "object": "drug0",
             "predicate": "molecularly interacts with (its identity at 1408 sets drug selectivity)",
             "predicate_id": "RO:0002436",
             "description": "Why these drugs are prokaryote-selective at all -- and why the resistant ribosome is the eukaryotic sequence.",
             "evidence": [{"reference": "PMID:10357824", "snippet": "A major difference in the binding site for these antibiotics between prokaryotic and eukaryotic ribosomes is the identity of the nucleotide at position 1408 (Escherichia coli numbering), which is an adenosine in prokaryotic ribosomes and a guanosine in eukaryotic ribosomes.",
                           "notes": "Recht et al. 1999. The resistance substitution makes the bacterial site look eukaryotic, which is the same fact that makes aminoglycosides selective in the first place."}]},
        ],
    },
    # ---------------------------------------------------------------------------------
    # inhA -- TWO resistance routes on one determinant (ARO:3003417), and one 1994 paper
    # demonstrated both:
    #
    #   * a MISSENSE mutation confers resistance  -> target alteration (rounds 18-19, 26);
    #   * the WILD-TYPE gene on a multicopy plasmid also confers resistance -> there is
    #     simply more target than the drug can modify. Titration by overexpression, which
    #     no earlier round has.
    #
    # Both are on the graph, as separate edges with their own evidence, because a record
    # that showed only one would misdescribe half the clinical alleles.
    "ARO:3003417": {
        "curated": "2026-08-06T00:00:00Z",
        "reference": "PMID:8284673",       # Banerjee et al. 1994, Science
        "mech": {"ARO:3000212": "A missense mutation within the mycobacterial inhA gene was shown to confer resistance to both INH and ethionamide (ETH) in M. smegmatis and in M. bovis."},
        "mech_res": "A missense mutation within the mycobacterial inhA gene was shown to confer resistance to both INH and ethionamide (ETH) in M. smegmatis and in M. bovis.",
        "det_res": [
            {"reference": "PMID:8284673", "snippet": "A missense mutation within the mycobacterial inhA gene was shown to confer resistance to both INH and ethionamide (ETH) in M. smegmatis and in M. bovis.",
             "notes": "Banerjee et al. 1994, route 1 -- target alteration, shown in two species."},
            {"reference": "PMID:8284673", "snippet": "The wild-type inhA gene also conferred INH and ETH resistance when transferred on a multicopy plasmid vector to M. smegmatis and M. bovis BCG.",
             "notes": "Route 2, from the same paper and the more surprising result: the WILD-TYPE gene confers resistance when overexpressed, so more target is sufficient without any change to the protein."},
        ],
        "res_drug": "These results suggest that InhA is likely a primary target of action for INH and ETH.",
        "note": "The drug's target itself: resistance either by altering InhA or by making more of it.",
        "extra_nodes": [
            {"node_id": "inha_activity",
             "label": "enoyl-[acyl-carrier-protein] reductase (NADH) activity (InhA)",
             "node_type": "MOLECULAR_FUNCTION", "grounding": "GO:0004318"},
            {"node_id": "mycolic", "label": "mycolic acid biosynthetic process",
             "node_type": "BIOLOGICAL_PROCESS", "grounding": "GO:0071768"},
            {"node_id": "inh_nad", "label": "isoniazid-NAD adduct in the InhA active site",
             "node_type": "STATE",
             "description": "The inhibitory species, formed after katG activates the prodrug (round 27). Ungrounded."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "inha_activity",
             "predicate": "enables (enoyl-ACP reduction)", "predicate_id": "RO:0002327",
             "evidence": [{"reference": "PMID:8284673", "snippet": "The InhA protein shows significant sequence conservation with the Escherichia coli enzyme EnvM, and cell-free assays indicate that it may be involved in mycolic acid biosynthesis.",
                           "notes": "Banerjee et al. 1994: InhA is an EnvM homologue acting in mycolic acid biosynthesis."}]},
            {"subject": "inha_activity", "object": "mycolic",
             "predicate": "part of (mycolic acid biosynthesis)", "predicate_id": "BFO:0000050",
             "description": "Why inhibiting InhA kills: mycolic acids are essential to the mycobacterial envelope.",
             "evidence": [{"reference": "PMID:8284673", "snippet": "The InhA protein shows significant sequence conservation with the Escherichia coli enzyme EnvM, and cell-free assays indicate that it may be involved in mycolic acid biosynthesis.",
                           "notes": "The pathway the enzyme belongs to."}]},
            {"subject": "inh_nad", "object": "inha_activity",
             "predicate": "negatively regulates (inhibits the target)", "predicate_id": "RO:0002212",
             "description": "Drug action: the activated drug is covalently attached to the NAD in InhA's own active site.",
             "evidence": [{"reference": "PMID:9417034", "snippet": "Data from x-ray crystallography and mass spectrometry reveal that the mechanism of isoniazid action against InhA is covalent attachment of the activated form of the drug to the nicotinamide ring of nicotinamide adenine dinucleotide bound within the active site of InhA.",
                           "notes": "Rozwarski et al. 1998. The species doing this exists only because katG activated the prodrug -- curated on ARO:3004266 in round 27."}]},
            {"subject": "determinant", "object": "inh_nad",
             "predicate": "negatively regulates (altered target binds the adduct less well)",
             "predicate_id": "RO:0002212",
             "description": "Route 1: a missense substitution in InhA reduces the drug-NAD adduct's grip on it.",
             "evidence": [{"reference": "PMID:8284673", "snippet": "A missense mutation within the mycobacterial inhA gene was shown to confer resistance to both INH and ethionamide (ETH) in M. smegmatis and in M. bovis.",
                           "notes": "Banerjee et al. 1994. The paper shows the mutation confers resistance; that it does so by weakening adduct binding is the reading Rozwarski et al. 1998 later supported structurally."}]},
            {"subject": "determinant", "object": "inha_activity",
             "predicate": "positively regulates (overexpression titrates the drug)",
             "predicate_id": "RO:0002213",
             "description": "Route 2, and it needs no change to the protein at all: more copies of the wild-type target than the activated drug can modify.",
             "evidence": [
                 {"reference": "PMID:8284673", "snippet": "The wild-type inhA gene also conferred INH and ETH resistance when transferred on a multicopy plasmid vector to M. smegmatis and M. bovis BCG.",
                  "notes": "Banerjee et al. 1994, multicopy plasmid in two hosts. This is why promoter substitutions upstream of inhA (the fabG1-inhA operon) are resistance alleles without touching the coding sequence."},
                 {"reference": "PMID:12406221", "snippet": "Mycobacteria containing inhA plasmids uniformly exhibited 20-fold or greater increased resistance to INH and 10-fold or greater increased resistance to ETH.",
                  "notes": "Larsen et al. 2002 quantified it across five strains and settled a disputed question: 20-fold or greater for isoniazid, 10-fold or greater for ethionamide."},
                 {"reference": "PMID:12406221", "snippet": "Using molecular beacons, quantified inhA and kasA mRNA levels showed that increased inhA mRNA levels correlated with INH resistance, whereas kasA mRNA levels did not.",
                  "notes": "And tied the resistance to the EXPRESSION LEVEL rather than to the plasmid: inhA mRNA correlated with resistance, kasA mRNA did not. That is the measured link a chromosomal promoter allele would act through."},
             ]},
        ],
    },
    # ---------------------------------------------------------------------------------
    # katG -- resistance by LOSING a function (ARO:3004266). A fifth kind of mechanism,
    # and the first that is not something the determinant DOES:
    #
    #   inactivation      the enzyme destroys the drug          (rounds 12-16)
    #   target alteration the target binds the drug less well   (18-19, 26)
    #   precursor depletion / substitution                      (20-21, 23)
    #   regulation        it switches on the genes that do      (22, 24)
    #   PRODRUG ACTIVATION LOSS  the determinant FAILS to turn the prodrug on
    #
    # Isoniazid is inert until katG's peroxidase activates it. A katG that has lost that
    # activity leaves the drug inert, so the graph's causal core is a NEGATIVE regulation
    # BY the determinant of a step it would otherwise perform -- which is why the node
    # labels say "defective" rather than leaving the reader to infer it.
    "ARO:3004266": {
        "curated": "2026-08-06T00:00:00Z",
        "reference": "PMID:1501713",       # Zhang, Heym, Allen, Young & Cole 1992, Nature
        "mech": {"ARO:3000212": "Deletion of katG from the chromosome was associated with INH resistance in two patient isolates of M. tuberculosis."},
        "mech_res": "Deletion of katG from the chromosome was associated with INH resistance in two patient isolates of M. tuberculosis.",
        "det_res": [
            {"reference": "PMID:1501713", "snippet": "Deletion of katG from the chromosome was associated with INH resistance in two patient isolates of M. tuberculosis.",
             "notes": "Zhang et al. 1992, loss of function: deleting katG confers resistance in patient isolates."},
            {"reference": "PMID:1501713", "snippet": "A single M. tuberculosis gene, katG, encoding both catalase and peroxidase, restored sensitivity to INH in a resistant mutant of Mycobacterium smegmatis, and conferred INH susceptibility in some strains of Escherichia coli.",
             "notes": "And the converse, in the same paper: restoring katG restores SENSITIVITY, in two different host species. Both directions is what makes this causal rather than correlative."},
        ],
        "res_drug": "A single M. tuberculosis gene, katG, encoding both catalase and peroxidase, restored sensitivity to INH in a resistant mutant of Mycobacterium smegmatis, and conferred INH susceptibility in some strains of Escherichia coli.",
        "note": "Prodrug activation loss: isoniazid is inert until katG activates it, so a katG that cannot leaves the drug inert.",
        "extra_nodes": [
            {"node_id": "family", "label": "catalase-peroxidase (KatG)", "node_type": "PROTEIN",
             "grounding": "NCBIfam:TIGR00198",
             "description": "KB protein-trait record for the catalase-peroxidase family. This determinant is a DEFECTIVE member of it -- the resistance is the defect."},
            {"node_id": "peroxidase", "label": "peroxidase activity (the activity isoniazid activation requires)",
             "node_type": "MOLECULAR_FUNCTION", "grounding": "GO:0004601"},
            {"node_id": "inh", "label": "isoniazid (inert prodrug)", "node_type": "CHEMICAL",
             "grounding": "CHEBI:6030"},
            {"node_id": "activated_inh", "label": "activated isoniazid", "node_type": "STATE",
             "description": "The reactive species katG generates. Ungrounded: the paper says 'the activated form of the drug' without naming a compound this corpus can cite a CURIE for."},
            {"node_id": "inh_nad", "label": "isoniazid-NAD adduct in the InhA active site",
             "node_type": "STATE",
             "description": "The inhibitory species: activated drug covalently attached to the nicotinamide ring of NAD bound in InhA. Ungrounded."},
            {"node_id": "inha", "label": "enoyl-[acyl-carrier-protein] reductase (NADH) activity (InhA)",
             "node_type": "MOLECULAR_FUNCTION", "grounding": "GO:0004318"},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "family",
             "predicate": "member of (the catalase-peroxidase family, defectively)",
             "predicate_id": "RO:0002350",
             "evidence": [
                 {"reference": "PMID:1501713", "snippet": "A single M. tuberculosis gene, katG, encoding both catalase and peroxidase, restored sensitivity to INH in a resistant mutant of Mycobacterium smegmatis, and conferred INH susceptibility in some strains of Escherichia coli.",
                  "notes": "Zhang et al. 1992 establish what katG is: one gene encoding both activities."},
                 {"reference": "NCBIfam:TIGR00198", "snippet": "catalase/peroxidase HPI",
                  "notes": "NCBIfam's own product name for the family this node grounds to. NOT the KB record's definition, which this repo composes."},
             ]},
            {"subject": "family", "object": "peroxidase",
             "predicate": "enables (peroxidase activity)", "predicate_id": "RO:0002327",
             "evidence": [{"reference": "PMID:1501713", "snippet": "A single M. tuberculosis gene, katG, encoding both catalase and peroxidase, restored sensitivity to INH in a resistant mutant of Mycobacterium smegmatis, and conferred INH susceptibility in some strains of Escherichia coli.",
                           "notes": "The peroxidase half is the one isoniazid activation needs."}]},
            {"subject": "peroxidase", "object": "activated_inh",
             "predicate": "causally upstream of (activates the prodrug)", "predicate_id": "RO:0002411",
             "description": "Isoniazid is inert as given; katG converts it to the species that inhibits InhA.",
             "evidence": [
                 {"reference": "PMID:1501713", "snippet": "A single M. tuberculosis gene, katG, encoding both catalase and peroxidase, restored sensitivity to INH in a resistant mutant of Mycobacterium smegmatis, and conferred INH susceptibility in some strains of Escherichia coli.",
                  "notes": "Restoring katG restores INH sensitivity in two host species, so the gene's product is what makes the drug work."},
                 {"reference": "PMID:9417034", "snippet": "Data from x-ray crystallography and mass spectrometry reveal that the mechanism of isoniazid action against InhA is covalent attachment of the activated form of the drug to the nicotinamide ring of nicotinamide adenine dinucleotide bound within the active site of InhA.",
                  "notes": "Rozwarski et al. 1998 name the acting species 'the activated form of the drug'. That katG is what activates it is an inference FROM THESE TWO SOURCES TOGETHER."},
             ]},
            {"subject": "inh", "object": "activated_inh",
             "predicate": "causally upstream of (is the substrate of activation)",
             "predicate_id": "RO:0002411",
             "evidence": [{"reference": "PMID:9417034", "snippet": "The preferred antitubercular drug isoniazid specifically targets a long-chain enoyl-acyl carrier protein reductase (InhA), an enzyme essential for mycolic acid biosynthesis in Mycobacterium tuberculosis.",
                           "notes": "Rozwarski et al. 1998: isoniazid is the drug whose activated form does the work."}]},
            {"subject": "activated_inh", "object": "inh_nad",
             "predicate": "causally upstream of (forms the covalent adduct)", "predicate_id": "RO:0002411",
             "evidence": [{"reference": "PMID:9417034", "snippet": "Data from x-ray crystallography and mass spectrometry reveal that the mechanism of isoniazid action against InhA is covalent attachment of the activated form of the drug to the nicotinamide ring of nicotinamide adenine dinucleotide bound within the active site of InhA.",
                           "notes": "Covalent attachment to the nicotinamide ring of NAD bound in the InhA active site, shown by crystallography and mass spectrometry."}]},
            {"subject": "inh_nad", "object": "inha",
             "predicate": "negatively regulates (inhibits the target)", "predicate_id": "RO:0002212",
             "description": "InhA is essential for mycolic acid biosynthesis, so inhibiting it is what kills the cell.",
             "evidence": [{"reference": "PMID:9417034", "snippet": "The preferred antitubercular drug isoniazid specifically targets a long-chain enoyl-acyl carrier protein reductase (InhA), an enzyme essential for mycolic acid biosynthesis in Mycobacterium tuberculosis.",
                           "notes": "Rozwarski et al. 1998 identify InhA as the target and why it matters."}]},
            {"subject": "determinant", "object": "peroxidase",
             "predicate": "negatively regulates (the defective katG cannot activate the prodrug)",
             "predicate_id": "RO:0002212",
             "description": "THE CAUSAL CORE, and it runs backwards compared with every earlier round: this determinant confers resistance by NOT doing something. A katG that has lost peroxidase activity leaves isoniazid inert, so none of the chain below it happens.",
             "evidence": [{"reference": "PMID:1501713", "snippet": "Deletion of katG from the chromosome was associated with INH resistance in two patient isolates of M. tuberculosis.",
                           "notes": "Deletion -- the extreme case of loss -- confers resistance in patient isolates. Clinical katG resistance mutations are usually point substitutions that reduce rather than abolish the activity."}]},
        ],
    },
    # ---------------------------------------------------------------------------------
    # rpoB -- rifamycin TARGET ALTERATION (ARO:3000210). The same shape as gyrA's QRDR
    # (round 18) on a different target: substitutions in a short conserved region of the
    # RNA polymerase beta subunit reduce the drug's grip on its binding pocket.
    #
    # These records carry TWO mechanism ids, so both need snippets -- the UncoveredMechanism
    # guard (#203) refuses to substitute one for the other.
    "ARO:3000210": {
        "curated": "2026-08-06T00:00:00Z",
        "reference": "PMID:8095569",       # Telenti et al. 1993, Lancet -- defined the RRDR
        "mech": {
            "ARO:0001002": "Thus, substitution of a limited number of highly conserved aminoacids encoded by the rpoB gene appears to be the molecular mechanism responsible for \u201csingle step\u201d high-level resistance to rifampicin in M tuberculosis.",
            "ARO:3000212": "Mutations involving 8 conserved aminoacids were identified in 64 of 66 rifampicin-resistant isolates of diverse geographical origin, but in none of 56 sensitive isolates. All mutations were clustered within a region of 23 aminoacids.",
        },
        "mech_res": "Thus, substitution of a limited number of highly conserved aminoacids encoded by the rpoB gene appears to be the molecular mechanism responsible for \u201csingle step\u201d high-level resistance to rifampicin in M tuberculosis.",
        "det_res": [
            {"reference": "PMID:8095569", "snippet": "Mutations involving 8 conserved aminoacids were identified in 64 of 66 rifampicin-resistant isolates of diverse geographical origin, but in none of 56 sensitive isolates. All mutations were clustered within a region of 23 aminoacids.",
             "notes": "Telenti et al. 1993. A case-control result, not an observation: the substitutions are in 64 of 66 resistant isolates and in NONE of 56 sensitive ones."},
            {"reference": "PMID:8095569", "snippet": "Thus, substitution of a limited number of highly conserved aminoacids encoded by the rpoB gene appears to be the molecular mechanism responsible for \u201csingle step\u201d high-level resistance to rifampicin in M tuberculosis.",
             "notes": "And the authors' own causal reading of it."},
        ],
        "res_drug": "Thus, substitution of a limited number of highly conserved aminoacids encoded by the rpoB gene appears to be the molecular mechanism responsible for \u201csingle step\u201d high-level resistance to rifampicin in M tuberculosis.",
        "note": "Target alteration: rifamycins bind a pocket in the RNA polymerase beta subunit, and substitutions in a 23-residue region of rpoB confer high-level resistance in one step.",
        "protein_traits": {
            "primary_key": "domain",
            # #422: the parenthetical was dropped mid-quote, which is an ELISION rather
            # than the truncation #423's guard was written for -- the source contains the
            # cited prefix and then diverges, so that repair declined it. Restored
            # verbatim from the KB record; the claim is unchanged either way.
            "domain": ("Pfam:PF04563", "RNA polymerase beta subunit domain", "DOMAIN", "RNA polymerases catalyse the DNA dependent polymerisation of RNA. Prokaryotes contain a single RNA polymerase compared to three in eukaryotes (not including mitochondrial and chloroplast polymerases). This domain forms one of the two distinctive lobes of the Rpb2 structure."),
            "part_pred": "part of (the beta-subunit domain of this determinant)",
            "part_note": "KB trait record Pfam:PF04563; snippet is the InterPro:IPR007644 abstract that record's definition is taken from. Rpb2 is the structural name for the beta subunit, which is what makes this the right domain for an rpoB determinant.",
        },
        "extra_nodes": [
            {"node_id": "rrdr",
             "label": "rifampicin resistance-determining region of RpoB, substituted in this determinant",
             "node_type": "MOTIF",
             "description": "The 23-residue region in which resistance substitutions cluster (Telenti et al. 1993). Positions differ per organism, so no per-record residue node is asserted -- the same frame caveat as the QRDR in rounds 18-19. Ungrounded: no ontology term denotes the RRDR."},
            {"node_id": "rnap_activity", "label": "DNA-directed RNA polymerase activity",
             "node_type": "MOLECULAR_FUNCTION", "grounding": "GO:0003899"},
            {"node_id": "rif", "label": "rifampicin", "node_type": "CHEMICAL",
             "grounding": "CHEBI:28077"},
            {"node_id": "rif_pocket", "label": "rifamycin-binding pocket of the beta subunit",
             "node_type": "STATE",
             "description": "The drug bound in the DNA/RNA channel, >12 A from the catalytic site. Ungrounded: a binding site on a complex, not a compound."},
        ],
        "extra_edges": [
            {"subject": "rrdr", "object": "domain",
             "predicate": "part of (the RRDR lies in the beta subunit)", "predicate_id": "BFO:0000050",
             "evidence": [
                 {"reference": "PMID:8095569", "snippet": "Mutations involving 8 conserved aminoacids were identified in 64 of 66 rifampicin-resistant isolates of diverse geographical origin, but in none of 56 sensitive isolates. All mutations were clustered within a region of 23 aminoacids.",
                  "notes": "Telenti et al. 1993 located the substitutions to a 23-residue region of rpoB."},
                 {"reference": "PMID:11290327", "snippet": "The inhibitor binds in a pocket of the RNAP beta subunit deep within the DNA/RNA channel, but more than 12 A away from the active site.",
                  "notes": "Campbell et al. 2001 place the drug's pocket in that same beta subunit. The containment is an inference FROM THESE TWO SOURCES TOGETHER, not a single asserted statement."},
             ]},
            {"subject": "domain", "object": "rnap_activity",
             "predicate": "enables (transcription elongation)", "predicate_id": "RO:0002327",
             "evidence": [{"reference": "PMID:11290327", "snippet": "The structure, combined with biochemical results, explains the effects of Rif on RNAP function and indicates that the inhibitor acts by directly blocking the path of the elongating RNA when the transcript becomes 2 to 3 nt in length.",
                           "notes": "The activity the drug blocks: extension of the nascent transcript."}]},
            {"subject": "rif", "object": "rif_pocket",
             "predicate": "molecularly interacts with (binds the beta-subunit pocket)",
             "predicate_id": "RO:0002436",
             "description": "Drug action, and it is allosteric rather than catalytic: the pocket is >12 A from the active site, so the drug obstructs the RNA's path instead of the chemistry.",
             "evidence": [{"reference": "PMID:11290327", "snippet": "The inhibitor binds in a pocket of the RNAP beta subunit deep within the DNA/RNA channel, but more than 12 A away from the active site.",
                           "notes": "Campbell et al. 2001, crystal structure of Thermus aquaticus core RNAP with rifampicin."}]},
            {"subject": "rif_pocket", "object": "rnap_activity",
             "predicate": "negatively regulates (blocks the elongating transcript)",
             "predicate_id": "RO:0002212",
             "evidence": [{"reference": "PMID:11290327", "snippet": "The structure, combined with biochemical results, explains the effects of Rif on RNAP function and indicates that the inhibitor acts by directly blocking the path of the elongating RNA when the transcript becomes 2 to 3 nt in length.",
                           "notes": "Blocking happens once the transcript reaches 2-3 nt -- which is why rifampicin stops initiation rather than ongoing elongation."}]},
            {"subject": "rrdr", "object": "rif_pocket",
             "predicate": "negatively regulates (substitution weakens drug binding)",
             "predicate_id": "RO:0002212",
             "description": "The causal core: substitutions in the RRDR reshape the pocket the drug binds, and resistance is high-level and single-step.",
             "evidence": [{"reference": "PMID:8095569", "snippet": "Thus, substitution of a limited number of highly conserved aminoacids encoded by the rpoB gene appears to be the molecular mechanism responsible for \u201csingle step\u201d high-level resistance to rifampicin in M tuberculosis.",
                           "notes": "Telenti et al. 1993. The RRDR is defined by where resistance substitutions fall; Campbell et al. 2001 later showed that region lines the drug's pocket."}]},
        ],
    },
    # ---------------------------------------------------------------------------------
    # vanY -- the D,D-carboxypeptidase, and the last enzyme family of the van set. Unlike
    # vanX it acts on the ASSEMBLED precursor rather than the free dipeptide, and the two
    # were shown to be non-redundant.
    "ARO:3000077": {
        "curated": "2026-08-06T00:00:00Z",
        "precondition": _requires_lac_cluster,
        "reference": "PMID:10094630",     # Arthur, Depardieu, Cabanie, Reynolds & Courvalin 1998
        "mech": {"ARO:3000213": "The enzyme was a Zn2+-dependent D,D-carboxypeptidase that cleaved the C-terminal residue of peptidoglycan precursors ending in R-D-Ala-D-Ala or R-D-Ala-D-Lac but not the dipeptide D-Ala-D-Ala."},
        "mech_res": "In Enterococcus faecalis, VanY was present in membrane and cytoplasmic fractions, produced UDP-MurNAc-tetrapeptide from cytoplasmic peptidoglycan precursors and was required for high-level glycopeptide resistance in a medium supplemented with D-Ala.",
        "det_res": [
            {"reference": "PMID:10094630", "snippet": "In Enterococcus faecalis, VanY was present in membrane and cytoplasmic fractions, produced UDP-MurNAc-tetrapeptide from cytoplasmic peptidoglycan precursors and was required for high-level glycopeptide resistance in a medium supplemented with D-Ala.",
             "notes": "Arthur et al. 1998: required for HIGH-LEVEL resistance, and only in D-Ala-supplemented medium -- a conditional requirement, stated as such rather than flattened to 'confers resistance'."},
            {"reference": "PMID:10094630", "snippet": "The specificity constants kcat/Km were 17- to 67-fold higher for substrates ending in the R-D-Ala-D-Ala target of glycopeptides.",
             "notes": "And why: it prefers the drug's own target by 17- to 67-fold in kcat/Km."},
        ],
        "res_drug": "The specificity constants kcat/Km were 17- to 67-fold higher for substrates ending in the R-D-Ala-D-Ala target of glycopeptides.",
        "note": "Removes the terminal D-Ala from assembled precursors, preferring the D-Ala-D-Ala target of glycopeptides by 17- to 67-fold.",
        "extra_nodes": [
            {"node_id": "family", "label": "D,D-carboxypeptidase VanY", "node_type": "PROTEIN",
             "grounding": "NCBIfam:NF000380",
             "description": "KB protein-trait record for the VanXY/VanY D,D-carboxypeptidase family."},
            {"node_id": "carboxypeptidase", "label": "serine-type D-Ala-D-Ala carboxypeptidase activity",
             "node_type": "MOLECULAR_FUNCTION", "grounding": "GO:0009002"},
            {"node_id": "precursor_dala",
             "label": "peptidoglycan precursor ending in R-D-Ala-D-Ala (the glycopeptide target)",
             "node_type": "STATE",
             "description": "Ungrounded: ChEBI has the dipeptide but not the assembled precursor."},
            {"node_id": "tetrapeptide", "label": "UDP-MurNAc-tetrapeptide", "node_type": "STATE",
             "description": "The product of removing the terminal D-Ala. Ungrounded, as above."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "family",
             "predicate": "member of (the VanY D,D-carboxypeptidase family)", "predicate_id": "RO:0002350",
             "evidence": [
                 {"reference": "PMID:10094630", "snippet": "The enzyme was a Zn2+-dependent D,D-carboxypeptidase that cleaved the C-terminal residue of peptidoglycan precursors ending in R-D-Ala-D-Ala or R-D-Ala-D-Lac but not the dipeptide D-Ala-D-Ala.",
                  "notes": "Establishes what VanY is, by purification from a baculovirus expression system."},
                 {"reference": "NCBIfam:NF000380", "snippet": "D,D-carboxypeptidase/D,D-dipeptidase VanXY",
                  "notes": "NCBIfam's own product name for the family this node grounds to."},
             ]},
            {"subject": "family", "object": "carboxypeptidase",
             "predicate": "enables (Zn2+-dependent D,D-carboxypeptidation)", "predicate_id": "RO:0002327",
             "evidence": [{"reference": "PMID:10094630", "snippet": "The enzyme was a Zn2+-dependent D,D-carboxypeptidase that cleaved the C-terminal residue of peptidoglycan precursors ending in R-D-Ala-D-Ala or R-D-Ala-D-Lac but not the dipeptide D-Ala-D-Ala.",
                           "notes": "And what it does NOT cleave -- the free dipeptide -- which is what makes it non-redundant with VanX."}]},
            {"subject": "carboxypeptidase", "object": "precursor_dala",
             "predicate": "has input (cleaves the C-terminal residue)", "predicate_id": "RO:0002233",
             "description": "It prefers the drug's own target: kcat/Km is 17- to 67-fold higher for R-D-Ala-D-Ala than for the resistant R-D-Ala-D-Lac.",
             "evidence": [{"reference": "PMID:10094630", "snippet": "The specificity constants kcat/Km were 17- to 67-fold higher for substrates ending in the R-D-Ala-D-Ala target of glycopeptides.",
                           "notes": "The preference is the point: VanY strips the precursor the drug binds far faster than the one that confers resistance."}]},
            {"subject": "carboxypeptidase", "object": "tetrapeptide",
             "predicate": "has output", "predicate_id": "RO:0002234",
             "evidence": [{"reference": "PMID:10094630", "snippet": "In Enterococcus faecalis, VanY was present in membrane and cytoplasmic fractions, produced UDP-MurNAc-tetrapeptide from cytoplasmic peptidoglycan precursors and was required for high-level glycopeptide resistance in a medium supplemented with D-Ala.",
                           "notes": "UDP-MurNAc-tetrapeptide, from cytoplasmic peptidoglycan precursors."}]},
            {"subject": "precursor_dala", "object": "drug0",
             "predicate": "molecularly interacts with (is the glycopeptide target)", "predicate_id": "RO:0002436",
             "requires": {"drug0": "ARO:3000081"},
             "description": "Drug action: the glycopeptide binds this precursor's D-Ala-D-Ala terminus, which is the residue VanY removes.",
             "evidence": [{"reference": "PMID:10094630", "snippet": "The specificity constants kcat/Km were 17- to 67-fold higher for substrates ending in the R-D-Ala-D-Ala target of glycopeptides.",
                           "notes": "The paper names R-D-Ala-D-Ala as the target of glycopeptides."}]},
            {"subject": "carboxypeptidase", "object": "resistance",
             "predicate": "causally upstream of (removes the drug's binding site)", "predicate_id": "RO:0002411",
             "description": "Non-redundant with VanX: VanX hydrolyses the free dipeptide, VanY strips D-Ala from membrane-bound lipid intermediates.",
             "evidence": [{"reference": "PMID:10094630", "snippet": "Thus, VanX and VanY had non-overlapping functions involving the hydrolysis of D-Ala-D-Ala and the removal of D-Ala from membrane-bound lipid intermediates respectively.",
                           "notes": "The authors' own summary of the division of labour, and the reason both genes exist."}]},
        ],
    },
    # ---------------------------------------------------------------------------------
    # The D-Ala-D-Ser route (vanC/E/G/L/N clusters): three enzymes, one shared downstream.
    # Round 21 covered the D-Ala-D-Lac route's vanH; this is the other terminus.
    "ARO:3002979": {      # D-Ala-D-Ser ligase: vanC, vanE, vanG, vanL, vanN
        "curated": "2026-08-06T00:00:00Z",
        "precondition": _requires_ser_cluster,
        "reference": "PMID:10817725",
        "mech": {"ARO:3000213": _SER_CLUSTER},
        "mech_res": _SER_CLUSTER,
        "det_res": _SER_PRECURSOR,
        "res_drug": _SER_PRECURSOR,
        "note": "Precursor substitution with D-serine: the ligase makes D-Ala-D-Ser instead of D-Ala-D-Ala.",
        "extra_nodes": _ser_shared_nodes() + [
            {"node_id": "ligase_activity", "label": "D-alanine--D-serine ligase activity",
             "node_type": "MOLECULAR_FUNCTION", "grounding": "EC:6.3.2.35",
             "description": "KB trait record for the activity this determinant carries."},
            {"node_id": "dala_dser", "label": "D-Ala-D-Ser dipeptide", "node_type": "CHEMICAL",
             "description": "Ungrounded: ChEBI has D-alanine and D-serine but not this dipeptide."},
        ],
        "extra_edges": _ser_shared_edges() + [
            {"subject": "determinant", "object": "ligase_activity",
             "predicate": "enables (D-Ala-D-Ser ligation)", "predicate_id": "RO:0002327",
             "evidence": [{"reference": "PMID:10817725", "snippet": _SER_CLUSTER,
                           "notes": "Arias et al. 2000: vanC-1 encodes the ligase that synthesises the dipeptide."}]},
            {"subject": "ligase_activity", "object": "dala_dser",
             "predicate": "has output", "predicate_id": "RO:0002234",
             "evidence": [{"reference": "PMID:10817725", "snippet": _SER_CLUSTER,
                           "notes": "The dipeptide D-Ala-D-Ser, for addition to UDP-MurNAc-tripeptide."}]},
            {"subject": "dala_dser", "object": "precursor_ser",
             "predicate": "causally upstream of (is added to the tripeptide)", "predicate_id": "RO:0002411",
             "evidence": [{"reference": "PMID:10817725", "snippet": _SER_CLUSTER,
                           "notes": "Addition to UDP-MurNAc-tripeptide is what makes the pentapeptide[D-Ser]."}]},
        ],
    },
    "ARO:3000372": {      # vanT: the membrane-bound serine racemase that supplies D-Ser
        "curated": "2026-08-06T00:00:00Z",
        "precondition": _requires_ser_cluster,
        "reference": "PMID:10209740",
        "mech": {"ARO:3000213": "The protein was overexpressed in Escherichia coli, and serine racemase activity was detected in the membrane but not in the cytoplasmic fraction after centrifugation of sonicated cells, whereas alanine racemase activity was located almost exclusively in the cytoplasm."},
        "mech_res": _SER_CLUSTER,
        "det_res": [
            {"reference": "PMID:10209740", "snippet": "The protein was overexpressed in Escherichia coli, and serine racemase activity was detected in the membrane but not in the cytoplasmic fraction after centrifugation of sonicated cells, whereas alanine racemase activity was located almost exclusively in the cytoplasm.",
             "notes": "Arias et al. 1999 localised the activity to the membrane, which is what distinguishes VanT from the cytoplasmic alanine racemase."},
            {"reference": "PMID:10817725", "snippet": _SER_CLUSTER,
             "notes": "And what that activity is for: providing D-Ser for the synthetic pathway."},
        ],
        "res_drug": _SER_PRECURSOR,
        "note": "Supplies the D-serine the ligase needs; confers no resistance by itself.",
        "extra_nodes": _ser_shared_nodes() + [
            {"node_id": "family", "label": "membrane-bound serine racemase VanT",
             "node_type": "PROTEIN", "grounding": "NCBIfam:NF033132",
             "description": "KB protein-trait record for the VanT family."},
            {"node_id": "racemase", "label": "serine racemase activity",
             "node_type": "MOLECULAR_FUNCTION", "grounding": "GO:0030378"},
            {"node_id": "d_serine", "label": "D-serine", "node_type": "CHEMICAL",
             "grounding": "CHEBI:16523"},
            {"node_id": "ligase_gene", "label": "D-Ala-D-Ser ligase of the van cluster",
             "node_type": "PROTEIN", "grounding": "ARO:3002979",
             "description": "KB record, curated in this same round -- the enzyme that consumes this D-serine."},
        ],
        "extra_edges": _ser_shared_edges() + [
            {"subject": "determinant", "object": "family",
             "predicate": "member of (the VanT serine-racemase family)", "predicate_id": "RO:0002350",
             "evidence": [
                 {"reference": "PMID:10209740", "snippet": "The protein was overexpressed in Escherichia coli, and serine racemase activity was detected in the membrane but not in the cytoplasmic fraction after centrifugation of sonicated cells, whereas alanine racemase activity was located almost exclusively in the cytoplasm.",
                  "notes": "Establishes what VanT is, by overexpression and fractionation."},
                 {"reference": "NCBIfam:NF033132", "snippet": "membrane-bound serine racemase VanT",
                  "notes": "NCBIfam's own product name for the family this node grounds to. NOT the KB record's definition, which this repo composes."},
             ]},
            {"subject": "family", "object": "racemase",
             "predicate": "enables (serine racemisation)", "predicate_id": "RO:0002327",
             "evidence": [{"reference": "PMID:10209740", "snippet": "The protein was overexpressed in Escherichia coli, and serine racemase activity was detected in the membrane but not in the cytoplasmic fraction after centrifugation of sonicated cells, whereas alanine racemase activity was located almost exclusively in the cytoplasm.",
                           "notes": "Membrane fraction only, unlike the host alanine racemase."}]},
            {"subject": "racemase", "object": "d_serine",
             "predicate": "has output", "predicate_id": "RO:0002234",
             "evidence": [{"reference": "PMID:10817725", "snippet": _SER_CLUSTER,
                           "notes": "vanT provides D-Ser for the synthetic pathway."}]},
            {"subject": "d_serine", "object": "ligase_gene",
             "predicate": "causally upstream of (is the ligase's substrate)", "predicate_id": "RO:0002411",
             "description": "Routes this record through the ligase record curated in the same round rather than restating the ligase's mechanism.",
             "evidence": [{"reference": "PMID:10817725", "snippet": _SER_CLUSTER,
                           "notes": "The ligase synthesises D-Ala-D-Ser; vanT is what makes the D-Ser available."}]},
        ],
    },
    "ARO:3000496": {      # vanXY: one protein, two activities, and a telling specificity
        "curated": "2026-08-06T00:00:00Z",
        "precondition": _requires_ser_cluster,
        "reference": "PMID:10564477",
        "mech": {"ARO:3000213": "The open reading frame downstream from vanC-1 encoded a soluble protein designated VanXYC (Mr 22 318), which had both of these activities."},
        "mech_res": _SER_CLUSTER,
        "det_res": [
            {"reference": "PMID:10564477", "snippet": "The open reading frame downstream from vanC-1 encoded a soluble protein designated VanXYC (Mr 22 318), which had both of these activities.",
             "notes": "Reynolds, Arias & Courvalin 1999: one 22 kDa protein carries both the D,D-dipeptidase and the D,D-carboxypeptidase activity."},
            {"reference": "PMID:10817725", "snippet": _SER_CLUSTER,
             "notes": "What those activities do in the pathway: hydrolyse D-Ala-D-Ala and remove D-Ala from the pentapeptide."},
        ],
        "res_drug": _SER_PRECURSOR,
        "note": "Removes the D-Ala-ending precursor and its dipeptide, leaving the D-Ser route.",
        "extra_nodes": _ser_shared_nodes() + [
            {"node_id": "family", "label": "D,D-carboxypeptidase/D,D-dipeptidase VanXY",
             "node_type": "PROTEIN", "grounding": "NCBIfam:NF000380",
             "description": "KB protein-trait record for the VanXY family."},
            {"node_id": "dipeptidase", "label": "dipeptidase activity",
             "node_type": "MOLECULAR_FUNCTION", "grounding": "GO:0016805"},
            {"node_id": "carboxypeptidase", "label": "serine-type D-Ala-D-Ala carboxypeptidase activity",
             "node_type": "MOLECULAR_FUNCTION", "grounding": "GO:0009002"},
            {"node_id": "dala_dala", "label": "D-alanyl-D-alanine", "node_type": "CHEMICAL",
             "grounding": "CHEBI:16576"},
        ],
        "extra_edges": _ser_shared_edges() + [
            {"subject": "determinant", "object": "family",
             "predicate": "member of (the VanXY bifunctional family)", "predicate_id": "RO:0002350",
             "evidence": [
                 {"reference": "PMID:10564477", "snippet": "The open reading frame downstream from vanC-1 encoded a soluble protein designated VanXYC (Mr 22 318), which had both of these activities.",
                  "notes": "Establishes what VanXY is."},
                 {"reference": "NCBIfam:NF000380", "snippet": "D,D-carboxypeptidase/D,D-dipeptidase VanXY",
                  "notes": "NCBIfam's own product name for the family this node grounds to."},
             ]},
            {"subject": "family", "object": "dipeptidase",
             "predicate": "enables (D,D-dipeptidase activity)", "predicate_id": "RO:0002327",
             "evidence": [{"reference": "PMID:10564477", "snippet": "The open reading frame downstream from vanC-1 encoded a soluble protein designated VanXYC (Mr 22 318), which had both of these activities.",
                           "notes": "The 'both of these activities' are the D,D-dipeptidase and the D,D-carboxypeptidase named in the title."}]},
            {"subject": "family", "object": "carboxypeptidase",
             "predicate": "enables (D,D-carboxypeptidase activity)", "predicate_id": "RO:0002327",
             "evidence": [{"reference": "PMID:10564477", "snippet": "The open reading frame downstream from vanC-1 encoded a soluble protein designated VanXYC (Mr 22 318), which had both of these activities.",
                           "notes": "The second of the two activities."}]},
            {"subject": "dipeptidase", "object": "dala_dala",
             "predicate": "has input (hydrolyses)", "predicate_id": "RO:0002233",
             "description": "And it spares the resistant route: very low activity against D-Ala-D-Ser, none against the D-Ser pentapeptide.",
             "evidence": [{"reference": "PMID:10564477", "snippet": "It had very low dipeptidase activity against D-Ala-D-Ser, unlike VanX, and no activity against UDP-MurNAc-pentapeptide[D-Ser], unlike VanY.",
                           "notes": "The negative result is what makes the pathway work -- the enzyme does not destroy the precursor it is helping to leave in place."}]},
            {"subject": "carboxypeptidase", "object": "precursor_dala",
             "predicate": "negatively regulates (removes the terminal D-Ala)", "predicate_id": "RO:0002212",
             "evidence": [{"reference": "PMID:10817725", "snippet": _SER_CLUSTER,
                           "notes": "vanXY(C) removes D-Ala from UDP-MurNAc-pentapeptide[D-Ala]."}]},
        ],
    },
    # ---------------------------------------------------------------------------------
    # vanR — the response regulator (ARO:3000574). A FOURTH kind of mechanism: regulation.
    # vanR neither destroys the drug, nor alters a target, nor remodels a precursor — it
    # transcribes the genes that do. So its graph ends at ARO:3000006 / ARO:3000011, whose
    # own mechanisms are curated, rather than restating them.
    "ARO:3000574": [
    {
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
        {
            "curated": "2026-08-06T00:00:00Z",
            "precondition": _requires_ser_cluster,
            "reference": "PMID:1556077",
            "mech": {"ARO:3000213": _VANRS_REG},
            "mech_res": _VANRS_REG,
            "det_res": [
                {"reference": "PMID:1556077", "snippet": _VANRS_REG,
                 "notes": "Arthur et al. 1992. vanR is part of the two-component system that regulates the resistance enzymes; it is not one of them."},
                {"reference": "PMID:10817725", "snippet": _SER_CLUSTER,
                 "notes": "In a D-Ala-D-Ser cluster the enzymes it induces are the ligase, vanT and vanXY -- all three curated records (round 23)."},
            ],
            "res_drug": _VANRS_INDUCIBLE,
            "note": "Regulation, not resistance, in a D-Ala-D-Ser cluster: the operon it induces is the ligase, vanT and vanXY.",
            "extra_nodes": _vanrs_ser_downstream()[0] + [
                {"node_id": "family", "label": "VanR-ABDEGLN family response regulator transcription factor",
                 "node_type": "PROTEIN", "grounding": "NCBIfam:NF033117",
                 "description": "KB protein-trait record for the vanR family."},
            ],
            "extra_edges": _vanrs_ser_downstream()[1] + [
                {"subject": "determinant", "object": "family",
                 "predicate": "member of (the vanR family)", "predicate_id": "RO:0002350",
                 "evidence": [
                     {"reference": "PMID:1556077", "snippet": _VANRS_REG,
                      "notes": "Establishes the two-component system this determinant belongs to."},
                     {"reference": "NCBIfam:NF033117", "snippet": "VanR-ABDEGLN family response regulator transcription factor",
                      "notes": "NCBIfam's own product name for the family this node grounds to."},
                 ]},
            ],
        },
    ],
    # ---------------------------------------------------------------------------------
    # vanS — the sensor histidine kinase (ARO:3000071). Same downstream half as vanR; the
    # difference is upstream, where VanS phosphorylates rather than being phosphorylated.
    "ARO:3000071": [
    {
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
        {
            "curated": "2026-08-06T00:00:00Z",
            "precondition": _requires_ser_cluster,
            "reference": "PMID:1556077",
            "mech": {"ARO:3000213": _VANRS_REG},
            "mech_res": _VANRS_REG,
            "det_res": [
                {"reference": "PMID:1556077", "snippet": _VANRS_REG,
                 "notes": "Arthur et al. 1992. vanS is part of the two-component system that regulates the resistance enzymes; it is not one of them."},
                {"reference": "PMID:10817725", "snippet": _SER_CLUSTER,
                 "notes": "In a D-Ala-D-Ser cluster the enzymes it induces are the ligase, vanT and vanXY -- all three curated records (round 23)."},
            ],
            "res_drug": _VANRS_INDUCIBLE,
            "note": "Regulation, not resistance, in a D-Ala-D-Ser cluster: the operon it induces is the ligase, vanT and vanXY.",
            "extra_nodes": _vanrs_ser_downstream()[0] + [
                {"node_id": "family", "label": "vancomycin resistance histidine kinase VanS",
                 "node_type": "PROTEIN", "grounding": "NCBIfam:NF033091",
                 "description": "KB protein-trait record for the vanS family."},
            ],
            "extra_edges": _vanrs_ser_downstream()[1] + [
                {"subject": "determinant", "object": "family",
                 "predicate": "member of (the vanS family)", "predicate_id": "RO:0002350",
                 "evidence": [
                     {"reference": "PMID:1556077", "snippet": _VANRS_REG,
                      "notes": "Establishes the two-component system this determinant belongs to."},
                     {"reference": "NCBIfam:NF033091", "snippet": "vancomycin resistance histidine kinase VanS",
                      "notes": "NCBIfam's own product name for the family this node grounds to."},
                 ]},
            ],
        },
    ],
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
             "requires": {"drug0": "ARO:3000081"},   # the Kd is vancomycin's
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
             "requires": {"drug0": "ARO:3000081"},   # the snippet is about glycopeptides
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


# The default note on a serine-hydrolase `enables` edge. NAMED, because it was an inline
# default and `repair_beta_lactam_notes.py` has to write exactly what this emits: two
# copies of one sentence is how the corpus came to hold "serine β-lactam hydrolysis" on
# 4,664 records while this file said "beta-lactam" (#466). ASCII deliberately -- aro.obo,
# the source these notes describe, uses "beta-lactam" 11,293 times and the Greek form
# twice. Verbatim SNIPPETS quoting the literature keep their β; this is our own prose.
SERINE_HYDROLYSIS_NOTE = ("The active site carries out the serine beta-lactam hydrolysis "
                          "mechanism.")


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


# ---------------------------------------------------------------------------------------
# Snippets whose true source is NOT the config's own `reference` (#365).
#
# `promoted_graph_dict` stamps `cfg["reference"]` on any bare-string snippet, which is
# right when the text is that family's own. For these four it is not: they are the shared
# PARENT mechanism definitions, quoted on child families. 113 evidence items across 153
# records cited e.g. ARO:3000557's definition under ARO:3000105 -- real CARD prose under
# an attribution that does not contain it.
#
# This is #400's shape at scale. #400 was fixed by converting one config to the list form;
# doing that here would mean editing 21 sites across 7 families and re-promoting 40,487
# records, of which family ARO:3000557 alone is 5,750 -- exactly the blast radius #280
# refuses and round 70 caused. A lookup keyed by the snippet fixes every site at once and
# re-promotes nothing.
#
# Keyed on whitespace-normalised text so a reflowed literal still matches.
SNIPPET_SOURCE = {
    "Antibiotic resistance via the transport of antibiotics out of the cell.": "ARO:0010000",
    "Enzyme that catalyzes the inactivation of an antibiotic resulting in resistance. Inactivation includes chemical modification, destruction, etc.": "ARO:3000557",
    "Enzymes that inactivate rifampin antibiotics by chemical modification.": "ARO:3000576",
    "Point mutations in the Mycobacterium tuberculosis ndh gene shown clinically to confer resistance to isoniazid.": "ARO:3003461",
    # ARO:3003588's config quotes ARO:3004363's definition. Once the truncation was
    # repaired the text became exactly ARO:3004363's, so this is the same repoint class
    # the table already handles (#365).
    "Lipid A acyltransferase genes confer resistance to certain types of peptide antibiotics such as polymyxins through the aminoacylation of lipopolysaccharide, thereby decreasing the negative charge of the outer membrane surface.": "ARO:3004363",
    # --- #426 -----------------------------------------------------------------------
    # Six more of the same shape, found by --configs (#424) rather than by the data side,
    # because `res_drug` is normally OVERRIDDEN by `_drug_assertion` and these literals
    # therefore reach almost no record today. That is what made them a trap and not a
    # visible defect: any path that falls back to `cfg["res_drug"]` writes them.
    #
    # Every one of these was already attributed CORRECTLY in the SAME config's `det_res`
    # list -- the bare `res_drug` copy is the only place the reference was lost -- so the
    # repoint target is not a judgement call, it is the neighbouring literal.
    "embB gene encodes for an arabinosyl transferase in the arabinogalactan synthesis pathway. It is inhibited by ethambutol. Mutations within the ERDR region of embB confers resistance to ethambutol.": "ARO:3000235",
    "Sequence variants of elongation factor Tu that confer resistance to elfamycin antibiotics.": "ARO:3001312",
    "arnA modifies lipid A with 4-amino-4-deoxy-L-arabinose (Ara4N) which allows gram-negative bacteria to resist the antimicrobial activity of cationic antimicrobial peptides and antibiotics such as polymyxin.": "ARO:3002985",
    "The almEFG operon is responsible for glycylation of lipid A as a mechanism of colistin resistance in Vibrio cholerae.": "ARO:3007434",
    "This family of phosphoethanolamine transferase catalyze the addition of 4-amino-4-deoxy-L-arabinose (L-Ara4N) and phosphoethanolamine to lipid A, which impedes the binding of colistin to the cell membrane.": "ARO:3004269",
    # Not an ARO term at all: a 1987 measurement quoted from the paper. ARO:3000617
    # (mecA) is the config's `reference` and says nothing about affinity. A PMID is
    # unverifiable offline and so leaves the audit rather than passing it -- which is the
    # honest outcome, not a bypass: the claim now names the source that can be checked.
    "All strains produced penicillin-binding protein 2' (PBP 2'), which has been associated with methicillin resistance and which has very low affinity for beta-lactam antibiotics.": "PMID:3499861",
}


def _true_source(snippet, fallback: str) -> str:
    """The reference a snippet actually comes from (#365).

    `fallback` is the config's own `reference`, which is correct for everything not in
    SNIPPET_SOURCE. Verified by `just audit-snippets`, which is what found these.

    TOTAL on purpose. `cfg["mech"]` values may be the #400 LIST form, whose items carry
    their own reference and need no correction -- and the first version of this crashed
    the promoter for ARO:3004910 (the only list-form family, and the one #400-#404
    hardened) with `'list' object has no attribute 'split'`. Every gate stayed green:
    `verify()` never calls `promoted_graph_dict`, so nothing exercised the code path.
    """
    if not isinstance(snippet, str):
        return fallback
    return SNIPPET_SOURCE.get(" ".join(snippet.split()), fallback)


def promoted_graph_dict(ident: str, label: str, mech: list, drug: list, names: dict,
                        cfg: dict, terms: dict | None = None,
                        skipped_out: list | None = None) -> dict:
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
    # PROTEIN for every family until round 29, but 105 draft records are ribosomal RNA and
    # calling those a protein would be simply false (#215). Optional, defaulting to the
    # old value so no existing family changes.
    determinant_node = {"node_id": "determinant", "label": label,
                        "node_type": cfg.get("determinant_node_type", "PROTEIN"),
                        "grounding": ident}
    # A limitation that is a property of the DETERMINANT -- "CARD names no specific protein
    # here" -- belongs on the node. Round 122 first wrote it as a second, weaker edge on a
    # pair that already had a strong one, which asserted and declined the same relation from
    # the same sentence (#380).
    if cfg.get("determinant_note"):
        determinant_node["description"] = cfg["determinant_note"]
    nodes = [determinant_node]
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
                           "RO:0000056", f"mech{i}", _true_source(snip, ref), snip,
                           f"Family mechanism {mid}."))
        edges.append(_edge(f"mech{i}", "causally upstream of", "RO:0002411", "resistance",
                           _true_source(cfg["mech_res"], ref) if isinstance(cfg["mech_res"], str)
                           else ref,
                           cfg["mech_res"], f"Mechanism {mid} \u2192 resistance."))
    edges.append(_edge("determinant", "causally upstream of (confers resistance)",
                       "RO:0002411", "resistance",
                       _true_source(cfg["det_res"], ref) if isinstance(cfg["det_res"], str)
                       else ref,
                       cfg["det_res"], "Determinant \u2192 resistance phenotype."))
    for i, did in enumerate(drug[:D.MAX_DRUGS]):
        # `determinant -> drug`, carrying ARO's own confers_resistance_to_drug_class, is
        # the shape BOTH the auto-draft and the 6,180 records promoted before round 18
        # use. The interim `resistance -> drug` edge was this promoter's alone (#194).
        #
        # Its evidence is CARD's assertion, not the family's literature snippet, because
        # the edge says "CARD asserts this" — regenerated from the obo so it matches what
        # the older records carry rather than overwriting it with a hydrolysis quote.
        assertion = _drug_assertion(ident, did, terms) if terms else None
        d_ref, d_snip, d_note = assertion or (
            _true_source(cfg["res_drug"], ref) if isinstance(cfg["res_drug"], str) else ref,
            cfg["res_drug"], f"Resistance to {names.get(did, did)}.")
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
                               f"mech{mech.index(em)}", _true_source(cfg["mech"][em], ref),
                               cfg["mech"][em],
                               pt.get("enable_note", SERINE_HYDROLYSIS_NOTE)))
    # Family-specific mechanism edges. The fixed determinant->mechanism->resistance shape
    # above was written for enzymatic INACTIVATION and cannot express other resistance
    # routes -- target alteration, precursor depletion, efflux -- where the causation runs
    # through parts of the target and complexes that shape has no place for.
    #
    # An edge whose subject or object is not among THIS record's nodes is skipped rather
    # than emitted dangling: mechanism and drug nodes come from each member's own ARO
    # relations, so a family member need not carry the one an edge names.
    defined = {n["node_id"]: n.get("grounding") for n in nodes}
    skipped = []
    for e in cfg.get("extra_edges", []):
        if e["subject"] not in defined or e["object"] not in defined:
            skipped.append((e["subject"], e["object"], "endpoint not on this record"))
            continue
        # IDENTITY, not just existence (#188). `drug0`/`mech0` are POSITIONAL — whatever
        # that record's own ARO relations produced, in order — so an edge naming `drug0`
        # gets that record's first drug, whatever it is. Every fluoroquinolone and
        # glycopeptide family was verified to have the drug its snippet is about, but
        # nothing enforced it, and the van clusters carry several drug classes each.
        # `requires` lets an edge state the grounding it was written for.
        mismatch = next(((k, want, defined.get(k))
                         for k, want in (e.get("requires") or {}).items()
                         if defined.get(k) != want), None)
        if mismatch:
            k, want, got = mismatch
            skipped.append((e["subject"], e["object"],
                            f"{k} is {got or 'ungrounded'}, edge requires {want}"))
            continue
        edge = {"subject": e["subject"], "predicate": e["predicate"],
                "predicate_id": e["predicate_id"], "object": e["object"]}
        if e.get("description"):
            edge["description"] = e["description"]
        # #365: an explicit evidence dict gets the same correction as a bare-string
        # snippet. Fixing only the stamping path left 10 records citing ARO:3000112 for
        # ARO:0010000's definition, and a --repromote put them straight back.
        edge["evidence"] = [{"reference": _true_source(i["snippet"], i["reference"]),
                             "snippet": i["snippet"],
                             "notes": i.get("notes", "")} for i in e["evidence"]]
        edges.append(edge)
    # A dropped edge used to be invisible: the promoter reports records, not edges, so a
    # family author could reasonably believe all their edges were written (#188).
    for subj, obj, why in skipped:
        print(f"    edge skipped on {ident}: {subj} -> {obj} ({why})")
    # #420 review: verify() needs the exact count, not a heuristic over emitted edges.
    # Its first version excluded a hard-coded "fixed shape" and so both miscounted
    # (drug1, protein_traits edges read as extra) and misfired (an extra edge touching
    # mech0 read as dropped) -- 13 of 155 configs could never trip it.
    if skipped_out is not None:
        skipped_out.extend(skipped)

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
# words that appear in a domain label without distinguishing it, so a snippet echoing
# only these has not named the domain.
_GENERIC_LABEL_WORDS = {"domain", "protein", "this", "carries", "subunit", "family",
                        "beta", "class", "site"}

KB_PREFIXES = ("ARO:", "Pfam:", "NCBIfam:", "PROSITE:", "CATH:", "InterPro:", "CDD:",
               "MEROPS:", "TED:", "GO:", "EC:", "SFLD:", "PANTHER:", "HAMAP:")


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


def _required_phrase(reason: str) -> str:
    """The thing a skip reason says the definition lacks, if it says that at all."""
    m = re.search(r"does not (?:name|call it|describe)(?: an?)? ([a-z][a-z0-9 /-]{2,44})",
                  reason, re.I)
    return m.group(1).strip() if m else ""


def skip_reason_near_miss(reason: str, text: str) -> str:
    """Did a precondition refuse a record that its OWN definition nearly satisfies? (#264)

    #256 catches a reason CONTRADICTED by the record. This catches the harder case: a
    reason that is LITERALLY TRUE and still wrong, because the pattern was too narrow.
    Three instances this session, none of which #256 sees:

      round 53  "does not name a penicillin-binding protein"  <- def said "PBP transpeptidases"
      round 59  "does not call it a class D beta-lactamase"   <- def said "class D RAD beta-lactamase"

    Two cheap signals, both of which those cases trip:

      scattered -- every token of the required phrase appears, just not contiguously
      acronym   -- the phrase's initials appear as a word (penicillin-binding protein -> PBP)

    Returns a description for a human to read, or "". Like the role audit, this is triage:
    a genuine miss ("BSU-1 is a BSU beta-lactamase" lacking "class D") stays silent because
    its tokens really are absent.
    """
    phrase = _required_phrase(reason)
    if not phrase:
        return ""
    own = _own_definition(text).lower()
    if not own or phrase in own:
        return ""
    # .lower() FIRST. Without it the [^a-z0-9] split treats an uppercase letter as a
    # separator, so "class D beta-lactamase" tokenised to [class, beta, lactamase] and the
    # discriminating "D" disappeared -- the second, independent way this detector lost the
    # same letter. Both are the defect class it exists to catch, in its own code.
    tokens = [w for w in re.split(r"[^a-z0-9]+", phrase.lower()) if w]
    if not tokens:
        return ""
    # Short tokens need FULL word boundaries. Dropping them (the first version's
    # `len(w) > 1`) discarded the discriminating letter: "class d beta-lactamase" became
    # "class beta-lactamase", which matched OXA-663's definition -- a record that really
    # does lack the "D". The detector reproducing the exact defect class it exists to find
    # is worth stating rather than quietly fixing.
    def _present(w: str) -> bool:
        pat = rf"\b{re.escape(w)}\b" if len(w) <= 2 else rf"\b{re.escape(w)}"
        return bool(re.search(pat, own))

    if all(_present(w) for w in tokens):
        return (f'refused for lacking "{phrase}", but every token of it appears in the '
                f"definition -- the pattern is probably too strict about adjacency")
    initials = "".join(w[0] for w in tokens)
    if len(initials) >= 2 and re.search(rf"\b{re.escape(initials)}\b", own):
        return (f'refused for lacking "{phrase}", but its acronym "{initials.upper()}" '
                f"appears in the definition")
    return ""


def skip_reason_contradicted(reason: str, text: str) -> str:
    """Is a skip reason's claim about the record's own definition actually true? (#253)

    Preconditions return prose that is printed as a record's justification, and until now
    NOTHING checked it. Round 52 skipped 17 records saying "definition describes a
    repressor" when none did -- the word came from inherited drug-class boilerplate. The
    outcome was accidentally right, so no gate failed and the log read as verification.

    Only the two claim shapes actually in use are checked, and only against the record's
    OWN definition:

      "... describes a X"      -> X must appear in it
      "... does not name a X"  -> X must NOT appear in it

    LIMITATION, stated because it matters: this catches round 52's bug and NOT round 53's.
    There the reason said "does not name a penicillin-binding protein" about a definition
    reading "PBP transpeptidases" -- true as literal text, wrong because PBP is a synonym.
    A synonym-aware version would need a lexicon this repo does not have.
    """
    own = _own_definition(text).lower()
    if not own:
        return ""
    m = re.search(r"describes an? ([a-z][a-z -]{2,40}?)(?:,|\.|$| not )", reason)
    if m and m.group(1).strip() not in own:
        return f'claims the definition describes "{m.group(1).strip()}", which it does not'
    m = re.search(r"does not name an? ([a-z][a-z -]{2,40}?)(?:,|\.|$| so )", reason)
    if m and m.group(1).strip() in own:
        return f'claims the definition does not name "{m.group(1).strip()}", but it does'
    return ""


# How many DISTINCT relation signatures to build per config. The whole candidate list is
# too slow for families of 4,688 records; this bounds it while still reaching the shapes
# that decide which `requires` guards fire.
MAX_VERIFY_SIGNATURES = 6

_VERIFY_NAMES = None


def _verify_names() -> dict:
    """OBO id -> name, read once. `verify` is called per config, ~150 times."""
    global _VERIFY_NAMES
    if _VERIFY_NAMES is None:
        _VERIFY_NAMES = D.obo_names(D.OBO)
    return _VERIFY_NAMES


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

    # #253: a skip reason is prose nobody verified. A guard that reaches the right answer
    # for a false stated reason reads as verification in the log, which is worse than one
    # that fails. Counted as a PROBLEM -- unlike a precondition skip, a reason that
    # contradicts the record is always a defect.
    pre = cfg.get("precondition")
    if pre is not None:
        for ident, label, text in candidates:
            reason = pre(ident, label, text)
            if not reason:
                continue
            bad = skip_reason_contradicted(reason, text)
            if bad:
                problems += 1
                print(f"  FALSE SKIP REASON    {ident} ({label}): {bad}")
                continue
            # Suppress when ANOTHER config of this family accepts the record. On a
            # list-form family every config sees every candidate, so one config's refusal
            # stays visible even when a sibling owns the record -- and a near-miss that
            # is really "a different config handles this" is noise.
            #
            # This is not cosmetic. In round 69 the detector correctly flagged
            # ARO:3004269 against the L-Ara4N config; I read it as a false positive and
            # moved on. It was pointing at a whole second chemistry with no config, which
            # round 73 then curated -- four rounds late. Suppressing the sibling-accepted
            # case leaves only the near-misses that mean something.
            if config_for(family, ident, label, text) is not None:
                continue
            near = skip_reason_near_miss(reason, text)
            if near:
                # Deliberately NOT counted as a problem. A contradicted reason (#256) is
                # always a defect; a near miss is a CANDIDATE -- eptA is correctly refused
                # by the L-Ara4N config and still trips the token test. Counting these
                # would leave verify-all permanently red, which this file already argues
                # is a gate nobody reads.
                print(f"  near-miss skip       {ident} ({label}): {near}")
    # A part-of edge asserts "this determinant HAS this domain", and its evidence is the
    # 4-tuple's snippet. Nothing checks that the snippet supports a MEMBERSHIP claim: 27 of
    # 33 families cite a bare source entry TITLE ("Beta-lactamase class-A active site"),
    # which identifies the signature without saying this determinant carries it (#196).
    # Reported, not failed -- it is a curation backlog like the uncovered mechanisms, and
    # the fix is per family: substitute the source abstract, as vanX does with the
    # InterPro:IPR000755 text that names VanX outright.
    thin_partof = 0
    pt = cfg.get("protein_traits")
    if pt:
        key = pt.get("primary_key", "active_site")
        cid, lab, _, snip = pt[key]
        label_words = [w for w in re.findall(r"[A-Za-z-]{4,}", lab)
                       if w.lower() not in _GENERIC_LABEL_WORDS]
        if len(snip) < 60 or not any(w.lower() in snip.lower() for w in label_words):
            thin_partof = 1
            print(f"  thin part-of evidence  {family}: {cid} cites {snip[:52]!r} — a bare "
                  f"entry title does not establish that this determinant has the domain")
    skips = 0
    pre = cfg.get("precondition")
    if pre:
        for ident, label, text in candidates:
            reason = pre(ident, label, text)
            if reason:
                print(f"  would skip  {ident} ({label}): {reason}")
                skips += 1
    # #414: BUILD a graph, do not just inspect the config. `verify()` used to validate
    # what a config CLAIMS and never what the promoter EMITS, so #413 shipped an
    # `AttributeError` that made this script unrunnable for ARO:3004910 while this very
    # function printed "0 problem(s)" for that family. Every other gate was green too --
    # the crash was reachable only by running a real promote.
    # B1: the build needs the obo for names, and data/raw is gitignored. Calling it
    # inside the try turned a missing file into "BUILD FAILED ... FileNotFoundError" --
    # a promoter defect that is really an absent input. It broke two existing tests in
    # CI, which is exactly where this was supposed to help (#417 review).
    built = 0
    seen_signatures: set = set()
    if not D.OBO.exists():
        print(f"  build check skipped: {D.OBO.name} absent (data/raw is gitignored); "
              f"run `just fetch-aro` to exercise the emit path")
        candidates = []
    for ident, label, text in candidates:
        if pre and pre(ident, label, text):
            continue
        mech, drug = D.parse_relations(text)
        if (tuple(mech), tuple(drug)) in seen_signatures:
            continue
        dropped: list = []
        try:
            promoted_graph_dict(ident, label, mech, drug, _verify_names(), cfg,
                                terms, skipped_out=dropped)
        except UncoveredMechanism:
            # B2: `break` here left 6 configs building NOTHING while printing
            # "0 graph built, 0 problem(s)" -- indistinguishable from verified, and the
            # same green-means-unchecked shape the NO CANDIDATES check above exists to
            # prevent. A later candidate often does build (#417 review).
            continue
        except Exception as exc:      # noqa: BLE001 -- any failure here is the finding
            print(f"  BUILD FAILED  {ident}: {type(exc).__name__}: {exc}")
            problems += 1
            break
        # `graph["edges"]` is never empty -- promoted_graph_dict unconditionally appends
        # determinant->resistance -- so the old EMPTY GRAPH check was dead code, 0 hits
        # across 183 configs (#419). Check what can actually be false: did this config's
        # own extra_edges reach the record, or were they ALL dropped as dangling/`requires`
        # mismatches? A config whose every extra edge is skipped is silently a no-op.
        wanted = len(cfg.get("extra_edges", ()))
        if wanted and len(dropped) == wanted:
            print(f"  NO EXTRA EDGES  {ident}: all {wanted} of this config's extra edges "
                  f"were dropped; the config is a no-op on this record")
            problems += 1
        built += 1
        # #419: build a record per DISTINCT relation signature, not just the first. 38% of
        # configs have candidates whose parse_relations differ, and those are what change
        # which `requires` guards fire and which edges are emitted.
        # #420 review: this used to BREAK on the first repeated signature, so 101 of 183
        # configs stopped at two builds and the biggest families reached 1 of 14 distinct
        # signatures. Skip duplicates; break only at the cap.
        sig = (tuple(mech), tuple(drug))
        seen_signatures.add(sig)
        if len(seen_signatures) >= MAX_VERIFY_SIGNATURES:
            break
    print(f"verify {family}: {len(curies)} KB CURIEs checked, {len(candidates)} candidate "
          f"records, {skips} precondition skip(s), {uncovered_records} uncovered-mechanism "
          f"record(s), {thin_partof} thin part-of, {built} graph(s) built, {problems} problem(s)")
    return problems



def _drug_assertion(ident: str, did: str, terms: dict):
    """CARD's own `confers_resistance_to_drug_class` line, and the term it sits on.

    A variant record rarely asserts the relation itself — it inherits it from a family or
    class ancestor — so this walks `is_a` from the record upward and returns the first term
    that asserts it. Returns None if nothing in the ancestry does, in which case the caller
    falls back to the family's literature snippet.

    THE RECORD ITSELF IS FIRST IN THE WALK, and that is deliberate: a term that asserts the
    relation directly must not be described as inheriting it. But the note said "an is_a
    ancestor of this record's ARO:3004574" whichever branch matched, so every direct
    assertion claimed the record was its own ancestor (#364). A term is not its own `is_a`
    ancestor; `aro.obo` gives ARO:3004574 `is_a ARO:0000031` and nothing else.

    215 such notes were on disk across 190 records. `fix_resistance_drug_edges` has written
    the correct form for a while -- 593 records carry it -- but this function was never
    changed, so the promoter re-created the defect on every run and re-promoting a repaired
    record silently undid the repair. That is why #408 could not simply re-promote its
    drifted records: 74 of them differ from their config for exactly this reason, with the
    RECORD right and the CONFIG wrong.

    The wording of both branches is copied from `fix_resistance_drug_edges` so the two
    writers agree byte for byte; `test_the_two_writers_agree_on_both_note_forms` pins that.
    """
    for anc in [ident] + [a for a in E.ancestry(terms, ident) if a != ident]:
        for rel in terms.get(anc, {}).get("rel", []):
            if rel.startswith("confers_resistance_to_drug_class") and did in rel:
                name = terms[anc].get("name", anc)
                if anc == ident:
                    note = (f"Asserted directly on {anc} ({name}) in the CARD/ARO release "
                            f"in data/raw/aro/aro.obo.")
                else:
                    note = (f"Asserted on {anc} ({name}), an is_a ancestor of this "
                            f"record's {ident}; inherited by this variant. CARD/ARO "
                            f"release in data/raw/aro/aro.obo.")
                return (anc, f"relationship: {rel}", note)
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


def graph_fingerprint(graph: dict) -> str:
    """sha256 of a graph, over its canonical dump rather than its repr (#204).

    `_dump` is what actually reaches disk, so hashing it means the fingerprint answers the
    question the caller has -- "is the file still what I wrote" -- and not a question about
    Python object identity. Key order is fixed by `sort_keys=False` on a dict this module
    builds in a fixed order, so the same graph hashes the same across runs.
    """
    return hashlib.sha256("\n".join(_dump(graph)).encode("utf-8")).hexdigest()


def curation_entry(cfg: dict, graph: dict | None = None,
                   family: str | None = None) -> dict:
    entry = {
        "timestamp": cfg.get("curated", LEGACY_PROMOTION),
        "curator": "edison-causal-graphs",
        "action": ("Promoted auto-draft to curated causal_graphs with family verbatim "
                   "snippets; SEEDED -> REVIEWED"),
        "llm_assisted": True,
    }
    if family is not None:
        entry["emitted_for"] = family
    if graph is not None:
        entry["emitted_hash"] = graph_fingerprint(graph)
    return entry


def curation_event(cfg: dict, graph: dict | None = None,
                   family: str | None = None) -> list[str]:
    # `family` forwarded, because a hash WITHOUT `emitted_for` is the one shape the guard
    # cannot read: `last_owner` comes back None, ownership protection silently degrades to
    # content equality, and the run reports "no emitted_hash" about a record that has one.
    return _dump({"curation_history": [curation_entry(cfg, graph, family)]})


def promoter_events(doc: dict) -> list[dict]:
    """This promoter's own fingerprinted events, oldest first."""
    return [e for e in (doc.get("curation_history") or [])
            if isinstance(e, dict) and e.get("curator") == "edison-causal-graphs"
            and e.get("emitted_hash")]


def promoter_wrote_this(doc: dict, family: str | None = None) -> tuple[str | None, str | None]:
    """(hash written for `family`, family that last wrote any graph here).

    TWO VALUES, because "did I write this" and "did SOMEONE ELSE write this" are different
    questions with different answers, and the first version only asked the first. A record
    claimed by three family configs carries whichever one ran last; reading only the latest
    hash made the broad family treat the narrow family's work as its own.

    A None hash means CANNOT TELL, not "unedited" -- every record promoted before #204
    lacks the field, so a caller that reads None as permission protects nothing that
    exists.
    """
    events = promoter_events(doc)
    if not events:
        return None, None
    mine = [e for e in events if family is not None and e.get("emitted_for") == family]
    last_owner = events[-1].get("emitted_for")
    return (str(mine[-1]["emitted_hash"]) if mine else None,
            str(last_owner) if last_owner else None)



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


def family_configs(family: str) -> list:
    """A family's config, or its configs — plural where one family spans two mechanisms.

    `vanR`/`vanS` are one ARO family each but sit in BOTH van routes: the D-Ala-D-Lac
    clusters induce vanH + vanX, the D-Ala-D-Ser clusters induce the ligase, vanT and
    vanXY. The right downstream is a property of the RECORD, not of the family, so a
    single config per family id cannot serve them (#208).

    The selector is the `precondition` each config already carries for #201 — the same
    predicate that refuses a record is what chooses between configs, so nothing new has to
    be written to make this work.
    """
    entry = FAMILY_SNIPPETS.get(family)
    if entry is None:
        return []
    return list(entry) if isinstance(entry, list) else [entry]


def config_for(family: str, ident: str, label: str, text: str):
    """The first config whose precondition passes, or None if every one refuses.

    A config without a precondition matches everything, so it must be last in the list —
    `_check_config_order` asserts that at import rather than letting a catch-all silently
    shadow a specific config.
    """
    for cfg in family_configs(family):
        pre = cfg.get("precondition")
        if pre is None or pre(ident, label, text) is None:
            return cfg
    return None



# ARO:3003040 spans BOTH beta-lactam PBP mechanisms, so it takes the list form: target
# replacement (round 52, an acquired foreign PBP) and target alteration (round 53, the
# native PBP mutated). Each config's precondition selects on the mechanism id the record
# itself carries, so the two are mutually exclusive and the order is not load-bearing.
FAMILY_SNIPPETS["ARO:3003040"] = [
    FAMILY_SNIPPETS["ARO:3003040"],
    FAMILY_SNIPPETS.pop("ARO:3003040-mutation"),
]


# ARO:3000576 holds FOUR chemistries that inactivate rifampin (round 62): the arr
# ADP-ribosyltransferases curated first, plus hydroxylation, phosphorylation and
# glycosylation. Each config's precondition selects on the mechanism id the record itself
# carries, so they are mutually exclusive and order is not load-bearing.
FAMILY_SNIPPETS["ARO:3000576"] = [
    FAMILY_SNIPPETS["ARO:3000576"],
    _rifampin_modification_config(
        "ARO:3000450", "hydroxylation",
        "Inactivation of an antibiotic via introduction a hydroxyl group (-OH).",
        "rifampin hydroxylase activity"),
    _rifampin_modification_config(
        "ARO:3000105", "phosphorylation",
        "Phosphorylation of antibiotic usually by ATP, sometimes GTP.",
        "rifampin phosphotransferase activity",
        extra_note=("The phosphoryl donor is deliberately NOT a node: CARD says 'usually "
                    "by ATP, sometimes GTP', and picking one would assert a specificity "
                    "the source explicitly declines to give.")),
    _rifampin_modification_config(
        "ARO:3000208", "glycosylation",
        "Addition of glycosyl moiety to antibiotics thereby inactivating them.",
        "rifampin glycosyltransferase activity"),
]


# ARO:3000557 ("antibiotic inactivation enzyme") holds several chemistries; its three
# largest are group transfers onto the drug. Each config's precondition selects on the
# mechanism id the record carries, so they are mutually exclusive.
FAMILY_SNIPPETS["ARO:3000557"] = [
    _inactivation_transfer_config(
        "ARO:3000107", "nucleotidylation", "Modification by NMP, usually AMP.",
        "antibiotic nucleotidyltransferase activity"),
    _inactivation_transfer_config(
        "ARO:3000105", "phosphorylation",
        "Phosphorylation of antibiotic usually by ATP, sometimes GTP.",
        "antibiotic phosphotransferase activity"),
    _inactivation_transfer_config(
        "ARO:3000106", "acylation",
        "Addition of an acyl group to an antibiotic, often via acetylation by acetylCoA.",
        "antibiotic acyltransferase activity"),
]

# The four remaining chemistries under ARO:3000557 that carry a specific mechanism id.
# Unlike the three group transfers above, these CLEAVE or ADD-TO the drug rather than
# transferring a group onto it, and each of their mechanism-term definitions is specific
# with no donor hedge -- so each gets its own snippet and none needs a donor node at all.
FAMILY_SNIPPETS["ARO:3000557"] = FAMILY_SNIPPETS["ARO:3000557"] + [
    # #422/#426. This carried PROSITE's prose ("Beta-lactamases (EC 3.5.2.6) are enzymes
    # which catalyze the hydrolysis of an amide bond in the beta-lactam ring...") under
    # ARO:3000187, which does not contain a word of it -- the text is the shared preamble
    # of PROSITE:PS00146/PS00336/PS00337/PS00743, and every other snippet in this helper is
    # the mechanism term's OWN definition. A repoint was not available at config level:
    # which PROSITE record a record should cite depends on ITS Ambler class, and this
    # config spans A, C and D. ARO:3000187's own definition is general over exactly those
    # three classes, is what the surrounding `notes` already claim to be quoting ("CARD's
    # definition of beta-lactam hydrolysis"), and is the more precise mechanism statement
    # of the two -- it names the acyl-enzyme intermediate the edges assert.
    _inactivation_transfer_config(
        "ARO:3000187", "beta-lactam hydrolysis",
        "Mechanism of enzymatic degradation common to Ambler Class A, C and D "
        "beta-lactamases. A serine residue located in the active site is used to form an "
        "acyl-enzyme intermediate and subsequent hydrolysis renders the beta-lactam "
        "inactive.",
        "beta-lactam hydrolase activity", hedged_donor=False),
    _inactivation_transfer_config(
        "ARO:3004140", "fusidic acid lactonisation",
        "Enzymes shown to inactivate fusidic acid by hydrolytic cleavage from the 16 "
        "beta-position of fusidic acid and its derivatives.",
        "fusidic acid hydrolase activity", hedged_donor=False),
    _inactivation_transfer_config(
        "ARO:3003985", "bacitracin amidohydrolysis",
        "Hydrolysis of amido side-chain of asparagine-12 forming hydrogen bond with "
        "undecaprenyl pyrophosphate in bacitracin leading to antibiotic inactivation.",
        "bacitracin amidohydrolase activity", hedged_donor=False),
    _inactivation_transfer_config(
        "ARO:3000450", "hydroxylation",
        "Inactivation of an antibiotic via introduction a hydroxyl group (-OH).",
        "antibiotic hydroxylase activity", hedged_donor=False,
        # tet(34) carries ARO:3000450 and describes target PROTECTION (#267).
        exclude_marker="purine nucleotide"),
]



# ARO:3003580 carries several surface-charge routes: mprF lysyl-phosphatidylglycerol
# (existing) and
# phosphoethanolamine addition (round 73). Same charge outcome, different moiety; each
# precondition selects on the record's own definition.
# APPEND, never assign: ARO:3000748 already carries configs from earlier rounds and
# a bare assignment silently dropped all four of them.
FAMILY_SNIPPETS["ARO:3000748"] = (
    family_configs("ARO:3000748") + [FAMILY_SNIPPETS.pop("ARO:3000748-subunit")]
)

FAMILY_SNIPPETS["ARO:3000185"] = (
    family_configs("ARO:3000185") + [FAMILY_SNIPPETS.pop("ARO:3000185-generic")]
)

FAMILY_SNIPPETS["ARO:3003580"] = [
    FAMILY_SNIPPETS["ARO:3003580"],
    FAMILY_SNIPPETS.pop("ARO:3003580-petn"),
    FAMILY_SNIPPETS.pop("ARO:3003580-alm"),
    FAMILY_SNIPPETS.pop("ARO:3003580-ara4n"),
    FAMILY_SNIPPETS.pop("ARO:3003580-acyl"),
    FAMILY_SNIPPETS.pop("ARO:3003580-cpr"),
]


# Three drug-specific inactivation family terms, same shape as round 85's aminoglycoside
# one. Each is a single record: the family term itself, whose members are curated by the
# chemistry configs (rounds 62-64, 68, 70) or not yet at all.
for _fam, _drug, _snip in [
    ("ARO:3004260", "bacitracin",
     "Bah amidohydrolases are membrane proteins that inactivate bacitracin."),
    ("ARO:3000342", "fosfomycin",
     "Enzymes that inactivate fosfomycin by chemical modification."),
    ("ARO:3000201", "macrolide antibiotics",
     "Enzymes shown to inactivate macrolide antibiotics by chemical modification, thereby "
     "conferring resistance to macrolides."),
    # Added round 101. Round 100 built this builder for exactly this shape and registered
    # three families, missing two whose FAMILY TERMS have the same wording while their
    # MEMBERS were curated long before (rounds 62-64). Curating a family's members does
    # not curate the term, and nothing had been asking.
    ("ARO:3000576", "rifampin antibiotics",
     "Enzymes that inactivate rifampin antibiotics by chemical modification."),
    ("ARO:3000233", "streptogramin antibiotics",
     "Resistance to streptogramin antibiotics may be conferred through enzymatic "
     "inactivation."),
]:
    FAMILY_SNIPPETS[_fam] = (
        family_configs(_fam) + [_drug_specific_inactivation_config(_fam, _drug, _snip)]
    )


# Two fungal cytochrome P450 family terms, round 66's EF-Tu shape. Round 84 left these
# calling them thinner than EF-Tu; comparing the definitions side by side shows the same
# shape, so leaving them was an inconsistency rather than a standard.
FAMILY_SNIPPETS["ARO:3007522"] = [_fungal_p450_config(
    "ARO:3007522", "Fungal cytochrome P450 enzymes which include mutations or other modifications to confer resistance to antifungal drug compounds.", "antifungal compounds", True)]
FAMILY_SNIPPETS["ARO:3007523"] = [_fungal_p450_config(
    "ARO:3007523", "Fungal cytochrome P450 enzymes which include mutations to confer resistance to triazole-class antibiotics.", "triazoles", False)]


# The daptomycin trio (rounds 110-111): three records naming an enzyme and a resistance
# claim with nothing between. Round 66's shape, applied by a builder so the three cannot
# drift -- rounds 104-105 found two cases where I had applied this shape inconsistently
# by hand.
#
# drmA is the interesting one: CARD calls it "UNCHARACTERIZED", which is a statement about
# the evidence rather than the protein, and the note keeps it.
for _fam, _snip, _act, _note in [
    ("ARO:3003800",
     "gdpD is a glycerolphosphodiesterase whose mutations confer resistance to daptomycin.",
     "glycerolphosphodiesterase activity", ""),
    ("ARO:3003805",
     "gshF is a bifunctional glutamate-cysteine ligase/ glutathione synthetase that when "
     "mutated, confers daptomycin resistance.",
     "bifunctional glutamate-cysteine ligase / glutathione synthetase activity",
     "CARD names BOTH activities of the bifunctional enzyme; neither is linked to the drug."),
    ("ARO:3003813",
     "drmA is an uncharacterized 6-pass membrane protein, with mutations to the protein "
     "causing modest resistance to daptomycin.",
     "uncharacterized 6-pass membrane protein",
     "CARD calls it UNCHARACTERIZED and the resistance MODEST -- a statement about the "
     "evidence and the effect size, both kept rather than trimmed."),
]:
    FAMILY_SNIPPETS[_fam] = [_minimal_enzyme_config(_fam, _snip, _act, _note)]


# The last of the function-naming tail (round 112). Same builder as the daptomycin trio,
# for the same reason. kasA is deliberately NOT here: it is #220's original record, whose
# isoniazid claim PMID:12406221 contradicts, and round 102's eccC5 showed this corpus has
# no structural way to carry a contested claim.
for _fam, _snip, _act, _note in [
    ("ARO:3004953",
     "Rv0565c is a bacterial monoxygenase that has been newly uncovered in recent "
     "literature to show resistance to antibiotic.",
     "monooxygenase activity",
     "CARD dates its own evidence -- 'NEWLY UNCOVERED in recent literature' -- and names "
     "no drug at all, only 'antibiotic'."),
    ("ARO:3004878",
     "clpC1 is a subunit of the clp protease that is ATP-dependent. It functions to direct "
     "the clp protease to specific substrates.",
     "substrate-targeting subunit of the ATP-dependent clp protease",
     "A SUBUNIT with a stated role in a named complex; its resistance mechanism is not "
     "given, so unlike round 86's efflux subunits there is no complex-to-process edge to "
     "write either."),
    ("ARO:3004882",
     "Mas is a multifunctional mycocerosic acid synthase membrane-associated mas. It "
     "catalyzes the elongation of N-fatty acyl-CoA with methylamalonyl-CoA as the "
     "elongating agent to form mycocerosyl fatty acids present in mycobacterium.",
     "mycocerosic acid synthase activity",
     "CARD names substrate, co-substrate and product -- more chemistry than most records "
     "here -- and no drug."),
    ("ARO:3004911",
     "nudC is a NADH pyrophosphatase that is involved in nicotinate and nicotinamide "
     "metabolism. Mutations that occur on the nudC gene resulting in the inability for "
     "isoniazid to function.",
     "NADH pyrophosphatase activity",
     "The isoniazid twin of round 110's ethionamide nudC record, and it says 'to FUNCTION' "
     "as well -- so the same refusal to write a prodrug edge applies, for the same word."),
]:
    FAMILY_SNIPPETS[_fam] = [_minimal_enzyme_config(_fam, _snip, _act, _note)]


# Two more from the tail my narrow "names a function" regex missed (round 113): both name
# a function in a form the pattern did not match -- "An alanyl-tRNA synthetase ..." and
# "Positive regulator of ...". Ninth too-narrow pattern of the session.
for _fam, _snip, _act, _note in [
    ("ARO:3003830",
     "An alanyl-tRNA synthetase conferring resistance to novobiocin in Escherichia coli. "
     "Sequence data unavailable.",
     "alanyl-tRNA synthetase activity",
     "CARD records its own gap: 'Sequence data unavailable.'"),
    ("ARO:3003840",
     "Positive regulator of gene expression in the cysteine regulon. cysB mutants confer "
     "resistance to novobiocin, an aminocoumarin antibiotic, in Escherichia coli. "
     "Sequence data unavailable.",
     "positive regulation of the cysteine regulon",
     "A regulator of a regulon unrelated to the drug, and CARD joins the two only by "
     "juxtaposition. 'Sequence data unavailable.' here too."),
]:
    FAMILY_SNIPPETS[_fam] = [_minimal_enzyme_config(_fam, _snip, _act, _note)]


# FrxA (round 120) -- an NADH-flavin oxidoreductase resisting TWO drug classes.
#
# Its sibling nfsB (round 107) is also a nitroreductase acting on nitroaromatic
# antibiotics, and CARD there says the enzyme reduces the drugs themselves, which licensed
# a prodrug-activation-loss reading. FrxA's sentence says only that it IS an oxidoreductase
# and that mutations confer resistance -- so the same reading is not available and the
# graph carries the function alone.
#
# NOT curated this round: ARO:3004915, the ESX-5 SECRETION SYSTEM term. Round 102 curated
# its subunits (eccB5, eccC5) with part-of edges into the complex; the system term itself
# is the complex-versus-subunit question that #229 is about, and curating it would answer
# that by fiat.
FAMILY_SNIPPETS["ARO:3007059"] = [_minimal_enzyme_config(
    "ARO:3007059",
    "FrxA encodes an NADH-flavin oxidoreductase in Helicobacter pylori. Mutations in this "
    "gene confer resistance to nitrofuran antibiotics and metronidazole.",
    "NADH-flavin oxidoreductase activity",
    "Two drug classes from one enzyme. Its sibling nfsB (round 107) says the enzyme REDUCES "
    "the antibiotics, which licensed a prodrug reading; this one does not, so the same edge "
    "is not written.")]

def _check_config_order() -> None:
    for fam in FAMILY_SNIPPETS:
        cfgs = family_configs(fam)
        for cfg in cfgs[:-1]:
            if cfg.get("precondition") is None:
                raise ValueError(
                    f"{fam}: a config with no precondition matches every record, so it "
                    f"must be last; one before it would silently shadow the rest")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--family", help="family ARO id (must be in FAMILY_SNIPPETS)")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--repromote-edited", action="store_true",
                    help="overwrite a promoted graph that has been EDITED since (#204). "
                         "The default refuses and lists them; this is for a curator who "
                         "has read the list and decided the config wins.")
    ap.add_argument("--drafts-only", action="store_true",
                    help="accepted for compatibility and now the DEFAULT; see --repromote")
    ap.add_argument("--force-repromote", action="store_true",
                    help="bypass the #280 blast-radius refusal; rewrites every already-"
                         "curated record under the family term, including ones curated "
                         "by other configs")
    ap.add_argument("--repromote", action="store_true",
                    help="also rewrite this promoter's own existing `resistance` graphs "
                         "(needed after a config change). Off by default: rewriting a "
                         "graph a curator may have improved is destructive, and the safe "
                         "behaviour should not depend on remembering a flag (#204)")
    ap.add_argument("--only", default="",
                    help="comma-separated ARO ids: re-promote ONLY these, still under "
                         "--family and still through their own config. The narrow answer "
                         "to #280 -- a config change that affects 6 records of a family's "
                         "65 currently has two options, rewrite all 65 or hand-edit the 6, "
                         "and both are how a repair introduces a defect (#425)")
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
            cands = _candidates(fam, terms)
            for cfg_i in family_configs(fam):
                total += verify(fam, cfg_i, terms, cands)
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
        cands = _candidates(args.family, terms)
        return 1 if sum(verify(args.family, c, terms, cands)
                        for c in family_configs(args.family)) else 0

    # #280: --repromote's blast radius is the whole family SUBTREE, and ARO family terms
    # are deep ancestors. Refreshing 8 records under ARO:3000557 re-promoted 5,036 --
    # thousands of beta-lactamases curated in rounds 12-16 under their OWN, more specific
    # configs, whose class A active-site wiring the generic config overwrote. Nothing was
    # committed and all 5,036 were restored, but nothing warned either.
    #
    # --only is checked HERE, against the family, rather than trusted from the command
    # line. A typo'd or out-of-family id would otherwise select nothing, and the run would
    # report "0 records written" and exit 0 -- indistinguishable from "already up to date",
    # which is the same silent-bypass shape --traits-root grew a guard for in #418.
    only = {s.strip() for s in args.only.split(",") if s.strip()}
    if only:
        stray = {i for i in only if args.family not in E.ancestry(terms, i)}
        if stray:
            print(f"FAIL: --only names {len(stray)} id(s) that are not under "
                  f"{args.family}: {', '.join(sorted(stray))}")
            return 1

    # A pre-pass, because the guard is useless after the first write.
    if args.repromote and args.apply and not args.force_repromote:
        n_draft = n_repromote = 0
        for pth in sorted(ARO_DIR.glob("*.yaml")):
            text = pth.read_text(encoding="utf-8")
            im = re.search(r'^identifier:\s*"?(ARO:[^"\s]+)"?\s*$', text, re.M)
            if not im or args.family not in E.ancestry(terms, im.group(1)):
                continue
            if only and im.group(1) not in only:
                continue                # --only shrinks the blast radius the guard measures
            lm = re.search(r'^label:\s*"?(.+?)"?\s*$', text, re.M)
            if config_for(args.family, im.group(1), lm.group(1) if lm else "", text) is None:
                continue
            if "graph_id: resistance-draft" in text:
                n_draft += 1
            elif ("graph_id: resistance\n" in text
                  and "curator: edison-causal-graphs" in text):
                n_repromote += 1
        # Refuse when the rewrite dwarfs the actual work. 5,036-vs-8 was three orders of
        # magnitude; a legitimate config change touching its own family is the same order.
        if n_repromote > max(25, 5 * n_draft):
            print(f"REFUSING --repromote: it would rewrite {n_repromote:,} already-curated "
                  f"records against {n_draft:,} draft(s) under {args.family}.")
            print("  Family terms are deep ancestors, so this set includes records curated "
                  "by OTHER, more specific configs (#280).")
            print("  If that is genuinely intended, re-run with --force-repromote.")
            print("  NOTE: that count is what this run REACHES, not what it would write. "
                  "The #204 ownership guard refuses records written by another family "
                  "config, so the actual write set is smaller -- 253 of these 1,599 on "
                  "ARO:3000076 when this was measured. --force-repromote lifts THIS "
                  "check only; it does not lift the ownership guard, and the two are "
                  "independent on purpose.")
            return 1

    promoted = repromoted = skip_done = skip_nodraft = skip_excluded = 0
    skip_edited = 0
    skip_unreadable = 0
    reached: set[str] = set()
    for pth in sorted(ARO_DIR.glob("*.yaml")):
        text = pth.read_text(encoding="utf-8")
        ident_m = re.search(r'^identifier:\s*"?(ARO:[^"\s]+)"?\s*$', text, re.M)
        if not ident_m:
            continue
        if args.family not in E.ancestry(terms, ident_m.group(1)):
            continue
        if only and ident_m.group(1) not in only:
            continue
        label_for_cfg = re.search(r'^label:\s*"?(.+?)"?\s*$', text, re.M)
        label_text = label_for_cfg.group(1) if label_for_cfg else ""
        # SELECT the config first, then apply its exclusions. A family may carry several
        # configs (#208) -- vanR/vanS span both van routes -- and the `precondition` each
        # already has for #201 is the selector: the predicate that refuses a record is
        # what chooses between configs.
        record_cfg = config_for(args.family, ident_m.group(1), label_text, text)
        if record_cfg is None:
            if not args.apply:
                reasons = [c["precondition"](ident_m.group(1), label_text, text)
                           for c in family_configs(args.family)]
                print(f"  precondition skip: {ident_m.group(1)} — "
                      f"{'; '.join(r for r in reasons if r)}")
            skip_excluded += 1
            continue
        if ident_m.group(1) in record_cfg.get("exclude", ()):
            # a descendant this config's mechanism does NOT describe, named rather than
            # derived because the reason differs each time and "why is this one not
            # promoted" should be answerable from the config.
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
            graph = promoted_graph_dict(ident, label, mech, drug, names, record_cfg, terms)
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
        # `record_io.graph_ids` raises on a duplicated top-level `causal_graphs:` key, and
        # that check has to come FIRST: `yaml.safe_load` silently keeps the LAST such block
        # and discards the earlier one, so merging through a loader would quietly delete
        # graphs on exactly the corrupted record record_io was written to catch. 0 records
        # carry a duplicate today; the point is not to be the tool that hides it.
        #
        # A parse failure is skipped rather than raised: the old line-splice never parsed,
        # so it could not crash mid-run and leave a partial batch written.
        try:
            RIO.graph_ids(text)
            doc = yaml.safe_load(text) or {}
        except (RIO.RecordError, yaml.YAMLError) as exc:
            print(f"  unparseable, skipped: {ident} — {type(exc).__name__}: "
                  f"{str(exc).splitlines()[0][:90]}")
            skip_unreadable += 1
            continue
        # BOTH ids, because this promoter owns both: `resistance-draft` is what it
        # consumes and `resistance` is what it produces. Filtering only `resistance` left
        # a promoted draft carrying its own superseded draft graph alongside the curated
        # one -- caught in review because the canary had exercised the RE-promote path
        # (where the graph is already `resistance`) and not the primary promote-a-draft
        # path, which is the one that runs 1,133 more times.
        # DOES THIS RECORD STILL HOLD WHAT WE WROTE? (#204, the half #205 left.)
        #
        # #205 stopped re-promotion destroying OTHER graphs and the curation_history by
        # merging instead of splicing. It did not address the case the issue calls the one
        # that loses work: an edit to the promoter's OWN `resistance` graph, which is
        # replaced wholesale on every --repromote.
        #
        # `is_ours` cannot see it. It establishes that this promoter once wrote a graph
        # here, not that the current content is still that graph -- and a curator who
        # improves a promoted graph leaves both its markers in place.
        #
        # TWO TESTS, because a fingerprint only protects records written after it exists:
        #
        #   * emitted_hash present -> exact. Still hashes the same: ours, untouched,
        #     overwriting is safe. Differs: SOMEONE EDITED IT. Refuse.
        #   * emitted_hash absent (every record promoted before this change) -> fall back
        #     to "does the graph still equal what this config emits today". If yes, the
        #     rewrite is a no-op and safe whatever its history. If no, an edit and a config
        #     change are INDISTINGUISHABLE from the record alone -- which is exactly why
        #     the issue rejected reproduce-and-compare as a complete answer -- so refuse
        #     and say so rather than guess.
        #
        # THE TRIGGER IS NOT LATENT, and #204 says it is. That issue looked for records
        # with more than one GRAPH and found none. The real shape is more than one CONFIG
        # claiming one graph: 5,433 of 7,211 promoter-owned records are claimed by two or
        # three family configs (#465 measured this), and whichever ran last owns what is
        # on disk.
        #
        # Measured on ARO:3000076 (class C beta-lactamase): a --repromote reaches 1,599
        # records and 1,346 hold a graph this config did not write, every one of them
        # reproducing from a DIFFERENT claiming config (0 are in #408's drifted set).
        #
        # WHAT THOSE 1,346 WOULD ACTUALLY LOSE, checked rather than asserted, because the
        # first version of this comment said "destroys what it did not write, at 84% of
        # one family" and that overstates it. Nodes, edges, references and snippets are
        # IDENTICAL in all 1,346. They differ in exactly one key: the graph `description`,
        # where the narrow family's name is replaced by the broad one's --
        #
        #   -PDC is a class C serine beta-lactamase (AmpC cephalosporinase); ...
        #   +class C beta-lactamase is a class C serine beta-lactamase (AmpC ...); ...
        #
        # so the replacement is degenerate prose rather than destroyed evidence. Still
        # worth refusing -- it is a strictly worse description written by a config that
        # does not own the record -- but the harm is a sentence, not a graph, and the
        # comment should say which.
        #
        # 253 records in that family still re-promote by default, which is what the flag
        # is for.
        existing = next((g for g in (doc.get("causal_graphs") or [])
                         if g.get("graph_id") == "resistance"), None)
        recorded, last_owner = promoter_wrote_this(doc, args.family)
        if existing is not None:
            # OWNERSHIP FIRST. Testing `recorded` first meant a family that had EVER
            # written this record was told "edited since this config wrote it" once
            # another config took it over -- blaming a human edit for what the record
            # itself says is a change of owner. Direction was safe (it still refused)
            # and the diagnosis was wrong, which is the failure this redesign existed
            # to remove.
            # UNCONDITIONAL, not `if not is_draft`. The merge below filters BOTH owned
            # graph ids, so a record carrying a `resistance-draft` AND a curated
            # `resistance` graph had the curated one replaced with no check and no
            # REFUSED line -- the same bug through the other door. Not reachable today
            # (188 records carry drafts, none also carries `graph_id: resistance`,
            # because the drafter skips any record with a causal_graphs block), which
            # is exactly why it would have sat here unnoticed.
            if last_owner is not None and last_owner != args.family:
                untouched = False
                why = f"written by {last_owner}, a different family config"
            elif recorded is not None:
                untouched = graph_fingerprint(existing) == recorded
                why = "edited since this config wrote it"
            elif last_owner is not None:
                # A DIFFERENT family config wrote what is here. Not an edit and not
                # drift -- it belongs to another config, and re-promoting this family
                # over it replaces a narrower family's account with a broader one's.
                untouched = False
                why = f"written by {last_owner}, a different family config"
            else:
                untouched = existing == graph
                why = ("no emitted_hash, and its graph is not what this config emits "
                       "-- an edit and a config change cannot be told apart here")
            if not untouched and not args.repromote_edited:
                print(f"  REFUSED {ident}: {why}. Re-run with --repromote-edited to "
                      f"overwrite it anyway.")
                skip_edited += 1
                continue

        graphs = [g for g in (doc.get("causal_graphs") or [])
                  if g.get("graph_id") not in OWNED_GRAPH_IDS]
        graphs.append(graph)
        history = list(doc.get("curation_history") or [])
        event = curation_entry(record_cfg, graph, args.family)
        # REPLACE this family's previous event, never dedup-and-skip. `if event not in
        # history` looked harmless and made the fingerprint go stale: promote with config
        # A, then B, then A again, and A's identical event is already present so it is not
        # re-appended -- leaving B's event last while the disk holds A's graph. The next A
        # run then refuses its own writes as "edited" with nothing edited. Keying on
        # (curator, emitted_for) also keeps exactly one event per family instead of one per
        # distinct hash.
        history = [e for e in history
                   if not (isinstance(e, dict)
                           and e.get("curator") == "edison-causal-graphs"
                           and e.get("emitted_for") == args.family)]
        history.append(event)
        new = RIO.replace_block(text, "causal_graphs", "\n".join(_dump({"causal_graphs": graphs})))
        new = RIO.replace_block(new, "curation_history",
                                "\n".join(_dump({"curation_history": history})))
        new = re.sub(r"^mapping_status: SEEDED$", "mapping_status: REVIEWED", new, flags=re.M)
        if args.apply:
            pth.write_text(new, encoding="utf-8")
        promoted += 1
        repromoted += 0 if is_draft else 1
        reached.add(ident_m.group(1))
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
    if skip_edited:
        # Its own line, and NOT folded into the skip counts. "Already curated" means there
        # was nothing to do; this means work would have been DESTROYED. Averaging the two
        # into one number is the conflation #204 is about.
        print(f"  REFUSED (edited since promotion, or unverifiable): {skip_edited:,} — "
              f"listed above. Nothing was written for these.")
    print(f"  skipped (already curated): {skip_done:,} | skipped (no draft): {skip_nodraft:,}"
          f" | skipped (excluded by config): {skip_excluded:,}"
          f" | skipped (unreadable): {skip_unreadable:,}")

    # Every --only id must have been WRITTEN, not merely be in the family. One that was
    # excluded by its config, or has no draft and no --repromote, silently contributes
    # nothing -- and "6 requested, 4 written" is the difference between a finished repair
    # and one that left two records asserting the thing it was fixing.
    #
    # AFTER the summary, not before it (#435): the first version returned 1 here, so the
    # one run that most needs its counts read printed none of them.
    if only:
        missed = sorted(only - reached)
        if missed and args.limit and promoted >= args.limit:
            # #435: this check used to be skipped outright whenever --limit was set, so
            # `--only A,B,C --limit 2` dropped C, printed "2 records written" and exited 0.
            # --limit is a deliberate early stop, so it is not a failure -- but it is also
            # not the success the exit code alone would report.
            print(f"NOTE: --limit {args.limit} stopped the run before {len(missed)} of the "
                  f"--only record(s) were reached: {', '.join(missed)}. Nothing is wrong "
                  f"with them; they were simply not attempted. Re-run without --limit.")
        elif missed:
            print(f"FAIL: --only named {len(only)} record(s) but {len(missed)} were not "
                  f"written: {', '.join(missed)}")
            print("  Each was skipped by its config's precondition, its exclude list, for "
                  "being already curated without --repromote, or REFUSED by the #204 "
                  "ownership guard -- that fourth reason was missing here, so a curator "
                  "was sent to the config three times over when the answer was "
                  "--repromote-edited. Re-read the skip and REFUSED lines above; nothing "
                  "was written for these.")
            return 1
    print("APPLIED." if args.apply else "Dry-run — pass --apply to write.")
    return 0



# Two more MECHANISM-keyed pockets, same root-keyed treatment as resistance-by-absence
# (round 71): the mechanism id is not an is_a ancestor of its own records, so the
# precondition does the selection and ARO:3000000 is only a scan root.
FAMILY_SNIPPETS["ARO:3000000"] = [
    FAMILY_SNIPPETS["ARO:3000000"],
    {
        # 14th mechanism kind: the cell stops needing the pathway the drug blocks, by
        # importing the product from the host instead. Nothing resists and nothing is
        # modified -- the target simply stops mattering.
        "curated": "2026-08-07T00:00:00Z",
        "precondition": _requires_mech("ARO:3007424", "host-nutrient bypass"),
        "reference": "ARO:3007424",
        "mech": {"ARO:3007424": "Resistance via uptake of host nutrients to bypass antibiotic mechanism."},
        "mech_res": "Resistance via uptake of host nutrients to bypass antibiotic mechanism.",
        "det_res": [
            {"reference": "ARO:3007424", "snippet": "Resistance via uptake of host nutrients to bypass antibiotic mechanism.",
             "notes": "The mechanism: uptake of a HOST nutrient bypasses the step the drug blocks."},
            {"reference": "ARO:3007427", "snippet": "ThfT is an ECF transporter S component that expands the substrate profile of endogenous ECF transporters to include folate biosynthesis end products. It confers resistance to the folate synthesis inhibitor sulfamethoxazole by allowing uptake of host folate.",
             "notes": "The worked case. SCOPE: ThfT and folate specifically -- the mechanism term does not name a nutrient, and the other two records are the generic family and the transporter component."},
        ],
        "res_drug": "Resistance via uptake of host nutrients to bypass antibiotic mechanism.",
        "note": "Bypass by host-nutrient uptake. The drug's target is untouched; it stops being required.",
        "extra_nodes": [
            {"node_id": "uptake", "label": "host-nutrient uptake activity",
             "node_type": "MOLECULAR_FUNCTION",
             "description": "Ungrounded: not looked up rather than guessed (rounds 56-71)."},
            {"node_id": "bypassed", "label": "the drug-blocked step is no longer required",
             "node_type": "STATE",
             "description": "The causal core. Ungrounded: a requirement's absence is not an entity."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "uptake",
             "predicate": "enables (imports the host nutrient)", "predicate_id": "RO:0002327",
             "evidence": [{"reference": "ARO:3007424", "snippet": "Resistance via uptake of host nutrients to bypass antibiotic mechanism.",
                           "notes": "'uptake of host nutrients'."}]},
            {"subject": "uptake", "object": "bypassed",
             "predicate": "causally upstream of (makes the blocked step dispensable)",
             "predicate_id": "RO:0002411",
             "description": "Why this is resistance without touching the drug or its target.",
             "evidence": [{"reference": "ARO:3007424", "snippet": "Resistance via uptake of host nutrients to bypass antibiotic mechanism.",
                           "notes": "'to bypass antibiotic mechanism' -- the target is not altered, it is made irrelevant."}]},
        ],
    },
    {
        # 15th mechanism kind: sequestration. The drug is neither destroyed nor expelled --
        # it is bound up so it never reaches its target. Distinct from the inactivation
        # chemistries (rounds 62-70), where the drug molecule is chemically changed.
        "curated": "2026-08-07T00:00:00Z",
        "precondition": _requires_mech("ARO:3001206", "inactivation by sequestration"),
        "reference": "ARO:3001206",
        # BOTH ids, because BRP(MBL) carries the generic ARO:0001004 as well and
        # UncoveredMechanism correctly refused it otherwise. The same sentence serves
        # both: CARD's sequestration definition opens with "Inactivation of an
        # antibiotic", so it IS the inactivation claim, not a substitute for one.
        "mech": {"ARO:0001004": "Inactivation of an antibiotic by formation of a complex, preventing interaction of the antibiotic with its target.",
                 "ARO:3001206": "Inactivation of an antibiotic by formation of a complex, preventing interaction of the antibiotic with its target."},
        "mech_res": "Inactivation of an antibiotic by formation of a complex, preventing interaction of the antibiotic with its target.",
        "det_res": [
            {"reference": "ARO:3001206", "snippet": "Inactivation of an antibiotic by formation of a complex, preventing interaction of the antibiotic with its target.",
             "notes": "The whole mechanism, and the distinction that matters: a COMPLEX is formed, so the drug is intact but unavailable."},
        ],
        "res_drug": "Inactivation of an antibiotic by formation of a complex, preventing interaction of the antibiotic with its target.",
        "note": "Sequestration. The drug is bound, not chemically changed -- unlike every inactivation chemistry in rounds 62-70.",
        "extra_nodes": [
            {"node_id": "complex", "label": "determinant-antibiotic complex",
             "node_type": "STATE",
             "description": "The bound drug. Ungrounded: a specific protein-drug complex has no term here."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "drug0",
             "predicate": "molecularly interacts with (binds the drug)",
             "predicate_id": "RO:0002436",
             "evidence": [{"reference": "ARO:3001206", "snippet": "Inactivation of an antibiotic by formation of a complex, preventing interaction of the antibiotic with its target.",
                           "notes": "'formation of a complex' -- a binding event, not a reaction."}]},
            {"subject": "complex", "object": "drug0",
             "predicate": "has part (the sequestered antibiotic)", "predicate_id": "BFO:0000051",
             "description": "The drug is a CONSTITUENT of the complex, which is what makes it unavailable -- round 21's correction, where a drug-interacts-with-complex edge was circular.",
             "evidence": [{"reference": "ARO:3001206", "snippet": "Inactivation of an antibiotic by formation of a complex, preventing interaction of the antibiotic with its target.",
                           "notes": "The complex is what the drug ends up inside."}]},
            {"subject": "complex", "object": "resistance",
             "predicate": "causally upstream of (drug never reaches its target)",
             "predicate_id": "RO:0002411",
             "evidence": [{"reference": "ARO:3001206", "snippet": "Inactivation of an antibiotic by formation of a complex, preventing interaction of the antibiotic with its target.",
                           "notes": "'preventing interaction of the antibiotic with its target'."}]},
        ],
    },
]


# ---------------------------------------------------------------------------------------
# Round 121 — three ribosomal-protein target families, and what each source will and will
# not support.
#
# All three are `ARO:3000212` (mutation conferring antibiotic resistance) and all three are
# small-subunit ribosomal proteins. They get three DIFFERENT graphs, because their CARD
# definitions differ in exactly the way that decides how much may be asserted:
#
#   rpsA (ARO:3004722) — CARD names the drug's activation, the binding, and the process
#                        inhibited, AND states the function is preserved. Fullest graph.
#   rpsL (ARO:3003395) — CARD states a mechanism its own primary source only hedges.
#                        Curated at the SOURCE's strength, not CARD's.
#   rpsE (ARO:3007526) — CARD says "associated with" and gives no mechanism at all.
#                        Structural facts only, plus a `correlated with` edge (#345).
#
# `Pfam:PF00575` is deliberately NOT used as rpsA's domain node: the KB record's label says
# "S1 RNA binding domain" but its definition is IPR059328's abstract ("Domain of unknown
# function DUF8284") — the wrong InterPro entry, filed as #344. Round 21's rule applies:
# the weaker-looking node with real evidence beats the better-looking node with borrowed
# evidence, and here the borrowed evidence is a different domain entirely.
#
# Three groundings recalled from memory were wrong and are left ungrounded rather than
# guessed (#346): CHEBI:45001 (obsolete, and its `term_replaced_by` is an unrelated
# chemical), SO:0000407 (is `cytosolic_18S_rRNA`, not 16S), SO:0005836 (is
# `regulatory_region`, not pseudoknot).

# Shi et al., Science 2011 — the paper that identified RpsA as POA's target. Every clause
# CARD's two rpsA records make is a sentence of this abstract.
_POA_ACTIVATION = "PZA is hydrolyzed intracellularly to pyrazinoic acid (POA) by pyrazinamidase (PZase, encoded by pncA), an enzyme frequently lost in PZA-resistant strains, but the target of POA in Mycobacterium tuberculosis has remained elusive."
_POA_TARGET = "Here, we identify a previously unknown target of POA as the ribosomal protein S1 (RpsA), a vital protein involved in protein translation and the ribosome-sparing process of trans-translation."
# The one sentence carrying BOTH the binding and its loss in the mutant — the same
# two-arms-in-one-sentence shape as round 21's vanH affinity quote.
_POA_BINDING = "RpsA overexpression conferred increased PZA resistance, and we confirmed that POA bound to RpsA (but not a clinically identified ΔAla mutant) and subsequently inhibited trans-translation rather than canonical translation."
_CARD_RPSA = "The 30S ribosomal protein S1 of Mycobacterium tuberculosis is required for mRNA translation initiation, playing a particular role in trans-translation. Mutations to rpsA prevent pyrazinoic acid, the active form of pyrazinamide catalyzed by pncA, from targeting RpsA to inhibit translation."
_CARD_RPSA_KEPT = "RpsA, the 30S ribosomal protein S1 of Mycobacterium tuberculosis, is involved in trans-translation and is targeted by pyrazinonic acid, the active form of the antibiotic pyrazinamide, which disrupts the initiation of mRNA translation. Mutations in the amino acid sequence of rpsA can confer resistance to pyrazinamide maintaining rpsA function."
_POA_ISOLATES = "Three PZA-resistant clinical isolates without pncA mutation harbored RpsA mutations."

FAMILY_SNIPPETS["ARO:3004722"] = {   # rpsA / ribosomal protein S1 — pyrazinamide
    "curated": "2026-08-10T00:00:00Z",
    "precondition": _requires_mech("ARO:3000212", "mutation"),
    "reference": "PMID:21835980",
    "mech": {"ARO:3000212": _POA_BINDING},
    "mech_res": _POA_BINDING,
    "det_res": [
        {"reference": "ARO:3004722", "snippet": _CARD_RPSA,
         "notes": "CARD makes the causal claim ('Mutations to rpsA PREVENT pyrazinoic acid ... "
                  "from targeting RpsA'), so CARD carries the edge that asserts it (#354)."},
        {"reference": "PMID:21835980", "snippet": _POA_ISOLATES,
         "notes": "Corroboration, and explicitly a CO-OCCURRENCE, not a conferral: three "
                  "isolates resistant WITHOUT a pncA mutation that carried RpsA mutations. "
                  "Shi's conferral result is about OVEREXPRESSION, not about these mutations, "
                  "so it is not cited here."},
    ],
    "res_drug": _POA_TARGET,
    "note": ("rpsA -- target alteration with the target's own function EXPLICITLY PRESERVED. "
             "CARD ARO:3004721 says mutations resist 'maintaining rpsA function', and Shi 2011 "
             "says POA inhibited 'trans-translation rather than canonical translation'. Two "
             "independent statements that nothing is lost, so NO loss-of-function edge is "
             "written -- see the test that pins the omission."),
    "extra_nodes": [
        {"node_id": "poa", "label": "pyrazinoic acid (POA), the active form of pyrazinamide",
         "node_type": "CHEMICAL", "grounding": "CHEBI:71311",
         "description": "ChEBI `pyrazine-2-carboxylic acid`. Grounded by label match, not by "
                        "recall: the recalled CHEBI:45001 is obsolete AND was a different "
                        "compound (#346)."},
        {"node_id": "trans_translation", "label": "trans-translation",
         "node_type": "BIOLOGICAL_PROCESS", "grounding": "GO:0070929"},
        {"node_id": "rpsa_wt", "label": "ribosomal protein S1 (RpsA), drug-sensitive form",
         "node_type": "PROTEIN",
         "description": "The drug's TARGET. THE SAME PROTEIN AS `determinant`, in its "
                        "unsubstituted form -- ARO:3004722 denotes the resistant allele, and "
                        "the source says POA does not bind that (#349). No EDGE states that "
                        "relation because RO has no allelic-variant predicate: RO:0002312 is "
                        "'evolutionary variant of', RO:0001000 'derives from', neither means "
                        "this. Forcing one would be #346's mistake (#357). Ungrounded -- only "
                        "the resistant allele has an ARO term."},
        {"node_id": "poa_rpsa", "label": "POA-RpsA complex", "node_type": "STATE",
         "description": "The binding event the resistant mutant loses. Ungrounded, as with "
                        "the other drug-target complexes in this corpus (round 21)."},
    ],
    "extra_edges": [
        {"subject": "drug0", "object": "poa",
         "predicate": "causally upstream of (hydrolysed to the active form)",
         "predicate_id": "RO:0002411",
         "requires": {"drug0": "ARO:3007155"},
         "description": "Pyrazinamide is a prodrug; PZase (pncA) makes the species that acts.",
         "evidence": [{"reference": "PMID:21835980", "snippet": _POA_ACTIVATION,
                       "notes": "The activation step CARD ARO:3004722 names ('catalyzed by pncA'). "
                                "NOTE the drug0 node is the drug CLASS (ARO:3007155, pyrazine "
                                "antibiotic) and this claim holds for pyrazinamide specifically, "
                                "not for every pyrazine (#353). NOT asserted: loss of pncA, a "
                                "different determinant and this abstract's own contrast case."}]},
        {"subject": "poa", "object": "rpsa_wt",
         "predicate": "molecularly interacts with (binds drug-sensitive RpsA)",
         "predicate_id": "RO:0002436",
         "description": "The drug's normal action. Its object is the drug-SENSITIVE protein, "
                        "not this record's determinant -- pointing it at the determinant made "
                        "the graph assert both that POA binds it and that it abolishes POA "
                        "binding (#349).",
         "evidence": [{"reference": "PMID:21835980", "snippet": _POA_BINDING,
                       "notes": "'POA bound to RpsA' -- and the parenthesis says which RpsA: "
                                "'but not a clinically identified ΔAla mutant'. DRUG-ACTION arm; "
                                "resistance is its loss."}]},
        {"subject": "poa_rpsa", "object": "poa",
         "predicate": "has part (the drug half of the complex)", "predicate_id": "BFO:0000051",
         "description": "The other constituent. Round 121 first defined this complex by its "
                        "protein half alone, so a node labelled for two participants was "
                        "structurally made of one (#370).",
         "evidence": [{"reference": "PMID:21835980", "snippet": _POA_BINDING,
                       "notes": "'POA bound to RpsA' -- POA is the other constituent."}]},
        {"subject": "poa_rpsa", "object": "rpsa_wt",
         "predicate": "has part (the protein half of the complex)", "predicate_id": "BFO:0000051",
         "description": "Round 21's rule: a complex is DEFINED by its constituents rather than "
                        "interacting with them.",
         "evidence": [{"reference": "PMID:21835980", "snippet": _POA_BINDING,
                       "notes": "'POA bound to RpsA' -- the two constituents of the complex."}]},
        {"subject": "rpsa_wt", "object": "trans_translation",
         "predicate": "enables (ribosome-sparing trans-translation)", "predicate_id": "RO:0002327",
         "evidence": [{"reference": "PMID:21835980", "snippet": _POA_TARGET,
                       "notes": "What the drug-sensitive protein does, which is what the drug "
                                "interrupts."}]},
        {"subject": "determinant", "object": "trans_translation",
         "predicate": "enables (ribosome-sparing trans-translation)", "predicate_id": "RO:0002327",
         "description": "The resistant variant STILL does this.",
         "evidence": [{"reference": "ARO:3004721", "snippet": _CARD_RPSA_KEPT,
                       "notes": "The claim the description makes, cited where it is actually "
                                "made: 'maintaining rpsA function'. Round 2 of review found the "
                                "description asserting this over evidence that did not say it "
                                "(#359). NOTE this is the more specific term ARO:3004721; "
                                "ARO:3004722's own definition says mutations 'prevent pyrazinoic "
                                "acid from TARGETING RpsA' and does not itself state that the "
                                "function is preserved (#371)."},
                      {"reference": "PMID:21835980", "snippet": _POA_TARGET,
                       "notes": "'a vital protein involved in protein translation and the "
                                "ribosome-sparing process of trans-translation'."}]},
        {"subject": "poa", "object": "trans_translation",
         "predicate": "negatively regulates (inhibits trans-translation)",
         "predicate_id": "RO:0002212",
         "description": "What the drug does once bound -- and the specificity that makes the "
                        "mechanism coherent: canonical translation is NOT inhibited.",
         "evidence": [{"reference": "PMID:21835980", "snippet": _POA_BINDING,
                       "notes": "'inhibited trans-translation rather than canonical translation'. "
                                "The negative half is the point -- the same device as round 23's "
                                "vanXY specificity edge."}]},
        {"subject": "determinant", "object": "poa_rpsa",
         "predicate": "negatively regulates (substitution abolishes drug binding)",
         "predicate_id": "RO:0002212",
         "description": "The causal core: the resistant substitution is the loss of the binding, "
                        "not the loss of the protein's job.",
         "evidence": [{"reference": "PMID:21835980", "snippet": _POA_BINDING,
                       "notes": "The parenthesis '(but not a clinically identified ΔAla mutant)' "
                                "is the resistance result -- a NEGATIVE finding, which is why the "
                                "whole sentence is quoted rather than its first clause."}]},
        {"subject": "poa_rpsa", "object": "trans_translation",
         "predicate": "negatively regulates (the bound complex is what inhibits)",
         "predicate_id": "RO:0002212",
         "evidence": [{"reference": "PMID:21835980", "snippet": _POA_BINDING,
                       "notes": "'bound to RpsA and subsequently inhibited' -- the binding is "
                                "upstream of the inhibition in the source's own word order."}]},
    ],
}

# rpsL. CARD asserts a mechanism ('S12 stabilizes the pseudoknot'; resistance 'by disrupting
# interactions between 16S rRNA and streptomycin') that PMID:7934937 -- the paper the
# definition is built from -- states only as a LINKAGE and an ASSOCIATION.
#
# The stance is PER-CLAIM, not per-record (#347 review rounds 4 and 5, which found this
# comment still asserting the record-level version). The conferral edges DO follow CARD,
# because CARD is the only source that states conferral and refusing it there would leave
# the record asserting a mechanism with nobody claiming the outcome. Exactly ONE edge --
# determinant -> pseudoknot -- is curated below CARD's strength, and it is the one claim the
# two sources actually disagree about. The gap is stated on that edge rather than resolved
# in CARD's favour.
_RPSL_MUTATIONS = "The mutations found either lead to amino acid changes in ribosomal protein S12 or alter the primary structure of the 16S rRNA."
_RPSL_PSEUDOKNOT = "The 16S rRNA region mutated perturbs a pseudoknot structure in a region which has been linked to ribosomal S12 protein."
_RPSL_SOURCE_ASSOC = "We demonstrate that streptomycin resistance is associated with mutations implicated in ribosomal resistance."
_RPSL_ASSOC = "Streptomycin resistance in about one-half of M. tuberculosis isolates is associated with missense mutations in the rpsL gene coding for ribosomal protein S12 or nucleotide substitutions in the 16S rRNA gene (rrs)."
_30S_ANTIBIOTICS = "We also describe the crystal structure of the 30S subunit complexed with the antibiotics paromomycin, streptomycin and spectinomycin, which interfere with decoding and translocation."
_CARD_RPSL = "Ribosomal protein S12 stabilizes the highly conserved pseudoknot structure formed by 16S rRNA. Amino acid substitutions in RpsL affect the higher-order structure of 16S rRNA and confer streptomycin resistance by disrupting interactions between 16S rRNA and streptomycin."

FAMILY_SNIPPETS["ARO:3003395"] = {   # rpsL / ribosomal protein S12 — streptomycin
    "curated": "2026-08-10T00:00:00Z",
    "precondition": _requires_mech("ARO:3000212", "mutation"),
    # `reference` is CARD, not the 1993 paper, and that is forced by #348 + #363 together:
    # the promoter attributes mech/mech_res/res_drug to `cfg["reference"]`, those three
    # edges assert CONFERRAL, and only CARD states conferral. Putting CARD's sentence under
    # PMID:7934937 would have re-created #348 in the act of fixing #363. The 1993 paper is
    # cited explicitly on the two edges whose claims it does make. Same shape as rpsE.
    "reference": "ARO:3003395",
    "mech": {"ARO:3000212": _CARD_RPSL},
    # #348: mech_res and res_drug are attributed to cfg["reference"] by the promoter, so
    # a snippet placed there must come from that reference. Musser's (PMID:8665467) sentence
    # appears ONLY on det_res, which names its own reference.
    #
    # #363: all three carry CARD's definition rather than PMID:7934937's association
    # sentence, because all three assert CONFERRAL and only CARD states it. That is exactly
    # WHY `reference` had to become ARO:3003395 -- do not repoint it back to the PMID
    # without also moving these snippets, or #348 returns.
    "mech_res": _CARD_RPSL,
    "det_res": [
        {"reference": "ARO:3003395", "snippet": _CARD_RPSL,
         "notes": "CARD makes the causal claim -- 'CONFER streptomycin resistance by "
                  "disrupting interactions' -- so CARD carries the edge that asserts it. "
                  "Round 3 of review found this edge citing only Musser's 'is ASSOCIATED "
                  "with', which does not state conferral (#363, the same defect as #354)."},
        {"reference": "PMID:8665467", "snippet": _RPSL_ASSOC,
         "notes": "Musser 1995, corroborating and explicitly an ASSOCIATION. The MAGNITUDE is "
                  "part of the claim -- 'about one-half' of isolates, and the other half is "
                  "the rrs route, not this record."},
        {"reference": "PMID:7934937", "snippet": _RPSL_MUTATIONS,
         "notes": "Finken 1993, which is what the substitutions ARE. It reports the two "
                  "routes and does not state conferral, which is why it does not carry this "
                  "edge alone (#363)."},
        {"reference": "PMID:7934937", "snippet": _RPSL_SOURCE_ASSOC,
         "notes": "Finken 1993 stating the association in its own voice. Retained after the "
                  "#363 fix moved the conferral claim to CARD, so the source's own weaker "
                  "wording stays on the record beside CARD's stronger one (#367)."},
    ],
    "res_drug": _CARD_RPSL,
    "note": ("rpsL -- target alteration IN TRANS: the determinant is a protein, but the "
             "drug's binding partner CARD names is the 16S rRNA. CARD says S12 'stabilizes' "
             "the pseudoknot; PMID:7934937, its source, says only that the region 'has been "
             "linked to' S12 -- so THAT edge is `correlated with`, not a causal one. The "
             "conferral edges DO follow CARD (#363): CARD is the only source that states "
             "conferral, and refusing it there would leave the record asserting a mechanism "
             "with no one claiming the outcome. The record follows the weaker source on the "
             "one claim where the two disagree, not everywhere."),
    "protein_traits": {
        "primary_key": "domain",
        "domain": ("Pfam:PF00164", "Ribosomal protein S12/S23", "DOMAIN",
                   "Ribosomal protein uS12 is one of the proteins from the small ribosomal subunit. In Escherichia coli, uS12 is known to be involved in the translation initiation step."),
        "part_pred": "part of (the S12 domain of this determinant)",
        "part_note": "KB trait: the S12 domain. Its InterPro abstract was checked to mention "
                     "uS12 itself, per #196.",
    },
    "extra_nodes": [
        {"node_id": "rrna16s", "label": "16S ribosomal RNA", "node_type": "NUCLEIC_ACID",
         "description": "Ungrounded on purpose: SO:0000407, recalled as 16S rRNA, is "
                        "`cytosolic_18S_rRNA` (#346). Not looked up further rather than guessed."},
        {"node_id": "pseudoknot", "label": "16S rRNA pseudoknot structure", "node_type": "STATE",
         "description": "Ungrounded: SO:0005836, recalled as pseudoknot, is `regulatory_region` "
                        "(#346)."},
        {"node_id": "strep_binding", "label": "16S rRNA-streptomycin interaction",
         "node_type": "STATE",
         "description": "The interaction CARD says the substitution disrupts."},
    ],
    "extra_edges": [
        {"subject": "pseudoknot", "object": "rrna16s",
         "predicate": "part of (a structure of the 16S rRNA)", "predicate_id": "BFO:0000050",
         "evidence": [{"reference": "PMID:7934937", "snippet": _RPSL_PSEUDOKNOT,
                       "notes": "'a pseudoknot structure in a region' of the 16S rRNA. The one "
                                "claim in this graph both CARD and its source state plainly."}]},
        {"subject": "determinant", "object": "pseudoknot",
         "predicate": "correlated with (linked to the pseudoknot region)",
         "predicate_id": "RO:0002610",
         "description": "Deliberately WEAKER than CARD. CARD says S12 'stabilizes' the "
                        "pseudoknot; the paper it is built from says the region 'has been linked "
                        "to' S12 and reports no stabilisation experiment.",
         "evidence": [{"reference": "PMID:7934937", "snippet": _RPSL_PSEUDOKNOT,
                       "notes": "'has been linked to ribosomal S12 protein' -- a hedged linkage. "
                                "CARD upgrades it to 'stabilizes'; this edge does not follow it."},
                      {"reference": "ARO:3003395", "snippet": _CARD_RPSL,
                       "notes": "CARD's stronger wording, recorded so the disagreement is visible "
                                "on the edge rather than only in a round report."}]},
        {"subject": "drug0", "object": "rrna16s",
         "predicate": "molecularly interacts with (streptomycin binds the small subunit)",
         "predicate_id": "RO:0002436",
         "requires": {"drug0": "ARO:0000016"},
         "description": "The drug-action arm. Streptomycin acts on the 30S subunit; CARD names "
                        "the 16S rRNA as its interaction partner on this record. The drug0 node "
                        "is the CLASS (ARO:0000016), which is as specific as the guard can be "
                        "(#353).",
         "evidence": [{"reference": "PMID:11014183", "snippet": _30S_ANTIBIOTICS,
                       "notes": "Carter 2000. Establishes streptomycin binds the 30S subunit and "
                                "interferes with decoding and translocation. It does NOT state "
                                "the 16S rRNA contact residue-by-residue; that specificity is "
                                "CARD's, cited alongside."},
                      {"reference": "ARO:3003395", "snippet": _CARD_RPSL,
                       "notes": "'interactions between 16S rRNA and streptomycin' -- CARD names "
                                "the partner."}]},
        {"subject": "determinant", "object": "strep_binding",
         "predicate": "negatively regulates (substitution disrupts drug binding)",
         "predicate_id": "RO:0002212",
         "description": "The causal core as CARD states it -- and CARD alone: PMID:7934937 "
                        "reports the association, not this step.",
         "evidence": [{"reference": "ARO:3003395", "snippet": _CARD_RPSL,
                       "notes": "'confer streptomycin resistance by disrupting interactions "
                                "between 16S rRNA and streptomycin'. CARD's mechanism claim, "
                                "attributed to CARD because its source does not make it."}]},
        {"subject": "strep_binding", "object": "drug0",
         "predicate": "has part (the streptomycin half of the interaction)",
         "predicate_id": "BFO:0000051",
         "requires": {"drug0": "ARO:0000016"},
         "description": "The other constituent, and the more important one: the causal core "
                        "edge says the substitution disrupts THIS, and without the drug half "
                        "the thing disrupted did not structurally contain the drug (#370).",
         "evidence": [{"reference": "ARO:3003395", "snippet": _CARD_RPSL,
                       "notes": "'interactions between 16S rRNA and STREPTOMYCIN'. The drug0 "
                                "node is the CLASS (ARO:0000016), as elsewhere on this record "
                                "(#353)."}]},
        {"subject": "strep_binding", "object": "rrna16s",
         "predicate": "has part (the 16S rRNA half of the interaction)",
         "predicate_id": "BFO:0000051",
         "description": "Round 21's correction: the interaction node is DEFINED by its "
                        "constituents rather than interacting with them.",
         "evidence": [{"reference": "ARO:3003395", "snippet": _CARD_RPSL,
                       "notes": "'interactions between 16S rRNA and streptomycin'."}]},
    ],
}

# rpsE. CARD gives structure and an ASSOCIATION, and no mechanism whatever.
_CARD_RPSE = "Amino acid substitutions in ribosomal protein S5, the product of the rpsE gene, is associated with resistance to spectinomycin (SpcR). This protein is located on the 30S subunit and interacts with 16S rRNA and other proteins."
_RPSE_LOOP2 = "Modelling showed that these mutations perturb the conserved network of stabilizing contacts between RpsE residues Lys25 (Lys23 in E. coli numbering) and Lys28 (Lys26), as well as helix 34 nucleotides G922, A923, and C1069 of 16S rRNA, potentially altering the architecture of the spectinomycin-binding site."

FAMILY_SNIPPETS["ARO:3007526"] = {   # rpsE / ribosomal protein S5 — spectinomycin
    "curated": "2026-08-10T00:00:00Z",
    "precondition": _requires_mech("ARO:3000212", "mutation"),
    "reference": "ARO:3007526",
    "mech": {"ARO:3000212": _CARD_RPSE},
    "mech_res": _CARD_RPSE,
    "det_res": [
        {"reference": "ARO:3007526", "snippet": _CARD_RPSE,
         "notes": "CARD says 'is ASSOCIATED WITH resistance' and gives no mechanism. The fixed "
                  "edge shape can only say `causally upstream of`, which overstates that -- "
                  "filed as #345. The explicit `correlated with` edge below is the honest form."},
    ],
    "res_drug": _CARD_RPSE,
    "note": ("rpsE -- an ASSOCIATION, not a mechanism. CARD supplies two structural facts "
             "(S5 is on the 30S subunit; it interacts with 16S rRNA) and links substitutions "
             "to resistance without joining them. No MECHANISM edge connects the substitution "
             "to the drug -- the promoter's fixed `confers resistance to (drug class)` edge is "
             "still emitted and still carries CARD's own assertion (#345, #350)."),
    "protein_traits": {
        "primary_key": "domain",
        "domain": ("Pfam:PF00333", "Ribosomal protein S5, N-terminal domain", "DOMAIN",
                   "Small ribosomal subunit protein uS5 is one of the proteins from the small ribosomal subunit, and is a protein of 166 to 254 amino acid residues. In Escherichia coli, uS5 is known to be important in the assembly and function of the 30S ribosomal subunit."),
        "part_pred": "part of (the S5 N-terminal domain of this determinant)",
        "part_note": "KB trait: the S5 N-terminal domain. Its InterPro abstract names uS5.",
        # Pfam:PF03719 (S5 C-terminal domain) is NOT here. `protein_traits["fold"]` emits
        # "member of (adopts fold)", which would type a C-terminal DOMAIN as a fold (#352).
        # It is instead an `extra_nodes` entry with a `part of` edge -- review round 2 was
        # right that extra_nodes is the second part slot, and that dropping the node
        # altogether lost a real KB-trait link for a reason that was not true (#358).
    },
    "extra_nodes": [
        {"node_id": "domain_c", "label": "Ribosomal protein S5, C-terminal domain",
         "node_type": "DOMAIN", "grounding": "Pfam:PF03719",
         "description": "KB protein-trait record: the determinant's other half. Typed as the "
                        "DOMAIN it is, rather than through protein_traits[\"fold\"] (#352, #358)."},
        {"node_id": "subunit30s", "label": "small ribosomal subunit (30S)",
         "node_type": "CELLULAR_LOCALIZATION", "grounding": "GO:0015935"},
        {"node_id": "rrna16s", "label": "16S ribosomal RNA", "node_type": "NUCLEIC_ACID",
         "description": "Ungrounded for the same reason as the rpsL graph (#346)."},
    ],
    "extra_edges": [
        {"subject": "domain_c", "object": "determinant",
         "predicate": "part of (the S5 C-terminal domain of this determinant)",
         "predicate_id": "BFO:0000050",
         "evidence": [{"reference": "Pfam:PF03719",
                       "snippet": "This entry represents the C-terminal of the ribosomal protein uS5, which is related to the 30S ribosomal protein S5P from Sulfolobus acidocaldarius (UniProtKB:O05641).",
                       "notes": "KB trait: the S5 C-terminal domain. Its InterPro abstract names "
                                "uS5, per #196."}]},
        {"subject": "determinant", "object": "subunit30s",
         "predicate": "part of (located on the 30S subunit)", "predicate_id": "BFO:0000050",
         "evidence": [{"reference": "ARO:3007526", "snippet": _CARD_RPSE,
                       "notes": "'This protein is located on the 30S subunit'."}]},
        {"subject": "determinant", "object": "rrna16s",
         "predicate": "molecularly interacts with (interacts with 16S rRNA)",
         "predicate_id": "RO:0002436",
         "evidence": [{"reference": "ARO:3007526", "snippet": _CARD_RPSE,
                       "notes": "'and interacts with 16S rRNA and other proteins'. The 'other "
                                "proteins' are NOT given nodes -- CARD does not name them."},
                      {"reference": "PMID:42450237", "snippet": _RPSE_LOOP2,
                       "notes": "CONTEXT ONLY, carrying three qualifications at once: it is a "
                                "MODELLING result ('Modelling showed'), it is HEDGED "
                                "('potentially altering'), and it is Neisseria, whereas these "
                                "records are Bacillus subtilis and unspecified. It is attached "
                                "to the interaction edge CARD already supports, and licenses no "
                                "edge of its own."}]},
        {"subject": "drug0", "object": "subunit30s",
         "predicate": "molecularly interacts with (spectinomycin acts on the 30S subunit)",
         "predicate_id": "RO:0002436",
         "requires": {"drug0": "ARO:0000016"},
         "description": "The drug-action arm, from the 30S crystal structures.",
         "evidence": [{"reference": "PMID:11014183", "snippet": _30S_ANTIBIOTICS,
                       "notes": "Carter 2000 solved the 30S subunit with spectinomycin bound. "
                                "NOTE the drug0 node is the drug CLASS (ARO:0000016, "
                                "aminoglycoside antibiotic); spectinomycin is an aminocyclitol "
                                "that CARD files under it, and the `requires` guard can only "
                                "check the class (#353). NOT asserted: that S5 is part of that "
                                "binding site, which this abstract does not say and CARD does "
                                "not claim."}]},
        {"subject": "determinant", "object": "resistance",
         "predicate": "correlated with (substitutions are associated with resistance)",
         "predicate_id": "RO:0002610",
         "description": "The honest strength of CARD's claim, written explicitly because the "
                        "fixed determinant->resistance edge cannot express it (#345).",
         "evidence": [{"reference": "ARO:3007526", "snippet": _CARD_RPSE,
                       "notes": "'is associated with resistance to spectinomycin'. Association is "
                                "all CARD asserts, so association is all this edge asserts."}]},
    ],
}


# ---------------------------------------------------------------------------------------
# Round 122 — target alteration IN TRANS, the second and third instances.
#
# Round 121 named the shape on rpsL: the determinant is a PROTEIN, but the drug's binding
# partner is the rRNA. The protein mutation does not change the drug's site; it changes the
# conformation of the molecule that IS one. uL3/pleuromutilin is the same shape on the
# large subunit, and it is the first family where a primary paper states it outright.
#
# The uL3 family needs TWO configs, and the reason is #371, filed one round earlier:
#   ARO:3005081 names uL3 -- so the Pfam:PF00297 KB trait node is licensed.
#   ARO:3005082 says only "Ribosomal protein mutations" -- naming no protein at all.
# A single config with `protein_traits` would assert the L3 family node on a record whose
# own definition never mentions L3, which is exactly the borrowed-specificity defect #371
# describes. The list form selects by precondition, as vanR/vanS does (#208).

_TIAMULIN_TARGET = "The antibiotic tiamulin targets the 50S subunit of the bacterial ribosome and interacts at the peptidyl transferase center."
_TIAMULIN_MUTANT = "Selection in a strain with all seven chromosomal rRNA operons yielded a mutant with an A445G mutation in the gene coding for ribosomal protein L3, resulting in an Asn149Asp alteration."
_TIAMULIN_FOOTPRINT = "Chemical footprinting experiments show a reduced binding of tiamulin to mutant ribosomes."
# The mechanism sentence, and it hedges the INFERENCE itself -- round 111's shape.
_TIAMULIN_INFERRED = "It is inferred that the L3 mutation, which points into the peptidyl transferase cleft, causes tiamulin resistance by alteration of the drug-binding site."
# A negative result that settles WHICH molecule is the determinant.
_TIAMULIN_NOT_RRNA = "No mutations in the rRNA were selected as resistance determinants using a strain expressing only a plasmid-encoded rRNA operon."
_PLEURO_SITE = "Our results show that tiamulin is located within the peptidyl transferase center (PTC) of the 50S ribosomal subunit with its tricyclic mutilin core positioned in a tight pocket at the A-tRNA binding site."
_PLEURO_INHIBITS = "Thereby, tiamulin directly inhibits peptide bond formation."
_L3_HEDGE = "Ribosomal protein L3 (also known as uL3) is one of the proteins from the large ribosomal subunit. In Escherichia coli, L3 is known to bind to the 23S rRNA and may participate in the formation of the peptidyltransferase centre of the ribosome."
_CARD_UL3 = "Thermus thermophilus ribosomal protein uL3 containing various mutations conferring resistance to tiamulin. Mutations in the ribosomal protein of uL3 acts by interfering with local rRNA conformation thus conferring resistance."
_CARD_RPMUT = "Ribosomal protein mutations that interfere with the rRNA conformation at the active site thus conferring antibiotic resistance."


def _ul3_shared(card_snippet, card_ref, names_l3):
    """The pleuromutilin arm, identical whether or not the record names uL3.

    What differs is ONLY the protein-trait node, because only ARO:3005081's definition
    says which protein it is (#371).
    """
    return {
        "curated": "2026-08-10T00:00:00Z",
        "reference": card_ref,
        "mech": {"ARO:3000212": card_snippet},
        "mech_res": card_snippet,
        "det_res": [
            {"reference": card_ref, "snippet": card_snippet,
             "notes": "CARD states the causation -- 'thus conferring resistance'."},
        ] + ([
            {"reference": "PMID:12936991", "snippet": _TIAMULIN_MUTANT,
             "notes": "Bosling 2003, the substitution itself -- Asn149Asp in L3. Cited only "
                      "where the record names L3 (#374)."},
            {"reference": "PMID:12936991", "snippet": _TIAMULIN_FOOTPRINT,
             "notes": "The measurement: REDUCED BINDING to mutant ribosomes. This is what "
                      "resistance is, physically."},
        ] if names_l3 else []),
        "res_drug": card_snippet,
        "extra_nodes": [
            {"node_id": "ptc", "label": "peptidyl transferase centre (the drug's binding site)",
             "node_type": "STATE",
             "description": "Ungrounded. GO:0000048 is `peptidyltransferase activity`, the "
                            "FUNCTION, and this node is the structural site the drug occupies "
                            "-- not the same thing, so it is not reused (#346's rule: a live "
                            "CURIE that means something else is worse than none)."},
            {"node_id": "subunit50s", "label": "large ribosomal subunit (50S)",
             "node_type": "CELLULAR_LOCALIZATION", "grounding": "GO:0015934",
             "description": "What the snippet actually locates the PTC in. The earlier "
                            "`ptc part of rrna23s` edge asserted the PTC's COMPOSITION, which "
                            "no snippet on this record states -- and PF00297's own hedge (L3 "
                            "'may participate in the formation of the PTC') says the PTC is "
                            "not wholly 23S rRNA anyway (#373)."},
            {"node_id": "rrna23s", "label": "23S ribosomal RNA", "node_type": "NUCLEIC_ACID",
             "description": "The molecule whose conformation the mutation alters. Ungrounded "
                            "for the same reason the 16S node is in round 121 (#346)."},
            {"node_id": "peptide_bond", "label": "peptide bond formation",
             "node_type": "BIOLOGICAL_PROCESS",
             "description": "UNGROUNDED. GO:0006414 is `translational elongation` and "
                            "GO:0000048 is `peptidyltransferase activity` -- a broader process "
                            "and an activity. Neither IS peptide bond formation, and #346's "
                            "rule says a live CURIE that means something else is worse than "
                            "none. It was grounded to GO:0006414 until review caught the "
                            "config applying that rule to the node above and breaking it here "
                            "(#376)."},
            {"node_id": "altered_conformation",
             "label": "altered local 23S rRNA conformation at the active site",
             "node_type": "STATE",
             "description": "What the substitution produces. A STATE because the object of "
                            "the causal edge should be the CONFORMATION, not the molecule: "
                            "'interferes with the rRNA conformation' does not say the rRNA's "
                            "function is decreased, and resistant ribosomes still translate "
                            "(#377). NOT because a STATE object is disallowed -- round 121's "
                            "ARO:3003395 points RO:0002212 at a STATE, and so does this "
                            "graph, twice (#385)."},
            {"node_id": "drug_binding", "label": "tiamulin-ribosome binding", "node_type": "STATE",
             "description": "The interaction the mutation reduces."},
        ],
        "extra_edges": [
            {"subject": "ptc", "object": "subunit50s",
             "predicate": "part of (the PTC of the 50S subunit)", "predicate_id": "BFO:0000050",
             "description": "Exactly what the snippet locates, and no more (#373).",
             "evidence": [{"reference": "PMID:15554968", "snippet": _PLEURO_SITE,
                           "notes": "'the peptidyl transferase center (PTC) OF THE 50S "
                                    "RIBOSOMAL SUBUNIT'. NOT asserted: the PTC's composition, "
                                    "which this sentence does not give."}]},
            # NO `rrna23s part of subunit50s` edge. It was written to replace the one #373
            # removed, and it repeated #373's defect: _PLEURO_23S says the structure gives
            # "a detailed picture of ITS interactions with the 23S rRNA" -- "its" is
            # tiamulin's. Co-mention in one sentence is not a part-hood claim (#383).
            {"subject": "drug0", "object": "ptc",
             "predicate": "molecularly interacts with (binds the peptidyl transferase centre)",
             "predicate_id": "RO:0002436",
             "requires": {"drug0": "ARO:3000670"},
             "description": "The drug-action arm.",
             "evidence": [{"reference": "PMID:15554968", "snippet": _PLEURO_SITE,
                           "notes": "NOTE the drug0 node is the drug CLASS (ARO:3000670, "
                                    "pleuromutilin antibiotic); tiamulin is the member both "
                                    "papers studied (#353)."},
                          {"reference": "PMID:12936991", "snippet": _TIAMULIN_TARGET,
                           "notes": "Bosling 2003 states the same target independently."}]},
            {"subject": "drug_binding", "object": "drug0",
             "predicate": "has part (the antibiotic)", "predicate_id": "BFO:0000051",
             "requires": {"drug0": "ARO:3000670"},
             "description": "Round 21's rule, and round 121's #370: a binding state is defined "
                            "by BOTH constituents, not one.",
             "evidence": ([{"reference": "PMID:12936991", "snippet": _TIAMULIN_FOOTPRINT,
                            "notes": "'binding of tiamulin to ... ribosomes' -- the drug half."}]
                          if names_l3 else
                          [{"reference": "PMID:12936991", "snippet": _TIAMULIN_TARGET,
                            "notes": "'tiamulin ... INTERACTS AT the peptidyl transferase "
                                     "center' -- the drug half, from a sentence about the DRUG "
                                     "rather than about the L3 mutant, whose experiment belongs "
                                     "to ARO:3005081 (#382)."}])},
            {"subject": "drug_binding", "object": "ptc",
             "predicate": "has part (the site it binds)", "predicate_id": "BFO:0000051",
             "requires": {"drug0": "ARO:3000670"},
             "evidence": [{"reference": "PMID:15554968", "snippet": _PLEURO_SITE,
                           "notes": "The site half of the same binding state."}]},
            {"subject": "determinant", "object": "altered_conformation",
             "predicate": "causally upstream of (the substitution alters the conformation)",
             "predicate_id": "RO:0002411",
             "description": "The in-trans step: a protein substitution changes the shape of the "
                            "RNA that forms the drug's site.",
             "evidence": [{"reference": card_ref, "snippet": card_snippet,
                           "notes": "CARD's own words -- 'interfering with local rRNA "
                                    "conformation' / 'interfere with the rRNA conformation at "
                                    "the active site'."}]},
            {"subject": "altered_conformation", "object": "rrna23s",
             "predicate": "characteristic of (a conformation of the 23S rRNA)",
             "predicate_id": "RO:0000052",
             "description": "Which molecule's conformation it is -- the fact that made this an "
                            "IN-TRANS mechanism.",
             "evidence": [{"reference": card_ref, "snippet": card_snippet,
                           "notes": "'the rRNA conformation'."}]},
            {"subject": "altered_conformation", "object": "drug_binding",
             "predicate": "negatively regulates (the altered site binds the drug less well)",
             "predicate_id": "RO:0002212",
             "requires": {"drug0": "ARO:3000670"},   # #386: guard everything touching this node
             "evidence": [{"reference": "PMID:12936991", "snippet": _TIAMULIN_INFERRED,
                           "notes": "'causes tiamulin resistance by ALTERATION OF THE "
                                    "DRUG-BINDING SITE' -- quoted with its 'It is inferred' "
                                    "hedge intact."}]},
            {"subject": "determinant", "object": "drug_binding",
             "predicate": "negatively regulates (mutation reduces drug binding)",
             "predicate_id": "RO:0002212",
             "requires": {"drug0": "ARO:3000670"},
             "description": "The causal core.",
             # #382: BOTH Bosling sentences name L3, so on a record that names no protein
             # they are the child term's evidence. The first fix removed one of five uses,
             # from det_res only, and a node description was added claiming all were gone.
             "evidence": [
                 {"reference": "PMID:12936991", "snippet": _TIAMULIN_FOOTPRINT,
                  "notes": "Measured, not inferred: chemical footprinting."},
                 {"reference": "PMID:12936991", "snippet": _TIAMULIN_INFERRED,
                  "notes": "The mechanism sentence, and the paper hedges the INFERENCE itself "
                           "-- 'It is INFERRED that the L3 mutation ... causes tiamulin "
                           "resistance by alteration of the drug-binding site.' Quoted with "
                           "the hedge rather than around it."},
             ]},
            {"subject": "drug_binding", "object": "peptide_bond",
             "predicate": "negatively regulates (bound drug blocks peptide bond formation)",
             "predicate_id": "RO:0002212",
             "requires": {"drug0": "ARO:3000670"},   # #386
             "description": "Why losing the binding rescues the cell: the binding is what stops "
                            "translation.",
             "evidence": [{"reference": "PMID:15554968", "snippet": _PLEURO_INHIBITS,
                           "notes": "'Thereby, tiamulin directly inhibits peptide bond "
                                    "formation.'"}]},
        ],
    }


def _ul3_named():
    """ARO:3005081 and anything else whose own definition names uL3/L3."""
    cfg = _ul3_shared(_CARD_UL3, "ARO:3005081", names_l3=True)
    cfg["precondition"] = _requires_named_l3
    # #375: the negative result that settles WHICH molecule is the determinant. It is on the
    # named record only -- it is an L3 experiment (#374) -- and it was quoted as this round's
    # headline finding while appearing in no record at all until review said so.
    for e in cfg["extra_edges"]:
        if e["subject"] == "determinant" and e["object"] == "altered_conformation":
            e["evidence"] = e["evidence"] + [
                {"reference": "PMID:12936991", "snippet": _TIAMULIN_NOT_RRNA,
                 "notes": "The negative result that makes this IN TRANS rather than a plain "
                          "target alteration: rRNA mutations were NOT selected, so the protein "
                          "is the determinant even though the drug binds the RNA."}]
    cfg["note"] = ("uL3 -- target alteration IN TRANS on the large subunit, the same shape "
                   "round 121 named for rpsL and the first family whose primary paper states "
                   "it outright. The record names the protein, so the L3 KB trait is used.")
    cfg["protein_traits"] = {
        "primary_key": "family",
        "family": ("Pfam:PF00297", "Ribosomal protein L3", "DOMAIN", _L3_HEDGE),
        "part_pred": "part of (the L3 family assignment of this determinant)",
        "part_note": ("KB trait: the L3 family. Its abstract names uL3 (#196) AND hedges the "
                      "PTC claim -- 'MAY PARTICIPATE in the formation of the peptidyltransferase "
                      "centre' -- which is quoted with the hedge, not around it."),
    }
    return cfg


def _ul3_unnamed():
    """ARO:3005082, which says only "Ribosomal protein mutations" and names no protein.

    No `protein_traits`. Asserting the L3 family here would borrow the child term's
    specificity for a parent that does not state it -- #371 exactly.
    """
    cfg = _ul3_shared(_CARD_RPMUT, "ARO:3005082", names_l3=False)
    # #387: #382 correctly withheld Bosling's L3 result from this record and left the two
    # edges that rested on it, so they fell back to CARD's sentence -- which says nothing
    # about the drug, about binding, or about any decrease. The edges go, not their evidence.
    # ARO:3003419 in this same round gets exactly this treatment from a definition of the
    # same shape ("...affect the higher-order structure of 16S rRNA and confer antibiotic
    # resistance"): no drug-binding arm, because the record names no drug interaction.
    cfg["extra_edges"] = [e for e in cfg["extra_edges"] if e["object"] != "drug_binding"]
    # `drug_binding` KEEPS its outgoing edges -- the drug-action arm is drug-class-general
    # and CARD-independent -- so it is not pruned. What must change is its DESCRIPTION,
    # which `_ul3_shared` writes as "the interaction the mutation reduces": a claim this
    # record refuses, since #387 removed both edges that said so.
    #
    # The first version pruned on subjects UNION objects, which is a no-op for a node that
    # survives as a subject (#406). Prune on INCOMING edges, which is the orphan shape.
    for n in cfg["extra_nodes"]:
        if n["node_id"] == "drug_binding":
            n["description"] = (
                "The drug-ribosome interaction. On THIS record nothing connects the "
                "substitution to it: CARD names no drug interaction here, so #387 removed "
                "both edges that asserted the mutation affected it. The uL3 record "
                "ARO:3005081 keeps those edges and the stronger wording (#406).")
    incoming = {e["object"] for e in cfg["extra_edges"]}
    outgoing = {e["subject"] for e in cfg["extra_edges"]}
    cfg["extra_nodes"] = [n for n in cfg["extra_nodes"]
                          if n["node_id"] in incoming or n["node_id"] in outgoing]
    cfg["note"] = ("Ribosomal protein mutation (generic) -- target alteration IN TRANS. NO "
                   "protein-trait node: CARD names no protein here, and taking uL3 from the "
                   "child term ARO:3005081 would be #371's borrowed specificity.")
    # NO extra "correlated with" edge on the determinant->rrna23s pair. It asserted and
    # declined to assert the same relation from the same sentence (#380), and the limitation
    # it meant to record -- CARD names no protein -- is a property of the NODE, not of any
    # relation, so no edge on that pair could carry it. It goes on the node instead.
    cfg["determinant_note"] = (
        "CARD names no specific ribosomal protein on this record. The uL3 identity, its "
        "Pfam:PF00297 family node and Bosling 2003's L3 experiments all belong to the child "
        "term ARO:3005081 and are deliberately absent here (#371, #374, #380).")
    return cfg


def _requires_named_l3(ident, label, text):
    """Does the record's OWN definition name L3/uL3?

    Reads only the record's own `definition:` -- the #252 lesson, since the ARO drug-class
    boilerplate mentions plenty of other proteins.
    """
    own = _own_definition(text).lower()
    if re.search(r"\bu?l3\b", own):
        return None
    return "own definition names no specific ribosomal protein, so the L3 KB trait is not licensed (#371)"


FAMILY_SNIPPETS["ARO:3005082"] = [_ul3_named(), _ul3_unnamed()]


# rpsL, drug-agnostic (ARO:3003419). Same first two sentences as ARO:3003395, and then it
# STOPS: "confer antibiotic resistance", where the drug-specific record says "confer
# streptomycin resistance BY DISRUPTING INTERACTIONS between 16S rRNA and streptomycin".
# The disruption mechanism is absent, so the strep_binding arm is absent -- the round-120
# FrxA/nfsB finding on a pair that differs by one clause of one sentence.
_CARD_RPSL_GENERIC = "Ribosomal protein S12 stabilizes the highly conserved pseudoknot structure formed by 16S rRNA. Amino acid substitutions in RpsL affect the higher-order structure of 16S rRNA and confer antibiotic resistance."

def _rpsl_generic_precondition(ident, label, text):
    """Refuse the drug-specific descendant.

    ARO:3003395 is under ARO:3003419 and has its own, STRICTLY STRONGER config (round 121:
    the strep_binding arm this one deliberately omits). Without this, a routine
    `--family ARO:3003419 --repromote --apply` silently replaces that graph with this
    weaker one -- data loss, not a rewrite -- and #280's blast-radius guard cannot fire
    because it refuses only above max(25, 5 * n_draft) and this family has two records
    (#381).
    """
    if ident == "ARO:3003395":
        return ("ARO:3003395 has its own drug-specific config, which asserts strictly more "
                "than this one; re-promoting it here would downgrade it (#381)")
    return _requires_mech("ARO:3000212", "mutation")(ident, label, text)


FAMILY_SNIPPETS["ARO:3003419"] = {
    "curated": "2026-08-10T00:00:00Z",
    "precondition": _rpsl_generic_precondition,
    "reference": "ARO:3003419",
    "mech": {"ARO:3000212": _CARD_RPSL_GENERIC},
    "mech_res": _CARD_RPSL_GENERIC,
    "det_res": [
        {"reference": "ARO:3003419", "snippet": _CARD_RPSL_GENERIC,
         "notes": "CARD states conferral, so CARD carries this edge (#363)."},
        {"reference": "PMID:7934937", "snippet": _RPSL_MUTATIONS,
         "notes": "Finken 1993, what the substitutions ARE."},
    ],
    "res_drug": _CARD_RPSL_GENERIC,
    "note": ("rpsL, drug-agnostic. Its definition ends at 'confer antibiotic resistance' "
             "where ARO:3003395 continues 'by disrupting interactions between 16S rRNA and "
             "streptomycin'. NO drug-binding arm is written, because this record names no "
             "drug interaction to disrupt -- see the test that pins the difference."),
    "protein_traits": {
        "primary_key": "domain",
        "domain": ("Pfam:PF00164", "Ribosomal protein S12/S23", "DOMAIN",
                   "Ribosomal protein uS12 is one of the proteins from the small ribosomal subunit. In Escherichia coli, uS12 is known to be involved in the translation initiation step."),
        "part_pred": "part of (the S12 domain of this determinant)",
        "part_note": "KB trait: the S12 domain, as on ARO:3003395.",
    },
    "extra_nodes": [
        {"node_id": "rrna16s", "label": "16S ribosomal RNA", "node_type": "NUCLEIC_ACID",
         "description": "Ungrounded: SO:0000407, recalled as 16S rRNA, is `cytosolic_18S_rRNA` (#346)."},
        {"node_id": "pseudoknot", "label": "16S rRNA pseudoknot structure", "node_type": "STATE",
         "description": "Ungrounded: SO:0005836, recalled as pseudoknot, is `regulatory_region` (#346)."},
        {"node_id": "altered_structure",
         "label": "altered higher-order structure of the 16S rRNA", "node_type": "STATE",
         "description": "What the substitution produces, as a STATE rather than the molecule "
                        "itself (#377)."},
    ],
    "extra_edges": [
        {"subject": "pseudoknot", "object": "rrna16s",
         "predicate": "part of (a structure of the 16S rRNA)", "predicate_id": "BFO:0000050",
         "evidence": [{"reference": "PMID:7934937", "snippet": _RPSL_PSEUDOKNOT,
                       "notes": "'a pseudoknot structure in a region' of the 16S rRNA."}]},
        {"subject": "altered_structure", "object": "rrna16s",
         "predicate": "characteristic of (a structure of the 16S rRNA)",
         "predicate_id": "RO:0000052",
         "description": "A conformation INHERES IN a molecule; it is not a mereological part "
                        "of one. BFO:0000050 was used here until review noted the snippet's "
                        "genitive -- 'the higher-order structure OF 16S rRNA' -- is the "
                        "inherence reading (#384).",
         "evidence": [{"reference": "ARO:3003419", "snippet": _CARD_RPSL_GENERIC,
                       "notes": "'the higher-order structure OF 16S rRNA'."}]},
        {"subject": "determinant", "object": "pseudoknot",
         "predicate": "correlated with (linked to the pseudoknot region)",
         "predicate_id": "RO:0002610",
         "description": "Same treatment as ARO:3003395: CARD says S12 'stabilizes', its source "
                        "says the region 'has been linked to' S12, and the edge follows the "
                        "source on the one claim they disagree about.",
         "evidence": [{"reference": "PMID:7934937", "snippet": _RPSL_PSEUDOKNOT,
                       "notes": "'has been linked to ribosomal S12 protein' -- hedged."},
                      {"reference": "ARO:3003419", "snippet": _CARD_RPSL_GENERIC,
                       "notes": "CARD's stronger 'stabilizes', recorded so the gap is on the "
                                "edge."}]},
        {"subject": "determinant", "object": "altered_structure",
         "predicate": "causally upstream of (substitution alters the higher-order structure)",
         "predicate_id": "RO:0002411",
         "description": "The furthest this record's own definition goes. ARO:3003395 continues "
                        "to the drug interaction; this one does not, and no drug-binding node "
                        "is written. The object is the CONFORMATION, not the molecule: "
                        "'affects the higher-order structure' does not say the rRNA's function "
                        "is decreased (#377). A STATE object is fine -- round 121's ARO:3003395 "
                        "uses one. That is a CORPUS convention, not something RO licenses: "
                        "RO:0002212 reads 'decreases the rate or magnitude of EXECUTION of q' "
                        "(#385, #388).",
         "evidence": [{"reference": "ARO:3003419", "snippet": _CARD_RPSL_GENERIC,
                       "notes": "'substitutions in RpsL AFFECT THE HIGHER-ORDER STRUCTURE of "
                                "16S rRNA and confer antibiotic resistance'. NOT asserted: any "
                                "disruption of a drug-rRNA interaction, which this definition "
                                "-- unlike ARO:3003395's -- does not mention."}]},
    ],
}


# ---------------------------------------------------------------------------------------
# Round 123 — nat, and the "mismatch" that was not one.
#
# The first draft of this round asserted that ARO:3000212 ("mutation conferring antibiotic
# resistance") disagreed with nat's definition, which names OVEREXPRESSION. Reading
# ARO:3000212's OWN definition settles it against that reading:
#
#   "Point mutations in the DNA may lead to an altered gene product ... Examples included
#    modified antibiotic targets with lower binding affinities and the deactivation of
#    repressors that result in INCREASED EXPRESSION of genes that inactivate or pump out
#    antibiotics."
#
# The mechanism term explicitly covers the increased-expression route. There is no mismatch,
# and #393 is corrected rather than curated around. This is round 51's lesson yet again:
# before building on a claim about a source, read what the source says.
#
# TWO configs, because the two records say different things (#395):
#   ARO:3004930 -- "Mutations that occur in nat WHICH THROUGH OVEREXPRESSION of the enzyme
#                   can result in ... resistance". CARD JOINS the two, so the graph can too.
#   ARO:3004910 -- names overexpression and mutation separately and never joins them.
_CARD_NAT = "Arylamine N-acetyltransferase catalyzes the transfer of the acetyl group from acetyl coenzyme A to the free amino group of arylamines and hydrazines. Reports have shown that overexpression of this enzyme may be responsible for increased resistance to isoniazid."
_CARD_NAT_MUT = "Mutations that occur in nat which through overexpression of the enzyme can result in or contribute to antibiotic resistance to isoniazid."
_MECH_MUTATION = "Point mutations in the DNA may lead to an altered gene product that may result in antibiotic resistance. Examples included modified antibiotic targets with lower binding affinities and the deactivation of repressors that result in increased expression of genes that inactivate or pump out antibiotics."
_NAT_PFAM = "Arylamine N-acetyltransferase (NAT) facilitates the transfer of an acetyl group from acetyl coenzyme A on to a wide range of arylamine, N-hydroxyarylamines and hydrazines. Acetylation of these compounds generally results in inactivation."


def _nat_config(card_ref, card_snippet, joins_mutation):
    """nat's graph. `joins_mutation` is true only where CARD itself joins the two routes."""
    cfg = {
        "curated": "2026-08-10T00:00:00Z",
        "reference": card_ref,
        # #400: the LIST form, so the reference travels with the snippet. Giving `mech`
        # a bare string makes the promoter stamp cfg["reference"] on it -- which put
        # ARO:3000212's definition under `reference: ARO:3004910` in the first fix for
        # #398. The snippet moved; the attribution did not.
        "mech": {"ARO:3000212": [
            {"reference": "ARO:3000212", "snippet": _MECH_MUTATION,
             "notes": "The mechanism term's own definition, which names both point mutations "
                      "and 'increased expression' among its examples (#393, corrected)."}]},
        "mech_res": [
            {"reference": "ARO:3000212", "snippet": _MECH_MUTATION,
             "notes": "ARO:3000212's own definition states that such mutations 'may result in "
                      "antibiotic resistance'."}],
        "det_res": [
            {"reference": card_ref, "snippet": card_snippet,
             "notes": ("Quoted whole because the qualifications are part of the claim."
                       if joins_mutation else
                       "Quoted whole because BOTH qualifications matter: 'REPORTS HAVE SHOWN' "
                       "attributes the claim and 'MAY BE responsible' hedges it.")},
            {"reference": "ARO:3000212", "snippet": _MECH_MUTATION,
             "notes": "The mechanism term's own definition, which names 'increased expression' "
                      "among its examples -- so an overexpression route is IN SCOPE for "
                      "ARO:3000212, not a mismatch with it (#393, corrected)."},
        ],
        "res_drug": card_snippet,
        "protein_traits": {
            "primary_key": "family",
            "family": ("Pfam:PF00797", "N-acetyltransferase", "DOMAIN", _NAT_PFAM),
            "part_pred": "part of (the N-acetyltransferase family assignment)",
            "part_note": "KB trait: the NAT family. Its abstract names arylamine "
                         "N-acetyltransferase itself (#196).",
        },
        "extra_nodes": [
            {"node_id": "acetylation", "label": "arylamine N-acetyltransferase activity",
             "node_type": "MOLECULAR_FUNCTION", "grounding": "GO:0004060",
             "description": "The EXACT term, and a KB record. GO:0008080 "
                            "(N-acetyltransferase activity) was used until review noted its "
                            "definition never names acetyl-CoA and its scope includes histone "
                            "and rRNA acetyltransferases (#399)."},
            {"node_id": "acetyl_coa", "label": "acetyl-CoA", "node_type": "CHEMICAL",
             "grounding": "CHEBI:15351"},
            {"node_id": "overexpression", "label": "overexpression of the enzyme",
             "node_type": "STATE",
             "description": "The route CARD names."},
        ],
        "extra_edges": [
            {"subject": "determinant", "object": "acetylation",
             "predicate": "enables (arylamine N-acetyltransferase activity)",
             "predicate_id": "RO:0002327",
             "evidence": [{"reference": card_ref, "snippet": card_snippet,
                           "notes": "The enzyme's identity."}
                          if not joins_mutation else
                          {"reference": "Pfam:PF00797", "snippet": _NAT_PFAM,
                           "notes": "KB trait: what an arylamine N-acetyltransferase does. "
                                    "This record's own definition gives the resistance route "
                                    "but not the chemistry."}]},
            {"subject": "acetylation", "object": "acetyl_coa",
             "predicate": "has input (the acetyl donor)", "predicate_id": "RO:0002233",
             "evidence": [{"reference": "Pfam:PF00797", "snippet": _NAT_PFAM,
                           "notes": "'transfer of an acetyl group from acetyl coenzyme A'."}]},
            {"subject": "overexpression", "object": "resistance",
             "predicate": ("causally upstream of (via overexpression)" if joins_mutation
                           else "correlated with (reported, and hedged)"),
             "predicate_id": "RO:0002411" if joins_mutation else "RO:0002610",
             "description": ("CARD joins the mutation and the overexpression on this record, "
                             "so the causal predicate is the source's own."
                             if joins_mutation else
                             "Deliberately weak, and twice over: the claim is ATTRIBUTED "
                             "('Reports have shown') and then HEDGED ('may be responsible')."),
             "evidence": [{"reference": card_ref, "snippet": card_snippet,
                           "notes": ("'can result in or contribute to antibiotic resistance'."
                                     if joins_mutation else
                                     "Both qualifications are in the quoted sentence rather "
                                     "than paraphrased away.")}]},
        ],
    }
    if joins_mutation:
        # #397: the only edge that says what PRODUCES the overexpression, and it exists
        # solely because this record's own definition supplies it. The parent's does not,
        # so the parent's `overexpression` node has no incoming edge and gets none invented.
        cfg["extra_edges"].insert(0, {
            "subject": "determinant", "object": "overexpression",
            "predicate": "causally upstream of (the mutation raises expression)",
            "predicate_id": "RO:0002411",
            "description": "This record's own definition JOINS the two routes; the parent's "
                           "does not (#395).",
            "evidence": [{"reference": card_ref, "snippet": card_snippet,
                          "notes": "'Mutations that occur in nat WHICH THROUGH OVEREXPRESSION "
                                   "of the enzyme can result in ... resistance'."}]})
        cfg["note"] = ("nat (mutation record) -- CARD joins the mutation to the overexpression "
                       "on THIS record, so the graph does too. NOT asserted: that isoniazid is "
                       "the enzyme's substrate; CARD names no substrate here at all.")
    else:
        cfg["precondition"] = _nat_does_not_join
        cfg["determinant_note"] = (
            "CARD names the chemistry and the resistance separately on this record and never "
            "joins them. The mutation->overexpression link belongs to ARO:3004930, whose own "
            "definition supplies it (#395).")
        cfg["note"] = ("nat -- CARD names the chemistry ('arylamines and hydrazines') and, "
                       "separately, that overexpression may confer isoniazid resistance. NOT "
                       "asserted: that isoniazid is the enzyme's substrate. Isoniazid IS a "
                       "hydrazine, so the inference is one step away -- and CARD does not take "
                       "it. The Pfam record makes the link for HUMAN NAT, which is not "
                       "evidence about this organism and carries no edge of its own (#396).")
    return cfg


def _nat_does_not_join(ident, label, text):
    """The complement of `_nat_joins_mutation`, so the two configs are DISJOINT (#401).

    Before this, ARO:3004930 passed both preconditions and was selected only because the
    joined config happened to be first in the list -- reordering silently stripped its
    `determinant -> overexpression` edge with every gate green.
    """
    if "through overexpression" in _own_definition(text).lower():
        return ("own definition joins the mutation to the overexpression, so the joined "
                "config serves this record (#401)")
    return _requires_mech("ARO:3000212", "mutation")(ident, label, text)


def _nat_joins_mutation(ident, label, text):
    own = _own_definition(text).lower()
    if "through overexpression" in own:
        return None
    return "own definition does not join the mutation to the overexpression (#395)"


_NAT_JOINED = _nat_config("ARO:3004930", _CARD_NAT_MUT, joins_mutation=True)
_NAT_JOINED["precondition"] = _nat_joins_mutation
FAMILY_SNIPPETS["ARO:3004910"] = [_NAT_JOINED,
                                  _nat_config("ARO:3004910", _CARD_NAT, joins_mutation=False)]

_check_config_order()


if __name__ == "__main__":
    raise SystemExit(main())
