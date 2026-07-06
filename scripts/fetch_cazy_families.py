#!/usr/bin/env python3
"""Fetch the CAZy family classification + resource content from cazy.org.

CAZy (Carbohydrate-Active enZymes, © CNRS / Aix-Marseille Université / INRAE,
AFMB) classifies carbohydrate-active enzymes into six sequence-based classes —
GH, GT, PL, CE, AA, CBM — grouped into clans that share a fold and catalytic
machinery. There is no open bulk download of the family-level metadata (the
cazy_data.zip is the per-protein dump), so we scrape the per-family pages.

License: CAZy content is © AFMB, academic-use, NOT openly licensed. Records seeded
from this are stamped with that license and FLAGGED (the corpus is otherwise CC0).

For each family we capture: clan, mechanism, catalytic 3D fold, note, and the
"Activities in Family" table (EC numbers + activity names). Cached, resumable, and
polite (a short delay per request).

Output (gitignored raw): data/raw/cazy/families.json
  { "GH1": {"class":"GH","clan":"GH-A","mechanism":"Retaining",
            "fold":"(β/α)8 barrel","note":"...","ec":["3.2.1.21",...],
            "activities":["β-glucosidase",...],"n_activities":35}, ... }
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW = REPO_ROOT / "data" / "raw" / "cazy"
OUT = RAW / "families.json"
UA = "Mozilla/5.0 (ProteinTraitsMech academic KB ingest; +https://github.com/CultureBotAI)"

CLASS_PAGES = {
    "GH": "Glycoside-Hydrolases.html",
    "GT": "GlycosylTransferases.html",
    "PL": "Polysaccharide-Lyases.html",
    "CE": "Carbohydrate-Esterases.html",
    "AA": "Auxiliary-Activities.html",
    "CBM": "Carbohydrate-Binding-Modules.html",
}
FAM_RE = re.compile(r"\b(GH|GT|PL|CE|AA|CBM)(\d+)\.html")


def get(url: str, tries: int = 4) -> str:
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=45) as r:
                return r.read().decode("utf-8", "replace")
        except Exception:  # noqa: BLE001
            if i == tries - 1:
                raise
            time.sleep(2 * (i + 1))
    return ""


def clean(s: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", " ", s or "")).replace("\xa0", " ").strip()


def field(h: str, label: str) -> str | None:
    m = re.search(re.escape(label) + r"\s*</td>\s*<td[^>]*>(.*?)</td>", h, re.S | re.I)
    if not m:
        m = re.search(re.escape(label) + r".{0,80}?<td[^>]*>(.*?)</td>", h, re.S | re.I)
    return re.sub(r"\s+", " ", clean(m.group(1))) if m else None


def parse_activities(h: str) -> tuple[list[str], list[str]]:
    """From the 'pos_onglet' activities table: (distinct EC list, activity names)."""
    tbl = re.search(r'id="pos_onglet".*?</table>', h, re.S)
    ecs, names = [], []
    if not tbl:
        return ecs, names
    for row in re.findall(r"<tr[^>]*>(.*?)</tr>", tbl.group(0), re.S):
        cells = [clean(c) for c in re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)]
        if len(cells) < 3 or cells[0].lower().startswith("activity"):
            continue
        ec, name = cells[1].strip(), cells[2].strip()
        for e in re.findall(r"\d+\.\d+\.\d+\.\d+", ec):
            if e not in ecs:
                ecs.append(e)
        if name and name not in names:
            names.append(name)
    return ecs, names


def family_ids() -> list[str]:
    fams: list[str] = []
    for cls, page in CLASS_PAGES.items():
        h = get(f"https://www.cazy.org/{page}")
        found = sorted({f"{m.group(1)}{m.group(2)}" for m in FAM_RE.finditer(h)
                        if m.group(1) == cls}, key=lambda x: int(x[len(cls):]))
        print(f"  {cls}: {len(found)} families")
        fams.extend(found)
    return fams


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--limit", type=int, default=0, help="cap families (testing)")
    ap.add_argument("--delay", type=float, default=0.25, help="polite delay per request")
    args = ap.parse_args()

    RAW.mkdir(parents=True, exist_ok=True)
    cache: dict = json.loads(OUT.read_text()) if OUT.exists() else {}
    print("Enumerating families from class pages…")
    fams = family_ids()
    if args.limit:
        fams = fams[: args.limit]
    print(f"{len(fams)} families total; {len(cache)} already cached")

    for i, fam in enumerate(fams):
        if fam in cache:
            continue
        cls = re.match(r"[A-Z]+", fam).group(0)
        h = get(f"https://www.cazy.org/{fam}.html")
        ecs, names = parse_activities(h)
        cache[fam] = {
            "class": cls,
            "clan": field(h, "Clan"),
            "mechanism": field(h, "Mechanism"),
            "fold": field(h, "3D Structure Status"),
            "note": field(h, "Note"),
            "ec": ecs,
            "activities": names[:12],
            "n_activities": len(names),
        }
        if i % 25 == 0:
            OUT.write_text(json.dumps(cache, separators=(",", ":")))
            print(f"  {i+1}/{len(fams)} — {fam}: clan={cache[fam]['clan']} "
                  f"ec={len(ecs)} act={len(names)}")
        time.sleep(args.delay)

    OUT.write_text(json.dumps(cache, sort_keys=True, indent=0))
    print(f"wrote {len(cache)} families → {OUT.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
