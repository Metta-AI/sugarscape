"""Repeat every independent ensemble size used for Figure 4."""

import argparse
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from calibrate import evaluate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    study = Path(__file__).resolve().parent
    published = json.loads((study / "published_variance.json").read_text())
    files = [Path(__file__), study / "independent.py", study / "calibrate.py",
             study / "published_variance.json", study / "VARIANCE_PROTOCOL.md"]
    (args.output / "provenance.json").write_text(json.dumps({
        "command": sys.argv, "python": sys.version,
        "revision": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "working_tree": subprocess.check_output(["git", "status", "--porcelain"], text=True),
        "sha256": {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in files},
    }, indent=2) + "\n")
    seed = 10000000
    rng = np.random.default_rng(161803)
    summaries = []
    fig, axes = plt.subplots(1, 3, figsize=(14, 4), constrained_layout=True)
    with ProcessPoolExecutor(args.workers) as pool, (args.output / "runs.jsonl").open("w") as log:
        for axis, (metabolism, vision) in zip(axes, ((1, 1), (2, 10), (4, 7))):
            group = []
            for size, reported in zip(published["K"], published[f"Y_{metabolism}_{vision}"]):
                tasks = [(value, metabolism, vision) for value in range(seed, seed + size)]
                seed += size
                results = list(pool.map(evaluate, tasks))
                for result in results:
                    log.write(json.dumps({"ensemble_size": size, **result.model_dump()}) + "\n")
                log.flush()
                population = np.array([result.final_population for result in results])
                bootstrap = rng.choice(population, size=(5000, size), replace=True).var(axis=1, ddof=1)
                interval = np.quantile(bootstrap, [.025, .975]).tolist()
                row = {"metabolism": metabolism, "vision": vision, "ensemble_size": size,
                       "published_variance": reported, "variance": float(population.var(ddof=1)),
                       "bootstrap_95_interval": interval}
                group.append(row)
                summaries.append(row)
                print(f"({metabolism},{vision}) n={size}: variance {row['variance']:.4f}", flush=True)
            sizes = [row["ensemble_size"] for row in group]
            axis.plot(sizes, [row["published_variance"] for row in group], label="Published source")
            axis.plot(sizes, [row["variance"] for row in group], label="Independent runs")
            axis.fill_between(sizes, [row["bootstrap_95_interval"][0] for row in group],
                              [row["bootstrap_95_interval"][1] for row in group], alpha=.15)
            axis.set(title=f"Maximum metabolism {metabolism}, vision {vision}",
                     xlabel="Independent ensemble size", ylabel="Population variance at step 30")
            axis.legend()
    (args.output / "summary.json").write_text(json.dumps(summaries, indent=2) + "\n")
    fig.savefig(args.output / "variance.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    main()
