from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import sys

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
