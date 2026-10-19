# The Need for Greed in Artificial Decisionmakers

Status: partial native reproduction. This study has 164 freshly audited inputs and 815,329 observations. One population median agrees graphically with Figure 2; the full tables and figures remain incomplete.

Kremer-Herman and Gupta, IEEE ISTAS 2024, pages 182–190. [Author manuscript](https://digital-terraria-lab.github.io/assets/papers/kremer-herman:2024:need-for-greed.pdf).
The paper explicitly names [author release v2024.1](https://github.com/digital-terraria-lab/sugarscape/tree/b9ca671ab7591c7b3606f2d76c33eda344d626d1). Its source is MIT-licensed; source and dataset hashes appear in `source-audit.json`.

The deposited protocol includes 400 baseline inputs and 10,100 sweep inputs: 101 selfishness levels, 100 original seeds each, and 5,000 steps. These configurations are byte-identical subsets of the Blueprints datasets. Reuse requires matching configurations, source manifests, and raw trajectories; matching names alone is insufficient.

## Audited evidence

- [Baseline reuse](results/baseline-reuse-2026-10-19): 64 Bentham baseline inputs, 320,064 observations. Another 336 baseline raw checks remain.
- [Selfishness 0.37](results/selfishness037-reuse-2026-10-19): all 100 deposited seeds, 495,265 observations, one extinction and 99 populations above the initial 250. No final population equals the initial population. Another 10,000 sweep inputs remain unaudited here.

Baseline and sweep configurations remain separate. Baseline selfishness endpoints are not substituted for sweep endpoints. Reused PyPy trajectories inherit the Blueprints runtime qualifications; this audit adds configuration and artifact verification, not an independent engine implementation.

The 0.37 cohort’s median per-run population mean is 1,151.480303939 including the initial row, or 1,151.6606 excluding it. Zero extension after extinction leaves both medians unchanged. [Direct Figure 2 vector extraction](results/figure2-population-2026-10-19) places both medians within the plotted stroke at selfishness 0.37. All four averaging conventions agree graphically; historical averaging remains unresolved.

Table IV combines levels 0.36–0.40, requiring 500 inputs. This single level does not reproduce that row. The paper classifies equality with the initial population as worse; the released plot classifies equality as better. Both remain distinguishable in retained endpoint counts.

## Repeat the fresh artifact audit

The verifier consumes the retained Need for Greed ZIP and Blueprints study artifacts. These are explicitly recorded dependencies, not downloaded or generated silently.

```sh
python replications/need_for_greed_2024/results/selfishness037-reuse-2026-10-19/verify.py /path/to/workspace /new/audit.json
```

The workspace must contain `sugarscape-blueprints` at its recorded evidence paths and `sugarscape-replication-evidence/papers/need-for-greed.zip`. The output must not exist. Every source archive, manifest, configuration and raw trajectory is checked before producing the report. The two full readbacks match byte-for-byte; independent NumPy arithmetic checks four medians and endpoint counts.

The first auditor attempt compared a nested hash mapping with its enclosing document. It failed before reporting results. The corrected schema access, original script, and failure receipt are preserved; no simulation was rerun or excluded.

[Native endpoint controls](results/endpoint-qualification-launch-2026-10-19) now test whether baseline configurations reproduce sweep endpoints. The selected selfishness-zero pair matches all 137 observations byte-for-byte through extinction. The 0.5 and 1.0 pairs remain pending; existing coverage totals are unchanged.

## Remaining work

Recover and freshly verify the remaining 336 baseline trajectories; execute or reuse all 10,000 remaining sweep inputs. Reproduce Tables I–IV and Figures 2–6 with declared aggregation and denominator conventions. Investigate discrepancies against the released code and original protocol before assigning a negative replication result.

Historical boxplot aggregation remains unresolved. The paper’s printed Table IV row 0.81–0.85 sums to 100.2%; the source audit preserves it without correction. Full paper completion requires the complete declared experiment and qualified comparisons, not this subset.
