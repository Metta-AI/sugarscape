# Phase III movement policies: released and corrected selectors

Scope: the movement-policy experiment in Pike's Phase III, Figures 3-7 and 3-8.
This does not include the separate common-resource experiments or complete the paper.

Run 1,200 trajectories: 100 NumPy/module-random seeds (0–99), two grouping approaches (explicit/network), three thresholds (1/5/10), and two selectors (released/corrected-highest).
Each trajectory uses 1,000 steps, 200 initial agents, the released landscape and defaults, and Mesa seed 42.
Set PYTHONHASHSEED=0. Use Python 3.11.14, Mesa 0.8.5, NumPy 1.26.4 and NetworkX 3.6.1 as in the validated pilots.
The author's NumPy and module-level random states are unavailable; these are newly specified paired seeds.
The selected last pre-publication source revisions are not authenticated paper revisions.

The released arm enables the original randomly chosen low/high/geometric-mean movement policy.
Its high-focus selector actually chooses the member with the smallest maximum holding; this mismatch is explicitly retained.
The corrected arm changes exactly one comparison operator in that method, selecting the largest maximum holding while preserving first-in-order ties.
All other rules, random policy selection, activation, trading, and resource handling remain original.
No shared-balance, network-deletion, or starvation-order corrections are loaded.

Default-setting adapters have byte-identical native controls for both approaches.
The corrected network threshold-ten seed-zero pilot and passive trace have five-file byte parity; all 260 high-focus calls select the largest maximum.
The same original high-focus method syntax occurs in both released approaches.
The known pilot seeds remain in the full grid; no seeds are selected or dropped based on outcomes.

Freeze the protocol, batch driver, native runner, configuration adapter and correction modules before launch.
Execute one sequential worker. Preserve commands, completion records, source hashes, raw-file hashes and exit statuses.
Stop on any failed run or below 2 GiB free; retain partial data and never substitute seeds.
Iteration order is seed, threshold, approach, selector, so paired conditions accumulate together.

## Measurements and interpretation

Require the complete declared grid before aggregate comparison.
Audit 1,000 observations per run, individual identities, finite holdings, positive transaction prices, configuration metadata, and file hashes.
Separate individual survivors from the native reporter that includes groups/resources.
Reconstruct per-step geometric mean prices, sample standard deviation of log prices (only for at least two trades), and transaction counts.
Preserve undefined prices/dispersion. Do not pool timestep samples as independent simulation replicates.
Report seed-level 95% intervals and paired differences between selectors, approaches and thresholds.
Compare movement-policy effects against the corresponding completed and audited no-policy Phase II conditions.
Report both released-code outcomes and correction sensitivity; do not silently relabel corrected runs as historical replication.
The paper's price convergence and survival claims require the complete comparisons, not one pilot or mere nonsignificance.
Concurrent local jobs invalidate historical runtime comparisons; retain timing as operational metadata only.
