#!/usr/bin/env python3
"""Complete the vanR parent graph.

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
TARGET = ROOT / "data" / "traits" / "function" / "resistance" / "aro" / "vanr-aro3000574.yaml"

HISTORY_ACTION = "Completed vanR parent regulation graph"
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

VANR_EVIDENCE = {
    "reference": "ARO:3000574",
    "snippet": (
        "VanR is a OmpR-family transcriptional activator in the VanSR regulatory system. "
        "When activated by VanS, it promotes cotranscription of VanA, VanH, and VanX."
    ),
    "notes": "CARD definition for vanR.",
}

BYPASS_EVIDENCE = {
    "reference": "ARO:3000012",
    "snippet": "Proteins involved in restructuring of the cell wall, causing antibiotic resistance.",
    "notes": "CARD definition for proteins conferring antibiotic resistance via molecular bypass.",
}

CELL_WALL_EVIDENCE = {
    "reference": "ARO:3000213",
    "snippet": (
        "Peptidoglycan precursors ending in D-Ala-D-Lac or D-Ala-D-Ser instead of "
        "D-Ala-D-Ala conferring high level glycopeptide resistance."
    ),
    "notes": "CARD definition for restructuring of bacterial cell wall.",
}

GLYCOPEPTIDE_EVIDENCE = {
    "reference": "ARO:3000574",
    "snippet": "relationship: confers_resistance_to_drug_class ARO:3000081 ! glycopeptide antibiotic",
    "notes": (
        "Asserted directly on ARO:3000574 (vanR) in the CARD/ARO release used "
        "for this record."
    ),
}

PROMOTER_EVIDENCE = {
    "reference": "PMID:1556077",
    "snippet": (
        "Analysis of transcriptional fusions with a reporter gene and RNA mapping indicated "
        "that the VanR-VanS two-component regulatory system activates a promoter used for "
        "cotranscription of the vanH, vanA, and vanX resistance genes."
    ),
    "notes": "Arthur et al. 1992 mapped the VanR/VanS-activated vanHAX promoter.",
}

ENZYME_SYNTHESIS_EVIDENCE = {
    "reference": "PMID:1556077",
    "snippet": (
        "Synthesis of these enzymes was regulated at the transcriptional level by the "
        "VanS-VanR two-component regulatory system encoded by the proximal part of the cluster."
    ),
    "notes": "Arthur et al. 1992.",
}

NECESSARY_ENZYMES_EVIDENCE = {
    "reference": "PMID:1556077",
    "snippet": (
        "The distal part of the van cluster encodes VanH, VanA, and a third enzyme, VanX, "
        "all of which are necessary for resistance."
    ),
    "notes": "Arthur et al. 1992.",
}

VANH_EVIDENCE = {
    "reference": "ARO:3000006",
    "snippet": (
        "VanH is a D-specific alpha-ketoacid dehydrogenase that synthesizes D-lactate. "
        "D-lactate is incorporated into the end of the peptidoglycan subunits, decreasing "
        "vancomycin binding affinity."
    ),
    "notes": "CARD definition for vanH.",
}

VANX_EVIDENCE = {
    "reference": "ARO:3000011",
    "snippet": (
        "VanX is a D,D-dipeptidase that cleaves D-Ala-D-Ala but not D-Ala-D-Lac, ensuring "
        "that the latter dipeptide that has reduced binding affinity with vancomycin is "
        "used to synthesize peptidoglycan substrate."
    ),
    "notes": "CARD definition for vanX.",
}

FAMILY_EVIDENCE = {
    "reference": "NCBIfam:NF033117",
    "snippet": "VanR-ABDEGLN family response regulator transcription factor",
    "notes": "NCBIfam product name for the profile-HMM family this node grounds to.",
}

PHOSPHORELAY_EVIDENCE = {
    "reference": "GO:0000156",
    "snippet": "phosphorelay response regulator activity",
    "notes": "GO molecular-function term used for VanR response-regulator activity.",
}

EDGE_DESCRIPTIONS = {
    (
        "determinant",
        "participates in (resistance mechanism)",
        "mech0",
    ): "CARD places VanR in the molecular-bypass pathway that restructures cell-wall precursors.",
    (
        "mech0",
        "causally upstream of",
        "resistance",
    ): "D-Ala-D-Lac or D-Ala-D-Ser precursors lower glycopeptide binding and cause resistance.",
    (
        "determinant",
        "causally upstream of (confers resistance)",
        "resistance",
    ): "VanR confers resistance indirectly by activating transcription of vanHAX resistance genes.",
    (
        "determinant",
        "confers resistance to (drug class)",
        "drug0",
    ): "CARD asserts that vanR confers resistance to glycopeptide antibiotic.",
    (
        "transcription",
        "positively regulates (cotranscribed from the induced promoter)",
        "vanh_gene",
    ): "VanR/VanS activates a promoter used to cotranscribe vanH.",
    (
        "transcription",
        "positively regulates (cotranscribed from the induced promoter)",
        "vanx_gene",
    ): "VanR/VanS activates the same promoter used to cotranscribe vanX.",
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
        "member of (the VanR response-regulator family)",
        "family",
    ): "VanR is an OmpR-like response regulator in the VanR NCBIfam family.",
    (
        "family",
        "enables (response-regulator phosphorelay)",
        "activity",
    ): "The VanR response-regulator family has phosphorelay response-regulator activity.",
    (
        "activity",
        "causally upstream of (activates the promoter)",
        "transcription",
    ): "VanS-activated VanR phosphorelay activity is upstream of vanHAX promoter activation.",
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
            extra = [VANR_EVIDENCE, ENZYME_SYNTHESIS_EVIDENCE, BYPASS_EVIDENCE]
        case ("mech0", "causally upstream of", "resistance"):
            extra = [VANR_EVIDENCE, ENZYME_SYNTHESIS_EVIDENCE, CELL_WALL_EVIDENCE]
        case ("determinant", "causally upstream of (confers resistance)", "resistance"):
            extra = [VANR_EVIDENCE, PROMOTER_EVIDENCE, NECESSARY_ENZYMES_EVIDENCE]
        case ("determinant", "confers resistance to (drug class)", "drug0"):
            extra = [GLYCOPEPTIDE_EVIDENCE, CELL_WALL_EVIDENCE]
        case (
            (
                "transcription",
                "positively regulates (cotranscribed from the induced promoter)",
                "vanh_gene" | "vanx_gene",
            )
        ):
            extra = [VANR_EVIDENCE, PROMOTER_EVIDENCE]
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
        case ("determinant", "member of (the VanR response-regulator family)", "family"):
            extra = [VANR_EVIDENCE, FAMILY_EVIDENCE]
        case ("family", "enables (response-regulator phosphorelay)", "activity"):
            extra = [VANR_EVIDENCE, FAMILY_EVIDENCE, PHOSPHORELAY_EVIDENCE]
        case (
            "activity",
            "causally upstream of (activates the promoter)",
            "transcription",
        ):
            extra = [VANR_EVIDENCE, PROMOTER_EVIDENCE, PHOSPHORELAY_EVIDENCE]
        case _:
            raise ValueError(f"unexpected edge {key}")
    return _unique_evidence(*existing, *extra)


def enrich_record(record: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != "ARO:3000574":
        raise ValueError(f"expected ARO:3000574, found {record.get('identifier')}")

    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1 or graphs[0].get("graph_id") != "resistance":
        raise ValueError("expected exactly one resistance graph")

    out = copy.deepcopy(record)
    graph = copy.deepcopy(out["causal_graphs"][0])
    graph["title"] = "vanR → VanS-activated vanHAX transcription → resistance"
    graph["description"] = (
        "Curated resistance-causation graph for the VanR parent response regulator. "
        "VanR confers glycopeptide resistance indirectly by activating the vanHAX promoter, "
        "which induces VanH and VanX enzymes that remodel peptidoglycan precursors."
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
