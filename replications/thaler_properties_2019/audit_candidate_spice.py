"""Audit all candidate NetLogo spice trajectories; only full cohorts emit inference."""

import argparse
import csv
import gzip
import hashlib
import io
import json
import math
from pathlib import Path
import re

import numpy as np
from scipy import stats

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("protocol", type=Path)
parser.add_argument("run", type=Path)
parser.add_argument("first", type=Path)
parser.add_argument("output", type=Path)
parser.add_argument("--recorded-run-root", type=Path)
parser.add_argument("--allow-prefix", action="store_true")
args = parser.parse_args()
assert not args.output.exists()
protocol = json.loads(args.protocol.read_text())
manifest = json.loads((args.run / "manifest.json").read_text())
assert manifest["protocol"] == protocol
assert (
    hashlib.sha256((args.run / "run_ensemble.py").read_bytes()).hexdigest()
    == manifest["runner_sha256"]
)
assert (
    hashlib.sha256(Path(protocol["source"]).read_bytes()).hexdigest()
    == protocol["source_sha256"]
)
assert (
    hashlib.sha256((Path(protocol["runtime"]) / "NetLogo.jar").read_bytes()).hexdigest()
    == protocol["jar_sha256"]
)
assert (
    len(protocol["seeds"])
    == len(set(protocol["seeds"]))
    == protocol["replications"]
    == 100
)
assert (
    protocol["run_interval"] == [1, 100]
    and protocol["steps"] == 1000
    and protocol["preset"] == "preset4"
)
observer = protocol["observer"]
reference = Path(observer["reference_source"]).read_bytes()
wrappers = Path(observer["reporters"]).read_bytes()
assert hashlib.sha256(reference).hexdigest() == observer["reference_source_sha256"]
assert hashlib.sha256(wrappers).hexdigest() == observer["reporters_sha256"]
original_parts = reference.split(b"@#$#@#$#@")
observed_parts = Path(protocol["source"]).read_bytes().split(b"@#$#@#$#@")
assert observed_parts[0] == original_parts[0] + wrappers
assert observed_parts[1:] == original_parts[1:]
first = protocol["first"]
assert first["index"] == 0 and first["seed"] == protocol["seeds"][0]
for name, digest in first["files_sha256"].items():
    assert hashlib.sha256((args.first / name).read_bytes()).hexdigest() == digest
ledger = (args.run / "completed.jsonl").read_bytes()
assert ledger.endswith(b"\n")
completed = [json.loads(line) for line in ledger.splitlines()]
assert 0 < len(completed) <= 99
assert [r["index"] for r in completed] == list(range(1, len(completed) + 1))
if not args.allow_prefix:
    assert len(completed) == 99, "All 99 remaining inputs required"
    assert json.loads((args.run / "complete.json").read_text()) == {
        "completed_runs": 99
    }
recorded_root = args.recorded_run_root if args.recorded_run_root else args.run.resolve()
first_xml = (args.first / "experiment.xml").read_text()
first_command = json.loads((args.first / "command.json").read_text())
reports = []
for index, root, pins in [(0, args.first, first["files_sha256"])] + [
    (r["index"], args.run / f"{r['index']:03d}-{r['seed']}", r["files_sha256"])
    for r in completed
]:
    seed = protocol["seeds"][index]
    raw = (
        (root / "trajectory.csv").read_bytes()
        if index == 0
        else gzip.decompress((root / "trajectory.csv.gz").read_bytes())
    )
    for name, digest in pins.items():
        data = raw if name == "trajectory.csv" else (root / name).read_bytes()
        assert hashlib.sha256(data).hexdigest() == digest
    assert (root / "experiment.xml").read_text() == first_xml.replace(
        f"random-seed {first['seed']} preset4 setup false",
        f"random-seed {seed} preset4 setup false",
    )
    if index:
        assert completed[index - 1]["seed"] == seed
        expected = first_command.copy()
        expected[expected.index("--setup-file") + 1] = str(
            recorded_root / root.name / "experiment.xml"
        )
        expected[expected.index("--table") + 1] = str(
            recorded_root / root.name / "trajectory.csv"
        )
        assert json.loads((root / "command.json").read_text()) == expected
    assert json.loads((root / "exit.json").read_text())["exit_code"] == 0
    assert not (root / "stderr.log").read_bytes()
    rows = list(csv.reader(io.StringIO(raw.decode())))
    assert rows[0] == ["BehaviorSpace Table data (NetLogo 4.0.4)"]
    assert rows[4] == ["min-pxcor", "max-pxcor", "min-pycor", "max-pycor"]
    assert rows[5] == ["-25", "25", "-25", "25"]
    header = [
        observer["reporter_mapping"][name]
        if name in observer["reporter_mapping"]
        else name
        for name in rows[6]
    ]
    records = [dict(zip(header, row, strict=True)) for row in rows[7:]]
    assert [int(r["[step]"]) for r in records] == list(range(1001))
    assert all(
        int(r["[run number]"]) == 1 and int(r["ticks"]) == int(r["[step]"])
        for r in records
    )
    assert int(records[0]["count agents"]) == 400
    observations = 0
    previous_ids = set()
    timelines = []
    for record in records:
        stack = []
        states = []
        for token in re.findall(r"\[|\]|[^\s\[\]]+", record[header[-1]]):
            if token == "[":
                entry = []
                if stack:
                    stack[-1].append(entry)
                else:
                    assert not states
                    states = entry
                stack.append(entry)
            elif token == "]":
                stack.pop()
            else:
                stack[-1].append(float(token))
        assert not stack
        assert len(states) == int(record["count agents"])
        assert all(len(a) == 9 and all(math.isfinite(x) for x in a) for a in states)
        ids = {a[0] for a in states}
        assert len(ids) == len(states)
        assert all(
            a[0] == int(a[0])
            and -25 <= a[1] <= 25
            and -25 <= a[2] <= 25
            and a[4] >= 0
            and a[5] >= 0
            for a in states
        )
        if int(record["[step]"]) > 0:
            assert ids <= previous_ids
        assert len({(a[1], a[2]) for a in states}) == len(states)
        assert all(
            a[3] == int(record["[step]"])
            and 1 <= a[6] <= 4
            and 1 <= a[7] <= 4
            and 1 <= a[8] <= 6
            for a in states
        )
        if int(record["[step]"]) == 0:
            assert all(5 <= a[4] <= 25 and 5 <= a[5] <= 25 for a in states)
        previous_ids = ids
        for i, resource in [(4, "sugar"), (5, "spice")]:
            assert math.isclose(
                sum(a[i] for a in states),
                float(record[f"sum [{resource}] of agents"]),
                rel_tol=1e-12,
                abs_tol=1e-8,
            )
        assert all(math.isfinite(float(record[k])) for k in header[:-1])
        observations += len(states)
        timelines.append(
            {
                "time": int(record["ticks"]),
                "population": len(states),
                "agent_sugar": float(record["sum [sugar] of agents"]),
                "agent_spice": float(record["sum [spice] of agents"]),
            }
        )
    populations = [r["population"] for r in timelines]
    if index:
        assert completed[index - 1]["final_population"] == populations[-1]
        assert completed[index - 1]["summary_records"] == len(records)
    reports.append(
        {
            "index": index,
            "seed": seed,
            "trajectory_sha256": hashlib.sha256(raw).hexdigest(),
            "summary_records": len(records),
            "agent_observations": observations,
            "population_trajectory": populations,
            "metrics": {
                "at100": populations[100],
                "at500": populations[500],
                "at1000": populations[1000],
                "late801_1000": float(np.mean(populations[801:])),
            },
            "first_below90": next(
                (i for i, n in enumerate(populations) if n < 90), None
            ),
        }
    )
comparisons = []
if not args.allow_prefix:
    assert len(reports) == 100
    for metric in reports[0]["metrics"]:
        values = np.array([r["metrics"][metric] for r in reports])
        mean = float(values.mean())
        margin = float(stats.t.ppf(0.975, 99) * stats.sem(values))
        comparisons.append(
            {
                "metric": metric,
                "n": 100,
                "mean": mean,
                "ci95": [mean - margin, mean + margin],
            }
        )
report = {
    "validated_unique_inputs": len(reports),
    "complete_ensemble": not args.allow_prefix,
    "agent_observations": sum(r["agent_observations"] for r in reports),
    "protocol_sha256": hashlib.sha256(args.protocol.read_bytes()).hexdigest(),
    "auditor_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "ledger_sha256": hashlib.sha256(ledger).hexdigest(),
    "results": reports,
    "comparisons": comparisons,
    "scope": "Recovered candidate NetLogo4.0.4/Java11 with RNG-isolated observers;2009 source identity unverified. Retained first seed counts once; replay excluded. Prefixes emit no inference; no paper credit.",
}
args.output.mkdir()
(args.output / "ledger-snapshot.jsonl").write_bytes(ledger)
(args.output / "audit.json").write_text(
    json.dumps(report, indent=2, allow_nan=False) + "\n"
)
print(json.dumps({k: v for k, v in report.items() if k != "results"}))
