#!/usr/bin/env python3
"""Rewrite aminoglycoside adenylyltransferase AAD ARO causal graphs.

The promoted aad/ANT(3'')/ANT(6) graphs ground the ARO aminoglycoside
nucleotidylation mechanism, nucleotidyltransferase domain, and
beta-polymerase-like fold, but they omit the ATP substrate and the
adenylylated inactive drug state that connect the reaction to resistance.

This updater rewrites the exact rank-77 aad records to an ATP-dependent
adenylylation model and preserves every existing determinant-to-drug-class
edge.

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
    "action": "Completed AAD aminoglycoside adenylyltransferase causal graphs",
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

NUCLEOTIDYLATION_EVIDENCE = {
    "reference": "ARO:3000107",
    "snippet": "Modification by NMP, usually AMP.",
    "notes": "CARD definition for nucleotidylation of antibiotic conferring resistance.",
}

ANT_PARENT_EVIDENCE = {
    "reference": "ARO:3000218",
    "snippet": (
        "Covalent modification of aminoglycoside antibiotic hydroxyl group by "
        "ATP-dependent transfer of AMP."
    ),
    "notes": "CARD definition for aminoglycoside nucleotidyltransferase (ANT).",
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

ANT_REACTION_EVIDENCE = {
    "reference": "PMID:25564464",
    "snippet": (
        "ANT(2″)-Ia confers resistance by magnesium-dependent transfer of a "
        "nucleoside monophosphate (AMP) to the 2″-hydroxyl of aminoglycoside "
        "substrates containing a 2-deoxystreptamine core."
    ),
    "notes": "Literature support for aminoglycoside nucleotidyltransferase activity.",
}

GO_NUCLEOTIDYLTRANSFERASE_EVIDENCE = {
    "reference": "GO:0016779",
    "snippet": (
        "Catalysis of the transfer of a nucleotidyl group from one compound "
        "(donor) to another (acceptor)."
    ),
    "notes": "GO grounding for the broad nucleotidyltransferase activity node.",
}

PFAM_EVIDENCE = {
    "reference": "Pfam:PF01909",
    "snippet": "Nucleotidyltransferase domain",
    "notes": "Pfam family for aminoglycoside nucleotidyltransferases.",
}

CATH_EVIDENCE = {
    "reference": "CATH:3.30.460",
    "snippet": "Beta Polymerase; domain 2",
    "notes": "CATH grounding for the nucleotidyltransferase fold.",
}

MECH0_NODE = {
    "node_id": "mech0",
    "label": "antibiotic inactivation",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:0001004",
}

MECH1_NODE = {
    "node_id": "mech1",
    "label": "nucleotidylation of antibiotic conferring resistance",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3000107",
}

TRANSFER_NODE = {
    "node_id": "transfer",
    "label": "nucleotidyltransferase activity",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "GO:0016779",
    "description": (
        "Grounded to the broad GO nucleotidyltransferase activity term and "
        "scoped here to ATP-dependent aminoglycoside adenylylation by ANT "
        "enzymes."
    ),
}

ATP_NODE = {
    "node_id": "atp",
    "label": "ATP",
    "node_type": "CHEMICAL",
    "grounding": "CHEBI:15422",
}

ADENYLYLATED_NODE = {
    "node_id": "adenylylated",
    "label": "adenylylated inactive aminoglycoside antibiotic",
    "node_type": "STATE",
    "description": (
        "Local state for an aminoglycoside antibiotic after ANT-mediated AMP "
        "transfer from ATP."
    ),
}

DOMAIN_NODE = {
    "node_id": "domain",
    "label": "nucleotidyltransferase domain",
    "node_type": "DOMAIN",
    "grounding": "Pfam:PF01909",
    "description": "Nucleotidyltransferase catalytic domain found in ANT enzymes.",
}

FOLD_NODE = {
    "node_id": "fold",
    "label": "DNA-polymerase-β-like nucleotidyltransferase fold",
    "node_type": "DOMAIN",
    "grounding": "CATH:3.30.460",
    "description": "Beta-polymerase-like nucleotidyltransferase fold.",
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
    ("transfer", "RO:0002233", "atp"),
    ("transfer", "RO:0002411", "adenylylated"),
    ("adenylylated", "RO:0002411", "resistance"),
    ("domain", "RO:0002327", "transfer"),
}

DRUG_ID = re.compile(r"^drug\d+$")


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str


_TARGET_ROWS = """
ARO:3002628 aad-6-aro3002628.yaml
ARO:3002601 aada-aro3002601.yaml
ARO:3004692 aada10-aro3004692.yaml
ARO:3002611 aada11-aro3002611.yaml
ARO:3002612 aada12-aro3002612.yaml
ARO:3002613 aada13-aro3002613.yaml
ARO:3002614 aada14-aro3002614.yaml
ARO:3002615 aada15-aro3002615.yaml
ARO:3002616 aada16-aro3002616.yaml
ARO:3002617 aada17-aro3002617.yaml
ARO:3002602 aada2-aro3002602.yaml
ARO:3002618 aada21-aro3002618.yaml
ARO:3002619 aada22-aro3002619.yaml
ARO:3002620 aada23-aro3002620.yaml
ARO:3002621 aada24-aro3002621.yaml
ARO:3003197 aada25-aro3003197.yaml
ARO:3004682 aada27-aro3004682.yaml
ARO:3002603 aada3-aro3002603.yaml
ARO:3002604 aada4-aro3002604.yaml
ARO:3002605 aada5-aro3002605.yaml
ARO:3002622 aada6-aada10-aro3002622.yaml
ARO:3002606 aada6-aro3002606.yaml
ARO:3002607 aada7-aro3002607.yaml
ARO:3002608 aada8-aro3002608.yaml
ARO:3004704 aada8b-aro3004704.yaml
ARO:3002609 aada9-aro3002609.yaml
ARO:3002627 aadk-aro3002627.yaml
ARO:3004683 aads-aro3004683.yaml
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
        f"CARD asserts that this ANT determinant confers resistance to {drug_label}.",
        *relation_evidence,
        _record_evidence(record),
        ANT_PARENT_EVIDENCE,
        AMINOGLYCOSIDE_MODIFYING_EVIDENCE,
    )


def _graph(record: dict[str, Any], old_graph: dict[str, Any]) -> dict[str, Any]:
    record_evidence = _record_evidence(record)
    common_evidence = (
        record_evidence,
        ANT_PARENT_EVIDENCE,
        AMINOGLYCOSIDE_MODIFYING_EVIDENCE,
        ANT_REACTION_EVIDENCE,
    )
    reaction_evidence = (
        record_evidence,
        ANT_PARENT_EVIDENCE,
        NUCLEOTIDYLATION_EVIDENCE,
        GO_NUCLEOTIDYLTRANSFERASE_EVIDENCE,
        ANT_REACTION_EVIDENCE,
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
            "The ANT nucleotidyltransferase activity acts on this CARD-linked "
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
        "title": f"{record['label']} → ATP-dependent aminoglycoside adenylylation",
        "description": (
            "Curated resistance-causation graph for ANT-mediated "
            "ATP-dependent aminoglycoside O-adenylylation and inactivation."
        ),
        "nodes": [
            _determinant_node(record),
            copy.deepcopy(MECH0_NODE),
            copy.deepcopy(MECH1_NODE),
            *drug_nodes,
            copy.deepcopy(TRANSFER_NODE),
            copy.deepcopy(ATP_NODE),
            copy.deepcopy(ADENYLYLATED_NODE),
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
                "CARD classifies ANT enzymes under the broad antibiotic "
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
                "ANT antibiotic inactivation results from ATP-dependent "
                "adenylylation of the aminoglycoside substrate.",
                ANT_PARENT_EVIDENCE,
                INACTIVATION_EVIDENCE,
                ANTIBIOTIC_INACTIVATION_EVIDENCE,
                NUCLEOTIDYLATION_EVIDENCE,
            ),
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech1",
                "CARD classifies ANT enzymes under nucleotidylation of "
                "antibiotic conferring resistance.",
                *common_evidence,
                NUCLEOTIDYLATION_EVIDENCE,
            ),
            _edge(
                "mech1",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "The ANT nucleotidylation resistance mechanism modifies "
                "aminoglycosides by adenylylation and inactivates them.",
                *common_evidence,
                NUCLEOTIDYLATION_EVIDENCE,
                INACTIVATION_EVIDENCE,
            ),
            _edge(
                "determinant",
                "enables (adenylylates the aminoglycoside)",
                "RO:0002327",
                "transfer",
                "ANT enzymes catalyze ATP-dependent aminoglycoside "
                "O-adenylylation.",
                *reaction_evidence,
            ),
            _edge(
                "transfer",
                "has input (ATP)",
                "RO:0002233",
                "atp",
                "ATP is the AMP donor used during ANT-mediated aminoglycoside "
                "O-adenylylation.",
                *reaction_evidence,
            ),
            *drug_input_edges,
            _edge(
                "transfer",
                "causally upstream of (inactivates the drug)",
                "RO:0002411",
                "adenylylated",
                "ANT activity transfers AMP from ATP to the aminoglycoside and "
                "produces an adenylylated inactive drug state.",
                *reaction_evidence,
                INACTIVATION_EVIDENCE,
            ),
            _edge(
                "adenylylated",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "The adenylylated aminoglycoside is inactive, lowering "
                "effective drug exposure and causing the resistance phenotype.",
                *common_evidence,
                INACTIVATION_EVIDENCE,
                NUCLEOTIDYLATION_EVIDENCE,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "ANT enzymes confer resistance through ATP-dependent "
                "aminoglycoside adenylylation and drug inactivation.",
                *common_evidence,
                INACTIVATION_EVIDENCE,
            ),
            *direct_drug_edges,
            _edge(
                "domain",
                "part of (catalytic domain of the protein)",
                "BFO:0000050",
                "determinant",
                "The nucleotidyltransferase domain is part of the ANT "
                "determinant.",
                record_evidence,
                ANT_PARENT_EVIDENCE,
                PFAM_EVIDENCE,
                ANT_REACTION_EVIDENCE,
            ),
            _edge(
                "determinant",
                "member of (adopts fold)",
                "RO:0002350",
                "fold",
                "The determinant adopts the beta-polymerase-like fold "
                "associated with aminoglycoside nucleotidyltransferases.",
                record_evidence,
                ANT_PARENT_EVIDENCE,
                CATH_EVIDENCE,
                ANT_REACTION_EVIDENCE,
            ),
            _edge(
                "domain",
                "enables (aminoglycoside adenylylation)",
                "RO:0002327",
                "transfer",
                "The nucleotidyltransferase domain enables the ATP-dependent "
                "aminoglycoside O-adenylylation activity.",
                record_evidence,
                ANT_PARENT_EVIDENCE,
                PFAM_EVIDENCE,
                GO_NUCLEOTIDYLTRANSFERASE_EVIDENCE,
                ANT_REACTION_EVIDENCE,
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
        raise ValueError(f"{path}: not an AAD target: {identifier}")
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
        help="ARO directory or one of the 28 AAD YAML files",
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
