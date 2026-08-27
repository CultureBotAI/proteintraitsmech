# What an id↔label gate would actually find (#493, for #484 item 5)

`just measure-id-label-drift`, full corpus, offline against `data/raw`.

**This document has been corrected twice by review. Both corrections are recorded here
rather than silently applied, because both were the measurement lying, not the corpus.**

## The numbers

```
grounded+labelled causal nodes : 342,631
  database prefixes, no ontology: 144,749   UniProtKB, RHEA, EC, CATH, PROSITE, MCSA …
  CHECKED                       : 197,882

  107,493  (54.3%)  OK_SYNONYM
   59,143  (29.9%)  OK_CANONICAL
   31,216  (15.8%)  MISMATCH
       30  ( 0.0%)  ID_NOT_FOUND
```

| prefix | checked | canonical | synonym | mismatch | not found |
|---|---:|---:|---:|---:|---:|
| CHEBI | 134,675 | 13,236 | 107,411 | 13,998 | 30 |
| ARO | 33,393 | 33,290 | — | 103 | 0 |
| GO | 24,015 | 12,361 | 82 | **11,572** | 0 |
| `proteintraitsmech` | 5,799 | 256 | — | **5,543** | 0 |

## Correction 1 — the first version's headline was an artifact of its own bug

It reported **77,122 mismatches (40.2%)** and concluded "that is not a backlog, it is noise".
The noise was the tool's. `data/raw/chebi/names.tsv.gz` — the file `load_chebi` already
opens — has an **`ascii_name` column at position 8** that the first version never read.
ChEBI keeps the markup form in `name` and the plain form in `ascii_name`, and this corpus
writes the plain one:

```
CHEBI:15378   name = H<small><sup>+</small></sup>      ascii_name = H(+)
```

`H(+)` was the flagship example of "notation drift" in the first write-up. It was in the
file, in a column one line away from the one being read. Reading it drops CHEBI's mismatch
from 65,447 to 13,998 and the headline from 40.2% to **15.8%**.

The lesson is not "check your columns". It is that the first version produced a *verdict* —
"turning this gate on would be a mistake" — from a number it had inflated ~3×, and the
verdict read as measured fact.

## Correction 2 — "only one surface has pairs" was wrong, and the census that said so was
gated on an unrelated condition

The first version claimed `causal_graphs[].nodes[]` is the only surface with an id *and* a
label, and called the alternatives "not deferred, absent". Measured:

```
409,005  canonical_examples.protein_id + protein_label   (UniProtKB — a database)
381,406  canonical_examples.taxon_id  + taxon_label      (NCBITaxon — an ontology)
```

That is **2.3× the surface this document measures**, and `taxon_id` is ontology-prefixed.
Neither is checked here — UniProtKB has no canonical ontology label, and this repo has no
local NCBITaxon dump — but "we did not measure this" and "there is nothing here" must not
print the same way.

Worse, the census that first reported these as 24,857 sat **inside the `grounding:`
prefilter**, so it only counted records that also happened to carry a causal graph — a 16×
under-count produced by gating a census on an unrelated condition. Same shape as the
prefilter bugs in #364 and #462, in the code written to measure a surface honestly.

## What the 15.8% actually is

**CHEBI (13,998)** — the residual after `ascii_name`. Markup, Greek-letter folding, and
trailing curator glosses (`H(+) (outside the membrane)`). Mostly notation, but not
entirely: `CHEBI:17860` is labelled `2-KETO-DEOXY-GALACTOSE` where CHEBI says
`6-phospho-2-dehydro-3-deoxy-D-galactonic acid` — a different compound. So "notation, not
semantics" is right for the great majority and is **not** safe as a blanket waiver
justification.

**ARO (103 of 33,393)** — deliberate glosses so a node reads standalone in a graph:
`'GOB-10 (subclass B3 metallo-β-lactamase determinant)'` against ARO's `'GOB-10'`. ARO is
**99.7% canonical**, the cleanest prefix in the corpus. Note these are the *same
phenomenon* as CHEBI's trailing glosses; one normalisation rule clears both.

**GO (11,572)** — and this is **not 11,572 findings**. Two patterns are 93.7% of it:
7,395 are the single pair `GO:0046677` labelled `antibiotic resistance phenotype`
(GO: `response to antibiotic`), and 3,443 are the stub `enzymatic activity EC x.x.x.x`.
The remaining ~734 is the tail worth reading. Filed as **#503**.

**`proteintraitsmech` (5,543 of 5,799 — 95.6%)** — new in the corrected run. These
groundings point at *this corpus*, so their labels are checkable against the records' own
`label:` slots, e.g. node `GLYOXYLIC ACID-binding site` against record `GLV-binding site`.
The first version classified this prefix as "a database" and skipped it. **It needs no
`data/raw` at all**, which makes it the only part of this measurement that could run in CI.

## Recommended gate

1. **Corpus-internal groundings** (`proteintraitsmech:`) — 5,543 mismatches, no external
   dependency, CI-able. The highest-value check and the one the first version discarded.
2. **ID existence** — 30 today, but see the caveat: several are absent from the local ChEBI
   dump while being current ChEBI terms, so part of the 30 is a property of a gitignored
   file rather than of the corpus. Pin only after separating those.
3. **Stub labels** — `enzymatic activity EC …` (3,443) and `ligand <PDB code>` (2,825) are
   regex-detectable scaffolding, not curator intent. A blanket `label_waived` on the node
   `label` slot would bury exactly these, which is an argument against the waiver the first
   version recommended.
4. **Unknown prefix** — an error rather than a silent pass, so `CHBEI:` fails. Finds
   nothing today; it is a trap for tomorrow.

Canonical-label matching across CHEBI remains the wrong gate — but on 13,998, not on the
77,122 the first version used to argue it.

## Implemented

The first recommendation is now a blocking CI gate. The committed baseline covers
429,271 records and 5,799 `proteintraitsmech:` nodes, with 5,543 mismatches and identity
SHA-256 `a0a4bc7cc9ae760658f967346149cbad500cdaf53dd0b8c42b675f32522f7456`.
The exact identity hash is required in addition to the count, so equal-count swaps fail.

The wider YAML surface is configured in `conf/id_label_targets.yaml` for the vendored
cross-ontology validator. It remains report-first and local because its OAK sqlite
adapters are not committed CI inputs.

## Scope note

Local and offline: `aro.obo`, `go.obo`, CHEBI `compounds.tsv.gz` / `names.tsv.gz`. No OAK
download, no network. `data/raw` is gitignored, so items 2–4 are local-only like
`audit-reproducible`; item 1 is not, and that is the point of putting it first.
