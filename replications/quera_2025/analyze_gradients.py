"""Analyze the prespecified 256-seed native gradient ensemble after its full audit."""

import csv
import hashlib
import json
from pathlib import Path
import statistics
import sys

from scipy.stats import t

root = Path(sys.argv[1])
audit_path = Path(sys.argv[2])
output = Path(sys.argv[3])
protocol = json.loads((root / "protocol.json").read_text())
audit = json.loads(audit_path.read_text())
assert protocol["seeds"] == list(range(3, 259))
assert protocol["finite_difference_steps"] == [0.001, 0.01, 0.05]
assert audit["rows"] == 115200
series = {}
for seed in protocol["seeds"]:
    path = root / f"seed-{seed}.csv"
    assert (
        hashlib.sha256(path.read_bytes()).hexdigest()
        == audit["source_sha256"][path.name]
    )
    with path.open() as stream:
        for row in csv.DictReader(stream):
            key = (int(row["parameter"]), float(row["step"]), int(row["time"]))
            series.setdefault(key, []).append(
                (seed, float(row["ad"]), float(row["fd"]))
            )
results = []
for (parameter, step, time), rows in sorted(series.items()):
    assert [row[0] for row in rows] == protocol["seeds"]
    values = {
        "ad": [row[1] for row in rows],
        "fd": [row[2] for row in rows],
        "paired_difference": [row[1] - row[2] for row in rows],
    }
    record = {
        "parameter": protocol["parameters"][parameter - 1],
        "step": step,
        "time": time,
        "seeds": len(rows),
    }
    for name, samples in values.items():
        mean = statistics.mean(samples)
        se = statistics.stdev(samples) / len(samples) ** 0.5
        radius = float(t.ppf(0.975, len(samples) - 1)) * se
        record[name] = {
            "mean": mean,
            "standard_error": se,
            "ci95": [mean - radius, mean + radius],
            "first_half_mean": statistics.mean(samples[:128]),
            "second_half_mean": statistics.mean(samples[128:]),
        }
    results.append(record)
output.mkdir(exist_ok=False)
(output / "comparison.json").write_text(
    json.dumps(
        {
            "protocol_sha256": hashlib.sha256(
                (root / "protocol.json").read_bytes()
            ).hexdigest(),
            "audit_sha256": hashlib.sha256(audit_path.read_bytes()).hexdigest(),
            "interpretation": "Pointwise Student-t intervals across independent seeds; AD/FD differences are paired. No simultaneous coverage or whole-paper decision. Half-ensemble means diagnose stability; step sensitivity requires comparison across all three steps.",
            "results": results,
        },
        indent=2,
    )
    + "\n"
)
print(json.dumps([row for row in results if row["time"] == 24], indent=2))
