# Brearcliffe and Crooks: Creating Intelligent Agents

Study status: native recorder corrected and qualified across 20,000 ticks. No reproduced-paper result yet.

Paper: [Creating Intelligent Agents: Combining Agent-Based Modeling with Machine Learning](https://doi.org/10.1007/978-3-030-83418-0_3).
The [author-deposited release](https://www.comses.net/codebases/ffb52fc3-69e1-4bbd-b5d7-fa460617f74e/releases/1.0.0/) includes the NetLogo model, symmetric map, and ODD description.
`source-audit.json` pins the downloaded artifacts and author manuscript. Preserve their original license notices.
The model header states CC-BY-NC-SA 3.0; release metadata states 4.0. This study does not relabel or relicense those sources.

The paper compares 16 ordered method pairings, 50 runs each, through ticks 0–20,000.
Seven per-breed statistics feed Figures 3–9. The original population slider is 400 per breed, yielding 800 initial agents.
The released experiment specifies only five repetitions and calls `random-seed new-seed`; it does not record historical seeds.
The manuscript states learning rate 0.8 and discount rate 0.9; the source sets learning rate 0.9 and gamma 0.8.
Keep the released-code interpretation separate from a prose-parameter sensitivity experiment; neither resolves historical settings by itself.

## Native pilot

The [launch record](results/native-pilot-launch-2026-10-19) selects Rule M versus evolutionary computing, with combat, corner starts, replacement, and growback 1.
This pairing does not use the disputed reinforcement-learning hyperparameters.
A separate retained model copy replaces only `random-seed new-seed` with `random-seed 20261019`.
The original source remains unchanged. This fixed seed is prospective, not a recovered author seed.

`Replay.java` uses NetLogo 6.1.1 and its original bundled matrix extension.
It records initial state and every subsequent tick, with both populations and all fourteen figure statistics.
A complete run must contain 20,001 finite observations with consecutive tick values.
The pilot has a 600-second wall limit, 1 GiB Java heap, and 50 MiB output cap. Partial outputs remain evidence, without completion credit.
The first full pilot completed but failed recorder qualification. The [retained discrepancy and correction](results/recorder-qualification-2026-10-19) show exact short-run agreement after isolating measurement randomness. The [full-horizon comparison](results/full-recorder-qualification-2026-10-19) now agrees exactly on all 320,016 values across 20,001 observations.

Compile against the NetLogo application JARs, then run:

```sh
java -Xmx1g -Djava.awt.headless=true -cp 'DRIVER_DIRECTORY:NETLOGO/app/*' \
  Replay /absolute/seeded-model.nlogo 'Rule M' EC 20000 /new/trajectory.csv
```

Place the original symmetric map and the NetLogo 6.1.1 matrix extension beside the retained model copy.
The external bounded launcher and exact command are retained in the launch record.

The [all-pairing qualification](results/all-pairings-launch-2026-10-19) is now running for 1,000 ticks per pairing with fixed bounds. Full paper ensembles have not started.

The [full learning-method comparison](results/rl-full-qualification-launch-2026-10-19) now runs Q-Learning versus SARSA for 20,000 ticks.
The [frozen ensemble preparation](results/ensemble-preparation-2026-10-19) defines 800 runs for each parameter interpretation, with matched prospective seeds. Both preparations reproduce identical bytes; execution has not started.

## Remaining work

Qualify the remaining method pairings and estimate their runtime before the full 800-run ensemble. The measured Rule M/EC pairing projects to about 49 CPU-hours for 800 runs; this is not a measured full-sweep estimate.
Resolve the released-code/prose parameter interpretations without silently changing the primary experiment.
Implement the study behavior in the fork, qualify it against the native model, and compare every published figure using full repeated ensembles.
Do not count a pilot, source audit, or five-repeat released sweep as a completed paper replication.
