"""Strict source-model tests for the PRINTS 42.0 KDAT parser."""

from __future__ import annotations

import copy
import dataclasses
import hashlib
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from prints_kdat import (  # noqa: E402
    PRINTS_42_0_SHA256,
    PRINTS_CANONICAL_STATUS,
    PRINTS_NONCANONICAL_STATUS,
    PrintsChecksumError,
    PrintsKdatError,
    PrintsRelease,
    build_fingerprint_representation,
    parse_prints_kdat,
)

MOTIF_1 = (
    b"fc; TEST MOTIF 1\n"
    b"fl; 4\n"
    b"ft; test motif I\n"
    b"fd; ACDE PROT_A 1 1 **/R2**\n"
    b"fd; ACDF PROT_B 3 3\n"
    b"KD; INTER_MOTIF_DISTANCE REGION=0-1; MIN=1; MAX=3\n"
)
MOTIF_2 = b"fc; TESTMOTIF2\nfl; 3\nft; test motif II\nfd; GHI PROT_A 7 2\nfd; GHJ PROT_B 5 -2\n"
KDAT = (
    b"gc; TESTPRINT\n"
    b"gx; PR00001; PR09999\n"
    b"gn; COMPOUND(2)\n"
    b"gt; Test fingerprint\n"
    b"gd; Source description at 1.8\xc5 resolution.\n"
    b"fm; FINAL MOTIF-SETS\n"
    b"fm; ----------------\n"
    b"bb;\n" + MOTIF_1 + b"bb;\n" + MOTIF_2 + b"bb;\n"
)


def _parse_bytes(tmp_path: pathlib.Path, content: bytes = KDAT):
    path = tmp_path / "prints.kdat"
    path.write_bytes(content)
    checksum = hashlib.sha256(content).hexdigest()
    return parse_prints_kdat(path, checksum)


def test_parser_preserves_source_order_repeat_rows_distances_and_raw_hashes(tmp_path):
    release = _parse_bytes(tmp_path)
    fingerprint = release.fingerprints["PR00001"]

    assert fingerprint.alternate_accessions == ("PR09999",)
    assert fingerprint.description == "Source description at 1.8Å resolution."
    assert fingerprint.source_record_sha256 == hashlib.sha256(KDAT).hexdigest()
    assert [motif.ordinal for motif in fingerprint.motifs] == [1, 2]
    assert [motif.code for motif in fingerprint.motifs] == ["TEST MOTIF 1", "TESTMOTIF2"]
    assert [motif.length for motif in fingerprint.motifs] == [4, 3]

    first, second = fingerprint.motifs
    assert first.source_motif_sha256 == hashlib.sha256(MOTIF_1).hexdigest()
    assert first.instances[0].repeat_number == 2
    assert first.instances[0].position == 1
    assert (
        first.training_distance_from_previous_min,
        first.training_distance_from_previous_max,
    ) == (1, 3)
    assert first.inter_motif_distance_constraint is not None
    assert first.inter_motif_distance_constraint.region_start_ordinal == 0
    assert first.inter_motif_distance_constraint.region_end_ordinal == 1
    assert first.inter_motif_distance_constraint.minimum == 1
    assert first.inter_motif_distance_constraint.maximum == 3
    assert first.inter_motif_distance_constraint.repeat_qualified is False
    assert second.source_motif_sha256 == hashlib.sha256(MOTIF_2).hexdigest()
    assert (
        second.training_distance_from_previous_min,
        second.training_distance_from_previous_max,
    ) == (-2, 2)
    assert second.inter_motif_distance_constraint is None
    assert release.source_artifact_sha256 == hashlib.sha256(KDAT).hexdigest()


def test_generic_fixture_is_immutable_and_cannot_claim_canonical_provenance(tmp_path):
    release = _parse_bytes(tmp_path)
    fingerprint = release.fingerprints["PR00001"]
    assert release.canonical_status == PRINTS_NONCANONICAL_STATUS
    assert release.source_artifact_size == len(KDAT)
    with pytest.raises(TypeError):
        release.fingerprints["PR00002"] = fingerprint  # type: ignore[index]
    with pytest.raises(PrintsKdatError, match="requires the canonical"):
        build_fingerprint_representation(release, fingerprint)

    # A public wrapper cannot reparent parser output under an official digest.
    different = PrintsRelease(
        release=release.release,
        source_path=release.source_path,
        source_artifact_sha256=PRINTS_42_0_SHA256,
        fingerprints={fingerprint.accession: fingerprint},
        source_artifact_size=release.source_artifact_size,
        canonical_status=PRINTS_CANONICAL_STATUS,
    )
    with pytest.raises(PrintsKdatError, match="not created by the checksum-verifying parser"):
        build_fingerprint_representation(different, fingerprint)

    # dataclasses.replace copies the private seal, so every bound field and the
    # exact immutable mapping identity are checked as well.
    reparented = dataclasses.replace(
        release,
        source_artifact_sha256=PRINTS_42_0_SHA256,
        canonical_status=PRINTS_CANONICAL_STATUS,
    )
    with pytest.raises(PrintsKdatError, match="reparented"):
        build_fingerprint_representation(reparented, fingerprint)


def test_parser_hashes_and_parses_one_immutable_capture(tmp_path, monkeypatch):
    import prints_kdat

    path = tmp_path / "prints.kdat"
    path.write_bytes(KDAT)
    expected = hashlib.sha256(KDAT).hexdigest()
    original_read = prints_kdat._read_source_bytes

    def read_then_swap(source_path):
        captured = original_read(source_path)
        source_path.write_bytes(KDAT.replace(b"PR00001", b"PR00002"))
        return captured

    monkeypatch.setattr(prints_kdat, "_read_source_bytes", read_then_swap)
    release = parse_prints_kdat(path, expected)

    assert release.source_artifact_sha256 == expected
    assert release.source_artifact_size == len(KDAT)
    assert set(release.fingerprints) == {"PR00001"}
    assert b"PR00002" in path.read_bytes()


def test_a_missing_kd_constraint_is_allowed(tmp_path):
    release = _parse_bytes(tmp_path, KDAT.replace(MOTIF_1, MOTIF_1.split(b"KD;", 1)[0]))
    assert release.fingerprints["PR00001"].motifs[0].inter_motif_distance_constraint is None


def test_repeat_qualified_kd_is_preserved_without_changing_training_extrema(tmp_path):
    release = _parse_bytes(
        tmp_path,
        KDAT.replace(b"REGION=0-1; MIN=1; MAX=3\n", b"REGION=0-1; MIN=1; MAX=3  /R\n"),
    )
    motif = release.fingerprints["PR00001"].motifs[0]
    assert motif.inter_motif_distance_constraint is not None
    assert motif.inter_motif_distance_constraint.repeat_qualified is True
    assert (
        motif.training_distance_from_previous_min,
        motif.training_distance_from_previous_max,
    ) == (1, 3)


def test_missing_and_checksum_mismatched_sources_fail_closed(tmp_path):
    missing = tmp_path / "missing.kdat"
    with pytest.raises(PrintsKdatError, match="missing pinned PRINTS source"):
        parse_prints_kdat(missing, "0" * 64)

    path = tmp_path / "prints.kdat"
    path.write_bytes(KDAT)
    with pytest.raises(PrintsChecksumError, match="checksum mismatch"):
        parse_prints_kdat(path, "0" * 64)


@pytest.mark.parametrize(
    ("broken", "message"),
    [
        (KDAT.replace(b"COMPOUND(2)", b"COMPOUND(3)"), "declares 3 motifs"),
        (KDAT.replace(b"fd; ACDE", b"fd; ACD"), "peptide length 3 != fl 4"),
        (
            KDAT.replace(
                b"fl; 4\nft; test motif I\nfd; ACDE", b"fd; ACDE\nfl; 4\nft; test motif I"
            ),
            "out-of-order fd",
        ),
        (KDAT.replace(b"**/R2**", b"**/R0**"), "invalid repeat marker"),
    ],
)
def test_count_length_order_and_repeat_marker_corruption_is_rejected(tmp_path, broken, message):
    with pytest.raises(PrintsKdatError, match=message):
        _parse_bytes(tmp_path, broken)


@pytest.mark.parametrize(
    ("broken", "message"),
    [
        (
            KDAT.replace(b"REGION=0-1; MIN=1; MAX=3", b"REGION=1-2; MIN=1; MAX=3"),
            "KD REGION 1-2.*must be 0-1",
        ),
        (
            KDAT.replace(b"REGION=0-1; MIN=1; MAX=3", b"REGION=0-1; MIN=4; MAX=3"),
            "KD MIN 4 exceeds MAX 3",
        ),
        (
            KDAT.replace(
                b"KD; INTER_MOTIF_DISTANCE REGION=0-1; MIN=1; MAX=3\n",
                b"KD; INTER_MOTIF_DISTANCE REGION=0-1; MIN=1; MAX=3\n"
                b"KD; INTER_MOTIF_DISTANCE REGION=0-1; MIN=1; MAX=3\n",
            ),
            "out-of-order or duplicate KD",
        ),
        (
            KDAT.replace(b"REGION=0-1; MIN=1; MAX=3", b"REGION=0-1; MIN=1; MAX=3 /X"),
            "malformed KD row",
        ),
    ],
)
def test_kd_grammar_cardinality_region_and_range_are_strict(tmp_path, broken, message):
    with pytest.raises(PrintsKdatError, match=message):
        _parse_bytes(tmp_path, broken)


def test_schema_has_a_dedicated_fingerprint_shape_not_an_overloaded_sequence_pattern():
    schema = yaml.safe_load(
        (REPO / "src/proteintraitsmech/schema/proteintraitsmech.yaml").read_text(encoding="utf-8")
    )
    record_attributes = schema["classes"]["ProteinTraitRecord"]["attributes"]
    fingerprint_slot = record_attributes["sequence_fingerprint_representations"]
    assert fingerprint_slot["range"] == "SequenceFingerprintRepresentation"
    assert fingerprint_slot["multivalued"] is True
    assert record_attributes["sequence_pattern"]["range"] == "string"

    representation = schema["classes"]["SequenceFingerprintRepresentation"]["attributes"]
    assert representation["motifs"]["range"] == "SequenceFingerprintMotif"
    assert representation["source_record_sha256"]["pattern"] == "^[0-9a-f]{64}$"
    motif = schema["classes"]["SequenceFingerprintMotif"]["attributes"]
    assert "training_distance_from_previous_min" in motif
    assert "training_distance_from_previous_max" in motif
    assert motif["training_distance_from_previous_min"]["required"] is True
    assert motif["training_distance_from_previous_max"]["required"] is True
    assert "distance_from_previous_min" not in motif
    assert "distance_from_previous_max" not in motif
    assert (
        motif["inter_motif_distance_constraint"]["range"]
        == "SequenceFingerprintInterMotifDistanceConstraint"
    )
    assert set(
        schema["enums"]["SequenceFingerprintRepresentationTypeEnum"]["permissible_values"]
    ) == {"PRINTS_FINAL_ORDERED_MOTIF_SETS"}


REAL_KDAT = REPO / "data/raw/interpro_members/prints42_0.kdat"


@pytest.mark.skipif(
    not REAL_KDAT.is_file(),
    reason="ignored pinned PRINTS 42.0 source is not present in data/raw/interpro_members",
)
def test_real_prints_42_source_invariants():
    release = parse_prints_kdat(REAL_KDAT, PRINTS_42_0_SHA256)
    assert release.canonical_status == PRINTS_CANONICAL_STATUS
    assert release.source_artifact_size == REAL_KDAT.stat().st_size
    assert len(release.fingerprints) == 2_106
    assert sum(len(item.motifs) for item in release.fingerprints.values()) == 12_444
    # The file has 456,785 `fd` tags, but one is a mistagged row in PR02011's
    # initial `ic` block. Exactly 456,784 belong to FINAL MOTIF-SETS.
    assert (
        sum(len(motif.instances) for item in release.fingerprints.values() for motif in item.motifs)
        == 456_784
    )
    assert sum(len(item.alternate_accessions) for item in release.fingerprints.values()) == 3
    ordinary_fingerprint = release.fingerprints["PR00439"]
    ordinary = ordinary_fingerprint.motifs[0]
    representation = build_fingerprint_representation(release, ordinary_fingerprint)
    assert representation["source_accession"] == "PRINTS:PR00439"
    assert representation["source_release"] == "42.0"
    assert representation["source_artifact_sha256"] == PRINTS_42_0_SHA256
    assert representation["source_record_sha256"] == ordinary_fingerprint.source_record_sha256
    assert representation["compatible_derivation_tool_hint"] == "EMBOSS_PRINTSEXTRACT"
    assert representation["motif_count"] == len(representation["motifs"])
    equal_clone = copy.deepcopy(ordinary_fingerprint)
    assert equal_clone == ordinary_fingerprint
    assert equal_clone is not ordinary_fingerprint
    with pytest.raises(PrintsKdatError, match="not owned by the supplied"):
        build_fingerprint_representation(release, equal_clone)
    assert ordinary.inter_motif_distance_constraint is not None
    assert ordinary.inter_motif_distance_constraint.minimum == 4
    assert ordinary.inter_motif_distance_constraint.maximum == 618
    assert ordinary.inter_motif_distance_constraint.repeat_qualified is False

    repeat_qualified = release.fingerprints["PR00308"].motifs
    assert (
        repeat_qualified[0].training_distance_from_previous_min,
        repeat_qualified[0].training_distance_from_previous_max,
    ) == (2, 51)
    assert repeat_qualified[0].inter_motif_distance_constraint is not None
    assert repeat_qualified[0].inter_motif_distance_constraint.minimum == 23
    assert repeat_qualified[0].inter_motif_distance_constraint.maximum == 45
    assert repeat_qualified[0].inter_motif_distance_constraint.repeat_qualified is True
    # /R qualifies the source constraint; it does not turn the all-fd extrema
    # into that constraint or imply runtime enforcement by this parser.
    assert repeat_qualified[2].training_distance_from_previous_max == 10
    assert repeat_qualified[2].inter_motif_distance_constraint is not None
    assert repeat_qualified[2].inter_motif_distance_constraint.maximum == -1
    assert repeat_qualified[2].inter_motif_distance_constraint.repeat_qualified is True

    missing_kd = release.fingerprints["PR01474"].motifs
    assert len(missing_kd) == 6
    assert all(motif.inter_motif_distance_constraint is None for motif in missing_kd)
