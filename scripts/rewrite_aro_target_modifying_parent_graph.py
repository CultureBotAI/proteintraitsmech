#!/usr/bin/env python3
"""Make the broad antibiotic-target-modifying-enzyme graph conservative.

ARO:3000519 covers enzymes that modify antibiotic targets generally. Its old
graph modeled the narrower 16S rRNA methyltransferase/decoding-site path from
one descendant branch, which does not apply to the MprF branch. This updater
keeps only the grounded class-level target-alteration route.

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
IDENTIFIER = "ARO:3000519"
FILENAME = "antibiotic-target-modifying-enzyme-aro3000519.yaml"

HISTORY_CURATOR = "codex-causal-graph-quality"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": (
        "Collapsed the broad antibiotic target modifying enzyme graph from a "
        "16S rRNA methyltransferase-specific route to its grounded ARO target "
        "alteration mechanism"
    ),
    "llm_assisted": True,
}

TARGET_ALTERATION_EVIDENCE = {
    "reference": "ARO:0001001",
    "snippet": (
        "Mutational alteration or enzymatic modification of antibiotic target "
        "which results in antibiotic resistance."
    ),
    "notes": "CARD definition for antibiotic target alteration.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "antibiotic target alteration",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:0001001",
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

CANONICAL_EDGES = {
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
}

LEGACY_16S_EDGES = {
    ("determinant", "RO:0002327", "methyltransferase"),
    ("methyltransferase", "RO:0002411", "methylated"),
    ("methylated", "RO:0002212", "decoding_site"),
}

GRAPH_DESCRIPTION = (
    "Conservative graph for the broad antibiotic target modifying enzyme "
    "parent. The graph keeps ARO's enzymatic target-alteration mechanism but "
    "removes the inherited 16S rRNA methyltransferase path because ARO:3000519 "
    "also has non-rRNA descendants."
)


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


def _target_evidence(record: dict[str, Any]) -> dict[str, str]:
    return {
        "reference": IDENTIFIER,
        "snippet": str(record["definition"]),
        "notes": "CARD definition for the antibiotic target modifying enzyme parent.",
    }


def _ordered_edge(edge: dict[str, Any]) -> dict[str, Any]:
    ordered = {
        "subject": edge["subject"],
        "predicate": edge["predicate"],
        "predicate_id": edge["predicate_id"],
        "object": edge["object"],
        "description": edge["description"],
        "evidence": edge["evidence"],
    }
    for key, value in edge.items():
        if key not in ordered:
            ordered[key] = value
    return ordered


def _edge(
    subject: str,
    predicate: str,
    predicate_id: str,
    object_: str,
    description: str,
    evidence: tuple[dict[str, str], ...],
) -> dict[str, Any]:
    return _ordered_edge(
        {
            "subject": subject,
            "predicate": predicate,
            "predicate_id": predicate_id,
            "object": object_,
            "description": description,
            "evidence": [copy.deepcopy(item) for item in evidence],
        }
    )


def _nodes_by_id(graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(node["node_id"]): node
        for node in graph.get("nodes") or []
        if isinstance(node, dict) and "node_id" in node
    }


def _validate_graph(graph: dict[str, Any]) -> None:
    allowed = CANONICAL_EDGES | LEGACY_16S_EDGES
    full_edges = set()
    seen: set[tuple[str, str, str]] = set()
    for edge in graph.get("edges") or []:
        full_key = _edge_key(edge)
        if full_key not in allowed:
            raise ValueError(f"{IDENTIFIER}: unexpected edge {full_key[0]} -> {full_key[2]}")
        if full_key in seen:
            raise ValueError(f"{IDENTIFIER}: duplicate edge {full_key[0]} -> {full_key[2]}")
        seen.add(full_key)
        if full_key in CANONICAL_EDGES:
            full_edges.add(full_key)

    missing_edges = sorted(CANONICAL_EDGES - full_edges)
    if missing_edges:
        missing = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in missing_edges)
        raise ValueError(f"{IDENTIFIER}: missing edge(s): {missing}")


def _canonical_edges(record: dict[str, Any]) -> list[dict[str, Any]]:
    target = _target_evidence(record)
    return [
        _edge(
            "determinant",
            "participates in (resistance mechanism)",
            "RO:0000056",
            "mech0",
            "ARO classifies these enzymes under antibiotic target alteration.",
            (target, TARGET_ALTERATION_EVIDENCE),
        ),
        _edge(
            "mech0",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            (
                "Antibiotic target alteration is the broad resistance mechanism "
                "represented by target-modifying enzymes."
            ),
            (target, TARGET_ALTERATION_EVIDENCE),
        ),
        _edge(
            "determinant",
            "causally upstream of (confers resistance)",
            "RO:0002411",
            "resistance",
            (
                "The determinant is modeled at ARO's broad antibiotic-target "
                "enzymatic-modification level."
            ),
            (target, TARGET_ALTERATION_EVIDENCE),
        ),
    ]


def enrich_record(record: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != IDENTIFIER:
        raise ValueError(f"expected {IDENTIFIER}, found {record.get('identifier')}")

    out = copy.deepcopy(record)
    before = copy.deepcopy(out.get("causal_graphs"))
    graphs = out.get("causal_graphs") or []
    graph = next((item for item in graphs if item.get("graph_id") == "resistance"), None)
    if graph is None:
        raise ValueError(f"{IDENTIFIER}: missing resistance causal graph")

    nodes = _nodes_by_id(graph)
    if "determinant" not in nodes:
        raise ValueError(f"{IDENTIFIER}: missing node(s): determinant")

    _validate_graph(graph)
    graph["nodes"] = [
        copy.deepcopy(nodes["determinant"]),
        copy.deepcopy(MECHANISM_NODE),
        copy.deepcopy(RESISTANCE_NODE),
    ]
    graph["description"] = GRAPH_DESCRIPTION
    graph["edges"] = _canonical_edges(out)
    return out, out.get("causal_graphs") != before


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    if path.name != FILENAME:
        raise ValueError(f"{path}: target {IDENTIFIER} must be in {FILENAME}")

    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: record is not a mapping")

    enriched, changed = enrich_record(record)
    normalize_aliases = "&id" in text or "*id" in text
    if not changed and not normalize_aliases:
        return text, False

    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    if HISTORY_CURATOR not in out:
        out = append_to_section(out, "curation_history", _dump({"curation_history": [HISTORY_EVENT]}))
    return out, True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    parser.add_argument(
        "--path",
        type=Path,
        default=ARO_DIR / FILENAME,
        help=f"target YAML file; defaults to {FILENAME}",
    )
    args = parser.parse_args()

    try:
        text = args.path.read_text(encoding="utf-8")
        out, changed = enrich_text(text, args.path)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"PROBLEM: {exc}", file=sys.stderr)
        return 1

    if changed:
        print(f"  {'wrote' if args.apply else 'would write'} {args.path.name}")
        if args.apply:
            args.path.write_text(out, encoding="utf-8")

    print(f"{'changed' if args.apply else 'would change'}: {int(changed)}")
    print(f"already enriched: {int(not changed)}")
    if not args.apply:
        print("dry run -- pass --apply to write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
