#!/usr/bin/env python3
"""Rewrite the first VIM beta-lactamase causal-graph record batch.

These score-79 metallo-beta-lactamase records still have old canonical graphs
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
    "action": "Completed first VIM beta-lactamase causal graphs",
    "llm_assisted": True,
}

TARGET_FILENAMES: tuple[str, ...] = (
    "vim-1-aro3002271.yaml",
    "vim-10-aro3002280.yaml",
    "vim-11-aro3002281.yaml",
    "vim-12-aro3002282.yaml",
    "vim-13-aro3002283.yaml",
    "vim-14-aro3002284.yaml",
    "vim-15-aro3002285.yaml",
    "vim-16-aro3002286.yaml",
    "vim-17-aro3002287.yaml",
    "vim-18-aro3002288.yaml",
    "vim-19-aro3002289.yaml",
    "vim-2-aro3002272.yaml",
    "vim-20-aro3002290.yaml",
    "vim-21-aro3002291.yaml",
    "vim-22-aro3002292.yaml",
    "vim-23-aro3002293.yaml",
    "vim-24-aro3002294.yaml",
    "vim-25-aro3002295.yaml",
    "vim-26-aro3002296.yaml",
    "vim-27-aro3002297.yaml",
    "vim-28-aro3002298.yaml",
    "vim-29-aro3002299.yaml",
    "vim-3-aro3002273.yaml",
    "vim-30-aro3002300.yaml",
    "vim-31-aro3002301.yaml",
    "vim-32-aro3002302.yaml",
    "vim-33-aro3002303.yaml",
    "vim-34-aro3002304.yaml",
    "vim-35-aro3002305.yaml",
    "vim-36-aro3002306.yaml",
    "vim-37-aro3002307.yaml",
    "vim-38-aro3002308.yaml",
    "vim-39-aro3002309.yaml",
    "vim-4-aro3002274.yaml",
    "vim-40-aro3002310.yaml",
    "vim-41-aro3002311.yaml",
    "vim-42-aro3003178.yaml",
    "vim-43-aro3003179.yaml",
    "vim-44-aro3003660.yaml",
    "vim-45-aro3003661.yaml",
    "vim-46-aro3003662.yaml",
    "vim-47-aro3005495.yaml",
    "vim-48-aro3005496.yaml",
    "vim-49-aro3005497.yaml",
    "vim-5-aro3002275.yaml",
    "vim-50-aro3005498.yaml",
    "vim-51-aro3005499.yaml",
    "vim-52-aro3005500.yaml",
    "vim-53-aro3005501.yaml",
    "vim-54-aro3005502.yaml",
    "vim-55-aro3005503.yaml",
    "vim-56-aro3005504.yaml",
    "vim-57-aro3005505.yaml",
    "vim-58-aro3005506.yaml",
    "vim-59-aro3005507.yaml",
    "vim-6-aro3002276.yaml",
    "vim-60-aro3005508.yaml",
    "vim-61-aro3005509.yaml",
    "vim-62-aro3005510.yaml",
    "vim-63-aro3005511.yaml",
)


def identifier_from_filename(filename: str) -> str:
    aro_number = filename.rsplit("-aro", maxsplit=1)[1].removesuffix(".yaml")
    return f"ARO:{aro_number}"


TARGETS: tuple[beta.Target, ...] = tuple(
    beta.Target(identifier_from_filename(filename), filename, beta.GraphKind.METALLO)
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
        raise ValueError(f"{path}: not a first VIM beta-lactamase target: {identifier}")
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
        help="ARO directory or one of the first VIM beta-lactamase YAML files",
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
