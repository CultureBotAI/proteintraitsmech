---
topic: swissprot-trait-profiles
phase: 2
date: 2026-07-21
issue: "#7 — scale + trait→GO decision tree"
prior: swissprot-trait-profiles-1.md
---

# Swiss-Prot trait profiles — Phase 2: scale + trait→GO decision tree

Phase 1 built the per-protein profile pipeline and showed the trait↔function signal
on 1,000 proteins. Phase 2 scales the matrix and trains the **decision tree** issue
#7 asks for — "predict function from the presence of certain traits."

## Scaled matrix
`just build-profiles --query "reviewed:true AND organism_id:9606" --limit 20000
--apply --jsonl-only` → **20,000 reviewed human proteins** in
`data/profiles/profiles.jsonl` (the protein×trait matrix). 99% carry ≥1 corpus
trait; mean 21.6 traits/protein (FUNCTION 260,976 · SEQUENCE 145,217 · STRUCTURE
26,030 matches). A new `--jsonl-only` mode scales the matrix without writing 20k
YAMLs; the matrix is regenerable, so it is gitignored (the 1,000-protein YAML
sample from phase 1 stays committed as the initial population).

## Decision tree — `scripts/train_trait_go_tree.py` (`just train-trait-tree`)
For each top GO **molecular-function** term (GO-MF, identified from the corpus trait
index), fit a shallow `DecisionTreeClassifier` on the **signature-trait** features
(Pfam/InterPro/CATH/PROSITE/SMART/CDD/NCBIfam, top 400 of 33,023), 75/25 train/test.
Interpretable by design (depth ≤4). scikit-learn 1.9 via system python3.

**Macro-F1 over 20 GO-MF targets: 0.49** — but that average hides a clean split:
*specific* molecular functions are predicted very well from their defining
signature, while *generic* ones ("protein binding") are not.

| GO-MF function | learned rule (top feature) | test F1 |
|---|---|--:|
| GO:0004984 olfactory receptor activity | `Pfam:PF13853` (7tm olfactory) | **0.94** |
| GO:0004930 G-protein coupled receptor activity | `CATH:1.20.1070.10` (GPCR fold) | **0.90** |
| GO:0005509 calcium ion binding | `InterPro:IPR011992` (EF-hand) | **0.78** |
| GO:0008270 zinc ion binding | `CATH:3.30.160.60` (zinc finger) | 0.75 |
| GO:0005524 ATP binding | `InterPro:IPR027417` (P-loop NTPase) | 0.75 |
| GO:0000981 DNA-binding TF activity | `PROSITE:PS00028` (C2H2 zinc finger) | 0.74 |
| GO:0004674 protein Ser/Thr kinase activity | `InterPro:IPR011009` (kinase-like) | 0.70 |
| GO:0016887 ATP hydrolysis activity | `InterPro:IPR027417` (P-loop) | 0.56 |
| GO:0042802 identical protein binding (generic) | `Pfam:PF13853` | 0.11 |
| GO:0046872 metal ion binding (generic/broad) | `CATH:3.30.160.60` | 0.12 |

The rules are the biology: 7TM olfactory domain → olfactory receptor; GPCR fold →
GPCR; EF-hand → Ca²⁺; zinc finger → Zn²⁺ / DNA-binding TF; P-loop → ATP; kinase
domain → Ser/Thr kinase. A trait presence *is* a function predictor.

Example tree (zinc ion binding, depth 3) — reads as nested if-present rules:
```
if CATH:3.30.160.60 (zinc finger)        → zinc binding
elif CATH:3.30.40.10 (RING/Zn)           → zinc binding
elif InterPro:IPR002219 (PKC C1/Zn)      → zinc binding
else                                     → not
```

## Reading the result
- **Specific structure/sequence traits are strong function predictors** (F1 0.7–0.94):
  the tree recovers the canonical fold/domain → activity mappings without being told
  them. This is the paper baseline the issue wanted.
- **Generic GO-MF terms** (protein binding, broad "metal ion binding") predict poorly
  — expected: many unrelated architectures share them. Filter to specific leaf GO or
  weight by information content in phase 3.

## Next (phase 3)
- **Broaden** beyond human (multi-organism reviewed) and report per-aspect (MF vs BP
  vs CC) trees; use GO information-content to drop uninformative targets.
- **Multi-label / probabilistic** model + calibrated confidence, and a proper
  train/test over a held-out organism.
- **Cross-axis feature correlation**: does a given sequence motif always co-occur with
  a given structural fold (SEQUENCE→STRUCTURE), independent of function.
- Feed the profile matrix into a **protein×trait browser map** (UMAP/PaCMAP), and use
  the confident rules to auto-suggest `canonical_examples` on the corresponding trait
  records.
