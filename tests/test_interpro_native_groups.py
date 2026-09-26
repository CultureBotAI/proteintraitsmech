"""Synthetic native API fixtures; these tests are not acquisition evidence."""

import copy
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from interpro_native_fixtures import synthetic_canaries

import pytest

from interpro_native_groups import NativeCaptureError, discover_groups


@pytest.fixture(scope="module")
def canaries():
    return synthetic_canaries()


def target(result, accession):
    return next(row for row in result["source_entries"] if row["native_accession"] == accession)


def test_independent_locations_remain_separate(canaries):
    native = canaries["P05719"]
    before = copy.deepcopy(native)
    result = discover_groups(*native)
    locations = target(result, "IPR000055")["locations"]
    assert [row["intervals"] for row in locations] == [
        [{"start": 7, "end": 190}], [{"start": 348, "end": 403}]
    ]
    assert len({row["native_location_sha256"] for row in locations}) == 2
    assert native == before


def test_discontinuous_location_and_integrated_entry_are_distinct(canaries):
    result = discover_groups(*canaries["Q796K8"])
    member = target(result, "SSF56519")["locations"]
    assert len(member) == 1
    assert member[0]["intervals"] == [{"start": 59, "end": 121}, {"start": 212, "end": 341}]
    assert [f["dc-status"] for f in member[0]["native_location"]["fragments"]] == [
        "C_TERMINAL_DISC", "N_TERMINAL_DISC"
    ]
    assert member[0]["native_location"]["representative"] is False
    integrated = target(result, "IPR036138")["locations"]
    assert [row["intervals"] for row in integrated] == [[{"start": 59, "end": 341}]]
    assert target(result, "G3DSA:1.10.10.1230")["locations"][0]["intervals"] == [
        {"start": 86, "end": 202}
    ]


@pytest.mark.parametrize("mutation,match", [
    ("sequence", "native protein sequence mismatch"),
    ("accession", "native protein identity mismatch"),
    ("matched_accession", "matched protein identity mismatch"),
    ("taxon", "matched protein taxon mismatch"),
    ("page", "incomplete single-page capture"),
    ("count", "native result count mismatch"),
    ("counters", "captures disagree"),
    ("duplicate_entry", "duplicate native entry identity"),
    ("flat", "missing native fragments"),
    ("empty", "missing native locations"),
    ("reversed", "fragment bounds mismatch"),
    ("outside", "fragment bounds mismatch"),
    ("boolean", "invalid fragment start"),
    ("overlap", "overlapping or unordered"),
    ("unknown_status", "unknown native discontinuity status"),
])
def test_rejects_incomplete_or_substituted_source(canaries, mutation, match):
    entries, protein, reference = copy.deepcopy(canaries["Q796K8"])
    matched = entries["results"][0]["proteins"][0]
    location = matched["entry_protein_locations"][0]
    fragment = location["fragments"][0]
    if mutation == "sequence":
        protein["metadata"]["sequence"] = "A" + reference["sequence"][1:]
    elif mutation == "accession":
        protein["metadata"]["accession"] = "Q796K8-2"
    elif mutation == "matched_accession":
        matched["accession"] = "Q796K8-2"
    elif mutation == "taxon":
        matched["organism"] = "83333"
    elif mutation == "page":
        entries["next"] = "https://www.ebi.ac.uk/interpro/api/?cursor=next"
    elif mutation == "count":
        entries["count"] += 1
    elif mutation == "counters":
        protein["metadata"]["counters"]["entries"] -= 1
    elif mutation == "duplicate_entry":
        entries["results"][1] = copy.deepcopy(entries["results"][0])
    elif mutation == "flat":
        matched["entry_protein_locations"] = [{"start": 86, "end": 202}]
    elif mutation == "empty":
        matched["entry_protein_locations"] = []
    elif mutation == "reversed":
        fragment["start"], fragment["end"] = 202, 86
    elif mutation == "outside":
        fragment["end"] = reference["sequence_length"] + 1
    elif mutation == "boolean":
        fragment["start"] = True
    elif mutation == "overlap":
        fragment["dc-status"] = "C_TERMINAL_DISC"
        location["fragments"].append({"start": 150, "end": 240, "dc-status": "N_TERMINAL_DISC"})
    elif mutation == "unknown_status":
        fragment["dc-status"] = "GUESSED"
    with pytest.raises(NativeCaptureError, match=match):
        discover_groups(entries, protein, reference)


def test_source_location_metadata_changes_remain_visible(canaries):
    original = canaries["Q796K8"]
    changed = copy.deepcopy(original)
    changed[0]["results"][0]["proteins"][0]["entry_protein_locations"][0]["model"] = "changed"
    before = target(discover_groups(*original), "G3DSA:1.10.10.1230")
    after = target(discover_groups(*changed), "G3DSA:1.10.10.1230")
    assert before["native_entry_sha256"] != after["native_entry_sha256"]
    assert before["locations"][0]["native_location_sha256"] != after["locations"][0]["native_location_sha256"]
    assert before["locations"][0]["intervals"] == after["locations"][0]["intervals"]
