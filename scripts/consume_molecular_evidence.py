#!/usr/bin/env python3
"""Resolve a pinned assertion or residue-bound mechanism; never assign an annotation.

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
RESIDUE_REQUEST_KEYS = (REQUEST_KEYS - {"assertion_id"}) | {"residue_query"}
UPSTREAM_KEYS = {"repository", "commit", "path", "sha256", "annotation_index", "term_id",
                 "expected_action", "site_ref", "expected_claim_count"}
RESIDUE_QUERY_LIMITS = (
    "Retrieval of explicitly curated mechanism residue bindings, not prediction or an exhaustive "
    "search of assays, contacts or sequence comparisons. Omitting substituted_residue selects only "
    "unsubstituted bindings; it is not a variant wildcard or a verified wild-type construct. "
    "A residue-set match does not establish an individual residue's necessity or sufficiency. "
    "Graphs retain their full protein, residue-set and assay scope; their edges are not automatically "
    "composed into new causal claims. No match means no matching curated mechanism in this bundle, "
    "not absence of a biological effect."
)


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


def argument_closure(assertions, roots):
    """Resolve evidence dependencies without converting edge polarity into a verdict."""
    # Preserve the complete argument DAG, not just its first layer. Edge polarity
    # belongs to each explanation: do not flatten a challenge of a supported
    # subclaim into direct support for (or against) the requested claim.
    basis, context, visited = set(), set(), set()
    argument_edges, context_edges = [], []
    pending = list(roots)
    while pending:
        key = pending.pop()
        if key in visited:
            continue
        visited.add(key)
        assertion = assertions[key]
        for field, relation in (("supporting_assertions", "SUPPORTS"),
                                ("challenging_assertions", "CHALLENGES")):
            for ref in sorted(set(assertion.get(field, []))):
                basis.add(ref)
                argument_edges.append({"explanation_id": key, "relation": relation, "assertion_id": ref})
                pending.append(ref)
        for ref in sorted(set(assertion.get("context_assertions", []))):
            context.add(ref)
            context_edges.append({"explanation_id": key, "assertion_id": ref})
    return {"basis": [deepcopy(assertions[key]) for key in sorted(basis)],
            "argument_edges": sorted(argument_edges, key=lambda e: (e["explanation_id"], e["relation"], e["assertion_id"])),
            "context": [deepcopy(assertions[key]) for key in sorted(context)],
            "context_edges": sorted(context_edges, key=lambda e: (e["explanation_id"], e["assertion_id"]))}


def mechanism_evidence(mechanism, assertions):
    """Return the entire curated graph and its argument/context closure, unpromoted."""
    closure = argument_closure(assertions, mechanism["assertion_refs"])
    refs = set(mechanism["assertion_refs"])
    refs.update(a["assertion_id"] for field in ("basis", "context") for a in closure[field])
    return {**deepcopy(mechanism),
            "assertions": [deepcopy(assertions[key]) for key in sorted(refs)],
            "argument_edges": closure["argument_edges"], "context_edges": closure["context_edges"]}


def validate_residue_query(query, protein):
    if (not isinstance(query, dict) or set(query) not in (
            {"position", "residue"}, {"position", "residue", "substituted_residue"})):
        raise ValueError("residue query has unknown or missing fields")
    if (type(query["position"]) is not int or
            not 1 <= query["position"] <= protein["sequence_length"] or
            query["residue"] != protein["sequence"][query["position"] - 1]):
        raise ValueError("query residue does not match the pinned reference sequence")
    if "substituted_residue" in query:
        alternate = query["substituted_residue"]
        if (not isinstance(alternate, str) or not re.fullmatch(r"[ACDEFGHIKLMNPQRSTVWYUOBZJX]", alternate)
                or alternate == query["residue"]):
            raise ValueError("query substitution must be a different single residue")


def matching_bindings(mechanism, request):
    query = request["residue_query"]
    matches = []
    for binding in mechanism.get("residue_bindings", []):
        if (binding["protein_id"] != request["protein_id"] or
                binding["sequence_sha256"] != request["sequence_sha256"] or
                any(binding.get(key) != query.get(key)
                    for key in ("position", "residue", "substituted_residue"))):
            continue
        # The complete node can span proteins with independent numbering frames.
        # A single-substitution query must not select a partial compound mutant;
        # unmodified partner residues do not add a second substitution.
        if "substituted_residue" in query and sum(
                other["node_id"] == binding["node_id"] and
                "substituted_residue" in other
                for other in mechanism["residue_bindings"]) != 1:
            continue
        matches.append(deepcopy(binding))
    return matches


def resolve(raw, request, upstream_raw=None):
    if not isinstance(request, dict) or set(request) not in (
            REQUEST_KEYS, REQUEST_KEYS | {"upstream_review"}, RESIDUE_REQUEST_KEYS):
        raise ValueError("consumer request has unknown or missing fields")
    if not all(isinstance(request[k], str) and request[k] for k in set(request) - {"upstream_review", "residue_query"}):
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
    result = {"request": deepcopy(request), "annotation_action": "NONE",
              "scope_note": bundle["scope_note"], "sources": deepcopy(bundle["sources"])}
    mechanisms = sorted(bundle.get("mechanisms", []), key=lambda m: m["mechanism_id"])
    if "residue_query" in request:
        protein = next((p for p in bundle["protein_references"] if p["protein_id"] == request["protein_id"]), None)
        if not protein or protein["sequence_sha256"] != request["sequence_sha256"]:
            raise ValueError("consumer protein/sequence mismatch")
        validate_residue_query(request["residue_query"], protein)
        result["mechanisms"] = []
        for mechanism in mechanisms:
            matches = matching_bindings(mechanism, request)
            if matches:
                result["mechanisms"].append({**mechanism_evidence(mechanism, assertions),
                                             "matched_residue_bindings": matches})
        result["retrieval_status"] = "MATCHED_CURATED_MECHANISMS" if result["mechanisms"] else "NO_CURATED_MECHANISM"
        result["retrieval_limitations"] = RESIDUE_QUERY_LIMITS
        return result

    claim = assertions.get(request["assertion_id"])
    if not claim or claim["protein_id"] != request["protein_id"] or claim["sequence_sha256"] != request["sequence_sha256"]:
        raise ValueError("consumer claim/protein/sequence mismatch")
    result.update(claim=deepcopy(claim), **argument_closure(assertions, [claim["assertion_id"]]))
    # Only an explicit direct link selects a graph. Shared citations, supporting
    # assertions, sequence correspondence or a trait class do not transfer it.
    result["mechanisms"] = [mechanism_evidence(m, assertions) for m in mechanisms
                            if claim["assertion_id"] in m["assertion_refs"] and
                            request["protein_id"] in m["protein_ids"]]
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
