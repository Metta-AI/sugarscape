"""Audit complete native batches against the full original generated-input archive."""

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
parser.add_argument("original", type=Path)
parser.add_argument("output", type=Path)
parser.add_argument("--bootstrap-sha256", required=True)
parser.add_argument("--recorded-root", required=True)
parser.add_argument("--seconds", type=int, required=True)
parser.add_argument("--morphology-absolute-tolerance", type=float, required=True)
args = parser.parse_args()
assert not args.output.exists()
assert 0 <= args.morphology_absolute_tolerance <= 1e-12
assert 0 < args.seconds <= 10800
assert hashlib.sha256(args.bootstrap.read_bytes()).hexdigest() == args.bootstrap_sha256
assert (
    hashlib.sha256(args.original.read_bytes()).hexdigest()
    == "26372b8698eefb1666ce8c6176f7188e55ced62fab795ff11a03cae564554199"
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
assert (
    hashlib.sha256((args.run / "GeneratedReplay.java").read_bytes()).hexdigest()
    == "c52a4dfaec12a5db99d19ba9a49f38e20cb6e40bac97ec667b49904d577182fd"
)
selection = json.loads((args.run / "selection.json").read_text())
assert (
    hashlib.sha256((args.run / "selected.csv.gz").read_bytes()).hexdigest()
    == selection["selected_gzip_sha256"]
)
with gzip.open(args.run / "selected.csv.gz", "rt") as stream:
    inputs = list(csv.DictReader(stream))
count = len(inputs)
assert count == selection["selected_rows"] == len(selection["rows"])
assert [r["selected_row"] for r in selection["rows"]] == list(range(count))
indices = [r["original_row"] for r in selection["rows"]]
assert indices == sorted(set(indices))
positions = {original: selected for selected, original in enumerate(indices)}
matched = 0
with gzip.open(args.original, "rt", newline="") as stream:
    header = next(csv.reader([stream.readline()]))
    for index, line in enumerate(stream):
        if index not in positions:
            continue
        position = positions[index]
        reference = dict(zip(header, next(csv.reader([line])), strict=True))
        assert inputs[position] == reference
        metadata = selection["rows"][position]
        assert (
            metadata["id"] == reference["id"]
            and metadata["seed"] == reference["replication"]
        )
        assert metadata["population"] == float(reference["population"])
        matched += 1
assert index + 1 == selection["original_rows"] == 2727994 and matched == count
start = json.loads((args.run / "start.json").read_text())
complete = json.loads((args.run / "complete.json").read_text())
assert json.loads((args.run / "terminal.json").read_text())["exit_code"] == 0
expected = json.loads((args.run / "expected-runtime.json").read_text())
assert start["source_sha256"] == expected and len(expected) == 51
assert (
    start["runner_sha256"]
    == hashlib.sha256((args.run / "run.py").read_bytes()).hexdigest()
)
assert start["workers"] == 8 and 'version "11.' in start["java"]
intervals = [[i * count // 8, (i + 1) * count // 8] for i in range(8)]
assert start["intervals"] == intervals
assert [r["interval"] for r in complete["results"]] == intervals
assert complete["rows"] == count and 0 < complete["elapsed_seconds"] < args.seconds
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
differences = []
exact = outside = 0
native_hashes = {}
for (first, stop), receipt in zip(intervals, complete["results"], strict=True):
    folder = args.run / f"batch-{first:04d}-{stop:04d}"
    raw = (folder / "results.csv").read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    assert digest == receipt["results_sha256"]
    native_hashes[folder.name] = digest
    status = json.loads((folder / "exit.json").read_text())
    assert (
        status["exit_code"] == 0
        and status["elapsed_seconds"] == receipt["elapsed_seconds"]
    )
    assert 0 < status["elapsed_seconds"] <= complete["elapsed_seconds"]
    remote = f"{args.recorded_root}/{folder.name}"
    command = json.loads((folder / "command.json").read_text())
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
        args.recorded_root + "/GeneratedReplay.java",
        "/root/sugarscape/proof-002/model/HEADLESS_Sugarscape.nlogo",
        args.recorded_root + "/selected.csv.gz",
        str(first),
        str(stop),
        remote + "/results.csv",
    ]
    with (folder / "results.csv").open() as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == stop - first == receipt["rows"]
    batch_exact = 0
    for position, row in enumerate(rows, first):
        reference = inputs[position]
        assert (
            int(row["row"]) == position
            and row["id"] == reference["id"]
            and row["seed"] == reference["replication"]
        )
        assert (
            float(row["population"]) == float(reference["population"])
            and float(row["ticks"]) == 10000
        )
        for metric in metrics:
            actual, target = float(row[metric]), float(reference[metric])
            assert math.isfinite(actual) and math.isfinite(target)
            difference = actual - target
            tolerance = (
                0
                if metric in ["gini", "mwgini"]
                else args.morphology_absolute_tolerance
            )
            exact += difference == 0
            batch_exact += difference == 0
            outside += abs(difference) > tolerance
            if difference:
                differences.append(
                    {
                        "original_row": indices[position],
                        "metric": metric,
                        "native": actual,
                        "archived": target,
                        "difference": difference,
                        "tolerance": tolerance,
                    }
                )
    assert receipt["exact_measurements"] == batch_exact
report = {
    "completed_inputs": count,
    "measurements": count * 12,
    "exact_measurements": exact,
    "outside_tolerance": outside,
    "differences": differences,
    "morphology_absolute_tolerance": args.morphology_absolute_tolerance,
    "gini_tolerance": 0,
    "original_rows": indices,
    "all_original_input_columns_verified": True,
    "bootstrap_sha256": args.bootstrap_sha256,
    "selection_sha256": hashlib.sha256(
        (args.run / "selection.json").read_bytes()
    ).hexdigest(),
    "native_output_sha256": native_hashes,
    "runtime_qualification": (
        "Checks immutable adapter, launch inputs, native command and declared runtime pins. "
        "Dependency binary execution provenance remains in the separate runtime preflight; "
        "this audit does not reconstruct it."
    ),
    "scope": "Only the specified completed inputs. No whole-ensemble or whole-paper conclusion.",
}
args.output.write_text(json.dumps(report, indent=2) + "\n")
print(
    json.dumps(
        {
            k: v
            for k, v in report.items()
            if k not in ["differences", "original_rows", "native_output_sha256"]
        }
    )
)
assert outside == 0, "Scientific discrepancies retained in audit output"
