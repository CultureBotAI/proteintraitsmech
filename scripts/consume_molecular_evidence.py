#!/usr/bin/env python3
"""Resolve a pinned explanation for a gene review; never assign an annotation.

The request is a consumer-side reference, not a PTM record or occurrence. Exact
keys, export bytes, version, protein and sequence identity must all agree.
"""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import sys

import yaml

from validate_molecular_evidence import validate_bundle

REQUEST_KEYS = {"bundle_id", "bundle_version", "bundle_sha256", "protein_id", "sequence_sha256",
                "assertion_id", "usage", "fixture"}
UPSTREAM_KEYS = {"repository", "commit", "path", "sha256", "annotation_index", "term_id",
                 "expected_action", "site_ref", "expected_claim_count"}


def verify_upstream(raw, spec, bundle, basis, protein_id):
    """Check only the pinned residue claims; do not validate/adopt a GO decision."""
    if not isinstance(spec, dict) or set(spec) != UPSTREAM_KEYS:
        raise ValueError("upstream review pin has unknown or missing fields")
    if (not all(isinstance(spec[k], str) and spec[k] for k in UPSTREAM_KEYS - {"annotation_index", "expected_claim_count"}) or
            not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", spec["repository"]) or
            not re.fullmatch(r"[0-9a-f]{40}", spec["commit"]) or
            not re.fullmatch(r"[0-9a-f]{64}", spec["sha256"]) or
            spec["path"].startswith("/") or ".." in spec["path"].split("/") or
            type(spec["annotation_index"]) is not int or spec["annotation_index"] < 0 or
            type(spec["expected_claim_count"]) is not int or spec["expected_claim_count"] < 1):
        raise ValueError("invalid upstream review pin")
    if raw is None or len(raw) > 4_000_000 or hashlib.sha256(raw).hexdigest() != spec["sha256"]:
        raise ValueError("upstream review bytes are missing or checksum mismatched")
    try:
        review = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        raise ValueError("invalid upstream review YAML") from exc
    if not isinstance(review, dict) or review.get("id") != protein_id.removeprefix("UniProtKB:"):
        raise ValueError("upstream review protein mismatch")
    annotations = review.get("existing_annotations")
    if not isinstance(annotations, list) or spec["annotation_index"] >= len(annotations):
        raise ValueError("upstream annotation does not resolve")
    annotation = annotations[spec["annotation_index"]]
    if (not isinstance(annotation, dict) or not isinstance(annotation.get("term"), dict) or
            annotation["term"].get("id") != spec["term_id"] or not isinstance(annotation.get("review"), dict) or
            annotation["review"].get("action") != spec["expected_action"]):
        raise ValueError("upstream annotation identity/action changed")
    propagation = annotation["review"].get("propagation_review", {})
    claims = propagation.get("residue_claims") if isinstance(propagation, dict) else None
    if not isinstance(claims, list) or len(claims) != spec["expected_claim_count"]:
        raise ValueError("upstream residue claim count changed")
    proteins = {p["protein_id"]: p for p in bundle["protein_references"]}
    sites = {s["assertion_id"]: s for s in bundle["sites"]}
    comparisons = [a for a in basis if a["evidence_origin"] == "COMPUTED_COMPARISON" and "site_ref" in a]
    checked, seen = [], set()
    for i, claim in enumerate(claims):
        if (not isinstance(claim, dict) or claim.get("claim_type") != "RETAINED" or
                claim.get("site_ref") != spec["site_ref"] or not isinstance(claim.get("anchor"), dict) or
                not isinstance(claim.get("target"), dict)):
            raise ValueError("only explicitly retained claims at the pinned site are supported")
        anchor, target = claim["anchor"], claim["target"]
        for residue in (anchor, target):
            protein = proteins.get(residue.get("accession"))
            position = residue.get("position")
            if (not protein or type(position) is not int or not 1 <= position <= protein["sequence_length"] or
                    protein["sequence"][position - 1] != residue.get("residue") or
                    ("sequence_version" in residue and residue["sequence_version"] != protein["sequence_version"])):
                raise ValueError("upstream residue does not match the pinned PTM sequence")
        key = (anchor["accession"], anchor["position"], target["accession"], target["position"])
        if key in seen or target["accession"] != protein_id:
            raise ValueError("duplicate or wrong-protein upstream residue claim")
        seen.add(key)
        matches = sorted(c["assertion_id"] for c in comparisons
                         if c["protein_id"] == target["accession"] and sites[c["site_ref"]]["protein_id"] == anchor["accession"]
                         and any(r["status"] == "IDENTICAL" and r["anchor_position"] == anchor["position"]
                                 and r["anchor_residue"] == anchor["residue"] and r.get("target_position") == target["position"]
                                 and r.get("target_residue") == target["residue"] for r in c["residues"]))
        if not matches:
            raise ValueError("upstream retained claim lacks matching PTM comparison evidence")
        checked.append({"source_pointer": f"/existing_annotations/{spec['annotation_index']}/review/propagation_review/residue_claims/{i}",
                        "anchor": deepcopy(anchor), "target": deepcopy(target), "comparison_assertions": matches})
    return {"source": deepcopy(spec), "status": "MATCHED_RETAINED_IDENTITIES", "checked_claims": checked,
            "limitations": "Read-only agreement on residue identities and correspondence, not experimental target binding, "
                           "site necessity, activity, or endorsement of the upstream GO action or method label."}


def resolve(raw, request, upstream_raw=None):
    if not isinstance(request, dict) or set(request) not in (REQUEST_KEYS, REQUEST_KEYS | {"upstream_review"}):
        raise ValueError("consumer request has unknown or missing fields")
    if not all(isinstance(request[k], str) and request[k] for k in REQUEST_KEYS):
        raise ValueError("consumer reference fields must be nonempty strings")
    if upstream_raw is not None and "upstream_review" not in request:
        raise ValueError("upstream review bytes require an explicit source pin")
    if request["usage"] != "MECHANISTIC_CONTEXT_ONLY":
        raise ValueError("this consumer cannot authorize annotations")
    if hashlib.sha256(raw).hexdigest() != request["bundle_sha256"]:
        raise ValueError("consumer export checksum mismatch")
    bundle = json.loads(raw)
    errors = validate_bundle(bundle)
    if errors:
        raise ValueError("invalid molecular bundle: " + "; ".join(errors))
    if bundle["bundle_id"] != request["bundle_id"] or bundle["version"] != request["bundle_version"]:
        raise ValueError("consumer bundle identity/version mismatch")
    assertions = {row["assertion_id"]: row for key in (
        "sites", "comparisons", "model_comparisons", "functional_observations", "explanations")
        for row in bundle.get(key, [])}
    claim = assertions.get(request["assertion_id"])
    if not claim or claim["protein_id"] != request["protein_id"] or claim["sequence_sha256"] != request["sequence_sha256"]:
        raise ValueError("consumer claim/protein/sequence mismatch")
    basis = set(claim.get("supporting_assertions", [])) | set(claim.get("challenging_assertions", []))
    result = {"request": deepcopy(request), "annotation_action": "NONE",
              "scope_note": bundle["scope_note"], "claim": deepcopy(claim),
              "basis": [deepcopy(assertions[key]) for key in sorted(basis)],
              "context": [deepcopy(assertions[key]) for key in sorted(set(claim.get("context_assertions", [])))],
              "sources": deepcopy(bundle["sources"])}
    if "upstream_review" in request:
        result["upstream_review"] = verify_upstream(upstream_raw, request["upstream_review"], bundle,
                                                   result["basis"], request["protein_id"])
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--upstream-review", help="Read-only upstream YAML path, or - for stdin; requires a pin in the request")
    args = parser.parse_args(argv)
    try:
        upstream = None
        if args.upstream_review == "-":
            upstream = sys.stdin.buffer.read(4_000_001)
        elif args.upstream_review:
            with Path(args.upstream_review).open("rb") as stream:
                upstream = stream.read(4_000_001)
        result = resolve(args.bundle.read_bytes(), json.loads(args.request.read_text()), upstream)
        print(json.dumps(result, indent=2, sort_keys=True))
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
