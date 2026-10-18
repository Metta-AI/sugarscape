# Native Figure 11 D-F comparison

The three views reconstruct the initial environment and iterations one and fifty
from the complete native seed-zero capture. The existing transition audit remains byte-identical.
Initial capacities and active-cell resource states come from native-matching records;
empty-cell resource states are reconstructed from source accounting and observed destinations.
This is a scientific state rendering, not an OpenGL renderer reproduction.

All three author images use the same fixed 256×256 cell-center grid, original orientation,
normalized RGB, and the source's five Viridis classes plus its red minus-one sentinel.
No crop, seed, palette, orientation or acceptance threshold was fitted.
Iteration zero maps to the initial capture; iterations one and fifty map to steps zero and forty-nine.

| Iteration | Matching color classes / 65,536 | Author red cells | Native red cells | Shared red coordinates |
| --- | ---: | ---: | ---: | ---: |
| Initial | 13,579 | 0 | 0 | 0 |
| 1 | 14,295 | 8,885 | 11,264 | 1,557 |
| 50 | 16,454 | 8,869 | 8,793 | 1,189 |

The native initial landscape matches the earlier GNU extraction, not the released illustration.
The earlier Clang/libc++ extraction matched all 65,536 initial image classes,
but that observation does not authenticate the historical compiler or subsequent state sequence.
The existing numerical benchmark was not changed to fit these illustrations.

Red is the original environment-sugar sentinel, not an independently defined agent-count metric.
The first-step red-count difference cannot by itself establish a mortality difference.
The caption names iterations one and fifty; the historical image execution and source provenance remain unresolved.
These image differences are documented observations, not a completed negative paper verdict.

Reproduce the native snapshots with the full transition audit, which now also writes
`NEW_REPORT.snapshots.json.gz`, then compare against the pinned benchmark repository's
`sample/figures/visualisation` directory:

```sh
python replications/richmond_2023/audit_state_transitions.py HOST/state.csv NATIVE/run/state.csv NEW_REPORT.json
python replications/richmond_2023/compare_native_images.py NEW_REPORT.snapshots.json.gz AUTHOR_IMAGES NEW_OUTPUT
```

The complete three class grids, source hashes, confusion matrices and sampling margins are retained.
The six-panel PNG was visually inspected; it labels archived versus reconstructed views explicitly.
