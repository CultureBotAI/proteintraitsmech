#!/usr/bin/env python3
"""Collapse and complete Alm polymyxin-resistance glycylation graphs.

The ARO Alm records already carry a curated graph for the AlmE/AlmF/AlmG
glycylation route, but it leaves the exact transfer step and lipid-A chemical
ungrounded. This updater keeps the Alm-specific relay as described local
states instead of inventing ontology IDs.

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
HISTORY_ACTION = "Collapsed and described Alm lipid A glycylation graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

CHARGE_ALTERATION_EVIDENCE = {
    "reference": "ARO:3003588",
    "snippet": (
        "The loss or reduction of the net negative charge within the cell wall "
        "of gram negative bacteria is a mechanism of resistance for cationic "
        "antimicrobials that depend on the negative charge for binding to the "
        "surface."
    ),
    "notes": (
        "CARD definition for the shared charge-alteration resistance mechanism."
    ),
}

ALMEFG_OPERON_EVIDENCE = {
    "reference": "ARO:3007434",
    "snippet": (
        "The almEFG operon is responsible for glycylation of lipid A as a "
        "mechanism of colistin resistance in Vibrio cholerae."
    ),
    "notes": "CARD definition for the AlmEFG operon.",
}

ALMEFG_RELAY_EVIDENCE = {
    "reference": "ARO:3007434",
    "snippet": (
        "Its mechanism involves transfer of a glycyl molecule to the carrier "
        "protein almF by almE followed by glycylation of lipid A by almG."
    ),
    "notes": (
        "CARD definition of the AlmEFG relay: AlmE charges AlmF with glycine "
        "before AlmG glycylates lipid A."
    ),
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "charge alteration conferring antibiotic resistance",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3003588",
}

DRUG_NODE = {
    "node_id": "drug0",
    "label": "peptide antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:3000053",
}

GLYCYLATED_LIPID_A_NODE = {
    "node_id": "glycylated_lipid_a",
    "label": "glycylated lipid A",
    "node_type": "STATE",
    "description": (
        "Local state representing lipid A after the AlmEFG relay adds glycine; "
        "left ungrounded because this branch asserts no exact ontology class for "
        "Alm-glycylated lipid A."
    ),
}

CHARGE_NODE = {
    "node_id": "charge",
    "label": "reduced net negative surface charge",
    "node_type": "STATE",
    "description": (
        "Local state representing the reduced negative envelope charge produced "
        "by lipid A glycylation."
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

CORE_EDGE_KEYS = {
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("determinant", "ARO:2000001", "drug0"),
    ("charge", "RO:0002212", "drug0"),
}

LEGACY_GLYCYLATION_EDGE_KEYS = {
    ("determinant", "RO:0000056", "glycyl_transfer"),
    ("glycyl_transfer", "RO:0002411", "lipid_a"),
    ("lipid_a", "RO:0002411", "charge"),
}

CANONICAL_GLYCYLATION_EDGE_KEYS = {
    ("determinant", "RO:0002411", "glycylated_lipid_a"),
    ("glycylated_lipid_a", "RO:0002411", "charge"),
}

CHARGE_RESISTANCE_EDGE_KEY = ("charge", "RO:0002411", "resistance")


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    drug_relation_reference: str


TARGETS = {
    "ARO:3007430": Target(
        identifier="ARO:3007430",
        filename="alm-glycyl-carrier-protein-aro3007430.yaml",
        drug_relation_reference="ARO:3007430",
    ),
    "ARO:3007431": Target(
        identifier="ARO:3007431",
        filename="almf-aro3007431.yaml",
        drug_relation_reference="ARO:3007430",
    ),
    "ARO:3007432": Target(
        identifier="ARO:3007432",
        filename="alm-glycyltransferase-aro3007432.yaml",
        drug_relation_reference="ARO:3007432",
    ),
    "ARO:3007433": Target(
        identifier="ARO:3007433",
        filename="alme-aro3007433.yaml",
        drug_relation_reference="ARO:3007432",
    ),
    "ARO:3004364": Target(
        identifier="ARO:3004364",
        filename="almg-aro3004364.yaml",
        drug_relation_reference="ARO:3004363",
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


def _canonical_edge_keys() -> set[tuple[str, str, str]]:
    return CORE_EDGE_KEYS | CANONICAL_GLYCYLATION_EDGE_KEYS | {CHARGE_RESISTANCE_EDGE_KEY}


def _input_allowed_edges() -> set[tuple[str, str, str]]:
    return _canonical_edge_keys() | LEGACY_GLYCYLATION_EDGE_KEYS


def _target_evidence(record: dict[str, Any]) -> dict[str, str]:
    return {
        "reference": str(record["identifier"]),
        "snippet": str(record["definition"]),
        "notes": f"CARD definition for {record['label']}.",
    }


def _drug_evidence(target: Target) -> dict[str, str]:
    if target.identifier == target.drug_relation_reference:
        notes = (
            f"Asserted directly on {target.identifier}; modeled here as a "
            "determinant-to-peptide-antibiotic drug-class edge."
        )
    else:
        notes = (
            f"Asserted on ancestor {target.drug_relation_reference}; modeled here "
            "as an inherited determinant-to-peptide-antibiotic drug-class edge."
        )
    return {
        "reference": target.drug_relation_reference,
        "snippet": (
            "relationship: confers_resistance_to_drug_class ARO:3000053 ! "
            "peptide antibiotic"
        ),
        "notes": notes,
    }


def _unique_evidence(evidence: tuple[dict[str, str], ...]) -> list[dict[str, str]]:
    unique: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for item in evidence:
        key = (item["reference"], item["snippet"], item.get("notes", ""))
        if key in seen:
            continue
        seen.add(key)
        unique.append(copy.deepcopy(item))
    return unique


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
            "evidence": _unique_evidence(evidence),
        }
    )


def _nodes_by_id(graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(node["node_id"]): node
        for node in graph.get("nodes") or []
        if isinstance(node, dict) and "node_id" in node
    }


def _validate_graph(graph: dict[str, Any], target: Target) -> None:
    nodes = _nodes_by_id(graph)
    required_nodes = {"determinant", "mech0", "drug0", "charge", "resistance"}
    found_nodes = set(nodes)
    if "glycylated_lipid_a" in found_nodes:
        required_nodes.add("glycylated_lipid_a")
    else:
        required_nodes.update({"glycyl_transfer", "lipid_a"})

    missing_nodes = sorted(required_nodes - found_nodes)
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")

    found_edges = set()
    seen: set[tuple[str, str, str]] = set()
    for edge in graph.get("edges") or []:
        key = _edge_key(edge)
        if key not in _input_allowed_edges():
            raise ValueError(f"{target.identifier}: unexpected edge {key[0]} -> {key[2]}")
        if key in seen:
            raise ValueError(f"{target.identifier}: duplicate edge {key[0]} -> {key[2]}")
        seen.add(key)
        found_edges.add(key)

    missing_core = sorted(CORE_EDGE_KEYS - found_edges)
    if missing_core:
        missing = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in missing_core)
        raise ValueError(f"{target.identifier}: missing core edge(s): {missing}")

    has_legacy_route = LEGACY_GLYCYLATION_EDGE_KEYS <= found_edges
    has_canonical_route = CANONICAL_GLYCYLATION_EDGE_KEYS <= found_edges
    if not has_legacy_route and not has_canonical_route:
        raise ValueError(
            f"{target.identifier}: missing both canonical and legacy glycylation edges"
        )


def _canonical_nodes(graph: dict[str, Any]) -> list[dict[str, Any]]:
    nodes = _nodes_by_id(graph)
    return [
        copy.deepcopy(nodes["determinant"]),
        copy.deepcopy(MECHANISM_NODE),
        copy.deepcopy(DRUG_NODE),
        copy.deepcopy(GLYCYLATED_LIPID_A_NODE),
        copy.deepcopy(CHARGE_NODE),
        copy.deepcopy(RESISTANCE_NODE),
    ]


def _canonical_edges(record: dict[str, Any], target: Target) -> list[dict[str, Any]]:
    target_evidence = _target_evidence(record)
    route_evidence = (target_evidence, ALMEFG_OPERON_EVIDENCE, ALMEFG_RELAY_EVIDENCE)
    charge_evidence = (ALMEFG_OPERON_EVIDENCE, CHARGE_ALTERATION_EVIDENCE)
    route_charge_evidence = (
        ALMEFG_OPERON_EVIDENCE,
        ALMEFG_RELAY_EVIDENCE,
        CHARGE_ALTERATION_EVIDENCE,
    )
    drug_evidence = (
        target_evidence,
        _drug_evidence(target),
        ALMEFG_OPERON_EVIDENCE,
    )

    return [
        _edge(
            "determinant",
            "participates in (resistance mechanism)",
            "RO:0000056",
            "mech0",
            (
                "The Alm determinant participates in the charge-alteration "
                "resistance mechanism through AlmEFG-dependent lipid A glycylation."
            ),
            route_charge_evidence,
        ),
        _edge(
            "mech0",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            "Charge alteration is the broad resistance mechanism for this Alm route.",
            charge_evidence,
        ),
        _edge(
            "determinant",
            "causally upstream of (confers resistance)",
            "RO:0002411",
            "resistance",
            "The Alm component contributes to lipid A glycylation and colistin resistance.",
            route_charge_evidence,
        ),
        _edge(
            "determinant",
            "confers resistance to (drug class)",
            "ARO:2000001",
            "drug0",
            "ARO links this Alm determinant or its parent to peptide-antibiotic resistance.",
            drug_evidence,
        ),
        _edge(
            "determinant",
            "causally upstream of (Alm-mediated lipid A glycylation)",
            "RO:0002411",
            "glycylated_lipid_a",
            (
                "AlmE, AlmF, and AlmG are modeled as operon components upstream "
                "of the glycylated-lipid-A state instead of as exact single "
                "enzymes for an ungrounded relay."
            ),
            route_evidence,
        ),
        _edge(
            "glycylated_lipid_a",
            "causally upstream of (reduces surface negative charge)",
            "RO:0002411",
            "charge",
            "Lipid A glycylation is the modeled surface modification that lowers charge.",
            route_charge_evidence,
        ),
        _edge(
            "charge",
            "negatively regulates (impedes drug binding)",
            "RO:0002212",
            "drug0",
            (
                "Lower net negative surface charge impedes binding by cationic "
                "peptide antibiotics such as colistin."
            ),
            charge_evidence,
        ),
        _edge(
            "charge",
            "causally upstream of (reduced peptide-antibiotic binding)",
            "RO:0002411",
            "resistance",
            (
                "The charge reduction caused by Alm-mediated lipid A glycylation "
                "is modeled as the terminal causal state for resistance."
            ),
            route_charge_evidence,
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
    graph["title"] = f"{record['label']} → Alm lipid A glycylation → resistance"
    graph["description"] = (
        "Conservative graph for an AlmEFG polymyxin-resistance component. The "
        "graph keeps the ARO charge-alteration and peptide-antibiotic routes, "
        "collapses the ungrounded Alm-specific glycyl relay to a described "
        "glycylated-lipid-A state, and connects the reduced surface-charge state "
        "to the resistance phenotype."
    )
    graph["nodes"] = _canonical_nodes(graph)
    graph["edges"] = _canonical_edges(out, target)
    return out, out.get("causal_graphs") != before


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: record is not a mapping")
    identifier = record.get("identifier")
    target = TARGETS.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not an Alm target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
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
    return [path / target.filename for target in TARGETS.values()]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    parser.add_argument(
        "--path",
        type=Path,
        default=ARO_DIR,
        help="ARO directory or one of the five target YAML files",
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
