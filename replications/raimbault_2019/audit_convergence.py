"""Reconstruct Table 2 convergence statistics from every archived generated run."""

import argparse
import csv
import gzip
import hashlib
import json
from pathlib import Path

import numpy as np

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("raw", type=Path)
parser.add_argument("source", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
source = (args.source / "sugarscape/comp.R").read_bytes()
assert (
    hashlib.sha256(source).hexdigest()
    == "ca8b3db5c6a4b8a4d065ef6dd82479ff4a3fb9193a526c07760d1eb67ebd254e"
)
assert (
    b"group_by(id,population,minSugar,maxSugar)%>%summarise(giniSharpe = mean(gini)/sd(gini))"
    in source
)
digest = hashlib.sha256()
with gzip.open(args.raw, "rb") as stream:
    while chunk := stream.read(1024 * 1024):
        digest.update(chunk)
assert (
    digest.hexdigest()
    == "1a2cdf93167571ab2943d488017ace08945e7afd3cd8ac4d1410fb214c79c8f5"
)
groups = {}
total = 0
with gzip.open(args.raw, "rt", newline="") as stream:
    for row in csv.DictReader(stream):
        key = tuple(
            int(float(row[k])) for k in ["id", "population", "minSugar", "maxSugar"]
        )
        if key not in groups:
            groups[key] = [[], []]
        for index, name in enumerate(["gini", "mwgini"]):
            value = float(row[name])
            assert np.isfinite(value) and 0 <= value <= 1
            groups[key][index].append(value)
        total += 1
assert total == 2727994 and len(groups) == 54560
args.output.mkdir(parents=True, exist_ok=False)
ratios = [[], []]
with (args.output / "groups.csv").open("x", newline="") as stream:
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(
        [
            "id",
            "population",
            "minSugar",
            "maxSugar",
            "n",
            "gini_mean",
            "gini_sd",
            "gini_sharpe",
            "mwgini_mean",
            "mwgini_sd",
            "mwgini_sharpe",
        ]
    )
    for key, metrics in sorted(groups.items()):
        values = []
        for index, observations in enumerate(metrics):
            assert len(observations) > 1
            mean = float(np.mean(observations))
            sd = float(np.std(observations, ddof=1))
            assert sd > 0
            ratio = mean / sd
            ratios[index].append(ratio)
            values.extend([mean, sd, ratio])
        writer.writerow([*key, len(metrics[0]), *values])
summaries = {}
for name, values in zip(["gini", "mwgini"], ratios, strict=True):
    q = np.quantile(values, [0, 0.25, 0.5, 0.75, 1])
    summaries[name] = [
        float(q[0]),
        float(q[1]),
        float(q[2]),
        float(np.mean(values)),
        float(q[3]),
        float(q[4]),
    ]
target = [2.343, 14.413, 20.993, 20.098, 26.208, 49.808]
report = {
    "rows": total,
    "groups": len(groups),
    "columns": [
        "minimum",
        "first_quartile",
        "median",
        "mean",
        "third_quartile",
        "maximum",
    ],
    "paper_table2": target,
    "summaries": summaries,
    "matches_at_published_precision": [
        round(x, 3) == y for x, y in zip(summaries["gini"], target, strict=True)
    ],
    "source_sha256": hashlib.sha256(source).hexdigest(),
    "raw_uncompressed_sha256": digest.hexdigest(),
    "groups_sha256": hashlib.sha256(
        (args.output / "groups.csv").read_bytes()
    ).hexdigest(),
    "scope": "Archived-data reanalysis, not new simulations. Terminal Gini follows author comp.R; moving-window Gini is a separately labeled diagnostic. Sample standard deviation and linear-interpolated quantiles match R defaults. No group omitted.",
}
(args.output / "audit.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
