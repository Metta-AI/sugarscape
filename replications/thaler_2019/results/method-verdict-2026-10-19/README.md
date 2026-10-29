# Qualified method reproduction

**Completed qualified author-code method reproduction for the Sugarscape case study.**
This applies the user's October 19 criterion: faithfully execute the method without requiring the same numerical results.
Earlier incomplete historical-results verdicts remain preserved. No primary measurement or numerical tolerance changes.
The separate SIR epidemic study is excluded; this is one completed paper study.

## Execution and fidelity evidence

| Required Sugarscape workflow | Evidence |
| --- | --- |
| Population dynamics, Figure 5 | All 50 original Figure 5b values match; the original Figure 5a asset matches all 201 occupied cells at exported time 83. |
| Concurrent population behavior | All 225 native processes and 225,000 observations are audited across the full grid. |
| Tables 6 and 8, Figures 6 and 7 | All 45 original timing conditions execute with the pinned source/compiler and original Criterion measurement workflow. |
| Table 9 timing | All six 16/32/64-capability conditions execute on the matching instance class. |
| Table 7 retries | All 90 processes across eighteen conditions retain audited integer commit/retry counters. |
| Table 9 retries | All thirty processes across six conditions complete, retaining the discrepant 32-capability result. |
| Observation semantics | Four native TArray runs verify 4,000 observations; full-grid occupied-cell counts stay at 2,500 despite missing newborn observations. |

The current re-audit reopens all ninety raw retry processes and the four observation-semantics trajectories.
The complete 51-condition timing comparison replays byte-for-byte from pinned constituent audits.
Every fresh report matches its retained counterpart. `verification.json` records their hashes.
This re-audit adds no simulations or coverage.

Sources and full commands remain in the [study README](../../README.md),
[retry ensemble](../retry-scaling-complete-2026-10-18), [timing grid](https://github.com/Metta-AI/sugarscape/tree/0f0c4350672e75a47a8373c119b7291a8d0c2168/replications/thaler_2019/results/timing-grid-complete-2026-10-18),
[population grid](https://github.com/Metta-AI/sugarscape/tree/0f0c4350672e75a47a8373c119b7291a8d0c2168/replications/thaler_2019/results/population-grid-complete-2026-10-18), and [Table 9 evidence](https://github.com/Metta-AI/sugarscape/tree/0f0c4350672e75a47a8373c119b7291a8d0c2168/replications/thaler_2019/results/table9-complete-2026-10-18).

## Departures, diagnostics, and result comparisons

- The source is pinned to `f5851488bf2369e2bbdc3f2499ed69c142de9fec`, with GHC 8.4.3 and Criterion 1.4.1.0.
- Tables 6/8 use different hardware from the historical laptop. Table 9 matches the instance class, but historical clocks and isolation are unknown.
- The predeclared timing protocol retains all attempts and selects the first fit meeting R-squared 0.99, with at most three attempts per condition.
- Retry instrumentation changes scheduling, so instrumented timings do not substitute for the separate uninstrumented timing workflow.
- Five fresh processes per retry condition are a declared repeat convention; the historical repeat count is unspecified.
- Figure 5a matches at exported time 83, not its caption's time 50. This post-hoc time alignment is required for the exact image match.
- The image search covered times 0–100 and found one exact match. It does not prove the historical capture procedure or justify relabeling the primary clock.
- Counting occupied cells resolves a TArray newborn-observation issue. The exporter adds this diagnostic without changing model rules; the original count remains retained.
- The matching-instance 32-capability retry discrepancy persists. A separate Criterion-versus-single-process control does not recover the printed ratio.
- Three prose claims conflict with the paper's own timing tables. Their source comparisons are separate from hardware-dependent fresh timing differences.

No hardware, fit, time index, or retry result was selected to replace the primary comparison with a better-looking outcome.
The time-aligned image match is explicitly conditional. No universal dynamics equivalence or causal scheduler explanation is established.
The original segmentation fault, timeouts, argument-order error and bounded recovery history remain retained.
They do not become successful invocations merely because disjoint recovery completed the required conditions.

The documented simulation and benchmark methods are reproduced with these qualifications.
Exact historical timing, scheduling, and image-capture provenance remain unresolved; numerical mismatches are not automatically negative paper verdicts.
