# Baseline timeout diagnosis

The failed egoistic input with seed 530238075247992587 previously completed in 2,095.149 seconds.
Its recovery limit was 1,800 seconds. Reviewing all 333 retained results finds six prior runtimes above that limit, with maximum 2,273.909 seconds.
The recovery plan should have used these retained runtimes when choosing its bound.
Different hosts and concurrency prevent direct timing guarantees, but this was a foreseeable timeout risk.
The sum of prior elapsed wall times is 29.378 hours; it is not measured CPU consumption.

The failed run's retained trajectory contains 4,399 complete records through timestep 4,398, versus the required 5,000.
Every completed record has the original seed, consecutive timestep, and finite scalar/array values. Its last population is 1,365.
There was no stderr traceback. The native timeout receipt reports exit124 after1,800.008seconds.
The raw4,630,527-byte file is retained losslessly in failed-trajectory.json.gz, with SHA-256 in partial-audit.json.
Parsing only closes the unfinished array in memory; it does not alter the retained failed output or create a successful result.

This identifies a timeout-planning error, not a demonstrated model mismatch or negative replication.
No partial trajectory is counted. The 219-input audited inventory remains unchanged.
The original coordinator remains bounded and stops admissions; already-running attempts must finish and be reconciled before recovery assignment.
A future recovery needs a fresh disjoint manifest and explicit bounds informed by retained timings. It must compare full hashes and this failed prefix before gaining credit.
