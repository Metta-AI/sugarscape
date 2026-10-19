# Independent degree-four estimator

The required 5,000-input workflow is running unchanged, with seed zero, five folds, immediate warnings, a four-hour bound, and both independent audits scheduled after successful completion. No new predictions are credited yet.

The initial launcher incorrectly included size 1,250. The author small-data notebook disables this chunk and Table 8 reports NA. This attempted control failed after 2.47 seconds, before a completed fold; its failure is retained, not treated as a negative replication.

Installed abctools 1.1.8 uses half the training rows to construct its semi-automatic summaries. At size 1,250, each fold supplies 1,000 training rows and thus 500 regression rows. The original degree-four transformation expands 146 statistics to 584 predictors. The retained package source rejects this underdetermined regression. At size 5,000, it receives 2,000 regression rows instead.

No polynomial degree, statistic, fold, or original parameter row is removed to make the run pass. The original launch protocol remains preserved alongside its explicit scope correction.
