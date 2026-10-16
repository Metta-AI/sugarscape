# Stevenson (2021): Dynamics of Wealth Inequality in Simple Artificial Societies

Source: [arXiv:2108.11892v2](https://arxiv.org/abs/2108.11892v2), October 14, 2021.
Status: two complete specification-based fixed-parameter ensembles; unresolved discrepancies. **Not a completed replication.**
No verified author implementation has been located in the searches performed so far.

## Model and explicit assumptions

`simulate.cpp` implements the fixed-parameter societies in Appendix A: a 50×50 torus, uniform capacity four, growth one, metabolism three, vision six, puberty one, and one initial agent.
Agents act in a shuffled order, select the nearest richest unoccupied visible cell (including their own), harvest, metabolize, and attempt asexual reproduction.
Newborns have zero wealth and wait until the next cycle. Resource regrowth follows all agent actions.
Death occurs when harvested wealth cannot pay metabolism; zero remaining wealth survives, consistent with the negative-surplus condition in Appendix A's equation 4.

The following operational choices require comparison against author code or sensitivity analysis:

- Increment age before action; a newborn first acts at age one.
- A parent can reproduce with wealth equal to the birth cost.
- Evaluate the fertility draw before searching for an empty adjacent cell.
- Select among empty birth locations uniformly; initial location is uniform.
- Use `std::mt19937_64` and the standard-library shuffle/distributions. Replay identity is limited to the recorded compiler/library environment.

No mutation, evolving inheritance, age-based mortality, or maximum lifespan is added.
The evolving societies in the paper remain unimplemented and are required before completing this study.

## Pilot protocol

Before inspecting its outcomes, the initial pilot uses seed zero and 40,000 cycles for each fixed scenario.
The horizon exceeds the paper's discussion of relaxation beyond 35,000 cycles; it does not establish equilibrium.
The low-fertility scenario uses infertility 85 and birth cost zero; the birth-cost scenario uses infertility 10 and cost 40.
Record statistics every 100 cycles, plus the first and terminal cycles. Preserve early extinction.
No numerical agreement criterion is inferred from these pilot outcomes.

The simulator checks resource conservation and population accounting at **every cycle**, including unrecorded cycles.
Its balance includes resource growth, metabolism paid by surviving agents, remaining resources consumed on starvation, and reproduction costs.
These are model-execution invariants, not evidence that all behavioral choices match the paper.

```sh
clang++ -std=c++17 -O2 -Wall -Wextra -Werror \
  replications/stevenson_2021/simulate.cpp -o /absolute/tools/stevenson-simulate
/absolute/tools/stevenson-simulate 0 85 0 40000 > /new/low-fertility.csv
/absolute/tools/stevenson-simulate 0 10 40 40000 > /new/birth-cost.csv
```

Arguments are seed, infertility denominator, birth cost, and maximum cycles.
Use fresh output files; shell redirection overwrites existing files.

## Required study targets

Table 1 reports 100 independent seeds for each of four scenarios, including evolving stable and chaotic societies.
Targets include population, mean age, wealth, Gini inequality, and fitted intrinsic growth rates.
Figures 1–4 and Appendix B additionally cover relaxation, wealth/age distributions, growth-regime comparisons, and evolution.
The steady-state sampling window, meaning of percentage uncertainties, evolutionary inheritance details, and original seeds require further source investigation.
The two fixed-parameter pilots do not substitute for those targets.

## Pilot evidence

[Raw trajectories and manifest](results/pilot-2026-10-15) retain both 40,000-cycle runs and a byte-identical independent-process repeat of low fertility.
Final populations are 834 and 823; all cycle-level resource and population checks pass.
All 401 recorded observations per run have finite metrics and valid Gini values.
The birth-cost pilot has final mean age 1,347.74; equilibrium and agreement with the published mean age remain unestablished.

## Birth-cost ensemble

The declared 100-seed, 100,000-cycle ensemble completed with no extinctions.
[All trajectories and analysis](results/birth-cost-ensemble-2026-10-15) are retained; gzip decompression preserves each original CSV exactly.
Validation checked 100,100 observations, all completion hashes, both declared windows, and recorded conservation checks.
The later-window mean age is 1,418.80 (95% interval 1,415.50–1,422.09), compared with the published 2,264.
Population is 821.457 versus 824, wealth 15,902.67 versus 16,254, and Gini 0.336714 versus 0.33.
These are unresolved discrepancies requiring implementation and measurement investigation, not negative-replication verdicts.
Paired changes between the two windows have intervals containing zero; this does not prove equilibrium.
No interpretation of the paper's percentage uncertainties or acceptance margin is inferred from these results.

## Low-fertility ensemble

The [low-fertility ensemble](results/low-fertility-ensemble-2026-10-15) also completed all 100 seeds and 100,000 cycles without extinction.
All 100,100 recorded observations, trajectory hashes, and declared windows passed validation.
Later-window means are population 836.485 versus published 837, wealth 4,543.39 versus 4,767,
mean age 438.06 versus 473, and Gini 0.530577 versus 0.53.
The Gini value matches printed precision; that alone does not establish agreement for this scenario or paper.
As with birth cost, paired-window intervals contain zero but do not prove stationarity.
The [birth-threshold diagnostic](BIRTH_THRESHOLD_DIAGNOSTIC.md) investigates one explicit implementation ambiguity using new seeds.
Its results will not silently replace either ensemble or establish the author's unknown rule.
