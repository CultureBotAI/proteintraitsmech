# Definition-state review across data sources

Deep-dive audit of definition coverage/quality per source and axis, prompted by
the observation that **STRUCTURE-source definitions still look lacking**. Also
answers: *does the definition-only embedding include both the general and the
mechanistic definition?*

Method: scanned all 317,621 records — for each, the main `definition` word count,
whether it matches a stub template (`… node 'X' (sccs …)`, `…-group 'Y' (…)`,
`CATH … 1.20.81: Z`), and which layered `definitions[].kind` it carries.

## Headline: layered definitions exist, but unevenly and with a missing kind

| Layer kind | Records | Source(s) |
|---|--:|---|
| STRUCTURAL | 54,519 | ECOD (all levels), CATH, SCOP **cf-fold only** |
| GENERAL | 7,375 | EC |
| **MECHANISTIC** | **0** | — none populated |

**No MECHANISTIC layer exists.** The mechanistic *content* is real but lives only
in the main `definition` string of the enzyme/active-site sources — it is never
labelled, so it can't be selected on:
- M-CSA (1,003 records, ~85-word mechanistic active-site descriptions),
- Rhea (18,558, the catalysed reaction),
- EC (7,375, the catalysed reaction — these also got a GENERAL layer).

## STRUCTURE axis — where it's lacking (91,265 records)

Per source: `avgW` = main-definition words, `struct%` = has a STRUCTURAL layer,
`stub%` = main definition is a template stub.

| source | n | avgW | struct% | stub% | read |
|---|--:|--:|--:|--:|---|
| ecod | 45,113 | 8 | **99%** | 100% | stub main def, but STRUCTURAL layer covers it ✓ |
| **scop** | 22,810 | 8 | **5%** | 100% | **only cf-folds have STRUCTURAL; 21.5k sf/fa/dm nodes have neither** |
| **ted** | 13,860 | 20 | **0%** | 0% | de-novo/novel folds — informative-ish def, but no fold classification to describe |
| cath | 8,151 | 9 | 99% | 97% | STRUCTURAL layer covers it ✓ |
| mcsa | 1,003 | 85 | 0% | 0% | rich mechanism prose — should be a MECHANISTIC layer |

By category the two big holes are **`STRUCT_DOMAIN` (13,514 — SCOP `dm` "automated
matches" placeholder nodes, 0% structural)** and the **SCOP `sf`/`fa` superfamily/
family levels** — all under a real fold but not carrying its description.

(No STRUCTURE record has a truly *empty* main definition — 0/91,265 — the problem
is stub/placeholder text, not absence.)

## Why the obvious fix doesn't work for SCOP sf/fa/dm

SCOP's `dir.com` comment file carries the structural prose only at the **fold
(cf)** level (1,281 comments — already used). At sf/fa level its comments are
**curatorial** ("automatically mapped to Pfam 02327", "not a true family"), not
structural. So SCOP's non-fold levels can't be sourced the same way.

## Recommended fixes (in priority order)

1. **SCOP structural inheritance (~21k).** Every SCOP sf/fa/dm node sits under a
   fold whose sccs prefix identifies it (`c.55.2.0` → fold `c.55`). Inherit the
   cf-ancestor's STRUCTURAL description (labelled "inherited from fold c.55"), the
   same pattern used for RepeatsDB geometry reps. Clean, sourced, big coverage.
2. **Populate the MECHANISTIC layer (~27k).** Label the existing mechanistic prose:
   M-CSA active-site mechanism → MECHANISTIC; Rhea/EC catalysed reaction →
   MECHANISTIC. This is what makes the *definition-only* map carry a real
   mechanistic dimension, and completes the general+mechanistic pairing the FUNCTION
   axis was meant to have.
3. **TED (13,860) — document the gap.** These are AlphaFold *novel* folds with no
   reference classification, so a named structural description isn't sourceable.
   The honest options are (a) leave the geometric summary it already has, or (b) a
   future pass computing geometric descriptors (secondary-structure string, contact
   topology) from the AF model — a real project, not a text lift.

## Answer: does the definition-only embedding include general + mechanistic?

The definition-only embedding (`embed_records --text-mode definition`) is
`definition + all layered-definition texts`, so it **does** include the GENERAL
layer (7,375 EC) and the STRUCTURAL layer (54,519) alongside the main definition.
It does **not** include a MECHANISTIC layer **because none exists yet** — the
mechanistic content is only in the unlabelled main `definition` (which *is*
embedded, so the semantics are present, just not as a distinguishable layer).
Populating the MECHANISTIC layer (fix #2) is what would make it explicit.
