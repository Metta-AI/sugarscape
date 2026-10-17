"""Audit the frozen serial timing ensemble directly from its retained archive."""

import argparse
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import random
import subprocess
import tarfile

import numpy as np
from scipy import stats

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("archive", type=Path)
parser.add_argument("engine", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
assert not args.output.exists()
assert (
    subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=args.engine, text=True
    ).strip()
    == "585e53398f4f58e89ec184c83bb20819f0e4c96a"
)
source = Path(__file__).parent
hashes, metadata, native, health = {}, {}, {}, {}
with tarfile.open(args.archive, "r|gz") as archive:
    for member in archive:
        if not member.isfile():
            continue
        name = member.name
        assert name not in hashes
        data = archive.extractfile(member).read()
        hashes[name] = hashlib.sha256(data).hexdigest()
        leaf = Path(name).name
        if leaf.endswith(".json") and leaf not in {
            "prices.json",
            "initial-agents.json",
            "observations.json",
        }:
            metadata[name] = json.loads(data)
        elif leaf == "completed.jsonl":
            records = [json.loads(line) for line in data.splitlines()]
        elif leaf == "native-times.csv":
            rows = list(csv.DictReader(io.StringIO(data.decode())))
            values = [float(row["Time Per Step"]) for row in rows]
            assert len(values) == 1000 and all(
                math.isfinite(v) and v >= 0 for v in values
            )
            native[str(Path(name).parent)] = math.fsum(values)
        elif leaf == "health.csv":
            count = invalid = 0
            for row in csv.DictReader(io.StringIO(data.decode())):
                assert 1 <= int(row["Step"]) <= 1000
                count += 1
                invalid += not all(
                    math.isfinite(float(row[k])) for k in ["Sugar_Level", "Spice_Level"]
                )
            health[str(Path(name).parent)] = {
                "records": count,
                "nonfinite_records": invalid,
            }
manifest = metadata["benchmark/manifest.json"]
assert manifest["required_runs"] == 900 and manifest["workers"] == 1
assert manifest["python"] == "3.11.14"
assert set(manifest["thread_environment"].values()) == {"1"}
for name, digest in manifest["source_sha256"].items():
    assert (
        hashes["benchmark/" + name]
        == digest
        == hashlib.sha256((source / name).read_bytes()).hexdigest()
    )
conditions = [(name, [name]) for name in ["standard", "explicit", "network"]]
conditions += [
    (f"{approach}-{policy}", [approach, "10", policy])
    for approach in ["explicit", "network"]
    for policy in ["none", "movement"]
]
conditions += [(name, [name]) for name in ["common-one", "common-multi"]]
schedule = []
rng = random.Random(20261017)
for seed in range(100):
    block = conditions.copy()
    rng.shuffle(block)
    schedule.extend(
        {"seed": seed, "condition": name, "arguments": arguments}
        for name, arguments in block
    )
assert manifest["schedule"] == schedule
assert len(records) == 900 and [r["ordinal"] for r in records] == list(range(900))
assert metadata["benchmark/complete.json"]["completed_runs"] == 900
parity = metadata["benchmark/parity-complete.json"]
assert parity["pairs"] == 9 and parity["exact_files"] == 36
assert [p["condition"] for p in parity["controls"]] == [c[0] for c in conditions]
receipts = [(f"ensemble-timed-{r['condition']}-{r['seed']}", r) for r in records]
for control in parity["controls"]:
    for flavor in ["observed", "timed"]:
        r = control[flavor]
        assert r["seed"] == 1001 and r["condition"] == control["condition"]
        receipts.append((f"control-{flavor}-{r['condition']}-1001", r))
    for name in control["exact_files"]:
        assert control["observed"]["sha256"][name] == control["timed"]["sha256"][name]
for stem, receipt in receipts:
    assert receipt["exit_code"] == 0
    recorded_exit = metadata["benchmark/" + stem + ".exit.json"]
    assert recorded_exit == {
        k: receipt[k] for k in ["condition", "seed", "flavor", "command", "exit_code"]
    }
    assert {
        name.removeprefix("benchmark/" + stem + "/")
        for name in hashes
        if name.startswith("benchmark/" + stem + "/")
    } == set(receipt["sha256"])
    for name, digest in receipt["sha256"].items():
        assert hashes[f"benchmark/{stem}/{name}"] == digest
variants = {
    "standard": "Initial/NetScape_Standard",
    "explicit": "Initial/NetScape_Brute",
    "network": "Initial/NetScape_Elegant",
    "policy-explicit": "Policy-Explicit",
    "groups-network": "Policy-Network",
    "common-one": "Common Resource- one level",
    "common-multi": "Common Resource- multi-level",
}
measurements = []
for record, item in zip(records, schedule, strict=True):
    assert (record["seed"], record["condition"], record["flavor"]) == (
        item["seed"],
        item["condition"],
        "timed",
    )
    stem = f"benchmark/ensemble-timed-{item['condition']}-{item['seed']}"
    command = record["command"]
    assert command[4:-2] == item["arguments"] and command[-2] == str(item["seed"])
    assert Path(command[-1]).name == Path(stem).name
    grouped = len(item["arguments"]) == 3
    root = stem + "/run" if grouped else stem
    if grouped:
        config = metadata[stem + "/configuration.json"]
        assert [
            config[k] for k in ["approach", "threshold", "policy", "seed", "steps"]
        ] == [item["arguments"][0], 10, item["arguments"][2], item["seed"], 1000]
        assert config["source_sha256"] == manifest["source_sha256"]["run_groups.py"]
        assert metadata[stem + "/parameterization-complete.json"] == {
            "grouping_calls": 1000
        }
    m = metadata[root + "/manifest.json"]
    variant = (
        ("policy-explicit" if item["arguments"][0] == "explicit" else "groups-network")
        if grouped
        else item["condition"]
    )
    assert m["variant"] == variant
    assert [m[k] for k in ["python", "mesa", "numpy", "networkx"]] == [
        "3.11.14",
        "0.8.5",
        "1.26.4",
        "3.6.1",
    ]
    assert [
        m[k]
        for k in [
            "numpy_seed",
            "policy_random_seed",
            "mesa_seed",
            "pythonhashseed",
            "steps",
        ]
    ] == [item["seed"], item["seed"], 42, "0", 1000]
    assert (
        m["revision"] == "585e53398f4f58e89ec184c83bb20819f0e4c96a"
        and m["library_revision"] == "99d2091721076df9fff32e8b49a0e33e98c34a6f"
    )
    assert m["runner_sha256"] == manifest["source_sha256"]["run_timing.py"]
    expected = {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest()
        for p in (args.engine / variants[variant]).glob("*.py")
    }
    assert m["source_hashes"] == expected
    timing = metadata[root + "/timing.json"]
    assert timing["steps"] == 1000
    metrics = {
        k: timing[k]
        for k in [
            "full_step_wall_seconds",
            "full_step_cpu_seconds",
            "native_timed_sections_seconds",
        ]
    }
    assert all(math.isfinite(v) and v > 0 for v in metrics.values())
    assert math.isclose(
        native[root],
        timing["native_timed_sections_seconds"],
        rel_tol=1e-12,
        abs_tol=1e-9,
    )
    assert (
        metadata[root + "/complete.json"]["elapsed"] == timing["full_step_wall_seconds"]
    )
    measurements.append(
        {
            "condition": item["condition"],
            "seed": item["seed"],
            **metrics,
            **health[root],
        }
    )
comparisons = []
for numerator, denominator in [
    ("explicit", "standard"),
    ("network", "standard"),
    ("explicit-none", "network-none"),
    ("explicit-movement", "network-movement"),
    ("common-multi", "common-one"),
]:
    for metric in metrics:
        a = np.array(
            [
                next(
                    r[metric]
                    for r in measurements
                    if r["condition"] == numerator and r["seed"] == seed
                )
                for seed in range(100)
            ]
        )
        b = np.array(
            [
                next(
                    r[metric]
                    for r in measurements
                    if r["condition"] == denominator and r["seed"] == seed
                )
                for seed in range(100)
            ]
        )
        for statistic, values in [
            ("paired_difference_seconds", a - b),
            ("paired_ratio", a / b),
        ]:
            mean = float(values.mean())
            margin = float(stats.t.ppf(0.975, 99) * stats.sem(values))
            comparisons.append(
                {
                    "numerator": numerator,
                    "denominator": denominator,
                    "metric": metric,
                    "statistic": statistic,
                    "n": 100,
                    "mean": mean,
                    "pointwise_ci95": [mean - margin, mean + margin],
                }
            )
report = {
    "runs": 900,
    "steps_checked": 900000,
    "control_pairs": 9,
    "parity_files": 36,
    "archive_sha256": hashlib.sha256(args.archive.read_bytes()).hexdigest(),
    "measurements": measurements,
    "comparisons": comparisons,
    "scope": "Native relative timing on this environment, not historical seconds. Common-resource nonfinite states remain invalid economic outcomes. Pointwise paired t intervals; no whole-paper credit.",
}
args.output.mkdir()
(args.output / "audit.json").write_text(
    json.dumps(report, indent=2, allow_nan=False) + "\n"
)
(args.output / "files-sha256.json").write_text(json.dumps(hashes, indent=2) + "\n")
print(
    json.dumps(
        {
            "runs": 900,
            "steps_checked": 900000,
            "nonfinite_health_records": sum(
                r["nonfinite_records"] for r in measurements
            ),
        }
    )
)
