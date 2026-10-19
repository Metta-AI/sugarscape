# Historical full GAM replay complete

The pinned R 4.0.5, mgcv 1.8-34 and Matrix 1.3-2 replay completes all five saved folds, retaining 10,000 predictive draws per held-out observation. The remote command exits zero after 2473.581 seconds, within its 7,200-second fitting bound. No timeout or partial fold receives credit.

Fresh storage download verifies the 4,581,658-byte archive, SHA-256 `672400a2a9123f594637b2dce298590b54321a95093686bb1154c2f44dca46a0`. All 20 member hashes and all six frozen input/source members verify. The five training/testing folds are unchanged.

The saved-output auditor checks all 18,750 predictions and bounds and recomputes 125 fold/aggregate metrics. Maximum scaled metric error is 3.84e-15 against the existing 1e-12 serialization tolerance. Repeated analysis is byte-identical. All predictions/bounds differ numerically from the modern replay, while all five final random-number states match exactly.

| Parameter | Paper | Modern runtime | Historical control |
| --- | ---: | ---: | ---: |
| initial.population | 0.528 | 0.499665 | 0.546044 |
| maximum.spice.endowment | 0.328 | 0.164329 | 0.291858 |
| maximum.sugar.endowment | 0.311 | 0.347444 | 0.369776 |
| pmut | 0.328 | 0.436194 | 0.454223 |
| wealth.reproduction | -1.329 | -3.002351 | -3.287907 |

Neither environment matches any of these five printed scores. Population and spice scores move closer to the paper; sugar, mutation, and wealth scores move farther away. The primary comparison remains 38 matches and 37 unresolved discrepancies across all 75 finite Table 8 entries.

This is a controlled runtime-bundle comparison, not identification of a single causal package. R, dependencies, operating system, processor architecture and numerical libraries differ together. The author's exact environment and random states remain unknown. Earlier point-fit-only controls omit the interval draws that advance the random stream; this complete workflow is the relevant five-fold comparison.

The result establishes runtime sensitivity without resolving the paper discrepancies. It adds no completed-study or validated-negative credit. Source, fold-selection and random-stream uncertainty remain separate research questions.
