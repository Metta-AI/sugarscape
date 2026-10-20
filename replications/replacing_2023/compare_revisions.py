"""Compare complete native trajectories without excluding changed metrics."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("archive", type=Path)
parser.add_argument("preconference", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
trajectories = []
for directory in [args.archive, args.preconference]:
    data = (directory / "trajectory.json").read_bytes()
    result = json.loads((directory / "result.json").read_text())
    assert hashlib.sha256(data).hexdigest() == result["trajectory_sha256"]
    rows = json.loads(data)
    assert len(rows) == result["observations"]
    assert [r["timestep"] for r in rows] == list(range(len(rows)))
    trajectories.append(rows)
archive, preconference = trajectories
assert len(archive) == len(preconference)
assert all(a.keys() == b.keys() for a, b in zip(archive, preconference, strict=True))
changed = Counter(k for a, b in zip(archive, preconference, strict=True) for k in a if a[k] != b[k])
windows = []
# Descriptive windows, not fitted pass/fail tolerances or a stationarity test.
for start, stop in [(0, 60), (60, 100), (100, 200), (500, 1000), (2000, 2500)]:
    summaries = []
    for rows in trajectories:
        subset = [r for r in rows if start <= r["timestep"] <= stop]
        assert subset
        summaries.append({"minimum": min(r["population"] for r in subset),
                          "maximum": max(r["population"] for r in subset),
                          "mean": sum(r["population"] for r in subset) / len(subset)})
    windows.append({"start": start, "stop": stop, "archive": summaries[0], "preconference": summaries[1]})
report = {"observations_per_revision": len(archive), "changed_fields": dict(changed),
          "population_identical": all(a["population"] == b["population"] for a, b in zip(archive, preconference, strict=True)),
          "windows": windows, "interpretation": "Historical-version diagnostic, not a paper-level equivalence or negative-replication verdict."}
args.output.mkdir(parents=True, exist_ok=False)
(args.output / "comparison.json").write_text(json.dumps(report, indent=2) + "\n")
fig, axes = plt.subplots(2, 1, figsize=(9, 6), sharex=True, constrained_layout=True)
for rows, label, style in [(archive, "December 20 archive", "-"), (preconference, "November 13 pre-conference", "--")]:
    axes[0].plot([r["timestep"] for r in rows], [r["population"] for r in rows], style, label=label, linewidth=1)
axes[0].set_ylabel("Population")
axes[0].legend()
axes[0].set_title("Constrained reproduction, seed 12345 — revision diagnostic")
axes[1].plot([r["timestep"] for r in archive], [a["meanHappiness"] - b["meanHappiness"] for a, b in zip(archive, preconference, strict=True)], linewidth=1)
axes[1].set_ylabel("Mean happiness difference\n(archive − pre-conference)")
axes[1].set_xlabel("Timestep")
fig.savefig(args.output / "revision-comparison.png", dpi=160)
plt.close(fig)
print(json.dumps(report))
