#!/usr/bin/env python3
"""Rewrite final GES and first GOB beta-lactamase causal-graph records.

These low-scoring class A and metallo-beta-lactamase records still have old
canonical beta-lactamase graphs with sparse edge descriptions and
single-reference evidence. This batch finishes GES and starts GOB.

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
    "action": "Completed final GES and first GOB beta-lactamase causal graphs",
    "llm_assisted": True,
}

TARGET_FILENAMES: tuple[str, ...] = (
    "ges-47-aro3007825.yaml",
    "ges-48-aro3007826.yaml",
    "ges-49-aro3007827.yaml",
    "ges-5-aro3002334.yaml",
    "ges-50-aro3007828.yaml",
    "ges-51-aro3007829.yaml",
    "ges-52-aro3007830.yaml",
    "ges-53-aro3007831.yaml",
    "ges-54-aro3007832.yaml",
    "ges-55-aro3007833.yaml",
    "ges-56-aro3007834.yaml",
    "ges-57-aro3007835.yaml",
    "ges-58-aro3008185.yaml",
    "ges-59-aro3008186.yaml",
    "ges-6-aro3002335.yaml",
    "ges-60-aro3008187.yaml",
    "ges-61-aro3008188.yaml",
    "ges-62-aro3008189.yaml",
    "ges-65-aro3008190.yaml",
    "ges-66-aro3008191.yaml",
    "ges-7-aro3002336.yaml",
    "ges-8-aro3002337.yaml",
    "ges-9-aro3002338.yaml",
    "ges-beta-lactamase-aro3000066.yaml",
    "gob-1-aro3000850.yaml",
    "gob-10-aro3004802.yaml",
    "gob-11-aro3004803.yaml",
    "gob-12-aro3004804.yaml",
    "gob-13-aro3004805.yaml",
    "gob-14-aro3004806.yaml",
    "gob-15-aro3004807.yaml",
    "gob-16-aro3004808.yaml",
    "gob-17-aro3008195.yaml",
    "gob-18-aro3004213.yaml",
    "gob-19-aro3005668.yaml",
    "gob-2-aro3004809.yaml",
    "gob-20-aro3005669.yaml",
    "gob-21-aro3005670.yaml",
    "gob-22-aro3005671.yaml",
    "gob-23-aro3005672.yaml",
    "gob-24-aro3005673.yaml",
    "gob-25-aro3005674.yaml",
    "gob-26-aro3005675.yaml",
    "gob-27-aro3005676.yaml",
    "gob-28-aro3005677.yaml",
    "gob-29-aro3005678.yaml",
    "gob-3-aro3004810.yaml",
    "gob-30-aro3005679.yaml",
    "gob-31-aro3005680.yaml",
    "gob-32-aro3005681.yaml",
    "gob-33-aro3005682.yaml",
    "gob-34-aro3005683.yaml",
    "gob-35-aro3005684.yaml",
    "gob-36-aro3005685.yaml",
    "gob-37-aro3005686.yaml",
    "gob-38-aro3005687.yaml",
    "gob-39-aro3005688.yaml",
    "gob-4-aro3004811.yaml",
    "gob-40-aro3005689.yaml",
    "gob-41-aro3005690.yaml",
    "gob-42-aro3005691.yaml",
)


def identifier_from_filename(filename: str) -> str:
    aro_number = filename.rsplit("-aro", maxsplit=1)[1].removesuffix(".yaml")
    return f"ARO:{aro_number}"


def graph_kind_from_filename(filename: str) -> beta.GraphKind:
    if filename.startswith("ges-"):
        return beta.GraphKind.CLASS_A
    if filename.startswith("gob-"):
        return beta.GraphKind.METALLO
    raise ValueError(f"no beta-lactamase graph kind is configured for {filename}")


TARGETS: tuple[beta.Target, ...] = tuple(
    beta.Target(
        identifier_from_filename(filename),
        filename,
        graph_kind_from_filename(filename),
    )
    for filename in TARGET_FILENAMES
)
TARGET_BY_ID = {target.identifier: target for target in TARGETS}

GOB10_DRUG_NODES: tuple[dict[str, str], ...] = (
    {
        "node_id": "drug0",
        "label": "carbapenem",
        "node_type": "CHEMICAL",
        "grounding": "ARO:0000020",
    },
    {
        "node_id": "drug1",
        "label": "cephalosporin",
        "node_type": "CHEMICAL",
        "grounding": "ARO:0000032",
    },
    {
        "node_id": "drug2",
        "label": "penicillin beta-lactam",
        "node_type": "CHEMICAL",
        "grounding": "ARO:3000008",
    },
)

GOB10_DRUG_RELATIONS: tuple[tuple[str, str, str], ...] = (
    ("drug0", "ARO:0000020", "carbapenem"),
    ("drug1", "ARO:0000032", "cephalosporin"),
    ("drug2", "ARO:3000008", "penicillin beta-lactam"),
)


def _gob10_old_graph() -> dict[str, Any]:
    return {
        "nodes": [dict(node) for node in GOB10_DRUG_NODES],
        "edges": [
            {
                "subject": "determinant",
                "predicate": "confers resistance to (drug class)",
                "predicate_id": "ARO:2000001",
                "object": drug_node_id,
                "evidence": [
                    {
                        "reference": "ARO:3004212",
                        "snippet": (
                            "relationship: confers_resistance_to_drug_class "
                            f"{aro_id} ! {label}"
                        ),
                        "notes": (
                            "Asserted on ARO:3004212 (GOB beta-lactamase), an "
                            "is_a ancestor of this record's ARO:3004802; "
                            "inherited by this variant. CARD/ARO release in "
                            "data/raw/aro/aro.obo."
                        ),
                    }
                ],
            }
            for drug_node_id, aro_id, label in GOB10_DRUG_RELATIONS
        ],
    }


def enrich_record(
    record: dict[str, Any],
    target: beta.Target,
) -> tuple[dict[str, Any], bool]:
    if target.identifier == "ARO:3004802":
        out = dict(record)
        out["causal_graphs"] = [
            beta._graph(record, _gob10_old_graph(), beta.METALLO_PARTS)
        ]
        return out, out != record

    return beta.enrich_record(record, target)


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
        raise ValueError(f"{path}: not a final-GES/first-GOB beta-lactamase target: {identifier}")
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
        help="ARO directory or one of the final-GES/first-GOB beta-lactamase YAML files",
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
