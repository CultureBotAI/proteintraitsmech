"""Focused tests for InterPro compact/grouped sidecar extraction."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "fetch_interpro_frame.py"
sys.path.insert(0, str(REPO / "scripts"))
SPEC = importlib.util.spec_from_file_location("fetch_interpro_frame", SCRIPT)
assert SPEC and SPEC.loader
F = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = F
SPEC.loader.exec_module(F)


def test_extract_entry_matches_preserves_interpro_location_groups() -> None:
    flat, grouped = F.extract_entry_matches(
        [
            {
                "metadata": {
                    "source_database": "cathgene3d",
                    "accession": "G3DSA:1.10.10.10",
                },
                "proteins": [
                    {
                        "entry_protein_locations": [
                            {"fragments": [{"start": 7, "end": 9}, {"start": 2, "end": 4}]},
                            {"fragments": [{"start": 20, "end": 18}]},
                        ]
                    }
                ],
            },
            {
                "metadata": {"source_database": "pfam", "accession": "PF00001"},
                "proteins": [
                    {
                        "entry_protein_locations": [
                            {"fragments": [{"start": "3", "end": "5"}]},
                            {"fragments": [{"start": "bad", "end": "6"}]},
                        ]
                    }
                ],
            },
        ]
    )

    assert flat == {
        "CATH:1.10.10.10": [[7, 9], [2, 4], [18, 20]],
        "Pfam:PF00001": [[3, 5]],
    }
    assert grouped == {
        "CATH:1.10.10.10": [[[7, 9], [2, 4]], [[18, 20]]],
        "Pfam:PF00001": [[[3, 5]]],
    }


def test_read_accession_targets_accepts_comments_uniprot_ids_and_deduplicates(
    tmp_path: Path,
) -> None:
    targets = tmp_path / "accessions.txt"
    targets.write_text(
        "\n".join(
            [
                "# bounded grouped InterPro repair batch",
                "UniProtKB:P12345",
                "Q54321",
                "P12345",
                "",
            ]
        ),
        encoding="utf-8",
    )

    assert F.read_accession_targets(targets) == ["P12345", "Q54321"]


@pytest.mark.parametrize("cached", [False, True])
@pytest.mark.parametrize("apply", [False, True])
@pytest.mark.parametrize("allow_stale", [False, True])
def test_unknown_release_stops_before_fetch_or_sidecar_change(
    tmp_path, monkeypatch, capsys, cached, apply, allow_stale
):
    accessions = tmp_path / "accessions.txt"
    accessions.write_text("P12345\n")
    flat = tmp_path / "flat.json"
    grouped = tmp_path / "grouped.json"
    if cached:
        for path in (flat, grouped):
            path.write_text(json.dumps(F.sidecar.wrap(
                "proteins", {"Q54321": {}}, "InterPro", "110.0")))
    before = {p: p.read_bytes() if p.exists() else None for p in (flat, grouped)}
    args = [str(SCRIPT), "--accessions", str(accessions), "--out", str(flat),
            "--grouped-out", str(grouped)]
    if apply:
        args.append("--apply")
    if allow_stale:
        args.append("--allow-stale")
    monkeypatch.setattr(sys, "argv", args)
    monkeypatch.setattr(F.sidecar, "interpro_release", lambda: None)
    monkeypatch.setattr(F, "fetch_protein", lambda *a: pytest.fail("must not fetch unpinned data"))

    assert F.main() == 2
    assert "cannot determine the current InterPro release" in capsys.readouterr().err
    assert {p: p.read_bytes() if p.exists() else None for p in (flat, grouped)} == before


def test_known_release_stamps_both_fetched_sidecars(tmp_path, monkeypatch):
    accessions = tmp_path / "accessions.txt"
    accessions.write_text("P12345\n")
    flat = tmp_path / "flat.json"
    grouped = tmp_path / "grouped.json"
    monkeypatch.setattr(sys, "argv", [str(SCRIPT), "--accessions", str(accessions),
                                    "--out", str(flat), "--grouped-out", str(grouped),
                                    "--sleep", "0", "--apply"])
    monkeypatch.setattr(F.sidecar, "interpro_release", lambda: "110.0")
    monkeypatch.setattr(F, "fetch_protein", lambda acc: (
        {"Pfam:PF00001": [[2, 3], [6, 7]]},
        {"Pfam:PF00001": [[[2, 3]], [[6, 7]]]},
    ))

    assert F.main() == 0
    for path in (flat, grouped):
        payload = json.loads(path.read_text())
        assert payload["_meta"]["release"] == "110.0"
        assert payload["_meta"]["count"] == 1
        assert set(payload["proteins"]) == {"P12345"}
    assert json.loads(grouped.read_text())["proteins"]["P12345"]["Pfam:PF00001"] == [
        [[2, 3]], [[6, 7]],
    ]
