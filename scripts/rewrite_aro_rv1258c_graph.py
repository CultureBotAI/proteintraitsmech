#!/usr/bin/env python3
"""Complete the antibiotic-resistant Rv1258c parent graph.

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
    / "antibiotic-resistant-rv1258c-aro3007183.yaml"
)

HISTORY_ACTION = "Completed antibiotic-resistant Rv1258c parent graph"
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

RV1258C_EVIDENCE = {
    "reference": "ARO:3007183",
    "snippet": "Mutations in the Rv1258c (Tap) efflux pump contributing to antibiotic resistance.",
    "notes": "CARD definition for antibiotic resistant Rv1258c.",
}

MUTATION_EVIDENCE = {
    "reference": "ARO:3000212",
    "snippet": (
        "Point mutations in the DNA may lead to an altered gene product that "
        "may result in antibiotic resistance."
    ),
    "notes": "CARD definition for mutation conferring antibiotic resistance.",
}

EFFLUX_EVIDENCE = {
    "reference": "ARO:0010000",
    "snippet": "Antibiotic resistance via the transport of antibiotics out of the cell.",
    "notes": "CARD definition for the antibiotic efflux resistance mechanism.",
}

EDGE_DESCRIPTIONS = {
    (
        "determinant",
        "participates in (resistance mechanism)",
        "mech0",
    ): "CARD classifies antibiotic-resistant Rv1258c under mutation-conferring resistance.",
    (
        "mech0",
        "causally upstream of",
        "resistance",
    ): "Tap efflux-pump mutations are the asserted cause of antibiotic resistance.",
    (
        "determinant",
        "causally upstream of (confers resistance)",
        "resistance",
    ): (
        "CARD asserts that Rv1258c mutations contribute to resistance, but the "
        "broad parent does not specify a drug class."
    ),
    (
        "determinant",
        "participates in (antibiotic efflux)",
        "efflux_process",
    ): "The Rv1258c determinant is a mutant of the Tap efflux pump.",
    (
        "efflux_process",
        "causally upstream of (confers resistance)",
        "resistance",
    ): "Antibiotic efflux lowers intracellular antibiotic exposure and can produce resistance.",
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


def _unique_evidence(*items: dict[str, str]) -> list[dict[str, str]]:
    evidence: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for item in items:
        marker = (item["reference"], item["snippet"])
        if marker in seen:
            continue
        seen.add(marker)
        evidence.append(copy.deepcopy(item))
    return evidence


def _evidence_for_edge(
    key: tuple[str, str, str], existing: list[dict[str, str]]
) -> list[dict[str, str]]:
    match key:
        case (
            ("determinant", "participates in (resistance mechanism)", "mech0")
            | ("mech0", "causally upstream of", "resistance")
            | ("determinant", "causally upstream of (confers resistance)", "resistance")
        ):
            extra = [RV1258C_EVIDENCE, MUTATION_EVIDENCE, EFFLUX_EVIDENCE]
        case ("determinant", "participates in (antibiotic efflux)", "efflux_process"):
            extra = [RV1258C_EVIDENCE, EFFLUX_EVIDENCE]
        case ("efflux_process", "causally upstream of (confers resistance)", "resistance"):
            extra = [RV1258C_EVIDENCE, EFFLUX_EVIDENCE]
        case _:
            raise ValueError(f"unexpected edge {key}")
    return _unique_evidence(*existing, *extra)


def enrich_record(record: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != "ARO:3007183":
        raise ValueError(f"expected ARO:3007183, found {record.get('identifier')}")

    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1 or graphs[0].get("graph_id") != "resistance":
        raise ValueError("expected exactly one resistance graph")

    out = copy.deepcopy(record)
    graph = copy.deepcopy(out["causal_graphs"][0])
    graph["title"] = "Antibiotic resistant Rv1258c → cautious Tap efflux model → resistance"
    graph["description"] = (
        "Curated resistance-causation graph for the broad antibiotic-resistant "
        "Rv1258c parent. The graph records the Rv1258c/Tap efflux-pump claim "
        "without inheriting the narrower aminoglycoside, isoniazid-like, "
        "polyamine, or pyrazine drug-class assertions from child records."
    )

    seen: set[tuple[str, str, str]] = set()
    for edge in _dicts(graph.get("edges")):
        key = (
            str(edge.get("subject")),
            str(edge.get("predicate")),
            str(edge.get("object")),
        )
        edge["description"] = EDGE_DESCRIPTIONS[key]
        edge["evidence"] = _evidence_for_edge(key, _dicts(edge.get("evidence")))
        seen.add(key)

    missing = sorted(set(EDGE_DESCRIPTIONS) - seen)
    if missing:
        raise ValueError(f"missing edge(s): {missing}")
    out["causal_graphs"] = [graph]
    return out, out != record


def enrich_text(text: str) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError("expected a YAML mapping")

    enriched, changed = enrich_record(record)
    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    if HISTORY_ACTION not in out:
        out = append_to_section(out, "curation_history", _dump({"curation_history": [HISTORY_EVENT]}))
        changed = True

    if "&id" in out or "*id" in out:
        raise ValueError("YAML anchors leaked into output")
    return out, changed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    args = parser.parse_args(argv)

    before = TARGET.read_text(encoding="utf-8")
    after, changed = enrich_text(before)

    if changed:
        print(f"  {'wrote' if args.apply else 'would write'} {TARGET.name}")
        if args.apply:
            TARGET.write_text(after, encoding="utf-8")

    print(f"{'changed' if args.apply else 'would change'}: {int(changed)}")
    print(f"already enriched: {int(not changed)}")
    if not args.apply:
        print("dry run -- pass --apply to write")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
