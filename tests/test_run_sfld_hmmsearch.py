"""Tests for the saved-plan SFLD controlled-run boundary."""

from __future__ import annotations

import hashlib
import json
import pathlib
import sys
from typing import Any

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import run_sfld_hmmsearch as runner  # noqa: E402
import validate_sfld_hmmsearch_receipt as receipt  # noqa: E402


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


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
DOMTBLOUT_PREFIX = (
    "# target name accession tlen query name accession qlen full-Evalue score bias\n"
    "# Program:         hmmsearch\n"
    "# Version:         3.4 (Aug 2023)\n"
)


def _registry_row() -> dict[str, Any]:
    sequence = "DACDEG"
    return {
        "protein_id": "UniProtKB:P12345",
        "protein_label": "Synthetic controlled-run target",
        "reviewed": True,
        "sequence": sequence,
        "sequence_length": len(sequence),
        "sequence_sha256": _sha(sequence.encode("ascii")),
        "sequence_version": 1,
        "taxon_id": "NCBITaxon:9606",
        "taxon_label": "Homo sapiens",
        "uniprot_release": "2026_02",
    }


def _fake_executable(path: pathlib.Path, *, behavior: str = "success") -> pathlib.Path:
    program = f"""#!{sys.executable}
import pathlib
import sys

VERSION = {VERSION!r}
ALIGNMENT = {ALIGNMENT!r}
DOMTBL_PREFIX = {DOMTBLOUT_PREFIX!r}
DOMTBL_ROW = {DOMTBL_ROW!r}
BEHAVIOR = {behavior!r}
if BEHAVIOR == "unsupported_version":
    VERSION = VERSION.replace("3.4", "3.3.2")
if BEHAVIOR == "missing_capability":
    VERSION = VERSION.replace("  --cut_ga  : use profile GA gathering cutoffs\\n", "")

if sys.argv[1:] == ["-h"]:
    sys.stdout.write(VERSION)
    if BEHAVIOR == "version_stderr":
        sys.stderr.write("unexpected version diagnostic\\n")
    raise SystemExit(0)
if BEHAVIOR == "exit_nonzero":
    raise SystemExit(7)

args = sys.argv[1:]
alignment_path = pathlib.Path(args[args.index("-A") + 1])
domtblout_path = pathlib.Path(args[args.index("--domtblout") + 1])
hmm_path = pathlib.Path(args[-2])
fasta_path = pathlib.Path(args[-1])
if pathlib.Path.cwd() != hmm_path.parent:
    raise SystemExit(8)
row = DOMTBL_ROW
if BEHAVIOR == "no_selected_hit":
    row = row.replace("UniProtKB:P12345", "UniProtKB:Q99999")
alignment_path.write_text(ALIGNMENT, encoding="ascii")
if BEHAVIOR == "replace_domtbl_inode":
    domtblout_path.unlink()
domtblout_path.write_text(DOMTBL_PREFIX + row + "\\n", encoding="ascii")
if BEHAVIOR == "mutate_copied_hmm":
    hmm_path.write_text("mutated by controlled process\\n", encoding="ascii")
sys.stdout.write(
    VERSION
    + f"# query HMM file:                  {{hmm_path}}\\n"
    + f"# target sequence database:        {{fasta_path}}\\n"
    + f"# MSA of all hits saved to file:   {{alignment_path}}\\n"
    + f"# per-dom hits tabular output:     {{domtblout_path}}\\n"
    + "# model-specific thresholding:     GA cutoffs\\n"
    + "# random number seed set to:       42\\n"
    + "# targ <seqfile> format asserted:  fasta\\n"
    + "# number of worker threads:        0\\n"
    + "Query: Model_SFLDF00001 [M=4]\\n//\\n"
)
"""
    path.write_text(program, encoding="utf-8")
    path.chmod(0o755)
    return path


def _bundle(
    tmp_path: pathlib.Path,
    *,
    behavior: str = "success",
) -> tuple[runner.SourcePaths, pathlib.Path, dict[str, str]]:
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    executable = _fake_executable(source_dir / "hmmsearch", behavior=behavior)
    hmm = source_dir / "sfld.hmm"
    hierarchy = source_dir / "sfld_hierarchy_flat.txt"
    sites = source_dir / "sfld_sites.annot"
    registry = source_dir / "protein_registry.jsonl"
    hmm.write_bytes(HMM)
    hierarchy.write_bytes(HIERARCHY)
    sites.write_bytes(SITES)
    registry.write_text(receipt.canonical_json(_registry_row()) + "\n", encoding="ascii")
    paths = runner.SourcePaths(
        executable=executable,
        hmm=hmm,
        hierarchy=hierarchy,
        sites=sites,
        registry=registry,
        runner=REPO / "scripts/run_sfld_hmmsearch.py",
    )
    hashes = {
        "expected_hmm_sha256": _sha(HMM),
        "expected_hierarchy_sha256": _sha(HIERARCHY),
        "expected_sites_sha256": _sha(SITES),
    }
    return paths, tmp_path / "controlled-run", hashes


def _plan(
    paths: runner.SourcePaths,
    output_dir: pathlib.Path,
    hashes: dict[str, str],
) -> dict[str, Any]:
    return runner.derive_execution_plan(
        paths=paths,
        output_dir=output_dir,
        model_accession="SFLDF00001",
        target_protein_id="UniProtKB:P12345",
        domain_number=1,
        timeout_seconds=30,
        approved_executable_sha256=_sha(paths.executable.read_bytes()),
        enforce_release_contract=False,
        **hashes,
    )


def _save_plan(tmp_path: pathlib.Path, value: dict[str, Any]) -> pathlib.Path:
    path = tmp_path / "execution-plan.json"
    path.write_text(receipt.canonical_json(value) + "\n", encoding="ascii")
    return path


def _execute(
    plan_path: pathlib.Path,
    paths: runner.SourcePaths,
    output_dir: pathlib.Path,
    hashes: dict[str, str],
) -> dict[str, Any]:
    return runner.execute_saved_plan(
        execution_plan_path=plan_path,
        paths=paths,
        output_dir=output_dir,
        model_accession="SFLDF00001",
        target_protein_id="UniProtKB:P12345",
        domain_number=1,
        timeout_seconds=30,
        approved_executable_sha256=_sha(paths.executable.read_bytes()),
        enforce_release_contract=False,
        captured_at_utc="2026-08-25T12:34:56Z",
        **hashes,
    )


def test_dry_plan_is_deterministic_content_addressed_and_executes_nothing(tmp_path):
    paths, output_dir, hashes = _bundle(tmp_path)

    first = _plan(paths, output_dir, hashes)
    second = _plan(paths, output_dir, hashes)

    assert first == second
    assert first["plan_id"].startswith(runner.PLAN_ID_PREFIX)
    assert first["execution"]["argv"] == [
        str((output_dir / "hmmsearch").absolute()),
        "--cut_ga",
        "--cpu",
        "0",
        "--seed",
        "42",
        "--tformat",
        "fasta",
        "-A",
        str((output_dir / "hits.sto").absolute()),
        "--domtblout",
        str((output_dir / "hits.domtblout").absolute()),
        str((output_dir / "sfld.hmm").absolute()),
        str((output_dir / "targets.fasta").absolute()),
    ]
    assert first["safety_boundary"]["trait_writes_authorized"] is False
    assert first["source_binding"]["executable_policy"] == {
        "approval_basis": "OPERATOR_SUPPLIED_EXACT_SHA256",
        "approved_sha256": _sha(paths.executable.read_bytes()),
        "approval_is_not_producer_authentication": True,
    }
    assert not output_dir.exists()


def test_unapproved_executable_digest_fails_before_any_output(tmp_path):
    paths, output_dir, hashes = _bundle(tmp_path)

    with pytest.raises(runner.SfldHmmsearchRunError, match="explicitly approved SHA-256"):
        runner.derive_execution_plan(
            paths=paths,
            output_dir=output_dir,
            model_accession="SFLDF00001",
            target_protein_id="UniProtKB:P12345",
            domain_number=1,
            timeout_seconds=30,
            approved_executable_sha256="0" * 64,
            enforce_release_contract=False,
            **hashes,
        )

    assert not output_dir.exists()


def test_exact_saved_plan_runs_copied_executable_and_installs_verified_receipt_last(
    tmp_path, monkeypatch
):
    paths, output_dir, hashes = _bundle(tmp_path)
    plan = _plan(paths, output_dir, hashes)
    plan_path = _save_plan(tmp_path, plan)
    created: list[str] = []
    original_create = runner._create_file  # noqa: SLF001
    original_install = runner._install_verified_receipt  # noqa: SLF001

    def recording_create(directory_descriptor, name, **kwargs):
        created.append(f"create:{name}")
        return original_create(directory_descriptor, name, **kwargs)

    def recording_install(directory_descriptor, **kwargs):
        result = original_install(directory_descriptor, **kwargs)
        created.append(f"install:{kwargs['final_name']}")
        return result

    monkeypatch.setattr(runner, "_create_file", recording_create)
    monkeypatch.setattr(runner, "_install_verified_receipt", recording_install)
    result = _execute(plan_path, paths, output_dir, hashes)

    assert result["status"] == "PASS_CONTROLLED_RUN_AND_RECEIPT_CONTENT_SEMANTIC_REPLAY"
    assert result["grounding_eligible"] is False
    assert result["hmmer_executable_build_or_acquisition_receipt_verified"] is False
    assert created[-1] == "install:selected-domain.receipt.json"
    assert not (output_dir / "selected-domain.receipt.candidate.json").exists()
    assert json.loads((output_dir / "execution-plan.json").read_text()) == plan
    installed = json.loads((output_dir / "selected-domain.receipt.json").read_text())
    assert installed["execution"]["argv"][0] == str(output_dir / "hmmsearch")
    assert installed["artifacts"]["hmm"]["path"] == str(output_dir / "sfld.hmm")
    assert installed["selected_domain"]["model_accession"] == "SFLDF00001"
    assert installed["selected_domain"]["target_sequence_identifier"] == "UniProtKB:P12345"
    assert result["receipt_verification"]["artifact_and_semantic_bindings_verified"] is True

    # The completed bundle is self-contained; changing external source copies
    # cannot alter or invalidate the installed receipt.
    paths.executable.write_text("changed after completed run\n", encoding="ascii")
    paths.hmm.write_bytes(b"changed after completed run\n")
    receipt_paths = receipt.ReceiptPaths(
        receipt=output_dir / "selected-domain.receipt.json",
        executable=output_dir / "hmmsearch",
        version_stdout=output_dir / "hmmsearch-version.stdout",
        version_stderr=output_dir / "hmmsearch-version.stderr",
        hmm=output_dir / "sfld.hmm",
        hierarchy=output_dir / "sfld_hierarchy_flat.txt",
        sites=output_dir / "sfld_sites.annot",
        registry=output_dir / "protein_registry.jsonl",
        fasta=output_dir / "targets.fasta",
        main_output=output_dir / "hmmsearch.stdout",
        stderr_output=output_dir / "hmmsearch.stderr",
        alignment_output=output_dir / "hits.sto",
        domtblout=output_dir / "hits.domtblout",
    )
    assert (
        receipt.verify_receipt(
            paths=receipt_paths,
            enforce_release_contract=False,
            **hashes,
        )["receipt_id"]
        == installed["receipt_id"]
    )


def test_saved_plan_input_drift_fails_before_output_directory_creation(tmp_path):
    paths, output_dir, hashes = _bundle(tmp_path)
    plan_path = _save_plan(tmp_path, _plan(paths, output_dir, hashes))
    paths.executable.write_text("#!/bin/sh\nexit 0\n", encoding="ascii")
    paths.executable.chmod(0o755)

    with pytest.raises(runner.SfldHmmsearchRunError, match="does not match current"):
        _execute(plan_path, paths, output_dir, hashes)

    assert not output_dir.exists()


def test_noncanonical_or_readdressed_plan_fails_before_execution(tmp_path):
    paths, output_dir, hashes = _bundle(tmp_path)
    plan = _plan(paths, output_dir, hashes)
    noncanonical = tmp_path / "noncanonical.json"
    noncanonical.write_text(json.dumps(plan, indent=2) + "\n", encoding="ascii")
    with pytest.raises(runner.SfldHmmsearchRunError, match="one canonical JSON row"):
        _execute(noncanonical, paths, output_dir, hashes)
    assert not output_dir.exists()

    plan["selector"]["domain_number"] = 2
    payload = dict(plan)
    payload.pop("plan_id")
    plan["plan_id"] = runner.PLAN_ID_PREFIX + receipt.value_sha256(payload)
    readdressed = _save_plan(tmp_path, plan)
    with pytest.raises(runner.SfldHmmsearchRunError, match="does not match current"):
        _execute(readdressed, paths, output_dir, hashes)
    assert not output_dir.exists()


@pytest.mark.parametrize(
    ("behavior", "message"),
    [
        ("exit_nonzero", "hmmsearch exited 7"),
        ("no_selected_hit", "0 rows for the exact"),
        ("replace_domtbl_inode", "run artifact identity changed"),
        ("mutate_copied_hmm", "changed copied source artifact hmm"),
        ("unsupported_version", "unsupported HMMER version"),
        ("missing_capability", "required capability"),
        ("version_stderr", "unexpected stderr"),
    ],
)
def test_failed_or_inconsistent_process_leaves_started_bundle_without_receipt(
    tmp_path, behavior, message
):
    paths, output_dir, hashes = _bundle(tmp_path, behavior=behavior)
    plan_path = _save_plan(tmp_path, _plan(paths, output_dir, hashes))

    with pytest.raises(runner.SfldHmmsearchRunError, match=message):
        _execute(plan_path, paths, output_dir, hashes)

    assert output_dir.is_dir()
    assert (output_dir / "run.started.json").is_file()
    assert not (output_dir / "selected-domain.receipt.json").exists()


def test_existing_output_or_symlinked_parent_fails_without_replacement(tmp_path):
    paths, output_dir, hashes = _bundle(tmp_path)
    output_dir.mkdir()
    sentinel = output_dir / "sentinel"
    sentinel.write_text("preserve\n", encoding="ascii")
    with pytest.raises(runner.SfldHmmsearchRunError, match="already exists"):
        _plan(paths, output_dir, hashes)
    assert sentinel.read_text(encoding="ascii") == "preserve\n"

    real_parent = tmp_path / "real-parent"
    real_parent.mkdir()
    linked_parent = tmp_path / "linked-parent"
    linked_parent.symlink_to(real_parent, target_is_directory=True)
    with pytest.raises(runner.SfldHmmsearchRunError, match="cannot safely bind directory"):
        _plan(paths, linked_parent / "run", hashes)
    assert not (real_parent / "run").exists()


def test_cli_requires_saved_plan_for_apply_before_any_output(tmp_path, monkeypatch, capsys):
    paths, output_dir, _hashes = _bundle(tmp_path)
    monkeypatch.setattr(runner, "SFLD_4_HMM_SHA256", _sha(HMM))
    argv = [
        "--executable",
        str(paths.executable),
        "--hmm",
        str(paths.hmm),
        "--hierarchy",
        str(paths.hierarchy),
        "--sites",
        str(paths.sites),
        "--registry",
        str(paths.registry),
        "--output-dir",
        str(output_dir),
        "--model-accession",
        "SFLDF00001",
        "--target-protein-id",
        "UniProtKB:P12345",
        "--approved-executable-sha256",
        _sha(paths.executable.read_bytes()),
        "--apply",
    ]

    assert runner.main(argv) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "--apply requires --execution-plan" in captured.err
    assert not output_dir.exists()


def test_current_production_sources_support_exact_dry_plan_without_hmmer_execution(
    tmp_path,
    capsys,
):
    production = {
        "hmm": runner.DEFAULT_HMM,
        "hierarchy": runner.DEFAULT_HIERARCHY,
        "sites": runner.DEFAULT_SITES,
        "registry": runner.DEFAULT_REGISTRY,
    }
    if not all(path.is_file() for path in production.values()):
        pytest.skip("production SFLD/registry source artifacts are not installed")
    executable = _fake_executable(tmp_path / "synthetic-hmmsearch")
    first_registry_row = json.loads(
        production["registry"].read_text(encoding="ascii").splitlines()[0]
    )
    paths = runner.SourcePaths(
        executable=executable,
        hmm=production["hmm"],
        hierarchy=production["hierarchy"],
        sites=production["sites"],
        registry=production["registry"],
        runner=REPO / "scripts/run_sfld_hmmsearch.py",
    )
    output_dir = tmp_path / "production-dry-plan"

    plan = runner.derive_execution_plan(
        paths=paths,
        output_dir=output_dir,
        model_accession="SFLDF00001",
        target_protein_id=first_registry_row["protein_id"],
        domain_number=1,
        timeout_seconds=30,
        approved_executable_sha256=_sha(executable.read_bytes()),
    )

    assert plan["source_binding"]["model_count"] == 299
    assert plan["target_registry_projection"]["protein_count"] == 126
    assert plan["target_registry_projection"]["canonical_fasta_sha256"] == (
        "0aa2b6f9d1ce74ebc132184284475de53f55ccc62d0ecd7498d79d522ef18e9f"
    )
    assert plan["inputs"]["hmm"]["sha256"] == runner.SFLD_4_HMM_SHA256
    assert not output_dir.exists()

    argv = [
        "--executable",
        str(executable),
        "--output-dir",
        str(output_dir),
        "--model-accession",
        "SFLDF00001",
        "--target-protein-id",
        first_registry_row["protein_id"],
        "--timeout-seconds",
        "30",
        "--approved-executable-sha256",
        _sha(executable.read_bytes()),
    ]
    assert runner.main(argv) == 0
    captured = capsys.readouterr()
    assert captured.err == ""
    assert captured.out == receipt.canonical_json(plan) + "\n"
    assert not output_dir.exists()
