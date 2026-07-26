---
date: 2026-07-25
issue: "#7 — act on what the held-out tests showed"
prior: swissprot-trait-profiles-6.md
---

# Swiss-Prot trait profiles — Phase 7: aspect-split function edges, and a null result

Phase 6 established two things about the cross-axis overlay: `seq-encodes-fold`
replicates across organisms (96–99%) while `trait-implies-function` does not
(81–88%), and its failures are concentrated in GO **cellular-component** and
lineage-specific terms. The overlay made no distinction between them. Phase 7
acts on that, and tests the other phase-6 recommendation — which turns out not to
have been needed.

## 1. Function edges are now split by GO aspect

The corpus already records each GO term's aspect as its `trait_category`, so no
second GO parse was required. `trait-implies-function` becomes four edge kinds:

| edge kind | edges |
|---|--:|
| `trait-implies-molecular-function` | 482 |
| `trait-implies-biological-process` | 148 |
| `trait-implies-localization` | 65 |
| `trait-implies-enzymatic-activity` | 13 |
| (`seq-encodes-fold`, unchanged) | 771 |

A consumer can now filter to the edges phase 6 showed are trustworthy without
re-deriving the aspect from an external GO release. This is the phase's main
deliverable: the evidence for differential trust existed but the data model gave
no way to express it.

## 2. Organism-balanced support — implemented, and it barely matters

Phase 6 recommended re-mining with per-organism weighted support "so a rule cannot
clear threshold on vertebrate abundance alone". That is now computed: for each
candidate rule, confidence is recomputed within each proteome that carries the
antecedent at least `--min-organism-support` times, and averaged so every organism
gets one vote regardless of size. It is emitted on every edge as
`balanced=<conf>|organisms=<k>`.

**Gating on it changes almost nothing:**

| `--min-balanced-conf` | rules dropped (of 1,479) |
|---|--:|
| 0.80 | 0 |
| 0.90 | 1 |
| 0.95 | 24 |
| 0.95 with voting floor lowered to 2 carriers | 30 |

The reason is that **pooling four proteomes already does the work balancing was
meant to do**. Phase 6's failures were rules mined on human *alone* and then
tested elsewhere. Mining on the pooled matrix never proposes them in the first
place — every one of the five worst phase-6 offenders is absent from the pooled
rule set:

| phase-6 rule (human-mined) | held-out conf | in pooled rules? |
|---|--:|---|
| `PROSITE:PS00657 → GO:0000785` (chromatin) | 0.03 | **gone** |
| `PROSITE:PS00658 → GO:0000785` | 0.05 | **gone** |
| `Pfam:PF01825 → GO:0016020` (membrane) | 0.23 | **gone** |
| `CATH:3.30.50.10 → GO:0005654` (nucleoplasm) | 0.00 | **gone** |
| `Pfam:PF00046 → GO:0000981` (homeobox → pol II TF) | 0.43 | **gone** |

So the honest conclusion is that the phase-6 recommendation was already satisfied
by the phase-6 matrix rebuild, and the balanced metric adds diagnostic value
(*how many proteomes actually back this edge?* — most are backed by 2) rather than
filtering power. `--min-balanced-conf` therefore **defaults to 0.0, off**: it
reports, it does not gate. Turning it into a default filter would have been
cargo-culting a correction for a problem the data no longer has.

This is worth stating plainly because the phase was scoped on the assumption the
gate would bite. It does not, and the measurement saying so is the result.

## 3. A dangling-endpoint bug in the overlay

Found while breaking the function edges down by aspect: 27 edges had a consequent
with **no `ProteinTraitRecord` in the corpus** — `GO:0005615` (extracellular
space) and `GO:0048278` (vesicle docking). The overlay's contract, stated when it
was introduced in phase 4, is that both endpoints are real records so
`build_docs_index.py` can load it bidirectionally; these 27 pointed at nothing.

Cause: the miner built each protein's trait set with a **prefix** filter only —

```python
ts = {t for t in ts if t.split(":")[0] in (SEQ_PREF + STRUCT_PREF + FUNC_PREF)}
```

`r["traits"]` is index-filtered by the profile builder, but `r["go"]` and
`r["ec"]` are raw UniProt annotations, so any GO term a protein carries could
become an overlay endpoint whether or not the knowledge base had a record for it.
Endpoints are now required to be in the corpus index. This is why the function
edges drop 735 → 708 while the fold edges are unchanged.

The bug predates this phase — it shipped in phase 4 and survived phase 6.

## Overlay, phase 6 → 7

| | phase 6 | phase 7 |
|---|--:|--:|
| edges | 1,506 | 1,479 |
| — dangling endpoints | 27 | **0** |
| — function edges as one undifferentiated kind | 735 | **split 4 ways** |
| `relation_source` fields | conf, lift, n, matrix | + `balanced`, `organisms` |

## Gate

* 0 dangling endpoints, verified against the corpus trait index.
* `suggest_canonical_examples.load_rules` re-parses all 1,479 edges and still
  reads the raw `conf=` (not the new `balanced=`) — checked explicitly, since the
  two now sit adjacent in the same string.
* Miner runtime ~16s; per-organism counts are collected only for candidate rules,
  since a full per-organism co-occurrence table over 8.07M pairs would be several
  GB.

## Not done

* **`canonical_examples` were not re-ranked against the new overlay.** The rule
  set moved by 27 edges out of 1,506 and gained metadata; re-running the 61k-record
  pass for that would rewrite the corpus for a change too small to alter the
  ranking meaningfully. The `rule coverage` figures in existing notes were computed
  against the phase-6 overlay, including the 2 traits that had no record.
* Protein × trait **browser map** (UMAP/PaCMAP of `profiles.jsonl`) — still open,
  carried since phase 4.

## Next

- Browser map of the protein × trait matrix.
- Consider whether `trait-implies-localization` edges belong in the overlay at all,
  now that they are separable: phase 6 showed they largely do not replicate, and
  65 edges is a small enough set to review by hand.
- Broaden the matrix beyond four organisms (no archaea, plants, or parasites), the
  standing limitation from phase 6.
