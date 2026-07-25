---
date: 2026-07-24
issue: "#7 — close the loop: trait classes → real proteins"
prior: swissprot-trait-profiles-4.md
---

# Swiss-Prot trait profiles — Phase 5: auto-suggested `canonical_examples`

Phases 1-2 built the protein × trait matrix; phases 3-4 mined the cross-axis rules
and materialised them as an overlay. Every artefact so far has been *about* traits.
Phase 5 writes the matrix back onto the trait records themselves: **which real
proteins actually carry this trait**, ranked so the pick is an archetype rather
than an arbitrary carrier.

## What was written

`just suggest-examples --mine-rules --apply`

| | |
|---|--:|
| trait records given `canonical_examples` | **44,929** |
| `CanonicalExample` entries emitted | **86,580** |
| — rule-backed picks | 671 |
| — focus / annotation-ranked picks | 44,258 |
| records skipped (already had examples) | 6,783 |
| records skipped (trait too generic, >25% of matrix) | 4 |

By axis: 24,407 SEQUENCE, 18,180 FUNCTION, 2,342 STRUCTURE. By namespace: GO
17,315 · InterPro 10,704 · CDD 8,780 · Pfam 3,874 · CATH 2,342 · PROSITE 976 ·
NCBIfam 834 · EC 104.

Corpus-wide `canonical_examples` coverage goes from 59,770 → 104,699 records
(14.6% → 25.6%). **Every one of the 2,342 CATH fold records observed in the matrix
had no exemplar before this pass** — structure-derived classifications have no
UniProt signature query, so `fetch_uniprot_examples.py` never reached them.

Provenance is a new `ExampleSourceEnum` value, `SWISSPROT_PROFILE` — a *selection
over the local matrix*, not a fresh query, and evidence-ranked rather than
first-N-hits, so conflating it with `UNIPROTKB_API` would have misreported how the
pick was made. Each entry's `note` carries the derivation:

> `Swiss-Prot profile matrix (20,000 reviewed Homo sapiens entries): carrier of
> CATH:1.10.10.10 (1 of 239 carriers); also carries 8/8 empirically coupled
> cross-axis traits (rule coverage 1.00)`

## Ranking — and the degenerate first cut

The point is picking the carrier that best *exemplifies* the trait:

```
score = rule_coverage + 0.20·axis_span + w_focus·focus + w_depth·depth
```

* **rule_coverage** — confidence-weighted fraction of the trait's empirically
  coupled cross-axis partners (phase-4 rule endpoints, either direction) that this
  protein also carries. A protein carrying the signature *and* the fold it encodes
  *and* the function they imply is the archetypal carrier. Dominates where a rule
  exists.
* **focus** — `1/(1+k/5)` over the protein's *k* classification-namespace traits. A
  protein carrying this domain and little else exemplifies it more cleanly than a
  30-domain giant that merely contains it.
* **depth** — `n_GO/(n_GO+20)`: better-characterised proteins win.

`focus` and `depth` pull against each other, so they are weighted by what
"archetype" means on the trait's own axis — for a domain or fold the archetypal
carrier is the *focused* one (0.15/0.10), for a function it is the
*well-characterised* one (0.20/0.05).

**The first cut got this wrong and it was worth catching.** Annotation depth was
capped at 20 GO terms, which saturated for any well-annotated protein: **30% of
traits had a tied top pick**, broken alphabetically by accession. The result was
`A1A4Y4` winning 58 records on nothing but sort order. Making both terms smooth
dropped ties to **1.5%**, and the most-reused exemplars became APOE (139),
SIRT1 (127), TNF (124), CTNNB1, α-synuclein — concentration that is *semantically
earned* rather than an artefact. 11,860 distinct proteins serve as top picks.

Spot-checks: `GO:0044207` (translation initiation ternary complex) → eIF2 subunit 1;
`Pfam:PF04567` (RNA pol Rpb2 domain 5) → RPC2 / RPB2; `CATH:1.10.10.10` (winged
helix) → FOXC1 at rule coverage 1.00.

## Widening the rule set

The committed phase-4 overlay was mined over the namespaces carrying the
SEQUENCE↔STRUCTURE encoding signal (Pfam / PROSITE / SMART / NCBIfam → CATH / GO /
EC), so **InterPro- and CDD-identified traits have no partners in it at all** and
would have ranked on annotation alone. `--mine-rules` recomputes cross-axis
partners in-process over every corpus namespace at the same thresholds
(support ≥30, conf ≥0.95, lift ≥5) — 1,427 rules over 791 traits, versus 516 edges
in the overlay. This does not disturb the committed overlay; overlay confidences
win on collision.

Even so, only 671 of 44,929 records are rule-backed. **That is the honest headline
limitation**: for 98.5% of records the pick is a well-reasoned heuristic (focused,
well-characterised carrier), not a rule-grounded archetype. Rules need ≥30
supporting proteins in a 20,000-protein human slice, and most trait classes are
rarer than that.

## Gate

* Every rewritten file is re-parsed in memory before it is written — a malformed
  emission is reported, not committed. Zero verify failures across 44,929 records.
* `linkml-validate` on a 240-record sample stratified across all 8 namespaces
  (30 each): **no issues found**. The validator caught one real bug en route —
  a bare `fetched_at: 2026-07-25` parses as a YAML *date*, not the string the
  schema's pattern expects; it is now emitted quoted.
* Idempotent: records with existing examples are skipped, so curator picks are
  never touched and re-running is a no-op.
* `data/profiles/profiles.jsonl` (gitignored) now carries per-entry
  `name` / `taxon` / `taxon_label` / `length` / `reviewed` — `CanonicalExample`
  needs a `protein_label`, and re-querying UniProt for what the profile build
  already fetched would have been silly. Rebuild with
  `just build-profiles --query "reviewed:true AND organism_id:9606" --limit 20000
  --jsonl-only --apply`.

## Caveats

* **Human-only exemplars.** The matrix is 20,000 reviewed *Homo sapiens* entries,
  so every suggested example is human. For predominantly bacterial trait classes
  (NCBIfam, many CDD entries) a human carrier is a poor archetype where one exists
  at all — the 834 NCBIfam records reached here are the human-observable tail.
  Multi-organism profiles are the fix, and the next item.
* `SWISSPROT_PROFILE` examples are **suggestions**, not curator picks. They are
  distinguishable by `source` and can be swept or re-ranked wholesale.
* Records already carrying examples were skipped, so the two provenance schemes
  do not mix on a record unless `--force` is passed.

## Next

- **Multi-organism profiles** (mouse / yeast / *E. coli*): fixes the human-only
  exemplar bias, raises rule support so more records become rule-backed, and
  delivers the held-out-organism confirmation that the phase-3 rules are not
  human-specific.
- Protein × trait **browser map** (UMAP/PaCMAP of `profiles.jsonl`).
- Feed the shared exemplars into the residue-frame base overlay (Path 1) — records
  that now share a `canonical_examples` protein are candidates for residue-level
  alignment.
