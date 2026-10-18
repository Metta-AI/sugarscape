# Complete native pension experiment

The unchanged deposited NetLogo model completes all **1,280 runs**: 128 conditions, ten repetitions each, and 1,000 steps per run. NetLogo 6.1.0 matches the deposited version; execution uses Java 11 and explicit new seeds `20261018 + behaviorspace-run-number`.

The audit verifies source and output hashes, original parameters and experiment semantics, all run IDs, seed assignments, finite metrics, Gini bounds, constant populations, and the sum of working and retired starvation counters. Only the declared seed and two observational metrics differ from the deposited experiment. Runtime JAR hashes and the actual command remain inside the archive.

All 768 condition/metric pairs include both samples' means, sample standard deviations, and standard errors across ten repetitions. These are descriptive comparisons. Historical seeds are unknown; no equivalence margin or significance criterion was declared. The prior workbook audit separately preserves the author's erroneous standard-error divisor based on 128 conditions.

| Metric | Minimum new-minus-archived mean | Maximum new-minus-archived mean |
| --- | ---: | ---: |
| `(died-retired-turtles + died-working-turtles)` | -155.7 | 199.5 |
| `died-retired-turtles` | -33 | 37 |
| `died-working-turtles` | -155.7 | 199.5 |
| `precision  (   accumulated-gdp / ( ticks + 1) )  2` | -2.789 | 1.292 |
| `precision  ( (gini-index-reserve / count turtles) * 2)  2` | -0.01 | 0.011 |
| `precision piggy-bank 2` | -1937 | 2832.7 |

Every archived member was compared byte-for-byte with native evidence. After extraction, the complete audit reproduces identically. To reproduce, obtain the pinned model and archived CSV named in `../pensions-2020.json`, extract `native-evidence.tar.gz`, then run:

```sh
python3 audit.py EXTRACTED_NATIVE DIRECTORY_WITH_PINNED_SOURCE_AND_CSV NEW_AUDIT.json
```

The runner retains original machine paths and historical execution receipts; edit runtime paths only for a new, separately recorded execution. Do not overwrite this evidence.

**No paper completion credit:** the full 2020 paper remains unavailable. Exact paper targets, source-revision alignment, and fork-level independent behavior validation remain open. This result establishes complete execution and auditing of the deposited experiment, not historical random-stream agreement or a negative paper result.
