#!/usr/bin/env python3
"""Curate nfsA nitrofuran nitroreductase resistance graphs.

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

HISTORY_ACTION = "Curated nfsA nitrofuran nitroreductase graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

MUTATION_EVIDENCE = {
    "reference": "ARO:3000212",
    "snippet": (
        "Point mutations in the DNA may lead to an altered gene product that "
        "may result in antibiotic resistance."
    ),
    "notes": "CARD definition for mutation conferring antibiotic resistance.",
}

NFSA_PARENT_EVIDENCE = {
    "reference": "ARO:3003754",
    "snippet": (
        "The nfsA-encoded nitroreductase is the major oxygen-insensitive "
        "nitroreductase present in E. coli. NfsA uses only NADPH and has "
        "broad electron acceptor specificity. Mutations in nfsA cause "
        "resistance to nitrofurazone and furazolidone."
    ),
    "notes": "CARD definition for antibiotic resistant nfsA.",
}

NFSA_CHILD_EVIDENCE = {
    "reference": "ARO:3003751",
    "snippet": (
        "nfsA encodes the major oxygen-insesitive nitroreductase in E. coli. "
        "The first step of resistance to nitrofurazone is mutation of nfsA."
    ),
    "notes": "CARD definition for E. coli nfsA nitrofuran resistance.",
}

NADPH_OXIDOREDUCTASE_EVIDENCE = {
    "reference": "GO:0016651",
    "snippet": (
        "Catalysis of an oxidation-reduction (redox) reaction in which NADH "
        "or NADPH acts as a hydrogen or electron donor and reduces a hydrogen "
        "or electron acceptor."
    ),
    "notes": (
        "GO oxidoreductase activity acting on NAD(P)H covers the reducing "
        "equivalents used by NfsA without guessing the nitrofuran-specific "
        "acceptor."
    ),
}

NITROFURAN_NODE = {
    "node_id": "drug0",
    "label": "nitrofuran antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:3004116",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "mutation conferring antibiotic resistance",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3000212",
}

NITROREDUCTION_NODE = {
    "node_id": "nitroreduction",
    "label": "oxygen-insensitive nitrofuran nitroreductase activity",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "GO:0016651",
    "description": (
        "Local NfsA nitrofuran-reduction activity, grounded to "
        "oxidoreductase activity acting on NAD(P)H as the nearest stable GO "
        "molecular-function parent."
    ),
}

RESISTANCE_NODE = {
    "node_id": "resistance",
    "label": "antibiotic resistance phenotype",
    "node_type": "PHENOTYPE",
    "grounding": "GO:0046677",
    "description": "Nitrofuran resistance phenotype conferred by loss of NfsA activity.",
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str


TARGETS: tuple[Target, ...] = (
    Target("ARO:3003754", "antibiotic-resistant-nfsa-aro3003754.yaml"),
    Target(
        "ARO:3003751",
        "escherichia-coli-nfsa-mutations-conferring-resistance-to-nitrofurantoin-aro3003751.yaml",
    ),
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


def _unique_evidence(*items: dict[str, Any]) -> list[dict[str, Any]]:
    unique: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for item in items:
        key = (
            str(item["reference"]),
            str(item.get("snippet", "")),
            str(item.get("notes", "")),
        )
        if key in seen:
            continue
        seen.add(key)
        unique.append(copy.deepcopy(item))
    return unique


def _source_evidence(record: dict[str, Any]) -> tuple[dict[str, str], ...]:
    return tuple(
        {
            "reference": str(item["reference"]),
            "notes": str(item.get("notes") or "ARO citation for this record."),
        }
        for item in _dicts(record.get("evidence"))
        if item.get("reference")
    )


def _record_evidence(record: dict[str, Any]) -> dict[str, str]:
    return {
        "reference": str(record["identifier"]),
        "snippet": str(record["definition"]),
        "notes": f"CARD definition for {record['label']}.",
    }


def _drug_relation_evidence(record: dict[str, Any]) -> list[dict[str, Any]]:
    for graph in _dicts(record.get("causal_graphs")):
        for edge in _dicts(graph.get("edges")):
            if (
                edge.get("subject") == "determinant"
                and edge.get("predicate_id") == "ARO:2000001"
                and edge.get("object") == "drug0"
            ):
                evidence = [
                    copy.deepcopy(item)
                    for item in _dicts(edge.get("evidence"))
                    if str(item.get("snippet", "")).startswith(
                        "relationship: confers_resistance_to_drug_class "
                    )
                ]
                if evidence:
                    return evidence
    raise ValueError(f"{record['identifier']}: missing ARO drug-relation evidence")


def _edge(
    subject: str,
    predicate: str,
    predicate_id: str,
    object_: str,
    description: str,
    *evidence: dict[str, Any],
) -> dict[str, Any]:
    return {
        "subject": subject,
        "predicate": predicate,
        "predicate_id": predicate_id,
        "object": object_,
        "description": description,
        "evidence": _unique_evidence(*evidence),
    }


def _graph(record: dict[str, Any]) -> dict[str, Any]:
    record_evidence = _record_evidence(record)
    source_evidence = _source_evidence(record)
    mutation_evidence = (
        record_evidence,
        NFSA_PARENT_EVIDENCE,
        NFSA_CHILD_EVIDENCE,
        MUTATION_EVIDENCE,
        *source_evidence,
    )
    nitroreduction_evidence = (
        record_evidence,
        NFSA_PARENT_EVIDENCE,
        NFSA_CHILD_EVIDENCE,
        NADPH_OXIDOREDUCTASE_EVIDENCE,
        *source_evidence,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → reduced nitrofuran activation",
        "description": (
            "Curated resistance-causation graph for nfsA mutations that reduce "
            "oxygen-insensitive nitrofuran nitroreduction."
        ),
        "nodes": [
            {
                "node_id": "determinant",
                "label": str(record["label"]),
                "node_type": "PROTEIN",
                "grounding": str(record["identifier"]),
            },
            copy.deepcopy(MECHANISM_NODE),
            copy.deepcopy(NITROREDUCTION_NODE),
            copy.deepcopy(NITROFURAN_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "ARO classifies nfsA records under mutation conferring "
                "antibiotic resistance.",
                *mutation_evidence,
            ),
            _edge(
                "determinant",
                "enables",
                "RO:0002327",
                "nitroreduction",
                "NfsA normally enables oxygen-insensitive reduction of "
                "nitrofuran antibiotics.",
                *nitroreduction_evidence,
            ),
            _edge(
                "determinant",
                "negatively regulates",
                "RO:0002212",
                "nitroreduction",
                "Resistance-conferring nfsA mutations reduce NfsA-dependent "
                "nitrofuran nitroreduction.",
                *nitroreduction_evidence,
                MUTATION_EVIDENCE,
            ),
            _edge(
                "nitroreduction",
                "has input",
                "RO:0002233",
                "drug0",
                "NfsA nitroreduction consumes nitrofuran antibiotics as "
                "substrates.",
                *nitroreduction_evidence,
            ),
            _edge(
                "nitroreduction",
                "negatively regulates (wild-type activation counteracts resistance)",
                "RO:0002212",
                "resistance",
                "Reduced NfsA-mediated activation of nitrofurans causes the "
                "modeled resistance phenotype.",
                *nitroreduction_evidence,
                MUTATION_EVIDENCE,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "nfsA loss-of-function mutations are a mutation-mediated "
                "nitrofuran-resistance mechanism.",
                *mutation_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "nfsA mutations confer nitrofuran resistance by reducing "
                "nitroreductase activity.",
                *mutation_evidence,
                NADPH_OXIDOREDUCTASE_EVIDENCE,
            ),
            _edge(
                "determinant",
                "confers resistance to (drug class)",
                "ARO:2000001",
                "drug0",
                "CARD asserts nitrofuran-antibiotic resistance for the nfsA "
                "lineage.",
                record_evidence,
                NFSA_PARENT_EVIDENCE,
                *_drug_relation_evidence(record),
                *source_evidence,
            ),
        ],
    }


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != target.identifier:
        raise ValueError(
            f"{target.filename}: expected {target.identifier}, "
            f"found {record.get('identifier')}"
        )
    if len(_dicts(record.get("causal_graphs"))) != 1:
        raise ValueError(f"{target.identifier}: expected exactly one causal graph")

    out = copy.deepcopy(record)
    before = copy.deepcopy(out["causal_graphs"])
    out["causal_graphs"] = [_graph(out)]
    return out, out["causal_graphs"] != before


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: record is not a mapping")
    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not an nfsA target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    if HISTORY_ACTION not in out:
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
        help="ARO directory or one of the two target YAML files",
    )
    args = parser.parse_args(argv)

    changed = unchanged = 0
    problems: list[str] = []
    for path in iter_target_paths(args.path):
        if not path.exists():
            problems.append(f"{path}: missing")
            continue
        try:
            text = path.read_text(encoding="utf-8")
            out, did_change = enrich_text(text, path)
        except (OSError, ValueError, yaml.YAMLError) as exc:
            problems.append(str(exc))
            continue
        if not did_change:
            unchanged += 1
            continue
        changed += 1
        print(f"  {'wrote' if args.apply else 'would write'} {path.name}")
        if args.apply:
            path.write_text(out, encoding="utf-8")

    print(f"{'changed' if args.apply else 'would change'}: {changed}")
    print(f"already enriched: {unchanged}")
    for problem in problems:
        print(f"PROBLEM: {problem}", file=sys.stderr)
    if not args.apply:
        print("dry run -- pass --apply to write")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
