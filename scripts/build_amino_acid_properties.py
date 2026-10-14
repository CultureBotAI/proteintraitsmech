#!/usr/bin/env python3
"""Replay pinned source files into the amino-acid catalog; dry-run by default."""
from __future__ import annotations

import argparse
import ast
import io
import json
from pathlib import Path
import sys
import tempfile

from Bio.PDB.MMCIF2Dict import MMCIF2Dict
import yaml

import amino_acid_properties as chemistry
from fetch_amino_acid_properties import CONTRACT

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = chemistry.CATALOG


def literal_table(raw, variable):
    """Parse a literal assignment, never import/execute downloaded Python."""
    matches = [n.value for n in ast.parse(raw.decode()).body
               if isinstance(n, ast.Assign) and len(n.targets) == 1
               and isinstance(n.targets[0], ast.Name) and n.targets[0].id == variable]
    if len(matches) != 1:
        raise ValueError(f"expected exactly one literal table: {variable}")
    table = ast.literal_eval(matches[0])
    if not isinstance(table, dict) or any(type(v) not in (int, float) for v in table.values()):
        raise ValueError(f"invalid numerical parameter table: {variable}")
    return table


def snapshot_inputs(snapshot):
    if snapshot.is_symlink() or (snapshot / "manifest.json").is_symlink():
        raise ValueError("refusing symlinked chemistry snapshot")
    manifest = json.loads((snapshot / "manifest.json").read_text())
    if manifest.get("kind") != "AMINO_ACID_PROPERTY_SNAPSHOT" or manifest.get("schema_version") != 1:
        raise ValueError("wrong chemistry snapshot manifest kind/version")
    rows = manifest.get("artifacts", [])
    receipts = {r["path"]: r for r in rows}
    if len(receipts) != len(rows) or set(receipts) != set(CONTRACT):
        raise ValueError("snapshot must cover each of the 22 sources exactly once")
    inputs = {}
    for name, receipt in receipts.items():
        if tuple(receipt.get(k) for k in ("requested_url", "license", "license_url")) != CONTRACT[name]:
            raise ValueError(f"snapshot source contract mismatch: {name}")
        if (snapshot / name).is_symlink():
            raise ValueError(f"refusing symlinked chemistry input: {name}")
        raw = (snapshot / name).read_bytes()
        if chemistry.digest(raw) != receipt["sha256"] or len(raw) != receipt["bytes"]:
            raise ValueError(f"snapshot checksum/size mismatch: {name}")
        inputs[name] = raw
    return inputs, receipts


def source_record(sid, name, receipt, version, snippet):
    url, license_name, license_url = CONTRACT[name]
    return dict(source_id=sid, reference=url, sha256=receipt["sha256"], version=version,
                license=license_name, license_url=license_url,
                evidence=[dict(reference=url, snippet=snippet,
                               notes="Checked source identity; atom/bond rows or the named literal parameter table support the projection.")])


def component(raw, aa, code, trait_id):
    cif = MMCIF2Dict(io.StringIO(raw.decode()))
    if (cif.get("_chem_comp.id"), cif.get("_chem_comp.one_letter_code")) != ([code], [aa]):
        raise ValueError(f"CCD identity mismatch: {code}/{aa}")
    if cif.get("_chem_comp.type", [""])[0].upper() not in {"L-PEPTIDE LINKING", "PEPTIDE LINKING"}:
        raise ValueError(f"not a standard peptide component: {code}")
    atom_fields = ("atom_id", "type_symbol", "pdbx_aromatic_flag", "pdbx_backbone_atom_flag", "pdbx_leaving_atom_flag")
    columns = [cif[f"_chem_comp_atom.{f}"] for f in atom_fields]
    if len({len(c) for c in columns}) != 1:
        raise ValueError("CCD atom columns differ in length")
    atoms = []
    for name, element, aromatic, backbone, leaving in zip(*columns):
        if any(v not in {"Y", "N"} for v in (aromatic, backbone, leaving)):
            raise ValueError("CCD flags must explicitly be Y or N")
        atoms.append(dict(atom_name=name, element=element, aromatic=aromatic == "Y",
                          backbone=backbone == "Y", leaving=leaving == "Y"))
    bond_columns = [cif[f"_chem_comp_bond.{f}"] for f in ("atom_id_1", "atom_id_2", "value_order")]
    if len({len(c) for c in bond_columns}) != 1:
        raise ValueError("CCD bond columns differ in length")
    bonds = [dict(atom_1=a, atom_2=b, bond_order=order) for a, b, order in zip(*bond_columns)]
    paths = list((ROOT / "data/traits/sequence/ptm_ontology").glob(f"*-mod{trait_id.split(':')[1]}.yaml"))
    if len(paths) != 1:
        raise ValueError(f"residue trait must resolve uniquely: {trait_id}")
    trait_raw = paths[0].read_bytes()
    record = yaml.safe_load(trait_raw)
    if record["identifier"] != trait_id:
        raise ValueError("residue trait file identifier mismatch")
    chemical_ids = [xref.replace("ChEBI:", "CHEBI:") for xref in record.get("xrefs", [])
                    if xref.lower().startswith("chebi:")]
    if len(chemical_ids) != 1:
        raise ValueError(f"expected one explicit residue ChEBI cross-reference: {trait_id}")
    entry = dict(one_letter=aa, three_letter=code, label=record["label"], residue_trait_ref=trait_id,
                 residue_chemical_ref=chemical_ids[0], trait_record_sha256=chemistry.digest(trait_raw),
                 structure_source_id=f"ccd:{code}", atoms=sorted(atoms, key=lambda a: a["atom_name"]),
                 bonds=sorted(bonds, key=lambda b: (b["atom_1"], b["atom_2"])))
    return entry, cif["_chem_comp.pdbx_modified_date"][0], cif["_chem_comp.name"][0]


def build(snapshot, review_path=None):
    inputs, receipts = snapshot_inputs(snapshot)
    kd = literal_table(inputs["ProtParamData.py"], "kd")
    pos = {k: v for k, v in literal_table(inputs["IsoelectricPoint.py"], "positive_pKs").items() if k != "Nterm"}
    neg = {k: v for k, v in literal_table(inputs["IsoelectricPoint.py"], "negative_pKs").items() if k != "Cterm"}
    if (kd, pos, neg) != (chemistry.KD, chemistry.POSITIVE_PKA, chemistry.NEGATIVE_PKA):
        raise ValueError("upstream parameters disagree with the existing versioned biophysical implementation")
    catalog = dict(catalog_id=chemistry.CATALOG_ID, version=chemistry.VERSION, scope=chemistry.SCOPE,
                   sources=[], property_definitions=chemistry.definitions(), amino_acids=[])
    for aa, (code, trait_id) in sorted(chemistry.IDENTITIES.items()):
        name = f"{code}.cif"
        entry, version, label = component(inputs[name], aa, code, trait_id)
        values, chemical_groups, ionization_type = chemistry.property_values(entry, kd, pos, neg)
        entry.update(properties=values, chemical_groups=chemical_groups, ionization_type=ionization_type)
        catalog["amino_acids"].append(entry)
        catalog["sources"].append(source_record(f"ccd:{code}", name, receipts[name], version, label))
    for name, excerpt in (("ProtParamData", "Kyte & Doolittle index of hydrophobicity"),
                          ("IsoelectricPoint", "Calculate isoelectric points of polypeptides using methods of Bjellqvist.")):
        filename = f"{name}.py"
        if excerpt not in inputs[filename].decode():
            raise ValueError(f"reviewed excerpt no longer matches: {filename}")
        catalog["sources"].append(source_record(f"biopython:{name}-1.85", filename, receipts[filename], "1.85", excerpt))
    catalog["sources"].sort(key=lambda s: s["source_id"])
    if review_path:
        catalog["review"] = yaml.safe_load(review_path.read_text())
    errors = chemistry.validate_catalog(catalog, require_review=review_path is not None)
    if errors:
        raise ValueError("; ".join(errors))
    return catalog


def write_catalog(catalog):
    errors = chemistry.validate_catalog(catalog)
    if errors:
        raise ValueError("; ".join(errors))
    if any(p.is_symlink() for p in (OUTPUT, OUTPUT.parent, OUTPUT.parent.parent, OUTPUT.parent.parent.parent)):
        raise ValueError("refusing symlinked chemistry output")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=OUTPUT.parent,
                                         prefix=".catalog-", suffix=".json", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(json.dumps(catalog, indent=2, sort_keys=True) + "\n")
        temporary.replace(OUTPUT)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--review", type=Path)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        if (args.apply or args.check) and not args.review:
            raise ValueError("publication/check requires an explicit reviewed-content file")
        catalog = build(args.snapshot, args.review)
        if args.check and OUTPUT.read_text() != json.dumps(catalog, indent=2, sort_keys=True) + "\n":
            raise ValueError("published catalog differs from exact source replay")
        if args.apply:
            write_catalog(catalog)
        print(json.dumps({"catalog_id": catalog["catalog_id"], "version": catalog["version"],
                          "content_sha256": chemistry.content_digest(catalog),
                          "reviewed": "review" in catalog, "mode": "apply" if args.apply else "check" if args.check else "dry-run",
                          "amino_acids": [{"code": e["one_letter"], "trait": e["residue_trait_ref"],
                                           "chemical": e["residue_chemical_ref"], "groups": e["chemical_groups"],
                                           "properties": {p["property_id"]: p.get("value", p["value_status"]) for p in e["properties"]}}
                                          for e in catalog["amino_acids"]]}, indent=2, sort_keys=True))
    except (OSError, ValueError, KeyError) as exc:
        print(f"amino-acid catalog build failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
