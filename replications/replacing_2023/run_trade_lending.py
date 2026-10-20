"""Run the predeclared paired diagnostic using unmodified author code."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("engine", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
engine = args.engine.resolve()
protocol_path = Path(__file__).with_name("trade-lending-protocol.json")
protocol = json.loads(protocol_path.read_text())
assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=engine, text=True).strip() == protocol["reference_revision"]
assert not subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=no"], cwd=engine, text=True).strip()
checksums = {protocol["baseline"]: protocol["baseline_sha256"],
             **{t["treatment"]: t["configuration_sha256"] for t in protocol["treatments"]}}
configs = {}
for name, checksum in checksums.items():
    raw = (engine / "examples" / f"{name}.json").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == checksum
    configs[name] = json.loads(raw)
    assert configs[name]["agentReplacements"] == 0
    assert configs[name]["timesteps"] == protocol["horizon"]
baseline = configs[protocol["baseline"]]
for treatment in protocol["treatments"]:
    config = configs[treatment["treatment"]]
    differences = {key: {"baseline": baseline[key], "treatment": config[key]}
                   for key in baseline.keys() | config.keys() if key != "__README__" and baseline[key] != config[key]}
    assert differences == treatment["differences"]
sources = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(engine.glob("*.py"))}
args.output.mkdir(parents=True, exist_ok=False)
output = args.output.resolve()
(output / "protocol.json").write_bytes(protocol_path.read_bytes())
(output / "manifest.json").write_text(json.dumps({"engine": str(engine), "python": sys.version,
    "protocol_sha256": hashlib.sha256(protocol_path.read_bytes()).hexdigest(), "source_sha256": sources}, indent=2) + "\n")
with (output / "completed.jsonl").open("x") as completed:
    for seed in protocol["seeds"]:
        for name, original in configs.items():
            assert all(hashlib.sha256((engine / path).read_bytes()).hexdigest() == value for path, value in sources.items())
            run = output / f"seed-{seed}" / name
            run.mkdir(parents=True)
            config = dict(original)
            config.update(seed=seed, headlessMode=True, debugMode=["none"], logfile=str(run / "trajectory.json"))
            (run / "config.json").write_text(json.dumps(config, indent=2) + "\n")
            command = [sys.executable, str(engine / "sugarscape.py"), "--conf", str(run / "config.json")]
            with (run / "stdout.log").open("x") as stdout, (run / "stderr.log").open("x") as stderr:
                result = subprocess.run(command, cwd=engine, stdout=stdout, stderr=stderr,
                    env={**os.environ, "PYTHONHASHSEED": "0", "PYTHONDONTWRITEBYTECODE": "1"}, check=False)
            record = {"seed": seed, "condition": name, "exit_code": result.returncode, "command": command,
                      "config_sha256": hashlib.sha256((run / "config.json").read_bytes()).hexdigest()}
            if result.returncode == 0:
                record["trajectory_sha256"] = hashlib.sha256((run / "trajectory.json").read_bytes()).hexdigest()
            completed.write(json.dumps(record) + "\n")
            completed.flush()
            print(json.dumps(record), flush=True)
            assert result.returncode == 0, record
