"""Reproducible molecular observations; no trait or grounding-registry writer.

The public objects follow the LinkML MolecularEvidenceBundle contract. Geometry
is computed evidence and sequence correspondence is a hypothesis, not a source
assertion. Experimental PDB coordinates are mapped only through residue SIFTS.
"""
from __future__ import annotations

from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path

import gemmi
from Bio import Align, __version__ as biopython_version
from Bio.Align import substitution_matrices

from build_ecod_sifts_candidates import AA3_TO_1, load_sifts_xml
from fetch_slc10_pilot import PANEL, STRUCTURES, sources

BACKBONE = frozenset({"N", "CA", "C", "O", "OXT"})
STATES = {
    "7ZYI": "Bile-salt-bound NTCP with Fab and nanobody; deposited cryo-EM conformation",
    "9QZQ": "Nanobody-inhibited closed-tunnel NTCP; not a demonstrated productive transport state",
    "8RQF": "Bulevirtide-bound NTCP; drug binding is not a viral infection assay",
}
LIGANDS = {"7ZYI": {"NA", "CHO"}, "9QZQ": {"NA"}, "8RQF": {"BJU"}}
METHOD = (f"PTM optimal-path DAG v1; Biopython {biopython_version} score cross-check; "
          "global BLOSUM62; gap-open/extend=-10/-0.5 and -12/-1; "
          "per-column consensus over ALL optimal paths at both settings; "
          "gap or disagreement => UNRESOLVED; no geometric nearest-neighbor mapping")


def sha256(value):
    return hashlib.sha256(value.encode() if isinstance(value, str) else value).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def read_snapshot(directory):
    directory = Path(directory)
    manifest = json.loads((directory / "manifest.json").read_text())
    if manifest.get("kind") != "SLC10_RESEARCH_SNAPSHOT" or manifest.get("schema_version") != 1:
        raise ValueError("not a complete SLC10 acquisition")
    expected = {r["local_name"].split("/")[-1]: r for r in sources()}
    artifacts = manifest.get("artifacts", [])
    if len(artifacts) != len(expected) or {a.get("path") for a in artifacts} != set(expected):
        raise ValueError("incomplete or duplicated snapshot artifacts")
    for artifact in artifacts:
        path = directory / artifact["path"]
        source = expected[artifact["path"]]
        if path.is_symlink() or sha256(path.read_bytes()) != artifact["sha256"]:
            raise ValueError(f"snapshot bytes changed: {path.name}")
        if artifact["requested_url"] != source["url"]:
            raise ValueError("snapshot source URL changed")
        if path.suffix == ".json" and artifact.get("uniprot_release") != manifest["uniprot_release"]:
            raise ValueError("mixed UniProt releases")
    return manifest


def protein_references(directory, manifest):
    references = []
    for accession in PANEL:
        entry = json.loads((Path(directory) / f"{accession}.json").read_text())
        if entry["primaryAccession"] != accession:
            raise ValueError("protein accession mismatch")
        sequence = entry["sequence"]["value"]
        if len(sequence) != entry["sequence"]["length"]:
            raise ValueError("protein sequence length mismatch")
        references.append({
            "protein_id": f"UniProtKB:{accession}",
            "protein_label": entry["proteinDescription"]["recommendedName"]["fullName"]["value"],
            "taxon_id": f"NCBITaxon:{entry['organism']['taxonId']}",
            "taxon_label": entry["organism"]["scientificName"],
            "sequence": sequence, "sequence_length": len(sequence),
            "sequence_sha256": sha256(sequence), "reviewed": entry["entryType"].endswith("reviewed (Swiss-Prot)"),
            "uniprot_release": manifest["uniprot_release"],
            "sequence_version": entry["entryAudit"]["sequenceVersion"],
        })
    return references


def atoms_from_block(block, model_number=1):
    category = block.get_mmcif_category("_atom_site.")
    if not category:
        raise ValueError("structure has no atoms")
    atoms, seen = [], set()
    for row in zip(*category.values(), strict=True):
        raw = dict(zip(category, row, strict=True))
        if int(raw["pdbx_PDB_model_num"]) != model_number:
            continue
        if raw["type_symbol"].upper() in {"H", "D"}:
            continue
        if raw["id"] in seen:
            raise ValueError("duplicate atom identifier")
        seen.add(raw["id"])
        atom = {
            "atom_id": raw["id"], "atom_name": raw["label_atom_id"],
            "element": raw["type_symbol"], "residue_name": raw["label_comp_id"],
            "auth_chain": raw["auth_asym_id"], "label_chain": raw["label_asym_id"],
            "auth_seq_id": raw["auth_seq_id"],
            "occupancy": float(raw["occupancy"]),
            "x": float(raw["Cartn_x"]), "y": float(raw["Cartn_y"]), "z": float(raw["Cartn_z"]),
        }
        for source, target in (("label_seq_id", "label_seq_id"),
                               ("label_alt_id", "altloc"), ("pdbx_PDB_ins_code", "insertion_code")):
            if raw[source] not in (None, False, ".", "?"):
                atom[target] = int(raw[source]) if target == "label_seq_id" else raw[source]
        if any(not math.isfinite(atom[k]) for k in ("x", "y", "z", "occupancy")):
            raise ValueError("non-finite atom coordinate/occupancy")
        if not 0 < atom["occupancy"] <= 1:
            raise ValueError("zero/invalid occupancy requires explicit handling")
        atoms.append(atom)
    if not atoms:
        raise ValueError("requested model has no heavy atoms")
    return atoms


def distance(first, second):
    return math.sqrt(sum((first[k] - second[k]) ** 2 for k in ("x", "y", "z")))


def source_residue_map(sifts, protein, auth_chain):
    accession = protein["protein_id"].split(":", 1)[1]
    result = {}
    for residue in sifts.residues:
        if residue.chain != auth_chain or residue.native is None:
            continue
        if residue.ambiguous or residue.uniprot_accession != accession:
            raise ValueError("ambiguous or wrong-protein SIFTS mapping")
        position = residue.uniprot_position
        if not position or not 1 <= position <= protein["sequence_length"]:
            raise ValueError("SIFTS residue outside pinned sequence")
        aa = protein["sequence"][position - 1]
        if aa != residue.uniprot_amino_acid or aa != residue.pdb_amino_acid:
            raise ValueError("SIFTS residue identity differs from pinned sequence")
        key = (str(residue.native.number), residue.native.insertion_code)
        if key in result:
            raise ValueError("duplicated SIFTS residue mapping")
        result[key] = (position, aa)
    if not result:
        raise ValueError("no exact SIFTS protein mappings")
    return result


def extract_sites(directory, pdb, protein, cutoff=4.5):
    if not math.isfinite(cutoff) or not 0 < cutoff <= 10:
        raise ValueError("invalid contact cutoff")
    directory = Path(directory)
    block = gemmi.cif.read_file(str(directory / f"{pdb}.cif")).sole_block()
    if block.name.upper() != pdb:
        raise ValueError("PDB identifier mismatch")
    sifts = load_sifts_xml(directory / f"{pdb.lower()}.xml.gz")
    if sifts.pdb_id.upper() != pdb or sifts.uniprot_release != protein["uniprot_release"]:
        raise ValueError("SIFTS identity/release mismatch")
    mapping = source_residue_map(sifts, protein, "A")
    atoms = atoms_from_block(block)
    protein_atoms = [a for a in atoms if a["auth_chain"] == "A" and a.get("label_seq_id")]
    # Check every deposited protein atom, not just the convenient contact subset.
    for atom in protein_atoms:
        key = (atom["auth_seq_id"], atom.get("insertion_code", ""))
        if key not in mapping or AA3_TO_1.get(atom["residue_name"]) != mapping[key][1]:
            raise ValueError(f"unmapped or mismatched deposited protein residue: {key}")
    ligands = defaultdict(list)
    for atom in atoms:
        if atom["residue_name"] in LIGANDS[pdb]:
            key = (atom["label_chain"], atom["auth_chain"], atom["auth_seq_id"],
                   atom.get("insertion_code", ""), atom["residue_name"])
            ligands[key].append(atom)
    if {key[-1] for key in ligands} != LIGANDS[pdb] or not protein_atoms:
        raise ValueError("expected ligand/protein coordinates absent")
    sites = []
    for key, ligand_atoms in sorted(ligands.items()):
        label_chain, auth_chain, number, insertion, component = key
        contacts = []
        for first in protein_atoms:
            position, aa = mapping[(first["auth_seq_id"], first.get("insertion_code", ""))]
            for second in ligand_atoms:
                dist = distance(first, second)
                if dist <= max(cutoff, 5.0):
                    contacts.append({"protein_position": position, "protein_residue": aa,
                                     "protein_atom": first, "ligand_atom": second,
                                     "atom_role": "MAINCHAIN" if first["atom_name"] in BACKBONE else "SIDECHAIN",
                                     "distance_angstrom": round(dist, 6)})
        sensitivity = []
        for threshold in sorted({4.0, 4.5, 5.0, cutoff}):
            # Use unrounded coordinate distances at every boundary.
            selected = [c for c in contacts if distance(c["protein_atom"], c["ligand_atom"]) <= threshold]
            sensitivity.append({"cutoff_angstrom": threshold, "atom_pair_count": len(selected),
                                "residue_positions": sorted({c["protein_position"] for c in selected}),
                                "sidechain_heteroatom_positions": sorted({c["protein_position"] for c in selected
                                    if c["atom_role"] == "SIDECHAIN" and c["protein_atom"]["element"] in {"N", "O", "S"}})})
        contacts = [c for c in contacts if distance(c["protein_atom"], c["ligand_atom"]) <= cutoff]
        if not contacts:
            raise ValueError(f"selected ligand has no contacts: {key}")
        instance = f"{label_chain}:{auth_chain}:{number}{insertion}:{component}"
        sites.append({
            "assertion_id": f"slc10-site:{pdb}-{label_chain}-{number}{insertion}-{component}-{cutoff:g}A",
            "protein_id": protein["protein_id"], "sequence_sha256": protein["sequence_sha256"],
            "label": f"NTCP {component} contact shell ({pdb}, {instance})",
            "evidence_origin": "COMPUTED_CONTACTS", "review_status": "PROPOSED",
            "structure_id": f"PDB:{pdb}", "structure_source": f"{pdb}.cif",
            "mapping_source": f"{pdb.lower()}.xml.gz", "structure_state": STATES[pdb],
            "model_number": 1, "assembly_scope": "DEPOSITED_ASYMMETRIC_UNIT",
            "conformer_policy": "INDEPENDENT_ATOM_PROXIMITIES_NO_JOINT_CONFORMER_ASSERTION",
            "ligand_id": f"PDBCCD:{component}", "ligand_instance": instance,
            "distance_cutoff_angstrom": cutoff, "contacts": contacts, "cutoff_sensitivity": sensitivity,
            "evidence": [{"reference": f"https://doi.org/10.2210/pdb{pdb}/pdb",
                          "notes": "Calculated from deposited atom_site coordinates; not a quoted functional claim."},
                         {"reference": f"https://www.ebi.ac.uk/pdbe/entry/pdb/{pdb.lower()}",
                          "notes": "Residue-level SIFTS mapping; exact source hash/version in bundle."}],
            "limitations": "Heavy-atom proximity is a contact candidate, not proof of coordination or causal necessity. "
                           "Backbone-mediated contact does not make substitutions functionally neutral. "
                           "Alternate atoms retain their identities/occupancies; contacts do not assert simultaneous conformers. "
                           "No symmetry expansion or inference of a complete transport cycle.",
        })
    return sites


def optimal_correspondences(anchor, target, gap_open, gap_extend):
    """All possible partners on optimal affine-gap paths, without enumerating paths.

    Forward Gotoh scores define a DAG. Backtracking every tied predecessor from
    every optimal terminal state visits each state at most once, so an exponential
    number of equivalent alignments cannot hide stable columns or force truncation.
    Opposite-gap transitions are allowed, matching PairwiseAligner's global model.
    """
    if not anchor or not target:
        raise ValueError("empty sequence has no protein correspondence")
    matrix = substitution_matrices.load("BLOSUM62")
    n, m = len(anchor), len(target)
    scores = [[[float("-inf")] * (m + 1) for _ in range(n + 1)] for _ in range(3)]
    match, deletion, insertion = scores
    match[0][0] = 0
    for i in range(1, n + 1):
        deletion[i][0] = gap_open + (i - 1) * gap_extend
    for j in range(1, m + 1):
        insertion[0][j] = gap_open + (j - 1) * gap_extend
    substitutions = {(a, b): float(matrix[a, b]) for a in set(anchor) for b in set(target)}
    for i, a in enumerate(anchor, 1):
        for j, b in enumerate(target, 1):
            match[i][j] = max(s[i - 1][j - 1] for s in scores) + substitutions[a, b]
            deletion[i][j] = max(match[i - 1][j] + gap_open,
                                 deletion[i - 1][j] + gap_extend,
                                 insertion[i - 1][j] + gap_open)
            insertion[i][j] = max(match[i][j - 1] + gap_open,
                                  deletion[i][j - 1] + gap_open,
                                  insertion[i][j - 1] + gap_extend)
    best = max(s[n][m] for s in scores)
    aligner = Align.PairwiseAligner(mode="global", substitution_matrix=matrix,
                                  open_gap_score=gap_open, extend_gap_score=gap_extend)
    if best != aligner.score(anchor, target):
        raise ValueError("optimal-path implementation disagrees with Biopython score")
    pending = [(state, n, m) for state in range(3) if scores[state][n][m] == best]
    visited, partners = set(), defaultdict(set)
    while pending:
        state, i, j = pending.pop()
        if (state, i, j) in visited or (i == 0 and j == 0):
            continue
        visited.add((state, i, j))
        if state == 0:
            partners[i].add(j)
            pi, pj = i - 1, j - 1
            penalties = [substitutions[anchor[i - 1], target[j - 1]]] * 3
        elif state == 1:
            partners[i].add(None)
            pi, pj, penalties = i - 1, j, [gap_open, gap_extend, gap_open]
        else:
            pi, pj, penalties = i, j - 1, [gap_open, gap_open, gap_extend]
        for previous, penalty in enumerate(penalties):
            if scores[previous][pi][pj] + penalty == scores[state][i][j]:
                pending.append((previous, pi, pj))
    return partners


def correspondence(anchor, target):
    """Consensus over optimal sequence alignments; unknown is a first-class result."""
    if anchor == target:
        return {p: p for p in range(1, len(anchor) + 1)}
    candidates = defaultdict(set)
    for gap_open, gap_extend in ((-10, -0.5), (-12, -1)):
        for position, partners in optimal_correspondences(anchor, target, gap_open, gap_extend).items():
            candidates[position].update(partners)
    return {p: next(iter(values)) if len(values) == 1 else None for p, values in candidates.items()}


def compare_site(site, anchor, target, mapping):
    rows = []
    for position in sorted({c["protein_position"] for c in site["contacts"]}):
        mapped = mapping.get(position)
        row = {"anchor_position": position, "anchor_residue": anchor["sequence"][position - 1],
               "status": "UNRESOLVED", "mapping_note": "Gap, alternative optimal alignment, or scoring-setting disagreement."}
        if mapped:
            aa = target["sequence"][mapped - 1]
            row.update({"target_position": mapped, "target_residue": aa,
                        "status": "IDENTICAL" if aa == row["anchor_residue"] else "CHANGED",
                        "mapping_note": "Computational consensus only; correspondence requires scientific review."})
        rows.append(row)
    accession = target["protein_id"].split(":", 1)[1]
    return {
        "assertion_id": f"slc10-comparison:{site['assertion_id'].split(':', 1)[1]}-{accession}",
        "protein_id": target["protein_id"], "sequence_sha256": target["sequence_sha256"],
        "evidence_origin": "COMPUTED_COMPARISON", "review_status": "PROPOSED",
        "site_ref": site["assertion_id"], "method": METHOD, "residues": rows,
        "evidence": [{"reference": f"https://www.uniprot.org/uniprotkb/{accession}/entry",
                      "notes": "Sequence source, not experimental evidence for the inferred site or activity."},
                     *site["evidence"]],
        "limitations": "Sequence correspondence is a derived hypothesis, not a qualified trait occurrence. "
                       "Conservation does not establish binding or transport; divergence does not establish inactivity. "
                       "No ion/ligand has been predicted or observed in this target by this comparison.",
    }


def build_structural_bundle(directory):
    directory = Path(directory)
    manifest = read_snapshot(directory)
    proteins = protein_references(directory, manifest)
    anchor = proteins[0]
    sites = [site for pdb in STRUCTURES for site in extract_sites(directory, pdb, anchor)]
    comparisons = []
    for protein in proteins:
        mapping = correspondence(anchor["sequence"], protein["sequence"])
        comparisons.extend(compare_site(site, anchor, protein, mapping) for site in sites)
    contracts = {r["local_name"].split("/")[-1]: r for r in sources()}
    artifacts = []
    for artifact in manifest["artifacts"]:
        name = artifact["path"]
        if name.endswith(".cif"):
            identity = {"artifact_kind": "EXPERIMENTAL_STRUCTURE", "structure_id": f"PDB:{name.removesuffix('.cif').upper()}"}
            block = gemmi.cif.read_file(str(directory / name)).sole_block()
            history = block.get_mmcif_category("_pdbx_audit_revision_history.")
            version = f"{history['major_revision'][-1]}.{history['minor_revision'][-1]} ({history['revision_date'][-1]})"
        elif name.endswith(".xml.gz"):
            identity = {"artifact_kind": "RESIDUE_MAPPING", "structure_id": f"PDB:{name.removesuffix('.xml.gz').upper()}"}
            version = load_sifts_xml(directory / name).entry_date
        else:
            identity = {"artifact_kind": "PROTEIN_SEQUENCE", "protein_id": f"UniProtKB:{name.removesuffix('.json')}"}
            version = manifest["uniprot_release"]
        artifacts.append({"source_id": name, **identity, "reference": artifact["requested_url"],
                          "sha256": artifact["sha256"], "source_version": version,
                          "license": contracts[name]["license"],
                          "license_url": contracts[name]["license_url"]})
    classifications = []
    for accession in PANEL:
        entry = json.loads((directory / f"{accession}.json").read_text())
        identifiers = sorted({f"{x['database']}:{x['id']}" for x in entry.get("uniProtKBCrossReferences", [])
                              if x["database"] == "Pfam" or (x["database"] == "PANTHER" and ":SF" not in x["id"])})
        classifications.append(f"{accession}: {', '.join(identifiers) or 'no selected source classification'}")
    scope = ("Seven-protein comparison panel, not a single source family. Pinned UniProt source classifications: "
             + "; ".join(classifications) + ". These source cross-references are context, not qualified PTM occurrences. "
             "Neither gene naming nor inclusion in this panel establishes equivalent sites or shared activity.")
    return {"bundle_id": "ptm-molecular:slc10", "version": "1", "scope_note": scope,
            "trait_refs": ["Pfam:PF01758", "Pfam:PF13593"], "protein_references": proteins,
            "sources": artifacts, "sites": sites, "comparisons": comparisons}
