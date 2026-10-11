#!/usr/bin/env python3
"""Registered API fetcher entrypoint for cross-Mech discovery, never promotion."""
import sys

from cross_mech_proteins import main

if __name__ == "__main__":
    raise SystemExit(main(["discover", *sys.argv[1:]]))
