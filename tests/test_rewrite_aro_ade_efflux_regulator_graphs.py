from __future__ import annotations

import copy
import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_ade_efflux_regulator_graphs.py"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_ade_efflux_regulator_graphs", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


R = _load()
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


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
        "description": "old description",
        "evidence": [
            {
                "reference": "ARO:3000702",
                "snippet": "AcrR archetype evidence",
            }
        ],
    }


def _record(
    identifier: str = "ARO:3000620",
    regulatory_node: str = "repression",
    duplicate_regulatory_edge: bool = True,
) -> dict:
    edges = [
        _edge("determinant", "mech0"),
        _edge("mech0", "resistance"),
        _edge("determinant", "resistance"),
        _edge(
            "determinant",
            regulatory_node,
            "enables (activates or represses the pump operon)",
            "RO:0002327",
        ),
        _edge(
            regulatory_node,
            "pump",
            "regulates pump expression",
            "RO:0002212",
        ),
    ]
    if duplicate_regulatory_edge:
        edges.append(
            _edge(
                "determinant",
                regulatory_node,
                "negatively regulates (mutation lifts the repression)",
                "RO:0002212",
            )
        )

    return {
        "identifier": identifier,
        "definition": "definition",
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "nodes": [
                    {
                        "node_id": "determinant",
                        "label": "ade determinant",
                        "node_type": "PROTEIN",
                        "grounding": identifier,
                    },
                    {
                        "node_id": "mech0",
                        "label": "antibiotic efflux",
                        "node_type": "MOLECULAR_FUNCTION",
                        "grounding": "ARO:0010000",
                    },
                    {
                        "node_id": "pump",
                        "label": "the efflux pump this determinant regulates",
                        "node_type": "PROTEIN",
                    },
                    {
                        "node_id": regulatory_node,
                        "label": "regulation of efflux pump expression",
                        "node_type": "BIOLOGICAL_PROCESS",
                    },
                    {
                        "node_id": "resistance",
                        "label": "antibiotic resistance phenotype",
                        "node_type": "PHENOTYPE",
                        "grounding": "GO:0046677",
                    },
                ],
                "edges": edges,
            }
        ],
    }


def _actual_edge_pairs(record: dict) -> set[tuple[str, str]]:
    return {
        (edge["subject"], edge["object"])
        for edge in record["causal_graphs"][0]["edges"]
    }


def test_target_filenames_are_exactly_the_expected_four():
    assert {target.filename for target in R.TARGETS.values()} == {
        "adel-aro3000620.yaml",
        "aden-aro3000559.yaml",
        "ader-aro3000553.yaml",
        "ades-aro3000549.yaml",
    }


def test_adel_rewrites_repression_to_adefgh_overexpression():
    out, changed = R.enrich_record(_record(), R.TARGETS["ARO:3000620"])

    assert changed
    graph = out["causal_graphs"][0]
    by_node = {node["node_id"]: node for node in graph["nodes"]}
    by_pair = {(edge["subject"], edge["object"]): edge for edge in graph["edges"]}

    assert by_node["pump"] == R.ADEFGH_NODE
    assert "repression" not in by_node
    assert by_node["overexpression"] == R.ADEFGH_OVEREXPRESSION_NODE
    assert len(by_pair) == len(R.TARGETS["ARO:3000620"].expected_edges)
    assert ("determinant", "overexpression") in by_pair
    assert by_pair[("overexpression", "pump")]["predicate_id"] == "RO:0002213"
    assert by_pair[("pump", "mech0")]["evidence"][0] == R.TARGET_EVIDENCE["ARO:3000620"]
    assert "&id" not in yaml.safe_dump(out, sort_keys=False)


def test_aden_drops_wildtype_repressor_edge_and_adds_adeijk_efflux():
    out, changed = R.enrich_record(_record("ARO:3000559"), R.TARGETS["ARO:3000559"])

    assert changed
    graph = out["causal_graphs"][0]
    by_node = {node["node_id"]: node for node in graph["nodes"]}
    full_keys = {
        (edge["subject"], edge["predicate_id"], edge["object"]) for edge in graph["edges"]
    }

    assert by_node["pump"] == R.ADEIJK_NODE
    assert by_node["repression"] == R.ADEIJK_REPRESSION_NODE
    assert ("determinant", "RO:0002327", "repression") not in full_keys
    assert _actual_edge_pairs(out) == R.TARGETS["ARO:3000559"].expected_edges


def test_ade_rs_targets_ground_adeabc_and_positive_regulation():
    target = R.TARGETS["ARO:3000549"]

    out, changed = R.enrich_record(
        _record("ARO:3000549", regulatory_node="activation", duplicate_regulatory_edge=False),
        target,
    )

    assert changed
    graph = out["causal_graphs"][0]
    by_node = {node["node_id"]: node for node in graph["nodes"]}
    by_pair = {(edge["subject"], edge["object"]): edge for edge in graph["edges"]}

    assert by_node["pump"] == R.ADEABC_NODE
    assert by_node["activation"] == R.ADEABC_ACTIVATION_NODE
    assert by_pair[("activation", "pump")]["predicate_id"] == "RO:0002213"
    assert by_pair[("pump", "mech0")]["predicate_id"] == "RO:0002327"


def test_archetype_evidence_is_replaced_with_exact_evidence():
    out, changed = R.enrich_record(_record("ARO:3000559"), R.TARGETS["ARO:3000559"])

    assert changed
    for edge in out["causal_graphs"][0]["edges"]:
        references = {item["reference"] for item in edge["evidence"]}
        assert "ARO:3000702" not in references
        assert "ARO:3000559" in references


def test_enrich_record_is_idempotent():
    target = R.TARGETS["ARO:3000553"]
    record = _record("ARO:3000553", regulatory_node="activation", duplicate_regulatory_edge=False)

    once, changed = R.enrich_record(record, target)
    twice, changed_again = R.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused():
    with pytest.raises(ValueError, match="expected ARO:3000559, found ARO:3000620"):
        R.enrich_record(_record(), R.TARGETS["ARO:3000559"])


def test_unexpected_edges_are_refused():
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("pump", "unmodeled"))

    with pytest.raises(ValueError, match="unexpected edge pump -> unmodeled"):
        R.enrich_record(record, R.TARGETS["ARO:3000620"])


def test_duplicate_edges_are_refused():
    record = _record()
    record["causal_graphs"][0]["edges"].append(
        _edge("pump", "mech0", "enables (drug efflux)", "RO:0002327")
    )
    record["causal_graphs"][0]["edges"].append(
        _edge("pump", "mech0", "enables (drug efflux)", "RO:0002327")
    )

    with pytest.raises(ValueError, match="duplicate edge pump -> mech0"):
        R.enrich_record(record, R.TARGETS["ARO:3000620"])


def test_missing_expected_edges_are_refused():
    record = _record()
    record["causal_graphs"][0]["edges"].pop(4)

    with pytest.raises(ValueError, match="missing edge\\(s\\): overexpression -> pump"):
        R.enrich_record(record, R.TARGETS["ARO:3000620"])


def test_enrich_text_adds_history_once():
    target = R.TARGETS["ARO:3000559"]
    text = yaml.safe_dump(_record("ARO:3000559"), sort_keys=False)

    once, changed = R.enrich_text(text, ARO_DIR / target.filename)
    twice, changed_again = R.enrich_text(once, ARO_DIR / target.filename)

    assert changed
    assert not changed_again
    assert once == twice
    assert "&id" not in once
    assert "*id" not in once
    assert once.count("codex-causal-graph-quality") == 1
    assert "curation_history:" in once


def test_enrich_text_rewrites_yaml_aliases_without_duplicating_history():
    target = R.TARGETS["ARO:3000553"]
    enriched, changed = R.enrich_record(
        _record("ARO:3000553", regulatory_node="activation", duplicate_regulatory_edge=False),
        target,
    )
    assert changed
    edges = enriched["causal_graphs"][0]["edges"]
    determinant_efflux = next(
        edge
        for edge in edges
        if (edge["subject"], edge["object"]) == ("determinant", "mech0")
    )
    efflux_resistance = next(
        edge
        for edge in edges
        if (edge["subject"], edge["object"]) == ("mech0", "resistance")
    )
    efflux_resistance["evidence"] = determinant_efflux["evidence"]
    text = yaml.safe_dump(enriched, sort_keys=False)
    assert "&id" in text
    text += "\ncuration_history:\n"
    text += "- timestamp: '2026-09-05T00:00:00Z'\n"
    text += "  curator: codex-causal-graph-quality\n"
    text += "  action: already enriched\n"
    text += "  llm_assisted: true\n"

    out, changed = R.enrich_text(text, ARO_DIR / target.filename)

    assert changed
    assert "&id" not in out
    assert "*id" not in out
    assert out.count("codex-causal-graph-quality") == 1


@pytest.mark.skipif(not ARO_DIR.is_dir(), reason="ARO records absent")
def test_all_shipped_targets_are_enriched_in_memory_without_unexpected_edges():
    for target in R.TARGETS.values():
        path = ARO_DIR / target.filename
        record = yaml.safe_load(path.read_text(encoding="utf-8"))
        out, changed = R.enrich_record(copy.deepcopy(record), target)
        assert changed or out == record
        graph = next(
            graph for graph in out["causal_graphs"] if graph["graph_id"] == "resistance"
        )
        by_node = {node["node_id"]: node for node in graph["nodes"]}
        assert by_node["pump"]["grounding"] == target.pump_node["grounding"]
        assert ("pump", "mech0") in _actual_edge_pairs(out)
        for edge in graph["edges"]:
            assert edge["description"]
            references = {item["reference"] for item in edge["evidence"]}
            assert target.identifier in references
            assert "ARO:3000702" not in references
