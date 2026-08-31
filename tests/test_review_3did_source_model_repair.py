"""Review-only boundary for the pinned 3did source-model repair plan."""

from __future__ import annotations

import copy
import hashlib
import json
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import plan_3did_source_model_repair as repair  # noqa: E402
import review_3did_source_model_repair as review  # noqa: E402


def _hashed(row):
    value = copy.deepcopy(row)
    value["row_sha256"] = repair.value_sha256(value)
    return value


def _fresh_plan():
    exact_current = _hashed(
        {
            "schema_version": repair.SCHEMA_VERSION,
            "kind": repair.CURRENT_ROW_KIND,
            "identifier": "proteintraitsmech:INTERFACE_PF00001_PF00002",
            "record_path": "structure/interface/3did/exact.yaml",
            "current_record_yaml_sha256": "1" * 64,
            "classification": "EXACT_SOURCE_NATIVE_CURRENT",
        }
    )
    spurious_current = _hashed(
        {
            "schema_version": repair.SCHEMA_VERSION,
            "kind": repair.CURRENT_ROW_KIND,
            "identifier": "proteintraitsmech:INTERFACE_PF1_PF1",
            "record_path": "structure/interface/3did/spurious.yaml",
            "current_record_yaml_sha256": "2" * 64,
            "classification": "SPURIOUS_LEGACY_MISPARSE_CURRENT",
        }
    )
    exact_source = _hashed(
        {
            "schema_version": repair.SCHEMA_VERSION,
            "kind": repair.SOURCE_ROW_KIND,
            "source_record_id": "3did-source-record:" + "a" * 64,
            "classification": "EXACT_SOURCE_NATIVE",
            "source_state": "EXACT_CURRENT_TRAIT",
        }
    )
    current_binding = {
        "identifier": spurious_current["identifier"],
        "record_path": spurious_current["record_path"],
        "current_record_yaml_sha256": spurious_current["current_record_yaml_sha256"],
    }
    primary = _hashed(
        {
            "schema_version": repair.SCHEMA_VERSION,
            "kind": repair.SOURCE_ROW_KIND,
            "source_record_id": "3did-source-record:" + "b" * 64,
            "classification": "COLLAPSE_PRIMARY_REPAIR_PROPOSAL",
            "source_state": "CORRECTED_TRAIT_MISSING",
            "current_binding": current_binding,
            "legacy_collision_group_size": 2,
            "legacy_collision_group_ordinal": 1,
            "legacy_collision_primary_source_record_id": "3did-source-record:" + "b" * 64,
            "corrected_proposal": {
                "identifier": "proteintraitsmech:INTERFACE_PF01000_PF02000",
                "record_path": "structure/interface/3did/primary.yaml",
                "proposed_record_yaml_sha256": "3" * 64,
            },
        }
    )
    suppressed = _hashed(
        {
            "schema_version": repair.SCHEMA_VERSION,
            "kind": repair.SOURCE_ROW_KIND,
            "source_record_id": "3did-source-record:" + "c" * 64,
            "classification": "COLLAPSE_SUPPRESSED_REPAIR_PROPOSAL",
            "source_state": "CORRECTED_TRAIT_MISSING",
            "current_binding": current_binding,
            "legacy_collision_group_size": 2,
            "legacy_collision_group_ordinal": 2,
            "legacy_collision_primary_source_record_id": "3did-source-record:" + "b" * 64,
            "corrected_proposal": {
                "identifier": "proteintraitsmech:INTERFACE_PF03000_PF04000",
                "record_path": "structure/interface/3did/suppressed.yaml",
                "proposed_record_yaml_sha256": "4" * 64,
            },
        }
    )
    current_rows = [exact_current, spurious_current]
    source_rows = [exact_source, primary, suppressed]
    summary = {
        "schema_version": repair.SCHEMA_VERSION,
        "kind": repair.SUMMARY_KIND,
        "plan_kind": repair.PLAN_KIND,
        "rows_sha256": repair.rows_sha256([*current_rows, *source_rows]),
        "current_trait_byte_index_sha256": repair.rows_sha256(current_rows),
        "source_repair_rows_sha256": repair.rows_sha256(source_rows),
        "source_compressed_sha256": "5" * 64,
        "source_decompressed_sha256": "6" * 64,
        "source_release": repair.SOURCE_RELEASE,
        "source_release_semantics": (
            "GZIP_ORIGINAL_FILENAME_ARTIFACT_LABEL_NOT_INTERNAL_RELEASE_HEADER"
        ),
        "source_license": repair.SOURCE_LICENSE,
        "source_license_status": "NO_EXPLICIT_OPEN_LICENSE_RELEASE_BLOCKER",
        "grounding_gate": repair.GROUNDING_GATE,
        "current_trait_count": 2,
        "source_record_count": 3,
        "corrected_trait_missing_count": 2,
        "spurious_current_trait_count": 1,
        "direct_repair_source_count": 0,
        "collapse_primary_source_count": 1,
        "collapse_suppressed_source_count": 1,
        "legacy_collision_key_count": 1,
        "legacy_collapsed_extra_source_count": 1,
    }
    summary["plan_id"] = repair.PLAN_ID_PREFIX + repair.value_sha256(summary)
    return current_rows, source_rows, summary


def _readdress_summary(summary):
    payload = {key: value for key, value in summary.items() if key != "plan_id"}
    summary["plan_id"] = repair.PLAN_ID_PREFIX + repair.value_sha256(payload)


def _template():
    return review.build_review_template(*_fresh_plan())


def _completed_rows(*, overrides=None):
    rows, summary = _template()
    completed = copy.deepcopy(rows)
    overrides = overrides or {}
    for row in completed:
        dimension = row["binding"]["review_dimension"]
        row["decision"] = {
            "action": overrides.get(dimension, review.COMPATIBLE_DECISIONS[dimension]),
            "reviewer": "reviewer@example.org",
            "reviewed_at": "2026-08-25T12:34:56Z",
            "comment": "fixture review",
        }
    return completed, summary


def _ledger_bytes(rows, summary):
    return review.dump_review_template(rows, summary).encode()


def test_template_is_exhaustive_deterministic_and_collision_bound():
    first_rows, first_summary = _template()
    second_rows, second_summary = _template()

    assert (first_rows, first_summary) == (second_rows, second_summary)
    assert first_summary["review_item_count"] == 3
    assert first_summary["review_dimension_counts"] == {
        review.ADD_DIMENSION: 2,
        review.REMOVE_DIMENSION: 1,
    }
    assert first_summary["source_proposal_classification_counts"] == {
        "COLLAPSE_PRIMARY_REPAIR_PROPOSAL": 1,
        "COLLAPSE_SUPPRESSED_REPAIR_PROPOSAL": 1,
    }
    removal = next(
        row for row in first_rows if row["binding"]["review_dimension"] == review.REMOVE_DIMENSION
    )
    assert removal["binding"]["dependent_source_record_ids"] == [
        "3did-source-record:" + "b" * 64,
        "3did-source-record:" + "c" * 64,
    ]
    for row in first_rows:
        assert row["binding_sha256"] == review.value_sha256(row["binding"])
        assert row["review_item_id"] == review.REVIEW_ITEM_ID_PREFIX + row["binding_sha256"]
        assert all(value is None for value in row["decision"].values())


def test_all_positive_decisions_emit_semantic_only_accepted_receipt():
    rows, summary = _completed_rows()
    raw = _ledger_bytes(rows, summary)
    receipt = review.validate_completed_ledger(
        rows,
        summary,
        expected_rows=_template()[0],
        expected_summary=summary,
        ledger_bytes=raw,
    )

    assert receipt["status"] == "ACCEPTED_SEMANTIC_PLAN_ONLY"
    assert receipt["proposal_compatible"] is True
    assert receipt["accepted_for_next_phase"] is True
    assert receipt["review_set_id"].startswith(review.REVIEW_SET_ID_PREFIX)
    assert receipt["apply_authorized"] is False
    assert receipt["serialization_status"] == "NOT_PERFORMED"
    assert receipt["writes_performed"] is False


@pytest.mark.parametrize(
    ("dimension", "action"),
    [
        (review.ADD_DIMENSION, "BLOCK_CORRECTED_TRAIT_ADDITION"),
        (review.ADD_DIMENSION, "REQUEST_SOURCE_MODEL_REPLAN"),
        (review.REMOVE_DIMENSION, "KEEP_LEGACY_TRAIT"),
        (review.REMOVE_DIMENSION, "REQUEST_SOURCE_MODEL_REPLAN"),
    ],
)
def test_valid_incompatible_decisions_emit_no_review_set_id(dimension, action):
    rows, summary = _completed_rows(overrides={dimension: action})
    receipt = review.validate_completed_ledger(
        rows,
        summary,
        expected_rows=_template()[0],
        expected_summary=summary,
        ledger_bytes=_ledger_bytes(rows, summary),
    )

    assert receipt["status"] == "VALID_NON_ACCEPTING"
    assert receipt["proposal_compatible"] is False
    assert receipt["accepted_for_next_phase"] is False
    assert "review_set_id" not in receipt


def test_missing_or_malformed_review_metadata_fails_closed():
    rows, summary = _completed_rows()
    rows[0]["decision"]["reviewer"] = None
    with pytest.raises(review.ThreeDidRepairReviewError, match="reviewer is malformed"):
        review.validate_completed_ledger(
            rows,
            summary,
            expected_rows=_template()[0],
            expected_summary=summary,
            ledger_bytes=_ledger_bytes(rows, summary),
        )

    rows, summary = _completed_rows()
    rows[0]["decision"]["reviewed_at"] = "2026-02-30T12:00:00Z"
    with pytest.raises(review.ThreeDidRepairReviewError, match="not a real timestamp"):
        review.validate_completed_ledger(
            rows,
            summary,
            expected_rows=_template()[0],
            expected_summary=summary,
            ledger_bytes=_ledger_bytes(rows, summary),
        )


def test_binding_summary_order_and_duplicate_tampering_fail_closed():
    expected_rows, summary = _template()
    rows, _ = _completed_rows()
    rows[0]["binding"]["target_identifier"] = "tampered"
    with pytest.raises(review.ThreeDidRepairReviewError, match="immutable review binding"):
        review.validate_completed_ledger(
            rows,
            summary,
            expected_rows=expected_rows,
            expected_summary=summary,
            ledger_bytes=_ledger_bytes(rows, summary),
        )

    rows, _ = _completed_rows()
    rows[0], rows[1] = rows[1], rows[0]
    with pytest.raises(review.ThreeDidRepairReviewError, match="immutable review binding"):
        review.validate_completed_ledger(
            rows,
            summary,
            expected_rows=expected_rows,
            expected_summary=summary,
            ledger_bytes=_ledger_bytes(rows, summary),
        )

    rows, _ = _completed_rows()
    rows[1]["review_item_id"] = rows[0]["review_item_id"]
    with pytest.raises(review.ThreeDidRepairReviewError, match="duplicate/malformed"):
        review.validate_completed_ledger(
            rows,
            summary,
            expected_rows=expected_rows,
            expected_summary=summary,
            ledger_bytes=_ledger_bytes(rows, summary),
        )

    rows, supplied_summary = _completed_rows()
    supplied_summary = dict(supplied_summary)
    supplied_summary["review_item_count"] = 2
    with pytest.raises(review.ThreeDidRepairReviewError, match="summary is stale or altered"):
        review.validate_completed_ledger(
            rows,
            supplied_summary,
            expected_rows=expected_rows,
            expected_summary=summary,
            ledger_bytes=_ledger_bytes(rows, supplied_summary),
        )

    rows, supplied_summary = _completed_rows()
    with pytest.raises(review.ThreeDidRepairReviewError, match="bytes do not match"):
        review.validate_completed_ledger(
            rows,
            supplied_summary,
            expected_rows=expected_rows,
            expected_summary=summary,
            ledger_bytes=b"different canonical source bytes\n",
        )


def test_planner_partition_cross_binding_and_hashes_fail_closed():
    current, source, summary = _fresh_plan()
    source[1]["current_binding"]["current_record_yaml_sha256"] = "f" * 64
    source[1]["row_sha256"] = repair.value_sha256(
        {key: value for key, value in source[1].items() if key != "row_sha256"}
    )
    summary["source_repair_rows_sha256"] = repair.rows_sha256(source)
    summary["rows_sha256"] = repair.rows_sha256([*current, *source])
    _readdress_summary(summary)
    with pytest.raises(review.ThreeDidRepairReviewError, match="current binding disagrees"):
        review.build_review_template(current, source, summary)

    current, source, summary = _fresh_plan()
    current[0]["row_sha256"] = "0" * 64
    summary["current_trait_byte_index_sha256"] = repair.rows_sha256(current)
    summary["rows_sha256"] = repair.rows_sha256([*current, *source])
    _readdress_summary(summary)
    with pytest.raises(review.ThreeDidRepairReviewError, match="planner row hash mismatch"):
        review.build_review_template(current, source, summary)

    current, source, summary = _fresh_plan()
    summary["plan_id"] = repair.PLAN_ID_PREFIX + "0" * 64
    with pytest.raises(review.ThreeDidRepairReviewError, match="content address mismatch"):
        review.build_review_template(current, source, summary)


@pytest.mark.parametrize(
    ("mutator", "message"),
    [
        (lambda text: text.replace("\n", "\r\n"), "CR/CRLF"),
        (lambda text: text.replace("\n", "\u2028", 1), "U\\+2028"),
        (lambda text: text.rstrip("\n"), "LF-terminated"),
        (lambda text: text.replace("\n", "\n\n", 1), "blank lines"),
        (lambda text: " " + text, "not canonical"),
    ],
)
def test_ledger_reader_requires_canonical_exact_lf(tmp_path, mutator, message):
    rows, summary = _completed_rows()
    path = tmp_path / "review.jsonl"
    path.write_text(mutator(_ledger_bytes(rows, summary).decode()), newline="")
    with pytest.raises(review.ThreeDidRepairReviewError, match=message):
        review._read_completed_ledger(path)


def test_ledger_reader_rejects_duplicate_keys_symlinks_fifo_and_oversize(tmp_path, monkeypatch):
    duplicate = tmp_path / "duplicate.jsonl"
    duplicate.write_bytes(b'{"a":1,"a":2}\n{}\n')
    with pytest.raises(review.ThreeDidRepairReviewError, match="duplicate JSON key"):
        review._read_completed_ledger(duplicate)

    nonfinite = tmp_path / "nonfinite.jsonl"
    nonfinite.write_bytes(b'{"value":NaN}\n{}\n')
    with pytest.raises(review.ThreeDidRepairReviewError, match="not canonical JSON data"):
        review._read_completed_ledger(nonfinite)

    link = tmp_path / "link.jsonl"
    link.symlink_to(duplicate)
    with pytest.raises(review.ThreeDidRepairReviewError, match="cannot safely open regular file"):
        review._read_completed_ledger(link)

    fifo = tmp_path / "ledger.fifo"
    review.os.mkfifo(fifo)
    with pytest.raises(review.ThreeDidRepairReviewError, match="not a regular file"):
        review._read_completed_ledger(fifo)

    oversized = tmp_path / "oversized.jsonl"
    oversized.write_bytes(b"{}\n{}\n")
    monkeypatch.setattr(review, "MAX_LEDGER_BYTES", 1)
    with pytest.raises(review.ThreeDidRepairReviewError, match="outside 1..1 bytes"):
        review._read_completed_ledger(oversized)


def test_ledger_capture_rejects_final_path_swap(tmp_path, monkeypatch):
    path = tmp_path / "ledger.jsonl"
    path.write_bytes(b"captured ledger bytes")
    replacement = tmp_path / "replacement.jsonl"
    replacement.write_bytes(b"replacement bytes")
    detached = tmp_path / "detached.jsonl"
    original_read = review.os.read
    swapped = False

    def swapping_read(descriptor, size):
        nonlocal swapped
        chunk = original_read(descriptor, size)
        if not swapped:
            swapped = True
            path.rename(detached)
            replacement.rename(path)
        return chunk

    monkeypatch.setattr(review.os, "read", swapping_read)
    with pytest.raises(
        review.ThreeDidRepairReviewError,
        match="(?:input changed during capture|path component changed)",
    ):
        review._capture_regular_file(path, label="fixture", max_bytes=1024)
    assert swapped


def test_cli_is_stdout_only_and_has_no_mutation_mode():
    parser = review._parser()
    destinations = {action.dest for action in parser._actions}
    assert destinations == {"help", "source", "traits", "ledger"}
    for forbidden in ("--apply", "--out", "--output", "--write", "--delete", "--fetch"):
        with pytest.raises(SystemExit):
            parser.parse_args([forbidden])


def test_cli_emits_template_or_nonaccepting_receipt_without_writes(tmp_path, monkeypatch, capsys):
    fresh = _fresh_plan()
    monkeypatch.setattr(review.repair, "plan_from_paths", lambda *_args, **_kwargs: fresh)
    assert review.main([]) == 0
    template_values = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
    assert len(template_values) == 4
    assert template_values[-1]["kind"] == review.TEMPLATE_SUMMARY_KIND

    rows, summary = _completed_rows(overrides={review.REMOVE_DIMENSION: "KEEP_LEGACY_TRAIT"})
    ledger = tmp_path / "completed.jsonl"
    ledger.write_bytes(_ledger_bytes(rows, summary))
    assert review.main(["--ledger", str(ledger)]) == 3
    receipt = json.loads(capsys.readouterr().out)
    assert receipt["status"] == "VALID_NON_ACCEPTING"
    assert receipt["apply_authorized"] is False
    assert "review_set_id" not in receipt


@pytest.mark.skipif(
    not repair.DEFAULT_SOURCE.is_file(),
    reason="ignored pinned 3did production artifact is absent",
)
def test_pinned_production_review_template_matches_exact_partition():
    current_rows, source_rows, planner_summary = repair.plan_from_paths(
        repair.DEFAULT_SOURCE,
        repair.DEFAULT_TRAITS,
    )
    rows, summary = review.build_review_template(current_rows, source_rows, planner_summary)

    assert len(rows) == 100
    assert summary["review_dimension_counts"] == {
        review.ADD_DIMENSION: 53,
        review.REMOVE_DIMENSION: 47,
    }
    assert summary["source_proposal_classification_counts"] == {
        "COLLAPSE_PRIMARY_REPAIR_PROPOSAL": 5,
        "COLLAPSE_SUPPRESSED_REPAIR_PROPOSAL": 6,
        "DIRECT_REPAIR_PROPOSAL": 42,
    }
    assert summary["legacy_collision_key_count"] == 5
    assert summary["legacy_collapsed_extra_source_count"] == 6
    assert summary["planner_plan_id"] == (
        "3did-source-model-repair-plan:"
        "9467cbed048ff0e904895b84519095745934758a6d9029230690e409a32d980b"
    )
    assert summary["bindings_sha256"] == (
        "de54f7f8aac865f29a4396a444d6945e634845054e7287e5cf523d0fcf8a0975"
    )
    assert summary["template_rows_sha256"] == (
        "4236d7f40c1d9d42705799f78576320ea3c8c2802332255487b9ab72286eb1ad"
    )
    assert summary["template_id"] == (
        "3did-source-model-repair-review-template:"
        "c6d60b4ad9c84155b711cb9a81f8d57aab697c51c51e30173caf442b990f808f"
    )
    template = review.dump_review_template(rows, summary)
    assert len(template.encode()) == 353_474
    assert hashlib.sha256(template.encode()).hexdigest() == (
        "848a8882f5b16bd4c69a708512a5e607d557d590b9d7afa9d0a488e4d51a05e1"
    )
    assert all(row["decision"]["action"] is None for row in rows)
