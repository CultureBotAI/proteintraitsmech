"""Tests for the cross-Mech protein-example snapshot, audit, and drift check (#652).

Everything runs offline: sibling Mechs and the trait tree are throwaway git
repositories under ``tmp_path``; network boundaries are injected.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import pathlib
import subprocess
import sys
import urllib.error
from types import SimpleNamespace

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "cross_mech_proteins.py"


def _load(name: str, path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


CM = _load("cross_mech_proteins", SCRIPT)

GIT_IDENTITY = ["-c", "user.name=cross-mech-test", "-c", "user.email=cross-mech-test@localhost"]
FLEET_COMMIT = "f" * 40


def _git(repo: pathlib.Path, *args: str) -> str:
    return subprocess.run(
        ["git", *GIT_IDENTITY, *args], cwd=repo, check=True, capture_output=True, text=True
    ).stdout


def _write(path: pathlib.Path, document) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")


def _sibling(root: pathlib.Path, name: str, files: dict[str, object]) -> pathlib.Path:
    """A sibling checkout whose origin is CultureBotAI/<name> and origin/main is HEAD."""

    repo = root / name
    repo.mkdir(parents=True)
    _git(repo, "init", "-q")
    _git(repo, "remote", "add", "origin", f"https://github.com/CultureBotAI/{name}.git")
    for relative, document in files.items():
        _write(repo / relative, document)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "seed")
    _git(repo, "update-ref", "refs/remotes/origin/main", "HEAD")
    return repo


def _advance(repo: pathlib.Path, files: dict[str, object]) -> None:
    for relative, document in files.items():
        _write(repo / relative, document)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "advance")
    _git(repo, "update-ref", "refs/remotes/origin/main", "HEAD")


def _fleet(*targets: tuple[str, str, list[str]]):
    mechs = {
        "proteintraitsmech": {
            "github": "CultureBotAI/proteintraitsmech",
            "record_globs": ["data/traits/**/*.yaml"],
        }
    }
    for key, github, globs in targets:
        mechs[key] = {"github": github, "record_globs": globs}
    text = yaml.safe_dump({"version": 1, "mechs": mechs}, sort_keys=True)
    return CM.parse_fleet_manifest(text, commit=FLEET_COMMIT)


NATURAL_PRODUCT = {
    "identifier": "CHEBI:29472",
    "biosynthetic_pathway": [
        {
            "step_number": 1,
            "enzyme_id": "UniProtKB:Q9I0Q0",
            "enzyme_label": "PqsH",
            "reaction_id": "RHEA:37872",
            "substrate": "CHEBI:62219",
        }
    ],
    "bioactivities": [{"target_enzyme": "UniProtKB:P63092"}],
    "causal_graphs": [
        {"nodes": [{"node_id": "pqsh", "identifier": "UniProtKB:Q9I0Q0"}], "edges": []}
    ],
}

TRAIT_RECORD = {
    "identifier": "traitmech:biofilm",
    "causal_graphs": [
        {
            "nodes": [
                {
                    "node_id": "wspR",
                    "grounding": "GO:0052621",
                    "protein_examples": [
                        {
                            "uniprot_id": "UniProtKB:Q9HXT9",
                            "protein_label": "Diguanylate cyclase WspR",
                            "taxon_id": "NCBITaxon:208964",
                            "evidence": [{"reference": "UniProtKB:Q9HXT9"}],
                        }
                    ],
                }
            ]
        }
    ],
}


@pytest.fixture
def fleet_root(tmp_path):
    root = tmp_path / "mechs"
    _sibling(
        root,
        "NaturalProductMech",
        {"data/natural_products/alkaloids/pqs.yaml": NATURAL_PRODUCT},
    )
    _sibling(root, "TraitMech", {"data/traits/ecology/biofilm.yaml": TRAIT_RECORD})
    fleet = _fleet(
        (
            "naturalproductmech",
            "CultureBotAI/NaturalProductMech",
            ["data/natural_products/**/*.yaml"],
        ),
        ("traitmech", "CultureBotAI/TraitMech", ["data/traits/**/*.yaml"]),
    )
    return root, fleet


# ----------------------------------------------------------------- pure helpers


def test_glob_translation_matches_fleet_semantics():
    deep = CM.glob_to_regex("data/traits/**/*.yaml")
    assert deep.match("data/traits/a.yaml")
    assert deep.match("data/traits/x/y/a.yaml")
    assert not deep.match("data/traitsx/a.yaml")
    assert not deep.match("data/traits/a.yml")
    flat = CM.glob_to_regex("kb/communities/*.yaml")
    assert flat.match("kb/communities/a.yaml")
    assert not flat.match("kb/communities/x/a.yaml")


def test_remote_urls_normalize_to_owner_repo():
    assert CM.normalize_remote("https://github.com/CultureBotAI/TraitMech.git") == (
        "culturebotai/traitmech"
    )
    assert CM.normalize_remote("git@github.com:CultureBotAI/TraitMech.git") == (
        "culturebotai/traitmech"
    )
    assert CM.normalize_remote("ssh://git@github.com/CultureBotAI/TraitMech") == (
        "culturebotai/traitmech"
    )
    assert CM.normalize_remote("https://gitlab.com/CultureBotAI/TraitMech.git") == ""


def test_fleet_manifest_excludes_self_and_refuses_a_foreign_fleet():
    fleet = _fleet(("traitmech", "CultureBotAI/TraitMech", ["data/traits/**/*.yaml"]))
    assert [target.key for target in fleet.targets] == ["traitmech"]
    assert fleet.sha256 and fleet.commit == FLEET_COMMIT
    foreign = yaml.safe_dump(
        {"version": 1, "mechs": {"x": {"github": "o/x", "record_globs": ["*.yaml"]}}}
    )
    with pytest.raises(CM.CrossMechError, match="refusing a foreign fleet"):
        CM.parse_fleet_manifest(foreign, commit=FLEET_COMMIT)
    with pytest.raises(CM.CrossMechError, match="record_globs"):
        CM.parse_fleet_manifest(
            yaml.safe_dump({"version": 1, "mechs": {"x": {"github": "o/x"}}}), commit=FLEET_COMMIT
        )


def test_channel_rules_are_unique_and_well_formed():
    seen = set()
    for channel in CM.CHANNELS:
        assert (channel.mech, channel.pattern) not in seen
        seen.add((channel.mech, channel.pattern))
        assert channel.role in CM.ROLES and channel.role != "UNCLASSIFIED"
        for source in channel.annotations:
            assert source.scope in {"self", "parent", "record", "list"}


# ------------------------------------------------------------------ extraction


def _rows(mech, document, path="data/x.yaml"):
    return {row["pattern"]: row for row in CM.mention_rows(mech, path, document)}


def test_biosynthetic_enzyme_carries_its_rhea_reaction_and_label():
    rows = _rows("naturalproductmech", NATURAL_PRODUCT)
    step = rows["/biosynthetic_pathway/[]/enzyme_id"]
    assert step["role"] == "EXAMPLE"
    assert step["protein_id"] == "UniProtKB:Q9I0Q0"
    assert step["sibling_label"] == "PqsH"
    assert step["annotations"] == [
        {"curie": "RHEA:37872", "relation": "catalyzes", "source": "self.reaction_id"}
    ]
    assert rows["/bioactivities/[]/target_enzyme"]["role"] == "TARGET"
    assert rows["/bioactivities/[]/target_enzyme"]["annotations"] == []
    assert rows["/causal_graphs/[]/nodes/[]/identifier"]["role"] == "GRAPH_NODE"


def test_traitmech_example_reads_the_node_grounding_and_evidence_is_a_reference():
    rows = _rows("traitmech", TRAIT_RECORD)
    example = rows["/causal_graphs/[]/nodes/[]/protein_examples/[]/uniprot_id"]
    assert example["annotations"][0]["curie"] == "GO:0052621"
    assert example["sibling_taxon_id"] == "NCBITaxon:208964"
    evidence = rows["/causal_graphs/[]/nodes/[]/protein_examples/[]/evidence/[]/reference"]
    assert evidence["role"] == "REFERENCE" and evidence["annotations"] == []


def test_pathway_edge_annotation_requires_the_catalyzes_predicate():
    document = {
        "id": "Reactome:R-MTU-1",
        "mechanistic_edges": [
            {"subject": "UniProtKB:P06721", "predicate": "catalyzes", "object": "RHEA:13966"},
            {"subject": "UniProtKB:P06722", "predicate": "inhibits", "object": "RHEA:13966"},
        ],
    }
    rows = CM.mention_rows("pathwaymech", "data/pathways/p.yaml", document)
    by_protein = {row["protein_id"]: row for row in rows}
    assert by_protein["UniProtKB:P06721"]["annotations"][0]["curie"] == "RHEA:13966"
    assert by_protein["UniProtKB:P06722"]["annotations"] == []


def test_cellstructure_rows_carry_component_record_and_complex_annotations():
    document = {
        "identifier": "GO:0009390",
        "components": [
            {
                "grounding": "InterPro:IPR014297",
                "protein_examples": [{"uniprot_id": "UniProtKB:P18775", "protein_label": "DmsA"}],
            }
        ],
        "complex_compositions": [
            {
                "source_accession": "ComplexPortal:CPX-320",
                "participants": [
                    {"participant_id": "UniProtKB:P18776", "label": "DmsB"},
                    {"participant_id": "CHEBI:60539"},
                ],
            }
        ],
        "causal_graphs": [{"nodes": [{"xrefs": ["UniProtKB:P69776", "Pfam:PF04728"]}]}],
    }
    rows = _rows("cellstructuremech", document)
    component = rows["/components/[]/protein_examples/[]/uniprot_id"]
    assert [item["curie"] for item in component["annotations"]] == [
        "GO:0009390",
        "InterPro:IPR014297",
    ]
    participant = rows["/complex_compositions/[]/participants/[]/participant_id"]
    assert {item["curie"] for item in participant["annotations"]} == {
        "ComplexPortal:CPX-320",
        "GO:0009390",
    }
    assert participant["sibling_label"] == "DmsB"
    node = rows["/causal_graphs/[]/nodes/[]/xrefs/[]"]
    assert [item["curie"] for item in node["annotations"]] == ["Pfam:PF04728"]


def test_bare_accessions_need_a_protein_key_and_isoforms_survive():
    document = {
        "x": [{"uniprot_id": "P12345-2", "name": "Q99999", "other": "UniProt:O15530"}],
    }
    rows = CM.mention_rows("traitmech", "data/x.yaml", document)
    assert sorted(row["protein_id"] for row in rows) == [
        "UniProtKB:O15530",
        "UniProtKB:P12345-2",
    ]
    assert {row["role"] for row in rows} == {"UNCLASSIFIED"}


def test_resistance_label_is_not_mistaken_for_a_protein_label():
    document = {
        "resistance_mechanisms": [
            {
                "label": "FKS1(P647A) associated with resistance",
                "protein_accession": "UniProtKB:P38631",
                "phenotype_id": "PHIPO:0000586",
            }
        ]
    }
    (row,) = CM.mention_rows("antibioticmech", "data/a.yaml", document)
    assert row["sibling_label"] is None
    assert row["annotations"] == [
        {
            "curie": "PHIPO:0000586",
            "relation": "resistance_phenotype",
            "source": "self.phenotype_id",
        }
    ]


# --------------------------------------------------------------- scan + snapshot


def test_scan_reads_committed_objects_not_the_working_tree(fleet_root, tmp_path):
    root, fleet = fleet_root
    dirty = root / "TraitMech" / "data" / "traits" / "ecology" / "biofilm.yaml"
    dirty.write_text("identifier: traitmech:biofilm\n", encoding="utf-8")
    result = CM.scan(fleet, root, environ={})
    proteins = {row["protein_id"] for row in result.rows}
    assert "UniProtKB:Q9HXT9" in proteins  # still read from origin/main, not the edit
    assert [mech["key"] for mech in result.mechs] == ["naturalproductmech", "traitmech"]
    assert all(CM.COMMIT_HEX.fullmatch(mech["commit"]) for mech in result.mechs)


def test_scan_respects_record_globs(tmp_path):
    root = tmp_path / "mechs"
    _sibling(
        root,
        "PathwayMech",
        {
            "data/pathways/p.yaml": {"participants": [{"id": "UniProtKB:P06721"}]},
            "docs/p.yaml": {"participants": [{"id": "UniProtKB:P11111"}]},
        },
    )
    fleet = _fleet(("pathwaymech", "CultureBotAI/PathwayMech", ["data/pathways/*.yaml"]))
    result = CM.scan(fleet, root, environ={})
    assert {row["protein_id"] for row in result.rows} == {"UniProtKB:P06721"}


def test_scan_refuses_a_checkout_whose_origin_is_another_repository(tmp_path):
    root = tmp_path / "mechs"
    repo = _sibling(root, "TraitMech", {"data/traits/t.yaml": TRAIT_RECORD})
    _git(repo, "remote", "set-url", "origin", "https://github.com/someone/TraitMech.git")
    fleet = _fleet(("traitmech", "CultureBotAI/TraitMech", ["data/traits/**/*.yaml"]))
    with pytest.raises(CM.CrossMechError, match="not 'CultureBotAI/TraitMech'"):
        CM.scan(fleet, root, environ={})


def test_snapshot_round_trips_and_detects_tampering(fleet_root, tmp_path):
    root, fleet = fleet_root
    result = CM.scan(fleet, root, environ={})
    out = tmp_path / "snapshot"
    manifest = CM.write_snapshot(result, fleet, out)
    rows, loaded = CM.load_snapshot(out)
    assert loaded == manifest
    assert rows == result.rows
    assert manifest["counts"]["unclassified_patterns"] == []
    assert manifest["fleet_manifest"]["commit"] == FLEET_COMMIT

    mentions = out / CM.MENTIONS_NAME
    original = mentions.read_bytes()
    mentions.write_bytes(original.replace(b"Q9HXT9", b"Q9HXT8"))
    with pytest.raises(CM.CrossMechError, match="mentions_sha256"):
        CM.load_snapshot(out)

    # A re-sorted, re-hashed file still fails: order and counts are part of the contract.
    lines = original.decode().splitlines(keepends=True)
    reordered = "".join(reversed(lines)).encode()
    manifest["mentions_sha256"] = hashlib.sha256(reordered).hexdigest()
    errors = CM.verify_snapshot(reordered, manifest)
    assert any("strictly sorted" in error for error in errors)


def test_check_command_flags_changed_rules(fleet_root, tmp_path, monkeypatch, capsys):
    root, fleet = fleet_root
    out = tmp_path / "snapshot"
    CM.write_snapshot(CM.scan(fleet, root, environ={}), fleet, out)
    assert CM.main(["check", "--snapshot", str(out)]) == 0
    monkeypatch.setattr(CM, "rules_sha256", lambda: "0" * 64)
    assert CM.main(["check", "--snapshot", str(out)]) == 1
    assert "channel rules changed" in capsys.readouterr().out


def test_local_drift_separates_record_changes_from_other_commits(fleet_root, tmp_path):
    root, fleet = fleet_root
    manifest = CM.build_manifest(CM.scan(fleet, root, environ={}), fleet, "")
    _advance(root / "TraitMech", {"README.yaml": {"note": "not a record"}})
    _advance(
        root / "NaturalProductMech",
        {"data/natural_products/alkaloids/new.yaml": {"identifier": "CHEBI:1"}},
    )
    states = {item["key"]: item for item in CM.local_drift(manifest, root, environ={})}
    assert states["traitmech"]["state"] == "MOVED_RECORDS_UNCHANGED"
    assert states["naturalproductmech"]["state"] == "STALE"
    assert states["naturalproductmech"]["changed"] == 1


def test_remote_head_and_fleet_fetch_guards():
    head = "a" * 40

    def runner(cmd, **kwargs):
        assert cmd[:3] == [
            "git",
            "ls-remote",
            "https://github.com/CultureBotAI/culturebotai-claw.git",
        ]
        return SimpleNamespace(returncode=0, stdout=f"{head}\tHEAD\n", stderr="")

    class Response:
        status = 200

        def __init__(self, url):
            self.url = url

        def geturl(self):
            return self.url

        def read(self, limit):
            return yaml.safe_dump(
                {
                    "version": 1,
                    "mechs": {
                        "proteintraitsmech": {
                            "github": "CultureBotAI/proteintraitsmech",
                            "record_globs": ["data/traits/**/*.yaml"],
                        }
                    },
                }
            ).encode()

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    fleet = CM.fetch_fleet_manifest(
        opener=lambda req, timeout: Response(req.full_url), runner=runner
    )
    assert fleet.commit == head and fleet.targets == ()

    def off_host(req, timeout):
        return Response("https://evil.example/fleet.yaml")

    with pytest.raises(CM.CrossMechError, match="redirected off"):
        CM.fetch_fleet_manifest(head, opener=off_host, runner=runner)


# ------------------------------------------------------------------------- audit


def _trait_tree(tmp_path: pathlib.Path) -> pathlib.Path:
    repo = tmp_path / "ptm"
    traits = repo / "data" / "traits"
    records = {
        "function/enzymatic_activity/rhea/r37871.yaml": {
            "identifier": "RHEA:37871",
            "trait_axis": "FUNCTION",
            "trait_category": "FUNC_ENZYMATIC_ACTIVITY",
        },
        "function/molecular_function/go/dgc.yaml": {
            "identifier": "GO:0052621",
            "trait_axis": "FUNCTION",
            "trait_category": "FUNC_MOLECULAR_FUNCTION",
            "canonical_examples": [{"protein_id": "UniProtKB:Q9HXT9", "protein_label": "WspR"}],
        },
        "sequence/domain/pfam/lpp.yaml": {
            "identifier": "Pfam:PF04728",
            "trait_axis": "SEQUENCE",
            "trait_category": "SEQ_DOMAIN",
            "canonical_examples": [
                {
                    "protein_id": "UniProtKB:P69776",
                    "protein_label": "Lpp",
                    "qualification_status": "QUALIFIED",
                }
            ],
        },
    }
    repo.mkdir()
    _git(repo, "init", "-q")
    for relative, document in records.items():
        _write(traits / relative, document)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "traits")
    # An untracked record and a modified identifier are seen through the working-tree patch.
    _write(
        traits / "function/interaction_partner/complexportal/cpx320.yaml",
        {
            "identifier": "ComplexPortal:CPX-320",
            "trait_axis": "FUNCTION",
            "trait_category": "FUNC_INTERACTION_PARTNER",
        },
    )
    return traits


def _directions(tmp_path: pathlib.Path) -> tuple[pathlib.Path, str]:
    path = tmp_path / "rhea-directions.tsv"
    text = "RHEA_ID_MASTER\tRHEA_ID_LR\tRHEA_ID_RL\tRHEA_ID_BI\n37871\t37872\t37873\t37874\n"
    path.write_text(text, encoding="utf-8")
    return path, hashlib.sha256(text.encode()).hexdigest()


def _row(protein, curie, *, role="EXAMPLE", channel="test.channel", mech="testmech"):
    return {
        "mech": mech,
        "record_path": "data/r.yaml",
        "record_id": None,
        "pointer": f"/{protein}/{curie}",
        "pattern": "/x",
        "protein_id": protein,
        "raw_value": protein,
        "channel": channel,
        "role": role,
        "relation": "r",
        "annotations": [{"curie": curie, "relation": "r", "source": "self.x"}],
        "sibling_label": None,
        "sibling_taxon_id": None,
    }


def test_audit_assigns_exactly_one_status_per_pair(tmp_path):
    traits = _trait_tree(tmp_path)
    directions, digest = _directions(tmp_path)
    rows = [
        _row("UniProtKB:Q9I0Q0", "RHEA:37872"),  # directional -> master, absent
        _row("UniProtKB:Q9HXT9", "GO:0052621"),  # legacy example already there
        _row("UniProtKB:P69776", "Pfam:PF04728", role="GRAPH_NODE"),  # qualified
        _row("UniProtKB:P18776", "ComplexPortal:CPX-320"),  # untracked record, absent
        _row("UniProtKB:P18776", "GO:0009390"),  # namespace known, record absent
        _row("UniProtKB:P38631", "PHIPO:0000586"),  # not a corpus namespace
    ]
    report = CM.audit(
        rows, traits_root=traits, rhea_directions=directions, rhea_directions_sha256=digest
    )
    statuses = {(pair["protein_id"], pair["trait_id"]): pair for pair in report["pairs"]}
    assert statuses[("UniProtKB:Q9I0Q0", "RHEA:37871")]["status"] == "ABSENT_FROM_TRAIT"
    assert statuses[("UniProtKB:Q9I0Q0", "RHEA:37871")]["sibling_curies"] == ["RHEA:37872"]
    assert statuses[("UniProtKB:Q9I0Q0", "RHEA:37871")]["route"] == "SOURCE_MEMBERSHIP:UniProtKB"
    assert statuses[("UniProtKB:Q9HXT9", "GO:0052621")]["status"] == "LEGACY_ON_TRAIT"
    assert statuses[("UniProtKB:Q9HXT9", "GO:0052621")]["route"] == "SOURCE_ANNOTATION:UniProtKB"
    assert statuses[("UniProtKB:P69776", "Pfam:PF04728")]["status"] == "QUALIFIED_ON_TRAIT"
    assert statuses[("UniProtKB:P69776", "Pfam:PF04728")]["route"] == "INTERPRO_MATCH:InterPro"
    cpx = statuses[("UniProtKB:P18776", "ComplexPortal:CPX-320")]
    assert cpx["status"] == "ABSENT_FROM_TRAIT"
    assert (
        cpx["record_path"] == "data/traits/function/interaction_partner/complexportal/cpx320.yaml"
    )
    assert statuses[("UniProtKB:P18776", "GO:0009390")]["status"] == "TRAIT_NOT_IN_PTM"
    assert statuses[("UniProtKB:P38631", "PHIPO:0000586")]["status"] == "NOT_A_PTM_NAMESPACE"
    assert report["summary"]["candidate_pairs"] == 3
    assert report["rhea_directions_sha256"] == digest
    assert CM.render_pairs_tsv(report["pairs"]).startswith("protein_id\ttrait_id\tstatus")


def test_audit_refuses_unpinned_rhea_directions(tmp_path):
    directions, _ = _directions(tmp_path)
    with pytest.raises(CM.CrossMechError, match="pinned release-141"):
        CM.load_rhea_directions(directions)


def test_audit_without_directions_still_resolves_master_ids(tmp_path):
    traits = _trait_tree(tmp_path)
    report = CM.audit(
        [_row("UniProtKB:Q9I0Q0", "RHEA:37871"), _row("UniProtKB:Q9I0Q0", "RHEA:37872")],
        traits_root=traits,
        rhea_directions=tmp_path / "absent.tsv",
    )
    statuses = {pair["trait_id"]: pair["status"] for pair in report["pairs"]}
    assert statuses == {"RHEA:37871": "ABSENT_FROM_TRAIT", "RHEA:37872": "TRAIT_NOT_IN_PTM"}
    assert report["rhea_ids_unchecked_for_direction"] == ["RHEA:37872"]


def test_rhea_directions_pin_matches_the_rhea_stage_pin(monkeypatch):
    monkeypatch.syspath_prepend(str(REPO / "scripts"))  # the stage imports sibling helpers
    stage = _load(
        "stage_rhea_uniprot_grounding_pin", REPO / "scripts" / "stage_rhea_uniprot_grounding.py"
    )
    assert CM.RHEA_DIRECTIONS_SHA256 == stage.CURRENT_SOURCE_SHA256["directions"]


def test_tracked_snapshot_verifies_when_present():
    """The committed data/cross_mech snapshot must always pass its own integrity check."""

    manifest_path = CM.SNAPSHOT_DIR / CM.MANIFEST_NAME
    if not manifest_path.is_file():
        pytest.skip("no tracked cross-Mech snapshot in this checkout")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    raw = (CM.SNAPSHOT_DIR / CM.MENTIONS_NAME).read_bytes()
    assert CM.verify_snapshot(raw, manifest) == []
    assert manifest["rules_sha256"] == CM.rules_sha256(), "rescan: channel rules changed"


# ------------------------------------------------------------- review fixes (#962-#969)


def test_rule_digest_tracks_extraction_constants(monkeypatch):
    before = CM.rules_sha256()
    monkeypatch.setattr(CM, "_NON_CURIE_SCHEMES", CM._NON_CURIE_SCHEMES | {"doi"})
    assert CM.rules_sha256() != before
    monkeypatch.undo()
    monkeypatch.setattr(CM, "EXTRACTION_VERSION", CM.EXTRACTION_VERSION + 1)
    assert CM.rules_sha256() != before


@pytest.mark.parametrize(
    "error",
    [subprocess.TimeoutExpired(cmd="git ls-remote", timeout=60), OSError("no git")],
)
def test_remote_head_turns_runner_failures_into_notices(error):
    def runner(*args, **kwargs):
        raise error

    with pytest.raises(CM.CrossMechError, match="did not complete"):
        CM.remote_head("CultureBotAI/TraitMech", runner=runner)


@pytest.mark.parametrize(
    "error",
    [
        urllib.error.HTTPError("https://raw.githubusercontent.com/x", 503, "busy", {}, None),
        urllib.error.URLError("unreachable"),
        TimeoutError("read timed out"),
    ],
)
def test_guarded_fetch_turns_network_failures_into_notices(error):
    def opener(request, timeout):
        raise error

    with pytest.raises(CM.CrossMechError, match="could not be fetched"):
        CM._guarded_fetch("https://raw.githubusercontent.com/x", opener=opener, host=CM.RAW_HOST)


def _pinned_manifest():
    return {
        "fleet_manifest": {"commit": FLEET_COMMIT, "sha256": "0" * 64},
        "mechs": [
            {
                "key": "traitmech",
                "github": "CultureBotAI/TraitMech",
                "record_globs": ["data/traits/**/*.yaml"],
                "commit": "b" * 40,
            }
        ],
    }


def test_remote_drift_reports_an_unreachable_network_without_raising():
    def runner(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd="git ls-remote", timeout=60)

    def opener(request, timeout):
        raise urllib.error.URLError("down")

    report = CM.remote_drift(_pinned_manifest(), runner=runner, opener=opener)
    assert {item["key"]: item["state"] for item in report} == {
        "traitmech": "UNAVAILABLE",
        "fleet-manifest": "UNAVAILABLE",
    }


def test_remote_drift_reports_fleet_membership_changes():
    head = "c" * 40

    def runner(cmd, **kwargs):
        return SimpleNamespace(returncode=0, stdout=f"{head}\tHEAD\n", stderr="")

    live = yaml.safe_dump(
        {
            "version": 1,
            "mechs": {
                "proteintraitsmech": {
                    "github": "CultureBotAI/proteintraitsmech",
                    "record_globs": ["data/traits/**/*.yaml"],
                },
                "traitmech": {
                    "github": "CultureBotAI/TraitMech",
                    "record_globs": ["data/traits/**/*.yaml"],
                },
                "dufmech": {"github": "CultureBotAI/DUFMech", "record_globs": ["data/x/*.yaml"]},
            },
        }
    ).encode()

    class Response:
        status = 200

        def __init__(self, url):
            self.url = url

        def geturl(self):
            return self.url

        def read(self, limit):
            return live

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    report = {
        item["key"]: item
        for item in CM.remote_drift(
            _pinned_manifest(), runner=runner, opener=lambda req, timeout: Response(req.full_url)
        )
    }
    assert report["traitmech"]["state"] == "MOVED"
    assert report["fleet-manifest"]["state"] == "STALE"
    assert report["fleet-manifest"]["added"] == ["dufmech CultureBotAI/DUFMech"]


def test_identifier_index_sees_edits_deletions_and_renames_under_hostile_config(tmp_path):
    traits = _trait_tree(tmp_path)
    repo = traits.parent.parent
    _git(repo, "config", "color.ui", "always")
    _git(repo, "config", "grep.fullName", "true")
    rhea = traits / "function/enzymatic_activity/rhea/r37871.yaml"
    rhea.write_text(rhea.read_text().replace("RHEA:37871", "RHEA:99999"), encoding="utf-8")
    (traits / "sequence/domain/pfam/lpp.yaml").unlink()
    _git(
        repo,
        "mv",
        "data/traits/function/molecular_function/go/dgc.yaml",
        "data/traits/function/molecular_function/go/renamed.yaml",
    )
    index = CM.build_identifier_index(traits)
    assert index["RHEA:99999"] == ["function/enzymatic_activity/rhea/r37871.yaml"]
    assert "RHEA:37871" not in index
    assert "Pfam:PF04728" not in index
    assert index["GO:0052621"] == ["function/molecular_function/go/renamed.yaml"]
    assert index["ComplexPortal:CPX-320"] == [
        "function/interaction_partner/complexportal/cpx320.yaml"
    ]


def test_glob_character_classes_follow_fnmatch():
    regex = CM.glob_to_regex("data/[ab]*/[!x]*.yaml")
    assert regex.match("data/alpha/y.yaml")
    assert not regex.match("data/gamma/y.yaml")
    assert not regex.match("data/alpha/x.yaml")


def test_strings_in_nested_and_root_lists_are_never_dropped():
    nested = CM.mention_rows("traitmech", "data/x.yaml", {"pairs": [["UniProtKB:P12345"]]})
    assert [(row["pointer"], row["role"]) for row in nested] == [("/pairs/0/0", "UNCLASSIFIED")]
    root = CM.mention_rows("traitmech", "data/x.yaml", ["UniProtKB:P12345"])
    assert [row["pointer"] for row in root] == ["/0"]


def test_proposed_steps_keep_their_qualifier_into_the_audit(tmp_path):
    document = {
        "biosynthetic_pathway": [
            {"enzyme_id": "UniProtKB:Q8GRA0", "reaction_id": "RHEA:37871", "proposed": True},
            {"enzyme_id": "UniProtKB:Q9I0Q0", "reaction_id": "RHEA:37871"},
        ]
    }
    rows = CM.mention_rows("naturalproductmech", "data/natural_products/a.yaml", document)
    by_protein = {row["protein_id"]: row for row in rows}
    assert by_protein["UniProtKB:Q8GRA0"]["annotations"][0]["qualifiers"] == {"proposed": True}
    assert "qualifiers" not in by_protein["UniProtKB:Q9I0Q0"]["annotations"][0]
    report = CM.audit(rows, traits_root=_trait_tree(tmp_path), rhea_directions=tmp_path / "x.tsv")
    pairs = {pair["protein_id"]: pair for pair in report["pairs"]}
    assert pairs["UniProtKB:Q8GRA0"]["qualifiers"] == [{"proposed": True}]
    assert pairs["UniProtKB:Q9I0Q0"]["qualifiers"] == [{}]
    assert report["summary"]["pairs_resting_only_on_proposed_claims"] == 1


def test_verification_refuses_relabelled_rows_and_wrong_mech_counts(fleet_root, tmp_path):
    root, fleet = fleet_root
    result = CM.scan(fleet, root, environ={})
    target = next(index for index, row in enumerate(result.rows) if row["role"] == "TARGET")
    result.rows[target] = {**result.rows[target], "role": "EXAMPLE"}
    text = CM.render_mentions(result.rows)
    manifest = CM.build_manifest(result, fleet, text)
    assert any("disagree with the rules" in e for e in CM.verify_snapshot(text.encode(), manifest))

    clean = CM.scan(fleet, root, environ={})
    text = CM.render_mentions(clean.rows)
    manifest = CM.build_manifest(clean, fleet, text)
    manifest["mechs"][0]["mentions"] += 1
    assert any(
        "counts do not match its rows" in e for e in CM.verify_snapshot(text.encode(), manifest)
    )


def test_local_drift_survives_a_missing_commit_and_honours_configured_roots(fleet_root, tmp_path):
    root, fleet = fleet_root
    manifest = CM.build_manifest(CM.scan(fleet, root, environ={}), fleet, "")
    relocated = tmp_path / "elsewhere"
    (root / "TraitMech").rename(relocated)
    for mech in manifest["mechs"]:
        if mech["key"] == "traitmech":
            mech["environment_variable"] = "TRAITMECH_ROOT"
        if mech["key"] == "naturalproductmech":
            mech["commit"] = "d" * 40  # not in the clone
    states = {
        item["key"]: item["state"]
        for item in CM.local_drift(manifest, root, environ={"TRAITMECH_ROOT": str(relocated)})
    }
    assert states == {"naturalproductmech": "UNAVAILABLE", "traitmech": "CURRENT"}


# -------------------------------------------------------------------- candidates


def _pair(trait_id, status, route, *, category="FUNC_LOCALIZATION", axis="FUNCTION"):
    return {
        "protein_id": "UniProtKB:P18776",
        "trait_id": trait_id,
        "status": status,
        "route": route,
        "trait_axis": axis,
        "trait_category": category,
        "record_path": f"data/traits/x/{trait_id.replace(':', '_')}.yaml",
        "sibling_curies": [trait_id],
        "relations": ["component_of_structure"],
        "mechs": ["cellstructuremech"],
        "sibling_records": ["cellstructuremech:data/structures/x.yaml"],
        "mentions": 1,
    }


def test_candidates_cover_absent_and_legacy_pairs_with_a_route_only():
    pairs = [
        _pair("GO:0009390", "ABSENT_FROM_TRAIT", "SOURCE_ANNOTATION:UniProtKB"),
        _pair("RHEA:37871", "LEGACY_ON_TRAIT", "SOURCE_MEMBERSHIP:UniProtKB"),
        _pair(
            "Pfam:PF04728",
            "ABSENT_FROM_TRAIT",
            "INTERPRO_MATCH:InterPro",
            category="SEQ_DOMAIN",
            axis="SEQUENCE",
        ),
        _pair("GO:0005886", "QUALIFIED_ON_TRAIT", "SOURCE_ANNOTATION:UniProtKB"),
        _pair("GO:7770085", "TRAIT_NOT_IN_PTM", "NONE"),
    ]
    rows = CM.candidate_rows(pairs, uniprot_release="2026_03", mentions_sha256="a" * 64)
    by_trait = {row["trait_id"]: row for row in rows}
    assert sorted(by_trait) == ["GO:0009390", "Pfam:PF04728", "RHEA:37871"]

    go = by_trait["GO:0009390"]
    assert go["mapping_method"] == "SOURCE_ANNOTATION"
    assert go["evidence_source"] == "UniProtKB"
    assert go["scope"] == "WHOLE_PROTEIN"
    assert go["source_release"] == "2026_03"
    assert go["batch"] == CM.CANDIDATE_BATCH
    assert go["cross_mech_provenance"]["snapshot_mentions_sha256"] == "a" * 64
    # Organism and sequence never come from the sibling record.
    assert not {"taxon_id", "taxon_label", "sequence_sha256"} & set(go)
    assert by_trait["RHEA:37871"]["mapping_method"] == "SOURCE_MEMBERSHIP"

    pfam = by_trait["Pfam:PF04728"]
    assert pfam["scope"] == "LOCALIZED" and pfam["mapping_method"] == "INTERPRO_MATCH"
    assert "source_release" not in pfam
    # A localized claim needs an occurrence on a known frame: kept out of the
    # whole-protein batch the selector draws from.
    assert pfam["batch"] == CM.NEEDS_OCCURRENCE_BATCH
    assert {go["batch"], by_trait["RHEA:37871"]["batch"]} == {CM.CANDIDATE_BATCH}

    ground = sys.modules["ground_uniprot_examples"]
    assert all(row["candidate_id"] == ground.derive_candidate_id(row) for row in rows)
    again = CM.candidate_rows(
        list(reversed(pairs)), uniprot_release="2026_03", mentions_sha256="a" * 64
    )
    assert again == rows


def test_candidates_refuse_a_malformed_release():
    with pytest.raises(CM.CrossMechError, match="uniprot-release"):
        CM.candidate_rows([], uniprot_release="latest", mentions_sha256="a" * 64)
