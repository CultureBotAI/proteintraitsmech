"""Scientific regression and fail-closed provenance checks for the biophysical pilot."""
from copy import deepcopy
import json
import math
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import biophysical as bio  # noqa: E402
from build_biophysical_overlay import build_overlay  # noqa: E402
from calculate_biophysical import main  # noqa: E402
from validate_biophysical import (  # noqa: E402
    load_catalog, load_registry, schema_errors, validate_collection, validate_observation,
)


def protein(sequence="ACDEFGHIKLMNPQRSTVWY", protein_id="UniProtKB:P12345"):
    return dict(protein_id=protein_id, protein_label="Synthetic test fixture", sequence=sequence,
                sequence_length=len(sequence), sequence_sha256=bio.sha256(sequence),
                sequence_version=1, uniprot_release="2026_03", taxon_id="NCBITaxon:9606",
                taxon_label="Homo sapiens", reviewed=True)


@pytest.fixture(scope="module")
def catalog():
    return load_catalog()


def by_code(observations):
    return {o["descriptor_id"].split(":")[-1]: o for o in observations}


def errors(obs, p, catalog):
    # Re-hash intentional mutations, so tests exercise semantics, not just the digest.
    obs["observation_id"] = bio.observation_id(obs)
    return validate_observation(obs, {p["protein_id"]: p}, catalog)


@pytest.mark.parametrize("sequence,charge,pi,gravy", [
    # Biopython IsoelectricPoint documented peptides; precise numbers independently
    # evaluated using Biopython 1.87 with its unchanged Bjellqvist tables.
    ("INGAR", 0.7600916142893016, 9.750021171569824, -0.42),
    ("PETER", -1.0358602083752255, 4.532079887390137, -2.76),
    (bio.ALPHABET, -0.12492899297528393, 6.784552192687988, -0.49),
])
def test_reference_charge_pi_and_hydropathy(sequence, charge, pi, gravy):
    observed = by_code(bio.calculate(protein(sequence)))
    assert observed["B01"]["value"] == pytest.approx(charge, abs=1e-12)
    assert observed["B02"]["value"] == pytest.approx(pi, abs=1e-4)
    assert observed["B08"]["value"] == pytest.approx(gravy, abs=1e-12)


def test_composition_entropy_and_charge_redundancy():
    observed = by_code(bio.calculate(protein(bio.ALPHABET)))
    assert observed["B03"]["value"] == observed["B04"]["value"] == 0.1
    assert observed["B05"]["value"] == 0.2
    assert all(c["value"] == 0.05 for c in observed["B13"]["components"])
    assert observed["B16"]["value"] == pytest.approx(math.log2(20))
    assert bio.entropy("AAAA") == 0
    # Histidine contributes to the titration model but not KRDE composition.
    histidine = by_code(bio.calculate(protein("HHHH")))
    assert histidine["B05"]["value"] == 0
    assert bio.charge("HHHH", 5) > bio.charge("HHHH", 7)


def test_scd_is_order_sensitive_and_has_defined_zero():
    assert bio.scd("KE") == -0.5
    assert bio.scd("KAE") == pytest.approx(-math.sqrt(2) / 3)
    assert bio.scd("AAAA") == 0
    assert bio.scd("KAAA") == 0
    assert bio.scd("KKEE") < bio.scd("KEKE")
    assert bio.scd("KEKAAAEE") == pytest.approx(bio.scd("EEAAAKEK"))


def test_hydrophobic_moment_geometry_and_window_coordinates():
    assert bio.hydrophobic_moment("AA", 180) == pytest.approx(0, abs=1e-12)
    assert bio.hydrophobic_moment("IK", 180) == pytest.approx(4.2)
    p = protein("AAIKVA")
    obs = by_code(bio.calculate(p, start=3, end=5, window=2, moment_window=2, angle=180))
    assert [(r["start"], r["end"]) for r in obs["B09"]["profile"]] == [(3, 4), (4, 5)]
    assert [r["value"] for r in obs["B09"]["profile"]] == pytest.approx([0.3, 0.15])
    assert obs["B10"]["profile"][0]["value"] == pytest.approx(4.2)
    assert obs["B09"]["analyzed_sequence_sha256"] == bio.sha256("IKV")


def test_native_region_is_not_a_new_free_peptide():
    p = protein("MAAAK")
    native = by_code(bio.calculate(p, start=2, end=4))
    cleaved = by_code(bio.calculate(p, start=2, end=4, region_termini="cleaved"))
    assert native["B01"]["value"] == 0
    assert native["B02"]["status"] == "UNDEFINED"
    assert cleaved["B02"]["status"] == "OK"
    assert native["B01"]["observation_id"] != cleaved["B01"]["observation_id"]


def test_nonstandard_residues_are_never_masked_or_given_zero(catalog):
    p = protein("AAXAA")
    obs = bio.calculate(p)
    for row in obs[:-1]:
        assert row["status"] == "UNDEFINED"
        assert not {"value", "components", "profile"} & row.keys()
        assert "X" in row["missing_reason"]
    assert obs[-1]["status"] == "NOT_AVAILABLE"
    assert validate_collection(obs, {p["protein_id"]: p}, catalog) == []


def test_short_sequence_and_runtime_limit_are_explicit(catalog):
    p = protein("KE")
    observed = by_code(bio.calculate(p, max_scd_length=1))
    assert observed["B06"]["status"] == "NOT_AVAILABLE"
    assert observed["B09"]["status"] == observed["B10"]["status"] == "UNDEFINED"
    assert validate_collection(list(observed.values()), {p["protein_id"]: p}, catalog) == []


def prediction(p, scores):
    return dict(protein_id=p["protein_id"], sequence_sha256=p["sequence_sha256"],
                predictor="SyntheticPredictorFixture", version="test-1", mode="test-only",
                reference="https://example.org/synthetic-test-only", scores=scores)


def test_disorder_threshold_segments_and_parent_context(catalog):
    p = protein("AAAAAA")
    pred = prediction(p, [0.1, 0.5, 0.6, 0.9, 0.2, 0.8])
    observed = by_code(bio.calculate(p, start=2, end=6, disorder=pred))["B22"]
    assert observed["evidence_mode"] == "MODEL_PREDICTION"
    assert observed["value"] == 3 / 5  # exactly 0.5 is not greater than the cutoff
    assert observed["intervals"] == [{"start": 3, "end": 4}, {"start": 6, "end": 6}]
    assert observed["method"]["version"] == "test-1"
    assert not errors(observed, p, catalog)
    observed["intervals"][0]["start"] = 2
    assert any("intervals disagree" in e for e in errors(observed, p, catalog))


@pytest.mark.parametrize("sequence", [bio.ALPHABET, "AX"])
def test_external_disorder_does_not_invent_the_predictors_residue_policy(catalog, sequence):
    p = protein(sequence)
    obs = by_code(bio.calculate(p, disorder=prediction(p, [0.7] * len(sequence))))["B22"]
    assert obs["status"] == "OK"
    assert obs["value"] == 1.0
    parameters = {param["name"] for param in obs["method"]["parameters"]}
    assert not {"alphabet", "nonstandard_residues"} & parameters
    assert not errors(obs, p, catalog)


@pytest.mark.parametrize("mutate", [
    lambda p: p.update(sequence_sha256="0" * 64),
    lambda p: p.update(scores=[0.2]),
    lambda p: p.update(scores=[0.2, float("nan")]),
    lambda p: p.update(scores=[0.2, 1.1]),
    lambda p: p.update(version=""),
    lambda p: p.update(unexpected=True),
])
def test_malformed_predictor_inputs_fail(mutate):
    p = protein("AA")
    pred = prediction(p, [0.2, 0.8])
    mutate(pred)
    with pytest.raises(ValueError):
        bio.calculate(p, disorder=pred)


@pytest.mark.parametrize("options", [
    {"start": 0, "end": 3}, {"start": 1}, {"start": 3, "end": 2},
    {"window": 0}, {"angle": float("inf")}, {"ph": float("nan")},
    {"ph": 15}, {"threshold": -1}, {"max_scd_length": 0},
])
def test_invalid_calculation_parameters_fail(options):
    with pytest.raises(ValueError):
        bio.calculate(protein(), **options)


def test_closed_schema_rejects_unknown_nested_fields(catalog):
    p = protein()
    obs = bio.calculate(p)[0]
    obs["method"]["guessed_precision"] = 1
    assert any("Additional properties" in e for e in errors(obs, p, catalog))


@pytest.mark.parametrize("mutate,fragment", [
    (lambda o: o.update(sequence_sha256="0" * 64), "sequence_sha256"),
    (lambda o: o.update(sequence_version=2), "sequence_version"),
    (lambda o: o.update(analyzed_sequence_sha256="0" * 64), "analyzed sequence"),
    (lambda o: o.update(region={"start": 1, "end": 2}), "WHOLE_PROTEIN"),
    (lambda o: o.update(scope="REGION"), "REGION requires"),
    (lambda o: o.update(unit="kg"), "unit differs"),
    (lambda o: o.update(conditions={}), "requires pH"),
    (lambda o: o.update(status="NOT_AVAILABLE", missing_reason="missing"), "numerical payloads"),
    (lambda o: o.update(components=[{"label": "A", "value": 1}]), "result fields"),
    (lambda o: o.update(evidence=[]), "evidence must"),
])
def test_provenance_scope_and_payload_invariants(catalog, mutate, fragment):
    p = protein()
    obs = bio.calculate(p)[0]
    mutate(obs)
    assert any(fragment in e for e in errors(obs, p, catalog))


def test_nonfinite_and_duplicate_observations_fail(catalog):
    p = protein()
    obs = bio.calculate(p)[0]
    obs["value"] = float("nan")
    assert validate_observation(obs, {p["protein_id"]: p}, catalog)
    obs = bio.calculate(p)[0]
    obs["value"] += 1
    assert any("content hash" in e for e in validate_observation(obs, {p["protein_id"]: p}, catalog))
    obs = bio.calculate(p)[0]
    assert any("duplicate" in e for e in validate_collection([obs, obs], {p["protein_id"]: p}, catalog))


def test_composition_and_window_corruption_fail(catalog):
    p = protein()
    obs = by_code(bio.calculate(p))
    obs["B13"]["components"][0]["value"] = 0.5
    assert any("sum to 1" in e for e in errors(obs["B13"], p, catalog))
    obs["B09"]["profile"][0]["end"] = 999
    assert any("scope" in e for e in errors(obs["B09"], p, catalog))


def test_catalog_represents_all_twelve_families_and_quality_links(catalog):
    assert {d["inventory_id"] for d in catalog.values()} == set(bio.PILOT)
    assert "PATO:0001886" in catalog["proteintraitsmech:B08"]["quality_anchors"]
    assert not schema_errors({"descriptors": list(catalog.values())}, "BiophysicalDescriptorCatalog")


@pytest.mark.parametrize("field,value", [
    ("inventory_id", "B99"), ("descriptor_id", "other:basic_fraction"),
    ("value_kind", "VECTOR"), ("unit", "kg"),
])
def test_catalog_rejects_changes_to_known_operational_contracts(tmp_path, catalog, field, value):
    descriptors = deepcopy(list(catalog.values()))
    next(d for d in descriptors if d["inventory_id"] == "B03")[field] = value
    path = tmp_path / "catalog.yaml"
    path.write_text(yaml.safe_dump({"descriptors": descriptors}))
    with pytest.raises(ValueError, match="pilot descriptor contract"):
        load_catalog(path)


def test_direct_validation_cannot_bypass_fraction_checks_with_remapped_inventory(catalog):
    p = protein()
    obs = by_code(bio.calculate(p))["B03"]
    obs["value"] = 2.0
    catalog = deepcopy(catalog)
    catalog[obs["descriptor_id"]]["inventory_id"] = "B99"
    assert any("pilot descriptor contract" in e for e in errors(obs, p, catalog))


@pytest.mark.parametrize("code", ["B01", "B22"])
@pytest.mark.parametrize("status", ["OK", "NOT_AVAILABLE"])
def test_pilot_calculations_cannot_be_relabeled_experimental(catalog, code, status):
    p = protein()
    obs = by_code(bio.calculate(p, disorder=prediction(p, [0.7] * p["sequence_length"])))[code]
    if status != "OK":
        for key in ("value", "profile", "intervals"):
            obs.pop(key, None)
        obs.update(status=status, missing_reason="Synthetic missing result")
    obs["evidence_mode"] = "EXPERIMENT"
    assert any("evidence mode" in e for e in errors(obs, p, catalog))


@pytest.mark.parametrize("name", ["mode", "prediction_context"])
def test_populated_disorder_requires_predictor_mode_and_context(catalog, name):
    p = protein()
    obs = by_code(bio.calculate(p, disorder=prediction(p, [0.7] * p["sequence_length"])))["B22"]
    obs["method"]["parameters"] = [param for param in obs["method"]["parameters"] if param["name"] != name]
    assert any("predictor mode and full-sequence context" in e for e in errors(obs, p, catalog))


def test_cli_is_idempotent_and_dry_run_by_default(tmp_path, catalog, capsys):
    p = protein()
    reg = tmp_path / "registry.jsonl"
    reg.write_text(json.dumps(p) + "\n")
    out = tmp_path / "observations.jsonl"
    args = ["--registry", str(reg), "--output", str(out)]
    assert main(args) == 0
    assert not out.exists()
    assert main(args + ["--apply"]) == 0
    before = out.read_bytes()
    assert main(args + ["--apply"]) == 0
    assert out.read_bytes() == before
    rows = [json.loads(line) for line in out.read_text().splitlines()]
    assert validate_collection(rows, load_registry(reg), catalog) == []
    # Reject bad input without replacing the last validated output.
    p["sequence_sha256"] = "0" * 64
    reg.write_text(json.dumps(p) + "\n")
    assert main(args + ["--apply"]) == 1
    assert out.read_bytes() == before


def map_inputs():
    p = protein()
    meta = dict(model="test-model", revision="pinned", pooling="mean", window=1022, overlap=256)
    data = dict(embedding=meta, points=[[0.2, 0.3, 0, p["protein_id"]]])
    embedded = [dict(accession=p["protein_id"], length=p["sequence_length"], sequence_sha256=p["sequence_sha256"])]
    return p, data, embedded, meta


def test_overlay_preserves_coordinates_and_zero_values(catalog):
    p, data, embedded, meta = map_inputs()
    before = deepcopy(data)
    overlay = build_overlay(data, embedded, meta, bio.calculate(p), catalog)
    assert data == before
    assert len(overlay["series"]) == 9
    assert next(s for s in overlay["series"] if s["descriptor_id"].endswith("B22"))["available"] == 0


def test_overlay_accepts_zero_embedding_overlap_but_not_missing_overlap(catalog):
    p, data, embedded, meta = map_inputs()
    meta["overlap"] = 0
    assert build_overlay(data, embedded, meta, bio.calculate(p), catalog)["map_proteins"] == 1
    del meta["overlap"]
    with pytest.raises(ValueError, match="overlap"):
        build_overlay(data, embedded, meta, bio.calculate(p), catalog)


def test_overlay_rejects_stale_sequence_or_mixed_conditions(catalog):
    p, data, embedded, meta = map_inputs()
    observations = bio.calculate(p)
    embedded[0]["sequence_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="embedded sequence"):
        build_overlay(data, embedded, meta, observations, catalog)
    embedded[0]["sequence_sha256"] = p["sequence_sha256"]
    with pytest.raises(ValueError, match="incompatible methods"):
        build_overlay(data, embedded, meta, observations + bio.calculate(p, ph=6), catalog)
    with pytest.raises(ValueError, match="revision"):
        build_overlay(data, embedded, {**meta, "revision": "different"}, observations, catalog)


@pytest.mark.parametrize("missing_first", [True, False])
def test_overlay_accepts_partial_disorder_coverage_but_rejects_mixed_predictors(catalog, missing_first):
    missing, data, embedded, meta = map_inputs()
    available = protein(protein_id="UniProtKB:P12346")
    data["points"].append([0.4, 0.5, 0, available["protein_id"]])
    embedded.append(dict(accession=available["protein_id"], length=available["sequence_length"],
                         sequence_sha256=available["sequence_sha256"]))
    predicted = bio.calculate(available, disorder=prediction(available, [0.7] * available["sequence_length"]))
    unavailable = bio.calculate(missing)
    observations = unavailable + predicted if missing_first else predicted + unavailable
    registry = {p["protein_id"]: p for p in (missing, available)}
    assert validate_collection(observations, registry, catalog) == []
    overlay = build_overlay(data, embedded, meta, observations, catalog)
    disorder = next(s for s in overlay["series"] if s["descriptor_id"].endswith("B22"))
    assert disorder["available"] == 1
    assert disorder["values"][missing["protein_id"]]["status"] == "NOT_AVAILABLE"
    assert disorder["values"][available["protein_id"]]["value"] == 1.0
    assert disorder["method"]["name"] == "SyntheticPredictorFixture"
    assert disorder["method"]["version"] == "test-1"
    incompatible = prediction(missing, [0.8] * missing["sequence_length"])
    incompatible["version"] = "test-2"
    with pytest.raises(ValueError, match="incompatible methods"):
        build_overlay(data, embedded, meta, bio.calculate(missing, disorder=incompatible) + predicted, catalog)


def test_browser_numeric_filter_includes_zero_and_excludes_missing():
    import shutil
    if not shutil.which("node"):
        pytest.skip("Node.js required for browser helper checks")
    script = """
    const assert=require('node:assert/strict');
    const b=require('./docs/biophysical-map.js');
    const series={minimum:-1,maximum:1,values:{zero:{status:'OK',value:0},
      missing:{status:'NOT_AVAILABLE',value:null},low:{status:'OK',value:-1}}};
    assert.equal(b.value(series,'zero'),0);
    assert.equal(b.value(series,'absent'),null);
    assert.equal(b.passes(series,'zero',0,0,true),true);
    assert.equal(b.passes(series,'low',0,null,true),false);
    assert.equal(b.passes(series,'missing',null,null,false),true);
    assert.equal(b.passes(series,'missing',0,null,false),false);
    assert.equal(b.passes(series,'missing',null,null,true),false);
    assert.equal(b.color(series,'missing'),'#999999');
    assert.notEqual(b.color(series,'zero'),b.color(series,'low'));
    """
    subprocess.run(["node", "-e", script], cwd=ROOT, check=True)


def test_pato_hydrophilicity_sibling_route_and_written_records():
    from seed_obo import SOURCES, build_routing
    from validate_strict import validate_one
    source = SOURCES["pato"]
    entries = [{"id": "PATO:0001884"}, {"id": "PATO:0001886"},
               {"id": "PATO:0001887", "is_a": ["PATO:0001886"]}]
    routed = build_routing(entries, source)
    assert routed["PATO:0001886"].root == "PATO:0001886"
    for filename in ("hydrophilicity-pato0001886.yaml", "hydrophilic-pato0001887.yaml"):
        path = ROOT / "data/traits/structure/surface/pato" / filename
        record = yaml.safe_load(path.read_text())
        assert record["term_kind"] == "CLASS"
        assert record["mapping_status"] == "SEEDED"
        assert record["license"] == "CC-BY-4.0"
        assert validate_one(path) == []


def test_redundancy_analysis_handles_ties_constants_and_mixed_methods(catalog):
    from analyze_biophysical import spearman, summarize
    assert spearman([1, 1, 3, 4], [4, 4, 2, 1]) == pytest.approx(-1)
    assert spearman([1, 1, 1, 1], [1, 2, 3, 4]) is None
    assert spearman([1, 2, 3], [1, 2, 3]) is None
    p = protein()
    observations = bio.calculate(p)
    report = summarize(observations, {p["protein_id"]: p}, catalog)
    assert report["fcr_identity"]["maximum_absolute_error"] == pytest.approx(0)
    assert "source:UniProtKB:2026_03" in report["strata"]
    second = protein(protein_id="UniProtKB:P12346")
    with pytest.raises(ValueError, match="different methods"):
        summarize(observations + bio.calculate(second, ph=6),
                  {p["protein_id"]: p, second["protein_id"]: second}, catalog)


def test_output_suffix_cannot_overwrite_jsonl_with_summary(tmp_path, capsys):
    output = tmp_path / "bad.tsv"
    assert main(["--output", str(output), "--apply"]) == 1
    assert not output.exists()
