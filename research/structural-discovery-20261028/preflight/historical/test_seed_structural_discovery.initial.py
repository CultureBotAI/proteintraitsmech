"""New-class writer safety: ignored collisions, validation and preservation."""

from __future__ import annotations

import copy
from pathlib import Path
import sys

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from seed_structural_discovery import seed  # noqa: E402


@pytest.fixture
def batch(tmp_path):
    records = []
    for suffix in ("ONE", "TWO"):
        records.append({
            "path": f"data/traits/structure/secondary/discovery-{suffix.lower()}.yaml",
            "record": {
                "identifier": f"proteintraitsmech:TEST_DISCOVERY_{suffix}",
                "label": f"test discovery {suffix}",
                "definition": "Synthetic writer safety fixture, not a scientific assertion.",
                "definition_source": "test fixture",
                "trait_axis": "STRUCTURE", "trait_category": "STRUCT_SECONDARY",
                "term_kind": "CLASS", "mapping_status": "PROPOSED", "license": "CC0-1.0",
                "evidence": [{"reference": "test fixture"}],
                "detection_methods": [{"name": "Fixture command", "recipe": "fixture {input}"}],
            },
        })
    manifest = tmp_path / "manifest.yaml"
    manifest.write_text(yaml.safe_dump({"version": 1, "records": records}))
    (tmp_path / "data/traits").mkdir(parents=True)
    return tmp_path, manifest, records


def test_dry_run_is_nonmutating_and_apply_is_idempotent(batch):
    root, manifest, rows = batch
    report = seed(root=root, manifest=manifest)
    assert [r["action"] for r in report["records"]] == ["would_create", "would_create"]
    assert not list((root / "data/traits").rglob("*.yaml"))
    seed(root=root, manifest=manifest, apply=True)
    before = [(root / r["path"]).read_bytes() for r in rows]
    report = seed(root=root, manifest=manifest, apply=True)
    assert [r["action"] for r in report["records"]] == ["unchanged", "unchanged"]
    assert [(root / r["path"]).read_bytes() for r in rows] == before


def test_human_edit_prevents_entire_batch_and_is_preserved(batch):
    root, manifest, rows = batch
    seed(root=root, manifest=manifest, only=rows[0]["record"]["identifier"], apply=True)
    first = root / rows[0]["path"]
    edited = first.read_text() + "# human annotation\n"
    first.write_text(edited)
    with pytest.raises(ValueError, match="refusing replacement"):
        seed(root=root, manifest=manifest, apply=True)
    assert first.read_text() == edited
    assert not (root / rows[1]["path"]).exists()


@pytest.mark.parametrize("field", ["identifier", "xrefs"])
def test_ignored_hidden_identity_collision_stops_creation(batch, field):
    root, manifest, rows = batch
    (root / ".gitignore").write_text("data/traits/.staged/\n")
    other = root / "data/traits/.staged/other.yaml"
    other.parent.mkdir()
    rec = copy.deepcopy(rows[0]["record"])
    if field == "xrefs":
        rec["xrefs"] = [rec["identifier"]]
        rec["identifier"] = "proteintraitsmech:OTHER"
    other.write_text(yaml.safe_dump(rec))
    before = other.read_bytes()
    with pytest.raises(ValueError, match="already present in another record"):
        seed(root=root, manifest=manifest, apply=True)
    assert other.read_bytes() == before
    assert all(not (root / r["path"]).exists() for r in rows)


def test_late_schema_error_leaves_all_destinations_absent(batch):
    root, manifest, rows = batch
    rows[1]["record"]["unknown_discovery_field"] = "must fail closed"
    manifest.write_text(yaml.safe_dump({"version": 1, "records": rows}))
    with pytest.raises(ValueError, match="Strict validation refused"):
        seed(root=root, manifest=manifest, apply=True)
    assert all(not (root / r["path"]).exists() for r in rows)


def test_path_traversal_cannot_escape_owned_corpus(batch):
    root, manifest, rows = batch
    rows[1]["path"] = "data/traits/structure/../../../outside.yaml"
    manifest.write_text(yaml.safe_dump({"version": 1, "records": rows}))
    with pytest.raises(ValueError, match="Unsafe"):
        seed(root=root, manifest=manifest, apply=True)
    assert not (root / "outside.yaml").exists()
    assert not (root / rows[0]["path"]).exists()


def test_human_review_status_cannot_be_minted(batch):
    root, manifest, rows = batch
    rows[0]["record"]["mapping_status"] = "REVIEWED"
    manifest.write_text(yaml.safe_dump({"version": 1, "records": rows}))
    with pytest.raises(ValueError, match="class/axis/status"):
        seed(root=root, manifest=manifest, apply=True)


def test_unknown_canary_identifier_is_an_error(batch):
    root, manifest, _ = batch
    with pytest.raises(ValueError, match="Unknown selected candidate"):
        seed(root=root, manifest=manifest, only="proteintraitsmech:NOT_SELECTED", apply=True)
