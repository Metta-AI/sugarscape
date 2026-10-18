# First four complete ranking cases

This snapshot contains 172,200 complete native runs, validated through 344,400 input/output records.
The four model cases retain all 100 policies and both clock phases at their full declared simulation budgets.
Every input, output, model, policy, seed, and request identity is audited. The objective arrays pass lossless readback.

All 1,920 ranking rows are retained, including nominal 2%, 10%, and 100% budgets, floor/ceiling integer counts, both tie rules, both weights, and pooled/within-rate scopes.
Independent sorting verifies 96,000 rank values. Exact rational arithmetic verifies every one of the 1,920 kappa values.
Kappa is one minus observed rank-distance disagreement divided by expected disagreement under the empirical marginal distributions.
Rank assignment uses [SciPy's documented average and ordinal modes](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.rankdata.html), independently checked against sorted integer totals.
Linear and quadratic penalties use the actual rank spacing, including half-ranks from ties; no category compression silently changes those distances.

The table shows the declared full-budget, pooled, average-tie cases; all other choices remain in each model's CSV.

| Model | First tax after move | Deaths, linear | Deaths, quadratic | Literal revenue, linear | Literal revenue, quadratic |
| --- | ---: | ---: | ---: | ---: | ---: |
| 40-pixel_centers-nearest | 1 | 0.933 | 0.995 | 0.958 | 0.998 |
| 40-pixel_centers-nearest | 5 | 0.931 | 0.994 | 0.947 | 0.997 |
| 30-pixel_centers-nearest | 1 | 0.923 | 0.993 | 0.956 | 0.997 |
| 30-pixel_centers-nearest | 5 | 0.912 | 0.992 | 0.953 | 0.997 |
| 30-aligned_endpoints-nearest | 1 | 0.918 | 0.992 | 0.944 | 0.996 |
| 30-aligned_endpoints-nearest | 5 | 0.918 | 0.992 | 0.942 | 0.996 |
| 20-pixel_centers-nearest | 1 | 0.858 | 0.978 | 0.895 | 0.986 |
| 20-pixel_centers-nearest | 5 | 0.857 | 0.979 | 0.899 | 0.987 |

The first 40×40 result has higher concordance than the published Figure 10.
This is an unresolved reconstruction discrepancy, not a validated negative replication.
The original control distribution, random-stream design, reduction conventions, rank aggregation, weights, and uncertainty-bar construction are unavailable or ambiguous.
Common seeds across policies can alter ranking precision; a separately declared post hoc independent-stream diagnostic is queued to examine that choice.
The native model and the ranking arithmetic require separate validation: passing the latter does not prove fidelity of the former.

`native-prefix.tar.gz` includes the raw files for these four complete cases, plus shared provenance.
Its frozen protocol describes the entire planned ensemble, but pending cases are intentionally absent from this archive.
It is sufficient to rerun `audit_ranking_model.py` for these four names; it is not a complete-ensemble archive.
`analyze_ranking_model.py` also requires the completed full-size convergence evidence and uses reference seeds 1–50.

No uncertainty bars or whole-paper completion are claimed. Remaining reduced cases, independent full-size comparison, source ambiguities, optimization, and transfer remain outstanding.
