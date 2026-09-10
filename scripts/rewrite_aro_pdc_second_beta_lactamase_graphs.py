#!/usr/bin/env python3
"""Rewrite the second PDC beta-lactamase causal-graph batch.

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
    "action": "Completed second PDC beta-lactamase causal graphs",
    "llm_assisted": True,
}

TARGET_FILENAMES: tuple[str, ...] = (
    "pdc-116-aro3006494.yaml",
    "pdc-117-aro3005303.yaml",
    "pdc-118-aro3005278.yaml",
    "pdc-119-aro3005309.yaml",
    "pdc-12-aro3006495.yaml",
    "pdc-120-aro3006496.yaml",
    "pdc-121-aro3006497.yaml",
    "pdc-122-aro3006498.yaml",
    "pdc-123-aro3006499.yaml",
    "pdc-124-aro3006500.yaml",
    "pdc-125-aro3006501.yaml",
    "pdc-126-aro3006502.yaml",
    "pdc-127-aro3006503.yaml",
    "pdc-128-aro3006504.yaml",
    "pdc-129-aro3006505.yaml",
    "pdc-13-aro3006506.yaml",
    "pdc-130-aro3006507.yaml",
    "pdc-131-aro3006508.yaml",
    "pdc-132-aro3006509.yaml",
    "pdc-133-aro3006510.yaml",
    "pdc-134-aro3006511.yaml",
    "pdc-135-aro3006512.yaml",
    "pdc-136-aro3006513.yaml",
    "pdc-137-aro3006514.yaml",
    "pdc-138-aro3006515.yaml",
    "pdc-139-aro3006516.yaml",
    "pdc-14-aro3005127.yaml",
    "pdc-140-aro3006517.yaml",
    "pdc-141-aro3006518.yaml",
    "pdc-142-aro3006519.yaml",
    "pdc-143-aro3006520.yaml",
    "pdc-144-aro3006521.yaml",
    "pdc-145-aro3006522.yaml",
    "pdc-146-aro3006523.yaml",
    "pdc-147-aro3006524.yaml",
    "pdc-148-aro3006525.yaml",
    "pdc-149-aro3006526.yaml",
    "pdc-15-aro3006527.yaml",
    "pdc-150-aro3006528.yaml",
    "pdc-151-aro3006529.yaml",
    "pdc-152-aro3006530.yaml",
    "pdc-153-aro3006531.yaml",
    "pdc-154-aro3006532.yaml",
    "pdc-155-aro3006533.yaml",
    "pdc-156-aro3006534.yaml",
    "pdc-157-aro3006535.yaml",
    "pdc-158-aro3006536.yaml",
    "pdc-159-aro3006537.yaml",
    "pdc-16-aro3006538.yaml",
    "pdc-160-aro3006539.yaml",
    "pdc-161-aro3006540.yaml",
    "pdc-162-aro3006541.yaml",
    "pdc-163-aro3006542.yaml",
    "pdc-164-aro3006543.yaml",
    "pdc-165-aro3006544.yaml",
    "pdc-166-aro3006545.yaml",
    "pdc-167-aro3006546.yaml",
    "pdc-168-aro3006547.yaml",
    "pdc-169-aro3006548.yaml",
    "pdc-17-aro3006549.yaml",
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
        raise ValueError(f"{path}: not a second-PDC beta-lactamase target: {identifier}")
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
        help="ARO directory or one of the second-PDC beta-lactamase YAML files",
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
