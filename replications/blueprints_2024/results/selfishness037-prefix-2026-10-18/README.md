# First 25 bulk selfishness-0.37 inputs

All 25 sealed inputs complete the original 5,000-step horizon: 125,025 observations independently audited locally against the original configuration ZIP. No trajectories are truncated and none ends in extinction.

The native archive matches the remote SHA-256 receipt. Every archived file matches its extracted bytes; all 25 local audits match the producer audits. Each source pin, original configuration, allowed logfile-only change, PyPy version, finite observation, terminal result, and trajectory hash passes the existing supplementary auditor.

These inputs are disjoint from the ten previously completed supplementary inputs. The regenerated complete inventory contains 99,965 remaining inputs. The selfishness-0.37 condition has 28 of 500 completed inputs, leaving 472. Runtime qualification repetitions count once per original input.

This is a completion-order checkpoint from an active bounded batch. It does not establish an unbiased condition aggregate or complete a paper replication. The existing eight-worker job continues within its original budget.

Reproduce each local audit with `audit_supplement.py ORIGINAL_SELFISHNESS_ZIP EXTRACTED_RUN NEW_OUTPUT --expected-runtime pypy`. Inventory provenance lists all four native archives and audit directories supplied to `plan_supplement.py`.
