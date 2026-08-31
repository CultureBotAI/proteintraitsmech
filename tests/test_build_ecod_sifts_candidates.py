"""Offline fixtures for the fail-closed ECOD -> SIFTS adapter."""

from __future__ import annotations

import copy
import gzip
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "build_ecod_sifts_candidates.py"
sys.path.insert(0, str(REPO / "scripts"))
SPEC = importlib.util.spec_from_file_location("build_ecod_sifts_candidates", SCRIPT)
assert SPEC and SPEC.loader
E = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = E
SPEC.loader.exec_module(E)

import validate_uniprot_grounding as V  # noqa: E402


def _jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "".join(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n" for row in rows),
        encoding="utf-8",
    )


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def _xml_residue(
    pdbe_position: int,
    native: str | None,
    pdb_name: str,
    *,
    uniprot_position: int | None,
    uniprot_name: str | None,
) -> str:
    uniprot = ""
    if uniprot_position is not None and uniprot_name is not None:
        uniprot = (
            '<crossRefDb dbSource="UniProt" dbCoordSys="UniProt" '
            f'dbAccessionId="P12345" dbResNum="{uniprot_position}" '
            f'dbResName="{uniprot_name}"/>'
        )
    return (
        f'<residue dbSource="PDBe" dbCoordSys="PDBe" dbResNum="{pdbe_position}" '
        f'dbResName="{pdb_name}">'
        '<crossRefDb dbSource="PDB" dbCoordSys="PDBresnum" '
        f'dbAccessionId="1abc" dbResNum="{native or "null"}" dbResName="{pdb_name}" '
        'dbChainId="A"/>'
        f"{uniprot}</residue>"
    )


def _fixture(
    root: Path,
    *,
    second_mapped: bool = True,
    second_pdb_name: str = "CYS",
    second_observed: bool = True,
) -> dict[str, Path | dict]:
    ecod = root / "ecod.txt"
    ecod.write_text(
        "# ECOD Domain List\n"
        "# Version: vTEST\n"
        "uid\tecod_domain_id\tmanual_rep\tf_id\tpdb\tchain\tpdb_range\tseqid_range\n"
        "1\te1abcA1\tTrue\t1.2.3.4\t1abc\tA\tA:10A-10B\tA:1-2\n",
        encoding="utf-8",
    )
    traits = root / "traits"
    traits.mkdir()
    trait = {
        "identifier": "ECOD:F.1.2.3.4",
        "label": "fixture fold",
        "definition": "fixture",
        "trait_axis": "STRUCTURE",
        "trait_category": "STRUCT_FOLD",
        "term_kind": "CLASS",
        "mapping_status": "SEEDED",
    }
    (traits / "fixture.yaml").write_text(yaml.safe_dump(trait, sort_keys=False), encoding="utf-8")
    sequence = "MACD"
    checksum = hashlib.sha256(sequence.encode("ascii")).hexdigest()
    reference = {
        "protein_id": "UniProtKB:P12345",
        "protein_label": "Fixture protein",
        "taxon_id": "NCBITaxon:9606",
        "taxon_label": "Homo sapiens",
        "sequence": sequence,
        "sequence_length": len(sequence),
        "sequence_sha256": checksum,
        "reviewed": True,
        "uniprot_release": "2026_03",
    }
    proteins = root / "protein_registry.jsonl"
    _jsonl(proteins, [reference])
    sifts = root / "sifts"
    sifts.mkdir()
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<entry xmlns="http://www.ebi.ac.uk/pdbe/docs/sifts/eFamily.xsd" '
        'xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" '
        'xmlns:dc="http://purl.org/dc/elements/1.1/" '
        'dbSource="PDBe" dbVersion="2.0" dbCoordSys="PDBe" '
        'dbAccessionId="1abc" date="2026-08-17">'
        '<rdf:RDF><rdf:Description rdf:about="self">'
        '<dc:rights rdf:resource="http://pdbe.org/sifts">fixture SIFTS rights</dc:rights>'
        "</rdf:Description></rdf:RDF>"
        '<listDB><db dbSource="PDB" dbVersion="33.26"/>'
        '<db dbSource="UniProt" dbVersion="2026.03"/></listDB>'
        '<entity type="protein" entityId="A"><segment segId="fixture">'
        "<listResidue>"
        + _xml_residue(1, "10A", "ALA", uniprot_position=2, uniprot_name="A")
        + _xml_residue(
            2,
            "10B" if second_observed else None,
            second_pdb_name,
            uniprot_position=3 if second_mapped else None,
            uniprot_name="C" if second_mapped else None,
        )
        + "</listResidue></segment></entity></entry>"
    )
    (sifts / "1abc.xml").write_text(xml, encoding="utf-8")
    return {
        "ecod": ecod,
        "traits": traits,
        "proteins": proteins,
        "sifts": sifts,
        "reference": reference,
        "trait": trait,
    }


def _build_argv(
    fixture: dict[str, Path | dict],
    outputs: dict[str, Path],
    *,
    offline_fixture_mode: bool = True,
) -> list[str]:
    argv = [
        "build",
        "--ecod",
        str(fixture["ecod"]),
        "--traits",
        str(fixture["traits"]),
        "--sifts-dir",
        str(fixture["sifts"]),
        "--protein-registry",
        str(fixture["proteins"]),
        "--candidates",
        str(outputs["candidates"]),
        "--mappings",
        str(outputs["mappings"]),
        "--evidence",
        str(outputs["evidence"]),
        "--blocked",
        str(outputs["blocked"]),
    ]
    if offline_fixture_mode:
        argv.append("--offline-fixture-mode")
    return argv


def _run(
    root: Path,
    fixture: dict[str, Path | dict],
    *,
    offline_fixture_mode: bool = True,
) -> dict[str, Path]:
    outputs = {
        "candidates": root / "candidates.jsonl",
        "mappings": root / "mappings.jsonl",
        "evidence": root / "evidence.jsonl",
        "blocked": root / "blocked.jsonl",
    }
    argv = _build_argv(fixture, outputs, offline_fixture_mode=offline_fixture_mode)
    result = E.main(argv)
    assert result == 0
    return outputs


def _production_snapshot(
    root: Path, fixture: dict[str, Path | dict], *, snapshot_id: str = "sifts-test-1"
) -> Path:
    source_dir = fixture["sifts"]
    ecod_path = fixture["ecod"]
    assert isinstance(source_dir, Path)
    assert isinstance(ecod_path, Path)
    plain_xml = source_dir / "1abc.xml"
    snapshot = root / snapshot_id
    snapshot.mkdir()
    compressed = snapshot / "1abc.xml.gz"
    compressed.write_bytes(gzip.compress(plain_xml.read_bytes(), mtime=0))
    entry = E.load_sifts_xml(compressed)
    manifest_entry = E._manifest_entry(entry, path=compressed)
    contract = E._snapshot_contract(
        snapshot_id=snapshot_id,
        ecod_path=ecod_path,
        release=E.ecod_release(ecod_path),
        representatives_only=True,
        pdb_ids=["1abc"],
    )
    manifest = E._manifest_value(contract, {"1abc": manifest_entry}, {})
    E._atomic_write(snapshot / E.MANIFEST_NAME, E.canonical_json(manifest) + "\n")
    fixture["sifts"] = snapshot
    return snapshot


def test_native_ranges_preserve_insertion_codes_and_discontinuity():
    ranges = E.parse_native_ranges("A:1B-99A,A:105-107")
    assert [item.as_dict() for item in ranges] == [
        {
            "chain_id": "A",
            "start": {"author_residue_number": 1, "author_insertion_code": "B"},
            "end": {"author_residue_number": 99, "author_insertion_code": "A"},
        },
        {
            "chain_id": "A",
            "start": {"author_residue_number": 105, "author_insertion_code": ""},
            "end": {"author_residue_number": 107, "author_insertion_code": ""},
        },
    ]


def test_exact_residue_mapping_emits_replayable_candidate_and_evidence(tmp_path):
    fixture = _fixture(tmp_path)
    outputs = _run(tmp_path, fixture)

    candidates = _read_jsonl(outputs["candidates"])
    mappings = _read_jsonl(outputs["mappings"])
    evidence_rows = _read_jsonl(outputs["evidence"])
    assert _read_jsonl(outputs["blocked"]) == []
    assert len(candidates) == len(mappings) == len(evidence_rows) == 1
    candidate = candidates[0]
    mapping = mappings[0]
    evidence = evidence_rows[0]
    assert candidate["candidate_status"] == "LOCATION_VERIFIED"
    assert candidate["qualification_status"] == "CANDIDATE_PROTEIN"
    assert candidate["trait_occurrence"]["qualification_status"] == "LOCATION_VERIFIED"
    assert candidate["mapping_method"] == "SIFTS_RESIDUE_MAPPING"
    assert candidate["residue_positions"] == [2, 3]
    assert candidate["expected_residues"] == "AC"
    assert candidate["source_residue_count"] == candidate["mapped_residue_count"] == 2
    assert candidate["ecod_pdb_range"] == "A:10A-10B"
    assert [
        (row["author_residue_number"], row["author_insertion_code"])
        for row in mapping["mapped_residues"]
    ] == [(10, "A"), (10, "B")]
    assert mapping["ecod_license"] == E.ECOD_LICENSE
    assert mapping["ecod_line_number"] == 4
    assert mapping["ecod_source_sha256"] == E.file_sha256(fixture["ecod"])
    assert mapping["sifts_snapshot_mode"] == E.OFFLINE_FIXTURE
    assert mapping["sifts_manifest_entry"]["pdb_id"] == "1abc"
    assert mapping["sifts_manifest_entry_sha256"] == E.value_sha256(mapping["sifts_manifest_entry"])
    assert mapping["sifts_rights"] == "fixture SIFTS rights"
    assert candidate["grounding_evidence"] == evidence
    assert {
        finding.code
        for finding in V.validate_grounding_evidence(evidence, path=outputs["evidence"], line=1)
    } == {"ecod_provider_receipt_required"}
    assert E.load_mapping_registry(outputs["mappings"], allow_offline_fixtures=True) == {
        mapping["mapping_id"]: mapping
    }
    with pytest.raises(E.EcodSiftsError, match="OFFLINE_FIXTURE mapping rejected"):
        E.load_mapping_registry(outputs["mappings"])

    occurrence = dict(candidate["trait_occurrence"])
    occurrence["qualification_status"] = "QUALIFIED"
    record = dict(fixture["trait"])
    reference = fixture["reference"]
    assert isinstance(reference, dict)
    record["canonical_examples"] = [
        {
            "protein_id": reference["protein_id"],
            "protein_label": reference["protein_label"],
            "taxon_id": reference["taxon_id"],
            "taxon_label": reference["taxon_label"],
            "sequence_length": reference["sequence_length"],
            "sequence_sha256": reference["sequence_sha256"],
            "uniprot_release": reference["uniprot_release"],
            "qualification_status": "QUALIFIED",
            "source": "UNIPROT_GROUNDING",
            "trait_occurrences": [occurrence],
        }
    ]
    assert {
        finding.code
        for finding in V.validate_record(
            record,
            {reference["protein_id"]: reference},
            evidence_registry={evidence["evidence_id"]: evidence},
        )
    } == {"ecod_provider_receipt_required"}


def test_candidate_builder_rejects_receipt_lock_plus_any_other_finding(tmp_path, monkeypatch):
    fixture = _fixture(tmp_path)
    original_validate = V.validate_grounding_evidence

    def validate_with_extra_finding(evidence, *, path, line):
        return [
            *original_validate(evidence, path=path, line=line),
            V.Finding(
                file=f"{path}:{line}",
                trait_id=str(evidence.get("trait_id", "")),
                protein_id=str(evidence.get("protein_id", "")),
                example_index="",
                occurrence_index="",
                code="fixture_additional_error",
                message="injected independent semantic failure",
            ),
        ]

    monkeypatch.setattr(V, "validate_grounding_evidence", validate_with_extra_finding)
    outputs = _run(tmp_path, fixture)

    assert _read_jsonl(outputs["candidates"]) == []
    assert _read_jsonl(outputs["mappings"]) == []
    assert _read_jsonl(outputs["evidence"]) == []
    blocked = _read_jsonl(outputs["blocked"])
    assert len(blocked) == 1
    assert blocked[0]["reason"] == "GROUNDING_EVIDENCE_INVALID"
    assert blocked[0]["detail"].endswith("ecod_provider_receipt_required,fixture_additional_error")


def test_compact_mapping_registry_is_content_addressed(tmp_path):
    fixture = _fixture(tmp_path)
    outputs = _run(tmp_path, fixture)
    mapping = _read_jsonl(outputs["mappings"])[0]
    mapping["mapped_residues"][0]["uniprot_position"] = 4
    _jsonl(outputs["mappings"], [mapping])

    try:
        E.load_mapping_registry(outputs["mappings"])
    except E.EcodSiftsError as exc:
        assert "mapping_id digest mismatch" in str(exc)
    else:
        raise AssertionError("tampered mapping registry was accepted")


def test_outputs_are_byte_idempotent(tmp_path):
    fixture = _fixture(tmp_path)
    outputs = _run(tmp_path, fixture)
    first = {name: path.read_bytes() for name, path in outputs.items()}
    _run(tmp_path, fixture)
    assert {name: path.read_bytes() for name, path in outputs.items()} == first


def test_unobserved_but_sequence_mapped_residue_is_included(tmp_path):
    fixture = _fixture(tmp_path, second_observed=False)
    outputs = _run(tmp_path, fixture)

    candidate = _read_jsonl(outputs["candidates"])[0]
    mapping = _read_jsonl(outputs["mappings"])[0]
    assert candidate["source_residue_count"] == 2
    assert mapping["mapped_residues"][1]["pdbe_sequence_position"] == 2
    assert mapping["mapped_residues"][1]["author_residue_number"] is None
    assert mapping["mapped_residues"][1]["author_insertion_code"] is None


def test_unmapped_defining_residue_is_blocked(tmp_path):
    fixture = _fixture(tmp_path, second_mapped=False)
    outputs = _run(tmp_path, fixture)
    assert _read_jsonl(outputs["candidates"]) == []
    assert _read_jsonl(outputs["evidence"]) == []
    assert _read_jsonl(outputs["blocked"])[0]["reason"] == ("INCOMPLETE_SIFTS_RESIDUE_MAPPING")


def test_pdb_uniprot_amino_acid_mismatch_is_blocked(tmp_path):
    fixture = _fixture(tmp_path, second_pdb_name="GLY")
    outputs = _run(tmp_path, fixture)
    assert _read_jsonl(outputs["candidates"]) == []
    blocked = _read_jsonl(outputs["blocked"])[0]
    assert blocked["reason"] == "PDB_UNIPROT_RESIDUE_MISMATCH"
    assert "10B:G!=C" in blocked["detail"]


def test_fetch_is_dry_run_by_default(tmp_path, capsys):
    fixture = _fixture(tmp_path)
    snapshot_root = tmp_path / "snapshot"
    result = E.main(
        [
            "fetch",
            "--ecod",
            str(fixture["ecod"]),
            "--snapshot-dir",
            str(snapshot_root),
            "--snapshot-id",
            "fixture-2026-08-24",
        ]
    )
    assert result == 0
    assert not snapshot_root.exists()
    output = capsys.readouterr().out
    assert "dry-run; no files written" in output
    assert "https://ftp.ebi.ac.uk/pub/databases/msd/sifts/xml/1abc.xml.gz" in output


def test_production_snapshot_and_mapping_replay_are_manifest_pinned(tmp_path):
    fixture = _fixture(tmp_path)
    snapshot = _production_snapshot(tmp_path, fixture)
    outputs = _run(tmp_path, fixture, offline_fixture_mode=False)

    mapping = _read_jsonl(outputs["mappings"])[0]
    manifest_raw = (snapshot / E.MANIFEST_NAME).read_bytes()
    assert mapping["sifts_snapshot_mode"] == E.PINNED_MANIFEST
    assert mapping["sifts_manifest_sha256"] == hashlib.sha256(manifest_raw).hexdigest()
    assert E.load_mapping_registry(outputs["mappings"]) == {mapping["mapping_id"]: mapping}


def test_recomputed_mapping_digest_cannot_hide_scientific_inconsistency(tmp_path):
    fixture = _fixture(tmp_path)
    outputs = _run(tmp_path, fixture)
    mapping = _read_jsonl(outputs["mappings"])[0]
    mapping["mapped_residues"] = mapping["mapped_residues"][:-1]
    mapping["mapping_id"] = f"ecod-sifts:{E.mapping_entry_sha256(mapping)}"
    _jsonl(outputs["mappings"], [mapping])

    with pytest.raises(E.EcodSiftsError, match="every ECOD defining residue"):
        E.load_mapping_registry(outputs["mappings"], allow_offline_fixtures=True)


def test_recomputed_mapping_digest_cannot_remap_a_bound_sifts_residue(tmp_path):
    fixture = _fixture(tmp_path)
    outputs = _run(tmp_path, fixture)
    mapping = _read_jsonl(outputs["mappings"])[0]
    mapping["mapped_residues"][0]["uniprot_position"] = 4
    mapping["mapping_id"] = f"ecod-sifts:{E.mapping_entry_sha256(mapping)}"
    _jsonl(outputs["mappings"], [mapping])

    with pytest.raises(E.EcodSiftsError, match="does not match SIFTS XML"):
        E.load_mapping_registry(outputs["mappings"], allow_offline_fixtures=True)


def test_recomputed_mapping_digest_cannot_replace_pinned_manifest_entry(tmp_path):
    fixture = _fixture(tmp_path)
    _production_snapshot(tmp_path, fixture)
    outputs = _run(tmp_path, fixture, offline_fixture_mode=False)
    mapping = _read_jsonl(outputs["mappings"])[0]
    replacement_sha = "0" * 64
    mapping["sifts_manifest_entry"]["sha256"] = replacement_sha
    mapping["sifts_manifest_entry_sha256"] = E.value_sha256(mapping["sifts_manifest_entry"])
    mapping["sifts_xml_sha256"] = replacement_sha
    mapping["mapping_id"] = f"ecod-sifts:{E.mapping_entry_sha256(mapping)}"
    _jsonl(outputs["mappings"], [mapping])

    with pytest.raises(E.EcodSiftsError, match="does not contain the bound entry"):
        E.load_mapping_registry(outputs["mappings"])


def test_mapping_registry_replays_bound_ecod_file_and_line(tmp_path):
    fixture = _fixture(tmp_path)
    outputs = _run(tmp_path, fixture)
    ecod_path = fixture["ecod"]
    assert isinstance(ecod_path, Path)
    ecod_path.write_text(
        ecod_path.read_text(encoding="utf-8").replace("A:10A-10B", "A:10A-10C"),
        encoding="utf-8",
    )

    with pytest.raises(E.EcodSiftsError, match="ECOD source file digest mismatch"):
        E.load_mapping_registry(outputs["mappings"], allow_offline_fixtures=True)


@pytest.mark.parametrize(
    ("field", "replacement"),
    [
        ("structure_id", "PDB:2xyz"),
        ("chain_id", "B"),
        ("ecod_domain_id", "e1abcA2"),
        ("sifts_mapping_id", "ecod-sifts:" + "f" * 64),
    ],
)
def test_candidate_identity_includes_structure_domain_chain_and_mapping(
    tmp_path, field, replacement
):
    fixture = _fixture(tmp_path)
    outputs = _run(tmp_path, fixture)
    candidate = _read_jsonl(outputs["candidates"])[0]
    changed = copy.deepcopy(candidate)
    changed[field] = replacement
    assert E._candidate_id(changed) != candidate["candidate_id"]


@pytest.mark.parametrize(
    ("old", "new", "message"),
    [
        ('date="2026-08-17"', 'date="17-08-2026"', "ISO YYYY-MM-DD"),
        (
            'rdf:resource="http://pdbe.org/sifts"',
            'rdf:resource="https://example.test/wrong"',
            "rights URL mismatch",
        ),
        ('dbSource="PDBe"', 'dbSource="NotPDBe"', "root source"),
    ],
)
def test_sifts_xml_requires_exact_date_rights_and_source(tmp_path, old, new, message):
    fixture = _fixture(tmp_path)
    sifts_dir = fixture["sifts"]
    assert isinstance(sifts_dir, Path)
    path = sifts_dir / "1abc.xml"
    with pytest.raises(E.EcodSiftsError, match="production SIFTS input"):
        E.load_sifts_xml(path)
    mutated = tmp_path / "mutated.xml"
    mutated.write_text(path.read_text(encoding="utf-8").replace(old, new, 1), encoding="utf-8")
    with pytest.raises(E.EcodSiftsError, match=message):
        E.load_sifts_xml(mutated, allow_plain_xml=True)


def test_fetch_manifest_is_resumable_then_immutable(tmp_path, monkeypatch, capsys):
    fixture = _fixture(tmp_path)
    sifts_dir = fixture["sifts"]
    assert isinstance(sifts_dir, Path)
    payload = gzip.compress((sifts_dir / "1abc.xml").read_bytes(), mtime=0)
    snapshot_root = tmp_path / "snapshots"
    argv = [
        "fetch",
        "--ecod",
        str(fixture["ecod"]),
        "--snapshot-dir",
        str(snapshot_root),
        "--snapshot-id",
        "release-2026-08-24",
        "--apply",
    ]

    def unavailable(*_args, **_kwargs):
        raise E.urllib.error.URLError("offline")

    monkeypatch.setattr(E.urllib.request, "urlopen", unavailable)
    assert E.main(argv) == 1
    manifest_path = snapshot_root / "release-2026-08-24" / E.MANIFEST_NAME
    incomplete = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert incomplete["complete"] is False
    assert incomplete["failures"][0]["pdb_id"] == "1abc"

    immutable_contract = manifest_path.read_bytes()
    assert E.main([*argv, "--all-occurrences"]) == 2
    assert manifest_path.read_bytes() == immutable_contract

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def read(self):
            return payload

    monkeypatch.setattr(E.urllib.request, "urlopen", lambda *_args, **_kwargs: Response())
    assert E.main(argv) == 0
    completed_bytes = manifest_path.read_bytes()
    completed = json.loads(completed_bytes)
    assert completed["complete"] is True
    assert completed["failures"] == []
    assert completed["snapshot_mode"] == E.PINNED_MANIFEST

    def unexpected_network(*_args, **_kwargs):
        raise AssertionError("completed snapshot attempted a network request")

    monkeypatch.setattr(E.urllib.request, "urlopen", unexpected_network)
    assert E.main(argv) == 0
    assert manifest_path.read_bytes() == completed_bytes
    capsys.readouterr()


@pytest.mark.parametrize("snapshot_id", ["../escape", "bad/name", ".", "bad-"])
def test_snapshot_id_must_be_one_safe_component(tmp_path, snapshot_id):
    fixture = _fixture(tmp_path)
    snapshot_root = tmp_path / "snapshot"
    result = E.main(
        [
            "fetch",
            "--ecod",
            str(fixture["ecod"]),
            "--snapshot-dir",
            str(snapshot_root),
            "--snapshot-id",
            snapshot_id,
        ]
    )
    assert result == 2
    assert not snapshot_root.exists()


def test_build_rejects_aliased_outputs_before_writing(tmp_path):
    fixture = _fixture(tmp_path)
    shared = tmp_path / "shared.jsonl"
    outputs = {
        "candidates": shared,
        "mappings": shared,
        "evidence": tmp_path / "evidence.jsonl",
        "blocked": tmp_path / "blocked.jsonl",
    }
    assert E.main(_build_argv(fixture, outputs)) == 2
    assert not any(path.exists() for path in set(outputs.values()))


@pytest.mark.parametrize("output_name", ["candidates", "mappings", "evidence", "blocked"])
@pytest.mark.parametrize(
    "protected_root_name",
    ["canonical-traits", "canonical-grounding", "selected-traits"],
)
@pytest.mark.parametrize("through_symlink", [False, True], ids=["direct", "symlink-alias"])
def test_build_rejects_every_output_under_protected_roots_before_any_write(
    tmp_path,
    monkeypatch,
    output_name,
    protected_root_name,
    through_symlink,
):
    fixture = _fixture(tmp_path)
    selected_traits = fixture["traits"]
    assert isinstance(selected_traits, Path)
    protected_roots = {
        "canonical-traits": E.TRAITS_ROOT,
        "canonical-grounding": E.GROUNDING_ROOT,
        "selected-traits": selected_traits,
    }
    protected_root = protected_roots[protected_root_name]
    probe_name = f"_ecod_sifts_no_write_probe_{output_name}.jsonl"
    canonical_probe = protected_root / probe_name
    assert not canonical_probe.exists()

    output_parent = protected_root
    if through_symlink:
        output_parent = tmp_path / f"{protected_root_name}-alias"
        output_parent.symlink_to(protected_root, target_is_directory=True)

    outputs = {
        "candidates": tmp_path / "candidates.jsonl",
        "mappings": tmp_path / "mappings.jsonl",
        "evidence": tmp_path / "evidence.jsonl",
        "blocked": tmp_path / "blocked.jsonl",
    }
    outputs[output_name] = output_parent / probe_name
    attempted_writes: list[Path] = []

    def reject_any_write(path, _text):
        attempted_writes.append(path)
        raise AssertionError(f"path validation reached a write: {path}")

    monkeypatch.setattr(E, "_atomic_write", reject_any_write)
    assert E.main(_build_argv(fixture, outputs)) == 2
    assert attempted_writes == []
    assert not canonical_probe.exists()
    assert not any(path.exists() for path in outputs.values())


def _require_physical_case_alias(alias: Path, canonical: Path) -> Path:
    try:
        physically_identical = alias.samefile(canonical)
    except OSError:
        physically_identical = False
    if not physically_identical:
        pytest.skip("filesystem does not expose this case-varied path as the same file")
    return alias


@pytest.mark.parametrize("output_name", ["candidates", "mappings", "evidence", "blocked"])
@pytest.mark.parametrize(
    "protected_root_name",
    ["canonical-traits", "canonical-grounding", "selected-traits"],
)
def test_build_rejects_every_output_through_case_varied_physical_roots(
    tmp_path,
    monkeypatch,
    output_name,
    protected_root_name,
):
    fixture = _fixture(tmp_path)
    selected_traits = fixture["traits"]
    assert isinstance(selected_traits, Path)
    protected_roots = {
        "canonical-traits": E.TRAITS_ROOT,
        "canonical-grounding": E.GROUNDING_ROOT,
        "selected-traits": selected_traits,
    }
    protected_root = protected_roots[protected_root_name]
    if protected_root_name == "canonical-traits":
        case_alias = E.REPO_ROOT / "DATA" / "TRAITS"
    elif protected_root_name == "canonical-grounding":
        case_alias = E.REPO_ROOT / "DATA" / "GROUNDING"
    else:
        case_alias = selected_traits.with_name(selected_traits.name.swapcase())
    case_alias = _require_physical_case_alias(case_alias, protected_root)

    probe_name = f"_ecod_sifts_case_alias_probe_{output_name}.jsonl"
    canonical_probe = protected_root / probe_name
    assert not canonical_probe.exists()
    outputs = {
        "candidates": tmp_path / "candidates.jsonl",
        "mappings": tmp_path / "mappings.jsonl",
        "evidence": tmp_path / "evidence.jsonl",
        "blocked": tmp_path / "blocked.jsonl",
    }
    outputs[output_name] = case_alias / probe_name
    attempted_writes: list[Path] = []

    def reject_any_write(path, _text):
        attempted_writes.append(path)
        raise AssertionError(f"case-alias validation reached a write: {path}")

    monkeypatch.setattr(E, "_atomic_write", reject_any_write)
    assert E.main(_build_argv(fixture, outputs)) == 2
    assert attempted_writes == []
    assert not canonical_probe.exists()
    assert not any(path.exists() for path in outputs.values())


@pytest.mark.parametrize("output_name", ["candidates", "mappings", "evidence", "blocked"])
@pytest.mark.parametrize("input_name", ["ecod", "proteins"])
def test_build_rejects_existing_input_case_aliases_before_any_write(
    tmp_path,
    monkeypatch,
    output_name,
    input_name,
):
    fixture = _fixture(tmp_path)
    protected_input = fixture[input_name]
    assert isinstance(protected_input, Path)
    case_alias = _require_physical_case_alias(
        protected_input.with_name(protected_input.name.swapcase()),
        protected_input,
    )
    before = protected_input.read_bytes()
    outputs = {
        "candidates": tmp_path / "candidates.jsonl",
        "mappings": tmp_path / "mappings.jsonl",
        "evidence": tmp_path / "evidence.jsonl",
        "blocked": tmp_path / "blocked.jsonl",
    }
    outputs[output_name] = case_alias
    attempted_writes: list[Path] = []

    def reject_any_write(path, _text):
        attempted_writes.append(path)
        raise AssertionError(f"input-alias validation reached a write: {path}")

    monkeypatch.setattr(E, "_atomic_write", reject_any_write)
    assert E.main(_build_argv(fixture, outputs)) == 2
    assert attempted_writes == []
    assert protected_input.read_bytes() == before


def test_build_rejects_case_varied_not_yet_existing_output_collision_before_write(
    tmp_path,
    monkeypatch,
):
    fixture = _fixture(tmp_path)
    upper = tmp_path / "Prospective-Output.JSONL"
    lower = tmp_path / "prospective-output.jsonl"
    assert not upper.exists()
    assert not lower.exists()
    outputs = {
        "candidates": upper,
        "mappings": lower,
        "evidence": tmp_path / "evidence.jsonl",
        "blocked": tmp_path / "blocked.jsonl",
    }
    attempted_writes: list[Path] = []

    def reject_any_write(path, _text):
        attempted_writes.append(path)
        raise AssertionError(f"output-collision validation reached a write: {path}")

    monkeypatch.setattr(E, "_atomic_write", reject_any_write)
    assert E.main(_build_argv(fixture, outputs)) == 2
    assert attempted_writes == []
    assert not any(path.exists() for path in outputs.values())


def test_build_rejects_unicode_normalized_prospective_output_collision_before_write(
    tmp_path,
    monkeypatch,
):
    fixture = _fixture(tmp_path)
    composed = tmp_path / "caf\N{LATIN SMALL LETTER E WITH ACUTE}.jsonl"
    decomposed = tmp_path / "cafe\N{COMBINING ACUTE ACCENT}.jsonl"
    assert not composed.exists()
    assert not decomposed.exists()
    outputs = {
        "candidates": composed,
        "mappings": decomposed,
        "evidence": tmp_path / "evidence.jsonl",
        "blocked": tmp_path / "blocked.jsonl",
    }
    attempted_writes: list[Path] = []

    def reject_any_write(path, _text):
        attempted_writes.append(path)
        raise AssertionError(f"unicode-collision validation reached a write: {path}")

    monkeypatch.setattr(E, "_atomic_write", reject_any_write)
    assert E.main(_build_argv(fixture, outputs)) == 2
    assert attempted_writes == []
    assert not any(path.exists() for path in outputs.values())


def test_build_and_fetch_reject_any_snapshot_or_output_under_traits(tmp_path):
    fixture = _fixture(tmp_path)
    forbidden_output = E.TRAITS_ROOT / "_forbidden_ecod_sifts_test_output.jsonl"
    forbidden_snapshot = E.TRAITS_ROOT / "forbidden-ecod-sifts-snapshot"
    assert not forbidden_output.exists()
    assert not forbidden_snapshot.exists()
    outputs = {
        "candidates": forbidden_output,
        "mappings": tmp_path / "mappings.jsonl",
        "evidence": tmp_path / "evidence.jsonl",
        "blocked": tmp_path / "blocked.jsonl",
    }
    assert E.main(_build_argv(fixture, outputs)) == 2
    assert not forbidden_output.exists()
    assert (
        E.main(
            [
                "fetch",
                "--ecod",
                str(fixture["ecod"]),
                "--snapshot-dir",
                str(E.TRAITS_ROOT),
                "--snapshot-id",
                "forbidden-ecod-sifts-snapshot",
            ]
        )
        == 2
    )
    assert not forbidden_snapshot.exists()
