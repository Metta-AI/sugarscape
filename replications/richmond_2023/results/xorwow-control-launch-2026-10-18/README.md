# RNG-family control for historical illustrations

The illustration-era engine uses CUDA's default `curandState` (XORWOW). The released engine instead selects Philox by default. Both movement choice and conflict resolution draw uniform random values; equal numeric seeds across these generators do not establish equal trajectories.

The complete model GPU-function and exit-condition prefix is byte-identical between the illustration-era and released benchmark revisions. Both engine revisions propagate submodel seeds using the same multiplication rule, so seed zero remains zero in this comparison. Protocol source paths, immutable revisions and hashes retain the basis for this hypothesis. CUDA documents its default generator at https://docs.nvidia.com/cuda/archive/12.2.2/curand/device-api-overview.html .

The bounded control uses the existing Clang-derived initial state, unchanged model/observer source, and 100 steps. Before building a variant, the original Philox binary must reproduce the prior state-file hash exactly. The variant changes only the engine's supported `FLAMEGPU_CURAND_ENGINE=XORWOW` option. Recorded compiler flags must include XORWOW and exclude Philox. Both trajectories will receive the same full state-accounting and fixed image-comparison audit.

Owned H100 command `cmd-xwnrm` has a 2,940-second execution limit plus 60 seconds for termination. Approximate cost cap is $5 including idle grace. The collector has a one-hour/100-MiB bound. Two pre-execution registration errors are retained: the service interpreted an unsuffixed duration as minutes, then rejected an on-wake command after restoration had finished. The uploaded script was hash-verified before the successful detached launch; rejected commands did not execute the model.

This is a frozen diagnostic, not a historical-engine reproduction. Differences in CUDA/runtime scheduling, visualization timing and other engine behavior remain possible. No new completion credit or negative-paper verdict is assigned. The previous raw archives and stopped-run evidence remain intact.
