# Exact checkpoint recovery control

The original ABC workflow now has an external execution control that saves each
held-out observation's summaries and random-generator states before and after
estimation. Writes use a pending file followed by atomic rename. Existing row
checkpoints require the exact expected incoming random state. Fold fingerprints
bind training/test data, parameters, estimator settings, function body and
incoming random state. Estimator mathematics and fold selection stay unchanged.

A complete 1,250-input degree-one semiautomatic ABC workflow was deliberately
interrupted after 37 durable observations, then resumed into a new output folder.
All five saved fold objects are identical to the prior unmodified run, including
6,250 parameter predictions, intervals, training/test data and outgoing random
states. Aggregate objects and metrics are also identical. Every archived member
was compared byte-for-byte with the retained source file.

The independent neural-network attempt estimated roughly four hours per fold,
beyond its four-hour whole-workflow cap. After this recovery validation, that
attempt was explicitly stopped before it saved a fold. Its logs remain retained.
A separate checkpointed attempt runs the same full 5,000-input workload under a
30-hour cap; no neural-network result is claimed here. The small published
neural-network cell remains NA. This control does not complete the paper.

Sources and command records retain the actual external evidence paths used.
