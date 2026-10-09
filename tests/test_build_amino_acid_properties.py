"""Chemistry source replay must fail closed before publication."""
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import amino_acid_properties as chemistry
import build_amino_acid_properties as builder


@pytest.fixture
def snapshot(tmp_path):
    rows = []
    for name, (url, license_name, license_url) in builder.CONTRACT.items():
        raw = ("synthetic source " + name).encode()
        (tmp_path / name).write_bytes(raw)
        rows.append(dict(path=name, requested_url=url, license=license_name, license_url=license_url,
                         sha256=chemistry.digest(raw), bytes=len(raw)))
    manifest = dict(kind="AMINO_ACID_PROPERTY_SNAPSHOT", schema_version=1, artifacts=rows)
    (tmp_path / "manifest.json").write_text(json.dumps(manifest))
    return tmp_path


def test_snapshot_membership_and_hash_verification(snapshot):
    inputs, receipts = builder.snapshot_inputs(snapshot)
    assert len(inputs) == len(receipts) == 22
    (snapshot / "SER.cif").write_text("corrupted")
    with pytest.raises(ValueError, match="checksum/size"):
        builder.snapshot_inputs(snapshot)


@pytest.mark.parametrize("mutation", [
    lambda m: m["artifacts"].pop(),
    lambda m: m["artifacts"].append(m["artifacts"][0]),
    lambda m: m["artifacts"][0].update(path="../escape"),
    lambda m: m["artifacts"][0].update(requested_url="https://example.org/impostor"),
    lambda m: m["artifacts"][0].update(license="unknown"),
    lambda m: m.update(kind="OTHER"),
])
def test_invalid_snapshot_contract(snapshot, mutation):
    path = snapshot / "manifest.json"
    data = json.loads(path.read_text())
    mutation(data)
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        builder.snapshot_inputs(snapshot)


def test_symlinked_input_rejected_even_with_matching_bytes(snapshot):
    original = snapshot / "SER.cif"
    target = snapshot / "copy.cif"
    original.rename(target)
    original.symlink_to(target)
    with pytest.raises(ValueError, match="symlinked"):
        builder.snapshot_inputs(snapshot)


@pytest.mark.parametrize("mode", ["--apply", "--check"])
def test_publication_requires_explicit_review(snapshot, mode, capsys):
    assert builder.main(["--snapshot", str(snapshot), mode]) == 1
    assert "requires an explicit reviewed-content file" in capsys.readouterr().err


def test_writer_validates_review_and_refuses_symlinks(tmp_path, monkeypatch):
    catalog = json.loads(chemistry.CATALOG.read_text())
    destination = tmp_path / "catalog.json"
    monkeypatch.setattr(builder, "OUTPUT", destination)
    builder.write_catalog(catalog)
    assert json.loads(destination.read_text()) == catalog
    destination.unlink()
    destination.symlink_to(tmp_path / "outside.json")
    with pytest.raises(ValueError, match="symlinked"):
        builder.write_catalog(catalog)
    catalog.pop("review")
    with pytest.raises(ValueError, match="source-transcription review"):
        builder.write_catalog(catalog)


def test_catalog_cli(capsys):
    assert chemistry.main([]) == 0
    assert json.loads(capsys.readouterr().out)["residue_count"] == 20
