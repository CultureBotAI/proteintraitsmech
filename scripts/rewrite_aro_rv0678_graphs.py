#!/usr/bin/env python3
"""Add descriptions and inherited evidence to Rv0678 efflux-regulator graphs.

The existing Rv0678 family graphs were intentionally conservative: CARD states
that Rv0678 negatively regulates expression of the mmpS5/L5 efflux pump, but
the broad family term does not say that resistant mutants relieve that
repression. This updater preserves that shape, keeps the named pump-expression
node local, and fills the graph-evidence quality gaps.

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

HISTORY_ACTION = "Improved Rv0678 efflux-regulator graph evidence"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

PARENT_IDENTIFIER = "ARO:3007672"

PARENT_EVIDENCE = {
    "reference": PARENT_IDENTIFIER,
    "snippet": (
        "Rv0678 encodes a transcription factor which negatively regulates "
        "the expression of the mmpS5/L5 efflux pump."
    ),
    "notes": "CARD definition for the antibiotic resistant Rv0678 parent term.",
}

PARENT_ARO_CITATION = {
    "reference": "DOI:10.1038/s41598-023-35563-0",
    "notes": "PMID:37280265 (aro citation)",
}

MUTATION_MECHANISM_EVIDENCE = {
    "reference": "ARO:3000212",
    "snippet": (
        "Point mutations in the DNA may lead to an altered gene product that "
        "may result in antibiotic resistance. Examples included modified "
        "antibiotic targets with lower binding affinities and the deactivation "
        "of repressors that result in increased expression of genes that "
        "inactivate or pump out antibiotics."
    ),
    "notes": (
        "CARD definition for the broad mutation-conferring resistance mechanism; "
        "the Rv0678 family is an efflux-pump repressor branch of this mechanism."
    ),
}

DRUG_CLASS_EVIDENCE = {
    "ARO:3004491": {
        "reference": "ARO:3004491",
        "snippet": "diarylquinoline antibiotic",
        "notes": "ARO drug-class term inherited by bedaquiline-resistant Rv0678 records.",
    },
    "ARO:0000001": {
        "reference": "ARO:0000001",
        "snippet": "fluoroquinolone antibiotic",
        "notes": "ARO drug-class term inherited by clofazimine-resistant Rv0678 records.",
    },
}

PUMP_EXPRESSION_NODE = {
    "node_id": "pump_expression",
    "label": "expression of the mmpS5/L5 efflux pump",
    "node_type": "BIOLOGICAL_PROCESS",
    "description": (
        "Local process for expression of the named MmpS5/L5 efflux pump that "
        "Rv0678 represses; no GO term specifies this pump set."
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
    ("determinant", "RO:0002212", "pump_expression"),
}

DRUG_EDGE_KEY = ("determinant", "ARO:2000001", "drug0")

EDGE_DESCRIPTIONS = {
    ("determinant", "RO:0000056", "mech0"): (
        "ARO classifies resistant Rv0678 variants under mutation conferring "
        "antibiotic resistance."
    ),
    ("mech0", "RO:0002411", "resistance"): (
        "ARO:3000212 covers resistant mutations in repressors that can increase "
        "expression of antibiotic efflux genes."
    ),
    ("determinant", "RO:0002411", "resistance"): (
        "The Rv0678 branch represents resistant mutations in the transcription "
        "factor that represses the mmpS5/L5 efflux pump."
    ),
    ("determinant", "ARO:2000001", "drug0"): (
        "ARO maps this Rv0678 branch to the inherited drug class."
    ),
    ("determinant", "RO:0002212", "pump_expression"): (
        "The wild-type Rv0678 transcription factor negatively regulates "
        "expression of the MmpS5/L5 efflux pump."
    ),
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    drug_ancestor: str | None = None

    @property
    def has_drug(self) -> bool:
        return self.drug_ancestor is not None


TARGETS = {
    "ARO:3007672": Target(
        identifier="ARO:3007672",
        filename="antibiotic-resistant-rv0678-aro3007672.yaml",
    ),
    "ARO:3007673": Target(
        identifier="ARO:3007673",
        filename="bedaquiline-resistant-rv0678-aro3007673.yaml",
        drug_ancestor="ARO:3007673",
    ),
    "ARO:3007674": Target(
        identifier="ARO:3007674",
        filename=(
            "mycobacterium-tuberculosis-rv0678-with-mutation-conferring-"
            "resistance-to-bedaqui-aro3007674.yaml"
        ),
        drug_ancestor="ARO:3007673",
    ),
    "ARO:3007853": Target(
        identifier="ARO:3007853",
        filename="clofazimine-resistant-rv0678-aro3007853.yaml",
        drug_ancestor="ARO:3007853",
    ),
    "ARO:3007852": Target(
        identifier="ARO:3007852",
        filename=(
            "mycobacterium-tuberculosis-rv0678-with-mutation-conferring-"
            "resistance-to-clofazi-aro3007852.yaml"
        ),
        drug_ancestor="ARO:3007853",
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


def _drug_relation_evidence(graph: dict[str, Any], target: Target) -> dict[str, str]:
    drug0 = next(
        node
        for node in _dicts(graph.get("nodes"))
        if node.get("node_id") == "drug0"
    )
    grounding = str(drug0["grounding"])
    return {
        "reference": str(target.drug_ancestor),
        "snippet": (
            "relationship: confers_resistance_to_drug_class "
            f"{grounding} ! {drug0['label']}"
        ),
        "notes": (
            f"ARO drug-class relationship asserted on {target.drug_ancestor} "
            f"and inherited by {target.identifier}."
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
    expected_nodes = {"determinant", "mech0", "pump_expression", "resistance"}
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
            copy.deepcopy(PUMP_EXPRESSION_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ]
    )
    return out


def _canonical_edges(
    record: dict[str, Any],
    graph: dict[str, Any],
    target: Target,
) -> list[dict[str, Any]]:
    source_evidence = _source_evidence(record)
    definition_evidence = _own_definition_evidence(record)
    mechanism_evidence = (
        PARENT_EVIDENCE,
        MUTATION_MECHANISM_EVIDENCE,
        PARENT_ARO_CITATION,
        *source_evidence,
    )
    resistance_evidence = (
        definition_evidence,
        PARENT_EVIDENCE,
        MUTATION_MECHANISM_EVIDENCE,
        PARENT_ARO_CITATION,
        *source_evidence,
    )
    repression_evidence = (
        PARENT_EVIDENCE,
        PARENT_ARO_CITATION,
        *source_evidence,
    )

    edges = [
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
    ]

    if target.has_drug:
        drug0 = _nodes_by_id(graph)["drug0"]
        drug_grounding = str(drug0["grounding"])
        edges.append(
            _edge(
                "determinant",
                "confers resistance to",
                "ARO:2000001",
                "drug0",
                (
                    definition_evidence,
                    _drug_relation_evidence(graph, target),
                    DRUG_CLASS_EVIDENCE[drug_grounding],
                    *source_evidence,
                ),
            )
        )

    edges.append(
        _edge(
            "determinant",
            "negatively regulates (represses pump expression)",
            "RO:0002212",
            "pump_expression",
            repression_evidence,
        )
    )
    return edges


def _canonical_graph(record: dict[str, Any], target: Target) -> dict[str, Any]:
    graph = record["causal_graphs"][0]
    _validate_graph(graph, target)
    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → Rv0678 mmpS5/L5 repression → antibiotic resistance",
        "description": (
            "Conservative graph for Rv0678-mediated resistance. Rv0678 is modeled "
            "as a negative regulator of MmpS5/L5 efflux-pump expression; the graph "
            "does not assert a derepression edge where CARD only states the "
            "wild-type repression."
        ),
        "nodes": _canonical_nodes(graph, target),
        "edges": _canonical_edges(record, graph, target),
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
        raise ValueError(f"not an Rv0678 target: {path}")

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
