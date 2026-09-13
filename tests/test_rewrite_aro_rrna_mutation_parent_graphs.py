from __future__ import annotations

import copy
import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_rrna_mutation_parent_graphs.py"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_rrna_mutation_parent_graphs", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


R = _load()
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _edge(subject: str, object_: str) -> dict:
    return {
        "subject": subject,
        "predicate": "causally upstream of",
        "predicate_id": "RO:0002411",
        "object": object_,
        "evidence": [
            {
                "reference": "ARO:3000328",
                "snippet": "SNPs in rRNA can confer antibiotic resistance",
            }
        ],
    }


def _record(identifier: str = "ARO:3000328") -> dict:
    return {
        "identifier": identifier,
        "definition": "definition",
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "nodes": [
                    {
                        "node_id": "determinant",
                        "label": "rRNA with mutation conferring antibiotic resistance",
                        "node_type": "NUCLEIC_ACID",
                        "grounding": identifier,
                    },
                    {
                        "node_id": "mech0",
                        "label": "mutation conferring antibiotic resistance",
                        "node_type": "MOLECULAR_FUNCTION",
                        "grounding": "ARO:3000212",
                    },
                    {
                        "node_id": "ribosome",
                        "label": "the bacterial ribosome",
                        "node_type": "CELLULAR_LOCALIZATION",
                    },
                    {
                        "node_id": "resistance",
                        "label": "antibiotic resistance phenotype",
                        "node_type": "PHENOTYPE",
                        "grounding": "GO:0046677",
                    },
                ],
                "edges": [
                    _edge("determinant", "mech0"),
                    _edge("mech0", "resistance"),
                    _edge("determinant", "resistance"),
                    _edge("determinant", "ribosome"),
                ],
            }
        ],
    }


def test_target_filenames_are_exactly_the_expected_two():
    assert {target.filename for target in R.TARGETS.values()} == {
        "rrna-with-mutation-conferring-antibiotic-resistance-aro3000328.yaml",
        "50s-rrna-with-mutation-conferring-antibiotic-resistance-aro3005003.yaml",
    }


def test_parent_enrichment_grounds_ribosome_and_describes_edges():
    out, changed = R.enrich_record(_record(), R.TARGETS["ARO:3000328"])

    assert changed
    graph = out["causal_graphs"][0]
    by_node = {node["node_id"]: node for node in graph["nodes"]}
    by_pair = {(edge["subject"], edge["object"]): edge for edge in graph["edges"]}

    assert by_node["ribosome"] == R.RIBOSOME_NODE
    assert len(by_pair) == len(R.EXPECTED_EDGES)
    for edge in graph["edges"]:
        assert edge["description"] == R.EDGE_DESCRIPTIONS[(edge["subject"], edge["object"])]
    assert by_pair[("determinant", "ribosome")]["evidence"][-1] == R.GO_RIBOSOME_EVIDENCE


def test_50s_target_gets_its_direct_aro_definition_on_every_edge():
    out, changed = R.enrich_record(_record("ARO:3005003"), R.TARGETS["ARO:3005003"])

    assert changed
    for edge in out["causal_graphs"][0]["edges"]:
        references = {item["reference"] for item in edge["evidence"]}
        assert "ARO:3005003" in references
    part_edge = next(
        edge
        for edge in out["causal_graphs"][0]["edges"]
        if (edge["subject"], edge["object"]) == ("determinant", "ribosome")
    )
    assert part_edge["evidence"][-2:] == [
        R.ARO_50S_RRNA_EVIDENCE,
        R.GO_RIBOSOME_EVIDENCE,
    ]


def test_enrich_record_is_idempotent():
    target = R.TARGETS["ARO:3000328"]

    once, changed = R.enrich_record(_record(), target)
    twice, changed_again = R.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused():
    with pytest.raises(ValueError, match="expected ARO:3000328, found ARO:3005003"):
        R.enrich_record(_record("ARO:3005003"), R.TARGETS["ARO:3000328"])


def test_unexpected_edges_are_refused():
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("ribosome", "unmodeled"))

    with pytest.raises(ValueError, match="unexpected edge ribosome -> unmodeled"):
        R.enrich_record(record, R.TARGETS["ARO:3000328"])


def test_duplicate_edges_are_refused():
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("determinant", "ribosome"))

    with pytest.raises(ValueError, match="duplicate edge determinant -> ribosome"):
        R.enrich_record(record, R.TARGETS["ARO:3000328"])


def test_missing_expected_edges_are_refused():
    record = _record()
    record["causal_graphs"][0]["edges"].pop()

    with pytest.raises(ValueError, match="missing edge\\(s\\): determinant -> ribosome"):
        R.enrich_record(record, R.TARGETS["ARO:3000328"])


def test_enrich_text_adds_history_once():
    target = R.TARGETS["ARO:3000328"]
    text = yaml.safe_dump(_record(), sort_keys=False)

    once, changed = R.enrich_text(text, ARO_DIR / target.filename)
    twice, changed_again = R.enrich_text(once, ARO_DIR / target.filename)

    assert changed
    assert not changed_again
    assert once == twice
    assert "&id" not in once
    assert "*id" not in once
    assert once.count(R.HISTORY_ACTION) == 1
    assert "curation_history:" in once


def test_enrich_text_rewrites_yaml_aliases_without_duplicating_history():
    target = R.TARGETS["ARO:3000328"]
    enriched, changed = R.enrich_record(_record(), target)
    assert changed
    edges = enriched["causal_graphs"][0]["edges"]
    determinant_mech = next(
        edge
        for edge in edges
        if (edge["subject"], edge["object"]) == ("determinant", "mech0")
    )
    mech_resistance = next(
        edge
        for edge in edges
        if (edge["subject"], edge["object"]) == ("mech0", "resistance")
    )
    mech_resistance["evidence"] = determinant_mech["evidence"]
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
    assert out.count(R.HISTORY_ACTION) == 1


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
        assert by_node["ribosome"]["grounding"] == "GO:0005840"
        for edge in graph["edges"]:
            assert edge["description"]
