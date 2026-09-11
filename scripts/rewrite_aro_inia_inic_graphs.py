#!/usr/bin/env python3
"""Prune iniA/iniC drug-specific graphs to a mutation core.

The drug-specific iniA/iniC records inherit a broad possible MDR-pump-like
mechanism from their antibiotic-resistant iniA/iniC parents. Their own CARD
definitions support mutation-conferring resistance, not direct efflux, so this
updater drops the auto-scaffolded antibiotic-efflux side path.

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

HISTORY_ACTION = "Pruned iniA/iniC drug-specific graphs to a mutation core"
BROAD_PARENT_ACTION = (
    "Removed weak antibiotic-resistant iniA/iniC parent drafts after curating drug-specific "
    "mutation records"
)
HISTORY_TIMESTAMP = "2026-09-11T00:00:00Z"
HISTORY_CURATOR = "codex-causal-graph-quality"

EFFLUX_EDGE_KEYS = {
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
}
MUTATION_INITIAL_KEYS = {
    ("determinant", "RO:0000056", "mech1"),
    ("mech1", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
}
MUTATION_FINAL_KEYS = {
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
}
DRUG_KEY = ("determinant", "ARO:2000001", "drug0")
FINAL_EDGE_ORDER = (
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("determinant", "ARO:2000001", "drug0"),
)

MUTATION_EVIDENCE = {
    "reference": "ARO:3000212",
    "snippet": (
        "Point mutations in the DNA may lead to an altered gene product that "
        "may result in antibiotic resistance. Examples included modified "
        "antibiotic targets with lower binding affinities and the deactivation "
        "of repressors that result in increased expression of genes that "
        "inactivate or pump out antibiotics."
    ),
    "notes": "CARD definition for the broad mutation-conferring resistance mechanism.",
}

POLYAMINE_EVIDENCE = {
    "reference": "ARO:3000527",
    "snippet": "polyamine antibiotic",
    "notes": "ARO drug-class term for the grounded polyamine antibiotic node.",
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

_TOP_KEY = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*:")


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    family_identifier: str
    family_label: str
    family_definition: str
    drug_name: str
    has_drug_node: bool
    action: str = HISTORY_ACTION
    remove_graph: bool = False

    @property
    def is_family(self) -> bool:
        return self.identifier == self.family_identifier

    @property
    def family_evidence(self) -> dict[str, str]:
        return {
            "reference": self.family_identifier,
            "snippet": self.family_definition,
            "notes": f"CARD definition for the {self.family_label} parent.",
        }


INIA_ETHAMBUTOL = (
    "ARO:3003447",
    "ethambutol-resistant iniA",
    "Mutations that occurs on the iniA genes resulting in the resistance to ethambutol.",
)
INIC_ETHAMBUTOL = (
    "ARO:3003450",
    "ethambutol-resistant iniC",
    "Mutations that occurs on the iniC genes resulting in the resistance to ethambutol.",
)
INIA_ISONIAZID = (
    "ARO:3007799",
    "isoniazid-resistant iniA",
    "Mutations that occurs on the iniA genes resulting in the resistance to isoniazid.",
)

TARGETS = (
    Target(
        "ARO:3003447",
        "ethambutol-resistant-inia-aro3003447.yaml",
        *INIA_ETHAMBUTOL,
        "ethambutol",
        True,
    ),
    Target(
        "ARO:3003448",
        "mycobacterium-tuberculosis-inia-mutant-conferring-resistance-to-ethambutol-"
        "aro3003448.yaml",
        *INIA_ETHAMBUTOL,
        "ethambutol",
        True,
    ),
    Target(
        "ARO:3003450",
        "ethambutol-resistant-inic-aro3003450.yaml",
        *INIC_ETHAMBUTOL,
        "ethambutol",
        True,
    ),
    Target(
        "ARO:3003451",
        "mycobacterium-tuberculosis-inic-mutant-conferring-resistance-to-ethambutol-"
        "aro3003451.yaml",
        *INIC_ETHAMBUTOL,
        "ethambutol",
        True,
    ),
    Target(
        "ARO:3007799",
        "isoniazid-resistant-inia-aro3007799.yaml",
        *INIA_ISONIAZID,
        "isoniazid",
        False,
    ),
    Target(
        "ARO:3007798",
        "mycobacterium-tuberculosis-inia-mutations-conferring-resistance-to-"
        "isoniazid-aro3007798.yaml",
        *INIA_ISONIAZID,
        "isoniazid",
        False,
    ),
    Target(
        "ARO:3003446",
        "antibiotic-resistant-inia-aro3003446.yaml",
        "",
        "",
        "",
        "",
        False,
        BROAD_PARENT_ACTION,
        True,
    ),
    Target(
        "ARO:3003449",
        "antibiotic-resistant-inic-aro3003449.yaml",
        "",
        "",
        "",
        "",
        False,
        BROAD_PARENT_ACTION,
        True,
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


def _remove_block(text: str, key: str) -> str:
    lines = text.splitlines(keepends=True)
    start = next((i for i, line in enumerate(lines) if line.startswith(f"{key}:")), None)
    if start is None:
        return text

    end = start + 1
    while end < len(lines) and not (lines[end].strip() and _TOP_KEY.match(lines[end])):
        end += 1
    return "".join(lines[:start]) + "".join(lines[end:])


def _history_event(action: str) -> dict[str, Any]:
    return {
        "timestamp": HISTORY_TIMESTAMP,
        "curator": HISTORY_CURATOR,
        "action": action,
        "llm_assisted": True,
    }


def _has_history_action(text: str, action: str) -> bool:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        return False
    history = record.get("curation_history")
    if not isinstance(history, list):
        return False
    return any(isinstance(event, dict) and event.get("action") == action for event in history)


def _append_history_once(text: str, target: Target) -> str:
    if _has_history_action(text, target.action):
        return text
    return append_to_section(
        text,
        "curation_history",
        _dump({"curation_history": [_history_event(target.action)]}),
    )


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


def _edge_evidence(graph: dict[str, Any], key: tuple[str, str, str]) -> list[dict[str, Any]]:
    for edge in _dicts(graph.get("edges")):
        if _edge_key(edge) == key:
            return copy.deepcopy(_dicts(edge.get("evidence")))
    return []


def _relation_evidence(
    graph: dict[str, Any],
    key: tuple[str, str, str],
    relation: str,
) -> list[dict[str, Any]]:
    return [
        item
        for item in _edge_evidence(graph, key)
        if str(item.get("snippet", "")).startswith(f"relationship: {relation} ")
    ]


def _initial_edge_keys(target: Target) -> set[tuple[str, str, str]]:
    keys = EFFLUX_EDGE_KEYS | MUTATION_INITIAL_KEYS
    if target.has_drug_node:
        keys = keys | {DRUG_KEY}
    return keys


def _final_edge_keys(target: Target) -> set[tuple[str, str, str]]:
    keys = set(MUTATION_FINAL_KEYS)
    if target.has_drug_node:
        keys.add(DRUG_KEY)
    return keys


def _validate_graph(graph: dict[str, Any], target: Target) -> None:
    found = {_edge_key(edge) for edge in _dicts(graph.get("edges"))}
    initial = _initial_edge_keys(target)
    final = _final_edge_keys(target)
    if found != initial and found != final:
        expected = initial | final
        unexpected = found - expected
        raise ValueError(
            f"{target.identifier}: unexpected edge set: "
            f"missing_initial={initial - found} missing_final={final - found} "
            f"unexpected={unexpected}"
        )


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


def _canonical_edges(
    record: dict[str, Any],
    graph: dict[str, Any],
    target: Target,
) -> list[dict[str, Any]]:
    local_evidence = () if target.is_family else (_record_evidence(record),)
    source_evidence = _source_evidence(record)
    route_evidence = (target.family_evidence, MUTATION_EVIDENCE, *local_evidence, *source_evidence)
    resistance_evidence = (
        target.family_evidence,
        MUTATION_EVIDENCE,
        *local_evidence,
        *_relation_evidence(
            graph,
            ("determinant", "RO:0002411", "resistance"),
            "confers_resistance_to_antibiotic",
        ),
        *source_evidence,
    )

    edges = {
        ("determinant", "RO:0000056", "mech0"): _edge(
            "determinant",
            "participates in (resistance mechanism)",
            "RO:0000056",
            "mech0",
            "ARO classifies this drug-specific iniA/iniC determinant under "
            "mutation-conferring antibiotic resistance.",
            *route_evidence,
        ),
        ("mech0", "RO:0002411", "resistance"): _edge(
            "mech0",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            f"The inherited mutation mechanism is upstream of {target.drug_name} resistance.",
            *resistance_evidence,
        ),
        ("determinant", "RO:0002411", "resistance"): _edge(
            "determinant",
            "causally upstream of (confers resistance)",
            "RO:0002411",
            "resistance",
            f"CARD states that mutations in this determinant confer {target.drug_name} "
            "resistance.",
            *resistance_evidence,
        ),
    }

    if target.has_drug_node:
        edges[DRUG_KEY] = _edge(
            "determinant",
            "confers resistance to (drug class)",
            "ARO:2000001",
            "drug0",
            "ARO maps this determinant or its drug-specific parent to the polyamine "
            "antibiotic drug class.",
            *_relation_evidence(
                graph,
                DRUG_KEY,
                "confers_resistance_to_drug_class",
            ),
            target.family_evidence,
            POLYAMINE_EVIDENCE,
            *local_evidence,
            *source_evidence,
        )

    return [edges[key] for key in FINAL_EDGE_ORDER if key in edges]


def _mutation_node(nodes: dict[str, dict[str, Any]]) -> dict[str, Any]:
    node = copy.deepcopy(nodes.get("mech1") or nodes["mech0"])
    node["node_id"] = "mech0"
    return node


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    if target.remove_graph:
        raise ValueError(f"{target.identifier}: no canonical graph for broad parent")
    if record.get("identifier") != target.identifier:
        raise ValueError(f"expected {target.identifier}, found {record.get('identifier')}")

    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1:
        raise ValueError(f"{target.identifier}: expected exactly one resistance graph")

    graph = graphs[0]
    _validate_graph(graph, target)
    nodes = _nodes_by_id(graph)

    out = copy.deepcopy(record)
    out["mapping_status"] = "REVIEWED"
    node_order = ["determinant", "mech0"]
    if target.has_drug_node:
        node_order.append("drug0")
    node_order.append("resistance")
    nodes_out = [
        _mutation_node(nodes) if node_id == "mech0" else copy.deepcopy(nodes[node_id])
        for node_id in node_order
    ]

    out["causal_graphs"] = [
        {
            "graph_id": "resistance",
            "title": f"{record['label']} → {target.drug_name} resistance mutation core",
            "description": (
                "Conservative graph for a drug-specific iniA/iniC determinant. "
                "The graph keeps CARD's broad mutation mechanism and prunes the "
                "weak inherited antibiotic-efflux side path."
            ),
            "nodes": nodes_out,
            "edges": _canonical_edges(record, graph, target),
        }
    ]
    return out, out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: record is not a mapping")

    target = TARGET_BY_FILENAME.get(path.name)
    if target is None:
        raise ValueError(f"{path}: not an iniA/iniC target")

    found = record.get("identifier")
    if found != target.identifier:
        raise ValueError(f"{path}: expected {target.identifier}, found {found}")

    if target.remove_graph:
        out = _remove_block(text, "causal_graphs")
        out = _append_history_once(out, target)
        return out, out != text

    enriched, changed = enrich_record(record, target)
    out = text.replace("mapping_status: SEEDED", "mapping_status: REVIEWED", 1)
    out = replace_block(out, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    out = _append_history_once(out, target)

    if "&id" in out or "*id" in out:
        raise ValueError(f"{path}: YAML anchors leaked into output")
    return out, changed or out != text


def iter_target_paths(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if not path.is_dir():
        raise ValueError(f"{path} is neither a file nor a directory")
    return [path / target.filename for target in TARGETS]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    parser.add_argument(
        "--path",
        type=Path,
        default=ARO_DIR,
        help="ARO directory or one iniA/iniC YAML file",
    )
    args = parser.parse_args()

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
