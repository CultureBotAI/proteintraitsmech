#!/usr/bin/env python3
"""Ground FolP target-alteration resistance graphs.

The existing FolP-family graphs model two useful GO-groundable nodes but leave
them label-only, and they copy the dapsone-specific lowered-affinity state from
ARO:3003388 into sulfonamide sibling records. This updater keeps the branch
conservative:

* all eight local FolP records get grounded dihydropteroate-synthase and
  folate-biosynthesis nodes;
* sulfone/sulfonamide children keep only their own ARO drug-class edge;
* ungrounded lowered-affinity state nodes are dropped instead of being copied
  into records where ARO does not make that assertion.

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
HISTORY_ACTION = "Grounded FolP graphs to GO terms and removed stale dapsone affinity state"
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

SULFONAMIDE_FOLP_EVIDENCE = {
    "reference": "ARO:3003415",
    "snippet": (
        "Point mutations in dihydropteroate synthase folP prevent sulfonamide "
        "antibiotics from inhibiting its role in folate synthesis, thus "
        "conferring sulfonamide resistance."
    ),
    "notes": "CARD definition for the sulfonamide-resistant FolP branch.",
}

DAPSONE_FOLP_EVIDENCE = {
    "reference": "ARO:3003388",
    "snippet": (
        "Dapsone inhibits bacterial synthesis of dihydrofolic acid by competing "
        "with with para-aminobenzoate for the active site of dihydropteroate "
        "synthetase. Thus acts as a competitive inhibitor of folP. Point "
        "mutation within the folP gene results in lowered affinity of dapsone "
        "for folP."
    ),
    "notes": "CARD definition for the dapsone-resistant FolP branch.",
}

GO_DHPS_EVIDENCE = {
    "reference": "GO:0004156",
    "snippet": (
        "Catalysis of the reaction: "
        "2-amino-4-hydroxy-6-hydroxymethyl-7,8-dihydropteridine diphosphate + "
        "4-aminobenzoate = diphosphate + dihydropteroate."
    ),
    "notes": "GO definition for dihydropteroate synthase activity.",
}

GO_FOLATE_EVIDENCE = {
    "reference": "GO:0009396",
    "snippet": (
        "The chemical reactions and pathways resulting in the formation of folic "
        "acid and its derivatives."
    ),
    "notes": "GO definition for folic acid-containing compound biosynthetic process.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "mutation conferring antibiotic resistance",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3000212",
}

DHPS_NODE = {
    "node_id": "dhps_activity",
    "label": "dihydropteroate synthase activity",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "GO:0004156",
}

FOLATE_BIOSYNTHESIS_NODE = {
    "node_id": "folate_biosynthesis",
    "label": "folic acid-containing compound biosynthetic process",
    "node_type": "BIOLOGICAL_PROCESS",
    "grounding": "GO:0009396",
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
    drug_inhibition_evidence: tuple[dict[str, str], ...] = ()


TARGETS = {
    "ARO:3000226": Target(
        identifier="ARO:3000226",
        filename="antibiotic-resistant-folp-aro3000226.yaml",
        graph_description=(
            "Conservative graph for antibiotic-resistant FolP. The graph grounds "
            "FolP's dihydropteroate synthase activity and its role in folate "
            "biosynthesis, and it drops the dapsone-specific lowered-affinity "
            "state from this broader parent."
        ),
    ),
    "ARO:3003388": Target(
        identifier="ARO:3003388",
        filename="dapsone-resistant-dihydropteroate-synthase-folp-aro3003388.yaml",
        graph_description=(
            "Conservative graph for dapsone-resistant FolP. The graph grounds "
            "FolP's dihydropteroate synthase activity and dapsone's competitive "
            "inhibition of that activity without keeping an ungrounded local "
            "low-affinity state node."
        ),
        drug_relation_reference="ARO:3003388",
        drug_relation_object="ARO:3003401",
        drug_relation_label="sulfone antibiotic",
        drug_inhibition_evidence=(DAPSONE_FOLP_EVIDENCE,),
    ),
    "ARO:3003415": Target(
        identifier="ARO:3003415",
        filename="sulfonamide-resistant-dihydropteroate-synthase-folp-aro3003415.yaml",
        graph_description=(
            "Conservative graph for sulfonamide-resistant FolP. The graph "
            "grounds FolP's dihydropteroate synthase activity and sulfonamide "
            "inhibition of that activity without borrowing the dapsone-specific "
            "low-affinity state."
        ),
        drug_relation_reference="ARO:3003415",
        drug_relation_object="ARO:3000282",
        drug_relation_label="sulfonamide antibiotic",
        drug_inhibition_evidence=(SULFONAMIDE_FOLP_EVIDENCE,),
    ),
    "ARO:3003386": Target(
        identifier="ARO:3003386",
        filename=(
            "escherichia-coli-folp-with-mutation-conferring-resistance-to-"
            "sulfonamides-aro3003386.yaml"
        ),
        graph_description=(
            "Conservative graph for Escherichia coli FolP sulfonamide "
            "resistance. The graph combines this record's point-mutation "
            "resistance definition with the inherited sulfonamide FolP "
            "drug-class and dihydropteroate-synthase context."
        ),
        drug_relation_reference="ARO:3003415",
        drug_relation_object="ARO:3000282",
        drug_relation_label="sulfonamide antibiotic",
        drug_inhibition_evidence=(SULFONAMIDE_FOLP_EVIDENCE,),
    ),
    "ARO:3003389": Target(
        identifier="ARO:3003389",
        filename=(
            "mycobacterium-leprae-folp-with-mutation-conferring-resistance-to-"
            "dapsone-aro3003389.yaml"
        ),
        graph_description=(
            "Conservative graph for Mycobacterium leprae FolP dapsone "
            "resistance. The graph combines this record's point-mutation "
            "resistance definition with the inherited dapsone-resistant FolP "
            "drug-class and dihydropteroate-synthase context."
        ),
        drug_relation_reference="ARO:3003388",
        drug_relation_object="ARO:3003401",
        drug_relation_label="sulfone antibiotic",
        drug_inhibition_evidence=(DAPSONE_FOLP_EVIDENCE,),
    ),
    "ARO:3004873": Target(
        identifier="ARO:3004873",
        filename=(
            "neisseria-gonorrhoeae-folp-with-mutation-conferring-resistance-to-"
            "sulfonamides-aro3004873.yaml"
        ),
        graph_description=(
            "Conservative graph for Neisseria gonorrhoeae FolP sulfonamide "
            "resistance. The graph combines this record's point-mutation "
            "resistance definition with the inherited sulfonamide FolP "
            "drug-class and dihydropteroate-synthase context."
        ),
        drug_relation_reference="ARO:3003415",
        drug_relation_object="ARO:3000282",
        drug_relation_label="sulfonamide antibiotic",
        drug_inhibition_evidence=(SULFONAMIDE_FOLP_EVIDENCE,),
    ),
    "ARO:3007749": Target(
        identifier="ARO:3007749",
        filename=(
            "salmonella-gallinarum-folp-with-mutation-conferring-resistance-to-"
            "sulfonamides-aro3007749.yaml"
        ),
        graph_description=(
            "Conservative graph for Salmonella gallinarum FolP sulfonamide "
            "resistance. The graph grounds FolP as a dihydropteroate synthase "
            "and keeps the inherited sulfonamide drug-class claim, but omits "
            "the sibling dapsone lowered-affinity route because this record "
            "instead reports altered FolP stability."
        ),
        drug_relation_reference="ARO:3003415",
        drug_relation_object="ARO:3000282",
        drug_relation_label="sulfonamide antibiotic",
    ),
    "ARO:3003387": Target(
        identifier="ARO:3003387",
        filename=(
            "streptococcus-pyogenes-folp-with-mutation-conferring-resistance-to-"
            "sulfonamides-aro3003387.yaml"
        ),
        graph_description=(
            "Conservative graph for Streptococcus pyogenes FolP sulfonamide "
            "resistance. The graph combines this record's point-mutation "
            "resistance definition with the inherited sulfonamide FolP "
            "drug-class and dihydropteroate-synthase context."
        ),
        drug_relation_reference="ARO:3003415",
        drug_relation_object="ARO:3000282",
        drug_relation_label="sulfonamide antibiotic",
        drug_inhibition_evidence=(SULFONAMIDE_FOLP_EVIDENCE,),
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


def _output_expected_edges(target: Target) -> set[tuple[str, str, str]]:
    expected = {
        ("determinant", "RO:0000056", "mech0"),
        ("mech0", "RO:0002411", "resistance"),
        ("determinant", "RO:0002411", "resistance"),
        ("determinant", "RO:0002327", "dhps_activity"),
        ("dhps_activity", "BFO:0000050", "folate_biosynthesis"),
    }
    if target.drug_relation_reference is not None:
        expected.add(("determinant", "ARO:2000001", "drug0"))
    if target.drug_inhibition_evidence:
        expected.add(("drug0", "RO:0002212", "dhps_activity"))
    return expected


def _input_expected_edges(target: Target) -> set[tuple[str, str, str]]:
    expected = set(_output_expected_edges(target))
    expected.add(("dhps_activity", "BFO:0000050", "folate_synthesis"))
    expected.update(
        {
            ("determinant", "RO:0000086", "low_affinity"),
            ("low_affinity", "RO:0002411", "dhps_activity"),
        }
    )
    if target.drug_relation_reference is not None:
        expected.add(("drug0", "RO:0002212", "dhps_activity"))
    return expected


def _validate_graph(graph: dict[str, Any], target: Target) -> None:
    allowed = _input_expected_edges(target)
    canonical = _output_expected_edges(target)

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

        if full_key == ("dhps_activity", "BFO:0000050", "folate_synthesis"):
            found.add(("dhps_activity", "BFO:0000050", "folate_biosynthesis"))
        elif full_key[2] != "low_affinity" and full_key[0] != "low_affinity":
            found.add(full_key)

    missing_edges = sorted(canonical - found)
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
            copy.deepcopy(DHPS_NODE),
            copy.deepcopy(FOLATE_BIOSYNTHESIS_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ]
    )
    graph["nodes"] = ordered


def _canonical_edges(record: dict[str, Any], target: Target) -> list[dict[str, Any]]:
    target_evidence = _target_evidence(record)
    edges = [
        _edge(
            "determinant",
            "participates in (resistance mechanism)",
            "RO:0000056",
            "mech0",
            "The ARO hierarchy classifies FolP variants under point mutations.",
            (target_evidence, MUTATION_EVIDENCE),
        ),
        _edge(
            "mech0",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            (
                "ARO links this point-mutation mechanism to antibiotic "
                "resistance in the FolP target enzyme."
            ),
            (target_evidence, MUTATION_EVIDENCE),
        ),
        _edge(
            "determinant",
            "causally upstream of (confers resistance)",
            "RO:0002411",
            "resistance",
            "The local ARO definition states that these FolP mutations confer resistance.",
            (target_evidence, MUTATION_EVIDENCE),
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
                    "The ARO hierarchy links this FolP determinant to the "
                    f"inherited {target.drug_relation_label} resistance class."
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
                "dhps_activity",
                "ARO identifies this FolP determinant as a dihydropteroate synthase.",
                (target_evidence, GO_DHPS_EVIDENCE),
            ),
            _edge(
                "dhps_activity",
                "part of (folate biosynthesis)",
                "BFO:0000050",
                "folate_biosynthesis",
                "The ARO definition places the FolP activity in folate synthesis.",
                (target_evidence, GO_FOLATE_EVIDENCE),
            ),
        ]
    )

    if target.drug_inhibition_evidence:
        edges.append(
            _edge(
                "drug0",
                "negatively regulates",
                "RO:0002212",
                "dhps_activity",
                (
                    "This drug class inhibits dihydropteroate synthase activity "
                    "at the para-aminobenzoate site."
                ),
                (target_evidence, *target.drug_inhibition_evidence, GO_DHPS_EVIDENCE),
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
    graph["title"] = f"{record['label']} → FolP target alteration → resistance"
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
        raise ValueError(f"{path}: not a FolP target: {identifier}")
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
        help="ARO directory or one of the eight target YAML files",
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
