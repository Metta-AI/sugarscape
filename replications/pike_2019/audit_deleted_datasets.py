"""Audit all recovered pre-rerun price, timing, population and composition data."""

import argparse
import csv
import gzip
import hashlib
import io
import json
import math
from pathlib import Path
import statistics

import numpy as np
from historical_pickle import ArchiveReader

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("recovery", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
raw_manifest = (args.recovery / "recovery.json").read_bytes()
assert (
    hashlib.sha256(raw_manifest).hexdigest()
    == "3f479c54b225ef358ea7443b556c09037d75e9b7282d6fd16a7d8cfbaedc142f"
)
manifest = json.loads(raw_manifest)
pins = {row["path"]: row for row in manifest["files"]}
assert len(pins) == 12
args.output.mkdir(exist_ok=False)
reports = []
for label, folder, stem, suffix in [
    ("network-10", "Policy Network", "net", "10"),
    ("network-10-policy", "Policy Network", "net", "10_policy"),
    ("explicit-10-policy", "Policy-Explicit", "brute", "10_policy"),
]:
    names = {
        "survivors": f"{stem}_multi_sur_{suffix}.p",
        "times": f"{stem}_multi_time_{suffix}.p",
        "prices": f"{'brute_' if stem == 'brute' else ''}total_price_{suffix}.p",
        "types": f"{'brute_' if stem == 'brute' else ''}type_df_{suffix}.p",
    }
    data = {}
    for key, name in names.items():
        path = f"{folder}/{name}"
        raw = (args.recovery / "raw" / path).read_bytes()
        assert len(raw) == pins[path]["bytes"]
        assert hashlib.sha256(raw).hexdigest() == pins[path]["sha256"]
        data[key] = ArchiveReader(io.BytesIO(raw)).load()
        assert len(data[key]) == 100
    keys = [f"Run{i}" for i in range(100)]
    assert list(data["prices"]) == list(data["types"]) == keys
    assert all(type(value) is int for value in data["survivors"])
    assert all(math.isfinite(value) and value > 0 for value in data["times"])
    table = io.StringIO(newline="")
    writer = csv.writer(table, lineterminator="\n")
    writer.writerow(
        [
            "run",
            "step",
            "trades",
            "invalid_prices",
            "sample_sd_log_price",
            "groups",
            "independents",
            "group_member_records",
        ]
    )
    per_run = []
    dispersions = []
    for index, key in enumerate(keys):
        prices, types = data["prices"][key], data["types"][key]
        assert list(types) == list(range(1, 1001))
        assert set(prices) <= set(range(1, 1001))
        trades = invalid = defined = 0
        duplicate_group_steps = 0
        for step in range(1, 1001):
            groups, independents = types[step]
            assert type(independents) is int
            assert all(
                len(group) in [2, 3] and type(group[-1]) is int for group in groups
            )
            group_ids = [group[0] for group in groups]
            duplicate_group_steps += len(group_ids) != len(set(group_ids))
            members = sum(group[-1] for group in groups)
            values = prices[step] if step in prices else []
            bad = sum(1 for value in values if not math.isfinite(value) or value <= 0)
            invalid += bad
            trades += len(values)
            deviation = ""
            if len(values) >= 2 and bad == 0:
                deviation = statistics.stdev([math.log(value) for value in values])
                dispersions.append(deviation)
                defined += 1
            writer.writerow(
                [
                    index,
                    step,
                    len(values),
                    bad,
                    deviation,
                    len(groups),
                    independents,
                    members,
                ]
            )
        per_run.append(
            {
                "run": index,
                "survivors": data["survivors"][index],
                "native_seconds": float(data["times"][index]),
                "final_metadata_population": independents + members,
                "final_metadata_minus_reported": independents
                + members
                - data["survivors"][index],
                "duplicate_group_id_steps": duplicate_group_steps,
                "trade_records": trades,
                "invalid_prices": invalid,
                "defined_dispersion_steps": defined,
            }
        )
    counts, edges = np.histogram(dispersions, bins=500)
    report = {
        "dataset": label,
        "input_paths": [f"{folder}/{name}" for name in names.values()],
        "runs": 100,
        "metadata_steps": 100000,
        "survivor_mean": statistics.mean(data["survivors"]),
        "native_mean_seconds": statistics.mean(map(float, data["times"])),
        "trade_records": sum(row["trade_records"] for row in per_run),
        "invalid_prices": sum(row["invalid_prices"] for row in per_run),
        "defined_dispersion_steps": len(dispersions),
        "undefined_dispersion_steps": 100000 - len(dispersions),
        "terminal_metadata_matches": sum(
            row["final_metadata_minus_reported"] == 0 for row in per_run
        ),
        "duplicate_group_id_steps": sum(
            row["duplicate_group_id_steps"] for row in per_run
        ),
        "histogram_counts": counts.tolist(),
        "histogram_edges": edges.tolist(),
        "per_run": per_run,
    }
    reports.append(report)
    with (args.output / f"{label}-runs.csv").open("x", newline="") as stream:
        run_writer = csv.DictWriter(
            stream, fieldnames=list(per_run[0]), lineterminator="\n"
        )
        run_writer.writeheader()
        run_writer.writerows(per_run)
    with (args.output / f"{label}-histogram.csv").open("x", newline="") as stream:
        histogram_writer = csv.writer(stream, lineterminator="\n")
        histogram_writer.writerow(["low", "high", "count"])
        histogram_writer.writerows(zip(edges[:-1], edges[1:], counts))
    (args.output / f"{label}.csv.gz").write_bytes(
        gzip.compress(table.getvalue().encode(), mtime=0)
    )
    print(
        json.dumps(
            {
                key: value
                for key, value in report.items()
                if key
                not in ["per_run", "histogram_counts", "histogram_edges", "input_paths"]
            }
        )
    )
summary = {
    "recovery_manifest_sha256": hashlib.sha256(raw_manifest).hexdigest(),
    "datasets": reports,
    "scope": "Three archived pre-rerun ensembles, not fresh simulations or final-paper targets. Group member counts are recorded totals, not independently recovered identities. Finite prices do not prove finite holdings; historical health and RNG states are absent.",
}
(args.output / "analysis.json").write_text(json.dumps(summary, indent=2) + "\n")
