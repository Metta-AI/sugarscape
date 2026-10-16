"""Check every plotted ordinate and observer parity through the native plotting workflow."""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import runpy
import shutil
import statistics

import matplotlib
matplotlib.use("Agg")
from matplotlib.axes import Axes

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("figures", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
figures = args.figures.resolve()
output = args.output.resolve()
manifest = json.loads((figures / "manifest.json").read_text())
script = figures / "make_paper_figures.py"
assert hashlib.sha256(script.read_bytes()).hexdigest() == manifest["script_sha256"]
data = figures / "results/canonical/part_b_stage5_main.csv"
assert hashlib.sha256(data.read_bytes()).hexdigest() == manifest["input_sha256"]
rows = list(csv.DictReader(data.open()))
labels = {"no intervention": "baseline", "labor / UBI": "labour/ubi", "wealth / UBI": "wealth/ubi",
          "UHI scenario": "uhi_scenario", "disp-levy / means-tested": "disp_levy/means_tested",
          "labor / means-tested": "labour/means_tested", "wealth / means-tested": "wealth/means_tested"}
speeds = ["slow", "balanced", "fast"]
assert len(rows) == 105
assert {(r["km_label"], r["cell_label"], int(r["seed"])) for r in rows} == {
    (speed, cell, seed) for speed in speeds for cell in labels.values() for seed in range(5)}
output.mkdir(parents=True, exist_ok=False)
(output / "results/canonical").mkdir(parents=True)
shutil.copyfile(data, output / "results/canonical/part_b_stage5_main.csv")
captured = []
native_plot = Axes.plot


def observed_plot(axis, *values, **settings):
    lines = native_plot(axis, *values, **settings)
    captured.extend((axis, line) for line in lines)
    return lines


Axes.plot = observed_plot
previous = Path.cwd()
try:
    os.chdir(output)
    runpy.run_path(str(script), run_name="__main__")
finally:
    os.chdir(previous)
    Axes.plot = native_plot
assert len(captured) == 14
metrics = {"Gini coefficient at step 300": "gini_final",
           "cumulative deaths from resource exhaustion": "starvation_deaths_total"}
points = []
for axis, line in captured:
    metric = metrics[axis.get_ylabel()]
    cell = labels[line.get_label()]
    assert list(line.get_xdata()) == [0, 1, 2]
    for speed, value in zip(speeds, line.get_ydata()):
        expected = statistics.mean(float(r[metric]) for r in rows if r["km_label"] == speed and r["cell_label"] == cell)
        assert abs(float(value) - expected) < 1e-12
        points.append({"metric": metric, "cell": cell, "speed": speed, "plotted": float(value), "independent_mean": expected})
assert len({(p["metric"], p["cell"], p["speed"]) for p in points}) == 42
for name in ["fig_gini_inversion.png", "fig_welfare_robustness.png"]:
    relative = "results/canonical/" + name
    assert (figures / relative).read_bytes() == (output / relative).read_bytes()
(output / "series-audit.json").write_text(json.dumps({"points_checked": 42, "absolute_tolerance": 1e-12,
    "native_observed_images_byte_identical": True, "points": points,
    "scope": "Fresh plotted data and observation parity; original published PNG pixels differ in this rendering environment."}, indent=2) + "\n")
print("All 42 plotted means match independent CSV calculations; both observer PNGs match native PNGs byte-for-byte")
