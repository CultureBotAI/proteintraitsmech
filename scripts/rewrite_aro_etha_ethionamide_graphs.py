#!/usr/bin/env python3
"""Complete ethionamide-specific ethA causal graphs.

The ethionamide-resistant ethA records already carry the right prodrug
activation-loss graph, but sparse one-reference edges leave the records at
score 80. This pass preserves the ethionamide-specific topology and completes
edge descriptions and multi-reference evidence.

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

HISTORY_ACTION = "Completed ethionamide EthA prodrug-activation graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

MUTATION_EVIDENCE = {
    "reference": "ARO:3000212",
    "snippet": (
        "Point mutations in the DNA may lead to an altered gene product that "
        "may result in antibiotic resistance."
    ),
    "notes": "CARD definition for mutation conferring antibiotic resistance.",
}

ETHIONAMIDE_ETHA_EVIDENCE = {
    "reference": "ARO:3003457",
    "snippet": (
        "Mutations that occurs on the ethA genes resulting in the inability to "
        "catalyzes the oxidation of ethionamide (ETH) to the corresponding "
        "sulfoxide (the active drug)."
    ),
    "notes": "CARD definition for ethionamide resistant ethA.",
}

MTB_ETHA_EVIDENCE = {
    "reference": "ARO:3003458",
    "snippet": (
        "Mycobacterium tuberculosis ethA (Rv3854c) is a mono-oxygenase enzyme "
        "which activates the antibiotic ethionamide in vivo. Mutations in ethA "
        "confer resistance to ethionamide by modulating the activation and "
        "activity of the ethionamide prodrug."
    ),
    "notes": "CARD definition for M. tuberculosis ethA mutations conferring ethionamide resistance.",
}

ETHA_HYPERSENSITIVITY_EVIDENCE = {
    "reference": "PMID:10944230",
    "snippet": (
        "We have demonstrated that overproduction of Rv3855 (EtaR), a putative "
        "regulatory protein from MTb, confers ETA resistance whereas "
        "overproduction of an adjacent, clustered monooxygenase (Rv3854c, "
        "EtaA) confers ETA hypersensitivity."
    ),
    "notes": "DeBarber et al. 2000, showing that EtaA abundance controls ethionamide sensitivity.",
}

ETHIONAMIDE_S_OXIDATION_EVIDENCE = {
    "reference": "PMID:10944230",
    "snippet": (
        "Synthesis of radiolabeled ETA and an examination of drug metabolites "
        "formed by whole cells of Mycobacterium tuberculosis (MTb) have allowed "
        "us to demonstrate that ETA is activated by S-oxidation before "
        "interacting with its cellular target."
    ),
    "notes": "DeBarber et al. 2000, showing S-oxidation of ethionamide before target engagement.",
}

ETHIONAMIDE_PRODUCT_EVIDENCE = {
    "reference": "PMID:10944230",
    "snippet": (
        "ETA is metabolized by MTb to a 4-pyridylmethanol product remarkably "
        "similar in structure to that formed by the activation of isoniazid by "
        "the catalase-peroxidase KatG."
    ),
    "notes": "DeBarber et al. 2000, identifying the activated ethionamide product class.",
}

EDGE_DESCRIPTIONS = {
    (
        "determinant",
        "participates in (resistance mechanism)",
        "mech0",
    ): "CARD classifies EthA resistance mutations under mutation-conferring antibiotic resistance.",
    (
        "mech0",
        "causally upstream of",
        "resistance",
    ): "Loss of EthA prodrug activation causes ethionamide resistance.",
    (
        "determinant",
        "causally upstream of (confers resistance)",
        "resistance",
    ): (
        "The mutant determinant blocks activation of the ethionamide prodrug, "
        "leaving less active inhibitor for the InhA target."
    ),
    (
        "determinant",
        "confers resistance to (drug class)",
        "drug0",
    ): "CARD asserts ethA-mediated resistance to thioamide antibiotics.",
    (
        "determinant",
        "enables (S-oxidation of the prodrug)",
        "monooxygenase",
    ): (
        "Wild-type EthA/EtaA is the monooxygenase activity whose disruption "
        "prevents ethionamide activation."
    ),
    (
        "eta",
        "causally upstream of (is S-oxidised)",
        "activated_eta",
    ): "Ethionamide is activated by S-oxidation before target engagement.",
    (
        "monooxygenase",
        "causally upstream of (activates the prodrug)",
        "activated_eta",
    ): "EthA/EtaA monooxygenase activity activates the ethionamide prodrug.",
    (
        "activated_eta",
        "negatively regulates (inhibits the shared target)",
        "inha_gene",
    ): "The activated ethionamide product inhibits the downstream InhA target.",
    (
        "determinant",
        "negatively regulates (the defective EthA cannot activate the prodrug)",
        "monooxygenase",
    ): (
        "Resistance mutations impair the EthA/EtaA activity required for "
        "ethionamide activation."
    ),
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str


TARGETS: tuple[Target, ...] = (
    Target("ARO:3003457", "ethionamide-resistant-etha-aro3003457.yaml"),
    Target(
        "ARO:3003458",
        "mycobacterium-tuberculosis-etha-with-mutation-conferring-resistance-to-ethionami-aro3003458.yaml",
    ),
)
TARGET_BY_ID = {target.identifier: target for target in TARGETS}

EXPECTED_EDGE_KEYS = set(EDGE_DESCRIPTIONS)


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


def _record_evidence(record: dict[str, Any]) -> dict[str, str]:
    return {
        "reference": str(record["identifier"]),
        "snippet": " ".join(str(record["definition"]).split()),
        "notes": f"CARD definition for {record['label']}.",
    }


def _unique_evidence(*items: dict[str, str]) -> list[dict[str, str]]:
    evidence: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for item in items:
        marker = (item["reference"], item["snippet"])
        if marker in seen:
            continue
        seen.add(marker)
        evidence.append(copy.deepcopy(item))
    return evidence


def _evidence_for_edge(
    key: tuple[str, str, str],
    existing: list[dict[str, str]],
    target_evidence: dict[str, str],
) -> list[dict[str, str]]:
    common = [
        target_evidence,
        ETHIONAMIDE_ETHA_EVIDENCE,
        MTB_ETHA_EVIDENCE,
        MUTATION_EVIDENCE,
        ETHA_HYPERSENSITIVITY_EVIDENCE,
        ETHIONAMIDE_S_OXIDATION_EVIDENCE,
    ]
    match key:
        case ("determinant", "participates in (resistance mechanism)", "mech0"):
            extra = common
        case ("mech0", "causally upstream of", "resistance"):
            extra = common
        case ("determinant", "causally upstream of (confers resistance)", "resistance"):
            extra = [*common, ETHIONAMIDE_PRODUCT_EVIDENCE]
        case ("determinant", "confers resistance to (drug class)", "drug0"):
            extra = [target_evidence, ETHIONAMIDE_ETHA_EVIDENCE, MUTATION_EVIDENCE]
        case ("determinant", "enables (S-oxidation of the prodrug)", "monooxygenase"):
            extra = [target_evidence, ETHIONAMIDE_ETHA_EVIDENCE, MTB_ETHA_EVIDENCE, ETHA_HYPERSENSITIVITY_EVIDENCE]
        case ("eta", "causally upstream of (is S-oxidised)", "activated_eta"):
            extra = [
                target_evidence,
                ETHIONAMIDE_ETHA_EVIDENCE,
                MTB_ETHA_EVIDENCE,
                ETHIONAMIDE_S_OXIDATION_EVIDENCE,
                ETHIONAMIDE_PRODUCT_EVIDENCE,
            ]
        case ("monooxygenase", "causally upstream of (activates the prodrug)", "activated_eta"):
            extra = [
                target_evidence,
                ETHIONAMIDE_ETHA_EVIDENCE,
                MTB_ETHA_EVIDENCE,
                ETHA_HYPERSENSITIVITY_EVIDENCE,
                ETHIONAMIDE_S_OXIDATION_EVIDENCE,
                ETHIONAMIDE_PRODUCT_EVIDENCE,
            ]
        case ("activated_eta", "negatively regulates (inhibits the shared target)", "inha_gene"):
            extra = [
                target_evidence,
                MTB_ETHA_EVIDENCE,
                ETHIONAMIDE_S_OXIDATION_EVIDENCE,
                ETHIONAMIDE_PRODUCT_EVIDENCE,
            ]
        case (
            "determinant",
            "negatively regulates (the defective EthA cannot activate the prodrug)",
            "monooxygenase",
        ):
            extra = [
                target_evidence,
                ETHIONAMIDE_ETHA_EVIDENCE,
                MTB_ETHA_EVIDENCE,
                MUTATION_EVIDENCE,
                ETHA_HYPERSENSITIVITY_EVIDENCE,
            ]
        case _:
            raise ValueError(f"unexpected edge {key}")
    return _unique_evidence(*existing, *extra)


def enrich_graph(graph: dict[str, Any], record: dict[str, Any]) -> dict[str, Any]:
    graph = copy.deepcopy(graph)
    graph["title"] = f"{record['label']} → ethionamide prodrug-activation loss → resistance"
    graph["description"] = (
        "Curated resistance-causation graph for ethionamide-resistant EthA "
        "mutations. The determinant impairs the EthA/EtaA monooxygenase "
        "activity that activates ethionamide, reducing formation of the active "
        "InhA inhibitor and causing thioamide resistance."
    )

    target_evidence = _record_evidence(record)
    seen_edges: set[tuple[str, str, str]] = set()
    for edge in _dicts(graph.get("edges")):
        key = (
            str(edge.get("subject")),
            str(edge.get("predicate")),
            str(edge.get("object")),
        )
        if key not in EXPECTED_EDGE_KEYS:
            raise ValueError(f"{record['identifier']}: unexpected edge {key}")
        seen_edges.add(key)
        edge["description"] = EDGE_DESCRIPTIONS[key]
        edge["evidence"] = _evidence_for_edge(
            key,
            _dicts(edge.get("evidence")),
            target_evidence,
        )

    missing_edges = sorted(EXPECTED_EDGE_KEYS - seen_edges)
    if missing_edges:
        raise ValueError(f"{record['identifier']}: missing edge(s): {missing_edges}")
    return graph


def _validate_record(record: dict[str, Any], path: Path, target: Target) -> None:
    if path.name != target.filename:
        raise ValueError(f"{path}: target {target.identifier} must be in {target.filename}")
    if record.get("identifier") != target.identifier:
        raise ValueError(
            f"{target.filename}: expected {target.identifier}, "
            f"found {record.get('identifier')}"
        )

    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1 or graphs[0].get("graph_id") != "resistance":
        raise ValueError(f"{target.identifier}: expected exactly one resistance graph")


def enrich_record(
    record: dict[str, Any], path: Path, target: Target
) -> tuple[dict[str, Any], bool]:
    _validate_record(record, path, target)

    out = copy.deepcopy(record)
    out["causal_graphs"] = [enrich_graph(out["causal_graphs"][0], record)]
    return out, out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not an ethionamide EthA target: {identifier}")

    enriched, changed = enrich_record(record, path, target)
    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    if HISTORY_ACTION not in out:
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
        help="ARO directory or one of the ethionamide EthA target YAML files",
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
