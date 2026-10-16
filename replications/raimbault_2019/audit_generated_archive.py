import collections
import csv
import gzip
import hashlib
import json
import math
import time
from pathlib import Path
import argparse

parser = argparse.ArgumentParser(
    description="Reconstruct the released generated-landscape aggregate from its original seeded runs."
)
parser.add_argument("raw", type=Path)
parser.add_argument("aggregate", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
digest = hashlib.sha256()
with gzip.open(args.raw, "rb") as raw:
    while chunk := raw.read(1024 * 1024):
        digest.update(chunk)
assert (
    digest.hexdigest()
    == "1a2cdf93167571ab2943d488017ace08945e7afd3cd8ac4d1410fb214c79c8f5"
)
assert (
    hashlib.sha256(args.aggregate.read_bytes()).hexdigest()
    == "f3fdab2fef48cbfd98eece1ee98e0d48bb69fac47197075c07550589273e4a2c"
)
p = args.output
p.mkdir(parents=True, exist_ok=False)
began = time.time()
groups = {}
row_count = 0
duplicates = 0
setups = collections.Counter()
params = {}
fields = ["mwgini", "spAlpha", "spDiffsteps", "spDiffusion", "spGrowth", "spPopulation"]
with gzip.open(args.raw, "rt", newline="") as stream:
    reader = csv.DictReader(stream)
    for row in reader:
        key = tuple(
            int(float(row[k])) for k in ["id", "population", "minSugar", "maxSugar"]
        )
        values = [float(row[k]) for k in fields]
        assert all(math.isfinite(v) for v in values)
        assert 0 <= float(row["gini"]) <= 1 and 0 <= values[0] <= 1
        seed = int(row["replication"])
        setup = int(row["setup"])
        setups[setup] += 1
        if key not in groups:
            groups[key] = [0, [0.0] * len(fields), set()]
        group = groups[key]
        group[0] += 1
        for i, v in enumerate(values):
            group[1][i] += v
        duplicates += seed in group[2]
        group[2].add(seed)
        generator = tuple(row[k] for k in fields[1:])
        if key[0] not in params:
            params[key[0]] = generator
        assert params[key[0]] == generator
        row_count += 1
aggregate = args.aggregate
archived = {
    tuple(int(float(r[k])) for k in ["id", "population", "minSugar", "maxSugar"]): r
    for r in csv.DictReader(aggregate.open())
}
assert set(groups) == set(archived)
max_errors = {k: 0.0 for k in fields}
mismatches = []
counts = collections.Counter()
with (p / "group-audit.csv").open("x", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(
        [
            "id",
            "population",
            "minSugar",
            "maxSugar",
            "count",
            "unique_seeds",
            "mean_mwgini",
            "archived_mean",
            "absolute_error",
        ]
    )
    for key, (n, sums, seen) in sorted(groups.items()):
        counts[n] += 1
        original = archived[key]
        for i, name in enumerate(fields):
            column = "gini" if name == "mwgini" else name
            error = abs(sums[i] / n - float(original[column]))
            max_errors[name] = max(max_errors[name], error)
            if error > 1e-10:
                mismatches.append({"key": key, "field": name, "error": error})
        writer.writerow(
            [
                *key,
                n,
                len(seen),
                sums[0] / n,
                original["gini"],
                abs(sums[0] / n - float(original["gini"])),
            ]
        )
report = {
    "raw_sha256": digest.hexdigest(),
    "rows": row_count,
    "groups": len(groups),
    "landscape_parameter_sets": len(params),
    "repetitions_histogram": dict(counts),
    "setup_counts": dict(setups),
    "within_group_duplicate_seeds": duplicates,
    "aggregate_maximum_errors": max_errors,
    "aggregate_mismatches": len(mismatches),
    "first_mismatches": mismatches[:20],
    "elapsed_seconds": time.time() - began,
}
(p / "raw-audit.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
assert not mismatches and not duplicates
