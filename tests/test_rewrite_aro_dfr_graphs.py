from __future__ import annotations

import copy
import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_dfr_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_dfr_graphs", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


R = _load()


def _edge(
    subject: str,
    object_: str,
    predicate: str = "causally upstream of",
    predicate_id: str = "RO:0002411",
) -> dict:
    return {
        "subject": subject,
        "predicate": predicate,
        "predicate_id": predicate_id,
        "object": object_,
        "evidence": [
            {
                "reference": "ARO:test",
                "snippet": "Test DFR evidence.",
            }
        ],
    }


def _node(node_id: str, node_type: str, grounding: str | None = None) -> dict:
    node = {
        "node_id": node_id,
        "label": node_id,
        "node_type": node_type,
    }
    if grounding is not None:
        node["grounding"] = grounding
    return node


def _record(identifier: str = "ARO:3001218", parent: bool = True) -> dict:
    return {
        "identifier": identifier,
        "label": "trimethoprim resistant dihydrofolate reductase dfr",
        "definition": "A trimethoprim-resistant dihydrofolate reductase.",
        "parent_traits": ["ARO:3003425"] if parent else [R.PARENT_IDENTIFIER],
        "trait_relations": [
            {
                "predicate": "RO:0000056",
                "object": "ARO:0001002",
                "relation_source": (
                    "ARO participates_in (mechanism) via "
                    "ARO:3000381 antibiotic target replacement protein"
                ),
            },
            {
                "predicate": "biolink:related_to",
                "object": R.DIAMINOPYRIMIDINE_IDENTIFIER,
                "relation_source": (
                    "ARO confers_resistance_to_drug_class via "
                    "ARO:3001218 trimethoprim resistant dihydrofolate reductase dfr"
                ),
            },
        ],
        "evidence": [
            {
                "reference": "DOI:10.1128/AAC.test",
                "notes": "PMID:1 (aro citation)",
            }
        ],
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "nodes": [
                    _node("determinant", "PROTEIN", identifier),
                    _node("mech0", "MOLECULAR_FUNCTION", "ARO:0001002"),
                    _node("drug0", "CHEMICAL", R.DIAMINOPYRIMIDINE_IDENTIFIER),
                    _node("domain", "DOMAIN", "Pfam:PF00186"),
                    _node("fold", "DOMAIN", "CATH:3.40.430"),
                    _node("resistance", "PHENOTYPE", "GO:0046677"),
                ],
                "edges": [
                    _edge(
                        "determinant",
                        "mech0",
                        "participates in (resistance mechanism)",
                        "RO:0000056",
                    ),
                    _edge("mech0", "resistance"),
                    _edge("determinant", "resistance"),
                    _edge(
                        "determinant",
                        "drug0",
                        "confers resistance to (drug class)",
                        "ARO:2000001",
                    ),
                    _edge("domain", "determinant", "part of", "BFO:0000050"),
                    _edge("determinant", "fold", "member of", "RO:0002350"),
                ],
            }
        ],
    }


def _edge_keys(record: dict) -> set[tuple[str, str, str]]:
    return {
        (edge["subject"], edge["predicate_id"], edge["object"])
        for edge in record["causal_graphs"][0]["edges"]
    }


def _node_ids(record: dict) -> list[str]:
    return [node["node_id"] for node in record["causal_graphs"][0]["nodes"]]


def test_target_discovery_is_parent_plus_exact_dfr_glob() -> None:
    paths = R.iter_target_paths(ARO_DIR)

    assert paths[0] == ARO_DIR / R.PARENT_FILENAME
    assert len(paths) == 58
    assert all(path.name.startswith("dfr") for path in paths[1:])


def test_parent_record_gets_domain_fold_activity_and_drug_route() -> None:
    target = R.Target(R.PARENT_IDENTIFIER, R.PARENT_FILENAME, is_parent=True)

    out, changed = R.enrich_record(_record(), target)

    assert changed
    assert _node_ids(out) == [
        "determinant",
        "mech0",
        "drug0",
        "domain",
        "fold",
        "shared_function",
        "structural_difference",
        "resistance",
    ]
    assert _edge_keys(out) == R.OUTPUT_EDGE_KEYS
    nodes = {node["node_id"]: node for node in out["causal_graphs"][0]["nodes"]}
    assert nodes["shared_function"] == R.SHARED_FUNCTION_NODE
    assert nodes["domain"] == R.DOMAIN_NODE
    assert nodes["fold"] == R.FOLD_NODE


def test_leaf_record_requires_dfr_parentage_and_keeps_child_grounding() -> None:
    target = R.Target("ARO:3002854", "dfra1-aro3002854.yaml", is_parent=False)

    out, changed = R.enrich_record(_record(target.identifier, parent=False), target)

    assert changed
    determinant = out["causal_graphs"][0]["nodes"][0]
    assert determinant["grounding"] == target.identifier
    assert _edge_keys(out) == R.OUTPUT_EDGE_KEYS


def test_target_for_record_refuses_non_dfr_leaf() -> None:
    with pytest.raises(ValueError, match="not a trimethoprim-resistant DFR target"):
        R.target_for_record(_record(), ARO_DIR / "not-dfr.yaml")


def test_target_for_record_refuses_dfr_leaf_with_wrong_parentage() -> None:
    record = _record("ARO:3002854", parent=False)
    record["parent_traits"] = ["ARO:unexpected"]

    with pytest.raises(ValueError, match="DFR leaf must be a direct"):
        R.target_for_record(record, ARO_DIR / "dfra1-aro3002854.yaml")


@pytest.mark.parametrize(
    "target,record",
    [
        (
            R.Target(R.PARENT_IDENTIFIER, R.PARENT_FILENAME, is_parent=True),
            _record(),
        ),
        (
            R.Target("ARO:3002854", "dfra1-aro3002854.yaml", is_parent=False),
            _record("ARO:3002854", parent=False),
        ),
    ],
)
def test_all_edges_are_described_and_multi_evidenced(
    target: R.Target,
    record: dict,
) -> None:
    out, changed = R.enrich_record(record, target)

    assert changed
    for edge in out["causal_graphs"][0]["edges"]:
        assert edge["description"]
        assert len({item["reference"] for item in edge["evidence"]}) > 1
        assert any(item.get("snippet") for item in edge["evidence"])


def test_enrich_record_is_idempotent() -> None:
    target = R.Target(R.PARENT_IDENTIFIER, R.PARENT_FILENAME, is_parent=True)

    once, changed = R.enrich_record(_record(), target)
    twice, changed_again = R.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_duplicate_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("determinant", "resistance"))

    with pytest.raises(ValueError, match="duplicate edge determinant -> resistance"):
        R.enrich_record(
            record,
            R.Target(R.PARENT_IDENTIFIER, R.PARENT_FILENAME, is_parent=True),
        )


def test_missing_core_edge_is_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"] = [
        edge
        for edge in record["causal_graphs"][0]["edges"]
        if edge["object"] != "fold"
    ]

    with pytest.raises(ValueError, match="missing edge"):
        R.enrich_record(
            record,
            R.Target(R.PARENT_IDENTIFIER, R.PARENT_FILENAME, is_parent=True),
        )


def test_enrich_text_adds_history_once() -> None:
    target = R.Target(R.PARENT_IDENTIFIER, R.PARENT_FILENAME, is_parent=True)
    text = yaml.safe_dump(_record(), sort_keys=False)

    once, changed = R.enrich_text(text, ARO_DIR / target.filename)
    twice, changed_again = R.enrich_text(once, ARO_DIR / target.filename)

    assert changed
    assert not changed_again
    assert once == twice
    assert once.count(R.HISTORY_ACTION) == 1
    assert "&id" not in once
    assert "*id" not in once


@pytest.mark.skipif(not ARO_DIR.is_dir(), reason="ARO records absent")
def test_shipped_targets_are_rewritten_in_memory() -> None:
    for path in R.iter_target_paths(ARO_DIR):
        record = yaml.safe_load(path.read_text(encoding="utf-8"))
        target = R.target_for_record(copy.deepcopy(record), path)

        out, changed = R.enrich_record(record, target)

        assert changed or out == record
        assert _node_ids(out) == [
            "determinant",
            "mech0",
            "drug0",
            "domain",
            "fold",
            "shared_function",
            "structural_difference",
            "resistance",
        ]
        assert _edge_keys(out) == R.OUTPUT_EDGE_KEYS
