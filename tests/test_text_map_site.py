"""Publication requires an explicit switch and current validated full inputs."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from proteintraitsmech import text_map_site as site


def configure(root: Path, value="false"):
    config = root / "conf" / "text_map.yaml"
    config.parent.mkdir(parents=True, exist_ok=True)
    config.write_text(f"enabled: {value}\n")


def fake_pipeline():
    calls = []
    profile = {
        "model": "BAAI/bge-large-en-v1.5",
        "revision": "d4aa6901d3a41ba39fb536a557fa166f842b0e09",
        "dimension": 1024,
    }
    manifest = {"encoder": profile, "projection": {"implementation": "pacmap.PaCMAP"}}

    def validate(bundle, *, input_path):
        assert json.loads(input_path.read_text()) == {"test": "fresh full inputs"}
        calls.append(("validate", bundle, input_path))
        return manifest

    def stage(output, published_dir, *, input_path):
        assert json.loads(input_path.read_text()) == {"test": "fresh full inputs"}
        calls.append(("stage", output, published_dir))
        return manifest

    pipeline = SimpleNamespace(
        MODEL=profile["model"],
        MODEL_REVISION=profile["revision"],
        MODEL_DIMENSION=1024,
        current_bundle=lambda output: output / "fixture-bundle",
        validate_bundle=validate,
        stage_map=stage,
    )
    return pipeline, calls, manifest


def enable_fixture(root, monkeypatch):
    configure(root, "true")
    source = root / "data" / "text_map"
    source.mkdir(parents=True)
    (source / "current.json").write_text("{}")
    pipeline, calls, manifest = fake_pipeline()
    monkeypatch.setattr(site, "load_pipeline", lambda _root: pipeline)

    def export(actual_root, output, **kwargs):
        assert actual_root == root
        assert not kwargs, "publication cannot request a canary or limited input set"
        output.write_text(json.dumps({"test": "fresh full inputs"}))
        return {"scope": "full"}

    monkeypatch.setattr(site, "export_inputs", export)
    return pipeline, calls, manifest


def test_disabled_map_requires_no_runtime_or_artifact(tmp_path, monkeypatch):
    configure(tmp_path)
    monkeypatch.setattr(
        site, "load_pipeline", lambda _root: pytest.fail("disabled map loaded runtime")
    )
    with site.prepare_text_map(tmp_path) as ready:
        assert ready is None


def test_enabled_map_missing_bundle_fails(tmp_path):
    configure(tmp_path, "true")
    with pytest.raises(ValueError, match="current.json"), site.prepare_text_map(tmp_path):
        pass


def test_enabled_map_missing_shared_runtime_fails(tmp_path):
    configure(tmp_path, "true")
    source = tmp_path / "data" / "text_map"
    source.mkdir(parents=True)
    (source / "current.json").write_text("{}")
    with pytest.raises(ValueError, match="CLAW-governed"), site.prepare_text_map(tmp_path):
        pass


@pytest.mark.parametrize("value", ["1", "'true'", "null", "[]"])
def test_enablement_requires_an_actual_boolean(tmp_path, value):
    configure(tmp_path, value)
    with pytest.raises(ValueError, match="enabled boolean"), site.prepare_text_map(tmp_path):
        pass


def test_enabled_map_uses_fresh_full_inputs_and_canonical_stage(tmp_path, monkeypatch):
    _, calls, _ = enable_fixture(tmp_path, monkeypatch)
    with site.prepare_text_map(tmp_path) as ready:
        inputs = ready.inputs
        ready.stage(tmp_path / "published")
        assert calls[-1] == (
            "stage",
            tmp_path / "data" / "text_map",
            tmp_path / "published" / "text-map",
        )
    assert not inputs.exists()
    assert calls[0][0] == "validate"


def test_legacy_encoder_cannot_be_published_as_the_common_space(tmp_path, monkeypatch):
    _, _, manifest = enable_fixture(tmp_path, monkeypatch)
    manifest["encoder"] = {"model": "MiniLM", "revision": "0" * 40, "dimension": 384}
    with pytest.raises(ValueError, match="pinned fleet BGE"), site.prepare_text_map(tmp_path):
        pass


def test_injected_projector_cannot_reach_the_site_build(tmp_path, monkeypatch):
    _, _, manifest = enable_fixture(tmp_path, monkeypatch)
    manifest["projection"]["implementation"] = "injected-projector"
    with pytest.raises(ValueError, match="actual PaCMAP"), site.prepare_text_map(tmp_path):
        pass


def test_subset_receipt_cannot_reach_publication(tmp_path, monkeypatch):
    enable_fixture(tmp_path, monkeypatch)
    monkeypatch.setattr(site, "export_inputs", lambda _root, _output: {"scope": "subset"})
    with pytest.raises(ValueError, match="full-corpus"), site.prepare_text_map(tmp_path):
        pass
