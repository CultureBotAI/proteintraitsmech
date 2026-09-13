#!/usr/bin/env python3
"""Rewrite the abstract antibiotic target-protection protein graph.

The ARO:3000185 parent states only the family-level mechanism: these proteins
bind antibiotic targets and thereby prevent antibiotic binding. Its children
instantiate several concrete cases, but the parent should stay target-neutral
instead of naming a ribosome, EF-G, RNA polymerase, or a drug family.

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

HISTORY_CURATOR = "codex-causal-graph-quality"
HISTORY_ACTION = "Grounded antibiotic target-protection parent graph"
HISTORY_EVENT = {
    "timestamp": "2026-09-08T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

TARGET_PROTEIN_EVIDENCE = {
    "reference": "ARO:3000185",
    "snippet": (
        "These proteins confer antibiotic resistance by bind the antibiotic "
        "target to prevent antibiotic binding."
    ),
    "notes": "CARD definition for antibiotic target protection protein.",
}

TARGET_PROTECTION_EVIDENCE = {
    "reference": "ARO:0001003",
    "snippet": (
        "Protection of antibiotic action target from antibiotic binding, "
        "which process will result in antibiotic resistance."
    ),
    "notes": "CARD definition for antibiotic target protection.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "antibiotic target protection",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:0001003",
}

TARGET_BINDING_NODE = {
    "node_id": "target_binding",
    "label": "target-protection protein bound to antibiotic target",
    "node_type": "STATE",
    "description": (
        "Local state for the determinant binding the unspecified antibiotic "
        "action target named by the ARO definitions."
    ),
}

BLOCKED_BINDING_NODE = {
    "node_id": "blocked_binding",
    "label": "antibiotic binding to target blocked",
    "node_type": "STATE",
    "description": (
        "Local state for protection of an unspecified antibiotic action "
        "target from antibiotic binding."
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

INPUT_ALLOWED_EDGE_KEYS = {
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("determinant", "RO:0002436", "target"),
    ("determinant", "RO:0002411", "blocked_binding"),
    ("determinant", "RO:0002411", "target_binding"),
    ("target_binding", "RO:0002411", "blocked_binding"),
    ("blocked_binding", "RO:0002411", "resistance"),
}

CORE_INPUT_EDGE_KEYS = {
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
}

OUTPUT_EDGE_KEYS = {
    *CORE_INPUT_EDGE_KEYS,
    ("determinant", "RO:0002411", "target_binding"),
    ("target_binding", "RO:0002411", "blocked_binding"),
    ("blocked_binding", "RO:0002411", "resistance"),
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str


TARGET = Target(
    "ARO:3000185",
    "antibiotic-target-protection-protein-aro3000185.yaml",
)
TARGETS = (TARGET,)
TARGET_BY_ID = {TARGET.identifier: TARGET}


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


def _unique_evidence(*items: dict[str, Any]) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
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


def _nodes_by_id(graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(node["node_id"]): node
        for node in _dicts(graph.get("nodes"))
        if "node_id" in node
    }


def _determinant_node(record: dict[str, Any]) -> dict[str, str]:
    return {
        "node_id": "determinant",
        "label": str(record["label"]),
        "node_type": "PROTEIN",
        "grounding": str(record["identifier"]),
    }


def _validate_graph(graph: dict[str, Any], target: Target) -> None:
    nodes = _nodes_by_id(graph)
    required_nodes = {"determinant", "mech0", "resistance"}
    missing_nodes = sorted(required_nodes - set(nodes))
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")

    found: set[tuple[str, str, str]] = set()
    seen: set[tuple[str, str, str]] = set()
    for edge in _dicts(graph.get("edges")):
        key = _edge_key(edge)
        if key not in INPUT_ALLOWED_EDGE_KEYS:
            raise ValueError(f"{target.identifier}: unexpected edge {key[0]} -> {key[2]}")
        if key in seen:
            raise ValueError(f"{target.identifier}: duplicate edge {key[0]} -> {key[2]}")
        seen.add(key)
        found.add(key)

    missing_edges = sorted(CORE_INPUT_EDGE_KEYS - found)
    if missing_edges:
        missing = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in missing_edges)
        raise ValueError(f"{target.identifier}: missing edge(s): {missing}")


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


def _graph(record: dict[str, Any]) -> dict[str, Any]:
    common_evidence = (
        _record_evidence(record),
        TARGET_PROTEIN_EVIDENCE,
        TARGET_PROTECTION_EVIDENCE,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → blocked antibiotic binding → antibiotic resistance",
        "description": (
            "Conservative graph for the generic antibiotic target-protection "
            "protein parent. The graph represents binding and protection as "
            "local states because ARO:3000185 does not name a specific "
            "target, target class, or drug class."
        ),
        "nodes": [
            _determinant_node(record),
            copy.deepcopy(MECHANISM_NODE),
            copy.deepcopy(TARGET_BINDING_NODE),
            copy.deepcopy(BLOCKED_BINDING_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "ARO classifies the determinant under antibiotic target protection.",
                *common_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Protection of antibiotic action targets from antibiotic binding results in resistance.",
                *common_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "Target-protection proteins confer resistance by preventing antibiotic binding.",
                *common_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (binds the antibiotic target)",
                "RO:0002411",
                "target_binding",
                (
                    "The determinant binds the unspecified antibiotic target "
                    "named by the generic parent definition."
                ),
                *common_evidence,
            ),
            _edge(
                "target_binding",
                "causally upstream of",
                "RO:0002411",
                "blocked_binding",
                "Binding of the protection protein prevents antibiotic binding to the target.",
                *common_evidence,
            ),
            _edge(
                "blocked_binding",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Blocked antibiotic binding to the action target results in resistance.",
                *common_evidence,
            ),
        ],
    }


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    _validate_record(record, target)

    out = copy.deepcopy(record)
    out["causal_graphs"] = [_graph(record)]
    return out, out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not a target-protection target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    if HISTORY_ACTION not in out:
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
        help="ARO directory or the antibiotic target-protection protein YAML file",
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
