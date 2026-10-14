#!/usr/bin/env python3
"""Closed-schema and cross-assertion checks for molecular evidence bundles."""
from __future__ import annotations

import argparse
from collections import Counter
from functools import lru_cache
from graphlib import CycleError, TopologicalSorter
import json
import math
from pathlib import Path
import re
import sys

import numpy as np
from linkml.validator import Validator
from linkml.validator.plugins import JsonschemaValidationPlugin
from linkml.validator.report import Severity

from audit_causal_graphs import audit_record, node_type_enum
from molecular_evidence import BACKBONE, distance, sha256
from build_ecod_sifts_candidates import AA3_TO_1
from slc10_model_comparison import coords
from residue_reasoning import ASSERTION_KINDS, validate_reasoning

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "src/proteintraitsmech/schema/proteintraitsmech.yaml"


@lru_cache(maxsize=1)
def validator():
    return Validator(schema=str(SCHEMA),
                     validation_plugins=[JsonschemaValidationPlugin(closed=True)])


def finite(value):
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, dict):
        return all(finite(v) for v in value.values())
    if isinstance(value, list):
        return all(finite(v) for v in value)
    return True


def null_errors(value, path=""):
    """Reject explicit nulls before schema validation, with JSON Pointer paths."""
    if value is None:
        yield f"{path or '<root>'}: explicit null is not permitted; omit optional fields"
    elif isinstance(value, dict):
        for key, child in value.items():
            token = str(key).replace("~", "~0").replace("/", "~1")
            yield from null_errors(child, f"{path}/{token}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from null_errors(child, f"{path}/{index}")


def source_binding_errors(sources, source_id, kind, identity_field, identity, label):
    source = sources.get(source_id)
    if source is None:
        return [f"{label}: source {source_id} does not resolve"]
    errors = []
    if source["artifact_kind"] != kind:
        errors.append(f"{label}: source {source_id} requires artifact_kind {kind}")
    if source.get(identity_field) != identity:
        errors.append(f"{label}: source {source_id} {identity_field} must match {identity}")
    return errors


def target_order_errors(rows, label):
    targets = [row["target_position"] for row in rows
               if row["status"] != "UNRESOLVED" and "target_position" in row]
    if any(second <= first for first, second in zip(targets, targets[1:])):
        return [f"{label}: resolved target positions must be unique and strictly increasing"]
    return []


def explanation_closure(assertion_refs, explanations):
    """Follow evidence dependencies, not explicit comparison anchor relationships.

    A comparison owns its target assertion; site_ref/anchor_protein_id describe
    its anchor separately. They do not relabel an anchor assay as target evidence.
    The visited set also makes malformed cyclic dependencies safe to inspect.
    """
    pending, reached = list(assertion_refs), set()
    while pending:
        ref = pending.pop()
        if ref in reached:
            continue
        reached.add(ref)
        if ref in explanations:
            for field in ("supporting_assertions", "challenging_assertions", "context_assertions"):
                pending.extend(explanations[ref].get(field, []))
    return reached


def validate_model_comparison(model, proteins, sources):
    errors = []
    if model["evidence_origin"] != "COMPUTED_COMPARISON":
        errors.append("predicted model comparison must remain COMPUTED_COMPARISON")
    for field, kind in (("anchor_structure_source", "EXPERIMENTAL_STRUCTURE"),
                        ("mapping_source", "RESIDUE_MAPPING")):
        errors.extend(source_binding_errors(sources, model[field], kind, "structure_id",
                                            model["anchor_structure_id"], f"{model['assertion_id']}.{field}"))
    errors.extend(source_binding_errors(sources, model["model_source"], "PREDICTED_STRUCTURE", "protein_id",
                                        model["protein_id"], f"{model['assertion_id']}.model_source"))
    anchor = proteins.get(model["anchor_protein_id"])
    target = proteins[model["protein_id"]]
    if not anchor:
        return [*errors, "model anchor protein does not resolve"]
    pairs = model["pairs"]
    errors.extend(target_order_errors(pairs, f"model comparison {model['assertion_id']}"))
    if [p["anchor_position"] for p in pairs] != list(range(1, anchor["sequence_length"] + 1)):
        errors.append("model pairs must cover every anchor position exactly once in order")
    selected = []
    for pair in pairs:
        a = pair["anchor_position"]
        if not 1 <= a <= anchor["sequence_length"] or anchor["sequence"][a - 1] != pair["anchor_residue"]:
            errors.append("model pair anchor residue mismatch")
        if pair["status"] == "UNRESOLVED":
            if any(k in pair for k in ("target_position", "target_residue", "target_ca", "target_plddt", "ca_displacement_angstrom")):
                errors.append("unresolved model pair cannot assign a target or geometry")
        else:
            t = pair.get("target_position", 0)
            aa = pair.get("target_residue")
            if not 1 <= t <= target["sequence_length"] or target["sequence"][t - 1] != aa:
                errors.append("model pair target residue mismatch")
            if (pair["status"] == "IDENTICAL") != (aa == pair["anchor_residue"]):
                errors.append("model pair identity status mismatch")
            if "target_ca" not in pair or "target_plddt" not in pair:
                errors.append("resolved model pair requires target coordinate and pLDDT")
            elif (pair["target_ca"]["auth_seq_id"] != str(t) or pair["target_ca"].get("label_seq_id") != t):
                errors.append("prediction CA numbering mismatch")
        for side in ("anchor", "target"):
            atom = pair.get(f"{side}_ca")
            if atom and (atom["atom_name"] != "CA" or atom["element"] != "C" or atom["occupancy"] <= 0 or
                         AA3_TO_1.get(atom["residue_name"]) != pair.get(f"{side}_residue")):
                errors.append("model pair CA identity mismatch")
        eligible = "anchor_ca" in pair and "target_ca" in pair and pair.get("target_plddt", -1) >= model["confidence_threshold"]
        if pair["used_in_fit"] != eligible:
            errors.append("model fit must select exactly all confidence-eligible sequence pairs")
        if eligible:
            selected.append(pair)
    if len(selected) != model["fit_residue_count"]:
        errors.append("model fit count mismatch")
    if len(selected) < model["minimum_fit_pairs"]:
        if model["fit_status"] != "INSUFFICIENT_PAIRS" or any(k in model for k in ("rotation", "translation", "fit_rmsd_angstrom")):
            errors.append("insufficient pairs cannot produce a transform")
        if any("ca_displacement_angstrom" in p for p in pairs):
            errors.append("no displacement without a fitted transform")
        return errors
    if (model["fit_status"] != "ALIGNED" or len(model.get("rotation", [])) != 9 or
            len(model.get("translation", [])) != 3 or "fit_rmsd_angstrom" not in model):
        return [*errors, "aligned model requires a complete transform and RMSD"]
    rotation = np.array(model["rotation"]).reshape(3, 3)
    translation = np.array(model["translation"])
    if not np.allclose(rotation.T @ rotation, np.eye(3), atol=1e-9, rtol=0) or not np.isclose(np.linalg.det(rotation), 1, atol=1e-9, rtol=0):
        errors.append("model rotation is not a proper rigid transform")
    residuals = []
    for pair in pairs:
        if "anchor_ca" not in pair or "target_ca" not in pair:
            if "ca_displacement_angstrom" in pair:
                errors.append("displacement requires both CA coordinates")
            continue
        residual = float(np.linalg.norm(np.array(coords(pair["target_ca"])) @ rotation + translation - coords(pair["anchor_ca"])))
        if not math.isclose(residual, pair.get("ca_displacement_angstrom", -1), abs_tol=1e-8):
            errors.append("model displacement disagrees with coordinates/transform")
        if pair["used_in_fit"]:
            residuals.append(residual)
    rmsd = math.sqrt(sum(r * r for r in residuals) / len(residuals)) if residuals else -1
    if not math.isclose(rmsd, model["fit_rmsd_angstrom"], abs_tol=1e-8):
        errors.append("model RMSD disagrees with selected pairs")
    # Internal consistency is insufficient: a self-consistent arbitrary transform
    # must not masquerade as the declared untrimmed least-squares superposition.
    reference = np.array([coords(p["anchor_ca"]) for p in selected])
    mobile = np.array([coords(p["target_ca"]) for p in selected])
    reference_centered = reference - reference.mean(axis=0)
    mobile_centered = mobile - mobile.mean(axis=0)
    if min(np.linalg.matrix_rank(reference_centered), np.linalg.matrix_rank(mobile_centered)) < 2:
        errors.append("degenerate coordinates cannot define a least-squares model fit")
    else:
        u, _, vt = np.linalg.svd(mobile_centered.T @ reference_centered)
        correction = np.diag([1., 1., np.linalg.det(u @ vt)])
        optimal_rotation = u @ correction @ vt
        optimal_rmsd = float(np.sqrt(np.mean(np.sum(
            (mobile_centered @ optimal_rotation - reference_centered) ** 2, axis=1))))
        if not math.isclose(rmsd, optimal_rmsd, rel_tol=1e-8, abs_tol=1e-8):
            errors.append("model transform is not a least-squares fit of selected pairs")
    return errors


def validate_bundle(bundle):
    errors = list(null_errors(bundle))
    if errors:
        return errors
    errors = [r.message for r in validator().validate(
        bundle, target_class="MolecularEvidenceBundle").results if r.severity == Severity.ERROR]
    if errors:
        return errors
    if not finite(bundle):
        return ["all molecular coordinates and distances must be finite"]

    def index(rows, key, label):
        result = {}
        for row in rows:
            if row[key] in result:
                errors.append(f"duplicate {label}: {row[key]}")
            result[row[key]] = row
        return result

    proteins = index(bundle["protein_references"], "protein_id", "protein")
    sources = index(bundle["sources"], "source_id", "source")
    sites = index(bundle["sites"], "assertion_id", "site")
    if not proteins or not sources or not sites or not bundle["trait_refs"]:
        errors.append("bundle requires nonempty proteins, sources, sites, and trait references")
    for source in sources.values():
        kind = source["artifact_kind"]
        if kind in {"PROTEIN_SEQUENCE", "PREDICTED_STRUCTURE"}:
            if source.get("protein_id") not in proteins:
                errors.append(f"source {source['source_id']}: {kind} requires protein_id that resolves in the bundle")
        elif kind in {"EXPERIMENTAL_STRUCTURE", "RESIDUE_MAPPING"}:
            if not source.get("structure_id"):
                errors.append(f"source {source['source_id']}: {kind} requires structure_id")
    for protein in proteins.values():
        if sha256(protein["sequence"]) != protein["sequence_sha256"]:
            errors.append("protein sequence checksum mismatch")
        if len(protein["sequence"]) != protein["sequence_length"]:
            errors.append("protein sequence length mismatch")
        pid = protein["protein_id"]
        isoform = int(pid.rsplit("-", 1)[1]) if "-" in pid else None
        if protein.get("isoform") != isoform:
            errors.append("protein isoform metadata mismatch")
    assertions = index([r for kind in ASSERTION_KINDS for r in bundle.get(kind, [])], "assertion_id", "assertion")
    for assertion in assertions.values():
        protein = proteins.get(assertion["protein_id"])
        if not protein or assertion["sequence_sha256"] != protein["sequence_sha256"]:
            errors.append(f"{assertion['assertion_id']}: protein/sequence does not resolve")
        if not assertion["evidence"] or not assertion["limitations"].strip():
            errors.append("assertions require evidence and explicit limits")
        for evidence in assertion["evidence"]:
            if not re.match(r"^(https?://\S+|DOI:10\.\S+)$", evidence["reference"]):
                errors.append("molecular assertion requires DOI or stable URL reference")
    if errors:
        return errors

    for site in sites.values():
        protein = proteins[site["protein_id"]]
        if site["evidence_origin"] != "COMPUTED_CONTACTS":
            errors.append("geometry site must remain COMPUTED_CONTACTS")
        for field, kind in (("structure_source", "EXPERIMENTAL_STRUCTURE"), ("mapping_source", "RESIDUE_MAPPING")):
            errors.extend(source_binding_errors(sources, site[field], kind, "structure_id",
                                                site["structure_id"], f"{site['assertion_id']}.{field}"))
        if not site["contacts"] or site["distance_cutoff_angstrom"] <= 0:
            errors.append("site requires contacts and a positive cutoff")
        seen = set()
        for contact in site["contacts"]:
            position = contact["protein_position"]
            if (not 1 <= position <= protein["sequence_length"] or
                    protein["sequence"][position - 1] != contact["protein_residue"]):
                errors.append("contact residue does not match exact protein sequence")
            a, b = contact["protein_atom"], contact["ligand_atom"]
            if AA3_TO_1.get(a["residue_name"]) != contact["protein_residue"]:
                errors.append("contact protein atom residue disagrees with mapped sequence residue")
            pair = (a["atom_id"], b["atom_id"])
            if pair in seen:
                errors.append("duplicate atom-pair contact")
            seen.add(pair)
            if a["element"].upper() in {"H", "D"} or b["element"].upper() in {"H", "D"}:
                errors.append("contact is not heavy-atom geometry")
            if a["occupancy"] <= 0 or b["occupancy"] <= 0:
                errors.append("contact atom has no positive occupancy")
            measured = distance(a, b)
            if abs(measured - contact["distance_angstrom"]) > 0.000001:
                errors.append("contact distance disagrees with coordinates")
            if measured > site["distance_cutoff_angstrom"]:
                errors.append("contact exceeds site cutoff")
            role = "MAINCHAIN" if a["atom_name"] in BACKBONE else "SIDECHAIN"
            if contact["atom_role"] != role:
                errors.append("contact atom role mismatch")
            instance = (f"{b['label_chain']}:{b['auth_chain']}:{b['auth_seq_id']}"
                        f"{b.get('insertion_code', '')}:{b['residue_name']}")
            if instance != site["ligand_instance"] or site["ligand_id"] != f"PDBCCD:{b['residue_name']}":
                errors.append("contact silently mixes ligand instances")
        previous = None
        for threshold in site.get("cutoff_sensitivity", []):
            cutoff, positions = threshold["cutoff_angstrom"], threshold["residue_positions"]
            hetero = threshold.get("sidechain_heteroatom_positions", [])
            if (cutoff <= 0 or positions != sorted(set(positions)) or hetero != sorted(set(hetero)) or
                    set(hetero) - set(positions) or threshold["atom_pair_count"] < len(positions) or
                    any(p > protein["sequence_length"] for p in positions)):
                errors.append("invalid contact threshold summary")
            if previous and (cutoff <= previous["cutoff_angstrom"] or
                             threshold["atom_pair_count"] < previous["atom_pair_count"] or
                             set(previous["residue_positions"]) - set(positions) or
                             set(previous.get("sidechain_heteroatom_positions", [])) - set(hetero)):
                errors.append("contact thresholds must be increasing and nested")
            if cutoff <= site["distance_cutoff_angstrom"]:
                selected = [c for c in site["contacts"] if distance(c["protein_atom"], c["ligand_atom"]) <= cutoff]
                expected_positions = sorted({c["protein_position"] for c in selected})
                expected_hetero = sorted({c["protein_position"] for c in selected if c["atom_role"] == "SIDECHAIN"
                                         and c["protein_atom"]["element"] in {"N", "O", "S"}})
                if len(selected) != threshold["atom_pair_count"] or positions != expected_positions or hetero != expected_hetero:
                    errors.append("threshold summary disagrees with deposited contact geometry")
            previous = threshold

    for comparison in bundle.get("comparisons", []):
        site = sites.get(comparison["site_ref"])
        if site is None:
            errors.append("comparison site does not resolve")
            continue
        if comparison["evidence_origin"] != "COMPUTED_COMPARISON":
            errors.append("derived correspondence must remain COMPUTED_COMPARISON")
        anchor, target = proteins[site["protein_id"]], proteins[comparison["protein_id"]]
        rows = comparison["residues"]
        errors.extend(target_order_errors(rows, f"site comparison {comparison['assertion_id']}"))
        positions = [r["anchor_position"] for r in rows]
        if positions != sorted({c["protein_position"] for c in site["contacts"]}):
            errors.append("comparison must cover each site residue exactly once, in order")
        for residue in rows:
            p = residue["anchor_position"]
            if not 1 <= p <= anchor["sequence_length"] or anchor["sequence"][p - 1] != residue["anchor_residue"]:
                errors.append("comparison anchor residue mismatch")
            if residue["status"] == "UNRESOLVED":
                if "target_position" in residue or "target_residue" in residue:
                    errors.append("unresolved correspondence cannot assert a target residue")
                continue
            t = residue.get("target_position", 0)
            aa = residue.get("target_residue")
            if not 1 <= t <= target["sequence_length"] or target["sequence"][t - 1] != aa:
                errors.append("comparison target residue mismatch")
            identical = residue["anchor_residue"] == aa
            if (residue["status"] == "IDENTICAL") != identical:
                errors.append("comparison identity status contradicts residue identities")

    for model in bundle.get("model_comparisons", []):
        errors.extend(validate_model_comparison(model, proteins, sources))

    for observation in bundle.get("functional_observations", []):
        if observation["outcome"] != "NOT_ASSESSED":
            if observation["evidence_origin"] != "EXPERIMENTAL_ASSAY":
                errors.append("functional result requires an experimental assay")
            if not any(e.get("snippet", "").strip() for e in observation["evidence"]):
                errors.append("functional result requires a supporting source excerpt")
        for field in ("conditions", "construct", "expression_localization_controls", "source_locator"):
            if not observation[field].strip():
                errors.append(f"functional observation requires explicit {field}")
        protein = proteins[observation["protein_id"]]
        substituted_positions = set()
        for change in observation.get("sequence_substitutions", []):
            position = change["position"]
            if position in substituted_positions:
                errors.append("duplicate assay substitution position")
            substituted_positions.add(position)
            if (not 1 <= position <= protein["sequence_length"] or
                    protein["sequence"][position - 1] != change["residue"]):
                errors.append("assay substitution does not match reference sequence")
            if change["residue"] == change["substituted_residue"]:
                errors.append("assay substitution must change the reference residue")

    for explanation in bundle.get("explanations", []):
        if explanation["evidence_origin"] != "CURATOR_INTERPRETATION":
            errors.append("explanation must remain CURATOR_INTERPRETATION")
        supporting = set(explanation.get("supporting_assertions", []))
        challenging = set(explanation.get("challenging_assertions", []))
        context = set(explanation.get("context_assertions", []))
        if supporting & challenging:
            errors.append("same assertion both supports and challenges one claim")
        if (supporting | challenging | context) - assertions.keys():
            errors.append("explanation assertion reference does not resolve")
        if any(assertions[ref]["evidence_origin"] == "CURATOR_INTERPRETATION" and "claim" in assertions[ref]
               for ref in context if ref in assertions):
            errors.append("explanation context cannot reference another explanation")
        if context & (supporting | challenging):
            errors.append("context-only assertions cannot also serve as explanation arguments")
        if explanation["assertion_id"] in supporting | challenging:
            errors.append("explanation cannot support itself")
        if explanation["assessment"] == "SUPPORTED" and not supporting:
            errors.append("supported explanation requires supporting assertions")
        if explanation["assessment"] == "CHALLENGED" and not challenging:
            errors.append("challenged explanation requires challenging assertions")
        if not explanation["unresolved_questions"]:
            errors.append("explanation must preserve open questions")

    # This is the evidence-dependency graph, not a biological mechanism graph:
    # biological feedback is allowed, but interpretations cannot justify themselves
    # indirectly through other interpretations (regardless of edge polarity).
    explanations = {e["assertion_id"]: e for e in bundle.get("explanations", [])}
    dependencies = {key: (set(e.get("supporting_assertions", [])) |
                          set(e.get("challenging_assertions", []))) & explanations.keys()
                    for key, e in explanations.items()}
    try:
        TopologicalSorter(dependencies).prepare()
    except CycleError:
        errors.append("explanation dependency cycle cannot justify an interpretation")

    mechanisms = bundle.get("mechanisms", [])
    index(mechanisms, "mechanism_id", "mechanism")
    warnings, stats = [], Counter()
    audit_record({"causal_graphs": [m["graph"] for m in mechanisms]}, bundle["bundle_id"],
                 node_type_enum(), errors, warnings, stats)
    errors.extend(w.message for w in warnings)
    for mechanism in mechanisms:
        if mechanism["trait_ref"] not in bundle["trait_refs"]:
            errors.append("mechanism trait scope does not resolve")
        if not mechanism["protein_ids"] or set(mechanism["protein_ids"]) - proteins.keys():
            errors.append("mechanism requires exact protein scope")
        if not mechanism["assertion_refs"] or set(mechanism["assertion_refs"]) - assertions.keys():
            errors.append("mechanism assertion scope does not resolve")
        for ref in sorted(explanation_closure(mechanism["assertion_refs"], explanations)):
            if ref in assertions and assertions[ref]["protein_id"] not in mechanism["protein_ids"]:
                errors.append(f"mechanism {mechanism['mechanism_id']}: assertion {ref} "
                              f"({assertions[ref]['protein_id']}) is outside its protein scope")
        if not mechanism["limitations"].strip():
            errors.append("mechanism requires explicit limitations")
        nodes = {n["node_id"]: n for n in mechanism["graph"]["nodes"]}
        residue_nodes = {key for key, node in nodes.items() if node["node_type"] == "RESIDUE"}
        bindings = mechanism.get("residue_bindings", [])
        if {b["node_id"] for b in bindings} != residue_nodes:
            errors.append("every residue node requires exact sequence bindings; no non-residue bindings")
        seen_bindings = set()
        for binding in bindings:
            key = (binding["node_id"], binding["protein_id"], binding["position"])
            if key in seen_bindings:
                errors.append("duplicate mechanism residue binding")
            seen_bindings.add(key)
            protein = proteins.get(binding["protein_id"])
            position = binding["position"]
            if (not protein or binding["protein_id"] not in mechanism["protein_ids"] or
                    binding["sequence_sha256"] != protein["sequence_sha256"] or
                    not 1 <= position <= protein["sequence_length"] or
                    protein["sequence"][position - 1] != binding["residue"]):
                errors.append("mechanism residue binding does not match scoped sequence")
            if "substituted_residue" in binding:
                change = {k: binding[k] for k in ("position", "residue", "substituted_residue")}
                if change["residue"] == change["substituted_residue"]:
                    errors.append("mechanism substitution must change the reference residue")
                # A double-mutant assay cannot justify one constituent mutation's
                # effect in isolation. Preserve the complete tested combination.
                fields = ("position", "residue", "substituted_residue")
                node_changes = {tuple(b[k] for k in fields) for b in bindings
                                if b["node_id"] == binding["node_id"] and b["protein_id"] == binding["protein_id"]
                                and "substituted_residue" in b}
                if not any(o["assertion_id"] in mechanism["assertion_refs"] and
                           o["protein_id"] == binding["protein_id"] and o["evidence_origin"] == "EXPERIMENTAL_ASSAY" and
                           o["outcome"] != "NOT_ASSESSED" and
                           node_changes == {tuple(c[k] for k in fields) for c in o.get("sequence_substitutions", [])}
                           for o in bundle.get("functional_observations", [])):
                    errors.append("mechanism substitution requires a matching scoped assay observation")
        for node in mechanism["graph"]["nodes"]:
            if not node.get("grounding") and not (node.get("local") and node.get("description")):
                errors.append("ungrounded mechanism nodes require local scope and description")
        for edge in mechanism["graph"]["edges"]:
            if not any(e.get("snippet", "").strip() for e in edge["evidence"]):
                errors.append("each causal edge requires a supporting verbatim excerpt")
            for evidence in edge["evidence"]:
                if not re.match(r"^(https?://\S+|DOI:10\.\S+)$", evidence["reference"]):
                    errors.append("molecular mechanism requires DOI or stable URL reference")
    errors.extend(validate_reasoning(bundle))
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path)
    args = parser.parse_args(argv)
    try:
        errors = validate_bundle(json.loads(args.bundle.read_text()))
    except (ValueError, OSError) as exc:
        errors = [str(exc)]
    for error in errors:
        print(error, file=sys.stderr)
    print(f"Molecular evidence validation: {len(errors)} errors")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
