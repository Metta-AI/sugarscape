# Complete held-out frontier transfer

All eighteen search groups complete 28,800 native full-model evaluations: 144 final policies, each evaluated on the same 200 held-out seeds. These seeds are disjoint from optimization seeds. No final policy was discarded to improve agreement.

Fresh archive replay reproduces the original audit byte-for-byte. Independent R recomputes 57,600 native objective values, all policy means and standard errors, and all 144 empirical dominance decisions. The final plot was visually reviewed. Layout corrections preserve every CSV data row byte-for-byte.

| Source width | Final policies | Dominated by a same-seed full-model search policy |
| --- | --- | --- |
| 50 | 23 | 4 |
| 40 | 24 | 7 |
| 30 | 30 | 21 |
| 20 | 21 | 14 |
| 10 | 33 | 26 |
| 5 | 13 | 13 |

Dominance uses held-out mean revenue and mortality. Counts describe this finite policy set; they do not establish statistical superiority or global optimality. Some full-model policies become dominated after evaluation on new seeds, demonstrating search-sample uncertainty.

All thirteen width-five policies are empirically dominated. Width-forty policies are dominated in seven of twenty-four cases. This supports examining reduction severity, but does not identify the historical Figure 11 frontiers. Optimizer population, generations, random streams, and unresolved model conventions remain declared reconstructions.

The 2,238,893-byte native archive and all 134 members pass fresh storage verification. The archive contains complete requests, native outputs, terminal records, plans, and source audit receipts. `report/held-out-transfer.pdf` and its CSV retain all policies.

Replaying `audit_frontier_transfer.py` also requires the pinned source search/model artifacts referenced in its plan. The archive alone is not a standalone recovered author implementation. Search evidence is retained in `../searches-complete-2026-10-20` and the linked native archive. `report.R` accepts the extracted transfer directory, transfer audit, and a new output directory.

Timing and held-out evaluation are now complete. Final requirement-by-requirement method assessment remains outstanding; no study-completion or validated-negative verdict is added here.
