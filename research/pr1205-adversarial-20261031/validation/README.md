# Coordinator validation receipts

Date: 2026-10-31 UTC. PR #1205; fixes #1225, #1226 and #1227; CI provenance #1206.
Commands ran in the isolated checkout's Python 3.13 environment, installed with
`uv sync --locked --extra dev --extra molecular --python 3.13`.
`UV_CACHE_DIR` points to a task-owned temporary cache; native `just` commands use
`UV_OFFLINE=1` after installation. For `just build-docs`, `.venv/bin` was first
on PATH because the recipe invokes `python3` directly.

| Command | Result and receipt |
| --- | --- |
| `.venv/bin/python -m pytest --rootdir=. -o cache_dir=.pytest_cache tests/test_seed_structural_discovery.py -q` | 29 passed; `seeder-regressions.log` |
| `just lint` | Pass; `lint.log` |
| `just audit-writers` | Pass; 621 scripts examined; `writer-audit.log` |
| `just sources-check` | Pass with existing source-rights notices; `sources-check.log` |
| `.venv/bin/python scripts/validate_internal_id_labels.py --show 0` | 429,421 records, 5,800 checked pairs, unchanged 5,544 mismatch identities; `integration-baseline.log` |
| `.venv/bin/python scripts/record_review.py check --base origin/main` | Initial missing historical blob in partial clone; preserved `native-reviews-before-materialization.log`. After explicit hash-verified object preparation: 38 valid reviews; `native-reviews-final.log` |
| `just validate-history` | Pass; `history.log`. Both new records were created by native `just new-history` using its documented fallback scaffolder. |
| `just build-docs` | Pass, 429,421 records; landing/SLC10 checks pass; `docs-build.log`. Generated bulk browser data remain ignored, as native policy specifies. |

The science delegate's separate strict/grounding/graph runs cover exactly the
three unchanged submitted records. The code delegate's independent fixtures
cover original malformed cases, the first fix's readonly-parent gap, final
guards, positive CLI behavior and four two-base Git recovery cases. Original
failure observations and helper/source snapshots remain unchanged.

The complete local suite was launched with
`just test --rootdir=. -o cache_dir=.pytest_cache -q` and is still running when
this draft commit is prepared. Its final log remains in the task's private
control-plane report directory; the PR body will record its actual outcome.
This is not a claim of a full-suite pass or permission to bypass merge gates.
Full-corpus strict/grounding/graph validation is a required combined merge-queue
gate; scoped local science checks are not described as full-corpus validation.
Final remote checks and merge integrity belong to the actual pushed-head/queue
control plane, not to these pre-commit local receipts. No recursive evidence
commit is needed just to record a check of the commit containing these receipts.
