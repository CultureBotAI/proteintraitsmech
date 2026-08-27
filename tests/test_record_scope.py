from __future__ import annotations

import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from record_scope import records_in_source_directories  # noqa: E402


def _record(root: pathlib.Path, relative: str) -> pathlib.Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("identifier: Test:1\n", encoding="utf-8")
    return path


def test_it_only_walks_selected_source_directories(tmp_path):
    wanted = _record(tmp_path, "sequence/domain/pfam/wanted.yaml")
    _record(tmp_path, "sequence/domain/interpro/not-wanted.yaml")
    _record(tmp_path, "function/activity/direct-record.yaml")

    assert list(records_in_source_directories(tmp_path, {"pfam"})) == [wanted]


def test_it_supports_nested_records_and_multiple_axes(tmp_path):
    first = _record(tmp_path, "function/family/sfld/nested/one.yaml")
    second = _record(tmp_path, "sequence/family/sfld/two.yaml")

    assert list(records_in_source_directories(tmp_path, {"sfld"})) == [first, second]


def test_missing_root_or_empty_scope_yields_nothing(tmp_path):
    assert list(records_in_source_directories(tmp_path / "missing", {"pfam"})) == []
    assert list(records_in_source_directories(tmp_path, set())) == []


def test_a_broken_symlink_aborts_rather_than_being_skipped(tmp_path):
    """Fail loud, not fail open (#538).

    `is_file()` is False for a broken symlink, so skipping it quietly turned an
    aborting check into one that reports DISAGREE: 0 and exits 0 — the same shape as
    #534, one directory down.
    """
    source = tmp_path / "sequence" / "domain" / "pfam"
    source.mkdir(parents=True)
    (source / "real.yaml").write_text("id: x\n", encoding="utf-8")
    (source / "broken.yaml").symlink_to(tmp_path / "nowhere")
    with pytest.raises(OSError, match="not a readable regular file"):
        list(records_in_source_directories(tmp_path, ["pfam"]))


def test_a_directory_named_yaml_aborts_rather_than_being_skipped(tmp_path):
    source = tmp_path / "sequence" / "domain" / "pfam"
    source.mkdir(parents=True)
    (source / "trap.yaml").mkdir()
    with pytest.raises(OSError, match="not a readable regular file"):
        list(records_in_source_directories(tmp_path, ["pfam"]))
