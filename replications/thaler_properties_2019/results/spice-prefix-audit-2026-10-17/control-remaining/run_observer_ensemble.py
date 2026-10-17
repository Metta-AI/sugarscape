"""Run complete fixed-seed appendix trajectories with a pinned native observer."""

import argparse
import csv
import gzip
import hashlib
import json
import shutil
import subprocess
import time
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("protocol", type=Path)
parser.add_argument("variant", choices=["original", "corrected"])
parser.add_argument("output", type=Path)
parser.add_argument("--start", type=int, default=0)
parser.add_argument("--stop", type=int, default=100)
args = parser.parse_args()
assert 0 <= args.start < args.stop <= 100
protocol = json.loads(args.protocol.read_text())
variant = protocol["variants"][args.variant]
native = Path(variant["root"])
for name, digest in variant["source_sha256"].items():
    assert hashlib.sha256((native / "source" / name).read_bytes()).hexdigest() == digest, name
assert hashlib.sha256((native / "observe").read_bytes()).hexdigest() == variant["binary_sha256"]
assert hashlib.sha256((native / "Observe.hs").read_bytes()).hexdigest() == variant["observer_sha256"]
args.output.mkdir(parents=True, exist_ok=False)
(args.output / "manifest.json").write_text(
    json.dumps(
        {
            "protocol": protocol,
            "variant": args.variant,
            "interval": [args.start, args.stop],
            "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        },
        indent=2,
    )
    + "\n"
)
shutil.copy2(__file__, args.output / "run_observer_ensemble.py")
started = time.monotonic()
with (args.output / "completed.jsonl").open("x") as ledger:
    for scenario in protocol["scenarios"]:
        for index, seed in enumerate(protocol["seeds"][args.start : args.stop], start=args.start):
            remaining = protocol["limits"]["seconds_per_worker"] - (time.monotonic() - started)
            assert remaining > 0
            assert shutil.disk_usage(args.output).free >= protocol["limits"]["minimum_free_bytes"]
            folder = args.output / scenario["key"] / f"{index:03d}-{seed}"
            folder.mkdir(parents=True)
            prefix = folder / "trajectory"
            command = [
                str(native / "observe"),
                scenario["constructor"],
                str(seed),
                str(scenario["steps"]),
                str(scenario["stride"]),
                str(prefix),
            ]
            (folder / "command.json").write_text(json.dumps(command) + "\n")
            before = time.monotonic()
            with (folder / "stdout.log").open("wb") as stdout, (folder / "stderr.log").open("wb") as stderr:
                result = subprocess.run(
                    command,
                    cwd=native,
                    stdout=stdout,
                    stderr=stderr,
                    timeout=min(remaining, protocol["limits"]["seconds_per_run"]),
                )
            (folder / "exit.json").write_text(json.dumps({"exit_code": result.returncode}) + "\n")
            result.check_returncode()
            summaries = list(csv.DictReader((folder / "trajectory.summary.csv").open()))
            assert [int(r["time"]) for r in summaries] == list(range(scenario["steps"] + 1))
            for r in summaries:
                assert 0 <= int(r["infected"]) <= int(r["population"])
                assert 0 <= int(r["zero_dominant"]) <= int(r["population"])
                assert int(r["red"]) + int(r["blue"]) == int(r["population"])
            for path in folder.glob("*.csv"):
                with gzip.GzipFile(filename=str(path) + ".gz", mode="wb", mtime=0) as stream:
                    stream.write(path.read_bytes())
            record = {
                "variant": args.variant,
                "scenario": scenario["key"],
                "index": index,
                "seed": seed,
                "steps": scenario["steps"],
                "summary_rows": len(summaries),
                "final_population": int(summaries[-1]["population"]),
                "elapsed_seconds": time.monotonic() - before,
                "files_sha256": {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(folder.iterdir())},
            }
            ledger.write(json.dumps(record) + "\n")
            ledger.flush()
            print(json.dumps({k: v for k, v in record.items() if k != "files_sha256"}), flush=True)
(args.output / "complete.json").write_text(
    json.dumps({"completed_runs": len(protocol["scenarios"]) * (args.stop - args.start)}) + "\n"
)
