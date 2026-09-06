#!/usr/bin/env python3
"""Ground and simplify streptogramin Vgb lyase graphs.

The Vgb graphs already carry ARO:3000338 for linearization of antibiotic
conferring resistance. This updater uses that grounded mechanism for the
ring-opening reaction, removes the duplicate local lyase node and ungroundable
lactone-ring substructure node, and keeps a described local state for the
linearized inactive antibiotic.

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
HISTORY_ACTION = "Grounded streptogramin Vgb lyase graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

PARENT_IDENTIFIER = "ARO:3000376"

VGB_PARENT_EVIDENCE = {
    "reference": PARENT_IDENTIFIER,
    "snippet": (
        "vgb (Virginiamycin B) lyase inactivates type B streptogramin "
        "antibiotics by linearizing the streptogramin lactone ring at the "
        "ester linkage through an elimination mechanism, thus conferring "
        "resistance to these compounds."
    ),
    "notes": "CARD definition for the streptogramin vgb lyase parent term.",
}

ANTIBIOTIC_INACTIVATION_EVIDENCE = {
    "reference": "ARO:0001004",
    "snippet": "Enzymatic inactivation of antibiotic to confer drug resistance.",
    "notes": "CARD definition for the antibiotic inactivation mechanism.",
}

STREPTOGRAMIN_INACTIVATION_EVIDENCE = {
    "reference": "ARO:3000233",
    "snippet": (
        "Resistance to streptogramin antibiotics may be conferred through "
        "enzymatic inactivation. There are two known mechanisms of "
        "streptogramin inactivation shown clinically to confer resistance: 1) "
        "vgB lyase enzymes linearize type B streptogramin antibiotics by "
        "breaking the ester linkage; 2) vat acetyltransferase enzymes modify "
        "type A streptogramin antibiotics by transferring an acetyl group from "
        "acetyl-CoA to the secondary streptogramin hydroxyl. Both mechanisms "
        "result in antibiotic inactivation thus conferring resistance."
    ),
    "notes": (
        "CARD definition for the streptogramin inactivation enzyme parent, "
        "separating Vgb type-B linearization from Vat type-A acetylation."
    ),
}

DRUG_RELATION_EVIDENCE = {
    "reference": PARENT_IDENTIFIER,
    "snippet": "relationship: confers_resistance_to_drug_class ARO:0000026 ! streptogramin antibiotic",
    "notes": (
        "ARO drug-class relationship asserted on the streptogramin vgb lyase "
        "parent and inherited by vgbA, vgbB, and vgbC."
    ),
}

STREPTOGRAMIN_EVIDENCE = {
    "reference": "ARO:0000026",
    "snippet": "streptogramin antibiotic",
    "notes": "ARO drug-class term targeted by streptogramin Vgb lyases.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "antibiotic inactivation",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:0001004",
}

LINEARIZATION_NODE = {
    "node_id": "mech1",
    "label": "linearization of antibiotic conferring resistance",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3000338",
}

DRUG_NODE = {
    "node_id": "drug0",
    "label": "streptogramin antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:0000026",
}

LINEARIZED_NODE = {
    "node_id": "linearized",
    "label": "linearized, inactive streptogramin B",
    "node_type": "STATE",
    "description": (
        "Local state for type-B streptogramin after the lactone ring is "
        "linearized at the ester linkage."
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
    ("determinant", "RO:0000056", "mech1"),
    ("mech1", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("determinant", "ARO:2000001", "drug0"),
}

OLD_LOCAL_EDGE_KEYS = {
    ("determinant", "RO:0002327", "lyase"),
    ("lactone", "BFO:0000050", "drug0"),
    ("lyase", "RO:0002233", "lactone"),
    ("lyase", "RO:0002411", "linearized"),
}

NEW_LINEARIZATION_EDGE_KEYS = {
    ("mech1", "RO:0002233", "drug0"),
    ("mech1", "RO:0002411", "linearized"),
    ("linearized", "RO:0002411", "resistance"),
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str

    @property
    def is_parent(self) -> bool:
        return self.identifier == PARENT_IDENTIFIER


TARGETS = {
    "ARO:3000376": Target(
        identifier="ARO:3000376",
        filename="streptogramin-vgb-lyase-aro3000376.yaml",
    ),
    "ARO:3001307": Target(
        identifier="ARO:3001307",
        filename="vgba-aro3001307.yaml",
    ),
    "ARO:3001308": Target(
        identifier="ARO:3001308",
        filename="vgbb-aro3001308.yaml",
    ),
    "ARO:3003990": Target(
        identifier="ARO:3003990",
        filename="vgbc-aro3003990.yaml",
    ),
}

EDGE_DESCRIPTIONS = {
    ("determinant", "RO:0000056", "mech0"): (
        "ARO classifies streptogramin Vgb lyases under antibiotic inactivation."
    ),
    ("mech0", "RO:0002411", "resistance"): (
        "Antibiotic inactivation is the broad mechanism reached by type-B "
        "streptogramin linearization."
    ),
    ("determinant", "RO:0000056", "mech1"): (
        "ARO classifies streptogramin Vgb lyases under antibiotic "
        "linearization."
    ),
    ("mech1", "RO:0002411", "resistance"): (
        "Linearization of the streptogramin B lactone ring inactivates the "
        "antibiotic and confers resistance."
    ),
    ("determinant", "RO:0002411", "resistance"): (
        "Vgb lyases confer resistance by linearizing type-B streptogramin "
        "antibiotics through an elimination mechanism."
    ),
    ("determinant", "ARO:2000001", "drug0"): (
        "ARO maps the streptogramin Vgb lyase family to streptogramin "
        "antibiotics."
    ),
    ("mech1", "RO:0002233", "drug0"): (
        "The type-B streptogramin antibiotic is the input to the linearization "
        "reaction."
    ),
    ("mech1", "RO:0002411", "linearized"): (
        "The linearization mechanism opens the lactone ring at the ester "
        "linkage."
    ),
    ("linearized", "RO:0002411", "resistance"): (
        "The linearized, inactive streptogramin B state is the modeled terminal "
        "cause of resistance."
    ),
}

EXPECTED_EDGE_KEYS = set(EDGE_DESCRIPTIONS)
INPUT_EDGE_KEYS = CORE_EDGE_KEYS | OLD_LOCAL_EDGE_KEYS | NEW_LINEARIZATION_EDGE_KEYS


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
        return VGB_PARENT_EVIDENCE
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


def _vgb_evidence(record: dict[str, Any], target: Target) -> tuple[dict[str, str], ...]:
    target_evidence = _target_evidence(record, target)
    if target.is_parent:
        return (target_evidence,)
    return (target_evidence, VGB_PARENT_EVIDENCE)


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
    missing_nodes = sorted(
        {"determinant", "mech0", "mech1", "drug0", "linearized", "resistance"} - set(nodes)
    )
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

    has_old_local_path = OLD_LOCAL_EDGE_KEYS <= found_edges
    has_new_linearization_path = NEW_LINEARIZATION_EDGE_KEYS <= found_edges
    if not has_old_local_path and not has_new_linearization_path:
        raise ValueError(f"{target.identifier}: missing Vgb linearization path")


def _canonical_nodes(graph: dict[str, Any]) -> list[dict[str, Any]]:
    nodes = _nodes_by_id(graph)
    return [
        copy.deepcopy(nodes["determinant"]),
        copy.deepcopy(MECHANISM_NODE),
        copy.deepcopy(LINEARIZATION_NODE),
        copy.deepcopy(DRUG_NODE),
        copy.deepcopy(LINEARIZED_NODE),
        copy.deepcopy(RESISTANCE_NODE),
    ]


def _canonical_edges(record: dict[str, Any], target: Target) -> list[dict[str, Any]]:
    source_evidence = _source_evidence(record)
    vgb_evidence = _vgb_evidence(record, target)
    broad_evidence = (
        *vgb_evidence,
        ANTIBIOTIC_INACTIVATION_EVIDENCE,
        STREPTOGRAMIN_INACTIVATION_EVIDENCE,
        *source_evidence,
    )
    linearization_evidence = (
        *vgb_evidence,
        STREPTOGRAMIN_INACTIVATION_EVIDENCE,
        *source_evidence,
    )
    drug_evidence = (
        *vgb_evidence,
        DRUG_RELATION_EVIDENCE,
        STREPTOGRAMIN_EVIDENCE,
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
            linearization_evidence,
        ),
        _edge(
            "mech1",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            linearization_evidence,
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
            linearization_evidence,
        ),
        _edge(
            "mech1",
            "causally upstream of (linearizes the drug)",
            "RO:0002411",
            "linearized",
            linearization_evidence,
        ),
        _edge(
            "linearized",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            linearization_evidence,
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
    graph["title"] = f"{record['label']} → streptogramin B linearization → antibiotic resistance"
    graph["description"] = (
        "Conservative graph for Vgb-mediated type-B streptogramin "
        "inactivation. The graph uses grounded ARO:3000338 linearization of "
        "antibiotic conferring resistance for the ring-opening reaction and "
        "keeps the lactone-ring ester linkage in descriptions rather than as "
        "an ungrounded substructure node."
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
        raise ValueError(f"{path}: not a streptogramin Vgb lyase target: {identifier}")
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
        help="ARO directory or one exact streptogramin Vgb lyase YAML file",
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
