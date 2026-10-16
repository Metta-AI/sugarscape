# Reproduction-boundary diagnostic

The author's later algorithms disagree about equality at puberty and birth cost.
[Local Sharing (2023), v1, Algorithm 1 line 17](https://arxiv.org/pdf/2305.17177v1) uses strict age and wealth comparisons.
[Struggle for Existence (2023), v2, Algorithm 1 line 19](https://arxiv.org/pdf/2302.03096v2) permits equality for both.
The first algorithm was checked visually against page 4 of the original PDF.
Neither establishes historical semantics for the 2021 study; the baseline remains unchanged.

Before running, declare a two-by-two diagnostic: age >= 1 versus > 1, and wealth >= birth cost versus > birth cost.
Run seeds 111–120 for both original fixed scenarios, each through 100,000 cycles or extinction: 80 runs total.
Use the original 50×50 world, vision six, metabolism three, regrowth one, and initial single agent with zero wealth.
Low fertility uses infertility 85 and birth cost zero; birth cost uses infertility 10 and cost 40.
Record every 100 cycles. Retain both original late windows, 50,100–75,000 and 75,100–100,000.
Report all seeds and extinctions, including discrepancies; do not choose the rule producing closest agreement.

Only comparison operators change. Preserve generated sources, exact diffs, compiler settings, hashes, trajectories, and native exit status.
Each birth-cost age-only pair should be byte-identical: a newborn cannot reach wealth 40 before becoming older than one cycle.
This is a whole-simulation invariance check, not a prediction of low-fertility agreement.
Use paired seed-level differences to describe sensitivity; changing a rule can change subsequent random draws.
Results remain exploratory and do not count as a completed or negative replication.
