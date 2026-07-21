---
topic: causal-graphs
round: 6
date: 2026-07-21
target: aro/FUNC_RESISTANCE — curator promotion pass on the KPC β-lactamase family (ARO:3000059, 232 records)
prior_round: causal-graphs-round5.md
method: family-level verbatim evidence (PMID:28388065, KPC-2 mechanism) applied across the family; audit-graphs --strict to track
---

# Causal graphs — Round 6: curator promotion pass (KPC family, 232 drafts → REVIEWED)

Round 5 auto-drafted a scaffold graph on every ARO gene; this round demonstrates the
**curator promotion pass** that turns drafts into gold **a family at a time**. The
insight: every member of one AMR gene family inherits the *same* mechanism + drug
classes, so **one curated set of verbatim snippets promotes the whole family**.

## Target: KPC β-lactamase (ARO:3000059, 232 members)

The flagship class A serine carbapenemase — clinically the most important
carbapenemase, and its mechanism is the *same* Ser70 acyl-enzyme chemistry curated
atomically in round 1 (MCSA:2). Promoting it links the resistance-determinant view
to the atomic mechanism for 232 records at once.

## Family evidence (PMID:28388065, KPC-2 mechanism — verbatim)
- class + threat: "The Klebsiella pneumoniae carbapenemase (KPC) class A β-lactamase
  poses a serious threat to nearly all β-lactam antibiotics."
- spectrum: "KPC-2 is the most prevalent carbapenemase in the United States and it
  has been termed the 'versatile β-lactamase' due to its large and shallow active
  site, allowing it to efficiently hydrolyze virtually all β-lactam antibiotics."
- mechanism: "The attack of Ser70 on the substrate β-lactam carbonyl results in a
  covalent acyl-enzyme complex. Subsequently, the catalytic water, activated by
  Glu166, cleaves the acyl-enzyme bond, leading to the formation of the hydrolyzed
  product." (← the same Ser70/Glu166 acyl-enzyme mechanism as MCSA:2)

## Tool — `scripts/promote_family_drafts.py` + `just promote-family-drafts`
For a given family ARO id (with curated snippets in `FAMILY_SNIPPETS`), it finds
every draft under that family, **regenerates the `resistance-draft` graph as a
curated `resistance` graph** whose edges carry a verbatim `snippet` (chosen by edge
role + the mechanism/drug the edge points at) and a real PMID `reference`, flips
`mapping_status: SEEDED → REVIEWED`, and appends a `curation_history` event.
Idempotent (skips already-curated records); extend `FAMILY_SNIPPETS` to promote more
families.

`just promote-family-drafts --family ARO:3000059 --apply`

## Result
| | count |
|---|--:|
| KPC drafts promoted → REVIEWED (9/9 edges snippet-cited each) | **232** |
| — schema `just validate` | clean |
| — `just audit-graphs --strict` per record | 0 errors, snippet-complete |

**Curation tracker (ARO causal graphs, corpus-wide):**
| state | records |
|---|--:|
| curated (REVIEWED, snippet-complete) | **236** (232 KPC + GOB-10/MdfA/ErmB/tet(M)) |
| remaining auto-drafts (SEEDED, snippet-pending) | 7,163 |

`grep -rl "graph_id: resistance-draft"` vs `"graph_id: resistance"` is the running
tracker; `just audit-graphs --strict` flags exactly the edges still lacking a snippet.

## The pattern, proven
- **Round 4** enriched the records (relations) → **round 5** auto-drafted scaffolds
  → **round 6** promotes them per family with shared evidence. A curator now clears
  the 7,163-draft backlog family-by-family, not gene-by-gene: one paper, one
  `FAMILY_SNIPPETS` entry, one `--apply` promotes a whole family (KPC = 232 records
  from a single mechanism paper).
- **Family-level inference is explicit:** the graph description states the evidence
  is the family archetype's and the members inherit it — standard AMR-variant
  curation, auditable.

## Open questions / next
- **Next families:** TEM (250), SHV (241), CTX-M (273), OXA (157) are the next
  high-value class-A/D β-lactamase families; each needs one `FAMILY_SNIPPETS` entry.
  Non-β-lactamase families (qnr target protection, MCR colistin, MFS/RND efflux)
  broaden the mechanism coverage.
- **Snippet-by-role granularity:** the promoter maps snippets by edge role + target
  grounding; a family with a genuinely distinct per-variant phenotype (e.g. KPC
  ceftazidime-avibactam-resistant variants) would need variant-specific evidence,
  not the family default — a refinement flag for the curator.
