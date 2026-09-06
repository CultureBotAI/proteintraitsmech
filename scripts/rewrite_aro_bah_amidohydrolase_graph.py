#!/usr/bin/env python3
"""Ground and describe the Bah amidohydrolase parent graph.

The Bah family record states that Bah amidohydrolases inactivate bacitracin.
ARO already has a specific child mechanism for the chemistry used by BahA:
amidohydrolysis of the bacitracin Asn-12 amido side chain. This updater reuses
that mechanism grounding while preserving the local inactive-bacitracin state.

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

TARGET_IDENTIFIER = "ARO:3004260"
TARGET_FILENAME = "bah-amidohydrolase-aro3004260.yaml"

HISTORY_CURATOR = "codex-causal-graph-quality"
HISTORY_ACTION = "Grounded the Bah amidohydrolase bacitracin-inactivation graph"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

BAH_EVIDENCE = {
    "reference": TARGET_IDENTIFIER,
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
        "Hydrolysis of amido side-chain of asparagine-12 forming hydrogen bond "
        "with undecaprenyl pyrophosphate in bacitracin leading to antibiotic "
        "inactivation."
    ),
    "notes": (
        "CARD definition for amidohydrolysis of bacitracin undecaprenyl "
        "pyrophosphate."
    ),
}

DRUG_RELATION_EVIDENCE = {
    "reference": TARGET_IDENTIFIER,
    "snippet": "relationship: confers_resistance_to_drug_class ARO:3000053 ! peptide antibiotic",
    "notes": (
        "ARO drug-class relationship asserted on the Bah amidohydrolase parent "
        "term."
    ),
}

PEPTIDE_ANTIBIOTIC_EVIDENCE = {
    "reference": "ARO:3000053",
    "snippet": "peptide antibiotic",
    "notes": "ARO drug-class term targeted by Bah amidohydrolase.",
}

PUBLISHED_BAHA_EVIDENCE = {
    "reference": "DOI:10.1038/ncomms13803",
    "notes": "PMID:27929110 (aro citation)",
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
        "used by the BahA child record."
    ),
}

INACTIVATED_NODE = {
    "node_id": "inactivated",
    "label": "amidohydrolyzed, inactive bacitracin",
    "node_type": "STATE",
    "description": (
        "Local state representing bacitracin after Bah-mediated "
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
        "ARO classifies Bah amidohydrolase under antibiotic inactivation."
    ),
    ("mech0", "RO:0002411", "resistance"): (
        "Antibiotic inactivation is the broad resistance mechanism reached by "
        "Bah-mediated bacitracin amidohydrolysis."
    ),
    ("determinant", "RO:0002411", "resistance"): (
        "Bah amidohydrolases confer resistance by inactivating bacitracin."
    ),
    ("determinant", "ARO:2000001", "drug0"): (
        "ARO maps Bah amidohydrolase to the peptide antibiotic class."
    ),
    ("determinant", "RO:0002327", "modification"): (
        "The determinant enables the bacitracin amidohydrolysis mechanism."
    ),
    ("modification", "RO:0002233", "drug0"): (
        "Bacitracin is the peptide-antibiotic substrate of the "
        "amidohydrolysis mechanism."
    ),
    ("modification", "RO:0002411", "inactivated"): (
        "Amidohydrolysis converts bacitracin to an inactive form."
    ),
}

EXPECTED_EDGE_KEYS = set(EDGE_DESCRIPTIONS)


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


def _source_evidence(record: dict[str, Any]) -> tuple[dict[str, str], ...]:
    return tuple(
        {
            "reference": str(item["reference"]),
            "notes": str(item.get("notes") or "ARO citation for this record."),
        }
        for item in record.get("evidence") or []
        if isinstance(item, dict) and item.get("reference")
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


def _validate_graph(graph: dict[str, Any]) -> None:
    nodes = _nodes_by_id(graph)
    expected_nodes = {
        "determinant",
        "mech0",
        "drug0",
        "modification",
        "inactivated",
        "resistance",
    }
    missing_nodes = sorted(expected_nodes - set(nodes))
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{TARGET_IDENTIFIER}: missing node(s): {missing}")

    found_edges = set()
    seen: set[tuple[str, str, str]] = set()
    for edge in graph.get("edges") or []:
        key = _edge_key(edge)
        if key not in EXPECTED_EDGE_KEYS:
            raise ValueError(f"{TARGET_IDENTIFIER}: unexpected edge {key[0]} -> {key[2]}")
        if key in seen:
            raise ValueError(f"{TARGET_IDENTIFIER}: duplicate edge {key[0]} -> {key[2]}")
        seen.add(key)
        found_edges.add(key)

    missing_edges = sorted(EXPECTED_EDGE_KEYS - found_edges)
    if missing_edges:
        missing = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in missing_edges)
        raise ValueError(f"{TARGET_IDENTIFIER}: missing edge(s): {missing}")


def _canonical_nodes(graph: dict[str, Any]) -> list[dict[str, Any]]:
    nodes = _nodes_by_id(graph)
    return [
        copy.deepcopy(nodes["determinant"]),
        copy.deepcopy(MECHANISM_NODE),
        copy.deepcopy(DRUG_NODE),
        copy.deepcopy(AMIDOHYDROLYSIS_NODE),
        copy.deepcopy(INACTIVATED_NODE),
        copy.deepcopy(RESISTANCE_NODE),
    ]


def _canonical_edges(record: dict[str, Any]) -> list[dict[str, Any]]:
    source_evidence = _source_evidence(record) or (PUBLISHED_BAHA_EVIDENCE,)
    broad_evidence = (
        BAH_EVIDENCE,
        ANTIBIOTIC_INACTIVATION_EVIDENCE,
        *source_evidence,
    )
    amidohydrolysis_evidence = (
        BAH_EVIDENCE,
        AMIDOHYDROLYSIS_EVIDENCE,
        *source_evidence,
    )
    resistance_evidence = (
        BAH_EVIDENCE,
        ANTIBIOTIC_INACTIVATION_EVIDENCE,
        AMIDOHYDROLYSIS_EVIDENCE,
        *source_evidence,
    )
    drug_evidence = (
        BAH_EVIDENCE,
        DRUG_RELATION_EVIDENCE,
        PEPTIDE_ANTIBIOTIC_EVIDENCE,
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
            resistance_evidence,
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
            "enables (amidohydrolyzes bacitracin)",
            "RO:0002327",
            "modification",
            amidohydrolysis_evidence,
        ),
        _edge(
            "modification",
            "has input (the bacitracin peptide antibiotic)",
            "RO:0002233",
            "drug0",
            amidohydrolysis_evidence,
        ),
        _edge(
            "modification",
            "causally upstream of (inactivates the drug)",
            "RO:0002411",
            "inactivated",
            amidohydrolysis_evidence,
        ),
    ]


def enrich_record(record: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != TARGET_IDENTIFIER:
        raise ValueError(f"expected {TARGET_IDENTIFIER}, found {record.get('identifier')}")

    out = copy.deepcopy(record)
    before = copy.deepcopy(out.get("causal_graphs"))
    graphs = out.get("causal_graphs") or []
    graph = next((item for item in graphs if item.get("graph_id") == "resistance"), None)
    if graph is None:
        raise ValueError(f"{TARGET_IDENTIFIER}: missing resistance causal graph")

    _validate_graph(graph)
    graph["title"] = (
        "Bah amidohydrolase → bacitracin amidohydrolysis → antibiotic resistance"
    )
    graph["description"] = (
        "Bah amidohydrolases confer peptide-antibiotic resistance by "
        "inactivating bacitracin. The reaction is grounded to ARO:3003985, "
        "amidohydrolysis of bacitracin undecaprenyl pyrophosphate, matching "
        "the BahA child mechanism."
    )
    graph["nodes"] = _canonical_nodes(graph)
    graph["edges"] = _canonical_edges(out)
    return out, out.get("causal_graphs") != before


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: record is not a mapping")
    identifier = record.get("identifier")
    if identifier != TARGET_IDENTIFIER:
        raise ValueError(f"{path}: not a Bah amidohydrolase target: {identifier}")
    if path.name != TARGET_FILENAME:
        raise ValueError(f"{path}: target {identifier} must be in {TARGET_FILENAME}")

    enriched, changed = enrich_record(record)
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
    return [path / TARGET_FILENAME]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    parser.add_argument(
        "--path",
        type=Path,
        default=ARO_DIR,
        help="ARO directory or the exact Bah amidohydrolase YAML file",
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
