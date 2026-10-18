# Long-run evolution qualification and initial checkpoint

The frozen experiment extends both existing conditional evolutionary scenarios to 100,000 cycles, with the same 100 seeds per scenario.
It retains the existing 830-agent initialization, trait distributions, inheritance and model dynamics.
The chaotic case's initial population and both scenarios' inheritance conventions remain reconstruction assumptions.

`build_long_evolution.py` changes observation exports only: omit per-birth rows and sample joint trait counts with the existing 100-cycle aggregate schedule.
Every-cycle native conservation and population-balance checks remain unchanged.
Initial traits remain recorded. Full 500-cycle inheritance ledgers remain available from the earlier experiments.

Both scenarios passed complete 5,000-cycle seed-zero qualification against the dense observer.
Aggregate and individual exports are byte-identical, and every retained joint-trait observation matches.
The source patch and both compiled executables are archived.

The first four long runs complete 100,000 cycles each, with 4,004 recorded aggregate observations in this snapshot.
Each agrees with its earlier 500-cycle ensemble at all six shared sample times; native accounting and sampled trait/population totals pass.
This checkpoint is partial evidence: the full experiment requires 200 completed audited runs before across-seed comparisons.

Four workers have a one-hour execution bound and a 300-second per-run bound.
All outcomes, including failures and extinction, are retained. The observer avoids exporting millions of redundant birth events during the extended horizon.
The native archive passes member-by-member SHA-256 readback.

Declared descriptive windows are cycles 35,100–50,000 and 75,100–100,000 at 100-cycle intervals.
Compute each seed's time average first, then across-seed means, standard deviations and 95% confidence intervals.
Treat extinction explicitly; do not drop extinct societies or fill undefined age/Gini with zero.
These windows do not establish the paper's sampling procedure, equilibrium, or a replication verdict.

```sh
python run_long_evolution.py /path/to/new-output /path/to/completed-stable-500 /path/to/completed-chaotic-500
```

The runner verifies the retained reference manifests before native qualification and requires exact model-source identity.
