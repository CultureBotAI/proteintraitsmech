#!/usr/bin/env python3
"""Rewrite trimethoprim-resistant DFR target-replacement ARO graphs.

The DFR leaves under ARO:3001218 already carried grounded DHFR domain/fold
nodes, but their graphs were the older shallow shape where the Pfam domain
enabled the abstract target-replacement mechanism directly.  This updater keeps
those grounded domain/fold anchors and adds the missing causal bridge:

    DHFR domain -> GO:0004146 activity
    determinant -> structural difference from the sensitive target -> resistance

The ARO:3001218 parent and every current ``dfr*.yaml`` leaf share the same
trimethoprim/diaminopyrimidine drug-class relation and are handled together.

Dry-run by default; pass ``--apply`` to write.
"""

from __future__ import annotations

import argparse
import copy
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from record_io import append_to_section, replace_block  # noqa: E402
from rewrite_aro_dhfr_graphs import (  # noqa: E402
    DHFR_EVIDENCE,
    GO_DHFR_EVIDENCE,
    MECHANISM_NODE,
    RESISTANCE_NODE,
    SHARED_FUNCTION_NODE,
    STRUCTURAL_DIFFERENCE_NODE,
    TARGET_REPLACEMENT_EVIDENCE,
)

ROOT = Path(__file__).resolve().parent.parent
ARO_DIR = ROOT / "data" / "traits" / "function" / "resistance" / "aro"

PARENT_IDENTIFIER = "ARO:3001218"
PARENT_FILENAME = "trimethoprim-resistant-dihydrofolate-reductase-dfr-aro3001218.yaml"
DIAMINOPYRIMIDINE_IDENTIFIER = "ARO:3000171"

HISTORY_ACTION = "Completed trimethoprim-resistant DFR target-replacement graphs"
HISTORY_CURATOR = "codex-causal-graph-quality"
HISTORY_EVENT = {
    "timestamp": "2026-09-08T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

TRIMETHOPRIM_DFR_EVIDENCE = {
    "reference": PARENT_IDENTIFIER,
    "snippet": (
        "Alternative dihydropteroate synthase dfr present on plasmids produces "
        "alternate proteins that are less sensitive to trimethoprim from "
        "inhibiting its role in folate synthesis, thus conferring "
        "trimethoprim resistance."
    ),
    "notes": "CARD definition for trimethoprim resistant dihydrofolate reductase dfr.",
}

INTRINSIC_DFR_EVIDENCE = {
    "reference": "PMID:35562546",
    "snippet": (
        "Trimethoprim resistance in Enterobacteriaceae occurs almost exclusively "
        "through the acquisition of plasmid-associated dfr genes that encode "
        "intrinsically insensitive DHFR enzymes."
    ),
    "notes": "DFR-family mechanism evidence already used by the ARO:3001218 draft graph.",
}

DIAMINOPYRIMIDINE_EVIDENCE = {
    "reference": DIAMINOPYRIMIDINE_IDENTIFIER,
    "snippet": "diaminopyrimidine antibiotic",
    "notes": "ARO drug-class term for diaminopyrimidine antibiotics.",
}

DIAMINOPYRIMIDINE_RELATION_EVIDENCE = {
    "reference": PARENT_IDENTIFIER,
    "snippet": (
        "relationship: confers_resistance_to_drug_class ARO:3000171 ! "
        "diaminopyrimidine antibiotic"
    ),
    "notes": (
        "Diaminopyrimidine drug-class relation asserted on ARO:3001218 and "
        "inherited by its DFR child records."
    ),
}

PFAM_DHFR_EVIDENCE = {
    "reference": "Pfam:PF00186",
    "snippet": "Dihydrofolate reductase",
    "notes": "Pfam family for the DHFR domain in these KB protein-trait records.",
}

CATH_DHFR_EVIDENCE = {
    "reference": "CATH:3.40.430",
    "snippet": "Dihydrofolate Reductase, subunit A",
    "notes": "CATH DHFR fold used by these KB protein-trait records.",
}

DRUG_NODE = {
    "node_id": "drug0",
    "label": "diaminopyrimidine antibiotic",
    "node_type": "CHEMICAL",
    "grounding": DIAMINOPYRIMIDINE_IDENTIFIER,
}

DOMAIN_NODE = {
    "node_id": "domain",
    "label": "dihydrofolate reductase domain",
    "node_type": "DOMAIN",
    "grounding": "Pfam:PF00186",
    "description": "KB protein-trait record carrying the trimethoprim-resistant DHFR mechanism.",
}

FOLD_NODE = {
    "node_id": "fold",
    "label": "dihydrofolate reductase fold",
    "node_type": "DOMAIN",
    "grounding": "CATH:3.40.430",
    "description": "KB protein-trait record carrying the DHFR fold.",
}

INPUT_ALLOWED_EDGE_KEYS = {
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("determinant", "ARO:2000001", "drug0"),
    ("domain", "BFO:0000050", "determinant"),
    ("determinant", "RO:0002350", "fold"),
    ("domain", "RO:0002327", "mech0"),
    ("domain", "RO:0002327", "shared_function"),
    ("determinant", "RO:0002327", "shared_function"),
    ("determinant", "RO:0000086", "structural_difference"),
    ("structural_difference", "RO:0002212", "drug0"),
    ("structural_difference", "RO:0002411", "resistance"),
}

CORE_INPUT_EDGE_KEYS = {
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("determinant", "ARO:2000001", "drug0"),
    ("domain", "BFO:0000050", "determinant"),
    ("determinant", "RO:0002350", "fold"),
}

OUTPUT_EDGE_KEYS = {
    *CORE_INPUT_EDGE_KEYS,
    ("domain", "RO:0002327", "shared_function"),
    ("determinant", "RO:0000086", "structural_difference"),
    ("structural_difference", "RO:0002212", "drug0"),
    ("structural_difference", "RO:0002411", "resistance"),
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    is_parent: bool


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


def _unique_evidence(*items: dict[str, Any]) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for item in items:
        key = (
            str(item["reference"]),
            str(item.get("snippet", "")),
            str(item.get("notes", "")),
        )
        if key in seen:
            continue
        seen.add(key)
        evidence.append(copy.deepcopy(item))
    return evidence


def _edge(
    subject: str,
    predicate: str,
    predicate_id: str,
    object_: str,
    description: str,
    *evidence: dict[str, Any],
) -> dict[str, Any]:
    return {
        "subject": subject,
        "predicate": predicate,
        "predicate_id": predicate_id,
        "object": object_,
        "description": description,
        "evidence": _unique_evidence(*evidence),
    }


def _record_evidence(record: dict[str, Any]) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = [
        {
            "reference": str(record["identifier"]),
            "snippet": str(record["definition"]),
            "notes": f"CARD definition for {record['label']}.",
        }
    ]
    for item in _dicts(record.get("evidence")):
        if not item.get("reference"):
            continue
        entry: dict[str, Any] = {"reference": str(item["reference"])}
        if item.get("snippet"):
            entry["snippet"] = str(item["snippet"])
        if item.get("notes"):
            entry["notes"] = str(item["notes"])
        evidence.append(entry)
    return evidence


def _nodes_by_id(graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(node["node_id"]): node
        for node in _dicts(graph.get("nodes"))
        if "node_id" in node
    }


def is_leaf_target_path(path: Path) -> bool:
    return path.suffix == ".yaml" and path.name.startswith("dfr")


def target_for_record(record: dict[str, Any], path: Path) -> Target:
    identifier = record.get("identifier")
    if not isinstance(identifier, str) or not identifier:
        raise ValueError(f"{path}: missing identifier")

    if path.name == PARENT_FILENAME:
        if identifier != PARENT_IDENTIFIER:
            raise ValueError(f"{path}: expected {PARENT_IDENTIFIER}, found {identifier}")
        return Target(identifier, path.name, is_parent=True)

    if not is_leaf_target_path(path):
        raise ValueError(f"{path}: not a trimethoprim-resistant DFR target")

    if record.get("parent_traits") != [PARENT_IDENTIFIER]:
        raise ValueError(f"{path}: DFR leaf must be a direct {PARENT_IDENTIFIER} child")
    relations = _dicts(record.get("trait_relations"))
    if not any(
        item.get("object") == DIAMINOPYRIMIDINE_IDENTIFIER
        and PARENT_IDENTIFIER in str(item.get("relation_source"))
        for item in relations
    ):
        raise ValueError(f"{path}: missing inherited diaminopyrimidine relation")
    return Target(identifier, path.name, is_parent=False)


def _validate_graph(graph: dict[str, Any], target: Target) -> None:
    nodes = _nodes_by_id(graph)
    required_nodes = {"determinant", "mech0", "drug0", "domain", "fold", "resistance"}
    missing_nodes = sorted(required_nodes - set(nodes))
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")

    found: set[tuple[str, str, str]] = set()
    seen: set[tuple[str, str, str]] = set()
    for edge in _dicts(graph.get("edges")):
        key = _edge_key(edge)
        if key not in INPUT_ALLOWED_EDGE_KEYS:
            raise ValueError(f"{target.identifier}: unexpected edge {key[0]} -> {key[2]}")
        if key in seen:
            raise ValueError(f"{target.identifier}: duplicate edge {key[0]} -> {key[2]}")
        seen.add(key)
        found.add(key)

    missing_edges = sorted(CORE_INPUT_EDGE_KEYS - found)
    if missing_edges:
        missing = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in missing_edges)
        raise ValueError(f"{target.identifier}: missing edge(s): {missing}")


def _graph(record: dict[str, Any], target: Target) -> dict[str, Any]:
    record_evidence = _record_evidence(record)
    parent_relation_evidence = (
        TRIMETHOPRIM_DFR_EVIDENCE
        if target.is_parent
        else DIAMINOPYRIMIDINE_RELATION_EVIDENCE
    )
    branch_evidence = (
        *record_evidence,
        TRIMETHOPRIM_DFR_EVIDENCE,
        DHFR_EVIDENCE,
        TARGET_REPLACEMENT_EVIDENCE,
        INTRINSIC_DFR_EVIDENCE,
    )
    function_evidence = (
        *branch_evidence,
        GO_DHFR_EVIDENCE,
    )
    drug_evidence = (
        *record_evidence,
        parent_relation_evidence,
        DIAMINOPYRIMIDINE_EVIDENCE,
        INTRINSIC_DFR_EVIDENCE,
    )
    domain_evidence = (
        *record_evidence,
        PFAM_DHFR_EVIDENCE,
        GO_DHFR_EVIDENCE,
    )
    fold_evidence = (
        *record_evidence,
        CATH_DHFR_EVIDENCE,
        DHFR_EVIDENCE,
    )
    structural_evidence = (
        *branch_evidence,
        parent_relation_evidence,
        DIAMINOPYRIMIDINE_EVIDENCE,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → DHFR target replacement → trimethoprim resistance",
        "description": (
            "Curated resistance-causation graph for a "
            "trimethoprim-resistant dihydrofolate reductase. The graph "
            "preserves the DHFR domain and fold annotations, grounds "
            "dihydrofolate reductase activity to GO:0004146, and models "
            "resistance as target replacement by a DHFR enzyme that is "
            "structurally less sensitive to trimethoprim."
        ),
        "nodes": [
            {
                "node_id": "determinant",
                "label": str(record["label"]),
                "node_type": "PROTEIN",
                "grounding": str(record["identifier"]),
            },
            copy.deepcopy(MECHANISM_NODE),
            copy.deepcopy(DRUG_NODE),
            copy.deepcopy(DOMAIN_NODE),
            copy.deepcopy(FOLD_NODE),
            copy.deepcopy(SHARED_FUNCTION_NODE),
            copy.deepcopy(STRUCTURAL_DIFFERENCE_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "ARO classifies trimethoprim-resistant DFR under antibiotic target replacement.",
                *branch_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "A trimethoprim-insensitive replacement DHFR maintains folate metabolism.",
                *function_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                (
                    "The DFR determinant encodes a DHFR enzyme that is less "
                    "sensitive to trimethoprim and can replace the inhibited "
                    "drug-sensitive target."
                ),
                *structural_evidence,
            ),
            _edge(
                "determinant",
                "confers resistance to (drug class)",
                "ARO:2000001",
                "drug0",
                "ARO maps trimethoprim-resistant DFR to diaminopyrimidine antibiotics.",
                *drug_evidence,
            ),
            _edge(
                "domain",
                "part of",
                "BFO:0000050",
                "determinant",
                "The Pfam DHFR domain is modeled as part of the DFR protein determinant.",
                *domain_evidence,
            ),
            _edge(
                "determinant",
                "member of",
                "RO:0002350",
                "fold",
                "The determinant adopts a DHFR fold used by these KB protein-trait records.",
                *fold_evidence,
            ),
            _edge(
                "domain",
                "enables",
                "RO:0002327",
                "shared_function",
                "The DHFR domain enables dihydrofolate reductase activity.",
                *function_evidence,
                PFAM_DHFR_EVIDENCE,
            ),
            _edge(
                "determinant",
                "has quality (structurally unlike the sensitive target)",
                "RO:0000086",
                "structural_difference",
                (
                    "The target-replacement determinant is structurally "
                    "different from trimethoprim-sensitive DHFR."
                ),
                *structural_evidence,
            ),
            _edge(
                "structural_difference",
                "negatively regulates (less sensitive to trimethoprim)",
                "RO:0002212",
                "drug0",
                (
                    "Structural difference from trimethoprim-sensitive DHFR "
                    "reduces drug sensitivity."
                ),
                *structural_evidence,
            ),
            _edge(
                "structural_difference",
                "causally upstream of (target replacement resists inhibition)",
                "RO:0002411",
                "resistance",
                (
                    "A less trimethoprim-sensitive replacement DHFR keeps the "
                    "same folate-metabolism activity and thereby confers "
                    "resistance."
                ),
                *structural_evidence,
            ),
        ],
    }


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != target.identifier:
        raise ValueError(f"expected {target.identifier}, found {record.get('identifier')}")
    if not record.get("label"):
        raise ValueError(f"{target.identifier}: missing label")
    if not record.get("definition"):
        raise ValueError(f"{target.identifier}: missing definition")

    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1 or graphs[0].get("graph_id") != "resistance":
        raise ValueError(f"{target.identifier}: expected exactly one resistance graph")
    _validate_graph(graphs[0], target)

    out = copy.deepcopy(record)
    out["causal_graphs"] = [_graph(record, target)]
    return out, out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    target = target_for_record(record, path)
    enriched, changed = enrich_record(record, target)
    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    if HISTORY_ACTION not in out:
        out = append_to_section(out, "curation_history", _dump({"curation_history": [HISTORY_EVENT]}))
        changed = True

    if "&id" in out or "*id" in out:
        raise ValueError(f"{path}: YAML anchors leaked into output")
    return out, changed


def iter_target_paths(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if not path.is_dir():
        raise ValueError(f"{path} is neither a file nor a directory")

    return [path / PARENT_FILENAME, *sorted(child for child in path.iterdir() if is_leaf_target_path(child))]


def _count_targets(paths: Iterable[Path]) -> str:
    return str(sum(1 for _ in paths))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    parser.add_argument(
        "--path",
        type=Path,
        default=ARO_DIR,
        help="ARO directory, the ARO:3001218 YAML file, or one DFR leaf YAML file",
    )
    args = parser.parse_args(argv)

    changed = unchanged = 0
    target_paths = iter_target_paths(args.path)
    problems: list[str] = []
    for path in target_paths:
        if not path.exists():
            problems.append(f"{path}: missing")
            continue
        try:
            before = path.read_text(encoding="utf-8")
            after, did_change = enrich_text(before, path)
        except (OSError, ValueError, yaml.YAMLError) as exc:
            problems.append(str(exc))
            continue

        if not did_change:
            unchanged += 1
            continue

        changed += 1
        print(f"  {'wrote' if args.apply else 'would write'} {path.name}")
        if args.apply:
            path.write_text(after, encoding="utf-8")

    print(f"{'changed' if args.apply else 'would change'}: {changed}")
    print(f"already enriched: {unchanged}")
    print(f"targets considered: {_count_targets(target_paths)}")
    for problem in problems:
        print(f"PROBLEM: {problem}", file=sys.stderr)
    if not args.apply:
        print("dry run -- pass --apply to write")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
