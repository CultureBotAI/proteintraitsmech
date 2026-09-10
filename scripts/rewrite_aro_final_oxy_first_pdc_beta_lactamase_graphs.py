#!/usr/bin/env python3
"""Rewrite final OXY and first PDC beta-lactamase causal graphs.

These score-79 beta-lactamase records still have old canonical graphs with
sparse edge descriptions and single-reference evidence. This batch finishes
OXY and starts PDC.

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
    "action": "Completed final OXY and first PDC beta-lactamase causal graphs",
    "llm_assisted": True,
}

CLASS_A_TARGET_FILENAMES: tuple[str, ...] = (
    "oxy-2-25-aro3008796.yaml",
    "oxy-2-26-aro3008797.yaml",
    "oxy-2-27-aro3008798.yaml",
    "oxy-2-28-aro3008799.yaml",
    "oxy-2-3-aro3002398.yaml",
    "oxy-2-30-aro3008800.yaml",
    "oxy-2-4-aro3002399.yaml",
    "oxy-2-5-aro3002400.yaml",
    "oxy-2-6-aro3002401.yaml",
    "oxy-2-7-aro3002402.yaml",
    "oxy-2-8-aro3002403.yaml",
    "oxy-2-9-aro3002404.yaml",
    "oxy-3-1-aro3002409.yaml",
    "oxy-3-2-aro3008801.yaml",
    "oxy-3-3-aro3008802.yaml",
    "oxy-4-1-aro3002410.yaml",
    "oxy-4-2-aro3008803.yaml",
    "oxy-4-3-aro3008804.yaml",
    "oxy-4-4-aro3008805.yaml",
    "oxy-4-5-aro3008806.yaml",
    "oxy-5-1-aro3002411.yaml",
    "oxy-5-10-aro3008807.yaml",
    "oxy-5-11-aro3008808.yaml",
    "oxy-5-2-aro3002412.yaml",
    "oxy-5-6-aro3008809.yaml",
    "oxy-5-7-aro3008810.yaml",
    "oxy-5-8-aro3008811.yaml",
    "oxy-6-1-aro3002413.yaml",
    "oxy-6-10-aro3008812.yaml",
    "oxy-6-11-aro3008813.yaml",
    "oxy-6-2-aro3002414.yaml",
    "oxy-6-3-aro3002415.yaml",
    "oxy-6-4-aro3002416.yaml",
    "oxy-6-5-aro3008814.yaml",
    "oxy-6-7-aro3008815.yaml",
    "oxy-7-1-aro3008816.yaml",
    "oxy-8-1-aro3008817.yaml",
    "oxy-8-2-aro3008818.yaml",
    "oxy-8-3-aro3008819.yaml",
    "oxy-9-1-aro3008820.yaml",
    "oxy-beta-lactamase-aro3002388.yaml",
)

CLASS_C_TARGET_FILENAMES: tuple[str, ...] = (
    "pdc-1-aro3002497.yaml",
    "pdc-10-aro3002509.yaml",
    "pdc-100-aro3006480.yaml",
    "pdc-101-aro3006481.yaml",
    "pdc-102-aro3006482.yaml",
    "pdc-103-aro3006483.yaml",
    "pdc-104-aro3005305.yaml",
    "pdc-105-aro3005277.yaml",
    "pdc-106-aro3006484.yaml",
    "pdc-107-aro3006485.yaml",
    "pdc-108-aro3006486.yaml",
    "pdc-109-aro3006487.yaml",
    "pdc-11-aro3005132.yaml",
    "pdc-110-aro3006488.yaml",
    "pdc-111-aro3006489.yaml",
    "pdc-112-aro3006490.yaml",
    "pdc-113-aro3006491.yaml",
    "pdc-114-aro3006492.yaml",
    "pdc-115-aro3006493.yaml",
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
    *targets_for_filenames(CLASS_A_TARGET_FILENAMES, beta.GraphKind.CLASS_A),
    *targets_for_filenames(CLASS_C_TARGET_FILENAMES, beta.GraphKind.CLASS_C),
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
        raise ValueError(f"{path}: not a final-OXY/first-PDC beta-lactamase target: {identifier}")
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
        help="ARO directory or one of the final-OXY/first-PDC beta-lactamase YAML files",
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
