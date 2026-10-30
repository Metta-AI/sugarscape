# Thaler and Siebers (2019): lock-free agents

Completed qualified author-code method study. All 51 timing cells were audited. Figure 5a matches time 83 rather than caption time 50; retry and historical performance discrepancies remain unresolved.

Sources: [publication 1](https://doi.org/10.1186/s40294-019-0067-9).

## Retained workflow

Retains original benchmark-report analysis, its report hashes, and the bounded native runner. Timing/retry campaign machinery, host-recovery files, and population-control investigations are archived.

The original Haskell projects retain BSD3 licensing; the paper is CC BY 4.0. Use the exact source/report revisions required by the runner and report manifest.

Use the pinned prerequisites from the archived study. Uppercase arguments denote supplied paths or identifiers; output paths must be new.

```sh
python replications/thaler_2019/audit_archive.py AUTHOR_ENGINE PAPER_PDF NEW_ANALYSIS
python replications/thaler_2019/run_native.py AUTHOR_ENGINE REVISION_FIDELITY_JSON NEW_RUN
```

## Historical study and evidence

The [pinned study record](https://github.com/Metta-AI/sugarscape/tree/b78c2d5158d9c0d606f25527c9955ec54cb745f6/replications/thaler_2019) retains full campaigns, removed scripts, reference outputs, source revisions, and dependency environments. It also links earlier raw-data archives.

Findings above describe that recorded study. The retained workflow covers the entrypoints listed here. Export historical files outside this checkout; generated diagnostics belong in temporary or explicitly chosen output directories.
