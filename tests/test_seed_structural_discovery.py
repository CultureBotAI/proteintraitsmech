"""New-class writer safety: ignored collisions, validation and preservation."""

from __future__ import annotations

import copy
import os
from pathlib import Path
import sys

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from seed_structural_discovery import check_report_destination, seed  # noqa: E402
import seed_structural_discovery as discovery  # noqa: E402


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


@pytest.mark.parametrize("field", ["identifier", "xrefs"])
def test_yaml_escaped_identity_is_parsed_before_collision_decision(batch, field):
    root, manifest, rows = batch
    identifier = rows[0]["record"]["identifier"]
    other = root / "data/traits/escaped.yaml"
    escaped = identifier.replace("TEST", r"\x54EST")
    if field == "identifier":
        other.write_text(f'identifier: "{escaped}"\n')
    else:
        other.write_text(f'identifier: proteintraitsmech:OTHER\nxrefs: ["{escaped}"]\n')
    with pytest.raises(ValueError, match="already present in another record"):
        seed(root=root, manifest=manifest, apply=True)
    assert all(not (root / r["path"]).exists() for r in rows)


def test_crlf_is_not_claimed_as_byte_identical_replay(batch):
    root, manifest, rows = batch
    seed(root=root, manifest=manifest, only=rows[0]["record"]["identifier"], apply=True)
    first = root / rows[0]["path"]
    crlf = first.read_bytes().replace(b"\n", b"\r\n")
    first.write_bytes(crlf)
    with pytest.raises(ValueError, match="refusing replacement"):
        seed(root=root, manifest=manifest, apply=True)
    assert first.read_bytes() == crlf
    assert not (root / rows[1]["path"]).exists()


def test_report_cannot_overwrite_trait_manifest_or_existing_evidence(batch):
    root, manifest, rows = batch
    evidence = root / "research/structural-discovery-20261028/existing.json"
    evidence.parent.mkdir(parents=True)
    evidence.write_text('{"retain": true}\n')
    for path in [root / rows[0]["path"], manifest, evidence]:
        with pytest.raises(ValueError, match="Report must be a new"):
            check_report_destination(path, root)
    check_report_destination(evidence.parent / "new.json", root)
    assert evidence.read_text() == '{"retain": true}\n'


def test_report_symlink_cannot_escape_owned_evidence(batch):
    root, _, _ = batch
    folder = root / "research/structural-discovery-20261028"
    folder.mkdir(parents=True)
    (folder / "escape").symlink_to(root / "data/traits", target_is_directory=True)
    with pytest.raises(ValueError, match="Report must be a new"):
        check_report_destination(folder / "escape/new.json", root)


@pytest.mark.parametrize("recipe", [None, True, 7, [], {}, "", " \n", "# explanation\n # only"])
def test_non_executable_recipe_in_late_row_prevents_entire_batch(batch, recipe):
    root, manifest, rows = batch
    rows[1]["record"]["detection_methods"][0]["recipe"] = recipe
    manifest.write_text(yaml.safe_dump({"version": 1, "records": rows}))
    with pytest.raises(ValueError, match="executable detection recipe"):
        seed(root=root, manifest=manifest, apply=True)
    assert all(not (root / row["path"]).exists() for row in rows)


def test_recipe_with_comment_header_and_command_is_accepted(batch):
    root, manifest, rows = batch
    rows[0]["record"]["detection_methods"][0]["recipe"] = "# Fixture\nfixture {input}"
    manifest.write_text(yaml.safe_dump({"version": 1, "records": rows}))
    result = seed(root=root, manifest=manifest, apply=True)
    assert all(row["action"] == "created" for row in result["records"])


@pytest.mark.parametrize("identifier", ["UniProtKB:P12345", "uniprotkb:P12345"])
def test_primary_protein_carrier_in_late_row_prevents_entire_batch(batch, identifier):
    root, manifest, rows = batch
    rows[1]["record"]["identifier"] = identifier
    manifest.write_text(yaml.safe_dump({"version": 1, "records": rows}))
    with pytest.raises(ValueError, match="carriers cannot"):
        seed(root=root, manifest=manifest, apply=True)
    assert all(not (root / row["path"]).exists() for row in rows)


def test_wrong_category_directory_in_late_row_prevents_entire_batch(batch):
    root, manifest, rows = batch
    rows[1]["record"]["trait_category"] = "STRUCT_CAVITY"
    manifest.write_text(yaml.safe_dump({"version": 1, "records": rows}))
    with pytest.raises(ValueError, match="category/path mismatch"):
        seed(root=root, manifest=manifest, apply=True)
    assert all(not (root / row["path"]).exists() for row in rows)


@pytest.mark.parametrize("bad_parent", ["owned_root_symlink", "file_parent", "internal_symlink", "unwritable_parent"])
def test_cli_refuses_bad_report_ancestry_before_seeding(batch, monkeypatch, bad_parent):
    root, manifest, rows = batch
    if bad_parent == "unwritable_parent" and (not hasattr(os, "geteuid") or os.geteuid() == 0):
        pytest.skip("Requires an unprivileged POSIX user to exercise directory permissions")
    folder = root / "research/structural-discovery-20261028"
    folder.parent.mkdir()
    protected = root / "retained-evidence.json"
    protected.write_text('{"retain": true}\n')
    if bad_parent == "owned_root_symlink":
        folder.symlink_to(root / "data/traits", target_is_directory=True)
        output = folder / "new.json"
    else:
        folder.mkdir()
        if bad_parent == "file_parent":
            (folder / "parent").write_text("existing evidence\n")
        elif bad_parent == "internal_symlink":
            (folder / "real").mkdir()
            (folder / "parent").symlink_to(folder / "real", target_is_directory=True)
        else:
            (folder / "parent").mkdir(mode=0o555)
        output = folder / "parent/new.json"
    calls = []

    def seed_fixture(**kwargs):
        calls.append(kwargs)
        return seed(root=root, manifest=manifest, **kwargs)

    monkeypatch.setattr(discovery, "check_report_destination",
                        lambda path: check_report_destination(path, root))
    monkeypatch.setattr(discovery, "seed", seed_fixture)
    monkeypatch.setattr(sys, "argv", ["seed_structural_discovery.py", "--apply", "--report", str(output)])
    try:
        with pytest.raises((ValueError, PermissionError)):
            discovery.main()
    finally:
        if bad_parent == "unwritable_parent":
            (folder / "parent").chmod(0o755)
    assert calls == []
    assert all(not (root / row["path"]).exists() for row in rows)
    assert not output.exists()
    assert protected.read_text() == '{"retain": true}\n'
    if bad_parent == "file_parent":
        assert (folder / "parent").read_text() == "existing evidence\n"
