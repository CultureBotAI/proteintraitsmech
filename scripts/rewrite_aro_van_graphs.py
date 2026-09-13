#!/usr/bin/env python3
"""Ground VanJ and VanK glycopeptide-resistance graphs.

The ARO VanJ/VanK neighborhood contains the two remaining 71-point records:
vanJ and vanK. This updater rewrites the exact four-record neighborhood around
them: the vanJ membrane-protein parent, the vanJ child, the vanK parent, and the
vanKI child. VanJ keeps its undecaprenyl-diphosphatase side path. VanK is
collapsed from an ungrounded cross-bridge transfer/substrate pair to grounded
participation in peptidoglycan biosynthesis because no precise local GO/Rhea
term exists for the Fem-family amino-acid cross-bridge addition reaction.

Dry-run by default; pass ``--apply`` to write.
"""

from __future__ import annotations

import argparse
import copy
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from record_io import append_to_section, replace_block  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ARO_DIR = ROOT / "data" / "traits" / "function" / "resistance" / "aro"

HISTORY_CURATOR = "codex-causal-graph-quality"
HISTORY_ACTION = "Grounded VanJ and VanK glycopeptide-resistance graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

RESTRUCTURING_EVIDENCE = {
    "reference": "ARO:3000213",
    "snippet": (
        "Peptidoglycan precursors ending in D-Ala-D-Lac or D-Ala-D-Ser instead "
        "of D-Ala-D-Ala conferring high level glycopeptide resistance."
    ),
    "notes": "CARD definition for the inherited cell-wall-restructuring resistance mechanism.",
}

VANJ_PARENT_EVIDENCE = {
    "reference": "ARO:3004255",
    "snippet": "vanJ and vanJ homologue proteins confer resistance to teicoplanin.",
    "notes": "CARD definition for the vanJ membrane-protein parent.",
}

VANK_PARENT_EVIDENCE = {
    "reference": "ARO:3002915",
    "snippet": (
        "VanK is a member of the Fem family of enzymes that add the cross-bridge "
        "amino acids to the stem pentapeptide of cell wall precursors in "
        "Streptomyces coelicolor that confers inducible, high-level vancomycin "
        "resistance."
    ),
    "notes": "CARD definition for vanK.",
}

UNDECAPRENYL_DIPHOSPHATASE_EVIDENCE = {
    "reference": "GO:0050380",
    "snippet": (
        "Catalysis of the reaction: di-trans,octa-cis-undecaprenyl diphosphate + "
        "H2O = di-trans,octa-cis-undecaprenyl phosphate + H+ + phosphate."
    ),
    "notes": (
        "GO definition for undecaprenyl-diphosphatase activity, the hydrolysis "
        "activity used to recycle undecaprenyl diphosphate."
    ),
}

PEPTIDOGLYCAN_WALL_EVIDENCE = {
    "reference": "GO:0009273",
    "snippet": (
        "The chemical reactions and pathways resulting in the formation of the "
        "peptidoglycan-based cell wall."
    ),
    "notes": "GO definition for peptidoglycan-based cell wall biogenesis.",
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

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "restructuring of bacterial cell wall conferring antibiotic resistance",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3000213",
}

DRUG_NODE = {
    "node_id": "drug0",
    "label": "glycopeptide antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:3000081",
}

UPP_RECYCLING_NODE = {
    "node_id": "upp_recycling",
    "label": "undecaprenyl-diphosphatase activity",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "GO:0050380",
}

PEPTIDOGLYCAN_WALL_NODE = {
    "node_id": "wall",
    "label": "peptidoglycan-based cell wall biogenesis",
    "node_type": "BIOLOGICAL_PROCESS",
    "grounding": "GO:0009273",
}

PEPTIDOGLYCAN_BIOSYNTHESIS_NODE = {
    "node_id": "peptidoglycan_biosynthesis",
    "label": "peptidoglycan biosynthetic process",
    "node_type": "BIOLOGICAL_PROCESS",
    "grounding": "GO:0009252",
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

DRUG_RELATION_OBJECT = "ARO:3000081"
DRUG_RELATION_LABEL = "glycopeptide antibiotic"


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    graph_title: str
    graph_description: str
    family: Literal["vanj", "vank"]
    side_path: Literal["vanj_recycling", "vank_peptidoglycan", "none"] = "none"


TARGETS = {
    "ARO:3004255": Target(
        identifier="ARO:3004255",
        filename="vanj-membrane-protein-aro3004255.yaml",
        graph_title="vanJ membrane protein → cell-wall restructuring → resistance",
        graph_description=(
            "Conservative graph for the vanJ membrane-protein parent. The graph "
            "keeps the homologue group's glycopeptide resistance claim and "
            "inherited cell-wall-restructuring mechanism but omits the "
            "undecaprenyl-diphosphatase path, which only the child vanJ record names."
        ),
        family="vanj",
    ),
    "ARO:3002914": Target(
        identifier="ARO:3002914",
        filename="vanj-aro3002914.yaml",
        graph_title="vanJ → undecaprenyl diphosphate recycling → resistance",
        graph_description=(
            "Conservative graph for vanJ glycopeptide resistance. The graph "
            "grounds undecaprenyl-diphosphatase activity and peptidoglycan-based "
            "cell-wall biogenesis from the ARO statement that vanJ recycles "
            "undecaprenol pyrophosphate during cell-wall biosynthesis."
        ),
        family="vanj",
        side_path="vanj_recycling",
    ),
    "ARO:3002915": Target(
        identifier="ARO:3002915",
        filename="vank-aro3002915.yaml",
        graph_title="vanK → peptidoglycan bridge formation → resistance",
        graph_description=(
            "Conservative graph for vanK glycopeptide resistance. The graph "
            "retains the Fem-family peptidoglycan-bridge role as grounded "
            "participation in peptidoglycan biosynthesis and drops the former "
            "ungrounded cross-bridge transfer and stem-pentapeptide nodes."
        ),
        family="vank",
        side_path="vank_peptidoglycan",
    ),
    "ARO:3003727": Target(
        identifier="ARO:3003727",
        filename="vank-gene-in-vani-cluster-aro3003727.yaml",
        graph_title="vanK gene in vanI cluster → peptidoglycan bridge formation → resistance",
        graph_description=(
            "Conservative graph for the vanKI child of vanK. The graph promotes "
            "the draft resistance route, keeps the inherited glycopeptide "
            "drug-class edge, and grounds its peptidoglycan-bridge role as "
            "participation in peptidoglycan biosynthesis."
        ),
        family="vank",
        side_path="vank_peptidoglycan",
    ),
}


PARENT_EVIDENCE = {
    "vanj": VANJ_PARENT_EVIDENCE,
    "vank": VANK_PARENT_EVIDENCE,
}

DRUG_RELATION_REFERENCE = {
    "vanj": "ARO:3004255",
    "vank": "ARO:3002915",
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


def _family_evidence(record: dict[str, Any], target: Target) -> tuple[dict[str, str], ...]:
    parent = PARENT_EVIDENCE[target.family]
    if record["identifier"] == parent["reference"]:
        return (_target_evidence(record), RESTRUCTURING_EVIDENCE)
    return (_target_evidence(record), parent, RESTRUCTURING_EVIDENCE)


def _drug_evidence(target: Target) -> dict[str, str]:
    return {
        "reference": DRUG_RELATION_REFERENCE[target.family],
        "snippet": f"confers_resistance_to_drug_class {DRUG_RELATION_OBJECT} ! {DRUG_RELATION_LABEL}",
        "notes": (
            f"ARO drug-class relationship on {DRUG_RELATION_REFERENCE[target.family]}; "
            "modeled here as a determinant-to-glycopeptide-antibiotic edge and "
            "inherited by its child records."
        ),
    }


def _drug_edge_evidence(record: dict[str, Any], target: Target) -> tuple[dict[str, str], ...]:
    parent = PARENT_EVIDENCE[target.family]
    drug = _drug_evidence(target)
    if record["identifier"] == parent["reference"]:
        return (_target_evidence(record), drug, RESTRUCTURING_EVIDENCE)
    return (_target_evidence(record), parent, drug, RESTRUCTURING_EVIDENCE)


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
        ("determinant", "ARO:2000001", "drug0"),
    }
    if target.side_path == "vanj_recycling":
        expected.update(
            {
                ("determinant", "RO:0002327", "upp_recycling"),
                ("upp_recycling", "BFO:0000050", "wall"),
            }
        )
    if target.side_path == "vank_peptidoglycan":
        expected.add(("determinant", "RO:0000056", "peptidoglycan_biosynthesis"))
    return expected


def _input_allowed_edges(target: Target) -> set[tuple[str, str, str]]:
    allowed = _canonical_edge_keys(target)
    if target.identifier == "ARO:3004255":
        allowed.add(("determinant", "RO:0002158", "vanj_record"))
    if target.identifier == "ARO:3002915":
        allowed.update(
            {
                ("determinant", "RO:0002327", "crossbridge_transfer"),
                ("crossbridge_transfer", "RO:0002233", "stem_pentapeptide"),
            }
        )
    return allowed


def _validate_graph(graph: dict[str, Any], target: Target) -> None:
    nodes = _nodes_by_id(graph)
    required_nodes = {"determinant", "mech0", "drug0", "resistance"}
    if target.side_path == "vanj_recycling":
        required_nodes.update({"upp_recycling", "wall"})

    missing_nodes = sorted(required_nodes - set(nodes))
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")

    required_edges = {
        ("determinant", "RO:0000056", "mech0"),
        ("mech0", "RO:0002411", "resistance"),
        ("determinant", "RO:0002411", "resistance"),
        ("determinant", "ARO:2000001", "drug0"),
    }
    if target.side_path == "vanj_recycling":
        required_edges.update(
            {
                ("determinant", "RO:0002327", "upp_recycling"),
                ("upp_recycling", "BFO:0000050", "wall"),
            }
        )

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
        copy.deepcopy(DRUG_NODE),
    ]
    if target.side_path == "vanj_recycling":
        ordered.extend(
            [
                copy.deepcopy(UPP_RECYCLING_NODE),
                copy.deepcopy(PEPTIDOGLYCAN_WALL_NODE),
            ]
        )
    if target.side_path == "vank_peptidoglycan":
        ordered.append(copy.deepcopy(PEPTIDOGLYCAN_BIOSYNTHESIS_NODE))
    ordered.append(copy.deepcopy(RESISTANCE_NODE))
    return ordered


def _canonical_edges(record: dict[str, Any], target: Target) -> list[dict[str, Any]]:
    target_evidence = _target_evidence(record)
    family_evidence = _family_evidence(record, target)
    drug_evidence = _drug_edge_evidence(record, target)

    edges = [
        _edge(
            "determinant",
            "participates in (resistance mechanism)",
            "RO:0000056",
            "mech0",
            "The ARO hierarchy classifies this determinant under cell-wall restructuring.",
            family_evidence,
        ),
        _edge(
            "mech0",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            "The inherited cell-wall-restructuring mechanism links Van determinants to resistance.",
            family_evidence,
        ),
        _edge(
            "determinant",
            "causally upstream of (confers resistance)",
            "RO:0002411",
            "resistance",
            "The ARO hierarchy links this Van determinant to glycopeptide resistance.",
            drug_evidence,
        ),
        _edge(
            "determinant",
            "confers resistance to (drug class)",
            "ARO:2000001",
            "drug0",
            "The ARO hierarchy links this Van determinant to glycopeptide antibiotics.",
            drug_evidence,
        ),
    ]

    if target.side_path == "vanj_recycling":
        edges.extend(
            [
                _edge(
                    "determinant",
                    "enables",
                    "RO:0002327",
                    "upp_recycling",
                    "ARO identifies vanJ as recycling undecaprenol pyrophosphate.",
                    (target_evidence, UNDECAPRENYL_DIPHOSPHATASE_EVIDENCE),
                ),
                _edge(
                    "upp_recycling",
                    "part of (peptidoglycan-based cell wall biogenesis)",
                    "BFO:0000050",
                    "wall",
                    "ARO places VanJ undecaprenyl-diphosphatase activity in cell-wall biosynthesis.",
                    (target_evidence, PEPTIDOGLYCAN_WALL_EVIDENCE),
                ),
            ]
        )
    if target.side_path == "vank_peptidoglycan":
        edges.append(
            _edge(
                "determinant",
                "participates in (peptidoglycan biosynthesis)",
                "RO:0000056",
                "peptidoglycan_biosynthesis",
                "ARO identifies VanK as forming peptidoglycan cross-bridges.",
                (target_evidence, PEPTIDOGLYCAN_BIOSYNTHESIS_EVIDENCE),
            )
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
    graph["title"] = target.graph_title
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
        raise ValueError(f"{path}: not a VanJ/VanK target: {identifier}")
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
        help="ARO directory or one of the four target YAML files",
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
