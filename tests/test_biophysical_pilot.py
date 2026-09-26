"""The publication gate must reject stale, partial and numerically wrong pilot bundles."""
from copy import deepcopy
import json
from pathlib import Path
import shutil
import sys

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from analyze_biophysical import summarize  # noqa: E402
from biophysical import canonical_json, observation_id, sha256  # noqa: E402
from build_biophysical_overlay import main as overlay_main  # noqa: E402
from calculate_biophysical import digest, main as calculate_main  # noqa: E402
from check_biophysical_pilot import check_pilot, equal_with_roundoff, main  # noqa: E402
from validate_biophysical import load_catalog, load_registry, read_jsonl  # noqa: E402


@pytest.fixture
def pilot(tmp_path, capsys):
    folder = tmp_path / "data/biophysical"
    folder.mkdir(parents=True)
    registry_path = tmp_path / "data/grounding/protein_registry.jsonl"
    registry_path.parent.mkdir()
    sequence = "ACDEFGHIKLMNPQRSTVWY"
    protein = dict(protein_id="UniProtKB:P12345", protein_label="Synthetic fixture",
                   sequence=sequence, sequence_length=len(sequence), sequence_sha256=sha256(sequence),
                   reviewed=True, uniprot_release="2026_03", sequence_version=1,
                   taxon_id="NCBITaxon:9606", taxon_label="Homo sapiens")
    registry_path.write_text(canonical_json(protein) + "\n")
    catalog_path = folder / "descriptors.yaml"
    shutil.copyfile(ROOT / "data/biophysical/descriptors.yaml", catalog_path)
    selected = folder / "pilot.proteins.txt"
    selected.write_text(protein["protein_id"] + "\n")
    observations = folder / "pilot.observations.jsonl"
    assert calculate_main(["--registry", str(registry_path), "--catalog", str(catalog_path),
                          "--proteins", str(selected), "--output", str(observations), "--apply"]) == 0
    map_path = tmp_path / "docs/data/sequence_map.json"
    map_path.parent.mkdir(parents=True)
    meta = dict(model="synthetic", revision="pinned", pooling="mean", window=1022, overlap=256)
    map_path.write_text(json.dumps(dict(embedding=meta, points=[[0.2, 0.4, 0, protein["protein_id"]]])))
    meta_path = folder / "pilot.embedding-meta.json"
    meta_path.write_text(json.dumps(meta))
    bindings_path = folder / "pilot.embedding-proteins.jsonl"
    bindings_path.write_text(canonical_json(dict(accession=protein["protein_id"], length=len(sequence),
                                              sequence_sha256=sha256(sequence))) + "\n")
    assert overlay_main(["--map", str(map_path), "--embedding-proteins", str(bindings_path),
                         "--embedding-meta", str(meta_path), "--registry", str(registry_path),
                         "--catalog", str(catalog_path), "--observations", str(observations),
                         "--output", str(map_path.with_name("sequence_biophysical.json")), "--apply"]) == 0
    report = summarize(list(read_jsonl(observations)), load_registry(registry_path), load_catalog(catalog_path))
    report["observations_sha256"] = digest(observations)
    (folder / "pilot.analysis.json").write_text(json.dumps(report))
    capsys.readouterr()
    return tmp_path


def test_complete_bundle_passes_without_writes(pilot):
    before = {str(p): p.read_bytes() for p in pilot.rglob("*") if p.is_file()}
    assert check_pilot(pilot) == []
    assert main(["--root", str(pilot)]) == 0
    assert {str(p): p.read_bytes() for p in pilot.rglob("*") if p.is_file()} == before


@pytest.mark.parametrize("path,field,value,fragment", [
    ("data/biophysical/pilot.observations.manifest.json", "observation_file_sha256", "0" * 64, "observation_file_sha256"),
    ("data/biophysical/pilot.observations.manifest.json", "protein_ids", [], "protein_ids"),
    ("data/biophysical/pilot.observations.manifest.json", "calculator_version", "old", "calculator_version"),
    ("data/biophysical/pilot.observations.manifest.json", "unrecognized", "value", "unexpected fields"),
    ("docs/data/sequence_biophysical.json", "map_sha256", "stale", "overlay is stale"),
    ("data/biophysical/pilot.analysis.json", "observation_count", 999, "analysis is stale"),
])
def test_manifest_and_published_artifact_drift_fails(pilot, path, field, value, fragment):
    target = pilot / path
    data = json.loads(target.read_text())
    data[field] = value
    target.write_text(json.dumps(data))
    assert any(fragment in error for error in check_pilot(pilot))


def test_silent_omission_of_one_descriptor_fails(pilot):
    path = pilot / "data/biophysical/pilot.observations.jsonl"
    rows = list(read_jsonl(path))[1:]
    path.write_text("".join(canonical_json(row) + "\n" for row in rows))
    assert any("exactly one observation" in error for error in check_pilot(pilot))


def test_rehashed_but_wrong_numeric_value_fails_replay(pilot):
    path = pilot / "data/biophysical/pilot.observations.jsonl"
    rows = list(read_jsonl(path))
    rows[0]["value"] = 123.0
    rows[0]["observation_id"] = observation_id(rows[0])
    path.write_text("".join(canonical_json(row) + "\n" for row in rows))
    assert any("numerical replay" in error for error in check_pilot(pilot))


def test_parameters_in_manifest_cannot_silently_change(pilot):
    path = pilot / "data/biophysical/pilot.observations.manifest.json"
    manifest = json.loads(path.read_text())
    manifest["options"]["ph"] = 6
    path.write_text(json.dumps(manifest))
    assert any("numerical replay" in error for error in check_pilot(pilot))


def test_tsv_and_missing_files_fail(pilot, capsys):
    path = pilot / "data/biophysical/pilot.observations.tsv"
    path.write_text("wrong\n")
    assert any("TSV differs" in error for error in check_pilot(pilot))
    path.unlink()
    assert main(["--root", str(pilot)]) == 1
    assert "validation failed" in capsys.readouterr().err


def test_roundoff_tolerance_does_not_ignore_metadata_or_substantial_numeric_changes():
    expected = {"number": 0.5, "conditions": {"ph": 7.0}, "method": "pinned", "coordinates": [1, 3]}
    actual = deepcopy(expected)
    actual["number"] += 1e-12
    assert equal_with_roundoff(actual, expected)
    actual["number"] += 1e-5
    assert not equal_with_roundoff(actual, expected)
    actual = deepcopy(expected)
    actual["method"] = "different"
    assert not equal_with_roundoff(actual, expected)
    assert not equal_with_roundoff(True, 1.0)
    assert not equal_with_roundoff(float("nan"), 0.5)


def test_ci_checks_the_bundle_and_pages_declares_the_new_assets():
    workflow = yaml.safe_load((ROOT / ".github/workflows/checks.yml").read_text())
    runs = [step.get("run", "") for job in workflow["jobs"].values() for step in job["steps"]]
    assert "just check-biophysical-pilot" in runs
    assert "just check-biophysical-experiments" in runs
    recipe = (ROOT / "justfile").read_text().split("\ncheck-biophysical-pilot ", 1)[1].split("\n\n", 1)[0]
    assert "scripts/check_biophysical_pilot.py" in recipe
    included = yaml.safe_load((ROOT / "docs/_config.yml").read_text())["include"]
    assert {"biophysical-map.js", "biophysical.md", "data"} <= set(included)
    assert 'src="biophysical-map.js"' in (ROOT / "docs/map.html").read_text()


@pytest.mark.skipif(shutil.which("just") is None, reason="just is not installed")
@pytest.mark.parametrize("recipe,script", [
    ("calculate-biophysical", "calculate_biophysical.py"),
    ("biophysical-map", "build_biophysical_overlay.py"),
    ("analyze-biophysical", "analyze_biophysical.py"),
    ("check-biophysical-pilot", "check_biophysical_pilot.py"),
    ("select-biophysical-cohort", "select_biophysical_cohort.py"),
    ("refresh-biophysical", "refresh_biophysical.py"),
    ("import-biophysical-experiments", "import_biophysical_experiments.py"),
    ("check-biophysical-experiments", "import_biophysical_experiments.py"),
])
def test_recipes_preserve_spaced_arguments_without_shell_reinterpretation(tmp_path, recipe, script):
    import os
    import subprocess
    capture = tmp_path / "argv.json"
    marker = tmp_path / "injected"
    uv = tmp_path / "uv"
    uv.write_text('#!/usr/bin/env python3\nimport json,os,sys\n'
                  'open(os.environ["PTM_TEST_ARGV"],"w").write(json.dumps(sys.argv[1:]))\n')
    uv.chmod(0o755)
    argument = f"a directory/$(touch {marker}).jsonl"
    env = dict(os.environ, PATH=str(tmp_path) + os.pathsep + os.environ["PATH"],
               PTM_TEST_ARGV=str(capture))
    subprocess.run(["just", "--justfile", str(ROOT / "justfile"), recipe, "--output", argument],
                   cwd=ROOT, env=env, check=True, capture_output=True, text=True)
    extra = {"check-biophysical-pilot": ["--require-input-provenance"],
             "check-biophysical-experiments": ["--check"]}.get(recipe, [])
    assert json.loads(capture.read_text()) == ["run", "python", "scripts/" + script, *extra, "--output", argument]
    assert not marker.exists()


def test_numeric_conditions_are_exact_metadata_even_inside_replay_tolerance(pilot):
    path = pilot / "data/biophysical/pilot.observations.jsonl"
    rows = list(read_jsonl(path))
    rows[0]["conditions"]["ph"] += 1e-12
    rows[0]["observation_id"] = observation_id(rows[0])
    path.write_text("".join(canonical_json(row) + "\n" for row in rows))
    assert any("numerical replay or provenance differs" in error for error in check_pilot(pilot))


@pytest.mark.parametrize("include_second", [True, False])
def test_pilot_requires_every_selected_protein_in_the_map(pilot, include_second):
    folder = pilot / "data/biophysical"
    registry_path = pilot / "data/grounding/protein_registry.jsonl"
    first = json.loads(registry_path.read_text())
    second = {**first, "protein_id": "UniProtKB:P12346"}
    registry = {p["protein_id"]: p for p in (first, second)}
    registry_path.write_text("".join(canonical_json(p) + "\n" for p in registry.values()))
    selected = folder / "pilot.proteins.txt"
    selected.write_text("\n".join(registry) + "\n")
    bindings_path = folder / "pilot.embedding-proteins.jsonl"
    first_binding = json.loads(bindings_path.read_text())
    bindings_path.write_text(canonical_json(first_binding) + "\n" +
                            canonical_json({**first_binding, "accession": second["protein_id"]}) + "\n")
    map_path = pilot / "docs/data/sequence_map.json"
    if include_second:
        map_data = json.loads(map_path.read_text())
        map_data["points"].append([0.4, 0.5, 0, second["protein_id"]])
        map_path.write_text(json.dumps(map_data))
    observations_path = folder / "pilot.observations.jsonl"
    catalog_path = folder / "descriptors.yaml"
    assert calculate_main(["--registry", str(registry_path), "--catalog", str(catalog_path),
                          "--proteins", str(selected), "--output", str(observations_path), "--apply"]) == 0
    # The general builder may use the matching subset; the publication gate must
    # reject an incomplete join even after every derived artifact is refreshed.
    assert overlay_main(["--map", str(map_path), "--embedding-proteins", str(bindings_path),
                         "--embedding-meta", str(folder / "pilot.embedding-meta.json"),
                         "--registry", str(registry_path), "--catalog", str(catalog_path),
                         "--observations", str(observations_path),
                         "--output", str(map_path.with_name("sequence_biophysical.json")), "--apply"]) == 0
    report = summarize(list(read_jsonl(observations_path)), registry, load_catalog(catalog_path))
    report["observations_sha256"] = digest(observations_path)
    (folder / "pilot.analysis.json").write_text(json.dumps(report))
    if include_second:
        assert check_pilot(pilot) == []
    else:
        assert any("exactly once in the sequence map" in error for error in check_pilot(pilot))


def test_cohort_comments_reproduce_consistently(pilot):
    folder = pilot / "data/biophysical"
    selected = folder / "pilot.proteins.txt"
    selected.write_text("  # indented cohort note\n\n  " + selected.read_text().strip() + "  \n")
    assert check_pilot(pilot) == []
    path = folder / "pilot.observations.jsonl"
    before = path.read_bytes()
    assert calculate_main(["--registry", str(pilot / "data/grounding/protein_registry.jsonl"),
                          "--catalog", str(folder / "descriptors.yaml"), "--proteins", str(selected),
                          "--output", str(path), "--apply"]) == 0
    assert path.read_bytes() == before
    assert check_pilot(pilot) == []
