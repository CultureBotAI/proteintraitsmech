#!/usr/bin/env python3
"""Rewrite the fourth TEM beta-lactamase causal-graph record batch.

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
    "action": "Completed fourth TEM beta-lactamase causal graphs",
    "llm_assisted": True,
}

TARGET_FILENAMES: tuple[str, ...] = (
    "tem-30-aro3000900.yaml",
    "tem-31-aro3000901.yaml",
    "tem-32-aro3000902.yaml",
    "tem-33-aro3000903.yaml",
    "tem-34-aro3000904.yaml",
    "tem-35-aro3000905.yaml",
    "tem-36-aro3000906.yaml",
    "tem-37-aro3000907.yaml",
    "tem-38-aro3000908.yaml",
    "tem-39-aro3000909.yaml",
    "tem-4-aro3000876.yaml",
    "tem-40-aro3000910.yaml",
    "tem-42-aro3000911.yaml",
    "tem-43-aro3000912.yaml",
    "tem-44-aro3000913.yaml",
    "tem-45-aro3000914.yaml",
    "tem-46-aro3000915.yaml",
    "tem-47-aro3000916.yaml",
    "tem-48-aro3000917.yaml",
    "tem-49-aro3000918.yaml",
    "tem-5-aro3000877.yaml",
    "tem-50-aro3000919.yaml",
    "tem-51-aro3000920.yaml",
    "tem-52-aro3000921.yaml",
    "tem-53-aro3000922.yaml",
    "tem-54-aro3000923.yaml",
    "tem-55-aro3000924.yaml",
    "tem-56-aro3000925.yaml",
    "tem-57-aro3000926.yaml",
    "tem-58-aro3000927.yaml",
    "tem-59-aro3000928.yaml",
    "tem-6-aro3000878.yaml",
    "tem-60-aro3000929.yaml",
    "tem-61-aro3000930.yaml",
    "tem-63-aro3000931.yaml",
    "tem-65-aro3000932.yaml",
    "tem-66-aro3000933.yaml",
    "tem-67-aro3000934.yaml",
    "tem-68-aro3000935.yaml",
    "tem-7-aro3000879.yaml",
    "tem-70-aro3000936.yaml",
    "tem-71-aro3000937.yaml",
    "tem-72-aro3000938.yaml",
    "tem-73-aro3000939.yaml",
    "tem-74-aro3000940.yaml",
    "tem-75-aro3000941.yaml",
    "tem-76-aro3000942.yaml",
    "tem-78-aro3000944.yaml",
    "tem-79-aro3000946.yaml",
    "tem-8-aro3000880.yaml",
    "tem-80-aro3000947.yaml",
    "tem-81-aro3000948.yaml",
    "tem-82-aro3000949.yaml",
    "tem-83-aro3000950.yaml",
    "tem-84-aro3000951.yaml",
    "tem-85-aro3000952.yaml",
    "tem-86-aro3000953.yaml",
    "tem-87-aro3000954.yaml",
    "tem-88-aro3000955.yaml",
    "tem-89-aro3000956.yaml",
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
        raise ValueError(f"{path}: not a fourth TEM beta-lactamase target: {identifier}")
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
        help="ARO directory or one of the fourth TEM beta-lactamase YAML files",
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
