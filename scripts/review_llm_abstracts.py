#!/usr/bin/env python3
"""LLM review of InterPro's unreviewed LLM abstracts, and promotion of what passes.

Issue #92. The PANTHER ingest deliberately did NOT promote InterPro's machine-written
abstracts to `definition`: stamping them `definition_source: InterPro` would launder
their provenance so that nobody downstream could tell a curator had never seen them.
They were parked in `definitions[]` with `method: GENERATED` instead.

The curation decision (2026-08) is that these abstracts may be promoted after review
by an LLM reviewer. That is a real quality gate, and it is NOT curator review — so the
promoted record says exactly that:

    definition_source: "InterPro:IPR052044 abstract (LLM-generated, LLM-reviewed
                        <model>, not curator-reviewed)"

and `mapping_status` becomes PROPOSED, not REVIEWED. A human still has the last word;
this only moves a candidate out of the parking lot and into the definition slot where
it is visible, attributed, and reversible.

TWO COMMANDS, DELIBERATELY SEPARATE
-----------------------------------
`review` is expensive and non-deterministic; `promote` is free and deterministic.
Keeping them apart means the verdicts are a durable, auditable artifact that can be
re-applied, re-examined, or partly rejected without paying for the reviews again.
The verdict file is committed for exactly that reason.

    just review-abstracts            # dry-run: shows the batch plan, calls nothing
    just review-abstracts --apply    # runs the reviewer, appends to the verdict file
    just promote-abstracts           # dry-run: shows what would change
    just promote-abstracts --apply   # edits records

`review --apply` is resumable: a candidate already in the verdict file is skipped, so
an interrupted run costs only the batch it was in.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from record_io import append_to_section, insert_before_license  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PANTHER_DIR = ROOT / "data" / "traits" / "sequence" / "family" / "panther"
VERDICTS = ROOT / "data" / "reviews" / "panther_llm_abstracts.jsonl"

UNREVIEWED = "LLM-generated, not curator-reviewed"
STUB_SOURCE = "PANTHER 19.0 (composed from the family name and its GO / protein-class annotations)"
DEMOTED = "rejected on re-review as superfamily-level"

# A synonym that is itself superfamily- or domain-level. Issue #112: the first review
# accepted abstracts that describe the SUPERFAMILY when the record's own synonym was
# generic, because criterion 2 (INFORMATIVE) was judged against that generic synonym
# rather than against the family. These are the records worth a second, stricter look.
AT_RISK_SYNONYM = re.compile(
    r"\b(superfamily|domain[- ]containing|family|families|-like|related)\b", re.I)

# The wrapper on PATH is a shell function that refuses to run and asks which profile
# to use, so a subprocess must call the real binary with the profile in the
# environment. A canary run in an interactive shell would not have caught this.
CLAUDE_BIN = os.environ.get("CLAUDE_BIN", str(Path.home() / ".local/bin/claude"))
CLAUDE_CONFIG_DIR = os.environ.get("PTM_CLAUDE_CONFIG_DIR", str(Path.home() / ".claude-work"))

STRICT_RUBRIC = """\
You are RE-reviewing protein-family definitions that a previous reviewer already approved.
Every one is now the record's `definition`. Your only question is narrower than before:

  Does this text describe THIS SPECIFIC FAMILY, or does it describe the superfamily,
  domain or fold that the family belongs to?

A definition that would read equally well on fifty sibling families is superfamily-level
and must be rejected, however accurate it is. The test: could a reader use it to tell this
family apart from its siblings? Concretely -

  KEEP    - names what this family does that its relatives do not: its substrate, its
            reaction, its specific role, its distinguishing feature.
  DEMOTE  - describes the shared domain/fold/superfamily, lists what "members of this
            family" do in general terms, or restates the synonym in longer words.

Two cautions, both from real errors in the first pass:

  * `synonyms` is AUTHORITATIVE for family identity; the `label` is often a PANTHER
    domain-naming artifact and can name a completely different protein. Judge against the
    synonym, never the label alone.
  * a generic SYNONYM does not license a generic DEFINITION. If the synonym is
    "GDSL esterase/lipase", the definition must still say what THIS family of GDSL
    enzymes does, not what GDSL enzymes do.

Return ONLY a JSON array, no prose and no code fence:
[{"id": "<the id given>", "verdict": "KEEP|DEMOTE", "confidence": 0.0-1.0, \
"reason": "<one sentence>"}]
"""

RUBRIC = """\
You are reviewing machine-written protein-family abstracts for a curated knowledge \
base. Each abstract was generated by an LLM at InterPro and has NOT been seen by a \
curator. Your review decides whether it may become the family's `definition`.

Judge each abstract on four things:

1. CONSISTENT - does it describe THIS family, agreeing with the label, synonyms and \
   any GO / protein-class annotations given? A plausible abstract about a different \
   family is the main risk and must be rejected.
2. INFORMATIVE - does it say materially more than the label already says? "X is a \
   family of X proteins" is a stub, not a definition.
3. SUPPORTED - does it avoid specifics it cannot know? Invented accessions, EC \
   numbers, citations, organisms, residue positions or mechanisms are disqualifying. \
   General, hedged statements of family function are fine.
4. DEFINITIONAL - does it say what the family IS, rather than commenting on why it \
   is interesting or what is unknown about it?

Verdict for each:
  PROMOTE - all four hold; safe to use as the definition verbatim.
  FLAG    - probably fine but something needs a human eye; say what in `concerns`.
  REJECT  - fails 1, 2, 3 or 4.

Be strict. FLAG or REJECT when uncertain: an abstract left parked costs nothing, and a \
wrong definition on a class record propagates. Do NOT rewrite or improve the text - \
you are a reviewer, and edited text would be unreviewed LLM prose again.

Return ONLY a JSON array, one object per input id, no prose and no code fence:
[{"id": "<the id given>", "verdict": "PROMOTE|FLAG|REJECT", "confidence": 0.0-1.0, \
"reason": "<one sentence>", "concerns": ["..."]}]
"""


# --------------------------------------------------------------------------- collect

def _yaml_records():
    import yaml
    for f in sorted(PANTHER_DIR.rglob("*.yaml")):
        yield f, yaml.safe_load(f.read_text(encoding="utf-8"))


def collect_candidates() -> list[dict]:
    """Records carrying an unreviewed LLM abstract that is not yet the definition."""
    out = []
    for path, rec in _yaml_records():
        abstract = next((d for d in (rec.get("definitions") or [])
                         if UNREVIEWED in (d.get("source") or "")), None)
        if abstract is None:
            continue
        out.append({
            "id": rec["identifier"],
            "path": str(path.relative_to(ROOT)),
            "label": rec.get("label", ""),
            "interpro": next((x.get("object") for x in (rec.get("mapped_xrefs") or [])
                              if str(x.get("object", "")).startswith("InterPro:")), None),
            "synonyms": [s.get("synonym_text") for s in (rec.get("synonyms") or [])],
            "current_definition": rec.get("definition", ""),
            "abstract": " ".join((abstract.get("text") or "").split()),
        })
    return out


def load_verdicts() -> dict[str, dict]:
    """Every verdict on file, across the shared file and any per-shard files.

    Resume and promote both read this, so a shard file left unmerged still counts as
    reviewed rather than being paid for a second time.
    """
    got = {}
    for path in sorted(VERDICTS.parent.glob("panther_llm_abstracts*.jsonl")) \
            if VERDICTS.parent.exists() else []:
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                v = json.loads(line)
                got[v["id"]] = v
    return got


# ---------------------------------------------------------------------------- review

def _prompt(batch: list[dict]) -> str:
    items = [{"id": c["id"], "label": c["label"], "synonyms": c["synonyms"],
              "interpro_entry": c["interpro"], "abstract": c["abstract"]}
             for c in batch]
    return f"{RUBRIC}\n\nReview these {len(items)} abstracts:\n\n{json.dumps(items, indent=1)}"


def _call_reviewer(prompt: str, model: str, timeout: int) -> str:
    env = dict(os.environ, CLAUDE_CONFIG_DIR=CLAUDE_CONFIG_DIR)
    proc = subprocess.run(
        [CLAUDE_BIN, "-p", prompt, "--model", model],
        capture_output=True, text=True, timeout=timeout, env=env,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"reviewer exited {proc.returncode}: {proc.stderr[:400]}")
    return proc.stdout


def _parse_verdicts(raw: str, batch: list[dict], model: str,
                    allowed: set[str] | None = None) -> list[dict]:
    # Scan for every complete JSON value rather than spanning first `[` to last `]`.
    # The reviewer is asked for one array and usually sends one, but it sometimes
    # sends two (e.g. splitting a batch), and a first-to-last span then hands
    # `[...]\n[...]` to json.loads, which fails with "Extra data" and discards a
    # whole batch of paid-for verdicts. The canary run hit this on its only call.
    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-z]*\n|\n```$", "", text)
    decoder, got, i = json.JSONDecoder(), [], 0
    while i < len(text):
        ch = text[i]
        if ch not in "[{":
            i += 1
            continue
        try:
            value, end = decoder.raw_decode(text, i)
        except ValueError:
            i += 1
            continue
        got.extend(value if isinstance(value, list) else [value])
        i = end
    if not got:
        raise ValueError(f"no JSON verdicts in reviewer output: {raw[:300]!r}")
    by_id = {v.get("id"): v for v in got if isinstance(v, dict)}
    out = []
    for c in batch:
        v = by_id.get(c["id"])
        if v is None:                      # never invent a verdict for a missing answer
            continue
        verdict = str(v.get("verdict", "")).upper()
        if verdict not in (allowed or {"PROMOTE", "FLAG", "REJECT"}):
            continue
        out.append({"id": c["id"], "path": c["path"], "verdict": verdict,
                    "confidence": v.get("confidence"), "reason": v.get("reason", ""),
                    "concerns": v.get("concerns") or [], "reviewer": model})
    return out


def cmd_review(args) -> int:
    candidates = collect_candidates()
    done = load_verdicts()
    todo = [c for c in candidates if c["id"] not in done]
    # Shards write to separate files and are merged afterwards. Four processes
    # appending to one file would mostly be fine (small writes to an O_APPEND fd are
    # atomic) but "mostly" is not a property worth relying on for paid-for verdicts.
    if args.shard:
        i, n = (int(x) for x in args.shard.split("/"))
        todo = [c for k, c in enumerate(todo) if k % n == i - 1]
    if args.limit:
        todo = todo[:args.limit]
    batches = [todo[i:i + args.batch_size] for i in range(0, len(todo), args.batch_size)]
    print(f"  candidates      : {len(candidates):,}")
    print(f"  already reviewed: {len(done):,}")
    print(f"  to review       : {len(todo):,} in {len(batches):,} batch(es) of {args.batch_size}")
    print(f"  reviewer        : {args.model} via {CLAUDE_BIN}")
    if not args.apply:
        print("\n  DRY RUN - no reviewer called. Re-run with --apply.")
        return 0

    out_path = Path(args.out) if args.out else VERDICTS
    out_path.parent.mkdir(parents=True, exist_ok=True)
    counts, failed = {"PROMOTE": 0, "FLAG": 0, "REJECT": 0}, 0
    for n, batch in enumerate(batches, 1):
        try:
            raw = _call_reviewer(_prompt(batch), args.model, args.timeout)
            verdicts = _parse_verdicts(raw, batch, args.model)
        except Exception as exc:                       # one bad batch must not kill the run
            failed += 1
            print(f"  batch {n}/{len(batches)}: FAILED ({type(exc).__name__}: {exc})"[:200])
            continue
        with out_path.open("a", encoding="utf-8") as fh:
            for v in verdicts:
                fh.write(json.dumps(v, ensure_ascii=False) + "\n")
                counts[v["verdict"]] += 1
        missing = len(batch) - len(verdicts)
        print(f"  batch {n}/{len(batches)}: {len(verdicts)}/{len(batch)} verdicts"
              + (f"  ({missing} unanswered)" if missing else "")
              + f"   running: {counts}")
    print(f"\n  wrote {sum(counts.values()):,} verdicts to {out_path}")
    if failed:
        print(f"  {failed} batch(es) failed and were skipped - re-run to retry them")
    return 0


# --------------------------------------------------------------------------- promote

_TOP_KEY = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*:")


def replace_scalar(text: str, key: str, value: str) -> str:
    """Replace a top-level scalar, folded or plain, preserving surrounding lines.

    The block form spans until the next top-level key, so the whole run has to go -
    replacing only the `key:` line would strand the old continuation lines as
    unparseable orphans.
    """
    lines = text.splitlines(keepends=True)
    try:
        i = next(n for n, ln in enumerate(lines) if ln.startswith(f"{key}:"))
    except StopIteration:
        raise KeyError(f"{key} not found")
    j = i + 1
    while j < len(lines) and not (lines[j].strip() and _TOP_KEY.match(lines[j])):
        j += 1
    return "".join(lines[:i] + [value if value.endswith("\n") else value + "\n"] + lines[j:])


def folded(key: str, text: str) -> str:
    """`key: >-` with the text as one long line, matching how the seeders write it."""
    return f"{key}: >-\n  {' '.join(text.split())}\n"


def promoted_source(interpro: str | None, reviewer: str) -> str:
    entry = f"{interpro} abstract" if interpro else "InterPro abstract"
    return f'definition_source: "{entry} (LLM-generated, LLM-reviewed {reviewer}, not curator-reviewed)"\n'


def cmd_promote(args) -> int:
    import yaml
    verdicts = load_verdicts()
    promote = {k: v for k, v in verdicts.items() if v["verdict"] == "PROMOTE"}
    print(f"  verdicts on file: {len(verdicts):,}")
    for kind in ("PROMOTE", "FLAG", "REJECT"):
        n = sum(1 for v in verdicts.values() if v["verdict"] == kind)
        print(f"    {kind:<8}{n:>7,}")
    changed = skipped = 0
    for vid, v in sorted(promote.items()):
        path = ROOT / v["path"]
        if not path.exists():
            print(f"  MISSING {v['path']}")
            continue
        text = path.read_text(encoding="utf-8")
        rec = yaml.safe_load(text)
        abstract = next((d for d in (rec.get("definitions") or [])
                         if UNREVIEWED in (d.get("source") or "")), None)
        if abstract is None:               # already promoted on an earlier run
            skipped += 1
            continue
        interpro = next((x.get("object") for x in (rec.get("mapped_xrefs") or [])
                         if str(x.get("object", "")).startswith("InterPro:")), None)
        body = " ".join((abstract.get("text") or "").split())

        out = replace_scalar(text, "definition", folded("definition", body))
        out = replace_scalar(out, "definition_source", promoted_source(interpro, v["reviewer"]))
        # the parked copy records that it was reviewed, so the file is self-describing
        out = out.replace(f'source: "{interpro} abstract ({UNREVIEWED})"',
                          f'source: "{interpro} abstract (LLM-generated, LLM-reviewed '
                          f'{v["reviewer"]}, not curator-reviewed)"')
        out = replace_scalar(out, "mapping_status", "mapping_status: PROPOSED\n")
        event = (f'curation_history:\n  - timestamp: "{args.timestamp}"\n'
                 f'    curator: review-llm-abstracts\n'
                 f'    action: "Promoted InterPro LLM abstract to definition after LLM review '
                 f'({v["reviewer"]}); SEEDED -> PROPOSED"\n'
                 f'    llm_assisted: true\n')
        out = (append_to_section(out, "curation_history", event)
               if "\ncuration_history:" in out or out.startswith("curation_history:")
               else insert_before_license(out, event))
        if out == text:
            continue
        changed += 1
        if args.apply:
            path.write_text(out, encoding="utf-8")
    verb = "promoted" if args.apply else "would promote"
    print(f"\n  {verb}: {changed:,}   already done: {skipped:,}")
    if not args.apply:
        print("  DRY RUN - re-run with --apply to write.")
    return 0


# --------------------------------------------------------------------- re-review (#112)

RE_VERDICTS = ROOT / "data" / "reviews" / "panther_generic_rereview.jsonl"


def collect_at_risk(only_generic_synonym: bool = False) -> list[dict]:
    """Promoted records to re-review. By default, ALL of them.

    This started as "records whose synonym is itself superfamily-level", on the theory
    that a generic synonym is what let a generic definition through. Measured, that
    theory is wrong: a 30-record sample of the records the filter EXCLUDED demoted at
    36%, against 42% for the ones it selected. The filter was not a discriminator, so
    using it would have left roughly 437 generic definitions in place while reporting
    the issue closed.

    The narrow behaviour is kept behind a flag because the measurement is worth being
    able to reproduce, not because it should be the default.
    """
    out = []
    for path, rec in _yaml_records():
        src = rec.get("definition_source") or ""
        if "LLM-reviewed" not in src or DEMOTED in src:
            continue
        syn = " ".join(s.get("synonym_text") or "" for s in (rec.get("synonyms") or []))
        if only_generic_synonym and (not syn or not AT_RISK_SYNONYM.search(syn)):
            continue
        out.append({
            "id": rec["identifier"],
            "path": str(path.relative_to(ROOT)),
            "label": rec.get("label", ""),
            "synonyms": [s.get("synonym_text") for s in (rec.get("synonyms") or [])],
            "interpro": next((x.get("object") for x in (rec.get("mapped_xrefs") or [])
                              if str(x.get("object", "")).startswith("InterPro:")), None),
            "definition": " ".join((rec.get("definition") or "").split()),
        })
    return out


def _load_jsonl(path):
    if not path.exists():
        return {}
    got = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            v = json.loads(line)
            got[v["id"]] = v
    return got


def cmd_rereview(args) -> int:
    candidates = collect_at_risk(only_generic_synonym=args.only_generic_synonym)
    done = _load_jsonl(RE_VERDICTS)
    todo = [c for c in candidates if c["id"] not in done]
    if args.shard:
        i, n = (int(x) for x in args.shard.split("/"))
        todo = [c for k, c in enumerate(todo) if k % n == i - 1]
    if args.limit:
        todo = todo[:args.limit]
    batches = [todo[i:i + args.batch_size] for i in range(0, len(todo), args.batch_size)]
    print(f"  at-risk promoted : {len(candidates):,}")
    print(f"  already re-reviewed: {len(done):,}")
    print(f"  to re-review     : {len(todo):,} in {len(batches):,} batch(es)")
    if not args.apply:
        print("\n  DRY RUN - no reviewer called. Re-run with --apply.")
        return 0
    out_path = Path(args.out) if args.out else RE_VERDICTS
    out_path.parent.mkdir(parents=True, exist_ok=True)
    counts = {"KEEP": 0, "DEMOTE": 0}
    for n, batch in enumerate(batches, 1):
        items = [{"id": c["id"], "label": c["label"], "synonyms": c["synonyms"],
                  "interpro_entry": c["interpro"], "definition": c["definition"]}
                 for c in batch]
        prompt = (f"{STRICT_RUBRIC}\n\nRe-review these {len(items)} definitions:\n\n"
                  f"{json.dumps(items, indent=1)}")
        try:
            raw = _call_reviewer(prompt, args.model, args.timeout)
            verdicts = _parse_verdicts(raw, batch, args.model, allowed={"KEEP", "DEMOTE"})
        except Exception as exc:
            print(f"  batch {n}/{len(batches)}: FAILED ({type(exc).__name__}: {exc})"[:180])
            continue
        with out_path.open("a", encoding="utf-8") as fh:
            for v in verdicts:
                fh.write(json.dumps(v, ensure_ascii=False) + "\n")
                counts[v["verdict"]] += 1
        print(f"  batch {n}/{len(batches)}: {len(verdicts)}/{len(batch)}   running: {counts}")
    print(f"\n  wrote {sum(counts.values()):,} verdicts to {out_path}")
    return 0


def cmd_demote(args) -> int:
    """Reverse a promotion exactly, using the stub the record still carries.

    Nothing is reconstructed: the composed definition was never deleted, only displaced,
    so demoting restores it verbatim from `definitions[]`. The promotion event stays in
    curation_history and a demotion event is appended - the record keeps the whole story
    rather than pretending the promotion never happened.
    """
    import yaml
    verdicts = _load_jsonl(RE_VERDICTS)
    demote = {k: v for k, v in verdicts.items() if v["verdict"] == "DEMOTE"}
    print(f"  re-review verdicts: {len(verdicts):,}   DEMOTE: {len(demote):,}")
    changed = skipped = 0
    problems = []
    for vid, v in sorted(demote.items()):
        path = ROOT / v["path"]
        text = path.read_text(encoding="utf-8")
        rec = yaml.safe_load(text)
        # "already demoted" is recorded on the PARKED ABSTRACT, not on
        # definition_source -- demoting restores the stub's source there, so testing
        # definition_source never matches and a re-run walked on to report a spurious
        # "marker not found" for every record it had already done. It failed safe, but
        # a tool that cries wolf on a clean re-run trains you to ignore it.
        if any(DEMOTED in (d.get("source") or "") for d in (rec.get("definitions") or [])):
            skipped += 1
            continue
        stub = next((d for d in (rec.get("definitions") or [])
                     if STUB_SOURCE in (d.get("source") or "")), None)
        if stub is None:                     # never guess at a definition
            problems.append(f"{vid}: stub missing, cannot demote")
            continue
        out = replace_scalar(text, "definition",
                             folded("definition", " ".join((stub.get("text") or "").split())))
        out = replace_scalar(out, "definition_source", f'definition_source: "{STUB_SOURCE}"\n')
        out = replace_scalar(out, "mapping_status", "mapping_status: SEEDED\n")
        # the parked abstract records that it was reviewed AND rejected, so it is not
        # picked up as a fresh candidate by collect_candidates on a later run
        old = f'(LLM-generated, LLM-reviewed {v["reviewer"]}, not curator-reviewed)"'
        new = f'(LLM-generated, LLM-reviewed {v["reviewer"]}, {DEMOTED})"'
        if old not in out:
            problems.append(f"{vid}: parked abstract marker not found")
            continue
        out = out.replace(old, new)
        event = (f'curation_history:\n  - timestamp: "{args.timestamp}"\n'
                 f'    curator: review-llm-abstracts\n'
                 f'    action: "Demoted definition on stricter re-review ({v["reviewer"]}): '
                 f'describes the superfamily, not the family; PROPOSED -> SEEDED"\n'
                 f'    llm_assisted: true\n')
        out = append_to_section(out, "curation_history", event)
        if out == text:
            continue
        changed += 1
        if args.apply:
            path.write_text(out, encoding="utf-8")
    verb = "demoted" if args.apply else "would demote"
    print(f"  {verb}: {changed:,}   already done: {skipped:,}")
    for p in problems[:10]:
        print(f"  PROBLEM {p}")
    if problems:
        print(f"  {len(problems)} record(s) could not be demoted safely and were left alone")
    if not args.apply:
        print("  DRY RUN - re-run with --apply to write.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("review", help="run the LLM reviewer over unreviewed abstracts")
    r.add_argument("--apply", action="store_true", help="actually call the reviewer")
    r.add_argument("--limit", type=int, default=0)
    r.add_argument("--batch-size", type=int, default=15)
    r.add_argument("--model", default="claude-sonnet-5")
    r.add_argument("--timeout", type=int, default=600)
    r.add_argument("--shard", default="", metavar="i/n", help="review only shard i of n")
    r.add_argument("--out", default="", help="verdict file to append to (default: the shared one)")
    r.set_defaults(func=cmd_review)

    rr = sub.add_parser("rereview", help="stricter re-review of superfamily-level promotions (#112)")
    rr.add_argument("--apply", action="store_true")
    rr.add_argument("--limit", type=int, default=0)
    rr.add_argument("--batch-size", type=int, default=15)
    rr.add_argument("--model", default="claude-sonnet-5")
    rr.add_argument("--timeout", type=int, default=600)
    rr.add_argument("--shard", default="", metavar="i/n")
    rr.add_argument("--only-generic-synonym", action="store_true",
                    help="reproduce the original narrow selection (see docstring)")
    rr.add_argument("--out", default="")
    rr.set_defaults(func=cmd_rereview)

    dm = sub.add_parser("demote", help="apply DEMOTE verdicts, restoring the composed stub")
    dm.add_argument("--apply", action="store_true")
    dm.add_argument("--timestamp", default="2026-08-03T00:00:00Z")
    dm.set_defaults(func=cmd_demote)

    p = sub.add_parser("promote", help="apply PROMOTE verdicts to the records")
    p.add_argument("--apply", action="store_true")
    p.add_argument("--timestamp", default="2026-08-03T00:00:00Z")
    p.set_defaults(func=cmd_promote)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
