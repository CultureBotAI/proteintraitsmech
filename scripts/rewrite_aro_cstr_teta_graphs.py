#!/usr/bin/env python3
"""Remove stale secondary-transporter evidence from C. striatum tetA.

CARD defines the Corynebacterium striatum tetAB genes as encoding an ABC
transporter. The existing tetA graph came from a generic secondary-transporter
efflux seed and therefore asserted domain/fold nodes that the record's
definition does not support. This updater reduces the graph to the
CARD-supported efflux core and adds target-specific evidence and descriptions
on every edge.

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

HISTORY_ACTION = "Removed stale domain/fold evidence from the Corynebacterium striatum tetA graph"
LEGACY_HISTORY_ACTIONS = {
    "Removed stale MFS evidence from the Corynebacterium striatum tetA graph",
}
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

TARGET_IDENTIFIER = "ARO:3004639"
TARGET_FILENAME = "corynebacterium-striatum-teta-aro3004639.yaml"

CSTR_TETA_DEFINITION = (
    "The tetAB genes of the Corynebacterium striatum R-plasmid encode an ABC "
    "transporter and confer tetracycline, oxytetracycline, and oxalic resistance."
)

CSTR_TETA_EVIDENCE = {
    "reference": TARGET_IDENTIFIER,
    "snippet": CSTR_TETA_DEFINITION,
    "notes": "CARD definition for Corynebacterium striatum tetA.",
}

ABC_EFFLUX_EVIDENCE = {
    "reference": "ARO:0010001",
    "snippet": (
        "Directed pumping of antibiotic out of a cell to confer resistance. "
        "ATP-binding cassette (ABC) transporters are present in all cells of all "
        "organisms and use the energy of ATP binding/hydrolysis to transport "
        "substrates across cell membranes."
    ),
    "notes": "CARD definition for ABC antibiotic efflux pumps.",
}

EFFLUX_PUMP_EVIDENCE = {
    "reference": "ARO:3000159",
    "snippet": "Efflux proteins that pump antibiotic out of a cell to confer resistance.",
    "notes": "CARD definition for efflux pump complexes and subunits.",
}

ANTIBIOTIC_EFFLUX_EVIDENCE = {
    "reference": "ARO:0010000",
    "snippet": "Antibiotic resistance via the transport of antibiotics out of the cell.",
    "notes": "CARD definition for the antibiotic-efflux resistance mechanism.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "antibiotic efflux",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:0010000",
}

RESISTANCE_NODE = {
    "node_id": "resistance",
    "label": "antibiotic resistance phenotype",
    "node_type": "PHENOTYPE",
    "grounding": "GO:0046677",
    "description": (
        "Resistance phenotype conferred by this determinant. Grounded to the "
        "nearest available superclass: ARO models determinants and mechanisms but "
        "has no term for the resistance phenotype itself."
    ),
}

EXPECTED_EDGE_KEYS = {
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
}

INPUT_EDGE_KEYS = EXPECTED_EDGE_KEYS | {
    ("domain", "BFO:0000050", "determinant"),
    ("determinant", "RO:0002350", "fold"),
    ("domain", "RO:0002327", "mech0"),
}

EDGE_DESCRIPTIONS = {
    ("determinant", "RO:0000056", "mech0"): (
        "ARO classifies Corynebacterium striatum tetA under the antibiotic-efflux "
        "resistance mechanism."
    ),
    ("mech0", "RO:0002411", "resistance"): (
        "TetAB-associated antibiotic efflux lowers intracellular antibiotic exposure."
    ),
    ("determinant", "RO:0002411", "resistance"): (
        "The Corynebacterium striatum R-plasmid tetAB genes encode an ABC efflux "
        "transporter that confers resistance."
    ),
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str


TARGETS = {
    TARGET_IDENTIFIER: Target(
        identifier=TARGET_IDENTIFIER,
        filename=TARGET_FILENAME,
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


def _without_legacy_history(record: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        copy.deepcopy(item)
        for item in _dicts(record.get("curation_history"))
        if item.get("action") not in LEGACY_HISTORY_ACTIONS
    ]


def _unique_evidence(evidence: tuple[dict[str, str], ...]) -> list[dict[str, str]]:
    unique: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for item in evidence:
        key = (item["reference"], " ".join(item.get("snippet", "").split()))
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
    missing_nodes = sorted({"determinant", "mech0", "resistance"} - set(nodes))
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")

    seen: set[tuple[str, str, str]] = set()
    for edge in _dicts(graph.get("edges")):
        key = _edge_key(edge)
        if key not in INPUT_EDGE_KEYS:
            raise ValueError(f"{target.identifier}: unexpected edge {key[0]} -> {key[2]}")
        if key in seen:
            raise ValueError(f"{target.identifier}: duplicate edge {key[0]} -> {key[2]}")
        seen.add(key)

    missing_edges = EXPECTED_EDGE_KEYS - seen
    if missing_edges:
        missing = ", ".join(
            f"{subject} -> {object_}"
            for subject, _, object_ in sorted(missing_edges)
        )
        raise ValueError(f"{target.identifier}: missing edge(s): {missing}")


def _canonical_graph(record: dict[str, Any], target: Target) -> dict[str, Any]:
    graph = record["causal_graphs"][0]
    _validate_graph(graph, target)
    nodes = _nodes_by_id(graph)
    source_evidence = _source_evidence(record)
    efflux_evidence = (
        CSTR_TETA_EVIDENCE,
        ABC_EFFLUX_EVIDENCE,
        EFFLUX_PUMP_EVIDENCE,
        ANTIBIOTIC_EFFLUX_EVIDENCE,
        *source_evidence,
    )

    return {
        "graph_id": "resistance",
        "title": "Corynebacterium striatum tetA → ABC efflux → tetracycline resistance",
        "description": (
            "Curated resistance graph for Corynebacterium striatum tetA. The "
            "prior generic domain/fold seed was removed because the CARD "
            "definition describes the tetAB genes as encoding an ABC transporter "
            "but does not ground a specific tetA subunit domain."
        ),
        "nodes": [
            copy.deepcopy(nodes["determinant"]),
            copy.deepcopy(MECHANISM_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                efflux_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                efflux_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                efflux_evidence,
            ),
        ],
    }


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != target.identifier:
        raise ValueError(f"expected {target.identifier}, found {record.get('identifier')}")

    out = copy.deepcopy(record)
    before = copy.deepcopy(out.get("causal_graphs"))
    graphs = out.get("causal_graphs") or []
    graph_index = next(
        (index for index, item in enumerate(graphs) if item.get("graph_id") == "resistance"),
        None,
    )
    if graph_index is None:
        raise ValueError(f"{target.identifier}: missing resistance causal graph")

    graphs[graph_index] = _canonical_graph(out, target)
    return out, out.get("causal_graphs") != before


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: record is not a mapping")
    identifier = record.get("identifier")
    target = TARGETS.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not a Corynebacterium striatum tetA target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
    normalize_aliases = "&id" in text or "*id" in text
    history = _without_legacy_history(record)
    removed_legacy_history = len(history) != len(_dicts(record.get("curation_history")))
    if not changed and not normalize_aliases and not removed_legacy_history:
        return text, False

    out = replace_block(
        text,
        "causal_graphs",
        _dump({"causal_graphs": enriched["causal_graphs"]}),
    )
    if removed_legacy_history:
        if not any(item.get("action") == HISTORY_ACTION for item in history):
            history.append(copy.deepcopy(HISTORY_EVENT))
        out = replace_block(
            out,
            "curation_history",
            _dump({"curation_history": history}),
        )
    elif HISTORY_ACTION not in out:
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
        help="ARO directory or exact Corynebacterium striatum tetA YAML",
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
