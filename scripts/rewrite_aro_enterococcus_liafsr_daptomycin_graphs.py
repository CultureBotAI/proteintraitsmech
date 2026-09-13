#!/usr/bin/env python3
"""Rewrite low-score Enterococcus LiaFSR daptomycin graphs.

The six Enterococcus liaF/liaR/liaS records are species-specific daptomycin
mutation records. They retain the broad ARO mutation mechanism and the
peptide-antibiotic drug-class edge inherited through the daptomycin-resistant
liaF/liaR/liaS parents, while their LiaFSR side branch is grounded to the GO
cell-envelope-stress response and kept conservative.

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

import rewrite_aro_liafsr_graph as liafsr  # noqa: E402
from record_io import append_to_section, replace_block  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ARO_DIR = ROOT / "data" / "traits" / "function" / "resistance" / "aro"

HISTORY_ACTION = "Completed Enterococcus LiaFSR daptomycin graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-08T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

DAPTOMYCIN_DRUG_NODE = {
    "node_id": "drug0",
    "label": "peptide antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:3000053",
}

CORE_EDGE_KEYS = {
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("determinant", "ARO:2000001", "drug0"),
    ("determinant", "RO:0002211", "stress_response"),
}

EXTRA_OLD_EDGE_KEYS = {
    ("drug0", "RO:0002411", "lipid_ii_stress"),
    ("lipid_ii_stress", "RO:0002411", "determinant"),
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str


TARGETS: tuple[Target, ...] = (
    Target(
        "ARO:3003077",
        "enterococcus-faecalis-liaf-mutant-conferring-daptomycin-resistance-aro3003077.yaml",
    ),
    Target(
        "ARO:3003792",
        "enterococcus-faecalis-liar-mutant-conferring-daptomycin-resistance-aro3003792.yaml",
    ),
    Target(
        "ARO:3003791",
        "enterococcus-faecalis-lias-mutant-conferring-daptomycin-resistance-aro3003791.yaml",
    ),
    Target(
        "ARO:3003790",
        "enterococcus-faecium-liaf-mutant-conferring-daptomycin-resistance-aro3003790.yaml",
    ),
    Target(
        "ARO:3003078",
        "enterococcus-faecium-liar-mutant-conferring-daptomycin-resistance-aro3003078.yaml",
    ),
    Target(
        "ARO:3003079",
        "enterococcus-faecium-lias-mutant-conferring-daptomycin-resistance-aro3003079.yaml",
    ),
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
    seen: set[tuple[str, str, str]] = set()
    for item in items:
        key = (
            str(item["reference"]),
            str(item.get("snippet", "")),
            str(item.get("notes", "")),
        )
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
                if str(item.get("snippet", "")).startswith(
                    "relationship: confers_resistance_to_drug_class "
                )
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
    missing_nodes = sorted(
        {"determinant", "mech0", "drug0", "stress_response", "resistance"} - set(nodes)
    )
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

    missing_edges = sorted(CORE_EDGE_KEYS - found)
    if missing_edges:
        missing = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in missing_edges)
        raise ValueError(f"{target.identifier}: missing edge(s): {missing}")

    if not _drug_relation_evidence(graph):
        raise ValueError(f"{target.identifier}: missing ARO drug-relation evidence")


def _canonical_nodes(graph: dict[str, Any]) -> list[dict[str, Any]]:
    nodes = _nodes_by_id(graph)
    return [
        copy.deepcopy(nodes["determinant"]),
        copy.deepcopy(liafsr.MECHANISM_NODE),
        copy.deepcopy(DAPTOMYCIN_DRUG_NODE),
        copy.deepcopy(liafsr.STRESS_RESPONSE_NODE),
        copy.deepcopy(liafsr.RESISTANCE_NODE),
    ]


def _canonical_edges(
    record: dict[str, Any],
    old_graph: dict[str, Any],
) -> list[dict[str, Any]]:
    target_evidence = _target_evidence(record)
    source_evidence = _source_evidence(record)
    mutation_evidence = (
        target_evidence,
        liafsr.MUTATION_EVIDENCE,
        *source_evidence,
    )
    stress_evidence = (
        target_evidence,
        liafsr.LIAFSR_EVIDENCE,
        liafsr.GO_ENVELOPE_STRESS_EVIDENCE,
        *source_evidence,
    )

    return [
        _edge(
            "determinant",
            "participates in (resistance mechanism)",
            "RO:0000056",
            "mech0",
            "ARO classifies the LiaFSR component variant under mutation conferring antibiotic resistance.",
            *mutation_evidence,
        ),
        _edge(
            "mech0",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            "The broad mutation mechanism covers LiaFSR variants associated with daptomycin resistance.",
            *mutation_evidence,
        ),
        _edge(
            "determinant",
            "causally upstream of (confers resistance)",
            "RO:0002411",
            "resistance",
            "The local ARO definition states that LiaFSR component mutations confer daptomycin resistance.",
            *mutation_evidence,
            liafsr.LIAFSR_EVIDENCE,
        ),
        _edge(
            "determinant",
            "confers resistance to (drug class)",
            "ARO:2000001",
            "drug0",
            "ARO maps daptomycin-resistant LiaFSR component variants to the peptide-antibiotic class.",
            *_drug_relation_evidence(old_graph),
            target_evidence,
            liafsr.MUTATION_EVIDENCE,
            *source_evidence,
        ),
        _edge(
            "determinant",
            "regulates",
            "RO:0002211",
            "stress_response",
            (
                "liaF, liaR, and liaS are components of the LiaFSR regulatory system "
                "for the cell-envelope-stress response."
            ),
            *stress_evidence,
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
            "title": f"{record['label']} → LiaFSR cell-envelope-stress response",
            "description": (
                "Conservative graph for an Enterococcus LiaFSR component mutation "
                "conferring daptomycin resistance. The graph grounds the LiaFSR "
                "cell-envelope-stress response to GO:0036460, keeps the inherited "
                "peptide-antibiotic edge, and stops before unspecified downstream "
                "outputs of the stress response."
            ),
            "nodes": _canonical_nodes(graph),
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
        raise ValueError(f"{path}: not an Enterococcus LiaFSR daptomycin target")

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
        help=(
            "ARO directory or one of the 6 low-score Enterococcus LiaFSR "
            "daptomycin YAML files"
        ),
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
