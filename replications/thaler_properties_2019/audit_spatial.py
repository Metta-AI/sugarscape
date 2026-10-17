"""Audit native spatial exports against unchanged trajectories and every-step summaries."""

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("root", type=Path)
parser.add_argument("original", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
protocol = json.loads((args.root / "protocol.json").read_text())
assert json.loads((args.root / "complete.json").read_text()) == {
    "completed_cases": 3,
    "reference_cases": 2,
}
for name, digest in protocol["original"]["source_sha256"].items():
    assert (
        hashlib.sha256((args.root / "source" / name).read_bytes()).hexdigest() == digest
    )
    assert (
        hashlib.sha256((args.original / "source" / name).read_bytes()).hexdigest()
        == digest
    )
old = (args.original / "Observe.hs").read_text()
assert (
    hashlib.sha256(old.encode()).hexdigest() == protocol["original"]["observer_sha256"]
)
expected = old.replace(
    '    ("mkParamsAnimationII_6", mkParamsAnimationII_6),',
    '    ("mkParamsAnimationII_6", mkParamsAnimationII_6),\n    ("migrationVision15", mkParamsAnimationII_6 { spVisionRange = (1, 15) }),',
)
expected = expected.replace(
    "  when (t == 0 || t == steps) $", "  when (t `mod` stride == 0 || t == steps) $"
)
assert (args.root / "Observe.hs").read_text() == expected
assert hashlib.sha256(expected.encode()).hexdigest() == protocol["observer_sha256"]
assert (
    hashlib.sha256((args.original / "observe").read_bytes()).hexdigest()
    == protocol["original"]["binary_sha256"]
)
steps, stride = protocol["steps"], protocol["stride"]
frames = list(range(0, steps + 1, stride))
assert frames[-1] == steps
results = []
spatial_data = {}
for label, constructor in protocol["cases"] + [protocol["additional_case"]]:
    root = args.root / "spatial"
    assert not (root / f"{label}.stderr.log").read_bytes()
    assert not (root / f"{label}.stdout.log").read_bytes()
    scenario = (root / f"{label}.scenario.txt").read_text()
    assert scenario.startswith(
        f"Constructor: {constructor}\nSeed: {protocol['seed']}\n"
    )
    if label != "migration_vision15":
        for suffix in ["summary.csv", "agents.csv", "trades.csv", "scenario.txt"]:
            assert (root / f"{label}.{suffix}").read_bytes() == (
                args.root / "reference" / f"{label}.{suffix}"
            ).read_bytes(), (label, suffix)
    summaries = list(csv.DictReader((root / f"{label}.summary.csv").open()))
    assert [int(r["time"]) for r in summaries] == list(range(steps + 1))
    assert all(math.isfinite(float(v)) for r in summaries for v in r.values())
    agents = {t: {} for t in frames}
    for row in csv.DictReader((root / f"{label}.agents.csv").open()):
        t, aid = int(row["time"]), int(row["id"])
        assert t in agents and aid not in agents[t]
        assert all(math.isfinite(float(v)) for k, v in row.items() if k != "culture")
        agents[t][aid] = row
    cells = {t: {} for t in frames}
    for row in csv.DictReader((root / f"{label}.cells.csv").open()):
        t = int(row["time"])
        coord = int(row["x"]), int(row["y"])
        assert t in cells and coord not in cells[t]
        assert all(math.isfinite(float(v)) for v in row.values())
        assert all(0 <= x < 51 for x in coord)
        cells[t][coord] = row
    assert all(len(c) == 2551 for c in cells.values()), (
        "Historical aliased map must remain unchanged"
    )
    if label != "migration_vision15":
        endpoints = list(
            csv.DictReader((args.root / "reference" / f"{label}.cells.csv").open())
        )
        assert endpoints == [r for t in [0, steps] for r in cells[t].values()]
    assert not list(csv.DictReader((root / f"{label}.trades.csv").open()))
    profiles = []
    for t in frames:
        summary = summaries[t]
        assert len(agents[t]) == int(summary["population"])
        for field in ["sugar", "spice"]:
            assert math.isclose(
                sum(float(a[field]) for a in agents[t].values()),
                float(summary["agent_" + field]),
                rel_tol=1e-12,
                abs_tol=1e-8,
            )
            assert math.isclose(
                sum(float(c[field]) for c in cells[t].values()),
                float(summary["environment_" + field]),
                rel_tol=1e-12,
                abs_tol=1e-8,
            )
        assert math.isclose(
            sum(float(c["pollution"]) for c in cells[t].values()),
            float(summary["pollution"]),
            rel_tol=1e-12,
            abs_tol=1e-8,
        )
        occupied = np.zeros(101, dtype=int)
        observed = np.zeros(101, dtype=int)
        for (x, y), cell in cells[t].items():
            if int(cell["occupier"]) >= 0:
                occupied[x + y] += 1
        for a in agents[t].values():
            observed[int(a["x"]) + int(a["y"])] += 1
        profiles.append(
            {
                "time": t,
                "population": len(agents[t]),
                "occupied_cells": int(occupied.sum()),
                "occupancy_diagonal_counts": occupied.tolist(),
                "observed_agents_diagonal_counts": observed.tolist(),
                "pollution_total": float(summary["pollution"]),
                "pollution_max": max(float(c["pollution"]) for c in cells[t].values()),
                "polluted_cells": sum(
                    float(c["pollution"]) > 0 for c in cells[t].values()
                ),
            }
        )
    results.append(
        {
            "case": label,
            "constructor": constructor,
            "snapshots": len(frames),
            "agent_observations": sum(map(len, agents.values())),
            "cell_observations": sum(map(len, cells.values())),
            "original_exports_exact": label != "migration_vision15",
            "final_population": int(summaries[-1]["population"]),
            "profiles": profiles,
            "files_sha256": {
                p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sorted(root.glob(label + ".*"))
            },
        }
    )
    spatial_data[label] = cells

base_lines = (args.root / "spatial/migration.scenario.txt").read_text().splitlines()
variant_lines = (
    (args.root / "spatial/migration_vision15.scenario.txt").read_text().splitlines()
)
differences = [(a, b) for a, b in zip(base_lines, variant_lines, strict=True) if a != b]
assert len(differences) == 2 and differences[0] == (
    "Constructor: mkParamsAnimationII_6",
    "Constructor: migrationVision15",
)
assert "(1,10)" in differences[1][0] and "(1,15)" in differences[1][1]
args.output.mkdir(exist_ok=False)
fig, axes = plt.subplots(2, 2, figsize=(12, 7), sharex=True, sharey=True)
maximum_bin = max(
    max(profile[field])
    for index in [0, 2]
    for profile in results[index]["profiles"]
    for field in ["occupancy_diagonal_counts", "observed_agents_diagonal_counts"]
)
for column, result in enumerate(results[i] for i in [0, 2]):
    for row, field in enumerate(
        ["occupancy_diagonal_counts", "observed_agents_diagonal_counts"]
    ):
        values = np.asarray([p[field] for p in result["profiles"]])
        im = axes[row, column].imshow(
            values,
            origin="lower",
            aspect="auto",
            extent=[0, 50, 0, steps],
            vmin=0,
            vmax=maximum_bin,
            cmap="viridis",
        )
        axes[row, column].set_title(
            result["case"]
            + ": "
            + ("occupied cells" if row == 0 else "observed agents")
        )
        axes[row, column].set_xlabel("Diagonal position (x+y)/2")
        axes[row, column].set_ylabel("Time")
fig.colorbar(im, ax=axes.ravel().tolist(), label="Count per diagonal bin")
fig.suptitle("Historical model: separate occupancy and pre-event observation views")
fig.savefig(args.output / "migration.png", dpi=140)
plt.close(fig)
fig, axes = plt.subplots(1, 4, figsize=(13, 3.5))
pollution_maximum = max(
    float(c["pollution"])
    for t in [0, 100, 500, 1000]
    for c in spatial_data["pollution"][t].values()
)
for ax, t in zip(axes, [0, 100, 500, 1000], strict=True):
    values = np.full((51, 51), np.nan)
    for (x, y), c in spatial_data["pollution"][t].items():
        values[y, x] = float(c["pollution"])
    im = ax.imshow(values, origin="lower", cmap="magma", vmin=0, vmax=pollution_maximum)
    ax.set_title(f"Time {t}")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    fig.colorbar(im, ax=ax, label="Pollution")
fig.suptitle(
    "Historical pollution fields; common scale; absent aliased cells shown white"
)
fig.tight_layout()
fig.savefig(args.output / "pollution.png", dpi=140)
plt.close(fig)
report = {
    "protocol_sha256": hashlib.sha256(
        (args.root / "protocol.json").read_bytes()
    ).hexdigest(),
    "observer_sha256": protocol["observer_sha256"],
    "binary_sha256": hashlib.sha256((args.root / "observe").read_bytes()).hexdigest(),
    "auditor_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "source_files_verified": len(protocol["original"]["source_sha256"]),
    "resolved_variant_differences": differences,
    "results": results,
    "scope": "Three diagnostic native trajectories, including two observational parity controls; no quantitative wave criterion, ensemble comparison, or whole-paper verdict.",
}
(args.output / "audit.json").write_text(
    json.dumps(report, indent=2, allow_nan=False) + "\n"
)
print(
    json.dumps(
        {
            "cases": [
                {k: v for k, v in r.items() if k not in ["profiles", "files_sha256"]}
                for r in results
            ]
        }
    )
)
