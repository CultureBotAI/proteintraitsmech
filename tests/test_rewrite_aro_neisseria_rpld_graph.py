from __future__ import annotations

import copy
import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_neisseria_rpld_graph.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_neisseria_rpld_graph", SCRIPT)
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
        "label": "Neisseria gonorrhoeae rpld",
        "definition": "rpld encodes for the 50S L4 ribosomal protein.",
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "nodes": [
                    _node("determinant", "NUCLEIC_ACID", identifier),
                    _node("mech0", "MOLECULAR_FUNCTION", "ARO:3000212"),
                    _node("drug0", "CHEMICAL", "ARO:0000000"),
                    _node("ribosome", "CELLULAR_LOCALIZATION"),
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


def test_target_is_exactly_neisseria_rpld() -> None:
    assert R.TARGET_IDENTIFIER == "ARO:3004956"
    assert R.TARGET_FILENAME == "neisseria-gonorrhoeae-rpld-aro3004956.yaml"
    assert R.iter_target_paths(ARO_DIR) == [ARO_DIR / R.TARGET_FILENAME]


def test_rewrite_keeps_broad_macrolide_ribosome_target() -> None:
    out, changed = R.enrich_record(_record())
    graph = out["causal_graphs"][0]

    assert changed
    assert _edge_pairs(out) == {
        ("determinant", "mech0"),
        ("mech0", "resistance"),
        ("determinant", "resistance"),
        ("determinant", "drug0"),
        ("drug0", "ribosome"),
    }
    by_node = {node["node_id"]: node for node in graph["nodes"]}
    assert by_node["ribosome"] == R.RIBOSOME_NODE
    assert all(node.get("grounding") for node in graph["nodes"])


def test_all_edges_are_described_and_multi_evidenced() -> None:
    out, changed = R.enrich_record(_record())

    assert changed
    for edge in out["causal_graphs"][0]["edges"]:
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
    with pytest.raises(ValueError, match="expected ARO:3004956, found ARO:3005001"):
        R.enrich_record(_record("ARO:3005001"))


def test_missing_required_node_is_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["nodes"] = [
        node for node in record["causal_graphs"][0]["nodes"] if node["node_id"] != "ribosome"
    ]

    with pytest.raises(ValueError, match="missing node\\(s\\): ribosome"):
        R.enrich_record(record)


@pytest.mark.skipif(not ARO_DIR.is_dir(), reason="ARO records absent")
def test_shipped_target_is_rewritten_in_memory() -> None:
    path = ARO_DIR / R.TARGET_FILENAME
    record = yaml.safe_load(path.read_text(encoding="utf-8"))

    out, changed = R.enrich_record(copy.deepcopy(record))

    assert changed or out == record
    assert all(edge.get("description") for edge in out["causal_graphs"][0]["edges"])
