"""The scanner exposes diagnostic scope without claiming scientific review."""

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_scan_reports_skipped_inputs_and_display_limit(tmp_path, monkeypatch, capsys):
    spec = importlib.util.spec_from_file_location(
        "review_source_categories", ROOT / "scripts/review_source_categories.py"
    )
    scanner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(scanner)
    traits = tmp_path / "data/traits"
    traits.mkdir(parents=True)
    for index in range(2):
        (traits / f"record-{index}.yaml").write_text(
            f"identifier: EX:{index}\ntrait_axis: FUNCTION\ntrait_category: SEQ_DOMAIN\n"
        )
    (traits / "broken.yaml").write_text("[unterminated")
    (traits / "empty.yaml").write_text("null\n")
    monkeypatch.setattr(scanner, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(scanner, "TRAITS", traits)
    monkeypatch.setattr(scanner.bd, "infer_source", lambda *_: "Fixture")
    monkeypatch.setattr("sys.argv", ["review_source_categories.py", "--show", "1"])
    assert scanner.main() == 0
    output = capsys.readouterr().out
    assert "scientific_review: false" in output
    assert "display limit: 1 per flag; skipped inputs: 2" in output
    assert "1 sources scanned; 2 total flag occurrences" in output
    assert "sources reviewed" not in output
    assert output.count("data/traits/record-") == 1
