# Complete-horizon descriptive trends

All 64 breed/setting metabolism curves finish below their initial mean; all sixteen EC vision curves also finish below their initial mean.
Only the sixteen EC metabolism curves have no upward stored-mean steps. Every EC vision curve has upward steps.
This supports initial-to-final decline, not a universal monotonic decline or causal explanation.
Step counts include floating-point summation noise in the stored means; they are not counts of meaningful biological changes.

Python analyzes every transition from tick 0 through 20,000, without selecting windows.
Independent R checks 1,600,080 mean values, with maximum scaled endpoint error 2.98e-16, and all eighty exact decimal step-sign counts.
The first R check failed: its decimal-to-binary conversion changed some near-zero increments.
For EC/EC breed A vision, 6,513 of 20,001 parsed values differ from Python, by at most 8.89e-16.
`parser-discrepancy.json` retains concrete decimal/hexadecimal examples.
The amended R verifier compares right-zero-padded decimal strings under the C collation order after checking their numeric format.
This independently preserves exact decimal ordering without a tolerance, changed analysis, or rerun simulation.
The original verifier and failure remain here.

Run `python analyze.py RESULTS PARAMETER_COMPARISON_JSON NEW_OUTPUT`, then `Rscript --vanilla verify_decimal.R RESULTS NEW_OUTPUT NEW_VALIDATION`.
