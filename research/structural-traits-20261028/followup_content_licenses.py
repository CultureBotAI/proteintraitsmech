"""Scope three project-content license tags; never license upstream exports."""
import datetime
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from structural_trait_curations import apply_blocks, digest

dispositions = {
    "PROTEIN_BINDING_SITE": "The SO:0000410-derived definition/mapping retains Sequence Ontology CC-BY-4.0 attribution. The legacy valuesets source retains Apache-2.0 attribution. Cited 3did/PISA/Bcl-xL publications and PISA software retain their own terms; PDB archive metadata are CC0-1.0. No article prose, figures, coordinates, database export or software is redistributed.",
    "CATALYTIC_RESIDUE": "The SO:0001104 mapping retains Sequence Ontology CC-BY-4.0 attribution; legacy valuesets provenance retains Apache-2.0 attribution. M-CSA/Bartlett publications, web content and any database exports retain their own terms. No article prose, figures or M-CSA data export is copied; rights for future source ingestion are not cleared here.",
    "METAL_BINDING_SITE": "Legacy valuesets provenance retains Apache-2.0 attribution. The MetalPDB article's CC-BY-NC-3.0 terms do not authorize redistribution of MetalPDB data here. PDB archive metadata are CC0-1.0; primary structural article rights are separate. No MetalPDB tables, article prose, figures or coordinates are copied.",
}
path = ROOT / "data/curation/structural_trait_curations.yaml"
data = yaml.safe_load(path.read_text())
stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
changed = 0
for entry in data["records"]:
    key = entry["identifier"].split(":")[1]
    if key not in dispositions:
        continue
    before = (ROOT / entry["path"]).read_text()
    record = yaml.safe_load(before)
    if record.get("license"):
        continue
    if digest(before) != entry["output_sha256"]:
        raise ValueError("License disposition requires exact inspected output")
    snapshot = Path(__file__).resolve().parent / "followup-preimages" / Path(entry["path"]).name
    snapshot.write_text(before)
    disposition = "Project-authored factual synthesis and annotations are CC-BY-4.0 under LICENSE/ LICENSE-DATA. " + dispositions[key]
    record["evidence"].append({"reference": "https://github.com/CultureBotAI/proteintraitsmech/blob/main/LICENSE", "notes": disposition})
    record["curation_history"].append({
        "timestamp": stamp, "curator": "codex-gpt-6-astra", "action": "EDIT", "llm_assisted": True,
        "changes": "Recorded CC-BY-4.0 for project-authored factual synthesis/annotations after source-specific rights review; retained upstream attributions and excluded third-party exports/software from that license claim.",
    })
    entry["blocks"]["license"] = "license: CC-BY-4.0\n"
    for field in ("evidence", "curation_history"):
        entry["blocks"][field] = yaml.safe_dump({field: record[field]}, sort_keys=False, width=98)
    entry["license_disposition"] = disposition
    entry["initial_input_sha256"] = entry["input_sha256"]
    entry["input_sha256"] = entry["prior_output_sha256"] = digest(before)
    entry["allow_proposed_followup"] = True
    entry["followup_preimage"] = str(snapshot.relative_to(ROOT))
    entry["output_sha256"] = digest(apply_blocks(before, entry))
    changed += 1


class LiteralDumper(yaml.SafeDumper):
    pass


def literal(dumper, value):
    return dumper.represent_scalar("tag:yaml.org,2002:str", value,
                                   style="|" if "\n" in value else None)


LiteralDumper.add_representer(str, literal)
path.write_text(yaml.dump(data, Dumper=LiteralDumper, sort_keys=False, allow_unicode=True, width=100))
print(f"Prepared {changed} project-content license dispositions; no trait records written")
