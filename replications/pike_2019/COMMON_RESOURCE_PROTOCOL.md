# Native common-resource ensemble

Scope: the paper’s complete Figure 3-9 threshold-10 comparison, 100 seeds each for the released one-level and multi-level common-resource models, 1,000 steps and 200 initial agents. This is one part of the full paper; lower-threshold comparisons (including five trades), movement-policy grids, timing comparisons, and historical version alignment remain required.

Reuse the preserved seed-zero native pilots `pike-common-one-pilot-001` and `pike-common-multi-fixed-observed-001`. Both retain complete observations, health, prices, source manifests, and successful terminal receipts. Their passive observation was separately validated. No corrected shared-pool implementation is included. Run seeds 1–99 sequentially, one-level then multi-level, for 198 new conditions. A later complete analysis must reconcile both historical pilots and all new runs without duplicate seeds.

Use the pinned author engine `585e53398f4f58e89ec184c83bb20819f0e4c96a`, library `99d2091721076df9fff32e8b49a0e33e98c34a6f`, Python 3.11.14, Mesa 0.8.5, NumPy 1.26.4, NetworkX 3.6.1, PYTHONHASHSEED=0, NumPy/module-level seed equal to the condition seed, and Mesa seed 42. Keep the released threshold 10, policy, activation, and resource behavior unchanged. Exact historical NumPy states and paper source pair are unavailable.

Retain all raw health values, including infinite holdings, and all native population reporters. Reconcile actual individual identities separately from reporter counts of resources/groups. Record each native process exit and every completed output hash. Stop on process failure, six-hour outer limit, or less than 8 GiB free space. Do not replace failed seeds, cap resources, impute undefined prices, or delete evidence.

The published common-resource survivor means are 94.35 (one-level) and 92.83 (multi-level). Compare only after the complete grid is audited. Report 95% intervals using runs as units and paired differences by seed. Audit price aggregation and reproduce the source notebook’s doubled p-values separately from valid two-sided statistics. Nonsignificance does not establish equivalence.

Numerical validity is an independent requirement: report the first nonfinite holding, affected records and seeds, negative holdings, and independently reconstructed price metrics. Invalid economics cannot become a passing replication just because the process exits successfully or survivor means are close. Preserve source-fidelity limitations and investigate the known stale-contribution reaggregation mechanism before any paper-level verdict. Corrective/sensitivity runs never replace native results.

## Provenance correction before full-grid analysis

Inspection after launching seeds 1–99 found that the old one-level seed-zero manifest lacks PYTHONHASHSEED, while the multi-level fixed-observed manifest explicitly records zero. Preserve the old one-level pilot and the already-frozen production protocol. A single separately recorded one-level seed-zero replay now uses the immutable production `run.py` and explicitly records PYTHONHASHSEED=0, with a ten-minute cap. Use this new replay for full-grid reconciliation after its outputs pass audit; compare the old pilot but do not count it twice. This correction changes no active production seed or model rule.
