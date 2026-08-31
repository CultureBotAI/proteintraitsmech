#!/usr/bin/env python3
"""Bind legacy UniProt review decisions to exact resolved-row digests.

The input decision ledger may be a complete review or a subset of complete record
groups.  Every mentioned candidate must exist in the resolved snapshot with the exact
same trait/record identity.  Existing ``resolution_digest`` values are accepted only
when already exact; this command never repairs a conflicting digest.

Dry-run validation is the default.  ``--apply`` may write only an explicitly named
``*.digest-bound.jsonl`` artifact beneath the ignored
``reports/uniprot-grounding/review-batches`` directory.  Inputs and output must be
distinct, and this utility never opens or writes a trait or durable data registry.
"""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

from finalize_uniprot_review_batch import (
    FinalizationError,
    _candidate_snapshot,
    _canonical_json,
    _exact_text,
    _read_jsonl,
    _record_path,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = REPO_ROOT / "data"
REVIEW_ARTIFACT_ROOT = REPO_ROOT / "reports" / "uniprot-grounding" / "review-batches"
OUTPUT_SUFFIX = ".digest-bound.jsonl"


class BindingError(RuntimeError):
    """Legacy decisions cannot be safely bound to the resolved snapshot."""


def _validate_paths(resolved: Path, decisions: Path, out: Path) -> None:
    inputs = {resolved.resolve(), decisions.resolve()}
    if len(inputs) != 2:
        raise BindingError("--resolved and --decisions must be distinct artifacts")
    output = out.resolve()
    if output in inputs:
        raise BindingError("--out must not alias either input artifact")
    for flag, path in (("--resolved", resolved), ("--decisions", decisions)):
        try:
            path.resolve().relative_to(DATA_ROOT.resolve())
        except ValueError:
            pass
        else:
            raise BindingError(f"{flag} must not read a trait or data-registry artifact")
    if not out.name.endswith(OUTPUT_SUFFIX):
        raise BindingError(f"--out filename must end with {OUTPUT_SUFFIX!r}")
    try:
        output.relative_to(REVIEW_ARTIFACT_ROOT.resolve())
    except ValueError as exc:
        raise BindingError(
            f"--out must be an explicitly named ignored artifact beneath {REVIEW_ARTIFACT_ROOT}"
        ) from exc


def _bound_rows(resolved: Path, decisions: Path) -> tuple[list[dict[str, Any]], int]:
    candidates = _candidate_snapshot(resolved)
    bound: dict[str, dict[str, Any]] = {}
    already_bound = 0
    for line_number, row in _read_jsonl(decisions, kind="legacy decision ledger"):
        subject = f"{decisions}:{line_number}: decision"
        candidate_id = _exact_text(row.get("candidate_id"), subject=subject, field="candidate_id")
        if candidate_id in bound:
            raise BindingError(
                f"{subject} duplicates candidate_id {candidate_id!r} in the decision ledger"
            )
        candidate = candidates.get(candidate_id)
        if candidate is None:
            raise BindingError(
                f"{subject} refers to candidate_id {candidate_id!r} absent from the "
                "resolved snapshot"
            )
        record_key = row.get("record_key")
        if not isinstance(record_key, dict):
            raise BindingError(f"{subject} lacks record_key")
        trait_id = _exact_text(
            record_key.get("trait_id"), subject=subject, field="record_key.trait_id"
        )
        record_path = _record_path(record_key.get("record_path"), subject=subject)
        if (trait_id, record_path) != candidate.record_key:
            raise BindingError(
                f"{subject} has stale record_key {(trait_id, record_path)!r}; expected "
                f"{candidate.record_key!r}"
            )
        expected_digest = str(candidate.row["resolution_digest"])
        if "resolution_digest" in row:
            existing = row["resolution_digest"]
            if existing != expected_digest:
                raise BindingError(
                    f"{subject} has conflicting existing resolution_digest {existing!r}; "
                    f"expected {expected_digest!r}"
                )
            already_bound += 1
        bound[candidate_id] = {**row, "resolution_digest": expected_digest}
    return [bound[candidate_id] for candidate_id in sorted(bound)], already_bound


def _jsonl_text(rows: list[dict[str, Any]]) -> str:
    return "".join(_canonical_json(row) + "\n" for row in rows)


def _atomic_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def run(args: argparse.Namespace) -> int:
    _validate_paths(args.resolved, args.decisions, args.out)
    rows, already_bound = _bound_rows(args.resolved, args.decisions)
    text = _jsonl_text(rows)
    newly_bound = len(rows) - already_bound
    action = "bound" if args.apply else "would bind"
    print(
        f"{action} {len(rows):,} decision row(s) to recomputed resolved-row digests "
        f"({newly_bound:,} legacy, {already_bound:,} already exact)"
    )
    if not args.apply:
        print("dry run: no output written; pass --apply to install the digest-bound artifact")
        return 0
    _atomic_text(args.out, text)
    print(f"wrote digest-bound decisions: {args.out}")
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--resolved",
        type=Path,
        required=True,
        help="exact resolved JSONL snapshot with valid resolution_digest rows",
    )
    parser.add_argument(
        "--decisions",
        type=Path,
        required=True,
        help="legacy or already-bound review decision JSONL",
    )
    parser.add_argument(
        "--out",
        type=Path,
        required=True,
        help=(
            "explicit output under reports/uniprot-grounding/review-batches; filename "
            f"must end in {OUTPUT_SUFFIX}"
        ),
    )
    parser.add_argument("--apply", action="store_true", help="atomically write --out")
    return parser


def main(argv: list[str] | None = None) -> int:
    try:
        return run(_parser().parse_args(argv))
    except (BindingError, FinalizationError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
