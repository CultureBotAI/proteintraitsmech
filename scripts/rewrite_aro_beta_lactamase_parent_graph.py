#!/usr/bin/env python3
"""Rewrite the broad beta-lactamase parent graph.

The beta-lactamase parent names beta-lactam ring opening but does not choose
the serine or metallo-beta-lactamase route used by its descendants.  This
updater replaces the generic auto-scaffold with a conservative local
beta-lactam hydrolysis path that feeds CARD's broad antibiotic-inactivation
mechanism.

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
TARGET_IDENTIFIER = "ARO:3000001"
TARGET_FILE = "beta-lactamase-aro3000001.yaml"

HISTORY_ACTION = "Completed broad beta-lactamase parent causal graph"
HISTORY_EVENT = {
    "timestamp": "2026-09-11T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

BETA_LACTAMASE_EVIDENCE = {
    "reference": "ARO:3000001",
    "snippet": (
        "The lactamase enzyme breaks that ring open, deactivating the "
        "molecule's antibacterial properties."
    ),
    "notes": "CARD definition for beta-lactamases.",
}

INACTIVATION_ENZYME_EVIDENCE = {
    "reference": "ARO:3000557",
    "snippet": (
        "Enzyme that catalyzes the inactivation of an antibiotic resulting in "
        "resistance. Inactivation includes chemical modification, destruction, etc."
    ),
    "notes": "CARD definition for antibiotic inactivation enzymes.",
}

ANTIBIOTIC_INACTIVATION_EVIDENCE = {
    "reference": "ARO:0001004",
    "snippet": "Enzymatic inactivation of antibiotic to confer drug resistance.",
    "notes": "CARD definition for antibiotic inactivation.",
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

EDGE_ORDER = (
    ("determinant", "RO:0000056", "mech0"),
    ("determinant", "RO:0002327", "ring_opening"),
    ("ring_opening", "RO:0002411", "inactive"),
    ("inactive", "RO:0002411", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
)


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


def _record_evidence(record: dict[str, Any]) -> tuple[dict[str, str], ...]:
    return tuple(
        {
            "reference": str(item["reference"]),
            "notes": str(item.get("notes") or "ARO citation for the beta-lactamase parent."),
        }
        for item in _dicts(record.get("evidence"))
        if item.get("reference")
    )


def _unique_evidence(*items: dict[str, Any]) -> list[dict[str, Any]]:
    unique: list[dict[str, Any]] = []
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
        unique.append(copy.deepcopy(item))
    return unique


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


def _edge_key(edge: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(edge.get("subject", "")),
        str(edge.get("predicate_id", "")),
        str(edge.get("object", "")),
    )


def _validate_current_graph(record: dict[str, Any]) -> None:
    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1:
        raise ValueError(f"{TARGET_IDENTIFIER}: expected exactly one resistance graph")

    expected = set(EDGE_ORDER)
    initial = {
        ("determinant", "RO:0000056", "mech0"),
        ("mech0", "RO:0002411", "resistance"),
        ("determinant", "RO:0002411", "resistance"),
    }
    found = {_edge_key(edge) for edge in _dicts(graphs[0].get("edges"))}
    if found != initial and found != expected:
        raise ValueError(f"{TARGET_IDENTIFIER}: unexpected edge set {sorted(found)}")


def _canonical_edges(record: dict[str, Any]) -> list[dict[str, Any]]:
    source_evidence = _record_evidence(record)
    beta_lactamase = (BETA_LACTAMASE_EVIDENCE, *source_evidence)
    inactivation = (
        BETA_LACTAMASE_EVIDENCE,
        INACTIVATION_ENZYME_EVIDENCE,
        ANTIBIOTIC_INACTIVATION_EVIDENCE,
        *source_evidence,
    )

    edges = {
        ("determinant", "RO:0000056", "mech0"): _edge(
            "determinant",
            "participates in (resistance mechanism)",
            "RO:0000056",
            "mech0",
            "ARO classifies beta-lactamases under broad antibiotic inactivation.",
            *inactivation,
        ),
        ("determinant", "RO:0002327", "ring_opening"): _edge(
            "determinant",
            "enables (opens the beta-lactam ring)",
            "RO:0002327",
            "ring_opening",
            "Beta-lactamases catalyze opening of the beta-lactam ring.",
            *beta_lactamase,
        ),
        ("ring_opening", "RO:0002411", "inactive"): _edge(
            "ring_opening",
            "causally upstream of (deactivates the antibiotic)",
            "RO:0002411",
            "inactive",
            "Opening the beta-lactam ring deactivates the antibiotic molecule.",
            *beta_lactamase,
        ),
        ("inactive", "RO:0002411", "mech0"): _edge(
            "inactive",
            "causally upstream of",
            "RO:0002411",
            "mech0",
            "The opened and inactive beta-lactam antibiotic state realizes antibiotic inactivation.",
            *inactivation,
        ),
        ("mech0", "RO:0002411", "resistance"): _edge(
            "mech0",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            "Enzymatic antibiotic inactivation is upstream of the resistant phenotype.",
            *inactivation,
        ),
        ("determinant", "RO:0002411", "resistance"): _edge(
            "determinant",
            "causally upstream of (confers resistance)",
            "RO:0002411",
            "resistance",
            "Beta-lactamases confer resistance by breaking open and deactivating beta-lactam antibiotics.",
            *inactivation,
        ),
    }
    return [edges[key] for key in EDGE_ORDER]


def enrich_record(record: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != TARGET_IDENTIFIER:
        raise ValueError(f"expected {TARGET_IDENTIFIER}, found {record.get('identifier')}")

    _validate_current_graph(record)
    out = copy.deepcopy(record)
    out["mapping_status"] = "REVIEWED"
    out["causal_graphs"] = [
        {
            "graph_id": "resistance",
            "title": "beta-lactamase → beta-lactam antibiotic resistance",
            "description": (
                "Conservative graph for the broad beta-lactamase parent. The graph "
                "models beta-lactam ring opening as a local mechanism because this "
                "parent term spans both serine and metallo-beta-lactamase chemistries."
            ),
            "nodes": [
                {
                    "node_id": "determinant",
                    "label": "beta-lactamase",
                    "node_type": "PROTEIN",
                    "grounding": "ARO:3000001",
                },
                {
                    "node_id": "mech0",
                    "label": "antibiotic inactivation",
                    "node_type": "MOLECULAR_FUNCTION",
                    "grounding": "ARO:0001004",
                },
                {
                    "node_id": "ring_opening",
                    "label": "beta-lactam ring opening",
                    "node_type": "MOLECULAR_FUNCTION",
                    "local": True,
                    "description": (
                        "Record-local broad beta-lactamase activity; no single external "
                        "term covers both serine and metallo-beta-lactamase ring-opening "
                        "chemistries at this parent level."
                    ),
                },
                {
                    "node_id": "inactive",
                    "label": "opened, inactive beta-lactam antibiotic",
                    "node_type": "STATE",
                    "local": True,
                    "description": (
                        "Record-local state representing a beta-lactam antibiotic whose "
                        "four-membered beta-lactam ring has been opened."
                    ),
                },
                copy.deepcopy(RESISTANCE_NODE),
            ],
            "edges": _canonical_edges(record),
        }
    ]
    return out, out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    if path.name != TARGET_FILE:
        raise ValueError(f"{path}: not the beta-lactamase parent target")

    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: record is not a mapping")

    enriched, changed = enrich_record(record)
    out = text.replace("mapping_status: SEEDED", "mapping_status: REVIEWED", 1)
    out = replace_block(out, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    if HISTORY_ACTION not in out:
        out = append_to_section(out, "curation_history", _dump({"curation_history": [HISTORY_EVENT]}))

    if "&id" in out or "*id" in out:
        raise ValueError(f"{path}: YAML anchors leaked into output")
    return out, changed or out != text


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    parser.add_argument(
        "--path",
        type=Path,
        default=ARO_DIR / TARGET_FILE,
        help="beta-lactamase parent YAML file",
    )
    args = parser.parse_args()

    try:
        before = args.path.read_text(encoding="utf-8")
        after, changed = enrich_text(before, args.path)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"PROBLEM: {exc}", file=sys.stderr)
        return 1

    if changed and args.apply:
        args.path.write_text(after, encoding="utf-8")
    print(f"{'changed' if args.apply else 'would change'}: {int(changed)}")
    if not args.apply:
        print("dry run -- pass --apply to write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
