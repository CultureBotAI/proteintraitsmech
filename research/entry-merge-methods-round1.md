---
topic: methods to merge / reconcile equivalent entries within each trait category
date: 2026-07-03
question: >-
  Within a category, entries from different sources (Pfam vs InterPro vs CATH
  domain; EC vs Rhea reaction; MEROPS vs Pfam peptidase family) classify
  overlapping biology. What METHODS decide when two entries are the same trait
  (MERGE) vs near-equivalent (biolink:close_match) vs distinct — and how do the
  per-resource detection recipes drive that decision?
status: recommendation — tiered, Biolink-typed, detection-recipe-driven
relates_to: .claude/skills/merge-traits, data/methods/methods.yaml, research/schema-hierarchy-review-1.md
---

# Entry-merge methods — round 1

## 1. The problem & the governing insight

At 277k records, each category holds parallel entries for the *same biology*
from different sources — a domain seen by Pfam, InterPro, CATH, SMART, CDD and
NCBIfam; a reaction as EC and as Rhea; a peptidase family in MEROPS and Pfam.
The Codex review (`research/schema-hierarchy-review-1.md`) said: **keep the
source-native hierarchies, link near-equivalents with `biolink:close_match`,
reserve `biolink:same_as`/MERGE for unequivocal identity.** The existing
`merge-traits` skill already does the unequivocal tier (R1 exact-id, R2
exact-pattern) and flags C1–C3 for review; this extends it with *method-based*
equivalence detection.

**Governing insight:** two entries are the same trait **iff they detect the same
thing**. So merge/equivalence reduces to comparing the OUTPUTS of the per-
resource **detection recipes** (`data/methods/methods.yaml`) — which proteins
each signature matches, and where. That is precisely "method recipes per
resource and per entry": run/lookup each entry's detection method → compare.

## 2. Tiered merge methods (cheapest & most authoritative first)

### Tier 0 — Authoritative integration mappings (no compute; already partly in corpus)
The cheapest, highest-confidence signal is a source that has *already* asserted
equivalence:

- **[InterPro](https://academic.oup.com/nar/article/49/D1/D344/5958491) member-DB
  integration** — InterPro manually maps signatures from **Pfam, PROSITE, SMART,
  CATH-Gene3D, SUPERFAMILY, PANTHER, TIGRFAM (=NCBIfam), CDD, PIRSF, PRINTS**
  into shared InterPro entries (>90% integrated for most DBs). **Signatures that
  map to the same InterPro entry are near-equivalent** → `biolink:close_match`.
  Source: `interpro.xml` `<member_list>` (we already derive Pfam→InterPro via
  `pfam2interpro`; extend to every member DB). Note: CATH-Gene3D/SUPERFAMILY are
  integrated as the *homologous-superfamily* type (they match wider sets), so
  their InterPro link is superfamily-level, not exact.
- **EC ↔ Rhea** (`rhea2ec`) → `close_match` reaction (already have as mapped_xref).
- **MEROPS ↔ Pfam/InterPro** (`merops/interpro.txt`) → `close_match` peptidase family.
- **CDD** accessions embed their origin (pfam#####/COG/TIGR) → direct equivalence.
- **TCDB ↔ Pfam/InterPro** (TCDB families cite Pfam) → `close_match`.

Emit these as `trait_relations` (`predicate: biolink:close_match`,
`relation_source: <mapping>`). This links the *majority* of domain/family/site
and reaction entries without any computation.

### Tier 1 — Signature member-set overlap (run the detection recipe → compare hits)
For entries with no Tier-0 mapping, compare **which UniProtKB proteins each
matches**. The member set comes straight from the detection recipe — or, for
free, from the **UniProt members query we already expose** (`uniprotMembersUrl`:
`xref:pfam-PF…`, `xref:interpro-IPR…`, `xref:gene3d-…`, `xref:supfam-SSF…`).

- Fetch each entry's member accession set `M(e)` (batched, `format=list`).
- For a candidate pair (same category) compute **Jaccard** `J = |A∩B| / |A∪B|`
  and **containment** `C = |A∩B| / min(|A|,|B|)`.
  - `J ≥ 0.90` **and reciprocal** → **MERGE candidate** (same trait).
  - `C ≥ 0.90`, `J` lower → **containment**: `biolink:narrow_match` / `member_of`
    (a subfamily within a family).
  - `0.5 ≤ J < 0.9` → `biolink:close_match` (related, keep both).
  - `< 0.5` → distinct.
- Blocking to avoid O(n²): only compare entries that share ≥1 member, or share a
  Tier-0/Tier-4 anchor.

### Tier 2 — Region/coordinate overlap on shared members (localized features)
For domains / sites / motifs / repeats, member overlap isn't enough — two
distinct domains can co-occur in the same proteins. On proteins both match,
require **reciprocal coordinate overlap ≥ 0.8** of the annotated ranges (from the
recipe's output or UniProt features) to confirm "same region".

### Tier 3 — Structural equivalence (STRUCT_FOLD / _TOPOLOGY / _SUPERFAMILY / _DOMAIN)
CATH, SCOPe, ECOD and TED classify the same folds under different trees; sequence
member-overlap is weak here. Use **structure comparison** of representatives:

- **Foldseek** / DALI between each entry's representative domain structure.
- Thresholds: **TM-score ≥ 0.5 → same fold** (`close_match` at fold level);
  **≥ 0.7 → same superfamily**. Recipe: `foldseek easy-search rep_A.pdb rep_B.pdb`.
- Links CATH-topology ↔ SCOP-fold ↔ ECOD-F-group ↔ TED-fold as `close_match`.

### Tier 4 — Ontology-anchor identity (functional categories)
A shared *specific* grounding is strong functional equivalence (refines the
skill's C2 rule): same **EC leaf**, same **Rhea**, same **MOD**, same
**ChEBI participant set**, same **GO** (specific, not generic like GO:0005515).
Two `FUNC_ENZYMATIC_ACTIVITY` entries with the same EC+Rhea → `close_match`/MERGE.

### Tier 5 — Label / definition semantics (review-only)
Normalized-label match across sources + optional embedding similarity — the
skill's C3 rule. **Never auto-merges**; surfaces candidates only.

## 3. Decision policy (Biolink-typed, conservative)

| Signal | Edge / action |
|---|---|
| Exact id (R1) / exact pattern (R2) | **MERGE** — fold into one record (existing skill) |
| Tier-0 mapping **and** Tier-1 `J ≥ 0.9` reciprocal (**and** Tier-2 for localized) | **MERGE candidate** → curator confirms; loser → `DEPRECATED` + xref |
| Curated strict identity | `biolink:same_as` (rare) |
| Tier-0 mapping, or `0.5 ≤ J < 0.9`, or Tier-3 structural equivalence | **`biolink:close_match`** (DEFAULT — keep both, link) |
| Containment (`C ≥ 0.9`) | `biolink:narrow_match` / `biolink:member_of` |
| Below thresholds | leave distinct / review |

Guardrails (from the skill + Codex): **never auto-MERGE across sources on a
mapping alone** — require member/region/structure agreement; **default to
close_match**, never destroy a source-native hierarchy; **log every dropped or
downgraded candidate**. `xrefs` remain associative, not identity.

## 4. Per-category method matrix

| Category(s) | Sources in play | Primary method(s) | Default cross-source edge |
|---|---|---|---|
| STRUCT_DOMAIN, SEQ_MOTIF, SEQ_REPEAT, SEQ_CONSERVATION, site cats | Pfam, InterPro, PROSITE, SMART, CDD, NCBIfam, MEROPS | Tier 0 (InterPro/MEROPS mapping) → Tier 1 member overlap → Tier 2 region | close_match; MERGE only on J≥0.9+region |
| STRUCT_FOLD, _TOPOLOGY, _ARCHITECTURE, _HOMOLOGOUS_SUPERFAMILY, _CLASS | CATH, SCOPe, ECOD, TED, Gene3D/SUPERFAMILY | Tier 3 structural (Foldseek/TM-score) + Tier 1 | close_match at matching rank |
| FUNC_ENZYMATIC_ACTIVITY | EC (ExPASy), Rhea, MEROPS, GO-MF | Tier 4 anchor (EC↔Rhea) + Tier 0 | close_match; MERGE on same EC+Rhea |
| FUNC_ORTHOLOG_GROUP | COG, KOG (CDD) | Tier 1 member overlap + eggNOG mapping | close_match |
| FUNC_TRANSPORT | TCDB | Tier 0 (TCDB↔Pfam) + Tier 1 | close_match |
| SEQ_DISORDER | DisProt (IDPO), IDEAL | shared **IDPO term** (already unified by the pivot) | already class-level; no merge needed |
| FUNC_PATHWAY | Reactome | Reactome↔GO-BP anchor | close_match |
| FUNC_RESISTANCE | ARO | ARO↔drug-ChEBI + AMR-gene mapping | close_match |
| MIXED_STRUCTURAL_REPEAT | RepeatsDB | Tier 3 structural | close_match |
| chemistry participants | ChEBI | ChEBI id identity | same_as |

## 5. How the detection recipes drive it (the connection requested)

The merge computation for Tiers 1–3 **is** the detection recipe applied per
entry, then compared:

- **Tier 1/2** run/lookup the *sequence* recipe (`hmmsearch` for Pfam/NCBIfam,
  `ps_scan` for PROSITE, `rpsblast` for CDD, `InterProScan` end-to-end) against
  a reference proteome (Swiss-Prot) → per-entry hit set + coordinates. The
  cheapest realization needs **no local runs**: reuse the UniProt members query
  (`uniprotMembersUrl`) which returns each entry's member accessions directly.
- **Tier 3** runs the *structure* recipe (`foldseek easy-search`) on the entries'
  representative domains.
- **Tier 4** reads the anchors already stored (EC/Rhea/ChEBI/MOD/GO).

So `data/methods/methods.yaml` is not only "how to detect a trait" but also the
engine for "are two traits the same" — comparing recipe outputs per entry.

## 6. Rollout (extends the merge-traits skill)

1. **Phase 1 — authoritative links (cheap, no compute).** Parse
   `interpro.xml <member_list>` → emit `trait_relations` `biolink:close_match`
   from each member-DB signature to its InterPro entry (all DBs, not just Pfam);
   add EC↔Rhea, MEROPS↔Pfam/InterPro, TCDB↔Pfam. A `build_equivalence.py`
   overlay (like `migrate_trait_relations.py`). This links the majority.
2. **Phase 2 — member overlap.** For unlinked entries per category, fetch member
   sets via the members recipe (batched, cached), compute J/C with blocking,
   propose MERGE (J≥0.9) / close_match. New rules in `analyze-merges`
   (**M1 integration-mapping, M2 member-overlap, M3 region-overlap**).
3. **Phase 3 — structural.** Foldseek over CATH/SCOPe/ECOD/TED representatives →
   fold/superfamily close_match (**M4 structural**).
4. **Governance.** MERGE tier auto-applies only for R1/R2 + (mapping ∧ J≥0.9);
   everything else is close_match or review. Re-validate + confirm the record
   total drops only by confirmed MERGE losers.

## 7. What NOT to do
- Do **not** collapse Pfam/InterPro/CATH/SCOP/ECOD into one record on a shared
  InterPro mapping alone — link with `close_match`, keep the source trees.
- Do **not** use generic anchors (GO:0005515 protein binding, SO:0001067) as
  identity — they group thousands of unrelated entries (the skill's existing
  false-positive guard).
- Do **not** treat `xrefs`/`mapped_xrefs` as identity assertions.

## 8. Round-1 implementation status (2026-07)

| Phase | Script / recipe | Output | Status |
|---|---|---|---|
| **1** InterPro member integration | `build_equivalence.py` · `just build-equivalence` | `data/equivalence/cross_source.tsv` — **24,299** `close_match` edges (Pfam 17,970 / CDD 3,749 / PROSITE 2,334 / NCBIfam 246 → InterPro) | **done, in browser** (bidirectional `eq` field) |
| **2** Member-set overlap | `build_member_overlap.py` · `just build-member-overlap` | `data/analysis/member_overlap_candidates.yaml` (review) + optional `member_overlap.tsv` (`--emit-edges`) | **tooling done; ran STRUCT_DOMAIN ×500 sample** |
| **3** Structural (Foldseek) | `build_structural_equivalence.py` · `just build-structural-equivalence` | `structural_reps.tsv` (**13,860** TED reps derived) → `structural.tsv` | **pipeline done; needs `foldseek` + AF downloads to execute** |

**Phase-2 finding — the localized-feature trap is real.** The top member-overlap
candidate was `IPR000536` *(nuclear-receptor ligand-binding domain)* vs `PF00105`
*(C4 zinc finger / DNA-binding domain)* at **J = 0.94** — two *distinct* domains
that co-occur in nuclear receptors, not one trait. This confirms §2 Tier-2:
member overlap alone must **not** assert equivalence for localized categories
(domains/sites/motifs/repeats). So Phase 2 defaults to a **review-candidates
file**; browser edges are emitted (`--emit-edges`) only for *non-localized*
pairs. **Tier-2 is now implemented** (`verify_region_overlap.py`): it pulls each
signature's InterPro match coordinates on the shared proteins and requires
reciprocal residue overlap. On the 10-candidate sample it **rejected 8** as
co-occurring/disjoint (the LBD/DBD case: PF00105 at 558-626 vs IPR000536 at
669-900) and **confirmed 2** genuine same-region equivalences (PAN domain
IPR000177↔PF00024; IPR000381↔PF00019), which become real browser edges. Tier-2
is what turns Phase-2 candidates into assertable equivalence.

**Phase-3 note.** The representative manifest is auto-derived from TED records
(each encodes an AlphaFold model + domain chopping). Executing the Foldseek
all-vs-all needs `foldseek` on PATH plus AlphaFold model downloads (heavy); the
driver detects a missing `foldseek` and prints run instructions. Cross-source
structural links (CATH↔SCOPe↔ECOD↔TED) additionally need those sources' domain
representatives dropped into the same manifest.

## Sources
- [InterPro: 20 years on (NAR 2021)](https://academic.oup.com/nar/article/49/D1/D344/5958491) · [member databases](https://interpro-documentation.readthedocs.io/en/latest/databases.html) · [homologous-superfamily entry type](https://proteinswebteam.github.io/interpro-blog/2017/10/03/Homologous-superfamily/)
- [Foldseek (structure search, TM-score)](https://www.nature.com/articles/s41587-023-01773-0) · Rhea↔EC (rhea2ec) · MEROPS↔InterPro
- Existing: `.claude/skills/merge-traits` (R1/R2/C1–C3), `data/methods/methods.yaml`, `research/schema-hierarchy-review-1.md`
