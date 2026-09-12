from __future__ import annotations

import copy
import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_vanrs_variant_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_vanrs_variant_graphs", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


R = _load()


def _edge(subject: str, object_: str, predicate: str = "causally upstream of") -> dict:
    return {
        "subject": subject,
        "predicate": predicate,
        "predicate_id": "RO:0002411",
        "object": object_,
        "evidence": [
            {
                "reference": "PMID:1556077",
                "snippet": "Synthesis of these enzymes was regulated at the transcriptional level.",
                "notes": "Existing promoted evidence.",
            }
        ],
    }


def _record(identifier: str = "ARO:3002921") -> dict:
    return {
        "identifier": identifier,
        "label": "test VanR",
        "definition": "test VanR/VanS variant definition",
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "nodes": [],
                "edges": [
                    _edge("determinant", "mech0", "participates in (resistance mechanism)"),
                    _edge("mech0", "resistance"),
                    _edge("determinant", "resistance", "causally upstream of (confers resistance)"),
                    _edge("determinant", "drug0", "confers resistance to (drug class)"),
                    _edge("transcription", "vanh_gene"),
                    _edge("vanh_gene", "resistance"),
                    _edge(
                        "determinant",
                        "family",
                        "member of (the VanR response-regulator family)",
                    ),
                    _edge("family", "activity", "enables (response-regulator phosphorelay)"),
                    _edge("activity", "transcription"),
                ],
            }
        ],
    }


def test_targets_are_exact_current_non_vana_vanrs_records() -> None:
    assert {target.identifier for target in R.TARGETS} == {
        "ARO:3002921",
        "ARO:3002922",
        "ARO:3002923",
        "ARO:3002924",
        "ARO:3002925",
        "ARO:3002926",
        "ARO:3002927",
        "ARO:3002928",
        "ARO:3002929",
        "ARO:3002930",
        "ARO:3003728",
        "ARO:3007191",
        "ARO:3002932",
        "ARO:3002933",
        "ARO:3002934",
        "ARO:3002935",
        "ARO:3002936",
        "ARO:3002937",
        "ARO:3002938",
        "ARO:3002939",
        "ARO:3002940",
        "ARO:3002941",
        "ARO:3003726",
        "ARO:3007192",
    }


def test_enrich_record_describes_and_multi_evidences_all_edges() -> None:
    out, changed = R.enrich_record(_record(), R.TARGETS[0])

    assert changed
    for edge in out["causal_graphs"][0]["edges"]:
        assert edge["description"]
        assert len({item["reference"] for item in edge["evidence"]}) > 1


def test_vans_partner_edge_is_supported() -> None:
    record = _record("ARO:3002932")
    record["causal_graphs"][0]["edges"][-1] = _edge(
        "activity",
        "vanr_protein",
        "positively regulates (phosphorylates the partner regulator)",
    )
    record["causal_graphs"][0]["edges"].append(
        _edge("vanr_protein", "transcription", "causally upstream of (activates the promoter)")
    )

    out, changed = R.enrich_record(record, R.TARGETS[12])

    assert changed
    by_pair = {
        (edge["subject"], edge["object"]): edge
        for edge in out["causal_graphs"][0]["edges"]
    }
    assert "VanS kinase activity controls" in by_pair[("activity", "vanr_protein")]["description"]
    assert "VanR activates transcription" in by_pair[("vanr_protein", "transcription")]["description"]


def test_enrich_record_is_idempotent() -> None:
    once, changed = R.enrich_record(_record(), R.TARGETS[0])
    twice, changed_again = R.enrich_record(once, R.TARGETS[0])

    assert changed
    assert not changed_again
    assert twice == once


def test_enrich_text_adds_history_once() -> None:
    text = yaml.safe_dump(_record(), sort_keys=False)
    path = ARO_DIR / R.TARGETS[0].filename

    once, changed = R.enrich_text(text, path)
    twice, changed_again = R.enrich_text(once, path)

    assert changed
    assert not changed_again
    assert once == twice
    assert once.count(R.HISTORY_CURATOR) == 1
    assert "&id" not in once
    assert "*id" not in once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3002921, found ARO:3002932"):
        R.enrich_record(_record("ARO:3002932"), R.TARGETS[0])


def test_too_few_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"] = record["causal_graphs"][0]["edges"][:3]

    with pytest.raises(ValueError, match="graph has too few VanR/VanS edges"):
        R.enrich_record(record, R.TARGETS[0])


@pytest.mark.skipif(not ARO_DIR.is_dir(), reason="ARO records absent")
def test_all_shipped_targets_are_rewritten_in_memory() -> None:
    for target in R.TARGETS:
        path = ARO_DIR / target.filename
        record = yaml.safe_load(path.read_text(encoding="utf-8"))

        out, changed = R.enrich_record(copy.deepcopy(record), target)

        assert changed or out == record
        for edge in out["causal_graphs"][0]["edges"]:
            assert edge.get("description")
            assert len({item["reference"] for item in edge["evidence"]}) > 1
