# Related author repository does not identify the paper experiment

The author's [sugarscape-rlearners repository](https://github.com/zacharyejohnson/sugarscape-rlearners/tree/18d19deb5b63b7cfcac7a94b4e49a57769e73090) was inspected at a pinned revision.
All 13 root files pass Git blob and SHA-256 verification. This repository contains explicit MIT license text.
That license finding applies to this repository; it does not resolve licensing of the separate Academics snapshot.

The main driver selects reinforcement-learning agents, 200 initial agents, 10 repeats, and 10,000 periods.
The two returned main-branch driver-history commits use four or ten repeats, with the same population and horizon.
The other branch head uses five repeats and additional mixed populations, still 200 initial agents and 10,000 periods.
All four fetched driver revisions pass blob verification and line-level protocol checks.
No tags were returned. This is a bounded source inspection, not an exhaustive search of every historical branch revision.

The complete main tree contains population files for runs 0, 1, 3, 4, 5, 6, 8 and 9.
All eight files pass blob and SHA-256 checks; all 80,000 population values are finite, nonnegative integers.
Each trace starts at 200 agents and contains 10,000 observations. Missing run identifiers are not assumed to have succeeded or failed.

The [Market Algorithm paper](https://jameslcaton.com/MarketAlgorithmAsDistributedGeneticAlgorithm-Johnson%2CCaton%2CMiljkovic%2CRayamajhee.pdf) instead specifies 2,000 initial agents, 100 repeats, and 60,000–100,000 periods.
This related implementation does not identify that experiment or resolve its missing snapshot and analysis pipeline.
No simulation, replication-study PR, or completed-paper credit is added.

Run `python verify.py EVIDENCE_DIRECTORY NEW_REPORT` with PyArrow against `sugarscape-replication-evidence/market-genetic-rlearners-001`.
The retained directory contains the pinned source, historical drivers, and eight raw Parquet files.
