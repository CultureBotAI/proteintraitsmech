"""Source-native facts for the immutable eLife 109154 / Zenodo 18866949 deposit.

Membership in a published seed alignment is sequence classification evidence,
not experimental enzyme activity. No alignment or HMM search is performed here.
"""

from __future__ import annotations

import hashlib
import io
import json
import re
import tarfile
import zipfile
from collections import OrderedDict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/elife_metallophores"
CATALOG = ROOT / "data/curation/elife109154_traits.yaml"
PREFIX = "proteintraitsmech:ELIFE109154_"
RELEASE = "Zenodo:18866949"
SOURCE = "eLife 109154 metallophore protein annotations"
ARCHIVE_URL = "https://zenodo.org/api/records/18866949/files/nrp-metallophore-SI.zip/content"
ARCHIVE_SHA256 = "638f968c12034b197ddf2b66c7450b3c76bb993faf7cf118d5972ee38228c8cc"
ARCHIVE_MD5 = "301af6363922095f6a70dd9408378d0a"
BASE = "nrp-metallophore-SI-main/1_rule_development/"
ASSERTIONS_PATH = "data/grounding/elife109154_source_assertions.jsonl"
ALIGNMENT_ALIASES = {"CyanoBH_Asp1": "CyanoBH_Asp", "VibH_like": "vibH"}
DOMAIN_MODELS = {"Cy_tandem", "IBH_Asp", "CyanoBH_Asp1", "CyanoBH_Asp2"}
BETA_MODELS = {"IBH_Asp", "IBH_His", "TBH_Asp", "CyanoBH_Asp1", "CyanoBH_Asp2"}
POSITIVE_CUTOFFS = {
    "Cy_tandem": 350, "EntA": 205, "EntC": 300, "FbnL": 40, "FbnM": 180,
    "GrbD": 400, "GrbE": 250, "IBH_Asp": 440, "IBH_His": 470, "TBH_Asp": 420,
    "CyanoBH_Asp1": 400, "CyanoBH_Asp2": 450, "IPL": 110, "Lys_monoox": 300,
    "Orn_monoox": 415, "PvdO": 250, "PvdP": 600, "SalSyn": 350, "VbsL": 570,
    "VibH_like": 400,
}
# Supplementary file 1a explicitly marks these reference clusters as false positives.
EXCLUDED_REFERENCE_BGCS = {"BGC0001117", "BGC0000378", "BGC0001312"}
UNIPROT = r"(?:[OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9](?:[A-Z][A-Z0-9]{2}[0-9]){1,2})"


def digest(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=True, allow_nan=False).encode()).hexdigest()


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def catalog() -> dict:
    return yaml.safe_load(CATALOG.read_text())


def parse_alignment(text: str) -> dict[str, str]:
    """Read source FASTA, CLUSTAL or Stockholm, retaining row identifiers.

    Identical repeated CLUSTAL rows within a block (Lys_monoox) are collapsed;
    conflicting repeats are refused. Lowercase inserts are amino acids, not gaps.
    """
    rows: dict[str, str] = OrderedDict()
    fasta = text.lstrip().startswith(">")
    if fasta:
        for entry in text.strip().split(">")[1:]:
            lines = entry.splitlines()
            header = lines[0].split()[0]
            sequence = "".join(line.strip() for line in lines[1:])
            if header in rows and rows[header] != sequence:
                raise ValueError(f"conflicting duplicate FASTA identifier: {header}")
            rows[header] = sequence
    block: dict[str, str] = {}
    for line in ([] if fasta else text.splitlines()):
        if not line.strip():
            block = {}
            continue
        if line[0].isspace() or line.startswith(("#", "//", "CLUSTAL")):
            continue
        parts = line.split()
        if len(parts) < 2:
            raise ValueError(f"invalid alignment row: {line}")
        name, seq = parts[:2]
        if name in block:
            if block[name] != seq:
                raise ValueError(f"conflicting duplicate alignment row: {name}")
            continue
        block[name] = seq
        rows[name] = rows.get(name, "") + seq
    for name, seq in rows.items():
        seq = seq.replace("-", "").replace(".", "").upper()
        if not re.fullmatch(r"[ACDEFGHIKLMNPQRSTVWYUOBZJX]+", seq):
            raise ValueError(f"invalid protein sequence: {name}")
        rows[name] = seq
    return rows


def source_accession(header: str) -> tuple[str, str] | None:
    match = re.search(r"(?:sp|tr)\|(" + UNIPROT + r")\|", header)
    if not match:
        match = re.match(r"(" + UNIPROT + r")(?:[_|/]|$)", header)
    if match:
        return "UniProtKB", match[1]
    match = re.search(r"(?:WP_\d+|[A-Z]{3}\d{5,7})\.\d+", header)
    if match:
        return "RefSeq" if match[0].startswith("WP_") else "EMBL", match[0]
    return None


def verified_archive(path: Path = RAW / "nrp-metallophore-SI.zip") -> zipfile.ZipFile:
    raw = path.read_bytes()
    if sha256(raw) != ARCHIVE_SHA256 or hashlib.md5(raw).hexdigest() != ARCHIVE_MD5:
        raise ValueError("supplemental archive does not match pinned publisher release")
    return zipfile.ZipFile(path)


def source_facts(archive: zipfile.ZipFile) -> tuple[dict, list[dict]]:
    names = set(archive.namelist())
    model_table = archive.read(BASE + "HMMs_final/hmmdetails.txt").decode()
    models = {}
    for line in model_table.splitlines():
        name, description, cutoff, file = line.split("\t")
        model_path = BASE + "HMMs_final/" + file
        models[name] = {"model": name, "source_description": description,
                        "bitscore_cutoff": float(cutoff), "hmm_path": model_path,
                        "hmm_available": model_path in names}
        if model_path in names:
            models[name]["hmm_sha256"] = sha256(archive.read(model_path))
    if any(models[k]["bitscore_cutoff"] != v for k, v in POSITIVE_CUTOFFS.items()):
        raise ValueError("source thresholds differ from the pinned publication contract")
    full_path = BASE + "hydroxylase_tree/genes.faa"
    full = parse_alignment(archive.read(full_path).decode())
    full_sha = sha256(archive.read(full_path))
    members = []
    for model in catalog()["traits"]:
        stem = ALIGNMENT_ALIASES.get(model, model)
        paths = [BASE + "alignments/" + stem + suffix for suffix in (".clw", ".sto", ".faa")]
        found = [p for p in paths if p in names]
        if not found:  # VbsL: model exists but no seed alignment is deposited.
            continue
        if len(found) != 1:
            raise ValueError(f"ambiguous source alignment for {model}")
        path = found[0]
        raw = archive.read(path)
        for header, seq in parse_alignment(raw.decode()).items():
            fact = {"model": model, "trait_id": PREFIX + model, "source_kind": "seed_alignment",
                    "source_release": RELEASE, "archive_url": ARCHIVE_URL,
                    "archive_sha256": ARCHIVE_SHA256, "alignment_path": path,
                    "alignment_sha256": sha256(raw), "source_header": header,
                    "source_sequence": seq}
            accession = source_accession(header)
            if accession:
                fact["source_namespace"], fact["source_accession"] = accession
            # The full proteins were deposited separately from cropped HMM alignments.
            if model in BETA_MODELS and header in full:
                fact.update(full_sequence=full[header], full_sequence_path=full_path,
                            full_sequence_artifact_sha256=full_sha)
            coords = re.search(r"(?:_Cy\||/)(\d+)-(\d+)$", header)
            if coords:
                start, end = map(int, coords.groups())
                if end - start + 1 != len(seq):
                    fact["coordinate_issue"] = "source interval length differs from aligned sequence"
                else:
                    fact["source_interval"] = {"start": start, "end": end}
            fact["candidate_id"] = "elife109154:" + digest(fact)
            members.append(fact)
    for tar_path in ("nrp-metallophore-SI-main/5_refseq_bigscape/reference_BGCs.tar.gz",):
        with tarfile.open(fileobj=io.BytesIO(archive.read(tar_path))) as source_tar:
            for member in source_tar.getmembers():
                if not member.isfile() or not member.name.endswith(".gbk"):
                    continue
                if any(bgc in member.name for bgc in EXCLUDED_REFERENCE_BGCS):
                    continue
                handle = source_tar.extractfile(member)
                raw = handle.read()
                for protein in parse_bgc_proteins(raw.decode(), models):
                    model = protein["model"]
                    fact = {"model": model, "trait_id": PREFIX + model,
                            "source_kind": "bgc_annotation", "source_release": RELEASE,
                            "archive_url": ARCHIVE_URL, "archive_sha256": ARCHIVE_SHA256,
                            "alignment_path": tar_path + "!" + member.name,
                            "alignment_sha256": sha256(raw),
                            "source_header": protein["protein_id"],
                            "source_sequence": protein["sequence"],
                            "native_annotation": protein["annotation"],
                            "source_bitscore": protein["bitscore"]}
                    accession = source_accession(protein["protein_id"])
                    if accession:
                        fact["source_namespace"], fact["source_accession"] = accession
                    fact["candidate_id"] = "elife109154:" + digest(fact)
                    members.append(fact)
    return models, members


def parse_bgc_proteins(text: str, models: dict) -> list[dict]:
    """Read explicit CDS translations and reported profile hits; never run source code."""
    result = []
    positive = set(catalog()["traits"])
    for match in re.finditer(r"^     CDS\s[^\n]+\n(?: {21}[^\n]*\n)*", text, re.M):
        block = match[0]
        pid = re.search(r'/protein_id="([^"]+)"', block)
        seq = re.search(r'/translation="([^"]+)"', block)
        if not pid or not seq:
            continue
        for annotation in re.findall(r'/sec_met_domain="([^"]+)"', block):
            annotation = " ".join(annotation.split())
            hit = re.match(r"(\S+) \(E-value: [^,]+, bitscore: ([0-9.]+),", annotation)
            if not hit or hit[1] not in positive:
                continue
            model, score = hit[1], float(hit[2])
            if score < models[model]["bitscore_cutoff"]:
                continue
            result.append({"model": model, "protein_id": pid[1],
                           "sequence": "".join(seq[1].split()),
                           "annotation": annotation, "bitscore": score})
    return result


def trait_path(model: str, root: Path = ROOT) -> Path:
    category = "domain" if model in DOMAIN_MODELS else "family"
    return root / "data/traits/sequence" / category / "elife_metallophores" / (model + ".yaml")


def build_record(model: str, models: dict) -> dict:
    entry = catalog()["traits"][model]
    native = models[model]
    record = {"identifier": PREFIX + model, "label": entry["label"],
              "definition": entry["definition"].strip(),
              "definition_source": "DOI:10.7554/eLife.109154.3; DOI:10.5281/zenodo.18866949",
              "trait_axis": "SEQUENCE", "trait_category": entry["category"],
              "term_kind": "CLASS", "mapping_status": "PROPOSED",
              "synonyms": [{"synonym_text": model, "synonym_type": "EXACT_SYNONYM"}],
              "evidence": [{"reference": "DOI:10.7554/eLife.109154.3",
                            "notes": "Figure 1 and Methods; agent-curated sequence-class definition. "
                            "A sequence-family assignment does not establish metabolite production."},
                           {"reference": "DOI:10.5281/zenodo.18866949",
                            "notes": f"{BASE}HMMs_final/hmmdetails.txt: {model}; "
                            f"source bitscore cutoff {native['bitscore_cutoff']:g}. "
                            "BGC rule combinations and negative constraints remain necessary."}],
              "datasets": [{"accession": RELEASE, "title": "NRP metallophore supplemental dataset",
                            "url": "https://zenodo.org/records/18866949",
                            "publication": "DOI:10.7554/eLife.109154.3",
                            "description": f"Source model {model}; chelator context: {entry['chelator']}.",
                            "notes": f"CC BY 4.0; Reitz (2026). Archive SHA-256 {ARCHIVE_SHA256}. "
                            + (f"Model member {native['hmm_path']}; SHA-256 {native['hmm_sha256']}."
                               if native['hmm_available'] else
                               "Lys_monoox.hmm is referenced but absent; source alignment is present.")}],
              "license": "CC-BY-4.0"}
    if native["hmm_available"]:
        record["detection_methods"] = [{
            "name": f"Published {model} profile; source bitscore cutoff {native['bitscore_cutoff']:g}",
            "method_type": "HMM_PROFILE", "tool": "https://hmmer.org/",
            "reference": "DOI:10.5281/zenodo.18866949",
            "recipe": f"hmmsearch -T {native['bitscore_cutoff']:g} "
                      f"data/raw/elife_metallophores/{native['hmm_path']} {{input}} > {{output}}"}]
    return record


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = "".join(json.dumps(r, sort_keys=True, ensure_ascii=True) + "\n" for r in rows)
    temp = path.with_suffix(path.suffix + ".part")
    temp.write_text(content)
    temp.replace(path)


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
