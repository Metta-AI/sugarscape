"""Validate recorded experiments and render the model-comparison evidence."""

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from run import PARAMETERS, PUBLISHED_VARIANCES, Run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    runs = []
    input_hashes = {}
    for path in args.inputs:
        data = path.read_bytes()
        input_hashes[str(path)] = hashlib.sha256(data).hexdigest()
        runs.extend(Run.model_validate_json(line) for line in data.splitlines())
    keys = [(r.engine, r.max_metabolism, r.max_vision, r.seed) for r in runs]
    assert len(keys) == len(set(keys)), "Duplicate seeds within an experiment"
    assert {r.engine for r in runs} == {"author-mesa", "dtl"}
    (args.output / "runs.jsonl").write_text("".join(r.model_dump_json() + "\n" for r in runs))
    rng = np.random.default_rng(314159)
    fig, axes = plt.subplots(2, 3, figsize=(13, 7), sharex="row", sharey="row")
    summaries = []
    for column, ((metabolism, vision), published) in enumerate(zip(PARAMETERS, PUBLISHED_VARIANCES)):
        for engine, color in (("author-mesa", "#2563a6"), ("dtl", "#b84a31")):
            group = sorted([r for r in runs if (r.engine, r.max_metabolism, r.max_vision)
                            == (engine, metabolism, vision)], key=lambda r: r.seed)
            assert len(group) >= 30
            assert [r.seed for r in group] == list(range(len(group)))
            populations = np.array([r.population for r in group])
            values = populations[:, 30]
            bootstrap = rng.choice(values, size=(5000, len(group)), replace=True)
            variance_interval = np.quantile(np.var(bootstrap, axis=1, ddof=1), [0.025, 0.975])
            summary = {
                "engine": engine, "max_metabolism": metabolism, "max_vision": vision,
                "seeds": len(group), "mean_population_30": float(values.mean()),
                "sample_variance_30": float(values.var(ddof=1)),
                "bootstrap_variance_95_interval": variance_interval.tolist(),
                "published_variance": published,
                "stable_first_30": int(np.all(populations[:30, 30:] == populations[:30, 30:31], axis=1).sum()),
                "initial_population_range": [int(populations[:, 0].min()), int(populations[:, 0].max())],
            }
            summaries.append(summary)
            for trajectory in populations[:30]:
                axes[0, column].plot(trajectory, color=color, alpha=0.08, linewidth=0.7)
            axes[0, column].plot(populations.mean(axis=0), color=color, label=f"{engine} (n={len(group)})")
            axes[1, column].plot(np.arange(30, 101), populations[:30, 30:].T - populations[:30, 30],
                                 color=color, alpha=0.2)
        axes[0, column].set_title(f"Maximum metabolism {metabolism}, vision {vision}")
        axes[0, column].axvline(30, color="black", linestyle="--", linewidth=0.7)
        axes[0, column].legend(fontsize=8)
        axes[1, column].axhline(0, color="black", linewidth=0.7)
        axes[1, column].set_xlabel("Simulation step")
    axes[0, 0].set_ylabel("Population")
    axes[1, 0].set_ylabel("Population change since step 30")
    fig.suptitle("McCulloch et al. (2022) audit — models are not yet equivalent", fontsize=14)
    fig.tight_layout()
    fig.savefig(args.output / "population.png", dpi=160)
    plt.close(fig)
    (args.output / "summary.json").write_text(json.dumps({
        "input_sha256": input_hashes, "bootstrap_seed": 314159,
        "analysis_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "bootstrap_resamples": 5000, "results": summaries,
    }, indent=2) + "\n")
    lines = ["# Recorded audit results", "", "Status: **discrepancy; no completed paper replication**.", "",
             "| Model | Max metabolism, vision | Seeds | Mean population at 30 | Variance | Bootstrap 95% variance interval | Published variance | Stable runs / first 30 |",
             "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for result in summaries:
        lower, upper = result["bootstrap_variance_95_interval"]
        lines.append(f"| {result['engine']} | {result['max_metabolism']}, {result['max_vision']} | "
                     f"{result['seeds']} | {result['mean_population_30']:.3f} | {result['sample_variance_30']:.3f} | "
                     f"[{lower:.3f}, {upper:.3f}] | {result['published_variance']} | {result['stable_first_30']}/30 |")
    lines.extend(["", "Intervals describe Monte Carlo uncertainty of these new runs; they do not establish model equivalence.",
                  "The original paper's seed-level observations are unavailable. The two models have different semantics.",
                  "These comparisons cannot validate the unimplemented history-matching and posterior experiments.", "",
                  "Thin lines show the first 30 runs; thick lines show means over all recorded seeds.", "",
                  "![Population trajectories and post-step-30 changes](population.png)", ""])
    (args.output / "RESULTS.md").write_text("\n".join(lines))


if __name__ == "__main__":
    main()
