#!/usr/bin/env python3
"""Rewrite SmeR/S two-component antibiotic-efflux regulator graphs.

The SmeR and SmeS leaf records already used the right conservative model:
these regulators do not efflux drugs themselves; they participate in a
two-component system that changes antibiotic-efflux rates.  This updater
fills in the sparse evidence and applies the same model to the SmeRS system
record.

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

HISTORY_ACTION = "Completed SmeR/S efflux-regulatory graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-09T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

REGULATORY_EFFLUX_EVIDENCE = {
    "reference": "ARO:3000451",
    "snippet": (
        "Protein(s) and two component regulatory systems that directly or indirectly "
        "change rates of antibiotic efflux."
    ),
    "notes": (
        "CARD definition for proteins and two-component systems that modulate antibiotic "
        "efflux; this licenses regulation of efflux without asserting that the regulator "
        "is itself a pump."
    ),
}

TCS_PROTEIN_EVIDENCE = {
    "reference": "ARO:3000750",
    "snippet": (
        "A protein, either a histidine kinase or a response regulator, that is part of a "
        "two-component regulatory system that directly or indirectly change rates of "
        "antibiotic efflux."
    ),
    "notes": (
        "CARD definition for response regulators and sensor kinases in two-component "
        "systems that modulate antibiotic efflux."
    ),
}

ANTIBIOTIC_EFFLUX_EVIDENCE = {
    "reference": "ARO:0010000",
    "snippet": "Antibiotic resistance via the transport of antibiotics out of the cell.",
    "notes": "CARD definition for the antibiotic efflux resistance mechanism.",
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    label: str
    role_description: str
    determinant_evidence: dict[str, str]
    role_evidence: dict[str, str]
    determinant_is_system: bool = False


TARGETS: tuple[Target, ...] = (
    Target(
        identifier="ARO:3003066",
        filename="smer-aro3003066.yaml",
        label="smeR",
        role_description=(
            "SmeR is the response-regulator component of the SmeR/SmeS two-component "
            "system, so the graph uses participates-in rather than enables."
        ),
        determinant_evidence={
            "reference": "ARO:3003066",
            "snippet": (
                "smeR is the responder component of a two component signal transduction "
                "system that includes smeS."
            ),
            "notes": "CARD definition identifying SmeR as the responder of the SmeRS pair.",
        },
        role_evidence=TCS_PROTEIN_EVIDENCE,
    ),
    Target(
        identifier="ARO:3003067",
        filename="smes-aro3003067.yaml",
        label="smeS",
        role_description=(
            "SmeS is the sensor-kinase component of the SmeR/SmeS two-component system, "
            "so the graph uses participates-in rather than enables."
        ),
        determinant_evidence={
            "reference": "ARO:3003067",
            "snippet": (
                "smeS is the protein kinase sensor component of a two component signal "
                "transduction system that includes smeR."
            ),
            "notes": "CARD definition identifying SmeS as the sensor kinase of the SmeRS pair.",
        },
        role_evidence=TCS_PROTEIN_EVIDENCE,
    ),
    Target(
        identifier="ARO:3003068",
        filename="smers-aro3003068.yaml",
        label="smeRS",
        role_description=(
            "SmeRS is the SmeR/SmeS two-component regulatory system for SmeABC."
        ),
        determinant_evidence={
            "reference": "ARO:3003068",
            "snippet": (
                "smeRS is a two component regulatory system for smeABC where smeR is a "
                "response regulator, while smeS is a sensor kinase."
            ),
            "notes": (
                "CARD definition identifying SmeRS as the two-component regulatory system "
                "made from SmeR and SmeS."
            ),
        },
        role_evidence=REGULATORY_EFFLUX_EVIDENCE,
        determinant_is_system=True,
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


def _resistance_node() -> dict[str, str]:
    return {
        "node_id": "resistance",
        "label": "antibiotic resistance phenotype",
        "node_type": "PHENOTYPE",
        "grounding": "GO:0046677",
        "description": (
            "Resistance phenotype conferred by this determinant. Grounded to the "
            "nearest available superclass: ARO models determinants and mechanisms but "
            "has no term for the resistance phenotype itself."
        ),
    }


def _nodes(target: Target) -> list[dict[str, str]]:
    return [
        {
            "node_id": "determinant",
            "label": target.label,
            "node_type": "PROTEIN",
            "grounding": target.identifier,
        },
        {
            "node_id": "mech0",
            "label": "antibiotic efflux",
            "node_type": "MOLECULAR_FUNCTION",
            "grounding": "ARO:0010000",
            "description": (
                "Inherited ARO mechanism class. The graph expands this role through "
                "regulatory signal transduction rather than treating SmeRS as a pump."
            ),
        },
        {
            "node_id": "signalling",
            "label": "two-component signal transduction",
            "node_type": "BIOLOGICAL_PROCESS",
            "grounding": "GO:0000160",
            "description": "Checked non-obsolete against OLS (#157).",
        },
        {
            "node_id": "efflux_process",
            "label": "antibiotic efflux",
            "node_type": "BIOLOGICAL_PROCESS",
            "grounding": "ARO:0010000",
            "description": (
                "Downstream efflux process whose pump chemistry is curated on pump "
                "records, not on the regulatory-system record."
            ),
        },
        _resistance_node(),
    ]


def _edges(target: Target) -> list[dict[str, Any]]:
    def ev(evidence: dict[str, str]) -> dict[str, str]:
        return copy.deepcopy(evidence)

    determinant_mechanism_evidence = [target.role_evidence, REGULATORY_EFFLUX_EVIDENCE]
    signalling_efflux_evidence = [target.role_evidence, REGULATORY_EFFLUX_EVIDENCE]
    if target.determinant_is_system:
        determinant_mechanism_evidence = [
            target.determinant_evidence,
            REGULATORY_EFFLUX_EVIDENCE,
        ]
        signalling_efflux_evidence = [
            target.determinant_evidence,
            REGULATORY_EFFLUX_EVIDENCE,
        ]

    determinant_to_signalling_predicate = (
        "participates in (two-component signal transduction)"
        if not target.determinant_is_system
        else "enables (two-component signal transduction)"
    )
    determinant_to_signalling_predicate_id = (
        "RO:0000056" if not target.determinant_is_system else "RO:0002327"
    )

    return [
        {
            "subject": "determinant",
            "predicate": "participates in (resistance mechanism)",
            "predicate_id": "RO:0000056",
            "object": "mech0",
            "description": (
                "CARD places this determinant in the antibiotic-efflux resistance "
                "mechanism via efflux regulation."
            ),
            "evidence": [ev(item) for item in determinant_mechanism_evidence],
        },
        {
            "subject": "mech0",
            "predicate": "causally upstream of",
            "predicate_id": "RO:0002411",
            "object": "resistance",
            "description": (
                "The inherited ARO mechanism is antibiotic efflux; the downstream efflux "
                "process confers resistance by transporting antibiotics out of the cell."
            ),
            "evidence": [ev(REGULATORY_EFFLUX_EVIDENCE), ev(ANTIBIOTIC_EFFLUX_EVIDENCE)],
        },
        {
            "subject": "determinant",
            "predicate": "causally upstream of (confers resistance)",
            "predicate_id": "RO:0002411",
            "object": "resistance",
            "description": (
                "The determinant participates in a two-component regulatory route that "
                "changes efflux rates and thereby contributes to antibiotic resistance."
            ),
            "evidence": [
                ev(target.determinant_evidence),
                ev(REGULATORY_EFFLUX_EVIDENCE),
                ev(ANTIBIOTIC_EFFLUX_EVIDENCE),
            ],
        },
        {
            "subject": "determinant",
            "predicate": determinant_to_signalling_predicate,
            "predicate_id": determinant_to_signalling_predicate_id,
            "object": "signalling",
            "description": target.role_description,
            "evidence": [ev(target.determinant_evidence), ev(target.role_evidence)],
        },
        {
            "subject": "signalling",
            "predicate": "regulates (changes efflux rates, directly or indirectly)",
            "predicate_id": "RO:0002211",
            "object": "efflux_process",
            "description": (
                "The parent evidence says two-component systems directly or indirectly "
                "change efflux rates, so this graph uses broad regulation rather than "
                "positive or direct regulation."
            ),
            "evidence": [ev(item) for item in signalling_efflux_evidence],
        },
        {
            "subject": "efflux_process",
            "predicate": "causally upstream of (confers resistance)",
            "predicate_id": "RO:0002411",
            "object": "resistance",
            "description": (
                "Transporting antibiotics out of the cell is the terminal modeled cause "
                "of resistance in this regulatory graph."
            ),
            "evidence": [ev(ANTIBIOTIC_EFFLUX_EVIDENCE), ev(REGULATORY_EFFLUX_EVIDENCE)],
        },
    ]


def _graph(target: Target) -> dict[str, Any]:
    return {
        "graph_id": "resistance",
        "title": f"{target.label} → two-component regulation of antibiotic efflux → resistance",
        "description": (
            "Curated resistance-causation graph for a two-component system that "
            "regulates antibiotic efflux. The graph stops at the efflux process; pump "
            "chemistry lives on the pump records."
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
        raise ValueError(f"{path}: not an SmeR/S target: {identifier}")
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
        help="ARO directory or one of the SmeR/S target YAML files",
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
