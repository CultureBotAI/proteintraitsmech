#!/usr/bin/env python3
"""Complete paired Mex core-complex draft graphs.

The paired Mex records are grounded ARO core-complex determinants rather than
single subunits or exact three-component pumps. Their own CARD definitions
support the simple efflux scaffold directly, so this updater promotes the
draft graph by adding descriptions and independent CARD efflux evidence without
inventing an exact outer-membrane partner.

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

HISTORY_ACTION = "Completed paired Mex core-complex graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-11T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

ANTIBIOTIC_EFFLUX_EVIDENCE = {
    "reference": "ARO:0010000",
    "snippet": "Antibiotic resistance via the transport of antibiotics out of the cell.",
    "notes": "CARD definition for the antibiotic efflux resistance mechanism.",
}

EFFLUX_PUMP_EVIDENCE = {
    "reference": "ARO:3000159",
    "snippet": "Efflux proteins that pump antibiotic out of a cell to confer resistance.",
    "notes": "CARD definition for efflux pump complexes and subunits.",
}

EDGE_KEYS = {
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
}
EDGE_ORDER = (
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
)

GRAPH_NODES = [
    "determinant",
    "mech0",
    "resistance",
]


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str


TARGETS = (
    Target("ARO:3009144", "mexab-aro3009144.yaml"),
    Target("ARO:3009145", "mexcd-aro3009145.yaml"),
    Target("ARO:3009146", "mexef-aro3009146.yaml"),
    Target("ARO:3009147", "mexghi-aro3009147.yaml"),
    Target("ARO:3009149", "mexmn-aro3009149.yaml"),
    Target("ARO:3009150", "mexpq-aro3009150.yaml"),
    Target("ARO:3009151", "mexvw-aro3009151.yaml"),
    Target("ARO:3009152", "mexxy-aro3009152.yaml"),
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


def _unique_evidence(*items: dict[str, str]) -> list[dict[str, str]]:
    unique: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in items:
        reference = item["reference"]
        if reference in seen:
            continue
        seen.add(reference)
        unique.append(copy.deepcopy(item))
    return unique


def _record_evidence(record: dict[str, Any]) -> dict[str, str]:
    return {
        "reference": str(record["identifier"]),
        "snippet": str(record["definition"]),
        "notes": f"CARD definition for {record['label']}.",
    }


def _edge(
    subject: str,
    predicate: str,
    predicate_id: str,
    object_: str,
    description: str,
    *evidence: dict[str, str],
) -> dict[str, Any]:
    return {
        "subject": subject,
        "predicate": predicate,
        "predicate_id": predicate_id,
        "object": object_,
        "description": description,
        "evidence": _unique_evidence(*evidence),
    }


def _canonical_graph(record: dict[str, Any], graph: dict[str, Any]) -> dict[str, Any]:
    nodes = _nodes_by_id(graph)
    determinant = str(record["label"])
    record_evidence = _record_evidence(record)
    efflux_evidence = (
        record_evidence,
        EFFLUX_PUMP_EVIDENCE,
        ANTIBIOTIC_EFFLUX_EVIDENCE,
    )
    edges = {
        ("determinant", "RO:0000056", "mech0"): _edge(
            "determinant",
            "participates in (resistance mechanism)",
            "RO:0000056",
            "mech0",
            f"CARD classifies {determinant} under the antibiotic efflux "
            "resistance mechanism.",
            *efflux_evidence,
        ),
        ("mech0", "RO:0002411", "resistance"): _edge(
            "mech0",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            f"The {determinant} core complex expels antibiotic through the "
            "antibiotic-efflux mechanism.",
            *efflux_evidence,
        ),
        ("determinant", "RO:0002411", "resistance"): _edge(
            "determinant",
            "causally upstream of (confers resistance)",
            "RO:0002411",
            "resistance",
            f"{determinant} contributes to multidrug resistance by mediating "
            "antibiotic efflux.",
            *efflux_evidence,
        ),
    }
    return {
        "graph_id": "resistance",
        "title": f"{determinant} → antibiotic efflux → resistance",
        "description": (
            "Curated resistance-causation graph for a paired Mex multidrug "
            "efflux core complex. The determinant is the grounded core complex "
            "that carries out antibiotic efflux with outer-membrane partners."
        ),
        "nodes": [copy.deepcopy(nodes[node_id]) for node_id in GRAPH_NODES],
        "edges": [edges[key] for key in EDGE_ORDER],
    }


def _validate_record(record: dict[str, Any], target: Target) -> None:
    if record.get("identifier") != target.identifier:
        raise ValueError(
            f"{target.filename}: expected {target.identifier}, found "
            f"{record.get('identifier')}"
        )
    if not record.get("label"):
        raise ValueError(f"{target.identifier}: missing label")
    if not record.get("definition"):
        raise ValueError(f"{target.identifier}: missing definition")

    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1:
        raise ValueError(f"{target.identifier}: expected exactly one resistance graph")


def _validate_graph(graph: dict[str, Any], target: Target) -> None:
    nodes = _nodes_by_id(graph)
    missing_nodes = sorted(set(GRAPH_NODES) - set(nodes))
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")

    seen: set[tuple[str, str, str]] = set()
    found: set[tuple[str, str, str]] = set()
    for edge in _dicts(graph.get("edges")):
        key = _edge_key(edge)
        if key not in EDGE_KEYS:
            raise ValueError(f"{target.identifier}: unexpected edge {key}")
        if key in seen:
            raise ValueError(f"{target.identifier}: duplicate edge {key}")
        seen.add(key)
        found.add(key)

    missing_edges = sorted(EDGE_KEYS - found)
    if missing_edges:
        missing = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in missing_edges)
        raise ValueError(f"{target.identifier}: missing edge(s): {missing}")


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    _validate_record(record, target)

    graph = _dicts(record["causal_graphs"])[0]
    _validate_graph(graph, target)

    out = copy.deepcopy(record)
    out["mapping_status"] = "REVIEWED"
    out["causal_graphs"] = [_canonical_graph(record, graph)]
    return out, out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    target = TARGET_BY_FILENAME.get(path.name)
    if target is None:
        raise ValueError(f"{path}: not a paired Mex target")

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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    parser.add_argument(
        "--path",
        type=Path,
        default=ARO_DIR,
        help="ARO directory or one of the paired Mex YAML files",
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
