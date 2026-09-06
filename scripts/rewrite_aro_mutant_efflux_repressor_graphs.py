#!/usr/bin/env python3
"""Ground and complete direct mutant efflux-repressor ARO graphs.

The records handled here are repressor mutants that derepress a concrete efflux
pump or operon.  This updater grounds the named pump, grounds broad
transcriptional repression to GO, removes the obsolete wild-type
determinant-to-repression role edge from the mutant causal path, adds the
missing pump-to-efflux edge, and replaces stale AcrR evidence with exact
target/pump/mutation evidence.

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
        "Replaced stale archetype evidence on direct mutant repressor graphs, "
        "grounded their named efflux pumps and transcriptional-repression nodes, "
        "removed the obsolete wild-type repressor edge, and linked pump "
        "derepression to antibiotic efflux"
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
    repressor_label: str
    pump_label: str
    pump_grounding: str
    repressed_process: str
    target_snippet: str
    target_notes: str
    pump_snippet: str
    pump_notes: str

    @property
    def target_evidence(self) -> dict[str, str]:
        return {
            "reference": self.identifier,
            "snippet": self.target_snippet,
            "notes": self.target_notes,
        }

    @property
    def pump_evidence(self) -> dict[str, str]:
        return {
            "reference": self.pump_grounding,
            "snippet": self.pump_snippet,
            "notes": self.pump_notes,
        }

    @property
    def pump_node(self) -> dict[str, str]:
        return {
            "node_id": "pump",
            "label": self.pump_label,
            "node_type": "PROTEIN",
            "grounding": self.pump_grounding,
            "description": (
                f"Grounded to CARD's {self.pump_label}, the pump derepressed by "
                f"{self.repressor_label} mutations."
            ),
        }

    @property
    def repression_node(self) -> dict[str, str]:
        return {
            "node_id": "repression",
            "label": f"negative regulation of {self.repressed_process}",
            "node_type": "BIOLOGICAL_PROCESS",
            "grounding": "GO:0045892",
            "description": (
                "Grounded to the broad GO DNA-templated transcriptional repression "
                f"process because {self.repressor_label} represses "
                f"{self.repressed_process}."
            ),
        }

    @property
    def edge_updates(self) -> dict[tuple[str, str], EdgeUpdate]:
        target = self.target_evidence
        pump = self.pump_evidence
        return {
            ("determinant", "mech0"): EdgeUpdate(
                predicate="participates in (resistance mechanism)",
                predicate_id="RO:0000056",
                description=(
                    "CARD classifies this repressor mutant under antibiotic efflux "
                    f"because {self.repressor_label} mutations derepress "
                    f"{self.pump_label}."
                ),
                evidence=(target, pump),
            ),
            ("mech0", "resistance"): EdgeUpdate(
                predicate="causally upstream of",
                predicate_id="RO:0002411",
                description=(
                    "The broad efflux mechanism represents elevated activity of the "
                    "derepressed efflux system."
                ),
                evidence=(target, pump),
            ),
            ("determinant", "mech1"): EdgeUpdate(
                predicate="participates in (mutation mechanism)",
                predicate_id="RO:0000056",
                description=(
                    "CARD also classifies this determinant under mutation "
                    "conferring antibiotic resistance."
                ),
                evidence=(target, MUTATION_EVIDENCE),
            ),
            ("mech1", "resistance"): EdgeUpdate(
                predicate="causally upstream of",
                predicate_id="RO:0002411",
                description=(
                    "The inherited mutation mechanism links loss-of-repressor "
                    "variants to the resistance phenotype."
                ),
                evidence=(target, MUTATION_EVIDENCE),
            ),
            ("determinant", "resistance"): EdgeUpdate(
                predicate="causally upstream of (confers resistance)",
                predicate_id="RO:0002411",
                description=(
                    f"{self.repressor_label} mutations lift normal repression of "
                    f"{self.pump_label}, increasing antibiotic efflux."
                ),
                evidence=(target, pump),
            ),
            ("repression", "pump"): EdgeUpdate(
                predicate="negatively regulates (holds pump expression down)",
                predicate_id="RO:0002212",
                description=(
                    "Normal repressor-dependent transcriptional repression keeps "
                    f"{self.pump_label} expression low."
                ),
                evidence=(target, GO_NEGATIVE_TRANSCRIPTION_EVIDENCE),
            ),
            ("determinant", "repression"): EdgeUpdate(
                predicate="negatively regulates (mutation lifts the repression)",
                predicate_id="RO:0002212",
                description=(
                    f"{self.repressor_label} mutations are represented as loss of "
                    f"normal {self.pump_label} repression."
                ),
                evidence=(target, GO_NEGATIVE_TRANSCRIPTION_EVIDENCE),
            ),
            ("pump", "mech0"): EdgeUpdate(
                predicate="enables (drug efflux)",
                predicate_id="RO:0002327",
                description=(
                    f"{self.pump_label} is the efflux system whose derepressed "
                    "expression supplies antibiotic efflux."
                ),
                evidence=(target, pump),
            ),
        }

    @property
    def expected_edges(self) -> set[tuple[str, str]]:
        return set(self.edge_updates)


TARGETS = {
    "ARO:3003028": Target(
        identifier="ARO:3003028",
        filename="lmra-aro3003028.yaml",
        repressor_label="lmrA",
        pump_label="lmrAB operon",
        pump_grounding="ARO:3003027",
        repressed_process="lmrAB transcription",
        target_snippet=(
            "lmrA is the repressor to the lmrAB operon in Bacillus subtilis. lmrA "
            "mutations result in lincomycin resistance."
        ),
        target_notes="CARD definition for the lmrA repressor mutant determinant.",
        pump_snippet=(
            "lmrAB operon is involved in lincosamide resistance in Bacillus subtilis."
        ),
        pump_notes="CARD definition for the lmrAB efflux operon repressed by lmrA.",
    ),
    "ARO:3000506": Target(
        identifier="ARO:3000506",
        filename="mexr-aro3000506.yaml",
        repressor_label="MexR",
        pump_label="MexAB-OprM",
        pump_grounding="ARO:3000386",
        repressed_process="MexAB-OprM transcription",
        target_snippet=(
            "MexR is the repressor of the MexRAB-OprM operon. Mutant forms of "
            "mexR result in up-regulation of efflux pump system MexAB-OprM."
        ),
        target_notes="CARD definition for the MexR repressor mutant determinant.",
        pump_snippet=(
            "MexAB-OprM is a multidrug efflux protein expressed in the Gram-negative "
            "Pseudomonas aeruginosa. MexA is the membrane fusion protein; MexB is "
            "the inner membrane transporter; and OprM is the outer membrane channel. "
            "MexAB-OprM is associated with resistance to fluoroquinolones, "
            "chloramphenicol, erythromycin, azithromycin, novobiocin, and certain "
            "β-lactams and lastly over-expression is linked to colistin resistance."
        ),
        pump_notes="CARD definition for the MexAB-OprM efflux pump derepressed by MexR.",
    ),
    "ARO:3003479": Target(
        identifier="ARO:3003479",
        filename="tetr-aro3003479.yaml",
        repressor_label="TetR",
        pump_label="tet(A)",
        pump_grounding="ARO:3000165",
        repressed_process="tetA transcription",
        target_snippet=(
            "TetR is the repressor of the tetracycline resistance element; its "
            "N-terminal region forms a helix-turn-helix structure and binds DNA. "
            "Binding of tetracycline to TetR reduces the repressor affinity for "
            "the tetracycline resistance gene (tetA) promoter operator sites. "
            "Mutations arise within tetR results in lower affinity for tetracyclin."
        ),
        target_notes="CARD definition for the tetR repressor mutant determinant.",
        pump_snippet=(
            "TetA is a tetracycline efflux pump found in many species of "
            "Gram-negative bacteria."
        ),
        pump_notes="CARD definition for the tet(A) efflux pump repressed by TetR.",
    ),
}

EXPECTED_INPUT_FULL_EDGES = {
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0000056", "mech1"),
    ("mech1", "RO:0002411", "resistance"),
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
    by_id = {node.get("node_id"): node for node in nodes if isinstance(node, dict)}
    if "determinant" not in by_id:
        msg = f"{target.identifier}: missing node(s): determinant"
        raise ValueError(msg)

    graph["nodes"] = [
        copy.deepcopy(by_id["determinant"]),
        copy.deepcopy(MECHANISM_NODE),
        copy.deepcopy(MUTATION_NODE),
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
        "Curated resistance-causation graph for mutant efflux-pump derepression. "
        "The graph replaces stale archetype evidence, removes the wild-type role "
        "edge from the mutant path, and grounds the named efflux pump and "
        "transcriptional repression nodes."
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
        raise ValueError(f"{path}: not a direct mutant repressor target: {identifier}")
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
        help="ARO directory or one direct mutant repressor target YAML file",
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
