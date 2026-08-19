#!/usr/bin/env python3
"""Scaffold a history record without a claw checkout.

PROVENANCE. Adapted from CultureBotAI/TraitMech@84322ab67d71
`scripts/new_history_record.py` (sha256 80549c3d6b17db3b), changing exactly three
things: the vendored schema path, the repo URL, and an example path in the usage text.

NOT covered by `just check-vendored-sync`, deliberately -- that gate enforces BYTE
identity against the hub, and this file cannot be byte-identical because those three
strings are repo-specific. It is a fallback scaffolder: claw's `kg_microbe_history`
is the canonical one when a checkout is available, and both write against the same
vendored `history.yaml` that `just validate-history` and CI check. The schema is the
contract; this is one of two producers of it.

`just new-history` calls claw's `kg_microbe_history` scaffolder, which needs a
`culturebotai-claw` checkout that is not always present — so on a machine
without one, records simply do not get written. Both edits in #294 were
hand-authored for that reason, and `history/README.md`'s own worked example is
literally the issue that PR was closing (#296).

The schema is already vendored at `src/proteintraitsmech/schema/history.yaml`, which is
what `just validate-history` and CI check against, so nothing about writing a
record actually requires claw. This is the fallback: same arguments, same output
contract (the record path is the last stdout line), validated against the same
vendored schema before it is written.

Claw stays the preferred path when available — `just new-history` tries it
first, so the canonical scaffolder keeps producing the canonical shape across
the fleet and this only fills the gap.

Usage:
    python scripts/new_history_record.py --kind record --slug cellulolysis \\
        --target-root data/traits/function/resistance/aro --event EDIT --outcome changed \\
        --summary "..." --details "..." --issue 183 --pr 294
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
HISTORY_ROOT = REPO_ROOT / "history"

# The layout is history/<kind-dir>/<slug>/, not history/records/<slug>/ for
# everything — history/infrastructure/curation-history/ is a live example. The
# schema does not constrain the path, so writing to the wrong directory
# validates clean and nothing downstream notices (#296 review).
#
# COPIED FROM claw's kg_microbe_history/scaffold.py KIND_DIRS, not inferred. The
# pluralisation is genuinely uneven (mappings/reports but schema/other), which is
# exactly why guessing it was the wrong move — and confirmed empirically by
# scaffolding all six kinds through claw and listing the directories.
KIND_DIRS = {"record": "records", "schema": "schema", "mapping": "mappings",
             "report": "reports", "infrastructure": "infrastructure",
             "other": "other"}

# Claw's placeholder, byte-for-byte. It has to be this exact string: the vendored
# schema carries `pattern: '^(?!TODO: replace this placeholder)'` specifically so
# a plain linkml-validate catches an unfilled record, and any OTHER wording — a
# near-miss like "TODO: fill in..." — slips past the negative lookahead and makes
# an unfilled record permanently committable.
CLAW_PLACEHOLDER = (
    "TODO: replace this placeholder before committing.\n"
    "What was done, what evidence or provider was used, how it was validated, "
    "and anything deliberately left undone.")
SCHEMA = REPO_ROOT / "src" / "proteintraitsmech" / "schema" / "history.yaml"
REPO_URL = "https://github.com/CultureBotAI/proteintraitsmech"

EVENTS = ("GENERAL", "CREATE", "EDIT", "REVIEW", "AUDIT")
OUTCOMES = ("changed", "no_change", "needs_followup", "blocked")
KINDS = ("record", "schema", "mapping", "report", "infrastructure", "other")


def session_id(timestamp: str, tool: str, seed: str) -> str:
    """`<compact-timestamp>-<tool>-<6 hex>`, matching the existing records.

    The suffix disambiguates two sessions that start in the same second; it is
    derived from the content rather than random so a re-run with identical
    arguments produces an identical id instead of a duplicate record.
    """
    # Date hyphens kept, time colons stripped — matching the existing records
    # (`2026-08-03T230903Z-claude-code-90a277`) rather than inventing a variant.
    date, _, clock = timestamp.partition("T")
    stamp = f"{date}T{clock.replace(':', '')}"
    digest = hashlib.sha256(seed.encode()).hexdigest()[:6]
    return f"{stamp}-{tool}-{digest}"


def _link(value: str, kind: str) -> str:
    """Expand a bare issue/PR number to a URL; pass a URL through unchanged.

    A DELIBERATE divergence from claw, which writes `--issue 296` through as the
    string "296". The schema declares these `range: uri`, and the one
    pre-existing committed record (history/records/dumbbell_shaped/) carries full
    URLs — so a bare number is both schema-wrong and unlike the corpus. Accepting
    either form means the same command produces a valid record through this path
    whichever way the caller writes it (#296).
    """
    value = value.strip()
    if value.startswith(("http://", "https://")):
        return value
    return f"{REPO_URL}/{kind}/{value.lstrip('#')}"


def build(args: argparse.Namespace, timestamp: str) -> tuple[dict, Path]:
    target_path = f"{args.target_root.rstrip('/')}/{args.slug}.yaml" \
        if args.target_root else args.path
    if not target_path:
        raise SystemExit("error: pass --target-root (with --slug) or --path")

    sid = session_id(timestamp, args.actor_name,
                     f"{target_path}|{args.summary}|{args.details}")
    actor = {"type": args.actor_type, "name": args.actor_name}
    for field, value in (("model", args.model), ("agent_tool", args.agent_tool),
                         ("agent_version", args.agent_version)):
        if value:
            actor[field] = value

    record: dict = {
        "history_version": 1,
        "target": {"kind": args.kind, "path": target_path},
        "session": {"id": sid, "timestamp": timestamp, "actors": [actor]},
        "events": [{
            "type": args.event,
            "outcome": args.outcome,
            # `sections` sits between outcome and summary: that is the schema's
            # declaration order and the order of the one committed record that
            # carries it. Appending it after `details` instead put the documented
            # invocation (history/README's headline example passes --sections) on
            # the divergent path.
            **({"sections": [x.strip() for x in args.sections.split(",") if x.strip()]}
               if args.sections else {}),
            "summary": args.summary,
            # Claw writes a placeholder rather than refusing, because a record is
            # scaffolded then edited. Matching it exactly, so the record FAILS
            # `just validate-history` until filled — which is what
            # history/README promises and what a near-miss string would break.
            "details": args.details or CLAW_PLACEHOLDER,
        }],
    }
    if args.slug:
        record["target"]["slug"] = args.slug
    links: dict = {}
    if args.issue:
        links["issues"] = [_link(i, "issues") for i in args.issue]
    if args.pr:
        links["prs"] = [_link(p, "pull") for p in args.pr]
    if args.url:
        links["urls"] = list(args.url)
    if links:
        # Between session and events, matching the existing records' field order
        # so a diff against a claw-written one is empty rather than a reshuffle.
        record = {"history_version": record["history_version"],
                  "target": record["target"], "session": record["session"],
                  "links": links, "events": record["events"]}

    out_dir = (Path(args.history_root) / KIND_DIRS[args.kind]
               / (args.slug or Path(target_path).stem))
    return record, out_dir / f"{sid}.yaml"


def validate(path: Path) -> None:
    """Validate before announcing success.

    A scaffolder that writes an invalid record is worse than none: CI's
    validate-history would fail on a file the author believed was generated
    correctly, in a directory that is append-only by policy.
    """
    result = subprocess.run(
        ["uv", "run", "linkml-validate", "--schema", str(SCHEMA),
         "--target-class", "HistoryRecord", str(path)],
        cwd=REPO_ROOT, capture_output=True, text=True)
    if result.returncode != 0:
        path.unlink(missing_ok=True)  # the temp file, never the target
        print(result.stdout or result.stderr, file=sys.stderr)
        raise SystemExit(
            f"error: generated record failed validation; not written ({path.name})")


def main(argv: list[str] | None = None) -> int:
    # The argument surface mirrors claw's `kg_microbe_history new` EXACTLY,
    # including which options are required and which have defaults. A fallback
    # that takes different arguments reproduces the original trap in a new form:
    # a command that works on a machine with claw fails on one without. This was
    # caught by running `just new-history` on a machine that HAS claw and
    # watching the two interfaces disagree (#296).
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--kind", required=True, choices=sorted(KINDS))
    ap.add_argument("--slug", default="", help="target identifier / directory name")
    ap.add_argument("--path", default="",
                    help="repo-relative path to the target; required for --kind other")
    ap.add_argument("--target-root", default="",
                    help="directory the target lives in, used to derive --path from --slug")
    ap.add_argument("--event", default="EDIT", choices=EVENTS)
    ap.add_argument("--outcome", default="changed", choices=OUTCOMES)
    ap.add_argument("--summary", required=True, help="one short line")
    ap.add_argument("--details", default="",
                    help="the substance; if omitted a TODO placeholder is written "
                         "for you to edit")
    ap.add_argument("--sections", default="", help="comma-separated")
    ap.add_argument("--actor-name", default="claude-code")
    ap.add_argument("--actor-type", default="ai_agent",
                    choices=("human", "ai_agent", "automation", "other"))
    ap.add_argument("--model", default="")
    ap.add_argument("--agent-tool", default="")
    ap.add_argument("--agent-version", default="")
    ap.add_argument("--issue", action="append", default=[])
    ap.add_argument("--pr", action="append", default=[])
    ap.add_argument("--url", action="append", default=[])
    ap.add_argument("--history-root", default=str(HISTORY_ROOT))
    ap.add_argument("--force", action="store_true",
                    help="overwrite an existing record; records are append-only, "
                         "so this is for correcting a mis-scaffolded one")
    ap.add_argument("--timestamp", default="",
                    help="ISO-8601 UTC; defaults to now. Set it for a reproducible id.")
    args = ap.parse_args(argv)

    timestamp = args.timestamp or _dt.datetime.now(
        _dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    record, out_path = build(args, timestamp)

    if out_path.exists() and not args.force:
        # Append-only: never silently overwrite. Identical arguments produce an
        # identical id, so this is the "already recorded" case, not a collision.
        raise SystemExit(f"error: {out_path} already exists; records are append-only")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    text = yaml.safe_dump(record, sort_keys=False, allow_unicode=True,
                          default_flow_style=False, width=88)

    # Validate a TEMP file, then move into place. Writing first and unlinking on
    # failure destroys whatever --force was overwriting, in a directory whose
    # entire policy is append-only (#296 review).
    # Keeps the .yaml suffix: linkml-validate picks its loader from the
    # extension and refuses a .tmp outright.
    # Keeps the .yaml suffix: linkml-validate picks its loader from the
    # extension and refuses a .tmp outright.
    scratch = out_path.with_name(f".{out_path.stem}.scratch.yaml")
    try:
        scratch.write_text(text)
        if args.details:
            validate(scratch)
        else:
            # The placeholder is SUPPOSED to fail the schema until edited, so
            # validating it directly would delete the record the caller asked
            # for. Validate a COPY with `details` substituted instead, so every
            # other field is still checked — otherwise `--timestamp nonsense`
            # writes a malformed record and exits 0 on this path.
            probe = dict(record)
            probe["events"] = [{**record["events"][0], "details": "placeholder probe"}]
            probe_path = out_path.with_name(f".{out_path.stem}.probe.yaml")
            try:
                probe_path.write_text(yaml.safe_dump(probe, sort_keys=False,
                                                     allow_unicode=True, width=88))
                validate(probe_path)
            finally:
                probe_path.unlink(missing_ok=True)
            print("note: --details omitted, so a placeholder was written. "
                  "`just validate-history` will fail until you replace it.",
                  file=sys.stderr)
        scratch.replace(out_path)
    finally:
        # A validation failure raises out of here, and an orphaned scratch file
        # in an append-only directory is its own small mess.
        scratch.unlink(missing_ok=True)
    # Path last on stdout, which is the contract `just new-history` documents.
    # Repo-relative when it can be, absolute otherwise: --history-root may point
    # outside the repo (the parity harness does), and relative_to() raises there.
    try:
        printable = out_path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        printable = out_path.as_posix()
    print(printable)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
