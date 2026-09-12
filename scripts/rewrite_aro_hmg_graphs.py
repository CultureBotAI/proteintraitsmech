#!/usr/bin/env python3
"""Rewrite HMG-CoA reductase mutation triazole-resistance graphs.

The HMG-CoA reductase-encoding parent still has a draft graph, and its
Aspergillus Hmg1 child has a reviewed graph with an ungrounded HMG-CoA
reductase activity node. This updater gives both records the same conservative
shape: mutation-mediated resistance to triazoles plus the grounded enzyme
activity asserted by the record definitions.

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

HISTORY_CURATOR = "codex-causal-graph-quality"
HISTORY_ACTION = "Grounded HMG-CoA reductase mutation graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-08T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

MUTATION_EVIDENCE = {
    "reference": "ARO:3000212",
    "snippet": (
        "Point mutations in the DNA may lead to an altered gene product that "
        "may result in antibiotic resistance."
    ),
    "notes": "CARD definition for mutation conferring antibiotic resistance.",
}

HMG_PARENT_EVIDENCE = {
    "reference": "ARO:3007668",
    "snippet": (
        "HMG-CoA reductase-encoding genes which include mutations to confer "
        "resistance to antifungal drug compounds."
    ),
    "notes": "CARD definition for HMG-CoA reductase-encoding genes.",
}

HMG_ACTIVITY_EVIDENCE = {
    "reference": "GO:0004420",
    "snippet": (
        "Catalysis of the reaction: (R)-mevalonate + CoA + 2 NADP+ = "
        "(S)-3-hydroxy-3-methylglutaryl-CoA + 2 H+ + 2 NADPH."
    ),
    "notes": "Gene Ontology definition for HMG-CoA reductase (NADPH) activity.",
}

RYBAK_HMG1_EVIDENCE = {
    "reference": "PMID:30940706",
    "snippet": (
        "Mutations in hmg1, Challenging the Paradigm of Clinical Triazole "
        "Resistance in Aspergillus fumigatus"
    ),
    "notes": (
        "Rybak et al. 2019 is the CARD-cited report for the Hmg1 "
        "triazole-resistance branch."
    ),
}

TRIAZOLE_EVIDENCE = {
    "reference": "ARO:3007499",
    "snippet": "triazole antibiotic",
    "notes": "ARO drug-class term for triazole antibiotics.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "mutation conferring antibiotic resistance",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3000212",
}

DRUG_NODE = {
    "node_id": "drug0",
    "label": "triazole antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:3007499",
}

HMG_ACTIVITY_NODE = {
    "node_id": "hmgcoa",
    "label": "hydroxymethylglutaryl-CoA reductase (NADPH) activity",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "GO:0004420",
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

INPUT_ALLOWED_EDGE_KEYS = {
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("determinant", "ARO:2000001", "drug0"),
    ("determinant", "RO:0002327", "hmgcoa"),
}

OUTPUT_EDGE_KEYS = INPUT_ALLOWED_EDGE_KEYS


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str


_TARGET_ROWS = """
ARO:3007668 hmg-coa-reductase-encoding-genes-aro3007668.yaml
ARO:3007670 aspergillus-spp-hmg1-with-mutations-conferring-resistance-to-triazoles-antibioti-aro3007670.yaml
"""

TARGETS: tuple[Target, ...] = tuple(
    Target(identifier, filename)
    for identifier, filename in (line.split() for line in _TARGET_ROWS.strip().splitlines())
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


def _unique_evidence(*items: dict[str, Any]) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
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
        evidence.append(copy.deepcopy(item))
    return evidence


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


def _record_evidence(record: dict[str, Any]) -> dict[str, str]:
    return {
        "reference": str(record["identifier"]),
        "snippet": str(record["definition"]),
        "notes": f"CARD definition for {record['label']}.",
    }


def _nodes_by_id(graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(node["node_id"]): node
        for node in _dicts(graph.get("nodes"))
        if "node_id" in node
    }


def _determinant_node(record: dict[str, Any]) -> dict[str, str]:
    return {
        "node_id": "determinant",
        "label": str(record["label"]),
        "node_type": "PROTEIN",
        "grounding": str(record["identifier"]),
    }


def _drug_relation_evidence(graph: dict[str, Any]) -> list[dict[str, Any]]:
    relation_evidence: list[dict[str, Any]] = []
    for edge in _dicts(graph.get("edges")):
        if _edge_key(edge) != ("determinant", "ARO:2000001", "drug0"):
            continue
        relation_evidence.extend(
            item
            for item in _dicts(edge.get("evidence"))
            if str(item.get("snippet", "")).startswith(
                "relationship: confers_resistance_to_drug_class "
            )
        )
    if not relation_evidence:
        raise ValueError("missing drug relationship evidence")
    return copy.deepcopy(relation_evidence)


def _validate_graph(graph: dict[str, Any], target: Target) -> None:
    nodes = _nodes_by_id(graph)
    required_nodes = {"determinant", "mech0", "drug0", "resistance"}
    missing_nodes = sorted(required_nodes - set(nodes))
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")

    found: set[tuple[str, str, str]] = set()
    seen: set[tuple[str, str, str]] = set()
    for edge in _dicts(graph.get("edges")):
        key = _edge_key(edge)
        if key not in INPUT_ALLOWED_EDGE_KEYS:
            raise ValueError(f"{target.identifier}: unexpected edge {key[0]} -> {key[2]}")
        if key in seen:
            raise ValueError(f"{target.identifier}: duplicate edge {key[0]} -> {key[2]}")
        seen.add(key)
        found.add(key)

    missing_edges = sorted(
        key for key in INPUT_ALLOWED_EDGE_KEYS if key[2] != "hmgcoa" and key not in found
    )
    if missing_edges:
        missing = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in missing_edges)
        raise ValueError(f"{target.identifier}: missing edge(s): {missing}")


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
    if len(graphs) != 1 or graphs[0].get("graph_id") not in {
        "resistance",
        "resistance-draft",
    }:
        raise ValueError(f"{target.identifier}: expected exactly one resistance graph")
    _validate_graph(graphs[0], target)


def _graph(record: dict[str, Any], old_graph: dict[str, Any]) -> dict[str, Any]:
    record_evidence = _record_evidence(record)
    mutation_evidence = (
        record_evidence,
        HMG_PARENT_EVIDENCE,
        MUTATION_EVIDENCE,
        RYBAK_HMG1_EVIDENCE,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → HMG-CoA reductase mutation → triazole resistance",
        "description": (
            "Conservative graph for HMG-CoA reductase mutations that confer "
            "triazole resistance. The graph grounds the HMG-CoA reductase "
            "activity but does not assert an ergosterol-pathway intermediate "
            "that is absent from the ARO statements for this branch."
        ),
        "nodes": [
            _determinant_node(record),
            copy.deepcopy(MECHANISM_NODE),
            copy.deepcopy(DRUG_NODE),
            copy.deepcopy(HMG_ACTIVITY_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "ARO classifies this HMG-CoA reductase branch under mutation-mediated resistance.",
                *mutation_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Mutations in these HMG-CoA reductase-encoding genes confer resistance.",
                *mutation_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "Mutated HMG-CoA reductase-encoding genes confer triazole resistance.",
                *mutation_evidence,
            ),
            _edge(
                "determinant",
                "confers resistance to",
                "ARO:2000001",
                "drug0",
                "ARO maps the HMG-CoA reductase branch to triazole antibiotics.",
                *_drug_relation_evidence(old_graph),
                record_evidence,
                HMG_PARENT_EVIDENCE,
                TRIAZOLE_EVIDENCE,
            ),
            _edge(
                "determinant",
                "enables",
                "RO:0002327",
                "hmgcoa",
                "These determinants encode HMG-CoA reductase activity.",
                record_evidence,
                HMG_ACTIVITY_EVIDENCE,
            ),
        ],
    }


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    _validate_record(record, target)

    out = copy.deepcopy(record)
    out["causal_graphs"] = [_graph(record, record["causal_graphs"][0])]
    return out, out != record


def _promote_to_reviewed(text: str) -> str:
    return re.sub(
        r"^mapping_status:\s*SEEDED\s*$",
        "mapping_status: REVIEWED",
        text,
        count=1,
        flags=re.M,
    )


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not an HMG-CoA reductase target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, _ = enrich_record(record, target)
    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    out = _promote_to_reviewed(out)
    if HISTORY_ACTION not in out:
        out = append_to_section(out, "curation_history", _dump({"curation_history": [HISTORY_EVENT]}))

    if "&id" in out or "*id" in out:
        raise ValueError(f"{path}: YAML anchors leaked into output")
    return out, out != text


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
        help="ARO directory or one of the two HMG-CoA reductase YAML files",
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
