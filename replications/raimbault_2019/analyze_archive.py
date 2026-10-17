"""Independently recompute the Sugarscape spatial distances in Table 4."""

import argparse
from collections import defaultdict
import csv
import hashlib
import json
from pathlib import Path

import numpy as np

TARGETS = {
    1: [0.07184, 0.13996, 0.39816, 0.42452, 0.64751, 1.13169],
    2: [0.08909, 0.19794, 1.52272, 1.29594, 2.16371, 2.98273],
    3: [0.1025, 0.2288, 3.1495, 2.5074, 4.2718, 5.5378],
    10: [0.1540, 0.4466, 9.8757, 7.6246, 13.0550, 16.8001],
}
PARAMETERS = ("population", "minSugar", "maxSugar")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reference", type=Path)
    parser.add_argument("generated", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    reference = defaultdict(list)
    with args.reference.open() as stream:
        for row in csv.DictReader(stream):
            key = tuple(float(row[name]) for name in PARAMETERS)
            reference[key].append(float(row["mwgini"]))
    means = {key: float(np.mean(values)) for key, values in reference.items()}
    grids = defaultdict(dict)
    with args.generated.open() as stream:
        for row in csv.DictReader(stream):
            key = tuple(float(row[name]) for name in PARAMETERS)
            grid = grids[int(row["id"])]
            assert key not in grid
            grid[key] = float(row["gini"])
    assert set(grids) == set(range(50))
    distances = {q: [] for q in TARGETS}
    coverage = []
    for identity, grid in sorted(grids.items()):
        keys = sorted(set(means) & set(grid))
        x = np.array([means[key] for key in keys])
        y = np.array([grid[key] for key in keys])
        finite = np.isfinite(x) & np.isfinite(y)
        coverage.append({"grid": identity, "available": len(grid), "shared": len(keys),
                         "finite": int(finite.sum()), "missing_reference_keys": len(set(means) - set(grid))})
        x, y = x[finite], y[finite]
        assert len(x) > 1
        denominator = x.var(ddof=1) + y.var(ddof=1)
        assert denominator > 0
        for q in TARGETS:
            distance = np.mean(np.abs(x - y) ** q) ** (1 / q)
            distances[q].append(float(2 * distance ** 2 / denominator))
    comparison = []
    for q, values in distances.items():
        quantiles = np.quantile(values, [0, .25, .5, .75, 1])
        measured = [*quantiles[:3], float(np.mean(values)), *quantiles[3:]]
        digits = 5 if q in (1, 2) else 4
        comparison.append({"q": q, "published": TARGETS[q], "measured": measured,
                           "matches_at_published_precision": [round(float(a), digits) == b
                                                              for a, b in zip(measured, TARGETS[q])]})
    report = {"reference_parameter_points": len(means), "reference_simulations": sum(map(len, reference.values())),
              "generated_parameter_points": sum(map(len, grids.values())),
              "columns": ["minimum", "first_quartile", "median", "mean", "third_quartile", "maximum"],
              "comparison": comparison, "coverage": coverage, "distances": distances,
              "sha256": {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                         for path in (args.reference, args.generated, Path(__file__))},
              "status": "Archived-data reanalysis only; fresh simulation replication unfinished."}
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output / "results.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(comparison, indent=2))


if __name__ == "__main__":
    main()
