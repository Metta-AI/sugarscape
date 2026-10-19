# Correct horizontal calibration against the paper’s actual plot frames

The previous digitizer mapped column 17 to tick zero for every figure.
The longest continuous top grid line starts at column 28 in Figures 3 and 8, column 17 in Figures 4 and 5, and column 31 in Figures 6, 7 and 9.
All end at column 302. Direct pixel checks verify these boundaries in all 112 source panels; representative extracted images were inspected visually.
The paper defines the horizontal range as ticks 0–20,000. No simulation values were used to choose the revised coordinates.
The one-pixel uncertainty and all vertical calibration/color thresholds remain unchanged.

The corrected target contains 62,016 records. All retained vertical measurements match the earlier artifact exactly.
Two complete PDF extractions are byte-identical. Endpoint-mode execution matches the pre-change script byte-for-byte.
The first endpoint regression check incorrectly compared against an older artifact with different status wording; its failed assertion is retained.
The corrected check executes the actual pre-change source. It does not normalize or weaken output comparisons.

All four complete cohorts were compared again with unchanged simulation means and summary hashes.
All 4,576 vision/metabolism comparison records remain byte-equivalent as JSON objects.
On the shared, visible combat/starvation columns, every previously positive separation disappears after the coordinate correction.
For Rule M/SARSA alone, those positive column counts fall from 65/69/63/62 to zero for combat A/B and starvation A/B.
This resolves an error in our measurement pipeline; it is not evidence of a negative replication.
The EC vision discrepancy remains: 245 of 286 columns are above the paper’s raster interval.

| Cohort | Visible curve records | Unresolved records | Overlapping endpoints / visible endpoints |
| --- | ---: | ---: | ---: |
| Rule M / Rule M | 2,162 | 1,714 | 9 / 9 |
| Rule M / EC | 3,803 | 73 | 12 / 14 |
| Rule M / Q-learning | 3,163 | 713 | 11 / 12 |
| Rule M / SARSA | 3,807 | 69 | 14 / 14 |

The comparator now requires the corrected target hash. Earlier artifacts remain historical evidence and are superseded for curve interpretation.
The two Figure 6 label conflicts remain excluded; hidden curves remain unresolved.
Raster overlap is not equivalence, adjacent columns are dependent, and historical seed/parameter ambiguity remains.
No new simulation or completed-study credit is added.
