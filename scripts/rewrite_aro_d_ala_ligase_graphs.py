#!/usr/bin/env python3
"""Rewrite D-Ala-D-Lac and D-Ala-D-Ser Van ligase graphs.

D-Ala-D-Lac ligase and D-Ala-D-Ser ligase both remodel glycopeptide-binding
peptidoglycan precursors. The D-Lac parent keeps its grounded ATP-grasp
domain/fold path; the D-Ser parent keeps an EC-grounded D-alanine--D-serine
ligation activity and models the branch-specific resistant precursor as a
described local state.

Dry-run by default; pass ``--apply`` to write.
"""

from __future__ import annotations

import argparse
import copy
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from record_io import append_to_section, replace_block  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ARO_DIR = ROOT / "data" / "traits" / "function" / "resistance" / "aro"

HISTORY_ACTION = "Completed D-Ala-D-Lac/D-Ala-D-Ser ligase graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-08T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

VAN_LIGASE_EVIDENCE = {
    "reference": "ARO:3002906",
    "snippet": (
        "Van ligases synthesize alternative substrates for peptidoglycan "
        "synthesis that reduce vancomycin binding affinity."
    ),
    "notes": "CARD definition for Van ligase.",
}

CELL_WALL_RESTRUCTURING_EVIDENCE = {
    "reference": "ARO:3000213",
    "snippet": (
        "Peptidoglycan precursors ending in D-Ala-D-Lac or D-Ala-D-Ser instead "
        "of D-Ala-D-Ala conferring high level glycopeptide resistance."
    ),
    "notes": "CARD definition for restructuring of bacterial cell wall.",
}

DLAC_LIGASE_EVIDENCE = {
    "reference": "PMID:10908650",
    "snippet": (
        "D-alanine-D-lactate ligase is directly responsible for the biosynthesis "
        "of alternate cell-wall precursors in bacteria that are resistant to the "
        "glycopeptide antibiotic vancomycin."
    ),
    "notes": "Evidence for D-Ala-D-Lac ligase-mediated precursor replacement.",
}

DSER_LIGASE_EVIDENCE = {
    "reference": "PMID:10817725",
    "snippet": (
        "vanC-1 encodes a ligase that synthesizes the dipeptide D-Ala-D-Ser for "
        "addition to UDP-MurNAc-tripeptide."
    ),
    "notes": "Evidence for D-Ala-D-Ser ligase-mediated precursor replacement.",
}

GLYCOPEPTIDE_EVIDENCE = {
    "reference": "ARO:3000081",
    "snippet": "glycopeptide antibiotic",
    "notes": "ARO drug-class term inherited from the Van ligase branch.",
}

PFAM_DLAC_EVIDENCE = {
    "reference": "Pfam:PF07478",
    "snippet": "D-ala D-ala ligase C-terminus",
    "notes": "Pfam family for the D-Ala-D-Lac ligase domain.",
}

CATH_ATP_GRASP_EVIDENCE = {
    "reference": "CATH:3.30.470",
    "snippet": "D-amino Acid Aminotransferase; Chain A, domain 1",
    "notes": "CATH fold carried by D-Ala-D-Lac ligases in the current graph set.",
}

DSER_EC_EVIDENCE = {
    "reference": "EC:6.3.2.35",
    "snippet": "D-alanine--D-serine ligase",
    "notes": "EC activity for D-Ala-D-Ser ligation.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "restructuring of bacterial cell wall conferring antibiotic resistance",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3000213",
}

GLYCOPEPTIDE_NODE = {
    "node_id": "drug0",
    "label": "glycopeptide antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:3000081",
}

DLAC_DOMAIN_NODE = {
    "node_id": "domain",
    "label": "D-Ala-D-Ala/D-Lac ligase domain",
    "node_type": "DOMAIN",
    "grounding": "Pfam:PF07478",
    "description": "ATP-grasp catalytic domain carried by D-Ala-D-Lac ligases.",
}

ATP_GRASP_FOLD_NODE = {
    "node_id": "fold",
    "label": "ATP-grasp fold",
    "node_type": "DOMAIN",
    "grounding": "CATH:3.30.470",
    "description": "Fold associated with D-Ala-D-Lac ligase ATP-grasp catalysis.",
}

DSER_LIGASE_ACTIVITY_NODE = {
    "node_id": "ligase_activity",
    "label": "D-alanine--D-serine ligase activity",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "EC:6.3.2.35",
    "description": "EC-grounded D-Ala-D-Ser ligase activity enabled by this Van ligase.",
}

RESISTANCE_NODE = {
    "node_id": "resistance",
    "label": "antibiotic resistance phenotype",
    "node_type": "PHENOTYPE",
    "grounding": "GO:0046677",
    "description": (
        "Resistance phenotype conferred by this determinant. Grounded to the "
        "nearest available superclass: ARO models determinants and mechanisms "
        "but has no term for the resistance phenotype itself."
    ),
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    precursor_label: str
    kind: Literal["dlac", "dser"]


TARGETS: tuple[Target, ...] = (
    Target(
        "ARO:3002978",
        "d-ala-d-lac-ligase-aro3002978.yaml",
        "peptidoglycan precursor ending in D-Ala-D-Lac",
        "dlac",
    ),
    Target(
        "ARO:3002979",
        "d-ala-d-ser-ligase-aro3002979.yaml",
        "peptidoglycan precursor ending in D-Ala-D-Ser",
        "dser",
    ),
)
TARGET_BY_ID = {target.identifier: target for target in TARGETS}


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


def _edge_key(edge: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(edge.get("subject", "")),
        str(edge.get("predicate_id", "")),
        str(edge.get("object", "")),
    )


def _unique_evidence(*items: dict[str, str]) -> list[dict[str, str]]:
    evidence: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in items:
        reference = item["reference"]
        if reference in seen:
            continue
        seen.add(reference)
        evidence.append(copy.deepcopy(item))
    return evidence


def _edge(
    subject: str,
    predicate: str,
    predicate_id: str,
    object_: str,
    description: str,
    *evidence: dict[str, str],
) -> dict[str, Any]:
    return {
        "subject": subject,
        "predicate": predicate,
        "predicate_id": predicate_id,
        "object": object_,
        "description": description,
        "evidence": _unique_evidence(*evidence),
    }


def _record_evidence(record: dict[str, Any]) -> dict[str, str]:
    return {
        "reference": str(record["identifier"]),
        "snippet": str(record["definition"]),
        "notes": f"CARD definition for {record['label']}.",
    }


def _determinant_node(record: dict[str, Any]) -> dict[str, str]:
    return {
        "node_id": "determinant",
        "label": str(record["label"]),
        "node_type": "PROTEIN",
        "grounding": str(record["identifier"]),
    }


def _alt_precursor_node(target: Target) -> dict[str, str]:
    return {
        "node_id": "alt_precursor",
        "label": target.precursor_label,
        "node_type": "STATE",
        "description": (
            "Local state for the alternative peptidoglycan precursor synthesized "
            "by this Van ligase branch."
        ),
    }


def _low_affinity_node(target: Target) -> dict[str, str]:
    return {
        "node_id": "low_affinity",
        "label": "reduced vancomycin binding affinity",
        "node_type": "STATE",
        "description": (
            f"Local state for the reduced vancomycin binding caused by "
            f"{target.precursor_label}."
        ),
    }


def _validate_record(record: dict[str, Any], target: Target) -> None:
    if record.get("identifier") != target.identifier:
        raise ValueError(
            f"{target.filename}: expected {target.identifier}, "
            f"found {record.get('identifier')}"
        )
    if not record.get("label"):
        raise ValueError(f"{target.identifier}: missing label")
    if not record.get("definition"):
        raise ValueError(f"{target.identifier}: missing definition")

    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1 or graphs[0].get("graph_id") != "resistance":
        raise ValueError(f"{target.identifier}: expected exactly one resistance graph")

    seen: set[tuple[str, str, str]] = set()
    for edge in _dicts(graphs[0].get("edges")):
        key = _edge_key(edge)
        if key in seen:
            raise ValueError(f"{target.identifier}: duplicate edge {key[0]} -> {key[2]}")
        seen.add(key)


def _common_edges(
    record: dict[str, Any],
    target: Target,
    *branch_evidence: dict[str, str],
) -> list[dict[str, Any]]:
    record_evidence = _record_evidence(record)
    mechanism_evidence = (
        record_evidence,
        VAN_LIGASE_EVIDENCE,
        CELL_WALL_RESTRUCTURING_EVIDENCE,
        *branch_evidence,
    )
    drug_evidence = (
        record_evidence,
        VAN_LIGASE_EVIDENCE,
        GLYCOPEPTIDE_EVIDENCE,
        *branch_evidence,
    )

    return [
        _edge(
            "determinant",
            "participates in (resistance mechanism)",
            "RO:0000056",
            "mech0",
            "CARD classifies this Van ligase under cell-wall restructuring.",
            *mechanism_evidence,
        ),
        _edge(
            "mech0",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            "Alternative peptidoglycan precursor synthesis causes glycopeptide resistance.",
            *mechanism_evidence,
        ),
        _edge(
            "determinant",
            "causally upstream of (confers resistance)",
            "RO:0002411",
            "resistance",
            "The ligase synthesizes an alternative peptidoglycan precursor that reduces vancomycin binding.",
            *mechanism_evidence,
        ),
        _edge(
            "determinant",
            "confers resistance to (drug class)",
            "ARO:2000001",
            "drug0",
            "ARO maps Van ligases to glycopeptide antibiotics.",
            {
                "reference": "ARO:3002906",
                "snippet": (
                    "relationship: confers_resistance_to_drug_class "
                    "ARO:3000081 ! glycopeptide antibiotic"
                ),
                "notes": "ARO drug-class relationship inherited from the Van ligase parent.",
            },
            *drug_evidence,
        ),
        _edge(
            "alt_precursor",
            "causally upstream of",
            "RO:0002411",
            "low_affinity",
            f"{target.precursor_label} has reduced vancomycin binding affinity.",
            *mechanism_evidence,
        ),
        _edge(
            "low_affinity",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            "Reduced vancomycin binding affinity causes glycopeptide resistance.",
            *mechanism_evidence,
            GLYCOPEPTIDE_EVIDENCE,
        ),
    ]


def _dlac_graph(record: dict[str, Any], target: Target) -> dict[str, Any]:
    record_evidence = _record_evidence(record)
    domain_evidence = (
        record_evidence,
        VAN_LIGASE_EVIDENCE,
        DLAC_LIGASE_EVIDENCE,
        PFAM_DLAC_EVIDENCE,
    )
    fold_evidence = (
        record_evidence,
        VAN_LIGASE_EVIDENCE,
        DLAC_LIGASE_EVIDENCE,
        CATH_ATP_GRASP_EVIDENCE,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → D-Ala-D-Lac peptidoglycan precursor synthesis",
        "description": (
            "Curated resistance-causation graph for D-Ala-D-Lac Van ligases. "
            "The determinant synthesizes an alternative peptidoglycan precursor "
            "that lowers glycopeptide binding affinity."
        ),
        "nodes": [
            _determinant_node(record),
            copy.deepcopy(MECHANISM_NODE),
            copy.deepcopy(GLYCOPEPTIDE_NODE),
            _alt_precursor_node(target),
            _low_affinity_node(target),
            copy.deepcopy(DLAC_DOMAIN_NODE),
            copy.deepcopy(ATP_GRASP_FOLD_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            *_common_edges(record, target, DLAC_LIGASE_EVIDENCE),
            _edge(
                "domain",
                "part of",
                "BFO:0000050",
                "determinant",
                "The D-Ala-D-Ala/D-Lac ligase domain is part of the determinant.",
                *domain_evidence,
            ),
            _edge(
                "determinant",
                "member of",
                "RO:0002350",
                "fold",
                "The determinant adopts the ATP-grasp fold used for D-Ala-D-Lac ligase activity.",
                *fold_evidence,
            ),
            _edge(
                "domain",
                "enables (D-Ala-D-Lac precursor synthesis)",
                "RO:0002327",
                "alt_precursor",
                "The D-Ala-D-Ala/D-Lac ligase domain synthesizes the D-Ala-D-Lac precursor.",
                *domain_evidence,
                CELL_WALL_RESTRUCTURING_EVIDENCE,
            ),
        ],
    }


def _dser_graph(record: dict[str, Any], target: Target) -> dict[str, Any]:
    record_evidence = _record_evidence(record)
    ligase_evidence = (
        record_evidence,
        VAN_LIGASE_EVIDENCE,
        CELL_WALL_RESTRUCTURING_EVIDENCE,
        DSER_LIGASE_EVIDENCE,
        DSER_EC_EVIDENCE,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → D-Ala-D-Ser peptidoglycan precursor synthesis",
        "description": (
            "Curated resistance-causation graph for D-Ala-D-Ser Van ligases. "
            "The determinant enables D-Ala-D-Ser ligation upstream of an "
            "alternative peptidoglycan precursor with reduced glycopeptide binding."
        ),
        "nodes": [
            _determinant_node(record),
            copy.deepcopy(MECHANISM_NODE),
            copy.deepcopy(GLYCOPEPTIDE_NODE),
            _alt_precursor_node(target),
            _low_affinity_node(target),
            copy.deepcopy(DSER_LIGASE_ACTIVITY_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            *_common_edges(record, target, DSER_LIGASE_EVIDENCE),
            _edge(
                "determinant",
                "enables (D-Ala-D-Ser ligation)",
                "RO:0002327",
                "ligase_activity",
                "The determinant enables D-Ala-D-Ser ligase activity.",
                *ligase_evidence,
            ),
            _edge(
                "ligase_activity",
                "causally upstream of",
                "RO:0002411",
                "alt_precursor",
                "D-Ala-D-Ser ligase activity produces the branch-specific alternative precursor.",
                *ligase_evidence,
            ),
        ],
    }


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    _validate_record(record, target)

    graph = _dlac_graph(record, target) if target.kind == "dlac" else _dser_graph(record, target)
    out = copy.deepcopy(record)
    out["causal_graphs"] = [graph]
    return out, out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not a D-Ala-D-Lac/D-Ala-D-Ser ligase target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    if HISTORY_ACTION not in out:
        out = append_to_section(out, "curation_history", _dump({"curation_history": [HISTORY_EVENT]}))
        changed = True

    if "&id" in out or "*id" in out:
        raise ValueError(f"{path}: YAML anchors leaked into output")
    return out, changed


def iter_target_paths(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if not path.is_dir():
        raise ValueError(f"{path} is neither a file nor a directory")
    return [path / target.filename for target in TARGETS]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    parser.add_argument(
        "--path",
        type=Path,
        default=ARO_DIR,
        help="ARO directory or one of the two D-Ala-D-Lac/D-Ala-D-Ser YAML files",
    )
    args = parser.parse_args(argv)

    changed = unchanged = 0
    problems: list[str] = []
    for path in iter_target_paths(args.path):
        if not path.exists():
            problems.append(f"{path}: missing")
            continue
        try:
            before = path.read_text(encoding="utf-8")
            after, did_change = enrich_text(before, path)
        except (OSError, ValueError, yaml.YAMLError) as exc:
            problems.append(str(exc))
            continue

        if not did_change:
            unchanged += 1
            continue

        changed += 1
        print(f"  {'wrote' if args.apply else 'would write'} {path.name}")
        if args.apply:
            path.write_text(after, encoding="utf-8")

    print(f"{'changed' if args.apply else 'would change'}: {changed}")
    print(f"already enriched: {unchanged}")
    for problem in problems:
        print(f"PROBLEM: {problem}", file=sys.stderr)
    if not args.apply:
        print("dry run -- pass --apply to write")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
