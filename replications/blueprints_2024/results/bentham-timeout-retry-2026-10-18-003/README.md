# Two additional original-input timeout recoveries

Original Bentham inputs 197 and 203 complete their unchanged 5,000-step horizons.
Fresh source/configuration/seed/trajectory audits validate 10,002 observations.
Both classify as better or equal under the released plotter’s definition.

Exact reconciliation reaches **1,835/2,000 homogeneous inputs**, with Bentham
335/500 and the other three models complete at 500 each. All 165 remaining
Bentham inputs are still required; this does not complete the paper.
Earlier timeout failures remain preserved and receive no scientific verdict.

The native archive preserves both complete input directories and original retry
plan, producer and failure records. Every file was checked byte-for-byte.
`archive.json` retains its SHA-256; `attempts.json` retains commands and durations.
For relocated extraction, rerun `audit_batch.py` using `--recorded-root` with the
original input path from `audit-commands.json`. Reconcile those audits with earlier
evidence using `reconciliation-command.json`. This frozen snapshot excludes later
outputs from the still-running producer.
