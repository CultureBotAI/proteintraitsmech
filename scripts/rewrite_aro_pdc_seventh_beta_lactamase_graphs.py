#!/usr/bin/env python3
"""Rewrite the seventh PDC beta-lactamase causal-graph batch.

These score-79 class C beta-lactamase records still have old canonical graphs
with sparse edge descriptions and single-reference evidence.

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
    "action": "Completed seventh PDC beta-lactamase causal graphs",
    "llm_assisted": True,
}

TARGET_FILENAMES: tuple[str, ...] = (
    "pdc-388-aro3006757.yaml",
    "pdc-389-aro3006758.yaml",
    "pdc-39-aro3006759.yaml",
    "pdc-390-aro3006760.yaml",
    "pdc-391-aro3006761.yaml",
    "pdc-392-aro3006762.yaml",
    "pdc-393-aro3005308.yaml",
    "pdc-394-aro3006763.yaml",
    "pdc-395-aro3006764.yaml",
    "pdc-396-aro3006765.yaml",
    "pdc-397-aro3006766.yaml",
    "pdc-398-aro3006767.yaml",
    "pdc-399-aro3006768.yaml",
    "pdc-4-aro3002501.yaml",
    "pdc-40-aro3006769.yaml",
    "pdc-400-aro3006770.yaml",
    "pdc-401-aro3006771.yaml",
    "pdc-402-aro3006772.yaml",
    "pdc-403-aro3006773.yaml",
    "pdc-404-aro3006774.yaml",
    "pdc-405-aro3006775.yaml",
    "pdc-406-aro3006776.yaml",
    "pdc-407-aro3006777.yaml",
    "pdc-408-aro3006778.yaml",
    "pdc-409-aro3006779.yaml",
    "pdc-41-aro3005157.yaml",
    "pdc-410-aro3006780.yaml",
    "pdc-411-aro3006781.yaml",
    "pdc-412-aro3006782.yaml",
    "pdc-413-aro3005282.yaml",
    "pdc-414-aro3006783.yaml",
    "pdc-415-aro3006784.yaml",
    "pdc-416-aro3006785.yaml",
    "pdc-417-aro3006786.yaml",
    "pdc-418-aro3006787.yaml",
    "pdc-419-aro3006788.yaml",
    "pdc-42-aro3006789.yaml",
    "pdc-420-aro3006790.yaml",
    "pdc-421-aro3006791.yaml",
    "pdc-422-aro3006792.yaml",
    "pdc-423-aro3006793.yaml",
    "pdc-424-aro3006794.yaml",
    "pdc-425-aro3006795.yaml",
    "pdc-426-aro3006796.yaml",
    "pdc-427-aro3006797.yaml",
    "pdc-428-aro3006798.yaml",
    "pdc-429-aro3005312.yaml",
    "pdc-43-aro3005134.yaml",
    "pdc-430-aro3006799.yaml",
    "pdc-431-aro3006800.yaml",
    "pdc-432-aro3006801.yaml",
    "pdc-433-aro3006802.yaml",
    "pdc-434-aro3006803.yaml",
    "pdc-435-aro3006804.yaml",
    "pdc-436-aro3006805.yaml",
    "pdc-437-aro3006806.yaml",
    "pdc-438-aro3005275.yaml",
    "pdc-439-aro3006807.yaml",
    "pdc-44-aro3005142.yaml",
    "pdc-440-aro3006808.yaml",
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
        raise ValueError(f"{path}: not a seventh-PDC beta-lactamase target: {identifier}")
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
        help="ARO directory or one of the seventh-PDC beta-lactamase YAML files",
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
