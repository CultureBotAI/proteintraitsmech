#!/usr/bin/env python3
"""Ground and describe the D-Ala-D-Ala ligase glycopeptide graph.

The D-Ala-D-Ala ligase parent is an inversion relative to van ligases: the
native non-van ligase synthesizes the D-Ala-D-Ala precursor that makes cells
vulnerable to glycopeptide antibiotics. This updater preserves that conservative
model while grounding D-Ala-D-Ala ligase activity and its D-alanyl-D-alanine
product.

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

TARGET_IDENTIFIER = "ARO:3003970"
TARGET_FILENAME = "d-ala-d-ala-ligase-aro3003970.yaml"

HISTORY_CURATOR = "codex-causal-graph-quality"
HISTORY_ACTION = (
    "Grounded the D-Ala-D-Ala ligase activity and D-alanyl-D-alanine precursor nodes"
)
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

DDL_EVIDENCE = {
    "reference": TARGET_IDENTIFIER,
    "snippet": (
        "Non-van ligases that synthesize D-Ala-D-Ala, the default cell wall "
        "precursor that makes a cell vulnerable to glycopeptide antibiotics. "
        "Mutations in the ddl gene can cause the production of "
        "nonfunctional/inactivated D-Ala-D-Ala ligases, which can render "
        "bacteria glycopeptide dependent depending on the presence of "
        "vancomycin resistance clusters."
    ),
    "notes": "CARD definition for the non-van D-Ala-D-Ala ligase parent term.",
}

MOLECULAR_BYPASS_EVIDENCE = {
    "reference": "ARO:3000213",
    "snippet": (
        "Peptidoglycan precursors ending in D-Ala-D-Lac or D-Ala-D-Ser instead "
        "of D-Ala-D-Ala conferring high level glycopeptide resistance."
    ),
    "notes": "CARD definition for restructuring of bacterial cell wall conferring antibiotic resistance.",
}

DRUG_RELATION_EVIDENCE = {
    "reference": "ARO:3002906",
    "snippet": "relationship: confers_resistance_to_drug_class ARO:3000081 ! glycopeptide antibiotic",
    "notes": (
        "ARO drug-class relationship asserted on the Van ligase ancestor and "
        "inherited by the D-Ala-D-Ala ligase record."
    ),
}

GLYCOPEPTIDE_EVIDENCE = {
    "reference": "ARO:3000081",
    "snippet": "glycopeptide antibiotic",
    "notes": "ARO drug-class term inherited from the Van ligase branch.",
}

DALA_DALA_LIGASE_EVIDENCE = {
    "reference": "GO:0008716",
    "snippet": (
        "Catalysis of the reaction: 2 D-alanine + ATP = D-alanyl-D-alanine + "
        "ADP + 2 H+ + phosphate."
    ),
    "notes": "GO definition for D-alanine-D-alanine ligase activity.",
}

D_ALANYL_D_ALANINE_EVIDENCE = {
    "reference": "CHEBI:16576",
    "snippet": (
        "A dipeptide comprising D-alanine with a D-alanyl residue attached to "
        "the α-nitrogen."
    ),
    "notes": "ChEBI definition for D-alanyl-D-alanine.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "restructuring of bacterial cell wall conferring antibiotic resistance",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3000213",
}

DRUG_NODE = {
    "node_id": "drug0",
    "label": "glycopeptide antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:3000081",
}

LIGATION_NODE = {
    "node_id": "dala_dala_synthesis",
    "label": "D-Ala-D-Ala ligase activity",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "GO:0008716",
    "description": (
        "Grounded to GO D-alanine-D-alanine ligase activity, matching CARD's "
        "description of non-van ligases that synthesize D-Ala-D-Ala."
    ),
}

SUSCEPTIBLE_PRECURSOR_NODE = {
    "node_id": "susceptible_precursor",
    "label": "D-alanyl-D-alanine",
    "node_type": "CHEMICAL",
    "grounding": "CHEBI:16576",
    "description": (
        "Grounded to ChEBI D-alanyl-D-alanine, the D-Ala-D-Ala precursor that "
        "CARD describes as making cells vulnerable to glycopeptide antibiotics."
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
        "ARO classifies this family under bacterial cell-wall restructuring."
    ),
    ("mech0", "RO:0002411", "resistance"): (
        "Cell-wall restructuring is the Van-branch mechanism that confers "
        "glycopeptide resistance."
    ),
    ("determinant", "RO:0002411", "resistance"): (
        "The record is retained as a conservative conditional glycopeptide "
        "dependence model rather than a direct loss-of-ddl resistance claim."
    ),
    ("determinant", "ARO:2000001", "drug0"): (
        "ARO maps the Van-ligase branch to glycopeptide antibiotics."
    ),
    ("determinant", "RO:0002327", "dala_dala_synthesis"): (
        "Native non-van D-Ala-D-Ala ligases enable D-Ala-D-Ala synthesis."
    ),
    ("dala_dala_synthesis", "RO:0002234", "susceptible_precursor"): (
        "D-alanyl-D-alanine is the output of D-Ala-D-Ala ligase activity."
    ),
    ("susceptible_precursor", "RO:0002436", "drug0"): (
        "D-Ala-D-Ala is retained as the precursor that makes the cell "
        "vulnerable to glycopeptide antibiotics."
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
        "dala_dala_synthesis",
        "susceptible_precursor",
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
        copy.deepcopy(LIGATION_NODE),
        copy.deepcopy(SUSCEPTIBLE_PRECURSOR_NODE),
        copy.deepcopy(RESISTANCE_NODE),
    ]


def _canonical_edges(record: dict[str, Any]) -> list[dict[str, Any]]:
    source_evidence = _source_evidence(record)
    mechanism_evidence = (DDL_EVIDENCE, MOLECULAR_BYPASS_EVIDENCE, *source_evidence)
    ligase_evidence = (DDL_EVIDENCE, DALA_DALA_LIGASE_EVIDENCE, *source_evidence)
    product_evidence = (
        DDL_EVIDENCE,
        DALA_DALA_LIGASE_EVIDENCE,
        D_ALANYL_D_ALANINE_EVIDENCE,
        *source_evidence,
    )
    drug_evidence = (
        DDL_EVIDENCE,
        DRUG_RELATION_EVIDENCE,
        GLYCOPEPTIDE_EVIDENCE,
        *source_evidence,
    )

    return [
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
            (DDL_EVIDENCE, *source_evidence),
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
            "enables (D-Ala-D-Ala synthesis)",
            "RO:0002327",
            "dala_dala_synthesis",
            ligase_evidence,
        ),
        _edge(
            "dala_dala_synthesis",
            "has output",
            "RO:0002234",
            "susceptible_precursor",
            product_evidence,
        ),
        _edge(
            "susceptible_precursor",
            "molecularly interacts with (the drug binds this precursor)",
            "RO:0002436",
            "drug0",
            drug_evidence,
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
        "D-Ala-D-Ala ligase → susceptible glycopeptide precursor → conditional glycopeptide response"
    )
    graph["description"] = (
        "Conservative graph for the native non-van D-Ala-D-Ala ligase family. "
        "D-Ala-D-Ala ligase activity is grounded to GO:0008716 and its "
        "D-alanyl-D-alanine product is grounded to CHEBI:16576, but the graph "
        "keeps the CARD caveat that nonfunctional ddl can render bacteria "
        "glycopeptide dependent only depending on the presence of vancomycin "
        "resistance clusters."
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
        raise ValueError(f"{path}: not a D-Ala-D-Ala ligase target: {identifier}")
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
        help="ARO directory or the exact D-Ala-D-Ala ligase YAML file",
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
