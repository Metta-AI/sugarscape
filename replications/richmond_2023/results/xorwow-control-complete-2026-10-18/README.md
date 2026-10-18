# Completed native XORWOW control

The exact Philox baseline replay gate passes. The native variant exits zero, and recorded compiler flags confirm XORWOW throughout the build. The model, observer, seed, initial state and 100-step horizon remain fixed.

The full state-accounting audit passes **889,233 post-step agent observations**, **619,271 movements**, and **2,302 deaths**. Only the two immutable input hashes change in the auditor. Observed destinations remain inputs; random choices and conflict winners are not independently reconstructed.

The unchanged grid, palette and orientation comparison yields:

| Illustration | Matching cell classes / 65,536 | Author red cells | Native red cells | Shared red coordinates |
| --- | ---: | ---: | ---: | ---: |
| 0 | 65,536 | 0 | 0 | 0 |
| 1 | 34,929 | 8,885 | 11,171 | 1,880 |
| 50 | 41,016 | 8,869 | 8,869 | 2,542 |

Changing RNG family alone does **not** recover the later illustrations. The iteration-50 red-cell count agrees, but occupied locations do not. This narrows the diagnostic hypothesis without establishing a negative paper replication. Historical engine behavior, visualization timing and complete random-stream provenance remain unresolved.

All archived files match the retained extraction byte-for-byte. The archive was exported before the owned H100 stop request succeeded. Figures were rendered and visually checked. Observer timings are excluded.

Reproduce with `audit_xorwow.py ORIGINAL_CLANG_INITIAL_CSV EXTRACTED/xorwow/state.csv NEW_REPORT.json`, then use the existing `compare_native_images.py` with the generated snapshots and pinned author images. The prior Clang initialization evidence supplies the initial CSV. The archive contains both complete native state captures, input JSON, build cache, compiler flags, logs and observer source.
