#!/usr/bin/env python3
"""Ground beta-1,3-D-glucan synthase resistance graphs.

The local ARO beta-glucan-synthase branch contains two draft parent graphs and a
reviewed Candida FKS2 child with label-only glucan-synthase and cell-wall nodes.
This updater curates the exact local chain from antifungal-resistant
beta-1,3-D-glucan synthase to the Candida FKS2 echinocandin-resistance record.

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
HISTORY_ACTION = "Grounded beta-1,3-D-glucan synthase resistance graphs"
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

ECHINOCANDIN_BRANCH_EVIDENCE = {
    "reference": "ARO:3007546",
    "snippet": (
        "Fungal beta-1,3-D-glucan synthases which include mutations to confer "
        "resistance to echinocandin-class antibiotics."
    ),
    "notes": "CARD definition for the echinocandin-resistant beta-glucan-synthase parent.",
}

GO_ACTIVITY_EVIDENCE = {
    "reference": "GO:0003843",
    "snippet": (
        "Catalysis of the reaction: UDP-glucose + "
        "[(1->3)-beta-D-glucosyl](n) = UDP + "
        "[(1->3)-beta-D-glucosyl](n+1)."
    ),
    "notes": "GO definition for 1,3-beta-D-glucan synthase activity.",
}

GO_BIOSYNTHESIS_EVIDENCE = {
    "reference": "GO:0006075",
    "snippet": (
        "The chemical reactions and pathways resulting in the formation of "
        "(1->3)-beta-D-glucans, compounds composed of glucose residues linked "
        "by (1->3)-beta-D-glucosidic bonds."
    ),
    "notes": "GO definition for (1->3)-beta-D-glucan biosynthetic process.",
}

GO_CELL_WALL_EVIDENCE = {
    "reference": "GO:0009272",
    "snippet": (
        "A cellular process that results in the biosynthesis of constituent "
        "macromolecules, assembly, and arrangement of constituent parts of a "
        "fungal-type cell wall. The fungal-type cell wall contains beta-glucan "
        "and may contain chitin."
    ),
    "notes": "GO definition for fungal-type cell wall biogenesis.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "mutation conferring antibiotic resistance",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3000212",
}

GLUCAN_SYNTHASE_NODE = {
    "node_id": "glucan_synthase_activity",
    "label": "1,3-beta-D-glucan synthase activity",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "GO:0003843",
}

BETA_GLUCAN_BIOSYNTHESIS_NODE = {
    "node_id": "beta_glucan_biosynthesis",
    "label": "(1->3)-beta-D-glucan biosynthetic process",
    "node_type": "BIOLOGICAL_PROCESS",
    "grounding": "GO:0006075",
}

FUNGAL_CELL_WALL_NODE = {
    "node_id": "fungal_cell_wall_biogenesis",
    "label": "fungal-type cell wall biogenesis",
    "node_type": "BIOLOGICAL_PROCESS",
    "grounding": "GO:0009272",
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


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    graph_description: str
    drug_relation_reference: str | None = None
    drug_relation_object: str | None = None
    drug_relation_label: str | None = None
    include_cell_wall: bool = False


TARGETS = {
    "ARO:3007545": Target(
        identifier="ARO:3007545",
        filename="antifungal-resistant-beta-1-3-d-glucan-synthase-aro3007545.yaml",
        graph_description=(
            "Conservative graph for the antifungal-resistant "
            "beta-1,3-D-glucan synthase parent. The graph grounds the named "
            "enzymatic activity and beta-glucan biosynthesis path, and keeps "
            "the resistance effect at ARO's broad mutation level."
        ),
    ),
    "ARO:3007546": Target(
        identifier="ARO:3007546",
        filename="echinocandin-antibiotic-resistant-beta-1-3-d-glucan-synthase-aro3007546.yaml",
        graph_description=(
            "Conservative graph for the echinocandin-resistant "
            "beta-1,3-D-glucan synthase parent. The graph grounds the named "
            "enzymatic activity and beta-glucan biosynthesis path, and keeps "
            "the echinocandin drug-class edge asserted by ARO."
        ),
        drug_relation_reference="ARO:3007546",
        drug_relation_object="ARO:3007496",
        drug_relation_label="echinocandin antibiotic",
    ),
    "ARO:3007548": Target(
        identifier="ARO:3007548",
        filename=(
            "candida-spp-fks2-with-mutations-conferring-resistance-to-"
            "echinocandin-antibiotic-aro3007548.yaml"
        ),
        graph_description=(
            "Conservative graph for Candida spp. FKS2 mutations conferring "
            "echinocandin resistance. The graph grounds FKS2's "
            "1,3-beta-D-glucan synthase activity, beta-glucan biosynthesis, "
            "and fungal cell-wall biogenesis, and keeps the inherited "
            "echinocandin drug-class edge asserted by ARO."
        ),
        drug_relation_reference="ARO:3007546",
        drug_relation_object="ARO:3007496",
        drug_relation_label="echinocandin antibiotic",
        include_cell_wall=True,
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


def _drug_evidence(target: Target) -> dict[str, str]:
    if (
        target.drug_relation_reference is None
        or target.drug_relation_object is None
        or target.drug_relation_label is None
    ):
        raise ValueError(f"{target.identifier}: no drug relation configured")

    return {
        "reference": target.drug_relation_reference,
        "snippet": (
            "confers_resistance_to_drug_class "
            f"{target.drug_relation_object} ! {target.drug_relation_label}"
        ),
        "notes": (
            f"ARO drug-class relationship on {target.drug_relation_reference}; "
            f"modeled here as a determinant-to-{target.drug_relation_label} edge."
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


def _has_drug(graph: dict[str, Any]) -> bool:
    return "drug0" in _nodes_by_id(graph)


def _required_input_edges(target: Target) -> set[tuple[str, str, str]]:
    required = {
        ("determinant", "RO:0000056", "mech0"),
        ("mech0", "RO:0002411", "resistance"),
        ("determinant", "RO:0002411", "resistance"),
    }
    if target.drug_relation_reference is not None:
        required.add(("determinant", "ARO:2000001", "drug0"))
    return required


def _output_expected_edges(target: Target) -> set[tuple[str, str, str]]:
    expected = {
        *_required_input_edges(target),
        ("determinant", "RO:0002327", "glucan_synthase_activity"),
        ("glucan_synthase_activity", "BFO:0000050", "beta_glucan_biosynthesis"),
    }
    if target.include_cell_wall:
        expected.add(
            ("beta_glucan_biosynthesis", "BFO:0000050", "fungal_cell_wall_biogenesis")
        )
    return expected


def _input_allowed_edges(target: Target) -> set[tuple[str, str, str]]:
    allowed = _output_expected_edges(target)
    allowed.update(
        {
            ("determinant", "RO:0002327", "glucan_synthesis"),
            ("glucan_synthesis", "BFO:0000050", "cell_wall"),
        }
    )
    return allowed


def _validate_graph(graph: dict[str, Any], target: Target) -> None:
    allowed = _input_allowed_edges(target)
    required = _required_input_edges(target)

    if _has_drug(graph) != (target.drug_relation_reference is not None):
        raise ValueError(f"{target.identifier}: unexpected drug0 node")

    found = set()
    seen: set[tuple[str, str, str]] = set()
    for edge in graph.get("edges") or []:
        full_key = _edge_key(edge)
        if full_key not in allowed:
            raise ValueError(f"{target.identifier}: unexpected edge {full_key[0]} -> {full_key[2]}")
        if full_key in seen:
            raise ValueError(f"{target.identifier}: duplicate edge {full_key[0]} -> {full_key[2]}")
        seen.add(full_key)

        if full_key in required:
            found.add(full_key)

    missing_edges = sorted(required - found)
    if missing_edges:
        missing = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in missing_edges)
        raise ValueError(f"{target.identifier}: missing edge(s): {missing}")


def _enrich_nodes(graph: dict[str, Any], target: Target) -> None:
    nodes = _nodes_by_id(graph)
    required = {"determinant"}
    if target.drug_relation_reference is not None:
        required.add("drug0")

    missing = sorted(required - set(nodes))
    if missing:
        missing_ids = ", ".join(missing)
        raise ValueError(f"{target.identifier}: missing node(s): {missing_ids}")

    ordered = [
        copy.deepcopy(nodes["determinant"]),
        copy.deepcopy(MECHANISM_NODE),
    ]
    if target.drug_relation_reference is not None:
        ordered.append(copy.deepcopy(nodes["drug0"]))
    ordered.extend(
        [
            copy.deepcopy(GLUCAN_SYNTHASE_NODE),
            copy.deepcopy(BETA_GLUCAN_BIOSYNTHESIS_NODE),
        ]
    )
    if target.include_cell_wall:
        ordered.append(copy.deepcopy(FUNGAL_CELL_WALL_NODE))
    ordered.append(copy.deepcopy(RESISTANCE_NODE))
    graph["nodes"] = ordered


def _activity_evidence(target_evidence: dict[str, str], target: Target) -> tuple[dict[str, str], ...]:
    if target.identifier == "ARO:3007548":
        return (target_evidence, ECHINOCANDIN_BRANCH_EVIDENCE, GO_ACTIVITY_EVIDENCE)
    return (target_evidence, GO_ACTIVITY_EVIDENCE)


def _canonical_edges(record: dict[str, Any], target: Target) -> list[dict[str, Any]]:
    target_evidence = _target_evidence(record)
    edges = [
        _edge(
            "determinant",
            "participates in (resistance mechanism)",
            "RO:0000056",
            "mech0",
            "The ARO hierarchy classifies resistant beta-glucan synthases under point mutations.",
            (target_evidence, MUTATION_EVIDENCE),
        ),
        _edge(
            "mech0",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            (
                "ARO links this point-mutation mechanism to resistance in the "
                "beta-1,3-D-glucan synthase target enzyme."
            ),
            (target_evidence, MUTATION_EVIDENCE),
        ),
        _edge(
            "determinant",
            "causally upstream of (confers resistance)",
            "RO:0002411",
            "resistance",
            (
                "The local ARO definition states that beta-1,3-D-glucan "
                "synthase mutations confer antifungal resistance."
            ),
            (target_evidence, MUTATION_EVIDENCE),
        ),
    ]

    if target.drug_relation_reference is not None:
        drug_evidence = (target_evidence, _drug_evidence(target), MUTATION_EVIDENCE)
        if target.identifier == "ARO:3007548":
            drug_evidence = (
                target_evidence,
                ECHINOCANDIN_BRANCH_EVIDENCE,
                _drug_evidence(target),
                MUTATION_EVIDENCE,
            )
        edges.append(
            _edge(
                "determinant",
                "confers resistance to (drug class)",
                "ARO:2000001",
                "drug0",
                (
                    "The ARO hierarchy links this determinant to the "
                    f"{target.drug_relation_label} resistance class."
                ),
                drug_evidence,
            )
        )

    edges.extend(
        [
            _edge(
                "determinant",
                "enables",
                "RO:0002327",
                "glucan_synthase_activity",
                "ARO identifies this determinant as a beta-1,3-D-glucan synthase.",
                _activity_evidence(target_evidence, target),
            ),
            _edge(
                "glucan_synthase_activity",
                "part of (beta-glucan biosynthesis)",
                "BFO:0000050",
                "beta_glucan_biosynthesis",
                "The beta-glucan synthase activity produces 1,3-beta-D-glucan.",
                _activity_evidence(target_evidence, target)
                + (GO_BIOSYNTHESIS_EVIDENCE,),
            ),
        ]
    )

    if target.include_cell_wall:
        edges.append(
            _edge(
                "beta_glucan_biosynthesis",
                "part of (fungal-type cell-wall biogenesis)",
                "BFO:0000050",
                "fungal_cell_wall_biogenesis",
                "The Candida FKS2 definition places beta-glucan synthesis in fungal cell-wall production.",
                (target_evidence, GO_BIOSYNTHESIS_EVIDENCE, GO_CELL_WALL_EVIDENCE),
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
    _enrich_nodes(graph, target)
    graph["graph_id"] = "resistance"
    graph["title"] = f"{record['label']} → beta-1,3-D-glucan synthase → resistance"
    graph["description"] = target.graph_description
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
        raise ValueError(f"{path}: not a beta-glucan-synthase target: {identifier}")
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
        help="ARO directory or one of the three target YAML files",
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
