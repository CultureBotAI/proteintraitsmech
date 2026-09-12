---
topic: microTrait direct ingest (HMM → rule → trait tables)
round: 1
date: 2026-09-11
question: >-
  microTrait was never ingested directly — it only reached the corpus as a
  flattened, grounding-free slice of the ENIGMA trait-onto-map catalogue
  (433,608 of 742,501 rows, zero ontology ids, 0 rows eligible for
  seed_traitontomap.py's EC-only filter). Can we ingest microTrait's own
  HMM → rule → trait model from the package, with its native groundings?
prior_round: none (new topic; protein-trait-sources-round1..3 never mention microTrait)
method: GitHub API + raw-file fetch of the package tables, PMC/Frontiers article, September 2026
---

# microTrait direct ingest — Round 1

New topic. Prior rounds (`protein-trait-sources-round1..3.md`) were checked with
an ignore-independent `grep -rli 'microtrait|karaoz|brodie' research/` and never
considered it. The only in-repo mentions are `download.yaml:739` and the
`seed_traitontomap.py` docstring, both listing "MicroTraits" as one of the tools
folded into trait-onto-map.

## Ranked findings

| # | Source | Fit (category) | Hier | Download / format | Licence | Rec |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | **microTrait rule tables** (`ukaraoz/microtrait` `data-raw/*.txt`) — 326 traits, 1,445 Boolean rules, 2,298 HMM rows with KEGG/EC/TCDB xrefs | FUNC_PATHWAY (composite guild traits), FUNC_TRANSPORT (substrate-uptake traits), FUNC_ENZYMATIC_ACTIVITY (single-enzyme rules), FUNC_ENVIRONMENTAL_RESPONSE (stress-tolerance traits) | ✅ 3 explicit granularity levels + colon-path names; 37 / 100 / 189 traits | pinned tag `v1.0.0` tarball; per-file raw TSV | **MIT** (`DESCRIPTION: License: MIT + file LICENSE`, © 2020 Ulas Karaoz) | ✅ **seed** |
| 2 | **microtrait-hmm** profile HMMs (`ukaraoz/microtrait-hmm`) — 1,864 `.hmm`, 1,595 seed `.faa`, 1,259 MSAs; `microtrait.hmmdb.gz` 63.9 MB | grounding only — the HMM is the sequence-level *definition* of each protein-family variable in a rule | n/a | `releases/download/latest/microtrait.hmmdb.gz` (the URL `prep.hmmmodels()` itself uses); per-family files in tree | ⚠️ **no LICENSE file in the repo** (GitHub reports `NONE`) | ⚠️ reference by name + `microtraithmm2dbxref.txt`; do not redistribute profiles until licence is stated |
| 3 | dbCAN subset used by microTrait (41 GH families, `inst/extdata/dbcan.selectids.txt`) | already covered — all 41 exist in `sequence/family/cazy/` | — | via dbCAN2 `download_file.php?file=dbCAN-HMMdb-V14.txt` | dbCAN (not needed; we have CAZy) | ↔ xref only |
| 4 | trait-onto-map's microTrait slice (`data/raw/traitontomap/trait_catalog.tsv`) | superseded by #1 | none | already local | MIT | ⛔ do not use — no ontology ids; 431,758 of 432,945 ids are per-gene instances |

## Detail & rationale

### What microTrait actually is, in our terms

microTrait (Karaoz & Brodie, *Front. Bioinform.* 2022, CC BY;
[PMC9580909](https://pmc.ncbi.nlm.nih.gov/articles/PMC9580909/)) maps a genome to
traits in three layers, each of which is a table in the package's `data-raw/`:

1. **Protein families as Boolean variables.** `microtrait_hmm.txt` — 2,298 rows,
   2,295 distinct HMM names. 2,232 carry a KEGG KO, 1,091 an EC number, 818 a
   TCDB id. The paper: "each protein family is a Boolean variable (i.e. equals 1 if
   detected, 0 otherwise)". Each name is a custom profile HMM built by
   `hmmbuild` from IMG/M seed sequences, with a trusted cutoff chosen by
   cross-validation against KEGG orthologs ("the smallest score that maximizes
   F-scores"). `microtrait_hmmsfromrules.txt` restricts to the 1,831 HMMs a rule
   actually references and carries the per-HMM F-score/TPR/FPR — 1,637 of 1,831
   have F ≥ 0.8.
2. **Rules as Boolean expressions over families and other rules.**
   `microtrait_rules.txt` — 1,445 rules, `name → ('a' & 'b') | ('c' …)`. Every
   quoted token resolves: 1,831 are HMM names, 755 are other rules (nesting), 0
   are unresolved. 936 `&`, 788 `|`, 3 `!`. Example:
   `arsenate->arsenite  ('arrA' & 'arrB')`; `iron reduction ('mtrA' | … | 'omcA')`.
3. **Traits as targets of rules.** `microtrait_traits.txt` — 326 traits with
   colon-path names (`Resource Acquisition:Substrate uptake:aromatic acid
   transport`), an explicit `granularity` 1/2/3 (37 / 100 / 189), a `type`
   (168 `count`, 158 `binary`), and a `strategy` (161 Resource Acquisition, 107
   Resource Use, 58 Stress Tolerance). `microtrait_rule2trait.txt` (975 rows:
   628 `count_by_substrate`, 235 `count`, 112 `binary`) maps rule → trait at
   each granularity; the 628 substrate rows resolve through
   `microtrait_substrate2rule.txt` (173 substrates → trait at 3 granularities).

Join integrity, measured on the tables: 975/975 rule2trait rules exist in
rules.txt; 271/271 trait names referenced exist in traits.txt; 0 traits are
orphaned. 498 of the 1,445 rules are intermediate (never mapped directly to a
trait) — they exist to be nested. 215 of the 628 substrate rows name a compound
list (`arginine;lysine;histidine`) with no substrate2rule entry, so those need a
split-and-lookup, not a straight join.

### Why this is a fit — and where the axis line falls

The **rule → HMM layer is a protein-trait class model** in exactly this
repository's sense: a rule is a named class defined by the presence of specific
protein families, and each family is defined at the sequence level by a profile
HMM. That satisfies the minimum bar (defined in terms of sequence elements) that
the trait-onto-map copy could not, because it stripped every grounding.

The **trait layer is mixed.** Substrate-uptake traits (`…:Substrate uptake:…`)
are transport capabilities → `FUNC_TRANSPORT`; enzymatic single-family rules
with an EC → `FUNC_ENZYMATIC_ACTIVITY`; composite guild traits (denitrification
steps, methanogenesis routes, hydrogenase groups, carbon fixation pathways) →
`FUNC_PATHWAY`; stress-tolerance traits → `FUNC_ENVIRONMENTAL_RESPONSE`. The
`Present`/`Absent` *values* seen in trait-onto-map are genome-level
observations, not classes, and must not be seeded; the class is the trait, the
genome's value is an instance. Organism-level phenotype semantics of these
traits (what the *organism* can do) belong to TraitMech/METPO; here we seed the
protein-family-defined capability and cross-link.

### Grounding overlap with the current corpus (measured)

| microTrait xref | distinct | already a record here | note |
| --- | ---: | ---: | --- |
| EC (complete, 4-level) | 618 | **596** in `function/enzymatic_activity/ec/` | direct `xrefs` / `parent_traits` anchors |
| TCDB | 809 ids | 12 exact; **99/99 at family level** (`x.y.z`) | our TCDB records are family-level; microTrait ids are subfamily/system-level — map to the family |
| dbCAN GH | 41 | **41/41** in `sequence/family/cazy/` | already covered |
| KEGG KO | 2,232 | no KO records in corpus | keep as `xrefs`, not anchors |

So a microTrait ingest is mostly *additive structure over records we already
have*: it supplies the Boolean composition (which families together constitute
a capability) and a three-level guild hierarchy that no current source gives us.

### Licence

- `ukaraoz/microtrait`: `DESCRIPTION` says `License: MIT + file LICENSE`;
  `LICENSE` is the R MIT template (`YEAR: 2020 / COPYRIGHT HOLDER: Ulas
  Karaoz`). GitHub's API reports `NOASSERTION` only because the two-line template
  is not self-describing. **MIT → CC0-compatible for derived records with
  attribution.** The rule tables live inside the package → covered.
- `ukaraoz/microtrait-hmm`: **no LICENSE file** (API: `NONE`). The profile HMMs
  and seed sequences are therefore all-rights-reserved by default. We do not need
  to redistribute them: the rule tables name families by string, and
  `data/microtraithmm2dbxref.txt` (1,595 rows: name → EC/TC, KEGG, description)
  is enough to ground each family to public identifiers. Flag, reference by URL,
  do not vendor.
- Paper: CC BY (verbatim: "This is an open-access article distributed under the
  terms of the Creative Commons Attribution License (CC BY)").

### Download route

The package pins a release: tag `v1.0.0` (2022-10-06),
`https://api.github.com/repos/ukaraoz/microtrait/tarball/v1.0.0`. A second tag
`kb` (2023-04-24) is the KBase-app branch. The default branch was last pushed
2026-05-29, so **fetch the pinned tag, not `master`**. Nine files under
`data-raw/` are the ingest inputs; raw URLs are
`https://raw.githubusercontent.com/ukaraoz/microtrait/v1.0.0/data-raw/<file>`.
All nine were fetched at `master` for this round and parsed cleanly as
tab-separated with a header row (`microtrait_ruleunwrapped.txt` has no header —
it is a debug expansion of `rules.txt` and is not needed).

The HMM database URL that `prep.hmmmodels()` hardcodes (`R/prep_hmmpackage.R:48`)
is `https://github.com/ukaraoz/microtrait-hmm/releases/download/latest/microtrait.hmmdb.gz`
(63,937,067 B). The `latest` tag is a floating release name (published
2021-11-15), so it cannot be release-pinned by URL alone — record the asset size
and a checksum in the `.fetch.json` sidecar if it is ever fetched.

### What a seeder would do (scope for the ingest issue)

- One `ProteinTraitRecord` per **rule that maps to a trait** (975 rule→trait
  rows over ~477 distinct mapped rules; the 498 intermediate rules become
  `parent_traits`/composition nodes only if a child needs them), identifier
  `microtrait:<rule-name>`, definition from the trait display name + the Boolean
  expression rendered in words, `xrefs` = the EC/TCDB/KEGG of every leaf family,
  `parent_traits` = the granularity-1/2 trait above it.
- One record per **trait** at granularities 1–3 (326), identifier
  `microtrait:trait/<slug>`, `parent_traits` from the colon path (measured: 49/56
  granularity-2 and 107/189 granularity-3 names have a colon-prefix ancestor at
  the level above; the rest attach to the nearest existing prefix — 172/189 do —
  or to the strategy root).
- The **HMM layer is not seeded**: each family name is recorded on the rule as a
  `representations` entry pointing at `microtrait-hmm/<name>.hmm` with the KEGG /
  EC / TCDB dbxrefs, and where an EC or TCDB family record already exists, that
  record is cross-linked rather than duplicated.
- Never emit `Present`/`Absent` or count values; never emit per-genome rows.

## Recommended next seeds (priority order)

1. **microTrait rule tables** — file a `candidate` block now (done in this PR),
   then an ingest issue scoped as above. Expected yield ≈ 326 trait records +
   ≈ 480 rule records, almost all `FUNC_PATHWAY` / `FUNC_TRANSPORT`, with EC/TCDB
   anchors for 596 + 99 of them and a hierarchy the corpus currently lacks.
2. **TCDB subfamily/system level** — microTrait's 809 TCDB ids land at
   subfamily/system depth where we hold only 12 exact records; if #1 is seeded,
   the family-level mapping loses specificity, which argues for re-seeding TCDB
   one level deeper first (separate decision; not a microTrait problem).
3. **Nothing from microtrait-hmm** until a licence is stated upstream.

## Sources

- microTrait package — https://github.com/ukaraoz/microtrait ·
  https://api.github.com/repos/ukaraoz/microtrait/tarball/v1.0.0 ·
  `data-raw/microtrait_{traits,rules,rule2trait,substrate2rule,hmm,hmmsfromrules,hmm-performance}.txt`
- microtrait-hmm — https://github.com/ukaraoz/microtrait-hmm ·
  https://github.com/ukaraoz/microtrait-hmm/releases/download/latest/microtrait.hmmdb.gz ·
  `data/microtraithmm2dbxref.txt`
- Karaoz U, Brodie EL. microTrait: A Toolset for a Trait-Based Representation of
  Microbial Genomes. Front Bioinform 2022; doi:10.3389/fbinf.2022.918853 —
  https://pmc.ncbi.nlm.nih.gov/articles/PMC9580909/
- `prep.hmmmodels()` source — https://raw.githubusercontent.com/ukaraoz/microtrait/master/R/prep_hmmpackage.R
- ENIGMA trait-onto-map (the indirect prior route) — https://github.com/enigma-org/trait-onto-map
