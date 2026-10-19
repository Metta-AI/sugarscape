# Complete prospective seed extension

All 512 native and 512 independent runs at seeds 64–575 finish successfully.
All 513,024 observations pass the trajectory audit; no runs are excluded.
The prior exploratory seeds 0–63 are not pooled into these comparisons.
The model rules, original parameter setting and 501-observation horizons remain unchanged.

| Predeclared event | Native | Independent | Two-sided Fisher p |
| --- | ---: | ---: | ---: |
| Price >=10 at both observations 475 and 500 | 0/512 | 0/512 | 1 |
| Final population <50 | 14/512 | 9/512 | 0.399477 |

The largest empirical cumulative-distribution difference across six metrics is 0.060546875, for mean price.
The shared-label permutation comparison gives joint p=0.83465 over 19,999 permutations.
Final-population medians are 488.5 and 500; minimum-population medians are both 11.
Price-at-475 medians are 1.024272 and 1.025965.
These results provide no evidence here for a broad distribution shift, but do not establish equivalence.
Zero persistent-price events cannot establish equal rates for such rare trajectories.
Neither historical estimator discrepancies nor fidelity across the full parameter space is resolved.
No completed-paper credit is added.

The launcher exited zero after all 513 commands succeeded, within its one-hour wall and 200 MiB bounds.
The 13,134,573-byte archive retains 2,060 files, including raw trajectories, logs, parameter files, source, compiled driver, protocol and receipts.
Every archived member matches its original bytes and recorded hash.
A fresh extraction reruns the complete audit and comparison, reproducing all outputs byte-for-byte.
Independent R calculations reproduce all six distribution statistics exactly and both rare-event counts and Fisher p-values within 1e-12.
`readback.json` and `validation.json` retain these checks; original evidence remains intact.
