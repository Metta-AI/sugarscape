# Static vision geometry qualification

The candidate caches six cardinal vision patch sets per patch during existing setup. Movement retains the original occupancy filter, current-patch union, tie-breaking, and random draws. Production models and active jobs are unchanged.

Two frozen generated inputs, populations 10 and 510, run 10,000 ticks each in baseline/cached/cached/baseline order. All eight executions pass. All 60,000 Gini-history comparisons and 16,710 original world-row comparisons are exact, including random states. Only export timestamps and the new cache column are excluded. All twelve final metrics match between variants; 24 archive comparisons pass the previously declared Gini/morphology tolerances.

At population 510, simulation times are 16.365/16.692 seconds for baseline and 11.302/11.419 for cached geometry: median ratio 1.455. At population 10, the ratio is 1.012. These shared-machine observations do not establish a full-grid speedup. Cache initialization and export costs are excluded from simulation timings; complete-process receipts are retained.

The initial candidate inserted its patch variable first. The morphology extension reads fixed variable positions and failed with a type cast. That source, failed execution, and logs remain archived. Appending the cache field preserves every original variable position; successful repeats use this corrected candidate.

The 8,997,054-byte archive preserves 99 files, including both candidates, baseline sources, runtime commands, failed and successful outputs, and original license notices. Fresh extraction verifies every member hash and reproduces the audit byte-for-byte.

Remaining: broader seed/population/layout qualification and measured end-to-end throughput before using the cache for the full generated ensemble. No generated-coverage increment, revised spending estimate, or paper-completion credit is claimed.
