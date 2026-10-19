# Table 9 native launch on the published instance type

The six 16/32/64-capability timings and five fresh retry processes per condition are now launched.
AWS instance `i-059f1fc4ff524c015` is `m5ad.16xlarge`, matching the paper's instance type.
The live host reports AMD EPYC 7571, one socket, 32 physical cores and two hardware threads per core.
The process has 64 logical CPUs available. Matching these specifications does not prove
identical clock behavior, host contention or the original operating-system/kernel environment.

The original GHC 8.4.3 model sources and Criterion 1.4.1.0 remain pinned.
The execution script builds and retains the uninstrumented timing binary first.
It then builds a separate retry binary with only the already verified statistics flag change.
Timings never use the instrumented binary. All failed attempts and partial outputs remain evidence.
Timing order and retry order are frozen before execution; five retry processes are our declared
sampling choice because the paper's historical retry repetition count is unknown.

Each timing condition uses the original raw iteration schedule and first passing R² ≥ 0.99 fit,
with at most three attempts. Each attempt is capped at 1,200 seconds.
The timing phase allows 7,200 seconds; retry processes have 300-second limits.
A separate 9,600-second outer process bound includes setup; the EC2 lease is three hours.
Any deadline leaves unmet conditions incomplete rather than reducing the study scope.

The AWS price API quoted $3.296/hour for Linux shared-tenancy on-demand service in us-east-1.
Three hours of compute costs $9.888, plus the 40 GiB root volume.
The account reaper checks expired leases every five minutes, so this is a nominal lease budget,
not a provider-guaranteed dollar cap. Stop preserves the disk; termination is separate.
The existing SSM launcher provides access without inbound SSH or copied credentials.
Only this new task-owned instance was created; no shared fleet workload was changed.

The collector targets this instance and process, validates the archive, downloads at most 100 MiB,
and verifies its byte count and SHA-256. The remote disk remains intact if collection is interrupted.
This launch establishes execution and hardware evidence, not Table 9 completion or a paper verdict.

## Independent complete-grid auditor

`timing/audit_table9.py EXTRACTED_TERMINAL_ARCHIVE NEW_OUTPUT` is prepared for the terminal capture.
It requires all six timings, thirty retry processes, exact frozen schedules, source-archive hashes,
separate executable hashes, successful native exits and matching allocation records.
It independently reconstructs timing slopes, R-squared and sample dispersion from the raw measurements;
retry ratios are recomputed from each original transaction-counter log.
Only formatting, lint and command-interface checks have run so far.
The full audit remains unvalidated until real terminal evidence arrives.
