"""Independent CI object-restoration probes, 2026-10-29, PTM issue #1206.

Purpose: exercise the exact checks.yml shell step in disposable local Git trees.
Inputs: the current workflow, immutable native review helper and historical
review bytes. Outputs: new timestamped probe JSON beside this retained helper.
The production pin is asserted exactly. For each fixture, only that one literal
SHA in the extracted shell body is replaced with the fixture's SHA. No other
shell transformation is made. All Git mutations and fetches are confined to
temporary repositories using a local filesystem origin; no GitHub/network,
real worktree Git mutation, scientific test, session or goal action occurs.
Temporary fixture paths are diagnostic, not retained or portable dependencies.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

import yaml


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WORKFLOW = ROOT / ".github/workflows/checks.yml"
PRODUCTION_PIN = "93c1a021d76a94fd299e0a1e3cf8f1b9671a3703"
ENV = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
       "GIT_TERMINAL_PROMPT": "0"}


def run(directory: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=directory, env=ENV, capture_output=True,
                          text=True, check=check)


def git(directory: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return run(directory, "git", *args, check=check)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def pin(path: Path) -> dict:
    raw = path.read_bytes()
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(raw), "bytes": len(raw)}


def refs(directory: Path) -> str:
    return git(directory, "for-each-ref", "--format=%(refname) %(objectname)").stdout


def state(directory: Path) -> dict:
    metadata = directory / ".git"
    return {
        "head_commit": git(directory, "rev-parse", "HEAD").stdout.strip(),
        "refs": refs(directory),
        "protected_bytes": {name: sha((metadata / name).read_bytes())
                            for name in ("HEAD", "index", "FETCH_HEAD", "config")},
        "worktree_bytes": {name: sha((directory / name).read_bytes())
                           for name in ("tracked.txt", "staged.txt", "untracked.txt")},
    }


def clone_fixture(parent: Path, origin: Path, name: str) -> Path:
    client = parent / name
    git(parent, "clone", "--no-local", "--single-branch", "--branch", "main",
        str(origin), str(client))
    git(client, "config", "protocol.file.allow", "always")
    (client / "tracked.txt").write_text("unstaged fixture change\n")
    (client / "staged.txt").write_text("staged fixture change\n")
    git(client, "add", "staged.txt")
    (client / "untracked.txt").write_text("untracked fixture content\n")
    (client / ".git/FETCH_HEAD").write_text("preserve this pre-existing FETCH_HEAD fixture\n")
    return client


def execute_case(client: Path, origin: Path, script: str, fixture_pin: str,
                 name: str, expect_success: bool, expected_before: bool) -> dict:
    substituted = script.replace(PRODUCTION_PIN, fixture_pin)
    assert substituted.replace(fixture_pin, PRODUCTION_PIN) == script
    before = state(client)
    remote_before = refs(origin)
    available_before = git(client, "cat-file", "-e", fixture_pin + "^{commit}", check=False).returncode == 0
    assert available_before is expected_before
    result = run(client, "bash", "--noprofile", "--norc", "-c", substituted, check=False)
    after = state(client)
    assert before == after, (name, before, after)
    assert refs(origin) == remote_before
    assert (result.returncode == 0) is expect_success, (name, result.stderr)
    available_after = git(client, "cat-file", "-e", fixture_pin + "^{commit}", check=False).returncode == 0
    if expect_success:
        assert available_after
        assert git(client, "rev-parse", "--verify", fixture_pin + "^{commit}").stdout.strip() == fixture_pin
    else:
        assert not available_after
    return {"case": name, "fixture_pin": fixture_pin,
            "production_pin_substitution_only": True,
            "production_shell_sha256": sha(script.encode()),
            "executed_fixture_shell_sha256": sha(substituted.encode()),
            "object_available_before": available_before, "object_available_after": available_after,
            "exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr,
            "head_refs_index_fetch_head_config_worktree_preserved": True,
            "local_origin_refs_preserved": True, "state_before_and_after": before}


def main() -> None:
    raw = WORKFLOW.read_bytes()
    workflow = yaml.safe_load(raw)
    steps = workflow["jobs"]["checks"]["steps"]
    selected = [step for step in steps if step.get("name") == "Restore inherited review Git base"]
    assert len(selected) == 1
    step = selected[0]
    script = step["run"]
    assert script.count(PRODUCTION_PIN) == 1
    assert "review_revision=" + PRODUCTION_PIN in script
    assert "git fetch --no-tags --no-write-fetch-head origin \"$review_revision\"" in script
    assert script.startswith("set -euo pipefail\n")
    assert steps[steps.index(step) + 1]["name"] == "Structured record review contract"
    inputs = [pin(WORKFLOW), pin(Path(__file__)), pin(ROOT / "scripts/record_review.py"),
              pin(ROOT / "docs/record-reviews.md"), pin(ROOT / "tests/test_record_review_contract.py"),
              pin(ROOT / "reviews/structured/20261029T044503Z-structural-ledger-guard-followup/review.yaml")]
    with tempfile.TemporaryDirectory(prefix="ptm-ci-provenance-probe-") as temporary:
        parent = Path(temporary)
        origin = parent / "local-origin"
        git(parent, "init", "--initial-branch=main", str(origin))
        git(origin, "config", "user.name", "Synthetic fixture")
        git(origin, "config", "user.email", "fixture@example.invalid")
        (origin / "tracked.txt").write_text("initial fixture\n")
        git(origin, "add", "tracked.txt")
        git(origin, "commit", "-m", "Synthetic main history")
        git(origin, "switch", "-c", "synthetic-old-review")
        (origin / "historical.txt").write_text("historical object available only through retained fixture PR ref\n")
        git(origin, "add", "historical.txt")
        git(origin, "commit", "-m", "Synthetic review-base commit")
        fixture_pin = git(origin, "rev-parse", "HEAD").stdout.strip()
        git(origin, "update-ref", "refs/pull/1202/head", fixture_pin)
        git(origin, "switch", "main")
        git(origin, "branch", "-D", "synthetic-old-review")
        client = clone_fixture(parent, origin, "missing-client")
        missing = execute_case(client, origin, script, fixture_pin,
                               "missing_commit_fetched_from_local_origin", True, False)
        git(client, "remote", "set-url", "origin", str(parent / "nonexistent-origin"))
        present = execute_case(client, origin, script, fixture_pin,
                               "already_present_succeeds_with_unavailable_origin", True, True)
        unavailable = clone_fixture(parent, origin, "unavailable-client")
        absent_pin = "f" * 40
        assert git(origin, "cat-file", "-e", absent_pin, check=False).returncode != 0
        absent = execute_case(unavailable, origin, script, absent_pin,
                              "unavailable_pin_fails_closed", False, False)
    assert WORKFLOW.read_bytes() == raw
    timestamp = dt.datetime.now(dt.timezone.utc)
    result = {
        "created_utc": timestamp.isoformat(), "reviewer": "Codex agent /root/preflight_boundary_review",
        "issue": "https://github.com/CultureBotAI/proteintraitsmech/issues/1206",
        "purpose": "Independent exact-shell local Git fixture probes; no actual remote fetch or scientific test",
        "inputs": inputs, "production_pin": PRODUCTION_PIN, "production_pin_exact": True,
        "production_shell": script, "cases": [missing, present, absent], "all_passed": True,
        "limits": ["Fixture substitutions replace only the production SHA literal; they do not establish GitHub availability of the production object.",
                   "All fixture repositories, refs and files were disposable local directories, removed after probes. Absolute fixture paths in stderr are historical diagnostic context only.",
                   "Native provenance semantics and immutable review content were inspected, not executed or modified. Actual required CI at the new head remains necessary.",
                   "The only real-worktree write is this new probe report; no actual Git refs, HEAD, index, corpus, goal or sessions were mutated."],
    }
    destination = HERE / ("restore-base-probes-" + timestamp.strftime("%Y%m%dT%H%M%S%fZ") + ".json")
    with destination.open("x") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"output": str(destination.relative_to(ROOT)), "sha256": sha(destination.read_bytes()),
                      "all_passed": True, "cases": len(result["cases"]), "workflow_sha256": sha(raw)}))


if __name__ == "__main__":
    main()
