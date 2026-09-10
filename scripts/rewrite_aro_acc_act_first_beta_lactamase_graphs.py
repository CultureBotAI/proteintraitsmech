#!/usr/bin/env python3
"""Rewrite first ACC/ACT class C beta-lactamase causal graphs.

These score-79 beta-lactamase records still have old canonical class C graphs
with sparse edge descriptions and single-reference evidence.  This first batch
covers the ACC family plus the first ACT records in score/path order.

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

HISTORY_CURATOR = "codex-causal-graph-quality"
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": "Completed first ACC/ACT beta-lactamase causal graphs",
    "llm_assisted": True,
}

TARGET_FILENAMES: tuple[str, ...] = (
    "acc-1-aro3001815.yaml",
    "acc-1a-aro3006228.yaml",
    "acc-1b-aro3006229.yaml",
    "acc-1c-aro3006230.yaml",
    "acc-1d-aro3006231.yaml",
    "acc-2-aro3001816.yaml",
    "acc-3-aro3001817.yaml",
    "acc-4-aro3001818.yaml",
    "acc-5-aro3001819.yaml",
    "acc-7-aro3006232.yaml",
    "acc-8-aro3006233.yaml",
    "acc-beta-lactamase-aro3000073.yaml",
    "act-1-aro3001821.yaml",
    "act-10-aro3001832.yaml",
    "act-100-aro3007883.yaml",
    "act-101-aro3007884.yaml",
    "act-102-aro3007885.yaml",
    "act-103-aro3007886.yaml",
    "act-104-aro3007887.yaml",
    "act-105-aro3007888.yaml",
    "act-106-aro3007889.yaml",
    "act-107-aro3007890.yaml",
    "act-108-aro3007891.yaml",
    "act-109-aro3007892.yaml",
    "act-11-aro3001833.yaml",
    "act-110-aro3007893.yaml",
    "act-111-aro3007894.yaml",
    "act-112-aro3007895.yaml",
    "act-113-aro3007896.yaml",
    "act-115-aro3007897.yaml",
    "act-116-aro3007898.yaml",
    "act-117-aro3007899.yaml",
    "act-118-aro3007900.yaml",
    "act-119-aro3007901.yaml",
    "act-12-aro3001834.yaml",
    "act-120-aro3007902.yaml",
    "act-121-aro3007903.yaml",
    "act-122-aro3007904.yaml",
    "act-123-aro3007905.yaml",
    "act-124-aro3007906.yaml",
    "act-13-aro3001835.yaml",
    "act-131-aro3007907.yaml",
    "act-14-aro3001836.yaml",
    "act-140-aro3007908.yaml",
    "act-141-aro3007909.yaml",
    "act-142-aro3007910.yaml",
    "act-143-aro3007911.yaml",
    "act-144-aro3007912.yaml",
    "act-145-aro3007913.yaml",
    "act-146-aro3007914.yaml",
    "act-148-aro3007915.yaml",
    "act-15-aro3001837.yaml",
    "act-150-aro3007916.yaml",
    "act-151-aro3007917.yaml",
    "act-153-aro3007918.yaml",
    "act-154-aro3007919.yaml",
    "act-155-aro3007920.yaml",
    "act-156-aro3007921.yaml",
    "act-157-aro3007922.yaml",
    "act-158-aro3007923.yaml",
)


def identifier_from_filename(filename: str) -> str:
    aro_number = filename.rsplit("-aro", maxsplit=1)[1].removesuffix(".yaml")
    return f"ARO:{aro_number}"


TARGETS: tuple[beta.Target, ...] = tuple(
    beta.Target(identifier_from_filename(filename), filename, beta.GraphKind.CLASS_C)
    for filename in TARGET_FILENAMES
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


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not a first ACC/ACT beta-lactamase target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = beta.enrich_record(record, target)
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
        help="ARO directory or one of the first ACC/ACT beta-lactamase YAML files",
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
