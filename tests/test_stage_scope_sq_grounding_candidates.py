"""Adversarial tests for staging SCOPe ``! SQ`` comments."""

from __future__ import annotations

import hashlib
import importlib
import json
import shutil
import os
import sys
from pathlib import Path
from typing import Any

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
stage = importlib.import_module("stage_scope_sq_grounding_candidates")


def _header(kind: str, version: str) -> str:
    return (
        f"# dir.{kind}.scope.txt\n"
        "# SCOPe release 2.08 (2021-07-29)  "
        f"[File format version {version}]\n"
        "# http://scop.berkeley.edu/\n"
        "# Copyright (c) 1994-2021 the SCOP and SCOPe authors; "
        "see http://scop.berkeley.edu/about\n"
    )


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _trait_body(
    sunid: str,
    level: str,
    sccs: str,
    parent: str | None,
) -> str:
    lines = [
        f"identifier: SCOP:{sunid}",
        f'label: "Fixture {level} {sunid}"',
        f"definition: Fixture SCOPe {level} node.",
        'definition_source: "SCOPe 2.08-stable"',
        "trait_axis: STRUCTURE",
        f"trait_category: {stage.LEVEL_TO_CATEGORY[level]}",
        "term_kind: CLASS",
        "mapping_status: SEEDED",
    ]
    if parent is not None:
        lines.extend(("parent_traits:", f"  - SCOP:{parent}"))
    lines.extend(("xrefs:", f"  - SCOP:{sccs}", "license: CC-BY 4.0"))
    return "\n".join(lines) + "\n"


def _registry_row(accession: str = "P12345", sequence: str = "ACDEFGHIKL") -> dict[str, Any]:
    return {
        "protein_id": f"UniProtKB:{accession}",
        "protein_label": f"Fixture {accession}",
        "reviewed": True,
        "sequence": sequence,
        "sequence_length": len(sequence),
        "sequence_sha256": hashlib.sha256(sequence.encode("ascii")).hexdigest(),
        "sequence_version": 1,
        "taxon_id": "NCBITaxon:9606",
        "taxon_label": "Homo sapiens",
        "uniprot_release": "2026_02",
    }


def _write_registry(path: Path, rows: list[dict[str, Any]]) -> None:
    _write(path, "".join(stage.canonical_json(row) + "\n" for row in rows))


def _case(
    tmp_path: Path,
    *,
    comments: list[tuple[str, str]] | None = None,
    extra_nodes: list[tuple[str, str, str, str, str]] | None = None,
    extra_parents: dict[str, str] | None = None,
    registry_rows: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    repo = tmp_path / "repo"
    raw = repo / "data/raw/scope"
    traits = repo / "data/traits"
    descriptions = raw / "dir.des.scope.2.08-stable.txt"
    hierarchy = raw / "dir.hie.scope.2.08-stable.txt"
    comment_path = raw / "dir.com.scope.2.08-stable.txt"
    registry = repo / "registry.jsonl"

    nodes = [
        ("1", "cl", "a", "-", "Fixture class"),
        ("2", "cf", "a.1", "-", "Fixture fold"),
        ("3", "sf", "a.1.1", "-", "Fixture superfamily"),
        ("4", "fa", "a.1.1.1", "-", "Fixture family"),
        ("5", "dm", "a.1.1.1", "-", "Fixture domain"),
        ("6", "sp", "a.1.1.1", "-", "Fixture species [TaxId: 9606]"),
    ]
    nodes.extend(extra_nodes or [])
    parents = {"1": "0", "2": "1", "3": "2", "4": "3", "5": "4", "6": "5"}
    parents.update(extra_parents or {})
    children: dict[str, list[str]] = {"0": []}
    for sunid, *_ in nodes:
        children[sunid] = []
    for child, parent in parents.items():
        children.setdefault(parent, []).append(child)

    _write(
        descriptions,
        _header("des", "1.02") + "".join("\t".join(node) + "\n" for node in nodes),
    )
    hierarchy_rows = [("0", "-", ",".join(children["0"]) or "-")]
    for sunid, *_ in nodes:
        hierarchy_rows.append((sunid, parents[sunid], ",".join(children[sunid]) or "-"))
    _write(
        hierarchy,
        _header("hie", "1.01") + "".join("\t".join(row) + "\n" for row in hierarchy_rows),
    )
    comment_rows = comments if comments is not None else [("6", "SQ P12345 2-5")]
    _write(
        comment_path,
        _header("com", "1.01") + "".join(f"{sunid} ! {text}\n" for sunid, text in comment_rows),
    )

    by_id = {node[0]: node for node in nodes}
    for sunid, parent in parents.items():
        node = by_id[sunid]
        level, sccs = node[1], node[2]
        if level not in stage.MODELED_LEVELS:
            continue
        route = traits / stage.LEVEL_TO_ROUTE[level]
        _write(
            route / f"fixture-{level}-sunid{sunid}.yaml",
            _trait_body(sunid, level, sccs, None if level == "cl" else parent),
        )
    # All four exact route directories must exist, even in tiny fixtures.
    for route in set(stage.LEVEL_TO_ROUTE.values()):
        (traits / route).mkdir(parents=True, exist_ok=True)
    _write_registry(registry, registry_rows if registry_rows is not None else [_registry_row()])
    pins = {
        "comments": hashlib.sha256(comment_path.read_bytes()).hexdigest(),
        "descriptions": hashlib.sha256(descriptions.read_bytes()).hexdigest(),
        "hierarchy": hashlib.sha256(hierarchy.read_bytes()).hexdigest(),
    }
    return {
        "repo": repo,
        "comments": comment_path,
        "descriptions": descriptions,
        "hierarchy": hierarchy,
        "traits": traits,
        "registries": [registry],
        "registry_pin": hashlib.sha256(registry.read_bytes()).hexdigest(),
        "pins": pins,
    }


def _build(case: dict[str, Any]) -> stage.StageResult:
    return stage.build_stage(
        comments_path=case["comments"],
        descriptions_path=case["descriptions"],
        hierarchy_path=case["hierarchy"],
        traits_root=case["traits"],
        protein_registry_path=case["registries"][0],
        repo_root=case["repo"],
        expected_source_sha256=case["pins"],
        expected_protein_registry_sha256=case["registry_pin"],
    )


def _repin_registry(case: dict[str, Any]) -> None:
    case["registry_pin"] = hashlib.sha256(case["registries"][0].read_bytes()).hexdigest()


def _assert_address(row: dict[str, Any], *, id_field: str, prefix: str, hash_field: str) -> None:
    without_hash = dict(row)
    observed_hash = without_hash.pop(hash_field)
    assert observed_hash == stage.value_sha256(without_hash)
    observed_id = without_hash.pop(id_field)
    assert observed_id == prefix + stage.value_sha256(without_hash)


def _assert_derivation_artifacts(row: dict[str, Any], case: dict[str, Any]) -> None:
    observed = {item["kind"]: item for item in row["derivation_source_artifacts"]}
    assert set(observed) == {"comments", "descriptions", "hierarchy"}
    for kind in observed:
        assert observed[kind]["sha256"] == case["pins"][kind]
        assert observed[kind]["path"] == case[kind].relative_to(case["repo"]).as_posix()


def test_exact_sq_mapping_expands_to_five_traits_and_binds_registry(tmp_path: Path) -> None:
    case = _case(tmp_path)
    result = _build(case)
    assert len(result.candidates) == 5
    assert result.blocked_clauses == ()
    assert result.blocked_out_of_bounds == ()
    assert result.blocked_taxon_conflicts == ()
    assert result.protein_requests == ()
    assert {row["trait_id"] for row in result.candidates} == {
        "SCOP:1",
        "SCOP:2",
        "SCOP:3",
        "SCOP:4",
        "SCOP:5",
    }
    for row in result.candidates:
        assert row["schema_version"] == 3
        assert row["candidate_status"] == stage.READY_LOCAL_REFERENCE
        assert (
            row["candidate_status_basis"]
            == "LOCAL_PROTEIN_REGISTRY_AVAILABILITY_ONLY_NOT_MAPPING_REVIEW_READINESS"
        )
        assert row["source_species_taxon_ids"] == ["NCBITaxon:9606"]
        assert row["source_registry_taxon_review_status"] == "EXACT_TAXON_MATCH"
        assert row["qualification_status"] == "CANDIDATE_PROTEIN"
        assert row["staging_reason"] == stage.STAGING_REASON
        assert row["coordinate_frame"] == "UNIPROT_CANONICAL"
        assert row["intervals"] == [{"start": 2, "end": 5}]
        assert row["mapping_method"] == "SOURCE_NATIVE_COORDINATES"
        assert row["qualification_mapping_method_required"] == "SIFTS_RESIDUE_MAPPING"
        assert row["evidence_source"] == "SCOPe"
        assert row["missing_receipts"] == list(stage.MISSING_RECEIPTS)
        assert set(stage.GLOBAL_PROMOTION_BLOCKERS) <= set(row["promotion_blockers"])
        assert row["grounding_evidence_emitted"] is False
        assert row["network_action_performed"] is False
        assert row["write_action_performed"] is False
        assert row["sequence_length"] == 10
        assert row["protein_reference_binding"]["status"] == (
            "EXACT_LOCAL_PROTEIN_REFERENCE_PRESENT"
        )
        assert (
            row["protein_reference_binding"]["protein_registry_artifact"]["sha256"]
            == (case["registry_pin"])
        )
        assertion = row["source_assertions"][0]
        assert [item["level"] for item in assertion["hierarchy_path"]] == [
            "sp",
            "dm",
            "fa",
            "sf",
            "cf",
            "cl",
        ]
        assert assertion["source_node_description"] == "Fixture species [TaxId: 9606]"
        assert assertion["source_field_index"] == 1
        assert assertion["source_segment_index"] == 1
        assert assertion["source_marker_kind"] == "EXACT_PROVIDER_FIELD"
        assert assertion["source_segment"] == "SQ P12345 2-5"
        assert assertion["source_segment_sha256"] == hashlib.sha256(b"SQ P12345 2-5").hexdigest()
        assert (
            assertion["source_segment_sha256_basis"]
            == "EXACT_UTF8_BANG_DELIMITED_COMMENT_FIELD_AFTER_ASCII_SPACE_TAB_TRIM"
        )
        _assert_derivation_artifacts(row, case)
        _assert_address(
            row,
            id_field="candidate_id",
            prefix="scope-sq-grounding-candidate:",
            hash_field="candidate_row_sha256",
        )
    assert result.summary["prospective_candidate_projection_count"] == 5
    assert result.summary["unique_prospective_candidate_projection_count"] == 5
    assert result.summary["ready_local_reference_candidate_count"] == 5
    assert result.summary["scope_trait_record_count"] == 5
    assert result.summary["schema_version"] == 3
    without_stage_id = dict(result.summary)
    observed_summary_hash = without_stage_id.pop("summary_row_sha256")
    assert observed_summary_hash == stage.value_sha256(without_stage_id)
    observed_stage_id = without_stage_id.pop("stage_id")
    assert observed_stage_id == "scope-sq-grounding-stage:" + stage.value_sha256(without_stage_id)


def test_duplicate_semantic_projections_retain_both_exact_assertions(tmp_path: Path) -> None:
    case = _case(
        tmp_path,
        comments=[("6", "SQ P12345 2-5"), ("7", "SQ P12345 2-5")],
        extra_nodes=[("7", "sp", "a.1.1.1", "-", "Second species [TaxId: 10090]")],
        extra_parents={"7": "5"},
    )
    result = _build(case)
    assert len(result.candidates) == 5
    assert result.summary["admitted_sq_clause_count"] == 2
    assert result.summary["unique_admitted_occurrence_count"] == 2
    assert result.summary["prospective_candidate_projection_count"] == 10
    assert result.summary["unique_prospective_candidate_projection_count"] == 5
    assert all(len(row["source_assertions"]) == 2 for row in result.candidates)
    assert {
        assertion["source_node_id"] for assertion in result.candidates[0]["source_assertions"]
    } == {"SCOP:6", "SCOP:7"}


def test_taxon_pair_candidate_count_deduplicates_merged_source_assertions(
    tmp_path: Path,
) -> None:
    case = _case(
        tmp_path,
        comments=[("7", "SQ P12345 2-5"), ("8", "SQ P12345 2-5")],
        extra_nodes=[
            ("7", "sp", "a.1.1.1", "-", "Mouse one [TaxId: 10090]"),
            ("8", "sp", "a.1.1.1", "-", "Mouse two [TaxId: 10090]"),
        ],
        extra_parents={"7": "5", "8": "5"},
    )
    result = _build(case)
    assert len(result.candidates) == 5
    assert all(len(row["source_assertions"]) == 2 for row in result.candidates)
    assert result.summary["ready_local_reference_unresolved_taxon_mismatch_candidate_count"] == 5
    assert result.summary["ready_local_reference_taxon_mismatch_pair_counts"] == [
        {
            "source_taxon_id": "NCBITaxon:10090",
            "registry_taxon_id": "NCBITaxon:9606",
            "candidate_count": 5,
        }
    ]


@pytest.mark.parametrize(
    ("segment", "required_reason"),
    [
        ("SQ P12345", "NO_EXACT_SINGLE_RANGE"),
        ("SQ P12345 Q12345 2-5", "MULTIPLE_UNIPROT_ACCESSIONS"),
        ("SQ P12345 2-5,7-9", "MULTIPLE_RANGES"),
        ("SQ NA 2-5", "NO_EXACT_UNIPROT_ACCESSION"),
        ("SQ P12345 RE 2-5", "INVALID_SQ_CLAUSE_SYNTAX"),
        ("SQ P12345 2-5; 7-9", "MULTIPLE_RANGES"),
        ("SQ P12345 2-5; Q12345 7-9", "MULTIPLE_UNIPROT_ACCESSIONS"),
        ("SQ P12345 9-2", "INVALID_REVERSED_RANGE"),
        ("annotation SQ P12345 2-5", "INVALID_SQ_FIELD"),
    ],
)
def test_mini_grammar_blocks_missing_multiple_and_invalid_claims(
    segment: str, required_reason: str
) -> None:
    _, _, _, reasons = stage.parse_sq_segment(segment)
    assert required_reason in reasons


def test_provider_comment_suffix_is_not_misread_as_another_claim() -> None:
    accession, start, end, reasons = stage.parse_sq_segment(
        "SQ P12345 2-5 # another known structure covers 7-9"
    )
    assert (accession, start, end, reasons) == ("P12345", 2, 5, ())
    assert stage.parse_sq_segment("SQ P12345 2-5; descriptive annotation 7-9")[3] == ()


def test_every_clause_is_emitted_and_non_species_exception_is_blocked(tmp_path: Path) -> None:
    case = _case(
        tmp_path,
        comments=[
            ("6", "SQ P12345 2-5 ! SQ P12345"),
            ("5", "SQ P12345 2-5"),
        ],
    )
    result = _build(case)
    assert result.summary["total_sq_clause_count"] == 3
    assert result.summary["admitted_sq_clause_count"] == 1
    assert result.summary["blocked_sq_clause_count"] == 2
    assert any("NO_EXACT_SINGLE_RANGE" in row["blocking_reasons"] for row in result.blocked_clauses)
    exception = next(
        row
        for row in result.blocked_clauses
        if "SOURCE_NODE_LEVEL_NOT_SP" in row["blocking_reasons"]
    )
    assert exception["source_node_id"] == "SCOP:5"
    assert exception["source_node_description"] == "Fixture domain"
    _assert_derivation_artifacts(exception, case)
    _assert_address(
        exception,
        id_field="blocked_clause_id",
        prefix="scope-sq-blocked-clause:",
        hash_field="blocked_clause_row_sha256",
    )


def test_bang_columns_are_whitespace_independent_and_prose_sq_is_diagnostic(
    tmp_path: Path,
) -> None:
    case = _case(
        tmp_path,
        comments=[
            (
                "6",
                "SQ P12345 2-5!SQ P12345 6-9 # related prose (SQ Q12345 1-2)",
            )
        ],
    )
    result = _build(case)
    assert len(result.candidates) == 10
    assert result.summary["exact_sq_clause_count"] == 2
    assert result.summary["total_sq_clause_count"] == 2
    assert result.summary["unmarked_sq_text_count"] == 1
    assert result.summary["total_sq_like_token_count"] == 3
    assert result.blocked_clauses == ()
    assert {row["intervals"][0]["start"] for row in result.candidates} == {2, 6}
    assertions = result.candidates[0]["source_assertions"]
    assert assertions[0]["source_field_index"] in {1, 2}
    assert all(item["source_marker_kind"] == "EXACT_PROVIDER_FIELD" for item in assertions)
    assert len(result.unmarked_sq_diagnostics) == 1
    diagnostic = result.unmarked_sq_diagnostics[0]
    assert diagnostic["kind"] == stage.UNMARKED_SQ_DIAGNOSTIC_KIND
    assert diagnostic["diagnostic_status"] == "NOT_A_PROVIDER_SQ_FIELD"
    assert diagnostic["source_field_index"] == 2
    assert diagnostic["source_segment"] == ("SQ P12345 6-9 # related prose (SQ Q12345 1-2)")
    _assert_derivation_artifacts(diagnostic, case)
    _assert_address(
        diagnostic,
        id_field="diagnostic_id",
        prefix="scope-unmarked-sq-diagnostic:",
        hash_field="diagnostic_row_sha256",
    )


@pytest.mark.parametrize(
    "fields",
    [
        "SQ P12345 2-5!SQ P12345 6-9",
        "SQ P12345 2-5 !   SQ P12345 6-9",
        "\tSQ P12345 2-5\t!\tSQ P12345 6-9\t",
    ],
)
def test_bang_delimiter_spacing_does_not_change_field_semantics(
    tmp_path: Path, fields: str
) -> None:
    case = _case(tmp_path, comments=[("6", fields)])
    result = _build(case)
    assert len(result.candidates) == 10
    assert result.blocked_clauses == ()
    assert result.summary["exact_sq_clause_count"] == 2
    assert result.summary["admitted_sq_clause_count"] == 2
    assert {row["intervals"][0]["start"] for row in result.candidates} == {2, 6}


def test_local_out_of_bounds_is_one_blocked_assertion_with_five_projections(
    tmp_path: Path,
) -> None:
    case = _case(tmp_path, comments=[("6", "SQ P12345 2-11")])
    result = _build(case)
    assert result.candidates == ()
    assert len(result.blocked_out_of_bounds) == 1
    blocked = result.blocked_out_of_bounds[0]
    assert blocked["candidate_status"] == "BLOCKED_OUT_OF_BOUNDS"
    assert blocked["qualification_status"] == "CANDIDATE_PROTEIN"
    assert len(blocked["affected_trait_projections"]) == 5
    assert {item["trait_id"] for item in blocked["affected_trait_projections"]} == {
        "SCOP:1",
        "SCOP:2",
        "SCOP:3",
        "SCOP:4",
        "SCOP:5",
    }
    assert result.summary["unique_prospective_candidate_projection_count"] == 5
    assert result.summary["candidate_count"] == 0
    assert result.summary["blocked_out_of_bounds_source_assertion_count"] == 1
    assert result.summary["blocked_out_of_bounds_affected_projection_count"] == 5
    _assert_derivation_artifacts(blocked, case)
    _assert_address(
        blocked,
        id_field="blocked_out_of_bounds_id",
        prefix="scope-sq-blocked-out-of-bounds:",
        hash_field="blocked_out_of_bounds_row_sha256",
    )


def test_missing_registry_reference_remains_candidate_without_sequence_claim(
    tmp_path: Path,
) -> None:
    case = _case(tmp_path, registry_rows=[_registry_row("Q12345")])
    result = _build(case)
    assert len(result.candidates) == 5
    assert all(
        row["candidate_status"] == "MISSING_LOCAL_PROTEIN_REFERENCE" for row in result.candidates
    )
    assert all("sequence_sha256" not in row for row in result.candidates)
    assert all(
        row["source_registry_taxon_review_status"] == "NOT_COMPARED_MISSING_LOCAL_REFERENCE"
        for row in result.candidates
    )
    assert all(
        row["protein_reference_binding"] == result.protein_requests[0]["protein_reference_binding"]
        for row in result.candidates
    )
    assert result.candidates[0]["protein_reference_binding"] == {
        "status": "MISSING_EXACT_PROTEIN_REFERENCE",
        "protein_registry_artifact": {
            "path": case["registries"][0].relative_to(case["repo"]).as_posix(),
            "sha256": case["registry_pin"],
            "size_bytes": len(case["registries"][0].read_bytes()),
        },
        "expected_uniprot_release": stage.EXPECTED_UNIPROT_RELEASE,
        "fetch_receipt_verification_status": "NOT_VERIFIED_BY_THIS_STAGE",
    }
    assert len(result.protein_requests) == 1
    request = result.protein_requests[0]
    assert request["protein_id"] == "UniProtKB:P12345"
    assert request["source_candidate_count"] == 5
    assert request["trait_count"] == 5
    assert request["source_assertion_count"] == 1
    assert request["maximum_source_coordinate"] == 5
    assert request["request_reason"] == stage.MISSING_PROTEIN_REFERENCE
    assert request["source_candidate_ids"] == sorted(
        row["candidate_id"] for row in result.candidates
    )
    assert request["grounding_evidence_emitted"] is False
    _assert_address(
        request,
        id_field="request_id",
        prefix="scope-sq-protein-request:",
        hash_field="request_row_sha256",
    )
    assert result.summary["protein_reference_request_count"] == 1


def test_missing_reference_request_aggregates_multiple_intervals_without_duplicates(
    tmp_path: Path,
) -> None:
    case = _case(
        tmp_path,
        comments=[("6", "SQ P12345 2-5 ! SQ P12345 6-9")],
        registry_rows=[_registry_row("Q12345")],
    )
    result = _build(case)

    assert len(result.candidates) == 10
    assert len(result.protein_requests) == 1
    request = result.protein_requests[0]
    assert request["source_candidate_count"] == 10
    assert request["trait_count"] == 5
    assert request["source_assertion_count"] == 2
    assert request["maximum_source_coordinate"] == 9
    assert {(item["start"], item["end"]) for item in request["source_assertion_bindings"]} == {
        (2, 5),
        (6, 9),
    }


def test_taxon_mismatch_is_exposed_without_inferred_lineage_compatibility(
    tmp_path: Path,
) -> None:
    case = _case(tmp_path)
    text = case["descriptions"].read_text().replace("TaxId: 9606", "TaxId: 10090")
    case["descriptions"].write_text(text, encoding="utf-8")
    case["pins"]["descriptions"] = hashlib.sha256(case["descriptions"].read_bytes()).hexdigest()
    result = _build(case)
    assert len(result.candidates) == 5
    assert all(
        row["source_registry_taxon_review_status"]
        == "UNRESOLVED_TAXON_MISMATCH_REQUIRES_LINEAGE_REVIEW"
        for row in result.candidates
    )
    assert result.summary["ready_local_reference_unresolved_taxon_mismatch_candidate_count"] == 5


def test_observed_bovine_source_human_p00734_conflict_is_blocked_once(
    tmp_path: Path,
) -> None:
    case = _case(
        tmp_path,
        comments=[("50533", "SQ P00734 333-622")],
        extra_nodes=[("50533", "sp", "a.1.1.1", "-", "Cow (Bos taurus) [TaxId: 9913]")],
        extra_parents={"50533": "5"},
        registry_rows=[_registry_row("P00734", "A" * 622)],
    )
    result = _build(case)
    assert result.candidates == ()
    assert len(result.blocked_taxon_conflicts) == 1
    blocked = result.blocked_taxon_conflicts[0]
    assert blocked["candidate_status"] == stage.BLOCKED_SOURCE_REGISTRY_TAXON_CONFLICT
    assert blocked["qualification_status"] == "CANDIDATE_PROTEIN"
    assert blocked["source_node_id"] == "SCOP:50533"
    assert blocked["source_species_taxon_id"] == "NCBITaxon:9913"
    assert blocked["taxon_id"] == "NCBITaxon:9606"
    assert blocked["protein_id"] == "UniProtKB:P00734"
    assert blocked["intervals"] == [{"start": 333, "end": 622}]
    assert len(blocked["affected_trait_projections"]) == 5
    assert result.summary["blocked_taxon_conflict_source_assertion_count"] == 1
    assert result.summary["blocked_taxon_conflict_affected_projection_count"] == 5
    assert result.summary["local_registry_available_projection_count"] == 5
    assert (
        "INCLUDING_BLOCKED_OOB_AND_TAXON_CONFLICT"
        in result.summary["local_registry_available_projection_semantics"]
    )
    _assert_derivation_artifacts(blocked, case)
    _assert_address(
        blocked,
        id_field="blocked_taxon_conflict_id",
        prefix="scope-sq-blocked-taxon-conflict:",
        hash_field="blocked_taxon_conflict_row_sha256",
    )


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda row: {**row, "uniprot_release": "2026_01"}, "release 2026_02"),
        (lambda row: {**row, "sequence_length": 99}, "length does not match"),
        (lambda row: {**row, "sequence_sha256": "0" * 64}, "sha256 does not match"),
        (lambda row: {**row, "unexpected": 1}, "schema mismatch"),
    ],
)
def test_registry_contract_is_exact_and_fail_closed(
    tmp_path: Path, mutation: Any, message: str
) -> None:
    case = _case(tmp_path, registry_rows=[mutation(_registry_row())])
    with pytest.raises(stage.ScopeSqStageError, match=message):
        _build(case)


def test_registry_collision_and_duplicate_input_paths_are_refused(tmp_path: Path) -> None:
    case = _case(tmp_path)
    second = case["repo"] / "second.jsonl"
    conflicting = _registry_row()
    conflicting["protein_label"] = "Conflicting label"
    _write_registry(second, [conflicting])
    case["registries"].append(second)
    with pytest.raises(stage.ScopeSqStageError, match="conflicting protein registry collision"):
        stage.load_protein_registries(case["registries"], repo_root=case["repo"])

    case["registries"] = [case["registries"][0], case["registries"][0]]
    with pytest.raises(stage.ScopeSqStageError, match="duplicate explicit protein registry path"):
        stage.load_protein_registries(case["registries"], repo_root=case["repo"])


def test_registry_input_order_is_normalized_before_capture(tmp_path: Path) -> None:
    case = _case(tmp_path)
    second = case["repo"] / "z-second.jsonl"
    _write_registry(second, [_registry_row()])
    case["registries"].append(second)
    forward_references, forward_artifacts = stage.load_protein_registries(
        case["registries"], repo_root=case["repo"]
    )
    case["registries"].reverse()
    reverse_references, reverse_artifacts = stage.load_protein_registries(
        case["registries"], repo_root=case["repo"]
    )
    assert forward_references == reverse_references
    assert forward_artifacts == reverse_artifacts
    assert [item.relative_path for item in forward_artifacts] == sorted(
        item.relative_path for item in forward_artifacts
    )


def test_build_requires_the_exact_single_registry_pin(tmp_path: Path) -> None:
    case = _case(tmp_path)
    case["registry_pin"] = "0" * 64

    with pytest.raises(stage.ScopeSqStageError, match="sha256 mismatch"):
        _build(case)


def test_missing_rows_bind_the_exact_registry_that_established_absence(tmp_path: Path) -> None:
    case = _case(tmp_path, registry_rows=[_registry_row("Q12345")])
    first = _build(case)

    _write_registry(case["registries"][0], [_registry_row("Q67890")])
    _repin_registry(case)
    second = _build(case)

    assert first.summary["stage_id"] != second.summary["stage_id"]
    assert [row["candidate_id"] for row in first.candidates] != [
        row["candidate_id"] for row in second.candidates
    ]
    assert [row["request_id"] for row in first.protein_requests] != [
        row["request_id"] for row in second.protein_requests
    ]
    assert (
        first.candidates[0]["protein_reference_binding"]["protein_registry_artifact"]["sha256"]
        != second.candidates[0]["protein_reference_binding"]["protein_registry_artifact"]["sha256"]
    )


def test_registry_json_must_be_canonical_and_have_no_duplicate_keys(tmp_path: Path) -> None:
    case = _case(tmp_path)
    registry = case["registries"][0]
    registry.write_text(json.dumps(_registry_row(), sort_keys=True) + "\n", encoding="utf-8")
    with pytest.raises(stage.ScopeSqStageError, match="not exact canonical JSON"):
        _build(case)

    row = stage.canonical_json(_registry_row())
    registry.write_text(row[:-1] + ',"protein_id":"UniProtKB:P12345"}\n', encoding="utf-8")
    with pytest.raises(stage.ScopeSqStageError, match="duplicate key"):
        _build(case)


def test_headers_pins_hierarchy_and_trait_routes_are_strict(tmp_path: Path) -> None:
    case = _case(tmp_path)
    case["pins"]["comments"] = "0" * 64
    with pytest.raises(stage.ScopeSqStageError, match="sha256 mismatch"):
        _build(case)

    case = _case(tmp_path / "missing-pin")
    del case["pins"]["comments"]
    with pytest.raises(stage.ScopeSqStageError, match="must contain exactly"):
        _build(case)

    case = _case(tmp_path / "header")
    text = case["comments"].read_text().replace("2021-07-29", "2021-07-30")
    case["comments"].write_text(text, encoding="utf-8")
    case["pins"]["comments"] = hashlib.sha256(case["comments"].read_bytes()).hexdigest()
    with pytest.raises(stage.ScopeSqStageError, match="must be release 2.08 dated"):
        _build(case)

    case = _case(tmp_path / "trait")
    trait = case["traits"] / stage.LEVEL_TO_ROUTE["dm"] / "fixture-dm-sunid5.yaml"
    trait.write_text(trait.read_text().replace("STRUCT_DOMAIN", "STRUCT_FOLD"), encoding="utf-8")
    with pytest.raises(stage.ScopeSqStageError, match="trait contract mismatch"):
        _build(case)

    case = _case(tmp_path / "hierarchy")
    text = case["hierarchy"].read_text().replace("5\t4\t6", "5\t3\t6")
    case["hierarchy"].write_text(text, encoding="utf-8")
    case["pins"]["hierarchy"] = hashlib.sha256(case["hierarchy"].read_bytes()).hexdigest()
    with pytest.raises(stage.ScopeSqStageError, match="level transition|inverse child list"):
        _build(case)

    case = _case(tmp_path / "shadow")
    shadow = case["traits"] / "function/protein_family/shadow.yaml"
    _write(shadow, 'identifier: "\\x53COP:5"\n')
    with pytest.raises(stage.ScopeSqStageError, match="outside its exact dm route"):
        _build(case)

    case = _case(tmp_path / "shadow-yml")
    shadow = case["traits"] / "function/protein_family/shadow.yml"
    _write(shadow, "identifier: SCOP:5\n")
    with pytest.raises(stage.ScopeSqStageError, match="exact lowercase .yaml suffix"):
        _build(case)

    case = _case(tmp_path / "shadow-uppercase-extension")
    shadow = case["traits"] / "function/protein_family/shadow.YAML"
    _write(shadow, "identifier: SCOP:5\n")
    with pytest.raises(stage.ScopeSqStageError, match="exact lowercase .yaml suffix"):
        _build(case)

    case = _case(tmp_path / "shadow-case-namespace")
    shadow = case["traits"] / "function/protein_family/shadow.yaml"
    _write(shadow, "identifier: sCoP:5\n")
    with pytest.raises(stage.ScopeSqStageError, match="noncanonical SCOP trait namespace"):
        _build(case)

    case = _case(tmp_path / "shadow-scope-alias")
    shadow = case["traits"] / "function/protein_family/shadow.yaml"
    _write(shadow, "identifier: SCOPe:5\n")
    with pytest.raises(stage.ScopeSqStageError, match="noncanonical SCOP trait namespace"):
        _build(case)

    case = _case(tmp_path / "trait-symlink")
    external = tmp_path / "external-trait.yaml"
    _write(external, "identifier: OTHER:1\n")
    (case["traits"] / "linked.yaml").symlink_to(external)
    with pytest.raises(stage.ScopeSqStageError, match="symlink below trait directory"):
        _build(case)


def test_content_drift_check_and_path_escape(tmp_path: Path) -> None:
    case = _case(tmp_path)
    captured = stage._capture(case["comments"], description="fixture", repo_root=case["repo"])
    case["comments"].write_text(case["comments"].read_text() + "6 ! note\n", encoding="utf-8")
    binding = stage._bind_absolute_directory(case["repo"], description="fixture repo")
    try:
        with pytest.raises(stage.ScopeSqStageError, match="drifted while staging"):
            stage._assert_unchanged(captured, description="fixture", bound_root=binding)
    finally:
        stage.os.close(binding.descriptor)

    outside = tmp_path / "outside.jsonl"
    _write_registry(outside, [_registry_row()])
    with pytest.raises(stage.ScopeSqStageError, match="escapes repository root"):
        stage.load_protein_registries([outside], repo_root=case["repo"])

    external_dir = tmp_path / "external-registry"
    external_registry = external_dir / "registry.jsonl"
    _write_registry(external_registry, [_registry_row()])
    (case["repo"] / "linked-dir").symlink_to(external_dir, target_is_directory=True)
    with pytest.raises(stage.ScopeSqStageError, match="without following symlinks"):
        stage.load_protein_registries(
            [case["repo"] / "linked-dir/registry.jsonl"], repo_root=case["repo"]
        )


def test_descriptor_relative_open_blocks_check_to_open_symlink_swap(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    case = _case(tmp_path)
    target = case["comments"]
    backup = target.with_suffix(".original")
    external = tmp_path / "external-comments.txt"
    external.write_text("external bytes must not be read\n", encoding="utf-8")
    original_open = stage.os.open
    original_supports_dir_fd = set(stage.os.supports_dir_fd)
    swapped = False

    def swapping_open(path: Any, flags: int, mode: int = 0o777, *, dir_fd: int | None = None):
        nonlocal swapped
        if path == target.name and dir_fd is not None and not swapped:
            swapped = True
            target.rename(backup)
            target.symlink_to(external)
        return original_open(path, flags, mode, dir_fd=dir_fd)

    monkeypatch.setattr(stage.os, "open", swapping_open)
    monkeypatch.setattr(
        stage.os,
        "supports_dir_fd",
        original_supports_dir_fd | {swapping_open},
    )
    monkeypatch.setattr(
        stage.os,
        "read",
        lambda *_args, **_kwargs: pytest.fail("external bytes were read after symlink swap"),
    )
    with pytest.raises(stage.ScopeSqStageError, match="without following symlinks"):
        _build(case)
    assert swapped


def test_descriptor_safety_capability_is_mandatory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    case = _case(tmp_path)
    monkeypatch.setattr(stage.os, "supports_dir_fd", set())
    with pytest.raises(stage.ScopeSqStageError, match="platform lacks required"):
        _build(case)


def test_output_is_deterministic_canonical_and_cli_has_no_write_mode(tmp_path: Path) -> None:
    case = _case(tmp_path)
    first = _build(case)
    second = _build(case)
    assert stage.render_stage(first) == stage.render_stage(second)
    assert stage.render_stage(first, summary_only=True) == stage.render_stage(
        second, summary_only=True
    )
    rows = [json.loads(line) for line in stage.render_stage(first).splitlines()]
    assert rows[-1] == first.summary
    assert (
        first.summary["candidate_rows_sha256"]
        == hashlib.sha256(
            "".join(stage.canonical_json(row) + "\n" for row in first.candidates).encode()
        ).hexdigest()
    )
    parser_dests = {action.dest for action in stage._parser()._actions}
    assert "apply" not in parser_dests
    assert "output" not in parser_dests
    assert "fetch" not in parser_dests
    assert "promote" not in parser_dests
    assert "protein_registry" in parser_dests
    justfile = (REPO / "justfile").read_text(encoding="utf-8")
    assert (
        "stage-scope-source-native *args:\n"
        "    uv run --frozen --offline --no-sync python "
        "scripts/stage_scope_sq_grounding_candidates.py {{args}}\n"
    ) in justfile


def test_every_output_family_is_zero_evidence_no_action_and_receipt_closed(
    tmp_path: Path,
) -> None:
    mixed = _case(
        tmp_path / "mixed",
        comments=[
            ("6", "SQ P12345 2-11 ! SQ P12345 ! note SQ Q12345 1-2"),
        ],
    )
    mixed_result = _build(mixed)
    missing = _case(
        tmp_path / "missing",
        registry_rows=[_registry_row("Q12345")],
    )
    missing_result = _build(missing)
    conflict = _case(
        tmp_path / "conflict",
        comments=[("50533", "SQ P00734 333-622")],
        extra_nodes=[("50533", "sp", "a.1.1.1", "-", "Cow [TaxId: 9913]")],
        extra_parents={"50533": "5"},
        registry_rows=[_registry_row("P00734", "A" * 622)],
    )
    conflict_result = _build(conflict)

    rows = [
        *mixed_result.blocked_clauses,
        *mixed_result.blocked_out_of_bounds,
        *mixed_result.unmarked_sq_diagnostics,
        *missing_result.candidates,
        *missing_result.protein_requests,
        *conflict_result.blocked_taxon_conflicts,
    ]
    assert rows
    for row in rows:
        assert row["schema_version"] == 3
        assert row["missing_receipts"] == list(stage.MISSING_RECEIPTS)
        assert set(stage.GLOBAL_PROMOTION_BLOCKERS) <= set(row["promotion_blockers"])
        assert row["grounding_evidence_emitted"] is False
        assert row["network_action_performed"] is False
        assert row["write_action_performed"] is False

    for result in (mixed_result, missing_result, conflict_result):
        assert result.summary["grounding_evidence_emitted_count"] == 0
        assert result.summary["network_action_performed"] is False
        assert result.summary["write_action_performed"] is False


def test_production_scope_snapshot_acceptance_when_private_artifacts_exist() -> None:
    required = [stage.DEFAULT_COMMENTS, stage.DEFAULT_DESCRIPTIONS, stage.DEFAULT_HIERARCHY]
    if not all(path.is_file() for path in required):
        pytest.skip("private SCOPe snapshot is unavailable")
    assert stage.DEFAULT_PROTEIN_REGISTRY.is_file()
    assert (
        hashlib.sha256(stage.DEFAULT_PROTEIN_REGISTRY.read_bytes()).hexdigest()
        == stage.EXPECTED_PROTEIN_REGISTRY_SHA256
    )
    result = stage.build_stage(
        comments_path=stage.DEFAULT_COMMENTS,
        descriptions_path=stage.DEFAULT_DESCRIPTIONS,
        hierarchy_path=stage.DEFAULT_HIERARCHY,
        traits_root=stage.DEFAULT_TRAITS_ROOT,
        protein_registry_path=stage.DEFAULT_PROTEIN_REGISTRY,
    )
    summary = result.summary
    assert summary["scope_trait_record_count"] == 22_810
    assert summary["trait_binding_count"] == 22_810
    assert summary["schema_version"] == 3
    assert summary["exact_sq_clause_count"] == 6_523
    assert summary["total_sq_clause_count"] == 6_523
    assert summary["unmarked_sq_text_count"] == 68
    assert summary["total_sq_like_token_count"] == 6_591
    assert summary["admitted_sq_clause_count"] == 4_656
    assert summary["unique_admitted_occurrence_count"] == 4_654
    assert summary["blocked_sq_clause_count"] == 1_867
    assert summary["blocked_sq_reason_counts"]["SOURCE_NODE_LEVEL_NOT_SP"] == 1
    assert summary["unique_prospective_candidate_projection_count"] == 23_192
    assert summary["candidate_count"] == 23_192
    q8avn9 = [row for row in result.candidates if row["protein_id"] == "UniProtKB:Q8AVN9"]
    assert len(q8avn9) == 10
    assert {(row["intervals"][0]["start"], row["intervals"][0]["end"]) for row in q8avn9} == {
        (2, 73),
        (74, 128),
    }
    assert {
        (
            assertion["source_line_number"],
            assertion["source_field_index"],
            assertion["source_segment"],
        )
        for row in q8avn9
        for assertion in row["source_assertions"]
    } == {
        (301_422, 1, "SQ Q8AVN9 2-73"),
        (301_422, 2, "SQ Q8AVN9 74-128"),
    }
    assert summary["candidate_unique_trait_count"] == 7_604
    assert summary["candidate_unique_protein_count"] == 3_588
    assert summary["ready_local_reference_candidate_count"] == 15
    assert summary["ready_local_reference_trait_count"] == 14
    assert summary["ready_local_reference_protein_count"] == 3
    assert summary["ready_local_reference_unresolved_taxon_mismatch_candidate_count"] == 5
    assert summary["ready_local_reference_taxon_review_status_counts"] == {
        "EXACT_TAXON_MATCH": 10,
        "UNRESOLVED_TAXON_MISMATCH_REQUIRES_LINEAGE_REVIEW": 5,
    }
    assert summary["ready_local_reference_taxon_mismatch_pair_counts"] == [
        {
            "source_taxon_id": "NCBITaxon:562",
            "registry_taxon_id": "NCBITaxon:83333",
            "candidate_count": 5,
        },
    ]
    assert summary["missing_local_protein_reference_candidate_count"] == 23_177
    assert summary["missing_local_protein_reference_trait_count"] == 7_601
    assert summary["missing_local_protein_reference_protein_count"] == 3_585
    assert summary["protein_reference_request_count"] == 3_585
    assert summary["protein_reference_request_unique_protein_count"] == 3_585
    assert summary["blocked_out_of_bounds_source_assertion_count"] == 0
    assert summary["blocked_out_of_bounds_affected_projection_count"] == 0
    assert summary["blocked_taxon_conflict_source_assertion_count"] == 0
    assert summary["blocked_taxon_conflict_affected_projection_count"] == 0
    assert summary["local_registry_available_projection_count"] == 15
    assert summary["local_heterogeneous_output_row_count"] == 15
    assert summary["local_union_trait_count"] == 14
    assert summary["local_union_protein_count"] == 3
    assert result.blocked_out_of_bounds == ()
    assert result.blocked_taxon_conflicts == ()
    assert len(result.protein_requests) == 3_585
    assert all(row["grounding_evidence_emitted"] is False for row in result.candidates)
    assert summary["grounding_evidence_emitted_count"] == 0
    assert summary["protein_registry_artifact"]["sha256"] == (
        stage.EXPECTED_PROTEIN_REGISTRY_SHA256
    )
    assert summary["protein_registry_fetch_receipt_verification_status"] == (
        "NOT_VERIFIED_BY_THIS_STAGE"
    )
    assert (
        sum(
            len(rows)
            for rows in (
                result.candidates,
                result.blocked_clauses,
                result.blocked_out_of_bounds,
                result.blocked_taxon_conflicts,
                result.unmarked_sq_diagnostics,
                result.protein_requests,
            )
        )
        + 1
        == 28_713
    )

    # Exact v3 row-family and complete-stream goldens are filled from the
    # independently replayed default protected-registry stage below.
    expected_hashes = {
        "candidate_rows_sha256": (
            "11551cecefc190770f72ef1c6d08fb7d28588e21ac18ff15f044e7c5c540cdca"
        ),
        "blocked_clause_rows_sha256": (
            "5b17b6c144e58e0af55c7e0173407231ade952dfc4c9833201c14655a70e80a7"
        ),
        "blocked_out_of_bounds_rows_sha256": (
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        ),
        "blocked_taxon_conflict_rows_sha256": (
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        ),
        "unmarked_sq_diagnostic_rows_sha256": (
            "e737b18f13d4dc37128eb7130b0e1be65d014be6c9ac25e9187c937bc1ddfd5c"
        ),
        "protein_request_rows_sha256": (
            "fa57769b5619658f20187ed904e3b389bdce0a98d9926b30140fe8dc5eb6f418"
        ),
        "combined_non_summary_rows_sha256": (
            "b4ae4dcb1d76135ed66e229ccb78e1f6f328e1c29e434148c6a3c3ae59a470c5"
        ),
        "trait_binding_rows_sha256": (
            "cf063a943352cf8010e2840805e36686dd10e81d2d073d6f58ca34ec1809d80c"
        ),
        "summary_row_sha256": ("67a660da88aad7d79acf2f9fe7be13988691c197e07e349fcbde4d877913f898"),
        "stage_id": (
            "scope-sq-grounding-stage:"
            "8c22574f759f23481934e3b1d432cdc072597bcab633b108c0b81bc29a92fcfb"
        ),
        "source_snapshot_id": (
            "scope-source-snapshot:feb7ab9116aaf530653f8b0e7354e0f5ab5265a2395a2c750b64a1cbd461d2b0"
        ),
    }
    assert {key: summary[key] for key in expected_hashes} == expected_hashes
    stream = hashlib.sha256()
    for rows in (
        result.candidates,
        result.blocked_clauses,
        result.blocked_out_of_bounds,
        result.blocked_taxon_conflicts,
        result.unmarked_sq_diagnostics,
        result.protein_requests,
        (result.summary,),
    ):
        for row in rows:
            stream.update((stage.canonical_json(row) + "\n").encode("utf-8"))
    assert stream.hexdigest() == (
        "358123ed156919cbcfa4a3c3c6779e0484b896ff2e3cb4ff67b1c17022d78efb"
    )


def test_absent_ripgrep_falls_back_to_a_superset_with_an_identical_result(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The prefilter must not depend on ripgrep, which CI does not install (#571).

    Without this the fallback is dead code on any machine that has ripgrep --
    which is every machine where this suite has ever been run green, and never
    CI, where the fallback is the only path. The fallback is deliberately a
    strict superset rather than a second matcher, because reproducing ripgrep's
    escape, NUL, and UTF-16 semantics twice is how the two paths drift apart
    silently (#539). So assert containment, not set equality, and assert that
    what the stage actually produces is identical either way.
    """

    case = _case(tmp_path)
    root = case["traits"]
    if shutil.which("rg") is None:
        pytest.skip("ripgrep is absent here, so the fallback is already the only path")

    matched = stage.ripgrep_prefilter.ripgrep_paths(root, stage._SCOPE_PREFILTER_PATTERNS, stage._SCOPE_PREFILTER_LABEL)
    assert matched is not None
    walked = stage.ripgrep_prefilter.walked_paths(root, stage._SCOPE_PREFILTER_LABEL)
    assert {Path(os.path.abspath(p)) for p in matched} <= {
        Path(os.path.abspath(p)) for p in walked
    }

    with_ripgrep = _build(case)
    monkeypatch.setenv("PATH", "")
    assert stage.ripgrep_prefilter.ripgrep_paths(root, stage._SCOPE_PREFILTER_PATTERNS, stage._SCOPE_PREFILTER_LABEL) is None
    without_ripgrep = _build(case)

    for attribute in ("candidates", "protein_requests", "summary"):
        assert stage.canonical_json(getattr(without_ripgrep, attribute)) == stage.canonical_json(
            getattr(with_ripgrep, attribute)
        )


def test_the_fallback_refuses_an_unscannable_trait_root(tmp_path: Path) -> None:
    """The fallback must fail closed exactly where ripgrep does (#573).

    ``os.walk`` reports a missing or unreadable tree as an empty one, so without
    an explicit guard the fallback would scan nothing, find nothing, and report
    success -- in the one environment (no ripgrep) it exists to serve.
    """

    missing = tmp_path / "no-such-trait-root"
    with pytest.raises(stage.ripgrep_prefilter.PrefilterError, match="not a directory"):
        stage.ripgrep_prefilter.walked_paths(missing, stage._SCOPE_PREFILTER_LABEL)

    unreadable = tmp_path / "unreadable"
    (unreadable / "nested").mkdir(parents=True)
    (unreadable / "nested" / "trait.yaml").write_text("identifier: X\n", encoding="utf-8")
    os.chmod(unreadable / "nested", 0o000)
    try:
        if os.access(unreadable / "nested", os.R_OK):
            pytest.skip("running as a user that ignores directory permissions")
        with pytest.raises(stage.ripgrep_prefilter.PrefilterError, match="cannot scan"):
            stage.ripgrep_prefilter.walked_paths(unreadable, stage._SCOPE_PREFILTER_LABEL)
    finally:
        os.chmod(unreadable / "nested", 0o700)
