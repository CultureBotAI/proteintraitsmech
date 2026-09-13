#!/usr/bin/env python3
"""Ground and complete MarR/RamR derepression-to-AcrAB ARO graphs.

MarR and RamR mutations do not directly derepress the AcrAB-TolC pump in their
CARD definitions.  MarR represses marA and RamR represses ramA; MarA/RamA then
activate AcrAB expression.  This updater replaces the stale direct-pump scaffold
with that repressor-to-activator path, grounds the activator/pump/transcription
nodes, removes the obsolete wild-type repressor role edge, and replaces stale
AcrR evidence with exact target/activator/pump evidence.

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
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": (
        "Replaced stale direct-pump MarR/RamR scaffolds with MarA/RamA-mediated "
        "AcrAB-TolC activation and exact target/activator/pump evidence"
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

GO_POSITIVE_TRANSCRIPTION_EVIDENCE = {
    "reference": "GO:0045893",
    "snippet": (
        "Any process that activates or increases the frequency, rate or extent of "
        "cellular DNA-templated transcription."
    ),
    "notes": "GO definition for the broad transcriptional activation process.",
}

ACRAB_TOLC_EVIDENCE = {
    "reference": "ARO:3000384",
    "snippet": (
        "AcrAB-TolC is a tripartite RND efflux system that confers resistance to "
        "tetracycline, chloramphenicol, ampicillin, nalidixic acid, and rifampin "
        "in Gram-negative bacteria. The system spans the cell membrane (AcrB) and "
        "the outer-membrane (TolC), and is linked together in the periplasm by AcrA."
    ),
    "notes": "CARD definition for the AcrAB-TolC pump activated by MarA/RamA.",
}

MARA_EVIDENCE = {
    "reference": "ARO:3000263",
    "snippet": (
        "In the presence of antibiotic stress, E. coli overexpresses the global "
        "activator protein MarA, which besides inducing MDR efflux pump AcrAB, "
        "also down- regulates synthesis of the porin OmpF."
    ),
    "notes": "CARD definition for the MarA AcrAB activator.",
}

RAMA_EVIDENCE = {
    "reference": "ARO:3000823",
    "snippet": (
        "RamA (resistance antibiotic multiple) is a positive regulator of "
        "AcrAB-TolC and leads to high level multidrug resistance in Klebsiella "
        "pneumoniae, Salmonella enterica, and Enterobacter aerugenes, increasing "
        "the expression of both the mar operon as well as AcrAB. RamA also "
        "decreases OmpF expression."
    ),
    "notes": "CARD definition for the RamA AcrAB-TolC activator.",
}

MARR_EVIDENCE = {
    "reference": "ARO:3000718",
    "snippet": (
        "MarR is a repressor of the mar operon marRAB, thus regulating the "
        "expression of marA, the activator of multidrug efflux pump AcrAB."
    ),
    "notes": "CARD definition for the marR repressor determinant.",
}

RAMR_EVIDENCE = {
    "snippet": (
        "RamR is a repressor that regulates RamA expression. Mutations lead to "
        "the upregulation of AcrAB, which is positively regulated by RamA."
    ),
    "notes": "CARD definition for this ramR repressor determinant.",
}

MUTATION_EVIDENCE = {
    "reference": "ARO:3000212",
    "snippet": (
        "Point mutations in the DNA may lead to an altered gene product that may "
        "result in antibiotic resistance. Examples included modified antibiotic "
        "targets with lower binding affinities and the deactivation of repressors "
        "that result in increased expression of genes that inactivate or pump out "
        "antibiotics."
    ),
    "notes": "CARD definition for the broad mutation-conferring resistance mechanism.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "antibiotic efflux",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:0010000",
}

MUTATION_NODE = {
    "node_id": "mech1",
    "label": "mutation conferring antibiotic resistance",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3000212",
}

PUMP_NODE = {
    "node_id": "pump",
    "label": "AcrAB-TolC",
    "node_type": "PROTEIN",
    "grounding": "ARO:3000384",
    "description": "Grounded to CARD's AcrAB-TolC efflux pump.",
}

ACTIVATION_NODE = {
    "node_id": "activation",
    "label": "positive regulation of AcrAB-TolC expression",
    "node_type": "BIOLOGICAL_PROCESS",
    "grounding": "GO:0045893",
    "description": (
        "Grounded to the broad GO DNA-templated transcriptional activation process "
        "because MarA and RamA activate AcrAB expression."
    ),
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
ACTIVATOR_ACTIVATION_EDGE = {
    "subject": "activator",
    "predicate": "enables (activates AcrAB expression)",
    "predicate_id": "RO:0002327",
    "object": "activation",
}
ACTIVATION_PUMP_EDGE = {
    "subject": "activation",
    "predicate": "positively regulates (raises AcrAB expression)",
    "predicate_id": "RO:0002213",
    "object": "pump",
}

OBSOLETE_EDGE = ("determinant", "RO:0002327", "repression")
OLD_REPRESSION_PUMP_EDGE = ("repression", "RO:0002212", "pump")
REPRESSION_ACTIVATOR_EDGE = ("repression", "RO:0002212", "activator")

EXPECTED_INPUT_FULL_EDGES = {
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0000056", "mech1"),
    ("mech1", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("determinant", "RO:0002327", "repression"),
    ("determinant", "RO:0002212", "repression"),
    ("repression", "RO:0002212", "pump"),
    ("repression", "RO:0002212", "activator"),
    ("activator", "RO:0002327", "activation"),
    ("activation", "RO:0002213", "pump"),
    ("pump", "RO:0002327", "mech0"),
}


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
    repressor_name: str
    activator_name: str
    activator_node: dict[str, str]
    repression_node: dict[str, str]
    target_evidence: dict[str, str]
    activator_evidence: dict[str, str]

    @property
    def edge_updates(self) -> dict[tuple[str, str], EdgeUpdate]:
        return {
            ("determinant", "mech0"): EdgeUpdate(
                predicate="participates in (resistance mechanism)",
                predicate_id="RO:0000056",
                description=(
                    "CARD classifies this derepressed regulator under antibiotic "
                    f"efflux because {self.activator_name} activates AcrAB expression."
                ),
                evidence=(
                    self.target_evidence,
                    self.activator_evidence,
                    ACRAB_TOLC_EVIDENCE,
                ),
            ),
            ("mech0", "resistance"): EdgeUpdate(
                predicate="causally upstream of",
                predicate_id="RO:0002411",
                description=(
                    "The broad efflux mechanism represents elevated AcrAB-TolC "
                    "activity lowering intracellular antibiotic exposure."
                ),
                evidence=(self.target_evidence, ACRAB_TOLC_EVIDENCE),
            ),
            ("determinant", "mech1"): EdgeUpdate(
                predicate="participates in (mutation mechanism)",
                predicate_id="RO:0000056",
                description=(
                    "CARD also classifies this determinant under mutation conferring "
                    "antibiotic resistance."
                ),
                evidence=(self.target_evidence, MUTATION_EVIDENCE),
            ),
            ("mech1", "resistance"): EdgeUpdate(
                predicate="causally upstream of",
                predicate_id="RO:0002411",
                description=(
                    "The inherited mutation mechanism links loss-of-repressor "
                    "variants to the resistance phenotype."
                ),
                evidence=(self.target_evidence, MUTATION_EVIDENCE),
            ),
            ("determinant", "resistance"): EdgeUpdate(
                predicate="causally upstream of (confers resistance)",
                predicate_id="RO:0002411",
                description=(
                    f"{self.repressor_name} loss derepresses {self.activator_name}, "
                    "raising AcrAB-TolC expression and driving efflux-mediated "
                    "resistance."
                ),
                evidence=(
                    self.target_evidence,
                    self.activator_evidence,
                    ACRAB_TOLC_EVIDENCE,
                ),
            ),
            ("determinant", "repression"): EdgeUpdate(
                predicate="negatively regulates (loss lifts the repression)",
                predicate_id="RO:0002212",
                description=(
                    f"Resistance-conferring {self.repressor_name} loss is modeled "
                    f"as loss of normal {self.activator_name} repression."
                ),
                evidence=(self.target_evidence, GO_NEGATIVE_TRANSCRIPTION_EVIDENCE),
            ),
            ("repression", "activator"): EdgeUpdate(
                predicate="negatively regulates (holds activator expression down)",
                predicate_id="RO:0002212",
                description=(
                    f"Normal {self.repressor_name}-dependent transcriptional "
                    f"repression keeps {self.activator_name} expression low."
                ),
                evidence=(self.target_evidence, GO_NEGATIVE_TRANSCRIPTION_EVIDENCE),
            ),
            ("activator", "activation"): EdgeUpdate(
                predicate="enables (activates AcrAB expression)",
                predicate_id="RO:0002327",
                description=(
                    f"{self.activator_name} participates in positive regulation of "
                    "AcrAB-TolC expression."
                ),
                evidence=(
                    self.activator_evidence,
                    GO_POSITIVE_TRANSCRIPTION_EVIDENCE,
                ),
            ),
            ("activation", "pump"): EdgeUpdate(
                predicate="positively regulates (raises AcrAB expression)",
                predicate_id="RO:0002213",
                description=(
                    f"{self.activator_name}-mediated activation raises AcrAB-TolC "
                    "expression."
                ),
                evidence=(
                    self.activator_evidence,
                    GO_POSITIVE_TRANSCRIPTION_EVIDENCE,
                    ACRAB_TOLC_EVIDENCE,
                ),
            ),
            ("pump", "mech0"): EdgeUpdate(
                predicate="enables (drug efflux)",
                predicate_id="RO:0002327",
                description=(
                    "AcrAB-TolC is the RND efflux system whose derepressed "
                    f"{self.activator_name} route supplies antibiotic efflux."
                ),
                evidence=(
                    self.target_evidence,
                    self.activator_evidence,
                    ACRAB_TOLC_EVIDENCE,
                ),
            ),
        }

    @property
    def expected_edges(self) -> set[tuple[str, str]]:
        return set(self.edge_updates)


def _evidence(reference: str, base: dict[str, str]) -> dict[str, str]:
    return {
        **base,
        "reference": reference,
    }


MARA_NODE = {
    "node_id": "activator",
    "label": "MarA",
    "node_type": "PROTEIN",
    "grounding": "ARO:3000263",
    "description": (
        "Grounded to CARD's MarA global activator, the marRAB product that activates "
        "AcrAB expression."
    ),
}

MARA_REPRESSION_NODE = {
    "node_id": "repression",
    "label": "negative regulation of marA transcription",
    "node_type": "BIOLOGICAL_PROCESS",
    "grounding": "GO:0045892",
    "description": (
        "Grounded to the broad GO DNA-templated transcriptional repression process "
        "because MarR represses the marRAB operon."
    ),
}

RAMA_NODE = {
    "node_id": "activator",
    "label": "RamA",
    "node_type": "PROTEIN",
    "grounding": "ARO:3000823",
    "description": (
        "Grounded to CARD's RamA activator, the AcrAB positive regulator repressed "
        "by RamR."
    ),
}

RAMA_REPRESSION_NODE = {
    "node_id": "repression",
    "label": "negative regulation of RamA transcription",
    "node_type": "BIOLOGICAL_PROCESS",
    "grounding": "GO:0045892",
    "description": (
        "Grounded to the broad GO DNA-templated transcriptional repression process "
        "because RamR represses RamA expression."
    ),
}

TARGETS = {
    "ARO:3000718": Target(
        identifier="ARO:3000718",
        filename="marr-aro3000718.yaml",
        repressor_name="MarR",
        activator_name="MarA",
        activator_node=MARA_NODE,
        repression_node=MARA_REPRESSION_NODE,
        target_evidence=MARR_EVIDENCE,
        activator_evidence=MARA_EVIDENCE,
    ),
    "ARO:3003378": Target(
        identifier="ARO:3003378",
        filename=(
            "escherichia-coli-acrab-tolc-with-marr-mutations-conferring-"
            "resistance-to-ciprofl-aro3003378.yaml"
        ),
        repressor_name="MarR",
        activator_name="MarA",
        activator_node=MARA_NODE,
        repression_node=MARA_REPRESSION_NODE,
        target_evidence=_evidence("ARO:3003378", MARR_EVIDENCE),
        activator_evidence=MARA_EVIDENCE,
    ),
    "ARO:3000824": Target(
        identifier="ARO:3000824",
        filename="ramr-aro3000824.yaml",
        repressor_name="RamR",
        activator_name="RamA",
        activator_node=RAMA_NODE,
        repression_node=RAMA_REPRESSION_NODE,
        target_evidence=_evidence("ARO:3000824", RAMR_EVIDENCE),
        activator_evidence=RAMA_EVIDENCE,
    ),
    "ARO:3003379": Target(
        identifier="ARO:3003379",
        filename="salmonella-enterica-ramr-mutants-aro3003379.yaml",
        repressor_name="RamR",
        activator_name="RamA",
        activator_node=RAMA_NODE,
        repression_node=RAMA_REPRESSION_NODE,
        target_evidence=_evidence("ARO:3003379", RAMR_EVIDENCE),
        activator_evidence=RAMA_EVIDENCE,
    ),
    "ARO:3003380": Target(
        identifier="ARO:3003380",
        filename="klebsiella-pneumoniae-ramr-mutants-aro3003380.yaml",
        repressor_name="RamR",
        activator_name="RamA",
        activator_node=RAMA_NODE,
        repression_node=RAMA_REPRESSION_NODE,
        target_evidence=_evidence("ARO:3003380", RAMR_EVIDENCE),
        activator_evidence=RAMA_EVIDENCE,
    ),
}

ADDED_EDGES = (
    ACTIVATOR_ACTIVATION_EDGE,
    ACTIVATION_PUMP_EDGE,
    PUMP_EFFLUX_EDGE,
)


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


def _normalize_edge_key(edge: dict[str, Any]) -> tuple[str, str]:
    full_key = _full_edge_key(edge)
    if full_key == OLD_REPRESSION_PUMP_EDGE:
        return REPRESSION_ACTIVATOR_EDGE[0], REPRESSION_ACTIVATOR_EDGE[2]
    return _edge_key(edge)


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
    by_id = {node.get("node_id"): node for node in nodes if isinstance(node, dict)}
    if "determinant" not in by_id:
        msg = f"{target.identifier}: missing node(s): determinant"
        raise ValueError(msg)

    graph["nodes"] = [
        copy.deepcopy(by_id["determinant"]),
        copy.deepcopy(MECHANISM_NODE),
        copy.deepcopy(MUTATION_NODE),
        copy.deepcopy(target.activator_node),
        copy.deepcopy(target.repression_node),
        copy.deepcopy(ACTIVATION_NODE),
        copy.deepcopy(PUMP_NODE),
        copy.deepcopy(RESISTANCE_NODE),
    ]


def _enrich_edges(graph: dict[str, Any], target: Target) -> None:
    edges = graph.setdefault("edges", [])
    existing = {_full_edge_key(edge) for edge in edges}
    for edge in ADDED_EDGES:
        if _full_edge_key(edge) not in existing:
            edges.append(copy.deepcopy(edge))

    seen: set[tuple[str, str]] = set()
    enriched_edges: list[dict[str, Any]] = []
    for edge in edges:
        full_key = _full_edge_key(edge)
        if full_key == OBSOLETE_EDGE:
            continue
        if full_key not in EXPECTED_INPUT_FULL_EDGES:
            msg = f"{target.identifier}: unexpected edge {full_key[0]} -> {full_key[2]}"
            raise ValueError(msg)

        key = _normalize_edge_key(edge)
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
                    "evidence": [copy.deepcopy(item) for item in update.evidence],
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
        "Curated resistance-causation graph for AcrAB derepression through an "
        "intermediate activator. The graph replaces the stale direct-pump scaffold "
        "with repressor loss, MarA/RamA derepression, AcrAB activation, and "
        "AcrAB-TolC drug efflux."
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
        raise ValueError(f"{path}: not a MarR/RamR repressor target: {identifier}")
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
        help="ARO directory or one MarR/RamR repressor target YAML file",
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
