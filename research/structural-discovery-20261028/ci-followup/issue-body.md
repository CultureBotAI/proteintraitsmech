PR #1205's required `checks` job fails on an inherited immutable review because its pre-squash Git base is absent from a fresh CI checkout.

- Failed run: https://github.com/CultureBotAI/proteintraitsmech/actions/runs/40836120832/job/123321190405
- Discovery head: `e6492195bccf54d50d5ec8acb2628cb26aa19ed6`; inherited base: `7276814bdf3bed73569a202c5e2c4b404e43d8f1`.
- Failing review: `reviews/structured/20261029T044503Z-structural-ledger-guard-followup/review.yaml`, which pins `93c1a021d76a94fd299e0a1e3cf8f1b9671a3703` as a working-tree base.
- Exact failure: `source provenance unverified: Git provenance check failed: rev-parse --verify 93c1a021d76a94fd299e0a1e3cf8f1b9671a3703^{commit}`.
- The review, native validator, consumer test and checks workflow are unchanged from the inherited base. This object exists in the preserved local checkout and on GitHub, explaining why local checks pass. It is the only nonancestor among ten current saved-review bases. PR #1202 was squash-merged; its retained head is `edaf56fe941c075c2c40b4b6cd02d663b809dcbd`. Full-depth checkout alone does not guarantee this pre-squash object remains available after feature-ref retirement.

The native contract deliberately requires historical Git bases to remain available (`docs/record-reviews.md`, provenance section). Do not rewrite immutable reviews, relabel their provenance, skip validation, recreate retired refs or patch the CLAW-governed validator locally.

Bounded proposed repair: in PTM-owned `checks.yml`, before native review validation, check for this literal commit; if absent fetch that exact SHA from the same origin with `--no-tags --no-write-fetch-head`, and require exact commit identity afterward. This only restores required objects in the ephemeral CI checkout. Fetch failure remains a failure. An independent native-boundary review accepted this nonsemantic availability approach; no general provenance-policy change is proposed.

Acceptance: a new PR check run must retrieve/verify the historical base and pass the existing structured-review contract plus the remaining required checks. Preserve the original failure evidence and all review bytes. No merge, queue entry, session operation or cleanup is authorized by this finding.
