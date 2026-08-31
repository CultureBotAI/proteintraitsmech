"""Scientific and adversarial tests for the no-write ELM source-native stage."""

from __future__ import annotations

import hashlib
import importlib
import json
import sys
from pathlib import Path
from typing import Any, Mapping

import pytest
import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

stage = importlib.import_module("stage_elm_source_native_grounding")
grounding = importlib.import_module("validate_uniprot_grounding")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_export(
    path: Path,
    *,
    metadata: list[tuple[str, str]],
    columns: tuple[str, ...],
    rows: list[list[str]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = b"".join(f"#{key}: {value}\n".encode() for key, value in metadata)
    raw += ("\t".join(f'"{item}"' for item in columns) + "\r\n").encode()
    for row in rows:
        assert len(row) == len(columns)
        raw += ("\t".join(f'"{item}"' for item in row) + "\r\n").encode()
    path.write_bytes(raw)


def _class_row(
    accession: str,
    identifier: str,
    expression: str,
    *,
    instances: int,
    pdb_instances: int = 0,
) -> list[str]:
    return [
        accession,
        identifier,
        "Fixture site",
        "Fixture description",
        expression,
        "0.01",
        str(instances),
        str(pdb_instances),
    ]


def _instance_row(
    accession: str,
    elm_type: str,
    identifier: str,
    primary: str,
    start: int,
    end: int,
    logic: str,
    *,
    aliases: str | None = None,
    organism: str = "Homo sapiens",
    references: str = "12345",
    methods: str = "mutation analysis; western blot",
    pdb: str = "",
) -> list[str]:
    return [
        accession,
        elm_type,
        identifier,
        f"{primary}_FIXTURE",
        primary,
        aliases or primary,
        str(start),
        str(end),
        references,
        methods,
        logic,
        pdb,
        organism,
    ]


def _trait_record(
    elm_class: stage.ElmClass,
    selected: list[tuple[stage.ElmInstance, str | None]],
) -> dict[str, Any]:
    category, _ = stage.ROUTE[elm_class.prefix]
    record: dict[str, Any] = {
        "identifier": elm_class.trait_id,
        "label": elm_class.identifier,
        "definition": stage._expected_trait_definition(elm_class),
        "definition_source": "ELM (Eukaryotic Linear Motif resource)",
        "trait_axis": "SEQUENCE",
        "trait_category": category,
        "term_kind": "CLASS",
        "mapping_status": "SEEDED",
        "sequence_pattern": elm_class.regex,
        "license": stage.TRAIT_LICENSE,
    }
    if selected:
        examples = []
        for source, sequence in selected:
            example: dict[str, Any] = {
                "protein_id": source.protein_id,
                "protein_label": source.protein_name,
                "taxon_label": source.organism_label,
                "note": "ELM true-positive instance",
                "source": "CURATOR",
                "features": [
                    {
                        "start": source.start,
                        "end": source.end,
                        "feature_type": "MOTIF",
                        "trait_axis": "SEQUENCE",
                        "trait_category": category,
                    }
                ],
            }
            if sequence is not None:
                example["sequence"] = sequence
            examples.append(example)
        record["canonical_examples"] = examples
    return record


def _reference(
    protein_id: str,
    sequence: str,
    *,
    taxon_label: str = "Homo sapiens",
) -> dict[str, Any]:
    value: dict[str, Any] = {
        "protein_id": protein_id,
        "protein_label": f"{protein_id} fixture",
        "taxon_id": "NCBITaxon:9606",
        "taxon_label": taxon_label,
        "sequence": sequence,
        "sequence_length": len(sequence),
        "sequence_sha256": hashlib.sha256(sequence.encode()).hexdigest(),
        "sequence_version": 1,
        "reviewed": True,
        "uniprot_release": "2026_02",
    }
    if "-" in protein_id.split(":", 1)[1]:
        value["isoform"] = int(protein_id.rsplit("-", 1)[1])
    return value


def _write_registry(path: Path, references: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(stage.canonical_json(item) + "\n" for item in references),
        encoding="utf-8",
    )


def _case(tmp_path: Path) -> dict[str, Any]:
    repo = tmp_path / "repo"
    classes_path = repo / "data/raw/elm/elm_classes.tsv"
    instances_path = repo / "data/raw/elm/elm_instances.tsv"
    traits_root = repo / "data/traits"
    registry_path = repo / "data/grounding/protein_registry.jsonl"

    class_rows = [
        _class_row("ELME000001", "LIG_TEST_1", "P.{2,5}P", instances=5),
        _class_row("ELME000002", "TRG_CEND_1", "P..P$", instances=1),
    ]
    instance_rows = [
        _instance_row("ELMI000001", "LIG", "LIG_TEST_1", "P12345", 2, 5, "true positive"),
        _instance_row("ELMI000002", "LIG", "LIG_TEST_1", "P99999", 2, 5, "false positive"),
        _instance_row(
            "ELMI000003",
            "LIG",
            "LIG_TEST_1",
            "Q11111-2",
            2,
            5,
            "true positive",
            aliases="Q11111 Q99999",
        ),
        _instance_row(
            "ELMI000004",
            "LIG",
            "LIG_TEST_1",
            "Q22222",
            2,
            5,
            "true positive",
            organism="Mus musculus",
        ),
        _instance_row("ELMI000005", "LIG", "LIG_TEST_1", "Q33333", 2, 6, "true positive"),
        _instance_row("ELMI000006", "TRG", "TRG_CEND_1", "Q44444", 2, 5, "true positive"),
    ]
    _write_export(
        classes_path,
        metadata=[
            ("ELM_Classes_Download_Version", "1.4"),
            ("ELM_Classes_Download_Date", "2026-07-03 14:22:05.578160"),
            ("Origin", "asimov"),
            ("Type", "tsv"),
            ("Num_Classes", "2"),
        ],
        columns=stage.CLASS_COLUMNS,
        rows=class_rows,
    )
    _write_export(
        instances_path,
        metadata=[
            ("ELM_Instance_Download_Version", "1.4"),
            ("ELM_Instance_Download_Date", "2026-07-03 16:15:11.938794"),
            ("Origin", "asimov"),
            ("Type", "tsv"),
            ("NumInstances", "6"),
        ],
        columns=stage.INSTANCE_COLUMNS,
        rows=instance_rows,
    )
    classes_artifact = stage.CapturedArtifact(
        classes_path,
        "data/raw/elm/elm_classes.tsv",
        _sha256(classes_path),
        classes_path.read_bytes(),
    )
    _, classes = stage.parse_classes(classes_artifact)
    instances_artifact = stage.CapturedArtifact(
        instances_path,
        "data/raw/elm/elm_instances.tsv",
        _sha256(instances_path),
        instances_path.read_bytes(),
    )
    _, instances = stage.parse_instances(instances_artifact, classes)
    by_identifier = {item.identifier: item for item in classes}
    selected = stage._selected_by_class(instances)
    inline_sequences = {
        "P12345": "MPAAPXXP",
        "Q11111-2": "MPXXPXXP",
        "Q22222": "MPAAPXXP",
        "Q33333": "MPAAPXXP",
        "Q44444": "MPAAPQQ",
    }
    for subdir in {route[1] for route in stage.ROUTE.values()}:
        (traits_root / "sequence" / subdir / "elm").mkdir(parents=True, exist_ok=True)
    for elm_class in classes:
        source_examples = selected.get(elm_class.identifier, ())
        record = _trait_record(
            elm_class,
            [(item, inline_sequences.get(item.primary_accession)) for item in source_examples],
        )
        path = stage._expected_trait_path(traits_root, elm_class)
        path.write_text(yaml.safe_dump(record, sort_keys=False), encoding="utf-8")
    references = [
        _reference("UniProtKB:P12345", "MPAAPXXP"),
        _reference("UniProtKB:Q22222", "MPAAPXXP", taxon_label="Homo sapiens"),
        _reference("UniProtKB:Q33333", "MPAAPXXP"),
        _reference("UniProtKB:Q44444", "MPAAPQQ"),
    ]
    _write_registry(registry_path, references)
    return {
        "repo": repo,
        "classes": classes_path,
        "instances": instances_path,
        "traits": traits_root,
        "registry": registry_path,
        "pins": {"classes": _sha256(classes_path), "instances": _sha256(instances_path)},
        "references": {item["protein_id"]: item for item in references},
        "class_by_identifier": by_identifier,
    }


def _build(case: Mapping[str, Any]) -> stage.StageResult:
    return stage.build_stage(
        classes_path=case["classes"],
        instances_path=case["instances"],
        traits_root=case["traits"],
        protein_registry_path=case["registry"],
        repo_root=case["repo"],
        expected_source_sha256=case["pins"],
    )


def _row(result: stage.StageResult, accession: str) -> dict[str, Any]:
    return next(
        row
        for row in result.occurrences
        if row["source_binding"]["elm_instance_accession"] == accession
    )


def _assert_content_address(
    row: dict[str, Any], *, id_field: str, prefix: str, row_hash_field: str
) -> None:
    without_row_hash = dict(row)
    observed_row_hash = without_row_hash.pop(row_hash_field)
    assert observed_row_hash == stage.value_sha256(without_row_hash)
    observed_id = without_row_hash.pop(id_field)
    assert observed_id == prefix + stage.value_sha256(without_row_hash)


def test_stage_partitions_logic_references_patterns_and_primary_isoform(tmp_path: Path) -> None:
    result = _build(_case(tmp_path))
    assert result.summary["class_count"] == 2
    assert result.summary["instance_count"] == 6
    assert result.summary["instance_logic_counts"] == {
        "false positive": 1,
        "true positive": 5,
    }
    assert result.summary["legacy_selected_example_count"] == 5
    assert result.summary["local_registry_sequence_match_candidate_count"] == 1
    assert result.summary["grounding_evidence_emitted_count"] == 0
    assert result.summary["missing_protein_reference_request_count"] == 1

    exact = _row(result, "ELMI000001")
    assert exact["grounding_status"] == "SEQUENCE_MATCHED_STAGING_ONLY_MISSING_RECEIPTS"
    assert exact["local_registry_sequence_evaluation"]["status"] == (
        "EXACT_REGEX_SPAN_IN_COMPLETE_PROTEIN"
    )
    assert exact["promotion_blockers"] == sorted(
        {
            stage.MISSING_ACQUISITION_RECEIPT,
            stage.MISSING_VERIFIED_PROTEIN_REGISTRY_RECEIPT,
        }
    )
    assert exact["local_registry_sequence_match_candidate"] is not None
    assert not exact["grounding_evidence_emitted"]

    false_positive = _row(result, "ELMI000002")
    assert false_positive["grounding_status"] == "EXCLUDED_NON_TRUE_POSITIVE_SOURCE_LOGIC"
    assert false_positive["local_registry_sequence_match_candidate"] is None
    assert "UniProtKB:P99999" not in {request["protein_id"] for request in result.protein_requests}

    missing_isoform = _row(result, "ELMI000003")
    assert missing_isoform["source_binding"]["protein_id"] == "UniProtKB:Q11111-2"
    assert not missing_isoform["source_binding"]["primary_accession_present_in_aliases"]
    request = result.protein_requests[0]
    assert request["protein_id"] == "UniProtKB:Q11111-2"
    assert request["coordinate_frame"] == "UNIPROT_ISOFORM"
    assert request["expected_uniprot_release"] == stage.EXPECTED_UNIPROT_RELEASE

    taxon = _row(result, "ELMI000004")
    assert stage.TAXON_LABEL_REVIEW in taxon["promotion_blockers"]
    width = _row(result, "ELMI000005")
    assert width["local_registry_sequence_evaluation"]["status"] == (
        "REGEX_SUBSPAN_WITHIN_SOURCE_INTERVAL"
    )
    assert stage.PATTERN_WIDTH_REVIEW in width["promotion_blockers"]
    terminal = _row(result, "ELMI000006")
    assert terminal["local_registry_sequence_evaluation"]["status"] == (
        "NO_REGEX_MATCH_IN_COMPLETE_PROTEIN"
    )
    assert stage.PATTERN_SEQUENCE_REVIEW in terminal["promotion_blockers"]


def test_local_registry_candidate_cannot_bypass_missing_receipts(tmp_path: Path) -> None:
    case = _case(tmp_path)
    result = _build(case)
    row = _row(result, "ELMI000001")
    candidate = row["local_registry_sequence_match_candidate"]
    assert candidate["qualification_status"] == "CANDIDATE_ONLY"
    assert candidate["qualification_blockers"] == sorted(
        {
            stage.MISSING_ACQUISITION_RECEIPT,
            stage.MISSING_VERIFIED_PROTEIN_REGISTRY_RECEIPT,
        }
    )
    assert candidate["source_evidence_id"] is None
    assert candidate["source_interval"] == {"start": 2, "end": 5}
    assert candidate["resolved_interval_sequence"] == "PAAP"
    assert candidate["resolved_interval_sequence_sha256"] == hashlib.sha256(b"PAAP").hexdigest()
    assert candidate["resolved_interval_sequence_origin"] == (
        "LOCAL_PROTEIN_REFERENCE_NOT_ELM_EXPORT"
    )
    assert candidate["resolved_protein_uniprot_release"] == stage.EXPECTED_UNIPROT_RELEASE
    assert candidate["candidate_kind"] == "ELM_LOCAL_REGISTRY_SEQUENCE_MATCH"
    assert not {"intervals", "expected_sequence", "sequence_sha256", "source_release"}.intersection(
        candidate
    )
    occurrence = {
        field: candidate[field]
        for field in grounding.OCCURRENCE_EVIDENCE_FIELDS
        if field in candidate
    }
    occurrence.update(
        {
            "qualification_status": "QUALIFIED",
            "source_evidence_id": None,
        }
    )
    reference = case["references"]["UniProtKB:P12345"]
    example = {
        field: reference[field]
        for field in (
            "protein_id",
            "protein_label",
            "taxon_id",
            "taxon_label",
            "sequence_length",
            "sequence_sha256",
            "uniprot_release",
        )
    }
    example.update(
        {
            "qualification_status": "QUALIFIED",
            "source": "UNIPROT_GROUNDING",
            "trait_occurrences": [occurrence],
        }
    )
    record = {
        "identifier": "ELM:ELME000001",
        "label": "LIG_TEST_1",
        "trait_axis": "SEQUENCE",
        "trait_category": "SEQ_MOTIF",
        "sequence_pattern": "P.{2,5}P",
        "canonical_examples": [example],
    }
    observed = {
        finding.code
        for finding in grounding.validate_record(
            record,
            {reference["protein_id"]: reference},
            require_qualified=True,
        )
    }
    assert "qualified_occurrence_without_evidence" in observed


def test_render_is_canonical_content_addressed_and_no_write(tmp_path: Path) -> None:
    case = _case(tmp_path)
    before = {
        path.relative_to(case["repo"]).as_posix(): _sha256(path)
        for path in case["repo"].rglob("*")
        if path.is_file() and not path.is_symlink()
    }
    result = _build(case)
    rendered = stage.render_stage(result)
    assert stage.render_stage(_build(case)) == rendered
    decoded = [json.loads(line) for line in rendered.splitlines()]
    assert decoded == [*result.occurrences, *result.protein_requests, result.summary]
    assert stage.render_stage(result, summary_only=True) == (
        stage.canonical_json(result.summary) + "\n"
    )
    for row in result.occurrences:
        _assert_content_address(
            row,
            id_field="occurrence_stage_id",
            prefix="elm-source-occurrence:",
            row_hash_field="occurrence_row_sha256",
        )
    for row in result.protein_requests:
        _assert_content_address(
            row,
            id_field="request_id",
            prefix="elm-protein-request:",
            row_hash_field="request_row_sha256",
        )
    _assert_content_address(
        result.summary,
        id_field="stage_id",
        prefix="elm-source-native-stage:",
        row_hash_field="summary_row_sha256",
    )
    after = {
        path.relative_to(case["repo"]).as_posix(): _sha256(path)
        for path in case["repo"].rglob("*")
        if path.is_file() and not path.is_symlink()
    }
    assert after == before


def test_source_and_trait_contracts_fail_closed(tmp_path: Path) -> None:
    bad_type = _case(tmp_path / "bad-type")
    raw = bad_type["instances"].read_bytes().replace(b'"LIG"', b'"TRG"', 1)
    bad_type["instances"].write_bytes(raw)
    bad_type["pins"]["instances"] = _sha256(bad_type["instances"])
    with pytest.raises(stage.ElmStageError, match="missing/mismatched class binding"):
        _build(bad_type)

    duplicate_key = _case(tmp_path / "duplicate-key")
    trait = stage._expected_trait_path(
        duplicate_key["traits"], duplicate_key["class_by_identifier"]["LIG_TEST_1"]
    )
    trait.write_text(trait.read_text() + "identifier: ELM:ELME000001\n", encoding="utf-8")
    with pytest.raises(stage.ElmStageError, match="duplicate key"):
        _build(duplicate_key)

    shadow = _case(tmp_path / "shadow")
    shadow_path = shadow["traits"] / "sequence/motif/other/shadow.yaml"
    shadow_path.parent.mkdir(parents=True)
    shadow_path.write_text("identifier: ELM:ELME000001\n", encoding="utf-8")
    with pytest.raises(stage.ElmStageError, match="outside its exact source-derived path"):
        _build(shadow)


def test_trait_definition_and_legacy_grounding_fields_fail_closed(tmp_path: Path) -> None:
    whitespace_case = _case(tmp_path / "definition-whitespace")
    whitespace_path = stage._expected_trait_path(
        whitespace_case["traits"],
        whitespace_case["class_by_identifier"]["LIG_TEST_1"],
    )
    whitespace_record = yaml.safe_load(whitespace_path.read_text(encoding="utf-8"))
    whitespace_record["definition"] = "  Fixture   site  —  Fixture description  "
    whitespace_path.write_text(yaml.safe_dump(whitespace_record, sort_keys=False), encoding="utf-8")
    _build(whitespace_case)

    definition_case = _case(tmp_path / "definition")
    definition_path = stage._expected_trait_path(
        definition_case["traits"],
        definition_case["class_by_identifier"]["LIG_TEST_1"],
    )
    definition_record = yaml.safe_load(definition_path.read_text(encoding="utf-8"))
    definition_record["definition"] = "Forged definition"
    definition_path.write_text(yaml.safe_dump(definition_record, sort_keys=False), encoding="utf-8")
    with pytest.raises(stage.ElmStageError, match="trait contract mismatch for definition"):
        _build(definition_case)

    qualified_case = _case(tmp_path / "prequalified")
    qualified_path = stage._expected_trait_path(
        qualified_case["traits"],
        qualified_case["class_by_identifier"]["LIG_TEST_1"],
    )
    qualified_record = yaml.safe_load(qualified_path.read_text(encoding="utf-8"))
    qualified_record["canonical_examples"][0]["qualification_status"] = "QUALIFIED"
    qualified_record["canonical_examples"][0]["sequence_sha256"] = "0" * 64
    qualified_path.write_text(yaml.safe_dump(qualified_record, sort_keys=False), encoding="utf-8")
    with pytest.raises(stage.ElmStageError, match="forbidden grounding fields"):
        _build(qualified_case)

    unexpected_case = _case(tmp_path / "unexpected")
    unexpected_path = stage._expected_trait_path(
        unexpected_case["traits"],
        unexpected_case["class_by_identifier"]["LIG_TEST_1"],
    )
    unexpected_record = yaml.safe_load(unexpected_path.read_text(encoding="utf-8"))
    unexpected_record["canonical_examples"][0]["unexpected_field"] = "drift"
    unexpected_path.write_text(yaml.safe_dump(unexpected_record, sort_keys=False), encoding="utf-8")
    with pytest.raises(stage.ElmStageError, match="unexpected legacy fields"):
        _build(unexpected_case)


def test_registry_rows_must_share_the_expected_uniprot_release(tmp_path: Path) -> None:
    case = _case(tmp_path)
    references = [dict(item) for item in case["references"].values()]
    references[1]["uniprot_release"] = "2026_01"
    _write_registry(case["registry"], references)
    with pytest.raises(stage.ElmStageError, match="does not equal expected UniProt release"):
        _build(case)


def test_source_and_trait_symlinks_are_rejected(tmp_path: Path) -> None:
    source_case = _case(tmp_path / "source")
    source = source_case["instances"]
    original = source.with_suffix(".original")
    source.rename(original)
    source.symlink_to(original)
    with pytest.raises(stage.ElmStageError, match="without following symlinks"):
        _build(source_case)

    trait_case = _case(tmp_path / "trait")
    external = tmp_path / "external.yaml"
    external.write_text("identifier: ELM:ELME999999\n", encoding="utf-8")
    (trait_case["traits"] / "linked.yaml").symlink_to(external)
    with pytest.raises(stage.ElmStageError, match="symlink below trait directory"):
        _build(trait_case)


def test_cli_has_no_apply_or_output_mode() -> None:
    with pytest.raises(SystemExit):
        stage.parse_args(["--apply"])
    with pytest.raises(SystemExit):
        stage.parse_args(["--out", "forbidden.jsonl"])


def test_production_elm_snapshot_when_artifacts_exist() -> None:
    required = [
        stage.DEFAULT_CLASSES,
        stage.DEFAULT_INSTANCES,
        stage.DEFAULT_TRAITS_ROOT,
        stage.DEFAULT_PROTEIN_REGISTRY,
    ]
    if not all(path.exists() for path in required):
        pytest.skip("ignored production ELM/grounding artifacts are unavailable")
    result = stage.build_stage()
    summary = result.summary
    assert summary["class_count"] == 353
    assert summary["class_type_counts"] == {
        "CLV": 11,
        "DEG": 33,
        "DOC": 42,
        "LIG": 199,
        "MOD": 40,
        "TRG": 28,
    }
    assert summary["instance_count"] == 4_277
    assert summary["instance_logic_counts"] == {
        "false positive": 73,
        "true negative": 33,
        "true positive": 4_047,
        "unknown": 124,
    }
    assert summary["legacy_selected_example_count"] == 2_774
    assert summary["legacy_selected_inline_sequence_count"] == 2_742
    assert summary["legacy_cap_omitted_true_positive_count"] == 1_273
    assert summary["true_positive_unique_protein_count"] == 2_605
    assert summary["true_positive_isoform_instance_count"] == 96
    assert summary["missing_protein_reference_request_count"] == 2_599
    assert summary["expected_uniprot_release"] == stage.EXPECTED_UNIPROT_RELEASE
    assert summary["protein_registry"]["role"] == (
        "LOCAL_PROTEIN_REFERENCE_REGISTRY_WITHOUT_FETCH_RECEIPT_BINDING"
    )
    assert summary["protein_registry_fetch_receipt_verification_status"] == (
        "NOT_VERIFIED_BY_THIS_STAGE"
    )
    assert summary["local_registry_sequence_match_candidate_count"] == 9
    assert summary["grounding_evidence_emitted_count"] == 0
    assert summary["local_registry_true_positive_pattern_status_counts"] == {
        "EXACT_REGEX_SPAN_IN_COMPLETE_PROTEIN": 9,
        "NO_EXACT_PROTEIN_REFERENCE": 4_038,
    }
    assert summary["source_snapshot"]["source_snapshot_id"] == (
        "elm-source-snapshot:986d677b81851ceeb339b02e9c00a8541323365ca2d1bb2046a3491e8565aadd"
    )
    assert summary["trait_binding_rows_sha256"] == (
        "653b23d0dd60bd6fc43386c80987b596203efa70bdb0f553736e0521b14c28fe"
    )
    assert summary["occurrence_rows_sha256"] == (
        "ab49eb78d5a5d320619f1cdd745a68a0fe22951314d34a401685fa0f7920a9cb"
    )
    assert summary["protein_request_rows_sha256"] == (
        "c7f1282dac56d6af8616a167933e2b38c6d5169f147fc843012de4127572a869"
    )
    assert summary["combined_non_summary_rows_sha256"] == (
        "a330a9c651321c632080025eaebed97631b73c10d9e6204fb8f3f6b45cb932f8"
    )
    assert summary["stage_id"] == (
        "elm-source-native-stage:7c518e862c108773f83d0ab1bf8aa70ace75b51c0a43658eacf06d937f90ab0d"
    )
