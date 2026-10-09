"""Release-pinned registry sequences reach the browser without qualifying new examples."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from docs_protein_sequences import ProteinSequenceRegistry  # noqa: E402

SPEC = importlib.util.spec_from_file_location("sequence_docs_build", ROOT / "scripts/build_docs_index.py")
BUILD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILD)


@pytest.fixture
def reference():
    seq = "ACDEFGHIKLMNPQRSTVWY"
    return {
        "protein_id": "UniProtKB:P12345", "protein_label": "Example protein",
        "taxon_id": "NCBITaxon:9606", "taxon_label": "Homo sapiens",
        "sequence": seq, "sequence_length": len(seq),
        "sequence_sha256": hashlib.sha256(seq.encode()).hexdigest(),
        "sequence_version": 2, "reviewed": True, "uniprot_release": "2026_03",
    }


@pytest.fixture
def example(reference):
    return {**{k: v for k, v in reference.items() if k != "sequence"},
            "source": "UNIPROT_GROUNDING", "qualification_status": "QUALIFIED",
            "trait_occurrences": [{"trait_id": "Pfam:PF00001",
                                   "protein_id": reference["protein_id"],
                                   "scope": "WHOLE_PROTEIN"}]}


def registry(tmp_path, *rows):
    path = tmp_path / "protein_registry.jsonl"
    path.write_text("".join(json.dumps(row) + "\n" for row in rows))
    return ProteinSequenceRegistry(path)


def test_project_qualified_sequence_without_mutating_sources(tmp_path, reference, example):
    refs = registry(tmp_path, reference)
    before = copy.deepcopy(example)
    stored = (tmp_path / "protein_registry.jsonl").read_bytes()
    projected = BUILD._project_example(example, "Pfam:PF00001", protein_sequences=refs)
    assert projected["seq"] == reference["sequence"]
    assert projected["seqsrc"] == "ProteinReference"
    assert projected["seqsha"] == reference["sequence_sha256"]
    assert projected["rel"] == "2026_03" and projected["sv"] == 2
    assert "feats" not in projected and "occ" not in projected
    assert example == before and (tmp_path / "protein_registry.jsonl").read_bytes() == stored


def test_legacy_projection_stays_legacy_even_with_registry(tmp_path, reference, example):
    refs = registry(tmp_path, reference)
    example.pop("qualification_status")
    projected = BUILD._project_example(example, protein_sequences=refs)
    assert "seq" not in projected and "seqsrc" not in projected
    example["sequence"] = "ACD"
    example["features"] = [{"start": 1, "end": 2, "feature_type": "REGION"}]
    projected = BUILD._project_example(example, protein_sequences=refs)
    assert projected["seq"] == "ACD" and projected["feats"] == [[1, 2, "REGION", "", ""]]
    assert "seqsrc" not in projected


def test_no_silent_fallback_for_qualified_example_without_registry(example):
    example["sequence"] = "ACD"
    with pytest.raises(ValueError, match="requires a protein sequence registry"):
        BUILD._project_example(example, "Pfam:PF00001")


@pytest.mark.parametrize("field,value", [
    ("protein_id", "UniProtKB:Q54321"), ("protein_label", "Different"),
    ("taxon_id", "NCBITaxon:562"), ("taxon_label", "Escherichia coli"),
    ("sequence_length", 18), ("sequence_sha256", "0" * 64),
    ("uniprot_release", "2026_02"), ("sequence_version", 1),
    ("reviewed", False), ("sequence", "ACD"),
])
def test_binding_mismatch_is_not_rendered(tmp_path, reference, example, field, value):
    refs = registry(tmp_path, reference)
    example[field] = value
    with pytest.raises(ValueError, match="sequence binding"):
        BUILD._project_example(example, "Pfam:PF00001", protein_sequences=refs)


def test_isoform_is_resolved_exactly_not_via_canonical_accession(tmp_path, reference, example):
    iso = {**reference, "protein_id": "UniProtKB:P12345-2", "isoform": 2,
           "sequence": "ACD", "sequence_length": 3,
           "sequence_sha256": hashlib.sha256(b"ACD").hexdigest()}
    example.update({k: v for k, v in iso.items() if k not in ("sequence", "isoform")})
    example["trait_occurrences"][0]["protein_id"] = iso["protein_id"]
    refs = registry(tmp_path, reference, iso)
    assert BUILD._project_example(example, protein_sequences=refs)["seq"] == "ACD"
    refs = registry(tmp_path, reference)
    with pytest.raises(ValueError, match="unresolved_protein_reference"):
        BUILD._project_example(example, protein_sequences=refs)


@pytest.mark.parametrize("kind", ["missing", "malformed", "duplicate", "checksum", "length"])
def test_invalid_registry_fails_closed(tmp_path, reference, kind):
    path = tmp_path / "registry.jsonl"
    if kind == "malformed":
        path.write_text("not JSON\n")
    elif kind == "duplicate":
        path.write_text((json.dumps(reference) + "\n") * 2)
    elif kind != "missing":
        reference["sequence_sha256" if kind == "checksum" else "sequence_length"] = (
            "0" * 64 if kind == "checksum" else 100)
        path.write_text(json.dumps(reference) + "\n")
    with pytest.raises(ValueError, match="protein sequence registry"):
        ProteinSequenceRegistry(path)


def test_optional_version_is_not_invented(tmp_path, reference, example):
    reference.pop("sequence_version")
    example.pop("sequence_version")
    projected = BUILD._project_example(example, protein_sequences=registry(tmp_path, reference))
    assert "sv" not in projected and projected["rel"] == "2026_03"


def test_existing_feature_track_is_preserved_only_in_matching_inline_frame(tmp_path, reference, example):
    refs = registry(tmp_path, reference)
    example["features"] = [{"start": 2, "end": 4, "feature_type": "DOMAIN",
                            "trait_axis": "SEQUENCE", "note": "An existing annotation"}]
    with pytest.raises(ValueError, match="feature track has no inline sequence"):
        BUILD._project_example(example, protein_sequences=refs)
    example["sequence"] = reference["sequence"]
    result = BUILD._project_example(example, protein_sequences=refs)
    assert result["feats"] == [[2, 4, "DOMAIN", "SEQUENCE", "An existing annotation"]]


@pytest.mark.parametrize("start,end", [(0, 3), (3, 2), (1, 100), (True, 2), (1, "2")])
def test_generic_feature_bounds_are_checked(tmp_path, reference, example, start, end):
    example["sequence"] = reference["sequence"]
    example["features"] = [{"start": start, "end": end, "feature_type": "DOMAIN"}]
    with pytest.raises(ValueError, match="feature bounds"):
        BUILD._project_example(example, protein_sequences=registry(tmp_path, reference))


def test_load_record_delivers_registry_sequence_in_detail_only(tmp_path, monkeypatch, reference, example):
    monkeypatch.setattr(BUILD, "REPO_ROOT", tmp_path)
    path = tmp_path / "trait.yaml"
    path.write_text(yaml.safe_dump({"identifier": "Pfam:PF00001", "label": "A trait",
                                    "canonical_examples": [example]}))
    row = BUILD.load_record(path, protein_sequences=registry(tmp_path, reference))
    pairs = BUILD.split_detail([row])
    lean, detail = pairs[0]
    assert "ex" not in lean and detail["ex"][0]["seq"] == reference["sequence"]


def test_bad_binding_fails_before_existing_site_files_are_replaced(tmp_path, monkeypatch, reference, example):
    refs = tmp_path / "protein_registry.jsonl"
    refs.write_text(json.dumps(reference) + "\n")
    traits, out = tmp_path / "traits", tmp_path / "out"
    traits.mkdir()
    out.mkdir()
    example["sequence_sha256"] = "0" * 64
    (traits / "trait.yaml").write_text(yaml.safe_dump({"identifier": "Pfam:PF00001",
                                                     "canonical_examples": [example]}))
    sentinel = out / "labels.json"
    sentinel.write_text("existing site")
    monkeypatch.setattr(BUILD, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(BUILD, "TRAITS_DIR", traits)
    monkeypatch.setattr(BUILD, "OUT_DIR", out)
    monkeypatch.setattr(BUILD, "PROTEIN_REGISTRY", refs)
    for name in ("load_equivalence", "load_chebi_names", "load_rhea_chebi", "load_go_chebi"):
        monkeypatch.setattr(BUILD, name, lambda: None)
    with pytest.raises(ValueError, match="sequence binding"):
        BUILD.main()
    assert sentinel.read_text() == "existing site"
    assert [p.name for p in out.iterdir()] == ["labels.json"]


@pytest.mark.parametrize("input_path", [
    "data/grounding/protein_registry.jsonl",
    "scripts/docs_protein_sequences.py",
    "scripts/validate_uniprot_grounding.py",
    "scripts/grounding_registry_layout.py",
    "scripts/uniprot_membership_snapshot.py",
    "scripts/go_true_path.py",
    "scripts/obo_syntax.py",
])
def test_pages_rebuilds_when_sequence_projection_inputs_change(input_path):
    # BaseLoader preserves GitHub's `on` key instead of YAML 1.1 boolean coercion.
    workflow = yaml.load((ROOT / ".github/workflows/pages.yml").read_text(), Loader=yaml.BaseLoader)
    assert input_path in workflow["on"]["push"]["paths"]


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js is not installed")
def test_browser_shows_pinned_sequence_provenance_without_inventing_annotations(tmp_path, reference, example):
    projected = BUILD._project_example(example, protein_sequences=registry(tmp_path, reference))
    projected["rel"] = '<img src=x onerror="bad()">'
    program = r"""
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync(process.argv[1], 'utf8');
assert.match(source, /\nboot\(\);\s*$/);
const context = {window: {}, document: {documentElement: {dataset: {theme: 'light'}}},
                 BrowseShards: {createLoader: () => ({loaded: new Set()})}};
vm.createContext(context);
vm.runInContext(source.replace(/\nboot\(\);\s*$/, '\n'), context);
context.example = JSON.parse(process.argv[2]);
const html = vm.runInContext('renderExample(example, false)', context);
assert.match(html, /Release-pinned UniProt sequence/);
assert.match(html, /sequence version 2/);
assert.ok(html.includes(context.example.seqsha));
assert.match(html, /no feature annotations stored/);
assert.equal((html.match(/class="rletter"/g) || []).length, context.example.seq.length);
assert.match(html, /&lt;img/);
assert.doesNotMatch(html, /<img/);
assert.doesNotMatch(html, /Trait coordinates/);
const unavailable = vm.runInContext('renderSequenceViewer("ACD", [[1, 2, "REGION", ""]])', context);
assert.match(unavailable, /no displayable feature annotations/);
assert.doesNotMatch(unavailable, /no feature annotations stored/);
"""
    result = subprocess.run(["node", "-e", program, str(ROOT / "docs/browse.js"),
                             json.dumps(projected)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
