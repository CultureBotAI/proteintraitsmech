#!/usr/bin/env python3
"""Ground and simplify FabI mutation resistance graphs.

The FabI graphs model Triclosan inhibition of enoyl-ACP reduction and name
isoniazid only as an inherited resistant drug class. This updater grounds the
FabI activity to GO:0004318, keeps the Triclosan inhibition as a local state,
and removes the redundant ungrounded fatty-acid-elongation process node.

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

HISTORY_ACTION = "Grounded FabI enoyl-ACP reductase graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

PARENT_IDENTIFIER = "ARO:3004270"
PARENT_EVIDENCE = {
    "reference": PARENT_IDENTIFIER,
    "snippet": (
        "fabI is a enoyl-acyl carrier reductase used in lipid metabolism and "
        "fatty acid biosynthesis. The bacterial biocide Triclosan blocks the "
        "final reduction step in fatty acid elongation, inhibiting "
        "biosynthesis. Point mutations in fabI can confer resistance to "
        "Triclosan and Isoniazid."
    ),
    "notes": "CARD definition for the antibiotic-resistant FabI parent.",
}

MUTATION_EVIDENCE = {
    "reference": "ARO:3000212",
    "snippet": (
        "Point mutations in the DNA may lead to an altered gene product that "
        "may result in antibiotic resistance."
    ),
    "notes": "CARD definition for mutation conferring antibiotic resistance.",
}

GO_ENOYL_ACP_REDUCTASE_EVIDENCE = {
    "reference": "GO:0004318",
    "snippet": (
        "Catalysis of the reaction: a 2,3-saturated acyl-[ACP] + NAD+ = a "
        "(2E)-enoyl-[ACP] + H+ + NADH."
    ),
    "notes": "GO definition for enoyl-[acyl-carrier-protein] reductase (NADH) activity.",
}

DISINFECTANT_EVIDENCE = {
    "reference": "ARO:3005386",
    "snippet": "disinfecting agents and antiseptics",
    "notes": "ARO drug-class term inherited by FabI records.",
}

ISONIAZID_EVIDENCE = {
    "reference": "ARO:3007152",
    "snippet": "isoniazid-like antibiotic",
    "notes": "ARO drug-class term inherited by FabI records.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "mutation conferring antibiotic resistance",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3000212",
}

DISINFECTANT_NODE = {
    "node_id": "drug0",
    "label": "disinfecting agents and antiseptics",
    "node_type": "CHEMICAL",
    "grounding": "ARO:3005386",
}

ISONIAZID_NODE = {
    "node_id": "drug1",
    "label": "isoniazid-like antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:3007152",
}

ENOYL_REDUCTION_NODE = {
    "node_id": "enoyl_reduction",
    "label": "enoyl-[acyl-carrier-protein] reductase (NADH) activity",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "GO:0004318",
}

INHIBITION_NODE = {
    "node_id": "inhibition",
    "label": "Triclosan inhibition of FabI enoyl-ACP reduction",
    "node_type": "STATE",
    "description": (
        "Local state for Triclosan blocking the final FabI-catalyzed reduction "
        "step in bacterial fatty-acid elongation."
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
    ("determinant", "RO:0002411", "resistance"),
    ("determinant", "ARO:2000001", "drug0"),
    ("determinant", "ARO:2000001", "drug1"),
    ("determinant", "RO:0002327", "enoyl_reduction"),
    ("drug0", "RO:0002411", "inhibition"),
    ("determinant", "RO:0002212", "inhibition"),
}

OLD_FA_ELONGATION_EDGE = ("enoyl_reduction", "BFO:0000050", "fa_elongation")

EDGE_DESCRIPTIONS = {
    ("determinant", "RO:0000056", "mech0"): (
        "ARO classifies these FabI records under mutation conferring "
        "antibiotic resistance."
    ),
    ("mech0", "RO:0002411", "resistance"): (
        "The FabI mechanism is a resistance-conferring gene variant caused by "
        "mutation."
    ),
    ("determinant", "RO:0002411", "resistance"): (
        "Point mutations in FabI can confer Triclosan and isoniazid "
        "resistance while the sourced Triclosan branch acts through enoyl-ACP "
        "reduction."
    ),
    ("determinant", "ARO:2000001", "drug0"): (
        "ARO maps the antibiotic-resistant FabI parent to disinfecting agents "
        "and antiseptics."
    ),
    ("determinant", "ARO:2000001", "drug1"): (
        "ARO maps the antibiotic-resistant FabI parent to isoniazid-like "
        "antibiotics."
    ),
    ("determinant", "RO:0002327", "enoyl_reduction"): (
        "FabI enables the GO-grounded NADH enoyl-ACP reductase activity used "
        "in fatty-acid biosynthesis."
    ),
    ("drug0", "RO:0002411", "inhibition"): (
        "Triclosan blocks the final FabI reduction step in bacterial "
        "fatty-acid elongation."
    ),
    ("determinant", "RO:0002212", "inhibition"): (
        "Resistance-conferring FabI mutations reduce the inhibitory effect of "
        "Triclosan on the FabI-catalyzed reduction step."
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
    "ARO:3004270": Target(
        identifier="ARO:3004270",
        filename="antibiotic-resistant-fabi-aro3004270.yaml",
    ),
    "ARO:3004045": Target(
        identifier="ARO:3004045",
        filename=(
            "escherichia-coli-fabi-mutations-conferring-resistance-to-"
            "isoniazid-and-triclosan-aro3004045.yaml"
        ),
    ),
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


def _target_evidence(record: dict[str, Any], target: Target) -> dict[str, str]:
    if target.is_parent:
        return PARENT_EVIDENCE
    return {
        "reference": str(record["identifier"]),
        "snippet": str(record["definition"]),
        "notes": f"CARD definition for {record['label']}.",
    }


def _drug_relation_evidence(target: Target, drug_node: str) -> dict[str, str]:
    drug_label = {
        "drug0": "disinfecting agents and antiseptics",
        "drug1": "isoniazid-like antibiotic",
    }[drug_node]
    drug_aro = {
        "drug0": "ARO:3005386",
        "drug1": "ARO:3007152",
    }[drug_node]
    if target.is_parent:
        notes = "ARO drug-class relationship asserted directly on antibiotic resistant fabI."
    else:
        notes = (
            "ARO drug-class relationship asserted on ARO:3004270 and inherited "
            f"by {target.identifier}."
        )
    return {
        "reference": PARENT_IDENTIFIER,
        "snippet": f"relationship: confers_resistance_to_drug_class {drug_aro} ! {drug_label}",
        "notes": notes,
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
        {
            "determinant",
            "mech0",
            "drug0",
            "drug1",
            "enoyl_reduction",
            "inhibition",
            "resistance",
        }
        - set(nodes)
    )
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")

    found_edges = set()
    seen: set[tuple[str, str, str]] = set()
    for edge in _dicts(graph.get("edges")):
        key = _edge_key(edge)
        if key == OLD_FA_ELONGATION_EDGE:
            continue
        if key not in EXPECTED_EDGE_KEYS:
            raise ValueError(f"{target.identifier}: unexpected edge {key[0]} -> {key[2]}")
        if key in seen:
            raise ValueError(f"{target.identifier}: duplicate edge {key[0]} -> {key[2]}")
        seen.add(key)
        found_edges.add(key)

    missing_edges = sorted(EXPECTED_EDGE_KEYS - found_edges)
    if missing_edges:
        missing = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in missing_edges)
        raise ValueError(f"{target.identifier}: missing edge(s): {missing}")


def _canonical_graph(record: dict[str, Any], target: Target) -> dict[str, Any]:
    graph = record["causal_graphs"][0]
    _validate_graph(graph, target)
    nodes = _nodes_by_id(graph)
    target_evidence = _target_evidence(record, target)
    source_evidence = _source_evidence(record)
    mutation_resistance_evidence = (
        target_evidence,
        PARENT_EVIDENCE,
        MUTATION_EVIDENCE,
        *source_evidence,
    )
    enoyl_evidence = (
        target_evidence,
        PARENT_EVIDENCE,
        GO_ENOYL_ACP_REDUCTASE_EVIDENCE,
        *source_evidence,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → FabI enoyl-ACP reduction → resistance",
        "description": (
            "Conservative graph for FabI-mediated Triclosan resistance. The "
            "graph grounds the FabI enoyl-ACP reductase activity, leaves "
            "Triclosan inhibition as a local state, and does not assert an "
            "isoniazid action because ARO names isoniazid as a resisted class "
            "without describing its FabI-specific mechanism."
        ),
        "nodes": [
            copy.deepcopy(nodes["determinant"]),
            copy.deepcopy(MECHANISM_NODE),
            copy.deepcopy(DISINFECTANT_NODE),
            copy.deepcopy(ISONIAZID_NODE),
            copy.deepcopy(ENOYL_REDUCTION_NODE),
            copy.deepcopy(INHIBITION_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                mutation_resistance_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                mutation_resistance_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                mutation_resistance_evidence,
            ),
            _edge(
                "determinant",
                "confers resistance to",
                "ARO:2000001",
                "drug0",
                (
                    target_evidence,
                    _drug_relation_evidence(target, "drug0"),
                    DISINFECTANT_EVIDENCE,
                    *source_evidence,
                ),
            ),
            _edge(
                "determinant",
                "confers resistance to",
                "ARO:2000001",
                "drug1",
                (
                    target_evidence,
                    _drug_relation_evidence(target, "drug1"),
                    ISONIAZID_EVIDENCE,
                    *source_evidence,
                ),
            ),
            _edge(
                "determinant",
                "enables",
                "RO:0002327",
                "enoyl_reduction",
                enoyl_evidence,
            ),
            _edge(
                "drug0",
                "causally upstream of",
                "RO:0002411",
                "inhibition",
                enoyl_evidence,
            ),
            _edge(
                "determinant",
                "negatively regulates",
                "RO:0002212",
                "inhibition",
                enoyl_evidence,
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


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    target = next((item for item in TARGETS.values() if item.filename == path.name), None)
    if target is None:
        raise ValueError(f"not a FabI target: {path}")

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

    changed = 0
    unchanged = 0
    for target in TARGETS.values():
        path = args.path / target.filename
        before = path.read_text(encoding="utf-8")
        after, did_change = enrich_text(before, path)
        if not did_change:
            unchanged += 1
            continue
        changed += 1
        if args.apply:
            path.write_text(after, encoding="utf-8")
            print(f"  wrote {target.filename}")
        else:
            print(f"  would write {target.filename}")

    if args.apply:
        print(f"changed: {changed}")
        print(f"already enriched: {unchanged}")
    else:
        print(f"would change: {changed}")
        print(f"already enriched: {unchanged}")
        print("dry run -- pass --apply to write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
