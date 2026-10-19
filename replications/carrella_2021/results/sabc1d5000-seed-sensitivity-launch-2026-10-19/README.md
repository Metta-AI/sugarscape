# Full-data estimator random-seed control

Ten prospectively fixed seeds, 1–10, run semi-automatic ABC 1D on the unchanged 5,000 author inputs and original five cross-validation folds.
The primary seed-zero scores remain unchanged. The earlier ten-seed sensitivity study used 1,250 inputs and does not answer this full-data question.
This runs the estimator only, without new agent simulations.

One local worker has a 600-second bound per estimator run and 120 seconds per audit, each with termination grace.
The enclosing job has a 6,600-second bound plus 30-second grace.
Before each seed, admission requires more than 700 MiB free disk and less than 400 MiB already retained in this job.
These are admission guards, not a hard filesystem quota; evidence and failures are preserved.
The same core package versions as the primary run are required.

Every successful seed must match all 3,775,000 training/test input cells and pass a separate audit of all 25,000 held-out predictions, interval coverage, and widths.
Reported ranges will describe sensitivity, not confidence intervals or a recovered historical random stream.
Launch adds no audited seeds, primary score matches, or completed-paper credit.

The exact command, process handles, source hashes, scripts, and predeclared protocol are retained.
