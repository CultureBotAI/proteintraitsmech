#!/usr/bin/env python3
"""Describe and multi-evidence conservative mshA activation-loss graphs.

The drug-specific mshA records already stop at CARD's activation-loss claim:
they do not assert the exact prodrug or reaction. This updater preserves that
conservative topology while adding descriptions and target-specific ARO
evidence to every edge.

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

HISTORY_ACTION = "Completed conservative mshA activation-loss graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

EDGE_ORDER = (
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("determinant", "ARO:2000001", "drug0"),
    ("determinant", "RO:0002212", "activation"),
)
EDGE_KEYS = set(EDGE_ORDER)

FAMILY_EVIDENCE = {
    "reference": "ARO:3004900",
    "snippet": "Mutations that occur in the mshA gene resulting in the inability for antibiotic to activate.",
    "notes": "CARD definition for the antibiotic-resistant mshA parent.",
}

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

DRUG_EVIDENCE = {
    "ARO:3007152": {
        "reference": "ARO:3007152",
        "snippet": "isoniazid-like antibiotic",
        "notes": "ARO drug-class term for the grounded isoniazid-like antibiotic node.",
    },
    "ARO:3007156": {
        "reference": "ARO:3007156",
        "snippet": "thioamide antibiotic",
        "notes": "ARO drug-class term for the grounded thioamide antibiotic node.",
    },
}

EDGE_DESCRIPTIONS = {
    ("determinant", "RO:0000056", "mech0"): (
        "ARO classifies mshA activation-loss determinants under mutation-conferring "
        "antibiotic resistance."
    ),
    ("mech0", "RO:0002411", "resistance"): (
        "The inherited mutation mechanism covers loss of antibiotic activation by mshA."
    ),
    ("determinant", "RO:0002411", "resistance"): (
        "CARD states that mshA mutations leave the antibiotic unable to activate."
    ),
    ("determinant", "ARO:2000001", "drug0"): (
        "ARO maps this mshA determinant to the record-specific drug class."
    ),
    ("determinant", "RO:0002212", "activation"): (
        "mshA mutation prevents antibiotic activation; the exact activation reaction is "
        "not asserted by these CARD records."
    ),
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str


TARGETS = (
    Target("ARO:3004901", "isoniazid-resistant-msha-aro3004901.yaml"),
    Target("ARO:3005107", "prothionamide-resistant-msha-aro3005107.yaml"),
    Target(
        "ARO:3004925",
        "mycobacterium-tuberculosis-msha-mutations-conferring-resistance-to-isoniazid-"
        "aro3004925.yaml",
    ),
    Target(
        "ARO:3005108",
        "mycobacterium-tuberculosis-msha-mutations-conferring-resistance-to-prothionamide-"
        "aro3005108.yaml",
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


def _target_evidence(record: dict[str, Any]) -> dict[str, str]:
    return {
        "reference": str(record["identifier"]),
        "snippet": str(record["definition"]),
        "notes": f"CARD definition for {record['label']}.",
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


def _drug_relation_evidence(edge: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        copy.deepcopy(item)
        for item in _dicts(edge.get("evidence"))
        if str(item.get("snippet", "")).startswith(
            "relationship: confers_resistance_to_drug_class "
        )
    ]


def _validate_graph(graph: dict[str, Any], target: Target) -> None:
    found = {_edge_key(edge) for edge in _dicts(graph.get("edges"))}
    if found != EDGE_KEYS:
        missing = EDGE_KEYS - found
        unexpected = found - EDGE_KEYS
        raise ValueError(f"{target.identifier}: unexpected edge set: {missing=} {unexpected=}")


def _edge(
    subject: str,
    predicate: str,
    predicate_id: str,
    object_: str,
    *evidence: dict[str, Any],
) -> dict[str, Any]:
    return {
        "subject": subject,
        "predicate": predicate,
        "predicate_id": predicate_id,
        "object": object_,
        "description": EDGE_DESCRIPTIONS[(subject, predicate_id, object_)],
        "evidence": _unique_evidence(*evidence),
    }


def _canonical_edges(record: dict[str, Any], graph: dict[str, Any]) -> list[dict[str, Any]]:
    source_evidence = _source_evidence(record)
    target_evidence = _target_evidence(record)
    nodes = _nodes_by_id(graph)
    drug = DRUG_EVIDENCE[str(nodes["drug0"]["grounding"])]
    edges_by_key = {_edge_key(edge): edge for edge in _dicts(graph.get("edges"))}
    route_evidence = (FAMILY_EVIDENCE, MUTATION_EVIDENCE, target_evidence, *source_evidence)
    drug_evidence = (
        *_drug_relation_evidence(edges_by_key[("determinant", "ARO:2000001", "drug0")]),
        FAMILY_EVIDENCE,
        target_evidence,
        drug,
        *source_evidence,
    )

    by_key = {
        ("determinant", "RO:0000056", "mech0"): _edge(
            "determinant",
            "participates in (resistance mechanism)",
            "RO:0000056",
            "mech0",
            *route_evidence,
        ),
        ("mech0", "RO:0002411", "resistance"): _edge(
            "mech0",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            *route_evidence,
        ),
        ("determinant", "RO:0002411", "resistance"): _edge(
            "determinant",
            "causally upstream of (confers resistance)",
            "RO:0002411",
            "resistance",
            *route_evidence,
        ),
        ("determinant", "ARO:2000001", "drug0"): _edge(
            "determinant",
            "confers resistance to (drug class)",
            "ARO:2000001",
            "drug0",
            *drug_evidence,
        ),
        ("determinant", "RO:0002212", "activation"): _edge(
            "determinant",
            "negatively regulates (prevents the antibiotic activating)",
            "RO:0002212",
            "activation",
            *route_evidence,
        ),
    }
    return [by_key[key] for key in EDGE_ORDER]


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != target.identifier:
        raise ValueError(f"expected {target.identifier}, found {record.get('identifier')}")

    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1:
        raise ValueError(f"{target.identifier}: expected exactly one resistance graph")

    graph = graphs[0]
    _validate_graph(graph, target)
    out = copy.deepcopy(record)
    out["causal_graphs"] = [
        {
            "graph_id": "resistance",
            "title": f"{record['label']} → conservative activation-loss resistance core",
            "description": (
                "Conservative graph for a drug-specific mshA record. The graph "
                "keeps CARD's activation-loss mechanism and record-specific drug "
                "class and does not add an unsupported mycothiol or prodrug "
                "reaction."
            ),
            "nodes": copy.deepcopy(graph["nodes"]),
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
        raise ValueError(f"{path}: not an mshA target")

    enriched, changed = enrich_record(record, target)
    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
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
        help="ARO directory or one of the mshA YAML files",
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
        except (OSError, ValueError, yaml.YAMLError, KeyError) as exc:
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
