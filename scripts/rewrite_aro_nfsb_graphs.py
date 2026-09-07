#!/usr/bin/env python3
"""Ground and evidence nfsB nitrofuran resistance graphs.

The nfsB graphs intentionally retain CARD's nfsA-mutant-background
precondition. This updater grounds the NfsB nitroreduction step to the nearest
stable NAD(P)H oxidoreductase GO parent, grounds the genetic background to the
antibiotic-resistant nfsA ARO term, and adds an explicit loss-of-function state
for resistance-causing nfsB mutations.

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
HISTORY_ACTION = "Grounded nfsB nitrofuran resistance graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

PARENT_IDENTIFIER = "ARO:3003755"

PARENT_EVIDENCE = {
    "reference": PARENT_IDENTIFIER,
    "snippet": (
        "The nsfB gene encodes a minor oxygen-insensitive nitroreductase. NfsB "
        "reduces a broad range of nitroaromatic compounds including the "
        "antibiotics nitrofurazone and nitrofurantoin. NfsB is a flavin "
        "mononucleotide (FMN)-containing protein and uses both NADH and NADPH "
        "as a source of reducing equivalents. Mutations in nfsB lead to "
        "increased resistance to nitrofurazone and furazolidone in an nfsA "
        "mutant background."
    ),
    "notes": "CARD definition for the antibiotic resistant nfsB parent.",
}

NFSA_EVIDENCE = {
    "reference": "ARO:3003754",
    "snippet": (
        "The nfsA-encoded nitroreductase is the major oxygen-insensitive "
        "nitroreductase present in E. coli. NfsA uses only NADPH and has broad "
        "electron acceptor specificity. Mutations in nfsA cause resistance to "
        "nitrofurazone and furazolidone."
    ),
    "notes": (
        "CARD definition for antibiotic resistant nfsA, the genetic background "
        "required for the nfsB second-step phenotype."
    ),
}

MUTATION_EVIDENCE = {
    "reference": "ARO:3000212",
    "snippet": (
        "Point mutations in the DNA may lead to an altered gene product that "
        "may result in antibiotic resistance."
    ),
    "notes": "CARD definition for mutation conferring antibiotic resistance.",
}

NADPH_OXIDOREDUCTASE_EVIDENCE = {
    "reference": "GO:0016651",
    "snippet": (
        "Catalysis of an oxidation-reduction (redox) reaction in which NADH or "
        "NADPH acts as a hydrogen or electron donor and reduces a hydrogen or "
        "electron acceptor."
    ),
    "notes": (
        "GO oxidoreductase activity acting on NAD(P)H covers the reducing "
        "equivalents used by NfsB without guessing the nitrofuran-specific "
        "acceptor."
    ),
}

NITROFURAN_EVIDENCE = {
    "reference": "ARO:3004116",
    "snippet": "nitrofuran antibiotic",
    "notes": "ARO drug-class term inherited by nfsB records.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "mutation conferring antibiotic resistance",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3000212",
}

DRUG_NODE = {
    "node_id": "drug0",
    "label": "nitrofuran antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:3004116",
}

NITROREDUCTION_NODE = {
    "node_id": "nitroreduction",
    "label": "oxygen-insensitive nitrofuran nitroreductase activity",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "GO:0016651",
    "description": (
        "Local NfsB nitrofuran-reduction activity, grounded to oxidoreductase "
        "activity acting on NAD(P)H as the nearest stable GO molecular-function "
        "parent."
    ),
}

LOSS_NODE = {
    "node_id": "loss",
    "label": "diminished NfsB nitroreductase activity",
    "node_type": "STATE",
    "description": (
        "Local loss-of-function state for nfsB mutations that reduce "
        "nitrofuran nitroreduction."
    ),
}

NFSA_BACKGROUND_NODE = {
    "node_id": "nfsa_background",
    "label": "nfsA mutant background",
    "node_type": "TRAIT",
    "grounding": "ARO:3003754",
    "description": (
        "Genetic precondition: the nfsA loss-of-function background required "
        "before nfsB mutations raise nitrofuran resistance."
    ),
}

RESISTANCE_NODE = {
    "node_id": "resistance",
    "label": "antibiotic resistance phenotype",
    "node_type": "PHENOTYPE",
    "grounding": "GO:0046677",
    "description": (
        "Resistance phenotype conferred by this determinant. Grounded to the "
        "nearest available superclass: ARO models determinants and mechanisms "
        "but has no term for the resistance phenotype itself."
    ),
}

CORE_EDGE_KEYS = {
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("determinant", "ARO:2000001", "drug0"),
}

SHARED_NFSB_EDGE_KEYS = {
    ("determinant", "RO:0002327", "nitroreduction"),
    ("nitroreduction", "RO:0002233", "drug0"),
    ("nfsa_background", "RO:0002411", "determinant"),
}

NEW_LOSS_EDGE_KEYS = {
    ("determinant", "RO:0000086", "loss"),
    ("loss", "RO:0002212", "nitroreduction"),
    ("loss", "RO:0002411", "resistance"),
}

EXPECTED_EDGE_KEYS = CORE_EDGE_KEYS | SHARED_NFSB_EDGE_KEYS | NEW_LOSS_EDGE_KEYS
INPUT_EDGE_KEYS = EXPECTED_EDGE_KEYS

EDGE_DESCRIPTIONS = {
    ("determinant", "RO:0000056", "mech0"): (
        "ARO classifies nfsB records under mutation conferring antibiotic "
        "resistance."
    ),
    ("mech0", "RO:0002411", "resistance"): (
        "Loss-of-function point mutations in nfsB are a mutation-mediated "
        "nitrofuran-resistance mechanism."
    ),
    ("determinant", "RO:0002411", "resistance"): (
        "nfsB mutations increase nitrofuran resistance after nfsA has already "
        "been inactivated."
    ),
    ("determinant", "ARO:2000001", "drug0"): (
        "ARO maps the antibiotic resistant nfsB family to nitrofuran "
        "antibiotics."
    ),
    ("determinant", "RO:0002327", "nitroreduction"): (
        "NfsB normally enables oxygen-insensitive reduction of nitroaromatic "
        "nitrofuran antibiotics."
    ),
    ("determinant", "RO:0000086", "loss"): (
        "Resistance-conferring nfsB mutations diminish the minor NfsB "
        "nitroreductase activity."
    ),
    ("loss", "RO:0002212", "nitroreduction"): (
        "Loss of NfsB function inhibits oxygen-insensitive nitrofuran "
        "nitroreduction."
    ),
    ("nitroreduction", "RO:0002233", "drug0"): (
        "NfsB nitroreduction consumes nitrofuran antibiotics as substrates."
    ),
    ("nfsa_background", "RO:0002411", "determinant"): (
        "Loss of the major NfsA nitroreductase is the genetic precondition "
        "under which nfsB mutations are reported to raise resistance."
    ),
    ("loss", "RO:0002411", "resistance"): (
        "Diminished NfsB nitroreductase activity is the second-step change "
        "that increases nitrofuran resistance in an nfsA mutant background."
    ),
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str

    @property
    def is_parent(self) -> bool:
        return self.identifier == PARENT_IDENTIFIER


TARGETS = {
    PARENT_IDENTIFIER: Target(
        identifier=PARENT_IDENTIFIER,
        filename="antibiotic-resistant-nfsb-aro3003755.yaml",
    ),
    "ARO:3003756": Target(
        identifier="ARO:3003756",
        filename=(
            "escherichia-coli-nfsb-with-mutation-conferring-resistance-to-"
            "nitrofurantoin-aro3003756.yaml"
        ),
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


def _edge_key(edge: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(edge.get("subject", "")),
        str(edge.get("predicate_id", "")),
        str(edge.get("object", "")),
    )


def _nodes_by_id(graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(node["node_id"]): node
        for node in _dicts(graph.get("nodes"))
        if "node_id" in node
    }


def _source_evidence(record: dict[str, Any]) -> tuple[dict[str, str], ...]:
    return tuple(
        {
            "reference": str(item["reference"]),
            "notes": str(item.get("notes") or "ARO citation for this record."),
        }
        for item in _dicts(record.get("evidence"))
        if item.get("reference")
    )


def _target_evidence(record: dict[str, Any], target: Target) -> dict[str, str]:
    if target.is_parent:
        return PARENT_EVIDENCE
    return {
        "reference": str(record["identifier"]),
        "snippet": str(record["definition"]),
        "notes": f"CARD definition for {record['label']}.",
    }


def _drug_relation_evidence(target: Target) -> dict[str, str]:
    if target.is_parent:
        notes = (
            "ARO drug-class relationship asserted directly on the antibiotic "
            "resistant nfsB parent."
        )
    else:
        notes = (
            "ARO drug-class relationship asserted on ARO:3003755 and inherited "
            f"by {target.identifier}."
        )
    return {
        "reference": PARENT_IDENTIFIER,
        "snippet": (
            "relationship: confers_resistance_to_drug_class ARO:3004116 ! "
            "nitrofuran antibiotic"
        ),
        "notes": notes,
    }


def _unique_evidence(evidence: tuple[dict[str, str], ...]) -> list[dict[str, str]]:
    unique: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for item in evidence:
        key = (
            item["reference"],
            item.get("snippet", ""),
            item.get("notes", ""),
        )
        if key in seen:
            continue
        seen.add(key)
        unique.append(copy.deepcopy(item))
    return unique


def _edge(
    subject: str,
    predicate: str,
    predicate_id: str,
    object_: str,
    evidence: tuple[dict[str, str], ...],
) -> dict[str, Any]:
    return {
        "subject": subject,
        "predicate": predicate,
        "predicate_id": predicate_id,
        "object": object_,
        "description": EDGE_DESCRIPTIONS[(subject, predicate_id, object_)],
        "evidence": _unique_evidence(evidence),
    }


def _validate_graph(graph: dict[str, Any], target: Target) -> None:
    nodes = _nodes_by_id(graph)
    missing_nodes = sorted(
        {"determinant", "mech0", "drug0", "nitroreduction", "nfsa_background", "resistance"}
        - set(nodes)
    )
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")

    found_edges = set()
    seen: set[tuple[str, str, str]] = set()
    for edge in _dicts(graph.get("edges")):
        key = _edge_key(edge)
        if key not in INPUT_EDGE_KEYS:
            raise ValueError(f"{target.identifier}: unexpected edge {key[0]} -> {key[2]}")
        if key in seen:
            raise ValueError(f"{target.identifier}: duplicate edge {key[0]} -> {key[2]}")
        seen.add(key)
        found_edges.add(key)

    existing_edges = found_edges - NEW_LOSS_EDGE_KEYS
    expected_existing_edges = CORE_EDGE_KEYS | SHARED_NFSB_EDGE_KEYS
    if existing_edges != expected_existing_edges:
        missing = expected_existing_edges - existing_edges
        missing_text = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in sorted(missing))
        raise ValueError(f"{target.identifier}: missing edge(s): {missing_text}")


def _canonical_graph(record: dict[str, Any], target: Target) -> dict[str, Any]:
    graph = record["causal_graphs"][0]
    _validate_graph(graph, target)
    nodes = _nodes_by_id(graph)
    target_evidence = _target_evidence(record, target)
    source_evidence = _source_evidence(record)

    mutation_evidence = (
        target_evidence,
        PARENT_EVIDENCE,
        MUTATION_EVIDENCE,
        *source_evidence,
    )
    nfsb_evidence = (
        target_evidence,
        PARENT_EVIDENCE,
        NADPH_OXIDOREDUCTASE_EVIDENCE,
        *source_evidence,
    )
    background_evidence = (
        target_evidence,
        PARENT_EVIDENCE,
        NFSA_EVIDENCE,
        *source_evidence,
    )
    drug_evidence = (
        target_evidence,
        PARENT_EVIDENCE,
        _drug_relation_evidence(target),
        NITROFURAN_EVIDENCE,
        *source_evidence,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → decreased nitrofuran reduction → resistance",
        "description": (
            "Conservative graph for nfsB-mediated nitrofuran resistance. The "
            "graph grounds the nitrofurazone/nitrofurantoin reduction activity "
            "to a broad NAD(P)H oxidoreductase GO parent, keeps the nfsA-mutant "
            "genetic background explicit, and models diminished NfsB activity "
            "as a described local loss-of-function state."
        ),
        "nodes": [
            copy.deepcopy(nodes["determinant"]),
            copy.deepcopy(MECHANISM_NODE),
            copy.deepcopy(DRUG_NODE),
            copy.deepcopy(NITROREDUCTION_NODE),
            copy.deepcopy(LOSS_NODE),
            copy.deepcopy(NFSA_BACKGROUND_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                mutation_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                mutation_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                mutation_evidence,
            ),
            _edge(
                "determinant",
                "confers resistance to",
                "ARO:2000001",
                "drug0",
                drug_evidence,
            ),
            _edge(
                "determinant",
                "enables",
                "RO:0002327",
                "nitroreduction",
                nfsb_evidence,
            ),
            _edge(
                "determinant",
                "has quality",
                "RO:0000086",
                "loss",
                nfsb_evidence,
            ),
            _edge(
                "loss",
                "negatively regulates",
                "RO:0002212",
                "nitroreduction",
                nfsb_evidence,
            ),
            _edge(
                "nitroreduction",
                "has input",
                "RO:0002233",
                "drug0",
                (*nfsb_evidence, *drug_evidence),
            ),
            _edge(
                "nfsa_background",
                "causally upstream of",
                "RO:0002411",
                "determinant",
                background_evidence,
            ),
            _edge(
                "loss",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                background_evidence,
            ),
        ],
    }


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != target.identifier:
        raise ValueError(f"expected {target.identifier}, found {record.get('identifier')}")

    out = copy.deepcopy(record)
    before = copy.deepcopy(out.get("causal_graphs"))
    graphs = out.get("causal_graphs") or []
    graph_index = next(
        (index for index, item in enumerate(graphs) if item.get("graph_id") == "resistance"),
        None,
    )
    if graph_index is None:
        raise ValueError(f"{target.identifier}: missing resistance causal graph")

    graphs[graph_index] = _canonical_graph(out, target)
    return out, out.get("causal_graphs") != before


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: record is not a mapping")
    identifier = record.get("identifier")
    target = TARGETS.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not an nfsB target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
    normalize_aliases = "&id" in text or "*id" in text
    if not changed and not normalize_aliases:
        return text, False

    out = replace_block(
        text,
        "causal_graphs",
        _dump({"causal_graphs": enriched["causal_graphs"]}),
    )
    if HISTORY_ACTION not in out:
        out = append_to_section(
            out,
            "curation_history",
            _dump({"curation_history": [HISTORY_EVENT]}),
        )
    return out, True


def iter_target_paths(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if not path.is_dir():
        raise ValueError(f"{path} is neither a file nor a directory")
    return [path / target.filename for target in TARGETS.values()]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    parser.add_argument("--path", type=Path, default=ARO_DIR, help="ARO directory or exact nfsB YAML")
    args = parser.parse_args()

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
