#!/usr/bin/env python3
"""Rewrite the second SHV beta-lactamase causal-graph batch.

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
    "action": "Completed second SHV beta-lactamase causal-graph batch",
    "llm_assisted": True,
}

TARGET_FILENAMES: tuple[str, ...] = (
    "shv-156-aro3001195.yaml",
    "shv-157-aro3001196.yaml",
    "shv-158-aro3001197.yaml",
    "shv-159-aro3001198.yaml",
    "shv-16-aro3001075.yaml",
    "shv-160-aro3001199.yaml",
    "shv-161-aro3001200.yaml",
    "shv-162-aro3001201.yaml",
    "shv-163-aro3001202.yaml",
    "shv-164-aro3001347.yaml",
    "shv-165-aro3001203.yaml",
    "shv-166-aro3001348.yaml",
    "shv-167-aro3001204.yaml",
    "shv-168-aro3001352.yaml",
    "shv-169-aro3001353.yaml",
    "shv-170-aro3001354.yaml",
    "shv-171-aro3001355.yaml",
    "shv-172-aro3001356.yaml",
    "shv-173-aro3001357.yaml",
    "shv-174-aro3001349.yaml",
    "shv-175-aro3001358.yaml",
    "shv-176-aro3001359.yaml",
    "shv-177-aro3001360.yaml",
    "shv-178-aro3001361.yaml",
    "shv-179-aro3001362.yaml",
    "shv-18-aro3001076.yaml",
    "shv-180-aro3001350.yaml",
    "shv-181-aro3001363.yaml",
    "shv-182-aro3001364.yaml",
    "shv-183-aro3001351.yaml",
    "shv-184-aro3001365.yaml",
    "shv-185-aro3003152.yaml",
    "shv-186-aro3003153.yaml",
    "shv-187-aro3003154.yaml",
    "shv-188-aro3003155.yaml",
    "shv-189-aro3003156.yaml",
    "shv-19-aro3001077.yaml",
    "shv-190-aro3003590.yaml",
    "shv-191-aro3003591.yaml",
    "shv-193-aro3005239.yaml",
    "shv-194-aro3005223.yaml",
    "shv-195-aro3005210.yaml",
    "shv-196-aro3005229.yaml",
    "shv-197-aro3005214.yaml",
    "shv-198-aro3005209.yaml",
    "shv-199-aro3005232.yaml",
    "shv-1b-b-aro3005237.yaml",
    "shv-2-aro3001060.yaml",
    "shv-20-aro3001078.yaml",
    "shv-200-aro3005248.yaml",
    "shv-201-aro3005211.yaml",
    "shv-202-aro3005253.yaml",
    "shv-203-aro3005249.yaml",
    "shv-204-aro3005213.yaml",
    "shv-205-aro3005207.yaml",
    "shv-206-aro3005227.yaml",
    "shv-207-aro3005236.yaml",
    "shv-208-aro3005226.yaml",
    "shv-209-aro3005242.yaml",
    "shv-21-aro3001079.yaml",
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
        raise ValueError(f"{path}: not a second SHV beta-lactamase target: {identifier}")
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
        help="ARO directory or one of the second SHV beta-lactamase YAML files",
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
