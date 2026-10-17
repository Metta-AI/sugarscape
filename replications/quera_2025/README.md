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
