#!/usr/bin/env python3
"""Select a deterministic, source-stratified UniProt grounding review batch.

The input remains an immutable candidate ledger.  Optional prior decision ledgers can
exclude reviewed records, but only when they are paired with the selected candidate
snapshot, its manifest, and the exact resolved-row snapshot.  Every decision is bound
to the recomputed ``resolution_digest`` of that resolved row.  Every mentioned record
group must decide all of its alternatives, and exactly one candidate must be
``APPROVED`` for exclusion.  Fully covered all-``REJECTED`` groups remain eligible for
re-review after source repair.  Repeated complete all-``REJECTED`` histories are
coalesced as one reopenable record.  Exactly one independently complete approved
adjudication may terminally supersede one or more complete all-``REJECTED``
adjudications for the same exact trait ID and record path; that mixed history is
content-addressed separately and excluded according to the approved candidate snapshot.
A second approved adjudication, partial, unknown, mixed-identity, stale, and other
ambiguous duplicate decisions fail closed.  With
``--defer-unchanged-all-rejected``, a fully
reviewed all-``REJECTED`` group is also deferred only while every resolved alternative
binds the same valid trait-record SHA-256 and the current normalized YAML file remains
byte-identical.  This opt-in comparison covers trait-record edits only; callers must
omit it after any source snapshot, content gate, provider, or resolver change so source
repairs reopen the group.  Changed files explicitly reopen; missing, unreadable, or
inconsistent bindings fail closed.  From the residual queue this command first
assigns every trait-record group to exactly one deterministic SHA-256 shard, then
chooses at most 1,000 groups from the requested shard.  It includes every group
containing a recognized special case within that shard and guarantees at least 25
records per source when that many are available in the shard.  Every candidate
alternative for a selected record is emitted; selection never silently substitutes one
protein for another.  Remaining record capacity is filled by a deterministic
round-robin over sources.

Output candidates are relabelled with the explicit review ``batch_id`` while retaining
their original label as ``source_batch``.  JSON and TSV manifests bind the selection to
the SHA-256 of the complete input queue and to the SHA-256 of the emitted JSONL.  The
command is dry-run by default and never reads or writes trait YAML files.

Example::

    uv run python scripts/select_uniprot_review_batch.py \
      --queue reports/uniprot-grounding/candidates.jsonl \
      --exclude-reviewed-candidates reports/uniprot-grounding/review-batches/\
ready-local-review-001.candidates.jsonl \
      --exclude-reviewed-manifest reports/uniprot-grounding/review-batches/\
ready-local-review-001.manifest.json \
      --exclude-reviewed-resolved reports/uniprot-grounding/review-batches/\
ready-local-review-001.resolved.jsonl \
      --exclude-decisions reports/uniprot-grounding/review-batches/\
ready-local-review-001.review-decisions.digest-bound.jsonl \
      --batch-id uniprot-2026-02-review-001 --apply
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import sys
import tempfile
from collections import Counter, defaultdict, deque
from collections.abc import Iterable
from dataclasses import dataclass
from io import StringIO
from pathlib import Path, PurePosixPath
from typing import Any

import ground_uniprot_examples as ground

REPO_ROOT = Path(__file__).resolve().parents[1]
TRAITS_ROOT = REPO_ROOT / "data" / "traits"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "reports" / "uniprot-grounding" / "review-batches"

MINIMUM_PER_SOURCE = 25
MAX_REVIEW_BATCH = 1000
MANIFEST_SCHEMA_VERSION = 6
SELECTION_ALGORITHM = "reviewed-exclusion-record-group-sha256-shard-special-first-minimum-rr-v6"
SHARD_ALGORITHM = "sha256-canonical-json-trait-id-record-path-modulo-v1"
DECISION_EXCLUSION_ALGORITHM = (
    "prior-candidate-resolved-digest-record-state-complete-current-projection-v6"
)

_BATCH_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_ISOFORM = re.compile(r"^UniProtKB:[A-Za-z0-9]+-([1-9][0-9]*)$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_DEFERRED_UNCHANGED = "DEFERRED_UNCHANGED"
_REOPENED_CHANGED = "REOPENED_CHANGED"

_MANIFEST_COLUMNS = (
    "schema_version",
    "selection_algorithm",
    "record_shard_algorithm",
    "batch_id",
    "source_batch",
    "queue_sha256",
    "decision_ledger_set_sha256",
    "decision_ledger_count",
    "decision_row_count",
    "unique_decided_candidate_rows",
    "repeated_all_rejected_trait_records",
    "repeated_all_rejected_adjudications",
    "repeated_all_rejected_decision_rows",
    "repeated_all_rejected_duplicate_decision_rows",
    "repeated_all_rejected_history_sha256",
    "resolved_all_rejected_trait_records",
    "resolved_all_rejected_superseded_adjudications",
    "resolved_all_rejected_superseded_decision_rows",
    "resolved_all_rejected_approved_adjudications",
    "resolved_all_rejected_approved_decision_rows",
    "resolved_all_rejected_history_sha256",
    "defer_unchanged_all_rejected",
    "all_rejected_deferral_sha256",
    "deferred_unchanged_candidate_rows",
    "deferred_unchanged_trait_records",
    "reopened_changed_candidate_rows",
    "reopened_changed_trait_records",
    "already_absent_reviewed_candidate_rows",
    "already_absent_reviewed_trait_records",
    "all_rejected_not_excluded_candidate_rows",
    "all_rejected_not_excluded_trait_records",
    "all_rejected_record_keys_sha256",
    "all_rejected_candidate_ids_sha256",
    "stale_reviewed_candidate_rows",
    "stale_reviewed_trait_records",
    "pre_exclusion_source_slice_candidate_rows",
    "pre_exclusion_source_slice_trait_records",
    "excluded_source_slice_candidate_rows",
    "excluded_source_slice_trait_records",
    "excluded_shard_candidate_rows",
    "excluded_shard_trait_records",
    "candidate_jsonl_sha256",
    "shard_count",
    "shard_index",
    "source_namespace",
    "global_source_slice_candidate_rows",
    "global_source_slice_trait_records",
    "global_source_slice_special_records",
    "global_source_slice_review_flags",
    "shard_available_candidate_rows",
    "shard_available_trait_records",
    "shard_minimum_required",
    "shard_selected_trait_records",
    "shard_selected_candidate_rows",
    "shard_available_special_records",
    "shard_selected_special_records",
    "shard_minimum_satisfied",
    "all_shard_special_selected",
    "shard_available_review_flags",
    "shard_selected_review_flags",
)


class SelectionError(RuntimeError):
    """The requested review batch cannot be selected without violating an invariant."""


@dataclass(frozen=True)
class QueueSnapshot:
    sha256: str
    total_rows: int
    batch_rows: tuple[dict[str, Any], ...]


@dataclass(frozen=True)
class DecisionLedgerSnapshot:
    path: Path
    sha256: str
    row_count: int
    approved_count: int
    rejected_count: int


@dataclass(frozen=True)
class ResolvedLedgerSnapshot:
    path: Path
    sha256: str
    row_count: int


@dataclass(frozen=True)
class ResolvedRowBinding:
    record_key: tuple[str, str]
    resolution_digest: str
    record_sha256: Any


@dataclass(frozen=True)
class AllRejectedRecordState:
    trait_id: str
    record_path: str
    bound_record_sha256: str
    current_record_sha256: str
    status: str
    reviewed_candidate_ids: tuple[str, ...]
    current_candidate_ids: tuple[str, ...]

    @property
    def record_key(self) -> tuple[str, str]:
        return self.trait_id, self.record_path


@dataclass(frozen=True)
class AllRejectedAdjudication:
    """One independently complete all-rejected decision occurrence."""

    trait_id: str
    record_path: str
    batch_id: str
    candidates_sha256: str
    manifest_sha256: str
    resolved_sha256: str
    decisions_sha256: str
    candidate_ids: tuple[str, ...]
    resolution_digests: tuple[tuple[str, str], ...]
    record_sha256s: tuple[Any, ...]

    @property
    def record_key(self) -> tuple[str, str]:
        return self.trait_id, self.record_path


@dataclass(frozen=True)
class RepeatedAllRejectedRecord:
    """Content-addressed history for one record reviewed all-rejected more than once."""

    trait_id: str
    record_path: str
    adjudications: tuple[AllRejectedAdjudication, ...]

    @property
    def record_key(self) -> tuple[str, str]:
        return self.trait_id, self.record_path


@dataclass(frozen=True)
class ApprovedAdjudication:
    """One independently complete adjudication with exactly one approved candidate."""

    trait_id: str
    record_path: str
    batch_id: str
    candidates_sha256: str
    manifest_sha256: str
    resolved_sha256: str
    decisions_sha256: str
    candidate_ids: tuple[str, ...]
    resolution_digests: tuple[tuple[str, str], ...]
    record_sha256s: tuple[Any, ...]
    approved_candidate_id: str
    approved_resolution_digest: str

    @property
    def record_key(self) -> tuple[str, str]:
        return self.trait_id, self.record_path


@dataclass(frozen=True)
class ResolvedAllRejectedHistory:
    """All-rejected histories terminally superseded by one approved adjudication."""

    trait_id: str
    record_path: str
    approved_adjudication: ApprovedAdjudication
    superseded_all_rejected_adjudications: tuple[AllRejectedAdjudication, ...]

    @property
    def record_key(self) -> tuple[str, str]:
        return self.trait_id, self.record_path


@dataclass(frozen=True)
class ReviewedBatchSnapshot:
    candidates_path: Path
    candidates_sha256: str
    candidate_row_count: int
    candidate_record_count: int
    manifest_path: Path
    manifest_sha256: str
    prior_queue_sha256: str
    prior_queue_matches_current: bool
    batch_id: str
    source_batch: str
    resolved: ResolvedLedgerSnapshot
    decisions: DecisionLedgerSnapshot
    fully_decided_record_count: int
    approved_record_count: int
    all_rejected_record_count: int


@dataclass(frozen=True)
class ReviewExclusions:
    records: frozenset[tuple[str, str]]
    reviewed_records: frozenset[tuple[str, str]]
    already_absent_records: frozenset[tuple[str, str]]
    all_rejected_records: frozenset[tuple[str, str]]
    candidate_ids: frozenset[str]
    excluded_candidate_ids: frozenset[str]
    already_absent_candidate_ids: frozenset[str]
    all_rejected_candidate_ids: frozenset[str]
    defer_unchanged_all_rejected: bool
    deferred_all_rejected_records: frozenset[tuple[str, str]]
    reopened_all_rejected_records: frozenset[tuple[str, str]]
    deferred_all_rejected_candidate_ids: frozenset[str]
    reopened_all_rejected_candidate_ids: frozenset[str]
    all_rejected_record_states: tuple[AllRejectedRecordState, ...]
    repeated_all_rejected_records: tuple[RepeatedAllRejectedRecord, ...]
    resolved_all_rejected_histories: tuple[ResolvedAllRejectedHistory, ...]
    batches: tuple[ReviewedBatchSnapshot, ...]

    @property
    def ledger_set_sha256(self) -> str | None:
        if not self.batches:
            return None
        content_addresses = sorted(
            (
                {
                    "candidates_sha256": batch.candidates_sha256,
                    "manifest_sha256": batch.manifest_sha256,
                    "resolved_sha256": batch.resolved.sha256,
                    "resolved_row_count": batch.resolved.row_count,
                    "decisions_sha256": batch.decisions.sha256,
                    "decision_row_count": batch.decisions.row_count,
                    "fully_decided_record_count": batch.fully_decided_record_count,
                    "approved_record_count": batch.approved_record_count,
                    "all_rejected_record_count": batch.all_rejected_record_count,
                }
                for batch in self.batches
            ),
            key=lambda item: (
                item["candidates_sha256"],
                item["manifest_sha256"],
                item["resolved_sha256"],
                item["decisions_sha256"],
            ),
        )
        return hashlib.sha256(_canonical_json(content_addresses).encode("utf-8")).hexdigest()

    @property
    def row_count(self) -> int:
        return sum(batch.decisions.row_count for batch in self.batches)

    @property
    def unique_decided_candidate_count(self) -> int:
        return len(self.candidate_ids)


@dataclass(frozen=True)
class ExplicitDecision:
    candidate_id: str
    resolution_digest: str
    decision: str
    trait_id: str
    record_path: str
    ledger_path: Path
    line_number: int


@dataclass(frozen=True)
class TraitRecord:
    record_path: str
    trait_id: str
    source_namespace: str
    candidates: tuple[dict[str, Any], ...]
    review_flags: tuple[str, ...]

    @property
    def key(self) -> tuple[str, str]:
        return (self.trait_id, self.record_path)

    @property
    def candidate_count(self) -> int:
        return len(self.candidates)


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _clean(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _safe_record_path(value: Any, line_number: int, *, subject: str = "candidate") -> str | None:
    """Return a normalized relative POSIX record identity, rejecting unsafe paths."""

    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    if not isinstance(value, str):
        raise SelectionError(f"{subject} line {line_number} has non-string record_path {value!r}")
    record_path = value
    path = PurePosixPath(record_path)
    if (
        record_path != record_path.strip()
        or "\\" in record_path
        or "\x00" in record_path
        or path.is_absolute()
        or ".." in path.parts
        or path.as_posix() != record_path
        or path.suffix not in {".yaml", ".yml"}
    ):
        raise SelectionError(
            f"{subject} line {line_number} has unsafe record_path {record_path!r}; "
            "expected a normalized relative POSIX path"
        )
    return record_path


def _validate_shard_pair(shard_count: int, shard_index: int) -> None:
    if not isinstance(shard_count, int) or isinstance(shard_count, bool) or shard_count < 1:
        raise SelectionError("--shard-count must be an integer greater than or equal to 1")
    if (
        not isinstance(shard_index, int)
        or isinstance(shard_index, bool)
        or not 0 <= shard_index < shard_count
    ):
        raise SelectionError(
            "--shard-index must be a zero-based integer in the range 0 <= index < --shard-count"
        )


def _row_batch(row: dict[str, Any]) -> str | None:
    """Use the current batch label, accepting batch_id only for compatible ledgers."""

    return _clean(row.get("batch")) or _clean(row.get("batch_id"))


def _read_queue(path: Path, batch: str) -> QueueSnapshot:
    if not path.is_file():
        raise SelectionError(f"candidate ledger does not exist: {path}")

    digest = hashlib.sha256()
    selected: list[dict[str, Any]] = []
    total_rows = 0
    with path.open("rb") as handle:
        before = os.fstat(handle.fileno())
        for line_number, raw_line in enumerate(handle, 1):
            digest.update(raw_line)
            if not raw_line.strip():
                continue
            total_rows += 1
            try:
                row = json.loads(raw_line)
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise SelectionError(f"{path}:{line_number}: invalid UTF-8 JSON: {exc}") from exc
            if not isinstance(row, dict):
                raise SelectionError(f"{path}:{line_number}: row is not a JSON object")
            if _row_batch(row) == batch:
                selected.append({**row, "_queue_line": line_number})
        after = os.fstat(handle.fileno())
    try:
        current = path.stat()
    except OSError as exc:
        raise SelectionError(
            f"candidate ledger disappeared while it was being read: {path}"
        ) from exc
    before_identity = (
        before.st_dev,
        before.st_ino,
        before.st_size,
        before.st_mtime_ns,
        before.st_ctime_ns,
    )
    after_identity = (
        after.st_dev,
        after.st_ino,
        after.st_size,
        after.st_mtime_ns,
        after.st_ctime_ns,
    )
    current_identity = (
        current.st_dev,
        current.st_ino,
        current.st_size,
        current.st_mtime_ns,
        current.st_ctime_ns,
    )
    if before_identity != after_identity or before_identity != current_identity:
        raise SelectionError(f"candidate ledger changed while it was being read: {path}")
    if not selected:
        raise SelectionError(f"candidate ledger has no rows with exact batch={batch!r}")
    return QueueSnapshot(digest.hexdigest(), total_rows, tuple(selected))


def _truthy_collection(value: Any) -> bool:
    return isinstance(value, (list, tuple, set, dict)) and bool(value)


def _count_over_one(row: dict[str, Any], keys: Iterable[str]) -> bool:
    for key in keys:
        value = row.get(key)
        if isinstance(value, int) and not isinstance(value, bool) and value > 1:
            return True
    return False


def _explicitly_ambiguous(row: dict[str, Any]) -> bool:
    if any(row.get(key) is True for key in ("ambiguous", "is_ambiguous")):
        return True
    for key in ("ambiguity_flag", "ambiguity_flags", "ambiguity_reason", "ambiguity_reasons"):
        value = row.get(key)
        if value is True or _truthy_collection(value) or (isinstance(value, str) and value.strip()):
            return True
    state = " ".join(
        _clean(row.get(key)) or ""
        for key in ("candidate_state", "candidate_status", "resolution_state")
    ).upper()
    if "AMBIGU" in state:
        return True
    reasons = row.get("reasons")
    if isinstance(reasons, list) and any(
        isinstance(reason, str) and "AMBIGU" in reason.upper() for reason in reasons
    ):
        return True
    flags = row.get("flags")
    if isinstance(flags, list):
        return any(isinstance(flag, str) and "AMBIGU" in flag.upper() for flag in flags)
    return False


def review_flags(row: dict[str, Any]) -> tuple[str, ...]:
    """Return the exhaustive-review classes represented by one candidate row."""

    flags: set[str] = set()
    protein_id = _clean(row.get("protein_id")) or ""
    if _ISOFORM.fullmatch(protein_id):
        flags.add("ISOFORM")

    intervals = row.get("intervals")
    multi_interval = isinstance(intervals, list) and len(intervals) > 1
    multi_hit = any(row.get(key) is True for key in ("multi_hit", "multiple_hits"))
    multi_hit = multi_hit or _count_over_one(
        row, ("hit_count", "match_count", "location_count", "interval_count")
    )
    hits = row.get("hits")
    if multi_interval or multi_hit or (isinstance(hits, list) and len(hits) > 1):
        flags.add("MULTI_INTERVAL_OR_HIT")

    positions = row.get("residue_positions")
    if isinstance(positions, list) and positions:
        flags.add("RESIDUE_SET")

    trait_id = _clean(row.get("trait_id"))
    source_trait_id = _clean(row.get("source_trait_id"))
    if (source_trait_id and source_trait_id != trait_id) or _truthy_collection(
        row.get("inheritance_path")
    ):
        flags.add("INHERITANCE")

    mapping_method = (_clean(row.get("mapping_method")) or "").upper()
    evidence_source = (_clean(row.get("evidence_source")) or "").upper()
    if "SIFTS" in mapping_method or evidence_source == "SIFTS":
        flags.add("SIFTS")
    if (_clean(row.get("mapping_completeness")) or "").upper() == "PARTIAL":
        flags.update(("PARTIAL_SIFTS", "SIFTS"))

    if _explicitly_ambiguous(row):
        flags.add("EXPLICIT_AMBIGUITY")
    return tuple(sorted(flags))


def _candidate_order(row: dict[str, Any]) -> tuple[str, str, int]:
    """Give retained alternatives a stable order independent of queue ordering."""

    return (
        _clean(row.get("protein_id")) or "",
        _clean(row.get("candidate_id")) or "",
        int(row["_queue_line"]),
    )


def _trait_records(rows: Iterable[dict[str, Any]]) -> list[TraitRecord]:
    by_path: dict[str, list[dict[str, Any]]] = defaultdict(list)
    seen_candidate_ids: dict[str, int] = {}
    trait_paths: dict[str, str] = {}
    for row in rows:
        line_number = int(row["_queue_line"])
        candidate_id = _clean(row.get("candidate_id"))
        trait_id = _clean(row.get("trait_id"))
        record_path = _safe_record_path(row.get("record_path"), line_number)
        source = _clean(row.get("source_namespace"))
        missing = [
            key
            for key, value in (
                ("candidate_id", candidate_id),
                ("trait_id", trait_id),
                ("record_path", record_path),
                ("source_namespace", source),
            )
            if not value
        ]
        if missing:
            raise SelectionError(
                f"candidate line {line_number} lacks required field(s): {', '.join(missing)}"
            )
        assert candidate_id is not None
        assert trait_id is not None
        assert record_path is not None
        if candidate_id in seen_candidate_ids:
            raise SelectionError(
                f"duplicate candidate_id {candidate_id!r} at lines "
                f"{seen_candidate_ids[candidate_id]} and {line_number}"
            )
        seen_candidate_ids[candidate_id] = line_number
        previous_path = trait_paths.setdefault(trait_id, record_path)
        if previous_path != record_path:
            raise SelectionError(
                f"trait_id {trait_id!r} maps to multiple record paths: "
                f"{previous_path!r}, {record_path!r}"
            )
        by_path[record_path].append(row)

    records: list[TraitRecord] = []
    for record_path in sorted(by_path):
        candidates = by_path[record_path]
        trait_ids = {_clean(row.get("trait_id")) for row in candidates}
        sources = {_clean(row.get("source_namespace")) for row in candidates}
        if len(trait_ids) != 1 or len(sources) != 1:
            raise SelectionError(
                f"record {record_path!r} has candidates with conflicting trait/source identity"
            )
        ordered_candidates = sorted(candidates, key=_candidate_order)
        all_flags = set().union(*(set(review_flags(row)) for row in candidates))
        clean_candidates = tuple(
            {key: value for key, value in candidate.items() if key != "_queue_line"}
            for candidate in ordered_candidates
        )
        records.append(
            TraitRecord(
                record_path=record_path,
                trait_id=next(iter(trait_ids)) or "",
                source_namespace=next(iter(sources)) or "",
                candidates=clean_candidates,
                review_flags=tuple(sorted(all_flags)),
            )
        )
    return records


def _stat_identity(stat_result: os.stat_result) -> tuple[int, int, int, int, int]:
    return (
        stat_result.st_dev,
        stat_result.st_ino,
        stat_result.st_size,
        stat_result.st_mtime_ns,
        stat_result.st_ctime_ns,
    )


def _read_decision_ledger(
    path: Path,
) -> tuple[DecisionLedgerSnapshot, tuple[ExplicitDecision, ...]]:
    if not path.is_file():
        raise SelectionError(f"decision ledger does not exist: {path}")

    digest = hashlib.sha256()
    decisions: list[ExplicitDecision] = []
    approved = 0
    rejected = 0
    try:
        with path.open("rb") as handle:
            before = os.fstat(handle.fileno())
            for line_number, raw_line in enumerate(handle, 1):
                digest.update(raw_line)
                if not raw_line.strip():
                    continue
                try:
                    row = json.loads(raw_line)
                except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                    raise SelectionError(
                        f"{path}:{line_number}: invalid UTF-8 JSON: {exc}"
                    ) from exc
                if not isinstance(row, dict):
                    raise SelectionError(f"{path}:{line_number}: decision is not a JSON object")

                candidate_id = row.get("candidate_id")
                if (
                    not isinstance(candidate_id, str)
                    or not candidate_id
                    or candidate_id != candidate_id.strip()
                ):
                    raise SelectionError(
                        f"{path}:{line_number}: decision lacks an exact non-empty candidate_id"
                    )
                decision = row.get("decision")
                if decision not in {"APPROVED", "REJECTED"}:
                    raise SelectionError(
                        f"{path}:{line_number}: candidate {candidate_id!r} has unknown decision "
                        f"{decision!r}; expected exactly APPROVED or REJECTED"
                    )
                resolution_digest = row.get("resolution_digest")
                if not isinstance(resolution_digest, str) or not _SHA256.fullmatch(
                    resolution_digest
                ):
                    raise SelectionError(
                        f"{path}:{line_number}: candidate {candidate_id!r} lacks a valid "
                        "resolution_digest"
                    )
                record_key = row.get("record_key")
                if not isinstance(record_key, dict):
                    raise SelectionError(
                        f"{path}:{line_number}: candidate {candidate_id!r} lacks record_key"
                    )
                trait_id = record_key.get("trait_id")
                if not isinstance(trait_id, str) or not trait_id or trait_id != trait_id.strip():
                    raise SelectionError(
                        f"{path}:{line_number}: candidate {candidate_id!r} has invalid "
                        "record_key.trait_id"
                    )
                record_path = _safe_record_path(
                    record_key.get("record_path"),
                    line_number,
                    subject=f"decision ledger {path}",
                )
                if record_path is None:
                    raise SelectionError(
                        f"{path}:{line_number}: candidate {candidate_id!r} lacks "
                        "record_key.record_path"
                    )
                decisions.append(
                    ExplicitDecision(
                        candidate_id=candidate_id,
                        resolution_digest=resolution_digest,
                        decision=decision,
                        trait_id=trait_id,
                        record_path=record_path,
                        ledger_path=path,
                        line_number=line_number,
                    )
                )
                approved += decision == "APPROVED"
                rejected += decision == "REJECTED"
            after = os.fstat(handle.fileno())
    except OSError as exc:
        raise SelectionError(f"cannot read decision ledger {path}: {exc}") from exc
    try:
        current = path.stat()
    except OSError as exc:
        raise SelectionError(f"decision ledger disappeared while being read: {path}") from exc
    if _stat_identity(before) != _stat_identity(after) or _stat_identity(before) != _stat_identity(
        current
    ):
        raise SelectionError(f"decision ledger changed while it was being read: {path}")
    if not decisions:
        raise SelectionError(f"decision ledger contains no explicit decisions: {path}")
    return (
        DecisionLedgerSnapshot(
            path=path,
            sha256=digest.hexdigest(),
            row_count=len(decisions),
            approved_count=approved,
            rejected_count=rejected,
        ),
        tuple(decisions),
    )


def _read_reviewed_candidates(path: Path) -> QueueSnapshot:
    if not path.is_file():
        raise SelectionError(f"reviewed candidate snapshot does not exist: {path}")
    digest = hashlib.sha256()
    rows: list[dict[str, Any]] = []
    try:
        with path.open("rb") as handle:
            before = os.fstat(handle.fileno())
            for line_number, raw_line in enumerate(handle, 1):
                digest.update(raw_line)
                if not raw_line.strip():
                    continue
                try:
                    row = json.loads(raw_line)
                except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                    raise SelectionError(
                        f"{path}:{line_number}: invalid UTF-8 JSON: {exc}"
                    ) from exc
                if not isinstance(row, dict):
                    raise SelectionError(
                        f"{path}:{line_number}: reviewed candidate is not a JSON object"
                    )
                rows.append({**row, "_queue_line": line_number})
            after = os.fstat(handle.fileno())
    except OSError as exc:
        raise SelectionError(f"cannot read reviewed candidate snapshot {path}: {exc}") from exc
    try:
        current = path.stat()
    except OSError as exc:
        raise SelectionError(
            f"reviewed candidate snapshot disappeared while being read: {path}"
        ) from exc
    if _stat_identity(before) != _stat_identity(after) or _stat_identity(before) != _stat_identity(
        current
    ):
        raise SelectionError(f"reviewed candidate snapshot changed while being read: {path}")
    if not rows:
        raise SelectionError(f"reviewed candidate snapshot contains no candidates: {path}")
    return QueueSnapshot(digest.hexdigest(), len(rows), tuple(rows))


def _read_reviewed_resolved(
    path: Path,
) -> tuple[ResolvedLedgerSnapshot, dict[str, ResolvedRowBinding]]:
    """Read and verify one exact resolved-row snapshot without touching traits."""

    if not path.is_file():
        raise SelectionError(f"reviewed resolved snapshot does not exist: {path}")
    digest = hashlib.sha256()
    by_id: dict[str, ResolvedRowBinding] = {}
    try:
        with path.open("rb") as handle:
            before = os.fstat(handle.fileno())
            for line_number, raw_line in enumerate(handle, 1):
                digest.update(raw_line)
                if not raw_line.strip():
                    continue
                try:
                    row = json.loads(raw_line)
                except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                    raise SelectionError(
                        f"{path}:{line_number}: invalid UTF-8 JSON in resolved snapshot: {exc}"
                    ) from exc
                if not isinstance(row, dict):
                    raise SelectionError(f"{path}:{line_number}: resolved row is not a JSON object")
                candidate_id = row.get("candidate_id")
                if (
                    not isinstance(candidate_id, str)
                    or not candidate_id
                    or candidate_id != candidate_id.strip()
                ):
                    raise SelectionError(
                        f"{path}:{line_number}: resolved row lacks an exact candidate_id"
                    )
                if candidate_id in by_id:
                    raise SelectionError(
                        f"{path}:{line_number}: duplicate resolved candidate_id {candidate_id!r}"
                    )
                trait_id = row.get("trait_id")
                if not isinstance(trait_id, str) or not trait_id or trait_id != trait_id.strip():
                    raise SelectionError(
                        f"{path}:{line_number}: resolved candidate {candidate_id!r} has "
                        "invalid trait_id"
                    )
                record_path = _safe_record_path(
                    row.get("record_path"),
                    line_number,
                    subject=f"resolved snapshot {path}",
                )
                if record_path is None:
                    raise SelectionError(
                        f"{path}:{line_number}: resolved candidate {candidate_id!r} lacks "
                        "record_path"
                    )
                resolution_digest = row.get("resolution_digest")
                if not isinstance(resolution_digest, str) or not _SHA256.fullmatch(
                    resolution_digest
                ):
                    raise SelectionError(
                        f"{path}:{line_number}: resolved candidate {candidate_id!r} lacks "
                        "a valid resolution_digest"
                    )
                # The resolver's own implementation, not a copy of it (#620).
                expected_digest = ground._resolution_digest(row)
                if resolution_digest != expected_digest:
                    raise SelectionError(
                        f"{path}:{line_number}: resolved candidate {candidate_id!r} has "
                        f"stale resolution_digest {resolution_digest}; expected "
                        f"{expected_digest}"
                    )
                by_id[candidate_id] = ResolvedRowBinding(
                    record_key=(trait_id, record_path),
                    resolution_digest=resolution_digest,
                    record_sha256=row.get("record_sha256"),
                )
            after = os.fstat(handle.fileno())
    except OSError as exc:
        raise SelectionError(f"cannot read reviewed resolved snapshot {path}: {exc}") from exc
    try:
        current = path.stat()
    except OSError as exc:
        raise SelectionError(
            f"reviewed resolved snapshot disappeared while being read: {path}"
        ) from exc
    if _stat_identity(before) != _stat_identity(after) or _stat_identity(before) != _stat_identity(
        current
    ):
        raise SelectionError(f"reviewed resolved snapshot changed while being read: {path}")
    if not by_id:
        raise SelectionError(f"reviewed resolved snapshot contains no rows: {path}")
    return (
        ResolvedLedgerSnapshot(
            path=path,
            sha256=digest.hexdigest(),
            row_count=len(by_id),
        ),
        by_id,
    )


def _read_review_manifest(path: Path) -> tuple[dict[str, Any], str]:
    if not path.is_file():
        raise SelectionError(f"review-batch manifest does not exist: {path}")
    try:
        before = path.stat()
        raw = path.read_bytes()
        after = path.stat()
    except OSError as exc:
        raise SelectionError(f"cannot read review-batch manifest {path}: {exc}") from exc
    if _stat_identity(before) != _stat_identity(after):
        raise SelectionError(f"review-batch manifest changed while it was being read: {path}")
    try:
        manifest = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SelectionError(f"{path}: invalid UTF-8 JSON manifest: {exc}") from exc
    if not isinstance(manifest, dict):
        raise SelectionError(f"{path}: review-batch manifest is not a JSON object")
    return manifest, hashlib.sha256(raw).hexdigest()


def _manifest_count(manifest: dict[str, Any], *keys: str) -> int | None:
    for key in keys:
        value = manifest.get(key)
        if isinstance(value, int) and not isinstance(value, bool):
            return value
    return None


def _verify_reviewed_batch(
    *,
    candidates_path: Path,
    manifest_path: Path,
    resolved_path: Path,
    decisions_path: Path,
    current_queue_sha256: str,
    current_source_batch: str,
) -> tuple[
    ReviewedBatchSnapshot,
    dict[tuple[str, str], set[str]],
    tuple[ExplicitDecision, ...],
    dict[str, ResolvedRowBinding],
]:
    candidate_snapshot = _read_reviewed_candidates(candidates_path)
    manifest, manifest_sha256 = _read_review_manifest(manifest_path)
    if manifest.get("candidate_jsonl_sha256") != candidate_snapshot.sha256:
        raise SelectionError(
            f"review-batch manifest {manifest_path} does not bind the exact candidate "
            f"snapshot {candidates_path}; expected candidate_jsonl_sha256 "
            f"{candidate_snapshot.sha256}"
        )
    prior_queue_sha256 = manifest.get("queue_sha256")
    if not isinstance(prior_queue_sha256, str) or not re.fullmatch(
        r"[0-9a-f]{64}", prior_queue_sha256
    ):
        raise SelectionError(
            f"review-batch manifest {manifest_path} lacks a valid bound queue_sha256"
        )
    if not isinstance(manifest.get("queue"), str) or not manifest["queue"].strip():
        raise SelectionError(f"review-batch manifest {manifest_path} lacks its queue path")
    batch_id = _clean(manifest.get("batch_id"))
    source_batch = _clean(manifest.get("source_batch"))
    if not batch_id or not source_batch:
        raise SelectionError(f"review-batch manifest {manifest_path} lacks batch_id/source_batch")
    if source_batch != current_source_batch:
        raise SelectionError(
            f"review-batch manifest {manifest_path} source_batch={source_batch!r} does not "
            f"match the selected queue batch {current_source_batch!r}"
        )
    for row in candidate_snapshot.batch_rows:
        line_number = int(row["_queue_line"])
        if _row_batch(row) != batch_id:
            raise SelectionError(
                f"{candidates_path}:{line_number}: candidate batch does not match "
                f"manifest batch_id={batch_id!r}"
            )
        if _clean(row.get("source_batch")) != source_batch:
            raise SelectionError(
                f"{candidates_path}:{line_number}: candidate source_batch does not match "
                f"manifest source_batch={source_batch!r}"
            )
    records = _trait_records(candidate_snapshot.batch_rows)
    expected_rows = _manifest_count(
        manifest, "selected_candidate_rows", "shard_selected_candidate_rows"
    )
    expected_records = _manifest_count(
        manifest, "selected_trait_records", "shard_selected_trait_records"
    )
    if expected_rows != candidate_snapshot.total_rows or expected_records != len(records):
        raise SelectionError(
            f"review-batch manifest {manifest_path} selected row/record counts do not "
            f"match {candidates_path}"
        )
    invariants = manifest.get("invariants")
    downstream = manifest.get("downstream_requirements")
    if not isinstance(invariants, dict) or not invariants.get(
        "all_selected_candidate_alternatives_retained"
    ):
        raise SelectionError(
            f"review-batch manifest {manifest_path} does not attest that all candidate "
            "alternatives were retained"
        )
    if not isinstance(downstream, dict) or not downstream.get(
        "all_alternatives_must_receive_an_explicit_review_decision"
    ):
        raise SelectionError(
            f"review-batch manifest {manifest_path} lacks the exhaustive-decision contract"
        )

    record_candidates: dict[tuple[str, str], set[str]] = {}
    for record in records:
        candidate_ids = {str(candidate["candidate_id"]) for candidate in record.candidates}
        record_candidates[record.key] = candidate_ids
        declared_counts = {
            candidate.get("record_candidate_count") for candidate in record.candidates
        }
        if declared_counts != {len(candidate_ids)}:
            raise SelectionError(
                f"reviewed candidate group trait_id={record.trait_id!r}, "
                f"record_path={record.record_path!r} does not bind its exact alternative count"
            )

    prior_candidate_records = {
        candidate_id: record_key
        for record_key, candidate_ids in record_candidates.items()
        for candidate_id in candidate_ids
    }
    resolved_ledger, resolved_by_id = _read_reviewed_resolved(resolved_path)
    expected_ids = set(prior_candidate_records)
    resolved_ids = set(resolved_by_id)
    if resolved_ids != expected_ids:
        raise SelectionError(
            f"reviewed resolved snapshot {resolved_path} does not exactly match selected "
            f"candidates {candidates_path}; added={sorted(resolved_ids - expected_ids)!r}, "
            f"missing={sorted(expected_ids - resolved_ids)!r}"
        )
    for candidate_id in sorted(expected_ids):
        resolved_key = resolved_by_id[candidate_id].record_key
        expected_key = prior_candidate_records[candidate_id]
        if resolved_key != expected_key:
            raise SelectionError(
                f"reviewed resolved snapshot {resolved_path} has mixed record identity for "
                f"candidate_id {candidate_id!r}; expected trait_id={expected_key[0]!r}, "
                f"record_path={expected_key[1]!r}"
            )

    ledger, decisions = _read_decision_ledger(decisions_path)
    for decision in decisions:
        resolved = resolved_by_id.get(decision.candidate_id)
        if resolved is not None and decision.resolution_digest != resolved.resolution_digest:
            raise SelectionError(
                f"stale resolution_digest for candidate_id {decision.candidate_id!r} at "
                f"{decision.ledger_path}:{decision.line_number}; expected "
                f"{resolved.resolution_digest}"
            )
    return (
        ReviewedBatchSnapshot(
            candidates_path=candidates_path,
            candidates_sha256=candidate_snapshot.sha256,
            candidate_row_count=candidate_snapshot.total_rows,
            candidate_record_count=len(records),
            manifest_path=manifest_path,
            manifest_sha256=manifest_sha256,
            prior_queue_sha256=prior_queue_sha256,
            prior_queue_matches_current=prior_queue_sha256 == current_queue_sha256,
            batch_id=batch_id,
            source_batch=source_batch,
            resolved=resolved_ledger,
            decisions=ledger,
            fully_decided_record_count=0,
            approved_record_count=0,
            all_rejected_record_count=0,
        ),
        record_candidates,
        decisions,
        resolved_by_id,
    )


def _current_trait_record_sha256(record_path: str) -> str:
    """Hash one normalized trait path, rejecting missing or unstable reads."""

    relative = PurePosixPath(record_path)
    target = REPO_ROOT.joinpath(*relative.parts)
    resolved_target = target.resolve()
    try:
        resolved_target.relative_to(TRAITS_ROOT.resolve())
    except ValueError as exc:
        raise SelectionError(
            f"all-rejected deferral record_path {record_path!r} is not under repo data/traits"
        ) from exc
    if not target.is_file():
        raise SelectionError(
            f"all-rejected deferral trait record is missing or unreadable: {record_path}"
        )
    digest = hashlib.sha256()
    try:
        with target.open("rb") as handle:
            before = os.fstat(handle.fileno())
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
            after = os.fstat(handle.fileno())
        current = target.stat()
    except OSError as exc:
        raise SelectionError(
            f"cannot read all-rejected deferral trait record {record_path}: {exc}"
        ) from exc
    if _stat_identity(before) != _stat_identity(after) or _stat_identity(before) != _stat_identity(
        current
    ):
        raise SelectionError(
            f"all-rejected deferral trait record changed while being read: {record_path}"
        )
    return digest.hexdigest()


def _all_rejected_record_state(
    record_key: tuple[str, str],
    adjudications: Iterable[AllRejectedAdjudication],
    current_candidate_ids: set[str] | None,
) -> AllRejectedRecordState:
    adjudication_rows = tuple(adjudications)
    reviewed_candidate_ids = {
        candidate_id
        for adjudication in adjudication_rows
        for candidate_id in adjudication.candidate_ids
    }
    bound_hashes: set[str] = set()
    for adjudication in adjudication_rows:
        for candidate_id, record_sha256 in zip(
            adjudication.candidate_ids, adjudication.record_sha256s, strict=True
        ):
            if not isinstance(record_sha256, str) or not _SHA256.fullmatch(record_sha256):
                raise SelectionError(
                    f"all-rejected record trait_id={record_key[0]!r}, "
                    f"record_path={record_key[1]!r} candidate {candidate_id!r} in "
                    f"batch {adjudication.batch_id!r} lacks a valid resolved record_sha256"
                )
            bound_hashes.add(record_sha256)
    if len(bound_hashes) != 1:
        raise SelectionError(
            f"all-rejected record trait_id={record_key[0]!r}, "
            f"record_path={record_key[1]!r} has inconsistent resolved record_sha256 values "
            "across alternatives or repeated adjudications"
        )
    bound_hash = next(iter(bound_hashes))
    current_hash = _current_trait_record_sha256(record_key[1])
    status = _DEFERRED_UNCHANGED if current_hash == bound_hash else _REOPENED_CHANGED
    return AllRejectedRecordState(
        trait_id=record_key[0],
        record_path=record_key[1],
        bound_record_sha256=bound_hash,
        current_record_sha256=current_hash,
        status=status,
        reviewed_candidate_ids=tuple(sorted(reviewed_candidate_ids)),
        current_candidate_ids=tuple(sorted(current_candidate_ids or set())),
    )


def _review_exclusions(
    records: list[TraitRecord],
    reviewed_artifacts: Iterable[tuple[Path, Path, Path, Path]],
    *,
    current_queue_sha256: str,
    current_source_batch: str,
    defer_unchanged_all_rejected: bool = False,
) -> ReviewExclusions:
    artifacts = tuple(
        sorted(
            reviewed_artifacts,
            key=lambda item: tuple(path.resolve().as_posix() for path in item),
        )
    )
    input_paths = [path.resolve() for artifact in artifacts for path in artifact]
    if len(input_paths) != len(set(input_paths)):
        raise SelectionError(
            "reviewed candidates, manifests, resolved snapshots, and decision ledgers "
            "must be distinct"
        )
    if not artifacts:
        return ReviewExclusions(
            records=frozenset(),
            reviewed_records=frozenset(),
            already_absent_records=frozenset(),
            all_rejected_records=frozenset(),
            candidate_ids=frozenset(),
            excluded_candidate_ids=frozenset(),
            already_absent_candidate_ids=frozenset(),
            all_rejected_candidate_ids=frozenset(),
            defer_unchanged_all_rejected=defer_unchanged_all_rejected,
            deferred_all_rejected_records=frozenset(),
            reopened_all_rejected_records=frozenset(),
            deferred_all_rejected_candidate_ids=frozenset(),
            reopened_all_rejected_candidate_ids=frozenset(),
            all_rejected_record_states=(),
            repeated_all_rejected_records=(),
            resolved_all_rejected_histories=(),
            batches=(),
        )

    current_candidate_records: dict[str, tuple[str, str]] = {}
    current_record_candidates: dict[tuple[str, str], set[str]] = {}
    current_paths: dict[str, tuple[str, str]] = {}
    current_traits: dict[str, tuple[str, str]] = {}
    for record in records:
        candidate_ids = {str(candidate["candidate_id"]) for candidate in record.candidates}
        current_record_candidates[record.key] = candidate_ids
        current_paths[record.record_path] = record.key
        current_traits[record.trait_id] = record.key
        for candidate_id in candidate_ids:
            current_candidate_records[candidate_id] = record.key

    batches: list[ReviewedBatchSnapshot] = []
    seen: dict[str, ExplicitDecision] = {}
    reviewed_records: set[tuple[str, str]] = set()
    all_rejected_records: set[tuple[str, str]] = set()
    current_exclusions: set[tuple[str, str]] = set()
    already_absent: set[tuple[str, str]] = set()
    excluded_candidate_ids: set[str] = set()
    already_absent_candidate_ids: set[str] = set()
    all_rejected_candidate_ids: set[str] = set()
    deferred_all_rejected_records: set[tuple[str, str]] = set()
    reopened_all_rejected_records: set[tuple[str, str]] = set()
    deferred_all_rejected_candidate_ids: set[str] = set()
    reopened_all_rejected_candidate_ids: set[str] = set()
    all_rejected_record_states: list[AllRejectedRecordState] = []
    record_adjudications: dict[
        tuple[str, str], list[AllRejectedAdjudication | ApprovedAdjudication]
    ] = defaultdict(list)
    for candidates_path, manifest_path, resolved_path, decisions_path in artifacts:
        batch, prior_record_candidates, decisions, resolved_by_id = _verify_reviewed_batch(
            candidates_path=candidates_path,
            manifest_path=manifest_path,
            resolved_path=resolved_path,
            decisions_path=decisions_path,
            current_queue_sha256=current_queue_sha256,
            current_source_batch=current_source_batch,
        )
        decisions_by_record: dict[tuple[str, str], set[str]] = defaultdict(set)
        statuses_by_record: dict[tuple[str, str], list[str]] = defaultdict(list)
        decisions_by_id: dict[str, ExplicitDecision] = {}
        batch_approved_records = 0
        batch_all_rejected_records = 0
        prior_candidate_records = {
            candidate_id: record_key
            for record_key, candidate_ids in prior_record_candidates.items()
            for candidate_id in candidate_ids
        }
        for decision in decisions:
            previous_in_batch = decisions_by_id.get(decision.candidate_id)
            if previous_in_batch is not None:
                raise SelectionError(
                    f"duplicate decision for candidate_id {decision.candidate_id!r} at "
                    f"{previous_in_batch.ledger_path}:{previous_in_batch.line_number} and "
                    f"{decision.ledger_path}:{decision.line_number}"
                )
            decisions_by_id[decision.candidate_id] = decision
            prior_key = prior_candidate_records.get(decision.candidate_id)
            decision_key = (decision.trait_id, decision.record_path)
            if prior_key is None:
                raise SelectionError(
                    f"unknown decision candidate_id {decision.candidate_id!r} at "
                    f"{decision.ledger_path}:{decision.line_number}; it is absent from "
                    f"the bound reviewed candidate snapshot {candidates_path}"
                )
            if decision_key != prior_key:
                raise SelectionError(
                    f"stale record_key for candidate_id {decision.candidate_id!r} at "
                    f"{decision.ledger_path}:{decision.line_number}; expected "
                    f"trait_id={prior_key[0]!r}, record_path={prior_key[1]!r}"
                )
            decisions_by_record[prior_key].add(decision.candidate_id)
            statuses_by_record[prior_key].append(decision.decision)

        for record_key, decided_ids in sorted(decisions_by_record.items()):
            expected_ids = prior_record_candidates[record_key]
            if decided_ids != expected_ids:
                missing = sorted(expected_ids - decided_ids)
                raise SelectionError(
                    f"partial decisions for trait_id={record_key[0]!r}, "
                    f"record_path={record_key[1]!r}; missing alternatives from the bound "
                    f"reviewed candidate snapshot {missing!r}"
                )
            approved_count = statuses_by_record[record_key].count("APPROVED")
            if approved_count > 1:
                raise SelectionError(
                    f"record trait_id={record_key[0]!r}, record_path={record_key[1]!r} has "
                    f"{approved_count} APPROVED candidates; expected at most one"
                )
            for candidate_id in sorted(expected_ids):
                decision = decisions_by_id[candidate_id]
                previous = seen.get(candidate_id)
                if (
                    previous is not None
                    and (
                        previous.trait_id,
                        previous.record_path,
                    )
                    != record_key
                ):
                    raise SelectionError(
                        f"duplicate decision candidate_id {candidate_id!r} is reused across "
                        "record identities at "
                        f"{previous.ledger_path}:{previous.line_number} and "
                        f"{decision.ledger_path}:{decision.line_number}"
                    )
                if previous is None:
                    seen[candidate_id] = decision
            ordered_ids = tuple(sorted(expected_ids))
            common = {
                "trait_id": record_key[0],
                "record_path": record_key[1],
                "batch_id": batch.batch_id,
                "candidates_sha256": batch.candidates_sha256,
                "manifest_sha256": batch.manifest_sha256,
                "resolved_sha256": batch.resolved.sha256,
                "decisions_sha256": batch.decisions.sha256,
                "candidate_ids": ordered_ids,
                "resolution_digests": tuple(
                    (candidate_id, resolved_by_id[candidate_id].resolution_digest)
                    for candidate_id in ordered_ids
                ),
                "record_sha256s": tuple(
                    resolved_by_id[candidate_id].record_sha256 for candidate_id in ordered_ids
                ),
            }
            if approved_count == 0:
                batch_all_rejected_records += 1
                record_adjudications[record_key].append(AllRejectedAdjudication(**common))
            else:
                batch_approved_records += 1
                approved_candidate_id = next(
                    candidate_id
                    for candidate_id in ordered_ids
                    if decisions_by_id[candidate_id].decision == "APPROVED"
                )
                record_adjudications[record_key].append(
                    ApprovedAdjudication(
                        **common,
                        approved_candidate_id=approved_candidate_id,
                        approved_resolution_digest=resolved_by_id[
                            approved_candidate_id
                        ].resolution_digest,
                    )
                )

        batches.append(
            ReviewedBatchSnapshot(
                **{
                    **batch.__dict__,
                    "fully_decided_record_count": len(decisions_by_record),
                    "approved_record_count": batch_approved_records,
                    "all_rejected_record_count": batch_all_rejected_records,
                }
            )
        )

    all_rejected_adjudications: dict[tuple[str, str], list[AllRejectedAdjudication]] = {}
    resolved_all_rejected_histories: list[ResolvedAllRejectedHistory] = []
    for record_key, adjudications in sorted(record_adjudications.items()):
        approved = [item for item in adjudications if isinstance(item, ApprovedAdjudication)]
        rejected = [item for item in adjudications if isinstance(item, AllRejectedAdjudication)]
        if len(approved) > 1:
            raise SelectionError(
                f"repeated reviewed record group trait_id={record_key[0]!r}, "
                f"record_path={record_key[1]!r} has {len(approved)} independently complete "
                "approved adjudications; expected at most one"
            )
        if not approved:
            all_rejected_records.add(record_key)
            all_rejected_adjudications[record_key] = rejected
            all_rejected_candidate_ids.update(
                candidate_id
                for adjudication in rejected
                for candidate_id in adjudication.candidate_ids
            )
            continue

        approved_adjudication = approved[0]
        reviewed_records.add(record_key)
        approved_ids = set(approved_adjudication.candidate_ids)
        current_ids = current_record_candidates.get(record_key)
        if current_ids is None:
            if (
                record_key[1] in current_paths
                or record_key[0] in current_traits
                or approved_ids & set(current_candidate_records)
            ):
                raise SelectionError(
                    f"stale reviewed record identity trait_id={record_key[0]!r}, "
                    f"record_path={record_key[1]!r} in the current exact queue batch"
                )
            already_absent.add(record_key)
            already_absent_candidate_ids.update(approved_ids)
        elif current_ids != approved_ids:
            raise SelectionError(
                f"stale candidate alternatives for trait_id={record_key[0]!r}, "
                f"record_path={record_key[1]!r}; added={sorted(current_ids - approved_ids)!r}, "
                f"missing={sorted(approved_ids - current_ids)!r}; re-review is required"
            )
        else:
            current_exclusions.add(record_key)
            excluded_candidate_ids.update(approved_ids)
        if rejected:
            resolved_all_rejected_histories.append(
                ResolvedAllRejectedHistory(
                    trait_id=record_key[0],
                    record_path=record_key[1],
                    approved_adjudication=approved_adjudication,
                    superseded_all_rejected_adjudications=tuple(
                        sorted(
                            rejected,
                            key=lambda item: _canonical_json(
                                _all_rejected_adjudication_payload(item)
                            ),
                        )
                    ),
                )
            )

    repeated_all_rejected_records = tuple(
        RepeatedAllRejectedRecord(
            trait_id=record_key[0],
            record_path=record_key[1],
            adjudications=tuple(
                sorted(
                    adjudications,
                    key=lambda item: _canonical_json(_all_rejected_adjudication_payload(item)),
                )
            ),
        )
        for record_key, adjudications in sorted(all_rejected_adjudications.items())
        if len(adjudications) > 1
    )
    if defer_unchanged_all_rejected:
        for record_key in sorted(all_rejected_records):
            adjudications = all_rejected_adjudications[record_key]
            reviewed_ids = {
                candidate_id
                for adjudication in adjudications
                for candidate_id in adjudication.candidate_ids
            }
            current_ids = current_record_candidates.get(record_key)
            if current_ids is None and (
                record_key[1] in current_paths
                or record_key[0] in current_traits
                or reviewed_ids & set(current_candidate_records)
            ):
                raise SelectionError(
                    f"mixed current identity for all-rejected record "
                    f"trait_id={record_key[0]!r}, record_path={record_key[1]!r}"
                )
            state = _all_rejected_record_state(
                record_key,
                adjudications,
                current_ids,
            )
            all_rejected_record_states.append(state)
            if state.status == _DEFERRED_UNCHANGED:
                deferred_all_rejected_records.add(record_key)
                if current_ids is not None:
                    current_exclusions.add(record_key)
                    deferred_all_rejected_candidate_ids.update(current_ids)
            else:
                reopened_all_rejected_records.add(record_key)
                if current_ids is not None:
                    reopened_all_rejected_candidate_ids.update(current_ids)

    return ReviewExclusions(
        records=frozenset(current_exclusions),
        reviewed_records=frozenset(reviewed_records),
        already_absent_records=frozenset(already_absent),
        all_rejected_records=frozenset(all_rejected_records),
        candidate_ids=frozenset(seen),
        excluded_candidate_ids=frozenset(excluded_candidate_ids),
        already_absent_candidate_ids=frozenset(already_absent_candidate_ids),
        all_rejected_candidate_ids=frozenset(all_rejected_candidate_ids),
        defer_unchanged_all_rejected=defer_unchanged_all_rejected,
        deferred_all_rejected_records=frozenset(deferred_all_rejected_records),
        reopened_all_rejected_records=frozenset(reopened_all_rejected_records),
        deferred_all_rejected_candidate_ids=frozenset(deferred_all_rejected_candidate_ids),
        reopened_all_rejected_candidate_ids=frozenset(reopened_all_rejected_candidate_ids),
        all_rejected_record_states=tuple(
            sorted(all_rejected_record_states, key=lambda state: state.record_key)
        ),
        repeated_all_rejected_records=repeated_all_rejected_records,
        resolved_all_rejected_histories=tuple(
            sorted(resolved_all_rejected_histories, key=lambda item: item.record_key)
        ),
        batches=tuple(batches),
    )


def _record_shard_sha256(record: TraitRecord) -> str:
    """Hash the unambiguous canonical JSON representation of the record key."""

    payload = _canonical_json([record.trait_id, record.record_path]).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _record_shard_index(record: TraitRecord, shard_count: int) -> int:
    return int(_record_shard_sha256(record), 16) % shard_count


def _shard_records(
    records: Iterable[TraitRecord], shard_count: int, shard_index: int
) -> list[TraitRecord]:
    return [record for record in records if _record_shard_index(record, shard_count) == shard_index]


def _source_slice(
    rows: Iterable[dict[str, Any]], requested_sources: Iterable[str]
) -> tuple[list[dict[str, Any]], tuple[str, ...]]:
    requested = tuple(sorted(set(requested_sources)))
    if not requested:
        return list(rows), ()
    available = {_clean(row.get("source_namespace")) for row in rows}
    missing = sorted(set(requested) - available)
    if missing:
        raise SelectionError(
            "requested source_namespace value(s) absent from exact batch: " + ", ".join(missing)
        )
    return [row for row in rows if _clean(row.get("source_namespace")) in requested], requested


def select_records(records: list[TraitRecord], max_records: int) -> list[TraitRecord]:
    """Select mandatory cases, source minima, then balanced deterministic remainder."""

    if not 1 <= max_records <= MAX_REVIEW_BATCH:
        raise SelectionError(f"--max-records must be between 1 and {MAX_REVIEW_BATCH}")
    by_source: dict[str, list[TraitRecord]] = defaultdict(list)
    for record in records:
        by_source[record.source_namespace].append(record)
    if not by_source:
        raise SelectionError("selected source slice contains no trait records")
    for source_records in by_source.values():
        source_records.sort(key=lambda record: record.key)

    selected: dict[str, TraitRecord] = {}
    for source in sorted(by_source):
        available = by_source[source]
        for record in available:
            if record.review_flags:
                selected[record.record_path] = record
        required = min(MINIMUM_PER_SOURCE, len(available))
        for record in available:
            if sum(item.source_namespace == source for item in selected.values()) >= required:
                break
            selected.setdefault(record.record_path, record)

    if len(selected) > max_records:
        special_count = sum(bool(record.review_flags) for record in selected.values())
        raise SelectionError(
            f"mandatory source minima and special cases require {len(selected):,} records "
            f"({special_count:,} special), exceeding --max-records={max_records:,}; "
            "select a smaller exact --source slice rather than dropping required review cases"
        )

    remaining = {
        source: deque(record for record in by_source[source] if record.record_path not in selected)
        for source in sorted(by_source)
    }
    while len(selected) < max_records and any(remaining.values()):
        for source in sorted(remaining):
            if len(selected) >= max_records:
                break
            if remaining[source]:
                record = remaining[source].popleft()
                selected[record.record_path] = record

    return sorted(selected.values(), key=lambda record: (record.source_namespace, *record.key))


def _flag_counts(records: Iterable[TraitRecord]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for record in records:
        counts.update(record.review_flags)
    return dict(sorted(counts.items()))


def _candidate_count(records: Iterable[TraitRecord]) -> int:
    return sum(record.candidate_count for record in records)


def _identity_set_sha256(values: Iterable[Any]) -> str:
    return hashlib.sha256(_canonical_json(sorted(values)).encode("utf-8")).hexdigest()


def _canonical_multiset_sha256(values: Iterable[Any]) -> str:
    ordered = sorted(values, key=_canonical_json)
    return hashlib.sha256(_canonical_json(ordered).encode("utf-8")).hexdigest()


def _all_rejected_adjudication_payload(
    adjudication: AllRejectedAdjudication,
) -> dict[str, Any]:
    return {
        "batch_id": adjudication.batch_id,
        "reviewed_candidates_sha256": adjudication.candidates_sha256,
        "review_manifest_sha256": adjudication.manifest_sha256,
        "reviewed_resolved_sha256": adjudication.resolved_sha256,
        "decisions_sha256": adjudication.decisions_sha256,
        "decision_rows": len(adjudication.candidate_ids),
        "candidate_ids_sha256": _identity_set_sha256(adjudication.candidate_ids),
        "resolution_bindings_sha256": _identity_set_sha256(adjudication.resolution_digests),
        "record_sha256_values_sha256": _canonical_multiset_sha256(adjudication.record_sha256s),
    }


def _all_rejected_adjudication_digest(adjudication: AllRejectedAdjudication) -> str:
    return hashlib.sha256(
        _canonical_json(_all_rejected_adjudication_payload(adjudication)).encode("utf-8")
    ).hexdigest()


def _repeated_all_rejected_record_payload(
    repeated: RepeatedAllRejectedRecord,
) -> dict[str, Any]:
    candidate_ids = {
        candidate_id
        for adjudication in repeated.adjudications
        for candidate_id in adjudication.candidate_ids
    }
    decision_rows = sum(len(item.candidate_ids) for item in repeated.adjudications)
    adjudication_digests = sorted(
        _all_rejected_adjudication_digest(item) for item in repeated.adjudications
    )
    return {
        "trait_id": repeated.trait_id,
        "record_path": repeated.record_path,
        "adjudication_count": len(repeated.adjudications),
        "decision_rows": decision_rows,
        "unique_candidate_rows": len(candidate_ids),
        "duplicate_decision_rows": decision_rows - len(candidate_ids),
        "candidate_ids_sha256": _identity_set_sha256(candidate_ids),
        "adjudication_digests": adjudication_digests,
        "adjudication_set_sha256": _identity_set_sha256(adjudication_digests),
    }


def _repeated_all_rejected_manifest(
    records: Iterable[RepeatedAllRejectedRecord],
) -> dict[str, Any]:
    repeated = tuple(sorted(records, key=lambda item: item.record_key))
    payloads = [_repeated_all_rejected_record_payload(item) for item in repeated]
    decision_rows = sum(item["decision_rows"] for item in payloads)
    unique_rows = sum(item["unique_candidate_rows"] for item in payloads)
    return {
        "trait_records": len(repeated),
        "adjudication_count": sum(item["adjudication_count"] for item in payloads),
        "decision_rows": decision_rows,
        "unique_candidate_rows": unique_rows,
        "duplicate_decision_rows": decision_rows - unique_rows,
        "record_keys_sha256": _identity_set_sha256(item.record_key for item in repeated),
        "history_sha256": hashlib.sha256(_canonical_json(payloads).encode("utf-8")).hexdigest(),
        "records": payloads,
    }


def _approved_adjudication_payload(
    adjudication: ApprovedAdjudication,
) -> dict[str, Any]:
    return {
        "batch_id": adjudication.batch_id,
        "reviewed_candidates_sha256": adjudication.candidates_sha256,
        "review_manifest_sha256": adjudication.manifest_sha256,
        "reviewed_resolved_sha256": adjudication.resolved_sha256,
        "decisions_sha256": adjudication.decisions_sha256,
        "decision_rows": len(adjudication.candidate_ids),
        "candidate_ids_sha256": _identity_set_sha256(adjudication.candidate_ids),
        "resolution_bindings_sha256": _identity_set_sha256(adjudication.resolution_digests),
        "record_sha256_values_sha256": _canonical_multiset_sha256(adjudication.record_sha256s),
        "approved_candidate_id": adjudication.approved_candidate_id,
        "approved_resolution_digest": adjudication.approved_resolution_digest,
    }


def _resolved_all_rejected_record_payload(
    history: ResolvedAllRejectedHistory,
) -> dict[str, Any]:
    rejected_payloads = sorted(
        (
            _all_rejected_adjudication_payload(adjudication)
            for adjudication in history.superseded_all_rejected_adjudications
        ),
        key=_canonical_json,
    )
    approved_payload = _approved_adjudication_payload(history.approved_adjudication)
    payload = {
        "trait_id": history.trait_id,
        "record_path": history.record_path,
        "superseded_all_rejected_adjudication_count": len(rejected_payloads),
        "superseded_all_rejected_decision_rows": sum(
            item["decision_rows"] for item in rejected_payloads
        ),
        "superseded_all_rejected_adjudications": rejected_payloads,
        "approved_adjudication": approved_payload,
    }
    payload["record_history_sha256"] = hashlib.sha256(
        _canonical_json(payload).encode("utf-8")
    ).hexdigest()
    return payload


def _resolved_all_rejected_manifest(
    histories: Iterable[ResolvedAllRejectedHistory],
) -> dict[str, Any]:
    ordered = tuple(sorted(histories, key=lambda item: item.record_key))
    payloads = [_resolved_all_rejected_record_payload(item) for item in ordered]
    all_rejected_decision_rows = sum(
        item["superseded_all_rejected_decision_rows"] for item in payloads
    )
    approved_decision_rows = sum(
        item["approved_adjudication"]["decision_rows"] for item in payloads
    )
    return {
        "trait_records": len(payloads),
        "superseded_all_rejected_adjudications": sum(
            item["superseded_all_rejected_adjudication_count"] for item in payloads
        ),
        "superseded_all_rejected_decision_rows": all_rejected_decision_rows,
        "approved_adjudications": len(payloads),
        "approved_decision_rows": approved_decision_rows,
        "record_keys_sha256": _identity_set_sha256(item.record_key for item in ordered),
        "history_sha256": hashlib.sha256(_canonical_json(payloads).encode("utf-8")).hexdigest(),
        "records": payloads,
    }


def _record_state_payload(state: AllRejectedRecordState) -> dict[str, Any]:
    return {
        "trait_id": state.trait_id,
        "record_path": state.record_path,
        "bound_record_sha256": state.bound_record_sha256,
        "current_record_sha256": state.current_record_sha256,
        "status": state.status,
        "reviewed_candidate_ids": list(state.reviewed_candidate_ids),
        "current_candidate_ids": list(state.current_candidate_ids),
    }


def _record_states_sha256(states: Iterable[AllRejectedRecordState]) -> str:
    payload = [_record_state_payload(state) for state in states]
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def _record_state_manifest(states: list[AllRejectedRecordState]) -> dict[str, Any]:
    return {
        "trait_records": len(states),
        "candidate_rows": sum(len(state.current_candidate_ids) for state in states),
        "reviewed_candidate_rows": sum(len(state.reviewed_candidate_ids) for state in states),
        "record_keys_sha256": _identity_set_sha256(state.record_key for state in states),
        "current_candidate_ids_sha256": _identity_set_sha256(
            candidate_id for state in states for candidate_id in state.current_candidate_ids
        ),
        "state_sha256": _record_states_sha256(states),
    }


def _decision_ledger_manifest(
    exclusions: ReviewExclusions,
    *,
    exact_batch_excluded: list[TraitRecord],
    exact_batch_all_rejected: list[TraitRecord],
    source_slice_excluded: list[TraitRecord],
    shard_excluded: list[TraitRecord],
) -> dict[str, Any]:
    states = list(exclusions.all_rejected_record_states)
    repeated = _repeated_all_rejected_manifest(exclusions.repeated_all_rejected_records)
    resolved_histories = _resolved_all_rejected_manifest(exclusions.resolved_all_rejected_histories)
    deferred_states = [state for state in states if state.status == _DEFERRED_UNCHANGED]
    reopened_states = [state for state in states if state.status == _REOPENED_CHANGED]
    deferred_reviewed_candidate_ids = {
        candidate_id for state in deferred_states for candidate_id in state.reviewed_candidate_ids
    }
    residual_all_rejected_records = (
        exclusions.all_rejected_records - exclusions.deferred_all_rejected_records
    )
    residual_all_rejected_candidate_ids = (
        exclusions.all_rejected_candidate_ids - deferred_reviewed_candidate_ids
    )
    return {
        "algorithm": DECISION_EXCLUSION_ALGORITHM,
        "ledger_set_sha256": exclusions.ledger_set_sha256,
        "ledger_count": len(exclusions.batches),
        "decision_row_count": exclusions.row_count,
        "unique_decided_candidate_rows": exclusions.unique_decided_candidate_count,
        "approved_count": sum(batch.decisions.approved_count for batch in exclusions.batches),
        "rejected_count": sum(batch.decisions.rejected_count for batch in exclusions.batches),
        "repeated_all_rejected": repeated,
        "resolved_all_rejected_histories": resolved_histories,
        "reviewed_batches": [
            {
                "batch_id": batch.batch_id,
                "source_batch": batch.source_batch,
                "reviewed_candidates": {
                    "path": batch.candidates_path.as_posix(),
                    "sha256": batch.candidates_sha256,
                    "candidate_rows": batch.candidate_row_count,
                    "trait_records": batch.candidate_record_count,
                },
                "review_manifest": {
                    "path": batch.manifest_path.as_posix(),
                    "sha256": batch.manifest_sha256,
                    "prior_queue_sha256": batch.prior_queue_sha256,
                    "prior_queue_matches_current": batch.prior_queue_matches_current,
                },
                "reviewed_resolved": {
                    "path": batch.resolved.path.as_posix(),
                    "sha256": batch.resolved.sha256,
                    "candidate_rows": batch.resolved.row_count,
                },
                "decisions": {
                    "path": batch.decisions.path.as_posix(),
                    "sha256": batch.decisions.sha256,
                    "row_count": batch.decisions.row_count,
                    "approved_count": batch.decisions.approved_count,
                    "rejected_count": batch.decisions.rejected_count,
                    "fully_decided_trait_records": batch.fully_decided_record_count,
                    "approved_trait_records": batch.approved_record_count,
                    "all_rejected_trait_records": batch.all_rejected_record_count,
                },
            }
            for batch in exclusions.batches
        ],
        "projection": {
            "fully_decided_candidate_rows": exclusions.unique_decided_candidate_count,
            "fully_decided_trait_records": len(exclusions.reviewed_records)
            + len(exclusions.all_rejected_records),
            "approved_candidate_rows": len(exclusions.excluded_candidate_ids)
            + len(exclusions.already_absent_candidate_ids),
            "approved_trait_records": len(exclusions.reviewed_records),
            "already_absent_candidate_rows": len(exclusions.already_absent_candidate_ids),
            "already_absent_trait_records": len(exclusions.already_absent_records),
            "current_exact_batch_excluded_candidate_rows": len(
                exclusions.excluded_candidate_ids | exclusions.deferred_all_rejected_candidate_ids
            ),
            "current_exact_batch_excluded_trait_records": len(exclusions.records),
            "stale_candidate_rows": 0,
            "stale_trait_records": 0,
        },
        "all_rejected_not_excluded": {
            "candidate_rows": len(residual_all_rejected_candidate_ids),
            "trait_records": len(residual_all_rejected_records),
            "candidate_ids_sha256": _identity_set_sha256(residual_all_rejected_candidate_ids),
            "record_keys_sha256": _identity_set_sha256(residual_all_rejected_records),
            "current_exact_batch_candidate_rows": _candidate_count(exact_batch_all_rejected),
            "current_exact_batch_trait_records": len(exact_batch_all_rejected),
        },
        "all_rejected_deferral": {
            "enabled": exclusions.defer_unchanged_all_rejected,
            "algorithm": "resolved-record-sha256-vs-current-trait-bytes-v1",
            "evaluated_state_sha256": _record_states_sha256(states),
            "evaluated_trait_records": len(states),
            "deferred_unchanged": _record_state_manifest(deferred_states),
            "reopened_changed": _record_state_manifest(reopened_states),
        },
        "exact_batch": {
            "excluded_candidate_rows": _candidate_count(exact_batch_excluded),
            "excluded_trait_records": len(exact_batch_excluded),
        },
        "source_slice": {
            "excluded_candidate_rows": _candidate_count(source_slice_excluded),
            "excluded_trait_records": len(source_slice_excluded),
        },
        "shard": {
            "excluded_candidate_rows": _candidate_count(shard_excluded),
            "excluded_trait_records": len(shard_excluded),
        },
    }


def _output_candidates(
    selected: list[TraitRecord],
    source_batch: str,
    batch_id: str,
    shard_count: int,
    shard_index: int,
) -> tuple[list[dict[str, Any]], str]:
    output: list[dict[str, Any]] = []
    for record in selected:
        for candidate in record.candidates:
            row = dict(candidate)
            row["source_batch"] = source_batch
            row["batch"] = batch_id
            row["batch_id"] = batch_id
            row["review_flags"] = list(review_flags(candidate))
            row["record_review_flags"] = list(record.review_flags)
            row["record_candidate_count"] = record.candidate_count
            row["review_shard_count"] = shard_count
            row["review_shard_index"] = shard_index
            row["record_shard_sha256"] = _record_shard_sha256(record)
            output.append(row)
    text = "".join(_canonical_json(row) + "\n" for row in output)
    return output, text


def _source_statistics(
    global_available: list[TraitRecord],
    shard_available: list[TraitRecord],
    selected: list[TraitRecord],
) -> list[dict[str, Any]]:
    global_by_source: dict[str, list[TraitRecord]] = defaultdict(list)
    shard_by_source: dict[str, list[TraitRecord]] = defaultdict(list)
    selected_by_source: dict[str, list[TraitRecord]] = defaultdict(list)
    for record in global_available:
        global_by_source[record.source_namespace].append(record)
    for record in shard_available:
        shard_by_source[record.source_namespace].append(record)
    for record in selected:
        selected_by_source[record.source_namespace].append(record)

    stats: list[dict[str, Any]] = []
    for source in sorted(global_by_source):
        source_global = global_by_source[source]
        source_available = shard_by_source[source]
        source_selected = selected_by_source[source]
        required = min(MINIMUM_PER_SOURCE, len(source_available))
        global_special = [record for record in source_global if record.review_flags]
        available_special = [record for record in source_available if record.review_flags]
        selected_special = [record for record in source_selected if record.review_flags]
        stats.append(
            {
                "source_namespace": source,
                "global_source_slice_candidate_rows": sum(
                    record.candidate_count for record in source_global
                ),
                "global_source_slice_trait_records": len(source_global),
                "global_source_slice_special_records": len(global_special),
                "global_source_slice_review_flags": _flag_counts(source_global),
                "shard_available_candidate_rows": sum(
                    record.candidate_count for record in source_available
                ),
                "shard_available_trait_records": len(source_available),
                "shard_minimum_required": required,
                "shard_selected_trait_records": len(source_selected),
                "shard_selected_candidate_rows": sum(
                    record.candidate_count for record in source_selected
                ),
                "shard_available_special_records": len(available_special),
                "shard_selected_special_records": len(selected_special),
                "shard_minimum_satisfied": len(source_selected) >= required,
                "all_shard_special_selected": {
                    record.record_path for record in available_special
                }.issubset({record.record_path for record in source_selected}),
                "shard_available_review_flags": _flag_counts(source_available),
                "shard_selected_review_flags": _flag_counts(source_selected),
            }
        )
    return stats


def _manifest_json(
    *,
    queue: Path,
    snapshot: QueueSnapshot,
    source_batch: str,
    batch_id: str,
    max_records: int,
    shard_count: int,
    shard_index: int,
    requested_sources: tuple[str, ...],
    pre_exclusion_global: list[TraitRecord],
    global_available: list[TraitRecord],
    exact_batch_excluded: list[TraitRecord],
    exact_batch_all_rejected: list[TraitRecord],
    source_slice_excluded: list[TraitRecord],
    shard_excluded: list[TraitRecord],
    exclusions: ReviewExclusions,
    shard_available: list[TraitRecord],
    selected: list[TraitRecord],
    selected_candidate_rows: int,
    candidate_sha256: str,
    source_stats: list[dict[str, Any]],
) -> dict[str, Any]:
    global_special = {record.record_path for record in global_available if record.review_flags}
    available_special = {record.record_path for record in shard_available if record.review_flags}
    selected_special = {record.record_path for record in selected if record.review_flags}
    exclusion_manifest = _decision_ledger_manifest(
        exclusions,
        exact_batch_excluded=exact_batch_excluded,
        exact_batch_all_rejected=exact_batch_all_rejected,
        source_slice_excluded=source_slice_excluded,
        shard_excluded=shard_excluded,
    )
    return {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "selection_algorithm": SELECTION_ALGORITHM,
        "record_shard_algorithm": SHARD_ALGORITHM,
        "shard_count": shard_count,
        "shard_index": shard_index,
        "batch_id": batch_id,
        "source_batch": source_batch,
        "defer_unchanged_all_rejected": exclusions.defer_unchanged_all_rejected,
        "requested_source_namespaces": list(requested_sources),
        "queue": queue.as_posix(),
        "queue_sha256": snapshot.sha256,
        "queue_total_rows": snapshot.total_rows,
        "queue_exact_batch_rows": len(snapshot.batch_rows),
        "reviewed_exclusions": exclusion_manifest,
        "pre_exclusion_source_slice_candidate_rows": _candidate_count(pre_exclusion_global),
        "pre_exclusion_source_slice_trait_records": len(pre_exclusion_global),
        "global_source_slice_candidate_rows": sum(
            record.candidate_count for record in global_available
        ),
        "global_source_slice_trait_records": len(global_available),
        "global_source_slice_special_records": len(global_special),
        "global_source_slice_review_flags": _flag_counts(global_available),
        "shard_available_candidate_rows": sum(record.candidate_count for record in shard_available),
        "shard_available_trait_records": len(shard_available),
        "shard_available_special_records": len(available_special),
        "shard_available_review_flags": _flag_counts(shard_available),
        "shard_selected_trait_records": len(selected),
        "shard_selected_candidate_rows": selected_candidate_rows,
        "shard_selected_special_records": len(selected_special),
        "shard_selected_review_flags": _flag_counts(selected),
        "max_records": max_records,
        "minimum_per_source_within_shard": MINIMUM_PER_SOURCE,
        "candidate_jsonl_sha256": candidate_sha256,
        "invariants": {
            "shard_is_nonempty": bool(shard_available),
            "unique_selected_record_groups_within_shard": len(
                {record.record_path for record in selected}
            )
            == len(selected),
            "every_available_record_matches_shard": all(
                _record_shard_index(record, shard_count) == shard_index
                for record in shard_available
            ),
            "all_selected_records_are_available_in_shard": {
                record.key for record in selected
            }.issubset({record.key for record in shard_available}),
            "no_one_approved_reviewed_record_in_residual_queue": not (
                {record.key for record in global_available} & exclusions.records
            ),
            "every_excluded_source_slice_record_is_approved_or_deferred_unchanged": {
                record.key for record in source_slice_excluded
            }.issubset(exclusions.reviewed_records | exclusions.deferred_all_rejected_records),
            "all_non_deferred_all_rejected_source_slice_records_remain_in_residual_queue": {
                record.key
                for record in pre_exclusion_global
                if record.key in exclusions.all_rejected_records
                and record.key not in exclusions.deferred_all_rejected_records
            }.issubset({record.key for record in global_available}),
            "all_deferred_unchanged_source_slice_records_are_absent_from_residual_queue": not (
                {
                    record.key
                    for record in pre_exclusion_global
                    if record.key in exclusions.deferred_all_rejected_records
                }
                & {record.key for record in global_available}
            ),
            "all_reopened_changed_source_slice_records_remain_in_residual_queue": {
                record.key
                for record in pre_exclusion_global
                if record.key in exclusions.reopened_all_rejected_records
            }.issubset({record.key for record in global_available}),
            "all_rejected_deferral_states_partition_when_enabled": (
                not exclusions.defer_unchanged_all_rejected
                and not exclusions.all_rejected_record_states
                and not exclusions.deferred_all_rejected_records
                and not exclusions.reopened_all_rejected_records
            )
            or (
                exclusions.defer_unchanged_all_rejected
                and exclusions.deferred_all_rejected_records.isdisjoint(
                    exclusions.reopened_all_rejected_records
                )
                and (
                    exclusions.deferred_all_rejected_records
                    | exclusions.reopened_all_rejected_records
                )
                == exclusions.all_rejected_records
                and len(exclusions.all_rejected_record_states)
                == len(exclusions.all_rejected_records)
            ),
            "all_deferred_and_reopened_record_hash_classifications_are_exact": all(
                (state.status == _DEFERRED_UNCHANGED)
                == (state.bound_record_sha256 == state.current_record_sha256)
                for state in exclusions.all_rejected_record_states
            ),
            "all_repeated_review_histories_are_coalesced_all_rejected": all(
                len(repeated.adjudications) > 1
                and repeated.record_key in exclusions.all_rejected_records
                for repeated in exclusions.repeated_all_rejected_records
            )
            and len({repeated.record_key for repeated in exclusions.repeated_all_rejected_records})
            == len(exclusions.repeated_all_rejected_records),
            "all_resolved_all_rejected_histories_are_terminal_approved_exclusions": all(
                history.superseded_all_rejected_adjudications
                and history.record_key in exclusions.reviewed_records
                and history.record_key not in exclusions.all_rejected_records
                and history.record_key not in exclusions.deferred_all_rejected_records
                and history.record_key not in exclusions.reopened_all_rejected_records
                for history in exclusions.resolved_all_rejected_histories
            )
            and len({history.record_key for history in exclusions.resolved_all_rejected_histories})
            == len(exclusions.resolved_all_rejected_histories),
            "all_selected_candidate_alternatives_retained": selected_candidate_rows
            == sum(record.candidate_count for record in selected),
            "within_record_cap": len(selected) <= max_records <= MAX_REVIEW_BATCH,
            "shard_source_minima_satisfied": all(
                stat["shard_minimum_satisfied"] for stat in source_stats
            ),
            "all_shard_special_cases_selected": available_special <= selected_special,
        },
        "downstream_requirements": {
            "at_most_one_approved_candidate_per_record": True,
            "all_alternatives_must_receive_an_explicit_review_decision": True,
        },
        "sources": source_stats,
    }


def _manifest_tsv(
    *,
    batch_id: str,
    source_batch: str,
    queue_sha256: str,
    candidate_sha256: str,
    shard_count: int,
    shard_index: int,
    pre_exclusion_global: list[TraitRecord],
    source_slice_excluded: list[TraitRecord],
    shard_excluded: list[TraitRecord],
    exclusions: ReviewExclusions,
    source_stats: list[dict[str, Any]],
) -> str:
    all_rejected_deferral_sha256 = _record_states_sha256(exclusions.all_rejected_record_states)
    repeated = _repeated_all_rejected_manifest(exclusions.repeated_all_rejected_records)
    resolved_histories = _resolved_all_rejected_manifest(exclusions.resolved_all_rejected_histories)
    deferred_reviewed_candidate_ids = {
        candidate_id
        for state in exclusions.all_rejected_record_states
        if state.status == _DEFERRED_UNCHANGED
        for candidate_id in state.reviewed_candidate_ids
    }
    residual_all_rejected_candidate_ids = (
        exclusions.all_rejected_candidate_ids - deferred_reviewed_candidate_ids
    )
    residual_all_rejected_records = (
        exclusions.all_rejected_records - exclusions.deferred_all_rejected_records
    )
    global_flag_totals: Counter[str] = Counter()
    shard_available_flag_totals: Counter[str] = Counter()
    shard_selected_flag_totals: Counter[str] = Counter()
    for stat in source_stats:
        global_flag_totals.update(stat["global_source_slice_review_flags"])
        shard_available_flag_totals.update(stat["shard_available_review_flags"])
        shard_selected_flag_totals.update(stat["shard_selected_review_flags"])
    total = {
        "source_namespace": "(TOTAL)",
        "global_source_slice_candidate_rows": sum(
            stat["global_source_slice_candidate_rows"] for stat in source_stats
        ),
        "global_source_slice_trait_records": sum(
            stat["global_source_slice_trait_records"] for stat in source_stats
        ),
        "global_source_slice_special_records": sum(
            stat["global_source_slice_special_records"] for stat in source_stats
        ),
        "global_source_slice_review_flags": dict(sorted(global_flag_totals.items())),
        "shard_available_candidate_rows": sum(
            stat["shard_available_candidate_rows"] for stat in source_stats
        ),
        "shard_available_trait_records": sum(
            stat["shard_available_trait_records"] for stat in source_stats
        ),
        "shard_minimum_required": sum(stat["shard_minimum_required"] for stat in source_stats),
        "shard_selected_trait_records": sum(
            stat["shard_selected_trait_records"] for stat in source_stats
        ),
        "shard_selected_candidate_rows": sum(
            stat["shard_selected_candidate_rows"] for stat in source_stats
        ),
        "shard_available_special_records": sum(
            stat["shard_available_special_records"] for stat in source_stats
        ),
        "shard_selected_special_records": sum(
            stat["shard_selected_special_records"] for stat in source_stats
        ),
        "shard_minimum_satisfied": all(stat["shard_minimum_satisfied"] for stat in source_stats),
        "all_shard_special_selected": all(
            stat["all_shard_special_selected"] for stat in source_stats
        ),
        "shard_available_review_flags": dict(sorted(shard_available_flag_totals.items())),
        "shard_selected_review_flags": dict(sorted(shard_selected_flag_totals.items())),
    }
    rows = [*source_stats, total]
    stream = StringIO(newline="")
    writer = csv.DictWriter(
        stream, fieldnames=_MANIFEST_COLUMNS, delimiter="\t", lineterminator="\n"
    )
    writer.writeheader()
    for stat in rows:
        writer.writerow(
            {
                "schema_version": MANIFEST_SCHEMA_VERSION,
                "selection_algorithm": SELECTION_ALGORITHM,
                "record_shard_algorithm": SHARD_ALGORITHM,
                "batch_id": batch_id,
                "source_batch": source_batch,
                "queue_sha256": queue_sha256,
                "decision_ledger_set_sha256": exclusions.ledger_set_sha256 or "",
                "decision_ledger_count": len(exclusions.batches),
                "decision_row_count": exclusions.row_count,
                "unique_decided_candidate_rows": exclusions.unique_decided_candidate_count,
                "repeated_all_rejected_trait_records": repeated["trait_records"],
                "repeated_all_rejected_adjudications": repeated["adjudication_count"],
                "repeated_all_rejected_decision_rows": repeated["decision_rows"],
                "repeated_all_rejected_duplicate_decision_rows": repeated[
                    "duplicate_decision_rows"
                ],
                "repeated_all_rejected_history_sha256": repeated["history_sha256"],
                "resolved_all_rejected_trait_records": resolved_histories["trait_records"],
                "resolved_all_rejected_superseded_adjudications": resolved_histories[
                    "superseded_all_rejected_adjudications"
                ],
                "resolved_all_rejected_superseded_decision_rows": resolved_histories[
                    "superseded_all_rejected_decision_rows"
                ],
                "resolved_all_rejected_approved_adjudications": resolved_histories[
                    "approved_adjudications"
                ],
                "resolved_all_rejected_approved_decision_rows": resolved_histories[
                    "approved_decision_rows"
                ],
                "resolved_all_rejected_history_sha256": resolved_histories["history_sha256"],
                "defer_unchanged_all_rejected": str(
                    exclusions.defer_unchanged_all_rejected
                ).lower(),
                "all_rejected_deferral_sha256": all_rejected_deferral_sha256,
                "deferred_unchanged_candidate_rows": len(
                    exclusions.deferred_all_rejected_candidate_ids
                ),
                "deferred_unchanged_trait_records": len(exclusions.deferred_all_rejected_records),
                "reopened_changed_candidate_rows": len(
                    exclusions.reopened_all_rejected_candidate_ids
                ),
                "reopened_changed_trait_records": len(exclusions.reopened_all_rejected_records),
                "already_absent_reviewed_candidate_rows": len(
                    exclusions.already_absent_candidate_ids
                ),
                "already_absent_reviewed_trait_records": len(exclusions.already_absent_records),
                "all_rejected_not_excluded_candidate_rows": len(
                    residual_all_rejected_candidate_ids
                ),
                "all_rejected_not_excluded_trait_records": len(residual_all_rejected_records),
                "all_rejected_record_keys_sha256": _identity_set_sha256(
                    residual_all_rejected_records
                ),
                "all_rejected_candidate_ids_sha256": _identity_set_sha256(
                    residual_all_rejected_candidate_ids
                ),
                "stale_reviewed_candidate_rows": 0,
                "stale_reviewed_trait_records": 0,
                "pre_exclusion_source_slice_candidate_rows": _candidate_count(pre_exclusion_global),
                "pre_exclusion_source_slice_trait_records": len(pre_exclusion_global),
                "excluded_source_slice_candidate_rows": _candidate_count(source_slice_excluded),
                "excluded_source_slice_trait_records": len(source_slice_excluded),
                "excluded_shard_candidate_rows": _candidate_count(shard_excluded),
                "excluded_shard_trait_records": len(shard_excluded),
                "candidate_jsonl_sha256": candidate_sha256,
                "shard_count": shard_count,
                "shard_index": shard_index,
                **stat,
                "shard_minimum_satisfied": str(stat["shard_minimum_satisfied"]).lower(),
                "all_shard_special_selected": str(stat["all_shard_special_selected"]).lower(),
                "global_source_slice_review_flags": _canonical_json(
                    stat["global_source_slice_review_flags"]
                ),
                "shard_available_review_flags": _canonical_json(
                    stat["shard_available_review_flags"]
                ),
                "shard_selected_review_flags": _canonical_json(stat["shard_selected_review_flags"]),
            }
        )
    return stream.getvalue()


def _output_paths(args: argparse.Namespace) -> tuple[Path, Path, Path]:
    stem = args.batch_id
    return (
        args.out or DEFAULT_OUTPUT_DIR / f"{stem}.candidates.jsonl",
        args.manifest_tsv or DEFAULT_OUTPUT_DIR / f"{stem}.manifest.tsv",
        args.manifest_json or DEFAULT_OUTPUT_DIR / f"{stem}.manifest.json",
    )


def _validate_output_paths(inputs: Iterable[Path], paths: Iterable[Path]) -> None:
    resolved = [path.resolve() for path in paths]
    if len(set(resolved)) != len(resolved):
        raise SelectionError("candidate and manifest output paths must be distinct")
    resolved_inputs = {path.resolve() for path in inputs}
    if resolved_inputs & set(resolved):
        raise SelectionError("an output path must not overwrite an input candidate ledger")


def _atomic_write_many(outputs: Iterable[tuple[Path, str]]) -> None:
    staged: list[tuple[Path, Path]] = []
    try:
        for path, content in outputs:
            path.parent.mkdir(parents=True, exist_ok=True)
            descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
            temporary = Path(temporary_name)
            staged.append((temporary, path))
            with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
        for temporary, path in staged:
            os.replace(temporary, path)
    finally:
        for temporary, _ in staged:
            temporary.unlink(missing_ok=True)


def _reviewed_artifact_quadruples(
    args: argparse.Namespace,
) -> tuple[tuple[Path, Path, Path, Path], ...]:
    counts = {
        "--exclude-reviewed-candidates": len(args.exclude_reviewed_candidates),
        "--exclude-reviewed-manifest": len(args.exclude_reviewed_manifests),
        "--exclude-reviewed-resolved": len(args.exclude_reviewed_resolved),
        "--exclude-decisions": len(args.exclude_decisions),
    }
    if len(set(counts.values())) != 1:
        detail = ", ".join(f"{flag}={count}" for flag, count in counts.items())
        raise SelectionError(
            "reviewed exclusions require one candidates + manifest + resolved + decisions "
            "quadruple "
            f"per prior batch ({detail})"
        )
    return tuple(
        zip(
            args.exclude_reviewed_candidates,
            args.exclude_reviewed_manifests,
            args.exclude_reviewed_resolved,
            args.exclude_decisions,
            strict=True,
        )
    )


def run(args: argparse.Namespace) -> int:
    source_batch = _clean(args.batch)
    if not source_batch:
        raise SelectionError("--batch must be non-empty")
    if not _BATCH_ID.fullmatch(args.batch_id):
        raise SelectionError(
            "--batch-id must be 1-128 characters using letters, digits, '.', '_', or '-'"
        )
    requested_sources = tuple(_clean(source) or "" for source in args.sources)
    if any(not source for source in requested_sources):
        raise SelectionError("--source values must be non-empty")
    _validate_shard_pair(args.shard_count, args.shard_index)
    reviewed_artifacts = _reviewed_artifact_quadruples(args)

    snapshot = _read_queue(args.queue, source_batch)
    exact_batch_records = _trait_records(snapshot.batch_rows)
    sliced_rows, normalized_sources = _source_slice(snapshot.batch_rows, requested_sources)
    pre_exclusion_global = _trait_records(sliced_rows)
    exclusions = _review_exclusions(
        exact_batch_records,
        reviewed_artifacts,
        current_queue_sha256=snapshot.sha256,
        current_source_batch=source_batch,
        defer_unchanged_all_rejected=args.defer_unchanged_all_rejected,
    )
    exact_batch_excluded = [
        record for record in exact_batch_records if record.key in exclusions.records
    ]
    exact_batch_all_rejected = [
        record
        for record in exact_batch_records
        if record.key in exclusions.all_rejected_records
        and record.key not in exclusions.deferred_all_rejected_records
    ]
    source_slice_excluded = [
        record for record in pre_exclusion_global if record.key in exclusions.records
    ]
    global_available = [
        record for record in pre_exclusion_global if record.key not in exclusions.records
    ]
    if not global_available:
        raise SelectionError(
            "no residual trait records remain in the selected source slice after "
            "excluding fully reviewed record groups"
        )
    shard_excluded = [
        record
        for record in source_slice_excluded
        if _record_shard_index(record, args.shard_count) == args.shard_index
    ]
    shard_available = _shard_records(global_available, args.shard_count, args.shard_index)
    if not shard_available:
        raise SelectionError(
            f"shard {args.shard_index} of {args.shard_count} contains no trait records "
            "in the selected source slice"
        )
    selected = select_records(shard_available, args.max_records)
    output_rows, candidate_text = _output_candidates(
        selected,
        source_batch,
        args.batch_id,
        args.shard_count,
        args.shard_index,
    )
    expected_candidate_ids = {
        str(candidate["candidate_id"]) for record in selected for candidate in record.candidates
    }
    observed_candidate_ids = {str(row["candidate_id"]) for row in output_rows}
    if observed_candidate_ids != expected_candidate_ids or len(output_rows) != len(
        expected_candidate_ids
    ):
        raise SelectionError("internal error: selected candidate alternatives were lost")
    candidate_sha256 = hashlib.sha256(candidate_text.encode("utf-8")).hexdigest()
    source_stats = _source_statistics(global_available, shard_available, selected)
    manifest = _manifest_json(
        queue=args.queue,
        snapshot=snapshot,
        source_batch=source_batch,
        batch_id=args.batch_id,
        max_records=args.max_records,
        shard_count=args.shard_count,
        shard_index=args.shard_index,
        requested_sources=normalized_sources,
        pre_exclusion_global=pre_exclusion_global,
        global_available=global_available,
        exact_batch_excluded=exact_batch_excluded,
        exact_batch_all_rejected=exact_batch_all_rejected,
        source_slice_excluded=source_slice_excluded,
        shard_excluded=shard_excluded,
        exclusions=exclusions,
        shard_available=shard_available,
        selected=selected,
        selected_candidate_rows=len(output_rows),
        candidate_sha256=candidate_sha256,
        source_stats=source_stats,
    )
    if not all(manifest["invariants"].values()):
        failed = [key for key, value in manifest["invariants"].items() if not value]
        raise SelectionError("selection invariant failed: " + ", ".join(failed))
    manifest_json = json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    manifest_tsv = _manifest_tsv(
        batch_id=args.batch_id,
        source_batch=source_batch,
        queue_sha256=snapshot.sha256,
        candidate_sha256=candidate_sha256,
        shard_count=args.shard_count,
        shard_index=args.shard_index,
        pre_exclusion_global=pre_exclusion_global,
        source_slice_excluded=source_slice_excluded,
        shard_excluded=shard_excluded,
        exclusions=exclusions,
        source_stats=source_stats,
    )
    out, tsv_path, json_path = _output_paths(args)
    reviewed_input_paths = tuple(path for triplet in reviewed_artifacts for path in triplet)
    _validate_output_paths((args.queue, *reviewed_input_paths), (out, tsv_path, json_path))

    action = "selected" if args.apply else "would select"
    print(
        f"{action} {len(selected):,}/{len(shard_available):,} unique trait records "
        f"in shard {args.shard_index}/{args.shard_count} from "
        f"{len(global_available):,} global source-slice records "
        f"after excluding {len(source_slice_excluded):,} fully reviewed records "
        f"({len(exclusions.deferred_all_rejected_records):,} unchanged all-rejected "
        f"deferred; {len(exclusions.reopened_all_rejected_records):,} changed reopened) "
        f"({len(output_rows):,} candidate alternatives); "
        f"queue_sha256={snapshot.sha256}"
    )
    if not args.apply:
        print("dry run: no output files written; pass --apply to install the batch")
        return 0
    _atomic_write_many(
        ((out, candidate_text), (tsv_path, manifest_tsv), (json_path, manifest_json))
    )
    print(f"wrote candidates: {out}")
    print(f"wrote manifest TSV: {tsv_path}")
    print(f"wrote manifest JSON: {json_path}")
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--queue", type=Path, required=True, help="candidate JSONL ledger")
    parser.add_argument("--batch", default="ready-local", help="exact input batch label")
    parser.add_argument("--batch-id", required=True, help="explicit output review-batch label")
    parser.add_argument(
        "--source",
        dest="sources",
        action="append",
        default=[],
        help="exact source_namespace slice; repeat as needed (default: every source)",
    )
    parser.add_argument(
        "--max-records",
        type=int,
        default=MAX_REVIEW_BATCH,
        help=f"selection cap, never above {MAX_REVIEW_BATCH}",
    )
    parser.add_argument(
        "--shard-count",
        type=int,
        default=1,
        help="number of deterministic record shards (default: 1)",
    )
    parser.add_argument(
        "--shard-index",
        type=int,
        default=0,
        help="zero-based deterministic record shard to select (default: 0)",
    )
    parser.add_argument(
        "--exclude-reviewed-candidates",
        dest="exclude_reviewed_candidates",
        action="append",
        type=Path,
        default=[],
        help=(
            "prior selected candidate JSONL snapshot; repeat with its manifest/resolved/decisions"
        ),
    )
    parser.add_argument(
        "--exclude-reviewed-manifest",
        dest="exclude_reviewed_manifests",
        action="append",
        type=Path,
        default=[],
        help="manifest that content-addresses the corresponding reviewed candidates",
    )
    parser.add_argument(
        "--exclude-reviewed-resolved",
        dest="exclude_reviewed_resolved",
        action="append",
        type=Path,
        default=[],
        help=(
            "exact resolved JSONL snapshot whose recomputed resolution digests bind the "
            "corresponding decisions"
        ),
    )
    parser.add_argument(
        "--exclude-decisions",
        dest="exclude_decisions",
        action="append",
        type=Path,
        default=[],
        help=(
            "prior JSONL decision ledger paired by argument order with reviewed "
            "candidates, manifest, and resolved rows; repeat all four options for "
            "another prior batch. Repeated complete all-REJECTED histories coalesce; "
            "exactly one complete approved adjudication may terminally supersede them, "
            "while a second approved adjudication fails closed"
        ),
    )
    parser.add_argument(
        "--defer-unchanged-all-rejected",
        action="store_true",
        help=(
            "exclude a fully reviewed all-REJECTED group only while its current "
            "data/traits YAML bytes exactly match the single record_sha256 bound by "
            "every resolved alternative; this does not detect source/gate/resolver "
            "changes, so omit it after any such change (default: reopen all rejected "
            "groups)"
        ),
    )
    parser.add_argument("--out", type=Path, help="selected candidate JSONL path")
    parser.add_argument("--manifest-tsv", type=Path, help="source-count manifest TSV")
    parser.add_argument("--manifest-json", type=Path, help="machine-readable manifest JSON")
    parser.add_argument("--apply", action="store_true", help="atomically write outputs")
    return parser


def main(argv: list[str] | None = None) -> int:
    try:
        return run(_parser().parse_args(argv))
    except SelectionError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
