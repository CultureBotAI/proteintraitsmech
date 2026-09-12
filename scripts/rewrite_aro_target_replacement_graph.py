#!/usr/bin/env python3
"""Describe the abstract antibiotic target-replacement graph.

The generic ARO target-replacement parent states that alternate proteins have
the same function as antibiotic-sensitive targets while being structurally
different from those targets. Unlike concrete descendants such as DHFR and
IleRS/Mup enzymes, this abstract parent intentionally does not name the shared
target function, so both same-function and structural-difference claims remain
described local states.

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
HISTORY_ACTION = "Described abstract target-replacement graph"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

TARGET_REPLACEMENT_PROTEIN_EVIDENCE = {
    "reference": "ARO:3000381",
    "snippet": (
        "Alternate proteins that have the same functions as other antibiotic "
        "target proteins, but are structurally different and thus resistant to "
        "antibiotics. These can replace the activity of other "
        "antibiotic-sensitive proteins in the presence of antibiotics."
    ),
    "notes": "CARD definition for antibiotic target replacement proteins.",
}

TARGET_REPLACEMENT_MECHANISM_EVIDENCE = {
    "reference": "ARO:0001002",
    "snippet": "antibiotic target replacement",
    "notes": (
        "ARO mechanism term linked from ARO:3000381 by its participates_in "
        "resistance-mechanism relation."
    ),
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "antibiotic target replacement",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:0001002",
}

SHARED_FUNCTION_NODE = {
    "node_id": "shared_function",
    "label": "functional equivalence to the sensitive target",
    "node_type": "STATE",
    "description": (
        "Local state representing CARD's abstract claim that the replacement "
        "protein has the same function as an antibiotic-sensitive target."
    ),
}

STRUCTURAL_DIFFERENCE_NODE = {
    "node_id": "structural_difference",
    "label": "structural difference from the sensitive target",
    "node_type": "STATE",
    "description": (
        "Local state representing CARD's abstract claim that the replacement "
        "protein is structurally different from antibiotic-sensitive targets."
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

CORE_EDGE_KEYS = {
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("determinant", "RO:0000086", "structural_difference"),
}

LEGACY_SHARED_FUNCTION_EDGE_KEY = (
    "determinant",
    "RO:0002327",
    "shared_function",
)

CANONICAL_SHARED_FUNCTION_EDGE_KEY = (
    "determinant",
    "RO:0000086",
    "shared_function",
)

STRUCTURAL_RESISTANCE_EDGE_KEY = (
    "structural_difference",
    "RO:0002411",
    "resistance",
)


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str


TARGETS = {
    "ARO:3000381": Target(
        identifier="ARO:3000381",
        filename="antibiotic-target-replacement-protein-aro3000381.yaml",
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


def _canonical_edge_keys() -> set[tuple[str, str, str]]:
    return CORE_EDGE_KEYS | {
        CANONICAL_SHARED_FUNCTION_EDGE_KEY,
        STRUCTURAL_RESISTANCE_EDGE_KEY,
    }


def _input_allowed_edges() -> set[tuple[str, str, str]]:
    return _canonical_edge_keys() | {LEGACY_SHARED_FUNCTION_EDGE_KEY}


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
            "evidence": _unique_evidence(evidence),
        }
    )


def _nodes_by_id(graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(node["node_id"]): node
        for node in graph.get("nodes") or []
        if isinstance(node, dict) and "node_id" in node
    }


def _validate_graph(graph: dict[str, Any], target: Target) -> None:
    nodes = _nodes_by_id(graph)
    missing_nodes = sorted(
        {
            "determinant",
            "mech0",
            "shared_function",
            "structural_difference",
            "resistance",
        }
        - set(nodes)
    )
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")

    found_edges = set()
    seen: set[tuple[str, str, str]] = set()
    for edge in graph.get("edges") or []:
        key = _edge_key(edge)
        if key not in _input_allowed_edges():
            raise ValueError(f"{target.identifier}: unexpected edge {key[0]} -> {key[2]}")
        if key in seen:
            raise ValueError(f"{target.identifier}: duplicate edge {key[0]} -> {key[2]}")
        seen.add(key)
        found_edges.add(key)

    missing_core = sorted(CORE_EDGE_KEYS - found_edges)
    if missing_core:
        missing = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in missing_core)
        raise ValueError(f"{target.identifier}: missing core edge(s): {missing}")

    has_shared_edge = (
        LEGACY_SHARED_FUNCTION_EDGE_KEY in found_edges
        or CANONICAL_SHARED_FUNCTION_EDGE_KEY in found_edges
    )
    if not has_shared_edge:
        raise ValueError(f"{target.identifier}: missing shared-function edge")


def _canonical_nodes(graph: dict[str, Any]) -> list[dict[str, Any]]:
    nodes = _nodes_by_id(graph)
    return [
        copy.deepcopy(nodes["determinant"]),
        copy.deepcopy(MECHANISM_NODE),
        copy.deepcopy(SHARED_FUNCTION_NODE),
        copy.deepcopy(STRUCTURAL_DIFFERENCE_NODE),
        copy.deepcopy(RESISTANCE_NODE),
    ]


def _canonical_edges() -> list[dict[str, Any]]:
    mechanism_evidence = (
        TARGET_REPLACEMENT_PROTEIN_EVIDENCE,
        TARGET_REPLACEMENT_MECHANISM_EVIDENCE,
    )

    return [
        _edge(
            "determinant",
            "participates in (resistance mechanism)",
            "RO:0000056",
            "mech0",
            "ARO classifies this parent under antibiotic target replacement.",
            mechanism_evidence,
        ),
        _edge(
            "mech0",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            (
                "The target-replacement mechanism provides an alternate "
                "protein that can substitute for an antibiotic-sensitive target."
            ),
            mechanism_evidence,
        ),
        _edge(
            "determinant",
            "causally upstream of (confers resistance)",
            "RO:0002411",
            "resistance",
            (
                "The replacement protein combines the sensitive target's "
                "function with structural divergence that resists antibiotic "
                "inhibition."
            ),
            mechanism_evidence,
        ),
        _edge(
            "determinant",
            "has quality (same function as the sensitive target)",
            "RO:0000086",
            "shared_function",
            (
                "This local state captures the same-function half of CARD's "
                "abstract target-replacement definition."
            ),
            mechanism_evidence,
        ),
        _edge(
            "determinant",
            "has quality (structurally unlike the sensitive target)",
            "RO:0000086",
            "structural_difference",
            (
                "This local state captures CARD's structurally-different claim "
                "for generic replacement proteins."
            ),
            mechanism_evidence,
        ),
        _edge(
            "structural_difference",
            "causally upstream of (target replacement resists inhibition)",
            "RO:0002411",
            "resistance",
            (
                "CARD states that the replacement proteins are structurally "
                "different and therefore resistant to antibiotics."
            ),
            mechanism_evidence,
        ),
    ]


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != target.identifier:
        raise ValueError(f"expected {target.identifier}, found {record.get('identifier')}")

    out = copy.deepcopy(record)
    before = copy.deepcopy(out.get("causal_graphs"))
    graphs = out.get("causal_graphs") or []
    graph = next((item for item in graphs if item.get("graph_id") == "resistance"), None)
    if graph is None:
        raise ValueError(f"{target.identifier}: missing resistance causal graph")

    _validate_graph(graph, target)
    graph["title"] = f"{record['label']} → target replacement → resistance"
    graph["description"] = (
        "Conservative graph for the abstract antibiotic target-replacement "
        "parent. The shared function and structural difference from the "
        "sensitive target stay as described local states because this parent "
        "does not identify a concrete replaced target."
    )
    graph["nodes"] = _canonical_nodes(graph)
    graph["edges"] = _canonical_edges()
    return out, out.get("causal_graphs") != before


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: record is not a mapping")
    identifier = record.get("identifier")
    target = TARGETS.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not a target-replacement target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
    normalize_aliases = "&id" in text or "*id" in text
    if not changed and not normalize_aliases:
        return text, False

    out = replace_block(
        text,
        "causal_graphs",
        _dump({"causal_graphs": enriched["causal_graphs"]}),
    )
    if HISTORY_ACTION not in out:
        out = append_to_section(
            out,
            "curation_history",
            _dump({"curation_history": [HISTORY_EVENT]}),
        )
    return out, True


def iter_target_paths(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if not path.is_dir():
        raise ValueError(f"{path} is neither a file nor a directory")
    return [path / target.filename for target in TARGETS.values()]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    parser.add_argument(
        "--path",
        type=Path,
        default=ARO_DIR,
        help="ARO directory or the abstract target-replacement YAML file",
    )
    args = parser.parse_args()

    changed = unchanged = 0
    problems: list[str] = []
    for path in iter_target_paths(args.path):
        if not path.exists():
            problems.append(f"{path}: missing")
            continue
        try:
            text = path.read_text(encoding="utf-8")
            out, did_change = enrich_text(text, path)
        except (OSError, ValueError, yaml.YAMLError) as exc:
            problems.append(str(exc))
            continue
        if not did_change:
            unchanged += 1
            continue
        changed += 1
        print(f"  {'wrote' if args.apply else 'would write'} {path.name}")
        if args.apply:
            path.write_text(out, encoding="utf-8")

    print(f"{'changed' if args.apply else 'would change'}: {changed}")
    print(f"already enriched: {unchanged}")
    for problem in problems:
        print(f"PROBLEM: {problem}", file=sys.stderr)
    if not args.apply:
        print("dry run -- pass --apply to write")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
