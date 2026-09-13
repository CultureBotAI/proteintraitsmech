#!/usr/bin/env python3
"""Ground and evidence streptogramin Vat acetyltransferase graphs.

The Vat graphs already include the grounded ARO node for acylation of an
antibiotic. The previous drafts also carried an ungrounded acetylation node that
duplicated the grounded mechanism. This updater routes the acetyl-CoA input, the
streptogramin input, and the acetylated inactive product through the grounded
acylation mechanism directly.

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

HISTORY_ACTION = "Grounded Vat streptogramin-acetylation graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

PARENT_IDENTIFIER = "ARO:3000453"
PARENT_EVIDENCE = {
    "reference": PARENT_IDENTIFIER,
    "snippet": (
        "vat (Virginiamycin acetyltransferases) enzymes catalyze the transfer "
        "of an acetyl group from acetyl-CoA to the secondary alcohol of "
        "streptogramin A compounds, thus inactivating virginiamycin-like "
        "antibiotics and conferring resistance to these compounds."
    ),
    "notes": "CARD definition for the streptogramin Vat acetyltransferase parent.",
}

INACTIVATION_EVIDENCE = {
    "reference": "ARO:0001004",
    "snippet": "Enzymatic inactivation of antibiotic to confer drug resistance.",
    "notes": "CARD definition for antibiotic inactivation.",
}

ACYLATION_EVIDENCE = {
    "reference": "ARO:3000106",
    "snippet": "Addition of an acyl group to an antibiotic, often via acetylation by acetylCoA.",
    "notes": "CARD definition for acylation of antibiotic conferring resistance.",
}

STREPTOGRAMIN_EVIDENCE = {
    "reference": "ARO:0000026",
    "snippet": "streptogramin antibiotic",
    "notes": "ARO drug-class term inherited by Vat records.",
}

ACETYL_COA_EVIDENCE = {
    "reference": "CHEBI:15351",
    "snippet": "acetyl-CoA",
    "notes": "Acetyl donor named by the Vat parent definition.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "antibiotic inactivation",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:0001004",
}

ACYLATION_NODE = {
    "node_id": "mech1",
    "label": "acylation of antibiotic conferring resistance",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3000106",
}

STREPTOGRAMIN_NODE = {
    "node_id": "drug0",
    "label": "streptogramin antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:0000026",
}

ACETYL_COA_NODE = {
    "node_id": "acetyl_coa",
    "label": "acetyl-CoA",
    "node_type": "CHEMICAL",
    "grounding": "CHEBI:15351",
}

ACETYLATED_STREPTOGRAMIN_NODE = {
    "node_id": "modified",
    "label": "acetylated inactive streptogramin A",
    "node_type": "STATE",
    "description": (
        "Local state for the acetylated, inactive streptogramin A product "
        "of Vat-mediated acetyl-group transfer."
    ),
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

EXPECTED_EDGE_KEYS = {
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0000056", "mech1"),
    ("mech1", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("determinant", "ARO:2000001", "drug0"),
    ("mech1", "RO:0002233", "acetyl_coa"),
    ("mech1", "RO:0002233", "drug0"),
    ("mech1", "RO:0002411", "modified"),
    ("modified", "RO:0002212", "drug0"),
}

REMOVED_EDGE_KEYS = {
    ("determinant", "RO:0002327", "acetylation"),
    ("acetylation", "RO:0002233", "acetyl_coa"),
    ("acetylation", "RO:0002233", "drug0"),
    ("acetylation", "RO:0002411", "modified"),
}

EDGE_DESCRIPTIONS = {
    ("determinant", "RO:0000056", "mech0"): (
        "ARO classifies Vat determinants under antibiotic inactivation."
    ),
    ("mech0", "RO:0002411", "resistance"): (
        "Antibiotic inactivation is the broad resistance mechanism for Vat "
        "streptogramin acetylation."
    ),
    ("determinant", "RO:0000056", "mech1"): (
        "ARO classifies Vat determinants under acylation of antibiotic "
        "conferring resistance."
    ),
    ("mech1", "RO:0002411", "resistance"): (
        "Vat enzymes transfer an acetyl group to streptogramin A compounds "
        "and thereby inactivate them."
    ),
    ("determinant", "RO:0002411", "resistance"): (
        "Vat determinants confer resistance by acetylating and inactivating "
        "streptogramin A compounds."
    ),
    ("determinant", "ARO:2000001", "drug0"): (
        "ARO maps Vat acetyltransferases to streptogramin antibiotics."
    ),
    ("mech1", "RO:0002233", "acetyl_coa"): (
        "Vat-mediated acylation uses acetyl-CoA as the acetyl donor."
    ),
    ("mech1", "RO:0002233", "drug0"): (
        "Vat-mediated acylation modifies streptogramin A compounds."
    ),
    ("mech1", "RO:0002411", "modified"): (
        "Vat-mediated acylation produces acetylated streptogramin A."
    ),
    ("modified", "RO:0002212", "drug0"): (
        "The acetylated streptogramin A state represents enzymatic "
        "inactivation of the drug."
    ),
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str

    @property
    def is_parent(self) -> bool:
        return self.identifier == PARENT_IDENTIFIER


TARGETS = {
    PARENT_IDENTIFIER: Target(
        identifier=PARENT_IDENTIFIER,
        filename="streptogramin-vat-acetyltransferase-aro3000453.yaml",
    ),
    "ARO:3002840": Target(identifier="ARO:3002840", filename="vata-aro3002840.yaml"),
    "ARO:3002841": Target(identifier="ARO:3002841", filename="vatb-aro3002841.yaml"),
    "ARO:3002842": Target(identifier="ARO:3002842", filename="vatc-aro3002842.yaml"),
    "ARO:3002843": Target(identifier="ARO:3002843", filename="vatd-aro3002843.yaml"),
    "ARO:3002844": Target(identifier="ARO:3002844", filename="vate-aro3002844.yaml"),
    "ARO:3003744": Target(identifier="ARO:3003744", filename="vatf-aro3003744.yaml"),
    "ARO:3002845": Target(identifier="ARO:3002845", filename="vath-aro3002845.yaml"),
    "ARO:3003987": Target(identifier="ARO:3003987", filename="vati-aro3003987.yaml"),
}


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


def _nodes_by_id(graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(node["node_id"]): node
        for node in _dicts(graph.get("nodes"))
        if "node_id" in node
    }


def _source_evidence(record: dict[str, Any]) -> tuple[dict[str, str], ...]:
    return tuple(
        {
            "reference": str(item["reference"]),
            "notes": str(item.get("notes") or "ARO citation for this record."),
        }
        for item in _dicts(record.get("evidence"))
        if item.get("reference")
    )


def _own_definition_evidence(record: dict[str, Any], target: Target) -> dict[str, str]:
    if target.is_parent:
        return PARENT_EVIDENCE
    return {
        "reference": target.identifier,
        "snippet": str(record["definition"]),
        "notes": f"CARD definition for {record['label']}.",
    }


def _unique_evidence(evidence: tuple[dict[str, str], ...]) -> list[dict[str, str]]:
    unique: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for item in evidence:
        key = (
            item["reference"],
            item.get("snippet", ""),
            item.get("notes", ""),
        )
        if key in seen:
            continue
        seen.add(key)
        unique.append(copy.deepcopy(item))
    return unique


def _drug_relation_evidence(target: Target) -> dict[str, str]:
    if target.is_parent:
        notes = "ARO drug-class relationship asserted directly on the Vat parent."
    else:
        notes = (
            "ARO drug-class relationship asserted on ARO:3000453 and inherited "
            f"by {target.identifier}."
        )
    return {
        "reference": PARENT_IDENTIFIER,
        "snippet": (
            "relationship: confers_resistance_to_drug_class ARO:0000026 ! "
            "streptogramin antibiotic"
        ),
        "notes": notes,
    }


def _edge(
    subject: str,
    predicate: str,
    predicate_id: str,
    object_: str,
    evidence: tuple[dict[str, str], ...],
) -> dict[str, Any]:
    return {
        "subject": subject,
        "predicate": predicate,
        "predicate_id": predicate_id,
        "object": object_,
        "description": EDGE_DESCRIPTIONS[(subject, predicate_id, object_)],
        "evidence": _unique_evidence(evidence),
    }


def _validate_graph(graph: dict[str, Any], target: Target) -> None:
    nodes = _nodes_by_id(graph)
    missing_nodes = sorted(
        {"determinant", "mech0", "mech1", "drug0", "acetyl_coa", "modified"}
        - set(nodes)
    )
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")

    found_edges = set()
    seen: set[tuple[str, str, str]] = set()
    all_edges = {_edge_key(edge) for edge in _dicts(graph.get("edges"))}
    for edge in _dicts(graph.get("edges")):
        key = _edge_key(edge)
        if key in REMOVED_EDGE_KEYS:
            continue
        if key not in EXPECTED_EDGE_KEYS:
            raise ValueError(f"{target.identifier}: unexpected edge {key[0]} -> {key[2]}")
        if key in seen:
            raise ValueError(f"{target.identifier}: duplicate edge {key[0]} -> {key[2]}")
        seen.add(key)
        found_edges.add(key)

    if {key for key in REMOVED_EDGE_KEYS if key[0] == "acetylation"} <= all_edges:
        required_edges = EXPECTED_EDGE_KEYS - {
            ("mech1", "RO:0002233", "acetyl_coa"),
            ("mech1", "RO:0002233", "drug0"),
            ("mech1", "RO:0002411", "modified"),
            ("modified", "RO:0002212", "drug0"),
        }
    else:
        required_edges = EXPECTED_EDGE_KEYS

    missing_edges = sorted(required_edges - found_edges)
    if missing_edges:
        missing = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in missing_edges)
        raise ValueError(f"{target.identifier}: missing edge(s): {missing}")


def _canonical_graph(record: dict[str, Any], target: Target) -> dict[str, Any]:
    graph = record["causal_graphs"][0]
    _validate_graph(graph, target)
    nodes = _nodes_by_id(graph)
    own_evidence = _own_definition_evidence(record, target)
    source_evidence = _source_evidence(record)
    inactivation_evidence = (
        own_evidence,
        PARENT_EVIDENCE,
        INACTIVATION_EVIDENCE,
        *source_evidence,
    )
    acylation_evidence = (
        own_evidence,
        PARENT_EVIDENCE,
        ACYLATION_EVIDENCE,
        *source_evidence,
    )
    resistance_evidence = (
        own_evidence,
        PARENT_EVIDENCE,
        *source_evidence,
    )
    drug_evidence = (
        _drug_relation_evidence(target),
        STREPTOGRAMIN_EVIDENCE,
        PARENT_EVIDENCE,
        *source_evidence,
    )
    acetyl_coa_evidence = (
        own_evidence,
        PARENT_EVIDENCE,
        ACETYL_COA_EVIDENCE,
        *source_evidence,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → streptogramin A acetylation → drug inactivation",
        "description": (
            "Conservative graph for Vat-mediated streptogramin resistance. "
            "The graph routes the acetyl-CoA and streptogramin inputs through "
            "the grounded ARO acylation mechanism and represents the "
            "acetylated, inactive streptogramin A as a local state."
        ),
        "nodes": [
            copy.deepcopy(nodes["determinant"]),
            copy.deepcopy(MECHANISM_NODE),
            copy.deepcopy(ACYLATION_NODE),
            copy.deepcopy(STREPTOGRAMIN_NODE),
            copy.deepcopy(ACETYL_COA_NODE),
            copy.deepcopy(ACETYLATED_STREPTOGRAMIN_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                inactivation_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                inactivation_evidence,
            ),
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech1",
                acylation_evidence,
            ),
            _edge(
                "mech1",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                acylation_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                resistance_evidence,
            ),
            _edge(
                "determinant",
                "confers resistance to (drug class)",
                "ARO:2000001",
                "drug0",
                drug_evidence,
            ),
            _edge(
                "mech1",
                "has input",
                "RO:0002233",
                "acetyl_coa",
                acetyl_coa_evidence,
            ),
            _edge(
                "mech1",
                "has input",
                "RO:0002233",
                "drug0",
                acylation_evidence,
            ),
            _edge(
                "mech1",
                "causally upstream of",
                "RO:0002411",
                "modified",
                acylation_evidence,
            ),
            _edge(
                "modified",
                "negatively regulates",
                "RO:0002212",
                "drug0",
                resistance_evidence,
            ),
        ],
    }


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != target.identifier:
        raise ValueError(
            f"{target.filename}: expected {target.identifier}, "
            f"found {record.get('identifier')}"
        )
    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1 or graphs[0].get("graph_id") != "resistance":
        raise ValueError(f"{target.identifier}: expected exactly one resistance graph")

    out = copy.deepcopy(record)
    out["causal_graphs"] = [_canonical_graph(record, target)]
    return out, out != record


def enrich_text(text: str, path: Path, target: Target) -> tuple[str, bool]:
    if path.name != target.filename:
        raise ValueError(f"{target.identifier}: not the expected path: {path}")

    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")
    enriched, changed = enrich_record(record, target)
    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))

    history = list(_dicts(enriched.get("curation_history")))
    if not any(item.get("action") == HISTORY_ACTION for item in history):
        out = append_to_section(out, "curation_history", _dump({"curation_history": [HISTORY_EVENT]}))
        changed = True

    if "&id" in out or "*id" in out:
        raise ValueError(f"{path}: YAML anchors leaked into output")
    return out, changed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--path", type=Path, default=ARO_DIR)
    args = parser.parse_args(argv)

    changed_count = 0
    for target in TARGETS.values():
        path = args.path / target.filename
        before = path.read_text(encoding="utf-8")
        after, changed = enrich_text(before, path, target)
        if not changed:
            continue
        changed_count += 1
        if args.apply:
            path.write_text(after, encoding="utf-8")
            print(f"  wrote {target.filename}")
        else:
            print(f"  would write {target.filename}")

    print(f"{'changed' if args.apply else 'would change'}: {changed_count}")
    if not changed_count:
        print(f"already enriched: {len(TARGETS)}")
    if not args.apply:
        print("dry run -- pass --apply to write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
