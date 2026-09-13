#!/usr/bin/env python3
"""Rewrite remaining score-77 23S rRNA macrolide-resistance ARO graphs.

The first species-specific updater curated most ARO:3004125 descendants but did
not include Propionibacteria, Streptococcus pneumoniae, Streptomyces
ambofaciens, or Treponema pallidum.  These leaves use the same inherited 23S
rRNA point-mutation graph: mutated 23S rRNA reduces macrolide binding at a 23S
site, causing macrolide resistance.

Dry-run by default; pass ``--apply`` to write.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

import rewrite_aro_23s_macrolide_species_rrna_graphs as species  # noqa: E402

ARO_DIR = species.ARO_DIR

HISTORY_ACTION = "Completed remaining species-specific 23S rRNA macrolide-resistance graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-09T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str


TARGETS: tuple[Target, ...] = (
    Target(
        "ARO:3004161",
        "propionibacteria-23s-rrna-with-mutation-conferring-resistance-to-macrolide-antib-"
        "aro3004161.yaml",
    ),
    Target(
        "ARO:3004170",
        "streptococcus-pneumoniae-23s-rrna-with-mutation-conferring-resistance-to-macroli-"
        "aro3004170.yaml",
    ),
    Target(
        "ARO:3004171",
        "streptomyces-ambofaciens-23s-rrna-with-mutation-conferring-resistance-to-macroli-"
        "aro3004171.yaml",
    ),
    Target(
        "ARO:3007759",
        "treponema-pallidum-23s-rrna-with-mutation-conferring-resistance-to-erythromycin-"
        "aro3007759.yaml",
    ),
)
TARGET_BY_ID = {target.identifier: target for target in TARGETS}


def _ground_altered_site_state(record: dict) -> None:
    graph = record["causal_graphs"][0]
    for node in graph["nodes"]:
        if node["node_id"] != "altered_site":
            continue
        node["grounding"] = "SO:0000252"
        node["description"] = (
            "Local state for a mutated 23S rRNA peptidyl-transferase-loop site "
            "with reduced macrolide binding affinity. Grounded to the broad "
            "rRNA Sequence Ontology term because no stable narrow term is "
            "available for this altered local state."
        )
        return
    raise ValueError(f"{record['identifier']}: generated graph missing altered_site node")


def enrich_record(record: dict, target: Target) -> tuple[dict, bool]:
    species_target = species.Target(target.identifier, target.filename)
    enriched, _ = species.enrich_record(record, species_target)
    _ground_altered_site_state(enriched)
    return enriched, enriched != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not a late 23S macrolide rRNA target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
    out = species.replace_block(
        text,
        "causal_graphs",
        species._dump({"causal_graphs": enriched["causal_graphs"]}),
    )
    if HISTORY_ACTION not in out:
        out = species.append_to_section(
            out,
            "curation_history",
            species._dump({"curation_history": [HISTORY_EVENT]}),
        )
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
        help="ARO directory or one of the four remaining 23S macrolide rRNA YAML files",
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
