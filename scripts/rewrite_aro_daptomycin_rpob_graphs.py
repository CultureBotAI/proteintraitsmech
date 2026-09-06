#!/usr/bin/env python3
"""Model daptomycin-resistant rpoB through dlt expression and surface charge.

The daptomycin rpoB records have their own ARO mechanism: rpoB amino-acid
substitutions alter dlt operon expression, increasing cell-surface positive
charge. This updater removes the generic RNA-polymerase active-center side path
and replaces it with that daptomycin-specific local state chain.

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

HISTORY_ACTION = "Modeled daptomycin rpoB dlt-charge route"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

PARENT_IDENTIFIER = "ARO:3003090"
PARENT_EVIDENCE = {
    "reference": PARENT_IDENTIFIER,
    "snippet": (
        "Daptomycin-resistant RNA polymerases include amino acids substitutions "
        "which alter expression of the dlt operon, which increases the cell "
        "surface positive charge. Known from S. aureus."
    ),
    "notes": "CARD definition for the daptomycin-resistant rpoB parent.",
}

MUTATION_EVIDENCE = {
    "reference": "ARO:3000212",
    "snippet": (
        "Point mutations in the DNA may lead to an altered gene product that "
        "may result in antibiotic resistance."
    ),
    "notes": "CARD definition for mutation conferring antibiotic resistance.",
}

PEPTIDE_ANTIBIOTIC_EVIDENCE = {
    "reference": "ARO:3000053",
    "snippet": "peptide antibiotic",
    "notes": "ARO drug-class term inherited by daptomycin-resistant rpoB records.",
}

RIFAMYCIN_EVIDENCE = {
    "reference": "ARO:3000157",
    "snippet": "rifamycin antibiotic",
    "notes": "ARO drug-class term inherited by daptomycin-resistant rpoB records.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "mutation conferring antibiotic resistance",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3000212",
}

PEPTIDE_NODE = {
    "node_id": "drug0",
    "label": "peptide antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:3000053",
}

RIFAMYCIN_NODE = {
    "node_id": "drug1",
    "label": "rifamycin antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:3000157",
}

DLT_EXPRESSION_NODE = {
    "node_id": "dlt_expression",
    "label": "altered dlt operon expression",
    "node_type": "STATE",
    "description": (
        "Local state for altered expression of the dlt operon downstream of "
        "daptomycin-resistant rpoB substitutions."
    ),
}

SURFACE_CHARGE_NODE = {
    "node_id": "surface_charge",
    "label": "increased cell-surface positive charge",
    "node_type": "STATE",
    "description": (
        "Local state for the increased cell-surface positive charge that ARO "
        "places downstream of altered dlt operon expression."
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
    ("determinant", "ARO:2000001", "drug1"),
    ("determinant", "RO:0002411", "dlt_expression"),
    ("dlt_expression", "RO:0002411", "surface_charge"),
    ("surface_charge", "RO:0002411", "resistance"),
}

OLD_RNAP_EDGE_KEYS = {
    ("determinant", "BFO:0000050", "active_center"),
    ("active_center", "BFO:0000050", "transcription"),
}

EDGE_DESCRIPTIONS = {
    ("determinant", "RO:0000056", "mech0"): (
        "ARO classifies daptomycin-resistant rpoB under mutation conferring "
        "antibiotic resistance."
    ),
    ("mech0", "RO:0002411", "resistance"): (
        "The daptomycin-resistant rpoB mechanism is a resistance-conferring "
        "amino-acid-substitution route."
    ),
    ("determinant", "RO:0002411", "resistance"): (
        "Daptomycin-resistant rpoB substitutions alter dlt operon expression "
        "and increase cell-surface positive charge."
    ),
    ("determinant", "ARO:2000001", "drug0"): (
        "ARO maps daptomycin-resistant rpoB to peptide antibiotics."
    ),
    ("determinant", "ARO:2000001", "drug1"): (
        "ARO maps daptomycin-resistant rpoB to rifamycin antibiotics."
    ),
    ("determinant", "RO:0002411", "dlt_expression"): (
        "Daptomycin-resistant rpoB substitutions alter expression of the dlt "
        "operon."
    ),
    ("dlt_expression", "RO:0002411", "surface_charge"): (
        "Altered dlt operon expression increases the cell-surface positive "
        "charge."
    ),
    ("surface_charge", "RO:0002411", "resistance"): (
        "The increased positive cell-surface charge is the daptomycin branch "
        "that ARO places downstream of resistant rpoB substitutions."
    ),
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str

    @property
    def is_parent(self) -> bool:
        return self.identifier == PARENT_IDENTIFIER


TARGETS = {
    "ARO:3003090": Target(
        identifier="ARO:3003090",
        filename="daptomycin-resistant-beta-subunit-of-rna-polymerase-rpob-aro3003090.yaml",
    ),
    "ARO:3003287": Target(
        identifier="ARO:3003287",
        filename="staphylococcus-aureus-rpob-mutants-conferring-resistance-to-daptomycin-aro3003287.yaml",
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


def _target_evidence(record: dict[str, Any], target: Target) -> dict[str, str]:
    if target.is_parent:
        return PARENT_EVIDENCE
    return {
        "reference": str(record["identifier"]),
        "snippet": str(record["definition"]),
        "notes": f"CARD definition for {record['label']}.",
    }


def _drug_relation_evidence(target: Target, drug_node: str) -> dict[str, str]:
    drug_label = {
        "drug0": "peptide antibiotic",
        "drug1": "rifamycin antibiotic",
    }[drug_node]
    drug_aro = {
        "drug0": "ARO:3000053",
        "drug1": "ARO:3000157",
    }[drug_node]
    if target.is_parent:
        notes = "ARO drug-class relationship asserted directly on daptomycin-resistant rpoB."
    else:
        notes = (
            "ARO drug-class relationship asserted on ARO:3003090 and inherited "
            f"by {target.identifier}."
        )
    return {
        "reference": PARENT_IDENTIFIER,
        "snippet": f"relationship: confers_resistance_to_drug_class {drug_aro} ! {drug_label}",
        "notes": notes,
    }


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
    missing_nodes = sorted({"determinant", "mech0", "drug0", "drug1"} - set(nodes))
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")

    found_edges = set()
    seen: set[tuple[str, str, str]] = set()
    for edge in _dicts(graph.get("edges")):
        key = _edge_key(edge)
        if key in OLD_RNAP_EDGE_KEYS:
            continue
        if key not in EXPECTED_EDGE_KEYS:
            raise ValueError(f"{target.identifier}: unexpected edge {key[0]} -> {key[2]}")
        if key in seen:
            raise ValueError(f"{target.identifier}: duplicate edge {key[0]} -> {key[2]}")
        seen.add(key)
        found_edges.add(key)

    preexisting_edges = EXPECTED_EDGE_KEYS - {
        ("determinant", "RO:0002411", "dlt_expression"),
        ("dlt_expression", "RO:0002411", "surface_charge"),
        ("surface_charge", "RO:0002411", "resistance"),
    }
    missing_edges = sorted(preexisting_edges - found_edges)
    if missing_edges:
        missing = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in missing_edges)
        raise ValueError(f"{target.identifier}: missing edge(s): {missing}")


def _canonical_graph(record: dict[str, Any], target: Target) -> dict[str, Any]:
    graph = record["causal_graphs"][0]
    _validate_graph(graph, target)
    nodes = _nodes_by_id(graph)
    target_evidence = _target_evidence(record, target)
    source_evidence = _source_evidence(record)
    mutation_resistance_evidence = (
        target_evidence,
        PARENT_EVIDENCE,
        MUTATION_EVIDENCE,
        *source_evidence,
    )
    dlt_charge_evidence = (
        target_evidence,
        PARENT_EVIDENCE,
        *source_evidence,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → dlt expression → positive charge → daptomycin resistance",
        "description": (
            "Conservative graph for daptomycin-resistant rpoB. The graph "
            "models ARO's stated dlt-operon/cell-surface-charge branch and "
            "removes the generic RNA-polymerase active-center side path "
            "because ARO does not connect that structural role to daptomycin "
            "resistance here."
        ),
        "nodes": [
            copy.deepcopy(nodes["determinant"]),
            copy.deepcopy(MECHANISM_NODE),
            copy.deepcopy(PEPTIDE_NODE),
            copy.deepcopy(RIFAMYCIN_NODE),
            copy.deepcopy(DLT_EXPRESSION_NODE),
            copy.deepcopy(SURFACE_CHARGE_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                mutation_resistance_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                mutation_resistance_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                mutation_resistance_evidence,
            ),
            _edge(
                "determinant",
                "confers resistance to",
                "ARO:2000001",
                "drug0",
                (
                    target_evidence,
                    _drug_relation_evidence(target, "drug0"),
                    PEPTIDE_ANTIBIOTIC_EVIDENCE,
                    *source_evidence,
                ),
            ),
            _edge(
                "determinant",
                "confers resistance to",
                "ARO:2000001",
                "drug1",
                (
                    target_evidence,
                    _drug_relation_evidence(target, "drug1"),
                    RIFAMYCIN_EVIDENCE,
                    *source_evidence,
                ),
            ),
            _edge(
                "determinant",
                "causally upstream of",
                "RO:0002411",
                "dlt_expression",
                dlt_charge_evidence,
            ),
            _edge(
                "dlt_expression",
                "causally upstream of",
                "RO:0002411",
                "surface_charge",
                dlt_charge_evidence,
            ),
            _edge(
                "surface_charge",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                dlt_charge_evidence,
            ),
        ],
    }


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
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
    target = next((item for item in TARGETS.values() if item.filename == path.name), None)
    if target is None:
        raise ValueError(f"not a daptomycin rpoB target: {path}")

    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")
    enriched, changed = enrich_record(record, target)
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

    changed = 0
    unchanged = 0
    for target in TARGETS.values():
        path = args.path / target.filename
        before = path.read_text(encoding="utf-8")
        after, did_change = enrich_text(before, path)
        if not did_change:
            unchanged += 1
            continue
        changed += 1
        if args.apply:
            path.write_text(after, encoding="utf-8")
            print(f"  wrote {target.filename}")
        else:
            print(f"  would write {target.filename}")

    if args.apply:
        print(f"changed: {changed}")
        print(f"already enriched: {unchanged}")
    else:
        print(f"would change: {changed}")
        print(f"already enriched: {unchanged}")
        print("dry run -- pass --apply to write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
