from __future__ import annotations

import pathlib
import sys

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
