#!/usr/bin/env python3
"""Rewrite species-specific 23S rRNA macrolide-resistance ARO graphs.

These ARO terms are children of ARO:3004125 and inherit the same causal shape:

    mutated 23S rRNA -> reduced macrolide binding at a 23S site -> resistance

The existing records carried the older, ungrounded ``pt_loop`` and
``conformation`` local nodes.  This updater mirrors the curated ARO:3004125
graph while preserving each species-specific ARO definition and ARO citation
list as child-record evidence.

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
from rewrite_aro_23s_macrolide_rrna_graph import (  # noqa: E402
    ALTERED_SITE_NODE,
    BINDING_SITE_NODE,
    DOUTHWAITE_EVIDENCE,
    LOOP_BINDING_EVIDENCE,
    MACROLIDE_NODE,
    MECHANISM_NODE,
    MUTATION_EVIDENCE,
    RESISTANCE_NODE,
    RRNA_EVIDENCE,
    RRNA_PARENT_EVIDENCE,
    SUBUNIT_NODE,
)

ROOT = Path(__file__).resolve().parent.parent
ARO_DIR = ROOT / "data" / "traits" / "function" / "resistance" / "aro"

HISTORY_ACTION = "Completed species-specific 23S rRNA macrolide-resistance mutation graph"
HISTORY_CURATOR = "codex-causal-graph-quality"
HISTORY_EVENT = {
    "timestamp": "2026-09-09T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

MACROLIDE_23S_PARENT_EVIDENCE = {
    "reference": "ARO:3004125",
    "snippet": (
        "Nucleotide point mutations in the 23S rRNA subunit may confer "
        "resistance to macrolide antibiotics."
    ),
    "notes": "CARD definition for 23S rRNA with mutation conferring resistance to macrolide antibiotics.",
}

INHERITED_MACROLIDE_RELATION_EVIDENCE = {
    "reference": "ARO:3004125",
    "snippet": "relationship: confers_resistance_to_drug_class ARO:0000000 ! macrolide antibiotic",
    "notes": (
        "Macrolide drug-class relation asserted on ARO:3004125 and inherited "
        "by its species-specific child records."
    ),
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str


TARGETS: tuple[Target, ...] = (
    Target(
        "ARO:3004133",
        "brachyspira-hyodysenteriae-23s-rrna-with-mutation-conferring-resistance-to-tylos-"
        "aro3004133.yaml",
    ),
    Target(
        "ARO:3004546",
        "campylobacter-jejuni-23s-rrna-with-mutation-conferring-resistance-to-erythromyci-"
        "aro3004546.yaml",
    ),
    Target(
        "ARO:3004174",
        "chlamydia-trachomatis-23s-rrna-with-mutation-conferring-resistance-to-macrolide--"
        "aro3004174.yaml",
    ),
    Target(
        "ARO:3004132",
        "chlamydomonas-reinhardtii-23s-rrna-with-mutation-conferring-resistance-to-erythr-"
        "aro3004132.yaml",
    ),
    Target(
        "ARO:3004654",
        "clostridioides-difficile-23s-rrna-with-mutation-conferring-resistance-to-erythro-"
        "aro3004654.yaml",
    ),
    Target(
        "ARO:3004160",
        "escherichia-coli-23s-rrna-with-mutation-conferring-resistance-to-clarithromycin-"
        "aro3004160.yaml",
    ),
    Target(
        "ARO:3004131",
        "escherichia-coli-23s-rrna-with-mutation-conferring-resistance-to-erythromycin-an-"
        "aro3004131.yaml",
    ),
    Target(
        "ARO:3004134",
        "helicobacter-pylori-23s-rrna-with-mutation-conferring-resistance-to-clarithromyc-"
        "aro3004134.yaml",
    ),
    Target(
        "ARO:3004138",
        "moraxella-catarrhalis-23s-rrna-with-mutation-conferring-resistance-to-macrolide--"
        "aro3004138.yaml",
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


def _unique_evidence(*groups: list[dict[str, str]]) -> list[dict[str, str]]:
    evidence: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for group in groups:
        for item in group:
            key = (
                str(item["reference"]),
                str(item.get("snippet", "")),
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
    *evidence_groups: list[dict[str, str]],
) -> dict[str, Any]:
    return {
        "subject": subject,
        "predicate": predicate,
        "predicate_id": predicate_id,
        "object": object_,
        "description": description,
        "evidence": _unique_evidence(*evidence_groups),
    }


def _record_evidence(record: dict[str, Any]) -> list[dict[str, str]]:
    evidence = [
        {
            "reference": str(record["identifier"]),
            "snippet": str(record["definition"]),
            "notes": f"CARD definition for {record['label']}.",
        }
    ]
    for item in _dicts(record.get("evidence")):
        if not item.get("reference"):
            continue
        entry = {"reference": str(item["reference"])}
        if item.get("snippet"):
            entry["snippet"] = str(item["snippet"])
        if item.get("notes"):
            entry["notes"] = str(item["notes"])
        evidence.append(entry)
    return evidence


def _graph(record: dict[str, Any]) -> dict[str, Any]:
    record_evidence = _record_evidence(record)
    mutation_evidence = [
        record_evidence,
        [MACROLIDE_23S_PARENT_EVIDENCE],
        [RRNA_PARENT_EVIDENCE],
        [MUTATION_EVIDENCE],
    ]
    site_evidence = [
        record_evidence,
        [MACROLIDE_23S_PARENT_EVIDENCE],
        [RRNA_PARENT_EVIDENCE],
        [RRNA_EVIDENCE],
        [DOUTHWAITE_EVIDENCE],
        [LOOP_BINDING_EVIDENCE],
    ]
    drug_evidence = [
        record_evidence,
        [INHERITED_MACROLIDE_RELATION_EVIDENCE],
        [DOUTHWAITE_EVIDENCE],
        [LOOP_BINDING_EVIDENCE],
    ]

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → reduced 23S macrolide binding",
        "description": (
            "Curated resistance-causation graph for a species-specific 23S "
            "rRNA point-mutation determinant that inherits the macrolide "
            "23S rRNA parent mechanism: reduced macrolide binding at the "
            "peptidyl-transferase loop, followed by macrolide resistance."
        ),
        "nodes": [
            {
                "node_id": "determinant",
                "label": str(record["label"]),
                "node_type": "NUCLEIC_ACID",
                "grounding": str(record["identifier"]),
            },
            copy.deepcopy(MECHANISM_NODE),
            copy.deepcopy(MACROLIDE_NODE),
            copy.deepcopy(BINDING_SITE_NODE),
            copy.deepcopy(ALTERED_SITE_NODE),
            copy.deepcopy(SUBUNIT_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "The species-specific ARO term inherits classification under "
                "mutation conferring antibiotic resistance.",
                *mutation_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "The inherited mutation mechanism captures 23S rRNA sequence "
                "changes that reduce macrolide binding.",
                *mutation_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "The species-specific 23S rRNA point mutation confers macrolide "
                "resistance through the inherited reduced-binding mechanism.",
                *mutation_evidence,
                [LOOP_BINDING_EVIDENCE],
            ),
            _edge(
                "determinant",
                "confers resistance to (drug class)",
                "ARO:2000001",
                "drug0",
                "The species-specific ARO child inherits a macrolide-antibiotic "
                "drug-class relation from ARO:3004125.",
                *drug_evidence,
            ),
            _edge(
                "binding_site",
                "part of",
                "BFO:0000050",
                "determinant",
                "The macrolide-binding peptidyl-transferase loop is modeled "
                "inside the mutated 23S rRNA.",
                *site_evidence,
            ),
            _edge(
                "determinant",
                "part of",
                "BFO:0000050",
                "subunit",
                "The mutated 23S rRNA is part of the bacterial or "
                "chloroplast-type 50S ribosomal subunit.",
                record_evidence,
                [RRNA_PARENT_EVIDENCE],
                [RRNA_EVIDENCE],
            ),
            _edge(
                "drug0",
                "molecularly interacts with (binds the 23S rRNA site)",
                "RO:0002436",
                "binding_site",
                "Macrolides bind at the peptidyl-transferase loop of 23S rRNA.",
                *drug_evidence,
                [RRNA_EVIDENCE],
            ),
            _edge(
                "determinant",
                "causally upstream of (alters macrolide binding)",
                "RO:0002411",
                "altered_site",
                "Point mutations in the 23S rRNA peptidyl-transferase loop "
                "produce a local state with reduced macrolide binding.",
                *site_evidence,
            ),
            _edge(
                "altered_site",
                "negatively regulates (reduces macrolide binding)",
                "RO:0002212",
                "binding_site",
                "The altered 23S rRNA loop reduces macrolide binding affinity "
                "at the site.",
                *site_evidence,
            ),
            _edge(
                "altered_site",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Reduced binding at the mutated 23S rRNA site is the terminal "
                "modeled cause of macrolide resistance.",
                *site_evidence,
            ),
        ],
    }


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != target.identifier:
        msg = f"expected {target.identifier}, found {record.get('identifier')}"
        raise ValueError(msg)
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
    missing = {"determinant", "mech0", "drug0", "resistance"} - node_ids
    if missing:
        missing_ids = ", ".join(sorted(missing))
        raise ValueError(f"{target.identifier}: missing node(s): {missing_ids}")

    out = copy.deepcopy(record)
    out["causal_graphs"] = [_graph(record)]
    return out, out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = str(record.get("identifier"))
    try:
        target = TARGET_BY_ID[identifier]
    except KeyError as exc:
        raise ValueError(f"{path}: not a species-specific 23S macrolide rRNA target") from exc
    if path.name != target.filename:
        raise ValueError(f"{path}: target must be in {target.filename}")

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
        help="ARO directory or an exact species-specific 23S macrolide rRNA YAML file",
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
