#!/usr/bin/env python3
"""Ground EMB arabinosyltransferase resistance graphs.

The existing EMB-family graphs copied an embB-specific explanatory sentence into
embA, embC, and embR, then modeled three local label-only nodes for arabinosyl
transfer, arabinogalactan synthesis, and ethambutol inhibition.  This updater
keeps the branch conservative:

* embA, embB, and embC transferase records are grounded to broad EC:2.4.2.-
  pentosyltransferase activity;
* embB records keep ARO's arabinogalactan-synthesis context, grounded to
  GO:0071766 Actinobacterium-type cell-wall biogenesis;
* embR records keep only the mutation-to-resistance and drug-class claims,
  because the local ARO definition does not support modeling EmbR as a direct
  arabinosyltransferase.

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
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": (
        "Grounded EMB arabinosyltransferase graphs to EC and GO terms and "
        "removed embB-specific ungrounded edges from non-embB records"
    ),
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

EMB_FAMILY_EVIDENCE = {
    "reference": "ARO:3005005",
    "snippet": (
        "Known antibiotic-resistant variants of emb arabinosyltransferases, "
        "primarily in Mycobacterium and conferring resistance to ethambutol "
        "through point mutation."
    ),
    "notes": "CARD definition for the antibiotic-resistant emb arabinosyltransferase parent.",
}

EMBB_EVIDENCE = {
    "reference": "ARO:3000235",
    "snippet": (
        "embB gene encodes for an arabinosyl transferase in the arabinogalactan "
        "synthesis pathway. It is inhibited by ethambutol. Mutations within the "
        "ERDR region of embB confers resistance to ethambutol."
    ),
    "notes": "CARD definition for the ethambutol-resistant embB parent.",
}

EC_PENTOSYLTRANSFERASE_EVIDENCE = {
    "reference": "EC:2.4.2.-",
    "snippet": "A transferase; glycosyltransferases; pentosyltransferases.",
    "notes": (
        "EC nomenclature grounding for the broad pentosyltransferase class used "
        "where the ARO term names an arabinosyltransferase branch rather than a "
        "single exact reaction."
    ),
}

GO_CELL_WALL_EVIDENCE = {
    "reference": "GO:0071766",
    "snippet": (
        "A cellular process that results in the biosynthesis of constituent "
        "macromolecules, assembly, and arrangement of constituent parts of a cell "
        "wall of the type found in Actinobacteria."
    ),
    "notes": (
        "GO definition for Actinobacterium-type cell-wall biogenesis, matching "
        "the mycobacterial cell-wall context named by embB's ARO definition."
    ),
}

PENTOSYLTRANSFERASE_NODE = {
    "node_id": "pentosyltransferase_activity",
    "label": "pentosyltransferase activity",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "EC:2.4.2.-",
    "description": (
        "Grounded to the broad EC pentosyltransferase class because EMB "
        "arabinosyltransferase ARO terms do not identify a single exact "
        "arabinosyl-transfer reaction."
    ),
}

ACTINOBACTERIAL_CELL_WALL_NODE = {
    "node_id": "cell_wall_biogenesis",
    "label": "Actinobacterium-type cell wall biogenesis",
    "node_type": "BIOLOGICAL_PROCESS",
    "grounding": "GO:0071766",
    "description": (
        "Grounded to the GO process for biosynthesis and assembly of "
        "Actinobacterium-type cell-wall macromolecules."
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
    target_definition_supports_role: bool = False
    inherited_role_evidence: tuple[dict[str, str], ...] = ()
    inherited_resistance_evidence: tuple[dict[str, str], ...] = ()
    include_activity: bool = True
    include_cell_wall: bool = False


TARGETS = {
    "ARO:3005005": Target(
        identifier="ARO:3005005",
        filename="antibiotic-resistant-emb-arabinosyltransferase-aro3005005.yaml",
        graph_description=(
            "Conservative graph for antibiotic-resistant emb "
            "arabinosyltransferase. The graph grounds the EMB "
            "arabinosyltransferase role to broad EC:2.4.2.- "
            "pentosyltransferase activity and keeps the mutation claim at the "
            "resistance-phenotype level."
        ),
        target_definition_supports_role=True,
    ),
    "ARO:3000235": Target(
        identifier="ARO:3000235",
        filename="ethambutol-resistant-embb-aro3000235.yaml",
        graph_description=(
            "Conservative graph for ethambutol resistant embB. ARO identifies "
            "EmbB as an arabinosyltransferase in the arabinogalactan pathway "
            "and links mutations in embB to ethambutol resistance; the graph "
            "grounds the enzymatic role but does not invent a stable CURIE for "
            "the local drug-inhibition state."
        ),
        drug_relation_reference="ARO:3000235",
        drug_relation_object="ARO:3000527",
        drug_relation_label="polyamine antibiotic",
        target_definition_supports_role=True,
        include_cell_wall=True,
    ),
    "ARO:3002706": Target(
        identifier="ARO:3002706",
        filename="ethambutol-resistant-embc-aro3002706.yaml",
        graph_description=(
            "Conservative graph for ethambutol resistant embC. The graph "
            "combines the embC mutation-to-resistance definition with the "
            "inherited EMB arabinosyltransferase role, grounded only to broad "
            "EC:2.4.2.- pentosyltransferase activity."
        ),
        drug_relation_reference="ARO:3002706",
        drug_relation_object="ARO:3000527",
        drug_relation_label="polyamine antibiotic",
        inherited_role_evidence=(EMB_FAMILY_EVIDENCE,),
    ),
    "ARO:3003452": Target(
        identifier="ARO:3003452",
        filename="ethambutol-resistant-emba-aro3003452.yaml",
        graph_description=(
            "Conservative graph for ethambutol resistant embA. The graph "
            "combines the embA mutation-to-resistance definition with the "
            "inherited EMB arabinosyltransferase role, grounded only to broad "
            "EC:2.4.2.- pentosyltransferase activity."
        ),
        drug_relation_reference="ARO:3003452",
        drug_relation_object="ARO:3000527",
        drug_relation_label="polyamine antibiotic",
        inherited_role_evidence=(EMB_FAMILY_EVIDENCE,),
    ),
    "ARO:3003454": Target(
        identifier="ARO:3003454",
        filename="ethambutol-resistant-embr-aro3003454.yaml",
        graph_description=(
            "Conservative graph for ethambutol resistant embR. The graph keeps "
            "the mutation-to-resistance and polyamine-antibiotic drug-class "
            "claims, and removes the inherited embB arabinosyltransferase "
            "activity edges because this ARO term names embR."
        ),
        drug_relation_reference="ARO:3003454",
        drug_relation_object="ARO:3000527",
        drug_relation_label="polyamine antibiotic",
        include_activity=False,
    ),
    "ARO:3003326": Target(
        identifier="ARO:3003326",
        filename=(
            "mycobacterium-tuberculosis-embb-mutant-conferring-resistance-to-"
            "ethambutol-aro3003326.yaml"
        ),
        graph_description=(
            "Conservative graph for Mycobacterium tuberculosis embB mutations "
            "conferring ethambutol resistance. The graph combines this "
            "point-mutation resistance claim with the inherited "
            "ethambutol-resistant embB activity and cell-wall context."
        ),
        drug_relation_reference="ARO:3000235",
        drug_relation_object="ARO:3000527",
        drug_relation_label="polyamine antibiotic",
        inherited_role_evidence=(EMBB_EVIDENCE,),
        inherited_resistance_evidence=(EMBB_EVIDENCE,),
        include_cell_wall=True,
    ),
    "ARO:3003325": Target(
        identifier="ARO:3003325",
        filename=(
            "mycobacterium-tuberculosis-variant-bovis-embb-with-mutation-"
            "conferring-resistanc-aro3003325.yaml"
        ),
        graph_description=(
            "Conservative graph for Mycobacterium tuberculosis variant bovis "
            "embB mutations conferring ethambutol resistance. The graph "
            "combines this point-mutation resistance claim with the inherited "
            "ethambutol-resistant embB activity and cell-wall context."
        ),
        drug_relation_reference="ARO:3000235",
        drug_relation_object="ARO:3000527",
        drug_relation_label="polyamine antibiotic",
        inherited_role_evidence=(EMBB_EVIDENCE,),
        inherited_resistance_evidence=(EMBB_EVIDENCE,),
        include_cell_wall=True,
    ),
    "ARO:3003453": Target(
        identifier="ARO:3003453",
        filename=(
            "mycobacterium-tuberculosis-emba-mutant-conferring-resistance-to-"
            "ethambutol-aro3003453.yaml"
        ),
        graph_description=(
            "Conservative graph for Mycobacterium tuberculosis embA mutations "
            "conferring ethambutol resistance. The graph combines this "
            "point-mutation resistance claim with the inherited EMB "
            "arabinosyltransferase role, grounded only to broad EC:2.4.2.- "
            "pentosyltransferase activity."
        ),
        drug_relation_reference="ARO:3003452",
        drug_relation_object="ARO:3000527",
        drug_relation_label="polyamine antibiotic",
        inherited_role_evidence=(EMB_FAMILY_EVIDENCE,),
    ),
    "ARO:3003327": Target(
        identifier="ARO:3003327",
        filename=(
            "mycobacterium-tuberculosis-embc-mutant-conferring-resistance-to-"
            "ethambutol-aro3003327.yaml"
        ),
        graph_description=(
            "Conservative graph for Mycobacterium tuberculosis embC mutations "
            "conferring ethambutol resistance. The graph combines this "
            "point-mutation resistance claim with the inherited EMB "
            "arabinosyltransferase role, grounded only to broad EC:2.4.2.- "
            "pentosyltransferase activity."
        ),
        drug_relation_reference="ARO:3002706",
        drug_relation_object="ARO:3000527",
        drug_relation_label="polyamine antibiotic",
        inherited_role_evidence=(EMB_FAMILY_EVIDENCE,),
    ),
    "ARO:3003455": Target(
        identifier="ARO:3003455",
        filename=(
            "mycobacterium-tuberculosis-embr-mutant-conferring-resistance-to-"
            "ethambutol-aro3003455.yaml"
        ),
        graph_description=(
            "Conservative graph for Mycobacterium tuberculosis embR mutations "
            "conferring ethambutol resistance. The graph keeps the "
            "mutation-to-resistance and inherited polyamine-antibiotic "
            "drug-class claims, and removes the inherited embB "
            "arabinosyltransferase activity edges because this ARO term names "
            "embR."
        ),
        drug_relation_reference="ARO:3003454",
        drug_relation_object="ARO:3000527",
        drug_relation_label="polyamine antibiotic",
        include_activity=False,
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


def _pair_key(edge: dict[str, Any]) -> tuple[str, str]:
    return str(edge.get("subject", "")), str(edge.get("object", ""))


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


def _mechanism_nodes(graph: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        node
        for node in graph.get("nodes") or []
        if isinstance(node, dict) and str(node.get("node_id", "")).startswith("mech")
    ]


def _nodes_by_id(graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(node["node_id"]): node
        for node in graph.get("nodes") or []
        if isinstance(node, dict) and "node_id" in node
    }


def _has_drug(graph: dict[str, Any]) -> bool:
    return "drug0" in _nodes_by_id(graph)


def _output_expected_edges(target: Target) -> set[tuple[str, str, str]]:
    expected = {
        ("determinant", "RO:0002411", "resistance"),
        ("determinant", "RO:0000056", "mech0"),
        ("mech0", "RO:0002411", "resistance"),
    }
    if target.drug_relation_reference is not None:
        expected.add(("determinant", "ARO:2000001", "drug0"))
    if target.include_activity:
        expected.add(("determinant", "RO:0002327", "pentosyltransferase_activity"))
    if target.include_cell_wall:
        expected.add(("pentosyltransferase_activity", "BFO:0000050", "cell_wall_biogenesis"))
    return expected


def _input_expected_edges(target: Target) -> set[tuple[str, str, str]]:
    expected = _output_expected_edges(target)
    expected.update(
        {
            ("determinant", "RO:0002327", "arabinosyl_transfer"),
            ("arabinosyl_transfer", "BFO:0000050", "arabinogalactan"),
            ("determinant", "RO:0002212", "inhibition"),
        }
    )
    if target.drug_relation_reference is not None:
        expected.add(("drug0", "RO:0002411", "inhibition"))
    return expected


def _validate_graph(graph: dict[str, Any], target: Target) -> None:
    allowed = _input_expected_edges(target)
    canonical = _output_expected_edges(target)

    if _has_drug(graph) != (target.drug_relation_reference is not None):
        raise ValueError(f"{target.identifier}: unexpected drug0 node")

    full_edges = set()
    seen: set[tuple[str, str]] = set()
    for edge in graph.get("edges") or []:
        full_key = _edge_key(edge)
        if full_key not in allowed:
            raise ValueError(f"{target.identifier}: unexpected edge {full_key[0]} -> {full_key[2]}")
        if _pair_key(edge) in seen:
            pair = _pair_key(edge)
            raise ValueError(f"{target.identifier}: duplicate edge {pair[0]} -> {pair[1]}")
        seen.add(_pair_key(edge))

        if full_key == ("determinant", "RO:0002327", "arabinosyl_transfer"):
            if target.include_activity:
                full_edges.add(("determinant", "RO:0002327", "pentosyltransferase_activity"))
        elif full_key == ("arabinosyl_transfer", "BFO:0000050", "arabinogalactan"):
            if target.include_cell_wall:
                full_edges.add(
                    ("pentosyltransferase_activity", "BFO:0000050", "cell_wall_biogenesis")
                )
        elif full_key[2] != "inhibition":
            full_edges.add(full_key)

    missing_edges = sorted(canonical - full_edges)
    if missing_edges:
        missing = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in missing_edges)
        raise ValueError(f"{target.identifier}: missing edge(s): {missing}")


def _enrich_nodes(graph: dict[str, Any], target: Target) -> None:
    nodes = _nodes_by_id(graph)
    required = {"determinant", "mech0", "resistance"}
    if target.drug_relation_reference is not None:
        required.add("drug0")

    missing = sorted(required - set(nodes))
    if missing:
        missing_ids = ", ".join(missing)
        raise ValueError(f"{target.identifier}: missing node(s): {missing_ids}")

    ordered = [
        copy.deepcopy(nodes["determinant"]),
        *[copy.deepcopy(node) for node in _mechanism_nodes(graph)],
    ]
    if target.drug_relation_reference is not None:
        ordered.append(copy.deepcopy(nodes["drug0"]))
    if target.include_activity:
        ordered.append(copy.deepcopy(PENTOSYLTRANSFERASE_NODE))
    if target.include_cell_wall:
        ordered.append(copy.deepcopy(ACTINOBACTERIAL_CELL_WALL_NODE))
    ordered.append(copy.deepcopy(nodes["resistance"]))
    graph["nodes"] = ordered


def _canonical_edges(
    record: dict[str, Any],
    target: Target,
) -> list[dict[str, Any]]:
    target_evidence = _target_evidence(record)
    role_evidence = (
        *([target_evidence] if target.target_definition_supports_role else []),
        *target.inherited_role_evidence,
    )
    resistance_evidence = (target_evidence, *target.inherited_resistance_evidence)

    edges = [
        _edge(
            "determinant",
            "participates in (resistance mechanism)",
            "RO:0000056",
            "mech0",
            (
                "The ARO hierarchy classifies this determinant under mutation "
                "conferring antibiotic resistance."
            ),
            (target_evidence, MUTATION_EVIDENCE),
        ),
        _edge(
            "mech0",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            (
                "The inherited mutation mechanism links this determinant class "
                "to the resistance phenotype without specifying a lower-level "
                "biochemical state."
            ),
            (target_evidence, MUTATION_EVIDENCE),
        ),
        _edge(
            "determinant",
            "causally upstream of (confers resistance)",
            "RO:0002411",
            "resistance",
            (
                "This graph keeps the direct resistance effect at ARO's "
                "class-level mutation claim."
            ),
            (*resistance_evidence, MUTATION_EVIDENCE),
        ),
    ]

    if target.drug_relation_reference is not None:
        edges.append(
            _edge(
                "determinant",
                "confers resistance to (drug class)",
                "ARO:2000001",
                "drug0",
                (
                    "The ARO hierarchy links this determinant to the inherited "
                    f"{target.drug_relation_label} resistance class."
                ),
                (target_evidence, _drug_evidence(target), MUTATION_EVIDENCE),
            )
        )

    if target.include_activity:
        edges.append(
            _edge(
                "determinant",
                "enables",
                "RO:0002327",
                "pentosyltransferase_activity",
                (
                    "The determinant is represented by the broad EMB "
                    "arabinosyltransferase role named in ARO."
                ),
                (*role_evidence, EC_PENTOSYLTRANSFERASE_EVIDENCE),
            )
        )

    if target.include_cell_wall:
        edges.append(
            _edge(
                "pentosyltransferase_activity",
                "part of (Actinobacterium-type cell-wall biogenesis)",
                "BFO:0000050",
                "cell_wall_biogenesis",
                (
                    "The embB-specific arabinosyltransferase role is placed in "
                    "Actinobacterium-type cell-wall biogenesis."
                ),
                (*target.inherited_role_evidence, *role_evidence, GO_CELL_WALL_EVIDENCE),
            )
        )

    return edges


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
    _enrich_nodes(graph, target)
    graph["description"] = target.graph_description
    graph["edges"] = _canonical_edges(out, target)
    return out, out.get("causal_graphs") != before


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: record is not a mapping")
    identifier = record.get("identifier")
    target = TARGETS.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not an EMB arabinosyltransferase target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
    normalize_aliases = "&id" in text or "*id" in text
    if not changed and not normalize_aliases:
        return text, False

    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    if HISTORY_CURATOR not in out:
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
        help="ARO directory or one of the ten target YAML files",
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
