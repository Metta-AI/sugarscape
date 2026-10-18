# Complete native benchmark

The unchanged 84-condition benchmark exited zero on H100, CUDA 11.8, GCC 11.4.
All 6,600 population records match the pinned V100 author archive exactly.
All 162 resolution rows are byte-identical to the author archive.
The independent aggregate audit reconciles all 132 population and timing means.
Timing agreement is not claimed across different GPUs and toolchains.

`native.tar.gz` retains the full receipt, protocol, compiler/GPU information and raw CSVs.
Run `audit_native.py EXTRACTED_NATIVE NEW_AUDIT_DIRECTORY` from the study directory.
Compare each native per-step CSV against the same filename in the pinned author's
`sample/data/v100-515.65.01/2.0.0-rc-v100-11.0-beltsoff` directory, excluding only `s_step`.
Compare `resolution_steps.csv` byte-for-byte. Input hashes are in `comparison.json`.
The original counter lifecycle and bin labeling are preserved.

The separate passive observer finished successfully, but its initial-state audit failed:
the native initial population is 11,264; the macOS GCC 16.2 host reference has 11,025.
Native compilation used Linux GCC 11.4. Initializer equivalence remains under investigation.
The failed audit and complete observer capture are retained externally.
No completed-paper credit is assigned until the remaining model and figure checks finish.
