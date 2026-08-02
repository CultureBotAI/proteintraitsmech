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

    Scoped to the `causal_graphs:` section, and tolerant of the ways YAML may write
    the same value. Three ways a looser test goes wrong:

      * `^\\s*graph_id:` matches **nothing**, because `graph_id` is the first key of
        a list item and PyYAML writes `- graph_id: …`. That mistake turned the
        builders from "skip records already done" into "append a duplicate on every
        run" — worse than the over-broad test it replaced.
      * Searching the whole document gives a **false positive** when the name appears
        in prose, e.g. a folded `definition:` containing the words `graph_id:
        reaction_chemistry`.
      * Matching a bare token gives a **false negative** on a quoted value
        (`- graph_id: "reaction_chemistry"`) or one with a trailing comment.
    """
    want = graph_id.strip()
    for line in _section_lines(text, "causal_graphs"):
        # Only a graph's OWN `graph_id` key counts. PyYAML writes it as the first
        # key of the list item (`- graph_id: …`) or, for a hand-formatted record,
        # at the item's own indent — never deeper. Accepting arbitrary indentation
        # let a nested scalar spoof it, e.g. a `description: |-` block whose text
        # happens to read `graph_id: reaction_chemistry`, which would make a builder
        # skip a graph the record does not have.
        m = re.match(r"(?:\s{0,2})(?:-\s*)?graph_id:\s*(.+?)\s*$", line)
        if not m:
            continue
        value = m.group(1)
        if value.startswith("#"):
            continue
        # strip a trailing comment, then surrounding quotes
        value = re.split(r"\s+#", value, maxsplit=1)[0].strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        if value == want:
            return True
    return False


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

    Returns the original text unchanged only if `payload` has no items.
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
        return head + payload + "".join(lines[at:])

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
    return head + items + "".join(lines[end:])


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
