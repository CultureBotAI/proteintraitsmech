#!/usr/bin/env python3
"""Review the broad antibiotic-inactivation enzyme ARO parent graph.

ARO:3000557 is the common parent for enzymatic antibiotic inactivation.  Its
definition supports the broad inactivation mechanism but does not select a
drug, acceptor, donor, or reaction chemistry.  This updater therefore promotes
the seeded 3-node graph as a reviewed, deliberately shallow graph.

Dry-run by default; pass ``--apply`` to write.
"""

from __future__ import annotations

import argparse
import copy
import sys
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from record_io import append_to_section, replace_block  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ARO_DIR = ROOT / "data" / "traits" / "function" / "resistance" / "aro"
IDENTIFIER = "ARO:3000557"
FILENAME = "antibiotic-inactivation-enzyme-aro3000557.yaml"

HISTORY_ACTION = "Promoted broad antibiotic-inactivation parent graph to reviewed"
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

DETERMINANT_EVIDENCE = {
    "reference": IDENTIFIER,
    "snippet": (
        "Enzyme that catalyzes the inactivation of an antibiotic resulting in "
        "resistance. Inactivation includes chemical modification, destruction, etc."
    ),
    "notes": (
        "CARD definition for the broad antibiotic-inactivation enzyme parent; no "
        "child reaction chemistry is selected at this level."
    ),
}

MECHANISM_RELATION_EVIDENCE = {
    "reference": IDENTIFIER,
    "snippet": "relationship: participates_in ARO:0001004 ! antibiotic inactivation",
    "notes": (
        "ARO mechanism relationship asserted on ARO:3000557 in data/raw/aro/aro.obo."
    ),
}

MECHANISM_EVIDENCE = {
    "reference": "ARO:0001004",
    "snippet": "Enzymatic inactivation of antibiotic to confer drug resistance.",
    "notes": "CARD definition for the broad antibiotic-inactivation mechanism.",
}

RESISTANCE_NODE = {
    "node_id": "resistance",
    "label": "antibiotic resistance phenotype",
    "node_type": "PHENOTYPE",
    "grounding": "GO:0046677",
    "description": (
        "Resistance phenotype conferred by this determinant. Grounded to the nearest "
        "available superclass: ARO models determinants and mechanisms but has no term "
        "for the resistance phenotype itself."
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


def _unique_evidence(*items: dict[str, str]) -> list[dict[str, str]]:
    evidence: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for item in items:
        key = (item["reference"], item.get("snippet", ""))
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


def _graph(record: dict[str, Any]) -> dict[str, Any]:
    common_evidence = (
        DETERMINANT_EVIDENCE,
        MECHANISM_EVIDENCE,
    )
    return {
        "graph_id": "resistance",
        "title": "antibiotic inactivation enzyme → antibiotic inactivation → resistance",
        "description": (
            "Curated broad resistance-causation graph for enzymatic antibiotic "
            "inactivation. The graph intentionally stops at the ARO antibiotic "
            "inactivation mechanism because this parent record does not identify a "
            "specific drug class or inactivation chemistry."
        ),
        "nodes": [
            {
                "node_id": "determinant",
                "label": str(record["label"]),
                "node_type": "PROTEIN",
                "grounding": str(record["identifier"]),
            },
            {
                "node_id": "mech0",
                "label": "antibiotic inactivation",
                "node_type": "MOLECULAR_FUNCTION",
                "grounding": "ARO:0001004",
            },
            RESISTANCE_NODE,
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "ARO directly classifies this enzyme parent under antibiotic inactivation.",
                DETERMINANT_EVIDENCE,
                MECHANISM_RELATION_EVIDENCE,
                MECHANISM_EVIDENCE,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "The ARO antibiotic-inactivation mechanism is defined as enzymatic inactivation of antibiotic to confer drug resistance.",
                *common_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "This broad enzyme parent confers resistance by catalyzing antibiotic inactivation.",
                *common_evidence,
            ),
        ],
    }


def enrich_record(record: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != IDENTIFIER:
        raise ValueError(f"expected {IDENTIFIER}, found {record.get('identifier')}")
    if not record.get("label"):
        raise ValueError(f"{IDENTIFIER}: missing label")
    if not record.get("definition"):
        raise ValueError(f"{IDENTIFIER}: missing definition")

    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1:
        raise ValueError(f"{IDENTIFIER}: expected exactly one draft graph")

    out = copy.deepcopy(record)
    out["mapping_status"] = "REVIEWED"
    out["causal_graphs"] = [_graph(record)]
    return out, out != record


def _replace_mapping_status(text: str, old_status: object) -> str:
    if old_status == "REVIEWED":
        return text
    before = f"mapping_status: {old_status}\n"
    after = "mapping_status: REVIEWED\n"
    if before not in text:
        raise ValueError(f"{IDENTIFIER}: cannot find mapping_status line {before.strip()!r}")
    return text.replace(before, after, 1)


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")
    if record.get("identifier") != IDENTIFIER:
        raise ValueError(f"{path}: not antibiotic inactivation enzyme: {record.get('identifier')}")
    if path.name != FILENAME:
        raise ValueError(f"{path}: {IDENTIFIER} must be in {FILENAME}")

    enriched, changed = enrich_record(record)
    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    out = _replace_mapping_status(out, record.get("mapping_status"))
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
    return [path / FILENAME]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    parser.add_argument(
        "--path",
        type=Path,
        default=ARO_DIR,
        help="ARO directory or the antibiotic inactivation enzyme YAML file",
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
