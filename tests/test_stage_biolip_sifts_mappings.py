"""Fail-closed BioLiP source-to-SIFTS mapping tests."""

from __future__ import annotations

import gzip
import importlib
import json
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

mapper = importlib.import_module("stage_biolip_sifts_mappings")


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
            "structure_id": f"PDB:{pdb_id}",
            "source_raw_line_sha256": "0" * 64,
            "source_occurrence_key": {
                "binding_site_code": "BS01",
                "ligand_chain": "X",
                "ligand_id": ligand,
                "ligand_serial_number": "1",
                "pdb_id": pdb_id,
                "receptor_chain": "A",
            },
        },
        "trait_binding": {
            "trait_id": f"proteintraitsmech:BIOLIP_{ligand}",
            "trait_record_path": f"data/traits/structure/binding_site/biolip/{ligand}.yaml",
            "trait_record_sha256": "1" * 64,
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


def _write_inputs(tmp_path: Path) -> tuple[Path, Path]:
    stage = tmp_path / "stage.jsonl"
    snapshot = tmp_path / "snapshot"
    snapshot.mkdir()
    rows = [
        _occurrence("occurrence:ok", "1abc", "OK", 1),
        _occurrence("occurrence:blocked", "1abc", "BAD", 2),
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
    xml = gzip.compress(_sifts_xml("1abc"))
    xml_path = snapshot / "1abc.xml.gz"
    xml_path.write_bytes(xml)
    manifest = {
        "schema_version": 1,
        "kind": mapper.SNAPSHOT_KIND,
        "complete": True,
        "entries": [
            {
                "path": "1abc.xml.gz",
                "pdb_id": "1abc",
                "sha256": __import__("hashlib").sha256(xml).hexdigest(),
                "sifts_entry_date": "2026-09-27",
                "sifts_uniprot_release": "2026_03",
                "sifts_uniprot_version": "2026.03",
                "size_bytes": len(xml),
                "url": f"{mapper.SIFTS_XML_ROOT}/1abc.xml.gz",
            }
        ],
        "failures": [],
        "fetch_request_count": 1,
        "requested_pdb_count": 1,
        "snapshot_id": "fixture",
        "source": "PDBe SIFTS residue-level XML",
        "source_root": mapper.SIFTS_XML_ROOT,
        "stage_combined_non_summary_rows_sha256": "fixture",
        "stage_id": "biolip-missing-protein-stage:fixture",
        "stage_path": "stage.jsonl",
        "stage_sha256": __import__("hashlib").sha256(stage.read_bytes()).hexdigest(),
    }
    (snapshot / "manifest.json").write_text(
        mapper.canonical_json(manifest) + "\n",
        encoding="utf-8",
    )
    return stage, snapshot


def _assert_content_address(
    row: dict[str, Any], *, id_field: str, prefix: str, row_hash_field: str
) -> None:
    without_row_hash = dict(row)
    observed_row_hash = without_row_hash.pop(row_hash_field)
    assert observed_row_hash == mapper.value_sha256(without_row_hash)
    without_id = dict(without_row_hash)
    observed_id = without_id.pop(id_field)
    assert observed_id == prefix + mapper.value_sha256(without_id)


def test_maps_complete_biolip_rows_and_retains_blockers(tmp_path: Path) -> None:
    stage, snapshot = _write_inputs(tmp_path)

    result = mapper.build_stage(source_stage=stage, sifts_snapshot=snapshot)

    assert len(result.mappings) == 1
    assert result.mappings[0]["protein_id"] == "UniProtKB:P12345"
    assert result.mappings[0]["residue_positions"] == [10]
    assert result.mappings[0]["expected_residues"] == "A"
    assert result.mappings[0]["qualification_claimed"] is False
    assert result.mappings[0]["mapping_method"] == "SIFTS_RESIDUE_MAPPING"

    assert len(result.blockers) == 1
    assert result.blockers[0]["blocking_reason"] == "AUTHOR_RESIDUE_NOT_IN_SIFTS"

    assert len(result.protein_requests) == 1
    assert result.protein_requests[0]["protein_id"] == "UniProtKB:P12345"

    for row in result.mappings:
        _assert_content_address(
            row,
            id_field="candidate_id",
            prefix="biolip-sifts-mapping-candidate:",
            row_hash_field="candidate_row_sha256",
        )
    for row in result.blockers:
        _assert_content_address(
            row,
            id_field="blocker_id",
            prefix="biolip-sifts-mapping-blocker:",
            row_hash_field="blocker_row_sha256",
        )
    for row in result.protein_requests:
        _assert_content_address(
            row,
            id_field="request_id",
            prefix="biolip-sifts-protein-reference-request:",
            row_hash_field="request_row_sha256",
        )

    rendered = mapper.render_stage(result)
    assert rendered == mapper.render_stage(result)
    decoded = [json.loads(line) for line in rendered.splitlines()]
    assert decoded == [*result.mappings, *result.blockers, *result.protein_requests, result.summary]


def test_incomplete_snapshot_refuses_to_map(tmp_path: Path) -> None:
    stage, snapshot = _write_inputs(tmp_path)
    manifest_path = snapshot / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["complete"] = False
    manifest_path.write_text(mapper.canonical_json(manifest) + "\n")

    assert mapper.main(["--stage", str(stage), "--sifts-snapshot", str(snapshot)]) == 2
