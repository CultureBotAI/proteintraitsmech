"""Scientific scope, exact source identity, and promotion regression checks."""

from __future__ import annotations

import copy
import json
import sys
import zipfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import elife_metallophore_grounding as grounding
import elife_metallophores as source
from validate_uniprot_grounding import validate_grounding_evidence, validate_record
from analyze_elife_metallophores import workbook


def example_fixture():
    fact = {"model": "EntA", "trait_id": source.PREFIX + "EntA",
            "source_kind": "seed_alignment", "source_release": source.RELEASE,
            "archive_url": source.ARCHIVE_URL, "archive_sha256": source.ARCHIVE_SHA256,
            "alignment_path": source.BASE + "alignments/EntA.clw",
            "alignment_sha256": "a" * 64, "source_header": "sp|P15047|ENTA_ECOLI",
            "source_sequence": "MAAC", "source_namespace": "UniProtKB",
            "source_accession": "P15047"}
    fact["candidate_id"] = "elife109154:" + source.digest(fact)
    entry = {"primaryAccession": "P15047", "entryType": "UniProtKB reviewed (Swiss-Prot)",
             "proteinDescription": {"recommendedName": {"fullName": {"value": "EntA"}}},
             "organism": {"taxonId": 83333, "scientificName": "Escherichia coli"},
             "sequence": {"value": "MAAC", "length": 4}, "entryAudit": {"sequenceVersion": 1}}
    body = json.dumps(entry)
    response = {"request_url": "https://rest.uniprot.org/uniprotkb/P15047.json", "body": body,
                "body_sha256": source.sha256(body.encode()),
                "headers": {"x-uniprot-release": grounding.UNIPROT_RELEASE}}
    record = {"identifier": fact["trait_id"], "definition": "EntA sequence family.",
              "trait_axis": "SEQUENCE", "trait_category": "SEQ_FAMILY"}
    row = grounding.resolve_response(fact, response, record)
    record["canonical_examples"] = [row["example"]]
    return row, record, response, fact


def test_duplicate_clustal_rows_do_not_double_the_protein():
    text = "CLUSTAL\n\np MA-c\np MA-c\nq MA.c\n\np dE\nq DE\n"
    assert source.parse_alignment(text) == {"p": "MACDE", "q": "MACDE"}


def test_duplicate_fasta_rows_must_be_identical():
    assert source.parse_alignment(">p\nMAAC\n>p\nMAAC\n") == {"p": "MAAC"}
    with pytest.raises(ValueError, match="conflicting duplicate"):
        source.parse_alignment(">p\nMAAC\n>p\nMAAD\n")


def test_stockholm_insert_residues_are_preserved():
    text = "# STOCKHOLM 1.0\np MAac.-D\n#=GR p PP 9999\n//\n"
    assert source.parse_alignment(text)["p"] == "MAACD"


def test_bgc_parser_requires_a_positive_reported_profile_above_cutoff():
    template = '''     CDS             1..12
                     /protein_id="WP_000000001.1"
                     /sec_met_domain="{model} (E-value: 1e-90, bitscore: {score},
                     seeds: 5, tool: rule-based-clusters)"
                     /translation="MAAC"
'''
    models = {"EntA": {"bitscore_cutoff": 205}}
    assert source.parse_bgc_proteins(template.format(model="EntA", score=204), models) == []
    assert source.parse_bgc_proteins(template.format(model="KtzT", score=900), models) == []
    rows = source.parse_bgc_proteins(template.format(model="EntA", score=205), models)
    assert rows[0]["protein_id"] == "WP_000000001.1"


def test_chelator_products_and_negative_constraints_are_not_new_protein_classes():
    catalog = source.catalog()
    assert len(catalog["traits"]) == 20
    assert set(catalog["traits"]) == set(source.POSITIVE_CUTOFFS)
    assert not set(catalog["excluded_models"]) & set(catalog["traits"])
    assert catalog["traits"]["CyanoBH_Asp2"]["category"] == "SEQ_DOMAIN"


def test_source_sequence_membership_passes_without_invented_coordinates():
    row, record, _, _ = example_fixture()
    with grounding.assertion_context([row["assertion"]]):
        assert not validate_record(record, {row["reference"]["protein_id"]: row["reference"]},
                                   evidence_registry={row["evidence"]["evidence_id"]: row["evidence"]},
                                   require_qualified=True)
    assert "intervals" not in row["example"]["trait_occurrences"][0]


@pytest.mark.parametrize("mutation", ["sequence", "release", "accession"])
def test_exact_response_disagreement_is_rejected(mutation):
    _, record, response, fact = example_fixture()
    record.pop("canonical_examples")
    if mutation == "release":
        response["headers"]["x-uniprot-release"] = "2020_01"
    else:
        body = json.loads(response["body"])
        if mutation == "sequence":
            body["sequence"]["value"] = "MAAD"
        else:
            body["primaryAccession"] = "P39071"
        response["body"] = json.dumps(body)
        response["body_sha256"] = source.sha256(response["body"].encode())
    with pytest.raises(ValueError):
        grounding.resolve_response(fact, response, record)


def test_staged_assertion_cannot_qualify_a_different_family_or_domain():
    row, _, _, _ = example_fixture()
    with grounding.assertion_context([row["assertion"]]):
        changed = copy.deepcopy(row["evidence"])
        changed["trait_id"] = source.PREFIX + "GrbD"
        assert grounding.contract_errors(changed)
        changed = copy.deepcopy(row["evidence"])
        changed["scope"] = "LOCALIZED"
        assert grounding.contract_errors(changed)


@pytest.mark.parametrize("field,value", [
    ("definition", "A different enzyme family."),
    ("trait_category", "SEQ_DOMAIN"),
    ("trait_axis", "FUNCTION"),
])
def test_review_binding_rejects_changed_trait_meaning(field, value):
    row, record, _, _ = example_fixture()
    record[field] = value
    with grounding.assertion_context([row["assertion"]]):
        assert grounding.record_errors(record, row["reference"], row["evidence"])


def test_metadata_cannot_be_swapped_under_the_same_sequence():
    row, record, _, _ = example_fixture()
    reference = dict(row["reference"], taxon_id="NCBITaxon:9606")
    with grounding.assertion_context([row["assertion"]]):
        assert grounding.record_errors(record, reference, row["evidence"])


def test_missing_receipt_keeps_this_provider_closed(monkeypatch, tmp_path):
    row, _, _, _ = example_fixture()
    monkeypatch.setattr(grounding, "ROOT", tmp_path)
    findings = validate_grounding_evidence(row["evidence"], path=Path("test"), line=1)
    assert "elife_metallophore_source_contract" in {f.code for f in findings}


def test_corrupt_source_assertion_is_rejected():
    row, _, _, _ = example_fixture()
    row["assertion"]["source_fact"]["source_header"] = "sp|P39071|DHBA_BACSU"
    with grounding.assertion_context([row["assertion"]]):
        assert grounding.contract_errors(row["evidence"])


def test_xlsx_cached_formulas_preserve_false_booleans_and_text(tmp_path):
    path = tmp_path / "source.xlsx"
    namespace = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("xl/workbook.xml", f'''<workbook xmlns="{namespace}"
          xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
          <sheets><sheet name="test" r:id="rId1"/></sheets></workbook>''')
        archive.writestr("xl/_rels/workbook.xml.rels",
                         '<Relationships><Relationship Id="rId1" Target="worksheets/sheet1.xml"/></Relationships>')
        archive.writestr("xl/worksheets/sheet1.xml", f'''<worksheet xmlns="{namespace}">
          <sheetData><row r="1"><c r="A1" t="b"><f>1=2</f><v>0</v></c>
          <c r="B1" t="str"><f>IF(A1,"TP","TN")</f><v>TN</v></c>
          <c r="C1"><v>1E-5</v></c></row></sheetData></worksheet>''')
    assert workbook(path)["test"] == [{"A": False, "B": "TN", "C": 1e-5}]
