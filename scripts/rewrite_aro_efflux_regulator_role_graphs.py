#!/usr/bin/env python3
"""Make leftover efflux-regulator graphs conservative and fully grounded.

These records were promoted from AcrR or AdeR archetypes even though their local
ARO definitions do not support a single grounded pump-expression path.  This
updater keeps the ARO-supported classification only:

* the determinant participates in antibiotic efflux through the ARO:3000451
  regulatory parent;
* antibiotic efflux is causally upstream of resistance;
* the determinant is causally upstream of the resistance phenotype at this broad
  role level.

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
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": (
        "Removed stale AcrR/AdeR archetype pump-expression paths from "
        "leftover efflux-regulator graphs and kept the grounded ARO:3000451 "
        "antibiotic-efflux role"
    ),
    "llm_assisted": True,
}

EFFLUX_REGULATOR_EVIDENCE = {
    "reference": "ARO:3000451",
    "snippet": (
        "Protein(s) and two component regulatory systems that directly or "
        "indirectly change rates of antibiotic efflux."
    ),
    "notes": (
        "CARD definition for the broad protein(s) and two-component regulatory "
        "system modulating antibiotic efflux parent."
    ),
}

ANTIBIOTIC_EFFLUX_EVIDENCE = {
    "reference": "ARO:0010000",
    "snippet": "Antibiotic resistance via the transport of antibiotics out of the cell.",
    "notes": "CARD definition for the antibiotic efflux resistance mechanism.",
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
        "nearest available superclass: ARO models determinants and mechanisms "
        "but has no term for the resistance phenotype itself."
    ),
}

CANONICAL_EDGES = {
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
}

LEGACY_REPRESSOR_EDGES = {
    ("determinant", "RO:0002327", "repression"),
    ("repression", "RO:0002212", "pump"),
    ("determinant", "RO:0002212", "repression"),
}

LEGACY_ACTIVATOR_EDGES = {
    ("determinant", "RO:0002327", "activation"),
    ("activation", "RO:0002213", "pump"),
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    graph_description: str


TARGETS = {
    "ARO:3000656": Target(
        identifier="ARO:3000656",
        filename="acrs-aro3000656.yaml",
        graph_description=(
            "Conservative role-level graph for AcrS. ARO classifies AcrS under "
            "protein regulators that modulate antibiotic efflux, but the local "
            "definition does not specify one resistance-causing allele or a "
            "single efflux-pump endpoint."
        ),
    ),
    "ARO:3000676": Target(
        identifier="ARO:3000676",
        filename="h-ns-aro3000676.yaml",
        graph_description=(
            "Conservative role-level graph for H-NS. ARO classifies H-NS under "
            "protein regulators that modulate antibiotic efflux, but the local "
            "definition names several RND-type exporter genes rather than a "
            "single resistance-causing pump-expression route."
        ),
    ),
    "ARO:3000815": Target(
        identifier="ARO:3000815",
        filename="mgra-aro3000815.yaml",
        graph_description=(
            "Conservative role-level graph for mgrA. ARO classifies mgrA under "
            "protein regulators that modulate antibiotic efflux, but the local "
            "definition explicitly mixes positive norA regulation with direct "
            "or indirect repression of other pumps."
        ),
    ),
    "ARO:3000818": Target(
        identifier="ARO:3000818",
        filename="nalc-aro3000818.yaml",
        graph_description=(
            "Conservative role-level graph for nalC. ARO classifies nalC under "
            "protein regulators that modulate antibiotic efflux; the local "
            "definition says nalC mutants derepress PA3720-PA3719 and confer "
            "multidrug resistance, but leaves the downstream MexAB-OprM route "
            "indirect."
        ),
    ),
    "ARO:3005069": Target(
        identifier="ARO:3005069",
        filename="rsma-aro3005069.yaml",
        graph_description=(
            "Conservative role-level graph for rsmA. ARO classifies rsmA under "
            "protein regulators that modulate antibiotic efflux, and the local "
            "definition ties rsmA to MexEF-OprN overexpression without stating "
            "a single direct transcriptional-repressor mechanism."
        ),
    ),
    "ARO:3000827": Target(
        identifier="ARO:3000827",
        filename="soxrs-aro3000827.yaml",
        graph_description=(
            "Conservative role-level graph for soxRS. ARO classifies SoxRS "
            "under protein regulators that modulate antibiotic efflux, and the "
            "local definition names it as a positive regulator for many "
            "multidrug efflux pumps rather than one grounded pump endpoint."
        ),
    ),
    "ARO:3003841": Target(
        identifier="ARO:3003841",
        filename="kdpe-aro3003841.yaml",
        graph_description=(
            "Conservative role-level graph for kdpE. ARO inherits an antibiotic "
            "efflux mechanism for this response regulator, but the local "
            "definition describes virulence and potassium-transport regulation "
            "without naming a resistance-causing efflux pump."
        ),
    ),
    "ARO:3004055": Target(
        identifier="ARO:3004055",
        filename="escherichia-coli-cpxr-aro3004055.yaml",
        graph_description=(
            "Conservative role-level graph for Escherichia coli CpxR. ARO "
            "classifies this response regulator under antibiotic efflux and "
            "the definition names marRAB-dependent activation of "
            "TolC-dependent transporters, but it does not identify one exact "
            "efflux pump class to ground here."
        ),
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


def _target_evidence(record: dict[str, Any]) -> dict[str, str]:
    return {
        "reference": str(record["identifier"]),
        "snippet": str(record["definition"]),
        "notes": f"CARD definition for {record['label']}.",
    }


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
            "evidence": [copy.deepcopy(item) for item in evidence],
        }
    )


def _nodes_by_id(graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(node["node_id"]): node
        for node in graph.get("nodes") or []
        if isinstance(node, dict) and "node_id" in node
    }


def _validate_graph(graph: dict[str, Any], target: Target) -> None:
    allowed = CANONICAL_EDGES | LEGACY_REPRESSOR_EDGES | LEGACY_ACTIVATOR_EDGES
    full_edges = set()
    seen: set[tuple[str, str, str]] = set()
    for edge in graph.get("edges") or []:
        full_key = _edge_key(edge)
        if full_key not in allowed:
            raise ValueError(f"{target.identifier}: unexpected edge {full_key[0]} -> {full_key[2]}")
        if full_key in seen:
            raise ValueError(f"{target.identifier}: duplicate edge {full_key[0]} -> {full_key[2]}")
        seen.add(full_key)
        if full_key in CANONICAL_EDGES:
            full_edges.add(full_key)

    missing_edges = sorted(CANONICAL_EDGES - full_edges)
    if missing_edges:
        missing = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in missing_edges)
        raise ValueError(f"{target.identifier}: missing edge(s): {missing}")


def _enrich_nodes(graph: dict[str, Any], target: Target) -> None:
    nodes = _nodes_by_id(graph)
    if "determinant" not in nodes:
        raise ValueError(f"{target.identifier}: missing node(s): determinant")

    graph["nodes"] = [
        copy.deepcopy(nodes["determinant"]),
        copy.deepcopy(MECHANISM_NODE),
        copy.deepcopy(RESISTANCE_NODE),
    ]


def _canonical_edges(record: dict[str, Any]) -> list[dict[str, Any]]:
    target = _target_evidence(record)
    return [
        _edge(
            "determinant",
            "participates in (resistance mechanism)",
            "RO:0000056",
            "mech0",
            "ARO classifies this regulatory determinant under antibiotic efflux.",
            (target, EFFLUX_REGULATOR_EVIDENCE),
        ),
        _edge(
            "mech0",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            "Antibiotic efflux exports antibiotics from the cell to produce resistance.",
            (target, ANTIBIOTIC_EFFLUX_EVIDENCE),
        ),
        _edge(
            "determinant",
            "causally upstream of (confers resistance)",
            "RO:0002411",
            "resistance",
            (
                "The determinant is modeled at ARO's broad antibiotic-efflux "
                "regulatory level rather than as a specific pump-expression route."
            ),
            (target, EFFLUX_REGULATOR_EVIDENCE, ANTIBIOTIC_EFFLUX_EVIDENCE),
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
    _enrich_nodes(graph, target)
    graph["description"] = target.graph_description
    graph["edges"] = _canonical_edges(out)
    return out, out.get("causal_graphs") != before


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: record is not a mapping")
    identifier = record.get("identifier")
    target = TARGETS.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not a leftover efflux-regulator target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
    normalize_aliases = "&id" in text or "*id" in text
    if not changed and not normalize_aliases:
        return text, False

    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    if HISTORY_CURATOR not in out:
        out = append_to_section(out, "curation_history", _dump({"curation_history": [HISTORY_EVENT]}))
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
        help="ARO directory or one of the eight target YAML files",
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
