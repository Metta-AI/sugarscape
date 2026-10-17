"""Reconstruct a complete original homogeneous ensemble and audit the author's parser."""

import argparse
import gzip
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("coverage", type=Path)
parser.add_argument("engine", type=Path)
parser.add_argument("model")
parser.add_argument("output", type=Path)
args = parser.parse_args()
coverage = json.loads(args.coverage.read_text())
engine = args.engine.resolve()
release = "b9ca671ab7591c7b3606f2d76c33eda344d626d1"
plot_source = engine / "plots/plot.py"
pinned = subprocess.check_output(
    ["git", "show", f"{release}:plots/plot.py"], cwd=engine
)
assert plot_source.read_bytes() == pinned
model_coverage = [r for r in coverage["models"] if r["model"] == args.model]
assert len(model_coverage) == 1 and model_coverage[0]["validated_interval"] == [0, 500]
inputs = {}
for item in coverage["inputs"]:
    if item["model"] != args.model:
        continue
    audit_path = Path(item["path"])
    assert hashlib.sha256(audit_path.read_bytes()).hexdigest() == item["sha256"]
    audit = json.loads(audit_path.read_text())
    for row in audit["results"]:
        seed = row["seed"]
        if seed in inputs:
            assert inputs[seed]["record"] == row
        else:
            inputs[seed] = {
                "record": row,
                "path": str(
                    Path(audit["recorded_root"]) / f"seed-{seed}/trajectory.json.gz"
                ),
            }
assert len(inputs) == 500
output = args.output.resolve()
output.mkdir(parents=True, exist_ok=False)
staged = output / "native-inputs"
staged.mkdir()
metrics = [
    "population",
    "agentMeanTimeToLive",
    "agentStarvationDeaths",
    "agentCombatDeaths",
    "agentWealthTotal",
    "meanAgeAtDeath",
]
values = np.zeros((500, 5001, len(metrics)))
observations = 0
for index, (seed, item) in enumerate(sorted(inputs.items())):
    assert shutil.disk_usage(output).free >= 4 * 1024**3
    raw = gzip.decompress(Path(item["path"]).read_bytes())
    assert hashlib.sha256(raw).hexdigest() == item["record"]["trajectory_sha256"]
    records = json.loads(raw)
    assert [r["timestep"] for r in records] == list(range(len(records)))
    assert len(records) == item["record"]["observations"]
    assert records[-1]["timestep"] == 5000 or records[-1]["population"] == 0
    for t, record in enumerate(records):
        values[index, t] = [record[m] for m in metrics]
    observations += len(records)
    (staged / f"{args.model}{seed}.json").write_bytes(raw)
assert np.isfinite(values).all()
means = np.mean(values, axis=0)
np.savetxt(
    output / "independent-means.csv",
    np.column_stack([np.arange(5001), means]),
    delimiter=",",
    header="timestep," + ",".join(metrics),
    comments="",
)
config = {
    "dataCollectionOptions": {
        "plotTimesteps": 5000,
        "decisionModels": [args.model],
        "plots": [],
    }
}
(output / "plot-config.json").write_text(json.dumps(config, indent=2) + "\n")
command = [
    sys.executable,
    str(plot_source),
    "--path",
    str(staged) + "/",
    "--conf",
    str(output / "plot-config.json"),
    "--outf",
    str(output / "author-means.dat"),
]
(output / "command.json").write_text(json.dumps(command, indent=2) + "\n")
with (
    (output / "author-stdout.log").open("wb") as stdout,
    (output / "author-stderr.log").open("wb") as stderr,
):
    subprocess.run(
        command, cwd=output, stdout=stdout, stderr=stderr, timeout=600, check=True
    )
author = np.loadtxt(output / "author-means.dat", skiprows=1)
assert author.shape == (5001, 7)
assert np.array_equal(author[:, 0], np.arange(5001))
assert np.array_equal(author[:, 1], means[:, 0])
assert np.allclose(author[:, 1:], means, rtol=1e-12, atol=1e-8)
assert np.all(means[:, 0] > 0)
derived = np.column_stack(
    [(means[:, 2] + means[:, 3]) / means[:, 0], means[:, 4] / means[:, 0]]
)
np.savetxt(
    output / "derived-means.csv",
    np.column_stack([np.arange(5001), derived]),
    delimiter=",",
    header="timestep,starvation_plus_combat_per_population,wealth_per_population",
    comments="",
)
report = {
    "model": args.model,
    "runs": 500,
    "observations": observations,
    "timesteps": 5001,
    "metrics": metrics,
    "compared_scalars": 5001 * len(metrics),
    "max_absolute_error_by_metric": dict(
        zip(
            metrics, np.max(np.abs(author[:, 1:] - means), axis=0).tolist(), strict=True
        )
    ),
    "population_exact": True,
    "floating_comparison": {"rtol": 1e-12, "atol": 1e-8},
    "final_means": dict(zip(metrics, means[-1].tolist(), strict=True)),
    "final_derived": {
        "starvation_plus_combat_per_population": float(derived[-1, 0]),
        "wealth_per_population": float(derived[-1, 1]),
    },
    "parser_sha256": hashlib.sha256(pinned).hexdigest(),
    "coverage_sha256": hashlib.sha256(args.coverage.read_bytes()).hexdigest(),
    "semantics": "Absent post-extinction rows contribute zero; denominator remains500. Derived ratios divide ensemble means, not per-run ratios.",
    "scope": "Complete one-model author-parser reproduction. Cross-model paper curves and graphical agreement remain unvalidated.",
}
(output / "inputs.json").write_text(json.dumps(inputs, indent=2) + "\n")
(output / "audit.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
