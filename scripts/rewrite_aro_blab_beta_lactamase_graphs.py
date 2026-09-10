#!/usr/bin/env python3
"""Rewrite BlaB metallo-beta-lactamase graphs.

This targets the BlaB class B beta-lactamase parent, its numbered descendants,
and Chryseobacterium meningosepticum BlaB.  All use the canonical
metallo-beta-lactamase graph while preserving their direct CARD drug-class
edges.

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

HISTORY_ACTION = "Completed BlaB metallo-beta-lactamase graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-09T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}


_TARGET_ROWS = """
ARO:3004201 blab-beta-lactamase-aro3004201.yaml
ARO:3005522 blab-1-aro3005522.yaml
ARO:3005533 blab-2-aro3005533.yaml
ARO:3005543 blab-3-aro3005543.yaml
ARO:3005553 blab-5-aro3005553.yaml
ARO:3005554 blab-6-aro3005554.yaml
ARO:3005555 blab-7-aro3005555.yaml
ARO:3005556 blab-8-aro3005556.yaml
ARO:3005557 blab-9-aro3005557.yaml
ARO:3005523 blab-10-aro3005523.yaml
ARO:3005524 blab-11-aro3005524.yaml
ARO:3005525 blab-12-aro3005525.yaml
ARO:3005526 blab-13-aro3005526.yaml
ARO:3005527 blab-14-aro3005527.yaml
ARO:3005528 blab-15-aro3005528.yaml
ARO:3005529 blab-16-aro3005529.yaml
ARO:3005530 blab-17-aro3005530.yaml
ARO:3005531 blab-18-aro3005531.yaml
ARO:3005532 blab-19-aro3005532.yaml
ARO:3005534 blab-20-aro3005534.yaml
ARO:3005535 blab-22-aro3005535.yaml
ARO:3005536 blab-23-aro3005536.yaml
ARO:3005537 blab-24-aro3005537.yaml
ARO:3005538 blab-25-aro3005538.yaml
ARO:3005539 blab-26-aro3005539.yaml
ARO:3005540 blab-27-aro3005540.yaml
ARO:3005541 blab-28-aro3005541.yaml
ARO:3005542 blab-29-aro3005542.yaml
ARO:3005544 blab-30-aro3005544.yaml
ARO:3005545 blab-31-aro3005545.yaml
ARO:3005546 blab-32-aro3005546.yaml
ARO:3005547 blab-33-aro3005547.yaml
ARO:3005548 blab-34-aro3005548.yaml
ARO:3005549 blab-35-aro3005549.yaml
ARO:3005550 blab-36-aro3005550.yaml
ARO:3005551 blab-38-aro3005551.yaml
ARO:3005552 blab-39-aro3005552.yaml
ARO:3000579 chryseobacterium-meningosepticum-blab-aro3000579.yaml
"""


TARGETS: tuple[beta.Target, ...] = tuple(
    beta.Target(identifier, filename, beta.GraphKind.METALLO)
    for identifier, filename in (line.split() for line in _TARGET_ROWS.strip().splitlines())
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


def enrich_record(record: dict[str, Any], target: beta.Target) -> tuple[dict[str, Any], bool]:
    return beta.enrich_record(record, target)


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not a BlaB beta-lactamase target: {identifier}")
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
        help="ARO directory or one of the 38 BlaB beta-lactamase YAML files",
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
