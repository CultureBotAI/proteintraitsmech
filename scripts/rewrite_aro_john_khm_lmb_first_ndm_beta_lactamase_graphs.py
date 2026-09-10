#!/usr/bin/env python3
"""Rewrite JOHN/KHM/LMB and first NDM beta-lactamase records.

These score-79 metallo-beta-lactamase records still have old canonical
beta-lactamase graphs with sparse edge descriptions and single-reference
evidence.

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
    "action": "Completed JOHN, KHM, LMB, and first NDM beta-lactamase causal graphs",
    "llm_assisted": True,
}

TARGET_FILENAMES: tuple[str, ...] = (
    "john-beta-lactamase-aro3004202.yaml",
    "khm-1-aro3000847.yaml",
    "khm-2-aro3008228.yaml",
    "khm-beta-lactamase-aro3004207.yaml",
    "lmb-1-aro3005018.yaml",
    "lmb-beta-lactamase-aro3005017.yaml",
    "ndm-1-aro3000589.yaml",
    "ndm-10-aro3002360.yaml",
    "ndm-11-aro3002361.yaml",
    "ndm-12-aro3002362.yaml",
    "ndm-13-aro3003182.yaml",
    "ndm-14-aro3003183.yaml",
    "ndm-15-aro3003663.yaml",
    "ndm-16a-aro3003664.yaml",
    "ndm-16b-aro3007202.yaml",
    "ndm-17-aro3004093.yaml",
    "ndm-18-aro3004861.yaml",
    "ndm-19-aro3004862.yaml",
    "ndm-2-aro3000590.yaml",
    "ndm-20-aro3004863.yaml",
    "ndm-21-aro3004864.yaml",
    "ndm-22-aro3004865.yaml",
    "ndm-23-aro3004866.yaml",
    "ndm-24-aro3004867.yaml",
    "ndm-25-aro3004868.yaml",
    "ndm-26-aro3004869.yaml",
    "ndm-27-aro3004870.yaml",
    "ndm-28-aro3004871.yaml",
    "ndm-29-aro3005131.yaml",
    "ndm-3-aro3002354.yaml",
    "ndm-30-aro3005700.yaml",
    "ndm-31-aro3005701.yaml",
    "ndm-33-aro3007023.yaml",
    "ndm-34-aro3007211.yaml",
    "ndm-35-aro3007212.yaml",
    "ndm-36-aro3007213.yaml",
    "ndm-37-aro3007214.yaml",
    "ndm-38-aro3007215.yaml",
    "ndm-39-aro3007216.yaml",
    "ndm-4-aro3002355.yaml",
    "ndm-40-aro3007217.yaml",
    "ndm-41-aro3007218.yaml",
    "ndm-42-aro3007219.yaml",
    "ndm-43-aro3007220.yaml",
    "ndm-44-aro3007443.yaml",
    "ndm-45-aro3007444.yaml",
    "ndm-46-aro3007445.yaml",
    "ndm-47-aro3007447.yaml",
    "ndm-48-aro3008396.yaml",
    "ndm-49-aro3008397.yaml",
    "ndm-5-aro3000467.yaml",
    "ndm-50-aro3008398.yaml",
    "ndm-51-aro3008399.yaml",
    "ndm-52-aro3008400.yaml",
    "ndm-53-aro3008401.yaml",
    "ndm-54-aro3008402.yaml",
    "ndm-55-aro3008403.yaml",
    "ndm-56-aro3008404.yaml",
    "ndm-57-aro3008405.yaml",
    "ndm-58-aro3008406.yaml",
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
        raise ValueError(f"{path}: not a JOHN/KHM/LMB/first-NDM beta-lactamase target: {identifier}")
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
        help="ARO directory or one of the JOHN/KHM/LMB/first-NDM beta-lactamase YAML files",
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
