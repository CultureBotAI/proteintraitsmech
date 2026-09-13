#!/usr/bin/env python3
"""Curate HOG1/SAPK echinocandin-resistance graphs.

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

HISTORY_ACTION = "Curated HOG1/SAPK echinocandin-resistance graph"
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

SAPK_PARENT_DEFINITION_EVIDENCE = {
    "reference": "ARO:3007663",
    "snippet": (
        "Stress-activated protein kinases (SAPK) are kinases involved in "
        "cellular response to stress whose absence confers resistance to "
        "antifungal drug compounds."
    ),
    "notes": "CARD definition for stress-activated protein kinases.",
}

ECHINOCANDIN_RELATION_EVIDENCE = {
    "reference": "ARO:3007663",
    "snippet": (
        "relationship: confers_resistance_to_drug_class ARO:3007496 ! "
        "echinocandin antibiotic"
    ),
    "notes": (
        "ARO drug-class relationship on stress-activated protein kinases, "
        "materialized into trait_relations and inherited by HOG1."
    ),
}

MAPK_ACTIVITY_EVIDENCE = {
    "reference": "GO:0004707",
    "snippet": "Catalysis of the reaction: protein + ATP = protein phosphate + ADP.",
    "notes": (
        "GO definition for MAP kinase activity; stress-activated protein "
        "kinase activity is a narrow synonym of this term."
    ),
}

CELL_WALL_ORGANIZATION_EVIDENCE = {
    "reference": "GO:0071555",
    "snippet": (
        "A process that results in the assembly, arrangement of constituent "
        "parts, or disassembly of the cell wall"
    ),
    "notes": (
        "Nearest broad GO process for a HOG1-dependent change in how chitin "
        "is arranged or exposed in the fungal cell wall."
    ),
}

HOG1_LITERATURE_EVIDENCE = {
    "reference": "PMID:30355673",
    "notes": (
        "Day et al. studied HOG1 deletion and cell-wall-drug resistance in "
        "Candida auris; this is CARD's citation for the HOG1/SAPK ARO branch."
    ),
}


@dataclass(frozen=True)
class RecordSpec:
    path: Path
    identifier: str
    label: str
    definition: str
    title: str
    description: str
    include_parent_definition: bool
    include_exposed_chitin: bool

    @property
    def definition_evidence(self) -> dict[str, str]:
        return {
            "reference": self.identifier,
            "snippet": self.definition,
            "notes": f"CARD definition for {self.label}.",
        }


RECORDS = (
    RecordSpec(
        path=ARO / "stress-activated-protein-kinases-aro3007663.yaml",
        identifier="ARO:3007663",
        label="stress-activated protein kinases",
        definition=(
            "Stress-activated protein kinases (SAPK) are kinases involved in "
            "cellular response to stress whose absence confers resistance to "
            "antifungal drug compounds."
        ),
        title="SAPK loss → echinocandin resistance",
        description=(
            "Conservative resistance-causation graph for the CARD "
            "stress-activated protein kinase parent. The graph grounds the "
            "wild-type kinase activity and the resistance-by-absence "
            "mechanism without asserting the HOG1-specific chitin-exposure "
            "route for every SAPK."
        ),
        include_parent_definition=False,
        include_exposed_chitin=False,
    ),
    RecordSpec(
        path=ARO
        / "candida-spp-high-osmolarity-glycerol-1-conferring-resistance-to-caspofungin-via--aro3007664.yaml",
        identifier="ARO:3007664",
        label=(
            "Candida spp. High Osmolarity Glycerol 1 conferring resistance "
            "to caspofungin via absence"
        ),
        definition=(
            "Hog1 is a stress-activated protein kinase. Deletion of Hog1 "
            "confers resistance to caspofungin through increase in exposed "
            "chitin levels in the cell wall."
        ),
        title="HOG1 loss → exposed cell-wall chitin → caspofungin resistance",
        description=(
            "HOG1-specific resistance-causation graph. The graph represents "
            "wild-type HOG1 as a MAP kinase whose absence increases exposed "
            "cell-wall chitin and uses that exposed-chitin state as the "
            "curated route from loss of HOG1 to caspofungin resistance."
        ),
        include_parent_definition=True,
        include_exposed_chitin=True,
    ),
)


EDGE_DESCRIPTIONS = {
    ("determinant", "participates in (resistance by absence)", "mech0"): (
        "CARD places this determinant in the resistance-by-absence mechanism."
    ),
    ("determinant", "enables (wild-type MAP kinase activity)", "mapk_activity"): (
        "The encoded wild-type stress-activated protein kinase enables MAP "
        "kinase activity."
    ),
    ("mapk_activity", "negatively regulates (loss-state resistance)", "resistance"): (
        "The parent term states that absence of stress-activated protein "
        "kinases confers antifungal resistance, so the wild-type kinase "
        "activity counteracts the resistance state modeled for SAPK loss."
    ),
    (
        "mapk_activity",
        "negatively regulates (exposed-chitin cell-wall organization)",
        "cell_wall_organization",
    ): (
        "CARD states that Hog1 deletion confers resistance through increased "
        "exposed chitin in the cell wall; the graph represents this loss "
        "statement as wild-type HOG1 activity limiting the cell-wall "
        "organization state that exposes more chitin."
    ),
    (
        "cell_wall_organization",
        "causally upstream of (caspofungin resistance)",
        "resistance",
    ): (
        "The HOG1 child term links cell-wall chitin exposure to the "
        "caspofungin-resistance phenotype."
    ),
    ("mech0", "causally upstream of", "resistance"): (
        "Deletion of the SAPK gene or gene product confers antifungal "
        "resistance."
    ),
    ("determinant", "causally upstream of (confers resistance)", "resistance"): (
        "This ARO determinant denotes SAPK/HOG1 loss and links that loss to "
        "an echinocandin-resistance phenotype."
    ),
    ("determinant", "confers resistance to (drug class)", "drug0"): (
        "ARO asserts that absence of this SAPK branch confers resistance to "
        "echinocandin antibiotics."
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
        return [spec.definition_evidence, SAPK_PARENT_DEFINITION_EVIDENCE]
    return [spec.definition_evidence]


def _edge_evidence(key: tuple[str, str, str], spec: RecordSpec) -> list[dict[str, str]]:
    definition_evidence = _definition_evidence(spec)
    match key:
        case ("determinant", "participates in (resistance by absence)", "mech0"):
            extra = [
                *definition_evidence,
                RESISTANCE_BY_ABSENCE_EVIDENCE,
                HOG1_LITERATURE_EVIDENCE,
            ]
        case ("determinant", "enables (wild-type MAP kinase activity)", "mapk_activity"):
            extra = [*definition_evidence, MAPK_ACTIVITY_EVIDENCE, HOG1_LITERATURE_EVIDENCE]
        case ("mapk_activity", "negatively regulates (loss-state resistance)", "resistance"):
            extra = [
                MAPK_ACTIVITY_EVIDENCE,
                *definition_evidence,
                RESISTANCE_BY_ABSENCE_EVIDENCE,
                HOG1_LITERATURE_EVIDENCE,
            ]
        case (
            "mapk_activity",
            "negatively regulates (exposed-chitin cell-wall organization)",
            "cell_wall_organization",
        ):
            extra = [
                MAPK_ACTIVITY_EVIDENCE,
                CELL_WALL_ORGANIZATION_EVIDENCE,
                *definition_evidence,
                HOG1_LITERATURE_EVIDENCE,
            ]
        case (
            "cell_wall_organization",
            "causally upstream of (caspofungin resistance)",
            "resistance",
        ):
            extra = [
                CELL_WALL_ORGANIZATION_EVIDENCE,
                *definition_evidence,
                HOG1_LITERATURE_EVIDENCE,
            ]
        case ("mech0", "causally upstream of", "resistance"):
            extra = [
                RESISTANCE_BY_ABSENCE_EVIDENCE,
                *definition_evidence,
                HOG1_LITERATURE_EVIDENCE,
            ]
        case ("determinant", "causally upstream of (confers resistance)", "resistance"):
            extra = [
                *definition_evidence,
                RESISTANCE_BY_ABSENCE_EVIDENCE,
                HOG1_LITERATURE_EVIDENCE,
            ]
        case ("determinant", "confers resistance to (drug class)", "drug0"):
            extra = [
                ECHINOCANDIN_RELATION_EVIDENCE,
                *definition_evidence,
                HOG1_LITERATURE_EVIDENCE,
            ]
        case _:
            raise ValueError(f"unexpected edge {key}")
    return _unique_evidence(*extra)


def _nodes(spec: RecordSpec) -> list[dict[str, str]]:
    nodes = [
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
            "node_id": "mapk_activity",
            "label": "MAP kinase activity",
            "node_type": "MOLECULAR_FUNCTION",
            "grounding": "GO:0004707",
        },
    ]
    if spec.include_exposed_chitin:
        nodes.append(
            {
                "node_id": "cell_wall_organization",
                "label": "cell wall organization",
                "node_type": "BIOLOGICAL_PROCESS",
                "grounding": "GO:0071555",
                "description": (
                    "Nearest GO process for the resistance-mediating HOG1-deletion "
                    "state; CARD specifies increased exposed chitin in the cell wall."
                ),
            }
        )
    nodes.extend(
        [
            {
                "node_id": "drug0",
                "label": "echinocandin antibiotic",
                "node_type": "CHEMICAL",
                "grounding": "ARO:3007496",
            },
            {
                "node_id": "resistance",
                "label": "antibiotic resistance phenotype",
                "node_type": "PHENOTYPE",
                "grounding": "GO:0046677",
                "description": "Echinocandin-resistance phenotype mediated by SAPK/HOG1 loss.",
            },
        ]
    )
    return nodes


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
            "predicate": "enables (wild-type MAP kinase activity)",
            "predicate_id": "RO:0002327",
            "object": "mapk_activity",
        },
    ]
    if spec.include_exposed_chitin:
        edges.extend(
            [
                {
                    "subject": "mapk_activity",
                    "predicate": "negatively regulates (exposed-chitin cell-wall organization)",
                    "predicate_id": "RO:0002212",
                    "object": "cell_wall_organization",
                },
                {
                    "subject": "cell_wall_organization",
                    "predicate": "causally upstream of (caspofungin resistance)",
                    "predicate_id": "RO:0002411",
                    "object": "resistance",
                },
            ]
        )
    else:
        edges.append(
            {
                "subject": "mapk_activity",
                "predicate": "negatively regulates (loss-state resistance)",
                "predicate_id": "RO:0002212",
                "object": "resistance",
            }
        )
    edges.extend(
        [
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
    )

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
        "description": spec.description,
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
