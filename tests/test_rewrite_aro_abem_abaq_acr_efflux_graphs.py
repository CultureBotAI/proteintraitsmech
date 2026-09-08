from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_abem_abaq_acr_efflux_graphs.py"


def _load():
    spec = importlib.util.spec_from_file_location(
        "rewrite_aro_abem_abaq_acr_efflux_graphs",
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
                "snippet": "relationship: confers_resistance_to_drug_class ARO:test ! test drug",
            }
        ],
    }


def _record(
    identifier: str = "ARO:3000753",
    kind: R.GraphKind = R.GraphKind.MATE,
    two_drugs: bool = False,
) -> dict:
    nodes = [
        _node("determinant", "PROTEIN", identifier),
        _node("mech0", "MOLECULAR_FUNCTION", "ARO:0010000"),
        _node("drug0", "CHEMICAL", "ARO:0000001"),
        _node("resistance", "PHENOTYPE", "GO:0046677"),
    ]
    if kind in {R.GraphKind.MFS, R.GraphKind.RND, R.GraphKind.TOLC_LIKE}:
        nodes.extend(
            [
                _node("domain", "DOMAIN", "Pfam:PF00873"),
                _node("fold", "DOMAIN", "CATH:3.30.70.1430"),
            ]
        )
    else:
        nodes.extend(
            [
                _node("extrusion", "MOLECULAR_FUNCTION"),
                _node("cation_gradient", "STATE"),
                _node("extruded", "STATE"),
            ]
        )

    drug_edges = [
        _edge(
            "determinant",
            "drug0",
            "confers resistance to (drug class)",
            "ARO:2000001",
        )
    ]
    if two_drugs:
        nodes.append(_node("drug1", "CHEMICAL", "ARO:0000016"))
        drug_edges.append(
            _edge(
                "determinant",
                "drug1",
                "confers resistance to (drug class)",
                "ARO:2000001",
            )
        )

    return {
        "identifier": identifier,
        "label": "test pump",
        "definition": "test pump definition",
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "title": "old",
                "description": "old",
                "nodes": nodes,
                "edges": [
                    _edge(
                        "determinant",
                        "mech0",
                        "participates in (resistance mechanism)",
                        "RO:0000056",
                    ),
                    _edge("mech0", "resistance"),
                    _edge("determinant", "resistance"),
                    *drug_edges,
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


def test_target_set_is_the_exact_rank_77_efflux_set() -> None:
    assert R.TARGETS == (
        R.Target("ARO:3000753", "abem-aro3000753.yaml", R.GraphKind.MATE),
        R.Target("ARO:3004574", "acinetobacter-baumannii-abaq-aro3004574.yaml", R.GraphKind.MFS),
        R.Target(
            "ARO:3004578",
            "acinetobacter-baumannii-abuo-aro3004578.yaml",
            R.GraphKind.TOLC_LIKE,
        ),
        R.Target("ARO:3000384", "acrab-tolc-aro3000384.yaml", R.GraphKind.RND),
        R.Target("ARO:3004082", "acrad-tolc-aro3004082.yaml", R.GraphKind.RND),
        R.Target("ARO:3000491", "acrd-aro3000491.yaml", R.GraphKind.RND),
    )


def test_mate_records_keep_drug_edge_and_gain_export_path() -> None:
    out, changed = R.enrich_record(
        _record("ARO:3000753"),
        R.TARGET_BY_ID["ARO:3000753"],
    )

    assert changed
    assert _node_ids(out) == [
        "determinant",
        "mech0",
        "drug0",
        "cation_gradient",
        "export",
        "extruded_drug",
        "resistance",
    ]
    assert _edge_keys(out) == {
        ("determinant", "RO:0000056", "mech0"),
        ("mech0", "RO:0002411", "resistance"),
        ("determinant", "RO:0002411", "resistance"),
        ("determinant", "ARO:2000001", "drug0"),
        ("cation_gradient", "RO:0002411", "export"),
        ("determinant", "RO:0002411", "export"),
        ("export", "RO:0002233", "drug0"),
        ("export", "RO:0002411", "extruded_drug"),
        ("extruded_drug", "RO:0002411", "resistance"),
    }


def test_mfs_records_keep_drug_edge_and_domain_fold_shape() -> None:
    out, changed = R.enrich_record(
        _record("ARO:3004574", R.GraphKind.MFS),
        R.TARGET_BY_ID["ARO:3004574"],
    )

    assert changed
    assert _node_ids(out) == [
        "determinant",
        "mech0",
        "drug0",
        "domain",
        "fold",
        "resistance",
    ]
    assert ("determinant", "ARO:2000001", "drug0") in _edge_keys(out)
    assert ("domain", "RO:0002327", "mech0") in _edge_keys(out)
    nodes = {node["node_id"]: node for node in out["causal_graphs"][0]["nodes"]}
    assert nodes["domain"]["grounding"] == "Pfam:PF07690"
    assert nodes["fold"]["grounding"] == "CATH:1.20.1250.20"


def test_rnd_records_keep_drug_edge_and_domain_fold_shape() -> None:
    out, changed = R.enrich_record(
        _record("ARO:3000384", R.GraphKind.RND),
        R.TARGET_BY_ID["ARO:3000384"],
    )

    assert changed
    assert ("determinant", "ARO:2000001", "drug0") in _edge_keys(out)
    assert ("domain", "RO:0002327", "mech0") in _edge_keys(out)
    nodes = {node["node_id"]: node for node in out["causal_graphs"][0]["nodes"]}
    assert nodes["domain"]["grounding"] == "Pfam:PF00873"
    assert nodes["fold"]["grounding"] == "CATH:3.30.70.1430"


def test_tolc_like_record_replaces_inner_transporter_domain_with_complex() -> None:
    out, changed = R.enrich_record(
        _record("ARO:3004578", R.GraphKind.TOLC_LIKE),
        R.TARGET_BY_ID["ARO:3004578"],
    )

    assert changed
    assert _node_ids(out) == [
        "determinant",
        "mech0",
        "drug0",
        "transporter",
        "export",
        "resistance",
    ]
    assert ("domain", "RO:0002327", "mech0") not in _edge_keys(out)
    assert ("determinant", "BFO:0000050", "transporter") in _edge_keys(out)
    assert ("export", "RO:0002233", "drug0") in _edge_keys(out)


def test_multiple_existing_drug_edges_are_preserved() -> None:
    out, changed = R.enrich_record(
        _record("ARO:3000753", two_drugs=True),
        R.TARGET_BY_ID["ARO:3000753"],
    )

    assert changed
    assert [node["node_id"] for node in out["causal_graphs"][0]["nodes"][:4]] == [
        "determinant",
        "mech0",
        "drug0",
        "drug1",
    ]
    assert ("determinant", "ARO:2000001", "drug0") in _edge_keys(out)
    assert ("determinant", "ARO:2000001", "drug1") in _edge_keys(out)
    assert ("export", "RO:0002233", "drug0") in _edge_keys(out)
    assert ("export", "RO:0002233", "drug1") in _edge_keys(out)


@pytest.mark.parametrize("target", R.TARGETS)
def test_all_output_edges_are_described_and_multi_evidenced(target: R.Target) -> None:
    out, changed = R.enrich_record(
        _record(target.identifier, target.kind),
        target,
    )

    assert changed
    for edge in out["causal_graphs"][0]["edges"]:
        assert edge["description"]
        assert len({item["reference"] for item in edge["evidence"]}) > 1
        assert all(item.get("snippet") for item in edge["evidence"])


@pytest.mark.parametrize("target", R.TARGETS)
def test_all_output_groundable_nodes_are_grounded(target: R.Target) -> None:
    out, changed = R.enrich_record(
        _record(target.identifier, target.kind),
        target,
    )

    assert changed
    for node in out["causal_graphs"][0]["nodes"]:
        if node["node_type"] != "STATE":
            assert node.get("grounding")


def test_enrich_record_is_idempotent() -> None:
    target = R.TARGET_BY_ID["ARO:3000753"]

    once, changed = R.enrich_record(_record("ARO:3000753"), target)
    twice, changed_again = R.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3004574, found ARO:3000753"):
        R.enrich_record(_record("ARO:3000753"), R.TARGET_BY_ID["ARO:3004574"])


def test_duplicate_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].append(
        _edge(
            "determinant",
            "drug0",
            "confers resistance to (drug class)",
            "ARO:2000001",
        )
    )

    with pytest.raises(ValueError, match="duplicate edge determinant -> drug0"):
        R.enrich_record(record, R.TARGET_BY_ID["ARO:3000753"])


def test_missing_drug_edge_is_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"] = [
        edge
        for edge in record["causal_graphs"][0]["edges"]
        if edge.get("predicate_id") != "ARO:2000001"
    ]

    with pytest.raises(ValueError, match="missing drug edge"):
        R.enrich_record(record, R.TARGET_BY_ID["ARO:3000753"])


def test_enrich_text_adds_history_once_and_avoids_yaml_anchors() -> None:
    text = yaml.safe_dump(_record("ARO:3000753"), sort_keys=False)

    once, changed = R.enrich_text(text, pathlib.Path("abem-aro3000753.yaml"))
    twice, changed_again = R.enrich_text(once, pathlib.Path("abem-aro3000753.yaml"))

    assert changed
    assert not changed_again
    assert once == twice
    assert R.HISTORY_CURATOR in once
    assert "&id" not in once
    assert "*id" not in once
