#!/usr/bin/env python3
"""Rewrite the third KPC beta-lactamase causal-graph record batch.

These score-80 class A beta-lactamase records still have old canonical graphs
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
    "action": "Completed third KPC beta-lactamase causal graphs",
    "llm_assisted": True,
}

TARGET_FILENAMES: tuple[str, ...] = (
    "kpc-211-aro3008333.yaml",
    "kpc-212-aro3008334.yaml",
    "kpc-213-aro3008335.yaml",
    "kpc-214-aro3008336.yaml",
    "kpc-215-aro3008337.yaml",
    "kpc-216-aro3008338.yaml",
    "kpc-217-aro3008339.yaml",
    "kpc-218-aro3008340.yaml",
    "kpc-22-aro3003180.yaml",
    "kpc-223-aro3008341.yaml",
    "kpc-224-aro3008342.yaml",
    "kpc-225-aro3008343.yaml",
    "kpc-226-aro3008344.yaml",
    "kpc-227-aro3008345.yaml",
    "kpc-228-aro3008346.yaml",
    "kpc-23-aro3005356.yaml",
    "kpc-230-aro3008347.yaml",
    "kpc-231-aro3008348.yaml",
    "kpc-232-aro3008349.yaml",
    "kpc-233-aro3008350.yaml",
    "kpc-234-aro3008351.yaml",
    "kpc-236-aro3008352.yaml",
    "kpc-237-aro3008353.yaml",
    "kpc-238-aro3008354.yaml",
    "kpc-239-aro3008355.yaml",
    "kpc-24-aro3004496.yaml",
    "kpc-240-aro3008356.yaml",
    "kpc-241-aro3008357.yaml",
    "kpc-242-aro3008358.yaml",
    "kpc-25-aro3005357.yaml",
    "kpc-26-aro3005358.yaml",
    "kpc-27-aro3005359.yaml",
    "kpc-28-aro3005361.yaml",
    "kpc-29-aro3005360.yaml",
    "kpc-3-aro3002313.yaml",
    "kpc-30-aro3005364.yaml",
    "kpc-31-aro3005362.yaml",
    "kpc-32-aro3005363.yaml",
    "kpc-33-aro3005365.yaml",
    "kpc-34-aro3005366.yaml",
    "kpc-35-aro3005367.yaml",
    "kpc-36-aro3005368.yaml",
    "kpc-37-aro3005369.yaml",
    "kpc-38-aro3005370.yaml",
    "kpc-39-aro3005371.yaml",
    "kpc-4-aro3002314.yaml",
    "kpc-40-aro3005372.yaml",
    "kpc-41-aro3005373.yaml",
    "kpc-42-aro3005374.yaml",
    "kpc-43-aro3005375.yaml",
    "kpc-44-aro3006186.yaml",
    "kpc-45-aro3005376.yaml",
    "kpc-46-aro3005377.yaml",
    "kpc-47-aro3008359.yaml",
    "kpc-48-aro3008360.yaml",
    "kpc-49-aro3005378.yaml",
    "kpc-5-aro3002315.yaml",
    "kpc-50-aro3005379.yaml",
    "kpc-51-aro3005380.yaml",
    "kpc-52-aro3005381.yaml",
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
        raise ValueError(f"{path}: not a third KPC beta-lactamase target: {identifier}")
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
        help="ARO directory or one of the third KPC beta-lactamase YAML files",
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
