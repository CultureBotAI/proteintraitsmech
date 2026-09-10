#!/usr/bin/env python3
"""Curate MgrB/PhoPQ colistin-resistance graphs.

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

HISTORY_ACTION = "Curated MgrB/PhoPQ colistin-resistance graph"
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

RESISTANCE_BY_ABSENCE_EVIDENCE = {
    "reference": "ARO:3003764",
    "snippet": (
        "Mechanism of antibiotic resistance conferred by deletion of gene "
        "(usually a porin)."
    ),
    "notes": "CARD definition for the resistance-by-absence mechanism.",
}

MGRB_PARENT_DEFINITION_EVIDENCE = {
    "reference": "ARO:3007684",
    "snippet": (
        "Mutations in mgrB transmembrane proteins can confer resistance to "
        "the antibiotic colistin."
    ),
    "notes": "CARD definition for transmembrane protein conferring colistin resistance.",
}

PEPTIDE_RELATION_EVIDENCE = {
    "reference": "ARO:3007684",
    "snippet": "relationship: confers_resistance_to_drug_class ARO:3000053 ! peptide antibiotic",
    "notes": (
        "ARO drug-class relationship on transmembrane protein conferring "
        "colistin resistance, materialized into trait_relations and inherited "
        "by mgrB."
    ),
}

MGRB_FAMILY_EVIDENCE = {
    "reference": "NCBIfam:NF007635",
    "snippet": "PhoP/PhoQ regulatory lipoprotein MgrB",
    "notes": "NCBIfam product name for the conserved MgrB protein family.",
}

PHOPQ_EVIDENCE = {
    "reference": "ARO:3000821",
    "snippet": (
        "PhoPQ is a two-component regulatory system. phoP is phosphorylated "
        "by phoQ at a low [mg2+], activating the repressor. Its part of a two "
        "component regulating system that activates the PmrA/B system which "
        "has downstream effects, leading to Antimicrobial resistance in many "
        "pathogens. In Salmonella, phoP bind to macAB ABC transporter and "
        "represses it. In Escherichia coli, phoPQ regulates arnA expression. "
        "In Pseudomonas aeruginosa, phoPQ regulates OprH expression. phoPQ "
        "have other roles in other species."
    ),
    "notes": "CARD definition for phoPQ.",
}

ARA4N_LIPID_A_EVIDENCE = {
    "reference": "GO:1901760",
    "snippet": "beta-L-Ara4N-lipid A biosynthetic process",
    "notes": (
        "GO pathway term for 4-amino-4-deoxy-L-arabinose modification of "
        "Lipid A."
    ),
}

LIPID_A_CHARGE_EVIDENCE = {
    "reference": "ARO:3003588",
    "snippet": (
        "The loss or reduction of the net negative charge within the cell "
        "wall of gram negative bacteria is a mechanism of resistance for "
        "cationic antimicrobials that depend on the negative charge for "
        "binding to the surface."
    ),
    "notes": (
        "CARD's charge-alteration mechanism term; aminoarabinose-modified "
        "Lipid A lowers the negative envelope charge available for colistin "
        "binding."
    ),
}

GUNN_EVIDENCE = {
    "reference": "PMID:9570402",
    "snippet": "lipid A aminoarabinose modification promotes resistance to cationic antimicrobial peptides",
    "notes": (
        "Gunn et al. connect PmrAB-regulated aminoarabinose Lipid A "
        "modification to polymyxin resistance."
    ),
}

POIREL_EVIDENCE = {
    "reference": "PMID:25190723",
    "snippet": (
        "The inactivation or down-regulation of the mgrB gene was shown to "
        "be a source of colistin resistance in K. pneumoniae"
    ),
    "notes": (
        "Poirel et al. identified mgrB inactivation or down-regulation as a "
        "source of acquired colistin resistance in Klebsiella pneumoniae."
    ),
}


@dataclass(frozen=True)
class RecordSpec:
    path: Path
    identifier: str
    label: str
    definition: str
    title: str
    include_parent_definition: bool

    @property
    def definition_evidence(self) -> dict[str, str]:
        return {
            "reference": self.identifier,
            "snippet": self.definition,
            "notes": f"CARD definition for {self.label}.",
        }


RECORDS = (
    RecordSpec(
        path=ARO / "transmembrane-protein-conferring-colistin-resistance-aro3007684.yaml",
        identifier="ARO:3007684",
        label="transmembrane protein conferring colistin resistance",
        definition=(
            "Mutations in mgrB transmembrane proteins can confer resistance "
            "to the antibiotic colistin."
        ),
        title="MgrB loss → PhoPQ derepression → Lipid A remodeling → colistin resistance",
        include_parent_definition=False,
    ),
    RecordSpec(
        path=ARO / "mgrb-aro3003820.yaml",
        identifier="ARO:3003820",
        label="mgrB",
        definition=(
            "mgrB is a small transmembrane protein produced in the PhoPQ "
            "signalling system. It acts as a negative regulator in this "
            "system. Inactivation or down-regulation of mgrB confers "
            "colistin resistance by absence as shown in Klebsiella "
            "pneumoniae."
        ),
        title="mgrB loss → PhoPQ derepression → Lipid A remodeling → colistin resistance",
        include_parent_definition=True,
    ),
)


EDGE_DESCRIPTIONS = {
    ("determinant", "participates in (resistance by absence)", "mech0"): (
        "CARD places this determinant in the resistance-by-absence mechanism."
    ),
    ("determinant", "member of (MgrB family)", "family"): (
        "The determinant is an MgrB-family PhoP/PhoQ regulatory lipoprotein."
    ),
    ("family", "negatively regulates (PhoPQ signaling)", "phopq"): (
        "MgrB-family proteins provide negative feedback to the PhoPQ two-component system."
    ),
    ("phopq", "positively regulates (PmrAB/arn Lipid A remodeling)", "lipid_a_mod"): (
        "PhoPQ signaling is upstream of PmrAB/arn-dependent "
        "4-amino-4-deoxy-L-arabinose modification of Lipid A."
    ),
    ("lipid_a_mod", "causally upstream of", "resistance"): (
        "Ara4N-Lipid A remodeling lowers the net negative charge that cationic "
        "polymyxins require for Gram-negative surface binding."
    ),
    ("mech0", "causally upstream of", "resistance"): (
        "Inactivation or down-regulation of the MgrB negative regulator "
        "confers colistin resistance through resistance by absence."
    ),
    ("determinant", "causally upstream of (confers resistance)", "resistance"): (
        "The ARO determinant denotes MgrB loss or mutation that derepresses "
        "PhoPQ and confers colistin resistance."
    ),
    ("determinant", "confers resistance to (drug class)", "drug0"): (
        "ARO asserts that MgrB transmembrane-protein changes confer "
        "resistance to peptide antibiotics."
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


def _unique_evidence(*items: dict[str, str] | None) -> list[dict[str, str]]:
    evidence: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for item in items:
        if item is None:
            continue
        marker = (item["reference"], item.get("snippet", ""))
        if marker in seen:
            continue
        seen.add(marker)
        evidence.append(copy.deepcopy(item))
    return evidence


def _definition_evidence(spec: RecordSpec) -> list[dict[str, str]]:
    if spec.include_parent_definition:
        return [spec.definition_evidence, MGRB_PARENT_DEFINITION_EVIDENCE]
    return [spec.definition_evidence]


def _edge_evidence(key: tuple[str, str, str], spec: RecordSpec) -> list[dict[str, str]]:
    definition_evidence = _definition_evidence(spec)
    match key:
        case ("determinant", "participates in (resistance by absence)", "mech0"):
            extra = [
                *definition_evidence,
                RESISTANCE_BY_ABSENCE_EVIDENCE,
                POIREL_EVIDENCE,
            ]
        case ("determinant", "member of (MgrB family)", "family"):
            extra = [
                *definition_evidence,
                MGRB_FAMILY_EVIDENCE,
                POIREL_EVIDENCE,
            ]
        case ("family", "negatively regulates (PhoPQ signaling)", "phopq"):
            extra = [
                *definition_evidence,
                MGRB_FAMILY_EVIDENCE,
                PHOPQ_EVIDENCE,
                POIREL_EVIDENCE,
            ]
        case ("phopq", "positively regulates (PmrAB/arn Lipid A remodeling)", "lipid_a_mod"):
            extra = [PHOPQ_EVIDENCE, ARA4N_LIPID_A_EVIDENCE, GUNN_EVIDENCE]
        case ("lipid_a_mod", "causally upstream of", "resistance"):
            extra = [
                ARA4N_LIPID_A_EVIDENCE,
                LIPID_A_CHARGE_EVIDENCE,
                GUNN_EVIDENCE,
                *definition_evidence,
            ]
        case ("mech0", "causally upstream of", "resistance"):
            extra = [
                RESISTANCE_BY_ABSENCE_EVIDENCE,
                *definition_evidence,
                PHOPQ_EVIDENCE,
                POIREL_EVIDENCE,
            ]
        case ("determinant", "causally upstream of (confers resistance)", "resistance"):
            extra = [
                *definition_evidence,
                RESISTANCE_BY_ABSENCE_EVIDENCE,
                PHOPQ_EVIDENCE,
                POIREL_EVIDENCE,
            ]
        case ("determinant", "confers resistance to (drug class)", "drug0"):
            extra = [PEPTIDE_RELATION_EVIDENCE, *definition_evidence, POIREL_EVIDENCE]
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
            "label": "resistance by absence",
            "node_type": "MOLECULAR_FUNCTION",
            "grounding": "ARO:3003764",
        },
        {
            "node_id": "family",
            "label": "PhoP/PhoQ regulatory lipoprotein MgrB",
            "node_type": "PROTEIN",
            "grounding": "NCBIfam:NF007635",
        },
        {
            "node_id": "phopq",
            "label": "phoPQ",
            "node_type": "PROTEIN",
            "grounding": "ARO:3000821",
        },
        {
            "node_id": "lipid_a_mod",
            "label": "beta-L-Ara4N-lipid A biosynthetic process",
            "node_type": "BIOLOGICAL_PROCESS",
            "grounding": "GO:1901760",
        },
        {
            "node_id": "drug0",
            "label": "peptide antibiotic",
            "node_type": "CHEMICAL",
            "grounding": "ARO:3000053",
        },
        {
            "node_id": "resistance",
            "label": "antibiotic resistance phenotype",
            "node_type": "PHENOTYPE",
            "grounding": "GO:0046677",
            "description": "Colistin resistance phenotype mediated by MgrB/PhoPQ signaling.",
        },
    ]


def _edges(spec: RecordSpec) -> list[dict[str, Any]]:
    edges = [
        {
            "subject": "determinant",
            "predicate": "participates in (resistance by absence)",
            "predicate_id": "RO:0000056",
            "object": "mech0",
        },
        {
            "subject": "determinant",
            "predicate": "member of (MgrB family)",
            "predicate_id": "biolink:member_of",
            "object": "family",
        },
        {
            "subject": "family",
            "predicate": "negatively regulates (PhoPQ signaling)",
            "predicate_id": "RO:0002212",
            "object": "phopq",
        },
        {
            "subject": "phopq",
            "predicate": "positively regulates (PmrAB/arn Lipid A remodeling)",
            "predicate_id": "RO:0002213",
            "object": "lipid_a_mod",
        },
        {
            "subject": "lipid_a_mod",
            "predicate": "causally upstream of",
            "predicate_id": "RO:0002411",
            "object": "resistance",
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
        "title": spec.title,
        "description": (
            "Conservative resistance-causation graph for mgrB inactivation or "
            "down-regulation. The graph grounds wild-type MgrB as a negative "
            "regulator of PhoPQ and follows the derepressed PhoPQ branch "
            "toward Ara4N-Lipid A remodeling and colistin resistance."
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
