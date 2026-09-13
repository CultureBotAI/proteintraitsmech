#!/usr/bin/env python3
"""Prune the Pseudomonas gyrA/parC fluoroquinolone graph to a conservative core.

ARO:3003702 requires both a parC mutation and a gyrA mutation. The historical
topoisomerase graph imported a single-subunit binding-loss model that the
promoter explicitly excludes for this record. This updater keeps CARD's
mutation and drug-class assertions but removes the unsupported binding-loss
side path.

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
FILENAME = "pseudomonas-aeruginosa-gyra-and-parc-conferring-resistance-to-fluoroquinolones-aro3003702.yaml"
IDENTIFIER = "ARO:3003702"

HISTORY_ACTION = "Pruned Pseudomonas gyrA/parC graph to conservative mutation core"
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

CORE_EDGE_ORDER = (
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("determinant", "ARO:2000001", "drug0"),
)
EXPECTED_EDGE_KEYS = CORE_EDGE_ORDER + (
    ("determinant", "RO:0000086", "binding_loss"),
    ("drug0", "RO:0002212", "dna_synth"),
    ("binding_loss", "RO:0002411", "dna_synth"),
)

TARGET_EVIDENCE = {
    "reference": IDENTIFIER,
    "snippet": (
        "Point mutation in Pseudomonas aeruginosa parC resulting in "
        "fluoroquinolone resistance also requiring a gyrA mutation."
    ),
    "notes": "CARD definition for the Pseudomonas gyrA/parC fluoroquinolone-resistance record.",
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

DRUG_CLASS_EVIDENCE = {
    "reference": "ARO:0000001",
    "snippet": "fluoroquinolone antibiotic",
    "notes": "ARO drug-class term for the grounded fluoroquinolone antibiotic node.",
}

EDGE_DESCRIPTIONS = {
    ("determinant", "RO:0000056", "mech0"): (
        "ARO classifies the Pseudomonas gyrA/parC determinant under mutation-conferring "
        "antibiotic resistance."
    ),
    ("mech0", "RO:0002411", "resistance"): (
        "The inherited mutation mechanism is upstream of fluoroquinolone resistance."
    ),
    ("determinant", "RO:0002411", "resistance"): (
        "The local ARO definition states that this Pseudomonas parC mutation, together "
        "with a gyrA mutation, results in fluoroquinolone resistance."
    ),
    ("determinant", "ARO:2000001", "drug0"): (
        "ARO maps this determinant through its ParC parent to the fluoroquinolone "
        "antibiotic drug class."
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


def _validate_graph(graph: dict[str, Any]) -> None:
    found: set[tuple[str, str, str]] = set()
    for edge in _dicts(graph.get("edges")):
        found.add(_edge_key(edge))

    expected = set(EXPECTED_EDGE_KEYS)
    core = set(CORE_EDGE_ORDER)
    if found != expected and found != core:
        missing = expected - found
        unexpected = found - expected
        raise ValueError(f"unexpected Pseudomonas gyrA/parC edge set: {missing=} {unexpected=}")


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
    route_evidence = (TARGET_EVIDENCE, MUTATION_EVIDENCE, *source_evidence)
    drug_evidence = (
        *_drug_relation_evidence(graph),
        TARGET_EVIDENCE,
        DRUG_CLASS_EVIDENCE,
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
    }
    return [by_key[key] for key in CORE_EDGE_ORDER]


def enrich_record(record: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != IDENTIFIER:
        raise ValueError(f"expected {IDENTIFIER}, found {record.get('identifier')}")

    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1:
        raise ValueError(f"{IDENTIFIER}: expected exactly one resistance graph")

    graph = graphs[0]
    _validate_graph(graph)
    nodes = _nodes_by_id(graph)

    out = copy.deepcopy(record)
    out["causal_graphs"] = [
        {
            "graph_id": "resistance",
            "title": (
                "Pseudomonas aeruginosa gyrA/parC mutations → conservative "
                "fluoroquinolone resistance core"
            ),
            "description": (
                "Conservative graph for the Pseudomonas aeruginosa parC mutation "
                "that also requires a gyrA mutation. The previous graph used a "
                "single-subunit target-binding model; this replacement keeps only "
                "the mutation mechanism and fluoroquinolone drug-class assertion "
                "that CARD states for this two-gene determinant."
            ),
            "nodes": [
                copy.deepcopy(nodes["determinant"]),
                copy.deepcopy(nodes["mech0"]),
                copy.deepcopy(nodes["drug0"]),
                copy.deepcopy(RESISTANCE_NODE),
            ],
            "edges": _canonical_edges(record, graph),
        }
    ]
    return out, out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    if path.name != FILENAME:
        raise ValueError(f"{path}: not {FILENAME}")

    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: record is not a mapping")

    enriched, changed = enrich_record(record)
    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    if HISTORY_ACTION not in out:
        out = append_to_section(out, "curation_history", _dump({"curation_history": [HISTORY_EVENT]}))
        changed = True

    if "&id" in out or "*id" in out:
        raise ValueError(f"{path}: YAML anchors leaked into output")
    return out, changed or out != text


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    parser.add_argument(
        "--path",
        type=Path,
        default=ARO_DIR / FILENAME,
        help="Pseudomonas gyrA/parC YAML file",
    )
    args = parser.parse_args()

    before = args.path.read_text(encoding="utf-8")
    after, changed = enrich_text(before, args.path)

    if changed:
        print(f"  {'wrote' if args.apply else 'would write'} {args.path.name}")
        if args.apply:
            args.path.write_text(after, encoding="utf-8")
    print(f"{'changed' if args.apply else 'would change'}: {int(changed)}")
    print(f"already enriched: {int(not changed)}")
    if not args.apply:
        print("dry run -- pass --apply to write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
