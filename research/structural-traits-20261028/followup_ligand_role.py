"""Prepare the independent ChEBI role/material correction in the ledger only."""
import datetime
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from structural_trait_curations import apply_blocks, digest

path = ROOT / "data/curation/structural_trait_curations.yaml"
data = yaml.safe_load(path.read_text())
entry = next(e for e in data["records"] if e["identifier"] ==
             "proteintraitsmech:ALLOSTERIC_COVALENT_REGULATORY_SITE")
before = (ROOT / entry["path"]).read_text()
record = yaml.safe_load(before)
graph = record["causal_graphs"][0]
if not any(n["node_id"] == "CHEBI:35224" for n in graph["nodes"]):
    raise SystemExit("No role-as-ligand node remains; no ledger or trait change")
if digest(before) != entry["output_sha256"]:
    raise ValueError("Current record is not the reviewed prior output")
snapshot = Path(__file__).resolve().parent / "followup-preimages/covalent-second-pass.yaml"
snapshot.write_text(before)
for node in graph["nodes"]:
    if node["node_id"] == "CHEBI:35224":
        node.update(node_id="kras_g12c_inhibitors", label="Tested KRAS(G12C) inhibitors",
                    local=True, node_type="LIGAND",
                    description="The tested inhibitor molecules in Ostrem et al. (2013). This local node groups that study set; it does not assert a single chemical identity or equate a biochemical role with a molecule.")
        node.pop("grounding", None)
for edge in graph["edges"]:
    for endpoint in ("subject", "object"):
        if edge[endpoint] == "CHEBI:35224":
            edge[endpoint] = "kras_g12c_inhibitors"
record["evidence"].append({
    "reference": "https://www.ebi.ac.uk/chebi/searchId.do?chebiId=CHEBI:35224",
    "notes": "ChEBI effector denotes a biochemical role rather than a material entity. The KRAS graph represents the tested inhibitor molecules as a local ligand set without assigning that role identifier as their chemical identity.",
})
record["curation_history"].append({
    "timestamp": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "curator": "codex-gpt-6-astra", "action": "EDIT", "llm_assisted": True,
    "changes": "Resolved independent graph review: replaced the ChEBI effector role used as a material input with a local study-scoped inhibitor-set LIGAND. Preserved all three experimental-scope edges and prior history; no qualification or human sign-off.",
})
for key in ("causal_graphs", "evidence", "curation_history"):
    entry["blocks"][key] = yaml.safe_dump({key: record[key]}, sort_keys=False, width=98)
entry["followup_preimage_history"] = [{"path": entry["followup_preimage"],
                                       "sha256": entry["prior_output_sha256"]}]
entry["followup_preimage"] = str(snapshot.relative_to(ROOT))
entry["prior_output_sha256"] = entry["input_sha256"] = digest(before)
entry["output_sha256"] = digest(apply_blocks(before, entry))


class LiteralDumper(yaml.SafeDumper):
    pass


def literal(dumper, value):
    return dumper.represent_scalar("tag:yaml.org,2002:str", value,
                                   style="|" if "\n" in value else None)


LiteralDumper.add_representer(str, literal)
path.write_text(yaml.dump(data, Dumper=LiteralDumper, sort_keys=False, allow_unicode=True, width=100))
print("Prepared one role/material follow-up; no trait records written")
