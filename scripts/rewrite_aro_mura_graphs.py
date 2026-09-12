#!/usr/bin/env python3
"""Ground MurA fosfomycin-resistance graphs.

The ARO MurA branch has a parent plus five bacterial children whose current
graphs leave MurA transferase activity and peptidoglycan biosynthesis
ungrounded. The same graphs also assert target overexpression on every child,
even though ARO only says that for the antibiotic-resistant parent,
Escherichia coli, and Staphylococcus aureus records.

This updater rewrites the exact six-record branch, grounds the MurA activity
and peptidoglycan-biosynthesis nodes, keeps the phosphonic-acid drug-class
edge, and removes unsupported overexpression from the Borreliella,
Mycobacterium, and Chlamydia children.

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
HISTORY_ACTION = "Grounded MurA fosfomycin-resistance graphs"
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

MURA_PARENT_EVIDENCE = {
    "reference": "ARO:3002811",
    "snippet": (
        "murA or UDP-N-acetylglucosamine enolpyruvyl transferase catalyses the "
        "initial step in peptidoglycan biosynthesis and is inhibited by "
        "fosfomycin. Overexpression of murA through mutations confers fosfomycin "
        "resistance."
    ),
    "notes": "CARD definition for the antibiotic-resistant murA transferase parent.",
}

MURA_ACTIVITY_EVIDENCE = {
    "reference": "GO:0008760",
    "snippet": (
        "Catalysis of the reaction: phosphoenolpyruvate + "
        "UDP-N-acetyl-alpha-D-glucosamine = phosphate + "
        "UDP-N-acetyl-3-O-(1-carboxyvinyl)-D-glucosamine."
    ),
    "notes": (
        "GO definition for UDP-N-acetylglucosamine "
        "1-carboxyvinyltransferase activity."
    ),
}

MURA_REACTION_EVIDENCE = {
    "reference": "RHEA:18681",
    "snippet": (
        "phosphoenolpyruvate + UDP-N-acetyl-alpha-D-glucosamine = "
        "UDP-N-acetyl-3-O-(1-carboxyvinyl)-alpha-D-glucosamine + phosphate"
    ),
    "notes": (
        "Rhea reaction cross-referenced from GO:0008760 for MurA "
        "1-carboxyvinyltransferase activity."
    ),
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
    "notes": (
        "GO definition for peptidoglycan biosynthetic process; the same GO record "
        "lists peptidoglycan biosynthesis as an exact synonym."
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
    "label": "phosphonic acid antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:3007149",
}

MURA_ACTIVITY_NODE = {
    "node_id": "enolpyruvyl_transfer",
    "label": "UDP-N-acetylglucosamine 1-carboxyvinyltransferase activity",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "GO:0008760",
}

PEPTIDOGLYCAN_BIOSYNTHESIS_NODE = {
    "node_id": "pg_synthesis",
    "label": "peptidoglycan biosynthetic process",
    "node_type": "BIOLOGICAL_PROCESS",
    "grounding": "GO:0009252",
}

OVEREXPRESSION_NODE = {
    "node_id": "overexpression",
    "label": "elevated murA levels",
    "node_type": "STATE",
    "description": (
        "ARO-supported state for records whose definitions explicitly attribute "
        "fosfomycin resistance to overexpression of murA through mutations."
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

DRUG_RELATION_REFERENCE = "ARO:3002811"
DRUG_RELATION_OBJECT = "ARO:3007149"
DRUG_RELATION_LABEL = "phosphonic acid antibiotic"

LEGACY_OVEREXPRESSION_EDGE_KEYS = {
    ("determinant", "RO:0000086", "overexpression"),
    ("overexpression", "RO:0002411", "pg_synthesis"),
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    graph_description: str
    has_overexpression: bool = False


TARGETS = {
    "ARO:3002811": Target(
        identifier="ARO:3002811",
        filename="antibiotic-resistant-mura-transferase-aro3002811.yaml",
        graph_description=(
            "Conservative graph for antibiotic-resistant MurA transferases. The "
            "graph grounds MurA 1-carboxyvinyltransferase activity and "
            "peptidoglycan biosynthesis, keeps the phosphonic-acid drug-class "
            "edge, and keeps the overexpression branch that ARO explicitly names "
            "for this parent."
        ),
        has_overexpression=True,
    ),
    "ARO:3003775": Target(
        identifier="ARO:3003775",
        filename=(
            "escherichia-coli-mura-with-mutation-conferring-resistance-to-"
            "fosfomycin-aro3003775.yaml"
        ),
        graph_description=(
            "Conservative graph for Escherichia coli MurA mutations. The graph "
            "grounds MurA 1-carboxyvinyltransferase activity and peptidoglycan "
            "biosynthesis, keeps the inherited phosphonic-acid drug-class edge, "
            "and keeps overexpression because this ARO definition explicitly "
            "mentions it."
        ),
        has_overexpression=True,
    ),
    "ARO:3003776": Target(
        identifier="ARO:3003776",
        filename=(
            "staphylococcus-aureus-mura-with-mutation-conferring-resistance-to-"
            "fosfomycin-aro3003776.yaml"
        ),
        graph_description=(
            "Conservative graph for Staphylococcus aureus MurA mutations. The "
            "graph grounds MurA 1-carboxyvinyltransferase activity and "
            "peptidoglycan biosynthesis, keeps the inherited phosphonic-acid "
            "drug-class edge, and keeps overexpression because this ARO "
            "definition explicitly mentions it."
        ),
        has_overexpression=True,
    ),
    "ARO:3003777": Target(
        identifier="ARO:3003777",
        filename=(
            "borreliella-burgdorferi-mura-with-mutation-conferring-resistance-to-"
            "fosfomycin-aro3003777.yaml"
        ),
        graph_description=(
            "Conservative graph for Borreliella burgdorferi MurA mutations. The "
            "graph grounds MurA 1-carboxyvinyltransferase activity and "
            "peptidoglycan biosynthesis, keeps the inherited phosphonic-acid "
            "drug-class edge, and drops the unsupported inherited "
            "overexpression branch."
        ),
    ),
    "ARO:3003784": Target(
        identifier="ARO:3003784",
        filename=(
            "mycobacterium-tuberculosis-intrinsic-mura-conferring-resistance-to-"
            "fosfomycin-aro3003784.yaml"
        ),
        graph_description=(
            "Conservative graph for Mycobacterium tuberculosis intrinsic MurA "
            "resistance. The graph grounds MurA 1-carboxyvinyltransferase "
            "activity and peptidoglycan biosynthesis, keeps the inherited "
            "phosphonic-acid drug-class edge, and drops the unsupported inherited "
            "overexpression branch."
        ),
    ),
    "ARO:3003785": Target(
        identifier="ARO:3003785",
        filename=(
            "chlamydia-trachomatis-intrinsic-mura-conferring-resistance-to-"
            "fosfomycin-aro3003785.yaml"
        ),
        graph_description=(
            "Conservative graph for Chlamydia trachomatis intrinsic MurA "
            "resistance. The graph grounds MurA 1-carboxyvinyltransferase "
            "activity and peptidoglycan biosynthesis, keeps the inherited "
            "phosphonic-acid drug-class edge, and drops the unsupported inherited "
            "overexpression branch."
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


def _mura_evidence(record: dict[str, Any]) -> tuple[dict[str, str], ...]:
    if record["identifier"] == MURA_PARENT_EVIDENCE["reference"]:
        return (_target_evidence(record),)
    return (_target_evidence(record), MURA_PARENT_EVIDENCE)


def _mutation_evidence(record: dict[str, Any]) -> tuple[dict[str, str], ...]:
    return _mura_evidence(record) + (MUTATION_EVIDENCE,)


def _drug_evidence() -> dict[str, str]:
    return {
        "reference": DRUG_RELATION_REFERENCE,
        "snippet": f"confers_resistance_to_drug_class {DRUG_RELATION_OBJECT} ! {DRUG_RELATION_LABEL}",
        "notes": (
            "ARO drug-class relationship on ARO:3002811; modeled here as a "
            "determinant-to-phosphonic-acid-antibiotic edge and inherited by "
            "the species-specific MurA children."
        ),
    }


def _drug_edge_evidence(record: dict[str, Any]) -> tuple[dict[str, str], ...]:
    return _mura_evidence(record) + (_drug_evidence(), MUTATION_EVIDENCE)


def _activity_evidence(record: dict[str, Any]) -> tuple[dict[str, str], ...]:
    return _mura_evidence(record) + (MURA_ACTIVITY_EVIDENCE, MURA_REACTION_EVIDENCE)


def _biosynthesis_evidence(record: dict[str, Any]) -> tuple[dict[str, str], ...]:
    return _mura_evidence(record) + (
        MURA_ACTIVITY_EVIDENCE,
        MURA_REACTION_EVIDENCE,
        PEPTIDOGLYCAN_BIOSYNTHESIS_EVIDENCE,
    )


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


def _canonical_edge_keys(target: Target) -> set[tuple[str, str, str]]:
    keys = {
        ("determinant", "RO:0000056", "mech0"),
        ("mech0", "RO:0002411", "resistance"),
        ("determinant", "RO:0002411", "resistance"),
        ("determinant", "ARO:2000001", "drug0"),
        ("determinant", "RO:0002327", "enolpyruvyl_transfer"),
        ("enolpyruvyl_transfer", "BFO:0000050", "pg_synthesis"),
        ("drug0", "RO:0002212", "enolpyruvyl_transfer"),
    }
    if target.has_overexpression:
        keys.update(LEGACY_OVEREXPRESSION_EDGE_KEYS)
    return keys


def _input_allowed_edges(target: Target) -> set[tuple[str, str, str]]:
    return _canonical_edge_keys(target) | LEGACY_OVEREXPRESSION_EDGE_KEYS


def _validate_graph(graph: dict[str, Any], target: Target) -> None:
    nodes = _nodes_by_id(graph)
    required_nodes = {
        "determinant",
        "mech0",
        "drug0",
        "enolpyruvyl_transfer",
        "pg_synthesis",
        "resistance",
    }
    if target.has_overexpression:
        required_nodes.add("overexpression")

    missing_nodes = sorted(required_nodes - set(nodes))
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")

    found = set()
    seen: set[tuple[str, str, str]] = set()
    for edge in graph.get("edges") or []:
        key = _edge_key(edge)
        if key not in _input_allowed_edges(target):
            raise ValueError(f"{target.identifier}: unexpected edge {key[0]} -> {key[2]}")
        if key in seen:
            raise ValueError(f"{target.identifier}: duplicate edge {key[0]} -> {key[2]}")
        seen.add(key)
        found.add(key)

    missing_edges = sorted(_canonical_edge_keys(target) - found)
    if missing_edges:
        missing = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in missing_edges)
        raise ValueError(f"{target.identifier}: missing edge(s): {missing}")


def _canonical_nodes(graph: dict[str, Any], target: Target) -> list[dict[str, Any]]:
    nodes = _nodes_by_id(graph)
    ordered = [
        copy.deepcopy(nodes["determinant"]),
        copy.deepcopy(MECHANISM_NODE),
        copy.deepcopy(DRUG_NODE),
        copy.deepcopy(MURA_ACTIVITY_NODE),
        copy.deepcopy(PEPTIDOGLYCAN_BIOSYNTHESIS_NODE),
    ]
    if target.has_overexpression:
        ordered.append(copy.deepcopy(OVEREXPRESSION_NODE))
    ordered.append(copy.deepcopy(RESISTANCE_NODE))
    return ordered


def _canonical_edges(record: dict[str, Any], target: Target) -> list[dict[str, Any]]:
    activity_evidence = _activity_evidence(record)
    biosynthesis_evidence = _biosynthesis_evidence(record)

    edges = [
        _edge(
            "determinant",
            "participates in (resistance mechanism)",
            "RO:0000056",
            "mech0",
            "The ARO hierarchy classifies resistant MurA variants under point mutations.",
            _mutation_evidence(record),
        ),
        _edge(
            "mech0",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            "The inherited point-mutation mechanism links MurA determinants to resistance.",
            _mutation_evidence(record),
        ),
        _edge(
            "determinant",
            "causally upstream of (confers resistance)",
            "RO:0002411",
            "resistance",
            "The ARO hierarchy links MurA variants to fosfomycin resistance.",
            _drug_edge_evidence(record),
        ),
        _edge(
            "determinant",
            "confers resistance to (drug class)",
            "ARO:2000001",
            "drug0",
            "The ARO hierarchy links this MurA determinant to phosphonic acid antibiotics.",
            _drug_edge_evidence(record),
        ),
        _edge(
            "determinant",
            "enables",
            "RO:0002327",
            "enolpyruvyl_transfer",
            "ARO identifies MurA as a UDP-N-acetylglucosamine enolpyruvyl transferase.",
            activity_evidence,
        ),
        _edge(
            "enolpyruvyl_transfer",
            "part of (peptidoglycan biosynthesis)",
            "BFO:0000050",
            "pg_synthesis",
            "ARO places the MurA transferase reaction at the initial step of peptidoglycan biosynthesis.",
            biosynthesis_evidence,
        ),
        _edge(
            "drug0",
            "negatively regulates (inhibits MurA activity)",
            "RO:0002212",
            "enolpyruvyl_transfer",
            "ARO states that fosfomycin inhibits the MurA transferase activity.",
            activity_evidence,
        ),
    ]

    if target.has_overexpression:
        overexpression_evidence = _mutation_evidence(record)
        edges.extend(
            [
                _edge(
                    "determinant",
                    "has quality (elevated expression)",
                    "RO:0000086",
                    "overexpression",
                    "ARO attributes fosfomycin resistance in this record to overexpression of murA through mutations.",
                    overexpression_evidence,
                ),
                _edge(
                    "overexpression",
                    "causally upstream of (wall synthesis continues under drug)",
                    "RO:0002411",
                    "pg_synthesis",
                    "ARO links elevated murA levels to fosfomycin resistance for this record.",
                    overexpression_evidence + (
                        MURA_ACTIVITY_EVIDENCE,
                        PEPTIDOGLYCAN_BIOSYNTHESIS_EVIDENCE,
                    ),
                ),
            ]
        )

    return edges


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != target.identifier:
        raise ValueError(f"expected {target.identifier}, found {record.get('identifier')}")

    out = copy.deepcopy(record)
    before = copy.deepcopy(out.get("causal_graphs"))
    graphs = out.get("causal_graphs") or []
    graph = next(
        (item for item in graphs if item.get("graph_id") in {"resistance", "resistance-draft"}),
        None,
    )
    if graph is None:
        raise ValueError(f"{target.identifier}: missing resistance causal graph")

    _validate_graph(graph, target)
    graph["graph_id"] = "resistance"
    graph["title"] = f"{record['label']} → MurA mutation → fosfomycin resistance"
    graph["description"] = target.graph_description
    graph["nodes"] = _canonical_nodes(graph, target)
    graph["edges"] = _canonical_edges(out, target)
    return out, out.get("causal_graphs") != before


def _promote_to_reviewed(text: str) -> str:
    return re.sub(r"^mapping_status:\s*SEEDED\s*$", "mapping_status: REVIEWED", text, count=1, flags=re.M)


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: record is not a mapping")
    identifier = record.get("identifier")
    target = TARGETS.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not a MurA target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
    normalize_aliases = "&id" in text or "*id" in text
    if not changed and not normalize_aliases and record.get("mapping_status") == "REVIEWED":
        return text, False

    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    out = _promote_to_reviewed(out)
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
        help="ARO directory or one of the six target YAML files",
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
