"""Sequence biophysics pilot, versioned and independent of trait qualification.

Only the 20 standard residues are accepted by the numerical methods. Registry
sequences are never normalized, masked, or silently truncated. Coordinates are
1-based inclusive in the exact canonical/isoform sequence.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import json
import math
from pathlib import Path

VERSION = "1.0.1"
ALPHABET = "ACDEFGHIKLMNPQRSTVWY"
PILOT = ("B01", "B02", "B03", "B04", "B05", "B06", "B08", "B09", "B10", "B13", "B16", "B22")
# Kyte & Doolittle 1982, AAindex KYTJ820101. Larger means more hydrophobic.
KD = dict(zip(ALPHABET, (1.8, 2.5, -3.5, -3.5, 2.8, -0.4, -3.2, 4.5, -3.9, 3.8,
                         1.9, -3.5, -1.6, -3.5, -4.5, -0.8, -0.7, 4.2, -0.9, -1.3)))
# Bjellqvist tables, as documented in Bio.SeqUtils.IsoelectricPoint (1.85).
POSITIVE_PKA = {"K": 10.0, "R": 12.0, "H": 5.98}
NEGATIVE_PKA = {"D": 4.05, "E": 4.45, "C": 9.0, "Y": 10.0}
NTERM_PKA = {"A": 7.59, "M": 7.0, "S": 6.93, "P": 8.36, "T": 6.82, "V": 7.44, "E": 7.7}
CTERM_PKA = {"D": 4.55, "E": 4.75}
IP_SOURCE = "https://biopython.org/docs/1.85/api/Bio.SeqUtils.IsoelectricPoint.html"
SCD_SOURCE = "https://doi.org/10.1063/1.4929391"
KD_SOURCE = "https://www.genome.jp/entry/aaindex:KYTJ820101"


def canonical_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                      allow_nan=False)


def sha256(text):
    return hashlib.sha256(text.encode("ascii")).hexdigest()


def observation_id(observation):
    return "ptm-observation:" + sha256(canonical_json(
        {k: v for k, v in observation.items() if k != "observation_id"}))


def comparison_context(observation):
    """Method/conditions that must agree before pooling whole-protein results.

    Per-protein terminal pKa adjustments are outputs of the same pinned model;
    per-protein prediction source hashes identify distinct inputs, not methods.
    """
    method = {k: v for k, v in observation["method"].items() if k != "source_artifact_sha256"}
    method["parameters"] = [p for p in method["parameters"]
                            if p["name"] not in {"nterm_pka", "cterm_pka"}]
    return {"method": method, "conditions": observation.get("conditions", {}),
            "unit": observation["unit"], "scale": observation.get("scale"),
            "normalization": observation.get("normalization"),
            "evidence_mode": observation["evidence_mode"], "proteoform": observation["proteoform"]}


def descriptor_id(inventory_id):
    return "proteintraitsmech:" + inventory_id


def check_sequence(sequence):
    if not sequence or set(sequence) - set(ALPHABET):
        raise ValueError("requires a nonempty sequence of the 20 standard uppercase amino acids")


def charge(sequence, ph, *, n_terminus=True, c_terminus=True):
    """Independent-site Henderson-Hasselbalch model, in elementary charges."""
    check_sequence(sequence)
    if not math.isfinite(ph) or not 0 <= ph <= 14:
        raise ValueError("pH must be finite and in [0,14]")
    counts = Counter(sequence)
    value = sum(counts[a] / (1 + 10 ** (ph - pka)) for a, pka in POSITIVE_PKA.items())
    value -= sum(counts[a] / (1 + 10 ** (pka - ph)) for a, pka in NEGATIVE_PKA.items())
    if n_terminus:
        value += 1 / (1 + 10 ** (ph - NTERM_PKA.get(sequence[0], 7.5)))
    if c_terminus:
        value -= 1 / (1 + 10 ** (CTERM_PKA.get(sequence[-1], 3.55) - ph))
    return value


def isoelectric_point(sequence, **termini):
    """Bisection on [0,14]; no clamp to a boundary when no root exists."""
    lo, hi = 0.0, 14.0
    if not charge(sequence, lo, **termini) > 0 > charge(sequence, hi, **termini):
        return None
    while hi - lo > 1e-6:
        mid = (hi + lo) / 2
        if charge(sequence, mid, **termini) > 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def scd(sequence):
    """Sawle-Ghosh SCD: sum(i<j) q_i q_j sqrt(j-i) / N, KR=+1, DE=-1.

    Zero charged pairs give zero (unlike kappa, this is defined). The caller
    bounds sequence length because this reference implementation is quadratic.
    """
    check_sequence(sequence)
    charged = [(i, 1 if a in "KR" else -1) for i, a in enumerate(sequence) if a in "KRDE"]
    roots = [math.sqrt(i) for i in range(len(sequence))]
    return math.fsum(qi * qj * roots[j - i] for k, (i, qi) in enumerate(charged)
                     for j, qj in charged[k + 1:]) / len(sequence)


def entropy(sequence):
    check_sequence(sequence)
    return -sum((n / len(sequence)) * math.log2(n / len(sequence))
                for n in Counter(sequence).values())


def hydrophobic_moment(sequence, angle=100.0):
    """Mean vector magnitude on the KD scale, with an assumed residue rotation."""
    check_sequence(sequence)
    theta = math.radians(angle)
    x = math.fsum(KD[a] * math.cos(i * theta) for i, a in enumerate(sequence))
    y = math.fsum(KD[a] * math.sin(i * theta) for i, a in enumerate(sequence))
    return math.hypot(x, y) / len(sequence)


def windows(sequence, width, start, statistic):
    return [{"start": start + i, "end": start + i + width - 1,
             "value": statistic(sequence[i:i + width])}
            for i in range(len(sequence) - width + 1)]


def disorder_segments(scores, start, threshold):
    intervals = []
    for i, score in enumerate(scores):
        if score > threshold:
            pos = start + i
            if intervals and intervals[-1]["end"] == pos - 1:
                intervals[-1]["end"] = pos
            else:
                intervals.append({"start": pos, "end": pos})
    return intervals


def validate_prediction(prediction, protein):
    """Require full-sequence scores and explicit predictor provenance; never align by ID alone."""
    expected = {"protein_id", "sequence_sha256", "predictor", "version", "mode", "reference", "scores"}
    if set(prediction) != expected:
        raise ValueError(f"disorder input requires exactly {sorted(expected)}")
    for name in expected - {"scores"}:
        if not isinstance(prediction[name], str) or not prediction[name].strip():
            raise ValueError(f"disorder {name} must be a nonempty string")
    for name in ("protein_id", "sequence_sha256"):
        if prediction[name] != protein[name]:
            raise ValueError(f"disorder {name} does not match the protein")
    scores = prediction["scores"]
    if not isinstance(scores, list) or len(scores) != len(protein["sequence"]):
        raise ValueError("disorder score count must match the full reference sequence")
    if any(type(v) not in (int, float) or not math.isfinite(v) or not 0 <= v <= 1 for v in scores):
        raise ValueError("disorder scores must be finite numbers in [0,1]")


def calculate(protein, *, start=None, end=None, ph=7.0, window=19, moment_window=11,
              angle=100.0, region_termini="native", disorder=None, threshold=0.5,
              max_scd_length=5000):
    """Twelve descriptor families; B10 is a local candidate-geometry profile.

    Native regions keep a terminal group only if they include that original
    chain end. Cleaved regions acquire free N/C termini. No PTM correction.
    B22 consumes externally supplied predictions on the FULL reference sequence
    before slicing, preserving the predictor's sequence context.
    """
    full = protein["sequence"]
    if not full or sha256(full) != protein["sequence_sha256"] or len(full) != protein["sequence_length"]:
        raise ValueError("registry sequence hash/length mismatch")
    if (start is None) != (end is None):
        raise ValueError("both start and end are required for a region")
    region = start is not None
    start, end = (start, end) if region else (1, len(full))
    if type(start) is not int or type(end) is not int or not 1 <= start <= end <= len(full):
        raise ValueError("invalid 1-based inclusive region")
    if region_termini not in {"native", "cleaved"}:
        raise ValueError("region_termini must be native or cleaved")
    if any(type(w) is not int or w < 1 for w in (window, moment_window, max_scd_length)):
        raise ValueError("window widths and max_scd_length must be positive integers")
    if not math.isfinite(angle) or not 0 < angle <= 180:
        raise ValueError("rotation must be in (0,180] degrees")
    if not math.isfinite(threshold) or not 0 <= threshold <= 1:
        raise ValueError("disorder threshold must be in [0,1]")
    if not math.isfinite(ph) or not 0 <= ph <= 14:
        raise ValueError("pH must be in [0,14]")
    if disorder is not None:
        validate_prediction(disorder, protein)
    sequence = full[start - 1:end]
    length = len(sequence)
    valid = not (set(sequence) - set(ALPHABET))
    implementation_sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    termini = {"n_terminus": region_termini == "cleaved" or start == 1,
               "c_terminus": region_termini == "cleaved" or end == len(full)}
    observations = []

    def add(code, name, reference, *, unit="1", parameters=None, **result):
        # External scores retain the predictor's input assumptions. The adapter
        # preserves the reference sequence; it must not invent a predictor
        # alphabet or inherit the local calculators' nonstandard-residue policy.
        params = {} if code == "B22" else {
            "alphabet": ALPHABET, "nonstandard_residues": "undefined; never mask or impute"}
        params.update(parameters or {})
        obs = {"descriptor_id": descriptor_id(code),
               **{k: protein[k] for k in ("protein_id", "sequence_sha256", "sequence_length", "uniprot_release")},
               "analyzed_sequence_sha256": sha256(sequence),
               "scope": "REGION" if region else "WHOLE_PROTEIN",
               "proteoform": "unmodified sequence model; " +
                            (f"{region_termini} region termini" if region else "free chain termini"),
               "evidence_mode": "SEQUENCE_CALCULATION", "status": "OK", "unit": unit,
               "method": {"name": name, "version": VERSION, "reference": reference,
                          "implementation": "scripts/biophysical.py",
                          "implementation_sha256": implementation_sha,
                          "parameters": [{"name": k, "value": str(v)} for k, v in sorted(params.items())]},
               "evidence": [{"reference": reference, "notes": "Method definition, not experimental evidence for this protein."}],
               **result}
        if "sequence_version" in protein:
            obs["sequence_version"] = protein["sequence_version"]
        if region:
            obs["region"] = {"start": start, "end": end}
        if not valid and code != "B22":
            for k in ("value", "components", "profile", "intervals"):
                obs.pop(k, None)
            obs.update(status="UNDEFINED", missing_reason="Nonstandard residues: " +
                       ",".join(sorted(set(sequence) - set(ALPHABET))))
        obs["observation_id"] = observation_id(obs)
        observations.append(obs)
        return obs

    pka_parameters = {"pka_set": "Bjellqvist; Biopython 1.85 tables", **termini,
                      "positive_pka": canonical_json(POSITIVE_PKA),
                      "negative_pka": canonical_json(NEGATIVE_PKA),
                      "nterm_pka": NTERM_PKA.get(sequence[0], 7.5),
                      "cterm_pka": CTERM_PKA.get(sequence[-1], 3.55),
                      "ptms_ligands_structure_shifts": "not modeled"}
    add("B01", "Independent-site charge", IP_SOURCE, unit="e", parameters=pka_parameters,
        conditions={"ph": ph}, **({"value": charge(sequence, ph, **termini)} if valid else {}))
    pi = isoelectric_point(sequence, **termini) if valid else None
    add("B02", "Isoelectric-point bisection", IP_SOURCE, unit="pH",
        parameters={**pka_parameters, "ph_range": "0..14", "ph_tolerance": "0.000001"},
        **({"value": pi} if pi is not None else {"status": "UNDEFINED", "missing_reason": "No unique charge-zero crossing in [0,14]."}))
    counts = Counter(sequence)
    for code, residues, name in (("B03", "KR", "Basic-residue fraction"),
                                  ("B04", "DE", "Acidic-residue fraction"),
                                  ("B05", "KRDE", "Fraction of charged residues")):
        add(code, name, "https://pappulab.github.io/localCIDER/", parameters={"residue_set": residues},
            normalization="residue count / analyzed sequence length",
            value=sum(counts[a] for a in residues) / length)
    add("B06", "Sawle-Ghosh sequence charge decoration", SCD_SOURCE,
        parameters={"charges": "K,R=+1; D,E=-1; others=0; no terminal charges",
                    "formula": "sum(i<j, q_i*q_j*sqrt(j-i))/N", "max_length": max_scd_length,
                    "applicability": "charge arrangement; conformational interpretation is IDR-specific"},
        **({"value": scd(sequence)} if valid and length <= max_scd_length else
           {"status": "NOT_AVAILABLE", "missing_reason": "Sequence exceeds the configured quadratic SCD length limit."}))
    scale = {"scale": "AAindex:KYTJ820101", "normalization": "original scale; larger is more hydrophobic"}
    add("B08", "Mean Kyte-Doolittle hydropathy", KD_SOURCE, **scale,
        **({"value": sum(KD[a] for a in sequence) / length} if valid else {}))
    for code, name, width, stat, reference, extra in (
        ("B09", "Local Kyte-Doolittle hydropathy", window,
         lambda seq: sum(KD[a] for a in seq) / len(seq), KD_SOURCE, {}),
        ("B10", "Local mean hydrophobic moment", moment_window,
         lambda seq: hydrophobic_moment(seq, angle), "https://doi.org/10.1038/299371a0",
         {"rotation_degrees": angle, "geometry": "assumed constant rotation; not observed secondary structure"}),
    ):
        profile_scale = {**scale, "normalization": "magnitude of vector sum / window length"} if code == "B10" else scale
        add(code, name, reference, **profile_scale,
            parameters={"window": width, "stride": 1, "weighting": "uniform",
                        "edges": "valid windows only; no padding", **extra},
            **({"profile": windows(sequence, width, start, stat)} if valid and length >= width else
               {"status": "UNDEFINED", "missing_reason": "Sequence shorter than the configured window."}))
    add("B13", "Amino-acid composition", "https://biopython.org/docs/1.85/api/Bio.SeqUtils.ProtParam.html",
        components=[{"label": a, "value": counts[a] / length} for a in ALPHABET],
        normalization="fractions over all analyzed residues; sum=1")
    add("B16", "Shannon sequence entropy", "https://doi.org/10.1002/j.1538-7305.1948.tb01338.x", unit="bit",
        parameters={"log_base": 2, "scope": "whole analyzed sequence; no low-complexity cutoff"},
        **({"value": entropy(sequence)} if valid else {}))
    if disorder is None:
        add("B22", "External disorder prediction", "https://iupred3.elte.hu/",
            evidence_mode="MODEL_PREDICTION", status="NOT_AVAILABLE",
            parameters={"threshold": threshold, "comparison": ">"},
            missing_reason="No named, versioned, sequence-matched predictor scores supplied.")
    else:
        scores = disorder["scores"][start - 1:end]
        obs = add("B22", disorder["predictor"], disorder["reference"],
                  evidence_mode="MODEL_PREDICTION",
                  parameters={"threshold": threshold, "comparison": ">", "mode": disorder["mode"],
                              "prediction_context": "full reference sequence before region slicing"},
                  value=sum(v > threshold for v in scores) / length,
                  profile=[{"start": start + i, "end": start + i, "value": v} for i, v in enumerate(scores)],
                  intervals=disorder_segments(scores, start, threshold))
        obs["method"]["version"] = disorder["version"]
        obs["method"]["source_artifact_sha256"] = sha256(canonical_json(disorder))
        obs["observation_id"] = observation_id(obs)
    return observations
