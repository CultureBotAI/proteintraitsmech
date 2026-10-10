"""GO true-path inheritance for exact UniProt GO facts (#1002)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import go_true_path as G  # noqa: E402

OBO = """format-version: 1.2
data-version: releases/2026-06-15

[Term]
id: GO:0000001
name: root ! with a bang in the name
namespace: cellular_component

[Term]
id: GO:0000002
name: middle
namespace: cellular_component
is_a: GO:0000001 ! root

[Term]
id: GO:0000003
name: leaf
namespace: cellular_component
relationship: part_of GO:0000002 ! middle
is_a: GO:0000001 ! root

[Term]
id: GO:0000004
name: function
namespace: molecular_function
relationship: part_of GO:0000001 ! a cross-namespace edge never inherits

[Term]
id: GO:0000005
name: obsolete
namespace: cellular_component
is_obsolete: true
is_a: GO:0000001

[Term]
id: GO:0000006
name: regulated
namespace: cellular_component
relationship: regulates GO:0000001

[Typedef]
id: part_of
name: part of
is_a: GO:0000009
"""


@pytest.fixture
def release(tmp_path):
    path = tmp_path / "go-basic.obo"
    path.write_text(OBO, encoding="utf-8")
    return G.load_go_obo(path)


def test_release_keeps_only_live_is_a_and_part_of_edges(release):
    assert release.release == "releases/2026-06-15"
    assert release.parents["GO:0000003"] == {"GO:0000002": "part_of", "GO:0000001": "is_a"}
    assert "GO:0000005" not in release.parents  # obsolete
    assert release.parents["GO:0000006"] == {}  # regulates never inherits
    assert release.parents["GO:0000004"] == {"GO:0000001": "part_of"}


def test_shortest_path_stays_inside_one_namespace(release):
    assert release.path("GO:0000003", "GO:0000001") == ["GO:0000003", "GO:0000001"]
    assert release.path("GO:0000003", "GO:0000002") == ["GO:0000003", "GO:0000002"]
    assert release.path("GO:0000001", "GO:0000003") is None  # never downward
    assert release.path("GO:0000004", "GO:0000001") is None  # cross-namespace
    assert release.path("GO:0000006", "GO:0000001") is None
    assert release.path("GO:0000003", "GO:0000003") is None


def test_edge_rows_prove_each_step_or_refuse(release):
    rows = release.edge_rows(["GO:0000003", "GO:0000002", "GO:0000001"])
    assert [(row["child"], row["parent"], row["relation"]) for row in rows] == [
        ("GO:0000003", "GO:0000002", "part_of"),
        ("GO:0000002", "GO:0000001", "is_a"),
    ]
    with pytest.raises(G.GoTruePathError, match="no is_a/part_of edge"):
        release.edge_rows(["GO:0000006", "GO:0000001"])
    with pytest.raises(G.GoTruePathError, match="crosses namespaces"):
        release.edge_rows(["GO:0000004", "GO:0000001"])


def test_edge_snapshot_round_trips_canonically_and_checks_against_release(release, tmp_path):
    rows = release.edge_rows(["GO:0000003", "GO:0000002", "GO:0000001"])
    edges = tmp_path / "edges.jsonl"
    edges.write_text(G.dump_edges(reversed(rows)), encoding="utf-8")
    assert G.load_edges(edges) == sorted(rows, key=lambda row: (row["child"], row["parent"]))
    assert G.edge_index(rows) == {
        "GO:0000003": frozenset({"GO:0000002"}),
        "GO:0000002": frozenset({"GO:0000001"}),
    }
    obo = tmp_path / "go-basic.obo"
    obo.write_text(OBO, encoding="utf-8")
    assert G.check(edges, obo) == []
    assert G.main(["check", "--edges", str(edges), "--obo", str(obo)]) == 0
    # A newer release that keeps every edge passes; the rows keep their own release.
    obo.write_text(OBO.replace("2026-06-15", "2026-09-01"), encoding="utf-8")
    assert G.check(edges, obo) == []
    # One that drops or changes a tracked edge is reported (#1039).
    obo.write_text(
        OBO.replace("relationship: part_of GO:0000002 ! middle\n", ""), encoding="utf-8"
    )
    (problem,) = G.check(edges, obo)
    assert "GO:0000003 -> GO:0000002" in problem
    assert G.main(["check", "--edges", str(edges), "--obo", str(obo)]) == 1


@pytest.mark.parametrize(
    "mutation",
    [
        {"relation": "regulates"},
        {"parent": "GO:0000003"},
        {"child": "PFAM:PF00001"},
        {"go_release": "2026-06-15"},
        {"source": "http://example.org/go.obo"},
        {"extra": "field"},
    ],
)
def test_malformed_edge_rows_are_rejected(release, tmp_path, mutation):
    (row,) = release.edge_rows(["GO:0000003", "GO:0000002"])
    with pytest.raises(G.GoTruePathError):
        G.merge_edges([{**row, **mutation}])


def test_conflicting_or_noncanonical_snapshots_are_rejected(release, tmp_path):
    (row,) = release.edge_rows(["GO:0000003", "GO:0000002"])
    with pytest.raises(G.GoTruePathError, match="conflicting"):
        G.merge_edges([row, {**row, "relation": "is_a"}])
    edges = tmp_path / "edges.jsonl"
    edges.write_text(G.dump_edges([row]).replace(",", ", "), encoding="utf-8")
    with pytest.raises(G.GoTruePathError, match="canonical"):
        G.load_edges(edges)
    assert G.load_edges(tmp_path / "absent.jsonl") == []


def test_union_index_adds_go_edges_to_trait_edges():
    trait = {"GO:0000002": frozenset({"GO:0000099"})}
    rows = [
        {
            "child": "GO:0000002",
            "parent": "GO:0000001",
            "relation": "is_a",
            "go_release": "releases/2026-06-15",
            "source": G.GO_BASIC_SOURCE,
        }
    ]
    assert G.union_index(trait, rows) == {"GO:0000002": frozenset({"GO:0000099", "GO:0000001"})}


def test_pinned_release_constants():
    assert G.PINNED_GO_RELEASE == "releases/2026-06-15"
    assert G.PINNED_GO_URL == "https://release.geneontology.org/2026-06-19/ontology/go-basic.obo"
    assert G.PINNED_GO_SHA256 == "c72fc198a86983d55e43aac585d1ffdbeb6e3601475b3f18b6045acdc0a0734c"
    assert G.PINNED_GO_MIN_BYTES == 32_000_000


def test_update_edges_no_change(release, tmp_path):
    rows = release.edge_rows(["GO:0000003", "GO:0000002", "GO:0000001"])
    edges = tmp_path / "edges.jsonl"
    edges.write_text(G.dump_edges(rows), encoding="utf-8")
    obo = tmp_path / "go-basic.obo"
    obo.write_text(OBO, encoding="utf-8")

    updated, messages = G.update(edges, obo, apply=False)
    assert messages == []
    assert updated == sorted(rows, key=lambda r: (r["child"], r["parent"]))
    assert G.main(["update", "--edges", str(edges), "--obo", str(obo)]) == 0


def test_update_edges_relation_changed(release, tmp_path):
    rows = release.edge_rows(["GO:0000003", "GO:0000002"])
    assert rows[0]["relation"] == "part_of"
    edges = tmp_path / "edges.jsonl"
    edges.write_text(G.dump_edges(rows), encoding="utf-8")

    # In new release, relation changes to is_a and date advances
    new_obo = OBO.replace(
        "relationship: part_of GO:0000002 ! middle", "is_a: GO:0000002 ! middle"
    ).replace("releases/2026-06-15", "releases/2026-08-01")
    obo = tmp_path / "go-basic.obo"
    obo.write_text(new_obo, encoding="utf-8")

    # Dry-run: messages generated but disk file untouched
    updated, messages = G.update(edges, obo, apply=False)
    assert len(messages) == 1
    assert "updated GO:0000003 -> GO:0000002: part_of (releases/2026-06-15) -> is_a (releases/2026-08-01)" in messages[0]
    on_disk = G.load_edges(edges)
    assert on_disk[0]["relation"] == "part_of"

    # Apply: disk file updated
    updated, messages = G.update(edges, obo, apply=True)
    assert len(messages) == 1
    on_disk = G.load_edges(edges)
    assert on_disk[0]["relation"] == "is_a"
    assert on_disk[0]["go_release"] == "releases/2026-08-01"


def test_update_edges_filtering_and_errors(release, tmp_path):
    rows = release.edge_rows(["GO:0000003", "GO:0000002", "GO:0000001"])
    edges = tmp_path / "edges.jsonl"
    edges.write_text(G.dump_edges(rows), encoding="utf-8")
    obo = tmp_path / "go-basic.obo"
    obo.write_text(OBO, encoding="utf-8")

    # Filter by non-existent edge raises GoTruePathError
    with pytest.raises(G.GoTruePathError, match="no tracked edge matched"):
        G.update(edges, obo, child="GO:0000999")

    # If edge does not exist in release, targeted filter raises GoTruePathError
    dropped_obo = OBO.replace("relationship: part_of GO:0000002 ! middle\n", "")
    obo.write_text(dropped_obo, encoding="utf-8")
    with pytest.raises(G.GoTruePathError, match="edge does not exist"):
        G.update(edges, obo, child="GO:0000003", parent="GO:0000002")
