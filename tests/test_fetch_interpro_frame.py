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
@pytest.mark.parametrize("release", [None, "", " ", "error", "110.0-error", 110, True])
def test_unknown_release_stops_before_fetch_or_sidecar_change(
    tmp_path, monkeypatch, capsys, cached, apply, allow_stale, release
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
    monkeypatch.setattr(F.sidecar, "interpro_release", lambda: release)
    monkeypatch.setattr(F, "fetch_protein", lambda *a: pytest.fail("must not fetch unpinned data"))

    assert F.main() == 2
    assert "cannot determine the current InterPro release" in capsys.readouterr().err
    assert {p: p.read_bytes() if p.exists() else None for p in (flat, grouped)} == before


def test_malformed_release_endpoint_payload_fails_closed(tmp_path, monkeypatch):
    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def read(self):
            return b'{"error":"temporary upstream metadata failure"}'

    flat = tmp_path / "flat.json"
    grouped = tmp_path / "grouped.json"
    monkeypatch.setattr(F.sidecar.urllib.request, "urlopen", lambda *a, **kw: Response())
    monkeypatch.setattr(sys, "argv", [str(SCRIPT), "--out", str(flat),
                                    "--grouped-out", str(grouped), "--apply"])
    monkeypatch.setattr(F, "target_proteins", lambda: pytest.fail("must not scan targets"))
    monkeypatch.setattr(F, "fetch_protein", lambda *a: pytest.fail("must not fetch"))

    assert F.main() == 2
    assert not flat.exists()
    assert not grouped.exists()


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


# ------------------------------------------------------- completeness (#1070)


def _crawl(tmp_path, monkeypatch, accessions, *extra, fetch=None):
    targets = tmp_path / "accessions.txt"
    targets.write_text("".join(f"{a}\n" for a in accessions))
    flat = tmp_path / "flat.json"
    grouped = tmp_path / "grouped.json"
    monkeypatch.setattr(sys, "argv", [str(SCRIPT), "--accessions", str(targets),
                                    "--out", str(flat), "--grouped-out", str(grouped),
                                    "--sleep", "0", "--apply", *extra])
    monkeypatch.setattr(F.sidecar, "interpro_release", lambda: "110.0")
    monkeypatch.setattr(F, "fetch_protein", fetch or (lambda acc: ({}, {})))
    status = F.main()
    return status, flat, grouped


def _meta(path):
    return json.loads(path.read_text())["_meta"]


def test_a_full_failure_free_crawl_is_stamped_complete(tmp_path, monkeypatch):
    status, flat, grouped = _crawl(tmp_path, monkeypatch, ["P12345", "Q54321"])
    assert status == 0
    for path in (flat, grouped):
        stamp = _meta(path)["completeness"]
        assert stamp["complete"] is True and F.sidecar.is_complete(_meta(path))
        assert stamp["targets"] == 2 and stamp["missing"] == 0
        assert stamp["target_set"] == F.ACCESSION_TARGET_SET and stamp["basis"] == "crawl"
        assert stamp["targets_sha256"] == F.sidecar.targets_sha256(["Q54321", "P12345"])


def test_a_limit_canary_is_stamped_incomplete(tmp_path, monkeypatch):
    status, flat, grouped = _crawl(tmp_path, monkeypatch, ["P12345", "Q54321"], "--limit", "1")
    assert status == 0
    for path in (flat, grouped):
        stamp = _meta(path)["completeness"]
        assert stamp["complete"] is False and stamp["missing"] == 1
        assert not F.sidecar.is_complete(_meta(path))
    # resuming without the cap finishes the crawl and stamps it complete
    status, flat, _ = _crawl(tmp_path, monkeypatch, ["P12345", "Q54321"])
    assert status == 0 and F.sidecar.is_complete(_meta(flat))


def test_a_partial_crawl_with_failures_is_stamped_incomplete(tmp_path, monkeypatch):
    fetch = lambda acc: None if acc == "Q54321" else ({}, {})  # noqa: E731
    status, flat, _ = _crawl(tmp_path, monkeypatch, ["P12345", "Q54321"],
                             "--allow-partial", fetch=fetch)
    assert status == 0  # accepted as final by --allow-partial, but never as complete
    assert _meta(flat)["completeness"]["complete"] is False


def _legacy_pair(tmp_path, proteins, *, release="110.0", grouped_release=None):
    """A frame pair as the pre-#1070 script wrote it: no completeness marker."""
    flat, grouped = tmp_path / "frame.json", tmp_path / "grouped.json"
    for path, rel in ((flat, release), (grouped, grouped_release or release)):
        blob = F.sidecar.wrap("proteins", {a: {} for a in proteins}, "InterPro", rel)
        blob["_meta"]["built"] = "2026-10-12"
        path.write_text(json.dumps(blob, separators=(",", ":")))
    return flat, grouped


def _certify(monkeypatch, flat, grouped, targets_file, *extra):
    monkeypatch.setattr(sys, "argv", [str(SCRIPT), "--certify", "--accessions",
                                    str(targets_file), "--out", str(flat),
                                    "--grouped-out", str(grouped), *extra])
    monkeypatch.setattr(F.sidecar, "interpro_release",
                        lambda: pytest.fail("certification is offline"))
    monkeypatch.setattr(F, "fetch_protein", lambda *a: pytest.fail("certification is offline"))
    return F.main()


def test_certify_stamps_a_covered_pre_marker_frame_offline_and_keeps_its_content(
    tmp_path, monkeypatch
):
    flat, grouped = _legacy_pair(tmp_path, ["P12345", "Q54321", "EXTRA1"])
    targets = tmp_path / "targets.txt"
    targets.write_text("P12345\nQ54321\n")
    before = {path: json.loads(path.read_text()) for path in (flat, grouped)}
    digests = {path: F.sidecar.content_sha256(before[path]) for path in (flat, grouped)}

    assert _certify(monkeypatch, flat, grouped, targets) == 0  # dry run
    assert {path: json.loads(path.read_text()) for path in (flat, grouped)} == before

    assert _certify(monkeypatch, flat, grouped, targets, "--apply") == 0
    for path in (flat, grouped):
        after = json.loads(path.read_text())
        stamp = after["_meta"].pop("completeness")
        assert after == before[path]  # payload, built, release and count unchanged
        assert stamp["complete"] is True and stamp["basis"] == "offline-certification"
        assert stamp["targets"] == 2 and stamp["certified"]
        assert F.sidecar.content_sha256(json.loads(path.read_text())) == digests[path]


def test_certify_refuses_a_frame_missing_a_target_in_either_file(tmp_path, monkeypatch, capsys):
    flat, grouped = _legacy_pair(tmp_path, ["P12345"])
    blob = json.loads(flat.read_text())
    blob["proteins"]["Q54321"] = {}
    blob["_meta"]["count"] = 2
    flat.write_text(json.dumps(blob))  # Q54321 only in the compact frame
    targets = tmp_path / "targets.txt"
    targets.write_text("P12345\nQ54321\n")
    before = {path: path.read_bytes() for path in (flat, grouped)}
    assert _certify(monkeypatch, flat, grouped, targets, "--apply") == 1
    assert "NOT certified: 1 target" in capsys.readouterr().err
    assert {path: path.read_bytes() for path in (flat, grouped)} == before


@pytest.mark.parametrize("case", ["legacy", "release", "count", "missing"])
def test_certify_refuses_unstamped_mixed_or_inconsistent_frames(tmp_path, monkeypatch, case):
    targets = tmp_path / "targets.txt"
    targets.write_text("P12345\n")
    if case == "release":
        flat, grouped = _legacy_pair(tmp_path, ["P12345"], grouped_release="109.0")
    else:
        flat, grouped = _legacy_pair(tmp_path, ["P12345"])
    if case == "legacy":
        flat.write_text(json.dumps({"P12345": {}}))
    if case == "count":
        blob = json.loads(grouped.read_text())
        blob["_meta"]["count"] = 5
        grouped.write_text(json.dumps(blob))
    if case == "missing":
        grouped.unlink()
    assert _certify(monkeypatch, flat, grouped, targets, "--apply") == 2


def test_certify_takes_no_crawl_options(tmp_path, monkeypatch):
    flat, grouped = _legacy_pair(tmp_path, ["P12345"])
    targets = tmp_path / "targets.txt"
    targets.write_text("P12345\n")
    with pytest.raises(SystemExit):
        _certify(monkeypatch, flat, grouped, targets, "--limit", "1")


def test_certify_derives_the_panel_target_set_from_the_traits_tree(tmp_path, monkeypatch):
    traits = tmp_path / "traits"
    (traits / "a").mkdir(parents=True)
    (traits / "a" / "pfam.yaml").write_text(
        "identifier: Pfam:PF00001\ntrait_category: SEQ_DOMAIN\n"
        "canonical_examples:\n- protein_id: UniProtKB:P12345\n")
    (traits / "a" / "site.yaml").write_text(
        "identifier: fixture:SITE\ntrait_category: STRUCT_ACTIVE_SITE\n"
        "canonical_examples:\n- protein_id: UniProtKB:P12345\n")
    assert F.target_proteins(traits) == ["P12345"]
    flat, grouped = _legacy_pair(tmp_path, ["P12345"])
    monkeypatch.setattr(sys, "argv", [str(SCRIPT), "--certify", "--traits", str(traits),
                                    "--out", str(flat), "--grouped-out", str(grouped),
                                    "--apply"])
    monkeypatch.setattr(F.sidecar, "interpro_release",
                        lambda: pytest.fail("certification is offline"))
    assert F.main() == 0
    stamp = _meta(flat)["completeness"]
    assert stamp["complete"] is True and stamp["target_set"] == F.PANEL_TARGET_SET


def test_content_digest_ignores_build_date_and_stamp_but_not_payload():
    one = F.sidecar.wrap("proteins", {"P12345": {"seq": "MA", "ft": []}}, "UniProt", "2026_03")
    two = json.loads(json.dumps(one))
    two["_meta"]["built"] = "1999-01-01"
    two["_meta"]["completeness"] = {"complete": True}
    assert F.sidecar.content_sha256(one) == F.sidecar.content_sha256(two)
    for mutate in (
        lambda blob: blob["proteins"]["P12345"].update(seq="MC"),
        lambda blob: blob["_meta"].update(release="2026_02"),
        lambda blob: blob["_meta"].update(absent=["Q00000"]),
    ):
        three = json.loads(json.dumps(one))
        mutate(three)
        assert F.sidecar.content_sha256(three) != F.sidecar.content_sha256(one)


def test_certify_with_accessions_refuses_the_panel_frame_paths(tmp_path, monkeypatch):
    targets = tmp_path / "targets.txt"
    targets.write_text("P12345\n")
    monkeypatch.setattr(sys, "argv", [str(SCRIPT), "--certify", "--accessions", str(targets)])
    monkeypatch.setattr(F, "certify", lambda *a: pytest.fail("must refuse before certifying"))
    with pytest.raises(SystemExit):
        F.main()


def test_certify_recipe_refuses_accessions():
    import shutil
    import subprocess

    if shutil.which("just") is None:
        pytest.skip("just is not installed")
    for argument in ("--accessions", "--accessions=x.txt"):
        completed = subprocess.run(["just", "certify-interpro-frame", argument], cwd=REPO,
                                   capture_output=True, text=True, check=False)
        assert completed.returncode == 2
        assert "organism panel only" in completed.stderr


def test_certify_drops_the_interim_marker_and_keeps_the_content_digest(tmp_path, monkeypatch):
    flat, grouped = _legacy_pair(tmp_path, ["P12345"])
    for path in (flat, grouped):
        blob = json.loads(path.read_text())
        blob["_meta"].update({"complete": True, "targets": 1})  # as #1095's fetcher wrote
        path.write_text(json.dumps(blob))
    digest = F.sidecar.content_sha256(json.loads(flat.read_text()))
    targets = tmp_path / "targets.txt"
    targets.write_text("P12345\n")
    assert _certify(monkeypatch, flat, grouped, targets, "--apply") == 0
    meta = _meta(flat)
    assert "complete" not in meta and "targets" not in meta
    assert meta["completeness"]["complete"] is True
    assert F.sidecar.content_sha256(json.loads(flat.read_text())) == digest

