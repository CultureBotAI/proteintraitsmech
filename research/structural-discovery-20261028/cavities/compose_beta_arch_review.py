#!/usr/bin/env python3
"""Serialize the independently assessed beta-arch review, 2026-10-29 / #1200.

Purpose: retain the reviewer's explicit field judgements in native RecordReview
format, with exact inspection and command evidence. Not an automatic scientist.
Input: one completed sibling beta-arch-native-* capture, unchanged reviewed
record/owners/rubrics and retained ontology verification. Output: new sibling
review-input.yaml, final-inspect.json, native-input-validation.log; never saves a
native immutable bundle. Parent owns final save. Run after reading actual bytes.
Requires owned .venv; no network, no record/Git/session mutations.
"""
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import yaml

from prepare_beta_arch_review import HERE, ROOT, PYTHON, TARGET, IDENTIFIER, INPUTS


class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True


def main():
    out = Path(sys.argv[1]).resolve()
    if out.parent != HERE or not out.name.startswith("beta-arch-native-"):
        raise ValueError("Expected a sibling capture directory")
    capture = json.loads((out / "inspect.json").read_text())
    result = json.loads((out / "checks.json").read_text())
    assert result["manifest_equals_emitted_record"] and result["all_inspected_inputs_unchanged"]
    assert all(c["exit_code"] == 0 for c in result["checks"])
    for row in capture["source"]["inputs"]:
        assert hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest() == row["sha256"], row["path"]
    # The term catalog was independently read after first inspection; capture it
    # as an additional input without mutating the original inspection evidence.
    cmd = [str(PYTHON), "scripts/record_review.py", "inspect", "--targets", str(out / "targets.yaml")]
    for p in INPUTS + ["research/structural-traits-20261028/method-ontology-check.json"]:
        cmd += ["--input", p]
    refreshed = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=True)
    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    stamp = now.replace("-", "").replace(":", "")
    with (out / ("final-inspect-" + stamp + ".json")).open("x") as handle:
        handle.write(refreshed.stdout)
    current = json.loads(refreshed.stdout)
    ids = [IDENTIFIER]
    evidence = []

    def ev(key, kind, reference, locator, summary, support="supports"):
        evidence.append(dict(evidence_id=key, kind=kind, reference=reference, locator=locator,
                             accessed_at=now, support=support, summary=summary))

    ev("record", "record_content", TARGET, "Entire emitted record and exact manifest row",
       "Read all fields; emitted mapping equals maintained row. CLASS/PROPOSED, no canonical examples or causal graph.")
    ev("primary", "primary_source", "DOI:10.1038/s41467-022-33004-6",
       "Retained motifs/natcomm-2022-immunoglobulin.xml: introduction, beta-arch methods, dIG8-CC characterization, deposition and rights",
       "Source supports nonpaired strand connections and experimental dIG8-CC arch geometry, including a helical connection. Study loop sampling is not a class cutoff. CC-BY4 notice inspected.")
    ev("archive", "database", "https://www.rcsb.org/structure/7SKO",
       "Identity, experiment, chains, assemblies and revision history",
       "dIG8-CC synthetic construct; v1.2 revised 2024-11-13; X-ray2.05angstrom; A-D chain copies; author/PISA C2 dimer assemblies. Whole-structure representative only.")
    ev("dssp", "authority", "https://github.com/PDB-REDO/dssp",
       "Native documentation; local mkdssp4.6.1 --version and --help",
       "CLI syntax is supported. Assignment and pairing output can support subsequent connected-strand review; the command does not itself label beta arches.")
    ev("rights", "authority", "https://raw.githubusercontent.com/PDB-REDO/dssp/trunk/LICENSE; https://www.wwpdb.org/about/usage-policies",
       "Official software BSD-2-Clause and archive CC0 notices",
       "Rights checked independently; source terms remain distinct from article and project CC-BY4. No coordinates, figure or software copied into record.")
    ev("rubric", "authority", ".claude/skills/curate-yaml-record/references/review-checklist.md",
       "All ten field areas plus schema and record-review profile",
       "Applied native identity, scope, definition, hierarchy, representation, chemistry, example, graph, discussion and audit rubric. Optional graph/local bounds not fabricated.")
    ev("parent", "record_content", "data/traits/structure/secondary/super-secondary-motif.yaml",
       "Entire current parent",
       "Existing parent is an arrangement of secondary elements defined by connectivity and spatial relations, appropriate for beta arch.")
    ev("terms", "authority", "research/structural-traits-20261028/method-ontology-check.json",
       "Retained official ECO term stanza",
       "ECO0007669 is computational evidence used in automatic assertion; attached to computational screening step rather than a claim of executed manual motif classification.")
    ev("checks", "validation", str((out / "checks.json").relative_to(ROOT)),
       "Actual independent native command outputs",
       "Scoped strict, graph and migration-safe grounding checks completed successfully. No require-qualified claim is made.")
    ev("ownership", "record_content", "data/curation/structural_trait_discovery.yaml; scripts/seed_structural_discovery.py; justfile",
       "Exact maintained row, emitter and native recipe",
       "Content owner and native writer are explicit; parsed emitted record equals source row. This is scientific review, not independent code certification.")
    ev("prior", "prior_review", "research/structural-discovery-20261028/cavities/motif-candidate-independent-review.json",
       "Bounded prewrite candidate review and ignored-inclusive novelty adjudication",
       "Earlier independent candidate assessment is retained as context; it did not save a RecordReview or claim qualification.")
    assessments = []

    def assess(key, area, topic, summary, refs, outcome="supported"):
        assessments.append(dict(assessment_id=key, area=area, topic=topic, outcome=outcome,
                                summary=summary, target_ids=ids, evidence_ids=refs))

    assess("A01", "identity", "Identifier, label, definition, synonyms and class scope",
           "Reusable whole strand-connection-strand class, distinct from beta hairpin, beta-arc connector, ambiguous beta-beta, and complete Ig domain. Exact hyphenated/Greek aliases preserve identity; no unsupported external xref added.", ["record", "primary", "prior", "rubric"])
    assess("A02", "scope", "STRUCTURE / STRUCT_SECONDARY / PROPOSED",
           "The coordinate-defined supersecondary class is correctly placed. PROPOSED and LLM-assisted history do not imply human sign-off.", ["record", "rubric"])
    assess("A03", "consistency", "Parent and relation semantics",
           "SUPER_SECONDARY_MOTIF exists and is a valid is-a parent. No part/whole confusion or unresolved SO identity is encoded.", ["parent", "record", "primary"])
    assess("A04", "representation", "Secondary-structure topology",
           "Curated E-connection-E notation expresses nonpairing of flanking strands; it is explicitly not a per-residue DSSP assignment. The connection may contain helix; no unjustified loop-length boundary is imposed.", ["record", "primary", "rubric"])
    assess("A05", "representation", "Documented detector scope",
           "The executable DSSP template matches native syntax. Evidence notes supply mandatory chain-continuity, pairing and geometry review and fail closed on missing/ambiguous coordinates. ECO annotation describes computational screening. No automatic beta-arch classifier or tested execution is claimed.", ["dssp", "terms", "record", "rubric"])
    assess("A06", "grounding", "7SKO representative and conflict handling",
           "Primary structural characterization plus deposition section grounds 7SKO as a synthetic dIG8-CC arch representative. Incorrect Figure5c 7SKP/chainC caption is preserved as a conflict. Dimeric assembly, chain-copy scope, missing local bounds and absence of canonical qualification are explicit.", ["primary", "archive", "record", "rubric"])
    assess("A07", "evidence", "Evidence placement and license",
           "Definition, detector, example and rights assertions are separately cited. Primary article CC-BY4, DSSP BSD2 and archive CC0 are preserved; project CC-BY4 applies to original synthesis only.", ["primary", "rights", "record"])
    assess("A08", "graph", "Function, chemistry and mechanism",
           "No universal mechanism, function participant or causal graph is claimed for this geometric motif; the native graph audit has zero graphs and errors.", ["record", "checks", "rubric"], "not_applicable")
    assess("A09", "provenance", "Status, history and maintained owner",
           "The creation event names the manifest, writer, evidence dossier and issue1200 context, retains PROPOSED and LLM attribution, and does not close adjacent work. Manifest and emitted content agree.", ["record", "ownership", "checks"])
    assess("A10", "completeness", "Bounded field completeness",
           "The class has supported definition, hierarchy, comparable topology, source-grounded structural representative and runnable screening with explicit manual discrimination. Optional discussions/datasets and canonical occurrences are not invented. Wider publication and qualification remain outside this review.", ["record", "rubric", "checks"])
    checks = []
    for c in result["checks"]:
        checks.append(dict(check_id=c["check_id"], name="Native scoped " + c["check_id"], status="passed",
                           required=True, summary="Independently executed; full output retained at " + c["log"],
                           target_ids=ids, command=" ".join(c["command"]), exit_code=c["exit_code"], evidence_ids=["checks"]))
    checks += [dict(check_id="manifest_equality", name="Parsed manifest/emission equality", status="passed",
                    required=True, summary="Entire parsed mapping agrees, including history and representative.", target_ids=ids,
                    evidence_ids=["record", "ownership", "checks"]),
               dict(check_id="detector_execution", name="Actual motif detection", status="not_applicable", required=False,
                    summary="Only CLI syntax was checked; the record explicitly documents an unexecuted screening recipe.", target_ids=ids,
                    evidence_ids=["record", "dssp"]),
               dict(check_id="imodulondb", name="Expression adapter", status="not_applicable", required=False,
                    summary="No regulator, expression or transcriptomic claim is made by this geometric class.", target_ids=ids,
                    evidence_ids=["record"])]
    review = dict(schema_version="1.0.0", review_id=stamp + "-independent-beta-arch",
                  kind="record", repository="CultureBotAI/proteintraitsmech",
                  title="Independent science review of emitted beta arch", started_at=result["started_at"], finished_at=now,
                  reviewer=dict(identity="Codex /root/cavity_binding_evidence", kind="agent", model="GPT-6",
                                independence="independent", independence_basis="Reviewer authored neither motif candidate card nor final manifest/record; prior candidate review and actual-byte review were independent."),
                  skill=".claude/skills/review-yaml-record/SKILL.md", completion="completed", verdict="pass_with_limitations",
                  scientific_review=True, summary="One emitted PROPOSED beta-arch record is source-supported and passes scoped native checks; no findings. Detection is documented screening plus explicit review, and the grounded PDB representative is not a qualified canonical protein example.",
                  source=current["source"], scope=dict(description="Full emitted beta-arch field audit", selection="Exact parent-assigned record, no sampling",
                  coverage="full", population_size=1, reviewed_target_ids=ids,
                  exclusions=[dict(target="Other records, whole-corpus publication and canonical qualification", reason="Not within this single-record science review")]),
                  targets=current["targets"], checks=checks, evidence=evidence, assessments=assessments, findings=[], actions=[],
                  limitations=["No structure detector was executed; DSSP assignment must be followed by the explicitly described manual classification.",
                               "7SKO is a source-grounded synthetic-construct representative, not a residue-localized or release-pinned QUALIFIED canonical occurrence.",
                               "Figure5c's PDB/chain discrepancy is preserved; deposition and archive evidence support the chosen7SKO anchor.",
                               "Native migration-safe grounding validation does not imply require-qualified completion.",
                               "Identifier reservation, global/open-work coordination, full release tests, writer certification and publication remain coordinator-owned.",
                               "CLAUDE.md is the documented symlink to AGENTS.md. Native inspection rejects symlinks; canonical AGENTS.md bytes are captured. The failed earlier inspection is retained.",
                               "This input awaits the coordinator's native immutable save; the helper does not save or alter existing review bundles."],
                  links=["research/structural-discovery-20261028/cavities/motif-candidate-independent-review.json"],
                  tags=["structural-discovery", "independent-science", "beta-arch"])
    dest = out / ("review-input-" + stamp + ".yaml")
    with dest.open("x") as handle:
        yaml.dump(review, handle, Dumper=NoAliasDumper, sort_keys=False, allow_unicode=True, width=100)
    validation = subprocess.run([str(PYTHON), "scripts/record_review.py", "validate", str(dest)], cwd=ROOT, text=True, capture_output=True)
    (out / ("native-input-validation-" + stamp + ".log")).write_text(validation.stdout + validation.stderr)
    print(json.dumps({"review": str(dest.relative_to(ROOT)), "validation_exit_code": validation.returncode}))
    if validation.returncode:
        raise RuntimeError(validation.stderr + validation.stdout)


if __name__ == "__main__":
    main()
