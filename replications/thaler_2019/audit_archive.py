"""Audit complete author benchmark reports against the published Sugarscape tables."""

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

import numpy as np

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    "source", type=Path, help="Original haskell-stm-sugarscape checkout"
)
parser.add_argument(
    "paper", type=Path, help="Publisher PDF for DOI 10.1186/s40294-019-0067-9"
)
parser.add_argument("output", type=Path, help="New evidence directory")
args = parser.parse_args()
assert (
    hashlib.sha256(args.paper.read_bytes()).hexdigest()
    == "1cdff1a896e4c36e2247a726a9acb27a09ee491cecdc60cab17c4f85f9aa6916"
)
root = args.output
root.mkdir(parents=True, exist_ok=False)
subprocess.run(
    ["pdftotext", "-layout", str(args.paper), str(root / "paper.txt")], check=True
)
pins = json.loads(Path(__file__).with_name("report-sha256.json").read_text())
extracted = []
for name, expected in pins.items():
    path = args.source / name
    content = path.read_bytes()
    assert hashlib.sha256(content).hexdigest() == expected, name
    match = re.search(r"var reports = (.*);", content.decode())
    for report in json.loads(match[1]):
        extracted.append(
            {
                "path": name,
                "sha256": expected,
                "name": report["reportName"],
                "analysis": report["reportAnalysis"],
                "measured": report["reportMeasured"],
                "keys": report["reportKeys"],
            }
        )
assert len(extracted) == 53
(root / "archived-benchmarks.json").write_text(json.dumps(extracted, indent=2) + "\n")

reports = json.loads((root / "archived-benchmarks.json").read_text())
rows = []
for report in reports:
    keys = report["keys"]
    observations = np.asarray(
        [
            [row[keys.index("iters")], row[keys.index("time")]]
            for row in report["measured"]
        ],
        dtype=float,
    )
    design = np.column_stack([np.ones(len(observations)), observations[:, 0]])
    intercept, slope = np.linalg.lstsq(design, observations[:, 1], rcond=None)[0]
    published = report["analysis"]["anRegress"][0]["regCoeffs"]["iters"]["estPoint"]
    assert abs(slope - published) < 1e-9, report["path"]
    standard_deviation = float(np.std(observations[:, 1] / observations[:, 0], ddof=1))
    archived_std = report["analysis"]["anStdDev"]["estPoint"]
    assert abs(standard_deviation - archived_std) < 1e-9, report["path"]
    rows.append(
        {
            "path": report["path"],
            "samples": len(observations),
            "ols_seconds": float(slope),
            "archived_seconds": published,
            "absolute_error": abs(float(slope) - published),
            "standard_deviation_seconds": standard_deviation,
            "archived_standard_deviation_seconds": archived_std,
            "standard_deviation_error": abs(standard_deviation - archived_std),
        }
    )
summary = {
    "reports": len(rows),
    "raw_measurements": sum(row["samples"] for row in rows),
    "max_ols_error": max(row["absolute_error"] for row in rows),
    "max_standard_deviation_error": max(
        row["standard_deviation_error"] for row in rows
    ),
    "scope": "Independent reanalysis of author archived timings only; no new simulation or hardware replication",
    "paper_sha256": hashlib.sha256(args.paper.read_bytes()).hexdigest(),
    "rows": rows,
}
(root / "archived-ols-audit.json").write_text(json.dumps(summary, indent=2) + "\n")

text = (root / "paper.txt").read_text()
rows = json.loads((root / "archived-ols-audit.json").read_text())["rows"]
reports = {r["path"].split("/")[-1]: r for r in rows}
comparisons = []
variability = []
for table, start, end in [
    (6, "Table 6 Performance comparison", "Best performance indicated"),
    (8, "Table 8 Performance comparison", "Best performance indicated"),
    (9, "Table 9 Sugarscape TArray performance", "Timings in seconds"),
]:
    section = text.split(start, 1)[1].split(end, 1)[0]
    for line in section.splitlines():
        if not re.match(r"^\s*\d+\s+", line):
            continue
        index = int(line.split()[0])
        values = re.findall(r"(\d+\.\d+)\s*\((\d+\.\d+)\)", line)
        variants = (
            ["seq", "io", "tvar", "tarray"] if table != 9 else ["normal", "rebirthing"]
        )
        if table == 6 and index > 1:
            variants = variants[1:]
        assert len(values) == len(variants)
        for variant, (value, bracket) in zip(variants, values, strict=True):
            if table == 6:
                filename = (
                    "sugarscape-seq-singlecore_500.html"
                    if variant == "seq"
                    else f"sugarscape-{variant}-normal_500_{index}.html"
                )
            elif table == 8:
                suffix = "" if variant == "seq" else "_4"
                filename = f"sugarscape-{variant}-rebirthing_{index}{suffix}.html"
            else:
                agents = 500 if variant == "normal" else 2500
                filename = f"sugarscape-tarray-{variant}_amazon_{agents}_{index}.html"
            seconds = reports[filename]["ols_seconds"]
            rounded = float(format(seconds, ".3g"))
            if table != 9:
                deviation = reports[filename]["standard_deviation_seconds"]
                variability.append(
                    {
                        "table": table,
                        "index": index,
                        "variant": variant,
                        "paper_seconds": float(bracket),
                        "recomputed_seconds": deviation,
                        "nearest_hundredth": round(deviation, 2),
                        "nearest_hundredth_matches": round(deviation, 2)
                        == float(bracket),
                        "absolute_difference": abs(float(bracket) - deviation),
                    }
                )
            comparisons.append(
                {
                    "table": table,
                    "index": index,
                    "variant": variant,
                    "paper_seconds": float(value),
                    "ols_seconds": seconds,
                    "three_significant_digits": rounded,
                    "match": rounded == float(value),
                    "paper_parenthesis": float(bracket),
                    "parenthesis_meaning": "retry ratio"
                    if table == 9
                    else "standard deviation",
                }
            )
result = {
    "timings": len(comparisons),
    "matches": sum(r["match"] for r in comparisons),
    "interpretation": (
        "Author timings compared to OLS slope rounded to three significant digits. "
        "Archive reanalysis only; standard deviations compared separately, retry ratios unvalidated."
    ),
    "rows": comparisons,
}
(root / "paper-timing-comparison.json").write_text(json.dumps(result, indent=2) + "\n")

assert result["timings"] == 51
assert result["matches"] == 51
print(
    json.dumps(
        {"reports": 53, "timings": result["timings"], "matches": result["matches"]}
    )
)

assert len(variability) == 45
variability_summary = {
    "cells": len(variability),
    "nearest_hundredth_matches": sum(
        r["nearest_hundredth_matches"] for r in variability
    ),
    "max_absolute_difference": max(r["absolute_difference"] for r in variability),
    "scope": "Descriptive comparison with printed standard deviations. No adjusted tolerance, acceptance claim, or retry-ratio validation.",
    "rows": variability,
}
(root / "paper-variability-comparison.json").write_text(
    json.dumps(variability_summary, indent=2) + "\n"
)
print(json.dumps({k: v for k, v in variability_summary.items() if k != "rows"}))
