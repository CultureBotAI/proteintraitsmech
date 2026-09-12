#!/usr/bin/env python3
"""Complete non-vanA VanR/VanS variant regulation graphs.

These promoted records already distinguish the D-Ala-D-Lac and D-Ala-D-Ser
cluster topologies. This script preserves that topology and fills in missing
edge descriptions plus multi-reference evidence for the non-vanA VanR/VanS
cluster-specific variants.

Dry-run by default; pass ``--apply`` to write.
"""

from __future__ import annotations

import argparse
import copy
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from record_io import append_to_section, replace_block  # noqa: E402
from rewrite_aro_vanr_parent_graph import (  # noqa: E402
    BYPASS_EVIDENCE,
    CELL_WALL_EVIDENCE,
    ENZYME_SYNTHESIS_EVIDENCE,
    FAMILY_EVIDENCE as VANR_FAMILY_EVIDENCE,
    GLYCOPEPTIDE_EVIDENCE as VANR_GLYCOPEPTIDE_EVIDENCE,
    NECESSARY_ENZYMES_EVIDENCE,
    PHOSPHORELAY_EVIDENCE,
    PROMOTER_EVIDENCE,
    VANH_EVIDENCE,
    VANR_EVIDENCE,
    VANX_EVIDENCE,
)
from rewrite_aro_vans_parent_graph import (  # noqa: E402
    FAMILY_EVIDENCE as VANS_FAMILY_EVIDENCE,
    GLYCOPEPTIDE_EVIDENCE as VANS_GLYCOPEPTIDE_EVIDENCE,
    SENSOR_KINASE_EVIDENCE,
    STIMULATION_EVIDENCE,
    VANS_EVIDENCE,
)

ROOT = Path(__file__).resolve().parent.parent
ARO_DIR = ROOT / "data" / "traits" / "function" / "resistance" / "aro"

HISTORY_ACTION = "Completed non-vanA VanR/VanS regulation graphs"
HISTORY_CURATOR = "codex-causal-graph-quality"
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}


class Regulator(Enum):
    VANR = "VanR"
    VANS = "VanS"


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    regulator: Regulator

    @property
    def parent_evidence(self) -> dict[str, str]:
        return VANR_EVIDENCE if self.regulator is Regulator.VANR else VANS_EVIDENCE

    @property
    def glycopeptide_evidence(self) -> dict[str, str]:
        if self.regulator is Regulator.VANR:
            return VANR_GLYCOPEPTIDE_EVIDENCE
        return VANS_GLYCOPEPTIDE_EVIDENCE

    @property
    def family_evidence(self) -> dict[str, str]:
        if self.regulator is Regulator.VANR:
            return VANR_FAMILY_EVIDENCE
        return VANS_FAMILY_EVIDENCE

    @property
    def activity_evidence(self) -> dict[str, str]:
        if self.regulator is Regulator.VANR:
            return PHOSPHORELAY_EVIDENCE
        return SENSOR_KINASE_EVIDENCE


TARGETS: tuple[Target, ...] = (
    Target("ARO:3002921", "vanr-gene-in-vanb-cluster-aro3002921.yaml", Regulator.VANR),
    Target("ARO:3002922", "vanr-gene-in-vanc-cluster-aro3002922.yaml", Regulator.VANR),
    Target("ARO:3002923", "vanr-gene-in-vand-cluster-aro3002923.yaml", Regulator.VANR),
    Target("ARO:3002924", "vanr-gene-in-vane-cluster-aro3002924.yaml", Regulator.VANR),
    Target("ARO:3002925", "vanr-gene-in-vanf-cluster-aro3002925.yaml", Regulator.VANR),
    Target("ARO:3002926", "vanr-gene-in-vang-cluster-aro3002926.yaml", Regulator.VANR),
    Target("ARO:3002927", "vanr-gene-in-vanl-cluster-aro3002927.yaml", Regulator.VANR),
    Target("ARO:3002928", "vanr-gene-in-vanm-cluster-aro3002928.yaml", Regulator.VANR),
    Target("ARO:3002929", "vanr-gene-in-vann-cluster-aro3002929.yaml", Regulator.VANR),
    Target("ARO:3002930", "vanr-gene-in-vano-cluster-aro3002930.yaml", Regulator.VANR),
    Target("ARO:3003728", "vanr-gene-in-vani-cluster-aro3003728.yaml", Regulator.VANR),
    Target("ARO:3007191", "vanr-gene-in-vanp-cluster-aro3007191.yaml", Regulator.VANR),
    Target("ARO:3002932", "vans-gene-in-vanb-cluster-aro3002932.yaml", Regulator.VANS),
    Target("ARO:3002933", "vans-gene-in-vanc-cluster-aro3002933.yaml", Regulator.VANS),
    Target("ARO:3002934", "vans-gene-in-vand-cluster-aro3002934.yaml", Regulator.VANS),
    Target("ARO:3002935", "vans-gene-in-vane-cluster-aro3002935.yaml", Regulator.VANS),
    Target("ARO:3002936", "vans-gene-in-vanf-cluster-aro3002936.yaml", Regulator.VANS),
    Target("ARO:3002937", "vans-gene-in-vang-cluster-aro3002937.yaml", Regulator.VANS),
    Target("ARO:3002938", "vans-gene-in-vanl-cluster-aro3002938.yaml", Regulator.VANS),
    Target("ARO:3002939", "vans-gene-in-vanm-cluster-aro3002939.yaml", Regulator.VANS),
    Target("ARO:3002940", "vans-gene-in-vann-cluster-aro3002940.yaml", Regulator.VANS),
    Target("ARO:3002941", "vans-gene-in-vano-cluster-aro3002941.yaml", Regulator.VANS),
    Target("ARO:3003726", "vans-gene-in-vani-cluster-aro3003726.yaml", Regulator.VANS),
    Target("ARO:3007192", "vans-gene-in-vanp-cluster-aro3007192.yaml", Regulator.VANS),
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


def _dicts(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _unique_evidence(*items: dict[str, str]) -> list[dict[str, str]]:
    evidence: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for item in items:
        marker = (item["reference"], item["snippet"])
        if marker in seen:
            continue
        seen.add(marker)
        evidence.append(copy.deepcopy(item))
    return evidence


def _description_for_edge(edge: dict[str, Any], target: Target) -> str:
    subject = edge.get("subject")
    object_ = edge.get("object")

    if subject == "determinant" and object_ == "mech0":
        return f"CARD places this {target.regulator.value} variant in the cell-wall bypass pathway."
    if subject == "mech0" and object_ == "resistance":
        return "Remodeled peptidoglycan precursors lower glycopeptide binding and cause resistance."
    if subject == "determinant" and object_ == "resistance":
        return (
            f"{target.regulator.value} confers resistance indirectly by regulating "
            "transcription of van resistance genes."
        )
    if subject == "determinant" and object_ == "drug0":
        return "CARD asserts inherited glycopeptide-antibiotic resistance for this cluster variant."
    if subject == "transcription":
        return "VanR/VanS-dependent transcription induces this van resistance gene."
    if str(subject).endswith("_gene") and object_ == "resistance":
        return "The induced resistance gene remodels peptidoglycan precursors."
    if subject == "determinant" and object_ == "family":
        return f"The determinant is a {target.regulator.value} two-component-system variant."
    if subject == "family" and object_ == "activity":
        return f"The {target.regulator.value} family enables its phosphorelay activity."
    if subject == "activity" and object_ == "transcription":
        return "VanR phosphorelay activity is upstream of van operon transcription."
    if subject == "activity" and object_ == "vanr_protein":
        return "VanS kinase activity controls the partner VanR response regulator."
    if subject == "vanr_protein" and object_ == "transcription":
        return "VanR activates transcription of the van resistance operon."

    key = (subject, edge.get("predicate"), object_)
    raise ValueError(f"{target.identifier}: unexpected edge {key}")


def _evidence_for_edge(
    edge: dict[str, Any],
    existing: list[dict[str, str]],
    target: Target,
    record_evidence: dict[str, str],
) -> list[dict[str, str]]:
    subject = edge.get("subject")
    object_ = edge.get("object")
    extra: list[dict[str, str]] = [record_evidence, target.parent_evidence]

    if subject == "determinant" and object_ == "mech0":
        extra.extend([BYPASS_EVIDENCE, ENZYME_SYNTHESIS_EVIDENCE])
    elif subject == "mech0" and object_ == "resistance":
        extra.extend([BYPASS_EVIDENCE, CELL_WALL_EVIDENCE])
    elif subject == "determinant" and object_ == "resistance":
        extra.extend([PROMOTER_EVIDENCE, ENZYME_SYNTHESIS_EVIDENCE, NECESSARY_ENZYMES_EVIDENCE])
        if target.regulator is Regulator.VANS:
            extra.append(STIMULATION_EVIDENCE)
    elif subject == "determinant" and object_ == "drug0":
        extra.extend([target.glycopeptide_evidence, CELL_WALL_EVIDENCE])
    elif subject == "transcription":
        extra.extend([PROMOTER_EVIDENCE, ENZYME_SYNTHESIS_EVIDENCE])
    elif str(subject).endswith("_gene") and object_ == "resistance":
        extra.extend([NECESSARY_ENZYMES_EVIDENCE, VANH_EVIDENCE, VANX_EVIDENCE, CELL_WALL_EVIDENCE])
    elif subject == "determinant" and object_ == "family":
        extra.append(target.family_evidence)
    elif subject == "family" and object_ == "activity":
        extra.extend([target.family_evidence, target.activity_evidence])
    elif subject == "activity" and object_ == "transcription":
        extra.extend([PHOSPHORELAY_EVIDENCE, PROMOTER_EVIDENCE])
    elif subject == "activity" and object_ == "vanr_protein":
        extra.extend([SENSOR_KINASE_EVIDENCE, STIMULATION_EVIDENCE, VANR_EVIDENCE])
    elif subject == "vanr_protein" and object_ == "transcription":
        extra.extend([VANR_EVIDENCE, PROMOTER_EVIDENCE])
    else:
        _description_for_edge(edge, target)

    return _unique_evidence(*existing, *extra)


def _validate_record(record: dict[str, Any], target: Target) -> None:
    if record.get("identifier") != target.identifier:
        raise ValueError(
            f"{target.filename}: expected {target.identifier}, "
            f"found {record.get('identifier')}"
        )
    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1 or graphs[0].get("graph_id") != "resistance":
        raise ValueError(f"{target.identifier}: expected exactly one resistance graph")
    if len(_dicts(graphs[0].get("edges"))) < 9:
        raise ValueError(f"{target.identifier}: graph has too few VanR/VanS edges")


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    _validate_record(record, target)

    out = copy.deepcopy(record)
    graph = out["causal_graphs"][0]
    record_evidence = {
        "reference": target.identifier,
        "snippet": str(record["definition"]),
        "notes": f"CARD definition for {record['label']}.",
    }
    for edge in _dicts(graph.get("edges")):
        edge["description"] = _description_for_edge(edge, target)
        edge["evidence"] = _evidence_for_edge(
            edge,
            _dicts(edge.get("evidence")),
            target,
            record_evidence,
        )
    return out, out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not a non-vanA VanR/VanS target: {identifier}")
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
        help="ARO directory or one of the non-vanA VanR/VanS YAML files",
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
