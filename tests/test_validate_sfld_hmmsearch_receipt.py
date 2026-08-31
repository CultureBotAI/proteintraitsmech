"""Safety and semantic tests for the read-only SFLD execution-receipt boundary."""

from __future__ import annotations

import hashlib
import json
import os
import pathlib
import sys
from dataclasses import replace
from typing import Any

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import validate_sfld_hmmsearch_receipt as receipt  # noqa: E402


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

VERSION = (
    "# hmmsearch :: search profile(s) against a sequence database\n"
    "# HMMER 3.4 (Aug 2023); http://hmmer.org/\n"
    "# Copyright (C) 2023 Howard Hughes Medical Institute.\n"
    "Usage: hmmsearch [options] <hmmfile> <seqdb>\n"
    "  --cut_ga  : use profile GA gathering cutoffs\n"
    "  --cpu <n>  : number of parallel CPU workers\n"
    "  --seed <n> : set RNG seed\n"
    "  --tformat <s> : assert target sequence format\n"
)
ALIGNMENT = (
    "# STOCKHOLM 1.0\n"
    "#=GF AC SFLDF00001\n"
    "#=GF ID Model_SFLDF00001\n"
    "UniProtKB:P12345/1-6 Dac-\n"
    "#=GR UniProtKB:P12345/1-6 PP 999.\n"
    "#=GC RF R..x\n"
    "\n"
    "UniProtKB:P12345/1-6 DEg\n"
    "#=GC RF xx.\n"
    "//\n"
)
DOMTBL_ROW = (
    "UniProtKB:P12345 - 6 Model_SFLDF00001 SFLDF00001 4 "
    "1e-10 10.5 0.0 1 1 1e-10 1e-10 9.3 0.0 1 4 1 6 1 6 0.99 -"
)
DOMTBLOUT = (
    "# target name accession tlen query name accession qlen full-Evalue score bias\n"
    "# Program:         hmmsearch\n"
    "# Version:         3.4 (Aug 2023)\n"
    f"{DOMTBL_ROW}\n"
)


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _registry_row(*, sequence: str = "DACDEG") -> dict[str, Any]:
    return {
        "protein_id": "UniProtKB:P12345",
        "protein_label": "Synthetic receipt target",
        "reviewed": True,
        "sequence": sequence,
        "sequence_length": len(sequence),
        "sequence_sha256": _sha(sequence.encode("ascii")),
        "sequence_version": 1,
        "taxon_id": "NCBITaxon:9606",
        "taxon_label": "Homo sapiens",
        "uniprot_release": "2026_02",
    }


def _main_output(tmp_path: pathlib.Path) -> str:
    return (
        VERSION
        + f"# query HMM file:                  {(tmp_path / 'sfld.hmm').absolute()}\n"
        + f"# target sequence database:        {(tmp_path / 'targets.fasta').absolute()}\n"
        + f"# MSA of all hits saved to file:   {(tmp_path / 'alignment.sto').absolute()}\n"
        + f"# per-dom hits tabular output:     {(tmp_path / 'domains.domtblout').absolute()}\n"
        + "# model-specific thresholding:     GA cutoffs\n"
        + "# random number seed set to:       42\n"
        + "# targ <seqfile> format asserted:  fasta\n"
        + "# number of worker threads:        0\n"
        + "Query: Model_SFLDF00001 [M=4]\n//\n"
    )


def _write(path: pathlib.Path, raw: bytes) -> pathlib.Path:
    path.write_bytes(raw)
    return path


def _make_bundle(tmp_path: pathlib.Path) -> tuple[receipt.ReceiptPaths, dict[str, str]]:
    row = _registry_row()
    registry_raw = (receipt.canonical_json(row) + "\n").encode("ascii")
    fasta_raw = receipt.canonical_registry_fasta([row])
    executable = _write(tmp_path / "hmmsearch", b"#!/bin/sh\nexit 0\n")
    executable.chmod(0o755)
    paths = receipt.ReceiptPaths(
        receipt=tmp_path / "receipt.json",
        executable=executable,
        version_stdout=_write(tmp_path / "version.stdout", VERSION.encode("ascii")),
        version_stderr=_write(tmp_path / "version.stderr", b""),
        hmm=_write(tmp_path / "sfld.hmm", HMM),
        hierarchy=_write(tmp_path / "sfld_hierarchy_flat.txt", HIERARCHY),
        sites=_write(tmp_path / "sfld_sites.annot", SITES),
        registry=_write(tmp_path / "protein_registry.jsonl", registry_raw),
        fasta=_write(tmp_path / "targets.fasta", fasta_raw),
        main_output=_write(tmp_path / "hmmsearch.stdout", _main_output(tmp_path).encode("ascii")),
        stderr_output=_write(tmp_path / "hmmsearch.stderr", b""),
        alignment_output=_write(tmp_path / "alignment.sto", ALIGNMENT.encode("ascii")),
        domtblout=_write(tmp_path / "domains.domtblout", DOMTBLOUT.encode("ascii")),
    )
    expected_hashes = {
        "expected_hmm_sha256": _sha(HMM),
        "expected_hierarchy_sha256": _sha(HIERARCHY),
        "expected_sites_sha256": _sha(SITES),
    }
    return paths, expected_hashes


def _build_and_install(
    paths: receipt.ReceiptPaths,
    expected_hashes: dict[str, str],
    *,
    timestamp: str = "2026-08-25T12:34:56Z",
) -> dict[str, Any]:
    value = receipt.build_receipt_value(
        paths=paths,
        selected_domtblout_line_number=4,
        captured_at_utc=timestamp,
        producer={
            "implementation": "tests.synthetic-controlled-runner",
            "implementation_sha256": "a" * 64,
        },
        enforce_release_contract=False,
        **expected_hashes,
    )
    paths.receipt.write_text(receipt.canonical_json(value) + "\n", encoding="ascii")
    return value


def _verify(
    paths: receipt.ReceiptPaths,
    expected_hashes: dict[str, str],
) -> dict[str, Any]:
    return receipt.verify_receipt(
        paths=paths,
        enforce_release_contract=False,
        **expected_hashes,
    )


def test_complete_receipt_replays_profile_site_and_full_registry_bindings(tmp_path):
    paths, expected_hashes = _make_bundle(tmp_path)
    value = _build_and_install(paths, expected_hashes)

    verification = _verify(paths, expected_hashes)

    assert value["receipt_id"].startswith(receipt.RECEIPT_ID_PREFIX)
    assert value["execution"]["argv"] == [
        str(paths.executable.absolute()),
        "--cut_ga",
        "--cpu",
        "0",
        "--seed",
        "42",
        "--tformat",
        "fasta",
        "-A",
        str(paths.alignment_output.absolute()),
        "--domtblout",
        str(paths.domtblout.absolute()),
        str(paths.hmm.absolute()),
        str(paths.fasta.absolute()),
    ]
    assert value["execution"]["working_directory"] == str(tmp_path.absolute())
    assert value["artifacts"]["executable"]["mode_bits"] == 0o755
    assert value["target_registry_binding"] == {
        "canonical_fasta_sha256": _sha(receipt.canonical_registry_fasta([_registry_row()])),
        "protein_count": 1,
        "registry_artifact_sha256": _sha(paths.registry.read_bytes()),
        "registry_rows_sha256": _sha(paths.registry.read_bytes()),
        "target_sequence_projection_sha256": value["target_registry_binding"][
            "target_sequence_projection_sha256"
        ],
        "uniprot_release": "2026_02",
    }
    selected = value["selected_domain"]
    assert selected["domtblout_raw_line"] == DOMTBL_ROW
    assert selected["model_accession"] == "SFLDF00001"
    assert selected["target_sequence_identifier"] == "UniProtKB:P12345"
    assert selected["target_sequence_registry_binding_verified"] is True
    assert selected["profile_threshold_evaluation"] == {
        "cut_ga_command_selected_row": True,
        "displayed_scores_are_rounding_consistent": True,
        "gathering_domain_score_bits": "9.25",
        "gathering_sequence_score_bits": "10.5",
        "observed_domain_score_bits": "9.3",
        "observed_full_sequence_score_bits": "10.5",
        "qualification_basis": (
            "ROW_EMITTED_BY_ATTESTED_HMMSEARCH_CUT_GA_AND_DISPLAYED_SCORES_"
            "NOT_BELOW_HALF_UNIT_ROUNDING_BOUNDS"
        ),
    }
    direct = selected["site_evaluation"]["direct_model_evaluation"]
    assert direct["correlated_site_tuple_matched"] is True
    assert direct["site_evidence"]["observed_residue_tuple"] == "DE"
    assert value["source_native_match_status"] == "PROFILE_AND_CORRELATED_SITE_MATCH"
    assert value["grounding_boundary"]["grounding_eligible"] is False
    assert value["grounding_boundary"]["process_execution_replayed_by_verifier"] is False
    assert verification == {
        "artifact_kind": receipt.VERIFICATION_KIND,
        "artifact_and_semantic_bindings_verified": True,
        "grounding_eligible": False,
        "process_execution_replayed": False,
        "provenance_limit": receipt.PROVENANCE_LIMIT,
        "receipt_id": value["receipt_id"],
        "schema_version": 1,
        "selected_model_accession": "SFLDF00001",
        "selected_target_sequence_identifier": "UniProtKB:P12345",
        "source_native_match_status": "PROFILE_AND_CORRELATED_SITE_MATCH",
        "status": "PASS_EXECUTION_RECEIPT_CONTENT_AND_SEMANTIC_BINDINGS_ONLY",
        "writes_performed": False,
    }


@pytest.mark.parametrize(
    "role",
    [
        "executable",
        "version_stdout",
        "hmm",
        "hierarchy",
        "sites",
        "registry",
        "fasta",
        "main_output",
        "alignment_output",
        "domtblout",
    ],
)
def test_any_material_artifact_change_breaks_the_installed_receipt(tmp_path, role):
    paths, expected_hashes = _make_bundle(tmp_path)
    _build_and_install(paths, expected_hashes)
    path = getattr(paths, role)
    path.write_bytes(path.read_bytes() + b"X")

    with pytest.raises((receipt.SfldHmmsearchReceiptError, ValueError)):
        _verify(paths, expected_hashes)


def test_executable_permission_mode_change_breaks_the_installed_receipt(tmp_path):
    paths, expected_hashes = _make_bundle(tmp_path)
    _build_and_install(paths, expected_hashes)
    paths.executable.chmod(0o700)

    with pytest.raises(receipt.SfldHmmsearchReceiptError, match="exactly reproduce"):
        _verify(paths, expected_hashes)


def test_builder_does_not_need_or_create_a_receipt_file(tmp_path):
    paths, expected_hashes = _make_bundle(tmp_path)
    assert not paths.receipt.exists()

    value = receipt.build_receipt_value(
        paths=paths,
        selected_domtblout_line_number=4,
        captured_at_utc="2026-08-25T12:34:56Z",
        producer={
            "implementation": "tests.synthetic-controlled-runner",
            "implementation_sha256": "a" * 64,
        },
        enforce_release_contract=False,
        **expected_hashes,
    )

    assert value["completion_status"] == "COMPLETE_RECEIPT_INSTALLED_AFTER_BOUND_OUTPUTS"
    assert not paths.receipt.exists()


def test_canonical_receipt_with_recomputed_id_cannot_override_exact_argv(tmp_path):
    paths, expected_hashes = _make_bundle(tmp_path)
    value = _build_and_install(paths, expected_hashes)
    value["execution"]["argv"][1] = "--cut_tc"
    value.pop("receipt_id")
    value["receipt_id"] = receipt.RECEIPT_ID_PREFIX + receipt.value_sha256(value)
    paths.receipt.write_text(receipt.canonical_json(value) + "\n", encoding="ascii")

    with pytest.raises(receipt.SfldHmmsearchReceiptError, match="independently derived"):
        _verify(paths, expected_hashes)


def test_duplicate_json_key_and_noncanonical_json_fail_closed(tmp_path):
    paths, expected_hashes = _make_bundle(tmp_path)
    value = _build_and_install(paths, expected_hashes)
    original = receipt.canonical_json(value)
    paths.receipt.write_text('{"schema_version":1,"schema_version":1}\n', encoding="ascii")
    with pytest.raises(receipt.SfldHmmsearchReceiptError, match="duplicate JSON key"):
        _verify(paths, expected_hashes)

    paths.receipt.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="ascii")
    assert paths.receipt.read_text(encoding="ascii").rstrip() != original
    with pytest.raises(receipt.SfldHmmsearchReceiptError, match="not one exact canonical"):
        _verify(paths, expected_hashes)


def test_registry_and_fasta_must_be_exact_canonical_full_projection(tmp_path):
    paths, expected_hashes = _make_bundle(tmp_path)
    row = _registry_row()
    paths.registry.write_text(json.dumps(row) + "\n", encoding="ascii")
    with pytest.raises(receipt.SfldHmmsearchReceiptError, match="not canonical JSON"):
        receipt.build_receipt_value(
            paths=paths,
            selected_domtblout_line_number=4,
            captured_at_utc="2026-08-25T12:34:56Z",
            producer={"implementation": "test", "implementation_sha256": "a" * 64},
            enforce_release_contract=False,
            **expected_hashes,
        )

    paths.registry.write_text(receipt.canonical_json(row) + "\n", encoding="ascii")
    paths.fasta.write_text(">UniProtKB:P12345 description\nDACDEG\n", encoding="ascii")
    with pytest.raises(receipt.SfldHmmsearchReceiptError, match="canonical projection"):
        receipt.build_receipt_value(
            paths=paths,
            selected_domtblout_line_number=4,
            captured_at_utc="2026-08-25T12:34:56Z",
            producer={"implementation": "test", "implementation_sha256": "a" * 64},
            enforce_release_contract=False,
            **expected_hashes,
        )


def test_scores_visibly_below_ga_fail_even_when_receipt_producer_selects_row(tmp_path):
    paths, expected_hashes = _make_bundle(tmp_path)
    paths.domtblout.write_text(DOMTBLOUT.replace(" 10.5 0.0", " 10.4 0.0"), encoding="ascii")

    with pytest.raises(receipt.SfldHmmsearchReceiptError, match="full-sequence score"):
        receipt.build_receipt_value(
            paths=paths,
            selected_domtblout_line_number=4,
            captured_at_utc="2026-08-25T12:34:56Z",
            producer={"implementation": "test", "implementation_sha256": "a" * 64},
            enforce_release_contract=False,
            **expected_hashes,
        )


def test_alignment_must_equal_exact_registry_coordinate_substring(tmp_path):
    paths, expected_hashes = _make_bundle(tmp_path)
    paths.alignment_output.write_text(ALIGNMENT.replace("DEg", "DFg"), encoding="ascii")

    with pytest.raises(receipt.SfldHmmsearchReceiptError, match="registry.*substring"):
        receipt.build_receipt_value(
            paths=paths,
            selected_domtblout_line_number=4,
            captured_at_utc="2026-08-25T12:34:56Z",
            producer={"implementation": "test", "implementation_sha256": "a" * 64},
            enforce_release_contract=False,
            **expected_hashes,
        )


def test_profile_pass_with_correlated_site_mismatch_is_valid_but_not_a_match(tmp_path):
    paths, expected_hashes = _make_bundle(tmp_path)
    row = _registry_row(sequence="DACDFG")
    paths.registry.write_text(receipt.canonical_json(row) + "\n", encoding="ascii")
    paths.fasta.write_bytes(receipt.canonical_registry_fasta([row]))
    paths.alignment_output.write_text(ALIGNMENT.replace("DEg", "DFg"), encoding="ascii")
    value = _build_and_install(paths, expected_hashes)

    assert value["source_native_match_status"] == "PROFILE_MATCH_CORRELATED_SITE_MISMATCH"
    assert (
        value["selected_domain"]["site_evaluation"]["direct_model_evaluation"][
            "correlated_site_tuple_matched"
        ]
        is False
    )
    assert _verify(paths, expected_hashes)["grounding_eligible"] is False


def test_invalid_selected_line_version_and_timestamp_fail_closed(tmp_path):
    paths, expected_hashes = _make_bundle(tmp_path)
    common = {
        "paths": paths,
        "producer": {"implementation": "test", "implementation_sha256": "a" * 64},
        "enforce_release_contract": False,
        **expected_hashes,
    }
    with pytest.raises(receipt.SfldHmmsearchReceiptError, match="not a domain row"):
        receipt.build_receipt_value(
            selected_domtblout_line_number=3,
            captured_at_utc="2026-08-25T12:34:56Z",
            **common,
        )
    with pytest.raises(receipt.SfldHmmsearchReceiptError, match="UTC-second"):
        receipt.build_receipt_value(
            selected_domtblout_line_number=4,
            captured_at_utc="2026-08-25 12:34:56",
            **common,
        )
    with pytest.raises(receipt.SfldHmmsearchReceiptError, match="real UTC calendar"):
        receipt.build_receipt_value(
            selected_domtblout_line_number=4,
            captured_at_utc="2026-02-31T12:34:56Z",
            **common,
        )
    paths.main_output.write_text(
        paths.main_output.read_text(encoding="ascii").replace("HMMER 3.4", "HMMER 3.3.2"),
        encoding="ascii",
    )
    with pytest.raises(receipt.SfldHmmsearchReceiptError, match="different HMMER versions"):
        receipt.build_receipt_value(
            selected_domtblout_line_number=4,
            captured_at_utc="2026-08-25T12:34:56Z",
            **common,
        )


def test_unsupported_but_self_consistent_hmmer_version_fails_closed(tmp_path):
    paths, expected_hashes = _make_bundle(tmp_path)
    for path in (paths.version_stdout, paths.main_output, paths.domtblout):
        path.write_text(
            path.read_text(encoding="ascii").replace("3.4", "3.3.2"),
            encoding="ascii",
        )

    with pytest.raises(receipt.SfldHmmsearchReceiptError, match="unsupported HMMER version"):
        receipt.build_receipt_value(
            paths=paths,
            selected_domtblout_line_number=4,
            captured_at_utc="2026-08-25T12:34:56Z",
            producer={"implementation": "test", "implementation_sha256": "a" * 64},
            enforce_release_contract=False,
            **expected_hashes,
        )


def test_incomplete_version_capability_capture_fails_closed(tmp_path):
    paths, expected_hashes = _make_bundle(tmp_path)
    paths.version_stdout.write_text(
        paths.version_stdout.read_text(encoding="ascii").replace(
            "  --cut_ga  : use profile GA gathering cutoffs\n",
            "",
        ),
        encoding="ascii",
    )

    with pytest.raises(receipt.SfldHmmsearchReceiptError, match="complete '-h' capability"):
        receipt.build_receipt_value(
            paths=paths,
            selected_domtblout_line_number=4,
            captured_at_utc="2026-08-25T12:34:56Z",
            producer={"implementation": "test", "implementation_sha256": "a" * 64},
            enforce_release_contract=False,
            **expected_hashes,
        )


def test_symlinked_artifact_and_hard_link_alias_fail_before_parsing(tmp_path):
    paths, expected_hashes = _make_bundle(tmp_path)
    real_fasta = paths.fasta
    linked_fasta = tmp_path / "linked.fasta"
    linked_fasta.symlink_to(real_fasta)
    symlink_paths = replace(paths, fasta=linked_fasta)
    with pytest.raises(receipt.SfldHmmsearchReceiptError, match="safely open regular file"):
        receipt.build_receipt_value(
            paths=symlink_paths,
            selected_domtblout_line_number=4,
            captured_at_utc="2026-08-25T12:34:56Z",
            producer={"implementation": "test", "implementation_sha256": "a" * 64},
            enforce_release_contract=False,
            **expected_hashes,
        )

    hard_link = tmp_path / "same-inode.stderr"
    os.link(paths.stderr_output, hard_link)
    hardlink_paths = replace(paths, version_stderr=hard_link)
    with pytest.raises(receipt.SfldHmmsearchReceiptError, match="hard-link aliases"):
        receipt.build_receipt_value(
            paths=hardlink_paths,
            selected_domtblout_line_number=4,
            captured_at_utc="2026-08-25T12:34:56Z",
            producer={"implementation": "test", "implementation_sha256": "a" * 64},
            enforce_release_contract=False,
            **expected_hashes,
        )


def test_cli_is_read_only_and_prints_one_canonical_verification(tmp_path, monkeypatch, capsys):
    paths, expected_hashes = _make_bundle(tmp_path)
    value = _build_and_install(paths, expected_hashes)
    monkeypatch.setattr(receipt, "SFLD_4_HMM_SHA256", expected_hashes["expected_hmm_sha256"])
    monkeypatch.setattr(
        receipt,
        "SFLD_4_HIERARCHY_SHA256",
        expected_hashes["expected_hierarchy_sha256"],
    )
    monkeypatch.setattr(receipt, "SFLD_4_SITES_SHA256", expected_hashes["expected_sites_sha256"])
    original_verify = receipt.verify_receipt

    def fixture_verify(*, paths):
        return original_verify(
            paths=paths,
            enforce_release_contract=False,
            **expected_hashes,
        )

    monkeypatch.setattr(receipt, "verify_receipt", fixture_verify)
    before = {path.name: path.read_bytes() for path in tmp_path.iterdir() if path.is_file()}
    argv = [
        "--receipt",
        str(paths.receipt),
        "--executable",
        str(paths.executable),
        "--version-stdout",
        str(paths.version_stdout),
        "--version-stderr",
        str(paths.version_stderr),
        "--hmm",
        str(paths.hmm),
        "--hierarchy",
        str(paths.hierarchy),
        "--sites",
        str(paths.sites),
        "--registry",
        str(paths.registry),
        "--fasta",
        str(paths.fasta),
        "--main-output",
        str(paths.main_output),
        "--stderr-output",
        str(paths.stderr_output),
        "--alignment-output",
        str(paths.alignment_output),
        "--domtblout",
        str(paths.domtblout),
    ]

    assert receipt.main(argv) == 0

    captured = capsys.readouterr()
    parsed = json.loads(captured.out)
    assert captured.out == receipt.canonical_json(parsed) + "\n"
    assert captured.err == ""
    assert parsed["receipt_id"] == value["receipt_id"]
    after = {path.name: path.read_bytes() for path in tmp_path.iterdir() if path.is_file()}
    assert after == before


def test_same_path_mutation_after_semantic_replay_fails_final_recheck(tmp_path, monkeypatch):
    paths, expected_hashes = _make_bundle(tmp_path)
    _build_and_install(paths, expected_hashes)
    original = receipt._build_expected_receipt  # noqa: SLF001

    def mutate_after_replay(**kwargs):
        result = original(**kwargs)
        paths.main_output.write_bytes(paths.main_output.read_bytes() + b"# raced\n")
        return result

    monkeypatch.setattr(receipt, "_build_expected_receipt", mutate_after_replay)
    with pytest.raises(receipt.SfldHmmsearchReceiptError, match="main_output changed"):
        _verify(paths, expected_hashes)


def test_current_protein_registry_has_stable_canonical_fasta_projection():
    registry_path = REPO / "data/grounding/protein_registry.jsonl"
    if not registry_path.is_file():
        pytest.skip("production ProteinReference registry is not installed")
    capture = receipt._capture_regular_file(  # noqa: SLF001
        registry_path,
        label="production registry",
        max_bytes=receipt._MAX_BYTES["registry"],  # noqa: SLF001
    )
    rows = receipt._load_registry(capture)  # noqa: SLF001
    fasta = receipt.canonical_registry_fasta(rows)

    assert len(rows) == 126
    assert capture.sha256 == "d587fad177207ca4f00d1dfb8649f4f9d2d21d01953d483f44a3a6e81acc729c"
    assert len(fasta) == 79906
    assert _sha(fasta) == "0aa2b6f9d1ce74ebc132184284475de53f55ccc62d0ecd7498d79d522ef18e9f"


def test_current_sfld_release_replays_exact_pinned_manifest_when_artifacts_exist():
    source_paths = {
        "hmm": receipt.DEFAULT_HMM,
        "hierarchy": receipt.DEFAULT_HIERARCHY,
        "sites": receipt.DEFAULT_SITES,
    }
    if not all(path.is_file() for path in source_paths.values()):
        pytest.skip("production SFLD source artifacts are not installed")
    captures = {
        role: receipt._capture_regular_file(  # noqa: SLF001
            path,
            label=f"production {role}",
            max_bytes=receipt._MAX_BYTES[role],  # noqa: SLF001
        )
        for role, path in source_paths.items()
    }
    release = receipt._load_release_from_captures(  # noqa: SLF001
        captures,
        expected_hmm_sha256=receipt.SFLD_4_HMM_SHA256,
        expected_hierarchy_sha256=receipt.SFLD_4_HIERARCHY_SHA256,
        expected_sites_sha256=receipt.SFLD_4_SITES_SHA256,
        enforce_release_contract=True,
    )
    manifest = receipt.build_sfld_release_manifest(release)

    assert len(release.models) == 299
    assert manifest["manifest_sha256"] == (
        "8b492f010c965f5d76f21e6d5665976570f7c14f25dc7499e9ecd6105ab685ad"
    )
