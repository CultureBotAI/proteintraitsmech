#!/usr/bin/env python3
"""Curate fungal nucleobase-transporter 5-flucytosine resistance graphs.

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

HISTORY_ACTION = "Curated fungal nucleobase-transporter 5-flucytosine graph"
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

FUNGAL_NUCLEOBASE_PARENT_EVIDENCE = {
    "reference": "ARO:3007641",
    "snippet": (
        "Fungal nucleobase transporters facilitate the movement of nucleobases "
        "across the fungal cell membrane. The absence confers resistance to "
        "antibiotics by preventing antibiotic entry into the cell."
    ),
    "notes": "CARD definition for fungal nucleobase transporters.",
}

PANTAZOPOULOU_EVIDENCE = {
    "reference": "PMID:17784857",
    "snippet": (
        "genetic, biochemical and molecular data are described concerning "
        "mostly the nucleobase transporters of Aspergillus nidulans and "
        "Saccharomyces cerevisiae"
    ),
    "notes": (
        "Pantazopoulou and Diallinas reviewed fungal nucleobase transporters, "
        "including pathogenic Candida and Aspergillus systems."
    ),
}

GSALLER_EVIDENCE = {
    "reference": "PMID:29610197",
    "snippet": "fcyB, a gene that encodes a purine-cytosine permease",
    "notes": (
        "Gsaller et al. identified Aspergillus fumigatus fcyB as the "
        "pH-regulated 5-flucytosine importer."
    ),
}

PYRIMIDINE_TRANSPORT_EVIDENCE = {
    "reference": "GO:0005350",
    "snippet": (
        "Enables the transfer of pyrimidine nucleobases, one of the two "
        "classes of nitrogen-containing ring compounds found in DNA and RNA, "
        "from one side of a membrane to the other."
    ),
    "notes": "GO definition for pyrimidine nucleobase transmembrane transporter activity.",
}

CYTOSINE_TRANSPORT_EVIDENCE = {
    "reference": "GO:0015209",
    "snippet": (
        "Enables the transfer of cytosine, 4-amino-2-hydroxypyrimidine from "
        "one side of a membrane to the other."
    ),
    "notes": "GO definition for cytosine transmembrane transporter activity.",
}

FLUCYTOSINE_EVIDENCE = {
    "reference": "CHEBI:5100",
    "snippet": "flucytosine",
    "notes": "ChEBI name for CHEBI:5100.",
}

PYRIMIDINE_ANTIFUNGAL_RELATION_EVIDENCE = {
    "reference": "ARO:3007641",
    "snippet": "confers_resistance_to_drug_class ARO:3007560 ! pyrimidine antifungal drug",
    "notes": (
        "ARO drug-class relationship on fungal nucleobase transporters, "
        "materialized into trait_relations and inherited by the child FCY "
        "records."
    ),
}


@dataclass(frozen=True)
class RecordSpec:
    path: Path
    identifier: str
    label: str
    definition: str
    title: str
    transport_node: dict[str, str]
    transport_evidence: dict[str, str]
    parent_evidence: bool = True
    literature_evidence: dict[str, str] | None = None

    @property
    def definition_evidence(self) -> dict[str, str]:
        return {
            "reference": self.identifier,
            "snippet": self.definition,
            "notes": f"CARD definition for {self.label}.",
        }


PYRIMIDINE_TRANSPORT_NODE = {
    "node_id": "transport",
    "label": "pyrimidine nucleobase transmembrane transporter activity",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "GO:0005350",
}

CYTOSINE_TRANSPORT_NODE = {
    "node_id": "transport",
    "label": "cytosine transmembrane transporter activity",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "GO:0015209",
}

RECORDS = (
    RecordSpec(
        path=ARO / "fungal-nucleobase-transporters-aro3007641.yaml",
        identifier="ARO:3007641",
        label="fungal nucleobase transporters",
        definition=(
            "Fungal nucleobase transporters facilitate the movement of "
            "nucleobases across the fungal cell membrane. The absence confers "
            "resistance to antibiotics by preventing antibiotic entry into the "
            "cell."
        ),
        title=(
            "Fungal nucleobase transporter loss → reduced 5-flucytosine "
            "uptake → resistance"
        ),
        transport_node=PYRIMIDINE_TRANSPORT_NODE,
        transport_evidence=PYRIMIDINE_TRANSPORT_EVIDENCE,
        parent_evidence=False,
        literature_evidence=PANTAZOPOULOU_EVIDENCE,
    ),
    RecordSpec(
        path=ARO
        / "aspergillus-spp-fcyb-conferring-resistance-to-5-flucytosine-via-reduced-permeabi-aro3007642.yaml",
        identifier="ARO:3007642",
        label=(
            "Aspergillus spp. fcyB conferring resistance to 5-flucytosine via "
            "reduced permeability"
        ),
        definition=(
            "FcyB encodes for purine-cytosine permease in fungal cells. "
            "Downregulation or absence of fcyB confers resistance to "
            "antibiotics by preventing entry into the cell."
        ),
        title="Aspergillus fcyB loss → reduced 5-flucytosine uptake → resistance",
        transport_node=CYTOSINE_TRANSPORT_NODE,
        transport_evidence=CYTOSINE_TRANSPORT_EVIDENCE,
        literature_evidence=GSALLER_EVIDENCE,
    ),
    RecordSpec(
        path=ARO
        / "candida-spp-fcy2-conferring-resistance-to-5-flucytosine-via-reduced-permeability-aro3007665.yaml",
        identifier="ARO:3007665",
        label=(
            "Candida spp. FCY2 conferring resistance to 5-flucytosine via "
            "reduced permeability"
        ),
        definition=(
            "FCY2 encodes for purine-cytosine permease in fungal cells. "
            "Downregulation or absence of FCY2 confers resistance to "
            "antibiotics by preventing entry into the cell."
        ),
        title="Candida FCY2 loss → reduced 5-flucytosine uptake → resistance",
        transport_node=CYTOSINE_TRANSPORT_NODE,
        transport_evidence=CYTOSINE_TRANSPORT_EVIDENCE,
        literature_evidence=PANTAZOPOULOU_EVIDENCE,
    ),
)


EDGE_DESCRIPTIONS = {
    ("determinant", "participates in (resistance mechanism)", "mech0"): (
        "CARD places the fungal nucleobase-transporter branch in the "
        "reduced-permeability resistance mechanism."
    ),
    ("mech0", "causally upstream of", "resistance"): (
        "Loss or down-regulation of a fungal nucleobase importer reduces "
        "5-flucytosine entry into the cell, producing permeability-mediated "
        "resistance."
    ),
    ("determinant", "causally upstream of (confers resistance)", "resistance"): (
        "This ARO determinant represents absence or down-regulation of the "
        "nucleobase transporter that normally imports 5-flucytosine."
    ),
    ("determinant", "confers resistance to (drug class)", "drug0"): (
        "ARO asserts that fungal nucleobase transporter loss confers "
        "resistance to pyrimidine antifungal drugs."
    ),
    ("determinant", "enables (5-flucytosine uptake)", "transport"): (
        "Wild-type FCY-family transporters import cytosine analogs across the "
        "fungal plasma membrane; reduced transporter activity lowers "
        "5-flucytosine uptake."
    ),
    ("transport", "has input", "flucytosine"): (
        "5-Flucytosine uptake uses the cytosine/pyrimidine nucleobase "
        "transport activity of the encoded fungal permease."
    ),
    ("transport", "negatively regulates (drug uptake counteracts resistance)", "resistance"): (
        "Cytosine permease activity counteracts this reduced-permeability "
        "phenotype by admitting 5-flucytosine into the fungal cell."
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
    if spec.parent_evidence:
        return [
            spec.definition_evidence,
            FUNGAL_NUCLEOBASE_PARENT_EVIDENCE,
            spec.literature_evidence,
        ]
    return [
        spec.definition_evidence,
        spec.literature_evidence,
    ]


def _edge_evidence(key: tuple[str, str, str], spec: RecordSpec) -> list[dict[str, str]]:
    definition_evidence = _definition_evidence(spec)
    match key:
        case ("determinant", "participates in (resistance mechanism)", "mech0"):
            extra = [*definition_evidence, REDUCED_PERMEABILITY_EVIDENCE]
        case ("mech0", "causally upstream of", "resistance"):
            extra = [
                *definition_evidence,
                REDUCED_PERMEABILITY_EVIDENCE,
                spec.transport_evidence,
            ]
        case ("determinant", "causally upstream of (confers resistance)", "resistance"):
            extra = [
                *definition_evidence,
                REDUCED_PERMEABILITY_EVIDENCE,
                FLUCYTOSINE_EVIDENCE,
            ]
        case ("determinant", "confers resistance to (drug class)", "drug0"):
            extra = [
                PYRIMIDINE_ANTIFUNGAL_RELATION_EVIDENCE,
                *definition_evidence,
                FLUCYTOSINE_EVIDENCE,
            ]
        case ("determinant", "enables (5-flucytosine uptake)", "transport"):
            extra = [
                *definition_evidence,
                spec.transport_evidence,
                FLUCYTOSINE_EVIDENCE,
            ]
        case ("transport", "has input", "flucytosine"):
            extra = [
                spec.transport_evidence,
                FLUCYTOSINE_EVIDENCE,
                *definition_evidence,
            ]
        case ("transport", "negatively regulates (drug uptake counteracts resistance)", "resistance"):
            extra = [
                spec.transport_evidence,
                FLUCYTOSINE_EVIDENCE,
                REDUCED_PERMEABILITY_EVIDENCE,
                *definition_evidence,
            ]
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
            "label": "pyrimidine antifungal drug",
            "node_type": "CHEMICAL",
            "grounding": "ARO:3007560",
        },
        copy.deepcopy(spec.transport_node),
        {
            "node_id": "flucytosine",
            "label": "flucytosine",
            "node_type": "CHEMICAL",
            "grounding": "CHEBI:5100",
        },
        {
            "node_id": "resistance",
            "label": "antibiotic resistance phenotype",
            "node_type": "PHENOTYPE",
            "grounding": "GO:0046677",
            "description": (
                "Resistance phenotype conferred by reduced 5-flucytosine "
                "entry into fungal cells."
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
            "predicate": "enables (5-flucytosine uptake)",
            "predicate_id": "RO:0002327",
            "object": "transport",
        },
        {
            "subject": "transport",
            "predicate": "has input",
            "predicate_id": "RO:0002233",
            "object": "flucytosine",
        },
        {
            "subject": "transport",
            "predicate": "negatively regulates (drug uptake counteracts resistance)",
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
        edge["description"] = EDGE_DESCRIPTIONS[key]
        edge["evidence"] = _edge_evidence(key, spec)
    return edges


def _graph(spec: RecordSpec) -> dict[str, Any]:
    return {
        "graph_id": "resistance",
        "title": spec.title,
        "description": (
            "Conservative resistance-causation graph for fungal "
            "nucleobase-transporter loss or down-regulation. The graph "
            "grounds the wild-type cytosine/pyrimidine nucleobase transport "
            "activity that imports 5-flucytosine and represents resistance as "
            "loss of that import route."
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
