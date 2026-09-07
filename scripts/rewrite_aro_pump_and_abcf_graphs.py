#!/usr/bin/env python3
"""Describe and evidence ABC/MFS efflux and ABC-F protection ARO graphs.

The MFS and ABC efflux records handled here already have the right
domain/fold/efflux shape, but every edge is single-evidenced and lacks a
description. The ABC-F parent is different: CARD explicitly scopes it to
ribosomal protection instead of transport, so this updater rewrites that graph
around ribosome binding and antibiotic displacement.

Dry-run by default; pass ``--apply`` to write.
"""

from __future__ import annotations

import argparse
import copy
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from record_io import append_to_section, replace_block  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ARO_DIR = ROOT / "data" / "traits" / "function" / "resistance" / "aro"

HISTORY_ACTION = "Described ABC/MFS efflux and ABC-F target-protection causal graphs"
HISTORY_CURATOR = "codex-causal-graph-quality"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

ANTIBIOTIC_EFFLUX_EVIDENCE = {
    "reference": "ARO:0010000",
    "snippet": "Antibiotic resistance via the transport of antibiotics out of the cell.",
    "notes": "CARD definition for the antibiotic efflux resistance mechanism.",
}

EFFLUX_PUMP_EVIDENCE = {
    "reference": "ARO:3000159",
    "snippet": "Efflux proteins that pump antibiotic out of a cell to confer resistance.",
    "notes": "CARD definition for efflux pump complexes and subunits.",
}

MFS_EVIDENCE = {
    "reference": "ARO:0010002",
    "snippet": (
        "Directed pumping of antibiotic out of a cell to confer resistance. Major "
        "facilitator superfamily (MFS) transporters and ABC transporters "
        "comprise the two largest and most functionally diverse of the "
        "transporter superfamilies. However, MFS transporters are distinct from "
        "ABC transporters in both their primary sequence and structure and in "
        "the mechanism of energy coupling. As secondary transporters they are, "
        "like RND and SMR transporters, energized by the electrochemical proton "
        "gradient."
    ),
    "notes": "CARD definition for MFS antibiotic efflux pumps.",
}

ABC_EFFLUX_EVIDENCE = {
    "reference": "ARO:0010001",
    "snippet": (
        "Directed pumping of antibiotic out of a cell to confer resistance. "
        "ATP-binding cassette (ABC) transporters are present in all cells of all "
        "organisms and use the energy of ATP binding/hydrolysis to transport "
        "substrates across cell membranes."
    ),
    "notes": "CARD definition for ABC antibiotic efflux pumps.",
}

MFS_TRANSPORT_EVIDENCE = {
    "reference": "PMID:38974671",
    "snippet": (
        "The antimicrobial antiport transport cycle in bacteria is driven by the "
        "ion-motive force, an energy mode associated with changes in transporter "
        "conformations and gating during efflux across the membrane."
    ),
    "notes": "Evidence for ion-motive-force-driven MFS efflux.",
}

ABC_TRANSPORT_EVIDENCE = {
    "reference": "PMID:29892271",
    "snippet": (
        "Tripartite efflux pumps built around ATP-binding cassette (ABC) "
        "transporters are membrane protein machineries that perform vectorial "
        "export of drugs and virulence factors from Gram negative bacteria, "
        "using ATP-hydrolysis as energy source."
    ),
    "notes": "Evidence for ATP-hydrolysis-driven ABC drug efflux.",
}

TARGET_PROTECTION_EVIDENCE = {
    "reference": "ARO:0001003",
    "snippet": (
        "Protection of antibiotic action target from antibiotic binding, which "
        "process will result in antibiotic resistance."
    ),
    "notes": "CARD definition for the antibiotic target protection mechanism.",
}

TARGET_PROTECTION_PARENT_EVIDENCE = {
    "reference": "ARO:3000185",
    "snippet": (
        "These proteins confer antibiotic resistance by bind the antibiotic "
        "target to prevent antibiotic binding."
    ),
    "notes": "CARD definition for antibiotic target protection proteins.",
}

ABC_F_EVIDENCE = {
    "reference": "ARO:3004469",
    "snippet": (
        "ABC-F proteins confer antibiotic resistance via ribosomal protection "
        "and not antibiotic efflux as in other ABC proteins."
    ),
    "notes": "CARD definition for ABC-F ribosomal protection proteins.",
}

ABC_F_DISPLACEMENT_EVIDENCE = {
    "reference": "PMID:27006457",
    "snippet": "such proteins are capable of displacing antibiotic from the ribosome in vitro",
    "notes": "Experimental evidence for ABC-F antibiotic displacement from the ribosome.",
}

GO_RIBOSOME_EVIDENCE = {
    "reference": "GO:0005840",
    "snippet": (
        "It consists of two subunits, one large and one small, each containing "
        "only protein and RNA."
    ),
    "notes": "GO definition for the ribosome.",
}

MFS_DOMAIN_EVIDENCE = {
    "reference": "Pfam:PF07690",
    "snippet": "Major Facilitator Superfamily",
    "notes": "Pfam family for the MFS transporter domain.",
}

MFS_FOLD_EVIDENCE = {
    "reference": "CATH:1.20.1250.20",
    "snippet": "MFS general substrate transporter like domains",
    "notes": "CATH fold for MFS general substrate transporter-like domains.",
}

ABC_DOMAIN_EVIDENCE = {
    "reference": "Pfam:PF00005",
    "snippet": "ABC transporter",
    "notes": "Pfam family for the ABC transporter ATP-binding domain.",
}

ABC_FOLD_EVIDENCE = {
    "reference": "CATH:3.40.50.300",
    "snippet": "P-loop containing nucleotide triphosphate hydrolases",
    "notes": "CATH fold for ABC ATPase domains.",
}

RESISTANCE_NODE = {
    "node_id": "resistance",
    "label": "antibiotic resistance phenotype",
    "node_type": "PHENOTYPE",
    "grounding": "GO:0046677",
    "description": (
        "Resistance phenotype conferred by this determinant. Grounded to the "
        "nearest available superclass: ARO models determinants and mechanisms "
        "but has no term for the resistance phenotype itself."
    ),
}


@dataclass(frozen=True)
class EffluxFamily:
    title: str
    family_evidence: dict[str, str]
    transport_evidence: dict[str, str]
    domain_node: dict[str, str]
    fold_node: dict[str, str]
    domain_evidence: dict[str, str]
    fold_evidence: dict[str, str]
    efflux_predicate: str
    graph_description: str


@dataclass(frozen=True)
class EffluxTarget:
    identifier: str
    filename: str
    determinant_evidence: dict[str, str]
    family: EffluxFamily


@dataclass(frozen=True)
class AbcFTarget:
    identifier: str
    filename: str
    determinant_evidence: dict[str, str]


Target = EffluxTarget | AbcFTarget

MFS_FAMILY = EffluxFamily(
    title="MFS antibiotic efflux",
    family_evidence=MFS_EVIDENCE,
    transport_evidence=MFS_TRANSPORT_EVIDENCE,
    domain_node={
        "node_id": "domain",
        "label": "major facilitator superfamily (MFS) transporter domain",
        "node_type": "DOMAIN",
        "grounding": "Pfam:PF07690",
        "description": "Transporter domain shared by MFS antibiotic efflux pumps.",
    },
    fold_node={
        "node_id": "fold",
        "label": "MFS general substrate transporter fold",
        "node_type": "DOMAIN",
        "grounding": "CATH:1.20.1250.20",
        "description": "Fold adopted by MFS general substrate transporter-like domains.",
    },
    domain_evidence=MFS_DOMAIN_EVIDENCE,
    fold_evidence=MFS_FOLD_EVIDENCE,
    efflux_predicate="enables (ion-motive-force-driven drug efflux)",
    graph_description=(
        "Curated resistance-causation graph for MFS antibiotic efflux pumps. "
        "The determinant enables ion-motive-force-driven export of antibiotics "
        "out of the cell, lowering intracellular drug exposure."
    ),
)

ABC_EFFLUX_FAMILY = EffluxFamily(
    title="ABC antibiotic efflux",
    family_evidence=ABC_EFFLUX_EVIDENCE,
    transport_evidence=ABC_TRANSPORT_EVIDENCE,
    domain_node={
        "node_id": "domain",
        "label": "ABC transporter ATP-binding domain",
        "node_type": "DOMAIN",
        "grounding": "Pfam:PF00005",
        "description": "ATP-binding domain shared by ABC antibiotic efflux pumps.",
    },
    fold_node={
        "node_id": "fold",
        "label": "P-loop NTPase fold (ABC ATPase nucleotide-binding domain)",
        "node_type": "DOMAIN",
        "grounding": "CATH:3.40.50.300",
        "description": "P-loop NTPase fold adopted by ABC ATPase domains.",
    },
    domain_evidence=ABC_DOMAIN_EVIDENCE,
    fold_evidence=ABC_FOLD_EVIDENCE,
    efflux_predicate="enables (ATP-driven drug efflux)",
    graph_description=(
        "Curated resistance-causation graph for ABC antibiotic efflux pumps. "
        "The determinant enables ATP-driven export of antibiotics across the "
        "cell membrane, lowering intracellular drug exposure."
    ),
)

EFFLUX_TARGETS: tuple[EffluxTarget, ...] = (
    EffluxTarget(
        identifier="ARO:3007669",
        filename="aadt-aro3007669.yaml",
        determinant_evidence={
            "reference": "ARO:3007669",
            "snippet": (
                "The AadT pump is a novel multidrug efflux pump from the proton "
                "antiporter 2 (DHA2) family and was discovered in Acinetobacter "
                "multidrug resistance plasmids."
            ),
            "notes": "CARD definition for aadT.",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3003942",
        filename="abca-aro3003942.yaml",
        determinant_evidence={
            "reference": "ARO:3003942",
            "snippet": (
                "AbcA is a multidrug resistant ABC transporter that confers "
                "resistance to methicillin, daptomycin, cefotaxime, and moenomycin."
            ),
            "notes": "CARD definition for abcA.",
        },
        family=ABC_EFFLUX_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3004573",
        filename="acinetobacter-baumannii-abaf-aro3004573.yaml",
        determinant_evidence={
            "reference": "ARO:3004573",
            "snippet": "Expression of abaF in E. coli resulted in increased resistance to fosfomycin.",
            "notes": "CARD definition for Acinetobacter baumannii AbaF.",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3004577",
        filename="acinetobacter-baumannii-amva-aro3004577.yaml",
        determinant_evidence={
            "reference": "ARO:3004577",
            "snippet": (
                "AmvA has 14 alpha-helical transmembrane segments, qualifying it "
                "as a member of the DHA2 transporter family of the major "
                "facilitator superfamily (MFS)."
            ),
            "notes": "CARD definition for Acinetobacter baumannii AmvA.",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:0010001",
        filename="atp-binding-cassette-abc-antibiotic-efflux-pump-aro0010001.yaml",
        determinant_evidence=ABC_EFFLUX_EVIDENCE,
        family=ABC_EFFLUX_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:0010002",
        filename="major-facilitator-superfamily-mfs-antibiotic-efflux-pump-aro0010002.yaml",
        determinant_evidence=MFS_EVIDENCE,
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3002987",
        filename="bcra-aro3002987.yaml",
        determinant_evidence={
            "reference": "ARO:3002987",
            "snippet": (
                "bcrA is an ABC transporter found in Bacillus licheniformis "
                "that confers bacitracin resistance."
            ),
            "notes": "CARD definition for bcrA.",
        },
        family=ABC_EFFLUX_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3002988",
        filename="bcrb-aro3002988.yaml",
        determinant_evidence={
            "reference": "ARO:3002988",
            "snippet": (
                "bcrB is an ABC transporter found in Bacillus licheniformis "
                "that confers bacitracin resistance."
            ),
            "notes": "CARD definition for bcrB.",
        },
        family=ABC_EFFLUX_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3003947",
        filename="efrab-aro3003947.yaml",
        determinant_evidence={
            "reference": "ARO:3003947",
            "snippet": (
                "EfrAB is a heterodimeric ABC transporter efflux pump found in "
                "Enterococcus faecalis and Enterococcus faecium that confers "
                "resistance to ciprofloxacin, erythromycin, rifampicin, "
                "quinupristine."
            ),
            "notes": "CARD definition for EfrAB.",
        },
        family=ABC_EFFLUX_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3007553",
        filename="candida-spp-cdr1-aro3007553.yaml",
        determinant_evidence={
            "reference": "ARO:3007553",
            "snippet": (
                "CDR1 is a pleiotropic drug resistance gene encoding ABC "
                "transporters that contributes to multidrug antifungal "
                "resistance in Candida spp."
            ),
            "notes": "CARD definition for Candida spp. CDR1.",
        },
        family=ABC_EFFLUX_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3007554",
        filename="candida-spp-cdr2-aro3007554.yaml",
        determinant_evidence={
            "reference": "ARO:3007554",
            "snippet": (
                "CDR2 is a Pleiotropic drug resistance gene encoding ABC "
                "transporters that contributes to multidrug antifungal "
                "resistance in Candida spp."
            ),
            "notes": "CARD definition for Candida spp. CDR2.",
        },
        family=ABC_EFFLUX_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3007566",
        filename="cryptococcus-spp-afr1-aro3007566.yaml",
        determinant_evidence={
            "reference": "ARO:3007566",
            "snippet": (
                "Cryptococcus spp. AFR1 gene is an ABC transporter gene that "
                "contributes to antifungal resistance through antibiotic efflux."
            ),
            "notes": "CARD definition for Cryptococcus spp. AFR1.",
        },
        family=ABC_EFFLUX_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3003801",
        filename="bcr-1-aro3003801.yaml",
        determinant_evidence={
            "reference": "ARO:3003801",
            "snippet": (
                "Transmembrane protein which expels bicyclomycin from the "
                "cell, leading to bicyclomycin resistance."
            ),
            "notes": "CARD definition for bcr-1.",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3002693",
        filename="cmla1-aro3002693.yaml",
        determinant_evidence={
            "reference": "ARO:3002693",
            "snippet": (
                "cmlA1 is a plasmid or transposon-encoded chloramphenicol "
                "exporter that is found in Pseudomonas aeruginosa and "
                "Klebsiella pneumoniae."
            ),
            "notes": "CARD definition for cmlA1.",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3002695",
        filename="cmla5-aro3002695.yaml",
        determinant_evidence={
            "reference": "ARO:3002695",
            "snippet": (
                "cmlA5 is a plasmid or transposon-encoded chloramphenicol "
                "exporter that is found in Escherichia coli."
            ),
            "notes": "CARD definition for cmlA5.",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3002696",
        filename="cmla6-aro3002696.yaml",
        determinant_evidence={
            "reference": "ARO:3002696",
            "snippet": (
                "cmlA6 is a plasmid-encoded chloramphenicol exporter that is "
                "found in Pseudomonas aeruginosa."
            ),
            "notes": "CARD definition for cmlA6.",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3004665",
        filename="cmla8-aro3004665.yaml",
        determinant_evidence={
            "reference": "ARO:3004665",
            "snippet": "cmlA8 is a plasmid that confers resistance to chloramphenicol.",
            "notes": "CARD definition for cmlA8.",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3005043",
        filename="cmla9-aro3005043.yaml",
        determinant_evidence={
            "reference": "ARO:3005043",
            "snippet": (
                "cmlA9 is a Major Facilitator Superfamily efflux gene that is "
                "found in Salmonella enterica."
            ),
            "notes": "CARD definition for cmlA9.",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3002698",
        filename="cmlb-aro3002698.yaml",
        determinant_evidence={
            "reference": "ARO:3002698",
            "snippet": (
                "cmlB is a plasmid-encoded chloramphenicol exporter that is "
                "found in Klebsiella aerogenes."
            ),
            "notes": "CARD definition for cmlB.",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3002699",
        filename="cmlb1-aro3002699.yaml",
        determinant_evidence={
            "reference": "ARO:3002699",
            "snippet": (
                "cmlB1 is a plasmid-encoded chloramphenicol exporter that is "
                "found in Bordetella bronchiseptica."
            ),
            "notes": "CARD definition for cmlB1.",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3002702",
        filename="cmra-aro3002702.yaml",
        determinant_evidence={
            "reference": "ARO:3002702",
            "snippet": (
                "cmrA is a transposon-encoded chloramphenicol exporter that is "
                "found in Rhodococcus rhodochrous."
            ),
            "notes": "CARD definition for cmrA.",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3002703",
        filename="cmx-aro3002703.yaml",
        determinant_evidence={
            "reference": "ARO:3002703",
            "snippet": (
                "cmx is a plasmid or transposon-encoded chloramphenicol "
                "exporter that is found in Corynebacterium striatum and "
                "Pseudomonas aeruginosa."
            ),
            "notes": "CARD definition for cmx.",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3002704",
        filename="fexa-aro3002704.yaml",
        determinant_evidence={
            "reference": "ARO:3002704",
            "snippet": (
                "fexA is a plasmid-encoded chloramphenicol exporter that is "
                "found in Mammaliicoccus lentus."
            ),
            "notes": "CARD definition for fexA.",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3003955",
        filename="efpa-aro3003955.yaml",
        determinant_evidence={
            "reference": "ARO:3003955",
            "snippet": "efpA is an MFS transporter found in Mycobacterium tuberculosis.",
            "notes": "CARD definition for efpA.",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3000344",
        filename="emrab-tolc-aro3000344.yaml",
        determinant_evidence={
            "reference": "ARO:3000344",
            "snippet": (
                "EmrAB-TolC is a multidrug efflux system found in E. coli. "
                "EmrB is the electrochemical-gradient powered transporter; "
                "EmrA is the linker; and TolC is the outer membrane channel."
            ),
            "notes": "CARD definition for EmrAB-TolC.",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3000373",
        filename="emrky-tolc-aro3000373.yaml",
        determinant_evidence={
            "reference": "ARO:3000373",
            "snippet": (
                "EmrKY is a homolog of EmrAB found in E. coli. Together with "
                "TolC, it is a tripartite multidrug transporter."
            ),
            "notes": "CARD definition for EmrKY-TolC.",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3001313",
        filename="fact-aro3001313.yaml",
        determinant_evidence={
            "reference": "ARO:3001313",
            "snippet": "Efflux protein facT confers resistance to factumycin.",
            "notes": "CARD definition for facT.",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3003960",
        filename="farab-aro3003960.yaml",
        determinant_evidence={
            "reference": "ARO:3003960",
            "snippet": (
                "farAB is an MFS efflux pump found in gonococci that is "
                "involved in antibacterial fatty acid resistance."
            ),
            "notes": "CARD definition for farAB.",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3007019",
        filename="fexb-aro3007019.yaml",
        determinant_evidence={
            "reference": "ARO:3007019",
            "snippet": "FexB is a plasmid-encoded exporter gene which confers resistance to florfenicol.",
            "notes": "CARD definition for fexB.",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3003963",
        filename="flo-aro3003963.yaml",
        determinant_evidence={
            "reference": "ARO:3003963",
            "snippet": (
                "The Flo transporters can be plasmid- or chromosome-encoded "
                "and are important determinants of florfenicol resistance."
            ),
            "notes": "CARD definition for flo.",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3002705",
        filename="flor-aro3002705.yaml",
        determinant_evidence={
            "reference": "ARO:3002705",
            "snippet": (
                "floR is a plasmid or chromosome-encoded chloramphenicol "
                "exporter."
            ),
            "notes": "CARD definition for floR.",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3007061",
        filename="hp1165-aro3007061.yaml",
        determinant_evidence={
            "reference": "ARO:3007061",
            "snippet": (
                "Hp1165 is a homolog of the Clostridium perfringes tetP gene "
                "and is part of the MFS efflux family."
            ),
            "notes": "CARD definition for hp1165.",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3003964",
        filename="hp1181-aro3003964.yaml",
        determinant_evidence={
            "reference": "ARO:3003964",
            "snippet": (
                "hp1181 is a translocase that is part of the MFS efflux pump "
                "family and has a role in active antibiotic efflux."
            ),
            "notes": "CARD definition for hp1181.",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3002813",
        filename="lmrb-aro3002813.yaml",
        determinant_evidence={
            "reference": "ARO:3002813",
            "snippet": (
                "lmrB is a chromosomally-encoded efflux pump that confers "
                "resistance to lincosamides in Bacillus subtilis."
            ),
            "notes": "CARD definition for lmrB.",
        },
        family=ABC_EFFLUX_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3000545",
        filename="macab-tolc-aro3000545.yaml",
        determinant_evidence={
            "reference": "ARO:3000545",
            "snippet": (
                "MacAB-TolC is an ABC efflux pump complex expressed in E. coli "
                "and Salmonella enterica."
            ),
            "notes": "CARD definition for MacAB-TolC.",
        },
        family=ABC_EFFLUX_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3007011",
        filename="mdea-aro3007011.yaml",
        determinant_evidence={
            "reference": "ARO:3007011",
            "snippet": (
                "mdeA is a multidrug efflux pump that confers resistance in "
                "varying degrees to several unrelated antibiotics."
            ),
            "notes": "CARD definition for mdeA.",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3001329",
        filename="mdtg-aro3001329.yaml",
        determinant_evidence={
            "reference": "ARO:3001329",
            "snippet": (
                "The MdtG protein, also named YceE, appears to be a member of "
                "the major facilitator superfamily of transporters."
            ),
            "notes": "CARD definition for mdtG.",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3001216",
        filename="mdth-aro3001216.yaml",
        determinant_evidence={
            "reference": "ARO:3001216",
            "snippet": "Multidrug resistance protein MdtH.",
            "notes": "CARD definition for mdtH.",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3001214",
        filename="mdtm-aro3001214.yaml",
        determinant_evidence={
            "reference": "ARO:3001214",
            "snippet": "Multidrug resistance protein MdtM.",
            "notes": "CARD definition for mdtM.",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3004101",
        filename="mdtnop-aro3004101.yaml",
        determinant_evidence={
            "reference": "ARO:3004101",
            "snippet": "MdtNOP is a MFS efflux pump protein found in E. coli.",
            "notes": "CARD definition for MdtNOP.",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3003950",
        filename="msba-aro3003950.yaml",
        determinant_evidence={
            "reference": "ARO:3003950",
            "snippet": (
                "MsbA is a multidrug resistance transporter homolog from E. coli "
                "and belongs to a superfamily of ABC transporters."
            ),
            "notes": "CARD definition for msbA.",
        },
        family=ABC_EFFLUX_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3000391",
        filename="nora-aro3000391.yaml",
        determinant_evidence={
            "reference": "ARO:3000391",
            "snippet": (
                "NorA is a multidrug efflux pump in Staphylococcus aureus that "
                "confers resistance to fluoroquinolones and other structurally "
                "unrelated antibiotics like acriflavine."
            ),
            "notes": "CARD definition for norA.",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3000421",
        filename="norb-aro3000421.yaml",
        determinant_evidence={
            "reference": "ARO:3000421",
            "snippet": (
                "NorB is a multidrug efflux pump in Staphylococcus aureus that "
                "confers resistance to fluoroquinolones and other structurally "
                "unrelated antibiotics like tetracycline."
            ),
            "notes": "CARD definition for norB.",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3007010",
        filename="norc-aro3007010.yaml",
        determinant_evidence={
            "reference": "ARO:3007010",
            "snippet": (
                "NorC is a multidrug efflux pump in Staphylococcus aureus that "
                "confers resistance to fluoroquinolones and other structurally "
                "unrelated antibiotics like tetracycline."
            ),
            "notes": "CARD definition for norC.",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3002522",
        filename="nova-aro3002522.yaml",
        determinant_evidence={
            "reference": "ARO:3002522",
            "snippet": (
                "A type III ABC transporter, identified on the novobiocin "
                "biosynthetic gene cluster, involved in the transport and "
                "resistance of novobiocin."
            ),
            "notes": "CARD definition for novA.",
        },
        family=ABC_EFFLUX_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3003748",
        filename="olec-aro3003748.yaml",
        determinant_evidence={
            "reference": "ARO:3003748",
            "snippet": (
                "oleC is an ABC transporter isolated from Streptomyces "
                "antibioticus and is involved in oleandomycin secretion."
            ),
            "notes": "CARD definition for oleC.",
        },
        family=ABC_EFFLUX_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3002892",
        filename="otr-b-aro3002892.yaml",
        determinant_evidence={
            "reference": "ARO:3002892",
            "snippet": (
                "otr(B) is a tetracycline resistance efflux pump found in "
                "Streptomyces rimosus."
            ),
            "notes": "CARD definition for otr(B).",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3002894",
        filename="otr-c-aro3002894.yaml",
        determinant_evidence={
            "reference": "ARO:3002894",
            "snippet": (
                "otr(C) is a tetracycline resistance efflux pump found in "
                "Streptomyces rimosus."
            ),
            "notes": "CARD definition for otr(C).",
        },
        family=ABC_EFFLUX_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3000769",
        filename="pata-patb-aro3000769.yaml",
        determinant_evidence={
            "reference": "ARO:3000769",
            "snippet": (
                "PatA-PatB is an efflux protein complex that is associated with "
                "fluoroquinolone resistance in Streptococcus pneumoniae."
            ),
            "notes": "CARD definition for PatA-PatB.",
        },
        family=ABC_EFFLUX_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3004666",
        filename="pexa-aro3004666.yaml",
        determinant_evidence={
            "reference": "ARO:3004666",
            "snippet": (
                "pexA is a florfenicol and chloramphenicol resistance gene "
                "discovered in Alaskan soil."
            ),
            "notes": "CARD definition for pexA.",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3002812",
        filename="pp-flo-aro3002812.yaml",
        determinant_evidence={
            "reference": "ARO:3002812",
            "snippet": (
                "pp-flo is a plasmid chloramphenicol exporter that is found in "
                "Photobacterium damselae subsp. piscicida."
            ),
            "notes": "CARD definition for pp-flo.",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3000448",
        filename="qepa1-aro3000448.yaml",
        determinant_evidence={
            "reference": "ARO:3000448",
            "snippet": (
                "QepA1 is a plasmid-mediated efflux pump in E. coli, shown to "
                "contribute to fluoroquinolone resistance."
            ),
            "notes": "CARD definition for QepA1.",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3004103",
        filename="qepa2-aro3004103.yaml",
        determinant_evidence={
            "reference": "ARO:3004103",
            "snippet": (
                "QepA2 is a plasmid-mediated quinolone resistance pump found "
                "in an Escherichia coli isolate from France."
            ),
            "notes": "CARD definition for QepA2.",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3002701",
        filename="rhodococcus-fascians-cmr-aro3002701.yaml",
        determinant_evidence={
            "reference": "ARO:3002701",
            "snippet": (
                "cmr is a plasmid-encoded chloramphenicol exporter that is "
                "found in Rhodococcus fascians and Corynebacterium glutamicum."
            ),
            "notes": "CARD definition for Rhodococcus fascians cmr.",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3007662",
        filename="rv1877-aro3007662.yaml",
        determinant_evidence={
            "reference": "ARO:3007662",
            "snippet": (
                "Rv1877, a putative Major Facilitator Superfamily efflux pump "
                "from M. tuberculosis actively effluxes fluoroquinolones "
                "ofloxacin and levofloxacin."
            ),
            "notes": "CARD definition for Rv1877.",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3002691",
        filename="salmonella-enterica-cmla-aro3002691.yaml",
        determinant_evidence={
            "reference": "ARO:3002691",
            "snippet": (
                "cmlA is a plasmid-encoded chloramphenicol exporter that is "
                "found in Salmonella typhimurium."
            ),
            "notes": "CARD definition for Salmonella enterica cmlA.",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3004572",
        filename="staphylococcus-aureus-lmrs-aro3004572.yaml",
        determinant_evidence={
            "reference": "ARO:3004572",
            "snippet": (
                "LmrS has 14 transmembrane helices and, when expressed in "
                "E. coli, is capable of extruding a variety of antibiotics "
                "inclinding linezolid, trimethoprim, florfenicol, "
                "chlorampheniocol, erythromycin, streptomycin, kanamycin, and "
                "fusidic acid."
            ),
            "notes": "CARD definition for Staphylococcus aureus LmrS.",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3004667",
        filename="staphylococcus-aureus-nora-aro3004667.yaml",
        determinant_evidence={
            "reference": "ARO:3004667",
            "snippet": (
                "NorA gene cloned from Staphylococcus aureus conferred "
                "relatively high resistance to hydrophilic quinolones such as "
                "norfloxacin, enoxacin, ofloxacin, and ciprofloxacin in S. "
                "aureus and Escherichia coli."
            ),
            "notes": "CARD definition for Staphylococcus aureus norA.",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3002690",
        filename="streptomyces-lividans-cmlr-aro3002690.yaml",
        determinant_evidence={
            "reference": "ARO:3002690",
            "snippet": (
                "cmlR is a plasmid or chromosome-encoded chloramphenicol "
                "resistance determinant (putative transmembrane protein) that "
                "is found in Escherichia coli and Streptomyces lividans."
            ),
            "notes": "CARD definition for Streptomyces lividans cmlR.",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3000343",
        filename="tap-aro3000343.yaml",
        determinant_evidence={
            "reference": "ARO:3000343",
            "snippet": (
                "Efflux pump proteins contained within Mycobacterial genomes "
                "which confer resistance to a number of different antibiotics "
                "including aminoglycosides, and tetracyclines."
            ),
            "notes": "CARD definition for tap.",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3000561",
        filename="tet-30-aro3000561.yaml",
        determinant_evidence={
            "reference": "ARO:3000561",
            "snippet": (
                "Tet30 is a tetracycline efflux pump found in agrobacterium, a "
                "Gram-negative bacterium."
            ),
            "notes": "CARD definition for tet(30).",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3000822",
        filename="pmra-aro3000822.yaml",
        determinant_evidence={
            "reference": "ARO:3000822",
            "snippet": (
                "PmrA is a MFS-type efflux pump expressed in Streptococcus "
                "pneumoniae that confers low-level resistance to norfloxacin, "
                "ciprofloxacin, and acriflavine."
            ),
            "notes": "CARD definition for pmrA.",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3004030",
        filename="rosab-aro3004030.yaml",
        determinant_evidence={
            "reference": "ARO:3004030",
            "snippet": (
                "An efflux pump/potassium antiporter system (RosAB) formed by "
                "the RosA and RosB proteins found in Yersinia."
            ),
            "notes": "CARD definition for RosAB.",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3003986",
        filename="taea-aro3003986.yaml",
        determinant_evidence={
            "reference": "ARO:3003986",
            "snippet": (
                "Pleuromutilin (Tiamulin) ABC efflux pump found in "
                "Paenibacillus sp. LC231, a strain of Paenibacillus isolated "
                "from Lechuguilla Cave, NM, USA."
            ),
            "notes": "CARD definition for TaeA.",
        },
        family=ABC_EFFLUX_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3003554",
        filename="tcma-aro3003554.yaml",
        determinant_evidence={
            "reference": "ARO:3003554",
            "snippet": (
                "Major facilitator superfamily transporter. Resistance to "
                "tetracenomycin C by an active tetracenomycin C efflux system "
                "which is probably energized by transmembrane electrochemical "
                "gradients."
            ),
            "notes": "CARD definition for tcmA.",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3002893",
        filename="tcr3-aro3002893.yaml",
        determinant_evidence={
            "reference": "ARO:3002893",
            "snippet": (
                "tcr3 is a tetracycline efflux pump that confers "
                "self-resistance to Kitasatospora aureofaciens."
            ),
            "notes": "CARD definition for tcr3.",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3000476",
        filename="tet-31-aro3000476.yaml",
        determinant_evidence={
            "reference": "ARO:3000476",
            "snippet": (
                "Tet31 is a tetracycline efflux pump found in Aeromonas "
                "salmonicida, a Gram-negative bacteria."
            ),
            "notes": "CARD definition for tet(31).",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3000478",
        filename="tet-33-aro3000478.yaml",
        determinant_evidence={
            "reference": "ARO:3000478",
            "snippet": (
                "Tet33 is a tetracycline efflux pump found in Gram-positive "
                "bacteria, including Arthrobacter and Corynebacterium."
            ),
            "notes": "CARD definition for tet(33).",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3000481",
        filename="tet-35-aro3000481.yaml",
        determinant_evidence={
            "reference": "ARO:3000481",
            "snippet": (
                "Tet35 is a tetracycline efflux pump found in the Gram-negative "
                "Vibrio and Stenotrophomonas."
            ),
            "notes": "CARD definition for tet(35).",
        },
        family=ABC_EFFLUX_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3000565",
        filename="tet-38-aro3000565.yaml",
        determinant_evidence={
            "reference": "ARO:3000565",
            "snippet": (
                "Tet38 is a tetracycline efflux pump found in the Gram-positive "
                "Staphylococcus aureus."
            ),
            "notes": "CARD definition for tet(38).",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3000566",
        filename="tet-39-aro3000566.yaml",
        determinant_evidence={
            "reference": "ARO:3000566",
            "snippet": (
                "Tet39 is a tetracycline efflux pump found in Gram-negative "
                "bacteria, including Brevundimonas, Stenotrophomonas, "
                "Enterobacter, Alcaligenes, Acinetobacter, and Providencia."
            ),
            "notes": "CARD definition for tet(39).",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3000567",
        filename="tet-40-aro3000567.yaml",
        determinant_evidence={
            "reference": "ARO:3000567",
            "snippet": (
                "Tet40 is a tetracycline efflux pump found in the Gram-positive "
                "Clostridium."
            ),
            "notes": "CARD definition for tet(40).",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3000569",
        filename="tet-41-aro3000569.yaml",
        determinant_evidence={
            "reference": "ARO:3000569",
            "snippet": (
                "Tet41 is a tetracycline efflux pump found in Serratia, a "
                "Gram-negative bacterium."
            ),
            "notes": "CARD definition for tet(41).",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3000572",
        filename="tet-42-aro3000572.yaml",
        determinant_evidence={
            "reference": "ARO:3000572",
            "snippet": (
                "Tet42 is a tetracycline efflux pump found in both "
                "Gram-negative (Pseudomonas) and Gram-positive "
                "(Microbacterium, Bacillus, Staphylococcus, Paenibacillus) "
                "bacteria."
            ),
            "notes": "CARD definition for tet(42).",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3000573",
        filename="tet-43-aro3000573.yaml",
        determinant_evidence={
            "reference": "ARO:3000573",
            "snippet": (
                "Tet(43) is a tetracycline resistance gene with unknown "
                "origins, isolated from metagenomic DNA."
            ),
            "notes": "CARD definition for tet(43).",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3003196",
        filename="tet-45-aro3003196.yaml",
        determinant_evidence={
            "reference": "ARO:3003196",
            "snippet": (
                "Tet45 is a tetracycline efflux pump found in Bhargavaea "
                "cecembensis strain previously isolated from a "
                "poultry-litter-impacted soil."
            ),
            "notes": "CARD definition for tet(45).",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3005006",
        filename="tet-57-aro3005006.yaml",
        determinant_evidence={
            "reference": "ARO:3005006",
            "snippet": "A tetracycline efflux MFS Transporter from Providencia sp. Y14.",
            "notes": "CARD definition for tet(57).",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3004441",
        filename="tet-59-aro3004441.yaml",
        determinant_evidence={
            "reference": "ARO:3004441",
            "snippet": (
                "Tet(59) is a chromosome-encoded tetracycline efflux pump "
                "described from a Chinese pig manure sample."
            ),
            "notes": "CARD definition for tet(59).",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3007492",
        filename="tet-62-aro3007492.yaml",
        determinant_evidence={
            "reference": "ARO:3007492",
            "snippet": "A novel tetA-type efflux pump.",
            "notes": "CARD definition for tet(62).",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3007493",
        filename="tet-63-aro3007493.yaml",
        determinant_evidence={
            "reference": "ARO:3007493",
            "snippet": "A tetracycline efflux MFS Transporter from Staphylococcus aureus.",
            "notes": "CARD definition for tet(63).",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3007494",
        filename="tet-64-aro3007494.yaml",
        determinant_evidence={
            "reference": "ARO:3007494",
            "snippet": "A tetracycline efflux MFS Transporter from Burkholderia ubonensis.",
            "notes": "CARD definition for tet(64).",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3007838",
        filename="tet-65-aro3007838.yaml",
        determinant_evidence={
            "reference": "ARO:3007838",
            "snippet": (
                "tet(65) is a tetracycline efflux gene identified from a "
                "Corynebacterium oculi plasmid."
            ),
            "notes": "CARD definition for tet(65).",
        },
        family=MFS_FAMILY,
    ),
)

ABC_F_TARGETS: tuple[AbcFTarget, ...] = (
    AbcFTarget(
        identifier="ARO:3004469",
        filename="abc-f-atp-binding-cassette-ribosomal-protection-protein-aro3004469.yaml",
        determinant_evidence=ABC_F_EVIDENCE,
    ),
    AbcFTarget(
        identifier="ARO:3002817",
        filename="cara-aro3002817.yaml",
        determinant_evidence={
            "reference": "ARO:3002817",
            "snippet": (
                "carA is an ABC-F subfamily protein involved in macrolide "
                "resistance."
            ),
            "notes": "CARD definition for carA.",
        },
    ),
    AbcFTarget(
        identifier="ARO:3003761",
        filename="eatav-aro3003761.yaml",
        determinant_evidence={
            "reference": "ARO:3003761",
            "snippet": (
                "eatAv is a mutated form of the wildtype eatA ABC-F subfamily "
                "protein isolated from Enterococcus faecium conferring "
                "resistance to lincosamides, streptogramin A's and "
                "pleuromutilins."
            ),
            "notes": "CARD definition for eatAv.",
        },
    ),
    AbcFTarget(
        identifier="ARO:3007637",
        filename="clostridioides-difficile-cplr-aro3007637.yaml",
        determinant_evidence={
            "reference": "ARO:3007637",
            "snippet": (
                "CplR is an ABC-F ATPase ribosomal protection protein from "
                "Clostridioides difficile which confers resistance to "
                "pleuromutilins and lincosamides."
            ),
            "notes": "CARD definition for Clostridioides difficile cplR.",
        },
    ),
    AbcFTarget(
        identifier="ARO:3007644",
        filename="clostridium-perfringes-cplr-aro3007644.yaml",
        determinant_evidence={
            "reference": "ARO:3007644",
            "snippet": (
                "CplR is an ABC-F ATPase ribosomal protection protein from "
                "Clostridium perfringes which confers resistance to "
                "pleuromutilins and lincosamides."
            ),
            "notes": "CARD definition for Clostridium perfringes cplR.",
        },
    ),
    AbcFTarget(
        identifier="ARO:3007645",
        filename="clostridium-sporogenes-cplr-aro3007645.yaml",
        determinant_evidence={
            "reference": "ARO:3007645",
            "snippet": (
                "CplR is an ABC-F ATPase ribosomal protection protein from "
                "Clostridium sporogenes which confers resistance to "
                "pleuromutilins and lincosamides."
            ),
            "notes": "CARD definition for Clostridium sporogenes cplR.",
        },
    ),
    AbcFTarget(
        identifier="ARO:3002881",
        filename="lmrc-aro3002881.yaml",
        determinant_evidence={
            "reference": "ARO:3002881",
            "snippet": (
                "lmrC is an ABC-F subfamily protein that confers resistance to "
                "lincosamides in Streptomyces lincolnensis and Lactococcus "
                "lactis."
            ),
            "notes": "CARD definition for lmrC.",
        },
    ),
    AbcFTarget(
        identifier="ARO:3007068",
        filename="miscellaneous-abc-f-subfamily-atp-binding-cassette-ribosomal-protection-proteins-aro3007068.yaml",
        determinant_evidence={
            "reference": "ARO:3007068",
            "snippet": (
                "Miscellaneous ABC-F subfamily ATP-binding cassette ribosomal "
                "protection proteins confer antibiotic resistance through "
                "ribosomal protection and not through antibiotic efflux."
            ),
            "notes": "CARD definition for miscellaneous ABC-F ribosomal protection proteins.",
        },
    ),
    AbcFTarget(
        identifier="ARO:3007646",
        filename="neobacillus-vireti-vmlr2-aro3007646.yaml",
        determinant_evidence={
            "reference": "ARO:3007646",
            "snippet": (
                "vmlR2 is an ABC-F ATPase ribosomal protection protein from "
                "Neobacillus vireti."
            ),
            "notes": "CARD definition for Neobacillus vireti vmlR2.",
        },
    ),
    AbcFTarget(
        identifier="ARO:3003036",
        filename="oleb-aro3003036.yaml",
        determinant_evidence={
            "reference": "ARO:3003036",
            "snippet": (
                "oleB is an ABC-F subfamily protein in Streptomyces "
                "antibioticus and is involved in oleandomycin secretion."
            ),
            "notes": "CARD definition for oleB.",
        },
    ),
    AbcFTarget(
        identifier="ARO:3003746",
        filename="optra-aro3003746.yaml",
        determinant_evidence={
            "reference": "ARO:3003746",
            "snippet": (
                "OptrA is a member of the ABC-F protein subfamily that confers "
                "resistance to oxazolidinones."
            ),
            "notes": "CARD definition for optrA.",
        },
    ),
    AbcFTarget(
        identifier="ARO:3004470",
        filename="poxta-aro3004470.yaml",
        determinant_evidence={
            "reference": "ARO:3004470",
            "snippet": (
                "PoxtA is an ABC-F subfamily ATP-binding cassette protein that "
                "confers resistance to tetracycline, -phenicol, and "
                "oxazolidone via modification of the bacterial ribosome."
            ),
            "notes": "CARD definition for poxtA.",
        },
    ),
    AbcFTarget(
        identifier="ARO:3002828",
        filename="srmb-aro3002828.yaml",
        determinant_evidence={
            "reference": "ARO:3002828",
            "snippet": (
                "srmB is an ABC-F subfamily protein found in Streptomyces "
                "ambofaciens that confers resistance to spiramycin."
            ),
            "notes": "CARD definition for srmB.",
        },
    ),
)
ABC_F_TARGET = ABC_F_TARGETS[0]

TARGETS: tuple[Target, ...] = (
    EFFLUX_TARGETS[0],
    ABC_F_TARGET,
    *ABC_F_TARGETS[1:],
    *EFFLUX_TARGETS[1:],
)
TARGET_BY_ID = {target.identifier: target for target in TARGETS}


def _dump(obj: Any) -> str:
    return yaml.safe_dump(
        obj,
        sort_keys=False,
        allow_unicode=True,
        width=100,
        default_flow_style=False,
    )


def _dicts(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _unique_evidence(*items: dict[str, str]) -> list[dict[str, str]]:
    evidence: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in items:
        reference = item["reference"]
        if reference in seen:
            continue
        seen.add(reference)
        evidence.append(copy.deepcopy(item))
    return evidence


def _edge(
    subject: str,
    predicate: str,
    predicate_id: str,
    object_: str,
    description: str,
    *evidence: dict[str, str],
) -> dict[str, Any]:
    return {
        "subject": subject,
        "predicate": predicate,
        "predicate_id": predicate_id,
        "object": object_,
        "description": description,
        "evidence": _unique_evidence(*evidence),
    }


def _determinant_node(record: dict[str, Any]) -> dict[str, str]:
    return {
        "node_id": "determinant",
        "label": str(record["label"]),
        "node_type": "PROTEIN",
        "grounding": str(record["identifier"]),
    }


def _efflux_graph(record: dict[str, Any], target: EffluxTarget) -> dict[str, Any]:
    family = target.family
    efflux_evidence = (
        target.determinant_evidence,
        family.family_evidence,
        EFFLUX_PUMP_EVIDENCE,
        ANTIBIOTIC_EFFLUX_EVIDENCE,
        family.transport_evidence,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → {family.title} → resistance",
        "description": family.graph_description,
        "nodes": [
            _determinant_node(record),
            {
                "node_id": "mech0",
                "label": "antibiotic efflux",
                "node_type": "MOLECULAR_FUNCTION",
                "grounding": "ARO:0010000",
            },
            copy.deepcopy(family.domain_node),
            copy.deepcopy(family.fold_node),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "CARD classifies this transporter under the antibiotic efflux "
                "resistance mechanism.",
                *efflux_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Antibiotic efflux confers resistance by transporting antibiotics "
                "out of the cell.",
                *efflux_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "The determinant exports antibiotic from the cell through its "
                "family-specific transport mechanism.",
                *efflux_evidence,
            ),
            _edge(
                "domain",
                "part of",
                "BFO:0000050",
                "determinant",
                "The transporter domain is part of the resistance determinant.",
                target.determinant_evidence,
                family.family_evidence,
                family.domain_evidence,
            ),
            _edge(
                "determinant",
                "member of",
                "RO:0002350",
                "fold",
                "The determinant adopts the transporter fold associated with this "
                "efflux-pump family.",
                target.determinant_evidence,
                family.family_evidence,
                family.fold_evidence,
            ),
            _edge(
                "domain",
                family.efflux_predicate,
                "RO:0002327",
                "mech0",
                "The transporter domain enables family-specific antibiotic export.",
                target.determinant_evidence,
                family.family_evidence,
                family.domain_evidence,
                family.transport_evidence,
            ),
        ],
    }


def _abc_f_graph(record: dict[str, Any], target: AbcFTarget) -> dict[str, Any]:
    protection_evidence = (
        target.determinant_evidence,
        TARGET_PROTECTION_EVIDENCE,
        TARGET_PROTECTION_PARENT_EVIDENCE,
        ABC_F_DISPLACEMENT_EVIDENCE,
    )
    atpase_evidence = (
        target.determinant_evidence,
        ABC_DOMAIN_EVIDENCE,
        ABC_FOLD_EVIDENCE,
        ABC_F_DISPLACEMENT_EVIDENCE,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → ribosomal protection → resistance",
        "description": (
            "Curated resistance-causation graph for ABC-F ribosomal protection "
            "proteins. The graph models the ABC ATPase determinant binding the "
            "ribosome and displacing bound antibiotic instead of modeling ABC-F "
            "as an efflux transporter."
        ),
        "nodes": [
            _determinant_node(record),
            {
                "node_id": "mech0",
                "label": "antibiotic target protection",
                "node_type": "MOLECULAR_FUNCTION",
                "grounding": "ARO:0001003",
            },
            {
                "node_id": "domain",
                "label": "ABC transporter ATP-binding domain",
                "node_type": "DOMAIN",
                "grounding": "Pfam:PF00005",
                "description": "ATP-binding domain carried by ABC-F ribosomal protection proteins.",
            },
            {
                "node_id": "fold",
                "label": "P-loop NTPase fold (ABC ATPase nucleotide-binding domain)",
                "node_type": "DOMAIN",
                "grounding": "CATH:3.40.50.300",
                "description": "P-loop NTPase fold adopted by ABC-F ATPase domains.",
            },
            {
                "node_id": "ribosome",
                "label": "ribosome",
                "node_type": "CELLULAR_LOCALIZATION",
                "grounding": "GO:0005840",
            },
            {
                "node_id": "displaced_antibiotic",
                "label": "antibiotic displaced from the ribosome",
                "node_type": "STATE",
                "description": (
                    "Local state for antibiotic removal from the ribosome by an "
                    "ABC-F target-protection protein."
                ),
            },
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "CARD classifies ABC-F proteins under antibiotic target "
                "protection, not efflux.",
                *protection_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Antibiotic target protection prevents antibiotics from binding "
                "or remaining bound to their target.",
                *protection_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "ABC-F proteins confer resistance through ribosomal target "
                "protection.",
                *protection_evidence,
            ),
            _edge(
                "domain",
                "part of",
                "BFO:0000050",
                "determinant",
                "The ABC ATP-binding domain is part of the ABC-F determinant.",
                *atpase_evidence,
            ),
            _edge(
                "determinant",
                "member of",
                "RO:0002350",
                "fold",
                "The ABC-F determinant adopts the P-loop NTPase fold used by ABC "
                "ATPase domains.",
                *atpase_evidence,
            ),
            _edge(
                "domain",
                "enables (ribosomal protection)",
                "RO:0002327",
                "mech0",
                "The ABC ATPase domain powers ribosomal target protection.",
                *atpase_evidence,
            ),
            _edge(
                "determinant",
                "molecularly interacts with",
                "RO:0002436",
                "ribosome",
                "ABC-F proteins protect the ribosome by binding it.",
                target.determinant_evidence,
                ABC_F_DISPLACEMENT_EVIDENCE,
                GO_RIBOSOME_EVIDENCE,
            ),
            _edge(
                "determinant",
                "causally upstream of (displaces antibiotic)",
                "RO:0002411",
                "displaced_antibiotic",
                "ABC-F proteins displace antibiotic from the ribosome.",
                *protection_evidence,
            ),
            _edge(
                "displaced_antibiotic",
                "negatively regulates (antibiotic occupancy)",
                "RO:0002212",
                "ribosome",
                "Displacement reduces antibiotic occupancy on the ribosome.",
                target.determinant_evidence,
                TARGET_PROTECTION_EVIDENCE,
                ABC_F_DISPLACEMENT_EVIDENCE,
                GO_RIBOSOME_EVIDENCE,
            ),
            _edge(
                "displaced_antibiotic",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Removing antibiotic from the ribosome is the terminal modeled "
                "cause of ABC-F target-protection resistance.",
                *protection_evidence,
            ),
        ],
    }


REQUIRED_NODES: dict[type[Target], set[str]] = {
    EffluxTarget: {"determinant", "mech0", "domain", "fold", "resistance"},
    AbcFTarget: {"determinant", "mech0", "domain", "fold", "resistance"},
}


def _validate_record(record: dict[str, Any], target: Target) -> None:
    if record.get("identifier") != target.identifier:
        raise ValueError(
            f"{target.filename}: expected {target.identifier}, "
            f"found {record.get('identifier')}"
        )
    if not record.get("label"):
        raise ValueError(f"{target.identifier}: missing label")

    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1 or graphs[0].get("graph_id") != "resistance":
        raise ValueError(f"{target.identifier}: expected exactly one resistance graph")

    node_ids = {
        str(node.get("node_id"))
        for node in _dicts(graphs[0].get("nodes"))
        if node.get("node_id")
    }
    missing_nodes = sorted(REQUIRED_NODES[type(target)] - node_ids)
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    _validate_record(record, target)

    if isinstance(target, EffluxTarget):
        graph = _efflux_graph(record, target)
    else:
        graph = _abc_f_graph(record, target)

    out = copy.deepcopy(record)
    out["causal_graphs"] = [graph]
    return out, out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not an ABC/MFS efflux or ABC-F target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    if HISTORY_CURATOR not in out:
        out = append_to_section(out, "curation_history", _dump({"curation_history": [HISTORY_EVENT]}))
        changed = True

    if "&id" in out or "*id" in out:
        raise ValueError(f"{path}: YAML anchors leaked into output")
    return out, changed


def iter_target_paths(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if not path.is_dir():
        raise ValueError(f"{path} is neither a file nor a directory")
    return [path / target.filename for target in TARGETS]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    parser.add_argument(
        "--path",
        type=Path,
        default=ARO_DIR,
        help="ARO directory or one of the target YAML files",
    )
    args = parser.parse_args(argv)

    changed = unchanged = 0
    problems: list[str] = []
    for path in iter_target_paths(args.path):
        if not path.exists():
            problems.append(f"{path}: missing")
            continue
        try:
            before = path.read_text(encoding="utf-8")
            after, did_change = enrich_text(before, path)
        except (OSError, ValueError, yaml.YAMLError) as exc:
            problems.append(str(exc))
            continue

        if not did_change:
            unchanged += 1
            continue

        changed += 1
        print(f"  {'wrote' if args.apply else 'would write'} {path.name}")
        if args.apply:
            path.write_text(after, encoding="utf-8")

    print(f"{'changed' if args.apply else 'would change'}: {changed}")
    print(f"already enriched: {unchanged}")
    for problem in problems:
        print(f"PROBLEM: {problem}", file=sys.stderr)
    if not args.apply:
        print("dry run -- pass --apply to write")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
