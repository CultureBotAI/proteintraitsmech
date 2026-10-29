"""Bounded offline coordination scan, authored 2026-10-29.

Purpose: locate supplied structural-candidate aliases and shared-file ownership
in the parent's already-captured open PR/issue snapshot. No network, Git,
scientific adjudication, ID allocation, or corpus writes.
Inputs: ../open-work-prewrite.json (exact SHA256 retained in output).
Output: open-work-scan.json beside this helper, for manual reviewer assessment.
Task: structural discovery after PR1202; context issues1200/1201. This helper
does not reserve identifiers and cannot observe private/unpushed work. Re-running
replaces only its derived scan, so retain/review input hashes when reusing it.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
INPUT = HERE.parent / "open-work-prewrite.json"
OUTPUT = HERE / "open-work-scan.json"
PATTERNS = {
    "beta_arch": r"(?:beta|β)[\s_-]*arch(?:es)?\b",
    "schellman": r"\bschellman\b",
    "beta_bulge_loop": r"(?:beta|β)[\s_-]*bulge[\s_-]*loop",
    "psi_loop": r"(?:psi|ψ)[\s_-]*loop",
    "asx_turn": r"\basx[\s_-]*turn",
    "st_turn_motif_staple": r"\b(?:st|serine[\s/-]*threonine|ser[\s/-]*thr)[\s_-]*(?:turn|motif|staple)\b",
    "membrane_fenestration": r"fenestrat|\blateral[\s_-]+(?:membrane|channel|opening|pore)",
    "subpocket": r"\bsub[\s_-]*pocket",
    "intersubunit_cavity": r"(?:inter[\s_-]*subunit|subunit[\s_-]*interface).{0,80}(?:cavit|pocket)|(?:cavit|pocket).{0,80}(?:inter[\s_-]*subunit|subunit[\s_-]*interface)",
    "interdomain_cavity": r"inter[\s_-]*domain.{0,80}(?:cavit|pocket)|(?:cavit|pocket).{0,80}inter[\s_-]*domain",
    "cryptic_pocket": r"cryptic.{0,40}pocket|pocket.{0,40}cryptic",
}
SHARED = {
    "schema": r"(?:^src/proteintraitsmech/schema/|^src/proteintraitsmech/datamodel/)",
    "methods": r"^(?:data/methods/methods\.yaml|scripts/build_methods\.py|tests/test_methods_recipes\.py)$",
    "internal_id_baseline": r"^(?:conf/internal_id_label_baseline\.yaml|scripts/validate_internal_id_labels\.py)$",
    "docs_builder_indexes": r"^(?:scripts/build_docs_index\.py|docs/(?:index\.html|browse\.(?:html|js)|data/)|conf/text_map\.yaml|data/text_map/)",
    "justfile": r"^justfile$",
    "grounding": r"^(?:data/grounding/|scripts/.*(?:ground|uniprot).*\.py|tests/.*(?:ground|uniprot).*)",
    "source_registry": r"^(?:download\.yaml|scripts/fetch_source\.py|\.gitignore)$",
}
PLAN = re.compile(
    r"structural[\s_-]+motif|super[\s_-]*secondary|secondary[\s_-]+structur|"
    r"\bcavit|\bpockets?\b|\bgrooves?\b|\bclefts?\b|\btunnels?\b|"
    r"methods\.yaml|build_methods|internal_id_label|build_docs_index|"
    r"schema/proteintraitsmech|ground_uniprot|source.rights|redistribut|"
    r"class.level|new.trait|identifier.{0,40}(?:assign|reserv|allocat)",
    re.I,
)


def hits(text: str) -> list[dict]:
    text = text.translate(str.maketrans({dash: "-" for dash in "‐‑‒–—−"}))
    found = []
    for key, expression in PATTERNS.items():
        matches = list(re.finditer(expression, text, re.I))
        if matches:
            found.append({
                "candidate": key,
                "match_count": len(matches),
                "examples": [text[max(0, m.start()-100):m.end()+180] for m in matches[:5]],
            })
    return found


def main() -> None:
    raw = INPUT.read_bytes()
    snapshot = json.loads(raw)
    prs = []
    for pr in snapshot["pull_requests"]:
        paths = [file["filename"] for file in pr["files"]]
        owned = {
            key: [path for path in paths if re.search(expression, path)]
            for key, expression in SHARED.items()
        }
        patch_hits = []
        for file in pr["files"]:
            matched = hits(file.get("patch", ""))
            if matched:
                patch_hits.append({"path": file["filename"], "hits": matched})
        prs.append({
            "number": pr["number"], "head": pr["headRefOid"],
            "branch": pr["headRefName"], "title": pr["title"], "url": pr["url"],
            "paths": paths,
            "shared_paths": {key: value for key, value in owned.items() if value},
            "review_artifacts_only": bool(paths) and all(path.startswith("reviews/structured/") for path in paths),
            "missing_patch_paths": [file["filename"] for file in pr["files"] if "patch" not in file],
            "body_hits": hits(pr["title"] + "\n" + pr["body"]),
            "path_hits": [{"path": path, "hits": hits(path)} for path in paths if hits(path)],
            "patch_hits": patch_hits,
        })
    issues = []
    for issue in snapshot["issues"]:
        text = issue["title"] + "\n" + issue["body"]
        matched = hits(text)
        plan_matches = list(PLAN.finditer(text))
        if matched or plan_matches:
            issues.append({
                "number": issue["number"], "title": issue["title"], "url": issue["url"],
                "candidate_hits": matched,
                "plan_examples": [text[max(0, m.start()-100):m.end()+180] for m in plan_matches[:8]],
            })
    report = {
        "schema_version": 1,
        "input": INPUT.name,
        "input_sha256": hashlib.sha256(raw).hexdigest(),
        "helper_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "snapshot_time": snapshot["observed_utc"],
        "main_sha": snapshot["main_sha"],
        "pr_count": len(snapshot["pull_requests"]),
        "issue_count": len(snapshot["issues"]),
        "candidate_patterns": PATTERNS,
        "shared_path_patterns": SHARED,
        "prs": prs,
        "issue_leads": issues,
        "limits": [
            "Offline lexical triage of all supplied PR titles/bodies/filenames/available patches and issue titles/bodies; manual assessment required.",
            "Patches may be omitted or truncated by GitHub. Missing patches are explicitly listed. No remote branch checkout or comments were inspected.",
            "No corpus absence, scientific identity, global reservation, private work or unpushed branch conclusion follows from this scan.",
        ],
    }
    OUTPUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"output": str(OUTPUT.relative_to(HERE.parent.parent.parent)), "prs": len(prs), "issue_leads": len(issues)}))


if __name__ == "__main__":
    main()
