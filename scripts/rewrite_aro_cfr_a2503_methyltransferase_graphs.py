#!/usr/bin/env python3
"""Rewrite Cfr-type A2503 23S rRNA methyltransferase causal graphs.

The score-80 Cfr/clb/cip/clc graphs already use the correct radical-SAM
A2503-methylation topology, but still have sparse edge descriptions and
single-reference evidence.

Dry-run by default; pass ``--apply`` to write.
"""

from __future__ import annotations

import argparse
import copy
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from record_io import append_to_section, replace_block  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ARO_DIR = ROOT / "data" / "traits" / "function" / "resistance" / "aro"

HISTORY_CURATOR = "codex-causal-graph-quality"
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": "Completed Cfr-type A2503 23S rRNA methyltransferase causal graphs",
    "llm_assisted": True,
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str


TARGETS: tuple[Target, ...] = (
    Target("ARO:3000202", "cfr-23s-ribosomal-rna-methyltransferase-aro3000202.yaml"),
    Target("ARO:3004649", "cfr-b-aro3004649.yaml"),
    Target("ARO:3004609", "cfr-b-group-aro3004609.yaml"),
    Target("ARO:3004610", "cfr-c-group-aro3004610.yaml"),
    Target("ARO:3005021", "cfr-d-aro3005021.yaml"),
    Target("ARO:3005020", "cfr-d-group-aro3005020.yaml"),
    Target("ARO:3005022", "cfr-e-group-aro3005022.yaml"),
    Target("ARO:3004607", "cfr-group-aro3004607.yaml"),
    Target("ARO:3003441", "cfra-aro3003441.yaml"),
    Target("ARO:3004146", "cfrc-aro3004146.yaml"),
    Target("ARO:3005023", "cfre-aro3005023.yaml"),
    Target("ARO:3003907", "cipa-aro3003907.yaml"),
    Target("ARO:3002814", "clba-aro3002814.yaml"),
    Target("ARO:3002815", "clbb-aro3002815.yaml"),
    Target("ARO:3002816", "clbc-aro3002816.yaml"),
    Target("ARO:3004599", "clcd-aro3004599.yaml"),
)
TARGET_BY_ID = {target.identifier: target for target in TARGETS}

CFR_PARENT_EVIDENCE = {
    "reference": "ARO:3000202",
    "snippet": (
        "Cfr genes produce enzymes which catalyze the methylation of the 23S rRNA "
        "subunit at position 8 of adenine-2503. Methylation of 23S rRNA at this "
        "site confers resistance to some classes of antibiotics, including "
        "streptogramins, chloramphenicols, florfenicols, linezolids and "
        "clindamycin."
    ),
    "notes": "CARD definition for Cfr-type 23S ribosomal RNA methyltransferases.",
}

TARGET_ALTERATION_EVIDENCE = {
    "reference": "ARO:0001001",
    "snippet": (
        "Mutational alteration or enzymatic modification of antibiotic target which "
        "results in antibiotic resistance."
    ),
    "notes": "CARD definition for antibiotic target alteration.",
}

RIBOSOMAL_ALTERATION_EVIDENCE = {
    "reference": "ARO:3000211",
    "snippet": (
        "Chemical alteration of the ribosome results in modification of an "
        "antibiotic's target leading to resistance."
    ),
    "notes": "CARD definition for ribosomal alteration conferring antibiotic resistance.",
}

RRNA_METHYLTRANSFERASE_EVIDENCE = {
    "reference": "ARO:3000164",
    "snippet": "Catalyzes methylation of rRNA.",
    "notes": "CARD definition for rRNA methyltransferase activity.",
}

PFAM_EVIDENCE = {
    "reference": "Pfam:PF04055",
    "snippet": "Radical SAM superfamily",
    "notes": "Pfam radical-SAM methyltransferase domain.",
}

CATH_EVIDENCE = {
    "reference": "CATH:3.20.20",
    "snippet": "TIM Barrel",
    "notes": "CATH radical-SAM partial TIM-barrel fold.",
}

A2503_EVIDENCE = {
    "reference": "PMID:20007606",
    "snippet": (
        "The Cfr methyltransferase confers combined resistance to five classes of "
        "antibiotics that bind to the peptidyl tranferase center of bacterial "
        "ribosomes by catalyzing methylation of the C-8 position of 23S rRNA "
        "nucleotide A2503."
    ),
    "notes": (
        "Evidence that Cfr methylates 23S rRNA A2503 in the peptidyl-transferase "
        "center and thereby confers broad resistance."
    ),
}

EDGE_DESCRIPTIONS = {
    ("determinant", "mech0"): (
        "CARD classifies this Cfr-type enzyme under antibiotic target alteration."
    ),
    ("mech0", "resistance"): (
        "23S rRNA A2503 methylation changes the ribosomal antibiotic target and thereby "
        "causes resistance."
    ),
    ("determinant", "mech1"): (
        "CARD classifies this Cfr-type enzyme under ribosomal alteration conferring "
        "antibiotic resistance."
    ),
    ("mech1", "resistance"): (
        "Methylation of the 23S rRNA peptidyl-transferase center blocks multiple "
        "ribosome-binding antibiotics."
    ),
    ("determinant", "resistance"): (
        "The determinant methylates 23S rRNA A2503 in the ribosomal drug-binding site."
    ),
    ("determinant", "drug0"): (
        "CARD asserts that Cfr-type 23S rRNA methyltransferases confer resistance to "
        "lincosamide antibiotics."
    ),
    ("determinant", "drug1"): (
        "CARD asserts that Cfr-type 23S rRNA methyltransferases confer resistance to "
        "streptogramin antibiotics."
    ),
    ("determinant", "drug2"): (
        "CARD asserts that Cfr-type 23S rRNA methyltransferases confer resistance to "
        "oxazolidinone antibiotics."
    ),
    ("determinant", "drug3"): (
        "CARD asserts that Cfr-type 23S rRNA methyltransferases confer resistance to "
        "phenicol antibiotics."
    ),
    ("domain", "determinant"): (
        "The grounded radical-SAM methyltransferase domain is part of the Cfr-type "
        "determinant."
    ),
    ("determinant", "fold"): (
        "The determinant adopts the radical-SAM partial TIM-barrel fold associated with "
        "this methyltransferase family."
    ),
    ("domain", "mech1"): (
        "The radical-SAM methyltransferase domain enables methylation of 23S rRNA A2503."
    ),
}

BASE_EDGE_EVIDENCE = {
    ("determinant", "mech0"): [
        CFR_PARENT_EVIDENCE,
        TARGET_ALTERATION_EVIDENCE,
        RIBOSOMAL_ALTERATION_EVIDENCE,
        RRNA_METHYLTRANSFERASE_EVIDENCE,
        A2503_EVIDENCE,
    ],
    ("mech0", "resistance"): [
        CFR_PARENT_EVIDENCE,
        TARGET_ALTERATION_EVIDENCE,
        RIBOSOMAL_ALTERATION_EVIDENCE,
        A2503_EVIDENCE,
    ],
    ("determinant", "mech1"): [
        CFR_PARENT_EVIDENCE,
        RIBOSOMAL_ALTERATION_EVIDENCE,
        RRNA_METHYLTRANSFERASE_EVIDENCE,
        A2503_EVIDENCE,
    ],
    ("mech1", "resistance"): [
        CFR_PARENT_EVIDENCE,
        TARGET_ALTERATION_EVIDENCE,
        RIBOSOMAL_ALTERATION_EVIDENCE,
        RRNA_METHYLTRANSFERASE_EVIDENCE,
        A2503_EVIDENCE,
    ],
    ("determinant", "resistance"): [
        CFR_PARENT_EVIDENCE,
        TARGET_ALTERATION_EVIDENCE,
        RIBOSOMAL_ALTERATION_EVIDENCE,
        RRNA_METHYLTRANSFERASE_EVIDENCE,
        A2503_EVIDENCE,
    ],
    ("determinant", "drug0"): [CFR_PARENT_EVIDENCE, A2503_EVIDENCE],
    ("determinant", "drug1"): [CFR_PARENT_EVIDENCE, A2503_EVIDENCE],
    ("determinant", "drug2"): [CFR_PARENT_EVIDENCE, A2503_EVIDENCE],
    ("determinant", "drug3"): [CFR_PARENT_EVIDENCE, A2503_EVIDENCE],
    ("domain", "determinant"): [
        CFR_PARENT_EVIDENCE,
        PFAM_EVIDENCE,
        RRNA_METHYLTRANSFERASE_EVIDENCE,
        A2503_EVIDENCE,
    ],
    ("determinant", "fold"): [
        CFR_PARENT_EVIDENCE,
        CATH_EVIDENCE,
        RRNA_METHYLTRANSFERASE_EVIDENCE,
        A2503_EVIDENCE,
    ],
    ("domain", "mech1"): [
        CFR_PARENT_EVIDENCE,
        RIBOSOMAL_ALTERATION_EVIDENCE,
        RRNA_METHYLTRANSFERASE_EVIDENCE,
        PFAM_EVIDENCE,
        A2503_EVIDENCE,
    ],
}


def _dump(obj: Any) -> str:
    return yaml.safe_dump(
        obj,
        sort_keys=False,
        allow_unicode=True,
        width=100,
        default_flow_style=False,
    )


def record_evidence(record: dict[str, Any]) -> dict[str, str]:
    return {
        "reference": str(record["identifier"]),
        "snippet": " ".join(str(record.get("definition", "")).split()),
        "notes": f"CARD definition for {record['label']}.",
    }


def fresh_evidence(items: list[dict[str, str]]) -> list[dict[str, str]]:
    return [copy.deepcopy(item) for item in items]


def enrich_graph(graph: dict[str, Any], record: dict[str, Any]) -> dict[str, Any]:
    graph = copy.deepcopy(graph)
    graph["title"] = f"{record['label']} → Cfr-type 23S rRNA A2503 methylation"
    graph["description"] = (
        "Curated resistance-causation graph for Cfr-type radical-SAM 23S rRNA "
        "methyltransferases. The determinant participates in antibiotic target alteration "
        "and ribosomal alteration by methylating A2503 in 23S rRNA through a grounded "
        "radical-SAM domain and fold."
    )

    for node in graph["nodes"]:
        if node["node_id"] == "domain":
            node["description"] = "Radical-SAM methyltransferase catalytic domain."
        elif node["node_id"] == "fold":
            node["description"] = "Radical-SAM partial TIM-barrel fold."

    target_evidence = record_evidence(record)
    for edge in graph["edges"]:
        key = (edge["subject"], edge["object"])
        edge["description"] = EDGE_DESCRIPTIONS[key]
        evidence = []
        if key[0] == "determinant":
            evidence.append(target_evidence)
        evidence.extend(edge.get("evidence", []))
        evidence.extend(BASE_EDGE_EVIDENCE[key])
        edge["evidence"] = fresh_evidence(evidence)

    return graph


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not a Cfr-type methyltransferase target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    graphs = record.get("causal_graphs")
    if not isinstance(graphs, list) or len(graphs) != 1:
        raise ValueError(f"{path}: expected exactly one causal graph")

    enriched_graph = enrich_graph(graphs[0], record)
    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": [enriched_graph]}))
    changed = out != text
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
        help="ARO directory or one of the Cfr-type methyltransferase YAML files",
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
        except (KeyError, OSError, ValueError, yaml.YAMLError) as exc:
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
