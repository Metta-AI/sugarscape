# Independent cohort arithmetic verification

The Python summarizer now retains its 20,000 whole-run bootstrap draws as compressed zero-based byte indices.
The statistics and random draw sequence are unchanged; retaining the indices makes arithmetic independently checkable.

`verify_cohort.R PREPARED AUDIT_JSON SUMMARY_DIRECTORY NEW_REPORT_JSON` reads the original 50 pinned trajectories.
It recomputes all 320,016 means and sample standard deviations using R matrix arithmetic, plus 14 endpoint summaries and percentile intervals.
It uses the saved resampling indices, so it does not independently verify the random-number generator.
The intervals remain pointwise; this check does not establish paper agreement.

Requirements: R with jsonlite and digest. Python lint and R parsing pass.
The actual incomplete cohort is rejected before output, with 36 inputs missing from the retained audited prefix.
The complete successful path and numerical comparison remain pending until all 50 inputs are audited.
