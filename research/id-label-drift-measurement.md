# What an id↔label gate would actually find (#493, for #484 item 5)

`just measure-id-label-drift`, full corpus, offline against `data/raw`.

## The headline

```
grounded+labelled causal nodes : 342,631
  database prefixes, no ontology: 150,377   UniProtKB, RHEA, EC, CATH, PROSITE, MCSA …
  ontology prefix, no local source:   171   ECOD 111, NCBIfam 60
  CHECKED                       : 192,083

   77,122  (40.2%)  MISMATCH
   58,887  (30.7%)  OK_CANONICAL
   56,044  (29.2%)  OK_SYNONYM
       30  ( 0.0%)  ID_NOT_FOUND
```

| prefix | checked | canonical | synonym | mismatch | not found |
|---|---:|---:|---:|---:|---:|
| CHEBI | 134,675 | 13,236 | 55,962 | **65,447** | 30 |
| ARO | 33,393 | 33,290 | — | 103 | 0 |
| GO | 24,015 | 12,361 | 82 | **11,572** | 0 |

## Turning that gate on as-is would be a mistake

77,122 findings is not a backlog, it is noise — and #493 predicted exactly this ("a gate whose failures nobody can act on"). The 40.2% is **three unrelated problems** that a canonical-label check cannot tell apart.

**1. CHEBI — notation, not semantics.** The overwhelming majority. Same chemical, different rendering:

| ours | CHEBI's |
|---|---|
| `FMNH2` | `FMNH<small><sub>2</sub></small>(2−)` |
| `H(+)` | `hydron` |
| `17beta-hydroxy-3,19-dioxo-5alpha-androstanone` | `19-oxo-5α-dihydrotestosterone` |

ASCII-for-Unicode, markup, and charge notation. Nothing is wrong. CultureMech hit this and built `label_waived_keys` for it — slots whose labels are curator-intended, exempt from canonical matching but **still id-existence checked**.

**2. ARO — deliberate elaboration.** 103 of 33,393, and they read as curation, not error:

```
ARO:3004802   ours = 'GOB-10 (subclass B3 metallo-β-lactamase determinant)'
              ARO  = 'GOB-10'
ARO:0010000   ours = 'H+-coupled multidrug efflux (antibiotic efflux)'
              ARO  = 'antibiotic efflux'
```

A gloss added in parentheses so the node reads standalone inside a graph. ARO is otherwise the cleanest prefix in the corpus: **99.7% canonical**.

**3. GO — the one place with real errors.** Some GO labels name a *different concept*, not a different rendering:

```
GO:0016817   ours = 'protein-synthesizing GTPase (elongation factor Tu) activity'
             GO   = 'hydrolase activity, acting on acid anhydrides'
GO:0042132   ours = 'enzymatic activity EC 3.1.3.11'          ← a placeholder, not a label
             GO   = 'fructose 1,6-bisphosphate 1-phosphatase activity'
```

The first is a grounding that points at a parent class three levels too general. That is a defect worth finding, and it is invisible underneath 65,447 CHEBI notation differences.

## Recommended gate

**Not canonical-label matching.** Two checks instead, both actionable:

1. **ID existence** — `ID_NOT_FOUND`, currently **30**. Small, unambiguous, gate at that ceiling with an identity baseline (a ceiling alone masks a swap, #411).
2. **Unknown prefix** — a prefix in neither `adapters` nor `ignored_prefixes` is an error, so `CHBEI:` fails instead of passing silently. Currently 0 after classifying the 171 `NO_SOURCE` (ECOD, NCBIfam) as database prefixes.

Configure the causal-node `label` slot as **label-waived**, which is precisely the vendored validator's existing concept and needs no fork.

**GO's semantic mismatches deserve their own issue**, scoped as "a grounding whose label names a different concept", not as label drift. The signal is real; the frame is wrong.

## Scope note

Only `causal_graphs[].nodes[]` carries an id *and* a label. `parent_traits` is a bare CURIE list; `trait_relations` and `mapped_xrefs` carry `object:` with no label. There is no correspondence to check there — not deferred, absent.

Local and offline: `aro.obo`, `go.obo`, CHEBI `compounds.tsv.gz`/`names.tsv.gz`. No OAK download, no network — but `data/raw` is gitignored, so like `audit-reproducible` this is a local gate, not a CI one.
