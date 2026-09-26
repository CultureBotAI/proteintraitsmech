"""Native residue-frame, exact exemplar, and acquisition-boundary regressions."""

import copy
import hashlib
import importlib
import json
import sys
from dataclasses import replace
from pathlib import Path

import pytest

ROOT = next(path for path in Path(__file__).resolve().parents if (path / "pyproject.toml").is_file())
sys.path[:0] = [str(Path(__file__).parent), str(ROOT / "scripts")]
mcsa = importlib.import_module("mcsa_native_source")


def reference(sequence="MAGHCUY", protein_id="UniProtKB:P12345"):
    result = {
        "protein_id": protein_id, "protein_label": "Fixture enzyme",
        "taxon_id": "NCBITaxon:9606", "taxon_label": "Homo sapiens",
        "sequence": sequence, "sequence_length": len(sequence),
        "sequence_sha256": hashlib.sha256(sequence.encode()).hexdigest(),
        "reviewed": True, "uniprot_release": "2026_03", "sequence_version": 1,
    }
    if "-" in protein_id:
        result["isoform"] = int(protein_id.rsplit("-", 1)[1])
    return result


def record(protein_id="UniProtKB:P12345"):
    return {
        "identifier": "MCSA:1", "label": "Fixture enzyme",
        "definition": "An enzyme that catalyses the fixture reaction.",
        "definition_source": mcsa.DEFINITION_SOURCE, "trait_axis": "STRUCTURE",
        "trait_category": "STRUCT_ACTIVE_SITE", "term_kind": "CLASS", "license": mcsa.LICENSE,
        "canonical_examples": [{"protein_id": protein_id, "note": "Existing example"}],
    }


def entry(identifier=1, accession="P12345"):
    residues = []
    for position, code in [(2, "Ala"), (4, "His"), (7, "Tyr")]:
        residues.append({
            "mcsa_id": identifier, "function_location_abv": "", "main_annotation": "",
            "ptm": "", "residue_chains": [{"auth_resid": position + 100, "resid": position + 200}],
            "residue_sequences": [{"uniprot_id": accession, "resid": position,
                                   "code": code, "is_reference": True}],
            "roles": [], "roles_summary": "proton donor",
        })
    return {
        "mcsa_id": identifier, "enzyme_name": "Fixture enzyme",
        "is_reference_uniprot_id": True, "reference_uniprot_id": accession,
        "url": f"www.ebi.ac.uk/thornton-srv/m-csa/entry/{identifier}/",
        "description": "An <i>enzyme</i> that catalyses\n the fixture reaction.",
        "protein": {"sequences": [{"uniprot_id": accession}]},
        "all_ecs": [], "reaction": {}, "residues": residues,
    }


def test_native_uniprot_positions_preserve_discontinuous_set_and_ignore_pdb_numbering():
    source, ref, trait = entry(), reference(), record()
    before = copy.deepcopy((source, ref, trait))
    result = mcsa.locate_existing_site(trait, ref, source)
    assert result.residue_positions == (2, 4, 7)
    assert [(r.source_residue_index, r.position, r.amino_acid) for r in result.native_residues] == [
        (0, 2, "A"), (1, 4, "H"), (2, 7, "Y")]
    assert result.native_entry_sha256 == mcsa.value_sha256(source)
    assert result.protein_reference_sha256 == mcsa.value_sha256(ref)
    assert result.coordinate_frame == "UNIPROT_CANONICAL"
    assert (source, ref, trait) == before


def test_selenocysteine_is_checked_as_u_without_rewriting_to_cysteine():
    source = entry()
    source["residues"][1]["residue_sequences"][0].update(resid=6, code="Sec")
    result = mcsa.locate_existing_site(record(), reference(), source)
    assert result.residue_positions == (2, 6, 7)
    with pytest.raises(mcsa.McsaSourceError, match="residue disagrees"):
        mcsa.locate_existing_site(record(), reference("MAGHCCY"), source)


def test_exact_isoform_is_preserved_and_cannot_borrow_the_canonical_mapping():
    pid = "UniProtKB:P12345-2"
    result = mcsa.locate_existing_site(record(pid), reference(protein_id=pid), entry(accession="P12345-2"))
    assert result.coordinate_frame == "UNIPROT_ISOFORM"
    assert result.protein_id == pid
    with pytest.raises(mcsa.McsaSourceError, match="exact native reference"):
        mcsa.locate_existing_site(record(pid), reference(protein_id=pid), entry())


def test_partner_membership_does_not_supply_its_missing_catalytic_residues():
    source = entry()
    source["protein"]["sequences"].append({"uniprot_id": "Q12345"})
    source["reference_uniprot_id"] = "P12345, Q12345"
    assert mcsa.locate_existing_site(record(), reference(), source).residue_positions == (2, 4, 7)
    with pytest.raises(mcsa.McsaSourceError, match="complete unambiguous"):
        mcsa.locate_existing_site(record("UniProtKB:Q12345"),
                                 reference(protein_id="UniProtKB:Q12345"), source)


@pytest.mark.parametrize("change", ["missing", "homologue", "duplicate", "other_protein", "other_entry"])
def test_every_source_residue_must_map_once_to_this_reference(change):
    source = entry()
    residue = source["residues"][-1]
    mapping = residue["residue_sequences"][0]
    if change == "missing":
        residue["residue_sequences"] = []
    elif change == "homologue":
        mapping["is_reference"] = False
    elif change == "duplicate":
        residue["residue_sequences"].append(copy.deepcopy(mapping))
    elif change == "other_protein":
        mapping["uniprot_id"] = "Q12345"
    else:
        residue["mcsa_id"] = 2
    with pytest.raises(mcsa.McsaSourceError):
        mcsa.locate_existing_site(record(), reference(), source)


@pytest.mark.parametrize("field,value", [
    ("resid", 0), ("resid", -1), ("resid", 8), ("resid", True), ("resid", "2"),
    ("resid", 2.0), ("code", "Gly"), ("code", "Xaa"), ("code", "ALA"),
    ("is_reference", 1),
])
def test_wrong_position_amino_acid_or_reference_flag_is_rejected(field, value):
    source = entry()
    source["residues"][0]["residue_sequences"][0][field] = value
    with pytest.raises(mcsa.McsaSourceError):
        mcsa.locate_existing_site(record(), reference(), source)


@pytest.mark.parametrize("field,value", [
    ("identifier", "MCSA:2"), ("identifier", "M-CSA:1"),
    ("label", "Another enzyme"), ("definition", "A different reaction."),
    ("definition_source", "unreviewed source"), ("trait_axis", "FUNCTION"),
    ("trait_category", "STRUCT_BINDING_SITE"), ("term_kind", "INSTANCE"), ("license", "CC0"),
])
def test_native_trait_meaning_cannot_be_replaced(field, value):
    trait = record()
    trait[field] = value
    with pytest.raises(mcsa.McsaSourceError):
        mcsa.locate_existing_site(trait, reference(), entry())


@pytest.mark.parametrize("examples", [None, [], [{"protein_id": "UniProtKB:Q12345"}],
                                      [{"protein_id": "UniProtKB:P12345"}] * 2])
def test_site_requires_one_already_existing_exact_example(examples):
    trait = record()
    trait["canonical_examples"] = examples
    with pytest.raises(mcsa.McsaSourceError, match="existing examples"):
        mcsa.locate_existing_site(trait, reference(), entry())


@pytest.mark.parametrize("field,value", [
    ("sequence_length", 8), ("sequence_sha256", "a" * 64),
    ("sequence", "MAGHCAY"), ("uniprot_release", "unknown"), ("protein_id", "not-an-accession"),
])
def test_reference_sequence_and_metadata_are_validated(field, value):
    ref = reference()
    ref[field] = value
    with pytest.raises(mcsa.McsaSourceError, match="ProteinReference"):
        mcsa.locate_existing_site(record(), ref, entry())


def test_empty_native_site_and_truncated_description_are_held():
    source = entry()
    source["residues"] = []
    with pytest.raises(mcsa.McsaSourceError, match="no catalytic residues"):
        mcsa.locate_existing_site(record(), reference(), source)
    source, trait = entry(), record()
    source["description"] = trait["definition"] = "This enzyme has the following roles:"
    with pytest.raises(mcsa.McsaSourceError, match="incomplete"):
        mcsa.locate_existing_site(trait, reference(), source)


def capture(tmp_path, entries=None, second_entries=None, receipt_change=None,
            document_change=None, manifest_change=None):
    rows = entries if entries is not None else [entry(1), entry(2)]
    total = len(rows)
    pages = (total + 99) // 100
    generations = []
    stamp = "2026-09-17T04:02:11+00:00"
    for generation in range(2):
        generation_rows = rows if generation == 0 or second_entries is None else second_entries
        directory = mcsa.SOURCE_DIRECTORY + ("/verification" if generation else "")
        proofs = []
        for page in range(1, pages + 1):
            document = {
                "count": total, "next": mcsa.page_url(page + 1) if page < pages else None,
                "previous": mcsa.page_url(page - 1) if page > 1 else None,
                "results": generation_rows[(page - 1) * 100:page * 100],
            }
            if document_change:
                document_change(generation, page, document)
            raw = json.dumps(document).encode()
            path = tmp_path / directory / f"entries-page-{page:03}.json"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
            page_sha = hashlib.sha256(raw).hexdigest()
            receipt = {
                "bytes": len(raw), "content_type": "application/json", "destination": path.relative_to(tmp_path).as_posix(),
                "fetched_at": stamp, "requested_url": mcsa.page_url(page),
                "resolved_url": mcsa.page_url(page), "sha256": page_sha,
            }
            if receipt_change:
                receipt_change(receipt)
            receipt_path = Path(str(path) + ".fetch.json")
            receipt_raw = json.dumps(receipt).encode()
            receipt_path.write_bytes(receipt_raw)
            proofs.append({
                "page": page, "path": path.relative_to(tmp_path).as_posix(), "sha256": page_sha,
                "receipt_sha256": hashlib.sha256(receipt_raw).hexdigest(),
                "receipt_path": receipt_path.relative_to(tmp_path).as_posix(), "bytes": len(raw),
                "fetched_at": stamp,
            })
        generations.append(proofs)
    normalized = "".join(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n"
                         for row in sorted(rows, key=lambda row: row["mcsa_id"])).encode()
    source_path = tmp_path / mcsa.SOURCE_DIRECTORY / "entries.jsonl"
    source_path.write_bytes(normalized)
    normalized_sha = hashlib.sha256(normalized).hexdigest()
    manifest = {
        "scope": "Fixture acquisition", "total_entries": total, "pages_per_pass": pages,
        "new_requests": pages * 2 - 1, "requested_urls": [mcsa.page_url(n) for n in range(1, pages + 1)],
        "method": "GET", "fetcher": "scripts/fetch_source.py", "license": mcsa.LICENSE,
        "attribution": mcsa.ATTRIBUTION, "canary_sha256": generations[0][0]["sha256"],
        "observed_at_utc": stamp, "passes": generations, "complete_acquisitions_equal": True,
        "normalized_path": source_path.relative_to(tmp_path).as_posix(), "normalized_sha256": normalized_sha,
        "normalized_bytes": len(normalized), "legacy_source_sha256": "f" * 64,
        "unchanged_native_entries": total, "changed_native_entry_ids": [],
        "added_native_entry_ids": [], "missing_native_entry_ids": [],
    }
    if manifest_change:
        manifest_change(manifest)
    path = tmp_path / "acquisition.json"
    path.write_text(json.dumps(manifest))
    pins = mcsa.SourcePins(hashlib.sha256(path.read_bytes()).hexdigest(), normalized_sha)
    return path, pins


def test_complete_source_replay_crosses_page_boundary_and_binds_every_entry(tmp_path):
    path, pins = capture(tmp_path, [entry(n) for n in range(1, 102)])
    result = mcsa.read_verified_source(tmp_path, path, pins)
    assert set(result.entries) == set(range(1, 102))
    assert result.entries[101] == entry(101)
    assert result.source_release == f"M-CSA entries API; sha256:{pins.normalized_sha256}"


@pytest.mark.parametrize("target", ["manifest", "normalized", "first_page", "receipt", "second_pass"])
def test_acquisition_rejects_changed_bytes_even_outside_a_selected_entry(tmp_path, target):
    path, pins = capture(tmp_path)
    files = {
        "manifest": path,
        "normalized": tmp_path / mcsa.SOURCE_DIRECTORY / "entries.jsonl",
        "first_page": tmp_path / mcsa.SOURCE_DIRECTORY / "entries-page-001.json",
        "receipt": tmp_path / mcsa.SOURCE_DIRECTORY / "entries-page-001.json.fetch.json",
        "second_pass": tmp_path / mcsa.SOURCE_DIRECTORY / "verification/entries-page-001.json",
    }
    files[target].write_bytes(files[target].read_bytes() + b" ")
    with pytest.raises(mcsa.McsaSourceError, match="checksum"):
        mcsa.read_verified_source(tmp_path, path, pins)


@pytest.mark.parametrize("field,value", [
    ("requested_url", "https://example.org/entries"), ("resolved_url", "https://example.org/entries"),
    ("bytes", True), ("destination", "other.json"), ("fetched_at", "2026-09-17"),
    ("content_type", "text/html"),
])
def test_rehashed_receipt_must_still_bind_the_exact_official_api(tmp_path, field, value):
    path, pins = capture(tmp_path, receipt_change=lambda row: row.update({field: value}))
    with pytest.raises(mcsa.McsaSourceError):
        mcsa.read_verified_source(tmp_path, path, pins)


@pytest.mark.parametrize("field,value", [
    ("total_entries", True), ("pages_per_pass", 2), ("complete_acquisitions_equal", 1),
    ("license", "CC0"), ("attribution", "someone else"), ("method", "POST"),
    ("normalized_path", "../outside.jsonl"), ("normalized_bytes", True),
])
def test_rehashed_manifest_must_preserve_source_scope_and_completeness(tmp_path, field, value):
    path, pins = capture(tmp_path, manifest_change=lambda row: row.update({field: value}))
    with pytest.raises(mcsa.McsaSourceError):
        mcsa.read_verified_source(tmp_path, path, pins)


def test_two_complete_captures_must_agree_on_native_content(tmp_path):
    changed = entry(2)
    changed["description"] = "A source entry changed between pages."
    path, pins = capture(tmp_path, second_entries=[entry(1), changed])
    with pytest.raises(mcsa.McsaSourceError, match="acquisitions disagree"):
        mcsa.read_verified_source(tmp_path, path, pins)


def test_pagination_cannot_silently_skip_a_page(tmp_path):
    path, pins = capture(tmp_path, document_change=lambda generation, page, row: row.update(next=mcsa.page_url(3)))
    with pytest.raises(mcsa.McsaSourceError, match="pagination"):
        mcsa.read_verified_source(tmp_path, path, pins)


def test_native_duplicate_entry_ids_are_rejected(tmp_path):
    path, pins = capture(tmp_path, entries=[entry(1), entry(1)])
    with pytest.raises(mcsa.McsaSourceError, match="duplicate native entry"):
        mcsa.read_verified_source(tmp_path, path, pins)


def test_fixed_normalized_pin_cannot_be_replaced_by_manifest_content(tmp_path):
    path, pins = capture(tmp_path)
    with pytest.raises(mcsa.McsaSourceError, match="normalized source identity"):
        mcsa.read_verified_source(tmp_path, path, replace(pins, normalized_sha256="a" * 64))


def test_duplicate_json_keys_and_symlinked_pages_are_rejected(tmp_path):
    with pytest.raises(mcsa.McsaSourceError, match="duplicate JSON"):
        mcsa.strict_json('{"mcsa_id":1,"mcsa_id":2}')
    path, pins = capture(tmp_path)
    page = tmp_path / mcsa.SOURCE_DIRECTORY / "entries-page-001.json"
    moved = tmp_path / "original-page.json"
    page.rename(moved)
    page.symlink_to(moved)
    with pytest.raises(mcsa.McsaSourceError, match="regular file"):
        mcsa.read_verified_source(tmp_path, path, pins)
