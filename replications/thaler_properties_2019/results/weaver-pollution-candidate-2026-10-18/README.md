# Pollution candidate and diffusion configuration

Two full NetLogo 4.0.4 executions use seed 602352629 and 1,000 steps.
The diagnostic starts from `preset1`, enables pollution and diffusion, and sets both rates to one.
These settings are explicit study choices: the candidate contains no pollution-enabled preset.
Historical identity with Weaver (2009) remains unverified.

The population-only control and isolated observers agree at every one of 1,001 frames.
Final population is 175. The independent audit validates 183,170 agent records and
262,701 cell records, including coordinates, identities, finite resources, and pollution totals.
This is one model input with an observation control, not two independent samples.

The archived first observer fails compilation because its three-item `list` expression lacks parentheses.
The corrected observer completes; the auditor rejects the actual incomplete first execution.
Neither failure is attributed to the original model.

## Configuration comparison

Haskell averages pollution over the cell and its four cardinal neighbors every tick.
The candidate calls `diffuse`, which distributes pollution among eight neighbors.
The [historical NetLogo manual](https://ccl.northwestern.edu/netlogo/4.0/docs/dictionary.html#diffuse)
distinguishes this from `diffuse4`. A rate change alone cannot match these neighborhoods.
Original Haskell coordinate aliasing adds a separate limitation.

Haskell initializes pollution to zero and divides sugar by `1 + pollution`.
The candidate initializes pollution to one and divides sugar by `pollution`.
That offset alone does not establish a dynamics difference: the denominators agree
under corresponding pollution states and constant-preserving diffusion.
We do not claim matching states across these differently configured models.

`source-audit.json` pins the inspected checkout; `historical-source-check.json` verifies
its relevant code against the paper revision. Five files match exactly. The sixth
changes only a page-number comment outside the pollution configuration.

## Evidence and readback

`native-evidence.tar.gz` contains completed and failed executions, the observer,
runner, commands, protocols, exit receipts, raw trajectories, and independent auditor.
All archive members were byte-checked against retained evidence. Extracted readback
reproduced `audit.json` exactly:

```sh
python completed/audit.py completed NEW_AUDIT.json
```

Each native execution had a 240-second timeout, one active Java processor, and a 512 MiB heap.
No qualitative acceptance threshold was fitted. These results establish a runnable
candidate and a concrete configuration gap; appendix A.5 remains unresolved.
