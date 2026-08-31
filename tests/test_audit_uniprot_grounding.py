"""Focused probes for the fail-closed UniProt grounding audit."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "audit_uniprot_grounding.py"
sys.path.insert(0, str(REPO / "scripts"))
SPEC = importlib.util.spec_from_file_location("audit_uniprot_grounding", SCRIPT)
assert SPEC and SPEC.loader
A = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = A
SPEC.loader.exec_module(A)

import validate_uniprot_grounding as V  # noqa: E402
import uniprot_membership_snapshot as M  # noqa: E402


def _record(traits: Path, name: str, text: str) -> None:
    path = traits / "sequence" / "domain" / "fixture" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value), encoding="utf-8")


def _jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "".join(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n" for row in rows),
        encoding="utf-8",
    )


def _authoritative_fixture(
    root: Path,
    *,
    trait_id: str = "PROSITE:PS00001",
    source_trait_id: str | None = None,
) -> tuple[Path, Path, Path, dict, dict]:
    """Write one validator-proven record and its two authoritative registries."""
    sequence = "MSTACDEFGHIKLMNPQRSTVWY"
    sequence_sha256 = hashlib.sha256(sequence.encode("ascii")).hexdigest()
    source_trait_id = source_trait_id or trait_id
    occurrence = {
        "trait_id": trait_id,
        "protein_id": "UniProtKB:P12345",
        "scope": "LOCALIZED",
        "coordinate_frame": "UNIPROT_CANONICAL",
        "intervals": [{"start": 2, "end": 4, "expected_sequence": "STA"}],
        "source_trait_id": source_trait_id,
        "mapping_method": "INTERPRO_MATCH",
        "evidence_source": "InterPro",
        "source_release": "109.0",
        "sequence_sha256": sequence_sha256,
        "qualification_status": "QUALIFIED",
    }
    if source_trait_id != trait_id:
        occurrence["inheritance_path"] = [source_trait_id, trait_id]
    evidence = V.build_grounding_evidence(
        occurrence,
        provider_kind="INTERPRO",
        provider_source="data/raw/interpro/protein2ipr.json",
        provider_release="109.0",
        provider_entry_sha256=hashlib.sha256(b"exact provider row").hexdigest(),
    )
    occurrence["source_evidence_id"] = evidence["evidence_id"]
    reference = {
        "protein_id": "UniProtKB:P12345",
        "protein_label": "Example protein",
        "taxon_id": "NCBITaxon:9606",
        "taxon_label": "Homo sapiens",
        "sequence": sequence,
        "sequence_length": len(sequence),
        "sequence_sha256": sequence_sha256,
        "reviewed": True,
        "uniprot_release": "2026_02",
    }
    record = {
        "identifier": trait_id,
        "label": "example motif",
        "trait_axis": "SEQUENCE",
        "trait_category": "SEQ_MOTIF",
        "residue_sequence": "STA",
        "canonical_examples": [
            {
                "protein_id": "UniProtKB:P12345",
                "protein_label": "Example protein",
                "taxon_id": "NCBITaxon:9606",
                "taxon_label": "Homo sapiens",
                "sequence_length": len(sequence),
                "sequence_sha256": sequence_sha256,
                "uniprot_release": "2026_02",
                "qualification_status": "QUALIFIED",
                "source": "UNIPROT_GROUNDING",
                "trait_occurrences": [occurrence],
            }
        ],
    }
    traits = root / "traits"
    _record(
        traits,
        "qualified.yaml",
        yaml.safe_dump(record, sort_keys=False),
    )
    protein_registry = root / "protein_registry.jsonl"
    evidence_registry = root / "occurrence_evidence.jsonl"
    _jsonl(protein_registry, [reference])
    _jsonl(evidence_registry, [evidence])
    return traits, protein_registry, evidence_registry, record, evidence


def _membership_fixture(
    root: Path,
) -> tuple[Path, Path, Path, Path, dict, dict]:
    """Write one validator-proven UniProt SOURCE_MEMBERSHIP record."""
    sequence = "MSTACDEFGHIKLMNPQRSTVWY"
    sequence_sha256 = hashlib.sha256(sequence.encode("ascii")).hexdigest()
    trait_id = "PANTHER:PTHR12345"
    membership = M.extract_entry_memberships(
        {
            "uniProtKBCrossReferences": [
                {
                    "database": "PANTHER",
                    "id": "PTHR12345",
                    "properties": [{"key": "family", "value": "fixture"}],
                }
            ]
        },
        protein_id="UniProtKB:P12345",
        sequence_sha256=sequence_sha256,
        uniprot_release="2026_02",
    )[0]
    membership_registry = root / "uniprot_memberships.jsonl"
    membership_registry.write_text(M.dump_memberships([membership]), encoding="utf-8")
    occurrence = {
        "trait_id": trait_id,
        "protein_id": "UniProtKB:P12345",
        "scope": "WHOLE_PROTEIN",
        "source_trait_id": trait_id,
        "mapping_method": "SOURCE_MEMBERSHIP",
        "evidence_source": "UniProtKB",
        "source_release": "2026_02",
        "sequence_sha256": sequence_sha256,
        "qualification_status": "QUALIFIED",
    }
    evidence = V.build_grounding_evidence(
        occurrence,
        provider_kind="UNIPROT",
        provider_source=str(membership_registry.resolve()),
        provider_release="2026_02",
        provider_entry_sha256=M.membership_entry_sha256(membership),
    )
    occurrence["source_evidence_id"] = evidence["evidence_id"]
    reference = {
        "protein_id": "UniProtKB:P12345",
        "protein_label": "Example protein",
        "taxon_id": "NCBITaxon:9606",
        "taxon_label": "Homo sapiens",
        "sequence": sequence,
        "sequence_length": len(sequence),
        "sequence_sha256": sequence_sha256,
        "reviewed": True,
        "uniprot_release": "2026_02",
    }
    record = {
        "identifier": trait_id,
        "label": "example protein family",
        "trait_axis": "FUNCTION",
        "trait_category": "FUNC_PROTEIN_FAMILY",
        "canonical_examples": [
            {
                "protein_id": "UniProtKB:P12345",
                "protein_label": "Example protein",
                "taxon_id": "NCBITaxon:9606",
                "taxon_label": "Homo sapiens",
                "sequence_length": len(sequence),
                "sequence_sha256": sequence_sha256,
                "uniprot_release": "2026_02",
                "qualification_status": "QUALIFIED",
                "source": "UNIPROT_GROUNDING",
                "trait_occurrences": [occurrence],
            }
        ],
    }
    traits = root / "traits"
    _record(traits, "qualified-membership.yaml", yaml.safe_dump(record, sort_keys=False))
    protein_registry = root / "protein_registry.jsonl"
    evidence_registry = root / "occurrence_evidence.jsonl"
    _jsonl(protein_registry, [reference])
    _jsonl(evidence_registry, [evidence])
    return (
        traits,
        protein_registry,
        evidence_registry,
        membership_registry,
        membership,
        evidence,
    )


def _inputs(tmp_path: Path) -> tuple[Path, Path, Path, Path]:
    traits = tmp_path / "traits"
    # Deliberately malformed below the three routing fields.  No-example records
    # must stay on the cheap scanner, so this still audits successfully.
    _record(
        traits,
        "a-no-protein.yaml",
        "identifier: Pfam:PF00001\n"
        "trait_axis: SEQUENCE\n"
        "trait_category: SEQ_DOMAIN\n"
        "deliberately malformed: [\n",
    )
    _record(
        traits,
        "b-invalid-protein.yaml",
        "identifier: Pfam:PF_NO_MATCH\n"
        "trait_axis: SEQUENCE\n"
        "trait_category: SEQ_DOMAIN\n"
        "canonical_examples:\n"
        "- protein_id: UniProtKB:UNS0001\n"
        "  protein_label: placeholder\n",
    )
    _record(
        traits,
        "c-organism-missing.yaml",
        "identifier: Pfam:PF00002\n"
        "trait_axis: SEQUENCE\n"
        "trait_category: SEQ_DOMAIN\n"
        "canonical_examples:\n"
        "- protein_id: UniProtKB:P12345\n"
        "  protein_label: Existing carrier\n",
    )
    _record(
        traits,
        "d-sequence-missing.yaml",
        "identifier: fixture:NO_SEQUENCE\n"
        "trait_axis: SEQUENCE\n"
        "trait_category: SEQ_DOMAIN\n"
        "canonical_examples:\n"
        "- protein_id: UniProtKB:P22222\n"
        "  protein_label: Protein two\n"
        "  taxon_id: NCBITaxon:2\n"
        "  taxon_label: Bacterium two\n",
    )
    _record(
        traits,
        "e-coordinate-missing.yaml",
        "identifier: fixture:NO_COORDINATE\n"
        "trait_axis: SEQUENCE\n"
        "trait_category: SEQ_DOMAIN\n"
        "canonical_examples:\n"
        "- protein_id: UniProtKB:P33333\n"
        "  protein_label: Protein three\n"
        "  taxon_id: NCBITaxon:3\n"
        "  taxon_label: Bacterium three\n"
        "  sequence_length: 6\n"
        "  sequence: ACDEFG\n"
        "  features:\n"
        "  - start: 2\n"
        "    end: 4\n"
        "    trait_category: SEQ_MOTIF\n",
    )
    _record(
        traits,
        "f-strict-shape.yaml",
        "identifier: fixture:SHAPE_ONLY\n"
        "trait_axis: SEQUENCE\n"
        "trait_category: SEQ_DOMAIN\n"
        "canonical_examples:\n"
        "- protein_id: UniProtKB:P44444\n"
        "  protein_label: Protein four\n"
        "  taxon_id: NCBITaxon:4\n"
        "  taxon_label: Bacterium four\n"
        "  sequence_length: 6\n"
        "  sequence: ACDEFG\n"
        "  features:\n"
        "  - start: 2\n"
        "    end: 4\n"
        "    trait_category: SEQ_DOMAIN\n",
    )
    _record(
        traits,
        "g-qualified.yaml",
        "identifier: fixture:QUALIFIED\n"
        "trait_axis: SEQUENCE\n"
        "trait_category: SEQ_DOMAIN\n"
        "canonical_examples:\n"
        "- protein_id: UniProtKB:P55555\n"
        "  protein_label: Protein five\n"
        "  qualification_status: QUALIFIED\n"
        "  trait_occurrences:\n"
        "  - trait_id: fixture:QUALIFIED\n"
        "    protein_id: UniProtKB:P55555\n"
        "    qualification_status: QUALIFIED\n",
    )
    _record(
        traits,
        "h-whole-protein.yaml",
        "identifier: PANTHER:PTHR00001\n"
        "trait_axis: FUNCTION\n"
        "trait_category: FUNC_PROTEIN_FAMILY\n",
    )
    _record(
        traits,
        "i-out-of-bounds.yaml",
        "identifier: CDD:cd00001\ntrait_axis: SEQUENCE\ntrait_category: SEQ_DOMAIN\n",
    )

    residue = tmp_path / "residue.json"
    interpro = tmp_path / "interpro.json"
    profiles = tmp_path / "profiles.jsonl"
    sequences = {
        "P12345": "ACDEFG",
        "Q54321": "ACDEFG",
        "Q11111": "ACDEFG",
        "P99999": "ACDEFG",
    }
    _json(
        residue,
        {
            "_meta": {
                "schema": 1,
                "source": "UniProt",
                "release": "2026_02",
                "absent": ["P22222"],
            },
            "proteins": {key: {"seq": value, "ft": []} for key, value in sequences.items()},
        },
    )
    _json(
        interpro,
        {
            "_meta": {"schema": 1, "source": "InterPro", "release": "109.0"},
            "proteins": {
                "P12345": {"Pfam:PF00001": [[2, 4]], "Pfam:PF00002": [[1, 6]]},
                "Q54321": {"Pfam:PF00001": [[1, 3], [5, 6]]},
                "Q11111": {"PANTHER:PTHR00001": [[1, 6]]},
                "P99999": {"CDD:cd00001": [[1, 7]]},
            },
        },
    )
    profile_rows = [
        {
            "accession": f"UniProtKB:{accession}",
            "name": f"Protein {accession}",
            "taxon": "NCBITaxon:9606",
            "taxon_label": "Homo sapiens",
            "length": len(sequence),
            "reviewed": True,
        }
        for accession, sequence in sequences.items()
    ]
    profiles.write_text("".join(json.dumps(row) + "\n" for row in profile_rows), encoding="utf-8")
    return traits, residue, interpro, profiles


def _read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def test_audit_is_fail_closed_and_emits_exact_candidates(tmp_path):
    traits, residue, interpro, profiles = _inputs(tmp_path)
    out = tmp_path / "out"
    records, candidates, blocked = A.run_audit(
        traits,
        residue,
        interpro,
        profiles,
        out,
        max_candidates_per_record=1,
        protein_registry_path=tmp_path / "missing-proteins.jsonl",
        evidence_registry_path=tmp_path / "missing-evidence.jsonl",
    )

    by_id = {row.trait_id: row for row in records}
    assert len(records) == 9
    assert by_id["Pfam:PF00001"].grounding_state == "NO_PROTEIN"
    assert by_id["Pfam:PF00001"].inline_state == "NO_VALID_PROTEIN"
    assert by_id["Pfam:PF00001"].candidate_state == "AMBIGUOUS_LOCAL_EXACT_CANDIDATES"
    assert by_id["Pfam:PF00001"].available_candidate_count == 1
    assert by_id["Pfam:PF00002"].inline_state == "PROTEIN_ORGANISM_INCOMPLETE"
    assert by_id["fixture:NO_SEQUENCE"].inline_state == "PROTEIN_ORGANISM_NO_SEQUENCE"
    assert by_id["fixture:NO_COORDINATE"].inline_state == "SEQUENCE_NO_CATEGORY_COORDINATE"
    assert by_id["fixture:SHAPE_ONLY"].inline_state == "STRICT_INLINE_SHAPE"
    assert by_id["fixture:SHAPE_ONLY"].grounding_state == "LEGACY_UNVERIFIED"
    assert by_id["fixture:QUALIFIED"].grounding_state == "DECLARED_QUALIFIED_UNVERIFIED"

    candidate_by_trait = {row["trait_id"]: row for row in candidates}
    pfam = candidate_by_trait["Pfam:PF00001"]
    assert pfam["protein_id"] == "UniProtKB:P12345"
    assert pfam["intervals"] == [{"start": 2, "end": 4}]
    assert pfam["residue_positions"] == []
    assert pfam["coordinate_frame"] == "UNIPROT_CANONICAL"
    assert pfam["sequence_release"] == "2026_02"
    assert pfam["source_release"] == "109.0"
    assert pfam["mapping_method"] == "INTERPRO_MATCH"
    assert pfam["candidate_status"] == "LOCATION_VERIFIED"
    assert pfam["qualification_status"] == "CANDIDATE_PROTEIN"
    assert pfam["reasons"] == []
    assert pfam["sequence_sha256"] == hashlib.sha256(b"ACDEFG").hexdigest()
    assert pfam["candidate_id"].startswith("ug-") and len(pfam["candidate_id"]) == 67
    assert "sequence" not in pfam
    identity = {
        key: pfam.get(key)
        for key in (
            "trait_id",
            "protein_id",
            "source_trait_id",
            "mapping_method",
            "evidence_source",
            "source_release",
            "sequence_release",
            "sequence_sha256",
            "scope",
            "coordinate_frame",
            "intervals",
            "residue_positions",
        )
    }
    canonical = json.dumps(identity, sort_keys=True, separators=(",", ":"))
    assert pfam["candidate_id"] == "ug-" + hashlib.sha256(canonical.encode()).hexdigest()

    whole = candidate_by_trait["PANTHER:PTHR00001"]
    assert whole["scope"] == "WHOLE_PROTEIN"
    assert whole["candidate_status"] == "WHOLE_PROTEIN_EVIDENCE_VERIFIED"
    assert "coordinate_frame" not in whole
    # This is a real HMM footprint, not a fabricated 1..L occurrence.  Promotion
    # decides how to retain supporting match intervals for whole-protein scope.
    assert whole["intervals"] == [{"start": 1, "end": 6}]

    reasons = {(row.trait_id, row.protein_id, row.reason) for row in blocked}
    assert ("Pfam:PF_NO_MATCH", "UniProtKB:UNS0001", "INVALID_UNIPROT_IDENTIFIER") in reasons
    assert (
        "fixture:NO_SEQUENCE",
        "UniProtKB:P22222",
        "ACCESSION_ABSENT_FROM_RESIDUE_FRAME",
    ) in reasons
    assert ("CDD:cd00001", "UniProtKB:P99999", "INTERPRO_INTERVAL_OUT_OF_BOUNDS") in reasons
    assert (
        "Pfam:PF00001",
        "UniProtKB:Q54321",
        "UNGROUPED_INTERPRO_LOCATIONS",
    ) in reasons
    assert "CDD:cd00001" not in candidate_by_trait

    assert {p.name for p in out.iterdir()} == {
        "summary.tsv",
        "records.tsv",
        "candidates.jsonl",
        "blocked.tsv",
    }
    assert len(_read_tsv(out / "records.tsv")) == 9
    totals = [row for row in _read_tsv(out / "summary.tsv") if row["group_by"] == "ALL"]
    assert sum(int(row["count"]) for row in totals) == 9


def test_outputs_are_byte_identical_on_rerun(tmp_path):
    traits, residue, interpro, profiles = _inputs(tmp_path)
    out = tmp_path / "out"
    missing_proteins = tmp_path / "missing-proteins.jsonl"
    missing_evidence = tmp_path / "missing-evidence.jsonl"
    A.run_audit(
        traits,
        residue,
        interpro,
        profiles,
        out,
        protein_registry_path=missing_proteins,
        evidence_registry_path=missing_evidence,
    )
    first = {path.name: path.read_bytes() for path in out.iterdir()}
    A.run_audit(
        traits,
        residue,
        interpro,
        profiles,
        out,
        protein_registry_path=missing_proteins,
        evidence_registry_path=missing_evidence,
    )
    second = {path.name: path.read_bytes() for path in out.iterdir()}
    assert second == first


def test_qualification_requires_both_statuses_and_an_exact_occurrence():
    base = {
        "protein_id": "UniProtKB:P12345",
        "protein_label": "Protein",
        "qualification_status": "QUALIFIED",
    }
    no_occurrence = A.classify_examples([base], "Pfam:PF1", "SEQ_DOMAIN")
    assert no_occurrence[0] == "LEGACY_UNVERIFIED"

    wrong = dict(base)
    wrong["trait_occurrences"] = [
        {
            "trait_id": "Pfam:OTHER",
            "protein_id": "UniProtKB:P12345",
            "qualification_status": "QUALIFIED",
        }
    ]
    assert A.classify_examples([wrong], "Pfam:PF1", "SEQ_DOMAIN")[0] == "LEGACY_UNVERIFIED"

    exact = dict(base)
    exact["trait_occurrences"] = [
        {
            "trait_id": "Pfam:PF1",
            "protein_id": "UniProtKB:P12345",
            "qualification_status": "QUALIFIED",
        }
    ]
    assert (
        A.classify_examples([exact], "Pfam:PF1", "SEQ_DOMAIN")[0] == "DECLARED_QUALIFIED_UNVERIFIED"
    )


def test_declared_qualification_becomes_qualified_only_after_semantic_validation(
    tmp_path,
):
    traits, proteins, evidence, _, _ = _authoritative_fixture(tmp_path)
    records, blocked = A.scan_records(
        traits,
        protein_registry_path=proteins,
        evidence_registry_path=evidence,
        membership_registry_path=tmp_path / "missing-memberships.jsonl",
    )

    assert len(records) == 1
    assert records[0].grounding_state == "QUALIFIED"
    assert records[0].qualified_example_count == 1
    assert blocked == []


def test_qualified_uniprot_membership_replays_exact_registry_fact(tmp_path):
    traits, proteins, evidence, memberships, _, _ = _membership_fixture(tmp_path)

    records, blocked = A.scan_records(
        traits,
        protein_registry_path=proteins,
        evidence_registry_path=evidence,
        membership_registry_path=memberships,
    )

    assert records[0].grounding_state == "QUALIFIED"
    assert records[0].qualified_example_count == 1
    assert blocked == []


def test_qualified_uniprot_membership_requires_membership_registry(tmp_path):
    traits, proteins, evidence, _, _, _ = _membership_fixture(tmp_path)

    records, blocked = A.scan_records(
        traits,
        protein_registry_path=proteins,
        evidence_registry_path=evidence,
        membership_registry_path=tmp_path / "missing-memberships.jsonl",
    )

    assert records[0].grounding_state == "DECLARED_QUALIFIED_UNVERIFIED"
    assert records[0].qualified_example_count == 0
    assert {item.reason for item in blocked} == {"SEMANTIC_MEMBERSHIP_REGISTRY_NOT_FOUND"}


def test_tampered_uniprot_membership_registry_fails_closed(tmp_path):
    traits, proteins, evidence, memberships, membership, _ = _membership_fixture(tmp_path)
    tampered = json.loads(json.dumps(membership))
    tampered["database_cross_reference"]["properties"][0]["value"] = "forged"
    _jsonl(memberships, [tampered])

    records, blocked = A.scan_records(
        traits,
        protein_registry_path=proteins,
        evidence_registry_path=evidence,
        membership_registry_path=memberships,
    )

    assert records[0].grounding_state == "DECLARED_QUALIFIED_UNVERIFIED"
    assert records[0].qualified_example_count == 0
    assert {item.reason for item in blocked} == {"SEMANTIC_MEMBERSHIP_REGISTRY_INVALID"}


def test_malformed_qualification_marker_is_semantically_blocked(tmp_path):
    traits = tmp_path / "traits"
    _record(
        traits,
        "malformed-declaration.yaml",
        "identifier: Pfam:PF00001\n"
        "trait_axis: SEQUENCE\n"
        "trait_category: SEQ_DOMAIN\n"
        "canonical_examples:\n"
        "- protein_id: UniProtKB:P12345\n"
        "  protein_label: Protein\n"
        "  qualification_status: QUALIFIED\n",
    )
    records, blocked = A.scan_records(
        traits,
        protein_registry_path=tmp_path / "missing-proteins.jsonl",
        evidence_registry_path=tmp_path / "missing-evidence.jsonl",
    )
    assert records[0].grounding_state == "DECLARED_QUALIFIED_UNVERIFIED"
    assert records[0].qualified_example_count == 0
    assert "SEMANTIC_QUALIFIED_WITHOUT_QUALIFIED_OCCURRENCE" in {item.reason for item in blocked}


def test_forged_evidence_digest_keeps_declaration_unverified(tmp_path):
    traits, proteins, evidence_path, _, evidence = _authoritative_fixture(tmp_path)
    evidence["provider_source"] = "made/up/provider.tsv"
    _jsonl(evidence_path, [evidence])

    records, blocked = A.scan_records(
        traits,
        protein_registry_path=proteins,
        evidence_registry_path=evidence_path,
    )

    assert records[0].grounding_state == "DECLARED_QUALIFIED_UNVERIFIED"
    assert records[0].qualified_example_count == 0
    reasons = {item.reason for item in blocked}
    assert "SEMANTIC_EVIDENCE_ID_DIGEST_MISMATCH" in reasons
    assert "SEMANTIC_UNKNOWN_SOURCE_EVIDENCE" in reasons


def test_inherited_qualification_requires_authoritative_hierarchy_edge(tmp_path):
    parent = "PROSITE:PS_PARENT"
    child = "PROSITE:PS_CHILD"
    traits, proteins, evidence, _, _ = _authoritative_fixture(
        tmp_path,
        trait_id=parent,
        source_trait_id=child,
    )
    child_path = traits / "sequence" / "domain" / "fixture" / "child.yaml"
    child_path.write_text(
        yaml.safe_dump(
            {
                "identifier": child,
                "label": "child motif",
                "trait_axis": "SEQUENCE",
                "trait_category": "SEQ_MOTIF",
                "parent_traits": [parent],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    records, blocked = A.scan_records(
        traits,
        protein_registry_path=proteins,
        evidence_registry_path=evidence,
    )
    parent_record = next(item for item in records if item.trait_id == parent)
    assert parent_record.grounding_state == "QUALIFIED"
    assert blocked == []

    child_path.write_text(
        yaml.safe_dump(
            {
                "identifier": child,
                "label": "child motif",
                "trait_axis": "SEQUENCE",
                "trait_category": "SEQ_MOTIF",
                "parent_traits": [],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    records, blocked = A.scan_records(
        traits,
        protein_registry_path=proteins,
        evidence_registry_path=evidence,
    )
    parent_record = next(item for item in records if item.trait_id == parent)
    assert parent_record.grounding_state == "DECLARED_QUALIFIED_UNVERIFIED"
    assert "SEMANTIC_UNPROVEN_TRAIT_INHERITANCE_EDGE" in {item.reason for item in blocked}


def test_all_legacy_scan_does_not_require_migration_registries(tmp_path):
    traits = tmp_path / "traits"
    _record(
        traits,
        "legacy.yaml",
        "identifier: fixture:LEGACY\n"
        "trait_axis: SEQUENCE\n"
        "trait_category: SEQ_DOMAIN\n"
        "canonical_examples:\n"
        "- protein_id: UniProtKB:P12345\n"
        "  protein_label: Legacy protein\n",
    )
    records, blocked = A.scan_records(
        traits,
        protein_registry_path=tmp_path / "missing-proteins.jsonl",
        evidence_registry_path=tmp_path / "missing-evidence.jsonl",
        membership_registry_path=tmp_path / "missing-memberships.jsonl",
    )
    assert records[0].grounding_state == "LEGACY_UNVERIFIED"
    assert not any(item.reason.startswith("SEMANTIC_") for item in blocked)


def test_inline_funnel_never_combines_fields_from_different_examples():
    examples = [
        {"protein_id": "UniProtKB:P12345", "protein_label": "first"},
        {
            "protein_id": "not-an-accession",
            "protein_label": "second",
            "taxon_id": "NCBITaxon:9606",
            "taxon_label": "Homo sapiens",
            "sequence": "ACDEFG",
            "features": [{"start": 1, "end": 6, "trait_category": "SEQ_DOMAIN"}],
        },
    ]
    result = A.classify_examples(examples, "Pfam:PF1", "SEQ_DOMAIN")
    assert result[1] == "PROTEIN_ORGANISM_INCOMPLETE"


def test_scope_policy_matches_the_semantic_validator():
    def record(axis: str, category: str) -> A.RecordAudit:
        return A.RecordAudit(
            trait_id="fixture:T",
            path=Path("x.yaml"),
            record_path="x.yaml",
            trait_axis=axis,
            trait_category=category,
            source_namespace="fixture",
            grounding_state="NO_PROTEIN",
            inline_state="NO_VALID_PROTEIN",
        )

    assert A._scope(record("FUNCTION", "FUNC_PROTEIN_FAMILY")) == "WHOLE_PROTEIN"
    assert A._scope(record("EVOLUTION", "EVOL_CONSERVATION")) == "WHOLE_PROTEIN"
    assert A._scope(record("SEQUENCE", "SEQ_FAMILY")) == "WHOLE_PROTEIN"
    assert A._scope(record("SEQUENCE", "SEQ_HOMOLOGOUS_SUPERFAMILY")) == "WHOLE_PROTEIN"
    assert A._scope(record("SEQUENCE", "SEQ_DOMAIN")) == "LOCALIZED"
