#!/usr/bin/env python3
"""Curate bifunctional VanXY D,D-peptidase glycopeptide-resistance graphs.

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

HISTORY_ACTION = "Curated VanXY bifunctional glycopeptide graph"
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

VANXY_PARENT_DEFINITION_EVIDENCE = {
    "reference": "ARO:3000496",
    "snippet": (
        "VanXY is a protein with both D,D-carboxypeptidase and "
        "D,D-dipeptidase activity, found in Enterococcus gallinarum. It "
        "cleaves and removes the terminal D-Ala of peptidoglycan subunits "
        "for the incorporation of D-Ser by VanC. D-Ala-D-Ser has low "
        "binding affinity with vancomycin."
    ),
    "notes": "CARD definition for vanXY.",
}

VANXY_ACTIVITY_EVIDENCE = {
    "reference": "PMID:10564477",
    "snippet": (
        "The open reading frame downstream from vanC-1 encoded soluble "
        "VanXYC, a 22,318-Da protein with both D,D-dipeptidase and "
        "D,D-carboxypeptidase activities."
    ),
    "notes": "Reynolds et al. 1999 identified the bifunctional VanXYC protein.",
}

VANXY_SPECIFICITY_EVIDENCE = {
    "reference": "PMID:10564477",
    "snippet": (
        "VanXYC had very low dipeptidase activity against D-Ala-D-Ser and "
        "no detectable carboxypeptidase activity against the "
        "D-Ala-D-Ser-ending UDP-MurNAc-pentapeptide."
    ),
    "notes": (
        "Reynolds et al. 1999 showed that VanXYC hydrolyzes "
        "D-Ala-D-Ala-ending substrates while sparing the VanC D-Ser route."
    ),
}

VANXY_PATHWAY_EVIDENCE = {
    "reference": "PMID:10817725",
    "snippet": (
        "In VanC-type enterococci, vanC-1 synthesizes D-Ala-D-Ser, VanXYC "
        "hydrolyzes D-Ala-D-Ala and removes D-Ala from the "
        "UDP-MurNAc-pentapeptide[D-Ala], and VanT supplies D-Ser."
    ),
    "notes": (
        "Arias, Courvalin, and Reynolds 2000 summarized the VanC D-Ser "
        "precursor pathway."
    ),
}

VANXY_SER_PRECURSOR_EVIDENCE = {
    "reference": "PMID:10817725",
    "snippet": (
        "Glycopeptide-resistant enterococci of the VanC type synthesize "
        "UDP-muramyl-pentapeptide[D-Ser] and prevent synthesis of "
        "peptidoglycan precursors ending in D-Ala."
    ),
    "notes": (
        "Arias, Courvalin, and Reynolds 2000 described how the VanC route "
        "replaces glycopeptide-bound D-Ala termini."
    ),
}

VANXY_FAMILY_EVIDENCE = {
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
    "reference": "ARO:3000496",
    "snippet": "relationship: confers_resistance_to_drug_class ARO:3000081 ! glycopeptide antibiotic",
    "notes": "CARD/ARO asserts this glycopeptide-antibiotic drug class on vanXY.",
}


@dataclass(frozen=True)
class RecordSpec:
    path: Path
    identifier: str
    label: str
    definition: str

    @property
    def definition_evidence(self) -> dict[str, str]:
        return {
            "reference": self.identifier,
            "snippet": self.definition,
            "notes": f"CARD definition for {self.label}.",
        }


RECORDS = (
    RecordSpec(
        path=ARO / "vanxy-aro3000496.yaml",
        identifier="ARO:3000496",
        label="vanXY",
        definition=(
            "VanXY is a protein with both D,D-carboxypeptidase and "
            "D,D-dipeptidase activity, found in Enterococcus gallinarum. It "
            "cleaves and removes the terminal D-Ala of peptidoglycan "
            "subunits for the incorporation of D-Ser by VanC. D-Ala-D-Ser "
            "has low binding affinity with vancomycin."
        ),
    ),
    RecordSpec(
        path=ARO / "vanxy-gene-in-vanc-cluster-aro3002966.yaml",
        identifier="ARO:3002966",
        label="vanXY gene in vanC cluster",
        definition="Also known as vanXYC, is a vanXY variant found in the vanC gene cluster.",
    ),
    RecordSpec(
        path=ARO / "vanxy-gene-in-vane-cluster-aro3002967.yaml",
        identifier="ARO:3002967",
        label="vanXY gene in vanE cluster",
        definition="Also known as vanXY, is a vanXY variant found in the vanE gene cluster.",
    ),
    RecordSpec(
        path=ARO / "vanxy-gene-in-vang-cluster-aro3003069.yaml",
        identifier="ARO:3003069",
        label="vanXY gene in vanG cluster",
        definition="Also known as vanXYG, is a vanXY variant found in the vanG gene cluster.",
    ),
    RecordSpec(
        path=ARO / "vanxy-gene-in-vanl-cluster-aro3002968.yaml",
        identifier="ARO:3002968",
        label="vanXY gene in vanL cluster",
        definition="Also known as vanXYL, is a vanXY variant found in the vanL gene cluster.",
    ),
    RecordSpec(
        path=ARO / "vanxy-gene-in-vann-cluster-aro3002969.yaml",
        identifier="ARO:3002969",
        label="vanXY gene in vanN cluster",
        definition="Also known as vanXYN, is a vanXY variant found in the vanN gene cluster.",
    ),
)

EDGE_DESCRIPTIONS = {
    ("determinant", "participates in (resistance mechanism)", "mech0"): (
        "CARD places VanXY in the molecular-bypass cell-wall restructuring mechanism."
    ),
    ("mech0", "causally upstream of", "resistance"): (
        "VanXY depletes the free D-Ala-D-Ala dipeptide and removes terminal "
        "D-Ala residues from D-Ala-D-Ala-ended precursors while the VanC-type "
        "pathway builds low-affinity D-Ala-D-Ser-ended peptidoglycan precursors."
    ),
    ("determinant", "causally upstream of (confers resistance)", "resistance"): (
        "Bifunctional VanXY supports VanC-type glycopeptide resistance by "
        "destroying D-Ala-D-Ala and trimming D-Ala-D-Ala-ending precursors."
    ),
    ("determinant", "confers resistance to (drug class)", "drug0"): (
        "CARD asserts that VanXY confers resistance to glycopeptide antibiotics."
    ),
    ("determinant", "member of (the VanXY bifunctional family)", "family"): (
        "The determinant is a VanXY-family bifunctional D,D-dipeptidase and "
        "D,D-carboxypeptidase."
    ),
    ("family", "enables (D,D-dipeptidase activity)", "dipeptidase"): (
        "The VanXY-family enzyme hydrolyzes the free D-Ala-D-Ala dipeptide."
    ),
    ("family", "enables (D,D-carboxypeptidase activity)", "carboxypeptidase"): (
        "The VanXY-family enzyme also removes the terminal D-Ala from "
        "D-Ala-D-Ala-ending peptidoglycan precursors."
    ),
    ("dipeptidase", "has input (hydrolyses)", "dala_dala"): (
        "VanXY uses free D-Ala-D-Ala as a D,D-dipeptidase substrate."
    ),
    ("dipeptidase", "negatively regulates (depletes)", "dala_dala"): (
        "Hydrolysis depletes free D-Ala-D-Ala, preventing ligation of the "
        "glycopeptide-bound terminus into peptidoglycan precursors."
    ),
    ("carboxypeptidase", "has input (cleaves the C-terminal residue)", "dala_dala"): (
        "VanXY carboxypeptidase activity targets precursors with a terminal "
        "D-Ala-D-Ala group."
    ),
    ("carboxypeptidase", "negatively regulates (removes the terminal D-Ala)", "dala_dala"): (
        "VanXY removes the terminal D-Ala from peptidoglycan precursors that "
        "end in the glycopeptide-bound D-Ala-D-Ala terminus."
    ),
    ("drug0", "molecularly interacts with (binds the D-Ala-D-Ala terminus)", "dala_dala"): (
        "Glycopeptides bind D-Ala-D-Ala termini; VanXY depletes both the free "
        "D-Ala-D-Ala substrate and precursors that expose that terminus."
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


def _edge_evidence(key: tuple[str, str, str], spec: RecordSpec) -> list[dict[str, str]]:
    record_definition = spec.definition_evidence

    match key:
        case ("determinant", "participates in (resistance mechanism)", "mech0"):
            extra = [
                record_definition,
                VANXY_PARENT_DEFINITION_EVIDENCE,
                VANXY_ACTIVITY_EVIDENCE,
                MOLECULAR_BYPASS_EVIDENCE,
            ]
        case ("mech0", "causally upstream of", "resistance"):
            extra = [
                VANXY_PARENT_DEFINITION_EVIDENCE,
                VANXY_PATHWAY_EVIDENCE,
                VANXY_SER_PRECURSOR_EVIDENCE,
                MOLECULAR_BYPASS_EVIDENCE,
            ]
        case ("determinant", "causally upstream of (confers resistance)", "resistance"):
            extra = [
                record_definition,
                VANXY_PARENT_DEFINITION_EVIDENCE,
                VANXY_ACTIVITY_EVIDENCE,
                VANXY_PATHWAY_EVIDENCE,
            ]
        case ("determinant", "confers resistance to (drug class)", "drug0"):
            extra = [
                GLYCOPEPTIDE_RELATION_EVIDENCE,
                record_definition,
                VANXY_PATHWAY_EVIDENCE,
            ]
        case ("determinant", "member of (the VanXY bifunctional family)", "family"):
            extra = [
                record_definition,
                VANXY_PARENT_DEFINITION_EVIDENCE,
                VANXY_ACTIVITY_EVIDENCE,
                VANXY_FAMILY_EVIDENCE,
            ]
        case ("family", "enables (D,D-dipeptidase activity)", "dipeptidase"):
            extra = [
                VANXY_ACTIVITY_EVIDENCE,
                VANXY_FAMILY_EVIDENCE,
                VANXY_PARENT_DEFINITION_EVIDENCE,
            ]
        case ("family", "enables (D,D-carboxypeptidase activity)", "carboxypeptidase"):
            extra = [
                VANXY_ACTIVITY_EVIDENCE,
                VANXY_FAMILY_EVIDENCE,
                VANXY_PARENT_DEFINITION_EVIDENCE,
            ]
        case ("dipeptidase", "has input (hydrolyses)", "dala_dala"):
            extra = [
                VANXY_ACTIVITY_EVIDENCE,
                VANXY_PATHWAY_EVIDENCE,
                VANXY_PARENT_DEFINITION_EVIDENCE,
            ]
        case ("dipeptidase", "negatively regulates (depletes)", "dala_dala"):
            extra = [
                VANXY_ACTIVITY_EVIDENCE,
                VANXY_SPECIFICITY_EVIDENCE,
                VANXY_PATHWAY_EVIDENCE,
                VANXY_PARENT_DEFINITION_EVIDENCE,
            ]
        case ("carboxypeptidase", "has input (cleaves the C-terminal residue)", "dala_dala"):
            extra = [
                VANXY_ACTIVITY_EVIDENCE,
                VANXY_PATHWAY_EVIDENCE,
                VANXY_SPECIFICITY_EVIDENCE,
                VANXY_PARENT_DEFINITION_EVIDENCE,
            ]
        case (
            "carboxypeptidase",
            "negatively regulates (removes the terminal D-Ala)",
            "dala_dala",
        ):
            extra = [
                VANXY_PATHWAY_EVIDENCE,
                VANXY_SPECIFICITY_EVIDENCE,
                VANXY_PARENT_DEFINITION_EVIDENCE,
            ]
        case ("drug0", "molecularly interacts with (binds the D-Ala-D-Ala terminus)", "dala_dala"):
            extra = [
                VANXY_SER_PRECURSOR_EVIDENCE,
                VANXY_PATHWAY_EVIDENCE,
                VANXY_PARENT_DEFINITION_EVIDENCE,
            ]
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
            "description": "NCBIfam family containing VanY and bifunctional VanXY peptidases.",
        },
        {
            "node_id": "dipeptidase",
            "label": "D,D-dipeptidase activity",
            "node_type": "MOLECULAR_FUNCTION",
            "grounding": "GO:0016805",
        },
        {
            "node_id": "carboxypeptidase",
            "label": "serine-type D-Ala-D-Ala carboxypeptidase activity",
            "node_type": "MOLECULAR_FUNCTION",
            "grounding": "GO:0009002",
        },
        {
            "node_id": "dala_dala",
            "label": "D-alanyl-D-alanine",
            "node_type": "CHEMICAL",
            "grounding": "CHEBI:16576",
            "description": (
                "VanXY hydrolyzes free D-Ala-D-Ala and removes the terminal "
                "D-Ala from peptidoglycan precursors ending in the same "
                "D-Ala-D-Ala chemical group."
            ),
        },
        {
            "node_id": "resistance",
            "label": "glycopeptide antibiotic resistance phenotype",
            "node_type": "PHENOTYPE",
            "grounding": "GO:0046677",
            "description": (
                "Resistance phenotype conferred by VanXY-dependent depletion "
                "of D-Ala-D-Ala and D-Ala-D-Ala-ended precursors."
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
            "predicate": "member of (the VanXY bifunctional family)",
            "predicate_id": "RO:0002350",
            "object": "family",
        },
        {
            "subject": "family",
            "predicate": "enables (D,D-dipeptidase activity)",
            "predicate_id": "RO:0002327",
            "object": "dipeptidase",
        },
        {
            "subject": "family",
            "predicate": "enables (D,D-carboxypeptidase activity)",
            "predicate_id": "RO:0002327",
            "object": "carboxypeptidase",
        },
        {
            "subject": "dipeptidase",
            "predicate": "has input (hydrolyses)",
            "predicate_id": "RO:0002233",
            "object": "dala_dala",
        },
        {
            "subject": "dipeptidase",
            "predicate": "negatively regulates (depletes)",
            "predicate_id": "RO:0002212",
            "object": "dala_dala",
        },
        {
            "subject": "carboxypeptidase",
            "predicate": "has input (cleaves the C-terminal residue)",
            "predicate_id": "RO:0002233",
            "object": "dala_dala",
        },
        {
            "subject": "carboxypeptidase",
            "predicate": "negatively regulates (removes the terminal D-Ala)",
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
        edge["evidence"] = _edge_evidence(key, spec)

    return {
        "graph_id": "resistance",
        "title": f"{spec.label} → VanXY D-Ala-D-Ala hydrolysis/trimming → glycopeptide resistance",
        "description": (
            "Curated resistance-causation graph for bifunctional VanXY-mediated "
            "glycopeptide resistance. VanXY hydrolyzes free D-Ala-D-Ala and "
            "removes terminal D-Ala from D-Ala-D-Ala-ended peptidoglycan "
            "precursors while sparing the VanC-type D-Ala-D-Ser route."
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
