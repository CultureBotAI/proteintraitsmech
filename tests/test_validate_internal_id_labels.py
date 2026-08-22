"""Tests for the corpus-internal id-label identity gate (#493)."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "validate_internal_id_labels.py"
spec = importlib.util.spec_from_file_location("validate_internal_id_labels", SCRIPT)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def _write(root: Path, rel: str, identifier: str, label: str, graph: str = "") -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"identifier: {identifier}\nlabel: {label}\ntrait_axis: FUNCTION\n{graph}",
        encoding="utf-8",
    )


def test_collect_checks_matching_mismatching_and_missing_internal_ids(tmp_path):
    _write(tmp_path, "canonical.yaml", "proteintraitsmech:A", "canonical A")
    graph = """causal_graphs:
  - graph_id: g
    nodes:
      - node_id: same
        label: Canonical   A
        grounding: proteintraitsmech:A
      - node_id: drift
        label: old A
        grounding: proteintraitsmech:A
      - node_id: missing
        label: unknown
        grounding: proteintraitsmech:MISSING
    edges: []
"""
    _write(tmp_path, "source.yaml", "X:1", "source", graph)

    rows, checked, records = gate.collect(tmp_path)

    assert records == 2
    assert checked == 3
    assert [row["node_id"] for row in rows] == ["drift", "missing"]
    assert rows[1]["canonical"] == "<ID NOT FOUND>"


def test_main_pins_count_and_identity_not_count_alone(tmp_path, capsys):
    _write(tmp_path, "canonical.yaml", "proteintraitsmech:A", "canonical A")
    graph = """causal_graphs:
  - graph_id: g
    nodes:
      - node_id: drift
        label: old A
        grounding: proteintraitsmech:A
    edges: []
"""
    _write(tmp_path, "source.yaml", "X:1", "source", graph)
    rows, checked, records = gate.collect(tmp_path)
    baseline = tmp_path / "baseline.yml"
    baseline.write_text(
        yaml.safe_dump(
            {
                "version": 1,
                "records": records,
                "checked_pairs": checked,
                "mismatches": len(rows),
                "sha256": gate.fingerprint(rows),
            }
        ),
        encoding="utf-8",
    )
    assert gate.main(["--path", str(tmp_path), "--baseline", str(baseline)]) == 0

    source = tmp_path / "source.yaml"
    source.write_text(source.read_text().replace("old A", "different A"))
    assert gate.main(["--path", str(tmp_path), "--baseline", str(baseline)]) == 1
    assert "baseline changed" in capsys.readouterr().out


def test_empty_scope_fails_closed(tmp_path):
    baseline = tmp_path / "baseline.yml"
    baseline.write_text(
        yaml.safe_dump(
            {
                "version": 1,
                "records": 0,
                "checked_pairs": 0,
                "mismatches": 0,
                "sha256": gate.fingerprint([]),
            }
        )
    )
    assert gate.main(["--path", str(tmp_path), "--baseline", str(baseline)]) == 1


def test_deleting_a_matching_pair_fails_even_when_mismatch_identity_is_unchanged(
    tmp_path,
):
    _write(tmp_path, "canonical.yaml", "proteintraitsmech:A", "canonical A")
    graph = """causal_graphs:
  - graph_id: g
    nodes:
      - node_id: drift
        label: old A
        grounding: proteintraitsmech:A
      - node_id: same
        label: canonical A
        grounding: proteintraitsmech:A
    edges: []
"""
    _write(tmp_path, "source.yaml", "X:1", "source", graph)
    rows, checked, records = gate.collect(tmp_path)
    baseline = tmp_path / "baseline.yml"
    baseline.write_text(
        yaml.safe_dump(
            {
                "version": 1,
                "records": records,
                "checked_pairs": checked,
                "mismatches": len(rows),
                "sha256": gate.fingerprint(rows),
            }
        )
    )
    source = tmp_path / "source.yaml"
    text = source.read_text()
    text = text.replace(
        "      - node_id: same\n"
        "        label: canonical A\n"
        "        grounding: proteintraitsmech:A\n",
        "",
    )
    source.write_text(text)

    assert gate.main(["--path", str(tmp_path), "--baseline", str(baseline)]) == 1
