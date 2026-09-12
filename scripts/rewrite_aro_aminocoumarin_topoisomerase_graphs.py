#!/usr/bin/env python3
"""Add descriptions and DOI evidence to aminocoumarin topoisomerase graphs.

These ARO records were already reviewed with the correct aminocoumarin
topoisomerase-loss-of-binding topology. They remained below a perfect quality
score because most edges had only one reference and four edges had no
description. This updater leaves the topology intact, adds exact edge
descriptions, and attaches the record-level ARO DOI citations to each edge.

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

HISTORY_ACTION = "Added aminocoumarin topoisomerase edge descriptions and DOI evidence"
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
    ("determinant", "RO:0000086", "binding_loss"),
    ("drug0", "RO:0002212", "dna_synth"),
    ("binding_loss", "RO:0002411", "dna_synth"),
)
EDGE_KEYS = set(EDGE_ORDER)

EDGE_DESCRIPTIONS = {
    ("determinant", "RO:0000056", "mech0"): (
        "ARO classifies aminocoumarin-resistant topoisomerase subunits as mutation-based "
        "resistance determinants."
    ),
    ("mech0", "RO:0002411", "resistance"): (
        "The topoisomerase mutation mechanism is upstream of aminocoumarin resistance."
    ),
    ("determinant", "RO:0002411", "resistance"): (
        "The mutated determinant prevents aminocoumarin binding and thereby confers "
        "resistance."
    ),
    ("determinant", "ARO:2000001", "drug0"): (
        "ARO maps this determinant or its direct aminocoumarin-resistant parent to the "
        "aminocoumarin antibiotic drug class."
    ),
    ("determinant", "RO:0000086", "binding_loss"): (
        "The resistant topoisomerase subunit has the modeled quality of preventing "
        "antibiotic binding."
    ),
    ("drug0", "RO:0002212", "dna_synth"): (
        "Aminocoumarin binding to bacterial topoisomerases inhibits DNA synthesis."
    ),
    ("binding_loss", "RO:0002411", "dna_synth"): (
        "Loss of aminocoumarin binding lets the topoisomerase continue supporting DNA "
        "synthesis."
    ),
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str


TARGETS = (
    Target("ARO:3000479", "aminocoumarin-resistant-gyrb-aro3000479.yaml"),
    Target("ARO:3000457", "aminocoumarin-resistant-pare-aro3000457.yaml"),
    Target("ARO:3000480", "aminocoumarin-resistant-pary-aro3000480.yaml"),
    Target(
        "ARO:3003302",
        "bartonella-bacilliformis-gyrb-conferring-resistance-to-aminocoumarin-"
        "aro3003302.yaml",
    ),
    Target(
        "ARO:3003303",
        "escherichia-coli-gyrb-conferring-resistance-to-aminocoumarin-aro3003303.yaml",
    ),
    Target(
        "ARO:3003301",
        "staphylococcus-aureus-gyrb-conferring-resistance-to-aminocoumarin-aro3003301.yaml",
    ),
    Target(
        "ARO:3003314",
        "staphylococcus-aureus-pare-conferring-resistance-to-aminocoumarin-aro3003314.yaml",
    ),
    Target(
        "ARO:3003318",
        "streptomyces-rishiriensis-pary-mutant-conferring-resistance-to-aminocoumarin-"
        "aro3003318.yaml",
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


def _source_evidence(record: dict[str, Any]) -> tuple[dict[str, str], ...]:
    return tuple(
        {
            "reference": str(item["reference"]),
            "notes": str(item.get("notes") or "ARO citation for this record."),
        }
        for item in _dicts(record.get("evidence"))
        if item.get("reference")
    )


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


def _validate_graph(record: dict[str, Any], graph: dict[str, Any], target: Target) -> None:
    if graph.get("graph_id") != "resistance":
        raise ValueError(f"{target.identifier}: expected the reviewed resistance graph")

    found: set[tuple[str, str, str]] = set()
    for edge in _dicts(graph.get("edges")):
        key = _edge_key(edge)
        if key not in EDGE_KEYS:
            raise ValueError(f"{target.identifier}: unexpected edge {key[0]} -> {key[2]}")
        if key in found:
            raise ValueError(f"{target.identifier}: duplicate edge {key[0]} -> {key[2]}")
        found.add(key)

    missing = EDGE_KEYS - found
    if missing:
        missing_text = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in sorted(missing))
        raise ValueError(f"{target.identifier}: missing edge(s): {missing_text}")

    source_evidence = _source_evidence(record)
    if not source_evidence:
        raise ValueError(f"{target.identifier}: missing record-level DOI evidence")


def _rewrite_edge(edge: dict[str, Any], source_evidence: tuple[dict[str, str], ...]) -> dict[str, Any]:
    key = _edge_key(edge)
    return {
        "subject": edge["subject"],
        "predicate": edge["predicate"],
        "predicate_id": edge["predicate_id"],
        "object": edge["object"],
        "description": EDGE_DESCRIPTIONS[key],
        "evidence": _unique_evidence(*_dicts(edge.get("evidence")), *source_evidence),
    }


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != target.identifier:
        raise ValueError(f"expected {target.identifier}, found {record.get('identifier')}")

    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1:
        raise ValueError(f"{target.identifier}: expected exactly one resistance graph")

    graph = graphs[0]
    _validate_graph(record, graph, target)

    source_evidence = _source_evidence(record)
    edges_by_key = {_edge_key(edge): edge for edge in _dicts(graph.get("edges"))}
    rewritten = copy.deepcopy(record)
    rewritten_graph = copy.deepcopy(graph)
    rewritten_graph["edges"] = [
        _rewrite_edge(edges_by_key[key], source_evidence) for key in EDGE_ORDER
    ]
    rewritten["causal_graphs"] = [rewritten_graph]
    return rewritten, rewritten != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: record is not a mapping")

    target = TARGET_BY_FILENAME.get(path.name)
    if target is None:
        raise ValueError(f"{path}: not an aminocoumarin topoisomerase target")

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
        help="ARO directory or one of the aminocoumarin topoisomerase YAML files",
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
