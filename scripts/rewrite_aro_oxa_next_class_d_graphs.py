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
    Target("ARO:3008692", "oxa-1282-aro3008692.yaml"),
    Target("ARO:3008693", "oxa-1283-aro3008693.yaml"),
    Target("ARO:3008694", "oxa-1284-aro3008694.yaml"),
    Target("ARO:3008695", "oxa-1285-aro3008695.yaml"),
    Target("ARO:3008696", "oxa-1286-aro3008696.yaml"),
    Target("ARO:3008697", "oxa-1287-aro3008697.yaml"),
    Target("ARO:3008698", "oxa-1288-aro3008698.yaml"),
    Target("ARO:3008699", "oxa-1289-aro3008699.yaml"),
    Target("ARO:3001811", "oxa-129-aro3001811.yaml"),
    Target("ARO:3008700", "oxa-1290-aro3008700.yaml"),
    Target("ARO:3008701", "oxa-1291-aro3008701.yaml"),
    Target("ARO:3008702", "oxa-1292-aro3008702.yaml"),
    Target("ARO:3008703", "oxa-1293-aro3008703.yaml"),
    Target("ARO:3008704", "oxa-1294-aro3008704.yaml"),
    Target("ARO:3008705", "oxa-1295-aro3008705.yaml"),
    Target("ARO:3008706", "oxa-1296-aro3008706.yaml"),
    Target("ARO:3008707", "oxa-1297-aro3008707.yaml"),
    Target("ARO:3008708", "oxa-1298-aro3008708.yaml"),
    Target("ARO:3008709", "oxa-1299-aro3008709.yaml"),
    Target("ARO:3008710", "oxa-1300-aro3008710.yaml"),
    Target("ARO:3008711", "oxa-1301-aro3008711.yaml"),
    Target("ARO:3001765", "oxa-136-aro3001765.yaml"),
    Target("ARO:3001767", "oxa-137-aro3001767.yaml"),
    Target("ARO:3001476", "oxa-184-aro3001476.yaml"),
    Target("ARO:3007702", "oxa-184-like-beta-lactamase-aro3007702.yaml"),
    Target("ARO:3001477", "oxa-185-aro3001477.yaml"),
    Target("ARO:3001766", "oxa-192-aro3001766.yaml"),
    Target("ARO:3001478", "oxa-193-aro3001478.yaml"),
    Target("ARO:3001483", "oxa-205-aro3001483.yaml"),
    Target("ARO:3001722", "oxa-266-aro3001722.yaml"),
    Target("ARO:3007712", "oxa-266-like-beta-lactamase-aro3007712.yaml"),
    Target("ARO:3001749", "oxa-294-aro3001749.yaml"),
    Target("ARO:3007715", "oxa-294-like-beta-lactamase-aro3007715.yaml"),
    Target("ARO:3001750", "oxa-295-aro3001750.yaml"),
    Target("ARO:3001752", "oxa-297-aro3001752.yaml"),
    Target("ARO:3001753", "oxa-298-aro3001753.yaml"),
    Target("ARO:3001551", "oxa-364-aro3001551.yaml"),
    Target("ARO:3007716", "oxa-364-like-beta-lactamase-aro3007716.yaml"),
    Target("ARO:3001581", "oxa-395-aro3001581.yaml"),
    Target("ARO:3001582", "oxa-396-aro3001582.yaml"),
    Target("ARO:3001769", "oxa-42-aro3001769.yaml"),
    Target("ARO:3007718", "oxa-42-like-beta-lactamase-aro3007718.yaml"),
    Target("ARO:3001770", "oxa-43-aro3001770.yaml"),
    Target("ARO:3003602", "oxa-446-aro3003602.yaml"),
    Target("ARO:3003603", "oxa-447-aro3003603.yaml"),
    Target("ARO:3003604", "oxa-448-aro3003604.yaml"),
    Target("ARO:3003605", "oxa-449-aro3003605.yaml"),
    Target("ARO:3003606", "oxa-450-aro3003606.yaml"),
    Target("ARO:3003607", "oxa-451-aro3003607.yaml"),
    Target("ARO:3003608", "oxa-452-aro3003608.yaml"),
    Target("ARO:3003609", "oxa-453-aro3003609.yaml"),
    Target("ARO:3003611", "oxa-455-aro3003611.yaml"),
    Target("ARO:3001797", "oxa-46-aro3001797.yaml"),
    Target("ARO:3007720", "oxa-46-like-beta-lactamase-aro3007720.yaml"),
    Target("ARO:3003616", "oxa-460-aro3003616.yaml"),
    Target("ARO:3003617", "oxa-461-aro3003617.yaml"),
    Target("ARO:3003621", "oxa-465-aro3003621.yaml"),
    Target("ARO:3003622", "oxa-466-aro3003622.yaml"),
    Target("ARO:3003626", "oxa-470-aro3003626.yaml"),
    Target("ARO:3003627", "oxa-471-aro3003627.yaml"),
    Target("ARO:3003628", "oxa-472-aro3003628.yaml"),
    Target("ARO:3003629", "oxa-473-aro3003629.yaml"),
    Target("ARO:3003631", "oxa-474-aro3003631.yaml"),
    Target("ARO:3003632", "oxa-475-aro3003632.yaml"),
    Target("ARO:3003633", "oxa-476-aro3003633.yaml"),
    Target("ARO:3003634", "oxa-477-aro3003634.yaml"),
    Target("ARO:3003635", "oxa-478-aro3003635.yaml"),
    Target("ARO:3003636", "oxa-479-aro3003636.yaml"),
    Target("ARO:3003642", "oxa-485-aro3003642.yaml"),
    Target("ARO:3003643", "oxa-486-aro3003643.yaml"),
    Target("ARO:3003645", "oxa-488-aro3003645.yaml"),
    Target("ARO:3005724", "oxa-489-aro3005724.yaml"),
    Target("ARO:3005726", "oxa-493-aro3005726.yaml"),
    Target("ARO:3007722", "oxa-493-like-beta-lactamase-aro3007722.yaml"),
    Target("ARO:3005727", "oxa-494-aro3005727.yaml"),
    Target("ARO:3001400", "oxa-5-aro3001400.yaml"),
    Target("ARO:3007723", "oxa-5-like-beta-lactamase-aro3007723.yaml"),
    Target("ARO:3001796", "oxa-50-aro3001796.yaml"),
    Target("ARO:3007724", "oxa-50-like-beta-lactamase-aro3007724.yaml"),
    Target("ARO:3005743", "oxa-513-aro3005743.yaml"),
    Target("ARO:3005748", "oxa-518-aro3005748.yaml"),
    Target("ARO:3005772", "oxa-548-aro3005772.yaml"),
    Target("ARO:3007726", "oxa-548-like-beta-lactamase-aro3007726.yaml"),
    Target("ARO:3005773", "oxa-549-aro3005773.yaml"),
    Target("ARO:3005774", "oxa-550-aro3005774.yaml"),
    Target("ARO:3005775", "oxa-551-aro3005775.yaml"),
    Target("ARO:3005776", "oxa-552-aro3005776.yaml"),
    Target("ARO:3005777", "oxa-553-aro3005777.yaml"),
    Target("ARO:3001771", "oxa-57-aro3001771.yaml"),
    Target("ARO:3005798", "oxa-577-aro3005798.yaml"),
    Target("ARO:3005799", "oxa-578-aro3005799.yaml"),
    Target("ARO:3005800", "oxa-579-aro3005800.yaml"),
    Target("ARO:3005801", "oxa-580-aro3005801.yaml"),
    Target("ARO:3005802", "oxa-581-aro3005802.yaml"),
    Target("ARO:3005803", "oxa-582-aro3005803.yaml"),
    Target("ARO:3005804", "oxa-583-aro3005804.yaml"),
    Target("ARO:3005805", "oxa-584-aro3005805.yaml"),
    Target("ARO:3005806", "oxa-585-aro3005806.yaml"),
    Target("ARO:3005807", "oxa-586-aro3005807.yaml"),
    Target("ARO:3005808", "oxa-587-aro3005808.yaml"),
    Target("ARO:3005809", "oxa-588-aro3005809.yaml"),
    Target("ARO:3005810", "oxa-589-aro3005810.yaml"),
    Target("ARO:3001772", "oxa-59-aro3001772.yaml"),
    Target("ARO:3005811", "oxa-590-aro3005811.yaml"),
    Target("ARO:3005812", "oxa-591-aro3005812.yaml"),
    Target("ARO:3005813", "oxa-592-aro3005813.yaml"),
    Target("ARO:3005814", "oxa-593-aro3005814.yaml"),
    Target("ARO:3005815", "oxa-594-aro3005815.yaml"),
    Target("ARO:3005816", "oxa-595-aro3005816.yaml"),
    Target("ARO:3005817", "oxa-596-aro3005817.yaml"),
    Target("ARO:3005818", "oxa-597-aro3005818.yaml"),
    Target("ARO:3005819", "oxa-598-aro3005819.yaml"),
    Target("ARO:3005820", "oxa-599-aro3005820.yaml"),
    Target("ARO:3005821", "oxa-600-aro3005821.yaml"),
    Target("ARO:3005822", "oxa-601-aro3005822.yaml"),
    Target("ARO:3005823", "oxa-602-aro3005823.yaml"),
    Target("ARO:3005824", "oxa-603-aro3005824.yaml"),
    Target("ARO:3005825", "oxa-604-aro3005825.yaml"),
    Target("ARO:3005826", "oxa-605-aro3005826.yaml"),
    Target("ARO:3005827", "oxa-606-aro3005827.yaml"),
    Target("ARO:3005828", "oxa-607-aro3005828.yaml"),
    Target("ARO:3005829", "oxa-608-aro3005829.yaml"),
    Target("ARO:3005830", "oxa-609-aro3005830.yaml"),
    Target("ARO:3001773", "oxa-61-aro3001773.yaml"),
    Target("ARO:3007730", "oxa-61-like-beta-lactamase-aro3007730.yaml"),
    Target("ARO:3005831", "oxa-610-aro3005831.yaml"),
    Target("ARO:3005832", "oxa-611-aro3005832.yaml"),
    Target("ARO:3005833", "oxa-612-aro3005833.yaml"),
    Target("ARO:3005834", "oxa-613-aro3005834.yaml"),
    Target("ARO:3005835", "oxa-614-aro3005835.yaml"),
    Target("ARO:3005836", "oxa-615-aro3005836.yaml"),
    Target("ARO:3005837", "oxa-616-aro3005837.yaml"),
    Target("ARO:3005838", "oxa-617-aro3005838.yaml"),
    Target("ARO:3005839", "oxa-618-aro3005839.yaml"),
    Target("ARO:3005840", "oxa-619-aro3005840.yaml"),
    Target("ARO:3005841", "oxa-620-aro3005841.yaml"),
    Target("ARO:3005842", "oxa-621-aro3005842.yaml"),
    Target("ARO:3005843", "oxa-622-aro3005843.yaml"),
    Target("ARO:3005844", "oxa-623-aro3005844.yaml"),
    Target("ARO:3005845", "oxa-624-aro3005845.yaml"),
    Target("ARO:3005846", "oxa-625-aro3005846.yaml"),
    Target("ARO:3005847", "oxa-626-aro3005847.yaml"),
    Target("ARO:3005848", "oxa-627-aro3005848.yaml"),
    Target("ARO:3005849", "oxa-628-aro3005849.yaml"),
    Target("ARO:3005850", "oxa-629-aro3005850.yaml"),
    Target("ARO:3001764", "oxa-63-aro3001764.yaml"),
    Target("ARO:3007732", "oxa-63-like-beta-lactamase-aro3007732.yaml"),
    Target("ARO:3005851", "oxa-630-aro3005851.yaml"),
    Target("ARO:3005852", "oxa-631-aro3005852.yaml"),
    Target("ARO:3005853", "oxa-632-aro3005853.yaml"),
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
