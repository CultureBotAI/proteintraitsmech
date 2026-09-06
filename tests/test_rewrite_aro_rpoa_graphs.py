from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_rpoa_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_rpoa_graphs", SCRIPT)
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
                "reference": R.PARENT_IDENTIFIER,
                "snippet": R.PARENT_EVIDENCE["snippet"],
            }
        ],
    }


def _record(identifier: str = R.PARENT_IDENTIFIER) -> dict:
    target = R.TARGETS[identifier]
    nodes = [
        {
            "node_id": "determinant",
            "label": target.identifier,
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
            "node_id": "transcription",
            "label": "transcription",
            "node_type": "BIOLOGICAL_PROCESS",
            "description": "Ungrounded: not looked up rather than guessed.",
        },
        {
            "node_id": "resistance",
            "label": "antibiotic resistance phenotype",
            "node_type": "PHENOTYPE",
            "grounding": "GO:0046677",
        },
    ]
    edges = [
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
            "transcription",
            "participates in (transcription)",
            "RO:0000056",
        ),
    ]
    if target.has_drug:
        nodes.insert(
            2,
            {
                "node_id": "drug0",
                "label": "rifamycin antibiotic",
                "node_type": "CHEMICAL",
                "grounding": "ARO:3000157",
            },
        )
        edges.insert(
            3,
            _edge(
                "determinant",
                "drug0",
                "confers resistance to (drug class)",
                "ARO:2000001",
            ),
        )

    return {
        "identifier": identifier,
        "label": "rpoA",
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
                "nodes": nodes,
                "edges": edges,
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


def test_target_set_matches_exact_rpoa_branch() -> None:
    assert {target.identifier for target in R.TARGETS.values()} == {
        "ARO:3004997",
        "ARO:3004998",
        "ARO:3004999",
    }
    assert {target.filename for target in R.TARGETS.values()} == {
        "antibiotic-resistant-rpoa-aro3004997.yaml",
        "rifampicin-resistant-rpoa-aro3004998.yaml",
        "mycobacterium-tuberculosis-rpoa-mutations-confer-resistance-to-rifampicin-aro3004999.yaml",
    }


@pytest.mark.parametrize("target", R.TARGETS.values(), ids=lambda target: target.identifier)
def test_rpoa_records_ground_transcription_without_active_center(
    target: R.Target,
) -> None:
    out, changed = R.enrich_record(_record(target.identifier), target)

    assert changed
    assert _edge_keys(out) == R._expected_edge_keys(target)
    assert _node_ids(out) == (
        ["determinant", "mech0", "drug0", "transcription", "resistance"]
        if target.has_drug
        else ["determinant", "mech0", "transcription", "resistance"]
    )
    graph = out["causal_graphs"][0]
    transcription = next(node for node in graph["nodes"] if node["node_id"] == "transcription")
    assert transcription["grounding"] == "GO:0006351"
    assert "active_center" not in yaml.safe_dump(out)


def test_all_output_edges_are_described() -> None:
    for target in R.TARGETS.values():
        out, changed = R.enrich_record(_record(target.identifier), target)

        assert changed
        graph = out["causal_graphs"][0]
        assert all(node.get("grounding") for node in graph["nodes"])
        assert all(edge.get("description") for edge in graph["edges"])


def test_drug_edges_are_multi_evidenced() -> None:
    for identifier in ("ARO:3004998", "ARO:3004999"):
        out, changed = R.enrich_record(_record(identifier), R.TARGETS[identifier])

        assert changed
        drug_edge = next(
            edge
            for edge in out["causal_graphs"][0]["edges"]
            if edge["object"] == "drug0"
        )
        assert len({item["reference"] for item in drug_edge["evidence"]}) > 1


def test_enrich_record_is_idempotent() -> None:
    target = R.TARGETS[R.PARENT_IDENTIFIER]
    once, changed = R.enrich_record(_record(target.identifier), target)
    twice, changed_again = R.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3004997, found ARO:3004998"):
        R.enrich_record(_record("ARO:3004998"), R.TARGETS["ARO:3004997"])


def test_unexpected_edges_are_refused() -> None:
    target = R.TARGETS[R.PARENT_IDENTIFIER]
    record = _record(target.identifier)
    record["causal_graphs"][0]["edges"].append(_edge("transcription", "resistance"))

    with pytest.raises(ValueError, match="unexpected edge transcription -> resistance"):
        R.enrich_record(record, target)


def test_duplicate_edges_are_refused() -> None:
    target = R.TARGETS[R.PARENT_IDENTIFIER]
    record = _record(target.identifier)
    record["causal_graphs"][0]["edges"].append(_edge("mech0", "resistance"))

    with pytest.raises(ValueError, match="duplicate edge mech0 -> resistance"):
        R.enrich_record(record, target)


def test_missing_edges_are_refused() -> None:
    target = R.TARGETS[R.PARENT_IDENTIFIER]
    record = _record(target.identifier)
    record["causal_graphs"][0]["edges"] = [
        edge
        for edge in record["causal_graphs"][0]["edges"]
        if edge["object"] != "transcription"
    ]

    with pytest.raises(ValueError, match="missing edge"):
        R.enrich_record(record, target)


def test_enrich_text_rewrites_yaml_aliases_and_adds_history_once() -> None:
    target = R.TARGETS["ARO:3004998"]
    enriched, changed = R.enrich_record(_record(target.identifier), target)
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
    out, changed = R.enrich_record(record, target)

    assert changed or out == record
    assert _edge_keys(out) == R._expected_edge_keys(target)
