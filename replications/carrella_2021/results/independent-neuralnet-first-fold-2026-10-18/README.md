# Independent neural-network first fold

The first completed fold validates 4,000 training rows, 1,000 held-out rows, and all 755,000 input values exactly.
All independent input files match their provenance hashes. The seed-zero fold partition is reconstructed independently.
The audit checks 5,000 posterior-median predictions and recomputes errors, interval coverage, and widths within 1e-10.

| Parameter | Independent RMSE | Interval coverage |
| --- | ---: | ---: |
| initial.population | 47.96470512 | 0.729 |
| pmut | 0.02907776 | 0.717 |
| maximum.sugar.endowment | 10.45396986 | 0.672 |
| maximum.spice.endowment | 10.27167837 | 0.672 |
| wealth.reproduction | 6.52728964 | 0.906 |

Baseline errors equal the author-data first fold. The retained comparison is descriptive across simulation random streams.
Four folds remain; this is neither an aggregate Table 8 result nor a completed paper replication.
The producer continues unchanged, retaining observation-level checkpoints.

`evidence.tar.gz` includes the native completed fold, runtime inventory, command, frozen checkpointing sources, input provenance, predictions, and audit.
Every member matches its retained original byte-for-byte. Rerunning the auditor on the extracted fold reproduces both audit and predictions byte-for-byte.
