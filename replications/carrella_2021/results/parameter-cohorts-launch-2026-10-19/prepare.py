"""Freeze ten outcome-blind parameter cohorts before simulation."""

import csv
import hashlib
import json
from pathlib import Path
import shutil
import numpy as np

root = Path("/Users/relh/Code/workspace")
out = Path(__file__).resolve().parent
prior = root / "sugarscape-replication-evidence/carrella-row675-seed-ensemble-002"
source = root / "sugarscape-nofreelunch-reference/data/sugarscape/params_sugarscape.csv"
repo = root / "sugarscape-carrella/replications/carrella_2021"
assert (
    hashlib.sha256(source.read_bytes()).hexdigest()
    == "216a4fbfd5357d7f5c8fa0140792aaa511df224ad83f91a6cdf23758e688c9fa"
)
with source.open() as stream:
    reader = csv.DictReader(stream)
    fields = reader.fieldnames
    rows = list(reader)
names = [n for n in fields if n != "random-seed"]
x = np.array([[float(r[n]) for n in names] for r in rows])
low, high = x.min(axis=0), x.max(axis=0)
z = (x - low) / (high - low)
selected = [int(np.argmin(((z - 0.5) ** 2).sum(axis=1)))]
while len(selected) < 10:
    distance = np.min(
        ((z[:, None, :] - z[selected][None, :, :]) ** 2).sum(axis=2), axis=1
    )
    distance[selected] = -1
    selected.append(int(np.argmax(distance)))
assert len(set(selected)) == 10 and 675 not in selected
# A separate scalar calculation verifies the selection without trajectory data.
scalar = [
    [(float(r[n]) - low[j]) / (high[j] - low[j]) for j, n in enumerate(names)]
    for r in rows
]
check = [
    min(range(len(rows)), key=lambda i: (sum((v - 0.5) ** 2 for v in scalar[i]), i))
]
while len(check) < 10:
    check.append(
        max(
            (i for i in range(len(rows)) if i not in check),
            key=lambda i: (
                min(
                    sum((a - b) ** 2 for a, b in zip(scalar[i], scalar[j]))
                    for j in check
                ),
                -i,
            ),
        )
    )
assert selected == check
plan = {
    "selection": "Nearest observed row to normalized parameter midpoint, then greedy farthest-point selection in five-dimensional squared Euclidean distance; observed min/max scaling; lowest row index breaks ties. No outcome values used.",
    "parameter_columns": names,
    "minima": low.tolist(),
    "maxima": high.tolist(),
    "original_rows_zero_based": selected,
    "seeds_per_engine": 64,
    "engines": ["native", "independent"],
    "total_runs": 1280,
    "observations_per_run": 501,
    "per_cohort_wall_limit_seconds": 600,
    "total_simulation_bound_seconds": 6000,
    "maximum_outputs_bytes": 536870912,
    "minimum_free_bytes": 2147483648,
    "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
    "analysis": "Retain all ten cohorts and all failures. Existing six-metric maximum ECDF permutation comparison and two rare-event Fisher comparisons per cohort. Report all effect sizes; apply Holm across 30 cohort-level tests (ten joint-six-metric and twenty rare-event tests) before flagging statistical differences. Failure to reject does not establish equivalence. Fixed seeds do not align different random generators. No whole-paper verdict.",
    "numpy": np.__version__,
}
(out / "plan.json").write_text(json.dumps(plan, indent=2) + "\n")
for index in selected:
    target = out / f"row-{index}"
    target.mkdir()
    (target / "independent-parameters").mkdir()
    for filename in ["model.py", "Replay.java", "Replay.class"]:
        shutil.copyfile(prior / filename, target / filename)
    with (target / "parameters.csv").open("w") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for seed in range(64):
            row = {**rows[index], "random-seed": str(seed)}
            writer.writerow(row)
            params = {
                "population": int(float(row["initial-population"])),
                "mutation": float(row["pmut"]),
                "maximum_sugar": int(float(row["maximum-sugar-endowment"])),
                "maximum_spice": int(float(row["maximum-spice-endowment"])),
                "reproduction": float(row["wealth-reproduction"]),
                "seed": seed,
            }
            (target / "independent-parameters" / f"{seed}.json").write_text(
                json.dumps(params) + "\n"
            )
    protocol = json.loads((prior / "protocol.json").read_text())
    protocol.update(
        original_input_zero_based=index,
        original_parameters=rows[index],
        fresh_seeds=list(range(64)),
        native_runs=64,
        independent_runs=64,
        wall_limit_seconds=600,
        maximum_outputs_bytes=52428800,
    )
    protocol["scope"] = plan["analysis"]
    protocol["native_parameter_interval"] = [0, 64]
    protocol["predeclared_measurements"]["analysis"] = plan["analysis"]
    pins = [
        source,
        root
        / "sugarscape-nofreelunch-reference/data/sugarscape/Sugarscape trade.nlogo",
        repo / "model.py",
        repo / "Replay.java",
        target / "parameters.csv",
        target / "model.py",
        target / "Replay.java",
        target / "Replay.class",
    ]
    protocol["input_sha256"] = {
        str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in pins
    }
    (target / "protocol.json").write_text(json.dumps(protocol, indent=2) + "\n")
    launcher = (
        (prior / "launch.py")
        .read_text()
        .replace('"64",\n            "576",', '"0",\n            "64",')
        .replace(
            '"native_runs": 512, "independent_runs": 512',
            '"native_runs": 64, "independent_runs": 64',
        )
    )
    assert '"576"' not in launcher
    (target / "launch.py").write_text(launcher)
print(json.dumps(plan, indent=2))
