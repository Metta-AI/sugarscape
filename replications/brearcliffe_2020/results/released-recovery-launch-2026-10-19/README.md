# Bounded recovery of twenty-five unstarted inputs

Command `cmd-pp9jf` started at 2026-10-19T22:58:35.689606Z on the existing task-owned CPU node.
Live plan readback confirms exactly SARSA/SARSA repeats 25–49, eight workers, unchanged inputs, and the original 1,800-second per-input limit.
The wrapper verifies prior batch termination, absence of all selected run directories, assignment hashes, and the existing qualified runtime before executing.
No previously completed input is assigned. This is a separate bounded recovery, not an extension of the original command.

Admission is bounded at 7,500 seconds; the outer limit is 7,800 seconds with a thirty-second termination grace.
The verified rate is $0.012/minute. Execution, export and idle bounds total at most $1.926; the allocation cap is $2 including staging margin.
Terminal export is limited to 900 seconds and 128 MiB. The collector waits for the explicit sealed archive path, avoiding dependence on paginated snapshot discovery.
The node retains its fifteen-minute idle stop. No unbounded retries or automatic extension are permitted.

The producer is confirmed running; this launch adds no completed-input or paper credit.
Full raw audits and the combined fifty-run cohort analysis remain required after successful execution.
