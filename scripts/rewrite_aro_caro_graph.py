#!/usr/bin/env python3
"""Complete the carO permeability-loss graph.

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
TARGET = ROOT / "data" / "traits" / "function" / "resistance" / "aro" / "caro-aro3003808.yaml"

HISTORY_ACTION = "Completed carO permeability-loss graph"
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

CARO_EVIDENCE = {
    "reference": "ARO:3003808",
    "snippet": (
        "carO is a transmembrane beta-barrel involved in the influx of "
        "carbapenem antibiotics in Acinetobacter baumannii. Disruption of the "
        "carO gene by distinct insertion elements results in a loss of carO "
        "expression causing resistance to carbapenem antibiotics. Homologs of "
        "carO have been identified in genera Acinetobacter, Moraxella and "
        "Psychrobacter."
    ),
    "notes": "CARD definition for carO.",
}

CARO_PORIN_EVIDENCE = {
    "reference": "ARO:3004283",
    "snippet": (
        "The imipenum resistance-associated CarO porin family is composed of "
        "the CarO porin originally identified in Acinetobacter baumannii. The "
        "loss of these porins is associated with imipenem and meropenem "
        "multi-drug resistance. The channels formed by CarO porins show "
        "slight cation selectivity."
    ),
    "notes": "CARD definition for the CarO porin parent.",
}

REDUCED_PERMEABILITY_EVIDENCE = {
    "reference": "ARO:3000244",
    "snippet": (
        "Reduction in permeability to antibiotic, generally through reduced "
        "production of porins, can provide resistance."
    ),
    "notes": "CARD definition for reduced permeability to antibiotic.",
}

RESISTANCE_BY_ABSENCE_EVIDENCE = {
    "reference": "ARO:3003764",
    "snippet": "Mechanism of antibiotic resistance conferred by deletion of gene (usually a porin).",
    "notes": "CARD definition for the resistance-by-absence mechanism.",
}

ABSENCE_PARENT_EVIDENCE = {
    "reference": "ARO:3003768",
    "snippet": (
        "Deletion of gene or gene product results in resistance. For example, "
        "deletion of a porin gene blocks drug from entering the cell."
    ),
    "notes": "CARD definition for the broader gene-conferring-resistance-via-absence branch.",
}

NIKAIDO_EVIDENCE = {
    "reference": "PMID:14665678",
    "snippet": (
        "Although outer membrane components often play important roles in the "
        "interaction of symbiotic or pathogenic bacteria with their host "
        "organisms, the major role of this membrane must usually be to serve "
        "as a permeability barrier to prevent the entry of noxious compounds "
        "and at the same time to allow the influx of nutrient molecules."
    ),
    "notes": (
        "Nikaido 2003. The outer membrane is a permeability barrier by "
        "default; channels are what let a drug across it, so losing a channel "
        "raises the barrier."
    ),
}

EDGE_DESCRIPTIONS = {
    (
        "determinant",
        "participates in (resistance mechanism)",
        "mech0",
    ): "CARD places carO in the reduced-permeability resistance mechanism.",
    (
        "mech0",
        "causally upstream of",
        "resistance",
    ): "Reduced CarO-mediated permeability keeps carbapenems from entering the cell.",
    (
        "determinant",
        "participates in (resistance mechanism)",
        "mech1",
    ): "carO disruption is a resistance-by-absence mechanism.",
    (
        "mech1",
        "causally upstream of",
        "resistance",
    ): "Loss of CarO expression removes a carbapenem influx route and causes resistance.",
    (
        "determinant",
        "causally upstream of (confers resistance)",
        "resistance",
    ): "Disrupting carO expression causes carbapenem resistance by blocking drug influx.",
    (
        "determinant",
        "confers resistance to (drug class)",
        "drug0",
    ): "CARD asserts inherited carbapenem resistance from the CarO porin parent.",
    (
        "determinant",
        "enables (admits the drug across the membrane)",
        "influx",
    ): "CarO is an outer-membrane channel involved in carbapenem influx.",
    (
        "barrier",
        "negatively regulates (the membrane excludes what has no channel)",
        "influx",
    ): "The outer membrane permeability barrier prevents influx when a channel is absent.",
    (
        "influx",
        "causally upstream of (the drug reaches its target)",
        "drug0",
    ): "Carbapenems have to cross the membrane through channels such as CarO to reach their targets.",
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
        marker = (item["reference"], item.get("snippet", ""))
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
            extra = [CARO_EVIDENCE, REDUCED_PERMEABILITY_EVIDENCE, NIKAIDO_EVIDENCE]
        case ("mech0", "causally upstream of", "resistance"):
            extra = [CARO_EVIDENCE, REDUCED_PERMEABILITY_EVIDENCE, NIKAIDO_EVIDENCE]
        case ("determinant", "participates in (resistance mechanism)", "mech1"):
            extra = [CARO_EVIDENCE, RESISTANCE_BY_ABSENCE_EVIDENCE, ABSENCE_PARENT_EVIDENCE]
        case ("mech1", "causally upstream of", "resistance"):
            extra = [CARO_EVIDENCE, RESISTANCE_BY_ABSENCE_EVIDENCE, ABSENCE_PARENT_EVIDENCE]
        case ("determinant", "causally upstream of (confers resistance)", "resistance"):
            extra = [
                CARO_EVIDENCE,
                CARO_PORIN_EVIDENCE,
                REDUCED_PERMEABILITY_EVIDENCE,
                ABSENCE_PARENT_EVIDENCE,
            ]
        case ("determinant", "confers resistance to (drug class)", "drug0"):
            extra = [CARO_EVIDENCE, CARO_PORIN_EVIDENCE]
        case ("determinant", "enables (admits the drug across the membrane)", "influx"):
            extra = [CARO_EVIDENCE, CARO_PORIN_EVIDENCE, REDUCED_PERMEABILITY_EVIDENCE]
        case (
            "barrier",
            "negatively regulates (the membrane excludes what has no channel)",
            "influx",
        ):
            extra = [NIKAIDO_EVIDENCE, REDUCED_PERMEABILITY_EVIDENCE, ABSENCE_PARENT_EVIDENCE]
        case ("influx", "causally upstream of (the drug reaches its target)", "drug0"):
            extra = [CARO_EVIDENCE, CARO_PORIN_EVIDENCE, NIKAIDO_EVIDENCE]
        case _:
            raise ValueError(f"unexpected edge {key}")
    return _unique_evidence(*existing, *extra)


def enrich_record(record: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != "ARO:3003808":
        raise ValueError(f"expected ARO:3003808, found {record.get('identifier')}")

    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1 or graphs[0].get("graph_id") != "resistance":
        raise ValueError("expected exactly one resistance graph")

    out = copy.deepcopy(record)
    graph = copy.deepcopy(out["causal_graphs"][0])
    graph["title"] = "carO loss → reduced carbapenem influx → resistance"
    graph["description"] = (
        "Curated resistance-causation graph for CarO-mediated carbapenem "
        "influx. Disruption of carO expression removes the porin route that "
        "admits carbapenems across the outer-membrane permeability barrier."
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
