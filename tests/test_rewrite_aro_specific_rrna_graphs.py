from __future__ import annotations

import copy
import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_specific_rrna_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_specific_rrna_graphs", SCRIPT)
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


def _edge(subject: str, object_: str) -> dict:
    return {
        "subject": subject,
        "predicate": "causally upstream of",
        "predicate_id": "RO:0002411",
        "object": object_,
        "evidence": [
            {
                "reference": "ARO:test",
                "snippet": "test",
            }
        ],
    }


def _record(identifier: str = "ARO:3003211") -> dict:
    return {
        "identifier": identifier,
        "label": "test label",
        "definition": "test definition",
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "nodes": [
                    _node("determinant", "NUCLEIC_ACID", identifier),
                    _node("mech0", "MOLECULAR_FUNCTION", "ARO:3000212"),
                    _node("mech1", "MOLECULAR_FUNCTION", "ARO:3000211"),
                    _node("binding_site", "NUCLEIC_ACID"),
                    _node("subunit", "CELLULAR_LOCALIZATION"),
                    _node("resistance", "PHENOTYPE", "GO:0046677"),
                    _node("translation", "BIOLOGICAL_PROCESS", "GO:0006412"),
                    _node("domain", "DOMAIN", "Pfam:PF04055"),
                    _node("fold", "DOMAIN", "CATH:3.20.20"),
                ],
                "edges": [
                    _edge("determinant", "mech0"),
                    _edge("mech0", "resistance"),
                ],
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


def test_targets_are_exact_current_floor_records() -> None:
    assert {target.identifier for target in R.TARGETS} == {
        "ARO:3003211",
        "ARO:3004274",
        "ARO:3000336",
    }
    assert {target.filename for target in R.TARGETS} == {
        "16s-rrna-with-mutation-conferring-antibiotic-resistance-aro3003211.yaml",
        "23s-ribosomal-rna-methyltransferase-aro3004274.yaml",
        "23s-rrna-with-mutation-conferring-antibiotic-resistance-aro3000336.yaml",
    }


def test_16s_mutation_graph_keeps_specific_target_site_and_drops_translation() -> None:
    out, changed = R.enrich_record(_record("ARO:3003211"), R.SIXTEEN_S)
    nodes = _node_ids(out)

    assert changed
    assert "translation" not in nodes
    assert "binding_site" in nodes
    assert "altered_site" in nodes
    assert ("altered_site", "resistance") in _edge_pairs(out)


def test_23s_mutation_graph_routes_reduced_binding_to_resistance() -> None:
    out, changed = R.enrich_record(
        _record("ARO:3000336"),
        R.TWENTY_THREE_S_MUTATION,
    )

    assert changed
    by_node = {
        node["node_id"]: node
        for node in out["causal_graphs"][0]["nodes"]
    }
    assert by_node["altered_site"]["node_type"] == "STATE"
    assert by_node["subunit"]["grounding"] == "GO:0015934"
    assert ("altered_site", "resistance") in _edge_pairs(out)


def test_23s_methyltransferase_graph_drops_cfr_specific_domain_nodes() -> None:
    out, changed = R.enrich_record(
        _record("ARO:3004274"),
        R.TWENTY_THREE_S_METHYLTRANSFERASE,
    )
    nodes = _node_ids(out)

    assert changed
    assert "domain" not in nodes
    assert "fold" not in nodes
    assert "methyltransferase" in nodes
    assert "methylated" in nodes
    assert "target_site" in nodes
    assert ("methylated", "resistance") in _edge_pairs(out)


def test_all_non_state_nodes_are_grounded_and_all_edges_are_complete() -> None:
    for target in R.TARGETS:
        out, changed = R.enrich_record(_record(target.identifier), target)
        graph = out["causal_graphs"][0]

        assert changed
        for node in graph["nodes"]:
            if node["node_type"] != "STATE":
                assert node.get("grounding")
        for edge in graph["edges"]:
            references = {evidence["reference"] for evidence in edge["evidence"]}
            assert edge["description"]
            assert len(references) > 1


def test_enrich_record_is_idempotent() -> None:
    once, changed = R.enrich_record(_record("ARO:3003211"), R.SIXTEEN_S)
    twice, changed_again = R.enrich_record(once, R.SIXTEEN_S)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3003211, found ARO:3000336"):
        R.enrich_record(_record("ARO:3000336"), R.SIXTEEN_S)


def test_missing_required_node_is_refused() -> None:
    record = _record("ARO:3003211")
    record["causal_graphs"][0]["nodes"] = [
        node
        for node in record["causal_graphs"][0]["nodes"]
        if node["node_id"] != "binding_site"
    ]

    with pytest.raises(ValueError, match="missing node\\(s\\): binding_site"):
        R.enrich_record(record, R.SIXTEEN_S)


def test_enrich_text_adds_history_once() -> None:
    text = yaml.safe_dump(_record("ARO:3003211"), sort_keys=False)
    path = ARO_DIR / R.SIXTEEN_S.filename

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
        assert all(edge.get("description") for edge in out["causal_graphs"][0]["edges"])
