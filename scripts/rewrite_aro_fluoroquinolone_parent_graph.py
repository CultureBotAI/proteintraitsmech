#!/usr/bin/env python3
"""Curate the broad fluoroquinolone-resistant topoisomerase parent graph.

The GyrA, GyrB, ParC and ParE children have subunit-specific QRDR graphs.  The
ARO:3000452 parent is broader: it says fluoroquinolones inhibit bacterial
type-II and type-IV topoisomerases and that QRDR point mutations can give rise
to resistance. This updater keeps the parent at that generic level instead of
asserting a single subunit-specific QRDR route.

Dry-run by default; pass ``--apply`` to write.
"""

from __future__ import annotations

import argparse
import copy
import re
import sys
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from record_io import append_to_section, replace_block  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ARO_DIR = ROOT / "data" / "traits" / "function" / "resistance" / "aro"

IDENTIFIER = "ARO:3000452"
FILENAME = "fluoroquinolone-resistant-dna-topoisomerase-aro3000452.yaml"
HISTORY_ACTION = "Curated generic fluoroquinolone topoisomerase graph"
HISTORY_EVENT = {
    "timestamp": "2026-09-11T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

TARGET_EVIDENCE = {
    "reference": IDENTIFIER,
    "snippet": (
        "Fluoroquinolones inhibit type II and type IV topoisomerases (2 "
        "strand breaking enzymes) such as GyrA/GyrB and ParC/ParE. Point "
        "mutations in the associated gyrA and parC genes, in particular in "
        "the 'quinolone resistance determining region' (QRDR), give rise to "
        "resistance to the class."
    ),
    "notes": (
        "CARD definition for the broad fluoroquinolone-resistant DNA "
        "topoisomerase parent."
    ),
}

MUTATION_EVIDENCE = {
    "reference": "ARO:3000212",
    "snippet": (
        "Point mutations in the DNA may lead to an altered gene product that "
        "may result in antibiotic resistance."
    ),
    "notes": "CARD definition for mutation conferring antibiotic resistance.",
}

FLUOROQUINOLONE_EVIDENCE = {
    "reference": "ARO:0000001",
    "snippet": "fluoroquinolone antibiotic",
    "notes": "ARO drug-class term named by the fluoroquinolone topoisomerase parent.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "mutation conferring antibiotic resistance",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3000212",
}

DRUG_NODE = {
    "node_id": "drug0",
    "label": "fluoroquinolone antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:0000001",
}

INHIBITION_NODE = {
    "node_id": "inhibition",
    "label": "fluoroquinolone inhibition of bacterial DNA gyrase and topoisomerase IV",
    "node_type": "STATE",
    "description": (
        "Local state for fluoroquinolone inhibition of bacterial type-II and "
        "type-IV topoisomerases; the parent is broader than a single GyrA, "
        "GyrB, ParC or ParE QRDR route."
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

INITIAL_EDGE_KEYS = {
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
}

EXPECTED_EDGE_KEYS = INITIAL_EDGE_KEYS | {
    ("drug0", "RO:0002411", "inhibition"),
    ("determinant", "RO:0002212", "inhibition"),
}

_MAPPING_STATUS = re.compile(r"^mapping_status:[ \t]*\S+[ \t]*$", re.M)


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


def _unique_evidence(evidence: tuple[dict[str, str], ...]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
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
        out.append(copy.deepcopy(item))
    return out


def _edge(
    subject: str,
    predicate: str,
    predicate_id: str,
    object_: str,
    description: str,
    evidence: tuple[dict[str, str], ...],
) -> dict[str, Any]:
    return {
        "subject": subject,
        "predicate": predicate,
        "predicate_id": predicate_id,
        "object": object_,
        "description": description,
        "evidence": _unique_evidence(evidence),
    }


def _validate_graph(graph: dict[str, Any]) -> None:
    nodes = _nodes_by_id(graph)
    missing_nodes = sorted({"determinant", "mech0", "resistance"} - set(nodes))
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{IDENTIFIER}: missing node(s): {missing}")

    seen: set[tuple[str, str, str]] = set()
    found_edges: set[tuple[str, str, str]] = set()
    for edge in _dicts(graph.get("edges")):
        key = _edge_key(edge)
        if key not in EXPECTED_EDGE_KEYS:
            raise ValueError(f"{IDENTIFIER}: unexpected edge {key[0]} -> {key[2]}")
        if key in seen:
            raise ValueError(f"{IDENTIFIER}: duplicate edge {key[0]} -> {key[2]}")
        seen.add(key)
        found_edges.add(key)

    if found_edges == EXPECTED_EDGE_KEYS:
        return

    missing_initial = INITIAL_EDGE_KEYS - found_edges
    unexpected_canonical = found_edges - INITIAL_EDGE_KEYS
    if missing_initial:
        missing = ", ".join(
            f"{subject} -> {object_}"
            for subject, _, object_ in sorted(missing_initial)
        )
        raise ValueError(f"{IDENTIFIER}: missing initial edge(s): {missing}")
    if unexpected_canonical:
        extra = ", ".join(
            f"{subject} -> {object_}"
            for subject, _, object_ in sorted(unexpected_canonical)
        )
        raise ValueError(f"{IDENTIFIER}: partial canonical edge(s): {extra}")


def _canonical_nodes(graph: dict[str, Any]) -> list[dict[str, Any]]:
    nodes = _nodes_by_id(graph)
    return [
        copy.deepcopy(nodes["determinant"]),
        copy.deepcopy(MECHANISM_NODE),
        copy.deepcopy(DRUG_NODE),
        copy.deepcopy(INHIBITION_NODE),
        copy.deepcopy(RESISTANCE_NODE),
    ]


def _canonical_edges(record: dict[str, Any]) -> list[dict[str, Any]]:
    source_evidence = _source_evidence(record)
    resistance_evidence = (TARGET_EVIDENCE, MUTATION_EVIDENCE, *source_evidence)
    inhibition_evidence = (TARGET_EVIDENCE, FLUOROQUINOLONE_EVIDENCE, *source_evidence)
    return [
        _edge(
            "determinant",
            "participates in (resistance mechanism)",
            "RO:0000056",
            "mech0",
            "CARD classifies resistant topoisomerase mutations as mutation-based resistance.",
            resistance_evidence,
        ),
        _edge(
            "mech0",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            (
                "QRDR point mutations in bacterial DNA gyrase or topoisomerase "
                "IV subunits are upstream of fluoroquinolone resistance."
            ),
            resistance_evidence,
        ),
        _edge(
            "determinant",
            "causally upstream of (confers resistance)",
            "RO:0002411",
            "resistance",
            (
                "The mutated topoisomerase determinant counters "
                "fluoroquinolone inhibition and gives rise to resistance."
            ),
            resistance_evidence,
        ),
        _edge(
            "drug0",
            "causally upstream of (inhibits target topoisomerases)",
            "RO:0002411",
            "inhibition",
            (
                "Fluoroquinolones inhibit bacterial type-II and type-IV DNA "
                "topoisomerases."
            ),
            inhibition_evidence,
        ),
        _edge(
            "determinant",
            "negatively regulates (reduces fluoroquinolone inhibition)",
            "RO:0002212",
            "inhibition",
            (
                "Resistance-conferring QRDR point mutations reduce "
                "fluoroquinolone inhibition of the target topoisomerases."
            ),
            inhibition_evidence,
        ),
    ]


def enrich_record(record: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != IDENTIFIER:
        raise ValueError(f"expected {IDENTIFIER}, found {record.get('identifier')}")

    out = copy.deepcopy(record)
    before = copy.deepcopy(out.get("causal_graphs"))
    graphs = _dicts(out.get("causal_graphs"))
    if len(graphs) != 1:
        raise ValueError(f"{IDENTIFIER}: expected exactly one causal graph")
    graph = graphs[0]
    _validate_graph(graph)

    graph["graph_id"] = "resistance"
    graph["title"] = (
        "fluoroquinolone-resistant DNA topoisomerase → reduced drug inhibition → resistance"
    )
    graph["description"] = (
        "Curated generic graph for the broad fluoroquinolone-resistant DNA "
        "topoisomerase parent. The graph records mutation-based resistance and "
        "the drug-inhibition state that covers both DNA gyrase and "
        "topoisomerase IV instead of a single subunit-specific QRDR route."
    )
    graph["nodes"] = _canonical_nodes(graph)
    graph["edges"] = _canonical_edges(out)
    out["causal_graphs"] = [graph]
    out["mapping_status"] = "REVIEWED"
    if not any(
        isinstance(item, dict) and item.get("action") == HISTORY_ACTION
        for item in out.get("curation_history") or []
    ):
        out.setdefault("curation_history", []).append(copy.deepcopy(HISTORY_EVENT))
    return out, out.get("causal_graphs") != before or record.get("mapping_status") != "REVIEWED"


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: not a YAML mapping")
    out, changed = enrich_record(record)
    graph_block = _dump({"causal_graphs": out["causal_graphs"]})
    result = replace_block(text, "causal_graphs", graph_block)
    result = _MAPPING_STATUS.sub("mapping_status: REVIEWED", result, count=1)
    if HISTORY_ACTION not in result:
        history_block = _dump({"curation_history": [HISTORY_EVENT]})
        result = append_to_section(result, "curation_history", history_block)
    return result, changed or result != text


def iter_paths(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    return [path / FILENAME]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, nargs="?", default=ARO_DIR)
    parser.add_argument("--apply", action="store_true", help="write changes")
    args = parser.parse_args(argv)

    changed = 0
    already = 0
    for path in iter_paths(args.path):
        text = path.read_text(encoding="utf-8")
        out, did_change = enrich_text(text, path)
        if did_change:
            if args.apply:
                path.write_text(out, encoding="utf-8")
                print(f"  wrote {path.name}")
            else:
                print(f"  would write {path.name}")
            changed += 1
        else:
            already += 1

    verb = "changed" if args.apply else "would change"
    print(f"{verb}: {changed}")
    print(f"already enriched: {already}")
    if not args.apply:
        print("dry run -- pass --apply to write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
