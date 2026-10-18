# Pensions: native execution qualification

The unchanged deposited model runs under NetLogo 6.1.0, matching its recorded version.
The official runtime archive and extracted JARs are hashed in `runtime-download.json`.
Execution uses Java 11, one active processor, and a 512 MiB heap.

One deposited condition uses population 400, retirement age 65, tax 4.7, and fixed fee 0.1.
With new seed 20261018, it completes 1,000 steps. A separate repeat and an every-step
recording control produce identical endpoint records. All 1,003 exported records
pass finite-value, timestamp, Gini-range, and death-counter reconciliation checks.
These controls establish execution and observation consistency, not historical agreement.

The first launcher failed before simulation because an XML declaration conflicts with
this version's experiment loader. Its source, error, and exit receipt remain archived.
Removing the declaration fixes the launcher; the model itself remains unchanged.
All members of `qualification.tar.gz` were verified against retained evidence.

The full deposited experiment now runs all 128 conditions with ten repetitions each,
using seed `20261018 + behaviorspace-run-number` and the original 1,000-step horizon.
Its protocol is frozen here. The native process has a two-hour limit; an outer guard
allows five minutes for shutdown. It has no completion credit while running.
The full paper remains unrecovered, so its exact claims and experiment alignment remain open.
