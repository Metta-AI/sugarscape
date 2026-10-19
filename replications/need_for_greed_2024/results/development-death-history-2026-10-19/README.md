# Development history of the death-rate calculation

The author's [June 30, 2024 plotting change](https://github.com/nkremerh/sugarscape/commit/31cb37cd5c61aa5dbd121a025bc1986423822b78) introduces starvation + combat + aging deaths divided by pooled population.
Its parent plotting file lacks the aging term.
Six of eleven inspected 2024 plotting snapshots contain the identical death-sum expression.
The December 12 change moves percentage calculations into simulation statistics.
Git dates establish source metadata; they do not prove when the paper's figures were generated.

The unchanged June `findMeans` function ran against per-timestep sums from the same 100 original selfishness-0.37 trajectories.
Fresh archive/member checks cover 495,265 observations.
All 5,001 calculated rates match the later v2024.3 control exactly and pass independent NumPy arithmetic with zero maximum difference.
The temporal means are 1.67073218% including the initial state and 1.67106633% excluding it.
The corresponding temporal medians are 1.64613839% and 1.64614172%.
These are diagnostics of pooled rates, not a claim about the paper's aggregation.
The full parser is not executed; the control preserves its zero-initialized post-extinction convention.

None of the eleven inspected plotting files calls a median function.
This does not exclude separate unpublished scripts or another plotting path.
Aging inclusion conflicts with the paper's stated exclusion and therefore remains a diagnostic, not a replacement replication metric.
The historical boxplot pipeline remains unidentified. No primary score, input coverage, or completed-study status changes.

`prepare.py` records the checked development head, original source hashes, and exact syntax-tree expressions.
Author source files and MIT license are preserved unchanged.
`analyze.py` executes the historical function on hash-verified native evidence.
`comparison.json` checks exact equality against the previously published later-release control.
The existing earlier release-history evidence remains untouched.
