#!/usr/bin/env python3
"""Stage a fail-closed receipt audit for the historical Batch-001 promotion.

This is deliberately *not* a durable migration writer.  It reconstructs every
historical approved claim from checksum-pinned resolved/review artifacts, proves that
the installed occurrence and durable registries are still the reviewed state, and
replays the current source-aware record-content gate.  An incomplete clean subset and
an explicit blocked ledger may be written only beneath the ignored review-batch report
directory, using ``--write-staging``.  Incomplete coverage always returns non-zero.

The command has no option that writes traits, durable registries, or a complete receipt
registry.  A later, explicitly authorized repair transaction must re-review the blocked
claims and create complete durable receipts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import yaml

import ground_uniprot_examples as ground
from finalize_uniprot_review_batch import (
    FinalizationError,
    _candidate_snapshot,
    _canonical_json,
    _exact_text,
    _read_jsonl,
    _record_path,
)
from validate_uniprot_grounding import OCCURRENCE_EVIDENCE_FIELDS

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = REPO_ROOT / "data"
TRAITS_ROOT = DATA_ROOT / "traits"
DURABLE_PROTEIN_REGISTRY = DATA_ROOT / "grounding" / "protein_registry.jsonl"
DURABLE_EVIDENCE_REGISTRY = DATA_ROOT / "grounding" / "occurrence_evidence.jsonl"
REVIEW_ARTIFACT_ROOT = REPO_ROOT / "reports" / "uniprot-grounding" / "review-batches"

CLEAN_SUFFIX = ".receipts-incomplete-clean.jsonl"
BLOCKED_SUFFIX = ".receipts-blocked.jsonl"
MANIFEST_SUFFIX = ".receipts-manifest.json"
INCOMPLETE_EXIT = 3
# Distinct from the generic error exit: an already-promoted batch is a state, not a
# fault, and reporting it as one sent readers looking for data corruption (#607).
ALREADY_INSTALLED_EXIT = 4


@dataclass(frozen=True)
class BootstrapProfile:
    """Exact historical input image and cardinalities admitted by this migration."""

    input_sha256: Mapping[str, str]
    resolved_rows: int
    decision_rows: int
    approved_rows: int
    staging_proteins: int
    staging_evidence: int
    durable_proteins: int
    durable_evidence: int


BATCH001_PROFILE = BootstrapProfile(
    input_sha256={
        "resolved": "32c1f5e55a6f8b8298b2baef780fb2430ae562b85098cec6268306dd9a8cae9e",
        "decisions": "9c45934f13cc5d118e5d7a34903e3b40877e83f2a52de3cf82bae5c2363b64e4",
        "staging_proteins": "4546587ccdfc286fc7e0d81d3f4d113b01068f07147ddf98c86dca25a3b9a090",
        "staging_evidence": "a1cac95e254dcbfd562bc93539c9b966a6f21fe15be95c597170ff7231716170",
        "durable_proteins": "d587fad177207ca4f00d1dfb8649f4f9d2d21d01953d483f44a3a6e81acc729c",
        "durable_evidence": "a8a8e56b18987bbfe17774bedb5dbc8a44980ac3777de4c3797625a37f06bb47",
    },
    resolved_rows=2_065,
    decision_rows=322,
    approved_rows=127,
    staging_proteins=1_758,
    staging_evidence=2_065,
    durable_proteins=126,
    durable_evidence=127,
)

# Kept as one monkeypatchable object so focused fixture tests exercise the same exact
# hash/count enforcement as the production Batch-001 invocation.
EXPECTED_PROFILE = BATCH001_PROFILE

# The checksum-pinned Batch-001 staging ledger contains candidate-only SFLD evidence
# produced before the provider-receipt boundary existed.  Those rows were never
# approved or promoted.  This is the sole current semantic finding admitted for an
# unapproved historical staging row; every approved/durable row remains subject to the
# full current validator with no exception.
HISTORICAL_UNAPPROVED_STAGING_FINDING = "sfld_provider_receipt_required"


class BootstrapError(RuntimeError):
    """The historical state cannot be reconstructed without ambiguity."""


class BootstrapAlreadyInstalled(BootstrapError):
    """The batch this dry run replays has already been promoted and committed.

    Not a fault. The preimage check below reads each record's pre-promotion text
    from the CURRENT Git HEAD, so it can only match while the promotion is
    uncommitted. Once the batch lands, HEAD returns the promoted record and the
    hashes disagree -- which is indistinguishable, by hash alone, from a record
    that drifted since review. Raising a separate type lets the two be told apart
    and stops the second message being printed for the first situation.
    """



@dataclass(frozen=True)
class BootstrapResult:
    clean_text: str
    blocked_text: str
    manifest_text: str
    clean_count: int
    blocked_count: int
    manifest: dict[str, Any]
    record_sha256: Mapping[Path, str]


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_text(value: str) -> str:
    return _sha256_bytes(value.encode("utf-8"))


def _artifact_sha256(path: Path) -> str:
    if not path.is_file():
        raise BootstrapError(f"required input artifact does not exist: {path}")
    return _sha256_bytes(path.read_bytes())


def _jsonl_text(rows: list[dict[str, Any]]) -> str:
    return "".join(_canonical_json(row) + "\n" for row in rows)


def _display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return str(resolved)


def _under(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def _validate_paths(args: argparse.Namespace) -> dict[str, Path]:
    inputs = {
        "resolved": args.resolved.resolve(),
        "decisions": args.decisions.resolve(),
        "staging_proteins": args.staging_protein_registry.resolve(),
        "staging_evidence": args.staging_evidence_registry.resolve(),
        "durable_proteins": args.durable_protein_registry.resolve(),
        "durable_evidence": args.durable_evidence_registry.resolve(),
    }
    if len(set(inputs.values())) != len(inputs):
        raise BootstrapError("all resolved, review, staging, and durable inputs must be distinct")
    if inputs["durable_proteins"] != DURABLE_PROTEIN_REGISTRY.resolve():
        raise BootstrapError(
            f"--durable-protein-registry must be exactly {DURABLE_PROTEIN_REGISTRY}"
        )
    if inputs["durable_evidence"] != DURABLE_EVIDENCE_REGISTRY.resolve():
        raise BootstrapError(
            f"--durable-evidence-registry must be exactly {DURABLE_EVIDENCE_REGISTRY}"
        )
    if args.traits.resolve() != TRAITS_ROOT.resolve():
        raise BootstrapError(f"--traits must be exactly {TRAITS_ROOT}")
    for role in ("resolved", "decisions", "staging_proteins", "staging_evidence"):
        if not _under(inputs[role], REVIEW_ARTIFACT_ROOT):
            raise BootstrapError(
                f"--{role.replace('_', '-')} must be beneath {REVIEW_ARTIFACT_ROOT}"
            )
    if not args.decisions.name.endswith(".digest-bound.jsonl"):
        raise BootstrapError("--decisions must name an exact *.digest-bound.jsonl artifact")

    outputs = {
        "clean": args.clean_out.resolve(),
        "blocked": args.blocked_out.resolve(),
        "manifest": args.manifest_out.resolve(),
    }
    if len(set(outputs.values())) != len(outputs):
        raise BootstrapError("the three staging outputs must be distinct")
    if set(outputs.values()).intersection(inputs.values()):
        raise BootstrapError("a staging output must not alias any input artifact")
    suffixes = {
        "clean": CLEAN_SUFFIX,
        "blocked": BLOCKED_SUFFIX,
        "manifest": MANIFEST_SUFFIX,
    }
    for role, output in outputs.items():
        if not _under(output, REVIEW_ARTIFACT_ROOT):
            raise BootstrapError(
                f"--{role}-out must be an explicitly named ignored artifact beneath "
                f"{REVIEW_ARTIFACT_ROOT}"
            )
        if not output.name.endswith(suffixes[role]):
            raise BootstrapError(f"--{role}-out filename must end with {suffixes[role]!r}")
        lowered = output.name.lower()
        if "durable" in lowered or (
            role == "clean" and "complete" in lowered.replace("incomplete", "")
        ):
            raise BootstrapError("complete or durable receipt output is categorically refused")
        if _under(output, DATA_ROOT):
            raise BootstrapError("staging outputs must never enter data/traits or data/grounding")
    return {**inputs, **outputs}


def _verify_input_image(inputs: Mapping[str, Path]) -> dict[str, str]:
    observed: dict[str, str] = {}
    for role, expected in EXPECTED_PROFILE.input_sha256.items():
        path = inputs[role]
        digest = _artifact_sha256(path)
        if digest != expected:
            raise BootstrapError(
                f"{role} SHA-256 mismatch for {path}; expected {expected}, got {digest}"
            )
        observed[role] = digest
    return observed


def _reviewed_approvals(
    resolved_path: Path, decisions_path: Path
) -> tuple[list[dict[str, Any]], int]:
    candidates = _candidate_snapshot(resolved_path)
    if len(candidates) != EXPECTED_PROFILE.resolved_rows:
        raise BootstrapError(
            f"resolved row count changed: expected {EXPECTED_PROFILE.resolved_rows:,}, "
            f"got {len(candidates):,}"
        )
    decisions: dict[str, dict[str, Any]] = {}
    decisions_by_record: dict[tuple[str, str], set[str]] = defaultdict(set)
    for line_number, row in _read_jsonl(decisions_path, kind="digest-bound decision ledger"):
        subject = f"{decisions_path}:{line_number}: decision"
        candidate_id = _exact_text(row.get("candidate_id"), subject=subject, field="candidate_id")
        if candidate_id in decisions:
            raise BootstrapError(f"{subject} duplicates candidate_id {candidate_id!r}")
        candidate = candidates.get(candidate_id)
        if candidate is None:
            raise BootstrapError(f"{subject} refers to an unknown candidate")
        decision = row.get("decision")
        if decision not in {"APPROVED", "REJECTED"}:
            raise BootstrapError(f"{subject} must be exactly APPROVED or REJECTED")
        record_key = row.get("record_key")
        if not isinstance(record_key, dict):
            raise BootstrapError(f"{subject} lacks record_key")
        trait_id = _exact_text(
            record_key.get("trait_id"), subject=subject, field="record_key.trait_id"
        )
        record_path = _record_path(record_key.get("record_path"), subject=subject)
        if (trait_id, record_path) != candidate.record_key:
            raise BootstrapError(f"{subject} has a stale record_key")
        if row.get("resolution_digest") != candidate.row["resolution_digest"]:
            raise BootstrapError(f"{subject} has a stale resolution_digest")
        decisions[candidate_id] = row
        decisions_by_record[candidate.record_key].add(candidate_id)
    if len(decisions) != EXPECTED_PROFILE.decision_rows:
        raise BootstrapError(
            f"decision row count changed: expected {EXPECTED_PROFILE.decision_rows:,}, "
            f"got {len(decisions):,}"
        )

    all_by_record: dict[tuple[str, str], set[str]] = defaultdict(set)
    for candidate_id, candidate in candidates.items():
        all_by_record[candidate.record_key].add(candidate_id)
    incomplete_groups = sorted(
        record_key
        for record_key, decided in decisions_by_record.items()
        if decided != all_by_record[record_key]
    )
    if incomplete_groups:
        raise BootstrapError(
            "decision ledger contains an incomplete reviewed record group: "
            f"{incomplete_groups[0]!r}"
        )

    approved: list[dict[str, Any]] = []
    for record_key, candidate_ids in sorted(decisions_by_record.items()):
        approved_ids = sorted(
            candidate_id
            for candidate_id in candidate_ids
            if decisions[candidate_id]["decision"] == "APPROVED"
        )
        if len(approved_ids) > 1:
            raise BootstrapError(f"reviewed record {record_key!r} has multiple approved candidates")
        if approved_ids:
            approved.append(candidates[approved_ids[0]].row)
    approved.sort(key=lambda row: str(row["candidate_id"]))
    if len(approved) != EXPECTED_PROFILE.approved_rows:
        raise BootstrapError(
            f"approved row count changed: expected {EXPECTED_PROFILE.approved_rows:,}, "
            f"got {len(approved):,}"
        )
    return approved, len(decisions) - len(approved)


def _semantic_registries(
    inputs: Mapping[str, Path], approved: list[dict[str, Any]]
) -> tuple[
    dict[str, dict[str, Any]],
    dict[str, dict[str, Any]],
    dict[str, dict[str, Any]],
    dict[str, dict[str, Any]],
]:
    staging_proteins = ground._semantic_registry(inputs["staging_proteins"])
    durable_proteins = ground._semantic_registry(inputs["durable_proteins"])
    durable_evidence = ground._semantic_evidence_registry(inputs["durable_evidence"])
    staging_evidence = _historical_staging_evidence_registry(
        inputs["staging_evidence"], approved_evidence_ids=frozenset(durable_evidence)
    )
    expected_counts = {
        "staging_proteins": EXPECTED_PROFILE.staging_proteins,
        "staging_evidence": EXPECTED_PROFILE.staging_evidence,
        "durable_proteins": EXPECTED_PROFILE.durable_proteins,
        "durable_evidence": EXPECTED_PROFILE.durable_evidence,
    }
    registries = {
        "staging_proteins": staging_proteins,
        "staging_evidence": staging_evidence,
        "durable_proteins": durable_proteins,
        "durable_evidence": durable_evidence,
    }
    for role, expected in expected_counts.items():
        if len(registries[role]) != expected:
            raise BootstrapError(
                f"{role} row count changed: expected {expected:,}, got {len(registries[role]):,}"
            )

    approved_evidence: dict[str, str] = {}
    approved_proteins: set[str] = set()
    for row in approved:
        candidate_id = str(row["candidate_id"])
        reasons = ground._validate_resolved_row(
            row, {"resolution_digest": str(row["resolution_digest"])}
        )
        if reasons:
            raise BootstrapError(f"{candidate_id}: invalid reviewed row: {', '.join(reasons)}")
        embedded = row.get("grounding_evidence")
        occurrence = row.get("trait_occurrence")
        if not isinstance(embedded, dict) or not isinstance(occurrence, dict):
            raise BootstrapError(f"{candidate_id}: reviewed row lacks evidence/occurrence")
        evidence_id = str(embedded.get("evidence_id") or "")
        if not evidence_id or occurrence.get("source_evidence_id") != evidence_id:
            raise BootstrapError(f"{candidate_id}: reviewed evidence binding is incomplete")
        previous = approved_evidence.setdefault(evidence_id, candidate_id)
        if previous != candidate_id:
            raise BootstrapError(
                f"durable evidence {evidence_id} maps to multiple approved candidates"
            )
        durable = durable_evidence.get(evidence_id)
        if durable is None or embedded != durable or staging_evidence.get(evidence_id) != durable:
            raise BootstrapError(
                f"{candidate_id}: embedded, staging, and durable evidence are not exact"
            )
        protein_id = str(row.get("protein_id") or "")
        approved_proteins.add(protein_id)
        durable_protein = durable_proteins.get(protein_id)
        if (
            durable_protein is None
            or staging_proteins.get(protein_id) != durable_protein
            or ground._value_digest(durable_protein) != row.get("protein_reference_sha256")
        ):
            raise BootstrapError(
                f"{candidate_id}: reviewed, staging, and durable ProteinReference differ"
            )
    if set(approved_evidence) != set(durable_evidence):
        missing = sorted(set(durable_evidence) - set(approved_evidence))
        extra = sorted(set(approved_evidence) - set(durable_evidence))
        raise BootstrapError(
            "approved evidence does not exactly cover the durable registry; "
            f"missing={missing[:5]}, extra={extra[:5]}"
        )
    if approved_proteins != set(durable_proteins):
        raise BootstrapError("approved proteins do not exactly cover the durable registry")
    ground._validate_registry_links(durable_proteins, durable_evidence)
    return staging_proteins, staging_evidence, durable_proteins, durable_evidence


def _historical_staging_evidence_registry(
    path: Path, *, approved_evidence_ids: frozenset[str]
) -> dict[str, dict[str, Any]]:
    """Load pinned candidate evidence without qualifying rejected historical rows.

    Current central semantics are mandatory for the approved projection, represented
    by the already validated durable evidence IDs.  A non-approved Batch-001 row may
    retain its historical content-addressed object only when the validator reports the
    exact singleton SFLD receipt finding.  Any shape, digest, duplicate, additional,
    or approved-row finding remains fatal.
    """

    from validate_uniprot_grounding import validate_grounding_evidence

    registry: dict[str, dict[str, Any]] = {}
    for line_number, row in _read_jsonl(path, kind="historical staging evidence"):
        findings = validate_grounding_evidence(row, path=path, line=line_number)
        evidence_id = row.get("evidence_id")
        allowed_unapproved_finding = (
            isinstance(evidence_id, str)
            and evidence_id not in approved_evidence_ids
            and [finding.code for finding in findings] == [HISTORICAL_UNAPPROVED_STAGING_FINDING]
        )
        if findings and not allowed_unapproved_finding:
            detail = "; ".join(f"{finding.code}: {finding.message}" for finding in findings[:3])
            raise BootstrapError(
                f"historical staging evidence validation rejected preflight: {detail}"
            )
        if not isinstance(evidence_id, str):
            raise BootstrapError(
                f"{path}:{line_number}: historical staging evidence lacks evidence_id"
            )
        if evidence_id in registry:
            raise BootstrapError(
                f"{path}:{line_number}: duplicate historical staging evidence_id {evidence_id}"
            )
        registry[evidence_id] = row
    return registry


def _head_text(record_path: str) -> str:
    """Read the historical pre-promotion record from the current Git HEAD."""

    try:
        completed = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "show", f"HEAD:{record_path}"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise BootstrapError(f"cannot read historical record preimage HEAD:{record_path}") from exc
    try:
        return completed.stdout.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise BootstrapError(f"historical record is not UTF-8: HEAD:{record_path}") from exc


def _carries_evidence(record: object, evidence_id: str) -> bool:
    """True when this record already declares that exact grounding evidence id.

    Structural rather than a substring search: the id has to appear as an actual
    ``source_evidence_id`` on a trait occurrence, so a mention in a comment or an
    unrelated field cannot be read as an installation.
    """
    if not isinstance(record, dict):
        return False
    for example in record.get("canonical_examples") or []:
        if not isinstance(example, dict):
            continue
        for occurrence in example.get("trait_occurrences") or []:
            if isinstance(occurrence, dict) and occurrence.get("source_evidence_id") == evidence_id:
                return True
    return False


def _load_installed_records(
    approved: list[dict[str, Any]],
    durable_evidence: Mapping[str, dict[str, Any]],
    traits_root: Path,
) -> tuple[dict[Path, dict[str, Any]], dict[Path, str], dict[str, tuple[Path, dict[str, Any]]]]:
    records: dict[Path, dict[str, Any]] = {}
    texts: dict[Path, str] = {}
    expected_paths: dict[str, Path] = {}
    for row in approved:
        candidate_id = str(row["candidate_id"])
        path = ground._safe_record_path(row.get("record_path"), traits_root)
        if path in records:
            raise BootstrapError(f"{candidate_id}: multiple approvals target one record")
        try:
            text = path.read_text(encoding="utf-8")
            record = yaml.safe_load(text)
        except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
            raise BootstrapError(f"{path}: cannot load installed trait record: {exc}") from exc
        if not isinstance(record, dict) or record.get("identifier") != row.get("trait_id"):
            raise BootstrapError(f"{candidate_id}: installed record identity changed")
        evidence_id = str(row["grounding_evidence"]["evidence_id"])
        expected_paths[evidence_id] = path
        records[path] = record
        texts[path] = text

        preimage = _head_text(str(row["record_path"]))
        if _sha256_text(preimage) != row.get("record_sha256"):
            # Two different situations produce one hash mismatch. Ask the record
            # on disk which it is: if it already carries this candidate's
            # evidence id, the promotion happened and HEAD is simply showing the
            # result of it. Anything else is a genuine drift since review.
            if _carries_evidence(record, evidence_id):
                raise BootstrapAlreadyInstalled(
                    f"{candidate_id}: this batch is already promoted and committed; "
                    f"the pre-promotion dry run cannot be replayed against HEAD "
                    f"(evidence {evidence_id} is installed in {row['record_path']})"
                )
            raise BootstrapError(f"{candidate_id}: historical record preimage is stale")
        try:
            preimage_record = yaml.safe_load(preimage)
        except yaml.YAMLError as exc:
            raise BootstrapError(f"{candidate_id}: historical record preimage is invalid") from exc
        installed, changed = ground._install_example(preimage_record, row)
        expected_text = ground._replace_examples_block(preimage, installed) if changed else preimage
        if expected_text != text:
            raise BootstrapError(
                f"{candidate_id}: current record differs from the deterministic Batch-001 install"
            )

    # Scan every trait once so an evidence ID copied into a different record cannot be
    # hidden by looking only at its expected path.  YAML parsing remains restricted to
    # the few files that actually contain a grounding evidence ID.
    occurrences: dict[str, list[tuple[Path, dict[str, Any], dict[str, Any]]]] = defaultdict(list)
    all_installed_ids: set[str] = set()
    for path in sorted(traits_root.rglob("*.yaml")):
        try:
            text = texts.get(path) or path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            raise BootstrapError(
                f"cannot scan trait grounding identifiers in {path}: {exc}"
            ) from exc
        if "ug-evidence:" not in text:
            continue
        record = records.get(path)
        if record is None:
            try:
                record = yaml.safe_load(text)
            except yaml.YAMLError as exc:
                raise BootstrapError(f"cannot parse grounded trait record {path}: {exc}") from exc
        if not isinstance(record, dict):
            raise BootstrapError(f"grounded trait record is not a mapping: {path}")
        for example in record.get("canonical_examples") or []:
            if not isinstance(example, dict):
                continue
            for occurrence in example.get("trait_occurrences") or []:
                if not isinstance(occurrence, dict):
                    continue
                evidence_id = occurrence.get("source_evidence_id")
                if isinstance(evidence_id, str) and evidence_id.startswith("ug-evidence:"):
                    all_installed_ids.add(evidence_id)
                    occurrences[evidence_id].append((path, example, occurrence))
    if all_installed_ids != set(durable_evidence):
        missing = sorted(set(durable_evidence) - all_installed_ids)
        extra = sorted(all_installed_ids - set(durable_evidence))
        raise BootstrapError(
            "installed occurrence evidence IDs do not exactly equal durable evidence; "
            f"missing={missing[:5]}, extra={extra[:5]}"
        )

    installed: dict[str, tuple[Path, dict[str, Any]]] = {}
    for evidence_id in sorted(durable_evidence):
        matches = occurrences.get(evidence_id, [])
        if len(matches) != 1:
            raise BootstrapError(
                f"{evidence_id}: resolves to {len(matches)} installed occurrences, expected one"
            )
        path, example, occurrence = matches[0]
        if path != expected_paths[evidence_id]:
            raise BootstrapError(f"{evidence_id}: installed in an unexpected record path")
        evidence = durable_evidence[evidence_id]
        mismatches = [
            field
            for field in OCCURRENCE_EVIDENCE_FIELDS
            if occurrence.get(field) != evidence.get(field)
        ]
        if occurrence.get("qualification_status") != "QUALIFIED":
            mismatches.append("qualification_status")
        if example.get("protein_id") != evidence.get("protein_id"):
            mismatches.append("example.protein_id")
        if mismatches:
            raise BootstrapError(f"{evidence_id}: installed occurrence differs in {mismatches[:5]}")
        installed[evidence_id] = (path, occurrence)
    return records, texts, installed


def _gate_args(args: argparse.Namespace) -> argparse.Namespace:
    return argparse.Namespace(
        interpro_xml=args.interpro_xml,
        interpro_xml_sha256=args.interpro_xml_sha256,
        pfam_clans=args.pfam_clans,
        pfam_clans_sha256=args.pfam_clans_sha256,
        pfam_types=args.pfam_types,
        pfam_types_sha256=args.pfam_types_sha256,
        panther_classifications=args.panther_classifications,
        panther_classifications_sha256=args.panther_classifications_sha256,
    )


def _build_result(
    args: argparse.Namespace,
    inputs: Mapping[str, Path],
    input_sha256: Mapping[str, str],
) -> BootstrapResult:
    approved, rejected_count = _reviewed_approvals(inputs["resolved"], inputs["decisions"])
    (
        _staging_proteins,
        _staging_evidence,
        durable_proteins,
        durable_evidence,
    ) = _semantic_registries(inputs, approved)
    records, texts, installed = _load_installed_records(
        approved, durable_evidence, args.traits.resolve()
    )
    gate_args = _gate_args(args)
    gate = ground._prepare_content_gate(records.values(), gate_args)

    clean: dict[str, dict[str, Any]] = {}
    all_receipts: dict[str, dict[str, Any]] = {}
    blocked: list[dict[str, Any]] = []
    finding_counts: Counter[str] = Counter()
    approved_by_evidence = {str(row["grounding_evidence"]["evidence_id"]): row for row in approved}
    for evidence_id in sorted(durable_evidence):
        row = approved_by_evidence[evidence_id]
        candidate_id = str(row["candidate_id"])
        path, _occurrence = installed[evidence_id]
        seed = {
            "evidence_id": evidence_id,
            "candidate_id": candidate_id,
            "trait_id": str(row["trait_id"]),
            "content_gate_projection": {
                "candidate": ground._content_gate_candidate_projection(row)
            },
        }
        candidate = ground._durable_gate_candidate(
            seed, durable_evidence[evidence_id], durable_proteins
        )
        if ground._content_gate_candidate_projection(
            candidate
        ) != ground._content_gate_candidate_projection(row):
            raise BootstrapError(f"{candidate_id}: durable gate candidate projection changed")
        projection, findings = ground._content_gate_projection(
            gate, records[path], candidate, gate_args
        )
        hard_findings = [
            finding for finding in findings if finding.severity == ground.CONTENT_GATE_HARD
        ]
        finding_counts.update(finding.code for finding in findings)
        receipt = ground._qualified_record_binding(
            evidence_id=evidence_id,
            candidate_id=candidate_id,
            trait_id=str(row["trait_id"]),
            record_path=path,
            record_sha256=_sha256_text(texts[path]),
            content_gate_projection=projection,
        )
        all_receipts[evidence_id] = receipt
        if hard_findings:
            blocked.append(
                {
                    "schema_version": 1,
                    "status": "HARD_BLOCKED",
                    "evidence_id": evidence_id,
                    "candidate_id": candidate_id,
                    "trait_id": row["trait_id"],
                    "protein_id": row["protein_id"],
                    "record_path": receipt["record_path"],
                    "record_sha256": receipt["record_sha256"],
                    "content_gate_digest": receipt["content_gate_digest"],
                    "hard_codes": sorted({finding.code for finding in hard_findings}),
                    "findings": [finding.as_dict() for finding in hard_findings],
                }
            )
        else:
            clean[evidence_id] = receipt

    if set(clean).intersection(row["evidence_id"] for row in blocked):
        raise BootstrapError("a hard-blocked evidence row entered the clean receipt subset")
    if set(clean).union(row["evidence_id"] for row in blocked) != set(durable_evidence):
        raise BootstrapError("clean and blocked projections do not cover durable evidence")
    complete = not blocked and set(clean) == set(durable_evidence)
    if complete:
        raise BootstrapError(
            "historical state is complete; this staging-only bootstrap refuses to emit a "
            "complete or durable receipt registry"
        )

    # Exercise the same production receipt dereference checks used by every future
    # promotion.  Hard rows are expected to fail only in the subsequent gate replay,
    # never while binding evidence, record paths, candidate identity, or intervals.
    bound_records, _bound_shas, replay_rows = ground._load_bound_durable_records(
        all_receipts, durable_evidence, durable_proteins, args.traits.resolve()
    )
    if len(bound_records) != len(records) or len(replay_rows) != len(durable_evidence):
        raise BootstrapError("production receipt dereference did not cover the full durable state")

    clean_rows = [clean[evidence_id] for evidence_id in sorted(clean)]
    blocked.sort(key=lambda row: str(row["evidence_id"]))
    clean_text = _jsonl_text(clean_rows)
    blocked_text = _jsonl_text(blocked)
    all_text = ground._registry_text(all_receipts)
    record_manifest_text = "".join(
        f"{all_receipts[evidence_id]['record_path']}\t"
        f"{all_receipts[evidence_id]['record_sha256']}\n"
        for evidence_id in sorted(all_receipts)
    )
    mapping_manifest_text = "".join(
        f"{evidence_id}\t{all_receipts[evidence_id]['candidate_id']}\t"
        f"{all_receipts[evidence_id]['trait_id']}\t"
        f"{all_receipts[evidence_id]['record_path']}\t"
        f"{all_receipts[evidence_id]['record_sha256']}\t"
        f"{all_receipts[evidence_id]['content_gate_digest']}\n"
        for evidence_id in sorted(all_receipts)
    )
    manifest = {
        "schema_version": 1,
        "kind": "UNIPROT_QUALIFIED_RECORD_BINDING_BOOTSTRAP",
        "staging_only": True,
        "complete": False,
        "inputs": {
            role: {"path": _display_path(inputs[role]), "sha256": input_sha256[role]}
            for role in sorted(input_sha256)
        },
        "outputs": {
            "clean_incomplete_receipts": {
                "path": _display_path(inputs["clean"]),
                "sha256": _sha256_text(clean_text),
            },
            "blocked": {
                "path": _display_path(inputs["blocked"]),
                "sha256": _sha256_text(blocked_text),
            },
        },
        "counts": {
            "resolved_rows": EXPECTED_PROFILE.resolved_rows,
            "decision_rows": EXPECTED_PROFILE.decision_rows,
            "approved_rows": len(approved),
            "rejected_rows": rejected_count,
            "durable_proteins": len(durable_proteins),
            "durable_evidence": len(durable_evidence),
            "installed_occurrences": len(installed),
            "clean_receipts": len(clean),
            "blocked": len(blocked),
            "missing_receipts": len(durable_evidence) - len(clean),
        },
        "finding_counts": dict(sorted(finding_counts.items())),
        "proof": {
            "all_candidate_receipts_sha256": _sha256_text(all_text),
            "mapping_manifest_sha256": _sha256_text(mapping_manifest_text),
            "record_manifest_sha256": _sha256_text(record_manifest_text),
            "production_receipt_dereference_count": len(replay_rows),
        },
    }
    manifest_text = json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    return BootstrapResult(
        clean_text=clean_text,
        blocked_text=blocked_text,
        manifest_text=manifest_text,
        clean_count=len(clean),
        blocked_count=len(blocked),
        manifest=manifest,
        record_sha256={path: _sha256_text(text) for path, text in texts.items()},
    )


def run(args: argparse.Namespace) -> int:
    inputs = _validate_paths(args)
    input_sha256 = _verify_input_image(inputs)
    result = _build_result(args, inputs, input_sha256)

    # Recheck every input and installed record immediately before any staging write.
    # This prevents a self-consistent but mixed-generation output if curation overlaps
    # the relatively expensive source/gate replay.
    changed_inputs = [
        role
        for role, expected in input_sha256.items()
        if _artifact_sha256(inputs[role]) != expected
    ]
    if changed_inputs:
        raise BootstrapError(
            "input artifact(s) changed during bootstrap preflight: "
            + ", ".join(sorted(changed_inputs))
        )
    changed_records = [
        path
        for path, expected in result.record_sha256.items()
        if not path.is_file() or _sha256_bytes(path.read_bytes()) != expected
    ]
    if changed_records:
        raise BootstrapError(
            "receipt-covered trait record(s) changed during bootstrap preflight: "
            + ", ".join(_display_path(path) for path in sorted(changed_records)[:5])
        )

    action = "STAGE" if args.write_staging else "DRY-RUN"
    print(
        f"{action}: {result.clean_count:,} gate-clean incomplete receipt(s), "
        f"{result.blocked_count:,} hard-blocked claim(s); complete=false"
    )
    print(
        "proof: all-receipts="
        f"{result.manifest['proof']['all_candidate_receipts_sha256']}, mapping="
        f"{result.manifest['proof']['mapping_manifest_sha256']}"
    )
    if args.write_staging:
        ground._install_promotion_transaction(
            [
                (inputs["clean"], result.clean_text),
                (inputs["blocked"], result.blocked_text),
                (inputs["manifest"], result.manifest_text),
            ],
            {},
        )
        print(
            "wrote three ignored staging artifacts atomically; durable coverage remains incomplete"
        )
    else:
        print("dry run: no staging, trait, or durable registry artifact written")
    return INCOMPLETE_EXIT


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resolved", type=Path, required=True)
    parser.add_argument("--decisions", type=Path, required=True)
    parser.add_argument("--staging-protein-registry", type=Path, required=True)
    parser.add_argument("--staging-evidence-registry", type=Path, required=True)
    parser.add_argument("--durable-protein-registry", type=Path, default=DURABLE_PROTEIN_REGISTRY)
    parser.add_argument("--durable-evidence-registry", type=Path, default=DURABLE_EVIDENCE_REGISTRY)
    parser.add_argument("--traits", type=Path, default=TRAITS_ROOT)
    parser.add_argument("--clean-out", type=Path, required=True)
    parser.add_argument("--blocked-out", type=Path, required=True)
    parser.add_argument("--manifest-out", type=Path, required=True)
    parser.add_argument("--interpro-xml", type=Path, default=ground.DEFAULT_INTERPRO_XML)
    parser.add_argument("--interpro-xml-sha256", default=ground.INTERPRO_109_XML_SHA256)
    parser.add_argument("--pfam-clans", type=Path, default=ground.DEFAULT_CONTENT_GATE_PFAM_CLANS)
    parser.add_argument("--pfam-clans-sha256", default=ground.PFAM_A_CLANS_SHA256)
    parser.add_argument("--pfam-types", type=Path, default=ground.DEFAULT_CONTENT_GATE_PFAM_TYPES)
    parser.add_argument("--pfam-types-sha256", default=ground.PFAM_TYPES_SHA256)
    parser.add_argument(
        "--panther-classifications",
        type=Path,
        default=ground.DEFAULT_CONTENT_GATE_PANTHER_CLASSIFICATIONS,
    )
    parser.add_argument(
        "--panther-classifications-sha256",
        default=ground.PANTHER_19_CLASSIFICATIONS_SHA256,
    )
    parser.add_argument(
        "--write-staging",
        action="store_true",
        help="atomically write only the three explicitly named ignored staging outputs",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    try:
        return run(_parser().parse_args(argv))
    except BootstrapAlreadyInstalled as exc:
        print(f"already installed: {exc}", file=sys.stderr)
        return ALREADY_INSTALLED_EXIT
    except (BootstrapError, FinalizationError, ground.GroundingError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
