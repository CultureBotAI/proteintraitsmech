#!/usr/bin/env python3
"""Rewrite the Van ligase graph around generic alternative precursor states.

Van ligases synthesize alternative peptidoglycan precursors that reduce
vancomycin binding. The previous graph represented the generic alternative
precursor as an ungrounded chemical; this updater models it as a described local
state because exact Van ligase products vary by D-Ala-D-Lac or D-Ala-D-Ser
branch.

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

HISTORY_ACTION = "Modeled Van ligase alternative precursor route"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

TARGET_IDENTIFIER = "ARO:3002906"
TARGET_FILENAME = "van-ligase-aro3002906.yaml"

VAN_LIGASE_EVIDENCE = {
    "reference": TARGET_IDENTIFIER,
    "snippet": (
        "Van ligases synthesize alternative substrates for peptidoglycan "
        "synthesis that reduce vancomycin binding affinity."
    ),
    "notes": "CARD definition for Van ligase.",
}

CELL_WALL_RESTRUCTURING_EVIDENCE = {
    "reference": "ARO:3000213",
    "snippet": (
        "Peptidoglycan precursors ending in D-Ala-D-Lac or D-Ala-D-Ser instead "
        "of D-Ala-D-Ala conferring high level glycopeptide resistance."
    ),
    "notes": "CARD definition for restructuring of bacterial cell wall.",
}

GLYCOPEPTIDE_EVIDENCE = {
    "reference": "ARO:3000081",
    "snippet": "glycopeptide antibiotic",
    "notes": "ARO drug-class term asserted on Van ligase.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "restructuring of bacterial cell wall conferring antibiotic resistance",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3000213",
}

GLYCOPEPTIDE_NODE = {
    "node_id": "drug0",
    "label": "glycopeptide antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:3000081",
}

ALTERNATIVE_PRECURSOR_NODE = {
    "node_id": "alt_precursor",
    "label": "alternative peptidoglycan precursor",
    "node_type": "STATE",
    "description": (
        "Local state for the alternative peptidoglycan precursors synthesized "
        "by Van ligases; the exact depsipeptide varies by Van branch."
    ),
}

LOW_AFFINITY_NODE = {
    "node_id": "low_affinity",
    "label": "reduced vancomycin binding affinity",
    "node_type": "STATE",
    "description": (
        "Local state for reduced vancomycin binding affinity downstream of "
        "alternative peptidoglycan precursor synthesis."
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
    ("determinant", "RO:0002411", "alt_precursor"),
    ("alt_precursor", "RO:0002411", "low_affinity"),
    ("low_affinity", "RO:0002411", "resistance"),
}

OLD_PRECURSOR_EDGE = ("determinant", "RO:0002327", "alt_precursor")
OLD_DOMAIN_EDGE_KEYS = {
    ("domain", "BFO:0000050", "determinant"),
    ("determinant", "RO:0002350", "fold"),
    ("domain", "RO:0002327", "mech0"),
}
OLD_DALA_DSER_EDGE_KEYS = {
    ("precursor_ser", "RO:0002212", "precursor_dala"),
    ("drug0", "RO:0002436", "precursor_dala"),
    ("determinant", "RO:0002327", "ligase_activity"),
    ("ligase_activity", "RO:0002234", "dala_dser"),
    ("dala_dser", "RO:0002411", "precursor_ser"),
}

EDGE_DESCRIPTIONS = {
    ("determinant", "RO:0000056", "mech0"): (
        "ARO classifies Van ligases under cell-wall restructuring resistance."
    ),
    ("mech0", "RO:0002411", "resistance"): (
        "The Van ligase route replaces D-Ala-D-Ala-ending precursors with "
        "D-Ala-D-Lac or D-Ala-D-Ser-ending precursors."
    ),
    ("determinant", "RO:0002411", "resistance"): (
        "Van ligases synthesize alternative peptidoglycan substrates that "
        "reduce vancomycin binding affinity."
    ),
    ("determinant", "ARO:2000001", "drug0"): (
        "ARO maps Van ligase to glycopeptide antibiotics."
    ),
    ("determinant", "RO:0002411", "alt_precursor"): (
        "Van ligases synthesize alternative substrates for peptidoglycan "
        "synthesis."
    ),
    ("alt_precursor", "RO:0002411", "low_affinity"): (
        "The alternative peptidoglycan precursors synthesized by Van ligases "
        "reduce vancomycin binding affinity."
    ),
    ("low_affinity", "RO:0002411", "resistance"): (
        "Reduced vancomycin binding affinity is the glycopeptide-resistance "
        "consequence of alternative precursor synthesis."
    ),
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str


TARGETS: tuple[Target, ...] = (
    Target(identifier=TARGET_IDENTIFIER, filename=TARGET_FILENAME),
    Target(identifier="ARO:3000010", filename="vana-aro3000010.yaml"),
    Target(identifier="ARO:3000013", filename="vanb-aro3000013.yaml"),
    Target(identifier="ARO:3000005", filename="vand-aro3000005.yaml"),
    Target(identifier="ARO:3002908", filename="vanf-aro3002908.yaml"),
    Target(identifier="ARO:3003723", filename="vani-aro3003723.yaml"),
    Target(identifier="ARO:3002911", filename="vanm-aro3002911.yaml"),
    Target(identifier="ARO:3002913", filename="vano-aro3002913.yaml"),
    Target(identifier="ARO:3007189", filename="vanp-aro3007189.yaml"),
    Target(identifier="ARO:3000368", filename="vanc-aro3000368.yaml"),
    Target(identifier="ARO:3002907", filename="vane-aro3002907.yaml"),
    Target(identifier="ARO:3002909", filename="vang-aro3002909.yaml"),
    Target(identifier="ARO:3002910", filename="vanl-aro3002910.yaml"),
    Target(identifier="ARO:3002912", filename="vann-aro3002912.yaml"),
)
TARGET = TARGETS[0]
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
    missing_nodes = sorted({"determinant", "mech0", "drug0", "resistance"} - set(nodes))
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")

    found_edges = set()
    seen: set[tuple[str, str, str]] = set()
    old_edge_keys = {_edge_key(edge) for edge in _dicts(graph.get("edges"))}
    for edge in _dicts(graph.get("edges")):
        key = _edge_key(edge)
        if key == OLD_PRECURSOR_EDGE or key in OLD_DOMAIN_EDGE_KEYS or key in OLD_DALA_DSER_EDGE_KEYS:
            continue
        if key not in EXPECTED_EDGE_KEYS:
            raise ValueError(f"{target.identifier}: unexpected edge {key[0]} -> {key[2]}")
        if key in seen:
            raise ValueError(f"{target.identifier}: duplicate edge {key[0]} -> {key[2]}")
        seen.add(key)
        found_edges.add(key)

    if OLD_PRECURSOR_EDGE in old_edge_keys:
        required_edges = EXPECTED_EDGE_KEYS - {
            ("determinant", "RO:0002411", "alt_precursor"),
            ("low_affinity", "RO:0002411", "resistance"),
        }
    else:
        required_edges = EXPECTED_EDGE_KEYS

    minimal_edges = {
        ("determinant", "RO:0000056", "mech0"),
        ("mech0", "RO:0002411", "resistance"),
        ("determinant", "RO:0002411", "resistance"),
        ("determinant", "ARO:2000001", "drug0"),
    }
    missing_edges = sorted((required_edges & old_edge_keys | minimal_edges) - found_edges)
    if missing_edges:
        missing = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in missing_edges)
        raise ValueError(f"{target.identifier}: missing edge(s): {missing}")

    if not _drug_relation_evidence(graph):
        raise ValueError(f"{target.identifier}: missing Van-ligase ARO drug relation evidence")


def _drug_relation_evidence(graph: dict[str, Any]) -> tuple[dict[str, str], ...]:
    evidence: list[dict[str, str]] = []
    for edge in _dicts(graph.get("edges")):
        if (
            edge.get("subject") == "determinant"
            and edge.get("predicate_id") == "ARO:2000001"
            and edge.get("object") == "drug0"
        ):
            for item in _dicts(edge.get("evidence")):
                if item.get("reference") and str(item.get("snippet", "")).startswith(
                    "relationship: confers_resistance_to_drug_class ARO:3000081"
                ):
                    evidence.append(copy.deepcopy(item))
    return tuple(evidence)


def _canonical_graph(record: dict[str, Any], target: Target) -> dict[str, Any]:
    graph = record["causal_graphs"][0]
    _validate_graph(graph, target)
    nodes = _nodes_by_id(graph)
    source_evidence = _source_evidence(record)
    target_evidence = _target_evidence(record)
    mechanism_evidence = (
        target_evidence,
        VAN_LIGASE_EVIDENCE,
        CELL_WALL_RESTRUCTURING_EVIDENCE,
        *source_evidence,
    )
    drug_evidence = (
        *_drug_relation_evidence(graph),
        GLYCOPEPTIDE_EVIDENCE,
        target_evidence,
        VAN_LIGASE_EVIDENCE,
        *source_evidence,
    )
    precursor_evidence = (
        target_evidence,
        VAN_LIGASE_EVIDENCE,
        CELL_WALL_RESTRUCTURING_EVIDENCE,
        *source_evidence,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → alternative peptidoglycan precursors",
        "description": (
            "Conservative graph for Van ligase-mediated glycopeptide "
            "resistance. The graph represents alternative peptidoglycan "
            "substrates as a local state because the exact precursor differs "
            "by Van branch, and it keeps reduced vancomycin binding affinity "
            "downstream of that alternative-precursor state."
        ),
        "nodes": [
            copy.deepcopy(nodes["determinant"]),
            copy.deepcopy(MECHANISM_NODE),
            copy.deepcopy(GLYCOPEPTIDE_NODE),
            copy.deepcopy(ALTERNATIVE_PRECURSOR_NODE),
            copy.deepcopy(LOW_AFFINITY_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                mechanism_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                mechanism_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                precursor_evidence,
            ),
            _edge(
                "determinant",
                "confers resistance to (drug class)",
                "ARO:2000001",
                "drug0",
                drug_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of",
                "RO:0002411",
                "alt_precursor",
                precursor_evidence,
            ),
            _edge(
                "alt_precursor",
                "causally upstream of",
                "RO:0002411",
                "low_affinity",
                precursor_evidence,
            ),
            _edge(
                "low_affinity",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                precursor_evidence,
            ),
        ],
    }


def enrich_record(
    record: dict[str, Any],
    target: Target = TARGET,
) -> tuple[dict[str, Any], bool]:
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
    target = TARGET_BY_FILENAME.get(path.name)
    if target is None:
        raise ValueError(f"not the Van ligase target: {path}")

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


def iter_target_paths(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if not path.is_dir():
        raise ValueError(f"{path} is neither a file nor a directory")
    return [path / target.filename for target in TARGETS]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument(
        "--path",
        type=Path,
        default=ARO_DIR,
        help="ARO directory or one of the fourteen D-Ala-D-Lac/D-Ala-D-Ser Van-ligase YAML files",
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
