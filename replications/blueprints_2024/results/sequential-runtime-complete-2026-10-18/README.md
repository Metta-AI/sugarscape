# Complete sequential runtime controls

Eight full 5,000-step runs completed on one two-CPU allocation, in CPython / PyPy / PyPy / CPython order per condition.
The independent auditor compares each trajectory byte-for-byte with the earlier retained original-input control.
All 40,008 observations match, with every timestep present, original configuration values preserved, and zero exit status.
Both conditions use seed 158402133555746433 and the unchanged v2024.1 model.

| Selfishness | CPython mean seconds | PyPy mean seconds | Mean speedup ratio | CPython maximum RSS range, KiB | PyPy maximum RSS range, KiB |
| --- | ---: | ---: | ---: | ---: | ---: |
| 0.0 | 1,248.79 | 398.89 | 3.13 | 85,488–87,052 | 354,588–356,764 |
| 0.5 | 280.27 | 85.46 | 3.28 | 34,240–35,600 | 168,280–169,764 |

RSS is resident memory, reported by GNU time. PyPy reduces elapsed time but uses more memory in both conditions.
These are two repeats per runtime at one seed and two configurations, not a universal speedup estimate or the paper's historical timing result.
Shared infrastructure and the small repetition count limit performance inference beyond these controls.
The measured memory and elapsed times support sizing a bounded supplementary batch; they do not establish parity for every unexecuted configuration.

The comparison uses CPython 3.11.14 and PyPy 7.3.20 / Python 3.11.13.
`audit_sequential_runtime.py` checks the native archive against `results/supplement-controls-2026-10-17/native.tar.gz` without extracting either archive.
It verifies source-manifest agreement, original configuration bytes, command/runtime identity, every trajectory, terminal status, and memory reports.
The raw archive includes all configurations, commands, full trajectories, logs, versions, runner source, and recovery record.
Its external export and downloaded bytes match the receipt SHA-256.
The completed task-owned node was stopped after evidence preservation; its disk contents remain intact.

These repeat two already-completed supplementary inputs. They add zero unique inputs and do not change the 99,992-input remaining worklist or complete the paper.
