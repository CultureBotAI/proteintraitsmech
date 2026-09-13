#!/usr/bin/env python3
"""Ground and evidence the FusB-type fusidic-acid target-protection graphs.

The FusB-type records model target protection by dissociating the stalled
ribosome-EF-G-GDP complex that fusidic acid forms. The previous graphs also
carried two ungroundable side details, EF-G as a generic protein and a
four-cysteine zinc-finger domain. This updater keeps the resistance branch and
removes those label-only, non-causal side nodes.

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

HISTORY_ACTION = "Grounded FusB-type fusidic-acid target-protection graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

PARENT_IDENTIFIER = "ARO:3005086"
PARENT_EVIDENCE = {
    "reference": PARENT_IDENTIFIER,
    "snippet": (
        "Fusidic acid resistance determinants through the mediation of target "
        "protection. These protein drive the dissociation of EF-G from the "
        "ribosome thus counteracting the action of Fusidic acid."
    ),
    "notes": "CARD definition for the FusB-type fusidic-acid target-protection parent.",
}

TARGET_PROTECTION_EVIDENCE = {
    "reference": "ARO:0001003",
    "snippet": (
        "Protection of antibiotic action target from antibiotic binding, which "
        "process will result in antibiotic resistance."
    ),
    "notes": "CARD definition for antibiotic target protection.",
}

COX_DISSOCIATION_EVIDENCE = {
    "reference": "PMID:22308410",
    "snippet": (
        "By binding to EF-G on the ribosome, FusB-type proteins promote the "
        "dissociation of stalled ribosome-EF-G-GDP complexes that form in the "
        "presence of FA, thereby allowing the ribosomes to resume translation."
    ),
    "notes": (
        "Cox et al. 2012; FusB-type proteins dissociate the stalled complex "
        "rather than displacing fusidic acid from EF-G."
    ),
}

FUSIDANE_EVIDENCE = {
    "reference": "ARO:3007153",
    "snippet": "fusidane antibiotic",
    "notes": "ARO drug-class term inherited by FusB-type fusidic-acid resistance records.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "antibiotic target protection",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:0001003",
}

FUSIDANE_NODE = {
    "node_id": "drug0",
    "label": "fusidane antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:3007153",
}

STALLED_COMPLEX_NODE = {
    "node_id": "stalled",
    "label": "stalled ribosome-EF-G-GDP complex",
    "node_type": "STATE",
    "description": (
        "Local state for the stalled ribosome-EF-G-GDP complex that fusidic "
        "acid forms and FusB-type target-protection proteins dissociate."
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
    ("drug0", "RO:0002411", "stalled"),
    ("determinant", "RO:0002212", "stalled"),
}

REMOVED_SIDE_EDGE_KEYS = {
    ("zinc_finger", "BFO:0000050", "determinant"),
    ("determinant", "RO:0002436", "efg"),
}

EDGE_DESCRIPTIONS = {
    ("determinant", "RO:0000056", "mech0"): (
        "ARO classifies FusB-type fusidic-acid resistance proteins under "
        "antibiotic target protection."
    ),
    ("mech0", "RO:0002411", "resistance"): (
        "The FusB-type target-protection route counteracts fusidic acid by "
        "dissociating EF-G from the ribosome."
    ),
    ("determinant", "RO:0002411", "resistance"): (
        "FusB-type determinants promote EF-G dissociation from the ribosome "
        "to counteract fusidic acid and confer resistance."
    ),
    ("determinant", "ARO:2000001", "drug0"): (
        "ARO maps FusB-type target-protection proteins to fusidane antibiotics."
    ),
    ("drug0", "RO:0002411", "stalled"): (
        "Fusidic acid forms stalled ribosome-EF-G-GDP complexes."
    ),
    ("determinant", "RO:0002212", "stalled"): (
        "FusB-type target-protection proteins promote dissociation of the "
        "stalled ribosome-EF-G-GDP complexes that form in the presence of "
        "fusidic acid."
    ),
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    own_definition: dict[str, str]

    @property
    def is_parent(self) -> bool:
        return self.identifier == PARENT_IDENTIFIER


TARGETS = {
    PARENT_IDENTIFIER: Target(
        identifier=PARENT_IDENTIFIER,
        filename="target-protecting-fusb-type-protein-conferring-resistance-to-fusidic-acid-aro3005086.yaml",
        own_definition=PARENT_EVIDENCE,
    ),
    "ARO:3003552": Target(
        identifier="ARO:3003552",
        filename="fusb-aro3003552.yaml",
        own_definition={
            "reference": "ARO:3003552",
            "snippet": (
                "FusB encodes a 2-domain zinc-binding protein that binds the "
                "ribosomal translocase EF-G, causing it to dissociate from the "
                "ribosome. This action increases the ribosomal turnover rate "
                "and confers resistance to fusidic acid. This protein is "
                "considered a FusB-type protein."
            ),
            "notes": "CARD definition for fusB.",
        },
    ),
    "ARO:3003733": Target(
        identifier="ARO:3003733",
        filename="fusc-aro3003733.yaml",
        own_definition={
            "reference": "ARO:3003733",
            "snippet": (
                "FusC is a fusidic acid resistance gene enabling ribosomal "
                "translocase EF-G dissociation from the ribosome that has "
                "been detected in Staphylococcus aureus and Staphylococcus "
                "intermedius. Its mechanism is believed to be similar to "
                "fusB due to its high level of sequence homology. It is "
                "considered a FusB-type protein."
            ),
            "notes": "CARD definition for fusC.",
        },
    ),
    "ARO:3003731": Target(
        identifier="ARO:3003731",
        filename="fusd-aro3003731.yaml",
        own_definition={
            "reference": "ARO:3003731",
            "snippet": (
                "A specific fusidic acid resistance gene conferring intrinsic "
                "resistance in the bacteria Staphylococcus saprophyticus. "
                "FusD behaves by causing dissociation of EF-G from the ribosome "
                "thus counteracting the action of Fusidic acid. It is "
                "considered a FusB-type protein."
            ),
            "notes": "CARD definition for fusD.",
        },
    ),
    "ARO:3004663": Target(
        identifier="ARO:3004663",
        filename="fusf-aro3004663.yaml",
        own_definition={
            "reference": "ARO:3004663",
            "snippet": (
                "A fusidic acid resistance determinant in Staphylococcus "
                "cohnii. This protein behaves akin to FusB as it is a "
                "FusB-type protein. It mediates dissociation of EF-G from the "
                "ribosome thus counteracting the action of Fusidic acid."
            ),
            "notes": "CARD definition for FusF.",
        },
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


def _drug_relation_evidence(target: Target) -> dict[str, str]:
    if target.is_parent:
        notes = (
            "ARO drug-class relationship asserted directly on the "
            "FusB-type fusidic-acid target-protection parent."
        )
    else:
        notes = (
            "ARO drug-class relationship asserted on ARO:3005086 and "
            f"inherited by {target.identifier}."
        )
    return {
        "reference": PARENT_IDENTIFIER,
        "snippet": (
            "relationship: confers_resistance_to_drug_class ARO:3007153 ! "
            "fusidane antibiotic"
        ),
        "notes": notes,
    }


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
    missing_nodes = sorted({"determinant", "mech0", "drug0", "stalled"} - set(nodes))
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")

    found_edges = set()
    seen: set[tuple[str, str, str]] = set()
    for edge in _dicts(graph.get("edges")):
        key = _edge_key(edge)
        if key in REMOVED_SIDE_EDGE_KEYS:
            continue
        if key not in EXPECTED_EDGE_KEYS:
            raise ValueError(f"{target.identifier}: unexpected edge {key[0]} -> {key[2]}")
        if key in seen:
            raise ValueError(f"{target.identifier}: duplicate edge {key[0]} -> {key[2]}")
        seen.add(key)
        found_edges.add(key)

    missing_edges = sorted(EXPECTED_EDGE_KEYS - found_edges)
    if missing_edges:
        missing = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in missing_edges)
        raise ValueError(f"{target.identifier}: missing edge(s): {missing}")


def _canonical_graph(record: dict[str, Any], target: Target) -> dict[str, Any]:
    graph = record["causal_graphs"][0]
    _validate_graph(graph, target)
    nodes = _nodes_by_id(graph)
    source_evidence = _source_evidence(record)
    mechanism_evidence = (
        target.own_definition,
        PARENT_EVIDENCE,
        TARGET_PROTECTION_EVIDENCE,
        *source_evidence,
    )
    resistance_evidence = (
        target.own_definition,
        PARENT_EVIDENCE,
        COX_DISSOCIATION_EVIDENCE,
        *source_evidence,
    )
    drug_evidence = (
        _drug_relation_evidence(target),
        FUSIDANE_EVIDENCE,
        PARENT_EVIDENCE,
        *source_evidence,
    )
    stalled_evidence = (
        COX_DISSOCIATION_EVIDENCE,
        PARENT_EVIDENCE,
        target.own_definition,
        *source_evidence,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → FusB-type stalled EF-G-ribosome rescue",
        "description": (
            "Conservative graph for FusB-type fusidic-acid resistance. The "
            "graph keeps the target-protection route in which fusidic acid "
            "forms stalled ribosome-EF-G-GDP complexes and FusB-type "
            "proteins promote dissociation of those stalled complexes."
        ),
        "nodes": [
            copy.deepcopy(nodes["determinant"]),
            copy.deepcopy(MECHANISM_NODE),
            copy.deepcopy(FUSIDANE_NODE),
            copy.deepcopy(STALLED_COMPLEX_NODE),
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
                "drug0",
                "causally upstream of",
                "RO:0002411",
                "stalled",
                stalled_evidence,
            ),
            _edge(
                "determinant",
                "negatively regulates",
                "RO:0002212",
                "stalled",
                stalled_evidence,
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


def enrich_text(text: str, path: Path, target: Target) -> tuple[str, bool]:
    if path.name != target.filename:
        raise ValueError(f"{target.identifier}: not the expected path: {path}")

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

    changed_count = 0
    for target in TARGETS.values():
        path = args.path / target.filename
        before = path.read_text(encoding="utf-8")
        after, changed = enrich_text(before, path, target)
        if not changed:
            continue
        changed_count += 1
        if args.apply:
            path.write_text(after, encoding="utf-8")
            print(f"  wrote {target.filename}")
        else:
            print(f"  would write {target.filename}")

    print(f"{'changed' if args.apply else 'would change'}: {changed_count}")
    if not changed_count:
        print(f"already enriched: {len(TARGETS)}")
    if not args.apply:
        print("dry run -- pass --apply to write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
