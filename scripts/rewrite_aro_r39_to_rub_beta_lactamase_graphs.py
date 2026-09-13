#!/usr/bin/env python3
"""Rewrite R39-through-RUB beta-lactamase graphs.

These exact score-77 R-series records still use the old beta-lactamase
archetype. R39, RAA, RAHN, RASA, RATA, RCP, RSA2, and RUB are class A serine
beta-lactamases; RSC1 is a class C serine beta-lactamase. RAD and RSD2 are
class D and intentionally excluded from this class A/C wrapper.

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

HISTORY_ACTION = "Completed R39-to-RUB beta-lactamase graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

TARGETS = (
    beta.Target("ARO:3003565", "r39-aro3003565.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3004198", "r39-beta-lactamase-aro3004198.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3009035", "raa-1-aro3009035.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3007876", "raa-beta-lactamase-aro3007876.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3006979", "rahn-1-aro3006979.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3006980", "rahn-2-aro3006980.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3009036", "rahn-3-aro3009036.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3009037", "rahn-4-aro3009037.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3009038", "rahn-5-aro3009038.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3009039", "rahn-6-aro3009039.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3005439", "rahn-beta-lactamase-aro3005439.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3009040", "rasa-1-aro3009040.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3007877", "rasa-beta-lactamase-aro3007877.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3007801", "rata-1-aro3007801.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3007802", "rata-2-aro3007802.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3007800", "rata-beta-lactamase-aro3007800.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3003563", "rcp-1-aro3003563.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3004235", "rcp-beta-lactamase-aro3004235.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3006981", "rsa2-1-aro3006981.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3005440", "rsa2-beta-lactamase-aro3005440.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3009041", "rsc1-1-aro3009041.yaml", beta.GraphKind.CLASS_C),
    beta.Target("ARO:3007878", "rsc1-beta-lactamase-aro3007878.yaml", beta.GraphKind.CLASS_C),
    beta.Target("ARO:3006984", "rub-1-aro3006984.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3005442", "rub-beta-lactamase-aro3005442.yaml", beta.GraphKind.CLASS_A),
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
        raise ValueError(f"{path}: not an R39-to-RUB beta-lactamase target: {identifier}")
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
        help="ARO directory or one R39-to-RUB beta-lactamase YAML file",
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
