#!/usr/bin/env python3
"""Rewrite the tenth PDC beta-lactamase causal-graph batch.

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
    "action": "Completed tenth PDC beta-lactamase causal graphs",
    "llm_assisted": True,
}

TARGET_FILENAMES: tuple[str, ...] = (
    "pdc-55-aro3005039.yaml",
    "pdc-550-aro3008897.yaml",
    "pdc-551-aro3008898.yaml",
    "pdc-552-aro3008899.yaml",
    "pdc-553-aro3008900.yaml",
    "pdc-554-aro3008901.yaml",
    "pdc-555-aro3008902.yaml",
    "pdc-556-aro3008903.yaml",
    "pdc-557-aro3008904.yaml",
    "pdc-558-aro3008905.yaml",
    "pdc-559-aro3008906.yaml",
    "pdc-56-aro3005140.yaml",
    "pdc-560-aro3008907.yaml",
    "pdc-561-aro3008908.yaml",
    "pdc-562-aro3008909.yaml",
    "pdc-563-aro3008910.yaml",
    "pdc-564-aro3008911.yaml",
    "pdc-565-aro3008912.yaml",
    "pdc-566-aro3008913.yaml",
    "pdc-567-aro3008914.yaml",
    "pdc-568-aro3008915.yaml",
    "pdc-569-aro3008916.yaml",
    "pdc-57-aro3005125.yaml",
    "pdc-570-aro3008917.yaml",
    "pdc-571-aro3008918.yaml",
    "pdc-572-aro3008919.yaml",
    "pdc-573-aro3008920.yaml",
    "pdc-574-aro3008921.yaml",
    "pdc-575-aro3008922.yaml",
    "pdc-576-aro3008923.yaml",
    "pdc-577-aro3008924.yaml",
    "pdc-578-aro3008925.yaml",
    "pdc-579-aro3008926.yaml",
    "pdc-58-aro3006843.yaml",
    "pdc-580-aro3008927.yaml",
    "pdc-581-aro3008928.yaml",
    "pdc-582-aro3008929.yaml",
    "pdc-583-aro3008930.yaml",
    "pdc-584-aro3008931.yaml",
    "pdc-585-aro3008932.yaml",
    "pdc-586-aro3008933.yaml",
    "pdc-587-aro3008934.yaml",
    "pdc-588-aro3008935.yaml",
    "pdc-589-aro3008936.yaml",
    "pdc-59-aro3005137.yaml",
    "pdc-590-aro3008937.yaml",
    "pdc-591-aro3008938.yaml",
    "pdc-592-aro3008939.yaml",
    "pdc-593-aro3008940.yaml",
    "pdc-594-aro3008941.yaml",
    "pdc-595-aro3008942.yaml",
    "pdc-596-aro3008943.yaml",
    "pdc-597-aro3008944.yaml",
    "pdc-598-aro3008945.yaml",
    "pdc-599-aro3008946.yaml",
    "pdc-6-aro3002505.yaml",
    "pdc-60-aro3006844.yaml",
    "pdc-600-aro3008947.yaml",
    "pdc-601-aro3008948.yaml",
    "pdc-602-aro3008949.yaml",
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
        raise ValueError(f"{path}: not a tenth-PDC beta-lactamase target: {identifier}")
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
        help="ARO directory or one of the tenth-PDC beta-lactamase YAML files",
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
