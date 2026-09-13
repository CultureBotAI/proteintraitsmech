#!/usr/bin/env python3
"""Collapse the lipid A acyltransferase charge-alteration graph.

The lipid A acyltransferase parent had an ungrounded local
``aminoacylation`` molecular-function node. The CARD definition supports the
surface-modification state and the downstream charge-reduction mechanism, so
this updater models aminoacylated LPS as a described local state and links it
through reduced negative surface charge to peptide-antibiotic resistance.

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

HISTORY_ACTION = "Collapsed lipid A acyltransferase aminoacylation graph"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

IDENTIFIER = "ARO:3004363"
FILENAME = "lipid-a-acyltransferase-aro3004363.yaml"

LIPID_A_ACYLTRANSFERASE_DEFINITION = (
    "Lipid A acyltransferase genes confer resistance to certain types of peptide "
    "antibiotics such as polymyxins through the aminoacylation of "
    "lipopolysaccharide, thereby decreasing the negative charge of the outer "
    "membrane surface."
)

TARGET_EVIDENCE = {
    "reference": IDENTIFIER,
    "snippet": LIPID_A_ACYLTRANSFERASE_DEFINITION,
    "notes": "CARD definition for lipid A acyltransferase.",
}

CHARGE_ALTERATION_EVIDENCE = {
    "reference": "ARO:3003588",
    "snippet": (
        "The loss or reduction of the net negative charge within the cell wall "
        "of gram negative bacteria is a mechanism of resistance for cationic "
        "antimicrobials that depend on the negative charge for binding to the "
        "surface."
    ),
    "notes": "CARD definition for the shared charge-alteration resistance mechanism.",
}

DRUG_RELATION_EVIDENCE = {
    "reference": IDENTIFIER,
    "snippet": (
        "relationship: confers_resistance_to_drug_class ARO:3000053 ! peptide "
        "antibiotic"
    ),
    "notes": "ARO drug-class relationship asserted directly on lipid A acyltransferase.",
}

PEPTIDE_ANTIBIOTIC_EVIDENCE = {
    "reference": "ARO:3000053",
    "snippet": "peptide antibiotic",
    "notes": "ARO drug class asserted on the lipid A acyltransferase parent.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "charge alteration conferring antibiotic resistance",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3003588",
}

DRUG_NODE = {
    "node_id": "drug0",
    "label": "peptide antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:3000053",
}

AMINOACYLATED_LPS_NODE = {
    "node_id": "aminoacylated_lps",
    "label": "aminoacylated lipopolysaccharide",
    "node_type": "STATE",
    "description": (
        "Local state representing LPS after lipid A acyltransferases aminoacylate "
        "lipopolysaccharide in the outer membrane."
    ),
}

CHARGE_NODE = {
    "node_id": "charge",
    "label": "reduced net negative surface charge",
    "node_type": "STATE",
    "description": (
        "Local state representing the reduced negative outer-membrane surface "
        "charge produced by lipid A aminoacylation."
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
    ("charge", "RO:0002212", "drug0"),
}

LEGACY_AMINOACYLATION_EDGE_KEYS = {
    ("determinant", "RO:0002327", "aminoacylation"),
    ("aminoacylation", "RO:0002411", "charge"),
}

CANONICAL_AMINOACYLATION_EDGE_KEYS = {
    ("determinant", "RO:0002411", "aminoacylated_lps"),
    ("aminoacylated_lps", "RO:0002411", "charge"),
}

CHARGE_RESISTANCE_EDGE_KEY = ("charge", "RO:0002411", "resistance")

EXPECTED_EDGE_KEYS = (
    CORE_EDGE_KEYS
    | CANONICAL_AMINOACYLATION_EDGE_KEYS
    | {CHARGE_RESISTANCE_EDGE_KEY}
)

EDGE_DESCRIPTIONS = {
    ("determinant", "RO:0000056", "mech0"): (
        "CARD classifies lipid A acyltransferase under charge-alteration "
        "antibiotic resistance."
    ),
    ("mech0", "RO:0002411", "resistance"): (
        "Lipid A aminoacylation decreases net negative outer-membrane charge, the "
        "charge-alteration mechanism for peptide-antibiotic resistance."
    ),
    ("determinant", "RO:0002411", "resistance"): (
        "Lipid A acyltransferases confer peptide-antibiotic resistance through "
        "aminoacylation of LPS and reduced outer-membrane negative charge."
    ),
    ("determinant", "ARO:2000001", "drug0"): (
        "ARO maps lipid A acyltransferase to peptide antibiotics."
    ),
    ("determinant", "RO:0002411", "aminoacylated_lps"): (
        "The acyltransferase determinant is upstream of aminoacylated LPS."
    ),
    ("aminoacylated_lps", "RO:0002411", "charge"): (
        "Aminoacylation of LPS decreases the negative charge of the outer-membrane "
        "surface."
    ),
    ("charge", "RO:0002212", "drug0"): (
        "Lower net negative surface charge impedes binding by cationic peptide "
        "antibiotics such as polymyxins."
    ),
    ("charge", "RO:0002411", "resistance"): (
        "Reduced negative outer-membrane charge is the terminal modeled state "
        "causally upstream of peptide-antibiotic resistance."
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
    seen: set[tuple[str, str]] = set()
    for item in evidence:
        key = (item["reference"], " ".join(item.get("snippet", "").split()))
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


def _validate_graph(graph: dict[str, Any]) -> None:
    nodes = _nodes_by_id(graph)
    missing_nodes = sorted({"determinant", "mech0", "drug0", "charge", "resistance"} - set(nodes))
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{IDENTIFIER}: missing node(s): {missing}")

    input_edges = EXPECTED_EDGE_KEYS | LEGACY_AMINOACYLATION_EDGE_KEYS
    seen: set[tuple[str, str, str]] = set()
    for edge in _dicts(graph.get("edges")):
        key = _edge_key(edge)
        if key not in input_edges:
            raise ValueError(f"{IDENTIFIER}: unexpected edge {key[0]} -> {key[2]}")
        if key in seen:
            raise ValueError(f"{IDENTIFIER}: duplicate edge {key[0]} -> {key[2]}")
        seen.add(key)

    missing_edges = CORE_EDGE_KEYS - seen
    if missing_edges:
        missing = ", ".join(
            f"{subject} -> {object_}"
            for subject, _, object_ in sorted(missing_edges)
        )
        raise ValueError(f"{IDENTIFIER}: missing edge(s): {missing}")

    legacy = LEGACY_AMINOACYLATION_EDGE_KEYS <= seen
    canonical = CANONICAL_AMINOACYLATION_EDGE_KEYS <= seen
    if not legacy and not canonical:
        raise ValueError(
            f"{IDENTIFIER}: missing both canonical and legacy aminoacylation edges"
        )


def _canonical_graph(record: dict[str, Any]) -> dict[str, Any]:
    graph = record["causal_graphs"][0]
    _validate_graph(graph)
    nodes = _nodes_by_id(graph)
    source_evidence = _source_evidence(record)
    route_evidence = (
        TARGET_EVIDENCE,
        CHARGE_ALTERATION_EVIDENCE,
        *source_evidence,
    )
    drug_evidence = (
        TARGET_EVIDENCE,
        CHARGE_ALTERATION_EVIDENCE,
        DRUG_RELATION_EVIDENCE,
        PEPTIDE_ANTIBIOTIC_EVIDENCE,
        *source_evidence,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → lipid A aminoacylation → peptide-antibiotic resistance",
        "description": (
            "Curated lipid A acyltransferase resistance graph. The graph keeps "
            "the CARD charge-alteration mechanism and peptide-antibiotic route, "
            "collapses ungrounded aminoacylation to a described aminoacylated-LPS "
            "state, and connects the reduced surface-charge state to resistance."
        ),
        "nodes": [
            copy.deepcopy(nodes["determinant"]),
            copy.deepcopy(MECHANISM_NODE),
            copy.deepcopy(DRUG_NODE),
            copy.deepcopy(AMINOACYLATED_LPS_NODE),
            copy.deepcopy(CHARGE_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                route_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                route_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                route_evidence,
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
                "causally upstream of",
                "RO:0002411",
                "aminoacylated_lps",
                route_evidence,
            ),
            _edge(
                "aminoacylated_lps",
                "causally upstream of (reduces surface negative charge)",
                "RO:0002411",
                "charge",
                route_evidence,
            ),
            _edge(
                "charge",
                "negatively regulates (impedes drug binding)",
                "RO:0002212",
                "drug0",
                route_evidence,
            ),
            _edge(
                "charge",
                "causally upstream of (reduced peptide-antibiotic binding)",
                "RO:0002411",
                "resistance",
                route_evidence,
            ),
        ],
    }


def enrich_record(record: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != IDENTIFIER:
        raise ValueError(f"expected {IDENTIFIER}, found {record.get('identifier')}")

    out = copy.deepcopy(record)
    before = copy.deepcopy(out.get("causal_graphs"))
    graphs = out.get("causal_graphs") or []
    graph_index = next(
        (index for index, item in enumerate(graphs) if item.get("graph_id") == "resistance"),
        None,
    )
    if graph_index is None:
        raise ValueError(f"{IDENTIFIER}: missing resistance causal graph")

    graphs[graph_index] = _canonical_graph(out)
    return out, out.get("causal_graphs") != before


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: record is not a mapping")
    if record.get("identifier") != IDENTIFIER:
        raise ValueError(f"{path}: not a lipid A acyltransferase target")
    if path.name != FILENAME:
        raise ValueError(f"{path}: target {IDENTIFIER} must be in {FILENAME}")

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
    return [path / FILENAME]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    parser.add_argument(
        "--path",
        type=Path,
        default=ARO_DIR,
        help="ARO directory or exact lipid A acyltransferase YAML",
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
