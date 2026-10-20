"""Audit complete predictive exports and summarize the frozen comparison."""

import csv
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

root, output = map(Path, sys.argv[1:3])
assert not output.exists()
assert json.loads((root / "optimization-terminal.json").read_bytes()) == {
    "exit_code": 0,
    "audited_epochs_per_method": 5000,
    "initial_flows_byte_identical": True,
    "posterior_analysis_complete": False,
}
protocol = json.loads((root / "protocol.json").read_bytes())
for name, digest in protocol["full_campaign"]["source_sha256"].items():
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == digest
for method in ["pathwise", "vargrad"]:
    audit = json.loads((root / f"{method}-audit.json").read_bytes())
    assert audit["epochs"] == 5000 and audit["validation_draws"] == 25000
    assert audit["optimizer_components_verified"] == 19114 * 5000
    for name, digest in audit["sha256"].items():
        assert hashlib.sha256((root / method / name).read_bytes()).hexdigest() == digest
predictive = root / "predictive"
observation = np.loadtxt(predictive / "observation.csv", delimiter=",")
assert observation.shape == (2, 50) and np.isfinite(observation).all()
assert (predictive / "observation.csv").read_bytes() == (
    root / "pathwise/observation.csv"
).read_bytes()
channels = ["mean_wealth", "alive_fraction"]
names = ["p1", "p6", "m_alpha", "m_beta", "w_alpha", "w_beta"]
truth = np.array([0.2, 0.8, 2.0, 5.0, 5.0, 2.0])
reports = {}
for distribution in ["prior", "pathwise", "vargrad", "truth"]:
    parameter_file = predictive / f"{distribution}-parameters.csv"
    with parameter_file.open() as stream:
        reader = csv.DictReader(stream)
        assert reader.fieldnames == ["sample", *names]
        rows = list(reader)
    assert [int(row["sample"]) for row in rows] == list(range(1, 1001))
    parameters = np.array([[float(row[name]) for name in names] for row in rows])
    assert np.isfinite(parameters).all()
    assert np.all((parameters[:, :2] > 0) & (parameters[:, :2] < 1))
    assert np.all((parameters[:, 2:] > 0.1) & (parameters[:, 2:] < 10))
    assert np.allclose(parameters[:, 0] + parameters[:, 1], 1, rtol=0, atol=1e-12)
    if distribution == "truth":
        assert np.array_equal(parameters, np.broadcast_to(truth, parameters.shape))
    trajectory_file = predictive / f"{distribution}-trajectories.csv"
    with trajectory_file.open() as stream:
        reader = csv.DictReader(stream)
        assert reader.fieldnames == ["sample", "seed", "time", *channels]
        rows = list(reader)
    assert len(rows) == 50000
    assert all(
        (int(row["sample"]), int(row["seed"]), int(row["time"]))
        == (index // 50 + 1, index // 50 + 10000, index % 50)
        for index, row in enumerate(rows)
    )
    trajectories = np.array(
        [[float(row[name]) for name in channels] for row in rows]
    ).reshape(1000, 50, 2)
    assert np.isfinite(trajectories).all()
    alive = trajectories[:, :, 1]
    assert np.all((alive >= 0) & (alive <= 1))
    assert np.all(alive[:, 0] == 1) and np.all(np.diff(alive, axis=1) <= 0)
    assert np.allclose(100 * alive, np.round(100 * alive), rtol=0, atol=1e-10)
    assert np.all((trajectories[:, 0, 0] >= 6) & (trajectories[:, 0, 0] <= 25))
    mean = np.mean(trajectories, axis=0)
    quantiles = np.quantile(trajectories, [0.025, 0.5, 0.975], axis=0, method="linear")
    parameter_quantiles = np.quantile(
        parameters, [0.025, 0.5, 0.975], axis=0, method="linear"
    )
    reports[distribution] = {
        "draws": 1000,
        "stored_states": 50000,
        "parameters": {
            name: {
                "mean": float(np.mean(parameters[:, index])),
                "q025": float(parameter_quantiles[0, index]),
                "median": float(parameter_quantiles[1, index]),
                "q975": float(parameter_quantiles[2, index]),
                "truth": float(truth[index]),
                "truth_inside_pointwise_interval": bool(
                    parameter_quantiles[0, index]
                    <= truth[index]
                    <= parameter_quantiles[2, index]
                ),
            }
            for index, name in enumerate(names)
        },
        "channels": {
            name: {
                "mean": mean[:, index].tolist(),
                "q025": quantiles[0, :, index].tolist(),
                "median": quantiles[1, :, index].tolist(),
                "q975": quantiles[2, :, index].tolist(),
                "observed_states_inside_interval": int(
                    np.count_nonzero(
                        (observation[index] >= quantiles[0, :, index])
                        & (observation[index] <= quantiles[2, :, index])
                    )
                ),
                "predictive_mean_rmse_against_observation": float(
                    np.sqrt(np.mean((mean[:, index] - observation[index]) ** 2))
                ),
            }
            for index, name in enumerate(channels)
        },
        "sha256": {
            path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in [parameter_file, trajectory_file]
        },
    }
report = {
    "protocol_sha256": hashlib.sha256((root / "protocol.json").read_bytes()).hexdigest(),
    "observation_sha256": hashlib.sha256(
        (predictive / "observation.csv").read_bytes()
    ).hexdigest(),
    "distributions": reports,
    "scope": "All 4000 declared predictive trajectories, including initial states, retained. Export invariants and summary arithmetic are checked; this is not independent movement replay. Intervals are pointwise empirical quantiles, not simultaneous coverage. Prior and validation settings are reconstructed; no historical posterior identity is inferred.",
}
output.write_text(json.dumps(report, indent=2) + "\n")
print(
    json.dumps(
        {
            "distributions": len(reports),
            "trajectories": 4000,
            "stored_states": 200000,
            "output": str(output),
        }
    )
)
