#!/usr/bin/env python3
"""Rewrite the fourth PDC beta-lactamase causal-graph batch.

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
    "action": "Completed fourth PDC beta-lactamase causal graphs",
    "llm_assisted": True,
}

TARGET_FILENAMES: tuple[str, ...] = (
    "pdc-222-aro3006602.yaml",
    "pdc-223-aro3006603.yaml",
    "pdc-224-aro3006604.yaml",
    "pdc-225-aro3005274.yaml",
    "pdc-226-aro3006605.yaml",
    "pdc-227-aro3006606.yaml",
    "pdc-228-aro3006607.yaml",
    "pdc-229-aro3006608.yaml",
    "pdc-23-aro3005155.yaml",
    "pdc-230-aro3006609.yaml",
    "pdc-231-aro3005304.yaml",
    "pdc-232-aro3006610.yaml",
    "pdc-233-aro3006611.yaml",
    "pdc-234-aro3006612.yaml",
    "pdc-235-aro3006613.yaml",
    "pdc-236-aro3006614.yaml",
    "pdc-237-aro3006615.yaml",
    "pdc-238-aro3006616.yaml",
    "pdc-239-aro3006617.yaml",
    "pdc-24-aro3006618.yaml",
    "pdc-240-aro3005143.yaml",
    "pdc-241-aro3006619.yaml",
    "pdc-242-aro3006620.yaml",
    "pdc-243-aro3006621.yaml",
    "pdc-244-aro3006622.yaml",
    "pdc-245-aro3006623.yaml",
    "pdc-246-aro3006624.yaml",
    "pdc-247-aro3006625.yaml",
    "pdc-248-aro3006626.yaml",
    "pdc-249-aro3006627.yaml",
    "pdc-25-aro3006628.yaml",
    "pdc-250-aro3006629.yaml",
    "pdc-251-aro3006630.yaml",
    "pdc-252-aro3006631.yaml",
    "pdc-253-aro3006632.yaml",
    "pdc-254-aro3006633.yaml",
    "pdc-255-aro3005297.yaml",
    "pdc-256-aro3006634.yaml",
    "pdc-257-aro3005311.yaml",
    "pdc-258-aro3005281.yaml",
    "pdc-259-aro3006635.yaml",
    "pdc-26-aro3006636.yaml",
    "pdc-260-aro3006637.yaml",
    "pdc-261-aro3006638.yaml",
    "pdc-262-aro3006639.yaml",
    "pdc-263-aro3006640.yaml",
    "pdc-264-aro3005284.yaml",
    "pdc-265-aro3006641.yaml",
    "pdc-266-aro3006642.yaml",
    "pdc-267-aro3006643.yaml",
    "pdc-268-aro3006644.yaml",
    "pdc-270-aro3006645.yaml",
    "pdc-271-aro3006646.yaml",
    "pdc-272-aro3005296.yaml",
    "pdc-273-aro3006647.yaml",
    "pdc-274-aro3006648.yaml",
    "pdc-275-aro3006649.yaml",
    "pdc-276-aro3006650.yaml",
    "pdc-277-aro3006651.yaml",
    "pdc-278-aro3006652.yaml",
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
        raise ValueError(f"{path}: not a fourth-PDC beta-lactamase target: {identifier}")
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
        help="ARO directory or one of the fourth-PDC beta-lactamase YAML files",
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
