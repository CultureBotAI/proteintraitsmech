#!/usr/bin/env python3
"""Rewrite BUT/CAR/CARB beta-lactamase graphs.

This exact score-77 slice contains BUT class C serine beta-lactamases, CAR
class B metallo-beta-lactamases, and the large CARB class A serine
beta-lactamase family. It reuses the canonical beta-lactamase graph builder
for all three enzyme classes.

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

HISTORY_ACTION = "Completed BUT-CARB beta-lactamase graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-08T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}


_TARGET_ROWS = """
CLASS_C ARO:3004293 but-beta-lactamase-aro3004293.yaml
CLASS_C ARO:3004294 but-1-aro3004294.yaml
CLASS_C ARO:3005558 but-2-aro3005558.yaml
METALLO ARO:3005395 car-beta-lactamase-aro3005395.yaml
METALLO ARO:3006903 car-1-aro3006903.yaml
CLASS_A ARO:3000091 carb-beta-lactamase-aro3000091.yaml
CLASS_A ARO:3002240 carb-1-aro3002240.yaml
CLASS_A ARO:3002241 carb-2-aro3002241.yaml
CLASS_A ARO:3002242 carb-3-aro3002242.yaml
CLASS_A ARO:3002243 carb-4-aro3002243.yaml
CLASS_A ARO:3002244 carb-5-aro3002244.yaml
CLASS_A ARO:3002245 carb-6-aro3002245.yaml
CLASS_A ARO:3002246 carb-7-aro3002246.yaml
CLASS_A ARO:3002247 carb-8-aro3002247.yaml
CLASS_A ARO:3002248 carb-9-aro3002248.yaml
CLASS_A ARO:3002249 carb-10-aro3002249.yaml
CLASS_A ARO:3005559 carb-11-aro3005559.yaml
CLASS_A ARO:3002250 carb-12-aro3002250.yaml
CLASS_A ARO:3002251 carb-13-aro3002251.yaml
CLASS_A ARO:3002252 carb-14-aro3002252.yaml
CLASS_A ARO:3002253 carb-15-aro3002253.yaml
CLASS_A ARO:3002255 carb-16-aro3002255.yaml
CLASS_A ARO:3002254 carb-17-aro3002254.yaml
CLASS_A ARO:3003174 carb-18-aro3003174.yaml
CLASS_A ARO:3003175 carb-19-aro3003175.yaml
CLASS_A ARO:3003150 carb-20-aro3003150.yaml
CLASS_A ARO:3003176 carb-21-aro3003176.yaml
CLASS_A ARO:3003151 carb-22-aro3003151.yaml
CLASS_A ARO:3003186 carb-23-aro3003186.yaml
CLASS_A ARO:3005560 carb-24-aro3005560.yaml
CLASS_A ARO:3005561 carb-25-aro3005561.yaml
CLASS_A ARO:3005562 carb-26-aro3005562.yaml
CLASS_A ARO:3005563 carb-27-aro3005563.yaml
CLASS_A ARO:3005564 carb-28-aro3005564.yaml
CLASS_A ARO:3005565 carb-29-aro3005565.yaml
CLASS_A ARO:3005566 carb-30-aro3005566.yaml
CLASS_A ARO:3005567 carb-31-aro3005567.yaml
CLASS_A ARO:3005568 carb-32-aro3005568.yaml
CLASS_A ARO:3005569 carb-33-aro3005569.yaml
CLASS_A ARO:3005570 carb-34-aro3005570.yaml
CLASS_A ARO:3005571 carb-35-aro3005571.yaml
CLASS_A ARO:3005572 carb-36-aro3005572.yaml
CLASS_A ARO:3005573 carb-38-aro3005573.yaml
CLASS_A ARO:3005574 carb-40-aro3005574.yaml
CLASS_A ARO:3005575 carb-41-aro3005575.yaml
CLASS_A ARO:3005576 carb-42-aro3005576.yaml
CLASS_A ARO:3005577 carb-43-aro3005577.yaml
CLASS_A ARO:3005578 carb-44-aro3005578.yaml
CLASS_A ARO:3005579 carb-45-aro3005579.yaml
CLASS_A ARO:3005580 carb-46-aro3005580.yaml
CLASS_A ARO:3005581 carb-47-aro3005581.yaml
CLASS_A ARO:3005582 carb-48-aro3005582.yaml
CLASS_A ARO:3005583 carb-49-aro3005583.yaml
CLASS_A ARO:3005584 carb-50-aro3005584.yaml
CLASS_A ARO:3005585 carb-51-aro3005585.yaml
CLASS_A ARO:3005586 carb-52-aro3005586.yaml
CLASS_A ARO:3005587 carb-53-aro3005587.yaml
CLASS_A ARO:3005588 carb-54-aro3005588.yaml
CLASS_A ARO:3005589 carb-55-aro3005589.yaml
CLASS_A ARO:3007803 carb-56-aro3007803.yaml
CLASS_A ARO:3007836 carb-57-aro3007836.yaml
CLASS_A ARO:3007837 carb-58-aro3007837.yaml
"""

TARGETS: tuple[beta.Target, ...] = tuple(
    beta.Target(identifier, filename, beta.GraphKind(kind))
    for kind, identifier, filename in (
        line.split() for line in _TARGET_ROWS.strip().splitlines()
    )
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


def _parts(target: beta.Target) -> beta.GraphParts:
    return beta._parts(target)


def enrich_record(record: dict[str, Any], target: beta.Target) -> tuple[dict[str, Any], bool]:
    return beta.enrich_record(record, target)


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not a BUT-CARB beta-lactamase target: {identifier}")
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
        help="ARO directory or one of the 62 BUT-CARB beta-lactamase YAML files",
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
