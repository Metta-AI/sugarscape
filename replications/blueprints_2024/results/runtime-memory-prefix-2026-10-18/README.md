# Five additional original runtime inputs

The sealed checkpoint adds Raw inputs [55,59) and Altruist input [3,4).
Independent audits validate 150,328 observations against the original archive,
source hashes, configurations, seeds, native commands, exit records and raw
trajectory hashes. Raw has two natural extinctions and two 50,000-step completions;
the Altruist input completes 50,000 steps. Extinction is the model’s terminal
condition, not a shortened surviving trajectory.

Exact reconciliation reaches **861/1,200 deposited inputs and 2,449,641 observations**.
All five inputs are new; no overlapping seed adds credit. The remaining 339
inputs, other paper experiments and the reported 500-seed runtime scope remain
incomplete. The producer was still running when this checkpoint was collected.

The archive SHA-256 is
`abd4ff022b65c3c1bd4843f982a20fcf3595661f59d43f0205b8b45677b74966`.
Export receipts identify the owned storage object. The public copy was verified
byte-for-byte against the download. Extract it into a fresh directory and run
`audit_runtime.py ORIGINAL_RUNTIME_ZIP EXTRACTED/GROUP NEW_AUDIT --allow-prefix
--recorded-root /root/sugarscape/blueprints-runtime-memory-001/runs/GROUP` for each
group. `audit-commands.json` retains the exact executed local commands.
