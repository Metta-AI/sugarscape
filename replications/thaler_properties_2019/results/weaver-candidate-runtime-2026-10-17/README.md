# Recovered NetLogo candidate: native execution and replay

The [2017 gist](https://gist.github.com/rht/65c3f0819e92ed9d8419429a12718d07)
points to the original NetLogo community Sugarscape URL. The
[University of Bologna catalog](https://www.cs.unibo.it/fioretti/CODE/GAS/index.html)
attributes that exact URL to Iain Weaver. The community page is currently unavailable.
The [Colgate mirror](https://math.colgate.edu/math312/sugarscape/) links its code to
Leicester, but its NetLogo 6.0.1 file contains porting changes and was not substituted.
These links support attribution; byte identity with the 2009 publication remains unverified.

The unchanged gist model runs under the official NetLogo 4.0.4 distribution, with
OpenJDK 11.0.32.1. External BehaviorSpace XML selects `preset4`, seed 602352629, and
1,000 steps. No model procedures or model-file sections are modified. The first
XML attempt lacked the required DOCTYPE and failed before producing a trajectory;
its failure is retained. Both subsequent runs exit 0 with a wall limit of 300 seconds,
512 MiB heap limit, and one active processor.

| Time | Population |
| --- | ---: |
| 0 | 400 |
| 100 | 123 |
| 500 | 111 |
| 1,000 | 104 |

Both runs contain 1,001 timestep records and 115,703 agent observations. The independent
auditor checks unique agent IDs, bounded coordinates, finite values, nonnegative
holdings, monotonic survivor IDs, and exact population/resource accounting against
individual agents. Every simulation record agrees on replay; only the timestamp
header differs. This is one unique input plus a replay, not two ensemble samples.

`provenance.json` pins the model revision/hash, runtime archive/JAR hashes, version,
Java runtime and source links. Recreate the runs with the archived commands and
external XML after placing those pinned inputs at the selected paths. The runtime is
available from [the official download server](https://downloads.netlogo.org/4.0.4/netlogo-4.0.4.tar.gz).
Restore both CSV files with `gzip -dk`, then run:

```
python audit_runtime.py first repeat NEW_AUDIT.json
```

This proves the recovered candidate executes reproducibly under the recorded runtime.
It does not establish a 100-seed result, historical Java 1.5 parity, the complete
Weaver model identity, equivalence with Haskell random streams, or paper completion.
