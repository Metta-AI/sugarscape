# Completed, qualified Sugarscape method reconstruction

The declared Sugarscape method study is complete, with mixed results and explicit reconstruction choices.
This is an author-code-based method reconstruction with independent state and arithmetic checks.
It is neither an independent implementation of every algorithm nor a numerical reproduction of the historical experiments.
Axtell and SIR experiments are outside this Sugarscape study.

The [paper](https://arxiv.org/html/2509.03303v2) evaluates Sugarscape gradients, compares two calibration estimators, and presents predictive, loss, and posterior plots.
Its continuous-gradient agreement contrasts with categorical-gradient divergence; its calibration discussion reports success for both estimators.
Our requirements cover those Sugarscape components, rather than only the successful pathwise result.

## Requirement assessment

| Requirement | Evidence and assessment |
| --- | --- |
| Native dynamics and measurement | Three calibration pilots independently replay 14,700 agent updates. All 256 gradient baselines replay 614,400 agent and 15,360,000 cell updates exactly. Initial-agent denominators and 50 stored states, including initialization, remain explicit. |
| Ordinary and differentiated states | All 34,560,000 gradient-baseline state values agree exactly. Reduction-order differences are separately reproduced, without changing trajectories. |
| Six-parameter gradient diagnostics | The 256-seed ensemble retains 115,200 records across three finite-difference steps. All 9,216 perturbed cases independently replay 22,118,400 agent and 552,960,000 cell updates with zero error. Categorical differences persist; continuous differences are smaller but not uniformly zero. |
| Calibration model and derivative connection | The two-channel model/loss/gradient qualification checks native and independently reconstructed values. The original adapter mismatched random realizations; a separate paired adapter corrects that connection while preserving earlier native trajectories. |
| Both complete optimization arms | Pathwise and VarGrad each execute 5,000 epochs. Independent replay checks 191,140,000 optimizer components and 50,000 validation draws in total. Both start from identical parameters. |
| Validation selection | Fixed validation rules select pathwise epoch 413 and VarGrad epoch 105. Selected parameter files match the recorded minima exactly. No result-based stopping or checkpoint substitution occurs. |
| Predictive comparison | All 4,000 trajectories and 200,000 stored states are retained. Independent R verifies 1,712 summary values. Pathwise wealth/alive-fraction RMSE is 0.690148/0.018633; VarGrad is 11.953682/0.343806. These compare against the calibration observation, not held-out outcomes. |
| Posterior and training histories | Three rendered PDFs retain 1,000 parameter draws per distribution and all 5,000 epochs per arm. Visual review corrected clipped labels without altering data. Historical smoothing and loss definitions remain unavailable. |
| Durable evidence | Fresh readback verifies all 36,724 perturbed-trace objects, both 15,006-file training archives, and the complete predictive archive. |

## Reconstruction and discrepancy assessment

The submission model revision remains pinned. The historical flow environment was unavailable: the coupled runtime contains 368 packages versus 348 in the original simulator environment.
Native parity, independent replay, and coupled model/loss checks qualify this environment; they do not identify historical dependencies.
The source samples initial positions with replacement, permits zero-score ties outside the vision mask, and checks survival using prior wealth.
Those behaviors remain unchanged and documented. We did not tune the model to repair a plot mismatch.

The frozen prior uses p1 Uniform(0,1), p6=1-p1, and four independent Uniform(0.1,10) Beta-shape priors.
Five independent flow coordinates encode six physical parameters; this is an explicit reconstruction of the probability constraint.
Learning rate 0.0005 follows a figure-filename hint. Weight decay 0.01, epsilon 1e-8, fixed validation randomness, and prior support are declared choices.
The model uses MMD scale 0.0001 and two simulator draws; training uses five Monte Carlo draws and unit-gradient normalization.
Four flow layers, two blocks, 32 hidden units, AdamW coefficients, full horizon, and validation selection follow the stated method.
The native convention records initialization plus 49 transitions for 50 stored states; it is not silently described as 50 transitions.

The original derivative adapter correction is a method implementation change, not an audit tolerance change.
Two later auditor corrections address Float32 norm arithmetic and the amended terminal metadata schema.
Both original failures, original auditors, corrected copies, and corrupted-input controls remain retained.
All optimizer update tolerances are unchanged. Predictive simulations were not rerun after their metadata audit failure.

Our VarGrad result does not support the historical claim that both estimators reproduce the calibration data.
Pathwise has better predictive agreement in this declared run, but does not recover every true parameter.
Its marginal 95% intervals include three of five independent truths; VarGrad includes two of five.
These interval counts are descriptive diagnostics, not a definition of high posterior mass or simultaneous coverage.
The two wealth-shape truths lie outside pathwise intervals; good predictive fit therefore does not establish parameter identification.

We investigated trajectory fidelity, derivative pairing, loss arithmetic, optimizer updates, initial parameters, sample exports, and checkpoint selection.
No failed or omitted run was replaced by a favorable seed. Nevertheless, one optimization seed and reconstructed settings cannot identify the cause of historical disagreement.
We therefore classify this as **completed qualified method reconstruction, mixed outcomes**, not a validated negative replication or wholly positive replication.
Exact Figure 11/19/20 numerical identity and historical parameter recovery remain unresolved claims, not asserted successes.
Further historical-artifact recovery or predeclared robustness experiments may refine the result; they are not silently substituted for this completed protocol.

## Reproduction

Use the pinned source and runtime records in `../native-training-qualification-2026-10-20` and `../calibration-adapter-qualification-2026-10-20`.
The former retains native `model.jl`, `train.jl`, and the prospectively frozen full-campaign protocol.
Native archived scripts retain their execution paths; relocate the DiffABM checkout path and environment paths explicitly when reproducing elsewhere.
Run `train.jl pathwise NEW_PATHWISE 5000` and `train.jl VarGrad NEW_VARGRAD 5000` with the recorded Julia/Python environment.
Use the repository's `replay_norms.jl` and `audit_training_native_norms.py` for complete post-run validation.
The predictive evidence directory retains `predict.jl`, both auditor versions, the amended metadata contract, independent R verifier, and renderer.
Archive manifests and object keys permit independent raw-output inspection without rerunning training.
