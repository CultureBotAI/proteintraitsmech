#!/usr/bin/env python3
"""Curate E. coli LamB and mipA permeability-loss graphs.

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

HISTORY_ACTION = "Curated E. coli LamB/mipA permeability-loss graph"
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

REDUCED_PERMEABILITY_EVIDENCE = {
    "reference": "ARO:3000244",
    "snippet": (
        "Reduction in permeability to antibiotic, generally through reduced "
        "production of porins, can provide resistance."
    ),
    "notes": "CARD definition for the reduced-permeability resistance mechanism.",
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
        "Nikaido 2003. The Gram-negative outer membrane is a permeability "
        "barrier by default, and channels admit otherwise excluded compounds."
    ),
}

LAMB_RECORD_EVIDENCE = {
    "reference": "ARO:3004126",
    "snippet": (
        "LamB is a negative regulator for antibiotic resistance, it serves as "
        "a porin to influx antibiotic. When down-regulated, it increases "
        "resistance to chlortetracycline, ciprofloxacin, balofloxacin and "
        "nalidixic acid."
    ),
    "notes": "CARD definition for Escherichia coli LamB.",
}

LAMB_LIN_EVIDENCE = {
    "reference": "PMID:24412198",
    "notes": (
        "Lin et al. showed that LamB functions as an antibiotic-influx porin "
        "and that its abundance decreases across resistant E. coli strains."
    ),
}

MIPA_RECORD_EVIDENCE = {
    "reference": "ARO:3004127",
    "snippet": (
        "MltA-interacting protein (mipA), is an antibiotic resistance-related "
        "outer membrane protein. Deletion of mipA increases kanamycin, "
        "nalidixic acid and streptomycin resistance."
    ),
    "notes": "CARD definition for Escherichia coli mipA.",
}

MIPA_LI_EVIDENCE = {
    "reference": "PMID:25940639",
    "notes": (
        "Li et al. identified MipA by outer-membrane proteomics and showed "
        "that mipA deletion raised kanamycin MIC in E. coli."
    ),
}

SUGAR_PORIN_EVIDENCE = {
    "reference": "ARO:3004279",
    "snippet": (
        "Members of the Sugar Porin family tend to facilitate the transport of "
        "maltodextrins and other sugars across the outer membrane of "
        "Gram-negative bacteria."
    ),
    "notes": "CARD definition for the Sugar Porin parent of E. coli LamB.",
}

MIPA_PARENT_EVIDENCE = {
    "reference": "ARO:3004280",
    "snippet": (
        "The MltA-interacting Protein (MipA) family consists mainly of "
        "homologs to MipA and OmpV proteins. Proteins of this family, are "
        "predicted to form a beta-barrel."
    ),
    "notes": "CARD definition for the MipA-interacting Protein parent.",
}


@dataclass(frozen=True)
class DrugClass:
    """An inherited CARD drug-class assertion."""

    node_id: str
    label: str
    grounding: str
    description: str
    evidence: dict[str, str]


@dataclass(frozen=True)
class RecordSpec:
    """Record-specific text and inherited drug-class assertions."""

    path: Path
    identifier: str
    label: str
    title: str
    description: str
    record_evidence: dict[str, str]
    literature_evidence: dict[str, str]
    parent_evidence: dict[str, str]
    drugs: tuple[DrugClass, DrugClass]


LAMB_DRUGS = (
    DrugClass(
        node_id="drug0",
        label="fluoroquinolone antibiotic",
        grounding="ARO:0000001",
        description=(
            "CARD asserts inherited fluoroquinolone resistance from the Sugar "
            "Porin parent; the E. coli LamB definition also names ciprofloxacin "
            "and balofloxacin."
        ),
        evidence={
            "reference": "ARO:3004279",
            "snippet": (
                "relationship: confers_resistance_to_drug_class ARO:0000001 ! "
                "fluoroquinolone antibiotic"
            ),
            "notes": (
                "Asserted on ARO:3004279 (Sugar Porin), an is_a ancestor of "
                "ARO:3004126, in CARD/ARO."
            ),
        },
    ),
    DrugClass(
        node_id="drug1",
        label="tetracycline antibiotic",
        grounding="ARO:3000050",
        description=(
            "CARD asserts inherited tetracycline resistance from the Sugar "
            "Porin parent; the E. coli LamB definition also names "
            "chlortetracycline."
        ),
        evidence={
            "reference": "ARO:3004279",
            "snippet": (
                "relationship: confers_resistance_to_drug_class ARO:3000050 ! "
                "tetracycline antibiotic"
            ),
            "notes": (
                "Asserted on ARO:3004279 (Sugar Porin), an is_a ancestor of "
                "ARO:3004126, in CARD/ARO."
            ),
        },
    ),
)

MIPA_DRUGS = (
    DrugClass(
        node_id="drug0",
        label="fluoroquinolone antibiotic",
        grounding="ARO:0000001",
        description=(
            "CARD asserts inherited fluoroquinolone resistance from the "
            "MipA-interacting Protein parent."
        ),
        evidence={
            "reference": "ARO:3004280",
            "snippet": (
                "relationship: confers_resistance_to_drug_class ARO:0000001 ! "
                "fluoroquinolone antibiotic"
            ),
            "notes": (
                "Asserted on ARO:3004280 (MipA-interacting Protein), an is_a "
                "ancestor of ARO:3004127, in CARD/ARO."
            ),
        },
    ),
    DrugClass(
        node_id="drug1",
        label="aminoglycoside antibiotic",
        grounding="ARO:0000016",
        description=(
            "CARD asserts inherited aminoglycoside resistance from the "
            "MipA-interacting Protein parent; the E. coli mipA definition "
            "names kanamycin and streptomycin."
        ),
        evidence={
            "reference": "ARO:3004280",
            "snippet": (
                "relationship: confers_resistance_to_drug_class ARO:0000016 ! "
                "aminoglycoside antibiotic"
            ),
            "notes": (
                "Asserted on ARO:3004280 (MipA-interacting Protein), an is_a "
                "ancestor of ARO:3004127, in CARD/ARO."
            ),
        },
    ),
)

RECORDS = (
    RecordSpec(
        path=ARO / "escherichia-coli-lamb-aro3004126.yaml",
        identifier="ARO:3004126",
        label="Escherichia coli LamB",
        title="E. coli LamB down-regulation → reduced antibiotic influx → resistance",
        description=(
            "Curated resistance-causation graph for LamB-mediated antibiotic "
            "permeability. LamB is a wild-type maltoporin; its down-regulation "
            "or loss reduces outer-membrane antibiotic entry, producing the "
            "resistance-by-absence phenotype represented by this ARO term."
        ),
        record_evidence=LAMB_RECORD_EVIDENCE,
        literature_evidence=LAMB_LIN_EVIDENCE,
        parent_evidence=SUGAR_PORIN_EVIDENCE,
        drugs=LAMB_DRUGS,
    ),
    RecordSpec(
        path=ARO / "escherichia-coli-mipa-aro3004127.yaml",
        identifier="ARO:3004127",
        label="Escherichia coli mipA",
        title="E. coli mipA deletion → reduced aminoglycoside/quinolone influx → resistance",
        description=(
            "Curated resistance-causation graph for MipA-linked antibiotic "
            "permeability. The determinant is a wild-type outer-membrane "
            "protein; its deletion raises kanamycin, streptomycin, and "
            "nalidixic-acid resistance through reduced permeability."
        ),
        record_evidence=MIPA_RECORD_EVIDENCE,
        literature_evidence=MIPA_LI_EVIDENCE,
        parent_evidence=MIPA_PARENT_EVIDENCE,
        drugs=MIPA_DRUGS,
    ),
)


EDGE_DESCRIPTIONS = {
    ("determinant", "participates in (resistance mechanism)", "mech0"): (
        "CARD places this outer-membrane protein in the reduced-permeability "
        "resistance mechanism."
    ),
    ("mech0", "causally upstream of", "resistance"): (
        "Reduced outer-membrane permeability decreases antibiotic entry and "
        "supports the resistant phenotype."
    ),
    ("determinant", "participates in (resistance mechanism)", "mech1"): (
        "CARD places the missing or down-regulated porin gene product in its "
        "resistance-by-absence mechanism."
    ),
    ("mech1", "causally upstream of", "resistance"): (
        "Loss of an antibiotic-entry route reduces permeability and produces "
        "resistance."
    ),
    ("determinant", "causally upstream of (confers resistance)", "resistance"): (
        "Down-regulation or deletion of this outer-membrane protein is the "
        "record-level resistance determinant."
    ),
    ("determinant", "enables (admits the drug across the membrane)", "influx"): (
        "The wild-type outer-membrane protein contributes to antibiotic entry; "
        "resistance is caused by reducing that entry route."
    ),
    ("influx", "negatively regulates (drug entry counteracts resistance)", "resistance"): (
        "Antibiotic influx counteracts permeability-mediated resistance; "
        "reduced influx is therefore upstream of the resistant phenotype."
    ),
}


def _drug_description(drug: DrugClass) -> str:
    return drug.description


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


def _edge_evidence(
    key: tuple[str, str, str],
    spec: RecordSpec,
    existing: list[dict[str, str]],
) -> list[dict[str, str]]:
    drug_by_id = {drug.node_id: drug for drug in spec.drugs}
    match key:
        case ("determinant", "participates in (resistance mechanism)", "mech0"):
            extra = [
                spec.record_evidence,
                REDUCED_PERMEABILITY_EVIDENCE,
                spec.literature_evidence,
                NIKAIDO_EVIDENCE,
            ]
        case ("mech0", "causally upstream of", "resistance"):
            extra = [
                spec.record_evidence,
                REDUCED_PERMEABILITY_EVIDENCE,
                ABSENCE_PARENT_EVIDENCE,
                spec.literature_evidence,
            ]
        case ("determinant", "participates in (resistance mechanism)", "mech1"):
            extra = [
                spec.record_evidence,
                RESISTANCE_BY_ABSENCE_EVIDENCE,
                ABSENCE_PARENT_EVIDENCE,
            ]
        case ("mech1", "causally upstream of", "resistance"):
            extra = [
                spec.record_evidence,
                RESISTANCE_BY_ABSENCE_EVIDENCE,
                REDUCED_PERMEABILITY_EVIDENCE,
            ]
        case ("determinant", "causally upstream of (confers resistance)", "resistance"):
            extra = [
                spec.record_evidence,
                spec.parent_evidence,
                REDUCED_PERMEABILITY_EVIDENCE,
                spec.literature_evidence,
            ]
        case ("determinant", "enables (admits the drug across the membrane)", "influx"):
            extra = [
                spec.record_evidence,
                spec.parent_evidence,
                NIKAIDO_EVIDENCE,
                spec.literature_evidence,
            ]
        case ("influx", "negatively regulates (drug entry counteracts resistance)", "resistance"):
            extra = [
                spec.record_evidence,
                REDUCED_PERMEABILITY_EVIDENCE,
                ABSENCE_PARENT_EVIDENCE,
                NIKAIDO_EVIDENCE,
            ]
        case ("determinant", "confers resistance to (drug class)", drug_id):
            drug = drug_by_id[drug_id]
            extra = [
                drug.evidence,
                spec.record_evidence,
                spec.parent_evidence,
                REDUCED_PERMEABILITY_EVIDENCE,
            ]
        case _:
            raise ValueError(f"unexpected edge {key}")
    return _unique_evidence(*existing, *extra)


def _nodes(spec: RecordSpec) -> list[dict[str, str]]:
    drug_nodes = [
        {
            "node_id": drug.node_id,
            "label": drug.label,
            "node_type": "CHEMICAL",
            "grounding": drug.grounding,
        }
        for drug in spec.drugs
    ]
    return [
        {
            "node_id": "determinant",
            "label": spec.label,
            "node_type": "PROTEIN",
            "grounding": spec.identifier,
        },
        {
            "node_id": "mech0",
            "label": "reduced permeability to antibiotic",
            "node_type": "MOLECULAR_FUNCTION",
            "grounding": "ARO:3000244",
        },
        {
            "node_id": "mech1",
            "label": "resistance by absence",
            "node_type": "MOLECULAR_FUNCTION",
            "grounding": "ARO:3003764",
        },
        *drug_nodes,
        {
            "node_id": "influx",
            "label": "xenobiotic transport",
            "node_type": "BIOLOGICAL_PROCESS",
            "grounding": "GO:0042908",
            "description": (
                "Wild-type drug influx across the Gram-negative outer membrane; "
                "reduced influx produces the resistance phenotype."
            ),
        },
        {
            "node_id": "resistance",
            "label": "antibiotic resistance phenotype",
            "node_type": "PHENOTYPE",
            "grounding": "GO:0046677",
            "description": (
                "Resistance phenotype conferred by reduced outer-membrane "
                "drug entry."
            ),
        },
    ]


def _edges(spec: RecordSpec) -> list[dict[str, Any]]:
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
            "predicate": "participates in (resistance mechanism)",
            "predicate_id": "RO:0000056",
            "object": "mech1",
        },
        {
            "subject": "mech1",
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
        *[
            {
                "subject": "determinant",
                "predicate": "confers resistance to (drug class)",
                "predicate_id": "ARO:2000001",
                "object": drug.node_id,
                "description": _drug_description(drug),
            }
            for drug in spec.drugs
        ],
        {
            "subject": "determinant",
            "predicate": "enables (admits the drug across the membrane)",
            "predicate_id": "RO:0002327",
            "object": "influx",
        },
        {
            "subject": "influx",
            "predicate": "negatively regulates (drug entry counteracts resistance)",
            "predicate_id": "RO:0002212",
            "object": "resistance",
        },
    ]

    for edge in edges:
        key = (
            str(edge.get("subject")),
            str(edge.get("predicate")),
            str(edge.get("object")),
        )
        if "description" not in edge:
            edge["description"] = EDGE_DESCRIPTIONS[key]
        edge["evidence"] = _edge_evidence(key, spec, _dicts(edge.get("evidence")))
    return edges


def enrich_record(record: dict[str, Any], spec: RecordSpec) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != spec.identifier:
        raise ValueError(f"expected {spec.identifier}, found {record.get('identifier')}")

    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1 or graphs[0].get("graph_id") != "resistance":
        raise ValueError("expected exactly one resistance graph")

    out = copy.deepcopy(record)
    out["causal_graphs"] = [
        {
            "graph_id": "resistance",
            "title": spec.title,
            "description": spec.description,
            "nodes": _nodes(spec),
            "edges": _edges(spec),
        }
    ]
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
