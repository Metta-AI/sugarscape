"""Extract Sugarscape Figure 10 timing bars from the pinned publisher SVG."""

import argparse
import gzip
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path


def coordinates(element):
    values = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", element.attrib["d"])]
    assert len(values) in (4, 10)
    points = list(zip(values[::2], values[1::2], strict=True))
    if "transform" in element.attrib:
        a, b, c, d, e, f = [
            float(x)
            for x in re.findall(r"-?\d+(?:\.\d+)?", element.attrib["transform"])
        ]
        assert b == c == 0
        points = [(a * x + e, d * y + f) for x, y in points]
    return (
        min(x for x, y in points),
        min(y for x, y in points),
        max(x for x, y in points),
        max(y for x, y in points),
    )


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("svg_gzip", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
raw = gzip.decompress(args.svg_gzip.read_bytes())
assert (
    hashlib.sha256(raw).hexdigest()
    == "969fbcc9a247ccc58cbf73bae461fec6278634a65c897617d25f999a9166fe4d"
)
root = ET.fromstring(raw)
group = root.find(".//{http://www.w3.org/2000/svg}g[@id='source-182']")
assert group is not None
lines = [e for e in group.iter() if e.attrib.get("stroke") == "rgb(100%, 100%, 100%)"]
horizontal = sorted(
    [coordinates(e)[1] for e in lines if coordinates(e)[1] == coordinates(e)[3]],
    reverse=True,
)
assert len(horizontal) == 7
zero, three_hundred = horizontal[0], horizontal[-1]
scale = (zero - three_hundred) / 300
assert all(abs((zero - y) / scale - 50 * i) < 0.02 for i, y in enumerate(horizontal))
white = [e for e in group.iter() if e.attrib.get("fill") == "rgb(100%, 100%, 100%)"]
rows = []
for name, pattern in zip(
    [
        "DynaSOAr",
        "mallocMC",
        "Halloc",
        "BitmapAlloc",
        "CUDA Allocator",
        "Baseline SOA",
        "Baseline AOS",
    ],
    [5, 13, 21, 29, 37, 43, 49],
    strict=True,
):
    elements = [
        e for e in group.iter() if e.attrib.get("fill") == f"url(#pattern-{pattern})"
    ]
    assert len(elements) == 1
    left, top, right, bottom = coordinates(elements[0])
    assert 260 < left < right < 297 and abs(bottom - zero) < 0.001
    caps = [
        e
        for e in white
        if abs(coordinates(e)[0] - left) < 0.001
        and abs(coordinates(e)[2] - right) < 0.001
    ]
    assert len(caps) <= 1
    row = {
        "allocator": name,
        "pattern": pattern,
        "colored_path": elements[0].attrib["d"],
    }
    if name == "CUDA Allocator":
        row.update(
            total_seconds=857.1,
            source="Printed overflow annotation above the Sugarscape CUDA bar",
            enumeration_seconds=None,
            limitation="Clipped bar does not expose separate enumeration duration",
        )
    else:
        cap_height = 0.0
        if caps:
            cap = coordinates(caps[0])
            assert abs(cap[3] - top) < 0.001
            cap_height = cap[3] - cap[1]
            row["enumeration_path"] = dict(caps[0].attrib)
        row.update(
            non_enumeration_seconds=(bottom - top) / scale,
            enumeration_seconds=cap_height / scale,
            total_seconds=(bottom - top + cap_height) / scale,
        )
    rows.append(row)
report = {
    "figure": 10,
    "page": 23,
    "paper_doi": "10.4230/LIPIcs.ECOOP.2019.17",
    "svg_sha256": hashlib.sha256(raw).hexdigest(),
    "axis_grid_y": horizontal,
    "svg_units_per_second": scale,
    "method": "Seven horizontal grid lines map to 0:50:300 seconds. Colored heights plus adjoining white caps give total duration. CUDA uses its printed overflow annotation.",
    "scope": "Digitized historical Titan Xp timing targets. No cross-hardware acceptance tolerance or uncertainty inferred.",
    "targets": rows,
}
with args.output.open("x") as handle:
    json.dump(report, handle, indent=2)
    handle.write("\n")
print(json.dumps({r["allocator"]: r["total_seconds"] for r in rows}))
