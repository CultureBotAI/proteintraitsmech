#!/usr/bin/env python3
"""Rewrite the TolC outer-membrane efflux-subunit ARO graph.

TolC is an outer-membrane channel used by multiple multidrug efflux complexes.
The existing graph incorrectly describes its local transporter node with an MFS
inner-membrane model. This updater keeps the graph family-neutral: TolC is part
of a local tripartite efflux complex that drives antibiotic export.

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
FILENAME = "tolc-aro3000237.yaml"
IDENTIFIER = "ARO:3000237"

HISTORY_CURATOR = "codex-causal-graph-quality"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": "Completed TolC outer-membrane efflux-subunit causal graph",
    "llm_assisted": True,
}

ANTIBIOTIC_EFFLUX_EVIDENCE = {
    "reference": "ARO:0010000",
    "snippet": "Antibiotic resistance via the transport of antibiotics out of the cell.",
    "notes": "CARD definition for the antibiotic efflux resistance mechanism.",
}

EFFLUX_PUMP_EVIDENCE = {
    "reference": "ARO:3000159",
    "snippet": "Efflux proteins that pump antibiotic out of a cell to confer resistance.",
    "notes": "CARD definition for efflux pump complexes and subunits.",
}

EFFLUX_SUBUNIT_EVIDENCE = {
    "reference": "ARO:3000748",
    "snippet": "Subunits of efflux proteins that pump antibiotic out of a cell to confer resistance.",
    "notes": "CARD definition for efflux pump subunits.",
}

TOLC_EVIDENCE = {
    "reference": IDENTIFIER,
    "snippet": (
        "TolC is a protein subunit of many multidrug efflux complexes in Gram "
        "negative bacteria. It is an outer membrane efflux protein and is "
        "constitutively open."
    ),
    "notes": "CARD definition for TolC.",
}

RND_TOLC_EVIDENCE = {
    "reference": "PMID:16915237",
    "snippet": (
        "AcrB is a principal multidrug efflux transporter in Escherichia coli "
        "that cooperates with an outer-membrane channel, TolC, and a "
        "membrane-fusion protein, AcrA."
    ),
    "notes": "Evidence for TolC as the outer-membrane channel in a tripartite pump.",
}

ABC_TOLC_EVIDENCE = {
    "reference": "PMID:29109272",
    "snippet": (
        "MacB is an ABC transporter that collaborates with the MacA adaptor "
        "protein and TolC exit duct to drive efflux of antibiotics and "
        "enterotoxin STII out of the bacterial cell."
    ),
    "notes": "Evidence for TolC as the exit duct in an ABC tripartite pump.",
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

EXPORT_NODE = {
    "node_id": "export",
    "label": "xenobiotic detoxification by transmembrane export across the plasma membrane",
    "node_type": "BIOLOGICAL_PROCESS",
    "grounding": "GO:1990961",
}

PUMP_NODE = {
    "node_id": "transporter",
    "label": "TolC-dependent tripartite efflux complex",
    "node_type": "STATE",
    "description": (
        "Local state for an assembled Gram-negative tripartite efflux pump "
        "using TolC as its outer-membrane channel."
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


def _unique_evidence(*items: dict[str, str]) -> list[dict[str, str]]:
    evidence: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in items:
        reference = item["reference"]
        if reference in seen:
            continue
        seen.add(reference)
        evidence.append(copy.deepcopy(item))
    return evidence


def _edge(
    subject: str,
    predicate: str,
    predicate_id: str,
    object_: str,
    description: str,
    *evidence: dict[str, str],
) -> dict[str, Any]:
    return {
        "subject": subject,
        "predicate": predicate,
        "predicate_id": predicate_id,
        "object": object_,
        "description": description,
        "evidence": _unique_evidence(*evidence),
    }


def _determinant_node(record: dict[str, Any]) -> dict[str, str]:
    return {
        "node_id": "determinant",
        "label": str(record["label"]),
        "node_type": "PROTEIN",
        "grounding": IDENTIFIER,
    }


def _graph(record: dict[str, Any]) -> dict[str, Any]:
    common_evidence = (
        TOLC_EVIDENCE,
        EFFLUX_SUBUNIT_EVIDENCE,
        EFFLUX_PUMP_EVIDENCE,
        ANTIBIOTIC_EFFLUX_EVIDENCE,
        RND_TOLC_EVIDENCE,
        ABC_TOLC_EVIDENCE,
    )
    complex_evidence = (
        TOLC_EVIDENCE,
        EFFLUX_SUBUNIT_EVIDENCE,
        RND_TOLC_EVIDENCE,
        ABC_TOLC_EVIDENCE,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → TolC-dependent efflux complex → resistance",
        "description": (
            "Curated resistance-causation graph for the TolC outer-membrane "
            "efflux channel. TolC is modeled as part of a local tripartite "
            "efflux complex, not as the inner-membrane transporter itself."
        ),
        "nodes": [
            _determinant_node(record),
            {
                "node_id": "mech0",
                "label": "antibiotic efflux",
                "node_type": "MOLECULAR_FUNCTION",
                "grounding": "ARO:0010000",
            },
            copy.deepcopy(PUMP_NODE),
            copy.deepcopy(EXPORT_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "CARD classifies TolC under antibiotic efflux through its "
                "role as an efflux-pump subunit.",
                *common_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Antibiotic efflux confers resistance by transporting antibiotics "
                "out of the cell.",
                *common_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "TolC contributes to multidrug resistance as the outer-membrane "
                "channel of efflux complexes.",
                *common_evidence,
            ),
            _edge(
                "determinant",
                "part of",
                "BFO:0000050",
                "transporter",
                "TolC is the outer-membrane channel subunit of modeled "
                "tripartite efflux complexes.",
                *complex_evidence,
            ),
            _edge(
                "transporter",
                "causally upstream of",
                "RO:0002411",
                "export",
                "TolC-dependent tripartite pumps export antibiotics out of the cell.",
                *common_evidence,
            ),
            _edge(
                "export",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Antibiotic export lowers intracellular drug exposure and causes "
                "the modeled resistance phenotype.",
                EFFLUX_PUMP_EVIDENCE,
                ANTIBIOTIC_EFFLUX_EVIDENCE,
                RND_TOLC_EVIDENCE,
                ABC_TOLC_EVIDENCE,
            ),
        ],
    }


def _validate_record(record: dict[str, Any]) -> None:
    if record.get("identifier") != IDENTIFIER:
        raise ValueError(f"{FILENAME}: expected {IDENTIFIER}, found {record.get('identifier')}")
    if not record.get("label"):
        raise ValueError(f"{IDENTIFIER}: missing label")

    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1 or graphs[0].get("graph_id") != "resistance":
        raise ValueError(f"{IDENTIFIER}: expected exactly one resistance graph")

    node_ids = {
        str(node.get("node_id"))
        for node in _dicts(graphs[0].get("nodes"))
        if node.get("node_id")
    }
    missing = {"determinant", "mech0", "transporter", "export", "resistance"} - node_ids
    if missing:
        missing_ids = ", ".join(sorted(missing))
        raise ValueError(f"{IDENTIFIER}: missing node(s): {missing_ids}")


def enrich_record(record: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    _validate_record(record)

    out = copy.deepcopy(record)
    out["causal_graphs"] = [_graph(record)]
    return out, out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    if path.name != FILENAME:
        raise ValueError(f"{path}: expected filename {FILENAME}")

    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    enriched, changed = enrich_record(record)
    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    if HISTORY_CURATOR not in out:
        out = append_to_section(out, "curation_history", _dump({"curation_history": [HISTORY_EVENT]}))
        changed = True

    if "&id" in out or "*id" in out:
        raise ValueError(f"{path}: YAML anchors leaked into output")
    return out, changed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    parser.add_argument(
        "--path",
        type=Path,
        default=ARO_DIR / FILENAME,
        help="TolC YAML file",
    )
    args = parser.parse_args(argv)

    try:
        before = args.path.read_text(encoding="utf-8")
        after, changed = enrich_text(before, args.path)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"PROBLEM: {exc}", file=sys.stderr)
        return 1

    if changed:
        print(f"  {'wrote' if args.apply else 'would write'} {args.path.name}")
        if args.apply:
            args.path.write_text(after, encoding="utf-8")

    print(f"{'changed' if args.apply else 'would change'}: {int(changed)}")
    print(f"already enriched: {int(not changed)}")
    if not args.apply:
        print("dry run -- pass --apply to write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
