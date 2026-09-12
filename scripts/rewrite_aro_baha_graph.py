#!/usr/bin/env python3
"""Rewrite the BahA bacitracin amidohydrolysis causal graph.

BahA is the named bacitracin amidohydrolase record.  Its promoted graph still
contains an ungrounded local hydrolase node and stops at the inactive-drug
state.  This updater reuses the bacitracin-specific ARO amidohydrolysis
mechanism used for the Bah amidohydrolase parent and terminates the
drug-inactivation path at resistance.

Dry-run by default; pass ``--apply`` to write.
"""

from __future__ import annotations

import argparse
import copy
import sys
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from record_io import append_to_section, replace_block  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ARO_DIR = ROOT / "data" / "traits" / "function" / "resistance" / "aro"

TARGET_IDENTIFIER = "ARO:3003984"
TARGET_FILENAME = "baha-aro3003984.yaml"

HISTORY_CURATOR = "codex-causal-graph-quality"
HISTORY_ACTION = "Completed the BahA bacitracin amidohydrolysis graph"
HISTORY_EVENT = {
    "timestamp": "2026-09-07T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

BAH_PARENT_EVIDENCE = {
    "reference": "ARO:3004260",
    "snippet": "Bah amidohydrolases are membrane proteins that inactivate bacitracin.",
    "notes": "CARD definition for the Bah amidohydrolase family term.",
}

ANTIBIOTIC_INACTIVATION_EVIDENCE = {
    "reference": "ARO:0001004",
    "snippet": "Enzymatic inactivation of antibiotic to confer drug resistance.",
    "notes": "CARD definition for the antibiotic inactivation mechanism.",
}

AMIDOHYDROLYSIS_EVIDENCE = {
    "reference": "ARO:3003985",
    "snippet": (
        "Hydrolysis of amido side-chain of asparagine-12 forming hydrogen "
        "bond with undecaprenyl pyrophosphate in bacitracin leading to "
        "antibiotic inactivation."
    ),
    "notes": (
        "CARD definition for amidohydrolysis of bacitracin undecaprenyl "
        "pyrophosphate."
    ),
}

DRUG_RELATION_EVIDENCE = {
    "reference": "ARO:3004260",
    "snippet": "relationship: confers_resistance_to_drug_class ARO:3000053 ! peptide antibiotic",
    "notes": (
        "ARO drug-class relationship asserted on the Bah amidohydrolase parent "
        "term and inherited by BahA."
    ),
}

PEPTIDE_ANTIBIOTIC_EVIDENCE = {
    "reference": "ARO:3000053",
    "snippet": "peptide antibiotic",
    "notes": "ARO drug-class term targeted by Bah amidohydrolase.",
}

PUBLISHED_BAHA_EVIDENCE = {
    "reference": "DOI:10.1038/ncomms13803",
    "notes": "CARD-cited report describing BahA in Paenibacillus sp. LC231.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "antibiotic inactivation",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:0001004",
}

DRUG_NODE = {
    "node_id": "drug0",
    "label": "peptide antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:3000053",
}

AMIDOHYDROLYSIS_NODE = {
    "node_id": "modification",
    "label": "amidohydrolysis of bacitracin undecaprenyl pyrophosphate",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3003985",
    "description": (
        "Grounded to the bacitracin-specific ARO amidohydrolysis mechanism "
        "asserted on the BahA record."
    ),
}

INACTIVATED_NODE = {
    "node_id": "inactivated",
    "label": "amidohydrolyzed, inactive bacitracin",
    "node_type": "STATE",
    "description": (
        "Local state representing bacitracin after BahA-mediated "
        "amidohydrolysis makes it inactive."
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

EDGE_DESCRIPTIONS = {
    ("determinant", "RO:0000056", "mech0"): (
        "ARO classifies BahA under antibiotic inactivation through the Bah "
        "amidohydrolase family."
    ),
    ("mech0", "RO:0002411", "resistance"): (
        "Antibiotic inactivation is the broad resistance mechanism reached by "
        "BahA-mediated bacitracin amidohydrolysis."
    ),
    ("determinant", "RO:0002411", "resistance"): (
        "BahA confers resistance by inactivating bacitracin through "
        "amidohydrolysis."
    ),
    ("determinant", "ARO:2000001", "drug0"): (
        "BahA inherits the Bah amidohydrolase peptide-antibiotic drug class."
    ),
    ("determinant", "RO:0002327", "modification"): (
        "BahA enables the bacitracin amidohydrolysis mechanism."
    ),
    ("modification", "RO:0002233", "drug0"): (
        "Bacitracin is the peptide-antibiotic substrate of the "
        "amidohydrolysis mechanism."
    ),
    ("modification", "RO:0002411", "inactivated"): (
        "Amidohydrolysis converts bacitracin to an inactive form."
    ),
    ("inactivated", "RO:0002411", "resistance"): (
        "Inactive amidohydrolyzed bacitracin reduces effective drug exposure "
        "and produces the resistance phenotype."
    ),
}

EXPECTED_EDGE_KEYS = set(EDGE_DESCRIPTIONS)
REQUIRED_INPUT_EDGE_KEYS = {
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("determinant", "ARO:2000001", "drug0"),
}
OLD_EDGE_KEYS = {
    ("determinant", "RO:0000056", "mech1"),
    ("mech1", "RO:0002411", "resistance"),
    ("determinant", "RO:0002327", "transfer"),
    ("transfer", "RO:0002233", "drug0"),
    ("transfer", "RO:0002411", "modified"),
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


def _unique_evidence(*items: dict[str, str]) -> list[dict[str, str]]:
    unique: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for item in items:
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
    *evidence: dict[str, str],
) -> dict[str, Any]:
    return {
        "subject": subject,
        "predicate": predicate,
        "predicate_id": predicate_id,
        "object": object_,
        "description": EDGE_DESCRIPTIONS[(subject, predicate_id, object_)],
        "evidence": _unique_evidence(*evidence),
    }


def _record_evidence(record: dict[str, Any]) -> dict[str, str]:
    return {
        "reference": str(record["identifier"]),
        "snippet": str(record["definition"]),
        "notes": f"CARD definition for {record['label']}.",
    }


def _nodes_by_id(graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(node["node_id"]): node
        for node in _dicts(graph.get("nodes"))
        if "node_id" in node
    }


def _validate_graph(graph: dict[str, Any]) -> None:
    nodes = _nodes_by_id(graph)
    missing_nodes = sorted(
        {"determinant", "mech0", "drug0", "resistance"} - set(nodes),
    )
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{TARGET_IDENTIFIER}: missing node(s): {missing}")
    if not {"modification", "transfer"} & set(nodes):
        raise ValueError(f"{TARGET_IDENTIFIER}: missing modification or transfer node")
    if not {"inactivated", "modified"} & set(nodes):
        raise ValueError(f"{TARGET_IDENTIFIER}: missing inactive drug state")

    seen: set[tuple[str, str, str]] = set()
    found: set[tuple[str, str, str]] = set()
    for edge in _dicts(graph.get("edges")):
        key = _edge_key(edge)
        if key not in EXPECTED_EDGE_KEYS and key not in OLD_EDGE_KEYS:
            raise ValueError(f"{TARGET_IDENTIFIER}: unexpected edge {key[0]} -> {key[2]}")
        if key in seen:
            raise ValueError(f"{TARGET_IDENTIFIER}: duplicate edge {key[0]} -> {key[2]}")
        seen.add(key)
        found.add(key)

    missing_edges = sorted(REQUIRED_INPUT_EDGE_KEYS - found)
    if missing_edges:
        missing = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in missing_edges)
        raise ValueError(f"{TARGET_IDENTIFIER}: missing edge(s): {missing}")


def _graph(record: dict[str, Any]) -> dict[str, Any]:
    record_evidence = _record_evidence(record)
    broad_evidence = (
        record_evidence,
        BAH_PARENT_EVIDENCE,
        ANTIBIOTIC_INACTIVATION_EVIDENCE,
        PUBLISHED_BAHA_EVIDENCE,
    )
    amidohydrolysis_evidence = (
        record_evidence,
        BAH_PARENT_EVIDENCE,
        AMIDOHYDROLYSIS_EVIDENCE,
        PUBLISHED_BAHA_EVIDENCE,
    )
    resistance_evidence = (
        record_evidence,
        BAH_PARENT_EVIDENCE,
        ANTIBIOTIC_INACTIVATION_EVIDENCE,
        AMIDOHYDROLYSIS_EVIDENCE,
        PUBLISHED_BAHA_EVIDENCE,
    )
    drug_evidence = (
        record_evidence,
        BAH_PARENT_EVIDENCE,
        DRUG_RELATION_EVIDENCE,
        PEPTIDE_ANTIBIOTIC_EVIDENCE,
        PUBLISHED_BAHA_EVIDENCE,
    )

    return {
        "graph_id": "resistance",
        "title": "BahA → bacitracin amidohydrolysis → antibiotic resistance",
        "description": (
            "BahA confers peptide-antibiotic resistance by inactivating "
            "bacitracin through amidohydrolysis, using the bacitracin-specific "
            "ARO:3003985 mechanism."
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
            copy.deepcopy(AMIDOHYDROLYSIS_NODE),
            copy.deepcopy(INACTIVATED_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                *broad_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                *broad_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                *resistance_evidence,
            ),
            _edge(
                "determinant",
                "confers resistance to",
                "ARO:2000001",
                "drug0",
                *drug_evidence,
            ),
            _edge(
                "determinant",
                "enables (amidohydrolyzes bacitracin)",
                "RO:0002327",
                "modification",
                *amidohydrolysis_evidence,
            ),
            _edge(
                "modification",
                "has input (the bacitracin peptide antibiotic)",
                "RO:0002233",
                "drug0",
                *amidohydrolysis_evidence,
            ),
            _edge(
                "modification",
                "causally upstream of (inactivates the drug)",
                "RO:0002411",
                "inactivated",
                *amidohydrolysis_evidence,
            ),
            _edge(
                "inactivated",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                *resistance_evidence,
            ),
        ],
    }


def enrich_record(record: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != TARGET_IDENTIFIER:
        raise ValueError(f"expected {TARGET_IDENTIFIER}, found {record.get('identifier')}")
    if not record.get("label"):
        raise ValueError(f"{TARGET_IDENTIFIER}: missing label")
    if not record.get("definition"):
        raise ValueError(f"{TARGET_IDENTIFIER}: missing definition")

    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1 or graphs[0].get("graph_id") != "resistance":
        raise ValueError(f"{TARGET_IDENTIFIER}: expected exactly one resistance graph")
    _validate_graph(graphs[0])

    out = copy.deepcopy(record)
    out["causal_graphs"] = [_graph(record)]
    return out, out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")
    identifier = record.get("identifier")
    if identifier != TARGET_IDENTIFIER:
        raise ValueError(f"{path}: not a BahA target: {identifier}")
    if path.name != TARGET_FILENAME:
        raise ValueError(f"{path}: target {identifier} must be in {TARGET_FILENAME}")

    enriched, changed = enrich_record(record)
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
        changed = True

    if "&id" in out or "*id" in out:
        raise ValueError(f"{path}: YAML anchors leaked into output")
    return out, changed


def iter_target_paths(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if not path.is_dir():
        raise ValueError(f"{path} is neither a file nor a directory")
    return [path / TARGET_FILENAME]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    parser.add_argument(
        "--path",
        type=Path,
        default=ARO_DIR,
        help="ARO directory or the exact BahA YAML file",
    )
    args = parser.parse_args(argv)

    changed = unchanged = 0
    problems: list[str] = []
    for path in iter_target_paths(args.path):
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
    for problem in problems:
        print(f"PROBLEM: {problem}", file=sys.stderr)
    if not args.apply:
        print("dry run -- pass --apply to write")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
