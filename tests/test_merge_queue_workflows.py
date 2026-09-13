"""Required checks must evaluate both PRs and native merge-group commits."""

import os
import subprocess
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
REQUIRED_WORKFLOWS = {
    "checks.yml": ["checks"],
    "history-and-vendored.yaml": ["vendored-sync", "validate-history"],
    "validate-strict.yaml": ["validate-strict"],
}


@pytest.mark.parametrize("filename", REQUIRED_WORKFLOWS)
def test_required_workflow_reports_for_every_pr_and_merge_group(filename):
    document = yaml.safe_load((ROOT / ".github/workflows" / filename).read_text())
    events = document.get("on", document.get(True))
    assert "pull_request" in events
    assert not events["pull_request"], "workflow filters can leave a required PR check pending"
    assert events["merge_group"] == {"types": ["checks_requested"]}
    assert document["permissions"] == {"contents": "read"}
    concurrency = document["concurrency"]
    assert concurrency["cancel-in-progress"] == "${{ github.event_name == 'pull_request' }}"
    assert "github.run_id" in concurrency["group"]
    for job in document["jobs"].values():
        assert "if" not in job, "a required job must not skip the queue commit"
        for step in job.get("steps", []):
            if step.get("uses", "").startswith("actions/checkout@"):
                assert "ref" not in step.get("with", {}), (
                    "checkout must evaluate the event's combined commit"
                )


def test_required_job_contexts_remain_stable():
    for filename, expected in REQUIRED_WORKFLOWS.items():
        document = yaml.safe_load((ROOT / ".github/workflows" / filename).read_text())
        observed = []
        for job_id, job in document["jobs"].items():
            versions = job.get("strategy", {}).get("matrix", {}).get("python-version")
            if "uses" in job:
                observed.append(f"{job_id} / {job_id}")
            elif versions:
                for version in versions:
                    name = job.get("name")
                    observed.append(
                        name.replace("${{ matrix.python-version }}", version)
                        if name
                        else f"{job_id} ({version})"
                    )
            else:
                observed.append(job.get("name", job_id))
        assert sorted(observed) == sorted(expected)


def test_merge_group_validates_the_full_corpus_without_pr_fields(tmp_path):
    document = yaml.safe_load((ROOT / ".github/workflows/validate-strict.yaml").read_text())
    step = next(s for s in document["jobs"]["validate-strict"]["steps"] if s.get("id") == "scope")
    run = step["run"].replace("${{ github.event_name }}", "merge_group")
    run = run.replace("${{ github.event.pull_request.base.sha }}", "")
    run = run.replace("${{ github.event.pull_request.head.sha }}", "")
    output = tmp_path / "output"
    result = subprocess.run(
        ["bash", "-c", run],
        cwd=tmp_path,
        env={**os.environ, "GITHUB_OUTPUT": str(output)},
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert output.read_text().splitlines() == ["mode=full", "changed_count=0"]
