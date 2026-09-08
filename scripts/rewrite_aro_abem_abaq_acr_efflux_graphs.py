#!/usr/bin/env python3
"""Rewrite low-scoring AbeM/AbaQ/AbuO/Acr efflux ARO causal graphs.

These exact rank-77 records still have promoted efflux graphs with mostly
single-reference, undescribed edges. They split across MATE, MFS, complete RND,
and TolC-like outer-membrane-channel models, but every record has a useful
CARD determinant-to-drug-class edge that should be preserved.

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
    "action": "Completed AbeM/AbaQ/AbuO/Acr efflux causal graphs",
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

EFFLUX_SUBUNIT_EVIDENCE = {
    "reference": "ARO:3000748",
    "snippet": "Subunits of efflux proteins that pump antibiotic out of a cell to confer resistance.",
    "notes": "CARD definition for efflux pump subunits.",
}

MATE_EVIDENCE = {
    "reference": "ARO:3000112",
    "snippet": (
        "Multidrug and toxic compound extrusion (MATE) transporters utilize "
        "the cationic gradient across the membrane as an energy source."
    ),
    "notes": "CARD definition for MATE transporters.",
}

MATE_SUBSTRATE_EVIDENCE = {
    "reference": "ARO:3000112",
    "snippet": (
        "Although there is a diverse substrate specificity, almost all MATE "
        "transporters recognize fluoroquinolones."
    ),
    "notes": "CARD definition for MATE antibiotic substrates.",
}

MFS_EVIDENCE = {
    "reference": "ARO:0010002",
    "snippet": (
        "Directed pumping of antibiotic out of a cell to confer resistance. "
        "Major facilitator superfamily (MFS) transporters and ABC "
        "transporters comprise the two largest and most functionally diverse "
        "of the transporter superfamilies. However, MFS transporters are "
        "distinct from ABC transporters in both their primary sequence and "
        "structure and in the mechanism of energy coupling. As secondary "
        "transporters they are, like RND and SMR transporters, energized by "
        "the electrochemical proton gradient."
    ),
    "notes": "CARD definition for MFS antibiotic efflux pumps.",
}

MFS_TRANSPORT_EVIDENCE = {
    "reference": "PMID:38974671",
    "snippet": (
        "The antimicrobial antiport transport cycle in bacteria is driven by "
        "the ion-motive force, an energy mode associated with changes in "
        "transporter conformations and gating during efflux across the "
        "membrane."
    ),
    "notes": "Evidence for ion-motive-force-driven MFS efflux.",
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

RND_EVIDENCE = {
    "reference": "ARO:0010004",
    "snippet": (
        "Directed pumping of antibiotic out of a cell to confer resistance. "
        "Resistance-nodulation-division (RND) proteins are found in both "
        "prokaryotic and eukaryotic cells and have diverse substrate "
        "specificities and physiological roles."
    ),
    "notes": "CARD definition for RND antibiotic efflux pumps.",
}

RND_TRANSPORT_EVIDENCE = {
    "reference": "PMID:16915237",
    "snippet": (
        "The structures indicate that drugs are exported by a three-step "
        "functionally rotating mechanism in which substrates undergo ordered "
        "binding change."
    ),
    "notes": "Evidence for RND pump-mediated drug export.",
}

RND_COMPLEX_EVIDENCE = {
    "reference": "PMID:16915237",
    "snippet": (
        "AcrB is a principal multidrug efflux transporter in Escherichia coli "
        "that cooperates with an outer-membrane channel, TolC, and a "
        "membrane-fusion protein, AcrA."
    ),
    "notes": "Evidence for a tripartite RND pump architecture.",
}

RND_DOMAIN_EVIDENCE = {
    "reference": "Pfam:PF00873",
    "snippet": "AcrB/AcrD/AcrF family",
    "notes": "Pfam family for RND transporter domains.",
}

RND_FOLD_EVIDENCE = {
    "reference": "CATH:3.30.70.1430",
    "snippet": "Multidrug efflux transporter AcrB pore domain",
    "notes": "CATH fold for the AcrB pore domain.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "antibiotic efflux",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:0010000",
}

MFS_DOMAIN_NODE = {
    "node_id": "domain",
    "label": "major facilitator superfamily (MFS) transporter domain",
    "node_type": "DOMAIN",
    "grounding": "Pfam:PF07690",
    "description": "Transporter domain shared by MFS antibiotic efflux pumps.",
}

MFS_FOLD_NODE = {
    "node_id": "fold",
    "label": "MFS general substrate transporter fold",
    "node_type": "DOMAIN",
    "grounding": "CATH:1.20.1250.20",
    "description": "Fold adopted by MFS general substrate transporter-like domains.",
}

RND_DOMAIN_NODE = {
    "node_id": "domain",
    "label": "RND transporter domain (AcrB/AcrD/AcrF family)",
    "node_type": "DOMAIN",
    "grounding": "Pfam:PF00873",
    "description": "Transporter domain used by RND antibiotic efflux pumps.",
}

RND_FOLD_NODE = {
    "node_id": "fold",
    "label": "AcrB pore-domain fold",
    "node_type": "DOMAIN",
    "grounding": "CATH:3.30.70.1430",
    "description": "Pore-domain fold used by RND antibiotic efflux pumps.",
}

CATION_GRADIENT_NODE = {
    "node_id": "cation_gradient",
    "label": "transmembrane cationic gradient",
    "node_type": "STATE",
    "description": (
        "Local state for the cationic gradient that powers MATE-family drug "
        "antiport. The ion is kept generic because CARD does not specialize "
        "the family to proton or sodium coupling."
    ),
}

TRANSPORTER_NODE = {
    "node_id": "transporter",
    "label": "TolC-like tripartite efflux complex",
    "node_type": "STATE",
    "description": (
        "Local state for a Gram-negative tripartite efflux pump using this "
        "TolC-like outer-membrane subunit as its channel."
    ),
}

EXPORT_NODE = {
    "node_id": "export",
    "label": "xenobiotic detoxification by transmembrane export across the plasma membrane",
    "node_type": "BIOLOGICAL_PROCESS",
    "grounding": "GO:1990961",
}

EXTRUDED_NODE = {
    "node_id": "extruded_drug",
    "label": "drug outside the cell",
    "node_type": "STATE",
    "description": "Local state for drug exported from the cytoplasm by a MATE transporter.",
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
    MATE = "MATE"
    MFS = "MFS"
    RND = "RND"
    TOLC_LIKE = "TOLC_LIKE"


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    kind: GraphKind


TARGETS: tuple[Target, ...] = (
    Target("ARO:3000753", "abem-aro3000753.yaml", GraphKind.MATE),
    Target("ARO:3004574", "acinetobacter-baumannii-abaq-aro3004574.yaml", GraphKind.MFS),
    Target("ARO:3004578", "acinetobacter-baumannii-abuo-aro3004578.yaml", GraphKind.TOLC_LIKE),
    Target("ARO:3000384", "acrab-tolc-aro3000384.yaml", GraphKind.RND),
    Target("ARO:3004082", "acrad-tolc-aro3004082.yaml", GraphKind.RND),
    Target("ARO:3000491", "acrd-aro3000491.yaml", GraphKind.RND),
)
TARGET_BY_ID = {target.identifier: target for target in TARGETS}


@dataclass(frozen=True)
class Family:
    title: str
    family_evidence: dict[str, str]
    transport_evidence: dict[str, str]
    domain_node: dict[str, str]
    fold_node: dict[str, str]
    domain_evidence: dict[str, str]
    fold_evidence: dict[str, str]
    efflux_predicate: str
    description: str


MFS_FAMILY = Family(
    title="MFS antibiotic efflux",
    family_evidence=MFS_EVIDENCE,
    transport_evidence=MFS_TRANSPORT_EVIDENCE,
    domain_node=MFS_DOMAIN_NODE,
    fold_node=MFS_FOLD_NODE,
    domain_evidence=MFS_DOMAIN_EVIDENCE,
    fold_evidence=MFS_FOLD_EVIDENCE,
    efflux_predicate="enables (ion-motive-force-driven drug efflux)",
    description=(
        "Curated resistance-causation graph for MFS antibiotic efflux pumps. "
        "The determinant enables ion-motive-force-driven export of antibiotics "
        "out of the cell, lowering intracellular drug exposure."
    ),
)

RND_FAMILY = Family(
    title="RND antibiotic efflux",
    family_evidence=RND_EVIDENCE,
    transport_evidence=RND_TRANSPORT_EVIDENCE,
    domain_node=RND_DOMAIN_NODE,
    fold_node=RND_FOLD_NODE,
    domain_evidence=RND_DOMAIN_EVIDENCE,
    fold_evidence=RND_FOLD_EVIDENCE,
    efflux_predicate="enables (proton-motive-force-driven drug efflux)",
    description=(
        "Curated resistance-causation graph for complete RND antibiotic efflux "
        "pumps. The graph links the RND transporter domain and AcrB "
        "pore-domain fold to the antibiotic efflux mechanism."
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


def _drug_relation_evidence(graph: dict[str, Any], drug_node_ids: set[str]) -> dict[str, list[dict]]:
    by_object: dict[str, list[dict]] = {node_id: [] for node_id in drug_node_ids}
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


def _validate_direct_drug_edges(graph: dict[str, Any], target: Target) -> None:
    nodes = _nodes_by_id(graph)
    drug_node_ids = {node_id for node_id in nodes if _is_drug_node_id(node_id)}
    if not drug_node_ids:
        raise ValueError(f"{target.identifier}: missing drug node(s)")

    seen: set[tuple[str, str, str]] = set()
    direct_drug_edges: set[str] = set()
    for edge in _dicts(graph.get("edges")):
        key = _edge_key(edge)
        if key in seen:
            subject, _, object_ = key
            raise ValueError(f"{target.identifier}: duplicate edge {subject} -> {object_}")
        seen.add(key)

        subject, predicate_id, object_ = key
        if (
            subject == "determinant"
            and predicate_id == "ARO:2000001"
            and object_ in drug_node_ids
        ):
            direct_drug_edges.add(object_)

    missing_drug_edges = sorted(drug_node_ids - direct_drug_edges)
    if missing_drug_edges:
        missing = ", ".join(missing_drug_edges)
        raise ValueError(f"{target.identifier}: missing drug edge(s): {missing}")


def _validate_record(record: dict[str, Any], target: Target) -> None:
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
    _validate_direct_drug_edges(graphs[0], target)


def _canonical_drug_edges(
    record: dict[str, Any],
    old_graph: dict[str, Any],
    *evidence: dict[str, Any],
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
            *evidence,
        )
        for drug_node in drug_nodes
    ]


def _drug_input_edges(
    old_graph: dict[str, Any],
    *evidence: dict[str, Any],
) -> list[dict[str, Any]]:
    drug_nodes = _drug_nodes(old_graph)
    drug_node_ids = {str(node["node_id"]) for node in drug_nodes}
    relation_evidence = _drug_relation_evidence(old_graph, drug_node_ids)

    return [
        _edge(
            "export",
            "has input (the drug)",
            "RO:0002233",
            str(drug_node["node_id"]),
            f"The efflux process exports this CARD-linked {drug_node['label']} class.",
            *evidence,
            *relation_evidence[str(drug_node["node_id"])],
        )
        for drug_node in drug_nodes
    ]


def _domain_fold_graph(
    record: dict[str, Any],
    old_graph: dict[str, Any],
    family: Family,
) -> dict[str, Any]:
    record_evidence = _record_evidence(record)
    efflux_evidence = (
        record_evidence,
        family.family_evidence,
        EFFLUX_PUMP_EVIDENCE,
        ANTIBIOTIC_EFFLUX_EVIDENCE,
        family.transport_evidence,
    )
    domain_evidence = (
        record_evidence,
        family.family_evidence,
        family.domain_evidence,
        family.transport_evidence,
    )
    fold_evidence = (
        record_evidence,
        family.family_evidence,
        family.fold_evidence,
        family.transport_evidence,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → {family.title} → resistance",
        "description": family.description,
        "nodes": [
            _determinant_node(record),
            copy.deepcopy(MECHANISM_NODE),
            *_drug_nodes(old_graph),
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
                "Antibiotic efflux confers resistance by transporting "
                "antibiotics out of the cell.",
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
            *_canonical_drug_edges(
                record,
                old_graph,
                family.family_evidence,
                EFFLUX_PUMP_EVIDENCE,
                ANTIBIOTIC_EFFLUX_EVIDENCE,
            ),
            _edge(
                "domain",
                "part of",
                "BFO:0000050",
                "determinant",
                "The transporter domain is part of the resistance determinant.",
                *domain_evidence,
            ),
            _edge(
                "determinant",
                "member of",
                "RO:0002350",
                "fold",
                "The determinant adopts the transporter fold associated with "
                "this efflux-pump family.",
                *fold_evidence,
            ),
            _edge(
                "domain",
                family.efflux_predicate,
                "RO:0002327",
                "mech0",
                "The transporter domain enables family-specific antibiotic export.",
                *domain_evidence,
            ),
        ],
    }


def _mate_graph(record: dict[str, Any], old_graph: dict[str, Any]) -> dict[str, Any]:
    record_evidence = _record_evidence(record)
    efflux_evidence = (
        record_evidence,
        MATE_EVIDENCE,
        EFFLUX_PUMP_EVIDENCE,
        ANTIBIOTIC_EFFLUX_EVIDENCE,
    )
    export_evidence = (
        record_evidence,
        MATE_EVIDENCE,
        ANTIBIOTIC_EFFLUX_EVIDENCE,
        MATE_SUBSTRATE_EVIDENCE,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → MATE cation-gradient efflux → resistance",
        "description": (
            "Curated resistance-causation graph for MATE antibiotic efflux "
            "pumps. The determinant uses a generic transmembrane cationic "
            "gradient to export antibiotic from the cell."
        ),
        "nodes": [
            _determinant_node(record),
            copy.deepcopy(MECHANISM_NODE),
            *_drug_nodes(old_graph),
            copy.deepcopy(CATION_GRADIENT_NODE),
            copy.deepcopy(EXPORT_NODE),
            copy.deepcopy(EXTRUDED_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "CARD classifies MATE pumps under the antibiotic efflux "
                "resistance mechanism.",
                *efflux_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Antibiotic efflux confers resistance by transporting "
                "antibiotics out of the cell.",
                *efflux_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "MATE transporters confer resistance by cation-gradient-driven "
                "antibiotic efflux.",
                *efflux_evidence,
            ),
            *_canonical_drug_edges(
                record,
                old_graph,
                MATE_EVIDENCE,
                EFFLUX_PUMP_EVIDENCE,
                ANTIBIOTIC_EFFLUX_EVIDENCE,
                MATE_SUBSTRATE_EVIDENCE,
            ),
            _edge(
                "cation_gradient",
                "causally upstream of (drives efflux)",
                "RO:0002411",
                "export",
                "A transmembrane cationic gradient powers MATE-family drug "
                "antiport across the membrane.",
                *export_evidence,
                EFFLUX_PUMP_EVIDENCE,
            ),
            _edge(
                "determinant",
                "causally upstream of",
                "RO:0002411",
                "export",
                "The MATE transporter exports drug from the cell.",
                *efflux_evidence,
                MATE_SUBSTRATE_EVIDENCE,
            ),
            *_drug_input_edges(old_graph, *export_evidence),
            _edge(
                "export",
                "causally upstream of (moves drug out of the cell)",
                "RO:0002411",
                "extruded_drug",
                "Antibiotic export moves intracellular drug outside the cell.",
                *export_evidence,
            ),
            _edge(
                "extruded_drug",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Moving drug outside the cell lowers intracellular drug "
                "exposure and causes the modeled resistance phenotype.",
                *efflux_evidence,
                MATE_SUBSTRATE_EVIDENCE,
            ),
        ],
    }


def _tolc_like_graph(record: dict[str, Any], old_graph: dict[str, Any]) -> dict[str, Any]:
    record_evidence = _record_evidence(record)
    efflux_evidence = (
        record_evidence,
        EFFLUX_SUBUNIT_EVIDENCE,
        RND_EVIDENCE,
        EFFLUX_PUMP_EVIDENCE,
        ANTIBIOTIC_EFFLUX_EVIDENCE,
        RND_COMPLEX_EVIDENCE,
    )
    complex_evidence = (
        record_evidence,
        EFFLUX_SUBUNIT_EVIDENCE,
        RND_EVIDENCE,
        RND_COMPLEX_EVIDENCE,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → TolC-like tripartite efflux complex → resistance",
        "description": (
            "Curated resistance-causation graph for a TolC-like "
            "outer-membrane efflux channel. The determinant is modeled as "
            "part of a local tripartite efflux complex, not as the "
            "inner-membrane RND transporter itself."
        ),
        "nodes": [
            _determinant_node(record),
            copy.deepcopy(MECHANISM_NODE),
            *_drug_nodes(old_graph),
            copy.deepcopy(TRANSPORTER_NODE),
            copy.deepcopy(EXPORT_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "CARD classifies this TolC-like efflux subunit under the "
                "antibiotic efflux resistance mechanism.",
                *efflux_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Antibiotic efflux confers resistance by transporting "
                "antibiotics out of the cell.",
                *efflux_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "The TolC-like outer-membrane subunit contributes to efflux "
                "complexes that pump antibiotic out of the cell.",
                *efflux_evidence,
            ),
            *_canonical_drug_edges(
                record,
                old_graph,
                EFFLUX_SUBUNIT_EVIDENCE,
                RND_EVIDENCE,
                EFFLUX_PUMP_EVIDENCE,
                ANTIBIOTIC_EFFLUX_EVIDENCE,
            ),
            _edge(
                "determinant",
                "part of",
                "BFO:0000050",
                "transporter",
                "The determinant is a TolC-like outer-membrane subunit of the "
                "modeled tripartite efflux complex.",
                *complex_evidence,
            ),
            _edge(
                "transporter",
                "causally upstream of",
                "RO:0002411",
                "export",
                "The complete tripartite efflux pump exports antibiotics from "
                "the cell.",
                *efflux_evidence,
            ),
            *_drug_input_edges(old_graph, *efflux_evidence),
            _edge(
                "export",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Antibiotic export lowers intracellular drug exposure and "
                "causes the modeled resistance phenotype.",
                *efflux_evidence,
            ),
        ],
    }


def _graph(record: dict[str, Any], old_graph: dict[str, Any], target: Target) -> dict[str, Any]:
    if target.kind == GraphKind.MATE:
        return _mate_graph(record, old_graph)
    if target.kind == GraphKind.MFS:
        return _domain_fold_graph(record, old_graph, MFS_FAMILY)
    if target.kind == GraphKind.RND:
        return _domain_fold_graph(record, old_graph, RND_FAMILY)
    if target.kind == GraphKind.TOLC_LIKE:
        return _tolc_like_graph(record, old_graph)
    raise ValueError(f"{target.identifier}: unhandled graph kind {target.kind}")


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    _validate_record(record, target)

    out = copy.deepcopy(record)
    out["causal_graphs"] = [_graph(record, record["causal_graphs"][0], target)]
    return out, out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not an AbeM/AbaQ/AbuO/Acr efflux target: {identifier}")
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
        help="ARO directory or one of the 6 AbeM/AbaQ/AbuO/Acr efflux YAML files",
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
