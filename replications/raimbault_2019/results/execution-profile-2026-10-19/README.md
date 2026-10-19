# Execution profile of two qualified inputs

The unchanged native model ran both previously qualified generated inputs, populations 10 and 510, through 10,000 ticks with Java Flight Recorder enabled. The run exited zero in 26.12 seconds. Instrumentation and shared local hardware make this unsuitable as a production speed benchmark.

All 20,000 Gini-history values and all twelve final metrics for both inputs match the prior baseline exactly. Exported worlds match 5,570 rows, including random state; only export timestamps differ. The retained archive passes thirteen member hashes, and fresh extraction reproduces the audit byte-for-byte.

The recording contains 1,093 execution samples: 1,076 on the NetLogo job thread and seventeen on the main thread. Inclusive procedure counts are movement 543, patch regrowth 268, Gini update 37, and landscape generation 81. Categories may overlap and include setup/reporting. They are sampled call stacks, not independent timings or full-grid cost estimates.

Movement samples frequently include candidate patch-set construction, at-points lookup, Scala vector iteration, and hash-set allocation. This suggests investigating static vision geometry before further Gini-only optimization. Any candidate optimization must preserve occupancy filtering, ordering, random draws, and full state; no candidate implementation or speedup is claimed here.

The original full-grid cost estimate and pending spending decision remain unchanged. No production runs or paper-completion credit are added.
