# Fixed-society ensemble and equilibration audit

This experiment was specified after the seed-zero operational pilots, before inspecting seeds 1–100.
It does not resolve undocumented author-code choices and is not a replacement for the evolutionary scenarios.

Run 100 new seeds (integers 1 through 100) for each of low fertility and birth cost.
Retain the pilot implementation and all model parameters. Run each simulation to 100,000 cycles or extinction.
Use the same seed set across scenarios, retaining every run, including extinction and execution failure.
The runner records the binary hash, exact commands, trajectory hashes, and successful process completion.
A successful process is subsequently subject to trajectory and metric validation; its completion record is not a scientific verdict.

Analyze population, wealth, mean age, and Gini at the retained 100-cycle observations.
For each seed, compute separate time averages for cycles (50,000,75,000] and (75,000,100,000].
Report the distribution of within-seed changes between windows and the across-seed mean, standard deviation, and 95% confidence interval for each window.
Keep time observations within a seed grouped; do not treat them as independent replicates.
Report terminal outcomes separately. Do not drop runs for lying outside the paper's values.

Compare the resulting descriptive estimates with Table 1 without interpreting its unexplained percentages as confidence intervals or acceptance margins.
A remaining trend or disagreement requires investigating equilibration and implementation choices, not changing the window to obtain agreement.
The full study also requires growth-rate fitting, age/wealth distributions and founder trajectories, evolutionary cases, and Figure 1–4/Appendix B comparisons.

```sh
python replications/stevenson_2021/run_ensemble.py /absolute/tools/stevenson-simulate low-fertility /new/low-fertility
python replications/stevenson_2021/run_ensemble.py /absolute/tools/stevenson-simulate birth-cost /new/birth-cost
```

## Analysis command

```sh
python replications/stevenson_2021/analyze_ensemble.py /completed/ensemble /new/analysis
```

The command requires exactly 100 ordered completion records and 100 trajectory files.
It checks recorded commands, hashes, complete sampling schedules, finite metrics, population bounds, and terminal states.
Confidence intervals use Student's t with 99 degrees of freedom, applied to the 100 seed-level averages or paired changes.
If a society becomes extinct, the analysis reports its seed and terminal outcome and withholds aggregate window statistics.
It does not silently replace undefined mean age/Gini with zero or exclude the extinct society from the population studied.

The incomplete live ensemble was rejected by the 100-run completion check, with no analysis directory created.
Both complete 100-seed ensembles subsequently passed this analysis, with no extinct seeds.
Their complete observations and descriptive comparisons are retained in the study results.
