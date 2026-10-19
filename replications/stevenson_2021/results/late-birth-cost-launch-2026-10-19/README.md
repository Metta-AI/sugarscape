# Later birth-cost window sensitivity

The earlier author specification uses cycles 130,000–150,000 for birth-cost sensitivity.
Our original ensemble ends at 100,000 cycles. This predeclared extension evaluates that later window without assigning it to the target paper.
The same 100 seeds, fixed model, infertility 10, birth cost 40 and 100-cycle observation interval remain unchanged.
Each run restarts from its original founder and must reproduce every retained observation through cycle 100,000 exactly.
Two local workers execute at most 120 seconds per seed; every exit and failure is retained.

The first two runs complete 150,000 cycles and match all 2,002 shared-prefix observations byte-for-byte.
Both full trajectories and observer outputs are retained here losslessly.
The full ensemble remains running; partial results receive no aggregate or completion credit.
The real incomplete ensemble was rejected before analysis output creation.

`protocol.json` pins the simulator, binary and launcher. `analyze.py` requires all 100 ordered successful records, rechecks hashes and prefixes, and compares the original (75,000,100,000] window with (130,000,150,000].
Its confidence intervals treat each seed as one replicate; all trajectories must remain nonextinct for these age/Gini summaries.
The original primary results remain unchanged.
