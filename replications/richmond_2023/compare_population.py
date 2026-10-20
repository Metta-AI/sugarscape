"""Compare immutable native population records with the pinned author archive."""

import argparse
import csv
import hashlib
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("snapshot", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
paths = [args.snapshot / name for name in ["native.csv", "reference.csv"]]
hashes = [hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]
assert hashes[1] == "022b45bd8c945fb0f4c7aba6ae2385c433b3b436f5a26601cbad0f4055c1e48b"
tables = []
for path in paths:
    with path.open() as stream:
        tables.append(list(csv.DictReader(stream)))
native, reference = tables
assert len(reference) == 4800 and 0 < len(native) <= len(reference)
fields = ["repetition", "grid_width", "pop_size", "p_occupation", "step"]
expected = [
    (str(r), str(w), str(w * w), "0.17", str(s))
    for r in range(3)
    for w in range(256, 4097, 256)
    for s in range(100)
]
assert [tuple(row[f] for f in fields) for row in reference] == expected
assert [tuple(row[f] for f in fields) for row in native] == expected[: len(native)]
differences = []
for actual, target in zip(native, reference):
    count = int(actual["pop_count"])
    assert 0 <= count <= int(actual["pop_size"])
    differences.append(count - int(target["pop_count"]))
report = {
    "observations": len(native),
    "exact_population_matches": sum(d == 0 for d in differences),
    "maximum_absolute_population_difference": max(map(abs, differences)),
    "native_sha256": hashes[0],
    "reference_sha256": hashes[1],
    "scope": "Live immutable population prefix comparison; timings excluded; not whole-ensemble or whole-model validation.",
}
assert report == json.loads((args.snapshot / "comparison.json").read_text())
with args.output.open("x") as stream:
    stream.write(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
