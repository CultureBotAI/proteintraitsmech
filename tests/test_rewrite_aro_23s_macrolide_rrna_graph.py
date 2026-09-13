from __future__ import annotations

import copy
import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_23s_macrolide_rrna_graph.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location(
        "rewrite_aro_23s_macrolide_rrna_graph",
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


def _record(identifier: str = R.TARGET_IDENTIFIER) -> dict:
    return {
        "identifier": identifier,
        "label": "23S rRNA with mutation conferring resistance to macrolide antibiotics",
        "definition": (
            "Nucleotide point mutations in the 23S rRNA subunit may confer "
            "resistance to macrolide antibiotics."
        ),
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "nodes": [
                    _node("determinant", "NUCLEIC_ACID", identifier),
                    _node("mech0", "MOLECULAR_FUNCTION", "ARO:3000212"),
                    _node("drug0", "CHEMICAL", "ARO:0000000"),
                    _node("pt_loop", "NUCLEIC_ACID"),
                    _node("conformation", "STATE"),
                    _node("resistance", "PHENOTYPE", "GO:0046677"),
                ],
                "edges": [],
            }
        ],
    }


def _edge_pairs(record: dict) -> set[tuple[str, str]]:
    return {
        (edge["subject"], edge["object"])
        for edge in record["causal_graphs"][0]["edges"]
    }


def test_target_is_exactly_23s_macrolide_rrna() -> None:
    assert R.TARGET_IDENTIFIER == "ARO:3004125"
    assert R.iter_target_paths(ARO_DIR) == [ARO_DIR / R.TARGET_FILENAME]


def test_rewrite_grounds_binding_site_and_preserves_affinity_loss() -> None:
    out, changed = R.enrich_record(_record())
    graph = out["causal_graphs"][0]

    assert changed
    assert _edge_pairs(out) == {
        ("determinant", "mech0"),
        ("mech0", "resistance"),
        ("determinant", "resistance"),
        ("determinant", "drug0"),
        ("binding_site", "determinant"),
        ("determinant", "subunit"),
        ("drug0", "binding_site"),
        ("determinant", "altered_site"),
        ("altered_site", "binding_site"),
        ("altered_site", "resistance"),
    }
    by_node = {node["node_id"]: node for node in graph["nodes"]}
    assert by_node["binding_site"] == R.BINDING_SITE_NODE
    assert by_node["altered_site"] == R.ALTERED_SITE_NODE
    assert by_node["subunit"] == R.SUBUNIT_NODE
    assert "pt_loop" not in by_node
    assert "conformation" not in by_node


def test_all_non_state_nodes_are_grounded_and_all_edges_are_complete() -> None:
    out, changed = R.enrich_record(_record())
    graph = out["causal_graphs"][0]

    assert changed
    for node in graph["nodes"]:
        if node["node_type"] != "STATE":
            assert node.get("grounding")
        else:
            assert node.get("description")
    for edge in graph["edges"]:
        references = {item["reference"] for item in edge["evidence"]}
        assert edge["description"]
        assert len(references) > 1


def test_enrich_record_is_idempotent() -> None:
    once, changed = R.enrich_record(_record())
    twice, changed_again = R.enrich_record(once)

    assert changed
    assert not changed_again
    assert twice == once


def test_enrich_text_adds_history_once() -> None:
    text = yaml.safe_dump(_record(), sort_keys=False)
    path = ARO_DIR / R.TARGET_FILENAME

    once, changed = R.enrich_text(text, path)
    twice, changed_again = R.enrich_text(once, path)

    assert changed
    assert not changed_again
    assert once == twice
    assert once.count(R.HISTORY_CURATOR) == 1
    assert "&id" not in once
    assert "*id" not in once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3004125, found ARO:3000336"):
        R.enrich_record(_record("ARO:3000336"))


def test_missing_required_node_is_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["nodes"] = [
        node for node in record["causal_graphs"][0]["nodes"] if node["node_id"] != "drug0"
    ]

    with pytest.raises(ValueError, match="missing node\\(s\\): drug0"):
        R.enrich_record(record)


@pytest.mark.skipif(not ARO_DIR.is_dir(), reason="ARO records absent")
def test_shipped_target_is_rewritten_in_memory() -> None:
    path = ARO_DIR / R.TARGET_FILENAME
    record = yaml.safe_load(path.read_text(encoding="utf-8"))

    out, changed = R.enrich_record(copy.deepcopy(record))

    assert changed or out == record
    assert all(edge.get("description") for edge in out["causal_graphs"][0]["edges"])
