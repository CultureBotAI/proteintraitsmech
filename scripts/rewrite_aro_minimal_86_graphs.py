#!/usr/bin/env python3
"""Promote minimal score-86 ARO drafts with exact local definitions.

These records have a four-edge ARO scaffold and exact CARD definitions for the
resistance determinant but no record-specific intermediate path worth asserting.
This updater keeps the ARO mechanism and drug-class route, adds descriptions and
exact ARO evidence, and promotes the graph from draft to reviewed.

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

HISTORY_ACTION = "Promoted minimal exact-definition resistance graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
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

EDGE_KEYS = {
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("determinant", "ARO:2000001", "drug0"),
}
EDGE_ORDER = (
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("determinant", "ARO:2000001", "drug0"),
)


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str


TARGETS = (
    Target(
        "ARO:3004561",
        "clostridioides-difficile-murg-with-mutation-conferring-resistance-to-"
        "vancomycin-aro3004561.yaml",
    ),
    Target("ARO:3004046", "kdpde-aro3004046.yaml"),
    Target("ARO:3004265", "lysocin-resistant-mena-aro3004265.yaml"),
    Target("ARO:3004560", "murg-transferase-aro3004560.yaml"),
    Target(
        "ARO:3003917",
        "staphylococcus-aureus-mena-with-mutation-conferring-resistance-to-"
        "lysocin-aro3003917.yaml",
    ),
)
TARGET_BY_FILENAME = {target.filename: target for target in TARGETS}


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


def _unique_evidence(*items: dict[str, Any]) -> list[dict[str, Any]]:
    unique: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for item in items:
        key = (
            str(item["reference"]),
            str(item.get("snippet", "")),
            str(item.get("notes", "")),
        )
        if key in seen:
            continue
        seen.add(key)
        unique.append(copy.deepcopy(item))
    return unique


def _source_evidence(record: dict[str, Any]) -> tuple[dict[str, str], ...]:
    return tuple(
        {
            "reference": str(item["reference"]),
            "notes": str(item.get("notes") or "ARO citation for this record."),
        }
        for item in _dicts(record.get("evidence"))
        if item.get("reference")
    )


def _target_evidence(record: dict[str, Any]) -> dict[str, str]:
    return {
        "reference": str(record["identifier"]),
        "snippet": str(record["definition"]),
        "notes": f"CARD definition for {record['label']}.",
    }


def _drug_relation_evidence(graph: dict[str, Any]) -> list[dict[str, Any]]:
    for edge in _dicts(graph.get("edges")):
        if _edge_key(edge) == ("determinant", "ARO:2000001", "drug0"):
            return [
                copy.deepcopy(item)
                for item in _dicts(edge.get("evidence"))
                if str(item.get("snippet", "")).startswith(
                    "relationship: confers_resistance_to_drug_class "
                )
            ]
    return []


def _mechanism_evidence(graph: dict[str, Any]) -> dict[str, str]:
    mechanism = _nodes_by_id(graph)["mech0"]
    reference = mechanism["grounding"]
    for edge in _dicts(graph.get("edges")):
        for item in _dicts(edge.get("evidence")):
            if item.get("reference") == reference and item.get("snippet"):
                return {
                    "reference": str(item["reference"]),
                    "snippet": str(item["snippet"]),
                    "notes": f"CARD definition for {mechanism['label']}.",
                }
    raise ValueError(f"missing CARD mechanism evidence for {reference}")


def _drug_term_evidence(graph: dict[str, Any]) -> dict[str, str]:
    drug = _nodes_by_id(graph)["drug0"]
    return {
        "reference": str(drug["grounding"]),
        "snippet": str(drug["label"]),
        "notes": "ARO drug-class term for the grounded drug-class node.",
    }


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


def _validate_graph(graph: dict[str, Any], target: Target) -> None:
    missing_nodes = sorted(
        {"determinant", "mech0", "drug0", "resistance"} - _nodes_by_id(graph).keys()
    )
    if missing_nodes:
        raise ValueError(f"{target.identifier}: missing node(s): {', '.join(missing_nodes)}")

    found: set[tuple[str, str, str]] = set()
    for edge in _dicts(graph.get("edges")):
        key = _edge_key(edge)
        if key not in EDGE_KEYS:
            raise ValueError(f"{target.identifier}: unexpected edge {key[0]} -> {key[2]}")
        if key in found:
            raise ValueError(f"{target.identifier}: duplicate edge {key[0]} -> {key[2]}")
        found.add(key)

    missing_edges = sorted(EDGE_KEYS - found)
    if missing_edges:
        missing = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in missing_edges)
        raise ValueError(f"{target.identifier}: missing edge(s): {missing}")

    if not _drug_relation_evidence(graph):
        raise ValueError(f"{target.identifier}: missing ARO drug-relation evidence")


def _canonical_edges(record: dict[str, Any], graph: dict[str, Any]) -> list[dict[str, Any]]:
    target_evidence = _target_evidence(record)
    source_evidence = _source_evidence(record)
    mechanism_evidence = _mechanism_evidence(graph)
    mechanism = _nodes_by_id(graph)["mech0"]
    drug = _nodes_by_id(graph)["drug0"]
    route_evidence = (
        target_evidence,
        mechanism_evidence,
        *source_evidence,
    )
    drug_evidence = (
        *_drug_relation_evidence(graph),
        target_evidence,
        _drug_term_evidence(graph),
        *source_evidence,
    )

    by_key = {
        ("determinant", "RO:0000056", "mech0"): _edge(
            "determinant",
            "participates in (resistance mechanism)",
            "RO:0000056",
            "mech0",
            f"ARO classifies this determinant under {mechanism['label']}.",
            *route_evidence,
        ),
        ("mech0", "RO:0002411", "resistance"): _edge(
            "mech0",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            f"The ARO {mechanism['label']} mechanism contributes to antibiotic resistance.",
            *route_evidence,
        ),
        ("determinant", "RO:0002411", "resistance"): _edge(
            "determinant",
            "causally upstream of (confers resistance)",
            "RO:0002411",
            "resistance",
            "The local ARO definition states that this determinant confers resistance.",
            *route_evidence,
        ),
        ("determinant", "ARO:2000001", "drug0"): _edge(
            "determinant",
            "confers resistance to (drug class)",
            "ARO:2000001",
            "drug0",
            f"ARO maps this determinant to {drug['label']}.",
            *drug_evidence,
        ),
    }
    return [by_key[key] for key in EDGE_ORDER]


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != target.identifier:
        raise ValueError(f"expected {target.identifier}, found {record.get('identifier')}")

    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1 or graphs[0].get("graph_id") not in {"resistance-draft", "resistance"}:
        raise ValueError(f"{target.identifier}: expected exactly one resistance graph")

    graph = graphs[0]
    _validate_graph(graph, target)
    nodes = _nodes_by_id(graph)

    out = copy.deepcopy(record)
    out["mapping_status"] = "REVIEWED"
    out["causal_graphs"] = [
        {
            "graph_id": "resistance",
            "title": f"{record['label']} → mechanism → resistance",
            "description": (
                "Conservative graph promoted from the ARO scaffold. The graph "
                "keeps the ARO mechanism and drug-class assertions and stops "
                "before any unstated determinant-specific downstream route."
            ),
            "nodes": [
                copy.deepcopy(nodes["determinant"]),
                copy.deepcopy(nodes["mech0"]),
                copy.deepcopy(nodes["drug0"]),
                copy.deepcopy(RESISTANCE_NODE),
            ],
            "edges": _canonical_edges(record, graph),
        }
    ]
    return out, out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: record is not a mapping")

    target = TARGET_BY_FILENAME.get(path.name)
    if target is None:
        raise ValueError(f"{path}: not a minimal score-86 target")

    enriched, changed = enrich_record(record, target)
    out = text.replace("mapping_status: SEEDED", "mapping_status: REVIEWED", 1)
    out = replace_block(out, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    if HISTORY_ACTION not in out:
        out = append_to_section(out, "curation_history", _dump({"curation_history": [HISTORY_EVENT]}))
        changed = True

    if "&id" in out or "*id" in out:
        raise ValueError(f"{path}: YAML anchors leaked into output")
    return out, changed or out != text


def iter_target_paths(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if not path.is_dir():
        raise ValueError(f"{path} is neither a file nor a directory")
    return [path / target.filename for target in TARGETS]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    parser.add_argument(
        "--path",
        type=Path,
        default=ARO_DIR,
        help="ARO directory or one of the minimal score-86 YAML files",
    )
    args = parser.parse_args()

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
