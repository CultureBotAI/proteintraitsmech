#!/usr/bin/env python3
"""Prepare the independently assessed native review input; never save a bundle."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import yaml

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
old = json.loads((OUT / "canary-native-inspection.json").read_text())
target = old["targets"][0]["target_id"]
source_paths = [row["path"] for row in old["source"]["inputs"] if row["role"] != "target"]
source_paths += [".claude/skills/curate-yaml-record/references/review-checklist.md", "justfile"]
command = [str(ROOT / ".venv/bin/python"), "scripts/record_review.py", "inspect", "--targets", str(OUT / "canary-native-targets.yaml")]
for path in source_paths:
    command.extend(["--input", path])
inspection = subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True)
current = json.loads(inspection.stdout)
current_hashes = {r["path"]: r["sha256"] for r in current["source"]["inputs"]}
for row in old["source"]["inputs"]:
    assert current_hashes[row["path"]] == row["sha256"], f"Input changed; reassessment required: {row['path']}"
with (OUT / "canary-native-inspection-with-rubric.json").open("x") as stream:
    stream.write(inspection.stdout)

actual = yaml.safe_load((ROOT / old["targets"][0]["path"]).read_text())
frozen = yaml.safe_load((OUT / "bottleneck-canary-reviewed-row-20261029T0704Z.yaml").read_text())
manifest = yaml.safe_load((ROOT / "data/curation/structural_trait_discovery.yaml").read_text())
assert actual == frozen == manifest["records"][0]["record"]
assert actual["mapping_status"] == "PROPOSED"
assert not actual.get("canonical_examples")
assert not actual.get("causal_graphs")
assert len(actual["curation_history"]) == 1 and actual["curation_history"][0]["llm_assisted"] is True
semantics = {"target": target, "actual_equals_frozen_row": True, "actual_equals_manifest_row": True, "qualified_examples": 0, "causal_graphs": 0, "history_events": 1, "mapping_status": actual["mapping_status"]}
with (OUT / "canary-emitted-semantic-comparison.json").open("x") as stream:
    json.dump(semantics, stream, indent=2)
    stream.write("\n")

finish = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
evidence = []
def ev(eid, kind, reference, locator, summary, support="supports", snapshot=None):
    row = dict(evidence_id=eid, kind=kind, reference=reference, locator=locator, accessed_at=finish, support=support, summary=summary)
    if snapshot:
        row["snapshot_sha256"] = snapshot
    evidence.append(row)

ev("record", "record_content", old["targets"][0]["path"], "Entire emitted YAML", "Full record read; emitted mapping equals the independently reviewed frozen row and maintained manifest. PROPOSED, one model-assisted creation event, no canonical examples and no causal graph.", snapshot=current_hashes[old["targets"][0]["path"]])
ev("schema", "authority", "src/proteintraitsmech/schema/proteintraitsmech.yaml", "ProteinTraitRecord, StructuralGeometryRepresentation, TraitRelation and DetectionMethod", "Schema permits source-linked representative geometry with optional residue ranges and documents detection recipe as an executable template rather than an executed workflow.", snapshot=current_hashes["src/proteintraitsmech/schema/proteintraitsmech.yaml"])
ev("rubric", "authority", ".claude/skills/curate-yaml-record/references/review-checklist.md", "All ten field-by-field audit areas", "Current native identity, axis, definition, relation, representation, function, example, graph, discussion and status rubric applied to the entire emitted record.", snapshot=current_hashes[".claude/skills/curate-yaml-record/references/review-checklist.md"])
ev("PLOS2012", "primary_source", "https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1002708", "Design and Implementation section3; static-structure analysis; Figure4 caption; copyright notice", "Primary text defines the path bottleneck using the minimum-radius ball and identifies the hydrogen-added 1CQW p1 model. The publisher gives a version-unspecified CC-BY notice.", snapshot=current_hashes["research/structural-discovery-20261028/motifs/caver2012-plos-primary.html"])
ev("CAVER_manual", "primary_source", "https://www.caver.cz/fil/download/manual/caver_userguide.pdf", "GPL notice; CLI pages6-7; starting point/probe/shell pages21-22; options page32; bottlenecks.csv pages48-49; seed; version3.01 notes", "Official manual supports the command template, PDB directory input, required starting point, model-sensitive configuration and output flag. Software and documentation retain GPL-3.0.", snapshot=current_hashes["research/structural-discovery-20261028/motifs/caver-discovery-userguide.pdf"])
ev("RCSB1CQW", "database", "https://www.rcsb.org/structure/1CQW", "Entry revision, experimental metadata, chain and author assembly; retained core entry API JSON", "1CQW is DhaA, chainA with author monomer; X-ray1.5angstrom, revision1.4 dated2024-02-07. It is a whole-structure input anchor, not a deposited residue annotation.", snapshot=current_hashes["research/structural-discovery-20261028/motifs/rcsb-1cqw-entry.json"])
ev("CAVER_registry", "database", "https://bio.tools/api/tool/caver/?format=json", "biotoolsID, name, primary publication, license and version fields", "Registry confirms caver identity, primary DOI/PMID and GPL-3.0. Its currently listed3.02 version does not imply execution of the record's documented3.0/3.01 recipe.", snapshot=current_hashes["research/structural-discovery-20261028/motifs/caver-biotools-registry.json"])
ev("EDAM", "authority", "https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl", "operation_2406 class", "Exact official class label Protein structure analysis inspected during immediate prewrite review; applies to CAVER geometry analysis.")
ev("ECO", "authority", "https://raw.githubusercontent.com/evidenceontology/evidenceontology/master/eco.obo", "release2026-07-10; ECO0007669 stanza", "Exact official computational evidence used in automatic assertion class inspected during immediate prewrite review; method evidence type does not assert this detector was executed.")
ev("wwPDB", "authority", "https://www.wwpdb.org/about/usage-policies", "Archive usage notice", "Archive data are CC0-1.0; this does not relicense the crystallography article. Notice inspected during immediate prewrite review.")
ev("native_tunnel", "record_content", "data/traits/structure/cavity/tunnel.yaml", "identifier, definition, axis/category and status", "The relation target exists and describes an entire tunnel. A minimum-width region is its part, not its subclass.", snapshot=current_hashes["data/traits/structure/cavity/tunnel.yaml"])
ev("prior", "prior_review", "research/structural-discovery-20261028/motifs/bottleneck-canary-science-assessment-20261029T0705Z.json", "Independent prewrite assessment and exact source hashes", "Prior scope-limited scientific input is retained; this native review covers the actual emitted record. No earlier finding disposition is claimed.", snapshot=current_hashes["research/structural-discovery-20261028/motifs/bottleneck-canary-science-assessment-20261029T0705Z.json"])
ev("validation", "validation", "research/structural-discovery-20261028/motifs/canary-native-strict.tsv", "Native actual-record strict result and observed graph audit output", "Independent strict validator exited0 with1file and0errors; graph audit exited0 with0graphs,0errors and0warnings.")
ev("grounding_validation", "validation", "research/structural-discovery-20261028/canary-grounding.log", "Coordinator's completed command and full output", "Coordinator reported exit0; inspected log reports1file and0semantic findings. Validator registry counts are loaded context, not qualified examples on this record.")
ev("ownership", "record_content", "data/curation/structural_trait_discovery.yaml; scripts/seed_structural_discovery.py; justfile", "Manifest row and seed-structural-discovery recipe", "Maintained content and emitter owners are explicit. Native command is registered in justfile. This scientific review is not a separate implementation audit.")

prior = json.loads((OUT / "bottleneck-canary-science-assessment-20261029T0705Z.json").read_text())
areas = ["identity", "scope", "nomenclature", "consistency", "representation", "representation", "representation", "evidence", "provenance", "provenance"]
assessments = []
for i, item in enumerate(prior["positive_assessments"]):
    ids = [{"native_schema":"schema", "manifest":"record"}.get(x,x) for x in item["sources"]]
    assessments.append(dict(assessment_id=f"A{i+1:02}", area=areas[i], topic=", ".join(item["fields"]), outcome="supported", summary=item["assessment"], target_ids=[target], evidence_ids=list(dict.fromkeys(ids + ["record", "rubric"]))))
assessments += [
    dict(assessment_id="A11", area="grounding", topic="Examples and qualification", outcome="supported", summary="Zero canonical examples and zero qualified occurrences are asserted. Whole-structure PDB representation is explicitly an input anchor; source-specific local coordinates and native qualification remain absent rather than invented.", target_ids=[target], evidence_ids=["record","RCSB1CQW","grounding_validation"]),
    dict(assessment_id="A12", area="graph", topic="Chemistry, function and causal graph", outcome="not_applicable", summary="No chemistry/function participant or causal graph is asserted; the geometry class does not require an invented class-wide mechanism.", target_ids=[target], evidence_ids=["record","rubric","validation"]),
    dict(assessment_id="A13", area="completeness", topic="Discussions, datasets and bounded completeness", outcome="supported", summary="Evidence notes are durable and actionable. Optional discussions/datasets are not required. Definition, geometric relation, documented method and source-linked representation suffice for this PROPOSED class; canonical example qualification remains an explicit limitation.", target_ids=[target], evidence_ids=["record","rubric"]),
    dict(assessment_id="A14", area="ownership", topic="Maintained inputs, emission and audit history", outcome="supported", summary="Emitted mapping equals the reviewed frozen row and maintained manifest, including all evidence, license and creation history. Future edits belong to the manifest and native emitter; PROPOSED status and LLM attribution are retained.", target_ids=[target], evidence_ids=["record","ownership"])
]
checks = [
    dict(check_id="strict", name="Native strict schema and semantic validation", status="passed", required=True, summary="One emitted file, zero errors; independently executed.", target_ids=[target], command=".venv/bin/python scripts/validate_strict.py --workers 1 --out research/structural-discovery-20261028/motifs/canary-native-strict.tsv data/traits/structure/cavity/tunnel-bottleneck.yaml", exit_code=0, evidence_ids=["validation"]),
    dict(check_id="graphs", name="Native graph audit", status="passed", required=True, summary="Zero graphs, errors and warnings; independently executed. This does not provide mechanistic evidence.", target_ids=[target], command=".venv/bin/python scripts/audit_causal_graphs.py data/traits/structure/cavity/tunnel-bottleneck.yaml", exit_code=0, evidence_ids=["validation"]),
    dict(check_id="grounding", name="Native grounding validator", status="passed", required=True, summary="Coordinator executed exit0; inspected complete log reports one target and zero findings. No require-qualified claim is made.", target_ids=[target], command="uv run python scripts/validate_uniprot_grounding.py data/traits/structure/cavity/tunnel-bottleneck.yaml --out research/structural-discovery-20261028/canary-grounding-findings.tsv", exit_code=0, evidence_ids=["grounding_validation"], scope_note="Execution by coordinator; full output independently inspected."),
    dict(check_id="emitted_semantics", name="Emitted versus independently reviewed content", status="passed", required=True, summary="Entire parsed mapping is identical to maintained manifest and frozen independent-review row, including history and examples.", target_ids=[target], evidence_ids=["record","prior"]),
    dict(check_id="external_execution", name="CAVER external execution", status="not_applicable", required=False, summary="Recipe is documented only; no local installation, detector run or output-based qualification is claimed.", target_ids=[target], evidence_ids=["CAVER_manual","record"]),
    dict(check_id="imodulondb", name="Structured expression adapter", status="not_applicable", required=False, summary="A geometric structural class with no expression, regulator or transcriptomic claim does not call for iModulonDB evidence.", target_ids=[target], evidence_ids=["record"])
]
review = dict(schema_version="1.0.0", review_id=stamp+"-independent-tunnel-bottleneck-canary", kind="record", repository=current["repository"], title="Independent scientific review of the emitted protein tunnel bottleneck canary", started_at="2026-10-29T07:07:43Z", finished_at=finish, reviewer=dict(identity="Codex /root/grounding_route_audit", kind="agent", model="GPT-6", independence="independent", independence_basis="Reviewer authored neither cavity candidate proposal nor record/manifest/emitter; independently inspected primary sources for the prewrite review and reread actual emitted record under current native rubric."), skill=".claude/skills/review-yaml-record/SKILL.md", completion="completed", verdict="pass_with_limitations", scientific_review=True, summary="One emitted PROPOSED geometric class is source-supported, schema-valid and semantically identical to its independently reviewed manifest row. No findings. Model-sensitive external detection is documented but unexecuted; no canonical protein occurrence, local residue boundary, transport function or gating mechanism is qualified.", source=current["source"], scope=dict(description="Entire emitted protein tunnel bottleneck record under the native ten-area field rubric.", selection="Exact coordinator-named canary path and identifier, no sampling.", coverage="full", population_size=1, reviewed_target_ids=[target], exclusions=[dict(target="Other discovery candidates and the corpus", reason="Only this emitted canary is scientifically reviewed; no corpus-wide or other-record inference.")]), targets=current["targets"], checks=checks, evidence=evidence, assessments=assessments, findings=[], actions=[], limitations=["The CAVER command is a documented external template. No detector execution, performance claim, model-specific bottleneck residue assignment or source-qualified protein occurrence was produced.", "The representative PDB entry is the whole-structure anchor for the paper's hydrogen-added model; original deposited coordinates are not the analyzed hydrogen-added model itself.", "Source licenses remain distinct: version-unspecified publisher CC-BY, GPL-3.0 software/manual, CC0-1.0 archive metadata and original project-authored CC-BY-4.0 synthesis.", "Scientific review does not confer human REVIEWED status, certify the writer implementation, reserve identifiers, certify all corpus/remote overlap checks, or authorize Git actions.", "The prior prewrite JSON is related evidence, not a native review bundle or a finding-resolution predecessor. This input is prepared for coordinator use with the native saver; this script does not save an immutable bundle."], links=["research/structural-discovery-20261028/motifs/bottleneck-canary-science-assessment-20261029T0705Z.json"], tags=["structural-discovery","canary","independent-science"])
destination = OUT / "canary-native-review-input.yaml"
with destination.open("x") as stream:
    yaml.safe_dump(review, stream, sort_keys=False, allow_unicode=True, width=100)
validated = subprocess.run([str(ROOT / ".venv/bin/python"), "scripts/record_review.py", "validate", str(destination)], cwd=ROOT, capture_output=True, text=True)
with (OUT / "canary-native-review-input-validation.json").open("x") as stream:
    json.dump(dict(command=validated.args, exit_code=validated.returncode, stdout=validated.stdout, stderr=validated.stderr, path=str(destination.relative_to(ROOT)), sha256=hashlib.sha256(destination.read_bytes()).hexdigest()), stream, indent=2)
    stream.write("\n")
print(validated.stdout, end="")
print(validated.stderr, end="", file=sys.stderr)
print(str(destination.relative_to(ROOT)))
raise SystemExit(validated.returncode)
