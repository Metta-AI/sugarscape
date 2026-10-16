"""Validate complete growth ensembles and execute the declared logistic fit."""
import argparse
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path

import numpy as np
import scipy
from scipy.optimize import least_squares
from scipy.special import expit
from scipy.stats import t as student_t


def residual(parameters, cycles, population):
    capacity, rate = np.exp(parameters[:2])
    return capacity * expit(rate * (cycles - parameters[2])) - population


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("run", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
manifest = json.loads((args.run / "manifest.json").read_text())
assert manifest["cycles"] == 3000 and manifest["record_every"] == 1
assert manifest["seeds"] == list(range(1, 101))
assert manifest["scenarios"] == {"low-fertility": [85, 0], "birth-cost": [10, 40]}
for filename, key in [("simulate.cpp", "source_sha256"), ("run_growth.py", "runner_sha256"),
                      ("GROWTH_PROTOCOL.md", "protocol_sha256")]:
    assert hashlib.sha256(Path(__file__).with_name(filename).read_bytes()).hexdigest() == manifest[key]
records = [json.loads(line) for line in (args.run / "completed.jsonl").read_text().splitlines()]
assert [(r["scenario"], r["seed"]) for r in records] == [
    (scenario, seed) for scenario in manifest["scenarios"] for seed in manifest["seeds"]]
results = []
observations = 0
shared_observations = 0
for record in records:
    scenario, seed = record["scenario"], record["seed"]
    raw = (args.run / f"{scenario}-{seed}.csv").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == record["trajectory_sha256"]
    rows = list(csv.DictReader(io.StringIO(raw.decode())))
    values = np.array([[float(v) for v in row.values()] for row in rows])
    assert np.isfinite(values).all()
    cycles = np.array([int(row["cycle"]) for row in rows])
    population = np.array([int(row["population"]) for row in rows])
    assert np.array_equal(cycles, np.arange(1, len(rows) + 1))
    assert len(rows) == 3000 or population[-1] == 0
    assert ((population >= 0) & (population <= 2500)).all()
    previous = 1
    for row, count in zip(rows, population):
        assert count == previous + int(row["births"]) - int(row["deaths"])
        assert int(row["conservation_error"]) == 0
        previous = count
    historical = Path(__file__).parent / "results" / f"{scenario}-ensemble-2026-10-15"
    old_raw = gzip.decompress((historical / f"seed-{seed}.csv.gz").read_bytes())
    old_ledger = [json.loads(line) for line in (historical / "completed.jsonl").read_text().splitlines()]
    old_record = next(r for r in old_ledger if r["seed"] == seed)
    assert hashlib.sha256(old_raw).hexdigest() == old_record["trajectory_sha256"]
    for old_row in csv.DictReader(io.StringIO(old_raw.decode())):
        cycle = int(old_row["cycle"])
        if cycle <= len(rows):
            assert old_row == rows[cycle - 1], (scenario, seed, cycle)
            shared_observations += 1
    observations += len(rows)
    result = {"scenario": scenario, "seed": seed, "extinct": bool(population[-1] == 0), "attempts": []}
    if population[-1] != 0:
        crossings = cycles[population >= 400]
        midpoint = float(crossings[0]) if len(crossings) else 1500.0
        for rate in (0.005, 0.02, 0.05):
            fit = least_squares(residual, [np.log(833.3333333333334), np.log(rate), midpoint],
                                args=(cycles, population))
            capacity, fitted_rate = np.exp(fit.x[:2])
            result["attempts"].append({"initial_rate": rate, "success": bool(fit.success),
                "status": int(fit.status), "message": fit.message, "K": float(capacity),
                "r": float(fitted_rate), "midpoint": float(fit.x[2]),
                "sse": float(np.dot(fit.fun, fit.fun)), "evaluations": int(fit.nfev)})
        converged = [a for a in result["attempts"] if a["success"] and
                     np.isfinite([a["K"], a["r"], a["midpoint"], a["sse"]]).all()]
        if converged:
            result["selected"] = min(converged, key=lambda a: a["sse"])
            result["rmse"] = float(np.sqrt(result["selected"]["sse"] / len(rows)))
    result["fit_completed"] = "selected" in result
    results.append(result)
summaries = {}
for scenario, target in [("low-fertility", 0.018), ("birth-cost", 0.032)]:
    fits = [r for r in results if r["scenario"] == scenario and r["fit_completed"]]
    summary = {"requested": 100, "fitted": len(fits), "paper_r": target}
    if len(fits) == 100:
        for metric in ("r", "K", "midpoint"):
            data = np.array([r["selected"][metric] for r in fits])
            mean, sd = float(data.mean()), float(data.std(ddof=1))
            halfwidth = float(student_t.ppf(0.975, 99) * sd / 10)
            summary[metric] = {"mean": mean, "sd": sd, "ci95": [mean-halfwidth, mean+halfwidth]}
        summary["r_difference"] = summary["r"]["mean"] - target
        summary["r_relative_difference"] = summary["r_difference"] / target
    summaries[scenario] = summary
args.output.mkdir(parents=True, exist_ok=False)
report = {"observations": observations, "shared_observations_exact": shared_observations,
          "numpy": np.__version__, "scipy": scipy.__version__, "summaries": summaries, "fits": results,
          "scope": "Declared diagnostic, not recovered author fitting protocol or full paper replication."}
(args.output / "analysis.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
print(json.dumps(summaries, indent=2))
