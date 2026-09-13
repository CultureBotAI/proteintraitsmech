#!/usr/bin/env python3
"""Rewrite safe broad SEEDED ARO parent-stub graphs.

These parent records assert one high-level mechanism but do not name one
specific enzyme, pump complex, or modified target.  A conservative three-edge
graph is enough: determinant class -> CARD mechanism -> resistance.

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

HISTORY_ACTION = "Completed broad ARO parent-stub resistance graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-09T00:00:00Z",
    "curator": "codex-causal-graph-quality",
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
    "notes": "CARD definition for the mutation-conferring-antibiotic-resistance mechanism.",
}

EFFLUX_EVIDENCE = {
    "reference": "ARO:0010000",
    "snippet": "Antibiotic resistance via the transport of antibiotics out of the cell.",
    "notes": "CARD definition for the antibiotic efflux mechanism.",
}

EFFLUX_PUMP_EVIDENCE = {
    "reference": "ARO:3000159",
    "snippet": "Efflux proteins that pump antibiotic out of a cell to confer resistance.",
    "notes": "CARD definition for efflux pump complexes and subunits.",
}

CHARGE_ALTERATION_EVIDENCE = {
    "reference": "ARO:3003588",
    "snippet": (
        "The loss or reduction of the net negative charge within the cell wall of "
        "gram negative bacteria is a mechanism of resistance for cationic "
        "antimicrobials that depend on the negative charge for binding to the surface."
    ),
    "notes": "CARD definition for charge alteration conferring antibiotic resistance.",
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    label: str
    mechanism_label: str
    mechanism_grounding: str
    own_evidence: dict[str, str]
    mechanism_evidence: dict[str, str]
    mechanism_description: str
    determinant_description: str
    extra_evidence: tuple[dict[str, str], ...] = ()


TARGETS: tuple[Target, ...] = (
    Target(
        identifier="ARO:0000031",
        filename="antibiotic-resistant-gene-variant-or-mutant-aro0000031.yaml",
        label="antibiotic resistant gene variant or mutant",
        mechanism_label="mutation conferring antibiotic resistance",
        mechanism_grounding="ARO:3000212",
        own_evidence={
            "reference": "ARO:0000031",
            "snippet": (
                "Resistance to antibiotics is often conferred by single nucleotide "
                "polymorphisms (SNPs) and other mutations in target genes."
            ),
            "notes": "CARD definition for the antibiotic-resistant gene-variant class.",
        },
        mechanism_evidence=MUTATION_EVIDENCE,
        mechanism_description=(
            "CARD places this parent determinant class under mutations that confer "
            "antibiotic resistance."
        ),
        determinant_description=(
            "The broad parent represents resistance-conferring variants or mutants; "
            "child terms carry the specific mutated genes."
        ),
    ),
    Target(
        identifier="ARO:3000159",
        filename="efflux-pump-complex-or-subunit-conferring-antibiotic-resistance-aro3000159.yaml",
        label="efflux pump complex or subunit conferring antibiotic resistance",
        mechanism_label="antibiotic efflux",
        mechanism_grounding="ARO:0010000",
        own_evidence=EFFLUX_PUMP_EVIDENCE,
        mechanism_evidence=EFFLUX_EVIDENCE,
        mechanism_description=(
            "CARD defines this parent class as efflux proteins that transport antibiotic "
            "out of the cell."
        ),
        determinant_description=(
            "The broad parent covers whole efflux complexes and single efflux subunits; "
            "subfamily records carry pump-class and complex-specific details."
        ),
    ),
    Target(
        identifier="ARO:3000748",
        filename="subunit-of-efflux-pump-conferring-antibiotic-resistance-aro3000748.yaml",
        label="subunit of efflux pump conferring antibiotic resistance",
        mechanism_label="antibiotic efflux",
        mechanism_grounding="ARO:0010000",
        own_evidence={
            "reference": "ARO:3000748",
            "snippet": (
                "Subunits of efflux proteins that pump antibiotic out of a cell to "
                "confer resistance."
            ),
            "notes": "CARD definition for efflux-pump subunits.",
        },
        mechanism_evidence=EFFLUX_EVIDENCE,
        mechanism_description=(
            "CARD classifies this subunit parent under the broad antibiotic-efflux "
            "resistance mechanism."
        ),
        determinant_description=(
            "The broad parent represents subunits of antibiotic efflux pumps; the graph "
            "stops at generic antibiotic efflux because exact complexes are curated on "
            "child records."
        ),
        extra_evidence=(EFFLUX_PUMP_EVIDENCE,),
    ),
    Target(
        identifier="ARO:3003580",
        filename="gene-altering-cell-wall-charge-aro3003580.yaml",
        label="gene altering cell wall charge",
        mechanism_label="charge alteration conferring antibiotic resistance",
        mechanism_grounding="ARO:3003588",
        own_evidence={
            "reference": "ARO:3003580",
            "snippet": (
                "Genes involved in alteration of the cell wall overall charge, leading "
                "to antimicrobial resistance due to reduced binding."
            ),
            "notes": "CARD definition for determinants that alter cell-wall charge.",
        },
        mechanism_evidence=CHARGE_ALTERATION_EVIDENCE,
        mechanism_description=(
            "CARD classifies this parent under charge alteration conferring antibiotic "
            "resistance."
        ),
        determinant_description=(
            "The broad parent groups determinants that alter bacterial envelope charge; "
            "child records carry the specific chemistry."
        ),
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


def _ev(evidence: dict[str, str]) -> dict[str, str]:
    return copy.deepcopy(evidence)


def _nodes(target: Target) -> list[dict[str, str]]:
    return [
        {
            "node_id": "determinant",
            "label": target.label,
            "node_type": "PROTEIN",
            "grounding": target.identifier,
            "description": target.determinant_description,
        },
        {
            "node_id": "mech0",
            "label": target.mechanism_label,
            "node_type": "MOLECULAR_FUNCTION",
            "grounding": target.mechanism_grounding,
            "description": (
                "High-level CARD resistance-mechanism class for this parent record."
            ),
        },
        {
            "node_id": "resistance",
            "label": "antibiotic resistance phenotype",
            "node_type": "PHENOTYPE",
            "grounding": "GO:0046677",
            "description": (
                "Resistance phenotype conferred by this determinant. Grounded to the "
                "nearest available superclass: ARO models determinants and mechanisms "
                "but has no term for the resistance phenotype itself."
            ),
        },
    ]


def _edges(target: Target) -> list[dict[str, Any]]:
    def evidence(*items: dict[str, str]) -> list[dict[str, str]]:
        return [_ev(item) for item in items]

    return [
        {
            "subject": "determinant",
            "predicate": "participates in (resistance mechanism)",
            "predicate_id": "RO:0000056",
            "object": "mech0",
            "description": target.mechanism_description,
            "evidence": evidence(
                target.own_evidence,
                target.mechanism_evidence,
                *target.extra_evidence,
            ),
        },
        {
            "subject": "mech0",
            "predicate": "causally upstream of",
            "predicate_id": "RO:0002411",
            "object": "resistance",
            "description": (
                "The CARD mechanism class is the high-level causal route from this "
                "broad determinant parent to antibiotic resistance."
            ),
            "evidence": evidence(
                target.mechanism_evidence,
                target.own_evidence,
                *target.extra_evidence,
            ),
        },
        {
            "subject": "determinant",
            "predicate": "causally upstream of (confers resistance)",
            "predicate_id": "RO:0002411",
            "object": "resistance",
            "description": (
                "The determinant class confers resistance through the grounded CARD "
                "mechanism without specifying one child-level chemistry or target."
            ),
            "evidence": evidence(
                target.own_evidence,
                target.mechanism_evidence,
                *target.extra_evidence,
            ),
        },
    ]


def _graph(target: Target) -> dict[str, Any]:
    return {
        "graph_id": "resistance",
        "title": f"{target.label} → {target.mechanism_label} → resistance",
        "description": (
            "Curated broad-parent resistance graph. The graph intentionally stops at a "
            "single grounded CARD mechanism because this parent record does not assert "
            "one specific child chemistry, pump, or altered target."
        ),
        "nodes": _nodes(target),
        "edges": _edges(target),
    }


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    before = _dump(record)
    record["mapping_status"] = "REVIEWED"
    record["causal_graphs"] = [_graph(target)]
    return record, _dump(record) != before


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not a broad parent-stub target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
    out = text
    out = replace_block(out, "mapping_status", _dump({"mapping_status": enriched["mapping_status"]}))
    out = replace_block(out, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    if HISTORY_ACTION not in out:
        out = append_to_section(out, "curation_history", _dump({"curation_history": [HISTORY_EVENT]}))
        changed = True

    if "&id" in out or "*id" in out:
        raise ValueError(f"{path}: YAML anchors leaked into output")
    return out, changed


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
        help="ARO directory or one of the broad parent-stub target YAML files",
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
