#!/usr/bin/env python3
"""Curate VanY D,D-carboxypeptidase glycopeptide-resistance graphs.

Dry-run by default; pass ``--apply`` to write.
"""

from __future__ import annotations

import argparse
import copy
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from record_io import append_to_section, replace_block  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ARO = ROOT / "data" / "traits" / "function" / "resistance" / "aro"

HISTORY_ACTION = "Curated VanY D,D-carboxypeptidase glycopeptide graph"
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

VANY_DEFINITION_EVIDENCE = {
    "reference": "ARO:3000077",
    "snippet": (
        "VanY is a D,D-carboxypeptidase that cleaves removes the terminal "
        "D-Ala from peptidoglycan for the addition of D-Lactate."
    ),
    "notes": "CARD definition for vanY.",
}

VANY_ACTIVITY_EVIDENCE = {
    "reference": "PMID:10094630",
    "snippet": (
        "The enzyme was a Zn2+-dependent D,D-carboxypeptidase that cleaved "
        "the C-terminal residue of peptidoglycan precursors ending in "
        "R-D-Ala-D-Ala or R-D-Ala-D-Lac but not the dipeptide D-Ala-D-Ala."
    ),
    "notes": "Arthur et al. 1998 purified and characterized the VanY carboxypeptidase.",
}

VANY_REQUIRED_EVIDENCE = {
    "reference": "PMID:10094630",
    "snippet": (
        "In Enterococcus faecalis, VanY was present in membrane and "
        "cytoplasmic fractions, produced UDP-MurNAc-tetrapeptide from "
        "cytoplasmic peptidoglycan precursors and was required for high-level "
        "glycopeptide resistance in a medium supplemented with D-Ala."
    ),
    "notes": (
        "Arthur et al. 1998 showed that VanY removes a terminal D-Ala and is "
        "conditionally required for high-level resistance."
    ),
}

VANY_SPECIFICITY_EVIDENCE = {
    "reference": "PMID:10094630",
    "snippet": (
        "The specificity constants kcat/Km were 17- to 67-fold higher for "
        "substrates ending in the R-D-Ala-D-Ala target of glycopeptides."
    ),
    "notes": (
        "Arthur et al. 1998 showed that VanY preferentially removes the "
        "glycopeptide-bound D-Ala-D-Ala terminus."
    ),
}

VANX_VANY_DIVISION_EVIDENCE = {
    "reference": "PMID:10094630",
    "snippet": (
        "Thus, VanX and VanY had non-overlapping functions involving the "
        "hydrolysis of D-Ala-D-Ala and the removal of D-Ala from "
        "membrane-bound lipid intermediates respectively."
    ),
    "notes": (
        "Arthur et al. 1998 distinguished the free-dipeptide VanX role from "
        "the lipid-intermediate VanY role."
    ),
}

VANY_FAMILY_EVIDENCE = {
    "reference": "NCBIfam:NF000380",
    "snippet": "D,D-carboxypeptidase/D,D-dipeptidase VanXY",
    "notes": "NCBIfam product name for the VanXY/VanY D,D-carboxypeptidase family.",
}

MOLECULAR_BYPASS_EVIDENCE = {
    "reference": "ARO:3000213",
    "snippet": (
        "Mechanism of antibiotic resistance mediated by circumventing or "
        "bypassing the antibiotic target."
    ),
    "notes": "CARD definition for restructuring of bacterial cell wall.",
}

GLYCOPEPTIDE_RELATION_EVIDENCE = {
    "reference": "ARO:3000077",
    "snippet": "relationship: confers_resistance_to_drug_class ARO:3000081 ! glycopeptide antibiotic",
    "notes": "CARD/ARO asserts this glycopeptide-antibiotic drug class on vanY.",
}


@dataclass(frozen=True)
class RecordSpec:
    path: Path
    identifier: str
    label: str


RECORDS = (
    RecordSpec(
        path=ARO / "vany-aro3000077.yaml",
        identifier="ARO:3000077",
        label="vanY",
    ),
    RecordSpec(
        path=ARO / "vany-gene-in-vana-cluster-aro3002955.yaml",
        identifier="ARO:3002955",
        label="vanY gene in vanA cluster",
    ),
    RecordSpec(
        path=ARO / "vany-gene-in-vanb-cluster-aro3002956.yaml",
        identifier="ARO:3002956",
        label="vanY gene in vanB cluster",
    ),
    RecordSpec(
        path=ARO / "vany-gene-in-vand-cluster-aro3002957.yaml",
        identifier="ARO:3002957",
        label="vanY gene in vanD cluster",
    ),
    RecordSpec(
        path=ARO / "vany-gene-in-vanf-cluster-aro3002958.yaml",
        identifier="ARO:3002958",
        label="vanY gene in vanF cluster",
    ),
    RecordSpec(
        path=ARO / "vany-gene-in-vanm-cluster-aro3002961.yaml",
        identifier="ARO:3002961",
        label="vanY gene in vanM cluster",
    ),
)

EDGE_DESCRIPTIONS = {
    ("determinant", "participates in (resistance mechanism)", "mech0"): (
        "CARD places VanY in the molecular-bypass cell-wall restructuring mechanism."
    ),
    ("mech0", "causally upstream of", "resistance"): (
        "Removing the terminal D-Ala from D-Ala-D-Ala-ended precursors helps "
        "eliminate the glycopeptide-bound peptidoglycan substrate."
    ),
    ("determinant", "causally upstream of (confers resistance)", "resistance"): (
        "VanY raises resistance by preferentially trimming precursors that "
        "end in the glycopeptide target R-D-Ala-D-Ala."
    ),
    ("determinant", "confers resistance to (drug class)", "drug0"): (
        "CARD asserts that VanY confers resistance to glycopeptide antibiotics."
    ),
    ("determinant", "member of (the VanY D,D-carboxypeptidase family)", "family"): (
        "The determinant is a VanY-family D,D-carboxypeptidase."
    ),
    ("family", "enables (Zn2+-dependent D,D-carboxypeptidation)", "carboxypeptidase"): (
        "The VanY-family enzyme cleaves a C-terminal D-Ala from peptidoglycan precursors."
    ),
    ("carboxypeptidase", "has input (cleaves the C-terminal residue)", "dala_dala"): (
        "VanY acts on peptidoglycan precursors ending in an R-D-Ala-D-Ala terminus."
    ),
    ("carboxypeptidase", "negatively regulates (trims)", "dala_dala"): (
        "VanY removes the terminal D-Ala from D-Ala-D-Ala-ended precursors, "
        "eliminating the glycopeptide-binding terminus."
    ),
    ("drug0", "molecularly interacts with (binds the D-Ala-D-Ala terminus)", "dala_dala"): (
        "Glycopeptides bind D-Ala-D-Ala termini in peptidoglycan precursors; "
        "VanY trims those termini from assembled lipid intermediates."
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


def _edge_evidence(key: tuple[str, str, str]) -> list[dict[str, str]]:
    match key:
        case ("determinant", "participates in (resistance mechanism)", "mech0"):
            extra = [VANY_DEFINITION_EVIDENCE, VANY_ACTIVITY_EVIDENCE, MOLECULAR_BYPASS_EVIDENCE]
        case ("mech0", "causally upstream of", "resistance"):
            extra = [
                VANY_DEFINITION_EVIDENCE,
                VANY_REQUIRED_EVIDENCE,
                VANY_SPECIFICITY_EVIDENCE,
                MOLECULAR_BYPASS_EVIDENCE,
            ]
        case ("determinant", "causally upstream of (confers resistance)", "resistance"):
            extra = [
                VANY_DEFINITION_EVIDENCE,
                VANY_REQUIRED_EVIDENCE,
                VANY_SPECIFICITY_EVIDENCE,
            ]
        case ("determinant", "confers resistance to (drug class)", "drug0"):
            extra = [
                GLYCOPEPTIDE_RELATION_EVIDENCE,
                VANY_DEFINITION_EVIDENCE,
                VANY_REQUIRED_EVIDENCE,
            ]
        case ("determinant", "member of (the VanY D,D-carboxypeptidase family)", "family"):
            extra = [VANY_FAMILY_EVIDENCE, VANY_ACTIVITY_EVIDENCE, VANY_DEFINITION_EVIDENCE]
        case ("family", "enables (Zn2+-dependent D,D-carboxypeptidation)", "carboxypeptidase"):
            extra = [VANY_ACTIVITY_EVIDENCE, VANY_FAMILY_EVIDENCE, VANY_DEFINITION_EVIDENCE]
        case ("carboxypeptidase", "has input (cleaves the C-terminal residue)", "dala_dala"):
            extra = [VANY_ACTIVITY_EVIDENCE, VANY_SPECIFICITY_EVIDENCE, VANY_DEFINITION_EVIDENCE]
        case ("carboxypeptidase", "negatively regulates (trims)", "dala_dala"):
            extra = [
                VANY_SPECIFICITY_EVIDENCE,
                VANY_REQUIRED_EVIDENCE,
                VANX_VANY_DIVISION_EVIDENCE,
                VANY_DEFINITION_EVIDENCE,
            ]
        case ("drug0", "molecularly interacts with (binds the D-Ala-D-Ala terminus)", "dala_dala"):
            extra = [VANY_SPECIFICITY_EVIDENCE, VANY_DEFINITION_EVIDENCE]
        case _:
            raise ValueError(f"unexpected edge {key}")
    return _unique_evidence(*extra)


def _graph(spec: RecordSpec) -> dict[str, Any]:
    nodes = [
        {
            "node_id": "determinant",
            "label": spec.label,
            "node_type": "PROTEIN",
            "grounding": spec.identifier,
        },
        {
            "node_id": "mech0",
            "label": "restructuring of bacterial cell wall conferring antibiotic resistance",
            "node_type": "MOLECULAR_FUNCTION",
            "grounding": "ARO:3000213",
        },
        {
            "node_id": "drug0",
            "label": "glycopeptide antibiotic",
            "node_type": "CHEMICAL",
            "grounding": "ARO:3000081",
        },
        {
            "node_id": "family",
            "label": "D,D-carboxypeptidase/D,D-dipeptidase VanXY",
            "node_type": "PROTEIN",
            "grounding": "NCBIfam:NF000380",
            "description": "NCBIfam family containing VanY and VanXY carboxypeptidases.",
        },
        {
            "node_id": "carboxypeptidase",
            "label": "serine-type D-Ala-D-Ala carboxypeptidase activity",
            "node_type": "MOLECULAR_FUNCTION",
            "grounding": "GO:0009002",
        },
        {
            "node_id": "dala_dala",
            "label": "D-alanyl-D-alanine stem-peptide terminus",
            "node_type": "CHEMICAL",
            "grounding": "CHEBI:16576",
            "description": (
                "VanY acts on R-D-Ala-D-Ala termini in peptidoglycan lipid "
                "intermediates; the same D-Ala-D-Ala group is represented by "
                "CHEBI:16576."
            ),
        },
        {
            "node_id": "resistance",
            "label": "glycopeptide antibiotic resistance phenotype",
            "node_type": "PHENOTYPE",
            "grounding": "GO:0046677",
            "description": (
                "Resistance phenotype supported by VanY-dependent removal of "
                "D-Ala-D-Ala termini."
            ),
        },
    ]

    edges = [
        {
            "subject": "determinant",
            "predicate": "participates in (resistance mechanism)",
            "predicate_id": "RO:0000056",
            "object": "mech0",
        },
        {
            "subject": "mech0",
            "predicate": "causally upstream of",
            "predicate_id": "RO:0002411",
            "object": "resistance",
        },
        {
            "subject": "determinant",
            "predicate": "causally upstream of (confers resistance)",
            "predicate_id": "RO:0002411",
            "object": "resistance",
        },
        {
            "subject": "determinant",
            "predicate": "confers resistance to (drug class)",
            "predicate_id": "ARO:2000001",
            "object": "drug0",
        },
        {
            "subject": "determinant",
            "predicate": "member of (the VanY D,D-carboxypeptidase family)",
            "predicate_id": "RO:0002350",
            "object": "family",
        },
        {
            "subject": "family",
            "predicate": "enables (Zn2+-dependent D,D-carboxypeptidation)",
            "predicate_id": "RO:0002327",
            "object": "carboxypeptidase",
        },
        {
            "subject": "carboxypeptidase",
            "predicate": "has input (cleaves the C-terminal residue)",
            "predicate_id": "RO:0002233",
            "object": "dala_dala",
        },
        {
            "subject": "carboxypeptidase",
            "predicate": "negatively regulates (trims)",
            "predicate_id": "RO:0002212",
            "object": "dala_dala",
        },
        {
            "subject": "drug0",
            "predicate": "molecularly interacts with (binds the D-Ala-D-Ala terminus)",
            "predicate_id": "RO:0002436",
            "object": "dala_dala",
        },
    ]

    for edge in edges:
        key = (
            str(edge["subject"]),
            str(edge["predicate"]),
            str(edge["object"]),
        )
        edge["description"] = EDGE_DESCRIPTIONS[key]
        edge["evidence"] = _edge_evidence(key)

    return {
        "graph_id": "resistance",
        "title": f"{spec.label} → terminal D-Ala trimming → glycopeptide resistance",
        "description": (
            "Curated resistance-causation graph for VanY-mediated "
            "glycopeptide resistance. VanY removes terminal D-Ala from "
            "D-Ala-D-Ala-ended peptidoglycan precursors, reducing the "
            "glycopeptide-bound substrate and supporting high-level resistance."
        ),
        "nodes": nodes,
        "edges": edges,
    }


def enrich_record(record: dict[str, Any], spec: RecordSpec) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != spec.identifier:
        raise ValueError(f"expected {spec.identifier}, found {record.get('identifier')}")

    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1 or graphs[0].get("graph_id") != "resistance":
        raise ValueError("expected exactly one resistance graph")

    out = copy.deepcopy(record)
    out["causal_graphs"] = [_graph(spec)]
    return out, out != record


def enrich_text(text: str, spec: RecordSpec) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError("expected a YAML mapping")

    enriched, changed = enrich_record(record, spec)
    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    if HISTORY_ACTION not in out:
        out = append_to_section(out, "curation_history", _dump({"curation_history": [HISTORY_EVENT]}))
        changed = True

    if "&id" in out or "*id" in out:
        raise ValueError("YAML anchors leaked into output")
    return out, changed


def run(apply: bool) -> tuple[int, int]:
    changed_count = 0
    for spec in RECORDS:
        before = spec.path.read_text(encoding="utf-8")
        after, changed = enrich_text(before, spec)
        if changed:
            changed_count += 1
            print(f"  {'wrote' if apply else 'would write'} {spec.path.name}")
            if apply:
                spec.path.write_text(after, encoding="utf-8")
    return changed_count, len(RECORDS) - changed_count


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    args = parser.parse_args(argv)

    changed_count, already = run(args.apply)
    print(f"{'changed' if args.apply else 'would change'}: {changed_count}")
    print(f"already enriched: {already}")
    if not args.apply:
        print("dry run -- pass --apply to write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
