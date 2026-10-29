"""Prepare two independently reviewed follow-ups; write ledger, never trait records.

Run after the first guarded application. Exact prior outputs and new events are
retained; the registered editor separately previews/validates/applies the result.
"""
import copy
import datetime
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from structural_trait_curations import apply_blocks, digest

LEDGER = ROOT / "data/curation/structural_trait_curations.yaml"
data = yaml.safe_load(LEDGER.read_text())
targets = {"proteintraitsmech:ALLOSTERIC_SUBUNIT_INTERFACE_SITE",
           "proteintraitsmech:ALLOSTERIC_COVALENT_REGULATORY_SITE"}
stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
changed = 0
for entry in data["records"]:
    if entry["identifier"] not in targets:
        continue
    before = (ROOT / entry["path"]).read_text()
    if entry.get("allow_proposed_followup"):
        if digest(before) not in {entry["input_sha256"], entry["output_sha256"]}:
            raise ValueError("Follow-up input/output drift")
        continue
    if digest(before) != entry["output_sha256"]:
        raise ValueError("Follow-up requires exact first-pass output")
    record = yaml.safe_load(before)
    old_entry = copy.deepcopy(entry)
    snapshots = Path(__file__).resolve().parent / "followup-preimages"
    snapshots.mkdir(exist_ok=True)
    snapshot = snapshots / Path(entry["path"]).name
    snapshot.write_text(before)
    if entry["identifier"].endswith("SUBUNIT_INTERFACE_SITE"):
        synonyms = copy.deepcopy(record["synonyms"])
        found = False
        for synonym in synonyms:
            if synonym["synonym_text"] == "inter-subunit allosteric pocket":
                synonym["synonym_type"] = "NARROW_SYNONYM"
                found = True
        if not found:
            raise ValueError("Reviewed synonym not found")
        entry["blocks"]["synonyms"] = yaml.safe_dump({"synonyms": synonyms}, sort_keys=False)
        change = "Classified inter-subunit allosteric pocket as a narrow synonym of the broader site class."
    else:
        graphs = copy.deepcopy(record["causal_graphs"])
        graph = graphs[0]
        found = False
        for node in graph["nodes"]:
            if node["node_id"] == "GO:0036094":
                node.update(node_id="kras_g12c_covalent_capture", local=True,
                            label="Covalent inhibitor capture by KRAS(G12C)",
                            node_type="BIOLOGICAL_PROCESS",
                            description="Covalent attachment of the tested inhibitors to mutant Cys12 in Ostrem et al. (2013). This is a study-scoped process, not GO noncovalent binding.")
                node.pop("grounding", None)
                found = True
        if not found:
            raise ValueError("Reviewed covalent-capture node not found")
        for edge in graph["edges"]:
            for endpoint in ("subject", "object"):
                if edge[endpoint] == "GO:0036094":
                    edge[endpoint] = "kras_g12c_covalent_capture"
        entry["blocks"]["causal_graphs"] = yaml.safe_dump({"causal_graphs": graphs}, sort_keys=False, width=98)
        evidence = record["evidence"] + [{
            "reference": "https://amigo.geneontology.org/amigo/term/GO:0005488",
            "notes": "GO binding is defined as noncovalent; its small-molecule-binding descendant GO:0036094 does not describe covalent attachment. The scoped graph uses a local process node for the observed KRAS(G12C) inhibitor capture.",
        }]
        entry["blocks"]["evidence"] = yaml.safe_dump({"evidence": evidence}, sort_keys=False, width=98)
        change = "Replaced noncovalent GO:0036094 grounding with a local study-scoped covalent-capture process; preserved the three supported KRAS(G12C) edges."
    history = record["curation_history"] + [{
        "timestamp": stamp, "curator": "codex-gpt-6-astra", "action": "EDIT",
        "changes": change + " Independent post-curation review correction; no human sign-off or protein qualification.",
        "llm_assisted": True,
    }]
    entry["blocks"]["curation_history"] = yaml.safe_dump({"curation_history": history}, sort_keys=False, width=98)
    entry["prior_output_sha256"] = entry["input_sha256"] = digest(before)
    entry["initial_input_sha256"] = old_entry["input_sha256"]
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
LEDGER.write_text(yaml.dump(data, Dumper=LiteralDumper, sort_keys=False, allow_unicode=True, width=100))
print(f"Prepared {changed} follow-ups; no trait records written")
