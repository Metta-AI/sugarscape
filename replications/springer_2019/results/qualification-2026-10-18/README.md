# Native CUDA qualification

The final portable build compiles all three implementations and completes six original-horizon (10,000-iteration) executions on a 32×32 grid. All source files are checked against the official artifact. Only two allocator headers differ, with four dependent-template keywords and two explicit template-specialization arguments. All Sugarscape model files are byte-identical.

Three earlier failed qualification attempts remain retained with complete archives and readable build/runtime logs:

1. Archived CUB conflicts with CUDA 11.8 Thrust; both static baselines run successfully.
2. Matching toolkit CUB/Thrust exposes missing dependent-template keywords; both baselines run successfully.
3. The author's later allocator syntax fix exposes two unresolved member-template addresses; both baselines run successfully.
4. Explicitly selecting those template specializations compiles and runs DynaSOAr as well.

The failed attempts are not negative replications. Their baseline repeats do not add scientific seeds. Across all attempts, 18 execution records share the same seed/configuration.

All native checksums are zero. Source inspection shows this checksum sums agent type codes only; it provides no independent resource, wealth, movement, or full-state validation. Full-size scientific experiments remain unstarted, and these timings do not reproduce Figure 10.

All four complete remote archives were exported, downloaded, and verified against sealed SHA-256 receipts before the owned GPU node was stopped. `raw-archives.json` records retained storage objects. The final complete archive is also included as `portable-native.tar.gz`; the smaller folders expose every attempted runner, compiler log, native log, dependency header, patch record, and terminal status without extracting the raw archives.

Run `audit_qualification.py NEW_REPORT.json ARCHIVE1 ARCHIVE2 ARCHIVE3 ARCHIVE4` to verify archive source identity, exact permitted syntax changes, complete build/run coverage, binary hashes, debug compilation flags, and native checksum/timing records. The auditor does not substitute successful execution for a paper-level verdict.
