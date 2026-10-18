"""Extract Sugarscape Figure 11 bars from the pinned publisher-page SVG."""

import argparse
import gzip
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("svg_gzip", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
raw = gzip.decompress(args.svg_gzip.read_bytes())
assert hashlib.sha256(raw).hexdigest() == (
    "969fbcc9a247ccc58cbf73bae461fec6278634a65c897617d25f999a9166fe4d"
)
root = ET.fromstring(raw)
group = root.find(".//{http://www.w3.org/2000/svg}g[@id='source-314']")
assert group is not None
names = [
    "DynaSOAr",
    "mallocMC",
    "Halloc",
    "BitmapAlloc",
    "Baseline SOA",
    "Baseline AOS",
]
patterns = [63, 70, 74, 81, 87, 93]
rows = []
for name, pattern in zip(names, patterns, strict=True):
    paths = [
        e for e in group.iter() if e.attrib.get("fill") == f"url(#pattern-{pattern})"
    ]
    assert len(paths) == 1
    path = paths[0].attrib["d"]
    coordinates = [float(n) for n in re.findall(r"-?\d+(?:\.\d+)?", path)]
    assert len(coordinates) == 10
    left, bottom, right, bottom2, right2, top, left2, top2, left3, bottom3 = coordinates
    assert left == left2 == left3 and right == right2
    assert bottom == bottom2 == bottom3 == 110.835938 and top == top2
    assert 241 <= left < right <= 280
    rows.append(
        {
            "allocator": name,
            "pattern": pattern,
            "path": path,
            "bar_height": bottom - top,
        }
    )
normalizer = rows[0]["bar_height"]
assert normalizer == 110.835938 - 41.761719
for row in rows:
    row["relative_maximum_problem_size"] = row["bar_height"] / normalizer
report = {
    "paper_doi": "10.4230/LIPIcs.ECOOP.2019.17",
    "pdf_sha256": "cc62810e47ad909395949ef2d70315839dadca6607538fe92265437a6db01f0d",
    "page": 23,
    "figure": 11,
    "application": "sugarscape",
    "method": "Vector bar heights divided by DynaSOAr height. Shared group coordinates cancel page scaling.",
    "label_mapping": "Six adjacent Sugarscape bars mapped left-to-right using the rendered publisher legend.",
    "interpretation": "Digitized published ratios, not recovered simulation measurements. No replication acceptance tolerance is inferred from vector precision.",
    "targets": rows,
}
with args.output.open("x") as handle:
    json.dump(report, handle, indent=2)
    handle.write("\n")
print(json.dumps({r["allocator"]: r["relative_maximum_problem_size"] for r in rows}))
