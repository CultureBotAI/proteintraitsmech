"""Focused tests for direct SFLD match-state and correlated-site evaluation."""

from __future__ import annotations

import json
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import sfld_match as matcher  # noqa: E402
from sfld_match import (  # noqa: E402
    SfldMatchError,
    evaluate_sfld_alignment,
    map_model_match_states,
    parse_hmmer_stockholm,
)
from sfld_release import (  # noqa: E402
    SfldHmmModel,
    SfldRelease,
    SfldSite,
    SfldSiteRule,
    canonical_json,
)


def _model(accession: str, level: str, length: int, digit: str) -> SfldHmmModel:
    return SfldHmmModel(
        accession=accession,
        native_classification_level=level,
        name=f"model_{accession}",
        description=f"test model {accession}",
        model_length=length,
        gathering_sequence_score=10.5,
        gathering_domain_score=9.25,
        training_sequence_count=3,
        hmm_checksum=int(digit),
        source_record_sha256=digit * 64,
    )


@pytest.fixture
def release(tmp_path: pathlib.Path) -> SfldRelease:
    models = {
        "SFLDS00001": _model("SFLDS00001", "SUPERFAMILY", 2, "1"),
        "SFLDG00001": _model("SFLDG00001", "SUBGROUP", 3, "2"),
        "SFLDF00001": _model("SFLDF00001", "FAMILY", 4, "3"),
    }
    rules = {
        "SFLDS00001": SfldSiteRule("SFLDS00001", (), (), "4" * 64),
        "SFLDG00001": SfldSiteRule(
            "SFLDG00001",
            (SfldSite(1, 2, "general acid"),),
            ("D",),
            "5" * 64,
        ),
        "SFLDF00001": SfldSiteRule(
            "SFLDF00001",
            (
                SfldSite(1, 1, "nucleophile"),
                SfldSite(2, 4, None),
            ),
            # DQ is deliberately absent even though D and Q each occur at the
            # respective position across the two source tuples.
            ("DE", "AQ"),
            "6" * 64,
        ),
    }
    return SfldRelease(
        release="4",
        hmm_path=tmp_path / "sfld.hmm",
        hierarchy_path=tmp_path / "sfld_hierarchy_flat.txt",
        sites_path=tmp_path / "sfld_sites.annot",
        hmm_sha256="7" * 64,
        hierarchy_sha256="8" * 64,
        sites_sha256="9" * 64,
        models=models,
        site_rules=rules,
        ancestors={
            "SFLDG00001": ("SFLDS00001",),
            "SFLDF00001": ("SFLDG00001", "SFLDS00001"),
        },
        direct_parents={
            "SFLDG00001": "SFLDS00001",
            "SFLDF00001": "SFLDG00001",
        },
    )


def _family_stockholm(*, final_residue: str = "E", accession: str = "SFLDF00001") -> str:
    return (
        "# STOCKHOLM 1.0\n"
        f"#=GF AC {accession}\n"
        "#=GF ID model_SFLDF00001\n"
        "target/1-6 Dac-\n"
        "#=GR target/1-6 PP 999.\n"
        "#=GC RF R..x\n"
        "\n"
        f"target/1-6 D{final_residue}g\n"
        "#=GC RF xx.\n"
        "//\n"
    )


def test_wrapped_interleaved_stockholm_maps_rf_states_to_one_based_target_residues():
    alignment = parse_hmmer_stockholm(_family_stockholm())
    mapping = map_model_match_states(alignment, expected_model_length=4)

    assert alignment.model_accession == "SFLDF00001"
    assert alignment.target_identifier == "target/1-6"
    assert alignment.aligned_target == "Dac-DEg"
    # Every non-dot/non-gap RF column is a state; insertion residues still
    # advance target coordinates, and a non-site deletion remains explicit.
    assert [entry.as_dict() for entry in mapping] == [
        {
            "alignment_column": 1,
            "domain_subsequence_position": 1,
            "model_position": 1,
            "residue": "D",
        },
        {
            "alignment_column": 4,
            "domain_subsequence_position": None,
            "model_position": 2,
            "residue": None,
        },
        {
            "alignment_column": 5,
            "domain_subsequence_position": 4,
            "model_position": 3,
            "residue": "D",
        },
        {
            "alignment_column": 6,
            "domain_subsequence_position": 5,
            "model_position": 4,
            "residue": "E",
        },
    ]


def test_complete_correlated_tuple_qualifies_and_ancestor_projections_clear_sites(release):
    result = evaluate_sfld_alignment(
        release,
        "SFLDF00001",
        parse_hmmer_stockholm(_family_stockholm()),
    )

    direct = result["direct_model_evaluation"]
    assert result["grounding_eligible"] is False
    assert result["qualification_status"] == "DIAGNOSTIC_ALIGNMENT_ONLY_NOT_PROFILE_QUALIFIED"
    assert direct["profile_threshold_evaluation"] == "NOT_PROVIDED_ALIGNMENT_ONLY"
    assert direct["profile_threshold_qualified"] is None
    assert direct["site_rule_status"] == "MATCHED_CORRELATED_TUPLE"
    assert direct["correlated_site_tuple_matched"] is True
    assert "site_rule_qualified" not in direct
    assert direct["site_evidence"] == {
        "mapped_sites": [
            {
                "description": "nucleophile",
                "domain_subsequence_position": 1,
                "model_position": 1,
                "ordinal": 1,
                "residue": "D",
            },
            {
                "description": None,
                "domain_subsequence_position": 5,
                "model_position": 4,
                "ordinal": 2,
                "residue": "E",
            },
        ],
        "matched_feature_pattern": "DE",
        "observed_residue_tuple": "DE",
        "source_site_record_sha256": "6" * 64,
    }
    assert result["source_binding"] == {
        "hierarchy_artifact_sha256": "8" * 64,
        "hmm_artifact_sha256": "7" * 64,
        "manifest_sha256": result["source_binding"]["manifest_sha256"],
        "sites_artifact_sha256": "9" * 64,
        "source_release": "4",
    }
    assert len(result["source_binding"]["manifest_sha256"]) == 64
    assert result["target"] == {
        "aligned_column_count": 7,
        "alignment_source_sha256": result["target"]["alignment_source_sha256"],
        "coordinate_basis": "ONE_BASED_HMMSEARCH_DOMAIN_SUBSEQUENCE",
        "identifier": "target/1-6",
        "parent_sequence_binding_verified": False,
        "parent_sequence_identifier": "target",
        "reported_parent_end": 6,
        "reported_parent_start": 1,
        "ungapped_residue_count": 6,
    }

    assert result["diagnostic_potential_ancestor_projections"] == [
        {
            "accession": "SFLDG00001",
            "distance_from_direct_model": 1,
            "grounding_eligible": False,
            "native_classification_level": "SUBGROUP",
            "profile_threshold_qualified": None,
            "projection_basis": "SFLD_HIERARCHY_FROM_DIRECT_MODEL",
            "source_model_record_sha256": "2" * 64,
        },
        {
            "accession": "SFLDS00001",
            "distance_from_direct_model": 2,
            "grounding_eligible": False,
            "native_classification_level": "SUPERFAMILY",
            "profile_threshold_qualified": None,
            "projection_basis": "SFLD_HIERARCHY_FROM_DIRECT_MODEL",
            "source_model_record_sha256": "1" * 64,
        },
    ]
    assert "ancestor_projections" not in result
    forbidden = {
        "alignment_mapping",
        "mapped_sites",
        "matched_feature_pattern",
        "observed_residue_tuple",
        "residue",
        "site_evidence",
        "domain_subsequence_position",
    }
    assert all(
        forbidden.isdisjoint(projection)
        for projection in result["diagnostic_potential_ancestor_projections"]
    )


def test_individually_allowed_residues_do_not_replace_correlated_tuple(release):
    result = evaluate_sfld_alignment(
        release,
        "SFLDF00001",
        parse_hmmer_stockholm(_family_stockholm(final_residue="Q")),
    )

    direct = result["direct_model_evaluation"]
    assert direct["site_evidence"]["observed_residue_tuple"] == "DQ"
    assert direct["site_evidence"]["matched_feature_pattern"] is None
    assert direct["site_rule_status"] == "MISMATCHED_CORRELATED_TUPLE"
    assert direct["correlated_site_tuple_matched"] is False
    assert result["diagnostic_potential_ancestor_projections"] == []


@pytest.mark.parametrize(
    ("text", "message"),
    [
        (
            _family_stockholm().replace("#=GF AC SFLDF00001\n", ""),
            "exactly one #=GF AC",
        ),
        (
            _family_stockholm().replace(
                "#=GF AC SFLDF00001\n",
                "#=GF AC SFLDF00001\n#=GF AC SFLDF00001\n",
            ),
            "exactly one #=GF AC",
        ),
        (
            _family_stockholm().replace("target/1-6 DEg", "other/1-3 DEg"),
            "exactly one target sequence",
        ),
        (
            _family_stockholm().replace("#=GC RF xx.\n", ""),
            "target fragment but no #=GC RF fragment",
        ),
        (_family_stockholm().replace("Dac-", "Da*-"), "invalid aligned target"),
        (_family_stockholm().replace("//\n", "//\ntrailing AA\n"), "content follows"),
    ],
)
def test_ambiguous_or_malformed_stockholm_input_fails_closed(text, message):
    with pytest.raises(SfldMatchError, match=message):
        parse_hmmer_stockholm(text)


@pytest.mark.parametrize(
    ("text", "message"),
    [
        (
            _family_stockholm().replace("#=GC RF R..x\n", ""),
            "target fragment but no #=GC RF fragment",
        ),
        (
            _family_stockholm().replace(
                "target/1-6 Dac-\n#=GR target/1-6 PP 999.\n#=GC RF R..x\n",
                "#=GC RF R..x\ntarget/1-6 Dac-\n",
            ),
            "#=GC RF fragment appears before",
        ),
        (
            _family_stockholm().replace(
                "target/1-6 Dac-\n",
                "target/1-6 Dac-\ntarget/1-6 Dac-\n",
            ),
            "duplicate target fragments",
        ),
        (
            _family_stockholm().replace(
                "#=GC RF R..x\n",
                "#=GC RF R..x\n#=GC RF R..x\n",
            ),
            "duplicate #=GC RF fragments",
        ),
        (
            _family_stockholm().replace("#=GC RF R..x\n", "#=GC RF R.x\n"),
            "different lengths",
        ),
    ],
)
def test_each_interleaved_stockholm_block_must_be_complete_ordered_and_aligned(text, message):
    with pytest.raises(SfldMatchError, match=message):
        parse_hmmer_stockholm(text)


@pytest.mark.parametrize(
    ("identifier", "message"),
    [
        ("target", "canonical parent_identifier/start-end"),
        ("target/0-5", "canonical parent_identifier/start-end"),
        ("target/1-0", "canonical parent_identifier/start-end"),
        ("target/7-6", "start bound must not exceed end bound"),
        ("target/01-06", "canonical parent_identifier/start-end"),
        ("target/1-5", "span must equal"),
        ("target/20-26", "span must equal"),
    ],
)
def test_target_identifier_requires_positive_canonical_bounds_matching_domain_length(
    identifier, message
):
    with pytest.raises(SfldMatchError, match=message):
        parse_hmmer_stockholm(_family_stockholm().replace("target/1-6", identifier))


def test_reported_parent_bounds_do_not_become_verified_parent_coordinates(release):
    text = _family_stockholm().replace("target/1-6", "UniProtKB:P12345/41-46")
    result = evaluate_sfld_alignment(
        release,
        "SFLDF00001",
        parse_hmmer_stockholm(text),
    )

    assert result["target"]["parent_sequence_identifier"] == "UniProtKB:P12345"
    assert result["target"]["reported_parent_start"] == 41
    assert result["target"]["reported_parent_end"] == 46
    assert result["target"]["parent_sequence_binding_verified"] is False
    assert result["target"]["coordinate_basis"] == "ONE_BASED_HMMSEARCH_DOMAIN_SUBSEQUENCE"
    assert (
        result["direct_model_evaluation"]["site_evidence"]["mapped_sites"][0][
            "domain_subsequence_position"
        ]
        == 1
    )


def test_repeated_domain_shape_with_more_than_one_target_per_block_fails_closed():
    text = (
        "# STOCKHOLM 1.0\n"
        "#=GF AC SFLDF00001\n"
        "target/1-6 Dac-\n"
        "target/7-12 Dac-\n"
        "#=GC RF R..x\n"
        "\n"
        "target/1-6 DEg\n"
        "target/7-12 DEg\n"
        "#=GC RF xx.\n"
        "//\n"
    )
    with pytest.raises(SfldMatchError, match="duplicate target fragments"):
        parse_hmmer_stockholm(text)


def test_source_model_length_site_deletion_and_ambiguous_site_residue_fail_closed(release):
    mismatched_source = parse_hmmer_stockholm(_family_stockholm(accession="SFLDG00001"))
    with pytest.raises(SfldMatchError, match="#=GF AC source mismatch"):
        evaluate_sfld_alignment(release, "SFLDF00001", mismatched_source)

    too_short = parse_hmmer_stockholm(_family_stockholm().replace("#=GC RF xx.", "#=GC RF x.."))
    with pytest.raises(SfldMatchError, match="RF model length mismatch"):
        evaluate_sfld_alignment(release, "SFLDF00001", too_short)

    deleted_site = parse_hmmer_stockholm(
        _family_stockholm(final_residue="-").replace("target/1-6", "target/1-5")
    )
    with pytest.raises(SfldMatchError, match="target deletion at annotated"):
        evaluate_sfld_alignment(release, "SFLDF00001", deleted_site)

    ambiguous_site = parse_hmmer_stockholm(_family_stockholm(final_residue="X"))
    with pytest.raises(SfldMatchError, match="ambiguous target residue"):
        evaluate_sfld_alignment(release, "SFLDF00001", ambiguous_site)


def test_site_free_model_has_no_correlated_tuple_to_mismatch(release):
    alignment = parse_hmmer_stockholm(
        "# STOCKHOLM 1.0\n#=GF AC SFLDS00001\ntarget/1-2 AX\n#=GC RF xx\n//\n"
    )
    result = evaluate_sfld_alignment(release, "SFLDS00001", alignment)

    direct = result["direct_model_evaluation"]
    assert direct["site_rule_status"] == "NO_SITES_DECLARED"
    assert direct["correlated_site_tuple_matched"] is True
    assert direct["site_evidence"] is None


def test_unknown_model_and_broken_hierarchy_fail_closed(release):
    alignment = parse_hmmer_stockholm(_family_stockholm())
    with pytest.raises(SfldMatchError, match="absent from the release"):
        evaluate_sfld_alignment(release, "SFLDF99999", alignment)

    release.ancestors["SFLDF00001"] = ("SFLDS00001",)
    with pytest.raises(SfldMatchError, match="hierarchy closure mismatch"):
        evaluate_sfld_alignment(release, "SFLDF00001", alignment)


def test_cli_prints_only_canonical_json_and_never_writes(monkeypatch, tmp_path, capsys, release):
    alignment_path = tmp_path / "hit.sto"
    alignment_path.write_text(_family_stockholm(), encoding="ascii")
    monkeypatch.setattr(matcher, "load_sfld_release", lambda *args, **kwargs: release)

    before = {
        path.relative_to(tmp_path): path.read_bytes()
        for path in tmp_path.rglob("*")
        if path.is_file()
    }
    assert (
        matcher.main(
            [
                "--alignment",
                str(alignment_path),
                "--model-accession",
                "SFLDF00001",
            ]
        )
        == 0
    )
    after = {
        path.relative_to(tmp_path): path.read_bytes()
        for path in tmp_path.rglob("*")
        if path.is_file()
    }

    captured = capsys.readouterr()
    parsed = json.loads(captured.out)
    assert captured.out == canonical_json(parsed) + "\n"
    assert captured.err == ""
    assert after == before
