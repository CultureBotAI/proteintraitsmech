"""Focused tests for the no-write direct Rhea/UniProtKB staging boundary."""

from __future__ import annotations

import hashlib
import importlib
import json
import os
import sys
from pathlib import Path
from typing import Any, Callable

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
stage = importlib.import_module("stage_rhea_uniprot_grounding")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _trait_text(trait_id: str, equation: str, *, examples: bool = False) -> str:
    extra = "canonical_examples:\n  - protein_id: UniProtKB:P99999\n" if examples else ""
    return (
        f"identifier: {trait_id}\n"
        f"label: {json.dumps(equation)}\n"
        "definition: >-\n"
        f"  Enzymatic reaction ({trait_id}): {equation}. A specific curated "
        "biochemical reaction; a protein with this activity catalyses it.\n"
        "definition_source: Rhea\n"
        "trait_axis: FUNCTION\n"
        "trait_category: FUNC_ENZYMATIC_ACTIVITY\n"
        "term_kind: CLASS\n"
        "mapping_status: REVIEWED\n"
        f"{extra}"
        "license: CC-BY 4.0\n"
    )


def _reference(protein_id: str = "UniProtKB:P12345") -> dict[str, Any]:
    sequence = "ACDEFGHIK"
    return {
        "protein_id": protein_id,
        "protein_label": "Fixture enzyme",
        "reviewed": True,
        "sequence": sequence,
        "sequence_length": len(sequence),
        "sequence_sha256": hashlib.sha256(sequence.encode("ascii")).hexdigest(),
        "sequence_version": 1,
        "taxon_id": "NCBITaxon:9606",
        "taxon_label": "Homo sapiens",
        "uniprot_release": "2026_02",
    }


def _case(tmp_path: Path) -> dict[str, Any]:
    repo = tmp_path / "repo"
    raw = repo / "data" / "raw" / "rhea"
    traits_root = repo / "data" / "traits"
    traits = traits_root / "function" / "enzymatic_activity" / "rhea"
    registry = repo / "data" / "grounding" / "protein_registry.jsonl"
    paths = {
        "mapping": raw / "rhea2uniprot_sprot.tsv",
        "release_properties": raw / "rhea-release.properties",
        "tsv_readme": raw / "rhea-tsv-README.txt",
        "license": raw / "LICENSE.txt",
        "directions": raw / "rhea-directions.tsv",
        "reactions": raw / "rhea-reactions.tsv",
    }
    _write(
        paths["mapping"],
        stage.MAPPING_HEADER
        + "\n"
        + "10000\tUN\t10000\tP12345\n"
        + "10001\tLR\t10000\tP12345\n"
        + "20002\tRL\t20000\tQ9Y261\n",
    )
    _write(
        paths["release_properties"],
        "rhea.release.number=999\nrhea.release.date=2026-01-01\n",
    )
    _write(
        paths["tsv_readme"],
        "Files named rhea2<db>.tsv contain cross-references to other databases\n"
        "RHEA_ID: reaction\nDIRECTION: direction\nMASTER_ID: master\nID: record\n",
    )
    _write(
        paths["license"],
        "Creative Commons Attribution 4.0 International\n"
        "All files in the Rhea FTP directory may be copied and redistributed freely\n",
    )
    _write(
        paths["directions"],
        stage.DIRECTIONS_HEADER + "\n10000\t10001\t10002\t10003\n" + "20000\t20001\t20002\t20003\n",
    )
    _write(
        paths["reactions"],
        stage.REACTIONS_HEADER
        + "\nRHEA:10000\tA + B = C\tCHEBI:1;CHEBI:2\tEC:1.1.1.1\n"
        + "RHEA:20000\tD = E\tCHEBI:3;CHEBI:4\t\n",
    )
    trait_10000 = traits / "fixture-one-rhea10000.yaml"
    trait_20000 = traits / "fixture-two-rhea20000.yaml"
    _write(trait_10000, _trait_text("RHEA:10000", "A + B = C"))
    _write(trait_20000, _trait_text("RHEA:20000", "D = E"))
    registry.parent.mkdir(parents=True, exist_ok=True)
    registry.write_text(stage.canonical_json(_reference()) + "\n", encoding="utf-8")
    return {
        "repo": repo,
        "raw": raw,
        "traits_root": traits_root,
        "traits": traits,
        "registry": registry,
        "paths": paths,
        "trait_10000": trait_10000,
        "trait_20000": trait_20000,
    }


def _build(case: dict[str, Any]) -> stage.StageResult:
    paths = case["paths"]
    return stage.build_stage(
        mapping_path=paths["mapping"],
        release_properties_path=paths["release_properties"],
        tsv_readme_path=paths["tsv_readme"],
        license_path=paths["license"],
        directions_path=paths["directions"],
        reactions_path=paths["reactions"],
        traits_root=case["traits_root"],
        traits_dir=case["traits"],
        protein_registry_path=case["registry"],
        repo_root=case["repo"],
        expected_source_sha256={role: None for role in paths},
        expected_rhea_release="999",
        expected_rhea_release_date="2026-01-01",
        expected_uniprot_release="2026_02",
    )


def _assert_content_address(
    row: dict[str, Any], *, id_field: str, prefix: str, row_hash_field: str
) -> None:
    without_row_hash = dict(row)
    observed_row_hash = without_row_hash.pop(row_hash_field)
    assert observed_row_hash == stage.value_sha256(without_row_hash)
    observed_id = without_row_hash.pop(id_field)
    assert observed_id == prefix + stage.value_sha256(without_row_hash)


def test_direct_source_pairs_aggregate_direction_rows_and_partition_registry(
    tmp_path: Path,
) -> None:
    result = _build(_case(tmp_path))
    assert [(row["trait_id"], row["protein_id"]) for row in result.candidates] == [
        ("RHEA:10000", "UniProtKB:P12345"),
        ("RHEA:20000", "UniProtKB:Q9Y261"),
    ]
    first, second = result.candidates
    assert first["source_association_count"] == 2
    assert [row["direction"] for row in first["source_associations"]] == ["UN", "LR"]
    assert first["protein_reference_binding"]["status"] == (
        "EXACT_LOCAL_REFERENCE_PRESENT_WITHOUT_FETCH_RECEIPT_BINDING"
    )
    assert second["source_association_count"] == 1
    assert second["source_associations"][0]["direction"] == "RL"
    assert second["protein_reference_binding"]["status"] == "MISSING_EXACT_PROTEIN_REFERENCE"
    assert len(result.protein_requests) == 1
    assert result.protein_requests[0]["protein_id"] == "UniProtKB:Q9Y261"
    assert result.protein_requests[0]["rhea_trait_ids"] == ["RHEA:20000"]


def test_candidates_are_direct_whole_protein_but_never_qualified(tmp_path: Path) -> None:
    result = _build(_case(tmp_path))
    for row in result.candidates:
        assert row["qualification_status"] == "CANDIDATE_ONLY"
        assert row["qualification_claimed"] is False
        assert row["grounding_evidence_emitted"] is False
        assert row["mapping_method"] == "SOURCE_MEMBERSHIP"
        assert row["membership_basis"] == stage.MEMBERSHIP_BASIS
        assert row["scope"] == "WHOLE_PROTEIN"
        assert row["provider_kind"] == "SOURCE_DATABASE"
        assert row["provider_name"] == "Rhea"
        assert row["provider_release_binding_status"] == (
            "COLOCATED_RELEASE_PROPERTY_CONTENT_BOUND_WITHOUT_ACQUISITION_RECEIPT"
        )
        assert row["source_trait_id"] == row["trait_id"]
        assert "intervals" not in row
        assert "coordinate_frame" not in row
        assert set(stage.GLOBAL_PROMOTION_BLOCKERS) <= set(row["promotion_blockers"])
        assert stage.MISSING_SOURCE_RECEIPT_VERIFIER in row["promotion_blockers"]
        assert "MISSING_RHEA_SOURCE_DATABASE_VALIDATOR_CONTRACT" not in row["promotion_blockers"]
        assert "EC" not in row["membership_basis"]
    assert stage.MISSING_PROTEIN_REFERENCE not in result.candidates[0]["promotion_blockers"]
    assert stage.MISSING_PROTEIN_REFERENCE in result.candidates[1]["promotion_blockers"]


def test_summary_is_exact_content_addressed_and_render_is_deterministic(tmp_path: Path) -> None:
    case = _case(tmp_path)
    before = sorted(str(path.relative_to(case["repo"])) for path in case["repo"].rglob("*"))
    first = _build(case)
    second = _build(case)
    after = sorted(str(path.relative_to(case["repo"])) for path in case["repo"].rglob("*"))
    assert before == after
    assert stage.render_stage(first) == stage.render_stage(second)
    decoded = [json.loads(line) for line in stage.render_stage(first).splitlines()]
    assert decoded == [*first.candidates, *first.protein_requests, first.summary]
    assert (
        stage.render_stage(first, summary_only=True) == stage.canonical_json(first.summary) + "\n"
    )
    for row in first.candidates:
        _assert_content_address(
            row,
            id_field="candidate_id",
            prefix="rhea-uniprot-source-membership-candidate:",
            row_hash_field="candidate_row_sha256",
        )
    for row in first.protein_requests:
        _assert_content_address(
            row,
            id_field="request_id",
            prefix="rhea-uniprot-protein-request:",
            row_hash_field="request_row_sha256",
        )
    _assert_content_address(
        first.summary,
        id_field="stage_id",
        prefix="rhea-uniprot-source-native-stage:",
        row_hash_field="summary_row_sha256",
    )
    summary = first.summary
    assert summary["source_mapping_physical_row_count"] == 3
    assert summary["source_unique_trait_protein_pair_count"] == 2
    assert summary["candidate_count"] == 2
    assert summary["grounding_evidence_emitted_count"] == 0
    assert summary["ec_bridge_policy"] == "EC_ONLY_ASSOCIATIONS_ARE_CATEGORICALLY_EXCLUDED"
    assert summary["provider_source_contract_status"] == (
        "DIRECT_TSV_STRUCTURAL_CONTRACT_DEFINED_BUT_ACQUISITION_RECEIPT_AND_VERIFIER_ABSENT"
    )
    assert summary["network_action_performed"] is False
    assert summary["write_action_performed"] is False


def test_traits_with_existing_examples_are_out_of_missing_protein_scope(tmp_path: Path) -> None:
    case = _case(tmp_path)
    _write(case["trait_10000"], _trait_text("RHEA:10000", "A + B = C", examples=True))
    result = _build(case)
    assert [(row["trait_id"], row["protein_id"]) for row in result.candidates] == [
        ("RHEA:20000", "UniProtKB:Q9Y261")
    ]
    assert result.summary["excluded_existing_example_pair_count"] == 1


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (
            lambda case: _write(
                case["paths"]["mapping"],
                stage.MAPPING_HEADER + "\n10002\tLR\t10000\tP12345\n",
            ),
            "direction/master mismatch",
        ),
        (
            lambda case: _write(
                case["paths"]["mapping"],
                stage.MAPPING_HEADER + "\n10000\tUN\t10000\tP12345\n10000\tUN\t10000\tP12345\n",
            ),
            "duplicate Rhea mapping row",
        ),
        (
            lambda case: _write(
                case["paths"]["mapping"],
                stage.MAPPING_HEADER + "\n10000\tUN\t10000\tP12345-2\n",
            ),
            "invalid Rhea mapping fields",
        ),
        (
            lambda case: _write(
                case["paths"]["release_properties"],
                "rhea.release.number=998\nrhea.release.date=2026-01-01\n",
            ),
            "Rhea release mismatch",
        ),
        (
            lambda case: _write(case["paths"]["tsv_readme"], "RHEA_ID:\n"),
            "lacks required contract text",
        ),
        (
            lambda case: _write(case["paths"]["license"], "not an open license\n"),
            "does not declare CC BY 4.0",
        ),
    ],
)
def test_source_contract_failures_are_closed(
    tmp_path: Path, mutate: Callable[[dict[str, Any]], None], message: str
) -> None:
    case = _case(tmp_path)
    mutate(case)
    with pytest.raises(stage.RheaStageError, match=message):
        _build(case)


def test_direction_and_reaction_master_sets_must_agree(tmp_path: Path) -> None:
    case = _case(tmp_path)
    _write(
        case["paths"]["directions"],
        stage.DIRECTIONS_HEADER + "\n10000\t10001\t10002\t10003\n",
    )
    with pytest.raises(stage.RheaStageError, match="master sets disagree"):
        _build(case)


def test_trait_contract_shadow_duplicate_and_missing_trait_fail_closed(tmp_path: Path) -> None:
    drift = _case(tmp_path / "drift")
    text = (
        drift["trait_10000"]
        .read_text(encoding="utf-8")
        .replace("trait_category: FUNC_ENZYMATIC_ACTIVITY", "trait_category: FUNC_PATHWAY")
    )
    _write(drift["trait_10000"], text)
    with pytest.raises(stage.RheaStageError, match="trait_category.*drifted"):
        _build(drift)

    shadow = _case(tmp_path / "shadow")
    _write(
        shadow["traits_root"] / "other" / "shadow.yaml",
        _trait_text("RHEA:10000", "A + B = C"),
    )
    with pytest.raises(stage.RheaStageError, match="semantic shadow"):
        _build(shadow)

    missing = _case(tmp_path / "missing")
    missing["trait_20000"].unlink()
    with pytest.raises(stage.RheaStageError, match="reaction/trait sets disagree"):
        _build(missing)


@pytest.mark.parametrize(
    ("filename", "identifier_line", "ignored"),
    [
        (".quoted.yml", 'identifier: "RHEA:10000"', False),
        ("escaped.yaml", r'identifier: "RHEA\u003A10000"', False),
        ("folded.yaml", "identifier: >-\n  RHEA:10000", False),
        ("ignored.yaml", "identifier: 'RHEA:10000'", True),
    ],
)
def test_noncanonical_and_ignored_rhea_semantic_shadows_fail_closed(
    tmp_path: Path, filename: str, identifier_line: str, ignored: bool
) -> None:
    case = _case(tmp_path)
    shadow = case["traits_root"] / "other" / filename
    text = _trait_text("RHEA:10000", "A + B = C").replace("identifier: RHEA:10000", identifier_line)
    _write(shadow, text)
    if ignored:
        _write(case["repo"] / ".ignore", "data/traits/other/ignored.yaml\n")
    with pytest.raises(stage.RheaStageError, match="semantic shadow"):
        _build(case)


def test_utf16_rhea_semantic_shadow_fails_closed(tmp_path: Path) -> None:
    case = _case(tmp_path)
    shadow = case["traits_root"] / "other" / "utf16.yaml"
    shadow.parent.mkdir(parents=True, exist_ok=True)
    shadow.write_bytes(_trait_text("RHEA:10000", "A + B = C").encode("utf-16"))
    with pytest.raises(stage.RheaStageError, match="semantic shadow"):
        _build(case)


def test_exact_rhea_route_rejects_non_rhea_files(tmp_path: Path) -> None:
    case = _case(tmp_path)
    _write(case["traits"] / "not-rhea.yaml", "identifier: GO:0000001\n")
    with pytest.raises(stage.RheaStageError, match="lacks an exact RHEA identifier"):
        _build(case)


def test_duplicate_yaml_key_and_trait_symlink_are_rejected(tmp_path: Path) -> None:
    duplicate = _case(tmp_path / "duplicate")
    with duplicate["trait_10000"].open("a", encoding="utf-8") as stream:
        stream.write("label: duplicate\n")
    with pytest.raises(stage.RheaStageError, match="duplicate YAML key"):
        _build(duplicate)

    symlink = _case(tmp_path / "symlink")
    original = symlink["trait_10000"].with_suffix(".original")
    symlink["trait_10000"].rename(original)
    symlink["trait_10000"].symlink_to(original)
    with pytest.raises(stage.RheaStageError, match="trait tree contains a symlink"):
        _build(symlink)


def test_registry_requires_canonical_rows_release_and_sequence_binding(tmp_path: Path) -> None:
    noncanonical = _case(tmp_path / "noncanonical")
    row = _reference()
    noncanonical["registry"].write_text(json.dumps(row) + "\n", encoding="utf-8")
    with pytest.raises(stage.RheaStageError, match="noncanonical ProteinReference"):
        _build(noncanonical)

    release = _case(tmp_path / "release")
    row = _reference()
    row["uniprot_release"] = "2026_03"
    release["registry"].write_text(stage.canonical_json(row) + "\n", encoding="utf-8")
    with pytest.raises(stage.RheaStageError, match="release mismatch"):
        _build(release)

    digest = _case(tmp_path / "digest")
    row = _reference()
    row["sequence_sha256"] = "0" * 64
    digest["registry"].write_text(stage.canonical_json(row) + "\n", encoding="utf-8")
    with pytest.raises(stage.RheaStageError, match="sequence digest mismatch"):
        _build(digest)


def test_source_symlink_hardlink_and_post_capture_mutation_are_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    symlink = _case(tmp_path / "symlink")
    mapping = symlink["paths"]["mapping"]
    original = mapping.with_suffix(".original")
    mapping.rename(original)
    mapping.symlink_to(original)
    with pytest.raises(stage.RheaStageError, match="traverses a symlink"):
        _build(symlink)

    hardlink = _case(tmp_path / "hardlink")
    os.link(hardlink["paths"]["mapping"], hardlink["raw"] / "mapping-alias.tsv")
    with pytest.raises(stage.RheaStageError, match="exactly one hard link"):
        _build(hardlink)

    changed = _case(tmp_path / "changed")
    real_assert = stage._assert_unchanged
    mutated = False

    def mutate_then_assert(
        artifact: stage.CapturedArtifact, *, repo_root: Path, description: str
    ) -> None:
        nonlocal mutated
        if not mutated and description == "Rhea mapping artifact":
            mutated = True
            changed["paths"]["mapping"].write_bytes(
                changed["paths"]["mapping"].read_bytes() + b"\n"
            )
        real_assert(artifact, repo_root=repo_root, description=description)

    monkeypatch.setattr(stage, "_assert_unchanged", mutate_then_assert)
    with pytest.raises(stage.RheaStageError, match="SHA-256 mismatch|changed after capture"):
        _build(changed)


def test_trait_identity_candidate_mutation_before_final_replay_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    case = _case(tmp_path)
    candidate = case["traits_root"] / "other" / "rhea-xref.yaml"
    _write(candidate, "identifier: GO:0000001\nxrefs:\n  - RHEA:10000\n")
    real_assert = stage._assert_unchanged
    mutated = False

    def mutate_then_assert(
        artifact: stage.CapturedArtifact, *, repo_root: Path, description: str
    ) -> None:
        nonlocal mutated
        if (
            not mutated
            and description == "Rhea trait identity candidate"
            and artifact.path == candidate
        ):
            mutated = True
            candidate.write_bytes(candidate.read_bytes() + b"\n")
        real_assert(artifact, repo_root=repo_root, description=description)

    monkeypatch.setattr(stage, "_assert_unchanged", mutate_then_assert)
    with pytest.raises(stage.RheaStageError, match="SHA-256 mismatch|changed after capture"):
        _build(case)


def test_expected_hash_pin_is_enforced(tmp_path: Path) -> None:
    case = _case(tmp_path)
    paths = case["paths"]
    pins = {role: None for role in paths}
    pins["mapping"] = "0" * 64
    with pytest.raises(stage.RheaStageError, match="SHA-256 mismatch"):
        stage.build_stage(
            mapping_path=paths["mapping"],
            release_properties_path=paths["release_properties"],
            tsv_readme_path=paths["tsv_readme"],
            license_path=paths["license"],
            directions_path=paths["directions"],
            reactions_path=paths["reactions"],
            traits_root=case["traits_root"],
            traits_dir=case["traits"],
            protein_registry_path=case["registry"],
            repo_root=case["repo"],
            expected_source_sha256=pins,
            expected_rhea_release="999",
            expected_rhea_release_date="2026-01-01",
        )


def test_acquisition_plan_is_canonical_no_network_and_content_addressed() -> None:
    plan = stage.acquisition_plan()
    _assert_content_address(
        plan,
        id_field="plan_id",
        prefix="rhea-uniprot-source-acquisition-plan:",
        row_hash_field="plan_row_sha256",
    )
    assert plan["expected_provider_release"] == "141"
    assert plan["expected_provider_release_date"] == "2026-06-10"
    assert plan["network_action_performed"] is False
    assert plan["write_action_performed"] is False
    assert plan["apply_authorized"] is False
    assert {row["role"] for row in plan["artifacts"]} == set(stage.CURRENT_SOURCE_SHA256)
    assert any("rhea2uniprot_sprot.tsv" in row["url"] for row in plan["artifacts"])
    assert plan["forbidden_substitutions"] == [
        "EXPASY_ENZYME_EC_DR_LINES",
        "RHEA2EC_BRIDGE",
        "UNRECEIPTED_SYNTHETIC_MAPPING",
        "PARTIAL_MAPPING_EXPORT",
    ]


def test_cli_has_no_apply_output_or_network_mode(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit):
        stage.parse_args(["--apply"])
    with pytest.raises(SystemExit):
        stage.parse_args(["--out", "result.jsonl"])
    assert stage.main(["--acquisition-plan"]) == 0
    output = capsys.readouterr().out
    assert output == stage.canonical_json(stage.acquisition_plan()) + "\n"
    assert stage.main(["--acquisition-plan", "--summary-only"]) == 2
    assert "cannot be combined" in capsys.readouterr().err


def test_production_stage_is_artifact_conditional_and_never_synthesizes_inputs() -> None:
    required = (
        stage.DEFAULT_MAPPING,
        stage.DEFAULT_RELEASE_PROPERTIES,
        stage.DEFAULT_TSV_README,
        stage.DEFAULT_LICENSE,
    )
    if not all(path.exists() for path in required):
        assert not any(path.exists() for path in required)
        assert stage.main(["--summary-only"]) == 2
        return
    result = stage.build_stage()
    assert result.summary["qualification_claimed"] is False
    assert result.summary["grounding_evidence_emitted_count"] == 0


def test_production_reaction_direction_and_trait_sets_replay_with_synthetic_pair(
    tmp_path: Path,
) -> None:
    """Exercise real release-141 catalogues without pretending the mapping was fetched."""
    required = (
        stage.DEFAULT_DIRECTIONS,
        stage.DEFAULT_REACTIONS,
        stage.DEFAULT_TRAITS_ROOT,
        stage.DEFAULT_PROTEIN_REGISTRY,
    )
    if not all(path.exists() for path in required):
        pytest.skip("ignored production Rhea/grounding artifacts are not installed")
    raw = tmp_path / "synthetic-rhea-inputs"
    mapping = raw / "rhea2uniprot_sprot.tsv"
    properties = raw / "rhea-release.properties"
    readme = raw / "rhea-tsv-README.txt"
    license_path = raw / "LICENSE.txt"
    _write(mapping, stage.MAPPING_HEADER + "\n10000\tUN\t10000\tP12345\n")
    _write(
        properties,
        "rhea.release.number=141\nrhea.release.date=2026-06-10\n",
    )
    _write(
        readme,
        "Files named rhea2<db>.tsv contain cross-references to other databases\n"
        "RHEA_ID: reaction\nDIRECTION: direction\nMASTER_ID: master\nID: record\n",
    )
    _write(
        license_path,
        "Creative Commons Attribution 4.0 International\n"
        "All files in the Rhea FTP directory may be copied and redistributed freely\n",
    )
    result = stage.build_stage(
        mapping_path=mapping,
        release_properties_path=properties,
        tsv_readme_path=readme,
        license_path=license_path,
        directions_path=stage.DEFAULT_DIRECTIONS,
        reactions_path=stage.DEFAULT_REACTIONS,
        traits_root=stage.DEFAULT_TRAITS_ROOT,
        traits_dir=stage.DEFAULT_TRAITS_DIR,
        protein_registry_path=stage.DEFAULT_PROTEIN_REGISTRY,
        # The temporary and workspace inputs only share a filesystem ancestor at
        # slash.  This test remains read-only outside pytest's temporary files.
        repo_root=Path("/"),
        expected_source_sha256={
            "mapping": None,
            "release_properties": None,
            "tsv_readme": None,
            "license": None,
            "directions": stage.CURRENT_SOURCE_SHA256["directions"],
            "reactions": stage.CURRENT_SOURCE_SHA256["reactions"],
        },
    )
    assert result.summary["rhea_reaction_count"] == 18_558
    assert result.summary["rhea_trait_count"] == 18_558
    assert result.summary["source_mapping_physical_row_count"] == 1
    assert [(row["trait_id"], row["protein_id"]) for row in result.candidates] == [
        ("RHEA:10000", "UniProtKB:P12345")
    ]
    assert result.summary["qualification_claimed"] is False
