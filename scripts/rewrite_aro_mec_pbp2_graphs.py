#!/usr/bin/env python3
"""Rewrite mec/methicillin-resistant PBP2 causal graphs.

The score-80 mecA/mecB/mecC/mecD/methicillin-resistant-PBP2 graphs already use
the intended beta-lactam target-replacement topology.  This pass keeps that
shape and completes missing edge descriptions and multi-reference evidence.

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
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": "Completed methicillin-resistant PBP2 target-replacement graphs",
    "llm_assisted": True,
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str


TARGETS: tuple[Target, ...] = (
    Target("ARO:3000617", "meca-aro3000617.yaml"),
    Target("ARO:3003440", "mecb-aro3003440.yaml"),
    Target("ARO:3001209", "mecc-aro3001209.yaml"),
    Target("ARO:3004185", "mecd-aro3004185.yaml"),
    Target("ARO:3001208", "methicillin-resistant-pbp2-aro3001208.yaml"),
)
TARGET_BY_ID = {target.identifier: target for target in TARGETS}

EXPECTED_EDGE_KEYS = {
    ("determinant", "mech0"),
    ("mech0", "resistance"),
    ("determinant", "resistance"),
    ("determinant", "drug0"),
    ("determinant", "pbp2a_activity"),
    ("low_affinity", "pbp2a_activity"),
    ("determinant", "low_affinity"),
    ("pbp2a_activity", "pg_synth"),
}

TARGET_REPLACEMENT_EVIDENCE = {
    "reference": "ARO:0001002",
    "snippet": (
        "Replacement or substitution of antibiotic action target, which process "
        "will result in antibiotic resistance."
    ),
    "notes": "CARD definition for antibiotic target replacement.",
}

TARGET_REPLACEMENT_PROTEIN_EVIDENCE = {
    "reference": "ARO:3000381",
    "snippet": (
        "Alternate proteins that have the same functions as other antibiotic "
        "target proteins, but are structurally different and thus resistant to "
        "antibiotics. These can replace the activity of other "
        "antibiotic-sensitive proteins in the presence of antibiotics."
    ),
    "notes": "CARD definition for antibiotic target replacement proteins.",
}

METHICILLIN_PBP2_EVIDENCE = {
    "reference": "ARO:3001208",
    "snippet": (
        "In methicillin sensitive S. aureus (MSSA), beta-lactams bind to native "
        "penicillin-binding proteins (PBPs) and disrupt synthesis of the cell "
        "membrane's peptidoglycan layer. In methicillin resistant S. aureus "
        "(MRSA), foreign PBP2a acquired by lateral gene transfer is able to "
        "perform peptidoglycan synthesis in the presence of beta-lactams."
    ),
    "notes": "CARD definition for methicillin resistant PBP2.",
}

MECA_EVIDENCE = {
    "reference": "ARO:3000617",
    "snippet": (
        "A foreign PBP2a acquired by lateral gene transfer that is able to "
        "perform peptidoglycan synthesis in the presence of beta-lactams."
    ),
    "notes": "CARD definition for mecA/PBP2a.",
}

LOW_AFFINITY_EVIDENCE = {
    "reference": "PMID:3499861",
    "snippet": (
        "All strains produced penicillin-binding protein 2' (PBP 2'), which has "
        "been associated with methicillin resistance and which has very low "
        "affinity for beta-lactam antibiotics."
    ),
    "notes": "Ueda et al. 1987, showing very low beta-lactam affinity of PBP 2'.",
}

PBP2A_PRESENCE_EVIDENCE = {
    "reference": "PMID:6563036",
    "snippet": (
        "We detected a high-molecular-weight PBP (PBP-2a; approximate size, "
        "78,000 daltons) that was only present in the resistant bacteria but not "
        "in the isogenic susceptible strains."
    ),
    "notes": (
        "Hartman and Tomasz 1984, associating PBP2a with otherwise isogenic "
        "methicillin-resistant bacteria."
    ),
}

EDGE_DESCRIPTIONS = {
    ("determinant", "mech0"): (
        "CARD classifies this acquired PBP under antibiotic target replacement."
    ),
    ("mech0", "resistance"): (
        "Target replacement provides an alternate low-affinity PBP that sustains "
        "cell-wall synthesis when beta-lactams inhibit native PBPs."
    ),
    ("determinant", "resistance"): (
        "The determinant encodes an acquired PBP that performs peptidoglycan "
        "synthesis in the presence of beta-lactams."
    ),
    ("determinant", "drug0"): (
        "CARD asserts that methicillin-resistant PBP2 determinants confer "
        "resistance to penicillin beta-lactams."
    ),
    ("determinant", "pbp2a_activity"): (
        "The acquired PBP performs peptidoglycan cross-linking under "
        "beta-lactam exposure."
    ),
    ("low_affinity", "pbp2a_activity"): (
        "Low beta-lactam affinity leaves the acquired PBP enzymatically active "
        "when native PBPs are inhibited."
    ),
    ("determinant", "low_affinity"): (
        "The determinant encodes an acquired PBP with low affinity for "
        "beta-lactam antibiotics."
    ),
    ("pbp2a_activity", "pg_synth"): (
        "The acquired PBP activity directly supports peptidoglycan synthesis."
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


def record_evidence(record: dict[str, Any]) -> dict[str, str]:
    return {
        "reference": str(record["identifier"]),
        "snippet": " ".join(str(record.get("definition", "")).split()),
        "notes": f"CARD definition for {record['label']}.",
    }


def fresh_evidence(items: list[dict[str, str]]) -> list[dict[str, str]]:
    return [copy.deepcopy(item) for item in items]


def unique_evidence(items: list[dict[str, str]]) -> list[dict[str, str]]:
    evidence = []
    seen = set()
    for item in items:
        marker = (item.get("reference"), item.get("snippet"))
        if marker in seen:
            continue
        seen.add(marker)
        evidence.append(item)
    return evidence


def evidence_for_edge(key: tuple[str, str], target_evidence: dict[str, str]) -> list[dict[str, str]]:
    mechanism_evidence = [
        target_evidence,
        TARGET_REPLACEMENT_EVIDENCE,
        TARGET_REPLACEMENT_PROTEIN_EVIDENCE,
        METHICILLIN_PBP2_EVIDENCE,
        MECA_EVIDENCE,
    ]
    match key:
        case ("determinant", "mech0"):
            return mechanism_evidence
        case ("mech0", "resistance"):
            return mechanism_evidence
        case ("determinant", "resistance"):
            return [*mechanism_evidence, LOW_AFFINITY_EVIDENCE, PBP2A_PRESENCE_EVIDENCE]
        case ("determinant", "drug0"):
            return [*mechanism_evidence, LOW_AFFINITY_EVIDENCE]
        case ("determinant", "pbp2a_activity"):
            return [*mechanism_evidence, LOW_AFFINITY_EVIDENCE]
        case ("low_affinity", "pbp2a_activity"):
            return [LOW_AFFINITY_EVIDENCE, *mechanism_evidence]
        case ("determinant", "low_affinity"):
            return [LOW_AFFINITY_EVIDENCE, PBP2A_PRESENCE_EVIDENCE, *mechanism_evidence]
        case ("pbp2a_activity", "pg_synth"):
            return [*mechanism_evidence, LOW_AFFINITY_EVIDENCE]
        case _:
            raise ValueError(f"unexpected edge {key}")


def enrich_graph(graph: dict[str, Any], record: dict[str, Any]) -> dict[str, Any]:
    graph = copy.deepcopy(graph)
    graph["title"] = f"{record['label']} → methicillin-resistant PBP target replacement"
    graph["description"] = (
        "Curated resistance-causation graph for mec/methicillin-resistant PBP2 "
        "target-replacement determinants. The determinant encodes an acquired "
        "low-affinity PBP that replaces beta-lactam-sensitive native PBPs and "
        "sustains peptidoglycan biosynthesis under drug exposure."
    )

    for node in graph["nodes"]:
        if node["node_id"] == "pbp2a_activity":
            node["description"] = (
                "Grounded to penicillin binding, the low-affinity acquired-PBP "
                "activity assayed by these papers."
            )
        elif node["node_id"] == "low_affinity":
            node["description"] = (
                "The causal core: the acquired PBP has low affinity for "
                "beta-lactams and therefore keeps functioning when the drug "
                "inhibits native PBPs."
            )

    keys = {(edge["subject"], edge["object"]) for edge in graph["edges"]}
    if keys != EXPECTED_EDGE_KEYS:
        raise ValueError(f"expected edge keys {sorted(EXPECTED_EDGE_KEYS)}, got {sorted(keys)}")

    target_evidence = record_evidence(record)
    for edge in graph["edges"]:
        key = (edge["subject"], edge["object"])
        edge["description"] = EDGE_DESCRIPTIONS[key]
        edge["evidence"] = fresh_evidence(
            unique_evidence([*edge.get("evidence", []), *evidence_for_edge(key, target_evidence)])
        )

    return graph


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not a mec/PBP2 target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    graphs = record.get("causal_graphs")
    if not isinstance(graphs, list) or len(graphs) != 1:
        raise ValueError(f"{path}: expected exactly one causal graph")

    enriched_graph = enrich_graph(graphs[0], record)
    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": [enriched_graph]}))
    changed = out != text
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
        help="ARO directory or one of the mec/PBP2 YAML files",
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
        except (KeyError, OSError, ValueError, yaml.YAMLError) as exc:
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
