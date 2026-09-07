#!/usr/bin/env python3
"""Rewrite tetracycline hydroxylation inactivation ARO graphs.

The tetracycline inactivation parent and TetX-like child records already carry
the right broad mechanism, hydroxylation mechanism, drug-class, and inactive
product-state nodes. This updater removes the ungrounded local duplicate of the
hydroxylation mechanism, adds the missing inactive-drug-to-resistance edge, and
adds descriptions plus multi-reference evidence to every edge.

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

HISTORY_ACTION = "Completed tetracycline inactivation causal graphs"
HISTORY_CURATOR = "codex-causal-graph-quality"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

ANTIBIOTIC_INACTIVATION_EVIDENCE = {
    "reference": "ARO:0001004",
    "snippet": "Enzymatic inactivation of antibiotic to confer drug resistance.",
    "notes": "CARD definition for antibiotic inactivation.",
}

INACTIVATION_ENZYME_EVIDENCE = {
    "reference": "ARO:3000557",
    "snippet": (
        "Enzyme that catalyzes the inactivation of an antibiotic resulting in "
        "resistance. Inactivation includes chemical modification, destruction, etc."
    ),
    "notes": "CARD definition for antibiotic inactivation enzymes.",
}

TETRACYCLINE_INACTIVATION_EVIDENCE = {
    "reference": "ARO:3000036",
    "snippet": (
        "Enzymes or other gene products which hydroxylate tetracycline and "
        "other tetracycline derivatives. Hydroxylation inactivates "
        "tetracycline-like antibiotics, thus conferring resistance to these "
        "compounds."
    ),
    "notes": "CARD definition for tetracycline inactivation enzymes.",
}

HYDROXYLATION_EVIDENCE = {
    "reference": "ARO:3000450",
    "snippet": "Inactivation of an antibiotic via introduction a hydroxyl group (-OH).",
    "notes": "CARD definition for hydroxylation of antibiotic conferring resistance.",
}

TETRACYCLINE_DRUG_CLASS_EVIDENCE = {
    "reference": "ARO:3000036",
    "snippet": (
        "relationship: confers_resistance_to_drug_class ARO:3000050 ! "
        "tetracycline antibiotic"
    ),
    "notes": (
        "CARD/ARO relationship asserting tetracycline antibiotic as the drug "
        "class for tetracycline inactivation enzymes."
    ),
}

TETRACYCLINE_DRUG_EVIDENCE = {
    "reference": "ARO:3000050",
    "snippet": "tetracycline antibiotic",
    "notes": "CARD drug-class term for tetracycline antibiotics.",
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


TARGETS: tuple[Target, ...] = (
    Target("ARO:3000036", "tetracycline-inactivation-enzyme-aro3000036.yaml"),
    Target("ARO:3000205", "tet-x-aro3000205.yaml"),
    Target("ARO:3002871", "tet-37-aro3002871.yaml"),
    Target("ARO:3004613", "tet-47-aro3004613.yaml"),
    Target("ARO:3004581", "tet-48-aro3004581.yaml"),
    Target("ARO:3004582", "tet-49-aro3004582.yaml"),
    Target("ARO:3004584", "tet-50-aro3004584.yaml"),
    Target("ARO:3004586", "tet-51-aro3004586.yaml"),
    Target("ARO:3004587", "tet-52-aro3004587.yaml"),
    Target("ARO:3004589", "tet-53-aro3004589.yaml"),
    Target("ARO:3004590", "tet-54-aro3004590.yaml"),
    Target("ARO:3004591", "tet-55-aro3004591.yaml"),
    Target("ARO:3004603", "tet-56-aro3004603.yaml"),
    Target("ARO:3004719", "tet-x3-aro3004719.yaml"),
    Target("ARO:3004720", "tet-x4-aro3004720.yaml"),
    Target("ARO:3005056", "tet-x6-aro3005056.yaml"),
    Target("ARO:3005057", "tet-x5-aro3005057.yaml"),
    Target("ARO:3005166", "tet-x1-aro3005166.yaml"),
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


def _canonical_graph(record: dict[str, Any]) -> dict[str, Any]:
    target_evidence = _record_evidence(record)
    broad_evidence = (
        target_evidence,
        TETRACYCLINE_INACTIVATION_EVIDENCE,
        INACTIVATION_ENZYME_EVIDENCE,
        ANTIBIOTIC_INACTIVATION_EVIDENCE,
    )
    hydroxylation_evidence = (
        target_evidence,
        TETRACYCLINE_INACTIVATION_EVIDENCE,
        HYDROXYLATION_EVIDENCE,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → tetracycline hydroxylation → resistance",
        "description": (
            "Curated resistance-causation graph for tetracycline inactivation "
            "enzymes. The determinant participates in broad antibiotic "
            "inactivation and in the narrower hydroxylation mechanism that "
            "hydroxylates tetracycline-like antibiotics to an inactive product."
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
                "description": (
                    "Hydroxylation route that chemically inactivates "
                    "tetracycline-like antibiotics."
                ),
            },
            {
                "node_id": "drug0",
                "label": "tetracycline antibiotic",
                "node_type": "CHEMICAL",
                "grounding": "ARO:3000050",
            },
            {
                "node_id": "inactivated",
                "label": "hydroxylated, inactive tetracycline",
                "node_type": "STATE",
                "description": (
                    "Local product state for a tetracycline-like antibiotic "
                    "chemically inactivated by hydroxylation."
                ),
            },
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "CARD classifies this enzyme under antibiotic inactivation.",
                *broad_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Enzymatic antibiotic inactivation removes active antibiotic and "
                "thereby causes resistance.",
                *broad_evidence,
            ),
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech1",
                "CARD classifies tetracycline inactivation enzymes under "
                "hydroxylation of antibiotic conferring resistance.",
                *hydroxylation_evidence,
            ),
            _edge(
                "mech1",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Hydroxylation inactivates tetracycline-like antibiotics and "
                "thereby causes resistance.",
                *hydroxylation_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "The determinant hydroxylates tetracycline-like antibiotics, "
                "leaving the drug inactive.",
                *broad_evidence,
                HYDROXYLATION_EVIDENCE,
            ),
            _edge(
                "determinant",
                "confers resistance to (drug class)",
                "ARO:2000001",
                "drug0",
                "CARD asserts that tetracycline inactivation enzymes confer "
                "resistance to tetracycline antibiotics.",
                target_evidence,
                TETRACYCLINE_INACTIVATION_EVIDENCE,
                TETRACYCLINE_DRUG_CLASS_EVIDENCE,
                TETRACYCLINE_DRUG_EVIDENCE,
            ),
            _edge(
                "mech1",
                "has input",
                "RO:0002233",
                "drug0",
                "The hydroxylation mechanism acts on the tetracycline-class "
                "antibiotic itself.",
                *hydroxylation_evidence,
                TETRACYCLINE_DRUG_EVIDENCE,
            ),
            _edge(
                "mech1",
                "causally upstream of (inactivates the drug)",
                "RO:0002411",
                "inactivated",
                "Hydroxylation of tetracycline-like antibiotics produces an "
                "inactive product state.",
                *hydroxylation_evidence,
            ),
            _edge(
                "inactivated",
                "causally upstream of (drug is inactive)",
                "RO:0002411",
                "resistance",
                "The hydroxylated antibiotic no longer blocks growth at "
                "otherwise inhibitory concentrations.",
                TETRACYCLINE_INACTIVATION_EVIDENCE,
                HYDROXYLATION_EVIDENCE,
                ANTIBIOTIC_INACTIVATION_EVIDENCE,
            ),
        ],
    }


REQUIRED_NODES = {
    "determinant",
    "mech0",
    "mech1",
    "drug0",
    "inactivated",
    "resistance",
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
    missing_nodes = sorted(REQUIRED_NODES - node_ids)
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    _validate_record(record, target)

    out = copy.deepcopy(record)
    out["causal_graphs"] = [_canonical_graph(record)]
    return out, out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not a tetracycline inactivation target: {identifier}")
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
        help="ARO directory or one of the tetracycline inactivation target YAML files",
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
