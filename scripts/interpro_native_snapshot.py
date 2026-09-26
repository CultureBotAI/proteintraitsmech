"""Portable native InterPro source snapshots and complete location sets.

This source reader neither writes records nor qualifies examples. Verification
requires independently reviewed complete snapshot and acquisition-bundle pins.
Every original response body/header receipt is retained, not just its projection.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path, PurePosixPath
import re

from fetch_interpro_native import strict_json
from interpro_native_capture import ResponseCapture, discover_capture_bundle
from interpro_native_groups import digest, require
from validate_uniprot_grounding import validate_protein_reference

DB_PREFIX = {"interpro": "InterPro", "pfam": "Pfam", "cdd": "CDD",
             "ncbifam": "NCBIfam", "prosite": "PROSITE", "profile": "PROSITE",
             "cathgene3d": "CATH", "smart": "SMART", "hamap": "HAMAP",
             "panther": "PANTHER", "pirsf": "PIRSF", "ssf": "SUPERFAMILY"}
REQUIRED_MEANING = {"identifier", "label", "definition", "definition_source",
                    "trait_axis", "trait_category", "term_kind"}
FACT_FIELDS = {"record_path", "record_semantics_sha256", "trait_id", "protein_id",
               "capture_id", "native_database", "native_accession", "native_entry_sha256",
               "location_set_sha256"}
SNAPSHOT_FIELDS = {"schema_version", "scope", "source_bundle_sha256", "captures",
                   "records", "facts", "snapshot_id"}
SCOPE = "Native source facts only; source-specific license, definition and scope review remain required."


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def record_semantics(record: dict) -> dict:
    require(isinstance(record, dict), "record must be an object")
    require(all(isinstance(record.get(key), str) and record[key].strip()
                for key in REQUIRED_MEANING), "incomplete record meaning")
    result = copy.deepcopy({k: v for k, v in record.items() if k != "canonical_examples"})
    digest(result)
    return result


def record_path(value: str) -> str:
    require(isinstance(value, str), "record path must be text")
    path = PurePosixPath(value)
    require(not path.is_absolute() and ".." not in path.parts and str(path) == value
            and value.startswith("data/traits/") and path.suffix in {".yaml", ".yml"},
            "record path must be canonical and repo-relative")
    return value


def canonical_trait(entry: dict) -> str:
    """Map only the exact asserted identifier; never an integrated parent/family."""
    database, accession = entry["native_database"], entry["native_accession"]
    require(database in DB_PREFIX, "unsupported native signature database")
    if database == "cathgene3d":
        require(bool(re.fullmatch(r"G3DSA:[1-9][0-9]*(?:\.[1-9][0-9]*){3}", accession)),
                "native CATH identifier must be an exact four-level superfamily")
        accession = accession.split(":", 1)[1]
    require(bool(re.fullmatch(r"[A-Za-z0-9._-]+", accession)), "invalid native signature accession")
    return f"{DB_PREFIX[database]}:{accession}"


def capture_envelope(directory: Path, expected_bundle_sha256: str) -> dict:
    """Copy a complete already-captured bundle without following raw-file links."""
    manifest = directory / "bundle.json"
    require(not directory.is_symlink() and not manifest.is_symlink(), "symlink capture")
    raw = manifest.read_bytes()
    require(sha(raw) == expected_bundle_sha256, "acquisition bundle digest mismatch")
    parsed = strict_json(raw)
    files = {}
    for name in parsed["files"]:
        require(bool(re.fullmatch(r"(?:catalog-before|catalog-after|protein|page-[0-9]{4})"
                                 r"\.(?:body|capture)\.json", name)), "invalid raw capture filename")
        path = directory / name
        require(not path.is_symlink() and path.is_file(), "raw capture must be a regular file")
        data = path.read_bytes()
        require(sha(data) == parsed["files"][name], "raw acquisition file digest mismatch")
        files[name] = data.decode("utf-8")
    envelope = {"bundle_json": raw.decode("utf-8"), "files": files}
    verify_capture(envelope, expected_bundle_sha256)
    return envelope


def verify_capture(envelope: dict, expected_bundle_sha256: str) -> tuple[dict, dict]:
    """Replay all responses from memory; original filesystem paths are descriptive."""
    require(isinstance(envelope, dict) and set(envelope) == {"bundle_json", "files"},
            "invalid capture envelope")
    raw = envelope["bundle_json"].encode("utf-8")
    require(sha(raw) == expected_bundle_sha256, "acquisition bundle differs from reviewed pin")
    manifest = strict_json(raw)
    require(set(manifest) == {"schema_version", "plan", "page_count", "files", "result"}
            and type(manifest["schema_version"]) is int and manifest["schema_version"] == 1,
            "invalid acquisition bundle fields")
    plan = manifest["plan"]
    require(digest({k: v for k, v in plan.items() if k != "plan_sha256"})
            == plan["plan_sha256"], "acquisition request plan changed")
    reference = plan["reference"]
    require(not validate_protein_reference(reference, path=Path("<native capture>"), line=0),
            "invalid complete ProteinReference")
    require(reference["protein_id"] == plan["protein_id"]
            and digest(reference) == plan["reference_sha256"], "capture reference mismatch")
    pages = manifest["page_count"]
    require(type(pages) is int and type(plan["max_pages"]) is int
            and 1 <= pages <= plan["max_pages"] <= 100, "invalid native page count")
    names = ["catalog-before", "protein", *[f"page-{i:04d}" for i in range(pages)], "catalog-after"]
    expected = {f"{name}.{kind}.json" for name in names for kind in ("body", "capture")}
    require(set(manifest["files"]) == expected and set(envelope["files"]) == expected,
            "incomplete native raw-file set")

    def capture(name):
        def read(filename):
            raw = envelope["files"][filename].encode("utf-8")
            require(sha(raw) == manifest["files"][filename], "native raw-file digest mismatch")
            return raw
        body = read(f"{name}.body.json")
        metadata = strict_json(read(f"{name}.capture.json"))
        require(metadata.pop("body_file") == f"{name}.body.json", "capture body filename mismatch")
        require(metadata.pop("body_sha256") == sha(body), "capture body checksum mismatch")
        require(metadata.pop("body_bytes") == len(body), "capture body length mismatch")
        require(isinstance(metadata.pop("failed_attempts"), list), "capture attempt history missing")
        metadata["headers"] = tuple(tuple(pair) for pair in metadata["headers"])
        return ResponseCapture(body=body, **metadata)

    result = discover_capture_bundle(
        capture("catalog-before"), [capture(f"page-{i:04d}") for i in range(pages)],
        capture("protein"), capture("catalog-after"), reference,
        release=plan["interpro_release"], minor=plan["interpro_minor_release"],
        page_size=plan["page_size"], max_pages=plan["max_pages"],
    )
    require(result == manifest["result"], "native capture projection changed")
    return result, copy.deepcopy(reference)


@dataclass(frozen=True)
class LocationSet:
    set_sha256: str
    record_path: str
    trait_id: str
    protein_id: str
    capture_id: str
    source_release: str
    source_minor_release: str
    native_uniprot_release: str
    reference: dict
    native_entry: dict
    locations: tuple[dict, ...]


@dataclass(frozen=True)
class VerifiedSnapshot:
    snapshot_id: str
    facts: dict[str, dict]
    sets: dict[str, LocationSet]
    records: dict[str, dict]
    captures: dict[str, tuple[dict, dict]]


def _fact(fact: dict, records: dict, captures: dict) -> LocationSet:
    require(isinstance(fact, dict) and set(fact) == FACT_FIELDS, "invalid location-set fact fields")
    payload = {k: v for k, v in fact.items() if k != "location_set_sha256"}
    require(digest(payload) == fact["location_set_sha256"], "location-set fact digest mismatch")
    path = record_path(fact["record_path"])
    require(path in records, "location set lacks reviewed record meaning")
    semantics = records[path]
    require(record_semantics(semantics) == semantics, "invalid captured record meaning")
    require(digest(semantics) == fact["record_semantics_sha256"]
            and semantics["identifier"] == fact["trait_id"], "location-set record meaning mismatch")
    require(fact["protein_id"] in captures, "location set lacks its native capture")
    source, reference = captures[fact["protein_id"]]
    require(source["capture_id"] == fact["capture_id"], "native capture identity mismatch")
    entries = [e for e in source["discovery"]["source_entries"]
               if e["native_database"] == fact["native_database"]
               and e["native_accession"] == fact["native_accession"]]
    require(len(entries) == 1, "missing exact native signature entry")
    entry = entries[0]
    require(canonical_trait(entry) == fact["trait_id"], "native signature does not assert exact trait")
    require(entry["native_entry_sha256"] == fact["native_entry_sha256"], "native entry changed")
    # The entire native set is copied; no candidate-supplied subset can select locations.
    locations = tuple(copy.deepcopy(entry["locations"]))
    require(bool(locations), "empty native location set")
    require(len({loc["native_location_sha256"] for loc in locations}) == len(locations),
            "duplicate identical native locations require review")
    return LocationSet(fact["location_set_sha256"], path, fact["trait_id"], fact["protein_id"],
                       source["capture_id"], source["interpro_release"],
                       source["interpro_minor_release"], source["native_uniprot_release"],
                       copy.deepcopy(reference), copy.deepcopy(entry), locations)


def _captures(envelopes: dict, expected_bundle_sha256: dict) -> dict:
    require(isinstance(envelopes, dict) and bool(envelopes)
            and set(envelopes) == set(expected_bundle_sha256), "native capture pin coverage mismatch")
    results = {}
    for protein in sorted(envelopes):
        result, reference = verify_capture(envelopes[protein], expected_bundle_sha256[protein])
        require(reference["protein_id"] == protein, "capture key differs from exact protein")
        results[protein] = result, reference
    return results


def build_snapshot(envelopes: dict, expected_bundle_sha256: dict,
                   records: dict, selected_pairs: list[tuple[str, str]]) -> dict:
    """Build unqualified native facts only for exact proteins already on records."""
    captures = _captures(envelopes, expected_bundle_sha256)
    require(isinstance(selected_pairs, list) and bool(selected_pairs), "no selected existing examples")
    require(len(set(selected_pairs)) == len(selected_pairs), "duplicate selected trait/protein pair")
    meanings, facts, identities, trait_paths = {}, [], set(), {}
    for path, protein in sorted(selected_pairs):
        record_path(path)
        require(path in records and protein in captures, "missing selected record or capture")
        record = records[path]
        semantics = record_semantics(record)
        identity = semantics["identifier"], protein
        require(trait_paths.setdefault(identity[0], path) == path,
                "one trait identifier is assigned to multiple record paths")
        require(identity not in identities, "duplicate native trait/protein identity")
        identities.add(identity)
        meanings[path] = semantics
        examples = record.get("canonical_examples")
        require(isinstance(examples, list), "existing example list required")
        matches = [e for e in examples if isinstance(e, dict) and e.get("protein_id") == protein]
        require(len(matches) == 1, "exact protein must already occur once on the record")
        source, reference = captures[protein]
        example = matches[0]
        for key in ("sequence", "sequence_sha256", "sequence_length", "taxon_id", "reviewed"):
            if example.get(key) is not None:
                require(example[key] == reference[key], f"existing example {key} differs from native reference")
        entries = [e for e in source["discovery"]["source_entries"]
                   if e["native_database"] in DB_PREFIX and canonical_trait(e) == identity[0]]
        require(len(entries) == 1, "native entry missing or ambiguous for exact selected trait")
        entry = entries[0]
        fact = {"record_path": path, "record_semantics_sha256": digest(semantics),
                "trait_id": identity[0], "protein_id": protein, "capture_id": source["capture_id"],
                "native_database": entry["native_database"], "native_accession": entry["native_accession"],
                "native_entry_sha256": entry["native_entry_sha256"]}
        fact["location_set_sha256"] = digest(fact)
        _fact(fact, meanings, captures)
        facts.append(fact)
    snapshot = {"schema_version": 1, "scope": SCOPE,
                "source_bundle_sha256": copy.deepcopy(expected_bundle_sha256),
                "captures": copy.deepcopy(envelopes), "records": meanings,
                "facts": sorted(facts, key=lambda x: x["location_set_sha256"])}
    snapshot["snapshot_id"] = "interpro-native-snapshot:" + digest(snapshot)
    return snapshot


def snapshot_bytes(snapshot: dict) -> bytes:
    return (json.dumps(snapshot, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()


def verify_snapshot(raw: bytes, expected_sha256: str,
                    expected_bundle_sha256: dict[str, str]) -> VerifiedSnapshot:
    require(sha(raw) == expected_sha256, "snapshot differs from independently reviewed byte checksum")
    snapshot = strict_json(raw)
    require(isinstance(snapshot, dict) and set(snapshot) == SNAPSHOT_FIELDS, "invalid native snapshot fields")
    require(type(snapshot["schema_version"]) is int and snapshot["schema_version"] == 1
            and snapshot["scope"] == SCOPE, "native snapshot version or scope changed")
    payload = {k: v for k, v in snapshot.items() if k != "snapshot_id"}
    require(snapshot["snapshot_id"] == "interpro-native-snapshot:" + digest(payload),
            "native snapshot content digest mismatch")
    require(snapshot["source_bundle_sha256"] == expected_bundle_sha256, "reviewed source bundle pins changed")
    captures = _captures(snapshot["captures"], expected_bundle_sha256)
    require(isinstance(snapshot["records"], dict) and bool(snapshot["records"]), "missing record meanings")
    require(isinstance(snapshot["facts"], list) and bool(snapshot["facts"]), "missing native location facts")
    facts, sets, identities, trait_paths = {}, {}, set(), {}
    for fact in snapshot["facts"]:
        locations = _fact(fact, snapshot["records"], captures)
        key = locations.set_sha256
        identity = locations.trait_id, locations.protein_id
        require(trait_paths.setdefault(locations.trait_id, locations.record_path) == locations.record_path,
                "one trait identifier is assigned to multiple record paths")
        require(key not in facts and identity not in identities, "duplicate native location set")
        facts[key], sets[key] = copy.deepcopy(fact), locations
        identities.add(identity)
    require(set(snapshot["records"]) == {s.record_path for s in sets.values()},
            "snapshot record meanings differ from the selected location sets")
    return VerifiedSnapshot(snapshot["snapshot_id"], facts, sets,
                            copy.deepcopy(snapshot["records"]), captures)
