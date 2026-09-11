#!/usr/bin/env python3
"""Replace off-scope aminocoumarin evidence in zoliflodacin GyrB graphs.

The zoliflodacin-resistant GyrB parent and its Neisseria gonorrhoeae child were
promoted through the broad topoisomerase scaffold, but still carried one
aminocoumarin-specific GyrB snippet from a sibling branch. This updater keeps
the reviewed topology, replaces that off-scope support with zoliflodacin
evidence from the local ARO records, and describes every edge.

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

HISTORY_ACTION = "Replaced zoliflodacin GyrB evidence and edge descriptions"
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

EDGE_ORDER = (
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("determinant", "ARO:2000001", "drug0"),
    ("determinant", "RO:0000086", "binding_loss"),
    ("drug0", "RO:0002212", "dna_synth"),
    ("binding_loss", "RO:0002411", "dna_synth"),
)
EDGE_KEYS = set(EDGE_ORDER)

EDGE_DESCRIPTIONS = {
    ("determinant", "RO:0000056", "mech0"): (
        "ARO classifies zoliflodacin-resistant GyrB subunits as mutation-based "
        "resistance determinants."
    ),
    ("mech0", "RO:0002411", "resistance"): (
        "The GyrB mutation mechanism is upstream of zoliflodacin resistance."
    ),
    ("determinant", "RO:0002411", "resistance"): (
        "The mutated GyrB determinant decreases zoliflodacin affinity and confers "
        "resistance."
    ),
    ("determinant", "ARO:2000001", "drug0"): (
        "ARO maps this determinant or its direct GyrB parent to the "
        "zoliflodacin-like antibiotic drug class."
    ),
    ("determinant", "RO:0000086", "binding_loss"): (
        "The resistant GyrB determinant has the modeled quality of decreasing "
        "zoliflodacin binding."
    ),
    ("drug0", "RO:0002212", "dna_synth"): (
        "Zoliflodacin binding to DNA gyrase inhibits DNA synthesis."
    ),
    ("binding_loss", "RO:0002411", "dna_synth"): (
        "Reduced zoliflodacin binding lets the mutated gyrase continue supporting DNA "
        "synthesis."
    ),
}

ARO_3005000_EVIDENCE = {
    "reference": "ARO:3005000",
    "snippet": (
        "Point mutations in DNA gyrase subunit B (gyrB) of Neisseria gonorrhoeae "
        "can result in resistance to Zoliflodacin."
    ),
    "notes": "CARD definition for the zoliflodacin-resistant GyrB parent term.",
}

ARO_3004859_EVIDENCE = {
    "reference": "ARO:3004859",
    "snippet": "Point mutation in Neisseria gonorrhoea gyrase B decreases affinity to zoliflodacin antibiotic.",
    "notes": "CARD definition for the Neisseria gonorrhoeae zoliflodacin-resistant GyrB child.",
}

DRUG_CLASS_EVIDENCE = {
    "reference": "ARO:3007160",
    "snippet": "zoliflodacin-like antibiotic",
    "notes": "ARO drug-class term for the grounded zoliflodacin-like antibiotic node.",
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


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str

    @property
    def is_child(self) -> bool:
        return self.identifier == "ARO:3004859"


TARGETS = (
    Target("ARO:3005000", "zoliflodacin-resistant-gyrb-aro3005000.yaml"),
    Target(
        "ARO:3004859",
        "neisseria-gonorrhoeae-gyrb-conferring-resistance-to-zoliflodacin-aro3004859.yaml",
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


def _drug_relation_evidence(edge: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        copy.deepcopy(item)
        for item in _dicts(edge.get("evidence"))
        if str(item.get("snippet", "")).startswith(
            "relationship: confers_resistance_to_drug_class "
        )
    ]


def _validate_graph(graph: dict[str, Any], target: Target) -> None:
    if graph.get("graph_id") != "resistance":
        raise ValueError(f"{target.identifier}: expected the reviewed resistance graph")

    found: set[tuple[str, str, str]] = set()
    for edge in _dicts(graph.get("edges")):
        key = _edge_key(edge)
        if key not in EDGE_KEYS:
            raise ValueError(f"{target.identifier}: unexpected edge {key[0]} -> {key[2]}")
        if key in found:
            raise ValueError(f"{target.identifier}: duplicate edge {key[0]} -> {key[2]}")
        found.add(key)

    missing = EDGE_KEYS - found
    if missing:
        missing_text = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in sorted(missing))
        raise ValueError(f"{target.identifier}: missing edge(s): {missing_text}")


def _evidence_for_key(
    key: tuple[str, str, str],
    edge: dict[str, Any],
    target: Target,
    source_evidence: tuple[dict[str, str], ...],
) -> list[dict[str, Any]]:
    child_evidence = (ARO_3004859_EVIDENCE,) if target.is_child else ()
    target_evidence = (
        ARO_3005000_EVIDENCE,
        MUTATION_EVIDENCE,
        *child_evidence,
        *source_evidence,
    )

    if key == ("determinant", "ARO:2000001", "drug0"):
        return _unique_evidence(
            *_drug_relation_evidence(edge),
            ARO_3005000_EVIDENCE,
            *child_evidence,
            DRUG_CLASS_EVIDENCE,
            *source_evidence,
        )
    return _unique_evidence(
        *(
            item
            for item in _dicts(edge.get("evidence"))
            if item.get("reference") != "ARO:3000479"
        ),
        *target_evidence,
    )


def _rewrite_edge(
    edge: dict[str, Any],
    target: Target,
    source_evidence: tuple[dict[str, str], ...],
) -> dict[str, Any]:
    key = _edge_key(edge)
    return {
        "subject": edge["subject"],
        "predicate": edge["predicate"],
        "predicate_id": edge["predicate_id"],
        "object": edge["object"],
        "description": EDGE_DESCRIPTIONS[key],
        "evidence": _evidence_for_key(key, edge, target, source_evidence),
    }


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != target.identifier:
        raise ValueError(f"expected {target.identifier}, found {record.get('identifier')}")

    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1:
        raise ValueError(f"{target.identifier}: expected exactly one resistance graph")

    graph = graphs[0]
    _validate_graph(graph, target)

    source_evidence = _source_evidence(record)
    edges_by_key = {_edge_key(edge): edge for edge in _dicts(graph.get("edges"))}
    rewritten = copy.deepcopy(record)
    rewritten_graph = copy.deepcopy(graph)
    rewritten_graph["edges"] = [
        _rewrite_edge(edges_by_key[key], target, source_evidence) for key in EDGE_ORDER
    ]
    rewritten["causal_graphs"] = [rewritten_graph]
    return rewritten, rewritten != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: record is not a mapping")

    target = TARGET_BY_FILENAME.get(path.name)
    if target is None:
        raise ValueError(f"{path}: not a zoliflodacin GyrB target")

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
        help="ARO directory or one of the zoliflodacin GyrB YAML files",
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
