# Table 8: first point-estimation experiment

This is an incremental experiment, not a replacement for the complete nine-algorithm comparison.
Before running it, transcribe the linear-regression targets from the published Table 8:

| Rows | Initial population | Maximum spice | Maximum sugar | Mutation probability | Reproduction wealth |
| --- | --- | --- | --- | --- | --- |
| 1,250 | 0.513 | 0.387 | 0.399 | -0.131 | 0.394 |
| 5,000 | 0.606 | 0.546 | 0.539 | 0.279 | 0.734 |

Use the pinned archive's 5,000 input/output rows. Remove the seed column and the four globally constant output columns.
For the smaller case use the first 1,250 rows, as in the author's notebook.
Use five-fold cross-validation with seed zero, preserving original row order inside training and testing partitions.
Fit ordinary linear regression on all 146 summaries for each parameter using R's `lm` and `predict`.
Calculate each fold's root mean squared error, average across folds, and normalize against the similarly averaged
training-mean baseline error. This follows the released code's metric, including the order of averaging.

The author did not record the R version. R 3.6 changed the default discrete sampling algorithm.
Run both historical `Rounding` and newer `Rejection` kinds with Mersenne-Twister and Inversion;
record both results without hiding the less similar result. Do not search arbitrary seeds.
Compare the ten resulting values for each kind against Table 8 at its three-decimal published precision.
A matching kind supports an environment explanation; it does not establish the original R version.

Retain each held-out prediction, fold, input row, baseline, and software version.
Do not infer confidence-interval coverage from this point-estimation experiment.
Bootstrap interval estimation and the other eight algorithms remain separate required work.
