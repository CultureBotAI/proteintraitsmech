"""The scorer behind the sequence-map measurement, on data small enough to check by hand.

How multi-superfamily proteins are labelled decided a scientific claim in #742's
review (first-sorted label vs any shared label reversed the single- vs
multi-superfamily comparison), so both labelings, their chance levels and their
bootstrap are pinned here. numpy only.
"""

from __future__ import annotations

import importlib.util
import pathlib

import pytest

np = pytest.importorskip("numpy")

ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("measure_sequence_map",
                                              ROOT / "scripts" / "measure_sequence_map.py")
measure = importlib.util.module_from_spec(spec)
spec.loader.exec_module(measure)  # type: ignore[union-attr]


def test_share_matrix_is_symmetric_and_a_protein_is_not_its_own_match():
    S = measure.share_matrix([{"a"}, {"a", "b"}, {"b"}, {"c"}])
    assert S.tolist() == [[False, True, False, False], [True, False, True, False],
                          [False, True, False, False], [False, False, False, False]]


def test_single_label_chance_is_the_sum_of_squared_proportions():
    scorer = measure.Scorer(y=np.array(["x", "x", "x", "y"]))
    assert scorer.chance == pytest.approx(0.75 ** 2 + 0.25 ** 2)
    # every neighbour of every protein is protein 0, an "x"
    ind = np.zeros((4, 2), dtype=int)
    assert scorer.per_point(ind).tolist() == [1.0, 1.0, 1.0, 0.0]
    assert scorer.lift(ind) == pytest.approx(0.75 / 0.625)


def test_any_match_chance_is_the_exact_share_rate_over_distinct_pairs():
    sets = [{"a"}, {"a", "b"}, {"b"}, {"c"}]
    scorer = measure.Scorer(label_sets=sets)
    assert scorer.chance == pytest.approx(4 / 12)        # 2 sharing pairs, ordered, of 4·3
    ind = np.array([[1], [2], [1], [0]])
    assert scorer.per_point(ind).tolist() == [1.0, 1.0, 1.0, 0.0]
    assert scorer.lift(ind) == pytest.approx(0.75 / (1 / 3))


def test_the_two_labelings_can_disagree_about_a_multi_label_protein():
    # protein 1 is {a, b}, labelled "a" by first-sorted; its neighbour is a pure "b"
    sets = [{"a"}, {"a", "b"}, {"b"}, {"b"}]
    first = np.array([sorted(s)[0] for s in sets])
    ind = np.array([[1], [2], [3], [2]])
    assert measure.Scorer(y=first).per_point(ind)[1] == 0.0
    assert measure.Scorer(label_sets=sets).per_point(ind)[1] == 1.0


@pytest.mark.parametrize("any_match", [False, True])
def test_the_bootstrap_interval_contains_its_point_estimate(any_match):
    # the defect this guards: a plug-in chance on resamples counts a protein drawn
    # twice as a matching pair, which put every interval below its own estimate
    rng = np.random.default_rng(0)
    n, k = 400, 10
    fams = rng.integers(0, 120, size=n)                  # many rare classes, as in CATH
    sets = [{int(f)} | ({int(f) + 1} if i % 3 == 0 else set()) for i, f in enumerate(fams)]
    ind = np.array([[j for j in np.argsort(np.abs(fams - fams[i]) + rng.random(n))[:k + 1]
                     if j != i][:k] for i in range(n)])
    res = rng.integers(0, n, size=(300, n))
    scorer = measure.Scorer(label_sets=sets, resamples=res) if any_match else \
        measure.Scorer(y=fams, resamples=res)
    lo, hi = np.percentile(scorer.lift_boot(ind), [2.5, 97.5])
    assert lo <= scorer.lift(ind) <= hi


def test_chance_is_computed_once_per_protein_set_and_reused_across_spaces():
    res = np.random.default_rng(1).integers(0, 6, size=(20, 6))
    scorer = measure.Scorer(y=np.array(list("aabbcc")), resamples=res)
    first = scorer.chance_boot()
    assert scorer.chance_boot() is first


def test_ec_levels_refuse_unassigned_positions():
    assert measure.ec_levels("3.4.24.-", 3) == "3.4.24"
    assert measure.ec_levels("EC:3.4.24.11", 1) == "3"
    assert measure.ec_levels("3.4.-.-", 3) is None
    assert measure.superfamily("CATH:3.40.50.300") == "3.40.50.300"


def test_a_point_is_never_its_own_neighbour_even_among_duplicates():
    # the trait map's SVD space has 2,711 distinct rows for 4,966 proteins; dropping
    # "column 0" left 45% of them in their own neighbour list as a guaranteed match
    pytest.importorskip("sklearn")
    structure = importlib.util.spec_from_file_location(
        "measure_map_structure", ROOT / "scripts" / "measure_map_structure.py")
    mod = importlib.util.module_from_spec(structure)
    structure.loader.exec_module(mod)  # type: ignore[union-attr]
    rng = np.random.default_rng(0)
    base = rng.normal(size=(12, 3))
    X = np.vstack([base, base, base, base[:4]])          # triplicates and quadruplicates
    ind = mod.neighbours(X, 5)
    assert ind.shape == (len(X), 5)
    assert not (ind == np.arange(len(X))[:, None]).any()
    # duplicates ARE legitimate neighbours: each point's nearest are its own twins
    twins = {i: {j for j in range(len(X)) if j != i and np.array_equal(X[i], X[j])}
             for i in range(len(X))}
    assert all(twins[i] <= set(ind[i].tolist()) for i in range(len(X)))
    # and when nothing is duplicated the answer is the ordinary one
    Y = rng.normal(size=(30, 4))
    plain = mod.neighbours(Y, 3)
    dist = np.linalg.norm(Y[:, None] - Y[None], axis=2)
    np.fill_diagonal(dist, np.inf)
    assert np.array_equal(np.sort(plain, axis=1), np.sort(np.argsort(dist, axis=1)[:, :3], axis=1))
