"""Sequence-selected apo-model comparisons, without ligand transfer or nearest-neighbor pairing."""
from __future__ import annotations

import json
import math
from pathlib import Path

import gemmi
import numpy as np
from Bio.SVDSuperimposer import SVDSuperimposer

from build_ecod_sifts_candidates import AA3_TO_1, load_sifts_xml
from fetch_slc10_models import MODEL_PANEL, MODEL_VERSION, sources
from molecular_evidence import atoms_from_block, correspondence, sha256, source_residue_map, METHOD

CONFIDENCE_THRESHOLD = 70.0
MINIMUM_FIT_PAIRS = 20
GEOMETRY_WARNING_ANGSTROM = 3.0


def read_model_snapshot(directory):
    directory = Path(directory)
    manifest = json.loads((directory / "manifest.json").read_text())
    if (manifest.get("kind") != "SLC10_PREDICTED_MODEL_SNAPSHOT" or
            manifest.get("schema_version") != 1 or manifest.get("model_version") != MODEL_VERSION):
        raise ValueError("not a complete version-pinned model snapshot")
    expected = {Path(r["local_name"]).name: r for r in sources()}
    artifacts = manifest.get("artifacts", [])
    if len(artifacts) != len(expected) or {a.get("path") for a in artifacts} != set(expected):
        raise ValueError("incomplete or duplicated model artifacts")
    for artifact in artifacts:
        path = directory / artifact["path"]
        if (path.is_symlink() or sha256(path.read_bytes()) != artifact["sha256"] or
                artifact["requested_url"] != expected[path.name]["url"] or
                artifact.get("model_version") != MODEL_VERSION or
                artifact.get("license") != expected[path.name]["license"] or
                artifact.get("license_url") != expected[path.name]["license_url"]):
            raise ValueError("model snapshot bytes, version, URL, or licence mismatch")
    return manifest


def read_model(path, protein):
    block = gemmi.cif.read_file(str(path)).sole_block()
    accession = protein["protein_id"].split(":", 1)[1]
    ref = block.get_mmcif_category("_ma_target_ref_db_details.")
    if (block.name != f"AF-{accession}-F1" or ref.get("db_accession") != [accession] or
            ref.get("db_name") != ["UNP"] or ref.get("seq_db_align_begin") != ["1"] or
            ref.get("seq_db_align_end") != [str(protein["sequence_length"])]):
        raise ValueError("prediction identity or full-sequence frame mismatch")
    sequence_rows = block.get_mmcif_category("_entity_poly_seq.")
    rows = sorted(zip(sequence_rows["num"], sequence_rows["mon_id"], strict=True), key=lambda r: int(r[0]))
    if ([int(p) for p, _ in rows] != list(range(1, protein["sequence_length"] + 1)) or
            "".join(AA3_TO_1.get(aa, "?") for _, aa in rows) != protein["sequence"]):
        raise ValueError("predicted sequence differs from pinned UniProt sequence")
    metrics = block.get_mmcif_category("_ma_qa_metric.")
    local_ids = {i for i, mode, kind in zip(metrics["id"], metrics["mode"], metrics["type"], strict=True)
                 if mode == "local" and kind == "pLDDT"}
    quality = block.get_mmcif_category("_ma_qa_metric_local.")
    confidence = {}
    for row in zip(*(quality[k] for k in ("label_seq_id", "metric_id", "metric_value", "model_id", "label_asym_id")), strict=True):
        position, metric_id, value, model_id, chain = row
        if metric_id not in local_ids or model_id != "1" or chain != "A":
            continue
        position, value = int(position), float(value)
        if position in confidence or not math.isfinite(value) or not 0 <= value <= 100:
            raise ValueError("invalid or duplicated model confidence")
        confidence[position] = value
    ca = {}
    for atom in atoms_from_block(block):
        position = atom.get("label_seq_id", 0)
        if (atom["auth_chain"] != "A" or atom["label_chain"] != "A" or
                not 1 <= position <= protein["sequence_length"] or
                atom["auth_seq_id"] != str(position) or atom.get("insertion_code") or
                AA3_TO_1.get(atom["residue_name"]) != protein["sequence"][position - 1]):
            raise ValueError("prediction atom frame or identity mismatch; no target ligands permitted")
        if atom["atom_name"] == "CA":
            if position in ca or atom.get("altloc"):
                raise ValueError("ambiguous prediction CA")
            ca[position] = atom
    expected = set(range(1, protein["sequence_length"] + 1))
    if set(ca) != expected or set(confidence) != expected:
        raise ValueError("model lacks complete CA coordinates or confidence")
    return ca, confidence


def experimental_ca(directory, protein):
    directory = Path(directory)
    mapping = source_residue_map(load_sifts_xml(directory / "7zyi.xml.gz"), protein, "A")
    atoms = atoms_from_block(gemmi.cif.read_file(str(directory / "7ZYI.cif")).sole_block())
    ca = {}
    # Deterministic single CA per residue, while the contact extractor preserves all altlocs.
    for atom in sorted(atoms, key=lambda a: (-a["occupancy"], a.get("altloc", ""), a["atom_id"])):
        if atom["auth_chain"] != "A" or atom["atom_name"] != "CA" or not atom.get("label_seq_id"):
            continue
        position, aa = mapping[(atom["auth_seq_id"], atom.get("insertion_code", ""))]
        if AA3_TO_1.get(atom["residue_name"]) != aa:
            raise ValueError("experimental CA identity mismatch")
        ca.setdefault(position, atom)
    return ca


def coords(atom):
    return [atom[axis] for axis in ("x", "y", "z")]


def fit_pairs(pairs, minimum=MINIMUM_FIT_PAIRS):
    selected = [p for p in pairs if p["used_in_fit"]]
    result = {"fit_residue_count": len(selected), "minimum_fit_pairs": minimum,
              "fit_status": "INSUFFICIENT_PAIRS"}
    if len(selected) < minimum:
        return result
    reference = np.array([coords(p["anchor_ca"]) for p in selected])
    mobile = np.array([coords(p["target_ca"]) for p in selected])
    if np.linalg.matrix_rank(reference - reference.mean(axis=0)) < 2 or np.linalg.matrix_rank(mobile - mobile.mean(axis=0)) < 2:
        raise ValueError("degenerate CA fit")
    fit = SVDSuperimposer()
    fit.set(reference, mobile)
    fit.run()
    rotation, translation = fit.get_rotran()
    result.update({"fit_status": "ALIGNED", "rotation": rotation.ravel().tolist(),
                   "translation": translation.tolist(), "fit_rmsd_angstrom": float(fit.get_rms())})
    for pair in pairs:
        if "anchor_ca" in pair and "target_ca" in pair:
            residual = float(np.linalg.norm(np.array(coords(pair["target_ca"])) @ rotation + translation - coords(pair["anchor_ca"])))
            pair["ca_displacement_angstrom"] = residual
            pair["geometry_note"] = (
                "LOW_CONFIDENCE: predicted local geometry is uncertain."
                if pair["target_plddt"] < CONFIDENCE_THRESHOLD else
                "DISCORDANT: >3 A residual; correspondence, conformation and global-fit effects remain unresolved."
                if residual > GEOMETRY_WARNING_ANGSTROM else
                "WITHIN_3A: geometric agreement under this fit, not evidence of binding or activity.")
    return result


def build_model_comparisons(snapshot, model_snapshot, proteins):
    model_snapshot = Path(model_snapshot)
    manifest = read_model_snapshot(model_snapshot)
    lookup = {p["protein_id"].split(":", 1)[1]: p for p in proteins}
    anchor = lookup["Q14973"]
    anchor_ca = experimental_ca(snapshot, anchor)
    model_owners = {f"AF-{accession}-F1-model_v{MODEL_VERSION}.cif": f"UniProtKB:{accession}"
                    for accession in MODEL_PANEL}
    artifacts = [{"source_id": a["path"], "reference": a["requested_url"], "sha256": a["sha256"],
                  "artifact_kind": "PREDICTED_STRUCTURE", "protein_id": model_owners[a["path"]],
                  "source_version": f"AlphaFold DB file version {MODEL_VERSION}", "license": a["license"],
                  "license_url": a["license_url"]} for a in manifest["artifacts"]]
    comparisons = []
    for accession in MODEL_PANEL:
        protein = lookup[accession]
        name = f"AF-{accession}-F1-model_v{MODEL_VERSION}.cif"
        target_ca, confidence = read_model(model_snapshot / name, protein)
        mapping = correspondence(anchor["sequence"], protein["sequence"])
        pairs = []
        for position, aa in enumerate(anchor["sequence"], 1):
            target = mapping.get(position)
            pair = {"anchor_position": position, "anchor_residue": aa, "status": "UNRESOLVED",
                    "mapping_note": "Sequence-path consensus only, not independent structural correspondence.",
                    "used_in_fit": False, "geometry_note": "UNRESOLVED_MAPPING: no target coordinate assigned."}
            if position in anchor_ca:
                pair["anchor_ca"] = anchor_ca[position]
            if target is not None:
                residue = protein["sequence"][target - 1]
                pair.update({"target_position": target, "target_residue": residue,
                             "status": "IDENTICAL" if aa == residue else "CHANGED",
                             "target_ca": target_ca[target], "target_plddt": confidence[target],
                             "used_in_fit": position in anchor_ca and confidence[target] >= CONFIDENCE_THRESHOLD,
                             "geometry_note": "UNOBSERVED_ANCHOR: no experimental CA coordinate." if position not in anchor_ca else
                                              "INSUFFICIENT_FIT: no transform computed yet."})
            pairs.append(pair)
        fit = fit_pairs(pairs)
        comparisons.append({
            "assertion_id": f"slc10-model:{accession}-v{MODEL_VERSION}-7ZYI",
            "protein_id": protein["protein_id"], "sequence_sha256": protein["sequence_sha256"],
            "evidence_origin": "COMPUTED_COMPARISON", "review_status": "PROPOSED",
            "anchor_protein_id": anchor["protein_id"], "anchor_structure_id": "PDB:7ZYI",
            "anchor_structure_source": "7ZYI.cif",
            "mapping_source": "7zyi.xml.gz", "model_source": name,
            "method": METHOD + "; untrimmed least-squares CA fit of all consensus pairs with target pLDDT>=70; "
                      "reference altloc: highest occupancy, then lexical altloc; no remapping after superposition",
            "confidence_threshold": CONFIDENCE_THRESHOLD, "pairs": pairs, **fit,
            "evidence": [{"reference": f"https://alphafold.ebi.ac.uk/entry/{accession}", "notes": "Apo prediction; exact input hash in sources."},
                         {"reference": "https://doi.org/10.2210/pdb7ZYI/pdb", "notes": "Experimental reference only; no ligand transferred to predicted model."}],
            "limitations": "Sequence-consensus pairing can still be biologically wrong. Global-fit residuals mix mapping error, "
                           "conformational change and model error; they are not physical movements. pLDDT is local confidence, "
                           "not interdomain alignment certainty. No target ion, binding, transport or inactivity is inferred.",
        })
    return artifacts, comparisons
