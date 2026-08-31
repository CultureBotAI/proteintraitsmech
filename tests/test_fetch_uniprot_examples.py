"""Unit tests for the UniProt candidate-query dispatch."""

from __future__ import annotations

import sys
import json
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import fetch_uniprot_examples as F  # noqa: E402


def test_all_exact_signature_namespaces_have_uniprot_queries():
    identifiers = {
        "CDD:cd04983": "xref:cdd-cd04983",
        "CATH:2.60.40.10": "xref:gene3d-2.60.40.10",
        "HAMAP:MF_01987": "xref:hamap-MF_01987",
        "InterPro:IPR007110": "xref:interpro-IPR007110",
        "NCBIfam:NF033225": "xref:ncbifam-NF033225",
        "PANTHER:PTHR19343": "xref:panther-PTHR19343",
        "Pfam:PF07686": "xref:pfam-PF07686",
        "PRINTS:PR00347": "xref:prints-PR00347",
        "PROSITE:PS50835": "xref:prosite-PS50835",
        "SFLD:SFLDG01019": "xref:sfld-SFLDG01019",
        "SMART:SM00406": "xref:smart-SM00406",
        "SUPERFAMILY:SSF48726": "xref:supfam-SSF48726",
    }

    for identifier, expected in identifiers.items():
        assert F.build_queries({"identifier": identifier})[0][0] == expected


def test_cath_never_uses_the_nonexistent_raw_cath_query_key():
    queries = F.build_queries({"identifier": "CATH:2.60.40.10"})
    assert queries == [("xref:gene3d-2.60.40.10", "xref:gene3d-2.60.40.10")]
    assert all("xref:cath-" not in query for query, _note in queries)


def test_new_signature_cross_references_are_retained_on_candidate_metadata():
    entry = {
        "uniProtKBCrossReferences": [
            {"database": "CDD", "id": "cd04983"},
            {"database": "NCBIfam", "id": "NF033225"},
            {"database": "PANTHER", "id": "PTHR19343"},
            {"database": "PRINTS", "id": "PR00347"},
            {"database": "SFLD", "id": "SFLDG01019"},
            {"database": "SUPFAM", "id": "SSF48726"},
            {"database": "Gene3D", "id": "2.60.40.10"},
        ]
    }

    assert F._extract_family_curies(entry) == [
        "CDD:cd04983",
        "NCBIfam:NF033225",
        "PANTHER:PTHR19343",
        "PRINTS:PR00347",
        "SFLD:SFLDG01019",
        "SUPERFAMILY:SSF48726",
        "CATH:2.60.40.10",
    ]


def test_api_hit_is_a_candidate_not_a_canonical_example():
    record = {
        "identifier": "Pfam:PF07686",
        "trait_axis": "SEQUENCE",
        "trait_category": "SEQ_DOMAIN",
    }
    entry = {
        "primaryAccession": "A0A0D9RE97",
        "entryType": "UniProtKB reviewed (Swiss-Prot)",
        "proteinDescription": {
            "recommendedName": {"fullName": {"value": "Example protein"}}
        },
        "organism": {"taxonId": 9606, "scientificName": "Homo sapiens"},
        "sequence": {"length": 120},
        "annotationScore": 4.0,
    }

    row = F.entry_to_candidate(
        entry,
        record,
        "data/traits/sequence/domain/pfam/example.yaml",
        "xref:pfam-PF07686",
        "2026_03",
    )

    assert row["candidate_status"] == "PROTEIN_RESOLVED"
    assert row["qualification_status"] == "CANDIDATE_PROTEIN"
    assert row["source_trait_id"] == record["identifier"]
    assert row["evidence_tier"] == "A"
    assert row["scope"] == "LOCALIZED"
    assert "sequence" not in row
    assert row["candidate_id"].startswith("ug-")


def test_only_exact_whole_protein_xref_hits_enter_membership_batch():
    entry = {
        "primaryAccession": "P12345",
        "entryType": "UniProtKB reviewed (Swiss-Prot)",
        "proteinDescription": {
            "recommendedName": {"fullName": {"value": "Family protein"}}
        },
        "organism": {"taxonId": 9606, "scientificName": "Homo sapiens"},
        "sequence": {"length": 120},
    }
    whole = F.entry_to_candidate(
        entry,
        {
            "identifier": "PANTHER:PTHR12345",
            "trait_axis": "SEQUENCE",
            "trait_category": "SEQ_FAMILY",
        },
        "data/traits/sequence/family/panther/example.yaml",
        "xref:panther-PTHR12345",
        "2026_03",
    )
    localized = F.entry_to_candidate(
        entry,
        {
            "identifier": "Pfam:PF00001",
            "trait_axis": "SEQUENCE",
            "trait_category": "SEQ_DOMAIN",
        },
        "data/traits/sequence/domain/pfam/example.yaml",
        "xref:pfam-PF00001",
        "2026_03",
    )
    inherited = F.entry_to_candidate(
        entry,
        {
            "identifier": "proteintraitsmech:family-example",
            "trait_axis": "SEQUENCE",
            "trait_category": "SEQ_FAMILY",
            "parent_traits": ["PANTHER:PTHR12345"],
        },
        "data/traits/sequence/family/example.yaml",
        "xref:panther-PTHR12345",
        "2026_03",
    )
    disallowed = F.entry_to_candidate(
        entry,
        {
            "identifier": "PANTHER:PTHR12345",
            "trait_axis": "STRUCTURE",
            "trait_category": "FUNC_PROTEIN_FAMILY",
        },
        "data/traits/structure/example.yaml",
        "xref:panther-PTHR12345",
        "2026_03",
    )

    assert whole["batch"] == F.READY_MEMBERSHIP_BATCH
    assert whole["scope"] == "WHOLE_PROTEIN"
    assert whole["mapping_method"] == "SOURCE_MEMBERSHIP"
    assert whole["evidence_source"] == "UniProtKB"
    assert whole["source_trait_id"] == whole["trait_id"]
    assert localized["batch"] == F.NEEDS_OCCURRENCE_BATCH
    assert inherited["batch"] == F.NEEDS_OCCURRENCE_BATCH
    assert inherited["evidence_tier"] == "D"
    assert disallowed["scope"] == "WHOLE_PROTEIN"
    assert disallowed["batch"] == F.NEEDS_OCCURRENCE_BATCH


def test_candidate_writer_is_atomic_deterministic_jsonl(tmp_path):
    rows = [
        {"candidate_id": "ug-b", "trait_id": "Pfam:PF2", "protein_id": "UniProtKB:P2"},
        {"candidate_id": "ug-a", "trait_id": "Pfam:PF1", "protein_id": "UniProtKB:P1"},
    ]
    out = tmp_path / "candidates.jsonl"

    F.write_candidates(out, rows)
    first = out.read_bytes()
    F.write_candidates(out, list(reversed(rows)))

    assert out.read_bytes() == first
    assert [json.loads(line)["trait_id"] for line in out.read_text().splitlines()] == [
        "Pfam:PF1",
        "Pfam:PF2",
    ]


def test_apply_is_refused_before_any_trait_write(tmp_path):
    trait = tmp_path / "record.yaml"
    trait.write_text(
        "identifier: Pfam:PF07686\n"
        "label: Example\n"
        "trait_axis: SEQUENCE\n"
        "trait_category: SEQ_DOMAIN\n",
        encoding="utf-8",
    )
    before = trait.read_bytes()

    assert F.main([str(trait), "--apply"]) == 2
    assert trait.read_bytes() == before
