from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_uhpa_graph.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_uhpa_graph", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


U = _load()


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
                "reference": U.TARGET_IDENTIFIER,
                "snippet": U.UHP_A_EVIDENCE["snippet"],
            }
        ],
    }


def _record(identifier: str = U.TARGET_IDENTIFIER) -> dict:
    return {
        "identifier": identifier,
        "label": "Escherichia coli uhpA with mutation conferring resistance to fosfomycin",
        "definition": U.UHP_A_EVIDENCE["snippet"],
        "mapping_status": "REVIEWED",
        "evidence": [
            {
                "reference": "DOI:test",
                "notes": "PMID:test (aro citation)",
            }
        ],
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "title": "old",
                "description": "old",
                "nodes": [
                    {
                        "node_id": "determinant",
                        "label": "Escherichia coli uhpA with mutation conferring "
                        "resistance to fosfomycin",
                        "node_type": "PROTEIN",
                        "grounding": identifier,
                    },
                    {
                        "node_id": "mech0",
                        "label": "mutation conferring antibiotic resistance",
                        "node_type": "MOLECULAR_FUNCTION",
                        "grounding": "ARO:3000212",
                    },
                    {
                        "node_id": "uhpt_expression",
                        "label": "expression of the fosfomycin importer uhpT",
                        "node_type": "BIOLOGICAL_PROCESS",
                    },
                    {
                        "node_id": "import",
                        "label": "uptake of fosfomycin into the cell",
                        "node_type": "BIOLOGICAL_PROCESS",
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
                        "resistance",
                        "causally upstream of (confers resistance)",
                    ),
                    _edge(
                        "determinant",
                        "uhpt_expression",
                        "positively regulates (activates uhpT expression)",
                        "RO:0002213",
                    ),
                    _edge(
                        "uhpt_expression",
                        "import",
                        "causally upstream of (fosfomycin uptake)",
                    ),
                    _edge(
                        "determinant",
                        "import",
                        "negatively regulates (mutations reduce drug uptake)",
                        "RO:0002212",
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


def test_target_matches_exact_uhpa_record() -> None:
    assert U.TARGET.identifier == "ARO:3003893"
    assert (
        U.TARGET.filename
        == "escherichia-coli-uhpa-with-mutation-conferring-resistance-to-fosfomycin-aro3003893.yaml"
    )


def test_uhpa_record_rewrites_biology_nodes_as_reduced_local_states() -> None:
    out, changed = U.enrich_record(_record())

    assert changed
    assert _node_ids(out) == [
        "determinant",
        "mech0",
        "uhpt_expression",
        "import",
        "resistance",
    ]
    assert _edge_keys(out) == U.EXPECTED_EDGE_KEYS
    assert {node["node_type"] for node in out["causal_graphs"][0]["nodes"][2:4]} == {"STATE"}


def test_all_non_state_nodes_are_grounded_and_edges_described() -> None:
    out, changed = U.enrich_record(_record())

    assert changed
    graph = out["causal_graphs"][0]
    for node in graph["nodes"]:
        if node["node_type"] != "STATE":
            assert node.get("grounding")
    assert all(edge.get("description") for edge in graph["edges"])


def test_all_output_edges_are_multi_evidenced() -> None:
    out, changed = U.enrich_record(_record())

    assert changed
    for edge in out["causal_graphs"][0]["edges"]:
        assert len({item["reference"] for item in edge["evidence"]}) > 1


def test_mutant_graph_omits_wild_type_positive_activation_edge() -> None:
    out, changed = U.enrich_record(_record())

    assert changed
    assert ("determinant", "RO:0002213", "uhpt_expression") not in _edge_keys(out)
    import_edge = next(
        edge
        for edge in out["causal_graphs"][0]["edges"]
        if edge["object"] == "uhpt_expression"
    )
    assert import_edge["predicate_id"] == "RO:0002411"


def test_enrich_record_is_idempotent() -> None:
    once, changed = U.enrich_record(_record())
    twice, changed_again = U.enrich_record(once)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3003893, found ARO:3003894"):
        U.enrich_record(_record("ARO:3003894"))


def test_unexpected_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("import", "uhpt_expression"))

    with pytest.raises(ValueError, match="unexpected edge import -> uhpt_expression"):
        U.enrich_record(record)


def test_duplicate_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("mech0", "resistance"))

    with pytest.raises(ValueError, match="duplicate edge mech0 -> resistance"):
        U.enrich_record(record)


def test_missing_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"] = [
        edge
        for edge in record["causal_graphs"][0]["edges"]
        if edge["object"] != "import"
    ]

    with pytest.raises(ValueError, match="missing edge"):
        U.enrich_record(record)


def test_enrich_text_rewrites_yaml_aliases_and_adds_history_once() -> None:
    enriched, changed = U.enrich_record(_record())
    assert changed
    edges = enriched["causal_graphs"][0]["edges"]
    edges[1]["evidence"] = edges[0]["evidence"]
    text = yaml.safe_dump(enriched, sort_keys=False)
    assert "&id" in text

    out, changed = U.enrich_text(text, ARO_DIR / U.TARGET.filename)
    again, changed_again = U.enrich_text(out, ARO_DIR / U.TARGET.filename)

    assert changed
    assert not changed_again
    assert "&id" not in out
    assert "*id" not in out
    assert out.count(U.HISTORY_ACTION) == 1
    assert again == out


@pytest.mark.skipif(not ARO_DIR.is_dir(), reason="ARO records absent")
def test_shipped_target_is_enriched_in_memory_without_unexpected_edges() -> None:
    path = ARO_DIR / U.TARGET.filename
    record = yaml.safe_load(path.read_text(encoding="utf-8"))
    out, changed = U.enrich_record(record)

    assert changed or out == record
    assert _edge_keys(out) == U.EXPECTED_EDGE_KEYS
