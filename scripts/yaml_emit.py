#!/usr/bin/env python3
"""The three functions every seeder uses to WRITE a record, in one place.

`record_io.py` owns editing a record that exists; this owns emitting one. Together they
close #93: the splice idiom moved to record_io during #100, and these three were the
remaining copy-paste surface.

    yaml_escape   43 copies, 10 distinct implementations
    folded        35 copies,  1 distinct behaviour among the seeders
    slugify       31 copies, 28 distinct implementations

WHY THIS IS A DROP-IN AND NOT A REWRITE
---------------------------------------
Changing what these emit would rewrite records: `yaml_escape` decides bytes and
`slugify` decides FILENAMES. So each function here was checked to be byte-identical to
every copy it replaces, over real corpus values, before anything was rewired:

  * the 10 `yaml_escape` copies agree on all 3,968 distinct scalar values sampled from
    the corpus, so one implementation is safe;
  * the 28 `slugify` copies differ in exactly two parameters and nothing else -
    `max_len` (60, 70, 80 or none) and the `fallback` used when the slug comes out
    empty (`cath`, `cazy`, `pfam`, ...). Character handling is identical: 37 copies use
    `[^A-Za-z0-9]+` and 2 use `[^a-z0-9]+`, which are the same thing after `.lower()`.
    Parameterising instead of picking a winner is what makes this rename nothing.

Consolidating by choosing one truncation length would have renamed files under
`ecod/` (34,959 records), `prosite/` (3,425), `mcsa/` (1,003) and `cazy/` (557).
"""

from __future__ import annotations

import re

_SLUG_RE = re.compile(r"[^A-Za-z0-9]+")

# Bare, these read back as something other than a string, so they must be quoted.
_YAML11_WORDS = {"null", "true", "false", "yes", "no", "on", "off", "none", "~"}

# `~`, `.inf`, `.nan` are the punctuation forms of the same YAML 1.1 resolvers. Every
# copy quoted the WORD forms and none quoted these - one gap in ten places (#109).
_YAML11_PUNCT = {"~", ".inf", "-.inf", "+.inf", ".nan"}

_UNSAFE = set(": #{}[],&*!|>%@`\\\"'")

# A value that parses as a number reads back as int/float, not str (#109). Matches what
# YAML 1.1 resolves, including the octal and sexagesimal forms `0755` and `1:30`.
_NUMERIC = re.compile(r"""^[-+]?(
      0b[01_]+ | 0o?[0-7_]+ | 0x[0-9a-fA-F_]+          # binary / octal / hex
    | [0-9][0-9_]*(\.[0-9_]*)?([eE][-+]?[0-9]+)?       # int / float / exponent
    | \.[0-9_]+([eE][-+]?[0-9]+)?                      # .5
    | [0-9][0-9_]*(:[0-5]?[0-9])+(\.[0-9_]*)?          # sexagesimal 1:30
)$""", re.X)


def yaml_escape(text: str) -> str:
    """A scalar that reads back as exactly the string given.

    Identical to the ten copies it replaces on every value in the corpus. It differs
    from them only on inputs none of those copies handled and none of the sources have
    yet produced - the three latent gaps measured in #109:

      * a bare numeric (`123`, `0755`, `1.5`) came back as int/float;
      * `~`, `.inf`, `.nan` came back as None/float;
      * a newline or tab produced YAML that would not parse at all.

    All three are fixed here by quoting, which is why consolidating changes no existing
    record: nothing in the corpus is any of those shapes.
    """
    if not text:
        return '""'
    if (any(c in _UNSAFE for c in text)
            or text[0] in "-?"
            or text.lower() in _YAML11_WORDS
            or text in _YAML11_PUNCT
            or _NUMERIC.match(text)
            or any(c in text for c in "\n\r\t")
            or text != text.strip()):
        body = (text.replace("\\", "\\\\").replace('"', '\\"')
                    .replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t"))
        return f'"{body}"'
    return text


def folded(text: str) -> list[str]:
    """A folded block scalar as `[">-", "  <one long line>"]`.

    Whitespace is collapsed, so an embedded newline cannot emit a second unindented
    line and break the record. Returns the lines rather than a string because that is
    the shape all nine seeder copies used.
    """
    return [">-", f"  {' '.join((text or '').split())}"]


def slugify(text: str, max_len: int | None = 70, fallback: str = "entry") -> str:
    """A filename-safe slug.

    `max_len` and `fallback` are parameters rather than constants precisely because the
    28 copies differ ONLY in those two, and hardcoding either would rename records that
    are already on disk. Pass what the calling seeder used:

        slugify(name, 70, "cath")      # the 23-seeder majority
        slugify(name, 80, "entry")     # ecod, mcsa, obo
        slugify(name, 60, "cazy")      # cazy
        slugify(name, None, "ps")      # prosite, which never truncated
    """
    return (_SLUG_RE.sub("-", text.lower()).strip("-")[:max_len]) or fallback


# --------------------------------------------------------------- source-text repair

def _mojibake_bytes(text: str) -> bytes:
    """The bytes a double-decode started from, if this text is one.

    Encoded per character because the damage mixes two tables: `€` (U+20AC) exists only
    in cp1252, while a C1 control such as U+0090 exists only in latin-1. A single
    `.encode("cp1252")` raises on the second and a single `.encode("latin-1")` raises on
    the first, so either alone silently declines to repair half the real cases.
    """
    out = bytearray()
    for ch in text:
        try:
            out += ch.encode("cp1252")
        except UnicodeEncodeError:
            if ord(ch) >= 0x100:
                raise
            out.append(ord(ch))
    return bytes(out)


def repair_mojibake(text: str) -> str:
    """Undo a UTF-8-decoded-as-cp1252 round trip, or return the text unchanged.

    Sources here serve UTF-8 that something upstream read as cp1252, so a hyphen
    (U+2010, bytes `E2 80 90`) arrives as `â€` + U+0090 and `ü` arrives as `Ã¼`. The
    damage is reversible exactly because it is a pure byte round trip: re-encode by the
    wrong table, decode by the right one.

    Only applies when the result is valid UTF-8, so text that is merely non-ASCII —
    Greek letters in a CAZy fold name, an em dash written correctly — is left alone.
    That is what makes this safe to run over every incoming string rather than over a
    hand-maintained list of known-bad values.
    """
    if text.isascii():
        return text
    # Repair RUN BY RUN, not whole-string. A CAZy definition carries correctly encoded
    # Greek (`(β / α) 8 barrel`, U+03B2) beside the damaged hyphen, and Greek has no
    # cp1252 byte -- so an all-or-nothing repair raises on it and silently declines to
    # fix the rest of the string. That is exactly what happened on GH20: the seeder ran,
    # the record was rewritten, and the mojibake was still there.
    out, run = [], []

    def flush():
        if not run:
            return
        chunk = "".join(run)
        try:
            out.append(_mojibake_bytes(chunk).decode("utf-8"))
        except (UnicodeDecodeError, UnicodeEncodeError, ValueError):
            out.append(chunk)
        run.clear()

    for ch in text:
        if ord(ch) < 0x100 or _CP1252_ENCODABLE(ch):
            run.append(ch)
        else:
            flush()
            out.append(ch)
    flush()
    return "".join(out)


def _CP1252_ENCODABLE(ch: str) -> bool:
    try:
        ch.encode("cp1252")
        return True
    except UnicodeEncodeError:
        return False


def folded_block(key: str, text: str, indent: str = "") -> str:
    """A whole `key: >-` block as one string, ready to splice into a record.

    The list-returning `folded` above is what a seeder wants when it is assembling
    `lines`; this is what a caller wants when it is splicing a finished block into
    existing text. Both collapse whitespace, so they cannot disagree about the value —
    they differ only in shape (#125).

    `indent` prefixes both lines, for a block nested under another key.
    """
    return f"{indent}{key}: >-\n{indent}  {' '.join((text or '').split())}\n"
