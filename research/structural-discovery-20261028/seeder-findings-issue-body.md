The new, not-yet-applied structural-discovery seeder has three independently reproduced guards to fix before its first corpus write.

1. A YAML-escaped primary identifier passes native strict validation but evades the raw-text `rg` prefilter. The seeder then creates a second record with the same parsed identity.
2. `read_text()` normalizes CRLF, so an existing destination can be declared unchanged while the reported SHA-256 does not match its bytes.
3. The CLI's `--report` accepts a trait destination even in dry-run mode, overwriting that record with JSON outside the native validated writer.

Reproduced in disposable fixture trees using the real native validator. No production trait record was written or damaged. Initial seeder SHA-256: `96cc0749a8791d599bafeefe3eea9bf2258f900e25d078416fe8553edf9c6e4a`. Retained probe and report will accompany the discovery PR under `research/structural-discovery-20261028/preflight/`.

Required fix: inspect parsed identities across ignored-inclusive corpus YAML; compare and report exact destination bytes; confine report output to the owned evidence directory and validate the destination before any record writes. Add regression tests, rerun the independent probes, and re-review the resulting writer before canary/batch application.

Scope: standalone structural discovery on `discover/structural-traits-20261028-04f08f`, context #1200/#1201. This finding does not authorize merging, a workflow-cycle restart or other-worker/session changes.
