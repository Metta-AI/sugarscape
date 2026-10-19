# Complete-ensemble analyzer validation

The analyzer consumes a terminal ten-seed ensemble and rejects unfinished ensembles before creating output.
It verifies pinned source hashes, all successful seed receipts, exact-input audit counts, and relevant package versions against the primary run.
It checks unique prediction identities and identical held-out truths across seeds.

Python independently recomputes fold errors, training-mean baseline errors, coverage, interval widths, and normalized scores from prediction CSV files.
The training mean for each fold uses only truths from the other four folds.

The existing complete 1,250-input ensemble passes: 62,500 predictions and 9,437,500 audited input cells.
Maximum absolute difference from R metrics is 3.410605131648481e-13, below the declared 1e-10 arithmetic tolerance.
A second execution produces byte-identical results. The actual unfinished 5,000-input ensemble is rejected without creating output.

This validates analysis plumbing on existing evidence. It adds no new simulation, historical-fidelity conclusion, or study completion credit.
The full 5,000-input ensemble remains running. Observed seed ranges are not confidence intervals.

Run from the checkout: `python replications/carrella_2021/summarize_estimator_seeds.py ENSEMBLE NEW_OUTPUT`.
The ensemble must retain its pinned source paths and per-seed R input/prediction audit artifacts.
