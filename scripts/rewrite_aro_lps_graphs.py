#!/usr/bin/env python3
"""Curate intrinsic Lps peptide-antibiotic resistance graphs.

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

HISTORY_ACTION = "Curated intrinsic Lps peptide-antibiotic graph"
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

LPS_PARENT_DEFINITION_EVIDENCE = {
    "reference": "ARO:3005050",
    "snippet": (
        "LpsB is involved in lipopolysaccharide synthesis. It provides "
        "intrinsic resistance to colistin and other peptide antibiotics such "
        "as polymyxins."
    ),
    "notes": "CARD definition for the Intrinsic peptide antibiotic resistant Lps parent.",
}

REDUCED_PERMEABILITY_EVIDENCE = {
    "reference": "ARO:3000244",
    "snippet": (
        "Reduction in permeability to antibiotic, generally through reduced "
        "production of porins, can provide resistance."
    ),
    "notes": "CARD definition for the reduced-permeability resistance mechanism.",
}

LPS_BIOSYNTHESIS_EVIDENCE = {
    "reference": "GO:0009103",
    "snippet": (
        "The chemical reactions and pathways resulting in the formation of "
        "lipopolysaccharides, any of a group of related, structurally complex "
        "components of the outer membrane of Gram-negative bacteria."
    ),
    "notes": "GO definition for lipopolysaccharide biosynthetic process.",
}

LOS_BIOSYNTHESIS_EVIDENCE = {
    "reference": "GO:1901271",
    "snippet": (
        "The chemical reactions and pathways resulting in the formation of "
        "lipooligosaccharide."
    ),
    "notes": "GO definition for lipooligosaccharide biosynthetic process.",
}

PEPTIDE_RELATION_EVIDENCE = {
    "reference": "ARO:3005050",
    "snippet": "confers_resistance_to_drug_class ARO:3000053 ! peptide antibiotic",
    "notes": (
        "ARO drug-class relationship on Intrinsic peptide antibiotic resistant "
        "Lps, materialized into trait_relations and inherited by LpsA and LpsB."
    ),
}

HOOD_LPSB_EVIDENCE = {
    "reference": "PMID:23230287",
    "snippet": "loss of LpsB function results in increased sensitivity to both colistin",
    "notes": (
        "Hood et al. identified Acinetobacter baumannii LpsB as an intrinsic "
        "colistin-tolerance determinant."
    ),
}

MOREY_LPSA_EVIDENCE = {
    "reference": "PMID:23980106",
    "notes": (
        "Morey et al. assayed Haemophilus influenzae lipooligosaccharide "
        "inner- and outer-core mutants, including lpsA."
    ),
}

FOX_LPSA_EVIDENCE = {
    "reference": "PMID:16847057",
    "notes": (
        "Fox et al. characterized Haemophilus influenzae LpsA as a "
        "glycosyltransferase acting on the terminal inner-core heptose."
    ),
}

COLISTIN_REVIEW_EVIDENCE = {
    "reference": "PMID:32284036",
    "notes": (
        "El-Sayed Ahmed et al. reviewed intrinsic and acquired colistin "
        "resistance, including LOS-biosynthesis genes."
    ),
}


@dataclass(frozen=True)
class RecordSpec:
    path: Path
    identifier: str
    label: str
    definition: str
    process_node: dict[str, str]
    process_evidence: dict[str, str]
    literature: tuple[dict[str, str], ...]
    include_parent_definition: bool

    @property
    def definition_evidence(self) -> dict[str, str]:
        return {
            "reference": self.identifier,
            "snippet": self.definition,
            "notes": f"CARD definition for {self.label}.",
        }


LPS_BIOSYNTHESIS_NODE = {
    "node_id": "surface_biosynthesis",
    "label": "lipopolysaccharide biosynthetic process",
    "node_type": "BIOLOGICAL_PROCESS",
    "grounding": "GO:0009103",
}

LOS_BIOSYNTHESIS_NODE = {
    "node_id": "surface_biosynthesis",
    "label": "lipooligosaccharide biosynthetic process",
    "node_type": "BIOLOGICAL_PROCESS",
    "grounding": "GO:1901271",
}

RECORDS = (
    RecordSpec(
        path=ARO / "intrinsic-peptide-antibiotic-resistant-lps-aro3005050.yaml",
        identifier="ARO:3005050",
        label="Intrinsic peptide antibiotic resistant Lps",
        definition=(
            "LpsB is involved in lipopolysaccharide synthesis. It provides "
            "intrinsic resistance to colistin and other peptide antibiotics "
            "such as polymyxins."
        ),
        process_node=LPS_BIOSYNTHESIS_NODE,
        process_evidence=LPS_BIOSYNTHESIS_EVIDENCE,
        literature=(HOOD_LPSB_EVIDENCE,),
        include_parent_definition=False,
    ),
    RecordSpec(
        path=ARO / "lpsb-aro3005051.yaml",
        identifier="ARO:3005051",
        label="LpsB",
        definition=(
            "LpsB is involved in lipopolysaccharide synthesis. It confers "
            "intrinsic resistance to colistin and other peptide antibiotics."
        ),
        process_node=LPS_BIOSYNTHESIS_NODE,
        process_evidence=LPS_BIOSYNTHESIS_EVIDENCE,
        literature=(HOOD_LPSB_EVIDENCE,),
        include_parent_definition=True,
    ),
    RecordSpec(
        path=ARO / "lpsa-aro3005052.yaml",
        identifier="ARO:3005052",
        label="LpsA",
        definition=(
            "LpsA plays a role in Lipooligosaccharide biosynthesis. LpsA "
            "confers resistance to polymyxin antibiotics."
        ),
        process_node=LOS_BIOSYNTHESIS_NODE,
        process_evidence=LOS_BIOSYNTHESIS_EVIDENCE,
        literature=(
            COLISTIN_REVIEW_EVIDENCE,
            FOX_LPSA_EVIDENCE,
            MOREY_LPSA_EVIDENCE,
        ),
        include_parent_definition=True,
    ),
)


EDGE_DESCRIPTIONS = {
    ("determinant", "participates in (resistance mechanism)", "mech0"): (
        "CARD places this LPS/LOS-biosynthesis determinant in the "
        "reduced-permeability resistance mechanism."
    ),
    ("mech0", "causally upstream of", "resistance"): (
        "LPS/LOS biosynthesis contributes to the Gram-negative surface "
        "barrier that underlies intrinsic peptide-antibiotic resistance."
    ),
    ("determinant", "confers resistance to (drug class)", "drug0"): (
        "ARO asserts that the intrinsic Lps branch confers resistance to "
        "peptide antibiotics."
    ),
    ("determinant", "causally upstream of (confers resistance)", "resistance"): (
        "This determinant supports LPS/LOS biosynthesis, preserving a "
        "cell-envelope state that contributes to intrinsic polymyxin "
        "resistance."
    ),
    ("determinant", "participates in (LPS/LOS biosynthesis)", "surface_biosynthesis"): (
        "The encoded Lps protein participates in biosynthesis of the "
        "lipopolysaccharide or lipooligosaccharide surface."
    ),
    ("surface_biosynthesis", "causally upstream of", "resistance"): (
        "LPS/LOS biosynthesis maintains the Gram-negative surface that "
        "supports intrinsic polymyxin tolerance."
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


def _definition_evidence(spec: RecordSpec) -> tuple[dict[str, str], ...]:
    if spec.include_parent_definition:
        return (spec.definition_evidence, LPS_PARENT_DEFINITION_EVIDENCE)
    return (spec.definition_evidence,)


def _edge_evidence(key: tuple[str, str, str], spec: RecordSpec) -> list[dict[str, str]]:
    definitions = _definition_evidence(spec)
    match key:
        case ("determinant", "participates in (resistance mechanism)", "mech0"):
            extra = (
                *definitions,
                REDUCED_PERMEABILITY_EVIDENCE,
                *spec.literature,
            )
        case ("mech0", "causally upstream of", "resistance"):
            extra = (
                *definitions,
                REDUCED_PERMEABILITY_EVIDENCE,
                spec.process_evidence,
                *spec.literature,
            )
        case ("determinant", "confers resistance to (drug class)", "drug0"):
            extra = (
                PEPTIDE_RELATION_EVIDENCE,
                *definitions,
                *spec.literature,
            )
        case ("determinant", "causally upstream of (confers resistance)", "resistance"):
            extra = (
                *definitions,
                spec.process_evidence,
                REDUCED_PERMEABILITY_EVIDENCE,
                *spec.literature,
            )
        case ("determinant", "participates in (LPS/LOS biosynthesis)", "surface_biosynthesis"):
            extra = (
                *definitions,
                spec.process_evidence,
                *spec.literature,
            )
        case ("surface_biosynthesis", "causally upstream of", "resistance"):
            extra = (
                *definitions,
                spec.process_evidence,
                REDUCED_PERMEABILITY_EVIDENCE,
                *spec.literature,
            )
        case _:
            raise ValueError(f"unexpected edge {key}")
    return _unique_evidence(*extra)


def _nodes(spec: RecordSpec) -> list[dict[str, str]]:
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
            "node_id": "drug0",
            "label": "peptide antibiotic",
            "node_type": "CHEMICAL",
            "grounding": "ARO:3000053",
        },
        copy.deepcopy(spec.process_node),
        {
            "node_id": "resistance",
            "label": "antibiotic resistance phenotype",
            "node_type": "PHENOTYPE",
            "grounding": "GO:0046677",
            "description": (
                "Resistance phenotype conferred by Lps-supported intrinsic "
                "peptide-antibiotic tolerance."
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
            "predicate": "confers resistance to (drug class)",
            "predicate_id": "ARO:2000001",
            "object": "drug0",
        },
        {
            "subject": "determinant",
            "predicate": "causally upstream of (confers resistance)",
            "predicate_id": "RO:0002411",
            "object": "resistance",
        },
        {
            "subject": "determinant",
            "predicate": "participates in (LPS/LOS biosynthesis)",
            "predicate_id": "RO:0000056",
            "object": "surface_biosynthesis",
        },
        {
            "subject": "surface_biosynthesis",
            "predicate": "causally upstream of",
            "predicate_id": "RO:0002411",
            "object": "resistance",
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
    return edges


def _graph(spec: RecordSpec) -> dict[str, Any]:
    return {
        "graph_id": "resistance",
        "title": f"{spec.label} → LPS/LOS biosynthesis → peptide-antibiotic resistance",
        "description": (
            "Conservative resistance-causation graph for intrinsic Lps "
            "peptide-antibiotic resistance. The graph replaces the stale porin "
            "influx model with the LPS/LOS-biosynthesis process named by the "
            "record itself."
        ),
        "nodes": _nodes(spec),
        "edges": _edges(spec),
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
