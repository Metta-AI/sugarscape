# Full-size convergence reconstruction

Twenty thousand native runs completed in 222.79 seconds with four bounded workers.
The 100 generated policies each use 100 seeds under both tax-clock phases.
All 40,000 request/result lines pass coverage, identity, policy, terminal-status, and provenance checks.
The evaluator, model, and runtime hashes match the previously qualified batch workflow.

| First tax after move | Maximum absolute mean-death change, 50 to 100 seeds | Maximum absolute literal-revenue mean change | Maximum death sample-SD change / 100-seed SD |
| --- | ---: | ---: | ---: |
| 1 | 0.74 agents | 32.63 sugar | 22.91% |
| 5 | 0.91 agents | 57.85 sugar | 24.00% |

Means and standard deviations need separate interpretation. Small mean changes do not establish stable variance estimates.
The largest SD percentages use the 100-seed estimate as denominator; they are descriptive, not a declared paper-failure threshold.
Each policy's signed changes and first-half/second-half mean differences with standard errors are in `policy-summaries.csv`.
All 59,400 prefix summaries are in `prefix-curves.csv.gz`; both population and sample SD conventions are included.
Both figures show every policy, with colors identifying its prescribed mean tax rate.
Common seeds couple the policies: the 100 similarly shaped curves are not 100 independent confirmations of a pattern.

The original vectors, generating distribution, and group allocation are unavailable.
The frozen protocol declares the conditional-uniform sampler, 34/33/33 allocation, seeds, clock treatments, and analysis before execution.
These findings are conditional on that reconstruction. They do not establish exact Figure 9 reproduction or a validated negative replication.
Reduced-model rankings, optimization, transfer, and historical timing remain incomplete. No paper-completion credit is assigned.

## Evidence and verification

`native-evidence.tar.gz` contains all inputs, native outputs, source snapshots, frozen model and landscape, runtime hashes, commands, and per-worker terminal status.
The independent readback compares 2,400 means and sample standard deviations against Python's `statistics` implementation, with absolute tolerance 1e-10.
It also checks the prefix-row count and uniqueness and verifies every archived file byte-for-byte; see `readback.json`.
The native archive includes `package_and_verify.py`, the executed readback procedure with its original evidence paths.

To reanalyze, extract the archive into a fresh directory and run the repository's `analyze_convergence.py` against it, with another fresh output directory.
To rerun the simulations, use `prepare_convergence.py` and `run_convergence.py` as documented in the study README.

`failed-launch-evidence.tar.gz` preserves the initial launch's four exit-code-1 failures, logs, and frozen protocol.
That launcher copied the model without its required landscape; all four workers failed before producing a result.
The corrected launcher freezes and verifies both files. The replacement protocol is byte-identical; no policies or seeds changed.
