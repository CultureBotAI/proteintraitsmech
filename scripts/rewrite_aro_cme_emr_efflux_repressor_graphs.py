#!/usr/bin/env python3
"""Ground and complete CmeR/CRP/EmrR loss-of-repression ARO graphs.

The three records handled here share the same stale AcrR-shaped seed: an
ungrounded "pump" node, an ungrounded repression node, a wild-type
determinant-to-repression role edge, no pump-to-efflux edge, and AcrR evidence
on every edge.  This updater grounds each record's named pump, grounds broad
transcriptional repression to GO, removes the obsolete wild-type role edge from
the mutant causal path, adds the missing pump-to-efflux edge, and replaces AcrR
evidence with exact target/pump evidence.

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
    "timestamp": "2026-09-05T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": (
        "Replaced stale archetype evidence on CmeR/CRP/EmrR graphs, grounded the "
        "named efflux pumps and transcriptional-repression nodes, removed the "
        "obsolete wild-type repressor edge, and linked pump expression to antibiotic "
        "efflux"
    ),
    "llm_assisted": True,
}

GO_NEGATIVE_TRANSCRIPTION_EVIDENCE = {
    "reference": "GO:0045892",
    "snippet": (
        "Any process that stops, prevents, or reduces the frequency, rate or extent "
        "of cellular DNA-templated transcription."
    ),
    "notes": "GO definition for the broad transcriptional repression process.",
}

TARGET_EVIDENCE = {
    "ARO:3000526": {
        "reference": "ARO:3000526",
        "snippet": (
            "CmeR is a repressor for the CmeABC multidrug efflux pump, binding to "
            "the cmeABC promoter region."
        ),
        "notes": "CARD definition for the cmeR repressor determinant.",
    },
    "ARO:3000518": {
        "reference": "ARO:3000518",
        "snippet": (
            "CRP is a global regulator that represses MdtEF multidrug efflux pump "
            "expression."
        ),
        "notes": "CARD definition for the CRP repressor determinant.",
    },
    "ARO:3000516": {
        "reference": "ARO:3000516",
        "snippet": (
            "EmrR is a negative regulator for the EmrAB-TolC multidrug efflux pump "
            "in E. coli. Mutations lead to EmrAB-TolC overexpression."
        ),
        "notes": "CARD definition for the emrR repressor determinant.",
    },
}

CMEABC_EVIDENCE = {
    "reference": "ARO:3000773",
    "snippet": (
        "CmeABC is a multidrug efflux pump in Campylobacter jejuni. Its "
        "overexpression led to enhanced resistance to ciprofloxacin, norfloxacin, "
        "cefotaxime, fusidic acid, and erythromycin. CmeA acts as the periplasmic "
        "fusion protein, CmeB is the inner membrane transporter, and CmeC is an "
        "outer membrane protein."
    ),
    "notes": "CARD definition for the CmeABC pump repressed by CmeR.",
}

MDTEF_TOLC_EVIDENCE = {
    "reference": "ARO:3000788",
    "snippet": (
        "MdtEF-TolC is a multidrug efflux complex in Gram-negative bacteria, "
        "including E. coli. MdtE is the membrane fusion protein, MdtF is the inner "
        "membrane transporter, while TolC is the outer membrane channel."
    ),
    "notes": "CARD definition for the MdtEF-TolC pump repressed by CRP.",
}

EMRAB_TOLC_EVIDENCE = {
    "reference": "ARO:3000344",
    "snippet": (
        "EmrAB-TolC is a multidrug efflux system found in E. coli. EmrB is the "
        "electrochemical-gradient powered transporter; EmrA is the linker; and "
        "TolC is the outer membrane channel. It confers resistance to nalidixic "
        "acid and thiolactomycin."
    ),
    "notes": "CARD definition for the EmrAB-TolC pump derepressed by emrR mutations.",
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
    "description": (
        "Resistance phenotype conferred by this determinant. Grounded to the "
        "nearest available superclass: ARO models determinants and mechanisms but "
        "has no term for the resistance phenotype itself."
    ),
}

PUMP_EFFLUX_EDGE = {
    "subject": "pump",
    "predicate": "enables (drug efflux)",
    "predicate_id": "RO:0002327",
    "object": "mech0",
}
PUMP_EFFLUX_FULL_EDGE = ("pump", "RO:0002327", "mech0")

OBSOLETE_EDGE = ("determinant", "RO:0002327", "repression")


@dataclass(frozen=True)
class EdgeUpdate:
    predicate: str
    predicate_id: str
    description: str
    evidence: tuple[dict[str, str], ...]


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    pump_node: dict[str, str]
    repression_node: dict[str, str]
    pump_evidence: dict[str, str]

    @property
    def target_evidence(self) -> dict[str, str]:
        return TARGET_EVIDENCE[self.identifier]

    @property
    def edge_updates(self) -> dict[tuple[str, str], EdgeUpdate]:
        target = self.target_evidence
        pump = self.pump_evidence
        return {
            ("determinant", "mech0"): EdgeUpdate(
                predicate="participates in (resistance mechanism)",
                predicate_id="RO:0000056",
                description=(
                    "CARD classifies this repressor under antibiotic efflux because "
                    f"it regulates {self.pump_node['label']} expression."
                ),
                evidence=(target, pump),
            ),
            ("mech0", "resistance"): EdgeUpdate(
                predicate="causally upstream of",
                predicate_id="RO:0002411",
                description=(
                    "The broad efflux mechanism represents elevated activity of the "
                    "regulated multidrug pump."
                ),
                evidence=(target, pump),
            ),
            ("determinant", "resistance"): EdgeUpdate(
                predicate="causally upstream of (confers resistance)",
                predicate_id="RO:0002411",
                description=(
                    "Loss of normal repressor activity is represented as raising "
                    f"{self.pump_node['label']} expression and increasing efflux."
                ),
                evidence=(target, pump),
            ),
            ("repression", "pump"): EdgeUpdate(
                predicate="negatively regulates (holds pump expression down)",
                predicate_id="RO:0002212",
                description=(
                    "Normal repressor-dependent transcriptional repression keeps "
                    f"{self.pump_node['label']} expression low."
                ),
                evidence=(target, GO_NEGATIVE_TRANSCRIPTION_EVIDENCE),
            ),
            ("determinant", "repression"): EdgeUpdate(
                predicate="negatively regulates (mutation lifts the repression)",
                predicate_id="RO:0002212",
                description=(
                    "Resistance-associated repressor loss is represented as loss of "
                    f"normal {self.pump_node['label']} repression."
                ),
                evidence=(target, GO_NEGATIVE_TRANSCRIPTION_EVIDENCE),
            ),
            ("pump", "mech0"): EdgeUpdate(
                predicate="enables (drug efflux)",
                predicate_id="RO:0002327",
                description=(
                    f"{self.pump_node['label']} is the multidrug pump whose "
                    "derepressed expression supplies antibiotic efflux."
                ),
                evidence=(target, pump),
            ),
        }

    @property
    def expected_edges(self) -> set[tuple[str, str]]:
        return set(self.edge_updates)


TARGETS = {
    "ARO:3000526": Target(
        identifier="ARO:3000526",
        filename="cmer-aro3000526.yaml",
        pump_node={
            "node_id": "pump",
            "label": "CmeABC multidrug efflux pump",
            "node_type": "PROTEIN",
            "grounding": "ARO:3000773",
            "description": (
                "Grounded to CARD's CmeABC multidrug efflux pump class, the pump "
                "repressed by CmeR."
            ),
        },
        repression_node={
            "node_id": "repression",
            "label": "negative regulation of CmeABC transcription",
            "node_type": "BIOLOGICAL_PROCESS",
            "grounding": "GO:0045892",
            "description": (
                "Grounded to the broad GO DNA-templated transcriptional repression "
                "process because CmeR represses CmeABC expression."
            ),
        },
        pump_evidence=CMEABC_EVIDENCE,
    ),
    "ARO:3000518": Target(
        identifier="ARO:3000518",
        filename="crp-aro3000518.yaml",
        pump_node={
            "node_id": "pump",
            "label": "MdtEF-TolC multidrug efflux complex",
            "node_type": "PROTEIN",
            "grounding": "ARO:3000788",
            "description": (
                "Grounded to CARD's MdtEF-TolC multidrug efflux complex, the pump "
                "repressed by CRP."
            ),
        },
        repression_node={
            "node_id": "repression",
            "label": "negative regulation of MdtEF transcription",
            "node_type": "BIOLOGICAL_PROCESS",
            "grounding": "GO:0045892",
            "description": (
                "Grounded to the broad GO DNA-templated transcriptional repression "
                "process because CRP represses MdtEF expression."
            ),
        },
        pump_evidence=MDTEF_TOLC_EVIDENCE,
    ),
    "ARO:3000516": Target(
        identifier="ARO:3000516",
        filename="emrr-aro3000516.yaml",
        pump_node={
            "node_id": "pump",
            "label": "EmrAB-TolC multidrug efflux pump",
            "node_type": "PROTEIN",
            "grounding": "ARO:3000344",
            "description": (
                "Grounded to CARD's EmrAB-TolC multidrug efflux system, the pump "
                "derepressed by emrR mutations."
            ),
        },
        repression_node={
            "node_id": "repression",
            "label": "negative regulation of EmrAB-TolC transcription",
            "node_type": "BIOLOGICAL_PROCESS",
            "grounding": "GO:0045892",
            "description": (
                "Grounded to the broad GO DNA-templated transcriptional repression "
                "process because EmrR represses EmrAB-TolC expression."
            ),
        },
        pump_evidence=EMRAB_TOLC_EVIDENCE,
    ),
}

EXPECTED_INPUT_FULL_EDGES = {
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("determinant", "RO:0002327", "repression"),
    ("repression", "RO:0002212", "pump"),
    ("determinant", "RO:0002212", "repression"),
    ("pump", "RO:0002327", "mech0"),
}


def _dump(obj: Any) -> str:
    return yaml.safe_dump(
        obj,
        sort_keys=False,
        allow_unicode=True,
        width=100,
        default_flow_style=False,
    )


def _edge_key(edge: dict[str, Any]) -> tuple[str, str]:
    return edge.get("subject", ""), edge.get("object", "")


def _full_edge_key(edge: dict[str, Any]) -> tuple[str, str, str]:
    return edge.get("subject", ""), edge.get("predicate_id", ""), edge.get("object", "")


def _ordered_edge(edge: dict[str, Any]) -> dict[str, Any]:
    ordered = {
        "subject": edge["subject"],
        "predicate": edge["predicate"],
        "predicate_id": edge["predicate_id"],
        "object": edge["object"],
        "description": edge["description"],
        "evidence": edge["evidence"],
    }
    for key, value in edge.items():
        if key not in ordered:
            ordered[key] = value
    return ordered


def _enrich_nodes(graph: dict[str, Any], target: Target) -> None:
    nodes = graph.get("nodes") or []
    by_id = {
        node.get("node_id"): node for node in nodes if isinstance(node, dict)
    }
    if "determinant" not in by_id:
        msg = f"{target.identifier}: missing node(s): determinant"
        raise ValueError(msg)

    graph["nodes"] = [
        copy.deepcopy(by_id["determinant"]),
        copy.deepcopy(MECHANISM_NODE),
        copy.deepcopy(target.pump_node),
        copy.deepcopy(target.repression_node),
        copy.deepcopy(RESISTANCE_NODE),
    ]


def _enrich_edges(graph: dict[str, Any], target: Target) -> None:
    edges = graph.setdefault("edges", [])
    if not any(_full_edge_key(edge) == PUMP_EFFLUX_FULL_EDGE for edge in edges):
        edges.append(copy.deepcopy(PUMP_EFFLUX_EDGE))

    seen_full: set[tuple[str, str, str]] = set()
    seen: set[tuple[str, str]] = set()
    enriched_edges: list[dict[str, Any]] = []
    for edge in edges:
        full_key = _full_edge_key(edge)
        if full_key in seen_full:
            msg = f"{target.identifier}: duplicate edge {full_key[0]} -> {full_key[2]}"
            raise ValueError(msg)
        seen_full.add(full_key)
        if full_key == OBSOLETE_EDGE:
            continue
        if full_key not in EXPECTED_INPUT_FULL_EDGES:
            msg = f"{target.identifier}: unexpected edge {full_key[0]} -> {full_key[2]}"
            raise ValueError(msg)

        key = _edge_key(edge)
        if key in seen:
            msg = f"{target.identifier}: duplicate edge {key[0]} -> {key[1]}"
            raise ValueError(msg)
        update = target.edge_updates[key]
        enriched_edges.append(
            _ordered_edge(
                {
                    "subject": key[0],
                    "predicate": update.predicate,
                    "predicate_id": update.predicate_id,
                    "object": key[1],
                    "description": update.description,
                    "evidence": [
                        copy.deepcopy(item)
                        for item in update.evidence
                    ],
                }
            )
        )
        seen.add(key)

    missing_edges = sorted(target.expected_edges - seen)
    if missing_edges:
        missing = ", ".join(f"{subject} -> {object_}" for subject, object_ in missing_edges)
        msg = f"{target.identifier}: missing edge(s): {missing}"
        raise ValueError(msg)

    graph["edges"] = enriched_edges


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != target.identifier:
        msg = f"expected {target.identifier}, found {record.get('identifier')}"
        raise ValueError(msg)

    out = copy.deepcopy(record)
    before = copy.deepcopy(out.get("causal_graphs"))
    graphs = out.get("causal_graphs") or []
    graph = next((item for item in graphs if item.get("graph_id") == "resistance"), None)
    if graph is None:
        msg = f"{target.identifier}: missing resistance causal graph"
        raise ValueError(msg)

    graph["description"] = (
        "Curated resistance-causation graph for loss of efflux-pump repression. The "
        "graph replaces the seeded archetype evidence and grounds the named efflux "
        "pump and transcriptional repression nodes."
    )
    _enrich_nodes(graph, target)
    _enrich_edges(graph, target)
    return out, out.get("causal_graphs") != before


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: record is not a mapping")
    identifier = record.get("identifier")
    target = TARGETS.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not a CmeR/CRP/EmrR repressor target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
    normalize_aliases = "&id" in text or "*id" in text
    if not changed and not normalize_aliases:
        return text, False

    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    if HISTORY_CURATOR not in out:
        out = append_to_section(out, "curation_history", _dump({"curation_history": [HISTORY_EVENT]}))
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
    parser.add_argument(
        "--path",
        type=Path,
        default=ARO_DIR,
        help="ARO directory or one CmeR/CRP/EmrR repressor target YAML file",
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
