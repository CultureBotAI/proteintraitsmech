"""Focused safety tests for ComplexPortal's staging-only component claims."""

from __future__ import annotations

import hashlib
import importlib
import json
import sys
from pathlib import Path
from typing import Any

import pytest

REPO = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(REPO / "scripts"))
stage = importlib.import_module("stage_complexportal_grounding_candidates")

SOURCE_SNAPSHOT_ID = (
    "complexportal-source-snapshot:a2bed4f99a9cd86074213668597e0eceffef228df8f757c24f00db4e32542541"
)
CANDIDATE_ROWS_SHA256 = "adae937c316379ae88d9e6445afcbfed81f5d051646e507b4e822bc676e89c62"
BLOCKED_ROWS_SHA256 = "2e4e65dab51d843028e6bdf4aa0896e6d6b49ad5f6005209c2be630f42906669"
REQUEST_ROWS_SHA256 = "8228f6f22b2552041f25a2c95e374084c2b2614f3c2664c67ff80c0e70e628b0"
COMBINED_ROWS_SHA256 = "3132f42a7518706f43518025b613a7e0ad59db10344be70bf2c4d527c3583d36"
TRAIT_BINDING_ROWS_SHA256 = "1db5b4990d5422d6a9d73a07d1e03441567e1d4457e9d22208f686220bd0e5ef"
SOURCE_TRAIT_BINDING_ROWS_SHA256 = (
    "656c395cb232d63604e6d762c08703568d6ea1c72e7d48f3543089baa2b3a062"
)
STAGE_ID = (
    "complexportal-grounding-stage:d8d543ce0da5925d978b2a6129745e76053d8dd535a177f6b46f47542328e936"
)
SUMMARY_ROW_SHA256 = "e6446834bc2485e2bf56c62802c93133758aeb968b888b4490776a7a0748fce0"
FULL_STREAM_SHA256 = "ebf9e64258ef0ce5e8350792e997410f8e1d510c39bddcd10bff2e5aa027ac4f"
FULL_STREAM_LINE_COUNT = 31_492


def _source_row(
    accession: str,
    direct_members: str,
    *,
    expanded_members: str | None = None,
    name: str,
    taxon: str,
    description: str = "Curated fixture complex.",
) -> list[str]:
    return [
        accession,
        name,
        f"{name} alias",
        taxon,
        direct_members,
        stage.EXACT_ECO_FIELDS["ECO:0000353"],
        "intact:EBI-1",
        "GO:0032991(protein-containing complex)",
        f"complex portal:{accession}(complex-primary)",
        description,
        "Heteromer",
        "-",
        "-",
        "-",
        "-",
        "-",
        "-",
        'psi-mi:"MI:0469"(IntAct)',
        expanded_members if expanded_members is not None else direct_members,
    ]


def _write_source(path: Path, rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        stage.EXPECTED_HEADER + "\n" + "".join("\t".join(row) + "\n" for row in rows),
        encoding="utf-8",
    )


def _write_trait(path: Path, accession: str, label: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"identifier: ComplexPortal:{accession}\n"
        f'label: "{label}"\n'
        "definition: A fixture complex.\n"
        "definition_source: Complex Portal\n"
        "trait_axis: FUNCTION\n"
        "trait_category: FUNC_INTERACTION_PARTNER\n"
        "term_kind: CLASS\n"
        "mapping_status: SEEDED\n"
        "license: CC0 (EBI Complex Portal)\n",
        encoding="utf-8",
    )


def _write_source_derived_trait(traits: Path, row: list[str]) -> Path:
    projection = stage.canonical_source_projection(row)
    path, raw = stage._expected_trait_artifact(projection, traits_dir=traits)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    return path


def _protein_reference(
    protein_id: str, *, taxon_id: str, taxon_label: str = "Fixture organism"
) -> dict[str, Any]:
    sequence = "ACDEFGHIK"
    return {
        "protein_id": protein_id,
        "protein_label": f"Fixture {protein_id}",
        "reviewed": True,
        "sequence": sequence,
        "sequence_length": len(sequence),
        "sequence_sha256": hashlib.sha256(sequence.encode("ascii")).hexdigest(),
        "sequence_version": 1,
        "taxon_id": taxon_id,
        "taxon_label": taxon_label,
        "uniprot_release": stage.EXPECTED_UNIPROT_RELEASE,
    }


def _write_registry(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "".join(
            stage.canonical_json(row) + "\n"
            for row in sorted(rows, key=lambda row: row["protein_id"])
        ),
        encoding="utf-8",
    )


def _case(tmp_path: Path) -> dict[str, Any]:
    repo = tmp_path / "repo"
    raw = repo / "data" / "raw" / "complexportal"
    traits = repo / "data" / "traits" / "function" / "interaction_partner" / "complexportal"
    # Column 5 is the direct list. CPX-30 and its chemical are not candidates;
    # column 19 supplies the expanded UniProt components used for membership.
    row_20 = _source_row(
        "CPX-20",
        "P12345(1)|CPX-30(1)|CHEBI:1(1)",
        expanded_members="P12345(1)|Q9Y261-2(0)",
        name="Fixture twenty",
        taxon="10090",
    )
    row_10 = _source_row(
        "CPX-10",
        "A0A123B456(1)",
        name="Fixture ten",
        taxon="9606",
        description="Second source row.",
    )
    _write_source(raw / "10090.tsv", [row_20])
    _write_source(raw / "9606.tsv", [row_10])
    # Categorical exclusion means this file is never parsed or hashed.
    (raw / stage.EXCLUDED_PREDICTED_NAME).write_bytes(b"not ComplexTAB\xff")
    trait_10 = _write_source_derived_trait(traits, row_10)
    trait_20 = _write_source_derived_trait(traits, row_20)
    _write_trait(traits / "predicted-only.yaml", "CPX-999", "Predicted-only fixture")
    registry = repo / "data" / "grounding" / "protein_registry.jsonl"
    registry.parent.mkdir(parents=True, exist_ok=True)
    registry.write_bytes(b"")
    return {
        "repo": repo,
        "raw": raw,
        "traits": traits,
        "traits_root": repo / "data" / "traits",
        "registry": registry,
        "row_20": row_20,
        "row_10": row_10,
        "trait_10": trait_10,
        "trait_20": trait_20,
    }


def _build(case: dict[str, Any]) -> stage.StageResult:
    return stage.build_stage(
        raw_dir=case["raw"],
        traits_root=case["traits_root"],
        traits_dir=case["traits"],
        protein_registry_path=case["registry"],
        repo_root=case["repo"],
        expected_source_files=("10090.tsv", "9606.tsv"),
        expected_source_sha256=None,
    )


def _assert_content_address(
    row: dict[str, Any], *, id_field: str, prefix: str, row_hash_field: str
) -> None:
    without_row_hash = dict(row)
    observed_row_hash = without_row_hash.pop(row_hash_field)
    assert observed_row_hash == stage.value_sha256(without_row_hash)
    observed_id = without_row_hash.pop(id_field)
    assert observed_id == prefix + stage.value_sha256(without_row_hash)


def test_expanded_membership_candidates_and_direct_provenance(tmp_path: Path) -> None:
    case = _case(tmp_path)
    result = _build(case)
    pairs = {(row["trait_id"], row["protein_id"]) for row in result.candidates}
    assert pairs == {
        ("ComplexPortal:CPX-10", "UniProtKB:A0A123B456"),
        ("ComplexPortal:CPX-20", "UniProtKB:P12345"),
        ("ComplexPortal:CPX-20", "UniProtKB:Q9Y261-2"),
    }
    assert result.blocked_tokens == ()
    assert all(row["qualification_status"] == "CANDIDATE_PROTEIN" for row in result.candidates)
    assert all(row["staging_reason"] == stage.STAGING_REASON for row in result.candidates)
    assert all(row["mapping_method"] == "SOURCE_MEMBERSHIP" for row in result.candidates)
    assert all(row["scope"] == "WHOLE_PROTEIN" for row in result.candidates)
    assert all(row["provider_kind"] == "SOURCE_DATABASE" for row in result.candidates)
    assert all(row["provider_name"] == "ComplexPortal" for row in result.candidates)
    assert all(row["eco_code"] == "ECO:0000353" for row in result.candidates)
    assert all(row["grounding_evidence_emitted"] is False for row in result.candidates)
    assert all(
        row["protein_reference_binding"]["status"] == "MISSING_EXACT_PROTEIN_REFERENCE"
        for row in result.candidates
    )
    assert all(
        row["provider_source"].startswith("data/raw/complexportal/") for row in result.candidates
    )
    assert all(row["source_artifact_path"] == row["provider_source"] for row in result.candidates)
    assert all(row["record_path"].startswith("data/traits/") for row in result.candidates)

    direct = next(row for row in result.candidates if row["protein_id"] == "UniProtKB:P12345")
    expanded = next(row for row in result.candidates if row["protein_id"] == "UniProtKB:Q9Y261-2")
    assert direct["source_member_provenance"]["present_in_direct_participant_list"] is True
    assert expanded["source_member_provenance"]["present_in_direct_participant_list"] is False
    assert expanded["source_member_stoichiometry"] is None
    assert expanded["source_member_stoichiometry_known"] is False
    assert direct["source_member_stoichiometry"] == 1
    assert direct["source_member_stoichiometry_known"] is True
    for row in result.candidates:
        assert row["source_row_sha256"] == stage.value_sha256(row["source_row_projection"])
        _assert_content_address(
            row,
            id_field="candidate_id",
            prefix="complexportal-grounding-candidate:",
            row_hash_field="candidate_row_sha256",
        )

    summary = result.summary
    assert summary["qualification_claimed"] is False
    assert summary["excluded_source_files"] == [stage.EXCLUDED_PREDICTED_NAME]
    assert summary["source_file_count"] == 2
    assert summary["source_complex_count"] == 2
    assert summary["covered_source_complex_count"] == 2
    assert summary["uncovered_source_complex_count"] == 0
    assert summary["uncovered_source_complex_ids"] == []
    assert summary["direct_member_token_count"] == 4
    assert summary["expanded_member_token_count"] == 3
    assert summary["candidate_count"] == 3
    assert summary["blocked_token_count"] == 0
    assert summary["missing_protein_reference_request_count"] == 3
    assert len(result.protein_requests) == 3
    assert summary["grounding_evidence_emitted_count"] == 0
    assert summary["unknown_stoichiometry_candidate_count"] == 1
    assert summary["trait_records_outside_curated_snapshot"] == 1


def test_blocked_expanded_tokens_are_bound_and_content_addressed(tmp_path: Path) -> None:
    case = _case(tmp_path)
    blocked_row = _source_row(
        "CPX-20",
        "CPX-30(1)",
        expanded_members=("O12345-PRO_0000000001(0)|[Q11111,Q22222](1)|EBI-42(1)|M14387(1)"),
        name="Fixture twenty",
        taxon="10090",
    )
    _write_source(case["raw"] / "10090.tsv", [blocked_row])
    _write_source_derived_trait(case["traits"], blocked_row)
    result = _build(case)
    assert len(result.blocked_tokens) == 4
    assert {row["source_member_class"] for row in result.blocked_tokens} == {
        "BLOCKED_PROCESSED_CHAIN",
        "BLOCKED_COMPOSITE_TOKEN",
        "BLOCKED_INTERNAL_INTERACTOR",
        "BLOCKED_INVALID_OR_UNSUPPORTED_ACCESSION",
    }
    assert {row["trait_id"] for row in result.blocked_tokens} == {"ComplexPortal:CPX-20"}
    assert all(row["provider_source"].endswith("10090.tsv") for row in result.blocked_tokens)
    assert all(row["record_sha256"] for row in result.blocked_tokens)
    for row in result.blocked_tokens:
        assert row["blocking_reasons"] == [row["source_member_class"]]
        assert row["source_row_sha256"] == stage.value_sha256(row["source_row_projection"])
        _assert_content_address(
            row,
            id_field="blocked_token_id",
            prefix="complexportal-grounding-blocked-token:",
            row_hash_field="blocked_token_row_sha256",
        )
    chain = next(
        row
        for row in result.blocked_tokens
        if row["source_member_class"] == "BLOCKED_PROCESSED_CHAIN"
    )
    assert chain["source_member_stoichiometry"] is None
    assert chain["source_member_stoichiometry_known"] is False
    assert result.summary["covered_source_complex_count"] == 1
    assert result.summary["uncovered_source_complex_ids"] == ["CPX-20"]
    assert result.summary["blocked_token_count"] == 4


def test_inexact_eco_field_blocks_otherwise_valid_member(tmp_path: Path) -> None:
    case = _case(tmp_path)
    bad_eco = list(case["row_10"])
    bad_eco[5] = "ECO:0005546(physical interaction evidence used in manual assertion)"
    _write_source(case["raw"] / "9606.tsv", [bad_eco])
    result = _build(case)
    assert all(row["trait_id"] != "ComplexPortal:CPX-10" for row in result.candidates)
    blocked = next(
        row for row in result.blocked_tokens if row["trait_id"] == "ComplexPortal:CPX-10"
    )
    assert blocked["eco_code"] == "ECO:0005546"
    assert blocked["source_member_class"] == "ACCEPTED_UNIPROT"
    assert blocked["blocking_reasons"] == ["EXACT_ECO_CODE_LABEL_MISMATCH"]
    assert result.summary["uncovered_source_complex_ids"] == ["CPX-10"]


def test_deterministic_canonical_output(tmp_path: Path) -> None:
    case = _case(tmp_path)
    first = _build(case)
    second = _build(case)
    assert stage.render_stage(first) == stage.render_stage(second)
    assert stage.render_stage(first, summary_only=True) == stage.render_stage(
        second, summary_only=True
    )
    decoded = [json.loads(line) for line in stage.render_stage(first).splitlines()]
    assert decoded[: len(first.candidates)] == list(first.candidates)
    blocked_start = len(first.candidates)
    request_start = blocked_start + len(first.blocked_tokens)
    assert decoded[blocked_start:request_start] == list(first.blocked_tokens)
    assert decoded[request_start:-1] == list(first.protein_requests)
    assert decoded[-1] == first.summary
    candidate_bytes = "".join(stage.canonical_json(row) + "\n" for row in first.candidates).encode()
    blocked_bytes = "".join(
        stage.canonical_json(row) + "\n" for row in first.blocked_tokens
    ).encode()
    assert first.summary["candidate_rows_sha256"] == hashlib.sha256(candidate_bytes).hexdigest()
    assert first.summary["blocked_token_rows_sha256"] == hashlib.sha256(blocked_bytes).hexdigest()
    for row in first.protein_requests:
        _assert_content_address(
            row,
            id_field="request_id",
            prefix="complexportal-protein-request:",
            row_hash_field="request_row_sha256",
        )
    _assert_content_address(
        first.summary,
        id_field="stage_id",
        prefix="complexportal-grounding-stage:",
        row_hash_field="summary_row_sha256",
    )
    parser_dests = {action.dest for action in stage._parser()._actions}
    assert "apply" not in parser_dests
    assert "output" not in parser_dests


def test_duplicate_source_rows_and_expanded_members_are_refused(tmp_path: Path) -> None:
    case = _case(tmp_path)
    source = case["raw"] / "10090.tsv"
    row = case["row_20"]
    _write_source(source, [row, row])
    with pytest.raises(stage.ComplexPortalStageError, match="duplicate curated ComplexPortal row"):
        _build(case)

    duplicate_member_row = _source_row(
        "CPX-20",
        "P12345(1)",
        expanded_members="P12345(1)|P12345(2)",
        name="Fixture twenty",
        taxon="10090",
    )
    _write_source(source, [duplicate_member_row])
    _write_source_derived_trait(case["traits"], duplicate_member_row)
    with pytest.raises(stage.ComplexPortalStageError, match="duplicate expanded participant"):
        _build(case)


def test_filename_taxonomy_and_trait_contract_are_exact(tmp_path: Path) -> None:
    case = _case(tmp_path)
    wrong_taxon = list(case["row_20"])
    wrong_taxon[3] = "9606"
    _write_source(case["raw"] / "10090.tsv", [wrong_taxon])
    with pytest.raises(stage.ComplexPortalStageError, match="does not exactly match"):
        _build(case)

    _write_source(case["raw"] / "10090.tsv", [case["row_20"]])
    trait_path = case["trait_20"]
    trait_path.write_text(
        trait_path.read_text(encoding="utf-8").replace(
            "trait_category: FUNC_INTERACTION_PARTNER",
            "trait_category: FUNC_PROTEIN_FAMILY",
        ),
        encoding="utf-8",
    )
    with pytest.raises(stage.ComplexPortalStageError, match="trait contract mismatch"):
        _build(case)


def test_final_drift_check_closes_source_hash_parse_gap(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    case = _case(tmp_path)
    original_projection = stage.canonical_source_projection
    mutated = False

    def mutate_after_projection(columns: list[str] | tuple[str, ...]) -> dict[str, str]:
        nonlocal mutated
        projection = original_projection(columns)
        if not mutated:
            mutated = True
            changed = list(case["row_20"])
            changed[9] = "Changed after the source byte image was parsed."
            _write_source(case["raw"] / "10090.tsv", [changed])
        return projection

    monkeypatch.setattr(stage, "canonical_source_projection", mutate_after_projection)
    with pytest.raises(stage.ComplexPortalStageError, match="drifted while staging"):
        _build(case)


def test_source_tamper_changes_every_bound_digest(tmp_path: Path) -> None:
    case = _case(tmp_path)
    before = _build(case)
    before_row = next(row for row in before.candidates if row["protein_id"] == "UniProtKB:P12345")

    changed_row = list(case["row_20"])
    changed_row[9] = "Tampered description."
    _write_source(case["raw"] / "10090.tsv", [changed_row])
    _write_source_derived_trait(case["traits"], changed_row)
    after = _build(case)
    after_row = next(row for row in after.candidates if row["protein_id"] == "UniProtKB:P12345")

    assert before_row["source_row_projection"] != after_row["source_row_projection"]
    assert before_row["source_row_sha256"] != after_row["source_row_sha256"]
    assert before_row["source_raw_line_sha256"] != after_row["source_raw_line_sha256"]
    assert before_row["source_raw_line_sha256_basis"] == (
        "RAW_UTF8_PHYSICAL_LINE_EXCLUDING_CANONICAL_LF_TERMINATOR"
    )
    assert before_row["provider_entry_sha256"] == before_row["source_raw_line_sha256"]
    assert before_row["source_artifact_sha256"] != after_row["source_artifact_sha256"]
    assert before_row["candidate_id"] != after_row["candidate_id"]
    assert before_row["candidate_row_sha256"] != after_row["candidate_row_sha256"]
    assert before.summary["candidate_rows_sha256"] != after.summary["candidate_rows_sha256"]
    assert before.summary["stage_id"] != after.summary["stage_id"]


def test_registry_partition_requests_and_taxon_comparison_are_explicit(tmp_path: Path) -> None:
    case = _case(tmp_path)
    _write_registry(
        case["registry"],
        [_protein_reference("UniProtKB:P12345", taxon_id="NCBITaxon:10090")],
    )
    result = _build(case)
    present = next(row for row in result.candidates if row["protein_id"] == "UniProtKB:P12345")
    assert present["protein_reference_binding"]["status"] == (
        "EXACT_LOCAL_PROTEIN_REFERENCE_PRESENT"
    )
    assert present["source_complex_to_protein_taxon_comparison"] == {
        "source_complex_taxon_id": "NCBITaxon:10090",
        "protein_reference_taxon_id": "NCBITaxon:10090",
        "status": "IDENTICAL",
        "acceptance_semantics": (
            "INFORMATIONAL_ONLY_COMPLEX_TAXON_IS_NOT_A_COMPONENT_PROTEIN_TAXON_ASSERTION"
        ),
    }
    assert stage.MISSING_PROTEIN_REFERENCE not in present["promotion_blockers"]
    assert result.summary["local_protein_reference_candidate_count"] == 1
    assert result.summary["local_protein_reference_unique_protein_count"] == 1
    assert result.summary["missing_protein_reference_candidate_count"] == 2
    assert result.summary["missing_protein_reference_request_count"] == 2
    assert {row["protein_id"] for row in result.protein_requests} == {
        "UniProtKB:A0A123B456",
        "UniProtKB:Q9Y261-2",
    }
    assert all(row["network_action_performed"] is False for row in result.protein_requests)
    assert all(row["write_action_performed"] is False for row in result.protein_requests)

    _write_registry(
        case["registry"],
        [_protein_reference("UniProtKB:P12345", taxon_id="NCBITaxon:9606")],
    )
    cross_taxon = _build(case)
    cross_taxon_row = next(
        row for row in cross_taxon.candidates if row["protein_id"] == "UniProtKB:P12345"
    )
    comparison = cross_taxon_row["source_complex_to_protein_taxon_comparison"]
    assert comparison["status"] == "DIFFERENT_HOST_OR_COMPONENT_TAXON"
    assert "INFORMATIONAL_ONLY" in comparison["acceptance_semantics"]
    assert stage.MISSING_PROTEIN_REFERENCE not in cross_taxon_row["promotion_blockers"]


def test_missing_reference_requests_deduplicate_and_aggregate_memberships(
    tmp_path: Path,
) -> None:
    case = _case(tmp_path)
    repeated = list(case["row_10"])
    repeated[18] = "A0A123B456(1)|P12345(1)"
    _write_source(case["raw"] / "9606.tsv", [repeated])
    result = _build(case)
    request = next(
        row for row in result.protein_requests if row["protein_id"] == "UniProtKB:P12345"
    )
    candidates = [row for row in result.candidates if row["protein_id"] == "UniProtKB:P12345"]
    assert request["trait_count"] == 2
    assert request["source_membership_count"] == 2
    assert request["complexportal_trait_ids"] == [
        "ComplexPortal:CPX-10",
        "ComplexPortal:CPX-20",
    ]
    assert request["source_candidate_ids"] == sorted(row["candidate_id"] for row in candidates)
    assert request["source_taxon_ids"] == ["NCBITaxon:10090", "NCBITaxon:9606"]
    assert request["source_artifact_paths"] == [
        "data/raw/complexportal/10090.tsv",
        "data/raw/complexportal/9606.tsv",
    ]
    assert sum(row["protein_id"] == "UniProtKB:P12345" for row in result.protein_requests) == 1


@pytest.mark.parametrize(
    "mutation",
    [
        lambda text: text.replace('label: "Fixture twenty"', 'label: "Forged label"'),
        lambda text: text.replace(
            "definition_source: Complex Portal",
            "canonical_examples: []\ndefinition_source: Complex Portal",
        ),
        lambda text: text.replace("license:", "note: forged field\nlicense:"),
    ],
)
def test_source_derived_trait_path_and_full_bytes_are_exact(tmp_path: Path, mutation) -> None:
    case = _case(tmp_path)
    path = case["trait_20"]
    path.write_text(mutation(path.read_text(encoding="utf-8")), encoding="utf-8")
    with pytest.raises(
        stage.ComplexPortalStageError,
        match="full trait bytes differ|trait route mismatch",
    ):
        _build(case)


def test_trait_duplicate_keys_escaped_shadow_and_route_inventory_fail_closed(
    tmp_path: Path,
) -> None:
    case = _case(tmp_path)
    predicted = case["traits"] / "predicted-only.yaml"
    predicted.write_text(
        predicted.read_text(encoding="utf-8") + "identifier: ComplexPortal:CPX-999\n",
        encoding="utf-8",
    )
    with pytest.raises(stage.ComplexPortalStageError, match="duplicate key"):
        _build(case)

    case = _case(tmp_path / "escaped")
    shadow = case["traits_root"] / "function" / "shadow.YML"
    shadow.parent.mkdir(parents=True, exist_ok=True)
    shadow.write_text('identifier: "\\x43omplexPortal:CPX-20"\nlabel: shadow\n', encoding="utf-8")
    with pytest.raises(stage.ComplexPortalStageError, match="semantic shadow"):
        _build(case)

    case = _case(tmp_path / "route")
    (case["traits"] / "README.txt").write_text("not a trait\n", encoding="utf-8")
    with pytest.raises(stage.ComplexPortalStageError, match="only flat regular lowercase"):
        _build(case)


def test_source_inventory_and_canonical_line_contract_are_exact(tmp_path: Path) -> None:
    case = _case(tmp_path)
    (case["raw"] / "extra.tsv").write_text("unexpected\n", encoding="utf-8")
    with pytest.raises(stage.ComplexPortalStageError, match="raw inventory differs"):
        _build(case)

    case = _case(tmp_path / "line")
    source = case["raw"] / "10090.tsv"
    source.write_bytes(source.read_bytes().replace(b"\n", b"\r\n"))
    with pytest.raises(stage.ComplexPortalStageError, match="canonical LF text"):
        _build(case)

    case = _case(tmp_path / "checksum")
    fixture_hashes = {
        name: hashlib.sha256((case["raw"] / name).read_bytes()).hexdigest()
        for name in ("10090.tsv", "9606.tsv")
    }
    fixture_hashes["10090.tsv"] = "0" * 64
    with pytest.raises(stage.ComplexPortalStageError, match="SHA-256 mismatch"):
        stage.build_stage(
            raw_dir=case["raw"],
            traits_root=case["traits_root"],
            traits_dir=case["traits"],
            protein_registry_path=case["registry"],
            repo_root=case["repo"],
            expected_source_files=("10090.tsv", "9606.tsv"),
            expected_source_sha256=fixture_hashes,
        )


def test_symlinks_and_swap_at_descriptor_open_are_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    case = _case(tmp_path)
    external = tmp_path / "external.yaml"
    external.write_bytes(case["trait_20"].read_bytes())
    original_read = stage._read_relative_bytes
    swapped = False

    def swap_then_read(*args, **kwargs):
        nonlocal swapped
        if (
            not swapped
            and kwargs.get("description") == "ComplexPortal trait candidate"
            and kwargs.get("display_path") == case["trait_20"]
        ):
            swapped = True
            case["trait_20"].rename(case["trait_20"].with_suffix(".saved"))
            case["trait_20"].symlink_to(external)
        return original_read(*args, **kwargs)

    monkeypatch.setattr(stage, "_read_relative_bytes", swap_then_read)
    with pytest.raises(stage.ComplexPortalStageError, match="without following symlinks"):
        _build(case)
    assert swapped is True


def test_trait_candidate_membership_and_irrelevant_digest_are_rechecked(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    case = _case(tmp_path)
    original_candidates = stage._candidate_trait_paths
    calls = 0

    def add_shadow_after_scan(*args, **kwargs):
        nonlocal calls
        paths = original_candidates(*args, **kwargs)
        calls += 1
        if calls == 1:
            shadow = case["traits_root"] / "late-shadow.yaml"
            shadow.write_text("identifier: ComplexPortal:CPX-20\n", encoding="utf-8")
        return paths

    monkeypatch.setattr(stage, "_candidate_trait_paths", add_shadow_after_scan)
    with pytest.raises(stage.ComplexPortalStageError, match="membership drifted"):
        _build(case)

    case = _case(tmp_path / "digest")
    conservative = case["traits_root"] / "conservative.yaml"
    conservative.write_text(
        'identifier: Pfam:PF00001\ndefinition: "contains \\\\ escape"\n',
        encoding="utf-8",
    )
    original_loader = stage._load_yaml_mapping
    mutated = False

    def mutate_irrelevant_after_parse(raw: bytes, *, path: Path):
        nonlocal mutated
        value = original_loader(raw, path=path)
        if path == conservative and not mutated:
            mutated = True
            conservative.write_text("identifier: ComplexPortal:CPX-20\n", encoding="utf-8")
        return value

    monkeypatch.setattr(stage, "_load_yaml_mapping", mutate_irrelevant_after_parse)
    with pytest.raises(stage.ComplexPortalStageError, match="drifted while staging"):
        _build(case)


def test_stage_candidate_cannot_bypass_central_complexportal_receipt_lock(
    tmp_path: Path,
) -> None:
    case = _case(tmp_path)
    candidate = _build(case).candidates[0]
    evidence = {
        "trait_id": candidate["trait_id"],
        "protein_id": candidate["protein_id"],
        "source_trait_id": candidate["source_trait_id"],
        "mapping_method": candidate["mapping_method"],
        "scope": candidate["scope"],
        "evidence_source": candidate["evidence_source"],
        "source_release": candidate["source_snapshot_id"],
        "sequence_sha256": "0" * 64,
        "provider_kind": candidate["provider_kind"],
        "provider_source": candidate["provider_source"],
        "provider_release": candidate["source_snapshot_id"],
        "provider_entry_sha256": candidate["provider_entry_sha256"],
    }
    evidence["evidence_id"] = stage.grounding.compute_evidence_id(evidence)
    observed = {
        finding.code
        for finding in stage.grounding.validate_grounding_evidence(
            evidence, path=Path("candidate-evidence.jsonl"), line=1
        )
    }
    assert "complexportal_provider_receipt_required" in observed


def test_receipt_blockers_zero_evidence_and_outside_trait_digest_are_bound(
    tmp_path: Path,
) -> None:
    case = _case(tmp_path)
    before = _build(case)
    required = set(stage.GLOBAL_PROMOTION_BLOCKERS)
    assert required == {
        stage.MISSING_PROVIDER_RECEIPT,
        stage.MISSING_PROVIDER_FILE_LIST_RECEIPT,
        stage.MISSING_REGISTRY_RECEIPT,
    }
    assert all(required <= set(row["promotion_blockers"]) for row in before.candidates)
    assert all(
        required | set(row["blocking_reasons"]) <= set(row["promotion_blockers"])
        for row in before.blocked_tokens
    )
    assert all(row["grounding_evidence_emitted"] is False for row in before.candidates)
    assert all(row["grounding_evidence_emitted"] is False for row in before.blocked_tokens)
    assert before.summary["grounding_evidence_emitted_count"] == 0
    assert not any(
        row.get("kind") == "GROUNDING_EVIDENCE"
        for row in [*before.candidates, *before.blocked_tokens, *before.protein_requests]
    )

    outside = case["traits"] / "predicted-only.yaml"
    outside.write_text(
        outside.read_text(encoding="utf-8").replace(
            'label: "Predicted-only fixture"', 'label: "Changed predicted fixture"'
        ),
        encoding="utf-8",
    )
    after = _build(case)
    assert before.summary["candidate_rows_sha256"] == after.summary["candidate_rows_sha256"]
    assert before.summary["trait_binding_rows_sha256"] != after.summary["trait_binding_rows_sha256"]
    assert before.summary["stage_id"] != after.summary["stage_id"]


@pytest.mark.parametrize("flag", ["--apply", "--out", "--output", "--fetch", "--promote"])
def test_cli_has_no_writer_fetch_or_promotion_modes(flag: str) -> None:
    with pytest.raises(SystemExit):
        stage._parser().parse_args([flag])


def test_stage_is_read_only_for_fixture_tree(tmp_path: Path) -> None:
    case = _case(tmp_path)

    def tree_digest() -> str:
        rows = []
        for path in sorted(case["repo"].rglob("*")):
            if path.is_file():
                rows.append(
                    {
                        "path": path.relative_to(case["repo"]).as_posix(),
                        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                    }
                )
        return stage.value_sha256(rows)

    before = tree_digest()
    result = _build(case)
    after = tree_digest()
    assert before == after
    assert result.summary["network_action_performed"] is False
    assert result.summary["write_action_performed"] is False


def test_offline_no_sync_just_recipe_is_pinned() -> None:
    justfile = (REPO / "justfile").read_text(encoding="utf-8")
    assert (
        "stage-complexportal-source-native *args:\n"
        "    uv run --frozen --offline --no-sync python "
        "scripts/stage_complexportal_grounding_candidates.py {{args}}\n"
    ) in justfile


def test_registry_canonical_release_and_identity_contracts_fail_closed(tmp_path: Path) -> None:
    case = _case(tmp_path)
    row = _protein_reference("UniProtKB:P12345", taxon_id="NCBITaxon:10090")
    wrong_release = dict(row, uniprot_release="2025_01")
    _write_registry(case["registry"], [wrong_release])
    with pytest.raises(stage.ComplexPortalStageError, match="does not equal 2026_02"):
        _build(case)

    _write_registry(case["registry"], [row, row])
    with pytest.raises(stage.ComplexPortalStageError, match="duplicate ProteinReference"):
        _build(case)

    case["registry"].write_text(stage.canonical_json(row) + "\r\n", encoding="utf-8", newline="")
    with pytest.raises(stage.ComplexPortalStageError, match="canonical LF JSONL"):
        _build(case)

    duplicate_key_line = stage.canonical_json(row).replace(
        '"protein_id":"UniProtKB:P12345",',
        '"protein_id":"UniProtKB:P12345","protein_id":"UniProtKB:P12345",',
    )
    case["registry"].write_text(duplicate_key_line + "\n", encoding="utf-8")
    with pytest.raises(stage.ComplexPortalStageError, match="duplicate key"):
        _build(case)


@pytest.mark.parametrize("target", ["source", "predicted", "registry"])
def test_source_predicted_and_registry_symlinks_are_refused(tmp_path: Path, target: str) -> None:
    case = _case(tmp_path)
    path = {
        "source": case["raw"] / "10090.tsv",
        "predicted": case["raw"] / stage.EXCLUDED_PREDICTED_NAME,
        "registry": case["registry"],
    }[target]
    external = tmp_path / f"external-{target}"
    path.rename(external)
    path.symlink_to(external)
    with pytest.raises(
        stage.ComplexPortalStageError,
        match="symlink|without following symlinks",
    ):
        _build(case)


def test_required_descriptor_safety_capability_fails_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    case = _case(tmp_path)
    monkeypatch.setattr(stage.os, "supports_dir_fd", set())
    with pytest.raises(stage.ComplexPortalStageError, match="platform lacks required"):
        _build(case)


def test_production_complexportal_snapshot_when_artifacts_exist() -> None:
    required = [
        *(stage.DEFAULT_RAW_DIR / name for name in stage.EXPECTED_CURATED_SOURCE_FILES),
        stage.DEFAULT_RAW_DIR / stage.EXCLUDED_PREDICTED_NAME,
        stage.DEFAULT_TRAITS_DIR,
        stage.DEFAULT_PROTEIN_REGISTRY,
    ]
    if not all(path.exists() for path in required):
        pytest.skip("ignored production ComplexPortal/grounding artifacts are unavailable")

    result = stage.build_stage()
    summary = result.summary
    assert summary["source_file_count"] == 28
    assert summary["source_complex_count"] == 5_295
    assert summary["candidate_count"] == 20_234
    assert summary["blocked_token_count"] == 916
    assert summary["blocked_reason_counts"] == {
        "BLOCKED_COMPOSITE_TOKEN": 115,
        "BLOCKED_INTERNAL_INTERACTOR": 1,
        "BLOCKED_PROCESSED_CHAIN": 799,
        "EXACT_ECO_CODE_LABEL_MISMATCH": 1,
    }
    assert summary["unique_protein_count"] == 10_360
    assert summary["isoform_candidate_count"] == 144
    assert summary["unique_isoform_protein_count"] == 94
    assert summary["covered_source_complex_count"] == 5_090
    assert summary["uncovered_source_complex_count"] == 205
    assert summary["local_protein_reference_candidate_count"] == 24
    assert summary["local_protein_reference_unique_protein_count"] == 19
    assert summary["missing_protein_reference_candidate_count"] == 20_210
    assert summary["missing_protein_reference_request_count"] == 10_341
    assert summary["source_complex_to_protein_taxon_comparison_counts"] == {
        "IDENTICAL": 24,
        "NO_LOCAL_PROTEIN_REFERENCE": 20_210,
    }
    assert summary["source_complex_taxon_is_component_taxon_acceptance_invariant"] is False
    assert summary["trait_record_count"] == 20_579
    assert summary["trait_candidate_artifact_count"] == 20_810
    assert summary["source_derived_exact_trait_binding_count"] == 5_295
    assert summary["protein_registry_row_count"] == 126
    assert summary["grounding_evidence_emitted_count"] == 0
    assert summary["qualification_claimed"] is False
    assert summary["source_snapshot_id"] == SOURCE_SNAPSHOT_ID
    assert summary["candidate_rows_sha256"] == CANDIDATE_ROWS_SHA256
    assert summary["blocked_token_rows_sha256"] == BLOCKED_ROWS_SHA256
    assert summary["protein_request_rows_sha256"] == REQUEST_ROWS_SHA256
    assert summary["combined_non_summary_rows_sha256"] == COMBINED_ROWS_SHA256
    assert summary["trait_binding_rows_sha256"] == TRAIT_BINDING_ROWS_SHA256
    assert summary["source_derived_trait_binding_rows_sha256"] == SOURCE_TRAIT_BINDING_ROWS_SHA256
    assert summary["stage_id"] == STAGE_ID
    assert summary["summary_row_sha256"] == SUMMARY_ROW_SHA256
    assert set(summary["missing_receipts"]) == set(stage.GLOBAL_PROMOTION_BLOCKERS)
    assert all(row["grounding_evidence_emitted"] is False for row in result.candidates)
    assert all(row["grounding_evidence_emitted"] is False for row in result.blocked_tokens)
    rendered = stage.render_stage(result)
    assert rendered.count("\n") == FULL_STREAM_LINE_COUNT
    assert hashlib.sha256(rendered.encode("utf-8")).hexdigest() == FULL_STREAM_SHA256
