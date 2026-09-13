from __future__ import annotations

import copy
import importlib.util
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_ndh_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_ndh_graphs", SCRIPT)
    assert spec is not None
    assert isinstance(spec.loader, SourceFileLoader)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


R = _load()

LABELS = {
    "ARO:3003460": "antibiotic resistant ndh",
    "ARO:3003461": "Mycobacterium tuberculosis ndh with mutation conferring resistance to isoniazid",
    "ARO:3003778": "Mycolicibacterium smegmatis ndh with mutation conferring resistance to isoniazid",
    "ARO:3003779": (
        "Mycobacterium tuberculosis variant bovis ndh with mutation conferring "
        "resistance to isoniazid"
    ),
}


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
                "reference": R.PARENT_IDENTIFIER,
                "snippet": R.PARENT_EVIDENCE["snippet"],
            }
        ],
    }


def _old_record(identifier: str = R.PARENT_IDENTIFIER) -> dict:
    return {
        "identifier": identifier,
        "label": LABELS[identifier],
        "definition": R.PARENT_EVIDENCE["snippet"],
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
                        "label": LABELS[identifier],
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
                        "label": "isoniazid-like antibiotic",
                        "node_type": "CHEMICAL",
                        "grounding": "ARO:3007152",
                    },
                    {
                        "node_id": "nadh_ox",
                        "label": "NADH oxidase activity of ndh",
                        "node_type": "MOLECULAR_FUNCTION",
                    },
                    {
                        "node_id": "ratio",
                        "label": "raised NADH / depleted NAD+ ratio",
                        "node_type": "STATE",
                    },
                    {
                        "node_id": "peroxidation",
                        "label": "peroxidation reactions required for isoniazid activation",
                        "node_type": "BIOLOGICAL_PROCESS",
                    },
                    {
                        "node_id": "displacement",
                        "label": "displacement of the NADH-isonicotinic acyl complex",
                        "node_type": "STATE",
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
                        "drug0",
                        "confers resistance to (drug class)",
                        "ARO:2000001",
                    ),
                    _edge(
                        "determinant",
                        "nadh_ox",
                        "negatively regulates (diminishes NADH oxidation)",
                        "RO:0002212",
                    ),
                    _edge("nadh_ox", "ratio"),
                    _edge(
                        "ratio",
                        "peroxidation",
                        "negatively regulates (prevents the activating chemistry)",
                        "RO:0002212",
                    ),
                    _edge(
                        "ratio",
                        "displacement",
                        "negatively regulates (prevents the displacement)",
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


def test_target_set_matches_exact_hidden_no_ignore_ndh_branch() -> None:
    assert {target.identifier for target in R.TARGETS.values()} == set(LABELS)
    assert {target.filename for target in R.TARGETS.values()} == {
        "antibiotic-resistant-ndh-aro3003460.yaml",
        (
            "mycobacterium-tuberculosis-ndh-with-mutation-conferring-"
            "resistance-to-isoniazid-aro3003461.yaml"
        ),
        (
            "mycolicibacterium-smegmatis-ndh-with-mutation-conferring-"
            "resistance-to-isoniazid-aro3003778.yaml"
        ),
        (
            "mycobacterium-tuberculosis-variant-bovis-ndh-with-mutation-"
            "conferring-resistance-aro3003779.yaml"
        ),
    }


@pytest.mark.parametrize("identifier", sorted(LABELS))
def test_ndh_records_ground_nadh_dehydrogenase_activity(identifier: str) -> None:
    target = R.TARGETS[identifier]
    out, changed = R.enrich_record(_old_record(identifier), target)

    assert changed
    assert _node_ids(out) == [
        "determinant",
        "mech0",
        "drug0",
        "nadh_dehydrogenase",
        "diminished_activity",
        "nadh_ratio",
        "blocked_activation",
        "inha_binding",
        "resistance",
    ]
    assert _edge_keys(out) == R.EXPECTED_EDGE_KEYS
    nadh_dehydrogenase = next(
        node
        for node in out["causal_graphs"][0]["nodes"]
        if node["node_id"] == "nadh_dehydrogenase"
    )
    assert nadh_dehydrogenase["grounding"] == "GO:0003954"


def test_ndh_keeps_both_downstream_ratio_arms_separate() -> None:
    target = R.TARGETS[R.PARENT_IDENTIFIER]
    out, changed = R.enrich_record(_old_record(target.identifier), target)

    assert changed
    downstream = {
        edge["object"]
        for edge in out["causal_graphs"][0]["edges"]
        if edge["subject"] == "nadh_ratio"
    }
    assert downstream == {"blocked_activation", "inha_binding"}


def test_all_non_state_nodes_are_grounded_and_edges_described() -> None:
    for target in R.TARGETS.values():
        out, changed = R.enrich_record(_old_record(target.identifier), target)

        assert changed
        graph = out["causal_graphs"][0]
        for node in graph["nodes"]:
            if node["node_type"] != "STATE":
                assert node.get("grounding")
        assert all(edge.get("description") for edge in graph["edges"])


def test_all_output_edges_are_multi_evidenced() -> None:
    for target in R.TARGETS.values():
        out, changed = R.enrich_record(_old_record(target.identifier), target)

        assert changed
        for edge in out["causal_graphs"][0]["edges"]:
            assert len({item["reference"] for item in edge["evidence"]}) > 1


def test_nadh_edges_have_go_evidence() -> None:
    target = R.TARGETS[R.PARENT_IDENTIFIER]
    out, changed = R.enrich_record(_old_record(target.identifier), target)

    assert changed
    nadh_edges = [
        edge
        for edge in out["causal_graphs"][0]["edges"]
        if "nadh" in edge["subject"] or "nadh" in edge["object"]
    ]
    assert nadh_edges
    for edge in nadh_edges:
        assert "GO:0003954" in {item["reference"] for item in edge["evidence"]}


def test_enrich_record_is_idempotent() -> None:
    target = R.TARGETS[R.PARENT_IDENTIFIER]
    once, changed = R.enrich_record(_old_record(target.identifier), target)
    twice, changed_again = R.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3003460, found ARO:3003778"):
        R.enrich_record(_old_record("ARO:3003778"), R.TARGETS[R.PARENT_IDENTIFIER])


def test_unexpected_edges_are_refused() -> None:
    target = R.TARGETS[R.PARENT_IDENTIFIER]
    record = _old_record(target.identifier)
    record["causal_graphs"][0]["edges"].append(_edge("inha_binding", "drug0"))

    with pytest.raises(ValueError, match="unexpected edge inha_binding -> drug0"):
        R.enrich_record(record, target)


def test_duplicate_edges_are_refused() -> None:
    target = R.TARGETS[R.PARENT_IDENTIFIER]
    record = _old_record(target.identifier)
    record["causal_graphs"][0]["edges"].append(_edge("mech0", "resistance"))

    with pytest.raises(ValueError, match="duplicate edge mech0 -> resistance"):
        R.enrich_record(record, target)


def test_missing_edges_are_refused() -> None:
    target = R.TARGETS[R.PARENT_IDENTIFIER]
    record = _old_record(target.identifier)
    record["causal_graphs"][0]["edges"] = [
        edge for edge in record["causal_graphs"][0]["edges"] if edge["object"] != "drug0"
    ]

    with pytest.raises(ValueError, match="missing core edge"):
        R.enrich_record(record, target)


def test_incomplete_ndh_edge_set_is_refused() -> None:
    target = R.TARGETS[R.PARENT_IDENTIFIER]
    record = _old_record(target.identifier)
    record["causal_graphs"][0]["edges"] = [
        edge
        for edge in record["causal_graphs"][0]["edges"]
        if edge["object"] != "displacement"
    ]

    with pytest.raises(ValueError, match="incomplete ndh edge set"):
        R.enrich_record(record, target)


def test_enrich_text_rewrites_yaml_aliases_and_adds_history_once() -> None:
    target = R.TARGETS["ARO:3003461"]
    enriched, changed = R.enrich_record(_old_record(target.identifier), target)
    assert changed
    edges = enriched["causal_graphs"][0]["edges"]
    edges[1]["evidence"] = edges[0]["evidence"]
    text = yaml.safe_dump(enriched, sort_keys=False)
    assert "&id" in text

    out, changed = R.enrich_text(text, ARO_DIR / target.filename)
    again, changed_again = R.enrich_text(out, ARO_DIR / target.filename)

    assert changed
    assert not changed_again
    assert "&id" not in out
    assert "*id" not in out
    assert out.count(R.HISTORY_ACTION) == 1
    assert again == out


@pytest.mark.skipif(not ARO_DIR.is_dir(), reason="ARO records absent")
@pytest.mark.parametrize("target", R.TARGETS.values(), ids=lambda target: target.identifier)
def test_shipped_targets_are_enriched_in_memory_without_unexpected_edges(
    target: R.Target,
) -> None:
    path = ARO_DIR / target.filename
    record = yaml.safe_load(path.read_text(encoding="utf-8"))
    out, changed = R.enrich_record(copy.deepcopy(record), target)

    assert changed or out == record
    assert _edge_keys(out) == R.EXPECTED_EDGE_KEYS
