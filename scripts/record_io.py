#!/usr/bin/env python3
"""Shared, tested primitives for editing a hand-formatted ProteinTraitRecord YAML.

Five builders independently reimplemented the same two operations — "append a block
to a list-valued key" and "has this record already got graph X?" — and four of the
six defects found reviewing PR #89 were instances of getting one of them wrong
(issue #93). This module is the single implementation, and `tests/test_record_io.py`
is the first test in the repo (issue #96).

WHY STRING SURGERY RATHER THAN A YAML ROUND-TRIP
------------------------------------------------
Deliberate, and it should stay that way. Records are hand-formatted — folded
scalars, stable key order, no reflowed prose — and `yaml.safe_load` +
`yaml.safe_dump` would rewrite all 424k of them on the first touch. These helpers
edit only the lines they must.

THE THREE MISTAKES THIS EXISTS TO PREVENT
------------------------------------------
1. **Stripping the parent key and not restoring it on every branch.** The M-CSA
   builder removed `causal_graphs:` from its payload unconditionally, then re-added
   it on only one of three insertion branches. A record lacking the key got a bare
   sequence item under a mapping — unparseable YAML — and the caller's
   `out == text` guard missed it because the text *had* changed.
2. **`re.sub` with a string replacement.** `\\g`, `\\1` and bare backslashes in the
   spliced YAML are interpreted as template syntax. No current source release
   contains a backslash, which is precisely why this would surface as corruption
   long after the change that introduced it.
3. **Testing `"causal_graphs:" in text` to decide "already done".** Records now
   carry several graphs, so the presence of *a* graph says nothing about whether
   *this* graph was written; the over-broad test permanently skipped records that
   still needed their own.
"""

from __future__ import annotations

import re

_TOP_KEY = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*:")
_LIST_ITEM = re.compile(r"^\s*-\s")


def has_graph(text: str, graph_id: str) -> bool:
    """True if the record already carries a graph with exactly this `graph_id`.

    Anchored and whole-line: a substring test would report `..._mcsa454` as a match
    for `..._mcsa45` and silently skip a record that still needs writing.

    The optional `- ` is load-bearing. `graph_id` is the first key of a list item, so
    PyYAML writes it as `- graph_id: reaction_chemistry`. An earlier fix used
    `^\\s*graph_id:` and therefore matched **nothing** — which turned the builders
    from "skip records already done" into "append a duplicate graph on every run",
    strictly worse than the over-broad test it replaced. Caught by the test below.
    """
    return re.search(rf"^\s*(?:-\s*)?graph_id:\s*{re.escape(graph_id)}\s*$", text,
                     re.M) is not None


def append_to_section(text: str, key: str, payload: str) -> str:
    """Append `payload` to the record's `key:` section, or insert it whole.

    `payload` is a complete block including its own `key:` line, e.g. the output of
    `yaml.safe_dump({"causal_graphs": [graph]})`. Passing the full block — rather
    than pre-stripping the key and hoping the caller re-adds it — is what makes the
    two cases safe to handle in one place:

      * key present → the payload's `key:` line is dropped and its items are
        appended after the section's existing items (so `curation_history` stays in
        chronological order);
      * key absent  → the payload is inserted whole, before `license:` if the record
        has one (it is the last key by convention), else at the end.

    Returns the original text unchanged only if `payload` has no items.
    """
    lines = text.splitlines(keepends=True)
    items = payload.split("\n", 1)[1] if "\n" in payload else ""
    if not items.strip():
        return text

    start = next((i for i, ln in enumerate(lines) if ln.startswith(f"{key}:")), None)
    if start is None:
        lic = next((i for i, ln in enumerate(lines) if ln.startswith("license:")), None)
        at = lic if lic is not None else len(lines)
        return "".join(lines[:at]) + payload + "".join(lines[at:])

    end = start + 1
    while end < len(lines) and not _TOP_KEY.match(lines[end]):
        end += 1
    return "".join(lines[:end]) + items + "".join(lines[end:])


def insert_before_license(text: str, payload: str) -> str:
    """Insert `payload` immediately before `license:`, or append it.

    Equivalent to what the builders did with `re.sub(r"^license:", …)` but with no
    replacement-template evaluation, so a backslash in `payload` stays a backslash.
    """
    lines = text.splitlines(keepends=True)
    lic = next((i for i, ln in enumerate(lines) if ln.startswith("license:")), None)
    if lic is None:
        return text.rstrip("\n") + "\n" + payload
    return "".join(lines[:lic]) + payload + "".join(lines[lic:])
