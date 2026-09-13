#!/usr/bin/env python3
"""Ground and evidence the conservative antifungal MSH2 graph.

The MSH2 record says only that MSH2 is a mismatch-repair gene and that altered
strains resist several antifungal classes. This updater preserves that cautious
shape, grounds the named DNA mismatch-repair process to GO:0006298, and enriches
the existing four edges without adding an uncited hypermutation route.

Dry-run by default; pass ``--apply`` to write.
"""

from __future__ import annotations

import argparse
import copy
import sys
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from record_io import append_to_section, replace_block  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ARO_DIR = ROOT / "data" / "traits" / "function" / "resistance" / "aro"

HISTORY_ACTION = "Grounded conservative MSH2 mismatch-repair graph"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

IDENTIFIER = "ARO:3009134"
FILENAME = "antifungal-resistance-associated-msh2-aro3009134.yaml"

MUTATION_EVIDENCE = {
    "reference": "ARO:3000212",
    "snippet": (
        "Point mutations in the DNA may lead to an altered gene product that may "
        "result in antibiotic resistance. Examples included modified antibiotic "
        "targets with lower binding affinities and the deactivation of repressors "
        "that result in increased expression of genes that inactivate or pump out "
        "antibiotics."
    ),
    "notes": "CARD definition for the broad mutation-conferring resistance mechanism.",
}

MISMATCH_REPAIR_NODE = {
    "node_id": "mismatch_repair",
    "label": "DNA mismatch repair",
    "node_type": "BIOLOGICAL_PROCESS",
    "grounding": "GO:0006298",
    "description": (
        "Grounded to the GO DNA mismatch repair process named by ARO for MSH2."
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
    ("determinant", "RO:0000056", "mismatch_repair"),
}

EDGE_DESCRIPTIONS = {
    ("determinant", "RO:0000056", "mech0"): (
        "ARO classifies altered MSH2 under mutation conferring antibiotic "
        "resistance."
    ),
    ("mech0", "RO:0002411", "resistance"): (
        "The broad ARO mutation mechanism covers altered gene products that may "
        "result in antibiotic resistance."
    ),
    ("determinant", "RO:0002411", "resistance"): (
        "ARO reports that fungal strains with alterations in MSH2 exhibit "
        "antifungal resistance while leaving the causal route unresolved."
    ),
    ("determinant", "RO:0000056", "mismatch_repair"): (
        "ARO names MSH2 as a fungal mismatch-repair gene."
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


def _edge_key(edge: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(edge.get("subject", "")),
        str(edge.get("predicate_id", "")),
        str(edge.get("object", "")),
    )


def _dicts(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _source_evidence(record: dict[str, Any]) -> tuple[dict[str, str], ...]:
    return tuple(
        {
            "reference": str(item["reference"]),
            "notes": str(item.get("notes") or "ARO citation for this record."),
        }
        for item in _dicts(record.get("evidence"))
        if item.get("reference")
    )


def _own_definition_evidence(record: dict[str, Any]) -> dict[str, str]:
    return {
        "reference": str(record["identifier"]),
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


def _nodes_by_id(graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(node["node_id"]): node
        for node in _dicts(graph.get("nodes"))
        if "node_id" in node
    }


def _validate_graph(graph: dict[str, Any]) -> None:
    nodes = _nodes_by_id(graph)
    missing_nodes = sorted(
        {"determinant", "mech0", "mismatch_repair", "resistance"} - set(nodes)
    )
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{IDENTIFIER}: missing node(s): {missing}")

    found_edges = set()
    seen: set[tuple[str, str, str]] = set()
    for edge in _dicts(graph.get("edges")):
        key = _edge_key(edge)
        if key not in EXPECTED_EDGE_KEYS:
            raise ValueError(f"{IDENTIFIER}: unexpected edge {key[0]} -> {key[2]}")
        if key in seen:
            raise ValueError(f"{IDENTIFIER}: duplicate edge {key[0]} -> {key[2]}")
        seen.add(key)
        found_edges.add(key)

    missing_edges = sorted(EXPECTED_EDGE_KEYS - found_edges)
    if missing_edges:
        missing = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in missing_edges)
        raise ValueError(f"{IDENTIFIER}: missing edge(s): {missing}")


def _canonical_graph(record: dict[str, Any]) -> dict[str, Any]:
    graph = record["causal_graphs"][0]
    _validate_graph(graph)
    nodes = _nodes_by_id(graph)
    own_evidence = _own_definition_evidence(record)
    source_evidence = _source_evidence(record)
    mutation_evidence = (
        own_evidence,
        MUTATION_EVIDENCE,
        *source_evidence,
    )
    mismatch_repair_evidence = (
        own_evidence,
        *source_evidence,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → DNA mismatch repair → antifungal resistance",
        "description": (
            "Conservative graph for antifungal resistance-associated MSH2. The "
            "graph keeps the ARO point-mutation resistance route, grounds the "
            "named DNA mismatch-repair process, and omits a hypermutation route "
            "because ARO does not state it."
        ),
        "nodes": [
            copy.deepcopy(nodes["determinant"]),
            copy.deepcopy(nodes["mech0"]),
            copy.deepcopy(MISMATCH_REPAIR_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                mutation_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                mutation_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                mutation_evidence,
            ),
            _edge(
                "determinant",
                "participates in (DNA mismatch repair)",
                "RO:0000056",
                "mismatch_repair",
                mismatch_repair_evidence,
            ),
        ],
    }


def enrich_record(record: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != IDENTIFIER:
        raise ValueError(f"{FILENAME}: expected {IDENTIFIER}, found {record.get('identifier')}")
    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1 or graphs[0].get("graph_id") != "resistance":
        raise ValueError(f"{IDENTIFIER}: expected exactly one resistance graph")

    out = copy.deepcopy(record)
    out["causal_graphs"] = [_canonical_graph(record)]
    return out, out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    if path.name != FILENAME:
        raise ValueError(f"not the MSH2 target: {path}")

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

    path = args.path / FILENAME
    before = path.read_text(encoding="utf-8")
    after, did_change = enrich_text(before, path)
    if args.apply:
        if did_change:
            path.write_text(after, encoding="utf-8")
            print(f"  wrote {FILENAME}")
        print(f"changed: {int(did_change)}")
        print(f"already enriched: {int(not did_change)}")
    else:
        if did_change:
            print(f"  would write {FILENAME}")
        print(f"would change: {int(did_change)}")
        print(f"already enriched: {int(not did_change)}")
        print("dry run -- pass --apply to write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
