---
topic: causal-graphs
round: 57
date: 2026-08-07
target: aro/FUNC_RESISTANCE — ndh (ARO:3003460), 4 records; ahpC blocked
prior_round: causal-graphs-round56.md
---

# Causal graphs — Round 57: ndh's two arms, and CARD contradicting itself on ahpC

## ndh — prodrug-activation loss, but at a distance

Round 56's pncA loses the activating enzyme itself. **ndh loses nothing of the sort.** It
is a NADH oxidase; its mutation shifts the **NADH/NAD⁺ ratio**, and that blocks isoniazid
two steps downstream. Same mechanism family, different causal distance — which is why it
needed its own config rather than reusing pncA's.

CARD carries the whole chain, including **both arms**, in one sentence:

> *"ndh is a NADH oxidase. It participates in antibiotic resistance by diminishing NADH
> oxidation and consequently causes an increase in NADH concentration and depletion of
> NAD+. This alteration of the NADH/NAD+ ratio prevents the peroxidation reactions
> required for the activation of INH, **as well as** the displacement of the
> NADH-isonicotinic acyl complex from InhA enzyme binding site."*

**That "as well as" is doing real work.** It joins two *independent* blocks — INH is never
activated, *and* the acyl complex is never displaced from InhA. Collapsing them into one
edge would silently drop a mechanism, so the config splits them and **a test pins that
both survive**.

`nadh_ox` is left ungrounded on purpose: CARD says "NADH oxidase" and the nearest GO terms
are NADH *dehydrogenase* activities. Round 56's rule — do not guess a CURIE you did not
verify.

## ahpC is blocked, and not for lack of evidence

Reading the three ahpC records first — the discipline that has paid off every round since
51 — turned up **CARD asserting two incompatible mechanisms for the same gene**:

| record | claim |
|---|---|
| ARO:3004893 | *"Mutations in ahpC that contribute to antibiotic resistance by **preventing ahpC from activating antibiotics**."* |
| ARO:3004921 | *"Mutations that occur in ahpC that result in **ahpC overexpression** thus conferring or contributing to resistance to isoniazid."* |

Loss-of-activation and over-expression are not two descriptions of one mechanism; they are
opposite directions. A third record (ARO:3004894) describes only what the enzyme *is*.

Filed as **#260**. Curating either claim would mean picking a side CARD does not pick, and
this KB has no way to represent a contested claim (#220, still open).

## Provenance

* records touched: **4** (ndh) · SEEDED → REVIEWED · ahpC's 3 left as drafts
* `just test`: **610 passed** (+2) · `just validate` on all 4: **0 failures**
* `--verify`: 0 precondition skips, 0 uncovered mechanisms, **0 problems**
* corpus: **371,358 edges · 0 errors · 371,358/371,358 snippet-cited**
* drafts remaining: **619 → 615**

## Open questions

* **#260 (ahpC)** needs a policy, not effort — the same shape as #220. It is the fourth
  record set this session whose blocker was the source's own inconsistency rather than
  missing literature.
* **The confirmed-ready queue is now empty.** What remains is the 565 label-only
  efflux/regulator block, which is the first batch too large for the line-by-line skip-log
  reading that caught three defects this session, and five open decisions.
