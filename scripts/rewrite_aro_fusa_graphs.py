#!/usr/bin/env python3
"""Curate FusA target-alteration fusidic-acid resistance graphs.

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

HISTORY_ACTION = "Curated FusA fusidic-acid target-alteration graphs"
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

FUSA_PARENT_EVIDENCE = {
    "reference": "ARO:3003734",
    "snippet": (
        "Antibiotic resistant fusA is caused by mutations to the elongation "
        "factor G (EF-G) and confers resistance to fusidic acid."
    ),
    "notes": "CARD definition for antibiotic resistant fusA.",
}

FUSIDANE_NODE = {
    "node_id": "drug0",
    "label": "fusidane antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:3007153",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "mutation conferring antibiotic resistance",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3000212",
}

TRANSLATION_NODE = {
    "node_id": "translation",
    "label": "translation",
    "node_type": "BIOLOGICAL_PROCESS",
    "grounding": "GO:0006412",
    "description": (
        "Grounded to the broad GO translation process that fusidic acid "
        "blocks by trapping EF-G on the ribosome."
    ),
}

RESISTANCE_NODE = {
    "node_id": "resistance",
    "label": "antibiotic resistance phenotype",
    "node_type": "PHENOTYPE",
    "grounding": "GO:0046677",
    "description": "Fusidic acid resistance mediated by mutant EF-G.",
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    literature_evidence: dict[str, str]


TARGETS: tuple[Target, ...] = (
    Target(
        identifier="ARO:3003734",
        filename="antibiotic-resistant-fusa-aro3003734.yaml",
        literature_evidence={
            "reference": "PMID:19289529",
            "snippet": (
                "Lannergård et al. connected S. aureus fusA/EF-G mutations to "
                "fusidic acid resistance."
            ),
            "notes": "Primary ARO citation for antibiotic resistant fusA.",
        },
    ),
    Target(
        identifier="ARO:3003735",
        filename=(
            "staphylococcus-aureus-fusa-with-mutation-conferring-resistance-to-"
            "fusidic-acid-aro3003735.yaml"
        ),
        literature_evidence={
            "reference": "PMID:12519196",
            "snippet": (
                "Besier et al. molecularly analyzed fusidic-acid resistance "
                "caused by S. aureus fusA mutations."
            ),
            "notes": "ARO citation for the S. aureus FusA mutant record.",
        },
    ),
)
TARGET_BY_ID = {target.identifier: target for target in TARGETS}

EDGE_DESCRIPTIONS = {
    ("determinant", "mech0"): (
        "CARD classifies these fusA resistance alleles under mutation "
        "conferring antibiotic resistance."
    ),
    ("determinant", "drug0"): (
        "CARD maps antibiotic-resistant fusA to the fusidane antibiotic drug "
        "class."
    ),
    ("drug0", "translation"): (
        "Fusidic acid inhibits translation by trapping EF-G on the ribosome."
    ),
    ("determinant", "translation"): (
        "Resistance-conferring fusA mutations alter EF-G and reduce the "
        "effective binding of fusidic acid, letting translation continue in "
        "the presence of the drug."
    ),
    ("translation", "resistance"): (
        "Maintaining translation in the presence of fusidic acid produces the "
        "resistance phenotype."
    ),
    ("mech0", "resistance"): (
        "Altered EF-G is the mutation-dependent mechanism that confers "
        "fusidic acid resistance."
    ),
    ("determinant", "resistance"): (
        "The fusA determinant links the EF-G alteration to the fusidic acid "
        "resistance phenotype."
    ),
}


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


def _record_evidence(record: dict[str, Any]) -> dict[str, str]:
    return {
        "reference": str(record["identifier"]),
        "snippet": str(record["definition"]),
        "notes": f"CARD definition for {record['label']}.",
    }


def _drug_relation_evidence(record: dict[str, Any]) -> dict[str, Any]:
    for graph in _dicts(record.get("causal_graphs")):
        for edge in _dicts(graph.get("edges")):
            if (
                edge.get("subject") == "determinant"
                and edge.get("predicate_id") == "ARO:2000001"
                and edge.get("object") == "drug0"
            ):
                evidence = _dicts(edge.get("evidence"))
                if evidence:
                    return copy.deepcopy(evidence[0])
    raise ValueError(f"{record['identifier']}: missing fusidane drug-class evidence")


def _edge(
    subject: str,
    predicate: str,
    predicate_id: str,
    object_: str,
    *evidence: dict[str, Any],
) -> dict[str, Any]:
    return {
        "subject": subject,
        "predicate": predicate,
        "predicate_id": predicate_id,
        "object": object_,
        "description": EDGE_DESCRIPTIONS[(subject, object_)],
        "evidence": _unique_evidence(*evidence),
    }


def _graph(
    record: dict[str, Any],
    target: Target,
    record_evidence: dict[str, str],
    drug_evidence: dict[str, Any],
) -> dict[str, Any]:
    mutation_evidence = _unique_evidence(
        record_evidence,
        FUSA_PARENT_EVIDENCE,
        MUTATION_EVIDENCE,
        target.literature_evidence,
    )
    target_alteration_evidence = _unique_evidence(
        record_evidence,
        FUSA_PARENT_EVIDENCE,
        target.literature_evidence,
    )
    drug_evidence = _unique_evidence(
        drug_evidence,
        FUSA_PARENT_EVIDENCE,
        record_evidence,
        target.literature_evidence,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → altered EF-G sustains translation in fusidic acid",
        "description": (
            "Curated FusA graph for fusidic acid resistance. Fusidic acid "
            "normally stalls EF-G on the ribosome; resistance-conferring "
            "fusA mutations alter EF-G and reduce drug binding to that target."
        ),
        "nodes": [
            {
                "node_id": "determinant",
                "label": record["label"],
                "node_type": "PROTEIN",
                "grounding": record["identifier"],
            },
            copy.deepcopy(MECHANISM_NODE),
            copy.deepcopy(FUSIDANE_NODE),
            copy.deepcopy(TRANSLATION_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                *mutation_evidence,
            ),
            _edge(
                "determinant",
                "confers resistance to (drug class)",
                "ARO:2000001",
                "drug0",
                *drug_evidence,
            ),
            _edge(
                "drug0",
                "negatively regulates",
                "RO:0002212",
                "translation",
                *drug_evidence,
            ),
            _edge(
                "determinant",
                "positively regulates",
                "RO:0002213",
                "translation",
                *target_alteration_evidence,
            ),
            _edge(
                "translation",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                *target_alteration_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                *mutation_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                *_unique_evidence(*mutation_evidence, *drug_evidence),
            ),
        ],
    }


def enrich_record(record: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    identifier = str(record.get("identifier", ""))
    try:
        target = TARGET_BY_ID[identifier]
    except KeyError as exc:
        raise ValueError(f"not a FusA target: {identifier}") from exc

    record_evidence = _record_evidence(record)
    drug_evidence = _drug_relation_evidence(record)

    out = copy.deepcopy(record)
    before = copy.deepcopy(out.get("causal_graphs"))
    out["mapping_status"] = "REVIEWED"
    out["causal_graphs"] = [_graph(record, target, record_evidence, drug_evidence)]
    return out, out["mapping_status"] != record.get("mapping_status") or out["causal_graphs"] != before


def enrich_text(text: str) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError("expected a YAML mapping")

    enriched, changed = enrich_record(record)
    out = replace_block(text, "mapping_status", f"mapping_status: {enriched['mapping_status']}\n")
    out = replace_block(
        out,
        "causal_graphs",
        _dump({"causal_graphs": enriched["causal_graphs"]}),
    )
    if HISTORY_ACTION not in out:
        out = append_to_section(
            out,
            "curation_history",
            _dump({"curation_history": [HISTORY_EVENT]}),
        )
        changed = True

    if "&id" in out or "*id" in out:
        raise ValueError("YAML anchors leaked into output")
    return out, changed


def _path_for(target: Target) -> Path:
    return ARO_DIR / target.filename


def iter_paths(paths: list[Path]) -> list[Path]:
    if not paths:
        return [_path_for(target) for target in TARGETS]

    out: list[Path] = []
    for path in paths:
        if path.is_dir():
            out.extend(_path_for(target) for target in TARGETS)
        else:
            out.append(path)
    return out


def run(paths: list[Path], apply: bool) -> int:
    changed = 0
    for path in iter_paths(paths):
        before = path.read_text(encoding="utf-8")
        after, path_changed = enrich_text(before)
        if path_changed:
            changed += 1
            print(f"  {'wrote' if apply else 'would write'} {path.name}")
            if apply:
                path.write_text(after, encoding="utf-8")
    return changed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="ARO directory or one of the FusA YAML files",
    )
    parser.add_argument("--apply", action="store_true", help="write changes")
    args = parser.parse_args(argv)

    changed = run(args.paths, args.apply)
    print(f"{'changed' if args.apply else 'would change'}: {changed}")
    print(f"already enriched: {len(iter_paths(args.paths)) - changed}")
    if not args.apply:
        print("dry run -- pass --apply to write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
