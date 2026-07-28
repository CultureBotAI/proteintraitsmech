---
date: 2026-07-27
issue: "#7 — clearing the tail"
prior: swissprot-trait-profiles-14.md
---

# Swiss-Prot trait profiles — Phase 15: three cleanup items, two of which said no

The remaining tail after the multi-trait families landed. All three were small and
well specified; two of them ended in "measured, don't act", which is worth
recording so they are not reopened blindly.

## 1. Stop re-requesting 10,238 dead accessions — done

`fetch_residue_frame.py --top-up` re-requested the same ~10,238 exemplar
accessions on every run. They are not errors: UniProt returns *no result* for
them inside an otherwise-successful batch (withdrawn or demerged entries), so
unlike the 9 malformed `UNS…` ones (#54, which 400'd loudly) nothing recorded
that they were dead.

An accession that comes back empty from a **successful** batch is now recorded in
the sidecar header as `_meta.absent` and skipped next time. The next top-up went
from "10,238 to fetch" to **0**.

## 2. The 68 SUPERFAMILY refutations — cannot be confirmed, and should not be

Phase 12 left the refuted identity pairs as a loose end: "check them against
SUPERFAMILY↔CATH mappings". Looking properly, most were never candidates:

| the 68 refuted pairs | count | what they are |
|---|--:|---|
| `type=domain` | **46** | InterPro *domain* entries — a different kind of entity from a homologous superfamily. `related_to` was always right. |
| `type=homologous_superfamily` on SUPERFAMILY | 22 | the only ones worth asking about |

For those 22 the answer is no, on principle rather than effort. **SUPERFAMILY is
SCOP-derived and CATH is an independent structural classification; neither
publishes a mapping to the other.** Confirming the pairs would mean asserting an
equivalence that no source database makes.

InterPro's `overlaps_with` field looked like a way in, and is not. `IPR010985`
(a homologous superfamily) overlaps six entries, among them:

| entry | type | name |
|---|---|---|
| IPR053853 | domain | Antitoxin FitA-like, ribbon-helix-helix |
| IPR002084 | family | Methionine repressor MetJ |
| IPR005569 | domain | Arc-like DNA binding domain |

A domain, a family and a superfamily cannot all be equivalent to one another.
`overlaps_with` records co-occurrence on proteins, which is what our
`related_to` edge already says. Promoting on that basis would be circular.

**These 22 stay `related_to` permanently.** Closing the loose end as
not-actionable rather than leaving it to be retried.

## 3. The docs payload — measured, and it did need acting on

Phase 14 warned the doubled exemplar payload might need a leaner projection. A
first measurement said no: exemplars were 28% of a detail bucket, of which
family classifications were a quarter.

That measurement was **against a stale local `docs/data/`**, built before the
cap-8 re-rank. Against the live bucket the answer inverts:

| | share of a detail bucket |
|---|--:|
| canonical_examples | **58.3%** (was 28% at cap 3) |
| — of which `family_classifications` | 12.0% |
| — of which sequences | 0.9% |
| everything else | 41.7% |

The fix is not to strip fields but to project fewer exemplars. Phase 14 raised
`--max-examples` 3 → 8 for a **data** reason — more protein sharing between
records, which is what the residue-frame aligner consumes — not so the detail
page could list eight of them. The record keeps all 8; the browser now shows the
top 5, which are the best because they are rank-ordered.

Saving: **~13%** of every detail bucket, affecting the 129-of-1,639 records in
the sampled bucket that carry more than five.

The lesson is the measurement, not the trim: the first reading came from an
artefact one build out of date and said the opposite of the truth.

## Gate

* Top-up verified to become a no-op (10,238 → 0) rather than assumed.
* The `overlaps_with` reasoning checked against real entries before being used to
  reject a confirmation path.
* Payload measured against the **live** artefact after the stale local copy gave
  the wrong answer.
