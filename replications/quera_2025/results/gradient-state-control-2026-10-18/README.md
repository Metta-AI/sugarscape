# Full gradient-ensemble state and derivative control

All original diagnostic seeds 3–258 run with ordinary floating-point inputs and
six-parameter ForwardDiff differentiation. The model, manifest and diagnostic
configuration remain unchanged. Native execution exits zero in 45.05 seconds.

An independent verifier imports only Julia standard libraries. It reloads all
512 saved histories and compares **34,560,000 state values exactly**. It then
matches the ordinary histories against every state value in the previously
validated movement trace. Thus the independent movement/resource replay applies
to these differentiated baseline trajectories as well.

All **38,400 newly computed derivatives** exactly match the corresponding 115,200
archived records, which repeat derivatives at three finite-difference step sizes.
Ordinary aggregate wealth also matches every archived baseline record exactly.

## Preserved aggregate-check failure and root cause

The first verifier incorrectly required ordinary and differentiated aggregate
sums to be bitwise identical. It failed; the receipt and traceback are retained
in `audit-exit.json`. All individual state values nevertheless match exactly.

Of 6,400 aggregate pairs, 4,632 differ, with maximum absolute difference
3.197442310920451e-14. For every pair, the verifier independently reconstructs
ordinary aggregation using `sum(wealth)/100` and differentiated aggregation using
`foldl(+, wealth)/100`. Both reconstructions match their native outputs exactly.
This explains the discrepancy through reduction order without adding a tolerance
or changing model code. `aggregate-differences.json` retains every differing pair.

## Scope and reproduction

This validates the complete baseline population of our reconstructed gradient
diagnostic. It does not identify the paper’s exact Figure 11 experiment or
reproduce the missing calibration protocol. Perturbed finite-difference full
histories are not included in this control. No completed-paper credit is added.

Extract `native-evidence.tar.gz` into a fresh directory. Every archive member was
compared byte-for-byte with native output; `archive.json` pins the archive hash.
Obtain the prior movement trace and gradient ensemble from their adjacent result
folders, then run:

```sh
julia --startup-file=no verify_gradient_states.jl EXTRACTED/native MOVEMENT/native ORIGINAL_GRADIENT_ENSEMBLE NEW_AUDIT
```

`audit-reduction-command.json` and its exit receipt preserve the executed command
and output. `audit/sha256.txt` pins all 768 histories and derivative files read
by the verifier. The portable producer is `run_gradient_states.jl SOURCE NEW_OUTPUT`
under the study’s pinned Julia project and depot.
