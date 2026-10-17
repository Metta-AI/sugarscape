"""Quantify the native initialization law against the paper's stated Beta law."""

import argparse
import csv
import hashlib
import json
from pathlib import Path
import statistics
import subprocess

import numpy as np
from scipy.special import beta, betainc

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("source", type=Path)
parser.add_argument("trace", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
assert (
    subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=args.source, text=True
    ).strip()
    == "9178eccd56dd352e3515e276239654239f8d3b41"
)
assert not subprocess.check_output(
    ["git", "status", "--porcelain", "--untracked-files=no"], cwd=args.source, text=True
).strip()
source = (args.source / "src/diff_utils.jl").read_text()
assert source.count("return (1 .- u .^ (1 / dist.beta)) .^ (1 / dist.alpha)") == 2
initializer = (args.source / "src/SugarScape.jl").read_text()
assert "metabolic_rate = 2.0 + 2 * rand(metabolic_rate_dist)" in initializer
assert "wealth = 6 + 19 * rand(wealth_dist)" in initializer
recorded = {
    line.split()[1]: line.split()[0]
    for line in (args.trace / "sha256.txt").read_text().splitlines()
}
configuration = (args.trace / "configuration.txt").read_bytes()
assert hashlib.sha256(configuration).hexdigest() == recorded["configuration.txt"]
assert b"metabolism_beta=2,5;wealth_beta=5,2;" in configuration
observed = {"metabolism": [], "wealth": []}
input_hashes = {}
for seed in range(3):
    parameters = args.trace / f"seed-{seed}-parameters.csv"
    agents = args.trace / f"seed-{seed}-agents.csv"
    for path in [parameters, agents]:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        assert digest == recorded[path.name]
        input_hashes[str(path)] = digest
    with parameters.open() as stream:
        by_agent = {}
        for row in csv.DictReader(stream):
            identifier = int(row["agent"])
            by_agent.setdefault(identifier, set()).add(float(row["metabolism"]))
    assert set(by_agent) == set(range(1, 101)) and all(
        len(v) == 1 for v in by_agent.values()
    )
    with agents.open() as stream:
        initial = [r for r in csv.DictReader(stream) if r["time"] == "0"]
    assert [int(r["agent"]) for r in initial] == list(range(1, 101))
    observed["metabolism"].extend(next(iter(by_agent[i])) for i in range(1, 101))
    observed["wealth"].extend(float(r["wealth"]) for r in initial)
for path in [args.source / "src/diff_utils.jl", args.source / "src/SugarScape.jl"]:
    input_hashes[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
grid = np.linspace(0, 1, 100001)
results = {}
cdf_rows = []
for name, a, b, offset, scale in [("metabolism", 2, 5, 2, 2), ("wealth", 5, 2, 6, 19)]:
    values = np.array(observed[name])
    normalized = (values - offset) / scale
    assert len(values) == 300 and np.all((normalized > 0) & (normalized < 1))
    native_cdf = 1 - (1 - grid**a) ** b
    paper_cdf = betainc(a, b, grid)
    native_mean = b * beta(1 + 1 / a, b)
    native_second = b * beta(1 + 2 / a, b)
    paper_mean = a / (a + b)
    paper_variance = a * b / ((a + b) ** 2 * (a + b + 1))
    maximum = int(np.argmax(np.abs(native_cdf - paper_cdf)))
    results[name] = {
        "alpha": a,
        "beta": b,
        "offset": offset,
        "scale": scale,
        "native_unit_mean": native_mean,
        "beta_unit_mean": paper_mean,
        "native_scaled_mean": offset + scale * native_mean,
        "beta_scaled_mean": offset + scale * paper_mean,
        "native_scaled_variance": scale**2 * (native_second - native_mean**2),
        "beta_scaled_variance": scale**2 * paper_variance,
        "grid_max_cdf_difference": float(abs(native_cdf[maximum] - paper_cdf[maximum])),
        "grid_max_location": float(grid[maximum]),
        "observed_agents": len(values),
        "observed_mean": statistics.fmean(values),
    }
    for index in range(0, len(grid), 100):
        cdf_rows.append(
            {
                "parameter": name,
                "unit_value": float(grid[index]),
                "native_cdf": float(native_cdf[index]),
                "beta_cdf": float(paper_cdf[index]),
                "empirical_cdf": float(np.mean(normalized <= grid[index])),
            }
        )
result = {
    "input_sha256": input_hashes,
    "distribution_derivation": "For U uniform(0,1), X=(1-U^(1/b))^(1/a) has F(x)=1-(1-x^a)^b and E[X^r]=b*B(1+r/a,b). This is the native formula, not the Beta(a,b) CDF.",
    "parameters": results,
    "cdf_grid_points": len(grid),
    "scope": "Analytic source-law comparison and descriptive initialization from three previously validated full native trajectories. Offsets/scales are held at native values to isolate distribution choice. No simulation correction, fitted posterior, statistical rejection, or paper-level replication verdict.",
}
args.output.mkdir(parents=True, exist_ok=False)
(args.output / "analysis.json").write_text(
    json.dumps(result, indent=2, allow_nan=False) + "\n"
)
with (args.output / "cdfs.csv").open("x") as stream:
    writer = csv.DictWriter(stream, fieldnames=list(cdf_rows[0]))
    writer.writeheader()
    writer.writerows(cdf_rows)
print(json.dumps(results, indent=2))
