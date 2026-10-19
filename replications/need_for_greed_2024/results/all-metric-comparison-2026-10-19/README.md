# Five measurements at selfishness 0.37

Fresh raw readback covers the same 100 original seeds and 495,265 observations. Population, mean wealth, mean time to live, and mean age at death agree graphically with Figures 2–4 and 6 under all four checked averaging conventions. Only this single selfishness level is compared.

| Measurement | Paper vector centerline | Observed mean including initial row, then median across seeds |
| --- | ---: | ---: |
| Population (earlier Figure 2 extraction) | 1151.5261 | 1151.4803 |
| Mean wealth | 130.4770 | 130.4840 |
| Mean time to live | 18.18744 | 18.18751 |
| Mean age at death | 59.61695 | 59.61659 |
| Starvation plus combat deaths (%) | 1.648409 | 0.401332 |

Graphical agreement means the comparison point falls within the nominal PDF vector stroke under the recorded axis calibration. It is not statistical equivalence or proof of historical averaging. Target centerlines are geometric extractions, not recovered numeric author data.

## Death-rate discrepancy and control

The paper explicitly excludes aging deaths from Figure 5. Eight starvation-plus-combat conventions yield medians 0.343082–0.401413%, all outside the plotted stroke. These vary inclusion of the initial row, treatment of zero-population rows, post-extinction padding, and mean ratios versus ratios of sums. Zero-population death counts remain recorded; they are not silently discarded from ratio-of-sums calculations.

A separate diagnostic adds aging deaths. Its eight medians are 1.666500–1.688562%, all within the nominal stroke around the 1.648409% centerline. Aging inclusion is therefore compatible with the graph at this condition, but contradicts the written definition. It does not replace the primary calculation or establish the historical pipeline. No validated negative replication is assigned.

The pinned release’s `plots/plot.py` exports starvation and combat counts for its time-series plot. It does not supply the paper’s across-selfishness median plotting pipeline. Further source investigation is required.

## Verification and reproducibility

`aggregate.py` reopens native archives and verifies archive hashes, all 100 trajectory hashes, consecutive timesteps, and native terminal states. It records 24 values per run: four conventions for four direct metrics and eight death-rate conventions. No simulation is rerun or excluded.

`validate_numpy.py` independently recomputes all 2,400 values from raw trajectories with NumPy. Maximum scaled error is 4.26e-16. It also records the separate aging-inclusion diagnostic. `compare.py` extracts median vector paths from Figures 3–6; repeated extraction is byte-identical. Captions and axis limits were visually checked on PDF pages five and six.

```sh
python aggregate.py BLUEPRINTS_CHECKOUT COHORT_AUDIT_JSON NEW_METRICS_JSON
python validate_numpy.py BLUEPRINTS_CHECKOUT COHORT_AUDIT_JSON METRICS_JSON NEW_VALIDATION_JSON
python compare.py AUTHOR_PDF METRICS_JSON NEW_COMPARISON_JSON
```

Validation requires NumPy; comparison requires PyMuPDF. Input hashes, original archive locations, per-run values, and comparison conventions are retained in the JSON reports. Full ensembles, quartiles, historical conventions, and the rest of the paper remain incomplete.
