"""Audit original A10 spice trajectories and reused trade-off controls."""

import argparse
import csv
import gzip
import hashlib
import io
import json
import math
from pathlib import Path

import numpy as np
from scipy import stats


def audit_trajectory(root, record, scenario, variant):
    folder = root / record["scenario"] / f"{record['index']:03d}-{record['seed']}"
    for name, digest in record["files_sha256"].items():
        data = (
            gzip.decompress((folder / (name + ".gz")).read_bytes())
            if name.endswith(".csv")
            else (folder / name).read_bytes()
        )
        assert hashlib.sha256(data).hexdigest() == digest, str(folder / name)
    assert json.loads((folder / "exit.json").read_text()) == {"exit_code": 0}
    command = json.loads((folder / "command.json").read_text())
    assert len(command) == 6 and command[:5] == [
        variant["root"] + "/observe",
        scenario["constructor"],
        str(record["seed"]),
        "1000",
        "10",
    ]
    assert command[-1].endswith(
        f"/{record['scenario']}/{record['index']:03d}-{record['seed']}/trajectory"
    )
    rows = {}
    for kind in ["summary", "agents", "cells", "trades"]:
        raw = gzip.decompress((folder / f"trajectory.{kind}.csv.gz").read_bytes())
        rows[kind] = list(csv.DictReader(io.StringIO(raw.decode())))
        assert all(
            math.isfinite(float(value))
            for row in rows[kind]
            for key, value in row.items()
            if key != "culture"
        )
    summaries = rows["summary"]
    assert [int(r["time"]) for r in summaries] == list(range(1001))
    assert not rows["trades"] and all(int(r["trade_count"]) == 0 for r in summaries)
    agents = {t: [] for t in range(0, 1001, 10)}
    for row in rows["agents"]:
        agents[int(row["time"])].append(row)
    for time, group in agents.items():
        assert (
            len(group)
            == len({r["id"] for r in group})
            == int(summaries[time]["population"])
        )
        for field in ["sugar", "spice"]:
            assert math.isclose(
                sum(float(r[field]) for r in group),
                float(summaries[time]["agent_" + field]),
                rel_tol=1e-12,
                abs_tol=1e-9,
            )
    assert set(int(r["time"]) for r in rows["cells"]) == {0, 1000}
    populations = [int(r["population"]) for r in summaries]
    assert populations[0] == 400 and populations[-1] == record["final_population"]
    # Both original configurations disable birth and replacement.
    assert all(a >= b for a, b in zip(populations, populations[1:]))
    text = (folder / "trajectory.scenario.txt").read_text().splitlines()
    assert text[0] == "Constructor: " + scenario["constructor"]
    assert text[1] == "Seed: " + str(record["seed"])
    below = [t for t, n in enumerate(populations) if n < 90]
    return {
        "population_trajectory": populations,
        "snapshot_agent_observations": len(rows["agents"]),
        "population_metrics": {
            "at100": populations[100],
            "at500": populations[500],
            "at1000": populations[1000],
            "late801_1000": float(np.mean(populations[801:])),
        },
        "first_below90": below[0] if below else None,
        "extinct": populations[-1] == 0,
    }, text


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("protocol", type=Path)
parser.add_argument("native", type=Path)
parser.add_argument("output", type=Path)
parser.add_argument("--book", type=Path, nargs="+", required=True)
parser.add_argument("--control", type=Path, nargs="+", required=True)
parser.add_argument("--allow-prefix", action="store_true")
args = parser.parse_args()
protocol = json.loads(args.protocol.read_text())
variant = protocol["variants"]["original"]
assert (
    protocol["replications"]
    == len(protocol["seeds"])
    == len(set(protocol["seeds"]))
    == 100
)
assert protocol["scenarios"] == [
    {
        "key": "spice_book",
        "constructor": "mkParamsAnimationIV_1",
        "steps": 1000,
        "stride": 10,
    }
]
for name, digest in variant["source_sha256"].items():
    assert (
        hashlib.sha256((args.native / "source" / name).read_bytes()).hexdigest()
        == digest
    )
assert (
    hashlib.sha256((args.native / "observe").read_bytes()).hexdigest()
    == variant["binary_sha256"]
)
assert (
    hashlib.sha256((args.native / "Observe.hs").read_bytes()).hexdigest()
    == variant["observer_sha256"]
)
records = {}
ledgers = []
ledger_snapshots = []
for key, constructor, roots in [
    ("spice_book", "mkParamsAnimationIV_1", args.book),
    ("trade_off", "mkCarryingCapacityWithSpice", args.control),
]:
    records[key] = {}
    reserved = set()
    for root in roots:
        manifest = json.loads((root / "manifest.json").read_text())
        run_protocol = manifest["protocol"]
        assert manifest["variant"] == "original"
        assert run_protocol["variants"]["original"] == variant
        assert run_protocol["seeds"] == protocol["seeds"]
        scenario = [s for s in run_protocol["scenarios"] if s["key"] == key]
        assert scenario == [
            {"key": key, "constructor": constructor, "steps": 1000, "stride": 10}
        ]
        if key == "spice_book":
            assert run_protocol == protocol
        assert (
            hashlib.sha256((root / "run_observer_ensemble.py").read_bytes()).hexdigest()
            == manifest["runner_sha256"]
        )
        start, stop = manifest["interval"]
        assert 0 <= start < stop <= 100
        indices = set(range(start, stop))
        assert not reserved.intersection(indices), "Duplicate execution intervals"
        reserved.update(indices)
        raw = (root / "completed.jsonl").read_bytes()
        ledger_snapshots.append(raw)
        ledger = [json.loads(line) for line in raw.splitlines()]
        expected = [
            (s["key"], i) for s in run_protocol["scenarios"] for i in range(start, stop)
        ]
        assert len(ledger) <= len(expected)
        assert [(r["scenario"], r["index"]) for r in ledger] == expected[: len(ledger)]
        selected = [r for r in ledger if r["scenario"] == key]
        if not args.allow_prefix:
            assert [r["index"] for r in selected] == list(range(start, stop)), (
                "Incomplete selected scenario"
            )
        ledgers.append(
            {
                "root": str(root),
                "sha256": hashlib.sha256(raw).hexdigest(),
                "selected_scenario": key,
                "selected_records": len(selected),
            }
        )
        for record in selected:
            assert (
                record["variant"] == "original"
                and record["steps"] == 1000
                and record["summary_rows"] == 1001
            )
            assert record["seed"] == protocol["seeds"][record["index"]]
            records[key][record["index"]] = (root, record, scenario[0])
paired = sorted(set(records["spice_book"]).intersection(records["trade_off"]))
assert paired, "No matched completed seeds"
if not args.allow_prefix:
    assert paired == list(range(100)), "All100 seeds required for both configurations"
results = []
labels = [
    "Constructor:",
    "Scenario:",
    "Vision range:",
    "Sugar metabolism range:",
    "Spice metabolism range:",
]
for index in paired:
    row = {"index": index, "seed": protocol["seeds"][index], "scenarios": {}}
    texts = []
    for key in ["spice_book", "trade_off"]:
        root, record, scenario = records[key][index]
        measured, text = audit_trajectory(root, record, scenario, variant)
        row["scenarios"][key] = measured
        texts.append(text)
    assert len(texts[0]) == len(texts[1])
    differences = [(a, b) for a, b in zip(*texts) if a != b]
    assert len(differences) == len(labels)
    for difference, label in zip(differences, labels):
        assert all(s.startswith(label) for s in difference)
    assert differences[2][0].endswith("(1,10)") and differences[2][1].endswith("(1,6)")
    assert all(a.endswith("(1,5)") and b.endswith("(1,4)") for a, b in differences[3:])
    results.append(row)
comparisons = []
if not args.allow_prefix:
    for metric in results[0]["scenarios"]["spice_book"]["population_metrics"]:
        arrays = [
            np.array(
                [r["scenarios"][key]["population_metrics"][metric] for r in results]
            )
            for key in ["spice_book", "trade_off"]
        ]
        estimates = {}
        for label, values in zip(
            ["spice_book", "trade_off", "book_minus_control"],
            [*arrays, arrays[0] - arrays[1]],
        ):
            mean = float(values.mean())
            margin = float(stats.t.ppf(0.975, 99) * stats.sem(values))
            estimates[label] = {"mean": mean, "ci95": [mean - margin, mean + margin]}
        comparisons.append({"metric": metric, "n": 100, "estimates": estimates})
report = {
    "protocol_sha256": hashlib.sha256(args.protocol.read_bytes()).hexdigest(),
    "auditor_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "complete_ensemble": not args.allow_prefix,
    "validated_pairs": len(paired),
    "source_files_verified": len(variant["source_sha256"]),
    "ledgers": ledgers,
    "unpaired_records_not_audited": {
        key: sorted(set(value) - set(paired)) for key, value in records.items()
    },
    "results": results,
    "comparisons": comparisons,
    "scope": "Original A10 configurations,100seed cohorts. Initial agents can differ. Population endpoints and late windows remain explicit; no exact-point or invented-equivalence verdict for approximate appendix values. Prefixes emit no inference.",
}
assert not args.output.exists()
snapshot_dir = args.output.with_name(args.output.stem + "-ledgers")
snapshot_dir.mkdir()
for index, raw in enumerate(ledger_snapshots):
    (snapshot_dir / f"{index:02d}.jsonl").write_bytes(raw)
report["ledger_snapshot_directory"] = snapshot_dir.name
with args.output.open("x") as stream:
    stream.write(json.dumps(report, indent=2, allow_nan=False) + "\n")
print(
    json.dumps(
        {
            "validated_pairs": len(paired),
            "complete_ensemble": report["complete_ensemble"],
            "comparisons": comparisons,
        }
    )
)
