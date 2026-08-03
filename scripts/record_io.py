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

import yaml

try:                                    # libyaml is ~11x faster on these sections
    from yaml import CSafeLoader as _Loader   # 652us vs 7.2ms per record
except ImportError:                     # pure-Python fallback; same semantics
    from yaml import SafeLoader as _Loader

_TOP_KEY = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*:")
_LIST_ITEM = re.compile(r"^\s*-\s")


def has_graph(text: str, graph_id: str) -> bool:
    """True if the record already carries a graph with exactly this `graph_id`.

    WHY THIS ONE READS BY PARSING, WHILE `append_to_section` STILL DOES STRING SURGERY
    ---------------------------------------------------------------------------------
    Writing must preserve hand formatting, so appending stays textual. *Reading* has
    no such constraint, and inferring YAML structure from indentation was a losing
    game: this function grew one branch per review round — indented items, dash-only
    items, quoted values, trailing comments, `graph_id` not first, non-zero item
    indent — and the seventh round still found two more shapes it got wrong:

      * a `description: |-` literal scalar whose text contains `- prose` captured the
        item indent from a dash *inside the scalar*, after which the scalar's own
        `graph_id:` text was read as an item key. That is the worst possible failure:
        it reported True for a graph the record does NOT have (so the builder skips
        it forever) and False for the one it DOES (so the builder appends a duplicate).
      * a flow-style item, `- {graph_id: x}`, matched no branch at all, and unlike an
        inline value on the key line `append_to_section` does not refuse it — so the
        builder appended a second copy of a graph already present.

    Both vanish if the section is parsed rather than pattern-matched. Only the
    `causal_graphs:` block is handed to the parser, not the whole record, so the cost
    stays proportional to the graphs and a folded `definition:` elsewhere cannot spoof
    a match. A malformed section raises rather than silently answering False: every
    one of the 424,467 records parses today, so this cannot fire on current data, and
    a loud failure beats the silent duplication that a False would cause.
    """
    want = graph_id.strip()
    return want in _graph_ids(text)


def _graph_ids(text: str) -> set[str]:
    """Every `graph_id` in the record's `causal_graphs:` section."""
    lines = text.splitlines()
    try:
        i = next(n for n, ln in enumerate(lines) if ln.startswith("causal_graphs:"))
    except StopIteration:
        return set()
    block = [lines[i]]
    for ln in lines[i + 1:]:
        if ln and _TOP_KEY.match(ln):
            break
        block.append(ln)
    section = yaml.load("\n".join(block), Loader=_Loader) or {}
    graphs = section.get("causal_graphs") or []
    if not isinstance(graphs, list):
        return set()
    return {str(g["graph_id"]).strip() for g in graphs
            if isinstance(g, dict) and g.get("graph_id") is not None}


def _section_lines(text: str, key: str):
    """The lines belonging to a top-level `key:` block, excluding the key line."""
    inside = False
    for line in text.splitlines():
        if line.startswith(f"{key}:"):
            inside = True
            continue
        if inside:
            if line and _TOP_KEY.match(line):
                return
            yield line


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

    Returns the original text unchanged when `payload` has no items, and also
    when the key carries an inline value it cannot safely extend — callers
    treat "unchanged" as "could not splice, skip this record".
    """
    lines = text.splitlines(keepends=True)
    items = payload.split("\n", 1)[1] if "\n" in payload else ""
    if not items.strip():
        return text

    start = next((i for i, ln in enumerate(lines) if ln.startswith(f"{key}:")), None)
    if start is not None and lines[start][len(key) + 1:].strip():
        # The key carries an inline value — `causal_graphs: []` or a flow-style
        # `[{graph_id: g1}]`. Appending block-style items after that yields
        # unparseable YAML. No record in the corpus is written this way, so this
        # cannot fire today; it returns unchanged rather than corrupting, and every
        # caller already treats "unchanged" as "could not splice, skip this record".
        return text
    if start is None:
        lic = next((i for i, ln in enumerate(lines) if ln.startswith("license:")), None)
        at = lic if lic is not None else len(lines)
        head = "".join(lines[:at])
        # A record whose final line has no newline would otherwise be concatenated
        # with the payload — `label: x` + `causal_graphs:` = `label: xcausal_graphs:`.
        if head and not head.endswith("\n"):
            head += "\n"
        tail = "".join(lines[at:])
        # Guard the boundary AFTER the payload too: a payload with no trailing
        # newline fused into the next key (`- reference: PMID:1license: CC0`).
        if payload and not payload.endswith("\n") and tail:
            payload += "\n"
        return head + payload + tail

    end = start + 1
    while end < len(lines) and not _TOP_KEY.match(lines[end]):
        end += 1

    # Re-indent the payload to match the section it joins. PyYAML always emits list
    # items at column 0, but a hand-curated record may indent them — two do, and they
    # are `beta-lactamase-class-a-mcsa2` and `-class-b1-mcsa15`, the only records
    # carrying hand-written residue→substrate edges. Appending column-0 items into a
    # two-space list produced unparseable YAML on exactly those two.
    indent = ""
    for ln in lines[start + 1:end]:
        m = re.match(r"^(\s*)-\s", ln)
        if m:
            indent = m.group(1)
            break
    if indent:
        items = "".join(indent + ln if ln.strip() else ln
                        for ln in items.splitlines(keepends=True))

    head = "".join(lines[:end])
    # `license:` is optional, so a section can be the last thing in the file — and
    # if its final line has no newline, appending fuses the two: `edges: []` +
    # `- graph_id: g2` -> `edges: []- graph_id: g2`. The key-absent branch below
    # guards this; the key-present branch did not.
    if head and not head.endswith("\n"):
        head += "\n"
    tail = "".join(lines[end:])
    if items and not items.endswith("\n") and tail:
        items += "\n"
    return head + items + tail


def insert_before_license(text: str, payload: str) -> str:
    """Insert `payload` immediately before `license:`, or append it.

    Equivalent to what the builders did with `re.sub(r"^license:", …)` but with no
    replacement-template evaluation, so a backslash in `payload` stays a backslash.
    """
    lines = text.splitlines(keepends=True)
    lic = next((i for i, ln in enumerate(lines) if ln.startswith("license:")), None)
    if lic is None:
        return text.rstrip("\n") + "\n" + payload
    tail = "".join(lines[lic:])
    if payload and not payload.endswith("\n") and tail:
        payload += "\n"
    return "".join(lines[:lic]) + payload + tail
