#!/usr/bin/env python3
"""Rewrite AAK class A beta-lactamase ARO causal graphs.

The promoted AAK graphs already have the right serine beta-lactamase graph
shape, but each mechanistic edge carries only the generic PMID:32576842 family
snippet and most edges have no description. This updater rewrites the exact
rank-77 AAK records with fully described, multi-evidence class A graphs while
preserving every existing determinant-to-drug-class edge.

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
    "timestamp": "2026-09-08T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": "Completed AAK class A beta-lactamase causal graphs",
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

AAK_EVIDENCE = {
    "reference": "ARO:3005387",
    "snippet": (
        "AAK beta-lactamases are a group of class A beta-lactamases found in "
        "Klebsiella pneumoniae."
    ),
    "notes": "CARD definition for AAK beta-lactamase.",
}

CLASS_A_EVIDENCE = {
    "reference": "ARO:3000078",
    "snippet": (
        "The Class A beta-lactamases are one of the subgroups of "
        "beta-lactamases that are classified as serine enzymes. Class A "
        "beta-lactamases exhibit a large degree of variability and are known "
        "to hydrolyze penicillins."
    ),
    "notes": "CARD definition for class A beta-lactamase.",
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

PROSITE_EVIDENCE = {
    "reference": "PROSITE:PS00146",
    "snippet": "Beta-lactamase class-A active site",
    "notes": "PROSITE active-site signature for class A beta-lactamases.",
}

CATH_EVIDENCE = {
    "reference": "CATH:3.40.710.10",
    "snippet": "DD-peptidase/beta-lactamase superfamily",
    "notes": "CATH fold for serine beta-lactamases.",
}

MECH0_NODE = {
    "node_id": "mech0",
    "label": "antibiotic inactivation",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:0001004",
}

MECH1_NODE = {
    "node_id": "mech1",
    "label": "hydrolysis of beta-lactam antibiotic by serine beta-lactamase",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3000187",
}

ACTIVE_SITE_NODE = {
    "node_id": "active_site",
    "label": "class A beta-lactamase active-site signature (S-x-x-K)",
    "node_type": "MOTIF",
    "grounding": "PROSITE:PS00146",
    "description": "Class A beta-lactamase catalytic serine active-site signature.",
}

FOLD_NODE = {
    "node_id": "fold",
    "label": "DD-peptidase/beta-lactamase superfamily fold",
    "node_type": "DOMAIN",
    "grounding": "CATH:3.40.710.10",
    "description": "DD-peptidase/beta-lactamase superfamily fold.",
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
    ("active_site", "BFO:0000050", "determinant"),
    ("determinant", "RO:0002350", "fold"),
    ("active_site", "RO:0002327", "mech1"),
}

DRUG_ID = re.compile(r"^drug\d+$")


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str


TARGETS: tuple[Target, ...] = (
    Target("ARO:3006863", "aak-1-aro3006863.yaml"),
    Target("ARO:3005387", "aak-beta-lactamase-aro3005387.yaml"),
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
    required_nodes = {"determinant", "mech0", "mech1", "active_site", "fold", "resistance"}
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
        direct_drug_edge = (
            subject == "determinant"
            and predicate_id == "ARO:2000001"
            and object_ in drug_node_ids
        )
        if key not in CORE_EDGE_KEYS and not direct_drug_edge:
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
        f"CARD asserts that this AAK determinant confers resistance to {drug_label}.",
        *relation_evidence,
        _record_evidence(record),
        AAK_EVIDENCE,
        CLASS_A_EVIDENCE,
        BETA_LACTAMASE_EVIDENCE,
    )


def _graph(record: dict[str, Any], old_graph: dict[str, Any]) -> dict[str, Any]:
    record_evidence = _record_evidence(record)
    common_evidence = (
        record_evidence,
        AAK_EVIDENCE,
        CLASS_A_EVIDENCE,
        INACTIVATION_ENZYME_EVIDENCE,
        ANTIBIOTIC_INACTIVATION_EVIDENCE,
        BETA_LACTAMASE_EVIDENCE,
        SERINE_REACTION_EVIDENCE,
    )
    specific_evidence = (
        record_evidence,
        AAK_EVIDENCE,
        CLASS_A_EVIDENCE,
        BETA_LACTAMASE_EVIDENCE,
        SERINE_BETA_LACTAMASE_EVIDENCE,
        SERINE_REACTION_EVIDENCE,
    )
    catalytic_evidence = (
        record_evidence,
        AAK_EVIDENCE,
        CLASS_A_EVIDENCE,
        PROSITE_EVIDENCE,
        SERINE_REACTION_EVIDENCE,
    )
    drug_nodes = _drug_nodes(old_graph)
    drug_node_ids = {str(node["node_id"]) for node in drug_nodes}
    relation_evidence = _drug_relation_evidence(old_graph, drug_node_ids)

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
        "title": f"{record['label']} → class A serine beta-lactam hydrolysis",
        "description": (
            "Curated resistance-causation graph for AAK class A beta-lactamase "
            "hydrolysis of beta-lactam antibiotics."
        ),
        "nodes": [
            _determinant_node(record),
            copy.deepcopy(MECH0_NODE),
            copy.deepcopy(MECH1_NODE),
            *drug_nodes,
            copy.deepcopy(ACTIVE_SITE_NODE),
            copy.deepcopy(FOLD_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "CARD classifies AAK class A beta-lactamases under broad "
                "antibiotic inactivation.",
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
                "CARD classifies AAK class A beta-lactamases under serine "
                "beta-lactam hydrolysis.",
                *specific_evidence,
            ),
            _edge(
                "mech1",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Serine beta-lactamase hydrolysis opens the beta-lactam ring "
                "and renders the antibiotic inactive.",
                *specific_evidence,
                ANTIBIOTIC_INACTIVATION_EVIDENCE,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "AAK beta-lactamases confer resistance through class A serine "
                "beta-lactam hydrolysis and antibiotic inactivation.",
                *common_evidence,
                SERINE_BETA_LACTAMASE_EVIDENCE,
            ),
            *direct_drug_edges,
            _edge(
                "active_site",
                "part of",
                "BFO:0000050",
                "determinant",
                "The class A S-x-x-K active-site signature is part of the AAK "
                "beta-lactamase determinant.",
                *catalytic_evidence,
            ),
            _edge(
                "determinant",
                "member of",
                "RO:0002350",
                "fold",
                "The AAK determinant adopts the DD-peptidase/beta-lactamase "
                "fold associated with serine beta-lactamases.",
                record_evidence,
                AAK_EVIDENCE,
                CLASS_A_EVIDENCE,
                CATH_EVIDENCE,
                SERINE_REACTION_EVIDENCE,
            ),
            _edge(
                "active_site",
                "enables (serine beta-lactam hydrolysis)",
                "RO:0002327",
                "mech1",
                "The class A active site provides the catalytic serine used "
                "for beta-lactam acylation and hydrolysis.",
                *catalytic_evidence,
                SERINE_BETA_LACTAMASE_EVIDENCE,
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
        raise ValueError(f"{path}: not an AAK target: {identifier}")
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
        help="ARO directory or one of the 2 AAK YAML files",
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
