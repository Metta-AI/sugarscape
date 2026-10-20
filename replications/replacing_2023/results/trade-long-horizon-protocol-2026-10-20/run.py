"""Bounded native long-horizon qualification with exact retained-prefix validation."""
from pathlib import Path
import gzip
import hashlib
import json
import os
import shutil
import subprocess
import sys

root = Path(__file__).resolve().parent
base = root.parent.parent
engine = base / "sugarscape-dtl-replacing-reference"
prior = base / "sugarscape-replacing/replications/replacing_2023/results/trade-lending-paired20-2026-10-15"
p = json.loads((root / "protocol.json").read_bytes())
assert shutil.disk_usage(root).free > 3 * 1024**3
assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=engine, text=True).strip() == p["reference_revision"]
assert not subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=no"], cwd=engine, text=True).strip()
sources = {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(engine.glob("*.py"))}
manifest = json.loads(gzip.decompress((prior / "manifest.json.gz").read_bytes()))
assert sources == manifest["source_sha256"]
assert sys.version == manifest["python"]
checksums = {p["baseline"]: p["baseline_sha256"], **{t["treatment"]: t["configuration_sha256"] for t in p["treatments"]}}
(root / "manifest.json").write_text(json.dumps({"source_sha256": sources, "python": sys.version, "protocol_sha256": hashlib.sha256((root / "protocol.json").read_bytes()).hexdigest()}, indent=2) + "\n")
results = []
for seed in p["pilot_seeds"]:
    for name, checksum in checksums.items():
        raw = (engine / "examples" / (name + ".json")).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == checksum
        run = root / f"seed-{seed}" / name
        run.mkdir(parents=True)
        config = json.loads(raw)
        config.update(seed=seed, timesteps=p["horizon"], headlessMode=True, debugMode=["none"], logfile=str(run / "trajectory.json"))
        previous_config = json.loads(gzip.decompress((prior / f"seed-{seed}" / name / "config.json.gz").read_bytes()))
        assert {k: v for k, v in config.items() if k not in ("timesteps", "logfile")} == {k: v for k, v in previous_config.items() if k not in ("timesteps", "logfile")}
        (run / "config.json").write_text(json.dumps(config, indent=2) + "\n")
        command = [sys.executable, str(engine / "sugarscape.py"), "--conf", str(run / "config.json")]
        with (run / "stdout.log").open("x") as stdout, (run / "stderr.log").open("x") as stderr:
            process = subprocess.run(command, cwd=engine, env={**os.environ, "PYTHONHASHSEED": "0", "PYTHONDONTWRITEBYTECODE": "1"}, stdout=stdout, stderr=stderr, timeout=p["per_run_timeout_seconds"])
        (run / "exit.json").write_text(json.dumps({"exit_code": process.returncode, "command": command}) + "\n")
        assert process.returncode == 0
        rows = json.loads((run / "trajectory.json").read_bytes())
        previous = json.loads(gzip.decompress((prior / f"seed-{seed}" / name / "trajectory.json.gz").read_bytes()))
        assert rows[:len(previous)] == previous
        assert [r["timestep"] for r in rows] == list(range(len(rows)))
        assert rows[-1]["timestep"] == p["horizon"] or rows[-1]["population"] == 0
        assert all(hashlib.sha256((engine / f).read_bytes()).hexdigest() == digest for f, digest in sources.items())
        result = {"seed": seed, "condition": name, "observations": len(rows), "prefix_observations_exact": len(previous), "final_population": rows[-1]["population"], "trajectory_sha256": hashlib.sha256((run / "trajectory.json").read_bytes()).hexdigest()}
        results.append(result)
        (root / "completed.json").write_text(json.dumps(results, indent=2) + "\n")
        print(json.dumps(result), flush=True)
(root / "terminal.json").write_text(json.dumps({"exit_code": 0, "runs": len(results), "scope": "Native execution and prefix checks only; independent full trajectory audit and drift analysis pending."}) + "\n")
