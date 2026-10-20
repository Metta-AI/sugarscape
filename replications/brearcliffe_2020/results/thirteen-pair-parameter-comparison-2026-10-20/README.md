# Thirteen paired cohorts

Both frozen parameter interpretations now have complete matched evidence for thirteen pairings: 650 matched inputs and 1,300 trajectories. No simulations were added for this comparison.

Independent R verifies 50,388 curve-pair classifications and 182 endpoint comparisons. There are 135 endpoint overlaps under both settings, eight only under paper settings, two only under released settings, eighteen under neither, and nineteen unresolved. Raster overlap is descriptive, not statistical equivalence.

The new SARSA / Rule M pairing has fourteen overlaps under both interpretations. All earlier twelve-pair records and source hashes remain exact. Repeated analysis is byte-identical. Neither interpretation is selected by these results.

Run `analyze.py RESULTS NEW_REPORT` followed by `Rscript --vanilla verify.R RESULTS NEW_REPORT NEW_VALIDATION`, where RESULTS is the study's results directory. Full native cohort audits and storage evidence remain linked from the study README.

The remaining three paper-table cohorts and full claim synthesis are incomplete. This adds no completed-study credit.
