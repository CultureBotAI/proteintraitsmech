#!/usr/bin/env python3
r"""DUF discovery-lead lane: route DUFMech's UniProt candidates into the grounding funnel.

WHY THIS EXISTS
---------------
The ordinary UniProt grounding audit discovers candidates only from the local provider
frames, which are crawled for a fixed ten-organism panel. Pfam "domain of unknown
function" (DUF) families are mostly carried by uncharacterized bacterial and
environmental proteins outside that panel, so almost every Pfam DUF trait record ends
up ``NO_LOCAL_EXACT_TRAIT_MATCH`` and the selector cannot reach it. DUFMech already
froze, per DUF family, up to three UniProtKB entries that carry the family's Pfam
cross-reference (``uniprot-duf-example-candidates-2026-10-07``). That snapshot names
*which proteins to look at*; it is not evidence that any of them carries the family.

TRUST LEVELS
------------
1. SNAPSHOT (pinned, never copied) -- DUFMech's frozen rows, read from git objects at
   the pinned commit ``PINNED_COMMIT`` of ``CultureBotAI/DUFMech`` and checked
   against the pinned SHA-256 of both the JSON and its manifest. A moving path or a
   working tree is never read.
2. AUDIT (``audit``, read-only) -- each (Pfam family, protein) lead is joined to the
   exact ``Pfam:<id>`` trait record here and given one status. Only leads on a record
   with no QUALIFIED canonical example become TARGET leads. The pinned record-content
   gate (the same one the audit and resolver apply) drops records whose own text the
   source images contradict, so no fetch is spent on a record that cannot qualify.
3. DISCOVERY (``discover``, network: UniProt REST only) -- a bounded, deterministic set
   of target records is chosen and each of its leads' exact sequence identity is read
   from the pinned UniProt release. Identity, not evidence: the selector-bound registry
   fetch re-acquires every protein under its own receipt. The InterPro matches for the
   same accessions are crawled separately by ``just fetch-duf-interpro-frame``
   (``fetch_interpro_frame.py --accessions``) into a release-stamped sidecar of its own.
4. CANDIDATES (``candidates``, offline) -- a lead becomes a funnel candidate only when
   the pinned InterPro frame itself asserts an exact match of the record's Pfam
   signature on that accession, with coordinates copied from the frame. The record's
   category fixes the scope (``SEQ_FAMILY`` and ``SEQ_HOMOLOGOUS_SUPERFAMILY`` are
   WHOLE_PROTEIN, everything else LOCALIZED); a LOCALIZED claim needs one exact
   InterPro location (grouped) or a single interval. Everything else is a reported
   rejection.
5. INCLUSION -- not here. Candidates go through the ordinary select -> fetch ->
   resolve -> review -> promote route; ``resolve-duf-review-batch`` only binds the DUF
   InterPro sidecar. This module writes no trait record and no durable registry.

A DUFMech row is a discovery lead, never qualification evidence (CLAUDE.md; the
cross-Mech policy in ``research/cross-mech-protein-examples.md``). See
``research/duf-discovery-leads.md``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import cross_mech_proteins as cm  # noqa: E402

REPO_ROOT = SCRIPTS.parent
TRAITS_ROOT = REPO_ROOT / "data" / "traits"
OUT_DIR = REPO_ROOT / "reports" / "uniprot-grounding" / "duf-leads"
DUF_FRAME_DIR = REPO_ROOT / "data" / "raw" / "align_cache" / "duf-leads"
DUF_INTERPRO_FRAME = DUF_FRAME_DIR / "interpro_frame.json"
DUF_INTERPRO_GROUPED_FRAME = DUF_FRAME_DIR / "interpro_grouped_locations.json"

# ---------------------------------------------------------------- the pinned input
DUFMECH_REPOSITORY = "CultureBotAI/DUFMech"
PINNED_COMMIT = "217c2cc5cfc2fc43b7196e46fac57ee2a71efe0b"
SNAPSHOT_ID = "uniprot-duf-example-candidates-2026-10-07"
SNAPSHOT_PATH = f"data/worklists/{SNAPSHOT_ID}.json"
MANIFEST_PATH = f"data/worklists/{SNAPSHOT_ID}.manifest.json"
SNAPSHOT_SHA256 = "0c9e637106357244f3b70f34b14c29e034e9bfdd4fec6b977b5f323174d55cbe"
MANIFEST_SHA256 = "1004848bc569d67505929c529fcf7e7012537b3053d4c423e22dd7abb84aa45f"
SNAPSHOT_UNIPROT_RELEASE = "2026_03"
# Only DUFMech's "ProteinTraitsMech trait without a family example" reason scopes a row
# to a DUF trait gap here. The renamed-TraitMech rows name families Pfam no longer
# calls DUFs; they are reported, not targeted.
GAP_REASON = "protein_traits_trait_without_family_example"

CANDIDATE_BATCH = "duf-leads"
LEAD_FIELDS = frozenset(
    {
        "annotation_score",
        "family_members",
        "length",
        "organism",
        "pfam_id",
        "protein_name",
        "rank",
        "reviewed",
        "selection_reasons",
        "source_url",
        "taxon_id",
        "uniprot_accession",
    }
)
_PFAM = re.compile(r"^PF[0-9]{5}$")
_ACCESSION = re.compile(rf"^{cm._ACCESSION}$")
_RELEASE = re.compile(r"^[0-9]{4}_[0-9]{2}$")
_INTERPRO_RELEASE = re.compile(r"^[0-9]+(?:\.[0-9]+)*$")
WHOLE_PROTEIN_CATEGORIES = frozenset({"SEQ_FAMILY", "SEQ_HOMOLOGOUS_SUPERFAMILY"})

LEAD_STATUSES = (
    "TARGET_ABSENT_FROM_TRAIT",
    "TARGET_LEGACY_ON_TRAIT",
    "RECORD_ALREADY_QUALIFIED",
    "RECORD_CONTENT_BLOCKED",
    "AMBIGUOUS_TRAIT_RECORD",
    "TRAIT_NOT_IN_PTM",
    "OUT_OF_SCOPE_REASON",
)
TARGET_STATUSES = frozenset({"TARGET_ABSENT_FROM_TRAIT", "TARGET_LEGACY_ON_TRAIT"})


class DufLeadError(RuntimeError):
    """A pinned input, provider, or invariant failed closed."""


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    cm._atomic_write(path, "".join(canonical_json(row) + "\n" for row in rows))


def _write_json(path: Path, value: Any) -> None:
    cm._atomic_write(path, json.dumps(value, indent=2, sort_keys=True) + "\n")


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise DufLeadError(f"missing {path}")
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


# ------------------------------------------------------------------- snapshot


def _git_bytes(repo: Path, *args: str) -> bytes:
    completed = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, check=False)
    if completed.returncode:
        message = completed.stderr.decode("utf-8", "replace").strip()
        raise DufLeadError(f"git {' '.join(args)} failed in {repo}: {message}")
    return completed.stdout


@dataclass(frozen=True)
class Snapshot:
    rows: list[dict[str, Any]]
    manifest: dict[str, Any]
    commit: str
    snapshot_sha256: str
    manifest_sha256: str

    def provenance(self) -> dict[str, Any]:
        return {
            "repository": DUFMECH_REPOSITORY,
            "commit": self.commit,
            "snapshot_id": SNAPSHOT_ID,
            "snapshot_path": SNAPSHOT_PATH,
            "snapshot_sha256": self.snapshot_sha256,
            "manifest_path": MANIFEST_PATH,
            "manifest_sha256": self.manifest_sha256,
        }


def verify_snapshot(
    raw: bytes,
    manifest_raw: bytes,
    *,
    expected_sha256: str = SNAPSHOT_SHA256,
    expected_manifest_sha256: str = MANIFEST_SHA256,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Check both pinned digests, the manifest's own claims, and every row's shape."""

    if sha256_bytes(raw) != expected_sha256:
        raise DufLeadError(f"snapshot SHA-256 {sha256_bytes(raw)} is not the pinned {expected_sha256}")
    if sha256_bytes(manifest_raw) != expected_manifest_sha256:
        raise DufLeadError(
            f"manifest SHA-256 {sha256_bytes(manifest_raw)} is not the pinned "
            f"{expected_manifest_sha256}"
        )
    manifest = json.loads(manifest_raw)
    declared = (manifest.get("files") or {}).get("json") or {}
    if declared.get("sha256") != expected_sha256 or declared.get("bytes") != len(raw):
        raise DufLeadError("the DUFMech manifest does not describe the pinned snapshot bytes")
    if (manifest.get("source") or {}).get("uniprot_releases") != [SNAPSHOT_UNIPROT_RELEASE]:
        raise DufLeadError("the DUFMech snapshot is not a single-release UniProt 2026_03 freeze")
    rows = json.loads(raw)
    if not isinstance(rows, list) or len(rows) != (manifest.get("rows") or {}).get("total"):
        raise DufLeadError("snapshot row count disagrees with its manifest")
    seen: set[tuple[str, str]] = set()
    for number, row in enumerate(rows, 1):
        if not isinstance(row, dict) or set(row) != LEAD_FIELDS:
            raise DufLeadError(f"snapshot row {number}: unexpected fields")
        if not _PFAM.fullmatch(str(row["pfam_id"])):
            raise DufLeadError(f"snapshot row {number}: invalid pfam_id {row['pfam_id']!r}")
        if not _ACCESSION.fullmatch(str(row["uniprot_accession"])):
            raise DufLeadError(f"snapshot row {number}: invalid accession")
        if not isinstance(row["reviewed"], bool) or not isinstance(row["selection_reasons"], list):
            raise DufLeadError(f"snapshot row {number}: invalid reviewed/selection_reasons")
        key = (row["pfam_id"], row["uniprot_accession"])
        if key in seen:
            raise DufLeadError(f"snapshot row {number}: duplicate lead {key}")
        seen.add(key)
    return rows, manifest


def load_snapshot(
    repo: Path,
    commit: str = PINNED_COMMIT,
    *,
    expected_sha256: str = SNAPSHOT_SHA256,
    expected_manifest_sha256: str = MANIFEST_SHA256,
) -> Snapshot:
    """Read the pinned snapshot from git objects in a verified DUFMech checkout."""

    if not (repo / ".git").exists():
        raise DufLeadError(f"no DUFMech git checkout at {repo}")
    origin = cm.normalize_remote(_git_bytes(repo, "remote", "get-url", "origin").decode())
    if origin != DUFMECH_REPOSITORY.lower():
        raise DufLeadError(f"{repo} has origin {origin or 'unknown'!r}, not {DUFMECH_REPOSITORY}")
    try:
        _git_bytes(repo, "cat-file", "-e", f"{commit}^{{commit}}")
    except DufLeadError as error:
        raise DufLeadError(
            f"pinned commit {commit} is not in {repo}; run `git -C {repo} fetch origin`"
        ) from error
    published = subprocess.run(
        ["git", "-C", str(repo), "merge-base", "--is-ancestor", commit, "origin/main"],
        capture_output=True,
        check=False,
    )
    if published.returncode:
        raise DufLeadError(f"pinned commit {commit} is not on {DUFMECH_REPOSITORY} origin/main")
    raw = _git_bytes(repo, "show", f"{commit}:{SNAPSHOT_PATH}")
    manifest_raw = _git_bytes(repo, "show", f"{commit}:{MANIFEST_PATH}")
    rows, manifest = verify_snapshot(
        raw,
        manifest_raw,
        expected_sha256=expected_sha256,
        expected_manifest_sha256=expected_manifest_sha256,
    )
    return Snapshot(rows, manifest, commit, sha256_bytes(raw), sha256_bytes(manifest_raw))


# ---------------------------------------------------------------------- audit


def scope_for(axis: str | None, category: str | None) -> str:
    if axis in {"FUNCTION", "EVOLUTION"} or category in WHOLE_PROTEIN_CATEGORIES:
        return "WHOLE_PROTEIN"
    return "LOCALIZED"


def _content_blocked(
    documents: Mapping[str, Mapping[str, Any]], *, make_gate: Callable[..., Any] | None
) -> dict[str, list[str]]:
    """record_path -> hard content-gate reasons, from the pinned source images."""

    if make_gate is None or not documents:
        return {}
    gate = make_gate(list(documents.values()))
    from uniprot_record_content_gate import hard_reasons  # noqa: PLC0415

    blocked: dict[str, list[str]] = {}
    for path, document in documents.items():
        reasons = hard_reasons(gate.evaluate(document))
        if reasons:
            blocked[path] = reasons
    return blocked


def default_content_gate(records: Sequence[Mapping[str, Any]]) -> Any:
    from uniprot_record_content_gate import (  # noqa: PLC0415
        ContentGateError,
        RecordContentGate,
    )

    try:
        return RecordContentGate(list(records))
    except ContentGateError as error:
        raise DufLeadError(f"record-content source replay failed closed: {error}") from error


def audit(
    snapshot: Snapshot,
    *,
    traits_root: Path = TRAITS_ROOT,
    index: Mapping[str, list[str]] | None = None,
    make_gate: Callable[..., Any] | None = default_content_gate,
) -> dict[str, Any]:
    """One status per lead; target leads sit on a Pfam record with no QUALIFIED example."""

    index = index if index is not None else cm.build_identifier_index(traits_root)
    families: dict[str, dict[str, Any]] = {}
    documents: dict[str, dict[str, Any]] = {}
    for pfam in sorted({row["pfam_id"] for row in snapshot.rows}):
        trait_id = f"Pfam:{pfam}"
        paths = index.get(trait_id) or []
        family: dict[str, Any] = {"trait_id": trait_id, "record_paths": paths}
        if len(paths) == 1:
            path = traits_root / paths[0]
            document = yaml.load(path.read_text(encoding="utf-8"), Loader=cm.Loader)  # noqa: S506
            if not isinstance(document, Mapping) or document.get("identifier") != trait_id:
                raise DufLeadError(f"{path} does not carry identifier {trait_id}")
            examples: dict[str, str] = {}
            for example in document.get("canonical_examples") or []:
                if isinstance(example, Mapping) and isinstance(example.get("protein_id"), str):
                    status = example.get("qualification_status") or "LEGACY_UNVERIFIED"
                    examples[example["protein_id"].strip()] = str(status)
            family.update(
                {
                    "record_path": f"data/traits/{paths[0]}",
                    "trait_axis": document.get("trait_axis"),
                    "trait_category": document.get("trait_category"),
                    "label": document.get("label"),
                    "examples": examples,
                    "record_state": (
                        "QUALIFIED"
                        if "QUALIFIED" in examples.values()
                        else "LEGACY_UNVERIFIED"
                        if examples
                        else "NO_PROTEIN"
                    ),
                }
            )
            if family["record_state"] != "QUALIFIED":
                documents[family["record_path"]] = dict(document)
        families[pfam] = family
    blocked = _content_blocked(documents, make_gate=make_gate)

    leads: list[dict[str, Any]] = []
    for row in snapshot.rows:
        family = families[row["pfam_id"]]
        lead: dict[str, Any] = {
            "trait_id": family["trait_id"],
            "protein_id": f"UniProtKB:{row['uniprot_accession']}",
            "pfam_id": row["pfam_id"],
            "lead_rank": row["rank"],
            "lead_reviewed": row["reviewed"],
            "lead_annotation_score": row["annotation_score"],
            "lead_selection_reasons": sorted(row["selection_reasons"]),
        }
        paths = family["record_paths"]
        if GAP_REASON not in row["selection_reasons"]:
            status = "OUT_OF_SCOPE_REASON"
        elif not paths:
            status = "TRAIT_NOT_IN_PTM"
        elif len(paths) > 1:
            status = "AMBIGUOUS_TRAIT_RECORD"
        else:
            lead.update(
                {
                    "record_path": family["record_path"],
                    "trait_axis": family["trait_axis"],
                    "trait_category": family["trait_category"],
                    "record_state": family["record_state"],
                    "scope": scope_for(family["trait_axis"], family["trait_category"]),
                }
            )
            if family["record_state"] == "QUALIFIED":
                status = "RECORD_ALREADY_QUALIFIED"
            elif family["record_path"] in blocked:
                status = "RECORD_CONTENT_BLOCKED"
                lead["content_gate_reasons"] = blocked[family["record_path"]]
            elif lead["protein_id"] in family["examples"]:
                status = "TARGET_LEGACY_ON_TRAIT"
            else:
                status = "TARGET_ABSENT_FROM_TRAIT"
        lead["status"] = status
        leads.append(lead)
    leads.sort(key=lambda lead: (lead["trait_id"], lead["lead_rank"], lead["protein_id"]))
    return {"leads": leads, "summary": audit_summary(snapshot, leads)}


def audit_summary(snapshot: Snapshot, leads: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    by_status = Counter(lead["status"] for lead in leads)
    target = [lead for lead in leads if lead["status"] in TARGET_STATUSES]
    records_by_status: dict[str, set[str]] = defaultdict(set)
    for lead in leads:
        records_by_status[lead["status"]].add(lead["trait_id"])
    return {
        "snapshot": snapshot.provenance(),
        "leads": len(leads),
        "leads_by_status": {status: by_status.get(status, 0) for status in LEAD_STATUSES},
        "families_by_status": {
            status: len(records_by_status.get(status, ())) for status in LEAD_STATUSES
        },
        "target_records": len({lead["trait_id"] for lead in target}),
        "target_records_by_scope": dict(
            sorted(Counter(lead["scope"] for lead in _one_per_record(target)).items())
        ),
        "target_leads_reviewed": sum(1 for lead in target if lead["lead_reviewed"]),
        "target_records_with_reviewed_lead": len(
            {lead["trait_id"] for lead in target if lead["lead_reviewed"]}
        ),
    }


def _one_per_record(leads: Iterable[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    seen: dict[str, Mapping[str, Any]] = {}
    for lead in leads:
        seen.setdefault(lead["trait_id"], lead)
    return list(seen.values())


# ------------------------------------------------------------------ discovery


def discovery_records(leads: Sequence[Mapping[str, Any]], max_records: int) -> list[str]:
    """Deterministic, bounded record choice: records with a reviewed lead first, then ID."""

    if max_records < 1:
        raise DufLeadError("--max-records must be positive")
    reviewed: dict[str, bool] = {}
    for lead in leads:
        if lead["status"] in TARGET_STATUSES:
            reviewed[lead["trait_id"]] = reviewed.get(lead["trait_id"], False) or bool(
                lead["lead_reviewed"]
            )
    ordered = sorted(reviewed, key=lambda trait_id: (not reviewed[trait_id], trait_id))
    return ordered[:max_records]


def discovery_plan(
    leads: Sequence[Mapping[str, Any]], *, max_records: int, snapshot: Mapping[str, Any]
) -> dict[str, Any]:
    records = discovery_records(leads, max_records)
    chosen = set(records)
    selected = [
        lead for lead in leads if lead["status"] in TARGET_STATUSES and lead["trait_id"] in chosen
    ]
    accessions = sorted({lead["protein_id"].removeprefix("UniProtKB:") for lead in selected})
    return {
        "schema_version": 1,
        "selection": "target records with a reviewed lead first, then trait_id; every target lead",
        "max_records": max_records,
        "snapshot": dict(snapshot),
        "records": records,
        "leads": [
            {"trait_id": lead["trait_id"], "protein_id": lead["protein_id"]} for lead in selected
        ],
        "accessions": accessions,
        "leads_sha256": sha256_bytes(canonical_json(selected).encode()),
    }


# ----------------------------------------------------------------- candidates


def verify_discovery_receipt(
    receipt: Mapping[str, Any],
    plan_raw: bytes,
    plan: Mapping[str, Any],
    sequences: Mapping[str, Mapping[str, Any]],
    *,
    uniprot_release: str,
) -> None:
    """The discovery receipt must bind these exact plan bytes and cover the plan."""

    if receipt.get("plan_sha256") != sha256_bytes(plan_raw):
        raise DufLeadError("discovery receipt does not bind the current discovery-plan.json")
    if receipt.get("expected_release") != uniprot_release:
        raise DufLeadError("discovery receipt was made for another UniProt release")
    planned = {f"UniProtKB:{accession}" for accession in plan["accessions"]}
    covered = set(sequences) | set(receipt.get("missing") or [])
    if covered != planned or receipt.get("discovered") != len(sequences):
        raise DufLeadError("discovery rows and receipt do not cover exactly the planned accessions")




def _intervals(value: Any) -> list[list[int]] | None:
    if not isinstance(value, list) or not value:
        return None
    out: list[list[int]] = []
    for item in value:
        if (
            not isinstance(item, list)
            or len(item) != 2
            or not all(isinstance(number, int) and not isinstance(number, bool) for number in item)
        ):
            return None
        out.append([item[0], item[1]])
    return sorted(out)


def _load_frame(path: Path, label: str) -> tuple[dict[str, Any], dict[str, Any]]:
    if not path.is_file():
        raise DufLeadError(f"no {label} at {path}; run `just fetch-duf-interpro-frame --apply`")
    blob = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(blob, dict) or not isinstance(blob.get("proteins"), dict):
        raise DufLeadError(f"{path} is not a release-stamped InterPro sidecar")
    meta = blob.get("_meta") or {}
    if meta.get("source") != "InterPro":
        raise DufLeadError(f"{path} is not an InterPro sidecar")
    return blob["proteins"], meta


def candidate_rows(
    leads: Sequence[Mapping[str, Any]],
    plan: Mapping[str, Any],
    sequences: Mapping[str, Mapping[str, Any]],
    frame: Mapping[str, Any],
    grouped: Mapping[str, Any],
    *,
    uniprot_release: str,
    interpro_release: str,
    frame_release: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Funnel candidates and rejections for the planned leads, from pinned providers only."""

    if _RELEASE.fullmatch(uniprot_release) is None:
        raise DufLeadError(f"--uniprot-release must look like 2026_03, got {uniprot_release!r}")
    if _INTERPRO_RELEASE.fullmatch(interpro_release) is None:
        raise DufLeadError(f"--interpro-release must look like 110.0, got {interpro_release!r}")
    if frame_release != interpro_release:
        raise DufLeadError(
            f"DUF InterPro frame release {frame_release!r} is not the pinned {interpro_release!r}"
        )
    from ground_uniprot_examples import (  # noqa: PLC0415
        derive_candidate_id,
        derive_interpro_location_id,
    )

    wanted = {(lead["trait_id"], lead["protein_id"]) for lead in plan["leads"]}
    planned = [lead for lead in leads if (lead["trait_id"], lead["protein_id"]) in wanted]
    if len(planned) != len(wanted):
        raise DufLeadError("the discovery plan names leads the current audit does not have")
    candidates: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []

    def reject(lead: Mapping[str, Any], reason: str, detail: str = "") -> None:
        rejected.append(
            {
                "trait_id": lead["trait_id"],
                "record_path": lead.get("record_path", ""),
                "protein_id": lead["protein_id"],
                "lead_reviewed": lead["lead_reviewed"],
                "reason": reason,
                "detail": detail,
            }
        )

    for lead in planned:
        if lead["status"] not in TARGET_STATUSES:
            reject(lead, f"NOT_A_TARGET:{lead['status']}")
            continue
        identity = sequences.get(lead["protein_id"])
        if identity is None:
            reject(lead, "NOT_RETURNED_BY_PINNED_UNIPROT", uniprot_release)
            continue
        if identity["uniprot_release"] != uniprot_release:
            raise DufLeadError(
                f"{lead['protein_id']} was discovered in {identity['uniprot_release']}, "
                f"not the pinned {uniprot_release}"
            )
        accession = lead["protein_id"].removeprefix("UniProtKB:")
        matches = frame.get(accession)
        if not isinstance(matches, dict):
            reject(lead, "ACCESSION_NOT_IN_INTERPRO_FRAME", interpro_release)
            continue
        flat = matches.get(lead["trait_id"])
        if flat is None:
            reject(lead, "NO_EXACT_INTERPRO_MATCH", f"InterPro {interpro_release}")
            continue
        intervals = _intervals(flat)
        if intervals is None:
            reject(lead, "MALFORMED_INTERPRO_INTERVAL")
            continue
        length = identity["sequence_length"]
        if any(not (1 <= start <= end <= length) for start, end in intervals):
            reject(lead, "INTERPRO_INTERVAL_OUT_OF_BOUNDS", f"length {length}")
            continue
        groups: list[tuple[str | None, list[list[int]]]] = []
        if lead["scope"] == "WHOLE_PROTEIN":
            groups.append((None, intervals))
        else:
            raw_groups = (grouped.get(accession) or {}).get(lead["trait_id"])
            if isinstance(raw_groups, list) and raw_groups:
                seen: set[str] = set()
                for raw in raw_groups:
                    group = _intervals(raw)
                    if group is None:
                        groups = []
                        break
                    location_id = derive_interpro_location_id(
                        lead["protein_id"],
                        lead["trait_id"],
                        [{"start": start, "end": end} for start, end in group],
                    )
                    if location_id not in seen:
                        seen.add(location_id)
                        groups.append((location_id, group))
                if not groups:
                    reject(lead, "MALFORMED_INTERPRO_GROUPED_LOCATION")
                    continue
            elif len(intervals) == 1:
                groups.append((None, intervals))
            else:
                reject(lead, "UNGROUPED_INTERPRO_LOCATIONS", f"{len(intervals)} ranges")
                continue
        for location_id, group in groups:
            row: dict[str, Any] = {
                "schema_version": 1,
                "batch": CANDIDATE_BATCH,
                "candidate_status": "CANDIDATE_PROTEIN",
                "qualification_status": "CANDIDATE_PROTEIN",
                "trait_id": lead["trait_id"],
                "record_path": lead["record_path"],
                "trait_axis": lead["trait_axis"],
                "trait_category": lead["trait_category"],
                "source_namespace": "Pfam",
                "protein_id": lead["protein_id"],
                "sequence_length": length,
                "sequence_sha256": identity["sequence_sha256"],
                "sequence_source": "UniProt",
                "sequence_release": identity["uniprot_release"],
                "scope": lead["scope"],
                "intervals": [{"start": start, "end": end} for start, end in group],
                "residue_positions": [],
                "source_trait_id": lead["trait_id"],
                "mapping_method": "INTERPRO_MATCH",
                "evidence_source": "InterPro",
                "source_release": interpro_release,
                "evidence_tier": "A",
                "reasons": [],
                "duf_lead_provenance": {
                    **plan["snapshot"],
                    "lead_status": lead["status"],
                    "lead_rank": lead["lead_rank"],
                    "lead_reviewed": lead["lead_reviewed"],
                    "lead_selection_reasons": lead["lead_selection_reasons"],
                },
            }
            if lead["scope"] == "LOCALIZED":
                row["coordinate_frame"] = "UNIPROT_CANONICAL"
            if location_id:
                row["interpro_location_id"] = location_id
            row["candidate_id"] = derive_candidate_id(row)
            candidates.append(row)
    candidates.sort(key=lambda row: (row["trait_id"], row["protein_id"], row["candidate_id"]))
    if len({row["candidate_id"] for row in candidates}) != len(candidates):
        raise DufLeadError("internal error: duplicate candidate IDs")
    rejected.sort(key=lambda row: (row["trait_id"], row["protein_id"], row["reason"]))
    return candidates, rejected


# ------------------------------------------------------------------- commands


def _snapshot_from_args(args: argparse.Namespace) -> Snapshot:
    return load_snapshot(Path(args.dufmech_repo))


def cmd_audit(args: argparse.Namespace) -> int:
    snapshot = _snapshot_from_args(args)
    result = audit(
        snapshot,
        traits_root=Path(args.traits),
        make_gate=None if args.no_content_gate else default_content_gate,
    )
    summary = result["summary"]
    summary["content_gate"] = not args.no_content_gate
    print(json.dumps(summary, indent=2, sort_keys=True))
    if not args.apply:
        print(f"dry run: pass --apply to write {args.out}/leads.jsonl and summary.json")
        return 0
    out = Path(args.out)
    _write_jsonl(out / "leads.jsonl", result["leads"])
    _write_json(out / "summary.json", summary)
    print(f"WROTE {out / 'leads.jsonl'}")
    return 0


def cmd_discover(args: argparse.Namespace) -> int:
    out = Path(args.out)
    leads = _read_jsonl(out / "leads.jsonl")
    summary = json.loads((out / "summary.json").read_text(encoding="utf-8"))
    plan = discovery_plan(leads, max_records=args.max_records, snapshot=summary["snapshot"])
    requests = (len(plan["accessions"]) + 99) // 100
    print(
        f"{len(plan['records']):,} target records, {len(plan['leads']):,} leads, "
        f"{len(plan['accessions']):,} accessions -> {requests} UniProt request(s); "
        f"the InterPro crawl is `just fetch-duf-interpro-frame` "
        f"(~{len(plan['accessions']):,} InterPro request(s))"
    )
    if not args.apply:
        print("dry run: no network access; pass --apply to read UniProt and write the plan")
        return 0
    result = cm.discover_sequences(
        [f"UniProtKB:{accession}" for accession in plan["accessions"]],
        expected_release=args.uniprot_release,
    )
    _write_json(out / "discovery-plan.json", plan)
    cm._atomic_write(out / "accessions.txt", "".join(f"{a}\n" for a in plan["accessions"]))
    _write_jsonl(out / "discovery.jsonl", result["rows"])
    _write_json(
        out / "discovery.receipt.json",
        {
            "expected_release": args.uniprot_release,
            "responses": result["responses"],
            "missing": result["missing"],
            "discovered": len(result["rows"]),
            "plan_sha256": sha256_bytes((out / "discovery-plan.json").read_bytes()),
        },
    )
    print(f"discovered {len(result['rows']):,}; missing {len(result['missing']):,}")
    print(f"WROTE {out / 'discovery-plan.json'}, accessions.txt, discovery.jsonl")
    return 0


def cmd_candidates(args: argparse.Namespace) -> int:
    out = Path(args.out)
    leads = _read_jsonl(out / "leads.jsonl")
    plan_raw = (out / "discovery-plan.json").read_bytes()
    plan = json.loads(plan_raw)
    sequences = cm.load_discovery(out / "discovery.jsonl")
    verify_discovery_receipt(
        json.loads((out / "discovery.receipt.json").read_text(encoding="utf-8")),
        plan_raw,
        plan,
        sequences,
        uniprot_release=args.uniprot_release,
    )
    frame, meta = _load_frame(Path(args.interpro_frame), "DUF InterPro frame")
    grouped, grouped_meta = _load_frame(Path(args.interpro_grouped_frame), "grouped DUF frame")
    if grouped_meta.get("release") != meta.get("release"):
        raise DufLeadError("compact and grouped DUF InterPro frames have different releases")
    candidates, rejected = candidate_rows(
        leads,
        plan,
        sequences,
        frame,
        grouped,
        uniprot_release=args.uniprot_release,
        interpro_release=args.interpro_release,
        frame_release=str(meta.get("release")),
    )
    report = {
        "candidates": len(candidates),
        "candidate_records": len({row["trait_id"] for row in candidates}),
        "candidate_proteins": len({row["protein_id"] for row in candidates}),
        "candidates_by_scope": dict(sorted(Counter(row["scope"] for row in candidates).items())),
        "planned_records": len(plan["records"]),
        "planned_leads": len(plan["leads"]),
        "rejected_leads": len(rejected),
        "rejected_by_reason": dict(sorted(Counter(row["reason"] for row in rejected).items())),
        "interpro_release": meta.get("release"),
        "uniprot_release": args.uniprot_release,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    if not args.apply:
        print(f"dry run: pass --apply to write {out / 'candidates.jsonl'}")
        return 0
    _write_jsonl(out / "candidates.jsonl", candidates)
    _write_jsonl(out / "rejected.jsonl", rejected)
    _write_json(out / "candidates.summary.json", report)
    print(f"WROTE {out / 'candidates.jsonl'} and rejected.jsonl")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = parser.add_subparsers(dest="command", required=True)

    audit_parser = sub.add_parser("audit", help="join the pinned DUFMech leads to data/traits")
    audit_parser.add_argument("--dufmech-repo", default=str(REPO_ROOT.parent / "DUFMech"))
    audit_parser.add_argument("--traits", default=str(TRAITS_ROOT))
    audit_parser.add_argument(
        "--no-content-gate",
        action="store_true",
        help="skip the pinned record-content replay (tests and diagnostics only)",
    )
    audit_parser.add_argument("--out", default=str(OUT_DIR))
    audit_parser.add_argument("--apply", action="store_true")
    audit_parser.set_defaults(func=cmd_audit)

    discover_parser = sub.add_parser("discover", help="bounded plan + pinned sequence identity")
    discover_parser.add_argument("--uniprot-release", required=True)
    discover_parser.add_argument(
        "--max-records",
        type=int,
        default=100,
        help="target records to crawl; keep it equal to the review batch's --max-records, "
        "because the selector draws records in hash order and would drop the "
        "reviewed-lead preference from a larger set",
    )
    discover_parser.add_argument("--out", default=str(OUT_DIR))
    discover_parser.add_argument("--apply", action="store_true")
    discover_parser.set_defaults(func=cmd_discover)

    candidates_parser = sub.add_parser("candidates", help="emit grounding-funnel candidates")
    candidates_parser.add_argument("--uniprot-release", required=True)
    candidates_parser.add_argument("--interpro-release", required=True)
    candidates_parser.add_argument("--interpro-frame", default=str(DUF_INTERPRO_FRAME))
    candidates_parser.add_argument(
        "--interpro-grouped-frame", default=str(DUF_INTERPRO_GROUPED_FRAME)
    )
    candidates_parser.add_argument("--out", default=str(OUT_DIR))
    candidates_parser.add_argument("--apply", action="store_true")
    candidates_parser.set_defaults(func=cmd_candidates)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except (DufLeadError, cm.CrossMechError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
