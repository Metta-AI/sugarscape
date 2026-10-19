# Original bundled-binary parity

All nine runs of the original release 1.1.2 bytecode finish successfully under OpenJDK 11.
Three configurations (`anim2-3`, `fig3-4`, `fig3-5`) each run twice natively and once with the existing read-only population observer.
Seed is zero; the scheduled-time limit is 1,000, matching the previous source-rebuild comparison.

Every native output and all 3,006 population-observer states exactly match the previous historical source rebuild.
Replacement accounting has zero disagreeing states.
Each reproduction configuration retains 989 disagreeing states out of 1,002, beginning at time 13.
Thus modern recompilation did not introduce these discrepancies in the tested runs.

All 387 bundled class files pass archive-hash readback, including 36 model class files.
Only the two existing replay wrappers are compiled, using an empty author-source search path.
JVM class-loading logs confirm that the model, scheduler, and random-number generator load from the unchanged extracted archive.
All extracted source, configuration, class and library hashes remain unchanged after execution.
No source overlay or compiler compatibility patch is used for the author model/framework.

This comparison uses the same modern Java runtime for both binary and rebuilt executions.
It does not establish historical JVM equivalence, recover versions 1 or 1.1.1, or authenticate the paper's MASON 10 experiment snapshot.
The study remains incomplete; no paper-level negative verdict or completion credit is assigned.

`run.py` retains extraction hashes, compilation, all commands, and native outputs.
`audit.py` verifies byte identity and class origins against `historical-native-2026-10-16`.
Repeated audit output is byte-identical; all published gzip files pass exact decompression readback.
The initial URI-string assertion and its correction are retained: Java's `file:/...` and Python's `file:///...` normalize to the same local path.
The correction changes no simulation or observed output.
