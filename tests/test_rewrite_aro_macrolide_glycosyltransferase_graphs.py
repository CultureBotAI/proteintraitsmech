from __future__ import annotations

import copy
import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_macrolide_glycosyltransferase_graphs.py"


def _load():
    spec = importlib.util.spec_from_file_location(
        "rewrite_aro_macrolide_glycosyltransferase_graphs",
        SCRIPT,
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


R = _load()
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"

DEFINITION = (
    "Macrolide glycosyltransferases are enzymes encoded by macrolide "
    "glycosyltransferase genes and inactivate macrolides by glycosylating them at "
    "2'-OH of desosamine sugar moiety."
)


def _edge(subject: str, object_: str) -> dict:
    return {
        "subject": subject,
        "predicate": "causally upstream of",
        "predicate_id": "RO:0002411",
        "object": object_,
        "evidence": [
            {
                "reference": "PMID:17376874",
                "snippet": R.FAMILY_PMID_EVIDENCE["snippet"],
            }
        ],
    }


def _record(identifier: str = "ARO:3000458", *, child: bool = False) -> dict:
    nodes = [
        {
            "node_id": "determinant",
            "label": "macrolide glycosyltransferase",
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
            "label": "glycosylation of antibiotic conferring resistance",
            "node_type": "MOLECULAR_FUNCTION",
            "grounding": "ARO:3000208",
        },
        {
            "node_id": "glycosyl",
            "label": "macrolide glycosyltransferase activity",
            "node_type": "MOLECULAR_FUNCTION",
        },
        {
            "node_id": "glyco_drug",
            "label": "glycosylated (inactive) macrolide",
            "node_type": "CHEMICAL",
        },
        {
            "node_id": "ribosome_site",
            "label": "23S rRNA macrolide binding site",
            "node_type": "NUCLEIC_ACID",
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
                "label": "macrolide antibiotic",
                "node_type": "CHEMICAL",
                "grounding": "ARO:0000000",
            },
        )

    edges = [
        _edge("determinant", "mech0"),
        _edge("mech0", "resistance"),
        _edge("determinant", "mech1"),
        _edge("mech1", "resistance"),
        _edge("determinant", "resistance"),
        _edge("determinant", "glycosyl"),
        _edge("glycosyl", "glyco_drug"),
        _edge("glyco_drug", "ribosome_site"),
    ]
    if child:
        edges.insert(5, _edge("determinant", "drug0"))
        edges.append(_edge("drug0", "ribosome_site"))

    return {
        "identifier": identifier,
        "definition": DEFINITION,
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "nodes": nodes,
                "edges": edges,
            }
        ],
    }


def test_target_filenames_are_exactly_the_expected_eight():
    assert {target.filename for target in R.TARGETS.values()} == {
        "macrolide-glycosyltransferase-aro3000458.yaml",
        "gima-aro3000463.yaml",
        "gima-family-macrolide-glycosyltransferase-aro3004236.yaml",
        "mgta-aro3000462.yaml",
        "mgt-macrolide-glycotransferase-aro3004237.yaml",
        "ole-glycosyltransferase-aro3000465.yaml",
        "oled-aro3000865.yaml",
        "olei-aro3000866.yaml",
    }


def test_parent_enrichment_adds_shared_node_groundings_and_descriptions():
    out, changed = R.enrich_record(_record(), R.TARGETS["ARO:3000458"])

    assert changed
    graph = out["causal_graphs"][0]
    by_node = {node["node_id"]: node for node in graph["nodes"]}
    by_pair = {(edge["subject"], edge["object"]): edge for edge in graph["edges"]}

    assert by_node["glycosyl"] == R.SHARED_NODE_UPDATES["glycosyl"]
    assert by_node["glyco_drug"] == R.SHARED_NODE_UPDATES["glyco_drug"]
    assert by_node["ribosome_site"] == R.SHARED_NODE_UPDATES["ribosome_site"]
    assert "grounding" not in by_node["glyco_drug"]
    assert "grounding" not in by_node["ribosome_site"]
    assert len(by_pair) == len(R.PARENT_EDGES)
    for edge in graph["edges"]:
        assert edge["description"]
    assert by_pair[("determinant", "glycosyl")]["evidence"] == [
        R.FAMILY_PMID_EVIDENCE,
        {
            "reference": "ARO:3000458",
            "snippet": DEFINITION,
            "notes": "Exact ARO definition of this determinant.",
        },
        R.GO_GLYCOSYLTRANSFERASE_EVIDENCE,
    ]


def test_child_targets_allow_the_drug_class_edges():
    target = R.TARGETS["ARO:3000463"]
    out, changed = R.enrich_record(_record("ARO:3000463", child=True), target)

    assert changed
    graph = out["causal_graphs"][0]
    by_pair = {(edge["subject"], edge["object"]): edge for edge in graph["edges"]}
    assert len(by_pair) == len(R.CHILD_EDGES)
    assert by_pair[("determinant", "drug0")]["description"] == (
        R.ALL_EDGE_DESCRIPTIONS[("determinant", "drug0")]
    )
    assert by_pair[("drug0", "ribosome_site")]["description"] == (
        R.ALL_EDGE_DESCRIPTIONS[("drug0", "ribosome_site")]
    )


def test_enrich_record_is_idempotent():
    target = R.TARGETS["ARO:3000458"]

    once, changed = R.enrich_record(_record(), target)
    twice, changed_again = R.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused():
    with pytest.raises(ValueError, match="expected ARO:3000458, found ARO:3000463"):
        R.enrich_record(_record("ARO:3000463", child=True), R.TARGETS["ARO:3000458"])


def test_unexpected_edges_are_refused():
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("glyco_drug", "unmodeled"))

    with pytest.raises(ValueError, match="unexpected edge glyco_drug -> unmodeled"):
        R.enrich_record(record, R.TARGETS["ARO:3000458"])


def test_missing_expected_edges_are_refused():
    record = _record()
    record["causal_graphs"][0]["edges"].pop()

    with pytest.raises(ValueError, match="missing edge\\(s\\): glyco_drug -> ribosome_site"):
        R.enrich_record(record, R.TARGETS["ARO:3000458"])


def test_enrich_text_adds_history_once():
    target = R.TARGETS["ARO:3000458"]
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
    target = R.TARGETS["ARO:3000458"]
    enriched, changed = R.enrich_record(_record(), target)
    assert changed
    edges = enriched["causal_graphs"][0]["edges"]
    det_glycosyl = next(
        edge for edge in edges if (edge["subject"], edge["object"]) == ("determinant", "glycosyl")
    )
    glycosyl_output = next(
        edge for edge in edges if (edge["subject"], edge["object"]) == ("glycosyl", "glyco_drug")
    )
    glycosyl_output["evidence"] = det_glycosyl["evidence"]
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
        for graph in out["causal_graphs"]:
            if graph["graph_id"] != "resistance":
                continue
            for edge in graph["edges"]:
                assert edge["description"]
