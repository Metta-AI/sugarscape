# Quera-Bofarull et al. (2025): Automatic Differentiation of Agent-Based Models

**Status: incomplete.** Three native forward simulations pass the recorded state audit. The paper’s gradient and calibration results remain unreplicated.

Paper: https://arxiv.org/html/2509.03303v2
Author implementation: https://github.com/arnauqb/DiffABM.jl/tree/9178eccd56dd352e3515e276239654239f8d3b41

## Native execution and evidence

We use the author’s `jmlr_submission` revision and its unchanged 348-package manifest with Julia 1.11.3. No model correction is applied. The Sugarscape implementation matches the prepublication revision inspected in the program source audit.

The calibration configuration uses 100 agents, a 25×25 landscape, vision 1/6 with probabilities 0.2/0.8, metabolic parameters 2/5, wealth parameters 5/2, and regeneration 1. Calling the author’s `abm_run` with 50 stored states executes 49 transitions. Seeds are 0, 1, and 2. Gaussian smoothing is 1; the gradient horizon is 10,000. These forward runs do not exercise differentiation.

The retained pilot contains 150 states, 15,000 agent observations, and 93,750 cell observations. The independent Python audit verifies hashes, shapes, ordering, finite values, initial ranges, resource bounds, and survival transitions. It does not independently replay movement.

| Seed | Final population | Initial duplicate positions | Nonpositive post-metabolism wealth while alive | Positive wealth after harvest but died |
|---|---:|---:|---:|---:|
| 0 | 75 | 6 | 25 | 1 |
| 1 | 78 | 11 | 22 | 0 |
| 2 | 75 | 8 | 27 | 1 |

All 14,700 survival transitions match prior-step wealth, as the source implements. This explains the 74 nonpositive-wealth survival observations. Initial positions are sampled with replacement. Occupancy-count discrepancies are recorded separately; they are not automatically interpreted as movement violations. These findings concern source behavior, not a validated negative replication of the paper.

`results/native-pilot-2026-10-17` contains the original runner, command receipt, exit receipt, output hashes, full compressed trajectories, and audit. The top-level runner only replaces the original absolute project/output paths with command arguments. Its scientific configuration is unchanged.

## Reproduce

Obtain the pinned DiffABM checkout above and Julia 1.11.3. Use an isolated Julia depot. Instantiate the checked-in Project/Manifest without updating dependencies:

```sh
julia --startup-file=no --project=/path/to/DiffABM -e 'using Pkg; Pkg.instantiate(;allow_autoprecomp=false); using DiffABM'
julia --startup-file=no --project=/path/to/DiffABM replications/quera_2025/run.jl /path/to/DiffABM /new/output/path
python3 replications/quera_2025/audit.py /new/output/path /new/audit/path
```

To inspect retained evidence, extract `trajectories.tar.gz` into a new directory, copy the retained `run.jl`, `configuration.txt`, and `sha256.txt` there, then run `audit.py`. The archive hash is in `archive.json`. The audit requires a new output directory.

## Remaining paper targets

- Figure 11: automatic-differentiation and finite-difference gradients for six parameters, 100 agents, a 50×50 landscape, and vision 1/3. Recover or explicitly reconstruct the finite-difference step sizes, replicate counts, normalization, seeds, and historical source revision.
- Figures 17, 19b, and 20b: calibration predictive behavior, loss, and posterior. Recover the exact prior and training protocol; reproduce the stated five Monte Carlo samples, 5,000 epochs, validation selection, and flow architecture.
- Independently replay movement and resource/occupancy changes before interpreting discrepancies as model failures.

Program source audits retain the original paper source, digitized vector-figure curves, historical dependency lockfile, and deleted author scripts. The recovered scripts use older configurations and do not establish the paper’s exact experiment protocol. In particular, gradient-figure metadata predates the change from initial wealth `10*sample` to `6+19*sample`; metadata alone does not identify the revision used.

Completion requires quantitative comparisons against these targets and investigation of implementation/configuration errors. This pilot contributes zero completed papers.

## Reconstructed gradient pilot

`results/gradient-pilot-2026-10-17` records full native 25-state trajectories for seeds 0–2, with six-parameter ForwardDiff derivatives and central finite differences at steps 0.001 and 0.01. Each plus/minus pair resets the same seed. The observable is total recorded wealth divided by the initial 100 agents, with no additional time normalization. The model uses the paper’s gradient geometry (50×50, vision 1/3), calibration parameter defaults, and the unchanged submission source.

The independent `audit_gradients.py RUN NEW_OUTPUT` validates all 900 records and recomputes finite differences. Initial wealth derivatives agree within 7.67e-8 at step 0.001. Initial vision/metabolism derivatives are exactly zero. Later estimates differ: the largest per-seed vision difference is 11.55 at step 0.01. These are paired trajectory diagnostics, not converged expectation estimates or a Figure 11 replication.

The first runner attempt failed because separate anonymous functions supplied incompatible ForwardDiff tags. Its source and failure receipt are retained. Using the same function object corrected the runner without changing the simulation or analysis protocol.

The separately declared 256-seed ensemble (seeds 3–258) completed all three steps (0.001, 0.01, 0.05). Its 115,200 records pass the independent audit. Exact published normalization, seed counts, step sizes, and historical source remain unresolved.

## Expectation-gradient diagnostic ensemble

`results/gradient-ensemble-2026-10-17` preserves all 256 per-seed aggregate trajectories, source, protocol, hashes, exit receipt, independent audit, pointwise intervals, and plot. Execution took 125.2 seconds on one local Julia thread. `analyze_gradients.py RUN AUDIT_JSON NEW_OUTPUT` computes paired differences across seeds, Student-t 95% intervals, and separate means for each 128-seed half. These intervals are pointwise and do not establish simultaneous coverage or a whole-paper verdict.

At transition 24, step 0.01 gives:

| Parameter | Mean AD | Mean FD | Paired AD−FD 95% interval |
|---|---:|---:|---|
| p1 | -1.09945 | -8.66722 | [6.12128, 9.01426] |
| p3 | 0.27486 | 2.32484 | [-2.73826, -1.36170] |
| m_alpha | -6.99431 | -7.03762 | [-0.03640, 0.12302] |
| m_beta | 1.35341 | 1.36251 | [-0.05021, 0.03200] |
| w_alpha | 0.64803 | 0.68633 | [-0.08695, 0.01034] |
| w_beta | -0.97236 | -1.00543 | [-0.01652, 0.08265] |

Vision discrepancies persist at step 0.05. The p1 FD means in the two halves are -9.29055 and -9.11920 at that step, versus -6.51086 and -9.84205 at step 0.001. The smallest step has greater uncertainty. Continuous-parameter differences are smaller; several pointwise intervals exclude zero at step 0.05, so this is not evidence of exact equality or unbiased AD.

![All reconstructed gradient estimates and pointwise intervals](results/gradient-ensemble-2026-10-17/gradients.png)

This broadly agrees with the paper’s qualitative distinction between continuous and categorical gradient quality. It does not quantitatively reproduce Figure 11: historical wealth scaling, observable normalization, and exact experiment settings remain unresolved. No new completed-paper credit is assigned.

To reproduce the retained analysis, verify `sha256.json`, extract `trajectories.tar.gz` into a new directory, and copy `protocol.json` and `exit.json` there. Run `audit_gradients.py`, then `analyze_gradients.py` with that audit. Plot using `plot_gradients.py COMPARISON_JSON OUTPUT_PNG`. Analysis uses SciPy; plotting uses Matplotlib.

## Ordinary-versus-differentiated trajectory control

A strict equality check on aggregate mean wealth failed by at most 2.14e-14 across three seeds. The failure and original runner are retained. A full-state follow-up found **405,000 exactly identical values** across all six histories: resources, x/y positions, individual wealth, survival, and occupancy. Thus the observed aggregate discrepancy arises during reduction, not from changed state trajectories in these three seeds. All 450 derivatives also match the earlier pilot exactly.

`results/gradient-primal-control-2026-10-17` contains both complete histories and receipts. Extract `full-states.tar.gz` and run `julia --startup-file=no replications/quera_2025/verify_primal_states.jl EXTRACTED_DIRECTORY`. This verifier uses only Julia’s Serialization standard library, independently reloads both histories, and requires exact equality. It does not infer state equality for the separate 256-seed ensemble.
