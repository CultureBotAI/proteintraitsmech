from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_class_d_beta_lactamase_graph.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location(
        "rewrite_aro_class_d_beta_lactamase_graph",
        SCRIPT,
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


C = _load()


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
                "reference": C.CLASS_D_IDENTIFIER,
                "snippet": C.CLASS_D_EVIDENCE["snippet"],
            }
        ],
    }


def _record(identifier: str = C.CLASS_D_IDENTIFIER) -> dict:
    return {
        "identifier": identifier,
        "label": "class D beta-lactamase",
        "definition": C.CLASS_D_EVIDENCE["snippet"],
        "mapping_status": "REVIEWED",
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "title": "old",
                "description": "old",
                "nodes": [
                    {
                        "node_id": "determinant",
                        "label": "class D beta-lactamase",
                        "node_type": "PROTEIN",
                        "grounding": identifier,
                    },
                    {
                        "node_id": "mech0",
                        "label": "antibiotic inactivation",
                        "node_type": "MOLECULAR_FUNCTION",
                        "grounding": "ARO:0001004",
                    },
                    {
                        "node_id": "mech1",
                        "label": "hydrolysis of beta-lactam antibiotic by "
                        "serine beta-lactamase",
                        "node_type": "MOLECULAR_FUNCTION",
                        "grounding": "ARO:3000187",
                    },
                    {
                        "node_id": "active_site",
                        "label": "beta-lactamase class A/C/D active-site "
                        "signature (S-x-x-K)",
                        "node_type": "MOTIF",
                        "grounding": "PROSITE:PS00337",
                    },
                    {
                        "node_id": "amide",
                        "label": "amide bond of the beta-lactam ring",
                        "node_type": "CHEMICAL",
                    },
                    {
                        "node_id": "resistance",
                        "label": "antibiotic resistance phenotype",
                        "node_type": "PHENOTYPE",
                        "grounding": "GO:0046677",
                    },
                ],
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
                    _edge(
                        "determinant",
                        "resistance",
                        "causally upstream of (confers resistance)",
                    ),
                    _edge(
                        "active_site",
                        "determinant",
                        "part of (active site of the protein)",
                        "BFO:0000050",
                    ),
                    _edge(
                        "active_site",
                        "mech1",
                        "enables (catalysis)",
                        "RO:0002327",
                    ),
                    _edge(
                        "mech0",
                        "amide",
                        "has input (the beta-lactam amide bond)",
                        "RO:0002233",
                    ),
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


def test_target_matches_exact_class_d_parent() -> None:
    assert C.TARGET.identifier == "ARO:3000075"
    assert C.TARGET.filename == "class-d-beta-lactamase-aro3000075.yaml"


def test_class_d_record_reuses_grounded_hydrolysis_and_removes_amide() -> None:
    out, changed = C.enrich_record(_record())

    assert changed
    assert _node_ids(out) == [
        "determinant",
        "mech0",
        "mech1",
        "active_site",
        "resistance",
    ]
    assert _edge_keys(out) == C.EXPECTED_EDGE_KEYS
    assert "node_id: amide" not in yaml.safe_dump(out)


def test_all_output_nodes_are_grounded_and_edges_described() -> None:
    out, changed = C.enrich_record(_record())

    assert changed
    graph = out["causal_graphs"][0]
    assert all(node.get("grounding") for node in graph["nodes"])
    assert all(edge.get("description") for edge in graph["edges"])


def test_all_output_edges_are_multi_evidenced() -> None:
    out, changed = C.enrich_record(_record())

    assert changed
    for edge in out["causal_graphs"][0]["edges"]:
        assert len({item["reference"] for item in edge["evidence"]}) > 1


def test_active_site_edges_keep_class_d_prosite_evidence() -> None:
    out, changed = C.enrich_record(_record())

    assert changed
    graph = out["causal_graphs"][0]
    active_site_edges = [
        edge
        for edge in graph["edges"]
        if edge["subject"] == "active_site"
    ]
    assert len(active_site_edges) == 2
    for edge in active_site_edges:
        assert "PROSITE:PS00337" in {item["reference"] for item in edge["evidence"]}


def test_enrich_record_is_idempotent() -> None:
    once, changed = C.enrich_record(_record())
    twice, changed_again = C.enrich_record(once)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3000075, found ARO:3000076"):
        C.enrich_record(_record("ARO:3000076"))


def test_unexpected_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("amide", "resistance"))

    with pytest.raises(ValueError, match="unexpected edge amide -> resistance"):
        C.enrich_record(record)


def test_duplicate_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("mech1", "resistance"))

    with pytest.raises(ValueError, match="duplicate edge mech1 -> resistance"):
        C.enrich_record(record)


def test_missing_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"] = [
        edge
        for edge in record["causal_graphs"][0]["edges"]
        if edge["subject"] != "active_site"
    ]

    with pytest.raises(ValueError, match="missing edge"):
        C.enrich_record(record)


def test_enrich_text_rewrites_yaml_aliases_and_adds_history_once() -> None:
    enriched, changed = C.enrich_record(_record())
    assert changed
    edges = enriched["causal_graphs"][0]["edges"]
    edges[1]["evidence"] = edges[0]["evidence"]
    text = yaml.safe_dump(enriched, sort_keys=False)
    assert "&id" in text

    out, changed = C.enrich_text(text, ARO_DIR / C.TARGET.filename)
    again, changed_again = C.enrich_text(out, ARO_DIR / C.TARGET.filename)

    assert changed
    assert not changed_again
    assert "&id" not in out
    assert "*id" not in out
    assert out.count(C.HISTORY_ACTION) == 1
    assert again == out


@pytest.mark.skipif(not ARO_DIR.is_dir(), reason="ARO records absent")
def test_shipped_target_is_enriched_in_memory_without_unexpected_edges() -> None:
    path = ARO_DIR / C.TARGET.filename
    record = yaml.safe_load(path.read_text(encoding="utf-8"))
    out, changed = C.enrich_record(record)

    assert changed or out == record
    assert _edge_keys(out) == C.EXPECTED_EDGE_KEYS
