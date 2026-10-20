# Qualified Sugarscape method reproduction

**Completed method reproduction with explicit reconstruction choices. Historical numerical agreement and a validated negative result are not established.**

The scope is the paper's Sugarscape case, including model construction, convergence sampling, reduction, policy ranking, genetic optimization, full-model transfer, and timing. The separate rabbits-and-grass case is outside this Sugarscape study.

| Requirement | Completed evidence | Qualification |
| --- | --- | --- |
| Figure 8 and Appendix B | Native model, landscape-cell audit, event/state qualification | Independent reconstruction; printed death-rule conflict preserved |
| Figure 9 | 20,000 native runs; 100 controls, 100 seeds, two clocks | Original controls and their generating distribution unavailable |
| Figure 10 | 2,538,400 reduced runs plus 10,000 independent full-size runs | Both rounding conventions, clocks, rank weights, ties and strata retained |
| Discrepancy investigation | 37,600 unique-stream inputs and 37,600 paired death-rule inputs | Sensitivities explain some variation; do not identify historical settings |
| Algorithm 1 | Eighteen searches, 432,000 native evaluations, complete genetic-decision replay | Population 24, twenty generations and neighborhood semantics declared |
| Figure 11 method | All 144 final policies, 200 held-out seeds each; 28,800 native runs | Finite candidate comparison; no proven global frontier |
| Independent reporting | R recomputes 57,600 objectives and 144 dominance decisions | One-standard-error bars are pointwise, not simultaneous inference |
| Table 2 method | Published batch counts executed three times; 18,039 measured runs plus 600 warmups | New hardware and interval definitions; historical seconds not reproduced |

The full-model optimizer and reduced-model optimizers use the same frozen budget. Every final evaluated policy is transferred; favorable policies are not selected after observing the paper targets. Three optimizer seeds are reported separately. All thirteen width-five policies are empirically dominated, compared with seven of twenty-four width-forty policies. These findings do not reproduce the paper's universal claim for its selected historical reduced frontiers.

## Fidelity and deviations

Direct review of the published Algorithm 1 image confirms evaluation, Pareto carryover, parent selection, complementary uniform crossover, declining component mutation, and generation iteration. The paper omits the neighborhood metric/radius, population size, generation limit and some tournament details. The primary campaign declares its choices. Alternative tournament semantics were exercised in qualification. Odd population slots retain one child; unevaluated final offspring receive no frontier credit.

Appendix B prose kills at zero sugar; Algorithm 3 uses a strict negative threshold. Primary ensembles follow prose, with the alternative retained as a paired sensitivity. Clock phase, negative-payment clipping, map sampling and vision rounding remain explicit. No convention was changed to force agreement.

The inherited GUI plot crashed on extinction. The qualified headless adapter removes that callback while preserving model rules. Full reference replay and retained-prefix comparison verify this correction. Failed evidence remains preserved.

Published batch counts are retained for ranking comparability. They are not evidence of equal runtime on this platform: the measured simulation batches span 1.7288–2.7325 seconds. A new equal-time performance claim would require separately calibrated budgets and experiments. It is not made here.

## Completion basis

The user's criterion is genuine method reproduction, not mandatory numerical agreement. Every Sugarscape method stage now has completed native evidence and independent checks. Missing historical artifacts and unproven global optimality qualify the interpretation; they are not replaced by favorable numerical thresholds. This counts as one qualified method reconstruction, not a wholly positive paper or a validated negative replication.

`assessment.json` links and hashes the requirement evidence and reviewed implementation. `rankings.json` reconciles all twelve complete ranking cases without counting failed or repeated prefixes twice. Reproduce that reconciliation using portable paths:

```sh
python reconcile_rankings.py /path/to/replications/oremland_2014 /path/to/new-rankings.json
```

Source: [Oremland and Laubenbacher (2014)](https://www.jasss.org/17/2/6.html), Sugarscape sections 4.20–4.29, Appendix B, and Algorithm 1.
