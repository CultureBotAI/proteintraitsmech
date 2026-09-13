#!/usr/bin/env python3
"""Curate UXS1 UDP-glucuronate-decarboxylase 5-FC-resistance graphs.

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

HISTORY_ACTION = "Curated UXS1 UDP-glucuronate 5-flucytosine graph"
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

UXS1_PARENT_DEFINITION_EVIDENCE = {
    "reference": "ARO:3007567",
    "snippet": (
        "UDP-glucuronic acid decarboxylase catalyzes the decarboxylation of "
        "UDP-glucuronic acid. Accumulation of UDP-glucuronic acid mediates "
        "resistance to 5-flucytosine."
    ),
    "notes": "CARD definition for UDP-glucuronic acid decarboxylase.",
}

PYRIMIDINE_ANTIFUNGAL_RELATION_EVIDENCE = {
    "reference": "ARO:3007567",
    "snippet": "relationship: confers_resistance_to_drug_class ARO:3007560 ! pyrimidine antifungal drug",
    "notes": (
        "ARO drug-class relationship on UDP-glucuronic acid decarboxylase, "
        "materialized into trait_relations and inherited by the UXS1 child."
    ),
}

GO_ACTIVITY_EVIDENCE = {
    "reference": "GO:0048040",
    "snippet": "Catalysis of the reaction: H+ + UDP-alpha-D-glucuronate = CO2 + UDP-alpha-D-xylose.",
    "notes": "GO definition for UDP-glucuronate decarboxylase activity.",
}

RHEA_REACTION_EVIDENCE = {
    "reference": "RHEA:23917",
    "snippet": "UDP-alpha-D-glucuronate + H(+) => UDP-alpha-D-xylose + CO2",
    "notes": (
        "Rhea's left-to-right child of RHEA:23916 declares "
        "UDP-alpha-D-glucuronate as a substrate and UDP-alpha-D-xylose as a "
        "product of UDP-glucuronate decarboxylation."
    ),
}

UDP_GLUCURONATE_EVIDENCE = {
    "reference": "CHEBI:58052",
    "snippet": "UDP-alpha-D-glucuronate",
    "notes": "Rhea substrate in the EC 4.1.1.35 reaction.",
}

UDP_XYLOSE_EVIDENCE = {
    "reference": "CHEBI:57632",
    "snippet": "UDP-alpha-D-xylose",
    "notes": "Rhea product in the EC 4.1.1.35 reaction.",
}

BILLMYRE_EVIDENCE = {
    "reference": "PMID:31913284",
    "notes": (
        "Billmyre et al. identified UXS1 among Cryptococcus 5-flucytosine "
        "resistance genes; this is a CARD citation for ARO:3007567 and "
        "ARO:3007568."
    ),
}

CHANG_EVIDENCE = {
    "reference": "PMID:34103502",
    "notes": (
        "Chang et al. connected UXS1, UDP-glucuronic acid accumulation, and "
        "5-fluorocytosine resistance in cryptococci; this is a CARD citation "
        "for ARO:3007567 and ARO:3007568."
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
        path=ARO / "udp-glucuronic-acid-decarboxylase-aro3007567.yaml",
        identifier="ARO:3007567",
        label="UDP-glucuronic acid decarboxylase",
        definition=(
            "UDP-glucuronic acid decarboxylase catalyzes the decarboxylation "
            "of UDP-glucuronic acid. Accumulation of UDP-glucuronic acid "
            "mediates resistance to 5-flucytosine."
        ),
        title=(
            "UDP-glucuronate decarboxylase loss → UDP-glucuronic acid "
            "accumulation → 5-flucytosine resistance"
        ),
        include_parent_definition=False,
    ),
    RecordSpec(
        path=ARO
        / "cryptococcus-spp-uxs1-conferring-resistance-to-5-flucytosine-via-absence-aro3007568.yaml",
        identifier="ARO:3007568",
        label="Cryptococcus spp. UXS1 conferring resistance to 5-flucytosine via absence",
        definition=(
            "UXS1 is a UDP-glucuronic acid decarboxylase. Deletion of UXS1 "
            "confers resistance to 5-flucytosine by accumulation of "
            "UDP-glucoronic acid, thereby suppressing the cellular toxicity "
            "of 5-flucytosine."
        ),
        title=(
            "Cryptococcus UXS1 loss → UDP-glucuronic acid accumulation → "
            "5-flucytosine resistance"
        ),
        include_parent_definition=True,
    ),
)


EDGE_DESCRIPTIONS = {
    ("determinant", "participates in (resistance by absence)", "mech0"): (
        "CARD places this determinant in the resistance-by-absence mechanism."
    ),
    ("determinant", "enables (wild-type UDP-glucuronate decarboxylation)", "activity"): (
        "The encoded wild-type UXS1 enzyme consumes UDP-glucuronic acid by "
        "catalyzing UDP-glucuronate decarboxylation."
    ),
    ("activity", "has input", "udp_glucuronate"): (
        "UDP-alpha-D-glucuronate is the sugar-nucleotide substrate consumed "
        "by UDP-glucuronate decarboxylase activity."
    ),
    ("activity", "has output", "udp_xylose"): (
        "UDP-alpha-D-xylose is the sugar-nucleotide product of "
        "UDP-glucuronate decarboxylation."
    ),
    ("activity", "negatively regulates (substrate-accumulation resistance)", "resistance"): (
        "The wild-type decarboxylase consumes UDP-glucuronic acid, so loss of "
        "this activity removes a check on the substrate accumulation that "
        "mediates 5-flucytosine resistance."
    ),
    ("udp_glucuronate", "causally upstream of (accumulation mediates resistance)", "resistance"): (
        "The ARO resistance claim is mediated by accumulation of "
        "UDP-glucuronic acid, represented here by the accumulating "
        "UDP-alpha-D-glucuronate substrate."
    ),
    ("mech0", "causally upstream of", "resistance"): (
        "Deletion of the UDP-glucuronate decarboxylase gene or gene product "
        "causes 5-flucytosine resistance by allowing UDP-glucuronic acid to "
        "accumulate."
    ),
    ("determinant", "causally upstream of (confers resistance)", "resistance"): (
        "This ARO determinant denotes loss of UDP-glucuronate decarboxylase "
        "and links that loss to a 5-flucytosine resistance phenotype."
    ),
    ("determinant", "confers resistance to (drug class)", "drug0"): (
        "ARO asserts that UDP-glucuronic acid decarboxylase loss confers "
        "resistance to pyrimidine antifungal drugs."
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
        return [spec.definition_evidence, UXS1_PARENT_DEFINITION_EVIDENCE]
    return [spec.definition_evidence]


def _edge_evidence(key: tuple[str, str, str], spec: RecordSpec) -> list[dict[str, str]]:
    definition_evidence = _definition_evidence(spec)
    match key:
        case ("determinant", "participates in (resistance by absence)", "mech0"):
            extra = [*definition_evidence, RESISTANCE_BY_ABSENCE_EVIDENCE]
        case ("determinant", "enables (wild-type UDP-glucuronate decarboxylation)", "activity"):
            extra = [*definition_evidence, GO_ACTIVITY_EVIDENCE, RHEA_REACTION_EVIDENCE]
        case ("activity", "has input", "udp_glucuronate"):
            extra = [GO_ACTIVITY_EVIDENCE, RHEA_REACTION_EVIDENCE, UDP_GLUCURONATE_EVIDENCE]
        case ("activity", "has output", "udp_xylose"):
            extra = [GO_ACTIVITY_EVIDENCE, RHEA_REACTION_EVIDENCE, UDP_XYLOSE_EVIDENCE]
        case ("activity", "negatively regulates (substrate-accumulation resistance)", "resistance"):
            extra = [
                GO_ACTIVITY_EVIDENCE,
                RHEA_REACTION_EVIDENCE,
                *definition_evidence,
                BILLMYRE_EVIDENCE,
                CHANG_EVIDENCE,
            ]
        case ("udp_glucuronate", "causally upstream of (accumulation mediates resistance)", "resistance"):
            extra = [
                UDP_GLUCURONATE_EVIDENCE,
                *definition_evidence,
                BILLMYRE_EVIDENCE,
                CHANG_EVIDENCE,
            ]
        case ("mech0", "causally upstream of", "resistance"):
            extra = [
                RESISTANCE_BY_ABSENCE_EVIDENCE,
                *definition_evidence,
                BILLMYRE_EVIDENCE,
                CHANG_EVIDENCE,
            ]
        case ("determinant", "causally upstream of (confers resistance)", "resistance"):
            extra = [
                *definition_evidence,
                RESISTANCE_BY_ABSENCE_EVIDENCE,
                BILLMYRE_EVIDENCE,
                CHANG_EVIDENCE,
            ]
        case ("determinant", "confers resistance to (drug class)", "drug0"):
            extra = [
                PYRIMIDINE_ANTIFUNGAL_RELATION_EVIDENCE,
                *definition_evidence,
                BILLMYRE_EVIDENCE,
                CHANG_EVIDENCE,
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
            "label": "resistance by absence",
            "node_type": "MOLECULAR_FUNCTION",
            "grounding": "ARO:3003764",
        },
        {
            "node_id": "activity",
            "label": "UDP-glucuronate decarboxylase activity",
            "node_type": "MOLECULAR_FUNCTION",
            "grounding": "GO:0048040",
            "xrefs": ["EC:4.1.1.35", "RHEA:23916"],
        },
        {
            "node_id": "udp_glucuronate",
            "label": "UDP-alpha-D-glucuronate",
            "node_type": "CHEMICAL",
            "grounding": "CHEBI:58052",
        },
        {
            "node_id": "udp_xylose",
            "label": "UDP-alpha-D-xylose",
            "node_type": "CHEMICAL",
            "grounding": "CHEBI:57632",
        },
        {
            "node_id": "drug0",
            "label": "pyrimidine antifungal drug",
            "node_type": "CHEMICAL",
            "grounding": "ARO:3007560",
        },
        {
            "node_id": "resistance",
            "label": "antibiotic resistance phenotype",
            "node_type": "PHENOTYPE",
            "grounding": "GO:0046677",
            "description": (
                "5-flucytosine resistance phenotype mediated by "
                "UDP-glucuronic acid accumulation."
            ),
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
            "predicate": "enables (wild-type UDP-glucuronate decarboxylation)",
            "predicate_id": "RO:0002327",
            "object": "activity",
        },
        {
            "subject": "activity",
            "predicate": "has input",
            "predicate_id": "RO:0002233",
            "object": "udp_glucuronate",
        },
        {
            "subject": "activity",
            "predicate": "has output",
            "predicate_id": "RO:0002234",
            "object": "udp_xylose",
        },
        {
            "subject": "activity",
            "predicate": "negatively regulates (substrate-accumulation resistance)",
            "predicate_id": "RO:0002212",
            "object": "resistance",
        },
        {
            "subject": "udp_glucuronate",
            "predicate": "causally upstream of (accumulation mediates resistance)",
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
            "Conservative resistance-causation graph for the "
            "UDP-glucuronic-acid-decarboxylase branch of resistance by "
            "absence. The graph grounds the missing wild-type activity that "
            "normally consumes UDP-glucuronic acid and connects loss of that "
            "activity to the UDP-glucuronic-acid accumulation that mediates "
            "5-flucytosine resistance."
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
