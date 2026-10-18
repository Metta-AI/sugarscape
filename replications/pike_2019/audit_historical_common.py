"""Reconstruct the author's retained 100-run multi-level common-resource archive."""

import argparse
from collections import Counter, defaultdict
import csv
import gzip
import hashlib
import io
import json
import math
from pathlib import Path
import pickle
import statistics
import subprocess

import numpy as np


class ArchiveReader(pickle.Unpickler):
    def find_class(self, module, name):
        return {
            ("collections", "defaultdict"): defaultdict,
            ("builtins", "list"): list,
            ("numpy.core.multiarray", "scalar"): np.core.multiarray.scalar,
            ("numpy", "dtype"): np.dtype,
        }[module, name]


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("engine", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
revision = "585e53398f4f58e89ec184c83bb20819f0e4c96a"
assert (
    subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=args.engine, text=True
    ).strip()
    == revision
)
pins = {
    "net_multi_sur_ging10_policy.p": "1c74b40512097ed561a8a47987861a158d38686fa6d426532e11308377257525",
    "net_multi_time_ging10_policy.p": "2021f1cf55228c6522c662f52c9716ec4a76e92de4b5c899e8c16b17f2e2ab9d",
    "total_price_ging10_policy.p": "f14c16a17b37d8c0eb2fe0e7b987fe81952b1cade455b32ce601db1c90c69446",
    "type_df_ging10_policy.p": "1b017ced039af6d471b3e73e16b1579280afff1761e1a73348ee89cce87bbc3f",
    "final_groups_ging10_policy.p": "81eed4dd66d3001209b9a3b1f767b79c79fb42a25f9278ed1fb0ba30e9de02a1",
}
data = {}
for name, digest in pins.items():
    raw = (args.engine / "Common Resource- multi-level" / name).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == digest
    data[name] = ArchiveReader(io.BytesIO(raw)).load()
    assert len(data[name]) == 100
survivors = data["net_multi_sur_ging10_policy.p"]
timings = data["net_multi_time_ging10_policy.p"]
assert all(type(value) is int and 0 <= value <= 200 for value in survivors)
assert all(math.isfinite(value) and value > 0 for value in timings)
assert sum(survivors) == 9283
run_keys = [f"Run{i}" for i in range(100)]
for name in [
    "total_price_ging10_policy.p",
    "type_df_ging10_policy.p",
    "final_groups_ging10_policy.p",
]:
    assert list(data[name]) == run_keys
stream = io.StringIO(newline="")
writer = csv.writer(stream)
writer.writerow(["run", "step", "trades", "sample_sd_log_price"])
summaries = []
dispersions = []
for index, key in enumerate(run_keys):
    types = data["type_df_ging10_policy.p"][key]
    prices = data["total_price_ging10_policy.p"][key]
    groups = data["final_groups_ging10_policy.p"][key]
    assert list(types) == list(range(1, 1001))
    assert set(prices) <= set(range(1, 1001))
    assert all(
        len(value) == 2 and isinstance(value[0], list) for value in types.values()
    )
    stack = [groups]
    ids = []
    while stack:
        value = stack.pop()
        if isinstance(value, dict):
            stack.extend(value.values())
        else:
            assert isinstance(value, list)
            assert all(
                type(identifier) is int and 0 <= identifier < 200
                for identifier in value
            )
            ids.extend(value)
    assert types[1000][1] == len(groups["Independents"])
    trades = 0
    defined = 0
    for step in range(1, 1001):
        values = prices[step] if step in prices else []
        assert all(math.isfinite(value) and value > 0 for value in values)
        trades += len(values)
        deviation = ""
        if len(values) >= 2:
            deviation = statistics.stdev([math.log(value) for value in values])
            dispersions.append(deviation)
            defined += 1
        writer.writerow([index, step, len(values), deviation])
    summaries.append(
        {
            "run": index,
            "survivors": survivors[index],
            "native_seconds": float(timings[index]),
            "unique_final_members": len(set(ids)),
            "final_member_records": len(ids),
            "duplicate_members": {
                str(identifier): count
                for identifier, count in Counter(ids).items()
                if count > 1
            },
            "top_level_groups": len(groups) - 1,
            "metadata_steps_with_nonempty_group_list": sum(
                bool(value[0]) for value in types.values()
            ),
            "trade_records": trades,
            "defined_dispersion_steps": defined,
            "undefined_dispersion_steps": 1000 - defined,
        }
    )
counts, edges = np.histogram(dispersions, bins=500)
report = {
    "revision": revision,
    "input_sha256": pins,
    "runs": 100,
    "steps": 100000,
    "survivor_mean": statistics.mean(survivors),
    "survivor_sample_sd": statistics.stdev(survivors),
    "survivor_range": [min(survivors), max(survivors)],
    "native_mean_seconds": statistics.mean(map(float, timings)),
    "all_unique_final_memberships_reconcile": all(
        row["unique_final_members"] == row["survivors"] for row in summaries
    ),
    "runs_with_duplicate_final_members": sum(
        bool(row["duplicate_members"]) for row in summaries
    ),
    "runs_with_final_groups": sum(row["top_level_groups"] > 0 for row in summaries),
    "metadata_steps_with_nonempty_group_list": sum(
        row["metadata_steps_with_nonempty_group_list"] for row in summaries
    ),
    "trade_records": sum(row["trade_records"] for row in summaries),
    "defined_dispersion_steps": len(dispersions),
    "undefined_dispersion_steps": 100000 - len(dispersions),
    "histogram_counts": counts.tolist(),
    "histogram_edges": edges.tolist(),
    "survivor_counts": dict(sorted(Counter(survivors).items())),
    "per_run": summaries,
    "scope": "Author archival data, not fresh simulation. Exact notebook survivor-mean recovery; health holdings and RNG states are absent from these five files. Finite prices do not establish finite holdings. Historical one-level and threshold-five data remain unrecovered.",
}
args.output.mkdir(exist_ok=False)
(args.output / "analysis.json").write_text(json.dumps(report, indent=2) + "\n")
(args.output / "price-steps.csv.gz").write_bytes(
    gzip.compress(stream.getvalue().encode(), mtime=0)
)
print(
    json.dumps(
        {
            key: value
            for key, value in report.items()
            if key
            not in [
                "per_run",
                "histogram_counts",
                "histogram_edges",
                "survivor_counts",
                "input_sha256",
            ]
        }
    )
)
