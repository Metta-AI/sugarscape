# Stevenson (2021): Dynamics of Wealth Inequality in Simple Artificial Societies

Source: [arXiv:2108.11892v2](https://arxiv.org/abs/2108.11892v2), October 14, 2021.
Status: complete fixed-parameter and conditional evolutionary ensembles; unresolved discrepancies. **Not a completed replication.**
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

The fixed-parameter simulator adds no mutation, inheritance changes, age-based mortality, or maximum lifespan.
A separate conditional inherited-trait extension now implements both evolutionary parameter cases; historical rules, growth-rate and steady-state targets remain unresolved.

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

## Figure 1 low-fertility ensemble comparison

[Descriptive comparison](results/figure1-low-comparison-2026-10-16/comparison.json) uses all 100 declared low-fertility seeds and 499 shared times, cycles 100–49,900.
The independent observation audit validates 153 completed runs at its snapshot; the complete 200-run ensemble is still pending.
All low-fertility aggregate trajectories match their earlier ensemble prefixes byte-for-byte.
Observation files, audit snapshot, comparison table, and inspected plot are retained.

Published population, mean-age, Gini, and elite-age samples lie inside pointwise central 95% seed intervals at 96.6%, 97.0%, 94.0%, and 92.0% of shared times.
These percentages are descriptive, not acceptance tests; the seed intervals are neither confidence intervals nor simultaneous bands.
For cycles 35,100–49,900, published versus ensemble-average population is 837.328 versus 836.440.
Mean age is 439.373 versus 456.128, Gini 0.524280 versus 0.533256, and elite age 1266.190 versus 1534.076.
Published late elite age falls below the ensemble’s 2.5th percentile of seed means (1318.642).
Unknown published seed, aggregation, elite conventions, and approximate vector coordinates prevent a paper-level verdict.
The comparison does not change model parameters or acceptance criteria.

Run `compare_figure1.py RUN AUDIT low-fertility NEW_OUTPUT` after `analyze_observations.py`.
It requires all 100 audited seeds for the selected scenario and rechecks trajectory hashes and published extraction hashes.
The final birth-cost comparison and evolutionary scenarios remain outstanding.

## Complete observation ensemble and birth-cost comparison

All 200 declared observation runs completed and passed the independent audit.
Each aggregate trajectory matches the corresponding original 100,000-cycle ensemble prefix byte-for-byte.
[Complete audit and comparison](results/figure1-birth-comparison-2026-10-16/audit.json) retain all 200 ledger entries and the remaining 100 observation files.
The earlier 153-run snapshot remains historical evidence; it no longer describes current completion.
An independent standard-library calculation also confirms all four previously reported low-fertility late means within 2.3e-13.

Across 499 shared birth-cost samples, the published population, mean-age, Gini, and elite-age curves lie inside pointwise seed intervals at 89.6%, 1.4%, 93.0%, and 7.6% of times.
Late published versus replication averages are population 823.951 versus 821.532, mean age 2245.622 versus 1417.953, Gini 0.332135 versus 0.336815, and elite age 2582.855 versus 1887.566.
The age discrepancy appears in both the figure and Table 1; it is not explained by a table transcription alone.
The tested observer preserves aggregate model behavior, but does not establish author-model equivalence.
Unknown historical semantics still prevent calling these disagreements validated negative replications.
Evolutionary scenarios and additional figure coverage remain required for study completion.

## Figure 2 labelled-founder comparison

[The founder comparison](results/figure2-comparison-2026-10-16/comparison.json) covers all 200 audited observation runs.
It matches only the explicitly labelled founder zero; grey path ordinals remain unidentified.
Published wealth lies inside pointwise central 95% surviving-seed intervals at 340/346 low-fertility times and 20/21 birth-cost times.
These descriptive intervals condition on survival; absent founders are not assigned zero wealth.
At the final shared published samples, 55/100 low-fertility founders survive to cycle 34,600 and 32/100 birth-cost founders survive to cycle 2,100.

Median last-observed-alive cycles are 36,650 and 1,300, respectively.
Eight low-fertility founders remain alive at the 50,000-cycle horizon, so their lifetimes are right-censored.
All other death times lie between the last observation and the next 100-cycle sample.
Published path endpoints near 34,661.5 and 2,137.0 are approximate graphics coordinates, not exact death records.
Unknown published seeds prevent treating these individual trajectories as population estimates.

An independent standard-library calculation verifies every survival count and all 1,101 wealth quantiles across 367 comparison rows.
The comparison rechecks all 200 native observation hashes against the completed audit ledger.
This adds Figure 2 coverage without changing the model or resolving the population-wide age discrepancy.
Evolution, Figure 3 sensitivity, and Appendix B remain outstanding; this study remains incomplete.

```sh
python replications/stevenson_2021/compare_figure2.py /complete/observation-run /complete/observation-audit /new/comparison
```

## Additional author evidence on reproduction boundaries

[Local Sharing (2023), version 1](https://arxiv.org/pdf/2305.17177v1), Algorithm 1 line 17, uses strict age and wealth thresholds.
Visual inspection of page 4 confirms both operators.
This differs from the non-strict comparisons in the previously checked Struggle for Existence algorithm.
These later algorithms describe different models and do not identify the 2021 implementation.
Their disagreement prevents treating either convention as settled historical evidence.
Source URLs, hashes, frozen runner hashes, and launch command are [retained](results/reproduction-boundaries-launch-2026-10-16/launch.json).

The [predeclared reproduction-boundary diagnostic](REPRODUCTION_BOUNDARIES.md) isolates both operators in a two-by-two design across both fixed scenarios.
It runs 80 bounded simulations using ten new seeds and preserves every outcome.
The baseline simulator remains unchanged. No new agreement or study completion is claimed before independent analysis.

```sh
python replications/stevenson_2021/run_boundaries.py /new/boundary-diagnostic
```

### Independent boundary-diagnostic validation

`analyze_boundaries.py RUN prefix|complete NEW_OUTPUT` checks the declared grid and generated source differences against the pinned baseline.
It verifies native binary and trajectory hashes, successful exits, finite metrics, timestamps, resource bounds, and sampled metabolism and birth costs.
The native simulator enforces resource and population balance every cycle; sparse output cannot independently reconstruct every transition.
Birth-cost age-only comparisons require both aggregate and observation files to match byte-for-byte.
Ensemble estimates require all 80 runs and retain every extinction instead of dropping failed societies.

[The first prefix audit](results/reproduction-boundaries-prefix-2026-10-16/analysis.json) validates three runs and preserves their lossless trajectories.
It contains no ensemble estimate. Complete mode rejects the unfinished run before creating an output directory.
A corrupted population value, with its ledger hash deliberately updated, also fails sampled accounting before output creation.
The 80-run experiment remains in progress; its full outcome and paper-level fidelity are unestablished.

## Complete reproduction-boundary experiment

[All 80 declared runs](results/reproduction-boundaries-complete-2026-10-16) completed 100,000 cycles without extinction.
`analyze_boundaries.py RUN complete NEW_OUTPUT` passes source-variant, command, file-hash, scalar, timestamp and sampled accounting checks.
All 20 birth-cost age-only pairs have byte-identical aggregate and observation files.
An independent standard-library recomputation validates all 640 seed/window metrics, with maximum absolute difference 4.55e-13.
All generated source variants, original trajectories, manifests, paired contrasts and both declared windows are retained.

For the late window, cycles 75,100–100,000, descriptive means are:

| Scenario / metric | Inclusive baseline | Strict wealth only | Paper Table 1 |
| --- | ---: | ---: | ---: |
| Low fertility: population | 836.66 | 836.33 | 837 |
| Low fertility: wealth | 4,551.87 | 5,132.87 | 4,767 |
| Low fertility: mean age | 439.47 | 548.98 | 473 |
| Low fertility: Gini | 0.53136 | 0.52757 | 0.53 |
| Birth cost: population | 821.63 | 824.04 | 824 |
| Birth cost: wealth | 15,900.86 | 16,244.13 | 16,254 |
| Birth cost: mean age | 1,423.12 | 2,346.69 | 2,264 |
| Birth cost: Gini | 0.33690 | 0.33269 | 0.33 |

Strict wealth changes birth-cost mean age by 923.57 cycles, with a paired seed-level 95% interval of [902.10, 945.04].
The strict-wealth mean-age interval is [2,330.12, 2,363.27]; the earlier window mean is 2,352.02.
Changing puberty equality has no effect in the birth-cost scenario, as predicted from the newborn resource constraint.
For low fertility, strict wealth increases mean age by 109.51 cycles and moves the estimate past the paper's 473.
Strict age alone gives a low-fertility late mean age of 447.69; strict age and wealth together give 545.78.

Thus wealth equality explains a large part of the birth-cost age discrepancy and improves several other birth-cost measurements, but does not establish the paper's historical rules.
Neither published-rule variant resolves all age results in both scenarios.
The author's percentage uncertainties have unspecified meaning and are not treated as acceptance margins or confidence intervals.
The original baseline remains unchanged. These exploratory diagnostics do not complete or invalidate the paper replication.

## Appendix B equation and Figure 6(b) diagnostic

[The retained vector extraction and audit](results/figure6-recurrence-2026-10-16) recover all 304 exported vertices for the four discrete-model curves.
`audit_figure6.py ORIGINAL_FIGURE_PDF NEW_OUTPUT` pins the original PDF, verifies axes and line styles, and preserves exported coordinates.
Only observed vertices within labeled cycles 1–80 enter inference; omitted collinear points are not interpolated.
Both delay candidates use identical observed transitions, requiring coordinates at cycles t−3, t and t+1.

Equation 6 prints `N(t+1) = N(t) * [1+r-N(t−tau)/K]` and the surrounding text discusses delay three.
Its positive constant solution is `N=r*K`; thus its parameter K is not itself carrying capacity unless r=1.
To diagnose the plot, hold each legend rate fixed and fit one coefficient b in `N(t+1)=N(t)*[1+r-b*N(t−tau)]`.
This is descriptive fitting, not a held-out prediction or a recovered author implementation.

| Legend r | Observed transitions | Zero-delay inferred r/b | Zero-delay RMS error | Delay-three RMS error |
| --- | ---: | ---: | ---: | ---: |
| 0.47 | 31 | 832.997 | 0.043 | 36.909 |
| 2 | 76 | 832.991 | 0.048 | 327.133 |
| 2.7 | 76 | 832.998 | 0.090 | 1,086.563 |

Errors are population counts. These curves are consistent with a zero-delay recurrence containing `r*N/K`, with inferred K near 833.
The printed equation can express the same zero-delay curves only by assigning different K values: approximately 1,772.334, 416.496 and 308.518.
The r=0.025 curve stays at tiny populations; coordinate rounding prevents useful identification of its density coefficient.
Do not interpret its fitted K as an estimate of carrying capacity.

This identifies an equation/parameter ambiguity requiring an explicit choice before reproducing the discrete regimes.
It does not establish that the author intended delay three for panel (b), nor recover the agent-based curves in panel (a).
Original agent dynamics and evolutionary cases remain unresolved; no model rule was changed to match these fits.
An independent standard-library calculation reproduces all eight fitted cases within 1.8e-14; a wrong source PDF is rejected before output creation.

### Forward reconstruction of Figure 6(b)

[Forward replay](results/figure6-forward-replay-2026-10-16) advances each recurrence for 80 cycles from population one at cycle one, using inferred K=833 and zero delay.
These inputs were chosen after the vector diagnostic; this is an exploratory reconstruction, not an independently specified replication.
`replay_figure6.py EXTRACTION NEW_OUTPUT` retains four algebraically equivalent floating-point expressions for all four legend rates.
It compares 262 available vertices per expression, totaling 1,048 comparisons; omitted late vertices remain unmeasured.

For `N*(1+r-r*N/K)`, maximum population differences are 0.075, 0.057, 0.066 and 0.759 for rates 0.025, 0.47, 2 and 2.7, respectively.
For the chaotic rate 2.7, all expressions have maximum differences below 0.075 through cycle 40.
Their maximum differences through cycle 80 range from 0.759 to 10.013 agents.
Every expression is retained; no best-fitting expression is designated as the author's implementation.
This sensitivity prevents interpreting late chaotic differences alone as evidence of a different model rule.

A fresh original-PDF extraction followed by replay produces byte-identical comparison and report files.
Changing a retained vector ordinate fails the input-hash check before any result directory is created.
This advances the discrete-curve reconstruction only; panel (a), evolutionary societies and paper-level completion remain outstanding.

## Observed growth flows

[Population-band analysis](results/growth-flows-2026-10-16/analysis.json) checks all 600,000 observations from the completed growth ensembles.
Bands use population before each cycle and retain every visit, including returns after declines.
An independent NumPy calculation exactly reproduced all 1,000 seed-band records.
The retained simulator source is revision `61c885c`, whose hash matches the original run manifest.

For low fertility, births per agent-cycle were 0.011772 at population 11–100 and 0.011779 at population 101–400.
Both bands had zero deaths; the configured fertility draw probability is 1/85, or 0.011765.
These descriptive observations differ from the whole-trajectory logistic fit's mean rate of 0.025721.
They support distinguishing observed birth frequency from the fitted logistic parameter; they do not resolve the author's fitting protocol.
Birth-cost runs produced 0.016011 births per agent-cycle at population 11–100, despite a fertility draw probability of 0.1.
Resource eligibility constrains reproduction in that scenario.
These are exploratory summaries of existing trajectories, without confidence intervals or a new replication verdict.

```bash
python replications/stevenson_2021/analyze_growth_flows.py /complete/growth-run /new/flow-analysis replications/stevenson_2021/results/growth-flows-2026-10-16/simulate.cpp
```

## Earlier author specification recovered

[The August 2021 predecessor audit](results/predecessor-source-audit-2026-10-18) supports the implemented action order and delayed newborn activation. Its birth-cost sensitivity uses a later 130,000–150,000-cycle window, outside our existing ensembles. This does not establish the target paper’s sampling protocol. Evolutionary inheritance/update rules and historical implementation remain unresolved; no acceptance rule or simulator behavior changed.

## Evolutionary initialization constrained by the original figure

[Figure 4 vector extraction](results/figure4-vector-constraints-2026-10-18) retains 22 curves and 4,015 vertices.
Both ten-trait marginal count sets independently imply 830 initial agents, with unequal per-trait counts and plotted zero initial wealth.
This differs from the one-agent fixed-society growth initialization; that initialization cannot be reused unchanged for Figure 4.
The exported observations cover approximately generations 0–499. Gray curves do not individually label their alternative trait values.
Joint trait assignments, inheritance, mutation, placement, ages, and generation-to-cycle mapping remain unresolved; these constraints do not complete the study.

## Conditional inherited-trait evolution implemented

[The 100-seed stable reconstruction](results/evolution-stable-2026-10-18) completes 50,000 cycles and audits 3,194,850 inheritance events.
Two full homogeneous controls preserve the original simulator's aggregate and individual observations byte-for-byte.
All runs select infertility 10 and birth cost zero by cycle 499 under the declared initialization and exact-inheritance assumptions.
Mean population, age, wealth, and Gini at that cycle are 856.38, 12.7652, 492.55, and 0.693396.
The four labelled Figure 4 curves supply 1,988 comparison vertices; pointwise ranges remain descriptive.
This implements one evolutionary scenario conditionally. It does not establish the original inheritance rules, steady-state sampling, chaotic scenario, or whole-paper replication.

## Conditional chaotic-parameter evolution

[The second 100-seed ensemble](results/evolution-chaotic-2026-10-18) completes another 50,000 cycles and audits 20,018,826 inheritance events.
Infertility initially ranges from 1–10; birth costs range from 0–90 in tens. Both pass unchanged to offspring.
All runs select infertility1/birthcost0 by cycle499 under the declared assumptions.
Cycle499 population ranges from 178 to 1,839, with means population888.74, age1.39440, wealth438.42, and Gini0.739173.
The original stable figure is not treated as a numerical target for this case.
Both evolutionary cases are now conditionally implemented; historical settings, sampling, intrinsic growth rates and full paper-level agreement remain unresolved.

## Growth rates of the selected traits

[Two additional 100-seed growth ensembles](results/selected-growth-2026-10-18) cover infertility/birth cost 10/0 and 1/0 from one founder for 3,000 cycles.
All 600,000 native observations pass accounting checks; the unchanged declared fitting convention yields mean logistic rates 0.238694 and 0.972369 versus Table 1's 0.170 and 1.542.
Independent residual recomputation validates all 600 optimizer attempts. Mean root-mean-square residuals are 34.73 and 464.14 agents.
The unknown author fitting protocol and poor chaotic-case logistic residuals prevent interpreting these discrepancies as validated negative replications.
Full growth-rate coverage is now executed under a declared convention; historical agreement and steady-state sampling remain unresolved.

## Long-run evolutionary ensembles

[The qualified extension](results/long-evolution-qualification-2026-10-18) runs both evolutionary scenarios for 100,000 cycles across the same 100 seeds each.
Two 5,000-cycle native observer pairs pass exact output comparisons. The initial four long runs complete with exact shared-prefix matches and accounting checks.
[The full 200-run ensemble and its late-window analysis are complete](results/long-evolution-complete-2026-10-18); historical interpretation remains unresolved.
The sparse observer changes exports only. Prior dense inheritance evidence remains retained, and no paper-completion credit is assigned.

[The independent long-run prefix audit](results/long-evolution-prefix-audit-2026-10-18) validates 52 complete runs and 52,052 observations.
Full-mode analysis rejects incomplete ensembles before writing output; prefix mode withholds across-seed statistics.
The final analysis passes all 200 runs, using the frozen windows and explicit extinction handling. No run became extinct.

## Complete Table 1 comparison

[All twenty printed means](results/long-evolution-complete-2026-10-18/table1/comparison.csv) now have descriptive reconstruction estimates from the declared ensembles and growth fits.
The new evolutionary late-window population means are 858.774/919.125 and Gini means are 0.689854/0.728303 for stable/chaotic scenarios.
All 200 long runs complete 100,000 cycles; 200,200 observations pass audit, and an independent calculation confirms all 96 statistical quantities.
This completes execution of the declared long ensembles, not the paper replication. Original conventions, fixed-society age discrepancies, growth fits and remaining figure/Appendix B scope remain unresolved.

## Figure 6(a) subsistence societies

[Both printed parameter cases](results/figure6a-subsistence-2026-10-18) now complete 100 seeds over 505 cycles, using metabolism four.
Two metabolism-three parity checks preserve the original engine outputs exactly; all 101,000 new cycles pass independent resource/population checks.
Original vectors provide 995 actual-curve comparisons, separating the visible 200-cycle axes from exported vertices through 505.
The unknown author seed, phase and fitting procedure prevent an exact-trajectory claim; pointwise seed bands are descriptive and no paper-completion credit is assigned.

## Later birth-cost sampling window

[The original 100-seed ensemble is being extended to 150,000 cycles](results/late-birth-cost-launch-2026-10-19), preserving rules and verifying every existing prefix.
The first two complete runs match 2,002 shared observations exactly. Full analysis rejects incomplete ensembles.
This tests the earlier author's 130,000–150,000 window as a declared sensitivity; it does not identify the target paper's sampling protocol.

## Figure 3 wealth and inequality targets

[All 362 markers](results/figure3-vector-targets-2026-10-19) are recovered from the original vector PDF: 50 puberty, 65 infertility and 66 birth-cost points in each panel.
Axis calibration confirms logarithmic mean-age, wealth, and Gini scales. Repeated extraction is byte-identical, and the rendered reconstruction matches source shapes.
Numerical parameter assignments, seeds and steady-state windows remain unknown; this closes target extraction, not the missing sensitivity experiments.
