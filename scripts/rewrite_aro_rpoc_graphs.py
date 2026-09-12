#!/usr/bin/env python3
"""Collapse rpoC resistance graphs to ARO-supported causal claims.

The reviewed rpoC graphs deliberately avoid inventing a drug-to-RNA-polymerase
mechanism, but still carry an ungrounded active-center side path copied from the
broad rpoC parent. This updater removes that non-causal side path and keeps the
supported mutation-to-resistance route plus the ARO drug-class edge on
drug-specific descendants.

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
HISTORY_ACTION = "Collapsed rpoC graphs to grounded mutation and drug-class edges"
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

DAPTOMYCIN_RPOC_EVIDENCE = {
    "reference": "ARO:3003290",
    "snippet": (
        "Daptomycin resistant RNA polymerases include amino acids substitutions "
        "which alter the binding affinity of daptomycin to the protein, "
        "resulting in antibiotic resistance."
    ),
    "notes": "CARD definition for the daptomycin-resistant rpoC parent.",
}

VANCOMYCIN_RPOC_EVIDENCE = {
    "reference": "ARO:3004725",
    "snippet": "Point mutations in rpoC, an RNA polymerase subunit, which confer resistance to vancomycin.",
    "notes": "CARD definition for the vancomycin-resistant rpoC parent.",
}

RIFAMPICIN_RPOC_EVIDENCE = {
    "reference": "ARO:3004995",
    "snippet": "rpoC catalyzes the transcription of DNA into RNA and mutations confer resistance to rifampicin.",
    "notes": "CARD definition for the rifampicin-resistant rpoC parent.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "mutation conferring antibiotic resistance",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3000212",
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
    inherited_resistance_evidence: tuple[dict[str, str], ...] = ()


TARGETS = {
    "ARO:3003289": Target(
        identifier="ARO:3003289",
        filename="antibiotic-resistant-rpoc-aro3003289.yaml",
        graph_description=(
            "Conservative graph for the antibiotic-resistant rpoC parent. The "
            "graph keeps ARO's point-mutation resistance claim and removes the "
            "RNA-polymerase active-center side path because ARO does not link "
            "that structural role to a drug interaction or resistance mechanism."
        ),
    ),
    "ARO:3003290": Target(
        identifier="ARO:3003290",
        filename="daptomycin-resistant-beta-prime-subunit-of-rna-polymerase-rpoc-aro3003290.yaml",
        graph_description=(
            "Conservative graph for daptomycin-resistant rpoC. The graph keeps "
            "the amino-acid-substitution resistance claim and the peptide "
            "antibiotic drug-class edge without modeling an unsupported "
            "RNA-polymerase active-center route."
        ),
        drug_relation_reference="ARO:3003290",
        drug_relation_object="ARO:3000053",
        drug_relation_label="peptide antibiotic",
    ),
    "ARO:3003291": Target(
        identifier="ARO:3003291",
        filename="staphylococcus-aureus-rpoc-conferring-resistance-to-daptomycin-aro3003291.yaml",
        graph_description=(
            "Conservative graph for Staphylococcus aureus rpoC mutations "
            "conferring daptomycin resistance. The graph keeps this record's "
            "point-mutation resistance claim and the inherited peptide "
            "antibiotic drug-class edge."
        ),
        drug_relation_reference="ARO:3003290",
        drug_relation_object="ARO:3000053",
        drug_relation_label="peptide antibiotic",
        inherited_resistance_evidence=(DAPTOMYCIN_RPOC_EVIDENCE,),
    ),
    "ARO:3004725": Target(
        identifier="ARO:3004725",
        filename="vancomycin-resistant-beta-prime-subunit-of-rna-polymerase-rpoc-aro3004725.yaml",
        graph_description=(
            "Conservative graph for vancomycin-resistant rpoC. The graph keeps "
            "the point-mutation resistance claim and the glycopeptide antibiotic "
            "drug-class edge without modeling an unsupported RNA-polymerase "
            "active-center route."
        ),
        drug_relation_reference="ARO:3004725",
        drug_relation_object="ARO:3000081",
        drug_relation_label="glycopeptide antibiotic",
    ),
    "ARO:3004681": Target(
        identifier="ARO:3004681",
        filename="clostridioides-difficile-rpoc-with-mutation-conferring-resistance-to-vancomycin-aro3004681.yaml",
        graph_description=(
            "Conservative graph for Clostridioides difficile rpoC mutations "
            "conferring vancomycin resistance. The graph keeps this record's "
            "point-mutation resistance claim and the inherited glycopeptide "
            "antibiotic drug-class edge."
        ),
        drug_relation_reference="ARO:3004725",
        drug_relation_object="ARO:3000081",
        drug_relation_label="glycopeptide antibiotic",
        inherited_resistance_evidence=(VANCOMYCIN_RPOC_EVIDENCE,),
    ),
    "ARO:3004995": Target(
        identifier="ARO:3004995",
        filename="rifampicin-resistant-rpoc-aro3004995.yaml",
        graph_description=(
            "Conservative graph for rifampicin-resistant rpoC. The graph keeps "
            "the point-mutation resistance claim and the rifamycin antibiotic "
            "drug-class edge without modeling a rifampicin-to-rpoC interaction."
        ),
        drug_relation_reference="ARO:3004995",
        drug_relation_object="ARO:3000157",
        drug_relation_label="rifamycin antibiotic",
    ),
    "ARO:3004994": Target(
        identifier="ARO:3004994",
        filename="mycobacterium-tuberculosis-rpoc-mutations-confer-resistance-to-rifampicin-aro3004994.yaml",
        graph_description=(
            "Conservative graph for Mycobacterium tuberculosis rpoC mutations "
            "conferring rifampicin resistance. The graph keeps this record's "
            "point-mutation resistance claim and the inherited rifamycin "
            "antibiotic drug-class edge."
        ),
        drug_relation_reference="ARO:3004995",
        drug_relation_object="ARO:3000157",
        drug_relation_label="rifamycin antibiotic",
        inherited_resistance_evidence=(RIFAMPICIN_RPOC_EVIDENCE,),
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


def _canonical_edges(target: Target) -> set[tuple[str, str, str]]:
    edges = {
        ("determinant", "RO:0000056", "mech0"),
        ("mech0", "RO:0002411", "resistance"),
        ("determinant", "RO:0002411", "resistance"),
    }
    if target.drug_relation_reference is not None:
        edges.add(("determinant", "ARO:2000001", "drug0"))
    return edges


def _input_allowed_edges(target: Target) -> set[tuple[str, str, str]]:
    allowed = set(_canonical_edges(target))
    allowed.update(
        {
            ("determinant", "BFO:0000050", "active_center"),
            ("active_center", "BFO:0000050", "transcription"),
        }
    )
    return allowed


def _validate_graph(graph: dict[str, Any], target: Target) -> None:
    allowed = _input_allowed_edges(target)
    required = _canonical_edges(target)

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
    ordered.append(copy.deepcopy(RESISTANCE_NODE))
    graph["nodes"] = ordered


def _canonical_edge_list(record: dict[str, Any], target: Target) -> list[dict[str, Any]]:
    target_evidence = _target_evidence(record)
    resistance_evidence = (
        target_evidence,
        *target.inherited_resistance_evidence,
        MUTATION_EVIDENCE,
    )
    edges = [
        _edge(
            "determinant",
            "participates in (resistance mechanism)",
            "RO:0000056",
            "mech0",
            "The ARO hierarchy classifies resistant rpoC variants under point mutations.",
            (target_evidence, MUTATION_EVIDENCE),
        ),
        _edge(
            "mech0",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            (
                "The inherited mutation mechanism links this rpoC determinant "
                "class to the resistance phenotype."
            ),
            resistance_evidence,
        ),
        _edge(
            "determinant",
            "causally upstream of (confers resistance)",
            "RO:0002411",
            "resistance",
            "The local ARO definition states that rpoC mutations confer resistance.",
            resistance_evidence,
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
                    "The ARO hierarchy links this rpoC determinant to the "
                    f"{target.drug_relation_label} resistance class."
                ),
                (
                    target_evidence,
                    *target.inherited_resistance_evidence,
                    _drug_evidence(target),
                    MUTATION_EVIDENCE,
                ),
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
    graph["title"] = f"{record['label']} → rpoC mutation → resistance"
    graph["description"] = target.graph_description
    graph["edges"] = _canonical_edge_list(out, target)
    return out, out.get("causal_graphs") != before


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: record is not a mapping")
    identifier = record.get("identifier")
    target = TARGETS.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not an rpoC target: {identifier}")
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
        help="ARO directory or one of the seven target YAML files",
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
