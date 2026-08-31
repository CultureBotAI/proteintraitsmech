"""Scientific and adversarial tests for the no-write DisProt source-native stage."""

from __future__ import annotations

import hashlib
import importlib
import json
import shutil
import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Mapping

import pytest
import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

stage = importlib.import_module("stage_disprot_source_native_grounding")
grounding = importlib.import_module("validate_uniprot_grounding")

UNIPROT_RELEASE = "2026_02"
SOURCE_SHA256 = "aeb8773ae59b2f569203c13a6515d3c2b1374168bd921f63daf4c2a0543e8844"
FRAME_SHA256 = "35f053876b234b92267c0f18e94bc8f085316f39343aa98668b714c610ba7848"
OCCURRENCE_ROWS_SHA256 = "23fa981b0237976bd051a3686f1c08a5adb6416bfb4ddff5c3d18f6e59bff5ab"
REQUEST_ROWS_SHA256 = "669eb58514fa6fa8a5986fa902d13b8e5fffcddba9dff7d6243fae1561e98b97"
COMBINED_ROWS_SHA256 = "3aaa94feb5f757f525ba0bda32dd12388643f7a63400b1da4cc55d82619282ea"
SUMMARY_ROW_SHA256 = "1ee6d608a105b157d8146cffa2ba60241a3718744554f36dd1c9292e6c2691e8"
STAGE_ID = (
    "disprot-source-native-stage:ae6b733744487ea1aa7c3f63569aaaa95d607f9b47204aa219124340aed372e1"
)
FULL_STREAM_SHA256 = "378a843980f6f3288e8270a85f4b5111e4a8c9977db18b71adfc18fe5ffcd095"

NAMESPACE_GROUPS = {
    "Structural state": (
        "proteintraitsmech:IDPO_STRUCTURAL_STATE",
        "disorder structural state",
        "A structural state of an intrinsically disordered region "
        "(disorder, order, molten globule, pre-molten globule).",
        "disorder-structural-state.yaml",
    ),
    "Structural transition": (
        "proteintraitsmech:IDPO_STRUCTURAL_TRANSITION",
        "disorder structural transition",
        "A conformational transition of a disordered region (e.g. disorder-to-order upon binding).",
        "disorder-structural-transition.yaml",
    ),
    "Disorder function": (
        "proteintraitsmech:IDPO_DISORDER_FUNCTION",
        "disorder-based function",
        "A function performed by an intrinsically disordered region "
        "(flexible linker/tail, PTM display site, self-regulation, "
        "molecular recognition, assembly).",
        "disorder-based-function.yaml",
    ),
}

TERM_META = {
    "IDPO:0000002": ("disorder", "Structural state"),
    "IDPO:0000011": ("disorder to order", "Structural transition"),
    "IDPO:0000033": ("flexible linker", "Disorder function"),
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _value_sha256(value: Any) -> str:
    return hashlib.sha256(stage.canonical_json(value).encode("utf-8")).hexdigest()


def _region(
    disprot_id: str,
    suffix: int,
    term_id: str,
    start: int,
    end: int,
    *,
    reference_source: str = "pmid",
    reference_id: str = "12345",
    ec_id: str = "ECO:0006165",
    ec_name: str = "nuclear magnetic resonance evidence",
    **extra: Any,
) -> dict[str, Any]:
    term_name, namespace = TERM_META[term_id]
    row: dict[str, Any] = {
        "annotation_extensions": [],
        "conditions": [],
        "construct_alterations": [],
        "cross_refs": [],
        "curator_id": "fixture-curator",
        "curator_name": "Fixture Curator",
        "curator_orcid": "0000-0002-1825-0097",
        "date": "2025-07-01T12:00:00.000Z",
        "disprot_namespace": namespace,
        "ec_go": "EXP",
        "ec_id": ec_id,
        "ec_name": ec_name,
        "ec_ontology": "ECO",
        "end": end,
        "interaction_partner": [],
        "reference_html": f"Fixture reference {reference_id}",
        "reference_id": reference_id,
        "reference_source": reference_source,
        "region_id": f"{disprot_id}r{suffix:03d}",
        "released": "2025_12",
        "sample": [],
        "start": start,
        "statement": [{"type": "Results", "text": "Fixture experimental statement."}],
        "states_connection": [],
        "term_id": term_id,
        "term_name": term_name,
        "term_namespace": namespace,
        "term_ontology": "IDPO",
        "validated": {
            "curator_id": "fixture-validator",
            "curator_name": "Fixture Validator",
            "timestamp": "2025-07-02T12:00:00.000Z",
        },
        "version": 1,
    }
    row.update(extra)
    return row


def _entry(
    accession: str,
    disprot_id: str,
    sequence: str,
    regions: list[dict[str, Any]],
    *,
    regions_counter: int | None = None,
) -> dict[str, Any]:
    consensus: dict[str, list[dict[str, Any]]] = {
        "full": [{"start": row["start"], "end": row["end"], "type": "D"} for row in regions]
    }
    for row in regions:
        consensus.setdefault(row["term_namespace"], []).append(
            {"start": row["start"], "end": row["end"], "type": "D"}
        )
    return {
        "acc": accession,
        "sequence": sequence,
        "creator": "fixture-curator",
        "dataset": [],
        "date": "2025-06-01T12:00:00.000Z",
        "disprot_id": disprot_id,
        "features": {"pfam": [], "gene3D": []},
        "genes": [],
        "length": len(sequence),
        "name": f"{accession} fixture protein",
        "ncbi_taxon_id": 9606,
        "organism": "Homo sapiens",
        "regions": regions,
        # This is an allocator/history field in production, not len(regions).
        "regions_counter": regions_counter if regions_counter is not None else len(regions),
        "released": "2025_06",
        "taxonomy": ["Eukaryota", "Metazoa"],
        "disorder_content": 0.25,
        "disprot_consensus": consensus,
    }


def _reference(protein_id: str, sequence: str) -> dict[str, Any]:
    return {
        "protein_id": protein_id,
        "protein_label": f"{protein_id} fixture protein",
        "taxon_id": "NCBITaxon:9606",
        "taxon_label": "Homo sapiens",
        "sequence": sequence,
        "sequence_length": len(sequence),
        "sequence_sha256": hashlib.sha256(sequence.encode("ascii")).hexdigest(),
        "sequence_version": 1,
        "reviewed": True,
        "uniprot_release": UNIPROT_RELEASE,
    }


def _write_source(path: Path, entries: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            entries, ensure_ascii=True, allow_nan=False, sort_keys=True, separators=(",", ":")
        ),
        encoding="utf-8",
    )


def _write_frame(
    path: Path,
    proteins: Mapping[str, str],
    *,
    absent: list[str],
    release: str = UNIPROT_RELEASE,
) -> None:
    value = {
        "_meta": {
            "schema": 1,
            "built": "2026-08-24",
            "source": "UniProt",
            "release": release,
            "count": len(proteins),
            "absent": sorted(absent),
        },
        "proteins": {
            accession: {"seq": sequence, "ft": []}
            for accession, sequence in sorted(proteins.items())
        },
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(stage.canonical_json(value), encoding="utf-8")


def _write_registry(path: Path, references: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(stage.canonical_json(item) + "\n" for item in references),
        encoding="utf-8",
    )


def _slug(text: str) -> str:
    return "-".join(
        part for part in "".join(c.lower() if c.isalnum() else " " for c in text).split()
    )


def _write_traits(traits_root: Path, entries: list[dict[str, Any]]) -> None:
    out = traits_root / "sequence" / "disorder"
    out.mkdir(parents=True, exist_ok=True)
    definition_source = "DisProt (Tosatto lab, U. Padova; IDPO-classed, proteins as examples)"
    for _namespace, (identifier, label, definition, filename) in NAMESPACE_GROUPS.items():
        record = {
            "identifier": identifier,
            "label": label,
            "definition": definition,
            "definition_source": definition_source,
            "trait_axis": "SEQUENCE",
            "trait_category": "SEQ_DISORDER",
            "term_kind": "CLASS",
            "mapping_status": "SEEDED",
            "license": "CC-BY-4.0",
        }
        (out / filename).write_text(yaml.safe_dump(record, sort_keys=False), encoding="utf-8")

    hits: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for entry in entries:
        for region in entry["regions"]:
            if region["term_ontology"] != "IDPO":
                continue
            example = hits[region["term_id"]].setdefault(
                entry["acc"],
                {
                    "protein_id": f"UniProtKB:{entry['acc']}",
                    "protein_label": entry["name"],
                    "taxon_id": f"NCBITaxon:{entry['ncbi_taxon_id']}",
                    "taxon_label": entry["organism"],
                    "sequence_length": entry["length"],
                    "note": f"DisProt entry {entry['disprot_id']}",
                    "source": "CURATOR",
                    "sequence": entry["sequence"],
                    "features": [],
                },
            )
            example["features"].append(
                {
                    "start": region["start"],
                    "end": region["end"],
                    "feature_type": "DISORDER",
                    "trait_axis": "SEQUENCE",
                    "trait_category": "SEQ_DISORDER",
                }
            )

    for term_id, proteins in hits.items():
        name, namespace = TERM_META[term_id]
        examples = sorted(
            proteins.values(), key=lambda item: (-len(item["features"]), item["protein_id"])
        )
        record = {
            "identifier": term_id,
            "label": name,
            "definition": (
                f"{name} — an IDPO disorder class ({namespace}, {term_id}); a protein "
                "region with this intrinsic-disorder property. "
                f"{len(proteins)} DisProt protein(s) annotated (examples below capped)."
            ),
            "definition_source": definition_source,
            "trait_axis": "SEQUENCE",
            "trait_category": "SEQ_DISORDER",
            "term_kind": "CLASS",
            "mapping_status": "SEEDED",
            "parent_traits": [NAMESPACE_GROUPS[namespace][0]],
            "canonical_examples": examples[:30],
            "license": "CC-BY-4.0",
        }
        filename = f"{_slug(name)}-{term_id.replace(':', '-').lower()}.yaml"
        (out / filename).write_text(yaml.safe_dump(record, sort_keys=False), encoding="utf-8")


def _case(tmp_path: Path) -> dict[str, Any]:
    repo = tmp_path / "repo"
    source = repo / "data/raw/disprot.entries.json"
    traits = repo / "data/traits"
    frame = repo / "data/raw/align_cache/residue_frame.json"
    registry = repo / "data/grounding/protein_registry.jsonl"

    exact_regions = [
        _region("DP00001", 1, "IDPO:0000002", 2, 4, reference_id="11111"),
        _region(
            "DP00001",
            2,
            "IDPO:0000002",
            2,
            4,
            reference_id="22222",
            ec_id="ECO:0006204",
            ec_name="circular dichroism evidence",
        ),
        _region(
            "DP00001",
            3,
            "IDPO:0000011",
            5,
            7,
            reference_source="doi",
            reference_id="10.1000/fixture",
            uniprot_changed=True,
            sequence_construct="TAD",
            construct_alterations=[
                {
                    "term_id": "IDPO:00480",
                    "term_name": "substitution",
                    "term_namespace": "Protein mutation",
                    "value": "p.Ile6Ala",
                    "start": None,
                    "end": None,
                    "position": None,
                }
            ],
            cross_refs=[{"db": "PDB", "id": "4TTB;PDB:4TTC"}],
        ),
    ]
    entries = [
        _entry("P11111", "DP00001", "MPEPTIDEK", exact_regions, regions_counter=9),
        _entry(
            "P22222",
            "DP00002",
            "MAGNIFYK",
            [
                _region(
                    "DP00002",
                    1,
                    "IDPO:0000033",
                    2,
                    5,
                    reference_source="mobidb",
                    reference_id="https://mobidb.org/P22222",
                )
            ],
        ),
        _entry(
            "P33333",
            "DP00003",
            "MQQQQQQK",
            [_region("DP00003", 1, "IDPO:0000002", 1, 3, reference_id="33333")],
        ),
        _entry(
            "P44444",
            "DP00004",
            "MSTATESK",
            [_region("DP00004", 1, "IDPO:0000011", 3, 6, reference_id="44444")],
        ),
    ]
    _write_source(source, entries)
    _write_traits(traits, entries)
    _write_frame(
        frame,
        {
            "P11111": "MPEPTIDEK",
            "P22222": "MAGNIFYK",
            # Deliberate full-protein mismatch against the DisProt export.
            "P44444": "MSTAQESK",
        },
        absent=["P33333"],
    )
    references = [
        _reference("UniProtKB:P11111", "MPEPTIDEK"),
        _reference("UniProtKB:P33333", "MQQQQQQK"),
        _reference("UniProtKB:P44444", "MSTATESK"),
    ]
    _write_registry(registry, references)
    return {
        "repo": repo,
        "source": source,
        "traits": traits,
        "frame": frame,
        "registry": registry,
        "entries": entries,
        "references": references,
        "source_sha256": _sha256(source),
        "frame_sha256": _sha256(frame),
    }


def _build(case: Mapping[str, Any]) -> stage.StageResult:
    return stage.build_stage(
        source_path=case["source"],
        traits_root=case["traits"],
        residue_frame_path=case["frame"],
        protein_registry_path=case["registry"],
        repo_root=case["repo"],
        expected_source_sha256=case["source_sha256"],
        expected_frame_sha256=case["frame_sha256"],
        expected_uniprot_release=UNIPROT_RELEASE,
    )


def _row(result: stage.StageResult, region_id: str) -> dict[str, Any]:
    return next(
        row for row in result.occurrences if row["source_binding"]["region_id"] == region_id
    )


def _assert_content_address(
    row: dict[str, Any], *, id_field: str, prefix: str, row_hash_field: str
) -> None:
    without_row_hash = dict(row)
    observed_row_hash = without_row_hash.pop(row_hash_field)
    assert observed_row_hash == _value_sha256(without_row_hash)
    observed_id = without_row_hash.pop(id_field)
    assert observed_id == prefix + _value_sha256(without_row_hash)


def test_stage_partitions_source_evidence_and_duplicate_coordinates(tmp_path: Path) -> None:
    result = _build(_case(tmp_path))
    assert len(result.occurrences) == 6
    assert result.summary["idpo_region_count"] == 6
    assert result.summary["trait_count"] == 3
    assert result.summary["protein_count"] == 4
    assert result.summary["trait_protein_pair_count"] == 5
    assert result.summary["local_registry_sequence_match_candidate_count"] == 3
    assert result.summary["exact_frame_missing_registry_count"] == 1
    assert result.summary["not_in_residue_frame_count"] == 1
    assert result.summary["residue_frame_sequence_mismatch_count"] == 1
    assert result.summary["missing_protein_reference_request_count"] == 1
    assert result.summary["grounding_evidence_emitted_count"] == 0

    first = _row(result, "DP00001r001")
    duplicate = _row(result, "DP00001r002")
    assert first["grounding_status"] == "SEQUENCE_MATCHED_STAGING_ONLY_MISSING_RECEIPTS"
    assert duplicate["grounding_status"] == first["grounding_status"]
    assert first["occurrence_stage_id"] != duplicate["occurrence_stage_id"]
    assert first["source_binding"]["source_interval"] == {"start": 2, "end": 4}
    assert duplicate["source_binding"]["source_interval"] == {"start": 2, "end": 4}
    assert first["source_binding"]["reference_id"] == "11111"
    assert duplicate["source_binding"]["reference_id"] == "22222"
    assert first["source_binding"]["ec_id"] != duplicate["source_binding"]["ec_id"]
    candidate = first["local_registry_sequence_match_candidate"]
    assert candidate["qualification_status"] == "CANDIDATE_ONLY"
    assert candidate["source_evidence_id"] is None
    assert candidate["source_interval"] == {"start": 2, "end": 4}
    assert candidate["resolved_interval_sequence"] == "PEP"
    assert candidate["mapping_method"] == "SOURCE_NATIVE_COORDINATES"
    assert candidate["evidence_source"] == "DisProt"
    assert candidate["trait_id"] == candidate["source_trait_id"] == "IDPO:0000002"
    assert "expected_sequence" not in candidate
    assert not first["grounding_evidence_emitted"]

    missing_registry = _row(result, "DP00002r001")
    assert missing_registry["grounding_status"] == "MISSING_LOCAL_PROTEIN_REFERENCE"
    assert missing_registry["local_registry_sequence_match_candidate"] is None
    assert result.protein_requests[0]["protein_id"] == "UniProtKB:P22222"
    assert result.protein_requests[0]["expected_uniprot_release"] == UNIPROT_RELEASE

    not_in_frame = _row(result, "DP00003r001")
    assert not_in_frame["grounding_status"] == "NOT_IN_RESIDUE_FRAME"
    assert not_in_frame["local_registry_sequence_match_candidate"] is None
    mismatch = _row(result, "DP00004r001")
    assert mismatch["grounding_status"] == "SOURCE_RESIDUE_FRAME_SEQUENCE_MISMATCH"
    assert mismatch["local_registry_sequence_match_candidate"] is None


def test_all_three_namespaces_bind_only_exact_idpo_traits(tmp_path: Path) -> None:
    result = _build(_case(tmp_path))
    observed = {
        (
            row["source_binding"]["source_trait_id"],
            row["source_binding"]["term_namespace"],
            row["trait_binding"]["parent_trait_id"],
        )
        for row in result.occurrences
    }
    assert observed == {
        (
            "IDPO:0000002",
            "Structural state",
            "proteintraitsmech:IDPO_STRUCTURAL_STATE",
        ),
        (
            "IDPO:0000011",
            "Structural transition",
            "proteintraitsmech:IDPO_STRUCTURAL_TRANSITION",
        ),
        (
            "IDPO:0000033",
            "Disorder function",
            "proteintraitsmech:IDPO_DISORDER_FUNCTION",
        ),
    }
    assert all(
        row["trait_id"] == row["source_binding"]["source_trait_id"] for row in result.occurrences
    )


def test_construct_and_changed_sequence_context_stays_blocking_and_visible(tmp_path: Path) -> None:
    row = _row(_build(_case(tmp_path)), "DP00001r003")
    source = row["source_binding"]
    assert source["uniprot_changed"] is True
    assert source["sequence_construct"] == "TAD"
    assert source["construct_alterations"][0]["term_name"] == "substitution"
    assert source["cross_refs"] == [{"db": "PDB", "id": "4TTB;PDB:4TTC"}]
    assert any("UNIPROT_CHANGED" in blocker for blocker in row["promotion_blockers"])
    assert any("CONSTRUCT" in blocker for blocker in row["promotion_blockers"])
    assert row["local_registry_sequence_match_candidate"] is not None
    assert row["local_registry_sequence_match_candidate"]["qualification_status"] == (
        "CANDIDATE_ONLY"
    )
    candidate = row["local_registry_sequence_match_candidate"]
    assert candidate["trait_id"] == candidate["source_trait_id"] == "IDPO:0000011"
    assert candidate["mapping_method"] == "SOURCE_NATIVE_COORDINATES"
    assert candidate["scope"] == "LOCALIZED"
    assert "source_release" not in candidate
    assert "provider_release" not in candidate
    assert "structure_id" not in stage.canonical_json(row)
    assert not row["grounding_evidence_emitted"]


def test_render_is_canonical_content_addressed_deterministic_and_no_write(
    tmp_path: Path,
) -> None:
    case = _case(tmp_path)
    before = {
        path.relative_to(case["repo"]).as_posix(): _sha256(path)
        for path in case["repo"].rglob("*")
        if path.is_file() and not path.is_symlink()
    }
    result = _build(case)
    rendered = stage.render_stage(result)
    assert stage.render_stage(_build(case)) == rendered
    decoded = [json.loads(line) for line in rendered.splitlines()]
    assert decoded == [*result.occurrences, *result.protein_requests, result.summary]
    for row in result.occurrences:
        _assert_content_address(
            row,
            id_field="occurrence_stage_id",
            prefix="disprot-source-occurrence:",
            row_hash_field="occurrence_row_sha256",
        )
    for row in result.protein_requests:
        _assert_content_address(
            row,
            id_field="request_id",
            prefix="disprot-protein-request:",
            row_hash_field="request_row_sha256",
        )
    _assert_content_address(
        result.summary,
        id_field="stage_id",
        prefix="disprot-source-native-stage:",
        row_hash_field="summary_row_sha256",
    )
    summary_rendered = stage.render_stage(result, summary_only=True)
    assert summary_rendered.count("\n") == 1
    assert json.loads(summary_rendered) == result.summary
    after = {
        path.relative_to(case["repo"]).as_posix(): _sha256(path)
        for path in case["repo"].rglob("*")
        if path.is_file() and not path.is_symlink()
    }
    assert after == before


def test_source_json_identity_coordinates_and_term_contracts_fail_closed(tmp_path: Path) -> None:
    duplicate_key = _case(tmp_path / "duplicate-key")
    raw = duplicate_key["source"].read_bytes()
    raw = raw.replace(b'{"acc":"P11111",', b'{"acc":"P11111","acc":"P11111",', 1)
    duplicate_key["source"].write_bytes(raw)
    duplicate_key["source_sha256"] = _sha256(duplicate_key["source"])
    with pytest.raises(ValueError, match="duplicate key"):
        _build(duplicate_key)

    duplicate_region = _case(tmp_path / "duplicate-region")
    duplicate_region["entries"][1]["regions"][0]["region_id"] = "DP00001r001"
    _write_source(duplicate_region["source"], duplicate_region["entries"])
    duplicate_region["source_sha256"] = _sha256(duplicate_region["source"])
    with pytest.raises(ValueError, match="duplicate.*region|region.*duplicate"):
        _build(duplicate_region)

    out_of_bounds = _case(tmp_path / "bounds")
    out_of_bounds["entries"][0]["regions"][0]["end"] = 99
    _write_source(out_of_bounds["source"], out_of_bounds["entries"])
    out_of_bounds["source_sha256"] = _sha256(out_of_bounds["source"])
    with pytest.raises(ValueError, match="bound|coordinate"):
        _build(out_of_bounds)

    term_conflict = _case(tmp_path / "term-conflict")
    term_conflict["entries"][2]["regions"][0]["term_name"] = "forged disorder name"
    _write_source(term_conflict["source"], term_conflict["entries"])
    term_conflict["source_sha256"] = _sha256(term_conflict["source"])
    with pytest.raises(ValueError, match="term|identity|name"):
        _build(term_conflict)


def test_source_and_frame_pins_and_releases_fail_closed(tmp_path: Path) -> None:
    source_pin = _case(tmp_path / "source-pin")
    source_pin["source_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="SHA-256|sha256|digest"):
        _build(source_pin)

    frame_pin = _case(tmp_path / "frame-pin")
    frame_pin["frame_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="SHA-256|sha256|digest"):
        _build(frame_pin)

    frame_release = _case(tmp_path / "frame-release")
    _write_frame(
        frame_release["frame"],
        {
            "P11111": "MPEPTIDEK",
            "P22222": "MAGNIFYK",
            "P44444": "MSTAQESK",
        },
        absent=["P33333"],
        release="2026_01",
    )
    frame_release["frame_sha256"] = _sha256(frame_release["frame"])
    with pytest.raises(ValueError, match="release"):
        _build(frame_release)

    registry_release = _case(tmp_path / "registry-release")
    references = [dict(item) for item in registry_release["references"]]
    references[0]["uniprot_release"] = "2026_01"
    _write_registry(registry_release["registry"], references)
    with pytest.raises(ValueError, match="release"):
        _build(registry_release)


def test_trait_semantic_shadow_definition_and_grounding_drift_fail_closed(
    tmp_path: Path,
) -> None:
    shadow = _case(tmp_path / "shadow")
    shadow_path = shadow["traits"] / "sequence" / "other" / "shadow.yaml"
    shadow_path.parent.mkdir(parents=True)
    shadow_path.write_text("identifier: IDPO:0000002\n", encoding="utf-8")
    with pytest.raises(ValueError, match="outside|shadow|duplicate"):
        _build(shadow)

    definition = _case(tmp_path / "definition")
    trait_path = definition["traits"] / "sequence/disorder/disorder-idpo-0000002.yaml"
    trait = yaml.safe_load(trait_path.read_text(encoding="utf-8"))
    trait["definition"] = "Forged definition"
    trait_path.write_text(yaml.safe_dump(trait, sort_keys=False), encoding="utf-8")
    with pytest.raises(ValueError, match="definition|trait contract"):
        _build(definition)

    prequalified = _case(tmp_path / "prequalified")
    trait_path = prequalified["traits"] / "sequence/disorder/disorder-idpo-0000002.yaml"
    trait = yaml.safe_load(trait_path.read_text(encoding="utf-8"))
    trait["canonical_examples"][0]["qualification_status"] = "QUALIFIED"
    trait["canonical_examples"][0]["source_evidence_id"] = "forged:evidence"
    trait_path.write_text(yaml.safe_dump(trait, sort_keys=False), encoding="utf-8")
    with pytest.raises(ValueError, match="forbidden|grounding|qualification"):
        _build(prequalified)


def test_source_and_trait_symlinks_are_rejected(tmp_path: Path) -> None:
    source_case = _case(tmp_path / "source")
    original = source_case["source"].with_suffix(".original")
    source_case["source"].rename(original)
    source_case["source"].symlink_to(original)
    with pytest.raises(ValueError, match="symlink|without following"):
        _build(source_case)

    trait_case = _case(tmp_path / "trait")
    external = tmp_path / "external-disprot-trait.yaml"
    external.write_text("identifier: IDPO:9999999\n", encoding="utf-8")
    (trait_case["traits"] / "linked.yaml").symlink_to(external)
    with pytest.raises(ValueError, match="symlink"):
        _build(trait_case)


def test_cli_has_no_network_apply_or_output_mode() -> None:
    for argv in (
        ["--apply"],
        ["--out", "forbidden.jsonl"],
        ["--output", "forbidden.jsonl"],
        ["--fetch"],
    ):
        with pytest.raises(SystemExit):
            stage.parse_args(argv)


@pytest.mark.parametrize("conflict", ["sequence", "taxon"])
def test_registry_conflicts_never_become_candidates(tmp_path: Path, conflict: str) -> None:
    case = _case(tmp_path)
    references = [dict(item) for item in case["references"]]
    target = references[0]
    if conflict == "sequence":
        target["sequence"] = "APEPTIDEK"
        target["sequence_sha256"] = hashlib.sha256(b"APEPTIDEK").hexdigest()
    else:
        target["taxon_id"] = "NCBITaxon:10090"
        target["taxon_label"] = "Mus musculus"
    _write_registry(case["registry"], references)
    result = _build(case)
    expected_status = (
        "LOCAL_PROTEIN_REFERENCE_SOURCE_SEQUENCE_MISMATCH"
        if conflict == "sequence"
        else "LOCAL_PROTEIN_REFERENCE_SOURCE_TAXON_MISMATCH"
    )
    affected = [row for row in result.occurrences if row["protein_id"] == "UniProtKB:P11111"]
    assert len(affected) == 3
    assert {row["grounding_status"] for row in affected} == {expected_status}
    assert all(row["local_registry_sequence_match_candidate"] is None for row in affected)
    assert result.summary["local_registry_sequence_match_candidate_count"] == 0


def test_requests_cover_missing_references_even_when_frame_is_absent_or_mismatched(
    tmp_path: Path,
) -> None:
    case = _case(tmp_path)
    _write_registry(case["registry"], [case["references"][0]])
    result = _build(case)
    assert [row["protein_id"] for row in result.protein_requests] == [
        "UniProtKB:P22222",
        "UniProtKB:P33333",
        "UniProtKB:P44444",
    ]
    by_id = {row["protein_id"]: row for row in result.protein_requests}
    assert by_id["UniProtKB:P33333"]["residue_frame_status"] == (
        "EXPLICITLY_ABSENT_FROM_LOCAL_RESIDUE_FRAME"
    )
    assert by_id["UniProtKB:P44444"]["residue_frame_status"] == ("SOURCE_SEQUENCE_MISMATCH")


def test_escaped_uppercase_merge_and_duplicate_key_trait_shadows_fail_closed(
    tmp_path: Path,
) -> None:
    escaped = _case(tmp_path / "escaped")
    shadow = escaped["traits"] / "sequence" / "other" / "shadow.YML"
    shadow.parent.mkdir(parents=True)
    shadow.write_text('identifier: "\\x49DPO:0000002"\n', encoding="utf-8")
    with pytest.raises(ValueError, match="outside|shadow|duplicate"):
        _build(escaped)

    merged = _case(tmp_path / "merge")
    shadow = merged["traits"] / "sequence" / "other" / "shadow.Yaml"
    shadow.parent.mkdir(parents=True)
    shadow.write_text(
        "base: &base\n  identifier: IDPO:0000002\n<<: *base\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="parse|merge|constructor|shadow|outside"):
        _build(merged)

    duplicate = _case(tmp_path / "duplicate")
    trait_path = duplicate["traits"] / "sequence/disorder/disorder-idpo-0000002.yaml"
    trait_path.write_text(
        trait_path.read_text(encoding="utf-8") + "identifier: IDPO:0000002\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="duplicate key"):
        _build(duplicate)


def test_initially_irrelevant_prefilter_candidate_cannot_turn_into_shadow(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    case = _case(tmp_path)
    shadow = case["traits"] / "sequence" / "other" / "shadow.yaml"
    shadow.parent.mkdir(parents=True)
    shadow.write_text("# IDPO conservative prefilter\nidentifier: TEST:safe\n", encoding="utf-8")
    original = stage._load_yaml_mapping
    mutated = False

    def mutate_after_parse(raw: bytes, *, path: Path) -> Mapping[str, Any]:
        nonlocal mutated
        value = original(raw, path=path)
        if path == shadow and not mutated:
            shadow.write_text("identifier: IDPO:0000002\n", encoding="utf-8")
            mutated = True
        return value

    monkeypatch.setattr(stage, "_load_yaml_mapping", mutate_after_parse)
    with pytest.raises(ValueError, match="drifted"):
        _build(case)
    assert mutated


def test_stage_candidate_still_hits_central_disprot_receipt_lock(tmp_path: Path) -> None:
    row = _row(_build(_case(tmp_path)), "DP00001r001")
    candidate = row["local_registry_sequence_match_candidate"]
    snapshot_id = candidate["disprot_source_snapshot_id"]
    evidence = {
        "trait_id": candidate["trait_id"],
        "protein_id": candidate["protein_id"],
        "source_trait_id": candidate["source_trait_id"],
        "mapping_method": candidate["mapping_method"],
        "scope": candidate["scope"],
        "coordinate_frame": candidate["coordinate_frame"],
        "intervals": [candidate["source_interval"]],
        "evidence_source": candidate["evidence_source"],
        "source_release": snapshot_id,
        "sequence_sha256": candidate["resolved_protein_sequence_sha256"],
        "provider_kind": "SOURCE_DATABASE",
        "provider_source": "data/raw/disprot.entries.json",
        "provider_release": snapshot_id,
        "provider_entry_sha256": row["source_binding"]["source_region_canonical_object_sha256"],
    }
    evidence["evidence_id"] = grounding.compute_evidence_id(evidence)
    observed = {
        finding.code
        for finding in grounding.validate_grounding_evidence(
            evidence, path=Path("candidate-evidence.jsonl"), line=1
        )
    }
    assert "disprot_provider_receipt_required" in observed


def test_production_disprot_snapshot_when_artifacts_exist() -> None:
    required = [
        REPO / "data/raw/disprot.entries.json",
        REPO / "data/traits/sequence/disorder",
        REPO / "data/raw/align_cache/residue_frame.json",
        REPO / "data/grounding/protein_registry.jsonl",
    ]
    if not all(path.exists() for path in required):
        pytest.skip("ignored production DisProt/grounding artifacts are unavailable")
    result = stage.build_stage()
    summary = result.summary
    assert summary["idpo_region_count"] == 9_387
    assert summary["entry_count"] == 3_199
    assert summary["total_region_count"] == 13_396
    assert summary["go_region_count"] == 4_009
    assert summary["trait_count"] == 32
    assert summary["namespace_count"] == 3
    assert summary["trait_binding_count"] == 35
    assert summary["namespace_group_trait_binding_count"] == 3
    assert {row["trait_id"] for row in summary["namespace_group_trait_bindings"]} == {
        values[0] for values in NAMESPACE_GROUPS.values()
    }
    assert summary["protein_count"] == 3_198
    assert summary["trait_protein_pair_count"] == 4_689
    assert summary["regions_counter_excess_entry_count"] == 946
    assert summary["regions_counter_excess_total"] == 3_815
    assert summary["duplicate_coordinate_group_count"] == 1_067
    assert summary["duplicate_coordinate_extra_region_count"] == 1_735
    assert summary["structured_context_region_count"] == 1_857
    assert summary["construct_context_region_count"] == 787
    assert summary["uniprot_changed_region_count"] == 108
    assert summary["term_not_annotate_region_count"] == 2
    assert summary["citation_source_counts"] == {"doi": 3, "mobidb": 20, "pmid": 9_364}
    assert summary["eco_identity_count"] == 112
    assert summary["legacy_selected_example_count"] == 500
    assert summary["legacy_selected_unique_protein_count"] == 384
    assert summary["legacy_selected_feature_count"] == 1_401
    assert summary["legacy_cap_omitted_trait_protein_pair_count"] == 4_189
    assert summary["local_registry_sequence_match_candidate_count"] == 61
    assert summary["exact_frame_missing_registry_count"] == 7_616
    assert summary["not_in_residue_frame_count"] == 1_699
    assert summary["residue_frame_sequence_mismatch_count"] == 11
    assert summary["missing_protein_reference_request_count"] == 3_191
    assert summary["grounding_evidence_emitted_count"] == 0
    assert (
        summary["local_registry_sequence_match_candidate_count"]
        + summary["exact_frame_missing_registry_count"]
        + summary["not_in_residue_frame_count"]
        + summary["residue_frame_sequence_mismatch_count"]
        == summary["idpo_region_count"]
    )
    assert summary["expected_uniprot_release"] == UNIPROT_RELEASE
    assert summary["source_artifact"]["sha256"] == SOURCE_SHA256
    assert summary["residue_frame_artifact"]["sha256"] == FRAME_SHA256
    assert summary["occurrence_rows_sha256"] == OCCURRENCE_ROWS_SHA256
    assert summary["protein_request_rows_sha256"] == REQUEST_ROWS_SHA256
    assert summary["combined_non_summary_rows_sha256"] == COMBINED_ROWS_SHA256
    assert summary["summary_row_sha256"] == SUMMARY_ROW_SHA256
    assert summary["stage_id"] == STAGE_ID
    rendered = stage.render_stage(result)
    assert rendered.count("\n") == 12_579
    assert hashlib.sha256(rendered.encode("utf-8")).hexdigest() == FULL_STREAM_SHA256
    assert all(not row["grounding_evidence_emitted"] for row in result.occurrences)


def test_absent_ripgrep_falls_back_to_a_superset_with_an_identical_result(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The prefilter must not depend on ripgrep, which CI does not install (#571).

    Without this the fallback is dead code on any machine that has ripgrep --
    which is every machine where this suite has ever been run green, and never
    CI, where the fallback is the only path. The fallback is deliberately a
    strict superset rather than a second matcher, because reproducing ripgrep's
    escape, NUL, and UTF-16 semantics twice is how the two paths drift apart
    silently (#539). So assert containment, not set equality, and assert that
    what the stage actually produces is identical either way.
    """

    case = _case(tmp_path)
    root = case["traits"]
    if shutil.which("rg") is None:
        pytest.skip("ripgrep is absent here, so the fallback is already the only path")

    matched = stage.ripgrep_prefilter.ripgrep_paths(root, stage._IDPO_PREFILTER_PATTERNS, stage._IDPO_PREFILTER_LABEL)
    assert matched is not None
    walked = stage.ripgrep_prefilter.walked_paths(root, stage._IDPO_PREFILTER_LABEL)
    assert {Path(os.path.abspath(p)) for p in matched} <= {
        Path(os.path.abspath(p)) for p in walked
    }

    with_ripgrep = _build(case)
    monkeypatch.setenv("PATH", "")
    assert stage.ripgrep_prefilter.ripgrep_paths(root, stage._IDPO_PREFILTER_PATTERNS, stage._IDPO_PREFILTER_LABEL) is None
    without_ripgrep = _build(case)

    for attribute in ("occurrences", "protein_requests", "summary"):
        assert stage.canonical_json(getattr(without_ripgrep, attribute)) == stage.canonical_json(
            getattr(with_ripgrep, attribute)
        )


def test_the_fallback_refuses_an_unscannable_trait_root(tmp_path: Path) -> None:
    """The fallback must fail closed exactly where ripgrep does (#573).

    ``os.walk`` reports a missing or unreadable tree as an empty one, so without
    an explicit guard the fallback would scan nothing, find nothing, and report
    success -- in the one environment (no ripgrep) it exists to serve.
    """

    missing = tmp_path / "no-such-trait-root"
    with pytest.raises(stage.ripgrep_prefilter.PrefilterError, match="not a directory"):
        stage.ripgrep_prefilter.walked_paths(missing, stage._IDPO_PREFILTER_LABEL)

    unreadable = tmp_path / "unreadable"
    (unreadable / "nested").mkdir(parents=True)
    (unreadable / "nested" / "trait.yaml").write_text("identifier: X\n", encoding="utf-8")
    os.chmod(unreadable / "nested", 0o000)
    try:
        if os.access(unreadable / "nested", os.R_OK):
            pytest.skip("running as a user that ignores directory permissions")
        with pytest.raises(stage.ripgrep_prefilter.PrefilterError, match="cannot scan"):
            stage.ripgrep_prefilter.walked_paths(unreadable, stage._IDPO_PREFILTER_LABEL)
    finally:
        os.chmod(unreadable / "nested", 0o700)
