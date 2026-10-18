# DynaSOAr Sugarscape benchmarks (Springer and Masuhara, 2019)

Status: source recovered; native qualification pending. No paper completion credit.

The [ECOOP paper](https://doi.org/10.4230/LIPIcs.ECOOP.2019.17) benchmarks a Sugarscape model with movement, resource consumption, ageing, and mating. Its [official artifact](https://doi.org/10.4230/DARTS.5.2.2) contains the model, allocator implementations, dependencies, and archived reproduction instructions. The artifact is the source of truth for this study; the framework's other applications are outside its Sugarscape scope.

[Source audit](results/source-2026-10-18/audit.json): archive MD5 matches the publisher's checksum; SHA-256 is `75421734305809c5999904082616996a904a19a5e43466cf076ec10660e559a1`. All archive files have recorded hashes. Four Sugarscape implementation files, configuration, build script, and benchmark driver match current GitHub revision `a4f956cd13160eb566e8a0caef6aad1e59c26da9` exactly. This comparison does not assert equality of the entire allocator library.

## Complete Sugarscape targets

- Figure 10: total and enumeration timing for DynaSOAr, mallocMC, Halloc, BitmapAlloc, CUDA allocation, and static array-of-structures/structure-of-arrays baselines.
- Figure 11: maximum Sugarscape problem size at equal allocator heap sizes, excluding enumeration arrays as the paper does.
- Sections 6.1–6.2: assess the Sugarscape performance and memory-efficiency interpretations against reproduced measurements.

Original defaults are a 1,700×1,700 grid, seed 42, and 10,000 iterations. The benchmark driver requests five repeats. The paper uses a Titan Xp, CUDA 9.1, Ubuntu 16.04.4, and an 8 GiB allocation heap for timing comparisons. Contemporary GPU results must state their hardware/toolchain differences. Historical absolute seconds cannot be transferred to a different GPU.

The source driver requests `sugarscape_no_cell`, while its archived CMake target is `sugarscape_soa_no_cell` and shell-build output is `sugarscape_dynasoar_no_cell`. Execute verified source paths rather than treating a missing executable as a failed paper result.

## Qualification protocol

Before full benchmarking, build the unchanged archived static-cell DynaSOAr implementation and both static baselines in debug mode. Use a 32×32 qualification grid, the original 10,000 iterations and seed 42, and two executions per binary. Preserve compilation logs, exit status, native checksum, timing, source hashes, and device/toolchain identity. Debug assertions and successful execution are prerequisite evidence, not independent model validation or paper replication.

The original CUDA 9.1 Docker tag is unavailable. Qualification therefore uses the pinned CUDA 11.8 Ubuntu 20.04 image recorded in the protocol, with compute-6.1 PTX for driver compilation. This changes compilation/runtime provenance; model sources remain unchanged. No timings from this small qualification grid count toward Figure 10.

Full-grid timing, matched-heap capacity searches, independent state/conservation checks, published-bar extraction, and claim-level analysis remain outstanding. Keep source defects, failed builds, allocator failures, and hardware differences visible before assigning any verdict.
