#!/usr/bin/env python3
"""Rewrite the first SHV beta-lactamase causal-graph batch.

These score-78 class A SHV beta-lactamase records still have old canonical
class A graphs with sparse edge descriptions and single-reference evidence.

Dry-run by default; pass ``--apply`` to write.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from record_io import append_to_section, replace_block  # noqa: E402
from rewrite_aro_early_beta_lactamase_graphs import (  # noqa: E402
    GraphKind,
    Target,
    enrich_record,
)

ROOT = Path(__file__).resolve().parent.parent
ARO_DIR = ROOT / "data" / "traits" / "function" / "resistance" / "aro"

HISTORY_CURATOR = "codex-causal-graph-quality"
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": "Completed first SHV beta-lactamase causal-graph batch",
    "llm_assisted": True,
}

TARGET_FILENAMES: tuple[str, ...] = (
    "shv-1-aro3001059.yaml",
    "shv-10-aro3001069.yaml",
    "shv-100-aro3001338.yaml",
    "shv-101-aro3001150.yaml",
    "shv-102-aro3001151.yaml",
    "shv-103-aro3001152.yaml",
    "shv-104-aro3001153.yaml",
    "shv-105-aro3001154.yaml",
    "shv-106-aro3001155.yaml",
    "shv-107-aro3001156.yaml",
    "shv-108-aro3001157.yaml",
    "shv-109-aro3001158.yaml",
    "shv-11-aro3001070.yaml",
    "shv-110-aro3001159.yaml",
    "shv-111-aro3001160.yaml",
    "shv-112-aro3001161.yaml",
    "shv-113-aro3001162.yaml",
    "shv-114-aro3001163.yaml",
    "shv-115-aro3001164.yaml",
    "shv-116-aro3001165.yaml",
    "shv-117-aro3001166.yaml",
    "shv-118-aro3001339.yaml",
    "shv-119-aro3001340.yaml",
    "shv-12-aro3001071.yaml",
    "shv-120-aro3001167.yaml",
    "shv-121-aro3001168.yaml",
    "shv-122-aro3001169.yaml",
    "shv-123-aro3001170.yaml",
    "shv-124-aro3001171.yaml",
    "shv-125-aro3001172.yaml",
    "shv-126-aro3001173.yaml",
    "shv-127-aro3001174.yaml",
    "shv-128-aro3001175.yaml",
    "shv-129-aro3001176.yaml",
    "shv-13-aro3001072.yaml",
    "shv-132-aro3001341.yaml",
    "shv-133-aro3001177.yaml",
    "shv-134-aro3001178.yaml",
    "shv-135-aro3001179.yaml",
    "shv-137-aro3001181.yaml",
    "shv-138-aro3001342.yaml",
    "shv-139-aro3001343.yaml",
    "shv-14-aro3001073.yaml",
    "shv-140-aro3001182.yaml",
    "shv-141-aro3001183.yaml",
    "shv-142-aro3001184.yaml",
    "shv-143-aro3001344.yaml",
    "shv-144-aro3001345.yaml",
    "shv-145-aro3001185.yaml",
    "shv-146-aro3001346.yaml",
    "shv-147-aro3001186.yaml",
    "shv-148-aro3001187.yaml",
    "shv-149-aro3001188.yaml",
    "shv-15-aro3001074.yaml",
    "shv-150-aro3001189.yaml",
    "shv-151-aro3001190.yaml",
    "shv-152-aro3001191.yaml",
    "shv-153-aro3001192.yaml",
    "shv-154-aro3001193.yaml",
    "shv-155-aro3001194.yaml",
)


def identifier_from_filename(filename: str) -> str:
    aro_number = filename.rsplit("-aro", maxsplit=1)[1].removesuffix(".yaml")
    return f"ARO:{aro_number}"


TARGETS: tuple[Target, ...] = tuple(
    Target(identifier_from_filename(filename), filename, GraphKind.CLASS_A)
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
        raise ValueError(f"{path}: not a first SHV beta-lactamase target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
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
        help="ARO directory or one of the first SHV beta-lactamase YAML files",
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
