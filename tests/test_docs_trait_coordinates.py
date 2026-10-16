"""The browser must distinguish exact trait locations from generic features."""

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("coordinate_docs_build", ROOT / "scripts/build_docs_index.py")
BUILD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILD)


@pytest.fixture
def reference():
    seq = "ACDEFGHIKLMNPQRSTVWY"
    return {
        "protein_id": "UniProtKB:P12345-2",
        "protein_label": "Example protein isoform",
        "taxon_id": "NCBITaxon:9606",
        "taxon_label": "Homo sapiens",
        "isoform": 2,
        "sequence": seq,
        "sequence_length": len(seq),
        "sequence_sha256": hashlib.sha256(seq.encode()).hexdigest(),
        "sequence_version": 3,
        "reviewed": True,
        "uniprot_release": "2026_03",
    }


@pytest.fixture
def example(reference):
    return {
        **reference,
        "source": "UNIPROT_GROUNDING",
        "qualification_status": "QUALIFIED",
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


@pytest.fixture
def seq_registry(tmp_path, reference):
    path = tmp_path / "protein_registry.jsonl"
    path.write_text(json.dumps(reference) + "\n", encoding="utf-8")
    return BUILD.ProteinSequenceRegistry(path)


def test_build_docs_index_uses_safe_yaml_loader():
    assert BUILD.SAFE_YAML_LOADER in (yaml.SafeLoader, getattr(yaml, "CSafeLoader", yaml.SafeLoader))


def test_projection_preserves_disjoint_locations_and_existing_feature_track(example, seq_registry):
    original = copy.deepcopy(example)
    projected = BUILD._project_example(example, "IEDB:123", protein_sequences=seq_registry)
    assert example == original
    assert projected["occ"][0] == {
        "ranges": [[2, 4], [11, 14]],
        "positions": [3, 7, 17],
        "coordinate_frame": "UNIPROT_ISOFORM",
        "mapping_method": "PATTERN_MATCH",
        "evidence_source": "IEDB",
        "source_trait_id": "IEDB:123",
        "source_release": "test release",
    }
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
def test_projection_does_not_present_other_or_unqualified_claims_as_trait_coordinates(example, changes, seq_registry):
    example["trait_occurrences"][0].update(changes)
    projected = BUILD._project_example(example, "IEDB:123", protein_sequences=seq_registry)
    assert "occ" not in projected


def test_generic_features_or_unqualified_example_do_not_supply_trait_coordinates(example, seq_registry):
    example.pop("qualification_status")
    projected = BUILD._project_example(example, "IEDB:123")
    assert "occ" not in projected
    assert "sv" not in projected and "rel" not in projected

    example["qualification_status"] = "LEGACY_UNVERIFIED"
    projected_legacy = BUILD._project_example(example, "IEDB:123")
    assert "occ" not in projected_legacy
    assert "sv" not in projected_legacy and "rel" not in projected_legacy

    example["qualification_status"] = "QUALIFIED"
    example["trait_occurrences"] = [{
        "trait_id": "IEDB:123",
        "protein_id": example["protein_id"],
        "qualification_status": "QUALIFIED",
        "scope": "WHOLE_PROTEIN",
    }]
    projected_qualified_whole = BUILD._project_example(example, "IEDB:123", protein_sequences=seq_registry)
    assert "occ" not in projected_qualified_whole


def test_load_record_projects_trait_coordinates(tmp_path, example, seq_registry, monkeypatch):
    monkeypatch.setattr(BUILD, "REPO_ROOT", tmp_path)
    record_dir = tmp_path / "data" / "traits"
    record_dir.mkdir(parents=True, exist_ok=True)
    record_file = record_dir / "test-trait.yaml"
    record_data = {
        "identifier": "IEDB:123",
        "label": "Test trait",
        "definition": "A test trait definition.",
        "trait_axis": "SEQUENCE",
        "trait_category": "EPITOPE",
        "canonical_examples": [example],
    }
    record_file.write_text(yaml.dump(record_data), encoding="utf-8")
    rec = BUILD.load_record(record_file, protein_sequences=seq_registry)
    assert rec is not None
    assert "ex" in rec and len(rec["ex"]) == 1
    assert "occ" in rec["ex"][0]
    assert rec["ex"][0]["occ"][0]["ranges"] == [[2, 4], [11, 14]]
    assert rec["ex"][0]["occ"][0]["positions"] == [3, 7, 17]
    assert rec["ex"][0]["occ"][0]["coordinate_frame"] == "UNIPROT_ISOFORM"


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js is not installed")
def test_browser_renders_locations_without_a_sequence_and_escapes_source_text(example, seq_registry):
    projected = BUILD._project_example(example, "IEDB:123", protein_sequences=seq_registry)
    projected.pop("seq")
    projected["occ"][0]["source_release"] = '<img src=x onerror="bad()">'

    fixture2 = {
        "id": "UniProtKB:P99999",
        "sv": 1,
        "rel": "2026_03",
        "occ": [{
            "ranges": [[5, 5]],
            "coordinate_frame": "UNIPROT_CANONICAL",
            "mapping_method": "INTERPRO_MATCH",
            "evidence_source": '<script>alert("xss")</script>',
            "source_trait_id": "InterPro:IPR000001",
        }],
    }

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

// Fixture 1: Isoform, pattern match, ranges & positions, escaping source_release
context.example1 = JSON.parse(process.argv[2]);
const html1 = vm.runInContext('renderExample(example1, false)', context);
assert.match(html1, /Trait coordinates/);
assert.match(html1, /1-based, inclusive/);
assert.match(html1, /2–4, 11–14/);
assert.doesNotMatch(html1, /2–14/);
assert.match(html1, /Residues 3, 7, 17/);
assert.match(html1, /Pattern match/);
assert.match(html1, /UniProt isoform/);
assert.match(html1, /sequence version 3/);
assert.match(html1, /UniProt release 2026_03/);
assert.match(html1, /https:\/\/www\.iedb\.org\/epitope\/123/);
assert.match(html1, /&lt;img/);
assert.doesNotMatch(html1, /<img/);
assert.doesNotMatch(html1, /Sequence &amp; feature map/);

// Fixture 2: Canonical, signature match, single-residue interval [5, 5], escaping hostile evidence_source
context.example2 = JSON.parse(process.argv[3]);
const html2 = vm.runInContext('renderExample(example2, false)', context);
assert.match(html2, /<strong>5<\/strong>/);
assert.doesNotMatch(html2, /5[–-]5/);
assert.match(html2, /Signature match/);
assert.match(html2, /UniProt canonical/);
assert.match(html2, /https:\/\/www\.ebi\.ac\.uk\/interpro\/entry\/InterPro\/IPR000001/);
assert.match(html2, /&lt;script&gt;alert\(&quot;xss&quot;\)&lt;\/script&gt;/);
assert.doesNotMatch(html2, /<script>/);

assert.equal(vm.runInContext('renderTraitCoordinates({feats: [[1, 19, "CHAIN", "SEQUENCE"]]})', context), '');

// Fixture 3: Minimal occurrence without method/frame has no dangling interpuncts or empty spans
const html3 = vm.runInContext('renderTraitCoordinates({occ: [{ranges: [[10, 20]]}]})', context);
assert.match(html3, /<strong>10–20<\/strong>/);
assert.doesNotMatch(html3, /·/);
assert.doesNotMatch(html3, /ex-location-source/);
"""
    result = subprocess.run(
        ["node", "-e", program, str(ROOT / "docs/browse.js"), json.dumps(projected), json.dumps(fixture2)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
