"""2026-10-29 supplemental coordination scan for the tunnel bottleneck canary.

Input: parent's open-work-prewrite.json, using retained scan_open_work.py.
Output: open-work-bottleneck-scan.json; original scan/report remain unchanged.
Task: structural discovery after PR1202, exact proposed TUNNEL_BOTTLENECK ID.
This is offline lexical coordination triage, not scientific review/reservation.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
import scan_open_work as scan  # noqa: E402

scan.PATTERNS["tunnel_bottleneck"] = (
    r"\bbottleneck\b|tunnel[\s_-]*bottleneck|tunnel.{0,40}constriction|"
    r"constriction.{0,40}(?:tunnel|pathway)|narrowest.{0,40}(?:pathway|tunnel)|"
    r"(?:SO:0000912|SO:0001141)"
)
scan.OUTPUT = Path(__file__).resolve().parent / "open-work-bottleneck-scan.json"
scan.main()
report = json.loads(scan.OUTPUT.read_text())
report["supplement_helper_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
report["supplement_scope"] = "Added bottleneck/tunnel constriction/narrowest pathway plus planned SO:0000912 and SO:0001141 identifiers. TUNNEL_BOTTLENECK is also matched through the case-insensitive underscore variant."
scan.OUTPUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
