from __future__ import annotations

import importlib.util
import json
import pathlib
import shutil
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "corpus_stats.py"


def _load():
    spec = importlib.util.spec_from_file_location("corpus_stats", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


STATS = _load()


def _write(root: pathlib.Path, name: str, text: str) -> None:
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_collects_record_axis_status_graph_and_artifact_metrics(tmp_path):
    traits = tmp_path / "traits"
    docs = tmp_path / "docs-data"
    _write(traits, "sequence/domain/a.yaml", "trait_axis: SEQUENCE\nmapping_status: SEEDED\n")
    _write(
        traits,
        "evolution/scope/b.yaml",
        "trait_axis: EVOLUTION\nmapping_status: REVIEWED\ncausal_graphs:\n"
        "  - graph_id: one\n  - graph_id: two\n",
    )
    _write(traits, "sequence_structure/repeat/c.yaml", "trait_axis: SEQUENCE_STRUCTURE\n")
    _write(docs, "records.SEQUENCE.json", "[]\n")
    _write(docs, "detail/000.json", "{}\n")

    got = STATS.collect_stats(traits, docs, workers=2)

    assert got["corpus"] == {
        "records": 3,
        "by_axis": {"EVOLUTION": 1, "SEQUENCE": 1, "SEQUENCE_STRUCTURE": 1},
        "by_mapping_status": {"REVIEWED": 1, "SEEDED": 1, "_MISSING": 1},
        "records_with_causal_graphs": 1,
        "causal_graphs": 2,
    }
    assert got["artifacts"]["docs_data"] == {
        "json_files": 2,
        "bytes": 6,
        "record_shards": 1,
        "largest_record_shard_bytes": 3,
        "detail_buckets": 1,
        "detail_bytes": 3,
        "largest_detail_bucket_bytes": 3,
    }


def test_cli_writes_machine_readable_json_atomically(tmp_path):
    traits = tmp_path / "traits"
    traits.mkdir()
    destination = tmp_path / "reports" / "corpus.json"
    out = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--traits",
            str(traits),
            "--docs-data",
            str(tmp_path / "missing-docs"),
            "--output",
            str(destination),
        ],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    assert out.returncode == 0, out.stderr
    assert json.loads(destination.read_text(encoding="utf-8"))["schema_version"] == 1
    assert not destination.with_suffix(".json.tmp").exists()


def test_streaming_rg_aggregation_matches_python_first_field_semantics(tmp_path):
    traits = tmp_path / "traits"
    _write(
        traits,
        "duplicate.yaml",
        "trait_axis: SEQUENCE\ntrait_axis: STRUCTURE\n"
        "mapping_status: SEEDED\nmapping_status: REVIEWED\n"
        "causal_graphs:\n  - graph_id: one\ncausal_graphs:\n  - graph_id: two\n",
    )
    _write(traits, "missing.yaml", "identifier: Test:missing\n")
    lines = [
        b"duplicate.yaml\0trait_axis: SEQUENCE\n",
        b"duplicate.yaml\0trait_axis: STRUCTURE\n",
        b"duplicate.yaml\0mapping_status: SEEDED\n",
        b"duplicate.yaml\0mapping_status: REVIEWED\n",
        b"duplicate.yaml\0causal_graphs:\n",
        b"duplicate.yaml\0  - graph_id: one\n",
        b"duplicate.yaml\0causal_graphs:\n",
        b"duplicate.yaml\0  - graph_id: two\n",
    ]

    streamed = STATS._metrics_from_rg_lines(lines, records=2)
    fallback = STATS._corpus_metrics_python(traits, workers=1)

    assert streamed == fallback
    assert streamed["by_axis"] == {"SEQUENCE": 1, "_MISSING": 1}
    assert streamed["by_mapping_status"] == {"SEEDED": 1, "_MISSING": 1}
    assert streamed["records_with_causal_graphs"] == 1
    assert streamed["causal_graphs"] == 2


def _adversarial_tree(root: pathlib.Path) -> pathlib.Path:
    """A tree whose files the two backends could disagree about (#539).

    One ordinary record, one carrying a NUL byte (binary to ripgrep, ordinary to
    `os.walk`), and one under a dotted directory (skipped by ripgrep's defaults,
    walked by `rglob`). The written test before this one fed ripgrep's output in
    by hand, so it compared the two *aggregations* and could never see a
    disagreement about which files exist.
    """
    traits = root / "traits"
    _write(traits, "plain/ok.yaml", "trait_axis: SEQUENCE\nmapping_status: SEEDED\n")
    _write(
        traits,
        ".hidden/h.yaml",
        "trait_axis: FUNCTION\nmapping_status: PROPOSED\n"
        "causal_graphs:\n  - graph_id: one\n  - graph_id: two\n",
    )
    (traits / "plain" / "nul.yaml").write_bytes(
        b"trait_axis: STRUCTURE\nmapping_status: REVIEWED\n\x00binary\n"
    )
    # A symlinked record, which `is_file()` follows and ripgrep does not (#627).
    outside = root / "outside"
    outside.mkdir(parents=True, exist_ok=True)
    (outside / "linked.yaml").write_text(
        "trait_axis: EVOLUTION\nmapping_status: SEEDED\n", encoding="utf-8"
    )
    (traits / "plain" / "link.yaml").symlink_to(outside / "linked.yaml")
    return traits


def test_both_backends_agree_on_a_tree_designed_to_split_them(tmp_path):
    """Runs the REAL ripgrep, which is the half the existing test cannot reach.

    Measured before the fix: ripgrep saw 2 of 4 records and filed the other two
    as `_MISSING`, because a NUL byte makes a record binary to it and dotted
    directories are skipped by default. `rglob` consults neither rule.
    """
    if shutil.which("rg") is None:
        pytest.skip("ripgrep is absent here, so there is no second backend to compare")
    traits = _adversarial_tree(tmp_path)

    streamed = STATS._corpus_metrics_rg(traits)
    fallback = STATS._corpus_metrics_python(traits, workers=1)

    assert streamed == fallback, f"backends disagree\n  rg     {streamed}\n  python {fallback}"
    assert "_MISSING" not in streamed["by_axis"]
    assert streamed["by_axis"] == {"FUNCTION": 1, "SEQUENCE": 1, "STRUCTURE": 1}


def test_the_python_backend_runs_when_ripgrep_is_absent(tmp_path, monkeypatch):
    """`collect_stats` short-circuits on ripgrep, so the fallback never ran here.

    Two mutations survived the suite as written -- `"records": len(paths)` to a
    constant, and `graphs += graph_count` to `+= 0` -- because every test took the
    ripgrep path. Forcing `shutil.which` to None is what makes the fallback
    executable code as far as the suite is concerned.
    """
    traits = _adversarial_tree(tmp_path)
    monkeypatch.setattr(STATS.shutil, "which", lambda _name: None)

    assert STATS._corpus_metrics_rg(traits) is None
    stats = STATS.collect_stats(traits, tmp_path / "no-docs", workers=1)["corpus"]

    assert stats["records"] == 3
    assert stats["by_axis"] == {"FUNCTION": 1, "SEQUENCE": 1, "STRUCTURE": 1}
    assert stats["by_mapping_status"] == {"PROPOSED": 1, "REVIEWED": 1, "SEEDED": 1}
    # Named explicitly in #539 as a mutation the suite could not kill, because no
    # test ever reached this backend: `graphs += graph_count` to `+= 0` survived.
    assert stats["causal_graphs"] == 2
    assert stats["records_with_causal_graphs"] == 1


def test_a_scan_attributing_more_records_than_exist_is_an_error():
    """The `if missing > 0` guard dropped a negative silently (#539).

    A negative means the scan and the file count disagree about which files
    exist, which is the one thing a numbers tool must not round away.
    """
    lines = [
        b"a.yaml\0trait_axis: SEQUENCE\n",
        b"b.yaml\0trait_axis: STRUCTURE\n",
    ]
    with pytest.raises(ValueError, match="more axes than the 1 files counted"):
        STATS._metrics_from_rg_lines(lines, records=1)


def test_symlinked_records_are_excluded_by_every_selection_path(tmp_path):
    """`--follow` would have been the obvious fix and is the wrong one (#627).

    `is_file()` follows a symlinked record and reads it; ripgrep does not follow
    symlinks at all, so it filed one as `_MISSING`. But `--follow` descends
    symlinked *directories* too and matched 3 files against a count of 2 on a
    fixture tree, which trips the negative-discrepancy check -- a loud overcount
    traded for a silent undercount.

    Excluding them instead matches what the repository already requires: several
    stage scripts reject a symlink below the trait directory outright, and the
    corpus holds none.
    """
    traits = _adversarial_tree(tmp_path)
    assert (traits / "plain" / "link.yaml").is_symlink()

    assert STATS._record_count(traits) == 3
    fallback = STATS._corpus_metrics_python(traits, workers=1)
    assert fallback["records"] == 3
    assert "EVOLUTION" not in fallback["by_axis"], "a symlinked record was counted"

    if shutil.which("rg") is not None:
        assert STATS._corpus_metrics_rg(traits) == fallback
