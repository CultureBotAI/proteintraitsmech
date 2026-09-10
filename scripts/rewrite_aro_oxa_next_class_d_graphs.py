#!/usr/bin/env python3
"""Describe and evidence the next exact OXA class D beta-lactamase graph slice.

Dry-run by default; pass ``--apply`` to write.
"""

from __future__ import annotations

import argparse
import copy
import sys
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from record_io import append_to_section, replace_block  # noqa: E402
from rewrite_aro_oxa_class_d_graphs import (  # noqa: E402
    ARO_DIR,
    HISTORY_CURATOR,
    Target,
    _dicts,
    _dump,
    enrich_record,
)

HISTORY_ACTION = "Completed additional OXA class D beta-lactamase causal graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

DRUG_CLASS_EDGE_PREDICATE = "ARO:2000001"

TARGETS: tuple[Target, ...] = (
    Target("ARO:3008425", "oxa-1004-aro3008425.yaml"),
    Target("ARO:3008435", "oxa-1014-aro3008435.yaml"),
    Target("ARO:3008439", "oxa-1018-aro3008439.yaml"),
    Target("ARO:3008440", "oxa-1019-aro3008440.yaml"),
    Target("ARO:3008441", "oxa-1020-aro3008441.yaml"),
    Target("ARO:3008442", "oxa-1021-aro3008442.yaml"),
    Target("ARO:3008443", "oxa-1022-aro3008443.yaml"),
    Target("ARO:3008444", "oxa-1023-aro3008444.yaml"),
    Target("ARO:3008445", "oxa-1024-aro3008445.yaml"),
    Target("ARO:3008446", "oxa-1025-aro3008446.yaml"),
    Target("ARO:3008447", "oxa-1026-aro3008447.yaml"),
    Target("ARO:3008448", "oxa-1027-aro3008448.yaml"),
    Target("ARO:3008449", "oxa-1028-aro3008449.yaml"),
    Target("ARO:3008450", "oxa-1029-aro3008450.yaml"),
    Target("ARO:3008451", "oxa-1030-aro3008451.yaml"),
    Target("ARO:3008452", "oxa-1031-aro3008452.yaml"),
    Target("ARO:3008453", "oxa-1032-aro3008453.yaml"),
    Target("ARO:3008454", "oxa-1033-aro3008454.yaml"),
    Target("ARO:3008455", "oxa-1034-aro3008455.yaml"),
    Target("ARO:3008456", "oxa-1035-aro3008456.yaml"),
    Target("ARO:3008517", "oxa-1099-aro3008517.yaml"),
    Target("ARO:3008518", "oxa-1100-aro3008518.yaml"),
    Target("ARO:3008519", "oxa-1101-aro3008519.yaml"),
    Target("ARO:3008520", "oxa-1102-aro3008520.yaml"),
    Target("ARO:3008521", "oxa-1103-aro3008521.yaml"),
    Target("ARO:3008522", "oxa-1104-aro3008522.yaml"),
    Target("ARO:3008523", "oxa-1105-aro3008523.yaml"),
    Target("ARO:3008524", "oxa-1106-aro3008524.yaml"),
    Target("ARO:3008525", "oxa-1107-aro3008525.yaml"),
    Target("ARO:3008542", "oxa-1124-aro3008542.yaml"),
    Target("ARO:3008543", "oxa-1125-aro3008543.yaml"),
    Target("ARO:3008544", "oxa-1126-aro3008544.yaml"),
    Target("ARO:3008545", "oxa-1127-aro3008545.yaml"),
    Target("ARO:3008546", "oxa-1128-aro3008546.yaml"),
    Target("ARO:3008547", "oxa-1129-aro3008547.yaml"),
    Target("ARO:3008548", "oxa-1130-aro3008548.yaml"),
    Target("ARO:3008549", "oxa-1131-aro3008549.yaml"),
    Target("ARO:3008550", "oxa-1132-aro3008550.yaml"),
    Target("ARO:3008551", "oxa-1133-aro3008551.yaml"),
    Target("ARO:3008552", "oxa-1134-aro3008552.yaml"),
    Target("ARO:3008553", "oxa-1135-aro3008553.yaml"),
    Target("ARO:3007698", "oxa-114-like-beta-lactamase-aro3007698.yaml"),
    Target("ARO:3008558", "oxa-1140-aro3008558.yaml"),
    Target("ARO:3001609", "oxa-114a-aro3001609.yaml"),
    Target("ARO:3005702", "oxa-114b-aro3005702.yaml"),
    Target("ARO:3005703", "oxa-114c-aro3005703.yaml"),
    Target("ARO:3005704", "oxa-114d-aro3005704.yaml"),
    Target("ARO:3005705", "oxa-114e-aro3005705.yaml"),
    Target("ARO:3005706", "oxa-114f-aro3005706.yaml"),
    Target("ARO:3005707", "oxa-114g-aro3005707.yaml"),
    Target("ARO:3005708", "oxa-114h-aro3005708.yaml"),
    Target("ARO:3005709", "oxa-114i-aro3005709.yaml"),
    Target("ARO:3005710", "oxa-114j-aro3005710.yaml"),
    Target("ARO:3005711", "oxa-114k-aro3005711.yaml"),
    Target("ARO:3005712", "oxa-114l-aro3005712.yaml"),
    Target("ARO:3005713", "oxa-114m-aro3005713.yaml"),
    Target("ARO:3005714", "oxa-114n-aro3005714.yaml"),
    Target("ARO:3005715", "oxa-114p-aro3005715.yaml"),
    Target("ARO:3005716", "oxa-114q-aro3005716.yaml"),
    Target("ARO:3005717", "oxa-114r-aro3005717.yaml"),
    Target("ARO:3005718", "oxa-114s-aro3005718.yaml"),
    Target("ARO:3005719", "oxa-114t-aro3005719.yaml"),
    Target("ARO:3005720", "oxa-114u-aro3005720.yaml"),
    Target("ARO:3005721", "oxa-114v-aro3005721.yaml"),
    Target("ARO:3005722", "oxa-114w-aro3005722.yaml"),
    Target("ARO:3005723", "oxa-114x-aro3005723.yaml"),
    Target("ARO:3008575", "oxa-1157-aro3008575.yaml"),
    Target("ARO:3008580", "oxa-1162-aro3008580.yaml"),
    Target("ARO:3008592", "oxa-1174-aro3008592.yaml"),
    Target("ARO:3001768", "oxa-118-aro3001768.yaml"),
    Target("ARO:3008604", "oxa-1188-aro3008604.yaml"),
    Target("ARO:3001775", "oxa-119-aro3001775.yaml"),
    Target("ARO:3008610", "oxa-1198-aro3008610.yaml"),
    Target("ARO:3008611", "oxa-1199-aro3008611.yaml"),
    Target("ARO:3001407", "oxa-12-aro3001407.yaml"),
    Target("ARO:3007699", "oxa-12-like-beta-lactamase-aro3007699.yaml"),
    Target("ARO:3008654", "oxa-1244-aro3008654.yaml"),
    Target("ARO:3008655", "oxa-1245-aro3008655.yaml"),
    Target("ARO:3008656", "oxa-1246-aro3008656.yaml"),
    Target("ARO:3008660", "oxa-1250-aro3008660.yaml"),
    Target("ARO:3008662", "oxa-1252-aro3008662.yaml"),
    Target("ARO:3008663", "oxa-1253-aro3008663.yaml"),
    Target("ARO:3008664", "oxa-1254-aro3008664.yaml"),
    Target("ARO:3008665", "oxa-1255-aro3008665.yaml"),
    Target("ARO:3008666", "oxa-1256-aro3008666.yaml"),
    Target("ARO:3008677", "oxa-1267-aro3008677.yaml"),
    Target("ARO:3008678", "oxa-1268-aro3008678.yaml"),
    Target("ARO:3008679", "oxa-1269-aro3008679.yaml"),
    Target("ARO:3008680", "oxa-1270-aro3008680.yaml"),
    Target("ARO:3008681", "oxa-1271-aro3008681.yaml"),
    Target("ARO:3008682", "oxa-1272-aro3008682.yaml"),
    Target("ARO:3008683", "oxa-1273-aro3008683.yaml"),
    Target("ARO:3008684", "oxa-1274-aro3008684.yaml"),
    Target("ARO:3008685", "oxa-1275-aro3008685.yaml"),
    Target("ARO:3008686", "oxa-1276-aro3008686.yaml"),
    Target("ARO:3008687", "oxa-1277-aro3008687.yaml"),
    Target("ARO:3008688", "oxa-1278-aro3008688.yaml"),
    Target("ARO:3008689", "oxa-1279-aro3008689.yaml"),
    Target("ARO:3008690", "oxa-1280-aro3008690.yaml"),
    Target("ARO:3008691", "oxa-1281-aro3008691.yaml"),
)
TARGET_BY_ID = {target.identifier: target for target in TARGETS}


def _record_without_drug_edges(record: dict[str, Any]) -> dict[str, Any]:
    out = copy.deepcopy(record)
    graphs = _dicts(out.get("causal_graphs"))
    if len(graphs) == 1:
        graph = graphs[0]
        graph["edges"] = [
            edge
            for edge in _dicts(graph.get("edges"))
            if edge.get("predicate_id") != DRUG_CLASS_EDGE_PREDICATE
        ]
    return out


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not a targeted OXA class D record: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    validation_record = _record_without_drug_edges(record)
    enriched, changed = enrich_record(validation_record, target)
    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    history = _dicts(enriched.get("curation_history"))
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
        help="ARO directory or one of the targeted OXA class D beta-lactamase YAML files",
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
