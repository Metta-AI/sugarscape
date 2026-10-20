# Paper-table EC / EC complete cohort

All fifty frozen inputs complete 20,000 steps: 1,000,050 observations including initial states.
The cumulative full-trajectory audit covers 1,052 unique inputs and 21,041,052 observations, preserving all 1,002 prior records exactly.
Coverage is 750 released-code and 302 paper-table inputs: fifteen and six complete pairings respectively.

All fifty trajectories are byte-identical to their paired released-code trajectories.
This confirms that changing the learning parameters leaves this non-learning pairing unchanged. It does not identify the historical learning settings.

Independent R checks 320,016 means, 320,016 sample standard deviations and fourteen endpoints using 20,000 whole-run bootstrap repetitions.
Maximum scaled errors are 1.466e-15 for means, 7.150e-15 for standard deviations and 5.534e-16 for interval endpoints.
The corrected raster comparison contains 3,274 visible records and 602 unresolved records.
Two of twelve readable endpoint mean ranges overlap the paper ranges; two endpoints are unresolved.
The full endpoint values and intervals remain in `comparison-summary.json` without selecting or relabelling breeds to improve agreement.
Raster ranges are not statistical intervals; these comparisons do not establish equivalence or a negative paper result.

[Durable storage readback](../paper-ec-ec-durable-evidence-2026-10-19) verifies the archive and all 502 members.
Method completion still requires the remaining declared pairings and the cross-interpretation claim synthesis.
Original historical seeds need not be recovered to establish method completion, but remain a qualification on exact-result comparisons.
