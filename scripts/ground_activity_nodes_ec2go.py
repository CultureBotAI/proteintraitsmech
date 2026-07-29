#!/usr/bin/env python3
"""Ground M-CSA `activity` nodes to GO molecular function via GO's own ec2go.

  python3 scripts/ground_activity_nodes_ec2go.py            # dry run
  python3 scripts/ground_activity_nodes_ec2go.py --apply

Every M-CSA graph carries one MOLECULAR_FUNCTION node for the enzyme's activity.
M-CSA gives EC numbers but no GO term, so those 1,001 nodes were written with
`xrefs: [EC:…]` and no `grounding` — the largest single block of ungrounded
non-STATE nodes left in the corpus.

GO publishes the mapping itself (`external2go/ec2go`), so this is a lookup
against an authoritative table, not an inference. Cached at data/raw/ec/ec2go.

EXACT VERSUS CLASS-LEVEL
------------------------
905 nodes have a GO term for their exact EC. 96 do not, and only match a parent
EC class (e.g. `1.1.1.-`). Those are still grounded, because a class-level
molecular function is true of the enzyme, but the node description says so
explicitly — a reader must be able to tell "alcohol dehydrogenase (NAD+)
activity" from "oxidoreductase activity, acting on CH-OH group of donors"
without opening the source.
"""

from __future__ import annotations

import argparse
import collections
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
EC2GO = REPO / "data" / "raw" / "ec" / "ec2go"
MCSA_DIR = REPO / "data" / "traits" / "structure" / "active_site" / "mcsa"


def load_ec2go() -> dict:
    out = {}
    for line in EC2GO.open(encoding="utf-8"):
        m = re.match(r"^EC:(\S+)\s*>\s*GO:(.+?)\s*;\s*(GO:\d+)", line)
        if m:
            out[m.group(1)] = (m.group(3), m.group(2).strip())
    return out


def lookup(ecs, table):
    """(GO id, GO label, exact?) for the first EC that resolves."""
    for e in ecs:
        if e in table:
            go, label = table[e]
            return go, label, True
    for e in ecs:                       # fall back to the EC class
        parts = e.split(".")
        for k in (3, 2, 1):
            cls = ".".join(parts[:k] + ["-"] * (4 - k))
            if cls in table:
                go, label = table[cls]
                return go, label, False
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    table = load_ec2go()
    stat = collections.Counter()

    for f in sorted(MCSA_DIR.glob("*.yaml")):
        text = f.read_text(encoding="utf-8")
        # the activity node is the only one with `node_id: activity`; edit it in
        # place so the rest of the record stays byte-identical
        m = re.search(r"(?m)^(\s+)- node_id: activity\n(?:\1  .*\n|\1    .*\n)*", text)
        if not m:
            continue
        stat["activity nodes"] += 1
        block = m.group(0)
        if re.search(r"^\s+grounding:", block, re.M):
            stat["already grounded"] += 1
            continue
        ecs = re.findall(r"- EC:(\S+)", block)
        if not ecs:
            stat["no EC xref"] += 1
            continue
        hit = lookup(ecs, table)
        if not hit:
            stat["no GO for any EC"] += 1
            continue
        go, label, exact = hit
        indent = m.group(1) + "  "
        if exact:
            desc = (f"GO molecular function for EC:{ecs[0]}, via GO's own ec2go "
                    f"mapping.")
            stat["grounded (exact EC)"] += 1
        else:
            desc = (f"Grounded to the EC *class*-level GO term ({label}); GO's "
                    f"ec2go has no term for the exact EC:{ecs[0]}, so this is "
                    f"broader than the enzyme's specific activity.")
            stat["grounded (EC class level)"] += 1
        # insert after node_type so the block keeps the field order used elsewhere
        new_block = re.sub(r"(?m)^(\s+node_type: MOLECULAR_FUNCTION\n)",
                           rf"\1{indent}grounding: {go}\n"
                           rf"{indent}description: {desc}\n",
                           block, count=1)
        if new_block == block:
            stat["could not splice"] += 1
            continue
        if args.apply:
            f.write_text(text.replace(block, new_block, 1), encoding="utf-8")

    for k, v in stat.most_common():
        print(f"  {k:<28} {v:>6,}", file=sys.stderr)
    if not args.apply:
        print("\nDry run — pass --apply to write.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
