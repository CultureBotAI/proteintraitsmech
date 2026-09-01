# NEXT_TASKS

Durable backlog of deferred / next work for ProteinTraitsMech. **Maintenance
convention:** update an item when work on it starts or ships (mark
`DONE (YYYY-MM-DD, PR #NN)` or move it out); add any new work thread as its own
section with enough context to pick it up cold; keep absolute dates. Reconcile
against merged PRs + `git log` before trusting it.

_Last reconciled: **2026-09-01**, against `main` at `51a54b00c30` + PRs #556–#621. The
2026-08-22 reconcile (PR #559) covered #514–#555; **24 PRs have merged since** and are
logged in "The grounding and gate-hardening thread" below. The prior reconcile's own
lesson repeated once more: its "Still open from this thread" list named four open PRs and
a table of open issues, and **ten of those issues are now closed** — #515, #516, #521,
#532, #534, #536, #538, #540, #541, #543. A reconcile is current only on the day it is
written._

_**Corpus size: 429,271 records** (re-measured 2026-09-01 via `just corpus-stats`;
unchanged since 2026-08-22 — the 2026-08-31 grounding thread added canonical examples to
127 existing records rather than new records). Every "424,467" below is a point-in-time
figure from an older round; run `just corpus-stats` rather than trusting one._

_**`NEXT_TASKS_LOOP.md` is stale** — last reconciled 2026-08-04, 18 days ago, and its own
header says the ranking "should be re-derived rather than trusted if much has merged
since". **197 PRs have merged since** (2026-08-04 through 2026-08-22; 08-07 and
08-08 alone merged 106). Do not read it as current._

## ⚠️ ARO draft backlog — measured 2026-08-10, superseding the figures further down

Rounds 121–123 kept being handed a summary of "what is left" whose every number was wrong.
Measured directly against the corpus (classify each draft by its own `definition` via
`_own_definition`, plus its label):

| the old note says | measured | |
|---|--:|---|
| katG/ahpC/fabG1/ethA **~40** | **17** | fabG1 was curated in round 51 |
| 16S/23S rRNA **~22** (elsewhere "105") | **0** | no draft matches an rRNA pattern |
| **565** label-only efflux/regulator | **27** | 16 efflux + 11 regulator |
| van set "last ~30 operon-level" | **33** cluster/operon | the only claim that held |

**7,211 curated · 188 drafts remaining**, in these buckets:

| n | bucket | decision or effort? |
|--:|---|---|
| 63 | short definition (<120 chars) | **effort** — `_minimal_enzyme_config` shape (rounds 66, 104, 105, 120) |
| 49 | other, long definition | **effort** |
| 33 | cluster / operon | **decision** — #309 |
| 15 | prodrug activation | **effort** — 17 before round 123 took `nat` |
| 16 | efflux | effort |
| 11 | regulator | effort |
| 1 | van, non-cluster | effort |

**~150 of 188 are effort, not decision** — the opposite of the standing framing.

### The three issues named as decision-blockers, measured

| issue | claimed | measured |
|---|---|---|
| **#203** | 1,044-record backlog | **0** — cleared by routine re-promotions after #201 closed the code path. No migration was ever run. |
| **#196** | backlog wanting a policy | **1**, and arguably a pass. Wants a `just audit-part-of` recipe, not a policy. |
| **#204** | needs a `CurationEvent` schema slot | ~~**confirmed open and genuinely decision-bound.**~~ **DONE (2026-08-20, PR #497.)** The fingerprint machinery now exists: promoter events carry `emitted_hash` **and** `emitted_for`, so the guard answers "did I write this, for *this* family" rather than the purely structural `is_ours`. Measured on merge: the ownership guard fires **0** times today — all 1,346 refusals come from the legacy `existing == graph` fallback, and the only difference in those 1,346 is the graph `description` (nodes, edges, references and snippets are identical). Follow-ups #498, #499, #501 are open. |

**Decision-bound: ~~#204, and~~ #309's 33 cluster/operon drafts. That is all of it** — #204
shipped, so #309 is now the whole decision-bound set.

The curated count was **re-measured at the merge tip**: 7,452 ARO files = 7,211 curated +
188 drafts + 53 carrying no causal graph at all. #392 said 7,262, which counted those 53 as
curated and used a mid-stack draft number — the one figure in this correction that had not
itself been re-measured (#407).

Full survey and reasoning: **#392**. Per-issue measurements are commented on #196, #203, #204.

_**Loop-ready work now lives in `NEXT_TASKS_LOOP.md`**, which ranks the open issues an
unattended `/goal` run can finish and says which need a human first. This file remains the
durable backlog: the long threads, the context, and what has shipped._

---

## The infrastructure and gates thread (2026-08-13 → 2026-08-22) — _superseded 2026-09-01; see the grounding and gate-hardening thread below_

**None of this was in this file until 2026-08-22.** **32 PRs merged in twelve days** — 33
between 2026-08-13 and 2026-08-22, less #561, which landed after this reconcile was written
— and the backlog recorded none of them, because the 2026-08-10 reconcile scoped itself to
ARO. The thread has one subject: **a gate nobody runs is indistinguishable from one that
passes**, and nearly every item below is a case of that.

The "Shipped" list below names **26** of those 32. The other six are recorded nowhere in
this section; they are logged here rather than dropped (#566 tracks the same failure in the
source table, this one is #565): **#420** and **#421** (identity-gate exit code, and a red
`main` where the `--update-baseline` guard banned its own test), **#487** (provider-triage
deep research), **#502** (the `fetch-source` skill), **#507** (parity doc: the claw
dependency decision does not exist), and **#525** (`check_vendored_sync.sh` curl hardening).
_A reconcile section that itself drops 19% of the window is the thesis restated: reconciling
is not self-verifying._

**Shipped.** Snippet backlog closed at 0 with an identity baseline, not just a ceiling
(#422/#425/#426, PRs #423/#427/#429/#431) · Pfam and InterPro definitions taken from the
entry that *integrates* them and from the API where the release ships no abstract
(#344/#445, PRs #444/#454) · records compared against the equivalence overlay they were
built from (#447, PR #453) · a term is no longer its own `is_a` ancestor (#364, PR #461) ·
records measured against the config that claims them (#408, PR #465) · five tests stopped
reading a gitignored release (#469, PR #470) · **`--force` re-seed no longer reverts 27,784
enriched definitions** (#455, PR #472) · repair scripts' finders made broader than their
fixers (#462, PR #477) · 4,664 serine-hydrolysis notes restored (#466, PR #486) ·
**`validate-all` made truly closed-schema and gated in CI** (#485, PR #488) · the shared
Mech curation foundation adopted, byte-identical from the hub (#484, PR #495) ·
re-promotion refuses to overwrite a graph it did not write (#204, PR #497) · the id-label
surface measured before gating it, then gated (#493, PRs #504/#554) · **who may write a
trait record, and by what route** — `just audit-writers` (#492, PR #509) · the schema
probes the justfile had claimed for the life of the repo (#496, PR #511) · deep-research
provider brought to hub parity (PR #514) · corpus statistics generated instead of
hard-coded, agent guidance made durable (#518, PR #527) · Pages budgets and filter-aware
sharding (#519, PR #529) · centralized atomic source downloads (#522, PR #530) · the fleet
provider contract and canonical sync pin (PR #553) · an atomic validated-write path for
trait editors (PR #555).

**Still open from this thread, and this is where the work is.** Four PRs from the batch
were still open on 2026-08-22: **#523** (#515, mech_shared validation scope), **#524**
(#516, single-record validation closed-mode), **#526** (#457, repeated full-corpus test
scans), **#528** (#521, source/seeder registry roles). _All four merged 2026-08-26; #515,
#516, #457 and #521 are closed (2026-09-01)._

The 2026-08-21 adversarial review of the seven-PR batch filed **#531–#545**; #546–#552 and
#558 came from the reviews of #553/#555. Grouped by what they actually are:

| group | issues | what they have in common |
|---|---|---|
| **A gate passes without reading anything** | ~~#534~~, ~~#540~~ — **both closed 2026-08-26** | `just audit-schema` reported "schema is internally coherent" having read **zero** records; `just validate` exited 0 on a **mistyped path**. Fixed in PRs #526 and #524: reading zero records now fails unless `--allow-empty-corpus`, and wholly-missing paths exit 2 unless `--allow-missing`. The class recurred twice more since and was caught both times — #616 (the new grounding gate failed a deletion-only diff, where the strict step beside it passed) and #622. |
| **Licensing / registry** | **#542**, #521, #517 | 353 ELM records from a source `download.yaml` marks `rejected`. See the ELM block above. |
| **New rules with no test that would catch their recurrence** | ~~#536~~, ~~#543~~ (closed) · open: #544, #545, #539 | measured by mutation: **12 of 12** mutations survive #528's registry rules; #529's cross-shard completeness is *provably* correct (400 random filter combinations, 0 under-fetch) but a `.some()`→`.every()` mutation leaves all 6 tests green; #523's parametrize iterates the constant it checks. |
| **CI reliability** | **#558**, #500, #537 | order-dependent test pollution (`write_validated_record` ImportError only under a full-suite run); tests share `reports/instance_validation_failures.tsv`; `uv.lock` is not a validation-scope input, so a linkml bump can skip corpus validation. |
| **Residuals and stale claims** | open: #531, #533, #535 · ~~#532, #538, #541~~ (closed 2026-08-26) · ~~#546–#552, all seven closed~~ | including this file's own genre of defect: #531 was filed with the wrong counts (17/32) and corrected to **11 of 40 recipes migrated, 23 still on bare curl** — and its title still carries the wrong figures. The #546–#552 block closed between 2026-08-21 and 2026-08-26; listing issue numbers in a defect table reads as open work, so they are struck rather than deleted (#567). |

**Both skill PRs have since merged** (#557 on 2026-08-23, #556 on 2026-08-27), and
`review-open-issues` was re-adapted twice more — from MicroGrowLink v1.1.0 (#572) and
CultureMech v2.0.0 (#596). _The paragraph below is kept as written, dated, because it is
the example the sentence after it is making._

**One of the two skill PRs has merged.** Both add a row at the same anchor in `CLAUDE.md`'s
task-to-skill router, so the second to merge takes a one-line conflict. **#557**
(`review-open-issues`, whole-queue triage) **merged 2026-08-23**, which leaves **#556**
(`next-tasks`, the skill that maintains *this* file) open and holding that conflict. Neither
touches `NEXT_TASKS.md`. _State as of 2026-08-26 (#568): the original sentence here was false
within 24 hours of being written, which is why live PR state carries a date in this file and
historical claims ("were still open on 2026-08-22") do not need one._

---

## The grounding and gate-hardening thread (2026-08-23 → 2026-09-01) — **the active thread**

**24 PRs merged since the 2026-08-22 reconcile** and none were logged here until now. Two
subjects, and the second is the more transferable.

### 1. The UniProt organism/protein grounding thread landed (#605, PR #608)

**222 files that had lived only in a working tree since 2026-08-18** — 147 modified, 73
untracked, no backup, on a branch (`docs/reconcile-next-tasks-2026-08-22`) whose own
committed content had already merged as #559. Preserved verbatim first in three commits,
then reconciled with `main` across 9 conflicts, then landed as **212 files / 79,123
insertions**.

What it adds: 31 scripts and 33 test modules for the candidate → resolve → semantic
validate → reviewed promote workflow; **9 schema classes and 11 enums** (+804 lines), with
`ProteinReference` and `GroundingEvidence` as new `tree_root`s; `data/grounding/`
registries (126 proteins, 127 evidence rows, tracked); and `canonical_examples` on **127
existing records**.

**Why it could not be split**, contrary to the plan filed on #605: the three parts are
validation-coupled. 127 records carry 127 examples over **126 distinct proteins**
(`UniProtKB:P53248` legitimately serves two traits), matching 126 registry rows and 127
evidence rows with **no orphan in either direction**. A records-only PR would land 127
`QUALIFIED` records whose registry rows do not exist yet, which `data/grounding/README.md`
defines as a validation failure.

Follow-on work, all merged: **#606** (PR #614) gated the grounding validator in CI —
`validate-all` had become two halves and only the first ran, while `checks.yml` said
otherwise; `data/grounding/` is now a full-validation input, which needed prefix support in
`validation_scope.py`. **#607** (PRs #615, #621) pinned the reviewed preimage in the
resolver ledger, so the promoter no longer reads it from a moving Git HEAD.

### 2. Five machine-local-green defects, and what caught them

Every one was correct on the laptop that wrote it and wrong elsewhere. **CI on a clean
Linux checkout caught three; two needed something else.**

| issue | what was machine-local | caught by |
|---|---|---|
| **#610** | `reports/` is untracked so `strict=True` crashed (13 tests); `REPO / "Justfile"` resolves only on a case-insensitive filesystem; two tests assumed a gitignored 2 GB download | CI |
| **#611** | non-strict `Path.resolve()` raises on a symlink loop in 3.12 and returns the path in 3.13; `requires-python` spans both | CI |
| **#613** | the run-artifact identity check compared `(st_dev, st_ino)`, which **Linux defeats by reusing a freed inode** — the guard did not work on the deployment platform | CI |
| **#607** | a test that passes only while the work is **uncommitted**; committing is what breaks it | local full suite |
| **#616** | the new grounding gate failed a deletion-only diff, where the strict step beside it passed | adversarial review, after CI was green |

**#618 gates the two shapes a static check can catch** — case-mismatched repository paths,
and strict resolves of roots absent from a clean checkout. It deliberately does **not**
claim to cover the class: CI remains the gate, and the module says so.

### 3. Three defects in guards written the same day

Filed and fixed within their own PRs, all one shape — **green because the check measured
something other than what it named**:

- **#619** — the constant finder was a single-line regex; five real constants written
  across lines were skipped, including `DEFAULT_PANTHER_CLASSIFICATIONS`, one of four
  pinned sources the content replay verifies. Now AST.
- **#620** — the resolution-digest rule existed in **three** implementations (`ground`,
  `finalize`, `select`). Changing one left two disagreeing; a unit test passed while the
  end-to-end failed. Now one call, pinned both ways.
- **#622** — a malformed `record_preimage` silently fell back to Git, and *passes* in an
  uncommitted tree, telling the operator the text was pinned when it was not.

**Each was found by mutation testing, not by the suite.** None would have failed on its own.

### Also merged in this window

`review-open-issues` re-adapted from MicroGrowLink v1.1.0 (#572) and CultureMech v2.0.0
(#596) · the `next-tasks` skill that maintains this file (#556) · vendored governance
migrated to claw (#564) · the trait-category vocabulary governed across the fleet (#581,
PR #582) with the audit gated on what this repo can fix (#585, PR #588) and the TraitMech
pin checked against the live repository (#584, PR #590) · one guarded ripgrep prefilter
shared across nine call sites (#571, PR #586) and a gate for undeclared external binaries
(PR #576) · scaffolder ids collision-free by construction (#593, PR #594) and offset
timestamps normalised to UTC (#595, PR #612) · the corpus map's hover identifier tinted by
its marker colour (PR #598) and the legend rebuilt from DOM nodes (#602, PR #609) ·
canonical deep-research providers (PR #604).

---

## Where the mechanism layer stands (2026-07-30)

**Every mechanism-rich source now carries causal graphs.** Rounds 12–17 took the
corpus from 0 to **39,647 records · 40,115 graphs · 347,473 nodes · 368,920 edges**,
audit **0 errors**, **368,920/368,920 edges snippet-cited**.

| source | records w/ graph | round | PR |
|---|--:|--:|---|
| Rhea | 18,558 | 16 | #89 |
| ARO / CARD | 7,399 of 7,452 | 14 | #80, #84 |
| EC | 6,888 of 7,375 | 16 | #89 |
| BioLiP | 5,571 | 15 | #86 |
| M-CSA | 1,003 | 12–13 | #77, #81, #82 |
| MetalPDB | 228 | 15 | #87 |

Round 17 added no new records — it **cross-linked** two existing sources: 427 Rhea
records gained 468 `catalytic_residues` graphs carrying the M-CSA residues that
perform them, joined on exact ChEBI set equality.

All 5,845 audit warnings are **ungrounded-node** warnings (5,845 = 347,473 −
341,628 grounded), unchanged across rounds 16 and 17. There are **zero**
missing-snippet and zero missing-`predicate_id` warnings left, so `--strict` is now
purely a grounding gate — a change from when the Refinements note below was written.

---

## Next up (actionable, ranked)

_Issue #7 (Swiss-Prot population + multi-trait families) was **closed 2026-07-27**
after 15 phases; the per-protein-YAML ask was answered with measurements rather
than deferred (see `research/docs-scalability-audit-1.md`). Issue #5 is all but
cleared._

1. **Per-gene curation of the remaining resistance causal-graph drafts — 1,219 →
   679.** The family-level promotion is done (6,180 REVIEWED). PR #84 made every
   draft edge *cited* (the corpus is 100% snippet-covered), so these are no longer
   defective — they are simply still `graph_id: resistance-draft` rather than
   family-wired graphs.
   **Round 18 (2026-08-05) closed the gyrA fluoroquinolone family: 25 records,
   275 cited edges** — `research/causal-graphs-round18.md`. **Round 19 (2026-08-05)
   closed parC, gyrB and parE: 28 more, 308 edges** — `research/causal-graphs-round19.md`.
   **Round 20 closed vanX: 9 records, 81 edges, and a third kind of mechanism —
   precursor depletion** — `research/causal-graphs-round20.md`. **Round 21 closed vanH:
   8 records, 80 edges, the other end of the same pathway** —
   `research/causal-graphs-round21.md`. **Rounds 22–27** then covered vanR/vanS (16 + 12,
   a fourth kind — regulation — and the first graphs citing earlier rounds' records as
   nodes), the D-Ala-D-Ser route (19: ligase, vanT, vanXY), vanY (6), rpoB (11, the
   rifamycin RRDR — first round outside the van set), katG (5, a **fifth** kind: resistance
   by *losing* a function) inhA (5, a **sixth**: titration by target overexpression) and 16S rRNA (45, the first
   determinant that is not a protein). Reports `research/causal-graphs-round{22..29}.md`.

   **The mechanism kinds now in the corpus:** inactivation · target alteration · precursor
   depletion · precursor substitution · regulation · prodrug-activation loss ·
   target overexpression · **target protection** (31) · **electrostatic repulsion** (32) ·
   **efflux** (33).

   **Family-shaped work still available**, measured by ancestry over the remaining drafts:
   two-component modulators (87), permeability (41), ~~target-modifying enzymes (24)~~ **DONE (round 49)**,
   macrolide inactivation — ~~esterases (6, round 46)~~; ~~phosphotransferases (16, r47)~~ ~~glycosyltransferases (8, r48)~~ — **all three chemistries done**, the other three cell-wall-charge chemistries (ArnT/PmrF,
   the ICR transferases, PhoP), and target protection's rifamycin (6) and fusidane (5)
   arms. ~~**Efflux (137) is filed as #223**~~ **— #223 was wrong and round 33 corrected it.** The
   SUBUNITS have no pump-class ancestry, but each is `part_of` a complex and the COMPLEX is
   `is_a` RND/MFS/ABC/…, so the class is two hops away and derivable. RND (77, round 33) and **ABC (14, round 34)** are done. ~~**MFS (13)** and **SMR (4)**~~ **DONE (round 35)** — four configs now sit under one
   family term, one per pump class. Round 36 closed 4 more by walking `is_a`
   ancestors for `part_of` (a species-specific *E. coli acrA* inherits its complex through
   the generic `acrA`). The **21 left are filed as #229** and are three different problems,
   none of them curation: 8 Mex transporter+adaptor pairs that are probably complexes
   miscategorised as subunits, the 10-record ini operon whose efflux role is proposed
   rather than established, and YajC carrying a complex id where a mechanism id belongs.

   **"No shared family config fits" — this item's own claim — is wrong for the
   target-alteration genes, and round 18 measured it.** 25 of the 30 gyrA drafts are
   `is_a` descendants of one family term (ARO:3003292) sharing one mechanism, one drug
   class and one pair of papers; `promote_family_drafts.py` covered them in one run.
   What is genuinely per-organism is the **residue numbering** (Ser83/Asp87 in E. coli
   GyrA = Ala90/Asp94 in M. tuberculosis), not the mechanism. The claim does still hold
   for the **565** drafts whose label carries no gene symbol at all — efflux subunits,
   two-component regulators — which is where it came from.

   Ranked remainder, by whether one family term covers them:
   - ~~**gyrB (18) · parC (14) · parE (8)** — same mechanism and same two papers as
     gyrA.~~ **DONE (round 19), and the premise was wrong on both counts.** Only **29**
     of those 40 are fluoroquinolone (the rest are **aminocoumarin**, a different drug),
     and they are **two** mechanisms, not one: ParC is topoisomerase IV's homologue of
     GyrA (A subunit, `Pfam:PF00521`, water-metal ion bridge), while GyrB and ParE are
     the **B** subunits (`Pfam:PF00204`, ATPase + TOPRIM) whose QRDR residues are not
     that pair — so they need their own papers (PMID:1656869, PMID:22290942) and must not
     cite the A-subunit affinity experiment.
   - **Aminocoumarin gyrB/parE (~5)** — ARO:3000479, ARO:3000457. A **third** shape:
     novobiocin binds the GyrB **ATPase** site (`Pfam:PF02518` is in the KB). Next.
   - **ARO:3003702** (P. aeruginosa gyrA **and** parC) — the first determinant naming two
     subunits; needs a config with one QRDR node per subunit. Held out by the promoter's
     new per-family `exclude` list.
   - **van* clusters (~103) — NOT one mechanism, and the ligases are already done.**
     Measured in round 20: `ARO:3002978` (D-Ala-D-Lac ligase, vanA/B/D/M) has **0 drafts**
     — round 14 promoted them. What remains is the accessory and regulatory machinery,
     organised by **gene role**, each needing its own edges and evidence:
     ~~vanR **14** · vanS **14**~~ **DONE — 16 in round 22, the other 12 in round 24
     once #208 let a family carry two configs** · ~~vanX **9**~~ **DONE (round 20)** ·
     ~~vanH **8**~~ **DONE (round 21)** · ~~vanY **7**~~ **DONE (round 25, 6 of 7)** · ~~vanT **7** · D-Ala-D-Ser ligases **6** · vanXY **6**~~
     **DONE (round 23)** · ~30 others.
     Next, and now one coherent round: **the D-Ala-D-Ser side** — the 12 vanR/vanS
     records round 22 held back (clusters vanC/E/G/I/L/N have no vanH, and all but vanI
     no vanX), the **D-Ala-D-Ser ligases** (6), **vanT** (7, the serine racemase) and
     **vanXY** (6). They share clusters and a downstream, so one round covers them.
     Then **vanY** (7).
   - ~~**rpoB (11)**~~ **DONE (round 26)** — rifamycin RRDR, the gyrA shape on a different
     target. The remaining rpo* records are **different drugs** (daptomycin, vancomycin)
     under different parents, plus rpoA/rpoC compensatory substitutions; each needs its
     own evidence.
   - ~~**katG (5)**~~ **DONE (round 27)** — a FIFTH mechanism kind: resistance by
     *losing* a function, since isoniazid is inert until katG activates it.
   - ~~**ethA (9)**~~ **DONE (round 30)** — found by fetching PMID:10944230 *by
     identifier* rather than by title, which is the reusable trick: a title search for a
     25-year-old mechanism paper competes with everything published since.
   - ~~**inhA (5)**~~ **DONE (round 28)** — TWO routes on one determinant, both from
     PMID:8284673: a missense substitution (target alteration) and the **wild-type** gene
     on a multicopy plasmid (titration by overexpression — a **sixth** mechanism kind).
   - **fabG1 (7)** — the promoter half of that operon. Round 28's overexpression edge
     *predicts* it, but the paper demonstrating chromosomal promoter alleles in
     M. tuberculosis was not found; stretching the multicopy-plasmid result to cover them
     is the over-reach #201 exists to stop. **Filed as #219**, and the blocker is now
     precise: the quantitative half was found (PMID:12406221, the correct id — 20-fold INH,
     10-fold ETH, with inhA mRNA correlating and kasA mRNA not) and **added to the inhA
     record**, but nothing — not even CARD's own definitions — states that a fabG1 promoter
     substitution raises inhA expression, which is the step that makes fabG1 a determinant.
   - **kasA (#220)** — PMID:12406221 specifically found kasA overexpression confers NO
     isoniazid resistance, contradicting a draft record. The corpus has no way to represent
     a contested claim, which may be a schema question.
   - **the other isoniazid-related genes** (**measured 17 on 2026-08-10**, 15 after round 123 took `nat`; #392) are 1–2 record chains (ndh, nudC, mshA/B/C,
     nat, furA, sigI, iniA, mymA, Rv0565c, inbR, kasA, mmaA3, Rv1258c). Several have thin
     or contested evidence; for some the honest outcome is staying drafts.
   - ~~**rRNA target alteration — 105 drafts, not ~22.**~~ **measured 0 on 2026-08-10** (#392). ~~16S/aminoglycoside (45)~~
     **DONE (round 29)**; 23S/macrolide (26) is next by size, then linezolid,
     pleuromutilin, oxazolidinone and tetracycline families. ~~**23S is filed as #217**~~ **DONE (round 50)** — the paper was found by searching for a
     BINDING-measurement rather than a substitution-construction: PMID:7689111.
     **Settle #215 first:** these determinants are RNA, the KB is of protein traits, and
     their graphs cannot route through any protein-trait record because the corpus holds
     no rRNA trait records. Round 29 curated them as they are and said so.
   - ~~**565 with no gene symbol**~~ — **measured 27 on 2026-08-10** (16 efflux + 11 regulator); see the block at the top of this file and #392.

   Tracker: `grep -rl "graph_id: resistance-draft" data/traits/function/resistance/aro/`.
   Skill: `edison-causal-graphs`; promoter: `promote_family_drafts.py`
   (`FAMILY_SNIPPETS`, now with `extra_nodes`/`extra_edges` for mechanisms the fixed
   inactivation shape cannot express).

2. ~~**Join Rhea reaction chemistry to the M-CSA catalytic residues that perform
   it.**~~ **DONE (2026-07-30, round 17, PR #89)** — 427 Rhea records gained 468
   `catalytic_residues` graphs / 2,871 edges, joined on **exact ChEBI set equality**
   (M-CSA reactant set == one Rhea side, product set == the other). Residue nodes are
   reused verbatim from the M-CSA records' SIFTS-resolved graphs.
   `scripts/build_rhea_mcsa_residue_graphs.py`; `research/causal-graphs-round17.md`.

   **This item's stated premise was wrong and the round corrected it.** It claimed
   the join would answer *"which residue attacks which substrate"*. **M-CSA cannot
   support that**: residue `roles` give a function, a `function_type`
   (reactant/interaction/spectator) and an EMO id but **never a target compound**;
   `marvin_xml` is a *filename* (max 107 chars), not atom-mapped arrow-pushing; and
   the only place a residue and a compound co-occur is free-text step prose that
   names compounds as jargon rather than by ChEBI. What was written instead is what
   M-CSA does assert: *this residue is causally responsible for this reaction*.

   **The residue→substrate edge is therefore not derivable from M-CSA at scale** —
   see item 3. Do not re-attempt it from M-CSA's structured fields.

3. **Generalise the residue→substrate edge, which already exists in five places.**
   **CORRECTED 2026-08-01.** This item previously claimed *"the corpus still has no
   `RESIDUE → CHEMICAL` edge"*. That was false — a fact-check found **1,870**: 1,865
   residue→metal edges from MetalPDB (round 15) and **5 hand-curated residue→substrate
   edges** in two β-lactamase M-CSA records, e.g.
   `ser70 --[nucleophilic attack on / RO:0002436]--> substrate (CHEBI:35627)` in
   `data/traits/structure/active_site/mcsa/beta-lactamase-class-a-mcsa2.yaml`.
   The claim came from generalising a 200-record sample into a universal negative.

   So the work is **generalisation, not invention**, and it starts from a worked
   example rather than a blank page. Read those two records first — they show the
   target node/edge shape and the evidence standard. Then find a source that states
   the target compound per residue at scale: UniProt `ACT_SITE` comments naming the
   attacked bond, or MACiE / EzCatDB. Rhea's `rh:reactivePart` is *not* a candidate
   (generic `[protein]-…` participants, not catalytic residues).
   **First step is a source assessment, not a build** — and the second lesson of
   round 17 is to check a coverage claim against the whole corpus before ranking a
   thread on it.

4. **Recover some of the 289 EC-agreeing M-CSA↔Rhea pairs whose ChEBI sets differ.**
   Round 17 dropped them deliberately (38% of EC-agreeing pairs do not share
   chemistry, which is why EC alone is not a join key). Some are genuine granularity
   differences — protonation state, conjugate acid/base, cofactor inclusion — that a
   ChEBI-hierarchy-aware comparison could close. The ChEBI ontology is already in
   `data/raw/chebi/`. Keep set equality as the strict tier and report any looser tier
   separately; do not merge the tiers.

5. **UniProt family/domain source coverage — 6 of 18 resources still absent.** See
   the dedicated section below. PANTHER is done (PR #89); SFLD is the next cheap one.
   HAMAP is licence-blocked (CC BY-NC-ND), not cheap — see the ranking.

6. **Swiss-Prot trait profiles (issue #7) — phases 1–14 shipped; issue NOT complete.**
   Delivered: protein×trait matrix over 10 proteomes, trait↔GO correlation,
   trait→function decision trees (held-out-organism validated), cross-axis feature
   correlations, residue-frame alignment. See "Recently shipped" and
   `research/swissprot-trait-profiles-{1..14}.md`.
   **Two of the issue's own asks remain open** (checked 2026-07-27, not assumed):
   - ~~**Multi-trait family clustering — never built.**~~ **DONE (2026-07-27,
     PR #63):** `scripts/cluster_trait_families.py` (`just cluster-families`)
     implements DiviK (doi:10.1186/s12859-022-05093-z) — divisive top-down
     splitting with local feature re-selection per node → **1,837 families with
     a shared trait core** over 29,313 proteins. Validated against held-out GO
     terms (excluded from the features): **81% of families have ≥80% of members
     sharing a GO term**, median 1.00. 57% of proteins are reported *unassigned*
     rather than forced into families. Was: the issue title says
     "+ build multi-trait families" and names doi:10.1186/s12859-022-05093-z.
     What exists is *exact signature-architecture matching* on the 1,000-protein
     pilot (45 families, `research/swissprot-trait-profiles-1.md` §Signal 2) —
     computed ad-hoc in that report, never a script. Phase 1 explicitly queued
     "replace exact-architecture matching with trait-set similarity (Jaccard /
     the s12859 method) for fuzzy families" and no phase did it. There is no
     clustering script in `scripts/`. The protein map (phase 8) is a 2-D
     projection, not clustering.
   - **Per-protein YAML coverage.** The issue asks for "a YAML record for each
     SwissProt protein". We have the `ProteinProfile` class and 1,000 committed
     YAMLs; the other 80,066 live in the gitignored `profiles.jsonl`, and
     Swiss-Prot has ~570k reviewed entries. The jsonl-only decision was made
     deliberately in phase 2 for scale — but it is a departure from the ask and
     should be confirmed rather than assumed settled.
   Remaining cleanup **DONE (2026-07-27, PR #65)** — see
   `research/swissprot-trait-profiles-15.md`:
   - Dead-accession cache: `--top-up` recorded 10,238 accessions UniProt does not
     serve into `_meta.absent` and now skips them (10,238 → 0 re-requests).
   - The 68 `residue_identity` refutations are **closed as not-actionable**: 46 are
     InterPro *domain* entries (never candidates), and the 22 SUPERFAMILY-based
     superfamilies cannot be confirmed on principle — SUPERFAMILY is SCOP-derived,
     CATH is independent, neither publishes a mapping, and InterPro's
     `overlaps_with` is co-occurrence (one superfamily "overlaps" a domain, a
     family and another domain). They stay `related_to` permanently.
   - Docs projection: exemplars were **58% of every detail bucket** (measured live;
     a stale local copy said 28% and gave the opposite answer). The browser now
     projects the top 5 of 8 — the cap was raised for protein sharing, not for
     display — cutting ~13% per bucket. Records keep all 8.

   **Scope call ANSWERED (2026-07-27, `research/docs-scalability-audit-1.md`):**
   issue #7 asks for "a YAML record for each SwissProt protein". Measured: a
   `ProteinProfile` averages 3,810 B, so 570k of them is ~2.2 GB and would take
   the repo to **980,494 tracked files — 2× the 500k threshold** where git and the
   GitHub UI degrade. **Keep the jsonl-only decision.** If more coverage must be
   committed, bucket it (~256 multi-record files, as the detail sidecars already
   do) rather than minting 570k tiny files. This is the `scalability-check`
   skill's tier D. Nothing else blocks closing #7.

7. **Web design review — dataviz / artifact-design findings (issue #5).**
   **Mostly cleared (2026-07-27, PR #68.)** CVD-unsafe palettes fixed via the
   `dataviz` validator: blue↔purple was ΔE 2.6 (protan), green↔teal ΔE 10.8
   (normal vision). Axis pills → reference slots 1–5, worst adjacent CVD ΔE 9.1
   light / 8.4 dark; the protein map → **domain of life** (3 hues, all-pairs
   ΔE 13.2 both modes) because no 10-hue set — and in dark mode no 5-hue set —
   passes all-pairs, with organism kept on the tooltip + CSV. Fixed a live
   regression found while measuring: six of ten proteomes were rendering as the
   same `#888` grey after phase 9 grew the matrix. Landing count fallbacks
   refreshed (were 47% stale).
   **Recorded as exceptions, not doing:** 4 landing cards (the corpus map is a
   real top-level destination with two tabs; reconciling to 3 would hide a view
   to satisfy a count); 1.4px canvas markers (the ≥8px rule is for dot plots — at
   78k points that is a solid blob, and the hover hit radius is already far
   larger than the mark). The Cayman→teal/amber rebrand stays **deferred by
   request**, and is all that remains on #5.

## UniProt family/domain source coverage — ranked ingestion thread

_Assessed 2026-07-31 against UniProt's own database registry
(`rest.uniprot.org/database`, category **"Family and domain databases"** — 18
entries), `download.yaml`, and a corpus-wide identifier census.
**Three rows re-measured 2026-08-22 and all three were wrong** — see the correction below.
**A fourth, PROSITE, was also wrong and that pass missed it** (#566)._

**7 of 18 are ingested as first-class trait records; 6 are not in `download.yaml`
at all.** (Was 6 and 7 — PANTHER was ingested on 2026-07-31, PR #89.)

| UniProt DB | PTM status | records |
|---|---|--:|
| InterPro | seeded | 26,264 |
| Pfam | seeded | 31,025 |
| CDD | seeded | 38,218 |
| NCBIfam | seeded | 38,394 |
| PROSITE | seeded (patterns + profiles) | ~~6,174~~ **3,425** |
| Gene3D | seeded as CATH-Gene3D | 8,151 |
| DisProt | seeded, but as the IDPO disorder *vocabulary*, not DisProt entries | 35 |
| IDEAL | "seeded" — exactly one concept (`proteintraitsmech:IDEAL_PROS`) | 1 |
| ~~HAMAP~~ · ~~SFLD~~ · MobiDB | ~~`candidate`, no seeder~~ **HAMAP and SFLD are seeded — see below**; MobiDB still `candidate` | ~~0~~ |
| **PANTHER** | **seeded 2026-07-31 (PR #89), CC-BY 4.0 — families only** | **15,489** |
| PIRSF · ~~PRINTS~~ · SMART · SUPERFAMILY · AntiFam · CATH-FunFam | ~~**absent from the manifest**~~ **PRINTS is seeded**; the other five are still absent | ~~0~~ |

### Correction — three of these shipped and the ranking never noticed (2026-08-22), plus one stale count (2026-08-26)

Measured by counting YAMLs under each source directory and reading `download.yaml`:

| source | this file said | actually |
|---|---|---|
| **SFLD** | `candidate`, no seeder, 0 records, *"the cheapest real promotion"* (ranked #2) | **`seeded`, 303 records**, via `seed_interpro_members.py`, CC0-1.0 |
| **HAMAP** | *"licence-blocked (CC BY-NC-ND), NOT cheap, do not rank with SFLD"* | **`seeded`, 2,394 records**, and `download.yaml` licenses it **CC-BY 4.0** — the NoDerivatives claim was wrong. A second `candidate` block covers HAMAP's *annotation rules* (prose), which is a different artefact and genuinely not ingested. |
| **PRINTS** | *"absent from the manifest"*, ranked #3 | **`seeded`, 2,106 records**, CC0-1.0 via InterPro's dedication |
| **PROSITE** | 6,174 records | **3,425** — 1,445 `SEQ_DOMAIN` + 1,980 `SEQ_FAMILY`, the only two `prosite` directories in the corpus. Never 6,174 in this era: the count is 3,425 at `4e6ab83cc62` and at this branch's base too. Stale, not a two-block sum — `download.yaml` carries one PROSITE block. Caught reviewing this PR, not by the pass above (#566). |

The first three came in through `seed_interpro_members.py` — one seeder, three sources, which is
why no single ingestion round shows up against their names. **#167 is still open and still
real**, but it is now a *modelling* gap on seeded data (a PRINTS fingerprint is an ordered
set of motifs, seeded as one flat record), not the absence this file recorded. Same for
**#165**: 140 of the 303 SFLD records are name-only stubs.

**⚠️ ELM: this file cites ELM as the model of correct restraint, and 353 ELM records are
committed.** The ranking below says *"treat it like the ELM case (rejected on
NonCommercial) until someone rules on it"* — but `download.yaml` still carries
`status: rejected`, `license: NonCommercial (ELM Software License Agreement) — FLAGGED`,
`seeder: None`, while `data/traits/**/elm/` holds **353 records** in a CC0-1.0 repo. The
exemplar of the rule is the thing violating it. Filed as **#542**; the licensing decision
belongs to **#517**, but the *engineering* half — a registry rule that "records exist for
a source ⇒ its status may not be `rejected`/`candidate`" — is actionable now and would
have caught this. MEROPS is the same shape at lower severity (`candidate` for the
peptidase clan/family block, 1,200 records under `merops/`, though an adjacent
`seed_merops_cleavage.py` block *is* `seeded` — the two need separating before anyone
counts the violation).

### Why "InterPro already integrates them" does not close this

InterPro 109.0 integrates them heavily (HAMAP 99.8%, PIRSF 98%, SMART 97%,
PRINTS 92%, SUPERFAMILY 82%). But `seed_interpro.py` **excludes InterPro's
`Family` type by design** (27,926 of 54,190 entries — and 54,190 − 27,926 =
26,264, exactly PTM's InterPro count), and that is precisely where the
family-oriented member databases live:

| member DB | integrated | of those, in `Family` entries | conceptually reachable in PTM |
|---|--:|--:|--:|
| PANTHER | 10,460 | 10,411 | **49** |
| PIRSF | 3,221 | 3,215 | **6** |
| HAMAP | 2,389 | 2,370 | **19** |
| SFLD | 163 | 159 | **4** |
| PRINTS | 1,937 | 1,773 | 164 |
| SMART | 1,276 | 157 | 1,119 |
| SUPERFAMILY | 1,649 | 0 | 1,649 |

And "reachable" is generous: `seed_interpro.py` parses no `member_list`, so a PTM
InterPro record carries **no** PANTHER/PIRSF/SMART accession. The member database's
own identifiers and hierarchy are not queryable in PTM even where the concept is
covered.

### Ranked

1. ~~**PANTHER**~~ **DONE (2026-07-31, PR #89)** — 15,489 families seeded as
   SEQUENCE / SEQ_FAMILY. Licence confirmed CC-BY 4.0. Families only: all 143,695
   entries would cross the ~500k tracked-file threshold, and InterPro integrates
   PANTHER at family level only. The 128,012 subfamilies remain available behind
   `seed_panther.py --subfamilies` if that scope call is revisited.
2. ~~**SFLD (303)** — the cheapest real promotion.~~ **DONE** — 303 records seeded via
   `seed_interpro_members.py`, CC0-1.0. Remaining work is quality, not ingest: **#165**
   (140 of 303 are name-only stubs; 5 have labels too short to mean anything).
   ~~**HAMAP (2,394) is NOT cheap and should not be ranked with it.**~~ **DONE, and the
   premise was wrong on the licence.** 2,394 records are seeded and `download.yaml`
   licenses HAMAP **CC-BY 4.0** — not the `CC BY-NC-ND 4.0 — FLAGGED` this entry claimed.
   What is still `candidate` is HAMAP's *annotation rules* (prose + references), a
   different artefact. **The ELM comparison this entry rests on has itself inverted** —
   see the correction above: ELM is still `rejected` and has 353 records committed (#542).
3. **PIRSF (3,285)** — small, sequence-signature classification →
   `SEQ_DOMAIN` / `SEQ_FAMILY` per axis-follows-representation. **The cheapest real
   ingest left**, now that SFLD, HAMAP and PRINTS have all shipped.
   ~~**PRINTS (2,106)**~~ **DONE** — seeded, CC0-1.0 via InterPro's dedication. Open work
   is **#167**: a fingerprint is an *ordered set* of motifs, seeded as one flat record.
4. **SMART (1,322)** and **SUPERFAMILY (2,019)** — lowest urgency: largely reachable
   through InterPro `Domain` entries already in PTM, and SCOPe (22,810) already
   carries SUPERFAMILY's parent classification.
5. **CATH-FunFam** — deepens the existing CATH hierarchy rather than adding a source.
6. **AntiFam (278)** — a *negative* resource (spurious protein predictions).
   Arguably out of scope as a trait; possible QC filter instead. Decide before
   ingesting.
7. **MobiDB** — instance-level per-protein disorder predictions; the trait-*class*
   analogue is IDPO, which is already seeded. Probably leave as `candidate`.

### The bigger lever, which is a decision and not an ingestion

Re-seeding InterPro's 27,926 `Family` entries with the seeder's existing
`--include-families` flag would do more for family coverage than ingesting PANTHER.
The flag exists and the docstring calls it **"not recommended"** — the exclusion was
a deliberate modelling call (a whole-protein family "does not localise to a
sequence/structure element"). Re-open that decision explicitly rather than quietly
flipping the flag; it interacts with `FUNC_PROTEIN_FAMILY`, which was added later
and may now be the right home for them.

## Open threads from rounds 15–16 (context, ranked within themselves)

- **METPO records should link to TraitMech, not get graphs here.** The 70 METPO
  records sitting in `FUNC_ENZYMATIC_ACTIVITY` (acetogenesis, aerobic respiration)
  were the only enzymatic-activity records round 16 left without graphs, and
  deliberately: they are metabolic strategies, not protein traits, so their causal
  graphs belong in the sibling **TraitMech** repo. **The work is an outbound
  cross-reference**, not local graph authoring. Separately, their categorisation as
  `FUNC_ENZYMATIC_ACTIVITY` looks wrong — a `review-source-categories` question.
- **`chemical_participants` cannot express reaction direction (schema question).**
  All 18,558 Rhea records still say `role: SUBSTRATE_OR_PRODUCT`, which is *correct*
  for an undirected master reaction — but the round-16 graph now carries the side
  assignment (cited to Rhea's directional child), so the record's own field is
  strictly less informative than its graph. Decide whether the seeder gains a
  directional variant or the field defers to the graph. Do not "fix" the field by
  copying the graph: the master reaction genuinely has no direction.
- **BioLiP coverage: 445 records** whose PDB/chain/ligand is absent from the
  non-redundant `BioLiP_nr.txt`. The full BioLiP release would cover them (round 15).
- **MetalPDB coverage: 63 records** where no site matched both metal and nuclearity
  with a protein ligand (round 15).
- **689 EC records assert no chemistry** because Rhea has no reaction for them, and
  **487 more got no graph at all** (410 class-level `EC:x.x.x.-` nodes, 77 leaf
  entries with no reaction, no `DR` protein and no GO mapping). Rhea covers the EC
  hierarchy incompletely; nothing local fixes this.
- **1,063 multi-reaction EC classes show at most 3 of their reactions.** Stated in
  each graph's description — a display cap, not a data limit.

## Broken gates — CLEARED (2026-08-04)

Both gates named here on 2026-07-31 are fixed, and both were re-measured today rather
than assumed:

- **non-CURIE `xrefs`** — the sweep found **28** values that could not satisfy the CURIE
  pattern (27 DOIs, plus a literal `CATH:???????`). Now **0**. DOIs moved to
  `evidence.reference`, whose range accepts them; the CATH placeholder was dropped.
  Re-measured by the text scan this section recommends: **0 non-CURIE xref values
  across all 424,467 records.** A full `just validate-all` was last run clean on
  2026-08-01 and is deliberately not re-run here — it takes hours, and the scan
  answers the same question in under a minute.
- **`just sources-check`** — the two invalid `download.yaml` statuses (`superseded`,
  `enrichment`) were added to the checker's allowed set rather than re-statused, which
  keeps the information about what those two sources are for. Exits 0 (17 warnings, all
  the pre-existing orphan-seeder kind). Closed as #91.

Kept as a heading rather than deleted because the note it carried is still worth having:
**do not diagnose a corpus-wide validation failure with `just validate-all`** — a full
sweep re-runs per-file on every failing batch and takes hours. A direct text scan against
the CURIE pattern answers the same question in under a minute, and is what re-measured
this today.

## Refinements (small, opportunistic)

- **Confirm MCR / APH causal-graph folds** vs the crystal structures before treating
  those REVIEWED graphs as gold (`CATH:3.40.720.10` MCR, `CATH:3.90.1200` APH).
- **B3-specific MBL domain node**: `CDD:cd07708` exists if a GOB/B3-specific (rather
  than pan-MBL `Pfam:PF00753`) domain node is wanted on GOB-10 / subclass-B3 graphs.
- **The 5,845 ungrounded causal nodes are the whole warning list** — 4,023 M-CSA
  STATE nodes (reaction intermediates), 1,817 BioLiP fusion-chain residues (BioLiP
  names several accessions for a chimeric chain and does not say which half a residue
  belongs to), and 5 hand-curated label-only nodes — 4 reaction intermediates plus one
  `rrna` node in `ermb-aro3000375.yaml` that is not one. MONDO/HP/reaction-intermediate grounding
  would close the first group; the BioLiP group needs the source to disambiguate.
- **`just audit-graphs --strict` is now purely a grounding gate.** Snippet and
  `predicate_id` coverage both reached 100% in round 16, so turning `--strict` on in
  CI today would gate solely on the 5,845 ungrounded nodes above. Gating on snippets
  (the original intent of this note) can be done with plain `just audit-graphs`.
- **The round-15 builders were never reviewed for the two idiom-level defects fixed
  in 5e9e920** — `re.sub` with a *string* replacement template (which interprets
  backslashes and `\g`), and skip predicates testing the bare substring
  `causal_graphs:` instead of their own `graph_id`. Both were latent in round 16 and
  are latent in round 15 too, which is exactly why they need looking for rather than
  waiting for. Issue #94; best done as part of the shared splice helper in #93.

## Recently shipped (DONE)

### 2026-08-01 → 08-04: the infrastructure round (14 PRs)

Almost none of this was planned here. It came out of reviewing merged work, and roughly
half of it corrected a claim in the issue that prompted it — which is the reusable lesson,
not the individual fixes.

**Data safety — the one that mattered most.**
- **`--force` re-seeds no longer destroy curation** (#100, PR #119). Measured, not
  estimated: the old behaviour rewrote **1,604 records, destroying 1,089 curated
  definitions and 1,604 curation histories** on PANTHER alone; corpus-wide exposure was
  39,647 causal graphs and 96,476 evidence blocks. Now 0 files modified. Enriched *lists*
  are unioned too, after `seed_prosite --force` was found dropping 4,193 GO xrefs.

**PANTHER definitions (#92).**
- **1,604 LLM abstracts promoted** after LLM review (PR #111), then **515 demoted** (PR
  #113) when a stricter re-review found them superfamily-level. Net **1,089** real
  definitions where stubs had been. The filter that selected which to re-review turned out
  **not to discriminate** (36% vs 42%), so the pass was extended to all 1,604 rather than
  reported as complete — see #114.

**Tests, lint and CI, where there had been none.**
- **First test suite** (#96, PRs #101/#108) → **248 tests** across 7 files on `main`.
- **All 63 ruff errors fixed and gated at zero** (#107, PR #121), with CI running `just
  lint` and `just test` on every PR. It immediately caught a `NameError` the import-time
  tests structurally could not.
- **Runtime harness for all five causal-graph builders** (#132/#141, PRs #140/#142) —
  catches `break`-instead-of-`continue`, which no source-level check can. Two loop shapes:
  four are glob-driven, `build_mcsa` is cache-driven and needs its own fixture. Covers the
  **skip path only** — graph construction and the splice-refusal branches are #144.

**Shared implementations, closing #93.**
- `record_io` (splice, `has_graph`, re-seed merge) and `yaml_emit` (`yaml_escape`,
  `folded`, `slugify`). `yaml_escape` went 43 copies → **1**; `slugify` 28 distinct
  implementations → 1 plus parameter-only wrappers, so **no record was renamed**. Closed
  #109 and, in effect, #110.

**Text decoding.**
- OBO escapes now decoded in definitions, not just citations (#103); double-decoded CAZy
  and TCDB text repaired (#123); **`just audit-text`** added (PR #142), reporting **0
  reversible damage** and **97 lossy U+FFFD**. The re-fetch showed that loss is upstream at
  BV-BRC, so **#139 stays open, re-scoped** — 97 records, not the one it was filed for.

**Process.**
- `prompts/backlog-loop-goal.md` and `NEXT_TASKS_LOOP.md` — the loop workflow and its
  ranking. Three scoped prompts are kept as spent worked examples.


- **Causal-graph mechanism layer, rounds 12–16** (2026-07-28 → 2026-07-30, PRs
  #77, #80–#89) — the mechanism layer went from 6,180 to **39,647** records with
  graphs and from ~0 to **366,049** cited edges, covering four distinct kinds of
  mechanism:
  - **Catalysis — M-CSA, 1,003 records** (rounds 12–13, PRs #77/#81/#82, closes
    #78/#79): stepwise mechanisms transcribed with residue roles; the last 265
    entries recovered via `mechanism_text`; residue frames reconciled to UniProt
    through SIFTS.
  - **Resistance — CARD/ARO** (round 14, PRs #80/#84): drug edges re-based on
    CARD's own assertion rather than ours, and every remaining edge given a
    snippet (corpus reached 100% cited). 1,219 drafts remain drafts — see Next up #1.
  - **Interaction — BioLiP 5,571 + MetalPDB 228** (round 15, PRs #86/#87): residue-
    level ligand contacts and metal coordination. Established the rule the later
    rounds run on — **do not quote your own seeder's text as evidence** — and the
    practice of verifying against a source's own internal redundancy.
  - **Transformation — Rhea 18,558 + EC 6,888** (round 16, **PR #89, open**):
    substrate→product chemistry. Rhea master reactions are undirected, so every
    input/output edge is cited to Rhea's *directional child*, which is where Rhea
    itself states which side is consumed. New `scripts/rhea_rdf.py` (stdlib
    streaming reader for `rhea.rdf.gz`); all 18,558 reactions verified by
    re-rendering Rhea's own equation string from the parsed participants.
  Reports: `research/causal-graphs-round{12..16}.md`.

- **Swiss-Prot trait profiles, phases 1–14** (2026-07-21 → 2026-07-27, PRs #29–#33,
  #37, #41, #45, #48, #51, #55, #58, #59, #61, #62). Protein×trait matrix over
  **10 proteomes / 80,066 proteins** (`build_swissprot_profiles.py`); cross-axis
  rule overlay `trait_cooccurrence.tsv` (2,590 edges, split by GO aspect);
  **309,535 `canonical_examples`** on 72,003 records (`suggest_canonical_examples.py`);
  held-out-organism validation (`test_rule_generalization.py` — seq-encodes-fold
  replicates 97.2% incl. 100% in an archaeon, trait-implies-function 84.8%);
  protein map (`build_protein_map.py`, "Proteins" tab); corpus-map structure audit
  (`measure_map_structure.py`); **residue-frame alignment** —
  `seq_struct_alignment.tsv` **0 → 16,350** and `seq_struct_func_sites.tsv`
  778 → **9,798** edges via the `profile` + `interpro_frame` providers and two
  release-stamped sidecars (`fetch_residue_frame.py`, `fetch_interpro_frame.py`,
  `sidecar.py`); **1,697 adjudicated `close_match`** CATH↔InterPro equivalences
  (`verify_residue_identity.py`) that no identifier mapping in the corpus had.
  Closed #54, #56, #57, #60. Reports: `research/swissprot-trait-profiles-{1..14}.md`.
  **Issue #7 itself stays open** — its clustering ask was never built (see Next up #2).

- **Causal-graph mechanism layer, rounds 1–11** (2026-07-21, PR #24/#28 + direct to
  main): `edison-causal-graphs` skill, `audit_causal_graphs.py` (`just audit-graphs`),
  `enrich_aro_resistance.py`, `draft_aro_causal_graphs.py`, `promote_family_drafts.py`.
  6,180 REVIEWED resistance graphs across all 6 CARD mechanism classes, every one
  routed through KB SEQUENCE/STRUCTURE trait records; audit 0 errors. Reports
  `research/causal-graphs-round{1..11}.md`.
- **Three-way SEQ/STRUCT/FUNC alignment + overlays** (2026-07-21, PR #24): Path-1
  residue-frame `seq_struct_func_sites.tsv` (778) + Path-2 co-membership
  `seq_struct_comembership.tsv` (13,400); `build_seq_struct_comembership.py`,
  interpro/sifts/biolip providers.
- **3did interfaces** (#23), **MEROPS cleavage sites** (#22), **orthology overlay**
  (#21, closes #20), **5 round-4 sources** (#17) — all 2026-07-20.
- **Deleted the superseded `seq-struct-alignment-step2` branch** (2026-07-21) — its
  providers were ported to `main`; its BioLiP record-mutation approach was replaced
  by the read-only `biolip` provider.

## Blocked / not actionable (kept for context — do not recommend as "next")

- ~~**Full `interpro,sifts` crawl to populate the base overlay** — ~33k API calls
  yielding 0 base edges; do not run.~~ **This was wrong and is now retracted
  (2026-07-27).** The measurement was sound for its moment and did not generalise:
  it assumed the *per-(signature, protein)* query shape and the pre-phase-5
  exemplar set, when signatures and folds genuinely shared no exemplars. Phase 11
  ran the crawl **per protein** over the exemplars phases 5–9 added and the base
  overlay went 0 → 12,424 edges (16,350 after phase 14). Kept here, struck through,
  because "do not run" sat in the backlog for a week over work that turned out to
  be the single largest win of the thread.
- **Fold data-gaps (`CATH:3.40.50.300`, `CATH:3.20.20.70`, Qnr β-helix)** — turned
  out to be false alarms; all existed and the ABC/qnr graphs were re-grounded
  (2026-07-21). Closed.
