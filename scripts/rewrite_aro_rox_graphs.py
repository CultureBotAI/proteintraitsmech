#!/usr/bin/env python3
"""Rewrite rifampin monooxygenase/Rox ARO causal graphs.

Rifampin monooxygenases inactivate rifamycin antibiotics by oxidative
modification.  The existing promoted graphs leave the local hydroxylase node
ungrounded, stop at the modified-drug state, and have sparse edge
descriptions.  This updater grounds the broad monooxygenase activity and
terminates the inactivation path at resistance.

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
    "action": "Completed rifampin monooxygenase causal graphs",
    "llm_assisted": True,
}

INACTIVATION_EVIDENCE = {
    "reference": "ARO:3000576",
    "snippet": "Enzymes that inactivate rifampin antibiotics by chemical modification.",
    "notes": "CARD definition for the rifampin inactivation enzyme parent.",
}

HYDROXYLATION_EVIDENCE = {
    "reference": "ARO:3000450",
    "snippet": "Inactivation of an antibiotic via introduction a hydroxyl group (-OH).",
    "notes": "CARD definition for hydroxylation of antibiotic conferring resistance.",
}

ROX_PARENT_EVIDENCE = {
    "reference": "ARO:3000445",
    "snippet": "Rifampin monooxygenases decolorize rifampin by monooxygenation.",
    "notes": "CARD definition for rifampin monooxygenases.",
}

NOCARDIA_ROX_EVIDENCE = {
    "reference": "DOI:10.1038/ja.2009.116",
    "snippet": (
        "The CARD-cited Nocardia farcinica Rox report identified a rifampin "
        "monooxygenase that inactivates rifampin."
    ),
    "notes": "CARD-cited evidence for Nocardia Rox-mediated rifampin inactivation.",
}

SVEN_ROX_EVIDENCE = {
    "reference": "DOI:10.1016/j.chembiol.2018.01.009",
    "snippet": (
        "The CARD-cited Streptomyces venezuelae Rox report linked naphthyl "
        "oxygenation and rifampin ring opening to rifamycin resistance."
    ),
    "notes": "CARD-cited evidence for Rox-mediated rifampin ring opening.",
}

GO_MONOOXYGENASE_EVIDENCE = {
    "reference": "GO:0004497",
    "snippet": "Catalysis of the incorporation of one atom from molecular oxygen into a substrate.",
    "notes": "GO grounding for the broad monooxygenase activity node.",
}

RIFAMYCIN_RELATION_EVIDENCE = {
    "reference": "ARO:3000445",
    "snippet": "relationship: confers_resistance_to_drug_class ARO:3000157 ! rifamycin antibiotic",
    "notes": "Rifamycin drug-class relation asserted on the rifampin monooxygenase parent.",
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

RIFAMYCIN_NODE = {
    "node_id": "drug0",
    "label": "rifamycin antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:3000157",
}

MONOOXYGENATION_NODE = {
    "node_id": "monooxygenation",
    "label": "monooxygenase activity",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "GO:0004497",
    "description": (
        "Grounded to the broad GO monooxygenase activity term and scoped here "
        "to rifamycin oxygenation."
    ),
}

MODIFIED_NODE = {
    "node_id": "modified",
    "label": "oxygenated ring-opened inactive rifamycin",
    "node_type": "STATE",
    "description": (
        "Local state for rifamycin after monooxygenase-mediated oxygenation "
        "and downstream ring opening."
    ),
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str


TARGETS: tuple[Target, ...] = (
    Target("ARO:3000445", "rifampin-monooxygenase-aro3000445.yaml"),
    Target("ARO:3007209", "streptomyces-venezuelae-rox-aro3007209.yaml"),
    Target("ARO:3007210", "nocardia-farcinica-rox-aro3007210.yaml"),
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


def _graph(record: dict[str, Any]) -> dict[str, Any]:
    record_evidence = _record_evidence(record)
    common_evidence = (
        record_evidence,
        ROX_PARENT_EVIDENCE,
        HYDROXYLATION_EVIDENCE,
        NOCARDIA_ROX_EVIDENCE,
        SVEN_ROX_EVIDENCE,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → rifamycin oxygenation",
        "description": (
            "Curated resistance-causation graph for Rox-mediated rifamycin "
            "oxygenation, ring opening, and inactivation."
        ),
        "nodes": [
            _determinant_node(record),
            {
                "node_id": "mech0",
                "label": "antibiotic inactivation",
                "node_type": "MOLECULAR_FUNCTION",
                "grounding": "ARO:0001004",
            },
            {
                "node_id": "mech1",
                "label": "hydroxylation of antibiotic conferring resistance",
                "node_type": "MOLECULAR_FUNCTION",
                "grounding": "ARO:3000450",
            },
            copy.deepcopy(RIFAMYCIN_NODE),
            copy.deepcopy(MONOOXYGENATION_NODE),
            copy.deepcopy(MODIFIED_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "CARD classifies rifampin monooxygenases under rifampin "
                "antibiotic inactivation.",
                record_evidence,
                INACTIVATION_EVIDENCE,
                ROX_PARENT_EVIDENCE,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Rifampin monooxygenase antibiotic inactivation results from "
                "oxidative modification of the drug.",
                INACTIVATION_EVIDENCE,
                HYDROXYLATION_EVIDENCE,
                ROX_PARENT_EVIDENCE,
            ),
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech1",
                "CARD classifies rifampin monooxygenases under hydroxylation "
                "of antibiotic conferring resistance.",
                *common_evidence,
            ),
            _edge(
                "mech1",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "The hydroxylation resistance mechanism inactivates rifamycins "
                "by chemical modification.",
                *common_evidence,
                INACTIVATION_EVIDENCE,
            ),
            _edge(
                "determinant",
                "enables (modifies the drug)",
                "RO:0002327",
                "monooxygenation",
                "Rifampin monooxygenases catalyze oxidative rifamycin "
                "modification.",
                *common_evidence,
                GO_MONOOXYGENASE_EVIDENCE,
            ),
            _edge(
                "monooxygenation",
                "has input (the drug)",
                "RO:0002233",
                "drug0",
                "Rifamycin antibiotics are substrates for Rox monooxygenase "
                "activity.",
                *common_evidence,
                RIFAMYCIN_RELATION_EVIDENCE,
            ),
            _edge(
                "monooxygenation",
                "causally upstream of (inactivates the drug)",
                "RO:0002411",
                "modified",
                "Rifamycin oxygenation by Rox leads to ring opening and drug "
                "inactivation.",
                *common_evidence,
                GO_MONOOXYGENASE_EVIDENCE,
            ),
            _edge(
                "modified",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "The oxygenated ring-opened rifamycin state is inactive and "
                "causes the modeled resistance phenotype.",
                *common_evidence,
                INACTIVATION_EVIDENCE,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "Rifampin monooxygenases confer rifamycin resistance through "
                "oxygenation, ring opening, and drug inactivation.",
                *common_evidence,
                INACTIVATION_EVIDENCE,
            ),
            _edge(
                "determinant",
                "confers resistance to (drug class)",
                "ARO:2000001",
                "drug0",
                "CARD asserts a rifamycin antibiotic drug-class relation on "
                "the rifampin monooxygenase parent.",
                record_evidence,
                ROX_PARENT_EVIDENCE,
                RIFAMYCIN_RELATION_EVIDENCE,
                HYDROXYLATION_EVIDENCE,
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
    out["causal_graphs"] = [_graph(record)]
    return out, out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not a rifampin monooxygenase target: {identifier}")
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
        help="ARO directory or one rifampin monooxygenase YAML file",
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
