"""Adversarial tests for BioLiP's no-write missing-protein staging boundary."""

from __future__ import annotations

import hashlib
import importlib
import json
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pytest

REPO = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(REPO / "scripts"))
stage = importlib.import_module("stage_biolip_missing_protein_candidates")
seed = importlib.import_module("seed_biolip")


def _source_row(
    pdb_id: str,
    ligand_id: str,
    *,
    binding_site_code: str = "BS01",
    receptor_chain: str = "A",
    ligand_chain: str = "X",
    ligand_serial: str = "1",
    author_residues: str = "A1 C2",
    receptor_residues: str = "A1 C2",
    receptor_sequence: str = "AC",
    uniprot_id: str = "",
) -> list[str]:
    row = [
        pdb_id,
        receptor_chain,
        "2.00",
        binding_site_code,
        ligand_id,
        ligand_chain,
        ligand_serial,
        author_residues,
        receptor_residues,
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        uniprot_id,
        "",
        "1",
        receptor_sequence,
    ]
    assert len(row) == 21
    return row


def _write_source(path: Path, rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join("\t".join(row) + "\n" for row in rows),
        encoding="utf-8",
    )


def _write_readme(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "Fixture copy of BioLiP's numbered column contract.\n\n"
        + "".join(
            f"{number:02d}\t{label}\n" for number, label in enumerate(stage.README_COLUMN_LABELS, 1)
        ),
        encoding="utf-8",
    )


def _write_seed_trait(route: Path, ligand_id: str, rows: list[list[str]]) -> Path:
    ligand = seed.Ligand(ligand_id)
    for row in rows:
        ligand.add_row(row)
    path = route / seed.target_path(ligand).name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(seed.build_yaml(ligand, {}), encoding="utf-8")
    return path


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _case(tmp_path: Path) -> dict[str, Any]:
    repo = tmp_path / "repo"
    raw_dir = repo / "data/raw/biolip"
    biolip = raw_dir / "BioLiP_nr.txt"
    readme = raw_dir / "readme.txt"
    traits = repo / "data/traits"
    route = traits / stage.BIOLIP_TRAIT_ROUTE

    # Lines 1 and 3 are byte-identical.  Line 2 has the same legacy weak key
    # (PDB, receptor chain, ligand) but is a distinct source-native occurrence.
    duplicate = _source_row("1abc", "LIG")
    weak_key_peer = _source_row(
        "1abc",
        "LIG",
        binding_site_code="BS02",
        ligand_chain="Y",
        ligand_serial="2",
        author_residues="C4A",
        receptor_residues="C2",
    )
    insertion_and_negative = _source_row(
        "2def",
        "NEG",
        author_residues="A-2 C4A",
        receptor_residues="A1 C2",
    )
    residue_mismatch = _source_row(
        "3ghi",
        "BAD",
        author_residues="A1 C2",
        receptor_residues="A1 C2",
        receptor_sequence="AX",
    )
    # This source ligand has a current canonical example and must be outside the
    # stage even though it shares the same 21-column source artifact.
    already_has_example = _source_row("4jkl", "SKP", uniprot_id="P12345")
    rows = [
        duplicate,
        weak_key_peer,
        duplicate,
        insertion_and_negative,
        residue_mismatch,
        already_has_example,
    ]
    _write_source(biolip, rows)
    _write_readme(readme)
    trait_paths = {
        "LIG": _write_seed_trait(route, "LIG", rows[:3]),
        "NEG": _write_seed_trait(route, "NEG", [insertion_and_negative]),
        "BAD": _write_seed_trait(route, "BAD", [residue_mismatch]),
        "SKP": _write_seed_trait(route, "SKP", [already_has_example]),
    }
    return {
        "repo": repo,
        "biolip": biolip,
        "readme": readme,
        "traits": traits,
        "route": route,
        "rows": rows,
        "trait_paths": trait_paths,
        "pins": {"biolip": _sha256(biolip), "readme": _sha256(readme)},
    }


def _build(case: Mapping[str, Any]) -> stage.StageResult:
    return stage.build_stage(
        biolip_path=case["biolip"],
        readme_path=case["readme"],
        traits_root=case["traits"],
        repo_root=case["repo"],
        expected_source_sha256=case["pins"],
    )


def _assert_content_address(
    row: dict[str, Any], *, id_field: str, prefix: str, row_hash_field: str
) -> None:
    without_row_hash = dict(row)
    observed_row_hash = without_row_hash.pop(row_hash_field)
    assert observed_row_hash == stage.value_sha256(without_row_hash)
    observed_id = without_row_hash.pop(id_field)
    assert observed_id == prefix + stage.value_sha256(without_row_hash)


def _tree_digest(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): _sha256(path)
        for path in sorted(root.rglob("*"))
        if path.is_file() and not path.is_symlink()
    }


def _mappings(value: Any):
    if isinstance(value, Mapping):
        yield value
        for item in value.values():
            yield from _mappings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _mappings(item)


def test_exact_duplicates_aggregate_but_weak_key_collisions_survive(
    tmp_path: Path,
) -> None:
    case = _case(tmp_path)
    result = _build(case)
    summary = result.summary
    assert summary["all_trait_count"] == 4
    assert summary["no_example_trait_count"] == 3
    assert summary["selected_source_physical_line_count"] == 5
    assert summary["selected_unique_source_line_count"] == 4
    assert summary["selected_duplicate_physical_line_count"] == 1

    lig_rows = [row for row in result.occurrences if row["source_binding"]["ligand_id"] == "LIG"]
    assert len(lig_rows) == 2
    assert sorted(row["source_binding"]["source_line_numbers"] for row in lig_rows) == [
        [1, 3],
        [2],
    ]
    assert {
        (
            row["source_binding"]["source_occurrence_key"]["pdb_id"],
            row["source_binding"]["source_occurrence_key"]["receptor_chain"],
            row["source_binding"]["source_occurrence_key"]["ligand_id"],
        )
        for row in lig_rows
    } == {("1abc", "A", "LIG")}
    assert {
        (
            row["source_binding"]["binding_site_code"],
            row["source_binding"]["ligand_chain_id"],
            row["source_binding"]["ligand_serial_number_text"],
        )
        for row in lig_rows
    } == {("BS01", "X", "1"), ("BS02", "Y", "2")}

    duplicate = next(
        row for row in lig_rows if row["source_binding"]["source_line_numbers"] == [1, 3]
    )
    expected_raw = ("\t".join(case["rows"][0]) + "\n").encode()
    assert (
        duplicate["source_binding"]["source_raw_line_sha256"]
        == hashlib.sha256(expected_raw).hexdigest()
    )
    assert duplicate["source_binding"]["source_physical_line_count"] == 2
    for row in result.occurrences:
        _assert_content_address(
            row,
            id_field="source_occurrence_id",
            prefix="biolip-missing-protein-source-occurrence:",
            row_hash_field="source_occurrence_row_sha256",
        )


def test_residue_validation_is_all_or_nothing_and_preserves_author_syntax(
    tmp_path: Path,
) -> None:
    result = _build(_case(tmp_path))
    blocked = next(row for row in result.occurrences if row["source_binding"]["ligand_id"] == "BAD")
    assert blocked["stage_status"] == stage.BLOCKED_STATUS
    assert blocked["source_residue_validation_policy"] == (
        "ALL_BINDING_RESIDUES_OR_WHOLE_ROW_BLOCKED"
    )
    assert blocked["source_residue_blocking_reasons"] == [
        "SOURCE_RESIDUE_RECEPTOR_SEQUENCE_MISMATCH"
    ]
    assert blocked["source_residue_count"] == 2
    assert [
        (pair["author_residue_token"], pair["receptor_sequence_residue_token"])
        for pair in blocked["binding_residue_pairs"]
    ] == [("A1", "A1"), ("C2", "C2")]
    assert all(
        blocked["source_occurrence_id"] not in request["source_occurrence_ids"]
        for request in result.fetch_requests
    )

    preserved = next(
        row for row in result.occurrences if row["source_binding"]["ligand_id"] == "NEG"
    )
    assert preserved["stage_status"] == stage.READY_STATUS
    assert preserved["binding_residue_pairs"] == [
        {
            "ordinal": 1,
            "author_residue_token": "A-2",
            "receptor_sequence_residue_token": "A1",
            "source_amino_acid": "A",
            "author_residue_number": -2,
            "author_insertion_code": "",
            "biolip_receptor_sequence_position": 1,
        },
        {
            "ordinal": 2,
            "author_residue_token": "C4A",
            "receptor_sequence_residue_token": "C2",
            "source_amino_acid": "C",
            "author_residue_number": 4,
            "author_insertion_code": "A",
            "biolip_receptor_sequence_position": 2,
        },
    ]


def test_scope_is_no_example_only_and_fetch_queue_is_small_and_deduplicated(
    tmp_path: Path,
) -> None:
    result = _build(_case(tmp_path))
    assert {row["source_binding"]["ligand_id"] for row in result.occurrences} == {
        "LIG",
        "NEG",
        "BAD",
    }
    assert all(
        row["trait_binding"]["trait_record_has_canonical_examples"] is False
        for row in result.occurrences
    )
    assert all(
        row["source_binding"]["source_uniprot_claim_status"] == "MISSING"
        for row in result.occurrences
    )
    assert result.summary["ready_for_residue_level_sifts_count"] == 3
    assert result.summary["source_residue_blocker_count"] == 1
    assert result.summary["residue_level_sifts_fetch_request_count"] == 2

    assert [row["pdb_id"] for row in result.fetch_requests] == ["1abc", "2def"]
    request_1abc = result.fetch_requests[0]
    assert request_1abc["source_occurrence_count"] == 2
    assert request_1abc["requested_artifact_kind"] == (
        "PDBe_SIFTS_REMEDIATED_RESIDUE_LEVEL_XML_GZIP"
    )
    assert request_1abc["requested_source_root"] == (
        "https://ftp.ebi.ac.uk/pub/databases/msd/sifts/xml_remediated"
    )
    assert request_1abc["requested_relative_path"] == "1abc.xml.gz"
    assert request_1abc["fetch_manifest_required"] is True
    assert request_1abc["required_fetch_manifest_semantics"] == (
        "COMPLETE_CANONICAL_CONTENT_ADDRESSED_MANIFEST_BINDING_EVERY_REQUESTED_FILE"
    )
    assert request_1abc["network_action_performed"] is False
    assert {
        tuple(binding["source_line_numbers"])
        for binding in request_1abc["source_line_and_trait_bindings"]
    } == {(1, 3), (2,)}
    for row in result.fetch_requests:
        _assert_content_address(
            row,
            id_field="fetch_request_id",
            prefix="biolip-residue-sifts-fetch-request:",
            row_hash_field="fetch_request_row_sha256",
        )

    rendered = stage.render_stage(result)
    assert rendered == stage.render_stage(result)
    decoded = [json.loads(line) for line in rendered.splitlines()]
    assert decoded == [*result.occurrences, *result.fetch_requests, result.summary]
    assert (
        stage.render_stage(result, summary_only=True) == stage.canonical_json(result.summary) + "\n"
    )
    for row in [*result.occurrences, *result.fetch_requests, result.summary]:
        assert row.get("qualification_claimed") is False
        assert row.get("network_action_performed", False) is False
        assert "protein_id" not in row
        for mapping in _mappings(row):
            assert not {
                "protein_id",
                "coordinate_frame",
                "intervals",
                "mapping_method",
                "qualification_status",
                "residue_positions",
                "trait_occurrence",
                "uniprot_position",
                "uniprot_residue_position",
            } & set(mapping)
            assert mapping.get("qualification_claimed") is not True
            assert mapping.get("protein_identity_claimed") is not True
            assert mapping.get("uniprot_coordinates_claimed") is not True


def test_trait_bindings_are_byte_bound_and_filename_is_not_interchangeable(
    tmp_path: Path,
) -> None:
    case = _case(tmp_path)
    result = _build(case)
    for occurrence in result.occurrences:
        binding = occurrence["trait_binding"]
        path = case["repo"] / binding["trait_record_path"]
        assert binding["trait_record_sha256"] == _sha256(path)
        assert binding["trait_id"].endswith("_" + binding["ligand_id"])

    moved_case = _case(tmp_path / "renamed")
    original = moved_case["trait_paths"]["LIG"]
    original.rename(original.with_name("interchangeable-name.yaml"))
    with pytest.raises(stage.BioLipStageError, match="exact .*path|exact filename"):
        _build(moved_case)


@pytest.mark.parametrize(
    "shadow_text",
    [
        'identifier: "\\x70roteintraitsmech:BIOLIP_LIG"\n',
        "identifier: >-\n  proteintraitsmech:BIOLIP_LIG\n",
        "shadow: &id proteintraitsmech:BIOLIP_LIG\nidentifier: *id\n",
    ],
)
def test_semantic_trait_shadows_outside_exact_route_fail_closed(
    tmp_path: Path, shadow_text: str
) -> None:
    case = _case(tmp_path)
    shadow = case["traits"] / "function/protein_family/shadow.yml"
    shadow.parent.mkdir(parents=True, exist_ok=True)
    shadow.write_text(shadow_text, encoding="utf-8")
    with pytest.raises(stage.BioLipStageError, match="outside its exact route"):
        _build(case)


def test_non_biolip_identity_inside_exact_route_fails_closed(tmp_path: Path) -> None:
    case = _case(tmp_path)
    unrelated = case["route"] / "unrelated.yaml"
    unrelated.write_text("identifier: OTHER:1\n", encoding="utf-8")
    with pytest.raises(stage.BioLipStageError, match="non-BioLiP trait identity"):
        _build(case)


@pytest.mark.parametrize(
    "replacement",
    [
        "xrefs:\n  - pdb.ligand:LIG\n  - CHEBI:12345\n",
        "xrefs:\n  - CHEBI:12345\n  - pdb.ligand:LIG\n",
    ],
)
def test_arbitrary_or_reordered_extra_source_xrefs_fail_closed(
    tmp_path: Path,
    replacement: str,
) -> None:
    case = _case(tmp_path)
    path = case["trait_paths"]["LIG"]
    text = path.read_text(encoding="utf-8")
    path.write_text(
        text.replace("xrefs:\n  - pdb.ligand:LIG\n", replacement),
        encoding="utf-8",
    )
    with pytest.raises(stage.BioLipStageError, match="exact BioLiP source-model contract"):
        _build(case)


def test_polymer_dna_collision_xref_exception_is_exact_and_visible(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    biolip = repo / "data/raw/biolip/BioLiP_nr.txt"
    readme = repo / "data/raw/biolip/readme.txt"
    traits = repo / "data/traits"
    route = traits / stage.BIOLIP_TRAIT_ROUTE
    row = _source_row("1abc", "dna")
    _write_source(biolip, [row])
    _write_readme(readme)
    path = _write_seed_trait(route, "dna", [row])
    text = path.read_text(encoding="utf-8")
    exact = "xrefs:\n  - CHEBI:16991\n"
    exception = "xrefs:\n  - CHEBI:16991\n  - pdb.ligand:DNA\n"
    assert exact in text
    path.write_text(text.replace(exact, exception), encoding="utf-8")
    case = {
        "repo": repo,
        "biolip": biolip,
        "readme": readme,
        "traits": traits,
        "pins": {"biolip": _sha256(biolip), "readme": _sha256(readme)},
    }

    result = _build(case)
    expected_status = "EXPLICIT_CURRENT_POLYMER_DNA_COLLISION_XREF_EXCEPTION"
    assert result.summary["trait_source_xref_status_counts"] == {expected_status: 1}
    assert result.occurrences[0]["trait_binding"]["trait_source_xrefs"] == [
        "CHEBI:16991",
        "pdb.ligand:DNA",
    ]
    assert result.occurrences[0]["trait_binding"]["trait_source_xref_status"] == expected_status

    path.write_text(
        path.read_text(encoding="utf-8").replace(
            exception,
            "xrefs:\n  - pdb.ligand:DNA\n  - CHEBI:16991\n",
        ),
        encoding="utf-8",
    )
    with pytest.raises(stage.BioLipStageError, match="exact BioLiP source-model contract"):
        _build(case)


def test_duplicate_yaml_keys_and_symlinks_fail_before_staging(tmp_path: Path) -> None:
    duplicate_case = _case(tmp_path / "duplicate-key")
    shadow = duplicate_case["traits"] / "function/duplicate.yaml"
    shadow.parent.mkdir(parents=True, exist_ok=True)
    shadow.write_text(
        "identifier: OTHER:1\nidentifier: proteintraitsmech:BIOLIP_LIG\n",
        encoding="utf-8",
    )
    with pytest.raises(stage.BioLipStageError, match="duplicate key"):
        _build(duplicate_case)

    trait_link_case = _case(tmp_path / "trait-link")
    external = trait_link_case["repo"] / "external.yaml"
    external.write_text("identifier: OTHER:1\n", encoding="utf-8")
    (trait_link_case["traits"] / "linked.yaml").symlink_to(external)
    with pytest.raises(stage.BioLipStageError, match="symlink below trait directory"):
        _build(trait_link_case)

    source_link_case = _case(tmp_path / "source-link")
    source = source_link_case["biolip"]
    original = source.with_suffix(".original")
    source.rename(original)
    source.symlink_to(original)
    with pytest.raises(stage.BioLipStageError, match="without following symlinks"):
        _build(source_link_case)


def test_pins_and_final_drift_check_fail_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pin_case = _case(tmp_path / "pin")
    pin_case["pins"]["biolip"] = "0" * 64
    with pytest.raises(stage.BioLipStageError, match="sha256 mismatch"):
        _build(pin_case)

    drift_case = _case(tmp_path / "drift")
    original_assert = stage._assert_unchanged
    changed = False

    def mutate_trait_once(artifact: Any, *, description: str, bound_root: Any) -> None:
        nonlocal changed
        if not changed and description == "trait record":
            changed = True
            with artifact.path.open("a", encoding="utf-8") as stream:
                stream.write("# concurrent drift\n")
        original_assert(artifact, description=description, bound_root=bound_root)

    monkeypatch.setattr(stage, "_assert_unchanged", mutate_trait_once)
    with pytest.raises(stage.BioLipStageError, match="drifted while staging"):
        _build(drift_case)
    assert changed


def test_segment_cache_is_out_of_scope_and_cannot_change_output(tmp_path: Path) -> None:
    case = _case(tmp_path)
    before = _build(case)
    cache = case["repo"] / "data/raw/align_cache/biolip_sifts.json"
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(
        json.dumps(
            {
                "malicious-segment-cache": {
                    "1abc": {
                        "UniProt": {
                            "P99999": {
                                "mappings": [
                                    {
                                        "chain_id": "A",
                                        "unp_start": 1,
                                        "unp_end": 2,
                                        "start": {"author_residue_number": 1},
                                        "end": {"author_residue_number": 2},
                                    }
                                ]
                            }
                        }
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    after = _build(case)
    assert stage.render_stage(after) == stage.render_stage(before)
    assert "UNMANIFESTED_SEGMENT_LEVEL_PDBe_MAPPING_CACHE" in after.summary["excluded_inputs"]


def test_descriptor_relative_open_blocks_source_symlink_swap(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    case = _case(tmp_path)
    target = case["biolip"]
    backup = target.with_suffix(".original")
    external = tmp_path / "external-biolip.txt"
    external.write_text("external bytes must not be read\n", encoding="utf-8")
    original_open = stage.os.open
    original_supports_dir_fd = set(stage.os.supports_dir_fd)
    swapped = False

    def swapping_open(path: Any, flags: int, mode: int = 0o777, *, dir_fd: int | None = None):
        nonlocal swapped
        if path == target.name and dir_fd is not None and not swapped:
            swapped = True
            target.rename(backup)
            target.symlink_to(external)
        return original_open(path, flags, mode, dir_fd=dir_fd)

    monkeypatch.setattr(stage.os, "open", swapping_open)
    monkeypatch.setattr(
        stage.os,
        "supports_dir_fd",
        original_supports_dir_fd | {swapping_open},
    )
    monkeypatch.setattr(
        stage.os,
        "read",
        lambda *_args, **_kwargs: pytest.fail("external bytes were read after symlink swap"),
    )
    with pytest.raises(stage.BioLipStageError, match="without following symlinks"):
        _build(case)
    assert swapped


def test_descriptor_safety_capability_is_mandatory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    case = _case(tmp_path)
    monkeypatch.setattr(stage.os, "supports_dir_fd", set())
    with pytest.raises(stage.BioLipStageError, match="platform lacks required"):
        _build(case)


def test_cli_is_stdout_only_and_has_no_write_network_or_apply_mode(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    case = _case(tmp_path)
    before = _tree_digest(case["repo"])
    real_build = stage.build_stage

    def build_under_fixture_root(**kwargs: Any) -> stage.StageResult:
        return real_build(repo_root=case["repo"], **kwargs)

    monkeypatch.setattr(stage, "build_stage", build_under_fixture_root)
    exit_code = stage.main(
        [
            "--biolip",
            str(case["biolip"]),
            "--readme",
            str(case["readme"]),
            "--traits-root",
            str(case["traits"]),
            "--expected-biolip-sha256",
            case["pins"]["biolip"],
            "--expected-readme-sha256",
            case["pins"]["readme"],
        ]
    )
    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.err == ""
    assert [json.loads(line)["kind"] for line in captured.out.splitlines()][-1] == (
        stage.SUMMARY_KIND
    )
    assert _tree_digest(case["repo"]) == before

    parser = stage._parser()
    options = {option for action in parser._actions for option in action.option_strings}
    assert not any(
        forbidden in option
        for option in options
        for forbidden in ("apply", "output", "write", "network", "fetch")
    )
    assert "must remain quiescent while the command runs" in (stage.__doc__ or "")


def test_production_biolip_missing_protein_snapshot_when_artifacts_exist() -> None:
    required = [stage.DEFAULT_BIOLIP, stage.DEFAULT_README, stage.DEFAULT_TRAITS_ROOT]
    if not all(path.exists() for path in required):
        pytest.skip("private BioLiP source bundle is unavailable")
    result = stage.build_stage(
        biolip_path=stage.DEFAULT_BIOLIP,
        readme_path=stage.DEFAULT_README,
        traits_root=stage.DEFAULT_TRAITS_ROOT,
    )
    summary = result.summary
    assert summary["source_physical_line_count"] == 86_458
    assert summary["source_unique_exact_line_count"] == 86_375
    assert summary["source_duplicate_physical_line_count"] == 83
    assert summary["source_distinct_ligand_count"] == 6_020
    assert summary["all_trait_count"] == 6_020
    assert summary["no_example_trait_count"] == 445
    assert summary["selected_source_physical_line_count"] == 643
    assert summary["selected_unique_source_line_count"] == 641
    assert summary["selected_duplicate_physical_line_count"] == 2
    assert summary["ready_for_residue_level_sifts_count"] == 638
    assert summary["source_residue_blocker_count"] == 3
    assert summary["ready_unique_trait_count"] == 443
    assert summary["blocked_unique_trait_count"] == 3
    assert summary["source_uniprot_claim_status_counts"] == {"MISSING": 641}
    assert summary["trait_source_xref_status_counts"] == {
        "EXACT_SEEDER_SOURCE_XREFS": 6_019,
        "EXPLICIT_CURRENT_POLYMER_DNA_COLLISION_XREF_EXCEPTION": 1,
    }
    assert summary["residue_level_sifts_fetch_request_count"] == 480
    assert summary["residue_level_sifts_requested_pdb_ids_sha256"] == (
        "1bba8f1fd537b5eb6ceb3e4c1db034cded0d4b6f28b449398a5aed96bea666ff"
    )
    assert summary["all_trait_binding_rows_sha256"] == (
        "0671a0a53d026bae51be05d81e4501f091f80d27581c8b3f057a12b084dca856"
    )
    assert summary["no_example_trait_binding_rows_sha256"] == (
        "bcb586ace9ee5803e4774579ac36e6e83b626a48ff4ec95bf9e79c04472bc097"
    )
    assert summary["occurrence_rows_sha256"] == (
        "d23d161fd7dfe61e43a63bb1e081d00c327e86f20b6be4d7aca49c186fc47325"
    )
    assert summary["fetch_request_rows_sha256"] == (
        "f135281921caa6b974d71026aedb78263ea948a2c2d6058dacd208332f989726"
    )
    assert summary["combined_non_summary_rows_sha256"] == (
        "fcc804932d40efba7c2585307a9c10c1ee07d09d6d8430dfa22f80a38e61da2e"
    )
    assert summary["stage_id"] == (
        "biolip-missing-protein-stage:"
        "f9fc94db49a9c066fba504596d88dc2f2ffeba46841e8f1359031eccd2b311dc"
    )
    assert len(result.occurrences) + len(result.fetch_requests) + 1 == 1_122
    assert hashlib.sha256(stage.render_stage(result).encode("utf-8")).hexdigest() == (
        "3cb24236f59e0c72b88a00583a1d7fd8c6001763d0e7ac36777e21fd963271fb"
    )
    assert {
        (
            row["trait_binding"]["trait_id"],
            tuple(row["source_binding"]["source_line_numbers"]),
        )
        for row in result.occurrences
        if row["stage_status"] == stage.BLOCKED_STATUS
    } == {
        ("proteintraitsmech:BIOLIP_A1AT9", (80_885,)),
        ("proteintraitsmech:BIOLIP_ESC", (81_564,)),
        ("proteintraitsmech:BIOLIP_GG2", (71_437,)),
    }
