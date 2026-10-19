# Historical full-workflow preparation

The prepared 4,421,269-byte archive contains the frozen complete replay script and all five saved input folds. All six archive members match their source hashes on fresh readback. Payload SHA-256: `61a5c95f38738fa85432d898f27cb27dd39fe24056f460b87eb8db380fff2391`.

The intended runtime is the same digest-pinned Rocker R 4.0.5 / mgcv 1.8-34 / Matrix 1.3-2 image used in the earlier point-fit controls. No node or historical run has been started. Full current-runtime qualification and a quoted total cost within $3 gate execution. The prospective run uses one fitting thread and a two-hour timeout.

The first modern-runtime fold now passes a fresh saved-output audit: 3,750 numeric predictions/bounds and 626 final random-state integers agree exactly. An initial whole-matrix identity assertion failed because generated data frames retain observation row names; the author's tibble matrices do not. Explicit dimensions, ordered parameter columns, every numeric value, and the random state agree. The failure and attribute difference remain recorded. This is one completed fold, not complete five-fold qualification.

Holding saved floating-point inputs fixed isolates runtime sensitivity from CSV parser sensitivity. The older runtime remains plausible rather than identified as the author's environment. It changes several components together, so this cannot attribute a difference to mgcv alone.
