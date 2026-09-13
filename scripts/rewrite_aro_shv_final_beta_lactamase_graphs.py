#!/usr/bin/env python3
"""Rewrite the final SHV beta-lactamase causal-graph batch.

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
    "action": "Completed final SHV beta-lactamase causal-graph batch",
    "llm_assisted": True,
}

TARGET_FILENAMES: tuple[str, ...] = (
    "shv-43-aro3001101.yaml",
    "shv-44-aro3001102.yaml",
    "shv-45-aro3001103.yaml",
    "shv-46-aro3001104.yaml",
    "shv-48-aro3001105.yaml",
    "shv-49-aro3001106.yaml",
    "shv-5-aro3001064.yaml",
    "shv-50-aro3001107.yaml",
    "shv-51-aro3001108.yaml",
    "shv-52-aro3001109.yaml",
    "shv-53-aro3001110.yaml",
    "shv-54-aro3001331.yaml",
    "shv-55-aro3001111.yaml",
    "shv-56-aro3001112.yaml",
    "shv-57-aro3001113.yaml",
    "shv-58-aro3001332.yaml",
    "shv-59-aro3001114.yaml",
    "shv-6-aro3001065.yaml",
    "shv-60-aro3001115.yaml",
    "shv-61-aro3001116.yaml",
    "shv-62-aro3001117.yaml",
    "shv-63-aro3001118.yaml",
    "shv-64-aro3001119.yaml",
    "shv-65-aro3001120.yaml",
    "shv-66-aro3001121.yaml",
    "shv-67-aro3001122.yaml",
    "shv-68-aro3001333.yaml",
    "shv-69-aro3001123.yaml",
    "shv-7-aro3001066.yaml",
    "shv-70-aro3001124.yaml",
    "shv-71-aro3001125.yaml",
    "shv-72-aro3001126.yaml",
    "shv-73-aro3001127.yaml",
    "shv-74-aro3001128.yaml",
    "shv-75-aro3001129.yaml",
    "shv-76-aro3001130.yaml",
    "shv-77-aro3001131.yaml",
    "shv-78-aro3001132.yaml",
    "shv-79-aro3001133.yaml",
    "shv-8-aro3001067.yaml",
    "shv-80-aro3001134.yaml",
    "shv-81-aro3001135.yaml",
    "shv-82-aro3001136.yaml",
    "shv-83-aro3001137.yaml",
    "shv-84-aro3001138.yaml",
    "shv-85-aro3001139.yaml",
    "shv-86-aro3001140.yaml",
    "shv-87-aro3001334.yaml",
    "shv-88-aro3001335.yaml",
    "shv-89-aro3001141.yaml",
    "shv-9-aro3001068.yaml",
    "shv-90-aro3001142.yaml",
    "shv-91-aro3001143.yaml",
    "shv-92-aro3001144.yaml",
    "shv-93-aro3001145.yaml",
    "shv-94-aro3001146.yaml",
    "shv-95-aro3001147.yaml",
    "shv-96-aro3001148.yaml",
    "shv-97-aro3001149.yaml",
    "shv-98-aro3001336.yaml",
    "shv-99-aro3001337.yaml",
    "shv-beta-lactamase-aro3000015.yaml",
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
        raise ValueError(f"{path}: not a final SHV beta-lactamase target: {identifier}")
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
        help="ARO directory or one of the final SHV beta-lactamase YAML files",
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
