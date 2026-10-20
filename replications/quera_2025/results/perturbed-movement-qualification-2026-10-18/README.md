# Perturbed trajectory replay qualification

Seed 3 exercises all six parameters, three finite-difference steps (0.001, 0.01, 0.05), and both signs: 36 complete trajectories with 25 stored states each. Each case reuses the original diagnostic configuration and common random seed.

Ordinary and passively observed native executions match all six full-state component hashes in every case. All 900 perturbed aggregate wealth values match the original gradient archive exactly. Independent Python replay reconstructs 86,400 agent updates and 2,160,000 cell updates with zero maximum state error. Every realized destination maximizes the native masked score; tie-selection probabilities remain outside this replay.

The updated auditor also reproduces all 256 prior baseline per-seed results exactly, excluding only the new explicit case identifier. Missing baseline metadata files were restored from the hash-verified retained archive after the first regression invocation failed before replay. No simulation outputs were replaced.

Direct buffered gzip output preserves complete observations without storing uncompressed copies. Qualification exited zero in 30.04 seconds. Every member of the retained archive passes hash readback. A separate earlier unbuffered qualification remains retained externally as execution evidence.

The frozen continuation protocol covers seeds 4–258: 9,180 additional cases. Seed 3 is excluded to avoid duplicate scientific inputs. Native execution has one thread, a two-hour bound, and a 2 GiB free-space guard. No uncompleted continuation case is counted here.

These checks validate the reconstructed diagnostic trajectories. Exact Figure 11 settings and the paper's 5,000-epoch calibration protocol remain unresolved; there is no paper completion claim.

The earlier unbuffered qualification also exited zero. All 144 compressed CSVs and the complete passive-parity table match the buffered run byte-for-byte.

The new compressed baseline mode also completes and independently replays seed 3 with zero state error. All four decompressed CSVs equal the original uncompressed seed-3 evidence byte-for-byte. Its complete archive passes readback.
