#!/usr/bin/env python3
"""OBO 1.4 line syntax, in one place.

`seed_obo.py` and `seed_psi_mod.py` each had their own copy of this parsing, and
the copies drifted: a fix for quoted descriptions landed in one and not the other,
which is the sixth time in this review cycle that a fix was applied in one place
and not its twin. Both now import from here, so a third divergence needs someone to
add a third copy deliberately.

The grammar this handles, from the OBO 1.4 spec:

    <ID> "<description>" {<trailing modifiers>} ! <comment>

Every suffix is optional. The order matters when stripping, and so does quoting —
`!` and `{` are ordinary characters inside a quoted description, so a naive
`split("!")` truncates `"activation A/B! now"` mid-string and leaves an unbalanced
fragment behind.
"""

from __future__ import annotations

import re

_MODIFIERS = re.compile(r"\s*\{[^{}]*\}\s*$")
_DESCRIPTION = re.compile(r'\s+"(?:[^"\\]|\\.)*"\s*$')

# The escapes OBO defines. An unrecognised `\x` is left alone rather than silently
# losing its backslash.
_ESCAPES = {"n": "\n", "W": " ", "t": "\t", ":": ":", ",": ",", '"': '"',
            "\\": "\\", "(": "(", ")": ")", "[": "[", "]": "]", "{": "{", "}": "}"}


def strip_comment(raw: str) -> str:
    """Drop a trailing `! comment`, ignoring any `!` inside a quoted string.

    Splitting on the first `!` unconditionally — which both copies used to do —
    truncates a description containing one and leaves an unterminated quote, after
    which the CURIE test fails and the whole xref is silently dropped, or worse,
    the fragment is misclassified as a citation because it still holds a `/`.
    """
    out, in_quote, i = [], False, 0
    while i < len(raw):
        c = raw[i]
        if c == "\\" and in_quote and i + 1 < len(raw):
            out.append(raw[i:i + 2])
            i += 2
            continue
        if c == '"':
            in_quote = not in_quote
        elif c == "!" and not in_quote:
            break
        out.append(c)
        i += 1
    return "".join(out).strip()


def strip_suffixes(local: str) -> str:
    """Remove the optional `{modifiers}` and `"description"` from an xref local part.

    Spec order: modifiers sit outermost, so they come off first.
    """
    local = _MODIFIERS.sub("", local).strip()
    local = _DESCRIPTION.sub("", local).strip()
    return local


def unescape(value: str) -> str:
    """Decode OBO backslash escapes.

    OBO escapes the separators it uses structurally, so a DOI carrying a colon
    arrives as `10.1002/(SICI)1520-6327(1997)35\\:1`. Copying that through verbatim
    ships an identifier that does not resolve — GO:0016087 did exactly that.
    """
    out, i = [], 0
    while i < len(value):
        c = value[i]
        if c == "\\" and i + 1 < len(value) and value[i + 1] in _ESCAPES:
            out.append(_ESCAPES[value[i + 1]])
            i += 2
        else:
            out.append(c)
            i += 1
    return "".join(out)
