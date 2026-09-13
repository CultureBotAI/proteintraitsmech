#!/usr/bin/env python3
"""Complete edge evidence for the ARO resistance-via-absence parent graph.

The gene-conferring-resistance-via-absence record is already REVIEWED and
already has the conservative five-edge graph. This updater only completes edge
descriptions and adds the two applicable CARD references to each edge.

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
TARGET = (
    ROOT
    / "data"
    / "traits"
    / "function"
    / "resistance"
    / "aro"
    / "gene-conferring-resistance-via-absence-aro3003768.yaml"
)

HISTORY_ACTION = "Completed resistance-via-absence parent graph edge evidence"
HISTORY_EVENT = {
    "timestamp": "2026-09-11T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

ABSENCE_EVIDENCE = {
    "reference": "ARO:3003768",
    "snippet": (
        "Deletion of gene or gene product results in resistance. For example, "
        "deletion of a porin gene blocks drug from entering the cell."
    ),
    "notes": "CARD definition for the gene-conferring-resistance-via-absence parent.",
}

MECHANISM_EVIDENCE = {
    "reference": "ARO:3003764",
    "snippet": "Mechanism of antibiotic resistance conferred by deletion of gene (usually a porin).",
    "notes": "CARD definition for the resistance-by-absence mechanism.",
}

EDGE_ORDER = (
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("determinant", "RO:0000086", "absence"),
    ("absence", "RO:0002411", "resistance"),
)
EDGE_KEYS = set(EDGE_ORDER)

EDGE_TEXT = {
    ("determinant", "RO:0000056", "mech0"): {
        "predicate": "participates in (resistance mechanism)",
        "description": (
            "ARO maps this determinant to the resistance-by-absence mechanism because "
            "deletion of the gene or gene product results in resistance."
        ),
        "evidence": (ABSENCE_EVIDENCE, MECHANISM_EVIDENCE),
    },
    ("mech0", "RO:0002411", "resistance"): {
        "predicate": "causally upstream of",
        "description": (
            "The resistance-by-absence mechanism is upstream of the resistance phenotype."
        ),
        "evidence": (MECHANISM_EVIDENCE, ABSENCE_EVIDENCE),
    },
    ("determinant", "RO:0002411", "resistance"): {
        "predicate": "causally upstream of (confers resistance)",
        "description": (
            "Deletion of the gene or gene product named by this determinant can result "
            "in antibiotic resistance."
        ),
        "evidence": (ABSENCE_EVIDENCE, MECHANISM_EVIDENCE),
    },
    ("determinant", "RO:0000086", "absence"): {
        "predicate": "has quality (deleted or inactivated)",
        "description": (
            "The determinant here is a loss: what the record names is a gene whose "
            "deletion confers resistance, not a gene product that acts."
        ),
        "evidence": (ABSENCE_EVIDENCE, MECHANISM_EVIDENCE),
    },
    ("absence", "RO:0002411", "resistance"): {
        "predicate": "causally upstream of (confers resistance)",
        "description": (
            "The absent state is the conservative causal core; the downstream effect "
            "differs across child records and no source covers all children."
        ),
        "evidence": (MECHANISM_EVIDENCE, ABSENCE_EVIDENCE),
    },
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


def _validate_graph(graph: dict[str, Any]) -> None:
    found = {_edge_key(edge) for edge in _dicts(graph.get("edges"))}
    if found != EDGE_KEYS:
        missing = EDGE_KEYS - found
        unexpected = found - EDGE_KEYS
        raise ValueError(f"ARO:3003768: unexpected edge set: {missing=} {unexpected=}")


def _edge(subject: str, predicate_id: str, object_: str) -> dict[str, Any]:
    edge_text = EDGE_TEXT[(subject, predicate_id, object_)]
    return {
        "subject": subject,
        "predicate": edge_text["predicate"],
        "predicate_id": predicate_id,
        "object": object_,
        "description": edge_text["description"],
        "evidence": [copy.deepcopy(item) for item in edge_text["evidence"]],
    }


def enrich_record(record: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != "ARO:3003768":
        raise ValueError(f"expected ARO:3003768, found {record.get('identifier')}")

    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1:
        raise ValueError("ARO:3003768: expected exactly one resistance graph")

    graph = copy.deepcopy(graphs[0])
    _validate_graph(graph)
    graph["edges"] = [_edge(*key) for key in EDGE_ORDER]

    out = copy.deepcopy(record)
    out["mapping_status"] = "REVIEWED"
    out["causal_graphs"] = [graph]
    return out, out != record


def enrich_text(text: str) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{TARGET}: record is not a mapping")

    enriched, changed = enrich_record(record)
    out = text.replace("mapping_status: SEEDED", "mapping_status: REVIEWED", 1)
    out = replace_block(out, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    if HISTORY_ACTION not in out:
        out = append_to_section(out, "curation_history", _dump({"curation_history": [HISTORY_EVENT]}))
        changed = True

    if "&id" in out or "*id" in out:
        raise ValueError(f"{TARGET}: YAML anchors leaked into output")
    return out, changed or out != text


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    parser.add_argument("--path", type=Path, default=TARGET, help="ARO:3003768 YAML file")
    args = parser.parse_args()

    if args.path.name != TARGET.name:
        print(f"PROBLEM: {args.path}: not the ARO:3003768 absence parent", file=sys.stderr)
        return 1
    if not args.path.exists():
        print(f"PROBLEM: {args.path}: missing", file=sys.stderr)
        return 1

    try:
        before = args.path.read_text(encoding="utf-8")
        after, changed = enrich_text(before)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"PROBLEM: {exc}", file=sys.stderr)
        return 1

    if changed:
        print(f"  {'wrote' if args.apply else 'would write'} {args.path.name}")
        if args.apply:
            args.path.write_text(after, encoding="utf-8")

    print(f"{'changed' if args.apply else 'would change'}: {int(changed)}")
    print(f"already enriched: {int(not changed)}")
    if not args.apply:
        print("dry run -- pass --apply to write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
