---
topic: causal-graphs
round: 80
date: 2026-08-07
target: aro/FUNC_RESISTANCE — emb arabinosyltransferases (ARO:3005005), 10 records
prior_round: causal-graphs-round79.md
---

# Causal graphs — Round 80: target alteration where the source names the target's job

Rounds 18–19, 53 and 61 curated target alteration where CARD gave the mutation and the
resistance but little about what the target *does*. embB's definition gives all three:

> *"embB gene encodes for an **arabinosyl transferase** in the **arabinogalactan synthesis
> pathway**. **It is inhibited by ethambutol.** Mutations within the ERDR region of embB
> confers resistance to ethambutol."*

Enzyme, pathway, drug action, and mutation — four claims in three sentences. So the graph
ends at a real process rather than at a bare `resistance` node:

```
determinant --enables--> arabinosyl_transfer --part of--> arabinogalactan
drug0       --causally upstream of--> inhibition
determinant --negatively regulates--> inhibition        ← the causal core
```

**Contrast #219 (fabG1)**, where the drug's action had to be sourced separately and three
rounds were spent failing to. Here CARD says *"It is inhibited by ethambutol"* outright.
Same organism, same drug class, entirely different quality of definition — which is the
argument for reading each family rather than assuming a house style, made once more.

## One scope note

The **ERDR region** is named by embB's definition and by no other member's. It is quoted in
the evidence but is **not** a node, and the `notes` say the sentence is embB's. A test pins
that no node label mentions ERDR.

## Provenance

* records touched: **10** · SEEDED → REVIEWED
* `just test`: **658 passed** (+1) · `just validate` on all 10: **0 failures**
* corpus: **0 errors · all edges snippet-cited**
* drafts remaining: **385 → 375**

## Open questions

* **Four curatable families remain in the ARO:3000212 block**: polyketide synthase (8),
  folP (7), rpoC (6), liaFSR (6).
* **#229** now has seven measured instances and wants rescoping.
