#!/usr/bin/env python3
"""Rewrite the second TEM beta-lactamase causal-graph record batch.

These score-79 class A TEM beta-lactamase records still have old canonical
graphs with sparse edge descriptions and single-reference evidence.

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
    "action": "Completed second TEM beta-lactamase causal graphs",
    "llm_assisted": True,
}

TARGET_FILENAMES: tuple[str, ...] = (
    "tem-154-aro3001020.yaml",
    "tem-155-aro3001021.yaml",
    "tem-156-aro3001022.yaml",
    "tem-157-aro3001023.yaml",
    "tem-158-aro3001024.yaml",
    "tem-159-aro3001025.yaml",
    "tem-16-aro3000887.yaml",
    "tem-160-aro3001026.yaml",
    "tem-161-aro3001027.yaml",
    "tem-162-aro3001028.yaml",
    "tem-163-aro3001029.yaml",
    "tem-164-aro3001030.yaml",
    "tem-165-aro3001031.yaml",
    "tem-166-aro3001032.yaml",
    "tem-167-aro3001033.yaml",
    "tem-168-aro3001034.yaml",
    "tem-169-aro3001035.yaml",
    "tem-17-aro3000888.yaml",
    "tem-170-aro3001036.yaml",
    "tem-171-aro3001037.yaml",
    "tem-172-aro3001038.yaml",
    "tem-173-aro3001039.yaml",
    "tem-174-aro3001040.yaml",
    "tem-175-aro3001370.yaml",
    "tem-176-aro3001041.yaml",
    "tem-177-aro3001042.yaml",
    "tem-178-aro3001043.yaml",
    "tem-179-aro3001371.yaml",
    "tem-18-aro3000889.yaml",
    "tem-180-aro3001372.yaml",
    "tem-181-aro3001044.yaml",
    "tem-182-aro3001373.yaml",
    "tem-183-aro3001045.yaml",
    "tem-184-aro3001375.yaml",
    "tem-185-aro3001374.yaml",
    "tem-186-aro3001046.yaml",
    "tem-187-aro3001047.yaml",
    "tem-188-aro3001048.yaml",
    "tem-189-aro3001049.yaml",
    "tem-19-aro3000890.yaml",
    "tem-190-aro3001050.yaml",
    "tem-191-aro3001051.yaml",
    "tem-192-aro3001052.yaml",
    "tem-193-aro3001053.yaml",
    "tem-194-aro3001054.yaml",
    "tem-195-aro3001055.yaml",
    "tem-196-aro3001376.yaml",
    "tem-197-aro3001056.yaml",
    "tem-198-aro3001057.yaml",
    "tem-199-aro3001058.yaml",
    "tem-2-aro3000874.yaml",
    "tem-20-aro3000891.yaml",
    "tem-200-aro3001377.yaml",
    "tem-201-aro3001378.yaml",
    "tem-202-aro3001379.yaml",
    "tem-203-aro3001380.yaml",
    "tem-204-aro3001381.yaml",
    "tem-205-aro3001382.yaml",
    "tem-206-aro3001383.yaml",
    "tem-207-aro3001384.yaml",
)


def identifier_from_filename(filename: str) -> str:
    aro_number = filename.rsplit("-aro", maxsplit=1)[1].removesuffix(".yaml")
    return f"ARO:{aro_number}"


TARGETS: tuple[beta.Target, ...] = tuple(
    beta.Target(identifier_from_filename(filename), filename, beta.GraphKind.CLASS_A)
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
        raise ValueError(f"{path}: not a second TEM beta-lactamase target: {identifier}")
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
        help="ARO directory or one of the second TEM beta-lactamase YAML files",
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
