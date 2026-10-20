# Complete captured-frame timing diagnostic

Both full state-accounting workflows were rerun with every frame retained. All scientific assertions remain unchanged, and both resulting state reports match the prior reports byte-for-byte. Only snapshot retention expands from three frames to all 101 frames, including initialization.

The comparison evaluates every captured frame against each of the three author images under both RNG variants: 606 comparisons. It preserves the established grid centers, palette and orientation. All six original fixed-frame comparisons reproduce exactly.

Neither later illustration has an exact cell-class match anywhere in either trajectory. Thus a simple frame-index mismatch within these two captured 100-step runs does not recover the illustrations. The initial landscape matches only initialization.

| Variant | Author image | Best matching cell classes / 65,536 | Native iteration |
| --- | --- | ---: | ---: |
| Philox | 1 | 41,724 | 0 |
| XORWOW | 1 | 41,724 | 0 |
| Philox | 50 | 41,524 | 76 |
| XORWOW | 50 | 41,639 | 92 |

The image-1 maximum occurs before agents are drawn, demonstrating why this background-dominated aggregate is not a replication criterion. These post-hoc maxima are diagnostics only; they never replace the published iteration labels or establish agreement.

`comparison.json` retains every candidate score, not only maxima. Reproduce with `python compare_all_frames.py THIS_DIRECTORY PINNED_AUTHOR_IMAGES NEW_REPORT.json`. All-frame auditors use the initial CSV and native state files from the preceding complete control archives. Source and snapshot hashes are retained in `verification.json`.

Historical engine differences, visualization-specific behavior, and random-stream provenance remain unresolved. No new simulation was launched and no study completion or negative-paper credit is added.
