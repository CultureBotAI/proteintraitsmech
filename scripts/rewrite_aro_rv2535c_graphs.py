#!/usr/bin/env python3
"""Ground and evidence the conservative Rv2535c aminopeptidase graphs.

The Rv2535c parent and bedaquiline parent name a putative Xaa-Pro
aminopeptidase role but do not describe the route from that role to resistance.
This updater preserves that conservative topology, grounds the role to the
generic GO aminopeptidase activity, and leaves the MmpL5/MmpS5-specific
Rv2535c leaf for a separate efflux pass.

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

HISTORY_ACTION = "Grounded conservative Rv2535c aminopeptidase graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

PARENT_IDENTIFIER = "ARO:3007690"

PARENT_EVIDENCE = {
    "reference": PARENT_IDENTIFIER,
    "snippet": (
        "Rv2535c or pepQ encodes a putative Xaa-Pro aminopeptidase and is a new "
        "genetic determinant of low-level bedaquiline and clofazimine "
        "cross-resistance in Mycobacterium tuberculosis when mutated."
    ),
    "notes": "CARD definition for the antibiotic resistant Rv2535c parent term.",
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

BEDAQUILINE_EVIDENCE = {
    "reference": "ARO:3007691",
    "snippet": "Loss-of-function mutations in Rv2535c are a common mechanism of resistance.",
    "notes": "CARD definition for the bedaquiline resistant Rv2535c parent term.",
}

DIARYLQUINOLINE_EVIDENCE = {
    "reference": "ARO:3004491",
    "snippet": "diarylquinoline antibiotic",
    "notes": "ARO drug-class term inherited by bedaquiline-resistant Rv2535c records.",
}

AMINOPEPTIDASE_NODE = {
    "node_id": "aminopeptidase",
    "label": "putative Xaa-Pro aminopeptidase activity",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "GO:0004177",
    "description": (
        "Grounded to the generic GO aminopeptidase activity. ARO calls the "
        "Rv2535c Xaa-Pro aminopeptidase assignment putative, and the graph "
        "keeps that uncertainty in the label."
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
    ("determinant", "RO:0002327", "aminopeptidase"),
}

DRUG_EDGE_KEY = ("determinant", "ARO:2000001", "drug0")

EDGE_DESCRIPTIONS = {
    ("determinant", "RO:0000056", "mech0"): (
        "ARO classifies resistant Rv2535c variants under mutation conferring "
        "antibiotic resistance."
    ),
    ("mech0", "RO:0002411", "resistance"): (
        "The broad ARO mutation mechanism covers altered gene products that may "
        "result in antibiotic resistance."
    ),
    ("determinant", "RO:0002411", "resistance"): (
        "ARO associates Rv2535c mutations with low-level bedaquiline and "
        "clofazimine cross-resistance."
    ),
    ("determinant", "ARO:2000001", "drug0"): (
        "ARO maps bedaquiline-resistant Rv2535c to diarylquinoline antibiotics."
    ),
    ("determinant", "RO:0002327", "aminopeptidase"): (
        "ARO states that Rv2535c/pepQ encodes a putative Xaa-Pro "
        "aminopeptidase."
    ),
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    has_drug: bool = False
    inherited_resistance_evidence: tuple[dict[str, str], ...] = ()


TARGETS = {
    "ARO:3007690": Target(
        identifier="ARO:3007690",
        filename="antibiotic-resistant-rv2535c-aro3007690.yaml",
    ),
    "ARO:3007691": Target(
        identifier="ARO:3007691",
        filename="bedaquiline-resistant-rv2535c-aro3007691.yaml",
        has_drug=True,
        inherited_resistance_evidence=(BEDAQUILINE_EVIDENCE,),
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


def _drug_relation_evidence(target: Target) -> dict[str, str]:
    reference = "ARO:3007691"
    return {
        "reference": reference,
        "snippet": (
            "relationship: confers_resistance_to_drug_class ARO:3004491 ! "
            "diarylquinoline antibiotic"
        ),
        "notes": (
            f"ARO drug-class relationship asserted on {reference} and inherited "
            f"by {target.identifier}."
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


def _nodes_by_id(graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(node["node_id"]): node
        for node in _dicts(graph.get("nodes"))
        if "node_id" in node
    }


def _expected_edge_keys(target: Target) -> set[tuple[str, str, str]]:
    edge_keys = set(COMMON_EDGE_KEYS)
    if target.has_drug:
        edge_keys.add(DRUG_EDGE_KEY)
    return edge_keys


def _validate_graph(graph: dict[str, Any], target: Target) -> None:
    nodes = _nodes_by_id(graph)
    expected_nodes = {"determinant", "mech0", "aminopeptidase", "resistance"}
    if target.has_drug:
        expected_nodes.add("drug0")
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
    if target.has_drug:
        out.append(copy.deepcopy(nodes["drug0"]))
    out.extend(
        [
            copy.deepcopy(AMINOPEPTIDASE_NODE),
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
    aminopeptidase_evidence = (
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
            mutation_evidence,
        ),
        _edge(
            "mech0",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            mutation_evidence,
        ),
        _edge(
            "determinant",
            "causally upstream of (confers resistance)",
            "RO:0002411",
            "resistance",
            mutation_evidence,
        ),
    ]

    if target.has_drug:
        edges.append(
            _edge(
                "determinant",
                "confers resistance to",
                "ARO:2000001",
                "drug0",
                (
                    own_evidence,
                    BEDAQUILINE_EVIDENCE,
                    _drug_relation_evidence(target),
                    DIARYLQUINOLINE_EVIDENCE,
                    *source_evidence,
                ),
            )
        )

    edges.append(
        _edge(
            "determinant",
            "enables",
            "RO:0002327",
            "aminopeptidase",
            aminopeptidase_evidence,
        )
    )
    return edges


def _canonical_graph(record: dict[str, Any], target: Target) -> dict[str, Any]:
    graph = record["causal_graphs"][0]
    _validate_graph(graph, target)
    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → putative aminopeptidase role → antibiotic resistance",
        "description": (
            "Conservative graph for antibiotic-resistant Rv2535c. The graph "
            "keeps the ARO point-mutation resistance route, grounds the named "
            "putative Xaa-Pro aminopeptidase role, and omits a route from that "
            "activity to resistance because the parent-shaped records do not "
            "describe it."
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
        raise ValueError(f"not an Rv2535c parent-shaped target: {path}")

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
