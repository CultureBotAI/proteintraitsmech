"""The sequence map's pure logic, checked without torch, a model, or the corpus.

`embed_sequences.py` and `build_sequence_map.py` import their heavy
dependencies lazily, so the windowing rule, the facet bins, and the label
helpers can be tested in the plain test environment. The embedding itself is
covered by the canary the recipe documents (`--verify-cpu`), not by pytest.
"""

from __future__ import annotations

import importlib.util
import json
import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


embed = _load("embed_sequences")
build = _load("build_sequence_map")


# ------------------------------------------------------------------ windowing


@pytest.mark.parametrize("length", [1, 4, 500, 1021, 1022])
def test_a_sequence_within_the_limit_is_one_window(length):
    assert embed.windows(length) == [(0, length)]


@pytest.mark.parametrize("length", [1023, 1500, 2044, 5000, 34350])
def test_windows_cover_every_residue_exactly_with_fixed_overlap(length):
    w = embed.windows(length)
    assert w[0][0] == 0 and w[-1][1] == length
    for (s0, e0), (s1, e1) in zip(w, w[1:]):
        assert s1 < e0, "consecutive windows must overlap"
        assert e0 - s1 == embed.OVERLAP
        assert s1 - s0 == embed.MAX_RESIDUES - embed.OVERLAP  # stride 766
    assert all(e - s <= embed.MAX_RESIDUES for s, e in w)
    assert all(e - s >= 1 for s, e in w)
    covered = set()
    for s, e in w:
        covered.update(range(s, e))
    assert covered == set(range(length))


def test_the_longest_corpus_sequence_becomes_45_windows():
    # the figure #508 committed to: 34,350 aa → 45 windows
    assert len(embed.windows(34350)) == 45


def test_no_window_is_ever_truncated_away():
    # the residue count over windows equals the sequence plus the overlaps,
    # i.e. nothing is dropped and nothing beyond the overlap is repeated
    length = 3000
    w = embed.windows(length)
    assert sum(e - s for s, e in w) == length + embed.OVERLAP * (len(w) - 1)


# --------------------------------------------------------------------- facets


def test_length_bins_are_ordered_and_the_last_is_the_windowed_tail():
    assert build.length_bin(200) == build.LENGTH_BINS[0]
    assert build.length_bin(201) == build.LENGTH_BINS[1]
    assert build.length_bin(500) == build.LENGTH_BINS[1]
    assert build.length_bin(1022) == build.LENGTH_BINS[2]
    assert build.length_bin(1023) == build.LENGTH_BINS[3]
    assert "windowed" in build.LENGTH_BINS[3]
    assert build.length_bin(embed.MAX_RESIDUES) != build.LENGTH_BINS[3]


def test_primary_axis_is_the_majority_with_deterministic_ties():
    assert build.primary_axis({"SEQUENCE": 3, "STRUCTURE": 1}) == "SEQUENCE"
    assert build.primary_axis({"STRUCTURE": 4, "SEQUENCE": 1}) == "STRUCTURE"
    assert build.primary_axis({"STRUCTURE": 2, "SEQUENCE": 2}) == "SEQUENCE"
    assert build.primary_axis({}) == "SEQUENCE"


def test_cath_class_reads_the_top_level_digit():
    assert build.cath_class(["CATH:3.40.50.300"]) == "Alpha-beta"
    assert build.cath_class(["CATH:1.10.510.10", "CATH:3.40.50.300"]) == "Mainly alpha"
    assert build.cath_class([]) == build.NO_FOLD


def test_cath_labels_merge_the_example_families_with_the_profiles(tmp_path):
    profiles = tmp_path / "profiles.jsonl"
    profiles.write_text(json.dumps({"accession": "UniProtKB:P1",
                                    "traits": ["CATH:2.60.40.10", "Pfam:PF1"]}) + "\n",
                        encoding="utf-8")
    proteins = [{"accession": "UniProtKB:P1", "families": ["CATH:3.40.50.300", "Pfam:PF2"]},
                {"accession": "UniProtKB:P2", "families": []}]
    labels = build.cath_labels(proteins, profiles)
    assert labels["UniProtKB:P1"] == ["CATH:2.60.40.10", "CATH:3.40.50.300"]
    assert labels["UniProtKB:P2"] == []


# ------------------------------------------------------------------- the page


def test_the_page_offers_the_sequence_map_and_deep_links_it():
    html = (ROOT / "docs" / "map.html").read_text(encoding="utf-8")
    assert 'data-map="sequence_map.json"' in html
    assert re.search(r'"#sequences":\s*"sequence_map.json"', html)
    assert "just sequence-map" in html, "the not-built hint must name the recipe"
