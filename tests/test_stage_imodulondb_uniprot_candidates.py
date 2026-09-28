"""Tests for staging iModulonDB rows against ProteinTraitsMech records."""

from __future__ import annotations

import importlib
import json
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
stage = importlib.import_module("stage_imodulondb_uniprot_candidates")


def _jsonl(path: pathlib.Path, rows: list[dict]) -> pathlib.Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n" for row in rows),
        encoding="utf-8",
    )
    return path


def _yaml(path: pathlib.Path, text: str) -> pathlib.Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _case(tmp_path: pathlib.Path) -> dict[str, pathlib.Path]:
    genes = _jsonl(
        tmp_path / "imodulondb" / "genes.jsonl",
        [
            {
                "organism": "e_coli",
                "dataset": "precise1k",
                "imodulon": 22,
                "gene_id": "b4062",
                "gene_locus": "b4062",
                "gene_name": "soxS",
                "gene_product": "DNA-binding transcriptional dual regulator SoxS",
                "weight": 0.262296982,
                "in_imodulon": True,
                "cog": "Transcription",
                "all_regulators": "SoxR, SoxS",
                "uniprot_id": "P0A9E2",
            },
            {
                "organism": "e_coli",
                "dataset": "precise1k",
                "imodulon": 22,
                "gene_id": "b2160",
                "gene_name": "yeiI",
                "gene_product": "putative sugar kinase YeiI",
                "weight": 0.01,
                "in_imodulon": False,
                "cog": "Carbohydrate transport and metabolism",
                "uniprot_id": "P33020",
            },
            {
                "organism": "e_coli",
                "dataset": "precise1k",
                "imodulon": 22,
                "gene_id": "b9999",
                "gene_name": "missing",
                "gene_product": "missing UniProt accession",
                "weight": 0.2,
                "in_imodulon": True,
            },
            {
                "organism": "e_coli",
                "dataset": "precise1k",
                "imodulon": 22,
                "gene_id": "b0001",
                "gene_name": "thrL",
                "gene_product": "thr operon leader peptide",
                "weight": 0.09,
                "in_imodulon": True,
                "uniprot_id": "P0AD86",
            },
        ],
    )
    registry = _jsonl(
        tmp_path / "data" / "grounding" / "protein_registry.jsonl",
        [
            {
                "protein_id": "UniProtKB:P0A9E2",
                "protein_label": "Regulatory protein SoxS",
                "taxon_id": "NCBITaxon:83333",
                "taxon_label": "Escherichia coli (strain K12)",
            },
            {
                "protein_id": "UniProtKB:P33020",
                "protein_label": "Putative kinase YeiI",
                "taxon_id": "NCBITaxon:83333",
                "taxon_label": "Escherichia coli (strain K12)",
            },
        ],
    )
    traits = tmp_path / "data" / "traits"
    _yaml(
        traits / "function" / "regulation" / "soxs.yaml",
        """\
identifier: proteintraitsmech:soxs_regulator
label: SoxS regulation
canonical_examples:
  - protein_id: UniProtKB:P0A9E2
""",
    )
    _yaml(
        traits / "function" / "stress" / "soxs.yaml",
        """\
identifier: proteintraitsmech:superoxide_response
label: superoxide response
canonical_examples:
  - protein_id: UniProtKB:P0A9E2
""",
    )
    return {"genes": genes, "registry": registry, "traits": traits}


def _rows(path: pathlib.Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_stage_joins_imodulondb_uniprot_rows_to_canonical_examples(tmp_path):
    case = _case(tmp_path)

    result = stage.stage(
        genes=stage.load_imodulondb_genes([case["genes"]]),
        references=stage.load_protein_registry(case["registry"]),
        record_examples=stage.load_record_examples(case["traits"]),
    )

    assert result.input_rows == 4
    assert [candidate.record.trait_id for candidate in result.candidates] == [
        "proteintraitsmech:soxs_regulator",
        "proteintraitsmech:superoxide_response",
    ]
    assert all(
        candidate.protein.protein_id == "UniProtKB:P0A9E2"
        for candidate in result.candidates
    )
    assert {blocked.reason for blocked in result.blocked} == {
        "NO_PROTEIN_REFERENCE",
        "NO_UNIPROT",
        "OUTSIDE_IMODULON",
    }


def test_cli_is_dry_run_by_default_and_writes_deterministic_outputs(tmp_path, capsys):
    case = _case(tmp_path)
    out = tmp_path / "reports" / "imodulondb"
    args = [
        "--genes",
        str(case["genes"]),
        "--protein-registry",
        str(case["registry"]),
        "--traits",
        str(case["traits"]),
        "--out",
        str(out),
    ]

    assert stage.main(args) == 0
    assert "dry run" in capsys.readouterr().out
    assert not out.exists()

    assert stage.main([*args, "--apply"]) == 0
    candidates = _rows(out / "candidates.jsonl")
    assert [row["trait_id"] for row in candidates] == [
        "proteintraitsmech:soxs_regulator",
        "proteintraitsmech:superoxide_response",
    ]
    candidates_tsv = (out / "candidates.tsv").read_text(encoding="utf-8")
    assert "trait_id" in candidates_tsv
    assert "proteintraitsmech:superoxide_response" in candidates_tsv
    assert {row["imodulon_key"] for row in candidates} == {"e_coli/precise1k/22"}
    assert {row["review_status"] for row in candidates} == {"NEEDS_REVIEW"}
    assert "computational transcriptomics context" in candidates[0]["evidence_guardrail"]

    blocked = (out / "blocked.tsv").read_text(encoding="utf-8")
    assert "NO_UNIPROT" in blocked
    assert "OUTSIDE_IMODULON" in blocked

    summary = (out / "summary.md").read_text(encoding="utf-8")
    assert "# iModulonDB ProteinTraits candidates" in summary
    assert "| NO_PROTEIN_REFERENCE | 1 |" in summary


def test_invalid_component_row_fails_closed(tmp_path, capsys):
    genes = _jsonl(
        tmp_path / "genes.jsonl",
        [
            {
                "organism": "e_coli",
                "dataset": "precise1k",
                "imodulon": True,
                "gene_id": "b4062",
                "weight": 0.2,
                "in_imodulon": True,
            }
        ],
    )

    assert stage.main(["--genes", str(genes), "--protein-registry", str(genes)]) == 2
    assert "imodulon must be an integer" in capsys.readouterr().err


def test_duplicate_candidate_key_fails_closed(tmp_path):
    case = _case(tmp_path)
    genes = stage.load_imodulondb_genes([case["genes"]])

    with pytest.raises(stage.ImodulonStageError, match="duplicate iModulonDB"):
        stage.stage(
            genes=[genes[0], genes[0]],
            references=stage.load_protein_registry(case["registry"]),
            record_examples=stage.load_record_examples(case["traits"]),
        )
