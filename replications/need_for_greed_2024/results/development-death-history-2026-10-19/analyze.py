"""Execute the unchanged June 2024 author plotting function on 100 pinned native runs."""

from pathlib import Path
import ast
import csv
import hashlib
import json
import statistics
import sys
import tarfile

import numpy as np

repo, audit_path, output = map(Path, sys.argv[1:])
assert not output.exists()
root = Path(__file__).resolve().parent
audit_raw = audit_path.read_bytes()
audit = json.loads(audit_raw)
assert audit["native_inputs"] == 100 and audit["condition"] == 0.37
columns = [
    "population",
    "agentWealthTotal",
    "agentStarvationDeaths",
    "agentCombatDeaths",
    "agentAgingDeaths",
    "agentDiseaseDeaths",
]
sums = {name: [0.0] * 5001 for name in columns}
groups = {}
for row in audit["runs"]:
    groups.setdefault(row["native_archive"], {})[
        row["manifest_member"].rsplit("/", 1)[0] + "/trajectory.json"
    ] = row
seen = set()
observations = 0
for path, wanted in sorted(groups.items()):
    assert (
        hashlib.sha256((repo / path).read_bytes()).hexdigest()
        == audit["native_archive_sha256"][path]
    )
    with tarfile.open(repo / path, mode="r|gz") as archive:
        for member in archive:
            if member.name not in wanted:
                continue
            expected = wanted[member.name]
            assert expected["entry"] not in seen
            seen.add(expected["entry"])
            raw = archive.extractfile(member).read()
            assert hashlib.sha256(raw).hexdigest() == expected["trajectory_sha256"]
            records = json.loads(raw)
            assert len(records) == expected["observations"]
            observations += len(records)
            for t, record in enumerate(records):
                assert record["timestep"] == t
                for name in columns:
                    sums[name][t] += record[name]
assert len(seen) == 100 and observations == 495265
source = root / "author-plot.py"
pin = json.loads((root / "source.json").read_text())
assert hashlib.sha256(source.read_bytes()).hexdigest() == pin["sha256"]
tree = ast.parse(source.read_text())
function = next(
    n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "findMeans"
)
namespace = {"totalTimesteps": 5000, "datacols": columns}
exec(
    compile(ast.Module(body=[function], type_ignores=[]), str(source), "exec"),
    namespace,
)
dataset = {"selfishness037": {"runs": 100, "metrics": sums, "means": {}}}
means = namespace["findMeans"](dataset)["selfishness037"]["means"]
rates = means["meanDeaths"]
matrix = np.array([sums[name] for name in columns])
assert np.all(matrix[0] > 0)
independent = (matrix[2] + matrix[3] + matrix[4]) / matrix[0] * 100
error = float(np.max(np.abs(independent - np.asarray(rates))))
assert error < 1e-12
output.mkdir()
with (output / "per-timestep.csv").open("w") as stream:
    writer = csv.writer(stream)
    writer.writerow(["timestep", *columns, "author_deaths_percent"])
    writer.writerows(
        [t, *[sums[name][t] for name in columns], rates[t]] for t in range(5001)
    )
report = {
    "inputs": 100,
    "observations": observations,
    "cohort_sha256": hashlib.sha256(audit_raw).hexdigest(),
    "source": pin,
    "function": "findMeans",
    "numpy_max_absolute_error": error,
    "per_timestep_rates_checked": len(rates),
    "disease_deaths_total": sum(sums["agentDiseaseDeaths"]),
    "death_percent": {
        "time_mean_including_initial": statistics.mean(rates),
        "time_mean_excluding_initial": statistics.mean(rates[1:]),
        "time_median_including_initial": statistics.median(rates),
        "time_median_excluding_initial": statistics.median(rates[1:]),
    },
    "scope": "Unmodified June30,2024 author findMeans function on per-timestep sums from original v2024.1 trajectories. Post-extinction contributions remain zero, matching parseDataset's initialization. This includes aging and pools populations across seeds; temporal summaries are diagnostics, not the paper's stated metric or proven historical pipeline.",
}
(output / "summary.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
