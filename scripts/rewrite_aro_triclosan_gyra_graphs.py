#!/usr/bin/env python3
"""Prune triclosan-resistant gyrA records to conservative mutation graphs.

CARD's triclosan gyrA records state that the resistance mechanism is unclear and
probably indirect through altered stress-response pathways. The current graphs
import a direct loss-of-topoisomerase-binding path that belongs to other
topoisomerase branches. This updater keeps the mutation mechanism and
disinfectant-class relation, removes the unsupported binding-loss side path,
and preserves the literature DOI citation already carried by the records.

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

HISTORY_ACTION = "Pruned triclosan gyrA graphs to conservative mutation core"
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

CORE_EDGE_ORDER = (
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("determinant", "ARO:2000001", "drug0"),
)
EXPECTED_EDGE_KEYS = CORE_EDGE_ORDER + (
    ("determinant", "RO:0000086", "binding_loss"),
    ("drug0", "RO:0002212", "dna_synth"),
    ("binding_loss", "RO:0002411", "dna_synth"),
)

PARENT_EVIDENCE = {
    "reference": "ARO:3004333",
    "snippet": (
        "DNA gyrase is responsible for DNA supercoiling and consists of two "
        "alpha and two beta subunits. Point mutations in gyrA have been shown "
        "to decrease susceptibility to the antibiotic triclosan. Although the "
        "mechanism is unclear, it is hypothesized that changes in supercoiling "
        "activity of mutant DNA gyrase proteins alters expression of stress "
        "response pathways thereby indirectly decreasing triclosan "
        "susceptibility. It has been shown that triclosan does not interact "
        "directly with gyrA."
    ),
    "notes": "CARD definition for the triclosan-resistant gyrA parent term.",
}

MUTATION_EVIDENCE = {
    "reference": "ARO:3000212",
    "snippet": (
        "Point mutations in the DNA may lead to an altered gene product that may "
        "result in antibiotic resistance. Examples included modified antibiotic "
        "targets with lower binding affinities and the deactivation of repressors "
        "that result in increased expression of genes that inactivate or pump out "
        "antibiotics."
    ),
    "notes": "CARD definition for the broad mutation-conferring resistance mechanism.",
}

DRUG_CLASS_EVIDENCE = {
    "reference": "ARO:3005386",
    "snippet": "disinfecting agents and antiseptics",
    "notes": "ARO drug-class term for the grounded disinfecting-agent node.",
}

EDGE_DESCRIPTIONS = {
    ("determinant", "RO:0000056", "mech0"): (
        "ARO classifies triclosan-resistant gyrA determinants under mutation-conferring "
        "antibiotic resistance."
    ),
    ("mech0", "RO:0002411", "resistance"): (
        "The inherited mutation mechanism is upstream of decreased triclosan "
        "susceptibility."
    ),
    ("determinant", "RO:0002411", "resistance"): (
        "CARD states that these gyrA point mutations decrease triclosan "
        "susceptibility through an unclear, probably indirect route."
    ),
    ("determinant", "ARO:2000001", "drug0"): (
        "ARO maps this determinant or its triclosan-resistant gyrA parent to "
        "disinfecting agents and antiseptics."
    ),
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str

    @property
    def is_parent(self) -> bool:
        return self.identifier == "ARO:3004333"


TARGETS = (
    Target("ARO:3004333", "triclosan-resistant-gyra-aro3004333.yaml"),
    Target(
        "ARO:3004335",
        "escherichia-coli-gyra-with-mutation-conferring-resistance-to-triclosan-"
        "aro3004335.yaml",
    ),
    Target(
        "ARO:3004334",
        "salmonella-enterica-gyra-with-mutation-conferring-resistance-to-triclosan-"
        "aro3004334.yaml",
    ),
)
TARGET_BY_FILENAME = {target.filename: target for target in TARGETS}

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


def _target_evidence(record: dict[str, Any]) -> dict[str, str]:
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


def _drug_relation_evidence(graph: dict[str, Any]) -> list[dict[str, Any]]:
    for edge in _dicts(graph.get("edges")):
        if _edge_key(edge) == ("determinant", "ARO:2000001", "drug0"):
            return [
                copy.deepcopy(item)
                for item in _dicts(edge.get("evidence"))
                if str(item.get("snippet", "")).startswith(
                    "relationship: confers_resistance_to_drug_class "
                )
            ]
    return []


def _validate_graph(graph: dict[str, Any]) -> None:
    found = {_edge_key(edge) for edge in _dicts(graph.get("edges"))}
    expected = set(EXPECTED_EDGE_KEYS)
    core = set(CORE_EDGE_ORDER)
    if found != expected and found != core:
        missing = expected - found
        unexpected = found - expected
        raise ValueError(f"unexpected triclosan gyrA edge set: {missing=} {unexpected=}")


def _edge(
    subject: str,
    predicate: str,
    predicate_id: str,
    object_: str,
    *evidence: dict[str, Any],
) -> dict[str, Any]:
    return {
        "subject": subject,
        "predicate": predicate,
        "predicate_id": predicate_id,
        "object": object_,
        "description": EDGE_DESCRIPTIONS[(subject, predicate_id, object_)],
        "evidence": _unique_evidence(*evidence),
    }


def _canonical_edges(
    record: dict[str, Any],
    graph: dict[str, Any],
    target: Target,
) -> list[dict[str, Any]]:
    local_evidence = () if target.is_parent else (_target_evidence(record),)
    source_evidence = _source_evidence(record)
    route_evidence = (
        PARENT_EVIDENCE,
        MUTATION_EVIDENCE,
        *local_evidence,
        *source_evidence,
    )
    drug_evidence = (
        *_drug_relation_evidence(graph),
        PARENT_EVIDENCE,
        DRUG_CLASS_EVIDENCE,
        *local_evidence,
        *source_evidence,
    )

    by_key = {
        ("determinant", "RO:0000056", "mech0"): _edge(
            "determinant",
            "participates in (resistance mechanism)",
            "RO:0000056",
            "mech0",
            *route_evidence,
        ),
        ("mech0", "RO:0002411", "resistance"): _edge(
            "mech0",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            *route_evidence,
        ),
        ("determinant", "RO:0002411", "resistance"): _edge(
            "determinant",
            "causally upstream of (confers resistance)",
            "RO:0002411",
            "resistance",
            *route_evidence,
        ),
        ("determinant", "ARO:2000001", "drug0"): _edge(
            "determinant",
            "confers resistance to (drug class)",
            "ARO:2000001",
            "drug0",
            *drug_evidence,
        ),
    }
    return [by_key[key] for key in CORE_EDGE_ORDER]


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != target.identifier:
        raise ValueError(f"expected {target.identifier}, found {record.get('identifier')}")

    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1:
        raise ValueError(f"{target.identifier}: expected exactly one resistance graph")

    graph = graphs[0]
    _validate_graph(graph)
    nodes = _nodes_by_id(graph)

    out = copy.deepcopy(record)
    out["causal_graphs"] = [
        {
            "graph_id": "resistance",
            "title": f"{record['label']} → conservative triclosan resistance core",
            "description": (
                "Conservative graph for a triclosan-resistant gyrA record. CARD "
                "states that the mechanism is unclear and probably indirect "
                "through altered stress-response pathways, so this graph keeps "
                "only the mutation mechanism and disinfectant-class assertion."
            ),
            "nodes": [
                copy.deepcopy(nodes["determinant"]),
                copy.deepcopy(nodes["mech0"]),
                copy.deepcopy(nodes["drug0"]),
                copy.deepcopy(RESISTANCE_NODE),
            ],
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
        raise ValueError(f"{path}: not a triclosan gyrA target")

    enriched, changed = enrich_record(record, target)
    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    parser.add_argument(
        "--path",
        type=Path,
        default=ARO_DIR,
        help="ARO directory or one of the triclosan gyrA YAML files",
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
