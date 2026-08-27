"""The shared Mech curation foundation (#484).

Three things are worth pinning here, and none of them is "does LinkML work".

  * the VENDORING CONTRACT — `mech_shared.yaml` and the id-label validator are carried
    byte-identical from claw, so the failure to catch is a well-meant local edit;
  * the WIRING — the schema imports the shared module and exposes its classes, which is
    the difference between vendoring a file and adopting it;
  * the HISTORY LAYER's split enforcement — validity hard, presence advisory. That split
    is easy to state and easy to implement backwards, and neither half was checked by
    anything until this file.

The production drift check is network-bound (it fetches claw at a pinned commit), so the
tests here inject local manifest/payload fixtures and exercise the checker and workflow
offline. They also prove that the schema really uses the governed shared modules.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import pathlib
import re
import subprocess
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCHEMA_DIR = REPO / "src" / "proteintraitsmech" / "schema"
CHECKER_PATH = REPO / "scripts" / "check_vendored_sync.py"


def _load_vendored_checker():
    spec = importlib.util.spec_from_file_location(
        "proteintraitsmech_vendored_sync_checker", CHECKER_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    # dataclasses resolves postponed annotations through the defining module.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


# --- the vendoring contract --------------------------------------------------------------

def test_the_pinned_canon_ref_exists_and_is_a_commit_sha():
    """The drift check exits 2 without this, which is right -- but a missing pin should
    fail loudly at the file, not at a curl 404 forty lines later."""
    ref = (REPO / "scripts" / ".vendored_canon_ref").read_text().strip()
    assert re.fullmatch(r"[0-9a-f]{40}", ref), f"not a full commit sha: {ref!r}"


def test_the_launcher_delegates_to_the_manifest_driven_checker_in_isolated_mode():
    """The shell no longer carries a second FILES/MAPPED source of truth."""
    launcher = (REPO / "scripts" / "check_vendored_sync.sh").read_text()
    assert "FILES=(" not in launcher
    assert "MAPPED=(" not in launcher
    assert 'exec python3 -I "${SCRIPT_DIR}/check_vendored_sync.py" "$@"' in launcher
    checker = _load_vendored_checker()
    assert checker.CANONICAL_REPOSITORY == "CultureBotAI/culturebotai-claw"
    assert checker.CANONICAL_MANIFEST_PATH.endswith("/vendored_artifacts.json")


def test_the_checker_reads_a_claw_manifest_and_expands_the_protein_package_offline(tmp_path):
    """Exercise the new manifest contract without fetching claw or any paid service."""
    checker = _load_vendored_checker()
    root = tmp_path / "consumer"
    root.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(
        [
            "git",
            "remote",
            "add",
            "origin",
            "https://github.com/CultureBotAI/proteintraitsmech.git",
        ],
        cwd=root,
        check=True,
    )

    pin = "a" * 40
    pin_path = root / "scripts" / ".vendored_canon_ref"
    pin_path.parent.mkdir()
    pin_path.write_text(pin + "\n", encoding="ascii")
    payload = b"name: governed-history\n"
    source = "src/kg_microbe_governance/artifacts/schema/history.yaml"
    target = root / "src" / "proteintraitsmech" / "schema" / "history.yaml"
    target.parent.mkdir(parents=True)
    target.write_bytes(payload)
    manifest = json.dumps(
        {
            "version": 1,
            "canonical_repository": "CultureBotAI/culturebotai-claw",
            "pin_path": "scripts/.vendored_canon_ref",
            "consumers": {
                "proteintraitsmech": {
                    "github": "CultureBotAI/proteintraitsmech",
                    "package_path": "src/proteintraitsmech",
                }
            },
            "artifacts": [
                {
                    "id": "history_schema",
                    "source": source,
                    "target": "{package_path}/schema/history.yaml",
                    "consumers": "all",
                    "sha256": hashlib.sha256(payload).hexdigest(),
                    "mode": "0644",
                }
            ],
        }
    ).encode()
    responses = {
        checker.raw_url(pin, checker.CANONICAL_MANIFEST_PATH): manifest,
        checker.raw_url(pin, source): payload,
    }
    requested = []

    def fetch(url):
        requested.append(url)
        return responses[url]

    checked, problems = checker.check_repository(root, fetch=fetch)
    assert checked == 1
    assert problems == ()
    assert requested == list(responses)


def test_the_vendored_module_is_not_edited_locally_in_the_obvious_way():
    """A full byte-comparison needs claw, so this catches only the crude tell: a local
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


def _vendored_sync_workflow():
    return yaml.safe_load(
        (REPO / ".github" / "workflows" / "history-and-vendored.yaml").read_text()
    )


def _run_vendored_sync_workflow(tmp_path, statuses):
    """Run the checked-in Actions shell block against a deterministic offline checker."""
    wf = _vendored_sync_workflow()
    steps = wf["jobs"]["vendored-sync"]["steps"]
    run = next(step["run"] for step in steps if step.get("name") ==
               "Verify vendored files match canonical claw")

    sandbox = tmp_path / "workflow"
    scripts = sandbox / "scripts"
    fake_bin = sandbox / "bin"
    scripts.mkdir(parents=True)
    fake_bin.mkdir()
    attempts = sandbox / "attempts"
    attempts.write_text("", encoding="ascii")
    sequence = sandbox / "statuses"
    sequence.write_text("".join(f"{status}\n" for status in statuses), encoding="ascii")
    sleeps = sandbox / "sleeps"
    sleeps.write_text("", encoding="ascii")
    (scripts / "check_vendored_sync.sh").write_text(
        """#!/usr/bin/env bash
set -u
attempt=$(( $(wc -l < "${ATTEMPT_LOG:?}") + 1 ))
printf '%s\\n' "$attempt" >> "$ATTEMPT_LOG"
status=$(sed -n "${attempt}p" "${STATUS_SEQUENCE:?}")
exit "$status"
""",
        encoding="ascii",
    )
    sleep = fake_bin / "sleep"
    sleep.write_text(
        "#!/usr/bin/env bash\nprintf '%s\\n' \"$*\" >> \"${SLEEP_LOG:?}\"\n",
        encoding="ascii",
    )
    sleep.chmod(0o755)
    result = subprocess.run(
        ["bash", "-c", run],
        cwd=sandbox,
        text=True,
        capture_output=True,
        env={
            **os.environ,
            "PATH": f"{fake_bin}{os.pathsep}{os.environ['PATH']}",
            "ATTEMPT_LOG": str(attempts),
            "STATUS_SEQUENCE": str(sequence),
            "SLEEP_LOG": str(sleeps),
        },
    )
    return result, attempts.read_text().splitlines(), sleeps.read_text().splitlines()


def test_the_vendored_sync_job_needs_no_project_dependency_install():
    """The standard-library checker remains a cheap blocking job with no uv install."""
    wf = _vendored_sync_workflow()
    triggers = wf.get("on", wf.get(True))
    steps = wf["jobs"]["vendored-sync"]["steps"]
    serialized = " ".join(str(step).lower() for step in steps)
    assert all("paths" not in (config or {}) for config in triggers.values())
    assert wf["jobs"]["vendored-sync"]["timeout-minutes"] == 5
    assert "setup-uv" not in serialized
    assert "pip install" not in serialized
    assert "uv sync" not in serialized


def test_vendored_sync_retries_exit_one_and_recovers_offline(tmp_path):
    result, attempts, sleeps = _run_vendored_sync_workflow(tmp_path, [1, 0])
    assert result.returncode == 0, result.stdout + result.stderr
    assert attempts == ["1", "2"]
    assert sleeps == ["5"]


def test_vendored_sync_retries_exit_one_three_times_then_fails_offline(tmp_path):
    result, attempts, sleeps = _run_vendored_sync_workflow(tmp_path, [1, 1, 1])
    assert result.returncode == 1, result.stdout + result.stderr
    assert attempts == ["1", "2", "3"]
    assert sleeps == ["5", "5"]


def test_vendored_sync_exit_two_is_an_immediate_precondition_failure_offline(tmp_path):
    result, attempts, sleeps = _run_vendored_sync_workflow(tmp_path, [2])
    assert result.returncode == 2, result.stdout + result.stderr
    assert attempts == ["1"]
    assert sleeps == []


def test_vendored_sync_unexpected_exit_fails_closed_without_retry_offline(tmp_path):
    result, attempts, sleeps = _run_vendored_sync_workflow(tmp_path, [99])
    assert result.returncode == 99, result.stdout + result.stderr
    assert attempts == ["1"]
    assert sleeps == []


def test_vendored_sync_sparse_checkout_carries_every_governed_directory():
    """A governed file omitted by sparse checkout looks missing only in CI."""
    wf = yaml.safe_load(
        (REPO / ".github" / "workflows" / "history-and-vendored.yaml").read_text()
    )
    checkout = wf["jobs"]["vendored-sync"]["steps"][0]["with"]["sparse-checkout"]
    assert set(checkout.split()) >= {"scripts", "src", "tests", "prompts"}
