"""Fixed-byte M-CSA facts retaining the complete captured native entry set.

There is no writer or qualification route here. A consumer must supply reviewed
byte pins independently of candidates, evidence, or the snapshot's own metadata.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import PurePosixPath

from mcsa_native_source import (
    ATTRIBUTION, LICENSE, MANIFEST_FIELDS, SOURCE_URL, McsaSourceError,
    SiteLocation, SourcePins, VerifiedSource, _native_entry, _require,
    _timestamp, locate_existing_site, page_url, strict_json, value_sha256,
)

FACT_FIELDS = {
    "fact_sha256", "record_path", "record_semantics", "protein_reference",
    "native_entry_id", "native_entry_sha256", "source_pins",
}
SNAPSHOT_FIELDS = {
    "schema_version", "source_url", "license", "attribution", "source_release",
    "source_pins", "acquisition_manifest_text", "native_entries", "facts", "snapshot_id",
}
REQUIRED_MEANING = {
    "identifier", "label", "definition", "definition_source", "trait_axis",
    "trait_category", "term_kind", "license",
}


def record_semantics(record: dict) -> dict:
    """Bind every non-example field; central promotion changes examples only."""
    _require(isinstance(record, dict), "record must be an object")
    _require(all(isinstance(record.get(key), str) and bool(record[key].strip())
                 for key in REQUIRED_MEANING), "record meaning or license is incomplete")
    result = copy.deepcopy({key: value for key, value in record.items() if key != "canonical_examples"})
    try:
        value_sha256(result)
    except (TypeError, ValueError) as exc:
        raise McsaSourceError("record meaning must have a complete JSON representation") from exc
    return result


def _entries(rows: object, pins: SourcePins) -> dict[int, dict]:
    _require(isinstance(rows, list) and bool(rows), "snapshot lacks the complete native source")
    entries = {}
    for row in rows:
        native = _native_entry(row)
        _require(native["mcsa_id"] not in entries, "duplicate capsule native entry")
        entries[native["mcsa_id"]] = native
    _require(list(entries) == sorted(entries), "native source entries are not in canonical ID order")
    normalized = "".join(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n" for row in rows).encode()
    _require(hashlib.sha256(normalized).hexdigest() == pins.normalized_sha256,
             "complete capsule native entries differ from the acquired source")
    return entries


def _acquisition(text: object, pins: SourcePins, entries: dict[int, dict]) -> dict:
    _require(isinstance(text, str) and hashlib.sha256(text.encode()).hexdigest() == pins.acquisition_sha256,
             "capsule acquisition bytes differ from the reviewed receipt manifest")
    manifest = strict_json(text)
    _require(isinstance(manifest, dict) and set(manifest) == MANIFEST_FIELDS,
             "capsule acquisition fields changed")
    total = manifest["total_entries"]
    pages = math.ceil(len(entries) / 100)
    _require(type(total) is int and total == len(entries)
             and type(manifest["pages_per_pass"]) is int and manifest["pages_per_pass"] == pages,
             "capsule acquisition entry or page count changed")
    _require(manifest["method"] == "GET" and manifest["fetcher"] == "scripts/fetch_source.py"
             and manifest["license"] == LICENSE and manifest["attribution"] == ATTRIBUTION
             and manifest["normalized_sha256"] == pins.normalized_sha256
             and manifest["complete_acquisitions_equal"] is True
             and manifest["requested_urls"] == [page_url(n) for n in range(1, pages + 1)],
             "capsule acquisition source contract changed")
    _require(isinstance(manifest["passes"], list) and len(manifest["passes"]) == 2
             and all(isinstance(rows, list) and len(rows) == pages for rows in manifest["passes"]),
             "capsule acquisition lacks both complete receipt sets")
    _timestamp(manifest["observed_at_utc"])
    return manifest


def validate_fact(fact: dict, pins: SourcePins, entries: dict[int, dict]) -> SiteLocation:
    _require(isinstance(fact, dict) and set(fact) == FACT_FIELDS, "invalid M-CSA source-fact fields")
    _require(fact["source_pins"] == asdict(pins), "fact belongs to another native acquisition")
    payload = {key: value for key, value in fact.items() if key != "fact_sha256"}
    _require(fact["fact_sha256"] == value_sha256(payload), "native source-fact digest mismatch")
    path = fact["record_path"]
    _require(isinstance(path, str), "source-fact record path must be text")
    pure = PurePosixPath(path)
    _require(not pure.is_absolute() and ".." not in pure.parts and str(pure) == path
             and path.startswith("data/traits/") and pure.suffix in {".yaml", ".yml"},
             "source-fact path must be canonical and repo-relative")
    semantics = fact["record_semantics"]
    _require(record_semantics(semantics) == semantics, "source fact has invalid record meaning")
    entry_id = fact["native_entry_id"]
    _require(type(entry_id) is int and entry_id in entries, "source fact lacks its exact native entry")
    native = entries[entry_id]
    _require(fact["native_entry_sha256"] == value_sha256(native), "source fact native entry digest changed")
    reference = fact["protein_reference"]
    record = {**semantics, "canonical_examples": [
        {"protein_id": reference.get("protein_id") if isinstance(reference, dict) else None}
    ]}
    return locate_existing_site(record, reference, native)


def build_snapshot(source: VerifiedSource, acquisition_manifest_text: str,
                   records: dict[str, dict], references: dict[str, dict]) -> tuple[dict, dict]:
    """Capture source facts only after replaying the whole acquired native source."""
    native_rows = [copy.deepcopy(source.entries[key]) for key in sorted(source.entries)]
    entries = _entries(native_rows, source.pins)
    manifest = _acquisition(acquisition_manifest_text, source.pins, entries)
    _require(manifest == source.acquisition, "verified source and receipt manifest disagree")
    by_trait = {f"MCSA:{key}": entry for key, entry in entries.items()}
    facts, blocked, identities = [], Counter(), set()
    for path, record in sorted(records.items()):
        semantics = record_semantics(record)
        trait_id = record["identifier"]
        _require(trait_id not in identities, "one native trait is assigned to multiple records")
        identities.add(trait_id)
        native = by_trait.get(trait_id)
        examples = record.get("canonical_examples")
        _require(isinstance(examples, list) and all(isinstance(row, dict) for row in examples),
                 "source records require their existing example list")
        for example in examples:
            reference = references.get(example.get("protein_id"))
            if reference is None:
                blocked["missing acquired ProteinReference"] += 1
                continue
            if native is None:
                blocked["missing exact native source entry"] += 1
                continue
            try:
                locate_existing_site(record, reference, native)
                fact = {
                    "record_path": path, "record_semantics": semantics,
                    "protein_reference": copy.deepcopy(reference),
                    "native_entry_id": native["mcsa_id"], "native_entry_sha256": value_sha256(native),
                    "source_pins": asdict(source.pins),
                }
                fact["fact_sha256"] = value_sha256(fact)
                validate_fact(fact, source.pins, entries)
                facts.append(fact)
            except McsaSourceError as exc:
                blocked[str(exc)] += 1
    _require(bool(facts), "no complete native site facts were captured")
    snapshot = {
        "schema_version": 1, "source_url": SOURCE_URL, "license": LICENSE,
        "attribution": ATTRIBUTION, "source_release": source.source_release,
        "source_pins": asdict(source.pins), "acquisition_manifest_text": acquisition_manifest_text,
        "native_entries": native_rows, "facts": sorted(facts, key=lambda fact: fact["fact_sha256"]),
    }
    snapshot["snapshot_id"] = "mcsa-native-snapshot:" + value_sha256(snapshot)
    return snapshot, dict(blocked)


def snapshot_bytes(snapshot: dict) -> bytes:
    return (json.dumps(snapshot, sort_keys=True, indent=2) + "\n").encode()


@dataclass(frozen=True)
class VerifiedSnapshot:
    snapshot_id: str
    source_release: str
    facts: dict[str, dict]
    locations: dict[str, SiteLocation]
    native_entries: dict[int, dict]


def verify_snapshot(raw: bytes, expected_sha256: str, expected_pins: SourcePins) -> VerifiedSnapshot:
    """Check the independent complete byte pin before interpreting embedded facts."""
    _require(hashlib.sha256(raw).hexdigest() == expected_sha256,
             "snapshot differs from the independently reviewed byte checksum")
    snapshot = strict_json(raw)
    _require(isinstance(snapshot, dict) and set(snapshot) == SNAPSHOT_FIELDS, "invalid native snapshot fields")
    _require(type(snapshot["schema_version"]) is int and snapshot["schema_version"] == 1
             and snapshot["source_url"] == SOURCE_URL and snapshot["license"] == LICENSE
             and snapshot["attribution"] == ATTRIBUTION
             and snapshot["source_pins"] == asdict(expected_pins)
             and snapshot["source_release"] == f"M-CSA entries API; sha256:{expected_pins.normalized_sha256}",
             "snapshot source, release, license or schema changed")
    payload = {key: value for key, value in snapshot.items() if key != "snapshot_id"}
    _require(snapshot["snapshot_id"] == "mcsa-native-snapshot:" + value_sha256(payload),
             "snapshot content digest mismatch")
    entries = _entries(snapshot["native_entries"], expected_pins)
    _acquisition(snapshot["acquisition_manifest_text"], expected_pins, entries)
    _require(isinstance(snapshot["facts"], list) and bool(snapshot["facts"]), "snapshot has no native site facts")
    facts, locations, identities = {}, {}, set()
    for fact in snapshot["facts"]:
        location = validate_fact(fact, expected_pins, entries)
        key, identity = fact["fact_sha256"], (location.trait_id, location.protein_id)
        _require(key not in facts and identity not in identities, "duplicate native source fact or trait/protein identity")
        facts[key], locations[key] = fact, location
        identities.add(identity)
    return VerifiedSnapshot(snapshot["snapshot_id"], snapshot["source_release"], facts, locations, entries)
