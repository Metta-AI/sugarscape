# Coverage with gaps

The real retained audit set still reports 1,586 unique inputs and 430 excluded repeats.
All previously published fields match; the new fields expose individual ranges and missing indices.

A separate reconciliation uses real Bentham intervals `[0,4)` and `[5,6)`, supplied out of order,
with `[5,6)` repeated. It reports five unique inputs, one excluded duplicate, prefix `[0,4)`,
and missing index 4 before the later completed input. The full-grid flag remains false.
These are subsets of existing evidence, not newly executed simulations or additional coverage.
The retained commands and input hashes identify every source audit.
