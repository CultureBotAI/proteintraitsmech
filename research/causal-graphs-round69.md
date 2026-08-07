---
topic: causal-graphs
round: 69
date: 2026-08-07
target: aro/FUNC_RESISTANCE — MATE efflux transporters (ARO:3000112), 10 records
prior_round: causal-graphs-round68.md
---

# Causal graphs — Round 69: the same edge as round 67, deliberately vaguer

Round 67 curated SMR and gave it a **proton** gradient node, because EmrE's text names the
ion outright: *"the import of protons down an electrochemical gradient"*.

MATE's text does not:

> *"Multidrug and toxic compound extrusion (MATE) transporters utilize the **cationic
> gradient** across the membrane as an energy source."* — ARO:3000112

**And that vagueness is the source being correct, not sloppy.** MATE transporters really
do split between Na⁺- and H⁺-coupled members. So the gradient node here is generic, and
copying round 67's proton node across would have been the easy mistake — the exact one
round 67's own report warned about for RND/MFS/ABC pumps.

Two efflux configs in this corpus now differ on the coupling ion, for a stated reason. **A
test pins both sides**, so neither can be harmonised into the other by a later reader who
notices the inconsistency without noticing why.

## The second hedge in the same definition

> *"Although there is a diverse substrate specificity, **almost all** MATE transporters
> recognize fluoroquinolones."*

"Almost all" is quoted intact on the drug edge rather than trimmed to a cleaner claim. A
test pins that too.

## The pattern across rounds 63–69

| round | the hedge | what it changed |
|---|---|---|
| 63 | "usually ATP, sometimes GTP" | no donor node |
| 65 | "associated with resistance" | association recorded, not upgraded |
| 65 | "not sufficient for resistance" | negative result quoted |
| 66 | no mechanism at all | mechanism edge omitted entirely |
| 68 | "usually AMP" / "often acetylCoA" | no donor node, ×3 |
| **69** | **"cationic gradient" / "almost all"** | **generic ion node; hedge quoted** |

Seven rounds in which the substantive work was reading how firmly the source states a
thing, not finding the statement. Round 64 is the counter-case that keeps it honest: where
CARD *is* specific, the config is specific too.

## Provenance

* records touched: **10** · SEEDED → REVIEWED
* `just test`: **639 passed** (+2) · `just validate` on all 10: **0 failures**
* `--verify`: **0 problems, 0 near-misses**
* corpus: **371,883 edges · 0 errors · 371,883/371,883 snippet-cited**
* drafts remaining: **458 → 448**

## Open questions

* **The iniA/iniB records under ARO:3000159 stay drafts** — #229 flagged their efflux role
  as only *proposed*, and nothing read this round changes that.
* **22 drafts under ARO:3000557** (small chemistries) and the rest of ARO:3000748's
  subunits remain.
