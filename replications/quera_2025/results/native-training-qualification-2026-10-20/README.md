# Native calibration training qualification

Both pathwise and VarGrad complete three native epochs with five Monte Carlo samples per update and two simulator samples per MMD evaluation.
Each arm has 19,114 trainable parameters. Independent Python verifies all 57,342 optimizer components per arm.
Maximum Float64 reconstruction errors are 4.94e-8 and 5.59e-8 against native Float32 updates.
The audit verifies unit-gradient normalization, AdamW moments, decay, and each parameter update.
A complete native workflow with one parameter update corrupted by 0.01 is rejected.
Both initial flow parameter vectors are byte-identical.

An independent seed-one observation and fixed validation random numbers select the lowest mean validation loss across epochs.
Each validation evaluation uses five posterior draws, with two simulator trajectories per draw.
Training random states are saved and restored around validation. Both qualification arms select epoch one.
The independently recomputed validation averages and saved parameter bytes match the selected epochs.
These three-epoch results qualify execution and selection; they do not establish convergence or favor either estimator.

The declared reconstructed prior is p1 Uniform(0,1), p6=1-p1, and independent Uniform(0.1,10) priors for the four Beta shapes.
The flow has five independent dimensions for six physical parameters, four layers, two blocks, and 32 hidden units.
Earlier six-dimensional flow sampling was a wrapper qualification, not a recovered historical posterior parameterization.
Learning rate 0.0005 follows a figure-filename hint; weight decay 0.01 is a separate declared choice.
AdamW uses beta values 0.9/0.99, epsilon 1e-8, and learning-rate-scaled decoupled decay.
Mean holdings include all initial agents. The MMD scale is 0.0001; none of these missing settings is selected for numerical agreement.
The author model and loss remain unchanged; the separately qualified random-realization-paired derivative adapter is explicit.
The released training-loss callback is replaced by the paper's validation-selection procedure with a declared validation construction.

`protocol.json` was frozen before fitting. Full native outputs, gradients, parameters, and validation draws are in `native-training.tar.gz`.
Fresh extraction followed by both audits reproduces each audit byte-for-byte.
Run `python audit_training.py EXTRACTED/pathwise-001 NEW_AUDIT_JSON` and repeat for `vargrad-001`; Python requires NumPy.
Native source retains execution-machine paths; the preceding adapter qualification pins the coupled runtime and source revisions.

The admitted full campaign runs 5,000 epochs per estimator sequentially, without early stopping or automatic retry.
Both arms retain every epoch's gradient and parameter vector for independent replay; best validation weights supply the posterior evaluation.
`full-campaign` records the prospective protocol, bounded local admission, and planned predictive analysis.
Its native model and trainer are byte-identical to the qualification files in this directory.
The supervisor uses this directory's `model.jl` and `train.jl` alongside the full-campaign files when reproducing elsewhere.
The first full arm is running; no full-training, posterior, or completed-study claim is made here.
No new cloud spending is reserved.

The full pathwise run's first three epochs reproduce all twelve immutable qualification artifacts byte-for-byte.
`pathwise-prefix-regression.json` records this check; it does not establish full-run completion.
The dependent predictive pipeline waits for both terminal 5,000-epoch optimizer audits before running the frozen 4,000-trajectory comparison.
Python verifies export invariants and recomputes pointwise summaries; independent R checks means, quantiles, coverage counts, and root-mean-square errors.
The analysis code has passed Python lint and R parsing; its native predictive execution remains pending.
Neither predictor summary checks nor R arithmetic constitute independent movement replay or historical posterior validation.
