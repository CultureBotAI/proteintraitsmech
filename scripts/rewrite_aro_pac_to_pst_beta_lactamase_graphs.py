#!/usr/bin/env python3
"""Rewrite PAC-through-PST beta-lactamase graphs.

These score-77 records still use the old beta-lactamase archetype. PAC and PNC
are class C serine beta-lactamases; PAD, PC1, PEN-A, PEN-B, and PME are class A
serine beta-lactamases; PEDO, PFM, PLN, POM, and PST are class B
metallo-beta-lactamases.

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

HISTORY_ACTION = "Completed PAC-to-PST beta-lactamase graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

TARGETS = (
    beta.Target("ARO:3005150", "pac-1-aro3005150.yaml", beta.GraphKind.CLASS_C),
    beta.Target("ARO:3005149", "pac-beta-lactamase-aro3005149.yaml", beta.GraphKind.CLASS_C),
    beta.Target("ARO:3008821", "pad-1-aro3008821.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3007872", "pad-beta-lactamase-aro3007872.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3008823", "pc1-aro3008823.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3000621", "pc1-beta-lactamase-blaz-aro3000621.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3003670", "pedo-1-aro3003670.yaml", beta.GraphKind.METALLO),
    beta.Target("ARO:3003714", "pedo-2-aro3003714.yaml", beta.GraphKind.METALLO),
    beta.Target("ARO:3003715", "pedo-3-aro3003715.yaml", beta.GraphKind.METALLO),
    beta.Target("ARO:3007873", "pen-a-beta-lactamase-aro3007873.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3008997", "pen-a1-aro3008997.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3008988", "pen-a10-aro3008988.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3008989", "pen-a11-aro3008989.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3008990", "pen-a12-aro3008990.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3008991", "pen-a13-aro3008991.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3008992", "pen-a15-aro3008992.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3008993", "pen-a16-aro3008993.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3008994", "pen-a17-aro3008994.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3008995", "pen-a18-aro3008995.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3008996", "pen-a19-aro3008996.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3009008", "pen-a2-aro3009008.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3008998", "pen-a20-aro3008998.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3008999", "pen-a21-aro3008999.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3009000", "pen-a22-aro3009000.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3009001", "pen-a23-aro3009001.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3009002", "pen-a24-aro3009002.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3009003", "pen-a25-aro3009003.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3009004", "pen-a26-aro3009004.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3009005", "pen-a27-aro3009005.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3009006", "pen-a28-aro3009006.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3009007", "pen-a29-aro3009007.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3009017", "pen-a3-aro3009017.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3009009", "pen-a30-aro3009009.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3009010", "pen-a31-aro3009010.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3009011", "pen-a32-aro3009011.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3009012", "pen-a33-aro3009012.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3009013", "pen-a34-aro3009013.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3009014", "pen-a35-aro3009014.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3009015", "pen-a37-aro3009015.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3009016", "pen-a38-aro3009016.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3009018", "pen-a5-aro3009018.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3009019", "pen-a6-aro3009019.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3009020", "pen-a7-aro3009020.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3009021", "pen-a8-aro3009021.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3009022", "pen-a9-aro3009022.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3007874", "pen-b-beta-lactamase-aro3007874.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3009023", "pen-b1-aro3009023.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3009024", "pen-b2-aro3009024.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3009025", "pen-b3-aro3009025.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3009026", "pen-b4-aro3009026.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3006965", "pfm-1-aro3006965.yaml", beta.GraphKind.METALLO),
    beta.Target("ARO:3006966", "pfm-2-aro3006966.yaml", beta.GraphKind.METALLO),
    beta.Target("ARO:3006967", "pfm-3-aro3006967.yaml", beta.GraphKind.METALLO),
    beta.Target("ARO:3007021", "pfm-4-aro3007021.yaml", beta.GraphKind.METALLO),
    beta.Target("ARO:3005432", "pfm-beta-lactamase-aro3005432.yaml", beta.GraphKind.METALLO),
    beta.Target("ARO:3006972", "pln-1-aro3006972.yaml", beta.GraphKind.METALLO),
    beta.Target("ARO:3005434", "pln-beta-lactamase-aro3005434.yaml", beta.GraphKind.METALLO),
    beta.Target("ARO:3006973", "pme-1-aro3006973.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3005435", "pme-beta-lactamase-aro3005435.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3009032", "pnc-1-aro3009032.yaml", beta.GraphKind.CLASS_C),
    beta.Target("ARO:3009033", "pnc-2-aro3009033.yaml", beta.GraphKind.CLASS_C),
    beta.Target("ARO:3009034", "pnc-3-aro3009034.yaml", beta.GraphKind.CLASS_C),
    beta.Target("ARO:3007875", "pnc-beta-lactamase-aro3007875.yaml", beta.GraphKind.CLASS_C),
    beta.Target("ARO:3006974", "pom-1-aro3006974.yaml", beta.GraphKind.METALLO),
    beta.Target("ARO:3006975", "pom-2-aro3006975.yaml", beta.GraphKind.METALLO),
    beta.Target("ARO:3005436", "pom-beta-lactamase-aro3005436.yaml", beta.GraphKind.METALLO),
    beta.Target("ARO:3006976", "pst-1-aro3006976.yaml", beta.GraphKind.METALLO),
    beta.Target("ARO:3006977", "pst-2-aro3006977.yaml", beta.GraphKind.METALLO),
    beta.Target("ARO:3005437", "pst-beta-lactamase-aro3005437.yaml", beta.GraphKind.METALLO),
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
        raise ValueError(f"{path}: not a PAC-to-PST beta-lactamase target: {identifier}")
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
        help="ARO directory or one PAC-to-PST beta-lactamase YAML file",
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
