"""Read-only audit supporting the biophysical-trait assessment.

Run from any directory with a Python that has PyYAML:
  python research/biophysical-traits-2026-09-23/audit_existing.py

Uses pathlib and rg --no-ignore --hidden, so ignored corpus files are included.
Writes only audit.json alongside this script. It does not curate records.
"""

from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess

import yaml


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TRAITS = ROOT / "data/traits"
LOADER = getattr(yaml, "CSafeLoader", yaml.SafeLoader)


def matches(pattern):
    result = subprocess.run(
        ["rg", "--no-ignore", "--hidden", "-l", "-g", "*.yaml", pattern, str(TRAITS)],
        capture_output=True, text=True, check=False,
    )
    if result.returncode not in (0, 1):
        raise RuntimeError(result.stderr)
    return sorted(str(Path(p).relative_to(ROOT)) for p in result.stdout.splitlines())


def summarize(path):
    raw = path.read_bytes()
    d = yaml.load(raw, Loader=LOADER)
    return {
        "path": str(path.relative_to(ROOT)),
        "sha256": hashlib.sha256(raw).hexdigest(),
        **{k: d.get(k) for k in ("identifier", "label", "trait_axis", "trait_category",
                                "mapping_status", "term_kind", "definition_source")},
        "parent_traits": d.get("parent_traits") or [],
        "canonical_examples": len(d.get("canonical_examples") or []),
        "evidence_items": len(d.get("evidence") or []),
        "detection_methods": len(d.get("detection_methods") or []),
    }


files = sorted(TRAITS.rglob("*.yaml"))
pato_paths = matches(r"^identifier:[ \t]*[\"']?PATO:[0-9]+[\"']?[ \t]*$")
pato = [summarize(ROOT / p) for p in pato_paths]
conditions = [summarize(p) for p in sorted((TRAITS / "structure/stability/conditions").glob("*.yaml"))]
scaffold = {"PATO:0000141", "PATO:0002182", "PATO:0002303", "PATO:0002305",
            "PATO:0045001", "PATO:0001018", "PATO:0001546"}

obo_path = ROOT / "data/raw/PATO.obo"
obo = obo_path.read_text()
candidates = {"PATO:0001886", "PATO:0001887", "PATO:0002186", "PATO:0002187",
              "PATO:0002188", "PATO:0002420"}
ontology_terms = []
for block in obo.split("[Term]")[1:]:
    m = re.search(r"^id: (.+)$", block, re.M)
    if m and m.group(1) in candidates:
        ontology_terms.append({
            "identifier": m.group(1),
            "label": re.search(r"^name: (.+)$", block, re.M).group(1),
            "parents": re.findall(r"^is_a: (.+)$", block, re.M),
            "obsolete": "is_obsolete: true" in block,
        })

schema_path = ROOT / "src/proteintraitsmech/schema/proteintraitsmech.yaml"
schema = yaml.load(schema_path.read_text(), Loader=LOADER)
classes = ("ProteinTraitRecord", "CanonicalExample", "ProteinReference", "TraitOccurrence", "EvidenceItem")
attributes = {name: sorted(schema["classes"][name].get("attributes", {})) for name in classes}
q = "[\"']?"
category_hits = {cat: matches(r"^trait_category:[ \t]*" + q + cat + q + r"[ \t]*$")
                 for cat in ("SEQ_COMPOSITION", "SEQ_LOW_COMPLEXITY", "SEQ_DISORDER")}
names = r"(hydrophilicity|hydrophilic|polarity|polar polarity|nonpolar polarity|isoelectric point|net charge)"
generic_label_hits = matches(r"(?i)^label:[ \t]*" + q + names + q + r"[ \t]*$")

result = {
    "audit_date": "2026-09-23",
    "scope": "Current local worktree, including gitignored files; not a claim about remote main.",
    "yaml_file_count": len(files),
    "pato_file_count": len(pato),
    "pato_category_counts": dict(Counter(r["trait_category"] for r in pato)),
    "pato_scaffolding_count": sum(r["identifier"] in scaffold for r in pato),
    "pato_non_scaffolding_count": sum(r["identifier"] not in scaffold for r in pato),
    "pato_records": pato,
    "condition_stability_count": len(conditions),
    "condition_stability_records": conditions,
    "category_record_counts": {k: len(v) for k, v in category_hits.items()},
    "category_record_paths": category_hits,
    "exact_generic_label_matches": generic_label_hits,
    "pato_source_release": re.search(r"^data-version: (.+)$", obo, re.M).group(1),
    "pato_source_sha256": hashlib.sha256(obo_path.read_bytes()).hexdigest(),
    "additional_pato_terms": ontology_terms,
    "schema_sha256": hashlib.sha256(schema_path.read_bytes()).hexdigest(),
    "schema_attributes": attributes,
    "trait_category_definitions": schema["enums"]["ProteinTraitCategoryEnum"]["permissible_values"],
}
(HERE / "audit.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({k: result[k] for k in ("yaml_file_count", "pato_file_count",
    "pato_category_counts", "pato_scaffolding_count", "pato_non_scaffolding_count",
    "condition_stability_count", "category_record_counts", "exact_generic_label_matches")}, indent=2))
