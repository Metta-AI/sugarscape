# Historical random-stream allocation audit

Following the unsuccessful XORWOW image control, inspect the exact illustration-era and release engine sources.
The archive retains both GitHub trees, inspected source files, upstream licenses, and their hashes.
`source-audit.json` identifies each checked expression and line number.

Both revisions:

- Initialize CUDA random states using `curand_init(seed, offset + id, 0, ...)`.
- Offset each function's random-state pointer by the preceding layer thread count.
- Select a thread's random state using its linear CUDA thread index.
- Implement the model's `uniform<float>()` call with `curand_uniform`.
- Multiply the parent seed for submodels; the declared seed zero remains zero.

The illustration model explicitly sets seed zero and applies configuration before population initialization.
This audit therefore supplies no evidence for changing the seed or sequence-offset formula.
It does not prove identical agent ordering, CUDA library behavior, reset lifecycle, or historical binaries.
The release engine's XORWOW control remains an approximation to the historical engine.
No additional GPU job was launched, and no replication credit is assigned.

The next historical-runtime experiment needs the pinned old engine and its supported toolchain,
with native configuration and initial-population verification before interpreting later image differences.
Arbitrary seed searches or fitted image transforms would not establish the published experiment.
