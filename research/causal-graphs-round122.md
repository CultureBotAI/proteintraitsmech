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
#208). The named record gets `Pfam:PF00297`; the generic one gets **no protein-trait node, no
citation of PF00297's abstract, and none of Bøsling's L3-specific experiments** — the last
two only after review, which found the split withholding the node and not the evidence
(#374). The limitation is recorded on the determinant **node**:

> *"CARD names no specific ribosomal protein on this record. The uL3 identity, its
> `Pfam:PF00297` family node and Bøsling 2003's L3 experiments all belong to the child term
> `ARO:3005081` and are deliberately absent here."*

The first version wrote that as a second, weaker edge on a pair that already had a strong
one — asserting and declining the same relation from the same sentence (#380).

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
`determinant --causally upstream of--> altered_structure`, which is as far as its own
definition goes. (That edge pointed `RO:0002212` straight at the rRNA molecule until review
noted the predicate needs a *process* and a *decrease*, and CARD claims neither — #377.)

Round 120 found FrxA and nfsB differing by one clause. This pair differs by **one clause of
one sentence, in otherwise identical text** — and a test pins that the generic config
asserts nothing touching a drug node.

Both records keep the pseudoknot arm at `RO:0002610`, because both make CARD's *"stabilizes"*
claim that PMID:7934937 only hedges as *"has been linked to"* (#363's per-claim stance).

## #370 applied before review found it

Round 121's `drug_binding` states were each defined by one of their two named constituents,
and the codex escalation caught it. This round's `drug_binding` node carries both
`has part → drug0` and `has part → ptc` from the start, with a test.

That is the first time one of these findings was applied **prospectively**. But the test was
weaker than the property: it read the config, and emission silently drops edges whose
`requires` is unmet — and only the drug half was guarded. So the exact one-sided state #370
is about could still have been emitted, with #370's own test green (#378). Both halves now
carry the same guard and the test reads the emitted records.

**Applying a finding prospectively is not the same as pinning it**, and this round proved it
on the very finding it was applying.

## Held

`ARO:3000260` (*glycopeptide resistance gene cluster VanL*) is a **gene cluster**, and
whether a cluster should carry a protein-trait causal graph is **#309**'s modelling
question. Curating it would answer that by fiat. Held with a test naming the blocker — the
fourth record now held that way, after kasA (#220), the ESX-5 term (#229) and mshC.

## Provenance

* records touched: **3** (2 uL3 + 1 rpsL) · SEEDED → REVIEWED · 1 held
* `just lint`: **all checks passed**
* `just test`: **745 passed** (+6), **run before the push**
* corpus after: **39,647 records · 40,115 graphs · 350,259 nodes · 372,563 edges ·
  0 errors · 372,563/372,563 edges snippet-cited**
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

## What the review found: nine findings, and the headline claim was not in the deliverable

All nine filed (#373–#381), all nine fixed. Three matter beyond their instance.

**1. The round's headline finding was in the report and in no record (#375).** This report's
own table calls PMID:12936991's negative result — *"No mutations in the rRNA were selected as
resistance determinants"* — *"a negative result that settles the shape … established
experimentally rather than inferred"*, and the commit message opened with it.

**The constant was defined and never referenced.** `_TIAMULIN_NOT_RRNA` and
`_TIAMULIN_MUTANT` appeared in no edge on any of the three records. Nothing catches an unused
module-level constant — ruff does not flag them, and #367 filed exactly this failure one
round earlier, on a different constant, for a different reason.

So: **twice in two rounds, the sentence a round was built around went missing from the round's
output, and both times only a reviewer reading the artifact found it.** That is not a slip; it
is what happens when the report is written from the config and the config is not read back.

**2. The split withheld the node and not the evidence (#374).** The two-config split existed
to keep uL3's identity off a record that names no protein — #371, applied prospectively and
described above as this round's best move. It withheld `Pfam:PF00297` and then handed the
generic record Bøsling's **L3 Asn149Asp footprinting result** as the sole support for its
causal core.

The rule was satisfied for one node type and violated for the evidence. And when the fix was
written, the *same defect reappeared one edge over* — the new `rrna23s part_of subunit50s`
edge cited `Pfam:PF00297`'s abstract on both configs, and it was **the test written for #374
that caught it**, not another review round.

**3. `RO:0002212` was pointed at molecules on three records (#377).** The predicate requires a
**process** object and a **decrease**: *"p decreases the rate or magnitude of execution of q"*.
CARD says the mutations *"interfere with the rRNA conformation"* — altering a shape is not
decreasing an execution, and the rRNA's function is emphatically not reduced, since resistant
ribosomes still translate. That is the mechanism.

**This regressed from round 121**, which pointed the same predicate at a STATE and never at a
molecule. Both records now route through an explicit `altered_conformation` /
`altered_structure` STATE node, which is also more honest: the altered conformation is a thing
the graph can say the drug binds less well.

Also fixed: a `part of` edge whose snippet located the *drug*, not the PTC's composition
(#373); a `peptide_bond` node grounded to `translational elongation` two lines below a comment
invoking the rule against exactly that (#376); an asymmetric `requires` guard that could emit
a one-sided binding state with #370's own test still green (#378); held-record tests that pass
for any nonexistent ARO id (#379); a weak edge that asserted and declined the same relation
from the same sentence (#380); and a config key the promoter silently ignored, which recorded
the limitation nowhere — `determinant_note` is now real (#380).

**4. `--repromote` would have silently downgraded round 121's work (#381).** `ARO:3003395` is
a descendant of `ARO:3003419`, and this round's generic config is **by design strictly weaker**
than round 121's drug-specific one. A routine `--family ARO:3003419 --repromote --apply` would
have replaced the streptomycin graph with the drug-free one, and **#280's blast-radius guard
cannot fire**: it refuses above `max(25, 5 × n_draft)`, and this family has two records.

235 ancestor/descendant config pairs exist in this codebase. This is the first where the
ancestor is deliberately weaker, which turns a rewrite into data loss. The precondition now
refuses ARO:3003395 by name, with the reason.

## Provenance after review

* review findings: **9** · filed: **9** (#373–#381) · fixed in this PR: **9**
* `just lint`: passed · `just test`: **745 passed**, run before the push and after the fixes
* corpus after: **350,259 nodes · 372,563 edges · 0 errors · 372,563/372,563 snippet-cited**
* `--verify` after the fixes: both refusals fire with their reasons — the named-L3 config
  skips ARO:3005082 (#371), and the generic rpsL config skips ARO:3003395 (#381)
* records re-promoted from clean drafts after every config change, never patched in place

## Review round 2: the fix that removed one of five, and the test that could not see the other four

Five findings, all filed (#382–#386), all fixed. The first is the round's real lesson.

**#374 was not fixed.** The fix removed `_TIAMULIN_FOOTPRINT` from the generic config's
`det_res` — **one of five uses.** `_TIAMULIN_INFERRED` and `_TIAMULIN_FOOTPRINT` remained in
`_ul3_shared`'s `extra_edges`, unconditional, so `ARO:3005082` still carried

> *"It is inferred that **the L3 mutation**, which points into the peptidyl transferase
> cleft, causes tiamulin resistance…"*

as the **sole support for its causal core** — on the record whose entire reason for existing
as a separate config is that it names no protein.

**And the same commit added a determinant-node description asserting the opposite:**
*"Bøsling 2003's L3 experiments … are deliberately absent here."* PMID:12936991 appeared five
times in that record. **The record contradicted itself**, and the paragraph above in this
report repeated the false claim.

**The regression test could not catch it.** It asserted
`"PMID:12936991" not in repr(unnamed["det_res"])` — scoped to the one place the fix had
touched. The four surviving citations were in `extra_edges`, which the assertion never read,
while the neighbouring `Pfam:PF00297` assertion *in the same test* correctly walked both.

That is the shape: **a fix and its test written in one motion share one blind spot.** Round
121's round-2 finding was that fixes inherit the frame of what they fix; this is the same
thing one level down — the test inherits the frame of the fix.

The corrected assertion also had to be **weakened to be right**: a reference-level ban on
PMID:12936991 fails, because that paper also states what the *drug* does (*"tiamulin targets
the 50S subunit and interacts at the peptidyl transferase center"*), which is true of any
member. The constraint belongs on **snippets that carry the L3-specific result**, and it is
now written that way, naming each of the four.

**Two more predicates were wrong for their claims.** The `rrna23s part_of subunit50s` edge —
written to *replace* the one #373 removed — repeated #373's defect: its snippet says the
structure gives *"a detailed picture of **its** interactions with the 23S rRNA"*, where "its"
is tiamulin's. Co-mention in one sentence is not part-hood. **The edge is gone; no snippet
supports it** (#383). And `altered_conformation --part of--> rrna23s` used `BFO:0000050` for a
conformation, which **inheres in** a molecule rather than being a part of one — the snippets'
genitive (*"the higher-order structure **of** 16S rRNA"*) is the inherence reading. Now
`RO:0000052 characteristic of` (#384).

**A node justified its own typing with a rule its graph breaks twice** (#385): *"RO:0002212
requires a PROCESS object and a DECREASE"* — while the same graph points RO:0002212 at
`drug_binding`, a STATE, twice. The typing decision was right; the stated reason was wrong.
The real objection was to the **molecule** as object, not to non-process objects, and round
121's merged ARO:3003395 already establishes STATE objects as the convention.

## Provenance after two review rounds

| round | findings | filed | fixed |
|---|--:|--:|--:|
| 1 | 9 | 9 (#373–#381) | 9 |
| 2 | 5 | 5 (#382–#386) | 5 |

* `just lint`: passed · `just test`: **745 passed**, run before the push and after each fix
* corpus: **350,259 nodes · 372,563 edges · 0 errors · 372,563/372,563 snippet-cited**
* verified directly on the emitted record: **no snippet naming L3 appears on ARO:3005082**
* records re-promoted from clean drafts after every config change, never patched in place
