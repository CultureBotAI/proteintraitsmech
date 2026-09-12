#!/usr/bin/env python3
"""Curate FusE/rplF fusidic-acid mutation graphs.

FusE is a mutation-based rplF/ribosomal-protein-L6 route. CARD describes the
site only as a potential secondary fusidic-acid action site, so this updater
keeps the target action as a local state instead of grounding it to the
primary EF-G fusidic-acid mechanism or to the unrelated FusH inactivation
route.

Dry-run by default; pass ``--apply`` to write.
"""

from __future__ import annotations

import argparse
import copy
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from record_io import append_to_section, replace_block  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ARO_DIR = ROOT / "data" / "traits" / "function" / "resistance" / "aro"

PARENT_IDENTIFIER = "ARO:3003736"
CHILD_IDENTIFIER = "ARO:3003737"
HISTORY_ACTION = "Curated FusE rplF fusidic-acid resistance graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-11T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

PARENT_EVIDENCE = {
    "reference": PARENT_IDENTIFIER,
    "snippet": (
        "Antibiotic resistant fusE is caused by mutations in a region of the "
        "rplF gene encoding riboprotein L6, and confers resistance to "
        "fusidic acid."
    ),
    "notes": "CARD definition for antibiotic-resistant FusE.",
}

MUTATION_EVIDENCE = {
    "reference": "ARO:3000212",
    "snippet": (
        "Point mutations in the DNA may lead to an altered gene product that "
        "may result in antibiotic resistance."
    ),
    "notes": "CARD definition for mutation conferring antibiotic resistance.",
}

FUSIDANE_RELATION_EVIDENCE = {
    "reference": PARENT_IDENTIFIER,
    "snippet": "relationship: confers_resistance_to_drug_class ARO:3007153 ! fusidane antibiotic",
    "notes": "ARO drug-class relationship asserted on antibiotic resistant fusE.",
}

FUSIDANE_EVIDENCE = {
    "reference": "ARO:3007153",
    "snippet": "fusidane antibiotic",
    "notes": "ARO drug-class term inherited by FusE records.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "mutation conferring antibiotic resistance",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3000212",
}

DRUG_NODE = {
    "node_id": "drug0",
    "label": "fusidane antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:3007153",
}

BLOCKED_ACTION_NODE = {
    "node_id": "blocked_action",
    "label": "fusidic acid action through the rplF/L6 secondary site",
    "node_type": "STATE",
    "description": (
        "Local state for fusidic-acid action through ribosomal protein L6, "
        "which CARD describes as a potential secondary site of action blocked "
        "by FusE mutations."
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

INITIAL_EDGE_KEYS = {
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("determinant", "ARO:2000001", "drug0"),
}

EXPECTED_EDGE_KEYS = INITIAL_EDGE_KEYS | {
    ("drug0", "RO:0002411", "blocked_action"),
    ("determinant", "RO:0002212", "blocked_action"),
}

_MAPPING_STATUS = re.compile(r"^mapping_status:[ \t]*\S+[ \t]*$", re.M)


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str

    @property
    def is_child(self) -> bool:
        return self.identifier == CHILD_IDENTIFIER


TARGETS = {
    PARENT_IDENTIFIER: Target(
        PARENT_IDENTIFIER,
        "antibiotic-resistant-fuse-aro3003736.yaml",
    ),
    CHILD_IDENTIFIER: Target(
        CHILD_IDENTIFIER,
        "staphylococcus-aureus-fuse-with-mutation-conferring-resistance-to-fusidic-acid-"
        "aro3003737.yaml",
    ),
}
TARGET_BY_FILENAME = {target.filename: target for target in TARGETS.values()}


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


def _source_evidence(record: dict[str, Any]) -> tuple[dict[str, str], ...]:
    return tuple(
        {
            "reference": str(item["reference"]),
            "notes": str(item.get("notes") or "ARO citation for this record."),
        }
        for item in _dicts(record.get("evidence"))
        if item.get("reference")
    )


def _target_evidence(record: dict[str, Any], target: Target) -> dict[str, str]:
    if target.is_child:
        return {
            "reference": str(record["identifier"]),
            "snippet": str(record["definition"]),
            "notes": (
                "CARD definition for Staphylococcus aureus fusE mutations "
                "conferring resistance to fusidic acid."
            ),
        }
    return PARENT_EVIDENCE


def _unique_evidence(evidence: tuple[dict[str, str], ...]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for item in evidence:
        key = (
            item["reference"],
            item.get("snippet", ""),
            item.get("notes", ""),
        )
        if key in seen:
            continue
        seen.add(key)
        out.append(copy.deepcopy(item))
    return out


def _edge(
    subject: str,
    predicate: str,
    predicate_id: str,
    object_: str,
    description: str,
    evidence: tuple[dict[str, str], ...],
) -> dict[str, Any]:
    return {
        "subject": subject,
        "predicate": predicate,
        "predicate_id": predicate_id,
        "object": object_,
        "description": description,
        "evidence": _unique_evidence(evidence),
    }


def _validate_graph(graph: dict[str, Any], target: Target) -> None:
    nodes = _nodes_by_id(graph)
    missing_nodes = sorted({"determinant", "mech0", "drug0", "resistance"} - set(nodes))
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")

    seen: set[tuple[str, str, str]] = set()
    found_edges: set[tuple[str, str, str]] = set()
    for edge in _dicts(graph.get("edges")):
        key = _edge_key(edge)
        if key not in EXPECTED_EDGE_KEYS:
            raise ValueError(f"{target.identifier}: unexpected edge {key[0]} -> {key[2]}")
        if key in seen:
            raise ValueError(f"{target.identifier}: duplicate edge {key[0]} -> {key[2]}")
        seen.add(key)
        found_edges.add(key)

    if found_edges == EXPECTED_EDGE_KEYS:
        return

    missing_initial = INITIAL_EDGE_KEYS - found_edges
    unexpected_canonical = found_edges - INITIAL_EDGE_KEYS
    if missing_initial:
        missing = ", ".join(
            f"{subject} -> {object_}"
            for subject, _, object_ in sorted(missing_initial)
        )
        raise ValueError(f"{target.identifier}: missing initial edge(s): {missing}")
    if unexpected_canonical:
        extra = ", ".join(
            f"{subject} -> {object_}"
            for subject, _, object_ in sorted(unexpected_canonical)
        )
        raise ValueError(f"{target.identifier}: partial canonical edge(s): {extra}")


def _canonical_nodes(graph: dict[str, Any]) -> list[dict[str, Any]]:
    nodes = _nodes_by_id(graph)
    return [
        copy.deepcopy(nodes["determinant"]),
        copy.deepcopy(MECHANISM_NODE),
        copy.deepcopy(DRUG_NODE),
        copy.deepcopy(BLOCKED_ACTION_NODE),
        copy.deepcopy(RESISTANCE_NODE),
    ]


def _canonical_edges(record: dict[str, Any], target: Target) -> list[dict[str, Any]]:
    target_evidence = _target_evidence(record, target)
    source_evidence = _source_evidence(record)
    resistance_evidence = (
        target_evidence,
        PARENT_EVIDENCE,
        MUTATION_EVIDENCE,
        *source_evidence,
    )
    drug_evidence = (
        target_evidence,
        PARENT_EVIDENCE,
        FUSIDANE_RELATION_EVIDENCE,
        FUSIDANE_EVIDENCE,
        *source_evidence,
    )
    return [
        _edge(
            "determinant",
            "participates in (resistance mechanism)",
            "RO:0000056",
            "mech0",
            "CARD classifies FusE/rplF resistance as mutation-based resistance.",
            resistance_evidence,
        ),
        _edge(
            "mech0",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            "rplF point, frameshift, or stop-codon mutations cause fusidic-acid resistance.",
            resistance_evidence,
        ),
        _edge(
            "determinant",
            "causally upstream of (confers resistance)",
            "RO:0002411",
            "resistance",
            (
                "Mutations in the rplF gene encoding ribosomal protein L6 "
                "confer resistance to fusidic acid."
            ),
            resistance_evidence,
        ),
        _edge(
            "determinant",
            "confers resistance to",
            "ARO:2000001",
            "drug0",
            "ARO maps FusE/rplF mutations to the fusidane antibiotic drug class.",
            drug_evidence,
        ),
        _edge(
            "drug0",
            "causally upstream of (acts through rplF/L6 secondary site)",
            "RO:0002411",
            "blocked_action",
            (
                "The S. aureus child definition describes ribosomal protein L6 "
                "as a potential secondary site of fusidic-acid action."
            ),
            drug_evidence,
        ),
        _edge(
            "determinant",
            "negatively regulates (blocks secondary site of action)",
            "RO:0002212",
            "blocked_action",
            "FusE/rplF mutations block fusidic-acid action through ribosomal protein L6.",
            drug_evidence,
        ),
    ]


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != target.identifier:
        raise ValueError(f"expected {target.identifier}, found {record.get('identifier')}")

    out = copy.deepcopy(record)
    before = copy.deepcopy(out.get("causal_graphs"))
    graphs = _dicts(out.get("causal_graphs"))
    if len(graphs) != 1:
        raise ValueError(f"{target.identifier}: expected exactly one causal graph")
    graph = graphs[0]
    _validate_graph(graph, target)

    graph["graph_id"] = "resistance"
    graph["title"] = f"{record['label']} → FusE rplF/L6 mutation → fusidane resistance"
    graph["description"] = (
        "Conservative graph for FusE/rplF-mediated fusidic-acid resistance. "
        "The graph keeps ribosomal protein L6 as the potential secondary "
        "site of action named by CARD and does not conflate this mutation "
        "route with EF-G target protection or FusH inactivation."
    )
    graph["nodes"] = _canonical_nodes(graph)
    graph["edges"] = _canonical_edges(record, target)
    out["causal_graphs"] = [graph]
    out["mapping_status"] = "REVIEWED"
    if not any(
        isinstance(item, dict) and item.get("action") == HISTORY_ACTION
        for item in out.get("curation_history") or []
    ):
        out.setdefault("curation_history", []).append(copy.deepcopy(HISTORY_EVENT))
    return out, out.get("causal_graphs") != before or record.get("mapping_status") != "REVIEWED"


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    target = TARGET_BY_FILENAME.get(path.name)
    if target is None:
        raise ValueError(f"{path}: not a FusE target")
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: not a YAML mapping")
    out, changed = enrich_record(record, target)
    graph_block = _dump({"causal_graphs": out["causal_graphs"]})
    result = replace_block(text, "causal_graphs", graph_block)
    result = _MAPPING_STATUS.sub("mapping_status: REVIEWED", result, count=1)
    if HISTORY_ACTION not in result:
        history_block = _dump({"curation_history": [HISTORY_EVENT]})
        result = append_to_section(result, "curation_history", history_block)
    return result, changed or result != text


def iter_paths(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    return [path / target.filename for target in TARGETS.values()]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, nargs="?", default=ARO_DIR)
    parser.add_argument("--apply", action="store_true", help="write changes")
    args = parser.parse_args(argv)

    changed = 0
    already = 0
    for path in iter_paths(args.path):
        text = path.read_text(encoding="utf-8")
        out, did_change = enrich_text(text, path)
        if did_change:
            if args.apply:
                path.write_text(out, encoding="utf-8")
                print(f"  wrote {path.name}")
            else:
                print(f"  would write {path.name}")
            changed += 1
        else:
            already += 1

    verb = "changed" if args.apply else "would change"
    print(f"{verb}: {changed}")
    print(f"already enriched: {already}")
    if not args.apply:
        print("dry run -- pass --apply to write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
