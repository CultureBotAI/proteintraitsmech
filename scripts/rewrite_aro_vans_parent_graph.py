#!/usr/bin/env python3
"""Complete the vanS parent graph.

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
from rewrite_aro_vanr_parent_graph import (  # noqa: E402
    BYPASS_EVIDENCE,
    CELL_WALL_EVIDENCE,
    ENZYME_SYNTHESIS_EVIDENCE,
    NECESSARY_ENZYMES_EVIDENCE,
    PROMOTER_EVIDENCE,
    VANH_EVIDENCE,
    VANR_EVIDENCE,
    VANX_EVIDENCE,
)

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "data" / "traits" / "function" / "resistance" / "aro" / "vans-aro3000071.yaml"

HISTORY_ACTION = "Completed vanS parent regulation graph"
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

VANS_EVIDENCE = {
    "reference": "ARO:3000071",
    "snippet": (
        "VanS is similar to histidine protein kinases like EnvZ and acts as a response "
        "regulator by activating VanR. VanS is required for high level transcription of "
        "other van glycopeptide resistance genes."
    ),
    "notes": "CARD definition for vanS.",
}

GLYCOPEPTIDE_EVIDENCE = {
    "reference": "ARO:3000071",
    "snippet": "relationship: confers_resistance_to_drug_class ARO:3000081 ! glycopeptide antibiotic",
    "notes": (
        "Asserted directly on ARO:3000071 (vanS) in the CARD/ARO release used "
        "for this record."
    ),
}

STIMULATION_EVIDENCE = {
    "reference": "PMID:1556077",
    "snippet": (
        "VanS stimulated VanR-dependent transcription and was related to "
        "membrane-associated histidine protein kinases which control the level of "
        "phosphorylation of response regulators."
    ),
    "notes": "Arthur et al. 1992.",
}

FAMILY_EVIDENCE = {
    "reference": "NCBIfam:NF033091",
    "snippet": "vancomycin resistance histidine kinase VanS",
    "notes": "NCBIfam product name for the profile-HMM family this node grounds to.",
}

SENSOR_KINASE_EVIDENCE = {
    "reference": "GO:0000155",
    "snippet": "phosphorelay sensor kinase activity",
    "notes": "GO molecular-function term used for VanS sensor-kinase activity.",
}

EDGE_DESCRIPTIONS = {
    (
        "determinant",
        "participates in (resistance mechanism)",
        "mech0",
    ): "CARD places VanS in the molecular-bypass pathway that restructures cell-wall precursors.",
    (
        "mech0",
        "causally upstream of",
        "resistance",
    ): "D-Ala-D-Lac or D-Ala-D-Ser precursors lower glycopeptide binding and cause resistance.",
    (
        "determinant",
        "causally upstream of (confers resistance)",
        "resistance",
    ): "VanS confers resistance indirectly by activating VanR-dependent vanHAX transcription.",
    (
        "determinant",
        "confers resistance to (drug class)",
        "drug0",
    ): "CARD asserts that vanS confers resistance to glycopeptide antibiotic.",
    (
        "transcription",
        "positively regulates (cotranscribed from the induced promoter)",
        "vanh_gene",
    ): "The VanR/VanS-regulated promoter cotranscribes vanH.",
    (
        "transcription",
        "positively regulates (cotranscribed from the induced promoter)",
        "vanx_gene",
    ): "The same VanR/VanS-regulated promoter cotranscribes vanX.",
    (
        "vanh_gene",
        "causally upstream of (the mechanism this regulator induces)",
        "resistance",
    ): "VanH supplies D-lactate for the modified precursor that lowers vancomycin binding.",
    (
        "vanx_gene",
        "causally upstream of (the mechanism this regulator induces)",
        "resistance",
    ): "VanX depletes D-Ala-D-Ala so modified peptidoglycan precursors are used.",
    (
        "determinant",
        "member of (the VanS sensor-kinase family)",
        "family",
    ): "VanS is a membrane-associated histidine kinase in the VanS NCBIfam family.",
    (
        "family",
        "enables (sensor histidine kinase phosphorelay)",
        "activity",
    ): "The VanS family has phosphorelay sensor-kinase activity.",
    (
        "activity",
        "positively regulates (phosphorylates the partner regulator)",
        "vanr_protein",
    ): "VanS kinase activity controls VanR phosphorylation and stimulates VanR-dependent transcription.",
    (
        "vanr_protein",
        "causally upstream of (activates the promoter)",
        "transcription",
    ): "VanR is the response regulator that activates the vanHAX promoter.",
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
            extra = [VANS_EVIDENCE, ENZYME_SYNTHESIS_EVIDENCE, BYPASS_EVIDENCE]
        case ("mech0", "causally upstream of", "resistance"):
            extra = [VANS_EVIDENCE, ENZYME_SYNTHESIS_EVIDENCE, CELL_WALL_EVIDENCE]
        case ("determinant", "causally upstream of (confers resistance)", "resistance"):
            extra = [VANS_EVIDENCE, STIMULATION_EVIDENCE, NECESSARY_ENZYMES_EVIDENCE]
        case ("determinant", "confers resistance to (drug class)", "drug0"):
            extra = [GLYCOPEPTIDE_EVIDENCE, CELL_WALL_EVIDENCE]
        case (
            (
                "transcription",
                "positively regulates (cotranscribed from the induced promoter)",
                "vanh_gene" | "vanx_gene",
            )
        ):
            extra = [VANS_EVIDENCE, PROMOTER_EVIDENCE]
        case (
            "vanh_gene",
            "causally upstream of (the mechanism this regulator induces)",
            "resistance",
        ):
            extra = [NECESSARY_ENZYMES_EVIDENCE, VANH_EVIDENCE, CELL_WALL_EVIDENCE]
        case (
            "vanx_gene",
            "causally upstream of (the mechanism this regulator induces)",
            "resistance",
        ):
            extra = [NECESSARY_ENZYMES_EVIDENCE, VANX_EVIDENCE, CELL_WALL_EVIDENCE]
        case ("determinant", "member of (the VanS sensor-kinase family)", "family"):
            extra = [VANS_EVIDENCE, STIMULATION_EVIDENCE, FAMILY_EVIDENCE]
        case ("family", "enables (sensor histidine kinase phosphorelay)", "activity"):
            extra = [VANS_EVIDENCE, STIMULATION_EVIDENCE, FAMILY_EVIDENCE, SENSOR_KINASE_EVIDENCE]
        case (
            "activity",
            "positively regulates (phosphorylates the partner regulator)",
            "vanr_protein",
        ):
            extra = [VANS_EVIDENCE, STIMULATION_EVIDENCE, SENSOR_KINASE_EVIDENCE, VANR_EVIDENCE]
        case (
            "vanr_protein",
            "causally upstream of (activates the promoter)",
            "transcription",
        ):
            extra = [VANS_EVIDENCE, VANR_EVIDENCE, PROMOTER_EVIDENCE]
        case _:
            raise ValueError(f"unexpected edge {key}")
    return _unique_evidence(*existing, *extra)


def enrich_record(record: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != "ARO:3000071":
        raise ValueError(f"expected ARO:3000071, found {record.get('identifier')}")

    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1 or graphs[0].get("graph_id") != "resistance":
        raise ValueError("expected exactly one resistance graph")

    out = copy.deepcopy(record)
    graph = copy.deepcopy(out["causal_graphs"][0])
    graph["title"] = "vanS → VanR-dependent vanHAX transcription → resistance"
    graph["description"] = (
        "Curated resistance-causation graph for the VanS parent sensor kinase. "
        "VanS confers glycopeptide resistance indirectly by activating VanR-dependent "
        "vanHAX transcription, which induces VanH and VanX enzymes that remodel "
        "peptidoglycan precursors."
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
