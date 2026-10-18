# Criterion retry-collection control

The author instrumented entry point uses Criterion's repeated benchmark workflow and prints cumulative counters after each simulation.
Our completed retry ensemble instead used one simulation per fresh process via `--iters 1`.
Both modes use the same previously audited instrumented executable.
This diagnostic tests whether repetition and counter accumulation help explain the 32-capability discrepancy.

The fixed shuffled schedule contains three single-iteration processes and three Criterion-default processes.
Each uses the original 500-agent, 1,000-step, seed-42, non-rebirthing configuration at 32 capabilities.
The collector retains every printed cumulative commit/retry count and derives each simulation's increment.
No counter reset, model change, or post-hoc repetition selection is introduced.
Instrumented timings will not enter the performance comparison.

The owned m5ad.16xlarge instance was freshly verified stopped before starting this distinct diagnostic.
The binary hash matches the prior audited experiment.
Each process has a 540-second limit; the service has a 3,600-second workload limit and owns its entire cgroup.
A verified host timer stops the instance at 10:21:01 UTC, before the 75-minute lease expires.
The maximum compute charge at the recorded rate is $4.12.
After terminal archive verification, the collector checks that ownership and lease remain unchanged before requesting an earlier stop.

The service is active at this checkpoint. No new retry outcome or completed-study credit is claimed.
Earlier single-process results, failures, and source inspections remain unchanged.
