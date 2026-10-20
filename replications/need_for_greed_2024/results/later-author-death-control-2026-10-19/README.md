# Later author plotting control

The unmodified `findMeans` function from author release v2024.3 includes starvation, combat, and aging deaths. It divides pooled deaths by pooled population at each timestep. This differs from the paper’s stated aging exclusion and from medians of per-run means.

Executed on the 100 audited selfishness-0.37 trajectories, it gives temporal means of 1.670732% or 1.671066%, and temporal medians of 1.646138% or 1.646142%, depending on initial-row inclusion. All four lie within Figure 5’s nominal stroke around its 1.648409% centerline. These are diagnostic summaries; no historical plotting convention is selected from this overlap.

The source commit is `cc0408afbb09d8d124ce6f7e6b1844d202d0f8b6`, with file hash in `source.json` and its original MIT license retained. The paper pins v2024.1. A later source implementation is evidence for a plausible measurement explanation, not proof of the paper’s historical pipeline.

`analyze.py` verifies all 100 trajectory hashes, sums native per-timestep counts, and executes the unchanged function extracted from the pinned source. Arrays are initialized to zero after native extinction, as the author parser does. The parser itself is not executed. No trajectory is excluded and no simulation is rerun.

Independent NumPy arithmetic agrees exactly on all 5,001 output death rates. Repeating the complete raw-readback analysis gives byte-identical summaries and per-timestep CSVs. Compressed CSV readback preserves the recorded hash.

```sh
python analyze.py BLUEPRINTS_CHECKOUT COHORT_AUDIT_JSON NEW_OUTPUT_DIRECTORY
```

The primary paper-defined death discrepancy remains retained. This control adds no completed-study credit or independent-engine qualification.
