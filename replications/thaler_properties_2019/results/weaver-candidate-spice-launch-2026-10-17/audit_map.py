"""Verify literal resource maps against native initial cell and patch totals."""

import argparse
import csv
import hashlib
import json
from pathlib import Path
import re

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("netlogo", type=Path)
parser.add_argument("haskell", type=Path)
parser.add_argument("cells", type=Path)
parser.add_argument("candidate_csv", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
netlogo = re.findall(r'"([0-4]{51})"', args.netlogo.read_text())
haskell = re.findall(r'"([0-4]{51})"', args.haskell.read_text())
assert len(netlogo) == 102 and len(haskell) == 51
assert netlogo[:51] == netlogo[51:] == haskell
cells = [r for r in csv.DictReader(args.cells.open()) if r["time"] == "0"]
assert len(cells) == len({(r["x"], r["y"]) for r in cells}) == 2601
for row in cells:
    x, y = int(row["x"]), int(row["y"])
    assert 0 <= x <= 50 and 0 <= y <= 50
    assert (
        float(row["sugar_capacity"]) == float(row["sugar"]) == int(haskell[y][50 - x])
    )
    assert float(row["spice_capacity"]) == float(row["spice"]) == int(haskell[y][x])
table = list(csv.reader(args.candidate_csv.open()))
assert table[0] == ["BehaviorSpace Table data (NetLogo 4.0.4)"]
assert table[5] == ["-25", "25", "-25", "25"]
initial = dict(zip(table[6], table[7], strict=True))
assert int(initial["[step]"]) == 0 and int(initial["count agents"]) == 400
total = sum(int(c) for row in haskell for c in row)
assert (
    float(initial["sum [psugar] of patches"])
    == float(initial["sum [pspice] of patches"])
    == total
)
report = {
    "input_sha256": {
        key: hashlib.sha256(path.read_bytes()).hexdigest()
        for key, path in [
            ("netlogo", args.netlogo),
            ("haskell", args.haskell),
            ("cells", args.cells),
            ("candidate_csv", args.candidate_csv),
        ]
    },
    "verified_cells": 2601,
    "initial_each_resource_total": total,
    "coordinate_mapping": "Haskell(x,y)=(25-NetLogo.pxcor,25-NetLogo.pycor)",
    "scope": "Literal capacities and native initial resource totals; not model equivalence or authenticated2009 source identity.",
}
with args.output.open("x") as stream:
    stream.write(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
