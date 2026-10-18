# Recovered migration preset qualification

The [Leicester guide preserved by Duke](https://courses.cs.duke.edu/spring25/compsci308/assign/02_simulation/Sugarscape_Leicester.pdf)
attributes the NetLogo translation to Iain Weaver. Its visible archive date is
March 3, 2016. Page 4 specifies migration growback every two ticks, a corner
cluster, and maximum vision ten. It describes diagonal migration qualitatively;
it supplies no seed, observation horizon, or quantitative wave criterion.
This guide strengthens provenance but does not authenticate the 2009 implementation.

The recovered [2017 candidate](https://gist.github.com/rht/65c3f0819e92ed9d8419429a12718d07)
also grows one sugar unit every two ticks. Its actual preset differs from Haskell:

| Setting | Candidate preset2 | Haskell migration |
| --- | ---: | ---: |
| Initial population | 400 | 300 |
| Metabolism range | 0–4 | 1–4 |
| Corner square side | 23 | 20 |
| Sugar growback | 1 every 2 ticks | 0.5 every tick |
| Vision range | 1–10 | 1–10 |

Equal average growback does not imply equal resource availability at each decision.
The guide's general metabolism description starts at one, whereas this candidate
preset permits zero. Neither source is silently substituted for the other.
These differences prevent attributing cross-model outcomes to one mechanism.

Three native runs use NetLogo 4.0.4, Java 11, seed 602352629, and 1,000 steps.
The first runs the unchanged candidate with population-only observation.
The second adds the previously qualified random-state-isolated reporters.
Every population value agrees across all 1,001 frames.
The third changes only maximum vision to 15 before setup; it is our diagnostic.

| Observed case | Initial population | Final population | Agent observations |
| --- | ---: | ---: | ---: |
| Native preset2 | 400 | 217 | 219,694 |
| Maximum vision 15 | 400 | 234 | 236,491 |

Both initial populations contain 91 zero-metabolism agents.
The complete audit checks unique identities and occupied coordinates, survivor
identity subsets, finite states, age, parameter bounds, initial cluster bounds,
and individual resource sums against reported totals. It retains diagonal
population profiles every ten steps without fitting a wave criterion.
All executions exit zero. Extracted archive readback reproduces the audit exactly.

`source-audit.json` pins source provenance and configuration differences.
`native-evidence.tar.gz` retains the frozen protocol, runner, external experiment
XML, commands, receipts, complete native trajectories, and auditor.
The candidate, observer, and runtime hashes refer to the already retained inputs
documented in the preceding candidate-runtime and isolated-observer studies.
After extraction, run `python audit.py EXTRACTED_DIRECTORY NEW_AUDIT.json`.

This is two unique model inputs plus one observer control, not three ensemble
samples. It establishes neither historical random-stream equivalence nor a
published migration-wave result. Migration and pollution replication remain open.
