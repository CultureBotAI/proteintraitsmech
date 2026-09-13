#!/usr/bin/env python3
"""Ground and describe cycloserine-resistant ald graphs.

The ald parent and Mycobacterium tuberculosis ald child describe mutations in
alanine dehydrogenase that can make cycloserine fail. The ARO text only says
ald participates in cell-wall synthesis through L-alanine supply, so this
updater grounds L-alanine and peptidoglycan biosynthesis while preserving the
current conservative stop before any unasserted D-alanine mimicry edge.

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
HISTORY_ACTION = "Grounded cycloserine-resistant ald graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

PARENT_IDENTIFIER = "ARO:3004943"

ALD_PARENT_EVIDENCE = {
    "reference": PARENT_IDENTIFIER,
    "snippet": (
        "ald plays a role in cell wall synthesis as L-alanine is an important "
        "constituent of the peptidoglycan layer. Resistance due to mutations "
        "in ald can cause cycloserine to not function."
    ),
    "notes": "CARD definition for the cycloserine-resistant ald parent term.",
}

MUTATION_EVIDENCE = {
    "reference": "ARO:3000212",
    "snippet": (
        "Point mutations in the DNA may lead to an altered gene product that may "
        "result in antibiotic resistance. Examples included modified antibiotic "
        "targets with lower binding affinities and the deactivation of "
        "repressors that result in increased expression of genes that "
        "inactivate or pump out antibiotics."
    ),
    "notes": "CARD definition for the broad mutation-conferring resistance mechanism.",
}

L_ALANINE_EVIDENCE = {
    "reference": "CHEBI:16977",
    "snippet": "The L-enantiomer of alanine.",
    "notes": "ChEBI definition for L-alanine.",
}

PEPTIDOGLYCAN_BIOSYNTHESIS_EVIDENCE = {
    "reference": "GO:0009252",
    "snippet": (
        "The chemical reactions and pathways resulting in the formation of "
        "peptidoglycans, any of a class of glycoconjugates found in bacterial "
        "cell walls and consisting of long glycan strands of alternating "
        "residues of beta-(1,4) linked N-acetylglucosamine and "
        "N-acetylmuramic acid, cross-linked by short peptides."
    ),
    "notes": "GO definition for peptidoglycan biosynthetic process.",
}

CYCLOSERINE_DRUG_EVIDENCE = {
    "reference": PARENT_IDENTIFIER,
    "snippet": "relationship: confers_resistance_to_drug_class ARO:3007154 ! cycloserine-like antibiotic",
    "notes": (
        "ARO drug-class relationship asserted on the cycloserine-resistant ald "
        "parent and inherited by the Mycobacterium tuberculosis ald child."
    ),
}

CYCLOSERINE_CLASS_EVIDENCE = {
    "reference": "ARO:3007154",
    "snippet": "cycloserine-like antibiotic",
    "notes": "ARO drug-class term targeted by cycloserine-resistant ald records.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "mutation conferring antibiotic resistance",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3000212",
}

DRUG_NODE = {
    "node_id": "drug0",
    "label": "cycloserine-like antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:3007154",
}

L_ALANINE_NODE = {
    "node_id": "l_alanine",
    "label": "L-alanine",
    "node_type": "CHEMICAL",
    "grounding": "CHEBI:16977",
    "description": (
        "Grounded to ChEBI L-alanine, the alanine enantiomer named by CARD as "
        "an important constituent of the peptidoglycan layer."
    ),
}

WALL_SYNTHESIS_NODE = {
    "node_id": "wall_synthesis",
    "label": "peptidoglycan biosynthetic process",
    "node_type": "BIOLOGICAL_PROCESS",
    "grounding": "GO:0009252",
    "description": (
        "Grounded to peptidoglycan biosynthesis, matching CARD's statement "
        "that ald plays a role in cell-wall synthesis through L-alanine."
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
    ("determinant", "RO:0002411", "resistance"),
    ("determinant", "ARO:2000001", "drug0"),
    ("determinant", "RO:0000056", "wall_synthesis"),
}

LEGACY_ALANINE_EDGE_KEY = (
    "l_alanine",
    "BFO:0000050",
    "wall_synthesis",
)

CANONICAL_ALANINE_EDGE_KEY = (
    "wall_synthesis",
    "RO:0002233",
    "l_alanine",
)


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str

    @property
    def is_parent(self) -> bool:
        return self.identifier == PARENT_IDENTIFIER


TARGETS = {
    "ARO:3004943": Target(
        identifier="ARO:3004943",
        filename="cycloserine-resistant-ald-aro3004943.yaml",
    ),
    "ARO:3004945": Target(
        identifier="ARO:3004945",
        filename=(
            "mycobacterium-tuberculosis-ald-mutations-confer-resistance-to-"
            "cycloserine-aro3004945.yaml"
        ),
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


def _edge_key(edge: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(edge.get("subject", "")),
        str(edge.get("predicate_id", "")),
        str(edge.get("object", "")),
    )


def _canonical_edge_keys() -> set[tuple[str, str, str]]:
    return CORE_EDGE_KEYS | {CANONICAL_ALANINE_EDGE_KEY}


def _input_allowed_edges() -> set[tuple[str, str, str]]:
    return _canonical_edge_keys() | {LEGACY_ALANINE_EDGE_KEY}


def _target_evidence(record: dict[str, Any], target: Target) -> dict[str, str]:
    if target.is_parent:
        return ALD_PARENT_EVIDENCE
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
        for item in record.get("evidence") or []
        if isinstance(item, dict) and item.get("reference")
    )


def _ald_evidence(record: dict[str, Any], target: Target) -> tuple[dict[str, str], ...]:
    target_evidence = _target_evidence(record, target)
    if target.is_parent:
        return (target_evidence,)
    return (target_evidence, ALD_PARENT_EVIDENCE)


def _unique_evidence(evidence: tuple[dict[str, str], ...]) -> list[dict[str, str]]:
    unique: list[dict[str, str]] = []
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
        unique.append(copy.deepcopy(item))
    return unique


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


def _edge(
    subject: str,
    predicate: str,
    predicate_id: str,
    object_: str,
    description: str,
    evidence: tuple[dict[str, str], ...],
) -> dict[str, Any]:
    return _ordered_edge(
        {
            "subject": subject,
            "predicate": predicate,
            "predicate_id": predicate_id,
            "object": object_,
            "description": description,
            "evidence": _unique_evidence(evidence),
        }
    )


def _nodes_by_id(graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(node["node_id"]): node
        for node in graph.get("nodes") or []
        if isinstance(node, dict) and "node_id" in node
    }


def _validate_graph(graph: dict[str, Any], target: Target) -> None:
    nodes = _nodes_by_id(graph)
    missing_nodes = sorted(
        {
            "determinant",
            "mech0",
            "drug0",
            "l_alanine",
            "wall_synthesis",
            "resistance",
        }
        - set(nodes)
    )
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")

    found_edges = set()
    seen: set[tuple[str, str, str]] = set()
    for edge in graph.get("edges") or []:
        key = _edge_key(edge)
        if key not in _input_allowed_edges():
            raise ValueError(f"{target.identifier}: unexpected edge {key[0]} -> {key[2]}")
        if key in seen:
            raise ValueError(f"{target.identifier}: duplicate edge {key[0]} -> {key[2]}")
        seen.add(key)
        found_edges.add(key)

    missing_core = sorted(CORE_EDGE_KEYS - found_edges)
    if missing_core:
        missing = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in missing_core)
        raise ValueError(f"{target.identifier}: missing core edge(s): {missing}")

    has_alanine_edge = (
        LEGACY_ALANINE_EDGE_KEY in found_edges
        or CANONICAL_ALANINE_EDGE_KEY in found_edges
    )
    if not has_alanine_edge:
        raise ValueError(f"{target.identifier}: missing L-alanine cell-wall edge")


def _canonical_nodes(graph: dict[str, Any]) -> list[dict[str, Any]]:
    nodes = _nodes_by_id(graph)
    return [
        copy.deepcopy(nodes["determinant"]),
        copy.deepcopy(MECHANISM_NODE),
        copy.deepcopy(DRUG_NODE),
        copy.deepcopy(L_ALANINE_NODE),
        copy.deepcopy(WALL_SYNTHESIS_NODE),
        copy.deepcopy(RESISTANCE_NODE),
    ]


def _canonical_edges(record: dict[str, Any], target: Target) -> list[dict[str, Any]]:
    source_evidence = _source_evidence(record)
    ald_evidence = _ald_evidence(record, target)
    mutation_evidence = (*ald_evidence, MUTATION_EVIDENCE, *source_evidence)
    wall_evidence = (
        *ald_evidence,
        L_ALANINE_EVIDENCE,
        PEPTIDOGLYCAN_BIOSYNTHESIS_EVIDENCE,
        *source_evidence,
    )
    drug_evidence = (
        *ald_evidence,
        CYCLOSERINE_DRUG_EVIDENCE,
        CYCLOSERINE_CLASS_EVIDENCE,
        *source_evidence,
    )

    return [
        _edge(
            "determinant",
            "participates in (resistance mechanism)",
            "RO:0000056",
            "mech0",
            "ARO classifies cycloserine-resistant ald under mutation conferring resistance.",
            mutation_evidence,
        ),
        _edge(
            "mech0",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            "The ald variants are modeled under the broad mutation mechanism.",
            mutation_evidence,
        ),
        _edge(
            "determinant",
            "causally upstream of (confers resistance)",
            "RO:0002411",
            "resistance",
            (
                "Mutations in ald can cause cycloserine to not function while "
                "ald participates in peptidoglycan biosynthesis through "
                "L-alanine."
            ),
            mutation_evidence,
        ),
        _edge(
            "determinant",
            "confers resistance to",
            "ARO:2000001",
            "drug0",
            "ARO maps cycloserine-resistant ald to the cycloserine-like antibiotic class.",
            drug_evidence,
        ),
        _edge(
            "determinant",
            "participates in (peptidoglycan biosynthesis)",
            "RO:0000056",
            "wall_synthesis",
            (
                "The determinant participates in the peptidoglycan biosynthetic "
                "process through L-alanine supply to the peptidoglycan layer."
            ),
            wall_evidence,
        ),
        _edge(
            "wall_synthesis",
            "has input",
            "RO:0002233",
            "l_alanine",
            (
                "L-alanine is modeled as an input into peptidoglycan "
                "biosynthesis rather than as part of the biosynthetic process "
                "itself."
            ),
            wall_evidence,
        ),
    ]


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != target.identifier:
        raise ValueError(f"expected {target.identifier}, found {record.get('identifier')}")

    out = copy.deepcopy(record)
    before = copy.deepcopy(out.get("causal_graphs"))
    graphs = out.get("causal_graphs") or []
    graph = next((item for item in graphs if item.get("graph_id") == "resistance"), None)
    if graph is None:
        raise ValueError(f"{target.identifier}: missing resistance causal graph")

    _validate_graph(graph, target)
    graph["title"] = f"{record['label']} → L-alanine cell-wall synthesis → cycloserine resistance"
    graph["description"] = (
        "Conservative graph for cycloserine-resistant ald. The graph grounds "
        "L-alanine to CHEBI:16977 and cell-wall synthesis to GO:0009252 "
        "peptidoglycan biosynthesis, but stops before any unasserted "
        "cycloserine-to-D-alanine mimicry edge."
    )
    graph["nodes"] = _canonical_nodes(graph)
    graph["edges"] = _canonical_edges(out, target)
    return out, out.get("causal_graphs") != before


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: record is not a mapping")
    identifier = record.get("identifier")
    target = TARGETS.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not a cycloserine-resistant ald target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
    normalize_aliases = "&id" in text or "*id" in text
    if not changed and not normalize_aliases:
        return text, False

    out = replace_block(
        text,
        "causal_graphs",
        _dump({"causal_graphs": enriched["causal_graphs"]}),
    )
    if HISTORY_ACTION not in out:
        out = append_to_section(
            out,
            "curation_history",
            _dump({"curation_history": [HISTORY_EVENT]}),
        )
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
        help="ARO directory or one exact cycloserine-resistant ald YAML file",
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
