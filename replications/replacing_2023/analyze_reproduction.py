"""Describe audited reproduction trajectories without inventing qualitative verdicts."""
import argparse
import hashlib
import json
from pathlib import Path
import statistics

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("batch", type=Path)
parser.add_argument("audit", type=Path)
parser.add_argument("baseline", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
audit = json.loads((args.audit / "audit.json").read_text())
assert audit["scenario"] == "reproduction_limited" and audit["runs"] == 20 and audit["horizon"] == 2500
manifest = json.loads((args.batch / "manifest.json").read_text())
targets = json.loads(Path(__file__).with_name("published_targets.json").read_text())
assert [r["seed"] for r in audit["results"]] == [r["seed"] for r in targets["table3"]]
assert manifest["revision"] == audit["revision"]
baseline_manifest = json.loads((args.baseline / "manifest.json").read_text())
assert baseline_manifest["release"] == manifest["revision"]
assert baseline_manifest["experiment"] == {"scenario": "reproduction_limited", "seed": targets["baseline_seed"]}
baseline_result = json.loads((args.baseline / "result.json").read_text())
inputs = [(targets["baseline_seed"], "baseline", args.baseline, baseline_result["trajectory_sha256"])]
inputs += [(r["seed"], r["published_qualitative_outcome"], args.batch / f"seed-{r['seed']}", r["trajectory_sha256"]) for r in audit["results"]]
args.output.mkdir(parents=True, exist_ok=False)
figure, axes = plt.subplots(2, 1, figsize=(11, 8), layout="constrained")
results = []
for seed, label, directory, checksum in inputs:
    raw = (directory / "trajectory.json").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == checksum
    run_manifest = json.loads((directory / "manifest.json").read_text())
    assert run_manifest["source_sha256"] == baseline_manifest["source_sha256"]
    assert run_manifest["source_config_sha256"] == baseline_manifest["source_config_sha256"]
    trajectory = json.loads(raw)
    assert [r["timestep"] for r in trajectory] == list(range(2501))
    assert all(r["seed"] == seed for r in trajectory)
    population = [r["population"] for r in trajectory]
    early_peak = max(population[:60])
    dip_window_min = min(population[60:101])
    # These are descriptive measurements, not thresholds for the paper's qualitative labels.
    drawdowns = [max(population[:t + 1]) - population[t] for t in range(60, 101)]
    late = population[2001:2501]
    results.append({"seed": seed, "published_label": label, "trajectory_sha256": checksum,
        "early_peak_0_59": early_peak, "minimum_60_100": dip_window_min,
        "early_peak_minus_window_minimum": early_peak - dip_window_min,
        "largest_running_peak_drawdown_60_100": max(drawdowns),
        "population_at_60": population[60], "population_at_100": population[100],
        "late_mean_2001_2500": statistics.mean(late), "late_population_std_2001_2500": statistics.pstdev(late),
        "late_range_2001_2500": max(late) - min(late), "final_population": population[-1]})
    color = {"baseline": "black", "similar": "#2070b4", "different": "#d95f02"}[label]
    for axis, stop in zip(axes, [2501, 201], strict=True):
        axis.plot(range(stop), population[:stop], color=color, alpha=1 if label == "baseline" else .5,
                  linewidth=2.2 if label == "baseline" else 1, label=label if seed in [12345, 14133, 32209] else None)
for axis in axes:
    axis.axvspan(60, 100, color="gray", alpha=.15)
    axis.set(xlabel="Timestep", ylabel="Population")
axes[0].legend(title="Published qualitative label")
axes[0].set_title("Released implementation: baseline and all twenty published reproduction seeds")
axes[1].set_title("Early trajectory; gray window marks the paper's stated first dip")
figure.savefig(args.output / "population-trajectories.png", dpi=160)
plt.close(figure)
report = {"audit_sha256": hashlib.sha256((args.audit / "audit.json").read_bytes()).hexdigest(),
          "revision": audit["revision"], "runs": len(results), "results": results,
          "interpretation": "Exploratory descriptors, not a predeclared pass/fail classification. The 60–100 window comes from the paper; 2001–2500 is our late-window diagnostic. Exact historical revision and qualitative similarity thresholds remain unresolved. No statistical test or causal conclusion is implied."}
(args.output / "analysis.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
print(json.dumps({"runs": len(results), "baseline": results[0],
    "published_similar_count": sum(r["published_label"] == "similar" for r in results),
    "published_different_count": sum(r["published_label"] == "different" for r in results),
    "early_peak_minus_window_minimum_range": [min(r["early_peak_minus_window_minimum"] for r in results), max(r["early_peak_minus_window_minimum"] for r in results)]}))
