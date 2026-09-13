#!/usr/bin/env python3
"""Rewrite generic RNA-polymerase target-protection ARO graphs.

The rifampin-resistant RNA polymerase-binding protein parent and the sigma
factor child assert antibiotic target protection but do not carry a direct CARD
rifamycin drug-class relationship.  Keep the graph at that asserted level and
drop the old ungrounded local target/protected-target state nodes.

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

HISTORY_ACTION = "Completed generic RNA-polymerase target-protection graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-09T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str


TARGETS: tuple[Target, ...] = (
    Target(
        "ARO:3000507",
        "rifampin-resistant-rna-polymerase-binding-protein-aro3000507.yaml",
    ),
    Target(
        "ARO:3000261",
        "sigma-factor-conferring-resistance-to-rifampin-aro3000261.yaml",
    ),
)
TARGET_BY_ID = {target.identifier: target for target in TARGETS}

RNAP_BINDING_PROTEIN_EVIDENCE = {
    "reference": "ARO:3000507",
    "snippet": (
        "Proteins which have been experimentally shown to protect "
        "RNA-polymerase from rifampin inhibition."
    ),
    "notes": "CARD definition for rifampin-resistant RNA polymerase-binding proteins.",
}

TARGET_PROTECTION_EVIDENCE = {
    "reference": "ARO:3000185",
    "snippet": (
        "These proteins confer antibiotic resistance by bind the antibiotic "
        "target to prevent antibiotic binding."
    ),
    "notes": "CARD definition for antibiotic target protection proteins.",
}

MECHANISM_EVIDENCE = {
    "reference": "ARO:0001003",
    "snippet": (
        "Protection of antibiotic action target from antibiotic binding, "
        "which process will result in antibiotic resistance."
    ),
    "notes": "CARD definition for antibiotic target protection.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "antibiotic target protection",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:0001003",
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

EDGE_DESCRIPTIONS = {
    ("determinant", "RO:0000056", "mech0"): (
        "CARD classifies this determinant under antibiotic target protection."
    ),
    ("mech0", "RO:0002411", "resistance"): (
        "Antibiotic target protection prevents antibiotic inhibition of the "
        "target and thereby causes resistance."
    ),
    ("determinant", "RO:0002411", "resistance"): (
        "The determinant protects RNA polymerase from rifampin inhibition."
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


def _dicts(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _source_evidence(record: dict[str, Any]) -> tuple[dict[str, str], ...]:
    return tuple(
        {
            "reference": str(item["reference"]),
            "notes": str(item.get("notes") or "ARO citation for this record."),
        }
        for item in _dicts(record.get("evidence"))
        if item.get("reference")
    )


def _record_evidence(record: dict[str, Any]) -> dict[str, str]:
    return {
        "reference": str(record["identifier"]),
        "snippet": " ".join(str(record["definition"]).split()),
        "notes": f"CARD definition for {record['label']}.",
    }


def _family_evidence(record: dict[str, Any]) -> tuple[dict[str, str], ...]:
    if record["identifier"] == "ARO:3000507":
        return ()
    return (RNAP_BINDING_PROTEIN_EVIDENCE,)


def _unique_evidence(evidence: tuple[dict[str, str], ...]) -> list[dict[str, str]]:
    unique: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for item in evidence:
        key = (
            item["reference"],
            item.get("snippet", ""),
            item.get("notes", ""),
        )
        if key in seen:
            continue
        seen.add(key)
        unique.append(copy.deepcopy(item))
    return unique


def _edge(
    subject: str,
    predicate: str,
    predicate_id: str,
    object_: str,
    evidence: tuple[dict[str, str], ...],
) -> dict[str, Any]:
    return {
        "subject": subject,
        "predicate": predicate,
        "predicate_id": predicate_id,
        "object": object_,
        "description": EDGE_DESCRIPTIONS[(subject, predicate_id, object_)],
        "evidence": _unique_evidence(evidence),
    }


def _graph(record: dict[str, Any]) -> dict[str, Any]:
    common_evidence = (
        _record_evidence(record),
        *_family_evidence(record),
        TARGET_PROTECTION_EVIDENCE,
        MECHANISM_EVIDENCE,
        *_source_evidence(record),
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → RNA polymerase target protection",
        "description": (
            "Curated resistance-causation graph for determinants that protect "
            "RNA polymerase from rifampin inhibition. The graph keeps the "
            "generic CARD antibiotic-target-protection mechanism without "
            "asserting a direct drug-class edge absent from these ARO records."
        ),
        "nodes": [
            {
                "node_id": "determinant",
                "label": str(record["label"]),
                "node_type": "PROTEIN",
                "grounding": str(record["identifier"]),
            },
            copy.deepcopy(MECHANISM_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                common_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                common_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                common_evidence,
            ),
        ],
    }


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != target.identifier:
        raise ValueError(f"expected {target.identifier}, found {record.get('identifier')}")
    if not record.get("label"):
        raise ValueError(f"{target.identifier}: missing label")
    if not record.get("definition"):
        raise ValueError(f"{target.identifier}: missing definition")

    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1 or graphs[0].get("graph_id") != "resistance":
        raise ValueError(f"{target.identifier}: expected exactly one resistance graph")

    out = copy.deepcopy(record)
    out["causal_graphs"] = [_graph(record)]
    return out, out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not a generic RNA-polymerase target-protection target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
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
        help="ARO directory or one of the two generic RNA-polymerase target-protection YAML files",
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
