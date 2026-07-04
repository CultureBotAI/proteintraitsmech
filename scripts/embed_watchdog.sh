#!/usr/bin/env bash
# Watchdog for embed_records.py on Apple-Silicon MPS: the MPS backend stalls
# (uninterruptible sleep, 0% GPU) after sustained encoding of ~30k docs. The
# encoder checkpoints every 3 chunks and resumes from the partial vectors file,
# so we just burst it: run until the progress log goes quiet for STALL_S, kill,
# and relaunch (which resumes). Repeat until vectors.f16.npy covers all records.
set -u
cd "$(dirname "$0")/.."
LOG=/tmp/embed_watchdog.log
N=$(python3 -c "import glob,json;print(sum(len(json.load(open(f))) for f in glob.glob('docs/data/records.*.json')))")
STALL_S=110
: > "$LOG"

rows() { python3 -c "import numpy as np;print(np.load('data/embeddings/vectors.f16.npy').shape[0])" 2>/dev/null || echo 0; }

echo "watchdog: target $N records" | tee -a "$LOG"
for burst in $(seq 1 20); do
  R=$(rows)
  if [ "$R" -ge "$N" ]; then echo "DONE: $R/$N" | tee -a "$LOG"; break; fi
  echo "burst $burst: resuming from $R/$N" | tee -a "$LOG"
  python3 scripts/embed_records.py >>"$LOG" 2>&1 &
  PID=$!
  last=""; quiet=0
  while kill -0 "$PID" 2>/dev/null; do
    sleep 20
    cur=$(grep -aE '/[0-9]' "$LOG" | tail -1)
    if [ "$cur" = "$last" ]; then quiet=$((quiet+20)); else last="$cur"; quiet=0; fi
    if [ "$quiet" -ge "$STALL_S" ]; then
      echo "  stalled ${quiet}s at: $cur — killing burst" | tee -a "$LOG"
      kill "$PID" 2>/dev/null; sleep 3; kill -9 "$PID" 2>/dev/null
      break
    fi
  done
  wait "$PID" 2>/dev/null
  # if the process exited cleanly at full coverage, the next rows() check ends it
done
echo "watchdog finished: $(rows)/$N" | tee -a "$LOG"
