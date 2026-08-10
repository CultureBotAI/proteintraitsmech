---
topic: causal-graphs
round: 122
date: 2026-08-10
target: aro/FUNC_RESISTANCE — uL3 (ARO:3005082), drug-agnostic rpsL (ARO:3003419), 3 records
prior_round: causal-graphs-round121.md
---

# Causal graphs — Round 122: the in-trans shape recurs, and the first family split by a rule filed one round earlier

Round 121 named a mechanism kind on rpsL: **target alteration in trans.** The determinant is
a *protein*, but the drug's binding partner is the *rRNA*. The mutation does not change the
drug's site; it changes the conformation of the molecule that is one.

This round curates two more instances — and the first one has a primary paper that states
the shape outright, which round 121's did not.

## uL3 and pleuromutilins — the in-trans shape, measured

**PMID:12936991** (Bøsling 2003) is the paper CARD's definition rests on, and it supplies
four separate things:

| claim | verbatim |
|---|---|
| the drug's target | *"The antibiotic tiamulin targets the 50S subunit of the bacterial ribosome and interacts at the peptidyl transferase center."* |
| **which molecule is the determinant** | *"No mutations in the rRNA were selected as resistance determinants using a strain expressing only a plasmid-encoded rRNA operon."* |
| the substitution | *"…yielded a mutant with an A445G mutation in the gene coding for ribosomal protein L3, resulting in an Asn149Asp alteration."* |
| **the measurement** | *"Chemical footprinting experiments show a reduced binding of tiamulin to mutant ribosomes."* |

The second is a **negative result that settles the shape**: rRNA mutations were *not*
selected, so the protein is the determinant even though the drug binds the RNA. That is the
in-trans case established experimentally rather than inferred from a definition — round 20's
and round 23's device (an enzyme's *specificity* proven by what it does *not* do), applied
to a determinant's identity.

**And the mechanism sentence hedges the inference itself:**

> *"**It is inferred that** the L3 mutation, which points into the peptidyl transferase
> cleft, causes tiamulin resistance by alteration of the drug-binding site."*

Round 111's shape — the *state of knowledge* qualified, not the value or the magnitude. It
is quoted **with** the hedge, on the same edge as the footprinting result, so the measured
half and the inferred half sit together rather than the inference being smoothed into the
measurement.

The drug-action arm is **PMID:15554968** (Schlünzen 2004), which solved the 50S with
tiamulin bound: *"tiamulin is located within the peptidyl transferase center (PTC) … with
its tricyclic mutilin core positioned in a tight pocket at the A-tRNA binding site"* and
*"Thereby, tiamulin directly inhibits peptide bond formation."*

**A third hedge, in the KB trait itself.** `Pfam:PF00297`'s abstract says L3 *"is known to
bind to the 23S rRNA and **may participate in** the formation of the peptidyltransferase
centre"* — which is precisely the claim the mechanism needs, hedged. Quoted with the hedge.
Three qualifications from three independent sources on one record, all preserved.

## The family split, forced by a rule filed one round earlier

`ARO:3005082` has two records, and they do not say the same thing:

> **ARO:3005081**: *"Thermus thermophilus ribosomal protein **uL3** containing various
> mutations conferring resistance to tiamulin…"*
>
> **ARO:3005082**: *"**Ribosomal protein mutations** that interfere with the rRNA
> conformation at the active site thus conferring antibiotic resistance."*

The parent **names no protein at all.** One config carrying `protein_traits` would assert
the L3 family node on a record that never mentions L3 — which is **#371 exactly**, filed
from round 121's codex escalation hours earlier: *a parent record's claim resting entirely
on its child term's definition.*

So the family gets **two configs**, selected by precondition (`vanR`/`vanS`'s list form,
#208). The named record gets `Pfam:PF00297`; the generic one gets no protein-trait node and
an extra deliberately-weak edge recording *why*:

```
determinant --correlated with (which protein is not stated)--> rrna23s
```

**This is the first time a review finding changed the shape of the next round's work rather
than being fixed and filed.** #371 was two hours old and it decided a modelling question
before the question was noticed.

The precondition reads **only the record's own definition** (#252), and its test drives off
the real records — a hand-written fixture returned `""` from `_own_definition` and would
have tested the parser instead of the predicate.

## Two rpsL records, one clause apart

`ARO:3003419` is the drug-agnostic sibling of round 121's `ARO:3003395`. The first two
sentences are **identical**. The third is not:

| | ending |
|---|---|
| ARO:3003395 | *"…confer **streptomycin** resistance **by disrupting interactions between 16S rRNA and streptomycin**."* |
| ARO:3003419 | *"…confer **antibiotic** resistance."* |

The drug-interaction mechanism is in one and absent from the other. So `ARO:3003419` gets
**no `strep_binding` node and no drug edge at all** — its graph stops at
`determinant --negatively regulates--> rrna16s`, which is as far as its own definition goes.

Round 120 found FrxA and nfsB differing by one clause. This pair differs by **one clause of
one sentence, in otherwise identical text** — and a test pins that the generic config
asserts nothing touching a drug node.

Both records keep the pseudoknot arm at `RO:0002610`, because both make CARD's *"stabilizes"*
claim that PMID:7934937 only hedges as *"has been linked to"* (#363's per-claim stance).

## #370 applied before review found it

Round 121's `drug_binding` states were each defined by one of their two named constituents,
and the codex escalation caught it. This round's `drug_binding` node carries both
`has part → drug0` and `has part → ptc` from the start, with a test.

That is the first time one of these findings was applied **prospectively**. It cost nothing
here; in round 121 it took six review passes to surface.

## Held

`ARO:3000260` (*glycopeptide resistance gene cluster VanL*) is a **gene cluster**, and
whether a cluster should carry a protein-trait causal graph is **#309**'s modelling
question. Curating it would answer that by fiat. Held with a test naming the blocker — the
fourth record now held that way, after kasA (#220), the ESX-5 term (#229) and mshC.

## Provenance

* records touched: **3** (2 uL3 + 1 rpsL) · SEEDED → REVIEWED · 1 held
* `just lint`: **all checks passed**
* `just test`: **745 passed** (+6), **run before the push**
* corpus after: **39,647 records · 40,115 graphs · 350,254 nodes · 372,559 edges ·
  0 errors · 372,559/372,559 edges snippet-cited**
* `just validate` on all 3 individually: **0 failures**
* `--verify`: the split confirmed before any write — the named-L3 config **skips
  ARO:3005082 with its reason**, the generic config takes it, 0 problems on both
* `just audit-fit`: **0** · `just audit-drafts`: 0 accepted-but-unpromoted, **63**
  unconfigured family terms
* canary: `ARO:3003419` promoted alone and verified on disk before the uL3 family ran
* drafts remaining: **193 → 190**

## Open questions

* **`ARO:3005083` is the 23S rRNA record for the same drug**, sitting beside the uL3 records
  in the same directory. It is `determinant_node_type: NUCLEIC_ACID` territory (#215) and
  its graph would be the *other half* of this round's — the drug's actual binding partner,
  curated as a determinant in its own right. That is the natural next round, and it is the
  first rRNA record with a fully curated protein partner to point at.
* **The in-trans shape now has three instances** (rpsL ×2, uL3 ×2). It is worth stating in
  the `edison-causal-graphs` skill before the rRNA set is approached, since every one of
  those records is the same mechanism seen from the other side.
* **#371 changed a modelling decision two hours after being filed.** Worth asking which
  other open findings would change work in progress if they were read at the top of a round
  rather than at review time.
