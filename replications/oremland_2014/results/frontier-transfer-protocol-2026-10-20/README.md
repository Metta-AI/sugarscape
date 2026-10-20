# Frozen frontier-transfer campaign

Status: running, with no new completed-study credit.

The campaign covers every published grid width: 50, 40, 30, 20, 10, and 5.
Three optimizer seeds each run 24 candidates for 20 evaluated generations, using 50 simulator seeds per candidate.
This plans 18 searches and 432,000 native simulations. Two local workers run at a time.
Each search has a 3600-second limit; new waves stop after 14400 seconds. Each native generation also has a 600-second limit.
A failed wave is retained and stops subsequent admission; no automatic retries occur.

The search budget is a declared reconstruction choice because the paper provides no numeric budget.
All model and landscape hashes reproduce the earlier reduction qualification exactly.
The frozen primary convention uses area-scaled population, pixel-center resampling, nearest vision rounding, and preserved original vision classes.
It follows prose death at nonpositive wealth, tax phase 0, and the unclipped payment formula.
Algorithm choices match the qualified dominance-all / Hamming-radius .25 implementation.
Prior sensitivities remain separate; these settings are not selected to match published outcomes.

After all searches complete, every final nondominated policy will be evaluated on the full-size model using seeds 10000–10199.
These seeds are disjoint from optimizer evaluations. The full-size search frontiers undergo the same reevaluation.
Comparisons retain optimizer-seed groups and source widths. Report means, standard errors, and dominated-policy fractions.
The finite searched frontier is not the true global frontier.
No curve is assigned the paper’s κ labels, whose corresponding grid widths are unspecified in the text.

The plan, exact controller, runtime manifests, model hashes, and search protocols were frozen before examining results.
`started.json` records launch provenance, not proof of continued execution or completion.
Run records and independent optimizer audits are required before interpreting any frontier.

```sh
python run_frontier_campaign.py /path/to/frozen/plan.json
```

A new location requires updating and verifying manifest paths before launch. Existing output directories are never reused.
