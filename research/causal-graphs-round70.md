---
topic: causal-graphs
round: 70
date: 2026-08-07
target: aro/FUNC_RESISTANCE — cleavage chemistries under ARO:3000557, 8 records
prior_round: causal-graphs-round69.md
---

# Causal graphs — Round 70: four cleavage chemistries, and the round I nearly destroyed 5,036 records

8 records: β-lactam hydrolysis (5), fusidic-acid lactonisation (2), bacitracin
amidohydrolysis (1). Each mechanism-term definition is specific and, unlike round 68's
group transfers, **none involves a donor at all** — these reactions cleave the drug or add
to it directly.

## Three mistakes, in order

**1. I reused round 68's factory unchanged.** Its notes say *"the donor is given as
'usually'/'often', so it is not modelled as a node"* — **false** for a hydrolase. I wrote
that onto 8 records before noticing. Fixed with a `hedged_donor` flag; a test pins the
correct wording for both branches.

**2. My fix landed in the wrong function.** I inserted the new keyword by string index,
searching for `"ARO:3000450", "hydroxylation"` — which **round 63's rifampin config uses
too**, and appears first. The kwarg went onto `_rifampin_modification_config`, which does
not accept it. A `TypeError` caught this one immediately; it is the only one of the three
that failed loudly.

**3. `--repromote` rewrote 5,036 records.** To pick up the corrected notes on 8 records I
reached for `--repromote`, which re-promotes *everything already curated under the family
term*. ARO:3000557 is an ancestor of thousands of β-lactamases curated in rounds 12–16
under their **own** configs. The generic hydrolysis config overwrote them:

```
5036 files changed, 346247 insertions(+), 305823 deletions(-)
KPC record: PROSITE:PS00146 gone   ← the class A active-site wiring, destroyed
```

Nothing was committed. `git checkout -- data/` restored all 5,036, and the 8 legitimate
promotions were then redone with a plain `--apply`, which only touches drafts.

## What actually protected the corpus

Not a gate — **`--repromote` is documented as destructive and I used it anyway.** What
saved it was checking a *named prior record* (KPC's PS00146) immediately after seeing an
implausible number, rather than trusting the count. That is the same habit that caught
rounds 52, 53, 59 and 68: read a specific record the tool claims to have handled.

The lesson worth keeping: **`--repromote` must never be used to refresh a subset.** Its
blast radius is every descendant of the family term, and family terms in ARO are deep
ancestors. Filed as **#280**.

## Also: a config-count assertion broke, for the third time

Round 68's test asserted `len(cfgs) == 3`. Adding four cleavage configs broke it — a test
about donor hedging, failing because of an unrelated addition. Now selects on the three
transfer mechanism ids. **Third time this session**, after #235 and rounds 35 and 48.

## Provenance

* records touched: **8** · SEEDED → REVIEWED · 5,036 wrongly-rewritten records reverted
* `just test`: **640 passed** (+1) · `just validate` on all 8: **0 failures**
* corpus: **371,907 edges · 0 errors · 371,907/371,907 snippet-cited**
* drafts remaining: **448 → 440**

## Open questions

* **#280** — `--repromote` needs a scope narrower than the family term, or a confirmation
  prompt when it would touch more than N records.
* **12 drafts under ARO:3000557** carry only the generic `ARO:0001004` and no specific
  chemistry; they need reading individually.
