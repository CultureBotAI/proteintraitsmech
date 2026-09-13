#!/usr/bin/env python3
"""Rewrite antibiotic phosphotransferase ARO causal graphs.

These phosphotransferase families confer resistance by phosphorylating and
inactivating their antibiotic substrates.  The existing promoted graphs leave
the phosphorylation node ungrounded, stop at the modified-drug state, and have
sparse edge descriptions.  This updater grounds the broad alcohol-acceptor
phosphotransferase activity and terminates the inactivation path at resistance.

The ciprofloxacin phosphotransferase class is intentionally excluded because
its definition notes that the only proposed example was later rejected and
that no experimentally validated enzymes with that function are known.

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
    "timestamp": "2026-09-07T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": "Completed antibiotic phosphotransferase causal graphs",
    "llm_assisted": True,
}

INACTIVATION_EVIDENCE = {
    "reference": "ARO:3000557",
    "snippet": (
        "Enzyme that catalyzes the inactivation of an antibiotic resulting in "
        "resistance."
    ),
    "notes": "CARD definition for antibiotic inactivation enzymes.",
}

PHOSPHORYLATION_EVIDENCE = {
    "reference": "ARO:3000105",
    "snippet": "Phosphorylation of antibiotic usually by ATP, sometimes GTP.",
    "notes": "CARD definition for phosphorylation of antibiotic conferring resistance.",
}

GO_PHOSPHOTRANSFERASE_EVIDENCE = {
    "reference": "GO:0016773",
    "snippet": (
        "Catalysis of the transfer of a phosphorus-containing group from one "
        "compound to an alcohol group acceptor."
    ),
    "notes": "GO grounding for broad phosphotransferase activity on hydroxyl acceptors.",
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


@dataclass(frozen=True)
class Family:
    identifier: str
    label: str
    drug_label: str
    drug_grounding: str
    product_label: str
    definition: str


RIFAMPIN = Family(
    identifier="ARO:3004040",
    label="rifampin phosphotransferase",
    drug_label="rifamycin antibiotic",
    drug_grounding="ARO:3000157",
    product_label="phosphorylated inactive rifampin",
    definition=(
        "Rifampin phosphotransferases inactivate rifamycin antibiotics by "
        "phosphorylating rifampin at the 21-OH position."
    ),
)

CAPREOMYCIN = Family(
    identifier="ARO:3007074",
    label="capreomycin phosphotransferase",
    drug_label="aminoglycoside antibiotic",
    drug_grounding="ARO:0000016",
    product_label="phosphorylated inactive capreomycin",
    definition=(
        "Capreomycin phosphotransferases confer resistance to capreomycin "
        "antibiotics through antibiotic phosphorylation."
    ),
)

VIOMYCIN = Family(
    identifier="ARO:3004261",
    label="viomycin phosphotransferase",
    drug_label="peptide antibiotic",
    drug_grounding="ARO:3000053",
    product_label="phosphorylated inactive viomycin",
    definition=(
        "Viomycin phosphotransferases confer resistance to viomycin "
        "antibiotics through antibiotic phosphorylation."
    ),
)

CHLORAMPHENICOL = Family(
    identifier="ARO:3000249",
    label="chloramphenicol phosphotransferase",
    drug_label="phenicol antibiotic",
    drug_grounding="ARO:3000387",
    product_label="phosphorylated inactive chloramphenicol",
    definition=(
        "Chloramphenicol phosphotransferases inactivate phenicol antibiotics "
        "by ATP-dependent phosphorylation of chloramphenicol at the C-3 "
        "hydroxyl group."
    ),
)


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    family: Family


TARGETS: tuple[Target, ...] = (
    Target("ARO:3004040", "rifampin-phosphotransferase-aro3004040.yaml", RIFAMPIN),
    Target("ARO:3000444", "rpha-aro3000444.yaml", RIFAMPIN),
    Target("ARO:3003992", "rphb-aro3003992.yaml", RIFAMPIN),
    Target("ARO:3007074", "capreomycin-phosphotransferase-aro3007074.yaml", CAPREOMYCIN),
    Target("ARO:3007075", "cph-aro3007075.yaml", CAPREOMYCIN),
    Target("ARO:3004261", "viomycin-phosphotransferase-aro3004261.yaml", VIOMYCIN),
    Target("ARO:3003061", "vph-aro3003061.yaml", VIOMYCIN),
    Target("ARO:3000249", "chloramphenicol-phosphotransferase-aro3000249.yaml", CHLORAMPHENICOL),
    Target("ARO:3002700", "cmlv-aro3002700.yaml", CHLORAMPHENICOL),
)
TARGET_BY_ID = {target.identifier: target for target in TARGETS}


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


def _record_evidence(record: dict[str, Any]) -> dict[str, str]:
    return {
        "reference": str(record["identifier"]),
        "snippet": str(record["definition"]),
        "notes": f"CARD definition for {record['label']}.",
    }


def _family_evidence(family: Family) -> dict[str, str]:
    return {
        "reference": family.identifier,
        "snippet": family.definition,
        "notes": f"CARD definition for {family.label}.",
    }


def _drug_relation_evidence(family: Family) -> dict[str, str]:
    return {
        "reference": family.identifier,
        "snippet": (
            "relationship: confers_resistance_to_drug_class "
            f"{family.drug_grounding} ! {family.drug_label}"
        ),
        "notes": f"Drug-class relation asserted on {family.label}.",
    }


def _determinant_node(record: dict[str, Any]) -> dict[str, str]:
    return {
        "node_id": "determinant",
        "label": str(record["label"]),
        "node_type": "PROTEIN",
        "grounding": str(record["identifier"]),
    }


def _graph(record: dict[str, Any], family: Family) -> dict[str, Any]:
    record_evidence = _record_evidence(record)
    family_evidence = _family_evidence(family)
    common_evidence = (
        record_evidence,
        family_evidence,
        PHOSPHORYLATION_EVIDENCE,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → antibiotic phosphorylation",
        "description": (
            "Curated resistance-causation graph for phosphotransferase-mediated "
            "antibiotic phosphorylation and inactivation."
        ),
        "nodes": [
            _determinant_node(record),
            {
                "node_id": "mech0",
                "label": "antibiotic inactivation",
                "node_type": "MOLECULAR_FUNCTION",
                "grounding": "ARO:0001004",
            },
            {
                "node_id": "mech1",
                "label": "phosphorylation of antibiotic conferring resistance",
                "node_type": "MOLECULAR_FUNCTION",
                "grounding": "ARO:3000105",
            },
            {
                "node_id": "drug0",
                "label": family.drug_label,
                "node_type": "CHEMICAL",
                "grounding": family.drug_grounding,
            },
            {
                "node_id": "phosphorylation",
                "label": "phosphotransferase activity",
                "node_type": "MOLECULAR_FUNCTION",
                "grounding": "GO:0016773",
                "description": (
                    "Grounded to the broad GO alcohol-acceptor "
                    "phosphotransferase activity term and scoped here to "
                    "antibiotic phosphorylation."
                ),
            },
            {
                "node_id": "modified",
                "label": family.product_label,
                "node_type": "STATE",
                "description": (
                    "Local state for the antibiotic after "
                    "phosphotransferase-mediated phosphorylation."
                ),
            },
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "CARD classifies these phosphotransferases under the broad "
                "antibiotic inactivation resistance mechanism.",
                record_evidence,
                family_evidence,
                INACTIVATION_EVIDENCE,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Phosphotransferase antibiotic inactivation results from "
                "enzymatic phosphorylation of the drug.",
                INACTIVATION_EVIDENCE,
                PHOSPHORYLATION_EVIDENCE,
                family_evidence,
            ),
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech1",
                "CARD classifies this determinant under phosphorylation of "
                "antibiotic conferring resistance.",
                *common_evidence,
            ),
            _edge(
                "mech1",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "The phosphorylation resistance mechanism inactivates "
                "antibiotics by chemical modification.",
                *common_evidence,
                INACTIVATION_EVIDENCE,
            ),
            _edge(
                "determinant",
                "enables (phosphorylates the drug)",
                "RO:0002327",
                "phosphorylation",
                "The determinant catalyzes phosphotransfer to its antibiotic "
                "substrate.",
                *common_evidence,
                GO_PHOSPHOTRANSFERASE_EVIDENCE,
            ),
            _edge(
                "phosphorylation",
                "has input (the drug)",
                "RO:0002233",
                "drug0",
                f"{family.drug_label} is the antibiotic substrate for this "
                "phosphotransferase reaction.",
                *common_evidence,
                _drug_relation_evidence(family),
            ),
            _edge(
                "phosphorylation",
                "causally upstream of (inactivates the drug)",
                "RO:0002411",
                "modified",
                "Antibiotic phosphorylation produces an inactive "
                "phosphorylated drug state.",
                *common_evidence,
                GO_PHOSPHOTRANSFERASE_EVIDENCE,
            ),
            _edge(
                "modified",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "The phosphorylated antibiotic is inactive, lowering effective "
                "drug exposure and causing the resistance phenotype.",
                *common_evidence,
                INACTIVATION_EVIDENCE,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "The determinant confers antibiotic resistance by "
                "phosphorylating and inactivating the drug.",
                *common_evidence,
                INACTIVATION_EVIDENCE,
            ),
            _edge(
                "determinant",
                "confers resistance to (drug class)",
                "ARO:2000001",
                "drug0",
                f"CARD asserts a {family.drug_label} drug-class relation for "
                f"{family.label}.",
                record_evidence,
                family_evidence,
                _drug_relation_evidence(family),
                PHOSPHORYLATION_EVIDENCE,
            ),
        ],
    }


def _validate_record(record: dict[str, Any], target: Target) -> None:
    if record.get("identifier") != target.identifier:
        raise ValueError(
            f"{target.filename}: expected {target.identifier}, "
            f"found {record.get('identifier')}"
        )
    if not record.get("label"):
        raise ValueError(f"{target.identifier}: missing label")
    if not record.get("definition"):
        raise ValueError(f"{target.identifier}: missing definition")

    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1 or graphs[0].get("graph_id") != "resistance":
        raise ValueError(f"{target.identifier}: expected exactly one resistance graph")

    node_ids = {
        str(node.get("node_id"))
        for node in _dicts(graphs[0].get("nodes"))
        if node.get("node_id")
    }
    missing = {"determinant", "mech0", "mech1", "drug0", "modified", "resistance"} - node_ids
    if missing:
        missing_ids = ", ".join(sorted(missing))
        raise ValueError(f"{target.identifier}: missing node(s): {missing_ids}")


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    _validate_record(record, target)

    out = copy.deepcopy(record)
    out["causal_graphs"] = [_graph(record, target.family)]
    return out, out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not an antibiotic phosphotransferase target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    if HISTORY_CURATOR not in out:
        out = append_to_section(out, "curation_history", _dump({"curation_history": [HISTORY_EVENT]}))
        changed = True

    if "&id" in out or "*id" in out:
        raise ValueError(f"{path}: YAML anchors leaked into output")
    return out, changed


def iter_target_paths(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if not path.is_dir():
        raise ValueError(f"{path} is neither a file nor a directory")
    return [path / target.filename for target in TARGETS]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    parser.add_argument(
        "--path",
        type=Path,
        default=ARO_DIR,
        help="ARO directory or one antibiotic phosphotransferase YAML file",
    )
    args = parser.parse_args(argv)

    changed = unchanged = 0
    problems: list[str] = []
    for path in iter_target_paths(args.path):
        if not path.exists():
            problems.append(f"{path}: missing")
            continue
        try:
            before = path.read_text(encoding="utf-8")
            after, did_change = enrich_text(before, path)
        except (OSError, ValueError, yaml.YAMLError) as exc:
            problems.append(str(exc))
            continue

        if not did_change:
            unchanged += 1
            continue

        changed += 1
        print(f"  {'wrote' if args.apply else 'would write'} {path.name}")
        if args.apply:
            path.write_text(after, encoding="utf-8")

    print(f"{'changed' if args.apply else 'would change'}: {changed}")
    print(f"already enriched: {unchanged}")
    for problem in problems:
        print(f"PROBLEM: {problem}", file=sys.stderr)
    if not args.apply:
        print("dry run -- pass --apply to write")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
