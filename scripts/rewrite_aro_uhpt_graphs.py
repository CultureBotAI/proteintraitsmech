#!/usr/bin/env python3
"""Curate UhpT reduced-fosfomycin-import ARO graphs.

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

HISTORY_ACTION = "Curated UhpT fosfomycin-import graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

MUTATION_EVIDENCE = {
    "reference": "ARO:3000212",
    "snippet": (
        "Point mutations in the DNA may lead to an altered gene product that "
        "may result in antibiotic resistance."
    ),
    "notes": "CARD definition for mutation conferring antibiotic resistance.",
}

UHPT_PARENT_EVIDENCE = {
    "reference": "ARO:3004248",
    "snippet": (
        "UhpT encodes a transporter that can import fosfomycin-type drugs "
        "into bacterial cells. Mutations to UhpT confer resistance."
    ),
    "notes": "CARD definition for antibiotic-resistant UhpT.",
}

ECOLI_EVIDENCE = {
    "reference": "PMID:20071153",
    "snippet": (
        "Takahata et al. found uhpT loss together with truncated GlpT in "
        "clinical Escherichia coli fosfomycin-resistant isolates and measured "
        "blocked or reduced transporter-substrate uptake."
    ),
    "notes": "CARD-cited clinical evidence for Escherichia coli UhpT resistance.",
}

SAUR_EVIDENCE = {
    "reference": "PMID:28579984",
    "snippet": (
        "Xu et al. found that Staphylococcus aureus uhpT deletion increased "
        "fosfomycin MIC and that plasmid complementation restored fosfomycin "
        "susceptibility."
    ),
    "notes": "CARD-cited experimental evidence for Staphylococcus aureus UhpT resistance.",
}

PHOSPHONIC_RELATION_EVIDENCE = {
    "reference": "ARO:3004248",
    "snippet": "relationship: confers_resistance_to_drug_class ARO:3007149 ! phosphonic acid antibiotic",
    "notes": (
        "CARD asserts this phosphonic-acid drug-class relation on the "
        "antibiotic-resistant UhpT parent."
    ),
}

GO_TRANSMEMBRANE_TRANSPORT_EVIDENCE = {
    "reference": "GO:0055085",
    "snippet": (
        "The process in which a solute is transported across a lipid bilayer, "
        "from one side of a membrane to the other."
    ),
    "notes": "GO definition for broad transmembrane transport.",
}

RESISTANCE_NODE = {
    "node_id": "resistance",
    "label": "antibiotic resistance phenotype",
    "node_type": "PHENOTYPE",
    "grounding": "GO:0046677",
    "description": (
        "Fosfomycin resistance phenotype conferred by reduced UhpT-mediated "
        "drug import."
    ),
}

PHOSPHONIC_NODE = {
    "node_id": "drug0",
    "label": "phosphonic acid antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:3007149",
}

REDUCED_IMPORT_NODE = {
    "node_id": "reduced_import",
    "label": "reduced UhpT-mediated fosfomycin import",
    "node_type": "BIOLOGICAL_PROCESS",
    "grounding": "GO:0055085",
    "description": (
        "Grounded to broad GO transmembrane transport because UhpT-dependent "
        "fosfomycin import is transmembrane transport."
    ),
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    extra_evidence: tuple[dict[str, str], ...]


TARGETS: tuple[Target, ...] = (
    Target(
        "ARO:3004248",
        "antibiotic-resistant-uhpt-aro3004248.yaml",
        (ECOLI_EVIDENCE, SAUR_EVIDENCE),
    ),
    Target(
        "ARO:3003890",
        "escherichia-coli-uhpt-with-mutation-conferring-resistance-to-fosfomycin-aro3003890.yaml",
        (ECOLI_EVIDENCE,),
    ),
    Target(
        "ARO:3003902",
        "staphylococcus-aureus-uhpt-with-mutation-conferring-resistance-to-fosfomycin-aro3003902.yaml",
        (SAUR_EVIDENCE,),
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


def _unique_evidence(*items: dict[str, str]) -> list[dict[str, str]]:
    evidence: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in items:
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
    *evidence: dict[str, str],
) -> dict[str, Any]:
    return {
        "subject": subject,
        "predicate": predicate,
        "predicate_id": predicate_id,
        "object": object_,
        "description": description,
        "evidence": _unique_evidence(*evidence),
    }


def _record_evidence(record: dict[str, Any]) -> dict[str, str]:
    return {
        "reference": str(record["identifier"]),
        "snippet": str(record["definition"]),
        "notes": f"CARD definition for {record['label']}.",
    }


def _determinant_node(record: dict[str, Any]) -> dict[str, str]:
    return {
        "node_id": "determinant",
        "label": str(record["label"]),
        "node_type": "PROTEIN",
        "grounding": str(record["identifier"]),
    }


def _graph(record: dict[str, Any], target: Target) -> dict[str, Any]:
    record_evidence = _record_evidence(record)
    common_evidence = (
        record_evidence,
        UHPT_PARENT_EVIDENCE,
        MUTATION_EVIDENCE,
        *target.extra_evidence,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → reduced fosfomycin import",
        "description": (
            "Curated resistance-causation graph for UhpT mutations that impair "
            "fosfomycin import into bacterial cells."
        ),
        "nodes": [
            _determinant_node(record),
            {
                "node_id": "mech0",
                "label": "mutation conferring antibiotic resistance",
                "node_type": "MOLECULAR_FUNCTION",
                "grounding": "ARO:3000212",
            },
            copy.deepcopy(REDUCED_IMPORT_NODE),
            copy.deepcopy(PHOSPHONIC_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "CARD classifies UhpT-mediated fosfomycin resistance under "
                "mutation conferring antibiotic resistance.",
                *common_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of",
                "RO:0002411",
                "reduced_import",
                "Resistance mutations impair the UhpT transporter and reduce "
                "fosfomycin import.",
                *common_evidence,
                GO_TRANSMEMBRANE_TRANSPORT_EVIDENCE,
            ),
            _edge(
                "reduced_import",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Reduced UhpT-mediated import lowers intracellular fosfomycin "
                "exposure and confers resistance.",
                *common_evidence,
                GO_TRANSMEMBRANE_TRANSPORT_EVIDENCE,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "UhpT mutations confer the modeled fosfomycin-resistance "
                "phenotype by reducing drug import.",
                *common_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "UhpT determinants connect resistance-conferring mutations to "
                "reduced fosfomycin import.",
                *common_evidence,
            ),
            _edge(
                "determinant",
                "confers resistance to (drug class)",
                "ARO:2000001",
                "drug0",
                "CARD asserts that the UhpT lineage confers resistance to "
                "phosphonic acid antibiotics.",
                record_evidence,
                PHOSPHONIC_RELATION_EVIDENCE,
                *target.extra_evidence,
            ),
        ],
    }


def _validate_record(record: dict[str, Any], target: Target) -> None:
    if record.get("identifier") != target.identifier:
        raise ValueError(
            f"{target.filename}: expected {target.identifier}, "
            f"found {record.get('identifier')}"
        )
    if not record.get("label"):
        raise ValueError(f"{target.identifier}: missing label")
    if not record.get("definition"):
        raise ValueError(f"{target.identifier}: missing definition")

    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1:
        raise ValueError(f"{target.identifier}: expected exactly one causal graph")


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    _validate_record(record, target)

    out = copy.deepcopy(record)
    before = copy.deepcopy(out["causal_graphs"])
    out["mapping_status"] = "REVIEWED"
    out["causal_graphs"] = [_graph(record, target)]
    return out, out["causal_graphs"] != before or out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not a UhpT fosfomycin target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
    out = text.replace("mapping_status: SEEDED", "mapping_status: REVIEWED", 1)
    out = replace_block(out, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    if HISTORY_ACTION not in out:
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
        help="ARO directory or one UhpT fosfomycin YAML file",
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
