from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_early_beta_lactamase_graphs.py"


def _load():
    spec = importlib.util.spec_from_file_location(
        "rewrite_aro_early_beta_lactamase_graphs",
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
    identifier: str = "ARO:3002481",
    kind: R.GraphKind = R.GraphKind.CLASS_A,
    two_drugs: bool = False,
) -> dict:
    parts = R.CLASS_A_PARTS if kind == R.GraphKind.CLASS_A else R.METALLO_PARTS
    nodes = [
        _node("determinant", "PROTEIN", identifier),
        _node("mech0", "MOLECULAR_FUNCTION", "ARO:0001004"),
        _node("mech1", "MOLECULAR_FUNCTION", parts.mech1_node["grounding"]),
        _node(parts.catalytic_node_id, "DOMAIN", parts.catalytic_node["grounding"]),
        _node("fold", "DOMAIN", parts.fold_node["grounding"]),
        _node("resistance", "PHENOTYPE", "GO:0046677"),
        _node("drug0", "CHEMICAL", "ARO:0000020"),
    ]

    drug_edges = [
        _edge(
            "determinant",
            "drug0",
            "confers resistance to (drug class)",
            "ARO:2000001",
        )
    ]
    if two_drugs:
        nodes.append(_node("drug1", "CHEMICAL", "ARO:0000032"))
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
        "label": "test beta-lactamase",
        "definition": "test beta-lactamase definition",
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
                    _edge(
                        "determinant",
                        "mech1",
                        "participates in (resistance mechanism)",
                        "RO:0000056",
                    ),
                    _edge("mech1", "resistance"),
                    _edge("determinant", "resistance"),
                    _edge(parts.catalytic_node_id, "determinant", "part of", "BFO:0000050"),
                    _edge("determinant", "fold", "member of", "RO:0002350"),
                    _edge(
                        parts.catalytic_node_id,
                        "mech1",
                        "enables (catalysis)",
                        "RO:0002327",
                    ),
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


def test_target_set_is_the_exact_early_beta_lactamase_set() -> None:
    assert R.TARGETS == (
        R.Target("ARO:3002481", "aer-1-aro3002481.yaml", R.GraphKind.CLASS_A),
        R.Target("ARO:3000089", "aer-beta-lactamase-aro3000089.yaml", R.GraphKind.CLASS_A),
        R.Target("ARO:3006890", "afm-1-aro3006890.yaml", R.GraphKind.METALLO),
        R.Target("ARO:3006891", "afm-2-aro3006891.yaml", R.GraphKind.METALLO),
        R.Target("ARO:3008070", "afm-3-aro3008070.yaml", R.GraphKind.METALLO),
        R.Target("ARO:3008071", "afm-4-aro3008071.yaml", R.GraphKind.METALLO),
        R.Target("ARO:3008072", "afm-5-aro3008072.yaml", R.GraphKind.METALLO),
        R.Target("ARO:3005388", "afm-beta-lactamase-aro3005388.yaml", R.GraphKind.METALLO),
        R.Target("ARO:3006892", "alg11-1-aro3006892.yaml", R.GraphKind.METALLO),
        R.Target("ARO:3005389", "alg11-beta-lactamase-aro3005389.yaml", R.GraphKind.METALLO),
        R.Target("ARO:3006893", "alg6-1-aro3006893.yaml", R.GraphKind.METALLO),
        R.Target("ARO:3005390", "alg6-beta-lactamases-aro3005390.yaml", R.GraphKind.METALLO),
        R.Target("ARO:3006894", "ali-1-aro3006894.yaml", R.GraphKind.METALLO),
        R.Target("ARO:3006895", "ali-2-aro3006895.yaml", R.GraphKind.METALLO),
        R.Target("ARO:3005391", "ali-beta-lactamase-aro3005391.yaml", R.GraphKind.METALLO),
        R.Target("ARO:3006896", "ana-1-aro3006896.yaml", R.GraphKind.METALLO),
        R.Target("ARO:3005392", "ana-beta-lactamase-aro3005392.yaml", R.GraphKind.METALLO),
        R.Target("ARO:3002993", "aqu-1-aro3002993.yaml", R.GraphKind.CLASS_A),
        R.Target("ARO:3004647", "aqu-2-aro3004647.yaml", R.GraphKind.CLASS_A),
        R.Target("ARO:3004648", "aqu-3-aro3004648.yaml", R.GraphKind.CLASS_A),
        R.Target("ARO:3002992", "aqu-beta-lactamase-aro3002992.yaml", R.GraphKind.CLASS_A),
        R.Target("ARO:3004734", "arl-1-aro3004734.yaml", R.GraphKind.CLASS_A),
        R.Target("ARO:3004735", "arl-2-aro3004735.yaml", R.GraphKind.CLASS_A),
        R.Target("ARO:3004736", "arl-3-aro3004736.yaml", R.GraphKind.CLASS_A),
        R.Target("ARO:3004737", "arl-4-aro3004737.yaml", R.GraphKind.CLASS_A),
        R.Target("ARO:3004738", "arl-5-aro3004738.yaml", R.GraphKind.CLASS_A),
        R.Target("ARO:3004739", "arl-6-aro3004739.yaml", R.GraphKind.CLASS_A),
        R.Target("ARO:3004742", "arl-beta-lactamase-aro3004742.yaml", R.GraphKind.CLASS_A),
        R.Target("ARO:3008074", "asu1-1-aro3008074.yaml", R.GraphKind.CLASS_A),
        R.Target("ARO:3007863", "asu1-beta-lactamase-aro3007863.yaml", R.GraphKind.CLASS_A),
        R.Target("ARO:3006897", "axc-1-aro3006897.yaml", R.GraphKind.CLASS_A),
        R.Target("ARO:3006898", "axc-2-aro3006898.yaml", R.GraphKind.CLASS_A),
        R.Target("ARO:3006899", "axc-3-aro3006899.yaml", R.GraphKind.CLASS_A),
        R.Target("ARO:3006900", "axc-4-aro3006900.yaml", R.GraphKind.CLASS_A),
        R.Target("ARO:3006901", "axc-5-aro3006901.yaml", R.GraphKind.CLASS_A),
        R.Target("ARO:3008075", "axc-6-aro3008075.yaml", R.GraphKind.CLASS_A),
        R.Target("ARO:3008076", "axc-7-aro3008076.yaml", R.GraphKind.CLASS_A),
        R.Target("ARO:3008077", "axc-8-aro3008077.yaml", R.GraphKind.CLASS_A),
        R.Target("ARO:3005393", "axc-beta-lactamase-aro3005393.yaml", R.GraphKind.CLASS_A),
        R.Target("ARO:3008078", "b3su1-1-aro3008078.yaml", R.GraphKind.METALLO),
        R.Target("ARO:3007864", "b3su1-beta-lactamase-aro3007864.yaml", R.GraphKind.METALLO),
        R.Target("ARO:3008079", "b3su2-1-aro3008079.yaml", R.GraphKind.METALLO),
        R.Target("ARO:3007865", "b3su2-beta-lactamase-aro3007865.yaml", R.GraphKind.METALLO),
    )


@pytest.mark.parametrize(
    ("target", "kind", "catalytic_id", "catalytic_grounding", "fold_grounding"),
    [
        (
            R.TARGET_BY_ID["ARO:3002481"],
            R.GraphKind.CLASS_A,
            "active_site",
            "PROSITE:PS00146",
            "CATH:3.40.710.10",
        ),
        (
            R.TARGET_BY_ID["ARO:3006890"],
            R.GraphKind.METALLO,
            "domain",
            "Pfam:PF00753",
            "CATH:3.60.15.30",
        ),
    ],
)
def test_records_keep_drug_edge_and_gain_family_catalytic_nodes(
    target: R.Target,
    kind: R.GraphKind,
    catalytic_id: str,
    catalytic_grounding: str,
    fold_grounding: str,
) -> None:
    out, changed = R.enrich_record(_record(target.identifier, kind), target)

    assert changed
    assert _node_ids(out) == [
        "determinant",
        "mech0",
        "mech1",
        "drug0",
        catalytic_id,
        "fold",
        "resistance",
    ]
    assert _edge_keys(out) == {
        ("determinant", "RO:0000056", "mech0"),
        ("mech0", "RO:0002411", "resistance"),
        ("determinant", "RO:0000056", "mech1"),
        ("mech1", "RO:0002411", "resistance"),
        ("determinant", "RO:0002411", "resistance"),
        ("determinant", "ARO:2000001", "drug0"),
        (catalytic_id, "BFO:0000050", "determinant"),
        ("determinant", "RO:0002350", "fold"),
        (catalytic_id, "RO:0002327", "mech1"),
    }
    nodes = {node["node_id"]: node for node in out["causal_graphs"][0]["nodes"]}
    assert nodes[catalytic_id]["grounding"] == catalytic_grounding
    assert nodes["fold"]["grounding"] == fold_grounding


def test_multiple_existing_drug_edges_are_preserved() -> None:
    target = R.TARGET_BY_ID["ARO:3002481"]

    out, changed = R.enrich_record(
        _record(target.identifier, target.kind, two_drugs=True),
        target,
    )

    assert changed
    assert [node["node_id"] for node in out["causal_graphs"][0]["nodes"][3:5]] == [
        "drug0",
        "drug1",
    ]
    assert ("determinant", "ARO:2000001", "drug0") in _edge_keys(out)
    assert ("determinant", "ARO:2000001", "drug1") in _edge_keys(out)


@pytest.mark.parametrize("target", R.TARGETS)
def test_all_output_edges_are_described_and_multi_evidenced(target: R.Target) -> None:
    out, changed = R.enrich_record(_record(target.identifier, target.kind), target)

    assert changed
    for edge in out["causal_graphs"][0]["edges"]:
        assert edge["description"]
        assert len({item["reference"] for item in edge["evidence"]}) > 1
        assert all(item.get("snippet") for item in edge["evidence"])


@pytest.mark.parametrize("target", R.TARGETS)
def test_all_output_nodes_are_grounded(target: R.Target) -> None:
    out, changed = R.enrich_record(_record(target.identifier, target.kind), target)

    assert changed
    for node in out["causal_graphs"][0]["nodes"]:
        assert node.get("grounding")


@pytest.mark.parametrize(
    ("target", "kind"),
    [
        (R.TARGET_BY_ID["ARO:3002481"], R.GraphKind.CLASS_A),
        (R.TARGET_BY_ID["ARO:3006890"], R.GraphKind.METALLO),
    ],
)
def test_enrich_record_is_idempotent(target: R.Target, kind: R.GraphKind) -> None:
    once, changed = R.enrich_record(_record(target.identifier, kind), target)
    twice, changed_again = R.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3006890, found ARO:3002481"):
        R.enrich_record(_record("ARO:3002481"), R.TARGET_BY_ID["ARO:3006890"])


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
        R.enrich_record(record, R.TARGET_BY_ID["ARO:3002481"])


def test_missing_drug_edge_is_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"] = [
        edge
        for edge in record["causal_graphs"][0]["edges"]
        if edge.get("predicate_id") != "ARO:2000001"
    ]

    with pytest.raises(ValueError, match="missing drug edge"):
        R.enrich_record(record, R.TARGET_BY_ID["ARO:3002481"])


def test_enrich_text_adds_history_once_and_avoids_yaml_anchors() -> None:
    text = yaml.safe_dump(_record("ARO:3002481"), sort_keys=False)

    once, changed = R.enrich_text(text, pathlib.Path("aer-1-aro3002481.yaml"))
    twice, changed_again = R.enrich_text(once, pathlib.Path("aer-1-aro3002481.yaml"))

    assert changed
    assert not changed_again
    assert once == twice
    assert R.HISTORY_CURATOR in once
    assert "&id" not in once
    assert "*id" not in once
