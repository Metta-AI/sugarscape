# Full-horizon EC/EC native recorder qualification

For original released-code input `released-code-pair-05-repeat-00`, seed 381016329, native NetLogo BehaviorSpace matches the existing custom recorder exactly.
All 320,016 values across 20,001 observations agree: two population counts and fourteen figure statistics at every tick through 20,000.
The native run exits zero after 317.37 seconds. A fresh local download reproduces the comparison against the previously audited trajectory.

Native table SHA256: `89285a6ab7a7f68cef3a23cc24661d9d1a3ab9c6e5e6ef0327f362cec3bba33e`.
Existing trajectory SHA256: `f44f53583f491a40307de1725d60b4c0d93db03e5940a82492b8424f96eb64c5`.
The compressed native table, exact command, experiment XML, scripts, terminal records, and transfer receipts are retained here.

This extends the prior 1,000-tick EC/EC recorder qualification to the full reported horizon for one seed.
It rules out a detected custom-recorder discrepancy for this input. Both executions use the same released model and NetLogo runtime.
It does not independently implement the model, recover historical seeds, establish all-seed recorder equivalence, or resolve the paper discrepancy.
The check used one worker on the existing node, bounded to 600 seconds with a 650-second outer limit.
No new seed coverage or completed-study credit is added.
