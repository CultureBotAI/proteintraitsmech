#!/usr/bin/env python3
"""Rewrite the remaining KPC beta-lactamase causal-graph records.

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
    "action": "Completed remaining KPC beta-lactamase causal graphs",
    "llm_assisted": True,
}

TARGET_FILENAMES: tuple[str, ...] = (
    "kpc-53-aro3008361.yaml",
    "kpc-54-aro3005382.yaml",
    "kpc-55-aro3005383.yaml",
    "kpc-56-aro3005384.yaml",
    "kpc-57-aro3005385.yaml",
    "kpc-58-aro3006187.yaml",
    "kpc-59-aro3006188.yaml",
    "kpc-6-aro3002316.yaml",
    "kpc-60-aro3006189.yaml",
    "kpc-61-aro3006190.yaml",
    "kpc-62-aro3006191.yaml",
    "kpc-63-aro3006192.yaml",
    "kpc-64-aro3006193.yaml",
    "kpc-65-aro3006194.yaml",
    "kpc-66-aro3006195.yaml",
    "kpc-67-aro3008362.yaml",
    "kpc-68-aro3008363.yaml",
    "kpc-69-aro3008364.yaml",
    "kpc-7-aro3002317.yaml",
    "kpc-70-aro3008365.yaml",
    "kpc-71-aro3006196.yaml",
    "kpc-72-aro3006197.yaml",
    "kpc-73-aro3006198.yaml",
    "kpc-74-aro3006199.yaml",
    "kpc-75-aro3006200.yaml",
    "kpc-76-aro3006201.yaml",
    "kpc-77-aro3006202.yaml",
    "kpc-78-aro3006203.yaml",
    "kpc-79-aro3006204.yaml",
    "kpc-8-aro3002318.yaml",
    "kpc-80-aro3006205.yaml",
    "kpc-81-aro3006206.yaml",
    "kpc-82-aro3006207.yaml",
    "kpc-83-aro3007089.yaml",
    "kpc-84-aro3008366.yaml",
    "kpc-85-aro3008367.yaml",
    "kpc-86-aro3007381.yaml",
    "kpc-87-aro3007375.yaml",
    "kpc-88-aro3008368.yaml",
    "kpc-89-aro3008369.yaml",
    "kpc-9-aro3002319.yaml",
    "kpc-90-aro3007087.yaml",
    "kpc-91-aro3008370.yaml",
    "kpc-92-aro3008371.yaml",
    "kpc-93-aro3007102.yaml",
    "kpc-94-aro3007402.yaml",
    "kpc-95-aro3007383.yaml",
    "kpc-96-aro3007436.yaml",
    "kpc-97-aro3007449.yaml",
    "kpc-98-aro3007450.yaml",
    "kpc-99-aro3007452.yaml",
    "kpc-beta-lactamase-aro3000059.yaml",
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
        raise ValueError(f"{path}: not a remaining KPC beta-lactamase target: {identifier}")
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
        help="ARO directory or one of the remaining KPC beta-lactamase YAML files",
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
