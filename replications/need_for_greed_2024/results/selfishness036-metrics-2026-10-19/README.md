# Complete selfishness-0.36 metric comparison

All 100 deposited inputs are present, with 490,477 observations. Two runs go extinct; the other 98 finish above 250 agents.
Selection matches the frozen original-input inventory exactly. Five previously audited archives are rehashed, and every selected trajectory is checked again.
This analysis adds no simulation coverage. The full five-level Table IV row remains incomplete.

| Measurement | Replication median across declared conventions | Paper centerline at 0.36 | Within plotted stroke |
| --- | ---: | ---: | --- |
| Population | 1135.7535–1135.9307 | 1135.7648 | 4/4 |
| Mean wealth | 129.9384–130.2354 | 130.2193 | 4/4 |
| Mean remaining lifespan | 18.2046–18.2068 | 18.2048 | 4/4 |
| Mean age at death | 59.3366–59.3485 | 59.3372 | 4/4 |
| Starvation-plus-combat death percentage | 0.3384–0.3934 | 1.6615 | 0/8 |

Conventions match the prior 0.37 analysis: per-run time means, then across-seed medians, with initial-row and post-extinction alternatives retained.
The death calculation excludes aging and disease as stated in the paper. Aging-inclusive values remain separately labeled diagnostics.
Graphical agreement is not statistical equivalence or identification of the historical aggregation pipeline. Quartiles for 0.36 remain unassessed.

Independent NumPy arithmetic verifies all 2,400 primary per-run values; maximum scaled error is 3.5632e-16.
The aggregate and vector comparison repeat byte-for-byte. The two complete conditions exhibit the same four agreeing median measurements and unresolved death-rate discrepancy.
This is not a validated negative replication or a completed paper.

## Reproduce

Use the retained `sugarscape-replication-evidence` tree containing the five named sealed archives and their audit reports.
`prepare.py` records their hashes and selects the complete cohort, including only the qualified PyPy pilot copy.
Run in a fresh directory directly under that evidence tree, with the five scripts copied here. Python requires NumPy and PyMuPDF for the indicated steps.

```sh
python prepare.py
python aggregate.py .. cohort.json metrics.json
python validate_numpy.py .. cohort.json metrics.json numpy-validation.json
python compare.py ../papers/need-for-greed-author-2024.pdf metrics.json comparison.json
```

For Figure 2, `population-cohort.json` is `cohort.json` plus `population_medians`, selecting every `population/` key from `metrics.json` medians.

```sh
python extract.py ../papers/need-for-greed-author-2024.pdf population-cohort.json population-comparison.json
```

`validation.json` records frozen script and result hashes. Raw archives remain at the durable storage locations documented in the prior pilot and checkpoint reports.
