# GAM comparison across simulation statistics: 5,000 inputs

All 25,000 held-out prediction pairs retain identical training/testing parameter columns.
Only the simulation statistics differ between datasets. The comparison reconstructs
the released mean-fold root mean squared error and each baseline-normalized score.

| Parameter | Author-data score | Independent-data score | Published score |
| --- | ---: | ---: | ---: |
| Initial population | 0.657583 | 0.663102 | 0.651 |
| Mutation probability | 0.378689 | 0.360610 | 0.428 |
| Maximum sugar endowment | 0.547270 | 0.586290 | 0.545 |
| Maximum spice endowment | 0.512286 | 0.593215 | 0.533 |
| Reproduction wealth | -0.632580 | 0.662000 | -0.894 |

Neither dataset matches any of the five published GAM values at printed precision.
This describes dataset sensitivity; it does not establish a causal explanation,
replace the author-data experiment, or complete the paper replication.

The largest single squared error accounts for 60.05% of total reproduction-wealth
squared error on author data and 80.99% on independent data. The improved aggregate
score therefore does not mean the independent prediction errors lack outliers.
These shares are descriptive diagnostics over all held-out predictions.

A separate Python calculation reconstructs all fold errors and normalized scores
from the paired predictions. The generalized comparator reproduces the preceding
1,250-input comparison exactly, including its predeclared outlier diagnostic.
An actual mismatched-size invocation is rejected before creating its output directory.
The fixed 1,250-input outlier row is not transplanted into the different 5,000-input folds.

```sh
Rscript replications/carrella_2021/compare_gam_streams.R AUTHOR_5000_DIRECTORY INDEPENDENT_5000_DIRECTORY NEW_OUTPUT_DIRECTORY
```

The two input directories contain the previously published native fold objects and
metrics. `validation.json` records independent verification and the source hash;
`paired-predictions.csv.gz` retains every pair without dropping outliers.
