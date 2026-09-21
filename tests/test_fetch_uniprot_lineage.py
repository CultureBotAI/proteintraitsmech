"""The UniProt lineage fetcher's logic, offline (#712).

The network is exercised by the canary the recipe documents; everything that
decides *what is asked* and *what an answer means* is pure and tested here.
"""

from __future__ import annotations

import importlib.util
import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("fetch_uniprot_lineage",
                                              ROOT / "scripts" / "fetch_uniprot_lineage.py")
fetch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fetch)  # type: ignore[union-attr]


def _entry(acc, taxon=9606, name="Homo sapiens", lineage=(("domain", "Eukaryota"),),
           secondary=()):
    return {"primaryAccession": acc, "secondaryAccessions": list(secondary),
            "entryType": "UniProtKB reviewed (Swiss-Prot)",
            "organism": {"taxonId": taxon, "scientificName": name},
            "lineages": [{"rank": r, "scientificName": n} for r, n in lineage]}


@pytest.mark.parametrize("lineage,want", [
    ((("no rank", "cellular organisms"), ("domain", "Bacteria"), ("phylum", "X")), "Bacteria"),
    ((("superkingdom", "Archaea"),), "Archaea"),                  # older release wording
    ((("no rank", "Viruses"), ("realm", "Riboviria")), "Viruses"),
    ((("domain", "Eukaryota"),), "Eukaryota"),
    ((("no rank", "unclassified sequences"),), "Unresolved"),
    ((), "Unresolved"),
    ((("phylum", "Bacteria"),), "Unresolved"),    # the name alone, at the wrong rank
])
def test_domain_comes_from_the_top_cellular_rank(lineage, want):
    assert fetch.domain_of(_entry("P12345", lineage=lineage)) == want


def test_an_entry_without_an_organism_is_a_row_not_a_crash():
    row = fetch.row_from_entry("P12345", {"primaryAccession": "P12345",
                                          "entryType": "Inactive"}, "2026_03")
    assert row == {"accession": "UniProtKB:P12345", "taxon_id": None, "organism": None,
                   "domain": "Unresolved", "entry_type": "Inactive",
                   "uniprot_release": "2026_03"}


def test_results_are_matched_back_to_what_was_asked():
    results = [_entry("P11111"), _entry("Q99999", secondary=["P22222"]),
               _entry("O00499", taxon=10090, name="Mus musculus")]
    rows, missing = fetch.match_results(
        ["P11111", "P22222", "O00499-6", "A0A000DEAD0"], results, "2026_03")
    assert missing == ["A0A000DEAD0"]
    by = {r["accession"]: r for r in rows}
    assert set(by) == {"UniProtKB:P11111", "UniProtKB:P22222", "UniProtKB:O00499-6"}
    # a merged accession keeps the name it was asked under
    assert by["UniProtKB:P22222"]["taxon_id"] == "NCBITaxon:9606"
    # an isoform that only comes back as its canonical entry inherits its organism
    assert by["UniProtKB:O00499-6"]["organism"] == "Mus musculus"


def test_an_isoform_returned_as_itself_wins_over_its_canonical_entry():
    results = [_entry("O00499", name="canonical"), _entry("O00499-6", name="isoform")]
    rows, _ = fetch.match_results(["O00499-6"], results, "2026_03")
    assert rows[0]["organism"] == "isoform"


def test_batches_and_request_url():
    assert fetch.batches(list("abcde"), 2) == [["a", "b"], ["c", "d"], ["e"]]
    assert fetch.batches([], 100) == []
    url = fetch.request_url(["P12345", "O00499-6"])
    assert url.startswith(fetch.ENDPOINT + "?")
    assert "accessions=P12345%2CO00499-6" in url and "size=2" in url and "format=json" in url


def test_only_uniprot_accession_syntax_is_ever_requested(tmp_path):
    good = tmp_path / "good.jsonl"
    good.write_text("".join(json.dumps({"accession": a}) + "\n" for a in
                            ["UniProtKB:P12345", "UniProtKB:A0A010QL44",
                             "UniProtKB:O00499-6", "UniProtKB:P12345"]), encoding="utf-8")
    assert fetch.load_accessions(good) == ["A0A010QL44", "O00499-6", "P12345"]
    bad = tmp_path / "bad.jsonl"
    bad.write_text(json.dumps({"accession": "UniProtKB:UNS123&fields=x"}) + "\n",
                   encoding="utf-8")
    with pytest.raises(fetch.LineageError, match="not a UniProtKB accession"):
        fetch.load_accessions(bad)


def test_outputs_round_trip_and_the_receipt_describes_them(tmp_path):
    rows = {"P11111": fetch.row_from_entry("P11111", _entry("P11111"), "2026_03"),
            "P22222": fetch.row_from_entry(
                "P22222", _entry("P22222", taxon=562, name="Escherichia coli",
                                 lineage=(("domain", "Bacteria"),)), "2026_03")}
    fetch.write_outputs(tmp_path, rows, ["A0A000DEAD0"], "2026_03", "02-September-2026", 3)
    cached, release = fetch.load_cache(tmp_path)
    assert release == "2026_03" and set(cached) == {"P11111", "P22222"}
    receipt = json.loads((tmp_path / "lineage.fetch.json").read_text())
    assert receipt["rows"] == 2 and receipt["accessions_asked"] == 3
    assert receipt["domains"] == {"Bacteria": 1, "Eukaryota": 1}
    assert receipt["not_returned"] == ["A0A000DEAD0"]
    assert receipt["rows_without_taxon"] == 0
    assert not [p for p in tmp_path.iterdir() if p.name.endswith(".part")]


def test_a_cache_that_mixes_releases_is_refused(tmp_path):
    (tmp_path / "lineage.jsonl").write_text(
        json.dumps({"accession": "UniProtKB:P11111", "uniprot_release": "2026_02"}) + "\n"
        + json.dumps({"accession": "UniProtKB:P22222", "uniprot_release": "2026_03"}) + "\n",
        encoding="utf-8")
    with pytest.raises(fetch.LineageError, match="mixes UniProt releases"):
        fetch.load_cache(tmp_path)


def test_the_default_is_a_dry_run_that_touches_nothing(tmp_path, monkeypatch, capsys):
    src = tmp_path / "proteins.jsonl"
    src.write_text(json.dumps({"accession": "UniProtKB:P12345"}) + "\n", encoding="utf-8")
    out = tmp_path / "out"

    def no_network(*a, **k):
        raise AssertionError("a dry run must not open a connection")

    monkeypatch.setattr(fetch.urllib.request, "urlopen", no_network)
    monkeypatch.setattr(sys, "argv", ["fetch_uniprot_lineage.py", "--accessions-from",
                                      str(src), "--out-dir", str(out)])
    assert fetch.main() == 0
    plan = json.loads(capsys.readouterr().out)
    assert plan["to_fetch"] == 1 and plan["requests"] == 1 and plan["apply"] is False
    assert not out.exists()
