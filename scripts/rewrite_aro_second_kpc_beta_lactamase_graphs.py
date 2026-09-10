#!/usr/bin/env python3
"""Rewrite the second KPC beta-lactamase causal-graph record batch.

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
    "action": "Completed second KPC beta-lactamase causal graphs",
    "llm_assisted": True,
}

TARGET_FILENAMES: tuple[str, ...] = (
    "kpc-154-aro3008280.yaml",
    "kpc-155-aro3008281.yaml",
    "kpc-156-aro3008282.yaml",
    "kpc-157-aro3008283.yaml",
    "kpc-158-aro3008284.yaml",
    "kpc-159-aro3008285.yaml",
    "kpc-16-aro3002326.yaml",
    "kpc-160-aro3008286.yaml",
    "kpc-161-aro3008287.yaml",
    "kpc-162-aro3008288.yaml",
    "kpc-163-aro3008289.yaml",
    "kpc-164-aro3008290.yaml",
    "kpc-165-aro3008291.yaml",
    "kpc-166-aro3008292.yaml",
    "kpc-167-aro3008293.yaml",
    "kpc-168-aro3008294.yaml",
    "kpc-169-aro3008295.yaml",
    "kpc-17-aro3002327.yaml",
    "kpc-170-aro3008296.yaml",
    "kpc-171-aro3008297.yaml",
    "kpc-172-aro3008298.yaml",
    "kpc-173-aro3008299.yaml",
    "kpc-174-aro3008300.yaml",
    "kpc-175-aro3008301.yaml",
    "kpc-176-aro3008302.yaml",
    "kpc-177-aro3008303.yaml",
    "kpc-178-aro3008304.yaml",
    "kpc-179-aro3008305.yaml",
    "kpc-18-aro3002328.yaml",
    "kpc-180-aro3008306.yaml",
    "kpc-181-aro3008307.yaml",
    "kpc-182-aro3008308.yaml",
    "kpc-183-aro3008309.yaml",
    "kpc-184-aro3008310.yaml",
    "kpc-185-aro3008311.yaml",
    "kpc-186-aro3008312.yaml",
    "kpc-187-aro3008313.yaml",
    "kpc-188-aro3008314.yaml",
    "kpc-189-aro3008315.yaml",
    "kpc-19-aro3002329.yaml",
    "kpc-190-aro3008316.yaml",
    "kpc-191-aro3008317.yaml",
    "kpc-192-aro3008318.yaml",
    "kpc-193-aro3008319.yaml",
    "kpc-194-aro3008320.yaml",
    "kpc-195-aro3008321.yaml",
    "kpc-196-aro3008322.yaml",
    "kpc-197-aro3008323.yaml",
    "kpc-2-aro3002312.yaml",
    "kpc-20-aro3003144.yaml",
    "kpc-201-aro3008324.yaml",
    "kpc-202-aro3008325.yaml",
    "kpc-203-aro3008326.yaml",
    "kpc-204-aro3008327.yaml",
    "kpc-205-aro3008328.yaml",
    "kpc-206-aro3008329.yaml",
    "kpc-207-aro3008330.yaml",
    "kpc-208-aro3008331.yaml",
    "kpc-209-aro3008332.yaml",
    "kpc-21-aro3003145.yaml",
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
        raise ValueError(f"{path}: not a second KPC beta-lactamase target: {identifier}")
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
        help="ARO directory or one of the second KPC beta-lactamase YAML files",
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
