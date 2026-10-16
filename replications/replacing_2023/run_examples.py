"""Execute every Table 4 example with its released seed and horizon."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("engine", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
engine = args.engine.resolve()
assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=engine, text=True).strip() == "032abd2d2338aadc5ad0287dae7520539f7af57b"
assert not subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=no"], cwd=engine, text=True).strip()
root = Path(__file__).resolve().parent
targets = json.loads((root / "published_targets.json").read_text())["table4"]
assert len(targets) == 17
sources = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(engine.glob("*.py"))}
args.output.mkdir(parents=True, exist_ok=False)
output = args.output.resolve()
(output / "manifest.json").write_text(json.dumps({"engine": str(engine), "python": sys.version,
    "source_sha256": sources, "targets": targets,
    "scope": "Operational coverage of all17released examples. Original example horizons are not substitutes for figure-specific experiments or quantitative trade/lending comparisons."}, indent=2) + "\n")
with (output / "completed.jsonl").open("x") as completed:
    for target in targets:
        name = target["configuration"]
        source = engine / "examples" / name
        assert hashlib.sha256(source.read_bytes()).hexdigest() == target["released_config_sha256"]
        assert all(hashlib.sha256((engine / name).read_bytes()).hexdigest() == value for name, value in sources.items())
        configuration = json.loads(source.read_text())
        run = output / source.stem
        run.mkdir()
        configuration.update(headlessMode=True, debugMode=["none"], logfile=str(run / "trajectory.json"))
        (run / "config.json").write_text(json.dumps(configuration, indent=2) + "\n")
        command = [sys.executable, str(engine / "sugarscape.py"), "--conf", str(run / "config.json")]
        with (run / "stdout.log").open("x") as stdout, (run / "stderr.log").open("x") as stderr:
            result = subprocess.run(command, cwd=engine, stdout=stdout, stderr=stderr,
                                    env={**os.environ, "PYTHONHASHSEED": "0", "PYTHONDONTWRITEBYTECODE": "1"}, check=False)
        record = {"configuration": name, "exit_code": result.returncode, "seed": configuration["seed"],
                  "horizon": configuration["timesteps"], "command": command}
        if result.returncode == 0:
            trajectory = json.loads((run / "trajectory.json").read_text())
            assert [r["timestep"] for r in trajectory] == list(range(len(trajectory)))
            assert trajectory[0]["population"] == configuration["startingAgents"]
            assert all(r["seed"] == configuration["seed"] and 0 <= r["population"] <= 2500 for r in trajectory)
            assert trajectory[-1]["timestep"] == configuration["timesteps"] or trajectory[-1]["population"] == 0
            nonfinite = [{"timestep": row["timestep"], "field": key} for row in trajectory for key, value in row.items()
                         if isinstance(value, (int, float)) and not math.isfinite(value)]
            record.update(observations=len(trajectory), final_population=trajectory[-1]["population"],
                          nonfinite_scalar_fields=nonfinite,
                          trajectory_sha256=hashlib.sha256((run / "trajectory.json").read_bytes()).hexdigest())
        completed.write(json.dumps(record) + "\n")
        completed.flush()
        print(json.dumps(record), flush=True)
