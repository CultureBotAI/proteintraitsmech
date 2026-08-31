from __future__ import annotations

import hashlib
import importlib
import json
import os
import sys
from pathlib import Path
from typing import Any

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
stage = importlib.import_module("stage_cath_grounding_candidates")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _canonical_file(path: Path, value: Any) -> None:
    _write(path, stage.canonical_json(value))


def _registry_row(accession: str = "P12345", sequence: str = "ACDEFG") -> dict[str, Any]:
    return {
        "protein_id": f"UniProtKB:{accession}",
        "protein_label": f"Fixture {accession}",
        "reviewed": True,
        "sequence": sequence,
        "sequence_length": len(sequence),
        "sequence_sha256": hashlib.sha256(sequence.encode("ascii")).hexdigest(),
        "sequence_version": 1,
        "taxon_id": "NCBITaxon:9606",
        "taxon_label": "Homo sapiens",
        "uniprot_release": stage.EXPECTED_UNIPROT_RELEASE,
    }


def _write_registry(path: Path, rows: list[dict[str, Any]]) -> None:
    _write(path, "".join(stage.canonical_json(row) + "\n" for row in rows))


def _names_text() -> str:
    return """#---------------------------------------------------------------------
# FILE NAME:    CathNames.v4.4.0
# FILE DATE:    16.12.2024
# CATH VERSION: v4.4.0
# VERSION DATE: 16.12.2024
# FILE FORMAT:  Cath Names File (CNF) Format 2.0
#---------------------------------------------------------------------
1    1aaaA00    :Mainly Alpha
1.10    1aabA00    :Orthogonal Bundle
1.10.20    1aacA00    :Test topology
1.10.20.30    1aadA00    :No-example family
1.10.20.40    1aaeA00    :Existing-example family
1.10.20.50    ???????    :
"""


def _trait_text(
    code: str,
    label: str,
    representative: str,
    category: str,
    *,
    examples: bool = False,
) -> str:
    parts = code.split(".")
    rows = [
        f"identifier: CATH:{code}",
        f'label: "{label}"',
        "definition: test definition",
        "definition_source: CATH",
        "trait_axis: STRUCTURE",
        f"trait_category: {category}",
        "term_kind: CLASS",
        "mapping_status: SEEDED",
    ]
    if len(parts) > 1:
        rows.extend(["parent_traits:", f"  - CATH:{'.'.join(parts[:-1])}"])
    if representative != "???????":
        rows.extend(
            [
                "xrefs:",
                f"  - CATH:{representative}",
                "structural_geometry_representations:",
                f"- structure_ref: PDB:{representative[:4]}",
                "  structure_source: CATH",
                (
                    "  evidence_source: CATH representative domain "
                    f"{representative} (chain {representative[4]})"
                ),
            ]
        )
    if examples:
        rows.extend(
            [
                "canonical_examples:",
                "  - protein_id: UniProtKB:P99999",
            ]
        )
    rows.append("license: CC-BY 4.0")
    return "\n".join(rows) + "\n"


def _case(tmp_path: Path) -> dict[str, Any]:
    repo = tmp_path / "repo"
    names = repo / "data/raw/cath/cath-names.txt"
    interpro = repo / "data/raw/align_cache/interpro_frame.json"
    residue = repo / "data/raw/align_cache/residue_frame.json"
    registry = repo / "data/grounding/protein_registry.jsonl"
    traits = repo / "data/traits"
    _write(names, _names_text())
    definitions = [
        ("structure/class/cath/one.yaml", "1", "Mainly Alpha", "1aaaA00", "STRUCT_CLASS", False),
        (
            "structure/architecture/cath/one-ten.yaml",
            "1.10",
            "Orthogonal Bundle",
            "1aabA00",
            "STRUCT_ARCHITECTURE",
            False,
        ),
        (
            "structure/topology/cath/one-ten-twenty.yaml",
            "1.10.20",
            "Test topology",
            "1aacA00",
            "STRUCT_TOPOLOGY",
            False,
        ),
        (
            "structure/homologous_superfamily/cath/no-example.yaml",
            "1.10.20.30",
            "No-example family",
            "1aadA00",
            "STRUCT_HOMOLOGOUS_SUPERFAMILY",
            False,
        ),
        (
            "structure/homologous_superfamily/cath/existing.yaml",
            "1.10.20.40",
            "Existing-example family",
            "1aaeA00",
            "STRUCT_HOMOLOGOUS_SUPERFAMILY",
            True,
        ),
        (
            "structure/homologous_superfamily/cath/placeholder.yaml",
            "1.10.20.50",
            "CATH homologous superfamily 1.10.20.50",
            "???????",
            "STRUCT_HOMOLOGOUS_SUPERFAMILY",
            False,
        ),
    ]
    for relative, code, label, representative, category, examples in definitions:
        _write(
            traits / relative,
            _trait_text(
                code,
                label,
                representative,
                category,
                examples=examples,
            ),
        )
    _canonical_file(
        interpro,
        {
            "_meta": {
                "schema": 1,
                "built": "2026-07-27",
                "source": "InterPro",
                "release": "109.0",
                "count": 3,
            },
            "proteins": {
                "P12345": {"CATH:1.10.20.30": [[1, 4]], "InterPro:IPR000001": [[1, 4]]},
                "P23456": {"CATH:1.10.20.30": [[1, 2], [4, 6]]},
                "Q12345": {"CATH:1.10.20.30": [[2, 5]]},
            },
        },
    )
    _canonical_file(
        residue,
        {
            "_meta": {
                "schema": 1,
                "built": "2026-07-27",
                "source": "UniProt",
                "release": "2026_02",
                "count": 3,
                "absent": [],
            },
            "proteins": {
                "P12345": {"seq": "ACDEFG", "ft": []},
                "P23456": {"seq": "ACDEFG", "ft": []},
                "Q12345": {"seq": "ACDEFG", "ft": []},
            },
        },
    )
    _write_registry(registry, [_registry_row()])
    pins = {
        "cath_names": hashlib.sha256(names.read_bytes()).hexdigest(),
        "interpro_frame": hashlib.sha256(interpro.read_bytes()).hexdigest(),
        "residue_frame": hashlib.sha256(residue.read_bytes()).hexdigest(),
    }
    counts = {
        "cath_name_count": 6,
        "all_cath_trait_count": 6,
        "no_example_trait_count": 5,
        "native_exact_representative_count": 4,
        "native_placeholder_count": 1,
        "annotation_discovery_count": 3,
        "annotation_single_location_count": 2,
        "annotation_ungrouped_multi_location_count": 1,
        "annotation_unique_trait_count": 1,
        "annotation_unique_protein_count": 3,
        "protein_registry_row_count": 1,
        "annotation_exact_local_reference_count": 1,
        "annotation_missing_local_reference_count": 2,
        "annotation_exact_local_reference_unique_protein_count": 1,
        "annotation_missing_local_reference_unique_protein_count": 2,
        "protein_reference_request_count": 2,
        "protein_reference_request_unique_protein_count": 2,
        "protein_reference_request_multi_observation_count": 0,
        "protein_reference_request_max_observation_count": 1,
    }
    return {
        "repo": repo,
        "names": names,
        "interpro": interpro,
        "residue": residue,
        "registry": registry,
        "traits": traits,
        "pins": pins,
        "registry_pin": hashlib.sha256(registry.read_bytes()).hexdigest(),
        "counts": counts,
    }


def _build(case: dict[str, Any]) -> stage.StageResult:
    return stage.build_stage(
        cath_names_path=case["names"],
        interpro_frame_path=case["interpro"],
        residue_frame_path=case["residue"],
        traits_root=case["traits"],
        protein_registry_path=case["registry"],
        repo_root=case["repo"],
        expected_source_sha256=case["pins"],
        expected_protein_registry_sha256=case["registry_pin"],
        expected_counts=case["counts"],
    )


def _repin_registry(case: dict[str, Any]) -> None:
    case["registry_pin"] = hashlib.sha256(case["registry"].read_bytes()).hexdigest()


def _assert_address(row: dict[str, Any], id_field: str, prefix: str, hash_field: str) -> None:
    value = dict(row)
    row_hash = value.pop(hash_field)
    identifier = value.pop(id_field)
    assert identifier == prefix + stage.value_sha256(value)
    value[id_field] = identifier
    assert row_hash == stage.value_sha256(value)


def test_annotation_discoveries_and_native_blockers_are_disjoint(tmp_path: Path) -> None:
    case = _case(tmp_path)
    result = _build(case)

    assert len(result.annotation_discoveries) == 3
    assert [row["protein_id"] for row in result.annotation_discoveries] == [
        "UniProtKB:P12345",
        "UniProtKB:P23456",
        "UniProtKB:Q12345",
    ]
    assert {row["trait_id"] for row in result.annotation_discoveries} == {"CATH:1.10.20.30"}
    assert all(not row["qualification_claimed"] for row in result.annotation_discoveries)
    assert all(
        row["evidence_class"] == "INTERPRO_GENE3D_ANNOTATION_NOT_NATIVE_CATH_PDB_EVIDENCE"
        for row in result.annotation_discoveries
    )
    assert [row["stage_status"] for row in result.annotation_discoveries] == [
        stage.SINGLE_LOCATION_STATUS,
        stage.UNGROUPED_MULTI_STATUS,
        stage.SINGLE_LOCATION_STATUS,
    ]
    multi = result.annotation_discoveries[1]
    assert multi["intervals"] == [{"start": 1, "end": 2}, {"start": 4, "end": 6}]
    assert stage.UNGROUPED_REASON in multi["blocking_reasons"]
    assert stage.MISSING_PROTEIN_REFERENCE in multi["blocking_reasons"]
    assert (
        stage.MISSING_PROTEIN_REFERENCE not in result.annotation_discoveries[0]["blocking_reasons"]
    )
    assert result.annotation_discoveries[0]["protein_reference_binding"]["status"] == (
        "EXACT_LOCAL_PROTEIN_REFERENCE_PRESENT"
    )
    assert result.annotation_discoveries[0]["candidate_status"] == stage.READY_LOCAL_REFERENCE
    assert all(
        row["protein_reference_binding"]["status"] == "MISSING_EXACT_PROTEIN_REFERENCE"
        for row in result.annotation_discoveries[1:]
    )
    assert all(
        row["candidate_status"] == stage.MISSING_LOCAL_PROTEIN_REFERENCE
        for row in result.annotation_discoveries[1:]
    )
    for row in result.annotation_discoveries:
        assert row["trait_binding"]["trait_record_path"].endswith("no-example.yaml")
        assert len(row["artifact_bindings"]) == 3
        assert row["schema_version"] == 2
        assert row["missing_receipts"] == list(stage.ANNOTATION_MISSING_RECEIPTS)
        assert row["grounding_evidence_emitted"] is False
        assert row["network_action_performed"] is False
        assert row["write_action_performed"] is False
        assert "mapping_method" not in row
        assert "sequence_sha256" not in row
        _assert_address(
            row,
            "annotation_discovery_id",
            "cath-gene3d-annotation-discovery:",
            "annotation_discovery_row_sha256",
        )

    assert len(result.native_blockers) == 5
    assert {row["trait_id"] for row in result.native_blockers} == {
        "CATH:1",
        "CATH:1.10",
        "CATH:1.10.20",
        "CATH:1.10.20.30",
        "CATH:1.10.20.50",
    }
    assert all(row["admitted_native_sources"] == [] for row in result.native_blockers)
    assert all(not row["qualification_claimed"] for row in result.native_blockers)
    assert all(
        stage.MISSING_BOUNDARIES_REASON in row["blocking_reasons"] for row in result.native_blockers
    )
    assert all(
        stage.MISSING_RESIDUE_SIFTS_REASON in row["blocking_reasons"]
        for row in result.native_blockers
    )
    placeholder = next(
        row for row in result.native_blockers if row["trait_id"] == "CATH:1.10.20.50"
    )
    assert placeholder["representative_domain"] is None
    assert placeholder["structure_id"] is None
    assert placeholder["blocking_reasons"][-1] == stage.MISSING_REPRESENTATIVE_REASON
    for row in result.native_blockers:
        assert row["missing_receipts"] == list(stage.NATIVE_MISSING_RECEIPTS)
        assert row["grounding_evidence_emitted"] is False
        assert row["network_action_performed"] is False
        assert row["write_action_performed"] is False
        _assert_address(
            row,
            "native_blocker_id",
            "cath-native-representative-blocker:",
            "native_blocker_row_sha256",
        )

    assert [row["protein_id"] for row in result.protein_requests] == [
        "UniProtKB:P23456",
        "UniProtKB:Q12345",
    ]
    p23456 = result.protein_requests[0]
    assert p23456["source_observation_count"] == 1
    assert p23456["source_interval_count"] == 2
    assert p23456["maximum_source_coordinate"] == 6
    assert p23456["protein_reference_binding"] == multi["protein_reference_binding"]
    assert p23456["source_observation_bindings"] == [stage._request_observation_binding(multi)]
    for request in result.protein_requests:
        assert request["request_reason"] == stage.MISSING_PROTEIN_REFERENCE
        assert request["grounding_evidence_emitted"] is False
        assert request["network_action_performed"] is False
        assert request["write_action_performed"] is False
        _assert_address(
            request,
            "request_id",
            "cath-protein-request:",
            "request_row_sha256",
        )

    assert result.summary["annotation_discovery_count"] == 3
    assert result.summary["annotation_single_location_count"] == 2
    assert result.summary["annotation_ungrouped_multi_location_count"] == 1
    assert result.summary["native_blocker_count"] == 5
    assert result.summary["protein_reference_request_count"] == 2
    assert result.summary["annotation_exact_local_reference_count"] == 1
    assert result.summary["annotation_missing_local_reference_count"] == 2
    assert result.summary["qualification_claimed"] is False
    assert result.summary["trait_tree_must_be_quiescent"] is True
    assert result.summary["trait_tree_verification_semantics"] == (
        "DESCRIPTOR_RELATIVE_NOFOLLOW_READS_WITH_REPEATED_MEMBERSHIP_AND_"
        "CONTENT_CHECKS_NOT_AN_ATOMIC_FILESYSTEM_SNAPSHOT"
    )


def test_request_aggregates_two_exact_observations_with_full_bindings(tmp_path: Path) -> None:
    case = _case(tmp_path)
    frame = json.loads(case["interpro"].read_text(encoding="utf-8"))
    frame["proteins"]["P23456"]["CATH:1.10.20.50"] = [[2, 5]]
    _canonical_file(case["interpro"], frame)
    case["pins"]["interpro_frame"] = hashlib.sha256(case["interpro"].read_bytes()).hexdigest()
    case["counts"].update(
        {
            "annotation_discovery_count": 4,
            "annotation_single_location_count": 3,
            "annotation_unique_trait_count": 2,
            "annotation_missing_local_reference_count": 3,
            "protein_reference_request_multi_observation_count": 1,
            "protein_reference_request_max_observation_count": 2,
        }
    )

    result = _build(case)
    request = next(
        row for row in result.protein_requests if row["protein_id"] == "UniProtKB:P23456"
    )
    observations = [
        row for row in result.annotation_discoveries if row["protein_id"] == "UniProtKB:P23456"
    ]

    assert request["source_observation_count"] == 2
    assert request["trait_count"] == 2
    assert request["source_interval_count"] == 3
    assert request["maximum_source_coordinate"] == 6
    assert request["source_annotation_discovery_ids"] == sorted(
        row["annotation_discovery_id"] for row in observations
    )
    expected_bindings = sorted(
        (stage._request_observation_binding(row) for row in observations),
        key=stage.canonical_json,
    )
    assert request["source_observation_bindings"] == expected_bindings
    assert all(
        set(binding)
        == {
            "annotation_discovery_id",
            "candidate_status",
            "trait_id",
            "intervals",
            "interpro_observation_sha256",
            "trait_binding",
            "source_name_binding",
        }
        for binding in request["source_observation_bindings"]
    )


def test_coarse_local_sifts_cannot_turn_native_blockers_into_evidence(tmp_path: Path) -> None:
    case = _case(tmp_path)
    before = _build(case)
    _canonical_file(
        case["repo"] / "data/raw/sifts/1aad.json",
        {"P12345": [{"pdb_start": 1, "pdb_end": 4, "uniprot_start": 1, "uniprot_end": 4}]},
    )
    after = _build(case)
    assert before.native_blockers == after.native_blockers
    assert before.annotation_discoveries == after.annotation_discoveries
    assert before.summary == after.summary
    assert all(row["admitted_native_sources"] == [] for row in after.native_blockers)


def test_all_trait_bindings_and_rows_are_content_and_path_bound(tmp_path: Path) -> None:
    case = _case(tmp_path)
    result = _build(case)
    summary = result.summary
    assert summary["all_cath_trait_count"] == 6
    assert summary["no_example_trait_count"] == 5
    assert summary["no_example_trait_category_counts"] == {
        "STRUCT_ARCHITECTURE": 1,
        "STRUCT_CLASS": 1,
        "STRUCT_HOMOLOGOUS_SUPERFAMILY": 2,
        "STRUCT_TOPOLOGY": 1,
    }
    assert [item["sha256"] for item in summary["source_artifacts"]] == [
        case["pins"]["cath_names"],
        case["pins"]["interpro_frame"],
        case["pins"]["residue_frame"],
    ]
    assert summary["protein_registry_artifact"]["sha256"] == case["registry_pin"]
    assert summary["protein_registry_artifact"]["size_bytes"] == len(case["registry"].read_bytes())
    assert summary["source_snapshot"]["provider_acquisition_receipts"] == {
        "CATH": None,
        "InterPro": None,
    }
    assert summary["source_snapshot"]["frame_generation_receipts"] == {
        "InterPro": None,
        "UniProt": None,
    }
    rendered = stage.render_stage(result)
    assert rendered == stage.render_stage(result)
    parsed = [json.loads(line) for line in rendered.splitlines()]
    assert parsed[-1] == summary
    assert len(parsed) == 3 + 5 + 2 + 1
    assert all(line == stage.canonical_json(json.loads(line)) for line in rendered.splitlines())
    assert stage.render_stage(result, summary_only=True) == stage.canonical_json(summary) + "\n"
    assert (
        summary["protein_request_rows_sha256"]
        == hashlib.sha256(
            "".join(stage.canonical_json(row) + "\n" for row in result.protein_requests).encode()
        ).hexdigest()
    )
    _assert_address(
        summary,
        "stage_id",
        "cath-grounding-discovery-stage:",
        "summary_row_sha256",
    )


def test_checksum_duplicate_key_route_and_shadow_guards(tmp_path: Path) -> None:
    case = _case(tmp_path)
    bad_pins = dict(case["pins"])
    bad_pins["cath_names"] = "0" * 64
    with pytest.raises(stage.CathStageError, match="sha256 mismatch"):
        stage.build_stage(
            cath_names_path=case["names"],
            interpro_frame_path=case["interpro"],
            residue_frame_path=case["residue"],
            traits_root=case["traits"],
            protein_registry_path=case["registry"],
            repo_root=case["repo"],
            expected_source_sha256=bad_pins,
            expected_protein_registry_sha256=case["registry_pin"],
            expected_counts=case["counts"],
        )

    outside = tmp_path / "outside-cath-names.txt"
    _write(outside, _names_text())
    outside_pins = dict(case["pins"])
    outside_pins["cath_names"] = hashlib.sha256(outside.read_bytes()).hexdigest()
    with pytest.raises(stage.CathStageError, match="escapes bound root"):
        stage.build_stage(
            cath_names_path=outside,
            interpro_frame_path=case["interpro"],
            residue_frame_path=case["residue"],
            traits_root=case["traits"],
            protein_registry_path=case["registry"],
            repo_root=case["repo"],
            expected_source_sha256=outside_pins,
            expected_protein_registry_sha256=case["registry_pin"],
            expected_counts=case["counts"],
        )

    original = case["interpro"].read_text()
    _write(case["interpro"], original.replace('"schema":1', '"schema":1,"schema":1'))
    case["pins"]["interpro_frame"] = hashlib.sha256(case["interpro"].read_bytes()).hexdigest()
    with pytest.raises(stage.CathStageError, match="duplicate key"):
        _build(case)

    case = _case(tmp_path / "wrong-route")
    moved = case["traits"] / "structure/topology/cath/no-example-shadow.yaml"
    _write(
        moved,
        _trait_text(
            "1.10.20.30",
            "No-example family",
            "1aadA00",
            "STRUCT_HOMOLOGOUS_SUPERFAMILY",
        ),
    )
    with pytest.raises(stage.CathStageError, match="outside its exact depth-4 route"):
        _build(case)

    case = _case(tmp_path / "escaped-shadow")
    shadow = case["traits"] / "function/shadow.yaml"
    _write(shadow, 'identifier: "\\x43ATH:1.10.20.30"\n')
    with pytest.raises(stage.CathStageError, match="outside its exact depth-4 route"):
        _build(case)

    case = _case(tmp_path / "block-scalar-shadow")
    shadow = case["traits"] / "function/block-shadow.yaml"
    _write(shadow, "identifier: >-\n  CATH:1.10.20.30\n")
    with pytest.raises(stage.CathStageError, match="outside its exact depth-4 route"):
        _build(case)

    case = _case(tmp_path / "explicit-key-shadow")
    shadow = case["traits"] / "function/explicit-key-shadow.yaml"
    _write(shadow, "? >-\n  identifier\n: CATH:1.10.20.30\n")
    with pytest.raises(stage.CathStageError, match="outside its exact depth-4 route"):
        _build(case)

    case = _case(tmp_path / "numeric-anchor-shadow")
    shadow = case["traits"] / "function/numeric-anchor-shadow.yaml"
    _write(shadow, "shadow_value: &1 CATH:1.10.20.30\nidentifier: *1\n")
    with pytest.raises(stage.CathStageError, match="outside its exact depth-4 route"):
        _build(case)

    case = _case(tmp_path / "uppercase-extension-shadow")
    shadow = case["traits"] / "function/shadow.YAML"
    _write(shadow, "identifier: CATH:1.10.20.30\n")
    with pytest.raises(stage.CathStageError, match="exact lowercase .yaml suffix"):
        _build(case)

    case = _case(tmp_path / "mixed-extension-shadow")
    shadow = case["traits"] / "function/shadow.yMl"
    _write(shadow, "identifier: CATH:1.10.20.30\n")
    with pytest.raises(stage.CathStageError, match="exact lowercase .yaml suffix"):
        _build(case)

    case = _case(tmp_path / "mixed-namespace-shadow")
    shadow = case["traits"] / "function/shadow.yaml"
    _write(shadow, "identifier: cAtH:1.10.20.30\n")
    with pytest.raises(stage.CathStageError, match="noncanonical CATH trait namespace"):
        _build(case)


def test_ripgrep_config_cannot_hide_a_cath_semantic_shadow(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    hostile_config = tmp_path / "hostile-ripgreprc"
    _write(hostile_config, "--max-filesize=1\n")
    monkeypatch.setenv("RIPGREP_CONFIG_PATH", str(hostile_config))
    case = _case(tmp_path / "case")
    shadow = case["traits"] / "function/hidden-by-hostile-config.yaml"
    _write(shadow, "identifier: CATH:1.10.20.30\n")

    with pytest.raises(stage.CathStageError, match="outside its exact depth-4 route"):
        _build(case)


def test_duplicate_yaml_keys_and_symlinks_fail_before_staging(tmp_path: Path) -> None:
    case = _case(tmp_path)
    shadow = case["traits"] / "function/duplicate.yaml"
    _write(shadow, "identifier: OTHER:1\nidentifier: CATH:1\n")
    with pytest.raises(stage.CathStageError, match="duplicate key"):
        _build(case)

    case = _case(tmp_path / "symlink")
    external = case["repo"] / "external.yaml"
    _write(external, "identifier: OTHER:1\n")
    link = case["traits"] / "function/link.yaml"
    link.parent.mkdir(parents=True, exist_ok=True)
    os.symlink(external, link)
    with pytest.raises(stage.CathStageError, match="symlink below trait directory is forbidden"):
        _build(case)


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda row: {**row, "uniprot_release": "2026_01"}, "release must be exactly 2026_02"),
        (lambda row: {**row, "sequence_length": 99}, "sequence_length does not match"),
        (lambda row: {**row, "sequence_sha256": "0" * 64}, "sha256 does not match"),
        (lambda row: {**row, "unexpected": 1}, "schema mismatch"),
    ],
)
def test_registry_contract_is_exact_and_fail_closed(
    tmp_path: Path, mutation: Any, message: str
) -> None:
    case = _case(tmp_path)
    _write_registry(case["registry"], [mutation(_registry_row())])
    _repin_registry(case)
    with pytest.raises(stage.CathStageError, match=message):
        _build(case)


def test_registry_pin_canonical_json_duplicates_and_sequence_agreement(tmp_path: Path) -> None:
    case = _case(tmp_path / "pin")
    case["registry_pin"] = "0" * 64
    with pytest.raises(stage.CathStageError, match="sha256 mismatch"):
        _build(case)

    case = _case(tmp_path / "noncanonical")
    case["registry"].write_text(
        json.dumps(_registry_row(), sort_keys=True) + "\n", encoding="utf-8"
    )
    _repin_registry(case)
    with pytest.raises(stage.CathStageError, match="not exact canonical JSON"):
        _build(case)

    case = _case(tmp_path / "duplicate-key")
    row = stage.canonical_json(_registry_row())
    case["registry"].write_text(row[:-1] + ',"protein_id":"UniProtKB:P12345"}\n', encoding="utf-8")
    _repin_registry(case)
    with pytest.raises(stage.CathStageError, match="duplicate key"):
        _build(case)

    case = _case(tmp_path / "duplicate-protein-id")
    _write_registry(case["registry"], [_registry_row(), _registry_row()])
    _repin_registry(case)
    with pytest.raises(stage.CathStageError, match="duplicate ProteinReference"):
        _build(case)

    case = _case(tmp_path / "same-release-disagreement")
    _write_registry(case["registry"], [_registry_row(sequence="ACDEFA")])
    _repin_registry(case)
    with pytest.raises(stage.CathStageError, match="same-release.*disagree"):
        _build(case)


def test_missing_rows_bind_the_exact_registry_that_established_absence(tmp_path: Path) -> None:
    case = _case(tmp_path)
    first = _build(case)

    _write_registry(case["registry"], [_registry_row(), _registry_row("Q99999")])
    _repin_registry(case)
    case["counts"]["protein_registry_row_count"] = 2
    second = _build(case)

    assert first.summary["stage_id"] != second.summary["stage_id"]
    assert [row["annotation_discovery_id"] for row in first.annotation_discoveries] != [
        row["annotation_discovery_id"] for row in second.annotation_discoveries
    ]
    assert [row["request_id"] for row in first.protein_requests] != [
        row["request_id"] for row in second.protein_requests
    ]
    first_binding = first.protein_requests[0]["protein_reference_binding"]
    second_binding = second.protein_requests[0]["protein_reference_binding"]
    assert (
        first_binding["protein_registry_artifact"]["sha256"]
        != second_binding["protein_registry_artifact"]["sha256"]
    )


def test_frame_releases_are_exact(tmp_path: Path) -> None:
    case = _case(tmp_path / "interpro")
    value = json.loads(case["interpro"].read_text(encoding="utf-8"))
    value["_meta"]["release"] = "108.0"
    _canonical_file(case["interpro"], value)
    case["pins"]["interpro_frame"] = hashlib.sha256(case["interpro"].read_bytes()).hexdigest()
    with pytest.raises(stage.CathStageError, match="InterPro.*109.0"):
        _build(case)

    case = _case(tmp_path / "residue")
    value = json.loads(case["residue"].read_text(encoding="utf-8"))
    value["_meta"]["release"] = "2026_01"
    _canonical_file(case["residue"], value)
    case["pins"]["residue_frame"] = hashlib.sha256(case["residue"].read_bytes()).hexdigest()
    with pytest.raises(stage.CathStageError, match="residue frame release.*2026_02"):
        _build(case)


def test_drift_is_detected_and_cli_has_no_write_or_apply_mode(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    case = _case(tmp_path)
    original_assert = stage._assert_unchanged
    changed = False

    def mutate_once(artifact, *, description, bound_root):
        nonlocal changed
        if not changed and description == "trait record":
            changed = True
            with artifact.path.open("a", encoding="utf-8") as stream:
                stream.write("# drift\n")
        return original_assert(artifact, description=description, bound_root=bound_root)

    monkeypatch.setattr(stage, "_assert_unchanged", mutate_once)
    with pytest.raises(stage.CathStageError, match="drifted while staging"):
        _build(case)

    parser = stage._parser()
    options = {option for action in parser._actions for option in action.option_strings}
    assert not any(
        any(word in option for word in ("output", "apply", "write", "fetch", "promote"))
        for option in options
    )
    assert "--protein-registry" in options
    assert "--expected-protein-registry-sha256" in options
    assert "--expect-uniprot-release" in options
    assert "must remain quiescent while staging" in (stage.__doc__ or "")


def test_registry_drift_is_detected_after_parse(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    case = _case(tmp_path)
    original_assert = stage._assert_unchanged
    changed = False

    def mutate_registry_once(artifact, *, description, bound_root):
        nonlocal changed
        if not changed and description == "ProteinReference registry":
            changed = True
            with artifact.path.open("a", encoding="utf-8") as stream:
                stream.write("\n")
        return original_assert(artifact, description=description, bound_root=bound_root)

    monkeypatch.setattr(stage, "_assert_unchanged", mutate_registry_once)
    with pytest.raises(stage.CathStageError, match="drifted while staging"):
        _build(case)
    assert changed


def test_count_contract_prevents_partial_or_silently_changed_scope(tmp_path: Path) -> None:
    case = _case(tmp_path)
    wrong = dict(case["counts"])
    wrong["annotation_discovery_count"] = 4
    case["counts"] = wrong
    with pytest.raises(stage.CathStageError, match="production count contract failed"):
        _build(case)


def test_production_cath_snapshot_golden_when_private_frames_exist() -> None:
    required = [
        stage.DEFAULT_CATH_NAMES,
        stage.DEFAULT_INTERPRO_FRAME,
        stage.DEFAULT_RESIDUE_FRAME,
        stage.DEFAULT_TRAITS_ROOT,
        stage.DEFAULT_PROTEIN_REGISTRY,
    ]
    if not all(path.exists() for path in required):
        pytest.skip("private/raw CATH and alignment frames are not all present")
    result = stage.build_stage(
        cath_names_path=stage.DEFAULT_CATH_NAMES,
        interpro_frame_path=stage.DEFAULT_INTERPRO_FRAME,
        residue_frame_path=stage.DEFAULT_RESIDUE_FRAME,
        traits_root=stage.DEFAULT_TRAITS_ROOT,
        protein_registry_path=stage.DEFAULT_PROTEIN_REGISTRY,
    )
    assert result.summary["cath_name_count"] == 8151
    assert result.summary["no_example_trait_count"] == 4192
    assert result.summary["native_blocker_count"] == 4192
    assert result.summary["native_exact_representative_count"] == 4191
    assert result.summary["native_placeholder_count"] == 1
    assert result.summary["annotation_discovery_count"] == 953
    assert result.summary["annotation_single_location_count"] == 813
    assert result.summary["annotation_ungrouped_multi_location_count"] == 140
    assert result.summary["annotation_unique_trait_count"] == 379
    assert result.summary["annotation_unique_protein_count"] == 415
    assert result.summary["protein_registry_row_count"] == 126
    assert result.summary["annotation_exact_local_reference_count"] == 0
    assert result.summary["annotation_missing_local_reference_count"] == 953
    assert result.summary["annotation_missing_local_reference_unique_protein_count"] == 415
    assert result.summary["protein_reference_request_count"] == 415
    assert result.summary["protein_reference_request_unique_protein_count"] == 415
    assert result.summary["protein_reference_request_multi_observation_count"] == 175
    assert result.summary["protein_reference_request_max_observation_count"] == 15
    assert len(result.protein_requests) == 415
    assert result.summary["protein_registry_artifact"]["sha256"] == (
        stage.EXPECTED_PROTEIN_REGISTRY_SHA256
    )
    assert result.summary["protein_registry_artifact"]["size_bytes"] == 121_024
    assert result.summary["grounding_evidence_emitted_count"] == 0
    assert result.summary["network_action_performed"] is False
    assert result.summary["write_action_performed"] is False
    # Filled from an independent local replay; these pin the complete output
    # projections, not just the headline counts.
    assert result.summary["annotation_discovery_rows_sha256"] == (
        "2353d5b87145ead27efde2a53ac4fec9ba65fbc3ccd9fa89097ad8a42772ad22"
    )
    assert result.summary["native_blocker_rows_sha256"] == (
        "e0621a95c7a41252166c38fe58151d6c80c56e55aa64b70f66bbef4dc2194893"
    )
    assert result.summary["protein_request_rows_sha256"] == (
        "057cc96e77c3f552560e0834e2c9f0bb249be1a6db252d801d22edfa84c19dee"
    )
    assert result.summary["combined_non_summary_rows_sha256"] == (
        "933a27907206e4dd4006c11824a2a32ef8c2e33f8abf72d0deb52e803c0665ca"
    )
    assert result.summary["all_cath_trait_binding_rows_sha256"] == (
        "0393f4b4a505c12698868594965877a119248cffb9266b3a4cf8114f1cd379c8"
    )
    assert result.summary["no_example_trait_binding_rows_sha256"] == (
        "2ce522975ace7ded750f6218bc050d40a1cd16510ff19c416a78d3d82c43ac63"
    )
    assert result.summary["stage_id"] == (
        "cath-grounding-discovery-stage:"
        "992c025a015c871d78c181bc11f6049d2887f53f3d843b5aa352b8da3d004fdf"
    )
    assert result.summary["summary_row_sha256"] == (
        "e984a7a08797feffd80515fd9e27f45043ec2a65d3dbd20479b883729dbe508b"
    )
    assert hashlib.sha256(stage.render_stage(result).encode("utf-8")).hexdigest() == (
        "2bf8ed6204f0216a43794616840c9d131869bde20a517df54fe690528e49c062"
    )
