"""Safety tests for the staging-only historical receipt bootstrap."""

from __future__ import annotations

import hashlib
import importlib
import json
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
bootstrap = importlib.import_module("bootstrap_uniprot_record_bindings")
ground = importlib.import_module("ground_uniprot_examples")
gate_module = importlib.import_module("uniprot_record_content_gate")
validator = importlib.import_module("validate_uniprot_grounding")


def _jsonl(path: pathlib.Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n" for row in rows),
        encoding="utf-8",
    )


def _rows(path: pathlib.Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def _sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _record() -> str:
    return (
        "identifier: Pfam:PF00001\n"
        "label: Fixture domain\n"
        "definition: A fixture domain.\n"
        "definition_source: Fixture\n"
        "trait_axis: SEQUENCE\n"
        "trait_category: SEQ_DOMAIN\n"
        "mapping_status: SEEDED\n"
        "license: CC0-1.0\n"
    )


def _case(tmp_path: pathlib.Path, monkeypatch) -> dict:
    repo = tmp_path / "repo"
    traits = repo / "data" / "traits"
    grounding = repo / "data" / "grounding"
    reports = repo / "reports" / "uniprot-grounding" / "review-batches"
    traits.mkdir(parents=True)
    grounding.mkdir(parents=True)
    reports.mkdir(parents=True)
    record = traits / "fixture.yaml"
    original = _record()
    record.write_text(original, encoding="utf-8")

    sequence = "ACDEFGHIK"
    sequence_sha = hashlib.sha256(sequence.encode("ascii")).hexdigest()
    reference = {
        "protein_id": "UniProtKB:P12345",
        "protein_label": "Fixture protein",
        "taxon_id": "NCBITaxon:9606",
        "taxon_label": "Homo sapiens",
        "sequence": sequence,
        "sequence_length": len(sequence),
        "sequence_sha256": sequence_sha,
        "sequence_version": 1,
        "reviewed": True,
        "uniprot_release": "2026_02",
    }
    occurrence = {
        "trait_id": "Pfam:PF00001",
        "protein_id": "UniProtKB:P12345",
        "scope": "LOCALIZED",
        "coordinate_frame": "UNIPROT_CANONICAL",
        "intervals": [{"start": 2, "end": 5}],
        "source_trait_id": "Pfam:PF00001",
        "mapping_method": "INTERPRO_MATCH",
        "evidence_source": "InterPro",
        "source_release": "109.0",
        "sequence_sha256": sequence_sha,
        "qualification_status": "QUALIFIED",
    }
    evidence = validator.build_grounding_evidence(
        occurrence,
        provider_kind="INTERPRO",
        provider_source="InterPro",
        provider_release="109.0",
        provider_entry_sha256="1" * 64,
    )
    occurrence["source_evidence_id"] = evidence["evidence_id"]
    row = {
        "schema_version": 1,
        "batch": "ready-local-review-fixture",
        "batch_id": "ready-local-review-fixture",
        "candidate_status": "QUALIFIED",
        "qualification_status": "QUALIFIED",
        "candidate_id": "",
        "trait_id": "Pfam:PF00001",
        "source_trait_id": "Pfam:PF00001",
        "record_path": "data/traits/fixture.yaml",
        "record_sha256": hashlib.sha256(original.encode("utf-8")).hexdigest(),
        "source_namespace": "Pfam",
        "trait_axis": "SEQUENCE",
        "trait_category": "SEQ_DOMAIN",
        "protein_id": reference["protein_id"],
        "protein_label": reference["protein_label"],
        "taxon_id": reference["taxon_id"],
        "taxon_label": reference["taxon_label"],
        "sequence_length": reference["sequence_length"],
        "sequence_sha256": sequence_sha,
        "sequence_version": 1,
        "reviewed": True,
        "uniprot_release": reference["uniprot_release"],
        "scope": "LOCALIZED",
        "coordinate_frame": "UNIPROT_CANONICAL",
        "intervals": [{"start": 2, "end": 5}],
        "residue_positions": [],
        "mapping_method": "INTERPRO_MATCH",
        "evidence_source": "InterPro",
        "source_release": "109.0",
        "evidence_tier": "A",
        "provider_evidence": [],
        "protein_reference_sha256": ground._value_digest(reference),
        "trait_occurrence": occurrence,
        "grounding_evidence": evidence,
        "reasons": [],
    }
    row["candidate_id"] = ground.derive_candidate_id(row)
    row["resolution_digest"] = ground._resolution_digest(row)
    decision = {
        "candidate_id": row["candidate_id"],
        "decision": "APPROVED",
        "primary_review_candidate_id": row["candidate_id"],
        "record_key": {
            "record_path": row["record_path"],
            "trait_id": row["trait_id"],
        },
        "resolution_digest": row["resolution_digest"],
        "review_notes": "Explicit fixture review.",
        "reviewed_at": "2026-08-24",
        "reviewer": "Test Curator",
    }

    resolved = reports / "fixture.resolved.jsonl"
    decisions = reports / "fixture.review-decisions.digest-bound.jsonl"
    staging_proteins = reports / "fixture.protein_registry.jsonl"
    staging_evidence = reports / "fixture.occurrence_evidence.jsonl"
    durable_proteins = grounding / "protein_registry.jsonl"
    durable_evidence = grounding / "occurrence_evidence.jsonl"
    _jsonl(resolved, [row])
    _jsonl(decisions, [decision])
    _jsonl(staging_proteins, [reference])
    _jsonl(staging_evidence, [evidence])
    _jsonl(durable_proteins, [reference])
    _jsonl(durable_evidence, [evidence])

    # Promotion reads the canonical JSONL image, whose nested key order is the order
    # subsequently emitted into YAML.  Re-read that exact image here as production did.
    installed, changed = ground._install_example(yaml.safe_load(original), _rows(resolved)[0])
    assert changed
    record.write_text(ground._replace_examples_block(original, installed), encoding="utf-8")

    monkeypatch.setattr(bootstrap, "REPO_ROOT", repo)
    monkeypatch.setattr(bootstrap, "DATA_ROOT", repo / "data")
    monkeypatch.setattr(bootstrap, "TRAITS_ROOT", traits)
    monkeypatch.setattr(bootstrap, "DURABLE_PROTEIN_REGISTRY", durable_proteins)
    monkeypatch.setattr(bootstrap, "DURABLE_EVIDENCE_REGISTRY", durable_evidence)
    monkeypatch.setattr(bootstrap, "REVIEW_ARTIFACT_ROOT", reports)
    monkeypatch.setattr(ground, "REPO_ROOT", repo)
    monkeypatch.setattr(bootstrap, "_head_text", lambda _record_path: original)
    monkeypatch.setattr(
        bootstrap,
        "EXPECTED_PROFILE",
        bootstrap.BootstrapProfile(
            input_sha256={
                "resolved": _sha(resolved),
                "decisions": _sha(decisions),
                "staging_proteins": _sha(staging_proteins),
                "staging_evidence": _sha(staging_evidence),
                "durable_proteins": _sha(durable_proteins),
                "durable_evidence": _sha(durable_evidence),
            },
            resolved_rows=1,
            decision_rows=1,
            approved_rows=1,
            staging_proteins=1,
            staging_evidence=1,
            durable_proteins=1,
            durable_evidence=1,
        ),
    )

    original_projection = ground._content_gate_projection

    def hard_projection(gate, trait_record, candidate, args):
        projection, findings = original_projection(gate, trait_record, candidate, args)
        finding = gate_module.Finding(
            code="DEFINITION_TEMPLATE_ONLY",
            severity=gate_module.HARD,
            detail="fixture hard blocker",
        )
        projection["findings"] = [*projection["findings"], finding.as_dict()]
        return projection, [*findings, finding]

    monkeypatch.setattr(ground, "_content_gate_projection", hard_projection)
    return {
        "repo": repo,
        "traits": traits,
        "record": record,
        "resolved": resolved,
        "decisions": decisions,
        "staging_proteins": staging_proteins,
        "staging_evidence": staging_evidence,
        "durable_proteins": durable_proteins,
        "durable_evidence": durable_evidence,
        "clean": reports / "fixture.receipts-incomplete-clean.jsonl",
        "blocked": reports / "fixture.receipts-blocked.jsonl",
        "manifest": reports / "fixture.receipts-manifest.json",
        "evidence_id": evidence["evidence_id"],
    }


def _args(case: dict, *, write: bool = False) -> list[str]:
    args = [
        "--resolved",
        str(case["resolved"]),
        "--decisions",
        str(case["decisions"]),
        "--staging-protein-registry",
        str(case["staging_proteins"]),
        "--staging-evidence-registry",
        str(case["staging_evidence"]),
        "--durable-protein-registry",
        str(case["durable_proteins"]),
        "--durable-evidence-registry",
        str(case["durable_evidence"]),
        "--traits",
        str(case["traits"]),
        "--clean-out",
        str(case["clean"]),
        "--blocked-out",
        str(case["blocked"]),
        "--manifest-out",
        str(case["manifest"]),
    ]
    if write:
        args.append("--write-staging")
    return args


def test_dry_run_validates_but_never_writes_incomplete_outputs(tmp_path, monkeypatch, capsys):
    case = _case(tmp_path, monkeypatch)

    assert bootstrap.main(_args(case)) == bootstrap.INCOMPLETE_EXIT
    output = capsys.readouterr().out
    assert "DRY-RUN: 0 gate-clean incomplete receipt(s), 1 hard-blocked claim(s)" in output
    assert "complete=false" in output
    assert "no staging, trait, or durable registry artifact written" in output
    assert not any(case[key].exists() for key in ("clean", "blocked", "manifest"))


def test_write_staging_is_incomplete_deterministic_and_keeps_hard_rows_out_of_clean(
    tmp_path, monkeypatch, capsys
):
    case = _case(tmp_path, monkeypatch)

    assert bootstrap.main(_args(case, write=True)) == bootstrap.INCOMPLETE_EXIT
    assert "durable coverage remains incomplete" in capsys.readouterr().out
    assert case["clean"].read_text(encoding="utf-8") == ""
    blocked = _rows(case["blocked"])
    assert len(blocked) == 1
    assert blocked[0]["evidence_id"] == case["evidence_id"]
    assert blocked[0]["status"] == "HARD_BLOCKED"
    assert blocked[0]["hard_codes"] == ["DEFINITION_TEMPLATE_ONLY"]
    manifest = json.loads(case["manifest"].read_text(encoding="utf-8"))
    assert manifest["complete"] is False
    assert manifest["staging_only"] is True
    assert manifest["counts"]["durable_evidence"] == 1
    assert manifest["counts"]["clean_receipts"] == 0
    assert manifest["counts"]["blocked"] == 1
    assert manifest["counts"]["missing_receipts"] == 1
    first = {key: case[key].read_bytes() for key in ("clean", "blocked", "manifest")}

    assert bootstrap.main(_args(case, write=True)) == bootstrap.INCOMPLETE_EXIT
    assert all(case[key].read_bytes() == first[key] for key in first)


@pytest.mark.parametrize(
    ("role", "replacement", "expected"),
    [
        ("clean", "outside.receipts-incomplete-clean.jsonl", "beneath"),
        ("blocked", "unsafe.receipts-blocked.jsonl", "beneath"),
        ("manifest", "unsafe.receipts-manifest.json", "beneath"),
    ],
)
def test_outputs_outside_ignored_review_root_are_refused(
    tmp_path, monkeypatch, capsys, role, replacement, expected
):
    case = _case(tmp_path, monkeypatch)
    case[role] = tmp_path / replacement

    assert bootstrap.main(_args(case, write=True)) == 2
    assert expected in capsys.readouterr().err
    assert not case[role].exists()


@pytest.mark.parametrize(
    ("role", "name"),
    [
        ("clean", "fixture.complete.receipts-incomplete-clean.jsonl"),
        ("clean", "fixture.durable.receipts-incomplete-clean.jsonl"),
        ("blocked", "fixture.durable.receipts-blocked.jsonl"),
    ],
)
def test_complete_or_durable_named_outputs_are_refused(tmp_path, monkeypatch, capsys, role, name):
    case = _case(tmp_path, monkeypatch)
    case[role] = bootstrap.REVIEW_ARTIFACT_ROOT / name

    assert bootstrap.main(_args(case, write=True)) == 2
    assert "complete or durable" in capsys.readouterr().err
    assert not case[role].exists()


@pytest.mark.parametrize("subdirectory", ["traits", "grounding"])
def test_data_tree_outputs_are_categorically_refused(tmp_path, monkeypatch, capsys, subdirectory):
    case = _case(tmp_path, monkeypatch)
    case["clean"] = bootstrap.DATA_ROOT / subdirectory / "unsafe.receipts-incomplete-clean.jsonl"

    assert bootstrap.main(_args(case, write=True)) == 2
    assert "beneath" in capsys.readouterr().err
    assert not case["clean"].exists()


def test_tampered_pinned_input_fails_before_any_output(tmp_path, monkeypatch, capsys):
    case = _case(tmp_path, monkeypatch)
    case["decisions"].write_text("{}\n", encoding="utf-8")

    assert bootstrap.main(_args(case, write=True)) == 2
    assert "decisions SHA-256 mismatch" in capsys.readouterr().err
    assert not any(case[key].exists() for key in ("clean", "blocked", "manifest"))


def test_missing_pinned_input_fails_before_any_output(tmp_path, monkeypatch, capsys):
    case = _case(tmp_path, monkeypatch)
    case["staging_evidence"].unlink()

    assert bootstrap.main(_args(case, write=True)) == 2
    assert "required input artifact does not exist" in capsys.readouterr().err
    assert not any(case[key].exists() for key in ("clean", "blocked", "manifest"))


def test_duplicate_installed_occurrence_is_refused(tmp_path, monkeypatch, capsys):
    case = _case(tmp_path, monkeypatch)
    duplicate = case["traits"] / "duplicate.yaml"
    record = yaml.safe_load(case["record"].read_text(encoding="utf-8"))
    record["identifier"] = "Pfam:PF99999"
    duplicate.write_text(yaml.safe_dump(record, sort_keys=False), encoding="utf-8")

    assert bootstrap.main(_args(case, write=True)) == 2
    assert "resolves to 2 installed occurrences" in capsys.readouterr().err
    assert not any(case[key].exists() for key in ("clean", "blocked", "manifest"))


def test_stale_installed_record_is_refused(tmp_path, monkeypatch, capsys):
    case = _case(tmp_path, monkeypatch)
    case["record"].write_text(
        case["record"].read_text(encoding="utf-8") + "# stale edit\n", encoding="utf-8"
    )

    assert bootstrap.main(_args(case, write=True)) == 2
    assert "differs from the deterministic Batch-001 install" in capsys.readouterr().err
    assert not any(case[key].exists() for key in ("clean", "blocked", "manifest"))


def test_duplicate_decision_fails_even_when_fixture_profile_binds_changed_bytes(
    tmp_path, monkeypatch, capsys
):
    case = _case(tmp_path, monkeypatch)
    decision = _rows(case["decisions"])[0]
    _jsonl(case["decisions"], [decision, decision])
    profile = bootstrap.EXPECTED_PROFILE
    hashes = dict(profile.input_sha256)
    hashes["decisions"] = _sha(case["decisions"])
    monkeypatch.setattr(
        bootstrap,
        "EXPECTED_PROFILE",
        bootstrap.BootstrapProfile(
            input_sha256=hashes,
            resolved_rows=1,
            decision_rows=2,
            approved_rows=1,
            staging_proteins=1,
            staging_evidence=1,
            durable_proteins=1,
            durable_evidence=1,
        ),
    )

    assert bootstrap.main(_args(case, write=True)) == 2
    assert "duplicates candidate_id" in capsys.readouterr().err
    assert not any(case[key].exists() for key in ("clean", "blocked", "manifest"))


def test_atomic_staging_failure_restores_all_three_preimages(tmp_path, monkeypatch, capsys):
    case = _case(tmp_path, monkeypatch)
    for key in ("clean", "blocked", "manifest"):
        case[key].write_text(f"old-{key}\n", encoding="utf-8")
    original = {key: case[key].read_bytes() for key in ("clean", "blocked", "manifest")}
    atomic_text = ground._atomic_text
    calls = 0

    def fail_once(path, text):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("fixture staging failure")
        atomic_text(path, text)

    monkeypatch.setattr(ground, "_atomic_text", fail_once)

    assert bootstrap.main(_args(case, write=True)) == 2
    assert "rolled back" in capsys.readouterr().err
    assert all(case[key].read_bytes() == original[key] for key in original)


def test_receipt_covered_record_race_fails_before_staging_write(tmp_path, monkeypatch, capsys):
    case = _case(tmp_path, monkeypatch)
    build_result = bootstrap._build_result

    def build_then_change(*args, **kwargs):
        result = build_result(*args, **kwargs)
        case["record"].write_text(
            case["record"].read_text(encoding="utf-8") + "# concurrent edit\n",
            encoding="utf-8",
        )
        return result

    monkeypatch.setattr(bootstrap, "_build_result", build_then_change)

    assert bootstrap.main(_args(case, write=True)) == 2
    assert "changed during bootstrap preflight" in capsys.readouterr().err
    assert not any(case[key].exists() for key in ("clean", "blocked", "manifest"))


def test_unapproved_historical_sfld_evidence_remains_candidate_only(tmp_path, monkeypatch, capsys):
    case = _case(tmp_path, monkeypatch)
    rows = _rows(case["staging_evidence"])
    sfld = dict(rows[0])
    sfld["trait_id"] = "SFLD:SFLDF00001"
    sfld["source_trait_id"] = "SFLD:SFLDF00001"
    sfld["evidence_id"] = validator.compute_evidence_id(sfld)
    findings = validator.validate_grounding_evidence(sfld, path=case["staging_evidence"], line=2)
    assert [finding.code for finding in findings] == [
        bootstrap.HISTORICAL_UNAPPROVED_STAGING_FINDING
    ]
    _jsonl(case["staging_evidence"], [*rows, sfld])

    profile = bootstrap.EXPECTED_PROFILE
    hashes = dict(profile.input_sha256)
    hashes["staging_evidence"] = _sha(case["staging_evidence"])
    monkeypatch.setattr(
        bootstrap,
        "EXPECTED_PROFILE",
        bootstrap.BootstrapProfile(
            input_sha256=hashes,
            resolved_rows=profile.resolved_rows,
            decision_rows=profile.decision_rows,
            approved_rows=profile.approved_rows,
            staging_proteins=profile.staging_proteins,
            staging_evidence=2,
            durable_proteins=profile.durable_proteins,
            durable_evidence=profile.durable_evidence,
        ),
    )

    assert bootstrap.main(_args(case)) == bootstrap.INCOMPLETE_EXIT
    assert "0 gate-clean incomplete receipt(s), 1 hard-blocked claim(s)" in capsys.readouterr().out
    assert not any(case[key].exists() for key in ("clean", "blocked", "manifest"))

    with pytest.raises(bootstrap.BootstrapError, match="sfld_provider_receipt_required"):
        bootstrap._historical_staging_evidence_registry(
            case["staging_evidence"], approved_evidence_ids=frozenset({sfld["evidence_id"]})
        )


def test_real_batch001_dry_run_when_ignored_fixture_is_available(capsys):
    batch = REPO / "reports" / "uniprot-grounding" / "review-batches"
    required = {
        "resolved": batch / "ready-local-review-001.resolved.jsonl",
        "decisions": batch / "ready-local-review-001.review-decisions.digest-bound.jsonl",
        "staging_proteins": batch / "ready-local-review-001.protein_registry.jsonl",
        "staging_evidence": batch / "ready-local-review-001.occurrence_evidence.jsonl",
        "durable_proteins": REPO / "data" / "grounding" / "protein_registry.jsonl",
        "durable_evidence": REPO / "data" / "grounding" / "occurrence_evidence.jsonl",
    }
    if not all(path.is_file() for path in required.values()):
        pytest.skip("ignored Batch-001 migration fixture is unavailable")

    # This replays a PRE-promotion dry run, and the tool reads each record's
    # historical preimage from the current Git HEAD (_head_text). That makes the
    # replay possible only while the promotion is uncommitted: once Batch-001 is
    # committed, HEAD returns the promoted record, its sha256 no longer matches
    # the reviewed preimage, and the tool reports staleness rather than the
    # counts below. The assertion is about the pre-promotion state, so say so and
    # skip instead of failing on a state change that is not a regression.
    # The HEAD coupling itself is filed separately.
    preimage_row = json.loads(required["resolved"].read_text(encoding="utf-8").splitlines()[0])
    if (
        bootstrap._sha256_text(bootstrap._head_text(str(preimage_row["record_path"])))
        != preimage_row["record_sha256"]
    ):
        pytest.skip("Batch-001 is committed at HEAD; its pre-promotion dry run cannot be replayed")

    clean = batch / "pytest-batch001.receipts-incomplete-clean.jsonl"
    blocked = batch / "pytest-batch001.receipts-blocked.jsonl"
    manifest = batch / "pytest-batch001.receipts-manifest.json"
    assert not any(path.exists() for path in (clean, blocked, manifest))
    args = [
        "--resolved",
        str(required["resolved"]),
        "--decisions",
        str(required["decisions"]),
        "--staging-protein-registry",
        str(required["staging_proteins"]),
        "--staging-evidence-registry",
        str(required["staging_evidence"]),
        "--durable-protein-registry",
        str(required["durable_proteins"]),
        "--durable-evidence-registry",
        str(required["durable_evidence"]),
        "--traits",
        str(REPO / "data" / "traits"),
        "--clean-out",
        str(clean),
        "--blocked-out",
        str(blocked),
        "--manifest-out",
        str(manifest),
    ]

    assert bootstrap.main(args) == bootstrap.INCOMPLETE_EXIT
    output = capsys.readouterr().out
    assert "120 gate-clean incomplete receipt(s), 7 hard-blocked claim(s)" in output
    assert "bbac03ec6d82e3e8e43a07b5fcd4b887c3ceee5f8537517ea41fb98e304416e9" in output
    assert not any(path.exists() for path in (clean, blocked, manifest))
