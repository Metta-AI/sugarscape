"""Replay complete native optimizer updates and validation checkpoint selection."""

import csv
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

root, destination, norm_file = map(Path, sys.argv[1:4])
with norm_file.open() as stream:
    norm_rows = list(csv.DictReader(stream))
assert len(norm_rows) == 5000
assert [int(row["epoch"]) for row in norm_rows] == list(range(1, 5001))
maximum_norm_relative_difference = 0.0
assert not destination.exists()
with (root / "epochs.csv").open() as stream:
    epochs = list(csv.DictReader(stream))
completion = dict(
    line.split("=", 1) for line in (root / "completion.txt").read_text().splitlines()
)
assert len(epochs) == int(completion["epochs"]) == 5000
assert [int(row["epoch"]) for row in epochs] == list(range(1, 5001))
parameters = np.loadtxt(root / "initial-parameters.csv", dtype=np.float32).astype(np.float64)
assert parameters.ndim == 1 and np.isfinite(parameters).all()
moment = np.zeros_like(parameters)
variance = np.zeros_like(parameters)
maximum_error = 0.0
validation_losses = []
for row in epochs:
    iteration = int(row["epoch"])
    gradient = np.loadtxt(root / f"gradient-{iteration}.csv", dtype=np.float32).astype(np.float64)
    updated = np.loadtxt(root / f"parameters-{iteration}.csv", dtype=np.float32).astype(np.float64)
    assert gradient.shape == updated.shape == parameters.shape
    assert np.isfinite(gradient).all() and np.isfinite(updated).all()
    assert all(np.isfinite(float(value)) for value in row.values())
    norm_row = norm_rows[iteration - 1]
    gradient_path = root / f"gradient-{iteration}.csv"
    assert hashlib.sha256(gradient_path.read_bytes()).hexdigest() == norm_row["gradient_sha256"]
    native_norm = float(np.float32(norm_row["native_float32_norm"]))
    assert native_norm == float(np.float32(norm_row["recorded_float32_norm"]))
    assert native_norm == float(np.float32(row["gradient_norm"]))
    assert np.isfinite(native_norm) and native_norm > 0
    reference_norm = float(np.linalg.norm(gradient))
    assert np.isclose(reference_norm, float(norm_row["float64_norm"]), rtol=1e-12, atol=1e-12)
    maximum_norm_relative_difference = max(
        maximum_norm_relative_difference, abs(reference_norm - native_norm) / reference_norm
    )
    normalized = gradient / native_norm
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
    "native_float32_norms_verified": len(norm_rows),
    "norm_replay_sha256": hashlib.sha256(norm_file.read_bytes()).hexdigest(),
    "maximum_float32_vs_float64_norm_relative_difference": maximum_norm_relative_difference,
    "epochs": len(epochs),
    "parameter_count": len(parameters),
    "optimizer_components_verified": len(parameters) * len(epochs),
    "maximum_float64_replay_absolute_error": maximum_error,
    "validation_draws": 5 * len(epochs),
    "selected_epoch": best,
    "selected_validation_loss": validation_losses[best - 1],
    "sha256": {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.iterdir())
        if path.is_file()
    },
    "scope": "Complete5000-epoch replay using exact exported Float32 values and independently replayed native Float32 normalization. Original optimizer-update tolerance unchanged; original Float64 norm-check failure retained. Predictive analysis remains separate.",
}
destination.write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({key: value for key, value in report.items() if key != "sha256"}))
