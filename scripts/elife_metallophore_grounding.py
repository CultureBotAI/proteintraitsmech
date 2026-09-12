"""Narrow, receipt-backed source-membership grounding for eLife 109154.

Only exact, whole-protein seed memberships or source BGC annotations qualify.
Cropped domains without verified coordinates remain candidates.
The registered grounding promoter owns the final transaction and record writer.
"""

from __future__ import annotations

import argparse
import copy
import json
import re
from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path

import yaml

from elife_metallophores import (
    ARCHIVE_MD5, ARCHIVE_SHA256, ARCHIVE_URL, ASSERTIONS_PATH, DOMAIN_MODELS,
    EXCLUDED_REFERENCE_BGCS,
    POSITIVE_CUTOFFS, PREFIX, RAW, RELEASE, ROOT, SOURCE, catalog, digest, read_jsonl, sha256,
    source_accession, source_facts, trait_path, verified_archive, write_jsonl,
)

UNIPROT_RELEASE = "2026_03"
RECEIPT_PATH = "data/grounding/elife109154_acquisition_receipt.json"
STAGING = ROOT / "reports/uniprot-grounding/elife109154"
_STAGED: ContextVar[dict | None] = ContextVar("elife109154_staged", default=None)


def jsonl_text(rows: list[dict]) -> str:
    return "".join(json.dumps(r, sort_keys=True, ensure_ascii=True) + "\n" for r in rows)


@contextmanager
def assertion_context(rows: list[dict]):
    token = _STAGED.set({r["assertion_digest"]: r for r in rows})
    try:
        yield
    finally:
        _STAGED.reset(token)


def load_assertions() -> dict:
    staged = _STAGED.get()
    if staged is not None:
        return staged
    raw = (ROOT / ASSERTIONS_PATH).read_bytes()
    receipt = json.loads((ROOT / RECEIPT_PATH).read_text())
    if (receipt.get("source_assertions_sha256") != sha256(raw)
            or receipt.get("archive_sha256") != ARCHIVE_SHA256
            or receipt.get("archive_md5") != ARCHIVE_MD5
            or receipt.get("archive_url") != ARCHIVE_URL
            or receipt.get("uniprot_release") != UNIPROT_RELEASE):
        raise ValueError("invalid eLife source/acquisition receipt")
    rows = [json.loads(line) for line in raw.decode().splitlines()]
    result = {r["assertion_digest"]: r for r in rows}
    if len(result) != len(rows):
        raise ValueError("duplicate source assertion")
    for row in rows:
        response_key = row["protein_reference"]["protein_id"]
        if receipt["uniprot_response_sha256"].get(response_key) != row["uniprot_response_sha256"]:
            raise ValueError("UniProt response is absent from the acquisition receipt")
    return result


def validate_assertion(row: dict) -> None:
    allowed = {"schema_version", "source_fact", "protein_reference", "uniprot_request_url",
               "uniprot_response_sha256", "trait_definition_sha256", "source_cross_reference",
               "assertion_digest"}
    if set(row) - allowed or row.get("schema_version") != 1:
        raise ValueError("invalid assertion schema")
    payload = {k: v for k, v in row.items() if k != "assertion_digest"}
    if row.get("assertion_digest") != digest(payload):
        raise ValueError("source assertion digest mismatch")
    fact = row["source_fact"]
    if fact.get("candidate_id") != "elife109154:" + digest(
            {k: v for k, v in fact.items() if k != "candidate_id"}):
        raise ValueError("source member digest mismatch")
    model = fact["model"]
    if model not in catalog()["traits"] or model in DOMAIN_MODELS:
        raise ValueError("no whole-protein membership contract for this model")
    if (fact["trait_id"] != PREFIX + model or fact["archive_sha256"] != ARCHIVE_SHA256
            or fact["archive_url"] != ARCHIVE_URL or fact["source_release"] != RELEASE):
        raise ValueError("source release or trait identity mismatch")
    if fact.get("source_kind") == "bgc_annotation":
        if any(bgc in fact["alignment_path"] for bgc in EXCLUDED_REFERENCE_BGCS):
            raise ValueError("source BGC is explicitly marked as a false positive")
        annotation = fact.get("native_annotation", "")
        hit = re.match(r"(\S+) \(E-value: [^,]+, bitscore: ([0-9.]+),", annotation)
        if (not hit or hit[1] != model or float(hit[2]) != fact.get("source_bitscore")
                or float(hit[2]) < POSITIVE_CUTOFFS[model]
                or not fact["alignment_path"].startswith(
                    "nrp-metallophore-SI-main/5_refseq_bigscape/reference_BGCs.tar.gz!reference_BGCs/")):
            raise ValueError("invalid source-reported BGC profile annotation")
    elif fact.get("source_kind") != "seed_alignment":
        raise ValueError("unsupported source assertion kind")
    reference = row["protein_reference"]
    if reference["uniprot_release"] != UNIPROT_RELEASE:
        raise ValueError("UniProt release mismatch")
    sequence = fact.get("full_sequence", fact["source_sequence"])
    if sequence != reference["sequence"] or sha256(sequence.encode()) != reference["sequence_sha256"]:
        raise ValueError("source full sequence differs from UniProt")
    namespace, source_id = source_accession(fact["source_header"]) or (None, None)
    if (namespace, source_id) != (fact["source_namespace"], fact["source_accession"]):
        raise ValueError("source identifier was not derived from the source header")
    accession = reference["protein_id"].removeprefix("UniProtKB:")
    if row["uniprot_request_url"] != f"https://rest.uniprot.org/uniprotkb/{accession}.json":
        raise ValueError("protein was not fetched by exact accession")
    if namespace == "UniProtKB":
        if accession != source_id:
            raise ValueError("source UniProt accession mismatch")
    else:
        xref = row.get("source_cross_reference", {})
        values = [xref.get("id")] + [v.get("value") for v in xref.get("properties", [])]
        if xref.get("database") != namespace or source_id not in values:
            raise ValueError("no exact source accession in the UniProt response")


def contract_errors(evidence: dict) -> list[tuple[str, str]]:
    try:
        row = load_assertions()[evidence["provider_entry_sha256"]]
        validate_assertion(row)
        fact = row["source_fact"]
        reference = row["protein_reference"]
        expected = {"trait_id": fact["trait_id"], "source_trait_id": fact["trait_id"],
                    "protein_id": reference["protein_id"], "mapping_method":
                    ("SOURCE_MEMBERSHIP" if fact["source_kind"] == "seed_alignment" else "SOURCE_ANNOTATION"),
                    "scope": "WHOLE_PROTEIN", "evidence_source": SOURCE,
                    "source_release": RELEASE, "provider_kind": "SOURCE_DATABASE",
                    "provider_source": ASSERTIONS_PATH, "provider_release": RELEASE,
                    "sequence_sha256": reference["sequence_sha256"]}
        if any(evidence.get(k) != v for k, v in expected.items()):
            raise ValueError("evidence differs from the exact source membership")
        if any(k in evidence for k in ("intervals", "residue_positions", "coordinate_frame",
                                      "inheritance_path", "expected_residues")):
            raise ValueError("whole-protein membership must not carry coordinates or inheritance")
    except (KeyError, TypeError, ValueError, OSError) as error:
        return [("elife_metallophore_source_contract", str(error))]
    return []


def record_errors(record: dict, reference: dict, evidence: dict) -> list[tuple[str, str]]:
    try:
        row = load_assertions()[evidence["provider_entry_sha256"]]
        if reference != row["protein_reference"]:
            raise ValueError("registry differs from the acquired UniProt reference")
        if record.get("trait_axis") != "SEQUENCE" or record.get("trait_category") != "SEQ_FAMILY":
            raise ValueError("source membership applies only to a whole-protein sequence family")
        if sha256(record.get("definition", "").encode()) != row["trait_definition_sha256"]:
            raise ValueError("trait definition changed after source-membership review")
    except (KeyError, TypeError, ValueError, OSError) as error:
        return [("elife_metallophore_record_binding", str(error))]
    return []


def resolve_response(fact: dict, response: dict, record: dict) -> dict:
    from fetch_uniprot_registry import Target, _entry_reference
    from validate_uniprot_grounding import build_grounding_evidence

    body = response["body"]
    if response["body_sha256"] != sha256(body.encode()):
        raise ValueError("acquired response checksum mismatch")
    if response["headers"].get("x-uniprot-release") != UNIPROT_RELEASE:
        raise ValueError("acquired response release mismatch")
    entry = json.loads(body)
    accession = entry["primaryAccession"]
    sequence = fact.get("full_sequence", fact["source_sequence"])
    target = Target("UniProtKB:" + accession, accession, (), len(sequence),
                    sha256(sequence.encode()), UNIPROT_RELEASE)
    reference, errors = _entry_reference(entry, target, UNIPROT_RELEASE)
    if errors:
        raise ValueError("; ".join(errors))
    assertion = {"schema_version": 1, "source_fact": fact, "protein_reference": reference,
                 "uniprot_request_url": response["request_url"],
                 "uniprot_response_sha256": response["body_sha256"],
                 "trait_definition_sha256": sha256(record["definition"].encode())}
    if fact["source_namespace"] != "UniProtKB":
        for xref in entry.get("uniProtKBCrossReferences", []):
            values = [xref.get("id")] + [v.get("value") for v in xref.get("properties", [])]
            if xref.get("database") == fact["source_namespace"] and fact["source_accession"] in values:
                assertion["source_cross_reference"] = xref
                break
    assertion["assertion_digest"] = digest(assertion)
    validate_assertion(assertion)
    occurrence = {"trait_id": fact["trait_id"], "protein_id": reference["protein_id"],
                  "source_trait_id": fact["trait_id"], "mapping_method":
                  ("SOURCE_MEMBERSHIP" if fact["source_kind"] == "seed_alignment" else "SOURCE_ANNOTATION"),
                  "scope": "WHOLE_PROTEIN", "evidence_source": SOURCE,
                  "source_release": RELEASE, "sequence_sha256": reference["sequence_sha256"],
                  "qualification_status": "QUALIFIED"}
    evidence = build_grounding_evidence(
        occurrence, provider_kind="SOURCE_DATABASE", provider_source=ASSERTIONS_PATH,
        provider_release=RELEASE, provider_entry_sha256=assertion["assertion_digest"])
    occurrence["source_evidence_id"] = evidence["evidence_id"]
    example = {k: v for k, v in reference.items() if k != "sequence"}
    description = ("membership in the deposited seed alignment" if fact["source_kind"] == "seed_alignment"
                   else "profile annotation in a deposited reference BGC")
    example.update(source="UNIPROT_GROUNDING", qualification_status="QUALIFIED",
                   reference="DOI:10.5281/zenodo.18866949", trait_occurrences=[occurrence],
                   note=f"Source {description}; full sequence verified against UniProt. "
                   "QUALIFIED describes sequence classification, not experimentally proven activity.")
    result = {"candidate_id": fact["candidate_id"], "model": fact["model"],
              "record_path": str(trait_path(fact["model"]).relative_to(ROOT)),
              "record_sha256": digest({k: v for k, v in record.items()
                                       if k not in {"canonical_examples", "curation_history"}}),
              "assertion": assertion, "reference": reference, "evidence": evidence,
              "example": example}
    result["resolution_digest"] = digest(result)
    return result


def resolve_current() -> tuple[list[dict], list[dict]]:
    with verified_archive() as archive:
        _, members = source_facts(archive)
    facts = {r["candidate_id"]: r for r in members}
    resolved, rejected = [], []
    for acquired in read_jsonl(RAW / "acquired_examples.jsonl"):
        fact = facts[acquired["candidate_id"]]
        record = yaml.safe_load(trait_path(fact["model"]).read_text())
        if not acquired["responses"]:
            rejected.append({"candidate_id": fact["candidate_id"], "model": fact["model"],
                             "reason": acquired.get("issue", "no exact response")})
        for response in acquired["responses"]:
            try:
                resolved.append(resolve_response(fact, response, record))
            except ValueError as error:
                rejected.append({"candidate_id": fact["candidate_id"], "model": fact["model"],
                                 "reason": str(error)})
    return resolved, rejected


def resolve(args: argparse.Namespace) -> int:
    resolved, rejected = resolve_current()
    if args.apply:
        write_jsonl(STAGING / "resolved.jsonl", resolved)
        write_jsonl(STAGING / "rejected.jsonl", rejected)
        review = [{"resolution_digest": r["resolution_digest"], "model": r["model"],
                   "protein_id": r["reference"]["protein_id"],
                   "taxon": r["reference"]["taxon_label"], "decision": "PENDING", "reason": ""}
                  for r in resolved]
        write_jsonl(STAGING / "review.jsonl", review)
    print(json.dumps({"resolved": len(resolved), "rejected": len(rejected), "applied": args.apply}))
    return 0


def promote(args: argparse.Namespace) -> int:
    from ground_uniprot_examples import (
        _install_promotion_transaction, _replace_examples_block, _strict_errors_for_text,
        _registry_text,
    )
    from validate_uniprot_grounding import load_evidence_registry, load_registry, validate_record

    resolved, _ = resolve_current()  # Replays pinned source bytes and exact API responses.
    current = {r["resolution_digest"]: r for r in resolved}
    decisions = read_jsonl(args.decisions)
    if len({r["resolution_digest"] for r in decisions}) != len(decisions):
        raise ValueError("duplicate review decision")
    selected = []
    for decision in decisions:
        if decision["resolution_digest"] not in current:
            raise ValueError("review no longer matches the source, response, or trait bytes")
        reviewed = current[decision["resolution_digest"]]
        if any(decision.get(key) != expected for key, expected in (
                ("model", reviewed["model"]),
                ("protein_id", reviewed["reference"]["protein_id"]),
                ("taxon", reviewed["reference"]["taxon_label"]))):
            raise ValueError("displayed review identity differs from the resolved candidate")
        if decision.get("decision") not in {"APPROVE", "REJECT"} or not decision.get("reason"):
            raise ValueError("every reviewed row needs a decision and rationale")
        if decision["decision"] == "APPROVE":
            selected.append(current[decision["resolution_digest"]])
    if not selected:
        raise ValueError("no approved examples")
    registry_path = ROOT / "data/grounding/protein_registry.jsonl"
    evidence_path = ROOT / "data/grounding/occurrence_evidence.jsonl"
    registry, errors = load_registry(registry_path)
    evidence_registry, evidence_errors = load_evidence_registry(evidence_path)
    if errors or evidence_errors:
        raise ValueError("durable registry validation failed before promotion")
    existing_assertions = read_jsonl(ROOT / ASSERTIONS_PATH) if (ROOT / ASSERTIONS_PATH).exists() else []
    assertions = {r["assertion_digest"]: r for r in existing_assertions}
    updates = {}
    for row in selected:
        pid = row["reference"]["protein_id"]
        if pid in registry and registry[pid] != row["reference"]:
            raise ValueError(f"existing protein registry conflict: {pid}")
        registry[pid] = row["reference"]
        evidence_registry[row["evidence"]["evidence_id"]] = row["evidence"]
        assertions[row["assertion"]["assertion_digest"]] = row["assertion"]
        path = trait_path(row["model"])
        text = updates.get(path, path.read_text())
        record = yaml.safe_load(text)
        examples = record.setdefault("canonical_examples", [])
        previous = next((e for e in examples if e.get("protein_id") == pid), None)
        if previous is not None and previous != row["example"]:
            raise ValueError(f"existing canonical example differs from reviewed example: {pid}")
        if previous is None:
            examples.append(copy.deepcopy(row["example"]))
        updates[path] = _replace_examples_block(text, record)
    assertion_rows = sorted(assertions.values(), key=lambda r: r["assertion_digest"])
    with assertion_context(assertion_rows):
        for path, text in updates.items():
            if _strict_errors_for_text(text):
                raise ValueError(f"closed-schema validation failed: {path}")
            findings = validate_record(yaml.safe_load(text), registry,
                                       evidence_registry=evidence_registry, require_qualified=True)
            if findings:
                raise ValueError(f"semantic validation failed: {path}: {findings}")
    assertion_text = jsonl_text(assertion_rows)
    receipt = {"schema_version": 1, "archive_url": ARCHIVE_URL, "archive_sha256": ARCHIVE_SHA256,
               "archive_md5": ARCHIVE_MD5, "uniprot_release": UNIPROT_RELEASE,
               "source_assertions_sha256": sha256(assertion_text.encode()),
               "uniprot_response_sha256": {r["protein_reference"]["protein_id"]:
                                            r["uniprot_response_sha256"] for r in assertion_rows},
               "review_decisions_sha256": sha256(args.decisions.read_bytes())}
    updates = {path: text for path, text in updates.items() if path.read_text() != text}
    artifacts = [
        (ROOT / ASSERTIONS_PATH, assertion_text),
        (ROOT / RECEIPT_PATH, json.dumps(receipt, sort_keys=True, indent=2) + "\n"),
        (registry_path, _registry_text(registry)),
        (evidence_path, _registry_text(evidence_registry)),
    ]
    artifacts = [(path, text) for path, text in artifacts
                 if not path.exists() or path.read_text() != text]
    if args.apply and (updates or artifacts):
        _install_promotion_transaction(artifacts, updates)
    print(json.dumps({"approved_examples": len(selected), "trait_records": len(updates),
                      "applied": args.apply}))
    return 0


def add_subcommands(subparsers) -> None:
    resolver = subparsers.add_parser("elife-resolve", help="resolve immutable eLife seed members")
    resolver.add_argument("--apply", action="store_true", help="write ignored review staging")
    resolver.set_defaults(func=resolve)
    promoter = subparsers.add_parser("elife-promote", help="promote reviewed eLife seed memberships")
    promoter.add_argument("--decisions", type=Path, required=True)
    promoter.add_argument("--apply", action="store_true")
    promoter.set_defaults(func=promote)
