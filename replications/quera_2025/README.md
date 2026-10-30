# Quera-Bofarull et al. (2025)

Completed qualified method study with mixed results. Native forward, gradient, calibration, and predictive workflows were audited. VarGrad mismatch, partial parameter recovery, and reconstruction choices remain explicit.

Sources: [publication 1](https://arxiv.org/html/2509.03303v2), [publication 2](https://arxiv.org/src/2509.03303v2).

## Retained workflow

Retains the original-code forward runner and exported-state auditor. Gradient replay, calibration extractors, training seals, and secondary diagnostics are archived. The pinned Julia environment remains an external prerequisite.

The runner requires the pinned external DiffABM project, Julia environment, and manifest checksum recorded in its source. A current replacement environment is not equivalent evidence.

Use the pinned prerequisites from the archived study. Uppercase arguments denote supplied paths or identifiers; output paths must be new.

```sh
julia --project=AUTHOR_PROJECT replications/quera_2025/run.jl AUTHOR_PROJECT NEW_RUN
python replications/quera_2025/audit.py NEW_RUN NEW_AUDIT
```

## Historical study and evidence

The [pinned study record](https://github.com/Metta-AI/sugarscape/tree/61d713c05e1a23d417bcb7ed6f18fc9fca969006/replications/quera_2025) retains full campaigns, removed scripts, reference outputs, source revisions, and dependency environments. It also links earlier raw-data archives.

Findings above describe that recorded study. The retained workflow covers the entrypoints listed here. Export historical files outside this checkout; generated diagnostics belong in temporary or explicitly chosen output directories.
