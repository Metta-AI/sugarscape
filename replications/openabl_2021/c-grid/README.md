# Complete published C input grid

All seven Figure4 requested sizes, 500 through32,000, execute100 steps with the released C generator and one OpenMP thread. Independent initialization reconstruction matches502,648 fields; complete four-stage replay matches502,648 final fields. Actual grid sizes round down to square counts.

The replay now indexes fixed half-integer cell centers instead of scanning every cell pair. Sorting neighbor indices preserves released array-order tie breaking. Radius1.5 includes exactly the nine neighboring offsets. Complete native output comparisons cover all seven grids, plus five completed copy-buffer controls in the validation record. The initial optimization incorrectly asserted integer centers; it failed before replay, and its failed local log remains retained.

Every native final agent ID, wealth, metabolism, and environment-sugar value equals its initial value across these seven conditions. Target positions change; at15,876 actual cells, one state field also changes. The comparison retains exact counts instead of generalizing the225-cell observation. Larger copy-buffer controls remain running.

The archive preserves instrumented model, generated C and binaries, initial/final snapshots, source pins, successful native receipts, and independent audits. Every archived member matches its source byte-for-byte. Frozen quadratic replays remain running separately; the indexed replay supplies the complete validation reported here.

Instrumented wall times under concurrent workloads are not historical performance replications. MASON, FLAME, GPU, distributed scaling, and exact compiler provenance remain required.
