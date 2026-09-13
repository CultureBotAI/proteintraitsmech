#!/usr/bin/env python3
"""Curate ArlS/BaeSR efflux-regulator graphs.

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
ARO = ROOT / "data" / "traits" / "function" / "resistance" / "aro"

HISTORY_ACTION = "Curated ArlS/BaeSR efflux-regulator graph"
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

ANTIBIOTIC_EFFLUX_EVIDENCE = {
    "reference": "ARO:0010000",
    "snippet": "Antibiotic resistance via the transport of antibiotics out of the cell.",
    "notes": "CARD definition for the antibiotic efflux resistance mechanism.",
}

GO_POSITIVE_TRANSCRIPTION_EVIDENCE = {
    "reference": "GO:0045893",
    "snippet": (
        "Any process that activates or increases the frequency, rate or "
        "extent of cellular DNA-templated transcription."
    ),
    "notes": "GO definition for broad transcriptional activation.",
}

ARLS_EVIDENCE = {
    "reference": "ARO:3000839",
    "snippet": (
        "ArlS is a protein histidine kinase that phosphorylates ArlR, a "
        "promoter for norA expression."
    ),
    "notes": "CARD definition for arlS.",
}

ARLR_EVIDENCE = {
    "reference": "ARO:3000838",
    "snippet": (
        "ArlR is a response regulator that binds to the norA promoter to "
        "activate expression. ArlR must first be phosphorylated by ArlS."
    ),
    "notes": "CARD definition for the ArlR response-regulator determinant.",
}

NORA_EVIDENCE = {
    "reference": "ARO:3000391",
    "snippet": (
        "NorA is a multidrug efflux pump in Staphylococcus aureus that "
        "confers resistance to fluoroquinolones and other structurally "
        "unrelated antibiotics like acriflavine."
    ),
    "notes": "CARD definition for the NorA efflux pump controlled by ArlRS.",
}

BAESR_EVIDENCE = {
    "reference": "ARO:3000531",
    "snippet": (
        "BaeSR is a two component regulatory system for efflux proteins in "
        "Gram-negative bacteria. BaeR is a response regulator, while BaeS is "
        "a sensor kinase."
    ),
    "notes": "CARD definition for the BaeSR two-component regulatory system.",
}

BAER_EVIDENCE = {
    "reference": "ARO:3000828",
    "snippet": (
        "BaeR is a response regulator that promotes the expression of MdtABC "
        "and AcrD efflux complexes."
    ),
    "notes": "CARD definition for the BaeR response-regulator determinant.",
}

MDTABC_TOLC_EVIDENCE = {
    "reference": "ARO:3000787",
    "snippet": (
        "MdtABC-TolC is a multidrug efflux system in Gram-negative bacteria, "
        "including E. coli and Salmonella. MdtA is a membrane fusion protein; "
        "TolC is the outer membrane channel; MdtBC form a drug transporter."
    ),
    "notes": "CARD definition for an efflux system promoted by BaeR.",
}

ACRD_EVIDENCE = {
    "reference": "ARO:3000491",
    "snippet": (
        "AcrD is an aminoglycoside efflux pump expressed in E. coli. Its "
        "expression can be induced by indole, and is regulated by baeRS and "
        "cpxAR."
    ),
    "notes": "CARD definition for an efflux pump regulated by BaeSR.",
}


@dataclass(frozen=True)
class RecordSpec:
    path: Path
    identifier: str
    title: str
    description: str
    nodes: tuple[dict[str, str], ...]
    edge_specs: tuple[EdgeSpec, ...]


@dataclass(frozen=True)
class EdgeSpec:
    subject: str
    predicate: str
    predicate_id: str
    object: str


NORA_NODE = {
    "node_id": "pump",
    "label": "NorA multidrug efflux pump",
    "node_type": "PROTEIN",
    "grounding": "ARO:3000391",
    "description": "Grounded to CARD's NorA multidrug efflux pump class.",
}

MDTABC_TOLC_NODE = {
    "node_id": "mdtabc_pump",
    "label": "MdtABC-TolC multidrug efflux system",
    "node_type": "PROTEIN",
    "grounding": "ARO:3000787",
    "description": "Grounded to CARD's MdtABC-TolC multidrug efflux system class.",
}

ACRD_NODE = {
    "node_id": "acrd_pump",
    "label": "AcrD aminoglycoside efflux pump",
    "node_type": "PROTEIN",
    "grounding": "ARO:3000491",
    "description": "Grounded to CARD's AcrD aminoglycoside efflux pump class.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "antibiotic efflux",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:0010000",
}

RESISTANCE_NODE = {
    "node_id": "resistance",
    "label": "antibiotic resistance phenotype",
    "node_type": "PHENOTYPE",
    "grounding": "GO:0046677",
    "description": "Resistance phenotype mediated by regulatory activation of efflux.",
}

ARLS_EDGES = (
    EdgeSpec("determinant", "participates in (resistance mechanism)", "RO:0000056", "mech0"),
    EdgeSpec("determinant", "positively regulates (phosphorylates ArlR)", "RO:0002213", "arlr"),
    EdgeSpec("arlr", "enables (activates NorA transcription)", "RO:0002327", "activation"),
    EdgeSpec("activation", "positively regulates (raises NorA expression)", "RO:0002213", "pump"),
    EdgeSpec("pump", "enables (drug efflux)", "RO:0002327", "mech0"),
    EdgeSpec("mech0", "causally upstream of", "RO:0002411", "resistance"),
    EdgeSpec(
        "determinant",
        "causally upstream of (confers resistance)",
        "RO:0002411",
        "resistance",
    ),
)

BAESR_EDGES = (
    EdgeSpec("determinant", "participates in (resistance mechanism)", "RO:0000056", "mech0"),
    EdgeSpec(
        "determinant",
        "enables (activates efflux pump expression)",
        "RO:0002327",
        "activation",
    ),
    EdgeSpec(
        "activation",
        "positively regulates (raises MdtABC expression)",
        "RO:0002213",
        "mdtabc_pump",
    ),
    EdgeSpec(
        "activation",
        "positively regulates (raises AcrD expression)",
        "RO:0002213",
        "acrd_pump",
    ),
    EdgeSpec("mdtabc_pump", "enables (drug efflux)", "RO:0002327", "mech0"),
    EdgeSpec("acrd_pump", "enables (drug efflux)", "RO:0002327", "mech0"),
    EdgeSpec("mech0", "causally upstream of", "RO:0002411", "resistance"),
    EdgeSpec(
        "determinant",
        "causally upstream of (confers resistance)",
        "RO:0002411",
        "resistance",
    ),
)

RECORDS = (
    RecordSpec(
        path=ARO / "arls-aro3000839.yaml",
        identifier="ARO:3000839",
        title="ArlS → ArlR phosphorylation → NorA expression → antibiotic efflux",
        description=(
            "Curated resistance-causation graph for ArlS activation of NorA "
            "efflux. The graph grounds phosphorylated ArlR as the intermediate "
            "response regulator and follows NorA expression to antibiotic efflux."
        ),
        nodes=(
            {
                "node_id": "determinant",
                "label": "arlS",
                "node_type": "PROTEIN",
                "grounding": "ARO:3000839",
            },
            MECHANISM_NODE,
            {
                "node_id": "arlr",
                "label": "ArlR response regulator",
                "node_type": "PROTEIN",
                "grounding": "ARO:3000838",
                "description": "Grounded to CARD's ArlR response-regulator class.",
            },
            {
                "node_id": "activation",
                "label": "positive regulation of NorA transcription",
                "node_type": "BIOLOGICAL_PROCESS",
                "grounding": "GO:0045893",
                "description": (
                    "Grounded to broad GO DNA-templated transcriptional "
                    "activation because ArlR activates norA expression."
                ),
            },
            NORA_NODE,
            RESISTANCE_NODE,
        ),
        edge_specs=ARLS_EDGES,
    ),
    RecordSpec(
        path=ARO / "baesr-aro3000531.yaml",
        identifier="ARO:3000531",
        title="BaeSR → MdtABC/AcrD expression → antibiotic efflux",
        description=(
            "Curated resistance-causation graph for the BaeSR two-component "
            "system. The graph grounds the BaeSR branch through BaeR-promoted "
            "MdtABC-TolC and AcrD expression and follows both efflux systems "
            "to the antibiotic-efflux mechanism."
        ),
        nodes=(
            {
                "node_id": "determinant",
                "label": "baeSR",
                "node_type": "PROTEIN",
                "grounding": "ARO:3000531",
            },
            MECHANISM_NODE,
            MDTABC_TOLC_NODE,
            ACRD_NODE,
            {
                "node_id": "activation",
                "label": "positive regulation of MdtABC/AcrD transcription",
                "node_type": "BIOLOGICAL_PROCESS",
                "grounding": "GO:0045893",
                "description": (
                    "Grounded to broad GO DNA-templated transcriptional "
                    "activation because BaeR promotes MdtABC and AcrD expression."
                ),
            },
            RESISTANCE_NODE,
        ),
        edge_specs=BAESR_EDGES,
    ),
)


EDGE_DESCRIPTIONS = {
    ("determinant", "mech0"): (
        "CARD classifies this regulator under antibiotic efflux because it "
        "promotes expression of a named efflux pump or pump system."
    ),
    ("determinant", "arlr"): (
        "ArlS phosphorylates ArlR, the response regulator that activates norA expression."
    ),
    ("arlr", "activation"): "ArlR binds the norA promoter to activate expression.",
    ("activation", "pump"): "ArlR-dependent activation increases NorA expression.",
    ("pump", "mech0"): "NorA is the multidrug pump whose expression supplies antibiotic efflux.",
    ("activation", "mdtabc_pump"): "BaeR-dependent activation increases MdtABC expression.",
    ("activation", "acrd_pump"): "BaeR-dependent activation increases AcrD expression.",
    ("mdtabc_pump", "mech0"): (
        "MdtABC-TolC is one multidrug efflux system promoted by BaeR."
    ),
    ("acrd_pump", "mech0"): "AcrD is one efflux pump regulated by BaeSR.",
    ("mech0", "resistance"): "Drug export through the named pump supplies antibiotic efflux.",
    ("determinant", "activation"): (
        "The BaeSR two-component system includes the BaeR response regulator "
        "that promotes MdtABC and AcrD expression."
    ),
    ("determinant", "resistance"): (
        "The regulator increases efflux-pump expression, which drives "
        "efflux-mediated resistance."
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


def _unique_evidence(*items: dict[str, str] | None) -> list[dict[str, str]]:
    evidence: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for item in items:
        if item is None:
            continue
        marker = (item["reference"], item.get("snippet", ""))
        if marker in seen:
            continue
        seen.add(marker)
        evidence.append(copy.deepcopy(item))
    return evidence


def _edge_evidence(spec: RecordSpec, edge: EdgeSpec) -> list[dict[str, str]]:
    is_baesr = spec.identifier == "ARO:3000531"
    if is_baesr:
        base = [BAESR_EVIDENCE, BAER_EVIDENCE]
        target_evidence = {
            "mdtabc_pump": MDTABC_TOLC_EVIDENCE,
            "acrd_pump": ACRD_EVIDENCE,
        }
    else:
        base = [ARLS_EVIDENCE, ARLR_EVIDENCE]
        target_evidence = {"arlr": ARLR_EVIDENCE, "pump": NORA_EVIDENCE}

    extra: list[dict[str, str] | None] = []
    if edge.object == "activation" or edge.subject == "activation":
        extra.append(GO_POSITIVE_TRANSCRIPTION_EVIDENCE)
    if edge.subject == "mech0" or edge.object == "mech0":
        extra.append(ANTIBIOTIC_EFFLUX_EVIDENCE)
    extra.append(target_evidence.get(edge.object))
    extra.append(target_evidence.get(edge.subject))

    if edge.object == "resistance":
        extra.extend(target_evidence.values())
        extra.append(ANTIBIOTIC_EFFLUX_EVIDENCE)
    return _unique_evidence(*base, *extra)


def _nodes(spec: RecordSpec) -> list[dict[str, str]]:
    return [copy.deepcopy(node) for node in spec.nodes]


def _edges(spec: RecordSpec) -> list[dict[str, Any]]:
    edges: list[dict[str, Any]] = []
    for edge in spec.edge_specs:
        key = (edge.subject, edge.object)
        edges.append(
            {
                "subject": edge.subject,
                "predicate": edge.predicate,
                "predicate_id": edge.predicate_id,
                "object": edge.object,
                "description": EDGE_DESCRIPTIONS[key],
                "evidence": _edge_evidence(spec, edge),
            }
        )
    return edges


def _graph(spec: RecordSpec) -> dict[str, Any]:
    return {
        "graph_id": "resistance",
        "title": spec.title,
        "description": spec.description,
        "nodes": _nodes(spec),
        "edges": _edges(spec),
    }


def enrich_record(record: dict[str, Any], spec: RecordSpec) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != spec.identifier:
        raise ValueError(f"expected {spec.identifier}, found {record.get('identifier')}")
    if len(_dicts(record.get("causal_graphs"))) != 1:
        raise ValueError(f"{spec.identifier}: expected exactly one causal graph")

    out = copy.deepcopy(record)
    before = copy.deepcopy(out["causal_graphs"])
    out["mapping_status"] = "REVIEWED"
    out["causal_graphs"] = [_graph(spec)]
    return out, out["causal_graphs"] != before or out != record


def enrich_text(text: str, spec: RecordSpec) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError("expected a YAML mapping")

    enriched, changed = enrich_record(record, spec)
    out = text.replace("mapping_status: SEEDED", "mapping_status: REVIEWED", 1)
    out = replace_block(out, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    if HISTORY_ACTION not in out:
        out = append_to_section(out, "curation_history", _dump({"curation_history": [HISTORY_EVENT]}))
        changed = True

    if "&id" in out or "*id" in out:
        raise ValueError("YAML anchors leaked into output")
    return out, changed or out != text


def run(apply: bool) -> tuple[int, int]:
    changed_count = 0
    for spec in RECORDS:
        before = spec.path.read_text(encoding="utf-8")
        after, changed = enrich_text(before, spec)
        if changed:
            changed_count += 1
            print(f"  {'wrote' if apply else 'would write'} {spec.path.name}")
            if apply:
                spec.path.write_text(after, encoding="utf-8")
    return changed_count, len(RECORDS) - changed_count


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    args = parser.parse_args(argv)

    changed_count, already = run(args.apply)
    print(f"{'changed' if args.apply else 'would change'}: {changed_count}")
    print(f"already enriched: {already}")
    if not args.apply:
        print("dry run -- pass --apply to write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
