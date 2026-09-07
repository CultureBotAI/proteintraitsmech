#!/usr/bin/env python3
"""Rewrite host-dependent nutrient-acquisition ARO graphs.

These records model resistance caused by bacterial uptake of host nutrients that
bypass the biosynthetic step blocked by an antibiotic.  The existing graphs have
the right mechanism term, but leave the bypass state terminal and under-describe
the edge evidence.

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
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": "Completed host-dependent nutrient-acquisition causal graphs",
    "llm_assisted": True,
}

MECHANISM_EVIDENCE = {
    "reference": "ARO:3007424",
    "snippet": "Resistance via uptake of host nutrients to bypass antibiotic mechanism.",
    "notes": "CARD definition for the host-dependent nutrient-acquisition resistance mechanism.",
}

THFT_EVIDENCE = {
    "reference": "PMID:36450721",
    "snippet": (
        "Rodrigo et al. identify thfT as an ECF transporter S component that "
        "lets Group A Streptococcus import extracellular reduced folates and "
        "bypass sulfamethoxazole inhibition of folate biosynthesis."
    ),
    "notes": "Worked sulfamethoxazole/folate example for this host-nutrient bypass mechanism.",
}

DRUG_CLASS_EVIDENCE = {
    "reference": "ARO:3007426",
    "snippet": (
        "CARD relates ECF transporter S component to sulfonamide antibiotic "
        "resistance through a confers_resistance_to_drug_class assertion."
    ),
    "notes": "Sulfonamide drug-class relation asserted on ARO:3007426 and inherited by ThfT.",
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

UPTAKE_NODE = {
    "node_id": "uptake",
    "label": "host nutrient uptake",
    "node_type": "STATE",
    "description": (
        "Local state for import of a host-provided nutrient that can replace "
        "the antibiotic-blocked endogenous biosynthetic product."
    ),
}

BYPASSED_NODE = {
    "node_id": "bypassed",
    "label": "drug-blocked biosynthetic step bypassed by host nutrient",
    "node_type": "STATE",
    "description": (
        "Local state for restoring the needed metabolite from the host "
        "environment instead of relying on the biosynthetic step inhibited by "
        "the antibiotic."
    ),
}

SULFONAMIDE_NODE = {
    "node_id": "drug0",
    "label": "sulfonamide antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:3000282",
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    has_sulfonamide_relation: bool = False


TARGETS: tuple[Target, ...] = (
    Target(
        "ARO:3007425",
        "protein-s-conferring-resistance-via-host-dependent-nutrient-acquisition-aro3007425.yaml",
    ),
    Target(
        "ARO:3007426",
        "ecf-transporter-s-component-aro3007426.yaml",
        has_sulfonamide_relation=True,
    ),
    Target(
        "ARO:3007427",
        "thft-aro3007427.yaml",
        has_sulfonamide_relation=True,
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
    common_evidence = (record_evidence, MECHANISM_EVIDENCE, THFT_EVIDENCE)

    nodes = [
        _determinant_node(record),
        {
            "node_id": "mech0",
            "label": "resistance by host-dependent nutrient acquisition",
            "node_type": "MOLECULAR_FUNCTION",
            "grounding": "ARO:3007424",
        },
    ]
    if target.has_sulfonamide_relation:
        nodes.append(copy.deepcopy(SULFONAMIDE_NODE))
    nodes.extend(
        [
            copy.deepcopy(UPTAKE_NODE),
            copy.deepcopy(BYPASSED_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ]
    )

    edges = [
        _edge(
            "determinant",
            "participates in (resistance mechanism)",
            "RO:0000056",
            "mech0",
            "CARD classifies this determinant under host-dependent "
            "nutrient-acquisition resistance.",
            *common_evidence,
        ),
        _edge(
            "mech0",
            "causally upstream of",
            "RO:0002411",
            "uptake",
            "The resistance mechanism proceeds through acquisition of a host "
            "nutrient that replaces the blocked biosynthetic product.",
            MECHANISM_EVIDENCE,
            THFT_EVIDENCE,
        ),
        _edge(
            "determinant",
            "causally upstream of",
            "RO:0002411",
            "uptake",
            "This class includes proteins that enable host-nutrient uptake.",
            *common_evidence,
        ),
        _edge(
            "uptake",
            "causally upstream of",
            "RO:0002411",
            "bypassed",
            "Uptake of host nutrient makes the antibiotic-inhibited "
            "biosynthetic step dispensable.",
            MECHANISM_EVIDENCE,
            THFT_EVIDENCE,
        ),
        _edge(
            "bypassed",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            "Bypassing the drug-blocked metabolic step lets the bacterium grow "
            "despite the antibiotic.",
            *common_evidence,
        ),
        _edge(
            "determinant",
            "causally upstream of (confers resistance)",
            "RO:0002411",
            "resistance",
            "The determinant confers resistance by enabling host-nutrient "
            "uptake that bypasses the antibiotic-blocked pathway.",
            *common_evidence,
        ),
    ]
    if target.has_sulfonamide_relation:
        edges.append(
            _edge(
                "determinant",
                "confers resistance to (drug class)",
                "ARO:2000001",
                "drug0",
                "CARD asserts a sulfonamide antibiotic drug-class relation for "
                "this host-dependent nutrient-acquisition lineage.",
                record_evidence,
                DRUG_CLASS_EVIDENCE,
                THFT_EVIDENCE,
            )
        )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → host nutrient uptake → resistance",
        "description": (
            "Curated resistance-causation graph for host-dependent nutrient "
            "acquisition. The determinant is modeled as enabling uptake of a "
            "host nutrient that bypasses the antibiotic-blocked biosynthetic "
            "step rather than directly modifying the drug or its target."
        ),
        "nodes": nodes,
        "edges": edges,
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

    required = {"determinant", "mech0", "uptake", "bypassed", "resistance"}
    if target.has_sulfonamide_relation:
        required.add("drug0")
    node_ids = {
        str(node.get("node_id"))
        for node in _dicts(graphs[0].get("nodes"))
        if node.get("node_id")
    }
    missing = required - node_ids
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
        raise ValueError(f"{path}: not a host-dependent nutrient-acquisition target: {identifier}")
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
        help="ARO directory or one host-dependent nutrient-acquisition YAML file",
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
