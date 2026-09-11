#!/usr/bin/env python3
"""Prune ethambutol-resistant iniB graphs to a mutation core.

The ethambutol-resistant iniB records support a point-mutation resistance core
and an inherited polyamine-antibiotic drug-class edge. Their broad iniBAC parent
only hedges a possible MDR-pump-like mechanism, so this updater drops the
auto-scaffolded antibiotic-efflux side path instead of treating efflux as a
record-local causal claim.

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

HISTORY_ACTION = "Pruned ethambutol-resistant iniB graphs to a mutation core"
HISTORY_EVENT = {
    "timestamp": "2026-09-11T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

INITIAL_EDGE_KEYS = {
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0000056", "mech1"),
    ("mech1", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("determinant", "ARO:2000001", "drug0"),
}
FINAL_EDGE_ORDER = (
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("determinant", "ARO:2000001", "drug0"),
)
FINAL_EDGE_KEYS = set(FINAL_EDGE_ORDER)

PARENT_EVIDENCE = {
    "reference": "ARO:3004136",
    "snippet": (
        "Point mutations occurring in the iniB region of the iniBAC operon "
        "shown to confer resistance to ethambutol."
    ),
    "notes": "CARD definition for the ethambutol-resistant iniB parent.",
}

MUTATION_EVIDENCE = {
    "reference": "ARO:3000212",
    "snippet": (
        "Point mutations in the DNA may lead to an altered gene product that "
        "may result in antibiotic resistance. Examples included modified "
        "antibiotic targets with lower binding affinities and the deactivation "
        "of repressors that result in increased expression of genes that "
        "inactivate or pump out antibiotics."
    ),
    "notes": "CARD definition for the broad mutation-conferring resistance mechanism.",
}

POLYAMINE_EVIDENCE = {
    "reference": "ARO:3000527",
    "snippet": "polyamine antibiotic",
    "notes": "ARO drug-class term for the grounded polyamine antibiotic node.",
}

EDGE_DESCRIPTIONS = {
    ("determinant", "RO:0000056", "mech0"): (
        "ARO classifies this ethambutol-resistant iniB determinant under "
        "mutation-conferring antibiotic resistance."
    ),
    ("mech0", "RO:0002411", "resistance"): (
        "The inherited mutation mechanism is upstream of ethambutol resistance."
    ),
    ("determinant", "RO:0002411", "resistance"): (
        "CARD states that point mutations in this iniB determinant confer "
        "ethambutol resistance."
    ),
    ("determinant", "ARO:2000001", "drug0"): (
        "ARO maps this determinant or its ethambutol-resistant iniB parent to "
        "the polyamine antibiotic drug class."
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


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str

    @property
    def is_parent(self) -> bool:
        return self.identifier == "ARO:3004136"


TARGETS = (
    Target("ARO:3004136", "ethambutol-resistant-inib-aro3004136.yaml"),
    Target(
        "ARO:3004135",
        "mycobacterium-tuberculosis-inib-with-mutation-conferring-resistance-to-"
        "ethambuto-aro3004135.yaml",
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


def _record_evidence(record: dict[str, Any]) -> dict[str, str]:
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


def _direct_antibiotic_evidence(graph: dict[str, Any]) -> list[dict[str, Any]]:
    for edge in _dicts(graph.get("edges")):
        if _edge_key(edge) == ("determinant", "RO:0002411", "resistance"):
            return [
                copy.deepcopy(item)
                for item in _dicts(edge.get("evidence"))
                if str(item.get("snippet", "")).startswith(
                    "relationship: confers_resistance_to_antibiotic "
                )
            ]
    return []


def _validate_graph(graph: dict[str, Any], target: Target) -> None:
    found = {_edge_key(edge) for edge in _dicts(graph.get("edges"))}
    if found != INITIAL_EDGE_KEYS and found != FINAL_EDGE_KEYS:
        expected = INITIAL_EDGE_KEYS | FINAL_EDGE_KEYS
        unexpected = found - expected
        raise ValueError(
            f"{target.identifier}: unexpected edge set: "
            f"missing_initial={INITIAL_EDGE_KEYS - found} "
            f"missing_final={FINAL_EDGE_KEYS - found} {unexpected=}"
        )


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


def _canonical_edges(
    record: dict[str, Any],
    graph: dict[str, Any],
    target: Target,
) -> list[dict[str, Any]]:
    local_evidence = () if target.is_parent else (_record_evidence(record),)
    source_evidence = _source_evidence(record)
    route_evidence = (PARENT_EVIDENCE, MUTATION_EVIDENCE, *local_evidence, *source_evidence)
    resistance_evidence = (
        PARENT_EVIDENCE,
        MUTATION_EVIDENCE,
        *local_evidence,
        *_direct_antibiotic_evidence(graph),
        *source_evidence,
    )
    drug_evidence = (
        *_drug_relation_evidence(graph),
        PARENT_EVIDENCE,
        POLYAMINE_EVIDENCE,
        *local_evidence,
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
            *resistance_evidence,
        ),
        ("determinant", "RO:0002411", "resistance"): _edge(
            "determinant",
            "causally upstream of (confers resistance)",
            "RO:0002411",
            "resistance",
            *resistance_evidence,
        ),
        ("determinant", "ARO:2000001", "drug0"): _edge(
            "determinant",
            "confers resistance to (drug class)",
            "ARO:2000001",
            "drug0",
            *drug_evidence,
        ),
    }
    return [by_key[key] for key in FINAL_EDGE_ORDER]


def _mutation_node(nodes: dict[str, dict[str, Any]]) -> dict[str, Any]:
    node = copy.deepcopy(nodes.get("mech1") or nodes["mech0"])
    node["node_id"] = "mech0"
    return node


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != target.identifier:
        raise ValueError(f"expected {target.identifier}, found {record.get('identifier')}")

    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1:
        raise ValueError(f"{target.identifier}: expected exactly one resistance graph")

    graph = graphs[0]
    _validate_graph(graph, target)
    nodes = _nodes_by_id(graph)

    out = copy.deepcopy(record)
    out["mapping_status"] = "REVIEWED"
    out["causal_graphs"] = [
        {
            "graph_id": "resistance",
            "title": f"{record['label']} → ethambutol resistance mutation core",
            "description": (
                "Conservative graph for an ethambutol-resistant iniB determinant. "
                "The graph keeps CARD's broad mutation mechanism and polyamine "
                "drug-class assertion and prunes the weak inherited antibiotic-efflux "
                "side path."
            ),
            "nodes": [
                copy.deepcopy(nodes["determinant"]),
                _mutation_node(nodes),
                copy.deepcopy(nodes["drug0"]),
                copy.deepcopy(RESISTANCE_NODE),
            ],
            "edges": _canonical_edges(record, graph, target),
        }
    ]
    return out, out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: record is not a mapping")

    target = TARGET_BY_FILENAME.get(path.name)
    if target is None:
        raise ValueError(f"{path}: not an ethambutol-resistant iniB target")

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
        help="ARO directory or one ethambutol-resistant iniB YAML file",
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
