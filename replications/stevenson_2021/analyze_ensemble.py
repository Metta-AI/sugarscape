"""Validate all 100 completed runs and compare the declared late-time windows."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from pydantic import BaseModel, Field
from scipy.stats import t

from run_ensemble import Experiment


class Completion(BaseModel):
    seed: int = Field(ge=1, le=100)
    command: list[str]
    elapsed_seconds: float = Field(gt=0)
    trajectory_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    assert not args.output.exists()
    manifest = json.loads((args.input / "manifest.json").read_text())
    experiment = Experiment.model_validate(manifest["experiment"])
    completions = [Completion.model_validate_json(line) for line in (args.input / "completed.jsonl").read_text().splitlines()]
    assert [record.seed for record in completions] == list(range(1, 101)), "All 100 successful runs are required"
    assert {p.name for p in args.input.glob("seed-*.csv") if not p.name.endswith("-observations.csv")} == {f"seed-{seed}.csv" for seed in range(1, 101)}
    metrics = ("population", "wealth", "mean_age", "gini")
    columns = ("cycle", *metrics, "landscape", "births", "deaths", "growth", "metabolism", "death_loss", "birth_loss", "conservation_error")
    per_seed = []
    extinct = []
    for record in completions:
        path = args.input / f"seed-{record.seed}.csv"
        assert hashlib.sha256(path.read_bytes()).hexdigest() == record.trajectory_sha256
        expected_parameters = ["85", "0"] if experiment.scenario == "low-fertility" else ["10", "40"]
        assert record.command[1:5] == [str(record.seed), *expected_parameters, str(experiment.cycles)]
        # Retained research manifests cover three recorded CLI versions. Preserve their readers.
        assert record.command[5:] in [[], ["100"], ["100", str((args.input / f"seed-{record.seed}-observations.csv").resolve())]]
        data = np.genfromtxt(path, delimiter=",", names=True)
        assert data.dtype.names == columns
        data = np.atleast_1d(data)
        assert all(np.isfinite(data[column]).all() for column in columns)
        final_cycle = int(data["cycle"][-1])
        assert 1 <= final_cycle <= experiment.cycles
        expected_cycles = sorted({1, final_cycle, *range(100, final_cycle + 1, 100)})
        np.testing.assert_array_equal(data["cycle"], expected_cycles)
        for column in columns:
            if column not in ("mean_age", "gini"):
                np.testing.assert_array_equal(data[column], np.floor(data[column]))
                assert (data[column] >= 0).all()
        assert (data["population"] <= 2500).all() and (data["landscape"] <= 10000).all()
        assert ((data["gini"] >= 0) & (data["gini"] <= 1)).all()
        assert (data["mean_age"] >= 0).all() and (data["conservation_error"] == 0).all()
        assert final_cycle == experiment.cycles or data["population"][-1] == 0
        result = {"seed": record.seed, "observations": len(data), "final_cycle": final_cycle,
                  "terminal": {metric: float(data[metric][-1]) for metric in metrics},
                  "trajectory_sha256": record.trajectory_sha256}
        if data["population"][-1] == 0:
            extinct.append(record.seed)
            result["windows"] = "Undefined for extinct societies; retain the run, do not condition aggregate results on survival"
        else:
            result["windows"] = {}
            for label, start, stop in [("earlier", 50000, 75000), ("later", 75000, 100000)]:
                selected = (data["cycle"] > start) & (data["cycle"] <= stop)
                assert int(selected.sum()) == 250
                result["windows"][label] = {metric: float(data[metric][selected].mean()) for metric in metrics}
        per_seed.append(result)
    summary = {"experiment": experiment.model_dump(), "validated_runs": len(per_seed),
               "extinct_seeds": extinct, "per_seed": per_seed,
               "interpretation": "Descriptive window comparison; no paper-level equivalence criterion or historical-code validation"}
    if extinct:
        summary["aggregate_status"] = "Not computed: extinction makes mean age and Gini undefined; no failed society is silently excluded"
    else:
        summary["aggregate_status"] = "All 100 seeds included; Student-t intervals treat seeds, not time samples, as independent"
        summary["statistics"] = {}
        critical = float(t.ppf(0.975, 99))
        for metric in metrics:
            earlier = np.array([row["windows"]["earlier"][metric] for row in per_seed])
            later = np.array([row["windows"]["later"][metric] for row in per_seed])
            summary["statistics"][metric] = {}
            for label, values in [("earlier", earlier), ("later", later), ("paired_change", later - earlier)]:
                mean, sd = float(values.mean()), float(values.std(ddof=1))
                half_width = critical * sd / np.sqrt(100)
                summary["statistics"][metric][label] = {"mean": mean, "sd": sd, "ci95": [mean - half_width, mean + half_width]}
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output / "analysis.json").write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n")
    print(f"Validated {len(per_seed)} complete trajectories; extinctions: {len(extinct)}")


if __name__ == "__main__":
    main()
