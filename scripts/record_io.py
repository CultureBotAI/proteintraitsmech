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
    return want in graph_ids(text)


class RecordError(ValueError):
    """This record cannot be read, and the caller should skip it rather than guess.

    One type for every "unusable record" reason, so a builder catches this instead of
    `yaml.YAMLError` (#104). That keeps the parser choice inside this module: callers
    do not import yaml, and a future change of loader does not touch six builders.
    Deliberately narrower than `Exception`, which would swallow real bugs.
    """


class DuplicateKeyError(RecordError):
    """A record carries the same top-level key twice, so its value is ambiguous."""


def graph_ids(text: str) -> set[str]:
    """Every `graph_id` in the record's `causal_graphs:` section.

    Raises `DuplicateKeyError` if `causal_graphs:` appears twice at top level (#105).
    This block-scan reads the FIRST occurrence; `yaml.safe_load` keeps the LAST, so on
    such a record the two disagree and `has_graph` answers from the block a loader
    discards — reporting a graph absent that a reader sees, after which a builder
    appends yet another copy.

    Raising rather than picking a side is the point. A duplicated top-level key is
    corruption, not a formatting choice: it is exactly what `insert_before_license`
    produced when it added a second `causal_graphs:` key, and PyYAML then silently
    dropped the original graphs. Preferring the last block would make `has_graph` agree
    with the loader and hide that failure completely.

    Latent and pre-existing: 0 of 424,467 records carry a duplicated top-level key, and
    the textual scanner this replaced had the same first-block behaviour.
    """
    lines = text.splitlines()
    try:
        i = next(n for n, ln in enumerate(lines) if ln.startswith("causal_graphs:"))
    except StopIteration:
        return set()
    if any(ln.startswith("causal_graphs:") for ln in lines[i + 1:]):
        raise DuplicateKeyError(
            "record has more than one top-level 'causal_graphs:' key; this scan reads "
            "the first, yaml.safe_load keeps the last, so the answer would be arbitrary")
    block = [lines[i]]
    for ln in lines[i + 1:]:
        if ln and _TOP_KEY.match(ln):
            break
        block.append(ln)
    try:
        section = yaml.load("\n".join(block), Loader=_Loader) or {}
    except yaml.YAMLError as exc:                       # unparseable section (#104)
        raise RecordError(f"causal_graphs section does not parse: {exc}") from exc
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
    # Normalise the payload to column 0 BEFORE applying the section's indent. The
    # original re-indent ADDED to whatever the payload already carried, which is right
    # only while every caller passes `yaml.safe_dump` output (always column 0). A
    # hand-written payload that indents its own items — the natural way to write one,
    # since it is how the file itself looks — was double-indented to four spaces and
    # the record stopped parsing. Found by the canary on the first `demote`, on a
    # record that already carried a curation_history event.
    payload_indent = ""
    for ln in items.splitlines():
        m = re.match(r"^(\s*)-\s", ln)
        if m:
            payload_indent = m.group(1)
            break
    if payload_indent:
        items = "".join(
            (ln[len(payload_indent):] if ln.startswith(payload_indent) else ln.lstrip())
            if ln.strip() else ln
            for ln in items.splitlines(keepends=True))
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


# --------------------------------------------------------------- re-seed merging (#100)

# Keys a curator or a review pass owns. A re-seed must never regress these on a record
# that has been curated, however stale the seeder thinks they are.
CURATED_SCALARS = ("definition", "definition_source", "mapping_status")


def top_level_keys(text: str) -> list[str]:
    """The record's top-level keys, in file order."""
    return [m.group(1) for m in
            (re.match(r"^([A-Za-z_][A-Za-z0-9_]*):", ln) for ln in text.splitlines()) if m]


def extract_block(text: str, key: str) -> str | None:
    """The `key:` line plus everything under it, up to the next top-level key."""
    lines = text.splitlines(keepends=True)
    start = next((i for i, ln in enumerate(lines) if ln.startswith(f"{key}:")), None)
    if start is None:
        return None
    end = start + 1
    while end < len(lines) and not (lines[end].strip() and _TOP_KEY.match(lines[end])):
        end += 1
    return "".join(lines[start:end])


def replace_block(text: str, key: str, block: str) -> str:
    """Replace a top-level key's whole block, or insert it before `license:`.

    Shared rather than reimplemented: `review_llm_abstracts.py` grew its own
    `replace_scalar` for exactly this, and one copy of a splice rule is the standing
    lesson of #93 — the same fix has had to be applied to a forgotten twin six times.
    """
    lines = text.splitlines(keepends=True)
    start = next((i for i, ln in enumerate(lines) if ln.startswith(f"{key}:")), None)
    if not block.endswith("\n"):
        block += "\n"
    if start is None:
        return insert_before_license(text, block)
    end = start + 1
    while end < len(lines) and not (lines[end].strip() and _TOP_KEY.match(lines[end])):
        end += 1
    return "".join(lines[:start]) + block + "".join(lines[end:])


def is_curated(text: str) -> bool:
    """True if a curator or review pass has touched this record.

    Two independent signals, because either can be present without the other: a
    status past SEEDED, or any curation_history at all. A record that has neither is
    a pristine import and a re-seed may overwrite it freely.
    """
    status = re.search(r"^mapping_status:\s*(\S+)", text, re.M)
    if status and status.group(1).strip().strip('"\'') != "SEEDED":
        return True
    return "\ncuration_history:" in text or text.startswith("curation_history:")


def merge_on_reseed(existing: str, fresh: str) -> str:
    """Fold a freshly seeded record into an existing one without losing curation.

    #100: `--force` overwrote the file outright, so a re-seed would have destroyed
    39,647 causal graphs, 96,476 evidence blocks and 1,604 reviewed definitions. The
    flag exists to pick up a new source release, which is a real need, so the answer
    is to let source-derived facts refresh while curated ones stay put.

    TWO RULES, AND ONLY ONE OF THEM IS A JUDGEMENT CALL
    ---------------------------------------------------
    1. **Any top-level key the fresh record does not contain is restored, always.**
       No heuristic guards this. If the seeder did not emit it, the seeder does not
       own it — that covers causal_graphs and curation_history, which no seeder emits
       at all, and evidence on the records where this seeder does not produce it.

    2. **definition, definition_source, mapping_status and definitions[] are kept
       only when the record shows curation** (status past SEEDED, or a
       curation_history). Those ARE seeder-owned fields, so this is the policy call:
       a curated record keeps its own, a pristine import refreshes.

    The first draft gated rule 1 on the curation check too. Sweeping 500 real curated
    records found it dropping evidence and causal_graphs from 14 of them: the graph
    builders add `causal_graphs` without flipping mapping_status or writing a
    curation_history, so 58,048 records carry curated content while looking pristine.
    Gating the safe rule on a heuristic reintroduced the exact bug being fixed.
    """
    out = fresh
    fresh_keys = set(top_level_keys(fresh))

    # rule 1 - unconditional
    for key in top_level_keys(existing):
        if key in fresh_keys:
            continue
        block = extract_block(existing, key)
        if block:
            out = replace_block(out, key, block)

    # rule 1b - list-valued keys are UNIONED, never replaced, on every record.
    # `xrefs` and `trait_relations` are seeder-emitted AND enriched afterwards by the
    # *2go mapping backfills, so "the seeder emitted it, the seeder owns it" is wrong
    # for them: a PROSITE --force dropped 4,193 GO xrefs and 2,745 trait_relations,
    # on records that look pristine (SEEDED, no curation_history) and so are not
    # reached by rule 2 at all. #100's title says it -- no re-seed is safe over
    # ENRICHED records, and enrichment does not announce itself.
    #
    # The trade is deliberate: a source that drops an xref no longer removes it here,
    # so a stale entry can persist. Keeping a stale xref is recoverable; silently
    # losing a curated mapping is not.
    out = _union_list_keys(existing, fresh, out)

    # rule 2 - only for a record that shows curation
    if not is_curated(existing):
        return out
    for key in CURATED_SCALARS:
        block = extract_block(existing, key)
        if block:
            out = replace_block(out, key, block)
    old_defs = extract_block(existing, "definitions")
    new_defs = extract_block(fresh, "definitions")
    if old_defs and new_defs:
        merged = _merge_definitions(old_defs, new_defs)
        if merged:
            out = replace_block(out, "definitions", merged)
    elif old_defs:
        out = replace_block(out, "definitions", old_defs)
    return out


# Fields that record WHERE an entry came from rather than WHAT it says. Two entries
# differing only in these are the same fact relabelled, not two facts: PROSITE renamed
# its relation_source from "derived" to "PROSITE documentation", and a naive union
# appended a second copy of the same relation to 2,745 records.
_PROVENANCE_FIELDS = frozenset({"relation_source", "mapping_source"})


def _key(value):
    """An identity for a list entry that ignores which run labelled it."""
    if isinstance(value, dict):
        return tuple(sorted((k, str(v)) for k, v in value.items()
                            if k not in _PROVENANCE_FIELDS))
    return str(value)


def _union_list_keys(existing: str, fresh: str, out: str) -> str:
    """Union every top-level key that is a list in both records, existing entries first.

    Order matters: an existing entry keeps its position so a re-seed does not reshuffle
    a curated list, and genuinely new entries are appended.
    """
    try:
        old_doc, new_doc = yaml.safe_load(existing) or {}, yaml.safe_load(fresh) or {}
    except yaml.YAMLError:
        return out
    if not isinstance(old_doc, dict) or not isinstance(new_doc, dict):
        return out
    for key, old_val in old_doc.items():
        new_val = new_doc.get(key)
        if key == "definitions" or not isinstance(old_val, list) or not isinstance(new_val, list):
            continue
        merged = list(old_val) + [v for v in new_val if _key(v) not in {_key(o) for o in old_val}]
        if merged == old_val and old_val == new_val:
            continue
        block = yaml.safe_dump({key: merged}, sort_keys=False, allow_unicode=True, width=100)
        out = replace_block(out, key, block)
    return out


def _merge_definitions(old_block: str, new_block: str) -> str | None:
    """Existing `definitions[]` entries, then any fresh one not already present.

    Compared on normalised text rather than on the whole item: the same abstract
    re-seeded carries a different `source` once it has been reviewed
    (`...LLM-reviewed...` vs `...not curator-reviewed`), and matching on the item as a
    whole would append a duplicate of every reviewed definition on each re-seed.

    A fresh entry is also dropped when the record ALREADY HAS AN ENTRY FROM THAT
    SOURCE, even though the text differs (#148). Two entries citing one source with
    two different texts is not two definitions, it is one definition and a stale copy,
    and this function is only reached for a curated record — where rule 2 has already
    decided the record's own version wins. Without this, the same source restating
    itself appended silently:

      * a re-seed against a new release whose abstract text changed, and
      * any caller passing an EDITED copy of the file rather than a fresh record,
        which appended a second entry beside the one it meant to replace (the
        failure mode `write_record` now documents, measured at 1,707 records).

    The invariant it defends holds across the corpus today: of 9,711 records carrying
    more than one `definitions[]` entry, ZERO have two entries sharing a source.
    """
    def items(block):
        parsed = yaml.safe_load(block) or {}
        return parsed.get("definitions") or []

    def norm(value):
        return " ".join(str(value or "").split())

    try:
        old, new = items(old_block), items(new_block)
    except yaml.YAMLError:
        return None
    seen = {norm(d.get("text")) for d in old if isinstance(d, dict)}
    seen_sources = {norm(d.get("source")) for d in old if isinstance(d, dict)}
    seen_sources.discard("")
    extra = [d for d in new
             if isinstance(d, dict) and norm(d.get("text")) not in seen
             and norm(d.get("source")) not in seen_sources]
    if not extra:
        return old_block
    tail = yaml.safe_dump({"definitions": extra}, sort_keys=False, allow_unicode=True, width=100)
    return append_to_section(old_block, "definitions", tail)


def write_record(path, text: str, encoding: str = "utf-8", *, merge: bool = True) -> None:
    """Write a seeded record, folding it into whatever curation the file already has.

    The single choke point for #100. Seeders called `path.write_text(...)` directly,
    so `--force` replaced the file and took the curation with it. Routing every trait
    write through here means a seeder does not have to remember the rule, which is the
    only way it stays true across 47 of them.

    PRECONDITION: `text` IS A FRESHLY GENERATED RECORD
    --------------------------------------------------
    Not an edited copy of the file at `path`. `merge_on_reseed` reads `text` as "what
    the seeder would emit today" and reconciles it against the file; hand it an edited
    copy of that same file and it reconciles the record against itself, which fails in
    two ways that no gate catches because both outputs are schema-legal:

      * `CURATED_SCALARS` (definition, definition_source, mapping_status) are restored
        from the file on any curated record, so an edit to one of them is REVERTED;
      * a changed `definitions[]` entry no longer matches by text, so it is appended
        beside the entry it was meant to replace rather than replacing it.

    Measured, on a repair that edited definitions in place and routed the result
    through here: 566 of 1,707 records silently kept the text the repair had removed,
    and 1,707 duplicate `definitions[]` blocks were added (#148). The same-source rule
    in `_merge_definitions` now absorbs the second failure, but the first is exactly
    what rule 2 is for and cannot be fixed here.

    **Pass `merge=False` for an in-place edit of an existing record.** That writes the
    text given, unchanged -- which is what a repair, migration or errata script wants,
    and what `path.write_text` would have done.
    """
    if merge and path.exists():
        text = merge_on_reseed(path.read_text(encoding=encoding), text)
    path.write_text(text, encoding=encoding)
