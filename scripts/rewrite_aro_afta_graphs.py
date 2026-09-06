#!/usr/bin/env python3
"""Ground AftA/arabinofuranosyltransferase resistance graphs.

The existing AftA-family graphs carried a local arabinofuranosyltransferase
activity node and a local mAGP node with no CURIEs. They also copied the AftA
parent role across a small branch that includes the generic rifamycin-resistant
arabinosyltransferase class and an embB descendant.

This updater keeps the graphs conservative:

* exact AftA records use EC:2.4.2.46, the galactan
  5-O-arabinofuranosyltransferase activity;
* rifamycin/embB records fall back to the broader EC:2.4.2.-
  pentosyltransferase class;
* all records end the biosynthetic context at grounded
  GO:0071766 Actinobacterium-type cell-wall biogenesis rather than inventing a
  ChEBI class for the whole mAGP complex.

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
        "Grounded AftA/arabinofuranosyltransferase graphs to EC and GO "
        "cell-wall-biosynthesis terms and removed the ungrounded mAGP endpoint"
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

AFTA_PARENT_EVIDENCE = {
    "reference": "ARO:3003422",
    "snippet": (
        "Arabinofuranosyltransferase is involved in the biosynthesis of the "
        "arabinogalactan region of the mAGP complex, an essential component of "
        "the mycobacterial cell wall."
    ),
    "notes": "CARD definition for the antibiotic-resistant aftA parent term.",
}

RIF_ARABINOSYLTRANSFERASE_EVIDENCE = {
    "reference": "ARO:3003464",
    "snippet": (
        "Arabinosyl transferases allow for the polymerization of arabinose to "
        "form arabinan. Arabanan is required for formation of mycobacterial cell "
        "walls and arabinosyltransferases are targets of the drug ethambutol. "
        "Mutations in these genes can confer resistance to rifampicin."
    ),
    "notes": (
        "CARD definition for the rifamycin-resistant arabinosyltransferase "
        "ancestor term."
    ),
}

ETHAMBUTOL_AFTA_EVIDENCE = {
    "reference": "ARO:3002876",
    "snippet": (
        "Arabinofuranosyltransferases allow for the polymerization of arabinose "
        "to form arabinan. Arabinan is required for formation of mycobacterial "
        "cell walls and arabinosyltransferases are targets of the drug "
        "ethambutol. Mutations in these genes can confer resistance to "
        "ethambutol."
    ),
    "notes": "CARD definition for the ethambutol-resistant aftA ancestor term.",
}

EC_AFTA_EVIDENCE = {
    "reference": "EC:2.4.2.46",
    "snippet": (
        "Adds an alpha-D-arabinofuranosyl group from "
        "trans,octacis-decaprenylphospho-beta-D-arabinofuranose at the "
        "5-O-position of the eighth, tenth and twelfth galactofuranose unit of "
        "the galactofuranan chain of "
        "[beta-D-galactofuranosyl-(1->5)-beta-D-galactofuranosyl- "
        "(1->6)]14-beta-D-galactofuranosyl-(1->5)-beta-D-galactofuranosyl-(1->4)- "
        "alpha-L-rhamnopyranosyl-(1->3)-N-acetyl-alpha-D-glucosaminyl-diphospho- "
        "trans,octacis-decaprenol"
    ),
    "notes": (
        "ExPASy ENZYME definition for EC 2.4.2.46, the galactan "
        "5-O-arabinofuranosyltransferase activity."
    ),
}

EC_PENTOSYLTRANSFERASE_EVIDENCE = {
    "reference": "EC:2.4.2.-",
    "snippet": "A transferase; glycosyltransferases; pentosyltransferases.",
    "notes": (
        "EC nomenclature grounding for the broad pentosyltransferase class used "
        "where the ARO term is broader than AftA."
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
        "the mycobacterial cell-wall context named by ARO."
    ),
}

AFTA_ACTIVITY_NODE = {
    "node_id": "afta_activity",
    "label": "galactan 5-O-arabinofuranosyltransferase",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "EC:2.4.2.46",
    "description": (
        "Grounded to the EC enzymatic activity specific to AftA-mediated "
        "5-O-arabinofuranosyl transfer onto a galactofuranan chain."
    ),
}

BROAD_PENTOSYLTRANSFERASE_NODE = {
    "node_id": "pentosyltransferase_activity",
    "label": "pentosyltransferase activity",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "EC:2.4.2.-",
    "description": (
        "Grounded to the broad EC pentosyltransferase class because this ARO "
        "rifamycin branch covers arabinosyltransferases rather than a single "
        "AftA-specific reaction."
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
    activity_node: dict[str, str]
    activity_evidence: dict[str, str]
    inherited_role_evidence: tuple[dict[str, str], ...] = ()
    inherited_resistance_evidence: tuple[dict[str, str], ...] = ()
    target_definition_supports_role: bool = True
    drug_relation_reference: str | None = None
    drug_relation_object: str | None = None
    drug_relation_label: str | None = None


TARGETS = {
    "ARO:3003422": Target(
        identifier="ARO:3003422",
        filename="antibiotic-resistant-afta-aro3003422.yaml",
        graph_description=(
            "Conservative role-only graph for antibiotic resistant aftA. The "
            "graph keeps ARO's inherited mutation-conferring-resistance class, "
            "grounds AftA as EC:2.4.2.46 galactan "
            "5-O-arabinofuranosyltransferase, and places that activity in "
            "Actinobacterium-type cell-wall biogenesis. No drug-specific "
            "resistance route or mutation-to-activity effect is asserted for "
            "this parent."
        ),
        activity_node=AFTA_ACTIVITY_NODE,
        activity_evidence=EC_AFTA_EVIDENCE,
    ),
    "ARO:3002876": Target(
        identifier="ARO:3002876",
        filename="ethambutol-resistant-afta-aro3002876.yaml",
        graph_description=(
            "Conservative graph for ethambutol resistant aftA. ARO links this "
            "class to ethambutol/polyamine-antibiotic resistance and identifies "
            "arabinofuranosyltransferase activity in mycobacterial cell-wall "
            "arabinan biosynthesis; the graph grounds AftA as EC:2.4.2.46 but "
            "does not assert how resistance mutations alter that activity."
        ),
        activity_node=AFTA_ACTIVITY_NODE,
        activity_evidence=EC_AFTA_EVIDENCE,
        inherited_role_evidence=(AFTA_PARENT_EVIDENCE,),
        drug_relation_reference="ARO:3002876",
        drug_relation_object="ARO:3000527",
        drug_relation_label="polyamine antibiotic",
    ),
    "ARO:3003464": Target(
        identifier="ARO:3003464",
        filename="rifamycin-resistant-arabinosyltransferase-aro3003464.yaml",
        graph_description=(
            "Conservative graph for rifamycin-resistant "
            "arabinosyltransferase. The ARO class says mutations in these "
            "genes can confer rifampicin resistance, but does not identify a "
            "specific AftA reaction or a rifamycin target-modification route, "
            "so the arabinosyltransferase role is grounded only to broad "
            "EC:2.4.2.- pentosyltransferase activity."
        ),
        activity_node=BROAD_PENTOSYLTRANSFERASE_NODE,
        activity_evidence=EC_PENTOSYLTRANSFERASE_EVIDENCE,
        drug_relation_reference="ARO:3003464",
        drug_relation_object="ARO:3000157",
        drug_relation_label="rifamycin antibiotic",
    ),
    "ARO:3004951": Target(
        identifier="ARO:3004951",
        filename=(
            "mycobacterium-tuberculosis-afta-mutations-confer-resistance-to-"
            "ethambutol-aro3004951.yaml"
        ),
        graph_description=(
            "Conservative graph for Mycobacterium tuberculosis aftA mutations "
            "conferring ethambutol resistance. The graph combines this "
            "point-mutation resistance claim with the inherited "
            "arabinofuranosyltransferase role, grounds the role as "
            "EC:2.4.2.46, and stops before any unsupported "
            "mutation-to-activity edge."
        ),
        activity_node=AFTA_ACTIVITY_NODE,
        activity_evidence=EC_AFTA_EVIDENCE,
        inherited_role_evidence=(ETHAMBUTOL_AFTA_EVIDENCE, AFTA_PARENT_EVIDENCE),
        inherited_resistance_evidence=(ETHAMBUTOL_AFTA_EVIDENCE,),
        target_definition_supports_role=False,
        drug_relation_reference="ARO:3002876",
        drug_relation_object="ARO:3000527",
        drug_relation_label="polyamine antibiotic",
    ),
    "ARO:3003465": Target(
        identifier="ARO:3003465",
        filename=(
            "mycobacterium-tuberculosis-embb-with-mutation-conferring-"
            "resistance-to-rifampici-aro3003465.yaml"
        ),
        graph_description=(
            "Conservative graph for Mycobacterium tuberculosis embB mutations "
            "conferring rifampicin resistance. The graph combines this "
            "point-mutation resistance claim with the inherited "
            "rifamycin-resistant arabinosyltransferase role, grounds the role "
            "only to broad EC:2.4.2.- pentosyltransferase activity, and stops "
            "before any unsupported AftA-specific or rifamycin "
            "target-modification edge."
        ),
        activity_node=BROAD_PENTOSYLTRANSFERASE_NODE,
        activity_evidence=EC_PENTOSYLTRANSFERASE_EVIDENCE,
        inherited_role_evidence=(RIF_ARABINOSYLTRANSFERASE_EVIDENCE,),
        inherited_resistance_evidence=(RIF_ARABINOSYLTRANSFERASE_EVIDENCE,),
        target_definition_supports_role=False,
        drug_relation_reference="ARO:3003464",
        drug_relation_object="ARO:3000157",
        drug_relation_label="rifamycin antibiotic",
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


def _input_expected_edges(graph: dict[str, Any], target: Target) -> set[tuple[str, str, str]]:
    expected = {
        ("determinant", "RO:0002411", "resistance"),
        ("determinant", "RO:0000056", "mech0"),
        ("mech0", "RO:0002411", "resistance"),
        ("determinant", "RO:0000056", "arabinofuranosyl_transfer"),
        ("arabinofuranosyl_transfer", "RO:0002234", "magp"),
        ("determinant", "RO:0002327", target.activity_node["node_id"]),
        (target.activity_node["node_id"], "BFO:0000050", "cell_wall_biogenesis"),
    }
    if target.drug_relation_reference is not None:
        expected.add(("determinant", "ARO:2000001", "drug0"))
    return expected


def _output_expected_edges(graph: dict[str, Any], target: Target) -> set[tuple[str, str, str]]:
    expected = {
        ("determinant", "RO:0002411", "resistance"),
        ("determinant", "RO:0000056", "mech0"),
        ("mech0", "RO:0002411", "resistance"),
        ("determinant", "RO:0002327", target.activity_node["node_id"]),
        (target.activity_node["node_id"], "BFO:0000050", "cell_wall_biogenesis"),
    }
    if target.drug_relation_reference is not None:
        expected.add(("determinant", "ARO:2000001", "drug0"))
    return expected


def _validate_graph(graph: dict[str, Any], target: Target) -> None:
    allowed = _input_expected_edges(graph, target)
    canonical = _output_expected_edges(graph, target)

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

        if full_key == ("determinant", "RO:0000056", "arabinofuranosyl_transfer"):
            full_edges.add(("determinant", "RO:0002327", target.activity_node["node_id"]))
        elif full_key == ("arabinofuranosyl_transfer", "RO:0002234", "magp"):
            full_edges.add((target.activity_node["node_id"], "BFO:0000050", "cell_wall_biogenesis"))
        else:
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
    ordered.extend(
        [
            copy.deepcopy(target.activity_node),
            copy.deepcopy(ACTINOBACTERIAL_CELL_WALL_NODE),
            copy.deepcopy(nodes["resistance"]),
        ]
    )
    graph["nodes"] = ordered


def _canonical_edges(
    graph: dict[str, Any],
    record: dict[str, Any],
    target: Target,
) -> list[dict[str, Any]]:
    target_evidence = _target_evidence(record)
    role_evidence = (
        *([target_evidence] if target.target_definition_supports_role else []),
        *target.inherited_role_evidence,
    )
    resistance_evidence = (target_evidence, *target.inherited_resistance_evidence)
    activity = target.activity_node["node_id"]

    edges = [
        _edge(
            "determinant",
            "participates in (resistance mechanism)",
            "RO:0000056",
            "mech0",
            (
                "The ARO hierarchy classifies this determinant under mutation "
                "conferring antibiotic resistance, while this graph leaves the "
                "mutation-to-cell-wall effect unresolved."
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
                "to the resistance phenotype without specifying the altered "
                "arabinogalactan chemistry."
            ),
            (target_evidence, MUTATION_EVIDENCE),
        ),
        _edge(
            "determinant",
            "causally upstream of (confers resistance)",
            "RO:0002411",
            "resistance",
            (
                "This ARO resistance determinant is kept at the class-level "
                "mutation claim; no direct drug-binding or target-modification "
                "edge is asserted."
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

    edges.extend(
        [
            _edge(
                "determinant",
                "enables",
                "RO:0002327",
                activity,
                (
                    "The determinant is represented by the arabinosyltransferase "
                    "role named in ARO; the edge does not assert how resistance "
                    "mutations alter this activity."
                ),
                (*role_evidence, target.activity_evidence),
            ),
            _edge(
                activity,
                "part of (Actinobacterium-type cell-wall biogenesis)",
                "BFO:0000050",
                "cell_wall_biogenesis",
                (
                    "The arabinosyltransferase role is kept as cell-wall "
                    "biosynthesis context, not as a complete resistance route."
                ),
                (*role_evidence, GO_CELL_WALL_EVIDENCE),
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
    graph = next((item for item in graphs if item.get("graph_id") == "resistance"), None)
    if graph is None:
        raise ValueError(f"{target.identifier}: missing resistance causal graph")

    _validate_graph(graph, target)
    _enrich_nodes(graph, target)
    graph["description"] = target.graph_description
    graph["edges"] = _canonical_edges(graph, out, target)
    return out, out.get("causal_graphs") != before


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: record is not a mapping")
    identifier = record.get("identifier")
    target = TARGETS.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not an AftA/arabinofuranosyltransferase target: {identifier}")
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
        help="ARO directory or one of the five target YAML files",
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
