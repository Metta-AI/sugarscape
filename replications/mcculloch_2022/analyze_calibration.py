"""Compare completed calibration experiments with the predeclared targets."""

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import statistics
from typing import Literal

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from calibrate import Trial


class Particle(Trial):
    particle: int
    attempts: int


class LoggedTrial(Trial):
    phase: Literal["ensemble", "wave", "pipeline", "conditional"]
    wave: int = 0
    particle: int = -1
    attempt: int = 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    complete = json.loads((args.input / "complete.json").read_text())
    assert complete["particles_per_experiment"] == 10000
    study = Path(__file__).resolve().parent
    published = json.loads((study / "published_calibration.json").read_text())
    waves = json.loads((args.input / "waves.json").read_text())
    assert len(waves) == complete["waves"]
    original = Counter({tuple(row["parameters"]): row["count"] for row in published["abc_counts"]})
    assert sum(original.values()) == published["abc_particles"] == 10000
    counts = {"published": original}
    summaries = {}
    logged = {}
    history = {}
    with (args.input / "trials.jsonl").open() as stream:
        for line in stream:
            trial = LoggedTrial.model_validate_json(line)
            if trial.phase in ("pipeline", "conditional"):
                key = trial.phase, trial.particle
                logged.setdefault(key, []).append(trial)
            else:
                assert 1 <= trial.wave <= len(waves)
                history.setdefault((trial.phase, trial.wave), []).append(trial)
    assert len(logged) == 20000
    for wave in waves:
        ensemble = history["ensemble", wave["wave"]]
        points = wave["prior"][::math.ceil(len(wave["prior"]) / 4)]
        assert len(ensemble) == 200 * len(points)
        variances = []
        for point in points:
            errors = [abs(trial.final_population - 66) for trial in ensemble
                      if [trial.metabolism, trial.vision] == point]
            assert len(errors) == 200
            variances.append(statistics.variance(errors))
        assert 2 * statistics.mean(variances) == wave["uncertainty"]
        predictions = history["wave", wave["wave"]]
        assert [[trial.metabolism, trial.vision] for trial in predictions] == wave["prior"]
        scores = [abs(trial.final_population - 66) / math.sqrt(wave["uncertainty"]) for trial in predictions]
        assert scores == wave["implausibility"]
        assert [point for point, score in zip(wave["prior"], scores) if score < 3] == wave["retained"]
    assert waves[-1]["prior"] == waves[-1]["retained"]
    assert all(previous["retained"] == following["prior"] for previous, following in zip(waves, waves[1:]))
    for label in ("pipeline", "conditional"):
        rows = [Particle.model_validate_json(line) for line in
                (args.input / f"{label}-particles.jsonl").read_text().splitlines()]
        assert [row.particle for row in rows] == list(range(10000))
        space = waves[-1]["retained"] if label == "pipeline" else published["waves"][-1]["plaus_space"]
        variance = waves[-1]["uncertainty"] if label == "pipeline" else published["waves"][-1]["uncert"]
        for row in rows:
            assert row.attempts >= 1
            assert [row.metabolism, row.vision] in space
            assert abs(row.final_population - 66) <= variance ** 0.5
            trials = logged[label, row.particle]
            assert [trial.attempt for trial in trials] == list(range(1, row.attempts + 1))
            assert all(abs(trial.final_population - 66) > variance ** 0.5 for trial in trials[:-1])
            final_trial = Trial.model_validate(trials[-1].model_dump())
            assert final_trial == Trial.model_validate(row.model_dump())
        current = Counter((row.metabolism, row.vision) for row in rows)
        counts[label] = current
        summaries[label] = {
            "simulator_calls": sum(row.attempts for row in rows),
            "modes": [list(point) for point, count in current.items() if count == max(current.values())],
            "rank_4_6": 1 + sum(count > current[4, 6] for count in current.values()),
            "four_seven_is_modal": current[4, 7] == max(current.values()),
            "counts": [{"parameters": list(point), "count": count} for point, count in sorted(current.items())],
        }
    points = sorted(set(original) | set(counts["conditional"]))
    p = np.array([original[point] for point in points]) / 10000
    q = np.array([counts["conditional"][point] for point in points]) / 10000
    rng = np.random.default_rng(271828)
    p_boot = rng.multinomial(10000, p, size=5000) / 10000
    q_boot = rng.multinomial(10000, q, size=5000) / 10000
    upper = float(np.quantile(np.abs(p_boot - q_boot).sum(axis=1) / 2, .95))
    summaries["conditional"].update({
        "total_variation_distance": float(np.abs(p - q).sum() / 2),
        "bootstrap_95_upper": upper,
        "predeclared_distribution_bound_passed": upper < .05,
    })
    old_prior = {tuple(point) for point in published["waves"][-1]["plaus_space"]}
    new_prior = {tuple(point) for point in waves[-1]["retained"]}
    summaries["history_matching"] = {
        "waves": len(waves), "published_waves": len(published["waves"]),
        "retained": len(new_prior), "published_retained": len(old_prior),
        "only_new": sorted(new_prior - old_prior), "only_published": sorted(old_prior - new_prior),
        "exact_prior_match": new_prior == old_prior,
    }
    files = [args.input / "complete.json", args.input / "waves.json",
             args.input / "trials.jsonl", args.input / "pipeline-particles.jsonl",
             args.input / "conditional-particles.jsonl", study / "published_calibration.json", Path(__file__)]
    summaries["sha256"] = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in files}
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output / "summary.json").write_text(json.dumps(summaries, indent=2) + "\n")
    fig, axes = plt.subplots(1, 3, figsize=(15, 4), constrained_layout=True)
    vmax = max(max(count.values()) / 10000 for count in counts.values())
    for ax, (label, count) in zip(axes, counts.items()):
        values = np.array([[count[m, v] / 10000 for v in range(1, 17)] for m in range(1, 5)])
        plot = ax.imshow(values, origin="lower", vmin=0, vmax=vmax, aspect="auto")
        ax.set(title=label, xlabel="Maximum vision", ylabel="Maximum metabolism")
        ax.set_xticks(range(16), range(1, 17))
        ax.set_yticks(range(4), range(1, 5))
    fig.colorbar(plot, ax=axes, label="Accepted particle fraction")
    fig.savefig(args.output / "posterior.png", dpi=150)
    plt.close(fig)
    print(json.dumps(summaries, indent=2))


if __name__ == "__main__":
    main()
