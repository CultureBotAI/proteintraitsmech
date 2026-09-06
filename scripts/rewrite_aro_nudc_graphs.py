#!/usr/bin/env python3
"""Ground ethionamide-resistant nudC NADH-pyrophosphatase graphs.

The ARO nudC branch names an NADH-pyrophosphatase activity and places the
enzyme in nicotinate/nicotinamide metabolism, but it does not state an
ethionamide prodrug-activation step. This updater grounds the side-path nodes
without adding that unsupported drug route.

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
HISTORY_ACTION = "Grounded ethionamide-resistant nudC NADH-pyrophosphatase graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": HISTORY_ACTION,
    "llm_assisted": True,
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

NUDC_PARENT_EVIDENCE = {
    "reference": "ARO:3004892",
    "snippet": (
        "nudC is a NADH pyrophosphatase that is involved in nicotinate and "
        "nicotinamide metabolism. Mutations that occur on the nudC gene "
        "resulting in the inability for ethionamide to function."
    ),
    "notes": "CARD definition for the ethionamide-resistant nudC parent.",
}

NADH_PYROPHOSPHATASE_EVIDENCE = {
    "reference": "GO:0035529",
    "snippet": "Catalysis of the reaction: NADH + H2O = AMP + NMNH + 2 H+.",
    "notes": "GO definition for NADH pyrophosphatase activity.",
}

NICOTINAMIDE_NUCLEOTIDE_EVIDENCE = {
    "reference": "GO:0046496",
    "snippet": (
        "The chemical reactions and pathways involving nicotinamide nucleotides, "
        "any nucleotide that contains combined nicotinamide."
    ),
    "notes": "GO definition for nicotinamide nucleotide metabolic process.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "mutation conferring antibiotic resistance",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3000212",
}

DRUG_NODE = {
    "node_id": "drug0",
    "label": "thioamide antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:3007156",
}

NADH_PYROPHOSPHATASE_NODE = {
    "node_id": "nadh_pyrophosphatase",
    "label": "NADH pyrophosphatase activity",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "GO:0035529",
}

NICOTINAMIDE_NUCLEOTIDE_NODE = {
    "node_id": "nicotinamide_nucleotide_metabolism",
    "label": "nicotinamide nucleotide metabolic process",
    "node_type": "BIOLOGICAL_PROCESS",
    "grounding": "GO:0046496",
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

DRUG_RELATION_REFERENCE = "ARO:3004892"
DRUG_RELATION_OBJECT = "ARO:3007156"
DRUG_RELATION_LABEL = "thioamide antibiotic"


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    graph_description: str


TARGETS = {
    "ARO:3004892": Target(
        identifier="ARO:3004892",
        filename="ethionamide-resistant-nudc-aro3004892.yaml",
        graph_description=(
            "Conservative graph for the ethionamide-resistant nudC parent. "
            "The graph grounds nudC's NADH pyrophosphatase activity and "
            "nicotinamide-nucleotide metabolism side path while leaving the "
            "resistance effect at ARO's mutation claim."
        ),
    ),
    "ARO:3004935": Target(
        identifier="ARO:3004935",
        filename="mycobacterium-tuberculosis-nudc-mutations-conferring-resistance-to-ethionamide-aro3004935.yaml",
        graph_description=(
            "Conservative graph for Mycobacterium tuberculosis nudC mutations "
            "conferring ethionamide resistance. The graph grounds nudC's NADH "
            "pyrophosphatase activity and nicotinamide-nucleotide metabolism "
            "side path, and keeps the inherited thioamide drug-class edge."
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


def _target_evidence(record: dict[str, Any]) -> dict[str, str]:
    return {
        "reference": str(record["identifier"]),
        "snippet": str(record["definition"]),
        "notes": f"CARD definition for {record['label']}.",
    }


def _parent_evidence(record: dict[str, Any]) -> tuple[dict[str, str], ...]:
    if record["identifier"] == NUDC_PARENT_EVIDENCE["reference"]:
        return ()
    return (NUDC_PARENT_EVIDENCE,)


def _drug_evidence() -> dict[str, str]:
    return {
        "reference": DRUG_RELATION_REFERENCE,
        "snippet": f"confers_resistance_to_drug_class {DRUG_RELATION_OBJECT} ! {DRUG_RELATION_LABEL}",
        "notes": (
            "ARO drug-class relationship on ARO:3004892; modeled here as a "
            "determinant-to-thioamide-antibiotic edge."
        ),
    }


def _unique_evidence(evidence: tuple[dict[str, str], ...]) -> list[dict[str, str]]:
    unique: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for item in evidence:
        key = (
            item["reference"],
            item["snippet"],
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


def _canonical_edge_keys() -> set[tuple[str, str, str]]:
    return {
        ("determinant", "RO:0000056", "mech0"),
        ("mech0", "RO:0002411", "resistance"),
        ("determinant", "RO:0002411", "resistance"),
        ("determinant", "ARO:2000001", "drug0"),
        ("determinant", "RO:0002327", "nadh_pyrophosphatase"),
        ("nadh_pyrophosphatase", "BFO:0000050", "nicotinamide_nucleotide_metabolism"),
    }


def _input_allowed_edges() -> set[tuple[str, str, str]]:
    allowed = _canonical_edge_keys()
    allowed.update(
        {
            ("determinant", "RO:0002327", "nadh_pp"),
            ("nadh_pp", "BFO:0000050", "nad_metabolism"),
        }
    )
    return allowed


def _validate_graph(graph: dict[str, Any], target: Target) -> None:
    nodes = _nodes_by_id(graph)
    missing_nodes = sorted({"determinant", "mech0", "drug0", "resistance"} - set(nodes))
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")

    found = set()
    seen: set[tuple[str, str, str]] = set()
    for edge in graph.get("edges") or []:
        key = _edge_key(edge)
        if key not in _input_allowed_edges():
            raise ValueError(f"{target.identifier}: unexpected edge {key[0]} -> {key[2]}")
        if key in seen:
            raise ValueError(f"{target.identifier}: duplicate edge {key[0]} -> {key[2]}")
        seen.add(key)
        found.add(key)

    required = {
        ("determinant", "RO:0000056", "mech0"),
        ("mech0", "RO:0002411", "resistance"),
        ("determinant", "RO:0002411", "resistance"),
        ("determinant", "ARO:2000001", "drug0"),
    }
    missing_edges = required - found

    activity_edges = {
        ("determinant", "RO:0002327", "nadh_pp"),
        ("determinant", "RO:0002327", "nadh_pyrophosphatase"),
    }
    if not found & activity_edges:
        missing_edges.add(("determinant", "RO:0002327", "nadh_pyrophosphatase"))

    metabolism_edges = {
        ("nadh_pp", "BFO:0000050", "nad_metabolism"),
        ("nadh_pyrophosphatase", "BFO:0000050", "nicotinamide_nucleotide_metabolism"),
    }
    if not found & metabolism_edges:
        missing_edges.add(
            ("nadh_pyrophosphatase", "BFO:0000050", "nicotinamide_nucleotide_metabolism")
        )

    if missing_edges:
        missing = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in sorted(missing_edges))
        raise ValueError(f"{target.identifier}: missing edge(s): {missing}")


def _canonical_nodes(graph: dict[str, Any]) -> list[dict[str, Any]]:
    nodes = _nodes_by_id(graph)
    return [
        copy.deepcopy(nodes["determinant"]),
        copy.deepcopy(MECHANISM_NODE),
        copy.deepcopy(DRUG_NODE),
        copy.deepcopy(NADH_PYROPHOSPHATASE_NODE),
        copy.deepcopy(NICOTINAMIDE_NUCLEOTIDE_NODE),
        copy.deepcopy(RESISTANCE_NODE),
    ]


def _canonical_edges(record: dict[str, Any]) -> list[dict[str, Any]]:
    target_evidence = _target_evidence(record)
    parent_evidence = _parent_evidence(record)
    resistance_evidence = (
        target_evidence,
        *parent_evidence,
        MUTATION_EVIDENCE,
    )
    activity_evidence = (
        target_evidence,
        *parent_evidence,
        NADH_PYROPHOSPHATASE_EVIDENCE,
    )

    return [
        _edge(
            "determinant",
            "participates in (resistance mechanism)",
            "RO:0000056",
            "mech0",
            "The ARO hierarchy classifies ethionamide-resistant nudC under point mutations.",
            (target_evidence, *parent_evidence, MUTATION_EVIDENCE),
        ),
        _edge(
            "mech0",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            "The inherited point-mutation mechanism links nudC determinants to ethionamide resistance.",
            resistance_evidence,
        ),
        _edge(
            "determinant",
            "causally upstream of (confers resistance)",
            "RO:0002411",
            "resistance",
            "The local ARO definition states that nudC mutations confer ethionamide resistance.",
            resistance_evidence,
        ),
        _edge(
            "determinant",
            "confers resistance to (drug class)",
            "ARO:2000001",
            "drug0",
            "The ARO hierarchy links ethionamide-resistant nudC to the thioamide antibiotic class.",
            (target_evidence, *parent_evidence, _drug_evidence(), MUTATION_EVIDENCE),
        ),
        _edge(
            "determinant",
            "enables",
            "RO:0002327",
            "nadh_pyrophosphatase",
            "ARO identifies nudC as an NADH pyrophosphatase.",
            activity_evidence,
        ),
        _edge(
            "nadh_pyrophosphatase",
            "part of (nicotinamide nucleotide metabolism)",
            "BFO:0000050",
            "nicotinamide_nucleotide_metabolism",
            (
                "NADH pyrophosphatase activity lies in the GO nicotinamide "
                "nucleotide metabolic-process branch."
            ),
            activity_evidence + (NICOTINAMIDE_NUCLEOTIDE_EVIDENCE,),
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
    graph["title"] = f"{record['label']} → NADH pyrophosphatase → resistance"
    graph["description"] = target.graph_description
    graph["nodes"] = _canonical_nodes(graph)
    graph["edges"] = _canonical_edges(out)
    return out, out.get("causal_graphs") != before


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: record is not a mapping")
    identifier = record.get("identifier")
    target = TARGETS.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not a nudC target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
    normalize_aliases = "&id" in text or "*id" in text
    if not changed and not normalize_aliases:
        return text, False

    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    if HISTORY_ACTION not in out:
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
