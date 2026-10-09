#!/usr/bin/env python3
"""Strict helpers for release-pinned UniProt database membership snapshots.

The UniProt search query that discovers a candidate is not occurrence evidence.  A
membership becomes replayable only after an exact-accession response independently
returns the same database cross-reference together with the protein sequence and the
``x-uniprot-release`` header.  This module normalizes each such positive fact into one
content-addressed JSONL row.

The rows are deliberately independent of candidate IDs and rankings.  A resolver must
look up the exact ``(protein_id, source_trait_id, uniprot_release, sequence_sha256)``
tuple and must never infer membership from absence, a query string, or a generic hit.

Three kinds of exact UniProt fact share this one snapshot (#652):

* a signature cross-reference (Pfam, InterPro, ...) and a ``ComplexPortal``
  cross-reference -- exact *membership* of the protein in the source class;
* a ``GO`` cross-reference -- an exact *annotation* to the GO term, with UniProt's
  ``GoEvidenceType`` preserved in the stored object so its evidence code is never lost.
  A ``ND`` (no biological data) annotation is not a fact and is never captured;
* a Rhea reaction cross-reference inside a ``CATALYTIC ACTIVITY`` comment -- exact
  membership of the protein among the catalysts of that master reaction, stored as the
  returned ``{"database": "Rhea", "id": "RHEA:n"}`` object plus that reaction's own
  returned ``evidences``, so its evidence strength stays auditable.  Directional
  ``physiologicalReactions``, ``RHEA-COMP:`` participant compounds, and a comment scoped
  to an isoform or chain (``molecule``) are never captured.

Capturing a fact is not qualifying it. :func:`fact_evidence_failure` is the default-deny
evidence policy the resolver and the validator share (#974): the plan keeps "EC-only,
textual, homology-only, or generic pathway inference" as candidate evidence, so a GO
annotation qualifies only with an experimental or curator code and a catalytic activity
only with experimental or curator-inference evidence. One narrow widening is the
maintainer's decision on #1004: on a reviewed Swiss-Prot entry, ``IEA:UniProtKB-EC`` GO
terms and catalytic activities curated without an evidence tag qualify; such facts
record ``uniprot_entry_type``. An EC-derived GO fact also records the entry's EC
assignments (``uniprot_ec_evidence``) and qualifies only when none of them is inferred
by similarity, sequence model, or automatic annotation (#1048). Any further widening is
again a maintainer decision.

:func:`expected_mapping_method` names the occurrence method each fact may support, so a
GO annotation can never be recorded as a membership or the reverse.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any, Iterable, Mapping

SCHEMA_VERSION = 1
MEMBERSHIP_ID_PREFIX = "ug-membership:"
UNIPROT_SEARCH = "https://rest.uniprot.org/uniprotkb/search"

# REST return field, JSON ``database`` value, corpus CURIE prefix.  Gene3D is
# UniProt's CATH-backed cross-reference; SUPFAM is UniProt's SUPERFAMILY name.
XREF_SPECS: tuple[tuple[str, str, str], ...] = (
    ("xref_cdd", "CDD", "CDD"),
    ("xref_gene3d", "Gene3D", "CATH"),
    ("xref_hamap", "HAMAP", "HAMAP"),
    ("xref_interpro", "InterPro", "InterPro"),
    ("xref_ncbifam", "NCBIfam", "NCBIfam"),
    ("xref_panther", "PANTHER", "PANTHER"),
    ("xref_pfam", "Pfam", "Pfam"),
    ("xref_prints", "PRINTS", "PRINTS"),
    ("xref_prosite", "PROSITE", "PROSITE"),
    ("xref_sfld", "SFLD", "SFLD"),
    ("xref_smart", "SMART", "SMART"),
    ("xref_supfam", "SUPFAM", "SUPERFAMILY"),
    # Functional facts for whole-protein FUNCTION records.  `go_id` is the REST field
    # that returns GO cross-references (there is no `xref_go`).
    ("xref_complexportal", "ComplexPortal", "ComplexPortal"),
    ("go_id", "GO", "GO"),
)
XREF_FIELDS = tuple(spec[0] for spec in XREF_SPECS)
# Rhea is not a cross-reference: UniProt states it inside CATALYTIC ACTIVITY comments.
CATALYTIC_ACTIVITY_FIELD = "cc_catalytic_activity"
FACT_FIELDS = (*XREF_FIELDS, CATALYTIC_ACTIVITY_FIELD)
RHEA_DATABASE = "Rhea"
RHEA_COMPOUND_PREFIX = "RHEA-COMP:"
DATABASE_TO_NAMESPACE = {database: namespace for _, database, namespace in XREF_SPECS}
DATABASE_TO_NAMESPACE[RHEA_DATABASE] = "RHEA"

# Default-deny evidence policy for the functional facts (#974). GO codes: experimental
# (EXP IDA IPI IMP IGI IEP and the high-throughput HTP HDA HMP HGI HEP) and curator (IC,
# TAS). ECO for catalytic activities: experimental (0000269), curator inference
# (0000305), and traceable author statement (0000304). Excluded on purpose: IEA, IBA and
# the ISS family (homology), NAS (untraceable text), RCA, and ECO 0000250/0000255/0000256
# (similarity, sequence model, automatic).
GO_QUALIFYING_EVIDENCE = frozenset(
    {"EXP", "IDA", "IPI", "IMP", "IGI", "IEP", "HTP", "HDA", "HMP", "HGI", "HEP", "IC", "TAS"}
)
RHEA_QUALIFYING_ECO = frozenset({"ECO:0000269", "ECO:0000304", "ECO:0000305"})
# Narrow, maintainer-approved widening (#1004): on a reviewed Swiss-Prot entry, a GO
# term inferred from the entry's curated EC number (IEA:UniProtKB-EC) and a catalytic
# activity curated without an evidence tag also qualify. Neither holds on TrEMBL, and
# every other IEA source, IBA, NAS and automatic ECO stays excluded. The EC number must
# itself be curated, not inferred (#1048): every evidence code on the entry's EC
# assignments (protein names and catalytic activities) must be absent or one of
# RHEA_QUALIFYING_ECO, so a by-similarity or sequence-model EC does not qualify.
SWISSPROT_ENTRY_TYPE = "UniProtKB reviewed (Swiss-Prot)"
TREMBL_ENTRY_TYPE = "UniProtKB unreviewed (TrEMBL)"
ENTRY_TYPES = frozenset({SWISSPROT_ENTRY_TYPE, TREMBL_ENTRY_TYPE})
SWISSPROT_ONLY_GO_EVIDENCE = frozenset({"IEA:UniProtKB-EC"})

# The occurrence method a UniProt fact may support.  Everything else is membership.
UNIPROT_FACT_METHODS = frozenset({"SOURCE_MEMBERSHIP", "SOURCE_ANNOTATION"})
ANNOTATION_NAMESPACES = frozenset({"GO"})
_GO_ID = re.compile(r"^GO:[0-9]{7}$")
_RHEA_ID = re.compile(r"^RHEA:[1-9][0-9]*$")
_COMPLEXPORTAL_ID = re.compile(r"^CPX-[1-9][0-9]*$")
_ECO_ID = re.compile(r"^ECO:[0-9]{7}$")

_UNIPROT = re.compile(
    r"^UniProtKB:([OPQ][0-9][A-Z0-9]{3}[0-9]|"
    r"[A-NR-Z][0-9](?:[A-Z][A-Z0-9]{2}[0-9]){1,2})(?:-([0-9]+))?$"
)
_RELEASE = re.compile(r"^[0-9]{4}_[0-9]{2}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")

_PAYLOAD_FIELDS = (
    "schema_version",
    "protein_id",
    "source_trait_id",
    "database",
    "database_id",
    "uniprot_release",
    "sequence_sha256",
    "api_endpoint",
    "database_cross_reference",
)
# Recorded only on a fact whose evidence the Swiss-Prot rule decides (#1004), so every
# fact captured before that rule keeps its content address.
_OPTIONAL_PAYLOAD_FIELDS = ("uniprot_entry_type", "uniprot_ec_evidence")
_ALLOWED_FIELDS = {"membership_id", *_PAYLOAD_FIELDS, *_OPTIONAL_PAYLOAD_FIELDS}


class MembershipSnapshotError(ValueError):
    """A membership snapshot is malformed, ambiguous, or not content-addressed."""


def _trait_local_id(database: str, database_id: str) -> str:
    """Map an exact provider ID to the corpus local ID without losing the raw ID.

    UniProt returns CATH-Gene3D superfamilies as ``G3DSA:<CATH-code>`` while
    ProteinTraitsMech keys the same identifiers as ``CATH:<CATH-code>``.  The
    original provider object and ``database_id`` remain unchanged in the row.
    """

    if database == "Gene3D" and database_id.startswith("G3DSA:"):
        local_id = database_id.removeprefix("G3DSA:")
        if not local_id:
            raise MembershipSnapshotError("Gene3D cross-reference has an empty G3DSA ID")
        return local_id
    # GO and Rhea return a full CURIE as their ID; ComplexPortal a bare CPX accession.
    if database == "GO":
        if _GO_ID.fullmatch(database_id) is None:
            raise MembershipSnapshotError(f"GO cross-reference has a malformed ID {database_id!r}")
        return database_id.removeprefix("GO:")
    if database == RHEA_DATABASE:
        if _RHEA_ID.fullmatch(database_id) is None:
            raise MembershipSnapshotError(f"Rhea reaction has a malformed ID {database_id!r}")
        return database_id.removeprefix("RHEA:")
    if database == "ComplexPortal" and _COMPLEXPORTAL_ID.fullmatch(database_id) is None:
        raise MembershipSnapshotError(
            f"ComplexPortal cross-reference has a malformed ID {database_id!r}"
        )
    return database_id


def expected_mapping_method(source_trait_id: str) -> str:
    """The only occurrence method an exact UniProt fact for this trait may support."""

    namespace = source_trait_id.split(":", 1)[0] if ":" in source_trait_id else ""
    return "SOURCE_ANNOTATION" if namespace in ANNOTATION_NAMESPACES else "SOURCE_MEMBERSHIP"


def fact_evidence_failure(row: Mapping[str, Any]) -> str | None:
    """Why a captured UniProt fact may not qualify on its evidence, or None (#974).

    Signature and ComplexPortal facts carry no per-entry evidence and are governed by
    their existing contracts; ComplexPortal is itself manually curated.
    """

    database = row.get("database")
    xref = row.get("database_cross_reference")
    xref = xref if isinstance(xref, Mapping) else {}
    if database == "GO":
        code = _go_evidence_code(xref)
        if code in GO_QUALIFYING_EVIDENCE:
            return None
        if _swissprot_conditional(row):
            label = f"go_evidence_{_go_evidence_value(xref)}"
            return _swissprot_failure(row, label) or _ec_evidence_failure(row, label)
        return f"go_evidence_{code or 'missing'}"
    if database == RHEA_DATABASE:
        codes = _rhea_evidence_codes(xref)
        if set(codes) & RHEA_QUALIFYING_ECO:
            return None
        if _swissprot_conditional(row):
            return _swissprot_failure(row, "rhea_evidence_missing")
        return "rhea_evidence_" + ("+".join(codes) if codes else "missing")
    return None


# Strength order among qualifying GO evidence, for choosing between facts (#1050):
# direct experimental, then indirect experimental, then curator, then the EC rule.
_GO_EVIDENCE_RANK = {
    **{code: 0 for code in ("EXP", "IDA", "IPI", "HTP", "HDA")},
    **{code: 1 for code in ("IMP", "IGI", "IEP", "HMP", "HGI", "HEP")},
    **{code: 2 for code in ("IC", "TAS")},
}


def fact_evidence_rank(row: Mapping[str, Any]) -> int:
    """Lower is stronger: the order in which qualifying GO facts are preferred."""

    xref = row.get("database_cross_reference")
    code = _go_evidence_code(xref if isinstance(xref, Mapping) else {})
    return _GO_EVIDENCE_RANK.get(code, 3)


def _ec_evidence_failure(row: Mapping[str, Any], label: str) -> str | None:
    """The #1048 condition on an EC-derived GO term: its EC must itself be curated."""

    evidence = row.get("uniprot_ec_evidence")
    if not evidence:
        return f"{label}_ec_evidence_missing"
    weak = sorted(
        {code for item in evidence for code in item.get("evidence_codes", [])}
        - RHEA_QUALIFYING_ECO
    )
    if weak:
        return f"{label}_ec_evidence_" + "+".join(weak)
    return None


def _entry_ec_evidence(entry: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Every EC assignment on an entry, with the union of its evidence codes (#1048).

    EC numbers come from the protein names (recommended, alternative and submission
    names, including those of included domains and contained chains) and from
    catalytic-activity reactions, so a weak tag on either statement of an EC is kept.
    Every EC on the entry is listed: which one an EC-derived GO term came from is not in
    the response, so one weak EC withholds them all.
    """

    found: dict[str, set[str]] = {}

    def objects(value: object, where: str) -> list[Mapping[str, Any]]:
        # A malformed container must not hide a weak EC (#1055): fail the accession.
        if value is None:
            return []
        if not isinstance(value, list) or any(not isinstance(item, Mapping) for item in value):
            raise MembershipSnapshotError(f"{where} is not a list of objects")
        return value

    def add(value: object, evidences: object, where: str) -> None:
        if value is None:
            return
        if not isinstance(value, str) or not value.strip():
            raise MembershipSnapshotError(f"{where} has a malformed EC number")
        codes = found.setdefault(value.strip(), set())
        for item in objects(evidences, f"{where} evidences"):
            code = item.get("evidenceCode")
            if not isinstance(code, str):
                raise MembershipSnapshotError(f"{where} has an evidence without evidenceCode")
            codes.add(code)

    description = entry.get("proteinDescription")
    if description is not None and not isinstance(description, Mapping):
        raise MembershipSnapshotError("proteinDescription is not an object")
    blocks: list[Mapping[str, Any]] = []
    if isinstance(description, Mapping):
        blocks.append(description)
        for key in ("includes", "contains"):
            blocks += objects(description.get(key), f"proteinDescription.{key}")
    for block in blocks:
        recommended = block.get("recommendedName")
        if recommended is not None and not isinstance(recommended, Mapping):
            raise MembershipSnapshotError("recommendedName is not an object")
        names = [recommended] if recommended is not None else []
        names += objects(block.get("alternativeNames"), "alternativeNames")
        names += objects(block.get("submissionNames"), "submissionNames")
        for name in names:
            for ec in objects(name.get("ecNumbers"), "ecNumbers"):
                add(ec.get("value"), ec.get("evidences"), "ecNumbers")
    for comment in objects(entry.get("comments"), "comments"):
        if comment.get("commentType") != "CATALYTIC ACTIVITY":
            continue
        reaction = comment.get("reaction")
        if reaction is None:
            continue
        if not isinstance(reaction, Mapping):
            raise MembershipSnapshotError("catalytic-activity reaction is not an object")
        add(reaction.get("ecNumber"), reaction.get("evidences"), "catalytic-activity reaction")
    return [
        {"ec_number": ec, "evidence_codes": sorted(codes)} for ec, codes in sorted(found.items())
    ]


def _ec_evidence_errors(value: object) -> list[str]:
    if not isinstance(value, list):
        return ["uniprot_ec_evidence must be a list"]
    errors: list[str] = []
    numbers = []
    for item in value:
        if (
            not isinstance(item, dict)
            or set(item) != {"ec_number", "evidence_codes"}
            or not isinstance(item["ec_number"], str)
            or not item["ec_number"]
            or item["ec_number"] != item["ec_number"].strip()
            or not isinstance(item["evidence_codes"], list)
            or any(
                not isinstance(code, str) or _ECO_ID.fullmatch(code) is None
                for code in item["evidence_codes"]
            )
            or item["evidence_codes"] != sorted(set(item["evidence_codes"]))
        ):
            return ["uniprot_ec_evidence items must be {ec_number, sorted unique ECO codes}"]
        numbers.append(item["ec_number"])
    if numbers != sorted(set(numbers)):
        errors.append("uniprot_ec_evidence must list each EC number once, sorted")
    return errors


def _rhea_evidence_codes(cross_reference: Mapping[str, Any]) -> list[str]:
    return sorted(
        {
            str(item.get("evidenceCode"))
            for item in cross_reference.get("evidences") or []
            if isinstance(item, Mapping) and item.get("evidenceCode")
        }
    )


def _swissprot_conditional(row: Mapping[str, Any]) -> bool:
    """Whether the fact's evidence qualifies only on a Swiss-Prot entry (#1004)."""

    xref = row.get("database_cross_reference")
    xref = xref if isinstance(xref, Mapping) else {}
    if row.get("database") == "GO":
        return _go_evidence_value(xref) in SWISSPROT_ONLY_GO_EVIDENCE
    if row.get("database") == RHEA_DATABASE:
        return not (xref.get("evidences") or [])
    return False


def _swissprot_failure(row: Mapping[str, Any], label: str) -> str | None:
    entry_type = row.get("uniprot_entry_type")
    if entry_type == SWISSPROT_ENTRY_TYPE:
        return None
    if entry_type == TREMBL_ENTRY_TYPE:
        return f"{label}_on_trembl"
    return f"{label}_entry_type_missing"


def _go_evidence_code(cross_reference: Mapping[str, Any]) -> str:
    """The GO evidence code (``IDA``, ``IEA``, ...) UniProt attached to a GO xref."""

    return _go_evidence_value(cross_reference).split(":", 1)[0].strip()


def _go_evidence_value(cross_reference: Mapping[str, Any]) -> str:
    """The full GO evidence (``IEA:UniProtKB-EC``), code plus assigning source."""

    for item in cross_reference.get("properties") or []:
        if isinstance(item, dict) and item.get("key") == "GoEvidenceType":
            value = item.get("value")
            if isinstance(value, str):
                return value.strip()
    return ""


def canonical_json(value: Any) -> str:
    """Return deterministic JSON used by every membership digest."""

    return json.dumps(
        value,
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _canonical_value(value: Any) -> Any:
    """Copy a JSON value into a deterministic, lossless Python shape."""

    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise MembershipSnapshotError("database cross-reference contains non-finite JSON")
        return value
    if isinstance(value, list):
        return [_canonical_value(item) for item in value]
    if isinstance(value, dict):
        if any(not isinstance(key, str) for key in value):
            raise MembershipSnapshotError("database cross-reference has a non-string key")
        return {key: _canonical_value(value[key]) for key in sorted(value)}
    raise MembershipSnapshotError(
        f"database cross-reference contains non-JSON value {type(value).__name__}"
    )


def _normalise_cross_reference(value: Mapping[str, Any]) -> dict[str, Any]:
    """Preserve the exact returned object while stabilizing property ordering."""

    normalized = _canonical_value(dict(value))
    # Properties and evidences are sets in UniProt's model; sort them so equal facts
    # always serialize, and therefore content-address, identically.
    for key in ("properties", "evidences"):
        items = normalized.get(key)
        if items is None:
            continue
        if not isinstance(items, list) or any(not isinstance(item, dict) for item in items):
            raise MembershipSnapshotError(
                f"database cross-reference {key} must be a list of objects"
            )
        normalized[key] = sorted(items, key=canonical_json)
    return normalized


def canonical_membership_payload(value: Mapping[str, Any]) -> dict[str, Any]:
    """Return the complete projection addressed by ``membership_id``."""

    payload = {field: value.get(field) for field in _PAYLOAD_FIELDS}
    payload.update({field: value[field] for field in _OPTIONAL_PAYLOAD_FIELDS if field in value})
    return payload


def membership_entry_sha256(value: Mapping[str, Any]) -> str:
    """Digest of the exact provider fact used as GroundingEvidence entry hash."""

    encoded = canonical_json(canonical_membership_payload(value)).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def compute_membership_id(value: Mapping[str, Any]) -> str:
    """Return the content address for one normalized membership fact."""

    return MEMBERSHIP_ID_PREFIX + membership_entry_sha256(value)


def _validate_membership(value: object) -> list[str]:
    if not isinstance(value, dict):
        return ["membership row is not an object"]
    errors: list[str] = []
    missing = sorted(_ALLOWED_FIELDS - set(_OPTIONAL_PAYLOAD_FIELDS) - set(value))
    unknown = sorted(set(value) - _ALLOWED_FIELDS)
    if missing:
        errors.append(f"missing fields {missing}")
    if unknown:
        errors.append(f"unknown fields {unknown}")
    if value.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must equal {SCHEMA_VERSION}")
    protein_id = value.get("protein_id")
    if not isinstance(protein_id, str) or _UNIPROT.fullmatch(protein_id) is None:
        errors.append("protein_id is not an exact UniProtKB accession")
    release = value.get("uniprot_release")
    if not isinstance(release, str) or _RELEASE.fullmatch(release) is None:
        errors.append("uniprot_release must have form YYYY_NN")
    sequence_sha = value.get("sequence_sha256")
    if not isinstance(sequence_sha, str) or _SHA256.fullmatch(sequence_sha) is None:
        errors.append("sequence_sha256 must be 64 lower-case hex digits")
    if value.get("api_endpoint") != UNIPROT_SEARCH:
        errors.append("api_endpoint is not the official UniProtKB search endpoint")
    if "uniprot_entry_type" in value:
        if value["uniprot_entry_type"] not in ENTRY_TYPES:
            errors.append(f"uniprot_entry_type must be one of {sorted(ENTRY_TYPES)}")
        elif not _swissprot_conditional(value):
            errors.append("uniprot_entry_type is recorded only where the Swiss-Prot rule applies")
    if "uniprot_ec_evidence" in value:
        if not (
            value.get("database") == "GO"
            and _swissprot_conditional(value)
            and "uniprot_entry_type" in value
        ):
            errors.append("uniprot_ec_evidence is recorded only on a stamped EC-derived GO fact")
        else:
            errors.extend(_ec_evidence_errors(value["uniprot_ec_evidence"]))

    database = value.get("database")
    database_id = value.get("database_id")
    namespace = DATABASE_TO_NAMESPACE.get(database) if isinstance(database, str) else None
    if namespace is None:
        errors.append(f"unsupported database {database!r}")
    if (
        not isinstance(database_id, str)
        or not database_id.strip()
        or database_id != database_id.strip()
    ):
        errors.append("database_id must be a non-empty, trimmed string")
    expected_trait: str | None = None
    if namespace and isinstance(database, str) and isinstance(database_id, str):
        try:
            expected_trait = f"{namespace}:{_trait_local_id(database, database_id)}"
        except MembershipSnapshotError as exc:
            errors.append(str(exc))
    if value.get("source_trait_id") != expected_trait:
        errors.append(
            f"source_trait_id must be the exact mapped database identifier {expected_trait!r}"
        )

    raw = value.get("database_cross_reference")
    if not isinstance(raw, dict):
        errors.append("database_cross_reference must be an object")
    else:
        try:
            normalized = _normalise_cross_reference(raw)
        except MembershipSnapshotError as exc:
            errors.append(str(exc))
        else:
            if normalized != raw:
                errors.append("database_cross_reference is not in canonical form")
            if raw.get("database") != database or raw.get("id") != database_id:
                errors.append("database/id do not match the preserved cross-reference")

    membership_id = value.get("membership_id")
    if not isinstance(membership_id, str) or not re.fullmatch(
        rf"{re.escape(MEMBERSHIP_ID_PREFIX)}[0-9a-f]{{64}}", membership_id
    ):
        errors.append("membership_id must be ug-membership: plus 64 lower-case hex digits")
    else:
        try:
            expected_id = compute_membership_id(value)
        except (TypeError, ValueError) as exc:
            errors.append(f"membership payload cannot be canonicalized: {exc}")
        else:
            if membership_id != expected_id:
                errors.append(f"membership_id digest mismatch; expected {expected_id}")
    return errors


def extract_entry_memberships(
    entry: Mapping[str, Any],
    *,
    protein_id: str,
    sequence_sha256: str,
    uniprot_release: str,
) -> list[dict[str, Any]]:
    """Extract supported positive facts from one exact UniProt response entry."""

    if _UNIPROT.fullmatch(protein_id) is None:
        raise MembershipSnapshotError(f"invalid protein_id {protein_id!r}")
    if _SHA256.fullmatch(sequence_sha256) is None:
        raise MembershipSnapshotError("invalid sequence_sha256")
    if _RELEASE.fullmatch(uniprot_release) is None:
        raise MembershipSnapshotError("invalid uniprot_release")
    entry_type = entry.get("entryType")
    # Read only for an entry that has an EC-derived GO fact to stamp (#1048, #1055).
    ec_evidence: list[list[dict[str, Any]]] = []
    raw_cross_references = entry.get("uniProtKBCrossReferences", [])
    if raw_cross_references is None:
        raw_cross_references = []
    if not isinstance(raw_cross_references, list):
        raise MembershipSnapshotError("uniProtKBCrossReferences is not a list")

    by_key: dict[tuple[str, str, str, str], dict[str, Any]] = {}

    def add(raw: dict[str, Any], location: str) -> None:
        database = raw.get("database")
        namespace = DATABASE_TO_NAMESPACE.get(database) if isinstance(database, str) else None
        if namespace is None:
            return
        database_id = raw.get("id")
        if not isinstance(database_id, str) or not database_id.strip():
            raise MembershipSnapshotError(f"{database} reference at {location} has no exact id")
        if database_id != database_id.strip():
            raise MembershipSnapshotError(f"{database} reference at {location} has an untrimmed id")
        if database == "GO" and _go_evidence_code(raw) == "ND":
            return  # "no biological data available" is the absence of a fact
        normalized_xref = _normalise_cross_reference(raw)
        row: dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "protein_id": protein_id,
            "source_trait_id": f"{namespace}:{_trait_local_id(database, database_id)}",
            "database": database,
            "database_id": database_id,
            "uniprot_release": uniprot_release,
            "sequence_sha256": sequence_sha256,
            "api_endpoint": UNIPROT_SEARCH,
            "database_cross_reference": normalized_xref,
        }
        if _swissprot_conditional(row) and entry_type in ENTRY_TYPES:
            # Without a recognized entryType the fact stays captured but cannot qualify.
            row["uniprot_entry_type"] = entry_type
            if database == "GO":
                # The EC assignment an EC-derived GO term rests on, for replay (#1048).
                if not ec_evidence:
                    ec_evidence.append(_entry_ec_evidence(entry))
                row["uniprot_ec_evidence"] = ec_evidence[0]
        row["membership_id"] = compute_membership_id(row)
        errors = _validate_membership(row)
        if errors:
            raise MembershipSnapshotError("; ".join(errors))
        key = (protein_id, row["source_trait_id"], uniprot_release, sequence_sha256)
        previous = by_key.get(key)
        if previous is not None and previous != row:
            raise MembershipSnapshotError(
                "ambiguous UniProt membership: multiple distinct cross-references for "
                f"{protein_id} / {row['source_trait_id']}"
            )
        by_key[key] = row

    for index, raw in enumerate(raw_cross_references):
        if not isinstance(raw, dict):
            raise MembershipSnapshotError(f"uniProtKBCrossReferences[{index}] is not an object")
        if raw.get("database") == RHEA_DATABASE:
            continue  # Rhea is admitted only from a catalytic-activity reaction below
        add(raw, f"uniProtKBCrossReferences[{index}]")

    comments = entry.get("comments") or []
    if not isinstance(comments, list):
        raise MembershipSnapshotError("comments is not a list")
    for comment_index, comment in enumerate(comments):
        if not isinstance(comment, dict) or comment.get("commentType") != "CATALYTIC ACTIVITY":
            continue
        if comment.get("molecule"):
            # "[Isoform 2]:" or a chain: not a fact about the whole canonical protein (#975).
            continue
        reaction = comment.get("reaction")
        if not isinstance(reaction, dict):
            raise MembershipSnapshotError(f"comments[{comment_index}] reaction is not an object")
        references = reaction.get("reactionCrossReferences") or []
        if not isinstance(references, list):
            raise MembershipSnapshotError(
                f"comments[{comment_index}] reactionCrossReferences is not a list"
            )
        for reference_index, raw in enumerate(references):
            if not isinstance(raw, dict):
                raise MembershipSnapshotError(
                    f"comments[{comment_index}] reaction reference {reference_index} "
                    "is not an object"
                )
            if raw.get("database") != RHEA_DATABASE:
                continue
            raw_id = raw.get("id")
            if isinstance(raw_id, str) and raw_id.startswith(RHEA_COMPOUND_PREFIX):
                # A Rhea generic/polymer compound is a reaction *participant*, which
                # UniProt lists under the Rhea database too; it is never a reaction.
                continue
            evidences = reaction.get("evidences") or []
            if not isinstance(evidences, list):
                raise MembershipSnapshotError(f"comments[{comment_index}] evidences is not a list")
            # The reaction's own evidence travels with the fact so its strength is
            # replayable (#974); everything else in the comment stays out.
            add(
                {**raw, "evidences": evidences},
                f"comments[{comment_index}].reactionCrossReferences[{reference_index}]",
            )
    return sorted(by_key.values(), key=lambda row: (row["source_trait_id"], row["membership_id"]))


def merge_memberships(*collections: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Validate, deduplicate, and deterministically sort membership rows."""

    by_id: dict[str, dict[str, Any]] = {}
    by_key: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    for collection in collections:
        for raw in collection:
            row = dict(raw)
            errors = _validate_membership(row)
            if errors:
                raise MembershipSnapshotError("; ".join(errors))
            membership_id = row["membership_id"]
            if membership_id in by_id and by_id[membership_id] != row:
                raise MembershipSnapshotError(f"membership ID collision for {membership_id}")
            key = (
                row["protein_id"],
                row["source_trait_id"],
                row["uniprot_release"],
                row["sequence_sha256"],
            )
            if key in by_key and by_key[key] != row:
                raise MembershipSnapshotError(
                    "ambiguous membership snapshot for "
                    f"{row['protein_id']} / {row['source_trait_id']}"
                )
            by_id[membership_id] = row
            by_key[key] = row
    return sorted(
        by_id.values(),
        key=lambda row: (
            row["protein_id"],
            row["source_trait_id"],
            row["uniprot_release"],
            row["sequence_sha256"],
            row["membership_id"],
        ),
    )


def dump_memberships(rows: Iterable[Mapping[str, Any]]) -> str:
    """Serialize a strict, deterministic one-fact-per-line snapshot."""

    normalized = merge_memberships(rows)
    return "".join(canonical_json(row) + "\n" for row in normalized)


def load_memberships(path: Path) -> list[dict[str, Any]]:
    """Load a snapshot fail-closed, including content and ambiguity checks."""

    if not path.is_file():
        raise MembershipSnapshotError(f"membership snapshot does not exist: {path}")
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise MembershipSnapshotError(
                    f"{path}:{line_number}: invalid JSON: {exc.msg}"
                ) from exc
            if not isinstance(value, dict):
                raise MembershipSnapshotError(f"{path}:{line_number}: row is not an object")
            errors = _validate_membership(value)
            if errors:
                raise MembershipSnapshotError(f"{path}:{line_number}: " + "; ".join(errors))
            rows.append(value)
    return merge_memberships(rows)


def find_exact_membership(
    rows: Iterable[Mapping[str, Any]],
    *,
    protein_id: str,
    source_trait_id: str,
    uniprot_release: str,
    sequence_sha256: str,
) -> dict[str, Any] | None:
    """Return one exact positive fact; missing or ambiguous evidence never qualifies."""

    matches = [
        dict(row)
        for row in rows
        if row.get("protein_id") == protein_id
        and row.get("source_trait_id") == source_trait_id
        and row.get("uniprot_release") == uniprot_release
        and row.get("sequence_sha256") == sequence_sha256
    ]
    if not matches:
        return None
    normalized = merge_memberships(matches)
    if len(normalized) != 1:
        raise MembershipSnapshotError(
            f"ambiguous exact membership for {protein_id} / {source_trait_id}"
        )
    return normalized[0]
