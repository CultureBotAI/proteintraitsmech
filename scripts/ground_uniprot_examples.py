#!/usr/bin/env python3
"""Resolve UniProt grounding candidates and explicitly promote reviewed examples.

This command is the fail-closed boundary between evidence discovery and trait-record
mutation.  ``resolve`` reads a candidate JSONL ledger and pinned local providers.  It
never writes under ``data/traits``; it emits deterministic resolved/review ledgers and a
deduplicated ProteinReference registry.  ``promote`` is dry-run by default, requires an
approval TSV bound to the exact resolution digest, rechecks provider-entry digests, and
uses :func:`record_io.write_validated_record` for every applied record.

Typical use::

    uv run python scripts/ground_uniprot_examples.py resolve \
      --queue reports/uniprot-grounding/candidates.jsonl \
      --providers protein-registry,interpro --batch ready-local

    # Copy review.tsv to approved.tsv and set decision=APPROVED only after review.
    uv run python scripts/ground_uniprot_examples.py promote \
      --resolved reports/uniprot-grounding/resolved.jsonl \
      --approved reports/uniprot-grounding/approved.tsv --apply

There is intentionally no ``--allow-stale`` switch.  Re-resolve against changed source
entries and review the new resolution digest instead.

ECOD/SIFTS candidates can be resolved for review, but promotion is deliberately blocked
until the standalone semantic validator can replay an installed durable mapping registry
against its pinned ECOD source and immutable SIFTS manifest.
"""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import os
import re
import sys
import tempfile
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

import yaml

from fetch_uniprot_registry import (
    RegistryBuildError as FetchReceiptError,
    VerifiedFetchReceipt,
    verify_fetch_receipt,
)
from prints_kdat import (
    PRINTS_42_0_SHA256,
    PRINTS_42_0_SOURCE_ARTIFACT,  # noqa: F401 - public fixture/provider compatibility
    PrintsRelease,
    build_fingerprint_representation,
    parse_prints_kdat,
)
from prints_snapshot import (
    EXPECTED_PRINTS_SNAPSHOT_ID,
    HIERARCHY_NAME as PRINTS_HIERARCHY_NAME,
    MANIFEST_NAME as PRINTS_MANIFEST_NAME,
    PrintsSnapshotError,
    verify_prints_manifest,
)
from record_io import replace_block, write_validated_record
from uniprot_record_content_gate import (
    DEFAULT_PANTHER_CLASSIFICATIONS as DEFAULT_CONTENT_GATE_PANTHER_CLASSIFICATIONS,
    DEFAULT_PFAM_CLANS as DEFAULT_CONTENT_GATE_PFAM_CLANS,
    DEFAULT_PFAM_TYPES as DEFAULT_CONTENT_GATE_PFAM_TYPES,
    HARD as CONTENT_GATE_HARD,
    INTERPRO_109_XML_SHA256,
    PANTHER_19_CLASSIFICATIONS_SHA256,
    PFAM_A_CLANS_SHA256,
    PFAM_TYPES_SHA256,
    HARD_CODES as CONTENT_GATE_HARD_CODES,
    ContentGateError,
    RecordContentGate,
    SourceConfig,
    hard_reasons as record_content_hard_reasons,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TRAITS = REPO_ROOT / "data" / "traits"
DEFAULT_RESIDUE_FRAME = REPO_ROOT / "data" / "raw" / "align_cache" / "residue_frame.json"
DEFAULT_INTERPRO_FRAME = REPO_ROOT / "data" / "raw" / "align_cache" / "interpro_frame.json"
DEFAULT_PROFILES = REPO_ROOT / "data" / "profiles" / "profiles.jsonl"
DEFAULT_PRINTS_DIR = REPO_ROOT / "data" / "raw" / "interpro_members"
DEFAULT_PRINTS_API = DEFAULT_PRINTS_DIR / "prints.jsonl"
DEFAULT_PRINTS_KDAT = DEFAULT_PRINTS_DIR / "prints42_0.kdat"
DEFAULT_PRINTS_HIERARCHY = DEFAULT_PRINTS_DIR / PRINTS_HIERARCHY_NAME
DEFAULT_PRINTS_MANIFEST = DEFAULT_PRINTS_DIR / PRINTS_MANIFEST_NAME
DEFAULT_INTERPRO_XML = REPO_ROOT / "data" / "raw" / "interpro" / "interpro.xml.gz"
DEFAULT_OUT_DIR = REPO_ROOT / "reports" / "uniprot-grounding"
DEFAULT_EVIDENCE_REGISTRY = DEFAULT_OUT_DIR / "occurrence_evidence.jsonl"
DEFAULT_MEMBERSHIP_REGISTRY = DEFAULT_OUT_DIR / "uniprot_memberships.jsonl"
DEFAULT_DURABLE_PROTEIN_REGISTRY = REPO_ROOT / "data" / "grounding" / "protein_registry.jsonl"
DEFAULT_DURABLE_EVIDENCE_REGISTRY = REPO_ROOT / "data" / "grounding" / "occurrence_evidence.jsonl"
DEFAULT_DURABLE_MEMBERSHIP_REGISTRY = REPO_ROOT / "data" / "grounding" / "uniprot_memberships.jsonl"
DEFAULT_DURABLE_QUALIFIED_RECORD_BINDINGS = (
    REPO_ROOT / "data" / "grounding" / "qualified_record_bindings.jsonl"
)
PROTECTED_GROUNDING_ROOT = REPO_ROOT / "data" / "grounding"
MAX_PROMOTION_BATCH = 1_000
MIN_SOURCE_REVIEWS = 25

_QUALIFIED_RECORD_BINDING_FIELDS = frozenset(
    {
        "schema_version",
        "evidence_id",
        "candidate_id",
        "trait_id",
        "record_path",
        "record_sha256",
        "content_gate_projection",
        "content_gate_digest",
    }
)
_CONTENT_GATE_CANDIDATE_FIELDS = (
    "candidate_id",
    "trait_id",
    "source_trait_id",
    "mapping_method",
    "scope",
    "sequence_length",
    "intervals",
)

_MEMBERSHIP_RESOLUTION_REASONS = {
    "full release-pinned sequence and checksum require resolution",
    "exact membership must be replayed from a same-response UniProt xref snapshot",
}

_SFLD_SOURCE_MODEL_REPAIR_REASON = "unqualifiable:sfld_source_model_repair_required"
_PRINTS_FINGERPRINT_MODEL_REPLAY_REASON = "unqualifiable:prints_fingerprint_model_replay_required"

_UNIPROT = re.compile(
    r"^UniProtKB:([OPQ][0-9][A-Z0-9]{3}[0-9]|"
    r"[A-NR-Z][0-9](?:[A-Z][A-Z0-9]{2}[0-9]){1,2})(?:-([0-9]+))?$"
)
_TAXON = re.compile(r"^NCBITaxon:[0-9]+$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_SEQUENCE = re.compile(r"^[ACDEFGHIKLMNPQRSTVWYUOBZJX*]+$")
_CURIE = re.compile(r"^[A-Za-z][A-Za-z0-9._-]*:[A-Za-z0-9._-]+$")

_CANDIDATE_ID_FIELDS = (
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

_REVIEW_COLUMNS = (
    "candidate_id",
    "resolution_digest",
    "decision",
    "qualification_status",
    "trait_id",
    "protein_id",
    "record_path",
    "source_namespace",
    "trait_axis",
    "trait_category",
    "scope",
    "evidence_tier",
    "mapping_method",
    "evidence_source",
    "source_release",
    "uniprot_release",
    "intervals",
    "review_flags",
    "reasons",
    "reviewer",
    "reviewed_at",
    "review_notes",
)

_REVIEW_DATE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")


class GroundingError(ValueError):
    """A command-level safety invariant failed."""


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _value_digest(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _text_digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _is_sfld_grounding(*claims: Any) -> bool:
    """Recognize SFLD identity independently of mutable qualification fields."""

    for claim in claims:
        if not isinstance(claim, dict):
            continue
        namespace = _clean_text(claim.get("source_namespace"))
        if namespace and namespace.upper() == "SFLD":
            return True
        for field_name in ("identifier", "trait_id", "source_trait_id"):
            curie = _clean_text(claim.get(field_name))
            if curie and curie.partition(":")[0].upper() == "SFLD":
                return True
    return False


def _is_prints_grounding(*claims: Any) -> bool:
    """Recognize PRINTS identity independently of mutable qualification fields."""

    for claim in claims:
        if not isinstance(claim, dict):
            continue
        namespace = _clean_text(claim.get("source_namespace"))
        if namespace and namespace.upper() == "PRINTS":
            return True
        for field_name in ("identifier", "trait_id", "source_trait_id"):
            curie = _clean_text(claim.get(field_name))
            if curie and curie.partition(":")[0].upper() == "PRINTS":
                return True
    return False


def _prints_representation_projection(representation: Any) -> dict[str, Any] | None:
    """Return the source-model fields that must replay independently of prose."""

    if not isinstance(representation, dict):
        return None
    motifs = representation.get("motifs")
    if not isinstance(motifs, list) or any(not isinstance(motif, dict) for motif in motifs):
        return None
    return {
        "source_accession": representation.get("source_accession"),
        "source_release": representation.get("source_release"),
        "representation_type": representation.get("representation_type"),
        "source_artifact": representation.get("source_artifact"),
        "source_artifact_sha256": representation.get("source_artifact_sha256"),
        "source_record_sha256": representation.get("source_record_sha256"),
        "compatible_derivation_tool_hint": representation.get("compatible_derivation_tool_hint"),
        "motif_count": representation.get("motif_count"),
        "motifs": [
            {
                "ordinal": motif.get("ordinal"),
                "motif_code": motif.get("motif_code"),
                "length": motif.get("length"),
                "description": motif.get("description"),
                "training_instance_count": motif.get("training_instance_count"),
                "source_motif_sha256": motif.get("source_motif_sha256"),
                "training_distance_from_previous_min": motif.get(
                    "training_distance_from_previous_min"
                ),
                "training_distance_from_previous_max": motif.get(
                    "training_distance_from_previous_max"
                ),
                **(
                    {
                        "inter_motif_distance_constraint": motif.get(
                            "inter_motif_distance_constraint"
                        )
                    }
                    if "inter_motif_distance_constraint" in motif
                    else {}
                ),
            }
            for motif in motifs
        ],
    }


def _prints_interval_shape_diagnostic(
    row: dict[str, Any],
    record: dict[str, Any],
    intervals: list[dict[str, int]],
    context: ProviderContext,
) -> tuple[dict[str, Any] | None, list[dict[str, Any]], list[str]]:
    """Compare anonymous interval shape with a PRINTS model, without replay claims.

    InterPro-frame locations have lost hit grouping and motif identity.  Ascending
    starts plus a model-compatible count/length vector are therefore only shape
    compatibility, never proof of an ordered fingerprint occurrence.  This
    diagnostic deliberately cannot discharge the source-wide PRINTS gate.
    """

    if "prints-snapshot" not in context.providers:
        return None, [], []
    if context.prints_release is None or context.prints_manifest is None:
        return (
            None,
            [],
            ["missing:prints_snapshot_provider"],
        )
    trait_id = _clean_text(record.get("identifier")) or _clean_text(row.get("trait_id"))
    source_trait_id = _clean_text(row.get("source_trait_id")) or trait_id
    if not source_trait_id or not source_trait_id.upper().startswith("PRINTS:"):
        return None, [], ["mismatch:prints_source_trait_id"]
    accession = source_trait_id.split(":", 1)[1]
    fingerprint = context.prints_release.fingerprints.get(accession)
    if fingerprint is None:
        return None, [], ["missing:prints_fingerprint_model"]

    observed_lengths = [interval["end"] - interval["start"] + 1 for interval in intervals]
    expected_lengths = [motif.length for motif in fingerprint.motifs]
    starts = [interval["start"] for interval in intervals]
    count_matches = len(intervals) == fingerprint.declared_motif_count
    starts_ascending = all(left < right for left, right in zip(starts, starts[1:]))
    length_vector_matches = count_matches and observed_lengths == expected_lengths
    diagnostic_reasons: list[str] = []
    if not count_matches:
        diagnostic_reasons.append("mismatch:prints_anonymous_interval_count_vs_motif_count")
        status = (
            "ANONYMOUS_INTERVAL_COUNT_SHORT"
            if len(intervals) < fingerprint.declared_motif_count
            else "ANONYMOUS_INTERVAL_COUNT_MISMATCH"
        )
    elif not starts_ascending:
        diagnostic_reasons.append("mismatch:prints_anonymous_interval_start_order")
        status = "ANONYMOUS_INTERVAL_START_ORDER_MISMATCH"
    elif not length_vector_matches:
        diagnostic_reasons.append("mismatch:prints_anonymous_interval_length_vector")
        status = "ANONYMOUS_INTERVAL_LENGTH_VECTOR_MISMATCH"
    else:
        status = "ANONYMOUS_INTERVAL_SHAPE_COMPATIBLE"

    expected_representation = build_fingerprint_representation(context.prints_release, fingerprint)
    representations = record.get("sequence_fingerprint_representations")
    if not isinstance(representations, list) or not representations:
        record_model_status = "MISSING_RECORD_REPRESENTATION"
        diagnostic_reasons.append("missing:prints_record_fingerprint_representation")
    else:
        matching = [
            representation
            for representation in representations
            if isinstance(representation, dict)
            and representation.get("source_accession") == f"PRINTS:{fingerprint.accession}"
        ]
        if len(matching) != 1:
            record_model_status = "AMBIGUOUS_RECORD_REPRESENTATION"
            diagnostic_reasons.append("mismatch:prints_record_fingerprint_representation")
        elif _prints_representation_projection(matching[0]) != expected_representation:
            record_model_status = "MISMATCHED_RECORD_REPRESENTATION"
            diagnostic_reasons.append("mismatch:prints_record_fingerprint_representation")
        else:
            record_model_status = "EXACT_RECORD_REPRESENTATION"

    manifest_id = str(context.prints_manifest["manifest_id"])
    model_projection = {
        "manifest_id": manifest_id,
        "source_accession": f"PRINTS:{fingerprint.accession}",
        "source_release": context.prints_release.release,
        "source_artifact_sha256": context.prints_release.source_artifact_sha256,
        "source_record_sha256": fingerprint.source_record_sha256,
        "motif_count": fingerprint.declared_motif_count,
        "motifs": expected_representation["motifs"],
    }
    evidence = _provider_evidence(
        "prints_fingerprint_model",
        context.prints_manifest_path or Path("."),
        f"PRINTS:{fingerprint.accession}",
        model_projection,
        {"source": "PRINTS", "release": context.prints_release.release},
        trait_id=trait_id,
    )
    evidence["snapshot_manifest_id"] = manifest_id
    evidence["source_record_sha256"] = fingerprint.source_record_sha256
    diagnostic = {
        "status": status,
        "diagnostic_semantics": (
            "ANONYMOUS_INTERVAL_SHAPE_COMPATIBILITY_NOT_MOTIF_OCCURRENCE_REPLAY"
        ),
        "motif_identity_verified": False,
        "occurrence_grouping_verified": False,
        "grounding_eligible": False,
        "record_model_status": record_model_status,
        "source_accession": f"PRINTS:{fingerprint.accession}",
        "source_release": context.prints_release.release,
        "snapshot_manifest_id": manifest_id,
        "source_artifact_sha256": context.prints_release.source_artifact_sha256,
        "source_record_sha256": fingerprint.source_record_sha256,
        "expected_motif_count": fingerprint.declared_motif_count,
        "observed_interval_count": len(intervals),
        "expected_motif_lengths": expected_lengths,
        "observed_interval_lengths": observed_lengths,
        "observed_intervals": intervals,
        "ascending_interval_starts": starts_ascending,
        "count_matches_model": count_matches,
        "length_vector_matches_model": length_vector_matches,
    }
    return diagnostic, [evidence], diagnostic_reasons


def _accession(protein_id: str | None) -> str | None:
    if not protein_id:
        return None
    return protein_id.split(":", 1)[1] if protein_id.startswith("UniProtKB:") else protein_id


def _normalise_sha(value: Any) -> str | None:
    text = _clean_text(value)
    if text and text.lower().startswith("sha256:"):
        text = text.split(":", 1)[1]
    return text.lower() if text else None


def _normalise_intervals(value: Any) -> tuple[list[dict[str, int]], list[str]]:
    if value in (None, ""):
        return [], []
    if not isinstance(value, list):
        return [], ["invalid:intervals_not_a_list"]
    out: list[dict[str, int]] = []
    reasons: list[str] = []
    for number, raw in enumerate(value, 1):
        if isinstance(raw, dict):
            start, end = raw.get("start"), raw.get("end")
        elif isinstance(raw, (list, tuple)) and len(raw) == 2:
            start, end = raw
        else:
            reasons.append(f"invalid:interval_{number}_shape")
            continue
        try:
            start, end = int(start), int(end)
        except (TypeError, ValueError):
            reasons.append(f"invalid:interval_{number}_coordinate")
            continue
        out.append({"start": start, "end": end})
    return sorted(out, key=lambda row: (row["start"], row["end"])), reasons


def _normalise_positions(value: Any) -> tuple[list[int], list[str]]:
    if value in (None, ""):
        return [], []
    if not isinstance(value, list):
        return [], ["invalid:residue_positions_not_a_list"]
    out: list[int] = []
    reasons: list[str] = []
    for number, raw in enumerate(value, 1):
        try:
            out.append(int(raw))
        except (TypeError, ValueError):
            reasons.append(f"invalid:residue_position_{number}")
    return sorted(set(out)), reasons


def derive_candidate_id(row: dict[str, Any]) -> str:
    """Stable evidence identity shared by audits and candidate generators.

    The full digest is deliberately retained.  A new source or UniProt release,
    sequence checksum, or coordinate set is a new review candidate; changing only a
    display label is not.  Missing fields are represented as JSON null/empty arrays so
    incomplete generator rows still receive a deterministic ID after normalization.
    """
    intervals, _ = _normalise_intervals(row.get("intervals"))
    positions, _ = _normalise_positions(row.get("residue_positions"))
    identity = {
        "trait_id": _clean_text(row.get("trait_id")),
        "protein_id": _clean_text(row.get("protein_id")),
        "source_trait_id": _clean_text(row.get("source_trait_id")),
        "mapping_method": _clean_text(row.get("mapping_method")),
        "evidence_source": _clean_text(row.get("evidence_source")),
        "source_release": _clean_text(row.get("source_release")),
        "sequence_release": _clean_text(row.get("uniprot_release") or row.get("sequence_release")),
        "sequence_sha256": _normalise_sha(row.get("sequence_sha256")),
        "scope": _clean_text(row.get("scope")),
        "coordinate_frame": _clean_text(row.get("coordinate_frame")),
        "intervals": intervals,
        "residue_positions": positions,
    }
    payload = {key: identity[key] for key in _CANDIDATE_ID_FIELDS}
    if identity["mapping_method"] == "SIFTS_RESIDUE_MAPPING":
        # One ECOD trait/protein pair can have several independently reviewable
        # structure occurrences.  Their exact structure, chain, and content-addressed
        # mapping must therefore remain distinct producer rows.
        payload.update(
            {
                "structure_id": _clean_text(row.get("structure_id")),
                "chain_id": _clean_text(row.get("chain_id")),
                "ecod_domain_id": _clean_text(row.get("ecod_domain_id")),
                "sifts_mapping_id": _clean_text(row.get("sifts_mapping_id")),
            }
        )
    return "ug-" + _value_digest(payload)


def _resolution_digest(row: dict[str, Any]) -> str:
    return _value_digest({key: value for key, value in row.items() if key != "resolution_digest"})


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise GroundingError(f"JSONL input does not exist: {path}")
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise GroundingError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
            if not isinstance(row, dict):
                raise GroundingError(f"{path}:{line_number}: JSONL row is not an object")
            rows.append(row)
    return rows


def _read_verified_jsonl(raw: bytes, *, source: Path) -> list[dict[str, Any]]:
    """Parse an immutable JSONL image returned by the strict fetch verifier."""

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise GroundingError(f"verified JSONL is not strict UTF-8 ({source}): {exc}") from exc
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise GroundingError(f"{source}:{line_number}: invalid verified JSON: {exc}") from exc
        if not isinstance(row, dict):
            raise GroundingError(f"{source}:{line_number}: verified JSONL row is not an object")
        rows.append(row)
    return rows


def _atomic_bytes(path: Path, payload: bytes) -> None:
    """Atomically install exact bytes for a non-trait artifact or rollback image."""

    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _atomic_text(path: Path, text: str) -> None:
    """Atomically write a non-trait JSONL/TSV artifact."""

    _atomic_bytes(path, text.encode("utf-8"))


def _write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    text = "".join(_canonical_json(row) + "\n" for row in rows)
    _atomic_text(path, text)


def _display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(REPO_ROOT.resolve()))
    except ValueError:
        return str(resolved)


def _lexical_absolute(path: Path) -> str:
    """Return the same non-symlink-resolving absolute spelling used by fetch plans."""

    return str(Path(os.path.abspath(os.fspath(path))))


def _lexical_display_path(path: str | Path) -> str:
    """Display a receipt-bound path without consulting the live filesystem."""

    lexical = Path(_lexical_absolute(Path(path)))
    repository = Path(_lexical_absolute(REPO_ROOT))
    try:
        return str(lexical.relative_to(repository))
    except ValueError:
        return str(lexical)


def _verify_resolve_fetch_boundary(args: argparse.Namespace) -> VerifiedFetchReceipt | None:
    """Verify one bounded fetch generation, or require explicit historical mode."""

    boundary_paths = {
        "--fetch-receipt": args.fetch_receipt,
        "--fetch-request-plan": args.fetch_request_plan,
        "--selector-manifest": args.selector_manifest,
        "--protein-registry": args.protein_registry,
        "--membership-registry": args.membership_registry,
        "--registry-blocked": args.registry_blocked,
    }
    if args.allow_unreceipted_inputs:
        receipt_only_paths = {
            name: path
            for name, path in boundary_paths.items()
            if name not in {"--protein-registry", "--membership-registry"}
        }
        supplied = sorted(name for name, path in receipt_only_paths.items() if path is not None)
        if supplied:
            raise GroundingError(
                "--allow-unreceipted-inputs cannot be combined with receipt-bound inputs: "
                + ", ".join(supplied)
            )
        if args.expect_uniprot_release is not None or args.allow_offline_uniprot_fixture:
            raise GroundingError(
                "unreceipted resolution cannot claim a receipt release or offline-fixture waiver"
            )
        return None

    missing = sorted(name for name, path in boundary_paths.items() if path is None)
    if args.expect_uniprot_release is None:
        missing.append("--expect-uniprot-release")
    if missing:
        raise GroundingError(
            "receipt-bound resolve requires all fetch-generation inputs; missing: "
            + ", ".join(sorted(missing))
            + "; use --allow-unreceipted-inputs only for the generic historical path"
        )

    assert args.fetch_receipt is not None
    assert args.fetch_request_plan is not None
    assert args.selector_manifest is not None
    assert args.protein_registry is not None
    assert args.membership_registry is not None
    assert args.registry_blocked is not None
    try:
        verified = verify_fetch_receipt(
            receipt_path=args.fetch_receipt,
            request_plan_path=args.fetch_request_plan,
        )
    except FetchReceiptError as exc:
        raise GroundingError(f"invalid UniProt fetch receipt boundary: {exc}") from exc

    plan = verified.request_plan
    receipt = verified.receipt
    path_bindings = {
        "candidate queue": (args.queue, plan["candidate_artifact"]["path"]),
        "selector manifest": (
            args.selector_manifest,
            plan["selector_manifest_artifact"]["path"],
        ),
        "request plan": (
            args.fetch_request_plan,
            receipt["request_plan_artifact"]["path"],
        ),
        "fetch receipt": (args.fetch_receipt, plan["output_paths"]["fetch_receipt"]),
        "protein registry": (
            args.protein_registry,
            receipt["outputs"]["protein_registry"]["path"],
        ),
        "membership registry": (
            args.membership_registry,
            receipt["outputs"]["membership_registry"]["path"],
        ),
        "blocked registry": (
            args.registry_blocked,
            receipt["outputs"]["blocked_registry"]["path"],
        ),
    }
    mismatches = [
        f"{role}: {_lexical_absolute(path)} != {expected}"
        for role, (path, expected) in path_bindings.items()
        if _lexical_absolute(path) != expected
    ]
    if mismatches:
        raise GroundingError(
            "resolver inputs do not match the verified fetch generation: " + "; ".join(mismatches)
        )
    if plan["batch_id"] != args.batch or receipt["batch_id"] != args.batch:
        raise GroundingError(
            "resolver batch does not match verified fetch generation: "
            f"{args.batch!r} != {receipt['batch_id']!r}"
        )
    expected_release = args.expect_uniprot_release
    if (
        plan["expected_uniprot_release"] != expected_release
        or receipt["expected_uniprot_release"] != expected_release
        or receipt["observed_uniprot_release"] != expected_release
    ):
        raise GroundingError(
            "resolver release does not match verified fetch generation: "
            f"{expected_release!r} != {receipt['observed_uniprot_release']!r}"
        )
    acquisition_mode = plan["acquisition_mode"]
    if acquisition_mode == "OFFLINE_FIXTURE":
        if not args.allow_offline_uniprot_fixture:
            raise GroundingError(
                "OFFLINE_FIXTURE UniProt acquisition is test-only; "
                "pass --allow-offline-uniprot-fixture explicitly"
            )
    elif acquisition_mode != "UNIPROT_REST" or receipt["network_action_performed"] is not True:
        raise GroundingError(
            "production receipt-bound resolution requires a completed UNIPROT_REST acquisition"
        )
    return verified


def _stored_path(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else REPO_ROOT / path


def _load_sidecar(path: Path, payload_key: str = "proteins") -> tuple[dict[str, Any], dict]:
    if not path.is_file():
        return {}, {}
    try:
        blob = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise GroundingError(f"cannot read provider {path}: {exc}") from exc
    if not isinstance(blob, dict):
        raise GroundingError(f"provider {path} is not a JSON object")
    if "_meta" in blob:
        payload = blob.get(payload_key)
        if not isinstance(payload, dict):
            raise GroundingError(f"provider {path} has no object-valued {payload_key!r}")
        return payload, blob.get("_meta") or {}
    return blob, {"legacy": True, "source": None, "release": None}


def _load_object_or_jsonl(path: Path, wanted: set[str] | None = None) -> dict[str, dict]:
    """Load a ProteinReference registry in JSON object, wrapped, or JSONL form."""
    if not path.is_file():
        return {}
    text = path.read_text(encoding="utf-8")
    try:
        blob = json.loads(text)
    except json.JSONDecodeError:
        blob = None
    rows: list[dict]
    if isinstance(blob, dict) and (blob.get("protein_id") or blob.get("accession")):
        rows = [blob]
    elif isinstance(blob, dict):
        payload = blob.get("proteins", blob)
        if isinstance(payload, dict):
            rows = []
            for key, value in payload.items():
                if key == "_meta" or not isinstance(value, dict):
                    continue
                rows.append({"protein_id": value.get("protein_id") or key, **value})
        elif isinstance(payload, list):
            rows = [row for row in payload if isinstance(row, dict)]
        else:
            raise GroundingError(f"registry {path} has an unsupported JSON shape")
    else:
        rows = _read_jsonl(path)
    out: dict[str, dict] = {}
    for row in rows:
        protein_id = _clean_text(row.get("protein_id") or row.get("accession"))
        if not protein_id:
            continue
        if not protein_id.startswith("UniProtKB:"):
            protein_id = f"UniProtKB:{protein_id}"
        if wanted is not None and protein_id not in wanted:
            continue
        if protein_id in out and out[protein_id] != row:
            raise GroundingError(f"registry {path} contains conflicting rows for {protein_id}")
        out[protein_id] = {**row, "protein_id": protein_id}
    return out


def _load_profiles(path: Path, wanted: set[str]) -> dict[str, dict]:
    if not path.is_file() or not wanted:
        return {}
    out: dict[str, dict] = {}
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise GroundingError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
            protein_id = _clean_text(row.get("protein_id") or row.get("accession"))
            if protein_id and not protein_id.startswith("UniProtKB:"):
                protein_id = f"UniProtKB:{protein_id}"
            if protein_id in wanted:
                out[protein_id] = row
    return out


def _metadata_projection(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "protein_id": _clean_text(row.get("protein_id") or row.get("accession")),
        "protein_label": _clean_text(row.get("protein_label") or row.get("name")),
        "taxon_id": _clean_text(row.get("taxon_id") or row.get("taxon")),
        "taxon_label": _clean_text(row.get("taxon_label")),
        "sequence_length": row.get("sequence_length", row.get("length")),
        "reviewed": row.get("reviewed"),
    }


def _provider_evidence(
    kind: str,
    path: Path,
    key: str,
    projection: Any,
    meta: dict | None = None,
    *,
    trait_id: str | None = None,
    stable_path: str | None = None,
) -> dict[str, Any]:
    meta = meta or {}
    evidence: dict[str, Any] = {
        "kind": kind,
        "path": stable_path if stable_path is not None else _display_path(path),
        "key": key,
        "source": meta.get("source"),
        "release": meta.get("release"),
        "built": meta.get("built"),
        "entry_sha256": _value_digest(projection),
    }
    if trait_id:
        evidence["trait_id"] = trait_id
    return evidence


@dataclass
class ProviderContext:
    providers: set[str]
    residue_path: Path
    residue: dict[str, Any] = field(default_factory=dict)
    residue_meta: dict = field(default_factory=dict)
    interpro_path: Path | None = None
    interpro: dict[str, Any] = field(default_factory=dict)
    interpro_meta: dict = field(default_factory=dict)
    profiles_path: Path | None = None
    profiles: dict[str, dict] = field(default_factory=dict)
    registry_path: Path | None = None
    registry_evidence_path: str | None = None
    registry: dict[str, dict] = field(default_factory=dict)
    membership_path: Path | None = None
    membership_evidence_path: str | None = None
    memberships: list[dict[str, Any]] = field(default_factory=list)
    sifts_path: Path | None = None
    sifts_mappings: dict[str, dict[str, Any]] = field(default_factory=dict)
    prints_manifest_path: Path | None = None
    prints_manifest: dict[str, Any] | None = None
    prints_release: PrintsRelease | None = None
    durable_membership_path: Path = DEFAULT_DURABLE_MEMBERSHIP_REGISTRY
    record_cache: dict[Path, tuple[dict, str, str]] = field(default_factory=dict)
    content_gate: RecordContentGate | None = None


def _content_gate_config(args: argparse.Namespace) -> SourceConfig:
    """Bind record-content replay to caller-selected, checksum-pinned sources."""

    return SourceConfig(
        interpro_xml=args.interpro_xml.resolve(),
        interpro_xml_sha256=args.interpro_xml_sha256,
        pfam_clans=args.pfam_clans.resolve(),
        pfam_clans_sha256=args.pfam_clans_sha256,
        pfam_types=args.pfam_types.resolve(),
        pfam_types_sha256=args.pfam_types_sha256,
        panther_classifications=args.panther_classifications.resolve(),
        panther_classifications_sha256=args.panther_classifications_sha256,
    )


def _prepare_content_gate(
    records: Iterable[dict[str, Any]], args: argparse.Namespace
) -> RecordContentGate:
    try:
        return RecordContentGate(list(records), _content_gate_config(args))
    except ContentGateError as exc:
        raise GroundingError(f"record-content source replay failed closed: {exc}") from exc


def _provider_context(
    args: argparse.Namespace,
    candidates: list[dict],
    *,
    verified_fetch: VerifiedFetchReceipt | None = None,
) -> ProviderContext:
    providers = {part.strip() for part in args.providers.split(",") if part.strip()}
    aliases = {"residue-frame": "protein-registry", "interpro-frame": "interpro"}
    providers = {aliases.get(value, value) for value in providers}
    unknown = providers - {
        "protein-registry",
        "interpro",
        "profiles",
        "uniprot-membership",
        "sifts-mapping",
        "prints-snapshot",
    }
    if unknown:
        raise GroundingError(f"unknown provider(s): {', '.join(sorted(unknown))}")
    wanted = {
        protein_id
        for row in candidates
        if (protein_id := _clean_text(row.get("protein_id"))) is not None
    }
    residue_path = args.residue_frame.resolve()
    residue: dict[str, Any] = {}
    residue_meta: dict = {}
    profiles: dict[str, dict] = {}
    registry: dict[str, dict] = {}
    registry_path = (
        Path(verified_fetch.request_plan["output_paths"]["protein_registry"])
        if verified_fetch is not None
        else (args.protein_registry.resolve() if args.protein_registry else None)
    )
    registry_evidence_path = (
        _lexical_display_path(verified_fetch.request_plan["output_paths"]["protein_registry"])
        if verified_fetch is not None
        else None
    )
    if "protein-registry" in providers:
        residue, residue_meta = _load_sidecar(residue_path)
        if registry_path:
            if verified_fetch is not None:
                validated_registry = _semantic_registry_bytes(
                    verified_fetch.protein_registry_jsonl_bytes,
                    registry_path,
                )
            else:
                if not registry_path.is_file():
                    raise GroundingError(
                        f"explicit protein registry does not exist: {registry_path}"
                    )
                validated_registry = _semantic_registry(registry_path)
            registry = {
                protein_id: reference
                for protein_id, reference in validated_registry.items()
                if protein_id in wanted
            }
        if args.profiles.is_file():
            profiles = _load_profiles(args.profiles.resolve(), wanted)
    interpro_path = args.interpro_frame.resolve()
    interpro: dict[str, Any] = {}
    interpro_meta: dict = {}
    if "interpro" in providers:
        interpro, interpro_meta = _load_sidecar(interpro_path)
    membership_path = (
        Path(verified_fetch.request_plan["output_paths"]["membership_registry"])
        if verified_fetch is not None
        else (args.membership_registry.resolve() if args.membership_registry is not None else None)
    )
    membership_evidence_path = (
        _lexical_display_path(verified_fetch.request_plan["output_paths"]["membership_registry"])
        if verified_fetch is not None
        else None
    )
    memberships: list[dict[str, Any]] = []
    if "uniprot-membership" in providers:
        if membership_path is None:
            raise GroundingError("provider uniprot-membership requires --membership-registry")
        if verified_fetch is not None:
            memberships = [
                row
                for row in _membership_rows_from_bytes(
                    verified_fetch.membership_registry_jsonl_bytes,
                    membership_path,
                )
                if row.get("protein_id") in wanted
            ]
        else:
            try:
                from uniprot_membership_snapshot import (
                    MembershipSnapshotError,
                    load_memberships,
                )

                memberships = [
                    row
                    for row in load_memberships(membership_path)
                    if row.get("protein_id") in wanted
                ]
            except MembershipSnapshotError as exc:
                raise GroundingError(f"invalid UniProt membership registry: {exc}") from exc
    sifts_path = args.sifts_registry.resolve() if args.sifts_registry is not None else None
    sifts_mappings: dict[str, dict[str, Any]] = {}
    if "sifts-mapping" in providers:
        if sifts_path is None:
            raise GroundingError("provider sifts-mapping requires --sifts-registry")
        try:
            from build_ecod_sifts_candidates import (
                EcodSiftsError,
                load_mapping_registry,
            )

            sifts_mappings = load_mapping_registry(
                sifts_path,
                allow_offline_fixtures=args.allow_offline_sifts_fixtures,
            )
        except (EcodSiftsError, OSError) as exc:
            raise GroundingError(f"invalid SIFTS mapping registry: {exc}") from exc
    prints_manifest_path: Path | None = None
    prints_manifest: dict[str, Any] | None = None
    prints_release: PrintsRelease | None = None
    if "prints-snapshot" in providers:
        prints_manifest_path = args.prints_manifest.resolve()
        prints_api_path = args.prints_api.resolve()
        prints_kdat_path = args.prints_kdat.resolve()
        prints_hierarchy_path = args.prints_hierarchy.resolve()
        interpro_xml_path = args.interpro_xml.resolve()
        try:
            prints_manifest = verify_prints_manifest(
                prints_manifest_path,
                expected_manifest_id=EXPECTED_PRINTS_SNAPSHOT_ID,
                api_path=prints_api_path,
                kdat_path=prints_kdat_path,
                hierarchy_path=prints_hierarchy_path,
                interpro_xml_path=interpro_xml_path,
            )
            prints_release = parse_prints_kdat(prints_kdat_path, PRINTS_42_0_SHA256)
        except (PrintsSnapshotError, ValueError, OSError) as exc:
            raise GroundingError(f"invalid PRINTS snapshot provider: {exc}") from exc
    return ProviderContext(
        providers=providers,
        residue_path=residue_path,
        residue=residue,
        residue_meta=residue_meta,
        interpro_path=interpro_path,
        interpro=interpro,
        interpro_meta=interpro_meta,
        profiles_path=args.profiles.resolve(),
        profiles=profiles,
        registry_path=registry_path,
        registry_evidence_path=registry_evidence_path,
        registry=registry,
        membership_path=membership_path,
        membership_evidence_path=membership_evidence_path,
        memberships=memberships,
        sifts_path=sifts_path,
        sifts_mappings=sifts_mappings,
        prints_manifest_path=prints_manifest_path,
        prints_manifest=prints_manifest,
        prints_release=prints_release,
        durable_membership_path=args.durable_membership_registry.resolve(),
    )


def _safe_record_path(value: Any, traits_root: Path) -> Path:
    raw = _clean_text(value)
    if not raw:
        raise GroundingError("missing:record_path")
    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = REPO_ROOT / candidate
        if not candidate.exists() and not raw.startswith("data/traits/"):
            candidate = traits_root / raw
    candidate = candidate.resolve()
    root = traits_root.resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise GroundingError(f"invalid:record_path_outside_traits:{raw}") from exc
    if candidate.suffix not in {".yaml", ".yml"}:
        raise GroundingError(f"invalid:record_path_not_yaml:{raw}")
    if not candidate.is_file():
        raise GroundingError(f"missing:record:{raw}")
    return candidate


def _path_is_under(path: Path, root: Path) -> bool:
    resolved_path = path.resolve()
    resolved_root = root.resolve()
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError:
        pass
    else:
        return True

    # APFS is commonly case-insensitive while pathlib's POSIX lexical comparison
    # remains case-sensitive.  Walk toward the nearest existing ancestor and use
    # filesystem identity so DATA/grounding cannot alias data/grounding unnoticed.
    candidate = resolved_path
    while True:
        try:
            if candidate.samefile(resolved_root):
                return True
        except OSError:
            pass
        parent = candidate.parent
        if parent == candidate:
            return False
        candidate = parent


def _physical_path_key(path: Path) -> tuple[Any, ...]:
    """Address an existing path or a not-yet-existing child by physical identity.

    Case-folding only the unresolved tail is conservative on case-sensitive filesystems
    and prevents two staging outputs from colliding on case-insensitive APFS.
    """

    candidate = path.resolve()
    unresolved_tail: list[str] = []
    while True:
        try:
            stat = candidate.stat()
        except OSError:
            parent = candidate.parent
            if parent == candidate:
                return ("unresolved", str(path.resolve()).casefold())
            unresolved_tail.append(unicodedata.normalize("NFC", candidate.name).casefold())
            candidate = parent
            continue
        return (
            "physical",
            stat.st_dev,
            stat.st_ino,
            tuple(reversed(unresolved_tail)),
        )


def _validate_resolve_output_paths(args: argparse.Namespace) -> None:
    """Keep staging ledgers disjoint from source inputs and protected durable data."""

    outputs = {
        "--out": args.out,
        "--review": args.review,
        "--registry-out": args.registry_out,
        "--evidence-out": args.evidence_out,
    }
    resolved_outputs = {name: path.resolve() for name, path in outputs.items()}
    output_keys = {name: _physical_path_key(path) for name, path in outputs.items()}
    if len(set(output_keys.values())) != len(output_keys):
        raise GroundingError("resolve staging outputs must be four distinct paths")

    protected_roots = {
        DEFAULT_TRAITS.resolve(),
        args.traits.resolve(),
        PROTECTED_GROUNDING_ROOT.resolve(),
    }
    input_names = (
        "queue",
        "residue_frame",
        "interpro_frame",
        "profiles",
        "prints_manifest",
        "prints_api",
        "prints_kdat",
        "prints_hierarchy",
        "interpro_xml",
        "pfam_clans",
        "pfam_types",
        "panther_classifications",
        "protein_registry",
        "fetch_receipt",
        "fetch_request_plan",
        "selector_manifest",
        "membership_registry",
        "registry_blocked",
        "sifts_registry",
        "durable_membership_registry",
    )
    protected_input_keys = {
        _physical_path_key(value)
        for name in input_names
        if isinstance((value := getattr(args, name, None)), Path)
    }
    for name, resolved in resolved_outputs.items():
        for root in protected_roots:
            if _path_is_under(resolved, root):
                raise GroundingError(
                    f"{name} staging output must be outside protected trait/grounding data: "
                    f"{outputs[name]}"
                )
        if output_keys[name] in protected_input_keys:
            raise GroundingError(f"{name} staging output aliases a resolver input: {outputs[name]}")


def _record_facts(path: Path, context: ProviderContext) -> tuple[dict, str, str]:
    cached = context.record_cache.get(path)
    if cached:
        return cached
    text = path.read_text(encoding="utf-8")
    try:
        record = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise GroundingError(f"invalid:record_yaml:{path}:{exc}") from exc
    if not isinstance(record, dict):
        raise GroundingError(f"invalid:record_not_mapping:{path}")
    result = record, text, _text_digest(text)
    context.record_cache[path] = result
    return result


def _same_or_reason(supplied: Any, authoritative: Any, field_name: str, reasons: list[str]) -> Any:
    if supplied is not None and authoritative is not None and supplied != authoritative:
        reasons.append(f"mismatch:{field_name}")
    return authoritative if authoritative is not None else supplied


def _sequence_from_sources(
    candidate: dict[str, Any], protein_id: str, context: ProviderContext, reasons: list[str]
) -> tuple[str | None, list[dict[str, Any]], dict | None]:
    accession = _accession(protein_id)
    evidence: list[dict[str, Any]] = []
    registry_row = context.registry.get(protein_id)
    residue_row = context.residue.get(accession or "")
    sequence = _clean_text((registry_row or {}).get("sequence"))
    if sequence is None and isinstance(residue_row, dict):
        sequence = _clean_text(residue_row.get("seq") or residue_row.get("sequence"))
    if sequence is None:
        sequence = _clean_text(candidate.get("sequence"))
    if sequence:
        sequence = "".join(sequence.split()).upper()
        if not _SEQUENCE.fullmatch(sequence):
            reasons.append("invalid:sequence_alphabet")
    else:
        reasons.append("missing:sequence")
    if registry_row:
        projection = dict(registry_row)
        evidence.append(
            _provider_evidence(
                "source_protein_registry",
                context.registry_path or Path("."),
                protein_id,
                projection,
                {"source": "ProteinReference", "release": registry_row.get("uniprot_release")},
                stable_path=context.registry_evidence_path,
            )
        )
    if isinstance(residue_row, dict) and sequence:
        sidecar_sequence = _clean_text(residue_row.get("seq") or residue_row.get("sequence"))
        if sidecar_sequence and "".join(sidecar_sequence.split()).upper() != sequence:
            reasons.append("mismatch:registry_vs_residue_sequence")
        evidence.append(
            _provider_evidence(
                "residue_frame",
                context.residue_path,
                accession or "",
                {"sequence": "".join((sidecar_sequence or "").split()).upper()},
                context.residue_meta,
            )
        )
    elif not registry_row:
        reasons.append("missing:versioned_sequence_provider")
    return sequence, evidence, registry_row


def _build_protein_reference(
    candidate: dict[str, Any], protein_id: str, context: ProviderContext, reasons: list[str]
) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    sequence, evidence, registry_row = _sequence_from_sources(
        candidate, protein_id, context, reasons
    )
    profile = context.profiles.get(protein_id)
    registry_meta = _metadata_projection(registry_row or {})
    profile_meta = _metadata_projection(profile or {})
    candidate_meta = _metadata_projection(candidate)
    if registry_row:
        authoritative = registry_meta
    else:
        # profiles.jsonl has no release header.  It is useful corroboration, but
        # assigning residue_frame's release to its independently fetched name/taxon
        # would manufacture provenance.  A candidate can become QUALIFIED only after
        # these facts come from a release-stamped ProteinReference/API provider.
        authoritative = profile_meta if profile else candidate_meta
        reasons.append("missing:versioned_metadata_provider")
    if profile:
        evidence.append(
            _provider_evidence(
                "profiles",
                context.profiles_path or Path("."),
                protein_id,
                profile_meta,
                {"source": "UniProtKB Swiss-Prot", "release": None},
            )
        )
    protein_label = _same_or_reason(
        candidate_meta["protein_label"], authoritative["protein_label"], "protein_label", reasons
    )
    taxon_id = _same_or_reason(
        candidate_meta["taxon_id"], authoritative["taxon_id"], "taxon_id", reasons
    )
    taxon_label = _same_or_reason(
        candidate_meta["taxon_label"], authoritative["taxon_label"], "taxon_label", reasons
    )
    sequence_length = len(sequence) if sequence else None
    supplied_length = candidate_meta["sequence_length"]
    if supplied_length is not None:
        try:
            supplied_length = int(supplied_length)
        except (TypeError, ValueError):
            reasons.append("invalid:sequence_length")
            supplied_length = None
    authoritative_length = authoritative["sequence_length"]
    if authoritative_length is not None:
        try:
            authoritative_length = int(authoritative_length)
        except (TypeError, ValueError):
            reasons.append("invalid:provider_sequence_length")
            authoritative_length = None
    _same_or_reason(supplied_length, sequence_length, "sequence_length", reasons)
    _same_or_reason(authoritative_length, sequence_length, "provider_sequence_length", reasons)
    reviewed = _same_or_reason(
        candidate_meta["reviewed"], authoritative["reviewed"], "reviewed", reasons
    )
    actual_sha = hashlib.sha256((sequence or "").encode("ascii")).hexdigest() if sequence else None
    supplied_sha = _normalise_sha(candidate.get("sequence_sha256"))
    if supplied_sha and not _SHA256.fullmatch(supplied_sha):
        reasons.append("invalid:sequence_sha256")
    _same_or_reason(supplied_sha, actual_sha, "sequence_sha256", reasons)
    registry_sha = _normalise_sha((registry_row or {}).get("sequence_sha256"))
    _same_or_reason(registry_sha, actual_sha, "registry_sequence_sha256", reasons)
    uniprot_release = _clean_text(
        (registry_row or {}).get("uniprot_release")
        or context.residue_meta.get("release")
        or candidate.get("uniprot_release")
        or candidate.get("sequence_release")
    )
    supplied_release = _clean_text(
        candidate.get("uniprot_release") or candidate.get("sequence_release")
    )
    _same_or_reason(supplied_release, uniprot_release, "uniprot_release", reasons)
    if not uniprot_release:
        reasons.append("missing:uniprot_release")
    sequence_version = (registry_row or {}).get(
        "sequence_version", candidate.get("sequence_version")
    )
    if sequence_version is not None:
        try:
            sequence_version = int(sequence_version)
            if sequence_version < 1:
                raise ValueError
        except (TypeError, ValueError):
            reasons.append("invalid:sequence_version")
            sequence_version = None
    required = {
        "protein_label": protein_label,
        "taxon_id": taxon_id,
        "taxon_label": taxon_label,
        "sequence": sequence,
        "sequence_length": sequence_length,
        "sequence_sha256": actual_sha,
        "reviewed": reviewed,
        "uniprot_release": uniprot_release,
    }
    for key, value in required.items():
        if value is None or value == "":
            reasons.append(f"missing:{key}")
    if taxon_id and not _TAXON.fullmatch(str(taxon_id)):
        reasons.append("invalid:taxon_id")
    if not isinstance(reviewed, bool):
        reasons.append("invalid:reviewed")
    if any(reason.startswith(("missing:", "invalid:", "mismatch:")) for reason in reasons):
        return None, evidence
    match = _UNIPROT.fullmatch(protein_id)
    reference: dict[str, Any] = {
        "protein_id": protein_id,
        "protein_label": protein_label,
        "taxon_id": taxon_id,
        "taxon_label": taxon_label,
        "sequence": sequence,
        "sequence_length": sequence_length,
        "sequence_sha256": actual_sha,
        "reviewed": reviewed,
        "uniprot_release": uniprot_release,
    }
    if match and match.group(2):
        reference["isoform"] = int(match.group(2))
    if sequence_version is not None:
        reference["sequence_version"] = sequence_version
    return reference, evidence


def _whole_protein_allowed(record: dict[str, Any]) -> bool:
    """Mirror the semantic validator's explicit whole-protein category boundary."""

    return record.get("trait_axis") in {"FUNCTION", "EVOLUTION"} or record.get(
        "trait_category"
    ) in {"SEQ_FAMILY", "SEQ_HOMOLOGOUS_SUPERFAMILY"}


def _compress_positions(positions: list[int]) -> list[dict[str, int]]:
    """Return the canonical interval projection without altering residue positions."""

    intervals: list[dict[str, int]] = []
    for position in positions:
        if intervals and position == intervals[-1]["end"] + 1:
            intervals[-1]["end"] = position
        else:
            intervals.append({"start": position, "end": position})
    return intervals


def _sifts_provider_release(mapping: dict[str, Any]) -> str | None:
    entry_date = _clean_text(mapping.get("sifts_entry_date"))
    release = _clean_text(mapping.get("sifts_uniprot_release"))
    if not entry_date or not release:
        return None
    return f"SIFTS {entry_date}; UniProt {release}"


def _resolve_occurrence(
    candidate: dict[str, Any],
    record: dict,
    protein_id: str,
    reference: dict[str, Any] | None,
    context: ProviderContext,
    reasons: list[str],
) -> tuple[
    dict[str, Any] | None,
    dict[str, Any] | None,
    list[dict[str, Any]],
    list[dict[str, int]],
]:
    evidence: list[dict[str, Any]] = []
    trait_id = _clean_text(record.get("identifier"))
    source_trait_id = _clean_text(candidate.get("source_trait_id")) or trait_id
    mapping_method = _clean_text(candidate.get("mapping_method"))
    evidence_source = _clean_text(candidate.get("evidence_source"))
    source_release = _clean_text(candidate.get("source_release"))
    axis = _clean_text(record.get("trait_axis"))
    category = _clean_text(record.get("trait_category"))
    scope = _clean_text(candidate.get("scope"))
    if not scope:
        scope = "WHOLE_PROTEIN" if axis in {"FUNCTION", "EVOLUTION"} else "LOCALIZED"
    if scope not in {"LOCALIZED", "WHOLE_PROTEIN"}:
        reasons.append("invalid:scope")
    if scope == "WHOLE_PROTEIN" and not _whole_protein_allowed(record):
        reasons.append(f"invalid:whole_protein_scope_for_{category or axis}")
    if not mapping_method:
        reasons.append("missing:mapping_method")
    inheritance = candidate.get("inheritance_path")
    if source_trait_id != trait_id:
        valid_path = (
            isinstance(inheritance, list)
            and len(inheritance) >= 2
            and inheritance[0] == source_trait_id
            and inheritance[-1] == trait_id
        )
        if not valid_path:
            reasons.append("mismatch:source_trait_id_without_inheritance_path")
        elif any(
            not isinstance(value, str) or not _CURIE.fullmatch(value) for value in inheritance
        ) or len(inheritance) != len(set(inheritance)):
            reasons.append("invalid:inheritance_path")
    intervals, interval_reasons = _normalise_intervals(candidate.get("intervals"))
    positions, position_reasons = _normalise_positions(candidate.get("residue_positions"))
    reasons.extend(interval_reasons)
    reasons.extend(position_reasons)
    if mapping_method == "INTERPRO_EXACT_MATCH":
        # Compatibility for draft ledgers written before the schema enum settled.
        mapping_method = "INTERPRO_MATCH"
    membership: dict[str, Any] | None = None
    preserved_occurrence: dict[str, Any] | None = None
    preserved_grounding_evidence: dict[str, Any] | None = None
    if mapping_method == "INTERPRO_MATCH":
        if "interpro" not in context.providers:
            reasons.append("missing:interpro_provider")
        accession = _accession(protein_id) or ""
        matches = context.interpro.get(accession)
        raw_source_intervals = matches.get(source_trait_id) if isinstance(matches, dict) else None
        source_intervals, source_interval_reasons = _normalise_intervals(raw_source_intervals)
        reasons.extend(source_interval_reasons)
        if raw_source_intervals is None:
            reasons.append("missing:exact_interpro_match")
        else:
            if intervals and intervals != source_intervals:
                reasons.append("mismatch:interpro_intervals")
            intervals = source_intervals
            evidence.append(
                _provider_evidence(
                    "interpro_frame",
                    context.interpro_path or Path("."),
                    accession,
                    source_intervals,
                    context.interpro_meta,
                    trait_id=source_trait_id,
                )
            )
        provider_release = _clean_text(context.interpro_meta.get("release"))
        if source_release and provider_release and source_release != provider_release:
            reasons.append("mismatch:source_release")
        source_release = provider_release or source_release
        if evidence_source and evidence_source.lower() != "interpro":
            reasons.append("mismatch:evidence_source")
        evidence_source = "InterPro"
    elif mapping_method == "SOURCE_MEMBERSHIP":
        if scope != "WHOLE_PROTEIN":
            reasons.append("invalid:membership_requires_whole_protein")
        if not _whole_protein_allowed(record):
            reasons.append("invalid:whole_protein_membership_not_permitted")
        if source_trait_id != trait_id:
            reasons.append("mismatch:membership_requires_exact_trait_id")
        if "uniprot-membership" not in context.providers:
            reasons.append("missing:uniprot_membership_provider")
        if reference is None:
            reasons.append("missing:protein_reference_for_membership")
        elif "uniprot-membership" in context.providers:
            try:
                from uniprot_membership_snapshot import (
                    MembershipSnapshotError,
                    find_exact_membership,
                    membership_entry_sha256,
                )

                membership = find_exact_membership(
                    context.memberships,
                    protein_id=protein_id,
                    source_trait_id=str(source_trait_id or ""),
                    uniprot_release=reference["uniprot_release"],
                    sequence_sha256=reference["sequence_sha256"],
                )
            except MembershipSnapshotError as exc:
                reasons.append(f"ambiguous:uniprot_membership:{exc}")
            if membership is None:
                reasons.append("missing:exact_uniprot_membership")
            else:
                provider_release = membership["uniprot_release"]
                # The producer's source_release may describe the earlier discovery
                # search.  The exact-accession snapshot is self-contained and bound to
                # the selected ProteinReference release/checksum, so it replaces (and
                # must not be vetoed by) that discovery metadata.
                source_release = provider_release
                if evidence_source and evidence_source != "UniProtKB":
                    reasons.append("mismatch:evidence_source")
                evidence_source = "UniProtKB"
                membership_evidence = _provider_evidence(
                    "uniprot_membership",
                    context.membership_path or Path("."),
                    membership["membership_id"],
                    membership,
                    {"source": "UniProtKB", "release": provider_release},
                    trait_id=source_trait_id,
                    stable_path=context.membership_evidence_path,
                )
                membership_evidence["entry_sha256"] = membership_entry_sha256(membership)
                evidence.append(membership_evidence)
    elif mapping_method == "SIFTS_RESIDUE_MAPPING":
        branch_reason_count = len(reasons)
        if "sifts-mapping" not in context.providers:
            reasons.append("missing:sifts_mapping_provider")
        if reference is None:
            reasons.append("missing:protein_reference_for_sifts")
        registry_reference = context.registry.get(protein_id)
        if registry_reference is None:
            reasons.append("missing:exact_protein_reference_for_sifts")
        elif reference is not None and registry_reference != reference:
            reasons.append("mismatch:exact_protein_reference_for_sifts")
        mapping_id = _clean_text(candidate.get("sifts_mapping_id"))
        if not mapping_id:
            reasons.append("missing:sifts_mapping_id")
        mapping = context.sifts_mappings.get(mapping_id or "")
        if mapping is None:
            reasons.append("missing:exact_sifts_mapping")
        else:
            from build_ecod_sifts_candidates import mapping_entry_sha256

            entry_sha = mapping_entry_sha256(mapping)
            expected_mapping_id = f"ecod-sifts:{entry_sha}"
            if (
                mapping_id != expected_mapping_id
                or mapping.get("mapping_id") != expected_mapping_id
            ):
                reasons.append("mismatch:sifts_mapping_content_address")
            expected_pairs = {
                "trait_id": trait_id,
                "protein_id": protein_id,
                "sequence_sha256": (reference or {}).get("sequence_sha256"),
                "uniprot_release": (reference or {}).get("uniprot_release"),
            }
            for field_name, expected_value in expected_pairs.items():
                if mapping.get(field_name) != expected_value:
                    reasons.append(f"mismatch:sifts_mapping_{field_name}")
            if mapping.get("sifts_uniprot_release") != (reference or {}).get("uniprot_release"):
                reasons.append("mismatch:sifts_mapping_release")
            structure_id = _clean_text(mapping.get("structure_id"))
            chain_id = _clean_text(mapping.get("chain_id"))
            if not structure_id or not structure_id.upper().startswith("PDB:"):
                reasons.append("invalid:sifts_structure_id")
            if not chain_id:
                reasons.append("missing:sifts_chain_id")
            elif chain_id != mapping.get("ecod_chain"):
                reasons.append("mismatch:sifts_mapping_chain")
            mapped_residues = mapping.get("mapped_residues")
            mapped_by_position: dict[int, str] = {}
            if not isinstance(mapped_residues, list) or not mapped_residues:
                reasons.append("invalid:sifts_mapped_residues")
                mapped_residues = []
            sequence = str((reference or {}).get("sequence") or "")
            for number, mapped in enumerate(mapped_residues, 1):
                if not isinstance(mapped, dict):
                    reasons.append(f"invalid:sifts_mapped_residue_{number}")
                    continue
                position = mapped.get("uniprot_position")
                amino_acid = mapped.get("uniprot_amino_acid")
                pdb_amino_acid = mapped.get("pdb_amino_acid")
                pdbe_position = mapped.get("pdbe_sequence_position")
                author_number = mapped.get("author_residue_number")
                insertion_code = mapped.get("author_insertion_code")
                if (author_number is None) != (insertion_code is None):
                    reasons.append(f"invalid:sifts_author_position_{number}")
                    continue
                if author_number is not None and (
                    isinstance(author_number, bool)
                    or not isinstance(author_number, int)
                    or not isinstance(insertion_code, str)
                ):
                    reasons.append(f"invalid:sifts_author_position_{number}")
                    continue
                if (
                    isinstance(position, bool)
                    or not isinstance(position, int)
                    or position < 1
                    or position > len(sequence)
                ):
                    reasons.append(f"invalid:sifts_uniprot_position_{number}")
                    continue
                if position in mapped_by_position:
                    reasons.append("ambiguous:sifts_duplicate_uniprot_position")
                    continue
                if (
                    not isinstance(amino_acid, str)
                    or len(amino_acid) != 1
                    or amino_acid != sequence[position - 1]
                ):
                    reasons.append(f"mismatch:sifts_uniprot_residue_{number}")
                    continue
                if pdb_amino_acid != amino_acid:
                    reasons.append(f"mismatch:sifts_pdb_residue_{number}")
                    continue
                if (
                    isinstance(pdbe_position, bool)
                    or not isinstance(pdbe_position, int)
                    or pdbe_position < 1
                ):
                    reasons.append(f"invalid:sifts_pdbe_position_{number}")
                    continue
                if mapped.get("chain_id") != chain_id:
                    reasons.append(f"mismatch:sifts_residue_chain_{number}")
                    continue
                mapped_by_position[position] = amino_acid
            mapped_positions = sorted(mapped_by_position)
            mapped_expected = "".join(mapped_by_position[position] for position in mapped_positions)
            mapped_intervals = _compress_positions(mapped_positions)
            provider_release = _sifts_provider_release(mapping)
            if provider_release is None:
                reasons.append("missing:sifts_provider_release")
            authoritative_source_release = _clean_text(mapping.get("ecod_release"))
            if not authoritative_source_release:
                reasons.append("missing:sifts_source_release")
            expected_occurrence: dict[str, Any] = {
                "trait_id": trait_id,
                "protein_id": protein_id,
                "scope": "LOCALIZED",
                "coordinate_frame": (
                    "UNIPROT_ISOFORM"
                    if _UNIPROT.fullmatch(protein_id).group(2)
                    else "UNIPROT_CANONICAL"
                ),
                "residue_positions": mapped_positions,
                "expected_residues": mapped_expected,
                "source_trait_id": trait_id,
                "mapping_method": "SIFTS_RESIDUE_MAPPING",
                "evidence_source": "ECOD via PDBe SIFTS",
                "source_release": authoritative_source_release,
                "sequence_sha256": (reference or {}).get("sequence_sha256"),
                "structure_id": structure_id,
                "chain_id": chain_id,
                "mapping_completeness": "COMPLETE",
                "source_residue_count": len(mapped_residues),
                "mapped_residue_count": len(mapped_residues),
                "qualification_status": "QUALIFIED",
            }
            flat_projection = {
                "scope": expected_occurrence["scope"],
                "coordinate_frame": expected_occurrence["coordinate_frame"],
                "intervals": mapped_intervals,
                "residue_positions": mapped_positions,
                "expected_residues": mapped_expected,
                "source_trait_id": expected_occurrence["source_trait_id"],
                "evidence_source": expected_occurrence["evidence_source"],
                "source_release": expected_occurrence["source_release"],
                "mapping_completeness": expected_occurrence["mapping_completeness"],
                "source_residue_count": expected_occurrence["source_residue_count"],
                "mapped_residue_count": expected_occurrence["mapped_residue_count"],
                "structure_id": structure_id,
                "chain_id": chain_id,
            }
            for field_name, expected_value in flat_projection.items():
                if candidate.get(field_name) != expected_value:
                    reasons.append(f"mismatch:sifts_candidate_{field_name}")
            if candidate.get("evidence_tier") != "B":
                reasons.append("mismatch:sifts_candidate_evidence_tier")
            if candidate.get("sifts_release") != provider_release:
                reasons.append("mismatch:sifts_candidate_provider_release")
            expected_candidate_provider_evidence = [
                {
                    "kind": "sifts_mapping",
                    "path": _display_path(context.sifts_path or Path(".")),
                    "key": mapping_id,
                    "source": "PDBe SIFTS",
                    "release": provider_release,
                    "entry_sha256": entry_sha,
                    "trait_id": trait_id,
                }
            ]
            if candidate.get("provider_evidence") != expected_candidate_provider_evidence:
                reasons.append("mismatch:sifts_candidate_provider_evidence")
            if (
                provider_release
                and authoritative_source_release
                and len(reasons) == branch_reason_count
            ):
                from validate_uniprot_grounding import (
                    build_grounding_evidence,
                    validate_grounding_evidence,
                )

                expected_evidence = build_grounding_evidence(
                    expected_occurrence,
                    provider_kind="SIFTS",
                    provider_source=_display_path(context.sifts_path or Path(".")),
                    provider_release=provider_release,
                    provider_entry_sha256=entry_sha,
                )
                expected_occurrence["source_evidence_id"] = expected_evidence["evidence_id"]
                expected_candidate_occurrence = {
                    **expected_occurrence,
                    "qualification_status": "LOCATION_VERIFIED",
                }
                evidence_findings = validate_grounding_evidence(
                    expected_evidence,
                    path=context.sifts_path or Path("."),
                    line=0,
                )
                if evidence_findings:
                    reasons.extend(
                        f"invalid:sifts_grounding_evidence:{finding.code}"
                        for finding in evidence_findings
                    )
                if candidate.get("trait_occurrence") != expected_candidate_occurrence:
                    reasons.append("mismatch:sifts_trait_occurrence_projection")
                if candidate.get("grounding_evidence") != expected_evidence:
                    reasons.append("mismatch:sifts_grounding_evidence_projection")
                if len(reasons) == branch_reason_count:
                    preserved_occurrence = copy.deepcopy(expected_occurrence)
                    preserved_grounding_evidence = copy.deepcopy(expected_evidence)
            mapping_evidence = _provider_evidence(
                "sifts_mapping",
                context.sifts_path or Path("."),
                str(mapping_id or ""),
                mapping,
                {"source": "PDBe SIFTS", "release": provider_release},
                trait_id=trait_id,
            )
            mapping_evidence["entry_sha256"] = entry_sha
            evidence.append(mapping_evidence)
            source_trait_id = trait_id
            evidence_source = "ECOD via PDBe SIFTS"
            source_release = authoritative_source_release
            scope = "LOCALIZED"
            intervals = copy.deepcopy(mapped_intervals)
            positions = copy.deepcopy(mapped_positions)
    else:
        reasons.append(f"unsupported:mapping_method:{mapping_method or 'NONE'}")
    if not evidence_source:
        reasons.append("missing:evidence_source")
    if not source_release:
        reasons.append("missing:source_release")
    evidence_tier = _clean_text(candidate.get("evidence_tier"))
    if mapping_method in {"INTERPRO_MATCH", "SOURCE_MEMBERSHIP"} and not evidence_tier:
        evidence_tier = "A"
    if evidence_tier not in {"A", "B"}:
        reasons.append(f"unqualifiable:evidence_tier:{evidence_tier or 'NONE'}")
    coordinate_frame = _clean_text(candidate.get("coordinate_frame"))
    if scope == "LOCALIZED":
        if not coordinate_frame:
            coordinate_frame = (
                "UNIPROT_ISOFORM"
                if _UNIPROT.fullmatch(protein_id).group(2)
                else "UNIPROT_CANONICAL"
            )
        expected_frame = (
            "UNIPROT_ISOFORM" if _UNIPROT.fullmatch(protein_id).group(2) else "UNIPROT_CANONICAL"
        )
        if coordinate_frame != expected_frame:
            reasons.append("mismatch:coordinate_frame")
        if not intervals and not positions:
            reasons.append("missing:localized_coordinates")
        # interpro_frame.json preserves the set of flattened ranges for an entry/protein,
        # but not the hit/location grouping from the InterPro API.  More than one range
        # can therefore mean a discontinuous occurrence, repeated independent hits, or a
        # PRINTS-style fingerprint.  Treating that list as one occurrence would invent a
        # biological assertion.  A richer provider must group it before qualification.
        if mapping_method == "INTERPRO_MATCH" and len(intervals) > 1:
            reasons.append("ambiguous:ungrouped_interpro_locations")
    else:
        if coordinate_frame is not None:
            reasons.append("invalid:whole_protein_coordinate_frame")
        if mapping_method == "SOURCE_MEMBERSHIP" and intervals:
            reasons.append("invalid:membership_coordinates")
        if positions:
            reasons.append("invalid:whole_protein_residue_positions")
        if candidate.get("expected_residues") is not None:
            reasons.append("invalid:whole_protein_expected_residues")
        coordinate_frame = None
    length = (reference or {}).get("sequence_length")
    sequence = (reference or {}).get("sequence") or ""
    for interval in intervals:
        if interval["start"] < 1 or interval["end"] < interval["start"]:
            reasons.append("invalid:interval_order")
        elif length and interval["end"] > length:
            reasons.append("invalid:interval_out_of_bounds")
    for position in positions:
        if position < 1 or (length and position > length):
            reasons.append("invalid:residue_position_out_of_bounds")
    expected_residues = _clean_text(candidate.get("expected_residues"))
    if expected_residues:
        expected_residues = expected_residues.upper()
        if len(expected_residues) != len(positions):
            reasons.append("mismatch:expected_residue_count")
        elif sequence and any(
            sequence[pos - 1] != aa for pos, aa in zip(positions, expected_residues)
        ):
            reasons.append("mismatch:expected_residues")
    if any(
        reason.startswith(
            ("missing:", "invalid:", "mismatch:", "unsupported:", "unqualifiable:", "ambiguous:")
        )
        for reason in reasons
    ):
        return None, None, evidence, intervals
    if mapping_method == "SIFTS_RESIDUE_MAPPING":
        if preserved_occurrence is None or preserved_grounding_evidence is None:
            reasons.append("missing:verified_sifts_projection")
            return None, None, evidence, intervals
        return preserved_occurrence, preserved_grounding_evidence, evidence, intervals
    occurrence: dict[str, Any] = {
        "trait_id": trait_id,
        "protein_id": protein_id,
        "scope": scope,
        "source_trait_id": source_trait_id,
        "mapping_method": mapping_method,
        "evidence_source": evidence_source,
        "source_release": source_release,
        "sequence_sha256": reference["sequence_sha256"],
        "qualification_status": "QUALIFIED",
    }
    if source_trait_id != trait_id and isinstance(inheritance, list):
        occurrence["inheritance_path"] = inheritance
    if scope == "LOCALIZED":
        occurrence["coordinate_frame"] = coordinate_frame
        if intervals:
            occurrence["intervals"] = intervals
        if positions:
            occurrence["residue_positions"] = positions
        if expected_residues:
            occurrence["expected_residues"] = expected_residues
    for key in (
        "mapping_completeness",
        "source_residue_count",
        "mapped_residue_count",
        "structure_id",
        "chain_id",
    ):
        if candidate.get(key) is not None:
            occurrence[key] = candidate[key]
    source_kind = (
        "uniprot_membership" if mapping_method == "SOURCE_MEMBERSHIP" else "interpro_frame"
    )
    source_evidence = next((item for item in evidence if item.get("kind") == source_kind), None)
    if source_evidence is None:
        reasons.append("missing:source_provider_evidence")
        return None, None, evidence, intervals
    from validate_uniprot_grounding import (
        build_grounding_evidence,
        validate_grounding_evidence,
    )

    provider_kind = "UNIPROT" if mapping_method == "SOURCE_MEMBERSHIP" else "INTERPRO"
    provider_source = (
        _display_path(context.durable_membership_path)
        if mapping_method == "SOURCE_MEMBERSHIP"
        else str(source_evidence.get("source") or "InterPro")
    )
    grounding_evidence = build_grounding_evidence(
        occurrence,
        provider_kind=provider_kind,
        provider_source=provider_source,
        provider_release=str(source_evidence.get("release") or source_release),
        provider_entry_sha256=str(source_evidence.get("entry_sha256") or ""),
    )
    evidence_findings = validate_grounding_evidence(
        grounding_evidence,
        path=Path(str(source_evidence.get("path") or ".")),
        line=0,
    )
    if evidence_findings:
        reasons.extend(
            f"invalid:grounding_evidence:{finding.code}" for finding in evidence_findings
        )
        return None, None, evidence, intervals
    occurrence["source_evidence_id"] = grounding_evidence["evidence_id"]
    return occurrence, grounding_evidence, evidence, intervals


def _resolve_candidate(
    candidate: dict[str, Any], context: ProviderContext, traits_root: Path
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    row = dict(candidate)
    row.pop("resolution_digest", None)
    # Embedded claims from producers are inputs to provider-specific verification,
    # never trusted resolved output.  Only a successfully verified projection is
    # installed again below.
    producer_occurrence = row.pop("trait_occurrence", None)
    producer_grounding_evidence = row.pop("grounding_evidence", None)
    original_candidate_id = _clean_text(row.get("candidate_id"))
    producer_reasons = row.pop("reasons", None)
    reasons: list[str] = []
    if producer_reasons is not None:
        if not isinstance(producer_reasons, list) or any(
            not isinstance(reason, str) or not reason.strip() for reason in producer_reasons
        ):
            reasons.append("invalid:producer_reasons")
        else:
            # Producer reasons are promotion blockers, not commentary.  Dropping them
            # would let `resolve` without the intended queue boundary reconsider an
            # explicitly blocked lossy/mismatched candidate.
            for reason in producer_reasons:
                normalized_reason = reason.strip()
                if (
                    candidate.get("mapping_method") == "SOURCE_MEMBERSHIP"
                    and normalized_reason in _MEMBERSHIP_RESOLUTION_REASONS
                ):
                    # These two discovery-state reasons are discharged only by the
                    # exact release/checksum/membership checks below. Every other
                    # producer reason remains a promotion blocker.
                    continue
                reasons.append(f"producer:{normalized_reason}")
    trait_id = _clean_text(row.get("trait_id"))
    protein_id = _clean_text(row.get("protein_id"))
    record: dict = {}
    record_path: Path | None = None
    record_sha: str | None = None
    if not trait_id or not _CURIE.fullmatch(trait_id):
        reasons.append("missing_or_invalid:trait_id")
    if not protein_id or not _UNIPROT.fullmatch(protein_id):
        reasons.append("missing_or_invalid:protein_id")
    try:
        record_path = _safe_record_path(row.get("record_path"), traits_root)
        record, _, record_sha = _record_facts(record_path, context)
        authoritative_id = _clean_text(record.get("identifier"))
        if trait_id and authoritative_id != trait_id:
            reasons.append("mismatch:record_identifier")
        trait_id = authoritative_id or trait_id
        for field_name in ("trait_axis", "trait_category"):
            supplied = _clean_text(row.get(field_name))
            authoritative = _clean_text(record.get(field_name))
            if supplied and authoritative and supplied != authoritative:
                reasons.append(f"mismatch:{field_name}")
            row[field_name] = authoritative or supplied
    except GroundingError as exc:
        reasons.append(str(exc))
    content_findings = []
    if record and context.content_gate is not None:
        try:
            content_findings = context.content_gate.evaluate(record)
        except ContentGateError as exc:
            raise GroundingError(
                f"{trait_id or row.get('record_path')}: record-content source replay "
                f"failed closed: {exc}"
            ) from exc
        reasons.extend(record_content_hard_reasons(content_findings))
    row["record_content_findings"] = [finding.as_dict() for finding in content_findings]
    reference: dict[str, Any] | None = None
    provider_evidence: list[dict[str, Any]] = []
    occurrence: dict[str, Any] | None = None
    grounding_evidence: dict[str, Any] | None = None
    if protein_id and _UNIPROT.fullmatch(protein_id):
        reference, sequence_evidence = _build_protein_reference(row, protein_id, context, reasons)
        provider_evidence.extend(sequence_evidence)
    if record and protein_id and _UNIPROT.fullmatch(protein_id):
        occurrence_candidate = row
        if producer_occurrence is not None or producer_grounding_evidence is not None:
            occurrence_candidate = {
                **row,
                "trait_occurrence": producer_occurrence,
                "grounding_evidence": producer_grounding_evidence,
            }
        (
            occurrence,
            grounding_evidence,
            occurrence_evidence,
            ledger_intervals,
        ) = _resolve_occurrence(
            occurrence_candidate, record, protein_id, reference, context, reasons
        )
        provider_evidence.extend(occurrence_evidence)
    else:
        ledger_intervals = []
    if record_path:
        row["record_path"] = _display_path(record_path)
    row["trait_id"] = trait_id
    row["protein_id"] = protein_id
    if record_sha:
        row["record_sha256"] = record_sha
    if reference:
        for key in (
            "protein_label",
            "taxon_id",
            "taxon_label",
            "sequence_length",
            "sequence_sha256",
            "reviewed",
            "uniprot_release",
            "sequence_version",
        ):
            if key in reference:
                row[key] = reference[key]
        row.pop("sequence_release", None)
        row["protein_reference_sha256"] = _value_digest(reference)
    if occurrence:
        row["scope"] = occurrence["scope"]
        row["source_trait_id"] = occurrence["source_trait_id"]
        row["mapping_method"] = occurrence["mapping_method"]
        row["evidence_source"] = occurrence["evidence_source"]
        row["source_release"] = occurrence["source_release"]
        row["coordinate_frame"] = occurrence.get("coordinate_frame")
        # A WHOLE_PROTEIN family assertion is not localized.  Keep the real HMM
        # footprint in the review ledger/candidate identity, but do not turn it into a
        # fabricated whole-protein TraitOccurrence interval.
        row["intervals"] = ledger_intervals
        row["residue_positions"] = occurrence.get("residue_positions", [])
        row["evidence_tier"] = row.get("evidence_tier") or "A"
        row["trait_occurrence"] = occurrence
        row["grounding_evidence"] = grounding_evidence
    if (
        record
        and context.content_gate is not None
        and reference is not None
        and occurrence is not None
    ):
        try:
            content_findings.extend(context.content_gate.evaluate_candidate(record, row))
        except ContentGateError as exc:
            raise GroundingError(
                f"{trait_id or row.get('record_path')}: record-content source replay "
                f"failed closed: {exc}"
            ) from exc
    row["record_content_findings"] = [finding.as_dict() for finding in content_findings]
    if _is_sfld_grounding(row, record, occurrence, grounding_evidence):
        # SFLD v3/v4 hierarchy rows currently conflate source levels and labels.
        # Provider evidence may still be replayed for review diagnostics, but no SFLD
        # candidate can cross the machine-qualification boundary until that source
        # model is repaired and regression-validated.
        reasons.append(_SFLD_SOURCE_MODEL_REPAIR_REASON)
    if _is_prints_grounding(row, record, occurrence, grounding_evidence):
        diagnostic, diagnostic_evidence, diagnostic_reasons = _prints_interval_shape_diagnostic(
            row,
            record,
            ledger_intervals,
            context,
        )
        if diagnostic is not None:
            row["prints_interval_shape_diagnostic"] = diagnostic
        provider_evidence.extend(diagnostic_evidence)
        reasons.extend(diagnostic_reasons)
        # A PRINTS hit is an ordered, multi-motif fingerprint, not an anonymous
        # collection of provider intervals.  Until motif identities, occurrence
        # grouping, and a pinned matcher replay are durable resolution inputs, even a
        # model-compatible interval shape cannot qualify a PRINTS exemplar.
        reasons.append(_PRINTS_FINGERPRINT_MODEL_REPLAY_REASON)
    row["provider_evidence"] = sorted(
        provider_evidence,
        key=lambda item: (item["kind"], item["path"], item["key"], item.get("trait_id", "")),
    )
    row["qualification_status"] = (
        "QUALIFIED" if reference and occurrence and not reasons else "REJECTED"
    )
    row["candidate_status"] = row["qualification_status"]
    row["reasons"] = sorted(set(reasons))
    # Producer IDs identify ledger rows, including deliberately incomplete discovery
    # rows.  Enrichment may change every evidence field, so approval freshness is bound
    # to resolution_digest rather than by silently changing the producer's key.
    row["candidate_id"] = original_candidate_id or derive_candidate_id(row)
    return row, reference if row["qualification_status"] == "QUALIFIED" else None


def _review_flags(row: dict[str, Any]) -> list[str]:
    """Return deterministic flags whose cases the review protocol samples exhaustively."""

    flags: list[str] = []
    protein_id = _clean_text(row.get("protein_id")) or ""
    match = _UNIPROT.fullmatch(protein_id)
    if match and match.group(2):
        flags.append("ISOFORM")
    intervals, _ = _normalise_intervals(row.get("intervals"))
    if len(intervals) > 1:
        flags.append("MULTI_INTERVAL_OR_HIT")
    positions, _ = _normalise_positions(row.get("residue_positions"))
    if positions:
        flags.append("DISCONTINUOUS_RESIDUE_SET")
    if row.get("source_trait_id") != row.get("trait_id") or row.get("inheritance_path"):
        flags.append("ANCESTOR_INHERITANCE")
    if row.get("mapping_method") == "SIFTS_RESIDUE_MAPPING":
        flags.append("SIFTS")
    if row.get("mapping_completeness") == "PARTIAL":
        flags.append("PARTIAL_SIFTS")
    if row.get("candidate_state") == "AMBIGUOUS_LOCAL_EXACT_CANDIDATES":
        flags.append("MULTI_CANDIDATE")
    for finding in row.get("record_content_findings") or []:
        if (
            isinstance(finding, dict)
            and finding.get("severity") == "REVIEW"
            and _clean_text(finding.get("code"))
        ):
            flags.append(f"RECORD_CONTENT:{finding['code']}")
    return sorted(set(flags))


def _select_batch(candidates: list[dict], batch: str | None) -> list[dict]:
    if not batch:
        return candidates
    selected: list[dict] = []
    for row in candidates:
        value = _clean_text(row.get("batch") or row.get("batch_id"))
        if value == batch:
            selected.append(row)
    return selected


def _registry_projection(reference: dict[str, Any]) -> dict[str, Any]:
    return {key: reference[key] for key in sorted(reference)}


def _assert_exact_staging_projection(
    resolved: list[dict[str, Any]],
    registry: dict[str, dict[str, Any]],
    evidence_registry: dict[str, dict[str, Any]],
) -> None:
    """Require replace-mode staging outputs to equal the final qualified projection."""

    qualified = [row for row in resolved if row.get("qualification_status") == "QUALIFIED"]
    expected_protein_ids = {
        str(row.get("protein_id") or "") for row in qualified if row.get("protein_id")
    }
    expected_evidence: dict[str, dict[str, Any]] = {}
    for row in qualified:
        candidate_id = str(row.get("candidate_id") or "")
        embedded = row.get("grounding_evidence")
        if not isinstance(embedded, dict):
            raise GroundingError(
                f"{candidate_id}: exact staging projection lacks embedded GroundingEvidence"
            )
        evidence_id = _clean_text(embedded.get("evidence_id"))
        if not evidence_id:
            raise GroundingError(f"{candidate_id}: exact staging projection lacks evidence_id")
        previous = expected_evidence.get(evidence_id)
        if previous is not None and previous != embedded:
            raise GroundingError(
                f"{candidate_id}: conflicting exact staging evidence {evidence_id}"
            )
        expected_evidence[evidence_id] = embedded

    if set(registry) != expected_protein_ids:
        missing = sorted(expected_protein_ids - set(registry))
        extra = sorted(set(registry) - expected_protein_ids)
        raise GroundingError(
            "exact staging ProteinReference projection mismatch; "
            f"missing={missing[:5]}, extra={extra[:5]}"
        )
    if set(evidence_registry) != set(expected_evidence):
        missing = sorted(set(expected_evidence) - set(evidence_registry))
        extra = sorted(set(evidence_registry) - set(expected_evidence))
        raise GroundingError(
            "exact staging GroundingEvidence projection mismatch; "
            f"missing={missing[:5]}, extra={extra[:5]}"
        )

    for evidence_id, expected in expected_evidence.items():
        evidence = evidence_registry[evidence_id]
        if evidence != expected:
            raise GroundingError(
                f"exact staging GroundingEvidence differs from resolved row: {evidence_id}"
            )
        protein_id = _clean_text(evidence.get("protein_id")) or ""
        reference = registry.get(protein_id)
        if reference is None:
            raise GroundingError(
                f"exact staging evidence {evidence_id} lacks ProteinReference {protein_id!r}"
            )
        if evidence.get("sequence_sha256") != reference.get("sequence_sha256"):
            raise GroundingError(
                f"exact staging evidence {evidence_id} has ProteinReference sequence mismatch"
            )


def resolve(args: argparse.Namespace) -> int:
    _validate_resolve_output_paths(args)
    verified_fetch = _verify_resolve_fetch_boundary(args)
    if args.replace_staging_outputs and args.limit is not None:
        raise GroundingError("--replace-staging-outputs cannot be combined with --limit")
    candidate_rows = (
        _read_verified_jsonl(verified_fetch.candidate_jsonl_bytes, source=args.queue)
        if verified_fetch is not None
        else _read_jsonl(args.queue)
    )
    candidates = _select_batch(candidate_rows, args.batch)
    if args.limit is not None:
        if args.limit < 1:
            raise GroundingError("--limit must be positive")
        candidates = candidates[: args.limit]
    context = _provider_context(args, candidates, verified_fetch=verified_fetch)
    traits_root = args.traits.resolve()
    gate_records: dict[Path, dict[str, Any]] = {}
    for candidate in candidates:
        try:
            path = _safe_record_path(candidate.get("record_path"), traits_root)
            gate_records[path] = _record_facts(path, context)[0]
        except GroundingError:
            # The normal candidate resolver records invalid/missing paths as stable
            # rejection reasons.  They cannot request a source-aware content check.
            continue
    context.content_gate = _prepare_content_gate(gate_records.values(), args)
    resolved: list[dict[str, Any]] = []
    fresh_references: dict[str, dict[str, Any]] = {}
    for candidate in candidates:
        row, reference = _resolve_candidate(candidate, context, traits_root)
        resolved.append(row)
        if reference:
            protein_id = reference["protein_id"]
            previous = fresh_references.get(protein_id)
            if previous is not None and previous != reference:
                row["qualification_status"] = "REJECTED"
                row["candidate_status"] = "REJECTED"
                row["reasons"] = sorted(row["reasons"] + ["mismatch:protein_reference_in_batch"])
            else:
                fresh_references[protein_id] = reference
    duplicate_ids = sorted(
        candidate_id
        for candidate_id, count in Counter(row["candidate_id"] for row in resolved).items()
        if count > 1
    )
    if duplicate_ids:
        raise GroundingError(
            "candidate ledger contains duplicate candidate_id values: "
            + ", ".join(duplicate_ids[:5])
        )
    existing_registry = (
        {} if args.replace_staging_outputs else _load_object_or_jsonl(args.registry_out)
    )
    existing_registry.update(fresh_references)
    registry_rows = [
        _registry_projection(existing_registry[key]) for key in sorted(existing_registry)
    ]
    registry_path = args.registry_out.resolve()
    registry_evidence_by_id = {
        reference["protein_id"]: _provider_evidence(
            "protein_registry",
            registry_path,
            reference["protein_id"],
            reference,
            {"source": "UniProt", "release": reference.get("uniprot_release")},
        )
        for reference in registry_rows
    }
    from validate_uniprot_grounding import load_evidence_registry

    evidence_by_id: dict[str, dict[str, Any]] = {}
    if not args.replace_staging_outputs and args.evidence_out.is_file():
        evidence_by_id, evidence_findings = load_evidence_registry(args.evidence_out)
        if evidence_findings:
            detail = "; ".join(
                f"{finding.code}: {finding.message}" for finding in evidence_findings[:3]
            )
            raise GroundingError(f"existing evidence registry is invalid: {detail}")
    for row in resolved:
        if row["qualification_status"] == "QUALIFIED":
            row["provider_evidence"].append(registry_evidence_by_id[row["protein_id"]])
            row["provider_evidence"] = sorted(
                row["provider_evidence"],
                key=lambda item: (
                    item["kind"],
                    item["path"],
                    item["key"],
                    item.get("trait_id", ""),
                ),
            )
            grounding_evidence = row.get("grounding_evidence")
            if not isinstance(grounding_evidence, dict):
                raise GroundingError(
                    f"{row['candidate_id']}: qualified row lacks grounding_evidence"
                )
            evidence_id = str(grounding_evidence.get("evidence_id") or "")
            previous = evidence_by_id.get(evidence_id)
            if previous is not None and previous != grounding_evidence:
                raise GroundingError(f"conflicting grounding evidence for {evidence_id}")
            evidence_by_id[evidence_id] = grounding_evidence
        row["resolution_digest"] = _resolution_digest(row)
    if args.replace_staging_outputs:
        _assert_exact_staging_projection(resolved, existing_registry, evidence_by_id)
    resolved.sort(
        key=lambda row: (
            row.get("trait_id") or "",
            row.get("protein_id") or "",
            row["candidate_id"],
        )
    )
    if verified_fetch is not None:
        rechecked_fetch = _verify_resolve_fetch_boundary(args)
        if rechecked_fetch != verified_fetch:
            raise GroundingError("verified UniProt fetch generation changed during resolution")
    _write_jsonl(args.registry_out, registry_rows)
    _write_jsonl(args.evidence_out, [evidence_by_id[key] for key in sorted(evidence_by_id)])
    _write_jsonl(args.out, resolved)
    review_rows = []
    for row in resolved:
        review_rows.append(
            {
                "candidate_id": row["candidate_id"],
                "resolution_digest": row["resolution_digest"],
                "decision": "",
                "qualification_status": row["qualification_status"],
                "trait_id": row.get("trait_id") or "",
                "protein_id": row.get("protein_id") or "",
                "record_path": row.get("record_path") or "",
                "source_namespace": row.get("source_namespace")
                or str(row.get("trait_id") or "").split(":", 1)[0],
                "trait_axis": row.get("trait_axis") or "",
                "trait_category": row.get("trait_category") or "",
                "scope": row.get("scope") or "",
                "evidence_tier": row.get("evidence_tier") or "",
                "mapping_method": row.get("mapping_method") or "",
                "evidence_source": row.get("evidence_source") or "",
                "source_release": row.get("source_release") or "",
                "uniprot_release": row.get("uniprot_release") or "",
                "intervals": _canonical_json(row.get("intervals") or []),
                "review_flags": ";".join(_review_flags(row)),
                "reasons": ";".join(row.get("reasons") or []),
                "reviewer": "",
                "reviewed_at": "",
                "review_notes": "",
            }
        )
    lines: list[str] = []
    from io import StringIO

    buffer = StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=_REVIEW_COLUMNS, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(review_rows)
    lines.append(buffer.getvalue())
    _atomic_text(args.review, "".join(lines))
    counts = Counter(row["qualification_status"] for row in resolved)
    print(
        f"resolved {len(resolved):,} candidate(s): "
        f"{counts['QUALIFIED']:,} QUALIFIED, {counts['REJECTED']:,} REJECTED"
    )
    print(f"WROTE {_display_path(args.out)}")
    print(f"WROTE {_display_path(args.review)}")
    print(f"WROTE {_display_path(args.registry_out)} ({len(registry_rows):,} proteins)")
    print(
        f"WROTE {_display_path(args.evidence_out)} ({len(evidence_by_id):,} source-evidence rows)"
    )
    return 1 if args.fail_on_rejected and counts["REJECTED"] else 0


def _read_approvals(path: Path) -> dict[str, dict[str, str]]:
    if not path.is_file():
        raise GroundingError(f"explicit approval TSV does not exist: {path}")
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        required = {
            "candidate_id",
            "resolution_digest",
            "decision",
            "reviewer",
            "reviewed_at",
            "review_notes",
        }
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise GroundingError(
                f"approval TSV must contain columns: {', '.join(sorted(required))}"
            )
        out: dict[str, dict[str, str]] = {}
        for line_number, row in enumerate(reader, 2):
            candidate_id = (row.get("candidate_id") or "").strip()
            decision = (row.get("decision") or "").strip().upper()
            if not candidate_id:
                raise GroundingError(f"{path}:{line_number}: missing candidate_id")
            if candidate_id in out:
                raise GroundingError(f"{path}:{line_number}: duplicate approval for {candidate_id}")
            if decision not in {"", "APPROVED", "REJECTED", "SKIP"}:
                raise GroundingError(f"{path}:{line_number}: unknown decision {decision!r}")
            if decision in {"APPROVED", "REJECTED"}:
                reviewer = (row.get("reviewer") or "").strip()
                reviewed_at = (row.get("reviewed_at") or "").strip()
                if not reviewer:
                    raise GroundingError(f"{path}:{line_number}: reviewed row lacks reviewer")
                if not _REVIEW_DATE.fullmatch(reviewed_at):
                    raise GroundingError(
                        f"{path}:{line_number}: reviewed_at must have form YYYY-MM-DD"
                    )
            out[candidate_id] = {**row, "decision": decision}
    return out


def _provider_projection(
    kind: str,
    evidence: dict[str, Any],
    cache: dict[tuple[str, Path], tuple[dict[str, Any], dict]],
    path: Path,
) -> Any:
    key = evidence.get("key")
    payload, _ = cache[(kind, path)]
    if kind in {"residue_frame", "interpro_frame"}:
        entry = payload.get(key)
        if kind == "residue_frame":
            if not isinstance(entry, dict):
                return None
            sequence = _clean_text(entry.get("seq") or entry.get("sequence")) or ""
            return {"sequence": "".join(sequence.split()).upper()}
        if not isinstance(entry, dict):
            return None
        intervals, reasons = _normalise_intervals(entry.get(evidence.get("trait_id")))
        return None if reasons else intervals
    if kind == "profiles":
        return _metadata_projection(payload.get(str(key), {}))
    if kind in {"source_protein_registry", "protein_registry"}:
        return payload.get(str(key))
    if kind == "uniprot_membership":
        return payload.get(str(key))
    if kind == "sifts_mapping":
        return payload.get(str(key))
    return None


def _provider_override(kind: str, evidence: dict[str, Any], args: argparse.Namespace) -> Path:
    override = {
        "residue_frame": args.residue_frame,
        "interpro_frame": args.interpro_frame,
        "profiles": args.profiles,
        # A source registry and the normalized output registry can differ in shape.
        # Never redirect source evidence to the output registry merely because the
        # promoter's --protein-registry points there.
        "source_protein_registry": None,
        "protein_registry": args.protein_registry,
        "uniprot_membership": args.membership_registry,
        "sifts_mapping": args.sifts_registry,
    }.get(kind)
    return override.resolve() if override else _stored_path(evidence["path"]).resolve()


def _provider_cache(
    rows: list[dict[str, Any]], args: argparse.Namespace
) -> dict[tuple[str, Path], tuple[dict[str, Any], dict]]:
    wanted: dict[tuple[str, Path], set[str]] = defaultdict(set)
    for row in rows:
        for evidence in row.get("provider_evidence") or []:
            if not isinstance(evidence, dict) or not evidence.get("kind"):
                continue
            kind = str(evidence["kind"])
            try:
                path = _provider_override(kind, evidence, args)
            except (KeyError, TypeError):
                continue
            wanted[(kind, path)].add(str(evidence.get("key") or ""))
    cache: dict[tuple[str, Path], tuple[dict[str, Any], dict]] = {}
    for (kind, path), keys in wanted.items():
        if not path.is_file():
            continue
        if kind in {"residue_frame", "interpro_frame"}:
            cache[(kind, path)] = _load_sidecar(path)
        elif kind == "profiles":
            cache[(kind, path)] = (_load_profiles(path, keys), {})
        elif kind in {"source_protein_registry", "protein_registry"}:
            cache[(kind, path)] = (_load_object_or_jsonl(path, keys), {})
        elif kind == "uniprot_membership":
            try:
                from uniprot_membership_snapshot import (
                    MembershipSnapshotError,
                    load_memberships,
                )

                rows = load_memberships(path)
            except MembershipSnapshotError as exc:
                raise GroundingError(f"invalid UniProt membership registry: {exc}") from exc
            cache[(kind, path)] = (
                {row["membership_id"]: row for row in rows if row["membership_id"] in keys},
                {},
            )
        elif kind == "sifts_mapping":
            try:
                from build_ecod_sifts_candidates import (
                    EcodSiftsError,
                    load_mapping_registry,
                )

                mappings = load_mapping_registry(path)
            except (EcodSiftsError, OSError) as exc:
                raise GroundingError(f"invalid SIFTS mapping registry: {exc}") from exc
            cache[(kind, path)] = (
                {key: mappings[key] for key in keys if key in mappings},
                {},
            )
    return cache


def _verify_provider_evidence(
    row: dict[str, Any],
    args: argparse.Namespace,
    cache: dict[tuple[str, Path], tuple[dict[str, Any], dict]],
) -> list[str]:
    reasons: list[str] = []
    evidence_rows = row.get("provider_evidence")
    if not isinstance(evidence_rows, list) or not evidence_rows:
        return ["missing:provider_evidence"]
    kinds = set()
    for evidence in evidence_rows:
        if not isinstance(evidence, dict):
            reasons.append("invalid:provider_evidence")
            continue
        kind = _clean_text(evidence.get("kind")) or ""
        kinds.add(kind)
        try:
            path = _provider_override(kind, evidence, args)
        except (KeyError, TypeError):
            reasons.append(f"missing:provider_path:{kind}")
            continue
        if not path.is_file():
            reasons.append(f"stale:provider_missing:{kind}")
            continue
        if (kind, path) not in cache:
            reasons.append(f"unsupported:provider_kind:{kind}")
            continue
        current = _provider_projection(kind, evidence, cache, path)
        if current is None:
            reasons.append(f"stale:provider_entry_missing:{kind}")
            continue
        if kind == "uniprot_membership":
            from uniprot_membership_snapshot import membership_entry_sha256

            observed_digest = membership_entry_sha256(current)
        elif kind == "sifts_mapping":
            from build_ecod_sifts_candidates import mapping_entry_sha256

            observed_digest = mapping_entry_sha256(current)
        else:
            observed_digest = _value_digest(current)
        if observed_digest != evidence.get("entry_sha256"):
            reasons.append(f"stale:provider_entry_changed:{kind}")
            continue
        if kind in {"residue_frame", "interpro_frame"}:
            _, meta = cache[(kind, path)]
            if evidence.get("release") != meta.get("release"):
                reasons.append(f"stale:provider_release_changed:{kind}")
        if kind == "sifts_mapping" and evidence.get("release") != _sifts_provider_release(current):
            reasons.append("stale:provider_release_changed:sifts_mapping")
        if kind == "sifts_mapping":
            try:
                stored_provider_path = _stored_path(str(evidence["path"])).resolve()
            except (KeyError, TypeError):
                reasons.append("missing:provider_path:sifts_mapping")
                continue
            if path != stored_provider_path:
                reasons.append("mismatch:sifts_provider_path_override")
            grounding_evidence = row.get("grounding_evidence")
            if not isinstance(grounding_evidence, dict):
                reasons.append("missing:sifts_grounding_evidence")
                continue
            try:
                evidence_provider_path = _stored_path(
                    str(grounding_evidence["provider_source"])
                ).resolve()
            except (KeyError, TypeError):
                reasons.append("missing:sifts_grounding_provider_source")
                continue
            if evidence_provider_path != stored_provider_path:
                reasons.append("mismatch:sifts_grounding_provider_source")
            if any(
                (
                    grounding_evidence.get("provider_kind") != "SIFTS",
                    grounding_evidence.get("provider_release") != _sifts_provider_release(current),
                    grounding_evidence.get("provider_entry_sha256") != observed_digest,
                    row.get("sifts_mapping_id") != current.get("mapping_id"),
                )
            ):
                reasons.append("mismatch:sifts_grounding_provider_binding")
    if "protein_registry" not in kinds:
        reasons.append("missing:protein_registry_evidence")
    if row.get("mapping_method") == "INTERPRO_MATCH" and "interpro_frame" not in kinds:
        reasons.append("missing:interpro_evidence")
    if row.get("mapping_method") == "SOURCE_MEMBERSHIP" and "uniprot_membership" not in kinds:
        reasons.append("missing:uniprot_membership_evidence")
    if row.get("mapping_method") == "SIFTS_RESIDUE_MAPPING" and "sifts_mapping" not in kinds:
        reasons.append("missing:sifts_mapping_evidence")
    return sorted(set(reasons))


def _authoritative_example(row: dict[str, Any]) -> dict[str, Any]:
    occurrence = row.get("trait_occurrence")
    if not isinstance(occurrence, dict):
        raise GroundingError(f"{row.get('candidate_id')}: missing trait_occurrence")
    example: dict[str, Any] = {
        "protein_id": row["protein_id"],
        "protein_label": row["protein_label"],
        "taxon_id": row["taxon_id"],
        "taxon_label": row["taxon_label"],
        "sequence_length": row["sequence_length"],
        "reviewed": row["reviewed"],
        "sequence_sha256": row["sequence_sha256"],
        "uniprot_release": row["uniprot_release"],
        "source": "UNIPROT_GROUNDING",
        "qualification_status": "QUALIFIED",
        "trait_occurrences": [occurrence],
    }
    if row.get("sequence_version") is not None:
        example["sequence_version"] = row["sequence_version"]
    return example


def _merge_qualified_example(existing: dict, authoritative: dict) -> tuple[dict, bool]:
    if existing.get("sequence"):
        existing_sha = hashlib.sha256(str(existing["sequence"]).encode("ascii")).hexdigest()
        if existing_sha != authoritative["sequence_sha256"]:
            raise GroundingError("mismatch:existing_inline_sequence")
    merged = copy.deepcopy(existing)
    original_source = merged.get("source")
    for key, value in authoritative.items():
        if key not in {"source", "trait_occurrences"}:
            merged[key] = value
    merged["source"] = original_source or authoritative["source"]
    occurrences = merged.get("trait_occurrences") or []
    if not isinstance(occurrences, list):
        raise GroundingError("invalid:existing_trait_occurrences")
    wanted = authoritative["trait_occurrences"][0]
    matching = [
        index
        for index, occurrence in enumerate(occurrences)
        if isinstance(occurrence, dict)
        and occurrence.get("trait_id") == wanted.get("trait_id")
        and occurrence.get("protein_id") == wanted.get("protein_id")
    ]
    if len(matching) > 1:
        raise GroundingError("invalid:duplicate_existing_trait_occurrence")
    if matching:
        index = matching[0]
        if (
            occurrences[index].get("qualification_status") == "QUALIFIED"
            and occurrences[index] != wanted
        ):
            raise GroundingError("conflict:different_qualified_trait_occurrence")
        occurrences[index] = wanted
    else:
        occurrences.append(wanted)
    merged["trait_occurrences"] = occurrences
    return merged, merged != existing


def _install_example(record: dict, row: dict[str, Any]) -> tuple[dict, bool]:
    examples = record.get("canonical_examples") or []
    if not isinstance(examples, list):
        raise GroundingError("invalid:canonical_examples_not_a_list")
    authoritative = _authoritative_example(row)
    matching = [
        index
        for index, example in enumerate(examples)
        if isinstance(example, dict) and example.get("protein_id") == row["protein_id"]
    ]
    if len(matching) > 1:
        raise GroundingError("invalid:duplicate_existing_protein_example")
    changed = False
    if matching:
        index = matching[0]
        examples[index], changed = _merge_qualified_example(examples[index], authoritative)
    else:
        examples.append(authoritative)
        changed = True
    updated = dict(record)
    updated["canonical_examples"] = examples
    return updated, changed


def _replace_examples_block(text: str, record: dict) -> str:
    block = yaml.safe_dump(
        {"canonical_examples": record["canonical_examples"]},
        sort_keys=False,
        allow_unicode=True,
        width=100,
    )
    return replace_block(text, "canonical_examples", block)


def _strict_errors_for_text(text: str) -> list[dict]:
    """Run the same closed-schema gate as the atomic writer during batch preflight."""
    from validate_strict import validate_one

    descriptor, temporary_name = tempfile.mkstemp(suffix=".yaml")
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)
        return validate_one(temporary)
    finally:
        temporary.unlink(missing_ok=True)


def _semantic_registry(path: Path) -> dict[str, dict[str, Any]]:
    """Load the registry through the grounding validator, refusing registry findings."""
    from validate_uniprot_grounding import load_registry

    registry, findings = load_registry(path)
    if findings:
        detail = "; ".join(f"{finding.code}: {finding.message}" for finding in findings[:3])
        raise GroundingError(f"semantic registry validation rejected preflight: {detail}")
    return registry


def _semantic_registry_bytes(raw: bytes, path: Path) -> dict[str, dict[str, Any]]:
    """Validate a fetch-verifier ProteinReference image without reopening its path."""

    from validate_uniprot_grounding import validate_protein_reference

    registry: dict[str, dict[str, Any]] = {}
    findings = []
    for line_number, row in enumerate(_read_verified_jsonl(raw, source=path), 1):
        findings.extend(validate_protein_reference(row, path=path, line=line_number))
        protein_id = row.get("protein_id")
        if not isinstance(protein_id, str):
            continue
        if protein_id in registry:
            raise GroundingError(
                f"semantic registry validation rejected duplicate protein_id: {protein_id}"
            )
        registry[protein_id] = row
    if findings:
        detail = "; ".join(f"{finding.code}: {finding.message}" for finding in findings[:3])
        raise GroundingError(f"semantic registry validation rejected preflight: {detail}")
    return registry


def _membership_rows_from_bytes(raw: bytes, path: Path) -> list[dict[str, Any]]:
    """Validate a fetch-verifier membership image without reopening its path."""

    from uniprot_membership_snapshot import MembershipSnapshotError, merge_memberships

    rows = _read_verified_jsonl(raw, source=path)
    try:
        normalized = merge_memberships(rows)
    except MembershipSnapshotError as exc:
        raise GroundingError(f"invalid UniProt membership registry: {exc}") from exc
    if normalized != rows:
        raise GroundingError("verified UniProt membership registry is not canonically ordered")
    return normalized


def _semantic_evidence_registry(path: Path) -> dict[str, dict[str, Any]]:
    """Load content-addressed source evidence and refuse every registry finding."""
    from validate_uniprot_grounding import load_evidence_registry

    evidence, findings = load_evidence_registry(path)
    if findings:
        detail = "; ".join(f"{finding.code}: {finding.message}" for finding in findings[:3])
        raise GroundingError(f"semantic evidence validation rejected preflight: {detail}")
    return evidence


def _artifact_digest(path: Path) -> str | None:
    """Return a file-content digest, distinguishing a missing durable artifact."""

    if not path.exists():
        return None
    if not path.is_file():
        raise GroundingError(f"durable registry path is not a file: {path}")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_durable_registry(path: Path) -> tuple[dict[str, dict[str, Any]], str | None]:
    """Load one optional durable ProteinReference registry from a stable snapshot."""

    before = _artifact_digest(path)
    if before is None:
        return {}, None
    registry = _semantic_registry(path)
    after = _artifact_digest(path)
    if before != after:
        raise GroundingError(f"durable protein registry changed during preflight: {path}")
    return registry, before


def _load_durable_evidence_registry(
    path: Path,
) -> tuple[dict[str, dict[str, Any]], str | None]:
    """Load one optional durable GroundingEvidence registry from a stable snapshot."""

    before = _artifact_digest(path)
    if before is None:
        return {}, None
    evidence = _semantic_evidence_registry(path)
    after = _artifact_digest(path)
    if before != after:
        raise GroundingError(f"durable evidence registry changed during preflight: {path}")
    return evidence, before


def _load_durable_qualified_record_bindings(
    path: Path,
    durable_evidence: dict[str, dict[str, Any]],
) -> tuple[dict[str, dict[str, Any]], str | None]:
    """Load the complete evidence-to-record receipt registry from a stable image.

    A missing registry is acceptable only for an empty durable evidence registry.  The
    receipt file is intentionally not inferred from trait records: doing so would turn
    the historical unreceipted state into an implicit bypass of the new gate.
    """

    before = _artifact_digest(path)
    if before is None:
        if durable_evidence:
            raise GroundingError(
                "durable qualified-record binding registry is missing while durable "
                f"evidence contains {len(durable_evidence):,} row(s): {path}"
            )
        return {}, None

    bindings: dict[str, dict[str, Any]] = {}
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                binding = json.loads(line)
            except json.JSONDecodeError as exc:
                raise GroundingError(
                    f"{path}:{line_number}: invalid qualified-record binding JSON: {exc}"
                ) from exc
            if not isinstance(binding, dict):
                raise GroundingError(
                    f"{path}:{line_number}: qualified-record binding is not an object"
                )
            fields = set(binding)
            if fields != _QUALIFIED_RECORD_BINDING_FIELDS:
                missing = sorted(_QUALIFIED_RECORD_BINDING_FIELDS - fields)
                extra = sorted(fields - _QUALIFIED_RECORD_BINDING_FIELDS)
                raise GroundingError(
                    f"{path}:{line_number}: qualified-record binding schema mismatch; "
                    f"missing={missing}, extra={extra}"
                )
            if binding.get("schema_version") != 1 or isinstance(
                binding.get("schema_version"), bool
            ):
                raise GroundingError(
                    f"{path}:{line_number}: qualified-record binding schema_version must be 1"
                )
            evidence_id = binding.get("evidence_id")
            if (
                not isinstance(evidence_id, str)
                or re.fullmatch(r"ug-evidence:[0-9a-f]{64}", evidence_id) is None
            ):
                raise GroundingError(
                    f"{path}:{line_number}: invalid qualified-record binding evidence_id"
                )
            if evidence_id in bindings:
                raise GroundingError(
                    f"{path}:{line_number}: duplicate qualified-record binding for {evidence_id}"
                )
            for field_name in ("candidate_id", "trait_id", "record_path"):
                if _clean_text(binding.get(field_name)) is None:
                    raise GroundingError(
                        f"{path}:{line_number}: qualified-record binding lacks {field_name}"
                    )
            for field_name in ("record_sha256", "content_gate_digest"):
                value = binding.get(field_name)
                if not isinstance(value, str) or _SHA256.fullmatch(value) is None:
                    raise GroundingError(
                        f"{path}:{line_number}: qualified-record binding has invalid {field_name}"
                    )
            projection = binding.get("content_gate_projection")
            if not isinstance(projection, dict):
                raise GroundingError(
                    f"{path}:{line_number}: content_gate_projection is not an object"
                )
            if binding["content_gate_digest"] != _value_digest(projection):
                raise GroundingError(
                    f"{path}:{line_number}: tampered qualified-record content-gate digest "
                    f"for {evidence_id}"
                )
            bindings[evidence_id] = binding

    missing = sorted(set(durable_evidence) - set(bindings))
    extra = sorted(set(bindings) - set(durable_evidence))
    if missing or extra:
        raise GroundingError(
            "durable qualified-record bindings do not exactly cover durable evidence; "
            f"missing={missing[:5]}, extra={extra[:5]}"
        )
    after = _artifact_digest(path)
    if before != after:
        raise GroundingError(
            f"durable qualified-record binding registry changed during preflight: {path}"
        )
    return bindings, before


def _content_gate_candidate_projection(row: dict[str, Any]) -> dict[str, Any]:
    """Project exactly the candidate facts consumed by the current content gate."""

    projection = {
        field_name: copy.deepcopy(row.get(field_name))
        for field_name in _CONTENT_GATE_CANDIDATE_FIELDS
    }
    projection["intervals"] = projection.get("intervals") or []
    return projection


def _durable_gate_candidate(
    binding: dict[str, Any],
    evidence: dict[str, Any],
    protein_registry: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Reconstruct gate inputs from durable facts, never from mutable receipt claims."""

    protein_id = _clean_text(evidence.get("protein_id")) or ""
    reference = protein_registry.get(protein_id)
    if reference is None:
        raise GroundingError(
            f"{binding['evidence_id']}: qualified-record binding lacks ProteinReference "
            f"{protein_id!r}"
        )
    stored_projection = binding.get("content_gate_projection")
    stored_candidate = (
        stored_projection.get("candidate") if isinstance(stored_projection, dict) else None
    )
    if not isinstance(stored_candidate, dict):
        raise GroundingError(
            f"{binding['evidence_id']}: qualified-record binding lacks a gate candidate"
        )
    # WHOLE_PROTEIN occurrences deliberately omit resolver match intervals from
    # GroundingEvidence.  Those intervals are still required to replay the PANTHER
    # low-coverage gate, so retain the digest-bound receipt projection only when the
    # durable evidence has no interval claim.  Every scientific field that evidence
    # does carry, and sequence length, remains reconstructed authoritatively below.
    intervals = evidence.get("intervals")
    if intervals is None:
        intervals = stored_candidate.get("intervals")
    normalized_intervals, interval_reasons = _normalise_intervals(intervals)
    if interval_reasons or normalized_intervals != (intervals or []):
        raise GroundingError(
            f"{binding['evidence_id']}: qualified-record binding has non-canonical intervals"
        )
    sequence_length = reference.get("sequence_length")
    if (
        isinstance(sequence_length, bool)
        or not isinstance(sequence_length, int)
        or sequence_length < 1
        or any(
            interval["start"] < 1
            or interval["end"] < interval["start"]
            or interval["end"] > sequence_length
            for interval in normalized_intervals
        )
    ):
        raise GroundingError(
            f"{binding['evidence_id']}: qualified-record binding intervals exceed the "
            "durable ProteinReference"
        )
    identity = {
        "trait_id": evidence.get("trait_id"),
        "protein_id": evidence.get("protein_id"),
        "source_trait_id": evidence.get("source_trait_id"),
        "mapping_method": evidence.get("mapping_method"),
        "evidence_source": evidence.get("evidence_source"),
        "source_release": evidence.get("source_release"),
        "sequence_release": reference.get("uniprot_release"),
        "sequence_sha256": evidence.get("sequence_sha256"),
        "scope": evidence.get("scope"),
        "coordinate_frame": evidence.get("coordinate_frame"),
        "intervals": normalized_intervals,
        "residue_positions": copy.deepcopy(evidence.get("residue_positions") or []),
        "structure_id": evidence.get("structure_id"),
        "chain_id": evidence.get("chain_id"),
        "ecod_domain_id": evidence.get("ecod_domain_id"),
        "sifts_mapping_id": evidence.get("sifts_mapping_id"),
    }
    expected_candidate_id = derive_candidate_id(identity)
    if binding["candidate_id"] != expected_candidate_id:
        raise GroundingError(
            f"{binding['evidence_id']}: qualified-record binding candidate_id does not "
            "match its durable scientific identity"
        )
    return {
        "candidate_id": binding["candidate_id"],
        "trait_id": evidence.get("trait_id"),
        "source_trait_id": evidence.get("source_trait_id"),
        "mapping_method": evidence.get("mapping_method"),
        "scope": evidence.get("scope"),
        "sequence_length": sequence_length,
        "intervals": copy.deepcopy(normalized_intervals),
    }


def _content_gate_projection(
    gate: RecordContentGate,
    record: dict[str, Any],
    candidate: dict[str, Any],
    args: argparse.Namespace,
) -> tuple[dict[str, Any], list[Any]]:
    """Return the reviewable, digestable result of one current pinned-gate replay."""

    try:
        findings = [*gate.evaluate(record), *gate.evaluate_candidate(record, candidate)]
    except ContentGateError as exc:
        raise GroundingError(
            f"{record.get('identifier')}: record-content source replay failed closed: {exc}"
        ) from exc
    projection = {
        "schema_version": 1,
        "policy": {
            "hard_severity": CONTENT_GATE_HARD,
            "hard_codes": sorted(CONTENT_GATE_HARD_CODES),
        },
        "source_artifact_sha256": {
            "interpro_xml": args.interpro_xml_sha256,
            "pfam_clans": args.pfam_clans_sha256,
            "pfam_types": args.pfam_types_sha256,
            "panther_classifications": args.panther_classifications_sha256,
        },
        "record_identifier": record.get("identifier"),
        "candidate": _content_gate_candidate_projection(candidate),
        "findings": [finding.as_dict() for finding in findings],
    }
    return projection, findings


def _qualified_record_binding(
    *,
    evidence_id: str,
    candidate_id: str,
    trait_id: str,
    record_path: Path,
    record_sha256: str,
    content_gate_projection: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "evidence_id": evidence_id,
        "candidate_id": candidate_id,
        "trait_id": trait_id,
        "record_path": _display_path(record_path),
        "record_sha256": record_sha256,
        "content_gate_projection": content_gate_projection,
        "content_gate_digest": _value_digest(content_gate_projection),
    }


def _load_membership_rows(path: Path, *, required: bool) -> list[dict[str, Any]]:
    """Load a strict membership snapshot, optionally treating absence as empty."""

    if not path.exists() and not required:
        return []
    try:
        from uniprot_membership_snapshot import MembershipSnapshotError, load_memberships

        return load_memberships(path)
    except MembershipSnapshotError as exc:
        raise GroundingError(f"invalid UniProt membership registry: {exc}") from exc


def _load_durable_memberships(
    path: Path,
) -> tuple[list[dict[str, Any]], str | None]:
    """Load an optional durable membership snapshot from a stable file image."""

    before = _artifact_digest(path)
    if before is None:
        return [], None
    memberships = _load_membership_rows(path, required=True)
    after = _artifact_digest(path)
    if before != after:
        raise GroundingError(f"durable membership registry changed during preflight: {path}")
    return memberships, before


def _validate_registry_mapping(registry: dict[str, dict[str, Any]], path: Path) -> None:
    """Strictly validate a complete merged ProteinReference mapping in memory."""

    from validate_uniprot_grounding import validate_protein_reference

    findings: list[Any] = []
    for line_number, protein_id in enumerate(sorted(registry), 1):
        reference = registry[protein_id]
        if reference.get("protein_id") != protein_id:
            raise GroundingError(
                f"durable ProteinReference key {protein_id!r} disagrees with its row"
            )
        findings.extend(validate_protein_reference(reference, path=path, line=line_number))
    if findings:
        detail = "; ".join(f"{finding.code}: {finding.message}" for finding in findings[:3])
        raise GroundingError(f"merged durable protein registry is invalid: {detail}")


def _validate_evidence_mapping(evidence_registry: dict[str, dict[str, Any]], path: Path) -> None:
    """Strictly validate a complete merged GroundingEvidence mapping in memory."""

    from validate_uniprot_grounding import validate_grounding_evidence

    findings: list[Any] = []
    for line_number, evidence_id in enumerate(sorted(evidence_registry), 1):
        evidence = evidence_registry[evidence_id]
        if evidence.get("evidence_id") != evidence_id:
            raise GroundingError(
                f"durable GroundingEvidence key {evidence_id!r} disagrees with its row"
            )
        findings.extend(validate_grounding_evidence(evidence, path=path, line=line_number))
    if findings:
        detail = "; ".join(f"{finding.code}: {finding.message}" for finding in findings[:3])
        raise GroundingError(f"merged durable evidence registry is invalid: {detail}")


def _validate_registry_links(
    registry: dict[str, dict[str, Any]],
    evidence_registry: dict[str, dict[str, Any]],
) -> None:
    """Require every durable evidence row to bind to the same durable sequence."""

    errors: list[str] = []
    for evidence_id in sorted(evidence_registry):
        evidence = evidence_registry[evidence_id]
        protein_id = _clean_text(evidence.get("protein_id")) or ""
        reference = registry.get(protein_id)
        if reference is None:
            errors.append(f"{evidence_id}: missing ProteinReference {protein_id!r}")
        elif evidence.get("sequence_sha256") != reference.get("sequence_sha256"):
            errors.append(f"{evidence_id}: ProteinReference sequence_sha256 mismatch")
    if errors:
        raise GroundingError(
            "merged durable registries have broken cross-references: " + "; ".join(errors[:3])
        )


def _selected_registry_rows(
    selected: list[dict[str, Any]],
    staging_registry: dict[str, dict[str, Any]],
    staging_evidence: dict[str, dict[str, Any]],
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    """Project only explicitly approved references and evidence from staging."""

    references: dict[str, dict[str, Any]] = {}
    evidence_rows: dict[str, dict[str, Any]] = {}
    for row in selected:
        candidate_id = str(row["candidate_id"])
        protein_id = _clean_text(row.get("protein_id")) or ""
        reference = staging_registry.get(protein_id)
        if reference is None:
            raise GroundingError(
                f"{candidate_id}: selected protein {protein_id!r} is absent from staging registry"
            )
        expected_reference_digest = _clean_text(row.get("protein_reference_sha256"))
        observed_reference_digest = _value_digest(reference)
        if expected_reference_digest != observed_reference_digest:
            raise GroundingError(
                f"{candidate_id}: staging ProteinReference differs from reviewed resolution"
            )
        previous_reference = references.get(protein_id)
        if previous_reference is not None and previous_reference != reference:
            raise GroundingError(f"conflicting selected ProteinReference rows for {protein_id}")
        references[protein_id] = reference

        occurrence = row.get("trait_occurrence")
        if not isinstance(occurrence, dict):
            raise GroundingError(f"{candidate_id}: selected row lacks trait_occurrence")
        evidence_id = _clean_text(occurrence.get("source_evidence_id"))
        if not evidence_id:
            raise GroundingError(f"{candidate_id}: selected occurrence lacks source_evidence_id")
        evidence = staging_evidence.get(evidence_id)
        if evidence is None:
            raise GroundingError(
                f"{candidate_id}: source evidence {evidence_id!r} is absent from staging registry"
            )
        embedded_evidence = row.get("grounding_evidence")
        if not isinstance(embedded_evidence, dict) or embedded_evidence != evidence:
            raise GroundingError(
                f"{candidate_id}: staging GroundingEvidence differs from reviewed resolution"
            )
        previous_evidence = evidence_rows.get(evidence_id)
        if previous_evidence is not None and previous_evidence != evidence:
            raise GroundingError(f"conflicting selected GroundingEvidence rows for {evidence_id}")
        evidence_rows[evidence_id] = evidence
    return references, evidence_rows


def _selected_membership_rows(
    selected: list[dict[str, Any]],
    references: dict[str, dict[str, Any]],
    staging_memberships: list[dict[str, Any]],
    durable_path: Path,
) -> list[dict[str, Any]]:
    """Select exact reviewed membership facts and verify their evidence binding."""

    from uniprot_membership_snapshot import (
        MembershipSnapshotError,
        find_exact_membership,
        membership_entry_sha256,
        merge_memberships,
    )

    selected_memberships: list[dict[str, Any]] = []
    for row in selected:
        if row.get("mapping_method") != "SOURCE_MEMBERSHIP":
            continue
        candidate_id = str(row["candidate_id"])
        protein_id = str(row["protein_id"])
        source_trait_id = str(row.get("source_trait_id") or "")
        reference = references.get(protein_id)
        if reference is None:
            raise GroundingError(
                f"{candidate_id}: membership promotion lacks selected ProteinReference"
            )
        try:
            membership = find_exact_membership(
                staging_memberships,
                protein_id=protein_id,
                source_trait_id=source_trait_id,
                uniprot_release=reference["uniprot_release"],
                sequence_sha256=reference["sequence_sha256"],
            )
        except MembershipSnapshotError as exc:
            raise GroundingError(f"{candidate_id}: ambiguous staging membership: {exc}") from exc
        if membership is None:
            raise GroundingError(f"{candidate_id}: exact staging membership disappeared")
        grounding_evidence = row.get("grounding_evidence")
        expected_provider_source = _display_path(durable_path)
        expected_entry_sha = membership_entry_sha256(membership)
        if not isinstance(grounding_evidence, dict) or any(
            (
                grounding_evidence.get("mapping_method") != "SOURCE_MEMBERSHIP",
                grounding_evidence.get("scope") != "WHOLE_PROTEIN",
                grounding_evidence.get("evidence_source") != "UniProtKB",
                grounding_evidence.get("source_release") != membership["uniprot_release"],
                grounding_evidence.get("provider_kind") != "UNIPROT",
                grounding_evidence.get("provider_source") != expected_provider_source,
                grounding_evidence.get("provider_release") != membership["uniprot_release"],
                grounding_evidence.get("provider_entry_sha256") != expected_entry_sha,
            )
        ):
            raise GroundingError(
                f"{candidate_id}: membership GroundingEvidence provider binding changed"
            )
        selected_memberships.append(membership)
    try:
        return merge_memberships(selected_memberships)
    except MembershipSnapshotError as exc:
        raise GroundingError(f"selected membership rows conflict: {exc}") from exc


def _merge_registry_rows(
    existing: dict[str, dict[str, Any]],
    additions: dict[str, dict[str, Any]],
    *,
    kind: str,
) -> dict[str, dict[str, Any]]:
    """Merge immutable reviewed rows, rejecting any same-key content conflict."""

    merged = dict(existing)
    for key in sorted(additions):
        row = additions[key]
        previous = merged.get(key)
        if previous is not None and previous != row:
            raise GroundingError(f"conflict: durable {kind} already has different row for {key}")
        merged[key] = row
    return merged


def _registry_text(registry: dict[str, dict[str, Any]]) -> str:
    return "".join(_canonical_json(registry[key]) + "\n" for key in sorted(registry))


def _validate_durable_paths(args: argparse.Namespace, traits_root: Path) -> None:
    outputs = {
        "durable protein registry": args.durable_protein_registry,
        "durable evidence registry": args.durable_evidence_registry,
        "durable membership registry": args.durable_membership_registry,
        "durable qualified-record bindings": args.durable_qualified_record_bindings,
    }
    output_keys = {name: _physical_path_key(path) for name, path in outputs.items()}
    if len(set(output_keys.values())) != len(output_keys):
        raise GroundingError(
            "durable protein, evidence, membership, and qualified-record binding paths must differ"
        )
    protected_input_keys = {
        _physical_path_key(args.resolved),
        _physical_path_key(args.approved),
        _physical_path_key(args.protein_registry),
        _physical_path_key(args.evidence_registry),
        _physical_path_key(args.membership_registry),
    }
    for optional in (
        args.residue_frame,
        args.interpro_frame,
        args.profiles,
        args.sifts_registry,
        args.interpro_xml,
        args.pfam_clans,
        args.pfam_types,
    ):
        if optional is not None:
            protected_input_keys.add(_physical_path_key(optional))
    for name, output in outputs.items():
        if output_keys[name] in protected_input_keys:
            raise GroundingError(
                f"durable registry output must differ from staging/review input: {output}"
            )
        if _path_is_under(output, traits_root) or _path_is_under(output, DEFAULT_TRAITS):
            raise GroundingError(f"durable registry output must be outside trait records: {output}")


def _semantic_errors_for_record(
    record: dict[str, Any],
    registry: dict[str, dict[str, Any]],
    path: Path,
    *,
    evidence_registry: dict[str, dict[str, Any]] | None = None,
    hierarchy_index: dict[str, frozenset[str]] | None = None,
) -> list[Any]:
    """Run sequence/cross-object validation that closed LinkML cannot express."""
    from validate_uniprot_grounding import validate_record

    return validate_record(
        record,
        registry,
        evidence_registry=evidence_registry,
        hierarchy_index=hierarchy_index,
        file=str(path),
        require_qualified=False,
    )


def _validate_resolved_row(row: dict[str, Any], approval: dict[str, str]) -> list[str]:
    reasons: list[str] = []
    if row.get("candidate_id") != derive_candidate_id(row):
        reasons.append("invalid:candidate_id_scientific_identity")
    if row.get("qualification_status") != "QUALIFIED" or row.get("reasons"):
        reasons.append("not_qualified")
    expected_digest = _resolution_digest(row)
    if row.get("resolution_digest") != expected_digest:
        reasons.append("invalid:resolution_digest")
    if approval.get("resolution_digest") != row.get("resolution_digest"):
        reasons.append("stale:approval_resolution_digest")
    occurrence = row.get("trait_occurrence")
    if not isinstance(occurrence, dict) or occurrence.get("qualification_status") != "QUALIFIED":
        reasons.append("missing:qualified_trait_occurrence")
    required = (
        "candidate_id",
        "record_path",
        "record_sha256",
        "trait_id",
        "protein_id",
        "protein_label",
        "taxon_id",
        "taxon_label",
        "sequence_length",
        "sequence_sha256",
        "uniprot_release",
        "mapping_method",
        "evidence_source",
        "source_release",
    )
    for key in required:
        if row.get(key) in (None, ""):
            reasons.append(f"missing:{key}")
    if row.get("evidence_tier") not in {"A", "B"}:
        reasons.append("unqualifiable:evidence_tier")
    return sorted(set(reasons))


def _review_source(row: dict[str, Any]) -> str:
    """Return the source stratum used by both selection and promotion review gates."""

    return (
        _clean_text(row.get("source_namespace")) or str(row.get("trait_id") or "").split(":", 1)[0]
    )


def _review_record_key(row: dict[str, Any]) -> tuple[str, str]:
    """Identify one trait record without letting alternatives inflate coverage."""

    trait_id = _clean_text(row.get("trait_id")) or ""
    record_path = _clean_text(row.get("record_path")) or ""
    if trait_id or record_path:
        return trait_id, record_path
    # Malformed, unselected rows still need a stable singleton group so review
    # accounting cannot accidentally merge them.  Selected rows fail the normal
    # required-field preflight below.
    return "", str(row.get("candidate_id") or "")


def _review_record_label(key: tuple[str, str]) -> str:
    trait_id, record_path = key
    if trait_id and record_path:
        return f"{trait_id} ({record_path})"
    return trait_id or record_path or "(missing record identity)"


def _load_bound_durable_records(
    bindings: dict[str, dict[str, Any]],
    durable_evidence: dict[str, dict[str, Any]],
    durable_registry: dict[str, dict[str, Any]],
    traits_root: Path,
) -> tuple[
    dict[Path, dict[str, Any]],
    dict[Path, str],
    dict[str, tuple[Path, dict[str, Any]]],
]:
    """Dereference every durable receipt and verify its immutable preimage binding."""

    from validate_uniprot_grounding import OCCURRENCE_EVIDENCE_FIELDS

    records: dict[Path, dict[str, Any]] = {}
    record_sha256: dict[Path, str] = {}
    replay_rows: dict[str, tuple[Path, dict[str, Any]]] = {}
    for evidence_id in sorted(bindings):
        binding = bindings[evidence_id]
        evidence = durable_evidence[evidence_id]
        if binding["trait_id"] != evidence.get("trait_id"):
            raise GroundingError(
                f"{evidence_id}: qualified-record binding trait_id disagrees with durable evidence"
            )
        path = _safe_record_path(binding["record_path"], traits_root)
        if binding["record_path"] != _display_path(path):
            raise GroundingError(
                f"{evidence_id}: qualified-record binding record_path is not canonical and "
                f"repo-relative: {binding['record_path']!r}"
            )
        if path not in records:
            try:
                text = path.read_text(encoding="utf-8")
                record = yaml.safe_load(text)
            except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
                raise GroundingError(
                    f"{path}: cannot load durable qualified-record binding: {exc}"
                ) from exc
            if not isinstance(record, dict):
                raise GroundingError(f"{path}: durable qualified record is not a YAML mapping")
            records[path] = record
            record_sha256[path] = _text_digest(text)
        if binding["record_sha256"] != record_sha256[path]:
            raise GroundingError(
                f"{evidence_id}: stale qualified-record binding record_sha256 for "
                f"{_display_path(path)}"
            )
        record = records[path]
        if record.get("identifier") != binding["trait_id"]:
            raise GroundingError(
                f"{evidence_id}: qualified-record binding trait_id disagrees with record"
            )
        matches: list[dict[str, Any]] = []
        for example in record.get("canonical_examples") or []:
            if not isinstance(example, dict):
                continue
            for occurrence in example.get("trait_occurrences") or []:
                if (
                    isinstance(occurrence, dict)
                    and occurrence.get("source_evidence_id") == evidence_id
                ):
                    matches.append(occurrence)
        if len(matches) != 1:
            raise GroundingError(
                f"{evidence_id}: qualified-record binding resolves to {len(matches)} "
                "installed occurrence(s), expected exactly one"
            )
        occurrence = matches[0]
        if occurrence.get("qualification_status") != "QUALIFIED":
            raise GroundingError(
                f"{evidence_id}: qualified-record binding occurrence is not QUALIFIED"
            )
        mismatched_fields = [
            field_name
            for field_name in OCCURRENCE_EVIDENCE_FIELDS
            if occurrence.get(field_name) != evidence.get(field_name)
        ]
        if mismatched_fields:
            raise GroundingError(
                f"{evidence_id}: qualified-record binding occurrence disagrees with durable "
                f"evidence fields {mismatched_fields[:5]}"
            )
        candidate = _durable_gate_candidate(binding, evidence, durable_registry)
        stored_candidate = (
            binding.get("content_gate_projection", {}).get("candidate")
            if isinstance(binding.get("content_gate_projection"), dict)
            else None
        )
        if stored_candidate != _content_gate_candidate_projection(candidate):
            raise GroundingError(
                f"{evidence_id}: tampered qualified-record binding candidate projection"
            )
        replay_rows[evidence_id] = (path, candidate)
    return records, record_sha256, replay_rows


def _promotion_qualified_record_preflight(
    *,
    selected: list[dict[str, Any]],
    selected_evidence: dict[str, dict[str, Any]],
    durable_bindings: dict[str, dict[str, Any]],
    durable_records: dict[Path, dict[str, Any]],
    durable_replay_rows: dict[str, tuple[Path, dict[str, Any]]],
    prospective_records: dict[Path, dict[str, Any]],
    prospective_sha256: dict[Path, str],
    args: argparse.Namespace,
    traits_root: Path,
) -> dict[str, dict[str, Any]]:
    """Replay durable and selected claims together and return the next receipt image."""

    gate_records = dict(durable_records)
    gate_records.update(prospective_records)
    gate = _prepare_content_gate(gate_records.values(), args)
    next_bindings: dict[str, dict[str, Any]] = {}
    blocked: list[str] = []
    stale: list[str] = []

    for evidence_id in sorted(durable_replay_rows):
        path, candidate = durable_replay_rows[evidence_id]
        record = gate_records[path]
        projection, findings = _content_gate_projection(gate, record, candidate, args)
        binding = durable_bindings[evidence_id]
        if projection != binding["content_gate_projection"]:
            stale.append(
                f"{evidence_id}: current content-gate projection differs from its receipt "
                f"({_display_path(path)})"
            )
        hard_codes = sorted(
            finding.code for finding in findings if finding.severity == CONTENT_GATE_HARD
        )
        if hard_codes:
            blocked.append(
                f"{binding['candidate_id']}: {','.join(hard_codes)} ({_display_path(path)})"
            )
        next_bindings[evidence_id] = _qualified_record_binding(
            evidence_id=evidence_id,
            candidate_id=binding["candidate_id"],
            trait_id=binding["trait_id"],
            record_path=path,
            record_sha256=prospective_sha256.get(path, binding["record_sha256"]),
            content_gate_projection=projection,
        )

    for row in selected:
        candidate_id = str(row["candidate_id"])
        path = _safe_record_path(row["record_path"], traits_root)
        record = gate_records[path]
        projection, findings = _content_gate_projection(gate, record, row, args)
        hard_codes = sorted(
            finding.code for finding in findings if finding.severity == CONTENT_GATE_HARD
        )
        if hard_codes:
            blocked.append(f"{candidate_id}: {','.join(hard_codes)} ({_display_path(path)})")
        occurrence = row.get("trait_occurrence")
        evidence_id = _clean_text(
            occurrence.get("source_evidence_id") if isinstance(occurrence, dict) else None
        )
        if evidence_id is None or evidence_id not in selected_evidence:
            raise GroundingError(f"{candidate_id}: cannot bind selected source evidence")
        receipt = _qualified_record_binding(
            evidence_id=evidence_id,
            candidate_id=candidate_id,
            trait_id=str(row["trait_id"]),
            record_path=path,
            record_sha256=prospective_sha256[path],
            content_gate_projection=projection,
        )
        previous = next_bindings.get(evidence_id)
        if previous is not None and previous != receipt:
            raise GroundingError(
                f"{candidate_id}: selected receipt conflicts with durable binding {evidence_id}"
            )
        next_bindings[evidence_id] = receipt

    if stale:
        raise GroundingError(
            "durable qualified-record content-gate receipt(s) are stale; no registry or "
            "trait write was attempted:\n  " + "\n  ".join(stale[:10])
        )
    if blocked:
        raise GroundingError(
            "promotion record-content preflight rejected current record(s) "
            "(durable/selected); no registry or trait write was attempted:\n  "
            + "\n  ".join(blocked[:10])
        )
    return next_bindings


def _install_promotion_transaction(
    artifact_updates: list[tuple[Path, str]],
    trait_updates: dict[Path, str],
) -> None:
    """Install a prevalidated promotion set with exact in-process rollback.

    ``os.replace`` is atomic for each file but not across files.  Snapshotting every
    target before the first replacement and restoring those bytes on any Python-level
    failure prevents an ordinary validation/I/O exception from leaving registries,
    receipts, and trait records at different promotion generations.  A sudden process
    or OS crash still requires a journal for true multi-file crash atomicity.
    """

    targets = [path.resolve() for path, _text in artifact_updates]
    targets.extend(path.resolve() for path in sorted(trait_updates))
    if len(targets) != len(set(targets)):
        raise GroundingError("promotion transaction contains duplicate output paths")
    snapshots = {path: path.read_bytes() if path.is_file() else None for path in targets}
    attempted: list[Path] = []
    try:
        for path, text in artifact_updates:
            resolved = path.resolve()
            attempted.append(resolved)
            _atomic_text(resolved, text)
        for path in sorted(trait_updates):
            resolved = path.resolve()
            attempted.append(resolved)
            write_validated_record(resolved, trait_updates[path], encoding="utf-8")
    except Exception as exc:
        rollback_errors: list[str] = []
        for path in reversed(attempted):
            try:
                snapshot = snapshots[path]
                if snapshot is None:
                    path.unlink(missing_ok=True)
                else:
                    _atomic_bytes(path, snapshot)
            except Exception as rollback_exc:  # pragma: no cover - catastrophic I/O path
                rollback_errors.append(f"{path}: {rollback_exc}")
        if rollback_errors:
            raise GroundingError(
                "promotion transaction failed and rollback was incomplete: "
                + "; ".join(rollback_errors[:5])
            ) from exc
        raise GroundingError(f"promotion transaction failed and was rolled back: {exc}") from exc


def promote(args: argparse.Namespace) -> int:
    resolved_rows = _read_jsonl(args.resolved)
    by_id: dict[str, dict[str, Any]] = {}
    for row in resolved_rows:
        candidate_id = _clean_text(row.get("candidate_id"))
        if not candidate_id:
            raise GroundingError("resolved ledger contains a row without candidate_id")
        if candidate_id in by_id:
            raise GroundingError(f"resolved ledger contains duplicate {candidate_id}")
        by_id[candidate_id] = row
    approvals = _read_approvals(args.approved)
    approved = {key: value for key, value in approvals.items() if value["decision"] == "APPROVED"}
    unknown = sorted(set(approvals) - set(by_id))
    if unknown:
        raise GroundingError(f"approval refers to unknown candidate(s): {', '.join(unknown[:5])}")
    if not approved:
        raise GroundingError("approval TSV contains no decision=APPROVED rows")
    if not 1 <= args.max_batch <= MAX_PROMOTION_BATCH:
        raise GroundingError(f"--max-batch must be between 1 and {MAX_PROMOTION_BATCH}")
    if args.min_source_reviews < 1:
        raise GroundingError("--min-source-reviews must be positive")
    if len(approved) > args.max_batch:
        raise GroundingError(
            f"approval batch has {len(approved):,} candidates; cap is {args.max_batch:,}"
        )
    candidates_by_record: dict[tuple[str, str], set[str]] = defaultdict(set)
    approved_by_record: dict[tuple[str, str], set[str]] = defaultdict(set)
    for candidate_id, row in by_id.items():
        record_key = _review_record_key(row)
        candidates_by_record[record_key].add(candidate_id)
        if candidate_id in approved:
            approved_by_record[record_key].add(candidate_id)
    multiply_approved = {
        record_key: candidate_ids
        for record_key, candidate_ids in approved_by_record.items()
        if len(candidate_ids) > 1
    }
    if multiply_approved:
        detail = "; ".join(
            f"{_review_record_label(record_key)}=[{', '.join(sorted(candidate_ids))}]"
            for record_key, candidate_ids in sorted(multiply_approved.items())[:5]
        )
        raise GroundingError(
            "review protocol approves multiple alternatives for one trait record: " + detail
        )
    undecided_approved_alternatives: dict[tuple[str, str], list[str]] = {}
    for record_key in approved_by_record:
        undecided = sorted(
            candidate_id
            for candidate_id in candidates_by_record[record_key]
            if approvals.get(candidate_id, {}).get("decision") not in {"APPROVED", "REJECTED"}
        )
        if undecided:
            undecided_approved_alternatives[record_key] = undecided
    if undecided_approved_alternatives:
        detail = "; ".join(
            f"{_review_record_label(record_key)}=[{', '.join(candidate_ids)}]"
            for record_key, candidate_ids in sorted(undecided_approved_alternatives.items())[:5]
        )
        raise GroundingError(
            "review protocol leaves alternatives undecided in an approved trait record: " + detail
        )
    selected = [by_id[key] for key in sorted(approved)]
    traits_root = args.traits.resolve()
    sfld_candidates = sorted(
        row["candidate_id"]
        for row in selected
        if _is_sfld_grounding(
            row,
            row.get("trait_occurrence"),
            row.get("grounding_evidence"),
        )
    )
    if sfld_candidates:
        raise GroundingError(
            "SFLD promotion is disabled until the SFLD source-model repair is "
            "complete and regression-validated; no registry or trait write was "
            "attempted (candidate(s): " + ", ".join(sfld_candidates[:5]) + ")"
        )
    prints_candidates = sorted(
        row["candidate_id"]
        for row in selected
        if _is_prints_grounding(
            row,
            row.get("trait_occurrence"),
            row.get("grounding_evidence"),
        )
    )
    if prints_candidates:
        raise GroundingError(
            "PRINTS promotion is disabled until the pinned PRINTS KDAT "
            "representation and exact ordered fingerprint count/length replay are "
            "integrated into durable resolution; no registry or trait write was "
            "attempted (candidate(s): " + ", ".join(prints_candidates[:5]) + ")"
        )
    if any(row.get("mapping_method") == "SIFTS_RESIDUE_MAPPING" for row in selected):
        raise GroundingError(
            "SIFTS promotion is disabled until a durable mapping registry and "
            "standalone semantic replay bind each mapping to a pinned ECOD raw line "
            "and immutable SIFTS XML manifest; no registry or trait write was attempted"
        )
    reviewed_ids = {
        candidate_id
        for candidate_id, approval in approvals.items()
        if approval["decision"] in {"APPROVED", "REJECTED"}
    }
    fully_reviewed_records = {
        record_key
        for record_key, candidate_ids in candidates_by_record.items()
        if all(candidate_id in reviewed_ids for candidate_id in candidate_ids)
    }
    available_by_source: dict[str, set[tuple[str, str]]] = defaultdict(set)
    reviewed_by_source: dict[str, set[tuple[str, str]]] = defaultdict(set)
    for row in by_id.values():
        source = _review_source(row)
        record_key = _review_record_key(row)
        available_by_source[source].add(record_key)
        if record_key in fully_reviewed_records:
            reviewed_by_source[source].add(record_key)
    approved_sources = {_review_source(row) for row in selected}
    required_by_source = {
        source: min(args.min_source_reviews, len(available_by_source[source]))
        for source in approved_sources
    }
    insufficient = {
        source: (len(reviewed_by_source[source]), required_by_source[source])
        for source in approved_sources
        if len(reviewed_by_source[source]) < required_by_source[source]
    }
    if insufficient:
        detail = ", ".join(
            f"{source or '(missing)'}={count}/{required}"
            for source, (count, required) in sorted(insufficient.items())
        )
        raise GroundingError(f"review protocol lacks source-stratified coverage: {detail}")
    coverage_detail = ", ".join(
        f"{source or '(missing)'}={len(reviewed_by_source[source])}/{required_by_source[source]}"
        for source in sorted(approved_sources)
    )
    print(f"review coverage: {coverage_detail}")
    unreviewed_special = sorted(
        row["candidate_id"]
        for row in resolved_rows
        if (
            (_review_source(row)) in approved_sources
            and _review_flags(row)
            and row["candidate_id"] not in reviewed_ids
        )
    )
    if unreviewed_special:
        raise GroundingError(
            "review protocol leaves flagged special case(s) undecided: "
            + ", ".join(unreviewed_special[:5])
        )
    provider_cache = _provider_cache(selected, args)
    preflight_errors: list[str] = []
    for row in selected:
        candidate_id = row["candidate_id"]
        reasons = _validate_resolved_row(row, approved[candidate_id])
        reasons.extend(_verify_provider_evidence(row, args, provider_cache))
        if reasons:
            preflight_errors.append(f"{candidate_id}: {', '.join(sorted(set(reasons)))}")
    if preflight_errors:
        raise GroundingError("promotion preflight rejected:\n  " + "\n  ".join(preflight_errors))
    _validate_durable_paths(args, traits_root)
    staging_registry = _semantic_registry(args.protein_registry.resolve())
    staging_evidence = _semantic_evidence_registry(args.evidence_registry.resolve())
    existing_registry, durable_registry_digest = _load_durable_registry(
        args.durable_protein_registry.resolve()
    )
    existing_evidence, durable_evidence_digest = _load_durable_evidence_registry(
        args.durable_evidence_registry.resolve()
    )
    existing_bindings, durable_bindings_digest = _load_durable_qualified_record_bindings(
        args.durable_qualified_record_bindings.resolve(), existing_evidence
    )
    (
        durable_bound_records,
        durable_bound_record_sha256,
        durable_replay_rows,
    ) = _load_bound_durable_records(
        existing_bindings,
        existing_evidence,
        existing_registry,
        traits_root,
    )
    selected_references, selected_evidence = _selected_registry_rows(
        selected, staging_registry, staging_evidence
    )
    membership_selected = any(row.get("mapping_method") == "SOURCE_MEMBERSHIP" for row in selected)
    merged_memberships: list[dict[str, Any]] = []
    durable_membership_digest: str | None = None
    membership_text = ""
    membership_changed = False
    if membership_selected:
        staging_memberships = _load_membership_rows(
            args.membership_registry.resolve(), required=True
        )
        existing_memberships, durable_membership_digest = _load_durable_memberships(
            args.durable_membership_registry.resolve()
        )
        selected_memberships = _selected_membership_rows(
            selected,
            selected_references,
            staging_memberships,
            args.durable_membership_registry.resolve(),
        )
        try:
            from uniprot_membership_snapshot import (
                MembershipSnapshotError,
                dump_memberships,
                merge_memberships,
            )

            merged_memberships = merge_memberships(existing_memberships, selected_memberships)
            membership_text = dump_memberships(merged_memberships)
        except MembershipSnapshotError as exc:
            raise GroundingError(f"durable membership merge conflict: {exc}") from exc
        membership_changed = durable_membership_digest != _text_digest(membership_text)
    registry = _merge_registry_rows(existing_registry, selected_references, kind="ProteinReference")
    evidence_registry = _merge_registry_rows(
        existing_evidence, selected_evidence, kind="GroundingEvidence"
    )
    _validate_registry_mapping(registry, args.durable_protein_registry.resolve())
    _validate_evidence_mapping(evidence_registry, args.durable_evidence_registry.resolve())
    _validate_registry_links(registry, evidence_registry)
    registry_text = _registry_text(registry)
    evidence_text = _registry_text(evidence_registry)
    registry_changed = durable_registry_digest != _text_digest(registry_text)
    evidence_changed = durable_evidence_digest != _text_digest(evidence_text)
    hierarchy_index: dict[str, frozenset[str]] = {}
    if any(row.get("source_trait_id") != row.get("trait_id") for row in selected):
        from validate_uniprot_grounding import build_hierarchy_index

        hierarchy_index, hierarchy_findings = build_hierarchy_index(
            sorted(traits_root.rglob("*.yaml"))
        )
        if hierarchy_findings:
            detail = "; ".join(
                f"{finding.code}: {finding.message}" for finding in hierarchy_findings[:3]
            )
            raise GroundingError(f"trait hierarchy validation rejected preflight: {detail}")
    grouped: dict[Path, list[dict[str, Any]]] = defaultdict(list)
    for row in selected:
        path = _safe_record_path(row["record_path"], traits_root)
        grouped[path].append(row)
    if len(grouped) > args.max_batch:
        raise GroundingError(
            f"approval batch touches {len(grouped):,} records; cap is {args.max_batch:,}"
        )
    candidates_to_write: dict[Path, tuple[str, str]] = {}
    prospective_records: dict[Path, dict[str, Any]] = {}
    prospective_sha256: dict[Path, str] = {}
    stale_selected_preimages: list[str] = []
    unchanged = 0
    for path in sorted(grouped):
        original_text = path.read_text(encoding="utf-8")
        try:
            record = yaml.safe_load(original_text)
        except yaml.YAMLError as exc:
            raise GroundingError(f"{path}: invalid YAML: {exc}") from exc
        if not isinstance(record, dict):
            raise GroundingError(f"{path}: record is not a mapping")
        original_sha = _text_digest(original_text)
        changed = False
        for row in sorted(grouped[path], key=lambda item: item["candidate_id"]):
            if record.get("identifier") != row.get("trait_id"):
                raise GroundingError(f"{row['candidate_id']}: record identifier changed")
            updated, row_changed = _install_example(record, row)
            if row_changed and original_sha != row.get("record_sha256"):
                stale_selected_preimages.append(
                    f"{row['candidate_id']}: stale:record_changed_since_resolve"
                )
            record = updated
            changed = changed or row_changed
            unchanged += int(not row_changed)
        prospective_records[path] = record
        if not changed:
            prospective_sha256[path] = original_sha
            continue
        candidate_text = _replace_examples_block(original_text, record)
        if candidate_text == original_text:
            raise GroundingError(f"{path}: canonical_examples splice made no change")
        prospective_sha256[path] = _text_digest(candidate_text)
        candidates_to_write[path] = (original_sha, candidate_text)
    bindings = _promotion_qualified_record_preflight(
        selected=selected,
        selected_evidence=selected_evidence,
        durable_bindings=existing_bindings,
        durable_records=durable_bound_records,
        durable_replay_rows=durable_replay_rows,
        prospective_records=prospective_records,
        prospective_sha256=prospective_sha256,
        args=args,
        traits_root=traits_root,
    )
    if stale_selected_preimages:
        raise GroundingError("\n".join(stale_selected_preimages))
    for path in sorted(prospective_records):
        semantic_errors = _semantic_errors_for_record(
            prospective_records[path],
            registry,
            path,
            evidence_registry=evidence_registry,
            hierarchy_index=hierarchy_index,
        )
        if semantic_errors:
            detail = "; ".join(
                f"{finding.code}: {finding.message}" for finding in semantic_errors[:3]
            )
            raise GroundingError(f"{path}: semantic validation rejected preflight: {detail}")
        candidate = candidates_to_write.get(path)
        if candidate is None:
            continue
        strict_errors = _strict_errors_for_text(candidate[1])
        if strict_errors:
            detail = "; ".join(error.get("message", "") for error in strict_errors[:3])
            raise GroundingError(f"{path}: strict validation rejected preflight: {detail}")
    if set(bindings) != set(evidence_registry):
        missing = sorted(set(evidence_registry) - set(bindings))
        extra = sorted(set(bindings) - set(evidence_registry))
        raise GroundingError(
            "prospective qualified-record bindings do not exactly cover merged durable "
            f"evidence; missing={missing[:5]}, extra={extra[:5]}"
        )
    bindings_text = _registry_text(bindings)
    bindings_changed = durable_bindings_digest != _text_digest(bindings_text)
    action = "APPLY" if args.apply else "DRY-RUN"
    print(
        f"{action}: {len(selected):,} approved candidate(s), "
        f"{len(candidates_to_write):,} record write(s), {unchanged:,} already present; "
        f"durable registries: {len(registry):,} protein(s), "
        f"{len(evidence_registry):,} evidence row(s), "
        f"{len(bindings):,} qualified-record binding(s), "
        f"{len(merged_memberships):,} membership row(s) in this merge"
    )
    if not args.apply:
        print(
            "No durable registries or trait records written; pass --apply after "
            "reviewing this preflight."
        )
        return 0
    # Recheck every durable artifact and trait immediately before the first mutation.
    # Atomic replacement prevents torn files; these comparisons also avoid overwriting
    # a curator edit that landed between batch preflight and commit.
    durable_changed_during_preflight = []
    durable_expectations = [
        (args.durable_protein_registry.resolve(), durable_registry_digest),
        (args.durable_evidence_registry.resolve(), durable_evidence_digest),
        (args.durable_qualified_record_bindings.resolve(), durable_bindings_digest),
    ]
    if membership_selected:
        durable_expectations.append(
            (
                args.durable_membership_registry.resolve(),
                durable_membership_digest,
            )
        )
    for path, expected_digest in durable_expectations:
        if _artifact_digest(path) != expected_digest:
            durable_changed_during_preflight.append(path)
    record_expectations = dict(durable_bound_record_sha256)
    record_expectations.update(
        {path: expected_sha for path, (expected_sha, _) in candidates_to_write.items()}
    )
    changed_during_preflight = [
        path
        for path, expected_sha in record_expectations.items()
        if _text_digest(path.read_text(encoding="utf-8")) != expected_sha
    ]
    if durable_changed_during_preflight:
        raise GroundingError(
            "durable registry artifact(s) changed during promotion preflight: "
            + ", ".join(str(path) for path in sorted(durable_changed_during_preflight)[:5])
        )
    if changed_during_preflight:
        raise GroundingError(
            "record(s) changed during promotion preflight: "
            + ", ".join(str(path) for path in sorted(changed_during_preflight)[:5])
        )
    # Install normalized registries and their receipt generation before trait mutation.
    # The transaction helper restores exact preimages after any in-process failure.
    artifact_updates: list[tuple[Path, str]] = []
    if membership_changed:
        artifact_updates.append((args.durable_membership_registry, membership_text))
    if registry_changed:
        artifact_updates.append((args.durable_protein_registry, registry_text))
    if evidence_changed:
        artifact_updates.append((args.durable_evidence_registry, evidence_text))
    if bindings_changed:
        artifact_updates.append((args.durable_qualified_record_bindings, bindings_text))
    _install_promotion_transaction(
        artifact_updates,
        {path: candidate_text for path, (_sha, candidate_text) in candidates_to_write.items()},
    )
    print(
        f"WROTE {int(membership_changed) + int(registry_changed) + int(evidence_changed) + int(bindings_changed):,} "
        "durable registry "
        "artifact(s) before trait mutation"
    )
    print(f"WROTE {len(candidates_to_write):,} validated trait record(s)")
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    resolver = subparsers.add_parser("resolve", help="resolve candidates without writing traits")
    resolver.add_argument("--queue", type=Path, required=True, help="candidate JSONL ledger")
    resolver.add_argument("--providers", default="protein-registry,interpro")
    resolver.add_argument(
        "--batch",
        required=True,
        help="required exact batch/batch_id filter; unlabelled rows are never selected",
    )
    resolver.add_argument("--limit", type=int, help="debug-only deterministic input cap")
    resolver.add_argument(
        "--replace-staging-outputs",
        action="store_true",
        help=(
            "replace ProteinReference/GroundingEvidence staging outputs with the exact "
            "final QUALIFIED projection; incompatible with --limit"
        ),
    )
    resolver.add_argument("--traits", type=Path, default=DEFAULT_TRAITS)
    resolver.add_argument("--residue-frame", type=Path, default=DEFAULT_RESIDUE_FRAME)
    resolver.add_argument("--interpro-frame", type=Path, default=DEFAULT_INTERPRO_FRAME)
    resolver.add_argument("--profiles", type=Path, default=DEFAULT_PROFILES)
    resolver.add_argument(
        "--prints-manifest",
        type=Path,
        default=DEFAULT_PRINTS_MANIFEST,
        help="content-addressed PRINTS raw-snapshot manifest",
    )
    resolver.add_argument(
        "--prints-api",
        type=Path,
        default=DEFAULT_PRINTS_API,
        help="captured PRINTS InterPro API JSONL bound by --prints-manifest",
    )
    resolver.add_argument(
        "--prints-kdat",
        type=Path,
        default=DEFAULT_PRINTS_KDAT,
        help="checksum-pinned PRINTS KDAT bound by --prints-manifest",
    )
    resolver.add_argument(
        "--prints-hierarchy",
        type=Path,
        default=DEFAULT_PRINTS_HIERARCHY,
        help="canonical PRINTS hierarchy JSONL bound by --prints-manifest",
    )
    resolver.add_argument(
        "--interpro-xml",
        type=Path,
        default=DEFAULT_INTERPRO_XML,
        help=(
            "InterPro XML used for record-content replay and whose PRINTS integrations "
            "are bound by --prints-manifest"
        ),
    )
    resolver.add_argument(
        "--interpro-xml-sha256",
        default=INTERPRO_109_XML_SHA256,
        help="required SHA-256 of --interpro-xml for record-content replay",
    )
    resolver.add_argument("--pfam-clans", type=Path, default=DEFAULT_CONTENT_GATE_PFAM_CLANS)
    resolver.add_argument("--pfam-clans-sha256", default=PFAM_A_CLANS_SHA256)
    resolver.add_argument("--pfam-types", type=Path, default=DEFAULT_CONTENT_GATE_PFAM_TYPES)
    resolver.add_argument("--pfam-types-sha256", default=PFAM_TYPES_SHA256)
    resolver.add_argument(
        "--panther-classifications",
        type=Path,
        default=DEFAULT_CONTENT_GATE_PANTHER_CLASSIFICATIONS,
    )
    resolver.add_argument(
        "--panther-classifications-sha256",
        default=PANTHER_19_CLASSIFICATIONS_SHA256,
    )
    resolver.add_argument(
        "--protein-registry", type=Path, help="optional authoritative input registry"
    )
    resolver.add_argument(
        "--fetch-receipt",
        type=Path,
        help="canonical completed UniProt fetch-generation receipt",
    )
    resolver.add_argument(
        "--fetch-request-plan",
        type=Path,
        help="canonical request plan independently supplied for receipt verification",
    )
    resolver.add_argument(
        "--selector-manifest",
        type=Path,
        help="exact selector manifest bound by the fetch request plan",
    )
    resolver.add_argument(
        "--membership-registry",
        type=Path,
        help="release-pinned UniProt databaseCrossReferences staging JSONL",
    )
    resolver.add_argument(
        "--registry-blocked",
        type=Path,
        help="exact blocked-accession TSV bound by the fetch receipt",
    )
    resolver.add_argument(
        "--expect-uniprot-release",
        help="exact YYYY_NN release required from the verified request plan and receipt",
    )
    resolver.add_argument(
        "--allow-offline-uniprot-fixture",
        action="store_true",
        help="test-only: admit a verified OFFLINE_FIXTURE UniProt fetch generation",
    )
    resolver.add_argument(
        "--allow-unreceipted-inputs",
        action="store_true",
        help="explicit historical/non-bounded resolver path without a fetch receipt",
    )
    resolver.add_argument(
        "--sifts-registry",
        type=Path,
        help="content-addressed ECOD/PDBe SIFTS mapping provider JSONL",
    )
    resolver.add_argument(
        "--allow-offline-sifts-fixtures",
        action="store_true",
        help="test-only: admit explicitly marked offline SIFTS fixture mappings",
    )
    resolver.add_argument(
        "--durable-membership-registry",
        type=Path,
        default=DEFAULT_DURABLE_MEMBERSHIP_REGISTRY,
        help="future durable provider path recorded in membership GroundingEvidence",
    )
    resolver.add_argument("--out", type=Path, default=DEFAULT_OUT_DIR / "resolved.jsonl")
    resolver.add_argument("--review", type=Path, default=DEFAULT_OUT_DIR / "review.tsv")
    resolver.add_argument(
        "--registry-out", type=Path, default=DEFAULT_OUT_DIR / "protein_registry.jsonl"
    )
    resolver.add_argument("--evidence-out", type=Path, default=DEFAULT_EVIDENCE_REGISTRY)
    resolver.add_argument("--fail-on-rejected", action="store_true")
    resolver.set_defaults(func=resolve)

    promoter = subparsers.add_parser("promote", help="promote explicitly approved rows")
    promoter.add_argument("--resolved", type=Path, required=True)
    promoter.add_argument("--approved", type=Path, required=True)
    promoter.add_argument("--traits", type=Path, default=DEFAULT_TRAITS)
    promoter.add_argument(
        "--protein-registry",
        type=Path,
        help="reviewed staging ProteinReference registry (default: beside --resolved)",
    )
    promoter.add_argument(
        "--evidence-registry",
        type=Path,
        help="reviewed staging GroundingEvidence registry (default: beside --resolved)",
    )
    promoter.add_argument(
        "--membership-registry",
        type=Path,
        help="reviewed staging UniProt membership snapshot (default: beside --resolved)",
    )
    promoter.add_argument(
        "--sifts-registry",
        type=Path,
        help="reviewed ECOD/PDBe SIFTS mapping provider (default: beside --resolved)",
    )
    promoter.add_argument(
        "--durable-protein-registry",
        type=Path,
        default=DEFAULT_DURABLE_PROTEIN_REGISTRY,
        help=f"durable approved ProteinReference output (default: {DEFAULT_DURABLE_PROTEIN_REGISTRY})",
    )
    promoter.add_argument(
        "--durable-evidence-registry",
        type=Path,
        default=DEFAULT_DURABLE_EVIDENCE_REGISTRY,
        help=f"durable approved GroundingEvidence output (default: {DEFAULT_DURABLE_EVIDENCE_REGISTRY})",
    )
    promoter.add_argument(
        "--durable-membership-registry",
        type=Path,
        default=DEFAULT_DURABLE_MEMBERSHIP_REGISTRY,
        help=(
            "durable approved UniProt membership output "
            f"(default: {DEFAULT_DURABLE_MEMBERSHIP_REGISTRY})"
        ),
    )
    promoter.add_argument(
        "--durable-qualified-record-bindings",
        type=Path,
        default=DEFAULT_DURABLE_QUALIFIED_RECORD_BINDINGS,
        help=(
            "transactional evidence-to-record content-gate receipts "
            f"(default: {DEFAULT_DURABLE_QUALIFIED_RECORD_BINDINGS})"
        ),
    )
    promoter.add_argument("--residue-frame", type=Path)
    promoter.add_argument("--interpro-frame", type=Path)
    promoter.add_argument("--profiles", type=Path)
    promoter.add_argument("--interpro-xml", type=Path, default=DEFAULT_INTERPRO_XML)
    promoter.add_argument("--interpro-xml-sha256", default=INTERPRO_109_XML_SHA256)
    promoter.add_argument("--pfam-clans", type=Path, default=DEFAULT_CONTENT_GATE_PFAM_CLANS)
    promoter.add_argument("--pfam-clans-sha256", default=PFAM_A_CLANS_SHA256)
    promoter.add_argument("--pfam-types", type=Path, default=DEFAULT_CONTENT_GATE_PFAM_TYPES)
    promoter.add_argument("--pfam-types-sha256", default=PFAM_TYPES_SHA256)
    promoter.add_argument(
        "--panther-classifications",
        type=Path,
        default=DEFAULT_CONTENT_GATE_PANTHER_CLASSIFICATIONS,
    )
    promoter.add_argument(
        "--panther-classifications-sha256",
        default=PANTHER_19_CLASSIFICATIONS_SHA256,
    )
    promoter.add_argument(
        "--max-batch",
        type=int,
        default=MAX_PROMOTION_BATCH,
        help=f"review batch cap; cannot exceed {MAX_PROMOTION_BATCH}",
    )
    promoter.add_argument(
        "--min-source-reviews",
        type=int,
        default=MIN_SOURCE_REVIEWS,
        help=(
            "minimum decided unique trait records per promoted source, capped by "
            f"available records (default: {MIN_SOURCE_REVIEWS})"
        ),
    )
    promoter.add_argument(
        "--apply",
        action="store_true",
        help="atomically install durable registries, then write validated trait records",
    )
    promoter.set_defaults(func=promote)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "resolve" and args.protein_registry:
        if args.protein_registry.resolve() == args.registry_out.resolve():
            raise SystemExit("input --protein-registry and --registry-out must differ")
    if args.command == "promote" and args.protein_registry is None:
        default_registry = args.resolved.resolve().parent / "protein_registry.jsonl"
        args.protein_registry = default_registry
    if args.command == "promote" and args.evidence_registry is None:
        args.evidence_registry = args.resolved.resolve().parent / "occurrence_evidence.jsonl"
    if args.command == "promote" and args.membership_registry is None:
        args.membership_registry = args.resolved.resolve().parent / "uniprot_memberships.jsonl"
    if args.command == "promote" and args.sifts_registry is None:
        args.sifts_registry = args.resolved.resolve().parent / "sifts_mappings.jsonl"
    try:
        return args.func(args)
    except GroundingError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
