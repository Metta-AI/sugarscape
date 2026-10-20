"""Audit the complete two-channel native Sugarscape MMD and AD workflow."""

from pathlib import Path
import csv
import hashlib
import json
import math
import statistics
import sys

root = Path(sys.argv[1])
output = Path(sys.argv[2])
assert not output.exists()
q = root / "paired-qualification"
reference_pins = json.loads((root / "reference-pins.json").read_bytes())
for name, digest in reference_pins.items():
    assert (
        hashlib.sha256((root / "reference" / name).read_bytes()).hexdigest() == digest
    )
    assert (q / name).read_bytes() == (root / "reference" / name).read_bytes()
with (q / "wealth.csv").open() as f:
    rows = list(csv.DictReader(f))
assert [int(r["time"]) for r in rows] == list(range(50))
y = [[float(r[f"observed_{channel}"]) for r in rows] for channel in ["wealth", "alive"]]
xs = [
    [
        [float(r[f"simulation_{i}_{channel}"]) for r in rows]
        for channel in ["wealth", "alive"]
    ]
    for i in [1, 2]
]
assert all(
    math.isfinite(x) for sample in [y, *xs] for channel in sample for x in channel
)
sigmas = [
    statistics.median(
        [
            math.sqrt(
                math.fsum((a - b) ** 2 for a, b in zip(left[c], right[c], strict=True))
            )
            for left, right in [(xs[0], xs[1]), (xs[0], y), (xs[1], y)]
        ]
    )
    + sys.float_info.epsilon
    for c in range(2)
]
kernels = [
    math.exp(
        -0.5
        * math.fsum(
            (a - b) ** 2 / sigmas[c] ** 2
            for c in range(2)
            for a, b in zip(left[c], right[c], strict=True)
        )
    )
    for left, right in [(xs[0], xs[1]), (xs[0], y), (xs[1], y)]
]
loss = -(kernels[0] - kernels[1] - kernels[2]) / (0.0001 * 50)
with (q / "loss-and-gradient.csv").open() as f:
    (result,) = list(csv.DictReader(f))
assert math.isclose(loss, float(result["native_loss"]), rel_tol=1e-10, abs_tol=1e-10)
assert math.isclose(loss, float(result["ad_loss"]), rel_tol=1e-10, abs_tol=1e-10)
with (q / "native-jacobians.csv").open() as f:
    jacobian_rows = list(csv.DictReader(f))
assert [
    (int(r["simulation"]), int(r["channel"]), int(r["time"])) for r in jacobian_rows
] == [(s, c, t) for s in [1, 2] for t in range(50) for c in [1, 2]]
assert all(
    math.isclose(
        float(r["value"]),
        xs[int(r["simulation"]) - 1][int(r["channel"]) - 1][int(r["time"])],
        rel_tol=1e-12,
        abs_tol=1e-12,
    )
    for r in jacobian_rows
)
gradients = {}
for parameter in ["p1", "p6", "m_alpha", "m_beta", "w_alpha", "w_beta"]:
    j = [
        [
            [
                float(r[parameter])
                for r in jacobian_rows
                if int(r["simulation"]) == s and int(r["channel"]) == c
            ]
            for c in [1, 2]
        ]
        for s in [1, 2]
    ]
    derivatives = [
        -kernels[0]
        * math.fsum(
            (a - b) * (da - db) / sigmas[c] ** 2
            for c in range(2)
            for a, b, da, db in zip(xs[0][c], xs[1][c], j[0][c], j[1][c], strict=True)
        ),
        -kernels[1]
        * math.fsum(
            (a - b) * da / sigmas[c] ** 2
            for c in range(2)
            for a, b, da in zip(xs[0][c], y[c], j[0][c], strict=True)
        ),
        -kernels[2]
        * math.fsum(
            (a - b) * da / sigmas[c] ** 2
            for c in range(2)
            for a, b, da in zip(xs[1][c], y[c], j[1][c], strict=True)
        ),
    ]
    gradient = -(derivatives[0] - derivatives[1] - derivatives[2]) / (0.0001 * 50)
    native = float(result[parameter])
    assert math.isfinite(native) and math.isclose(
        gradient, native, rel_tol=1e-9, abs_tol=1e-9
    )
    gradients[parameter] = {
        "independent": gradient,
        "native": native,
        "absolute_difference": abs(gradient - native),
    }
with (q / "flow-samples.csv").open() as f:
    samples = list(csv.DictReader(f))
assert len(samples) == 20 and all(
    len(r) == 7 and all(math.isfinite(float(x)) for x in r.values()) for r in samples
)
assert "No optimization" in (q / "scope.txt").read_text()
pins = json.loads((root / "provenance.json").read_bytes())["prior_runtime_pins"]
for name, digest in pins.items():
    assert hashlib.sha256(Path(name).read_bytes()).hexdigest() == digest
hashes = {
    str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
    for p in sorted(q.rglob("*"))
    if p.is_file()
}
report = {
    "observed_states": 50,
    "simulated_states": 100,
    "channels": ["mean_wealth", "alive_fraction"],
    "native_jacobian_values": 1200,
    "flow_samples": 20,
    "independent_loss": loss,
    "native_loss": float(result["native_loss"]),
    "ad_loss": float(result["ad_loss"]),
    "bandwidths": sigmas,
    "gradients": gradients,
    "prior_runtime_pins_unchanged": True,
    "prior_seed0_agent_and_cell_csvs_byte_identical": True,
    "sha256": hashes,
    "scope": "End-to-end native two-channel model/loss/AD chain and flow sampling only. Bandwidths are held fixed in derivatives, matching author ignore_derivatives. This is not finite-difference unbiasedness, posterior calibration or paper replication.",
}
output.write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({k: v for k, v in report.items() if k not in ["sha256", "gradients"]}))
