#!/usr/bin/env python3
"""Curate VanH D-lactate-dehydrogenase glycopeptide-resistance graphs.

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

HISTORY_ACTION = "Curated VanH D-lactate glycopeptide graph"
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

VANH_PARENT_DEFINITION_EVIDENCE = {
    "reference": "ARO:3000006",
    "snippet": (
        "VanH is a D-specific alpha-ketoacid dehydrogenase that synthesizes "
        "D-lactate. D-lactate is incorporated into the end of the "
        "peptidoglycan subunits, decreasing vancomycin binding affinity."
    ),
    "notes": "CARD definition for vanH.",
}

VANH_ACTIVITY_EVIDENCE = {
    "reference": "PMID:1931965",
    "snippet": (
        "purification of VanH to homogeneity, characterization as a "
        "D-specific alpha-keto acid dehydrogenase"
    ),
    "notes": "Bugg et al. purified VanH and assayed its D-specific dehydrogenase activity.",
}

VANH_LIGASE_SUBSTRATE_EVIDENCE = {
    "reference": "PMID:1931965",
    "snippet": (
        "VanA was found to catalyze ester bond formation between D-alanine "
        "and the D-hydroxy acid products of VanH"
    ),
    "notes": "Bugg et al. connected VanH products to Van ligase substrates.",
}

VANH_FAMILY_EVIDENCE = {
    "reference": "NCBIfam:NF000492",
    "snippet": "D-lactate dehydrogenase VanH",
    "notes": "NCBIfam product name for the VanH D-lactate-dehydrogenase family.",
}

D_LACTATE_DEHYDROGENASE_EVIDENCE = {
    "reference": "GO:0008720",
    "snippet": "Catalysis of the reaction: (R)-lactate + NAD+ = H+ + NADH + pyruvate.",
    "notes": "GO definition for D-lactate dehydrogenase (NAD+) activity.",
}

R_LACTATE_EVIDENCE = {
    "reference": "CHEBI:16004",
    "snippet": "(R)-lactate",
    "notes": "ChEBI name for the VanH D-lactate product.",
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
    "reference": "ARO:3000006",
    "snippet": "relationship: confers_resistance_to_drug_class ARO:3000081 ! glycopeptide antibiotic",
    "notes": "CARD/ARO asserts this glycopeptide-antibiotic drug class on vanH.",
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
        path=ARO / "vanh-aro3000006.yaml",
        identifier="ARO:3000006",
        label="vanH",
        definition=(
            "VanH is a D-specific alpha-ketoacid dehydrogenase that "
            "synthesizes D-lactate. D-lactate is incorporated into the end of "
            "the peptidoglycan subunits, decreasing vancomycin binding "
            "affinity."
        ),
    ),
    RecordSpec(
        path=ARO / "vanh-gene-in-vana-cluster-aro3002942.yaml",
        identifier="ARO:3002942",
        label="vanH gene in vanA cluster",
        definition="Also known as vanHA, is a vanH variant in the vanA gene cluster.",
    ),
    RecordSpec(
        path=ARO / "vanh-gene-in-vanb-cluster-aro3002943.yaml",
        identifier="ARO:3002943",
        label="vanH gene in vanB cluster",
        definition="Also known as vanHB, is a vanH variant in the vanB gene cluster.",
    ),
    RecordSpec(
        path=ARO / "vanh-gene-in-vand-cluster-aro3002944.yaml",
        identifier="ARO:3002944",
        label="vanH gene in vanD cluster",
        definition="Also known as vanHD, is a vanH variant in the vanD gene cluster.",
    ),
    RecordSpec(
        path=ARO / "vanh-gene-in-vanf-cluster-aro3002945.yaml",
        identifier="ARO:3002945",
        label="vanH gene in vanF cluster",
        definition="Also known as vanHF, is a vanH variant in the vanF gene cluster.",
    ),
    RecordSpec(
        path=ARO / "vanh-gene-in-vanm-cluster-aro3002947.yaml",
        identifier="ARO:3002947",
        label="vanH gene in vanM cluster",
        definition="Also known as vanHM, is a vanH variant in the vanM gene cluster.",
    ),
    RecordSpec(
        path=ARO / "vanh-gene-in-vano-cluster-aro3002948.yaml",
        identifier="ARO:3002948",
        label="vanH gene in vanO cluster",
        definition="Also known as vanHO, is a vanH variant in the vanO gene cluster.",
    ),
    RecordSpec(
        path=ARO / "vanh-gene-in-vanp-cluster-aro3007188.yaml",
        identifier="ARO:3007188",
        label="vanH gene in vanP cluster",
        definition="vanH variant in the vanP cluster.",
    ),
)


EDGE_DESCRIPTIONS = {
    ("determinant", "participates in (resistance mechanism)", "mech0"): (
        "CARD places VanH in the molecular-bypass cell-wall restructuring mechanism."
    ),
    ("mech0", "causally upstream of", "resistance"): (
        "VanH supplies the D-hydroxy acid substrate used to replace the "
        "glycopeptide-bound D-Ala-D-Ala precursor terminus."
    ),
    ("determinant", "causally upstream of (confers resistance)", "resistance"): (
        "VanH supports glycopeptide resistance by supplying D-lactate for "
        "low-affinity D-Ala-D-Lac precursor synthesis."
    ),
    ("determinant", "confers resistance to (drug class)", "drug0"): (
        "CARD asserts that VanH confers resistance to glycopeptide antibiotics."
    ),
    ("determinant", "member of (the VanH D-lactate-dehydrogenase family)", "family"): (
        "The determinant is a VanH-family D-lactate dehydrogenase."
    ),
    ("family", "enables (D-lactate dehydrogenase activity)", "activity"): (
        "VanH-family proteins reduce alpha-keto acids to D-hydroxy acids."
    ),
    ("activity", "has output", "d_lactate"): (
        "The modeled physiological output of VanH activity is D-lactate."
    ),
    ("d_lactate", "causally upstream of (is the Van ligase substrate)", "mech0"): (
        "Van ligase esterifies D-lactate to D-alanine, bypassing the normal "
        "D-Ala-D-Ala glycopeptide-binding terminus."
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
                VANH_PARENT_DEFINITION_EVIDENCE,
                VANH_ACTIVITY_EVIDENCE,
                MOLECULAR_BYPASS_EVIDENCE,
            ]
        case ("mech0", "causally upstream of", "resistance"):
            extra = [
                VANH_PARENT_DEFINITION_EVIDENCE,
                VANH_LIGASE_SUBSTRATE_EVIDENCE,
                MOLECULAR_BYPASS_EVIDENCE,
                R_LACTATE_EVIDENCE,
            ]
        case ("determinant", "causally upstream of (confers resistance)", "resistance"):
            extra = [
                record_definition,
                VANH_PARENT_DEFINITION_EVIDENCE,
                VANH_ACTIVITY_EVIDENCE,
                VANH_LIGASE_SUBSTRATE_EVIDENCE,
            ]
        case ("determinant", "confers resistance to (drug class)", "drug0"):
            extra = [
                GLYCOPEPTIDE_RELATION_EVIDENCE,
                record_definition,
                VANH_PARENT_DEFINITION_EVIDENCE,
                VANH_ACTIVITY_EVIDENCE,
            ]
        case ("determinant", "member of (the VanH D-lactate-dehydrogenase family)", "family"):
            extra = [
                record_definition,
                VANH_PARENT_DEFINITION_EVIDENCE,
                VANH_ACTIVITY_EVIDENCE,
                VANH_FAMILY_EVIDENCE,
            ]
        case ("family", "enables (D-lactate dehydrogenase activity)", "activity"):
            extra = [
                VANH_FAMILY_EVIDENCE,
                D_LACTATE_DEHYDROGENASE_EVIDENCE,
                VANH_ACTIVITY_EVIDENCE,
            ]
        case ("activity", "has output", "d_lactate"):
            extra = [
                D_LACTATE_DEHYDROGENASE_EVIDENCE,
                R_LACTATE_EVIDENCE,
                VANH_PARENT_DEFINITION_EVIDENCE,
                VANH_ACTIVITY_EVIDENCE,
            ]
        case ("d_lactate", "causally upstream of (is the Van ligase substrate)", "mech0"):
            extra = [
                R_LACTATE_EVIDENCE,
                VANH_PARENT_DEFINITION_EVIDENCE,
                VANH_LIGASE_SUBSTRATE_EVIDENCE,
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
            "label": "D-lactate dehydrogenase VanH",
            "node_type": "PROTEIN",
            "grounding": "NCBIfam:NF000492",
        },
        {
            "node_id": "activity",
            "label": "D-lactate dehydrogenase (NAD+) activity",
            "node_type": "MOLECULAR_FUNCTION",
            "grounding": "GO:0008720",
        },
        {
            "node_id": "d_lactate",
            "label": "(R)-lactate",
            "node_type": "CHEMICAL",
            "grounding": "CHEBI:16004",
        },
        {
            "node_id": "resistance",
            "label": "antibiotic resistance phenotype",
            "node_type": "PHENOTYPE",
            "grounding": "GO:0046677",
            "description": (
                "Resistance phenotype conferred by VanH-supported "
                "D-Ala-D-Lac precursor synthesis."
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
            "predicate": "member of (the VanH D-lactate-dehydrogenase family)",
            "predicate_id": "RO:0002350",
            "object": "family",
        },
        {
            "subject": "family",
            "predicate": "enables (D-lactate dehydrogenase activity)",
            "predicate_id": "RO:0002327",
            "object": "activity",
        },
        {
            "subject": "activity",
            "predicate": "has output",
            "predicate_id": "RO:0002234",
            "object": "d_lactate",
        },
        {
            "subject": "d_lactate",
            "predicate": "causally upstream of (is the Van ligase substrate)",
            "predicate_id": "RO:0002411",
            "object": "mech0",
        },
    ]

    for edge in edges:
        key = (
            str(edge.get("subject")),
            str(edge.get("predicate")),
            str(edge.get("object")),
        )
        edge["description"] = EDGE_DESCRIPTIONS[key]
        edge["evidence"] = _edge_evidence(key, spec)

    return {
        "graph_id": "resistance",
        "title": f"{spec.label} → D-lactate synthesis → glycopeptide resistance",
        "description": (
            "Curated resistance-causation graph for VanH glycopeptide "
            "resistance. The graph grounds the VanH family and its D-lactate "
            "dehydrogenase activity while avoiding ungrounded local precursor "
            "and vancomycin-complex states."
        ),
        "nodes": nodes,
        "edges": edges,
    }


def enrich_record(record: dict[str, Any], spec: RecordSpec) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != spec.identifier:
        raise ValueError(f"expected {spec.identifier}, found {record.get('identifier')}")
    if len(_dicts(record.get("causal_graphs"))) != 1:
        raise ValueError(f"{spec.identifier}: expected exactly one causal graph")

    out = copy.deepcopy(record)
    before = copy.deepcopy(out["causal_graphs"])
    out["causal_graphs"] = [_graph(spec)]
    return out, out["causal_graphs"] != before


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
