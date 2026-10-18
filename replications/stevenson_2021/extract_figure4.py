"""Extract the original evolutionary figure without assuming unlabelled trait identities."""

import argparse
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("pdf", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
assert (
    hashlib.sha256(args.pdf.read_bytes()).hexdigest()
    == "25769a97e6a71cf5720ebcccaf2aa69d44adae8b15f06b1a8f4f377a460be31d"
)
args.output.mkdir(parents=True, exist_ok=False)
svg = args.output / "figure4.svg"
subprocess.run(
    ["pdftocairo", "-svg", str(args.pdf.resolve()), str(svg.resolve())], check=True
)
paths = ET.parse(svg).findall(".//{http://www.w3.org/2000/svg}path")
anchors = {
    105: "M 2591.992188 373.320312 L 2591.992188 2510.898438 ",
    112: "M 2506.71875 288.007812 L 710.195312 288.007812 ",
    142: "M 2591.992188 3253.28125 L 2591.992188 5390.898438 ",
    149: "M 2506.71875 3168.007812 L 799.296875 3168.007812 ",
    155: "M 2506.71875 5471.992188 L 697.1875 5471.992188 ",
}
for index, expected in anchors.items():
    assert paths[index].attrib["d"] == expected
series = []
for family, indices in [
    ("infertility", [104, *range(119, 137, 2)]),
    ("birth_cost", [118, *range(120, 137, 2)]),
]:
    for group, index in enumerate(indices):
        name = (
            ("infertility_10" if family == "infertility" else "birth_cost_0")
            if group == 0
            else f"{family}_unlabelled_{group}"
        )
        series.append((name, family, index, 373.320312, 2510.898438, 710.195312, 800))
series.extend(
    [
        ("gini", "aggregate", 141, 3253.28125, 5390.898438, 799.296875, 0.6),
        ("wealth", "aggregate", 154, 3253.28125, 5390.898438, 697.1875, 2000),
    ]
)
reports = []
for name, family, index, t0, t500, ymax, scale in series:
    path = paths[index].attrib
    assert path["transform"] == "matrix(0.1, 0, 0, -0.1, 0, 576)"
    assert re.sub(r"[ML] [0-9.]+ [0-9.]+\s*", "", path["d"]) == ""
    points = [
        (float(x), float(y))
        for x, y in re.findall(r"[ML] ([0-9.]+) ([0-9.]+)", path["d"])
    ]
    values = [
        ((y - t0) / (t500 - t0) * 500, (2506.71875 - x) / (2506.71875 - ymax) * scale)
        for x, y in points
    ]
    assert all(a[0] < b[0] for a, b in zip(values, values[1:]))
    assert max(abs(t - round(t)) for t, _ in values) < 0.05
    assert round(values[0][0]) == 0 and round(values[-1][0]) == 499
    stream = io.StringIO()
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(["approximate_generation", "approximate_value"])
    writer.writerows(values)
    target = args.output / (name + ".csv.gz")
    target.write_bytes(gzip.compress(stream.getvalue().encode(), mtime=0))
    reports.append(
        {
            "series": name,
            "family": family,
            "path_index": index,
            "vertices": len(values),
            "initial_value": values[0][1],
            "terminal_value": values[-1][1],
            "first_generation": values[0][0],
            "last_generation": values[-1][0],
            "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
        }
    )
initial = {}
for family in ["infertility", "birth_cost"]:
    counts = [r["initial_value"] for r in reports if r["family"] == family]
    assert len(counts) == 10 and max(abs(x - round(x)) for x in counts) < 0.05
    initial[family] = {
        "approximate_counts": counts,
        "nearest_integer_counts": [round(x) for x in counts],
        "nearest_integer_total": sum(round(x) for x in counts),
    }
assert (
    initial["infertility"]["nearest_integer_total"]
    == initial["birth_cost"]["nearest_integer_total"]
    == 830
)
report = {
    "pdf_sha256": hashlib.sha256(args.pdf.read_bytes()).hexdigest(),
    "svg_sha256": hashlib.sha256(svg.read_bytes()).hexdigest(),
    "series": reports,
    "initial_trait_marginals": initial,
    "limits": "Vector digitization, not raw observations. Gray curves identify nine alternatives in each family but do not individually label their trait values. Rounded initial counts constrain the plotted initial population, not the joint trait assignment, random seed, ages, or mutation/inheritance rules. Axis says generations; correspondence to simulation cycles remains unverified. Collinear points are omitted; no missing observation is fabricated.",
}
(args.output / "audit.json").write_text(json.dumps(report, indent=2) + "\n")
print(
    json.dumps(
        {
            "series": len(reports),
            "vertices": sum(r["vertices"] for r in reports),
            "initial_population_inferred": 830,
        }
    )
)
