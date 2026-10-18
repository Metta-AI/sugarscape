# Conditional stable evolutionary reconstruction

All 100 seeds complete 500 action cycles: 50,000 native cycles with resource and population accounting throughout.
The audit validates 3,194,850 birth events against recorded parental traits, joint trait totals against native populations, and charged reproduction costs.
Two 1,000-cycle homogeneous one-agent controls match the original fixed simulator byte-for-byte in both aggregate and individual observations.
The generated source and exact patch against the pinned fixed model are retained.

## Declared assumptions

The Figure 4 count constraints set the initial population to 830, with zero wealth.
Distinct cells are sampled uniformly by rejection sampling; initial ages are zero.
Infertility is independently uniform over 10,20,...,100 and birth cost over 0,10,...,90.
Both traits pass unchanged from parent to child; no mutation or trait reassignment occurs.
The fixed simulator's activation, movement, reproduction equality, newborn delay, and regrowth conventions remain unchanged.
One plotted generation is provisionally treated as one action cycle.
These are explicit reconstruction choices, not verified historical implementation details.

## Results and limits

Every surviving agent has infertility 10 and birth cost zero by cycle 499 in all 100 runs.
This agrees qualitatively with the original figure's selection of those traits.
The retained comparison uses 1,988 exported vertices from the four explicitly labelled population-trait, wealth, and Gini curves.
Gray alternative traits are not assigned invented labels.

| Metric | Reconstruction mean at cycle 499 | Paper Table 1 evolved-stable value |
| --- | ---: | ---: |
| Population | 856.38 | 859 |
| Mean age | 12.7652 | 12.7 |
| Wealth | 492.55 | 504 |
| Gini | 0.693396 | 0.688 |

The rows use different or unknown sampling protocols. Proximity is not a steady-state replication verdict.
The author's percentage uncertainties remain uninterpreted; no acceptance threshold is inferred from these outcomes.
Pointwise ensemble percentiles are descriptive ranges, not simultaneous confidence intervals.
The chaotic evolutionary scenario, intrinsic growth rates, long-horizon statistics, and missing author conventions remain outstanding.

## Replay

Use a fresh directory. `build_evolution.py OUTPUT/model` pins the fixed source and generates the inherited-trait extension.
Compile its `simulate_evolution.cpp` with `clang++ -std=c++17 -O2 -Wall -Wextra -Werror` into `OUTPUT/model/evolution`.
Run `gtimeout --signal=TERM --kill-after=30 900 python3 run_evolution.py OUTPUT`.
The launcher writes the frozen protocol before qualification and native execution, uses two workers, and bounds each native run to 60 seconds.
Analyze with `analyze_evolution.py OUTPUT ORIGINAL_FIGURE_EXTRACTION NEW_ANALYSIS` in the pinned NumPy environment.
The raw archive includes every trajectory, observation, inheritance ledger, native exit, command, source, executable, and manifest; each archived member passes hash readback.
