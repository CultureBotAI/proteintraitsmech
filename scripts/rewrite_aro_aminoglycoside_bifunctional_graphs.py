#!/usr/bin/env python3
"""Ground aminoglycoside bifunctional resistance-protein graphs.

The ARO aminoglycoside bifunctional branch intentionally should not pick one
exact acetylation, phosphorylation, or nucleotidylation reaction: these records
only claim broad aminoglycoside inactivation by chemical modification. The
current graphs nevertheless carry an extra ungrounded molecular-function node
named ``modification``.

This updater rewrites the exact five-record bifunctional branch to use the
grounded ARO antibiotic-inactivation activity as the modification step, keeps
the aminoglycoside drug-class edge from the branch parent, and retains only the
local inactivated-drug state.

Dry-run by default; pass ``--apply`` to write.
"""

from __future__ import annotations

import argparse
import copy
import re
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
HISTORY_ACTION = "Grounded aminoglycoside bifunctional resistance graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

ANTIBIOTIC_INACTIVATION_EVIDENCE = {
    "reference": "ARO:0001004",
    "snippet": "Enzymatic inactivation of antibiotic to confer drug resistance.",
    "notes": "CARD definition for the antibiotic inactivation mechanism.",
}

AMINOGLYCOSIDE_MODIFYING_EVIDENCE = {
    "reference": "ARO:3007380",
    "snippet": (
        "Resistance-conferring genetic elements encoding proteins involved in "
        "the enzymatic inactivation of aminoglycoside antibiotics through "
        "chemical modification."
    ),
    "notes": "CARD definition for aminoglycoside-modifying enzymes.",
}

BIFUNCTIONAL_PARENT_EVIDENCE = {
    "reference": "ARO:3007419",
    "snippet": (
        "Bifunctional aminoglycoside-inactivating enzymes composed of two "
        "separate functional domains. These proteins possess activity from both "
        "enzyme components, thereby conferring resistance to the combination of "
        "antibiotics from both domains, and may include acetylation, "
        "phosphorylation or nucleotidylation activity."
    ),
    "notes": "CARD definition for aminoglycoside bifunctional resistance proteins.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "antibiotic inactivation",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:0001004",
}

DRUG_NODE = {
    "node_id": "drug0",
    "label": "aminoglycoside antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:0000016",
}

INACTIVATED_NODE = {
    "node_id": "inactivated",
    "label": "chemically modified, inactive aminoglycoside antibiotic",
    "node_type": "STATE",
    "description": (
        "Local state representing the aminoglycoside antibiotic after broad "
        "enzymatic inactivation by a bifunctional resistance protein."
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

DRUG_RELATION_REFERENCE = "ARO:3007419"
DRUG_RELATION_OBJECT = "ARO:0000016"
DRUG_RELATION_LABEL = "aminoglycoside antibiotic"

REQUIRED_CORE_EDGE_KEYS = {
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("determinant", "ARO:2000001", "drug0"),
}

LEGACY_MODIFICATION_EDGE_KEYS = {
    ("determinant", "RO:0002327", "modification"),
    ("modification", "RO:0002233", "drug0"),
    ("modification", "RO:0002411", "inactivated"),
}

INACTIVATION_EDGE_KEYS = {
    ("mech0", "RO:0002233", "drug0"),
    ("mech0", "RO:0002411", "inactivated"),
    ("inactivated", "RO:0002411", "resistance"),
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str


TARGETS = {
    "ARO:3007419": Target(
        identifier="ARO:3007419",
        filename="aminoglycoside-bifunctional-resistance-protein-aro3007419.yaml",
    ),
    "ARO:3002597": Target(
        identifier="ARO:3002597",
        filename="aac-6-ie-aph-2-ia-bifunctional-protein-aro3002597.yaml",
    ),
    "ARO:3002598": Target(
        identifier="ARO:3002598",
        filename="ant-3-ii-aac-6-iid-bifunctional-protein-aro3002598.yaml",
    ),
    "ARO:3002599": Target(
        identifier="ARO:3002599",
        filename="aac-6-30-aac-6-ib-bifunctional-protein-aro3002599.yaml",
    ),
    "ARO:3002600": Target(
        identifier="ARO:3002600",
        filename="aac-3-ib-aac-6-ib3-bifunctional-protein-aro3002600.yaml",
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


def _target_evidence(record: dict[str, Any]) -> dict[str, str]:
    return {
        "reference": str(record["identifier"]),
        "snippet": str(record["definition"]),
        "notes": f"CARD definition for {record['label']}.",
    }


def _branch_evidence(record: dict[str, Any]) -> tuple[dict[str, str], ...]:
    if record["identifier"] == BIFUNCTIONAL_PARENT_EVIDENCE["reference"]:
        return (_target_evidence(record), AMINOGLYCOSIDE_MODIFYING_EVIDENCE)
    return (
        _target_evidence(record),
        BIFUNCTIONAL_PARENT_EVIDENCE,
        AMINOGLYCOSIDE_MODIFYING_EVIDENCE,
    )


def _drug_evidence() -> dict[str, str]:
    return {
        "reference": DRUG_RELATION_REFERENCE,
        "snippet": f"confers_resistance_to_drug_class {DRUG_RELATION_OBJECT} ! {DRUG_RELATION_LABEL}",
        "notes": (
            "ARO drug-class relationship on ARO:3007419; modeled here as a "
            "determinant-to-aminoglycoside-antibiotic edge and inherited by "
            "the bifunctional leaf records."
        ),
    }


def _unique_evidence(evidence: tuple[dict[str, str], ...]) -> list[dict[str, str]]:
    unique: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for item in evidence:
        key = (
            item["reference"],
            item["snippet"],
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


def _canonical_edge_keys() -> set[tuple[str, str, str]]:
    return REQUIRED_CORE_EDGE_KEYS | INACTIVATION_EDGE_KEYS


def _input_allowed_edges() -> set[tuple[str, str, str]]:
    return _canonical_edge_keys() | LEGACY_MODIFICATION_EDGE_KEYS


def _validate_inactivation_edges(
    found: set[tuple[str, str, str]],
    target: Target,
) -> None:
    has_legacy = LEGACY_MODIFICATION_EDGE_KEYS <= found
    has_canonical = INACTIVATION_EDGE_KEYS <= found
    if not has_legacy and not has_canonical:
        raise ValueError(
            f"{target.identifier}: missing both canonical and legacy inactivation edges"
        )


def _validate_graph(graph: dict[str, Any], target: Target) -> None:
    nodes = _nodes_by_id(graph)
    required_nodes = {"determinant", "mech0", "drug0", "inactivated", "resistance"}
    if "modification" in nodes:
        required_nodes.add("modification")

    missing_nodes = sorted(required_nodes - set(nodes))
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")

    found = set()
    seen: set[tuple[str, str, str]] = set()
    for edge in graph.get("edges") or []:
        key = _edge_key(edge)
        if key not in _input_allowed_edges():
            raise ValueError(f"{target.identifier}: unexpected edge {key[0]} -> {key[2]}")
        if key in seen:
            raise ValueError(f"{target.identifier}: duplicate edge {key[0]} -> {key[2]}")
        seen.add(key)
        found.add(key)

    missing_edges = sorted(REQUIRED_CORE_EDGE_KEYS - found)
    if missing_edges:
        missing = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in missing_edges)
        raise ValueError(f"{target.identifier}: missing edge(s): {missing}")
    _validate_inactivation_edges(found, target)


def _canonical_nodes(graph: dict[str, Any]) -> list[dict[str, Any]]:
    nodes = _nodes_by_id(graph)
    return [
        copy.deepcopy(nodes["determinant"]),
        copy.deepcopy(MECHANISM_NODE),
        copy.deepcopy(DRUG_NODE),
        copy.deepcopy(INACTIVATED_NODE),
        copy.deepcopy(RESISTANCE_NODE),
    ]


def _canonical_edges(record: dict[str, Any]) -> list[dict[str, Any]]:
    branch_evidence = _branch_evidence(record)
    inactivation_evidence = branch_evidence + (ANTIBIOTIC_INACTIVATION_EVIDENCE,)
    drug_evidence = branch_evidence + (
        _drug_evidence(),
        ANTIBIOTIC_INACTIVATION_EVIDENCE,
    )

    return [
        _edge(
            "determinant",
            "participates in (resistance mechanism)",
            "RO:0000056",
            "mech0",
            "The ARO hierarchy classifies this bifunctional enzyme under antibiotic inactivation.",
            inactivation_evidence,
        ),
        _edge(
            "mech0",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            "Antibiotic inactivation is the broad mechanism produced by these bifunctional enzymes.",
            inactivation_evidence,
        ),
        _edge(
            "determinant",
            "causally upstream of (confers resistance)",
            "RO:0002411",
            "resistance",
            "ARO links these bifunctional aminoglycoside-inactivating enzymes to resistance.",
            drug_evidence,
        ),
        _edge(
            "determinant",
            "confers resistance to (drug class)",
            "ARO:2000001",
            "drug0",
            "The ARO hierarchy links this bifunctional enzyme to aminoglycoside antibiotics.",
            drug_evidence,
        ),
        _edge(
            "mech0",
            "has input (drug)",
            "RO:0002233",
            "drug0",
            "The antibiotic-inactivation activity acts on aminoglycoside antibiotics.",
            inactivation_evidence,
        ),
        _edge(
            "mech0",
            "causally upstream of (inactivates the drug)",
            "RO:0002411",
            "inactivated",
            "The broad ARO mechanism chemically modifies and inactivates the aminoglycoside.",
            inactivation_evidence,
        ),
        _edge(
            "inactivated",
            "causally upstream of (drug is inactive)",
            "RO:0002411",
            "resistance",
            "The chemically inactivated aminoglycoside is the terminal modeled cause of resistance.",
            inactivation_evidence,
        ),
    ]


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != target.identifier:
        raise ValueError(f"expected {target.identifier}, found {record.get('identifier')}")

    out = copy.deepcopy(record)
    before = copy.deepcopy(out.get("causal_graphs"))
    graphs = out.get("causal_graphs") or []
    graph = next(
        (item for item in graphs if item.get("graph_id") in {"resistance", "resistance-draft"}),
        None,
    )
    if graph is None:
        raise ValueError(f"{target.identifier}: missing resistance causal graph")

    _validate_graph(graph, target)
    graph["graph_id"] = "resistance"
    graph["title"] = f"{record['label']} → aminoglycoside inactivation → resistance"
    graph["description"] = (
        "Conservative graph for a bifunctional aminoglycoside-inactivating "
        "enzyme. The graph keeps the ARO antibiotic-inactivation and "
        "aminoglycoside drug-class routes and drops the ungrounded generic "
        "modification activity because the exact acetylation, phosphorylation, "
        "or nucleotidylation reaction is not specified by this ARO record."
    )
    graph["nodes"] = _canonical_nodes(graph)
    graph["edges"] = _canonical_edges(out)
    return out, out.get("causal_graphs") != before


def _promote_to_reviewed(text: str) -> str:
    return re.sub(r"^mapping_status:\s*SEEDED\s*$", "mapping_status: REVIEWED", text, count=1, flags=re.M)


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: record is not a mapping")
    identifier = record.get("identifier")
    target = TARGETS.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not an aminoglycoside bifunctional target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
    normalize_aliases = "&id" in text or "*id" in text
    if not changed and not normalize_aliases and record.get("mapping_status") == "REVIEWED":
        return text, False

    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    out = _promote_to_reviewed(out)
    if HISTORY_ACTION not in out:
        out = append_to_section(out, "curation_history", _dump({"curation_history": [HISTORY_EVENT]}))
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
