"""Run disjoint frozen seeds through the unchanged recovered NetLogo candidate."""

import csv
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

root = Path(sys.argv[1]).resolve()
protocol = json.loads((root / "protocol.json").read_text())
source = Path(protocol["source"])
runtime = Path(protocol["runtime"])
assert hashlib.sha256(source.read_bytes()).hexdigest() == protocol["source_sha256"]
assert hashlib.sha256((runtime / "NetLogo.jar").read_bytes()).hexdigest() == protocol["jar_sha256"]
first = protocol["first"]
for name, digest in first["files_sha256"].items():
    assert hashlib.sha256((Path(first["root"]) / name).read_bytes()).hexdigest() == digest
assert len(protocol["seeds"]) == len(set(protocol["seeds"])) == 100
assert protocol["run_interval"] == [1, 100] and first["seed"] == protocol["seeds"][0]
output = root / "runs"
output.mkdir(exist_ok=False)
(output / "manifest.json").write_text(
    json.dumps(
        {"protocol": protocol, "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}, indent=2
    )
    + "\n"
)
shutil.copy2(__file__, output / "run_ensemble.py")
limits = protocol["limits"]
started = time.monotonic()
with (output / "completed.jsonl").open("x") as ledger:
    for index in range(1, 100):
        remaining = limits["seconds_total"] - (time.monotonic() - started)
        assert remaining > 0 and shutil.disk_usage(root).free >= limits["minimum_free_bytes"]
        seed = protocol["seeds"][index]
        folder = output / f"{index:03d}-{seed}"
        folder.mkdir()
        xml = (Path(first["root"]) / "experiment.xml").read_text()
        assert xml.count(f"random-seed {first['seed']} preset4 setup false") == 1
        xml = xml.replace(f"random-seed {first['seed']} preset4 setup false", f"random-seed {seed} preset4 setup false")
        (folder / "experiment.xml").write_text(xml)
        command = json.loads((Path(first["root"]) / "command.json").read_text())
        command[command.index("--setup-file") + 1] = str(folder / "experiment.xml")
        command[command.index("--table") + 1] = str(folder / "trajectory.csv")
        (folder / "command.json").write_text(json.dumps(command, indent=2) + "\n")
        before = time.monotonic()
        with (folder / "stdout.log").open("wb") as stdout, (folder / "stderr.log").open("wb") as stderr:
            result = subprocess.run(
                command, cwd=runtime, stdout=stdout, stderr=stderr, timeout=min(remaining, limits["seconds_per_run"])
            )
        (folder / "exit.json").write_text(
            json.dumps({"exit_code": result.returncode, "elapsed_seconds": time.monotonic() - before}) + "\n"
        )
        result.check_returncode()
        assert not (folder / "stderr.log").read_bytes()
        with (folder / "trajectory.csv").open() as stream:
            rows = list(csv.reader(stream))
        header = rows[6]
        records = [dict(zip(header, row, strict=True)) for row in rows[7:]]
        assert [int(r["[step]"]) for r in records] == list(range(1001))
        assert int(records[0]["count agents"]) == 400
        raw = (folder / "trajectory.csv").read_bytes()
        with gzip.GzipFile(filename=str(folder / "trajectory.csv.gz"), mode="wb", mtime=0) as stream:
            stream.write(raw)
        record = {
            "index": index,
            "seed": seed,
            "summary_records": len(records),
            "final_population": int(records[-1]["count agents"]),
            "files_sha256": {
                f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(folder.iterdir()) if f.is_file()
            },
        }
        ledger.write(json.dumps(record) + "\n")
        ledger.flush()
        print(json.dumps({k: v for k, v in record.items() if k != "files_sha256"}), flush=True)
(output / "complete.json").write_text(json.dumps({"completed_runs": 99}) + "\n")
