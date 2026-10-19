# Prospective seed extension

The retained 64+64 ensemble cannot resolve rare persistent late-price frequencies.
This extension fixes seeds 64–575 before execution: 512 new runs per engine, disjoint from seeds 0–63.
It keeps original input 675's parameters, unchanged model sources and 501 observations per trajectory.
The native parameter file includes earlier rows for index alignment; Replay executes only [64,576).

Predeclared measurements include price >=10 at both observations 475 and 500, and final population below 50.
The six continuous metrics from the exploratory diagnostic are retained.
Analyze the new cohort separately; do not treat a nonsignificant difference as equivalence.
No results are discarded and no primary estimator dataset is replaced.

The sequential local launcher has a 3,600-second wall limit and a 200 MiB output cap.
It checks at least 2 GiB free before each command and retains all failures.
A command timeout raises after stopping that child process; unfinished outputs receive no completion credit.
The unchanged native driver and frozen independent model are hash-pinned.
The launcher was observed running; this record establishes launch only, not a completed cohort or paper result.
