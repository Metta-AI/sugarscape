"""Bounded stratified generated-landscape benchmark with native output audits."""

import concurrent.futures
import csv
import gzip
import hashlib
import json
import math
import subprocess
import threading
import time
from pathlib import Path

root = Path(__file__).resolve().parent
runtime = Path("/root/sugarscape/proof-002")
selection = json.loads((root / "selection.json").read_text())
assert hashlib.sha256((root / "selected.csv.gz").read_bytes()).hexdigest() == selection["selected_gzip_sha256"]
assert selection["original_sha256"] == "1a2cdf93167571ab2943d488017ace08945e7afd3cd8ac4d1410fb214c79c8f5"
assert selection["selected_rows"] == 550
with gzip.open(root / "selected.csv.gz", "rt") as stream:
    inputs = list(csv.DictReader(stream))
assert len(inputs) == 550
expected = json.loads((root / "expected-runtime.json").read_text())
for name, checksum in expected.items():
    assert hashlib.sha256((runtime / name).read_bytes()).hexdigest() == checksum, name
assert (
    hashlib.sha256((root / "GeneratedReplay.java").read_bytes()).hexdigest()
    == "c52a4dfaec12a5db99d19ba9a49f38e20cb6e40bac97ec667b49904d577182fd"
)
java = subprocess.check_output(["java", "-version"], stderr=subprocess.STDOUT, text=True)
assert 'version "11.' in java
output = root / "runs"
output.mkdir()
(root / "start.json").write_text(
    json.dumps(
        {
            "unix": time.time(),
            "workers": 8,
            "java": java,
            "source_sha256": expected,
            "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "selection_sha256": hashlib.sha256((root / "selection.json").read_bytes()).hexdigest(),
            "scope": "550input stratified throughput/fidelity sample, not full generatedensemble.",
        },
        indent=2,
    )
    + "\n"
)
failed = threading.Event()
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


def replay(index):
    if failed.is_set():
        return {"selected_row": index, "state": "not_started_after_failure"}
    out = output / f"row-{index:04d}"
    out.mkdir()
    command = [
        "/usr/bin/time",
        "-f",
        "%U %S %M",
        "-o",
        str(out / "resources.txt"),
        "java",
        "-Djava.awt.headless=true",
        "-Xmx768m",
        "-cp",
        f"{runtime}/app/NetLogo.jar:{runtime}/app/*",
        str(root / "GeneratedReplay.java"),
        str(runtime / "model/HEADLESS_Sugarscape.nlogo"),
        str(root / "selected.csv.gz"),
        str(index),
        str(index + 1),
        str(out / "results.csv"),
    ]
    (out / "command.json").write_text(json.dumps(command) + "\n")
    began = time.monotonic()
    with (out / "native.log").open("x") as log:
        result = subprocess.run(command, cwd=runtime / "model", stdout=log, stderr=subprocess.STDOUT)
    seconds = time.monotonic() - began
    (out / "exit.json").write_text(json.dumps({"exit_code": result.returncode, "elapsed_seconds": seconds}) + "\n")
    if result.returncode:
        failed.set()
        return {"selected_row": index, "state": "native_failed", "exit_code": result.returncode}
    rows = list(csv.DictReader((out / "results.csv").open()))
    assert len(rows) == 1
    row = rows[0]
    ref = inputs[index]
    assert int(row["row"]) == index and row["id"] == ref["id"] and row["seed"] == ref["replication"]
    assert float(row["population"]) == float(ref["population"]) and float(row["ticks"]) == 10000
    comparisons = []
    for metric in metrics:
        actual = float(row[metric])
        archived = float(ref[metric])
        assert math.isfinite(actual) and math.isfinite(archived)
        error = abs(actual - archived)
        tolerance = 0.0 if metric in ["gini", "mwgini"] else 1e-12
        comparisons.append(
            {
                "metric": metric,
                "actual": actual,
                "archived": archived,
                "absolute_error": error,
                "tolerance": tolerance,
                "passes": error <= tolerance,
            }
        )
    valid = all(c["passes"] for c in comparisons)
    (out / "audit.json").write_text(
        json.dumps({"input": selection["rows"][index], "comparisons": comparisons, "valid": valid}, indent=2) + "\n"
    )
    if not valid:
        failed.set()
    return {"selected_row": index, "state": "complete" if valid else "audit_failed", "elapsed_seconds": seconds}


def stop_on_exception(future):
    if future.exception():
        failed.set()


with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
    futures = []
    for index in range(550):
        future = pool.submit(replay, index)
        future.add_done_callback(stop_on_exception)
        futures.append(future)
    statuses = [future.result() for future in futures]
(root / "summary.json").write_text(
    json.dumps(
        {
            "statuses": statuses,
            "complete": all(r["state"] == "complete" for r in statuses),
            "finished_unix": time.time(),
        },
        indent=2,
    )
    + "\n"
)
assert all(r["state"] == "complete" for r in statuses)
