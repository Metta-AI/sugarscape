"""Extract both actual and fitted subsistence curves from the original vector figure."""

import argparse
import csv
import hashlib
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
    == "d4e9c64d3792db28af5e0e7e4e2bb67206fcc81f7e94b85ba74d2b05d5aeadaf"
)
args.output.mkdir(parents=True, exist_ok=False)
svg = args.output / "figure6.svg"
subprocess.run(
    ["pdftocairo", "-svg", str(args.pdf.resolve()), str(svg.resolve())], check=True
)
paths = ET.parse(svg).findall(".//{http://www.w3.org/2000/svg}path")
assert paths[112].attrib["d"] == "M 2663.984375 373.320312 L 2663.984375 2506.71875 "
assert paths[118].attrib["d"] == "M 2581.289062 288.007812 L 681.015625 288.007812 "
reports = []
for index, infertility, kind, dash in [
    (111, 10, "actual", None),
    (124, 10, "fitted", "45 30"),
    (125, 5, "actual", "0 30"),
    (126, 5, "fitted", "7.5 22.5 37.5 22.5"),
]:
    path = paths[index].attrib
    assert path["transform"] == "matrix(0.1, 0, 0, -0.1, 0, 576)"
    assert path["stroke"] == "rgb(0%, 0%, 0%)"
    if dash is None:
        assert "stroke-dasharray" not in path
    else:
        assert path["stroke-dasharray"] == dash
    assert re.sub(r"[ML] [0-9.]+ [0-9.]+\s*", "", path["d"]) == ""
    points = [
        (
            (float(y) - 373.320312) / (2506.71875 - 373.320312) * 200,
            (2581.289062 - float(x)) / (2581.289062 - 681.015625) * 800,
        )
        for x, y in re.findall(r"[ML] ([0-9.]+) ([0-9.]+)", path["d"])
    ]
    assert all(a[0] < b[0] for a, b in zip(points, points[1:]))
    assert max(abs(t - round(t)) for t, n in points) < 0.02
    assert round(points[0][0]) == 0 and round(points[-1][0]) == 505
    filename = f"infertility-{infertility}-{kind}.csv"
    with (args.output / filename).open("w") as f:
        writer = csv.writer(f)
        writer.writerow(["approximate_cycle", "approximate_population"])
        writer.writerows(points)
    reports.append(
        {
            "file": filename,
            "infertility": infertility,
            "metabolism": 4,
            "puberty": 1,
            "birth_cost": 0,
            "kind": kind,
            "vertices": len(points),
            "visible_vertices": sum(0 <= round(t) <= 200 for t, n in points),
            "sha256": hashlib.sha256((args.output / filename).read_bytes()).hexdigest(),
        }
    )
(args.output / "audit.json").write_text(
    json.dumps(
        {
            "pdf_sha256": hashlib.sha256(args.pdf.read_bytes()).hexdigest(),
            "svg_sha256": hashlib.sha256(svg.read_bytes()).hexdigest(),
            "curves": reports,
            "scope": "Vector coordinates; caption and line styles identify parameters. Rendered axis ends at200, but paths retain vertices through505. Preserve hidden vertices separately; do not interpolate omitted collinear points. Original seeds and fitting convention remain unknown.",
        },
        indent=2,
    )
    + "\n"
)
print(json.dumps(reports))
