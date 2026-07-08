#!/usr/bin/env python3
"""Shared primitive for the layered-definition composers.

Every `enrich_*_defs.py` composer adds a typed layer to a record's
`definitions:` list (GENERAL / STRUCTURAL / MECHANISTIC). Records increasingly
carry MORE THAN ONE layer (a domain has both a STRUCTURAL fold description and a
MECHANISTIC binding description), so a composer must **append into the existing
`definitions:` list**, not emit a second `definitions:` key (which would be a
duplicate mapping key → invalid YAML).

`add_layer` does exactly that, idempotently:
  • if the record already carries a layer of `kind`, it is a no-op;
  • if a `definitions:` list exists, the new item is appended to it;
  • otherwise a `definitions:` block is created (before `license:` if present,
    else at end of file).

Regex-based (matching the house style of the other seeders/composers) — the
YAMLs are seeder-emitted with a stable shape, so a structural parse isn't
warranted, but the block-extent logic below is deliberately conservative.

Stdlib-only.
"""

from __future__ import annotations

import re


def def_body(text: str) -> str:
    """The main `definition:` scalar (folded or inline), whitespace-collapsed."""
    m = (re.search(r"(?m)^definition:[ \t]*[>|]-?\s*\n((?:[ \t]+.*\n)+)", text)
         or re.search(r"(?m)^definition:[ \t]+(?![>|]\s*$)(.+)$", text))
    return " ".join(m.group(1).split()) if m else ""


def label_of(text: str) -> str:
    m = re.search(r'(?m)^label:[ \t]+"?(.+?)"?\s*$', text)
    return m.group(1).strip() if m else ""


def has_kind(text: str, kind: str) -> bool:
    """True if a `definitions:` list item of this kind already exists."""
    return bool(re.search(rf"(?m)^\s*-\s*kind:\s*{re.escape(kind)}\b", text))


def _item(kind: str, layer_text: str, source: str, method: str) -> str:
    body = " ".join((layer_text or "").split())
    src = source.replace("\\", "\\\\").replace('"', '\\"')
    return ("  - kind: %s\n"
            "    text: >-\n      %s\n"
            '    source: "%s"\n'
            "    method: %s\n") % (kind, body, src, method)


def add_layer(text: str, kind: str, layer_text: str, source: str,
              method: str = "SOURCED") -> tuple[str, bool]:
    """Return (new_text, changed). No-op (changed=False) if `kind` already
    present or `layer_text` is empty."""
    if not (layer_text and layer_text.strip()):
        return text, False
    if has_kind(text, kind):
        return text, False
    item = _item(kind, layer_text, source, method)

    m = re.search(r"(?m)^definitions:[ \t]*$", text)
    if m:
        # Find the extent of the existing list (indented lines after the key),
        # then insert the new item right after the last list line.
        start = m.end()
        lines = text[start:].splitlines(keepends=True)
        consumed = 0
        for ln in lines:
            if ln.strip() == "" or re.match(r"[ \t]", ln):
                consumed += len(ln)
            else:
                break
        # trim any trailing blank lines back into the tail, not the block
        block = text[start:start + consumed]
        block = block.rstrip("\n") + "\n"
        insert_at = start + len(block)
        return text[:insert_at] + item + text[insert_at:], True

    block = "definitions:\n" + item
    if re.search(r"(?m)^license:", text):
        return re.sub(r"(?m)^(license:.*)$", lambda mm: block + mm.group(1),
                      text, count=1), True
    return text.rstrip("\n") + "\n" + block, True
