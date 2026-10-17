"""Execute a declared interval of the original Sugarscape CLI with fixed seeds."""

import argparse
import gzip
import hashlib
import json
import math
import re
import shutil
import subprocess
import time
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("source", type=Path)
parser.add_argument("protocol", type=Path)
parser.add_argument("scenario", choices=["carrying", "wealth", "trading"])
parser.add_argument("output", type=Path)
parser.add_argument("--start", type=int, default=0)
parser.add_argument("--stop", type=int, default=100)
parser.add_argument("--seconds", type=int, default=21600)
args = parser.parse_args()
assert 0 <= args.start < args.stop <= 100
assert 0 < args.seconds <= 21600
source = args.source.resolve()
root = args.output.resolve()
protocol = json.loads(args.protocol.read_text())
scenario = protocol["scenarios"][args.scenario]
pins = json.loads((args.protocol.parent / "source-manifest.json").read_text())["source_sha256"]
for name, digest in pins.items():
    assert hashlib.sha256((source / name).read_bytes()).hexdigest() == digest, name
compiler = subprocess.check_output(["stack", "exec", "--", "ghc", "--numeric-version"], cwd=source, text=True).strip()
assert compiler == protocol["compiler"] == "8.4.4"
install = subprocess.check_output(["stack", "path", "--local-install-root"], cwd=source, text=True).strip()
binary = Path(install) / "bin" / "sugarscape"
root.mkdir(parents=True, exist_ok=False)
manifest = {
    "protocol": protocol,
    "scenario": args.scenario,
    "interval": [args.start, args.stop],
    "seconds": args.seconds,
    "source": str(source),
    "source_sha256": pins,
    "compiler": compiler,
    "binary": str(binary),
    "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
    "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
}
(root / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
shutil.copy2(__file__, root / "run_ensemble.py")
started = time.monotonic()
with (root / "completed.jsonl").open("x") as ledger:
    for index in range(args.start, args.stop):
        remaining = args.seconds - (time.monotonic() - started)
        assert remaining > 0
        assert shutil.disk_usage(root).free >= protocol["limits"]["minimum_free_bytes"]
        seed = protocol["seeds"][index]
        folder = root / f"{index:03d}-{seed}"
        folder.mkdir()
        output = folder / "dynamics.m"
        command = [
            str(binary),
            "-s",
            scenario["native_name"],
            "-f",
            str(scenario["steps"]),
            "-o",
            str(output),
            "-r",
            str(seed),
        ]
        (folder / "command.json").write_text(json.dumps(command) + "\n")
        before = time.monotonic()
        with (folder / "stdout.log").open("wb") as log, (folder / "stderr.log").open("wb") as errors:
            result = subprocess.run(command, cwd=source, stdout=log, stderr=errors, timeout=min(1800, remaining))
        (folder / "exit.json").write_text(json.dumps({"exit_code": result.returncode}) + "\n")
        result.check_returncode()
        raw = output.read_bytes()
        lines = raw.decode().splitlines()
        assert lines[:2] == ["clear;", "dynamics = {"] and lines[-1] == "};"
        times = []
        populations = []
        agent_ids = set()
        in_step = False
        for line in lines[2:-1]:
            if line.startswith("{ "):
                assert not in_step
                times.append(int(re.fullmatch(r"\{ (\d+),", line)[1]))
                agent_ids = set()
                in_step = True
            elif line == "}":
                assert in_step
                populations.append(len(agent_ids))
                in_step = False
            else:
                assert in_step and line.startswith("[") and line.endswith("], ")
                fields = line[1:].split(", ", 7)
                assert len(fields) == 8
                agent_id = int(fields[0])
                assert agent_id not in agent_ids
                agent_ids.add(agent_id)
                assert all(math.isfinite(float(x)) for x in fields[1:7])
        assert not in_step
        assert times == list(range(1, scenario["steps"] + 1))
        assert len(populations) == scenario["steps"]
        compressed = gzip.compress(raw, mtime=0)
        assert gzip.decompress(compressed) == raw
        (folder / "dynamics.m.gz").write_bytes(compressed)
        receipt = {
            "index": index,
            "seed": seed,
            "scenario": args.scenario,
            "steps": len(times),
            "agent_observations": sum(populations),
            "final_population": populations[-1],
            "elapsed_seconds": time.monotonic() - before,
            "files_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(folder.iterdir())},
        }
        ledger.write(json.dumps(receipt) + "\n")
        ledger.flush()
        print(json.dumps(receipt), flush=True)
(root / "complete.json").write_text(json.dumps({"completed_runs": args.stop - args.start}) + "\n")
