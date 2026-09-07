#!/usr/bin/env python3
"""Rewrite fusidic acid inactivation/FusH ARO causal graphs.

Fusidic acid inactivation enzymes confer resistance by hydrolyzing fusidic acid
to an inactive lactone derivative.  The existing promoted graphs leave a local
fusidic acid hydrolase activity ungrounded and stop at the modified-drug state.
This updater reuses the ARO:3004140 fusidic-acid hydrolysis mechanism directly
and terminates the inactivation path at resistance.

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
HISTORY_EVENT = {
    "timestamp": "2026-09-07T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": "Completed fusidic acid inactivation causal graphs",
    "llm_assisted": True,
}

INACTIVATION_EVIDENCE = {
    "reference": "ARO:0001004",
    "snippet": "Enzymatic inactivation of antibiotic to confer drug resistance.",
    "notes": "CARD definition for the antibiotic inactivation mechanism.",
}

FUSIDIC_PARENT_EVIDENCE = {
    "reference": "ARO:3003025",
    "snippet": "Enzymes that confer resistance to fusidic acid by inactivation.",
    "notes": "CARD definition for the fusidic acid inactivation enzyme family.",
}

LACTONIZATION_EVIDENCE = {
    "reference": "ARO:3004140",
    "snippet": (
        "Enzymes shown to inactivate fusidic acid by hydrolytic cleavage from "
        "the 16 beta-position of fusidic acid and its derivatives. This "
        "converts fusidic acid to an inactivate lactone derivative, thus "
        "conferring resistance to fusidic acid."
    ),
    "notes": "CARD definition for fusidic acid hydrolysis to inactive lactone.",
}

FUSH_EVIDENCE = {
    "reference": "DOI:10.1099/00221287-143-3-867",
    "notes": "CARD-cited evidence for Streptomyces lividans FusH.",
}

FUSIDANE_RELATION_EVIDENCE = {
    "reference": "ARO:3003025",
    "snippet": "relationship: confers_resistance_to_drug_class ARO:3007153 ! fusidane antibiotic",
    "notes": "Fusidane drug-class relation asserted on the fusidic acid inactivation parent.",
}

FUSIDANE_ANTIBIOTIC_EVIDENCE = {
    "reference": "ARO:3007153",
    "snippet": "fusidane antibiotic",
    "notes": "ARO drug-class term targeted by fusidic acid inactivation enzymes.",
}

FUSIDANE_NODE = {
    "node_id": "drug0",
    "label": "fusidane antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:3007153",
}

LACTONIZATION_NODE = {
    "node_id": "mech1",
    "label": "hydrolysis of fusidic acid to inactive lactone derivative",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3004140",
}

MODIFIED_NODE = {
    "node_id": "modified",
    "label": "inactive fusidic acid lactone derivative",
    "node_type": "STATE",
    "description": "Local state for fusidic acid after hydrolytic lactone formation.",
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
    evidence: tuple[dict[str, str], ...] = ()


TARGETS: tuple[Target, ...] = (
    Target("ARO:3003025", "fusidic-acid-inactivation-enzyme-aro3003025.yaml"),
    Target("ARO:3003026", "fush-aro3003026.yaml", (FUSH_EVIDENCE,)),
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
    seen: set[tuple[str, str]] = set()
    for item in items:
        key = (
            item["reference"],
            item.get("snippet", ""),
        )
        if key in seen:
            continue
        seen.add(key)
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
    mechanism_evidence = (
        record_evidence,
        FUSIDIC_PARENT_EVIDENCE,
        LACTONIZATION_EVIDENCE,
        *target.evidence,
    )
    resistance_evidence = (
        record_evidence,
        FUSIDIC_PARENT_EVIDENCE,
        LACTONIZATION_EVIDENCE,
        INACTIVATION_EVIDENCE,
        *target.evidence,
    )
    drug_evidence = (
        record_evidence,
        FUSIDIC_PARENT_EVIDENCE,
        FUSIDANE_RELATION_EVIDENCE,
        FUSIDANE_ANTIBIOTIC_EVIDENCE,
        *target.evidence,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → fusidic acid lactonization",
        "description": (
            "Curated resistance-causation graph for fusidic-acid hydrolysis "
            "to an inactive lactone derivative."
        ),
        "nodes": [
            _determinant_node(record),
            {
                "node_id": "mech0",
                "label": "antibiotic inactivation",
                "node_type": "MOLECULAR_FUNCTION",
                "grounding": "ARO:0001004",
            },
            copy.deepcopy(LACTONIZATION_NODE),
            copy.deepcopy(FUSIDANE_NODE),
            copy.deepcopy(MODIFIED_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "ARO classifies fusidic acid inactivation enzymes under "
                "antibiotic inactivation.",
                record_evidence,
                FUSIDIC_PARENT_EVIDENCE,
                INACTIVATION_EVIDENCE,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Fusidic acid lactonization enzymatically inactivates "
                "fusidane antibiotics.",
                *resistance_evidence,
            ),
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech1",
                "ARO classifies fusidic acid inactivation enzymes under "
                "hydrolysis of fusidic acid to an inactive lactone derivative.",
                *mechanism_evidence,
            ),
            _edge(
                "mech1",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Hydrolytic conversion of fusidic acid to its lactone "
                "derivative inactivates the drug and confers resistance.",
                *resistance_evidence,
            ),
            _edge(
                "determinant",
                "confers resistance to (drug class)",
                "ARO:2000001",
                "drug0",
                "CARD asserts a fusidane antibiotic drug-class relation on "
                "the fusidic acid inactivation enzyme parent.",
                *drug_evidence,
            ),
            _edge(
                "mech1",
                "has input (the drug)",
                "RO:0002233",
                "drug0",
                "Fusidic acid is a fusidane-antibiotic substrate of the "
                "hydrolytic lactonization mechanism.",
                *mechanism_evidence,
            ),
            _edge(
                "mech1",
                "causally upstream of (inactivates the drug)",
                "RO:0002411",
                "modified",
                "Hydrolysis at the fusidic acid 16 beta-position converts the "
                "drug to an inactive lactone derivative.",
                *mechanism_evidence,
            ),
            _edge(
                "modified",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "The inactive fusidic acid lactone reduces effective drug "
                "exposure and produces the resistance phenotype.",
                *resistance_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "Fusidic acid inactivation enzymes confer resistance by "
                "hydrolyzing fusidic acid to an inactive lactone derivative.",
                *resistance_evidence,
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
    if len(graphs) != 1 or graphs[0].get("graph_id") != "resistance":
        raise ValueError(f"{target.identifier}: expected exactly one resistance graph")

    node_ids = {
        str(node.get("node_id"))
        for node in _dicts(graphs[0].get("nodes"))
        if node.get("node_id")
    }
    missing = {"determinant", "mech0", "mech1", "drug0", "modified", "resistance"} - node_ids
    if missing:
        missing_ids = ", ".join(sorted(missing))
        raise ValueError(f"{target.identifier}: missing node(s): {missing_ids}")


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    _validate_record(record, target)

    out = copy.deepcopy(record)
    out["causal_graphs"] = [_graph(record, target)]
    return out, out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not a fusidic acid inactivation target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    if HISTORY_CURATOR not in out:
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
        help="ARO directory or one fusidic acid inactivation YAML file",
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
