#!/usr/bin/env python3
"""Rewrite aminoglycoside acetyltransferase AAC ARO causal graphs.

The promoted AAC graphs ground the ARO aminoglycoside-acetylation mechanisms,
GNAT domain, and GNAT fold, but they still stop at the ARO mechanism nodes:
they omit the acetyl-CoA donor, the acetyltransferase reaction, and the
acetylated inactive drug state that explain how acylation causes resistance.

This updater rewrites the exact rank-77 plain AAC records to an
acetyl-CoA-dependent N-acetylation model and preserves every existing
determinant-to-drug-class edge, so related AAC(6')-Ib-cr graphs with a second
fluoroquinolone drug edge can be handled by the same graph builder.

Dry-run by default; pass ``--apply`` to write.
"""

from __future__ import annotations

import argparse
import copy
import re
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
    "timestamp": "2026-09-07T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": "Completed AAC aminoglycoside acetyltransferase causal graphs",
    "llm_assisted": True,
}

INACTIVATION_EVIDENCE = {
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

ACYLATION_EVIDENCE = {
    "reference": "ARO:3000106",
    "snippet": "Addition of an acyl group to an antibiotic, often via acetylation by acetylCoA.",
    "notes": "CARD definition for acylation of antibiotic conferring resistance.",
}

AAC_PARENT_EVIDENCE = {
    "reference": "ARO:3000121",
    "snippet": (
        "Aminoglycoside acetyltransferase enzymes modify aminoglycoside "
        "antibiotics by catalyzing the transfer of an acetyl group to one of "
        "the amino groups present in aminoglycosides, using acetyl coenzyme A "
        "as a donor substrate."
    ),
    "notes": "CARD definition for aminoglycoside acetyltransferase (AAC).",
}

AMINOGLYCOSIDE_MODIFYING_EVIDENCE = {
    "reference": "ARO:3007380",
    "snippet": (
        "Resistance-conferring genetic elements encoding proteins involved in "
        "the enzymatic inactivation of aminoglycoside antibiotics through "
        "chemical modification."
    ),
    "notes": "CARD definition for aminoglycoside-modifying enzymes.",
}

GNAT_REVIEW_EVIDENCE = {
    "reference": "PMID:26818562",
    "snippet": (
        "N-Acetyltransferases transfer an acetyl group from acetyl-CoA to a "
        "large array of substrates, from small molecules such as "
        "aminoglycoside antibiotics to macromolecules."
    ),
    "notes": "Literature support for GNAT-mediated acetyl transfer to aminoglycosides.",
}

GO_ACETYLTRANSFERASE_EVIDENCE = {
    "reference": "GO:0016407",
    "snippet": "Catalysis of the transfer of an acetyl group to an acceptor molecule.",
    "notes": "GO grounding for the broad acetyltransferase activity node.",
}

ACETYL_COA_EVIDENCE = {
    "reference": "CHEBI:15351",
    "snippet": "Acetyl-CoA is an acyl-CoA having acetyl as its S-acetyl component.",
    "notes": "ChEBI grounding for the acetyl-CoA input.",
}

INTERPRO_EVIDENCE = {
    "reference": "InterPro:IPR000182",
    "snippet": "GNAT domain",
    "notes": "InterPro grounding for the GNAT acetyltransferase domain.",
}

CATH_EVIDENCE = {
    "reference": "CATH:3.40.630",
    "snippet": "Aminopeptidase",
    "notes": "CATH grounding for the acyl-CoA N-acyltransferase fold.",
}

MECH0_NODE = {
    "node_id": "mech0",
    "label": "antibiotic inactivation",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:0001004",
}

MECH1_NODE = {
    "node_id": "mech1",
    "label": "acylation of antibiotic conferring resistance",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3000106",
}

TRANSFER_NODE = {
    "node_id": "transfer",
    "label": "acetyltransferase activity",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "GO:0016407",
    "description": (
        "Grounded to the broad GO acetyltransferase activity term and scoped "
        "here to acetyl-CoA-dependent antibiotic N-acetylation by AAC enzymes."
    ),
}

ACETYL_COA_NODE = {
    "node_id": "acetyl_coa",
    "label": "acetyl-CoA",
    "node_type": "CHEMICAL",
    "grounding": "CHEBI:15351",
}

ACETYLATED_NODE = {
    "node_id": "acetylated",
    "label": "acetylated inactive antibiotic",
    "node_type": "STATE",
    "description": (
        "Local state for an antibiotic after AAC-mediated acetyl transfer "
        "from acetyl-CoA."
    ),
}

DOMAIN_NODE = {
    "node_id": "domain",
    "label": "GNAT acetyltransferase domain",
    "node_type": "DOMAIN",
    "grounding": "InterPro:IPR000182",
    "description": "GNAT acetyltransferase catalytic domain found in AAC enzymes.",
}

FOLD_NODE = {
    "node_id": "fold",
    "label": "acyl-CoA N-acyltransferase (GNAT) fold",
    "node_type": "DOMAIN",
    "grounding": "CATH:3.40.630",
    "description": "GNAT acyltransferase structural fold.",
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

CORE_EDGE_KEYS = {
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0000056", "mech1"),
    ("mech1", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("domain", "BFO:0000050", "determinant"),
    ("determinant", "RO:0002350", "fold"),
}

LEGACY_EDGE_KEYS = {
    ("domain", "RO:0002327", "mech1"),
}

CANONICAL_EDGE_KEYS = {
    ("determinant", "RO:0002327", "transfer"),
    ("transfer", "RO:0002233", "acetyl_coa"),
    ("transfer", "RO:0002411", "acetylated"),
    ("acetylated", "RO:0002411", "resistance"),
    ("domain", "RO:0002327", "transfer"),
}

DRUG_ID = re.compile(r"^drug\d+$")


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str


_TARGET_ROWS = """
ARO:3000341 aac-2-aro3000341.yaml
ARO:3007393 aac-2-i-aro3007393.yaml
ARO:3002523 aac-2-ia-aro3002523.yaml
ARO:3002524 aac-2-ib-aro3002524.yaml
ARO:3002525 aac-2-ic-aro3002525.yaml
ARO:3002526 aac-2-id-aro3002526.yaml
ARO:3002527 aac-2-ie-aro3002527.yaml
ARO:3007394 aac-2-ii-aro3007394.yaml
ARO:3004628 aac-2-iia-aro3004628.yaml
ARO:3003988 aac-2-iib-aro3003988.yaml
ARO:3000322 aac-3-aro3000322.yaml
ARO:3007384 aac-3-i-aro3007384.yaml
ARO:3002528 aac-3-ia-aro3002528.yaml
ARO:3002530 aac-3-ib-aro3002530.yaml
ARO:3002531 aac-3-ic-aro3002531.yaml
ARO:3002529 aac-3-id-aro3002529.yaml
ARO:3007385 aac-3-ii-aro3007385.yaml
ARO:3002533 aac-3-iia-aro3002533.yaml
ARO:3002534 aac-3-iib-aro3002534.yaml
ARO:3002535 aac-3-iic-aro3002535.yaml
ARO:3004623 aac-3-iid-aro3004623.yaml
ARO:3004621 aac-3-iie-aro3004621.yaml
ARO:3005085 aac-3-iig-aro3005085.yaml
ARO:3007386 aac-3-iii-aro3007386.yaml
ARO:3002536 aac-3-iiia-aro3002536.yaml
ARO:3002537 aac-3-iiib-aro3002537.yaml
ARO:3002538 aac-3-iiic-aro3002538.yaml
ARO:3007387 aac-3-iv-aro3007387.yaml
ARO:3002539 aac-3-iva-aro3002539.yaml
ARO:3005061 aac-3-ivb-aro3005061.yaml
ARO:3007391 aac-3-ix-aro3007391.yaml
ARO:3002543 aac-3-ixa-aro3002543.yaml
ARO:3007388 aac-3-vi-aro3007388.yaml
ARO:3002540 aac-3-via-aro3002540.yaml
ARO:3007389 aac-3-vii-aro3007389.yaml
ARO:3002541 aac-3-viia-aro3002541.yaml
ARO:3007390 aac-3-viii-aro3007390.yaml
ARO:3002542 aac-3-viiia-aro3002542.yaml
ARO:3007392 aac-3-x-aro3007392.yaml
ARO:3002544 aac-3-xa-aro3002544.yaml
ARO:3002583 aac-6-29a-aro3002583.yaml
ARO:3002584 aac-6-29b-aro3002584.yaml
ARO:3002585 aac-6-31-aro3002585.yaml
ARO:3002586 aac-6-32-aro3002586.yaml
ARO:3003989 aac-6-34-aro3003989.yaml
ARO:3000345 aac-6-aro3000345.yaml
ARO:3004641 aac-6-i-43-aro3004641.yaml
ARO:3004638 aac-6-i-48-aro3004638.yaml
ARO:3007395 aac-6-i-aro3007395.yaml
ARO:3002588 aac-6-i30-aro3002588.yaml
ARO:3002587 aac-6-i33-aro3002587.yaml
ARO:3002545 aac-6-ia-aro3002545.yaml
ARO:3002571 aac-6-iaa-aro3002571.yaml
ARO:3002572 aac-6-iad-aro3002572.yaml
ARO:3002573 aac-6-iae-aro3002573.yaml
ARO:3002574 aac-6-iaf-aro3002574.yaml
ARO:3002575 aac-6-iai-aro3002575.yaml
ARO:3003677 aac-6-iaj-aro3003677.yaml
ARO:3003199 aac-6-iak-aro3003199.yaml
ARO:3003200 aac-6-ian-aro3003200.yaml
ARO:3007204 aac-6-iap-aro3007204.yaml
ARO:3002546 aac-6-ib-aro3002546.yaml
ARO:3003676 aac-6-ib-aro3003676.yaml
ARO:3002592 aac-6-ib-hangzhou-aro3002592.yaml
ARO:3002593 aac-6-ib-sk-aro3002593.yaml
ARO:3002591 aac-6-ib-suzhou-aro3002591.yaml
ARO:3002581 aac-6-ib10-aro3002581.yaml
ARO:3002582 aac-6-ib11-aro3002582.yaml
ARO:3002576 aac-6-ib3-aro3002576.yaml
ARO:3002577 aac-6-ib4-aro3002577.yaml
ARO:3002578 aac-6-ib7-aro3002578.yaml
ARO:3002579 aac-6-ib8-aro3002579.yaml
ARO:3002580 aac-6-ib9-aro3002580.yaml
ARO:3002549 aac-6-ic-aro3002549.yaml
ARO:3002553 aac-6-if-aro3002553.yaml
ARO:3002554 aac-6-ig-aro3002554.yaml
ARO:3002555 aac-6-ih-aro3002555.yaml
ARO:3002556 aac-6-ii-aro3002556.yaml
ARO:3007396 aac-6-ii-aro3007396.yaml
ARO:3002594 aac-6-iia-aro3002594.yaml
ARO:3002595 aac-6-iib-aro3002595.yaml
ARO:3002596 aac-6-iic-aro3002596.yaml
ARO:3002589 aac-6-iid-aro3002589.yaml
ARO:3002590 aac-6-iih-aro3002590.yaml
ARO:3002557 aac-6-ij-aro3002557.yaml
ARO:3002558 aac-6-ik-aro3002558.yaml
ARO:3004635 aac-6-il-aro3004635.yaml
ARO:3004629 aac-6-im-aro3004629.yaml
ARO:3002559 aac-6-ip-aro3002559.yaml
ARO:3002560 aac-6-iq-aro3002560.yaml
ARO:3002561 aac-6-ir-aro3002561.yaml
ARO:3002562 aac-6-is-aro3002562.yaml
ARO:3002563 aac-6-isa-aro3002563.yaml
ARO:3002564 aac-6-it-aro3002564.yaml
ARO:3002565 aac-6-iu-aro3002565.yaml
ARO:3002566 aac-6-iv-aro3002566.yaml
ARO:3002567 aac-6-iw-aro3002567.yaml
ARO:3002568 aac-6-ix-aro3002568.yaml
ARO:3002569 aac-6-iy-aro3002569.yaml
ARO:3002570 aac-6-iz-aro3002570.yaml
"""


TARGETS: tuple[Target, ...] = tuple(
    Target(identifier, filename)
    for identifier, filename in (line.split() for line in _TARGET_ROWS.strip().splitlines())
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
        reference = str(item["reference"])
        snippet = str(item.get("snippet", ""))
        key = (reference, snippet)
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


def _validate_graph(graph: dict[str, Any], target: Target) -> None:
    nodes = _nodes_by_id(graph)
    drug_node_ids = {node_id for node_id in nodes if _is_drug_node_id(node_id)}
    required_nodes = {"determinant", "mech0", "mech1", "domain", "fold", "resistance"}
    missing_nodes = sorted(required_nodes - set(nodes))
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")
    if not drug_node_ids:
        raise ValueError(f"{target.identifier}: missing drug node(s)")

    seen: set[tuple[str, str, str]] = set()
    found: set[tuple[str, str, str]] = set()
    direct_drug_edges: set[str] = set()
    for edge in _dicts(graph.get("edges")):
        key = _edge_key(edge)
        subject, predicate_id, object_ = key
        transfer_drug_edge = (
            subject == "transfer" and predicate_id == "RO:0002233" and object_ in drug_node_ids
        )
        direct_drug_edge = (
            subject == "determinant"
            and predicate_id == "ARO:2000001"
            and object_ in drug_node_ids
        )
        allowed = (
            key in CORE_EDGE_KEYS
            or key in LEGACY_EDGE_KEYS
            or key in CANONICAL_EDGE_KEYS
            or transfer_drug_edge
            or direct_drug_edge
        )
        if not allowed:
            raise ValueError(f"{target.identifier}: unexpected edge {subject} -> {object_}")
        if key in seen:
            raise ValueError(f"{target.identifier}: duplicate edge {subject} -> {object_}")
        seen.add(key)
        found.add(key)
        if direct_drug_edge:
            direct_drug_edges.add(object_)

    missing_edges = sorted(CORE_EDGE_KEYS - found)
    if missing_edges:
        missing = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in missing_edges)
        raise ValueError(f"{target.identifier}: missing edge(s): {missing}")

    missing_drug_edges = sorted(drug_node_ids - direct_drug_edges)
    if missing_drug_edges:
        missing = ", ".join(missing_drug_edges)
        raise ValueError(f"{target.identifier}: missing drug edge(s): {missing}")


def _canonical_drug_edge(
    record: dict[str, Any],
    drug_node: dict[str, Any],
    relation_evidence: list[dict[str, Any]],
) -> dict[str, Any]:
    drug_label = str(drug_node["label"])
    return _edge(
        "determinant",
        "confers resistance to (drug class)",
        "ARO:2000001",
        str(drug_node["node_id"]),
        f"CARD asserts that this AAC determinant confers resistance to {drug_label}.",
        *relation_evidence,
        _record_evidence(record),
        AAC_PARENT_EVIDENCE,
        AMINOGLYCOSIDE_MODIFYING_EVIDENCE,
    )


def _graph(record: dict[str, Any], old_graph: dict[str, Any]) -> dict[str, Any]:
    record_evidence = _record_evidence(record)
    common_evidence = (
        record_evidence,
        AAC_PARENT_EVIDENCE,
        AMINOGLYCOSIDE_MODIFYING_EVIDENCE,
        GNAT_REVIEW_EVIDENCE,
    )
    reaction_evidence = (
        record_evidence,
        AAC_PARENT_EVIDENCE,
        ACYLATION_EVIDENCE,
        GO_ACETYLTRANSFERASE_EVIDENCE,
        GNAT_REVIEW_EVIDENCE,
        ACETYL_COA_EVIDENCE,
    )
    drug_nodes = _drug_nodes(old_graph)
    drug_node_ids = {str(node["node_id"]) for node in drug_nodes}
    relation_evidence = _drug_relation_evidence(old_graph, drug_node_ids)

    drug_input_edges = [
        _edge(
            "transfer",
            "has input (the drug)",
            "RO:0002233",
            str(drug_node["node_id"]),
            "The AAC acetyltransferase activity acts on this CARD-linked "
            f"{drug_node['label']} class.",
            *reaction_evidence,
            *relation_evidence[str(drug_node["node_id"])],
        )
        for drug_node in drug_nodes
    ]
    direct_drug_edges = [
        _canonical_drug_edge(
            record,
            drug_node,
            relation_evidence[str(drug_node["node_id"])],
        )
        for drug_node in drug_nodes
    ]

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → acetyl-CoA-dependent antibiotic acetylation",
        "description": (
            "Curated resistance-causation graph for AAC-mediated "
            "acetyl-CoA-dependent antibiotic N-acetylation and inactivation."
        ),
        "nodes": [
            _determinant_node(record),
            copy.deepcopy(MECH0_NODE),
            copy.deepcopy(MECH1_NODE),
            *drug_nodes,
            copy.deepcopy(TRANSFER_NODE),
            copy.deepcopy(ACETYL_COA_NODE),
            copy.deepcopy(ACETYLATED_NODE),
            copy.deepcopy(DOMAIN_NODE),
            copy.deepcopy(FOLD_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "CARD classifies AAC enzymes under the broad antibiotic "
                "inactivation resistance mechanism.",
                *common_evidence,
                INACTIVATION_EVIDENCE,
                ANTIBIOTIC_INACTIVATION_EVIDENCE,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "AAC antibiotic inactivation results from acetyl-CoA-dependent "
                "acetylation of the antibiotic substrate.",
                AAC_PARENT_EVIDENCE,
                INACTIVATION_EVIDENCE,
                ANTIBIOTIC_INACTIVATION_EVIDENCE,
                ACYLATION_EVIDENCE,
            ),
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech1",
                "CARD classifies AAC enzymes under acylation of antibiotic "
                "conferring resistance.",
                *common_evidence,
                ACYLATION_EVIDENCE,
            ),
            _edge(
                "mech1",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "The AAC acylation resistance mechanism modifies antibiotics "
                "by acetylation and inactivates them.",
                *common_evidence,
                ACYLATION_EVIDENCE,
                INACTIVATION_EVIDENCE,
            ),
            _edge(
                "determinant",
                "enables (acetylates the antibiotic)",
                "RO:0002327",
                "transfer",
                "AAC enzymes catalyze acetyl-CoA-dependent antibiotic "
                "N-acetylation.",
                *reaction_evidence,
            ),
            _edge(
                "transfer",
                "has input (the acetyl donor)",
                "RO:0002233",
                "acetyl_coa",
                "Acetyl-CoA is the acetyl donor used during AAC-mediated "
                "antibiotic N-acetylation.",
                *reaction_evidence,
            ),
            *drug_input_edges,
            _edge(
                "transfer",
                "causally upstream of (inactivates the drug)",
                "RO:0002411",
                "acetylated",
                "AAC activity transfers an acetyl group to the antibiotic "
                "and produces an acetylated inactive drug state.",
                *reaction_evidence,
                INACTIVATION_EVIDENCE,
            ),
            _edge(
                "acetylated",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "The acetylated antibiotic is inactive, lowering effective "
                "drug exposure and causing the resistance phenotype.",
                *common_evidence,
                INACTIVATION_EVIDENCE,
                ACYLATION_EVIDENCE,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "AAC enzymes confer resistance through acetyl-CoA-dependent "
                "antibiotic acetylation and drug inactivation.",
                *common_evidence,
                INACTIVATION_EVIDENCE,
            ),
            *direct_drug_edges,
            _edge(
                "domain",
                "part of (catalytic domain of the protein)",
                "BFO:0000050",
                "determinant",
                "The GNAT acetyltransferase domain is part of the AAC "
                "determinant.",
                record_evidence,
                AAC_PARENT_EVIDENCE,
                INTERPRO_EVIDENCE,
                GNAT_REVIEW_EVIDENCE,
            ),
            _edge(
                "determinant",
                "member of (adopts fold)",
                "RO:0002350",
                "fold",
                "The determinant adopts the acyl-CoA N-acyltransferase fold "
                "associated with GNAT acetyltransferases.",
                record_evidence,
                AAC_PARENT_EVIDENCE,
                CATH_EVIDENCE,
                GNAT_REVIEW_EVIDENCE,
            ),
            _edge(
                "domain",
                "enables (antibiotic acetylation)",
                "RO:0002327",
                "transfer",
                "The GNAT acetyltransferase domain enables the "
                "acetyl-CoA-dependent antibiotic N-acetylation activity.",
                record_evidence,
                AAC_PARENT_EVIDENCE,
                INTERPRO_EVIDENCE,
                GO_ACETYLTRANSFERASE_EVIDENCE,
                GNAT_REVIEW_EVIDENCE,
            ),
        ],
    }


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
    _validate_graph(graphs[0], target)


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    _validate_record(record, target)

    out = copy.deepcopy(record)
    out["causal_graphs"] = [_graph(record, record["causal_graphs"][0])]
    return out, out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not an AAC target: {identifier}")
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
        help="ARO directory or one of the 100 AAC YAML files",
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
