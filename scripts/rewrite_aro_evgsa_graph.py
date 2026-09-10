#!/usr/bin/env python3
"""Curate the evgSA EmrKY/MdtEF efflux-regulator graph.

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
TARGET = (
    ROOT
    / "data"
    / "traits"
    / "function"
    / "resistance"
    / "aro"
    / "evgsa-aro3000515.yaml"
)

HISTORY_ACTION = "Curated evgSA EmrKY/MdtEF efflux-regulator graph"
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

EVGSA_EVIDENCE = {
    "reference": "ARO:3000515",
    "snippet": (
        "EvgSA is a two-component regulatory system that regulates MdtEF and "
        "EmrKY expression for multidrug resistance. EvgS is a sensor protein "
        "that phosphorylates the regulatory protein EvgA, though EvgA can be "
        "phosphorylated by other methods when it is overexpressed."
    ),
    "notes": "CARD definition for evgSA.",
}

EVGA_EVIDENCE = {
    "reference": "ARO:3000832",
    "snippet": (
        "EvgA, when phosphorylated, is a positive regulator for efflux "
        "protein complexes emrKY and mdtEF."
    ),
    "notes": "CARD definition for the evgA efflux-pump activator.",
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


@dataclass(frozen=True)
class Pump:
    node_id: str
    label: str
    grounding: str
    activated_process: str
    snippet: str

    @property
    def evidence(self) -> dict[str, str]:
        return {
            "reference": self.grounding,
            "snippet": self.snippet,
            "notes": f"CARD definition for the {self.label} pump activated by EvgSA.",
        }

    @property
    def node(self) -> dict[str, str]:
        return {
            "node_id": self.node_id,
            "label": self.label,
            "node_type": "PROTEIN",
            "grounding": self.grounding,
            "description": f"Grounded to CARD's {self.label}, a pump activated by EvgSA.",
        }


EMRKY_TOLC = Pump(
    node_id="emrky_tolc",
    label="EmrKY-TolC",
    grounding="ARO:3000373",
    activated_process="emrKY transcription",
    snippet=(
        "EmrKY is a homolog of EmrAB found in E. coli. Together with TolC, it "
        "is a tripartite multidrug transporter."
    ),
)

MDTEF_TOLC = Pump(
    node_id="mdtef_tolc",
    label="MdtEF-TolC",
    grounding="ARO:3000788",
    activated_process="mdtEF transcription",
    snippet=(
        "MdtEF-TolC is a multidrug efflux complex in Gram-negative bacteria, "
        "including E. coli. MdtE is the membrane fusion protein, MdtF is the "
        "inner membrane transporter, while TolC is the outer membrane channel."
    ),
)

PUMPS = (EMRKY_TOLC, MDTEF_TOLC)

EDGE_DESCRIPTIONS = {
    ("determinant", "mech0"): (
        "CARD classifies evgSA under antibiotic efflux because it regulates "
        "the EmrKY-TolC and MdtEF-TolC efflux complexes."
    ),
    ("mech0", "resistance"): (
        "The broad efflux mechanism represents activity of the EvgSA-regulated "
        "EmrKY-TolC and MdtEF-TolC multidrug pumps."
    ),
    ("determinant", "resistance"): (
        "The EvgSA two-component system activates EmrKY-TolC and MdtEF-TolC "
        "expression, increasing antibiotic efflux."
    ),
    ("determinant", "activation"): (
        "EvgSA participates in positive regulation of emrKY and mdtEF transcription."
    ),
    ("activation", "emrky_tolc"): (
        "Transcriptional activation raises emrKY transcription and increases "
        "expression of EmrKY-TolC."
    ),
    ("activation", "mdtef_tolc"): (
        "Transcriptional activation raises mdtEF transcription and increases "
        "expression of MdtEF-TolC."
    ),
    ("emrky_tolc", "mech0"): (
        "EmrKY-TolC is a multidrug pump whose EvgSA-activated expression "
        "supplies antibiotic efflux."
    ),
    ("mdtef_tolc", "mech0"): (
        "MdtEF-TolC is a multidrug pump whose EvgSA-activated expression "
        "supplies antibiotic efflux."
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
    seen: set[tuple[str, str]] = set()
    for item in items:
        marker = (item["reference"], item.get("snippet", ""))
        if marker in seen:
            continue
        seen.add(marker)
        evidence.append(copy.deepcopy(item))
    return evidence


def _edge(
    subject: str,
    predicate: str,
    predicate_id: str,
    object_: str,
    evidence: list[dict[str, str]],
) -> dict[str, Any]:
    return {
        "subject": subject,
        "predicate": predicate,
        "predicate_id": predicate_id,
        "object": object_,
        "description": EDGE_DESCRIPTIONS[(subject, object_)],
        "evidence": copy.deepcopy(evidence),
    }


def _graph() -> dict[str, Any]:
    pump_evidence = _unique_evidence(
        EVGSA_EVIDENCE,
        EVGA_EVIDENCE,
        EMRKY_TOLC.evidence,
        MDTEF_TOLC.evidence,
        ANTIBIOTIC_EFFLUX_EVIDENCE,
    )

    edges = [
        _edge(
            "determinant",
            "participates in (resistance mechanism)",
            "RO:0000056",
            "mech0",
            pump_evidence,
        ),
        _edge(
            "mech0",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            pump_evidence,
        ),
        _edge(
            "determinant",
            "causally upstream of (confers resistance)",
            "RO:0002411",
            "resistance",
            pump_evidence,
        ),
        _edge(
            "determinant",
            "enables (activates pump transcription)",
            "RO:0002327",
            "activation",
            _unique_evidence(EVGSA_EVIDENCE, EVGA_EVIDENCE, GO_POSITIVE_TRANSCRIPTION_EVIDENCE),
        ),
    ]
    for pump in PUMPS:
        edges.append(
            _edge(
                "activation",
                "positively regulates (raises pump expression)",
                "RO:0002213",
                pump.node_id,
                _unique_evidence(
                    EVGSA_EVIDENCE,
                    EVGA_EVIDENCE,
                    GO_POSITIVE_TRANSCRIPTION_EVIDENCE,
                    pump.evidence,
                ),
            )
        )
    for pump in PUMPS:
        edges.append(
            _edge(
                pump.node_id,
                "enables (drug efflux)",
                "RO:0002327",
                "mech0",
                _unique_evidence(EVGSA_EVIDENCE, EVGA_EVIDENCE, pump.evidence),
            )
        )

    return {
        "graph_id": "resistance",
        "title": "evgSA → EmrKY/MdtEF expression → antibiotic efflux",
        "description": (
            "Curated graph for EvgSA efflux-pump activation. The graph grounds "
            "the EmrKY-TolC and MdtEF-TolC efflux pumps named in the evgSA "
            "branch and links EvgSA-dependent transcriptional activation of "
            "both pump complexes to antibiotic efflux."
        ),
        "nodes": [
            {
                "node_id": "determinant",
                "label": "evgSA",
                "node_type": "PROTEIN",
                "grounding": "ARO:3000515",
            },
            {
                "node_id": "mech0",
                "label": "antibiotic efflux",
                "node_type": "MOLECULAR_FUNCTION",
                "grounding": "ARO:0010000",
            },
            *(pump.node for pump in PUMPS),
            {
                "node_id": "activation",
                "label": "positive regulation of emrKY and mdtEF transcription",
                "node_type": "BIOLOGICAL_PROCESS",
                "grounding": "GO:0045893",
                "description": (
                    "Grounded to broad GO DNA-templated transcriptional "
                    "activation because EvgSA promotes EmrKY and MdtEF "
                    "pump-complex expression."
                ),
            },
            {
                "node_id": "resistance",
                "label": "antibiotic resistance phenotype",
                "node_type": "PHENOTYPE",
                "grounding": "GO:0046677",
                "description": (
                    "Antibiotic resistance phenotype mediated by EvgSA-dependent "
                    "activation of efflux."
                ),
            },
        ],
        "edges": edges,
    }


def enrich_record(record: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != "ARO:3000515":
        raise ValueError(f"expected ARO:3000515, found {record.get('identifier')}")
    if len(_dicts(record.get("causal_graphs"))) != 1:
        raise ValueError("ARO:3000515: expected exactly one causal graph")

    out = copy.deepcopy(record)
    before = copy.deepcopy(out["causal_graphs"])
    out["causal_graphs"] = [_graph()]
    return out, out["causal_graphs"] != before


def enrich_text(text: str) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError("expected a YAML mapping")

    enriched, changed = enrich_record(record)
    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    if HISTORY_ACTION not in out:
        out = append_to_section(out, "curation_history", _dump({"curation_history": [HISTORY_EVENT]}))
        changed = True

    if "&id" in out or "*id" in out:
        raise ValueError("YAML anchors leaked into output")
    return out, changed


def run(apply: bool) -> bool:
    before = TARGET.read_text(encoding="utf-8")
    after, changed = enrich_text(before)
    if changed:
        print(f"  {'wrote' if apply else 'would write'} {TARGET.name}")
        if apply:
            TARGET.write_text(after, encoding="utf-8")
    return changed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    args = parser.parse_args(argv)

    changed = run(args.apply)
    print(f"{'changed' if args.apply else 'would change'}: {int(changed)}")
    print(f"already enriched: {int(not changed)}")
    if not args.apply:
        print("dry run -- pass --apply to write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
