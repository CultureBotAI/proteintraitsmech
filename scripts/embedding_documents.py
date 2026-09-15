"""Existing full/definition embedding document assembly, shared with JSONL export."""

from __future__ import annotations


def human_cat(cat: str) -> str:
    """SEQ_PTM_SITE -> 'ptm site' etc. (drop the axis prefix, spell it out)."""
    parts = (cat or "").split("_")
    if parts and parts[0] in ("SEQ", "STRUCT", "MIXED", "FUNC", "EVO"):
        parts = parts[1:]
    return " ".join(parts).lower()


def build_document(r: dict, d: dict, mode: str = "full") -> tuple[str, bool]:
    """Return exactly the legacy document text and its label-fallback flag."""
    if mode not in {"full", "definition"}:
        raise ValueError("text mode must be full or definition")
    used_label_fallback = False
    rid = r["id"]
    definition = str(d.get("def") or r.get("def") or "")
    # layered definitions [[kind, text, source], …] → their texts, kind-prefixed
    layered = [
        f"{(x[0] or '').lower()}: {x[1]}".strip(": ")
        for x in (d.get("defs") or [])
        if x and len(x) > 1 and x[1]
    ]
    if mode == "definition":
        doc = ". ".join(p for p in [definition] + layered if p)
        if not doc:  # issue #10: surface the fallbacks
            doc = str(r.get("label") or rid)
            used_label_fallback = True
    else:  # full
        syn = d.get("syn") or []
        chem = r.get("chem") or []  # ChEBI *names* (semantic) not ids
        pat = d.get("pat")
        cat = human_cat(r.get("cat", ""))
        axis = (r.get("axis") or "").replace("_", " ").lower()
        # Identifiers/groundings: opaque individually, but their SHARED tokens
        # cluster same-source / same-classification-subtree entries — the
        # record's own hierarchical id (siblings share its prefix, e.g.
        # ECOD:F.1.1.1.3 / …1.4), its parents (siblings share the exact parent
        # id), and its xrefs/mappings (related entries share groundings). That
        # within-source structural similarity is signal, not noise. Only
        # per-INSTANCE ids (canonical_example sequences/accessions) are excluded.
        ground = [rid]
        ground += [str(p[0]) for p in (d.get("pt") or []) if p and p[0]]
        ground += [str(x) for x in (d.get("xr") or [])]
        ground += [str(m[0]) for m in (d.get("mx") or []) if m and m[0]]
        ground = list(dict.fromkeys(ground))[:16]  # dedupe, cap
        parts = [str(r.get("label") or rid)]  # numeric label parses to int in the shard
        if cat:
            parts.append(f"{cat} ({axis} trait)")
        if definition:
            parts.append(definition)
        parts.extend(layered)  # structural / mechanistic / general layers
        if syn:
            parts.append("also known as " + ", ".join(str(s) for s in syn))
        if pat:  # sequence_pattern (regex/motif) is class-defining
            parts.append(f"pattern: {pat}")
        if chem:
            parts.append("chemistry: " + ", ".join(str(c) for c in chem[:8]))
        parts.append("identifiers: " + ", ".join(ground))
        doc = ". ".join(parts)
    return doc, used_label_fallback
