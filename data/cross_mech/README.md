# Cross-Mech protein snapshot

What the sibling Mechs say about proteins, pinned to exact commits. Strategy, channel
rules, statuses, and the inclusion route: [research/cross-mech-protein-examples.md](../../research/cross-mech-protein-examples.md).

- `protein_mentions.jsonl` — one canonical-JSON row per UniProtKB protein mention in a
  sibling record (`mech`, `record_path`, JSON `pointer`, `protein_id`, the classifying
  `channel`, `role`, `relation`, and the sibling `annotations` that name its trait).
  Rows are sorted by (`mech`, `record_path`, `pointer`).
- `manifest.json` — the claw fleet-manifest pin, each Mech's scanned commit and record
  globs, the channel-rule digest, the SHA-256 of `protein_mentions.jsonl`, and counts.

Never hand-edit either file. Regenerate both together and commit the diff:

```bash
just scan-cross-mech-proteins --fetch --apply   # rescan every sibling at origin/main
just check-cross-mech-proteins --local          # integrity + drift against checkouts
just audit-cross-mech-proteins                  # statuses -> reports/cross-mech/ (ignored)
```

A sibling assertion recorded here is discovery provenance only. Nothing in this
directory qualifies a canonical example; that happens only through the UniProt
grounding funnel.
