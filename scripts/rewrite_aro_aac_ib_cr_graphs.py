#!/usr/bin/env python3
"""Rewrite AAC(6')-Ib-cr dual drug-class acetyltransferase graphs.

AAC(6')-Ib-cr records use the same acetyl-CoA-dependent AAC antibiotic
acetylation mechanism as the curated plain AAC graphs, but carry both inherited
fluoroquinolone and aminoglycoside drug-class edges.

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

import rewrite_aro_aac_graphs as aac  # noqa: E402
from record_io import append_to_section, replace_block  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ARO_DIR = ROOT / "data" / "traits" / "function" / "resistance" / "aro"

HISTORY_ACTION = "Completed AAC(6')-Ib-cr dual drug-class acetyltransferase graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-09T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

TARGETS: tuple[aac.Target, ...] = (
    aac.Target("ARO:3005113", "aac-6-ib-cr-aro3005113.yaml"),
    aac.Target("ARO:3002547", "aac-6-ib-cr1-aro3002547.yaml"),
    aac.Target("ARO:3005112", "aac-6-ib-cr3-aro3005112.yaml"),
    aac.Target("ARO:3005114", "aac-6-ib-cr4-aro3005114.yaml"),
    aac.Target("ARO:3005115", "aac-6-ib-cr5-aro3005115.yaml"),
    aac.Target("ARO:3005116", "aac-6-ib-cr6-aro3005116.yaml"),
    aac.Target("ARO:3005117", "aac-6-ib-cr7-aro3005117.yaml"),
    aac.Target("ARO:3005118", "aac-6-ib-cr8-aro3005118.yaml"),
    aac.Target("ARO:3005119", "aac-6-ib-cr9-aro3005119.yaml"),
    aac.Target("ARO:3007770", "aac-6-ib-cr10-aro3007770.yaml"),
    aac.Target("ARO:3007771", "aac-6-ib-cr11-aro3007771.yaml"),
)
TARGET_BY_ID = {target.identifier: target for target in TARGETS}

ACETYLATED_STATE_EDGE_KEYS = {
    ("transfer", "RO:0002411", "acetylated"),
    ("acetylated", "RO:0002411", "resistance"),
}


def _dump(obj: Any) -> str:
    return yaml.safe_dump(
        obj,
        sort_keys=False,
        allow_unicode=True,
        width=100,
        default_flow_style=False,
    )


def target_for_record(record: dict[str, Any], path: Path) -> aac.Target:
    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not an AAC(6')-Ib-cr target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")
    return target


def _edge_key(edge: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(edge.get("subject", "")),
        str(edge.get("predicate_id", "")),
        str(edge.get("object", "")),
    )


def _append_unique_evidence(
    evidence: list[dict[str, Any]],
    seen: set[tuple[str, str]],
    edge: dict[str, Any],
) -> None:
    for item in aac._dicts(edge.get("evidence")):
        reference = str(item.get("reference", ""))
        snippet = str(item.get("snippet", ""))
        key = (reference, snippet)
        if key in seen:
            continue
        seen.add(key)
        evidence.append(copy.deepcopy(item))


def _transfer_resistance_edge(evidence: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "subject": "transfer",
        "predicate": "causally upstream of (inactivates the drug)",
        "predicate_id": "RO:0002411",
        "object": "resistance",
        "description": (
            "AAC activity transfers an acetyl group to the antibiotic, "
            "inactivating the drug substrate and causing resistance."
        ),
        "evidence": evidence,
    }


def _collapse_acetylated_state(graph: dict[str, Any]) -> dict[str, Any]:
    """Remove the broad local inactive-drug state from the shared AAC graph."""

    out = copy.deepcopy(graph)
    out["nodes"] = [
        node
        for node in aac._dicts(out.get("nodes"))
        if node.get("node_id") != "acetylated"
    ]

    collapsed_evidence: list[dict[str, Any]] = []
    seen_evidence: set[tuple[str, str]] = set()
    insert_at = 0
    edges: list[dict[str, Any]] = []

    for edge in aac._dicts(out.get("edges")):
        if _edge_key(edge) in ACETYLATED_STATE_EDGE_KEYS:
            if edge.get("subject") == "transfer":
                insert_at = len(edges)
            _append_unique_evidence(collapsed_evidence, seen_evidence, edge)
            continue
        edges.append(edge)

    if not collapsed_evidence:
        raise ValueError("AAC graph is missing the acetylated-state edge chain")

    edges.insert(insert_at, _transfer_resistance_edge(collapsed_evidence))
    out["edges"] = edges
    return out


def enrich_record(record: dict[str, Any], target: aac.Target) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != target.identifier:
        raise ValueError(
            f"{target.filename}: expected {target.identifier}, "
            f"found {record.get('identifier')}"
        )
    if not record.get("label"):
        raise ValueError(f"{target.identifier}: missing label")
    if not record.get("definition"):
        raise ValueError(f"{target.identifier}: missing definition")

    graphs = aac._dicts(record.get("causal_graphs"))
    if len(graphs) != 1 or graphs[0].get("graph_id") != "resistance":
        raise ValueError(f"{target.identifier}: expected exactly one resistance graph")

    out = copy.deepcopy(record)
    graph = aac._graph(record, graphs[0])
    out["causal_graphs"] = [_collapse_acetylated_state(graph)]
    return out, out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    target = target_for_record(record, path)
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
        help="ARO directory or one of the 11 AAC(6')-Ib-cr YAML files",
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
