"""Plot all seeds from a complete audited reconstruction, masking empty populations."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("audit", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
audit_bytes = (args.audit / "audit.json").read_bytes()
audit = json.loads(audit_bytes)
assert audit["complete_ensemble"] and audit["mode"] == "complete"
assert audit["validated_runs"] == len(audit["runs"]) == 150
assert {(r["protocol"], r["threshold"], r["seed"]) for r in audit["runs"]} == {
    (model, threshold, seed) for model in ("paper-com0", "paper-com1", "paper-com2") for threshold in range(5) for seed in range(10)}
args.output.mkdir(parents=True, exist_ok=False)
cycles = np.arange(1, 2001)
for model in ("paper-com0", "paper-com1", "paper-com2"):
    fig, axes = plt.subplots(5, 4, figsize=(16, 13), sharex=True)
    metric_fig, metric_axes = plt.subplots(5, 3, figsize=(13, 13), sharex=True, sharey=True)
    for run in (r for r in audit["runs"] if r["protocol"] == model):
        path = args.audit / run["name"]
        manifest = json.loads((path / "manifest.json").read_text())
        series = {}
        for metric in ("numberOfAgents.avg", "cooperating.avg", "talkPref.avg", "listenPref.avg"):
            relative = "data/experiment_0_." + metric
            raw = gzip.decompress((path / (Path(relative).name + ".gz")).read_bytes())
            assert hashlib.sha256(raw).hexdigest() == manifest["output_sha256"][relative]
            series[metric] = np.array([float(line.split()[1]) for line in raw.decode().splitlines()])
            assert len(series[metric]) == 2000
        population = series["numberOfAgents.avg"]
        for metric in ("cooperating.avg", "talkPref.avg", "listenPref.avg"):
            series[metric][population == 0] = np.nan
        log = gzip.decompress((path / "run.log.gz").read_bytes())
        assert hashlib.sha256(log).hexdigest() == run["log_sha256"]
        counts = np.array([list(map(int, line.split(',')[1:])) for line in log.decode().splitlines() if line.startswith("harvest-counts,")])
        assert counts.shape == (2000, 5) and np.array_equal(counts[:, 0], np.arange(2000))
        event_fraction = np.divide(counts[:, 2], counts[:, 1], out=np.full(2000, np.nan), where=counts[:, 1] > 0)
        consumer_fraction = np.divide(counts[:, 4], counts[:, 3], out=np.full(2000, np.nan), where=counts[:, 3] > 0)
        threshold = run["threshold"]
        color = plt.get_cmap("tab10")(run["seed"])
        for column, values in enumerate((population, event_fraction, series["talkPref.avg"], series["listenPref.avg"])):
            axes[threshold, column].plot(cycles, values, color=color, linewidth=0.45, alpha=0.7)
        for column, values in enumerate((series["cooperating.avg"], event_fraction, consumer_fraction)):
            metric_axes[threshold, column].plot(cycles, values, color=color, linewidth=0.45, alpha=0.7)
    for threshold in range(5):
        axes[threshold, 0].set_ylabel(f"CT={threshold}\nPopulation")
        metric_axes[threshold, 0].set_ylabel(f"CT={threshold}\nFraction")
        for column in range(1, 4):
            axes[threshold, column].set_ylim(-0.03, 1.03)
        for axis in (*axes[threshold], *metric_axes[threshold]):
            axis.set_xlim(0, 2000)
            axis.grid(alpha=0.2)
        for axis in metric_axes[threshold]:
            axis.set_ylim(-0.03, 1.03)
    for column, title in enumerate(("Population", "Shared harvest events / all events", "Mean talk preference", "Mean listen preference")):
        axes[0, column].set_title(title, fontsize=10)
    for column, title in enumerate(("Native cooperating-agent mean", "Shared events / all harvest events", "Shared participants / all participants")):
        metric_axes[0, column].set_title(title, fontsize=10)
    for figure, grid, suffix, subtitle in ((fig, axes, "trajectories", "Ten seeds per threshold; undefined ratios and extinct-agent preferences masked"),
                                          (metric_fig, metric_axes, "cooperation", "Three measurement definitions; all ten seeds shown separately")):
        for axis in grid[-1]:
            axis.set_xlabel("Cycle")
        figure.suptitle(f"{model}: specification reconstruction\n{subtitle}", fontsize=12)
        figure.legend([plt.Line2D([], [], color=plt.get_cmap("tab10")(seed), label=f"Seed {seed}") for seed in range(10)],
                      [f"Seed {seed}" for seed in range(10)], loc="lower center", ncol=10, frameon=False)
        figure.tight_layout(rect=(0, 0.025, 1, 0.955))
        figure.savefig(args.output / f"{model}-{suffix}.png", dpi=150)
        plt.close(figure)
(args.output / "manifest.json").write_text(json.dumps({"audit_sha256": hashlib.sha256(audit_bytes).hexdigest(),
    "matplotlib": matplotlib.__version__, "numpy": np.__version__, "runs": 150,
    "scope": "Reconstruction trajectories, not digitized publication overlays. Colors identify seeds0–9 within each panel."}, indent=2) + "\n")
