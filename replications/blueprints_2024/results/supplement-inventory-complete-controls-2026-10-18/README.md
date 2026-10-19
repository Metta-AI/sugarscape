# Corrected remaining supplementary inputs

The earlier 99,994-row inventory excluded six initial controls but missed two already completed original inputs from the paired-runtime study.
This correction excludes all eight validated original inputs and leaves **99,992** remaining:

| Experiment | Original inputs | Completed inputs excluded | Remaining |
| --- | ---: | ---: | ---: |
| Selfishness | 50,500 | 5 | 50,495 |
| Mixed societies | 49,500 | 3 | 49,497 |
| Total | 100,000 | 8 | 99,992 |

The two additional exclusions use selfishness 0.37 and 0.73 with original seed 175856849482260318.
Their prior independent audits validate 5,001 observations each, including exact original configurations and complete native trajectories.
They were already complete; this correction adds no new scientific result.
No sweep dispatch used the earlier worklist.

The planner now accepts repeated audit/archive source pairs instead of assuming one six-control directory layout.
Each audit resolves its producer manifest by exact SHA-256 inside the supplied native archive.
The original configuration, source release, archive identity, seed, and complete trajectory hashes are then checked.
Repeated records for the same input must agree on both configuration and trajectory hashes; they exclude only one input.
No native files are extracted or modified.

Reproduce from the repository root:

```sh
python replications/blueprints_2024/plan_supplement.py /path/to/original-archives /path/to/new-output \
  --completed-source replications/blueprints_2024/results/supplement-controls-2026-10-17/audits \
    replications/blueprints_2024/results/supplement-controls-2026-10-17/native.tar.gz \
  --completed-source replications/blueprints_2024/results/runtime-pairs-2026-10-17/audit \
    replications/blueprints_2024/results/runtime-pairs-2026-10-17/native.tar.gz
python replications/blueprints_2024/results/supplement-inventory-complete-controls-2026-10-18/readback.py \
  /path/to/original-archives
```

The independent CSV readback proves exact coverage of both original ZIP filename sets by remaining inputs plus exclusions.
It also proves that precisely the two missed completed inputs were removed and every other worklist row is unchanged.
A second complete planner execution supplies the six-control source twice; the remaining worklist is byte-identical and still excludes eight unique inputs.
Retain every completed source when regenerating future worklists; runtime repetitions must never be counted as additional required inputs.

The prior inventory and its original report remain available as historical evidence.
Neither this worklist nor its verification launches simulations or completes the paper.
