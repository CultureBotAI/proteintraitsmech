#!/usr/bin/env python3
"""Ground and evidence the bacA/bcrC undecaprenyl-diphosphatase graphs.

The bacA/bcrC graphs model undecaprenyl pyrophosphate recycling during cell-wall
biosynthesis. The VanJ batch already grounded this recycling step to
GO:0050380; this updater applies the same grounding here, removes the redundant
ungrounded lipid-carrier node, and adds descriptions plus inherited evidence to
all remaining edges.

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

HISTORY_ACTION = "Grounded BacA/BcrC undecaprenyl-diphosphatase graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

BAC_A_IDENTIFIER = "ARO:3002986"
BAC_A_EVIDENCE = {
    "reference": BAC_A_IDENTIFIER,
    "snippet": (
        "The bacA gene product (BacA) recycles undecaprenyl pyrophosphate "
        "during cell wall biosynthesis which confers resistance to bacitracin."
    ),
    "notes": "CARD definition for bacA.",
}

BCRC_IDENTIFIER = "ARO:3003250"
BCRC_EVIDENCE = {
    "reference": BCRC_IDENTIFIER,
    "snippet": (
        "The bcrC gene product (BcrC) is an undecaprenyl pyrophosphate "
        "phosphatase originally isolated from Bacillus subtilis. When "
        "overexpressed it can confer resistance to bacitracin."
    ),
    "notes": "CARD definition for bcrC.",
}

MECHANISM_EVIDENCE = {
    "reference": "ARO:3000213",
    "snippet": (
        "Peptidoglycan precursors ending in D-Ala-D-Lac or D-Ala-D-Ser instead "
        "of D-Ala-D-Ala conferring high level glycopeptide resistance."
    ),
    "notes": "CARD definition for the inherited cell-wall restructuring mechanism.",
}

RECYCLING_EVIDENCE = {
    "reference": "GO:0050380",
    "snippet": (
        "Catalysis of the reaction: di-trans,octa-cis-undecaprenyl diphosphate "
        "+ H2O = di-trans,octa-cis-undecaprenyl phosphate + H+ + phosphate."
    ),
    "notes": (
        "GO definition for undecaprenyl-diphosphatase activity, the hydrolysis "
        "activity used to recycle undecaprenyl diphosphate."
    ),
}

PEPTIDE_ANTIBIOTIC_EVIDENCE = {
    "reference": "ARO:3000053",
    "snippet": "peptide antibiotic",
    "notes": "ARO drug-class term inherited by bacitracin-resistant bacA/bcrC records.",
}

RECYCLING_NODE = {
    "node_id": "recycling",
    "label": "undecaprenyl-diphosphatase activity",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "GO:0050380",
    "description": (
        "Grounded to GO undecaprenyl-diphosphatase activity, the hydrolysis "
        "activity that recycles the lipid carrier named by ARO."
    ),
}

WALL_NODE = {
    "node_id": "wall",
    "label": "peptidoglycan biosynthetic process",
    "node_type": "BIOLOGICAL_PROCESS",
    "grounding": "GO:0009252",
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
    ("determinant", "RO:0002327", "recycling"),
    ("recycling", "BFO:0000050", "wall"),
}

EDGE_DESCRIPTIONS = {
    ("determinant", "RO:0000056", "mech0"): (
        "ARO places bacA and bcrC under cell-wall restructuring resistance."
    ),
    ("mech0", "RO:0002411", "resistance"): (
        "Undecaprenyl pyrophosphate recycling during cell-wall biosynthesis is "
        "modeled under the inherited cell-wall restructuring mechanism."
    ),
    ("determinant", "RO:0002411", "resistance"): (
        "ARO states that the bacA/bcrC undecaprenyl pyrophosphate recycling "
        "route confers bacitracin resistance."
    ),
    ("determinant", "ARO:2000001", "drug0"): (
        "ARO maps undecaprenyl pyrophosphate related proteins to peptide "
        "antibiotics."
    ),
    ("determinant", "RO:0002327", "recycling"): (
        "BacA recycles undecaprenyl pyrophosphate and BcrC is an "
        "undecaprenyl-pyrophosphate phosphatase."
    ),
    ("recycling", "BFO:0000050", "wall"): (
        "ARO places BacA undecaprenyl pyrophosphate recycling during cell-wall "
        "biosynthesis."
    ),
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    own_definition: dict[str, str]


TARGETS = {
    "ARO:3002986": Target(
        identifier="ARO:3002986",
        filename="baca-aro3002986.yaml",
        own_definition=BAC_A_EVIDENCE,
    ),
    "ARO:3003250": Target(
        identifier="ARO:3003250",
        filename="bcrc-aro3003250.yaml",
        own_definition=BCRC_EVIDENCE,
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


def _drug_relation_evidence(target: Target) -> dict[str, str]:
    return {
        "reference": "ARO:3003398",
        "snippet": (
            "relationship: confers_resistance_to_drug_class ARO:3000053 ! "
            "peptide antibiotic"
        ),
        "notes": (
            "ARO drug-class relationship asserted on ARO:3003398 and inherited "
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


def _validate_graph(graph: dict[str, Any], target: Target) -> None:
    nodes = _nodes_by_id(graph)
    missing_nodes = sorted({"determinant", "mech0", "drug0", "recycling", "wall"} - set(nodes))
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")

    found_edges = set()
    seen: set[tuple[str, str, str]] = set()
    for edge in _dicts(graph.get("edges")):
        key = _edge_key(edge)
        if key == ("recycling", "RO:0002233", "upp"):
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
    shared_resistance_evidence = (
        BAC_A_EVIDENCE,
        BCRC_EVIDENCE,
        MECHANISM_EVIDENCE,
        *source_evidence,
    )
    recycling_evidence = (
        BAC_A_EVIDENCE,
        BCRC_EVIDENCE,
        RECYCLING_EVIDENCE,
        *source_evidence,
    )
    wall_evidence = (
        BAC_A_EVIDENCE,
        RECYCLING_EVIDENCE,
        *source_evidence,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → undecaprenyl diphosphate recycling → resistance",
        "description": (
            "Conservative graph for bacitracin-resistant bacA/bcrC. The graph "
            "grounds the named undecaprenyl pyrophosphate "
            "recycling/dephosphorylation activity, places it in peptidoglycan "
            "biosynthesis, and omits bacitracin-to-carrier binding because "
            "ARO does not state that drug action."
        ),
        "nodes": [
            copy.deepcopy(nodes["determinant"]),
            copy.deepcopy(nodes["mech0"]),
            copy.deepcopy(nodes["drug0"]),
            copy.deepcopy(RECYCLING_NODE),
            copy.deepcopy(WALL_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                shared_resistance_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                shared_resistance_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                shared_resistance_evidence,
            ),
            _edge(
                "determinant",
                "confers resistance to",
                "ARO:2000001",
                "drug0",
                (
                    target.own_definition,
                    _drug_relation_evidence(target),
                    PEPTIDE_ANTIBIOTIC_EVIDENCE,
                    *source_evidence,
                ),
            ),
            _edge(
                "determinant",
                "enables",
                "RO:0002327",
                "recycling",
                recycling_evidence,
            ),
            _edge(
                "recycling",
                "part of (cell wall biosynthesis)",
                "BFO:0000050",
                "wall",
                wall_evidence,
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
        raise ValueError(f"not a bacA/bcrC target: {path}")

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
