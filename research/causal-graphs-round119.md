---
topic: causal-graphs
round: 119
date: 2026-08-10
target: aro/FUNC_RESISTANCE — furA (2) + mshC (2), 4 records
prior_round: causal-graphs-round118.md
---

# Causal graphs — Round 119: the most complete regulatory sentence, attached to no resistance claim

## furA states its molecular basis and never mentions the drug

> *"Transcriptional regulator furA, **represses** the transcription of the
> catalase-peroxidase gene **katG** and its own transcription **by binding to the promoter
> region**."*

Direction, two targets, and the **molecular basis** — more regulatory detail than any other
record in this corpus. Rounds 78, 79, 110 and 115 all curated regulators whose definitions
gave direction at best and never said *how*.

**And it makes no resistance claim at all.** katG activates isoniazid, so repressing katG is
the obvious route — CARD's sentence contains neither the drug nor the word *resistance*.

That is round 106's rpoB position inverted: there the **drug's action** was known and
unstated; here the **entire resistance link** is. A test bans *isoniazid*, *resist* and
*activat* from the asserted text.

## Two mshC records, curated differently

Round 94 left **ARO:3004889** — *"Mutations … resulting in the inability for antibiotic to
function"*, no function named.

**ARO:3004904** is the same gene and adds the chemistry: *"It catalyzes the ATP-dependent
condensation of **GlcN-Ins** and **L-cysteine** to form **L-Cys-GlcN-Ins**."*

So one is curated and one stays a draft — as with mshA and mshB in round 109. A test asserts
exactly that split, because "two records for one gene, treated differently" is the kind of
thing a later pass would read as an inconsistency and fix.

Still *"to function"*, so still no prodrug edge — the sixth graph that word has decided.

## Provenance

* records touched: **4** · SEEDED → REVIEWED
* `just test`: **725 passed** (+2), **run before the push** · corpus: **0 errors**
* drafts remaining: **203 → 199**

## Open questions

* **~91 unconfigured drafts remain.** FrxA (nitrofuran/metronidazole), ahpC's second record
  and the ESX-5 system term were read this round and not curated.
