#!/usr/bin/env python3
"""Rewrite SME-through-STA beta-lactamase graphs.

These exact score-77 S-series records still use the old beta-lactamase
archetype. SME and SPU are class A serine beta-lactamases; SRT and SST are
class C serine beta-lactamases; SPG, SPM, SPN79, SPR, SPS, and STA are class B
metallo-beta-lactamases. The alphabetically interleaved spd
aminoglycoside-phosphotransferase record is intentionally excluded from this
beta-lactamase wrapper.

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

HISTORY_ACTION = "Completed SME-to-STA beta-lactamase graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

TARGETS = (
    beta.Target("ARO:3002379", "sme-1-aro3002379.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3002380", "sme-2-aro3002380.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3002381", "sme-3-aro3002381.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3002382", "sme-4-aro3002382.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3002383", "sme-5-aro3002383.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3000055", "sme-beta-lactamase-aro3000055.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3003720", "spg-1-aro3003720.yaml", beta.GraphKind.METALLO),
    beta.Target("ARO:3004224", "spg-beta-lactamase-aro3004224.yaml", beta.GraphKind.METALLO),
    beta.Target("ARO:3003793", "spm-1-aro3003793.yaml", beta.GraphKind.METALLO),
    beta.Target("ARO:3000580", "spm-beta-lactamase-aro3000580.yaml", beta.GraphKind.METALLO),
    beta.Target("ARO:3006995", "spn79-1-aro3006995.yaml", beta.GraphKind.METALLO),
    beta.Target("ARO:3005447", "spn79-beta-lactamase-aro3005447.yaml", beta.GraphKind.METALLO),
    beta.Target("ARO:3006996", "spr-1-aro3006996.yaml", beta.GraphKind.METALLO),
    beta.Target("ARO:3005448", "spr-beta-lactamase-aro3005448.yaml", beta.GraphKind.METALLO),
    beta.Target("ARO:3006997", "sps-1-aro3006997.yaml", beta.GraphKind.METALLO),
    beta.Target("ARO:3005449", "sps-beta-lactamase-aro3005449.yaml", beta.GraphKind.METALLO),
    beta.Target("ARO:3006998", "spu-1-aro3006998.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3005450", "spu-beta-lactamase-aro3005450.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3002493", "srt-1-aro3002493.yaml", beta.GraphKind.CLASS_C),
    beta.Target("ARO:3002494", "srt-2-aro3002494.yaml", beta.GraphKind.CLASS_C),
    beta.Target("ARO:3006853", "srt-3-aro3006853.yaml", beta.GraphKind.CLASS_C),
    beta.Target("ARO:3009065", "srt-4-aro3009065.yaml", beta.GraphKind.CLASS_C),
    beta.Target("ARO:3000095", "srt-beta-lactamase-aro3000095.yaml", beta.GraphKind.CLASS_C),
    beta.Target("ARO:3006999", "sst-1-aro3006999.yaml", beta.GraphKind.CLASS_C),
    beta.Target("ARO:3005451", "sst-beta-lactamase-aro3005451.yaml", beta.GraphKind.CLASS_C),
    beta.Target("ARO:3007000", "sta-1-aro3007000.yaml", beta.GraphKind.METALLO),
    beta.Target("ARO:3005452", "sta-beta-lactamase-aro3005452.yaml", beta.GraphKind.METALLO),
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
        raise ValueError(f"{path}: not an SME-to-STA beta-lactamase target: {identifier}")
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
        help="ARO directory or one SME-to-STA beta-lactamase YAML file",
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
