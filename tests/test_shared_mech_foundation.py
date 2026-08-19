"""The shared Mech curation foundation (#484).

Three things are worth pinning here, and none of them is "does LinkML work".

  * the VENDORING CONTRACT — `mech_shared.yaml` and the id-label validator are carried
    byte-identical from the hub, so the failure to catch is a well-meant local edit;
  * the WIRING — the schema imports the shared module and exposes its classes, which is
    the difference between vendoring a file and adopting it;
  * the HISTORY LAYER's split enforcement — validity hard, presence advisory. That split
    is easy to state and easy to implement backwards, and neither half was checked by
    anything until this file.

The drift check itself is network-bound (it fetches the hub at a pinned commit), so the
tests here assert the things that hold offline: that the contract's inputs exist, that
the local copies are the ones the check governs, and that the schema really uses them.
"""

from __future__ import annotations

import pathlib
import re
import subprocess
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCHEMA_DIR = REPO / "src" / "proteintraitsmech" / "schema"


# --- the vendoring contract --------------------------------------------------------------

def test_the_pinned_canon_ref_exists_and_is_a_commit_sha():
    """The drift check exits 2 without this, which is right -- but a missing pin should
    fail loudly at the file, not at a curl 404 forty lines later."""
    ref = (REPO / "scripts" / ".vendored_canon_ref").read_text().strip()
    assert re.fullmatch(r"[0-9a-f]{40}", ref), f"not a full commit sha: {ref!r}"


def test_every_governed_file_is_actually_present():
    """`check_vendored_sync.sh` reports MISSING and fails for an absent file. This says the
    same thing without a network round trip, so the common case is caught in the unit
    suite rather than only in CI."""
    script = (REPO / "scripts" / "check_vendored_sync.sh").read_text()
    same_path = re.search(r"^FILES=\(\n(.*?)^\)", script, re.M | re.S).group(1)
    # THE SET'S MEMBERSHIP, not just "every listed file exists". Emptying `FILES=()`
    # made this pass while the gate cheerfully reported "OK: all 1 vendored files" --
    # a test that certifies a contract is only as good as its check that the contract
    # still has anything in it. Named explicitly so dropping one to "simplify" fails
    # here rather than silently freeing that file to drift.
    listed = {ln.strip() for ln in same_path.strip().splitlines()
              if ln.strip() and not ln.strip().startswith("#")}
    assert listed == {
        "scripts/validate_id_label_correspondence.py",
        "scripts/chem_formula.py",
        "tests/test_id_label_empty_adapter.py",
        "tests/test_id_label_unknown_prefix.py",
        "tests/test_id_label_plausibility.py",
    }, f"the governed same-path set changed: {sorted(listed)}"
    for line in same_path.strip().splitlines():
        rel = line.strip()
        if not rel or rel.startswith("#"):
            continue
        assert (REPO / rel).is_file(), f"governed file missing: {rel}"
    mapped = re.search(r"^MAPPED=\(\n(.*?)^\)", script, re.M | re.S).group(1)
    for line in mapped.strip().splitlines():
        entry = line.strip().strip('"')
        if not entry or entry.startswith("#"):
            continue
        glob = entry.split("|", 1)[0]
        assert list(REPO.glob(glob)), f"no local file matches governed glob: {glob}"


def test_the_vendored_module_is_not_edited_locally_in_the_obvious_way():
    """A full byte-comparison needs the hub, so this catches only the crude tell: a local
    edit that leaves a marker behind. The real gate is `just check-vendored-sync`; this is
    the cheap one that runs on every `just test`."""
    text = (SCHEMA_DIR / "mech_shared.yaml").read_text()
    assert "proteintraitsmech" not in text.lower(), (
        "the vendored shared module names this repo -- it has been localised, which the "
        "drift check will fail")
    # keyed on the module's IDENTITY, not on a sentence of upstream prose -- a legitimate
    # re-vendor that rewords the description should not turn this red.
    assert yaml.safe_load(text)["name"] == "mech_shared"


# --- the wiring, which is the difference between vendoring and adopting -------------------

def test_the_schema_imports_the_shared_module():
    schema = yaml.safe_load((SCHEMA_DIR / "proteintraitsmech.yaml").read_text())
    assert "mech_shared" in schema["imports"]


@pytest.mark.parametrize("slot,cls", [("discussions", "Discussion"), ("datasets", "Dataset")])
def test_the_record_exposes_the_shared_classes(slot, cls):
    schema = yaml.safe_load((SCHEMA_DIR / "proteintraitsmech.yaml").read_text())
    attrs = schema["classes"]["ProteinTraitRecord"]["attributes"]
    assert slot in attrs, f"ProteinTraitRecord has no {slot}"
    assert attrs[slot]["range"] == cls
    assert attrs[slot]["multivalued"] is True


def test_a_record_carrying_a_discussion_validates():
    """A valid discussion passes. Paired with the test below, which is the half that
    actually detects a missing import."""
    rec = {
        "identifier": "Pfam:PF00001", "label": "x",
        "definition": "A trait.", "trait_axis": "SEQUENCE",
        "trait_category": "SEQ_DOMAIN", "term_kind": "CLASS",
        # `discussion_id` and `prompt`, not `id`/`title`. Written out rather than
        # guessed: the closed validator rejected the guess by name, which is the
        # behaviour this test is here to rely on.
        "discussions": [{
            "discussion_id": "gap-1", "kind": "KNOWLEDGE_GAP", "status": "OPEN",
            "prompt": "No structural evidence for the proposed mechanism.",
        }],
    }
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as fh:
        yaml.safe_dump(rec, fh, sort_keys=False)
        path = fh.name
    # the repo's OWN strict validator, not a bare linkml call: closed mode is the gate
    # that matters, and it is the one that would reject a slot the import failed to bring
    # in. Running the real thing also means this test cannot pass against a laxer path.
    out = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "validate_strict.py"), path],
        capture_output=True, text=True, cwd=REPO)
    assert out.returncode == 0, out.stdout + out.stderr


def test_a_BOGUS_slot_inside_a_discussion_is_REJECTED(tmp_path):
    """This is the test that proves the import RESOLVED, and the one above is not.

    A review removed `- mech_shared` from `imports` and the positive test stayed green:
    with the range unresolved, closed mode simply stops constraining the section, so a
    valid instance still validates. The degradation is invisible from the passing side --
    it is only visible from the side that should FAIL. Without the import, both a bogus
    nested slot and a bogus enum value are accepted with exit 0.

    Same shape as everything else in this repo's recent history: a guarantee stated by a
    test that only ever exercises the happy path.
    """
    rec = tmp_path / "r.yaml"
    rec.write_text(yaml.safe_dump({
        "identifier": "Pfam:PF00001", "label": "x", "definition": "A trait.",
        "trait_axis": "SEQUENCE", "trait_category": "SEQ_DOMAIN", "term_kind": "CLASS",
        "discussions": [{"discussion_id": "g", "kind": "KNOWLEDGE_GAP", "status": "OPEN",
                         "prompt": "p", "not_a_real_slot": "x"}],
    }, sort_keys=False), encoding="utf-8")
    out = subprocess.run([sys.executable, str(REPO / "scripts" / "validate_strict.py"),
                          str(rec)], capture_output=True, text=True, cwd=REPO)
    assert out.returncode != 0, (
        "closed mode accepted an undeclared slot inside a Discussion -- the shared module "
        "is imported but not constraining anything\n" + out.stdout)


def test_a_BOGUS_enum_value_in_a_discussion_is_REJECTED(tmp_path):
    """The second half of the same degradation."""
    rec = tmp_path / "r.yaml"
    rec.write_text(yaml.safe_dump({
        "identifier": "Pfam:PF00001", "label": "x", "definition": "A trait.",
        "trait_axis": "SEQUENCE", "trait_category": "SEQ_DOMAIN", "term_kind": "CLASS",
        "discussions": [{"discussion_id": "g", "kind": "NOT_A_KIND", "status": "OPEN",
                         "prompt": "p"}],
    }, sort_keys=False), encoding="utf-8")
    out = subprocess.run([sys.executable, str(REPO / "scripts" / "validate_strict.py"),
                          str(rec)], capture_output=True, text=True, cwd=REPO)
    assert out.returncode != 0, out.stdout


# --- the history layer's split enforcement ------------------------------------------------

def test_the_history_schema_is_vendored_and_defines_the_target_class():
    schema = yaml.safe_load((SCHEMA_DIR / "history.yaml").read_text())
    assert "HistoryRecord" in schema["classes"]


def test_validate_history_REJECTS_a_malformed_record(tmp_path):
    """Validity is the hard half. A record that exists and is wrong must fail."""
    bad = tmp_path / "records" / "x" / "bad.yaml"
    bad.parent.mkdir(parents=True)
    bad.write_text("history_version: 1\ntarget: {kind: not_a_kind}\n", encoding="utf-8")
    out = subprocess.run(["just", "validate-history", str(tmp_path)],
                         capture_output=True, text=True, cwd=REPO)
    assert out.returncode != 0, out.stdout + out.stderr


def test_validate_history_ACCEPTS_an_empty_tree(tmp_path):
    """Presence is the advisory half: no records is not a failure. Asserted because it is
    exactly the behaviour a well-meaning tightening would remove, and because #484's
    acceptance criteria ask for the opposite -- see docs/fleet-parity.md."""
    out = subprocess.run(["just", "validate-history", str(tmp_path)],
                         capture_output=True, text=True, cwd=REPO)
    assert out.returncode == 0, out.stdout + out.stderr
    assert "No history records" in out.stdout


def test_the_committed_history_records_are_valid():
    out = subprocess.run(["just", "validate-history"], capture_output=True, text=True,
                         cwd=REPO)
    assert out.returncode == 0, out.stdout + out.stderr


def test_the_scaffolder_writes_a_valid_record_with_a_collision_free_name(tmp_path):
    """Two runs for the same target must not produce the same filename -- that property is
    the entire reason for the directory-per-slug + shortid layout, and nothing else checks
    it."""
    names = set()
    for _ in range(2):
        out = subprocess.run(
            [sys.executable, str(REPO / "scripts" / "new_history_record.py"),
             "--kind", "record", "--slug", "same-target", "--path", "data/traits/x.yaml",
             "--event", "EDIT", "--outcome", "changed", "--summary", "s",
             "--history-root", str(tmp_path)],
            capture_output=True, text=True, cwd=REPO)
        assert out.returncode == 0, out.stdout + out.stderr
        names.add(out.stdout.strip().splitlines()[-1])
    assert len(names) == 2, f"the scaffolder reused a filename: {names}"
    written = list(tmp_path.rglob("*.yaml"))
    assert len(written) == 2
    for path in written:
        doc = yaml.safe_load(path.read_text())
        assert doc["target"]["kind"] == "record"
        assert doc["events"][0]["type"] == "EDIT"


# --- the CI wiring, which is where a gate quietly stops running --------------------------

def test_validate_strict_fires_when_the_SHARED_module_changes():
    """The schema now IMPORTS mech_shared, so a change there changes what validate-strict
    validates. Its trigger listed only the main schema path, so the gate would not have
    fired on the import -- a gate that stops covering its own inputs."""
    wf = (REPO / ".github" / "workflows" / "validate-strict.yaml").read_text()
    assert wf.count("src/proteintraitsmech/schema/mech_shared.yaml") == 2, (
        "mech_shared must be in BOTH the pull_request and push path filters")


def test_the_vendored_sync_job_needs_no_python():
    """It is a fast blocking job on purpose. If it grows a uv/linkml dependency it stops
    being able to fail in seconds, and the fleet loses its cheapest guard."""
    wf = yaml.safe_load((REPO / ".github" / "workflows" / "history-and-vendored.yaml")
                        .read_text())
    steps = wf["jobs"]["vendored-sync"]["steps"]
    assert not any("uv" in str(s).lower() or "python" in str(s).lower() for s in steps), steps
