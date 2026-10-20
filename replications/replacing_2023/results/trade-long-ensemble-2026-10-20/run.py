"""Run disjoint horizon extensions only after native observer qualification passes."""
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from pathlib import Path
import ast
import gzip
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time

root = Path(__file__).resolve().parent
base = root.parent.parent
engine = base / "sugarscape-dtl-replacing-reference"
qualification = root.parent / "replacing-trade-passive-qualification-001"
prior = base / "sugarscape-replacing/replications/replacing_2023/results/trade-lending-paired20-2026-10-15"
p = json.loads((root / "protocol.json").read_bytes())
q = json.loads((qualification / "audit.json").read_bytes())
assert all(q[k] == v for k, v in p["qualification_required"].items())
assert hashlib.sha256((qualification / "trajectory.json").read_bytes()).hexdigest() == q["native_trajectory_sha256"]
assert hashlib.sha256((root / "observe.py").read_bytes()).hexdigest() == p["observer_sha256"]
qualified_class = next(n for n in ast.parse((qualification / "observe.py").read_text()).body if isinstance(n, ast.ClassDef))
ensemble_class = next(n for n in ast.parse((root / "observe.py").read_text()).body if isinstance(n, ast.ClassDef))
assert ast.dump(qualified_class) == ast.dump(ensemble_class)
assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=engine, text=True).strip() == p["reference_revision"]
assert not subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=no"], cwd=engine, text=True).strip()
assert shutil.disk_usage(root).free > 4 * 1024**3
assert not (root / "dispatch.json").exists()
(root / "dispatch.json").write_text(json.dumps({"pid": os.getpid(), "start_unix": time.time(), "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "protocol_sha256": hashlib.sha256((root / "protocol.json").read_bytes()).hexdigest()}, indent=2) + "\n")
conditions = [p["baseline"], *[t["treatment"] for t in p["treatments"]]]
requests = [(seed, condition) for seed in p["seeds"] for condition in conditions if (seed, condition) != (14133, "spice_growback")]
assert len(requests) == 59 and len(set(requests)) == 59
checksums = {p["baseline"]: p["baseline_sha256"], **{t["treatment"]: t["configuration_sha256"] for t in p["treatments"]}}


def run_one(seed, condition):
    run = root / f"seed-{seed}" / condition
    run.mkdir(parents=True)
    raw = (engine / "examples" / (condition + ".json")).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == checksums[condition]
    config = json.loads(raw)
    config.update(seed=seed, timesteps=p["horizon"], headlessMode=True, debugMode=["none"], logfile=str(run / "trajectory.json"))
    previous = prior / f"seed-{seed}" / condition
    previous_config = json.loads(gzip.decompress((previous / "config.json.gz").read_bytes()))
    assert {k: v for k, v in config.items() if k not in ("timesteps", "logfile")} == {k: v for k, v in previous_config.items() if k not in ("timesteps", "logfile")}
    config_path = run / "config.json"
    config_path.write_text(json.dumps(config, indent=2) + "\n")
    command = [sys.executable, str(root / "observe.py"), str(run), str(config_path)]
    start = time.monotonic()
    with (run / "stdout.log").open("x") as stdout, (run / "stderr.log").open("x") as stderr:
        process = subprocess.run(command, cwd=engine, env={**os.environ, "PYTHONHASHSEED": "0", "PYTHONDONTWRITEBYTECODE": "1"}, stdout=stdout, stderr=stderr, timeout=p["per_run_timeout_seconds"])
    (run / "exit.json").write_text(json.dumps({"exit_code": process.returncode, "command": command, "elapsed_seconds": time.monotonic() - start}, indent=2) + "\n")
    assert process.returncode == 0
    prefix = [json.loads(line) for line in (run / "original-schedule.jsonl").read_text().splitlines()]
    assert prefix == json.loads(gzip.decompress((previous / "trajectory.json.gz").read_bytes()))
    raw = (run / "trajectory.json").read_bytes()
    rows = json.loads(raw)
    assert [r["timestep"] for r in rows] == list(range(len(rows)))
    assert rows[-1]["timestep"] == p["horizon"] or rows[-1]["population"] == 0
    return {"seed": seed, "condition": condition, "observations": len(rows), "original_schedule_records_exact": len(prefix), "trajectory_sha256": hashlib.sha256(raw).hexdigest(), "config_sha256": hashlib.sha256(config_path.read_bytes()).hexdigest(), "final_population": rows[-1]["population"]}


deadline = time.monotonic() + p["admission_seconds"]
pending = list(requests)
completed = []
with ThreadPoolExecutor(max_workers=p["workers"]) as pool:
    active = set()
    while pending or active:
        while pending and len(active) < p["workers"] and time.monotonic() < deadline:
            seed, condition = pending.pop(0)
            active.add(pool.submit(run_one, seed, condition))
        if not active:
            break
        done, active = wait(active, return_when=FIRST_COMPLETED)
        for future in done:
            result = future.result()
            completed.append(result)
            (root / "completed.json").write_text(json.dumps(completed, indent=2) + "\n")
            print(json.dumps(result), flush=True)
(root / "terminal.json").write_text(json.dumps({"completed": len(completed), "remaining": pending, "all_requests_complete": not pending, "scope": "Native execution plus original-report reconstruction. Independent full-ensemble audit and analysis required."}, indent=2) + "\n")
