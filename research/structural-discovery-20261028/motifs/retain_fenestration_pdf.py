#!/usr/bin/env python3
"""2026-10-29: retain already-downloaded primary evidence for discovery review.

Goal: parent-owned structural discovery, coordination #1200/#1201/#1204.
Input: /tmp/nalcn-fenestration.pdf supplied by cavity researcher, exact hash pinned.
Original URL: https://pdfs.semanticscholar.org/9044/6796fd3bbb5d18c8921be8d527eeaa8a3a10.pdf
Outputs: unchanged PDF, pdftotext extraction, and provenance JSON beside this file.
The /tmp input is historical and not portable; retained PDF plus hash is replay input.
No corpus, Git, native review bundle or live-session mutation.
"""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import subprocess
HERE=Path(__file__).resolve().parent
source=Path('/tmp/nalcn-fenestration.pdf')
raw=source.read_bytes()
digest=hashlib.sha256(raw).hexdigest()
assert digest=='2e41cc55e593194f998f2656d2d0101ce9d5a9d5236e5673f02abc4638498b8b'
destination=HERE/'fenestration-pnas-published.pdf'
textpath=HERE/'fenestration-pnas-published.txt'
assert not textpath.exists()
with destination.open('xb') as stream:
    stream.write(raw)
result=subprocess.run(['pdftotext','-layout',str(destination),str(textpath)],capture_output=True,text=True)
assert result.returncode==0, result.stderr
record={'date':datetime.now(timezone.utc).isoformat(),'source_url':'https://pdfs.semanticscholar.org/9044/6796fd3bbb5d18c8921be8d527eeaa8a3a10.pdf','tmp_input':str(source),'pdf':str(destination),'pdf_sha256':digest,'text':str(textpath),'text_sha256':hashlib.sha256(textpath.read_bytes()).hexdigest(),'command':result.args,'exit_code':result.returncode,'goal_reference':'Parent-owned structural discovery goal; #1200/#1201/#1204 coordination','scope':'Retains primary published paper, not independent new scientific evidence or a detector execution'}
with (HERE/'fenestration-pdf-provenance.json').open('x') as stream:
    json.dump(record,stream,indent=2)
    stream.write('\n')
print(json.dumps(record,indent=2))
