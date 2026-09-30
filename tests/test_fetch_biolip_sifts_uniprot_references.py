"""Release-pinned BioLiP/SIFTS UniProt reference fetch tests."""

from __future__ import annotations

import gzip
import hashlib
import importlib
import json
import sys
from pathlib import Path
from typing import Any

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

mapper = importlib.import_module("stage_biolip_sifts_mappings")
fetcher = importlib.import_module("fetch_biolip_sifts_uniprot_references")


def _occurrence(source_id: str, pdb_id: str, ligand: str, position: int) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "kind": mapper.INPUT_OCCURRENCE_KIND,
        "stage_status": "READY_FOR_RESIDUE_LEVEL_SIFTS",
        "qualification_claimed": False,
        "protein_identity_claimed": False,
        "uniprot_coordinates_claimed": False,
        "source_residue_count": 1,
        "binding_residue_pairs": [
            {
                "author_insertion_code": "",
                "author_residue_number": position,
                "author_residue_token": f"A{position}",
                "biolip_receptor_sequence_position": 1,
                "ordinal": 1,
                "receptor_sequence_residue_token": "A1",
                "source_amino_acid": "A",
            }
        ],
        "source_binding": {
            "binding_residues_pdb_author_text": f"A{position}",
            "binding_residues_receptor_sequence_text": "A1",
            "binding_site_code": "BS01",
            "ligand_chain_id": "X",
            "ligand_id": ligand,
            "ligand_serial_number_text": "1",
            "receptor_chain_id": "A",
            "receptor_sequence_length": 1,
            "receptor_sequence_sha256": "3" * 64,
            "resolution_text": "1.0",
            "source_field_projection_sha256": "4" * 64,
            "source_line_numbers": [1],
            "source_occurrence_key": {
                "binding_site_code": "BS01",
                "ligand_chain": "X",
                "ligand_id": ligand,
                "ligand_serial_number": "1",
                "pdb_id": pdb_id,
                "receptor_chain": "A",
            },
            "source_physical_line_count": 1,
            "source_raw_line_sha256": "0" * 64,
            "source_raw_line_sha256_basis": "RAW_UTF8_PHYSICAL_LINE_INCLUDING_LF",
            "source_uniprot_accession_claims": [],
            "source_uniprot_claim_status": "MISSING",
            "source_uniprot_field_text": "",
            "structure_id": f"PDB:{pdb_id}",
        },
        "trait_binding": {
            "ligand_id": ligand,
            "trait_id": f"proteintraitsmech:BIOLIP_{ligand}",
            "trait_record_has_canonical_examples": False,
            "trait_record_path": f"data/traits/structure/binding_site/biolip/{ligand}.yaml",
            "trait_record_sha256": "1" * 64,
            "trait_source_xref_status": "EXACT_SEEDER_SOURCE_XREFS",
            "trait_source_xrefs": [f"pdb.ligand:{ligand}"],
        },
        "source_occurrence_id": source_id,
        "source_occurrence_row_sha256": "2" * 64,
    }


def _sifts_xml(pdb_id: str) -> bytes:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<entry xmlns="http://www.ebi.ac.uk/pdbe/docs/sifts/eFamily.xsd"
       xmlns:dc="http://purl.org/dc/elements/1.1/"
       xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
       dbSource="PDBe"
       dbCoordSys="PDBe"
       dbAccessionId="{pdb_id}"
       date="2026-09-27">
  <listDB><db dbSource="UniProt" dbVersion="2026.03"/></listDB>
  <entity>
    <segment>
      <listResidue>
        <residue dbSource="PDBe" dbCoordSys="PDBe" dbResNum="1">
          <crossRefDb dbSource="PDB" dbCoordSys="PDBresnum"
                      dbAccessionId="{pdb_id}" dbChainId="A"
                      dbResNum="1" dbResName="ALA"/>
          <crossRefDb dbSource="UniProt" dbCoordSys="UniProt"
                      dbAccessionId="P12345" dbResNum="10" dbResName="A"/>
        </residue>
      </listResidue>
    </segment>
  </entity>
  <dc:rights rdf:resource="http://pdbe.org/sifts">PDBe SIFTS terms</dc:rights>
</entry>
""".encode()


def _manifest_entry(
    snapshot: Path, pdb_id: str, *, sifts_uniprot_release: str = "2026_03"
) -> dict[str, Any]:
    xml = gzip.compress(_sifts_xml(pdb_id))
    xml_path = snapshot / f"{pdb_id}.xml.gz"
    xml_path.write_bytes(xml)
    return {
        "path": xml_path.name,
        "pdb_id": pdb_id,
        "sha256": hashlib.sha256(xml).hexdigest(),
        "sifts_entry_date": "2026-09-27",
        "sifts_uniprot_release": sifts_uniprot_release,
        "sifts_uniprot_version": sifts_uniprot_release.replace("_", "."),
        "size_bytes": len(xml),
        "url": f"{mapper.SIFTS_XML_ROOT}/{xml_path.name}",
    }


def _write_inputs(
    tmp_path: Path, rows: list[dict[str, Any]] | None = None
) -> tuple[Path, Path]:
    stage = tmp_path / "stage.jsonl"
    snapshot = tmp_path / "snapshot"
    snapshot.mkdir()
    rows = rows or [
        _occurrence(
            "biolip-missing-protein-source-occurrence:ok",
            "1abc",
            "ATP",
            1,
        )
    ]
    summary = {
        "schema_version": 1,
        "kind": mapper.INPUT_SUMMARY_KIND,
        "stage_id": "biolip-missing-protein-stage:fixture",
        "combined_non_summary_rows_sha256": "fixture",
        "ready_for_residue_level_sifts_count": len(rows),
    }
    stage.write_text(
        "".join(mapper.canonical_json(row) + "\n" for row in [*rows, summary]),
        encoding="utf-8",
    )
    pdb_ids = sorted(
        {row["source_binding"]["source_occurrence_key"]["pdb_id"] for row in rows}
    )
    manifest = {
        "schema_version": 1,
        "kind": mapper.SNAPSHOT_KIND,
        "complete": True,
        "entries": [_manifest_entry(snapshot, pdb_id) for pdb_id in pdb_ids],
        "failures": [],
        "fetch_request_count": len(pdb_ids),
        "requested_pdb_count": len(pdb_ids),
        "snapshot_id": "fixture",
        "source": "PDBe SIFTS residue-level XML",
        "source_root": mapper.SIFTS_XML_ROOT,
        "stage_combined_non_summary_rows_sha256": "fixture",
        "stage_id": "biolip-missing-protein-stage:fixture",
        "stage_path": "stage.jsonl",
        "stage_sha256": hashlib.sha256(stage.read_bytes()).hexdigest(),
    }
    (snapshot / "manifest.json").write_text(
        mapper.canonical_json(manifest) + "\n",
        encoding="utf-8",
    )
    return stage, snapshot


def _entry(accession: str, sequence: str = "CCCCCCCCCA") -> dict[str, Any]:
    return {
        "primaryAccession": accession,
        "uniProtkbId": f"{accession}_FIXTURE",
        "entryType": "UniProtKB reviewed (Swiss-Prot)",
        "proteinDescription": {"recommendedName": {"fullName": {"value": "Fixture protein"}}},
        "organism": {"taxonId": 562, "scientificName": "Escherichia coli"},
        "sequence": {"value": sequence, "length": len(sequence)},
        "entryAudit": {"sequenceVersion": 3},
        "uniProtKBCrossReferences": [
            {"database": "Pfam", "id": "PF00001", "properties": []}
        ],
    }


def _responses(path: Path, responses: list[dict[str, Any]], release: str = "2026_03") -> None:
    path.write_text(
        json.dumps({"release": release, "responses": responses}),
        encoding="utf-8",
    )


def _paths(tmp_path: Path) -> tuple[Path, Path, Path, Path, Path, Path]:
    return (
        tmp_path / "registry.jsonl",
        tmp_path / "memberships.jsonl",
        tmp_path / "mappings.jsonl",
        tmp_path / "blocked.tsv",
        tmp_path / "receipt.json",
        tmp_path / "plan.json",
    )


def _dry_args(
    tmp_path: Path,
    *,
    responses: Path | None = None,
    extra: tuple[str, ...] = (),
) -> list[str]:
    stage, snapshot = _write_inputs(tmp_path)
    out, memberships, mappings, blocked, receipt, _plan = _paths(tmp_path)
    args = [
        "--stage",
        str(stage),
        "--sifts-snapshot",
        str(snapshot),
        "--expect-release",
        "2026_03",
        "--out",
        str(out),
        "--membership-out",
        str(memberships),
        "--mapping-out",
        str(mappings),
        "--blocked",
        str(blocked),
        "--receipt",
        str(receipt),
    ]
    if responses is not None:
        args.extend(("--offline-responses", str(responses)))
    return [*args, *extra]


def _prepare_apply(
    tmp_path: Path,
    responses: Path,
    *extra: str,
) -> tuple[list[str], Path, Path, Path, Path, Path]:
    out, memberships, mappings, blocked, receipt, plan = _paths(tmp_path)
    args = _dry_args(tmp_path, responses=responses, extra=extra)
    namespace = fetcher.parser().parse_args(args)
    prepared = fetcher._derive_request_plan(namespace)
    plan.write_text(fetcher.render_request_plan(prepared.plan), encoding="utf-8")
    return (
        [*args, "--request-plan", str(plan), "--apply"],
        out,
        memberships,
        mappings,
        blocked,
        receipt,
    )


def _jsonl_rows(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def _write_readdressed_mapping(path: Path, row: dict[str, Any]) -> None:
    row.pop("mapping_id", None)
    row.pop("mapping_row_sha256", None)
    row["mapping_id"] = fetcher.MAPPING_REGISTRY_ID_PREFIX + mapper.value_sha256(row)
    row["mapping_row_sha256"] = mapper.value_sha256(row)
    path.write_text(fetcher._canonical_json(row) + "\n", encoding="utf-8")


def _bind_source_ligand(
    row: dict[str, Any],
    *,
    ligand_id: str,
    trait_id: str,
    trait_record_path: str,
    trait_source_xref_status: str,
    trait_source_xrefs: list[str],
) -> None:
    row["trait_id"] = trait_id
    row["record_path"] = trait_record_path
    source_projection = row["source_projection"]
    source_projection["source_binding"]["ligand_id"] = ligand_id
    source_projection["source_binding"]["source_occurrence_key"][
        "ligand_id"
    ] = ligand_id
    source_projection["trait_binding"].update(
        {
            "ligand_id": ligand_id,
            "trait_id": trait_id,
            "trait_record_path": trait_record_path,
            "trait_source_xref_status": trait_source_xref_status,
            "trait_source_xrefs": trait_source_xrefs,
        }
    )


def test_dry_run_emits_exact_canonical_plan_without_outputs(
    tmp_path: Path, capsys, monkeypatch
) -> None:
    responses = tmp_path / "responses.json"
    _responses(responses, [{"requested": ["P12345"], "results": []}])
    monkeypatch.setattr(
        fetcher,
        "NetworkClient",
        lambda *_args, **_kwargs: raise_network_attempt(),
    )

    assert fetcher.main(_dry_args(tmp_path, responses=responses)) == 0

    captured = capsys.readouterr()
    assert captured.err == ""
    assert captured.out.endswith("\n") and captured.out.count("\n") == 1
    plan = json.loads(captured.out)
    assert captured.out == fetcher.render_request_plan(plan)
    assert plan["kind"] == fetcher.PLAN_KIND
    assert plan["qualification_claimed"] is False
    assert plan["target_count"] == 1
    assert plan["target_rows"][0]["protein_id"] == "UniProtKB:P12345"
    assert plan["requests"][0]["accessions"] == ["P12345"]
    assert plan["requests"][0]["request_url"].startswith(
        "https://rest.uniprot.org/uniprotkb/search?"
    )
    assert plan["mapping_stage"]["mapped_unique_protein_count"] == 1
    out, memberships, mappings, blocked, receipt, plan_path = _paths(tmp_path)
    assert not any(path.exists() for path in (out, memberships, mappings, blocked, receipt, plan_path))


def raise_network_attempt() -> None:
    raise AssertionError("dry-run attempted a network fetch")


def test_offline_apply_writes_references_memberships_blocked_and_receipt(tmp_path: Path) -> None:
    responses = tmp_path / "responses.json"
    _responses(
        responses,
        [{"requested": ["P12345"], "results": [_entry("P12345", "CCCCCCCCCA")]}],
    )
    args, out, memberships, mappings, blocked, receipt = _prepare_apply(tmp_path, responses)

    assert fetcher.main(args) == 0

    references = _jsonl_rows(out)
    assert [row["protein_id"] for row in references] == ["UniProtKB:P12345"]
    assert references[0]["uniprot_release"] == "2026_03"
    membership_rows = _jsonl_rows(memberships)
    assert len(membership_rows) == 1
    assert membership_rows[0]["source_trait_id"] == "Pfam:PF00001"
    mapping_rows = _jsonl_rows(mappings)
    assert len(mapping_rows) == 1
    assert mapping_rows[0]["kind"] == fetcher.MAPPING_REGISTRY_KIND
    assert mapping_rows[0]["mapping_id"].startswith(fetcher.MAPPING_REGISTRY_ID_PREFIX)
    without_row_hash = dict(mapping_rows[0])
    observed_row_hash = without_row_hash.pop("mapping_row_sha256")
    assert observed_row_hash == mapper.value_sha256(without_row_hash)
    without_mapping_id = dict(without_row_hash)
    observed_mapping_id = without_mapping_id.pop("mapping_id")
    assert observed_mapping_id == (
        fetcher.MAPPING_REGISTRY_ID_PREFIX + mapper.value_sha256(without_mapping_id)
    )
    assert mapping_rows[0]["protein_id"] == "UniProtKB:P12345"
    assert mapping_rows[0]["sequence_sha256"] == references[0]["sequence_sha256"]
    assert mapping_rows[0]["uniprot_release"] == "2026_03"
    assert mapping_rows[0]["fetch_request_plan_id"].startswith(fetcher.PLAN_ID_PREFIX)
    assert mapping_rows[0]["mapped_residues"][0]["uniprot_position"] == 10
    assert blocked.read_text(encoding="utf-8") == (
        "protein_id\taccession\tcandidate_count\tcandidate_ids\t"
        "trait_ids\treason\tdetail\n"
    )
    value = json.loads(receipt.read_text(encoding="utf-8"))
    assert value["kind"] == fetcher.RECEIPT_KIND
    assert value["generation_boundary"] is True
    assert value["observed_uniprot_release"] == "2026_03"
    assert value["outputs"]["protein_registry"]["row_count"] == 1
    assert value["outputs"]["membership_registry"]["row_count"] == 1
    assert value["outputs"]["sifts_mapping_registry"]["row_count"] == 1
    assert value["outputs"]["blocked_registry"]["row_count"] == 0


def test_biolip_sifts_mapping_registry_loader_verifies_output_rows(tmp_path: Path) -> None:
    responses = tmp_path / "responses.json"
    _responses(
        responses,
        [{"requested": ["P12345"], "results": [_entry("P12345", "CCCCCCCCCA")]}],
    )
    args, _out, _memberships, mappings, _blocked, _receipt = _prepare_apply(
        tmp_path, responses
    )
    assert fetcher.main(args) == 0

    rows = _jsonl_rows(mappings)
    loaded = fetcher.load_mapping_registry(mappings)

    assert set(loaded) == {rows[0]["mapping_id"]}
    assert loaded[rows[0]["mapping_id"]] == rows[0]
    assert fetcher.mapping_entry_sha256(rows[0]) == rows[0]["mapping_row_sha256"]


def test_biolip_sifts_mapping_registry_rejects_tampered_rows(tmp_path: Path) -> None:
    responses = tmp_path / "responses.json"
    _responses(
        responses,
        [{"requested": ["P12345"], "results": [_entry("P12345", "CCCCCCCCCA")]}],
    )
    args, _out, _memberships, mappings, _blocked, _receipt = _prepare_apply(
        tmp_path, responses
    )
    assert fetcher.main(args) == 0

    [row] = _jsonl_rows(mappings)
    row["sequence_sha256"] = "0" * 64
    mappings.write_text(mapper.canonical_json(row) + "\n", encoding="utf-8")

    with pytest.raises(fetcher.RegistryBuildError, match="mapping_id digest mismatch"):
        fetcher.load_mapping_registry(mappings)


def test_biolip_sifts_mapping_registry_accepts_writer_canonical_non_ascii(
    tmp_path: Path,
) -> None:
    responses = tmp_path / "responses.json"
    _responses(
        responses,
        [{"requested": ["P12345"], "results": [_entry("P12345", "CCCCCCCCCA")]}],
    )
    args, _out, _memberships, mappings, _blocked, _receipt = _prepare_apply(
        tmp_path, responses
    )
    assert fetcher.main(args) == 0

    [row] = _jsonl_rows(mappings)
    row["source_stage_artifact"]["path"] = str(tmp_path / "josé" / "stage.jsonl")
    _write_readdressed_mapping(mappings, row)

    assert "josé" in mappings.read_text(encoding="utf-8")
    assert fetcher.load_mapping_registry(mappings)[row["mapping_id"]] == row


def test_biolip_sifts_mapping_registry_accepts_dna_xref_exception(
    tmp_path: Path,
) -> None:
    responses = tmp_path / "responses.json"
    _responses(
        responses,
        [{"requested": ["P12345"], "results": [_entry("P12345", "CCCCCCCCCA")]}],
    )
    args, _out, _memberships, mappings, _blocked, _receipt = _prepare_apply(
        tmp_path, responses
    )
    assert fetcher.main(args) == 0

    [row] = _jsonl_rows(mappings)
    _bind_source_ligand(
        row,
        ligand_id="dna",
        trait_id="proteintraitsmech:BIOLIP_DNA",
        trait_record_path=(
            "data/traits/structure/binding_site/biolip/dna-binding-site-dna.yaml"
        ),
        trait_source_xref_status="EXPLICIT_CURRENT_POLYMER_DNA_COLLISION_XREF_EXCEPTION",
        trait_source_xrefs=["CHEBI:16991", "pdb.ligand:DNA"],
    )
    _write_readdressed_mapping(mappings, row)

    assert fetcher.load_mapping_registry(mappings)[row["mapping_id"]] == row


@pytest.mark.parametrize(
    ("ligand_id", "trait_id", "trait_record_path", "trait_source_xrefs"),
    [
        (
            "dna",
            "proteintraitsmech:BIOLIP_DNA",
            "data/traits/structure/binding_site/biolip/dna-binding-site-dna.yaml",
            ["CHEBI:16991"],
        ),
        (
            "rna",
            "proteintraitsmech:BIOLIP_RNA",
            "data/traits/structure/binding_site/biolip/rna-binding-site-rna.yaml",
            ["CHEBI:33697"],
        ),
        (
            "peptide",
            "proteintraitsmech:BIOLIP_PEPTIDE",
            "data/traits/structure/binding_site/biolip/peptide-binding-site-peptide.yaml",
            ["CHEBI:16670"],
        ),
    ],
)
def test_biolip_sifts_mapping_registry_accepts_exact_polymer_xrefs(
    tmp_path: Path,
    ligand_id: str,
    trait_id: str,
    trait_record_path: str,
    trait_source_xrefs: list[str],
) -> None:
    responses = tmp_path / "responses.json"
    _responses(
        responses,
        [{"requested": ["P12345"], "results": [_entry("P12345", "CCCCCCCCCA")]}],
    )
    args, _out, _memberships, mappings, _blocked, _receipt = _prepare_apply(
        tmp_path, responses
    )
    assert fetcher.main(args) == 0

    [row] = _jsonl_rows(mappings)
    _bind_source_ligand(
        row,
        ligand_id=ligand_id,
        trait_id=trait_id,
        trait_record_path=trait_record_path,
        trait_source_xref_status="EXACT_SEEDER_SOURCE_XREFS",
        trait_source_xrefs=trait_source_xrefs,
    )
    _write_readdressed_mapping(mappings, row)

    assert fetcher.load_mapping_registry(mappings)[row["mapping_id"]] == row


@pytest.mark.parametrize(
    ("field_text", "expected"),
    [
        ("P12345-0", ("MALFORMED", ("P12345-0",))),
        ("P12345-01", ("MALFORMED", ("P12345-01",))),
        ("P12345-1", ("SINGLE", ("P12345-1",))),
    ],
)
def test_parse_source_uniprot_accessions_rejects_zero_isoforms(
    field_text: str,
    expected: tuple[str, tuple[str, ...]],
) -> None:
    assert fetcher._parse_source_uniprot_accessions(field_text) == expected


@pytest.mark.parametrize(
    "field_text",
    [
        "P12345",
        "P12345,Q9H9K5",
        "P12345,NOPE",
        "P12345-0",
        "-",
    ],
)
def test_biolip_sifts_mapping_registry_accepts_source_uniprot_provenance(
    tmp_path: Path,
    field_text: str,
) -> None:
    responses = tmp_path / "responses.json"
    _responses(
        responses,
        [{"requested": ["P12345"], "results": [_entry("P12345", "CCCCCCCCCA")]}],
    )
    args, _out, _memberships, mappings, _blocked, _receipt = _prepare_apply(
        tmp_path, responses
    )
    assert fetcher.main(args) == 0

    [row] = _jsonl_rows(mappings)
    status, accessions = fetcher._parse_source_uniprot_accessions(field_text)
    source_binding = row["source_projection"]["source_binding"]
    source_binding["source_uniprot_field_text"] = field_text
    source_binding["source_uniprot_claim_status"] = status
    source_binding["source_uniprot_accession_claims"] = list(accessions)
    _write_readdressed_mapping(mappings, row)

    assert fetcher.load_mapping_registry(mappings)[row["mapping_id"]] == row


@pytest.mark.parametrize("count_field", ["source_residue_count", "mapped_residue_count"])
def test_biolip_sifts_mapping_registry_rejects_boolean_counts(
    tmp_path: Path, count_field: str
) -> None:
    responses = tmp_path / "responses.json"
    _responses(
        responses,
        [{"requested": ["P12345"], "results": [_entry("P12345", "CCCCCCCCCA")]}],
    )
    args, _out, _memberships, mappings, _blocked, _receipt = _prepare_apply(
        tmp_path, responses
    )
    assert fetcher.main(args) == 0

    [row] = _jsonl_rows(mappings)
    row[count_field] = True
    _write_readdressed_mapping(mappings, row)

    with pytest.raises(fetcher.RegistryBuildError, match=rf"invalid {count_field}"):
        fetcher.load_mapping_registry(mappings)


def test_biolip_sifts_mapping_registry_rejects_boolean_manifest_size(
    tmp_path: Path,
) -> None:
    responses = tmp_path / "responses.json"
    _responses(
        responses,
        [{"requested": ["P12345"], "results": [_entry("P12345", "CCCCCCCCCA")]}],
    )
    args, _out, _memberships, mappings, _blocked, _receipt = _prepare_apply(
        tmp_path, responses
    )
    assert fetcher.main(args) == 0

    [row] = _jsonl_rows(mappings)
    manifest_entry = row["sifts_snapshot"]["sifts_manifest_entry"]
    manifest_entry["size_bytes"] = True
    row["sifts_snapshot"]["sifts_manifest_entry_sha256"] = mapper.value_sha256(
        manifest_entry
    )
    _write_readdressed_mapping(mappings, row)

    with pytest.raises(fetcher.RegistryBuildError, match="invalid size_bytes"):
        fetcher.load_mapping_registry(mappings)


@pytest.mark.parametrize(
    ("mutate", "match"),
    [
        pytest.param(
            lambda row: row["source_projection"].pop("source_occurrence_id"),
            "source projection is invalid",
            id="missing-source-occurrence-id",
        ),
        pytest.param(
            lambda row: row["source_projection"]["source_binding"][
                "source_occurrence_key"
            ].__setitem__("pdb_id", "2def"),
            "source occurrence PDB mismatch",
            id="pdb-key-mismatch",
        ),
        pytest.param(
            lambda row: row["source_projection"]["binding_residue_pairs"][
                0
            ].__setitem__("source_amino_acid", "G"),
            "source_amino_acid mismatch",
            id="binding-pair-residue-mismatch",
        ),
    ],
)
def test_biolip_sifts_mapping_registry_rejects_malformed_source_projection(
    tmp_path: Path, mutate, match: str
) -> None:
    responses = tmp_path / "responses.json"
    _responses(
        responses,
        [{"requested": ["P12345"], "results": [_entry("P12345", "CCCCCCCCCA")]}],
    )
    args, _out, _memberships, mappings, _blocked, _receipt = _prepare_apply(
        tmp_path, responses
    )
    assert fetcher.main(args) == 0

    [row] = _jsonl_rows(mappings)
    mutate(row)
    _write_readdressed_mapping(mappings, row)

    with pytest.raises(fetcher.RegistryBuildError, match=match):
        fetcher.load_mapping_registry(mappings)


def test_biolip_sifts_mapping_registry_rejects_source_uniprot_provenance_mismatch(
    tmp_path: Path,
) -> None:
    responses = tmp_path / "responses.json"
    _responses(
        responses,
        [{"requested": ["P12345"], "results": [_entry("P12345", "CCCCCCCCCA")]}],
    )
    args, _out, _memberships, mappings, _blocked, _receipt = _prepare_apply(
        tmp_path, responses
    )
    assert fetcher.main(args) == 0

    [row] = _jsonl_rows(mappings)
    source_binding = row["source_projection"]["source_binding"]
    source_binding["source_uniprot_field_text"] = "P12345,Q9H9K5"
    source_binding["source_uniprot_claim_status"] = "SINGLE"
    source_binding["source_uniprot_accession_claims"] = ["P12345"]
    _write_readdressed_mapping(mappings, row)

    with pytest.raises(fetcher.RegistryBuildError, match="claim status mismatch"):
        fetcher.load_mapping_registry(mappings)


def test_missing_exact_accession_is_blocked_not_substituted(tmp_path: Path) -> None:
    responses = tmp_path / "responses.json"
    _responses(responses, [{"requested": ["P12345"], "results": [_entry("Q9H9K5")]}])
    args, out, _memberships, mappings, blocked, _receipt = _prepare_apply(tmp_path, responses)

    assert fetcher.main(args) == 0

    assert _jsonl_rows(out) == []
    assert _jsonl_rows(mappings) == []
    assert "ACCESSION_NOT_RETURNED" in blocked.read_text(encoding="utf-8")


def test_fetched_sequence_must_replay_mapped_biolip_sifts_residues(tmp_path: Path) -> None:
    responses = tmp_path / "responses.json"
    _responses(
        responses,
        [{"requested": ["P12345"], "results": [_entry("P12345", "CCCCCCCCCK")]}],
    )
    args, out, _memberships, mappings, blocked, _receipt = _prepare_apply(tmp_path, responses)

    assert fetcher.main(args) == 0

    assert _jsonl_rows(out) == []
    assert _jsonl_rows(mappings) == []
    blocked_text = blocked.read_text(encoding="utf-8")
    assert "MAPPED_RESIDUE_VALIDATION_FAILED" in blocked_text
    assert "mapped position 10 expected A but fetched sequence has K" in blocked_text


def test_release_mismatch_fails_before_replacing_outputs(tmp_path: Path) -> None:
    responses = tmp_path / "responses.json"
    _responses(
        responses,
        [{"requested": ["P12345"], "results": [_entry("P12345")]}],
        release="2026_04",
    )
    args, out, memberships, mappings, blocked, receipt = _prepare_apply(
        tmp_path, responses, "--expect-release", "2026_03"
    )
    for path, marker in (
        (out, "old-registry\n"),
        (memberships, "old-memberships\n"),
        (mappings, "old-mappings\n"),
        (blocked, "old-blocked\n"),
        (receipt, "old-receipt\n"),
    ):
        path.write_text(marker, encoding="utf-8")

    assert fetcher.main(args) == 2

    assert out.read_text(encoding="utf-8") == "old-registry\n"
    assert memberships.read_text(encoding="utf-8") == "old-memberships\n"
    assert mappings.read_text(encoding="utf-8") == "old-mappings\n"
    assert blocked.read_text(encoding="utf-8") == "old-blocked\n"
    assert receipt.read_text(encoding="utf-8") == "old-receipt\n"


def test_apply_requires_exact_saved_plan(tmp_path: Path, capsys) -> None:
    responses = tmp_path / "responses.json"
    _responses(responses, [{"requested": ["P12345"], "results": []}])
    args, out, memberships, mappings, blocked, receipt = _prepare_apply(tmp_path, responses)

    without_plan = list(args)
    index = without_plan.index("--request-plan")
    del without_plan[index : index + 2]
    assert fetcher.main(without_plan) == 2
    assert "requires an exact saved --request-plan" in capsys.readouterr().err

    assert fetcher.main([*args, "--batch-size", "2"]) == 2
    assert "does not match rederived exact plan" in capsys.readouterr().err
    assert fetcher.main([*args, "--mapping-out", str(tmp_path / "moved-mappings.jsonl")]) == 2
    assert "does not match rederived exact plan" in capsys.readouterr().err
    assert not any(path.exists() for path in (out, memberships, mappings, blocked, receipt))


def test_sifts_release_must_match_expected_uniprot_release(tmp_path: Path, capsys) -> None:
    stage, snapshot = _write_inputs(tmp_path)
    out, memberships, mappings, blocked, receipt, _plan = _paths(tmp_path)
    args = [
        "--stage",
        str(stage),
        "--sifts-snapshot",
        str(snapshot),
        "--expect-release",
        "2026_04",
        "--out",
        str(out),
        "--membership-out",
        str(memberships),
        "--blocked",
        str(blocked),
        "--receipt",
        str(receipt),
    ]

    assert fetcher.main(args) == 2

    assert "does not match expected UniProt release" in capsys.readouterr().err
    assert not any(path.exists() for path in (out, memberships, mappings, blocked, receipt))


def test_outputs_must_not_overwrite_bound_inputs(tmp_path: Path, capsys) -> None:
    stage, snapshot = _write_inputs(tmp_path)
    out, memberships, mappings, blocked, receipt, _plan = _paths(tmp_path)

    assert (
        fetcher.main(
            [
                "--stage",
                str(stage),
                "--sifts-snapshot",
                str(snapshot),
                "--expect-release",
                "2026_03",
                "--out",
                str(stage),
                "--membership-out",
                str(memberships),
                "--mapping-out",
                str(mappings),
                "--blocked",
                str(blocked),
                "--receipt",
                str(receipt),
            ]
        )
        == 2
    )

    assert "output collides with BioLiP source stage" in capsys.readouterr().err
    assert not any(path.exists() for path in (out, memberships, mappings, blocked, receipt))
