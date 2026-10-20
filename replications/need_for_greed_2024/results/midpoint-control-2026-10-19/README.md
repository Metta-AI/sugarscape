# Complete native midpoint pair

The Bentham baseline and selfishness-0.5 sweep at original seed 238165197779399277 both complete 5,000 steps. Their 5,001 observations match byte-for-byte across all 38 logged fields. Final population is 978 in both runs.

The new baseline trajectory also matches its previously retained audit hash exactly: `d2f922e3f14470666d6fcd648407b2f006cfddf1e021fb9d9c6d25d2e6e8516b`. This is a newly executed control with its own provenance, not a recovered original raw file.

The baseline took 527.04 seconds; the sweep took 591.96 seconds. Both exited zero within the fixed 600-second limits. Their original deposited configurations are retained; only logfile paths changed. Source hashes match the pinned author release.

`audit.py EVIDENCE_DIRECTORY NEW_OUTPUT_JSON` verifies source pins, original ZIP bytes, effective configurations, terminal receipts, complete consecutive observations, finite scalar fields, pair equality, and prior baseline hash agreement. Repeating the audit gives byte-identical reports. Both compressed trajectories pass exact decompression readback.

This qualifies the selected midpoint pair, not all 100 seeds or unlogged internal states. The selfishness-one controls remain running or pending in the original six-input batch. Shared-ensemble coverage and completed-paper counts are unchanged until the control batch is reconciled.
