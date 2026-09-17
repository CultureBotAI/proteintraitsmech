#!/usr/bin/env python3
"""Rewrite low-score fosfomycin thiol-transferase graphs.

The fosfomycin thiol-transferase branch shares antibiotic-inactivation and
fosfomycin epoxide-ring-opening semantics through ARO. The previous graphs
used single-reference evidence and projected a FosA VOC/glyoxalase domain/fold
onto every child; this rewrite keeps the common grounded mechanism and
phosphonic-acid drug-class edge, then stops at a local inactive fosfomycin state.

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
ARO_DIR = ROOT / "data" / "traits" / "function" / "resistance" / "aro"

HISTORY_ACTION = "Completed fosfomycin thiol-transferase graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-08T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

FOSFOMYCIN_THIOL_TRANSFERASE = "ARO:3000133"
DRUG_RELATION_SNIPPET = (
    "relationship: confers_resistance_to_drug_class ARO:3007149 ! "
    "phosphonic acid antibiotic"
)

ANTIBIOTIC_INACTIVATION_EVIDENCE = {
    "reference": "ARO:0001004",
    "snippet": "Enzymatic inactivation of antibiotic to confer drug resistance.",
    "notes": "CARD definition for the antibiotic-inactivation resistance mechanism.",
}

INACTIVATION_ENZYME_EVIDENCE = {
    "reference": "ARO:3000557",
    "snippet": (
        "Enzyme that catalyzes the inactivation of an antibiotic resulting in "
        "resistance. Inactivation includes chemical modification, destruction, etc."
    ),
    "notes": "CARD definition for antibiotic-inactivation enzymes.",
}

FOSFOMYCIN_INACTIVATION_EVIDENCE = {
    "reference": "ARO:3000342",
    "snippet": "Enzymes that inactivate fosfomycin by chemical modification.",
    "notes": "CARD definition for fosfomycin inactivation enzymes.",
}

THIOL_TRANSFERASE_EVIDENCE = {
    "reference": FOSFOMYCIN_THIOL_TRANSFERASE,
    "snippet": (
        "Catalyzes the addition of a thiol group from a nucleophilic molecule "
        "to fosfomycin."
    ),
    "notes": "CARD definition for fosfomycin thiol transferases.",
}

EPOXIDE_OPENING_EVIDENCE = {
    "reference": "ARO:3000125",
    "snippet": (
        "The use of different nucleophilic molecules by enzymes can break up "
        "the epoxide ring of fosfomycin and render the molecule ineffective."
    ),
    "notes": "CARD definition for fosfomycin epoxide-ring opening.",
}

PHOSPHONIC_ACID_EVIDENCE = {
    "reference": "ARO:3007149",
    "snippet": "phosphonic acid antibiotic",
    "notes": "ARO phosphonic-acid antibiotic drug class inherited by Fos records.",
}

INACTIVATION_NODE = {
    "node_id": "mech0",
    "label": "antibiotic inactivation",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:0001004",
}

EPOXIDE_OPENING_NODE = {
    "node_id": "mech1",
    "label": "fosfomycin epoxide-ring opening",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3000125",
    "description": (
        "Grounded to ARO:3000125, the CARD mechanism for enzymes that "
        "inactivate fosfomycin by breaking its epoxide ring."
    ),
}

DRUG_NODE = {
    "node_id": "drug0",
    "label": "phosphonic acid antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:3007149",
}

MODIFIED_NODE = {
    "node_id": "modified",
    "label": "inactive epoxide-opened fosfomycin",
    "node_type": "STATE",
    "description": (
        "Local product state for fosfomycin after a nucleophile opens the "
        "epoxide ring and inactivates the antibiotic."
    ),
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

CORE_EDGE_KEYS = {
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0000056", "mech1"),
    ("mech1", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("determinant", "ARO:2000001", "drug0"),
    ("mech1", "RO:0002233", "drug0"),
    ("mech1", "RO:0002411", "modified"),
}

EXTRA_OLD_EDGE_KEYS = {
    ("domain", "BFO:0000050", "determinant"),
    ("determinant", "RO:0002350", "fold"),
    ("domain", "RO:0002327", "mech1"),
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str


TARGETS: tuple[Target, ...] = (
    Target("ARO:3000149", "fosa-aro3000149.yaml"),
    Target("ARO:3002804", "fosa2-aro3002804.yaml"),
    Target("ARO:3002872", "fosa3-aro3002872.yaml"),
    Target("ARO:3003210", "fosa4-aro3003210.yaml"),
    Target("ARO:3003209", "fosa5-aro3003209.yaml"),
    Target("ARO:3004111", "fosa6-aro3004111.yaml"),
    Target("ARO:3004113", "fosa7-aro3004113.yaml"),
    Target("ARO:3007371", "fosa8-aro3007371.yaml"),
    Target("ARO:3000172", "fosb-aro3000172.yaml"),
    Target("ARO:3004670", "fosb1-aro3004670.yaml"),
    Target("ARO:3005100", "fosb2-aro3005100.yaml"),
    Target("ARO:3002873", "fosb3-aro3002873.yaml"),
    Target("ARO:3004671", "fosb4-aro3004671.yaml"),
    Target("ARO:3004672", "fosb5-aro3004672.yaml"),
    Target("ARO:3004673", "fosb6-aro3004673.yaml"),
    Target("ARO:3007372", "fosbx1-aro3007372.yaml"),
    Target("ARO:3004661", "staphylococcus-aureus-fosb-aro3004661.yaml"),
    Target("ARO:3004674", "fosd-aro3004674.yaml"),
    Target("ARO:3000133", "fosfomycin-thiol-transferase-aro3000133.yaml"),
    Target("ARO:3007368", "fosg-aro3007368.yaml"),
    Target("ARO:3007369", "fosh-aro3007369.yaml"),
    Target("ARO:3007370", "fosi-aro3007370.yaml"),
    Target("ARO:3003207", "fosk-aro3003207.yaml"),
    Target("ARO:3005024", "fosl1-aro3005024.yaml"),
    Target("ARO:3007097", "fosm1-aro3007097.yaml"),
    Target("ARO:3007098", "fosm2-aro3007098.yaml"),
    Target("ARO:3007099", "fosm3-aro3007099.yaml"),
    Target("ARO:3000198", "fosx-aro3000198.yaml"),
    Target("ARO:3003208", "fosxcc-aro3003208.yaml"),
    Target("ARO:3007069", "fosy-aro3007069.yaml"),
)
TARGET_BY_FILENAME = {target.filename: target for target in TARGETS}


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


def _nodes_by_id(graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(node["node_id"]): node
        for node in _dicts(graph.get("nodes"))
        if "node_id" in node
    }


def _unique_evidence(*items: dict[str, Any]) -> list[dict[str, Any]]:
    unique: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for item in items:
        key = (str(item["reference"]), " ".join(str(item.get("snippet", "")).split()))
        if key in seen:
            continue
        seen.add(key)
        unique.append(copy.deepcopy(item))
    return unique


def _source_evidence(record: dict[str, Any]) -> tuple[dict[str, str], ...]:
    return tuple(
        {
            "reference": str(item["reference"]),
            "notes": str(item.get("notes") or "ARO citation for this record."),
        }
        for item in _dicts(record.get("evidence"))
        if item.get("reference")
    )


def _target_evidence(record: dict[str, Any]) -> dict[str, str]:
    return {
        "reference": str(record["identifier"]),
        "snippet": str(record["definition"]),
        "notes": f"CARD definition for {record['label']}.",
    }


def _drug_relation_evidence(graph: dict[str, Any]) -> list[dict[str, Any]]:
    for edge in _dicts(graph.get("edges")):
        if (
            edge.get("subject") == "determinant"
            and edge.get("predicate_id") == "ARO:2000001"
            and edge.get("object") == "drug0"
        ):
            return [
                copy.deepcopy(item)
                for item in _dicts(edge.get("evidence"))
                if item.get("reference")
                and str(item.get("snippet", "")) == DRUG_RELATION_SNIPPET
            ]
    return []


def _edge(
    subject: str,
    predicate: str,
    predicate_id: str,
    object_: str,
    description: str,
    *evidence: dict[str, Any],
) -> dict[str, Any]:
    return {
        "subject": subject,
        "predicate": predicate,
        "predicate_id": predicate_id,
        "object": object_,
        "description": description,
        "evidence": _unique_evidence(*evidence),
    }


def _validate_graph(graph: dict[str, Any], target: Target) -> None:
    nodes = _nodes_by_id(graph)
    missing_nodes = sorted({"determinant", "mech0", "mech1", "drug0", "resistance"} - nodes.keys())
    if missing_nodes:
        raise ValueError(f"{target.identifier}: missing node(s): {', '.join(missing_nodes)}")

    found: set[tuple[str, str, str]] = set()
    seen: set[tuple[str, str, str]] = set()
    for edge in _dicts(graph.get("edges")):
        key = _edge_key(edge)
        if key not in CORE_EDGE_KEYS and key not in EXTRA_OLD_EDGE_KEYS:
            raise ValueError(f"{target.identifier}: unexpected edge {key[0]} -> {key[2]}")
        if key in seen:
            raise ValueError(f"{target.identifier}: duplicate edge {key[0]} -> {key[2]}")
        seen.add(key)
        found.add(key)

    required = CORE_EDGE_KEYS - {
        ("mech1", "RO:0002233", "drug0"),
        ("mech1", "RO:0002411", "modified"),
    }
    missing_edges = sorted(required - found)
    if missing_edges:
        missing = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in missing_edges)
        raise ValueError(f"{target.identifier}: missing edge(s): {missing}")

    if not _drug_relation_evidence(graph):
        raise ValueError(f"{target.identifier}: missing ARO drug-relation evidence")


def _canonical_edges(
    record: dict[str, Any],
    old_graph: dict[str, Any],
) -> list[dict[str, Any]]:
    target_evidence = _target_evidence(record)
    source_evidence = _source_evidence(record)
    inactivation_evidence = (
        target_evidence,
        FOSFOMYCIN_INACTIVATION_EVIDENCE,
        INACTIVATION_ENZYME_EVIDENCE,
        ANTIBIOTIC_INACTIVATION_EVIDENCE,
        *source_evidence,
    )
    epoxide_evidence = (
        target_evidence,
        THIOL_TRANSFERASE_EVIDENCE,
        EPOXIDE_OPENING_EVIDENCE,
        FOSFOMYCIN_INACTIVATION_EVIDENCE,
        *source_evidence,
    )

    return [
        _edge(
            "determinant",
            "participates in (inactivation mechanism)",
            "RO:0000056",
            "mech0",
            "CARD classifies this Fos branch under antibiotic inactivation.",
            *inactivation_evidence,
        ),
        _edge(
            "mech0",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            "Fosfomycin inactivation is causally upstream of the resistance phenotype.",
            *inactivation_evidence,
        ),
        _edge(
            "determinant",
            "participates in (fosfomycin epoxide-ring opening)",
            "RO:0000056",
            "mech1",
            "CARD classifies this branch under fosfomycin epoxide-ring opening.",
            *epoxide_evidence,
        ),
        _edge(
            "mech1",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            "Epoxide-ring opening chemically modifies and inactivates fosfomycin.",
            *epoxide_evidence,
        ),
        _edge(
            "determinant",
            "causally upstream of (confers resistance)",
            "RO:0002411",
            "resistance",
            "The determinant opens the fosfomycin epoxide ring upstream of drug inactivation.",
            *epoxide_evidence,
            ANTIBIOTIC_INACTIVATION_EVIDENCE,
        ),
        _edge(
            "determinant",
            "confers resistance to",
            "ARO:2000001",
            "drug0",
            "ARO maps the fosfomycin thiol-transferase branch to phosphonic acid antibiotics.",
            *_drug_relation_evidence(old_graph),
            target_evidence,
            THIOL_TRANSFERASE_EVIDENCE,
            PHOSPHONIC_ACID_EVIDENCE,
            *source_evidence,
        ),
        _edge(
            "mech1",
            "has input (fosfomycin)",
            "RO:0002233",
            "drug0",
            "Fosfomycin is the phosphonic-acid antibiotic input to the epoxide-opening reaction.",
            *epoxide_evidence,
            PHOSPHONIC_ACID_EVIDENCE,
        ),
        _edge(
            "mech1",
            "causally upstream of (inactivates the drug)",
            "RO:0002411",
            "modified",
            "The epoxide-opening mechanism produces an inactive modified fosfomycin state.",
            *epoxide_evidence,
        ),
    ]


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != target.identifier:
        raise ValueError(f"expected {target.identifier}, found {record.get('identifier')}")

    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1 or graphs[0].get("graph_id") != "resistance":
        raise ValueError(f"{target.identifier}: expected exactly one resistance graph")

    graph = graphs[0]
    _validate_graph(graph, target)

    out = copy.deepcopy(record)
    out["causal_graphs"] = [
        {
            "graph_id": "resistance",
            "title": f"{record['label']} → fosfomycin epoxide-ring opening → resistance",
            "description": (
                "Curated resistance graph for fosfomycin thiol transferases. "
                "The graph keeps CARD's antibiotic-inactivation and fosfomycin "
                "epoxide-ring-opening mechanisms, preserves the inherited "
                "phosphonic-acid drug-class edge, and stops at a local inactive "
                "fosfomycin state."
            ),
            "nodes": [
                copy.deepcopy(_nodes_by_id(graph)["determinant"]),
                copy.deepcopy(INACTIVATION_NODE),
                copy.deepcopy(EPOXIDE_OPENING_NODE),
                copy.deepcopy(DRUG_NODE),
                copy.deepcopy(MODIFIED_NODE),
                copy.deepcopy(RESISTANCE_NODE),
            ],
            "edges": _canonical_edges(record, graph),
        }
    ]
    return out, out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: record is not a mapping")

    target = TARGET_BY_FILENAME.get(path.name)
    if target is None:
        raise ValueError(f"{path}: not a fosfomycin thiol-transferase target")

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
        help="ARO directory or one of the 31 low-score fosfomycin thiol-transferase YAML files",
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
