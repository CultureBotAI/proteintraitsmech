#!/usr/bin/env python3
"""Read-only collision scan; writes evidence only to this script's directory.

The initial broad scans were executed inline. Their exact rg argument vectors are
retained in initial-collision-search.json. --replay-initial reproduces those calls
without replacing their immutable outputs. The default refined scan avoids whole
minified JSON lines and corrects substring false positives such as 'architecture'.
No files outside this evidence directory are created or changed.
"""
import argparse
import datetime as dt
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PATTERNS = {
    "beta_arch": r"\b(?:beta|β)[_ -]arch(?:es)?\b|\b(?:beta|β)[_ -]arc(?:s)?\b",
    "schellman_loop": r"\bschellmann?\b|\bpaperclip\b",
    "asx_turn": r"\basx[_ -]turns?\b|aspartate.asparagine[_ -]turn",
    "st_turn": r"\bst[_ -]turns?\b|serine.threonine[_ -]turn",
    "beta_bulge_loop": r"\b(?:beta|β)[_ -]bulge[_ -]loops?\b",
    "psi_loop": r"\b(?:psi|ψ)[_ -]loops?\b",
    "niche": r"\bniche\b",
    "st_motif": r"\bst[_ -]motifs?\b|serine.threonine[_ -]motif",
}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--replay-initial", action="store_true")
    args = p.parse_args()
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    if args.replay_initial:
        manifest = json.loads((HERE / "initial-collision-search.json").read_text())
        outputs = []
        for result in manifest["results"]:
            dst = HERE / f"replay-{stamp}-{result['candidate_key']}.txt.gz"
            raw = subprocess.run(result["command"], cwd=ROOT, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, check=False)
            with gzip.open(dst, "wb") as out:
                out.write(raw.stdout)
            outputs.append({"path": str(dst.relative_to(ROOT)), "returncode": raw.returncode,
                            "stdout_sha256": hashlib.sha256(raw.stdout).hexdigest(),
                            "stderr": raw.stderr.decode(errors="replace")})
        (HERE / f"replay-{stamp}.json").write_text(json.dumps(outputs, indent=2) + "\n")
        return
    roots = [v for v in ["data/traits", "data/curation", "data/mappings", "data/raw",
                         "reports", "research", "docs/data"] if (ROOT / v).exists()]
    command = ["rg", "--no-ignore", "--hidden", "-l", "-i"]
    for glob in ("*.yaml", "*.yml", "*.json", "*.jsonl", "*.tsv", "*.md", "*.txt", "*.obo"):
        command += ["--glob", glob]
    command += ["--glob", "!research/structural-discovery-20261028/motifs/**",
                "|".join(f"(?:{v})" for v in PATTERNS.values()), *roots]
    result = subprocess.run(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if result.returncode not in (0, 1):
        raise RuntimeError(result.stderr.decode())
    output = {"created_at": stamp, "ignored_files_included": True,
              "command": command, "patterns": PATTERNS,
              "self_evidence_excluded": str(HERE.relative_to(ROOT)), "results": {}}
    regexes = {k: re.compile(v, re.I) for k, v in PATTERNS.items()}
    for key in regexes:
        output["results"][key] = []
    for name in result.stdout.decode().splitlines():
        path = ROOT / name
        data = path.read_text(errors="replace")
        for key, rx in regexes.items():
            matches = list(rx.finditer(data))
            if not matches:
                continue
            output["results"][key].append({"path": name, "occurrences": len(matches),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "snippets": [data[max(0,m.start()-150):m.end()+240] for m in matches[:12]]})
    target = HERE / f"refined-collision-search-{stamp}.json"
    target.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"output": str(target.relative_to(ROOT)),
                      "matched_files": {k: len(v) for k,v in output["results"].items()}}, indent=2))

if __name__ == "__main__":
    main()
