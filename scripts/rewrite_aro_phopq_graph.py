#!/usr/bin/env python3
"""Rewrite the phoPQ graph around two-component efflux modulation.

The phoPQ record belongs to the two-component regulatory family that modulates
antibiotic efflux, but the previous graph reused the AcrR repressor archetype
and therefore claimed a generic pump-repression route. This updater keeps the
inherited antibiotic-efflux mechanism and models PhoPQ's downstream effect as a
local altered-efflux-rate state rather than a species-specific pump target.

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

HISTORY_ACTION = "Modeled phoPQ two-component efflux modulation"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

TARGET_IDENTIFIER = "ARO:3000821"
TARGET_FILENAME = "phopq-aro3000821.yaml"

PHOPQ_EVIDENCE = {
    "reference": TARGET_IDENTIFIER,
    "snippet": (
        "PhoPQ is a two-component regulatory system. phoP is phosphorylated "
        "by phoQ at a low [mg2+], activating the repressor. Its part of a two "
        "component regulating system that activates the PmrA/B system which "
        "has downstream effects, leading to Antimicrobial resistance in many "
        "pathogens. In Salmonella, phoP bind to macAB ABC transporter and "
        "represses it. In Escherichia coli, phoPQ regulates arnA expression. "
        "In Pseudomonas aeruginosa, phoPQ regulates OprH expression. phoPQ "
        "have other roles in other species."
    ),
    "notes": "CARD definition for phoPQ.",
}

TCS_EFFLUX_EVIDENCE = {
    "reference": "ARO:3000451",
    "snippet": (
        "Protein(s) and two component regulatory systems that directly or "
        "indirectly change rates of antibiotic efflux."
    ),
    "notes": "CARD definition for the inherited two-component efflux-modulation parent.",
}

EFFLUX_EVIDENCE = {
    "reference": "ARO:0010000",
    "snippet": "Antibiotic resistance via the transport of antibiotics out of the cell.",
    "notes": "CARD definition for antibiotic efflux.",
}

PEPTIDE_ANTIBIOTIC_EVIDENCE = {
    "reference": "ARO:3000053",
    "snippet": "peptide antibiotic",
    "notes": "ARO drug-class term asserted on phoPQ.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "antibiotic efflux",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:0010000",
}

PEPTIDE_NODE = {
    "node_id": "drug0",
    "label": "peptide antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:3000053",
}

EFFLUX_MODULATION_NODE = {
    "node_id": "efflux_modulation",
    "label": "altered antibiotic efflux rate",
    "node_type": "STATE",
    "description": (
        "Local state for direct or indirect changes to antibiotic efflux rates "
        "downstream of the PhoPQ two-component regulatory system."
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

EXPECTED_EDGE_KEYS = {
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("determinant", "ARO:2000001", "drug0"),
    ("determinant", "RO:0002411", "efflux_modulation"),
    ("efflux_modulation", "RO:0002411", "resistance"),
}

REMOVED_ACRR_EDGE_KEYS = {
    ("determinant", "RO:0002327", "repression"),
    ("repression", "RO:0002212", "pump"),
    ("determinant", "RO:0002212", "repression"),
    ("pump", "RO:0002212", "drug0"),
}

EDGE_DESCRIPTIONS = {
    ("determinant", "RO:0000056", "mech0"): (
        "ARO classifies phoPQ under antibiotic efflux through the "
        "two-component efflux-modulation parent."
    ),
    ("mech0", "RO:0002411", "resistance"): (
        "PhoPQ is inherited from a two-component regulatory family that "
        "changes rates of antibiotic efflux."
    ),
    ("determinant", "RO:0002411", "resistance"): (
        "The PhoPQ two-component system has downstream effects leading to "
        "antimicrobial resistance in multiple pathogens."
    ),
    ("determinant", "ARO:2000001", "drug0"): (
        "ARO maps phoPQ to peptide antibiotics."
    ),
    ("determinant", "RO:0002411", "efflux_modulation"): (
        "PhoPQ participates in species-specific regulatory branches that "
        "change downstream resistance effectors."
    ),
    ("efflux_modulation", "RO:0002411", "resistance"): (
        "The inherited parent places direct or indirect changes in antibiotic "
        "efflux rates downstream of two-component systems."
    ),
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str


TARGET = Target(identifier=TARGET_IDENTIFIER, filename=TARGET_FILENAME)


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
    unique: list[dict[str, str]] = []
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
    missing_nodes = sorted({"determinant", "mech0", "drug0", "resistance"} - set(nodes))
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")

    found_edges = set()
    seen: set[tuple[str, str, str]] = set()
    old_edge_keys = {_edge_key(edge) for edge in _dicts(graph.get("edges"))}
    for edge in _dicts(graph.get("edges")):
        key = _edge_key(edge)
        if key in REMOVED_ACRR_EDGE_KEYS:
            continue
        if key not in EXPECTED_EDGE_KEYS:
            raise ValueError(f"{target.identifier}: unexpected edge {key[0]} -> {key[2]}")
        if key in seen:
            raise ValueError(f"{target.identifier}: duplicate edge {key[0]} -> {key[2]}")
        seen.add(key)
        found_edges.add(key)

    if REMOVED_ACRR_EDGE_KEYS <= old_edge_keys:
        required_edges = EXPECTED_EDGE_KEYS - {
            ("determinant", "RO:0002411", "efflux_modulation"),
            ("efflux_modulation", "RO:0002411", "resistance"),
        }
    else:
        required_edges = EXPECTED_EDGE_KEYS

    missing_edges = sorted(required_edges - found_edges)
    if missing_edges:
        missing = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in missing_edges)
        raise ValueError(f"{target.identifier}: missing edge(s): {missing}")


def _canonical_graph(record: dict[str, Any], target: Target) -> dict[str, Any]:
    graph = record["causal_graphs"][0]
    _validate_graph(graph, target)
    nodes = _nodes_by_id(graph)
    source_evidence = _source_evidence(record)
    mechanism_evidence = (
        PHOPQ_EVIDENCE,
        TCS_EFFLUX_EVIDENCE,
        EFFLUX_EVIDENCE,
        *source_evidence,
    )
    resistance_evidence = (
        PHOPQ_EVIDENCE,
        TCS_EFFLUX_EVIDENCE,
        *source_evidence,
    )
    drug_evidence = (
        {
            "reference": TARGET_IDENTIFIER,
            "snippet": (
                "relationship: confers_resistance_to_drug_class ARO:3000053 ! "
                "peptide antibiotic"
            ),
            "notes": "ARO drug-class relationship asserted directly on phoPQ.",
        },
        PEPTIDE_ANTIBIOTIC_EVIDENCE,
        PHOPQ_EVIDENCE,
        *source_evidence,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → two-component antibiotic-efflux modulation",
        "description": (
            "Conservative graph for PhoPQ-mediated antibiotic resistance. The "
            "graph removes the AcrR-specific pump-repression branch and keeps "
            "the ARO-inherited claim that PhoPQ acts through two-component "
            "regulation that directly or indirectly changes antibiotic efflux "
            "rates."
        ),
        "nodes": [
            copy.deepcopy(nodes["determinant"]),
            copy.deepcopy(MECHANISM_NODE),
            copy.deepcopy(PEPTIDE_NODE),
            copy.deepcopy(EFFLUX_MODULATION_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                mechanism_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                mechanism_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                resistance_evidence,
            ),
            _edge(
                "determinant",
                "confers resistance to (drug class)",
                "ARO:2000001",
                "drug0",
                drug_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of",
                "RO:0002411",
                "efflux_modulation",
                resistance_evidence,
            ),
            _edge(
                "efflux_modulation",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                mechanism_evidence,
            ),
        ],
    }


def enrich_record(record: dict[str, Any], target: Target = TARGET) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != target.identifier:
        raise ValueError(
            f"{target.filename}: expected {target.identifier}, "
            f"found {record.get('identifier')}"
        )
    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1 or graphs[0].get("graph_id") != "resistance":
        raise ValueError(f"{target.identifier}: expected exactly one resistance graph")

    out = copy.deepcopy(record)
    out["causal_graphs"] = [_canonical_graph(record, target)]
    return out, out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    if path.name != TARGET.filename:
        raise ValueError(f"not the phoPQ target: {path}")

    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")
    enriched, changed = enrich_record(record)
    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))

    history = list(_dicts(enriched.get("curation_history")))
    if not any(item.get("action") == HISTORY_ACTION for item in history):
        out = append_to_section(out, "curation_history", _dump({"curation_history": [HISTORY_EVENT]}))
        changed = True

    if "&id" in out or "*id" in out:
        raise ValueError(f"{path}: YAML anchors leaked into output")
    return out, changed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--path", type=Path, default=ARO_DIR)
    args = parser.parse_args(argv)

    path = args.path / TARGET.filename
    before = path.read_text(encoding="utf-8")
    after, changed = enrich_text(before, path)
    if changed:
        if args.apply:
            path.write_text(after, encoding="utf-8")
            print(f"  wrote {TARGET.filename}")
            print("changed: 1")
        else:
            print(f"  would write {TARGET.filename}")
            print("would change: 1")
            print("dry run -- pass --apply to write")
        return 0

    print("changed: 0" if args.apply else "would change: 0")
    print("already enriched: 1")
    if not args.apply:
        print("dry run -- pass --apply to write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
