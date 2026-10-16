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
/absolute/tools/stevenson-simulate 0 85 0 40000 100 /new/low-observations.csv > /new/low-fertility.csv
/absolute/tools/stevenson-simulate 0 10 40 40000 100 /new/birth-observations.csv > /new/birth-cost.csv
```

Arguments are seed, infertility denominator, birth cost, maximum cycles, recording interval, and a new observation CSV path.
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

## Birth-threshold sensitivity result

The [predeclared diagnostic](results/birth-threshold-diagnostic-2026-10-15) completed all twenty runs,
ten new seeds per variant, with 20,020 validated observations and no extinctions.
Changing only `wealth >= birth_cost` to `wealth > birth_cost` substantially changes the outcome:

| Later-window metric | Baseline | Strict threshold | Published Table 1 |
| --- | ---: | ---: | ---: |
| Population | 821.418 | 824.216 | 824 |
| Wealth | 15,908.38 | 16,237.67 | 16,254 |
| Mean age | 1,415.86 | 2,381.55 | 2,264 |
| Gini | 0.336643 | 0.332668 | 0.33 |

The paired mean-age change is +965.70 cycles (95% Student-t interval +937.02 to +994.37 across ten seeds).
The strict variant's age interval is 2,349.81–2,413.30, still above the published mean.
This identifies sensitivity to one unresolved rule; it does not identify the author's implementation or establish replication.
Both windows, all seed-level estimates, source patches, runtime hashes, and lossless trajectories are retained.
The original simulator and its two 100-seed ensembles remain unchanged pending stronger source evidence.

### Related author specification

Stevenson's [2023 paper, version 2](https://arxiv.org/pdf/2302.03096v2), Algorithm 1, line 19,
explicitly permits reproduction when surplus equals birth cost and age equals puberty.
That supports the baseline inequality as an author-used convention, despite the strict variant's closer population result.
However, the algorithm describes a later genetically programmed model, not the 2021 implementation.
It cannot establish historical equivalence or resolve the remaining age discrepancy.
The downloaded PDF has SHA-256 `0a3942d14aa51f0fcd3565fdc17e90b03d91f8268ec87cb14bade20ab097348e`.
GitHub repository search for the author's name and code search for the paper's author email returned no matches.
Those searches do not establish that author code is unavailable.

## Recording-frequency verification

The simulator now requires an explicit recording interval; existing ensemble calls retain 100-cycle output.
[System-level verification](results/recording-proof-2026-10-15/proof.json) runs both fixed scenarios for 3,000 cycles with the original binary, updated sparse output, and updated per-cycle output.
Original and updated sparse CSVs are byte-identical; all 6,000 dense observations contain exactly the same sparse samples.
Recording frequency does not change random draws or simulation rules.
Historical retained commands target their original binary and remain unchanged as evidence.
After storage recovered, both 100-seed per-cycle growth ensembles launched under the [declared growth protocol](GROWTH_PROTOCOL.md).
The analysis requires exact agreement with earlier same-seed trajectories before fitting continuous logistic growth.
The completed growth diagnostic is reported below; the study remains incomplete.
Renewed author/title/GitHub searches did not identify a verified implementation; that does not establish its absence.

## Growth-rate diagnostic completed

[All 200 dense trajectories, fit attempts, and residual plots](results/growth-2026-10-15) are retained.
All 600,000 observations pass finite-value, timestamp, population-accounting, and conservation checks.
All 6,200 observations shared with earlier same-seed ensembles match exactly.
The full-ensemble analyzer first rejected the incomplete run, then passed after completion.
All 600 optimization attempts converged, with within-seed growth-rate differences below 0.000001 across starting values.

| Scenario | Mean fitted growth rate | 95% interval across seeds | Published | Relative difference |
| --- | ---: | ---: | ---: | ---: |
| Low fertility | 0.0257210 | 0.0255210–0.0259210 | 0.018 | +42.89% |
| Birth cost | 0.0330662 | 0.0330241–0.0331082 | 0.032 | +3.33% |

Residuals show systematic structure around the growth transition.
The largest absolute mean residual is 32.96 agents for low fertility and 80.34 for birth cost.
Per-seed root mean squared residuals range from 17.85–22.15 and 13.38–14.93 agents, respectively.
These fits approximate the trajectories; optimization convergence does not establish the logistic model's adequacy.
The author fitting window and procedure remain unknown, and behavioral assumptions remain unresolved.
These differences therefore do not establish a negative replication.

Reproduce the declared analysis on a completed external run:

```sh
python replications/stevenson_2021/analyze_growth.py /complete/growth-run /new/analysis
```

## Original arXiv source recovered

The [version-two source bundle](https://arxiv.org/src/2108.11892v2) contains the LaTeX manuscript, five EPS figures, and their five converted PDFs.
[The retained inventory](results/author-source-2026-10-16/inventory.json) records the archive and every file hash.
The bundle contains neither simulator source nor plotting/fitting scripts. EPS headers identify R graphics output.
The TeX source does not resolve the fitting window, optimizer, weighting, or evolutionary inheritance ambiguity.
It confirms the initial single agent and 100-seed scenario protocol.
The original vector figures are now available for quantitative target extraction; no new agreement is claimed from their recovery alone.
Renewed title, identifier, and author searches did not identify a verified GitHub implementation.

## Original Figure 1 curves recovered

`extract_figure1.py ORIGINAL_FIGURE_PDF NEW_OUTPUT` pins the recovered PDF and checks its labeled-axis vector anchors.
[Eight extracted curves and a visual reconstruction](results/figure1-vector-2026-10-16) preserve exported vertices in lossless CSVs.
The reconstructed shapes match visual inspection of the source figure.
The export drops collinear vertices and rounds coordinates, so these are approximate curves, not recovered raw per-cycle data.
The plotted seed and aggregation remain unknown.

Late-window summaries integrate line segments over cycles 35,000–50,000, stopping at the last available vertex.
They do not average irregularly spaced vertices or impose exact agreement on independent-seed runs.

| Extracted series | Approximate late-window mean |
| --- | ---: |
| Low-fertility mean age | 439.84 |
| Birth-cost mean age | 2,245.98 |
| Low-fertility population | 836.514 |
| Birth-cost population | 823.906 |
| Low-fertility Gini | 0.52398 |
| Birth-cost Gini | 0.33200 |

The plotted low-fertility mean age is closer to our ensemble's 438.06 than to Table 1's 473.
Different unknown seeds and sampling windows prevent a definitive consistency judgment.
The birth-cost curve remains far above our 1,418.80 ensemble mean, so vector recovery does not resolve that behavioral discrepancy.
Elite-age curves are retained as additional targets; the current simulator does not yet record the corresponding elite statistic.
No new paper completion or negative verdict follows from this figure extraction.

## Elite and founder observation coverage

The simulator now emits a separate observation CSV containing elite summaries and the living members of the first thirty births.
Elite membership uses the wealthiest ceil(population/10), with equal wealth ordered by birth identifier; this unresolved author convention is explicit.
No observation sorts live agents, consumes random numbers, or changes movement, reproduction, death, or regrowth.
The aggregate CSV format remains unchanged. Both ensemble runners pass the required new output path.

[Complete-system verification](results/observation-proof-2026-10-16/proof.json) checks both scenarios for 3,000 cycles at per-cycle resolution.
All 6,000 aggregate observations are byte-identical to the original binary.
Elite counts, wealth, and age also match independent reconstruction for 598 early complete-population observations.
Later elite results have no independent full-population oracle in this proof; that limitation is retained.

The [declared observation ensemble](OBSERVATION_PROTOCOL.md) runs all 100 original seeds per scenario through 50,000 cycles.
Each run must match its already completed same-seed aggregate prefix byte-for-byte before entering the completion ledger.
Raw and losslessly compressed output, native exit status, and content hashes are preserved.
The first two low-fertility runs pass this full-prefix check; the overall observation ensemble is still running.
These measurements expand required figure coverage without resolving the model's remaining historical ambiguities.

## Independent observation audit

`analyze_observations.py RUN prefix|complete NEW_OUTPUT` independently validates compressed and raw hashes, exit records, and the complete ordered seed ledger.
It compares each aggregate trajectory directly with the retained original 100,000-cycle same-seed result.
Checks cover elite counts and resource bounds, founder identifier uniqueness, continuous observation intervals, and constant inferred birth cycles.
When the first thirty births still comprise the whole population, independent ranking reconstructs elite summaries.

[The first prefix audit](results/observation-audit-2026-10-16/audit.json) passes all 24 completed runs and explicitly marks the ensemble incomplete.
Complete mode rejects this unfinished ensemble and creates no completion report.
The aggregate analyzer also rechecks all 100 archived low-fertility runs after its command reader update; its entire analysis remains unchanged.
Historical stored command formats remain readable alongside the current mandatory observation-output argument.

## Founder-history vector targets

`extract_figure2.py ORIGINAL_FIGURE_PDF NEW_OUTPUT` recovers the original founder curves using inspected axis anchors.
[The retained extraction](results/figure2-vector-2026-10-16/extraction.json) contains 202,347 vertices across 44 traces, plus a visually checked reconstruction.
Only the black curves explicitly identify founder zero. Grey path ordinals are not asserted to be agent identifiers.
There are 31 low-fertility and 13 birth-cost paths, versus caption counts of 30 and 12; that source ambiguity is preserved.

The first founder's birth-cost wealth falls from approximately 40 to 1 between cycles 40.07 and 40.87.
Integer rounding locates the event at cycle 41, but this does not select the strict reproduction threshold.
A failed fertility draw at cycle 40 followed by success at 41 also produces it under the baseline rule.
All thirteen large wealth drops are retained, without selecting only events favorable to either interpretation.
The unknown author seed and coordinate rounding still prevent treating these curves as exact native trajectories.
