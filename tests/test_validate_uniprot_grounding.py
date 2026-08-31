"""Semantic gates for release-pinned, record-specific UniProt examples."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest
import yaml
from linkml.validator import Validator
from linkml.validator.plugins import JsonschemaValidationPlugin
from linkml.validator.report import Severity

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import validate_uniprot_grounding as V  # noqa: E402
import uniprot_membership_snapshot as M  # noqa: E402
from validate_strict import validate_one  # noqa: E402


SEQUENCE = "MSTACDEFGHIKLMNPQRSTVWY"
CHECKSUM = hashlib.sha256(SEQUENCE.encode("ascii")).hexdigest()
PROVIDER_ENTRY_CHECKSUM = hashlib.sha256(b"exact-provider-entry").hexdigest()
EVIDENCE_REGISTRY: dict[str, dict] = {}


def reference(protein_id: str = "UniProtKB:P12345", **changes: object) -> dict:
    value = {
        "protein_id": protein_id,
        "protein_label": "Example protein",
        "taxon_id": "NCBITaxon:9606",
        "taxon_label": "Homo sapiens",
        "sequence": SEQUENCE,
        "sequence_length": len(SEQUENCE),
        "sequence_sha256": CHECKSUM,
        "reviewed": True,
        "uniprot_release": "2026_02",
    }
    if protein_id.endswith("-2"):
        value["isoform"] = 2
    value.update(changes)
    return value


def occurrence(
    *,
    provider_kind: str | None = None,
    provider_source: str = "data/raw/interpro/protein2ipr.json",
    provider_release: str | None = None,
    provider_entry_sha256: str = PROVIDER_ENTRY_CHECKSUM,
    **changes: object,
) -> dict:
    value = {
        "trait_id": "PROSITE:PS00001",
        "protein_id": "UniProtKB:P12345",
        "scope": "LOCALIZED",
        "coordinate_frame": "UNIPROT_CANONICAL",
        "intervals": [{"start": 2, "end": 4, "expected_sequence": "STA"}],
        "source_trait_id": "PROSITE:PS00001",
        "mapping_method": "INTERPRO_MATCH",
        "evidence_source": "InterPro",
        "source_release": "109.0",
        "sequence_sha256": CHECKSUM,
        "qualification_status": "QUALIFIED",
    }
    value.update(changes)
    method = str(value.get("mapping_method"))
    provider_kind = provider_kind or {
        "UNIPROT_FEATURE": "UNIPROT",
        "INTERPRO_MATCH": "INTERPRO",
        "SIFTS_RESIDUE_MAPPING": "SIFTS",
    }.get(method, "SOURCE_DATABASE")
    provider_release = provider_release or str(value.get("source_release"))
    evidence = V.build_grounding_evidence(
        value,
        provider_kind=provider_kind,
        provider_source=provider_source,
        provider_release=provider_release,
        provider_entry_sha256=provider_entry_sha256,
    )
    value["source_evidence_id"] = evidence["evidence_id"]
    EVIDENCE_REGISTRY[evidence["evidence_id"]] = evidence
    return value


def example(**changes: object) -> dict:
    value = {
        "protein_id": "UniProtKB:P12345",
        "protein_label": "Example protein",
        "taxon_id": "NCBITaxon:9606",
        "taxon_label": "Homo sapiens",
        "sequence_length": len(SEQUENCE),
        "sequence_sha256": CHECKSUM,
        "uniprot_release": "2026_02",
        "qualification_status": "QUALIFIED",
        "source": "UNIPROT_GROUNDING",
        "trait_occurrences": [occurrence()],
    }
    value.update(changes)
    return value


def record(**changes: object) -> dict:
    value = {
        "identifier": "PROSITE:PS00001",
        "label": "example motif",
        "trait_axis": "SEQUENCE",
        "trait_category": "SEQ_MOTIF",
        "residue_sequence": "STA",
        "canonical_examples": [example()],
    }
    value.update(changes)
    return value


def codes(findings: list[V.Finding]) -> set[str]:
    return {finding.code for finding in findings}


def membership_cli_fixture(tmp_path: Path) -> dict[str, object]:
    """Write one complete, exact UniProt SOURCE_MEMBERSHIP validation fixture."""

    membership_path = tmp_path / "uniprot_memberships.jsonl"
    membership = M.extract_entry_memberships(
        {
            "uniProtKBCrossReferences": [
                {
                    "database": "PANTHER",
                    "id": "PTHR12345",
                    "properties": [{"key": "family", "value": "fixture"}],
                }
            ]
        },
        protein_id="UniProtKB:P12345",
        sequence_sha256=CHECKSUM,
        uniprot_release="2026_02",
    )[0]
    membership_path.write_text(M.dump_memberships([membership]), encoding="utf-8")
    whole_occurrence = occurrence(
        trait_id="PANTHER:PTHR12345",
        source_trait_id="PANTHER:PTHR12345",
        scope="WHOLE_PROTEIN",
        coordinate_frame=None,
        intervals=None,
        mapping_method="SOURCE_MEMBERSHIP",
        evidence_source="UniProtKB",
        source_release="2026_02",
        provider_kind="UNIPROT",
        provider_source=str(membership_path.resolve()),
        provider_release="2026_02",
        provider_entry_sha256=M.membership_entry_sha256(membership),
    )
    whole_occurrence.pop("coordinate_frame")
    whole_occurrence.pop("intervals")
    whole_record = record(
        identifier="PANTHER:PTHR12345",
        trait_axis="FUNCTION",
        trait_category="FUNC_PROTEIN_FAMILY",
        residue_sequence=None,
        canonical_examples=[example(trait_occurrences=[whole_occurrence])],
    )
    whole_record.pop("residue_sequence")
    trait_path = tmp_path / "trait.yaml"
    trait_path.write_text(yaml.safe_dump(whole_record, sort_keys=False), encoding="utf-8")
    registry_path = tmp_path / "protein_registry.jsonl"
    registry_path.write_text(json.dumps(reference()) + "\n", encoding="utf-8")
    evidence = EVIDENCE_REGISTRY[whole_occurrence["source_evidence_id"]]
    evidence_path = tmp_path / "occurrence_evidence.jsonl"
    evidence_path.write_text(json.dumps(evidence) + "\n", encoding="utf-8")
    return {
        "membership": membership,
        "membership_path": membership_path,
        "occurrence": whole_occurrence,
        "record": whole_record,
        "trait_path": trait_path,
        "registry_path": registry_path,
        "evidence": evidence,
        "evidence_path": evidence_path,
    }


def validate_record(
    value: object,
    registry: dict[str, dict],
    **kwargs: object,
) -> list[V.Finding]:
    kwargs.setdefault("evidence_registry", EVIDENCE_REGISTRY)
    return V.validate_record(value, registry, **kwargs)


def test_new_grounding_shape_passes_closed_linkml_validation(tmp_path):
    path = tmp_path / "qualified.yaml"
    path.write_text(yaml.safe_dump(record(), sort_keys=False), encoding="utf-8")
    assert validate_one(path) == []


def test_protein_reference_is_a_closed_standalone_linkml_root():
    validator = Validator(
        schema=str(ROOT / "src/proteintraitsmech/schema/proteintraitsmech.yaml"),
        validation_plugins=[JsonschemaValidationPlugin(closed=True)],
    )
    report = validator.validate(reference(), target_class="ProteinReference")
    assert [result for result in report.results if result.severity == Severity.ERROR] == []

    malformed = reference()
    malformed["unknown_registry_fact"] = "must fail closed"
    report = validator.validate(malformed, target_class="ProteinReference")
    assert any(result.severity == Severity.ERROR for result in report.results)


def test_grounding_evidence_is_a_closed_content_addressed_linkml_root():
    grounded_occurrence = occurrence()
    evidence = EVIDENCE_REGISTRY[grounded_occurrence["source_evidence_id"]]
    validator = Validator(
        schema=str(ROOT / "src/proteintraitsmech/schema/proteintraitsmech.yaml"),
        validation_plugins=[JsonschemaValidationPlugin(closed=True)],
    )
    report = validator.validate(evidence, target_class="GroundingEvidence")
    assert [result for result in report.results if result.severity == Severity.ERROR] == []

    malformed = dict(evidence, unknown_provider_claim="must fail closed")
    report = validator.validate(malformed, target_class="GroundingEvidence")
    assert any(result.severity == Severity.ERROR for result in report.results)


def test_qualified_localized_occurrence_passes_semantic_validation():
    registry = {"UniProtKB:P12345": reference()}
    assert validate_record(record(), registry) == []


def test_inline_sequence_is_not_required_because_registry_owns_it():
    assert "sequence" not in example()
    assert validate_record(record(), {"UniProtKB:P12345": reference()}) == []


def test_sequence_version_is_verified_when_present_but_not_required():
    registry = {"UniProtKB:P12345": reference(sequence_version=7)}
    assert validate_record(record(), registry) == []
    bad = record(canonical_examples=[example(sequence_version=6)])
    assert "sequence_version_mismatch" in codes(validate_record(bad, registry))


def test_unmarked_existing_example_is_legacy_not_qualified():
    legacy = {
        "identifier": "Pfam:PF00001",
        "label": "legacy",
        "trait_axis": "SEQUENCE",
        "canonical_examples": [
            {
                "protein_id": "UniProtKB:P12345",
                "protein_label": "Old label",
            }
        ],
    }
    assert V.effective_qualification_status(legacy["canonical_examples"][0]) == (
        "LEGACY_UNVERIFIED"
    )
    assert validate_record(legacy, {}) == []
    strict_codes = codes(validate_record(legacy, {}, require_qualified=True))
    assert {"legacy_unverified_example", "no_qualified_example"} <= strict_codes


def test_intermediate_candidate_state_is_rejected_inside_canonical_examples():
    candidate = record(
        canonical_examples=[example(qualification_status="SEQUENCE_VERIFIED", trait_occurrences=[])]
    )
    assert "unqualified_canonical_example" in codes(validate_record(candidate, {}))


def test_example_and_occurrence_must_both_be_qualified():
    registry = {"UniProtKB:P12345": reference()}
    no_occurrence_status = occurrence()
    no_occurrence_status.pop("qualification_status")
    bad = record(canonical_examples=[example(trait_occurrences=[no_occurrence_status])])
    observed = codes(validate_record(bad, registry))
    assert "unqualified_occurrence_in_canonical_example" in observed
    assert "qualified_without_qualified_occurrence" in observed

    bad = record(canonical_examples=[example(qualification_status="LEGACY_UNVERIFIED")])
    assert "qualified_occurrence_on_unqualified_example" in codes(validate_record(bad, registry))


def test_qualified_example_must_resolve_exact_registry_accession():
    observed = codes(validate_record(record(), {}))
    assert "unresolved_protein_reference" in observed


def test_qualified_metadata_and_sequence_snapshot_must_match_registry():
    bad_example = example(
        protein_label="Wrong",
        taxon_id="NCBITaxon:10090",
        taxon_label="Mus musculus",
        sequence_length=999,
        sequence_sha256="0" * 64,
        uniprot_release="2025_01",
        reviewed=False,
        sequence="AAAA",
    )
    observed = codes(
        validate_record(record(canonical_examples=[bad_example]), {"UniProtKB:P12345": reference()})
    )
    assert {
        "protein_label_mismatch",
        "taxon_id_mismatch",
        "taxon_label_mismatch",
        "sequence_length_mismatch",
        "sequence_sha256_mismatch",
        "uniprot_release_mismatch",
        "reviewed_mismatch",
        "inline_sequence_mismatch",
    } <= observed


def test_registry_checks_length_checksum_required_fields_and_unknown_fields(tmp_path):
    bad = reference(
        sequence_length=2,
        sequence_sha256="0" * 64,
        reviewed="yes",
        mystery="value",
    )
    findings = V.validate_protein_reference(bad, path=tmp_path / "registry.jsonl", line=1)
    assert {
        "registry_length_mismatch",
        "registry_checksum_mismatch",
        "registry_invalid_reviewed",
        "registry_unknown_field",
    } <= codes(findings)


def test_registry_isoform_suffix_and_coordinate_frame_are_exact(tmp_path):
    canonical_with_isoform = reference(isoform=2)
    assert "canonical_has_isoform" in codes(
        V.validate_protein_reference(canonical_with_isoform, path=tmp_path / "r", line=1)
    )
    wrong_isoform = reference("UniProtKB:P12345-2", isoform=3)
    assert "isoform_mismatch" in codes(
        V.validate_protein_reference(wrong_isoform, path=tmp_path / "r", line=2)
    )

    iso_ref = reference("UniProtKB:P12345-2")
    iso_occurrence = occurrence(
        protein_id="UniProtKB:P12345-2", coordinate_frame="UNIPROT_CANONICAL"
    )
    iso_example = example(protein_id="UniProtKB:P12345-2", trait_occurrences=[iso_occurrence])
    observed = codes(
        validate_record(record(canonical_examples=[iso_example]), {"UniProtKB:P12345-2": iso_ref})
    )
    assert "coordinate_frame_mismatch" in observed


def test_registry_loader_rejects_bad_json_and_duplicate_keys(tmp_path):
    path = tmp_path / "registry.jsonl"
    path.write_text(
        json.dumps(reference()) + "\nnot json\n" + json.dumps(reference()) + "\n",
        encoding="utf-8",
    )
    registry, findings = V.load_registry(path)
    assert list(registry) == ["UniProtKB:P12345"]
    assert {"registry_json_error", "duplicate_registry_key"} <= codes(findings)


def test_evidence_id_is_stable_and_loader_rejects_bad_rows(tmp_path):
    grounded_occurrence = occurrence()
    good = EVIDENCE_REGISTRY[grounded_occurrence["source_evidence_id"]]
    with_explicit_nulls = dict(good, inheritance_path=None, structure_id=None)
    assert V.compute_evidence_id(with_explicit_nulls) == good["evidence_id"]

    unknown = dict(good, unsupported_claim="forged")
    missing = dict(good)
    missing.pop("provider_source")
    missing["evidence_id"] = V.compute_evidence_id(missing)
    bad_provider_digest = dict(good, provider_entry_sha256="not-a-digest")
    bad_provider_digest["evidence_id"] = V.compute_evidence_id(bad_provider_digest)
    bad_content_digest = dict(good, source_release="110.0")
    path = tmp_path / "evidence.jsonl"
    path.write_text(
        "\n".join(
            [
                json.dumps(good),
                json.dumps(unknown),
                json.dumps(missing),
                json.dumps(bad_provider_digest),
                json.dumps(bad_content_digest),
                json.dumps(good),
                "not-json",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    loaded, findings = V.load_evidence_registry(path)
    assert list(loaded) == [good["evidence_id"]]
    assert {
        "evidence_unknown_field",
        "evidence_missing_field",
        "invalid_provider_entry_digest",
        "evidence_id_digest_mismatch",
        "duplicate_evidence_key",
        "evidence_json_error",
    } <= codes(findings)


def test_qualified_occurrence_evidence_must_resolve_and_match_exactly():
    registry = {"UniProtKB:P12345": reference()}
    grounded_occurrence = occurrence()
    grounded_record = record(canonical_examples=[example(trait_occurrences=[grounded_occurrence])])
    assert validate_record(grounded_record, registry) == []
    assert "evidence_registry_unavailable" in codes(V.validate_record(grounded_record, registry))

    unknown = dict(grounded_occurrence, source_evidence_id="ug-evidence:" + "0" * 64)
    assert "unknown_source_evidence" in codes(
        validate_record(record(canonical_examples=[example(trait_occurrences=[unknown])]), registry)
    )
    mismatched = dict(grounded_occurrence, source_release="forged-release")
    assert "occurrence_evidence_mismatch" in codes(
        validate_record(
            record(canonical_examples=[example(trait_occurrences=[mismatched])]), registry
        )
    )
    missing = dict(grounded_occurrence)
    missing.pop("source_evidence_id")
    assert "qualified_occurrence_without_evidence" in codes(
        validate_record(record(canonical_examples=[example(trait_occurrences=[missing])]), registry)
    )


def test_interpro_provider_and_source_cannot_be_forged():
    forged_provider = occurrence(
        trait_id="Pfam:PF00001",
        source_trait_id="Pfam:PF00001",
        provider_kind="SOURCE_DATABASE",
    )
    forged_record = record(
        identifier="Pfam:PF00001",
        trait_category="SEQ_DOMAIN",
        canonical_examples=[example(trait_occurrences=[forged_provider])],
    )
    assert "evidence_provider_method_mismatch" in codes(
        validate_record(forged_record, {"UniProtKB:P12345": reference()})
    )

    forged_source = occurrence(
        trait_id="Pfam:PF00001",
        source_trait_id="Pfam:PF00001",
        evidence_source="Pfam",
    )
    forged_record = record(
        identifier="Pfam:PF00001",
        trait_category="SEQ_DOMAIN",
        canonical_examples=[example(trait_occurrences=[forged_source])],
    )
    assert "interpro_source_mismatch" in codes(
        validate_record(forged_record, {"UniProtKB:P12345": reference()})
    )


def test_ecod_source_native_coordinates_cannot_bypass_sifts():
    forged = occurrence(
        trait_id="ECOD:123.1.1",
        source_trait_id="ECOD:123.1.1",
        mapping_method="SOURCE_NATIVE_COORDINATES",
        evidence_source="ECOD",
        source_release="2026-01",
        provider_kind="SOURCE_DATABASE",
        provider_source="data/raw/ecod/domains.tsv",
        provider_release="2026-01",
    )
    ecod_record = record(
        identifier="ECOD:123.1.1",
        trait_axis="STRUCTURE",
        trait_category="STRUCT_DOMAIN",
        canonical_examples=[example(trait_occurrences=[forged])],
    )
    observed = codes(validate_record(ecod_record, {"UniProtKB:P12345": reference()}))
    assert {
        "structure_evidence_requires_sifts",
        "structure_native_coordinates_forbidden",
    } <= observed


def test_mcsa_source_native_coordinates_cannot_bypass_sifts():
    for namespace in ("MCSA", "M-CSA"):
        trait_id = f"{namespace}:123"
        forged = occurrence(
            trait_id=trait_id,
            source_trait_id=trait_id,
            mapping_method="SOURCE_NATIVE_COORDINATES",
            evidence_source="MCSA",
            source_release="2026-08",
            provider_kind="SOURCE_DATABASE",
            provider_source="data/raw/mcsa.entries.jsonl",
            provider_release="2026-08",
        )
        mcsa_record = record(
            identifier=trait_id,
            trait_axis="STRUCTURE",
            trait_category="STRUCT_ACTIVE_SITE",
            canonical_examples=[example(trait_occurrences=[forged])],
        )
        observed = codes(validate_record(mcsa_record, {"UniProtKB:P12345": reference()}))
        assert {
            "structure_evidence_requires_sifts",
            "structure_native_coordinates_forbidden",
        } <= observed


def test_non_structure_source_native_coordinates_do_not_require_sifts():
    trait_id = "ELM:ELME000001"
    source_native = occurrence(
        trait_id=trait_id,
        source_trait_id=trait_id,
        mapping_method="SOURCE_NATIVE_COORDINATES",
        evidence_source="ELM",
        source_release="1.4",
        provider_kind="SOURCE_DATABASE",
        provider_source="data/raw/elm/elm_instances.tsv",
        provider_release="1.4",
    )
    elm_record = record(
        identifier=trait_id,
        canonical_examples=[example(trait_occurrences=[source_native])],
    )

    observed = codes(validate_record(elm_record, {"UniProtKB:P12345": reference()}))
    assert observed == {"elm_provider_receipt_required"}
    assert "structure_evidence_requires_sifts" not in observed


def test_elm_regex_is_matched_at_exact_source_span_in_complete_protein():
    trait_id = "ELM:ELME000001"
    source_native = occurrence(
        trait_id=trait_id,
        source_trait_id=trait_id,
        mapping_method="SOURCE_NATIVE_COORDINATES",
        evidence_source="ELM",
        source_release="elm-source-snapshot:fixture",
        provider_kind="SOURCE_DATABASE",
        provider_source="data/raw/elm/elm_instances.tsv",
        provider_release="elm-source-snapshot:fixture",
    )
    elm_record = record(
        identifier=trait_id,
        sequence_pattern="S.A",
        canonical_examples=[example(trait_occurrences=[source_native])],
    )
    assert codes(validate_record(elm_record, {"UniProtKB:P12345": reference()})) == {
        "elm_provider_receipt_required"
    }

    terminal_only = dict(elm_record)
    terminal_only["sequence_pattern"] = "STA$"
    observed = codes(validate_record(terminal_only, {"UniProtKB:P12345": reference()}))
    assert "record_sequence_pattern_mismatch" in observed

    greedy, error = V.compile_elm_sequence_pattern("P.{2,5}P")
    assert error is None and greedy is not None
    sequence = "MPAAPXXP"
    assert greedy.match(sequence, 1).end() == 8
    assert V.elm_pattern_matches_exact_span(greedy, sequence, 2, 5)
    terminal, error = V.compile_elm_sequence_pattern("P..P$")
    assert error is None and terminal is not None
    assert not V.elm_pattern_matches_exact_span(terminal, "MPAAPQQ", 2, 5)

    context_expanded = dict(elm_record)
    context_expanded["sequence_pattern"] = "ST"
    observed = codes(validate_record(context_expanded, {"UniProtKB:P12345": reference()}))
    assert "record_sequence_pattern_mismatch" in observed


def test_elm_exact_span_backtracks_across_alternatives_to_required_endpoint():
    alternative, error = V.compile_elm_sequence_pattern("A|AB")
    assert error is None and alternative is not None
    sequence = "MABQ"

    # Python's preferred first alternative consumes only A. The endpoint
    # constraint must make the engine retry AB for the two-residue source span.
    assert alternative.match(sequence, 1).end() == 2
    assert V.elm_pattern_matches_exact_span(alternative, sequence, 2, 3)


def test_elm_start_anchor_rejects_a_non_n_terminal_source_span():
    n_terminal, error = V.compile_elm_sequence_pattern("^AB")
    assert error is None and n_terminal is not None

    assert not V.elm_pattern_matches_exact_span(n_terminal, "MABQ", 2, 3)


def test_elm_provider_contract_is_source_native_and_release_exact():
    trait_id = "ELM:ELME000001"
    wrong = occurrence(
        trait_id=trait_id,
        source_trait_id=trait_id,
        mapping_method="PATTERN_MATCH",
        evidence_source="NotELM",
        source_release="elm-source-snapshot:fixture",
        provider_kind="SOURCE_DATABASE",
        provider_source="data/raw/elm/elm_instances.tsv",
        provider_release="different-snapshot",
    )
    observed = codes(
        V.validate_grounding_evidence(
            EVIDENCE_REGISTRY[wrong["source_evidence_id"]],
            path=Path("evidence.jsonl"),
            line=1,
        )
    )
    assert {
        "elm_source_method_mismatch",
        "elm_source_mismatch",
        "elm_release_mismatch",
        "elm_provider_receipt_required",
    } <= observed


def test_elm_evidence_source_cannot_hide_behind_non_elm_trait_ids():
    disguised = occurrence(
        trait_id="Pfam:PF00001",
        source_trait_id="Pfam:PF00001",
        mapping_method="SOURCE_NATIVE_COORDINATES",
        evidence_source="ELM",
        source_release="elm-source-snapshot:fixture",
        provider_kind="SOURCE_DATABASE",
        provider_source="data/raw/elm/elm_instances.tsv",
        provider_release="elm-source-snapshot:fixture",
    )
    observed = codes(
        V.validate_grounding_evidence(
            EVIDENCE_REGISTRY[disguised["source_evidence_id"]],
            path=Path("evidence.jsonl"),
            line=1,
        )
    )
    assert observed == {
        "elm_provider_receipt_required",
        "elm_source_trait_namespace_mismatch",
    }


def test_disprot_idpo_provider_contract_is_exact_and_receipt_closed():
    trait_id = "IDPO:0000002"
    source_native = occurrence(
        trait_id=trait_id,
        source_trait_id=trait_id,
        mapping_method="SOURCE_NATIVE_COORDINATES",
        evidence_source="DisProt",
        source_release="disprot-source-snapshot:fixture",
        provider_kind="SOURCE_DATABASE",
        provider_source="data/raw/disprot.entries.json",
        provider_release="disprot-source-snapshot:fixture",
    )
    evidence = EVIDENCE_REGISTRY[source_native["source_evidence_id"]]

    assert codes(V.validate_grounding_evidence(evidence, path=Path("evidence.jsonl"), line=1)) == {
        "disprot_provider_receipt_required"
    }


@pytest.mark.parametrize(
    ("change", "expected_code"),
    [
        ({"mapping_method": "PATTERN_MATCH"}, "disprot_source_method_mismatch"),
        ({"provider_kind": "UNIPROT"}, "disprot_provider_mismatch"),
        ({"evidence_source": "NotDisProt"}, "disprot_source_mismatch"),
        ({"provider_release": "different-snapshot"}, "disprot_release_mismatch"),
        ({"scope": "WHOLE_PROTEIN"}, "disprot_scope_mismatch"),
        ({"source_trait_id": "IDPO:0000003"}, "disprot_source_trait_mismatch"),
        ({"source_trait_id": "Pfam:PF00001"}, "disprot_source_trait_mismatch"),
    ],
)
def test_disprot_idpo_provider_contract_rejects_each_wrong_field(change, expected_code):
    values = {
        "trait_id": "IDPO:0000002",
        "source_trait_id": "IDPO:0000002",
        "mapping_method": "SOURCE_NATIVE_COORDINATES",
        "evidence_source": "DisProt",
        "source_release": "disprot-source-snapshot:fixture",
        "provider_kind": "SOURCE_DATABASE",
        "provider_source": "data/raw/disprot.entries.json",
        "provider_release": "disprot-source-snapshot:fixture",
    }
    values.update(change)
    source_native = occurrence(**values)
    evidence = EVIDENCE_REGISTRY[source_native["source_evidence_id"]]
    observed = codes(V.validate_grounding_evidence(evidence, path=Path("evidence.jsonl"), line=1))

    assert expected_code in observed
    assert "disprot_provider_receipt_required" in observed


@pytest.mark.parametrize(
    ("trait_id", "source_trait_id", "evidence_source"),
    [
        ("IDPO:0000002", "IDPO:0000002", "NotDisProt"),
        ("Pfam:PF00001", "IDPO:0000002", "NotDisProt"),
        ("Pfam:PF00001", "Pfam:PF00001", "DisProt"),
    ],
)
def test_disprot_lock_triggers_from_either_idpo_namespace_or_reverse_source(
    trait_id, source_trait_id, evidence_source
):
    disguised = occurrence(
        trait_id=trait_id,
        source_trait_id=source_trait_id,
        mapping_method="SOURCE_NATIVE_COORDINATES",
        evidence_source=evidence_source,
        source_release="disprot-source-snapshot:fixture",
        provider_kind="SOURCE_DATABASE",
        provider_source="data/raw/disprot.entries.json",
        provider_release="disprot-source-snapshot:fixture",
    )
    evidence = EVIDENCE_REGISTRY[disguised["source_evidence_id"]]
    observed = codes(V.validate_grounding_evidence(evidence, path=Path("evidence.jsonl"), line=1))

    assert "disprot_provider_receipt_required" in observed
    if evidence_source != "DisProt":
        assert "disprot_source_mismatch" in observed
    if trait_id != source_trait_id or not trait_id.startswith("IDPO:"):
        assert "disprot_source_trait_mismatch" in observed


def test_disprot_lock_does_not_change_elm_or_non_disprot_provider_contracts():
    elm_id = "ELM:ELME000001"
    elm = occurrence(
        trait_id=elm_id,
        source_trait_id=elm_id,
        mapping_method="SOURCE_NATIVE_COORDINATES",
        evidence_source="ELM",
        source_release="elm-source-snapshot:fixture",
        provider_kind="SOURCE_DATABASE",
        provider_source="data/raw/elm/elm_instances.tsv",
        provider_release="elm-source-snapshot:fixture",
    )
    elm_codes = codes(
        V.validate_grounding_evidence(
            EVIDENCE_REGISTRY[elm["source_evidence_id"]],
            path=Path("evidence.jsonl"),
            line=1,
        )
    )
    assert elm_codes == {"elm_provider_receipt_required"}
    ordinary = occurrence()
    ordinary_codes = codes(
        V.validate_grounding_evidence(
            EVIDENCE_REGISTRY[ordinary["source_evidence_id"]],
            path=Path("evidence.jsonl"),
            line=2,
        )
    )
    assert ordinary_codes == set()


def complexportal_evidence(**changes: object) -> dict:
    values = {
        "trait_id": "ComplexPortal:CPX-10",
        "source_trait_id": "ComplexPortal:CPX-10",
        "scope": "WHOLE_PROTEIN",
        "coordinate_frame": None,
        "intervals": None,
        "mapping_method": "SOURCE_MEMBERSHIP",
        "evidence_source": "ComplexPortal",
        "source_release": "complexportal-source-snapshot:fixture",
        "provider_kind": "SOURCE_DATABASE",
        "provider_source": "data/raw/complexportal/9606.tsv",
        "provider_release": "complexportal-source-snapshot:fixture",
    }
    values.update(changes)
    grounded = occurrence(**values)
    return EVIDENCE_REGISTRY[grounded["source_evidence_id"]]


def test_complexportal_provider_contract_is_exact_and_receipt_closed():
    evidence = complexportal_evidence()

    assert codes(V.validate_grounding_evidence(evidence, path=Path("evidence.jsonl"), line=1)) == {
        "complexportal_provider_receipt_required"
    }


@pytest.mark.parametrize(
    ("change", "expected_code"),
    [
        ({"mapping_method": "SOURCE_ANNOTATION"}, "complexportal_source_method_mismatch"),
        ({"provider_kind": "UNIPROT"}, "complexportal_provider_mismatch"),
        ({"evidence_source": "NotComplexPortal"}, "complexportal_source_mismatch"),
        ({"provider_release": "different-snapshot"}, "complexportal_release_mismatch"),
        ({"scope": "LOCALIZED"}, "complexportal_scope_mismatch"),
        (
            {"source_trait_id": "ComplexPortal:CPX-11"},
            "complexportal_source_trait_mismatch",
        ),
        ({"trait_id": "Pfam:PF00001"}, "complexportal_source_trait_mismatch"),
        (
            {
                "trait_id": "ComplexPortal:CPX-0",
                "source_trait_id": "ComplexPortal:CPX-0",
            },
            "complexportal_source_trait_mismatch",
        ),
        (
            {
                "trait_id": "ComplexPortal:CPX-01",
                "source_trait_id": "ComplexPortal:CPX-01",
            },
            "complexportal_source_trait_mismatch",
        ),
    ],
)
def test_complexportal_provider_contract_rejects_each_wrong_field(change, expected_code):
    evidence = complexportal_evidence(**change)
    observed = codes(V.validate_grounding_evidence(evidence, path=Path("evidence.jsonl"), line=1))

    assert expected_code in observed
    assert "complexportal_provider_receipt_required" in observed


@pytest.mark.parametrize(
    ("trait_id", "source_trait_id", "evidence_source"),
    [
        ("ComplexPortal:CPX-10", "Pfam:PF00001", "NotComplexPortal"),
        ("Pfam:PF00001", "ComplexPortal:CPX-10", "NotComplexPortal"),
        ("Pfam:PF00001", "Pfam:PF00001", "ComplexPortal"),
    ],
)
def test_complexportal_lock_triggers_from_either_namespace_or_reverse_source(
    trait_id, source_trait_id, evidence_source
):
    evidence = complexportal_evidence(
        trait_id=trait_id,
        source_trait_id=source_trait_id,
        evidence_source=evidence_source,
    )
    observed = codes(V.validate_grounding_evidence(evidence, path=Path("evidence.jsonl"), line=1))

    assert "complexportal_provider_receipt_required" in observed
    if evidence_source != "ComplexPortal":
        assert "complexportal_source_mismatch" in observed
    assert "complexportal_source_trait_mismatch" in observed


def test_complexportal_lock_does_not_change_elm_disprot_or_ordinary_contracts():
    elm_id = "ELM:ELME000001"
    elm = occurrence(
        trait_id=elm_id,
        source_trait_id=elm_id,
        mapping_method="SOURCE_NATIVE_COORDINATES",
        evidence_source="ELM",
        source_release="elm-source-snapshot:fixture",
        provider_kind="SOURCE_DATABASE",
        provider_source="data/raw/elm/elm_instances.tsv",
        provider_release="elm-source-snapshot:fixture",
    )
    disprot_id = "IDPO:0000002"
    disprot = occurrence(
        trait_id=disprot_id,
        source_trait_id=disprot_id,
        mapping_method="SOURCE_NATIVE_COORDINATES",
        evidence_source="DisProt",
        source_release="disprot-source-snapshot:fixture",
        provider_kind="SOURCE_DATABASE",
        provider_source="data/raw/disprot.entries.json",
        provider_release="disprot-source-snapshot:fixture",
    )
    ordinary = occurrence()

    assert codes(
        V.validate_grounding_evidence(
            EVIDENCE_REGISTRY[elm["source_evidence_id"]],
            path=Path("evidence.jsonl"),
            line=1,
        )
    ) == {"elm_provider_receipt_required"}
    assert codes(
        V.validate_grounding_evidence(
            EVIDENCE_REGISTRY[disprot["source_evidence_id"]],
            path=Path("evidence.jsonl"),
            line=2,
        )
    ) == {"disprot_provider_receipt_required"}
    assert (
        codes(
            V.validate_grounding_evidence(
                EVIDENCE_REGISTRY[ordinary["source_evidence_id"]],
                path=Path("evidence.jsonl"),
                line=3,
            )
        )
        == set()
    )


def rhea_evidence(**changes: object) -> dict:
    values = {
        "trait_id": "RHEA:10000",
        "source_trait_id": "RHEA:10000",
        "scope": "WHOLE_PROTEIN",
        "coordinate_frame": None,
        "intervals": None,
        "mapping_method": "SOURCE_MEMBERSHIP",
        "evidence_source": "Rhea",
        "source_release": "141",
        "provider_kind": "SOURCE_DATABASE",
        "provider_source": "data/raw/rhea/rhea2uniprot_sprot.tsv",
        "provider_release": "141",
    }
    values.update(changes)
    grounded = occurrence(**values)
    return EVIDENCE_REGISTRY[grounded["source_evidence_id"]]


def test_rhea_provider_contract_is_exact_but_receipt_verifier_closed():
    evidence = rhea_evidence()

    assert codes(V.validate_grounding_evidence(evidence, path=Path("evidence.jsonl"), line=1)) == {
        "rhea_provider_receipt_required"
    }


@pytest.mark.parametrize(
    ("change", "expected_code"),
    [
        ({"mapping_method": "SOURCE_ANNOTATION"}, "rhea_source_method_mismatch"),
        ({"provider_kind": "UNIPROT"}, "rhea_provider_mismatch"),
        ({"evidence_source": "NotRhea"}, "rhea_source_mismatch"),
        ({"source_release": "142"}, "rhea_release_mismatch"),
        ({"provider_release": "142"}, "rhea_release_mismatch"),
        ({"scope": "LOCALIZED"}, "rhea_scope_mismatch"),
        ({"source_trait_id": "RHEA:10001"}, "rhea_source_trait_mismatch"),
        (
            {"trait_id": "RHEA:0", "source_trait_id": "RHEA:0"},
            "rhea_source_trait_mismatch",
        ),
        (
            {"trait_id": "RHEA:010000", "source_trait_id": "RHEA:010000"},
            "rhea_source_trait_mismatch",
        ),
        ({"provider_source": "data/raw/rhea/fixture.tsv"}, "rhea_provider_source_mismatch"),
        (
            {"inheritance_path": ["RHEA:10001", "RHEA:10000"]},
            "rhea_inheritance_mismatch",
        ),
        ({"structure_id": "PDB:1ABC"}, "rhea_structural_provenance_mismatch"),
        ({"chain_id": "A"}, "rhea_structural_provenance_mismatch"),
        ({"mapping_completeness": "NOT_APPLICABLE"}, "rhea_structural_provenance_mismatch"),
        ({"source_residue_count": 1}, "rhea_structural_provenance_mismatch"),
        ({"mapped_residue_count": 1}, "rhea_structural_provenance_mismatch"),
    ],
)
def test_rhea_provider_contract_rejects_each_wrong_field(change, expected_code):
    evidence = rhea_evidence(**change)
    observed = codes(V.validate_grounding_evidence(evidence, path=Path("evidence.jsonl"), line=1))

    assert expected_code in observed
    assert "rhea_provider_receipt_required" in observed
    assert "source_database_contract_required" not in observed


@pytest.mark.parametrize(
    ("trait_id", "source_trait_id", "evidence_source"),
    [
        ("RHEA:10000", "Pfam:PF00001", "NotRhea"),
        ("Pfam:PF00001", "RHEA:10000", "NotRhea"),
        ("Pfam:PF00001", "Pfam:PF00001", "Rhea"),
    ],
)
def test_rhea_lock_triggers_from_either_namespace_or_reverse_source(
    trait_id, source_trait_id, evidence_source
):
    evidence = rhea_evidence(
        trait_id=trait_id,
        source_trait_id=source_trait_id,
        evidence_source=evidence_source,
    )
    observed = codes(V.validate_grounding_evidence(evidence, path=Path("evidence.jsonl"), line=1))

    assert "rhea_provider_receipt_required" in observed
    assert "rhea_source_trait_mismatch" in observed
    if evidence_source != "Rhea":
        assert "rhea_source_mismatch" in observed


@pytest.mark.parametrize(
    ("trait_id", "evidence_source"),
    [
        ("Rhea:10000", "rhea"),
        ("RHEA2:10000", "Rhea2"),
        ("RHEA-legacy:10000", "Rhea release 141"),
    ],
)
def test_rhea_contract_trigger_is_exact_and_near_misses_remain_generic(trait_id, evidence_source):
    evidence = rhea_evidence(
        trait_id=trait_id,
        source_trait_id=trait_id,
        evidence_source=evidence_source,
    )

    observed = codes(V.validate_grounding_evidence(evidence, path=Path("evidence.jsonl"), line=1))
    assert observed == {"source_database_contract_required"}


def scope_occurrence(**changes: object) -> dict:
    values = {
        "trait_id": "SCOP:100",
        "source_trait_id": "SCOP:100",
        "mapping_method": "SIFTS_RESIDUE_MAPPING",
        "evidence_source": "SCOPe",
        "source_release": "2.08",
        "provider_kind": "SIFTS",
        "provider_source": "data/raw/sifts/scop_residue_mapping.jsonl",
        # The SIFTS provider release is intentionally independent of SCOPe 2.08.
        "provider_release": "2026-08-25",
        "structure_id": "PDB:1ABC",
        "chain_id": "A",
        "mapping_completeness": "COMPLETE",
        "source_residue_count": 3,
        "mapped_residue_count": 3,
    }
    values.update(changes)
    return occurrence(**values)


def scope_evidence(**changes: object) -> dict:
    grounded = scope_occurrence(**changes)
    return EVIDENCE_REGISTRY[grounded["source_evidence_id"]]


def test_scope_complete_sifts_contract_is_closed_only_on_provider_receipt():
    evidence = scope_evidence()

    assert codes(V.validate_grounding_evidence(evidence, path=Path("evidence.jsonl"), line=1)) == {
        "scope_provider_receipt_required"
    }
    assert evidence["provider_release"] != evidence["source_release"]


@pytest.mark.parametrize(
    ("change", "expected_code"),
    [
        ({"mapping_method": "SOURCE_NATIVE_COORDINATES"}, "scope_source_method_mismatch"),
        ({"evidence_source": "SCOPe dir.com"}, "scope_source_mismatch"),
        ({"trait_id": "SCOP:0"}, "scope_trait_id_mismatch"),
        ({"trait_id": "SCOP:01"}, "scope_trait_id_mismatch"),
        ({"source_trait_id": "SCOP:0"}, "scope_trait_id_mismatch"),
        ({"source_trait_id": "SCOP:01"}, "scope_trait_id_mismatch"),
        ({"provider_kind": "SOURCE_DATABASE"}, "scope_provider_mismatch"),
        ({"scope": "WHOLE_PROTEIN"}, "scope_scope_mismatch"),
        ({"coordinate_frame": "UNIPROT_ISOFORM"}, "scope_coordinate_frame_mismatch"),
        ({"source_release": "2.08-stable"}, "scope_release_mismatch"),
    ],
)
def test_scope_provider_contract_rejects_each_wrong_field(change, expected_code):
    evidence = scope_evidence(**change)
    observed = codes(V.validate_grounding_evidence(evidence, path=Path("evidence.jsonl"), line=1))

    assert expected_code in observed
    assert "scope_provider_receipt_required" in observed


@pytest.mark.parametrize(
    ("trait_id", "source_trait_id", "evidence_source", "source_mismatch"),
    [
        ("SCOP:100", "Pfam:PF00001", "NotSCOPe", True),
        ("Pfam:PF00001", "SCOP:100", "NotSCOPe", True),
        ("SCOPe:100", "Pfam:PF00001", "NotSCOPe", True),
        ("Pfam:PF00001", "Pfam:PF00001", "SCOPe", False),
    ],
)
def test_scope_lock_triggers_from_either_namespace_or_reverse_source(
    trait_id, source_trait_id, evidence_source, source_mismatch
):
    inheritance_path = [source_trait_id, trait_id] if source_trait_id != trait_id else None
    evidence = scope_evidence(
        trait_id=trait_id,
        source_trait_id=source_trait_id,
        evidence_source=evidence_source,
        inheritance_path=inheritance_path,
    )
    observed = codes(V.validate_grounding_evidence(evidence, path=Path("evidence.jsonl"), line=1))

    assert "scope_provider_receipt_required" in observed
    assert "scope_trait_id_mismatch" in observed
    assert ("scope_source_mismatch" in observed) is source_mismatch


def test_scope_source_native_coordinates_cannot_bypass_sifts():
    evidence = scope_evidence(
        mapping_method="SOURCE_NATIVE_COORDINATES",
        provider_kind="SOURCE_DATABASE",
    )
    observed = codes(V.validate_grounding_evidence(evidence, path=Path("evidence.jsonl"), line=1))

    assert {
        "scope_source_method_mismatch",
        "scope_provider_mismatch",
        "scope_provider_receipt_required",
        "structure_evidence_requires_sifts",
        "structure_native_coordinates_forbidden",
        "sifts_provider_required",
    } <= observed


def test_scope_distinct_canonical_ids_use_an_explicit_inheritance_path():
    grounded = scope_occurrence(
        trait_id="SCOP:100",
        source_trait_id="SCOP:101",
        inheritance_path=["SCOP:101", "SCOP:100"],
    )
    evidence = EVIDENCE_REGISTRY[grounded["source_evidence_id"]]
    assert codes(V.validate_grounding_evidence(evidence, path=Path("evidence.jsonl"), line=1)) == {
        "scope_provider_receipt_required"
    }

    scope_record = record(
        identifier="SCOP:100",
        trait_axis="STRUCTURE",
        trait_category="STRUCT_DOMAIN",
        canonical_examples=[example(trait_occurrences=[grounded])],
    )
    observed = codes(
        validate_record(
            scope_record,
            {"UniProtKB:P12345": reference()},
            hierarchy_index={"SCOP:101": {"SCOP:100"}},
        )
    )
    assert observed == {"scope_provider_receipt_required"}


@pytest.mark.parametrize(
    "near_miss",
    ["SCOPe dir.com", "SCOPe2", "scope", "SCOP", " SCOPe"],
)
def test_scope_evidence_source_trigger_is_exact_and_does_not_match_near_misses(near_miss):
    ordinary = occurrence(
        mapping_method="SOURCE_NATIVE_COORDINATES",
        evidence_source=near_miss,
        source_release="2.08",
        provider_kind="SOURCE_DATABASE",
        provider_source="data/raw/provider/ordinary.tsv",
        provider_release="independent-provider-release",
    )
    evidence = EVIDENCE_REGISTRY[ordinary["source_evidence_id"]]
    observed = codes(V.validate_grounding_evidence(evidence, path=Path("evidence.jsonl"), line=1))

    assert not {code for code in observed if code.startswith("scope_")}


def test_scope_lock_does_not_change_complexportal_or_ordinary_contracts():
    portal_codes = codes(
        V.validate_grounding_evidence(complexportal_evidence(), path=Path("evidence.jsonl"), line=1)
    )
    ordinary = occurrence()
    ordinary_codes = codes(
        V.validate_grounding_evidence(
            EVIDENCE_REGISTRY[ordinary["source_evidence_id"]],
            path=Path("evidence.jsonl"),
            line=2,
        )
    )

    assert portal_codes == {"complexportal_provider_receipt_required"}
    assert ordinary_codes == set()


def cath_interpro_occurrence(**changes: object) -> dict:
    values = {
        "trait_id": "CATH:3.40.50.300",
        "source_trait_id": "CATH:3.40.50.300",
        "mapping_method": "INTERPRO_MATCH",
        "evidence_source": "InterPro",
        "source_release": "109.0",
        "provider_kind": "INTERPRO",
        "provider_source": "data/raw/interpro/protein2ipr.json",
        "provider_release": "109.0",
    }
    values.update(changes)
    return occurrence(**values)


def cath_native_occurrence(**changes: object) -> dict:
    values = {
        "trait_id": "CATH:3.40.50.300",
        "source_trait_id": "CATH:3.40.50.300",
        "mapping_method": "SIFTS_RESIDUE_MAPPING",
        "evidence_source": "CATH",
        "source_release": "v4.4.0",
        "provider_kind": "SIFTS",
        "provider_source": "data/raw/sifts/cath_residue_mapping.jsonl",
        # The SIFTS release is intentionally independent of CATH v4.4.0.
        "provider_release": "2026-08-25",
        "structure_id": "PDB:1ABC",
        "chain_id": "A",
        "mapping_completeness": "COMPLETE",
        "source_residue_count": 3,
        "mapped_residue_count": 3,
    }
    values.update(changes)
    return occurrence(**values)


def cath_interpro_evidence(**changes: object) -> dict:
    grounded = cath_interpro_occurrence(**changes)
    return EVIDENCE_REGISTRY[grounded["source_evidence_id"]]


def cath_native_evidence(**changes: object) -> dict:
    grounded = cath_native_occurrence(**changes)
    return EVIDENCE_REGISTRY[grounded["source_evidence_id"]]


def test_cath_interpro_contract_is_closed_only_on_provider_receipt():
    evidence = cath_interpro_evidence()

    assert codes(V.validate_grounding_evidence(evidence, path=Path("evidence.jsonl"), line=1)) == {
        "cath_provider_receipt_required"
    }
    assert evidence["source_release"] == evidence["provider_release"] == "109.0"


def test_cath_native_sifts_contract_is_closed_only_on_provider_receipt():
    evidence = cath_native_evidence()

    assert codes(V.validate_grounding_evidence(evidence, path=Path("evidence.jsonl"), line=1)) == {
        "cath_provider_receipt_required"
    }
    assert evidence["source_release"] == "v4.4.0"
    assert evidence["provider_release"] == "2026-08-25"
    assert evidence["provider_release"] != evidence["source_release"]


@pytest.mark.parametrize(
    ("change", "expected_code"),
    [
        ({"mapping_method": "SOURCE_NATIVE_COORDINATES"}, "cath_source_method_mismatch"),
        ({"evidence_source": "CATH"}, "cath_source_mismatch"),
        ({"provider_kind": "SOURCE_DATABASE"}, "cath_provider_mismatch"),
        ({"scope": "WHOLE_PROTEIN"}, "cath_scope_mismatch"),
        ({"coordinate_frame": "UNIPROT_ISOFORM"}, "cath_coordinate_frame_mismatch"),
        ({"source_release": "109.0-stable"}, "cath_release_mismatch"),
        ({"provider_release": "109.1"}, "cath_release_mismatch"),
    ],
)
def test_cath_interpro_contract_rejects_each_wrong_field(change, expected_code):
    evidence = cath_interpro_evidence(**change)
    observed = codes(V.validate_grounding_evidence(evidence, path=Path("evidence.jsonl"), line=1))

    assert expected_code in observed
    assert "cath_provider_receipt_required" in observed


@pytest.mark.parametrize(
    "ancestor_id",
    ["CATH:3", "CATH:3.40", "CATH:3.40.50"],
)
def test_cath_interpro_source_must_be_an_exact_four_level_descendant(ancestor_id):
    evidence = cath_interpro_evidence(
        trait_id=ancestor_id,
        source_trait_id=ancestor_id,
    )
    observed = codes(V.validate_grounding_evidence(evidence, path=Path("evidence.jsonl"), line=1))

    assert observed == {
        "cath_interpro_source_trait_mismatch",
        "cath_provider_receipt_required",
    }


@pytest.mark.parametrize(
    ("change", "expected_code"),
    [
        ({"mapping_method": "SOURCE_NATIVE_COORDINATES"}, "cath_source_method_mismatch"),
        ({"evidence_source": "InterPro"}, "cath_source_mismatch"),
        ({"provider_kind": "INTERPRO"}, "cath_provider_mismatch"),
        ({"scope": "WHOLE_PROTEIN"}, "cath_scope_mismatch"),
        ({"coordinate_frame": "UNIPROT_ISOFORM"}, "cath_coordinate_frame_mismatch"),
        ({"source_release": "4.4.0"}, "cath_release_mismatch"),
    ],
)
def test_cath_native_contract_rejects_each_wrong_field(change, expected_code):
    evidence = cath_native_evidence(**change)
    observed = codes(V.validate_grounding_evidence(evidence, path=Path("evidence.jsonl"), line=1))

    assert expected_code in observed
    assert "cath_provider_receipt_required" in observed


@pytest.mark.parametrize(
    "invalid_id",
    ["CATH:0", "CATH:01", "CATH:1.0", "CATH:1.02", "CATH:1.2.3.4.5"],
)
@pytest.mark.parametrize("field", ["trait_id", "source_trait_id"])
def test_cath_both_ids_are_independently_canonical(field, invalid_id):
    evidence = cath_interpro_evidence(**{field: invalid_id})
    observed = codes(V.validate_grounding_evidence(evidence, path=Path("evidence.jsonl"), line=1))

    assert "cath_trait_id_mismatch" in observed
    assert "cath_provider_receipt_required" in observed


@pytest.mark.parametrize(
    ("trait_id", "source_trait_id", "evidence_source", "source_mismatch"),
    [
        ("CATH:3.40.50", "Pfam:PF00001", "NotCATH", True),
        ("Pfam:PF00001", "CATH:3.40.50", "NotCATH", True),
        ("Pfam:PF00001", "Pfam:PF00001", "CATH", False),
    ],
)
def test_cath_lock_triggers_from_either_namespace_or_reverse_source(
    trait_id, source_trait_id, evidence_source, source_mismatch
):
    inheritance_path = [source_trait_id, trait_id] if source_trait_id != trait_id else None
    evidence = cath_native_evidence(
        trait_id=trait_id,
        source_trait_id=source_trait_id,
        evidence_source=evidence_source,
        inheritance_path=inheritance_path,
    )
    observed = codes(V.validate_grounding_evidence(evidence, path=Path("evidence.jsonl"), line=1))

    assert "cath_provider_receipt_required" in observed
    assert "cath_trait_id_mismatch" in observed
    assert ("cath_source_mismatch" in observed) is source_mismatch


@pytest.mark.parametrize(
    "near_miss",
    ["CATH v4.4.0", "CATH2", "cath", "Cath", " CATH", "CATH "],
)
def test_cath_evidence_source_trigger_is_exact_and_does_not_match_near_misses(near_miss):
    ordinary = occurrence(
        mapping_method="SOURCE_NATIVE_COORDINATES",
        evidence_source=near_miss,
        source_release="v4.4.0",
        provider_kind="SOURCE_DATABASE",
        provider_source="data/raw/provider/ordinary.tsv",
        provider_release="independent-provider-release",
    )
    evidence = EVIDENCE_REGISTRY[ordinary["source_evidence_id"]]
    observed = codes(V.validate_grounding_evidence(evidence, path=Path("evidence.jsonl"), line=1))

    assert observed == {"source_database_contract_required"}


@pytest.mark.parametrize(
    ("change", "expected_code"),
    [
        ({"structure_id": None}, "incomplete_sifts_provenance"),
        ({"chain_id": None}, "incomplete_sifts_provenance"),
        ({"mapping_completeness": "PARTIAL"}, "incomplete_sifts_mapping"),
        ({"mapped_residue_count": 2}, "incomplete_sifts_mapping"),
    ],
)
def test_cath_native_lane_retains_generic_sifts_checks(change, expected_code):
    evidence = cath_native_evidence(**change)
    observed = codes(V.validate_grounding_evidence(evidence, path=Path("evidence.jsonl"), line=1))

    assert expected_code in observed
    assert "cath_provider_receipt_required" in observed


@pytest.mark.parametrize(
    "builder",
    [cath_interpro_occurrence, cath_native_occurrence],
)
def test_cath_distinct_canonical_ids_use_an_explicit_inheritance_path(builder):
    grounded = builder(
        trait_id="CATH:3.40.50",
        source_trait_id="CATH:3.40.50.300",
        inheritance_path=["CATH:3.40.50.300", "CATH:3.40.50"],
    )
    evidence = EVIDENCE_REGISTRY[grounded["source_evidence_id"]]
    assert codes(V.validate_grounding_evidence(evidence, path=Path("evidence.jsonl"), line=1)) == {
        "cath_provider_receipt_required"
    }

    cath_record = record(
        identifier="CATH:3.40.50",
        trait_axis="STRUCTURE",
        trait_category="STRUCT_TOPOLOGY",
        canonical_examples=[example(trait_occurrences=[grounded])],
    )
    observed = codes(
        validate_record(
            cath_record,
            {"UniProtKB:P12345": reference()},
            hierarchy_index={"CATH:3.40.50.300": {"CATH:3.40.50"}},
        )
    )
    assert observed == {"cath_provider_receipt_required"}


def test_cath_lock_does_not_change_scope_or_ordinary_interpro_contracts():
    scope_codes = codes(
        V.validate_grounding_evidence(scope_evidence(), path=Path("evidence.jsonl"), line=1)
    )
    ordinary = occurrence()
    ordinary_codes = codes(
        V.validate_grounding_evidence(
            EVIDENCE_REGISTRY[ordinary["source_evidence_id"]],
            path=Path("evidence.jsonl"),
            line=2,
        )
    )

    assert scope_codes == {"scope_provider_receipt_required"}
    assert ordinary_codes == set()


def pending_sifts_evidence(
    *, trait_id: str, evidence_source: str, source_trait_id: str | None = None, **changes: object
) -> dict:
    values = {
        "trait_id": trait_id,
        "source_trait_id": source_trait_id or trait_id,
        "mapping_method": "SIFTS_RESIDUE_MAPPING",
        "evidence_source": evidence_source,
        "source_release": "source-release-fixture",
        "provider_kind": "SIFTS",
        "provider_source": "data/raw/sifts/provider-fixture.jsonl",
        "provider_release": "sifts-release-fixture",
        "structure_id": "PDB:1ABC",
        "chain_id": "A",
        "mapping_completeness": "COMPLETE",
        "source_residue_count": 3,
        "mapped_residue_count": 3,
    }
    values.update(changes)
    grounded = occurrence(**values)
    return EVIDENCE_REGISTRY[grounded["source_evidence_id"]]


@pytest.mark.parametrize(
    ("trait_id", "evidence_source", "expected_code", "interpro_lane"),
    [
        ("PRINTS:PR00001", "InterPro", "prints_provider_receipt_required", True),
        ("SFLD:SFLDF00001", "InterPro", "sfld_provider_receipt_required", True),
        ("ECOD:F.1.2.3.4", "ECOD via PDBe SIFTS", "ecod_provider_receipt_required", False),
        (
            "proteintraitsmech:INTERFACE_PF00001_PF00002",
            "3did",
            "threedid_provider_receipt_required",
            False,
        ),
        (
            "proteintraitsmech:BIOLIP_ATP",
            "BioLiP",
            "biolip_provider_receipt_required",
            False,
        ),
        ("MCSA:123", "MCSA", "mcsa_provider_receipt_required", False),
        (
            "proteintraitsmech:METALPDB_ZN_MONONUCLEAR",
            "MetalPDB",
            "metalpdb_provider_receipt_required",
            False,
        ),
        ("RepeatsDB:1.2", "RepeatsDB", "repeatsdb_provider_receipt_required", False),
    ],
)
def test_pending_provider_identity_is_closed_only_on_its_specific_receipt(
    trait_id, evidence_source, expected_code, interpro_lane
):
    if interpro_lane:
        grounded = occurrence(
            trait_id=trait_id,
            source_trait_id=trait_id,
            mapping_method="INTERPRO_MATCH",
            evidence_source=evidence_source,
            source_release="109.0",
            provider_kind="INTERPRO",
            provider_source="data/raw/interpro/protein2ipr.json",
            provider_release="109.0",
        )
        evidence = EVIDENCE_REGISTRY[grounded["source_evidence_id"]]
    else:
        evidence = pending_sifts_evidence(
            trait_id=trait_id,
            evidence_source=evidence_source,
        )

    observed = [
        finding.code
        for finding in V.validate_grounding_evidence(evidence, path=Path("evidence.jsonl"), line=1)
    ]
    assert observed.count(expected_code) == 1
    assert set(observed) == {expected_code}


@pytest.mark.parametrize(
    ("trait_id", "evidence_source", "expected_code"),
    [
        ("ThreeDID:PF00001_PF00002", "ThreeDID", "threedid_provider_receipt_required"),
        ("MCSA:123", "M-CSA", "mcsa_provider_receipt_required"),
        ("M-CSA:123", "MCSA", "mcsa_provider_receipt_required"),
    ],
)
def test_pending_provider_aliases_share_one_specific_receipt_lock(
    trait_id, evidence_source, expected_code
):
    evidence = pending_sifts_evidence(trait_id=trait_id, evidence_source=evidence_source)

    observed = [
        finding.code
        for finding in V.validate_grounding_evidence(evidence, path=Path("evidence.jsonl"), line=1)
    ]
    assert observed.count(expected_code) == 1
    assert set(observed) == {expected_code}


@pytest.mark.parametrize(
    ("evidence_source", "expected_code"),
    [
        ("PRINTS", "prints_provider_receipt_required"),
        ("SFLD", "sfld_provider_receipt_required"),
        ("ECOD", "ecod_provider_receipt_required"),
        ("ECOD via PDBe SIFTS", "ecod_provider_receipt_required"),
        ("3did", "threedid_provider_receipt_required"),
        ("ThreeDID", "threedid_provider_receipt_required"),
        ("BioLiP", "biolip_provider_receipt_required"),
        ("MCSA", "mcsa_provider_receipt_required"),
        ("M-CSA", "mcsa_provider_receipt_required"),
        ("MetalPDB", "metalpdb_provider_receipt_required"),
        ("RepeatsDB", "repeatsdb_provider_receipt_required"),
    ],
)
def test_pending_provider_lock_triggers_from_exact_reverse_source(evidence_source, expected_code):
    evidence = pending_sifts_evidence(
        trait_id="PROSITE:PS00001",
        evidence_source=evidence_source,
    )

    observed = [
        finding.code
        for finding in V.validate_grounding_evidence(evidence, path=Path("evidence.jsonl"), line=1)
    ]
    assert observed.count(expected_code) == 1
    assert set(observed) == {expected_code}


@pytest.mark.parametrize(
    ("near_miss", "specific_code"),
    [
        ("PRINTS2", "prints_provider_receipt_required"),
        ("SFLD4", "sfld_provider_receipt_required"),
        ("ECODish", "ecod_provider_receipt_required"),
        ("ThreeDIDb", "threedid_provider_receipt_required"),
        ("BioLiP2", "biolip_provider_receipt_required"),
        ("MCSAx", "mcsa_provider_receipt_required"),
        ("MetalPDB2", "metalpdb_provider_receipt_required"),
        ("RepeatsDB2", "repeatsdb_provider_receipt_required"),
    ],
)
def test_pending_provider_reverse_source_matching_is_exact(near_miss, specific_code):
    evidence = pending_sifts_evidence(
        trait_id="PROSITE:PS00001",
        evidence_source=near_miss,
    )

    observed = codes(V.validate_grounding_evidence(evidence, path=Path("evidence.jsonl"), line=1))
    assert specific_code not in observed
    assert observed == {"sifts_provider_receipt_required"}


def test_malformed_provider_source_is_reported_without_receipt_matcher_crash():
    grounded = occurrence(evidence_source=["PRINTS"])
    evidence = EVIDENCE_REGISTRY[grounded["source_evidence_id"]]

    observed = codes(V.validate_grounding_evidence(evidence, path=Path("evidence.jsonl"), line=1))
    assert "invalid_evidence_field" in observed
    assert "interpro_source_mismatch" in observed
    assert "prints_provider_receipt_required" not in observed


@pytest.mark.parametrize(
    ("near_miss_id", "specific_code"),
    [
        ("PRINTS2:PR00001", "prints_provider_receipt_required"),
        ("SFLD2:SFLDF00001", "sfld_provider_receipt_required"),
        ("ECODish:F.1.2.3.4", "ecod_provider_receipt_required"),
        (
            "proteintraitsmech:INTERFACEX_PF00001_PF00002",
            "threedid_provider_receipt_required",
        ),
        ("proteintraitsmech:BIOLIPX_ATP", "biolip_provider_receipt_required"),
        ("MCSAX:123", "mcsa_provider_receipt_required"),
        (
            "proteintraitsmech:METALPDBX_ZN_MONONUCLEAR",
            "metalpdb_provider_receipt_required",
        ),
        ("RepeatsDB2:1.2", "repeatsdb_provider_receipt_required"),
    ],
)
def test_pending_provider_identifier_matching_is_exact(near_miss_id, specific_code):
    evidence = pending_sifts_evidence(
        trait_id=near_miss_id,
        evidence_source="ordinary source",
    )

    observed = codes(V.validate_grounding_evidence(evidence, path=Path("evidence.jsonl"), line=1))
    assert specific_code not in observed
    assert observed == {"sifts_provider_receipt_required"}


def test_pending_provider_table_keys_and_findings_are_unique():
    assert len({lock.key for lock in V.PENDING_PROVIDER_LOCKS}) == len(V.PENDING_PROVIDER_LOCKS)
    assert len({lock.code for lock in V.PENDING_PROVIDER_LOCKS}) == len(V.PENDING_PROVIDER_LOCKS)


def test_unmatched_sifts_method_or_kind_has_one_generic_receipt_lock():
    by_method = pending_sifts_evidence(
        trait_id="PROSITE:PS00001",
        evidence_source="ordinary structural source",
        provider_kind="SOURCE_DATABASE",
    )
    by_kind = occurrence(
        mapping_method="SOURCE_NATIVE_COORDINATES",
        evidence_source="ordinary structural source",
        source_release="source-release-fixture",
        provider_kind="SIFTS",
        provider_source="data/raw/sifts/provider-fixture.jsonl",
        provider_release="sifts-release-fixture",
    )

    method_codes = codes(
        V.validate_grounding_evidence(by_method, path=Path("evidence.jsonl"), line=1)
    )
    kind_evidence = EVIDENCE_REGISTRY[by_kind["source_evidence_id"]]
    kind_codes = codes(
        V.validate_grounding_evidence(kind_evidence, path=Path("evidence.jsonl"), line=2)
    )
    assert "sifts_provider_receipt_required" in method_codes
    assert "source_database_contract_required" not in method_codes
    assert "sifts_provider_receipt_required" in kind_codes


def test_unmatched_source_database_contract_is_closed():
    grounded = occurrence(
        trait_id="ExampleDB:12345",
        source_trait_id="ExampleDB:12345",
        scope="WHOLE_PROTEIN",
        coordinate_frame=None,
        intervals=None,
        mapping_method="SOURCE_MEMBERSHIP",
        evidence_source="ExampleDB",
        source_release="fixture-release",
        provider_kind="SOURCE_DATABASE",
        provider_source="data/raw/exampledb/fixture.tsv",
        provider_release="fixture-release",
    )
    evidence = EVIDENCE_REGISTRY[grounded["source_evidence_id"]]

    assert codes(V.validate_grounding_evidence(evidence, path=Path("evidence.jsonl"), line=1)) == {
        "source_database_contract_required"
    }


@pytest.mark.parametrize(
    "trait_id",
    ["PROSITE:PS00001", "Pfam:PF00001", "HAMAP:MF_00001", "Gene3D:G3DSA_1.10.10.10"],
)
def test_pending_provider_locks_do_not_change_ordinary_interpro_contracts(trait_id):
    grounded = occurrence(trait_id=trait_id, source_trait_id=trait_id)
    evidence = EVIDENCE_REGISTRY[grounded["source_evidence_id"]]

    assert V.validate_grounding_evidence(evidence, path=Path("evidence.jsonl"), line=1) == []


def test_pending_provider_locks_do_not_change_uniprot_feature_or_membership_contracts():
    feature = occurrence(
        mapping_method="UNIPROT_FEATURE",
        evidence_source="UniProtKB",
        source_release="2026_02",
        provider_kind="UNIPROT",
        provider_source="data/raw/uniprot/features.jsonl",
        provider_release="2026_02",
    )
    membership = occurrence(
        trait_id="PANTHER:PTHR12345",
        source_trait_id="PANTHER:PTHR12345",
        scope="WHOLE_PROTEIN",
        coordinate_frame=None,
        intervals=None,
        mapping_method="SOURCE_MEMBERSHIP",
        evidence_source="UniProtKB",
        source_release="2026_02",
        provider_kind="UNIPROT",
        provider_source="data/raw/uniprot/memberships.jsonl",
        provider_release="2026_02",
    )

    for grounded in (feature, membership):
        evidence = EVIDENCE_REGISTRY[grounded["source_evidence_id"]]
        assert V.validate_grounding_evidence(evidence, path=Path("evidence.jsonl"), line=1) == []


def test_current_durable_interpro_evidence_remains_clean_when_present():
    path = V.DEFAULT_EVIDENCE_REGISTRY
    if not path.is_file():
        pytest.skip("durable grounding evidence is not installed")

    registry, findings = V.load_evidence_registry(path)
    assert len(registry) == 127
    assert {row["provider_kind"] for row in registry.values()} == {"INTERPRO"}
    assert findings == []


def test_uniprot_feature_provider_release_must_equal_source_release():
    feature = occurrence(
        mapping_method="UNIPROT_FEATURE",
        evidence_source="UniProtKB",
        source_release="2026_02",
        provider_kind="UNIPROT",
        provider_source="data/raw/uniprot/features.jsonl",
        provider_release="2025_04",
    )
    observed = codes(
        V.validate_grounding_evidence(
            EVIDENCE_REGISTRY[feature["source_evidence_id"]],
            path=Path("evidence.jsonl"),
            line=1,
        )
    )
    assert "uniprot_release_mismatch" in observed


def test_hierarchy_index_is_built_from_exact_parent_edges(tmp_path):
    child = tmp_path / "child.yaml"
    child.write_text(
        yaml.safe_dump(
            {
                "identifier": "PROSITE:PS_CHILD",
                "parent_traits": ["PROSITE:PS00001"],
            }
        ),
        encoding="utf-8",
    )
    parent = tmp_path / "parent.yaml"
    parent.write_text(
        yaml.safe_dump(
            {
                "identifier": "PROSITE:PS00001",
                "parent_traits": [],
            }
        ),
        encoding="utf-8",
    )
    hierarchy, findings = V.build_hierarchy_index([tmp_path])
    assert findings == []
    assert hierarchy["PROSITE:PS_CHILD"] == frozenset({"PROSITE:PS00001"})


def test_interval_order_bounds_and_expected_sequence_are_checked():
    bad_occurrence = occurrence(
        intervals=[
            {"start": 5, "end": 4},
            {"start": 2, "end": 99},
            {"start": 2, "end": 4, "expected_sequence": "AAA"},
            {"start": 3, "end": 5},
        ]
    )
    observed = codes(
        validate_record(
            record(canonical_examples=[example(trait_occurrences=[bad_occurrence])]),
            {"UniProtKB:P12345": reference()},
        )
    )
    assert {
        "reversed_interval",
        "coordinate_out_of_bounds",
        "interval_sequence_mismatch",
        "overlapping_or_unsorted_intervals",
    } <= observed


def test_discontinuous_residue_positions_preserve_order_and_match_residues():
    good_occurrence = occurrence(
        intervals=None,
        residue_positions=[2, 4, 6],
        expected_residues="SAD",
    )
    good_occurrence.pop("intervals")
    good_record = record(
        residue_sequence="SAD",
        canonical_examples=[example(trait_occurrences=[good_occurrence])],
    )
    registry = {"UniProtKB:P12345": reference()}
    assert validate_record(good_record, registry) == []

    bad_occurrence = dict(good_occurrence, residue_positions=[4, 2, 2], expected_residues="AAA")
    observed = codes(
        validate_record(
            record(canonical_examples=[example(trait_occurrences=[bad_occurrence])]), registry
        )
    )
    assert "unsorted_or_duplicate_positions" in observed
    assert "expected_residue_mismatch" in observed


def test_exact_trait_identity_or_explicit_inheritance_path_is_required():
    inherited = occurrence(
        source_trait_id="PROSITE:PS_CHILD",
        inheritance_path=["PROSITE:PS_CHILD", "PROSITE:PS00001"],
    )
    registry = {"UniProtKB:P12345": reference()}
    inherited_record = record(canonical_examples=[example(trait_occurrences=[inherited])])
    assert "inheritance_hierarchy_unavailable" in codes(validate_record(inherited_record, registry))
    hierarchy = {"PROSITE:PS_CHILD": {"PROSITE:PS00001"}}
    assert validate_record(inherited_record, registry, hierarchy_index=hierarchy) == []
    assert "unproven_trait_inheritance_edge" in codes(
        validate_record(
            inherited_record,
            registry,
            hierarchy_index={"PROSITE:PS_CHILD": {"PROSITE:PS_OTHER"}},
        )
    )

    undocumented = occurrence(source_trait_id="PROSITE:PS_CHILD")
    assert "undocumented_trait_inheritance" in codes(
        validate_record(
            record(canonical_examples=[example(trait_occurrences=[undocumented])]), registry
        )
    )


def test_prosite_and_literal_patterns_are_checked_against_occurrence_sequence():
    compiled, error = V.compile_sequence_pattern("[ST]-x-A.")
    assert error is None and compiled is not None and compiled.fullmatch("STA")
    compiled, error = V.compile_sequence_pattern("S-T-{P}.")
    assert error is None and compiled is not None and compiled.fullmatch("STA")
    compiled, error = V.compile_sequence_pattern("STA")
    assert error is None and compiled is not None and compiled.fullmatch("STA")

    patterned = record(sequence_pattern="[ST]-x-A.")
    assert validate_record(patterned, {"UniProtKB:P12345": reference()}) == []
    mismatch = record(sequence_pattern="C-C-C.")
    assert "record_sequence_pattern_mismatch" in codes(
        validate_record(mismatch, {"UniProtKB:P12345": reference()})
    )


def test_function_whole_protein_shape_still_requires_a_source_contract_without_fake_extent():
    whole_occurrence = occurrence(
        trait_id="GO:0000001",
        source_trait_id="GO:0000001",
        scope="WHOLE_PROTEIN",
        coordinate_frame=None,
        intervals=None,
        mapping_method="SOURCE_ANNOTATION",
    )
    whole_occurrence.pop("coordinate_frame")
    whole_occurrence.pop("intervals")
    whole_example = example(trait_occurrences=[whole_occurrence])
    whole_record = record(
        identifier="GO:0000001",
        trait_axis="FUNCTION",
        trait_category="FUNC_MOLECULAR_FUNCTION",
        residue_sequence=None,
        canonical_examples=[whole_example],
    )
    whole_record.pop("residue_sequence")
    assert codes(validate_record(whole_record, {"UniProtKB:P12345": reference()})) == {
        "source_database_contract_required"
    }


def test_cli_replays_exact_uniprot_membership_provider_fact(tmp_path):
    fixture = membership_cli_fixture(tmp_path)
    output = tmp_path / "validation.tsv"

    assert (
        V.main(
            [
                str(fixture["trait_path"]),
                "--registry",
                str(fixture["registry_path"]),
                "--evidence-registry",
                str(fixture["evidence_path"]),
                "--membership-registry",
                str(fixture["membership_path"]),
                "--out",
                str(output),
                "--quiet",
            ]
        )
        == 0
    )
    assert output.read_text(encoding="utf-8").count("\n") == 1


def test_cli_membership_replay_rejects_missing_tampered_or_wrong_exact_fact(tmp_path):
    fixture = membership_cli_fixture(tmp_path)
    membership_path = fixture["membership_path"]
    assert isinstance(membership_path, Path)

    def run(suffix: str) -> str:
        output = tmp_path / f"validation-{suffix}.tsv"
        assert (
            V.main(
                [
                    str(fixture["trait_path"]),
                    "--registry",
                    str(fixture["registry_path"]),
                    "--evidence-registry",
                    str(fixture["evidence_path"]),
                    "--membership-registry",
                    str(membership_path),
                    "--out",
                    str(output),
                    "--quiet",
                ]
            )
            == 1
        )
        return output.read_text(encoding="utf-8")

    membership_path.unlink()
    assert "membership_registry_not_found" in run("missing")

    membership = fixture["membership"]
    assert isinstance(membership, dict)
    tampered = json.loads(M.dump_memberships([membership]))
    tampered["database_cross_reference"]["properties"][0]["value"] = "forged"
    membership_path.write_text(json.dumps(tampered) + "\n", encoding="utf-8")
    assert "membership_registry_invalid" in run("tampered")

    wrong = M.extract_entry_memberships(
        {"uniProtKBCrossReferences": [{"database": "PANTHER", "id": "PTHR99999"}]},
        protein_id="UniProtKB:P12345",
        sequence_sha256=CHECKSUM,
        uniprot_release="2026_02",
    )[0]
    membership_path.write_text(M.dump_memberships([wrong]), encoding="utf-8")
    assert "exact_uniprot_membership_not_found" in run("wrong-trait")


def test_cli_membership_replay_rejects_forged_provider_digest(tmp_path):
    fixture = membership_cli_fixture(tmp_path)
    evidence = dict(fixture["evidence"])
    evidence["provider_entry_sha256"] = "0" * 64
    evidence["evidence_id"] = V.compute_evidence_id(evidence)
    evidence_path = fixture["evidence_path"]
    assert isinstance(evidence_path, Path)
    evidence_path.write_text(json.dumps(evidence) + "\n", encoding="utf-8")
    whole_record = fixture["record"]
    assert isinstance(whole_record, dict)
    whole_record["canonical_examples"][0]["trait_occurrences"][0]["source_evidence_id"] = evidence[
        "evidence_id"
    ]
    trait_path = fixture["trait_path"]
    assert isinstance(trait_path, Path)
    trait_path.write_text(yaml.safe_dump(whole_record, sort_keys=False), encoding="utf-8")
    output = tmp_path / "validation-forged-digest.tsv"

    assert (
        V.main(
            [
                str(trait_path),
                "--registry",
                str(fixture["registry_path"]),
                "--evidence-registry",
                str(evidence_path),
                "--membership-registry",
                str(fixture["membership_path"]),
                "--out",
                str(output),
                "--quiet",
            ]
        )
        == 1
    )
    assert "membership_provider_entry_mismatch" in output.read_text(encoding="utf-8")


def test_whole_protein_scope_is_category_limited_and_rejects_fake_coordinates():
    whole = occurrence(
        scope="WHOLE_PROTEIN",
        coordinate_frame="UNIPROT_CANONICAL",
        mapping_method="SOURCE_MEMBERSHIP",
    )
    observed = codes(
        validate_record(
            record(canonical_examples=[example(trait_occurrences=[whole])]),
            {"UniProtKB:P12345": reference()},
        )
    )
    assert {"whole_protein_not_permitted", "whole_protein_has_coordinates"} <= observed


def test_function_axis_cannot_be_localized():
    functional = record(
        trait_axis="FUNCTION",
        trait_category="FUNC_MOLECULAR_FUNCTION",
    )
    assert "localized_scope_not_permitted" in codes(
        validate_record(functional, {"UniProtKB:P12345": reference()})
    )


def test_complete_sifts_mapping_passes_and_partial_or_wrong_counts_fail():
    sifts = occurrence(
        mapping_method="SIFTS_RESIDUE_MAPPING",
        structure_id="PDB:1ABC",
        chain_id="A",
        mapping_completeness="COMPLETE",
        source_residue_count=3,
        mapped_residue_count=3,
    )
    registry = {"UniProtKB:P12345": reference()}
    assert codes(
        validate_record(record(canonical_examples=[example(trait_occurrences=[sifts])]), registry)
    ) == {"sifts_provider_receipt_required"}

    partial = dict(
        sifts,
        mapping_completeness="PARTIAL",
        source_residue_count=4,
        mapped_residue_count=3,
    )
    observed = codes(
        validate_record(record(canonical_examples=[example(trait_occurrences=[partial])]), registry)
    )
    assert {"partial_mapping_cannot_qualify", "incomplete_sifts_mapping"} <= observed


def test_pdb_derived_occurrence_cannot_bypass_sifts():
    bypass = occurrence(structure_id="PDB:1ABC", mapping_method="SOURCE_NATIVE_COORDINATES")
    assert "pdb_mapping_without_sifts" in codes(
        validate_record(
            record(canonical_examples=[example(trait_occurrences=[bypass])]),
            {"UniProtKB:P12345": reference()},
        )
    )


def test_cli_writes_deterministic_tsv_and_fails_false_qualified_claim(tmp_path):
    registry_path = tmp_path / "registry.jsonl"
    registry_path.write_text(json.dumps(reference()) + "\n", encoding="utf-8")
    bad_record = record(canonical_examples=[example(taxon_label="Wrong organism")])
    evidence_id = bad_record["canonical_examples"][0]["trait_occurrences"][0]["source_evidence_id"]
    evidence_path = tmp_path / "evidence.jsonl"
    evidence_path.write_text(json.dumps(EVIDENCE_REGISTRY[evidence_id]) + "\n", encoding="utf-8")
    trait_path = tmp_path / "trait.yaml"
    trait_path.write_text(yaml.safe_dump(bad_record, sort_keys=False), encoding="utf-8")
    output = tmp_path / "validation.tsv"
    assert (
        V.main(
            [
                str(trait_path),
                "--registry",
                str(registry_path),
                "--evidence-registry",
                str(evidence_path),
                "--out",
                str(output),
                "--quiet",
            ]
        )
        == 1
    )
    rows = output.read_text(encoding="utf-8").splitlines()
    assert rows[0].endswith("\tcode\tmessage")
    assert any("taxon_label_mismatch" in row for row in rows[1:])


def test_cli_missing_default_registries_is_legacy_safe_but_qualified_fails(tmp_path, monkeypatch):
    missing_proteins = tmp_path / "missing-proteins.jsonl"
    missing_evidence = tmp_path / "missing-evidence.jsonl"
    monkeypatch.setattr(V, "DEFAULT_REGISTRY", missing_proteins)
    monkeypatch.setattr(V, "DEFAULT_EVIDENCE_REGISTRY", missing_evidence)

    legacy_path = tmp_path / "legacy.yaml"
    legacy_path.write_text(
        yaml.safe_dump(
            {
                "identifier": "Pfam:PF00001",
                "canonical_examples": [
                    {
                        "protein_id": "UniProtKB:P12345",
                        "protein_label": "legacy",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    output = tmp_path / "legacy.tsv"
    assert V.main([str(legacy_path), "--out", str(output), "--quiet"]) == 0

    qualified_path = tmp_path / "qualified.yaml"
    qualified_path.write_text(yaml.safe_dump(record()), encoding="utf-8")
    output = tmp_path / "qualified.tsv"
    assert V.main([str(qualified_path), "--out", str(output), "--quiet"]) == 1
    observed = output.read_text(encoding="utf-8")
    assert "registry_not_found" in observed
    assert "evidence_registry_not_found" in observed


def test_quoted_and_escaped_qualification_keys_cannot_skip_elm_validation(tmp_path, monkeypatch):
    trait_id = "ELM:ELME000001"
    source_native = occurrence(
        trait_id=trait_id,
        source_trait_id=trait_id,
        mapping_method="SOURCE_NATIVE_COORDINATES",
        evidence_source="ELM",
        source_release="elm-source-snapshot:fixture",
        provider_kind="SOURCE_DATABASE",
        provider_source="data/raw/elm/elm_instances.tsv",
        provider_release="elm-source-snapshot:fixture",
    )
    elm_record = record(
        identifier=trait_id,
        sequence_pattern="S.A",
        canonical_examples=[example(trait_occurrences=[source_native])],
    )
    evidence = EVIDENCE_REGISTRY[source_native["source_evidence_id"]]
    encoded = json.dumps(elm_record)
    escaped = encoded.replace('"qualification_status"', '"qualification\\u005fstatus"')
    for name, text in (("quoted.yaml", encoded), ("escaped.yml", escaped)):
        trait_path = tmp_path / name
        trait_path.write_text(text, encoding="utf-8")
        assert "elm_provider_receipt_required" in codes(
            V.validate_yaml_file(
                trait_path,
                {"UniProtKB:P12345": reference()},
                evidence_registry={evidence["evidence_id"]: evidence},
            )
        )

    assert {path.name for path in V.iter_yaml_files([tmp_path])} == {
        "escaped.yml",
        "quoted.yaml",
    }

    missing_proteins = tmp_path / "missing-proteins.jsonl"
    missing_evidence = tmp_path / "missing-evidence.jsonl"
    monkeypatch.setattr(V, "DEFAULT_REGISTRY", missing_proteins)
    monkeypatch.setattr(V, "DEFAULT_EVIDENCE_REGISTRY", missing_evidence)
    output = tmp_path / "quoted-validation.tsv"
    assert V.main([str(tmp_path / "quoted.yaml"), "--out", str(output), "--quiet"]) == 1
    observed = output.read_text(encoding="utf-8")
    assert "registry_not_found" in observed
    assert "evidence_registry_not_found" in observed


def test_iter_yaml_files_recursively_discovers_uppercase_yml_suffix(tmp_path):
    nested = tmp_path / "nested"
    nested.mkdir()
    uppercase = nested / "trait.YML"
    uppercase.write_text("identifier: TEST:uppercase\n", encoding="utf-8")
    (nested / "ignored.txt").write_text("not a trait\n", encoding="utf-8")

    assert V.iter_yaml_files([tmp_path]) == [uppercase]


def test_cli_missing_default_membership_registry_is_safe_when_not_used(tmp_path, monkeypatch):
    missing_memberships = tmp_path / "missing-memberships.jsonl"
    monkeypatch.setattr(V, "DEFAULT_MEMBERSHIP_REGISTRY", missing_memberships)
    grounded_record = record()
    evidence_id = grounded_record["canonical_examples"][0]["trait_occurrences"][0][
        "source_evidence_id"
    ]
    trait_path = tmp_path / "localized.yaml"
    trait_path.write_text(yaml.safe_dump(grounded_record, sort_keys=False), encoding="utf-8")
    registry_path = tmp_path / "registry.jsonl"
    registry_path.write_text(json.dumps(reference()) + "\n", encoding="utf-8")
    evidence_path = tmp_path / "evidence.jsonl"
    evidence_path.write_text(json.dumps(EVIDENCE_REGISTRY[evidence_id]) + "\n", encoding="utf-8")
    output = tmp_path / "validation.tsv"

    assert (
        V.main(
            [
                str(trait_path),
                "--registry",
                str(registry_path),
                "--evidence-registry",
                str(evidence_path),
                "--out",
                str(output),
                "--quiet",
            ]
        )
        == 0
    )
    assert "membership_registry_not_found" not in output.read_text(encoding="utf-8")


def test_cli_builds_authoritative_hierarchy_from_trait_inputs(tmp_path):
    registry_path = tmp_path / "registry.jsonl"
    registry_path.write_text(json.dumps(reference()) + "\n", encoding="utf-8")
    inherited = occurrence(
        source_trait_id="PROSITE:PS_CHILD",
        inheritance_path=["PROSITE:PS_CHILD", "PROSITE:PS00001"],
    )
    inherited_record = record(canonical_examples=[example(trait_occurrences=[inherited])])
    evidence_path = tmp_path / "evidence.jsonl"
    evidence_path.write_text(
        json.dumps(EVIDENCE_REGISTRY[inherited["source_evidence_id"]]) + "\n",
        encoding="utf-8",
    )
    (tmp_path / "parent.yaml").write_text(
        yaml.safe_dump(inherited_record, sort_keys=False), encoding="utf-8"
    )
    (tmp_path / "child.yaml").write_text(
        yaml.safe_dump(
            {
                "identifier": "PROSITE:PS_CHILD",
                "label": "child",
                "trait_axis": "SEQUENCE",
                "parent_traits": ["PROSITE:PS00001"],
            }
        ),
        encoding="utf-8",
    )
    output = tmp_path / "validation.tsv"
    assert (
        V.main(
            [
                str(tmp_path),
                "--registry",
                str(registry_path),
                "--evidence-registry",
                str(evidence_path),
                "--out",
                str(output),
                "--quiet",
            ]
        )
        == 0
    )
    assert output.read_text(encoding="utf-8").count("\n") == 1


def test_a_deletion_only_file_list_is_not_a_failure(tmp_path, capsys):
    """CI's changed-file list can name only deleted records (#616).

    validate_strict.py grew `--allow-missing` for exactly this (#540). Once the
    grounding validator runs beside it on the same list, the two have to agree
    about what a deletion-only diff means, or a PR that only removes records goes
    red on the half that lacks the flag.
    """
    missing = tmp_path / "gone.yaml"
    assert V.main(["--allow-missing", str(missing)]) == 0
    assert "nothing to validate" in capsys.readouterr().err


def test_a_mistyped_path_still_fails_without_the_flag(tmp_path):
    """Opt in, do not assume: a human typing a wrong path must not see success.

    Returning 0 for a path that was never read would report "validated" about a
    file that does not exist -- the weakening #540 explicitly refused.
    """
    assert V.main([str(tmp_path / "gone.yaml")]) == 2


def test_the_flag_does_not_mask_an_empty_corpus(tmp_path, monkeypatch):
    """`--allow-missing` covers supplied paths, never a default scan.

    With no paths the validator scans the corpus root; if that finds nothing the
    checkout is broken, and exiting 0 there would be the fail-open shape of #573
    -- green because it looked at nothing.
    """
    monkeypatch.setattr(V, "DEFAULT_TRAITS", tmp_path / "empty-traits")
    assert V.main(["--allow-missing"]) == 2
