# Sequence map: preprocessing and layout sweep

12,705 proteins embedded; scored on 4,989 with a CATH superfamily (912 classes) and 2,227 with an EC sub-subclass (176 classes) that are also on the protein map. Neighbour-purity lift at k=25; PaCMAP, seed 42 for the grid. **Ranked on CATH superfamily; EC and the global score were not used to choose.** Global = random-triplet accuracy against the centred 1,280-d embedding over 199,963 triplets (0.5 = random).

| prep | PCA | neighbours | variance kept | input CATH | 2-D CATH | 2-D ÷ input | input EC | 2-D EC | global |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| centre | none | 5 | 100.0% | 33.1× | **26.3×** | 80% | 9.9× | 8.0× | 0.676 ← best |
| centre | 200 | 5 | 91.7% | 30.5× | **23.6×** | 77% | 9.1× | 7.1× | 0.687 |
| centre | none | 10 | 100.0% | 33.1× | **23.5×** | 71% | 9.9× | 6.9× | 0.725 ← choice |
| l2 | 200 | 5 | 92.7% | 30.7× | **23.4×** | 76% | 9.2× | 7.0× | 0.691 |
| l2 | none | 5 | 100.0% | 29.4× | **22.8×** | 78% | 9.0× | 7.1× | 0.687 |
| centre | 200 | 10 | 91.7% | 30.5× | **21.3×** | 70% | 9.1× | 6.6× | 0.719 |
| l2 | 200 | 10 | 92.7% | 30.7× | **21.2×** | 69% | 9.2× | 6.5× | 0.722 |
| l2 | 100 | 5 | 87.4% | 26.9× | **20.2×** | 75% | 8.1× | 6.3× | 0.687 |
| centre | 100 | 5 | 85.8% | 26.8× | **19.9×** | 74% | 8.1× | 6.5× | 0.693 |
| centre | none | 15 | 100.0% | 33.1× | **19.5×** | 59% | 9.9× | 6.6× | 0.707 |
| l2 | none | 10 | 100.0% | 29.4× | **18.9×** | 64% | 9.0× | 5.8× | 0.700 |
| centre | 200 | 15 | 91.7% | 30.5× | **18.2×** | 59% | 9.1× | 6.2× | 0.702 |
| l2 | 200 | 15 | 92.7% | 30.7× | **17.9×** | 58% | 9.2× | 6.1× | 0.704 |
| l2 | 50 | 5 | 80.6% | 23.1× | **16.6×** | 72% | 7.1× | 5.4× | 0.722 |
| l2 | 100 | 10 | 87.4% | 26.9× | **16.5×** | 61% | 8.1× | 5.4× | 0.722 |
| centre | 50 | 5 | 78.1% | 23.0× | **16.4×** | 71% | 7.0× | 5.5× | 0.713 |
| centre | 100 | 10 | 85.8% | 26.8× | **16.3×** | 61% | 8.1× | 5.4× | 0.713 |
| l2 | none | 15 | 100.0% | 29.4× | **15.7×** | 53% | 9.0× | 5.2× | 0.699 |
| centre | 100 | 15 | 85.8% | 26.8× | **14.7×** | 55% | 8.1× | 5.4× | 0.714 |
| centre | none | 30 | 100.0% | 33.1× | **14.3×** | 43% | 9.9× | 5.2× | 0.715 |
| l2 | 100 | 15 | 87.4% | 26.9× | **14.1×** | 53% | 8.1× | 4.9× | 0.716 ← shipped |
| centre | 200 | 30 | 91.7% | 30.5× | **13.9×** | 46% | 9.1× | 5.1× | 0.718 |
| centre | 50 | 10 | 78.1% | 23.0× | **13.8×** | 60% | 7.0× | 4.8× | 0.711 |
| l2 | 50 | 10 | 80.6% | 23.1× | **13.8×** | 60% | 7.1× | 4.8× | 0.713 |
| l2 | 200 | 30 | 92.7% | 30.7× | **13.6×** | 44% | 9.2× | 5.0× | 0.718 |
| centre | 50 | 15 | 78.1% | 23.0× | **12.6×** | 55% | 7.0× | 4.7× | 0.717 |
| l2 | 50 | 15 | 80.6% | 23.1× | **12.6×** | 55% | 7.1× | 4.6× | 0.721 |
| centre | 200 | 50 | 91.7% | 30.5× | **12.5×** | 41% | 9.1× | 4.8× | 0.722 |
| centre | none | 50 | 100.0% | 33.1× | **12.4×** | 38% | 9.9× | 4.8× | 0.722 |
| l2 | 200 | 50 | 92.7% | 30.7× | **12.4×** | 40% | 9.2× | 4.9× | 0.723 |
| l2 | none | 30 | 100.0% | 29.4× | **12.3×** | 42% | 9.0× | 4.3× | 0.714 |
| l2 | 100 | 30 | 87.4% | 26.9× | **12.3×** | 46% | 8.1× | 4.8× | 0.719 |
| centre | 100 | 30 | 85.8% | 26.8× | **12.2×** | 45% | 8.1× | 4.8× | 0.721 |
| l2 | 100 | 50 | 87.4% | 26.9× | **11.5×** | 43% | 8.1× | 4.6× | 0.724 |
| centre | 100 | 50 | 85.8% | 26.8× | **11.4×** | 43% | 8.1× | 4.7× | 0.724 |
| centre | 50 | 30 | 78.1% | 23.0× | **11.2×** | 49% | 7.0× | 4.5× | 0.724 |
| l2 | 50 | 30 | 80.6% | 23.1× | **10.7×** | 46% | 7.1× | 3.9× | 0.723 |
| centre | 50 | 50 | 78.1% | 23.0× | **10.6×** | 46% | 7.0× | 4.3× | 0.729 |
| l2 | 50 | 50 | 80.6% | 23.1× | **10.6×** | 46% | 7.1× | 4.3× | 0.729 |
| l2 | none | 50 | 100.0% | 29.4× | **10.4×** | 35% | 9.0× | 4.1× | 0.730 |

## Shipped default, best and choice, over 5 seeds

*Best* = highest 2-D CATH-superfamily lift. *Choice* = highest among configurations whose global score on the grid seed is at least the shipped default's (0.716).

| configuration | 2-D CATH superfamily (mean, min–max) | 2-D EC sub-subclass (mean, min–max) | global (mean, min–max) |
|---|--:|--:|--:|
| l2 → PCA(100) → 15 nb (shipped) | 14.4× (14.1–14.9) | 5.1× (4.9–5.3) | 0.715 (0.711–0.720) |
| centre → no PCA → 5 nb (best) | 26.2× (25.8–26.4) | 7.8× (7.7–8.0) | 0.679 (0.676–0.683) |
| centre → no PCA → 10 nb (choice) | 22.9× (22.1–23.5) | 6.8× (6.7–6.9) | 0.718 (0.709–0.725) |

**Best (centre → no PCA → 5 nb) against the shipped default:**

- CATH superfamily, the label used to rank: worst seed 25.8× vs the default's best seed 14.9× — clear of seed noise.
- EC sub-subclass, not used to rank: 7.8× vs 5.1× — the gain carries over to a label the setting was not tuned on.
- Global structure: 0.679 (0.676–0.683) vs 0.715 (0.711–0.720) — every seed is below every seed of the default: the local gain is paid for with the global picture.

**Choice (centre → no PCA → 10 nb) against the shipped default:**

- CATH superfamily, the label used to rank: worst seed 22.1× vs the default's best seed 14.9× — clear of seed noise.
- EC sub-subclass, not used to rank: 6.8× vs 5.1× — the gain carries over to a label the setting was not tuned on.
- Global structure: 0.718 (0.709–0.725) vs 0.715 (0.711–0.720) — not below the default once seed spread is counted.

## Marginal means of 2-D CATH-superfamily lift

- prep: centre 16.2×, l2 15.4×
- PCA: none 17.6×, 50 12.9×, 100 14.9×, 200 17.8×
- neighbours: 5 21.2×, 10 18.2×, 15 15.7×, 30 12.6×, 50 11.5×
- global score by neighbours: 5 0.694, 10 0.715, 15 0.710, 30 0.719, 50 0.725
