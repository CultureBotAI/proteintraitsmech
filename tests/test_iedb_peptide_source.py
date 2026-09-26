"""Native acquisition and sequence-frame regressions for IEDB peptide candidates."""

from __future__ import annotations

import copy
import csv
import hashlib
import importlib
import io
import json
import sys
import zipfile
from dataclasses import replace
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
iedb = importlib.import_module("iedb_peptide_source")


def _reference(sequence="MACDEFGHIK", protein_id="UniProtKB:P12345"):
    result = {
        "protein_id": protein_id, "protein_label": "Fixture antigen",
        "taxon_id": "NCBITaxon:9606", "taxon_label": "Homo sapiens",
        "sequence": sequence, "sequence_length": len(sequence),
        "sequence_sha256": hashlib.sha256(sequence.encode()).hexdigest(),
        "reviewed": True, "uniprot_release": "2026_03",
    }
    if "-" in protein_id:
        result["isoform"] = int(protein_id.rsplit("-", 1)[1])
    return result


def _record(peptide="ACDEF", protein_id="UniProtKB:P12345"):
    return {
        "identifier": "IEDB:10", "label": f"epitope {peptide}",
        "definition": f"Linear peptide epitope {peptide} from fixture antigen.",
        "definition_source": "IEDB (epitope_full_v3)", "trait_axis": "SEQUENCE",
        "trait_category": "SEQ_EPITOPE", "term_kind": "CLASS", "sequence_pattern": peptide,
        "canonical_examples": [{"protein_id": protein_id, "note": "Existing example"}],
    }


def _native(peptide="ACDEF", parent="P12345", source="Q12345", start="200", end="204"):
    values = [""] * 32
    values[0] = "http://www.iedb.org/epitope/10"
    values[1] = "Linear peptide"
    values[2] = peptide
    values[5], values[6] = start, end
    values[10] = f"http://www.uniprot.org/uniprot/{source}"
    values[12] = f"http://www.uniprot.org/uniprot/{parent}"
    return iedb.NativeRow(1, tuple(values))


def _change_row(row, column, value):
    values = list(row.values)
    values[column] = value
    return replace(row, values=tuple(values))


def _export(tmp_path, native_rows=None, *, header=None, trailing_row=None):
    text = io.StringIO(newline="")
    writer = csv.writer(text)
    writer.writerow(iedb.GROUP_HEADER)
    writer.writerow(iedb.COLUMN_HEADER if header is None else header)
    for row in native_rows or [_native()]:
        writer.writerow(row.values)
    if trailing_row is not None:
        writer.writerow(trailing_row)
    csv_bytes = text.getvalue().encode()
    archive = tmp_path / "source.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as output:
        output.writestr(iedb.CSV_MEMBER, csv_bytes)
    archive_sha = hashlib.sha256(archive.read_bytes()).hexdigest()
    receipt = tmp_path / "source.zip.fetch.json"
    receipt.write_text(json.dumps({
        "bytes": archive.stat().st_size, "content_type": "application/zip",
        "destination": str(archive), "fetched_at": "2026-09-16T22:39:43+00:00",
        "requested_url": iedb.SOURCE_URL, "resolved_url": iedb.SOURCE_URL,
        "sha256": archive_sha,
    }))
    pins = iedb.ExportPins(
        archive_sha, hashlib.sha256(csv_bytes).hexdigest(),
        hashlib.sha256(receipt.read_bytes()).hexdigest(),
    )
    return archive, receipt, pins


def test_verified_export_binds_complete_member_and_raw_rows(tmp_path):
    first = _change_row(_native(), 9, "Protein with comma, newline\nand α character")
    second = _change_row(_native(), 0, "https://www.iedb.org/epitope/11")
    archive, receipt, pins = _export(tmp_path, [first, second])
    result = iedb.read_verified_export(archive, receipt, pins, {"IEDB:10", "IEDB:99"})
    assert result.data_records_scanned == 2
    assert result.rows == {"IEDB:10": (first,)}
    assert result.rows["IEDB:10"][0].row_sha256 == iedb.value_sha256(list(first.values))
    assert result.source_release == f"epitope_full_v3; sha256:{pins.csv_sha256}"


@pytest.mark.parametrize("target", ["archive", "receipt", "csv_pin"])
def test_export_rejects_changed_bytes_or_pin(tmp_path, target):
    archive, receipt, pins = _export(tmp_path)
    if target == "archive":
        archive.write_bytes(archive.read_bytes() + b"tampered")
    elif target == "receipt":
        receipt.write_text(receipt.read_text() + "\n")
    else:
        pins = replace(pins, csv_sha256="a" * 64)
    with pytest.raises(iedb.IedbSourceError):
        iedb.read_verified_export(archive, receipt, pins, {"IEDB:10"})


@pytest.mark.parametrize("field,value", [
    ("requested_url", "https://example.org/source.zip"),
    ("resolved_url", "https://example.org/source.zip"),
    ("destination", "different.zip"), ("bytes", True),
    ("fetched_at", "2026-09-16"), ("fetched_at", "invalid"),
])
def test_rehashed_receipt_still_requires_official_acquisition_contract(tmp_path, field, value):
    archive, receipt, pins = _export(tmp_path)
    row = json.loads(receipt.read_text())
    row[field] = value
    receipt.write_text(json.dumps(row))
    pins = replace(pins, receipt_sha256=hashlib.sha256(receipt.read_bytes()).hexdigest())
    with pytest.raises(iedb.IedbSourceError):
        iedb.read_verified_export(archive, receipt, pins, {"IEDB:10"})


def test_rehashed_export_rejects_changed_column_semantics(tmp_path):
    header = list(iedb.COLUMN_HEADER)
    header[10], header[12] = header[12], header[10]
    args = _export(tmp_path, header=header)
    with pytest.raises(iedb.IedbSourceError, match="headers changed"):
        iedb.read_verified_export(*args, {"IEDB:10"})


def test_export_validates_rows_after_the_requested_epitope(tmp_path):
    args = _export(tmp_path, trailing_row=["malformed"])
    with pytest.raises(iedb.IedbSourceError, match="row 2"):
        iedb.read_verified_export(*args, {"IEDB:10"})


def test_duplicate_native_rows_are_retained_and_cannot_be_arbitrarily_selected(tmp_path):
    args = _export(tmp_path, [_native(), _native()])
    export = iedb.read_verified_export(*args, {"IEDB:10"})
    assert len(export.rows["IEDB:10"]) == 2
    with pytest.raises(iedb.IedbSourceError, match="exactly one native"):
        iedb.locate_existing_peptide(_record(), _reference(), export.rows["IEDB:10"])


def test_compute_positions_on_parent_without_transferring_other_antigen_positions():
    record, reference, native = _record(), _reference(), _native()
    before = copy.deepcopy((record, reference, native))
    match = iedb.locate_existing_peptide(record, reference, (native,))
    assert (match.start, match.end) == (2, 6)
    assert match.coordinate_frame == "UNIPROT_CANONICAL"
    assert match.protein_reference_sha256 == iedb.value_sha256(reference)
    assert match.native_row_sha256 == native.row_sha256
    assert (record, reference, native) == before


@pytest.mark.parametrize("column,value", [
    (0, "http://www.iedb.org/epitope/11"), (1, "Discontinuous peptide"),
    (2, "acdef"), (2, "ACDEG"), (3, "1"), (4, "phosphorylation"),
    (12, "http://www.uniprot.org/uniprot/Q12345"),
    (12, "http://www.uniprot.org/uniprot/P12345-2"),
])
def test_rejects_different_native_identity_peptide_or_modifications(column, value):
    native = _change_row(_native(), column, value)
    with pytest.raises(iedb.IedbSourceError):
        iedb.locate_existing_peptide(_record(), _reference(), (native,))


@pytest.mark.parametrize("sequence,peptide,error", [
    ("MFGHIKLMN", "ACDEF", "absent"),
    ("MACDEFACDEFG", "ACDEF", "multiple"),
    ("MAAAAAAG", "AAAAA", "multiple"),
])
def test_absent_and_repeated_matches_including_overlaps_are_held(sequence, peptide, error):
    with pytest.raises(iedb.IedbSourceError, match=error):
        iedb.locate_existing_peptide(
            _record(peptide), _reference(sequence), (_native(peptide),)
        )


@pytest.mark.parametrize("start,end", [("3", "7"), ("2", ""), ("", "6"), ("0", "4")])
def test_conflicting_or_partial_native_positions_on_same_protein_are_held(start, end):
    native = _native(source="P12345", start=start, end=end)
    with pytest.raises(iedb.IedbSourceError, match="native coordinates"):
        iedb.locate_existing_peptide(_record(), _reference(), (native,))


@pytest.mark.parametrize("start,end", [("2", "6"), ("", "")])
def test_same_protein_native_positions_can_agree_or_be_unreported(start, end):
    native = _native(source="P12345", start=start, end=end)
    match = iedb.locate_existing_peptide(_record(), _reference(), (native,))
    assert (match.start, match.end) == (2, 6)


def test_isoform_identity_is_preserved_and_never_collapsed_to_canonical():
    pid = "UniProtKB:P12345-2"
    record, reference = _record(protein_id=pid), _reference(protein_id=pid)
    native = _native(parent="P12345-2", source="P12345", start="200", end="204")
    match = iedb.locate_existing_peptide(record, reference, (native,))
    assert match.protein_id == pid
    assert match.coordinate_frame == "UNIPROT_ISOFORM"
    with pytest.raises(iedb.IedbSourceError, match="native parent"):
        iedb.locate_existing_peptide(record, reference, (_native(),))


@pytest.mark.parametrize("field,value", [
    ("sequence_length", 9), ("sequence_sha256", "a" * 64),
    ("sequence", "ACDEF"), ("uniprot_release", "unknown"),
])
def test_incomplete_or_inconsistent_protein_references_cannot_localize(field, value):
    reference = _reference()
    reference[field] = value
    with pytest.raises(iedb.IedbSourceError, match="ProteinReference"):
        iedb.locate_existing_peptide(_record(), reference, (_native(),))


@pytest.mark.parametrize("examples", [[], [{"protein_id": "UniProtKB:Q12345"}],
                                      [{"protein_id": "UniProtKB:P12345"}] * 2])
def test_location_requires_one_already_existing_exact_example(examples):
    record = _record()
    record["canonical_examples"] = examples
    with pytest.raises(iedb.IedbSourceError, match="existing examples"):
        iedb.locate_existing_peptide(record, _reference(), (_native(),))


@pytest.mark.parametrize("uri", [
    "https://example.org/uniprot/P12345", "https://www.uniprot.org/uniprot/P12345.1",
    "https://www.uniprot.org/uniprot/P12345?x=1", "https://www.uniprot.org/uniprot/P12345#x",
    "https://www.uniprot.org/uniprot/P12345/extra", "http://uniprot.org.evil/uniprot/P12345",
])
def test_identifiers_are_exact_uris_without_version_or_query_rewriting(uri):
    assert iedb.uniprot_id(uri) is None
