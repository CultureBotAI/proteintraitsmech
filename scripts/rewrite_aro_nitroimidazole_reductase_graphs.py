#!/usr/bin/env python3
"""Ground and simplify nitroimidazole reductase causal graphs.

The Nim graphs model a local reduction activity plus two ungrounded chemical
substructure nodes: the nitro group and its amino-group product. This updater
grounds the reduction step to the nearest stable GO molecular-function parent
and folds the chemistry-specific nitro-to-amine detail into one described local
inactive-drug STATE, avoiding ungrounded functional-group nodes.

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
HISTORY_ACTION = "Grounded nitroimidazole reductase graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

PARENT_IDENTIFIER = "ARO:3007103"

PARENT_EVIDENCE = {
    "reference": PARENT_IDENTIFIER,
    "snippet": (
        "Nitroimidazole reductases are a group of enzymes that deactivate "
        "nitroimidazole antibiotics by reducing their nitro functional group "
        "to an amino group."
    ),
    "notes": "CARD definition for the nitroimidazole reductase parent term.",
}

ANTIBIOTIC_INACTIVATION_EVIDENCE = {
    "reference": "ARO:0001004",
    "snippet": "Enzymatic inactivation of antibiotic to confer drug resistance.",
    "notes": "CARD definition for the antibiotic inactivation mechanism.",
}

INACTIVATION_ENZYME_EVIDENCE = {
    "reference": "ARO:3000557",
    "snippet": (
        "Enzyme that catalyzes the inactivation of an antibiotic resulting in "
        "resistance. Inactivation includes chemical modification, destruction, etc."
    ),
    "notes": "CARD definition for antibiotic inactivation enzymes.",
}

DRUG_RELATION_EVIDENCE = {
    "reference": PARENT_IDENTIFIER,
    "snippet": (
        "relationship: confers_resistance_to_drug_class ARO:3004115 ! "
        "nitroimidazole antibiotic"
    ),
    "notes": (
        "ARO drug-class relationship asserted on the nitroimidazole reductase "
        "parent and inherited by Nim child records."
    ),
}

NITROIMIDAZOLE_EVIDENCE = {
    "reference": "ARO:3004115",
    "snippet": "nitroimidazole antibiotic",
    "notes": "ARO drug-class term targeted by nitroimidazole reductases.",
}

OXIDOREDUCTASE_EVIDENCE = {
    "reference": "GO:0016491",
    "snippet": (
        "Catalysis of an oxidation-reduction (redox) reaction, a reversible "
        "chemical reaction in which the oxidation state of an atom or atoms "
        "within a molecule is altered."
    ),
    "notes": (
        "GO oxidoreductase activity is the nearest stable superclass for "
        "nitroimidazole nitro-group reduction."
    ),
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "antibiotic inactivation",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:0001004",
}

DRUG_NODE = {
    "node_id": "drug0",
    "label": "nitroimidazole antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:3004115",
}

REDUCTION_NODE = {
    "node_id": "reduction",
    "label": "nitroimidazole nitro-group reduction",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "GO:0016491",
    "description": (
        "Local nitroimidazole-specific reduction activity, grounded to "
        "oxidoreductase activity as the nearest stable GO molecular-function "
        "superclass."
    ),
}

INACTIVE_NODE = {
    "node_id": "inactive",
    "label": "inactive nitroimidazole amine product",
    "node_type": "STATE",
    "description": (
        "Local state for nitroimidazole antibiotics after enzymatic reduction "
        "of the nitro functional group to an amino group."
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
}

OLD_REDUCTION_EDGE_KEYS = {
    ("determinant", "RO:0002327", "reduction"),
    ("nitro", "BFO:0000050", "drug0"),
    ("reduction", "RO:0002233", "nitro"),
    ("reduction", "RO:0002234", "amine"),
}

NEW_REDUCTION_EDGE_KEYS = {
    ("determinant", "RO:0002327", "reduction"),
    ("reduction", "RO:0002233", "drug0"),
    ("reduction", "RO:0002411", "inactive"),
    ("inactive", "RO:0002411", "resistance"),
}

EXPECTED_EDGE_KEYS = CORE_EDGE_KEYS | NEW_REDUCTION_EDGE_KEYS
INPUT_EDGE_KEYS = CORE_EDGE_KEYS | OLD_REDUCTION_EDGE_KEYS | NEW_REDUCTION_EDGE_KEYS


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str

    @property
    def is_parent(self) -> bool:
        return self.identifier == PARENT_IDENTIFIER


TARGETS = {
    "ARO:3007103": Target(
        identifier="ARO:3007103",
        filename="nitroimidazole-reductase-aro3007103.yaml",
    ),
    "ARO:3007104": Target(identifier="ARO:3007104", filename="nima-aro3007104.yaml"),
    "ARO:3004655": Target(identifier="ARO:3004655", filename="nimb-aro3004655.yaml"),
    "ARO:3007105": Target(identifier="ARO:3007105", filename="nimc-aro3007105.yaml"),
    "ARO:3007106": Target(identifier="ARO:3007106", filename="nimd-aro3007106.yaml"),
    "ARO:3007107": Target(identifier="ARO:3007107", filename="nime-aro3007107.yaml"),
    "ARO:3007108": Target(identifier="ARO:3007108", filename="nimf-aro3007108.yaml"),
    "ARO:3007109": Target(identifier="ARO:3007109", filename="nimg-aro3007109.yaml"),
    "ARO:3007110": Target(identifier="ARO:3007110", filename="nimh-aro3007110.yaml"),
    "ARO:3007111": Target(identifier="ARO:3007111", filename="nimi-aro3007111.yaml"),
    "ARO:3007112": Target(identifier="ARO:3007112", filename="nimj-aro3007112.yaml"),
    "ARO:3007113": Target(identifier="ARO:3007113", filename="nimk-aro3007113.yaml"),
    "ARO:3007671": Target(
        identifier="ARO:3007671",
        filename="clostridioides-difficile-nimb-aro3007671.yaml",
    ),
}

EDGE_DESCRIPTIONS = {
    ("determinant", "RO:0000056", "mech0"): (
        "ARO classifies nitroimidazole reductases under antibiotic inactivation."
    ),
    ("mech0", "RO:0002411", "resistance"): (
        "Nitroimidazole reductase-mediated drug inactivation is the broad "
        "mechanism leading to resistance."
    ),
    ("determinant", "RO:0002411", "resistance"): (
        "Nitroimidazole reductases deactivate nitroimidazole antibiotics by "
        "reducing the drug nitro group to an amine."
    ),
    ("determinant", "ARO:2000001", "drug0"): (
        "ARO maps the nitroimidazole reductase family to nitroimidazole "
        "antibiotics."
    ),
    ("determinant", "RO:0002327", "reduction"): (
        "The determinant enables nitroimidazole nitro-group reduction."
    ),
    ("reduction", "RO:0002233", "drug0"): (
        "The nitroimidazole antibiotic is the input to the nitro-group "
        "reduction step."
    ),
    ("reduction", "RO:0002411", "inactive"): (
        "The reaction reduces the drug nitro functional group to an amino "
        "group."
    ),
    ("inactive", "RO:0002411", "resistance"): (
        "Reduction to the inactive amine-containing product is the modeled "
        "terminal inactivation event."
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


def _target_evidence(record: dict[str, Any], target: Target) -> dict[str, str]:
    if target.is_parent:
        return PARENT_EVIDENCE
    return {
        "reference": str(record["identifier"]),
        "snippet": str(record["definition"]),
        "notes": f"CARD definition for {record['label']}.",
    }


def _source_evidence(record: dict[str, Any]) -> tuple[dict[str, str], ...]:
    return tuple(
        {
            "reference": str(item["reference"]),
            "notes": str(item.get("notes") or "ARO citation for this record."),
        }
        for item in record.get("evidence") or []
        if isinstance(item, dict) and item.get("reference")
    )


def _nim_evidence(record: dict[str, Any], target: Target) -> tuple[dict[str, str], ...]:
    target_evidence = _target_evidence(record, target)
    if target.is_parent:
        return (target_evidence,)
    return (target_evidence, PARENT_EVIDENCE)


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
    evidence: tuple[dict[str, str], ...],
) -> dict[str, Any]:
    return _ordered_edge(
        {
            "subject": subject,
            "predicate": predicate,
            "predicate_id": predicate_id,
            "object": object_,
            "description": EDGE_DESCRIPTIONS[(subject, predicate_id, object_)],
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
    missing_nodes = sorted({"determinant", "mech0", "drug0", "reduction", "resistance"} - set(nodes))
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")

    found_edges = set()
    seen: set[tuple[str, str, str]] = set()
    for edge in graph.get("edges") or []:
        key = _edge_key(edge)
        if key not in INPUT_EDGE_KEYS:
            raise ValueError(f"{target.identifier}: unexpected edge {key[0]} -> {key[2]}")
        if key in seen:
            raise ValueError(f"{target.identifier}: duplicate edge {key[0]} -> {key[2]}")
        seen.add(key)
        found_edges.add(key)

    missing_core = sorted(CORE_EDGE_KEYS - found_edges)
    if missing_core:
        missing = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in missing_core)
        raise ValueError(f"{target.identifier}: missing core edge(s): {missing}")

    has_old_reduction_path = OLD_REDUCTION_EDGE_KEYS <= found_edges
    has_new_reduction_path = NEW_REDUCTION_EDGE_KEYS <= found_edges
    if not has_old_reduction_path and not has_new_reduction_path:
        raise ValueError(f"{target.identifier}: missing nitroimidazole reduction path")


def _canonical_nodes(graph: dict[str, Any]) -> list[dict[str, Any]]:
    nodes = _nodes_by_id(graph)
    return [
        copy.deepcopy(nodes["determinant"]),
        copy.deepcopy(MECHANISM_NODE),
        copy.deepcopy(DRUG_NODE),
        copy.deepcopy(REDUCTION_NODE),
        copy.deepcopy(INACTIVE_NODE),
        copy.deepcopy(RESISTANCE_NODE),
    ]


def _canonical_edges(record: dict[str, Any], target: Target) -> list[dict[str, Any]]:
    source_evidence = _source_evidence(record)
    nim_evidence = _nim_evidence(record, target)
    broad_evidence = (
        *nim_evidence,
        ANTIBIOTIC_INACTIVATION_EVIDENCE,
        INACTIVATION_ENZYME_EVIDENCE,
        *source_evidence,
    )
    reduction_evidence = (
        *nim_evidence,
        OXIDOREDUCTASE_EVIDENCE,
        *source_evidence,
    )
    drug_evidence = (
        *nim_evidence,
        DRUG_RELATION_EVIDENCE,
        NITROIMIDAZOLE_EVIDENCE,
        *source_evidence,
    )

    return [
        _edge(
            "determinant",
            "participates in (resistance mechanism)",
            "RO:0000056",
            "mech0",
            broad_evidence,
        ),
        _edge(
            "mech0",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            broad_evidence,
        ),
        _edge(
            "determinant",
            "causally upstream of (confers resistance)",
            "RO:0002411",
            "resistance",
            broad_evidence,
        ),
        _edge(
            "determinant",
            "confers resistance to",
            "ARO:2000001",
            "drug0",
            drug_evidence,
        ),
        _edge(
            "determinant",
            "enables",
            "RO:0002327",
            "reduction",
            reduction_evidence,
        ),
        _edge(
            "reduction",
            "has input",
            "RO:0002233",
            "drug0",
            reduction_evidence,
        ),
        _edge(
            "reduction",
            "causally upstream of (inactivates the drug)",
            "RO:0002411",
            "inactive",
            reduction_evidence,
        ),
        _edge(
            "inactive",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            broad_evidence,
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
    graph["title"] = f"{record['label']} → nitroimidazole reduction → antibiotic resistance"
    graph["description"] = (
        "Conservative graph for nitroimidazole reductase-mediated antibiotic "
        "inactivation. The graph grounds the local nitro-group reduction step "
        "to GO:0016491 oxidoreductase activity and represents reduction of "
        "the drug nitro functional group to an amino group as one local "
        "inactive-drug state."
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
        raise ValueError(f"{path}: not a nitroimidazole reductase target: {identifier}")
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
        help="ARO directory or one exact nitroimidazole reductase YAML file",
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
