#!/usr/bin/env python3
"""Rewrite the third SHV beta-lactamase causal-graph batch.

These score-78 class A SHV beta-lactamase records still have old canonical
class A graphs with sparse edge descriptions and single-reference evidence.

Dry-run by default; pass ``--apply`` to write.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from record_io import append_to_section, replace_block  # noqa: E402
from rewrite_aro_early_beta_lactamase_graphs import (  # noqa: E402
    GraphKind,
    Target,
    enrich_record,
)

ROOT = Path(__file__).resolve().parent.parent
ARO_DIR = ROOT / "data" / "traits" / "function" / "resistance" / "aro"

HISTORY_CURATOR = "codex-causal-graph-quality"
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": "Completed third SHV beta-lactamase causal-graph batch",
    "llm_assisted": True,
}

TARGET_FILENAMES: tuple[str, ...] = (
    "shv-210-aro3005225.yaml",
    "shv-211-aro3005230.yaml",
    "shv-212-aro3005212.yaml",
    "shv-213-aro3005251.yaml",
    "shv-214-aro3005235.yaml",
    "shv-215-aro3005243.yaml",
    "shv-216-aro3005215.yaml",
    "shv-217-aro3005250.yaml",
    "shv-218-aro3005238.yaml",
    "shv-219-aro3005231.yaml",
    "shv-22-aro3001080.yaml",
    "shv-220-aro3005224.yaml",
    "shv-221-aro3005252.yaml",
    "shv-222-aro3005208.yaml",
    "shv-223-aro3005234.yaml",
    "shv-224-aro3005240.yaml",
    "shv-225-aro3005241.yaml",
    "shv-226-aro3005228.yaml",
    "shv-227-aro3005233.yaml",
    "shv-228-aro3005247.yaml",
    "shv-229-aro3009048.yaml",
    "shv-23-aro3001081.yaml",
    "shv-230-aro3009049.yaml",
    "shv-231-aro3009050.yaml",
    "shv-232-aro3009051.yaml",
    "shv-233-aro3009052.yaml",
    "shv-234-aro3009053.yaml",
    "shv-235-aro3009054.yaml",
    "shv-236-aro3009055.yaml",
    "shv-237-aro3009056.yaml",
    "shv-238-aro3009057.yaml",
    "shv-239-aro3009058.yaml",
    "shv-24-aro3001082.yaml",
    "shv-240-aro3009059.yaml",
    "shv-241-aro3009060.yaml",
    "shv-242-aro3009061.yaml",
    "shv-243-aro3009062.yaml",
    "shv-244-aro3009063.yaml",
    "shv-245-aro3009064.yaml",
    "shv-25-aro3001083.yaml",
    "shv-26-aro3001084.yaml",
    "shv-27-aro3001085.yaml",
    "shv-28-aro3001086.yaml",
    "shv-29-aro3001087.yaml",
    "shv-2a-aro3001061.yaml",
    "shv-3-aro3001062.yaml",
    "shv-30-aro3001088.yaml",
    "shv-31-aro3001089.yaml",
    "shv-32-aro3001090.yaml",
    "shv-33-aro3001091.yaml",
    "shv-34-aro3001092.yaml",
    "shv-35-aro3001093.yaml",
    "shv-36-aro3001094.yaml",
    "shv-37-aro3001095.yaml",
    "shv-38-aro3001096.yaml",
    "shv-39-aro3001097.yaml",
    "shv-4-aro3001063.yaml",
    "shv-40-aro3001098.yaml",
    "shv-41-aro3001099.yaml",
    "shv-42-aro3001100.yaml",
)


def identifier_from_filename(filename: str) -> str:
    aro_number = filename.rsplit("-aro", maxsplit=1)[1].removesuffix(".yaml")
    return f"ARO:{aro_number}"


TARGETS: tuple[Target, ...] = tuple(
    Target(identifier_from_filename(filename), filename, GraphKind.CLASS_A)
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
        raise ValueError(f"{path}: not a third SHV beta-lactamase target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
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
        help="ARO directory or one of the third SHV beta-lactamase YAML files",
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
