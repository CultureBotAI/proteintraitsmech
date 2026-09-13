#!/usr/bin/env python3
"""Ground the mutant efflux regulatory protein parent graph.

The broad mutant-efflux-regulator parent supports the generic route
``mutant regulator -> increased efflux-protein expression -> antibiotic
efflux -> resistance``. Its pump-expression quantity is local to the resistance
graph, so this updater represents it as a described STATE and adds CARD-backed
edge descriptions and multi-source evidence across the graph.

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

from record_io import append_to_section, replace_block  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ARO_DIR = ROOT / "data" / "traits" / "function" / "resistance" / "aro"

HISTORY_ACTION = "Grounded mutant efflux regulatory protein parent graph"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

IDENTIFIER = "ARO:3000219"
FILENAME = "mutant-efflux-regulatory-protein-conferring-antibiotic-resistance-aro3000219.yaml"

MUTANT_REGULATOR_EVIDENCE = {
    "reference": IDENTIFIER,
    "snippet": (
        "Efflux regulatory proteins with mutations that result in increased "
        "expression of efflux proteins."
    ),
    "notes": (
        "CARD definition for mutant efflux regulators that increase "
        "efflux-protein expression."
    ),
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

ANTIBIOTIC_EFFLUX_EVIDENCE = {
    "reference": "ARO:0010000",
    "snippet": "Antibiotic resistance via the transport of antibiotics out of the cell.",
    "notes": "CARD definition for the antibiotic-efflux resistance mechanism.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "mutation conferring antibiotic resistance",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3000212",
}

PUMP_EXPRESSION_NODE = {
    "node_id": "pump_expression",
    "label": "increased expression of efflux pump proteins",
    "node_type": "STATE",
    "description": (
        "Local state for increased efflux-protein expression caused by "
        "resistance-conferring mutations in efflux regulatory proteins."
    ),
}

EFFLUX_PROCESS_NODE = {
    "node_id": "efflux_process",
    "label": "antibiotic efflux",
    "node_type": "BIOLOGICAL_PROCESS",
    "grounding": "ARO:0010000",
    "description": "Antibiotic efflux downstream of increased efflux-protein expression.",
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
    ("determinant", "RO:0002213", "pump_expression"),
    ("pump_expression", "RO:0002411", "efflux_process"),
    ("efflux_process", "RO:0002411", "resistance"),
}

EDGE_DESCRIPTIONS = {
    ("determinant", "RO:0000056", "mech0"): (
        "ARO classifies mutant efflux regulatory proteins under mutation "
        "conferring antibiotic resistance."
    ),
    ("mech0", "RO:0002411", "resistance"): (
        "Resistance-conferring efflux-regulator mutations increase efflux-protein "
        "expression."
    ),
    ("determinant", "RO:0002411", "resistance"): (
        "Mutant efflux regulatory proteins increase expression of efflux proteins "
        "to confer antibiotic resistance."
    ),
    ("determinant", "RO:0002213", "pump_expression"): (
        "CARD states that this parent covers mutations that increase expression "
        "of efflux proteins."
    ),
    ("pump_expression", "RO:0002411", "efflux_process"): (
        "Increased efflux-protein expression increases antibiotic efflux."
    ),
    ("efflux_process", "RO:0002411", "resistance"): (
        "Antibiotic efflux removes antibiotics from the cell and is causally "
        "upstream of resistance."
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


def _validate_graph(graph: dict[str, Any]) -> None:
    nodes = _nodes_by_id(graph)
    missing_nodes = sorted(
        {"determinant", "mech0", "pump_expression", "efflux_process", "resistance"}
        - set(nodes)
    )
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{IDENTIFIER}: missing node(s): {missing}")

    seen: set[tuple[str, str, str]] = set()
    for edge in _dicts(graph.get("edges")):
        key = _edge_key(edge)
        if key not in EXPECTED_EDGE_KEYS:
            raise ValueError(f"{IDENTIFIER}: unexpected edge {key[0]} -> {key[2]}")
        if key in seen:
            raise ValueError(f"{IDENTIFIER}: duplicate edge {key[0]} -> {key[2]}")
        seen.add(key)

    missing_edges = EXPECTED_EDGE_KEYS - seen
    if missing_edges:
        missing = ", ".join(
            f"{subject} -> {object_}"
            for subject, _, object_ in sorted(missing_edges)
        )
        raise ValueError(f"{IDENTIFIER}: missing edge(s): {missing}")


def _canonical_graph(record: dict[str, Any]) -> dict[str, Any]:
    graph = record["causal_graphs"][0]
    _validate_graph(graph)
    nodes = _nodes_by_id(graph)
    mutation_evidence = (MUTANT_REGULATOR_EVIDENCE, MUTATION_EVIDENCE)
    efflux_evidence = (MUTANT_REGULATOR_EVIDENCE, ANTIBIOTIC_EFFLUX_EVIDENCE)
    all_evidence = (
        MUTANT_REGULATOR_EVIDENCE,
        MUTATION_EVIDENCE,
        ANTIBIOTIC_EFFLUX_EVIDENCE,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → increased efflux protein expression → resistance",
        "description": (
            "Curated graph for the broad mutant efflux regulatory protein parent. "
            "The graph preserves CARD's mutation-conferring-resistance mechanism, "
            "models increased expression of efflux proteins as a described local "
            "state, and links that state through antibiotic efflux to resistance."
        ),
        "nodes": [
            copy.deepcopy(nodes["determinant"]),
            copy.deepcopy(MECHANISM_NODE),
            copy.deepcopy(PUMP_EXPRESSION_NODE),
            copy.deepcopy(EFFLUX_PROCESS_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                mutation_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                all_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                all_evidence,
            ),
            _edge(
                "determinant",
                "positively regulates",
                "RO:0002213",
                "pump_expression",
                mutation_evidence,
            ),
            _edge(
                "pump_expression",
                "causally upstream of (more pump, more efflux)",
                "RO:0002411",
                "efflux_process",
                efflux_evidence,
            ),
            _edge(
                "efflux_process",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                efflux_evidence,
            ),
        ],
    }


def enrich_record(record: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != IDENTIFIER:
        raise ValueError(f"expected {IDENTIFIER}, found {record.get('identifier')}")

    out = copy.deepcopy(record)
    before = copy.deepcopy(out.get("causal_graphs"))
    graphs = out.get("causal_graphs") or []
    graph_index = next(
        (index for index, item in enumerate(graphs) if item.get("graph_id") == "resistance"),
        None,
    )
    if graph_index is None:
        raise ValueError(f"{IDENTIFIER}: missing resistance causal graph")

    graphs[graph_index] = _canonical_graph(out)
    return out, out.get("causal_graphs") != before


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: record is not a mapping")
    if record.get("identifier") != IDENTIFIER:
        raise ValueError(f"{path}: not a mutant efflux regulator parent target")
    if path.name != FILENAME:
        raise ValueError(f"{path}: target {IDENTIFIER} must be in {FILENAME}")

    enriched, changed = enrich_record(record)
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
    return [path / FILENAME]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    parser.add_argument(
        "--path",
        type=Path,
        default=ARO_DIR,
        help="ARO directory or exact mutant efflux regulator parent YAML",
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
