#!/usr/bin/env python3
"""Ground antibiotic-resistant DHFR target-replacement graph.

The ARO dihydrofolate-reductase parent inherits the broad antibiotic target
replacement graph. Unlike the abstract target-replacement parent, this record
does name the replacement function: dihydrofolate reductase activity. This
updater grounds that activity to GO:0004146, keeps the structural-difference
state local, and describes every edge.

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
HISTORY_ACTION = "Grounded antibiotic-resistant DHFR graph"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

TARGET_REPLACEMENT_EVIDENCE = {
    "reference": "ARO:3000381",
    "snippet": (
        "Alternate proteins that have the same functions as other antibiotic "
        "target proteins, but are structurally different and thus resistant to "
        "antibiotics. These can replace the activity of other "
        "antibiotic-sensitive proteins in the presence of antibiotics."
    ),
    "notes": "CARD definition for antibiotic target replacement proteins.",
}

DHFR_EVIDENCE = {
    "reference": "ARO:3003425",
    "snippet": (
        "Key enzyme in folate metabolism. Catalyzes an essential reaction for "
        "de novo glycine and purine synthesis, and for DNA precursor synthesis."
    ),
    "notes": "CARD definition for antibiotic resistant dihydrofolate reductase.",
}

GO_DHFR_EVIDENCE = {
    "reference": "GO:0004146",
    "snippet": (
        "Catalysis of the reaction: 5,6,7,8-tetrahydrofolate + NADP+ = "
        "7,8-dihydrofolate + NADPH + H+."
    ),
    "notes": "GO definition for dihydrofolate reductase activity.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "antibiotic target replacement",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:0001002",
}

SHARED_FUNCTION_NODE = {
    "node_id": "shared_function",
    "label": "dihydrofolate reductase activity",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "GO:0004146",
}

STRUCTURAL_DIFFERENCE_NODE = {
    "node_id": "structural_difference",
    "label": "structural difference from the sensitive target",
    "node_type": "STATE",
    "description": (
        "Local state representing the target-replacement protein's structural "
        "difference from antibiotic-sensitive target proteins."
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
    ("determinant", "RO:0002327", "shared_function"),
    ("determinant", "RO:0000086", "structural_difference"),
}

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
    "ARO:3003425": Target(
        identifier="ARO:3003425",
        filename="antibiotic-resistant-dihydrofolate-reductase-aro3003425.yaml",
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
    return CORE_EDGE_KEYS | {STRUCTURAL_RESISTANCE_EDGE_KEY}


def _target_evidence(record: dict[str, Any]) -> dict[str, str]:
    return {
        "reference": str(record["identifier"]),
        "snippet": str(record["definition"]),
        "notes": f"CARD definition for {record['label']}.",
    }


def _unique_evidence(evidence: tuple[dict[str, str], ...]) -> list[dict[str, str]]:
    unique: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for item in evidence:
        key = (item["reference"], item["snippet"], item.get("notes", ""))
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
        if key not in _canonical_edge_keys():
            raise ValueError(f"{target.identifier}: unexpected edge {key[0]} -> {key[2]}")
        if key in seen:
            raise ValueError(f"{target.identifier}: duplicate edge {key[0]} -> {key[2]}")
        seen.add(key)
        found_edges.add(key)

    missing_core = sorted(CORE_EDGE_KEYS - found_edges)
    if missing_core:
        missing = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in missing_core)
        raise ValueError(f"{target.identifier}: missing core edge(s): {missing}")


def _canonical_nodes(graph: dict[str, Any]) -> list[dict[str, Any]]:
    nodes = _nodes_by_id(graph)
    return [
        copy.deepcopy(nodes["determinant"]),
        copy.deepcopy(MECHANISM_NODE),
        copy.deepcopy(SHARED_FUNCTION_NODE),
        copy.deepcopy(STRUCTURAL_DIFFERENCE_NODE),
        copy.deepcopy(RESISTANCE_NODE),
    ]


def _canonical_edges(record: dict[str, Any]) -> list[dict[str, Any]]:
    target_evidence = _target_evidence(record)
    replacement_evidence = (target_evidence, TARGET_REPLACEMENT_EVIDENCE)
    function_evidence = (
        target_evidence,
        TARGET_REPLACEMENT_EVIDENCE,
        GO_DHFR_EVIDENCE,
    )

    return [
        _edge(
            "determinant",
            "participates in (resistance mechanism)",
            "RO:0000056",
            "mech0",
            "ARO classifies antibiotic-resistant DHFR under target replacement.",
            replacement_evidence,
        ),
        _edge(
            "mech0",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            "Target replacement allows a structurally different enzyme to act under antibiotic pressure.",
            replacement_evidence,
        ),
        _edge(
            "determinant",
            "causally upstream of (confers resistance)",
            "RO:0002411",
            "resistance",
            (
                "Antibiotic-resistant DHFR preserves an essential folate-metabolism "
                "function while remaining structurally resistant to the drug-sensitive "
                "target it replaces."
            ),
            function_evidence,
        ),
        _edge(
            "determinant",
            "enables",
            "RO:0002327",
            "shared_function",
            (
                "The replacement determinant performs dihydrofolate reductase "
                "activity, the essential function that lets it stand in for a "
                "sensitive target."
            ),
            function_evidence,
        ),
        _edge(
            "determinant",
            "has quality (structurally unlike the sensitive target)",
            "RO:0000086",
            "structural_difference",
            (
                "Structural divergence from sensitive target proteins is the "
                "modeled state that lets replacement proteins resist antibiotic "
                "inhibition."
            ),
            replacement_evidence,
        ),
        _edge(
            "structural_difference",
            "causally upstream of (target replacement resists inhibition)",
            "RO:0002411",
            "resistance",
            (
                "The structurally different replacement protein is therefore "
                "resistant to antibiotics while keeping the same activity."
            ),
            replacement_evidence,
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
    graph["title"] = f"{record['label']} → DHFR target replacement → resistance"
    graph["description"] = (
        "Conservative graph for antibiotic-resistant dihydrofolate reductase as "
        "a target-replacement protein. The graph grounds the shared activity to "
        "GO:0004146 and keeps the broad structural difference from sensitive "
        "target proteins as a described local state."
    )
    graph["nodes"] = _canonical_nodes(graph)
    graph["edges"] = _canonical_edges(out)
    return out, out.get("causal_graphs") != before


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: record is not a mapping")
    identifier = record.get("identifier")
    target = TARGETS.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not an antibiotic-resistant DHFR target: {identifier}")
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
        help="ARO directory or the antibiotic-resistant DHFR YAML file",
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
