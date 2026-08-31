"""Tests for the no-write SFLD semantic-review boundary."""

from __future__ import annotations

import copy
import hashlib
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import plan_sfld_source_model_migration as planner  # noqa: E402
import review_sfld_source_model_migration as review  # noqa: E402
from sfld_release import (  # noqa: E402
    SfldHmmModel,
    SfldRelease,
    SfldSite,
    SfldSiteRule,
    build_sfld_release_manifest,
)


def _bundle(tmp_path: pathlib.Path):
    root_model = SfldHmmModel(
        accession="SFLDS00001",
        native_classification_level="SUPERFAMILY",
        name="root_chemistry",
        description="root chemistry",
        model_length=3,
        gathering_sequence_score=8.5,
        gathering_domain_score=7.25,
        training_sequence_count=4,
        hmm_checksum=1,
        source_record_sha256="1" * 64,
    )
    family_model = SfldHmmModel(
        accession="SFLDF00001",
        native_classification_level="FAMILY",
        name="mannonate_dehydratase",
        description="mannonate dehydratase",
        model_length=4,
        gathering_sequence_score=10.5,
        gathering_domain_score=9.25,
        training_sequence_count=3,
        hmm_checksum=2,
        source_record_sha256="2" * 64,
    )
    root_site_rule = SfldSiteRule("SFLDS00001", (), (), "3" * 64)
    family_site_rule = SfldSiteRule(
        "SFLDF00001",
        (SfldSite(1, 1, "nucleophile"), SfldSite(2, 4, None)),
        ("DE", "DQ"),
        "4" * 64,
    )
    release = SfldRelease(
        release="4",
        hmm_path=pathlib.Path("captured.hmm"),
        hierarchy_path=pathlib.Path("captured.hierarchy"),
        sites_path=pathlib.Path("captured.sites"),
        hmm_sha256="3" * 64,
        hierarchy_sha256="4" * 64,
        sites_sha256="5" * 64,
        models={
            root_model.accession: root_model,
            family_model.accession: family_model,
        },
        site_rules={
            root_site_rule.accession: root_site_rule,
            family_site_rule.accession: family_site_rule,
        },
        ancestors={"SFLDF00001": ("SFLDS00001",)},
        direct_parents={"SFLDF00001": "SFLDS00001"},
    )
    snapshot = planner.SourceSnapshot(
        release=release,
        manifest=build_sfld_release_manifest(release),
        interpro_types={"IPR000001": "domain", "IPR000002": "family"},
        interpro_xml_sha256="6" * 64,
    )

    traits = tmp_path / "data/traits/function/protein_family/sfld"
    traits.mkdir(parents=True)
    records: dict[str, planner.TraitCapture] = {}
    values = [
        {
            "identifier": "SFLD:SFLDS00001",
            "label": "root chemistry",
            "definition": "A current integrating family abstract.",
            "definition_source": "InterPro:IPR000002 abstract (SFLD member signature)",
            "trait_axis": "FUNCTION",
            "trait_category": "FUNC_PROTEIN_FAMILY",
            "mapped_xrefs": [
                {
                    "object": "InterPro:IPR000002",
                    "mapping_source": "interpro-member-list",
                }
            ],
        },
        {
            "identifier": "SFLD:SFLDF00001",
            "label": "mannonate dehydratase",
            "definition": "A current integrating domain abstract.",
            "definition_source": "InterPro:IPR000001 abstract (SFLD member signature)",
            "trait_axis": "FUNCTION",
            "trait_category": "FUNC_PROTEIN_FAMILY",
            "parent_traits": ["SFLD:SFLDS00001"],
            "mapped_xrefs": [
                {
                    "object": "InterPro:IPR000001",
                    "mapping_source": "interpro-member-list",
                }
            ],
        },
        {
            "identifier": "SFLD:SFLDG99999",
            "label": "model-less signature",
            "definition": "A generated signature restatement.",
            "definition_source": ("SFLD signature name (composed; no curated InterPro abstract)"),
            "trait_axis": "FUNCTION",
            "trait_category": "FUNC_PROTEIN_FAMILY",
        },
    ]
    for value in values:
        accession = value["identifier"].split(":", 1)[1]
        path = traits / f"{accession.lower()}.yaml"
        raw = yaml.safe_dump(value, sort_keys=False).encode()
        path.write_bytes(raw)
        records[value["identifier"]] = planner.TraitCapture(
            path=path,
            relative_to_traits=path.relative_to(tmp_path / "data/traits"),
            record=value,
            yaml_sha256=hashlib.sha256(raw).hexdigest(),
        )

    return planner.build_plan(
        records=records,
        snapshot=snapshot,
        repo_root=tmp_path,
        expected_modelless_accessions=frozenset({"SFLDG99999"}),
    )


def _template(tmp_path: pathlib.Path):
    planner_rows, planner_summary = _bundle(tmp_path)
    rows, summary = review.build_review_template(planner_rows, planner_summary)
    return planner_rows, planner_summary, rows, summary


def _complete(
    rows,
    *,
    routing_action: str = "KEEP_FUNCTION_PROTEIN_FAMILY_ROUTE",
    routing_actions: dict[str, str] | None = None,
    override_dimension: str | None = None,
    override_action: str | None = None,
):
    completed = copy.deepcopy(rows)
    positive = {
        review.ROUTING_DIMENSION: routing_action,
        review.DEFINITION_DIMENSION: "KEEP_CURRENT_LABEL_AND_DEFINITION",
        review.PROFILE_DIMENSION: "APPROVE_SOURCE_PROFILE_PROJECTION",
        review.MODELLESS_DIMENSION: "RETAIN_MODELLESS_REFERENCE_ONLY",
    }
    if override_dimension is not None:
        assert override_action is not None
        positive[override_dimension] = override_action
    for row in completed:
        dimension = row["binding"]["review_dimension"]
        action = positive[dimension]
        if dimension == review.ROUTING_DIMENSION and routing_actions is not None:
            action = routing_actions.get(row["binding"]["target_identifier"], action)
        row["decision"] = {
            "action": action,
            "reviewer": "curator@example.org",
            "reviewed_at": "2026-08-25T12:34:56Z",
            "comment": "Reviewed against the bound source and current record.",
        }
    return completed


def test_template_is_exhaustive_blank_and_apply_incapable(tmp_path):
    planner_rows, planner_summary, rows, summary = _template(tmp_path)

    assert len(planner_rows) == 3
    assert summary["planner_plan_id"] == planner_summary["plan_id"]
    assert summary["review_item_count"] == 9
    assert summary["review_dimension_counts"] == {
        review.DEFINITION_DIMENSION: 3,
        review.MODELLESS_DIMENSION: 1,
        review.ROUTING_DIMENSION: 3,
        review.PROFILE_DIMENSION: 2,
    }
    assert not summary["writer_available"]
    assert not summary["apply_authorized"]
    assert not summary["grounding_eligible"]
    assert summary["serialization_status"] == "NOT_PERFORMED"
    assert all(set(row) == review._ROW_FIELDS for row in rows)
    assert all(set(row["decision"]) == review._DECISION_FIELDS for row in rows)
    assert all(all(value is None for value in row["decision"].values()) for row in rows)
    assert all(row["binding_sha256"] == review.value_sha256(row["binding"]) for row in rows)
    assert summary["template_rows_sha256"] == review.rows_sha256(rows)
    assert summary["template_id"].startswith(review.TEMPLATE_ID_PREFIX)

    routing = next(
        row for row in rows if row["binding"]["review_dimension"] == review.ROUTING_DIMENSION
    )
    assert routing["binding"]["route_targets"] == review.ROUTE_TARGETS
    assert "ROUTE_TO_SEQUENCE_DOMAIN" in routing["binding"]["decision_options"]
    profile = next(
        row
        for row in rows
        if row["binding"]["review_dimension"] == review.PROFILE_DIMENSION
        and row["binding"]["target_identifier"] == "SFLD:SFLDF00001"
    )
    assert profile["binding"]["source_profile_projection"]["site_feature_patterns"] == [
        "DE",
        "DQ",
    ]


def test_template_is_deterministic_and_binds_each_planner_row(tmp_path):
    planner_rows, planner_summary = _bundle(tmp_path)
    first_rows, first_summary = review.build_review_template(planner_rows, planner_summary)
    second_rows, second_summary = review.build_review_template(planner_rows, planner_summary)

    assert first_rows == second_rows
    assert first_summary == second_summary
    planner_hashes = {row["row_sha256"] for row in planner_rows}
    assert {row["binding"]["planner_row_sha256"] for row in first_rows} == planner_hashes
    assert review.dump_review_template(first_rows, first_summary).endswith("\n")


def test_complete_positive_ledger_accepts_only_a_semantic_plan(tmp_path):
    _planner_rows, _planner_summary, rows, summary = _template(tmp_path)
    completed = _complete(rows, routing_action="ROUTE_TO_SEQUENCE_DOMAIN")
    ledger = review.dump_review_template(completed, summary).encode()

    receipt = review.validate_completed_ledger(
        completed,
        summary,
        expected_rows=rows,
        expected_summary=summary,
        ledger_bytes=ledger,
    )

    assert receipt["status"] == "ACCEPTED_SEMANTIC_PLAN_ONLY"
    assert receipt["proposal_compatible"]
    assert receipt["accepted_for_next_phase"]
    assert receipt["review_set_id"].startswith(review.REVIEW_SET_ID_PREFIX)
    assert receipt["routing_decision_counts"] == {"ROUTE_TO_SEQUENCE_DOMAIN": 3}
    assert receipt["cross_route_source_parent_edge_count"] == 0
    assert not receipt["apply_authorized"]
    assert receipt["serialization_status"] == "NOT_PERFORMED"
    assert not receipt["writes_performed"]
    assert not receipt["writer_available"]
    assert not receipt["grounding_eligible"]


def test_cross_route_source_parent_edge_is_valid_but_nonaccepting(tmp_path):
    _planner_rows, _planner_summary, rows, summary = _template(tmp_path)
    completed = _complete(
        rows,
        routing_actions={
            "SFLD:SFLDS00001": "KEEP_FUNCTION_PROTEIN_FAMILY_ROUTE",
            "SFLD:SFLDF00001": "ROUTE_TO_SEQUENCE_DOMAIN",
        },
    )
    ledger = review.dump_review_template(completed, summary).encode()

    receipt = review.validate_completed_ledger(
        completed,
        summary,
        expected_rows=rows,
        expected_summary=summary,
        ledger_bytes=ledger,
    )

    assert receipt["status"] == "VALID_NON_ACCEPTING"
    assert not receipt["accepted_for_next_phase"]
    assert receipt["cross_route_source_parent_edge_count"] == 1
    assert receipt["cross_route_source_parent_edges"] == [
        {
            "child": "SFLD:SFLDF00001",
            "parent": "SFLD:SFLDS00001",
            "status": "CROSS_ROUTE_SOURCE_PARENT_EDGE_REQUIRES_REPLAN",
        }
    ]


@pytest.mark.parametrize(
    ("dimension", "action"),
    [
        (review.ROUTING_DIMENSION, "REQUEST_ROUTING_REPLAN"),
        (review.DEFINITION_DIMENSION, "BLOCK_CURRENT_LABEL_OR_DEFINITION"),
        (review.PROFILE_DIMENSION, "REQUEST_SOURCE_MODEL_REPLAN"),
        (review.MODELLESS_DIMENSION, "BLOCK_MODELLESS_RECORD"),
    ],
)
def test_structurally_valid_block_or_replan_is_nonaccepting(tmp_path, dimension, action):
    _planner_rows, _planner_summary, rows, summary = _template(tmp_path)
    completed = _complete(rows, override_dimension=dimension, override_action=action)
    ledger = review.dump_review_template(completed, summary).encode()

    receipt = review.validate_completed_ledger(
        completed,
        summary,
        expected_rows=rows,
        expected_summary=summary,
        ledger_bytes=ledger,
    )

    assert receipt["status"] == "VALID_NON_ACCEPTING"
    assert not receipt["proposal_compatible"]
    assert not receipt["accepted_for_next_phase"]
    assert "review_set_id" not in receipt


def test_completed_ledger_rejects_binding_tamper_reordering_and_stale_summary(tmp_path):
    _planner_rows, _planner_summary, rows, summary = _template(tmp_path)
    completed = _complete(rows)

    tampered = copy.deepcopy(completed)
    tampered[0]["binding"]["target_identifier"] = "SFLD:SFLDF99998"
    with pytest.raises(review.SfldMigrationReviewError, match="immutable review binding"):
        review.validate_completed_ledger(
            tampered,
            summary,
            expected_rows=rows,
            expected_summary=summary,
            ledger_bytes=review.dump_review_template(tampered, summary).encode(),
        )

    reordered = list(reversed(completed))
    with pytest.raises(review.SfldMigrationReviewError, match="immutable review binding"):
        review.validate_completed_ledger(
            reordered,
            summary,
            expected_rows=rows,
            expected_summary=summary,
            ledger_bytes=review.dump_review_template(reordered, summary).encode(),
        )

    stale = dict(summary)
    stale["planner_plan_id"] = planner.PLAN_ID_PREFIX + "0" * 64
    with pytest.raises(review.SfldMigrationReviewError, match="summary is stale"):
        review.validate_completed_ledger(
            completed,
            stale,
            expected_rows=rows,
            expected_summary=summary,
            ledger_bytes=review.dump_review_template(completed, stale).encode(),
        )


def test_completed_ledger_requires_real_metadata_and_exact_supplied_bytes(tmp_path):
    _planner_rows, _planner_summary, rows, summary = _template(tmp_path)
    completed = _complete(rows)

    malformed = copy.deepcopy(completed)
    malformed[0]["decision"]["reviewed_at"] = "2026-02-30T12:34:56Z"
    with pytest.raises(review.SfldMigrationReviewError, match="not a real timestamp"):
        review.validate_completed_ledger(
            malformed,
            summary,
            expected_rows=rows,
            expected_summary=summary,
            ledger_bytes=review.dump_review_template(malformed, summary).encode(),
        )

    canonical = review.dump_review_template(completed, summary).encode()
    with pytest.raises(review.SfldMigrationReviewError, match="bytes do not match"):
        review.validate_completed_ledger(
            completed,
            summary,
            expected_rows=rows,
            expected_summary=summary,
            ledger_bytes=canonical + b"\n",
        )


def test_planner_partition_rejects_tampered_rows_and_open_write_state(tmp_path):
    planner_rows, planner_summary = _bundle(tmp_path)
    tampered_rows = copy.deepcopy(planner_rows)
    tampered_rows[0]["definition_status"] = "ALTERED"
    with pytest.raises(review.SfldMigrationReviewError, match="row hash mismatch"):
        review.build_review_template(tampered_rows, planner_summary)

    altered_summary = dict(planner_summary)
    altered_summary["writer_available"] = True
    altered_summary_without_id = dict(altered_summary)
    altered_summary_without_id.pop("plan_id")
    altered_summary["plan_id"] = planner.PLAN_ID_PREFIX + planner.value_sha256(
        altered_summary_without_id
    )
    with pytest.raises(review.SfldMigrationReviewError, match="writer/apply path"):
        review.build_review_template(planner_rows, altered_summary)


def test_review_compiler_fails_closed_on_new_unhandled_planner_requirement(tmp_path):
    planner_rows, planner_summary = _bundle(tmp_path)
    altered_rows = copy.deepcopy(planner_rows)
    altered_rows[0]["review_requirements"].append("FUTURE_UNHANDLED_REVIEW")
    row_without_hash = {key: value for key, value in altered_rows[0].items() if key != "row_sha256"}
    altered_rows[0]["row_sha256"] = planner.value_sha256(row_without_hash)
    altered_summary = copy.deepcopy(planner_summary)
    altered_summary["rows_sha256"] = planner.rows_sha256(altered_rows)
    altered_summary_without_id = dict(altered_summary)
    altered_summary_without_id.pop("plan_id")
    altered_summary["plan_id"] = planner.PLAN_ID_PREFIX + planner.value_sha256(
        altered_summary_without_id
    )

    with pytest.raises(review.SfldMigrationReviewError, match="does not cover"):
        review.build_review_template(altered_rows, altered_summary)


def test_completed_ledger_reader_requires_canonical_exact_lf_regular_file(tmp_path):
    _planner_rows, _planner_summary, rows, summary = _template(tmp_path)
    completed = _complete(rows)
    canonical = review.dump_review_template(completed, summary)
    ledger = tmp_path / "completed.jsonl"
    ledger.write_text(canonical)

    supplied_rows, supplied_summary, raw = review._read_completed_ledger(ledger)
    assert supplied_rows == completed
    assert supplied_summary == summary
    assert raw == canonical.encode()

    ledger.write_bytes(canonical.replace("\n", "\r\n").encode())
    with pytest.raises(review.SfldMigrationReviewError, match="CR/CRLF"):
        review._read_completed_ledger(ledger)

    ledger.write_text(canonical.rstrip("\n"))
    with pytest.raises(review.SfldMigrationReviewError, match="LF-terminated"):
        review._read_completed_ledger(ledger)


def test_completed_ledger_reader_rejects_duplicate_json_keys_and_symlink(tmp_path):
    duplicate = tmp_path / "duplicate.jsonl"
    duplicate.write_text('{"a":1,"a":1}\n{}\n')
    with pytest.raises(review.SfldMigrationReviewError, match="duplicate JSON key"):
        review._read_completed_ledger(duplicate)

    target = tmp_path / "target.jsonl"
    target.write_text("{}\n{}\n")
    link = tmp_path / "link.jsonl"
    link.symlink_to(target)
    with pytest.raises(review.SfldMigrationReviewError, match="cannot safely open regular file"):
        review._read_completed_ledger(link)


def test_main_emits_template_or_nonaccepting_receipt_without_writes(
    tmp_path,
    monkeypatch,
    capsys,
):
    planner_rows, planner_summary, rows, summary = _template(tmp_path)
    monkeypatch.setattr(
        review,
        "replay_migration_plan",
        lambda _args: (planner_rows, planner_summary),
    )

    assert review.main([]) == 0
    emitted = capsys.readouterr()
    assert emitted.err == ""
    assert emitted.out == review.dump_review_template(rows, summary)

    completed = _complete(
        rows,
        override_dimension=review.DEFINITION_DIMENSION,
        override_action="REQUEST_LABEL_OR_DEFINITION_REPLAN",
    )
    ledger = tmp_path / "review.jsonl"
    ledger.write_text(review.dump_review_template(completed, summary))
    assert review.main(["--ledger", str(ledger)]) == 3
    receipt_output = capsys.readouterr()
    assert receipt_output.err == ""
    assert '"status":"VALID_NON_ACCEPTING"' in receipt_output.out


def test_cli_surface_has_no_output_apply_writer_or_grounding_option():
    option_strings = {
        option for action in review._parser()._actions for option in action.option_strings
    }
    assert "--ledger" in option_strings
    for forbidden in ("--output", "--apply", "--write", "--ground", "--promote"):
        assert forbidden not in option_strings
