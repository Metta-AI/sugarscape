"""Build and replay the unmodified released population exporter twice."""

import argparse
import csv
import hashlib
import json
import platform
import subprocess
import time
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("source", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
source = args.source.resolve()
output = args.output.resolve()
assert platform.system() == "Linux"
manifest = json.loads((source / "source-manifest.json").read_text())
for name, digest in manifest["source_sha256"].items():
    assert hashlib.sha256((source / name).read_bytes()).hexdigest() == digest, name
protocol = json.loads((source / "target-protocol.json").read_text())
assert (
    hashlib.sha256((source / "population-target.csv").read_bytes()).hexdigest()
    == protocol["artifacts"]["population-target.csv"]
)
output.mkdir(parents=True, exist_ok=False)
(output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
project = source / "criterion/sugarscape-seq"
started = time.monotonic()
with (output / "build.log").open("wb") as log:
    subprocess.run(
        ["stack", "build", "--jobs", "2"], cwd=project, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=900
    )
compiler = subprocess.check_output(["stack", "exec", "--", "ghc", "--numeric-version"], cwd=project, text=True).strip()
assert compiler == "8.4.3", compiler
install = subprocess.check_output(["stack", "path", "--local-install-root"], cwd=project, text=True).strip()
binary = Path(install) / "bin/sugarscape-seq"
records = []
for index in [1, 2]:
    assert not (project / "popSize.csv").exists()
    before = time.monotonic()
    with (output / f"run-{index}.log").open("wb") as log:
        subprocess.run(
            [str(binary)],
            cwd=project,
            stdout=log,
            stderr=subprocess.STDOUT,
            check=True,
            timeout=min(600, max(1, 1800 - (before - started))),
        )
    destination = output / f"population-{index}.csv"
    (project / "popSize.csv").rename(destination)
    with destination.open() as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 1000
    times = [float(row["T"]) for row in rows]
    population = [int(row["PopSize"]) for row in rows]
    assert times == list(range(1000))
    assert all(0 <= value <= 500 for value in population)
    assert all(after <= before for before, after in zip(population[:-1], population[1:], strict=True))
    records.append(
        {
            "run": index,
            "sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
            "rows": len(rows),
            "elapsed_seconds": time.monotonic() - before,
            "first": population[0],
            "last": population[-1],
        }
    )
    (output / f"run-{index}.json").write_text(json.dumps(records[-1], indent=2) + "\n")
assert records[0]["sha256"] == records[1]["sha256"], "Repeat replay differs"
with (source / "population-target.csv").open() as handle:
    target = list(csv.DictReader(handle))
assert [int(row["time"]) for row in target] == protocol["acceptance_frozen_before_native_output"]["times"]
errors = [abs(population[int(row["time"])] - float(row["population_digitized"])) for row in target]
threshold = protocol["acceptance_frozen_before_native_output"]["maximum_absolute_population_error"]
result = {
    "source_revision": manifest["revision"],
    "compiler": compiler,
    "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
    "runs": records,
    "target_protocol": protocol,
    "absolute_errors": errors,
    "maximum_error": max(errors),
    "within_threshold": sum(error <= threshold for error in errors),
    "matches_frozen_figure_target": all(error <= threshold for error in errors),
    "scope": (
        "Sequential Figure5 population replay only. "
        "Does not establish full paper replication or performance/scaling claims."
    ),
}
(output / "comparison.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result))
