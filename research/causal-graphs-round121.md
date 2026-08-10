---
topic: causal-graphs
round: 121
date: 2026-08-10
target: aro/FUNC_RESISTANCE — rpsA (ARO:3004722), rpsL (ARO:3003395), rpsE (ARO:3007526), 5 records
prior_round: causal-graphs-round120.md
---

# Causal graphs — Round 121: three ribosomal proteins, three different graphs, and the round three groundings I remembered turned out to be wrong

Round 120 found that FrxA and nfsB — two nitroreductases — differ by one edge because of
one clause. This round is that finding at family scale: **three small-subunit ribosomal
proteins, all `ARO:3000212`, all target-alteration in the loose sense, and three graphs
that share almost nothing**, because their CARD definitions differ in exactly the place
that decides how much may be asserted.

| family | records | what CARD gives | graph |
|---|--:|---|--:|
| **rpsA** (ARO:3004722) | 2 | activation, binding, the process inhibited, **and that the function is kept** | 8 extra edges |
| **rpsL** (ARO:3003395) | 1 | a mechanism its **own source only hedges** | 5 extra edges |
| **rpsE** (ARO:3007526) | 2 | *"is associated with"*, and **no mechanism at all** | 5 extra edges |

A single shared config was the obvious shortcut and would have written rpsA's binding
mechanism onto rpsE, which CARD does not support for it. A test pins that the three configs have three
different references AND three different edge shapes, and that rpsA's `poa`,
`rpsa_wt` and `trans_translation` nodes appear nowhere in rpsE's config.

## rpsA — the first record whose definition rules a mechanism *out*

Every clause of CARD's two rpsA records is a sentence of **Shi et al., Science 2011
(PMID:21835980)**, which is the paper that identified the target:

| claim | verbatim |
|---|---|
| activation | *"PZA is hydrolyzed intracellularly to pyrazinoic acid (POA) by pyrazinamidase (PZase, encoded by pncA)…"* |
| the target | *"we identify a previously unknown target of POA as the ribosomal protein S1 (RpsA), a vital protein involved in protein translation and the ribosome-sparing process of trans-translation."* |
| **binding and its loss, one sentence** | *"we confirmed that POA bound to RpsA (but not a clinically identified ΔAla mutant) and subsequently inhibited trans-translation rather than canonical translation."* |
| why RpsA is the determinant | *"Three PZA-resistant clinical isolates without pncA mutation harbored RpsA mutations."* |

That third sentence carries **both arms** — the drug's normal binding, and the resistant
mutant's failure to bind — which is why the whole sentence is quoted on both edges rather
than paraphrased once. Round 21's vanH affinity quote had the same shape.

**The new qualification kind.** Every source qualification catalogued so far weakens a
claim: a value hedged (63), a claim attributed (97), a magnitude (92), the state of
knowledge (111), a genetic precondition (107), a direction unspecified (115), a function
assignment itself uncertain (117). This one **rules a different mechanism out**:

> ARO:3004721: *"Mutations … can confer resistance to pyrazinamide **maintaining rpsA
> function**."*
>
> Shi 2011: *"inhibited trans-translation **rather than canonical translation**."*

Two independent statements that nothing is lost. So the graph asserts
`determinant --enables--> trans-translation` and **never** a negative edge from the
determinant onto it — only POA gets one. A test pins the presence of the positive edge and
the absence of the negative, because a reader who knows that ribosomal mutations usually
cost fitness would otherwise read the omission as an oversight.

**rpsA has no domain node**, which is the second finding.

## Three groundings I remembered, and all three were wrong

#157 established that every CURIE is checked non-obsolete before use. This round is the
argument that the check is necessary and **not sufficient**.

| recalled as | actually | how it was caught |
|---|---|---|
| `CHEBI:45001` — pyrazinoic acid | **obsolete**, and never was pyrazinoic acid | the #157 check |
| `SO:0000407` — 16S rRNA | `cytosolic_18S_rRNA` | reading the label |
| `SO:0005836` — pseudoknot | `regulatory_region` | reading the label |

The first is the interesting one. Having been told a CURIE is obsolete, the obvious repair
is to follow the term's own `term_replaced_by`. OLS gives:

```
CHEBI:45001  obsolete=True  term_replaced_by: CHEBI_225237
CHEBI:225237 obsolete=False  2-phenylethanaminium
```

**2-phenylethanaminium is not pyrazinoic acid.** The recalled CURIE was simply wrong, the
term happened to be obsolete for unrelated reasons, and its successor is a different
chemical. Substituting it would have produced a **live, current, false** grounding — which
is strictly harder to find than a dead one, because the gate goes quiet. Filed as **#346**.

The right grounding, found by searching ChEBI for the *name*: **CHEBI:71311**
(`pyrazine-2-carboxylic acid`). The two SO nodes were left **ungrounded** rather than
guessed, and each node's `description` says which CURIE was rejected and why.

## The Pfam record whose label and definition describe different domains

rpsA's natural protein-trait node is `Pfam:PF00575`, *"S1 RNA binding domain"* — a real KB
record, correct label, and InterPro does integrate PF00575 into **IPR003029** of that name.

Its KB definition reads:

> *"This domain is found in uncharacterised proteins mainly from Alveolata lineage…"*
> — `definition_source: InterPro:IPR059328`

**IPR059328 is `Domain of unknown function DUF8284`.** The record's prose is a different
entry's abstract.

Round 21's rule decides it: the weaker-looking node with real evidence beats the
better-looking node with borrowed evidence — and here the borrowed evidence is not merely
about a superset, it is about something else. **rpsA gets no domain node**, and a test
asserts `PF00575` appears nowhere in its config.

Then the corpus-wide version, measured rather than assumed. A deterministic 58-record
spread over the 16,201 Pfam records, each checked against InterPro's own
`metadata.integrated`:

```
sampled 58  matching=57  MISMATCHED=1  api_errors=0
    PF22273  claims IPR055682  actually IPR054231
```

**One mismatch in 58 is one observation, and the review was right that it will not carry
an extrapolation.** PF00575 cannot join the numerator — it was found by targeted
inspection, not drawn in the sample — and a single hit at n=58 gives a 95% interval of
roughly **0.04%–9%**, i.e. anywhere from ~7 to ~1,500 of 16,201 records. The honest
statement is: **at least two records are confirmed wrong, and the rate is unknown.**
Filed as **#344**, which needs the full 16,201-call check, not a better estimate.

It matters beyond cosmetics because these
definitions are *cited as evidence snippets*: the label looks right, the CURIE is right,
and only the prose is another domain's — which defeats the #196 check that a domain's
abstract must mention the protein.

## rpsL — curated at its source's strength, not CARD's

CARD asserts a mechanism:

> *"Ribosomal protein S12 **stabilizes** the highly conserved pseudoknot structure formed
> by 16S rRNA. … confer streptomycin resistance **by disrupting interactions between 16S
> rRNA and streptomycin**."*

**PMID:7934937** (Finken 1993) is the paper that definition is built from. It says:

> *"The 16S rRNA region mutated perturbs a pseudoknot structure in a region which **has
> been linked to** ribosomal S12 protein."*

A hedged linkage, and no stabilisation experiment. So the edge is
`determinant --correlated with [RO:0002610]--> pseudoknot`, not a causal or regulatory
predicate — and it carries **both** references, so the disagreement is visible on the edge
rather than only in this report. A test pins the predicate and the two-reference set.

This is round 51's lesson pointed the other way. Round 51: *don't source a mechanism the
record doesn't claim.* Round 121: **when the record claims more than its own source, follow
the source.** Both are the same discipline — read what is actually asserted, by whom.

The mechanism shape is also new: **target alteration in trans.** The determinant is a
protein, but the drug's binding partner CARD names is the *16S rRNA*. The mutation does not
change the drug's binding site; it changes the conformation of the molecule that is one.

`det_res` cites **PMID:8665467** for the association, and the magnitude is part of the
claim: *"Streptomycin resistance in **about one-half** of M. tuberculosis isolates…"* — the
other half is the *rrs* route, which is not this record.

## rpsE — an association, and the edge shape that cannot say so

CARD gives two structural facts and refuses to join them to anything:

> *"Amino acid substitutions in ribosomal protein S5 … **is associated with** resistance to
> spectinomycin (SpcR). This protein is located on the 30S subunit and interacts with 16S
> rRNA and other proteins."*

So the graph asserts the structure (`part of` the 30S subunit, `molecularly interacts with`
16S rRNA), the drug's action on the 30S from Carter 2000, and
`determinant --correlated with--> resistance`. **No mechanism edge joins the substitution
to the drug** — the promoter's fixed `confers resistance to (drug class)` edge is still
emitted, carrying CARD's own assertion.

That distinction is the review's, not mine. The first version of this round said flatly
"no edge connects the substitution to the drug", and the test that pinned it read the
config's `extra_edges` — a subset that by construction can never hold the fixed edge. **The
test passed vacuously while the sentence it defended was false of the artifact.** It now
loads the emitted YAML and asserts what is actually there: exactly one edge to a drug node,
and it is `ARO:2000001`.

**The promoter cannot express this, and that is a defect.** `promoted_graph_dict` always
emits `determinant --causally upstream of (confers resistance)--> resistance`. The record
is therefore honest in its notes and overclaiming in its predicate — the same defect class
as #306, where deliberate omissions live in prose no gate can see. Filed as **#345** with a
suggested `det_res_pred` override.

**The Neisseria modelling paper is context, not evidence.** PMID:42450237 models RpsE loop-2
substitutions against the spectinomycin site and carries **three qualifications at once**:
it is *modelling*, it is *hedged* (*"potentially altering the architecture"*), and it is
*Neisseria*, whereas these records are *B. subtilis* and unspecified. It rides on an edge
CARD already supports and licenses none of its own; a test asserts it is never an edge's
sole evidence.

## Held, with a test

`ARO:3004989` (*pyrazinamide resistant Rv3008*):

> *"A hypothetical protein for which it has been **predicted** but **no experimental
> evidence exists** to determine its function. **May** contribute to pyrazinamide
> resistance."*

Round 117's *"putative"* shape doubled: the function assignment is uncertain **and** the
resistance contribution is uncertain. There is no claim left to assert, so nothing is
asserted — and the test says why, so it does not read as an oversight.

## Provenance

* records touched: **5** (2 rpsA + 1 rpsL + 2 rpsE) · SEEDED → REVIEWED · 1 held
* `just test`: **737 passed** (+10), **run before the push**
* corpus after: **39,647 records · 40,115 graphs · 350,242 nodes · 372,536 edges ·
  0 errors · 372,536/372,536 edges snippet-cited**
* `just validate` on all 5 individually: **0 failures**
* `--verify` on all three families: **9 KB CURIEs checked, 0 precondition skips,
  0 uncovered mechanisms, 0 problems**
* `just audit-fit`: **0** curated records accepted by no config
* `just audit-drafts`: 0 accepted-but-unpromoted · **64 unconfigured family terms** remain
* canary: rpsL promoted alone and verified on disk (status flipped, 12 snippets, validates)
  before the other two families were run
* drafts remaining: **198 → 193**

## Open questions

* **#344 needs a script, not a spot fix.** 275–550 Pfam definitions are estimated wrong and
  the estimate comes from 58 API calls; the real check is 16,201. Until it runs, any domain
  node taken from a Pfam record should have its definition read, not just its label.
* **#345 is the fourth time the fixed edge shape has been the constraint** (after #208's
  one-config-per-family, #215's PROTEIN node type, #188's dangling endpoints). Each was
  solved by making one hard-coded thing configurable. `det_res_pred` is the same move.
* **The three-wrong-recalls rate is the argument for a rule, not a habit.** Every grounding
  written from memory this round was wrong. The ones that reached a gate were caught; the
  ones that did not were caught only by reading a label. A grounding should be confirmed by
  **label match**, always.
* **64 unconfigured family terms remain** in the ARO set, plus the decision-bound blocks
  (#309's 28, #229's 22, #215's 10).

## What the adversarial review found, and what it cost

Twelve findings, nine filed (#348–#356). Seven were fixed in the same PR. Three are worth
recording here because they are defect *classes*, not slips:

**1. A snippet under the wrong reference (#348).** `mech_res` and `res_drug` are attributed
by the promoter to `cfg["reference"]`. rpsL's `reference` is PMID:7934937, but the sentence
placed there was Musser's (PMID:8665467) — so one sentence was attributed to two papers in
one record, and one of those attributions was false. The config *also* cited it correctly on
`det_res`, which is what made it invisible: the right citation was present, just not on
every edge carrying the text. There is now a test asserting Musser's sentence appears only
where Musser is named — and **that test immediately failed**, because one of the three
fixes had silently not applied.

**2. A graph that asserted the negation of its own snippet (#349).** The rpsA config had
`poa --molecularly interacts with--> determinant`, evidenced by *"POA bound to RpsA (but not
a clinically identified ΔAla mutant)"*. But `determinant` is grounded to ARO:3004722,
**"pyrazinamide-resistant rpsA"** — the very variant the parenthesis excludes. Ten lines
later the same graph said that determinant abolishes POA binding. Both edges cited the same
sentence; one of them read it backwards.

The fix is a `rpsa_wt` node for the drug-sensitive protein, so the drug-action arm and the
resistance arm attach to different things. **This is a shape problem, not a typo**: the
determinant node in every ARO resistance record denotes the *resistant* allele, so any
drug-action edge pointed at it is suspect. The other configs escaped it by hanging the drug
off a sub-part; this one was the first to point it at the determinant directly.

**3. Three tests weaker than they read (#350).** Beyond the vacuous rpsE test: a
`for banned in (...)` loop that could never fail, because the line above it had already
asserted the id equals a value in none of them; and `counts[0] < counts[-1]` over sorted
sizes, which only rules out all three configs being identical — two could be byte-identical
and it passes. Both now assert content.

The pattern across all three: **the check was written from the same understanding as the
thing checked.** A test written straight after a config tends to encode the author's belief
about the config rather than an independent property of it. That is the argument for the
review being a separate adversarial pass rather than a re-read, and it is why the round-39
rule — gate before the push, separately — has a sibling: *have someone else try to break the
claim.*

## Provenance after review

* review findings: **12 + 6 + 5** across three rounds · issues filed: **17** (#348–#364) ·
  fixed in this PR: **16**
* left filed: **#355** (two `poa` node treatments across rounds 56 and 121),
  **#356** (promotion drops the auto-draft's `participates_in` caveat, ~7,200 records),
  **#364** (194 self-referential `is_a` ancestor notes, a promoter template defect)
* `just test`: **737 passed** (+10), run before the push and again after each fix round
* all three families re-promoted from clean drafts after each config change, never patched
  in place

## Review round 2: what the fixes got wrong

Six more findings, all filed (#357–#362), all six fixed. Two are worth recording.

**The #349 fix relocated the contradiction rather than removing it.** Adding `rpsa_wt`
stopped the graph asserting that POA both binds and does not bind the determinant. But
nothing then related the two nodes, so a consumer saw **two unrelated proteins both
enabling trans-translation**, with `poa_rpsa --has part--> rpsa_wt` sitting beside
`determinant --negatively regulates--> poa_rpsa`.

The honest fix wanted an allelic-variant predicate, and **RO has none**. Searched:
`RO:0002312` is *"evolutionary variant of"* — about evolution, not alleles; `RO:0001000`
*"derives from"*, `RO:0002156` *"derived by descent from"* and the allelopathy terms all
mean something else. So the relation is stated in both nodes' `description`, with the
absence of the edge and its reason written there, and a test asserts the description says
it. **Forcing `RO:0002312` would have been this round's own #346 mistake** — a live,
correct-looking CURIE that means the wrong thing.

This will recur. **Every ARO determinant node denotes a resistant allele**, while most
drug-action arms are about the sensitive form. Filed as **#357**; it wants a convention,
not a per-round decision.

**The #352 fix was right about the defect and wrong about the remedy.** `PF03719` really
was mis-typed — `protein_traits["fold"]` emits *"member of (adopts fold)"* for what is a
C-terminal **domain**. But the fix dropped the node entirely, on the stated ground that
"the shape offers no second part slot" — and `extra_nodes` sits four lines below that
comment, which is exactly the slot, and which the same config already uses for
`subunit30s`. A real KB-trait link was deleted for a reason that was not true, and the
false reason was then baked into a passing test's docstring. PF03719 is back as a
correctly-typed `DOMAIN` node with a `part of` edge (**#358**).

The pattern across both: **a fix written under time pressure inherits the mistaken frame
of the thing it fixes.** Round 1 caught tests that encoded the author's belief about a
config rather than a property of it; round 2 caught fixes that encoded the author's belief
about what the shape allowed. Two review rounds found different classes of defect, which is
the argument for running more than one.

## Review round 3: the fix that was never checked against its own siblings

Five findings, two filed (#363, #364), three corrections to the report's own numbers.

**#354 was fixed on rpsA and left standing on rpsL.** rpsA's conferral edge had cited a
co-occurrence; the remedy was to let CARD, which makes the causal claim, carry the edge.
Round 3 found rpsL's conferral edge citing

> *"Streptomycin resistance in about one-half of M. tuberculosis isolates **is associated
> with** missense mutations in the rpsL gene…"*

— the same defect, the same round, the same file, **and the same remedy already sitting
unused in the config**: `_CARD_RPSL` says *"…**confer** streptomycin resistance by
disrupting interactions…"* and was already cited on three other edges.

Nothing prompted the check. Fixing a finding on the family it was reported against is the
natural move, and it is not the same as fixing the defect.

**And the fix collided with an earlier fix.** Moving CARD's sentence onto `mech_res` would
have put CARD's text under `reference: PMID:7934937` — **re-creating #348 in the act of
fixing #363.** Both are resolved by making `reference` the CARD term, as rpsE already does,
and citing PMID:7934937 explicitly on the two edges whose claims it actually makes.

Three findings collide on that one field, which is why the test now names all three and
asserts the string **literally** rather than `== the_constant` (#360's residual gap: an
identity check against a constant passes for any value the constant is edited to).

## Where three rounds of review left this

| round | findings | filed | fixed here |
|---|--:|--:|--:|
| 1 | 12 | 9 (#348–#356) | 7 |
| 2 | 6 | 6 (#357–#362) | 6 |
| 3 | 5 | 2 (#363–#364) | 3 + 2 report corrections |

**Each round found a different class.** Round 1: claims not supported by their snippets.
Round 2: fixes that inherited the mistaken frame of what they fixed. Round 3: a fix applied
to one family and not its siblings, and a fix that collided with an earlier one.

The rate is not falling because the work is getting worse — it is falling because each
round can only see the artifact the previous round produced. Three rounds is not obviously
enough; it is where the returns visibly narrowed, from correctness to bookkeeping.
