#!/usr/bin/env python3
"""Ground and complete cycloserine-resistant Alr graphs.

The Alr cycloserine parent and its Mycobacterium tuberculosis child both
describe alanine racemase mutations that can confer cycloserine resistance.
This updater grounds alanine racemase activity, L-alanine, D-alanine, and
peptidoglycan biosynthesis while preserving a conservative broad mutation
mechanism for the actual resistance route.

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
HISTORY_ACTION = "Grounded cycloserine-resistant Alr graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

PARENT_IDENTIFIER = "ARO:3004946"

CYCLOSERINE_ALR_EVIDENCE = {
    "reference": PARENT_IDENTIFIER,
    "snippet": (
        "Provides the D-alanine required for cell wall biosynthesis. Transforms "
        "L-alanine to D-alanine. Can confer resistance to cycloserine."
    ),
    "notes": "CARD definition for the cycloserine-resistant Alr parent term.",
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

ALR_ACTIVITY_EVIDENCE = {
    "reference": "GO:0008784",
    "snippet": "alanine racemase activity",
    "notes": "GO activity term matching CARD's L-alanine to D-alanine transformation.",
}

L_ALANINE_EVIDENCE = {
    "reference": "CHEBI:16977",
    "snippet": "The L-enantiomer of alanine.",
    "notes": "ChEBI definition for L-alanine.",
}

D_ALANINE_EVIDENCE = {
    "reference": "CHEBI:15570",
    "snippet": "The D-enantiomer of alanine.",
    "notes": "ChEBI definition for D-alanine.",
}

PEPTIDOGLYCAN_BIOSYNTHESIS_EVIDENCE = {
    "reference": "GO:0009252",
    "snippet": (
        "The chemical reactions and pathways resulting in the formation of "
        "peptidoglycans, any of a class of glycoconjugates found in bacterial "
        "cell walls and consisting of long glycan strands of alternating "
        "residues of beta-(1,4) linked N-acetylglucosamine and N-acetylmuramic "
        "acid, cross-linked by short peptides."
    ),
    "notes": "GO definition for peptidoglycan biosynthetic process.",
}

CYCLOSERINE_DRUG_EVIDENCE = {
    "reference": PARENT_IDENTIFIER,
    "snippet": "relationship: confers_resistance_to_drug_class ARO:3007154 ! cycloserine-like antibiotic",
    "notes": (
        "ARO drug-class relationship asserted on the cycloserine-resistant Alr "
        "parent and inherited by the Mycobacterium tuberculosis Alr child."
    ),
}

CYCLOSERINE_CLASS_EVIDENCE = {
    "reference": "ARO:3007154",
    "snippet": "cycloserine-like antibiotic",
    "notes": "ARO drug-class term targeted by cycloserine-resistant Alr records.",
}

DCS_INHIBITION_EVIDENCE = {
    "reference": "PMID:28971867",
    "snippet": "DCS inhibits Alr irreversibly by covalently bonding to PLP.",
    "notes": "Nakatani et al. summarize D-cycloserine inhibition of alanine racemase.",
}

MUTANT_ALR_EVIDENCE = {
    "reference": "PMID:28971867",
    "snippet": "these mutations likely confer resistance to d-cycloserine.",
    "notes": (
        "Nakatani et al. combined molecular modeling, MIC testing, and enzyme "
        "activity measurements on Mycobacterium tuberculosis Alr mutants."
    ),
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

ALR_ACTIVITY_NODE = {
    "node_id": "alr_activity",
    "label": "alanine racemase activity",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "GO:0008784",
    "description": (
        "Grounded to GO alanine racemase activity, matching CARD's statement "
        "that Alr transforms L-alanine to D-alanine."
    ),
}

L_ALANINE_NODE = {
    "node_id": "l_alanine",
    "label": "L-alanine",
    "node_type": "CHEMICAL",
    "grounding": "CHEBI:16977",
    "description": "ChEBI-grounded L-alanine, the substrate that Alr racemizes.",
}

D_ALANINE_NODE = {
    "node_id": "d_alanine",
    "label": "D-alanine",
    "node_type": "CHEMICAL",
    "grounding": "CHEBI:15570",
    "description": "ChEBI-grounded D-alanine, the Alr product used for cell-wall biosynthesis.",
}

WALL_SYNTHESIS_NODE = {
    "node_id": "wall_synthesis",
    "label": "peptidoglycan biosynthetic process",
    "node_type": "BIOLOGICAL_PROCESS",
    "grounding": "GO:0009252",
    "description": (
        "Grounded to peptidoglycan biosynthesis, matching CARD's statement "
        "that Alr supplies D-alanine for cell-wall biosynthesis."
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
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str

    @property
    def is_parent(self) -> bool:
        return self.identifier == PARENT_IDENTIFIER


TARGETS = {
    "ARO:3004946": Target(
        identifier="ARO:3004946",
        filename="cycloserine-resistant-alr-aro3004946.yaml",
    ),
    "ARO:3004947": Target(
        identifier="ARO:3004947",
        filename=(
            "mycobacterium-tuberculosis-alr-with-mutation-conferring-resistance-"
            "to-cycloserin-aro3004947.yaml"
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


def _dicts(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _nodes_by_id(graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(node["node_id"]): node
        for node in _dicts(graph.get("nodes"))
        if "node_id" in node
    }


def _edge_key(edge: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(edge.get("subject", "")),
        str(edge.get("predicate_id", "")),
        str(edge.get("object", "")),
    )


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


def _source_evidence(record: dict[str, Any]) -> tuple[dict[str, str], ...]:
    return tuple(
        {
            "reference": str(item["reference"]),
            "notes": str(item.get("notes") or "ARO citation for this record."),
        }
        for item in _dicts(record.get("evidence"))
        if item.get("reference")
    )


def _own_definition_evidence(record: dict[str, Any]) -> dict[str, str]:
    return {
        "reference": str(record["identifier"]),
        "snippet": str(record["definition"]),
        "notes": f"CARD definition for {record['label']}.",
    }


def _alr_evidence(
    record: dict[str, Any],
    target: Target,
) -> tuple[dict[str, str], ...]:
    if target.is_parent:
        return (_own_definition_evidence(record),)
    return (_own_definition_evidence(record), CYCLOSERINE_ALR_EVIDENCE)


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


def _input_graph(record: dict[str, Any]) -> dict[str, Any]:
    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1:
        raise ValueError(f"{record.get('identifier')}: expected exactly one causal graph")
    if graphs[0].get("graph_id") not in {"resistance", "resistance-draft"}:
        raise ValueError(f"{record.get('identifier')}: expected a resistance graph")
    return graphs[0]


def _validate_core_graph(graph: dict[str, Any], identifier: str) -> None:
    missing_nodes = sorted({"determinant", "mech0", "drug0", "resistance"} - _nodes_by_id(graph).keys())
    if missing_nodes:
        raise ValueError(f"{identifier}: missing node(s): {', '.join(missing_nodes)}")

    found: set[tuple[str, str, str]] = set()
    seen: set[tuple[str, str, str]] = set()
    for edge in _dicts(graph.get("edges")):
        key = _edge_key(edge)
        if key in seen:
            raise ValueError(f"{identifier}: duplicate edge {key[0]} -> {key[2]}")
        seen.add(key)
        found.add(key)

    missing_edges = sorted(CORE_EDGE_KEYS - found)
    if missing_edges:
        missing = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in missing_edges)
        raise ValueError(f"{identifier}: missing core edge(s): {missing}")


def _canonical_nodes(old_graph: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        copy.deepcopy(_nodes_by_id(old_graph)["determinant"]),
        copy.deepcopy(MECHANISM_NODE),
        copy.deepcopy(DRUG_NODE),
        copy.deepcopy(ALR_ACTIVITY_NODE),
        copy.deepcopy(L_ALANINE_NODE),
        copy.deepcopy(D_ALANINE_NODE),
        copy.deepcopy(WALL_SYNTHESIS_NODE),
        copy.deepcopy(RESISTANCE_NODE),
    ]


def _canonical_edges(record: dict[str, Any], target: Target) -> list[dict[str, Any]]:
    source_evidence = _source_evidence(record)
    alr_evidence = _alr_evidence(record, target)
    mutation_evidence = (*alr_evidence, MUTATION_EVIDENCE, MUTANT_ALR_EVIDENCE, *source_evidence)
    alr_activity_evidence = (
        *alr_evidence,
        ALR_ACTIVITY_EVIDENCE,
        DCS_INHIBITION_EVIDENCE,
        *source_evidence,
    )
    alanine_evidence = (
        *alr_evidence,
        ALR_ACTIVITY_EVIDENCE,
        L_ALANINE_EVIDENCE,
        D_ALANINE_EVIDENCE,
        PEPTIDOGLYCAN_BIOSYNTHESIS_EVIDENCE,
        *source_evidence,
    )
    drug_evidence = (
        *alr_evidence,
        CYCLOSERINE_DRUG_EVIDENCE,
        CYCLOSERINE_CLASS_EVIDENCE,
        *source_evidence,
    )
    inhibition_evidence = (
        *alr_evidence,
        CYCLOSERINE_CLASS_EVIDENCE,
        DCS_INHIBITION_EVIDENCE,
        *source_evidence,
    )

    return [
        _edge(
            "determinant",
            "participates in (resistance mechanism)",
            "RO:0000056",
            "mech0",
            "ARO classifies cycloserine-resistant Alr under mutation conferring resistance.",
            mutation_evidence,
        ),
        _edge(
            "mech0",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            "The Alr variants are modeled under the broad mutation mechanism.",
            mutation_evidence,
        ),
        _edge(
            "determinant",
            "causally upstream of (confers resistance)",
            "RO:0002411",
            "resistance",
            (
                "Alr mutations can confer cycloserine resistance while Alr "
                "continues to supply D-alanine for peptidoglycan biosynthesis."
            ),
            mutation_evidence,
        ),
        _edge(
            "determinant",
            "confers resistance to",
            "ARO:2000001",
            "drug0",
            "ARO maps cycloserine-resistant Alr to the cycloserine-like antibiotic class.",
            drug_evidence,
        ),
        _edge(
            "determinant",
            "enables",
            "RO:0002327",
            "alr_activity",
            "Alr enables alanine racemase activity.",
            alr_activity_evidence,
        ),
        _edge(
            "alr_activity",
            "has input",
            "RO:0002233",
            "l_alanine",
            "Alanine racemase activity transforms L-alanine as a substrate.",
            alanine_evidence,
        ),
        _edge(
            "alr_activity",
            "has output",
            "RO:0002234",
            "d_alanine",
            "Alanine racemase activity produces D-alanine.",
            alanine_evidence,
        ),
        _edge(
            "alr_activity",
            "part of (peptidoglycan biosynthesis)",
            "BFO:0000050",
            "wall_synthesis",
            "Alr-supplied D-alanine is required for cell-wall peptidoglycan biosynthesis.",
            alanine_evidence,
        ),
        _edge(
            "drug0",
            "negatively regulates",
            "RO:0002212",
            "alr_activity",
            "D-cycloserine inhibits Alr alanine racemase activity.",
            inhibition_evidence,
        ),
    ]


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != target.identifier:
        raise ValueError(f"expected {target.identifier}, found {record.get('identifier')}")

    graph = _input_graph(record)
    _validate_core_graph(graph, target.identifier)

    out = copy.deepcopy(record)
    new_graph = {
        "graph_id": "resistance",
        "title": f"{record['label']} → alanine racemase activity → cycloserine resistance",
        "description": (
            "Conservative graph for cycloserine-resistant Alr. The graph "
            "grounds Alr's L-alanine-to-D-alanine racemase activity and its "
            "connection to peptidoglycan biosynthesis, while keeping the "
            "broad ARO mutation mechanism as the causal resistance route."
        ),
        "nodes": _canonical_nodes(graph),
        "edges": _canonical_edges(record, target),
    }
    before = copy.deepcopy(out.get("causal_graphs"))
    out["causal_graphs"] = [new_graph]
    return out, out.get("causal_graphs") != before


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGETS.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not a cycloserine-resistant Alr target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

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
    return [path / target.filename for target in TARGETS.values()]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    parser.add_argument(
        "--path",
        type=Path,
        default=ARO_DIR,
        help="ARO directory or one exact cycloserine-resistant Alr YAML file",
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
