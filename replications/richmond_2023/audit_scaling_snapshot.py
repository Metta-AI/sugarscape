"""Audit a sealed, complete-condition scaling prefix against the author archive."""

import argparse
import csv
from decimal import Decimal
import hashlib
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("snapshot", type=Path)
parser.add_argument("reference", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
receipt = json.loads((args.snapshot / "snapshot.json").read_text())
tables = {}
for name in ["performance_scaling.csv", "performance_scalingperStep.csv"]:
    raw = (args.snapshot / name).read_bytes()
    assert receipt["files"][name] == {
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "newline_terminated": True,
    }
    assert raw.endswith(b"\n")
    tables[name] = list(csv.DictReader(raw.decode().splitlines()))
reference_raw = args.reference.read_bytes()
assert (
    hashlib.sha256(reference_raw).hexdigest()
    == "022b45bd8c945fb0f4c7aba6ae2385c433b3b436f5a26601cbad0f4055c1e48b"
)
reference = list(csv.DictReader(reference_raw.decode().splitlines()))
conditions = [(r, w) for r in range(3) for w in range(256, 4097, 256)]
expected = [(r, w, step) for r, w in conditions for step in range(100)]
assert len(reference) == 4800
assert [
    (int(row["repetition"]), int(row["grid_width"]), int(row["step"]))
    for row in reference
] == expected
assert all(
    row["p_occupation"] == "0.17"
    and int(row["pop_size"]) == int(row["grid_width"]) ** 2
    for row in reference
)
aggregates = tables["performance_scaling.csv"]
steps = tables["performance_scalingperStep.csv"]
assert 0 < len(aggregates) <= 48
assert len(steps) == 100 * len(aggregates)
assert [
    (int(row["repetition"]), int(row["grid_width"])) for row in aggregates
] == conditions[: len(aggregates)]
assert [
    (int(row["repetition"]), int(row["grid_width"]), int(row["step"])) for row in steps
] == expected[: len(steps)]
assert all(
    row["p_occupation"] == "0.17"
    and int(row["pop_size"]) == int(row["grid_width"]) ** 2
    for row in aggregates + steps
)
differences = []
for actual, target in zip(steps, reference):
    count = int(actual["pop_count"])
    assert 0 <= count <= int(actual["pop_size"])
    timing = Decimal(actual["s_step"])
    assert timing.is_finite() and timing > 0
    differences.append(count - int(target["pop_count"]))
means = []
for index, aggregate in enumerate(aggregates):
    observations = steps[index * 100 : (index + 1) * 100]
    for field in ["pop_count", "s_step"]:
        values = [Decimal(row[field]) for row in observations]
        mean = sum(values) / 100
        recorded = Decimal(aggregate[field + "_mean"])
        assert recorded.is_finite()
        bound = Decimal(10) ** recorded.as_tuple().exponent / 2
        if field == "s_step":
            bound += (
                sum(Decimal(10) ** value.as_tuple().exponent / 2 for value in values)
                / 100
            )
        assert abs(mean - recorded) <= bound
        means.append(
            {
                "condition": conditions[index],
                "metric": field,
                "recomputed": str(mean),
                "recorded": str(recorded),
                "rounding_bound": str(bound),
            }
        )
report = {
    "scaling_conditions": len(aggregates),
    "scaling_conditions_required": 48,
    "observations": len(steps),
    "exact_population_matches": sum(value == 0 for value in differences),
    "maximum_absolute_population_difference": max(map(abs, differences)),
    "aggregate_means_verified": len(means),
    "input_files": receipt["files"],
    "reference_sha256": hashlib.sha256(reference_raw).hexdigest(),
    "scope": "Live complete-condition prefix only. Different GPU; no performance equivalence or full-paper verdict. Source and binary validation remain separate provenance.",
    "means": means,
}
with args.output.open("x") as stream:
    stream.write(json.dumps(report, indent=2) + "\n")
print(json.dumps({key: value for key, value in report.items() if key != "means"}))
