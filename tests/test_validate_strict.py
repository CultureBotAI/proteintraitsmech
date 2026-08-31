"""Unit tests for scripts/validate_strict.py.

Locks in:
- Closed-mode catches unknown top-level fields (the failure mode
  proteintraitsmech#485 is about: `validate-all` advertised closed-mode
  but batched open-mode `linkml-validate` CLI calls).
- Closed-mode also catches unknown nested fields (inside a nested
  attribute like `evolutionary_scope`), not just top-level ones.
- Missing required attributes surface as ERROR rows.
- The error classifier categorizes messages into known buckets.
- iter_yaml_files filters non-YAML and walks directories.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from validate_strict import (  # noqa: E402
    classify,
    iter_yaml_files,
    main,
    validate_one,
)


# ---------------------------------------------------------------- classify


@pytest.mark.parametrize(
    "message, expected_category",
    [
        (
            "Additional properties are not allowed ('bogus_field' was unexpected) in /",
            "unexpected_field",
        ),
        ("'identifier' is a required property in /", "missing_required"),
        ("'foo' is not one of ['bar', 'baz']", "enum_mismatch"),
        (
            "'PTM_BAD' does not match '^[A-Za-z][A-Za-z0-9._-]*:[A-Za-z0-9._-]+$'",
            "pattern_mismatch",
        ),
        ("Something totally weird happened", "other"),
    ],
)
def test_classify_buckets(message, expected_category):
    cat, _detail = classify(message)
    assert cat == expected_category


def test_classify_unexpected_field_extracts_name():
    _cat, detail = classify(
        "Additional properties are not allowed ('bogus_field' was unexpected) in /"
    )
    assert "bogus_field" in detail


# ---------------------------------------------------------------- validate_one


# Minimal valid ProteinTraitRecord that satisfies the closed-mode schema
# (identifier, label, trait_axis are the only required attributes).
_VALID_RECORD = """\
identifier: proteintraitsmech:TEST_RECORD
label: test trait
trait_axis: SEQUENCE
"""


def test_validate_one_clean_yaml_produces_no_errors(tmp_path):
    p = tmp_path / "ok.yaml"
    p.write_text(_VALID_RECORD)
    errors = validate_one(p)
    assert errors == []


def test_validate_one_unknown_top_level_field_fails(tmp_path):
    """Closed-mode must flag an unknown top-level field. This is the
    proteintraitsmech#485 gate: the old batched-CLI validate-all let this
    pass silently."""
    p = tmp_path / "bogus.yaml"
    p.write_text(_VALID_RECORD + "bogus_field: oops\n")
    errors = validate_one(p)
    assert len(errors) >= 1
    cats = {e["category"] for e in errors}
    assert "unexpected_field" in cats


def test_validate_one_unknown_nested_field_fails(tmp_path):
    """Closed-mode must also flag an unknown field nested inside a
    non-scalar attribute (evolutionary_scope), not just at the top level."""
    p = tmp_path / "bogus_nested.yaml"
    p.write_text(
        _VALID_RECORD
        + "evolutionary_scope:\n"
        + "  min_prevalence: 0.1\n"
        + "  max_prevalence: 0.9\n"
        + "  bogus_nested_field: oops\n"
    )
    errors = validate_one(p)
    assert len(errors) >= 1
    cats = {e["category"] for e in errors}
    assert "unexpected_field" in cats


def test_validate_one_missing_required_field_fails(tmp_path):
    """A ProteinTraitRecord without `identifier` must fail validation."""
    p = tmp_path / "missing.yaml"
    p.write_text("label: test trait\ntrait_axis: SEQUENCE\n")
    errors = validate_one(p)
    assert len(errors) >= 1
    cats = {e["category"] for e in errors}
    assert "missing_required" in cats


def test_validate_one_yaml_parse_error_surfaces_as_row(tmp_path):
    p = tmp_path / "broken.yaml"
    p.write_text("identifier: proteintraitsmech:TEST\n  not: aligned\n garbage:\n: bad\n")
    errors = validate_one(p)
    assert any(e["category"] == "yaml_parse_error" for e in errors)


def test_validate_one_enforces_ordered_prints_fingerprint_invariants(tmp_path):
    p = tmp_path / "bad-fingerprint.yaml"
    p.write_text(
        _VALID_RECORD.replace("proteintraitsmech:TEST_RECORD", "PRINTS:PR00001")
        + "sequence_fingerprint_representations:\n"
        + "  - source_accession: PRINTS:PR00001\n"
        + "    source_release: '42.0'\n"
        + "    representation_type: PRINTS_FINAL_ORDERED_MOTIF_SETS\n"
        + "    source_artifact: data/raw/interpro_members/prints42_0.kdat\n"
        + "    source_artifact_sha256: "
        + "47b4f0c32002bce2f9b85f335c942cc52deae8bed54c2b4b2eec5e36c5810771\n"
        + "    source_record_sha256: "
        + "0" * 64
        + "\n"
        + "    compatible_derivation_tool_hint: EMBOSS_PRINTSEXTRACT\n"
        + "    motif_count: 3\n"
        + "    motifs:\n"
        + "      - ordinal: 2\n"
        + "        motif_code: FIRST\n"
        + "        length: 4\n"
        + "        training_instance_count: 2\n"
        + "        source_motif_sha256: "
        + "1" * 64
        + "\n"
        + "        training_distance_from_previous_min: 4\n"
        + "        training_distance_from_previous_max: 1\n"
        + "        inter_motif_distance_constraint:\n"
        + "          region_start_ordinal: 0\n"
        + "          region_end_ordinal: 2\n"
        + "          minimum: 5\n"
        + "          maximum: 2\n"
        + "          repeat_qualified: false\n"
        + "      - ordinal: 1\n"
        + "        motif_code: SECOND\n"
        + "        length: 5\n"
        + "        training_instance_count: 2\n"
        + "        source_motif_sha256: "
        + "2" * 64
        + "\n"
    )
    errors = validate_one(p)
    semantic = [error["message"] for error in errors if error["category"] == "semantic_invariant"]
    assert any("motif_count 3 does not equal 2" in message for message in semantic)
    assert any("motif ordinals must be contiguous" in message for message in semantic)
    assert any("training_distance_from_previous_min exceeds" in message for message in semantic)
    assert any("inter-motif constraint minimum exceeds maximum" in message for message in semantic)
    assert any("constraint REGION must be 1-2" in message for message in semantic)


_VALID_SFLD_PROFILE = """\
identifier: SFLD:SFLDF00001
label: test SFLD family
trait_axis: FUNCTION
sequence_profile_representations:
  - source_accession: SFLD:SFLDF00001
    source_release: '4'
    representation_type: SFLD_4_HMMER3_PROFILE_WITH_CORRELATED_SITES
    source_model_artifact: data/raw/interpro_members/sfld.hmm
    source_model_artifact_sha256: e011a4139e6477a526710b32e8aeaa68203329c799305b015ec35c3b6d09672f
    source_model_record_sha256: '0000000000000000000000000000000000000000000000000000000000000000'
    source_sites_artifact: data/raw/interpro_members/sfld_sites.annot
    source_sites_artifact_sha256: 60ee2408e5bb2bed2eba4ee2101e219b74dcee7abb2bc03aba9e3e905dcf8c66
    source_site_record_sha256: '1111111111111111111111111111111111111111111111111111111111111111'
    source_hierarchy_artifact: data/raw/interpro_members/sfld_hierarchy_flat.txt
    source_hierarchy_artifact_sha256: e9d379421227fb9eb3c5eb259d2a925c321a7bf1e697055d361f7397b53f86b9
    native_classification_level: FAMILY
    model_length: 4
    gathering_sequence_score: 10.5
    gathering_domain_score: 9.25
    training_sequence_count: 3
    hmm_checksum: 3
    profile_search_mode: HMMSEARCH_CUT_GA
    site_coordinate_system: HMM_MODEL_MATCH_STATE
    site_evidence_scope: DIRECT_MODEL_MATCH_ONLY
    site_count: 2
    sites:
      - ordinal: 1
        model_position: 1
        description: nucleophile
      - ordinal: 2
        model_position: 4
    site_feature_pattern_count: 2
    site_feature_patterns:
      - DE
      - DQ
"""


def test_validate_one_accepts_content_addressed_sfld_profile_shape(tmp_path):
    p = tmp_path / "sfld-profile.yaml"
    p.write_text(_VALID_SFLD_PROFILE)
    assert validate_one(p) == []


def test_validate_one_enforces_sfld_profile_cross_field_invariants(tmp_path):
    p = tmp_path / "bad-sfld-profile.yaml"
    broken = (
        _VALID_SFLD_PROFILE.replace(
            "native_classification_level: FAMILY", "native_classification_level: SUBGROUP"
        )
        .replace("site_count: 2", "site_count: 3")
        .replace("site_feature_pattern_count: 2", "site_feature_pattern_count: 3")
        .replace("      - DE\n      - DQ", "      - D\n      - D")
        .replace(
            "source_model_artifact_sha256: e011a4139e6477a526710b32e8aeaa68203329c799305b015ec35c3b6d09672f",
            "source_model_artifact_sha256: " + "f" * 64,
        )
    )
    p.write_text(broken)
    errors = validate_one(p)
    semantic = [error["message"] for error in errors if error["category"] == "semantic_invariant"]

    assert any("site_count 3 does not equal 2" in message for message in semantic)
    assert any("site_feature_pattern_count 3 does not equal 2" in message for message in semantic)
    assert any("FEATURE tuple length must equal site_count" in message for message in semantic)
    assert any("FEATURE tuples must be unique" in message for message in semantic)
    assert any("source_model_artifact_sha256 must be" in message for message in semantic)
    assert any("requires native level FAMILY" in message for message in semantic)


# ---------------------------------------------------------------- iter_yaml_files


def test_iter_yaml_files_walks_directory_and_filters(tmp_path):
    (tmp_path / "a.yaml").write_text("x: 1\n")
    (tmp_path / "b.yml").write_text("x: 2\n")  # .yml — skipped by rglob('*.yaml')
    (tmp_path / "c.txt").write_text("nope")  # non-YAML — skipped
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "d.yaml").write_text("y: 3\n")

    out = iter_yaml_files([tmp_path])
    names = {p.name for p in out}
    # rglob('*.yaml') only picks .yaml (not .yml) when walking a directory
    assert "a.yaml" in names
    assert "d.yaml" in names
    assert "b.yml" not in names
    assert "c.txt" not in names


def test_iter_yaml_files_accepts_yml_file_passed_directly(tmp_path):
    """When a .yml file is passed *as a file argument* (not via dir walk),
    iter_yaml_files accepts it — only the directory rglob is .yaml-only."""
    yml = tmp_path / "explicit.yml"
    yml.write_text("x: 1\n")
    txt = tmp_path / "explicit.txt"
    txt.write_text("nope")

    out = iter_yaml_files([yml, txt])
    names = {p.name for p in out}
    assert "explicit.yml" in names
    assert "explicit.txt" not in names


# ---------------------------------------------------------------- main


def test_main_writes_tsv_header_and_returns_zero_when_clean(tmp_path):
    p = tmp_path / "ok.yaml"
    p.write_text(_VALID_RECORD)
    out = tmp_path / "out.tsv"
    rc = main([str(p), "--out", str(out), "--workers", "1", "--quiet"])
    assert rc == 0
    assert out.read_text().splitlines()[0] == "file\tcategory\tdetail\tpath\tmessage"


def test_main_returns_one_and_writes_error_row_on_failure(tmp_path):
    p = tmp_path / "bogus.yaml"
    p.write_text(_VALID_RECORD + "bogus_field: oops\n")
    out = tmp_path / "out.tsv"
    rc = main([str(p), "--out", str(out), "--workers", "1", "--quiet"])
    assert rc == 1
    rows = out.read_text().splitlines()
    assert len(rows) == 2  # header + one ERROR row
    assert "unexpected_field" in rows[1]


def test_main_fail_on_never_still_returns_zero_on_failure(tmp_path):
    p = tmp_path / "bogus.yaml"
    p.write_text(_VALID_RECORD + "bogus_field: oops\n")
    out = tmp_path / "out.tsv"
    rc = main([str(p), "--out", str(out), "--workers", "1", "--quiet", "--fail-on", "never"])
    assert rc == 0


def test_main_rejects_nonpositive_worker_count(tmp_path):
    p = tmp_path / "ok.yaml"
    p.write_text(_VALID_RECORD)
    with pytest.raises(SystemExit) as error:
        main([str(p), "--workers", "0"])
    assert error.value.code == 2


def test_main_returns_two_when_default_scope_has_no_files(tmp_path, monkeypatch):
    import validate_strict

    monkeypatch.setattr(validate_strict, "DEFAULT_ROOTS", [tmp_path / "does_not_exist"])
    assert main([]) == 2


def test_main_returns_zero_when_all_supplied_paths_are_missing(tmp_path):
    """Deletion-only CI diff: paths were supplied but none exist on disk
    (e.g. every changed data/traits file in the PR was deleted) — this is
    not an error (proteintraitsmech#488 review)."""
    missing = tmp_path / "gone.yaml"
    rc = main([str(missing), "--out", str(tmp_path / "out.tsv")])
    assert rc == 0
