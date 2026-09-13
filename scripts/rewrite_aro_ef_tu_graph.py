#!/usr/bin/env python3
"""Complete the broad antibiotic-resistant EF-Tu graph.

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
TARGET = ROOT / "data" / "traits" / "function" / "resistance" / "aro" / (
    "antibiotic-resistant-ef-tu-aro3003356.yaml"
)

HISTORY_ACTION = "Completed antibiotic-resistant EF-Tu parent graph"
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

EF_TU_EVIDENCE = {
    "reference": "ARO:3003356",
    "snippet": (
        "Sequence variants of elongation factor Tu that confer resistance to "
        "different classes of antibiotics."
    ),
    "notes": "CARD definition for antibiotic resistant EF-Tu.",
}

ELFAMYCIN_EVIDENCE = {
    "reference": "ARO:3001312",
    "snippet": (
        "Sequence variants of elongation factor Tu that confer resistance to "
        "elfamycin antibiotics."
    ),
    "notes": "CARD definition for the elfamycin-resistant EF-Tu child class.",
}

MUTATION_EVIDENCE = {
    "reference": "ARO:3000212",
    "snippet": (
        "Point mutations in the DNA may lead to an altered gene product that "
        "may result in antibiotic resistance."
    ),
    "notes": "CARD definition for mutation conferring antibiotic resistance.",
}

EF_ACTIVITY_EVIDENCE = {
    "reference": "GO:0003746",
    "snippet": "translation elongation factor activity",
    "notes": "GO molecular-function term used for EF-Tu activity.",
}

ELONGATION_EVIDENCE = {
    "reference": "GO:0006414",
    "snippet": "translational elongation",
    "notes": "GO biological-process term for the pathway served by EF-Tu.",
}

EDGE_DESCRIPTIONS = {
    (
        "determinant",
        "participates in (resistance mechanism)",
        "mech0",
    ): "CARD classifies antibiotic-resistant EF-Tu under mutation-conferring antibiotic resistance.",
    (
        "mech0",
        "causally upstream of",
        "resistance",
    ): "EF-Tu sequence variation is the asserted resistance mechanism for this broad parent.",
    (
        "determinant",
        "causally upstream of (confers resistance)",
        "resistance",
    ): (
        "CARD asserts that sequence variants of EF-Tu confer resistance, but "
        "the broad parent does not specify the drug-binding change."
    ),
    (
        "determinant",
        "enables (elongation factor activity)",
        "ef_activity",
    ): "EF-Tu is a translation elongation factor.",
    (
        "ef_activity",
        "part of (translational elongation)",
        "elongation",
    ): "EF-Tu activity participates in translational elongation.",
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
        case ("determinant", "participates in (resistance mechanism)", "mech0"):
            extra = [EF_TU_EVIDENCE, ELFAMYCIN_EVIDENCE, MUTATION_EVIDENCE]
        case ("mech0", "causally upstream of", "resistance"):
            extra = [EF_TU_EVIDENCE, ELFAMYCIN_EVIDENCE, MUTATION_EVIDENCE]
        case ("determinant", "causally upstream of (confers resistance)", "resistance"):
            extra = [EF_TU_EVIDENCE, ELFAMYCIN_EVIDENCE, MUTATION_EVIDENCE]
        case ("determinant", "enables (elongation factor activity)", "ef_activity"):
            extra = [EF_TU_EVIDENCE, EF_ACTIVITY_EVIDENCE]
        case ("ef_activity", "part of (translational elongation)", "elongation"):
            extra = [EF_TU_EVIDENCE, EF_ACTIVITY_EVIDENCE, ELONGATION_EVIDENCE]
        case _:
            raise ValueError(f"unexpected edge {key}")
    return _unique_evidence(*existing, *extra)


def enrich_record(record: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != "ARO:3003356":
        raise ValueError(f"expected ARO:3003356, found {record.get('identifier')}")

    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1 or graphs[0].get("graph_id") != "resistance":
        raise ValueError("expected exactly one resistance graph")

    out = copy.deepcopy(record)
    graph = copy.deepcopy(out["causal_graphs"][0])
    graph["title"] = "Antibiotic resistant EF-Tu → EF-Tu sequence variation → resistance"
    graph["description"] = (
        "Curated resistance-causation graph for the broad "
        "antibiotic-resistant EF-Tu parent. The graph records the asserted "
        "EF-Tu sequence-variant mechanism and EF-Tu translation role without "
        "claiming one uncited drug-binding mechanism for all children."
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
