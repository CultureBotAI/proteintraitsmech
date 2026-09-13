#!/usr/bin/env python3
"""Ground and evidence the conservative antifungal fungal-P450 graphs.

The fungal cytochrome-P450 branch names P450 enzymes and triazole/imidazole drug
classes but does not describe azole binding or lanosterol-demethylase target
alteration. This updater preserves that conservative topology, grounds the
generic cytochrome P450 monooxygenase node to GO:0004497, and adds descriptions
plus inherited ARO/drug-class evidence to every existing edge.

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

HISTORY_ACTION = "Grounded conservative fungal P450 monooxygenase graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

PARENT_IDENTIFIER = "ARO:3007522"

PARENT_EVIDENCE = {
    "reference": PARENT_IDENTIFIER,
    "snippet": (
        "Fungal cytochrome P450 enzymes which include mutations or other "
        "modifications to confer resistance to antifungal drug compounds."
    ),
    "notes": (
        "CARD definition for the antifungal-resistant cytochrome P450 enzyme "
        "parent term."
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

TRIAZOLE_EVIDENCE = {
    "reference": "ARO:3007523",
    "snippet": (
        "Fungal cytochrome P450 enzymes which include mutations to confer "
        "resistance to triazole-class antibiotics."
    ),
    "notes": (
        "CARD definition for the triazole-resistant fungal cytochrome P450 "
        "enzyme parent term."
    ),
}

IMIDAZOLE_EVIDENCE = {
    "reference": "ARO:3007667",
    "snippet": (
        "Fungal cytochrome P450 enzymes which include mutations to confer "
        "resistance to imidazole-class antibiotics."
    ),
    "notes": (
        "CARD definition for the imidazole-resistant fungal cytochrome P450 "
        "enzyme parent term."
    ),
}

P450_ACTIVITY_NODE = {
    "node_id": "p450_activity",
    "label": "cytochrome P450 monooxygenase activity",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "GO:0004497",
    "description": (
        "Grounded to the generic GO monooxygenase activity because ARO names "
        "fungal cytochrome P450 enzymes but does not assert a narrower reaction "
        "for the resistance mechanism."
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

COMMON_EDGE_KEYS = {
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("determinant", "RO:0002327", "p450_activity"),
}

EDGE_DESCRIPTIONS = {
    ("determinant", "RO:0000056", "mech0"): (
        "ARO classifies resistant fungal cytochrome P450 variants under "
        "mutation conferring antibiotic resistance."
    ),
    ("mech0", "RO:0002411", "resistance"): (
        "The broad ARO mutation mechanism covers altered gene products that may "
        "result in antibiotic resistance."
    ),
    ("determinant", "RO:0002411", "resistance"): (
        "ARO reports antifungal resistance for altered fungal cytochrome P450 "
        "enzymes while leaving the target-alteration route unresolved."
    ),
    ("determinant", "RO:0002327", "p450_activity"): (
        "ARO names the determinant as a fungal cytochrome P450 enzyme without "
        "stating an azole-binding mechanism."
    ),
}


@dataclass(frozen=True)
class DrugClass:
    node_id: str
    relation_reference: str
    grounding: str
    label: str


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    drug_classes: tuple[DrugClass, ...] = ()
    inherited_resistance_evidence: tuple[dict[str, str], ...] = ()


TRIAZOLE = DrugClass(
    node_id="drug0",
    relation_reference="ARO:3007523",
    grounding="ARO:3007499",
    label="triazole antibiotic",
)

IMIDAZOLE = DrugClass(
    node_id="drug0",
    relation_reference="ARO:3007667",
    grounding="ARO:3007500",
    label="imidazole antibiotic",
)

IMIDAZOLE_SECOND = DrugClass(
    node_id="drug1",
    relation_reference="ARO:3007667",
    grounding="ARO:3007500",
    label="imidazole antibiotic",
)

TARGETS = {
    "ARO:3007522": Target(
        identifier="ARO:3007522",
        filename="antifungal-resistant-cytochrome-p450-enzyme-aro3007522.yaml",
    ),
    "ARO:3007523": Target(
        identifier="ARO:3007523",
        filename="triazole-resistant-fungal-cytochrome-p450-enzyme-aro3007523.yaml",
        drug_classes=(TRIAZOLE,),
        inherited_resistance_evidence=(TRIAZOLE_EVIDENCE,),
    ),
    "ARO:3007524": Target(
        identifier="ARO:3007524",
        filename=(
            "candida-spp-erg11-with-mutations-conferring-resistance-to-azole-"
            "antibiotics-aro3007524.yaml"
        ),
        drug_classes=(TRIAZOLE,),
        inherited_resistance_evidence=(TRIAZOLE_EVIDENCE,),
    ),
    "ARO:3007565": Target(
        identifier="ARO:3007565",
        filename=(
            "aspergillus-spp-cyp51a-with-mutations-conferring-resistance-to-"
            "triazoles-antibio-aro3007565.yaml"
        ),
        drug_classes=(TRIAZOLE,),
        inherited_resistance_evidence=(TRIAZOLE_EVIDENCE,),
    ),
    "ARO:3007666": Target(
        identifier="ARO:3007666",
        filename=(
            "candida-spp-cyp51a1-with-mutations-conferring-resistance-to-"
            "triazoles-and-imidaz-aro3007666.yaml"
        ),
        drug_classes=(TRIAZOLE, IMIDAZOLE_SECOND),
        inherited_resistance_evidence=(TRIAZOLE_EVIDENCE, IMIDAZOLE_EVIDENCE),
    ),
    "ARO:3007667": Target(
        identifier="ARO:3007667",
        filename="imidazole-resistant-fungal-cytochrome-p450-enzyme-aro3007667.yaml",
        drug_classes=(IMIDAZOLE,),
        inherited_resistance_evidence=(IMIDAZOLE_EVIDENCE,),
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


def _dicts(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _source_evidence(record: dict[str, Any]) -> tuple[dict[str, str], ...]:
    return tuple(
        {
            "reference": str(item["reference"]),
            "notes": str(item.get("notes") or "ARO citation for this record."),
        }
        for item in _dicts(record.get("evidence"))
        if item.get("reference")
    )


def _own_definition_evidence(record: dict[str, Any]) -> dict[str, str]:
    return {
        "reference": str(record["identifier"]),
        "snippet": str(record["definition"]),
        "notes": f"CARD definition for {record['label']}.",
    }


def _drug_term_evidence(drug_class: DrugClass) -> dict[str, str]:
    return {
        "reference": drug_class.grounding,
        "snippet": drug_class.label,
        "notes": f"ARO drug-class term for {drug_class.label}.",
    }


def _drug_relation_evidence(target: Target, drug_class: DrugClass) -> dict[str, str]:
    return {
        "reference": drug_class.relation_reference,
        "snippet": (
            "relationship: confers_resistance_to_drug_class "
            f"{drug_class.grounding} ! {drug_class.label}"
        ),
        "notes": (
            "ARO drug-class relationship asserted on "
            f"{drug_class.relation_reference} and inherited by {target.identifier}."
        ),
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


def _nodes_by_id(graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(node["node_id"]): node
        for node in _dicts(graph.get("nodes"))
        if "node_id" in node
    }


def _expected_edge_keys(target: Target) -> set[tuple[str, str, str]]:
    edge_keys = set(COMMON_EDGE_KEYS)
    edge_keys.update(
        ("determinant", "ARO:2000001", drug_class.node_id)
        for drug_class in target.drug_classes
    )
    return edge_keys


def _validate_graph(graph: dict[str, Any], target: Target) -> None:
    nodes = _nodes_by_id(graph)
    expected_nodes = {"determinant", "mech0", "p450_activity", "resistance"}
    expected_nodes.update(drug_class.node_id for drug_class in target.drug_classes)
    missing_nodes = sorted(expected_nodes - set(nodes))
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")

    expected_edges = _expected_edge_keys(target)
    found_edges = set()
    seen: set[tuple[str, str, str]] = set()
    for edge in _dicts(graph.get("edges")):
        key = _edge_key(edge)
        if key not in expected_edges:
            raise ValueError(f"{target.identifier}: unexpected edge {key[0]} -> {key[2]}")
        if key in seen:
            raise ValueError(f"{target.identifier}: duplicate edge {key[0]} -> {key[2]}")
        seen.add(key)
        found_edges.add(key)

    missing_edges = sorted(expected_edges - found_edges)
    if missing_edges:
        missing = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in missing_edges)
        raise ValueError(f"{target.identifier}: missing edge(s): {missing}")


def _canonical_nodes(graph: dict[str, Any], target: Target) -> list[dict[str, Any]]:
    nodes = _nodes_by_id(graph)
    out = [
        copy.deepcopy(nodes["determinant"]),
        copy.deepcopy(nodes["mech0"]),
    ]
    out.extend(copy.deepcopy(nodes[drug_class.node_id]) for drug_class in target.drug_classes)
    out.extend(
        [
            copy.deepcopy(P450_ACTIVITY_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ]
    )
    return out


def _canonical_edges(
    record: dict[str, Any],
    target: Target,
) -> list[dict[str, Any]]:
    source_evidence = _source_evidence(record)
    own_evidence = _own_definition_evidence(record)
    mutation_evidence = (
        own_evidence,
        PARENT_EVIDENCE,
        MUTATION_EVIDENCE,
        *target.inherited_resistance_evidence,
        *source_evidence,
    )
    p450_evidence = (
        own_evidence,
        PARENT_EVIDENCE,
        *target.inherited_resistance_evidence,
        *source_evidence,
    )

    edges = [
        _edge(
            "determinant",
            "participates in (resistance mechanism)",
            "RO:0000056",
            "mech0",
            EDGE_DESCRIPTIONS[("determinant", "RO:0000056", "mech0")],
            mutation_evidence,
        ),
        _edge(
            "mech0",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            EDGE_DESCRIPTIONS[("mech0", "RO:0002411", "resistance")],
            mutation_evidence,
        ),
        _edge(
            "determinant",
            "causally upstream of (confers resistance)",
            "RO:0002411",
            "resistance",
            EDGE_DESCRIPTIONS[("determinant", "RO:0002411", "resistance")],
            mutation_evidence,
        ),
    ]

    for drug_class in target.drug_classes:
        edges.append(
            _edge(
                "determinant",
                "confers resistance to",
                "ARO:2000001",
                drug_class.node_id,
                f"ARO maps this fungal cytochrome P450 determinant to {drug_class.label}.",
                (
                    own_evidence,
                    _drug_relation_evidence(target, drug_class),
                    _drug_term_evidence(drug_class),
                    *target.inherited_resistance_evidence,
                    *source_evidence,
                ),
            )
        )

    edges.append(
        _edge(
            "determinant",
            "enables",
            "RO:0002327",
            "p450_activity",
            EDGE_DESCRIPTIONS[("determinant", "RO:0002327", "p450_activity")],
            p450_evidence,
        )
    )
    return edges


def _canonical_graph(record: dict[str, Any], target: Target) -> dict[str, Any]:
    graph = record["causal_graphs"][0]
    _validate_graph(graph, target)
    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → cytochrome P450 role → antifungal resistance",
        "description": (
            "Conservative graph for antifungal-resistant fungal cytochrome "
            "P450 enzymes. The graph keeps the ARO mutation resistance route, "
            "grounds the named cytochrome P450 monooxygenase role, and omits "
            "azole-binding and lanosterol-demethylase target-alteration edges "
            "because ARO does not state them for this branch."
        ),
        "nodes": _canonical_nodes(graph, target),
        "edges": _canonical_edges(record, target),
    }


def enrich_record(
    record: dict[str, Any],
    target: Target,
) -> tuple[dict[str, Any], bool]:
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
        raise ValueError(f"not a fungal P450 target: {path}")

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
