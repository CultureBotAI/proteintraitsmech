"""Preserve independent InterPro locations and their discontinuous fragments.

This parser performs no coordinate inference or qualification.
"""

from __future__ import annotations

import copy
import hashlib
import json
from typing import Any


class NativeCaptureError(ValueError):
    """A native capture cannot support an unambiguous discovery projection."""


def digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(raw.encode()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise NativeCaptureError(message)


def text(value: Any, field: str) -> str:
    require(isinstance(value, str) and bool(value.strip()), f"missing {field}")
    return value


def integer(value: Any, field: str) -> int:
    require(type(value) is int and value > 0, f"invalid {field}")
    return value


def discover_groups(entries: dict, protein: dict, reference: dict) -> dict:
    """Preserve native location boundaries and fragment metadata without inference.

    The bounded canaries must contain a complete single page. Multi-page input
    requires a separate acquisition/receipt contract; this function refuses an
    unfinished page instead of treating its prefix as the whole source result.
    Native accession and database strings are retained, not converted to trait IDs.
    """
    require(isinstance(entries, dict) and isinstance(protein, dict), "invalid capture")
    require(isinstance(reference, dict), "invalid reference")
    protein_id = text(reference.get("protein_id"), "reference protein_id")
    require(protein_id.startswith("UniProtKB:"), "unsupported reference namespace")
    accession = protein_id.split(":", 1)[1]
    sequence = text(reference.get("sequence"), "reference sequence")
    sequence_sha = hashlib.sha256(sequence.encode("ascii")).hexdigest()
    length = integer(reference.get("sequence_length"), "reference length")
    require(len(sequence) == length, "reference length mismatch")
    require(sequence_sha == reference.get("sequence_sha256"), "reference checksum mismatch")
    taxon = text(reference.get("taxon_id"), "reference taxon")
    require(taxon.startswith("NCBITaxon:"), "unsupported reference taxon")
    taxon_number = taxon.split(":", 1)[1]
    metadata = protein.get("metadata")
    require(isinstance(metadata, dict), "missing protein metadata")
    require(text(metadata.get("accession"), "protein accession").upper() == accession.upper(),
            "native protein identity mismatch")
    require(metadata.get("sequence") == sequence, "native protein sequence mismatch")
    require(integer(metadata.get("length"), "native protein length") == length,
            "native protein length mismatch")
    organism = metadata.get("source_organism")
    require(isinstance(organism, dict) and str(organism.get("taxId")) == taxon_number,
            "native protein taxon mismatch")
    require(metadata.get("source_database") in {"reviewed", "unreviewed"},
            "unknown native protein database")
    require((metadata["source_database"] == "reviewed") == reference.get("reviewed"),
            "native reference review-status mismatch")
    require("next" in entries and "previous" in entries, "missing pagination state")
    require(entries["next"] is None and entries["previous"] is None,
            "incomplete single-page capture")
    results = entries.get("results")
    require(isinstance(results, list), "missing native results")
    require(type(entries.get("count")) is int and entries["count"] == len(results),
            "native result count mismatch")
    counters = metadata.get("counters")
    require(isinstance(counters, dict) and counters.get("entries") == len(results),
            "protein and entry captures disagree on entry count")

    groups = []
    seen = set()
    for entry_index, entry in enumerate(results):
        require(isinstance(entry, dict), "invalid native entry")
        entry_meta = entry.get("metadata")
        require(isinstance(entry_meta, dict), "missing native entry metadata")
        entry_id = text(entry_meta.get("accession"), "native entry accession")
        database = text(entry_meta.get("source_database"), "native entry database")
        identity = database, entry_id
        require(identity not in seen, "duplicate native entry identity")
        seen.add(identity)
        proteins = entry.get("proteins")
        require(isinstance(proteins, list) and len(proteins) == 1,
                "expected exactly one native protein per entry")
        matched = proteins[0]
        require(isinstance(matched, dict), "invalid matched protein")
        require(text(matched.get("accession"), "matched accession").upper() == accession.upper(),
                "matched protein identity mismatch")
        require(integer(matched.get("protein_length"), "matched protein length") == length,
                "matched protein length mismatch")
        require(str(matched.get("organism")) == taxon_number, "matched protein taxon mismatch")
        require(matched.get("source_database") == metadata["source_database"],
                "matched protein database mismatch")
        locations = matched.get("entry_protein_locations")
        require(isinstance(locations, list) and bool(locations), "missing native locations")
        native_entry_sha = digest(entry)
        projected = []
        for location_index, location in enumerate(locations):
            require(isinstance(location, dict), "invalid native location")
            fragments = location.get("fragments")
            require(isinstance(fragments, list) and bool(fragments), "missing native fragments")
            intervals = []
            previous_end = 0
            for fragment in fragments:
                require(isinstance(fragment, dict), "invalid native fragment")
                start = integer(fragment.get("start"), "fragment start")
                end = integer(fragment.get("end"), "fragment end")
                require(start <= end <= length, "fragment bounds mismatch")
                require(start > previous_end, "overlapping or unordered native fragments")
                status = fragment.get("dc-status")
                require(status in {"CONTINUOUS", "N_TERMINAL_DISC", "C_TERMINAL_DISC",
                                   "NC_TERMINAL_DISC"}, "unknown native discontinuity status")
                require(len(fragments) == 1 or status != "CONTINUOUS",
                        "continuous fragment in a discontinuous location")
                intervals.append({"start": start, "end": end})
                previous_end = end
            projected.append({
                "native_location_index": location_index,
                "native_location_sha256": digest(location),
                "intervals": intervals,
                "native_location": copy.deepcopy(location),
            })
        groups.append({
            "native_entry_index": entry_index,
            "native_accession": entry_id,
            "native_database": database,
            "native_entry_sha256": native_entry_sha,
            "native_metadata": copy.deepcopy(entry_meta),
            "locations": projected,
        })
    return {
        "scope": "Discovery only; native location groups preserved without coordinate qualification.",
        "protein_id": protein_id,
        "sequence_sha256": sequence_sha,
        "sequence_length": length,
        "entry_capture_sha256": digest(entries),
        "protein_capture_sha256": digest(protein),
        "reference_sha256": digest(reference),
        "source_entries": groups,
        "production_requirements_remaining": [
            "Replay native acquisition receipts and bind the exact source release.",
            "Review an explicit native-database/accession to canonical-trait mapping.",
            "Bind every independent location to its own source evidence.",
            "Review and install the complete location set as one protein alternative.",
            "Preserve existing qualification conflict and legacy flattened-input gates.",
        ],
    }
