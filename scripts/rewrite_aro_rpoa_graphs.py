#!/usr/bin/env python3
"""Ground and evidence the conservative antibiotic-resistant rpoA graphs.

The rpoA branch can assert that RNA polymerase participates in
DNA-templated transcription, but not the active-center side path available to
rpoB and rpoC. This updater keeps that conservative shape, grounds the
transcription node to GO:0006351, and adds descriptions and inherited evidence
to the mutation and drug-class edges.

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

HISTORY_ACTION = "Grounded conservative rpoA transcription graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

PARENT_IDENTIFIER = "ARO:3004997"

PARENT_EVIDENCE = {
    "reference": PARENT_IDENTIFIER,
    "snippet": (
        "RNA polymerase is a multisubunit enzyme that is necessary for "
        "transcription. Mutations in rpoA gene confer antibiotic resistance."
    ),
    "notes": "CARD definition for the antibiotic resistant rpoA parent term.",
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

RIFAMPICIN_RPOA_EVIDENCE = {
    "reference": "ARO:3004998",
    "snippet": "rpoA catalyzes the transcription of DNA into RNA and mutations confer resistance to rifampicin.",
    "notes": "CARD definition for the rifampicin resistant rpoA parent term.",
}

RIFAMYCIN_EVIDENCE = {
    "reference": "ARO:3000157",
    "snippet": "rifamycin antibiotic",
    "notes": "ARO drug-class term inherited by rifampicin-resistant rpoA records.",
}

TRANSCRIPTION_NODE = {
    "node_id": "transcription",
    "label": "DNA-templated transcription",
    "node_type": "BIOLOGICAL_PROCESS",
    "grounding": "GO:0006351",
    "description": (
        "Grounded to the GO DNA-templated transcription process named generically "
        "in the ARO RNA-polymerase definition."
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
    ("determinant", "RO:0000056", "transcription"),
}

DRUG_EDGE_KEY = ("determinant", "ARO:2000001", "drug0")

EDGE_DESCRIPTIONS = {
    ("determinant", "RO:0000056", "mech0"): (
        "ARO classifies resistant rpoA variants under mutation conferring "
        "antibiotic resistance."
    ),
    ("mech0", "RO:0002411", "resistance"): (
        "The broad ARO mutation mechanism covers altered gene products that may "
        "result in antibiotic resistance."
    ),
    ("determinant", "RO:0002411", "resistance"): (
        "ARO states that mutations in rpoA confer antibiotic resistance while "
        "leaving the alpha-subunit-specific mechanism unresolved."
    ),
    ("determinant", "ARO:2000001", "drug0"): (
        "ARO maps rifampicin-resistant rpoA to rifamycin antibiotics."
    ),
    ("determinant", "RO:0000056", "transcription"): (
        "The rpoA determinant participates in the RNA-polymerase transcription "
        "process; no active-center edge is asserted for the alpha subunit."
    ),
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    has_drug: bool = False
    inherited_resistance_evidence: tuple[dict[str, str], ...] = ()


TARGETS = {
    "ARO:3004997": Target(
        identifier="ARO:3004997",
        filename="antibiotic-resistant-rpoa-aro3004997.yaml",
    ),
    "ARO:3004998": Target(
        identifier="ARO:3004998",
        filename="rifampicin-resistant-rpoa-aro3004998.yaml",
        has_drug=True,
    ),
    "ARO:3004999": Target(
        identifier="ARO:3004999",
        filename=(
            "mycobacterium-tuberculosis-rpoa-mutations-confer-resistance-to-"
            "rifampicin-aro3004999.yaml"
        ),
        has_drug=True,
        inherited_resistance_evidence=(RIFAMPICIN_RPOA_EVIDENCE,),
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
    reference = "ARO:3004998"
    return {
        "reference": reference,
        "snippet": "relationship: confers_resistance_to_drug_class ARO:3000157 ! rifamycin antibiotic",
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
    expected_nodes = {"determinant", "mech0", "transcription", "resistance"}
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
            copy.deepcopy(TRANSCRIPTION_NODE),
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
    transcription_evidence = (
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
                    RIFAMPICIN_RPOA_EVIDENCE,
                    _drug_relation_evidence(target),
                    RIFAMYCIN_EVIDENCE,
                    *source_evidence,
                ),
            )
        )

    edges.append(
        _edge(
            "determinant",
            "participates in (transcription)",
            "RO:0000056",
            "transcription",
            transcription_evidence,
        )
    )
    return edges


def _canonical_graph(record: dict[str, Any], target: Target) -> dict[str, Any]:
    graph = record["causal_graphs"][0]
    _validate_graph(graph, target)
    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → rpoA transcription role → antibiotic resistance",
        "description": (
            "Conservative graph for antibiotic-resistant rpoA. The graph keeps "
            "the ARO point-mutation resistance route, grounds rpoA's "
            "transcription role, and omits rpoB/rpoC-style active-center "
            "partonomy because ARO does not assert it for the alpha subunit."
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
        raise ValueError(f"not an rpoA target: {path}")

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
