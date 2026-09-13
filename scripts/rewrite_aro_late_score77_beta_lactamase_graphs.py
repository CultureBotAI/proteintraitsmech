#!/usr/bin/env python3
"""Rewrite late score-77 beta-lactamase graphs.

These exact score-77 records still use the old beta-lactamase archetype. The
subclass-B, TTU, varG, VMB, YEM, and ZOG records are class B
metallo-beta-lactamases; YOC is a class C serine beta-lactamase. Non-
beta-lactamase records interleaved in the score queue are intentionally
excluded from this exact wrapper.

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

HISTORY_ACTION = "Completed late score-77 beta-lactamase graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

TARGETS = (
    beta.Target(
        "ARO:3007117",
        "subclass-b1-bacteroides-xylanisolvens-crx-beta-lactamase-aro3007117.yaml",
        beta.GraphKind.METALLO,
    ),
    beta.Target(
        "ARO:3004227",
        "subclass-b1-pedo-beta-lactamase-aro3004227.yaml",
        beta.GraphKind.METALLO,
    ),
    beta.Target(
        "ARO:3004288",
        "subclass-b1-vibrio-cholerae-varg-beta-lactamase-aro3004288.yaml",
        beta.GraphKind.METALLO,
    ),
    beta.Target(
        "ARO:3004220",
        "subclass-b3-pedo-beta-lactamase-aro3004220.yaml",
        beta.GraphKind.METALLO,
    ),
    beta.Target("ARO:3007002", "ttu-1-aro3007002.yaml", beta.GraphKind.METALLO),
    beta.Target("ARO:3005454", "ttu-beta-lactamase-aro3005454.yaml", beta.GraphKind.METALLO),
    beta.Target("ARO:3004289", "vibrio-cholerae-varg-aro3004289.yaml", beta.GraphKind.METALLO),
    beta.Target("ARO:3005015", "vmb-1-aro3005015.yaml", beta.GraphKind.METALLO),
    beta.Target("ARO:3005014", "vmb-beta-lactamase-aro3005014.yaml", beta.GraphKind.METALLO),
    beta.Target("ARO:3007005", "yem-1-aro3007005.yaml", beta.GraphKind.METALLO),
    beta.Target("ARO:3005457", "yem-beta-lactamase-aro3005457.yaml", beta.GraphKind.METALLO),
    beta.Target("ARO:3009096", "yoc-1-aro3009096.yaml", beta.GraphKind.CLASS_C),
    beta.Target("ARO:3007882", "yoc-beta-lactamase-aro3007882.yaml", beta.GraphKind.CLASS_C),
    beta.Target("ARO:3007006", "zog-1-aro3007006.yaml", beta.GraphKind.METALLO),
    beta.Target("ARO:3005458", "zog-beta-lactamase-aro3005458.yaml", beta.GraphKind.METALLO),
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


def enrich_record(
    record: dict[str, Any],
    target: beta.Target,
) -> tuple[dict[str, Any], bool]:
    return beta.enrich_record(record, target)


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not a late score-77 beta-lactamase target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    history = beta._dicts(record.get("curation_history"))
    if not any(item.get("action") == HISTORY_ACTION for item in history):
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
        help="ARO directory or one late score-77 beta-lactamase YAML file",
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
