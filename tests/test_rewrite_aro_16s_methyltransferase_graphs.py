from __future__ import annotations

import copy
import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_16s_methyltransferase_graphs.py"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_16s_methyltransferase_graphs", SCRIPT)
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
                "reference": "PMID:40643688",
                "snippet": "16S rRNA methyltransferase evidence",
            }
        ],
    }


def _record(identifier: str = "ARO:3000857", *, child: bool = False) -> dict:
    nodes = [
        {
            "node_id": "determinant",
            "label": "16S ribosomal RNA methyltransferase",
            "node_type": "PROTEIN",
            "grounding": identifier,
        },
        {
            "node_id": "mech0",
            "label": "antibiotic target alteration",
            "node_type": "MOLECULAR_FUNCTION",
            "grounding": "ARO:0001001",
        },
        {
            "node_id": "mech1",
            "label": "ribosomal alteration conferring antibiotic resistance",
            "node_type": "MOLECULAR_FUNCTION",
            "grounding": "ARO:3000211",
        },
        {
            "node_id": "methyltransferase",
            "label": "16S rRNA methyltransferase activity",
            "node_type": "MOLECULAR_FUNCTION",
        },
        {
            "node_id": "decoding_site",
            "label": "16S rRNA decoding site (aminoglycoside binding site)",
            "node_type": "NUCLEIC_ACID",
        },
        {
            "node_id": "methylated",
            "label": "methylated decoding site",
            "node_type": "STATE",
        },
        {
            "node_id": "resistance",
            "label": "antibiotic resistance phenotype",
            "node_type": "PHENOTYPE",
            "grounding": "GO:0046677",
        },
    ]
    if child:
        nodes.insert(
            3,
            {
                "node_id": "drug0",
                "label": "aminoglycoside antibiotic",
                "node_type": "CHEMICAL",
                "grounding": "ARO:0000016",
            },
        )

    edges = [
        _edge("determinant", "mech0"),
        _edge("mech0", "resistance"),
        _edge("determinant", "mech1"),
        _edge("mech1", "resistance"),
        _edge("determinant", "resistance"),
        _edge("determinant", "methyltransferase"),
        _edge("methyltransferase", "methylated"),
        _edge("methylated", "decoding_site"),
    ]
    if child:
        edges.insert(5, _edge("determinant", "drug0"))
        edges.append(_edge("drug0", "decoding_site"))

    return {
        "identifier": identifier,
        "label": "16S rRNA methyltransferase",
        "definition": "definition",
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "nodes": nodes,
                "edges": edges,
            }
        ],
    }


def test_target_filenames_are_exactly_the_expected_three():
    assert {target.filename for target in R.TARGETS.values()} == {
        "16s-ribosomal-rna-methyltransferase-aro3000857.yaml",
        "16s-rrna-methyltransferase-a1408-aro3004272.yaml",
        "16s-rrna-methyltransferase-g1405-aro3004271.yaml",
    }


def test_parent_enrichment_grounds_nodes_describes_edges_and_adds_terminal_edge():
    out, changed = R.enrich_record(_record(), R.TARGETS["ARO:3000857"])

    assert changed
    graph = out["causal_graphs"][0]
    by_node = {node["node_id"]: node for node in graph["nodes"]}
    by_pair = {(edge["subject"], edge["object"]): edge for edge in graph["edges"]}

    assert by_node["methyltransferase"] == R.SHARED_NODE_UPDATES["methyltransferase"]
    assert by_node["decoding_site"] == R.SHARED_NODE_UPDATES["decoding_site"]
    assert by_node["methylated"] == R.SHARED_NODE_UPDATES["methylated"]
    assert by_node["decoding_site"]["grounding"] == "SO:0000252"
    assert by_node["methylated"]["grounding"] == "SO:0000252"
    assert len(by_pair) == len(R.PARENT_EDGES)
    assert ("methylated", "resistance") in by_pair
    for edge in graph["edges"]:
        assert edge["description"]
    assert by_pair[("determinant", "methyltransferase")]["evidence"][-2:] == [
        R.RRNA_METHYLTRANSFERASE_EVIDENCE,
        R.SO_RRNA_EVIDENCE,
    ]
    assert by_pair[("methyltransferase", "methylated")]["evidence"][-2:] == [
        R.RRNA_METHYLTRANSFERASE_EVIDENCE,
        R.SO_RRNA_EVIDENCE,
    ]


def test_child_targets_allow_the_drug_class_edges():
    target = R.TARGETS["ARO:3004272"]
    out, changed = R.enrich_record(_record("ARO:3004272", child=True), target)

    assert changed
    by_pair = {
        (edge["subject"], edge["object"]): edge
        for edge in out["causal_graphs"][0]["edges"]
    }
    assert len(by_pair) == len(R.CHILD_EDGES)
    assert by_pair[("determinant", "drug0")]["description"] == (
        R.ALL_EDGE_DESCRIPTIONS[("determinant", "drug0")]
    )
    assert by_pair[("drug0", "decoding_site")]["description"] == (
        R.ALL_EDGE_DESCRIPTIONS[("drug0", "decoding_site")]
    )
    assert ("methylated", "resistance") in by_pair


def test_enrich_record_is_idempotent():
    target = R.TARGETS["ARO:3000857"]

    once, changed = R.enrich_record(_record(), target)
    twice, changed_again = R.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused():
    with pytest.raises(ValueError, match="expected ARO:3000857, found ARO:3004272"):
        R.enrich_record(_record("ARO:3004272", child=True), R.TARGETS["ARO:3000857"])


def test_unexpected_edges_are_refused():
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("methylated", "unmodeled"))

    with pytest.raises(ValueError, match="unexpected edge methylated -> unmodeled"):
        R.enrich_record(record, R.TARGETS["ARO:3000857"])


def test_missing_expected_edges_are_refused():
    record = _record()
    record["causal_graphs"][0]["edges"].pop()

    with pytest.raises(ValueError, match="missing edge\\(s\\): methylated -> decoding_site"):
        R.enrich_record(record, R.TARGETS["ARO:3000857"])


def test_enrich_text_adds_history_once():
    target = R.TARGETS["ARO:3000857"]
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
    target = R.TARGETS["ARO:3000857"]
    enriched, changed = R.enrich_record(_record(), target)
    assert changed
    edges = enriched["causal_graphs"][0]["edges"]
    determinant_methyltransferase = next(
        edge
        for edge in edges
        if (edge["subject"], edge["object"]) == ("determinant", "methyltransferase")
    )
    methyltransferase_methylated = next(
        edge
        for edge in edges
        if (edge["subject"], edge["object"]) == ("methyltransferase", "methylated")
    )
    methyltransferase_methylated["evidence"] = determinant_methyltransferase["evidence"]
    text = yaml.safe_dump(enriched, sort_keys=False)
    assert "&id" in text
    text += "\ncuration_history:\n"
    text += "- timestamp: '2026-09-05T00:00:00Z'\n"
    text += "  curator: codex-causal-graph-quality\n"
    text += f"  action: {R.HISTORY_ACTION}\n"
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
        for graph in out["causal_graphs"]:
            if graph["graph_id"] != "resistance":
                continue
            assert ("methylated", "resistance") in {
                (edge["subject"], edge["object"]) for edge in graph["edges"]
            }
            for edge in graph["edges"]:
                assert edge["description"]
