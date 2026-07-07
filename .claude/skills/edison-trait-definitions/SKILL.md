---
name: edison-trait-definitions
description: Use this skill to research and write consistent trait DEFINITIONS in batches, one data source at a time — prioritizing trait categories whose records have stub/empty definitions, using the corpus's already-good definitions as style exemplars, and enforcing definitions that are consistent hierarchically across a (source, trait_category, trait_axis) grouping and down the parent→child tree. It applies the Edison method (many small evidence-backed experiments, write a research/ report every round) to definitions rather than to source discovery (that is the sibling `edison-deep-research` skill). Trigger when asked to improve/write/backfill definitions, fill definition gaps, make definitions consistent across a source/category/axis, or "deep research definitions for batch/source X".
---

# Edison Trait Definitions

Sibling of [[edison-deep-research]] (which finds new *sources*). This one makes
the definitions of records we already have **complete and consistent**, source by
source. Records carry a main `definition` string plus layered
`definitions[{kind: GENERAL|STRUCTURAL|MECHANISTIC, text, source, method}]` — see
`research/definition-state-review.md` for the state of play.

## The one rule that is never skipped

> **Every round produces a markdown file under `research/`.** Name it
> `research/trait-definitions-round<N>.md` (increment per round, never overwrite).
> The ranked gap table + the per-batch definition pattern are the deliverable.

## What a good definition is (score every batch)

1. **Substantive, not a template stub.** Rejects `"<X> node 'Y' (sccs …)"`,
   `"<name> — an NCBIfam protein family (NF…, equivalog)"`, `"represents a domain
   found in …"`-only. Says what the trait *is* / does / is built from.
2. **Sourced, not invented.** Composed from the source's own metadata (product,
   EC/GO, activity, mechanism, fold names) or its abstract/paper — never
   fabricated. LLM-generate only to fill genuine gaps, and stamp
   `method: GENERATED`.
3. **Consistent within the (source, category, axis) batch.** Every record in the
   batch follows the *same sentence pattern* — same lead, same field order, same
   voice. This is the core ask: a reader should not be able to tell two records
   in the batch were written separately.
4. **Consistent down the hierarchy.** A child's definition is compatible with its
   `parent_traits` — an ECOD family under fold `X` echoes the fold's structural
   description; a GH13 subfamily def is a specialization of the GH13 def; it never
   contradicts the parent. Prefer *inheriting/specializing* the parent over
   writing from scratch.
5. **Right layer.** Enzyme/mechanism prose → a MECHANISTIC layer; a plain
   "what it is" → GENERAL; structural elements + arrangement → STRUCTURAL; the
   main `definition` stays the general fallback.

## Protocol

1. **Read prior rounds** (`research/trait-definitions-round*.md`) +
   `research/definition-state-review.md`. Carry forward the open batches; don't
   redo a finished one.
2. **Enumerate the gap** with the audit below — rank (source, axis, category)
   batches by stub-definition count where `lay%` (layered-def coverage) is low.
   The worst batches with **no** compensating layer are the targets (e.g. NCBIfam
   FUNC_PROTEIN_FAMILY, ARO FUNC_RESISTANCE, CDD FUNC_ORTHOLOG_GROUP); a stub main
   def is OK if a STRUCTURAL/MECHANISTIC layer already carries the content.
3. **Pick ONE batch** (one source × category). Pull **5 current records** and
   **3–5 exemplar definitions** from a well-populated sibling in the *same axis/
   category* (InterPro/Pfam/CDD abstracts, GO, EC are the usual exemplars).
4. **Find the content source.** What metadata does the batch's source expose that
   a definition can be *composed* from? (e.g. NCBIfam `hmm_PGAP.tsv` →
   product_name + family_type + EC + GO; ARO → mechanism + drug class; CDD → the
   embedded name + `[functional category]`.) Verify with `WebSearch`/`WebFetch`
   on the source's docs/paper when the convention is unclear.
5. **Design the pattern** — one sentence template the whole batch will follow,
   filled from the metadata, echoing the parent. Write it out with 3 worked
   examples across the batch's range.
6. **Write the enrichment** (`scripts/enrich_<source>_definitions.py`): idempotent,
   dry-run-by-default, composes the pattern per record from the raw metadata,
   `method: SOURCED` (or `GENERATED` + flag where composed by LLM). Model it on
   the existing `enrich_*_defs.py` scripts.
7. **Write the round report** (template below); validate a sample
   (`just validate`); note the coverage delta.
8. **Re-embed when a batch lands** — definitions feed the maps + related-traits;
   batch several enrichments, then run the embed pipeline once (it is the dominant
   compute — see `research/tool-value-analysis.md`).

## Enumerate the gap (reproducible audit)

```bash
python3 - <<'PY'
import os, re, collections
STUB = re.compile(r"(node '|group '|-group |sccs |\(sccs|classification node|"
                  r"automated matches|represents (a|the) |— an? \w+ (protein )?family)", re.I)
def body(t):
    m = (re.search(r'(?m)^definition:[ \t]*>-\s*\n((?:[ \t]+.*\n)+)', t)
         or re.search(r'(?m)^definition:[ \t]+(?![>|]\s*$)(.+)$', t))
    return " ".join(m.group(1).split()) if m else ""
agg = collections.defaultdict(lambda: {"n": 0, "w": 0, "stub": 0, "lay": 0})
for root, _, fs in os.walk('data/traits'):
    for fn in fs:
        if not fn.endswith('.yaml'): continue
        t = open(os.path.join(root, fn)).read()
        s = (re.search(r'^identifier:\s*([A-Za-z0-9_]+):', t, re.M) or [0, '?'])[1].lower()
        a = (re.search(r'^trait_axis:\s*(\S+)', t, re.M) or [0, '?'])[1]
        c = (re.search(r'^trait_category:\s*(\S+)', t, re.M) or [0, '?'])[1]
        d = body(t); w = len(d.split())
        v = agg[(s, a, c)]; v["n"] += 1; v["w"] += w
        v["stub"] += (w < 12 or bool(STUB.search(d))); v["lay"] += ('definitions:' in t)
rows = [(v["stub"], s, a, c, v["n"], v["w"]//v["n"], 100*v["stub"]//v["n"], 100*v["lay"]//v["n"])
        for (s, a, c), v in agg.items() if v["n"] >= 100]
rows.sort(reverse=True)
print(f"{'source':<12}{'axis':<11}{'category':<26}{'n':>7}{'avgW':>5}{'stub%':>6}{'lay%':>6}")
for st, s, a, c, n, w, sp, lp in rows[:25]:
    flag = "  <- TARGET" if lp < 20 and sp > 50 else ""
    print(f"{s:<12}{a[:10]:<11}{c:<26}{n:>7,}{w:>5}{sp:>5}%{lp:>5}%{flag}")
PY
```

`lay% < 20 and stub% > 50` = a real gap (stub def, nothing else carrying the
content). High stub% with high lay% is fine — a layer already covers it.

## Report template

```markdown
---
topic: trait-definitions
round: <N>
date: <YYYY-MM-DD>
batch: <source> / <trait_category> / <trait_axis>
prior_round: trait-definitions-round<N-1>.md
---

# Trait definitions — Round <N>: <source>/<category>

## Gap (from the audit)
| source | axis | category | n | avgW | stub% | lay% |
...

## Current vs exemplar
- current (×3): "<stub def>"
- exemplar (sibling, ×3): "<good def>"

## Content source
<what metadata composes the definition; verification URLs>

## The consistent pattern
`<template>` — filled from `<fields>`, echoing parent `<parent field>`.
Worked examples (×3 across the batch's range):
1. …

## Coverage
records: N · will define: M (sourced K / generated K) · residual gap: …
```

## Best practices

1. **One source per round.** Consistency is *within* a batch; mixing sources
   breaks it. Finish a source's category before moving on.
2. **Compose, don't hallucinate.** The batch's own release almost always has the
   content (a product name, an activity, EC/GO, a fold name). Reach for the raw
   file first; `WebSearch` only to learn the convention or fill a true blank.
3. **Echo the parent.** Read the `parent_traits` record's definition first and
   specialize it — that is what makes definitions consistent *down* the tree.
4. **Same pattern, every record.** Encode the pattern in an `enrich_*` script so
   all N records are byte-consistent; never hand-write definitions one by one.
5. **Flag generated text.** `method: GENERATED` on anything an LLM wrote, so the
   provenance stays honest (`DefinitionMethodEnum`).
6. **Validate + re-embed.** `just validate` a sample; the maps/related-traits
   only reflect new definitions after a re-embed, so batch them.
7. **Write the report even for a small batch.** The Edison rule: no report → the
   round didn't happen.
