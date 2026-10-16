# Dogan (2026): completed mixed replication

The released numerical experiments reproduce. Several explanatory claims do not.
This is a completed mixed study of the pinned working paper and its released model, not a wholly positive replication.
It uses an original-source integration in Metta-AI/sugarscape, not an independently implemented DTL model.

## Scope and fidelity

Source: [author repository](https://github.com/dgnerg867-ux/sugarscape/tree/0b6a3df470388f60535d8ffb67c34a7f9fa0059a), revision `0b6a3df470388f60535d8ffb67c34a7f9fa0059a`.
The manuscript is an unpublished working paper. Its PDF hash is recorded in the canonical manifest.
Original MIT and Apache notices remain with the bundled source.

All 700 primary original runs complete: 205 canonical, 45 horizon, 210 composition, 75 levy, 105 per-seed calibration, and 60 multiplier runs.
Original calibration runs also execute; these are not counted as additional scientific conditions.
The fork separately completes all 205 canonical runs, producing four byte-identical files containing 206,010 cells.
All sixteen bundled files match their provenance hashes.
The [artifact audit](results/completion-2026-10-16/artifact-audit.json) rechecks retained output hashes, native exits, coverage, and original/fork equality.
The [README](README.md) supplies commands, environment, individual validators, and raw-evidence locations.

Python 3.12.4 and the author's four package pins are preserved.
NetworkX 3.7 supplies an omitted dependency; this is our explicit environment recovery choice, not a claimed author pin.
No published seed, horizon, model rule, parameter, or failing result was removed to improve agreement.
The original and bundled model remain unchanged. The levy correction is a separate, fully retained research variant.

## Numerical claims

| Claim / target | Result | Evidence |
| --- | --- | --- |
| Main Tables 1 and 6 | All 56 printed values match fresh simulation | [Static/UHI audit](results/static-uhi-2026-10-15/tables1-and6.json) |
| Main Tables 2 and 5 | All 168 printed values match | [Transition audit](results/transition-tables-2026-10-15/tables2-and5.json) |
| Main Table 3 | All 105 printed values match independently reconstructed agent-level decomposition | [Decomposition](results/decomposition-2026-10-15/table3.json) |
| Main Table 4 | All 42 printed values match; death categories reconcile in all 105 runs | [Fresh transition evidence](results/transition-2026-10-15) |
| Appendix Tables B.1, C.1, D.1 | All 282 printed values match | [Welfare](results/full-canonical-2026-10-15/table-b1.json), [composition](results/composition-2026-10-15/table-c1.json), [horizon](results/horizon-2026-10-15/table-d1.json) |
| Figures 1 and 2 | All 42 plotted ordinates match independent means; image pixels differ with rendering environment | [Figure audit](results/figures-2026-10-15/series-audit.json) |
| Original canonical reports | All nine regenerate byte-for-byte | [Reports](results/full-canonical-2026-10-15/reports) |
| Mortality advantage over baseline and universal arms | All 570 available paired-seed comparisons favor pure means-tested policies | [Dominance audit](results/mortality-dominance-2026-10-16/mortality-dominance.json) |
| Per-seed threshold calibration | Maximum mean-Gini change 0.022269 rounds to 0.022; reported adjacent swap and mortality rank stability reproduce | [Per-seed audit](results/completed-sweeps-2026-10-16/perseed-audit.json) |
| UHI multiplier insensitivity | Mortality unchanged across all four multipliers in all 15 speed/seed conditions | [Multiplier audit](results/completion-2026-10-16/multiplier-audit.json) |
| Excluding owners preserves inequality deterioration | Both pure means-tested policies have higher Gini and worse ranks under fast than slow automation | [Owner exclusion](results/owner-exclusion-2026-10-16/owner-exclusion.json) |

These are descriptive replications of the published seed sets, not newly established statistical significance.
The horizon design has no universal-policy arm at 600 steps. Its baseline comparison cannot establish the absent comparison.
The legacy starvation script duplicates the canonical conditions but computes stock-at-death differently; it is not an additional manuscript experiment.

## Contradicted claims and diagnosed causes

| Manuscript claim | Validated finding |
| --- | --- |
| Within-type contributions are lower under means-tested policies at every speed | Four of six mean comparisons are higher. Fast working-human Gini is also higher under both policies. [All 420 type/run records](results/within-type-2026-10-16/within-type.json) reconcile with the exact Table 3 reproduction. |
| The menu lacks recurring direct taxation of autonomous wealth | Native wealth taxation reaches autonomous agents. A full fast seed-zero run collects 1,657.743030 units over 14,910 positive autonomous tax calls. [Observed/native trajectories](results/tax-reach-2026-10-16/tax-reach.json) are byte-identical and match canonical outcomes. |
| Only the displacement levy reaches the autonomous-owner channel | Labor and wealth taxes also collect from owners; the same native tax audit measures both. |
| Equation 4's levy transfers the capped deduction into the treasury | Original code deducts `W*min(1,L/W)` but credits `L*min(1,L/W)`. All 60 observed events violate conservation. The isolated correction conserves transfers and completes all 75 paired conditions. [Diagnostic and protocol](LEVY_DIAGNOSTIC.md). |
| The wealth cap binds in roughly a quarter of fast D=50 events | It cannot bind under this 300-step protocol: new-owner wealth is at least 50, while the maximum nominal levy is 25. The event audit observes zero caps. |
| Mortality varies by less than 5% across D | Original fast mortality varies by 6.907% under the declared maximum/minimum convention. Corrected balanced and fast ranges also exceed 5%. [Paired comparison](results/completed-sweeps-2026-10-16/levy-audit.json). |
| Static coefficients of variation are all below 0.13 | Maximum is 0.1320268, correctly printed as 0.132 in Table 1. All remain below 0.15. |
| Welfare-specification changes preserve every inequality ranking | Baseline/UHI exchange ranks under balanced automation. The gap is small; mortality ranks remain unchanged. |
| Composition preserves the full mortality ordering; inequality exceptions are already pinned at extremes | Two complete mortality orderings occur. The named inequality exceptions move ranks. Highest-baseline and lowest-pure-means-tested mortality still hold in all nine mean settings. |
| Section 4.2 has 200 on-grid agents and total populations 235–280 | All 105 native snapshots have 180 on-grid agents and totals 215/230/260. This matches the specified initial composition when owners are counted off-grid. |
| Fast automation exhausts working humans by step 300 | There are 45 working humans at step 300 in every fast canonical run. Fast and balanced reach zero at 600; slow retains 30. [Population audit](results/completion-2026-10-16/artifact-audit.json). |
| Single-resource fractions 87.4–98.0% bound every seed | That range describes five-seed means. Individual runs span 80–100%. |

These discrepancies are not inferred from an unexplained failure of our model.
The numerical outputs reproduce the deposit, independent arithmetic reproduces the tables, and native observers preserve complete trajectories.
The levy defect is localized to the author's transfer formula; the corrected model is never substituted for faithful reproduction.
The correction changes sensitivity estimates, so the original levy robustness argument cannot be accepted without qualification.

## Interpretation and completion boundary

The paper's descriptive mortality advantage and sensitivity of aggregate inequality to automation speed reproduce within its tested design.
Its stronger account of universal within-type equalization and the absence of recurring autonomous taxation does not survive the implementation audit.
The decomposition remains a valid numerical result, but it does not establish that explanation.

Spatial capture as the binding cause, an absolute ceiling on transfers, and the superiority of proposed new policies are not identified by the released experiments.
Reproducing the welfare-function intervention does not isolate spatial competition from every other channel.
New causal ablations or proposed policies would be extensions, not missing executions of reported experiments.
No result here supports an extrapolation to real economies.

The study is complete as a mixed computational replication of this pinned paper, with reproduced outcomes and validated contradictions recorded together.
It does not establish independent-engine equivalence, pixel-exact rendering, historical environments beyond the recorded pins, or untested counterfactuals.
Those limits remain explicit; this study does not replace any unfinished paper in the broader program.
