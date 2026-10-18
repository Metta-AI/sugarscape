# Complete native retry ensemble

All 90 fresh processes and eighteen conditions pass the independent raw-counter audit.
Each process uses seed 42 and 1,000 model steps; five processes cover each condition.
The audit verifies baseline source pins, the sole instrumentation-flag change,
retained executable hashes, commands, successful exits, scheduling and integer counters.
The native command completed at 2026-10-18 02:28:25 UTC.

TArray has fewer retries than TVar at every capability count; all observed ranges are disjoint.
Both normal-scenario mean ratios increase with capability count, consistent with Table 7.
The exact reported ratios do not all reproduce on this different CPU.
Five-process ranges describe these runs; they are not confidence intervals.
No new numerical acceptance threshold or whole-paper verdict is assigned.
The paper's historical repetition count remains unspecified.

| Variant | Capabilities | Agents | Mean retries/commits | Observed range | Paper |
| --- | ---: | ---: | ---: | ---: | ---: |
| tvar | 1 | 500 | 0.002525 | 0.002447–0.002578 | 0.00 |
| tvar | 2 | 500 | 1.035187 | 1.034453–1.036356 | 1.04 |
| tvar | 3 | 500 | 2.176288 | 2.173679–2.179785 | 2.15 |
| tvar | 4 | 500 | 3.340344 | 3.338715–3.342328 | 3.20 |
| tvar | 5 | 500 | 4.530320 | 4.526849–4.533757 | 4.06 |
| tvar | 6 | 500 | 5.812510 | 5.805590–5.824699 | 5.02 |
| tvar | 7 | 500 | 6.909872 | 6.902296–6.920121 | 6.09 |
| tvar | 8 | 500 | 8.194269 | 8.167232–8.215473 | 8.45 |
| tarray | 1 | 500 | 0.001287 | 0.001209–0.001381 | 0.00 |
| tarray | 2 | 500 | 0.020035 | 0.019455–0.020536 | 0.02 |
| tarray | 3 | 500 | 0.039491 | 0.038740–0.040267 | 0.04 |
| tarray | 4 | 500 | 0.056256 | 0.055371–0.057070 | 0.06 |
| tarray | 5 | 500 | 0.073362 | 0.072408–0.074513 | 0.07 |
| tarray | 6 | 500 | 0.090081 | 0.089152–0.091049 | 0.09 |
| tarray | 7 | 500 | 0.106497 | 0.104744–0.107871 | 0.10 |
| tarray | 8 | 500 | 0.121191 | 0.119124–0.122992 | 0.11 |
| tvar | 4 | 2500 | 2.802528 | 2.798403–2.804517 | 3.28 |
| tarray | 4 | 2500 | 0.012419 | 0.012300–0.012591 | 0.01 |

All ten single-capability processes print `0.00` despite positive retry counts.
The raw integers remain authoritative; printed zero does not mean zero retries.

Extract `native.tar.gz` and `provenance.tar.gz` into separate fresh directories, then run:

```sh
python replications/thaler_2019/audit_retry_scaling.py NATIVE PROVENANCE NEW_AUDIT.json
```

The uninstrumented timing experiment is separate. Its preserved SIGSEGV is unresolved.
Figure 5a provenance, the population grid, four local timing conditions,
and all Table 9 measurements remain outside this completed retry ensemble.
