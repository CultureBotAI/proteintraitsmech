"""Assemble the bounded field ledger from inspected proposals; never writes records.

Run against the documented pre-curation records. Seeder hooks are bypassed only
inside this research process to capture the uncurated emission preimages.
The resulting data/curation ledger, rather than this research helper, is consumed
by native seeders and the registered editor. Source dossiers retain limitations.
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import seed_foundational_traits as foundational
import seed_localstructuralfeature as local
import seed_secondary_structure as secondary
from structural_trait_curations import apply_blocks, digest

HERE = Path(__file__).resolve().parent
STAMP = "2026-10-28T18:52:22Z"

# This process assembles the ledger; maintained seeders consume it. Capture their
# raw emissions without recursively applying the previous ledger version.
for module in (foundational, local, secondary):
    module.curate_seed = lambda text, owner: text


def block(key, value):
    if value is None or value == []:
        return None
    if key == "definition":
        import textwrap

        return "definition: >-\n" + textwrap.fill(value, width=98, initial_indent="  ",
                                                  subsequent_indent="  ") + "\n"
    return yaml.safe_dump({key: value}, sort_keys=False, allow_unicode=True, width=98)


sources = {}
paths = {}
for rec in secondary.build_records():
    sources.setdefault(rec["identifier"], {})["seed_secondary_structure"] = digest(secondary.emit(rec))
    paths[rec["identifier"]] = rec["path"]
for rec in local.TERMS:
    identifier = "proteintraitsmech:" + rec["term"]
    sources.setdefault(identifier, {})["seed_localstructuralfeature"] = digest(local.yaml_for(rec))
    paths[identifier] = local.target_path(rec)
for spec in foundational.SPECS:
    sources.setdefault(spec.identifier, {})["seed_foundational_traits"] = digest(
        foundational.emit_record(spec))
    paths[spec.identifier] = foundational.TRAITS_DIR / spec.rel_dir / spec.filename

motifs = json.loads((HERE / "motifs/evidence-dossier.json").read_text())
motif_review = json.loads((HERE / "cavities/motif-independent-review.json").read_text())
motif_corrections = {row["id"]: row for row in motif_review["corrections"]}
support_notes = {
    "HELIX_TURN_HELIX": "The ontology describes a two-helix structural motif. DNA binding and sequence-screen predictions are separate claims.",
    "BETA_ALPHA_BETA": "The documented motif requires parallel paired strands joined through a helix; the E-H-E token alone does not encode strand pairing.",
    "GREEK_KEY": "The conventional four-strand connectivity is +3,-1,-1. The primary analysis distinguishes multiple hydrogen-bonding and three-dimensional arrangements within this convention.",
    "BETA_HAIRPIN": "The two strands are antiparallel and paired; the connecting loop need not be a four-residue beta turn. The E-turn-E token uses turn to denote this connector.",
    "BETA_TURN": "The geometric beta-turn convention can include motifs without the end-to-end hydrogen bond required by the narrower DSSP T assignment.",
    "SUPER_SECONDARY_MOTIF": "The described coordinate-based analyses use connectivity and spatial relationships to distinguish recurring combinations of secondary elements. This umbrella has no single topology matcher.",
    "POLYPEPTIDE_STRUCTURAL_MOTIF": "The ontology allows a recurring element that need not be an independently stable globular unit; it does not exclude motifs within such units.",
    "TURN": "DSSP assigns T as a hydrogen-bonded turn state. The assignment is not an exhaustive classifier of geometrically defined beta turns.",
}
proposals = []
for proposal in motifs["proposals"]:
    identifier = proposal["identifier"]
    fields = copy.deepcopy(proposal["proposed_fields"])
    old = yaml.safe_load(paths[identifier].read_text())
    source = fields["definition_source"]
    fields["evidence"] = list(old.get("evidence") or []) + [{
        "reference": source,
        "notes": support_notes[identifier.split(":")[1]],
    }]
    license_disposition = (
        "Project-authored factual synthesis, annotations and topology notation are CC-BY-4.0 "
        "under LICENSE/ LICENSE-DATA; this is not a license for the cited articles or tools. "
        "No article prose, figures, matrices or software are redistributed. Source-specific "
        "terms and inspected sections are retained in the evidence dossier."
    )
    fields["license"] = "CC-BY-4.0"
    for method in fields.get("detection_methods", []):
        method["edam_operation"] = (
            "EDAM:operation_0268" if identifier.endswith(":HELIX_TURN_HELIX") else
            "EDAM:operation_0319" if identifier.endswith(":TURN") else "EDAM:operation_2406")
        method["evidence_code"] = "ECO:0007669"
    if source in {"SO:0001081", "SO:0001079", "SO:0001133"}:
        license_disposition = motif_corrections["rights-disposition-specificity"]["proposed_value"]
        fields["evidence"].append({
            "reference": "https://github.com/The-Sequence-Ontology/SO-Ontologies/blob/master/LICENSE",
            "notes": "Sequence Ontology CC-BY-4.0 terms inspected 2026-10-28; definition paraphrased "
                     "from the 2026-08-07 ontology. Cited papers and software retain their own terms.",
        })
    else:
        fields["evidence"].append({
            "reference": "https://github.com/CultureBotAI/proteintraitsmech/blob/main/LICENSE",
            "notes": license_disposition,
        })
    if identifier.endswith(":BETA_TURN"):
        correction = motif_corrections["beta-turn-boundary"]
        fields["definition"] = correction["proposed_definition"]
        fields["definitions"][0]["text"] = correction["proposed_structural_definition"]
        fields["definitions"][0]["source"] = "https://www.uoxray.uoregon.edu/local/manuals/promotif/document_2.html"
    if identifier.endswith(":TURN"):
        correction = motif_corrections["turn-state-field"]
        fields["secondary_structure_representations"] = [correction["proposed_representation"]]
        fields["detection_methods"][0]["name"] = correction["proposed_method_name"]
    if identifier.endswith(":GREEK_KEY"):
        advice = motif_review["greek_key_method_advice"]
        fields["detection_methods"] = [{key: advice[key] for key in
            ("name", "method_type", "tool", "reference", "recipe")}]
        fields["detection_methods"][0].update(edam_operation="EDAM:operation_2406",
                                               evidence_code="ECO:0000305")
        fields["evidence"].append({"reference": advice["tool"], "notes": advice["evidence_note"]})
    if identifier.endswith((":BETA_ALPHA_BETA", ":BETA_HAIRPIN", ":BETA_TURN")):
        fields["evidence"].append({
            "reference": "https://www.uoxray.uoregon.edu/local/manuals/promotif/document_2.html",
            "notes": "PROMOTIF v2 manual documents the recipe and class-specific output. "
                     "An authorized installation is required under its academic-use terms; "
                     "the program was neither installed nor run in this curation.",
        })
    if identifier.endswith(":BETA_HAIRPIN"):
        fields["evidence"].append({
            "reference": "DOI:10.1002/pro.4936",
            "notes": "Section 2.1/Figure 1 distinguish paired-strand hairpins from arches. "
                     "Both are called beta-beta loops; bare beta-beta is therefore not installed "
                     "as an exact synonym. No source prose or figures reproduced.",
        })
    if identifier.endswith(":HELIX_TURN_HELIX"):
        fields["evidence"].extend([
            {"reference": "PMID:2402433", "notes": "The Dodd-Egan matrix estimates HTH likelihood "
             "from sequence. The linked EMBOSS implementation is a screening method; "
             "a hit does not establish the 3D motif or DNA-binding activity."},
            {"reference": "PMID:1387915", "notes": "The lambda repressor-operator study explicitly "
             "describes its HTH region. PDB 1LMB is a representative structure containing that "
             "region; no local residue selection or qualified UniProt occurrence is asserted."},
        ])
        fields["structural_geometry_representations"] = [{
            "structure_ref": "PDB:1LMB",
            "structure_source": "PDB, entry version 1.3",
            "evidence_source": "PMID:1387915; https://www.rcsb.org/structure/1LMB; inspected "
            "2026-10-28. Lambda repressor chains C/D (author 3/4), X-ray 1.8 angstrom. "
            "Structure containing the source-described HTH region; motif bounds unspecified.",
        }]
    proposals.append({"identifier": identifier, "fields": fields,
                      "limitations": proposal["limits_and_acceptance"],
                      "license_disposition": license_disposition})

# The geometry/binding proposal file is produced by the separate source audit.
cavities_path = HERE / "cavities/field-proposals.json"
if cavities_path.exists():
    for proposal in json.loads(cavities_path.read_text())["proposals"]:
        identifier = proposal["identifier"]
        original = paths[identifier].read_text()
        if digest(original) != proposal["expected_sha256"]:
            raise ValueError(f"Inspected input changed: {identifier}")
        old = yaml.safe_load(original)
        fields = copy.deepcopy(proposal["set_fields"])
        fields["evidence"] = list(old.get("evidence") or []) + proposal["append_evidence"]
        fields["discussions"] = list(old.get("discussions") or []) + proposal["append_discussions"]
        if identifier.endswith(":CAVITY_SUBSTRATE_ACCESS_TUNNEL"):
            for item in fields["evidence"]:
                if item["reference"] == "PMID:23093919":
                    item["notes"] = ("CAVER computes candidate pathways between internal regions "
                        "and exterior solvent. The method paper discusses their potential roles "
                        "in molecular transport; geometry alone does not establish substrate "
                        "identity, flux or catalytic effects.")
        if identifier.endswith(":ALLOSTERIC_SUBUNIT_INTERFACE_SITE"):
            for item in fields["evidence"]:
                if item["reference"] == "PMID:42539251":
                    item["notes"] = ("The FraB preprint studies substrate half-site reactivity "
                        "in a dimer. It is context for intersubunit coupling, not evidence "
                        "for the generic effector-binding interface mechanism.")
        if identifier.endswith(":ALLOSTERIC_CRYPTIC_POCKET"):
            for item in fields["evidence"]:
                if item["reference"] == "PMID:42734533":
                    item["notes"] = ("Computational pocket-opening study: cryptic ligand-binding "
                        "sites are inaccessible in a reference apo conformation and accessible "
                        "after conformational change. This does not establish allosteric function.")
                elif item["reference"] == "PMID:42821008":
                    item["notes"] = ("Perspective on allosteric and cryptic pockets as drug-target "
                        "opportunities; contextual discussion, not a primary causal experiment.")
        for method in fields.get("detection_methods", []):
            method["edam_operation"] = ("EDAM:operation_2575" if
                method.get("tool") == "biotools:fpocket" else "EDAM:operation_2406")
            method["evidence_code"] = "ECO:0007669"
            if method.get("method_type") == "HOMOLOGY_TRANSFER" or identifier.endswith(":METAL_BINDING_SITE"):
                method["evidence_code"] = "ECO:0000305"
        if identifier.split(":")[1] in {"CAVITY", "CLEFT", "GROOVE", "POCKET", "TUNNEL"}:
            fields["definition_source"] = "https://linkml.io/valuesets/elements/LocalStructuralFeature/"
            fields["evidence"].append({
                "reference": "https://github.com/linkml/valuesets/blob/main/LICENSE",
                "notes": "The named LocalStructuralFeature enum member is distributed under "
                         "Apache-2.0, inspected 2026-10-28. Method papers retain their own terms.",
            })
        elif identifier.startswith("proteintraitsmech:ALLOSTERIC_"):
            fields["definition_source"] = ("PMID:24256730" if identifier.endswith(
                ("COVALENT_REGULATORY_SITE", "CRYPTIC_POCKET")) else "PMID:31665428")
        elif identifier.startswith("proteintraitsmech:CAVITY_"):
            fields["definition_source"] = ("PMID:9525859" if identifier.endswith(
                "SELECTIVITY_FILTER_PORE") else "PMID:23093919")
        elif identifier.endswith(":PROTEIN_BINDING_SITE"):
            fields["definition_source"] = "SO:0000410"
            fields["xrefs"] = ["SO:0000410"]
            fields["detection_methods"] = [{
                "name": "PISA interface and assembly analysis; biological binding requires review",
                "method_type": "STRUCTURAL_ALGORITHM", "tool": "biotools:pdbepisa",
                "reference": "PMID:17681537", "edam_operation": "EDAM:operation_2949",
                "evidence_code": "ECO:0007669",
                "recipe": "pisa {id} -analyse {input} {db.config} && pisa {id} -xml {db.config} > {output}",
            }]
            fields["evidence"].extend([
                {"reference": "PMID:17681537", "notes": "PISA infers assemblies and interfaces "
                 "from structural data; its predictions require biological-context review."},
                {"reference": "https://www.ccp4.ac.uk/html/pisa.html", "notes": "Author CLI "
                 "documentation specifies the session identifier, configuration file and XML "
                 "export command used here. An installed, configured PISA is a prerequisite; "
                 "the command was not executed in this curation."},
                {"reference": "PMID:9020082", "notes": "The Bcl-xL/Bak peptide complex and "
                 "interaction-disrupting variants support a representative protein-binding "
                 "interface. This does not establish a universal oligomerization mechanism."},
            ])
            fields["structural_geometry_representations"] = [{
                "structure_ref": "PDB:1BXL", "structure_source": "PDB, entry version 1.4",
                "evidence_source": "PMID:9020082; https://www.rcsb.org/structure/1BXL; inspected "
                "2026-10-28. Solution-NMR Bcl-xL chain A/Bak peptide chain B complex. "
                "Interface-containing representative; exact contact residues unspecified. "
                "No qualified UniProt occurrence asserted.",
            }]
        elif identifier.endswith(":CATALYTIC_RESIDUE"):
            fields["definition_source"] = "PMID:29106569"
        elif identifier.endswith(":METAL_BINDING_SITE"):
            fields["definition_source"] = "PMID:23155064"
            fields["evidence"].append({
                "reference": "PMID:1433293", "notes": "The carbonic-anhydrase-II study describes "
                "the zinc environment in PDB 2CBA. It supports a metal-site representative, "
                "not a universal link from metal binding to folding or catalysis.",
            })
            fields["structural_geometry_representations"] = [{
                "structure_ref": "PDB:2CBA", "structure_source": "PDB, entry version 1.5",
                "evidence_source": "PMID:1433293; https://www.rcsb.org/structure/2CBA; inspected "
                "2026-10-28. Human carbonic anhydrase II chain A, X-ray structure. "
                "Representative containing the source-described zinc site; exact donor-atom "
                "selection unspecified. No qualified UniProt occurrence asserted.",
            }]
        if identifier.endswith(":ALLOSTERIC_REGULATORY_SITE"):
            fields["definition"] = fields["definition"].replace(
                "through intramolecular coupling", "through coupling within the protein or protein complex")
        proposals.append({"identifier": identifier, "fields": fields,
                          "limitations": " ".join(p["prompt"] for p in proposal["append_discussions"]),
                          "license_disposition": "Upstream source terms retained; literature and tool "
                          "licenses are separate from the per-record source tag."})

# Apply the independent claim-level graph review to its exact inspected inputs.
graph_review = json.loads((HERE / "motifs/graph-review.json").read_text())
decisions = {row["identifier"]: row for row in graph_review["decisions"]}
for proposal in proposals:
    identifier = proposal["identifier"]
    decision = decisions.get(identifier)
    if decision is None or decision["decision"] == "retain_absence":
        continue
    fields = proposal["fields"]
    if decision["decision"] == "remove_unsupported_graph":
        fields["causal_graphs"] = None
        continue
    old = yaml.safe_load(paths[identifier].read_text())
    patch = decision["patch"]
    graphs = copy.deepcopy(old["causal_graphs"])
    graph = next(g for g in graphs if g["graph_id"] == patch["graph_id"])
    graph.update(patch["graph_updates"])
    graph["nodes"] = [node for node in graph["nodes"]
                      if node["node_id"] not in patch.get("remove_node_ids", [])]
    renames = {}
    for node in graph["nodes"]:
        before_id = node["node_id"]
        update = patch["node_updates"].get(before_id, {})
        for key in update.get("remove_fields", []):
            node.pop(key, None)
        node.update({key: value for key, value in update.items() if key != "remove_fields"})
        renames[before_id] = node["node_id"]
    for update in patch["edge_updates"]:
        edge = graph["edges"][update["index"]]
        edge.update({key: value for key, value in update.items() if key not in {"index", "evidence"}})
        edge["evidence"] = [update["evidence"]]
    graph["edges"] = [edge for i, edge in enumerate(graph["edges"])
                      if i not in patch.get("remove_edge_indices", [])]
    for edge in graph["edges"]:
        edge["subject"] = renames.get(edge["subject"], edge["subject"])
        edge["object"] = renames.get(edge["object"], edge["object"])
    fields["causal_graphs"] = graphs

records = []
for proposal in proposals:
    identifier = proposal["identifier"]
    path = paths[identifier]
    text = path.read_text()
    old = yaml.safe_load(text)
    fields = proposal["fields"]
    fields["mapping_status"] = "PROPOSED"
    fields["curation_history"] = list(old.get("curation_history") or []) + [{
        "timestamp": STAMP, "curator": "codex-gpt-6-astra",
        "action": "structural_trait_evidence_curation_20261028",
        "changes": "Updated " + ", ".join(key for key, value in fields.items()
                                         if value != old.get(key)) +
                   " using the cited sources and data/curation/structural_trait_curations.yaml. "
                   "Retained scoped evidence and method limits; no canonical protein "
                   "qualification or human REVIEWED status conferred.",
        "llm_assisted": True,
    }]
    entry = {
        "identifier": identifier, "path": str(path.relative_to(ROOT)),
        "trait_category": old["trait_category"], "input_sha256": digest(text),
        "seed_preimages": sources[identifier],
        "allow_seeded_history": bool(old.get("curation_history")),
        "limitations": proposal.get("limitations", ""),
        "license_disposition": proposal.get("license_disposition", "Existing source terms retained."),
        "blocks": {key: block(key, value) for key, value in fields.items()
                   if value != old.get(key) or key == "curation_history"},
    }
    entry["output_sha256"] = digest(apply_blocks(text, entry))
    records.append(entry)


class LiteralDumper(yaml.SafeDumper):
    pass


def literal(dumper, value):
    return dumper.represent_scalar("tag:yaml.org,2002:str", value,
                                   style="|" if "\n" in value else None)


LiteralDumper.add_representer(str, literal)
out = ROOT / "data/curation/structural_trait_curations.yaml"
out.write_text(yaml.dump({"version": 1, "records": records}, Dumper=LiteralDumper,
                         sort_keys=False, allow_unicode=True, width=100))
print(f"{len(records)} reviewed existing-ID entries -> {out.relative_to(ROOT)}")
