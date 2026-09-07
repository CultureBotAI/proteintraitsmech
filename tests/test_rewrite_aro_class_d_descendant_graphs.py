from __future__ import annotations

import copy
import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_class_d_descendant_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location(
        "rewrite_aro_class_d_descendant_graphs",
        SCRIPT,
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


R = _load()


def _node(node_id: str, node_type: str, grounding: str | None = None) -> dict:
    node = {
        "node_id": node_id,
        "label": node_id,
        "node_type": node_type,
    }
    if grounding:
        node["grounding"] = grounding
    return node


def _evidence(reference: str = "ARO:test") -> list[dict[str, str]]:
    return [
        {
            "reference": reference,
            "snippet": f"Snippet for {reference}.",
            "notes": f"Notes for {reference}.",
        }
    ]


def _edge(
    subject: str,
    predicate_id: str,
    object_: str,
    predicate: str = "related to",
) -> dict:
    return {
        "subject": subject,
        "predicate": predicate,
        "predicate_id": predicate_id,
        "object": object_,
        "evidence": _evidence(),
    }


def _record(identifier: str = "ARO:3004746", drug_count: int = 1) -> dict:
    nodes = [
        _node("determinant", "PROTEIN", identifier),
        _node("mech0", "MOLECULAR_FUNCTION", "ARO:0001004"),
        _node("mech1", "MOLECULAR_FUNCTION", "ARO:3000187"),
        *[
            _node(f"drug{i}", "CHEMICAL", f"ARO:drug{i}")
            for i in range(drug_count)
        ],
        _node("active_site", "MOTIF", "PROSITE:PS00337"),
        _node("amide", "CHEMICAL"),
        _node("resistance", "PHENOTYPE", "GO:0046677"),
    ]
    edges = [
        _edge("determinant", "RO:0000056", "mech0"),
        _edge("mech0", "RO:0002411", "resistance"),
        _edge("determinant", "RO:0000056", "mech1"),
        _edge("mech1", "RO:0002411", "resistance"),
        _edge("determinant", "RO:0002411", "resistance"),
        *[
            _edge(
                "determinant",
                R.DRUG_CLASS_PREDICATE_ID,
                f"drug{i}",
                "confers resistance to",
            )
            for i in range(drug_count)
        ],
        _edge("active_site", "BFO:0000050", "determinant"),
        _edge("active_site", "RO:0002327", "mech1"),
        _edge("mech0", "RO:0002233", "amide"),
    ]
    return {
        "identifier": identifier,
        "label": "test class D beta-lactamase",
        "definition": "A test descendant of class D beta-lactamase.",
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "nodes": nodes,
                "edges": edges,
            }
        ],
    }


def _edge_pairs(record: dict) -> set[tuple[str, str]]:
    return {
        (edge["subject"], edge["object"])
        for edge in record["causal_graphs"][0]["edges"]
    }


def _node_ids(record: dict) -> set[str]:
    return {
        node["node_id"]
        for node in record["causal_graphs"][0]["nodes"]
    }


def test_targets_are_exact_class_d_descendant_records() -> None:
    assert {target.identifier for target in R.TARGETS} == {
        "ARO:3004746",
        "ARO:3004747",
        "ARO:3004758",
        "ARO:3004759",
        "ARO:3005394",
        "ARO:3005396",
        "ARO:3004241",
    }


def test_enrich_record_removes_only_local_amide_node() -> None:
    target = R.TARGET_BY_ID["ARO:3004746"]

    out, changed = R.enrich_record(_record(), target)

    assert changed
    assert _node_ids(out) == {
        "determinant",
        "mech0",
        "mech1",
        "drug0",
        "active_site",
        "resistance",
    }
    assert ("mech0", "amide") not in _edge_pairs(out)


def test_two_drug_class_edges_are_preserved() -> None:
    target = R.TARGET_BY_ID["ARO:3004241"]

    out, changed = R.enrich_record(_record("ARO:3004241", drug_count=2), target)

    assert changed
    assert {"drug0", "drug1"} <= _node_ids(out)
    assert ("determinant", "drug0") in _edge_pairs(out)
    assert ("determinant", "drug1") in _edge_pairs(out)


def test_expected_edges_are_written_for_one_drug_record() -> None:
    target = R.TARGET_BY_ID["ARO:3004746"]

    out, changed = R.enrich_record(_record(), target)

    assert changed
    assert _edge_pairs(out) == {
        ("determinant", "mech0"),
        ("mech0", "resistance"),
        ("determinant", "mech1"),
        ("mech1", "resistance"),
        ("determinant", "resistance"),
        ("determinant", "drug0"),
        ("active_site", "determinant"),
        ("active_site", "mech1"),
    }


def test_all_nodes_are_grounded_and_all_edges_are_complete() -> None:
    target = R.TARGET_BY_ID["ARO:3004746"]

    out, changed = R.enrich_record(_record(), target)
    graph = out["causal_graphs"][0]

    assert changed
    assert all(node.get("grounding") for node in graph["nodes"])
    for edge in graph["edges"]:
        references = {item["reference"] for item in edge["evidence"]}
        assert edge["description"]
        assert len(references) > 1


def test_drug_edge_description_is_preserved() -> None:
    record = _record()
    drug_edge = [
        edge
        for edge in record["causal_graphs"][0]["edges"]
        if edge["predicate_id"] == R.DRUG_CLASS_PREDICATE_ID
    ][0]
    drug_edge["description"] = "CARD asserts a precise beta-lactam drug class."
    target = R.TARGET_BY_ID["ARO:3004746"]

    out, changed = R.enrich_record(record, target)

    assert changed
    out_drug_edge = [
        edge
        for edge in out["causal_graphs"][0]["edges"]
        if edge["predicate_id"] == R.DRUG_CLASS_PREDICATE_ID
    ][0]
    assert out_drug_edge["description"] == "CARD asserts a precise beta-lactam drug class."


def test_enrich_record_is_idempotent() -> None:
    target = R.TARGET_BY_ID["ARO:3004746"]

    once, changed = R.enrich_record(_record(), target)
    twice, changed_again = R.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3004746, found ARO:3004758"):
        R.enrich_record(_record("ARO:3004758"), R.TARGET_BY_ID["ARO:3004746"])


def test_missing_required_node_is_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["nodes"] = [
        node
        for node in record["causal_graphs"][0]["nodes"]
        if node["node_id"] != "active_site"
    ]

    with pytest.raises(ValueError, match="missing node\\(s\\): active_site"):
        R.enrich_record(record, R.TARGET_BY_ID["ARO:3004746"])


def test_missing_drug_edge_is_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"] = [
        edge
        for edge in record["causal_graphs"][0]["edges"]
        if edge["predicate_id"] != R.DRUG_CLASS_PREDICATE_ID
    ]

    with pytest.raises(ValueError, match="missing ARO drug-class edge"):
        R.enrich_record(record, R.TARGET_BY_ID["ARO:3004746"])


def test_unexpected_non_amide_edge_is_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].append(
        _edge("mech1", "RO:0002233", "amide"),
    )

    with pytest.raises(ValueError, match="unexpected edge mech1 -> amide"):
        R.enrich_record(record, R.TARGET_BY_ID["ARO:3004746"])


def test_enrich_text_adds_history_once() -> None:
    text = yaml.safe_dump(_record("ARO:3004746"), sort_keys=False)
    path = ARO_DIR / R.TARGET_BY_ID["ARO:3004746"].filename

    once, changed = R.enrich_text(text, path)
    twice, changed_again = R.enrich_text(once, path)

    assert changed
    assert not changed_again
    assert once == twice
    assert once.count(R.HISTORY_CURATOR) == 1
    assert "&id" not in once
    assert "*id" not in once


@pytest.mark.skipif(not ARO_DIR.is_dir(), reason="ARO records absent")
def test_all_shipped_targets_are_rewritten_in_memory() -> None:
    for target in R.TARGETS:
        path = ARO_DIR / target.filename
        record = yaml.safe_load(path.read_text(encoding="utf-8"))

        out, changed = R.enrich_record(copy.deepcopy(record), target)

        assert changed or out == record
        assert "amide" not in _node_ids(out)
        assert all(edge.get("description") for edge in out["causal_graphs"][0]["edges"])
