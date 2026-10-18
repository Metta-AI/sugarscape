"""Run the frozen 8000-input production shard in eight native Java batches."""

import concurrent.futures
import csv
import gzip
import hashlib
import json
import subprocess
import time
from pathlib import Path

root = Path(__file__).resolve().parent
runtime = Path("/root/sugarscape/proof-002")
selection = json.loads((root / "selection.json").read_text())
assert hashlib.sha256((root / "selected.csv.gz").read_bytes()).hexdigest() == selection["selected_gzip_sha256"]
assert (
    hashlib.sha256((root / "selection.json").read_bytes()).hexdigest()
    == "f23aee3e58431a80a2cda67c72e1195f9136bccc085e190aeba255368fa445ed"
)
assert (
    hashlib.sha256((root / "GeneratedReplay.java").read_bytes()).hexdigest()
    == "c52a4dfaec12a5db99d19ba9a49f38e20cb6e40bac97ec667b49904d577182fd"
)
expected = json.loads((root / "expected-runtime.json").read_text())
for name, digest in expected.items():
    assert hashlib.sha256((runtime / name).read_bytes()).hexdigest() == digest, name
with gzip.open(root / "selected.csv.gz", "rt") as stream:
    inputs = list(csv.DictReader(stream))
assert len(inputs) == 8000
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
intervals = [(i * 8000 // 8, (i + 1) * 8000 // 8) for i in range(8)]
java = subprocess.check_output(["java", "-version"], stderr=subprocess.STDOUT, text=True)
assert 'version "11.' in java
with (root / "gnu-time-version.txt").open("w") as stream:
    subprocess.run(["/usr/bin/time", "--version"], stdout=stream, stderr=subprocess.STDOUT, check=True)
began = time.monotonic()
(root / "start.json").write_text(
    json.dumps(
        {
            "unix": time.time(),
            "java": java,
            "workers": 8,
            "intervals": intervals,
            "source_sha256": expected,
            "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        },
        indent=2,
    )
    + "\n"
)


def run(interval):
    start, stop = interval
    out = root / f"batch-{start:04d}-{stop:04d}"
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
        str(start),
        str(stop),
        str(out / "results.csv"),
    ]
    (out / "command.json").write_text(json.dumps(command) + "\n")
    started = time.monotonic()
    with (out / "native.log").open("x") as log:
        result = subprocess.run(command, cwd=runtime / "model", stdout=log, stderr=subprocess.STDOUT)
    elapsed = time.monotonic() - started
    (out / "exit.json").write_text(json.dumps({"exit_code": result.returncode, "elapsed_seconds": elapsed}) + "\n")
    assert result.returncode == 0
    rows = list(csv.DictReader((out / "results.csv").open()))
    assert len(rows) == stop - start
    differences = []
    exact = 0
    for i, row in enumerate(rows, start):
        ref = inputs[i]
        assert int(row["row"]) == i and row["id"] == ref["id"] and row["seed"] == ref["replication"]
        assert float(row["population"]) == float(ref["population"]) and float(row["ticks"]) == 10000
        for metric in metrics:
            delta = float(row[metric]) - float(ref[metric])
            exact += delta == 0
            if delta != 0:
                differences.append(
                    {
                        "selected_row": i,
                        "original_row": selection["rows"][i]["original_row"],
                        "metric": metric,
                        "native": row[metric],
                        "archived": ref[metric],
                        "difference": delta,
                    }
                )
            assert abs(delta) <= (0 if metric in ["gini", "mwgini"] else 1e-12), (i, metric, row[metric], ref[metric])
    (out / "differences.json").write_text(json.dumps(differences, indent=2) + "\n")
    return {
        "interval": interval,
        "elapsed_seconds": elapsed,
        "rows": len(rows),
        "measurements": len(rows) * 12,
        "exact_measurements": exact,
        "results_sha256": hashlib.sha256((out / "results.csv").read_bytes()).hexdigest(),
    }


with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
    results = list(pool.map(run, intervals))
(root / "complete.json").write_text(
    json.dumps(
        {
            "results": results,
            "elapsed_seconds": time.monotonic() - began,
            "rows": 8000,
            "measurements": 96000,
            "scope": "First production shard only; pending independent validation and not full generated ensemble.",
        },
        indent=2,
    )
    + "\n"
)
