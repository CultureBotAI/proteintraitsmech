#!/usr/bin/env python3
"""Native beta-arch review evidence capture, 2026-10-29; discovery goal / #1200.

Purpose: capture exact inputs before independent judgement, run scoped native
validators, and retain their real output. It does not author a scientific verdict.
Inputs: current beta-arch record, maintained discovery manifest/emitter, native
rubrics/schema and already inspected motif sources named in INPUTS.
Outputs: new timestamped sibling directory containing targets.yaml, inspect.json,
checks.json, validator logs and TSVs. No records, Git, or immutable reviews change.
Requires the owned repository .venv. No network. Fail rather than overwrite.
"""
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess
import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PYTHON = ROOT / ".venv/bin/python"
TARGET = "data/traits/structure/secondary/beta-arch.yaml"
IDENTIFIER = "proteintraitsmech:BETA_ARCH"
INPUTS = [
    # CLAUDE.md is a symlink to AGENTS.md; native inspect rejects symlink paths.
    "AGENTS.md", "justfile", "docs/record-reviews.md",
    "docs/record-review-profile.md", "conf/record_review.yaml",
    ".claude/skills/review-yaml-record/SKILL.md",
    ".claude/skills/curate-yaml-record/references/review-checklist.md",
    "schema/record_review.yaml", "src/proteintraitsmech/schema/proteintraitsmech.yaml",
    "data/curation/structural_trait_discovery.yaml", "scripts/seed_structural_discovery.py",
    "data/traits/structure/secondary/super-secondary-motif.yaml",
    "data/traits/structure/secondary/polypeptide-structural-motif.yaml",
    "research/structural-discovery-20261028/motifs/ranked-candidate-cards.json",
    "research/structural-discovery-20261028/motifs/natcomm-2022-immunoglobulin.xml",
    "research/structural-discovery-20261028/cavities/motif-candidate-independent-review.json",
    "research/structural-discovery-20261028/cavities/prepare_beta_arch_review.py",
]


def main():
    assert (ROOT / TARGET).is_file(), "Emission has not completed"
    start = dt.datetime.now(dt.timezone.utc)
    out = HERE / ("beta-arch-native-" + start.strftime("%Y%m%dT%H%M%SZ"))
    out.mkdir(exist_ok=False)
    owner_paths = [
        {"repository": "CultureBotAI/proteintraitsmech", "path": p, "role": role}
        for p, role in [
            ("data/curation/structural_trait_discovery.yaml", "Maintained discovery record content"),
            ("scripts/seed_structural_discovery.py", "Native validated discovery emitter"),
        ]
    ]
    targets = {"targets": [{"target_id": IDENTIFIER, "path": TARGET, "label": "beta arch",
                             "record_class": "ProteinTraitRecord", "kind": "generated",
                             "owner_paths": owner_paths}]}
    (out / "targets.yaml").write_text(yaml.safe_dump(targets, sort_keys=False))
    cmd = [str(PYTHON), "scripts/record_review.py", "inspect", "--targets", str(out / "targets.yaml")]
    for p in INPUTS:
        cmd += ["--input", p]
    inspected = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=False)
    (out / "inspect.log").write_text(inspected.stdout + inspected.stderr)
    if inspected.returncode:
        raise RuntimeError(inspected.stderr)
    capture = json.loads(inspected.stdout)
    (out / "inspect.json").write_text(json.dumps(capture, indent=2) + "\n")
    checks = []
    commands = {
        "strict": [str(PYTHON), "scripts/validate_strict.py", "--workers", "1", "--out", str(out / "strict.tsv"), TARGET],
        "graphs": [str(PYTHON), "scripts/audit_causal_graphs.py", TARGET],
        "grounding": [str(PYTHON), "scripts/validate_uniprot_grounding.py", TARGET, "--out", str(out / "grounding.tsv")],
    }
    for key, command in commands.items():
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
        (out / (key + ".log")).write_text(result.stdout + result.stderr)
        checks.append({"check_id": key, "command": command, "exit_code": result.returncode,
                       "log": str((out / (key + ".log")).relative_to(ROOT))})
    manifest = yaml.safe_load((ROOT / "data/curation/structural_trait_discovery.yaml").read_text())
    row = next(r["record"] for r in manifest["records"] if r["path"] == TARGET)
    record = yaml.safe_load((ROOT / TARGET).read_text())
    unchanged = all(hashlib.sha256((ROOT / r["path"]).read_bytes()).hexdigest() == r["sha256"]
                    for r in capture["source"]["inputs"])
    results = {"started_at": start.isoformat().replace("+00:00", "Z"),
               "finished_at": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
               "checks": checks, "manifest_equals_emitted_record": row == record,
               "all_inspected_inputs_unchanged": unchanged}
    (out / "checks.json").write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps({"output": str(out.relative_to(ROOT)), **results}, indent=2))


if __name__ == "__main__":
    main()
