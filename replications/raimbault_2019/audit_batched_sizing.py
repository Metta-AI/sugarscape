"""Audit the completed frozen eight-process sizing workflow and native measurements."""

import argparse
import csv
import gzip
import hashlib
import json
import math
from pathlib import Path
import tarfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("run", type=Path)
parser.add_argument("bootstrap", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
assert not args.output.exists()
assert (
    hashlib.sha256(args.bootstrap.read_bytes()).hexdigest()
    == "4be24f5536dc76bf459f07d11791af3ccdb467bf9e75447f1ef4622736fc8f0f"
)
with tarfile.open(args.bootstrap) as archive:
    for name in [
        "run.py",
        "GeneratedReplay.java",
        "selected.csv.gz",
        "selection.json",
        "expected-runtime.json",
    ]:
        assert archive.extractfile(name).read() == (args.run / name).read_bytes(), name
selection = json.loads((args.run / "selection.json").read_text())
with gzip.open(args.run / "selected.csv.gz", "rt") as stream:
    inputs = list(csv.DictReader(stream))
assert len(inputs) == selection["selected_rows"] == 550
assert len({(row["id"], row["population"]) for row in selection["rows"]}) == 550
assert sum(row["stratum_rows"] for row in selection["rows"]) == 2727994
start = json.loads((args.run / "start.json").read_text())
complete = json.loads((args.run / "complete.json").read_text())
expected = json.loads((args.run / "expected-runtime.json").read_text())
assert start["source_sha256"] == expected
assert (
    start["runner_sha256"]
    == hashlib.sha256((args.run / "run.py").read_bytes()).hexdigest()
)
assert start["workers"] == 8 and 'version "11.' in start["java"]
model_files = sorted(p for p in (args.run / "runtime").rglob("*") if p.is_file())
for path in model_files:
    assert (
        hashlib.sha256(path.read_bytes()).hexdigest()
        == expected[str(path.relative_to(args.run / "runtime"))]
    )
assert len(model_files) == 14
intervals = [[i * 550 // 8, (i + 1) * 550 // 8] for i in range(8)]
assert start["intervals"] == intervals
assert [row["interval"] for row in complete["results"]] == intervals
metrics = [
    "gini",
    "mwgini",
    "moran",
    "distance",
    "entropy",
    "slope",
    "rsquared",
    "moranRessource",
    "distanceRessource",
    "entropyRessource",
    "slopeRessource",
    "rsquaredRessource",
]
results = []
for (first, stop), receipt in zip(intervals, complete["results"], strict=True):
    folder = args.run / f"batch-{first:04d}-{stop:04d}"
    output = folder / "results.csv"
    assert hashlib.sha256(output.read_bytes()).hexdigest() == receipt["results_sha256"]
    status = json.loads((folder / "exit.json").read_text())
    assert (
        status["exit_code"] == 0
        and status["elapsed_seconds"] == receipt["elapsed_seconds"]
    )
    assert 0 < status["elapsed_seconds"] < 3600
    command = json.loads((folder / "command.json").read_text())
    remote = f"/root/sugarscape/batched-sizing-001/{folder.name}"
    assert command == [
        "/usr/bin/time",
        "-f",
        "%U %S %M",
        "-o",
        remote + "/resources.txt",
        "java",
        "-Djava.awt.headless=true",
        "-Xmx768m",
        "-cp",
        "/root/sugarscape/proof-002/app/NetLogo.jar:/root/sugarscape/proof-002/app/*",
        "/root/sugarscape/batched-sizing-001/GeneratedReplay.java",
        "/root/sugarscape/proof-002/model/HEADLESS_Sugarscape.nlogo",
        "/root/sugarscape/batched-sizing-001/selected.csv.gz",
        str(first),
        str(stop),
        remote + "/results.csv",
    ]
    rows = list(csv.DictReader(output.open()))
    assert len(rows) == stop - first == receipt["rows"]
    for index, row in enumerate(rows, first):
        reference = inputs[index]
        assert (
            int(row["row"]) == index
            and row["id"] == reference["id"]
            and row["seed"] == reference["replication"]
        )
        assert (
            float(row["population"]) == float(reference["population"])
            and float(row["ticks"]) == 10000
        )
        for metric in metrics:
            value = float(row[metric])
            assert math.isfinite(value) and value == float(reference[metric]), (
                index,
                metric,
            )
    assert receipt["exact_measurements"] == len(rows) * 12
    user, system, rss = map(float, (folder / "resources.txt").read_text().split())
    assert all(math.isfinite(value) and value > 0 for value in [user, system, rss])
    results.append(
        {
            "interval": [first, stop],
            "cpu_seconds": user + system,
            "wall_seconds": status["elapsed_seconds"],
            "peak_rss_kib": rss,
        }
    )
for name, limit in [("terminal.json", 3600), ("bootstrap-terminal.json", 4200)]:
    terminal = json.loads((args.run / name).read_text())
    assert terminal["exit_code"] == 0 and terminal["limit_seconds"] == limit
    assert 0 < terminal["finished_unix"] - terminal["started_unix"] <= limit
assert complete["rows"] == 550 and complete["exact_measurements"] == 6600
assert max(row["wall_seconds"] for row in results) <= complete["elapsed_seconds"] < 3600
report = {
    "completed_inputs": 550,
    "exact_measurements": 6600,
    "maximum_error": 0.0,
    "batch_count": 8,
    "elapsed_seconds": complete["elapsed_seconds"],
    "cpu_seconds": sum(row["cpu_seconds"] for row in results),
    "retained_model_files_verified": len(model_files),
    "runtime_pins": len(expected),
    "runtime_qualification": "Dependency hashes are pinned in the producer manifest; dependency binaries are not contained in this result archive.",
    "batches": results,
    "scope": "Aggregate sample throughput only; no stratum-weighted full-workload cost projection.",
    "files_sha256": {
        str(p.relative_to(args.run)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(args.run.rglob("*"))
        if p.is_file()
    },
}
args.output.write_text(json.dumps(report, indent=2) + "\n")
print(
    json.dumps(
        {k: v for k, v in report.items() if k not in ["batches", "files_sha256"]}
    )
)
