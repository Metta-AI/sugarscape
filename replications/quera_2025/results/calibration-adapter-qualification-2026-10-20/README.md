# Coupled calibration adapter qualification

The original BlackBIRDS adapter pairs simulator values with derivatives from a separate random realization.
Passive tracing verifies separate primal and dual model calls, with 85/100 and 84/100 differing values in the two samples.
All five exported native artifacts remain byte-identical with tracing enabled.
Both inspected DifferentiationInterface versions, 0.6.43 and 0.6.54, evaluate the value and Jacobian separately.
The ordinary loss is 167.7298745604437; the original differentiated loss is 88.1527470240483 despite resetting the same seed.
This is an implementation discrepancy in the executed adapter, not a paper-level negative replication.

`paired.jl` introduces a separate backend that restores the initial random state for every forward-differentiation call.
It takes both value and Jacobian from the same differentiated result; the author model and MMD loss remain unchanged.
The corrected ordinary loss is 167.7298745604437 and differentiated loss is 167.72987456044382.
Independent Python reconstructs the two-channel loss and six chain-rule gradients, with maximum gradient difference 2.59e-12.
All 1,200 Jacobian components participate in the audit; each nominal sample matches its ordinary simulation draw.
A complete-workflow artifact with one corrupted gradient is rejected. A separate trace corruption is also rejected.
These checks establish arithmetic and random-realization pairing, not unbiasedness of the underlying surrogate gradients.

The qualification uses 100 agents, a 25×25 landscape, 50 stored states, seed-zero observations, and simulator seed 20261021.
The channels are mean wealth across initial agents and alive fraction. Gaussian smoothing is 1.
The six parameters are [0.2, 0.8, 2, 5, 5, 2]. The MMD loss uses two simulator samples and w=0.0001.
The channel denominator, seeds, and loss scale are declared reconstruction choices, not recovered historical calibration settings.
The loss scale is not optimizer weight decay.
Twenty samples and densities from the six-dimensional, four-layer, two-block, 32-unit flow are finite.
No optimization or posterior predictive comparison has been executed in this qualification.

The isolated coupled environment has 368 packages, compared with 348 in the previous DiffABM environment.
There are 164 changed common packages and 74 newly present packages; this is a reconstructed runtime.
The original manifest remains unchanged. Complete seed-zero agent and cell CSVs match the prior qualified runtime byte-for-byte.
DiffABM is pinned to 9178eccd56dd352e3515e276239654239f8d3b41; BlackBIRDS to 277bc7e99df581f0e73de9d7a63ad1ccc81dd833.
PyTorchNormalizingFlows is pinned to 01438e4c95c3f924704eb85945950c6a03ab8502.
The retained environment uses Julia 1.11.3; runtime PyCall selects the qualified Python 3.11.14 environment with Torch 2.6.0 and normflows 1.7.3.
The initial incorrect one-channel attempt and failed Python binding remain preserved as failed/superseded evidence.

Extract `native-evidence.tar.gz` into a new directory and copy the retained JSON files there.
Run `python3 audit_paired.py EXTRACTED_DIRECTORY NEW_AUDIT_JSON` to repeat the complete arithmetic audit.
The provenance check also requires the original manifest paths; preserve them or explicitly relocate those references without changing hashes.
Native scripts retain execution-machine paths. Relocate source, project, and output paths when reproducing elsewhere.
Use `PYCALL_JL_RUNTIME_PYTHON` to select the qualified Python runtime, an isolated Julia depot, and one Julia thread.
The original adapter and passive trace remain available separately from the correction.

Remaining work includes the declared five-sample, 5,000-epoch optimization, validation selection, prior specification, and posterior/predictive comparisons.
Historical prior and validation settings remain unresolved and must be reconstructed explicitly if unavailable.
This result adds no completed-study credit.
