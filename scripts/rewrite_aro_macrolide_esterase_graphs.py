#!/usr/bin/env python3
"""Ground and simplify macrolide esterase causal graphs.

The Ere/EstT graphs already contain ARO:3000321 for hydrolysis of the macrolide
macrocycle lactone ring. This updater routes hydrolysis directly through that
grounded mechanism and removes the duplicate ungrounded esterase node plus the
local macrolactone-ring state.

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
HISTORY_ACTION = "Grounded macrolide esterase graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

PARENT_IDENTIFIER = "ARO:3000320"

PARENT_EVIDENCE = {
    "reference": PARENT_IDENTIFIER,
    "snippet": (
        "Hydrolytic enzymes that cleave the macrocycle lactone ring of "
        "macrolide antibiotics."
    ),
    "notes": "CARD definition for the macrolide esterase parent term.",
}

ANTIBIOTIC_INACTIVATION_EVIDENCE = {
    "reference": "ARO:0001004",
    "snippet": "Enzymatic inactivation of antibiotic to confer drug resistance.",
    "notes": "CARD definition for the antibiotic inactivation mechanism.",
}

MACROLACTONE_HYDROLYSIS_EVIDENCE = {
    "reference": "ARO:3000321",
    "snippet": "Hydrolysis of the the macrocycle lactone ring of macrolide antibiotics.",
    "notes": "CARD definition for hydrolysis of macrolide macrocycle lactone ring.",
}

MORAR_EVIDENCE = {
    "reference": "PMID:22303981",
    "snippet": (
        "One mechanism of macrolide resistance is via drug inactivation: "
        "enzymatic hydrolysis of the macrolactone ring catalyzed by "
        "erythromycin esterases, EreA and EreB."
    ),
    "notes": "Morar et al. 2012; erythromycin esterases hydrolyze the macrolactone ring.",
}

DRUG_RELATION_EVIDENCE = {
    "reference": PARENT_IDENTIFIER,
    "snippet": (
        "relationship: confers_resistance_to_drug_class ARO:0000000 ! "
        "macrolide antibiotic"
    ),
    "notes": (
        "ARO drug-class relationship asserted on the macrolide esterase parent "
        "and inherited by Ere/EstT child records."
    ),
}

MACROLIDE_EVIDENCE = {
    "reference": "ARO:0000000",
    "snippet": "macrolide antibiotic",
    "notes": "ARO drug-class term targeted by macrolide esterases.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "antibiotic inactivation",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:0001004",
}

MACROLACTONE_HYDROLYSIS_NODE = {
    "node_id": "mech1",
    "label": "hydrolysis of macrolide macrocycle lactone ring",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3000321",
}

MACROLIDE_NODE = {
    "node_id": "drug0",
    "label": "macrolide antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:0000000",
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
    ("determinant", "RO:0000056", "mech1"),
    ("mech1", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("determinant", "ARO:2000001", "drug0"),
}

OLD_ESTERASE_EDGE_KEYS = {
    ("determinant", "RO:0002327", "esterase"),
    ("esterase", "RO:0002212", "ring"),
    ("ring", "BFO:0000050", "drug0"),
}

NEW_HYDROLYSIS_EDGE_KEYS = {
    ("mech1", "RO:0002233", "drug0"),
}

EXPECTED_EDGE_KEYS = CORE_EDGE_KEYS | NEW_HYDROLYSIS_EDGE_KEYS
INPUT_EDGE_KEYS = CORE_EDGE_KEYS | OLD_ESTERASE_EDGE_KEYS | NEW_HYDROLYSIS_EDGE_KEYS


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str

    @property
    def is_parent(self) -> bool:
        return self.identifier == PARENT_IDENTIFIER


TARGETS = {
    PARENT_IDENTIFIER: Target(
        identifier=PARENT_IDENTIFIER,
        filename="macrolide-esterase-aro3000320.yaml",
    ),
    "ARO:3000361": Target(identifier="ARO:3000361", filename="erea-aro3000361.yaml"),
    "ARO:3002826": Target(identifier="ARO:3002826", filename="erea2-aro3002826.yaml"),
    "ARO:3000363": Target(identifier="ARO:3000363", filename="ereb-aro3000363.yaml"),
    "ARO:3004608": Target(identifier="ARO:3004608", filename="ered-aro3004608.yaml"),
    "ARO:3007459": Target(identifier="ARO:3007459", filename="estt-aro3007459.yaml"),
}

EDGE_DESCRIPTIONS = {
    ("determinant", "RO:0000056", "mech0"): (
        "ARO classifies macrolide esterases under antibiotic inactivation."
    ),
    ("mech0", "RO:0002411", "resistance"): (
        "Antibiotic inactivation is the broad resistance mechanism reached by "
        "macrolactone-ring hydrolysis."
    ),
    ("determinant", "RO:0000056", "mech1"): (
        "ARO classifies macrolide esterases under hydrolysis of the macrolide "
        "macrocycle lactone ring."
    ),
    ("mech1", "RO:0002411", "resistance"): (
        "Hydrolysis of the macrolactone ring inactivates macrolide antibiotics."
    ),
    ("determinant", "RO:0002411", "resistance"): (
        "Macrolide esterases confer resistance by cleaving the macrocycle "
        "lactone ring of macrolide antibiotics."
    ),
    ("determinant", "ARO:2000001", "drug0"): (
        "ARO maps the macrolide esterase family to macrolide antibiotics."
    ),
    ("mech1", "RO:0002233", "drug0"): (
        "The macrolide antibiotic is the input to macrolactone-ring hydrolysis."
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


def _esterase_evidence(record: dict[str, Any], target: Target) -> tuple[dict[str, str], ...]:
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
    missing_nodes = sorted({"determinant", "mech0", "mech1", "drug0", "resistance"} - set(nodes))
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

    has_old_esterase_path = OLD_ESTERASE_EDGE_KEYS <= found_edges
    has_new_hydrolysis_input = NEW_HYDROLYSIS_EDGE_KEYS <= found_edges
    if not has_old_esterase_path and not has_new_hydrolysis_input:
        raise ValueError(f"{target.identifier}: missing macrolactone hydrolysis path")


def _canonical_nodes(graph: dict[str, Any]) -> list[dict[str, Any]]:
    nodes = _nodes_by_id(graph)
    return [
        copy.deepcopy(nodes["determinant"]),
        copy.deepcopy(MECHANISM_NODE),
        copy.deepcopy(MACROLACTONE_HYDROLYSIS_NODE),
        copy.deepcopy(MACROLIDE_NODE),
        copy.deepcopy(RESISTANCE_NODE),
    ]


def _canonical_edges(record: dict[str, Any], target: Target) -> list[dict[str, Any]]:
    source_evidence = _source_evidence(record)
    esterase_evidence = _esterase_evidence(record, target)
    broad_evidence = (
        *esterase_evidence,
        ANTIBIOTIC_INACTIVATION_EVIDENCE,
        MACROLACTONE_HYDROLYSIS_EVIDENCE,
        MORAR_EVIDENCE,
        *source_evidence,
    )
    hydrolysis_evidence = (
        *esterase_evidence,
        MACROLACTONE_HYDROLYSIS_EVIDENCE,
        MORAR_EVIDENCE,
        *source_evidence,
    )
    drug_evidence = (
        *esterase_evidence,
        DRUG_RELATION_EVIDENCE,
        MACROLIDE_EVIDENCE,
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
            "participates in (resistance mechanism)",
            "RO:0000056",
            "mech1",
            hydrolysis_evidence,
        ),
        _edge(
            "mech1",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            hydrolysis_evidence,
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
            "mech1",
            "has input",
            "RO:0002233",
            "drug0",
            hydrolysis_evidence,
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
    graph["title"] = f"{record['label']} → macrolide ring hydrolysis → antibiotic resistance"
    graph["description"] = (
        "Conservative graph for macrolide esterase-mediated antibiotic "
        "inactivation. The graph removes duplicate local esterase and "
        "macrolactone-ring nodes, routes the reaction through ARO:3000321 "
        "hydrolysis of macrolide macrocycle lactone ring, and treats the "
        "macrolide antibiotic as that hydrolysis reaction's input."
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
        raise ValueError(f"{path}: not a macrolide esterase target: {identifier}")
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
        help="ARO directory or one exact macrolide esterase YAML file",
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
