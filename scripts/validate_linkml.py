#!/usr/bin/env python3
"""Validate every ProteinTraitRecord YAML by invoking the
`linkml-validate` CLI. Files are batched (default 200 per invocation)
so 18K records finish in ~1-2 minutes instead of ~4h at one subprocess
per file. When a batch fails, the batch is re-run one file at a time to
pinpoint the offender.

Usage:
  python3 scripts/validate_linkml.py                    # all traits
  python3 scripts/validate_linkml.py data/traits/sequence/motif
  python3 scripts/validate_linkml.py data/traits/**/foo.yaml
  python3 scripts/validate_linkml.py --batch 50 …       # override batch size
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA = REPO_ROOT / "src" / "proteintraitsmech" / "schema" / "proteintraitsmech.yaml"
DEFAULT_ROOT = REPO_ROOT / "data" / "traits"
DEFAULT_BATCH = 200


def collect_targets(paths: list[str]) -> list[Path]:
    if not paths:
        return sorted(DEFAULT_ROOT.rglob("*.yaml"))
    files: list[Path] = []
    for arg in paths:
        p = Path(arg)
        if not p.is_absolute():
            p = REPO_ROOT / p
        if p.is_dir():
            files.extend(sorted(p.rglob("*.yaml")))
        elif p.is_file():
            files.append(p)
        else:
            matches = sorted(REPO_ROOT.glob(arg))
            if not matches:
                print(f"warn: no match for {arg}", file=sys.stderr)
            files.extend(matches)
    return files


def run_linkml(files: list[Path]) -> tuple[bool, str]:
    cmd = [
        "linkml-validate",
        "-s",
        str(SCHEMA),
        "--target-class",
        "ProteinTraitRecord",
        *(str(f) for f in files),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.returncode == 0, (proc.stdout + proc.stderr).strip()


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", help="files/dirs/globs; default: data/traits")
    parser.add_argument("--batch", type=int, default=DEFAULT_BATCH,
                        help=f"files per linkml-validate call (default {DEFAULT_BATCH})")
    args = parser.parse_args(argv)

    targets = collect_targets(args.paths)
    if not targets:
        print("no YAML files matched", file=sys.stderr)
        return 2
    n_batches = (len(targets) + args.batch - 1) // args.batch
    print(
        f"Validating {len(targets)} records against "
        f"{SCHEMA.relative_to(REPO_ROOT)} in {n_batches} batch(es) of {args.batch}"
    )

    failures: list[tuple[Path, str]] = []
    for bi in range(n_batches):
        batch = targets[bi * args.batch : (bi + 1) * args.batch]
        ok, out = run_linkml(batch)
        if ok:
            print(f"  [{bi + 1}/{n_batches}] ok ({len(batch)} files)")
            continue
        # Batch failed → isolate offenders by re-validating one at a time.
        print(f"  [{bi + 1}/{n_batches}] batch FAILED — isolating…", file=sys.stderr)
        for f in batch:
            ok_f, out_f = run_linkml([f])
            if not ok_f:
                rel = f.relative_to(REPO_ROOT)
                failures.append((f, out_f))
                print(f"    FAIL {rel}", file=sys.stderr)
                for line in out_f.splitlines():
                    print(f"      {line}", file=sys.stderr)

    print()
    print(f"Passed: {len(targets) - len(failures)}/{len(targets)}")
    if failures:
        print(f"Failed: {len(failures)}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
