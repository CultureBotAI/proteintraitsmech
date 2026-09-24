"""Focused tests for InterPro compact/grouped sidecar extraction."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "fetch_interpro_frame.py"
sys.path.insert(0, str(REPO / "scripts"))
SPEC = importlib.util.spec_from_file_location("fetch_interpro_frame", SCRIPT)
assert SPEC and SPEC.loader
F = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = F
SPEC.loader.exec_module(F)


def test_extract_entry_matches_preserves_interpro_location_groups() -> None:
    flat, grouped = F.extract_entry_matches(
        [
            {
                "metadata": {
                    "source_database": "cathgene3d",
                    "accession": "G3DSA:1.10.10.10",
                },
                "proteins": [
                    {
                        "entry_protein_locations": [
                            {"fragments": [{"start": 7, "end": 9}, {"start": 2, "end": 4}]},
                            {"fragments": [{"start": 20, "end": 18}]},
                        ]
                    }
                ],
            },
            {
                "metadata": {"source_database": "pfam", "accession": "PF00001"},
                "proteins": [
                    {
                        "entry_protein_locations": [
                            {"fragments": [{"start": "3", "end": "5"}]},
                            {"fragments": [{"start": "bad", "end": "6"}]},
                        ]
                    }
                ],
            },
        ]
    )

    assert flat == {
        "CATH:1.10.10.10": [[7, 9], [2, 4], [18, 20]],
        "Pfam:PF00001": [[3, 5]],
    }
    assert grouped == {
        "CATH:1.10.10.10": [[[7, 9], [2, 4]], [[18, 20]]],
        "Pfam:PF00001": [[[3, 5]]],
    }
