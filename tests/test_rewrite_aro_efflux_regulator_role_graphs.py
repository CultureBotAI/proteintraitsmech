from __future__ import annotations

import copy
import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_efflux_regulator_role_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_efflux_regulator_role_graphs", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


R = _load()


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
                "reference": "ARO:3000702",
                "snippet": "AcrR is a repressor of the AcrAB-TolC multidrug efflux complex.",
            }
        ],
    }


def _record(identifier: str = "ARO:3000656", *, activator: bool = False) -> dict:
    regulation_node = {
        "node_id": "activation",
        "label": "activation of efflux pump expression",
        "node_type": "BIOLOGICAL_PROCESS",
    }
    regulatory_edges = [
        _edge(
            "determinant",
            "activation",
            "enables (activates the pump operon)",
            "RO:0002327",
        ),
        _edge(
            "activation",
            "pump",
            "positively regulates (raises pump expression)",
            "RO:0002213",
        ),
    ]
    if not activator:
        regulation_node = {
            "node_id": "repression",
            "label": "repression of efflux pump expression",
            "node_type": "BIOLOGICAL_PROCESS",
        }
        regulatory_edges = [
            _edge(
                "determinant",
                "repression",
                "enables (represses the pump operon)",
                "RO:0002327",
            ),
            _edge(
                "repression",
                "pump",
                "negatively regulates (holds pump expression down)",
                "RO:0002212",
            ),
            _edge(
                "determinant",
                "repression",
                "negatively regulates (mutation lifts the repression)",
                "RO:0002212",
            ),
        ]

    return {
        "identifier": identifier,
        "label": "AcrS",
        "definition": "AcrS is a repressor of the AcrAB efflux complex.",
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "description": "old graph",
                "nodes": [
                    {
                        "node_id": "determinant",
                        "label": "AcrS",
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
                    regulation_node,
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
                    *regulatory_edges,
                ],
            }
        ],
    }


def _by_node(record: dict) -> dict[str, dict]:
    return {node["node_id"]: node for node in record["causal_graphs"][0]["nodes"]}


def _edge_keys(record: dict) -> set[tuple[str, str, str]]:
    return {
        (edge["subject"], edge["predicate_id"], edge["object"])
        for edge in record["causal_graphs"][0]["edges"]
    }


def test_target_filenames_are_exactly_the_expected_leftover_regulators() -> None:
    assert {target.filename for target in R.TARGETS.values()} == {
        "acrs-aro3000656.yaml",
        "escherichia-coli-cpxr-aro3004055.yaml",
        "h-ns-aro3000676.yaml",
        "kdpe-aro3003841.yaml",
        "mgra-aro3000815.yaml",
        "nalc-aro3000818.yaml",
        "rsma-aro3005069.yaml",
        "soxrs-aro3000827.yaml",
    }


def test_repressor_archetype_is_reduced_to_grounded_efflux_role() -> None:
    target = R.TARGETS["ARO:3000656"]

    out, changed = R.enrich_record(_record(target.identifier), target)

    assert changed
    nodes = _by_node(out)
    assert set(nodes) == {"determinant", "mech0", "resistance"}
    assert nodes["mech0"] == R.MECHANISM_NODE
    assert nodes["resistance"] == R.RESISTANCE_NODE
    assert _edge_keys(out) == R.CANONICAL_EDGES
    assert out["causal_graphs"][0]["description"] == target.graph_description


def test_activator_archetype_is_reduced_to_grounded_efflux_role() -> None:
    target = R.TARGETS["ARO:3000827"]

    out, changed = R.enrich_record(_record(target.identifier, activator=True), target)

    assert changed
    assert set(_by_node(out)) == {"determinant", "mech0", "resistance"}
    assert _edge_keys(out) == R.CANONICAL_EDGES


@pytest.mark.parametrize("target", R.TARGETS.values())
def test_all_edges_get_grounded_descriptions_multi_reference_evidence(target) -> None:
    out, changed = R.enrich_record(_record(target.identifier), target)

    assert changed
    text = yaml.safe_dump(out, sort_keys=False)
    assert "node_id: pump" not in text
    assert "node_id: repression" not in text
    assert "node_id: activation" not in text
    graph = out["causal_graphs"][0]
    assert all(node.get("grounding") for node in graph["nodes"])
    for edge in graph["edges"]:
        assert edge["description"]
        assert len({item["reference"] for item in edge["evidence"]}) > 1
        assert all(item.get("snippet") for item in edge["evidence"])


def test_enrich_record_is_idempotent() -> None:
    target = R.TARGETS["ARO:3000656"]

    once, changed = R.enrich_record(_record(target.identifier), target)
    twice, changed_again = R.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3000656, found ARO:3000676"):
        R.enrich_record(_record("ARO:3000676"), R.TARGETS["ARO:3000656"])


def test_unexpected_edges_are_refused() -> None:
    record = _record("ARO:3000656")
    record["causal_graphs"][0]["edges"].append(_edge("pump", "mech0", "enables", "RO:0002327"))

    with pytest.raises(ValueError, match="unexpected edge pump -> mech0"):
        R.enrich_record(record, R.TARGETS["ARO:3000656"])


def test_duplicate_edges_are_refused() -> None:
    record = _record("ARO:3000656")
    record["causal_graphs"][0]["edges"].append(
        _edge(
            "repression",
            "pump",
            "negatively regulates (holds pump expression down)",
            "RO:0002212",
        )
    )

    with pytest.raises(ValueError, match="duplicate edge repression -> pump"):
        R.enrich_record(record, R.TARGETS["ARO:3000656"])


def test_enrich_text_rewrites_yaml_aliases_and_adds_history_once() -> None:
    target = R.TARGETS["ARO:3000656"]
    enriched, changed = R.enrich_record(_record(target.identifier), target)
    assert changed
    edges = enriched["causal_graphs"][0]["edges"]
    edges[1]["evidence"] = edges[0]["evidence"]
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


@pytest.mark.parametrize("target", R.TARGETS.values())
def test_shipped_targets_are_enriched_in_memory_without_unexpected_edges(target) -> None:
    path = ARO_DIR / target.filename
    record = yaml.safe_load(path.read_text(encoding="utf-8"))
    out, changed = R.enrich_record(copy.deepcopy(record), target)
    assert changed or out == record
