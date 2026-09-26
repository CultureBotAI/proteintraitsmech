# Retained disorder predictions

This run fills B22 for all 256 selected proteins using **metapredict 3.0.2, V3**
on CPU with `normalized=True`, `round_values=True`, one complete reference
sequence per call, one PyTorch thread and deterministic algorithms enabled.
Upstream normalization clips to [0,1] and rounds scores to four decimal places.
PTM applies the existing strict **score > 0.5** contract. It does not apply
metapredict's disorder-domain gap-closing or minimum-length heuristics.

The model predicts disorder from sequence. V3 uses hybrid disorder/pLDDT training
targets, so these results are not experimental disorder or independent validation
of an ESM embedding. Only uppercase standard amino acids are accepted here.
Unsupported sequences remain unavailable; they are never masked or shortened.
The current bounded cohort contains no unsupported input and no missing scores.

## Artifacts and provenance

- `predictions.raw.jsonl`: exact full input sequences and local per-residue outputs.
- `predictions.jsonl`: the normalized PTM adapter representation with full-sequence hashes.
- `run.json`: input/output hashes, selected IDs, predictor version/mode, checkpoint
  hash, runner hash, platform, Python version and explicit limitations.
- `requirements.txt`: all installed package versions from the inference environment.
- `upstream/model.pt`: the 23,626-byte V3 checkpoint, SHA-256
  `32de116ad8e2edefc3abf96ea3495e90527323c6108db91dd7866391b77341bd`.
- `upstream/local_data.py` and `test_metapredict.py.txt`: upstream numerical
  regression fixtures, parsed as literals rather than executed.
- `reference-result.json`: the documented full-sequence example and observed
  output. Maximum absolute error against the upstream S2 fixture was **0**;
  the check allows 0.001, matching the upstream tolerance.
- `.fetch.json` receipts: acquisition URLs, timestamps and hashes.

Code, checkpoint and fixtures come from the
[upstream 3.0.2 source](https://github.com/idptools/metapredict/tree/34ddeefba8285c57fb5307792ce5f6789f860bef),
distributed under the retained [MIT license](upstream/LICENSE). The license
permits reuse and redistribution with its notice. These scores were computed
locally, with no prediction-service restrictions. Full protein sequences retain
UniProt Consortium attribution under CC BY 4.0. Method reference:
[Emenecker, Griffith and Holehouse (2021)](https://doi.org/10.1016/j.bpj.2021.08.039).

## Reproduce inference

Inference is optional; normal checks and bundle refresh use the retained scores.
From the repository root, create an isolated Python 3.13 environment. The frozen
environment records this run's macOS ARM package versions; other platforms may
need the corresponding CPU PyTorch distribution.

```bash
uv venv --python 3.13 /tmp/ptm-disorder-env
uv pip install --python /tmp/ptm-disorder-env/bin/python \
  -r data/biophysical/disorder/requirements.txt
just select-biophysical-cohort --apply
/tmp/ptm-disorder-env/bin/python scripts/predict_biophysical_disorder.py --apply
just refresh-biophysical --apply
just check-biophysical-pilot
```

The runner verifies the installed version and checkpoint hash before inference,
then verifies the upstream example before publishing any scores. Numerical output
may vary slightly across platforms; retained prediction scores are exact inputs
to downstream replay, while the upstream reference uses the explicit tolerance.
Changing the selection, runner or package requires a new recorded run.

CI checks every raw/normalized score, input sequence, dependency-file hash,
checkpoint/fixture hash and run manifest, then numerically replays B22 fractions
and segments. CI does not rerun the neural network. Retained output provenance
and independent model execution are distinct checks.
