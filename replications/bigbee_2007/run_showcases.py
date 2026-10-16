"""Compile the pinned author release and replay every draft showcase twice."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("engine", type=Path)
parser.add_argument("jdk", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
engine = args.engine.resolve()
assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=engine, text=True).strip() == "2baa2e411f1be3e8da5e352de98468b42db3d75d"
assert not subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=no"], cwd=engine, text=True).strip()
root = Path(__file__).resolve().parent
targets = json.loads((root / "targets.json").read_text())["targets"]
assert len(targets) == 17
for target in targets:
    config = engine / target["configuration"]
    assert hashlib.sha256(config.read_bytes()).hexdigest() == target["configuration_sha256"]
    settings = [line.strip() for line in config.read_text().splitlines() if line.strip() and not line.lstrip().startswith("#")]
    assert "stats_out=print" in settings
    assert not any(line.startswith("log_class") for line in settings)
args.output.mkdir(parents=True, exist_ok=False)
output = args.output.resolve()
classes = output / "classes"
classes.mkdir()
sources = sorted((engine / "sim/app/sugarscape").glob("**/*.java"))
java = str(args.jdk.resolve() / "java")
javac = str(args.jdk.resolve() / "javac")
compile_command = [javac, "-cp", str(engine / "lib/*"), "-d", str(classes), *map(str, sources)]
manifest = {"revision": "2baa2e411f1be3e8da5e352de98468b42db3d75d", "engine": str(engine),
            "seed": 0, "horizon": 1000, "repetitions": 2, "compile_command": compile_command,
            "java": subprocess.check_output([java, "-version"], stderr=subprocess.STDOUT, text=True),
            "adapter_sha256": hashlib.sha256((root / "Replay.java").read_bytes()).hexdigest(),
            "source_sha256": {str(p.relative_to(engine)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
            "dependencies_sha256": {str(p.relative_to(engine)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((engine / "lib").glob("*.jar"))},
            "targets": targets, "overrides": {"chart_display": "false"},
            "scope": "Operational coverage and repeatability of all17draft configurations. New seed0 and common1000-step horizon are not the paper's experimental protocol."}
(output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
with (output / "compile.log").open("x") as log:
    subprocess.run(compile_command, cwd=engine, stdout=log, stderr=subprocess.STDOUT, check=True)
results = []
with (output / "completed.jsonl").open("x") as completion:
    for target in targets:
        for repetition in [1, 2]:
            name = f'{target["id"]}-repeat{repetition}'
            command = [java, "-Djava.awt.headless=true", "-cp", f'{classes}:{engine / "lib/*"}:{engine}',
                       str(root / "Replay.java"), target["configuration"], "0", "1000"]
            with (output / f"{name}.csv").open("x") as stdout, (output / f"{name}.stderr").open("x") as stderr:
                result = subprocess.run(command, cwd=engine, stdout=stdout, stderr=stderr, check=False)
            record = {"target": target["id"], "repetition": repetition, "command": command,
                      "exit_code": result.returncode, "stdout_sha256": hashlib.sha256((output / f"{name}.csv").read_bytes()).hexdigest()}
            results.append(record)
            completion.write(json.dumps(record) + "\n")
            completion.flush()
            print(json.dumps(record), flush=True)
assert all(r["exit_code"] == 0 for r in results), "One or more native showcases failed; retain and inspect all recorded exit statuses"
