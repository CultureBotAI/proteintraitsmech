---
name: edison-deep-research
description: Use this skill for iterative, multi-source, fact-checked "Edison" deep research into candidate DATA SOURCES / RESOURCES to feed ProteinTraitsMech (or any similar knowledge base) — e.g. "find more sources of protein sequence/structure traits", "what other databases could we seed", "round 2 of the source research". It fans out web searches, verifies each candidate (download availability, licence, hierarchy, definition basis) against the acceptance criteria, dedupes against what is already seeded and against prior rounds, ranks the findings, and ALWAYS persists a cited markdown report under research/. Trigger on requests to research/expand data sources, do a "deep research" round, or continue a prior round.
---

# Edison Deep Research

Iterative, evidence-backed research into **candidate data sources** for the
knowledge base. "Edison" = do many small experiments (searches + verifications),
keep only what survives the criteria, and **write it down every time**.

## The one rule that is never skipped

> **Every run produces a markdown file under `research/`.** No exceptions. If a
> round's report isn't saved, the round isn't done. (Round 1 was lost because it
> lived only as seeding work — that must not recur.)

File naming: `research/<topic-slug>-round<N>.md`. For the standing topic use
`research/protein-trait-sources-round<N>.md`. Increment `<N>` per round; never
overwrite a prior round.

## Acceptance criteria (score every candidate)

1. **Established** — recognised, maintained community resource (has a NAR/db
   paper or equivalent, current release).
2. **Downloadable** — bulk data via FTP/HTTP/API/flat files; record the exact
   URL and format.
3. **Licence** — compatible with a CC0-redistributable KB. Flag anything
   non-commercial / no-derivatives / login-walled as ⚠️ or ⛔ with the reason.
4. **Hierarchy (preferred)** — a parent/child classification we can map to
   `parent_traits`. Note the levels.
5. **Minimum bar** — each trait is defined in terms of **sequence or structure**
   elements. Reject entity-only ontologies (e.g. PRO) and pure prediction tools.

## Protocol

1. **Read prior rounds first.** Load every `research/<topic>-round*.md`. Carry
   forward their "deferred" and "open gaps" lists; do not re-propose adopted
   sources.
2. **Enumerate the gap.** From the current corpus (facets / README seeds table),
   list under-populated or empty `trait_category` values — those are the
   targets.
3. **Fan out searches.** Run several `WebSearch` queries in parallel per gap
   (family/domain classifications, structural classifications, site/ligand,
   disorder, PTM, motif, enzyme-mechanism, repeats, …).
4. **Verify, don't trust.** For each surviving candidate, confirm download +
   licence + hierarchy from the source page or its paper (`WebFetch`/
   `WebSearch`). Capture citations (URLs).
5. **Dedupe & rank.** Drop anything already seeded or already adopted in a prior
   round. Rank ✅ / ⚠️ / ⛔ with a one-line rationale and the target category.
6. **Write the report** (template below), then propose the **next seeds** in
   priority order. Optionally add a `[[…]]`-linked memory for any durable
   finding.

## Report template

```markdown
---
topic: <topic>
round: <N>
date: <YYYY-MM-DD>
question: >- <the refined question>
prior_round: <topic>-round<N-1>.md
method: WebSearch/WebFetch verification, <month year>
---

# <Topic> — Round <N>

Builds on [Round <N-1>](<prior file>). Focus of this round: <gaps>.

## Ranked findings
| # | Source | Fit (category) | Hier | Download / format | Licence | Rec |
...

## Detail & rationale
<per-source paragraph with the evidence that decided ✅/⚠️/⛔>

## Recommended next seeds (priority order)
1. ...

## Sources
- <name> — <url> · <url>
```

## Conventions

- Prefer **integrative** and **hierarchical** resources (they yield real
  `parent_traits`) — e.g. InterPro over any single member DB.
- Always record the **licence** verbatim enough to judge CC0 compatibility; a
  great source with a non-commercial licence is ⛔ for ingestion (link/reference
  only).
- Keep the report skimmable: the ranked table is the deliverable; prose only
  where a call needs justifying.
- After writing, tell the user the file path and the top 3 recommended seeds.

## History

- [`research/protein-trait-sources-round1.md`](../../../research/protein-trait-sources-round1.md) — baseline (adopted PROSITE/TED/ECOD/UniProt/PSI-MOD/M-CSA/DisProt/PSI-MI/PATO/METPO; deferred NCBIfam/CDD/IDEAL; rejected PRO).
- [`research/protein-trait-sources-round2.md`](../../../research/protein-trait-sources-round2.md) — InterPro, CATH, RepeatsDB, MEROPS, SCOP2, MobiDB, BioLiP2, MetalPDB, SFLD, dbPTM, CAZy; ELM rejected on licence.
