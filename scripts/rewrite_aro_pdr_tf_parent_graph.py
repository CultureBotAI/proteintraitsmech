#!/usr/bin/env python3
"""Curate the generic fungal PDR transcription-factor efflux graph.

The broad PDR parent says fungal PDR transcription factors regulate genes that
encode efflux pumps. CARD does not name a specific pump or the direction of
regulation at this parent, so this updater keeps the local transporter-gene
node and the neutral RO:0002211 regulation predicate used by the PDR1 child.

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

IDENTIFIER = "ARO:3007552"
FILENAME = "pleiotropic-drug-resistance-transcription-factors-aro3007552.yaml"
HISTORY_ACTION = "Curated generic PDR transcription-factor efflux graph"
HISTORY_EVENT = {
    "timestamp": "2026-09-11T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

PDR_PARENT_EVIDENCE = {
    "reference": IDENTIFIER,
    "snippet": (
        "Pleiotropic Drug Resistance factors (PDR) are transcription factors "
        "in fungi that regulate the expression of genes encoding for efflux "
        "pumps causing multidrug resistance."
    ),
    "notes": (
        "CARD definition for the PDR transcription-factor parent; CARD does "
        "not specify whether the parent activates or represses the efflux-pump "
        "genes."
    ),
}

EFFLUX_EVIDENCE = {
    "reference": "ARO:0010000",
    "snippet": "Antibiotic resistance via the transport of antibiotics out of the cell.",
    "notes": "CARD definition for antibiotic efflux.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "antibiotic efflux",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:0010000",
}

TRANSPORTER_GENES_NODE = {
    "node_id": "transporter_genes",
    "label": "genes encoding fungal efflux pumps",
    "node_type": "NUCLEIC_ACID",
    "local": True,
    "description": (
        "Local node for the efflux-pump genes regulated by PDR transcription "
        "factors; CARD names no exact gene at this generic parent."
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
    ("determinant", "RO:0002211", "transporter_genes"),
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
    allowed_edges = INITIAL_EDGE_KEYS | EXPECTED_EDGE_KEYS
    for edge in _dicts(graph.get("edges")):
        key = _edge_key(edge)
        if key not in allowed_edges:
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
        copy.deepcopy(TRANSPORTER_GENES_NODE),
        copy.deepcopy(RESISTANCE_NODE),
    ]


def _canonical_edges(record: dict[str, Any]) -> list[dict[str, Any]]:
    source_evidence = _source_evidence(record)
    mechanism_evidence = (PDR_PARENT_EVIDENCE, EFFLUX_EVIDENCE, *source_evidence)
    return [
        _edge(
            "determinant",
            "participates in (resistance mechanism)",
            "RO:0000056",
            "mech0",
            (
                "CARD classifies fungal PDR transcription factors under "
                "antibiotic efflux because they regulate efflux-pump genes."
            ),
            mechanism_evidence,
        ),
        _edge(
            "mech0",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            "Antibiotic efflux is the broad mechanism downstream of PDR regulation.",
            mechanism_evidence,
        ),
        _edge(
            "determinant",
            "causally upstream of (confers resistance)",
            "RO:0002411",
            "resistance",
            (
                "Regulation of efflux-pump genes by fungal PDR transcription "
                "factors causes multidrug resistance."
            ),
            (PDR_PARENT_EVIDENCE, *source_evidence, EFFLUX_EVIDENCE),
        ),
        _edge(
            "determinant",
            "regulates (efflux-pump gene expression)",
            "RO:0002211",
            "transporter_genes",
            (
                "Neutral RO:0002211 is used because CARD says PDR transcription "
                "factors regulate genes encoding efflux pumps but does not "
                "assert a direction at this generic parent."
            ),
            (PDR_PARENT_EVIDENCE, *source_evidence),
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
    graph["title"] = "fungal PDR transcription factors → efflux-pump genes → multidrug resistance"
    graph["description"] = (
        "Curated generic graph for fungal PDR transcription factors. CARD "
        "states that PDR factors regulate the expression of genes encoding "
        "efflux pumps, but does not name exact genes or a direction of "
        "regulation at this parent."
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
