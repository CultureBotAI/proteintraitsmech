"""Release-pinned BioLiP/SIFTS UniProt reference fetch tests."""

from __future__ import annotations

import gzip
import hashlib
import importlib
import json
import sys
from pathlib import Path
from typing import Any

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
    rows = rows or [_occurrence("occurrence:ok", "1abc", "ATP", 1)]
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


def _paths(tmp_path: Path) -> tuple[Path, Path, Path, Path, Path]:
    return (
        tmp_path / "registry.jsonl",
        tmp_path / "memberships.jsonl",
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
    out, memberships, blocked, receipt, _plan = _paths(tmp_path)
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
) -> tuple[list[str], Path, Path, Path, Path]:
    out, memberships, blocked, receipt, plan = _paths(tmp_path)
    args = _dry_args(tmp_path, responses=responses, extra=extra)
    namespace = fetcher.parser().parse_args(args)
    prepared = fetcher._derive_request_plan(namespace)
    plan.write_text(fetcher.render_request_plan(prepared.plan), encoding="utf-8")
    return [*args, "--request-plan", str(plan), "--apply"], out, memberships, blocked, receipt


def _jsonl_rows(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


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
    out, memberships, blocked, receipt, plan_path = _paths(tmp_path)
    assert not any(path.exists() for path in (out, memberships, blocked, receipt, plan_path))


def raise_network_attempt() -> None:
    raise AssertionError("dry-run attempted a network fetch")


def test_offline_apply_writes_references_memberships_blocked_and_receipt(tmp_path: Path) -> None:
    responses = tmp_path / "responses.json"
    _responses(
        responses,
        [{"requested": ["P12345"], "results": [_entry("P12345", "CCCCCCCCCA")]}],
    )
    args, out, memberships, blocked, receipt = _prepare_apply(tmp_path, responses)

    assert fetcher.main(args) == 0

    references = _jsonl_rows(out)
    assert [row["protein_id"] for row in references] == ["UniProtKB:P12345"]
    assert references[0]["uniprot_release"] == "2026_03"
    membership_rows = _jsonl_rows(memberships)
    assert len(membership_rows) == 1
    assert membership_rows[0]["source_trait_id"] == "Pfam:PF00001"
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
    assert value["outputs"]["blocked_registry"]["row_count"] == 0


def test_missing_exact_accession_is_blocked_not_substituted(tmp_path: Path) -> None:
    responses = tmp_path / "responses.json"
    _responses(responses, [{"requested": ["P12345"], "results": [_entry("Q9H9K5")]}])
    args, out, _memberships, blocked, _receipt = _prepare_apply(tmp_path, responses)

    assert fetcher.main(args) == 0

    assert _jsonl_rows(out) == []
    assert "ACCESSION_NOT_RETURNED" in blocked.read_text(encoding="utf-8")


def test_fetched_sequence_must_replay_mapped_biolip_sifts_residues(tmp_path: Path) -> None:
    responses = tmp_path / "responses.json"
    _responses(
        responses,
        [{"requested": ["P12345"], "results": [_entry("P12345", "CCCCCCCCCK")]}],
    )
    args, out, _memberships, blocked, _receipt = _prepare_apply(tmp_path, responses)

    assert fetcher.main(args) == 0

    assert _jsonl_rows(out) == []
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
    args, out, memberships, blocked, receipt = _prepare_apply(
        tmp_path, responses, "--expect-release", "2026_03"
    )
    for path, marker in (
        (out, "old-registry\n"),
        (memberships, "old-memberships\n"),
        (blocked, "old-blocked\n"),
        (receipt, "old-receipt\n"),
    ):
        path.write_text(marker, encoding="utf-8")

    assert fetcher.main(args) == 2

    assert out.read_text(encoding="utf-8") == "old-registry\n"
    assert memberships.read_text(encoding="utf-8") == "old-memberships\n"
    assert blocked.read_text(encoding="utf-8") == "old-blocked\n"
    assert receipt.read_text(encoding="utf-8") == "old-receipt\n"


def test_apply_requires_exact_saved_plan(tmp_path: Path, capsys) -> None:
    responses = tmp_path / "responses.json"
    _responses(responses, [{"requested": ["P12345"], "results": []}])
    args, out, memberships, blocked, receipt = _prepare_apply(tmp_path, responses)

    without_plan = list(args)
    index = without_plan.index("--request-plan")
    del without_plan[index : index + 2]
    assert fetcher.main(without_plan) == 2
    assert "requires an exact saved --request-plan" in capsys.readouterr().err

    assert fetcher.main([*args, "--batch-size", "2"]) == 2
    assert "does not match rederived exact plan" in capsys.readouterr().err
    assert not any(path.exists() for path in (out, memberships, blocked, receipt))


def test_sifts_release_must_match_expected_uniprot_release(tmp_path: Path, capsys) -> None:
    stage, snapshot = _write_inputs(tmp_path)
    out, memberships, blocked, receipt, _plan = _paths(tmp_path)
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
    assert not any(path.exists() for path in (out, memberships, blocked, receipt))


def test_outputs_must_not_overwrite_bound_inputs(tmp_path: Path, capsys) -> None:
    stage, snapshot = _write_inputs(tmp_path)
    out, memberships, blocked, receipt, _plan = _paths(tmp_path)

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
                "--blocked",
                str(blocked),
                "--receipt",
                str(receipt),
            ]
        )
        == 2
    )

    assert "output collides with BioLiP source stage" in capsys.readouterr().err
    assert not any(path.exists() for path in (out, memberships, blocked, receipt))
