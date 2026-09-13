from __future__ import annotations

import copy
import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_mprf_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_mprf_graphs", SCRIPT)
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
        "description": "old description",
        "evidence": [
            {
                "reference": "PMID:11342591",
                "snippet": (
                    "As this unusual modification leads to a reduced negative "
                    "charge of the membrane surface, MprF-mediated peptide resistance"
                ),
            }
        ],
    }


def _record(identifier: str = "ARO:3003421", *, drug: bool = False) -> dict:
    nodes = [
        {
            "node_id": "determinant",
            "label": "antibiotic resistant mprF",
            "node_type": "PROTEIN",
            "grounding": identifier,
        },
        {
            "node_id": "mech0",
            "label": "charge alteration conferring antibiotic resistance",
            "node_type": "MOLECULAR_FUNCTION",
            "grounding": "ARO:3003588",
        },
    ]
    edges = [
        _edge("determinant", "mech0", "participates in", "RO:0000056"),
        _edge("mech0", "resistance"),
    ]

    if drug:
        nodes.append(
            {
                "node_id": "drug0",
                "label": "peptide antibiotic",
                "node_type": "CHEMICAL",
                "grounding": "ARO:3000053",
            }
        )

    nodes.extend(
        [
            {
                "node_id": "lysyl_pg",
                "label": "lysyl-phosphatidylglycerol",
                "node_type": "CHEMICAL",
            },
            {
                "node_id": "surface_charge",
                "label": "reduced net negative charge",
                "node_type": "QUALITY",
            },
            {
                "node_id": "resistance",
                "label": "antibiotic resistance phenotype",
                "node_type": "PHENOTYPE",
                "grounding": "GO:0046677",
            },
        ]
    )
    edges.extend(
        [
            _edge("determinant", "resistance"),
            _edge("determinant", "lysyl_pg"),
            _edge("lysyl_pg", "surface_charge"),
        ]
    )

    if drug:
        edges.insert(
            2,
            _edge(
                "determinant",
                "drug0",
                "confers resistance to (drug class)",
                "ARO:2000001",
            ),
        )
        edges.append(
            _edge(
                "surface_charge",
                "drug0",
                "negatively regulates (repels the cationic peptide)",
                "RO:0002212",
            )
        )

    return {
        "identifier": identifier,
        "label": "antibiotic resistant mprF",
        "definition": (
            "Catalyzes the transfer of a lysyl group from L-lysyl-tRNA(Lys) to "
            "membrane-bound phosphatidylglycerol (PG), which produces "
            "lysylphosphatidylglycerol (LPG)."
        ),
        "causal_graphs": [{"graph_id": "resistance", "nodes": nodes, "edges": edges}],
    }


def _edge_pairs(record: dict) -> set[tuple[str, str]]:
    return {
        (edge["subject"], edge["object"])
        for edge in record["causal_graphs"][0]["edges"]
    }


def _by_node(record: dict) -> dict[str, dict]:
    return {
        node["node_id"]: node
        for node in record["causal_graphs"][0]["nodes"]
    }


def test_target_filenames_are_exactly_the_expected_mprf_records():
    assert {target.filename for target in R.TARGETS.values()} == {
        "antibiotic-resistant-mprf-aro3003421.yaml",
        "defensin-resistant-mprf-aro3000863.yaml",
        "daptomycin-resistant-mprf-aro3003091.yaml",
        "staphylococcus-aureus-mprf-aro3003769.yaml",
        "staphylococcus-aureus-mprf-with-mutation-conferring-resistance-to-daptomycin-aro3003319.yaml",
        "bacillus-subtilis-mprf-aro3003324.yaml",
        "listeria-monocytogenes-mprf-aro3003770.yaml",
        "brucella-suis-mprf-aro3003772.yaml",
        "clostridium-perfringens-mprf-aro3003773.yaml",
        "streptococcus-agalactiae-mprf-aro3003774.yaml",
    }


def test_parent_enrichment_adds_grounded_activity_product_and_terminal_resistance_edge():
    out, changed = R.enrich_record(
        _record("ARO:3003421"),
        R.TARGETS["ARO:3003421"],
    )

    assert changed
    by_node = _by_node(out)
    assert by_node["mprf_activity"] == R.MPRF_ACTIVITY_NODE
    assert by_node["lysyl_pg"] == R.LYSYL_PG_NODE
    assert by_node["surface_charge"] == R.SURFACE_CHARGE_NODE
    assert _edge_pairs(out) == {
        ("determinant", "mech0"),
        ("mech0", "resistance"),
        ("determinant", "resistance"),
        ("determinant", "mprf_activity"),
        ("mprf_activity", "lysyl_pg"),
        ("lysyl_pg", "surface_charge"),
        ("surface_charge", "resistance"),
    }


def test_drug_child_enrichment_preserves_drug_repulsion_edge():
    out, changed = R.enrich_record(
        _record("ARO:3000863", drug=True),
        R.TARGETS["ARO:3000863"],
    )

    assert changed
    assert ("surface_charge", "drug0") in _edge_pairs(out)
    assert ("surface_charge", "resistance") not in _edge_pairs(out)
    assert ("determinant", "lysyl_pg") not in _edge_pairs(out)


def test_all_edges_get_descriptions_multiple_references_and_exact_ontology_evidence():
    out, changed = R.enrich_record(
        _record("ARO:3000863", drug=True),
        R.TARGETS["ARO:3000863"],
    )

    assert changed
    graph = out["causal_graphs"][0]
    all_references = {
        item["reference"]
        for edge in graph["edges"]
        for item in edge["evidence"]
    }

    assert "GO:0050071" in all_references
    assert "RHEA:10668" in all_references
    assert "CHEBI:75792" in all_references
    assert "PMID:14769468" in all_references
    for edge in graph["edges"]:
        assert edge["description"]
        assert len({item["reference"] for item in edge["evidence"]}) > 1
        assert len(
            {
                (item["reference"], item["snippet"], item.get("notes"))
                for item in edge["evidence"]
            }
        ) == len(edge["evidence"])


def test_mutation_mechanism_edges_keep_mutation_evidence():
    record = _record("ARO:3003091", drug=True)
    record["causal_graphs"][0]["nodes"][1]["grounding"] = "ARO:3000212"

    out, changed = R.enrich_record(record, R.TARGETS["ARO:3003091"])

    assert changed
    determinant_mech = next(
        edge
        for edge in out["causal_graphs"][0]["edges"]
        if (edge["subject"], edge["object"]) == ("determinant", "mech0")
    )
    assert "ARO:3000212" in {
        item["reference"] for item in determinant_mech["evidence"]
    }


def test_enrich_record_is_idempotent():
    target = R.TARGETS["ARO:3000863"]

    once, changed = R.enrich_record(_record(target.identifier, drug=True), target)
    twice, changed_again = R.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused():
    with pytest.raises(ValueError, match="expected ARO:3003421, found ARO:3000863"):
        R.enrich_record(_record("ARO:3000863"), R.TARGETS["ARO:3003421"])


def test_unexpected_edges_are_refused():
    record = _record("ARO:3003421")
    record["causal_graphs"][0]["edges"].append(_edge("lysyl_pg", "unmodeled"))

    with pytest.raises(ValueError, match="unexpected edge lysyl_pg -> unmodeled"):
        R.enrich_record(record, R.TARGETS["ARO:3003421"])


def test_duplicate_edges_are_refused():
    record = _record("ARO:3003421")
    record["causal_graphs"][0]["edges"].append(_edge("lysyl_pg", "surface_charge"))

    with pytest.raises(ValueError, match="duplicate edge lysyl_pg -> surface_charge"):
        R.enrich_record(record, R.TARGETS["ARO:3003421"])


def test_missing_canonical_edges_are_refused():
    target = R.TARGETS["ARO:3000863"]
    out, changed = R.enrich_record(_record(target.identifier, drug=True), target)
    assert changed
    out["causal_graphs"][0]["edges"].pop()

    with pytest.raises(ValueError, match="missing edge\\(s\\): surface_charge -> drug0"):
        R.enrich_record(out, target)


def test_enrich_text_adds_history_once():
    target = R.TARGETS["ARO:3003421"]
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
    target = R.TARGETS["ARO:3003421"]
    enriched, changed = R.enrich_record(_record(), target)
    assert changed
    edges = enriched["causal_graphs"][0]["edges"]
    determinant_mech = next(
        edge for edge in edges if (edge["subject"], edge["object"]) == ("determinant", "mech0")
    )
    mech_resistance = next(
        edge for edge in edges if (edge["subject"], edge["object"]) == ("mech0", "resistance")
    )
    mech_resistance["evidence"] = determinant_mech["evidence"]
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
def test_shipped_targets_are_enriched_in_memory_without_unexpected_edges(target):
    path = ARO_DIR / target.filename
    record = yaml.safe_load(path.read_text(encoding="utf-8"))
    out, changed = R.enrich_record(copy.deepcopy(record), target)
    assert changed or out == record
