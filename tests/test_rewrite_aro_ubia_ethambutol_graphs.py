from __future__ import annotations

import copy
import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_ubia_ethambutol_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location(
        "rewrite_aro_ubia_ethambutol_graphs",
        SCRIPT,
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


R = _load()


def _edge(subject: str, predicate_id: str, object_: str, evidence: list[dict] | None = None) -> dict:
    return {
        "subject": subject,
        "predicate": "seeded predicate",
        "predicate_id": predicate_id,
        "object": object_,
        "evidence": evidence or [{"reference": "ARO:3004949"}],
    }


def _graph(identifier: str, direct_antibiotic: bool = False) -> dict:
    resistance_evidence = [{"reference": identifier}]
    if direct_antibiotic:
        resistance_evidence.append(
            {
                "reference": identifier,
                "snippet": "relationship: confers_resistance_to_antibiotic ARO:3000497 ! ethambutol",
                "notes": "CARD asserts a resistance relation on this record's own ARO term.",
            }
        )

    return {
        "graph_id": "resistance-draft",
        "nodes": [
            {"node_id": "determinant"},
            {"node_id": "mech0"},
            {"node_id": "drug0"},
            {"node_id": "resistance"},
        ],
        "edges": [
            _edge("determinant", "RO:0000056", "mech0"),
            _edge("mech0", "RO:0002411", "resistance"),
            _edge("determinant", "RO:0002411", "resistance", resistance_evidence),
            _edge(
                "determinant",
                "ARO:2000001",
                "drug0",
                [
                    {
                        "reference": "ARO:3004949",
                        "snippet": (
                            "relationship: confers_resistance_to_drug_class "
                            "ARO:3000527 ! polyamine antibiotic"
                        ),
                        "notes": "Asserted directly on ARO:3004949.",
                    }
                ],
            ),
        ],
    }


def _record(identifier: str = "ARO:3004949", *, child: bool = False) -> dict:
    evidence = [
        {
            "reference": "DOI:10.1038/s41598-018-33731-1",
            "notes": "PMID:30337678 (aro citation)",
        },
        {
            "reference": "DOI:10.1016/j.tube.2018.11.006",
            "notes": "PMID:30711156 (aro citation)",
        },
    ]
    return {
        "identifier": identifier,
        "label": (
            "Mycobacterium tuberculosis ubiA mutations confer resistance to ethambutol"
            if child
            else "ethambutol resistant ubiA"
        ),
        "definition": (
            "Mutations in the ubiA gene contribute to or confer resistance to ethambutol."
            if child
            else "DDPR synthase involved in arabinogalactan synthesis. Mutations can "
            "confer resistance to ethambutol."
        ),
        "mapping_status": "SEEDED",
        "evidence": evidence if child else [],
        "causal_graphs": [_graph(identifier, direct_antibiotic=child)],
    }


def _parent_text(identifier: str = "ARO:3004948") -> str:
    return f"""identifier: {identifier}
label: antibiotic resistant ubiA
definition: DPPR synthase involved in arabinogalactan synthesis.
mapping_status: SEEDED
causal_graphs:
- graph_id: resistance-draft
  nodes:
  - node_id: determinant
    label: determinant
    node_type: PROTEIN
  edges: []
license: CC-BY 4.0
"""


def _edge_keys(record: dict) -> set[tuple[str, str, str]]:
    return {
        (edge["subject"], edge["predicate_id"], edge["object"])
        for edge in record["causal_graphs"][0]["edges"]
    }


def _history_actions(text: str) -> list[str]:
    return [
        event["action"]
        for event in yaml.safe_load(text)["curation_history"]
    ]


def test_targets_are_exact_ubia_family() -> None:
    assert {target.identifier for target in R.TARGETS} == {
        "ARO:3004948",
        "ARO:3004949",
        "ARO:3004950",
    }


def test_broad_parent_draft_graph_is_removed() -> None:
    out, changed = R.enrich_text(_parent_text(), ARO_DIR / R.BROAD_PARENT.filename)

    assert changed
    assert "causal_graphs:" not in out
    assert R.BROAD_PARENT_ACTION in _history_actions(out)


def test_parent_record_is_rewritten_as_mutation_core() -> None:
    out, changed = R.enrich_record(_record(), R.ETHAMBUTOL_PARENT)

    graph = out["causal_graphs"][0]
    assert changed
    assert out["mapping_status"] == "REVIEWED"
    assert graph["graph_id"] == "resistance"
    assert graph["description"].startswith("Conservative graph")
    assert [node["node_id"] for node in graph["nodes"]] == [
        "determinant",
        "mech0",
        "drug0",
        "resistance",
    ]
    assert _edge_keys(out) == set(R.FINAL_EDGE_ORDER)
    assert all(edge.get("description") for edge in graph["edges"])


def test_child_keeps_direct_drug_and_literature_evidence() -> None:
    out, _ = R.enrich_record(_record("ARO:3004950", child=True), R.MTUB_CHILD)

    for edge in out["causal_graphs"][0]["edges"]:
        references = {item["reference"] for item in edge["evidence"]}
        assert len(references) > 1
        assert any(item.get("snippet") for item in edge["evidence"])
        assert "ARO:3004950" in references
        assert "DOI:10.1038/s41598-018-33731-1" in references
        assert "DOI:10.1016/j.tube.2018.11.006" in references

    assert any(
        "confers_resistance_to_antibiotic ARO:3000497" in item.get("snippet", "")
        for edge in out["causal_graphs"][0]["edges"]
        for item in edge["evidence"]
    )


def test_all_parent_edges_have_snippets_and_multiple_references() -> None:
    out, _ = R.enrich_record(_record(), R.ETHAMBUTOL_PARENT)

    for edge in out["causal_graphs"][0]["edges"]:
        assert len({item["reference"] for item in edge["evidence"]}) > 1
        assert any(item.get("snippet") for item in edge["evidence"])


def test_enrich_record_is_idempotent() -> None:
    once, changed = R.enrich_record(_record(), R.ETHAMBUTOL_PARENT)
    twice, changed_again = R.enrich_record(once, R.ETHAMBUTOL_PARENT)

    assert changed
    assert not changed_again
    assert twice == once


def test_enrich_text_adds_history_once() -> None:
    text = yaml.safe_dump(_record(), sort_keys=False)
    path = ARO_DIR / R.ETHAMBUTOL_PARENT.filename

    once, changed = R.enrich_text(text, path)
    twice, changed_again = R.enrich_text(once, path)

    assert changed
    assert not changed_again
    assert once == twice
    assert _history_actions(once).count(R.GRAPH_ACTION) == 1
    assert "&id" not in once
    assert "*id" not in once


def test_identifier_mismatch_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3004949, found ARO:3004950"):
        R.enrich_record(_record("ARO:3004950", child=True), R.ETHAMBUTOL_PARENT)
    with pytest.raises(ValueError, match="expected ARO:3004948, found ARO:3004949"):
        R.enrich_text(
            _parent_text("ARO:3004949"),
            ARO_DIR / R.BROAD_PARENT.filename,
        )


def test_missing_drug_edge_is_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"] = record["causal_graphs"][0]["edges"][:3]

    with pytest.raises(ValueError, match="missing"):
        R.enrich_record(record, R.ETHAMBUTOL_PARENT)


@pytest.mark.skipif(not ARO_DIR.is_dir(), reason="ARO records absent")
def test_shipped_targets_are_rewritten_in_memory() -> None:
    for target in R.TARGETS:
        path = ARO_DIR / target.filename
        before = path.read_text(encoding="utf-8")
        after, changed = R.enrich_text(before, path)
        assert changed or after == before

        if target.remove_graph:
            assert "causal_graphs:" not in after
            assert target.action in _history_actions(after)
            continue

        record = yaml.safe_load(after)
        assert record["mapping_status"] == "REVIEWED"
        assert _edge_keys(record) == set(R.FINAL_EDGE_ORDER)

        out, changed_again = R.enrich_record(copy.deepcopy(record), target)
        assert not changed_again
        assert out == record
