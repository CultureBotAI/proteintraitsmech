#!/usr/bin/env python3
"""Complete EF-Tu child graphs with inherited conservative EF-Tu evidence.

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

HISTORY_ACTION = "Completed EF-Tu child resistance graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

EF_TU_PARENT_EVIDENCE = {
    "reference": "ARO:3003356",
    "snippet": (
        "Sequence variants of elongation factor Tu that confer resistance to "
        "different classes of antibiotics."
    ),
    "notes": "CARD definition for antibiotic-resistant EF-Tu.",
}

ELFAMYCIN_EF_TU_EVIDENCE = {
    "reference": "ARO:3001312",
    "snippet": (
        "Sequence variants of elongation factor Tu that confer resistance to "
        "elfamycin antibiotics."
    ),
    "notes": "CARD definition for elfamycin-resistant EF-Tu.",
}

MUTATION_EVIDENCE = {
    "reference": "ARO:3000212",
    "snippet": (
        "Point mutations in the DNA may lead to an altered gene product that "
        "may result in antibiotic resistance."
    ),
    "notes": "CARD definition for mutation conferring antibiotic resistance.",
}

ELFAMYCIN_RELATION_EVIDENCE = {
    "reference": "ARO:3001312",
    "snippet": "relationship: confers_resistance_to_drug_class ARO:3001219 ! elfamycin antibiotic",
}

EF_ACTIVITY_EVIDENCE = {
    "reference": "GO:0003746",
    "snippet": "translation elongation factor activity",
    "notes": "GO molecular-function term used for EF-Tu activity.",
}

ELONGATION_EVIDENCE = {
    "reference": "GO:0006414",
    "snippet": "translational elongation",
    "notes": "GO biological-process term for the pathway served by EF-Tu.",
}

EDGE_DESCRIPTIONS = {
    (
        "determinant",
        "participates in (resistance mechanism)",
        "mech0",
    ): "CARD classifies EF-Tu sequence variants under mutation-conferring antibiotic resistance.",
    (
        "mech0",
        "causally upstream of",
        "resistance",
    ): "The inherited mutation mechanism captures EF-Tu sequence variation that confers resistance.",
    (
        "determinant",
        "causally upstream of (confers resistance)",
        "resistance",
    ): "CARD asserts that the modeled EF-Tu sequence variants confer resistance.",
    (
        "determinant",
        "confers resistance to (drug class)",
        "drug0",
    ): "CARD asserts inherited elfamycin-antibiotic resistance on elfamycin-resistant EF-Tu.",
    (
        "determinant",
        "enables (elongation factor activity)",
        "ef_activity",
    ): "EF-Tu is a translation elongation factor.",
    (
        "ef_activity",
        "part of (translational elongation)",
        "elongation",
    ): "EF-Tu activity participates in translational elongation.",
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str

    @property
    def drug_notes(self) -> str:
        if self.identifier == "ARO:3001312":
            return (
                "Asserted directly on ARO:3001312 (elfamycin resistant EF-Tu) in the "
                "CARD/ARO release in data/raw/aro/aro.obo."
            )
        return (
            "Asserted on ARO:3001312 (elfamycin resistant EF-Tu), an is_a ancestor "
            f"of this record's {self.identifier}; inherited by this variant. "
            "CARD/ARO release in data/raw/aro/aro.obo."
        )


TARGETS: tuple[Target, ...] = (
    Target(
        "ARO:3003357",
        "clostridioides-difficile-ef-tu-mutants-conferring-resistance-to-elfamycin-"
        "aro3003357.yaml",
    ),
    Target("ARO:3001312", "elfamycin-resistant-ef-tu-aro3001312.yaml"),
    Target(
        "ARO:3003875",
        "enterococcus-faecium-ef-tu-mutants-conferring-resistance-to-elfamycin-"
        "aro3003875.yaml",
    ),
    Target(
        "ARO:3003438",
        "enterococcus-faecium-ef-tu-mutants-conferring-resistance-to-ge2270a-"
        "aro3003438.yaml",
    ),
    Target(
        "ARO:3003358",
        "escherichia-coli-ef-tu-mutants-conferring-resistance-to-elfamycin-"
        "aro3003358.yaml",
    ),
    Target(
        "ARO:3003370",
        "escherichia-coli-ef-tu-mutants-conferring-resistance-to-enacyloxin-iia-"
        "aro3003370.yaml",
    ),
    Target(
        "ARO:3003368",
        "escherichia-coli-ef-tu-mutants-conferring-resistance-to-kirromycin-"
        "aro3003368.yaml",
    ),
    Target(
        "ARO:3003369",
        "escherichia-coli-ef-tu-mutants-conferring-resistance-to-pulvomycin-"
        "aro3003369.yaml",
    ),
    Target(
        "ARO:3003360",
        "planobispora-rosea-ef-tu-mutants-conferring-resistance-to-elfamycin-"
        "aro3003360.yaml",
    ),
    Target(
        "ARO:3003361",
        "planobispora-rosea-ef-tu-mutants-conferring-resistance-to-inhibitor-ge2270a-"
        "aro3003361.yaml",
    ),
    Target(
        "ARO:3003359",
        "streptomyces-cinnamoneus-ef-tu-mutants-conferring-resistance-to-elfamycin-"
        "aro3003359.yaml",
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
    elfamycin_relation = {**ELFAMYCIN_RELATION_EVIDENCE, "notes": target.drug_notes}

    match key:
        case ("determinant", "participates in (resistance mechanism)", "mech0"):
            extra = [record_evidence, EF_TU_PARENT_EVIDENCE, ELFAMYCIN_EF_TU_EVIDENCE, MUTATION_EVIDENCE]
        case ("mech0", "causally upstream of", "resistance"):
            extra = [record_evidence, EF_TU_PARENT_EVIDENCE, ELFAMYCIN_EF_TU_EVIDENCE, MUTATION_EVIDENCE]
        case ("determinant", "causally upstream of (confers resistance)", "resistance"):
            extra = [record_evidence, EF_TU_PARENT_EVIDENCE, ELFAMYCIN_EF_TU_EVIDENCE, MUTATION_EVIDENCE]
        case ("determinant", "confers resistance to (drug class)", "drug0"):
            extra = [
                elfamycin_relation,
                record_evidence,
                ELFAMYCIN_EF_TU_EVIDENCE,
                EF_TU_PARENT_EVIDENCE,
            ]
        case ("determinant", "enables (elongation factor activity)", "ef_activity"):
            extra = [record_evidence, EF_TU_PARENT_EVIDENCE, EF_ACTIVITY_EVIDENCE]
        case ("ef_activity", "part of (translational elongation)", "elongation"):
            extra = [
                EF_TU_PARENT_EVIDENCE,
                record_evidence,
                EF_ACTIVITY_EVIDENCE,
                ELONGATION_EVIDENCE,
            ]
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
    graph["title"] = f"{record['label']} → EF-Tu sequence variation → elfamycin resistance"
    graph["description"] = (
        "Curated resistance-causation graph for EF-Tu sequence variants that "
        "confer elfamycin-class resistance. The graph preserves CARD's "
        "inherited drug-class assertion and EF-Tu translation role without "
        "claiming one uncited drug-binding mechanism for all EF-Tu children."
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
        raise ValueError(f"{path}: not an EF-Tu child target: {identifier}")
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
        help="ARO directory or one EF-Tu child target YAML file",
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
