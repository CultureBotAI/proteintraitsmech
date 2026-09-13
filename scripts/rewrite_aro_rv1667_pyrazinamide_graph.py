#!/usr/bin/env python3
"""Rewrite the CARD Rv1667 pyrazinamide-resistance causal graph.

The two broader Rv1667 parents are useful ARO grouping records but weak graph
carriers: the antibiotic parent names no drug, and the pyrazinamide parent
mentions a probable mycobacterial transporter for macrolide export.  The
Mycobacterium tuberculosis child has the direct pyrazinamide-resistance
definition and the CARD-cited Zhang et al. 2017 paper on Rv1667c efflux.

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

ANTIBIOTIC_PARENT_ACTION = (
    "Removed generic Rv1667 parent mutation draft after curating the M. tuberculosis "
    "pyrazinamide-specific graph"
)
PYRAZINAMIDE_PARENT_ACTION = (
    "Removed inherited Rv1667 pyrazinamide draft after curating the M. tuberculosis "
    "pyrazinamide-specific graph"
)
CHILD_ACTION = "Completed M. tuberculosis Rv1667 pyrazinamide efflux causal graph; SEEDED -> REVIEWED"

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
EFFLUX_EVIDENCE = {
    "reference": "ARO:0010000",
    "snippet": "Antibiotic resistance via the transport of antibiotics out of the cell.",
    "notes": "CARD definition for the antibiotic efflux resistance mechanism.",
}
ZHANG_EVIDENCE = {
    "reference": "DOI:10.1128/AAC.00940-17",
    "snippet": (
        "Identification of Novel Efflux Proteins Rv0191, Rv3756c, Rv3008, and Rv1667c "
        "Involved in Pyrazinamide Resistance in Mycobacterium tuberculosis"
    ),
    "notes": (
        "CARD-cited Zhang et al. 2017 title supporting Rv1667c as an efflux protein involved "
        "in pyrazinamide resistance."
    ),
}
DRUG_RELATION_EVIDENCE = {
    "reference": "ARO:3004983",
    "snippet": "relationship: confers_resistance_to_drug_class ARO:3007155 ! pyrazine antibiotic",
    "notes": (
        "CARD asserts a pyrazine-antibiotic resistance relation on the pyrazinamide resistant "
        "Rv1667 parent."
    ),
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


ANTIBIOTIC_PARENT = Target(
    "ARO:3004982",
    "antibiotic-resistant-rv1667-aro3004982.yaml",
    ANTIBIOTIC_PARENT_ACTION,
)
PYRAZINAMIDE_PARENT = Target(
    "ARO:3004983",
    "pyrazinamide-resistant-rv1667-aro3004983.yaml",
    PYRAZINAMIDE_PARENT_ACTION,
)
CHILD = Target(
    "ARO:3004984",
    "mycobacterium-tuberculosis-rv1667-mutations-confer-resistance-to-pyrazinamide-aro3004984.yaml",
    CHILD_ACTION,
)
PARENTS = (ANTIBIOTIC_PARENT, PYRAZINAMIDE_PARENT)
TARGETS = (*PARENTS, CHILD)

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


def _graph(record: dict[str, Any]) -> dict[str, Any]:
    record_evidence = _record_evidence(record)
    efflux_evidence = (record_evidence, EFFLUX_EVIDENCE, ZHANG_EVIDENCE)
    return {
        "graph_id": "resistance",
        "title": "M. tuberculosis Rv1667 mutations → pyrazinamide resistance",
        "description": (
            "Curated Rv1667 pyrazinamide-resistance graph. CARD assigns this determinant to the "
            "broad mutation-conferring mechanism, links it to the pyrazine-antibiotic class through "
            "its pyrazinamide-resistant Rv1667 parent, and cites Zhang et al. evidence for Rv1667c "
            "involvement in pyrazinamide efflux."
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
                "node_id": "efflux",
                "label": "antibiotic efflux",
                "node_type": "MOLECULAR_FUNCTION",
                "grounding": "ARO:0010000",
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
                "CARD classifies Rv1667 pyrazinamide-resistance variants under the broad mutation-conferring "
                "antibiotic-resistance mechanism.",
                record_evidence,
                MUTATION_EVIDENCE,
            ),
            _edge(
                "determinant",
                "causally upstream of (putative antibiotic export)",
                "RO:0002411",
                "efflux",
                "The M. tuberculosis Rv1667 record notes that resistance may be due to antibiotic export, "
                "consistent with the Zhang et al. efflux-protein evidence.",
                *efflux_evidence,
            ),
            _edge(
                "efflux",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Antibiotic export lowers pyrazinamide exposure and causes the resistance phenotype.",
                *efflux_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "CARD states that Rv1667 mutations can contribute to or confer pyrazinamide resistance.",
                record_evidence,
                ZHANG_EVIDENCE,
            ),
            _edge(
                "determinant",
                "confers resistance to (drug class)",
                "ARO:2000001",
                "drug0",
                "CARD asserts a pyrazine-antibiotic resistance relation on the pyrazinamide resistant "
                "Rv1667 parent and this M. tuberculosis variant inherits that relation.",
                DRUG_RELATION_EVIDENCE,
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


def repair_parent_text(text: str, target: Target, path: Path | None = None) -> tuple[str, bool]:
    _require_identifier(text, target, path or target.path)
    out = _remove_block(text, "causal_graphs")
    out = _append_history_once(out, target)
    return out, out != text


def curate_child_text(text: str, target: Target = CHILD, path: Path | None = None) -> tuple[str, bool]:
    record = _require_identifier(text, target, path or target.path)
    out = _set_mapping_status(text, "REVIEWED")
    out = replace_block(out, "causal_graphs", _dump({"causal_graphs": [_graph(record)]}))
    out = _append_history_once(out, target)
    return out, out != text


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    for target in PARENTS:
        if path.name == target.filename:
            return repair_parent_text(text, target, path)
    if path.name == CHILD.filename:
        return curate_child_text(text, CHILD, path)
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
