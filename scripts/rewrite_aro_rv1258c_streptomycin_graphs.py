#!/usr/bin/env python3
"""Complete streptomycin-specific Rv1258c Tap-efflux graphs.

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

HISTORY_ACTION = "Completed streptomycin-specific Rv1258c graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

RV1258C_EVIDENCE = {
    "reference": "ARO:3007183",
    "snippet": "Mutations in the Rv1258c (Tap) efflux pump contributing to antibiotic resistance.",
    "notes": "CARD definition for antibiotic-resistant Rv1258c.",
}

MUTATION_EVIDENCE = {
    "reference": "ARO:3000212",
    "snippet": (
        "Point mutations in the DNA may lead to an altered gene product that "
        "may result in antibiotic resistance."
    ),
    "notes": "CARD definition for mutation conferring antibiotic resistance.",
}

EFFLUX_EVIDENCE = {
    "reference": "ARO:0010000",
    "snippet": "Antibiotic resistance via the transport of antibiotics out of the cell.",
    "notes": "CARD definition for the antibiotic efflux resistance mechanism.",
}

DRUG_RELATION_EVIDENCE = {
    "reference": "ARO:3004970",
    "snippet": "relationship: confers_resistance_to_drug_class ARO:0000016 ! aminoglycoside antibiotic",
}

EDGE_DESCRIPTIONS = {
    (
        "determinant",
        "participates in (resistance mechanism)",
        "mech0",
    ): "CARD classifies streptomycin-resistant Rv1258c under mutation-conferring resistance.",
    (
        "mech0",
        "causally upstream of",
        "resistance",
    ): "Tap efflux-pump mutations are the asserted cause of streptomycin resistance.",
    (
        "determinant",
        "causally upstream of (confers resistance)",
        "resistance",
    ): "Rv1258c mutations contribute to aminoglycoside resistance through Tap efflux.",
    (
        "determinant",
        "confers resistance to (drug class)",
        "drug0",
    ): "CARD asserts aminoglycoside-antibiotic resistance on streptomycin-resistant Rv1258c.",
    (
        "determinant",
        "participates in (antibiotic efflux)",
        "efflux_process",
    ): "The Rv1258c determinant is a mutant of the Tap efflux pump.",
    (
        "efflux_process",
        "causally upstream of (confers resistance)",
        "resistance",
    ): "Antibiotic efflux lowers intracellular antibiotic exposure and can produce resistance.",
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    drug_notes: str


TARGETS = (
    Target(
        "ARO:3004970",
        "streptomycin-resistant-rv1258c-aro3004970.yaml",
        (
            "Asserted directly on ARO:3004970 (streptomycin resistant Rv1258c) in the "
            "CARD/ARO release in data/raw/aro/aro.obo."
        ),
    ),
    Target(
        "ARO:3004971",
        "mycobacterium-tuberculosis-rv1258c-mutations-confer-resistance-to-streptomycin-"
        "aro3004971.yaml",
        (
            "Asserted on ARO:3004970 (streptomycin resistant Rv1258c), an is_a "
            "ancestor of this record's ARO:3004971; inherited by this variant. "
            "CARD/ARO release in data/raw/aro/aro.obo."
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


def _dicts(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _unique_evidence(*items: dict[str, str]) -> list[dict[str, str]]:
    evidence: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for item in items:
        marker = (item["reference"], item["snippet"])
        if marker in seen:
            continue
        seen.add(marker)
        evidence.append(copy.deepcopy(item))
    return evidence


def _record_evidence(record: dict[str, Any]) -> dict[str, str]:
    return {
        "reference": str(record["identifier"]),
        "snippet": str(record["definition"]),
        "notes": f"CARD definition for {record['label']}.",
    }


def _evidence_for_edge(
    key: tuple[str, str, str],
    existing: list[dict[str, str]],
    record: dict[str, Any],
    target: Target,
) -> list[dict[str, str]]:
    record_evidence = _record_evidence(record)
    drug_relation = {**DRUG_RELATION_EVIDENCE, "notes": target.drug_notes}

    match key:
        case ("determinant", "participates in (resistance mechanism)", "mech0"):
            extra = [record_evidence, RV1258C_EVIDENCE, MUTATION_EVIDENCE, EFFLUX_EVIDENCE]
        case ("mech0", "causally upstream of", "resistance"):
            extra = [record_evidence, RV1258C_EVIDENCE, MUTATION_EVIDENCE, EFFLUX_EVIDENCE]
        case ("determinant", "causally upstream of (confers resistance)", "resistance"):
            extra = [record_evidence, RV1258C_EVIDENCE, MUTATION_EVIDENCE, EFFLUX_EVIDENCE]
        case ("determinant", "confers resistance to (drug class)", "drug0"):
            extra = [drug_relation, record_evidence, RV1258C_EVIDENCE]
        case ("determinant", "participates in (antibiotic efflux)", "efflux_process"):
            extra = [record_evidence, RV1258C_EVIDENCE, EFFLUX_EVIDENCE]
        case ("efflux_process", "causally upstream of (confers resistance)", "resistance"):
            extra = [EFFLUX_EVIDENCE, record_evidence, RV1258C_EVIDENCE]
        case _:
            raise ValueError(f"unexpected edge {key}")
    return _unique_evidence(*existing, *extra)


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != target.identifier:
        raise ValueError(
            f"{target.filename}: expected {target.identifier}, found {record.get('identifier')}"
        )

    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1 or graphs[0].get("graph_id") != "resistance":
        raise ValueError(f"{target.identifier}: expected exactly one resistance graph")

    out = copy.deepcopy(record)
    graph = copy.deepcopy(out["causal_graphs"][0])
    graph["title"] = f"{record['label']} → Tap-mediated antibiotic efflux → resistance"
    graph["description"] = (
        "Curated resistance-causation graph for streptomycin-linked Rv1258c "
        "variants. The graph records the Tap efflux-pump claim and the "
        "inherited aminoglycoside-antibiotic resistance assertion without "
        "inventing a specific coupling ion or energy source."
    )

    seen: set[tuple[str, str, str]] = set()
    for edge in _dicts(graph.get("edges")):
        key = (
            str(edge.get("subject")),
            str(edge.get("predicate")),
            str(edge.get("object")),
        )
        edge["description"] = EDGE_DESCRIPTIONS[key]
        edge["evidence"] = _evidence_for_edge(key, _dicts(edge.get("evidence")), record, target)
        seen.add(key)

    missing = sorted(set(EDGE_DESCRIPTIONS) - seen)
    if missing:
        raise ValueError(f"{target.identifier}: missing edge(s): {missing}")

    out["causal_graphs"] = [graph]
    return out, out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not an Rv1258c streptomycin target: {identifier}")
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
        help="ARO directory or a streptomycin-specific Rv1258c target YAML file",
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
