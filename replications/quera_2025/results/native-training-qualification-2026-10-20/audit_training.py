"""Replay complete native optimizer updates and validation checkpoint selection."""

import csv
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

root, destination = map(Path, sys.argv[1:3])
assert not destination.exists()
with (root / "epochs.csv").open() as stream:
    epochs = list(csv.DictReader(stream))
completion = dict(
    line.split("=", 1) for line in (root / "completion.txt").read_text().splitlines()
)
assert len(epochs) == int(completion["epochs"]) == 3
assert [int(row["epoch"]) for row in epochs] == [1, 2, 3]
parameters = np.loadtxt(root / "initial-parameters.csv", dtype=np.float64)
assert parameters.ndim == 1 and np.isfinite(parameters).all()
moment = np.zeros_like(parameters)
variance = np.zeros_like(parameters)
maximum_error = 0.0
validation_losses = []
for row in epochs:
    iteration = int(row["epoch"])
    gradient = np.loadtxt(root / f"gradient-{iteration}.csv", dtype=np.float64)
    updated = np.loadtxt(root / f"parameters-{iteration}.csv", dtype=np.float64)
    assert gradient.shape == updated.shape == parameters.shape
    assert np.isfinite(gradient).all() and np.isfinite(updated).all()
    assert all(np.isfinite(float(value)) for value in row.values())
    norm = np.linalg.norm(gradient)
    assert np.isclose(norm, float(row["gradient_norm"]), rtol=2e-6, atol=1e-8)
    normalized = gradient / norm
    moment = 0.9 * moment + 0.1 * normalized
    variance = 0.99 * variance + 0.01 * normalized**2
    delta = (moment / (1 - 0.9**iteration)) / (
        np.sqrt(variance / (1 - 0.99**iteration)) + 1e-8
    )
    expected = parameters - 0.0005 * (delta + 0.01 * parameters)
    error = float(np.max(np.abs(expected - updated)))
    # Native parameters and optimizer accumulators are Float32.
    assert np.allclose(expected, updated, rtol=2e-6, atol=2e-7), error
    maximum_error = max(maximum_error, error)
    parameters = updated
    with (root / f"validation-samples-{iteration}.csv").open() as stream:
        samples = list(csv.DictReader(stream))
    assert [int(sample["sample"]) for sample in samples] == list(range(1, 6))
    for sample in samples:
        assert all(np.isfinite(float(value)) for value in sample.values())
        assert 0 < float(sample["p1"]) < 1
        assert np.isclose(float(sample["p1"]) + float(sample["p6"]), 1, atol=1e-12)
        assert all(
            0.1 < float(sample[name]) < 10
            for name in ["m_alpha", "m_beta", "w_alpha", "w_beta"]
        )
    loss = sum(float(sample["negative_log_likelihood"]) / 5 for sample in samples)
    assert np.isclose(loss, float(row["validation_loss"]), rtol=1e-12, atol=1e-12)
    validation_losses.append(loss)
best = int(np.argmin(validation_losses)) + 1
assert int(completion["best_epoch"]) == best
assert float(completion["best_validation"]) == validation_losses[best - 1]
assert (root / "best-parameters.csv").read_bytes() == (
    root / f"parameters-{best}.csv"
).read_bytes()
for filename in ["observation.csv", "validation.csv"]:
    values = np.loadtxt(root / filename, delimiter=",")
    assert values.shape == (2, 50) and np.isfinite(values).all()
report = {
    "method": completion["method"],
    "epochs": len(epochs),
    "parameter_count": len(parameters),
    "optimizer_components_verified": len(parameters) * len(epochs),
    "maximum_float64_replay_absolute_error": maximum_error,
    "validation_draws": 15,
    "selected_epoch": best,
    "selected_validation_loss": validation_losses[best - 1],
    "sha256": {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.iterdir())
        if path.is_file()
    },
    "scope": "Complete native training qualification, optimizer arithmetic, and checkpoint selection. No historical calibration or posterior replication claim.",
}
destination.write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({key: value for key, value in report.items() if key != "sha256"}))
