#!/usr/bin/env python3
"""Ground the Neisseria gonorrhoeae mtrR mutant graph.

The Neisseria gonorrhoeae mtrR mutant record inherited an RND-pump seed, so
its prior graph put RND transporter domain and AcrB fold nodes on the mutant
MtrR regulator itself. This updater rewrites the graph as MtrR loss of
mtrCDE repression, grounds the regulated MtrCDE efflux pump, and preserves the
ARO-supported antibiotic-efflux route.

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

ROOT = Path(__file__).resolve().parent.parent
ARO_DIR = ROOT / "data" / "traits" / "function" / "resistance" / "aro"

HISTORY_ACTION = "Grounded Neisseria gonorrhoeae mtrR mutant efflux graph"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

IDENTIFIER = "ARO:3004851"
FILENAME = "neisseria-gonorrhoeae-mtrr-with-mutation-conferring-resistance-aro3004851.yaml"

TARGET_EVIDENCE = {
    "reference": IDENTIFIER,
    "snippet": (
        "MtrR is a repressor of mtrCDE efflux pump expression, point mutations "
        "in mtrR confer resistance to azithromycin and other drugs."
    ),
    "notes": (
        "CARD definition for Neisseria gonorrhoeae mtrR mutations that confer "
        "azithromycin resistance."
    ),
}

MTRR_EVIDENCE = {
    "reference": "ARO:3000817",
    "snippet": (
        "MtrR is a repressor of mtrCDE expression. Mutations in mtrR increase "
        "multidrug resistance."
    ),
    "notes": "CARD definition for the mtrR repressor determinant.",
}

MTRCDE_EVIDENCE = {
    "reference": "ARO:3000369",
    "snippet": (
        "The mtr (multiple transferable resistance) system of Neisseria "
        "gonorrhoeae confers resistance to many hydrophobic agents including "
        "antibiotics, fatty-acids and detergents. MtrCDE is homologous to "
        "AcrAB-TolC, where MtrC is the membrane fusion protein, MtrD is the "
        "inner membrane transporter, and MtrE is the outer membrane channel "
        "protein."
    ),
    "notes": "CARD definition for the MtrCDE efflux pump repressed by MtrR.",
}

EFFLUX_EVIDENCE = {
    "reference": "ARO:0010000",
    "snippet": "Antibiotic resistance via the transport of antibiotics out of the cell.",
    "notes": "CARD definition for the antibiotic-efflux resistance mechanism.",
}

GO_NEGATIVE_TRANSCRIPTION_EVIDENCE = {
    "reference": "GO:0045892",
    "snippet": (
        "Any process that stops, prevents, or reduces the frequency, rate or extent "
        "of cellular DNA-templated transcription."
    ),
    "notes": "GO definition for the broad transcriptional repression process.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "antibiotic efflux",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:0010000",
}

PUMP_NODE = {
    "node_id": "pump",
    "label": "MtrCDE",
    "node_type": "PROTEIN",
    "grounding": "ARO:3000369",
    "description": "Grounded to CARD's MtrCDE, the pump derepressed by mtrR mutations.",
}

REPRESSION_NODE = {
    "node_id": "repression",
    "label": "negative regulation of mtrCDE expression",
    "node_type": "BIOLOGICAL_PROCESS",
    "grounding": "GO:0045892",
    "description": (
        "Grounded to the broad GO DNA-templated transcriptional repression process "
        "because MtrR represses mtrCDE expression."
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
}

DEREPRESSION_EDGE_KEYS = {
    ("repression", "RO:0002212", "pump"),
    ("determinant", "RO:0002212", "repression"),
    ("pump", "RO:0002327", "mech0"),
}

OBSOLETE_RND_EDGE_KEYS = {
    ("domain", "BFO:0000050", "determinant"),
    ("determinant", "RO:0002350", "fold"),
    ("domain", "RO:0002327", "mech0"),
}

EXPECTED_EDGE_KEYS = CORE_EDGE_KEYS | DEREPRESSION_EDGE_KEYS

EDGE_DESCRIPTIONS = {
    ("determinant", "RO:0000056", "mech0"): (
        "ARO classifies this mtrR mutant under antibiotic efflux because mtrR "
        "mutations derepress the MtrCDE efflux pump."
    ),
    ("mech0", "RO:0002411", "resistance"): (
        "Antibiotic efflux is the broad resistance mechanism supplied by "
        "derepressed MtrCDE."
    ),
    ("determinant", "RO:0002411", "resistance"): (
        "Point mutations in mtrR derepress MtrCDE and confer resistance to "
        "azithromycin and other drugs."
    ),
    ("repression", "RO:0002212", "pump"): (
        "Normal MtrR-mediated transcriptional repression keeps MtrCDE expression low."
    ),
    ("determinant", "RO:0002212", "repression"): (
        "Resistance-associated mtrR point mutations reduce normal repression of "
        "mtrCDE expression."
    ),
    ("pump", "RO:0002327", "mech0"): (
        "MtrCDE is the multidrug pump whose derepressed expression supplies "
        "antibiotic efflux."
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


def _unique_evidence(evidence: tuple[dict[str, str], ...]) -> list[dict[str, str]]:
    unique: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for item in evidence:
        key = (item["reference"], " ".join(item.get("snippet", "").split()))
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


def _validate_graph(graph: dict[str, Any]) -> None:
    nodes = _nodes_by_id(graph)
    missing_nodes = sorted({"determinant", "mech0", "resistance"} - set(nodes))
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{IDENTIFIER}: missing node(s): {missing}")

    input_edges = EXPECTED_EDGE_KEYS | OBSOLETE_RND_EDGE_KEYS
    seen: set[tuple[str, str, str]] = set()
    for edge in _dicts(graph.get("edges")):
        key = _edge_key(edge)
        if key not in input_edges:
            raise ValueError(f"{IDENTIFIER}: unexpected edge {key[0]} -> {key[2]}")
        if key in seen:
            raise ValueError(f"{IDENTIFIER}: duplicate edge {key[0]} -> {key[2]}")
        seen.add(key)

    missing_edges = CORE_EDGE_KEYS - seen
    if missing_edges:
        missing = ", ".join(
            f"{subject} -> {object_}"
            for subject, _, object_ in sorted(missing_edges)
        )
        raise ValueError(f"{IDENTIFIER}: missing edge(s): {missing}")


def _canonical_graph(record: dict[str, Any]) -> dict[str, Any]:
    graph = record["causal_graphs"][0]
    _validate_graph(graph)
    nodes = _nodes_by_id(graph)
    source_evidence = _source_evidence(record)
    efflux_evidence = (
        TARGET_EVIDENCE,
        MTRR_EVIDENCE,
        MTRCDE_EVIDENCE,
        EFFLUX_EVIDENCE,
        *source_evidence,
    )
    repression_evidence = (
        TARGET_EVIDENCE,
        MTRR_EVIDENCE,
        GO_NEGATIVE_TRANSCRIPTION_EVIDENCE,
        *source_evidence,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → MtrCDE derepression → antibiotic efflux",
        "description": (
            "Curated graph for Neisseria gonorrhoeae mtrR resistance mutations. "
            "The graph replaces the stale RND-pump domain seed with the local "
            "MtrR repressor biology: point mutations in mtrR reduce repression "
            "of MtrCDE expression, derepressed MtrCDE supplies antibiotic efflux, "
            "and increased efflux confers resistance."
        ),
        "nodes": [
            copy.deepcopy(nodes["determinant"]),
            copy.deepcopy(MECHANISM_NODE),
            copy.deepcopy(PUMP_NODE),
            copy.deepcopy(REPRESSION_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                efflux_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                efflux_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                efflux_evidence,
            ),
            _edge(
                "repression",
                "negatively regulates (holds pump expression down)",
                "RO:0002212",
                "pump",
                repression_evidence,
            ),
            _edge(
                "determinant",
                "negatively regulates (loss lifts the repression)",
                "RO:0002212",
                "repression",
                repression_evidence,
            ),
            _edge(
                "pump",
                "enables (drug efflux)",
                "RO:0002327",
                "mech0",
                efflux_evidence,
            ),
        ],
    }


def enrich_record(record: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != IDENTIFIER:
        raise ValueError(f"expected {IDENTIFIER}, found {record.get('identifier')}")

    out = copy.deepcopy(record)
    before = copy.deepcopy(out.get("causal_graphs"))
    graphs = out.get("causal_graphs") or []
    graph_index = next(
        (index for index, item in enumerate(graphs) if item.get("graph_id") == "resistance"),
        None,
    )
    if graph_index is None:
        raise ValueError(f"{IDENTIFIER}: missing resistance causal graph")

    graphs[graph_index] = _canonical_graph(out)
    return out, out.get("causal_graphs") != before


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: record is not a mapping")
    if record.get("identifier") != IDENTIFIER:
        raise ValueError(f"{path}: not a Neisseria gonorrhoeae mtrR mutant target")
    if path.name != FILENAME:
        raise ValueError(f"{path}: target {IDENTIFIER} must be in {FILENAME}")

    enriched, changed = enrich_record(record)
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
    return [path / FILENAME]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    parser.add_argument(
        "--path",
        type=Path,
        default=ARO_DIR,
        help="ARO directory or exact Neisseria gonorrhoeae mtrR mutant YAML",
    )
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
