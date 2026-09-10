#!/usr/bin/env python3
"""Curate VanT serine-racemase glycopeptide-resistance graphs.

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

HISTORY_ACTION = "Curated VanT serine-racemase glycopeptide graph"
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

VANT_PARENT_DEFINITION_EVIDENCE = {
    "reference": "ARO:3000372",
    "snippet": (
        "VanT is a membrane bound serine racemase, converting L-serine to "
        "D-serine. It is associated with VanC, which incorporates D-serine "
        "into D-Ala-D-Ser-ended peptidoglycan subunits with decreased "
        "vancomycin-binding affinity."
    ),
    "notes": "CARD definition for vanT.",
}

VANT_ACTIVITY_EVIDENCE = {
    "reference": "PMID:10209740",
    "snippet": (
        "vanT overexpression in Escherichia coli yielded serine racemase "
        "activity in the membrane fraction rather than in the cytoplasmic "
        "fraction containing alanine racemase."
    ),
    "notes": "Arias et al. 1999 localized VanT serine racemase activity to membranes.",
}

VANT_PATHWAY_EVIDENCE = {
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

DSER_LIGASE_EVIDENCE = {
    "reference": "ARO:3002979",
    "snippet": (
        "A van ligase that synthesizes D-Ala-D-Ser, an alternative "
        "peptidoglycan substrate that confers resistance to vancomycin."
    ),
    "notes": "CARD definition for D-Ala-D-Ser ligase.",
}

SERINE_RACEMASE_REACTION_EVIDENCE = {
    "reference": "RHEA:10980",
    "snippet": "L-serine = D-serine",
    "notes": "Rhea reaction for L-serine/D-serine racemization.",
}

VANT_FAMILY_EVIDENCE = {
    "reference": "NCBIfam:NF033132",
    "snippet": "membrane-bound serine racemase VanT",
    "notes": "NCBIfam product name for the membrane-bound VanT serine-racemase family.",
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
    "reference": "ARO:3000372",
    "snippet": "relationship: confers_resistance_to_drug_class ARO:3000081 ! glycopeptide antibiotic",
    "notes": "CARD/ARO asserts this glycopeptide-antibiotic drug class on vanT.",
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
        path=ARO / "vant-aro3000372.yaml",
        identifier="ARO:3000372",
        label="vanT",
        definition=(
            "VanT is a membrane bound serine racemase, converting L-serine "
            "to D-serine. It is associated with VanC, which incorporated "
            "D-serine into D-Ala-D-Ser terminal end of peptidoglycan subunits "
            "that have a decreased binding affinity with vancomycin. It was "
            "isolated from Enterococcus gallinarum."
        ),
    ),
    RecordSpec(
        path=ARO / "vant-gene-in-vanc-cluster-aro3002970.yaml",
        identifier="ARO:3002970",
        label="vanT gene in vanC cluster",
        definition="Also known as vanTC, is a vanT variant found in the vanC gene cluster.",
    ),
    RecordSpec(
        path=ARO / "vant-gene-in-vane-cluster-aro3002971.yaml",
        identifier="ARO:3002971",
        label="vanT gene in vanE cluster",
        definition="Also known as vanTE, is a vanT variant found in the vanE gene cluster.",
    ),
    RecordSpec(
        path=ARO / "vant-gene-in-vang-cluster-aro3002972.yaml",
        identifier="ARO:3002972",
        label="vanT gene in vanG cluster",
        definition="Also known as vanTG, is a vanT variant found in the vanG gene cluster.",
    ),
    RecordSpec(
        path=ARO / "vant-gene-in-vann-cluster-aro3002975.yaml",
        identifier="ARO:3002975",
        label="vanT gene in vanN cluster",
        definition="Also known as vanTN, is a vanT variant found in the vanN gene cluster.",
    ),
)

EDGE_DESCRIPTIONS = {
    ("determinant", "participates in (resistance mechanism)", "mech0"): (
        "CARD places VanT in the molecular-bypass cell-wall restructuring mechanism."
    ),
    ("mech0", "causally upstream of", "resistance"): (
        "VanT supplies D-serine for D-Ala-D-Ser synthesis, which lets the "
        "VanC-type pathway build low-affinity D-Ala-D-Ser-ended peptidoglycan."
    ),
    ("determinant", "causally upstream of (confers resistance)", "resistance"): (
        "Membrane-bound VanT supports glycopeptide resistance by producing the "
        "D-serine consumed by the D-Ala-D-Ser ligase."
    ),
    ("determinant", "confers resistance to (drug class)", "drug0"): (
        "CARD asserts that VanT confers resistance to glycopeptide antibiotics."
    ),
    ("determinant", "member of (the VanT serine-racemase family)", "family"): (
        "The determinant is a membrane-bound VanT-family serine racemase."
    ),
    ("family", "enables (serine racemization)", "racemase"): (
        "VanT-family proteins enable L-serine/D-serine racemization."
    ),
    ("racemase", "has input", "l_serine"): (
        "VanT uses L-serine as the substrate for D-serine biosynthesis."
    ),
    ("racemase", "has output", "d_serine"): (
        "VanT produces D-serine for the VanC-type peptidoglycan-precursor pathway."
    ),
    ("d_serine", "causally upstream of (is the ligase substrate)", "ligase_gene"): (
        "D-serine is consumed by D-Ala-D-Ser ligase to make the low-affinity "
        "D-Ala-D-Ser precursor terminus."
    ),
    ("ligase_gene", "causally upstream of", "resistance"): (
        "D-Ala-D-Ser ligation downstream of VanT produces the alternative "
        "peptidoglycan substrate that lowers glycopeptide binding."
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
                VANT_PARENT_DEFINITION_EVIDENCE,
                VANT_ACTIVITY_EVIDENCE,
                MOLECULAR_BYPASS_EVIDENCE,
            ]
        case ("mech0", "causally upstream of", "resistance"):
            extra = [
                VANT_PARENT_DEFINITION_EVIDENCE,
                VANT_PATHWAY_EVIDENCE,
                DSER_LIGASE_EVIDENCE,
                MOLECULAR_BYPASS_EVIDENCE,
            ]
        case ("determinant", "causally upstream of (confers resistance)", "resistance"):
            extra = [
                record_definition,
                VANT_PARENT_DEFINITION_EVIDENCE,
                VANT_ACTIVITY_EVIDENCE,
                VANT_PATHWAY_EVIDENCE,
                DSER_LIGASE_EVIDENCE,
            ]
        case ("determinant", "confers resistance to (drug class)", "drug0"):
            extra = [
                GLYCOPEPTIDE_RELATION_EVIDENCE,
                record_definition,
                VANT_PARENT_DEFINITION_EVIDENCE,
                DSER_LIGASE_EVIDENCE,
            ]
        case ("determinant", "member of (the VanT serine-racemase family)", "family"):
            extra = [
                record_definition,
                VANT_PARENT_DEFINITION_EVIDENCE,
                VANT_ACTIVITY_EVIDENCE,
                VANT_FAMILY_EVIDENCE,
            ]
        case ("family", "enables (serine racemization)", "racemase"):
            extra = [
                VANT_ACTIVITY_EVIDENCE,
                VANT_FAMILY_EVIDENCE,
                SERINE_RACEMASE_REACTION_EVIDENCE,
                VANT_PARENT_DEFINITION_EVIDENCE,
            ]
        case ("racemase", "has input", "l_serine"):
            extra = [
                VANT_ACTIVITY_EVIDENCE,
                SERINE_RACEMASE_REACTION_EVIDENCE,
                VANT_PARENT_DEFINITION_EVIDENCE,
            ]
        case ("racemase", "has output", "d_serine"):
            extra = [
                VANT_ACTIVITY_EVIDENCE,
                SERINE_RACEMASE_REACTION_EVIDENCE,
                VANT_PARENT_DEFINITION_EVIDENCE,
                VANT_PATHWAY_EVIDENCE,
            ]
        case ("d_serine", "causally upstream of (is the ligase substrate)", "ligase_gene"):
            extra = [
                VANT_PARENT_DEFINITION_EVIDENCE,
                VANT_PATHWAY_EVIDENCE,
                DSER_LIGASE_EVIDENCE,
            ]
        case ("ligase_gene", "causally upstream of", "resistance"):
            extra = [
                VANT_PARENT_DEFINITION_EVIDENCE,
                VANT_PATHWAY_EVIDENCE,
                DSER_LIGASE_EVIDENCE,
                MOLECULAR_BYPASS_EVIDENCE,
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
            "label": "membrane-bound serine racemase VanT",
            "node_type": "PROTEIN",
            "grounding": "NCBIfam:NF033132",
            "description": "NCBIfam family containing membrane-bound VanT serine racemases.",
        },
        {
            "node_id": "racemase",
            "label": "serine racemase activity",
            "node_type": "MOLECULAR_FUNCTION",
            "grounding": "GO:0030378",
        },
        {
            "node_id": "l_serine",
            "label": "L-serine",
            "node_type": "CHEMICAL",
            "grounding": "CHEBI:33384",
            "description": "Rhea participant in the L-serine/D-serine racemization reaction.",
        },
        {
            "node_id": "d_serine",
            "label": "D-serine",
            "node_type": "CHEMICAL",
            "grounding": "CHEBI:35247",
            "description": "Rhea participant and VanT product consumed by D-Ala-D-Ser ligase.",
        },
        {
            "node_id": "ligase_gene",
            "label": "D-Ala-D-Ser ligase",
            "node_type": "PROTEIN",
            "grounding": "ARO:3002979",
            "description": (
                "D-Ala-D-Ser Van ligase record downstream of VanT-dependent "
                "D-serine production."
            ),
        },
        {
            "node_id": "resistance",
            "label": "glycopeptide antibiotic resistance phenotype",
            "node_type": "PHENOTYPE",
            "grounding": "GO:0046677",
            "description": (
                "Resistance phenotype supported by VanT-dependent D-serine "
                "production for D-Ala-D-Ser peptidoglycan-precursor synthesis."
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
            "predicate": "member of (the VanT serine-racemase family)",
            "predicate_id": "RO:0002350",
            "object": "family",
        },
        {
            "subject": "family",
            "predicate": "enables (serine racemization)",
            "predicate_id": "RO:0002327",
            "object": "racemase",
        },
        {
            "subject": "racemase",
            "predicate": "has input",
            "predicate_id": "RO:0002233",
            "object": "l_serine",
        },
        {
            "subject": "racemase",
            "predicate": "has output",
            "predicate_id": "RO:0002234",
            "object": "d_serine",
        },
        {
            "subject": "d_serine",
            "predicate": "causally upstream of (is the ligase substrate)",
            "predicate_id": "RO:0002411",
            "object": "ligase_gene",
        },
        {
            "subject": "ligase_gene",
            "predicate": "causally upstream of",
            "predicate_id": "RO:0002411",
            "object": "resistance",
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
        "title": f"{spec.label} → VanT D-serine production → glycopeptide resistance",
        "description": (
            "Curated resistance-causation graph for VanT-mediated "
            "glycopeptide resistance. Membrane-bound VanT racemizes L-serine "
            "to D-serine, which is then consumed by D-Ala-D-Ser ligase to "
            "build low-affinity peptidoglycan precursors."
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
