#!/usr/bin/env python3
"""Map staged BioLiP binding residues through a completed residue-level SIFTS snapshot.

This is the missing middle boundary between the no-protein BioLiP source stage and a
future UniProt registry fetch.  It consumes:

* ``BIOLIP_MISSING_PROTEIN_SOURCE_OCCURRENCE`` rows from
  ``stage_biolip_missing_protein_candidates.py``; and
* a complete, manifest-bound PDBe residue-level SIFTS snapshot fetched by
  ``fetch_biolip_residue_sifts.py``.

Every output row remains candidate or blocker evidence.  A mapped BioLiP row names a
single UniProt accession and its mapped positions, but still claims no qualification:
BioLiP provider release/rights review, release-pinned ``ProteinReference`` rows, source
review, resolver integration, and explicit promotion authorization are all future gates.

There is no network, output-file, apply, trait-writer, or GroundingEvidence-writer mode.
Canonical JSONL is written to stdout, followed by a content-addressed summary row.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import build_ecod_sifts_candidates as ecod_sifts


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STAGE = REPO_ROOT / "reports/uniprot-grounding/biolip-missing-protein-stage.jsonl"
DEFAULT_SIFTS_SNAPSHOT = (
    REPO_ROOT / "data/raw/biolip-sifts-xml/biolip-missing-protein-2026-09-24-full"
)

SCHEMA_VERSION = 1
INPUT_OCCURRENCE_KIND = "BIOLIP_MISSING_PROTEIN_SOURCE_OCCURRENCE"
INPUT_SUMMARY_KIND = "BIOLIP_MISSING_PROTEIN_STAGE_SUMMARY"
SNAPSHOT_KIND = "BIOLIP_RESIDUE_LEVEL_SIFTS_SNAPSHOT"

MAPPING_KIND = "BIOLIP_SIFTS_MAPPING_CANDIDATE"
BLOCKER_KIND = "BIOLIP_SIFTS_MAPPING_BLOCKER"
REQUEST_KIND = "BIOLIP_SIFTS_PROTEIN_REFERENCE_REQUEST"
SUMMARY_KIND = "BIOLIP_SIFTS_MAPPING_STAGE_SUMMARY"

READY_STATUS = "MAPPED_TO_UNIPROT_CANONICAL_RESIDUES"
MISSING_PROTEIN_REFERENCE_STATUS = "MISSING_RELEASE_PINNED_PROTEIN_REFERENCE"
BLOCKED_STATUS = "BLOCKED_SIFTS_MAPPING"

PROVIDER_NAME = "BioLiP"
PROVIDER_KIND = "SOURCE_DATABASE"
MAPPING_METHOD = "SIFTS_RESIDUE_MAPPING"
SCOPE = "LOCALIZED"
COORDINATE_FRAME = "UNIPROT_CANONICAL"
SIFTS_XML_ROOT = "https://ftp.ebi.ac.uk/pub/databases/msd/sifts/xml"

PROMOTION_BLOCKERS = (
    "BIOLIP_HAS_NO_EXPLICIT_OPEN_LICENSE",
    "MISSING_BIOLIP_PROVIDER_RELEASE_RECEIPT",
    "MISSING_RELEASE_PINNED_PROTEIN_REFERENCE",
    "HUMAN_REVIEW_REQUIRED_BEFORE_PROMOTION",
    "EXPLICIT_PROMOTION_AUTHORIZATION_REQUIRED",
)


class BioLipSiftsMappingError(ValueError):
    """A BioLiP/SIFTS mapping input cannot produce a replayable candidate ledger."""


@dataclass(frozen=True)
class CapturedStage:
    path: Path
    sha256: str
    stage_id: str
    combined_non_summary_rows_sha256: str
    occurrences: tuple[dict[str, Any], ...]


@dataclass(frozen=True)
class Snapshot:
    path: Path
    manifest_path: Path
    manifest_sha256: str
    manifest: dict[str, Any]
    entries_by_pdb: Mapping[str, dict[str, Any]]
    uniprot_release: str


@dataclass(frozen=True)
class StageResult:
    mappings: tuple[dict[str, Any], ...]
    blockers: tuple[dict[str, Any], ...]
    protein_requests: tuple[dict[str, Any], ...]
    summary: dict[str, Any]


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def value_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _rows_sha256(rows: Iterable[Mapping[str, Any]]) -> str:
    payload = "".join(canonical_json(row) + "\n" for row in rows)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _content_address(
    row: dict[str, Any], *, id_field: str, prefix: str, row_hash_field: str
) -> dict[str, Any]:
    if id_field in row or row_hash_field in row:
        raise BioLipSiftsMappingError("content-address fields were already present")
    row[id_field] = prefix + value_sha256(row)
    row[row_hash_field] = value_sha256(row)
    return row


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return str(path)


def _require_text(value: Any, *, field: str, source: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise BioLipSiftsMappingError(f"{source} has invalid {field}")
    return value


def _read_canonical_json(path: Path, *, description: str) -> tuple[dict[str, Any], str]:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise BioLipSiftsMappingError(f"cannot read {description} {path}: {exc}") from exc
    digest = hashlib.sha256(raw).hexdigest()
    try:
        text = raw.decode("utf-8")
        value = json.loads(text)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BioLipSiftsMappingError(f"{description} is not valid JSON: {path}: {exc}") from exc
    if not isinstance(value, dict) or text != canonical_json(value) + "\n":
        raise BioLipSiftsMappingError(f"{description} is not one canonical JSON row: {path}")
    return value, digest


def _read_stage(path: Path) -> CapturedStage:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise BioLipSiftsMappingError(f"cannot read BioLiP stage {path}: {exc}") from exc
    occurrences: list[dict[str, Any]] = []
    summary: dict[str, Any] | None = None
    seen_occurrences: set[str] = set()
    for line_number, line in enumerate(raw.splitlines(keepends=True), 1):
        if not line.strip():
            raise BioLipSiftsMappingError(f"{path}:{line_number}: blank line")
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise BioLipSiftsMappingError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
        if not isinstance(row, dict):
            raise BioLipSiftsMappingError(f"{path}:{line_number}: row is not an object")
        if line != (canonical_json(row) + "\n").encode("utf-8"):
            raise BioLipSiftsMappingError(f"{path}:{line_number}: row is not canonical JSON")
        kind = row.get("kind")
        if kind == INPUT_SUMMARY_KIND:
            if summary is not None:
                raise BioLipSiftsMappingError("BioLiP stage contains multiple summary rows")
            summary = row
        elif kind == INPUT_OCCURRENCE_KIND:
            occurrence_id = _require_text(
                row.get("source_occurrence_id"),
                field="source_occurrence_id",
                source=f"{path}:{line_number}",
            )
            if occurrence_id in seen_occurrences:
                raise BioLipSiftsMappingError(f"duplicate occurrence {occurrence_id}")
            seen_occurrences.add(occurrence_id)
            if row.get("stage_status") == "READY_FOR_RESIDUE_LEVEL_SIFTS":
                occurrences.append(row)
    if summary is None:
        raise BioLipSiftsMappingError("BioLiP stage is missing its summary row")
    expected_count = summary.get("ready_for_residue_level_sifts_count")
    if expected_count != len(occurrences):
        raise BioLipSiftsMappingError(
            "BioLiP ready occurrence count mismatch: "
            f"summary={expected_count!r}, rows={len(occurrences)}"
        )
    return CapturedStage(
        path=path,
        sha256=hashlib.sha256(raw).hexdigest(),
        stage_id=_require_text(summary.get("stage_id"), field="stage_id", source=str(path)),
        combined_non_summary_rows_sha256=_require_text(
            summary.get("combined_non_summary_rows_sha256"),
            field="combined_non_summary_rows_sha256",
            source=str(path),
        ),
        occurrences=tuple(occurrences),
    )


def _read_snapshot(path: Path, *, stage: CapturedStage) -> Snapshot:
    manifest_path = path / "manifest.json"
    manifest, digest = _read_canonical_json(
        manifest_path,
        description="BioLiP SIFTS manifest",
    )
    if manifest.get("kind") != SNAPSHOT_KIND:
        raise BioLipSiftsMappingError("BioLiP SIFTS manifest has unexpected kind")
    if manifest.get("source_root") != SIFTS_XML_ROOT:
        raise BioLipSiftsMappingError("BioLiP SIFTS manifest source_root mismatch")
    if manifest.get("stage_sha256") != stage.sha256:
        raise BioLipSiftsMappingError("BioLiP SIFTS manifest is bound to a different stage")
    if manifest.get("stage_id") != stage.stage_id:
        raise BioLipSiftsMappingError("BioLiP SIFTS manifest stage_id mismatch")
    if (
        manifest.get("stage_combined_non_summary_rows_sha256")
        != stage.combined_non_summary_rows_sha256
    ):
        raise BioLipSiftsMappingError("BioLiP SIFTS manifest stage row digest mismatch")
    if manifest.get("complete") is not True:
        raise BioLipSiftsMappingError("BioLiP SIFTS manifest is incomplete")
    if manifest.get("failures") != []:
        raise BioLipSiftsMappingError("BioLiP SIFTS manifest contains failures")
    entries = manifest.get("entries")
    if not isinstance(entries, list) or not entries:
        raise BioLipSiftsMappingError("BioLiP SIFTS manifest contains no entries")
    expected_pdb_ids = sorted(
        {
            row["source_binding"]["source_occurrence_key"]["pdb_id"]
            for row in stage.occurrences
        }
    )
    if manifest.get("requested_pdb_count") != len(expected_pdb_ids):
        raise BioLipSiftsMappingError("BioLiP SIFTS manifest requested_pdb_count mismatch")
    if manifest.get("fetch_request_count") != len(expected_pdb_ids):
        raise BioLipSiftsMappingError("BioLiP SIFTS manifest fetch_request_count mismatch")
    pdb_ids: list[str] = []
    sifts_uniprot_releases: set[str] = set()
    entries_by_pdb: dict[str, dict[str, Any]] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            raise BioLipSiftsMappingError("BioLiP SIFTS manifest entry is not an object")
        pdb_id = _require_text(entry.get("pdb_id"), field="pdb_id", source=str(manifest_path))
        pdb_ids.append(pdb_id)
        sifts_uniprot_releases.add(
            _require_text(
                entry.get("sifts_uniprot_release"),
                field="sifts_uniprot_release",
                source=str(manifest_path),
            )
        )
        if entry.get("path") != f"{pdb_id}.xml.gz":
            raise BioLipSiftsMappingError(f"SIFTS manifest entry path mismatch for {pdb_id}")
        if pdb_id in entries_by_pdb:
            raise BioLipSiftsMappingError(f"duplicate SIFTS manifest entry for {pdb_id}")
        entries_by_pdb[pdb_id] = entry
    if pdb_ids != sorted(pdb_ids):
        raise BioLipSiftsMappingError("BioLiP SIFTS manifest entries are not sorted")
    if pdb_ids != expected_pdb_ids:
        missing = sorted(set(expected_pdb_ids) - set(pdb_ids))
        unexpected = sorted(set(pdb_ids) - set(expected_pdb_ids))
        raise BioLipSiftsMappingError(
            "BioLiP SIFTS manifest PDB set mismatch: "
            f"missing={missing!r}, unexpected={unexpected!r}"
        )
    if len(sifts_uniprot_releases) != 1:
        raise BioLipSiftsMappingError(
            "BioLiP SIFTS manifest contains multiple SIFTS UniProt releases"
        )
    return Snapshot(
        path=path,
        manifest_path=manifest_path,
        manifest_sha256=digest,
        manifest=manifest,
        entries_by_pdb=entries_by_pdb,
        uniprot_release=next(iter(sifts_uniprot_releases)),
    )


def _load_sifts_indexes(
    snapshot: Snapshot, occurrences: Sequence[dict[str, Any]]
) -> dict[str, Mapping[tuple[str, ecod_sifts.NativePosition | None], list[ecod_sifts.SiftsResidue]]]:
    requested_pdbs = {
        row["source_binding"]["source_occurrence_key"]["pdb_id"] for row in occurrences
    }
    indexes: dict[
        str, Mapping[tuple[str, ecod_sifts.NativePosition | None], list[ecod_sifts.SiftsResidue]]
    ] = {}
    for pdb_id in sorted(requested_pdbs):
        manifest_entry = snapshot.entries_by_pdb.get(pdb_id)
        if manifest_entry is None:
            raise BioLipSiftsMappingError(f"BioLiP stage references unsnapshotted PDB {pdb_id}")
        xml_path = snapshot.path / str(manifest_entry["path"])
        entry = ecod_sifts.load_sifts_xml(xml_path)
        if entry.pdb_id != pdb_id:
            raise BioLipSiftsMappingError(f"{xml_path}: SIFTS PDB id mismatch")
        if entry.xml_sha256 != manifest_entry.get("sha256"):
            raise BioLipSiftsMappingError(f"{xml_path}: SIFTS XML digest changed")
        by_author: dict[
            tuple[str, ecod_sifts.NativePosition | None], list[ecod_sifts.SiftsResidue]
        ] = defaultdict(list)
        for residue in entry.residues:
            by_author[(residue.chain, residue.native)].append(residue)
        indexes[pdb_id] = by_author
    return indexes


def _manifest_projection(snapshot: Snapshot, pdb_id: str) -> dict[str, Any]:
    entry = dict(snapshot.entries_by_pdb[pdb_id])
    return {
        "sifts_manifest_entry": entry,
        "sifts_manifest_entry_sha256": value_sha256(entry),
        "sifts_manifest_path": _display_path(snapshot.manifest_path),
        "sifts_manifest_sha256": snapshot.manifest_sha256,
        "sifts_snapshot_id": snapshot.manifest["snapshot_id"],
    }


def _source_projection(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "binding_residue_pairs": row["binding_residue_pairs"],
        "source_binding": row["source_binding"],
        "source_occurrence_id": row["source_occurrence_id"],
        "source_occurrence_row_sha256": row["source_occurrence_row_sha256"],
        "trait_binding": row["trait_binding"],
    }


def _blocker_row(
    row: Mapping[str, Any],
    *,
    reason: str,
    detail: str,
) -> dict[str, Any]:
    output: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "kind": BLOCKER_KIND,
        "stage_status": BLOCKED_STATUS,
        "blocking_reason": reason,
        "blocking_detail": detail,
        "qualification_claimed": False,
        "protein_identity_claimed": False,
        "uniprot_coordinates_claimed": False,
        "source_projection": _source_projection(row),
    }
    return _content_address(
        output,
        id_field="blocker_id",
        prefix="biolip-sifts-mapping-blocker:",
        row_hash_field="blocker_row_sha256",
    )


def _mapping_row(
    row: Mapping[str, Any],
    mapped: Sequence[tuple[int, Mapping[str, Any], ecod_sifts.SiftsResidue]],
    *,
    protein_id: str,
    snapshot: Snapshot,
) -> dict[str, Any]:
    pdb_id = row["source_binding"]["source_occurrence_key"]["pdb_id"]
    mapped_residues = [
        {
            "author_insertion_code": pair["author_insertion_code"],
            "author_residue_number": pair["author_residue_number"],
            "chain_id": res.chain,
            "ordinal": ordinal,
            "pdb_amino_acid": res.pdb_amino_acid,
            "pdbe_sequence_position": res.pdbe_position,
            "source_amino_acid": pair["source_amino_acid"],
            "uniprot_amino_acid": res.uniprot_amino_acid,
            "uniprot_position": res.uniprot_position,
        }
        for ordinal, pair, res in mapped
    ]
    residue_positions = [int(item["uniprot_position"]) for item in mapped_residues]
    output: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "kind": MAPPING_KIND,
        "stage_status": READY_STATUS,
        "qualification_claimed": False,
        "protein_identity_claimed": True,
        "uniprot_coordinates_claimed": True,
        "provider": PROVIDER_NAME,
        "provider_kind": PROVIDER_KIND,
        "mapping_method": MAPPING_METHOD,
        "scope": SCOPE,
        "coordinate_frame": COORDINATE_FRAME,
        "structure_id": row["source_binding"]["structure_id"],
        "chain_id": row["source_binding"]["source_occurrence_key"]["receptor_chain"],
        "protein_id": protein_id,
        "trait_id": row["trait_binding"]["trait_id"],
        "record_path": row["trait_binding"]["trait_record_path"],
        "record_sha256": row["trait_binding"]["trait_record_sha256"],
        "residue_positions": residue_positions,
        "expected_residues": "".join(str(item["source_amino_acid"]) for item in mapped_residues),
        "source_residue_count": row["source_residue_count"],
        "mapped_residue_count": len(mapped_residues),
        "mapping_completeness": "COMPLETE",
        "mapped_residues": mapped_residues,
        "source_projection": _source_projection(row),
        "sifts_snapshot": _manifest_projection(snapshot, pdb_id),
        "promotion_blocking_reasons": list(PROMOTION_BLOCKERS),
    }
    return _content_address(
        output,
        id_field="candidate_id",
        prefix="biolip-sifts-mapping-candidate:",
        row_hash_field="candidate_row_sha256",
    )


def _map_occurrence(
    row: Mapping[str, Any],
    *,
    sifts_index: Mapping[tuple[str, ecod_sifts.NativePosition | None], list[ecod_sifts.SiftsResidue]],
    snapshot: Snapshot,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    chain = row["source_binding"]["source_occurrence_key"]["receptor_chain"]
    mapped: list[tuple[int, Mapping[str, Any], ecod_sifts.SiftsResidue]] = []
    for pair in row["binding_residue_pairs"]:
        native = ecod_sifts.NativePosition(
            int(pair["author_residue_number"]),
            str(pair["author_insertion_code"]).upper(),
        )
        matches = sifts_index.get((chain, native), [])
        if not matches:
            return None, _blocker_row(
                row,
                reason="AUTHOR_RESIDUE_NOT_IN_SIFTS",
                detail=f"{chain}:{native.text()}",
            )
        if len(matches) > 1:
            return None, _blocker_row(
                row,
                reason="AMBIGUOUS_AUTHOR_RESIDUE",
                detail=f"{chain}:{native.text()}",
            )
        residue = matches[0]
        if (
            residue.ambiguous
            or residue.uniprot_accession is None
            or residue.uniprot_position is None
        ):
            return None, _blocker_row(
                row,
                reason="INCOMPLETE_UNIPROT_MAPPING",
                detail=f"{chain}:{native.text()}",
            )
        if residue.pdb_amino_acid != pair["source_amino_acid"]:
            return None, _blocker_row(
                row,
                reason="PDB_BIOLIP_RESIDUE_MISMATCH",
                detail=(
                    f"{chain}:{native.text()}:"
                    f"{residue.pdb_amino_acid}!={pair['source_amino_acid']}"
                ),
            )
        if residue.uniprot_amino_acid != pair["source_amino_acid"]:
            return None, _blocker_row(
                row,
                reason="UNIPROT_BIOLIP_RESIDUE_MISMATCH",
                detail=(
                    f"{chain}:{native.text()}:"
                    f"{residue.uniprot_amino_acid}!={pair['source_amino_acid']}"
                ),
            )
        mapped.append((int(pair["ordinal"]), pair, residue))
    accessions = {residue.uniprot_accession for _, _, residue in mapped}
    if len(accessions) != 1:
        return None, _blocker_row(
            row,
            reason="CHIMERIC_UNIPROT_MAPPING",
            detail=",".join(sorted(str(accession) for accession in accessions)),
        )
    if len({residue.uniprot_position for _, _, residue in mapped}) != len(mapped):
        return None, _blocker_row(row, reason="NON_UNIQUE_UNIPROT_POSITION", detail="")
    protein_id = f"UniProtKB:{next(iter(accessions))}"
    mapped.sort(key=lambda item: item[0])
    return _mapping_row(row, mapped, protein_id=protein_id, snapshot=snapshot), None


def build_stage(*, source_stage: Path, sifts_snapshot: Path) -> StageResult:
    stage = _read_stage(source_stage)
    snapshot = _read_snapshot(sifts_snapshot, stage=stage)
    sifts_indexes = _load_sifts_indexes(snapshot, stage.occurrences)
    mappings: list[dict[str, Any]] = []
    blockers: list[dict[str, Any]] = []
    for row in sorted(stage.occurrences, key=lambda item: item["source_occurrence_id"]):
        pdb_id = row["source_binding"]["source_occurrence_key"]["pdb_id"]
        mapping, blocker = _map_occurrence(row, sifts_index=sifts_indexes[pdb_id], snapshot=snapshot)
        if mapping is not None:
            mappings.append(mapping)
        if blocker is not None:
            blockers.append(blocker)

    by_protein: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in mappings:
        by_protein[row["protein_id"]].append(row)
    requests: list[dict[str, Any]] = []
    for protein_id in sorted(by_protein):
        rows = sorted(by_protein[protein_id], key=lambda item: item["candidate_id"])
        candidate_ids = [row["candidate_id"] for row in rows]
        request: dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "kind": REQUEST_KIND,
            "stage_status": MISSING_PROTEIN_REFERENCE_STATUS,
            "qualification_claimed": False,
            "protein_id": protein_id,
            "accession": protein_id.removeprefix("UniProtKB:"),
            "mapping_candidate_count": len(candidate_ids),
            "mapping_candidate_ids": candidate_ids,
            "mapping_candidate_ids_sha256": value_sha256(candidate_ids),
            "trait_ids": sorted({row["trait_id"] for row in rows}),
            "record_paths": sorted({row["record_path"] for row in rows}),
            "sifts_uniprot_release": snapshot.uniprot_release,
        }
        requests.append(
            _content_address(
                request,
                id_field="request_id",
                prefix="biolip-sifts-protein-reference-request:",
                row_hash_field="request_row_sha256",
            )
        )

    summary: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "kind": SUMMARY_KIND,
        "qualification_claimed": False,
        "source_stage_path": _display_path(stage.path),
        "source_stage_sha256": stage.sha256,
        "source_stage_id": stage.stage_id,
        "sifts_snapshot_path": _display_path(snapshot.path),
        "sifts_manifest_sha256": snapshot.manifest_sha256,
        "ready_source_occurrence_count": len(stage.occurrences),
        "mapping_candidate_count": len(mappings),
        "mapping_blocker_count": len(blockers),
        "mapped_unique_trait_count": len({row["record_path"] for row in mappings}),
        "mapped_unique_protein_count": len(by_protein),
        "protein_reference_request_count": len(requests),
        "blocker_reason_counts": dict(Counter(row["blocking_reason"] for row in blockers)),
        "mapping_candidate_rows_sha256": _rows_sha256(mappings),
        "mapping_blocker_rows_sha256": _rows_sha256(blockers),
        "protein_reference_request_rows_sha256": _rows_sha256(requests),
        "promotion_blocking_reasons": list(PROMOTION_BLOCKERS),
    }
    summary["stage_id"] = "biolip-sifts-mapping-stage:" + value_sha256(summary)
    return StageResult(tuple(mappings), tuple(blockers), tuple(requests), summary)


def render_stage(result: StageResult, *, summary_only: bool = False) -> str:
    rows = (
        [result.summary]
        if summary_only
        else [*result.mappings, *result.blockers, *result.protein_requests, result.summary]
    )
    return "".join(canonical_json(row) + "\n" for row in rows)


def parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stage", type=Path, default=DEFAULT_STAGE)
    ap.add_argument("--sifts-snapshot", type=Path, default=DEFAULT_SIFTS_SNAPSHOT)
    ap.add_argument("--summary-only", action="store_true")
    return ap


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        result = build_stage(source_stage=args.stage, sifts_snapshot=args.sifts_snapshot)
    except (OSError, BioLipSiftsMappingError, ecod_sifts.EcodSiftsError, KeyError) as exc:
        print(f"refusing to stage BioLiP SIFTS mappings: {exc}", file=sys.stderr)
        return 2
    sys.stdout.write(render_stage(result, summary_only=args.summary_only))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
