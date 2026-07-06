---
name: embedding-field-audit
description: Use this skill to decide which ProteinTraitRecord fields to include vs exclude when assembling the text that gets embedded (scripts/embed_records.py → load_corpus), so the vectors capture what defines and distinguishes each trait CLASS rather than per-instance noise, opaque identifiers, or boilerplate. It profiles each field empirically (coverage, cardinality, length, opaque-id-ness) and applies a fixed decision rubric — e.g. EXCLUDE canonical_examples protein sequences (per-protein, long, non-class-level) but INCLUDE sequence_pattern regexes (PROSITE patterns are class-defining). Trigger when asked which fields to embed, to tune/curate the embedding document, to improve the corpus map / related-traits quality, or before re-running embed_records.
---

# Embedding Field Audit

## What this is

`embed_records.py` serializes each record to one short document, then embeds it
(bge-large, ~512-token window). The **quality of every downstream semantic
feature** — related-traits, Tier-5 candidates, the corpus map, the
definition-only map — is bounded by *what text goes into that document*. This
skill decides, field by field, what to include.

The goal is a document that captures the trait **class's semantic identity** and
maximally **distinguishes** it from other classes — nothing else. Every token
spent on per-instance data, opaque identifiers, or boilerplate is a token stolen
from the 512-token window and a small push toward the corpus mean.

## The four tests (apply to every field)

A field's text earns a place in the embedding only if it passes **all four**:

1. **Class-level, not instance-level.** Does it describe the *trait class*, or a
   particular protein that happens to carry it? Example proteins, their
   sequences, accessions, and taxa describe instances → **out**.
2. **Discriminative.** Does the value differ between classes? A field that is
   near-constant across the corpus (license, term_kind, mapping_status) adds no
   separating signal → **out**.
3. **Meaningful to a language model.** Is it natural language, or a token whose
   form carries meaning (a PROSITE regex, an EC/GO/ChEBI *name*)? An opaque
   accession (`PDB:4ION`, `TED:AF-…-TED03`, `cd07064`) is noise to a text model
   → **out** (keep it as a *field* for search, just not in the embedded string).
4. **Fits the window.** Would it crowd out the definition? Long repeated blocks
   (full example lists, evidence snippets) → **out** or heavily capped.

## Field-by-field rubric

| Field | Embed? | Rationale |
|---|---|---|
| `label` | **INCLUDE** | The trait name — highest signal per token. |
| `definition` | **INCLUDE** | Primary semantic content. The anchor. |
| `definitions[].text` (GENERAL/STRUCTURAL/MECHANISTIC) | **INCLUDE** | Rich, distinguishing prose — the structural "multihelical; 2 layers…" and mechanistic layers are exactly what separates near-neighbours. Prefix each with its `kind`. |
| `synonyms[].synonym_text` | **INCLUDE** | Alternate names broaden lexical coverage; cheap, high-value. |
| `trait_axis`, `trait_category` | **INCLUDE (spelled out)** | Coarse semantic bucket ("ptm site (sequence trait)"), already done via `human_cat`. |
| `sequence_pattern` (regex / motif) | **INCLUDE** | A PROSITE pattern like `C-x(2)-C-x(4)-H` **defines** the class; its token structure is discriminative. Include the regex/consensus text. |
| `secondary_structure_representations` (descriptive parts) | **INCLUDE (text only)** | Fold/topology words are semantic; drop any bare ids. |
| `chemical_participants` (ChEBI **names** / roles) | **INCLUDE names** | "ATP", "substrate", "cofactor" are semantic. Exclude the bare `CHEBI:` ids. |
| `evolutionary_scope` (taxon_scope, method words) | **INCLUDE text** | Short descriptive tokens; skip numeric prevalence. |
| `parent_traits` | **CONDITIONAL** | Embed the parent's *label* (resolve the CURIE), not the bare CURIE — the parent name adds context; the accession does not. |
| `xrefs` / `mapped_xrefs` | **CONDITIONAL, capped** | A *few* **semantic** groundings help (`EC:3.2.1.21`, `GO:…`, `RHEA:…`, `CHEBI:…` where the prefix implies meaning). **Cap ~8** and **drop opaque structural accessions** (PDB, TED, ECOD, CATH-domain, `cd######`). Currently capped at 8 — also filter by prefix. |
| `trait_relations` | **CONDITIONAL** | The `predicate` (member_of/part_of) is signal; the object CURIE is not — embed at most the predicate word. |
| `structural_geometry_representations` | **EXCLUDE the id** | `structure_ref: PDB:4ION` is an opaque accession → out. Any *descriptive* field (fold text) → in. |
| `canonical_examples[].sequence` and the whole example block | **EXCLUDE** | **Per-protein instances**: sequences (long, dominate the window, not class-level), `protein_id`, `protein_label`, `taxon_*`, `sequence_length`, `annotation_score`, `fetched_at`. This is the canonical thing to strip. |
| `evidence` (DOI/PMID + snippet) | **EXCLUDE** | Provenance, not identity. A verbatim snippet risks leaking example-specific wording that pulls unrelated records together. |
| `identifier` | **EXCLUDE from text** | It is the row **key** (kept in `ids.json`), never embedded content. |
| `definition_source`, `license`, `term_kind`, `mapping_status` | **EXCLUDE** | Metadata / near-constant → zero discriminative value. |

## Empirical audit (data-drive the borderline calls)

Rules of thumb are a start; measure before committing a field. For each candidate
field compute **coverage** (too rare → not worth wiring), **cardinality /
uniqueness** (near-constant → boilerplate; near-unique → discriminative),
**mean token length** (window cost), and an **opaque-id ratio** (share of values
that are bare CURIEs/accessions → model-noise).

```bash
python3 - <<'PY'
import os, re, json, collections
FIELDS = ["definition", "sequence_pattern", "license", "term_kind"]  # extend
OPAQUE = re.compile(r'^[A-Za-z][\w.]*:[\w.:-]+$|^cd\d+$|^[A-Za-z]{2}\d{5,}$')
stat = {f: {"n": 0, "vals": collections.Counter(), "len": 0, "opaque": 0} for f in FIELDS}
tot = 0
for root, _, files in os.walk("data/traits"):
    for fn in files:
        if not fn.endswith(".yaml"): continue
        tot += 1
        t = open(os.path.join(root, fn), encoding="utf-8").read()
        for f in FIELDS:
            # folded/literal block (>- , |-) first, else an inline scalar that
            # is NOT just a block marker
            m = (re.search(rf'(?m)^{f}:[ \t]*[>|]-?\s*\n((?:[ \t]+.*\n)+)', t)
                 or re.search(rf'(?m)^{f}:[ \t]+(?![>|]\s*$)(.+)$', t))
            if not m: continue
            v = " ".join(m.group(1).split())
            s = stat[f]; s["n"] += 1; s["vals"][v[:40]] += 1
            s["len"] += len(v.split())
            if OPAQUE.match(v): s["opaque"] += 1
for f, s in stat.items():
    n = s["n"] or 1
    print(f"{f:28} cov {100*s['n']//tot:>3}%  uniq {len(s['vals'])/n:.2f}  "
          f"avg_tok {s['len']//n:>4}  opaque {100*s['opaque']//n:>3}%")
PY
```

Read it as: **high coverage + high uniqueness + low opaque% + modest length =
INCLUDE**; **near-constant (uniq→0) or high opaque% = EXCLUDE**; long + rare =
skip.

## Applying it

The decisions live in `load_corpus()` in `scripts/embed_records.py` (the `parts`
list it joins per record). To change what is embedded:

1. Ensure the field is **projected into the docs shards / detail sidecars** by
   `build_docs_index.py` (embed_records reads the projection, not the YAML) — e.g.
   `sequence_pattern` and `definitions` need a projection key before they can be
   embedded.
2. Add/remove the corresponding `parts.append(...)` in `load_corpus`, following
   the rubric (spell out coded values; cap and prefix-filter groundings; never
   append example sequences).
3. **Re-embed and re-index:** `embed_records` → `embed_neighbors` → `embed_map`
   → `just build-docs`. Embedding is the dominant compute (see
   `research/tool-value-analysis.md`), so batch field changes and re-run once.

## Best practices

1. **The definition (+ layered definitions) should dominate the vector.** Order
   `parts` so label + definition come first; keep everything else short so the
   512-token window is spent on meaning.
2. **Spell out codes, drop accessions.** `human_cat` already turns
   `SEQ_PTM_SITE` into "ptm site". Do the same for any coded field; never embed a
   bare PDB/TED/ECOD/`cd######` id.
3. **Cap and prefix-filter groundings.** Keep ≤8, and only semantic prefixes
   (EC/GO/RHEA/CHEBI/PR/MOD). A long tail of structural accessions is pure noise.
4. **Never embed `canonical_examples`.** Especially sequences — they are long,
   per-instance, and pull unrelated classes together by incidental sequence
   overlap.
5. **Measure, then commit.** Run the audit snippet on any field you're unsure
   about; let coverage/uniqueness/opaque% decide the borderline cases.
6. **Re-embedding is expensive — change fields in a batch**, then re-run the
   whole embed → neighbors → map → build-docs chain once.
