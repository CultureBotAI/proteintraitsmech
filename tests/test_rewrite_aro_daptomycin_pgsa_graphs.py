from __future__ import annotations

import copy
import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_daptomycin_pgsa_graphs.py"


def _load():
    spec = importlib.util.spec_from_file_location(
        "rewrite_aro_daptomycin_pgsa_graphs",
        SCRIPT,
    )
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
                "reference": "ARO:3003420",
                "snippet": "pgsA is an integral membrane protein.",
            }
        ],
    }


def _record(identifier: str = "ARO:3003080") -> dict:
    return {
        "identifier": identifier,
        "definition": "definition",
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "nodes": [
                    {
                        "node_id": "determinant",
                        "label": "daptomycin resistant pgsA",
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
                        "node_id": "drug0",
                        "label": "peptide antibiotic",
                        "node_type": "CHEMICAL",
                        "grounding": "ARO:3000053",
                    },
                    {
                        "node_id": "pgp_synthase",
                        "label": "CDP-diacylglycerol-glycerol-3-phosphate "
                        "3-phosphatidyltransferase activity",
                        "node_type": "MOLECULAR_FUNCTION",
                    },
                    {
                        "node_id": "phospholipid",
                        "label": "phospholipid biosynthesis",
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
                    _edge("determinant", "mech0", "participates in", "RO:0000056"),
                    _edge("mech0", "resistance"),
                    _edge("determinant", "resistance"),
                    _edge("determinant", "drug0", "confers resistance to", "ARO:2000001"),
                    _edge("determinant", "pgp_synthase", "enables", "RO:0002327"),
                    _edge(
                        "pgp_synthase",
                        "phospholipid",
                        "part of (phospholipid biosynthesis)",
                        "BFO:0000050",
                    ),
                ],
            }
        ],
    }


def _actual_edge_pairs(record: dict) -> set[tuple[str, str]]:
    return {
        (edge["subject"], edge["object"])
        for edge in record["causal_graphs"][0]["edges"]
    }


def test_target_filenames_are_exactly_the_expected_three():
    assert {target.filename for target in R.TARGETS.values()} == {
        "daptomycin-resistant-pgsa-aro3003080.yaml",
        "bacillus-subtilis-pgsa-with-mutation-conferring-resistance-to-daptomycin-aro3003788.yaml",
        "staphylococcus-aureus-pgsa-mutations-conferring-resistance-to-daptomycin-aro3003323.yaml",
    }


@pytest.mark.parametrize("target", R.TARGETS.values())
def test_enrichment_grounds_pgp_synthase_and_phospholipid_nodes(target):
    out, changed = R.enrich_record(_record(target.identifier), target)

    assert changed
    graph = out["causal_graphs"][0]
    by_node = {node["node_id"]: node for node in graph["nodes"]}

    for node_id, node in R.SHARED_NODE_UPDATES.items():
        assert by_node[node_id] == node


@pytest.mark.parametrize("target", R.TARGETS.values())
def test_enrichment_keeps_expected_edge_set(target):
    out, changed = R.enrich_record(_record(target.identifier), target)

    assert changed
    assert _actual_edge_pairs(out) == R.EXPECTED_EDGES


@pytest.mark.parametrize("target", R.TARGETS.values())
def test_all_edges_get_descriptions_and_multiple_evidence_items(target):
    out, changed = R.enrich_record(_record(target.identifier), target)

    assert changed
    for edge in out["causal_graphs"][0]["edges"]:
        assert edge["description"]
        assert len(
            {
                (item["reference"], item["snippet"], item["notes"])
                for item in edge["evidence"]
            }
        ) == len(edge["evidence"])
        if target.identifier != R.DAPTOMYCIN_PGSA_IDENTIFIER:
            assert len({item["reference"] for item in edge["evidence"]}) > 1


def test_species_children_get_child_parent_and_activity_evidence():
    target = R.TARGETS["ARO:3003323"]

    out, changed = R.enrich_record(_record(target.identifier), target)

    assert changed
    for edge in out["causal_graphs"][0]["edges"]:
        references = {item["reference"] for item in edge["evidence"]}
        assert "ARO:3003323" in references or (edge["subject"], edge["object"]) == (
            "pgp_synthase",
            "phospholipid",
        )
        if (edge["subject"], edge["object"]) in {
            ("determinant", "resistance"),
            ("determinant", "drug0"),
            ("determinant", "pgp_synthase"),
        }:
            assert "ARO:3003080" in references
        if (edge["subject"], edge["object"]) in {
            ("determinant", "resistance"),
            ("determinant", "pgp_synthase"),
            ("pgp_synthase", "phospholipid"),
        }:
            assert "ARO:3003420" in references
        if (edge["subject"], edge["object"]) == ("determinant", "pgp_synthase"):
            assert "GO:0008444" in references


def test_enrich_record_is_idempotent():
    target = R.TARGETS["ARO:3003080"]

    once, changed = R.enrich_record(_record(), target)
    twice, changed_again = R.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused():
    with pytest.raises(ValueError, match="expected ARO:3003080, found ARO:3003323"):
        R.enrich_record(_record("ARO:3003323"), R.TARGETS["ARO:3003080"])


def test_unexpected_edges_are_refused():
    target = R.TARGETS["ARO:3003080"]
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("pgp_synthase", "unmodeled"))

    with pytest.raises(ValueError, match="unexpected edge pgp_synthase -> unmodeled"):
        R.enrich_record(record, target)


def test_duplicate_edges_are_refused():
    target = R.TARGETS["ARO:3003080"]
    record = _record()
    record["causal_graphs"][0]["edges"].append(
        _edge(
            "pgp_synthase",
            "phospholipid",
            "part of (phospholipid biosynthesis)",
            "BFO:0000050",
        )
    )

    with pytest.raises(ValueError, match="duplicate edge pgp_synthase -> phospholipid"):
        R.enrich_record(record, target)


def test_missing_expected_edges_are_refused():
    target = R.TARGETS["ARO:3003080"]
    record = _record()
    record["causal_graphs"][0]["edges"].pop(5)

    with pytest.raises(ValueError, match="missing edge\\(s\\): pgp_synthase -> phospholipid"):
        R.enrich_record(record, target)


def test_enrich_text_adds_history_once():
    target = R.TARGETS["ARO:3003080"]
    text = yaml.safe_dump(_record(), sort_keys=False)

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
    target = R.TARGETS["ARO:3003080"]
    enriched, changed = R.enrich_record(_record(), target)
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
    text += "- timestamp: '2026-09-06T00:00:00Z'\n"
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

        for node_id, node in R.SHARED_NODE_UPDATES.items():
            assert by_node[node_id] == node
        assert _actual_edge_pairs(out) == R.EXPECTED_EDGES
        for edge in graph["edges"]:
            assert edge["description"]
            assert len(
                {
                    (item["reference"], item["snippet"], item["notes"])
                    for item in edge["evidence"]
                }
            ) == len(edge["evidence"])
            if target.identifier != R.DAPTOMYCIN_PGSA_IDENTIFIER:
                assert len({item["reference"] for item in edge["evidence"]}) > 1
