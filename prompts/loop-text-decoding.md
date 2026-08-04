# Loop B — #103, #123: text decoded wrong, and the records that carry it

**Use:** none — spent. Executed as #134; #103 and #123 are closed. Kept as a worked
example: both issues had a wrong root cause, and the run corrected them.

Feed this to `/goal`, or paste it to any agent. A worked instance of
`prompts/backlog-loop-goal.md`, which remains the workflow; this supplies the scope,
the measured facts and the traps.

_Facts measured on `main` at `d11217c5df5`, 2026-08-04._

---

Work **#103 and #123 as ONE pull request, two commits.**

## Why these two together

They have **zero file overlap** — I checked the one plausible collision, and
`fetch_cazy_families.py` uses `html.unescape` while `seed_obo` uses
`obo_syntax.unescape`, which are unrelated mechanisms. They are grouped because they
are the **same kind of bug with the same gate**: a source's text is decoded wrong, and
records on disk carry the damage.

**This PR changes records — 39 of them.** That is the whole difference from Loop A, and
it sets the verification: every changed record must be shown, counted, and validated.

| issue | files | records |
|---|---|---|
| #103 | `seed_obo.py` / `obo_syntax.py` | **37** |
| #123 | `fetch_cazy_families.py`, `seed_tcdb.py` | **2** |

## #103 — OBO escapes decoded for citations but not definitions

37 records carry a literal `\n` inside a folded `definition:` block. `seed_obo` decodes
OBO escapes when normalising a citation (`_unescape_obo` on the way to `PMID:`) but not
when writing the definition text.

**Measured distribution — it is almost entirely one source:**

```
MI                35     e.g. aphenotypic-neutral-multigenic-phenotype-result-mi2398.yaml
MOD                1     e.g. 2-2-aminosuccinimidyl-pentanedioic-acid-mod01946.yaml
proteintraitsmech  1     e.g. seed-subsystem-glutathione-non-redox-reactions.yaml
```

So this is a PSI-MI problem with two strays, not a corpus-wide one. The
`proteintraitsmech:` one is **not** OBO-sourced — check where its `\n` came from before
applying an OBO decoder to it.

### ⚠️ The trap that makes this not a global search-and-replace

**Three records contain `\textsuperscript`, which is LaTeX, not an OBO escape.**
Decoding `\t` there produces a tab and corrupts them:

```
PANTHER:PTHR30401   trna-2-selenouridine-synthase-pthr30401.yaml
InterPro:IPR058840  trna-2-selenouridine-synthase-aaa-domain-ipr058840.yaml
Pfam:PF26341        aaa-selu-pf26341.yaml
```

Any fix must be scoped to OBO-sourced records, or to the escapes OBO actually defines
in the position they actually occur. A blanket unescape over `data/traits` is the wrong
shape.

## #123 — two records carry mojibake, and one is not stable

```
data/traits/sequence/family/cazy/glycoside-hydrolase-gh20.yaml
data/traits/function/transport/tcdb/the-transmembrane-peptide-chondroitin-sulphate-gold-nanoparticle-tat-c-1-d-202.yaml
```

Both show the UTF-8-read-as-cp1252 signature (`â€` where the source has a non-breaking
hyphen, U+2011). The CAZy one is **not stable**: re-seeding produces *different bytes*
in the same position — the committed record has `â€` followed by `a`, a fresh seed
produces `â€` followed by U+0090, a C1 control character. So it drifts on every re-seed.

**Root cause is in the fetch/decode step, not the record.** Both paths assume UTF-8 and
paper over failure:

```python
fetch_cazy_families.py:55   r.read().decode("utf-8", "replace")
seed_tcdb.py:73,134         read_text(encoding="utf-8", errors="replace")
```

`errors="replace"` is what turns a wrong-charset response into silent mojibake instead
of a loud failure. Honour the charset the server declares, or detect it; failing loudly
on an undecodable byte is better than writing a C1 control character into a definition.

Fixing the decode does not by itself repair the two records on disk — they were written
by an earlier run. Both need re-seeding or correcting, and the PR should show the diff.

## Gates

```bash
just test
just lint
just validate-all data/traits          # closed-mode; this PR changes records
just audit-graphs
```

**And the two that matter for a data PR:**

1. **Count and show every changed record.** `git status --porcelain data/traits | wc -l`
   should equal 39, or you should be able to say exactly why it does not.
2. **Re-run the affected seeder twice** and confirm the second run is a byte-identical
   no-op. For #123 that is the actual acceptance test: the CAZy record must stop drifting.

## Traps

- **`\textsuperscript` is LaTeX.** See above. This is the single most likely way to turn
  a 37-record fix into a 40-record corruption.
- **`errors="replace"` hides the bug you are fixing.** Removing it may make a fetch fail
  where it used to "succeed" — that is the point, but say so rather than restoring it.
- **Do not fix the records by hand.** The seeder must produce the right bytes, or the
  next re-seed undoes you. Fix the decode, then re-seed, then show the diff.
- **Mutation-verify anything you add**, asserting the mutation target exists first.

Pause and ask before merging.
