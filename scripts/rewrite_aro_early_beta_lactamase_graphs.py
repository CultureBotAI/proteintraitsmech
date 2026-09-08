#!/usr/bin/env python3
"""Rewrite early alphabetic low-scoring beta-lactamase ARO causal graphs.

These exact score-77 AER/AFM/ALG/ALI/ANA/AQU/ARL/ASU1/AXC/B3SU records still
have promoted beta-lactamase graphs with mostly single-reference, undescribed
edges. They split across class A serine beta-lactamases and class B
metallo-beta-lactamases; both graph kinds preserve all existing
determinant-to-drug-class edges.

Dry-run by default; pass ``--apply`` to write.
"""

from __future__ import annotations

import argparse
import copy
import re
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from record_io import append_to_section, replace_block  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ARO_DIR = ROOT / "data" / "traits" / "function" / "resistance" / "aro"

HISTORY_CURATOR = "codex-causal-graph-quality"
HISTORY_EVENT = {
    "timestamp": "2026-09-08T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": "Completed early beta-lactamase causal graphs",
    "llm_assisted": True,
}

INACTIVATION_ENZYME_EVIDENCE = {
    "reference": "ARO:3000557",
    "snippet": (
        "Enzyme that catalyzes the inactivation of an antibiotic resulting in "
        "resistance."
    ),
    "notes": "CARD definition for antibiotic inactivation enzymes.",
}

ANTIBIOTIC_INACTIVATION_EVIDENCE = {
    "reference": "ARO:0001004",
    "snippet": "Enzymatic inactivation of antibiotic to confer drug resistance.",
    "notes": "CARD definition for antibiotic inactivation.",
}

BETA_LACTAMASE_EVIDENCE = {
    "reference": "ARO:3000001",
    "snippet": (
        "The lactamase enzyme breaks that ring open, deactivating the "
        "molecule's antibacterial properties."
    ),
    "notes": "CARD definition for beta-lactamases.",
}

CLASS_A_EVIDENCE = {
    "reference": "ARO:3000078",
    "snippet": (
        "The Class A beta-lactamases are one of the subgroups of "
        "beta-lactamases that are classified as serine enzymes. Class A "
        "beta-lactamases exhibit a large degree of variability and are known "
        "to hydrolyze penicillins."
    ),
    "notes": "CARD definition for class A beta-lactamases.",
}

CLASS_C_EVIDENCE = {
    "reference": "ARO:3000076",
    "snippet": (
        "AmpC type beta-lactamases are commonly isolated from "
        "extended-spectrum cephalosporin-resistant Gram-negative bacteria. "
        "AmpC beta-lactamases (also termed class C or group 1) are typically "
        "encoded on the chromosome of many Gram-negative bacteria including "
        "Citrobacter, Serratia, Enterobacter species, and P. aeruginosa where "
        "its expression is usually inducible; it may also occur on Escherichia "
        "coli but is not usually inducible, although it can be hyperexpressed. "
        "AmpC type beta-lactamases may also be carried on plasmids. AmpC "
        "beta-lactamases, in contrast to ESBLs, hydrolyse broad and "
        "extended-spectrum cephalosporins (cephamycins as well as to "
        "oxyimino-beta-lactams) but are not inhibited by beta-lactamase "
        "inhibitors such as clavulanic acid."
    ),
    "notes": "CARD definition for class C beta-lactamase.",
}

SERINE_BETA_LACTAMASE_EVIDENCE = {
    "reference": "ARO:3000187",
    "snippet": (
        "Mechanism of enzymatic degradation common to Ambler Class A, C and D "
        "beta-lactamases. A serine residue located in the active site is used "
        "to form an acyl-enzyme intermediate and subsequent hydrolysis renders "
        "the beta-lactam inactive."
    ),
    "notes": "CARD definition for serine beta-lactamase hydrolysis.",
}

SERINE_REACTION_EVIDENCE = {
    "reference": "PMID:32576842",
    "snippet": (
        "In the first acylation step, the β-lactam antibiotic forms an "
        "acyl-enzyme intermediate (ES*) with the catalytic serine residue."
    ),
    "notes": "Evidence for the serine beta-lactamase acyl-enzyme mechanism.",
}

CLASS_C_REACTION_EVIDENCE = {
    "reference": "PMID:19136439",
    "snippet": (
        "AmpC β-lactamases are clinically important cephalosporinases encoded "
        "on the chromosomes of many of the Enterobacteriaceae and a few other "
        "organisms."
    ),
    "notes": "Evidence for AmpC/class C beta-lactamases.",
}

PROSITE_CLASS_A_EVIDENCE = {
    "reference": "PROSITE:PS00146",
    "snippet": "Beta-lactamase class-A active site",
    "notes": "PROSITE active-site signature for class A beta-lactamases.",
}

PROSITE_CLASS_C_EVIDENCE = {
    "reference": "PROSITE:PRU10102",
    "snippet": "Beta-lactamase class-C active site",
    "notes": "PROSITE active-site signature for class C beta-lactamases.",
}

CATH_SERINE_BETA_LACTAMASE_EVIDENCE = {
    "reference": "CATH:3.40.710.10",
    "snippet": "DD-peptidase/beta-lactamase superfamily",
    "notes": "CATH fold for serine beta-lactamases.",
}

METALLO_BETA_LACTAMASE_EVIDENCE = {
    "reference": "ARO:3000203",
    "snippet": (
        "Mechanism of enzymatic degradation common to Ambler Class B "
        "beta-lactamases. One or two zinc atoms are used to orient a hydroxide "
        "nucleophile for attack of the beta-lactam ring."
    ),
    "notes": "CARD definition for metallo-beta-lactamase hydrolysis.",
}

MBL_REACTION_EVIDENCE = {
    "reference": "PMID:33199283",
    "snippet": (
        "MBLs are one class of β-lactamases (Ambler class B), requiring "
        "divalent zinc ions for their β-lactamase activity."
    ),
    "notes": "Evidence for zinc-dependent metallo-beta-lactamase activity.",
}

PFAM_MBL_EVIDENCE = {
    "reference": "Pfam:PF00753",
    "snippet": "Metallo-beta-lactamase superfamily",
    "notes": "Pfam family for metallo-beta-lactamases.",
}

CATH_MBL_EVIDENCE = {
    "reference": "CATH:3.60.15.30",
    "snippet": "Metallo-beta-lactamase domain",
    "notes": "CATH fold for metallo-beta-lactamases.",
}

MECH0_NODE = {
    "node_id": "mech0",
    "label": "antibiotic inactivation",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:0001004",
}

SERINE_MECH1_NODE = {
    "node_id": "mech1",
    "label": "hydrolysis of beta-lactam antibiotic by serine beta-lactamase",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3000187",
}

METALLO_MECH1_NODE = {
    "node_id": "mech1",
    "label": "hydrolysis of beta-lactam antibiotic by metallo-beta-lactamase",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3000203",
}

CLASS_A_ACTIVE_SITE_NODE = {
    "node_id": "active_site",
    "label": "class A beta-lactamase active-site signature (S-x-x-K)",
    "node_type": "MOTIF",
    "grounding": "PROSITE:PS00146",
    "description": "Class A beta-lactamase catalytic serine active-site signature.",
}

CLASS_C_ACTIVE_SITE_NODE = {
    "node_id": "active_site",
    "label": "class C beta-lactamase active-site signature (Ser64 S-x-x-K)",
    "node_type": "MOTIF",
    "grounding": "PROSITE:PRU10102",
    "description": "Class C beta-lactamase catalytic serine active-site signature.",
}

SERINE_FOLD_NODE = {
    "node_id": "fold",
    "label": "DD-peptidase/beta-lactamase superfamily fold",
    "node_type": "DOMAIN",
    "grounding": "CATH:3.40.710.10",
    "description": "DD-peptidase/beta-lactamase superfamily fold.",
}

MBL_DOMAIN_NODE = {
    "node_id": "domain",
    "label": "metallo-beta-lactamase superfamily domain",
    "node_type": "DOMAIN",
    "grounding": "Pfam:PF00753",
    "description": "Metallo-beta-lactamase domain that binds catalytic zinc.",
}

MBL_FOLD_NODE = {
    "node_id": "fold",
    "label": "metallo-beta-lactamase domain fold",
    "node_type": "DOMAIN",
    "grounding": "CATH:3.60.15.30",
    "description": "Metallo-beta-lactamase structural fold.",
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

DRUG_ID = re.compile(r"^drug\d+$")


class GraphKind(Enum):
    CLASS_A = "CLASS_A"
    CLASS_C = "CLASS_C"
    METALLO = "METALLO"


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    kind: GraphKind


TARGETS: tuple[Target, ...] = (
    Target("ARO:3002481", "aer-1-aro3002481.yaml", GraphKind.CLASS_A),
    Target("ARO:3000089", "aer-beta-lactamase-aro3000089.yaml", GraphKind.CLASS_A),
    Target("ARO:3006890", "afm-1-aro3006890.yaml", GraphKind.METALLO),
    Target("ARO:3006891", "afm-2-aro3006891.yaml", GraphKind.METALLO),
    Target("ARO:3008070", "afm-3-aro3008070.yaml", GraphKind.METALLO),
    Target("ARO:3008071", "afm-4-aro3008071.yaml", GraphKind.METALLO),
    Target("ARO:3008072", "afm-5-aro3008072.yaml", GraphKind.METALLO),
    Target("ARO:3005388", "afm-beta-lactamase-aro3005388.yaml", GraphKind.METALLO),
    Target("ARO:3006892", "alg11-1-aro3006892.yaml", GraphKind.METALLO),
    Target("ARO:3005389", "alg11-beta-lactamase-aro3005389.yaml", GraphKind.METALLO),
    Target("ARO:3006893", "alg6-1-aro3006893.yaml", GraphKind.METALLO),
    Target("ARO:3005390", "alg6-beta-lactamases-aro3005390.yaml", GraphKind.METALLO),
    Target("ARO:3006894", "ali-1-aro3006894.yaml", GraphKind.METALLO),
    Target("ARO:3006895", "ali-2-aro3006895.yaml", GraphKind.METALLO),
    Target("ARO:3005391", "ali-beta-lactamase-aro3005391.yaml", GraphKind.METALLO),
    Target("ARO:3006896", "ana-1-aro3006896.yaml", GraphKind.METALLO),
    Target("ARO:3005392", "ana-beta-lactamase-aro3005392.yaml", GraphKind.METALLO),
    Target("ARO:3002993", "aqu-1-aro3002993.yaml", GraphKind.CLASS_A),
    Target("ARO:3004647", "aqu-2-aro3004647.yaml", GraphKind.CLASS_A),
    Target("ARO:3004648", "aqu-3-aro3004648.yaml", GraphKind.CLASS_A),
    Target("ARO:3002992", "aqu-beta-lactamase-aro3002992.yaml", GraphKind.CLASS_A),
    Target("ARO:3004734", "arl-1-aro3004734.yaml", GraphKind.CLASS_A),
    Target("ARO:3004735", "arl-2-aro3004735.yaml", GraphKind.CLASS_A),
    Target("ARO:3004736", "arl-3-aro3004736.yaml", GraphKind.CLASS_A),
    Target("ARO:3004737", "arl-4-aro3004737.yaml", GraphKind.CLASS_A),
    Target("ARO:3004738", "arl-5-aro3004738.yaml", GraphKind.CLASS_A),
    Target("ARO:3004739", "arl-6-aro3004739.yaml", GraphKind.CLASS_A),
    Target("ARO:3004742", "arl-beta-lactamase-aro3004742.yaml", GraphKind.CLASS_A),
    Target("ARO:3008074", "asu1-1-aro3008074.yaml", GraphKind.CLASS_A),
    Target("ARO:3007863", "asu1-beta-lactamase-aro3007863.yaml", GraphKind.CLASS_A),
    Target("ARO:3006897", "axc-1-aro3006897.yaml", GraphKind.CLASS_A),
    Target("ARO:3006898", "axc-2-aro3006898.yaml", GraphKind.CLASS_A),
    Target("ARO:3006899", "axc-3-aro3006899.yaml", GraphKind.CLASS_A),
    Target("ARO:3006900", "axc-4-aro3006900.yaml", GraphKind.CLASS_A),
    Target("ARO:3006901", "axc-5-aro3006901.yaml", GraphKind.CLASS_A),
    Target("ARO:3008075", "axc-6-aro3008075.yaml", GraphKind.CLASS_A),
    Target("ARO:3008076", "axc-7-aro3008076.yaml", GraphKind.CLASS_A),
    Target("ARO:3008077", "axc-8-aro3008077.yaml", GraphKind.CLASS_A),
    Target("ARO:3005393", "axc-beta-lactamase-aro3005393.yaml", GraphKind.CLASS_A),
    Target("ARO:3008078", "b3su1-1-aro3008078.yaml", GraphKind.METALLO),
    Target("ARO:3007864", "b3su1-beta-lactamase-aro3007864.yaml", GraphKind.METALLO),
    Target("ARO:3008079", "b3su2-1-aro3008079.yaml", GraphKind.METALLO),
    Target("ARO:3007865", "b3su2-beta-lactamase-aro3007865.yaml", GraphKind.METALLO),
)
TARGET_BY_ID = {target.identifier: target for target in TARGETS}


@dataclass(frozen=True)
class GraphParts:
    title: str
    mech1_node: dict[str, str]
    catalytic_node_id: str
    catalytic_node: dict[str, str]
    fold_node: dict[str, str]
    family_evidence: dict[str, str]
    mechanism_evidence: dict[str, str]
    reaction_evidence: dict[str, str]
    catalytic_evidence: dict[str, str]
    fold_evidence: dict[str, str]
    catalytic_predicate: str
    catalytic_description: str


CLASS_A_PARTS = GraphParts(
    title="class A serine beta-lactam hydrolysis",
    mech1_node=SERINE_MECH1_NODE,
    catalytic_node_id="active_site",
    catalytic_node=CLASS_A_ACTIVE_SITE_NODE,
    fold_node=SERINE_FOLD_NODE,
    family_evidence=CLASS_A_EVIDENCE,
    mechanism_evidence=SERINE_BETA_LACTAMASE_EVIDENCE,
    reaction_evidence=SERINE_REACTION_EVIDENCE,
    catalytic_evidence=PROSITE_CLASS_A_EVIDENCE,
    fold_evidence=CATH_SERINE_BETA_LACTAMASE_EVIDENCE,
    catalytic_predicate="enables (serine beta-lactam hydrolysis)",
    catalytic_description=(
        "The class A S-x-x-K active site provides the catalytic serine used for "
        "beta-lactam acylation and hydrolysis."
    ),
)

CLASS_C_PARTS = GraphParts(
    title="class C serine beta-lactam hydrolysis",
    mech1_node=SERINE_MECH1_NODE,
    catalytic_node_id="active_site",
    catalytic_node=CLASS_C_ACTIVE_SITE_NODE,
    fold_node=SERINE_FOLD_NODE,
    family_evidence=CLASS_C_EVIDENCE,
    mechanism_evidence=SERINE_BETA_LACTAMASE_EVIDENCE,
    reaction_evidence=CLASS_C_REACTION_EVIDENCE,
    catalytic_evidence=PROSITE_CLASS_C_EVIDENCE,
    fold_evidence=CATH_SERINE_BETA_LACTAMASE_EVIDENCE,
    catalytic_predicate="enables (serine beta-lactam hydrolysis)",
    catalytic_description=(
        "The class C S-x-x-K active site provides the catalytic serine used "
        "for beta-lactam acylation and hydrolysis."
    ),
)

METALLO_PARTS = GraphParts(
    title="metallo-beta-lactamase zinc-dependent hydrolysis",
    mech1_node=METALLO_MECH1_NODE,
    catalytic_node_id="domain",
    catalytic_node=MBL_DOMAIN_NODE,
    fold_node=MBL_FOLD_NODE,
    family_evidence=BETA_LACTAMASE_EVIDENCE,
    mechanism_evidence=METALLO_BETA_LACTAMASE_EVIDENCE,
    reaction_evidence=MBL_REACTION_EVIDENCE,
    catalytic_evidence=PFAM_MBL_EVIDENCE,
    fold_evidence=CATH_MBL_EVIDENCE,
    catalytic_predicate="enables (zinc-dependent beta-lactam hydrolysis)",
    catalytic_description=(
        "The metallo-beta-lactamase domain binds catalytic zinc that orients "
        "the hydroxide nucleophile for beta-lactam hydrolysis."
    ),
)


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


def _edge_key(edge: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(edge.get("subject", "")),
        str(edge.get("predicate_id", "")),
        str(edge.get("object", "")),
    )


def _is_drug_node_id(node_id: str) -> bool:
    return DRUG_ID.fullmatch(node_id) is not None


def _drug_sort_key(node: dict[str, Any]) -> int:
    match = DRUG_ID.fullmatch(str(node["node_id"]))
    if match is None:
        raise ValueError(f"unexpected drug node_id: {node['node_id']}")
    return int(str(node["node_id"])[len("drug") :])


def _unique_evidence(*items: dict[str, Any]) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for item in items:
        key = (str(item["reference"]), str(item.get("snippet", "")))
        if key in seen:
            continue
        seen.add(key)
        evidence.append(copy.deepcopy(item))
    return evidence


def _edge(
    subject: str,
    predicate: str,
    predicate_id: str,
    object_: str,
    description: str,
    *evidence: dict[str, Any],
) -> dict[str, Any]:
    return {
        "subject": subject,
        "predicate": predicate,
        "predicate_id": predicate_id,
        "object": object_,
        "description": description,
        "evidence": _unique_evidence(*evidence),
    }


def _record_evidence(record: dict[str, Any]) -> dict[str, str]:
    return {
        "reference": str(record["identifier"]),
        "snippet": str(record["definition"]),
        "notes": f"CARD definition for {record['label']}.",
    }


def _determinant_node(record: dict[str, Any]) -> dict[str, str]:
    return {
        "node_id": "determinant",
        "label": str(record["label"]),
        "node_type": "PROTEIN",
        "grounding": str(record["identifier"]),
    }


def _nodes_by_id(graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(node["node_id"]): node
        for node in _dicts(graph.get("nodes"))
        if "node_id" in node
    }


def _drug_nodes(graph: dict[str, Any]) -> list[dict[str, Any]]:
    drug_nodes = [
        node
        for node in _dicts(graph.get("nodes"))
        if _is_drug_node_id(str(node.get("node_id", "")))
    ]
    if not drug_nodes:
        raise ValueError("missing drug node")
    return [copy.deepcopy(node) for node in sorted(drug_nodes, key=_drug_sort_key)]


def _drug_relation_evidence(
    graph: dict[str, Any],
    drug_node_ids: set[str],
) -> dict[str, list[dict[str, Any]]]:
    by_object: dict[str, list[dict[str, Any]]] = {node_id: [] for node_id in drug_node_ids}
    for edge in _dicts(graph.get("edges")):
        if (
            edge.get("subject") == "determinant"
            and edge.get("predicate_id") == "ARO:2000001"
        ):
            object_ = str(edge.get("object", ""))
            if object_ in by_object:
                by_object[object_].extend(
                    item
                    for item in _dicts(edge.get("evidence"))
                    if str(item.get("snippet", "")).startswith(
                        "relationship: confers_resistance_to_drug_class "
                    )
                )
    return by_object


def _core_edge_keys(catalytic_node_id: str) -> set[tuple[str, str, str]]:
    return {
        ("determinant", "RO:0000056", "mech0"),
        ("mech0", "RO:0002411", "resistance"),
        ("determinant", "RO:0000056", "mech1"),
        ("mech1", "RO:0002411", "resistance"),
        ("determinant", "RO:0002411", "resistance"),
        (catalytic_node_id, "BFO:0000050", "determinant"),
        ("determinant", "RO:0002350", "fold"),
        (catalytic_node_id, "RO:0002327", "mech1"),
    }


def _validate_graph(graph: dict[str, Any], target: Target, parts: GraphParts) -> None:
    nodes = _nodes_by_id(graph)
    drug_node_ids = {node_id for node_id in nodes if _is_drug_node_id(node_id)}
    required_nodes = {
        "determinant",
        "mech0",
        "mech1",
        parts.catalytic_node_id,
        "fold",
        "resistance",
    }
    missing_nodes = sorted(required_nodes - set(nodes))
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")
    if not drug_node_ids:
        raise ValueError(f"{target.identifier}: missing drug node(s)")

    seen: set[tuple[str, str, str]] = set()
    found: set[tuple[str, str, str]] = set()
    direct_drug_edges: set[str] = set()
    core_edge_keys = _core_edge_keys(parts.catalytic_node_id)
    for edge in _dicts(graph.get("edges")):
        key = _edge_key(edge)
        subject, predicate_id, object_ = key
        direct_drug_edge = (
            subject == "determinant"
            and predicate_id == "ARO:2000001"
            and object_ in drug_node_ids
        )
        if key not in core_edge_keys and not direct_drug_edge:
            raise ValueError(f"{target.identifier}: unexpected edge {subject} -> {object_}")
        if key in seen:
            raise ValueError(f"{target.identifier}: duplicate edge {subject} -> {object_}")
        seen.add(key)
        found.add(key)
        if direct_drug_edge:
            direct_drug_edges.add(object_)

    missing_edges = sorted(core_edge_keys - found)
    if missing_edges:
        missing = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in missing_edges)
        raise ValueError(f"{target.identifier}: missing edge(s): {missing}")

    missing_drug_edges = sorted(drug_node_ids - direct_drug_edges)
    if missing_drug_edges:
        missing = ", ".join(missing_drug_edges)
        raise ValueError(f"{target.identifier}: missing drug edge(s): {missing}")


def _validate_record(record: dict[str, Any], target: Target, parts: GraphParts) -> None:
    if record.get("identifier") != target.identifier:
        raise ValueError(
            f"{target.filename}: expected {target.identifier}, "
            f"found {record.get('identifier')}"
        )
    if not record.get("label"):
        raise ValueError(f"{target.identifier}: missing label")
    if not record.get("definition"):
        raise ValueError(f"{target.identifier}: missing definition")

    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1 or graphs[0].get("graph_id") != "resistance":
        raise ValueError(f"{target.identifier}: expected exactly one resistance graph")
    _validate_graph(graphs[0], target, parts)


def _canonical_drug_edges(
    record: dict[str, Any],
    old_graph: dict[str, Any],
    parts: GraphParts,
) -> list[dict[str, Any]]:
    drug_nodes = _drug_nodes(old_graph)
    drug_node_ids = {str(node["node_id"]) for node in drug_nodes}
    relation_evidence = _drug_relation_evidence(old_graph, drug_node_ids)

    return [
        _edge(
            "determinant",
            "confers resistance to (drug class)",
            "ARO:2000001",
            str(drug_node["node_id"]),
            f"CARD asserts that this determinant confers resistance to {drug_node['label']}.",
            *relation_evidence[str(drug_node["node_id"])],
            _record_evidence(record),
            parts.family_evidence,
            BETA_LACTAMASE_EVIDENCE,
            ANTIBIOTIC_INACTIVATION_EVIDENCE,
        )
        for drug_node in drug_nodes
    ]


def _graph(record: dict[str, Any], old_graph: dict[str, Any], parts: GraphParts) -> dict[str, Any]:
    record_evidence = _record_evidence(record)
    common_evidence = (
        record_evidence,
        INACTIVATION_ENZYME_EVIDENCE,
        ANTIBIOTIC_INACTIVATION_EVIDENCE,
        BETA_LACTAMASE_EVIDENCE,
        parts.family_evidence,
        parts.reaction_evidence,
    )
    specific_evidence = (
        record_evidence,
        BETA_LACTAMASE_EVIDENCE,
        parts.family_evidence,
        parts.mechanism_evidence,
        parts.reaction_evidence,
    )
    catalytic_evidence = (
        record_evidence,
        parts.family_evidence,
        parts.catalytic_evidence,
        parts.reaction_evidence,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → {parts.title}",
        "description": (
            "Curated resistance-causation graph for beta-lactamase antibiotic "
            "inactivation. The determinant participates in broad antibiotic "
            "inactivation and in a narrower beta-lactam hydrolysis mechanism "
            "through a grounded catalytic feature and fold."
        ),
        "nodes": [
            _determinant_node(record),
            copy.deepcopy(MECH0_NODE),
            copy.deepcopy(parts.mech1_node),
            *_drug_nodes(old_graph),
            copy.deepcopy(parts.catalytic_node),
            copy.deepcopy(parts.fold_node),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "CARD classifies this enzyme under antibiotic inactivation.",
                *common_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Beta-lactamase antibiotic inactivation opens the beta-lactam "
                "ring and thereby causes resistance.",
                *common_evidence,
            ),
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech1",
                "CARD classifies this enzyme under a narrower beta-lactam "
                "hydrolysis mechanism.",
                *specific_evidence,
            ),
            _edge(
                "mech1",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "The narrower beta-lactamase hydrolysis mechanism opens the "
                "beta-lactam ring and renders the antibiotic inactive.",
                *specific_evidence,
                ANTIBIOTIC_INACTIVATION_EVIDENCE,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "The determinant hydrolyzes and inactivates beta-lactam "
                "antibiotics.",
                *common_evidence,
                parts.mechanism_evidence,
            ),
            *_canonical_drug_edges(record, old_graph, parts),
            _edge(
                parts.catalytic_node_id,
                "part of",
                "BFO:0000050",
                "determinant",
                "The grounded catalytic feature is part of the beta-lactamase "
                "determinant.",
                *catalytic_evidence,
            ),
            _edge(
                "determinant",
                "member of",
                "RO:0002350",
                "fold",
                "The determinant adopts the grounded fold associated with this "
                "beta-lactamase family.",
                record_evidence,
                parts.family_evidence,
                parts.fold_evidence,
                parts.reaction_evidence,
            ),
            _edge(
                parts.catalytic_node_id,
                parts.catalytic_predicate,
                "RO:0002327",
                "mech1",
                parts.catalytic_description,
                *catalytic_evidence,
                parts.mechanism_evidence,
            ),
        ],
    }


def _parts(target: Target) -> GraphParts:
    if target.kind == GraphKind.CLASS_A:
        return CLASS_A_PARTS
    if target.kind == GraphKind.CLASS_C:
        return CLASS_C_PARTS
    if target.kind == GraphKind.METALLO:
        return METALLO_PARTS
    raise ValueError(f"{target.identifier}: unhandled graph kind {target.kind}")


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    parts = _parts(target)
    _validate_record(record, target, parts)

    out = copy.deepcopy(record)
    out["causal_graphs"] = [_graph(record, record["causal_graphs"][0], parts)]
    return out, out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not an early beta-lactamase target: {identifier}")
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
        help="ARO directory or one of the 43 early beta-lactamase YAML files",
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
