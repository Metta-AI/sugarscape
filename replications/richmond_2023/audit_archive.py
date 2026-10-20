"""Audit the complete published Figure 11 CSV grid without rerunning simulations."""

import argparse
import csv
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("source", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
assert (
    subprocess.check_output(
        ["git", "-C", str(args.source), "rev-parse", "HEAD"], text=True
    ).strip()
    == "290702073492677f2fc9164419e9d5900d119e02"
)
subprocess.run(
    ["git", "-C", str(args.source), "diff", "--exit-code", "HEAD", "--"],
    check=True,
    stdout=subprocess.DEVNULL,
)
data = args.source / "sample/data/v100-515.65.01/2.0.0-rc-v100-11.0-beltsoff"
args.output.mkdir(parents=True, exist_ok=False)
files = {}
counts = {}
comparisons = []
for experiment, widths, densities in [
    ("performance_scaling", range(256, 4097, 256), ["0.17"]),
    ("occupation", [512], ["0.02", "0.04", "0.08", "0.16", "0.32", "0.64"]),
]:
    names = [experiment + ".csv", experiment + "perStep.csv"]
    tables = []
    for name in names:
        content = (data / name).read_bytes()
        files[name] = hashlib.sha256(content).hexdigest()
        with (data / name).open() as stream:
            tables.append(list(csv.DictReader(stream)))
        counts[name] = len(tables[-1])
    aggregate, steps = tables
    expected = {(r, w, d) for r in range(3) for w in widths for d in densities}
    groups = {}
    for row in steps:
        key = (int(row["repetition"]), int(row["grid_width"]), row["p_occupation"])
        assert key in expected
        assert int(row["pop_size"]) == key[1] ** 2
        assert 0 <= int(row["pop_count"]) <= key[1] ** 2
        assert Decimal(row["s_step"]).is_finite() and Decimal(row["s_step"]) > 0
        groups.setdefault(key, []).append(row)
    assert set(groups) == expected and len(aggregate) == len(expected)
    seen = set()
    for row in aggregate:
        key = (int(row["repetition"]), int(row["grid_width"]), row["p_occupation"])
        assert key not in seen and key in expected
        seen.add(key)
        observations = groups[key]
        assert [int(s["step"]) for s in observations] == list(range(100))
        assert int(row["pop_size"]) == key[1] ** 2
        for field, target in [
            ("s_step", "s_step_mean"),
            ("pop_count", "pop_count_mean"),
        ]:
            values = [Decimal(s[field]) for s in observations]
            assert all(v.is_finite() for v in values)
            mean = sum(values) / 100
            recorded = Decimal(row[target])
            # Each CSV number is rounded independently by the native stream.
            step_error = (
                sum(Decimal(10) ** v.as_tuple().exponent / 2 for v in values) / 100
                if field == "s_step"
                else Decimal(0)
            )
            bound = step_error + Decimal(10) ** recorded.as_tuple().exponent / 2
            error = abs(mean - recorded)
            assert error <= bound, (key, target, mean, recorded, bound)
            comparisons.append(
                {
                    "experiment": experiment,
                    "key": key,
                    "metric": target,
                    "reconstructed": str(mean),
                    "recorded": str(recorded),
                    "error": str(error),
                    "rounding_bound": str(bound),
                }
            )
    assert seen == expected
name = "resolution_steps.csv"
files[name] = hashlib.sha256((data / name).read_bytes()).hexdigest()
with (data / name).open() as stream:
    resolution = list(csv.DictReader(stream))
expected = {
    (r, d, n)
    for r in range(3)
    for d in ["0.02", "0.04", "0.08", "0.16", "0.32", "0.64"]
    for n in range(1, 10)
}
seen = set()
for row in resolution:
    key = (
        int(row["repetition"]),
        row["p_occupation"],
        int(row["resolution_iterations"]),
    )
    assert key not in seen and key in expected
    seen.add(key)
    assert int(row["grid_width"]) == 512 and int(row["pop_size"]) == 512**2
    assert (
        0
        <= Decimal(row["mean_unresolved_count"])
        <= Decimal(row["mean_pop_count"])
        <= 512**2
    )
    if key[2] == 1:
        assert int(row["mean_unresolved_count"]) == 0
assert seen == expected
counts[name] = len(resolution)
for name in [
    "src/main.cu",
    "plot_publication.py",
    "CMakeLists.txt",
    "sample/readme.md",
]:
    files[name] = hashlib.sha256((args.source / name).read_bytes()).hexdigest()
report = {
    "source_revision": "290702073492677f2fc9164419e9d5900d119e02",
    "files_sha256": files,
    "rows": counts,
    "recomputed_aggregates": len(comparisons),
    "comparisons": comparisons,
    "resolution_first_bin_all_zero": True,
    "scope": "Archived data structural and aggregation audit only. No fresh simulation, independent model, or performance replication.",
}
(args.output / "audit.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({"rows": counts, "recomputed_aggregates": len(comparisons)}))
