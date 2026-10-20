"""Reconstruct the deposited pensions workbook; this is not a simulation replication."""

import argparse
from collections import defaultdict
import csv
import hashlib
import json
import math
from pathlib import Path
import statistics
import xml.etree.ElementTree as ET
import zipfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    "source", type=Path, help="Directory containing the deposited CSV and XLSX"
)
parser.add_argument("output", type=Path, help="New audit JSON file")
args = parser.parse_args()
assert not args.output.exists()
stem = "Sugarscape Pension Law pensionsExperiments-table"
expected_hashes = {
    stem + ".csv": "627bbaa69cd0c3dffc6a7a093db6b354f45c79510cd0128c124cac1080270690",
    stem
    + "-aggregated.xlsx": "182ce9e8647a113f232bd4a56fdaa52661a8ddda0c326cbd0080940e260bf0fe",
}
for name, digest in expected_hashes.items():
    assert hashlib.sha256((args.source / name).read_bytes()).hexdigest() == digest, name

with (args.source / (stem + ".csv")).open(newline="") as stream:
    for _ in range(6):
        next(stream)
    records = list(csv.DictReader(stream))
assert len(records) == 1280
assert {int(r["[run number]"]) for r in records} == set(range(1, 1281))
assert {int(r["[step]"]) for r in records} == {1000}
parameters = ["initial-population", "retirement-age", "pension-taxes", "fixed-fee"]
metrics = list(records[0])[-6:]
groups = defaultdict(list)
for record in records:
    groups[tuple(float(record[k]) for k in parameters)].append(record)
assert len(groups) == 128 and {len(g) for g in groups.values()} == {10}

ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
with zipfile.ZipFile(args.source / (stem + "-aggregated.xlsx")) as archive:
    strings = [
        "".join(item.itertext())
        for item in ET.fromstring(archive.read("xl/sharedStrings.xml")).findall(
            "m:si", ns
        )
    ]
    sheet = []
    for row in ET.fromstring(archive.read("xl/worksheets/sheet1.xml")).findall(
        ".//m:row", ns
    ):
        values = []
        for cell in row.findall("m:c", ns):
            value = cell.find("m:v", ns)
            # The exported header has an empty row-number cell.
            if value is not None:
                values.append(
                    strings[int(value.text)]
                    if cell.attrib.get("t") == "s"
                    else value.text
                )
        sheet.append(values)
assert len(sheet) == 129 and len(sheet[0]) == 22
assert sheet[0][:4] == ["ip", "ra", "pt", "ff"]
comparisons = []
seen = set()
for row in sheet[1:]:
    assert len(row) == 23
    values = list(map(float, row[1:]))
    key = tuple(values[:4])
    assert key not in seen
    seen.add(key)
    group = groups[key]
    for i, metric in enumerate(metrics):
        observations = [float(record[metric]) for record in group]
        mean = statistics.mean(observations)
        sd = statistics.stdev(observations)
        native_se = sd / math.sqrt(len(groups))
        replicate_se = sd / math.sqrt(len(group))
        for actual, deposited in [
            (mean, values[4 + i]),
            (sd, values[10 + i]),
            (native_se, values[16 + i]),
        ]:
            assert math.isfinite(actual) and abs(actual - deposited) <= 0.005000001, (
                key,
                metric,
                actual,
                deposited,
            )
        comparisons.append(
            {
                "parameters": key,
                "metric": metric,
                "mean": mean,
                "sd": sd,
                "native_se": native_se,
                "replicate_se": replicate_se,
                "workbook_se": values[16 + i],
            }
        )
assert seen == set(groups) and len(comparisons) == 768
report = {
    "input_sha256": expected_hashes,
    "runs": 1280,
    "conditions": 128,
    "replicates_per_condition": 10,
    "workbook_values_reconstructed_within_printed_rounding": 2304,
    "native_to_replicate_se_ratio": math.sqrt(10 / 128),
    "comparisons": comparisons,
    "scope": "Archived-data reconstruction only. No simulation or paper-level verdict. Native and replicate-based errors retained separately.",
}
args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
print(
    "Reconstructed 2304 deposited workbook values across 128 conditions; no paper verdict."
)
