#!/usr/bin/env python3
"""Rewrite remaining NDM, OCH, and first OXY beta-lactamase causal graphs.

These score-79 beta-lactamase records still have old canonical graphs with
sparse edge descriptions and single-reference evidence. This batch finishes
NDM, finishes OCH, and starts OXY.

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
    "action": "Completed remaining NDM, OCH, and first OXY beta-lactamase causal graphs",
    "llm_assisted": True,
}

METALLO_TARGET_FILENAMES: tuple[str, ...] = (
    "ndm-6-aro3002356.yaml",
    "ndm-60-aro3008407.yaml",
    "ndm-61-aro3008408.yaml",
    "ndm-64-aro3008409.yaml",
    "ndm-65-aro3008410.yaml",
    "ndm-66-aro3008411.yaml",
    "ndm-67-aro3008412.yaml",
    "ndm-68-aro3008413.yaml",
    "ndm-69-aro3008414.yaml",
    "ndm-7-aro3002357.yaml",
    "ndm-70-aro3008415.yaml",
    "ndm-71-aro3008416.yaml",
    "ndm-72-aro3008417.yaml",
    "ndm-73-aro3008418.yaml",
    "ndm-74-aro3008419.yaml",
    "ndm-8-aro3002358.yaml",
    "ndm-9-aro3002359.yaml",
    "ndm-beta-lactamase-aro3000057.yaml",
)

CLASS_C_TARGET_FILENAMES: tuple[str, ...] = (
    "och-1-aro3002514.yaml",
    "och-2-aro3002515.yaml",
    "och-3-aro3002516.yaml",
    "och-4-aro3002517.yaml",
    "och-5-aro3002518.yaml",
    "och-6-aro3002519.yaml",
    "och-7-aro3002520.yaml",
    "och-8-aro3002521.yaml",
    "och-beta-lactamase-aro3000094.yaml",
)

CLASS_A_TARGET_FILENAMES: tuple[str, ...] = (
    "oxy-1-1-aro3002389.yaml",
    "oxy-1-11-aro3008777.yaml",
    "oxy-1-12-aro3008778.yaml",
    "oxy-1-13-aro3008779.yaml",
    "oxy-1-16-aro3008780.yaml",
    "oxy-1-17-aro3008781.yaml",
    "oxy-1-18-aro3008782.yaml",
    "oxy-1-19-aro3008783.yaml",
    "oxy-1-2-aro3002390.yaml",
    "oxy-1-3-aro3002391.yaml",
    "oxy-1-4-aro3002392.yaml",
    "oxy-1-6-aro3002394.yaml",
    "oxy-1-7-aro3009192.yaml",
    "oxy-10-1-aro3008784.yaml",
    "oxy-11-1-aro3008785.yaml",
    "oxy-12-1-aro3008786.yaml",
    "oxy-12-2-aro3008787.yaml",
    "oxy-2-1-aro3002396.yaml",
    "oxy-2-10-aro3002405.yaml",
    "oxy-2-11-aro3002406.yaml",
    "oxy-2-12-aro3002407.yaml",
    "oxy-2-13-aro3002408.yaml",
    "oxy-2-14-aro3006129.yaml",
    "oxy-2-15-aro3006130.yaml",
    "oxy-2-17-aro3008788.yaml",
    "oxy-2-18-aro3008789.yaml",
    "oxy-2-19-aro3008790.yaml",
    "oxy-2-2-aro3002397.yaml",
    "oxy-2-20-aro3008791.yaml",
    "oxy-2-21-aro3008792.yaml",
    "oxy-2-22-aro3008793.yaml",
    "oxy-2-23-aro3008794.yaml",
    "oxy-2-24-aro3008795.yaml",
)


def identifier_from_filename(filename: str) -> str:
    aro_number = filename.rsplit("-aro", maxsplit=1)[1].removesuffix(".yaml")
    return f"ARO:{aro_number}"


def targets_for_filenames(
    filenames: tuple[str, ...],
    kind: beta.GraphKind,
) -> tuple[beta.Target, ...]:
    return tuple(
        beta.Target(identifier_from_filename(filename), filename, kind)
        for filename in filenames
    )


TARGETS: tuple[beta.Target, ...] = (
    *targets_for_filenames(METALLO_TARGET_FILENAMES, beta.GraphKind.METALLO),
    *targets_for_filenames(CLASS_C_TARGET_FILENAMES, beta.GraphKind.CLASS_C),
    *targets_for_filenames(CLASS_A_TARGET_FILENAMES, beta.GraphKind.CLASS_A),
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
        raise ValueError(f"{path}: not a remaining-NDM/OCH/first-OXY beta-lactamase target: {identifier}")
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
        help="ARO directory or one of the remaining-NDM/OCH/first-OXY beta-lactamase YAML files",
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
