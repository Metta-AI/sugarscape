# Held-out frontier transfer qualification

Nine policies from three completed full-size optimizer sensitivities were evaluated on 200 held-out seeds each.
All 1800 native simulations finish 50 steps. Seeds 10000–10199 are disjoint from the search seeds 0–49.
No reduced-model or paper-completion credit is assigned to this qualification.

Before execution, the evaluator checks the source audits and hashes of every source search artifact.
It uses the unchanged full-size model, explicit NetLogo 5.3.1 runtime, and qualified native evaluator.
Every retained frontier policy is reevaluated; none is dropped based on its held-out result.

The independent auditor verifies each source model’s width, copied frontier and protocol hashes, request, native result, and terminal status.
It reconstructs sample means and standard errors with integer sums and sums of squares.
It independently reconstructs every empirical dominance decision against the same-seed full-size searched frontiers.
Identical policy/seed inputs, when present, must reproduce identical observable native outputs.
A corrupted standard error is rejected with all native records unchanged; the negative archive and traceback are retained.

These source runs all use width 50. Their pooled reference is an implementation qualification, not reduced-to-full-model evidence.
The production campaign instead has one full-size search per optimizer seed and compares its five reduced-size searches against that reference.
Neither comparison treats the finite searched frontier as a proven global frontier.

Archives retain exact requests, outputs, copied source frontiers, protocols, source audits, runtime metadata, and the executed evaluator.
Every archive member matches its original bytes. Fresh extraction reproduces the independent audit byte-for-byte.
The independent auditor also requires the original pinned source runtime manifests and models to verify grid-width labels.

```sh
python run_frontier_transfer.py /path/to/plan.json /path/to/new-output
python audit_frontier_transfer.py /path/to/new-output /path/to/new-audit.json
```
