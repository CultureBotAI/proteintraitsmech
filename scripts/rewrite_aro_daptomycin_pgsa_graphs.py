#!/usr/bin/env python3
"""Ground and complete daptomycin-resistant pgsA ARO graphs.

The daptomycin pgsA descendants share the same phosphatidylglycerophosphate
synthase and phospholipid-biosynthesis graph as the already-enriched
antibiotic-resistant pgsA parent, with one additional peptide-antibiotic edge.
This updater grounds those two shared nodes and adds exact pgsA parent,
daptomycin parent, mutation-mechanism, and child evidence to every edge.

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
        "Grounded daptomycin-resistant pgsA descendant graphs to GO PGP "
        "synthase and phospholipid-biosynthesis terms and added exact pgsA, "
        "daptomycin, mutation-mechanism, and ontology evidence"
    ),
    "llm_assisted": True,
}

PGSA_PARENT_IDENTIFIER = "ARO:3003420"
DAPTOMYCIN_PGSA_IDENTIFIER = "ARO:3003080"

PGSA_PARENT_EVIDENCE = {
    "reference": PGSA_PARENT_IDENTIFIER,
    "snippet": (
        "pgsA or phosphatidylglycerophosphate synthetase is an integral membrane "
        "protein involved in phospholipid biosynthesis. It is a "
        "CDP-diacylglycerol-glycerol-3-phosphate 3-phosphatidyltransferase."
    ),
    "notes": "CARD definition for the antibiotic-resistant pgsA parent term.",
}

DAPTOMYCIN_PGSA_EVIDENCE = {
    "reference": DAPTOMYCIN_PGSA_IDENTIFIER,
    "snippet": (
        "pgsA or phosphatidylglycerophosphate synthetase is an integral membrane "
        "protein involved in phospholipid biosynthesis. It is a "
        "CDP-diacylglycerol-glycerol-3-phosphate 3-phosphatidyltransferase. "
        "Laboratory experiments have detected mutations conferring daptomycin "
        "resistance in Entercoccus."
    ),
    "notes": "CARD definition for the daptomycin-resistant pgsA parent term.",
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

PGP_SYNTHASE_EVIDENCE = {
    "reference": "GO:0008444",
    "snippet": (
        "Catalysis of the reaction: sn-glycerol 3-phosphate + CDP-diacylglycerol "
        "= 3-(3-sn-phosphatidyl)-sn-glycerol 1-phosphate + CMP + H+."
    ),
    "notes": "GO reaction definition for phosphatidylglycerophosphate synthase activity.",
}

PHOSPHOLIPID_BIOSYNTHESIS_EVIDENCE = {
    "reference": "GO:0008654",
    "snippet": (
        "The chemical reactions and pathways resulting in the formation of a "
        "phospholipid, a lipid containing phosphoric acid as a mono- or diester."
    ),
    "notes": "GO definition for the broad phospholipid biosynthetic process.",
}

PEPTIDE_ANTIBIOTIC_EVIDENCE = {
    "reference": "ARO:3000053",
    "snippet": "peptide antibiotic",
    "notes": "ARO drug-class term inherited by daptomycin-resistant pgsA records.",
}

SHARED_NODE_UPDATES = {
    "pgp_synthase": {
        "node_id": "pgp_synthase",
        "label": "CDP-diacylglycerol-glycerol-3-phosphate 3-phosphatidyltransferase activity",
        "node_type": "MOLECULAR_FUNCTION",
        "grounding": "GO:0008444",
        "description": (
            "Grounded to the GO molecular-function class whose synonyms include "
            "phosphatidylglycerophosphate synthase activity."
        ),
    },
    "phospholipid": {
        "node_id": "phospholipid",
        "label": "phospholipid biosynthetic process",
        "node_type": "BIOLOGICAL_PROCESS",
        "grounding": "GO:0008654",
        "description": (
            "Grounded to the broad GO pathway class for formation of phospholipids; "
            "the pgsA evidence narrows this local node to the "
            "phosphatidylglycerol pathway."
        ),
    },
}

EXPECTED_EDGES = {
    ("determinant", "mech0"),
    ("mech0", "resistance"),
    ("determinant", "resistance"),
    ("determinant", "drug0"),
    ("determinant", "pgp_synthase"),
    ("pgp_synthase", "phospholipid"),
}
EDGE_ORDER = (
    ("determinant", "mech0"),
    ("mech0", "resistance"),
    ("determinant", "resistance"),
    ("determinant", "drug0"),
    ("determinant", "pgp_synthase"),
    ("pgp_synthase", "phospholipid"),
)


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
    snippet: str
    notes: str

    @property
    def target_evidence(self) -> dict[str, str]:
        return {
            "reference": self.identifier,
            "snippet": self.snippet,
            "notes": self.notes,
        }

    @property
    def pgsA_evidence(self) -> tuple[dict[str, str], ...]:
        if self.identifier == DAPTOMYCIN_PGSA_IDENTIFIER:
            return (self.target_evidence, PGSA_PARENT_EVIDENCE)
        return (self.target_evidence, DAPTOMYCIN_PGSA_EVIDENCE, PGSA_PARENT_EVIDENCE)

    @property
    def edge_updates(self) -> dict[tuple[str, str], EdgeUpdate]:
        pgsA = self.pgsA_evidence
        mutation = (self.target_evidence, MUTATION_EVIDENCE)
        return {
            ("determinant", "mech0"): EdgeUpdate(
                predicate="participates in (resistance mechanism)",
                predicate_id="RO:0000056",
                description=(
                    "CARD classifies daptomycin-resistant pgsA variants under "
                    "mutation conferring antibiotic resistance."
                ),
                evidence=mutation,
            ),
            ("mech0", "resistance"): EdgeUpdate(
                predicate="causally upstream of",
                predicate_id="RO:0002411",
                description=(
                    "The broad mutation mechanism covers pgsA variants associated "
                    "with daptomycin resistance."
                ),
                evidence=mutation,
            ),
            ("determinant", "resistance"): EdgeUpdate(
                predicate="causally upstream of (confers resistance)",
                predicate_id="RO:0002411",
                description=(
                    "Mutations in pgsA alter a phospholipid-biosynthesis enzyme "
                    "and confer daptomycin resistance."
                ),
                evidence=(*pgsA, MUTATION_EVIDENCE),
            ),
            ("determinant", "drug0"): EdgeUpdate(
                predicate="confers resistance to",
                predicate_id="ARO:2000001",
                description=(
                    "CARD maps these pgsA variants to daptomycin resistance in the "
                    "peptide-antibiotic class."
                ),
                evidence=(
                    self.target_evidence,
                    DAPTOMYCIN_PGSA_EVIDENCE,
                    PEPTIDE_ANTIBIOTIC_EVIDENCE,
                ),
            ),
            ("determinant", "pgp_synthase"): EdgeUpdate(
                predicate="enables",
                predicate_id="RO:0002327",
                description=(
                    "pgsA encodes phosphatidylglycerophosphate synthase, a "
                    "CDP-diacylglycerol-glycerol-3-phosphate "
                    "3-phosphatidyltransferase."
                ),
                evidence=(*pgsA, PGP_SYNTHASE_EVIDENCE),
            ),
            ("pgp_synthase", "phospholipid"): EdgeUpdate(
                predicate="part of (phospholipid biosynthesis)",
                predicate_id="BFO:0000050",
                description=(
                    "Phosphatidylglycerophosphate synthase activity is part of the "
                    "phospholipid-biosynthesis pathway."
                ),
                evidence=(
                    PGSA_PARENT_EVIDENCE,
                    PGP_SYNTHASE_EVIDENCE,
                    PHOSPHOLIPID_BIOSYNTHESIS_EVIDENCE,
                ),
            ),
        }


TARGETS = {
    "ARO:3003080": Target(
        identifier="ARO:3003080",
        filename="daptomycin-resistant-pgsa-aro3003080.yaml",
        snippet=DAPTOMYCIN_PGSA_EVIDENCE["snippet"],
        notes=DAPTOMYCIN_PGSA_EVIDENCE["notes"],
    ),
    "ARO:3003788": Target(
        identifier="ARO:3003788",
        filename="bacillus-subtilis-pgsa-with-mutation-conferring-resistance-to-daptomycin-aro3003788.yaml",
        snippet=(
            "Point mutations that occur within the Bacillus subtilis pgsA gene "
            "resulting in resistance to daptomycin."
        ),
        notes="CARD definition for the Bacillus subtilis pgsA mutant term.",
    ),
    "ARO:3003323": Target(
        identifier="ARO:3003323",
        filename="staphylococcus-aureus-pgsa-mutations-conferring-resistance-to-daptomycin-aro3003323.yaml",
        snippet=(
            "Point mutations that occur within Staphylococcus aureus pgsA gene "
            "resulting in resistance to daptomycin."
        ),
        notes="CARD definition for the Staphylococcus aureus pgsA mutant term.",
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


def _edge_key(edge: dict[str, Any]) -> tuple[str, str]:
    return edge.get("subject", ""), edge.get("object", "")


def _unique_evidence(evidence: tuple[dict[str, str], ...]) -> list[dict[str, str]]:
    unique: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for item in evidence:
        key = (
            item["reference"],
            item["snippet"],
            item.get("notes", ""),
        )
        if key in seen:
            continue
        seen.add(key)
        unique.append(copy.deepcopy(item))
    return unique


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
    found: set[str] = set()
    for index, node in enumerate(nodes):
        node_id = node.get("node_id")
        if node_id not in SHARED_NODE_UPDATES:
            continue
        nodes[index] = copy.deepcopy(SHARED_NODE_UPDATES[node_id])
        found.add(node_id)

    missing = sorted(set(SHARED_NODE_UPDATES) - found)
    if missing:
        missing_ids = ", ".join(missing)
        msg = f"{target.identifier}: missing node(s): {missing_ids}"
        raise ValueError(msg)


def _canonical_edges(target: Target) -> list[dict[str, Any]]:
    by_key = target.edge_updates
    return [
        _ordered_edge(
            {
                "subject": subject,
                "predicate": by_key[(subject, object_)].predicate,
                "predicate_id": by_key[(subject, object_)].predicate_id,
                "object": object_,
                "description": by_key[(subject, object_)].description,
                "evidence": _unique_evidence(by_key[(subject, object_)].evidence),
            }
        )
        for subject, object_ in EDGE_ORDER
    ]


def _validate_edges(graph: dict[str, Any], target: Target) -> None:
    seen: set[tuple[str, str]] = set()
    for edge in graph.get("edges") or []:
        key = _edge_key(edge)
        if key in seen:
            msg = f"{target.identifier}: duplicate edge {key[0]} -> {key[1]}"
            raise ValueError(msg)
        if key not in EXPECTED_EDGES:
            msg = f"{target.identifier}: unexpected edge {key[0]} -> {key[1]}"
            raise ValueError(msg)
        seen.add(key)

    missing_edges = sorted(EXPECTED_EDGES - seen)
    if missing_edges:
        missing = ", ".join(f"{subject} -> {object_}" for subject, object_ in missing_edges)
        msg = f"{target.identifier}: missing edge(s): {missing}"
        raise ValueError(msg)


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

    _enrich_nodes(graph, target)
    _validate_edges(graph, target)
    graph["description"] = (
        "Curated resistance-causation graph for daptomycin-resistant pgsA. The "
        "graph grounds phosphatidylglycerophosphate synthase and the broad "
        "phospholipid-biosynthesis process while retaining the peptide-antibiotic "
        "resistance-class edge."
    )
    graph["edges"] = _canonical_edges(target)
    return out, out.get("causal_graphs") != before


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: record is not a mapping")
    identifier = record.get("identifier")
    target = TARGETS.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not a daptomycin pgsA target: {identifier}")
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
        help="ARO directory or one of the three target YAML files",
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
