# Full published GPU size grid

All 13 published GPU size conditions have executed for 100 model steps.
The prior 250-requested-cell qualification supplies the smallest condition;
this deposit adds the remaining 12 unchanged generated-model conditions.
Requested counts round down to square grids, as in the released source.

| Requested cells | Actual cells | Native observations | Initial fields compared |
| ---: | ---: | ---: | ---: |
| 500 | 484 | 48,884 | 3,872 |
| 1,000 | 961 | 97,061 | 7,688 |
| 2,000 | 1,936 | 195,536 | 15,488 |
| 4,000 | 3,969 | 400,869 | 31,752 |
| 8,000 | 7,921 | 800,021 | 63,368 |
| 16,000 | 15,876 | 1,603,476 | 127,008 |
| 32,000 | 31,684 | 3,200,084 | 253,472 |
| 64,000 | 63,504 | 6,413,904 | 508,032 |
| 128,000 | 127,449 | 12,872,349 | 1,019,592 |
| 256,000 | 255,025 | 25,757,525 | 2,040,200 |
| 512,000 | 511,225 | 51,633,725 | 4,089,800 |
| 1,024,000 | 1,022,121 | 103,234,221 | 8,176,968 |

The new conditions contain 206,257,655 native agent observations in 1,212 complete XML snapshots.
Independent initialization reconstructs all 16,337,240 fields exactly.
Including one native 250-cell qualification run gives 206,280,380 observations and 16,339,040 initial fields.
Repeat and diagnostic-control executions are not counted as additional published size conditions.

Every snapshot is checked for iteration sequence, fixed unique positions, fixed resource capacity,
resource bounds, valid state range, and finite target coordinates.
These checks do not independently validate every native transition.
The earlier message-order nondeterminism and ordered transition control remain documented in `../gpu-condition`.

The run uses the same pinned historical FLAME GPU 1 source and build-only CUDA include override
as qualification, on an H100 with CUDA 11.8 and GCC 11.4.
No model or engine source correction was applied.
A separate archive readback verifies all 12 generated model-source hashes against the generation plan and local originals.
Every retained native run log reports exit status zero; sources and build/run logs are included in `native-source-readback/`.
Each condition had a 600-second limit; the producer exited zero under its 3,600-second cap.
The default per-step XML output remained enabled.
This is not a historical Titan Xp timing reproduction or a controlled repeated performance comparison.
The million-cell, thousand-step distributed benchmark and exact source-line count also remain incomplete.

The 12 raw archives total 2,078,262,877 bytes and retain generated code, build/run logs, and all native XML snapshots.
Each archive was exported to durable storage and downloaded with its checksum verified before audit.
`summary.json` records object locations, sizes, and SHA-256 values; per-condition export receipts confirm completion.
Raw archives require authorized access to the recorded evidence bucket and are not duplicated in Git.
The owned GPU node was stopped after export; the raw local copies are retained too.

Run `python replications/openabl_2021/audit_gpu_archive.py ARCHIVE REQUESTED_CELLS NEW_OUTPUT` to repeat the streaming audit.
This portable entry point locates its sibling initializer. Its complete 500-requested-cell workflow reproduces the recorded audit reports exactly.
The frozen `audit_archive.py` retains the original execution path for provenance.
`plan.json` pins generation commands and generated model hashes; `run.sh` retains the exact native execution procedure.
Per-condition audit and initialization reports are preserved, along with the terminal producer response.
This deposit adds no whole-paper completion credit.
