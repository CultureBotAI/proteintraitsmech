#!/usr/bin/env python3
"""Rewrite BRP and generic antibiotic-sequestration ARO causal graphs.

These records all model antibiotic sequestration: a resistance protein binds an
antibiotic into a determinant-drug complex and prevents target interaction.  The
generic ARO:3001207 parent is kept drug-agnostic; bleomycin-resistance protein
records keep the inherited glycopeptide drug class and explicitly model BRP-drug
complex formation.

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
HISTORY_ACTION = "Curated antibiotic-sequestration and BRP graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-11T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

INACTIVATION_EVIDENCE = {
    "reference": "ARO:0001004",
    "snippet": "Direct inactivation of the antibiotic by the resistance gene product.",
    "notes": "CARD definition for broad antibiotic inactivation.",
}

SEQUESTRATION_EVIDENCE = {
    "reference": "ARO:3001206",
    "snippet": "Inactivation of an antibiotic through direct binding by a resistance protein.",
    "notes": "CARD definition for antibiotic inactivation by sequestration.",
}

GENERIC_EVIDENCE = {
    "reference": "ARO:3001207",
    "snippet": (
        "A gene product inactivates an antibiotic by forming a complex that "
        "prevents interaction with the antibiotic target."
    ),
    "notes": "CARD definition for the antibiotic-sequestration determinant parent.",
}

BRP_EVIDENCE = {
    "reference": "ARO:3004256",
    "snippet": "Bleomycin resistant proteins confer resistance to bleomycin-like molecules.",
    "notes": "CARD definition for the bleomycin-resistant-protein parent.",
}

BRP_MBL_EVIDENCE = {
    "reference": "ARO:3001205",
    "snippet": (
        "BRP(MBL) expression confers resistance to bleomycin and bleomycin-like "
        "antibiotics."
    ),
    "notes": "CARD definition for BRP(MBL).",
}

BRP_MBL_PUBMED_EVIDENCE = {
    "reference": "DOI:10.1128/AAC.02413-16",
    "snippet": "BRP(MBL) is a metallo-beta-lactamase-associated bleomycin resistance protein.",
    "notes": "Dortet et al. characterized BRP(MBL) as a bleomycin-resistance protein.",
}

BLMT_COMPLEX_EVIDENCE = {
    "reference": "PMID:11134052",
    "snippet": (
        "Crystal structures of the Tn5-carried bleomycin resistance determinant "
        "were solved uncomplexed and complexed with bleomycin."
    ),
    "notes": (
        "A structurally characterized bleomycin-resistance protein supports "
        "direct BRP-drug binding as a sequestration mechanism."
    ),
}

GLYCOPEPTIDE_EVIDENCE = {
    "reference": "ARO:3000081",
    "snippet": "glycopeptide antibiotic",
    "notes": "ARO drug-class term inherited by bleomycin-resistance protein records.",
}

RESISTANCE_NODE = {
    "node_id": "resistance",
    "label": "antibiotic resistance phenotype",
    "node_type": "PHENOTYPE",
    "grounding": "GO:0046677",
    "description": (
        "Resistance phenotype conferred by this determinant. Grounded to the nearest "
        "available superclass: ARO models determinants and mechanisms but has no "
        "term for the resistance phenotype itself."
    ),
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    determinant_evidence: dict[str, str]
    parent_evidence: dict[str, str]
    with_drug: bool
    publication_evidence: dict[str, str] | None = None


TARGETS: tuple[Target, ...] = (
    Target(
        "ARO:3001207",
        "gene-involved-in-antibiotic-sequestration-aro3001207.yaml",
        GENERIC_EVIDENCE,
        GENERIC_EVIDENCE,
        False,
    ),
    Target(
        "ARO:3004256",
        "bleomycin-resistant-protein-aro3004256.yaml",
        BRP_EVIDENCE,
        GENERIC_EVIDENCE,
        True,
        BLMT_COMPLEX_EVIDENCE,
    ),
    Target(
        "ARO:3001205",
        "brp-mbl-aro3001205.yaml",
        BRP_MBL_EVIDENCE,
        BRP_EVIDENCE,
        True,
        BRP_MBL_PUBMED_EVIDENCE,
    ),
)

TARGET_BY_ID = {target.identifier: target for target in TARGETS}


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


def _unique_evidence(*items: dict[str, str] | None) -> list[dict[str, str]]:
    evidence: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in items:
        if item is None:
            continue
        reference = item["reference"]
        if reference in seen:
            continue
        seen.add(reference)
        evidence.append(copy.deepcopy(item))
    return evidence


def _edge(
    subject: str,
    predicate: str,
    predicate_id: str,
    object_: str,
    description: str,
    *evidence: dict[str, str] | None,
) -> dict[str, Any]:
    return {
        "subject": subject,
        "predicate": predicate,
        "predicate_id": predicate_id,
        "object": object_,
        "description": description,
        "evidence": _unique_evidence(*evidence),
    }


def _base_nodes(record: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "node_id": "determinant",
            "label": str(record["label"]),
            "node_type": "PROTEIN",
            "grounding": str(record["identifier"]),
        },
        {
            "node_id": "mech0",
            "label": "antibiotic inactivation",
            "node_type": "MOLECULAR_FUNCTION",
            "grounding": "ARO:0001004",
        },
        {
            "node_id": "mech1",
            "label": "antibiotic inactivation by sequestration",
            "node_type": "MOLECULAR_FUNCTION",
            "grounding": "ARO:3001206",
        },
        {
            "node_id": "complex",
            "label": "determinant-antibiotic sequestration complex",
            "node_type": "STATE",
            "description": (
                "Local state for a resistance determinant bound to the antibiotic "
                "that it sequesters."
            ),
        },
        copy.deepcopy(RESISTANCE_NODE),
    ]


def _drug_node() -> dict[str, Any]:
    return {
        "node_id": "drug0",
        "label": "bleomycin-family glycopeptide antibiotic",
        "node_type": "CHEMICAL",
        "grounding": "ARO:3000081",
        "description": (
            "Grounded to CARD's broad glycopeptide-antibiotic drug class because "
            "the ARO relation uses that term for bleomycin-like antibiotics."
        ),
    }


def _base_edges(target: Target) -> list[dict[str, Any]]:
    evidence = (
        target.determinant_evidence,
        target.parent_evidence,
        target.publication_evidence,
        SEQUESTRATION_EVIDENCE,
    )
    return [
        _edge(
            "determinant",
            "participates in (resistance mechanism)",
            "RO:0000056",
            "mech0",
            "Antibiotic sequestration is modeled under the broad antibiotic "
            "inactivation mechanism.",
            target.determinant_evidence,
            INACTIVATION_EVIDENCE,
        ),
        _edge(
            "mech0",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            "Drug sequestration inactivates the antibiotic by preventing it from "
            "interacting with its target.",
            *evidence,
            INACTIVATION_EVIDENCE,
        ),
        _edge(
            "determinant",
            "participates in (resistance mechanism)",
            "RO:0000056",
            "mech1",
            "The determinant participates in antibiotic inactivation by "
            "sequestration.",
            *evidence,
        ),
        _edge(
            "mech1",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            "Antibiotic sequestration prevents target interaction and thereby "
            "confers resistance.",
            *evidence,
        ),
        _edge(
            "determinant",
            "causally upstream of (confers resistance)",
            "RO:0002411",
            "resistance",
            "The determinant confers resistance by sequestering the antibiotic in "
            "a determinant-drug complex.",
            *evidence,
        ),
        _edge(
            "determinant",
            "causally upstream of (forms sequestration complex)",
            "RO:0002411",
            "complex",
            "Binding by the determinant forms the antibiotic-sequestration complex.",
            *evidence,
        ),
        _edge(
            "complex",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            "The determinant-antibiotic complex sequesters the drug and prevents "
            "target interaction.",
            *evidence,
        ),
        _edge(
            "complex",
            "has part",
            "BFO:0000051",
            "determinant",
            "The sequestration complex contains the determinant protein.",
            *evidence,
        ),
    ]


def _graph(record: dict[str, Any], target: Target) -> dict[str, Any]:
    nodes = _base_nodes(record)
    edges = _base_edges(target)
    if target.with_drug:
        nodes.append(_drug_node())
        edges.extend(
            [
                _edge(
                    "determinant",
                    "confers resistance to (drug class)",
                    "ARO:2000001",
                    "drug0",
                    "CARD asserts glycopeptide resistance for this "
                    "bleomycin-resistance protein record.",
                    target.determinant_evidence,
                    GLYCOPEPTIDE_EVIDENCE,
                ),
                _edge(
                    "determinant",
                    "molecularly interacts with (binds the drug)",
                    "RO:0002436",
                    "drug0",
                    "Bleomycin-resistance proteins bind bleomycin-like drugs as "
                    "the sequestration mechanism.",
                    target.determinant_evidence,
                    target.publication_evidence,
                    BLMT_COMPLEX_EVIDENCE,
                ),
                _edge(
                    "complex",
                    "has part",
                    "BFO:0000051",
                    "drug0",
                    "The sequestration complex contains the bound "
                    "bleomycin-family drug.",
                    target.determinant_evidence,
                    target.publication_evidence,
                    BLMT_COMPLEX_EVIDENCE,
                    GLYCOPEPTIDE_EVIDENCE,
                ),
            ]
        )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → antibiotic sequestration → resistance",
        "description": (
            "Curated resistance-causation graph for an antibiotic-sequestration "
            "determinant. The graph models direct drug binding into a "
            "determinant-antibiotic complex as the event that prevents the "
            "antibiotic from interacting with its target."
        ),
        "nodes": nodes,
        "edges": edges,
    }


def _validate_record(record: dict[str, Any], target: Target) -> None:
    if record.get("identifier") != target.identifier:
        raise ValueError(
            f"{target.filename}: expected {target.identifier}, "
            f"found {record.get('identifier')}"
        )
    if not record.get("label"):
        raise ValueError(f"{target.identifier}: missing label")

    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1 or graphs[0].get("graph_id") not in {"resistance", "resistance-draft"}:
        raise ValueError(f"{target.identifier}: expected exactly one resistance graph")

    node_ids = {
        str(node.get("node_id"))
        for node in _dicts(graphs[0].get("nodes"))
        if node.get("node_id")
    }
    missing_nodes = {"determinant", "mech0", "resistance"} - node_ids
    if missing_nodes:
        missing = ", ".join(sorted(missing_nodes))
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    _validate_record(record, target)

    out = copy.deepcopy(record)
    out["mapping_status"] = "REVIEWED"
    out["causal_graphs"] = [_graph(record, target)]
    return out, out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not an antibiotic-sequestration target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
    out = text.replace("mapping_status: SEEDED", "mapping_status: REVIEWED", 1)
    out = replace_block(out, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    if HISTORY_CURATOR not in out:
        out = append_to_section(out, "curation_history", _dump({"curation_history": [HISTORY_EVENT]}))
        changed = True

    if "&id" in out or "*id" in out:
        raise ValueError(f"{path}: YAML anchors leaked into output")
    return out, changed or out != text


def iter_target_paths(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if not path.is_dir():
        raise ValueError(f"{path} is neither a file nor a directory")
    return [path / target.filename for target in TARGETS]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    parser.add_argument(
        "--path",
        type=Path,
        default=ARO_DIR,
        help="ARO directory or one of the antibiotic-sequestration YAML files",
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
