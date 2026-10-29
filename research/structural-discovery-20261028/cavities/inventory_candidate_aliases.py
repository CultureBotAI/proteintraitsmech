"""Read-only candidate alias inventory, 2026-10-28.

Goal: parent-owned structural-discovery goal, discover/structural-traits-20261028-04f08f.
Purpose: distinguish candidate cavity/pocket classes from existing records and staging.
Inputs: all data/traits YAMLs, data/research/scripts/conf text, docs/data/labels.json.
Outputs: sibling alias-inventory.json. No scientific files or indexes are changed.
Uses rg --no-ignore --hidden so ignored/staging files are included.
"""
import datetime
import hashlib
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).with_name("alias-inventory.json")
PATTERNS = {
    "tunnel_bottleneck": r"bottleneck|narrowest[ _-]+(?:part|region|pathway)|tunnel[ _-]+(?:neck|gorge|constriction)|(?:neck|constriction)[ _-]+of[ _-]+(?:the[ _-]+)?tunnel",
    "membrane_fenestration": r"fenestrat|lateral[ _-]+portal",
    "pocket_subcompartment": r"sub[ _-]*pocket|sub[ _-]*cavit|pocket[ _-]+subcompartment",
    "intersubunit_packing_cavity": r"(?:inter[ _-]*subunit|inter[ _-]*chain|interfacial).{0,35}(?:cavit|pocket)|(?:cavit|pocket).{0,35}(?:inter[ _-]*subunit|inter[ _-]*chain|interfacial)",
    "interdomain_packing_cavity": r"inter[ _-]*domain.{0,35}(?:cavit|pocket)|(?:cavit|pocket).{0,35}inter[ _-]*domain",
    "generic_cryptic_pocket": r"cryptic.{0,20}(?:site|pocket)|transient.{0,20}pocket",
    "channel_vestibule": r"vestibul",
    "branched_tunnel": r"branch.{0,20}(?:tunnel|channel)|(?:tunnel|channel).{0,20}branch",
}


def run_rg(pattern, paths, fields=False):
    command = ["rg", "--no-ignore", "--hidden", "--line-number", "--ignore-case"]
    if fields:
        pattern = r"^(identifier|label|[ \t-]*synonym_text):.*(" + pattern + ")"
        command += ["--glob", "*.yaml"]
    else:
        command += ["--glob", "!structural-discovery-20261028/**", "--glob", "*.yaml", "--glob", "*.yml", "--glob", "*.json", "--glob", "*.md", "--glob", "*.py", "--max-columns", "1200", "--max-columns-preview"]
    command += [pattern, *paths]
    p = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
    assert p.returncode in (0, 1), p.stderr
    return {"command": command, "exit_code": p.returncode, "matches": p.stdout.splitlines()}


def main():
    labels_path = ROOT / "docs/data/labels.json"
    labels = json.loads(labels_path.read_text()) if labels_path.exists() else {}
    selected = set(sys.argv[1:])
    results = json.loads(OUT.read_text())["results"] if selected and OUT.exists() else {}
    for key, pattern in PATTERNS.items():
        if selected and key not in selected:
            continue
        hits = run_rg(pattern, ["data/traits"], True)
        context = run_rg(pattern, ["data", "research", "scripts", "conf"])
        context["matches"] = [x for x in context["matches"] if not x.startswith("research/structural-discovery-20261028/")]
        results[key] = {"pattern": pattern, "record_identity_hits": hits,
                        "ignored_inclusive_context": context,
                        "indexed_labels": [{"identifier": k, "label": v} for k, v in labels.items() if re.search(pattern, v, re.I)]}
    result = {"created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "branch": subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip(),
              "base_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
              "ignored_files_included": True,
              "limitations": "Lexical candidate search is not semantic duplicate certification; fold/family/function matches require class-level adjudication. Current discovery output excluded from context matches.",
              "labels_sha256": hashlib.sha256(labels_path.read_bytes()).hexdigest() if labels_path.exists() else None,
              "results": results}
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({k: {"record_identity_hits": len(v["record_identity_hits"]["matches"]), "context_hits": len(v["ignored_inclusive_context"]["matches"]), "indexed_labels": len(v["indexed_labels"])} for k, v in results.items()}, indent=2))


if __name__ == "__main__":
    main()
