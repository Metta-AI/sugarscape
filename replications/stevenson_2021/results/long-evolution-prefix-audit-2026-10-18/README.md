# Independent long-run prefix audit

The independent analyzer validates the first 52 complete long runs (26 seeds in each scenario), covering 52,052 recorded observations.
It checks producer hashes, exact command parameters, complete sampling schedules, finite and bounded metrics, native conservation outputs, initial trait identities, joint-trait counts and terminal outcomes.
All native files for these 52 runs and the required model/source metadata are retained. Archive member hashes pass readback.
The previous four-run qualification snapshot is included in these 52; it is not additional evidence coverage.

Per-seed time averages use the frozen windows, cycles 35,100–50,000 and 75,100–100,000.
This prefix mode deliberately emits no across-seed statistics. The ensemble requires 100 seeds for each scenario.
A full-mode invocation on incomplete evidence fails before creating output; the exact command and failure are retained.

After all 200 runs complete, full mode reports means, sample standard deviations and Student-t 95% intervals across the 100 seed averages.
It also reports paired window changes. Time observations are not treated as independent replicates.
Any extinct society causes that scenario's aggregate statistics to be withheld; its terminal outcome remains retained.
Neither window agreement nor numerical closeness establishes the original sampling convention or a paper verdict.

```sh
python analyze_long_evolution.py /path/to/experiment /path/to/new-prefix-audit --completed-prefix
# Requires all 200 runs and the terminal completion record:
python analyze_long_evolution.py /path/to/experiment /path/to/new-complete-analysis
```
