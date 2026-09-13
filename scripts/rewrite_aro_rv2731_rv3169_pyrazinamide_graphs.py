#!/usr/bin/env python3
"""Rewrite Rv2731/Rv3169 pyrazinamide-resistance causal graphs.

The antibiotic-resistant and pyrazinamide-resistant parent records are useful
ARO grouping terms but weak graph carriers.  Their species-specific
Mycobacterium tuberculosis children carry the direct pyrazinamide-resistance
mutation definitions and ARO evidence.

Dry-run by default; pass ``--apply`` to write.
"""

from __future__ import annotations

import argparse
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
HISTORY_TIMESTAMP = "2026-09-11T00:00:00Z"

MUTATION_EVIDENCE = {
    "reference": "ARO:3000212",
    "snippet": (
        "Point mutations in the DNA may lead to an altered gene product that may result in "
        "antibiotic resistance. Examples included modified antibiotic targets with lower binding "
        "affinities and the deactivation of repressors that result in increased expression of "
        "genes that inactivate or pump out antibiotics."
    ),
    "notes": "CARD definition for mutation conferring antibiotic resistance.",
}
PYRAZINE_EVIDENCE = {
    "reference": "ARO:3007155",
    "snippet": "pyrazine antibiotic",
    "notes": "CARD drug-class grounding for pyrazinamide.",
}
RESISTANCE_NODE = {
    "node_id": "resistance",
    "label": "antibiotic resistance phenotype",
    "node_type": "PHENOTYPE",
    "grounding": "GO:0046677",
    "description": (
        "Resistance phenotype conferred by this determinant. Grounded to the nearest available "
        "superclass: ARO models determinants and mechanisms but has no term for the resistance "
        "phenotype itself."
    ),
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    action: str

    @property
    def path(self) -> Path:
        return ARO_DIR / self.filename


@dataclass(frozen=True)
class Family:
    gene: str
    antibiotic_parent: Target
    pyrazinamide_parent: Target
    child: Target
    pyrazinamide_parent_definition: str


RV2731 = Family(
    gene="Rv2731",
    antibiotic_parent=Target(
        "ARO:3004985",
        "antibiotic-resistant-rv2731-aro3004985.yaml",
        (
            "Removed generic Rv2731 parent mutation draft after curating the M. tuberculosis "
            "pyrazinamide-specific graph"
        ),
    ),
    pyrazinamide_parent=Target(
        "ARO:3004986",
        "pyrazinamide-resistant-rv2731-aro3004986.yaml",
        (
            "Removed inherited Rv2731 pyrazinamide draft after curating the M. tuberculosis "
            "pyrazinamide-specific graph"
        ),
    ),
    child=Target(
        "ARO:3004987",
        "mycobacterium-tuberculosis-rv2731-mutations-confer-resistance-to-pyrazinamide-aro3004987.yaml",
        (
            "Completed M. tuberculosis Rv2731 pyrazinamide mutation causal graph; "
            "SEEDED -> REVIEWED"
        ),
    ),
    pyrazinamide_parent_definition=(
        "A conserved alanine and arginine-rich protein with an unknown function. The protein has "
        "shown to contribute to or confer resistance to pyrazinamide."
    ),
)
RV3169 = Family(
    gene="Rv3169",
    antibiotic_parent=Target(
        "ARO:3004991",
        "antibiotic-resistant-rv3169-aro3004991.yaml",
        (
            "Removed generic Rv3169 parent mutation draft after curating the M. tuberculosis "
            "pyrazinamide-specific graph"
        ),
    ),
    pyrazinamide_parent=Target(
        "ARO:3004992",
        "pyrazinamide-resistant-rv3169-aro3004992.yaml",
        (
            "Removed inherited Rv3169 pyrazinamide draft after curating the M. tuberculosis "
            "pyrazinamide-specific graph"
        ),
    ),
    child=Target(
        "ARO:3004993",
        "mycobacterium-tuberculosis-rv3169-mutations-confer-resistance-to-pyrazinamide-aro3004993.yaml",
        (
            "Completed M. tuberculosis Rv3169 pyrazinamide mutation causal graph; "
            "SEEDED -> REVIEWED"
        ),
    ),
    pyrazinamide_parent_definition=(
        "A conserved protein with an unknown function determined through proteomics study. May "
        "contribute or confer resistance to pyrazinamide resistance."
    ),
)
FAMILIES = (RV2731, RV3169)
PARENTS = tuple(target for family in FAMILIES for target in (
    family.antibiotic_parent,
    family.pyrazinamide_parent,
))
CHILDREN = tuple(family.child for family in FAMILIES)
TARGETS = (*PARENTS, *CHILDREN)

_TOP_KEY = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*:")
_MAPPING_STATUS = re.compile(r"^mapping_status:[ \t]*(.+?)[ \t]*$", re.M)


def _dump(obj: Any) -> str:
    return yaml.safe_dump(obj, sort_keys=False, allow_unicode=True, width=100)


def _remove_block(text: str, key: str) -> str:
    lines = text.splitlines(keepends=True)
    start = next((i for i, line in enumerate(lines) if line.startswith(f"{key}:")), None)
    if start is None:
        return text

    end = start + 1
    while end < len(lines) and not (lines[end].strip() and _TOP_KEY.match(lines[end])):
        end += 1
    return "".join(lines[:start]) + "".join(lines[end:])


def _set_mapping_status(text: str, status: str) -> str:
    out, count = _MAPPING_STATUS.subn(f"mapping_status: {status}", text, count=1)
    if count != 1:
        raise ValueError("expected exactly one top-level mapping_status")
    return out


def _history_event(target: Target) -> dict[str, Any]:
    return {
        "timestamp": HISTORY_TIMESTAMP,
        "curator": HISTORY_CURATOR,
        "action": target.action,
        "llm_assisted": True,
    }


def _has_history_action(text: str, action: str) -> bool:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        return False
    history = record.get("curation_history")
    if not isinstance(history, list):
        return False
    return any(isinstance(event, dict) and event.get("action") == action for event in history)


def _append_history_once(text: str, target: Target) -> str:
    if _has_history_action(text, target.action):
        return text
    return append_to_section(
        text,
        "curation_history",
        _dump({"curation_history": [_history_event(target)]}),
    )


def _record_evidence(record: dict[str, Any]) -> dict[str, str]:
    return {
        "reference": str(record["identifier"]),
        "snippet": str(record["definition"]),
        "notes": f"CARD definition for {record['label']}.",
    }


def _parent_definition_evidence(family: Family) -> dict[str, str]:
    return {
        "reference": family.pyrazinamide_parent.identifier,
        "snippet": family.pyrazinamide_parent_definition,
        "notes": f"CARD definition for pyrazinamide resistant {family.gene}.",
    }


def _drug_relation_evidence(family: Family) -> dict[str, str]:
    return {
        "reference": family.pyrazinamide_parent.identifier,
        "snippet": "relationship: confers_resistance_to_drug_class ARO:3007155 ! pyrazine antibiotic",
        "notes": (
            f"CARD asserts a pyrazine-antibiotic resistance relation on pyrazinamide resistant "
            f"{family.gene}."
        ),
    }


def _unique_evidence(*items: dict[str, str]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in items:
        if item["reference"] in seen:
            continue
        seen.add(item["reference"])
        out.append(dict(item))
    return out


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


def _graph(record: dict[str, Any], family: Family) -> dict[str, Any]:
    record_evidence = _record_evidence(record)
    parent_definition_evidence = _parent_definition_evidence(family)
    return {
        "graph_id": "resistance",
        "title": f"M. tuberculosis {family.gene} mutations → pyrazinamide resistance",
        "description": (
            f"Curated {family.gene} pyrazinamide-resistance graph. CARD assigns this determinant "
            "to the broad mutation-conferring mechanism and links it to the pyrazine-antibiotic "
            f"class through its pyrazinamide-resistant {family.gene} parent. No more specific "
            "molecular function is asserted by the local CARD-derived record, so this graph keeps "
            "the causal model at the mutation and phenotype levels."
        ),
        "nodes": [
            {
                "node_id": "determinant",
                "label": str(record["label"]),
                "node_type": "PROTEIN",
                "grounding": str(record["identifier"]),
            },
            {
                "node_id": "mutation",
                "label": "mutation conferring antibiotic resistance",
                "node_type": "MOLECULAR_FUNCTION",
                "grounding": "ARO:3000212",
            },
            {
                "node_id": "drug0",
                "label": "pyrazine antibiotic",
                "node_type": "CHEMICAL",
                "grounding": "ARO:3007155",
            },
            dict(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mutation",
                (
                    f"CARD classifies {family.gene} pyrazinamide-resistance variants under the "
                    "broad mutation-conferring antibiotic-resistance mechanism."
                ),
                record_evidence,
                MUTATION_EVIDENCE,
            ),
            _edge(
                "mutation",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                (
                    "CARD's mutation-conferring mechanism links point mutations to altered gene "
                    f"products that can cause antibiotic resistance, and the M. tuberculosis "
                    f"{family.gene} record states that these mutations can contribute to or "
                    "confer pyrazinamide resistance."
                ),
                MUTATION_EVIDENCE,
                record_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                (
                    f"CARD states that {family.gene} mutations can contribute to or confer "
                    "pyrazinamide resistance."
                ),
                record_evidence,
                parent_definition_evidence,
            ),
            _edge(
                "determinant",
                "confers resistance to (drug class)",
                "ARO:2000001",
                "drug0",
                (
                    "CARD asserts a pyrazine-antibiotic resistance relation on the pyrazinamide "
                    f"resistant {family.gene} parent and this M. tuberculosis variant inherits "
                    "that relation."
                ),
                _drug_relation_evidence(family),
                PYRAZINE_EVIDENCE,
            ),
        ],
    }


def _require_identifier(text: str, target: Target, path: Path) -> dict[str, Any]:
    record = yaml.safe_load(text)
    found = record.get("identifier") if isinstance(record, dict) else None
    if found != target.identifier:
        raise ValueError(f"{path}: expected {target.identifier}, found {found}")
    return record


def _family_by_child(target: Target) -> Family:
    for family in FAMILIES:
        if family.child == target:
            return family
    raise KeyError(target)


def repair_parent_text(text: str, target: Target, path: Path | None = None) -> tuple[str, bool]:
    _require_identifier(text, target, path or target.path)
    out = _remove_block(text, "causal_graphs")
    out = _append_history_once(out, target)
    return out, out != text


def curate_child_text(text: str, target: Target, path: Path | None = None) -> tuple[str, bool]:
    record = _require_identifier(text, target, path or target.path)
    family = _family_by_child(target)
    out = _set_mapping_status(text, "REVIEWED")
    out = replace_block(out, "causal_graphs", _dump({"causal_graphs": [_graph(record, family)]}))
    out = _append_history_once(out, target)
    return out, out != text


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    for target in PARENTS:
        if path.name == target.filename:
            return repair_parent_text(text, target, path)
    for target in CHILDREN:
        if path.name == target.filename:
            return curate_child_text(text, target, path)
    return text, False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write the rewrite")
    args = parser.parse_args(argv)

    for target in TARGETS:
        text = target.path.read_text(encoding="utf-8")
        out, changed = enrich_text(text, target.path)
        if not changed:
            print(f"unchanged {target.path.relative_to(ROOT)}")
            continue
        if args.apply:
            target.path.write_text(out, encoding="utf-8")
            print(f"rewrote {target.path.relative_to(ROOT)}")
        else:
            print(f"would rewrite {target.path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
