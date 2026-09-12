#!/usr/bin/env python3
"""Rewrite LRG/LUT/MAL/MBL beta-lactamase graphs.

These score-77 records still use the old beta-lactamase archetype. LRG, LUT,
and MAL are class A serine beta-lactamases; MBL is a class B
metallo-beta-lactamase.

Dry-run by default; pass ``--apply`` to write.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

import rewrite_aro_early_beta_lactamase_graphs as beta  # noqa: E402
from record_io import append_to_section, replace_block  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ARO_DIR = ROOT / "data" / "traits" / "function" / "resistance" / "aro"

HISTORY_ACTION = "Completed LRG/LUT/MAL/MBL beta-lactamase graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-09T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

TARGETS = (
    beta.Target("ARO:3006941", "lrg-1-aro3006941.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3005419", "lrg-beta-lactamase-aro3005419.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3006943", "lut-1-aro3006943.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3006944", "lut-2-aro3006944.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3006945", "lut-3-aro3006945.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3006946", "lut-4-aro3006946.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3006947", "lut-5-aro3006947.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3006948", "lut-6-aro3006948.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3005421", "lut-beta-lactamase-aro3005421.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3006949", "mal-1-aro3006949.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3006950", "mal-2-aro3006950.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3005422", "mal-beta-lactamase-aro3005422.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3005423", "mbl-beta-lactamase-aro3005423.yaml", beta.GraphKind.METALLO),
    beta.Target("ARO:3006951", "mbl1b-aro3006951.yaml", beta.GraphKind.METALLO),
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


def enrich_record(
    record: dict[str, Any],
    target: beta.Target,
) -> tuple[dict[str, Any], bool]:
    return beta.enrich_record(record, target)


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not an LRG/LUT/MAL/MBL beta-lactamase target: {identifier}")
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
        help="ARO directory or one LRG/LUT/MAL/MBL beta-lactamase YAML file",
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
