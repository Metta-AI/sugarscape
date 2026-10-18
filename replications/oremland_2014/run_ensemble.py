"""Compile and run a bounded native NetLogo 5.3.1 reconstruction ensemble."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("java_home", type=Path)
parser.add_argument("netlogo_app", type=Path)
parser.add_argument("model", type=Path)
parser.add_argument("output", type=Path)
parser.add_argument("--seeds", type=int, default=100)
parser.add_argument("--seconds", type=int, default=1800)
parser.add_argument("--timeout", type=Path, required=True)
args = parser.parse_args()
assert 1 <= args.seeds <= 100 and 0 < args.seconds <= 3600
args.output.mkdir(parents=True, exist_ok=False)
output = args.output.resolve()
config = (args.netlogo_app / "NetLogo.cfg").read_text().splitlines()
assert "app.version=5.3.1" in config
names = next(
    line.split("=", 1)[1] for line in config if line.startswith("app.classpath=")
).split(":")
jars = [args.netlogo_app / name for name in ["NetLogo.jar", *names]]
classpath = ":".join(str(path.resolve()) for path in jars) + ":" + str(output)
source = Path(__file__).with_name("RunEnsemble.java")
compile_command = [
    str(args.java_home / "bin/javac"),
    "-cp",
    classpath,
    "-d",
    str(output),
    str(source.resolve()),
]
subprocess.run(compile_command, check=True)
command = [
    str(args.timeout),
    "--signal=TERM",
    "--kill-after=30",
    str(args.seconds),
    str(args.java_home / "bin/java"),
    "-Xmx512m",
    "-XX:ActiveProcessorCount=1",
    "-Djava.awt.headless=true",
    "-Dfile.encoding=UTF-8",
    "-cp",
    classpath,
    "RunEnsemble",
    str(args.model.resolve()),
    str(output / "runs"),
    str(args.seeds),
]
manifest = {
    "compile_command": compile_command,
    "command": command,
    "java_version": subprocess.check_output(
        [str(args.java_home / "bin/java"), "-version"],
        stderr=subprocess.STDOUT,
        text=True,
    ),
    "java_source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
    "java_class_sha256": hashlib.sha256(
        (output / "RunEnsemble.class").read_bytes()
    ).hexdigest(),
    "model_sha256": hashlib.sha256(args.model.read_bytes()).hexdigest(),
    "jars": {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in jars
        if path.is_file()
    },
    "missing_declared_jars": [path.name for path in jars if not path.is_file()],
    "seeds": args.seeds,
    "seconds_limit": args.seconds,
    "scope": "Native reconstructed 50x50 uniform-tax diagnostic ensemble; not original published controls or whole-paper replication.",
}
(output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
started = time.time()
with (output / "run.log").open("x") as stream:
    result = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT)
(output / "exit.json").write_text(
    json.dumps(
        {"exit_code": result.returncode, "elapsed_seconds": time.time() - started},
        indent=2,
    )
    + "\n"
)
raise SystemExit(result.returncode)
