"""Content-addressed review of the read-only PRINTS migration plan."""

from __future__ import annotations

import copy
import hashlib
import json
import os
import pathlib
import sys
from typing import Any, Callable

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import migrate_prints_source_model as migration  # noqa: E402
import review_prints_migration_plan as review  # noqa: E402


def _plan_row(
    accession: str,
    requirements: list[str],
    *,
    yaml_hash_character: str,
) -> dict[str, Any]:
    route_review = "ROUTING_REVIEW" in requirements
    hierarchy_repair = "HIERARCHY_REPAIR" in requirements
    row: dict[str, Any] = {
        "schema_version": migration.SCHEMA_VERSION,
        "kind": migration.ROW_KIND,
        "identifier": f"PRINTS:{accession}",
        "record_path": f"data/traits/sequence/family/prints/{accession.lower()}.yaml",
        "current_record_yaml_sha256": yaml_hash_character * 64,
        "current_record_hash_domain": "EXACT_YAML_BYTES",
        "record_state": "REVIEW_ONLY" if "RECORD_REVIEW" in requirements else "EXACT_LEGACY",
        "classification": "TEST_CLASSIFICATION",
        "review_requirements": requirements,
        "member_type": "family",
        "member_route": {
            "trait_axis": "SEQUENCE",
            "trait_category": "SEQ_FAMILY",
            "directory": "sequence/family",
        },
        "integrating_interpro": "IPR000001",
        "integrating_interpro_type": "domain" if route_review else "family",
        "integrating_interpro_route": {
            "trait_axis": "SEQUENCE",
            "trait_category": "SEQ_DOMAIN" if route_review else "SEQ_FAMILY",
            "directory": "sequence/domain" if route_review else "sequence/family",
        },
        "route_status": "ROUTING_REVIEW" if route_review else "AGREES",
        "hierarchy_status": ("CONFIRMED_LEGACY_GENERATED_PARENT" if hierarchy_repair else "NONE"),
        "hierarchy_source_semantics": "PRINTS_POSTPROCESSING_RELATIONS_NOT_SUBCLASS_EDGES",
        "confirmed_legacy_generated_parent": ("PRINTS:PR99999" if hierarchy_repair else None),
        "path_status": "EXPECTED_MEMBER_ROUTE",
        "expected_record_directory": "data/traits/sequence/family/prints",
        "current_route": {
            "trait_axis": "SEQUENCE",
            "trait_category": "SEQ_FAMILY",
        },
        "source_record_sha256": "d" * 64,
        "motif_count": 2,
        "changed_fields": ["definition", "sequence_fingerprint_representations"],
        "replacement_fields": {"definition": "source-native"},
        "remove_fields": ["parent_traits"] if hierarchy_repair else [],
        "content_proposal_semantic_sha256": "e" * 64,
        "content_proposal_hash_domain": "CANONICAL_JSON_SEMANTIC_OBJECT",
        "proposed_record_sha256": None,
        "proposed_record_hash_status": "NOT_MATERIALIZED_PLAN_ONLY",
        "legacy_mismatch_fields": ["label"] if "RECORD_REVIEW" in requirements else [],
        "unmanaged_fields_preserved": [],
    }
    hierarchy_row = {
        "accession": accession,
        "code": "TESTPRINT",
        "domain_flag": False,
        "evalue_cutoff": "1e-04",
        "hierarchical_relations": [],
        "minimum_motif_count": 0,
    }
    projections = (
        {
            "label": {
                "current": {"present": True, "value": "Curator label"},
                "legacy_expected": {"present": True, "value": "Legacy label"},
                "proposed": {"present": True, "value": "Source label"},
            }
        }
        if "RECORD_REVIEW" in requirements
        else {}
    )
    row.update(
        {
            "normalized_hierarchy_row": hierarchy_row,
            "normalized_hierarchy_row_sha256": migration.value_sha256(hierarchy_row),
            "normalized_hierarchy_domain_flag": False,
            "member_type_is_domain": False,
            "member_hierarchy_domain_alignment": "AGREES",
            "record_review_value_projections": projections,
            "record_review_value_projections_sha256": migration.value_sha256(projections),
        }
    )
    row["row_sha256"] = migration.value_sha256(row)
    return row


def _refresh_plan_content_addresses(rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    for row in rows:
        row.pop("row_sha256", None)
        row["row_sha256"] = migration.value_sha256(row)
    rows_bytes = "".join(migration.canonical_json(row) + "\n" for row in rows).encode()
    hierarchy_rows = [row["normalized_hierarchy_row"] for row in rows]
    summary.update(
        {
            "normalized_hierarchy_row_count": len(rows),
            "normalized_hierarchy_projection_sha256": migration.value_sha256(hierarchy_rows),
            "normalized_hierarchy_domain_count": sum(
                row["normalized_hierarchy_domain_flag"] for row in rows
            ),
            "member_hierarchy_domain_alignment_counts": dict(
                sorted(
                    {
                        alignment: sum(
                            row["member_hierarchy_domain_alignment"] == alignment for row in rows
                        )
                        for alignment in {row["member_hierarchy_domain_alignment"] for row in rows}
                    }.items()
                )
            ),
            "routing_review_member_hierarchy_domain_alignment_counts": dict(
                sorted(
                    {
                        alignment: sum(
                            row["route_status"] == "ROUTING_REVIEW"
                            and row["member_hierarchy_domain_alignment"] == alignment
                            for row in rows
                        )
                        for alignment in {
                            row["member_hierarchy_domain_alignment"]
                            for row in rows
                            if row["route_status"] == "ROUTING_REVIEW"
                        }
                    }.items()
                )
            ),
            "rows_sha256": hashlib.sha256(rows_bytes).hexdigest(),
        }
    )
    summary.pop("plan_id", None)
    summary["plan_id"] = migration.PLAN_ID_PREFIX + migration.value_sha256(summary)


def _plan() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows = [
        _plan_row(
            "PR00001",
            ["ROUTING_REVIEW", "HIERARCHY_REPAIR"],
            yaml_hash_character="a",
        ),
        _plan_row("PR00002", ["RECORD_REVIEW"], yaml_hash_character="b"),
        _plan_row("PR00003", [], yaml_hash_character="c"),
    ]
    summary: dict[str, Any] = {
        "schema_version": migration.SCHEMA_VERSION,
        "kind": migration.SUMMARY_KIND,
        "plan_kind": migration.PLAN_KIND,
        "snapshot_manifest_id": "prints-snapshot:" + "1" * 64,
        "source_release": "42.0",
        "source_artifact_sha256": "2" * 64,
        "legacy_parent_replay_source_sha256": "3" * 64,
        "record_count": len(rows),
        "motif_count": 6,
        "classification_counts": {"TEST_CLASSIFICATION": 3},
        "record_state_counts": {"EXACT_LEGACY": 2, "REVIEW_ONLY": 1},
        "route_status_counts": {"AGREES": 2, "ROUTING_REVIEW": 1},
        "hierarchy_status_counts": {
            "CONFIRMED_LEGACY_GENERATED_PARENT": 1,
            "NONE": 2,
        },
        "path_status_counts": {"EXPECTED_MEMBER_ROUTE": 3},
        "changed_record_count": 3,
        "review_required_count": 2,
        "record_review_count": 1,
        "review_only_mismatch_field_counts": {"label": 1},
        "review_only_identifiers": ["PRINTS:PR00002"],
    }
    _refresh_plan_content_addresses(rows, summary)
    return rows, summary


def _completed_values(
    *,
    decision_overrides: dict[tuple[str, str], str] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows, summary = _plan()
    template_rows, template_summary = review.build_review_template(rows, summary)
    completed = copy.deepcopy(template_rows)
    overrides = decision_overrides or {}
    for row in completed:
        identifier = row["binding"]["identifier"]
        for requirement, value in row["decisions"].items():
            value["decision"] = overrides.get(
                (identifier, requirement), review.COMPATIBLE_DECISIONS[requirement]
            )
            value["reviewer"] = "prints-source-reviewer"
            value["reviewed_at"] = "2026-08-25T12:34:56Z"
            value["comment"] = (
                "Reviewed against the pinned PRINTS and InterPro source facts."
                if requirement != "HIERARCHY_REPAIR"
                else ""
            )
    return completed, template_summary


def _write_ledger(
    path: pathlib.Path,
    rows: list[dict[str, Any]],
    summary: dict[str, Any],
) -> bytes:
    raw = "".join(review.canonical_json(value) + "\n" for value in [*rows, summary]).encode()
    path.write_bytes(raw)
    return raw


def test_plan_stdout_replay_requires_canonical_rows_and_content_addresses():
    rows, summary = _plan()
    text = "".join(migration.canonical_json(value) + "\n" for value in [*rows, summary])

    assert review._parse_plan_stdout(text) == (rows, summary)

    changed = copy.deepcopy(rows)
    changed[0]["member_type"] = "domain"
    invalid_text = "".join(migration.canonical_json(value) + "\n" for value in [*changed, summary])
    with pytest.raises(review.PrintsMigrationReviewError, match="row_sha256 does not replay"):
        review._parse_plan_stdout(invalid_text)

    with pytest.raises(review.PrintsMigrationReviewError, match="not canonical"):
        review._parse_plan_stdout(text.replace("{", "{ ", 1))


def test_template_is_exhaustive_deterministic_and_dimension_specific():
    rows, summary = _plan()
    first_rows, first_summary = review.build_review_template(rows, summary)
    second_rows, second_summary = review.build_review_template(rows, summary)

    assert first_rows == second_rows
    assert first_summary == second_summary
    assert [row["binding"]["identifier"] for row in first_rows] == [
        "PRINTS:PR00001",
        "PRINTS:PR00002",
    ]
    assert first_summary["review_row_count"] == 2
    assert first_summary["review_dimension_count"] == 3
    assert first_summary["requirement_counts"] == {
        "HIERARCHY_REPAIR": 1,
        "RECORD_REVIEW": 1,
        "ROUTING_REVIEW": 1,
    }
    assert first_summary["decision_options"] == {
        key: list(review.DECISION_OPTIONS[key]) for key in sorted(review.DECISION_OPTIONS)
    }
    assert first_summary["planner_review_summary"] == {
        "normalized_hierarchy_row_count": 3,
        "normalized_hierarchy_projection_sha256": summary["normalized_hierarchy_projection_sha256"],
        "normalized_hierarchy_domain_count": 0,
        "member_hierarchy_domain_alignment_counts": {"AGREES": 3},
        "routing_review_member_hierarchy_domain_alignment_counts": {"AGREES": 1},
    }
    assert first_summary["template_id"].startswith(review.TEMPLATE_ID_PREFIX)
    for row in first_rows:
        assert row["binding_sha256"] == review.value_sha256(row["binding"])
        assert list(row["decisions"]) == row["binding"]["review_requirements"]
        assert all(value["decision"] == "PENDING" for value in row["decisions"].values())
    assert review.dump_review_template(rows, summary).count("\n") == 3


def test_unknown_future_review_dimension_fails_closed():
    rows, summary = _plan()
    rows[0]["review_requirements"] = ["PATH_REVIEW"]
    _refresh_plan_content_addresses(rows, summary)

    with pytest.raises(review.PrintsMigrationReviewError, match="unsupported review"):
        review.build_review_template(rows, summary)


def test_plan_without_mandatory_v3_reviewer_context_fails_closed():
    rows, summary = _plan()
    del rows[0]["normalized_hierarchy_row"]
    rows[0].pop("row_sha256")
    rows[0]["row_sha256"] = migration.value_sha256(rows[0])

    with pytest.raises(
        review.PrintsMigrationReviewError, match="incomplete planner review context"
    ):
        review.build_review_template(rows, summary)


def test_explicit_planner_review_context_is_verified_and_exposed():
    rows, summary = _plan()
    row = rows[1]
    hierarchy_row = {
        "accession": "PR00002",
        "code": "TESTPRINT",
        "domain_flag": False,
        "evalue_cutoff": "1e-04",
        "hierarchical_relations": [],
        "minimum_motif_count": 0,
    }
    projections = {
        "label": {
            "current": {"present": True, "value": "Curator label"},
            "legacy_expected": {"present": True, "value": "Legacy label"},
            "proposed": {"present": True, "value": "Source label"},
        }
    }
    row.update(
        {
            "normalized_hierarchy_row": hierarchy_row,
            "normalized_hierarchy_row_sha256": review.value_sha256(hierarchy_row),
            "normalized_hierarchy_domain_flag": False,
            "member_type_is_domain": False,
            "member_hierarchy_domain_alignment": "AGREES",
            "record_review_value_projections": projections,
            "record_review_value_projections_sha256": review.value_sha256(projections),
        }
    )
    _refresh_plan_content_addresses(rows, summary)

    template_rows, _template_summary = review.build_review_template(rows, summary)
    binding = next(
        item["binding"]
        for item in template_rows
        if item["binding"]["identifier"] == "PRINTS:PR00002"
    )
    assert binding["record_facts"]["record_review_value_projections"] == projections
    assert binding["routing_facts"]["member_hierarchy_domain_alignment"] == "AGREES"
    assert binding["hierarchy_facts"]["normalized_hierarchy_row"] == hierarchy_row

    row["record_review_value_projections_sha256"] = "f" * 64
    _refresh_plan_content_addresses(rows, summary)
    with pytest.raises(review.PrintsMigrationReviewError, match="projection hash"):
        review.build_review_template(rows, summary)


def test_keep_member_route_is_non_accepting_when_hierarchy_domain_flag_disagrees(tmp_path):
    rows, summary = _plan()
    row = rows[0]
    hierarchy_row = {
        "accession": "PR00001",
        "code": "TESTPRINT",
        "domain_flag": True,
        "evalue_cutoff": "1e-04",
        "hierarchical_relations": [],
        "minimum_motif_count": 0,
    }
    row.update(
        {
            "normalized_hierarchy_row": hierarchy_row,
            "normalized_hierarchy_row_sha256": review.value_sha256(hierarchy_row),
            "normalized_hierarchy_domain_flag": True,
            "member_type_is_domain": False,
            "member_hierarchy_domain_alignment": "DISAGREES",
            "record_review_value_projections": {},
            "record_review_value_projections_sha256": review.value_sha256({}),
        }
    )
    _refresh_plan_content_addresses(rows, summary)
    template_rows, template_summary = review.build_review_template(rows, summary)
    for template_row in template_rows:
        for requirement, decision in template_row["decisions"].items():
            decision.update(
                decision=review.COMPATIBLE_DECISIONS[requirement],
                reviewer="prints-source-reviewer",
                reviewed_at="2026-08-25T12:34:56Z",
                comment=(
                    "Reviewed source disagreement." if requirement != "HIERARCHY_REPAIR" else ""
                ),
            )
    ledger = tmp_path / "domain-disagreement.jsonl"
    _write_ledger(ledger, template_rows, template_summary)

    receipt = review.validate_completed_ledger(
        ledger_path=ledger,
        plan_rows=rows,
        plan_summary=summary,
    )

    assert receipt["status"] == "VALID_NON_ACCEPTING"
    assert receipt["proposal_compatible"] is False
    assert receipt["accepted_for_next_phase"] is False
    assert receipt["incompatible_record_count"] == 1
    assert "review_set_id" not in receipt


def test_completed_ledger_emits_content_addressed_non_authorizing_receipt(tmp_path):
    rows, summary = _plan()
    completed, template_summary = _completed_values()
    ledger = tmp_path / "prints-review.jsonl"
    raw = _write_ledger(ledger, completed, template_summary)

    receipt = review.validate_completed_ledger(
        ledger_path=ledger,
        plan_rows=rows,
        plan_summary=summary,
    )
    repeated = review.validate_completed_ledger(
        ledger_path=ledger,
        plan_rows=rows,
        plan_summary=summary,
    )

    assert receipt == repeated
    assert receipt["status"] == "ACCEPTED_SEMANTIC_PLAN_ONLY"
    assert receipt["proposal_compatible"] is True
    assert receipt["accepted_for_next_phase"] is True
    assert receipt["migration_review_outcome"] == ("ALL_REVIEW_DIMENSIONS_PROPOSAL_COMPATIBLE")
    assert receipt["apply_authorized"] is False
    assert receipt["serialization_status"] == "NOT_PERFORMED"
    assert receipt["trait_write_count"] == 0
    assert receipt["grounding_write_count"] == 0
    assert receipt["review_row_count"] == 2
    assert receipt["review_dimension_count"] == 3
    assert receipt["reviewer_dimension_counts"] == {"prints-source-reviewer": 3}
    assert receipt["incompatible_record_count"] == 0
    assert receipt["ledger_sha256"] == hashlib.sha256(raw).hexdigest()
    assert receipt["decision_projection_sha256"] == review.value_sha256(completed)
    assert receipt["review_set_id"] == review.REVIEW_SET_ID_PREFIX + review.value_sha256(
        {key: value for key, value in receipt.items() if key != "review_set_id"}
    )


@pytest.mark.parametrize(
    ("decision", "expected_outcome"),
    [
        ("BLOCK_ROUTING_MIGRATION", "BLOCKED_OR_REPLAN_REQUIRED"),
        ("REQUEST_ROUTING_REPLAN", "BLOCKED_OR_REPLAN_REQUIRED"),
    ],
)
def test_block_and_replan_are_never_reported_as_compatible(tmp_path, decision, expected_outcome):
    plan_rows, plan_summary = _plan()
    completed, template_summary = _completed_values(
        decision_overrides={("PRINTS:PR00001", "ROUTING_REVIEW"): decision}
    )
    completed[0]["decisions"]["ROUTING_REVIEW"]["comment"] = "Do not serialize this route."
    ledger = tmp_path / "blocked.jsonl"
    _write_ledger(ledger, completed, template_summary)

    receipt = review.validate_completed_ledger(
        ledger_path=ledger,
        plan_rows=plan_rows,
        plan_summary=plan_summary,
    )

    assert receipt["migration_review_outcome"] == expected_outcome
    assert receipt["status"] == "VALID_NON_ACCEPTING"
    assert receipt["proposal_compatible"] is False
    assert receipt["accepted_for_next_phase"] is False
    assert receipt["incompatible_record_count"] == 1
    assert "review_set_id" not in receipt
    assert len(receipt["diagnostic_content_sha256"]) == 64


def test_ledger_rejects_missing_extra_duplicate_stale_and_reordered_rows(tmp_path):
    plan_rows, plan_summary = _plan()
    completed, template_summary = _completed_values()

    variants: list[tuple[str, list[dict[str, Any]], str]] = [
        ("missing", completed[:-1], "incomplete or has extras"),
        ("extra", [*completed, copy.deepcopy(completed[-1])], "incomplete or has extras"),
        ("duplicate", [completed[0], copy.deepcopy(completed[0])], "identifiers"),
        ("reordered", list(reversed(completed)), "identifiers"),
    ]
    stale = copy.deepcopy(completed)
    stale[0]["binding"]["current_record_yaml_sha256"] = "f" * 64
    variants.append(("stale", stale, "immutable review binding"))
    nonstring_identifier = copy.deepcopy(completed)
    nonstring_identifier[0]["binding"]["identifier"] = ["PRINTS:PR00001"]
    variants.append(("nonstring-identifier", nonstring_identifier, "identifiers"))

    for name, candidate_rows, match in variants:
        ledger = tmp_path / f"{name}.jsonl"
        _write_ledger(ledger, candidate_rows, template_summary)
        with pytest.raises(review.PrintsMigrationReviewError, match=match):
            review.validate_completed_ledger(
                ledger_path=ledger,
                plan_rows=plan_rows,
                plan_summary=plan_summary,
            )


def test_ledger_rejects_pending_wrong_dimension_and_incomplete_attribution(tmp_path):
    plan_rows, plan_summary = _plan()
    cases: list[tuple[str, Callable[[list[dict[str, Any]]], None], str]] = [
        (
            "pending",
            lambda rows: rows[0]["decisions"]["ROUTING_REVIEW"].update(decision="PENDING"),
            "invalid or pending",
        ),
        (
            "wrong-dimension",
            lambda rows: rows[0]["decisions"]["ROUTING_REVIEW"].update(
                decision="APPROVE_SOURCE_NATIVE_CONTENT"
            ),
            "invalid or pending",
        ),
        (
            "missing-comment",
            lambda rows: rows[0]["decisions"]["ROUTING_REVIEW"].update(comment=""),
            "comment must be non-empty",
        ),
        (
            "missing-reviewer",
            lambda rows: rows[0]["decisions"]["ROUTING_REVIEW"].update(reviewer=""),
            "reviewer must be",
        ),
        (
            "bad-time",
            lambda rows: rows[0]["decisions"]["ROUTING_REVIEW"].update(
                reviewed_at="2026-02-30T00:00:00Z"
            ),
            "not a real UTC timestamp",
        ),
    ]
    for name, mutate, match in cases:
        completed, template_summary = _completed_values()
        mutate(completed)
        ledger = tmp_path / f"{name}.jsonl"
        _write_ledger(ledger, completed, template_summary)
        with pytest.raises(review.PrintsMigrationReviewError, match=match):
            review.validate_completed_ledger(
                ledger_path=ledger,
                plan_rows=plan_rows,
                plan_summary=plan_summary,
            )


def test_mechanical_hierarchy_comment_may_be_empty_but_block_comment_may_not(tmp_path):
    plan_rows, plan_summary = _plan()
    completed, template_summary = _completed_values()
    assert completed[0]["decisions"]["HIERARCHY_REPAIR"]["comment"] == ""
    ledger = tmp_path / "mechanical.jsonl"
    _write_ledger(ledger, completed, template_summary)
    assert (
        review.validate_completed_ledger(
            ledger_path=ledger,
            plan_rows=plan_rows,
            plan_summary=plan_summary,
        )["status"]
        == "ACCEPTED_SEMANTIC_PLAN_ONLY"
    )

    completed[0]["decisions"]["HIERARCHY_REPAIR"]["decision"] = "BLOCK_HIERARCHY_REPAIR"
    _write_ledger(ledger, completed, template_summary)
    with pytest.raises(review.PrintsMigrationReviewError, match="comment must be non-empty"):
        review.validate_completed_ledger(
            ledger_path=ledger,
            plan_rows=plan_rows,
            plan_summary=plan_summary,
        )


def test_ledger_requires_canonical_unique_key_lf_terminated_input(tmp_path):
    plan_rows, plan_summary = _plan()
    completed, template_summary = _completed_values()
    ledger = tmp_path / "ledger.jsonl"
    raw = _write_ledger(ledger, completed, template_summary)

    ledger.write_bytes(raw[:-1])
    with pytest.raises(review.PrintsMigrationReviewError, match="LF-terminated"):
        review.validate_completed_ledger(
            ledger_path=ledger,
            plan_rows=plan_rows,
            plan_summary=plan_summary,
        )

    lines = raw.decode().splitlines()
    lines[0] = lines[0].replace("{", "{ ", 1)
    ledger.write_text("\n".join(lines) + "\n", encoding="utf-8")
    with pytest.raises(review.PrintsMigrationReviewError, match="not canonical"):
        review.validate_completed_ledger(
            ledger_path=ledger,
            plan_rows=plan_rows,
            plan_summary=plan_summary,
        )

    lines = raw.decode().splitlines()
    lines[0] = lines[0].replace(
        '"kind":"PRINTS_MIGRATION_REVIEW_DECISION",',
        '"kind":"PRINTS_MIGRATION_REVIEW_DECISION","kind":"duplicate",',
    )
    ledger.write_text("\n".join(lines) + "\n", encoding="utf-8")
    with pytest.raises(review.PrintsMigrationReviewError, match="duplicate JSON key"):
        review.validate_completed_ledger(
            ledger_path=ledger,
            plan_rows=plan_rows,
            plan_summary=plan_summary,
        )


@pytest.mark.parametrize(
    ("separator", "match"),
    [
        ("\r\n", "CR/CRLF"),
        ("\r", "CR/CRLF"),
        ("\N{NEXT LINE}", "U\\+0085"),
        ("\N{LINE SEPARATOR}", "U\\+2028"),
        ("\N{PARAGRAPH SEPARATOR}", "U\\+2029"),
    ],
)
def test_ledger_rejects_non_lf_line_aliases(tmp_path, separator, match):
    plan_rows, plan_summary = _plan()
    completed, template_summary = _completed_values()
    ledger = tmp_path / "bad-lines.jsonl"
    raw = _write_ledger(ledger, completed, template_summary).decode("utf-8")
    ledger.write_text(raw.replace("\n", separator, 1), encoding="utf-8")

    with pytest.raises(review.PrintsMigrationReviewError, match=match):
        review.validate_completed_ledger(
            ledger_path=ledger,
            plan_rows=plan_rows,
            plan_summary=plan_summary,
        )


def test_ledger_capture_rejects_symlink_fifo_device_directory_and_oversize(tmp_path):
    regular = tmp_path / "regular.jsonl"
    regular.write_bytes(b"{}\n")
    symlink = tmp_path / "ledger-symlink.jsonl"
    symlink.symlink_to(regular)
    with pytest.raises(review.PrintsMigrationReviewError, match="safely open regular file"):
        review._capture_regular_file(symlink, label="ledger", max_bytes=1024)

    source_directory = tmp_path / "source-directory"
    source_directory.mkdir()
    (source_directory / "ledger.jsonl").write_bytes(b"{}\n")
    directory_alias = tmp_path / "directory-alias"
    directory_alias.symlink_to(source_directory, target_is_directory=True)
    with pytest.raises(review.PrintsMigrationReviewError, match="directory component"):
        review._capture_regular_file(
            directory_alias / "ledger.jsonl",
            label="ledger",
            max_bytes=1024,
        )

    fifo = tmp_path / "ledger.fifo"
    os.mkfifo(fifo)
    with pytest.raises(review.PrintsMigrationReviewError, match="not a regular file"):
        review._capture_regular_file(fifo, label="ledger", max_bytes=1024)
    with pytest.raises(review.PrintsMigrationReviewError, match="not a regular file"):
        review._capture_regular_file(tmp_path, label="ledger", max_bytes=1024)
    with pytest.raises(review.PrintsMigrationReviewError, match="not a regular file"):
        review._capture_regular_file(pathlib.Path("/dev/null"), label="ledger", max_bytes=1024)

    oversized = tmp_path / "oversized.jsonl"
    oversized.write_bytes(b"x" * 101)
    with pytest.raises(review.PrintsMigrationReviewError, match="outside 1..100 bytes"):
        review._capture_regular_file(oversized, label="ledger", max_bytes=100)


def test_ledger_capture_rejects_path_swap_after_descriptor_open(tmp_path, monkeypatch):
    ledger = tmp_path / "ledger.jsonl"
    ledger.write_bytes(b"{}\n")
    displaced = tmp_path / "displaced.jsonl"
    original_read = review.os.read
    swapped = False

    def swap_then_read(descriptor, count):
        nonlocal swapped
        if not swapped:
            swapped = True
            ledger.rename(displaced)
            ledger.write_bytes(b"{}\n")
        return original_read(descriptor, count)

    monkeypatch.setattr(review.os, "read", swap_then_read)
    with pytest.raises(review.PrintsMigrationReviewError, match="changed during capture"):
        review._capture_regular_file(ledger, label="ledger", max_bytes=1024)


def test_ledger_validation_never_uses_path_read_bytes(tmp_path, monkeypatch):
    plan_rows, plan_summary = _plan()
    completed, template_summary = _completed_values()
    ledger = tmp_path / "review.jsonl"
    _write_ledger(ledger, completed, template_summary)
    monkeypatch.setattr(
        pathlib.Path,
        "read_bytes",
        lambda _path: pytest.fail("Path.read_bytes bypassed descriptor capture"),
    )

    receipt = review.validate_completed_ledger(
        ledger_path=ledger,
        plan_rows=plan_rows,
        plan_summary=plan_summary,
    )
    assert receipt["accepted_for_next_phase"] is True


def test_stale_template_summary_is_rejected(tmp_path):
    plan_rows, plan_summary = _plan()
    completed, template_summary = _completed_values()
    template_summary["migration_rows_sha256"] = "f" * 64
    ledger = tmp_path / "stale-summary.jsonl"
    _write_ledger(ledger, completed, template_summary)

    with pytest.raises(review.PrintsMigrationReviewError, match="template summary is stale"):
        review.validate_completed_ledger(
            ledger_path=ledger,
            plan_rows=plan_rows,
            plan_summary=plan_summary,
        )


def test_obsolete_v1_template_cannot_validate_under_v2_semantics(tmp_path):
    plan_rows, plan_summary = _plan()
    completed, template_summary = _completed_values()
    for row in completed:
        row["schema_version"] = 1
    template_summary["schema_version"] = 1
    ledger = tmp_path / "obsolete-v1.jsonl"
    _write_ledger(ledger, completed, template_summary)

    with pytest.raises(review.PrintsMigrationReviewError, match="template summary is stale"):
        review.validate_completed_ledger(
            ledger_path=ledger,
            plan_rows=plan_rows,
            plan_summary=plan_summary,
        )


def test_cli_is_stdout_only_and_replays_before_template_or_validation(
    tmp_path, monkeypatch, capsys
):
    plan_rows, plan_summary = _plan()
    calls: list[pathlib.Path] = []

    def replay(args):
        calls.append(args.traits)
        return plan_rows, plan_summary

    monkeypatch.setattr(review, "replay_migration_plan", replay)
    trait_path = tmp_path / "traits"
    assert review.main(["template", "--traits", str(trait_path)]) == 0
    template_text = capsys.readouterr().out
    assert len(template_text.splitlines()) == 3
    assert json.loads(template_text.splitlines()[-1])["status"] == "PENDING_REVIEW"

    completed, template_summary = _completed_values()
    ledger = tmp_path / "review.jsonl"
    _write_ledger(ledger, completed, template_summary)
    assert review.main(["validate", "--ledger", str(ledger), "--traits", str(trait_path)]) == 0
    receipt = json.loads(capsys.readouterr().out)
    assert receipt["status"] == "ACCEPTED_SEMANTIC_PLAN_ONLY"
    assert calls == [trait_path, trait_path]
    assert sorted(path.name for path in tmp_path.iterdir()) == ["review.jsonl"]


def test_cli_returns_nonzero_and_no_acceptance_id_for_valid_incompatible_review(
    tmp_path, monkeypatch, capsys
):
    plan_rows, plan_summary = _plan()
    completed, template_summary = _completed_values(
        decision_overrides={("PRINTS:PR00001", "ROUTING_REVIEW"): "REQUEST_ROUTING_REPLAN"}
    )
    completed[0]["decisions"]["ROUTING_REVIEW"]["comment"] = "Routing needs a new plan."
    ledger = tmp_path / "replan.jsonl"
    _write_ledger(ledger, completed, template_summary)
    monkeypatch.setattr(
        review,
        "replay_migration_plan",
        lambda _args: (plan_rows, plan_summary),
    )

    assert review.main(["validate", "--ledger", str(ledger)]) == 3
    receipt = json.loads(capsys.readouterr().out)
    assert receipt["status"] == "VALID_NON_ACCEPTING"
    assert receipt["accepted_for_next_phase"] is False
    assert receipt["proposal_compatible"] is False
    assert "review_set_id" not in receipt


def test_cli_failure_is_canonical_stdout_receipt(tmp_path, monkeypatch, capsys):
    def fail(_args):
        raise review.PrintsMigrationReviewError("fixture replay stopped")

    monkeypatch.setattr(review, "replay_migration_plan", fail)
    assert review.main(["template", "--traits", str(tmp_path)]) == 2
    output = capsys.readouterr().out.strip()
    assert output == review.canonical_json(json.loads(output))
    assert json.loads(output) == {
        "schema_version": review.SCHEMA_VERSION,
        "kind": review.RECEIPT_KIND,
        "status": "INVALID",
        "proposal_compatible": False,
        "accepted_for_next_phase": False,
        "apply_authorized": False,
        "serialization_status": "NOT_PERFORMED",
        "trait_write_count": 0,
        "grounding_write_count": 0,
        "error": "fixture replay stopped",
    }


@pytest.mark.skipif(
    not all(
        path.is_file()
        for path in (
            migration.DEFAULT_API,
            migration.DEFAULT_KDAT,
            migration.DEFAULT_HIERARCHY,
            migration.DEFAULT_HIERARCHY_SOURCE,
            migration.DEFAULT_MANIFEST,
            migration.DEFAULT_INTERPRO,
        )
    ),
    reason="ignored pinned PRINTS production snapshot is absent",
)
def test_pinned_production_review_template_matches_current_plan():
    args = review._parser().parse_args(["template"])
    rows, summary = review.replay_migration_plan(args)
    template_rows, template_summary = review.build_review_template(rows, summary)

    assert summary["plan_id"] == (
        "prints-migration-plan:fcce6d6d5ecb5443ca1eb659e35bfce5a424a9e621662b15b5a3febc9b8e6fbf"
    )
    assert summary["rows_sha256"] == (
        "b36ad35933fa3408fb6cc4c0eacf26eef1bafafe7140da259a889365a4d66d49"
    )
    assert summary["normalized_hierarchy_projection_sha256"] == (
        "fa21deb29c23f39f01acd8f85fd4319ef40af7700a5e221d6fd80b4b6343d665"
    )
    assert summary["member_hierarchy_domain_alignment_counts"] == {
        "AGREES": 2087,
        "DISAGREES": 19,
    }
    assert summary["routing_review_member_hierarchy_domain_alignment_counts"] == {
        "AGREES": 102,
        "DISAGREES": 7,
    }
    assert len(template_rows) == 1117
    assert template_summary["review_dimension_count"] == 1138
    assert template_summary["requirement_counts"] == {
        "HIERARCHY_REPAIR": 1026,
        "RECORD_REVIEW": 3,
        "ROUTING_REVIEW": 109,
    }
    assert template_summary["snapshot_manifest_id"] == (
        "prints-snapshot:05fdb2bd7460d07294708bc6143b2d8ef1fcfdea28cb28d1042fec67715c8b10"
    )
    assert template_summary["template_rows_sha256"] == (
        "bd3a3cecf949f4cebc028e8a81ea3abe53f0e4cbba054ee346ae7d7782d0afb4"
    )
    assert template_summary["template_id"] == (
        "prints-migration-review-template:"
        "e473d5f1b613fc97b63b077f3a3b963df6170db5152d93cbb813873e2068f262"
    )
