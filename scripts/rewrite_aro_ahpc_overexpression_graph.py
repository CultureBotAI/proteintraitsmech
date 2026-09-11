#!/usr/bin/env python3
"""Curate the AhpC isoniazid leaf that names overexpression explicitly.

The broader ahpC ancestors are contradictory: one CARD definition describes
activation loss while another defines only wild-type alkyl hydroperoxide
reductase activity. ARO:3004921 is narrower and says the mutations result in
ahpC overexpression, so this updater rewrites only that leaf and adds an
overexpression state without promoting either ancestor.

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

HISTORY_ACTION = "Curated AhpC overexpression isoniazid graph"
HISTORY_EVENT = {
    "timestamp": "2026-09-11T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

MUTATION_EVIDENCE = {
    "reference": "ARO:3000212",
    "snippet": (
        "Point mutations in the DNA may lead to an altered gene product that "
        "may result in antibiotic resistance. Examples included modified "
        "antibiotic targets with lower binding affinities and the deactivation "
        "of repressors that result in increased expression of genes that "
        "inactivate or pump out antibiotics."
    ),
    "notes": (
        "CARD definition for the broad mutation-conferring resistance mechanism; "
        "its examples include mutation-driven increased expression."
    ),
}

ISONIAZID_RELATION_EVIDENCE = {
    "reference": "ARO:3004921",
    "snippet": "relationship: confers_resistance_to_antibiotic ARO:3000520 ! isoniazid",
    "notes": "Asserted directly on ARO:3004921 in the source ARO term.",
}

ISONIAZID_CLASS_EVIDENCE = {
    "reference": "ARO:3004894",
    "snippet": (
        "relationship: confers_resistance_to_drug_class "
        "ARO:3007152 ! isoniazid-like antibiotic"
    ),
    "notes": (
        "Asserted on ARO:3004894 (Isoniazid resistant ahpC), an is_a ancestor "
        "of ARO:3004921; inherited by this variant."
    ),
}

INITIAL_EDGE_KEYS = {
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("determinant", "ARO:2000001", "drug0"),
}
FINAL_EDGE_ORDER = (
    ("determinant", "RO:0000056", "mech0"),
    ("determinant", "RO:0002411", "overexpression"),
    ("overexpression", "RO:0002411", "resistance"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("determinant", "ARO:2000001", "drug0"),
)

GRAPH_NODES = [
    "determinant",
    "mech0",
    "drug0",
    "overexpression",
    "resistance",
]


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str


TARGET = Target(
    "ARO:3004921",
    "mycobacterium-tuberculosis-ahpc-mutations-confer-resistance-to-isoniazid-aro3004921.yaml",
)
TARGETS = (TARGET,)
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


def _unique_evidence(*items: dict[str, str]) -> list[dict[str, str]]:
    unique: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for item in items:
        key = (
            item["reference"],
            item.get("snippet", ""),
            item.get("notes", ""),
        )
        if key in seen:
            continue
        seen.add(key)
        unique.append(copy.deepcopy(item))
    return unique


def _record_evidence(record: dict[str, Any]) -> dict[str, str]:
    return {
        "reference": str(record["identifier"]),
        "snippet": str(record["definition"]),
        "notes": f"CARD definition for {record['label']}.",
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


def _canonical_graph(record: dict[str, Any], graph: dict[str, Any]) -> dict[str, Any]:
    nodes = _nodes_by_id(graph)
    determinant = str(record["label"])
    record_evidence = _record_evidence(record)
    source_evidence = _source_evidence(record)
    route_evidence = (record_evidence, MUTATION_EVIDENCE, *source_evidence)
    overexpression_evidence = (record_evidence, *source_evidence)
    resistance_evidence = (
        record_evidence,
        ISONIAZID_RELATION_EVIDENCE,
        MUTATION_EVIDENCE,
        *source_evidence,
    )
    drug_evidence = (
        ISONIAZID_CLASS_EVIDENCE,
        ISONIAZID_RELATION_EVIDENCE,
        record_evidence,
        *source_evidence,
    )

    edges = {
        ("determinant", "RO:0000056", "mech0"): _edge(
            "determinant",
            "participates in (resistance mechanism)",
            "RO:0000056",
            "mech0",
            (
                "CARD defines this determinant as ahpC mutations and classifies "
                "it under mutation-conferring antibiotic resistance."
            ),
            *route_evidence,
        ),
        ("determinant", "RO:0002411", "overexpression"): _edge(
            "determinant",
            "causally upstream of (raises expression)",
            "RO:0002411",
            "overexpression",
            "This record states that the ahpC mutations result in ahpC overexpression.",
            *overexpression_evidence,
        ),
        ("overexpression", "RO:0002411", "resistance"): _edge(
            "overexpression",
            "causally upstream of (confers or contributes to resistance)",
            "RO:0002411",
            "resistance",
            "CARD names AhpC overexpression as the route to isoniazid resistance here.",
            *overexpression_evidence,
        ),
        ("mech0", "RO:0002411", "resistance"): _edge(
            "mech0",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            (
                "Mutation-conferring resistance is upstream of resistance through "
                "the AhpC-overexpression route on this record."
            ),
            *resistance_evidence,
        ),
        ("determinant", "RO:0002411", "resistance"): _edge(
            "determinant",
            "causally upstream of (confers resistance)",
            "RO:0002411",
            "resistance",
            (
                "The ahpC mutations confer or contribute to isoniazid resistance "
                "by increasing AhpC expression."
            ),
            *resistance_evidence,
        ),
        ("determinant", "ARO:2000001", "drug0"): _edge(
            "determinant",
            "confers resistance to (drug class)",
            "ARO:2000001",
            "drug0",
            (
                "ARO maps the isoniazid-resistant ahpC parent to the "
                "isoniazid-like antibiotic drug class."
            ),
            *drug_evidence,
        ),
    }

    overexpression_node = {
        "node_id": "overexpression",
        "label": "AhpC overexpression",
        "node_type": "STATE",
        "description": "The expression state named in ARO:3004921's own definition.",
    }
    return {
        "graph_id": "resistance",
        "title": f"{determinant} → AhpC overexpression → isoniazid resistance",
        "description": (
            "Curated resistance-causation graph for the Mycobacterium tuberculosis "
            "AhpC isoniazid leaf. The graph models only the child term's "
            "definition-supported mutation-to-overexpression route and does not "
            "promote the contradictory broad ahpC ancestors."
        ),
        "nodes": [
            copy.deepcopy(nodes["determinant"]),
            copy.deepcopy(nodes["mech0"]),
            copy.deepcopy(nodes["drug0"]),
            overexpression_node,
            copy.deepcopy(nodes["resistance"]),
        ],
        "edges": [edges[key] for key in FINAL_EDGE_ORDER],
    }


def _validate_record(record: dict[str, Any], target: Target) -> None:
    if record.get("identifier") != target.identifier:
        raise ValueError(
            f"{target.filename}: expected {target.identifier}, found "
            f"{record.get('identifier')}"
        )
    if not record.get("label"):
        raise ValueError(f"{target.identifier}: missing label")
    if not record.get("definition"):
        raise ValueError(f"{target.identifier}: missing definition")

    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1:
        raise ValueError(f"{target.identifier}: expected exactly one resistance graph")


def _validate_graph(graph: dict[str, Any], target: Target) -> None:
    nodes = _nodes_by_id(graph)
    missing_nodes = sorted(set(GRAPH_NODES) - {"overexpression"} - set(nodes))
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")

    seen: set[tuple[str, str, str]] = set()
    found: set[tuple[str, str, str]] = set()
    for edge in _dicts(graph.get("edges")):
        key = _edge_key(edge)
        if key not in INITIAL_EDGE_KEYS and key not in FINAL_EDGE_ORDER:
            raise ValueError(f"{target.identifier}: unexpected edge {key}")
        if key in seen:
            raise ValueError(f"{target.identifier}: duplicate edge {key}")
        seen.add(key)
        if key in INITIAL_EDGE_KEYS:
            found.add(key)

    missing_edges = sorted(INITIAL_EDGE_KEYS - found)
    if missing_edges:
        missing = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in missing_edges)
        raise ValueError(f"{target.identifier}: missing edge(s): {missing}")


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    _validate_record(record, target)

    graph = _dicts(record["causal_graphs"])[0]
    _validate_graph(graph, target)

    out = copy.deepcopy(record)
    out["mapping_status"] = "REVIEWED"
    out["causal_graphs"] = [_canonical_graph(record, graph)]
    return out, out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    target = TARGET_BY_FILENAME.get(path.name)
    if target is None:
        raise ValueError(f"{path}: not an AhpC overexpression target")

    enriched, changed = enrich_record(record, target)
    out = text.replace("mapping_status: SEEDED", "mapping_status: REVIEWED", 1)
    out = replace_block(out, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    if HISTORY_ACTION not in out:
        out = append_to_section(out, "curation_history", _dump({"curation_history": [HISTORY_EVENT]}))
        changed = True

    if "&id" in out or "*id" in out:
        raise ValueError(f"{path}: YAML anchors leaked into output")
    return out, changed or out != text


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
        help="ARO directory or the AhpC overexpression YAML file",
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
