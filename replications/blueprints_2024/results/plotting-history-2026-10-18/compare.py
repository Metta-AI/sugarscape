"""Check the pre-submission three-cause definition against all Figure 6 paths."""

import argparse
import ast
import gzip
import hashlib
import io
import json
from pathlib import Path
import numpy as np

p = argparse.ArgumentParser(description=__doc__)
p.add_argument("repository", type=Path)
p.add_argument("output", type=Path)
a = p.parse_args()
root = a.output
historical = (root / "cc0408af-plot.py").read_text()
tree = ast.parse(historical)
assignments = [
    n
    for n in ast.walk(tree)
    if isinstance(n, ast.Assign)
    and any(isinstance(t, ast.Name) and t.id == "deaths" for t in n.targets)
]
assert len(assignments) == 1
expression = ast.unparse(assignments[0].value)
expected = "dataset[model]['metrics']['agentStarvationDeaths'][i] + dataset[model]['metrics']['agentCombatDeaths'][i] + dataset[model]['metrics']['agentAgingDeaths'][i]"
assert expression == expected
results = []
for model, folder in [
    ("raw", "raw-figures-2026-10-17"),
    ("altruistic", "altruistic-figures-2026-10-18"),
    ("egoistic", "egoistic-figures-2026-10-18"),
    ("bentham", "bentham-figures-2026-10-18"),
]:
    source = a.repository / "replications/blueprints_2024/results" / folder
    raw = gzip.decompress((source / "all-cause-deaths.csv.gz").read_bytes())
    data = np.loadtxt(io.BytesIO(raw), delimiter=",", skiprows=1)
    if model == "raw":
        mean_path = (
            a.repository
            / "replications/blueprints_2024/results/raw-timeseries-2026-10-17/independent-means.csv"
        )
        mean_bytes = mean_path.read_bytes()
    else:
        mean_path = source / "timeseries/independent-means.csv.gz"
        mean_bytes = gzip.decompress(mean_path.read_bytes())
    means = np.loadtxt(io.BytesIO(mean_bytes), delimiter=",", skiprows=1)
    assert data.shape == (5001, 6) and means.shape == (5001, 7)
    assert np.array_equal(data[:, 0], means[:, 0]) and np.all(means[:, 1] > 0)
    assert np.all(data[:, 3] == 0)
    ratio = (data[:, 1] + data[:, 2] + data[:, 4]) / means[:, 1]
    assert np.allclose(ratio, data[:, -1], rtol=1e-14, atol=1e-16)
    fig = np.loadtxt(
        io.BytesIO(gzip.decompress((source / f"figure-6-{model}.csv.gz").read_bytes())),
        delimiter=",",
        skiprows=1,
    )
    comparison = json.loads((source / "initial-comparison.json").read_text())[2]
    frame = comparison["frame"]
    indices = fig[:, 0].astype(int)
    expected_y = frame[3] - ratio[indices] / 0.12 * (frame[3] - frame[1])
    errors = np.abs(fig[:, 2] - expected_y)
    assert np.all(errors <= 0.005)
    results.append(
        {
            "model": model,
            "source": str(source.relative_to(a.repository)),
            "deaths_csv_sha256": hashlib.sha256(raw).hexdigest(),
            "means_csv_sha256": hashlib.sha256(mean_bytes).hexdigest(),
            "timesteps": len(data),
            "disease_deaths_zero_at_every_timestep": True,
            "matched_vertices": len(errors),
            "maximum_error_pdf_points": float(errors.max()),
            "threshold_pdf_points": 0.005,
            "final_ratio": float(ratio[-1]),
        }
    )
report = {
    "historical_definition_commit": "cc0408afbb09d8d124ce6f7e6b1844d202d0f8b6",
    "date": "2024-08-23",
    "source_sha256": hashlib.sha256(historical.encode()).hexdigest(),
    "verified_source_expression": expression,
    "definition": "(starvation + combat + aging) / population * 100",
    "all_four_match": True,
    "comparisons": results,
    "scope": "Released definition predates paper submission and is numerically consistent with all four Figure6 curves. Exact historical plotting revision remains unidentified; disease is omitted in this release but is zero throughout these ensembles.",
}
(root / "comparison.json").write_text(json.dumps(report, indent=2) + "\n")
print(
    json.dumps(
        {
            "matched_vertices": sum(x["matched_vertices"] for x in results),
            "all_four_match": True,
        }
    )
)
