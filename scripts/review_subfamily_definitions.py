#!/usr/bin/env python3
"""LLM review of the 228 subfamily-derived PANTHER definitions (#151 follow-up).

#154 gave 228 annotation-free PANTHER families a definition composed from the GO /
protein-class terms every one of their annotated subfamilies shares. The rule is
mechanical and the provenance is explicit, but nothing checked whether the resulting
claim is *biologically sensible for that family*. Two cases found by hand while
reviewing showed the range:

  * PTHR12652 PEROXISOMAL BIOGENESIS FACTOR 11 -> peroxisomal membrane. Obviously right.
  * PTHR10036 CD59 GLYCOPROTEIN -> acetylcholine receptor regulator activity. Reads
    wrong for a complement regulator, and is defensible only once you know PTHR10036
    spans the Ly6/uPAR family, which includes the lynx/SLURP nAChR modulators.

This asks a second model to make that call for every record, one batch at a time.

WHAT THIS DOES NOT DO
---------------------
It does not edit records. It writes verdicts to a JSONL for triage. Acting on a
verdict is a separate, reviewable step -- the same separation `review_llm_abstracts.py`
keeps between `review` and `promote`.

ANTI-FABRICATION
----------------
A previous codex run in this repo invented 25 plausible PANTHER records after the
command that should have written its input was denied, leaving the prompt empty. Two
guards, both hard failures rather than warnings:

  * the prompt must exceed MIN_PROMPT_CHARS before the model is called at all;
  * every id in the reply must be one that was sent, and every id sent must come back.
    A batch that fails either is recorded as an error and retried once, never merged.

Usage:
    python3 scripts/review_subfamily_definitions.py --limit 1     # canary: one batch
    python3 scripts/review_subfamily_definitions.py               # all batches
    python3 scripts/review_subfamily_definitions.py --report      # summarise the JSONL
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RECORDS = REPO / "data" / "traits" / "sequence" / "family" / "panther"
OUT = REPO / "research" / "subfamily-definition-review.jsonl"

BATCH = 12
# Measured on the ENTRIES, never on the whole prompt. The rubric is 1,431 characters
# of boilerplate, so a whole-prompt threshold is really a test of the rubric: an empty
# batch came to 1,432 chars and cleared a 1,500 limit by 68 characters of luck, and one
# entry cleared it regardless of whether the other eleven were there. The guard exists
# because a codex run in this repo fabricated 25 records from an input that never
# arrived -- it has to fail when the DATA is missing, not when the prompt is short.
MIN_ENTRY_CHARS = 40
# A 12-entry batch takes ~4m50s wall-clock and almost no local CPU (3s user), so the
# limit is the provider, not this machine. Serial, 228 records is ~95 minutes.
WORKERS = 4

# Run the model from an EMPTY directory, not the repo. codex exec is an agent: pointed
# at this checkout it explores before answering, and 424,468 files is enough to turn a
# 4-second text judgement into a 20-minute one (measured -- the first canary was killed
# at 20 minutes with zero batches done; the same prompt from an empty dir took 3.7s).
# Nothing here needs repo access: every fact the model judges is in the prompt.
SANDBOX_DIR = Path("/tmp/ptm-codex-sandbox")
MODEL_CMD = ["codex", "exec", "--sandbox", "read-only", "--skip-git-repo-check",
             "-C", str(SANDBOX_DIR)]

_IDENT = re.compile(r"^identifier: PANTHER:(\S+)\s*$", re.M)
_LABEL = re.compile(r"^label: (.*)$", re.M)
_DEF = re.compile(r"^definition: >-\n  (.*)$", re.M)
_MARK = "of its annotated subfamilies"

RUBRIC = """You are auditing machine-composed definitions in a curated knowledge base
of protein family traits.

Each entry below is a PANTHER protein family that the PANTHER 19.0 release annotates
with NOTHING on the family's own row. The definition was therefore composed from the
GO and protein-class terms that EVERY ONE of its annotated subfamilies shares. The
prose states this explicitly and gives the number of subfamilies.

For each entry decide whether the borrowed terms are a defensible description OF THE
FAMILY AS A WHOLE.

verdict must be exactly one of:
  OK           - the terms are consistent with what this family is.
  QUESTIONABLE - the terms describe a real part of the family but reading them as
                 family-wide is misleading, OR the terms are so generic
                 ("binding", "cellular process") that they say nothing.
  WRONG        - the terms contradict what this family is known to be, or clearly
                 belong to a different protein group.

Judge the BIOLOGY, not the writing. The phrasing and provenance are already settled;
do not comment on them. A family name you do not recognise is not automatically
QUESTIONABLE - say OK if the terms are at least consistent with the name.

Reply with a JSON array and NOTHING else. One object per entry, same order:
  {"id": "<the PTHR id exactly as given>", "verdict": "OK|QUESTIONABLE|WRONG",
   "reason": "<one sentence, under 30 words>"}
"""


def load_records() -> list[dict]:
    out = []
    for path in sorted(RECORDS.rglob("*.yaml")):
        text = path.read_text(encoding="utf-8")
        dm = _DEF.search(text)
        if not dm or _MARK not in dm.group(1):
            continue
        defn = dm.group(1)
        # Only the borrowed part matters; the boilerplate is identical everywhere.
        claim = defn.split("annotated subfamilies.", 1)[-1].strip()
        nm = re.search(r"shared by all (\d+) of its annotated subfamilies", defn)
        out.append({"id": _IDENT.search(text).group(1),
                    "label": _LABEL.search(text).group(1).strip().strip('"'),
                    "n_subfamilies": int(nm.group(1)) if nm else 0,
                    "claim": claim, "path": str(path.relative_to(REPO))})
    return out


def render_entries(batch: list[dict]) -> str:
    """Just the data, so it can be length-checked without the rubric masking it."""
    lines = []
    for r in batch:
        lines.append(f'- id: {r["id"]}')
        lines.append(f'  family name: {r["label"]}')
        lines.append(f'  annotated subfamilies: {r["n_subfamilies"]}')
        lines.append(f'  borrowed terms: {r["claim"]}')
    return "\n".join(lines)


def build_prompt(batch: list[dict]) -> str:
    return RUBRIC + "\n\n" + render_entries(batch)


def extract_json(stdout: str):
    """codex prints its reply after a `codex` marker; take the last JSON array."""
    starts = [m.start() for m in re.finditer(r"\[", stdout)]
    for i in reversed(starts):
        chunk = stdout[i:]
        for j in range(len(chunk), 0, -1):
            if chunk[j - 1] != "]":
                continue
            try:
                val = json.loads(chunk[:j])
            except json.JSONDecodeError:
                continue
            if isinstance(val, list) and val and isinstance(val[0], dict):
                return val
    return None


def review_batch(batch: list[dict]) -> tuple[list[dict] | None, str]:
    if not batch:
        return None, "empty batch -- refusing to call"
    entries = render_entries(batch)
    if len(entries) < MIN_ENTRY_CHARS * len(batch):
        return None, (f"entries too short ({len(entries)} chars for {len(batch)} "
                      f"records) -- refusing to call")
    blank = [r["id"] for r in batch if not str(r.get("claim", "")).strip()
             or not str(r.get("label", "")).strip()]
    if blank:
        return None, f"records with no label or no claim: {blank[:4]} -- refusing to call"
    prompt = RUBRIC + "\n\n" + entries
    proc = subprocess.run(MODEL_CMD + [prompt], capture_output=True, text=True)
    if proc.returncode != 0:
        return None, f"codex exited {proc.returncode}: {proc.stderr[-200:]}"
    parsed = extract_json(proc.stdout)
    if parsed is None:
        return None, f"no JSON array in reply: {proc.stdout[-200:]!r}"
    sent = {r["id"] for r in batch}
    got = {str(d.get("id")) for d in parsed}
    if got != sent:
        return None, (f"id mismatch -- invented={sorted(got - sent)[:4]} "
                      f"missing={sorted(sent - got)[:4]}")
    return parsed, ""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--limit", type=int, default=0, help="stop after N batches")
    ap.add_argument("--report", action="store_true", help="summarise the JSONL only")
    ap.add_argument("--workers", type=int, default=WORKERS,
                    help="batches in flight at once")
    args = ap.parse_args()

    if args.report:
        if not OUT.exists():
            print(f"no {OUT}", file=sys.stderr)
            return 1
        rows = [json.loads(x) for x in OUT.read_text(encoding="utf-8").splitlines() if x]
        by = {}
        for r in rows:
            by.setdefault(r["verdict"], []).append(r)
        print(f"reviewed: {len(rows):,}")
        for v in ("OK", "QUESTIONABLE", "WRONG"):
            print(f"  {v:<14}{len(by.get(v, [])):>5}")
        for v in ("WRONG", "QUESTIONABLE"):
            for r in by.get(v, [])[:12]:
                print(f"  [{v}] {r['id']} {r['label']}\n        {r['reason']}")
        return 0

    records = load_records()
    print(f"subfamily-derived records: {len(records):,}", file=sys.stderr)
    if not records:
        print("nothing to review", file=sys.stderr)
        return 1
    done = set()
    if OUT.exists():
        done = {json.loads(x)["id"]
                for x in OUT.read_text(encoding="utf-8").splitlines() if x}
        print(f"already reviewed: {len(done):,}", file=sys.stderr)
    todo = [r for r in records if r["id"] not in done]
    batches = [todo[i:i + BATCH] for i in range(0, len(todo), BATCH)]
    if args.limit:
        batches = batches[:args.limit]
    print(f"batches to run: {len(batches)}", file=sys.stderr)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    SANDBOX_DIR.mkdir(parents=True, exist_ok=True)
    ok = failed = 0
    lock = threading.Lock()

    def run(item):
        nonlocal ok, failed
        n, batch = item
        verdicts, err = review_batch(batch)
        if verdicts is None:
            verdicts, err = review_batch(batch)      # one retry, never merged blind
        with lock:
            if verdicts is None:
                failed += 1
                print(f"  batch {n}/{len(batches)}: FAILED -- {err}", file=sys.stderr)
                return
            index = {r["id"]: r for r in batch}
            with OUT.open("a", encoding="utf-8") as fh:
                for v in verdicts:
                    rec = index[str(v["id"])]
                    fh.write(json.dumps({"id": rec["id"], "label": rec["label"],
                                         "n_subfamilies": rec["n_subfamilies"],
                                         "path": rec["path"], "claim": rec["claim"],
                                         "verdict": str(v.get("verdict", "")).upper(),
                                         "reason": v.get("reason", "")},
                                        ensure_ascii=False) + "\n")
            ok += len(verdicts)
            print(f"  batch {n}/{len(batches)}: {len(verdicts)} verdicts "
                  f"({ok} done)", file=sys.stderr)

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        list(pool.map(run, enumerate(batches, 1)))
    print(f"wrote {ok:,} verdicts to {OUT}" + (f"; {failed} batch(es) failed" if failed else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
