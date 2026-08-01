---
name: scalability-check
description: Assess whether the repo is still scalable for (1) Git/GitHub and (2) GitHub Pages as the corpus grows, and recommend or apply strategy adjustments (build docs in CI vs commit them, lean browser index + lazy detail, per-file-count storage tier, git-history cleanup). Trigger when asked "is this scalable", after a large ingestion, when the browser feels slow, when .git or the repo is getting large, or when a Pages deploy struggles.
---

# Scalability Check

Run this after big ingestions. Two independent axes fail differently: **Git**
(repo size, file count, history bloat) and **GitHub Pages** (site size, deploy
file-count, and — the real ceiling — client-side browser load).

## 1. Measure

```bash
# Git / working tree
find data/traits -name '*.yaml' | wc -l              # record count == file count
du -sh data/traits docs/data .git
git ls-files | wc -l                                 # total tracked files
git rev-list --count HEAD                             # commits
# largest blobs ever committed (history bloat)
git rev-list --objects --all | git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' \
  | awk '/^blob/{print $3,$4}' | sort -rn | head
# Pages / browser load
ls -la docs/data/records.*.json                      # sum = bytes the browser fetches+parses
python3 -c "import json,glob;print(sum(len(json.load(open(f))) for f in glob.glob('docs/data/records.*.json')),'records loaded in-memory')"
```

## 2. Thresholds & verdicts

| Signal | Green | Watch | Act |
|--------|-------|-------|-----|
| Repo tracked size | < 1 GB | 1–5 GB | > 5 GB (GitHub warns/blocks) |
| **Tracked file count** | < 100k | 100k–500k (git ops slow, UI struggles) | > 500k |
| **.git size / history** | small, stable | growing each commit from regenerable blobs | large + still committing generated data |
| Pages site (`docs/`) | < 1 GB | — | > 1 GB (Pages hard limit) |
| Pages deploy files | 10s–100s | 1000s (slow) | ~4000+ (deploy timeout — bucket them) |
| **Browser load (Σ shards)** | < 20 MB / < 50k recs | 20–66 MB / 50–150k | > ~66 MB / > ~150k (load-everything wall) |
| Single git file | < 50 MB | 50–100 MB (git warns) | > 100 MB (git rejects) |

## 3. Strategy adjustments (apply the ones the measurements trigger)

**A. Stop committing regenerable docs data; build it in CI.** `docs/data/`
(records.*.json, facets.json, seq/) is 100% regenerable from `data/traits/` via
`build_docs_index.py`. Committing it rewrites tens of MB every seeding commit —
the dominant history-bloat driver. Fix: gitignore it and generate + deploy in a
GitHub Actions Pages workflow (`build-docs` → `actions/upload-pages-artifact` →
`actions/deploy-pages`; set Pages source = GitHub Actions). Also gives control
over the deploy (fixes flaky branch-based Pages).

**B. Lean index + lazy detail (browser scalability).** The browser loads every
shard and parses all records — the practical ceiling is ~150k. Precompute a lean
index (id, label, axis, cat, src only — ~5× smaller, gzips to ~1 MB per 100k)
for the list/search view, and fetch each record's full JSON on demand (the same
pattern the sequence sidecars already use). Decouples browser perf from corpus
size → scales past 500k. Keep facet counts in facets.json.

**C. Shard sizing.** Keep every `records.<AXIS>[.NN].json` under the git 50 MB
warning via `MAX_SHARD_RECORDS` in `build_docs_index.py`; bucket per-record
sidecars (seq, and any future per-record blob) into a fixed small number of
files so the Pages deploy never sees thousands of files.

**D. File-count tier for bulk sources.** One-YAML-per-record is the core model
and fine to ~100–200k. For very high-volume machine-seeded sources (e.g. a full
ChEBI, eggNOG-scale sets) that would push the tree toward 500k+ files,
reconsider: store those sources as a smaller number of multi-record files, or
keep them out of `data/traits/` (index-only), rather than minting hundreds of
thousands of tiny files. Decide per source at ingest time (see
[`ingest-source`](../ingest-source/skill.md) "decide scope").

**E. History cleanup (only when .git is a real problem).** `git gc --aggressive`
reclaims loose space. A full shrink needs a history rewrite (`git filter-repo
--path docs/data --invert-paths` to drop old generated blobs) — rewrites history
and force-pushes, so coordinate. Prefer preventing bloat (A) over cleaning it.

## 4. Report

State each axis's verdict (green/watch/act) with the numbers, then the specific
adjustments triggered and whether they were applied or are recommended. Re-run
the measurements after applying.
