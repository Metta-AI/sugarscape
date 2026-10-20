"""Independently recompute raw metrics and test aging inclusion as a diagnostic."""

from pathlib import Path
import hashlib
import json
import sys
import tarfile

import numpy as np

repo, audit_path, metrics_path, output = map(Path, sys.argv[1:])
assert not output.exists()
audit = json.loads(audit_path.read_bytes())
metrics_raw = metrics_path.read_bytes()
metrics = json.loads(metrics_raw)
expected = {r["entry"]: r for r in metrics["runs"]}
groups = {}
for r in audit["runs"]:
    groups.setdefault(r["native_archive"], {})[
        r["manifest_member"].rsplit("/", 1)[0] + "/trajectory.json"
    ] = r
fields = [
    "population",
    "meanWealth",
    "agentMeanTimeToLive",
    "meanAgeAtDeath",
    "agentStarvationDeaths",
    "agentCombatDeaths",
    "agentAgingDeaths",
    "agentDiseaseDeaths",
]
errors = []
results = []
for path, wanted in sorted(groups.items()):
    assert (
        hashlib.sha256((repo / path).read_bytes()).hexdigest()
        == audit["native_archive_sha256"][path]
    )
    seen = set()
    with tarfile.open(repo / path, mode="r|gz") as archive:
        for member in archive:
            if member.name not in wanted:
                continue
            assert member.name not in seen
            seen.add(member.name)
            row = wanted[member.name]
            raw = archive.extractfile(member).read()
            assert hashlib.sha256(raw).hexdigest() == row["trajectory_sha256"]
            records = json.loads(raw)
            matrix = np.array(
                [[r[f] for f in fields] for r in records], dtype=np.float64
            )
            assert (
                matrix.shape == (row["observations"], 8) and np.isfinite(matrix).all()
            )
            values = {}
            aging = {}
            for start, suffix in [(0, "including_initial"), (1, "excluding_initial")]:
                a = matrix[start:]
                positive = a[:, 0] > 0
                for j, field in enumerate(fields[:4]):
                    values[field + "/observed/" + suffix] = float(np.mean(a[:, j]))
                    values[field + "/zero_extended/" + suffix] = float(
                        np.sum(a[:, j]) / (5001 - start)
                    )
                for diagnostic in [False, True]:
                    counts = np.sum(a[:, 4 : 7 if diagnostic else 6], axis=1)
                    rates = counts[positive] / a[positive, 0] * 100
                    target = aging if diagnostic else values
                    target["death_percent/positive_rows/" + suffix] = float(
                        np.mean(rates)
                    )
                    target["death_percent/zero_rows_set_zero/" + suffix] = float(
                        np.sum(rates) / len(a)
                    )
                    target["death_percent/zero_extended/" + suffix] = float(
                        np.sum(rates) / (5001 - start)
                    )
                    target["death_percent/ratio_of_sums/" + suffix] = float(
                        np.sum(counts) / np.sum(a[:, 0]) * 100
                    )
            assert values.keys() == expected[row["entry"]]["values"].keys()
            for key, value in values.items():
                reference = expected[row["entry"]]["values"][key]
                error = abs(value - reference) / max(1, abs(reference))
                assert error < 1e-12
                errors.append(error)
            results.append(
                {
                    "entry": row["entry"],
                    "primary": values,
                    "aging_included_diagnostic": aging,
                    "total_disease_deaths": float(np.sum(matrix[:, 7])),
                }
            )
    assert seen == wanted.keys()
assert len(results) == len({r["entry"] for r in results}) == 100
results.sort(key=lambda r: r["entry"])
primary = {
    key: float(np.median([r["primary"][key] for r in results]))
    for key in results[0]["primary"]
}
for key, value in primary.items():
    assert abs(value - metrics["medians"][key]) / max(1, abs(value)) < 1e-12
aging_medians = {
    key: float(np.median([r["aging_included_diagnostic"][key] for r in results]))
    for key in results[0]["aging_included_diagnostic"]
}
report = {
    "numpy_version": np.__version__,
    "metrics_sha256": hashlib.sha256(metrics_raw).hexdigest(),
    "native_runs": 100,
    "primary_values_checked": len(errors),
    "maximum_scaled_error": max(errors),
    "primary_medians": primary,
    "aging_included_medians": aging_medians,
    "runs": results,
    "scope": "Independent NumPy raw-trajectory arithmetic. Aging inclusion is a measurement diagnostic that contradicts the paper's stated exclusion; it does not replace primary results or establish the author's historical pipeline.",
}
output.write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({k: v for k, v in report.items() if k != "runs"}, indent=2))
