#!/usr/bin/env python3
"""Rewrite the third TEM beta-lactamase causal-graph record batch.

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
    "action": "Completed third TEM beta-lactamase causal graphs",
    "llm_assisted": True,
}

TARGET_FILENAMES: tuple[str, ...] = (
    "tem-208-aro3001385.yaml",
    "tem-209-aro3001386.yaml",
    "tem-21-aro3000892.yaml",
    "tem-210-aro3001387.yaml",
    "tem-211-aro3001388.yaml",
    "tem-212-aro3001389.yaml",
    "tem-213-aro3001390.yaml",
    "tem-214-aro3001391.yaml",
    "tem-215-aro3001392.yaml",
    "tem-216-aro3001393.yaml",
    "tem-217-aro3001394.yaml",
    "tem-218-aro3001395.yaml",
    "tem-219-aro3003157.yaml",
    "tem-22-aro3000893.yaml",
    "tem-220-aro3003158.yaml",
    "tem-221-aro3003113.yaml",
    "tem-222-aro3003114.yaml",
    "tem-223-aro3003592.yaml",
    "tem-224-aro3005255.yaml",
    "tem-225-aro3005256.yaml",
    "tem-226-aro3005257.yaml",
    "tem-227-aro3005258.yaml",
    "tem-228-aro3005259.yaml",
    "tem-229-aro3005260.yaml",
    "tem-230-aro3005261.yaml",
    "tem-231-aro3005262.yaml",
    "tem-232-aro3005263.yaml",
    "tem-233-aro3005264.yaml",
    "tem-234-aro3005265.yaml",
    "tem-235-aro3005266.yaml",
    "tem-236-aro3005267.yaml",
    "tem-237-aro3005268.yaml",
    "tem-238-aro3005269.yaml",
    "tem-239-aro3009066.yaml",
    "tem-24-aro3000894.yaml",
    "tem-240-aro3005270.yaml",
    "tem-241-aro3005271.yaml",
    "tem-242-aro3005272.yaml",
    "tem-243-aro3005273.yaml",
    "tem-244-aro3007453.yaml",
    "tem-245-aro3007454.yaml",
    "tem-246-aro3007448.yaml",
    "tem-247-aro3007451.yaml",
    "tem-248-aro3009067.yaml",
    "tem-249-aro3009068.yaml",
    "tem-25-aro3000895.yaml",
    "tem-250-aro3009069.yaml",
    "tem-251-aro3009070.yaml",
    "tem-252-aro3009071.yaml",
    "tem-253-aro3009072.yaml",
    "tem-254-aro3009073.yaml",
    "tem-255-aro3009074.yaml",
    "tem-256-aro3009075.yaml",
    "tem-257-aro3009076.yaml",
    "tem-258-aro3009077.yaml",
    "tem-26-aro3000896.yaml",
    "tem-27-aro3000897.yaml",
    "tem-28-aro3000898.yaml",
    "tem-29-aro3000899.yaml",
    "tem-3-aro3000875.yaml",
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
        raise ValueError(f"{path}: not a third TEM beta-lactamase target: {identifier}")
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
        help="ARO directory or one of the third TEM beta-lactamase YAML files",
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
