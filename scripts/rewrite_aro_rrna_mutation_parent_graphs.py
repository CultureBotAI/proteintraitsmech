#!/usr/bin/env python3
"""Ground and describe broad rRNA-mutation ARO causal graphs.

The two records handled here only support a shallow parent graph: rRNA sequence
variation in the bacterial ribosome participates in the inherited mutation
mechanism and confers resistance. This updater grounds the ribosome node to the
local GO ribosome class, describes every edge, and adds the direct 50S ARO
definition where the 50S child previously used only inherited parent evidence.

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

HISTORY_CURATOR = "codex-causal-graph-quality"
HISTORY_ACTION = "Supplemented broad rRNA mutation parent evidence"
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

ARO_50S_RRNA_EVIDENCE = {
    "reference": "ARO:3005003",
    "snippet": (
        "Mutations in the prokaryotic 50S ribosomal RNA subunit which disrupt binding "
        "sites and thereby reduce antibiotic efficacy."
    ),
    "notes": (
        "CARD's 50S rRNA mutation definition directly states that the subunit-specific "
        "mutations disrupt antibiotic binding sites."
    ),
}

MUTATION_MECHANISM_EVIDENCE = {
    "reference": "ARO:3000212",
    "snippet": (
        "Point mutations in the DNA may lead to an altered gene product that may "
        "result in antibiotic resistance."
    ),
    "notes": "CARD definition for mutation conferring antibiotic resistance.",
}

GO_RIBOSOME_EVIDENCE = {
    "reference": "GO:0005840",
    "snippet": (
        "It consists of two subunits, one large and one small, each containing only "
        "protein and RNA."
    ),
    "notes": (
        "GO's ribosome definition supports rRNA as a component of the broad ribosome "
        "node used by these parent graphs."
    ),
}

RIBOSOME_NODE = {
    "node_id": "ribosome",
    "label": "bacterial ribosome",
    "node_type": "CELLULAR_LOCALIZATION",
    "grounding": "GO:0005840",
    "description": (
        "Grounded to the broad GO ribosome class because the ARO evidence scopes this "
        "local node to the bacterial ribosome."
    ),
}

EDGE_DESCRIPTIONS = {
    ("determinant", "mech0"): (
        "CARD classifies rRNA mutations under mutation conferring antibiotic "
        "resistance."
    ),
    ("mech0", "resistance"): (
        "The inherited mutation mechanism represents rRNA sequence changes that "
        "reduce efficacy of ribosome-targeting antibiotics."
    ),
    ("determinant", "resistance"): (
        "SNPs in the modeled rRNA are the determinant-level cause of reduced efficacy "
        "for antibiotics that target the bacterial ribosome."
    ),
    ("determinant", "ribosome"): (
        "The mutated rRNA is modeled as part of the ribosome to identify the cellular "
        "target of these resistance-conferring changes."
    ),
}

EXPECTED_EDGES = set(EDGE_DESCRIPTIONS)


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    extra_evidence: dict[tuple[str, str], list[dict[str, str]]]


TARGETS = {
    "ARO:3000328": Target(
        identifier="ARO:3000328",
        filename="rrna-with-mutation-conferring-antibiotic-resistance-aro3000328.yaml",
        extra_evidence={
            ("determinant", "mech0"): [MUTATION_MECHANISM_EVIDENCE],
            ("mech0", "resistance"): [MUTATION_MECHANISM_EVIDENCE],
            ("determinant", "resistance"): [MUTATION_MECHANISM_EVIDENCE],
            ("determinant", "ribosome"): [GO_RIBOSOME_EVIDENCE],
        },
    ),
    "ARO:3005003": Target(
        identifier="ARO:3005003",
        filename="50s-rrna-with-mutation-conferring-antibiotic-resistance-aro3005003.yaml",
        extra_evidence={
            ("determinant", "mech0"): [ARO_50S_RRNA_EVIDENCE],
            ("mech0", "resistance"): [ARO_50S_RRNA_EVIDENCE],
            ("determinant", "resistance"): [ARO_50S_RRNA_EVIDENCE],
            ("determinant", "ribosome"): [
                ARO_50S_RRNA_EVIDENCE,
                GO_RIBOSOME_EVIDENCE,
            ],
        },
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


def _edge_key(edge: dict[str, Any]) -> tuple[str, str]:
    return edge.get("subject", ""), edge.get("object", "")


def _ordered_edge(edge: dict[str, Any]) -> dict[str, Any]:
    ordered = {
        "subject": edge["subject"],
        "predicate": edge["predicate"],
        "predicate_id": edge["predicate_id"],
        "object": edge["object"],
        "description": edge["description"],
        "evidence": edge["evidence"],
    }
    for key, value in edge.items():
        if key not in ordered:
            ordered[key] = value
    return ordered


def _extend_evidence(
    evidence: list[dict[str, Any]], extra: list[dict[str, str]]
) -> list[dict[str, Any]]:
    extra_references = {item["reference"] for item in extra}
    out = [
        copy.deepcopy(item)
        for item in evidence
        if item.get("reference") not in extra_references
    ]
    out.extend(copy.deepcopy(item) for item in extra)
    return out


def _enrich_ribosome_node(graph: dict[str, Any], target: Target) -> None:
    nodes = graph.get("nodes") or []
    for index, node in enumerate(nodes):
        if node.get("node_id") == "ribosome":
            nodes[index] = copy.deepcopy(RIBOSOME_NODE)
            return

    msg = f"{target.identifier}: missing ribosome node"
    raise ValueError(msg)


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != target.identifier:
        msg = f"expected {target.identifier}, found {record.get('identifier')}"
        raise ValueError(msg)

    out = copy.deepcopy(record)
    before = copy.deepcopy(out.get("causal_graphs"))
    graphs = out.get("causal_graphs") or []
    graph = next((item for item in graphs if item.get("graph_id") == "resistance"), None)
    if graph is None:
        msg = f"{target.identifier}: missing resistance causal graph"
        raise ValueError(msg)

    _enrich_ribosome_node(graph, target)

    seen: set[tuple[str, str]] = set()
    enriched_edges = []
    for edge in graph.get("edges", []):
        key = _edge_key(edge)
        if key in seen:
            msg = f"{target.identifier}: duplicate edge {key[0]} -> {key[1]}"
            raise ValueError(msg)
        if key not in EXPECTED_EDGES:
            msg = f"{target.identifier}: unexpected edge {key[0]} -> {key[1]}"
            raise ValueError(msg)

        edge["description"] = EDGE_DESCRIPTIONS[key]
        edge["evidence"] = _extend_evidence(
            edge["evidence"],
            target.extra_evidence.get(key, []),
        )
        enriched_edges.append(_ordered_edge(edge))
        seen.add(key)

    missing_edges = sorted(EXPECTED_EDGES - seen)
    if missing_edges:
        missing = ", ".join(f"{subject} -> {object_}" for subject, object_ in missing_edges)
        msg = f"{target.identifier}: missing edge(s): {missing}"
        raise ValueError(msg)

    graph["edges"] = enriched_edges
    return out, out.get("causal_graphs") != before


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: record is not a mapping")
    identifier = record.get("identifier")
    target = TARGETS.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not an rRNA mutation parent target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
    normalize_aliases = "&id" in text or "*id" in text
    if not changed and not normalize_aliases:
        return text, False

    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    history = record.get("curation_history") or []
    if not any(item.get("action") == HISTORY_ACTION for item in history):
        out = append_to_section(out, "curation_history", _dump({"curation_history": [HISTORY_EVENT]}))
    return out, True


def iter_target_paths(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if not path.is_dir():
        raise ValueError(f"{path} is neither a file nor a directory")
    return [path / target.filename for target in TARGETS.values()]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    parser.add_argument(
        "--path",
        type=Path,
        default=ARO_DIR,
        help="ARO directory or one of the two target YAML files",
    )
    args = parser.parse_args()

    changed = unchanged = 0
    problems: list[str] = []
    for path in iter_target_paths(args.path):
        if not path.exists():
            problems.append(f"{path}: missing")
            continue
        try:
            text = path.read_text(encoding="utf-8")
            out, did_change = enrich_text(text, path)
        except (OSError, ValueError, yaml.YAMLError) as exc:
            problems.append(str(exc))
            continue
        if not did_change:
            unchanged += 1
            continue
        changed += 1
        print(f"  {'wrote' if args.apply else 'would write'} {path.name}")
        if args.apply:
            path.write_text(out, encoding="utf-8")

    print(f"{'changed' if args.apply else 'would change'}: {changed}")
    print(f"already enriched: {unchanged}")
    for problem in problems:
        print(f"PROBLEM: {problem}", file=sys.stderr)
    if not args.apply:
        print("dry run -- pass --apply to write")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
