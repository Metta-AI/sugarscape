# GAM sensitivity across simulation statistics

All 6,250 held-out predictions are paired by fold, row, and parameter.
Training and testing parameter columns match exactly across both simulation datasets.
The simulator random streams and resulting summary statistics differ.
The comparison recomputes the released metric: mean fold root mean squared error.
Both recomputed scores match their previously audited aggregate outputs.

| Parameter | Author-data score | Independent-data score | Published score |
| --- | ---: | ---: | ---: |
| Initial population | 0.499665 | 0.601619 | 0.528 |
| Mutation probability | 0.436194 | 0.457359 | 0.328 |
| Maximum sugar endowment | 0.347444 | 0.539755 | 0.311 |
| Maximum spice endowment | 0.164329 | 0.548530 | 0.328 |
| Reproduction wealth | -3.002351 | 0.817684 | -1.329 |

Neither dataset matches any of these five published values at printed precision.
This comparison does not replace the primary author-data result or establish a negative replication.

The previously diagnosed reproduction-wealth outlier is fixed before this comparison: fold two, held-out row 131, true value 92.
Its author-data prediction is -6,945.811, and its price summary is 17.761826 against a training range of 0.310144–1.394660.
The same parameter row under independent statistics predicts 92.356097.
Its corresponding price summary is 1.036271, within its training range of 0.866606–1.420271.
One author-data observation accounts for 99.943% of pooled reproduction-wealth squared error.
The largest independent-data observation contributes 16.757%.
These observations demonstrate dataset sensitivity. They do not isolate a causal simulator difference or recover the historical fitting environment.

`paired-predictions.csv.gz` preserves every pair and squared error.
`provenance.json` hashes all ten source folds, metrics, package manifests, and analysis code.
Reproduce with `Rscript compare_gam_streams.R AUTHOR_GAM1250 INDEPENDENT_GAM1250 NEW_OUTPUT`.
The required independent native fold objects are in the preceding independent GAM result archive.
The full Carrella study remains incomplete.
