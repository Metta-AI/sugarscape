# Timing propositions and reporting inconsistencies

The audit separates paper prose, printed cells, and fresh native fitted means.
It evaluates 13 explicit propositions against each set of 51 timing cells.
The complete-grid comparison replays byte-for-byte; repeated claim extraction also matches exactly.

Three prose propositions disagree with the paper’s own tables:

| Proposition | Printed table evidence | Fresh execution |
| --- | --- | --- |
| Lock-Based optimum at three capabilities (page 21) | Minimum at two: 20.0 seconds | Minimum at seven: 6.474134 seconds |
| TVar optimum at three capabilities (page 21) | Minimum at one: 21.1 seconds | Minimum at six: 8.305119 seconds |
| Lock-Based faster than TVar throughout rebirth scaling (page 23) | At 2,500 agents: 272.0 versus 147.0 seconds | At 2,500 agents: 79.452583 versus 50.012244 seconds |

Two additional fresh point-estimate directions differ from the printed table and prose:
sequential and Lock-Based runs at 2,000 agents are slower than at 1,500.
The sequential means are 129.450456 versus 129.298704 seconds.
The Lock-Based means are 54.788658 versus 54.501625 seconds.
These small differences receive no significance or equivalence interpretation.

Other inspected propositions hold for both printed cells and fresh means:
TArray is fastest at capabilities 3–8 and across all rebirth populations;
TArray is slowest at one capability;
Lock-Based beats TVar at every Table 6 capability;
sequential and TVar improve from 2,000 to 2,500 agents;
both Table 9 workloads slow from 16 to 32 to 64 capabilities.

Tables 6/8 use different hardware. Table 9 matches instance class without historical scheduling evidence.
This post-hoc comparison adds neither a tolerance nor a completed-study verdict.
Causal explanations concerning laziness, contention, and scheduling remain untested.

Run `audit_timing_claims.py PAPER_PDF NEW_OUTPUT` from this checkout.
The command verifies the paper, frozen target and underlying audit hashes before evaluating propositions.
