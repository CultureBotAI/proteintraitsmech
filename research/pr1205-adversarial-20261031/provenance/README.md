# PR1205 provenance/publication adversarial audit

Owner: `/root/cavity_binding_evidence`. Date: 2026-10-31. Reference: explicit user
request to review/fix/merge PR1205; issues1200/1201/1204/1206 are historical context.
All work uses the parent-materialized isolated clone under `/private/tmp`, at
head `bc0c6d97aaab0ba20fcf8be28bc1527430679ccb`. The original Documents worktree,
other sessions and scientific records were not touched.

`assessment.json` gives two bounded third-party redistribution findings and the
positive checks, with authorship/independence limitations. Root owns any issue,
fix, commit, native review save, merge and branch action. This directory is an
audit observation, not an executable remediation or a new scientific review.

`audit_publication.py` is the first helper created/executed for this audit. It uses
Python standard library only and derives its repository root from its location.
Inputs: the initial publication manifest, additive checksum list, all published
discovery Python sources (ignored files included), the gzip snapshot and the four
new native review YAML source-input lists. Output: an exclusively created JSON
file directly under this directory. It reads no original-worktree or external
temporary inputs, makes no network call, changes no Git state, rewrites no old
report and executes no scientific detector. The narrow native-YAML extraction
is recorded as80 rows and is not a replacement for the canonical validator.

The initial execution used:

```sh
python3 research/pr1205-adversarial-20261031/provenance/audit_publication.py \
  --head bc0c6d97aaab0ba20fcf8be28bc1527430679ccb \
  --output research/pr1205-adversarial-20261031/provenance/publication-audit-20261031-initial.json
```

The report is retained unchanged. Root's complete-checkout signal and a later
read-only `git rev-parse HEAD` confirmed the requested head. Subsequent direct
commands read JSON/XML/ZIP source and native guidance, searched helper path/output
behavior, and performed the ignored-inclusive license searches below. They
created no other executable helper. No historic helper was rerun because some
intentionally overwrite fixed historical outputs or depend on earlier manifests.

Full checkout absence check (exit1, no matching GPLv3 text):

```sh
rg --no-ignore --hidden -l \
  'give all recipients a copy of this License along with the Program|Version 3, 29 June 2007' \
  --glob '!.git/**' --glob '!.venv/**' .
```

The complementary ignored-inclusive license/COPYING/GPL filename search returned
only `LICENSE`, `LICENSE-CODE`, `LICENSE-DATA`, a project license helper and
`motifs/so-license.txt`; none is GPLv3. The `.git` object store and any runtime
environment are excluded because they are not the distributed project files.
The task-wide CC-BY2 search found its license name and a nested author reference,
but no applicable license URI/copy or adjacent full citation for the SQL archive.

Before checkout finished, read-only `gh api` requests inspected exact-head PR
metadata and source files from `/private/tmp`, with `login:false`. No API content
was written into the repository or presented as a newly pinned source release.
Browser verification was limited to the already-used BMC source and applicable
license terms: publisher DOI10.1186/1471-2105-10-60, Creative Commons BY2 legalcode,
and SPDX's GPLv3 full text. GNU's page timed out; SPDX supplied the inspected full
license. URLs and exact source locators are in the assessment. Browser responses
were not saved as raw artifacts, and no raw-page hash is invented. Existing
source files retain their original rights; this audit's factual summaries do not
relicense them.

Reviewer previously authored the cavities evidence and beta-arch independent
review, but not the beta-arch proposal/record, packaging implementation or CI
repair. The fresh beta-arch primary comparison is explicitly a repeat check, not
a claim to be a newly uninvolved reviewer. No native immutable bundle was saved.

## Bounded official CAVER distribution followup

Root requested this followup for PROV-001/issue1227 (issue517 context).
`inspect_caver_distribution.py` is the second retained helper. Purpose: inspect
the directly linked official CAVER3.01 ZIP for a preferred editable manual source
or explicit redistribution exception. Inputs: one hardcoded official archive
URL; at most40MiB downloaded to memory. Outputs: new metadata-only
`caver301-distribution-inspection.json`, with archive/member hashes and inventory.
It does not install or execute CAVER, extract members to disk, retain another raw
archive or edit any original source. It ran once on2026-10-31; an approved network
escalation was needed after an ordinary `curl -IL` could not resolve the host.
Read-only browser checks covered official download/user-guide pages only.

The archive has1061 members and no recognizable editable-document filename.
Its PDF differs from the original retained manual, so it is not silently used
as an exact replacement. This bounded negative result does not prove that no
editable source exists anywhere. The full conclusion, native review preservation
mechanism and exact two-path withdrawal suggestion are in
`caver-source-disposition-followup.json`.

One direct bounded `curl --fail --location --max-time 30` invocation retained the
complete official license as `GPL-3.0.gnu.txt` from
`https://www.gnu.org/licenses/gpl-3.0.txt` (35,149bytes,
SHA256`3972dc9744f6499f0f9b2dbf76696f2ae7ad8af9b23dde66d6af86c9dfb36986`).
This copyright2007 Free Software Foundation text permits unchanged copying.
No executable helper was created for that download. Root can copy these exact
bytes to the final source-notices location without downloading the32MB archive
again. Original source terms are not changed by this audit.

## Final publication delta check

After the parent applied issue1227, the unchanged `audit_publication.py` ran a
second time with `--head 9dae07a86b815f9f21cd0ce96b050c8e4192feaf` and new output
`publication-audit-20261031-followup.json`. This records current working-tree
differences against historical inventories; expected differences are assessed
in `final-publication-delta-assessment.json`, not hidden or rewritten into the
initial manifest. No third helper was created. Direct read-only `git diff`,
`git cat-file`, SHA256 and source-notice reads checked the two-path deletion
boundary, unchanged original review bundles/manifests, exact historical manual
bytes, complete license copy and SQL citation. These reads created no executable
or raw manual copy. Root owns the subsequent commit and release gates.
