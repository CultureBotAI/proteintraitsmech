"""The browser must distinguish exact trait locations from generic features."""

import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("coordinate_docs_build", ROOT / "scripts/build_docs_index.py")
BUILD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILD)


@pytest.fixture
def example():
    return {
        "protein_id": "UniProtKB:P12345-2",
        "qualification_status": "QUALIFIED",
        "sequence_version": 3,
        "uniprot_release": "2026_03",
        "sequence": "ACDEFGHIKLMNPQRSTVWY",
        "features": [{"start": 1, "end": 19, "feature_type": "CHAIN", "trait_axis": "SEQUENCE"}],
        "trait_occurrences": [{
            "trait_id": "IEDB:123",
            "protein_id": "UniProtKB:P12345-2",
            "qualification_status": "QUALIFIED",
            "scope": "LOCALIZED",
            "coordinate_frame": "UNIPROT_ISOFORM",
            "intervals": [{"start": 2, "end": 4}, {"start": 11, "end": 14}],
            "residue_positions": [3, 7, 17],
            "mapping_method": "PATTERN_MATCH",
            "source_trait_id": "IEDB:123",
            "evidence_source": "IEDB",
            "source_release": "test release",
        }],
    }


def test_projection_preserves_disjoint_locations_and_existing_feature_track(example):
    original = copy.deepcopy(example)
    projected = BUILD._project_example(example, "IEDB:123")
    assert example == original
    assert projected["occ"][0]["ranges"] == [[2, 4], [11, 14]]
    assert projected["occ"][0]["positions"] == [3, 7, 17]
    assert projected["occ"][0]["coordinate_frame"] == "UNIPROT_ISOFORM"
    assert projected["sv"] == 3 and projected["rel"] == "2026_03"
    assert projected["feats"] == [[1, 19, "CHAIN", "SEQUENCE", ""]]
    assert projected["seq"] == original["sequence"]


@pytest.mark.parametrize("changes", [
    {"trait_id": "IEDB:456"},
    {"protein_id": "UniProtKB:P12345"},
    {"qualification_status": "LEGACY_UNVERIFIED"},
    {"scope": "WHOLE_PROTEIN"},
    {"intervals": [], "residue_positions": []},
])
def test_projection_does_not_present_other_or_unqualified_claims_as_trait_coordinates(example, changes):
    example["trait_occurrences"][0].update(changes)
    assert "occ" not in BUILD._project_example(example, "IEDB:123")


def test_generic_features_or_unqualified_example_do_not_supply_trait_coordinates(example):
    example.pop("qualification_status")
    assert "occ" not in BUILD._project_example(example, "IEDB:123")
    example["qualification_status"] = "QUALIFIED"
    example.pop("trait_occurrences")
    assert "occ" not in BUILD._project_example(example, "IEDB:123")


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js is not installed")
def test_browser_renders_locations_without_a_sequence_and_escapes_source_text(example):
    projected = BUILD._project_example(example, "IEDB:123")
    projected.pop("seq")
    projected["occ"][0]["source_release"] = '<img src=x onerror="bad()">'
    # Run the real browser functions, disabling only the asynchronous application
    # boot. No DOM or network is needed to render an example's coordinate text.
    program = r"""
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync(process.argv[1], 'utf8');
assert.match(source, /\nboot\(\);\s*$/);
const context = {window: {}, BrowseShards: {createLoader: () => ({loaded: new Set()})}};
vm.createContext(context);
vm.runInContext(source.replace(/\nboot\(\);\s*$/, '\n'), context);
context.example = JSON.parse(process.argv[2]);
const html = vm.runInContext('renderExample(example, false)', context);
assert.match(html, /Trait coordinates/);
assert.match(html, /1-based, inclusive/);
assert.match(html, /2–4, 11–14/);
assert.doesNotMatch(html, /2–14/);
assert.match(html, /Residues 3, 7, 17/);
assert.match(html, /UniProt isoform/);
assert.match(html, /sequence version 3/);
assert.match(html, /UniProt release 2026_03/);
assert.match(html, /https:\/\/www\.iedb\.org\/epitope\/123/);
assert.match(html, /&lt;img/);
assert.doesNotMatch(html, /<img/);
assert.doesNotMatch(html, /Sequence &amp; feature map/);
assert.equal(vm.runInContext('renderTraitCoordinates({feats: [[1, 19, "CHAIN", "SEQUENCE"]]})', context), '');
"""
    result = subprocess.run(
        ["node", "-e", program, str(ROOT / "docs/browse.js"), json.dumps(projected)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
