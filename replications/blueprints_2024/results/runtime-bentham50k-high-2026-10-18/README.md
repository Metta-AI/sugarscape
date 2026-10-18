# Two complete Bentham 50,000-step runtime inputs

Original runtime inputs [50,52) complete all 50,000 steps, with 100,002 audited
observations. Both finish in the author's better-or-equal category. Source pins,
original configuration bytes, random seeds, command paths, exit records, ledger
hashes, trajectory fields and terminal outcomes pass `audit_runtime.py`.

The unchanged declared interval remains [50,100). Only these two completed
inputs receive credit. The sealed checkpoint was exported to owned object
storage, downloaded, checksum-verified and audited after extraction. The public
archive matches that verified download byte-for-byte.

Exact original-input reconciliation raises deposited runtime coverage from
854 to 856 of 1,200 configurations, with 2,299,313 observations. This is the
deposited 100-seed runtime grid, not the paper's claimed 500-seed Table 6 ensemble.
Remaining inputs and the full paper remain incomplete.
