#!/usr/bin/env python3
"""Validate and combine partitioned UniProt review decisions.

This command joins curator decision partitions to one immutable resolved-candidate
snapshot and its blank review TSV.  Every decision must carry the exact
``resolution_digest`` of its resolved evidence row.  It fails closed unless every
candidate has exactly one explicit decision and every trait-record group has either one
approved primary candidate or no approved candidate.  The command never opens a trait
record and refuses artifact paths inside ``data/traits``.

Dry-run validation is the default.  Pass ``--apply`` to atomically replace the canonical
decision JSONL and completed approval TSV after every input and cross-file invariant has
passed.
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
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from io import StringIO
from pathlib import Path, PurePosixPath
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
TRAITS_ROOT = REPO_ROOT / "data" / "traits"

_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_REVIEW_DATE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
_DECISIONS = frozenset({"APPROVED", "REJECTED"})
_REVIEW_FIELDS = ("decision", "reviewer", "reviewed_at", "review_notes")
_BOUND_TSV_FIELDS = (
    "resolution_digest",
    "trait_id",
    "record_path",
    "source_namespace",
    "mapping_method",
    "evidence_source",
    "source_release",
    "uniprot_release",
)


class FinalizationError(RuntimeError):
    """Review artifacts cannot be finalized without violating an invariant."""


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    trait_id: str
    record_path: str
    row: dict[str, Any]

    @property
    def record_key(self) -> tuple[str, str]:
        return self.trait_id, self.record_path


@dataclass(frozen=True)
class Decision:
    candidate_id: str
    resolution_digest: str
    decision: str
    primary_review_candidate_id: str | None
    trait_id: str
    record_path: str
    reviewer: str
    reviewed_at: str
    review_notes: str

    def canonical_row(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "decision": self.decision,
            "primary_review_candidate_id": self.primary_review_candidate_id,
            "record_key": {
                "record_path": self.record_path,
                "trait_id": self.trait_id,
            },
            "resolution_digest": self.resolution_digest,
            "review_notes": self.review_notes,
            "reviewed_at": self.reviewed_at,
            "reviewer": self.reviewer,
        }


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _exact_text(value: Any, *, subject: str, field: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise FinalizationError(f"{subject} has invalid exact non-empty {field}")
    return value


def _record_path(value: Any, *, subject: str) -> str:
    text = _exact_text(value, subject=subject, field="record_path")
    path = PurePosixPath(text)
    if (
        "\\" in text
        or "\x00" in text
        or path.is_absolute()
        or ".." in path.parts
        or path.as_posix() != text
        or path.suffix not in {".yaml", ".yml"}
    ):
        raise FinalizationError(
            f"{subject} has unsafe record_path {text!r}; expected a normalized relative "
            "POSIX YAML path"
        )
    return text


def _read_jsonl(path: Path, *, kind: str) -> list[tuple[int, dict[str, Any]]]:
    if not path.is_file():
        raise FinalizationError(f"{kind} does not exist: {path}")
    rows: list[tuple[int, dict[str, Any]]] = []
    try:
        with path.open(encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, 1):
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise FinalizationError(
                        f"{path}:{line_number}: invalid JSON in {kind}: {exc}"
                    ) from exc
                if not isinstance(row, dict):
                    raise FinalizationError(
                        f"{path}:{line_number}: {kind} row is not a JSON object"
                    )
                rows.append((line_number, row))
    except UnicodeDecodeError as exc:
        raise FinalizationError(f"{path}: {kind} is not valid UTF-8: {exc}") from exc
    if not rows:
        raise FinalizationError(f"{kind} contains no rows: {path}")
    return rows


def _candidate_snapshot(path: Path) -> dict[str, Candidate]:
    candidates: dict[str, Candidate] = {}
    trait_paths: dict[str, str] = {}
    path_identities: dict[str, tuple[str, str]] = {}
    for line_number, row in _read_jsonl(path, kind="resolved candidate snapshot"):
        subject = f"{path}:{line_number}: candidate"
        candidate_id = _exact_text(row.get("candidate_id"), subject=subject, field="candidate_id")
        trait_id = _exact_text(row.get("trait_id"), subject=subject, field="trait_id")
        record_path = _record_path(row.get("record_path"), subject=subject)
        source = _exact_text(row.get("source_namespace"), subject=subject, field="source_namespace")
        if candidate_id in candidates:
            raise FinalizationError(
                f"{path}:{line_number}: duplicate candidate_id {candidate_id!r}"
            )
        previous_path = trait_paths.setdefault(trait_id, record_path)
        if previous_path != record_path:
            raise FinalizationError(
                f"trait_id {trait_id!r} maps to multiple record paths: "
                f"{previous_path!r}, {record_path!r}"
            )
        previous_identity = path_identities.setdefault(record_path, (trait_id, source))
        if previous_identity != (trait_id, source):
            raise FinalizationError(
                f"record_path {record_path!r} has conflicting trait/source identities"
            )
        digest = row.get("resolution_digest")
        if not isinstance(digest, str) or not _SHA256.fullmatch(digest):
            raise FinalizationError(f"{subject} lacks a valid resolution_digest")
        expected_digest = hashlib.sha256(
            _canonical_json(
                {key: value for key, value in row.items() if key != "resolution_digest"}
            ).encode("utf-8")
        ).hexdigest()
        if digest != expected_digest:
            raise FinalizationError(
                f"{subject} has stale resolution_digest {digest}; expected {expected_digest}"
            )
        candidates[candidate_id] = Candidate(candidate_id, trait_id, record_path, row)
    return candidates


def _review_date(value: Any, *, subject: str) -> str:
    text = _exact_text(value, subject=subject, field="reviewed_at")
    if not _REVIEW_DATE.fullmatch(text):
        raise FinalizationError(f"{subject} reviewed_at must have form YYYY-MM-DD")
    try:
        date.fromisoformat(text)
    except ValueError as exc:
        raise FinalizationError(f"{subject} has invalid reviewed_at date {text!r}") from exc
    return text


def _decision_partitions(
    paths: list[Path], candidates: dict[str, Candidate]
) -> dict[str, Decision]:
    decisions: dict[str, Decision] = {}
    for path in paths:
        for line_number, row in _read_jsonl(path, kind="decision partition"):
            subject = f"{path}:{line_number}: decision"
            candidate_id = _exact_text(
                row.get("candidate_id"), subject=subject, field="candidate_id"
            )
            if candidate_id in decisions:
                raise FinalizationError(
                    f"{subject} duplicates candidate_id {candidate_id!r} across decision partitions"
                )
            candidate = candidates.get(candidate_id)
            if candidate is None:
                raise FinalizationError(
                    f"{subject} refers to unknown candidate_id {candidate_id!r}"
                )
            decision = row.get("decision")
            if decision not in _DECISIONS:
                raise FinalizationError(
                    f"{subject} has decision {decision!r}; expected exactly APPROVED or REJECTED"
                )
            record_key = row.get("record_key")
            if not isinstance(record_key, dict):
                raise FinalizationError(f"{subject} lacks record_key")
            trait_id = _exact_text(
                record_key.get("trait_id"), subject=subject, field="record_key.trait_id"
            )
            record_path = _record_path(record_key.get("record_path"), subject=subject)
            if (trait_id, record_path) != candidate.record_key:
                raise FinalizationError(
                    f"{subject} has stale record_key {(trait_id, record_path)!r}; expected "
                    f"{candidate.record_key!r}"
                )
            resolution_digest = row.get("resolution_digest")
            if not isinstance(resolution_digest, str) or not _SHA256.fullmatch(resolution_digest):
                raise FinalizationError(f"{subject} lacks a valid resolution_digest")
            expected_digest = str(candidate.row["resolution_digest"])
            if resolution_digest != expected_digest:
                raise FinalizationError(
                    f"{subject} has stale resolution_digest {resolution_digest!r}; "
                    f"expected {expected_digest!r}"
                )
            primary = row.get("primary_review_candidate_id")
            if primary is not None:
                primary = _exact_text(primary, subject=subject, field="primary_review_candidate_id")
            reviewer = _exact_text(row.get("reviewer"), subject=subject, field="reviewer")
            reviewed_at = _review_date(row.get("reviewed_at"), subject=subject)
            notes = _exact_text(row.get("review_notes"), subject=subject, field="review_notes")
            decisions[candidate_id] = Decision(
                candidate_id=candidate_id,
                resolution_digest=resolution_digest,
                decision=decision,
                primary_review_candidate_id=primary,
                trait_id=trait_id,
                record_path=record_path,
                reviewer=reviewer,
                reviewed_at=reviewed_at,
                review_notes=notes,
            )

    missing = sorted(set(candidates) - set(decisions))
    if missing:
        raise FinalizationError(
            f"decision partitions do not cover {len(missing)} candidate(s): "
            + ", ".join(missing[:5])
        )
    if len(decisions) != len(candidates):
        # Unknown rows are rejected while parsing; this is a defensive exact-set check.
        raise FinalizationError("decision partitions do not exactly cover the candidate snapshot")
    return decisions


def _validate_record_groups(
    candidates: dict[str, Candidate], decisions: dict[str, Decision]
) -> tuple[int, int]:
    grouped: dict[tuple[str, str], list[str]] = defaultdict(list)
    for candidate_id, candidate in candidates.items():
        grouped[candidate.record_key].append(candidate_id)

    approved_groups = 0
    all_rejected_groups = 0
    for record_key, candidate_ids in grouped.items():
        approved = sorted(
            candidate_id
            for candidate_id in candidate_ids
            if decisions[candidate_id].decision == "APPROVED"
        )
        if len(approved) > 1:
            raise FinalizationError(
                f"record {record_key!r} has multiple approved candidates: {', '.join(approved)}"
            )
        if approved:
            expected_primary = approved[0]
            bad_primary = sorted(
                candidate_id
                for candidate_id in candidate_ids
                if decisions[candidate_id].primary_review_candidate_id != expected_primary
            )
            if bad_primary:
                raise FinalizationError(
                    f"record {record_key!r} primary_review_candidate_id must be "
                    f"{expected_primary!r} for every candidate; mismatches: "
                    + ", ".join(bad_primary)
                )
            approved_groups += 1
        else:
            primaries = {
                decisions[candidate_id].primary_review_candidate_id
                for candidate_id in candidate_ids
            }
            if len(primaries) != 1:
                raise FinalizationError(
                    f"all-rejected record {record_key!r} must use one consistent "
                    "primary_review_candidate_id (or all null)"
                )
            sole_primary = next(iter(primaries))
            if sole_primary is not None and sole_primary not in candidate_ids:
                raise FinalizationError(
                    f"all-rejected record {record_key!r} has out-of-group "
                    f"primary_review_candidate_id {sole_primary!r}"
                )
            all_rejected_groups += 1
    return approved_groups, all_rejected_groups


def _tsv_text(path: Path, candidates: dict[str, Candidate], decisions: dict[str, Decision]) -> str:
    if not path.is_file():
        raise FinalizationError(f"review TSV does not exist: {path}")
    try:
        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            fieldnames = reader.fieldnames
            if not fieldnames:
                raise FinalizationError(f"review TSV has no header: {path}")
            if len(fieldnames) != len(set(fieldnames)):
                raise FinalizationError(f"review TSV has duplicate column names: {path}")
            required = {"candidate_id", *_BOUND_TSV_FIELDS, *_REVIEW_FIELDS}
            missing_columns = sorted(required - set(fieldnames))
            if missing_columns:
                raise FinalizationError(
                    f"review TSV lacks required columns: {', '.join(missing_columns)}"
                )
            rows = list(reader)
    except UnicodeDecodeError as exc:
        raise FinalizationError(f"review TSV is not valid UTF-8: {path}: {exc}") from exc

    seen: set[str] = set()
    completed: list[dict[str, str]] = []
    for line_number, row in enumerate(rows, 2):
        if None in row or any(value is None for value in row.values()):
            raise FinalizationError(f"{path}:{line_number}: malformed review TSV row")
        subject = f"{path}:{line_number}: review row"
        candidate_id = _exact_text(row.get("candidate_id"), subject=subject, field="candidate_id")
        if candidate_id in seen:
            raise FinalizationError(f"{subject} duplicates candidate_id {candidate_id!r}")
        seen.add(candidate_id)
        candidate = candidates.get(candidate_id)
        if candidate is None:
            raise FinalizationError(f"{subject} refers to unknown candidate_id {candidate_id!r}")
        for field in _BOUND_TSV_FIELDS:
            expected = candidate.row.get(field)
            expected_text = "" if expected is None else str(expected)
            if row[field] != expected_text:
                raise FinalizationError(
                    f"{subject} has stale {field}={row[field]!r}; expected {expected_text!r}"
                )
        for field in _REVIEW_FIELDS:
            if row[field] != "":
                raise FinalizationError(f"{subject} must have blank {field} before finalization")
        decision = decisions[candidate_id]
        completed_row = dict(row)
        completed_row.update(
            {
                "decision": decision.decision,
                "reviewer": decision.reviewer,
                "reviewed_at": decision.reviewed_at,
                "review_notes": decision.review_notes,
            }
        )
        completed.append(completed_row)

    missing_ids = sorted(set(candidates) - seen)
    if missing_ids:
        raise FinalizationError(
            f"review TSV does not contain {len(missing_ids)} candidate(s): "
            + ", ".join(missing_ids[:5])
        )
    if len(seen) != len(candidates):
        raise FinalizationError("review TSV candidate IDs do not exactly match the snapshot")

    buffer = StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(completed)
    return buffer.getvalue()


def _decisions_text(decisions: dict[str, Decision]) -> str:
    return "".join(
        _canonical_json(decisions[candidate_id].canonical_row()) + "\n"
        for candidate_id in sorted(decisions)
    )


def _inside(path: Path, directory: Path) -> bool:
    try:
        path.resolve().relative_to(directory.resolve())
    except ValueError:
        return False
    return True


def _validate_paths(
    candidates: Path,
    review_tsv: Path,
    partitions: list[Path],
    decisions_out: Path,
    approved_out: Path,
) -> None:
    inputs = [candidates, review_tsv, *partitions]
    outputs = [decisions_out, approved_out]
    input_resolved = [path.resolve() for path in inputs]
    output_resolved = [path.resolve() for path in outputs]
    if len(input_resolved) != len(set(input_resolved)):
        raise FinalizationError("candidate, review, and decision input paths must be distinct")
    if len(output_resolved) != len(set(output_resolved)):
        raise FinalizationError("--decisions-out and --approved-out must be distinct")
    if set(input_resolved) & set(output_resolved):
        raise FinalizationError("an output path must not alias any input review artifact")
    for path in inputs:
        if _inside(path, TRAITS_ROOT):
            raise FinalizationError(
                f"refusing to read a review artifact inside data/traits: {path}"
            )
    for path in outputs:
        if _inside(path, TRAITS_ROOT):
            raise FinalizationError(
                f"refusing to write a review artifact inside data/traits: {path}"
            )


def _atomic_write_many(outputs: list[tuple[Path, str]]) -> None:
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


def run(args: argparse.Namespace) -> int:
    _validate_paths(
        args.candidates,
        args.review_tsv,
        args.decisions,
        args.decisions_out,
        args.approved_out,
    )
    candidates = _candidate_snapshot(args.candidates)
    decisions = _decision_partitions(args.decisions, candidates)
    approved_groups, all_rejected_groups = _validate_record_groups(candidates, decisions)
    approved_text = _tsv_text(args.review_tsv, candidates, decisions)
    decisions_text = _decisions_text(decisions)
    action = "finalized" if args.apply else "would finalize"
    print(
        f"{action} {len(decisions):,} decisions across "
        f"{approved_groups + all_rejected_groups:,} trait records "
        f"({approved_groups:,} approved, {all_rejected_groups:,} all rejected)"
    )
    if not args.apply:
        print("dry run: no output files written; pass --apply to install finalized artifacts")
        return 0
    _atomic_write_many([(args.decisions_out, decisions_text), (args.approved_out, approved_text)])
    print(f"wrote canonical decisions: {args.decisions_out}")
    print(f"wrote completed approval TSV: {args.approved_out}")
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--candidates",
        type=Path,
        required=True,
        help="immutable resolved-candidate JSONL snapshot with resolution_digest",
    )
    parser.add_argument("--review-tsv", type=Path, required=True, help="blank resolver review TSV")
    parser.add_argument(
        "--decisions",
        type=Path,
        action="append",
        required=True,
        help=(
            "explicit JSONL decision partition carrying the exact resolved-row "
            "resolution_digest; repeat for every partition"
        ),
    )
    parser.add_argument("--decisions-out", type=Path, required=True)
    parser.add_argument("--approved-out", type=Path, required=True)
    parser.add_argument("--apply", action="store_true", help="atomically write both outputs")
    return parser


def main(argv: list[str] | None = None) -> int:
    try:
        return run(_parser().parse_args(argv))
    except (FinalizationError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
