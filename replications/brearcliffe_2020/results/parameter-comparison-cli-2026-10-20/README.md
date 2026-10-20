# Complete-cohort comparison command

The reusable comparison command defaults to all sixteen ordered pairings. It requires both complete fifty-run interpretations and the same corrected paper targets for every requested pairing. Missing cohorts fail without producing a partial report.

The real thirteen-pair workflow reproduces every prior data field exactly; only scope wording changes. Independent R verifies 50,388 curve pairs and 182 endpoints. A default sixteen-pair invocation fails on the still-missing paper-table SARSA/EC cohort and creates no report. This exercises actual evidence paths, not mocked inputs.

From the study directory, once all sixteen cohorts are published:

```sh
python compare_parameter_interpretations.py results /path/to/new-comparison.json
Rscript --vanilla verify_parameter_interpretations.R results /path/to/new-comparison.json /path/to/new-verification.json
```

An explicitly requested complete prefix can be assessed with `--pairs 13`; this does not claim sixteen-pair completion. The command never chooses a smaller prefix automatically.

No new simulations or completed-study credit are added. Current results remain in the thirteen-pair comparison evidence.
