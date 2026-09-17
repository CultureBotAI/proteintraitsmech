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
| 1 | **microTrait rule tables** (`ukaraoz/microtrait` `data-raw/*.txt`) — 271 distinct traits, 1,445 Boolean rules (947 listed in rule2trait; 841 reach a trait), 2,298 HMM rows with KEGG/EC/TCDB xrefs | FUNC_PATHWAY (composite guild traits), FUNC_TRANSPORT (substrate-uptake traits), FUNC_ENZYMATIC_ACTIVITY (single-enzyme rules), FUNC_ENVIRONMENTAL_RESPONSE (stress-tolerance traits) | ✅ colon-path names give 222/271 an ancestor trait; 3 reporting levels (37 / 100 / 189 traits shown at granularity 1/2/3) | seven per-file raw TSVs at the pinned `v1.0.0` ref | **MIT** (`DESCRIPTION: License: MIT + file LICENSE`, © 2020 Ulas Karaoz) | ✅ **seed** |
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
3. **Traits as targets of rules.** `microtrait_traits.txt` — 326 rows, **271
   distinct traits** (#684). A trait has a colon-path name (`Resource
   Acquisition:Substrate uptake:aromatic acid transport`), a `type` (121
   `count`, 150 `binary`) and a `strategy` (110 Resource Acquisition, 103
   Resource Use, 58 Stress Tolerance). The `granularity` column is a
   *reporting level*, not a partition: the same trait is listed once per level
   it is shown at — 224 traits at one level, 39 at two, 8 at all three — so
   37 / 100 / 189 traits appear at granularity 1 / 2 / 3, and the finest level a
   trait reaches is 1 for 26, 2 for 56, 3 for 189. `microtrait_rule2trait.txt`
   (975 rows: 628 `count_by_substrate`, 235 `count`, 112 `binary`) lists 947
   distinct rules. Direct rows name traits at each level; the 628 substrate
   rows instead require a join through `microtrait_substrate2rule.txt` (173
   substrates → trait at 3 levels). A listed rule need not have a successful
   trait mapping.

Join integrity, measured on the tables: 975/975 rule2trait rules exist in
rules.txt; 271/271 trait names referenced exist in traits.txt; every one of the
271 traits is reachable from at least one rule (directly, or via a split of the
`;`-joined substrate list). Of the 1,445 rules, 498 are absent from
rule2trait; the other 947 are listed there, but only **841 reach at least one
trait** after the join. The remaining **106 rules have no resolved trait**.

The 215 exact substrate misses comprise **110 compound-list rows** (such as
`arginine;lysine;histidine`) and **105 singleton rows**. Splitting each list
still leaves 26 unknown substrate names across 114 rows, all marked
`development`: 106 rows resolve to no trait and 8 resolve only partially.
For example, line 3 of the pinned `microtrait_rule2trait.txt` names rule `aaeB`,
substrate `hydroxybenzoate`, three empty trait columns, and version
`development`; `hydroxybenzoate` has no substrate-table entry. All production
rows resolve fully. The audit by `microtrait_trait-version` is:

| Version | Rows | Distinct listed rules | Rules reaching a trait | Rules reaching no trait | Rows with unknown substrates |
| --- | ---: | ---: | ---: | ---: | ---: |
| production | 697 | 669 | 669 | 0 | 0 |
| development | 278 | 278 | 172 | 106 | 114 |
| all | 975 | 947 | 841 | 106 | 114 |

Reproduce the join using Python's standard-library `csv.DictReader` on the
pinned TSVs: collect each row's nonempty `microtrait_trait-name1..3`, split
`microtrait_rule-substrate` on `;` for `count_by_substrate` rows, and union the
trait names of matching substrate keys. Retain missing tokens separately and
group by rule name and version. This minimal audit, run with the files under
`data/raw/microtrait/`, prints `947 841 106 26`:

```python
import csv
from pathlib import Path

root = Path("data/raw/microtrait")
def read(name):
    with (root / f"microtrait_{name}.txt").open(newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))
def targets(row):
    return {row[f"microtrait_trait-name{i}"] for i in (1, 2, 3)
            if row[f"microtrait_trait-name{i}"]}

substrates = {row["microtrait_substrate-name"]: row
              for row in read("substrate2rule")}
mapped, unknown = {}, set()
for row in read("rule2trait"):
    found = targets(row)
    if row["microtrait_rule-type"] == "count_by_substrate":
        for token in row["microtrait_rule-substrate"].split(";"):
            if token in substrates:
                found.update(targets(substrates[token]))
            else:
                unknown.add(token)
    mapped.setdefault(row["microtrait_rule-name"], set()).update(found)
print(len(mapped), sum(bool(v) for v in mapped.values()),
      sum(not v for v in mapped.values()), len(unknown))
```

Hierarchy, measured over the 271 distinct names using the colon path alone:
222 have an ancestor among the traits and 204 have their immediate parent
present; the 49 roots (30 at depth 3, 18 at depth 4, 1 at depth 2 — e.g.
`Resource Acquisition:Substrate assimilation:N compounds`) attach to their
strategy.

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

The package has two release tags: `v1.0.0` (2022-10-06) and `kb` (2023-04-24,
the KBase-app variant). The default branch was last pushed 2026-05-29 and is 28
commits ahead of `v1.0.0`, so **fetch at the pinned tag, not `master`**. The
ingest inputs are seven per-file raw URLs (#685 — one block per file, matching
every other GitHub-hosted block in `download.yaml`, and a stable byte artefact
for `fetch_source.py --sha256`, which a GitHub-generated archive is not):
`https://raw.githubusercontent.com/ukaraoz/microtrait/v1.0.0/data-raw/microtrait_{traits,rules,rule2trait,substrate2rule,hmm,hmmsfromrules,hmm-performance}.txt`.
Verified for this round: all seven, plus `LICENSE`, fetched at `refs/tags/v1.0.0`
are **byte-identical** to the `master` copies the measurements above were made
on (the 28 newer commits touch other `data-raw/` files), and `DESCRIPTION` at
the tag carries the same `License: MIT + file LICENSE`. Each parses as
tab-separated with a header row. `microtrait_ruleunwrapped.txt` has no header —
it is a debug expansion of `rules.txt` — and `microtrait_hmm_names_fromrules.txt`
duplicates `hmmsfromrules.txt`; neither is needed.

The HMM database URL that `prep.hmmmodels()` hardcodes (`R/prep_hmmpackage.R:48`)
is `https://github.com/ukaraoz/microtrait-hmm/releases/download/latest/microtrait.hmmdb.gz`
(63,937,067 B). The `latest` tag is a floating release name (published
2021-11-15), so it cannot be release-pinned by URL alone — record the asset size
and a checksum in the `.fetch.json` sidecar if it is ever fetched.

### What a seeder would do (scope for the ingest issue)

- One `ProteinTraitRecord` per **accepted rule with a verified trait mapping**.
  The 947 distinct names in `rule2trait.txt` (#686) are listed rules; 841 have
  at least one resolved mapping, including 8 with unresolved substrate tokens.
  Preserve the version, select an explicit production/development policy, and
  quarantine all 114 rows with unknown substrates for review. The 106 rules
  with no resolved trait must not be counted as mapped-rule candidates. The
  498 rules absent from rule2trait become composition nodes only if a child
  needs them. Identifier
  `microtrait:<rule-name>`, definition from the trait display name + the Boolean
  expression rendered in words, `xrefs` = the EC/TCDB/KEGG of every leaf family,
  `parent_traits` = the trait(s) the rule maps to.
- One record per **distinct trait** (271, not one per reporting level),
  identifier `microtrait:trait/<slug>`, `parent_traits` from the colon path:
  204 have their immediate parent among the traits, 18 more have a higher
  ancestor, and the 49 roots attach to their strategy (Resource Acquisition /
  Resource Use / Stress Tolerance). The granularity levels a trait is reported
  at are recorded as metadata, not as separate records.
- The **HMM layer is not seeded**: each family name is recorded on the rule as a
  `representations` entry pointing at `microtrait-hmm/<name>.hmm` with the KEGG /
  EC / TCDB dbxrefs, and where an EC or TCDB family record already exists, that
  record is cross-linked rather than duplicated.
- Never emit `Present`/`Absent` or count values; never emit per-genome rows.

## Recommended next seeds (priority order)

1. **microTrait rule tables** — file the `candidate` blocks now (done in this
   PR), then an ingest issue scoped as above. The tables contain **271 distinct
   traits** and **841 rules reaching at least one trait**, of which 669 are
   production and 172 development (including 8 only partially resolved).
   These are reachability counts; accepted record yield depends on the version
   policy, review of unresolved rows, and any needed composition nodes. The
   candidates are almost all `FUNC_PATHWAY` / `FUNC_TRANSPORT`, with EC anchors
   already in the corpus for 596 of the 618 EC numbers the families carry,
   family-level TCDB anchors for all 99 TCDB families, and a hierarchy the
   corpus currently lacks.
2. **TCDB subfamily/system level** — microTrait's 809 TCDB ids land at
   subfamily/system depth where we hold only 12 exact records; if #1 is seeded,
   the family-level mapping loses specificity, which argues for re-seeding TCDB
   one level deeper first (separate decision; not a microTrait problem).
3. **Nothing from microtrait-hmm** until a licence is stated upstream.

## Sources

- microTrait package — https://github.com/ukaraoz/microtrait ·
  https://raw.githubusercontent.com/ukaraoz/microtrait/v1.0.0/data-raw/ ·
  `microtrait_{traits,rules,rule2trait,substrate2rule,hmm,hmmsfromrules,hmm-performance}.txt` ·
  https://github.com/ukaraoz/microtrait/blob/v1.0.0/DESCRIPTION
- microtrait-hmm — https://github.com/ukaraoz/microtrait-hmm ·
  https://github.com/ukaraoz/microtrait-hmm/releases/download/latest/microtrait.hmmdb.gz ·
  `data/microtraithmm2dbxref.txt`
- Karaoz U, Brodie EL. microTrait: A Toolset for a Trait-Based Representation of
  Microbial Genomes. Front Bioinform 2022; doi:10.3389/fbinf.2022.918853 —
  https://pmc.ncbi.nlm.nih.gov/articles/PMC9580909/
- `prep.hmmmodels()` source — https://raw.githubusercontent.com/ukaraoz/microtrait/master/R/prep_hmmpackage.R
- ENIGMA trait-onto-map (the indirect prior route) — https://github.com/enigma-org/trait-onto-map
