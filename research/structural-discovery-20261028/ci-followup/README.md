# Required CI provenance repair, 2026-10-29

[Issue #1206](https://github.com/CultureBotAI/proteintraitsmech/issues/1206) records
an inherited CI failure exposed by discovery PR #1205 at
`e6492195bccf54d50d5ec8acb2628cb26aa19ed6`.
The original [failed job](https://github.com/CultureBotAI/proteintraitsmech/actions/runs/40836120832/job/123321190405)
and exact failure log are retained in `initial-checks-failure.log`.

`reviews/structured/20261029T044503Z-structural-ledger-guard-followup/review.yaml`
is unchanged from base `7276814bdf3bed73569a202c5e2c4b404e43d8f1`. It pins
`93c1a021d76a94fd299e0a1e3cf8f1b9671a3703`, the only nonancestor among ten current
saved-review bases. Local Git retains that object; the fresh PR CI checkout did
not. PR #1202's retained head is `edaf56fe941c075c2c40b4b6cd02d663b809dcbd`;
the GitHub compare API verified the historical base is two commits behind that
head, with no divergence. Historical main checks report success; the fresh PR
checkout is the observed failure, not a new failure of that historical run.

Native `docs/record-reviews.md` requires historical Git bases to remain available.
The canonical CLAW loader deliberately refuses unverified provenance. The bounded
repair changes only PTM-owned `.github/workflows/checks.yml`: before the native
review test, restore the literal historical commit from the same origin if absent
using `git fetch --no-tags --no-write-fetch-head`, then require the exact commit
identity. A missing/unavailable commit or identity mismatch still fails the job.
It does not recreate a branch/tag, change checkout/index, rewrite a review, alter
validation semantics or expand CI permissions. Concurrent PR #794 also edits this
workflow; this small step is isolated from its biophysical additions and must be
reconciled if those changes land first.

The initial discovery commit's publication manifest remains its immutable snapshot.
This directory documents a subsequent substantive CI repair; final control-plane
head confirmations and mutable PR status stay outside commits. Scientific records,
manifest, seeder/tests and four native reviews remain byte-identical to the locally
validated discovery commit (8616 passed, 52 skipped; focused40 and registry26).
No scientific detector, source research or full-corpus validation was rerun.
The new commit's actual CI outcome is reported in PR metadata, not predicted here.

The workflow step itself is retained executable source. Its purpose is historical
Git-object availability, inputs are the literal SHA and same-repository origin,
and outputs are ephemeral CI objects plus a verified commit identity. Date/reference:
2026-10-29, #1206, standalone structural discovery. The independently retained
fixture probe and review document their own inputs, outputs and limits. Native
history scaffolding records this edit. No merge, queue entry, cleanup or session
changes are authorized.

## Independent verification

`independent-ci-fix-assessment.json` reports pass with limitations and no findings.
`probe_review_base_restore.py` extracts the actual workflow shell, asserts the
production pin, and substitutes only that literal with a disposable local Git
fixture's commit. The retained `restore-base-probes-20261029T074218272665Z.json`
records three passing cases: fetch a missing commit, avoid fetching an existing
commit even with an unavailable origin, and fail on an unavailable pin. HEAD,
all refs, index, FETCH_HEAD, config and staged/unstaged/untracked file bytes were
preserved. These synthetic checks do not establish live GitHub retrieval.

Run a new independent fixture observation with
`PYTHONDONTWRITEBYTECODE=1 .venv/bin/python research/structural-discovery-20261028/ci-followup/probe_review_base_restore.py`.
The helper writes a new timestamped report and refuses overwrite. Its temporary
repositories are disposable synthetic inputs, not unretained scientific data.
`artifact-sha256.txt` seals this additive result set and the changed workflow/history;
it excludes its own hash. The initial 26 Python sources are unchanged; this probe
is the twenty-seventh retained Python source in the discovery task.
