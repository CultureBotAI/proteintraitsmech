#!/usr/bin/env python3
"""Rewrite the uhpA fosfomycin graph around reduced importer expression.

The uhpA record states that wild-type UhpA activates the fosfomycin importer
uhpT and that resistance mutations reduce uhpT expression. This updater keeps
the mutant causal chain directly as local states:

    mutated uhpA → reduced uhpT expression → reduced fosfomycin uptake

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

HISTORY_ACTION = "Modeled uhpA reduced fosfomycin uptake route"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

TARGET_IDENTIFIER = "ARO:3003893"
TARGET_FILENAME = "escherichia-coli-uhpa-with-mutation-conferring-resistance-to-fosfomycin-aro3003893.yaml"

UHP_A_EVIDENCE = {
    "reference": TARGET_IDENTIFIER,
    "snippet": (
        "uhpA is a positive activator of the fosfomycin importer uhpT, thus "
        "mutations to uhpA confer fosfomycin resistance by reducing uhpT "
        "expression."
    ),
    "notes": "CARD definition for Escherichia coli uhpA with mutation.",
}

MUTATION_EVIDENCE = {
    "reference": "ARO:3000212",
    "snippet": (
        "Point mutations in the DNA may lead to an altered gene product that "
        "may result in antibiotic resistance."
    ),
    "notes": "CARD definition for mutation conferring antibiotic resistance.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "mutation conferring antibiotic resistance",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3000212",
}

UHP_T_EXPRESSION_NODE = {
    "node_id": "uhpt_expression",
    "label": "reduced uhpT expression",
    "node_type": "STATE",
    "description": (
        "Local state for the reduced expression of the fosfomycin importer "
        "uhpT caused by resistance-conferring uhpA mutations."
    ),
}

FOSFOMYCIN_UPTAKE_NODE = {
    "node_id": "import",
    "label": "reduced fosfomycin uptake",
    "node_type": "STATE",
    "description": (
        "Local state for reduced uptake through the uhpT fosfomycin importer "
        "after uhpT expression drops."
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
    ("determinant", "RO:0002411", "uhpt_expression"),
    ("uhpt_expression", "RO:0002411", "import"),
    ("import", "RO:0002411", "resistance"),
}

OLD_DIRECT_IMPORT_EDGE = ("determinant", "RO:0002212", "import")
OLD_WILDTYPE_ACTIVATION_EDGE = ("determinant", "RO:0002213", "uhpt_expression")

EDGE_DESCRIPTIONS = {
    ("determinant", "RO:0000056", "mech0"): (
        "ARO classifies uhpA fosfomycin resistance under mutation conferring "
        "antibiotic resistance."
    ),
    ("mech0", "RO:0002411", "resistance"): (
        "The uhpA mechanism is a resistance-conferring altered gene product "
        "caused by mutation."
    ),
    ("determinant", "RO:0002411", "resistance"): (
        "Resistance-conferring uhpA mutations reduce expression of the uhpT "
        "fosfomycin importer."
    ),
    ("determinant", "RO:0002411", "uhpt_expression"): (
        "Mutations in the uhpA activator reduce expression of the uhpT "
        "fosfomycin importer."
    ),
    ("uhpt_expression", "RO:0002411", "import"): (
        "Reduced expression of the fosfomycin importer uhpT reduces "
        "fosfomycin uptake."
    ),
    ("import", "RO:0002411", "resistance"): (
        "Reduced fosfomycin uptake is the resistance route ARO places "
        "downstream of uhpA mutation."
    ),
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str


TARGET = Target(identifier=TARGET_IDENTIFIER, filename=TARGET_FILENAME)


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
    missing_nodes = sorted({"determinant", "mech0", "uhpt_expression", "import"} - set(nodes))
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")

    found_edges = set()
    seen: set[tuple[str, str, str]] = set()
    for edge in _dicts(graph.get("edges")):
        key = _edge_key(edge)
        if key in {OLD_DIRECT_IMPORT_EDGE, OLD_WILDTYPE_ACTIVATION_EDGE}:
            continue
        if key not in EXPECTED_EDGE_KEYS:
            raise ValueError(f"{target.identifier}: unexpected edge {key[0]} -> {key[2]}")
        if key in seen:
            raise ValueError(f"{target.identifier}: duplicate edge {key[0]} -> {key[2]}")
        seen.add(key)
        found_edges.add(key)

    old_edges = {OLD_DIRECT_IMPORT_EDGE, OLD_WILDTYPE_ACTIVATION_EDGE}
    if old_edges <= {_edge_key(edge) for edge in _dicts(graph.get("edges"))}:
        required_edges = EXPECTED_EDGE_KEYS - {
            ("determinant", "RO:0002411", "uhpt_expression"),
            ("import", "RO:0002411", "resistance"),
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
    evidence = (
        UHP_A_EVIDENCE,
        MUTATION_EVIDENCE,
        *_source_evidence(record),
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → reduced uhpT expression → reduced fosfomycin uptake",
        "description": (
            "Conservative graph for uhpA-mediated fosfomycin resistance. The "
            "graph models the mutant state directly: resistance-conferring "
            "uhpA mutations reduce expression of the fosfomycin importer uhpT "
            "and thereby reduce fosfomycin uptake."
        ),
        "nodes": [
            copy.deepcopy(nodes["determinant"]),
            copy.deepcopy(MECHANISM_NODE),
            copy.deepcopy(UHP_T_EXPRESSION_NODE),
            copy.deepcopy(FOSFOMYCIN_UPTAKE_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of",
                "RO:0002411",
                "uhpt_expression",
                evidence,
            ),
            _edge(
                "uhpt_expression",
                "causally upstream of",
                "RO:0002411",
                "import",
                evidence,
            ),
            _edge(
                "import",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                evidence,
            ),
        ],
    }


def enrich_record(record: dict[str, Any], target: Target = TARGET) -> tuple[dict[str, Any], bool]:
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
    if path.name != TARGET.filename:
        raise ValueError(f"not the uhpA target: {path}")

    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")
    enriched, changed = enrich_record(record)
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

    path = args.path / TARGET.filename
    before = path.read_text(encoding="utf-8")
    after, changed = enrich_text(before, path)
    if changed:
        if args.apply:
            path.write_text(after, encoding="utf-8")
            print(f"  wrote {TARGET.filename}")
            print("changed: 1")
        else:
            print(f"  would write {TARGET.filename}")
            print("would change: 1")
            print("dry run -- pass --apply to write")
        return 0

    print("changed: 0" if args.apply else "would change: 0")
    print("already enriched: 1")
    if not args.apply:
        print("dry run -- pass --apply to write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
