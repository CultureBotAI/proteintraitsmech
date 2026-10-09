"""Source-reviewed reference chemistry, never an automatic mechanism predictor."""
from __future__ import annotations

from collections import Counter
import argparse
from copy import deepcopy
from datetime import date
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
import re
import sys

from linkml.validator import Validator
from linkml.validator.plugins import JsonschemaValidationPlugin
from linkml.validator.report import Severity

from biophysical import KD, POSITIVE_PKA, NEGATIVE_PKA
from fetch_amino_acid_properties import COMPONENTS, CONTRACT

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data/molecular/amino_acids/catalog.json"
SCHEMA = ROOT / "src/proteintraitsmech/schema/proteintraitsmech.yaml"
MOD_ORDER = "ARNDCEQGHILKMFPSTWYV"
IDENTITIES = {aa: (component, f"MOD:{i + 10:05d}")
              for i, (aa, component) in enumerate(zip(MOD_ORDER, COMPONENTS))}
# Source-reviewed residue (not free amino acid) cross-references in MOD:00010–29.
CHEMICAL_IDS = dict(zip("ACDEFGHIKLMNPQRSTVWY", (
    29948, 29950, 29958, 29972, 29997, 29947, 29979, 30009, 29967, 30006,
    29983, 29956, 30017, 30011, 29952, 29999, 30013, 30015, 29954, 29975)))
CATALOG_ID = "ptm-chemistry:standard-amino-acids"
VERSION = "1.0.0"
PH = 7.0
STRUCTURE_PROPERTIES = (
    "SIDE_CHAIN_HEAVY_ATOM_COUNT", "SIDE_CHAIN_AROMATIC_ATOM_COUNT",
    "SIDE_CHAIN_HETEROATOM_COUNT", "SIDE_CHAIN_HYDROXYL_COUNT", "BACKBONE_RING_CLOSURE",
)
PROPERTY_IDS = (*STRUCTURE_PROPERTIES, "KYTE_DOOLITTLE_HYDROPATHY", "SIDE_CHAIN_PKA",
                "REFERENCE_SIDE_CHAIN_CHARGE_PH7")
SCOPE = (
    "Unmodified standard peptide-residue reference chemistry only. CCD atom/bond flags are a "
    "chemical reference, not coordinates, physiological protonation, or a protein interaction. "
    "Properties do not establish binding, catalysis, trafficking, transport or variant effects. "
    "Modified, ambiguous and nonstandard residues require separate evidence; do not substitute parents."
)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)


def digest(value):
    return hashlib.sha256(value if isinstance(value, bytes) else canonical(value).encode()).hexdigest()


def content_digest(catalog):
    return digest({k: v for k, v in catalog.items() if k != "review"})


def definitions():
    rows = []
    for key, label, method, unit, limits in (
        ("SIDE_CHAIN_HEAVY_ATOM_COUNT", "Side-chain heavy-atom count",
         "Count CCD non-backbone, non-leaving atoms other than H.", "atom",
         "Atom count is not steric volume, accessibility, or measured packing."),
        ("SIDE_CHAIN_AROMATIC_ATOM_COUNT", "Side-chain aromatic-atom count",
         "Count side-chain heavy atoms with the CCD aromatic flag.", "atom",
         "Aromatic atoms do not establish a pi interaction in a protein."),
        ("SIDE_CHAIN_HETEROATOM_COUNT", "Side-chain N/O/S atom count",
         "Count side-chain heavy atoms whose element is N, O, or S.", "atom",
         "Heteroatom count is not a hydrogen-bond donor/acceptor count."),
        ("SIDE_CHAIN_HYDROXYL_COUNT", "Non-carboxyl side-chain hydroxyl count",
         "Count side-chain O bonded to H and C, excluding carboxyl O; includes phenol.", "group",
         "Reference O-H groups do not establish protonation or hydrogen bonds in a protein."),
        ("BACKBONE_RING_CLOSURE", "Side chain closes onto backbone nitrogen",
         "One if a side-chain heavy atom is directly bonded to backbone N; otherwise zero.", "1",
         "Reference connectivity does not establish a conformation or folding outcome."),
    ):
        rows.append(dict(property_id=key, label=label, method=method, unit=unit,
                         conditions="CCD reference component, unmodified standard residue.", limitations=limits))
    rows.extend([
        dict(property_id="KYTE_DOOLITTLE_HYDROPATHY", label="Kyte-Doolittle residue hydropathy",
             method="Original KYTJ820101 values transcribed from Biopython 1.85 ProtParamData.kd.",
             unit="1", conditions="Original empirical scale; not a site-specific free energy.",
             limitations="Larger is more hydrophobic on this scale; no categorical cutoff or solubility inference.",
             quality_trait_refs=["PATO:0001884"]),
        dict(property_id="SIDE_CHAIN_PKA", label="Reference side-chain pKa parameter",
             method="Bjellqvist side-chain tables as implemented in Biopython 1.85 IsoelectricPoint.",
             unit="pH", conditions="Independent-site sequence model; excludes terminal groups.",
             limitations="Not an experimentally measured pKa at a particular protein site; omits environmental shifts."),
        dict(property_id="REFERENCE_SIDE_CHAIN_CHARGE_PH7", label="Modeled side-chain charge at pH 7",
             method="Henderson-Hasselbalch: base 1/(1+10^(pH-pKa)); acid -1/(1+10^(pKa-pH)).",
             unit="e", conditions="pH 7; independent side-chain model, no terminal groups, ligands or PTMs.",
             limitations="No titratable group in this model gives zero; this is not observed site charge or assay pH.",
             quality_trait_refs=["PATO:0002193"]),
    ])
    return rows


def groups(atoms, bonds):
    """Derive small explicit chemical subgraphs, not interaction capabilities."""
    by_name = {a["atom_name"]: a for a in atoms}
    side = {name: a for name, a in by_name.items()
            if not a["backbone"] and not a["leaving"] and a["element"] != "H"}
    adjacency = {name: {} for name in by_name}
    for bond in bonds:
        a, b = bond["atom_1"], bond["atom_2"]
        adjacency[a][b] = adjacency[b][a] = bond["bond_order"]
    result, carboxyl_oxygens = [], set()

    def add(kind, names):
        result.append({"group_type": kind, "atom_names": sorted(names)})

    aromatic = [n for n, a in side.items() if a["aromatic"]]
    if aromatic:
        add("AROMATIC_ATOMS", aromatic)
    for name, atom in side.items():
        ns = adjacency[name]
        oxygen = [n for n in ns if by_name[n]["element"] == "O"]
        nitrogen = [n for n in ns if by_name[n]["element"] == "N"]
        hydrogen = [n for n in ns if by_name[n]["element"] == "H"]
        carbon = [n for n in ns if by_name[n]["element"] == "C"]
        if atom["element"] == "C":
            if len(oxygen) == 2 and sorted(ns[n] for n in oxygen) == ["DOUB", "SING"]:
                add("CARBOXYL", [name, *oxygen])
                carboxyl_oxygens.update(oxygen)
            if len(oxygen) == len(nitrogen) == 1 and ns[oxygen[0]] == "DOUB" and ns[nitrogen[0]] == "SING":
                add("CARBOXAMIDE", [name, *oxygen, *nitrogen])
            if len(nitrogen) == 3 and sorted(ns[n] for n in nitrogen) == ["DOUB", "SING", "SING"]:
                add("GUANIDINO", [name, *nitrogen])
        # An amide/guanidino NH2 is not an alkyl amino group. CCD lysine is
        # protonated (NH3), so requiring exactly two H also misses the real case.
        if (atom["element"] == "N" and len(carbon) == 1 and len(hydrogen) in {2, 3}
                and not atom["aromatic"] and not by_name[carbon[0]]["aromatic"]
                and all(order == "SING" for order in ns.values())
                and all(order == "SING" for order in adjacency[carbon[0]].values())):
            add("PRIMARY_AMINO_GROUP", [name])
        if atom["element"] == "S":
            if hydrogen:
                add("THIOL", [name])
            elif len(carbon) == 2:
                add("THIOETHER", [name])
        if "N" in ns and by_name["N"]["backbone"]:
            add("BACKBONE_RING_CLOSURE", ["N", name])
    for name, atom in side.items():
        if atom["element"] == "O" and name not in carboxyl_oxygens:
            ns = adjacency[name]
            if any(by_name[n]["element"] == "H" for n in ns) and any(by_name[n]["element"] == "C" for n in ns):
                add("HYDROXYL", [name])
    return sorted(result, key=lambda r: (r["group_type"], r["atom_names"]))


def property_values(entry, kd=KD, positive=POSITIVE_PKA, negative=NEGATIVE_PKA):
    side = [a for a in entry["atoms"] if not a["backbone"] and not a["leaving"] and a["element"] != "H"]
    gs = groups(entry["atoms"], entry["bonds"])
    counts = [len(side), sum(a["aromatic"] for a in side), sum(a["element"] != "C" for a in side),
              sum(g["group_type"] == "HYDROXYL" for g in gs),
              int(any(g["group_type"] == "BACKBONE_RING_CLOSURE" for g in gs))]
    values = [dict(property_id=key, value=value, value_status="DEFINED",
                   source_id=entry["structure_source_id"], evidence_origin="CHEMICAL_GRAPH_DERIVATION")
              for key, value in zip(STRUCTURE_PROPERTIES, counts)]
    aa = entry["one_letter"]
    pka = positive.get(aa, negative.get(aa))
    ionization = "BASE" if aa in positive else "ACID" if aa in negative else "NO_TITRATABLE_GROUP_IN_MODEL"
    charge = (1 / (1 + 10 ** (PH - pka)) if aa in positive else
              -1 / (1 + 10 ** (pka - PH)) if aa in negative else 0.0)
    values.extend([
        dict(property_id="KYTE_DOOLITTLE_HYDROPATHY", value=kd[aa], value_status="DEFINED",
             source_id="biopython:ProtParamData-1.85", evidence_origin="PUBLISHED_PARAMETER"),
        dict(property_id="SIDE_CHAIN_PKA", **({"value": pka} if pka is not None else {}),
             value_status="DEFINED" if pka is not None else "NOT_APPLICABLE",
             source_id="biopython:IsoelectricPoint-1.85", evidence_origin="PUBLISHED_PARAMETER"),
        dict(property_id="REFERENCE_SIDE_CHAIN_CHARGE_PH7", value=charge, value_status="DEFINED",
             source_id="biopython:IsoelectricPoint-1.85", evidence_origin="REFERENCE_IONIZATION_MODEL"),
    ])
    return values, gs, ionization


@lru_cache(maxsize=1)
def validator():
    return Validator(schema=str(SCHEMA), validation_plugins=[JsonschemaValidationPlugin(closed=True)])


def _unsafe_scalar(value):
    if value is None or isinstance(value, float) and not math.isfinite(value):
        return True
    if isinstance(value, dict):
        return any(_unsafe_scalar(v) for v in value.values())
    if isinstance(value, list):
        return any(_unsafe_scalar(v) for v in value)
    return False


def validate_catalog(catalog, require_review=True):
    if not isinstance(catalog, dict):
        return ["catalog must be an object"]
    if _unsafe_scalar(catalog):
        return ["catalog forbids explicit null and nonfinite values"]
    errors = [r.message for r in validator().validate(catalog, target_class="AminoAcidPropertyCatalog").results
              if r.severity == Severity.ERROR]
    if errors:
        return errors
    if (catalog["catalog_id"], catalog["version"], catalog["scope"]) != (CATALOG_ID, VERSION, SCOPE):
        errors.append("catalog identity, version or scientific scope mismatch")
    if catalog["property_definitions"] != definitions():
        errors.append("property definitions differ from the reviewed operational contract")
    sources = {r["source_id"]: r for r in catalog["sources"]}
    if len(sources) != len(catalog["sources"]) or len(sources) != len(CONTRACT):
        errors.append("catalog requires exactly 22 distinct sources")
    expected_sources = {f"ccd:{c}": f"{c}.cif" for c in COMPONENTS}
    expected_sources.update({f"biopython:{name}-1.85": f"{name}.py" for name in ("ProtParamData", "IsoelectricPoint")})
    if set(sources) != set(expected_sources):
        errors.append("catalog source identities differ from the reviewed contract")
    for sid, source in sources.items():
        if sid not in expected_sources:
            continue
        if tuple(source[k] for k in ("reference", "license", "license_url")) != CONTRACT[expected_sources[sid]]:
            errors.append(f"{sid}: source URL or license mismatch")
        if (sid.startswith("biopython:") and source["version"] != "1.85" or
                sid.startswith("ccd:") and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", source["version"])):
            errors.append(f"{sid}: source version mismatch")
        if sid.startswith("ccd:"):
            try:
                date.fromisoformat(source["version"])
            except ValueError:
                errors.append(f"{sid}: invalid source date")
        if not source["evidence"] or any(not e.get("snippet", "").strip() for e in source["evidence"]):
            errors.append(f"{sid}: source evidence requires a short checked excerpt")
        if any(e["reference"] != source["reference"] for e in source["evidence"]):
            errors.append(f"{sid}: source excerpt reference mismatch")
    entries = catalog["amino_acids"]
    if Counter(e["one_letter"] for e in entries) != Counter(IDENTITIES.keys()):
        errors.append("catalog must contain each of the 20 standard residues exactly once")
    for entry in entries:
        aa = entry["one_letter"]
        if (entry["three_letter"], entry["residue_trait_ref"]) != IDENTITIES[aa]:
            errors.append(f"{aa}: standard residue identity/trait mapping mismatch")
        if entry["residue_chemical_ref"] != f"CHEBI:{CHEMICAL_IDS[aa]}":
            errors.append(f"{aa}: residue chemical identity mismatch")
        if entry["structure_source_id"] != f"ccd:{entry['three_letter']}":
            errors.append(f"{aa}: chemical component source mismatch")
        atoms = {a["atom_name"]: a for a in entry["atoms"]}
        if len(atoms) != len(entry["atoms"]) or not {"N", "CA", "C", "O"} <= set(atoms):
            errors.append(f"{aa}: duplicate atoms or incomplete backbone")
            continue
        if any(type(a[k]) is not bool for a in atoms.values() for k in ("aromatic", "backbone", "leaving")):
            errors.append(f"{aa}: chemical flags must be booleans")
        pairs = []
        malformed = False
        for bond in entry["bonds"]:
            a, b = bond["atom_1"], bond["atom_2"]
            if a == b or a not in atoms or b not in atoms:
                errors.append(f"{aa}: invalid chemical bond endpoint")
                malformed = True
            pairs.append(tuple(sorted((a, b))))
        if len(set(pairs)) != len(pairs) or not pairs:
            errors.append(f"{aa}: duplicate or empty bond table")
            malformed = True
        if malformed:
            continue
        values, gs, ionization = property_values(entry)
        if entry.get("chemical_groups", []) != gs:
            errors.append(f"{aa}: chemical groups disagree with reference bonds")
        if entry["ionization_type"] != ionization:
            errors.append(f"{aa}: ionization classification mismatch")
        if entry["properties"] != values or any(type(p.get("value")) is bool for p in entry["properties"]):
            errors.append(f"{aa}: property values/provenance disagree with reference chemistry or parameters")
    review = catalog.get("review")
    if require_review and not review:
        errors.append("catalog requires an explicit source-transcription review")
    if review:
        try:
            date.fromisoformat(review["reviewed_on"])
        except ValueError:
            errors.append("catalog review date is invalid")
        if review["content_sha256"] != content_digest(catalog):
            errors.append("catalog review content digest mismatch")
        if not review["checks"] or not all(review[k].strip() for k in ("reviewer", "scope", "limitations")):
            errors.append("catalog review requires checks, reviewer, scope and limitations")
    return errors


def residue_chemistry(catalog, one_letter):
    """Return reference properties without silently mapping unsupported residues."""
    entry = next((e for e in catalog["amino_acids"] if e["one_letter"] == one_letter), None)
    if entry is None:
        return {"status": "UNSUPPORTED_RESIDUE", "residue": one_letter,
                "reason": "No unmodified standard-residue catalog entry; no parent substitution or imputation."}
    return {"status": "REFERENCE_CHEMISTRY", "residue": one_letter, "entry": deepcopy(entry)}


def compare_residues(catalog, reference, alternate=None):
    """Contrast catalog values, not local effects; never creates causal edges."""
    result = {"catalog_id": catalog["catalog_id"], "catalog_version": catalog["version"],
              "catalog_sha256": digest(catalog), "review": deepcopy(catalog.get("review")),
              "reference": residue_chemistry(catalog, reference), "scope": catalog["scope"],
              "property_definitions": deepcopy(catalog["property_definitions"]),
              "causal_inference": "NONE"}
    source_ids = {"biopython:ProtParamData-1.85", "biopython:IsoelectricPoint-1.85"}
    source_ids.update(f"ccd:{IDENTITIES[aa][0]}" for aa in (reference, alternate) if aa in IDENTITIES)
    result["sources"] = [deepcopy(s) for s in catalog["sources"] if s["source_id"] in source_ids]
    if alternate is None:
        return result
    result["alternate"] = residue_chemistry(catalog, alternate)
    if any(result[side]["status"] != "REFERENCE_CHEMISTRY" for side in ("reference", "alternate")):
        result["comparison_status"] = "UNSUPPORTED_RESIDUE"
        return result
    props = [{p["property_id"]: p for p in result[side]["entry"]["properties"]}
             for side in ("reference", "alternate")]
    differences = []
    for key in PROPERTY_IDS:
        before, after = props[0][key], props[1][key]
        row = {"property_id": key, "reference": deepcopy(before), "alternate": deepcopy(after)}
        if before["value_status"] == after["value_status"] == "DEFINED":
            row["delta_alternate_minus_reference"] = after["value"] - before["value"]
        differences.append(row)
    result.update(comparison_status="REFERENCE_PROPERTY_CONTRAST", differences=differences)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("catalog", type=Path, nargs="?", default=CATALOG)
    args = parser.parse_args(argv)
    try:
        catalog = json.loads(args.catalog.read_text())
        errors = validate_catalog(catalog)
        if errors:
            raise ValueError("; ".join(errors))
        print(json.dumps({"catalog_id": catalog["catalog_id"], "catalog_sha256": digest(catalog),
                          "residue_count": len(catalog["amino_acids"]), "source_count": len(catalog["sources"]),
                          "review": catalog["review"]["reviewer"], "status": "VALID_REFERENCE_CHEMISTRY"}))
    except (ValueError, OSError) as exc:
        print(f"invalid amino-acid catalog: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
