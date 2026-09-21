"""The sequence map's logic, checked without torch, a model, or the corpus.

`embed_sequences.py` and `build_sequence_map.py` import their heavy
dependencies lazily, and the batching/pooling loop takes its model as a plain
callable, so the windowing rule, the pooling arithmetic, the facets, and the
guards can all be tested with numpy alone. The real model is covered by the
canary the recipe documents (`--verify-cpu`), not by pytest.
"""

from __future__ import annotations

import importlib.util
import json
import pathlib
import re
import sys

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


@pytest.mark.parametrize("length", [1023, 1500, 1788, 1789, 2044, 5000, 34350])
def test_windows_cover_every_residue_exactly_with_fixed_overlap(length):
    w = embed.windows(length)
    assert w[0][0] == 0 and w[-1][1] == length
    for (s0, e0), (s1, e1) in zip(w, w[1:]):
        assert e0 - s1 == embed.OVERLAP
        assert s1 - s0 == embed.MAX_RESIDUES - embed.OVERLAP  # stride 766
    assert all(1 <= e - s <= embed.MAX_RESIDUES for s, e in w)
    covered = set()
    for s, e in w:
        covered.update(range(s, e))
    assert covered == set(range(length))


def test_the_longest_corpus_sequence_becomes_45_windows():
    # the figure #508 committed to: 34,350 aa → 45 windows
    assert len(embed.windows(34350)) == 45


# -------------------------------------------------------------------- pooling

np = pytest.importorskip("numpy")
SENTINEL = 1e6          # any leak of CLS / EOS / padding into a mean is unmissable


class StubForward:
    """A position-independent 'model': residue c → [ord(c), 1]. Because a
    residue's vector does not depend on its window, the windowed, overlap-
    averaged mean must equal the plain mean over the sequence."""

    def __init__(self, drop_char: str | None = None):
        self.calls: list[list[str]] = []
        self.drop_char = drop_char

    def __call__(self, texts):
        self.calls.append(list(texts))
        toks = [[c for c in t if c != self.drop_char] for t in texts]
        width = max(len(t) for t in toks) + 2
        hid = np.full((len(texts), width, 2), SENTINEL, dtype=np.float32)
        for r, t in enumerate(toks):
            for j, c in enumerate(t):
                hid[r, 1 + j] = (ord(c), 1.0)
        return hid, np.asarray([len(t) + 2 for t in toks])


def _seq(n: int) -> str:
    return "".join("ACDEFGHIKLMNPQRSTVWY"[(i * 7 + i // 13) % 20] for i in range(n))


@pytest.mark.parametrize("max_tokens,max_batch", [(16384, 64), (2048, 64), (100, 64),
                                                  (16384, 1), (4096, 3)])
def test_windowed_pooling_equals_the_plain_mean(max_tokens, max_batch):
    lengths = [1, 2, 7, 300, 300, 1021, 1022, 1023, 1024, 1788, 1789, 2555, 5000]
    seqs = [_seq(n) for n in lengths]
    got: dict[int, np.ndarray] = {}
    emb = embed.Embedder(StubForward(), max_tokens, max_batch)
    emb.run(seqs, lambda i, v: got.__setitem__(i, v))
    assert sorted(got) == list(range(len(seqs))), "every sequence finishes exactly once"
    for i, s in enumerate(seqs):
        want = np.mean([ord(c) for c in s])
        assert got[i][0] == pytest.approx(want, rel=1e-5), f"length {len(s)}"
        assert got[i][1] == pytest.approx(1.0), "a sentinel leaked into the mean"
    assert emb.windows == sum(len(embed.windows(n)) for n in lengths)


def test_the_token_budget_is_respected_except_for_a_single_oversize_window():
    fwd = StubForward()
    embed.Embedder(fwd, max_tokens=2048, max_batch=64).run(
        [_seq(n) for n in (1500, 600, 600, 50, 50, 50)], lambda i, v: None)
    for texts in fwd.calls:
        padded = (max(len(t) for t in texts) + 2) * len(texts)
        assert padded <= 2048 or len(texts) == 1


def test_a_tokenizer_that_drops_characters_is_refused_not_pooled():
    # "MK V"-style input: fewer tokens than characters would pull EOS into the mean
    with pytest.raises(ValueError, match="Refusing to embed"):
        embed.Embedder(StubForward(drop_char="J"), 16384, 64).run(
            ["MJJK"], lambda i, v: None)


@pytest.mark.parametrize("raw,want", [
    ("mkvl", "MKVL"), ("  MKVL\n", "MKVL"), ("MXBZUO", "MXBZUO"),
    ("MK VL", None), ("MK*VL", None), ("M12K", None), ("   ", None), ("", None),
    ("MKÅ", None), (None, None)])
def test_only_plain_residue_strings_are_embedded(raw, want):
    assert embed.clean_sequence(raw) == want


def test_verify_picks_always_include_the_longest():
    lengths = [300, 34350, 157, 900, 1200]
    assert embed.verify_picks(lengths, 1) == [1]
    assert 1 in embed.verify_picks(lengths, 3) and 2 in embed.verify_picks(lengths, 3)
    assert embed.verify_picks(lengths, 99) == [0, 1, 2, 3, 4]
    assert embed.verify_picks(lengths, 0) == []


def test_the_mps_fallback_is_refused_unless_explicitly_allowed():
    # #508 asked for it to stay unset; a warning is easy to scroll past (#710)
    assert embed.mps_fallback_problem({}, False) is None
    assert embed.mps_fallback_problem({"PYTORCH_ENABLE_MPS_FALLBACK": "0"}, False) is None
    assert embed.mps_fallback_problem({"PYTORCH_ENABLE_MPS_FALLBACK": ""}, False) is None
    refused = embed.mps_fallback_problem({"PYTORCH_ENABLE_MPS_FALLBACK": "1"}, False)
    assert refused.startswith("error:") and "--allow-mps-fallback" in refused
    allowed = embed.mps_fallback_problem({"PYTORCH_ENABLE_MPS_FALLBACK": "1"}, True)
    assert allowed.startswith("warning:")


def test_the_fallback_guard_applies_to_mps_only_and_runs_before_the_corpus_is_parsed():
    # a CPU or CUDA run has no reason to be blocked by an MPS-only variable, and a
    # refusal should not cost the 80 s it takes to parse the corpus first
    src = (SCRIPTS / "embed_sequences.py").read_text(encoding="utf-8")
    main = src[src.index("def main()"):]
    guard = main.index("mps_fallback_problem(os.environ")
    assert 'if device.type == "mps":' in main[:guard]
    assert main.index("device = pick_device(args.device)") < guard < main.index(
        "files = sequence_files(")
    assert main.count("pick_device(args.device)") == 1


# ---------------------------------------------------------------- preparation


def _blobs():
    rng = np.random.default_rng(0)
    common = rng.normal(size=16) * 8           # the shared direction raw ESM means have
    a = common + rng.normal(size=(30, 16))
    b = common + rng.normal(size=(30, 16)) + np.eye(16)[0] * 4
    return np.vstack([a, b]).astype(np.float32)


def test_prepare_centres_before_normalising_only_when_asked():
    X = _blobs()
    l2, *_ = build.prepare(X, "l2", 0)
    centred, *_ = build.prepare(X, "centre", 0)
    assert np.allclose(np.linalg.norm(l2, axis=1), 1, atol=1e-5)
    assert np.allclose(np.linalg.norm(centred, axis=1), 1, atol=1e-5)
    # uncentred unit vectors all point the same way; centred ones do not
    assert float(np.linalg.norm(l2.mean(axis=0))) > 0.9
    assert float(np.linalg.norm(centred.mean(axis=0))) < 0.3
    assert X[0, 0] == _blobs()[0, 0], "prepare must not modify its input"


def test_prepare_with_pca_returns_unit_rows_and_the_variance_it_kept():
    Z, scores, n_comp, kept, ratios = build.prepare(_blobs(), "centre", 4)
    assert Z.shape == (60, 4) and scores.shape == (60, 4) and n_comp == 4
    assert np.allclose(np.linalg.norm(Z, axis=1), 1, atol=1e-5)
    assert 0 < kept <= 1 and len(ratios) == 4 and kept == pytest.approx(sum(ratios))
    Z0, scores0, n0, kept0, ratios0 = build.prepare(_blobs(), "l2", 0)
    assert scores0 is None and n0 == 0 and kept0 == 1.0 and ratios0 == []
    with pytest.raises(ValueError):
        build.prepare(_blobs(), "whiten", 0)


def test_pca_component_signs_are_fixed_by_the_largest_loading():
    # an SVD is only defined up to sign per component; without the convention two
    # numpy builds could mirror the map. Feeding the mirrored data must flip nothing
    # but the scores themselves.
    X = _blobs()
    centred = X - X.mean(axis=0)
    _, scores, *_ = build.prepare(X, "centre", 3)
    Xu = centred / np.linalg.norm(centred, axis=1, keepdims=True)
    Xc = Xu.astype(np.float64) - Xu.mean(axis=0, dtype=np.float64)
    _, _, Vt = np.linalg.svd(Xc, full_matrices=False)
    for c in range(3):
        loading = Vt[c] * np.sign(Vt[c][np.abs(Vt[c]).argmax()])
        assert loading[np.abs(loading).argmax()] > 0
        assert np.allclose(scores[:, c], Xc @ loading, atol=1e-4), \
            f"component {c} does not follow the largest-loading-positive convention"


def test_a_negative_pca_width_is_refused():
    with pytest.raises(ValueError, match=">= 0"):
        build.prepare(_blobs(), "l2", -3)


def test_prepare_is_deterministic_and_matches_the_definition_of_pca():
    X = _blobs()
    Z1, s1, *_ = build.prepare(X, "centre", 5)
    Z2, s2, *_ = build.prepare(X.copy(), "centre", 5)
    assert np.array_equal(s1, s2) and np.array_equal(Z1, Z2)
    # scores are uncorrelated and ordered by variance, which is what makes them PCA
    cov = np.cov(s1.astype(np.float64), rowvar=False)
    assert np.allclose(cov - np.diag(np.diag(cov)), 0, atol=1e-3)
    assert np.all(np.diff(np.diag(cov)) <= 1e-6)


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


def test_primary_axis_survives_the_placeholder_for_a_missing_axis():
    # embed_sequences writes "?" when a record has no trait_axis
    assert build.primary_axis({"?": 5}) == "SEQUENCE"
    assert build.primary_axis({"?": 5, "STRUCTURE": 1}) == "STRUCTURE"


def test_cath_class_is_the_majority_class_not_the_first_in_sorted_order():
    assert build.cath_class(["CATH:3.40.50.300"]) == "Alpha-beta"
    # sorted order puts class 1 first; two of the three domains are class 3
    assert build.cath_class(["CATH:1.10.510.10", "CATH:3.30.200.20",
                             "CATH:3.40.50.300"]) == "Alpha-beta"
    # a tie breaks toward the lower class number, deterministically
    assert build.cath_class(["CATH:3.40.50.300", "CATH:1.10.510.10"]) == "Mainly alpha"
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


def test_domain_groups_keep_the_three_validated_hues_and_fold_the_rest():
    assert build.domain_group({"domain": "Bacteria"}) == "Bacteria"
    assert build.domain_group({"domain": "Viruses"}) == build.OTHER_DOMAIN
    assert build.domain_group({"domain": "Unresolved"}) == build.OTHER_DOMAIN
    assert build.domain_group(None) == build.OTHER_DOMAIN
    # the three domains reuse the protein map's palette; nothing new to validate
    protein_map = _load("build_protein_map")
    assert set(build.DOMAIN_ORDER) == set(protein_map.DOMAIN_COLORS_LIGHT)
    assert build.OTHER_COLOR.lower() in (ROOT / "docs" / "map.html").read_text().lower(), \
        "the remainder must use the page's own fallback grey, which the contrast test covers"


def test_lineage_rows_load_by_accession_with_their_release(tmp_path):
    path = tmp_path / "lineage.jsonl"
    path.write_text(
        json.dumps({"accession": "UniProtKB:P1", "domain": "Archaea",
                    "organism": "Methanocaldococcus jannaschii",
                    "uniprot_release": "2026_03"}) + "\n", encoding="utf-8")
    rows, release = build.load_lineage(path)
    assert release == "2026_03" and rows["UniProtKB:P1"]["domain"] == "Archaea"


def test_colouring_by_domain_without_the_sidecar_is_refused_with_the_fix(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", [
        "build_sequence_map.py", "--emb-dir", str(_emb_dir(tmp_path, False)),
        "--lineage", str(tmp_path / "absent.jsonl"), "--out", str(tmp_path / "m.json")])
    assert build.main() == 2
    err = capsys.readouterr().err
    assert "fetch-uniprot-lineage" in err and "--colour axis" in err


# ---------------------------------------------------------- the partial guard


def _emb_dir(tmp_path, partial):
    for name in ("ids.json", "vectors.f16.npy", "proteins.jsonl"):
        (tmp_path / name).write_text("[]", encoding="utf-8")
    (tmp_path / "meta.json").write_text(json.dumps(
        {"partial": partial, "filter": {"limit": 3, "accession": []}}), encoding="utf-8")
    return tmp_path


def test_a_canary_embedding_is_refused_before_anything_is_built(tmp_path, monkeypatch, capsys):
    out = tmp_path / "map.json"
    monkeypatch.setattr(sys, "argv", ["build_sequence_map.py", "--emb-dir",
                                      str(_emb_dir(tmp_path, True)), "--out", str(out)])
    assert build.main() == 2
    assert "marked partial" in capsys.readouterr().err
    assert not out.exists()


def test_the_embedder_marks_limit_and_accession_runs_partial():
    src = (SCRIPTS / "embed_sequences.py").read_text(encoding="utf-8")
    assert re.search(r"partial = bool\(args\.limit or args\.accession\)", src)
    assert '"partial": partial' in src


# ------------------------------------------------------------------- the page


def test_the_page_offers_the_sequence_map_and_deep_links_it():
    html = (ROOT / "docs" / "map.html").read_text(encoding="utf-8")
    assert 'data-map="sequence_map.json"' in html
    assert re.search(r'"#sequences":\s*"sequence_map.json"', html)
    assert "just sequence-map" in html, "the not-built hint must name the recipe"


def test_third_party_labels_are_credited_on_the_page_not_only_in_the_json():
    # UniProt's organism names and lineage are CC BY 4.0: attribution where shown
    html = (ROOT / "docs" / "map.html").read_text(encoding="utf-8")
    assert "d.lineage.source" in html and "d.lineage.license" in html
    shipped = json.loads((ROOT / "docs" / "data" / "sequence_map.json").read_text())
    assert "UniProt" in shipped["lineage"]["source"]
    assert "CC BY 4.0" in shipped["lineage"]["license"]
    assert shipped["lineage"]["uniprot_release"]


def test_the_second_facet_is_named_by_the_map_not_by_the_page():
    # it is annotation depth on the protein map and sequence length here (#733)
    html = (ROOT / "docs" / "map.html").read_text(encoding="utf-8")
    assert 'id="depth-label"' in html
    assert re.search(r'getElementById\("depth-label"\)\.textContent\s*=', html)
    assert "sample_label" in html, "a uniform sample must not be called stratified"
