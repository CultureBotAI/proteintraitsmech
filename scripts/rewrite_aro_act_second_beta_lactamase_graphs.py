#!/usr/bin/env python3
"""Rewrite the second ACT class C beta-lactamase causal-graph batch.

These score-79 beta-lactamase records still have old canonical class C graphs
with sparse edge descriptions and single-reference evidence.  This batch picks
up immediately after the first ACC/ACT wrapper in score/path order.

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
    "action": "Completed second ACT beta-lactamase causal graphs",
    "llm_assisted": True,
}

TARGET_FILENAMES: tuple[str, ...] = (
    "act-159-aro3007924.yaml",
    "act-16-aro3001827.yaml",
    "act-160-aro3007925.yaml",
    "act-161-aro3007926.yaml",
    "act-162-aro3007927.yaml",
    "act-165-aro3007928.yaml",
    "act-166-aro3007929.yaml",
    "act-167-aro3007930.yaml",
    "act-168-aro3007931.yaml",
    "act-169-aro3007932.yaml",
    "act-17-aro3001838.yaml",
    "act-170-aro3007933.yaml",
    "act-171-aro3007934.yaml",
    "act-172-aro3007935.yaml",
    "act-173-aro3007936.yaml",
    "act-174-aro3007937.yaml",
    "act-175-aro3007938.yaml",
    "act-176-aro3007939.yaml",
    "act-177-aro3007940.yaml",
    "act-178-aro3007941.yaml",
    "act-179-aro3007942.yaml",
    "act-18-aro3001839.yaml",
    "act-180-aro3007943.yaml",
    "act-181-aro3007944.yaml",
    "act-182-aro3007945.yaml",
    "act-183-aro3007946.yaml",
    "act-184-aro3007947.yaml",
    "act-185-aro3007948.yaml",
    "act-186-aro3007949.yaml",
    "act-187-aro3007950.yaml",
    "act-188-aro3007951.yaml",
    "act-189-aro3007952.yaml",
    "act-19-aro3001840.yaml",
    "act-190-aro3007953.yaml",
    "act-191-aro3007954.yaml",
    "act-192-aro3007955.yaml",
    "act-193-aro3007956.yaml",
    "act-194-aro3007957.yaml",
    "act-2-aro3001822.yaml",
    "act-20-aro3001841.yaml",
    "act-21-aro3001842.yaml",
    "act-22-aro3001843.yaml",
    "act-23-aro3001828.yaml",
    "act-24-aro3001844.yaml",
    "act-25-aro3001845.yaml",
    "act-27-aro3001847.yaml",
    "act-28-aro3001848.yaml",
    "act-29-aro3001849.yaml",
    "act-3-aro3001823.yaml",
    "act-30-aro3001850.yaml",
    "act-31-aro3001851.yaml",
    "act-32-aro3001852.yaml",
    "act-33-aro3001853.yaml",
    "act-34-aro3001854.yaml",
    "act-35-aro3001855.yaml",
    "act-36-aro3003171.yaml",
    "act-37-aro3003172.yaml",
    "act-38-aro3003655.yaml",
    "act-39-aro3006234.yaml",
    "act-4-aro3001829.yaml",
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
        raise ValueError(f"{path}: not a second ACT beta-lactamase target: {identifier}")
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
        help="ARO directory or one of the second ACT beta-lactamase YAML files",
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
