#!/usr/bin/env python3
"""Rewrite the spd ANT(9) aminoglycoside nucleotidyltransferase graph.

spd is a child of ANT(9)-I and still has the old promoted aminoglycoside
nucleotidyltransferase graph.  Reuse the canonical ATP-dependent
adenylylation model used for aad and the remaining ANT group records.

Dry-run by default; pass ``--apply`` to write.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

import rewrite_aro_aad_graphs as aad  # noqa: E402

ARO_DIR = aad.ARO_DIR

HISTORY_ACTION = "Completed spd aminoglycoside nucleotidyltransferase graph"
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


TARGETS: tuple[Target, ...] = (Target("ARO:3002631", "spd-aro3002631.yaml"),)
TARGET_BY_ID = {target.identifier: target for target in TARGETS}


def enrich_record(record: dict, target: Target) -> tuple[dict, bool]:
    aad_target = aad.Target(target.identifier, target.filename)
    enriched, _ = aad.enrich_record(record, aad_target)
    _ground_adenylylated_state(enriched)
    return enriched, enriched != record


def _ground_adenylylated_state(record: dict) -> None:
    graph = record["causal_graphs"][0]
    for node in graph["nodes"]:
        if node["node_id"] != "adenylylated":
            continue
        node["grounding"] = "ARO:0000016"
        node["description"] = (
            "Local state for an aminoglycoside antibiotic after ANT-mediated "
            "AMP transfer from ATP. Grounded to the broad ARO aminoglycoside "
            "antibiotic class because no stable narrow term is available for "
            "this adenylylated inactive state."
        )
        return
    raise ValueError(f"{record['identifier']}: generated graph missing adenylylated node")


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not an spd target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
    out = aad.replace_block(
        text,
        "causal_graphs",
        aad._dump({"causal_graphs": enriched["causal_graphs"]}),
    )
    if HISTORY_ACTION not in out:
        out = aad.append_to_section(
            out,
            "curation_history",
            aad._dump({"curation_history": [HISTORY_EVENT]}),
        )
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
        help="ARO directory or the spd YAML file",
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
