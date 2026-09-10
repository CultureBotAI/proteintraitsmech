#!/usr/bin/env python3
"""Rewrite bacterial 16S rRNA leaf mutation causal graphs.

These score-78 records are bacterial, species-specific 16S rRNA mutations
that retain old sparse graphs.  They share the same target-alteration shape as
the curated 16S rRNA drug-class parent graph: mutated 16S rRNA alters a local
antibiotic-binding site in the small ribosomal subunit.

Dry-run by default; pass ``--apply`` to write.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from record_io import append_to_section, replace_block  # noqa: E402
from rewrite_aro_rrna_drug_class_parent_graphs import (  # noqa: E402
    SIXTEEN_S,
    Target,
    enrich_record,
)

ROOT = Path(__file__).resolve().parent.parent
ARO_DIR = ROOT / "data" / "traits" / "function" / "resistance" / "aro"

HISTORY_CURATOR = "codex-causal-graph-quality"
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": "Completed bacterial 16S rRNA leaf mutation causal graphs",
    "llm_assisted": True,
}

TARGET_FILENAMES: tuple[str, ...] = (
    "chlamydophila-psittaci-16s-rrna-mutation-conferring-resistance-to-spectinomycin-aro3003485.yaml",
    "cutibacterium-acnes-16s-rrna-mutation-conferring-resistance-to-tetracycline-aro3003499.yaml",
    "escherichia-coli-16s-rrna-mutation-conferring-resistance-to-edeine-aro3003223.yaml",
    "escherichia-coli-16s-rrna-rrnb-mutation-conferring-resistance-to-spectinomycin-aro3003377.yaml",
    "escherichia-coli-16s-rrna-rrnb-mutation-conferring-resistance-to-streptomycin-aro3003406.yaml",
    "escherichia-coli-16s-rrna-rrnb-mutation-conferring-resistance-to-tetracycline-aro3003411.yaml",
    "escherichia-coli-16s-rrna-rrsb-mutation-conferring-resistance-to-g418-aro3003397.yaml",
    "escherichia-coli-16s-rrna-rrsb-mutation-conferring-resistance-to-gentamicin-c-aro3003396.yaml",
    "escherichia-coli-16s-rrna-rrsb-mutation-conferring-resistance-to-kanamycin-a-aro3003399.yaml",
    "escherichia-coli-16s-rrna-rrsb-mutation-conferring-resistance-to-neomycin-aro3003402.yaml",
    "escherichia-coli-16s-rrna-rrsb-mutation-conferring-resistance-to-paromomycin-aro3003403.yaml",
    "escherichia-coli-16s-rrna-rrsb-mutation-conferring-resistance-to-spectinomycin-aro3003376.yaml",
    "escherichia-coli-16s-rrna-rrsb-mutation-conferring-resistance-to-streptomycin-aro3003405.yaml",
    "escherichia-coli-16s-rrna-rrsb-mutation-conferring-resistance-to-tetracycline-aro3003410.yaml",
    "escherichia-coli-16s-rrna-rrsb-mutation-conferring-resistance-to-tobramycin-aro3003408.yaml",
    "escherichia-coli-16s-rrna-rrsc-mutation-conferring-resistance-to-kasugamicin-aro3003333.yaml",
    "escherichia-coli-16s-rrna-rrsh-mutation-conferring-resistance-to-spectinomycin-aro3003372.yaml",
    "helicobacter-pylori-16s-rrna-mutation-conferring-resistance-to-tetracycline-aro3003510.yaml",
    "mycobacterium-tuberculosis-16s-rrna-mutation-conferring-resistance-to-amikacin-aro3003481.yaml",
    "mycobacterium-tuberculosis-16s-rrna-mutation-conferring-resistance-to-capreomyci-aro3004853.yaml",
    "mycobacterium-tuberculosis-16s-rrna-mutation-conferring-resistance-to-kanamycin-aro3003436.yaml",
    "mycobacterium-tuberculosis-16s-rrna-mutation-conferring-resistance-to-streptomyc-aro3003480.yaml",
    "mycobacterium-tuberculosis-16s-rrna-mutation-conferring-resistance-to-viomycin-aro3003437.yaml",
    "mycobacterium-tuberculosis-16s-rrna-rrns-mutation-conferring-resistance-to-amika-aro3007536.yaml",
    "mycobacterium-tuberculosis-16s-rrna-rrns-mutation-conferring-resistance-to-kanam-aro3007537.yaml",
    "mycobacteroides-abscessus-16s-rrna-mutation-conferring-resistance-to-amikacin-aro3003239.yaml",
    "mycobacteroides-abscessus-16s-rrna-mutation-conferring-resistance-to-gentamicin-aro3003240.yaml",
    "mycobacteroides-abscessus-16s-rrna-mutation-conferring-resistance-to-kanamycin-aro3003236.yaml",
    "mycobacteroides-abscessus-16s-rrna-mutation-conferring-resistance-to-neomycin-aro3003238.yaml",
    "mycobacteroides-abscessus-16s-rrna-mutation-conferring-resistance-to-tobramycin-aro3003237.yaml",
    "mycobacteroides-chelonae-16s-rrna-mutation-conferring-resistance-to-amikacin-aro3003514.yaml",
    "mycobacteroides-chelonae-16s-rrna-mutation-conferring-resistance-to-gentamicin-c-aro3003517.yaml",
    "mycobacteroides-chelonae-16s-rrna-mutation-conferring-resistance-to-kanamycin-a-aro3003515.yaml",
    "mycobacteroides-chelonae-16s-rrna-mutation-conferring-resistance-to-neomycin-aro3003518.yaml",
    "mycobacteroides-chelonae-16s-rrna-mutation-conferring-resistance-to-tobramycin-aro3003516.yaml",
    "mycolicibacterium-smegmatis-16s-rrna-rrsa-mutation-conferring-resistance-to-hygr-aro3003539.yaml",
    "mycolicibacterium-smegmatis-16s-rrna-rrsa-mutation-conferring-resistance-to-kana-aro3003543.yaml",
    "mycolicibacterium-smegmatis-16s-rrna-rrsa-mutation-conferring-resistance-to-neom-aro3003544.yaml",
    "mycolicibacterium-smegmatis-16s-rrna-rrsa-mutation-conferring-resistance-to-viom-aro3003546.yaml",
    "mycolicibacterium-smegmatis-16s-rrna-rrsb-mutation-conferring-resistance-to-hygr-aro3003540.yaml",
    "mycolicibacterium-smegmatis-16s-rrna-rrsb-mutation-conferring-resistance-to-kana-aro3003542.yaml",
    "mycolicibacterium-smegmatis-16s-rrna-rrsb-mutation-conferring-resistance-to-neom-aro3003545.yaml",
    "mycolicibacterium-smegmatis-16s-rrna-rrsb-mutation-conferring-resistance-to-stre-aro3003541.yaml",
    "mycolicibacterium-smegmatis-16s-rrna-rrsb-mutation-conferring-resistance-to-viom-aro3003547.yaml",
    "neisseria-gonorrhoeae-16s-rrna-mutation-conferring-resistance-to-spectinomycin-aro3003495.yaml",
    "neisseria-meningitidis-16s-rrna-mutation-conferring-resistance-to-spectinomycin-aro3003497.yaml",
    "pasteurella-multocida-16s-rrna-mutation-conferring-resistance-to-spectinomycin-aro3003493.yaml",
    "salmonella-enterica-16s-rrna-rrsd-mutation-conferring-resistance-to-spectinomyci-aro3003512.yaml",
)


def identifier_from_filename(filename: str) -> str:
    aro_number = filename.rsplit("-aro", maxsplit=1)[1].removesuffix(".yaml")
    return f"ARO:{aro_number}"


TARGETS: tuple[Target, ...] = tuple(
    Target(identifier_from_filename(filename), filename, SIXTEEN_S)
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
        raise ValueError(f"{path}: not a bacterial 16S rRNA leaf target: {identifier}")
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
        help="ARO directory or one of the bacterial 16S rRNA leaf YAML files",
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
