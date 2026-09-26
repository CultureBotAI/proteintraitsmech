#!/usr/bin/env python3
"""Reproduce a bounded, source-backed experimental stability/solubility slice.

Only explicitly identified wild-type constructs are mapped to pinned reference
regions. Values are extracted from retained source XML, with reporting gaps and
secondary-source chains preserved. No whole-protein map overlay is generated.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import io
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

from biophysical import canonical_json, descriptor_id, observation_id, sha256
from calculate_biophysical import atomic_write, digest
from validate_biophysical import load_catalog, schema_errors, validate_collection

ROOT = Path(__file__).resolve().parents[1]
CRESPO = "https://doi.org/10.1371/journal.pone.0019425"
FORSYTHE = "https://doi.org/10.1021/je980316a"
COMPILATION = "https://doi.org/10.1021/cg501359h"
ARTICLE_HASHES = {"crespo2011.xml": "f9caf45151beeb297ebf16e1f477324867effefafeeb316242ac02f8f457c980",
                  "crystallization2015.xml": "809e72679623351ad19de0deede6a697b1c3c3e884c57745f7ef96f4be97f5ab"}


def text(element):
    return " ".join("".join(element.itertext()).split())


def number(value):
    return float(value.replace("−", "-"))


def source_tables(folder):
    trees = {}
    for filename, expected in ARTICLE_HASHES.items():
        if digest(folder / "sources" / filename) != expected:
            raise ValueError(f"experimental source differs from its reviewed snapshot: {filename}")
        trees[filename] = ET.parse(folder / "sources" / filename).getroot()
    return trees


def references(folder):
    source = folder / "sources/P00698.json"
    receipt = json.loads(source.with_suffix(".json.fetch.json").read_text())
    release = receipt.get("uniprot_release", "")
    if (not re.fullmatch(r"[0-9]{4}_[0-9]{2}", release) or receipt["sha256"] != digest(source)
            or receipt["requested_url"] != "https://rest.uniprot.org/uniprotkb/stream?query=accession%3AP00698&format=json"):
        raise ValueError("lysozyme reference requires a matching official response and captured UniProt release")
    entries = json.loads(source.read_text())["results"]
    if len(entries) != 1 or entries[0]["primaryAccession"] != "P00698":
        raise ValueError("expected exactly the requested lysozyme accession")
    entry = entries[0]
    sequence = entry["sequence"]["value"]
    lysozyme = {"protein_id": "UniProtKB:P00698",
                "protein_label": entry["proteinDescription"]["recommendedName"]["fullName"]["value"],
                "sequence": sequence, "sequence_sha256": sha256(sequence),
                "sequence_length": entry["sequence"]["length"], "sequence_version": entry["entryAudit"]["sequenceVersion"],
                "uniprot_release": release, "reviewed": entry["entryType"] == "UniProtKB reviewed (Swiss-Prot)",
                "taxon_id": "NCBITaxon:" + str(entry["organism"]["taxonId"]),
                "taxon_label": entry["organism"]["scientificName"]}
    chains = [f for f in entry["features"] if f["type"] == "Chain" and f["description"] == "Lysozyme C"]
    if len(chains) != 1 or (chains[0]["location"]["start"]["value"], chains[0]["location"]["end"]["value"]) != (19, 147):
        raise ValueError("reviewed lysozyme mature-chain annotation differs")
    ubiquitin = json.loads((folder / "sources/P0CG47.registry.json").read_text())
    expected_ub = "MQIFVKTLTGKTITLEVEPSDTIENVKAKIQDKEGIPPDQQRLIFAGKQLEDGRTLSDYNIQKESTLHLVLRLRGG"
    if ubiquitin["protein_id"] != "UniProtKB:P0CG47" or ubiquitin["sequence"][:76] != expected_ub:
        raise ValueError("the reviewed human ubiquitin reference region differs")
    registry = {p["protein_id"]: p for p in (lysozyme, ubiquitin)}
    for protein in registry.values():
        errors = schema_errors(protein, "ProteinReference")
        if errors or protein["sequence_sha256"] != sha256(protein["sequence"]) or protein["sequence_length"] != len(protein["sequence"]):
            raise ValueError(f"invalid experimental protein reference: {errors}")
    return registry


def extract_observations(folder, registry):
    trees = source_tables(folder)
    ub = registry["UniProtKB:P0CG47"]
    lys = registry["UniProtKB:P00698"]
    observations = []

    def add(code, protein, region, value, conditions, assay, source, locator, params=None,
            normalization=None, uncertainty=None):
        is_ub = protein["protein_id"] == ub["protein_id"]
        parameters = {
            "sample_identity": "wt-ub; recombinant human ubiquitin" if is_ub else "wild-type hen egg-white lysozyme",
            "sequence_identity_basis": (
                "Study identifies 76-residue wild-type human ubiquitin and intact mass 8564.0 Da; mapped to P0CG47 1..76 as a reference frame, not a genomic-origin assertion."
                if is_ub else "Study-named native hen egg-white material mapped to the reviewed P00698 mature chain 19..147; lot-specific sequence/PTMs were not determined here."),
            "source_locator": locator, "assay": assay,
            "unreported_conditions": "See assay-specific reporting gaps below; no unstated conditions are imputed.",
            "uncertainty_status": "Not reported for this extracted value" if uncertainty is None else "Source-estimated error; not identified as SD or SE",
            **(params or {}),
        }
        reference = CRESPO if is_ub else FORSYTHE
        sequence = protein["sequence"][region[0] - 1:region[1]]
        observation = {
            **{k: protein[k] for k in ("protein_id", "sequence_sha256", "sequence_length", "sequence_version", "uniprot_release")},
            "descriptor_id": descriptor_id(code), "scope": "REGION",
            "region": {"start": region[0], "end": region[1], "expected_sequence": sequence},
            "analyzed_sequence_sha256": sha256(sequence),
            "proteoform": "Untagged wild-type human ubiquitin, free 76-residue chain" if is_ub else
                          "Native mature hen egg-white lysozyme; study-named material, lot-specific PTMs uncharacterized",
            "evidence_mode": "EXPERIMENT", "status": "OK", "value": value,
            "unit": {"B25": "degC", "B26": "kJ/mol", "B27": "mol/L", "B30": "g/L"}[code],
            "conditions": conditions,
            "method": {"name": assay, "version": "source publication 2011" if is_ub else "source publication 1999; reproduced 2015",
                       "reference": reference, "implementation": "scripts/import_biophysical_experiments.py",
                       "implementation_sha256": digest(Path(__file__)),
                       "source_artifact_sha256": digest(folder / "sources" / source),
                       "parameters": [{"name": key, "value": str(val)} for key, val in sorted(parameters.items())]},
            "evidence": [{"reference": reference, "notes": locator}],
        }
        if not is_ub:
            observation["evidence"].append({"reference": COMPILATION,
                "notes": "Values transcribed from Table 1's Forsythe rows, not remeasured by this 2015 study. Original method verified against the authors' NASA abstract https://ntrs.nasa.gov/citations/19990069901 ."})
        if normalization:
            observation["normalization"] = normalization
        if uncertainty:
            observation["uncertainty"] = uncertainty
        observation["observation_id"] = observation_id(observation)
        observations.append(observation)

    crespo = trees["crespo2011.xml"]
    table1 = crespo.find(".//table-wrap[@id='pone-0019425-t001']")
    for row in table1.findall(".//tbody/tr"):
        cells = [text(cell) for cell in row.findall("td")]
        ph, tm = number(cells[0]), number(cells[1])  # Explicitly the wt-ub column.
        add("B25", ub, (1, 76), tm, {"ph": ph, "concentration_molar": 15e-6},
            "Thermal unfolding monitored by circular dichroism", "crespo2011.xml",
            f"Table 1, wt-ub Tm column, pH {ph}; CD Spectroscopy and fluorescence measurements",
            {"wavelength_nm": "200", "temperature_ramp_celsius_per_hour": "60",
             "transition_criterion": "zero crossing of second derivative of the thermal melting curve",
             "unreported_conditions": "Buffer composition, ionic strength and scan reversibility for Table 1 not specified; no equilibrium reversibility claim."},
            uncertainty={"kind": "estimated error", "value": 0.1,
                         "description": "Table 1 states an estimated Tm error of plus/minus 0.1 degrees C; not identified as SD or SE."})
    table2 = crespo.find(".//table-wrap[@id='pone-0019425-t002']")
    wt = next(row for row in table2.findall(".//tbody/tr") if text(row.find("td")) == "wt-ub")
    source_dg = number(text(wt.findall("td")[11]))
    add("B26", ub, (1, 76), -source_dg, {"ph": 2.0, "temperature_celsius": 25.0, "buffer": "10 mM glycine/HCl"},
        "Global equilibrium fluorescence and stopped-flow fit", "crespo2011.xml", "Table 2, wt-ub DeltaG_un column and footnotes",
        {"source_value_kj_per_mol": str(source_dg),
         "source_sign_convention": "-RT ln(K_ui * (k_in/k_ni)) = G(native)-G(unfolded)",
         "sign_conversion": "multiply source value by -1",
         "reference_state": "zero guanidinium chloride concentration; extrapolated from the fitted denaturant series",
         "equilibrium_model": "sequential three-state on-pathway U-I-N, global fit",
         "unreported_conditions": "Ionic strength, pressure and uncertainty of the Table 2 free-energy estimate not reported; equilibrium and kinetic assays used different protein concentrations."},
        normalization="G(unfolded)-G(native)")
    paragraphs = " ".join(text(p) for p in crespo.findall(".//p"))
    patterns = [(2.0, r"transition mid-point for wt-ub was found to be at ([0-9.]+) M GdmCl", "tyrosine fluorescence"),
                (5.0, r"transition mid-point for the wt was found to be at ([0-9.]+) M", "circular dichroism")]
    for ph, pattern, assay in patterns:
        matches = re.findall(pattern, paragraphs)
        if len(matches) != 1:
            raise ValueError("chemical-denaturation midpoint source locator is ambiguous")
        add("B27", ub, (1, 76), float(matches[0]), {"ph": ph, "temperature_celsius": 25.0},
            "Equilibrium chemical denaturation monitored by " + assay, "crespo2011.xml",
            f"Results: Effect of (2S,4R)-4-fluoroproline on equilibrium stability, wt-ub at pH {ph}",
            {"denaturant": "guanidinium chloride", "transition_criterion": "source-reported equilibrium unfolding midpoint",
             "equilibration_hours": "2", "unreported_conditions": "Midpoint uncertainty and complete solution composition not given for these values; no concentration or buffer default inferred."})
    table = trees["crystallization2015.xml"].find(".//table-wrap[@id='tbl1']")
    solubility_rows = 0
    for row in table.findall(".//tbody/tr"):
        cells = [text(cell) for cell in row.findall("td")]
        if not cells[5].startswith("Forsythe 1999"):
            continue
        ph, salt, temperature, buffer, solubility = map(number, cells[:5])
        add("B30", lys, (19, 147), solubility,
            {"ph": ph, "temperature_celsius": temperature, "buffer": f"{buffer:g} M sodium acetate", "solvent": "water"},
            "Miniature-column equilibrium solubility measurement", "crystallization2015.xml",
            f"Table 1, Forsythe 1999 row at {temperature:g} degrees C; original study DOI 10.1021/je980316a",
            {"solid_phase": "tetragonal hen egg-white lysozyme crystals",
             "equilibrium_basis": "source-reported solubility using a miniature column apparatus; not transient reactor concentration",
             "salt_composition": f"NaCl {salt:g}% w/v ({salt * 10:g} g/L)",
             "unreported_conditions": "Value-specific uncertainty, sample lot and equilibration time not supplied in the retained table. Total ionic strength is not inferred from salt concentration alone."},
            normalization="mass concentration of dissolved protein")
        solubility_rows += 1
    if len(observations) != 14 or solubility_rows != 3:
        raise ValueError("reviewed experimental extraction cardinality changed")
    return observations


def experimental_tsv(observations):
    output = io.StringIO()
    fields = ["observation_id", "protein_id", "descriptor_id", "region_start", "region_end",
              "value", "unit", "ph", "temperature_celsius", "buffer", "assay", "source_locator",
              "uncertainty", "reporting_gaps", "evidence", "proteoform", "normalization",
              "conditions", "method_parameters"]
    writer = csv.DictWriter(output, fieldnames=fields, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    for observation in observations:
        params = {p["name"]: p["value"] for p in observation["method"]["parameters"]}
        row = {k: observation[k] for k in ("observation_id", "protein_id", "descriptor_id", "value", "unit")}
        row.update({"region_start": observation["region"]["start"], "region_end": observation["region"]["end"],
                    **{k: observation["conditions"].get(k, "not reported") for k in ("ph", "temperature_celsius", "buffer")},
                    "assay": params["assay"], "source_locator": params["source_locator"],
                    "uncertainty": canonical_json(observation["uncertainty"]) if "uncertainty" in observation else "not reported",
                    "reporting_gaps": params["unreported_conditions"],
                    "evidence": " | ".join(e["reference"] for e in observation["evidence"]),
                    "proteoform": observation["proteoform"], "normalization": observation.get("normalization", ""),
                    "conditions": canonical_json(observation["conditions"]),
                    "method_parameters": canonical_json(params)})
        writer.writerow(row)
    return output.getvalue()


def artifacts(root=ROOT):
    folder = root / "data/biophysical/experimental"
    registry = references(folder)
    observations = extract_observations(folder, registry)
    errors = validate_collection(observations, registry, load_catalog(folder / "descriptors.yaml"))
    if errors:
        raise ValueError("\n".join(errors))
    contents = "".join(canonical_json(o) + "\n" for o in observations)
    manifest = {"observation_count": len(observations),
                "descriptors": dict(Counter(o["descriptor_id"] for o in observations)),
                "observation_file_sha256": sha256(contents),
                "source_sha256": {str(p.relative_to(folder)): digest(p) for p in sorted((folder / "sources").iterdir()) if p.is_file()},
                "catalog_sha256": digest(folder / "descriptors.yaml"),
                "importer_sha256": digest(Path(__file__)),
                "sequence_attribution": "UniProt Consortium, CC BY 4.0; references preserve source release and sequence versions",
                "ubiquitin_reference_origin": "https://github.com/CultureBotAI/proteintraitsmech/blob/5bf6e9fcb8aea9db21250133a39b7d1a760692db/data/grounding/protein_registry.jsonl",
                "interpretation": "Two study-named wild-type constructs mapped to exact reference regions by explicit curation. No lot-specific sequence verification, new canonical qualification or whole-protein property assignment."}
    return {folder / "protein_registry.jsonl": "".join(canonical_json(registry[k]) + "\n" for k in sorted(registry)),
            folder / "observations.jsonl": contents,
            folder / "observations.tsv": experimental_tsv(observations),
            folder / "manifest.json": json.dumps(manifest, indent=2, sort_keys=True) + "\n"}


def check_experiments(root=ROOT):
    return [f"experimental artifact differs from its sources: {path.name}"
            for path, expected in artifacts(root).items() if path.read_text() != expected]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.check:
            errors = check_experiments(args.root)
            if errors:
                raise ValueError("\n".join(errors))
            print("Experimental biophysics verified against retained sources and explicit measurement contracts.")
        else:
            output = artifacts(args.root)
            if args.apply:
                for path, value in output.items():
                    atomic_write(path, value)
            print(f"{'Wrote' if args.apply else 'Would write'} 14 experimental observations across B25/B26/B27/B30.")
    except (OSError, ValueError, KeyError, TypeError, StopIteration, ET.ParseError) as exc:
        print(f"experimental import failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
