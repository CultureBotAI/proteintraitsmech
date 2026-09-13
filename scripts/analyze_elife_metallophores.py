#!/usr/bin/env python3
"""Reproduce publication-table statistics and the source protein-association ledger."""

from __future__ import annotations

import argparse
import csv
import io
import json
import posixpath
import re
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET

from elife_metallophores import (
    DOMAIN_MODELS, RAW, ROOT, catalog, read_jsonl, sha256, source_facts, verified_archive,
)

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def workbook(path: Path) -> dict[str, list[dict[str, object]]]:
    """Read cached XLSX cell values with stdlib XML; do not evaluate formulas/macros."""
    result = {}
    with zipfile.ZipFile(path) as archive:
        strings = []
        if "xl/sharedStrings.xml" in archive.namelist():
            for elem in ET.fromstring(archive.read("xl/sharedStrings.xml")):
                strings.append("".join(t.text or "" for t in elem.findall(".//m:t", NS)))
        rels = {r.attrib["Id"]: r.attrib["Target"] for r in
                ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))}
        root = ET.fromstring(archive.read("xl/workbook.xml"))
        for sheet in root.findall("m:sheets/m:sheet", NS):
            rid = sheet.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
            target = rels[rid]
            member = target.lstrip("/") if target.startswith("/") else posixpath.normpath(
                posixpath.join("xl", target))
            rows = []
            with archive.open(member) as handle:
                for _, row in ET.iterparse(handle, events=("end",)):
                    if row.tag != "{" + NS["m"] + "}row":
                        continue
                    values = {}
                    for cell in row.findall("m:c", NS):
                        column = re.match(r"[A-Z]+", cell.attrib["r"])[0]
                        value = cell.findtext("m:v", default="", namespaces=NS)
                        kind = cell.get("t")
                        if kind == "s" and value:
                            value = strings[int(value)]
                        elif kind == "b":
                            value = value == "1"
                        elif kind == "inlineStr":
                            value = "".join(t.text or "" for t in cell.findall(".//m:t", NS))
                        elif value and kind in {None, "n"}:
                            value = float(value) if any(c in value.lower() for c in (".", "e")) else int(value)
                        values[column] = value
                    rows.append(values)
                    row.clear()
            result[sheet.attrib["name"]] = rows
    return result


def confusion(rows: list[dict], prediction: str) -> dict:
    matrix = Counter((r["S"], r[prediction]) for r in rows)
    tp, fp, fn, tn = (matrix[True, True], matrix[False, True],
                      matrix[True, False], matrix[False, False])
    return {"TP": tp, "FP": fp, "FN": fn, "TN": tn,
            "precision": tp / (tp + fp), "recall": tp / (tp + fn),
            "F1": 2 * tp / (2 * tp + fp + fn)}


def analyze() -> tuple[dict, str]:
    with verified_archive() as archive:
        models, facts = source_facts(archive)
        archive_entries = len(archive.namelist())
        gtdb_path = ("nrp-metallophore-SI-main/7_gtdb_reps_statistics/"
                     "All_genomes_AS7_parsed_products_with_taxonomy.csv")
        gtdb = list(csv.DictReader(io.StringIO(archive.read(gtdb_path).decode())))
    bacteria = [r for r in gtdb if "d__Bacteria" in r["gtdb_taxonomy"]]
    producers = [r for r in bacteria if "NRP-metallophore" in r["Parsed_Products"]]
    phyla = Counter(next(t.strip().removeprefix("p__") for t in r["gtdb_taxonomy"].split(";")
                         if t.strip().startswith("p__")) for r in producers)
    sheets = workbook(RAW / "elife-109154-supp1-v2.xlsx")
    references = [r for r in sheets["1a - BGCs"][1:] if r.get("B")]
    manual = [r for r in sheets["1b - Manual curation"][3:] if r.get("B")]
    refseq = [r for r in sheets["1c - Refseq Reps Jun25"][1:] if r.get("A")]
    summary = {
        "publication": "10.7554/eLife.109154.3", "dataset": "10.5281/zenodo.18866949",
        "supplement_sha256": sha256((RAW / "elife-109154-supp1-v2.xlsx").read_bytes()),
        "archive_entries": archive_entries, "positive_traits": len(catalog()["traits"]),
        "gtdb": {"source_member": gtdb_path, "export_rows": len(gtdb),
                 "unique_accessions": len({r["accession"] for r in gtdb}),
                 "bacterial_genomes": len(bacteria),
                 "bacterial_genomes_with_nrp_metallophore": len(producers),
                 "positive_genome_fraction": len(producers) / len(bacteria),
                 "positive_genomes_by_phylum": dict(phyla)},
        "domain_models": sorted(DOMAIN_MODELS),
        "source_associations": dict(Counter(r["source_kind"] for r in facts)),
        "missing_positive_models": [k for k in catalog()["traits"] if not models[k]["hmm_available"]],
        "missing_seed_alignments": sorted(set(catalog()["traits"]) -
                                          {r["model"] for r in facts if r["source_kind"] == "seed_alignment"}),
        "reference_bgcs": len(references),
        "reference_false_positives": [r["B"] for r in references if "*" in str(r["B"])],
        "manual_validation": {"regions": len(manual),
                              "initial_positive": sum(r["I"] is True for r in manual),
                              "corrected_positive": sum(r["S"] is True for r in manual),
                              "antiSMASH": confusion(manual, "N"),
                              "transporters": confusion(manual, "X"),
                              "ensemble": confusion(manual, "AC")},
        "refseq": {"table_rows": len(refseq), "nrps_regions": sum(r["D"] is True for r in refseq),
                   "nrp_metallophore_regions": sum(r["E"] is True for r in refseq),
                   "complete_nrp_metallophore_regions": sum(r["E"] is True and r["I"] is False
                                                             for r in refseq),
                   "complete_nrps_metallophore_regions": sum(r["D"] is True and r["E"] is True
                                                              and r["I"] is False for r in refseq)},
    }
    assertions = ROOT / "data/grounding/elife109154_source_assertions.jsonl"
    qualified = {r["source_fact"]["candidate_id"]: r for r in read_jsonl(assertions)} if assertions.exists() else {}
    output = io.StringIO()
    writer = csv.writer(output, delimiter="\t", lineterminator="\n")
    writer.writerow(["trait_id", "source_kind", "source_namespace", "source_accession",
                     "source_header", "source_member", "source_sequence_length",
                     "source_sequence_sha256", "canonical_uniprot_id", "status"])
    for fact in facts:
        qualified_row = qualified.get(fact["candidate_id"])
        status = "QUALIFIED" if qualified_row else (
            "DOMAIN_COORDINATES_UNRESOLVED" if fact["model"] in DOMAIN_MODELS else "SOURCE_ASSOCIATION_ONLY")
        seq = fact.get("full_sequence", fact["source_sequence"])
        writer.writerow([fact["trait_id"], fact["source_kind"], fact.get("source_namespace", ""),
                         fact.get("source_accession", ""), fact["source_header"], fact["alignment_path"],
                         len(seq), sha256(seq.encode()),
                         qualified_row["protein_reference"]["protein_id"] if qualified_row else "", status])
    summary["canonical_examples"] = len(qualified)
    summary["traits_with_canonical_examples"] = len({r["source_fact"]["model"] for r in qualified.values()})
    return summary, output.getvalue()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    summary, ledger = analyze()
    content = json.dumps(summary, indent=2, sort_keys=True) + "\n"
    if args.apply:
        destination = ROOT / "data/curation"
        (destination / "elife109154_source_summary.json").write_text(content)
        (destination / "elife109154_protein_associations.tsv").write_text(ledger)
    print(content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
