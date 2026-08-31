"""Regression tests for the fail-closed SFLD 4 three-artifact parser."""

from __future__ import annotations

import hashlib
import json
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import sfld_release as sfld  # noqa: E402
from sfld_release import (  # noqa: E402
    SfldChecksumError,
    SfldReleaseError,
    build_sfld_profile_representation,
    build_sfld_release_manifest,
    load_sfld_release,
)
from validate_strict import validate_one  # noqa: E402


def _hmm(accession: str, length: int, *, checksum: int) -> bytes:
    scores_20 = " ".join(["1.0"] * 20)
    scores_7 = " ".join(["1.0"] * 7)
    matrix = b"".join(
        (
            f"      {position} {scores_20} {position} a x - -\n"
            f"          {scores_20}\n"
            f"          {scores_7}\n"
        ).encode()
        for position in range(1, length + 1)
    )
    return (
        b"HMMER3/f [3.1b1 | May 2013]\n"
        + f"NAME  Model_{accession}\n".encode()
        + f"ACC   {accession}\n".encode()
        + f"DESC  Test model {accession}\n".encode()
        + f"LENG  {length}\n".encode()
        + b"ALPH  amino\n"
        + b"RF    yes\n"
        + b"MM    no\n"
        + b"CONS  yes\n"
        + b"CS    no\n"
        + b"MAP   yes\n"
        + b"NSEQ  3\n"
        + f"CKSUM {checksum}\n".encode()
        + b"GA    10.50 9.25\n"
        + b"HMM          A C D E F G H I K L M N P Q R S T V W Y\n"
        + b"            m->m m->i m->d i->m i->i d->m d->d\n"
        + f"  COMPO  {scores_20}\n".encode()
        + f"          {scores_20}\n".encode()
        + f"          {scores_7}\n".encode()
        + matrix
        + b"//\n"
    )


HMM = (
    _hmm("SFLDS00001", 3, checksum=1)
    + _hmm("SFLDG00001", 3, checksum=2)
    + _hmm("SFLDF00001", 4, checksum=3)
)
SITES = (
    b"## MSA feature annotation file\n"
    b"# Format version: 1.1\n"
    b"# MSA file: sfld.msa\n"
    b"# Date 2018-07-03 14:44:20\n"
    b"ACC SFLDS00001 0 0\n"
    b"ACC SFLDG00001 1 1\n"
    b"SITE 2 general acid\n"
    b"FEATURE D\n"
    b"ACC SFLDF00001 2 2\n"
    b"SITE 1 nucleophile\n"
    b"SITE 4 \n"
    b"FEATURE DE\n"
    b"FEATURE DQ\n"
)
HIERARCHY = b"SFLDG00001: SFLDS00001\nSFLDF00001: SFLDS00001 SFLDG00001\n"


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _load(
    tmp_path: pathlib.Path,
    *,
    hmm: bytes = HMM,
    sites: bytes = SITES,
    hierarchy: bytes = HIERARCHY,
):
    hmm_path = tmp_path / "sfld.hmm"
    sites_path = tmp_path / "sfld_sites.annot"
    hierarchy_path = tmp_path / "sfld_hierarchy_flat.txt"
    hmm_path.write_bytes(hmm)
    sites_path.write_bytes(sites)
    hierarchy_path.write_bytes(hierarchy)
    return load_sfld_release(
        hmm_path,
        hierarchy_path,
        sites_path,
        expected_hmm_sha256=_sha(hmm),
        expected_hierarchy_sha256=_sha(hierarchy),
        expected_sites_sha256=_sha(sites),
        enforce_release_contract=False,
    )


def test_release_preserves_ga_native_levels_correlated_sites_and_hierarchy(tmp_path):
    release = _load(tmp_path)

    family = release.models["SFLDF00001"]
    assert family.native_classification_level == "FAMILY"
    assert family.gathering_sequence_score == 10.5
    assert family.gathering_domain_score == 9.25
    assert family.model_length == 4
    assert release.direct_parents == {
        "SFLDG00001": "SFLDS00001",
        "SFLDF00001": "SFLDG00001",
    }
    assert release.ancestors["SFLDF00001"] == ("SFLDG00001", "SFLDS00001")

    rule = release.site_rules["SFLDF00001"]
    assert [site.model_position for site in rule.sites] == [1, 4]
    assert rule.sites[1].description is None
    assert rule.feature_patterns == ("DE", "DQ")
    # A feature is a correlated tuple, not independent per-position alphabets.
    assert "QQ" not in rule.feature_patterns


def test_profile_projection_preserves_exact_model_and_correlated_site_contract(tmp_path):
    release = _load(tmp_path)

    representation = build_sfld_profile_representation(release, "SFLDF00001")

    assert representation == {
        "source_accession": "SFLD:SFLDF00001",
        "source_release": "4",
        "representation_type": "SFLD_4_HMMER3_PROFILE_WITH_CORRELATED_SITES",
        "source_model_artifact": "data/raw/interpro_members/sfld.hmm",
        "source_model_artifact_sha256": _sha(HMM),
        "source_model_record_sha256": release.models["SFLDF00001"].source_record_sha256,
        "source_sites_artifact": "data/raw/interpro_members/sfld_sites.annot",
        "source_sites_artifact_sha256": _sha(SITES),
        "source_site_record_sha256": release.site_rules["SFLDF00001"].source_record_sha256,
        "source_hierarchy_artifact": ("data/raw/interpro_members/sfld_hierarchy_flat.txt"),
        "source_hierarchy_artifact_sha256": _sha(HIERARCHY),
        "native_classification_level": "FAMILY",
        "model_length": 4,
        "gathering_sequence_score": 10.5,
        "gathering_domain_score": 9.25,
        "training_sequence_count": 3,
        "hmm_checksum": 3,
        "profile_search_mode": "HMMSEARCH_CUT_GA",
        "site_coordinate_system": "HMM_MODEL_MATCH_STATE",
        "site_evidence_scope": "DIRECT_MODEL_MATCH_ONLY",
        "site_count": 2,
        "sites": [
            {"ordinal": 1, "model_position": 1, "description": "nucleophile"},
            {"ordinal": 2, "model_position": 4},
        ],
        "site_feature_pattern_count": 2,
        "site_feature_patterns": ["DE", "DQ"],
    }


def test_profile_projection_refuses_accession_without_executable_model(tmp_path):
    release = _load(tmp_path)

    with pytest.raises(SfldReleaseError, match="no executable model SFLDF99999"):
        build_sfld_profile_representation(release, "SFLDF99999")


def test_profile_projection_is_accepted_by_the_strict_record_validator(tmp_path):
    release = _load(tmp_path)
    record_path = tmp_path / "projected-record.yaml"
    record_path.write_text(
        yaml.safe_dump(
            {
                "identifier": "SFLD:SFLDF00001",
                "label": "test SFLD family",
                "trait_axis": "FUNCTION",
                "sequence_profile_representations": [
                    build_sfld_profile_representation(release, "SFLDF00001")
                ],
            },
            sort_keys=False,
        )
    )

    # The fixture uses synthetic artifact digests rather than production pins;
    # patch the representation's source-wide digest values to the production
    # constants enforced by validate_strict while retaining record-level hashes.
    text = record_path.read_text()
    text = text.replace(_sha(HMM), sfld.SFLD_4_HMM_SHA256)
    text = text.replace(_sha(SITES), sfld.SFLD_4_SITES_SHA256)
    text = text.replace(_sha(HIERARCHY), sfld.SFLD_4_HIERARCHY_SHA256)
    record_path.write_text(text)

    assert validate_one(record_path) == []


def test_manifest_is_deterministic_and_declares_non_inherited_sites(tmp_path):
    release = _load(tmp_path)
    first = build_sfld_release_manifest(release)
    second = build_sfld_release_manifest(release)

    assert first == second
    assert len(first["manifest_sha256"]) == 64
    assert first["matching_contract"] == {
        "profile_search_mode": "HMMSEARCH_CUT_GA",
        "site_coordinate_system": "HMM_MODEL_MATCH_STATE",
        "site_evidence_scope": "DIRECT_MODEL_MATCH_ONLY",
        "feature_patterns_are_correlated_tuples": True,
        "ancestor_propagation_clears_sites": True,
    }
    assert first["counts"]["model_count_by_native_level"] == {
        "SUPERFAMILY": 1,
        "SUBGROUP": 1,
        "FAMILY": 1,
    }


def test_missing_and_checksum_mismatched_artifacts_fail_closed(tmp_path):
    missing = tmp_path / "missing.hmm"
    hierarchy_path = tmp_path / "hierarchy.txt"
    sites_path = tmp_path / "sites.annot"
    hierarchy_path.write_bytes(HIERARCHY)
    sites_path.write_bytes(SITES)
    with pytest.raises(SfldReleaseError, match="missing pinned SFLD HMM"):
        load_sfld_release(
            missing,
            hierarchy_path,
            sites_path,
            expected_hmm_sha256="0" * 64,
            expected_hierarchy_sha256=_sha(HIERARCHY),
            expected_sites_sha256=_sha(SITES),
            enforce_release_contract=False,
        )

    hmm_path = tmp_path / "sfld.hmm"
    hmm_path.write_bytes(HMM)
    with pytest.raises(SfldChecksumError, match="HMM checksum mismatch"):
        load_sfld_release(
            hmm_path,
            hierarchy_path,
            sites_path,
            expected_hmm_sha256="0" * 64,
            expected_hierarchy_sha256=_sha(HIERARCHY),
            expected_sites_sha256=_sha(SITES),
            enforce_release_contract=False,
        )


@pytest.mark.parametrize(
    ("broken", "message"),
    [
        (HMM.removesuffix(b"//\n"), "lacks // terminator"),
        (
            HMM.replace(
                b"      3 " + b"1.0 " * 20 + b"3 a x - -\n",
                b"",
                1,
            ),
            "matrix is truncated before match state 3",
        ),
        (HMM.replace(b"GA    10.50 9.25", b"GA    nan 9.25", 1), "non-finite GA"),
    ],
)
def test_malformed_hmm_records_fail_closed(tmp_path, broken, message):
    with pytest.raises(SfldReleaseError, match=message):
        _load(tmp_path, hmm=broken)


@pytest.mark.parametrize(
    ("broken", "message"),
    [
        (SITES.replace(b"FEATURE DE\n", b"FEATURE D\n"), "tuple length"),
        (
            SITES.replace(b"SITE 1 nucleophile\nSITE 4 ", b"SITE 5 nucleophile\nSITE 6 "),
            "exceeds HMM",
        ),
        (
            SITES.replace(b"SITE 1 nucleophile\nSITE 4 ", b"SITE 4 nucleophile\nSITE 1 "),
            "not strictly ordered",
        ),
        (SITES.replace(b"ACC SFLDS00001 0 0\n", b""), "must equal HMM accessions"),
    ],
)
def test_malformed_or_incomplete_site_rules_fail_closed(tmp_path, broken, message):
    with pytest.raises(SfldReleaseError, match=message):
        _load(tmp_path, sites=broken)


@pytest.mark.parametrize(
    ("broken", "message"),
    [
        (
            b"SFLDG00001: SFLDS00001\nSFLDF00001: SFLDG00001\n",
            "transitive closure",
        ),
        (
            b"SFLDG00001: SFLDS99999\nSFLDF00001: SFLDG00001 SFLDS99999\n",
            "absent from sfld.hmm",
        ),
        (
            b"SFLDF00001: SFLDS00001 SFLDG00001\n",
            "cannot derive one direct parent",
        ),
    ],
)
def test_hierarchy_must_be_complete_unambiguous_closure(tmp_path, broken, message):
    with pytest.raises(SfldReleaseError, match=message):
        _load(tmp_path, hierarchy=broken)


def _patch_cli_contract(monkeypatch, tmp_path: pathlib.Path):
    release = _load(tmp_path)
    monkeypatch.setattr(sfld, "SFLD_4_HMM_SHA256", _sha(HMM))
    monkeypatch.setattr(sfld, "SFLD_4_HIERARCHY_SHA256", _sha(HIERARCHY))
    monkeypatch.setattr(sfld, "SFLD_4_SITES_SHA256", _sha(SITES))
    monkeypatch.setattr(sfld, "_SFLD_4_EXPECTED_COUNTS", sfld._release_counts(release))
    return release


def _cli_args(tmp_path: pathlib.Path) -> list[str]:
    return [
        "--hmm",
        str(tmp_path / "sfld.hmm"),
        "--hierarchy",
        str(tmp_path / "sfld_hierarchy_flat.txt"),
        "--sites",
        str(tmp_path / "sfld_sites.annot"),
    ]


def test_cli_dry_run_prints_full_manifest_without_writing(monkeypatch, tmp_path, capsys):
    _patch_cli_contract(monkeypatch, tmp_path)
    raw_dir = tmp_path / "data" / "raw" / "interpro_members"
    raw_dir.mkdir(parents=True)
    monkeypatch.setattr(sfld, "_REPO_ROOT", tmp_path)

    before = sorted(path.relative_to(tmp_path) for path in tmp_path.rglob("*"))
    assert sfld.main(_cli_args(tmp_path)) == 0
    after = sorted(path.relative_to(tmp_path) for path in tmp_path.rglob("*"))

    assert after == before
    output = json.loads(capsys.readouterr().out)
    assert output["manifest_kind"] == "SFLD_SOURCE_MODEL"
    assert output["counts"]["model_count"] == 3
    assert not (raw_dir / "sfld_release_manifest.json").exists()


def test_cli_tampering_fails_before_any_manifest_write(monkeypatch, tmp_path, capsys):
    _patch_cli_contract(monkeypatch, tmp_path)
    raw_dir = tmp_path / "data" / "raw" / "interpro_members"
    raw_dir.mkdir(parents=True)
    monkeypatch.setattr(sfld, "_REPO_ROOT", tmp_path)
    (tmp_path / "sfld.hmm").write_bytes(HMM + b"tampered\n")

    assert sfld.main([*_cli_args(tmp_path), "--apply"]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "HMM checksum mismatch" in captured.err
    assert not (raw_dir / "sfld_release_manifest.json").exists()


def test_cli_apply_atomically_installs_canonical_manifest(monkeypatch, tmp_path, capsys):
    _patch_cli_contract(monkeypatch, tmp_path)
    raw_dir = tmp_path / "data" / "raw" / "interpro_members"
    raw_dir.mkdir(parents=True)
    monkeypatch.setattr(sfld, "_REPO_ROOT", tmp_path)

    assert sfld.main([*_cli_args(tmp_path), "--apply"]) == 0
    captured = capsys.readouterr()
    manifest = json.loads(captured.out)
    manifest_path = raw_dir / "sfld_release_manifest.json"
    assert manifest_path.read_bytes() == (sfld.canonical_json(manifest) + "\n").encode("ascii")
    assert f"wrote: {manifest_path}" in captured.err
    assert not list(raw_dir.glob(".sfld_release_manifest.json.*.tmp"))
