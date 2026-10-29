#!/usr/bin/env python3
"""Freeze and strictly validate one already-reviewed manifest row; no target writes."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PIN = "d5b2a0b813eafe48f9bd18fbba5dd077095453b0360e31824dc41aab89c6b7bc"
MANIFEST = ROOT / "data/curation/structural_trait_discovery.yaml"
sha = lambda b: hashlib.sha256(b).hexdigest()
raw = MANIFEST.read_bytes()
assert sha(raw) == PIN, "Manifest drift: require fresh scientific review"
data = yaml.safe_load(raw)
rows = [r for r in data["records"] if r["record"]["identifier"] == "proteintraitsmech:TUNNEL_BOTTLENECK"]
assert len(rows) == 1
snapshot = OUT / "bottleneck-canary-reviewed-row-20261029T0704Z.yaml"
with snapshot.open("x") as stream:
    yaml.safe_dump(rows[0]["record"], stream, sort_keys=False, allow_unicode=True)
sys.path.insert(0, str(ROOT / "scripts"))
from validate_strict import validate_one
errors = validate_one(snapshot)
inputs = [
    MANIFEST,
    ROOT / "src/proteintraitsmech/schema/proteintraitsmech.yaml",
    ROOT / "data/traits/structure/cavity/tunnel.yaml",
    ROOT / "scripts/seed_structural_discovery.py",
    ROOT / "scripts/validate_strict.py",
    ROOT / "research/structural-discovery-20261028/cavities/tunnel-bottleneck-card.json",
    Path("/tmp/caver-discovery-userguide.pdf"),
    Path("/tmp/caver-discovery-userguide.txt"),
    snapshot,
    Path(__file__),
]
result = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "command": ".venv/bin/python research/structural-discovery-20261028/motifs/check_bottleneck_canary.py",
    "validation_function": "scripts.validate_strict.validate_one (closed JsonschemaValidationPlugin plus native semantic checks)",
    "errors": errors,
    "inputs": [{"path": str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p), "sha256": sha(p.read_bytes())} for p in inputs],
    "live_manifest_unchanged_after_validation": sha(MANIFEST.read_bytes()) == PIN,
    "target_mutations": [],
}
with (OUT / "bottleneck-canary-validation-20261029T0704Z.json").open("x") as stream:
    json.dump(result, stream, indent=2)
    stream.write("\n")
print(json.dumps(result, indent=2))
raise SystemExit(bool(errors))
