"""Exact residue chemistry/context/effect ledgers, without invented causal paths."""
from __future__ import annotations

from copy import deepcopy
import math
import re

import gemmi

from amino_acid_properties import compare_residues, digest, validate_catalog, PROPERTY_IDS
from molecular_evidence import (AA3_TO_1, STATES, atoms_from_block, distance,
                                load_sifts_xml, source_residue_map)

ASSERTION_KINDS = ("sites", "comparisons", "model_comparisons", "functional_observations",
                   "explanations", "residue_environments", "residue_simulations")
ENVIRONMENT_METHOD = (
    "PTM residue neighborhood v1: all heavy-atom pairs to other SIFTS-mapped residues "
    "in the same deposited chain, including sequence neighbors; model 1; no symmetry "
    "expansion; independent alternate atoms, not a joint conformer or bond assignment."
)


def build_environment(snapshot, protein, position, pdb="7ZYI", chain="A", cutoff=4.5):
    """Call only after the builder verifies the complete source snapshot."""
    if type(position) is not int or not 1 <= position <= protein["sequence_length"]:
        raise ValueError("environment position outside reference")
    if not math.isfinite(cutoff) or not 0 < cutoff <= 10:
        raise ValueError("invalid environment cutoff")
    block = gemmi.cif.read_file(str(snapshot / f"{pdb}.cif")).sole_block()
    mapping_file = load_sifts_xml(snapshot / f"{pdb.lower()}.xml.gz")
    if (block.name.upper() != pdb or mapping_file.pdb_id.upper() != pdb or
            mapping_file.uniprot_release != protein["uniprot_release"]):
        raise ValueError("environment structure/mapping identity or release mismatch")
    mapping = source_residue_map(mapping_file, protein, chain)
    atoms = [a for a in atoms_from_block(block) if a["auth_chain"] == chain and a.get("label_seq_id")]
    mapped = []
    for atom in atoms:
        address = mapping.get((atom["auth_seq_id"], atom.get("insertion_code", "")))
        if not address or AA3_TO_1.get(atom["residue_name"]) != address[1]:
            raise ValueError("unmapped/mismatched residue in environment chain")
        mapped.append((atom, *address))
    focus = [a for a, p, _ in mapped if p == position]
    if not focus:
        raise ValueError("focus residue not observed in reference structure")
    neighbors = []
    for a in focus:
        for b, p, aa in mapped:
            d = distance(a, b)
            if p != position and d <= cutoff:
                neighbors.append(dict(partner_position=p, partner_residue=aa, focus_atom_id=a["atom_id"],
                                      partner_atom=b, distance_angstrom=round(d, 6)))
    return dict(assertion_id=f"slc10-environment:{pdb}-{chain}-{position}-{cutoff:g}A",
                protein_id=protein["protein_id"], sequence_sha256=protein["sequence_sha256"],
                position=position, residue=protein["sequence"][position - 1],
                evidence_origin="COMPUTED_CONTACTS", review_status="PROPOSED",
                structure_id=f"PDB:{pdb}", structure_source=f"{pdb}.cif", mapping_source=f"{pdb.lower()}.xml.gz",
                structure_state=STATES[pdb], model_number=1, auth_chain=chain,
                distance_cutoff_angstrom=cutoff, method=ENVIRONMENT_METHOD,
                focus_atoms=focus, neighbors=neighbors,
                evidence=[dict(reference=f"https://doi.org/10.2210/pdb{pdb}/pdb",
                               notes="Calculated deposited heavy-atom distances, not a quoted functional claim."),
                          dict(reference=f"https://www.ebi.ac.uk/pdbe/entry/pdb/{pdb.lower()}",
                               notes="Exact SIFTS mapping source is pinned in the bundle.")],
                limitations="Reference conformation only, not a mutant structure. Intrachain neighbors exclude "
                "water, ligands and other chains; no absence-of-interaction inference. Includes covalent sequence "
                "neighbors. Proximity does not establish hydrogen bonds, salt bridges, necessity, trafficking "
                "or transport effects; independent alternate atoms need not coexist.")


def _address_matches(row, binding, *, variant=False):
    keys = ["protein_id", "sequence_sha256", "position", "residue"]
    if variant:
        keys.append("substituted_residue")
    return all(row.get(k) == binding.get(k) for k in keys)


def validate_reasoning(bundle):
    """Cross-object semantics after closed schema and finite-value validation."""
    errors = []
    catalog = bundle.get("amino_acid_catalog")
    if catalog is not None:
        errors.extend(validate_catalog(catalog))
    if bundle.get("residue_reasoning") and catalog is None:
        errors.append("residue reasoning requires a reviewed embedded chemistry catalog")
    if errors:
        return errors
    proteins = {p["protein_id"]: p for p in bundle["protein_references"]}
    sources = {s["source_id"]: s for s in bundle["sources"]}
    environments = {r["assertion_id"]: r for r in bundle.get("residue_environments", [])}
    simulations = {r["assertion_id"]: r for r in bundle.get("residue_simulations", [])}
    sites = {r["assertion_id"]: r for r in bundle["sites"]}
    contexts = {**environments, **simulations, **sites}
    mechanisms = {m["mechanism_id"]: m for m in bundle.get("mechanisms", [])}
    assays = {r["assertion_id"]: r for r in bundle.get("functional_observations", [])}
    for row in [*environments.values(), *simulations.values()]:
        label = row["assertion_id"]
        p = proteins.get(row["protein_id"])
        pos = row["position"]
        if (not p or row["sequence_sha256"] != p["sequence_sha256"] or type(pos) is not int or
                not 1 <= pos <= p["sequence_length"] or p["sequence"][pos - 1] != row["residue"]):
            errors.append(f"{label}: context residue does not match pinned protein")
            continue
        if label in simulations:
            if row["evidence_origin"] != "PUBLISHED_SIMULATION" or row["substituted_residue"] == row["residue"]:
                errors.append(f"{label}: simulation must remain variant-specific published computation")
            if not re.fullmatch(r"(CHEBI|UniProtKB|PR|RNAcentral|PDBCCD):\S+", row["partner_id"]):
                errors.append(f"{label}: simulation partner requires a grounded molecular identity")
            if not any(e.get("snippet", "").strip() for e in row["evidence"]):
                errors.append(f"{label}: simulation requires source excerpt")
            continue
        if row["evidence_origin"] != "COMPUTED_CONTACTS" or row["method"] != ENVIRONMENT_METHOD or row["model_number"] != 1:
            errors.append(f"{label}: environment computation contract mismatch")
        for field, kind in (("structure_source", "EXPERIMENTAL_STRUCTURE"), ("mapping_source", "RESIDUE_MAPPING")):
            source = sources.get(row[field], {})
            if source.get("artifact_kind") != kind or source.get("structure_id") != row["structure_id"]:
                errors.append(f"{label}: environment source does not resolve with matching identity/role")
        atoms = {a["atom_id"]: a for a in row["focus_atoms"]}
        if not atoms or len(atoms) != len(row["focus_atoms"]):
            errors.append(f"{label}: empty/duplicate environment focus atoms")
        for a in atoms.values():
            if (a["auth_chain"] != row["auth_chain"] or AA3_TO_1.get(a["residue_name"]) != row["residue"] or
                    a["element"] in {"H", "D"} or not a.get("label_seq_id") or a["occupancy"] <= 0):
                errors.append(f"{label}: invalid reference focus atom")
        focus_addresses = {(a["auth_seq_id"], a.get("insertion_code", ""), a["label_chain"], a.get("label_seq_id"))
                           for a in atoms.values()}
        if len(focus_addresses) != 1:
            errors.append(f"{label}: focus atoms span multiple residues")
        pairs, partner_atoms = set(), {}
        for neighbor in row["neighbors"]:
            a = atoms.get(neighbor["focus_atom_id"])
            b = neighbor["partner_atom"]
            q = neighbor["partner_position"]
            key = (neighbor["focus_atom_id"], b["atom_id"])
            identity = (q, neighbor["partner_residue"], b)
            if key in pairs or (b["atom_id"] in partner_atoms and partner_atoms[b["atom_id"]] != identity):
                errors.append(f"{label}: duplicate/inconsistent neighborhood atom pair")
            pairs.add(key)
            partner_atoms[b["atom_id"]] = identity
            if (type(q) is not int or not 1 <= q <= p["sequence_length"] or q == pos or
                    p["sequence"][q - 1] != neighbor["partner_residue"] or
                    AA3_TO_1.get(b["residue_name"]) != neighbor["partner_residue"] or
                    b["auth_chain"] != row["auth_chain"] or not b.get("label_seq_id") or
                    b["element"] in {"H", "D"} or b["occupancy"] <= 0 or b["atom_id"] in atoms):
                errors.append(f"{label}: neighbor does not match reference protein/chain")
            if not a or (distance(a, b) > row["distance_cutoff_angstrom"] or
                         abs(distance(a, b) - neighbor["distance_angstrom"]) > 1e-5):
                errors.append(f"{label}: invalid neighborhood atom/distance/cutoff")
        if row["distance_cutoff_angstrom"] <= 0:
            errors.append(f"{label}: environment cutoff must be positive")
    seen = set()
    for row in bundle.get("residue_reasoning", []):
        label = row["reasoning_id"]
        if label in seen:
            errors.append(f"duplicate residue reasoning: {label}")
        seen.add(label)
        m = mechanisms.get(row["mechanism_id"])
        binding = row["residue_binding"]
        if not m or binding not in m.get("residue_bindings", []):
            errors.append(f"{label}: reasoning must reference an exact mechanism binding")
            continue
        if row["catalog_sha256"] != digest(catalog):
            errors.append(f"{label}: chemistry catalog pin mismatch")
        if not row["property_context_links"] or not row["context_trait_links"] or not row["limitations"].strip():
            errors.append(f"{label}: reasoning requires explicit property/context/consequence links and limits")
        # Do not split a compound perturbation into a single-residue explanation.
        changes = [b for b in m["residue_bindings"] if b["node_id"] == binding["node_id"] and "substituted_residue" in b]
        if len(changes) != 1 or changes[0] != binding:
            errors.append(f"{label}: current reasoning contract requires an isolated single substitution")
        if any(binding.get(k) not in {e["one_letter"] for e in catalog["amino_acids"]}
               for k in ("residue", "substituted_residue")):
            errors.append(f"{label}: unsupported chemistry cannot justify context links")
        linked = set()
        for link in row["property_context_links"]:
            ref = link["context_ref"]
            if ref in linked:
                errors.append(f"{label}: duplicate property/context link")
            linked.add(ref)
            c = contexts.get(ref)
            if (not c or c["protein_id"] != binding["protein_id"] or
                    c["sequence_sha256"] != binding["sequence_sha256"]):
                errors.append(f"{label}: context protein/sequence does not match binding")
                continue
            if (not link["property_ids"] or len(set(link["property_ids"])) != len(link["property_ids"]) or
                    set(link["property_ids"]) - set(PROPERTY_IDS)):
                errors.append(f"{label}: missing/invalid/duplicate property selection")
            if ref in sites:
                matches = any(cn["protein_position"] == binding["position"] and cn["protein_residue"] == binding["residue"]
                              for cn in c["contacts"])
            else:
                matches = _address_matches(c, binding, variant=ref in simulations)
            expected = "COMPUTATIONAL_HYPOTHESIS" if ref in simulations else "REFERENCE_CONTEXT_ONLY"
            if ref in simulations and link.get("partner_id") != c["partner_id"]:
                errors.append(f"{label}: simulation partner does not match property/context link")
            if ref not in simulations and "partner_id" in link:
                errors.append(f"{label}: partner selection is only supported for simulation context")
            if not matches or link["assessment"] != expected:
                errors.append(f"{label}: context residue/variant or evidence assessment mismatch")
            if not link["description"].strip() or not link["limitations"].strip():
                errors.append(f"{label}: property/context link requires description and limitations")
        seen_outcomes = set()
        for link in row["context_trait_links"]:
            ref = link["observation_ref"]
            assay = assays.get(ref)
            variant = {k: binding[k] for k in ("position", "residue", "substituted_residue") if k in binding}
            if (not assay or ref not in m["assertion_refs"] or assay["protein_id"] != binding["protein_id"] or
                    assay["sequence_sha256"] != binding["sequence_sha256"] or
                    assay["evidence_origin"] != "EXPERIMENTAL_ASSAY" or assay["outcome"] == "NOT_ASSESSED" or
                    assay.get("sequence_substitutions") != [variant]):
                errors.append(f"{label}: consequence requires a matching scoped single-variant measured assay")
            if ref in seen_outcomes:
                errors.append(f"{label}: duplicate consequence branch")
            seen_outcomes.add(ref)
            if not link["context_refs"] or len(set(link["context_refs"])) != len(link["context_refs"]) or set(link["context_refs"]) - linked:
                errors.append(f"{label}: consequence contexts must resolve through this residue's property links")
            for context_ref in link["context_refs"]:
                if context_ref in simulations and (not assay or assay.get("substrate_id") != simulations[context_ref]["partner_id"]):
                    errors.append(f"{label}: simulation/assay substrate mismatch or missing explicit identity")
            if link["assessment"] == "SOURCE_PROPOSED_HYPOTHESIS":
                if not any(e.get("snippet", "").strip() and re.match(r"^(https?://\S+|DOI:10\.\S+)$", e["reference"])
                           for e in link.get("evidence", [])):
                    errors.append(f"{label}: mediation hypothesis requires its own exact source evidence")
            if not link["description"].strip() or not link["limitations"].strip():
                errors.append(f"{label}: consequence link requires description and limitations")
    return errors


def query_chemistry(bundle, query, protein):
    """A valid residue has chemistry even when no curated mechanism matches."""
    binding = {"protein_id": protein["protein_id"], "sequence_sha256": protein["sequence_sha256"], **query}
    result = {"residue_address": binding, "causal_inference": "NONE", "local_context": []}
    catalog = bundle.get("amino_acid_catalog")
    if catalog is None:
        return {**result, "status": "CATALOG_NOT_INCLUDED"}
    result.update(status="REFERENCE_CHEMISTRY", chemistry=compare_residues(
        catalog, query["residue"], query.get("substituted_residue")))
    for kind in ("residue_environments", "residue_simulations"):
        for context in bundle.get(kind, []):
            if _address_matches(context, binding, variant=kind == "residue_simulations"):
                result["local_context"].append(deepcopy(context))
    for site in bundle["sites"]:
        if (site["protein_id"] == binding["protein_id"] and site["sequence_sha256"] == binding["sequence_sha256"] and
                any(c["protein_position"] == query["position"] and c["protein_residue"] == query["residue"]
                    for c in site["contacts"])):
            result["local_context"].append(deepcopy(site))
    result["limitations"] = ("Reference-structure context is not a mutant structure. An exact variant simulation "
                             "is labeled separately. Missing curated context is not absence of interactions or effect.")
    return result


def residue_evidence(bundle, mechanism, bindings):
    """Keep the graph unchanged; expose catalog contrasts and explicit ledgers separately."""
    catalog = bundle.get("amino_acid_catalog")
    if catalog is None:
        return {"status": "CATALOG_NOT_INCLUDED", "entries": [], "causal_inference": "NONE"}
    assertions = {r["assertion_id"]: r for kind in ASSERTION_KINDS for r in bundle.get(kind, [])}
    entries = []
    for binding in bindings:
        entry = {"residue_binding": deepcopy(binding),
                 "chemistry": compare_residues(catalog, binding["residue"], binding.get("substituted_residue")),
                 "reasoning": []}
        for row in bundle.get("residue_reasoning", []):
            if row["mechanism_id"] != mechanism["mechanism_id"] or row["residue_binding"] != binding:
                continue
            refs = {link["context_ref"] for link in row["property_context_links"]}
            refs.update(link["observation_ref"] for link in row["context_trait_links"])
            entry["reasoning"].append({**deepcopy(row), "assertions": [deepcopy(assertions[r]) for r in sorted(refs)]})
        entry["reasoning_status"] = "CURATED_EVIDENCE_LEDGER" if entry["reasoning"] else "NO_CURATED_PROPERTY_CONTEXT_LINK"
        entries.append(entry)
    return {"status": "REFERENCE_CHEMISTRY_WITH_SCOPED_EVIDENCE", "entries": entries, "causal_inference": "NONE"}
