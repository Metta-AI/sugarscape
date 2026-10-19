# Criterion execution-budget correction

Criterion 1.4.1.0 executes a warmup and batches of 1, 2, 3, 4 and 5 iterations
before returning the four-sample report used by the original experiment.
The fifth batch executes before the stop gate; its measurement is excluded from the returned accumulator.
Thus the reported ten iterations require at least sixteen actual model iterations on the slow-benchmark path.

Using the paper's 32-capability rebirth slope gives 16 × 76.4 = 1,222.4 seconds before overhead.
The previous 1,200-second attempt cap was inadequate even for that reference-based estimate.
The 64-capability estimate is 1,585.6 seconds. These calculations do not prove the timeout's sole cause.

The revised protocol permits 3,600 seconds per attempt, 14,400 seconds for timings,
18,000 seconds combined native work and 18,600 seconds for the outer shell.
A six-hour instance lease caps nominal compute at $19.776, excluding retained disk.
The runner now reads these bounds from the frozen protocol instead of duplicating them in code.
All six conditions, raw sampling, first-passing-fit rule and thirty retry processes remain unchanged.
The failed attempt remains retained. A corrected run subsequently launched in `sugarscape-table9-002` on the same retained instance.
Its original process identifier is 1865, with a 18,600-second outer timeout.
Collection is bounded at 100 MiB and 22,000 seconds. No result or completion is credited yet.
