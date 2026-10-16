# Dogan (2026): Policy Robustness Under Accelerating Automation

Source: [author repository and working paper](https://github.com/dgnerg867-ux/sugarscape), pinned to `0b6a3df470388f60535d8ffb67c34a7f9fa0059a`.
The author's citation identifies this as an unpublished 2026 working paper, not a peer-reviewed publication.
This study supplements the existing replication program; it does not replace unfinished studies.

The repository contains the manuscript, original model, canonical result tables, and experiment scripts.
Author contributions use MIT licensing; Mesa-derived files retain Apache-2.0 licensing and attribution.
The reference checkout remains separate and unmodified.

## Declared execution protocol

Use the author's Python 3.12.4 and exact four dependency versions from `requirements.txt` on macOS arm64.
Run `python replications/dogan_2026/run.py REFERENCE NEW_OUTPUT` using that environment.
The runner validates the source revision, clean tracked files, and installed versions before execution.
It launches the original script in a fresh output directory, preserving published CSVs and recording source/reference hashes.
`PYTHONHASHSEED=0` is an explicit reproducibility setting; the model's original seeds and all experimental settings remain unchanged.

The canonical sweep includes 25 static-policy runs, 105 transition runs, 75 welfare-sensitivity runs, and two threshold-calibration runs.
All policy experiments retain the original five seeds and 300-step horizons.
Compare every output row and column with the author's corresponding CSV before interpreting the paper's claims.
Undefined statistics must retain matching missingness rather than being silently replaced or excluded.
Validate the reported tables and policy rankings independently of the author's analysis.

## Remaining scope

Canonical execution alone does not complete this paper.
The manuscript also includes composition, per-seed threshold, displacement-levy, horizon, starvation, and transfer-rate robustness analyses.
Their exact reported targets and scripts require auditing, followed by complete executions and independent comparisons.
An equivalent integration in the Metta-AI fork and paper-level conclusions remain unfinished.

## Environment recovery

The exact four-package installation fails before simulation: Mesa imports `networkx`, which the author's requirements omit and Mesa declares as an extra.
The failed run's manifest, traceback, and exit status are retained.
A separate retry adds NetworkX 3.7; this version is our recovery choice, not a verified author version.
`environment.txt` records every installed distribution so transitive dependencies are explicit.
The original Python version and four author-pinned versions remain unchanged.
The snapshot reference has 24,675 rows; no constant-population assumption is imposed on the transition model.
