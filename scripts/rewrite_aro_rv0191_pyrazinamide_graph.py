#!/usr/bin/env python3
"""Rewrite the CARD Rv0191 pyrazinamide-resistance causal graphs.

The broad ``antibiotic resistant Rv0191`` parent only says that Rv0191 mutations
can contribute to antibiotic resistance, with no drug or Rv0191-specific
mechanism.  The pyrazinamide-specific record is more concrete: CARD describes
Rv0191 as an active efflux pump whose overexpression causes pyrazinamide
resistance, and cites Zhang et al. 2017 for Rv0191 involvement in PZA resistance.
The M. tuberculosis child carries the direct mutation-to-pyrazinamide-resistance
definition and inherits the pyrazine-antibiotic class from that parent.

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

PARENT_ACTION = (
    "Removed generic Rv0191 parent mutation draft after curating the pyrazinamide-specific graph"
)
CHILD_ACTION = "Completed Rv0191 pyrazinamide efflux causal graph; SEEDED -> REVIEWED"
MTUB_CHILD_ACTION = (
    "Completed M. tuberculosis Rv0191 pyrazinamide mutation causal graph; SEEDED -> REVIEWED"
)

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
        "CARD-cited Zhang et al. 2017 title supporting Rv0191 as an efflux protein involved "
        "in pyrazinamide resistance."
    ),
}

DRUG_RELATION_EVIDENCE = {
    "reference": "ARO:3004980",
    "snippet": "relationship: confers_resistance_to_drug_class ARO:3007155 ! pyrazine antibiotic",
    "notes": "CARD asserts a pyrazine-antibiotic resistance relation on pyrazinamide resistant Rv0191.",
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


PARENT = Target(
    identifier="ARO:3004979",
    filename="antibiotic-resistant-rv0191-aro3004979.yaml",
    action=PARENT_ACTION,
)
CHILD = Target(
    identifier="ARO:3004980",
    filename="pyrazinamide-resistant-rv0191-aro3004980.yaml",
    action=CHILD_ACTION,
)
MTUB_CHILD = Target(
    identifier="ARO:3004981",
    filename="mycobacterium-tuberculosis-rv0191-mutations-confer-resistance-to-pyrazinamide-aro3004981.yaml",
    action=MTUB_CHILD_ACTION,
)
TARGETS = (PARENT, CHILD, MTUB_CHILD)

_TOP_KEY = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*:")
_MAPPING_STATUS = re.compile(r"^mapping_status:[ \t]*(.+?)[ \t]*$", re.M)


def _dump(obj: Any) -> str:
    return yaml.safe_dump(
        obj,
        sort_keys=False,
        allow_unicode=True,
        width=100,
        default_flow_style=False,
    )


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
    evidence: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in items:
        reference = item["reference"]
        if reference in seen:
            continue
        seen.add(reference)
        evidence.append(dict(item))
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


def _graph(record: dict[str, Any]) -> dict[str, Any]:
    record_evidence = _record_evidence(record)
    common_evidence = (record_evidence, EFFLUX_EVIDENCE, ZHANG_EVIDENCE)

    return {
        "graph_id": "resistance",
        "title": "pyrazinamide resistant Rv0191 → active efflux → resistance",
        "description": (
            "Curated Rv0191 pyrazinamide-resistance graph. CARD assigns this determinant to "
            "the broad mutation-conferring mechanism and pyrazine-antibiotic drug class; the "
            "record definition and Zhang et al. evidence support Rv0191 as an active efflux "
            "pump involved in pyrazinamide resistance."
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
                "CARD classifies pyrazinamide resistant Rv0191 under the broad mutation-conferring "
                "antibiotic-resistance mechanism.",
                record_evidence,
                MUTATION_EVIDENCE,
            ),
            _edge(
                "determinant",
                "enables (active drug efflux)",
                "RO:0002327",
                "efflux",
                "The Rv0191 determinant is represented as an active pyrazinamide efflux pump.",
                *common_evidence,
            ),
            _edge(
                "efflux",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Active drug efflux lowers pyrazinamide exposure and causes the resistance phenotype.",
                *common_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "CARD states that Rv0191 overexpression causes pyrazinamide resistance.",
                record_evidence,
                ZHANG_EVIDENCE,
            ),
            _edge(
                "determinant",
                "confers resistance to (drug class)",
                "ARO:2000001",
                "drug0",
                "CARD asserts that pyrazinamide resistant Rv0191 confers resistance to the pyrazine-antibiotic "
                "drug class.",
                DRUG_RELATION_EVIDENCE,
                PYRAZINE_EVIDENCE,
            ),
        ],
    }


def _mtub_child_graph(record: dict[str, Any]) -> dict[str, Any]:
    record_evidence = _record_evidence(record)
    return {
        "graph_id": "resistance",
        "title": "M. tuberculosis Rv0191 mutations → pyrazinamide resistance",
        "description": (
            "Curated M. tuberculosis Rv0191 pyrazinamide-resistance graph. CARD assigns this "
            "determinant to the broad mutation-conferring mechanism and links it to the "
            "pyrazine-antibiotic class through its pyrazinamide-resistant Rv0191 parent. The "
            "parent Rv0191 record carries the active-efflux function; this child graph keeps "
            "the causal model at the directly asserted mutation and phenotype levels."
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
                "CARD classifies Rv0191 pyrazinamide-resistance variants under the broad "
                "mutation-conferring antibiotic-resistance mechanism.",
                record_evidence,
                MUTATION_EVIDENCE,
            ),
            _edge(
                "mutation",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "CARD's mutation-conferring mechanism links point mutations to altered gene "
                "products that can cause antibiotic resistance, and the M. tuberculosis Rv0191 "
                "record states that these mutations contribute to or confer pyrazinamide "
                "resistance.",
                MUTATION_EVIDENCE,
                record_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "CARD states that Rv0191 mutations contribute to or confer pyrazinamide resistance.",
                record_evidence,
                ZHANG_EVIDENCE,
            ),
            _edge(
                "determinant",
                "confers resistance to (drug class)",
                "ARO:2000001",
                "drug0",
                "CARD asserts a pyrazine-antibiotic resistance relation on pyrazinamide resistant "
                "Rv0191 and this M. tuberculosis variant inherits that relation.",
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


def repair_parent_text(text: str, target: Target = PARENT, path: Path | None = None) -> tuple[str, bool]:
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


def curate_mtub_child_text(
    text: str,
    target: Target = MTUB_CHILD,
    path: Path | None = None,
) -> tuple[str, bool]:
    record = _require_identifier(text, target, path or target.path)

    out = _set_mapping_status(text, "REVIEWED")
    out = replace_block(out, "causal_graphs", _dump({"causal_graphs": [_mtub_child_graph(record)]}))
    out = _append_history_once(out, target)
    return out, out != text


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    if path.name == PARENT.filename:
        return repair_parent_text(text, PARENT, path)
    if path.name == CHILD.filename:
        return curate_child_text(text, CHILD, path)
    if path.name == MTUB_CHILD.filename:
        return curate_mtub_child_text(text, MTUB_CHILD, path)
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
