#!/usr/bin/env python3
"""Rewrite fluoroquinolone topoisomerase QRDR causal graphs.

The score-80/81 single-subunit gyrA, gyrB, parC, and parE records already use
the intended quinolone-target-alteration topology.  This pass keeps that graph
shape, grounds the local QRDR node to Sequence Ontology's generic polypeptide
region, adds the missing edge descriptions, and adds a second independent
reference to sparse edges.

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

HISTORY_CURATOR = "codex-causal-graph-quality"
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": "Completed fluoroquinolone topoisomerase QRDR causal graphs",
    "llm_assisted": True,
}


@dataclass(frozen=True)
class GraphKind:
    family: str
    parent: str
    subunit: str
    shared_domain: str
    domain_part: str
    qrdr_part: str
    qrdr_core: str
    determinant_resistance: str
    qrdr_domain_extra: tuple[dict[str, str], ...]
    qrdr_cleavage_extra: tuple[dict[str, str], ...]


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    kind: GraphKind


MUTATION_EVIDENCE = {
    "reference": "ARO:3000212",
    "snippet": (
        "Point mutations in the DNA may lead to an altered gene product that may "
        "result in antibiotic resistance."
    ),
    "notes": "CARD definition for mutation conferring antibiotic resistance.",
}

TOPOISOMERASE_CLEAVAGE_EVIDENCE = {
    "reference": "PMID:15659402",
    "snippet": (
        "Topoisomerase (topo) IV and gyrase are bacterial type IIA DNA "
        "topoisomerases essential for DNA replication and chromosome segregation "
        "that act via a transient double-stranded DNA break involving a covalent "
        "enzyme-DNA \"cleavage complex.\""
    ),
    "notes": (
        "Leo et al. 2005, supporting the type-II-topoisomerase "
        "cleavage-complex intermediate."
    ),
}

BUSH_STABILIZATION_EVIDENCE = {
    "reference": "DOI:10.3390/molecules25235662",
    "snippet": (
        "Quinolones stabilise the topoisomerase-DNA cleavage complex in which "
        "there is a double-strand break."
    ),
    "notes": (
        "Bush et al. 2020, review of quinolone trapping of DNA gyrase and "
        "topoisomerase IV cleavage complexes."
    ),
}

BUSH_CELL_DEATH_EVIDENCE = {
    "reference": "DOI:10.3390/molecules25235662",
    "snippet": (
        "If the cleavage complex is not processed, DNA replication and "
        "transcription are blocked, eventually leading to cell death: slow death."
    ),
    "notes": (
        "Bush et al. 2020, linking unresolved topoisomerase-DNA cleavage "
        "complexes to blocked replication/transcription and death."
    ),
}

SO_QRDR_EVIDENCE = {
    "reference": "SO:0000839",
    "snippet": "polypeptide_region",
    "notes": (
        "Sequence Ontology superclass used for this protein-local QRDR; no "
        "ontology term denotes a quinolone resistance-determining region itself."
    ),
}

INTERPRO_A_SUBUNIT_EVIDENCE = {
    "reference": "InterPro:IPR002205",
    "snippet": (
        "domain 3 (N-terminal of gyrA) is responsible for the breaking-rejoining "
        "function through its capacity to form protein-DNA bridges"
    ),
    "notes": (
        "InterPro abstract behind Pfam:PF00521, the shared GyrA/ParC subunit-A "
        "domain in this KB."
    ),
}

INTERPRO_B_SUBUNIT_EVIDENCE = {
    "reference": "InterPro:IPR013506",
    "snippet": (
        "There are four functional domains in topoisomerase II: domain 1 "
        "(N-terminal of gyrB) is an ATPase, domain 2 (C-terminal of gyrB) is "
        "responsible for subunit interactions, domain 3 (N-terminal of gyrA) is "
        "responsible for the breaking-rejoining function through its capacity to "
        "form protein-DNA bridges, and domain 4 (C-terminal of gyrA) is able to "
        "non-specifically bind DNA."
    ),
    "notes": (
        "InterPro abstract behind Pfam:PF00204, the shared GyrB/ParE subunit-B "
        "domain in this KB."
    ),
}

ALDRED_SUBUNITS_EVIDENCE = {
    "reference": "PMID:24576155",
    "snippet": (
        "The subunits in gyrase are GyrA and GyrB. The homologous subunits in "
        "topoisomerase IV are ParC and ParE in Gram-negative species and GrlA "
        "and GrlB in Gram-positive species. GyrA (and the equivalent "
        "topoisomerase IV subunit) contains the active site tyrosine residue. "
        "GyrB (and the equivalent topoisomerase IV subunit) contains the ATPase "
        "domain as well as the TOPRIM domain, which binds the divalent metal "
        "ions involved in DNA cleavage and ligation."
    ),
    "notes": "Aldred 2014, the subunit architecture of gyrase and topoisomerase IV.",
}

ALDRED_A_SUBUNIT_QRDR_EVIDENCE = {
    "reference": "PMID:24576155",
    "snippet": (
        "Furthermore, mutation of either residue significantly decreases the "
        "affinity of gyrase or topoisomerase IV for quinolones, and mutation of "
        "both residues abolishes the ability of clinically relevant quinolones "
        "to stabilize cleavage complexes."
    ),
    "notes": (
        "Aldred 2014, the GyrA/ParC water-metal ion bridge that QRDR "
        "substitutions disrupt."
    ),
}

ALDRED_PARC_QRDR_EVIDENCE = {
    "reference": "PMID:24576155",
    "snippet": "In A. baumannii topoisomerase IV, these residues are Ser84 and Glu88, respectively.",
    "notes": (
        "Aldred 2014, identifying the water-metal ion bridge pair in a "
        "topoisomerase IV A subunit."
    ),
}

GYRA_QRDR_EVIDENCE = {
    "reference": "PMID:2168148",
    "snippet": (
        "quinolone resistance was caused by a point mutation within the region "
        "between amino acids 67 and 106, especially in the vicinity of amino "
        "acid 83, of the GyrA protein"
    ),
    "notes": "Yoshida et al. 1990, defining the GyrA QRDR.",
}

PARC_QRDR_EVIDENCE = {
    "reference": "PMID:15388468",
    "snippet": (
        "Mutations were found in parC that encoded Thr57-Ser, Thr66-Ile, and "
        "Ser80-Arg substitutions."
    ),
    "notes": "Eaves et al. 2004, Salmonella enterica ParC QRDR substitutions.",
}

GYRB_QRDR_EVIDENCE = {
    "reference": "PMID:1656869",
    "snippet": (
        "all nine type 1 mutants had a point mutation from aspartic acid to "
        "asparagine at amino acid 426 and that all four type 2 mutants had a "
        "point mutation from lysine to glutamic acid at amino acid 447"
    ),
    "notes": "Yoshida et al. 1991, defining the GyrB QRDR in E. coli.",
}

PANTEL_GYRB_EVIDENCE = {
    "reference": "PMID:22290942",
    "snippet": (
        "All these substitutions are clearly implicated in FQ resistance, "
        "underlining the presence of a hot spot region housing most of the GyrB "
        "substitutions implicated in FQ resistance (residues NTE, 538 to 540)."
    ),
    "notes": (
        "Pantel et al. 2012 measured fluoroquinolone inhibition of reconstituted "
        "gyrase with mutant GyrB subunits."
    ),
}

PARE_QRDR_EVIDENCE = {
    "reference": "PMID:15388468",
    "snippet": (
        "Novel mutations were also found in parE encoding Glu453-Gly, "
        "His461-Tyr, Ala498-Thr, Val512-Gly, and Ser518-Cys."
    ),
    "notes": "Eaves et al. 2004, Salmonella enterica ParE QRDR substitutions.",
}


GYRA = GraphKind(
    family="GyrA",
    parent="ARO:3003292",
    subunit="GyrA",
    shared_domain="subunit-A",
    domain_part="The grounded GyrA/ParC N-terminal subunit-A domain contains the QRDR.",
    qrdr_part="The GyrA QRDR is an N-terminal polypeptide region of the subunit-A domain.",
    qrdr_core=(
        "GyrA QRDR substitutions reduce fluoroquinolone trapping of the gyrase-DNA "
        "cleavage complex."
    ),
    determinant_resistance=(
        "The determinant carries a GyrA QRDR substitution that lowers "
        "fluoroquinolone binding to the gyrase-DNA cleavage complex."
    ),
    qrdr_domain_extra=(GYRA_QRDR_EVIDENCE, SO_QRDR_EVIDENCE),
    qrdr_cleavage_extra=(ALDRED_A_SUBUNIT_QRDR_EVIDENCE, GYRA_QRDR_EVIDENCE),
)

PARC = GraphKind(
    family="ParC",
    parent="ARO:3000619",
    subunit="ParC",
    shared_domain="subunit-A",
    domain_part="The grounded GyrA/ParC N-terminal subunit-A domain contains the QRDR.",
    qrdr_part=(
        "ParC is topoisomerase IV's homologue of GyrA, so its QRDR sits in the "
        "same subunit-A domain entry."
    ),
    qrdr_core=(
        "ParC QRDR substitutions reduce fluoroquinolone trapping of the "
        "topoisomerase IV-DNA cleavage complex."
    ),
    determinant_resistance=(
        "The determinant carries a ParC QRDR substitution that lowers "
        "fluoroquinolone action on topoisomerase IV."
    ),
    qrdr_domain_extra=(ALDRED_SUBUNITS_EVIDENCE, PARC_QRDR_EVIDENCE, SO_QRDR_EVIDENCE),
    qrdr_cleavage_extra=(
        ALDRED_A_SUBUNIT_QRDR_EVIDENCE,
        ALDRED_PARC_QRDR_EVIDENCE,
        PARC_QRDR_EVIDENCE,
    ),
)

GYRB = GraphKind(
    family="GyrB",
    parent="ARO:3000864",
    subunit="GyrB",
    shared_domain="subunit-B",
    domain_part="The grounded GyrB/ParE subunit-B domain contains the QRDR.",
    qrdr_part="The GyrB QRDR is a region of the B subunit, distinct from the GyrA QRDR.",
    qrdr_core=(
        "GyrB QRDR substitutions reduce fluoroquinolone inhibition of DNA gyrase "
        "through the B subunit."
    ),
    determinant_resistance=(
        "The determinant carries a GyrB QRDR substitution that lowers "
        "fluoroquinolone inhibition of DNA gyrase."
    ),
    qrdr_domain_extra=(GYRB_QRDR_EVIDENCE, PANTEL_GYRB_EVIDENCE, SO_QRDR_EVIDENCE),
    qrdr_cleavage_extra=(PANTEL_GYRB_EVIDENCE, GYRB_QRDR_EVIDENCE),
)

PARE = GraphKind(
    family="ParE",
    parent="ARO:3003313",
    subunit="ParE",
    shared_domain="subunit-B",
    domain_part="The grounded GyrB/ParE subunit-B domain contains the QRDR.",
    qrdr_part=(
        "ParE is topoisomerase IV's homologue of GyrB, so its QRDR sits in the "
        "same subunit-B domain entry."
    ),
    qrdr_core=(
        "ParE QRDR substitutions are associated with fluoroquinolone resistance "
        "through topoisomerase IV's B subunit."
    ),
    determinant_resistance=(
        "The determinant carries a ParE QRDR substitution associated with lower "
        "fluoroquinolone action on topoisomerase IV."
    ),
    qrdr_domain_extra=(PARE_QRDR_EVIDENCE, ALDRED_SUBUNITS_EVIDENCE, SO_QRDR_EVIDENCE),
    qrdr_cleavage_extra=(PARE_QRDR_EVIDENCE, ALDRED_SUBUNITS_EVIDENCE),
)

TARGETS: tuple[Target, ...] = (
    Target("ARO:3003292", "fluoroquinolone-resistant-gyra-aro3003292.yaml", GYRA),
    Target("ARO:3003294", "escherichia-coli-gyra-conferring-resistance-to-fluoroquinolones-aro3003294.yaml", GYRA),
    Target("ARO:3003295", "mycobacterium-tuberculosis-gyra-conferring-resistance-to-fluoroquinolones-aro3003295.yaml", GYRA),
    Target("ARO:3003296", "staphylococcus-aureus-gyra-conferring-resistance-to-fluoroquinolones-aro3003296.yaml", GYRA),
    Target("ARO:3003297", "bartonella-bacilliformis-gyra-conferring-resistance-to-fluoroquinolones-aro3003297.yaml", GYRA),
    Target("ARO:3003298", "mycobacterium-leprae-gyra-conferring-resistance-to-fluoroquinolones-aro3003298.yaml", GYRA),
    Target("ARO:3003684", "pseudomonas-aeruginosa-gyra-conferring-resistance-to-fluoroquinolones-aro3003684.yaml", GYRA),
    Target("ARO:3003789", "campylobacter-jejuni-gyra-conferring-resistance-to-fluoroquinolones-aro3003789.yaml", GYRA),
    Target("ARO:3003817", "acinetobacter-baumannii-gyra-conferring-resistance-to-fluoroquinolones-aro3003817.yaml", GYRA),
    Target("ARO:3003924", "haemophilus-parainfluenzae-gyra-conferring-resistance-to-fluoroquinolones-aro3003924.yaml", GYRA),
    Target("ARO:3003926", "salmonella-enterica-gyra-conferring-resistance-to-fluoroquinolones-aro3003926.yaml", GYRA),
    Target("ARO:3003928", "neisseria-gonorrhoeae-gyra-with-mutations-conferring-resistance-to-fluoroquinolo-aro3003928.yaml", GYRA),
    Target("ARO:3003931", "capnocytophaga-gingivalis-gyra-conferring-resistance-to-fluoroquinolones-aro3003931.yaml", GYRA),
    Target("ARO:3003940", "shigella-flexneri-gyra-conferring-resistance-to-fluoroquinolones-aro3003940.yaml", GYRA),
    Target("ARO:3003974", "cutibacterium-acnes-gyra-conferring-resistance-to-fluoroquinolones-aro3003974.yaml", GYRA),
    Target("ARO:3003995", "clostridioides-difficile-gyra-conferring-resistance-to-fluoroquinolones-aro3003995.yaml", GYRA),
    Target("ARO:3004631", "mycoplasma-genitalium-gyra-mutation-confers-resistance-to-fluoroquinolones-aro3004631.yaml", GYRA),
    Target("ARO:3004860", "burkholderia-dolosa-gyra-conferring-resistance-to-fluoroquinolones-aro3004860.yaml", GYRA),
    Target("ARO:3007052", "helicobacter-pylori-gyra-conferring-resistance-to-fluoroquinolones-aro3007052.yaml", GYRA),
    Target("ARO:3007473", "mycobacterium-avium-gyra-with-mutation-conferring-resistance-to-fluoroquinolone-aro3007473.yaml", GYRA),
    Target("ARO:3007544", "erysipelothrix-rhusiopathiae-gyra-with-mutation-conferring-resistance-to-enroflo-aro3007544.yaml", GYRA),
    Target("ARO:3007751", "salmonella-isangi-gyra-conferring-resistance-to-fluoroquinolones-aro3007751.yaml", GYRA),
    Target("ARO:3007806", "mycobacterium-tuberculosis-gyra-mutations-conferring-resistance-to-moxifloxacin-aro3007806.yaml", GYRA),
    Target("ARO:3007807", "mycobacterium-tuberculosis-gyra-mutations-conferring-resistance-to-ofloxacin-aro3007807.yaml", GYRA),
    Target("ARO:3007809", "mycobacterium-tuberculosis-gyra-mutations-conferring-resistance-to-levofloxacin-aro3007809.yaml", GYRA),
    Target("ARO:3000864", "fluoroquinolone-resistant-gyrb-aro3000864.yaml", GYRB),
    Target("ARO:3003304", "mycobacterium-leprae-gyrb-conferring-resistance-to-fluoroquinolones-aro3003304.yaml", GYRB),
    Target("ARO:3003305", "ureaplasma-urealyticum-gyrb-conferring-resistance-to-fluoroquinolones-aro3003305.yaml", GYRB),
    Target("ARO:3003306", "morganella-morganii-gyrb-conferring-resistance-to-fluoroquinolones-aro3003306.yaml", GYRB),
    Target("ARO:3003307", "salmonella-serovars-gyrb-conferring-resistance-to-fluoroquinolones-aro3003307.yaml", GYRB),
    Target("ARO:3003459", "mycobacterium-tuberculosis-gyrb-mutant-conferring-resistance-to-fluoroquinolones-aro3003459.yaml", GYRB),
    Target("ARO:3004562", "clostridioides-difficile-gyrb-conferring-resistance-to-fluoroquinolones-aro3004562.yaml", GYRB),
    Target("ARO:3007053", "helicobacter-pylori-gyrb-conferring-resistance-to-fluoroquinolones-aro3007053.yaml", GYRB),
    Target("ARO:3007752", "salmonella-isangi-gyrb-conferring-resistance-to-fluoroquinolones-aro3007752.yaml", GYRB),
    Target("ARO:3000619", "fluoroquinolone-resistant-parc-aro3000619.yaml", PARC),
    Target("ARO:3003308", "escherichia-coli-parc-conferring-resistance-to-fluoroquinolones-aro3003308.yaml", PARC),
    Target("ARO:3003309", "ureaplasma-urealyticum-parc-conferring-resistance-to-fluoroquinolones-aro3003309.yaml", PARC),
    Target("ARO:3003310", "mycoplasma-hominis-parc-conferring-resistance-to-fluoroquinolones-aro3003310.yaml", PARC),
    Target("ARO:3003311", "streptococcus-pneumoniae-parc-conferring-resistance-to-fluoroquinolones-aro3003311.yaml", PARC),
    Target("ARO:3003312", "staphylococcus-aureus-parc-conferring-resistance-to-fluoroquinolones-aro3003312.yaml", PARC),
    Target("ARO:3003818", "acinetobacter-baumannii-parc-conferring-resistance-to-fluoroquinolones-aro3003818.yaml", PARC),
    Target("ARO:3003925", "haemophilus-parainfluenzae-parc-conferring-resistance-to-fluoroquinolones-aro3003925.yaml", PARC),
    Target("ARO:3003929", "neisseria-gonorrhoeae-parc-conferring-resistance-to-fluoroquinolones-aro3003929.yaml", PARC),
    Target("ARO:3003939", "salmonella-enterica-parc-conferring-resistance-to-fluoroquinolones-aro3003939.yaml", PARC),
    Target("ARO:3003941", "shigella-flexneri-parc-conferring-resistance-to-fluoroquinolones-aro3003941.yaml", PARC),
    Target("ARO:3004630", "mycoplasma-genitalium-parc-mutations-confers-resistance-to-moxifloxacin-aro3004630.yaml", PARC),
    Target("ARO:3003313", "fluoroquinolone-resistant-pare-aro3003313.yaml", PARE),
    Target("ARO:3003315", "staphylococcus-aureus-pare-conferring-resistance-to-fluoroquinolones-aro3003315.yaml", PARE),
    Target("ARO:3003316", "escherichia-coli-pare-conferring-resistance-to-fluoroquinolones-aro3003316.yaml", PARE),
    Target("ARO:3003317", "salmonella-serovars-pare-conferring-resistance-to-fluoroquinolones-aro3003317.yaml", PARE),
    Target("ARO:3003685", "pseudomonas-aeruginosa-pare-conferring-resistance-to-fluoroquinolones-aro3003685.yaml", PARE),
)
TARGET_BY_ID = {target.identifier: target for target in TARGETS}

EXPECTED_EDGE_KEYS = {
    ("determinant", "mech0"),
    ("mech0", "resistance"),
    ("determinant", "resistance"),
    ("determinant", "drug0"),
    ("domain", "determinant"),
    ("qrdr", "domain"),
    ("domain", "gyrase_activity"),
    ("gyrase_activity", "cleavage_complex"),
    ("drug0", "cleavage_complex"),
    ("qrdr", "cleavage_complex"),
    ("cleavage_complex", "cell_death"),
}


def _dump(obj: Any) -> str:
    return yaml.safe_dump(
        obj,
        sort_keys=False,
        allow_unicode=True,
        width=100,
        default_flow_style=False,
    )


def record_evidence(record: dict[str, Any]) -> dict[str, str]:
    return {
        "reference": str(record["identifier"]),
        "snippet": " ".join(str(record.get("definition", "")).split()),
        "notes": f"CARD definition for {record['label']}.",
    }


def fresh_evidence(items: list[dict[str, str]]) -> list[dict[str, str]]:
    return [copy.deepcopy(item) for item in items]


def unique_evidence(items: list[dict[str, str]]) -> list[dict[str, str]]:
    evidence = []
    seen = set()
    for item in items:
        marker = (item.get("reference"), item.get("snippet"))
        if marker in seen:
            continue
        seen.add(marker)
        evidence.append(item)
    return evidence


def interpro_evidence(kind: GraphKind) -> dict[str, str]:
    if kind in (GYRA, PARC):
        return INTERPRO_A_SUBUNIT_EVIDENCE
    return INTERPRO_B_SUBUNIT_EVIDENCE


def set_node_grounding(graph: dict[str, Any]) -> None:
    for node in graph["nodes"]:
        if node["node_id"] == "qrdr":
            node["grounding"] = "SO:0000839"
            node["description"] = str(node.get("description", "")).replace(
                "Ungrounded: no ontology term denotes the QRDR.",
                (
                    "Grounded to Sequence Ontology's generic polypeptide_region "
                    "superclass because no ontology term denotes the QRDR itself."
                ),
            )
        elif node["node_id"] == "cleavage_complex":
            node["description"] = (
                "The covalent enzyme-cleaved DNA intermediate that quinolones bind "
                "and stabilise. This is a source-local topoisomerase reaction state."
            )


def evidence_for_edge(
    key: tuple[str, str],
    kind: GraphKind,
    target_evidence: dict[str, str],
) -> list[dict[str, str]]:
    match key:
        case ("determinant", "mech0"):
            return [target_evidence, MUTATION_EVIDENCE, *kind.qrdr_cleavage_extra]
        case ("mech0", "resistance"):
            return [target_evidence, MUTATION_EVIDENCE, *kind.qrdr_cleavage_extra]
        case ("determinant", "resistance"):
            return [target_evidence, MUTATION_EVIDENCE, *kind.qrdr_cleavage_extra]
        case ("determinant", "drug0"):
            return [target_evidence, BUSH_STABILIZATION_EVIDENCE, *kind.qrdr_cleavage_extra]
        case ("domain", "determinant"):
            return [target_evidence, interpro_evidence(kind), ALDRED_SUBUNITS_EVIDENCE]
        case ("qrdr", "domain"):
            return [*kind.qrdr_domain_extra]
        case ("domain", "gyrase_activity"):
            return [interpro_evidence(kind), ALDRED_SUBUNITS_EVIDENCE]
        case ("gyrase_activity", "cleavage_complex"):
            return [TOPOISOMERASE_CLEAVAGE_EVIDENCE]
        case ("drug0", "cleavage_complex"):
            return [BUSH_STABILIZATION_EVIDENCE]
        case ("qrdr", "cleavage_complex"):
            return [target_evidence, *kind.qrdr_cleavage_extra]
        case ("cleavage_complex", "cell_death"):
            return [BUSH_CELL_DEATH_EVIDENCE]
        case _:
            raise ValueError(f"unexpected edge {key}")


def edge_description(edge: dict[str, Any], kind: GraphKind) -> str:
    key = (edge["subject"], edge["object"])
    match key:
        case ("determinant", "mech0"):
            return (
                f"CARD classifies this fluoroquinolone-resistant {kind.subunit} "
                "determinant under mutation conferring antibiotic resistance."
            )
        case ("mech0", "resistance"):
            return (
                "QRDR substitution is a mutation-driven target alteration that "
                "reduces fluoroquinolone trapping of a type-II-topoisomerase "
                "cleavage complex."
            )
        case ("determinant", "resistance"):
            return kind.determinant_resistance
        case ("determinant", "drug0"):
            return (
                f"CARD asserts that fluoroquinolone-resistant {kind.subunit} "
                "determinants confer resistance to fluoroquinolone antibiotics."
            )
        case ("domain", "determinant"):
            return kind.domain_part
        case ("qrdr", "domain"):
            return kind.qrdr_part
        case ("domain", "gyrase_activity"):
            return (
                f"The {kind.shared_domain} domain belongs to the bacterial type IIA "
                "topoisomerases that catalyze ATP-dependent DNA strand passage."
            )
        case ("gyrase_activity", "cleavage_complex"):
            return (
                "Type IIA topoisomerase activity transiently forms a covalent "
                "enzyme-cleaved-DNA intermediate."
            )
        case ("drug0", "cleavage_complex"):
            return (
                "Fluoroquinolones bind and stabilize the cleaved gyrase or "
                "topoisomerase IV complex, increasing the level of broken DNA."
            )
        case ("qrdr", "cleavage_complex"):
            return kind.qrdr_core
        case ("cleavage_complex", "cell_death"):
            return (
                "Unresolved topoisomerase-DNA cleavage complexes block replication "
                "and transcription and can become lethal DNA lesions."
            )
        case _:
            raise ValueError(f"unexpected edge {key}")


def enrich_graph(graph: dict[str, Any], record: dict[str, Any], kind: GraphKind) -> dict[str, Any]:
    graph = copy.deepcopy(graph)
    graph["title"] = f"{record['label']} → fluoroquinolone topoisomerase QRDR alteration"
    graph["description"] = (
        f"Curated resistance-causation graph for fluoroquinolone-resistant {kind.family} "
        "QRDR determinants. The determinant is a mutated type-II-topoisomerase subunit "
        "whose QRDR substitution reduces fluoroquinolone trapping of the cleaved enzyme-DNA "
        "complex."
    )
    set_node_grounding(graph)

    keys = {(edge["subject"], edge["object"]) for edge in graph["edges"]}
    if keys != EXPECTED_EDGE_KEYS:
        raise ValueError(f"expected edge keys {sorted(EXPECTED_EDGE_KEYS)}, got {sorted(keys)}")

    target_evidence = record_evidence(record)
    for edge in graph["edges"]:
        key = (edge["subject"], edge["object"])
        edge["description"] = edge_description(edge, kind)
        edge["evidence"] = fresh_evidence(
            unique_evidence(
                [*edge.get("evidence", []), *evidence_for_edge(key, kind, target_evidence)]
            )
        )

    return graph


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not a fluoroquinolone topoisomerase target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    graphs = record.get("causal_graphs")
    if not isinstance(graphs, list) or len(graphs) != 1:
        raise ValueError(f"{path}: expected exactly one causal graph")

    enriched_graph = enrich_graph(graphs[0], record, target.kind)
    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": [enriched_graph]}))
    changed = out != text
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
        help="ARO directory or one of the fluoroquinolone topoisomerase YAML files",
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
        except (KeyError, OSError, ValueError, yaml.YAMLError) as exc:
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
