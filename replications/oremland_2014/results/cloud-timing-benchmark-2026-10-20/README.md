# Native timing benchmark

All 18,639 native inputs complete: 600 warmups and 18,039 measured runs. Each published batch count runs three times. A fresh local audit equals the native-host audit exactly. Fresh storage readback verifies the archive and all 28 members.

Median batch times in seconds:

| Width | Runs per batch | Setup | Simulation | Whole instrumented interval |
| --- | --- | --- | --- | --- |
| 50 | 50 | 0.5124 | 1.8273 | 2.6638 |
| 40 | 88 | 0.5312 | 1.7288 | 2.6734 |
| 30 | 173 | 0.6432 | 1.8718 | 3.1848 |
| 20 | 427 | 0.9431 | 1.9268 | 4.1758 |
| 10 | 1375 | 1.2070 | 1.9088 | 5.6812 |
| 5 | 3900 | 2.1800 | 2.7325 | 10.6657 |

Timing uses one pinned logical CPU, AMD EPYC 9R45, Temurin Java 11.0.32.1, and NetLogo 5.3.1. Host contention is not excluded. The paper's historical hardware and timing scope are not recovered. These measurements do not establish agreement with historical seconds or isolate algorithmic speedup.

Setup and simulation retain native command compilation/dispatch. Simulation timing excludes final reporters and output serialization; the whole interval includes additional recorder work. The width-five batch therefore illustrates sensitivity to timing scope. Three batches describe this execution; they are not independent machine replications.

The frozen policy, seeds, order, warmups, and batch sizes are unchanged from the qualified protocol. Equivalent-count fields are throughput estimates, not additional native runs. Held-out transfer and final study synthesis remain incomplete.

To repeat the complete audit, decompress the retained JSONL files beside their gzip copies, then run:

```sh
python audit_benchmark.py benchmark repeated-audit.json
```

The native archive SHA-256 is `7a3c443608eee113b6f70146d804050939382b2714352f9a2508e8a3a91447d4`. Runtime, model, and reference pins are retained in the preceding cloud qualification evidence. Compute was stopped after verified export; billing reconciliation remains external to the research evidence.
