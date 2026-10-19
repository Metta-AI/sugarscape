# Independent bootstrap-forest recovery

The original 5,000-input producer reached its four-hour limit with one completed fold.
Its exit code is 124 and original process is absent. The interrupted second fold is not counted.

The retained first fold passes independent reconstruction of 755,000 input cells and 5,000 predictions.
Errors, interval coverage, and interval widths agree within 1e-10. The native checkpoint hash is recorded and its published copy verified.
The previously qualified recovery runner restores its outgoing random state and original partitions.
Folds 2–5 now continue in a fresh destination with unchanged estimator settings and a 20-hour bound.
The prior failed attempt and its logs remain preserved.

This is a recovery launch, not a completed full estimator or paper replication.
Completion requires auditing all five resulting folds and aggregate scores.
