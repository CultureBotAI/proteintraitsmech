#!/usr/bin/env python3
"""Ground mshB mycothiol-biosynthesis resistance graphs.

The ARO mshB branch has a broad mutation-resistance parent and an isoniazid
child that names the GlcNAc-Ins deacetylase reaction in mycothiol synthesis.
This updater promotes the exact two-record branch and adds the reaction side
path only to the child whose ARO definition supports it.

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
HISTORY_ACTION = "Grounded mshB mycothiol-biosynthesis resistance graphs"
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

MSHB_PARENT_EVIDENCE = {
    "reference": "ARO:3004902",
    "snippet": "Mutations that occur in the mshB gene that results in antibiotic resistance.",
    "notes": "CARD definition for the antibiotic-resistant mshB parent.",
}

MSHB_DEACETYLASE_EVIDENCE = {
    "reference": "GO:0035595",
    "snippet": (
        "Catalysis of the reaction: "
        "1D-myo-inositol 2-acetamido-2-deoxy-alpha-D-glucopyranoside + H2O = "
        "1D-myo-inositol 2-amino-2-deoxy-alpha-D-glucopyranoside + acetate."
    ),
    "notes": "GO definition for N-acetylglucosaminylinositol deacetylase activity.",
}

GLCN_INS_EVIDENCE = {
    "reference": "RHEA:26181",
    "snippet": (
        "1D-myo-inositol 2-acetamido-2-deoxy-alpha-D-glucopyranoside + H2O => "
        "1D-myo-inositol 2-amino-2-deoxy-alpha-D-glucopyranoside + acetate"
    ),
    "notes": (
        "Rhea's left-to-right directional child of RHEA:26180 declares "
        "1D-myo-inositol 2-amino-2-deoxy-alpha-D-glucopyranoside as a product "
        "grounded to CHEBI:58886."
    ),
}

MYCOTHIOL_BIOSYNTHESIS_EVIDENCE = {
    "reference": "GO:0010125",
    "snippet": (
        "The chemical reactions and pathways resulting in the formation of "
        "mycothiol, which consists of N-acetyl-L-cysteine linked to a "
        "pseudodisaccharide, D-glucosamine and myo-inositol."
    ),
    "notes": "GO definition for mycothiol biosynthetic process.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "mutation conferring antibiotic resistance",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3000212",
}

DRUG_NODE = {
    "node_id": "drug0",
    "label": "isoniazid-like antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:3007152",
}

MSHB_DEACETYLASE_NODE = {
    "node_id": "mshb_deacetylase",
    "label": "N-acetylglucosaminylinositol deacetylase activity",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "GO:0035595",
}

GLCN_INS_NODE = {
    "node_id": "glcn_ins",
    "label": "GlcN-Ins",
    "node_type": "CHEMICAL",
    "grounding": "CHEBI:58886",
}

MYCOTHIOL_BIOSYNTHESIS_NODE = {
    "node_id": "mycothiol_biosynthesis",
    "label": "mycothiol biosynthetic process",
    "node_type": "BIOLOGICAL_PROCESS",
    "grounding": "GO:0010125",
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

DRUG_RELATION_REFERENCE = "ARO:3004903"
DRUG_RELATION_OBJECT = "ARO:3007152"
DRUG_RELATION_LABEL = "isoniazid-like antibiotic"


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    graph_description: str
    has_drug: bool = False
    has_reaction: bool = False


TARGETS = {
    "ARO:3004902": Target(
        identifier="ARO:3004902",
        filename="antibiotic-resistant-mshb-aro3004902.yaml",
        graph_description=(
            "Conservative graph for the antibiotic-resistant mshB parent. "
            "The graph keeps only the broad mshB mutation-resistance claim "
            "because this ARO record does not identify a drug class or name "
            "MshB's mycothiol-biosynthesis reaction."
        ),
    ),
    "ARO:3004903": Target(
        identifier="ARO:3004903",
        filename="isoniazid-resistant-mshb-aro3004903.yaml",
        graph_description=(
            "Conservative graph for isoniazid-resistant mshB. The graph "
            "grounds the MshB deacetylase reaction and GlcN-Ins product named "
            "by ARO, keeps the isoniazid-like drug-class edge, and does not "
            "add an unsupported isoniazid activation edge."
        ),
        has_drug=True,
        has_reaction=True,
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


def _mutation_evidence(record: dict[str, Any]) -> tuple[dict[str, str], ...]:
    if record["identifier"] == MSHB_PARENT_EVIDENCE["reference"]:
        return (_target_evidence(record), MUTATION_EVIDENCE)
    return (_target_evidence(record), MSHB_PARENT_EVIDENCE, MUTATION_EVIDENCE)


def _drug_evidence() -> dict[str, str]:
    return {
        "reference": DRUG_RELATION_REFERENCE,
        "snippet": f"confers_resistance_to_drug_class {DRUG_RELATION_OBJECT} ! {DRUG_RELATION_LABEL}",
        "notes": (
            "ARO drug-class relationship on ARO:3004903; modeled here as a "
            "determinant-to-isoniazid-like-antibiotic edge."
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


def _canonical_edge_keys(target: Target) -> set[tuple[str, str, str]]:
    expected = {
        ("determinant", "RO:0000056", "mech0"),
        ("mech0", "RO:0002411", "resistance"),
        ("determinant", "RO:0002411", "resistance"),
    }
    if target.has_drug:
        expected.add(("determinant", "ARO:2000001", "drug0"))
    if target.has_reaction:
        expected.update(
            {
                ("determinant", "RO:0002327", "mshb_deacetylase"),
                ("mshb_deacetylase", "RO:0002234", "glcn_ins"),
                ("mshb_deacetylase", "BFO:0000050", "mycothiol_biosynthesis"),
            }
        )
    return expected


def _input_allowed_edges(target: Target) -> set[tuple[str, str, str]]:
    allowed = _canonical_edge_keys(target)
    if target.has_reaction:
        allowed.update(
            {
                ("determinant", "RO:0002327", "deacetylation"),
                ("deacetylation", "BFO:0000050", "mycothiol"),
            }
        )
    return allowed


def _validate_graph(graph: dict[str, Any], target: Target) -> None:
    nodes = _nodes_by_id(graph)
    required_nodes = {"determinant", "mech0", "resistance"}
    if target.has_drug:
        required_nodes.add("drug0")
    if "drug0" in nodes and not target.has_drug:
        raise ValueError(f"{target.identifier}: unexpected drug0 node")

    missing_nodes = sorted(required_nodes - set(nodes))
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")

    required_edges = {
        ("determinant", "RO:0000056", "mech0"),
        ("mech0", "RO:0002411", "resistance"),
        ("determinant", "RO:0002411", "resistance"),
    }
    if target.has_drug:
        required_edges.add(("determinant", "ARO:2000001", "drug0"))

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

    missing_edges = sorted(required_edges - found)
    if missing_edges:
        missing = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in missing_edges)
        raise ValueError(f"{target.identifier}: missing edge(s): {missing}")


def _canonical_nodes(graph: dict[str, Any], target: Target) -> list[dict[str, Any]]:
    nodes = _nodes_by_id(graph)
    ordered = [
        copy.deepcopy(nodes["determinant"]),
        copy.deepcopy(MECHANISM_NODE),
    ]
    if target.has_drug:
        ordered.append(copy.deepcopy(DRUG_NODE))
    if target.has_reaction:
        ordered.extend(
            [
                copy.deepcopy(MSHB_DEACETYLASE_NODE),
                copy.deepcopy(GLCN_INS_NODE),
                copy.deepcopy(MYCOTHIOL_BIOSYNTHESIS_NODE),
            ]
        )
    ordered.append(copy.deepcopy(RESISTANCE_NODE))
    return ordered


def _canonical_edges(record: dict[str, Any], target: Target) -> list[dict[str, Any]]:
    target_evidence = _target_evidence(record)
    mutation_evidence = _mutation_evidence(record)
    reaction_evidence = (target_evidence, MSHB_DEACETYLASE_EVIDENCE)

    edges = [
        _edge(
            "determinant",
            "participates in (resistance mechanism)",
            "RO:0000056",
            "mech0",
            "The ARO hierarchy classifies resistant mshB variants under point mutations.",
            mutation_evidence,
        ),
        _edge(
            "mech0",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            "The inherited point-mutation mechanism links mshB determinants to resistance.",
            mutation_evidence,
        ),
        _edge(
            "determinant",
            "causally upstream of (confers resistance)",
            "RO:0002411",
            "resistance",
            "The ARO hierarchy links mshB mutation records to antibiotic resistance.",
            mutation_evidence,
        ),
    ]

    if target.has_drug:
        edges.append(
            _edge(
                "determinant",
                "confers resistance to (drug class)",
                "ARO:2000001",
                "drug0",
                "The ARO hierarchy links this mshB determinant to isoniazid-like antibiotics.",
                (target_evidence, MSHB_PARENT_EVIDENCE, _drug_evidence(), MUTATION_EVIDENCE),
            )
        )

    if target.has_reaction:
        edges.extend(
            [
                _edge(
                    "determinant",
                    "enables",
                    "RO:0002327",
                    "mshb_deacetylase",
                    "ARO identifies MshB as the deacetylase that converts GlcNAc-Ins to GlcN-Ins.",
                    reaction_evidence,
                ),
                _edge(
                    "mshb_deacetylase",
                    "has output (GlcN-Ins)",
                    "RO:0002234",
                    "glcn_ins",
                    "MshB deacetylase activity forms GlcN-Ins.",
                    reaction_evidence + (GLCN_INS_EVIDENCE,),
                ),
                _edge(
                    "mshb_deacetylase",
                    "part of (mycothiol biosynthesis)",
                    "BFO:0000050",
                    "mycothiol_biosynthesis",
                    "ARO places the MshB deacetylase reaction in mycothiol biosynthesis.",
                    reaction_evidence + (MYCOTHIOL_BIOSYNTHESIS_EVIDENCE,),
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
    graph["title"] = f"{record['label']} → mshB mutation → resistance"
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
        raise ValueError(f"{path}: not an mshB target: {identifier}")
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
